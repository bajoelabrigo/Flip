"""YouTuber-style templates (0.15.0, part B of docs/plan-stock.md): Reto extremo, Top 10 / ranking, Fitness.
Category youtuber; order 6000-6099; ids yt-reto-*, yt-top-*, yt-fit-*. 18 per style, about a third 16:9.

- Reto extremo (6000-6017): giant money counters, «$1 vs $1.000.000», «Último en salir gana», «Día 1 / Día 100»,
  on-screen timers, eliminations, mystery boxes, scoreboards; huge type with thick outlines, cuts on the beat.
- Top 10 / ranking (6018-6035): countdowns with big numbers, a slot and a title per entry, the reveal of number one
  (podium, cards, side list, cinema, neon, paper, retro, split, medals, «ranking» to fill).
- Fitness (6036-6053): rep counters, timers per set, before and after, weekly plans, workout steps, stats.

Counters count with quick successive text clips (templates_c1.count_up / count_fn): the final value is one editable
text («Número final» or a named label); the values before it are not editable. Timers that run in real seconds
(one clip per second) leave their digits fixed, the labels around them editable.
"""

from __future__ import annotations

import functools
import math

import kit
from kit import (Box, bg, bg_gradient, blink, centered, confetti, dots, effect, fill, flash, framed, glow, gradient,
                 grain, keys, kb, label, letterbox, line, no_stroke, outline, photo_bg, pill, pop, ring, rrect,
                 shade_bottom, shade_full, shade_top, shadow, slide_in, song, spike, stroke, tall, tanim, text_style,
                 vignette, wide)
from scene import argb
from templates_c1 import big, bills, burst, count_fn, count_up, curve_motion, ease_out, geo, hollow_ring, rays

O = 6000
CAT = "youtuber"
# Sample photos this batch never uses: a brand or logo shows (Nike swoosh on y2-gym-07, Puma on y2-run-03, Under
# Armour, Yeezy sneakers, a Tarmak ball, logos on dumbbells, mats, towels, banners and gym signs...).
# Un solo origen: la lista de kit.py. Antes cada lote traía su copia y las dos se desincronizaban.
BLOCKED = kit.BLOCKED

RT = ["reto extremo", "youtuber", "challenge"]
TP = ["ranking", "youtuber", "top 10"]
FT = ["fitness", "youtuber", "workout"]


def mk(maker, i, id, es, en, dur, tags, **kw):
    return maker(id, es, en, CAT, dur, order=O + i, tags=tags, **kw)


# --- helpers -----------------------------------------------------------------------------------------

def heavy(colour: str, ow: float = 12, oc: str = "#000000", drop: float = 10, glow_c: str | None = None,
          alpha: float = 1.0) -> list:
    """Thick-outline YouTube type: hard drop shadow, optional glow, outline, fill."""
    out = []
    if drop:
        out.append(shadow(oc, 0, drop, 0, 1.0))
    if glow_c:
        out.append(glow(glow_c, 30, 0.55))
    out += [stroke(ow, oc), fill(colour, alpha)]
    return out


def say(t, content, t0, dur, box, font, size, colour, *, track=None, name=None, **kw):
    return label(t, track or t.track("text", name or "Texto"), content, t0, dur, box, font, size, colour, name=name,
                 **kw)


def punch(t, times, peak=0.45, fall=0.3, shake=0.0, rgb=0.0):
    fx = [effect("zoom_pulse", animated={"punch": spike(times, peak, fall)})]
    if shake:
        fx.append(effect("beat_shake", animated={"amount": spike(times, shake, fall)}))
    if rgb:
        fx.append(effect("rgb_split", animated={"amount": spike(times, rgb, fall * 0.8)}))
    t.adjust(fx, name="Golpe")


def cuts(t, samples, starts, end, box=None, *, transition=None, tdur=0.3, kbs=0.06, punch_in=False, labels=None,
         track=None, effects=None, name="Fotos"):
    """One slot per start on one track; each lasts to the next start (overlapping by tdur when joined by a
    transition), the last to `end`."""
    box = box or t.full
    track = track or t.track("video", name)
    clips = []
    for i, (s, a) in enumerate(zip(samples, starts)):
        b = starts[i + 1] if i + 1 < len(starts) else end
        d = b - a + (tdur if transition and i + 1 < len(starts) else 0)
        if punch_in:
            motion = [(0, {"s": 1.16}, "snap"), (0.25, {}, "linear"), (d, {"s": 1.0 + kbs})]
        elif i % 2 == 0:
            motion = kb(d, 1.0, 1.0 + kbs)
        else:
            motion = kb(d, 1.0 + kbs, 1.0)
        extra = {}
        if effects:
            extra["effects"] = effects(i) if callable(effects) else effects
        c = t.photo(track, s, a, d, box, motion, label=labels[i] if labels else None, **extra)
        if clips and transition:
            t.transition(track, clips[-1], c, transition, tdur)
        clips.append(c)
    return clips


def disc(t, sample, t0, dur, box, motion=None, *, label=None, reuse=None, effects=None, ring_c=None, ring_w=10):
    if ring_c:
        t.solid(t.track("shape", "Aro"), ring_c, t0, dur,
                Box(box.x - ring_w, box.y - ring_w, box.w + 2 * ring_w, box.h + 2 * ring_w), motion, kind="ellipse",
                layers=[shadow("#000000", 0, 10, 26, 0.35), fill(ring_c), no_stroke()])
    tr = t.track("video", "Foto")
    extra = {"effects": effects} if effects else {}
    c = t.photo(tr, sample, t0, dur, box, motion, label=label, reuse=reuse, **extra)
    t.mask(tr, c, "ellipse")
    return c


def seq(t, items, box, style_fn, *, track=None, name="Texto", labels=None, motion=None, **extra):
    """items: [(t0, dur, text)], one after another on one track; labels[k] (or None) makes item k editable."""
    track = track or t.track("text", name)
    out = []
    for k, (a, d, s) in enumerate(items):
        lab = labels[k] if labels else None
        out.append(t.text(track, s, a, d, box, style_fn(k), motion, label=lab, editable=lab is not None, **extra))
    return out


def progress_ring(t, colour, box, t0, dur, trim, width=30, name="Progreso"):
    clip = t.solid(t.track("shape", name), colour, t0, dur, box, kind="ellipse",
                   layers=hollow_ring(colour, width, trim=1.0), rotation=keys([(0, -90)]))
    clip["shapeStyle"]["keyframes"] = {"layer.stroke.trimEnd": trim}
    return clip


def track_ring(t, colour, box, t0, dur, width=30, alpha=0.15):
    return t.solid(t.track("shape", "Pista"), colour, t0, dur, box, kind="ellipse",
                   layers=hollow_ring(colour, width, alpha))


def halo(colour: str, width: float = 30, alpha: float = 0.3) -> dict:
    """A soft wide stroke under a neon outline (a glow layer would fill the whole shape)."""
    return {"id": "halo", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "center",
            "paint": {"kind": "solid", "color": argb(colour, alpha)}, "opacity": 1.0}


def mmss(s: float) -> str:
    s = int(round(s))
    return f"{s // 60}:{s % 60:02d}"


def accent(colour: str) -> dict:
    return {"rule": "none", "colorEnabled": True, "color": argb(colour)}


def gold_text(drop=10):
    return [shadow("#3A2600", 0, drop, 0, 1.0), glow("#FFC83D", 28, 0.5), stroke(10, "#3A2600"),
            gradient([(0, "#FFF4C2"), (0.5, "#FFC83D"), (1, "#D48A00")], angle=90)]


# =====================================================================================================
# 1. RETO EXTREMO
# =====================================================================================================

def reto_1_vs_millon():
    t = mk(tall, 0, "yt-reto-1-vs-millon", "$1 vs $1.000.000", "$1 vs $1,000,000", 9.0,
           RT + ["dinero", "barato vs caro", "money", "versus"], thumb_at=5.6, background="#0A0A0A")
    bg(t, "#0A0A0A")
    top, bot = Box(0, 0, 1080, 950), Box(0, 970, 1080, 950)
    t.photo(t.track("video", "Foto $1"), "y2-dish-05", 0.0, 9.0, top, slide_in(dx=-1080, length=0.5),
            label="Lo barato")
    t.solid(t.track("shape", "Sombra"), "#000000", 0.0, 9.0, Box(0, 560, 1080, 390),
            layers=[gradient([(0, "#000000", 0.0), (1, "#000000", 0.8)], angle=90), no_stroke()])
    t.photo(t.track("video", "Foto $1.000.000"), "y2-dish-01", 0.3, 8.7, bot, slide_in(dx=1080, length=0.5),
            label="Lo caro")
    t.solid(t.track("shape", "Sombra"), "#000000", 0.3, 8.7, Box(0, 1500, 1080, 420),
            layers=[gradient([(0, "#000000", 0.0), (1, "#000000", 0.85)], angle=90), no_stroke()])
    say(t, "$1", 0.7, 8.3, Box(50, 680, 980, 260), "Anton", 240, "#FFE600", weight=400, align="left",
        layers=heavy("#FFE600", 14), anim_in=tanim("stamp", duration=0.35), name="Precio barato")
    count_up(t, t.track("text", "Contador"), 1, 1_000_000, "$1.000.000", 1.3, 3.0, Box(40, 1640, 1000, 250),
             big("Anton", 200, "#3DFF6E", weight=400, layers=heavy("#3DFF6E", 14), align="right"), prefix="$",
             power=3.0, name="Precio caro",
             final_style=big("Anton", 200, "#3DFF6E", weight=400, align="right",
                             layers=heavy("#3DFF6E", 14, glow_c="#3DFF6E"),
                             anim_loop=tanim("pulse", amount=3, speed=1.2)))
    t.solid(t.track("shape", "VS"), "#FF1F3D", 0.9, 8.1, centered(540, 960, 250, 250), pop(0, 0.4), kind="ellipse",
            layers=[shadow("#000000", 0, 10, 0, 1.0), stroke(10, "#FFFFFF"), fill("#FF1F3D")])
    say(t, "VS", 1.0, 8.0, centered(540, 966, 250, 200), "Luckiest Guy", 120, "#FFFFFF", weight=400,
        layers=heavy("#FFFFFF", 6, drop=6), anim_in=tanim("pop", duration=0.3),
        anim_loop=tanim("jitter", amount=1.2, angle=3, speed=10), editable=False)
    say(t, "¿CUÁL GANA?", 4.8, 4.2, Box(90, 70, 900, 150), "Luckiest Guy", 96, "#FFFFFF", weight=400,
        layers=heavy("#FFFFFF", 8, drop=6), box_bg=("#FF1F3D", 1.0), box_pad=24, box_radius=24,
        anim_in=tanim("pop", duration=0.35), name="Pregunta")
    flash(t, 4.3, 0.3, peak=0.6)
    punch(t, [0.9, 4.3], 0.5, 0.3)
    song(t, "cine", 0, 0.85)
    return t


def reto_ultimo_gana():
    t = mk(wide, 1, "yt-reto-ultimo-en-salir", "Último en salir gana", "Last to leave wins", 10.0,
           RT + ["último en salir", "premio", "last to leave"], thumb_at=7.6)
    photo_bg(t, "y2b-h-fun-01", s1=1.08, label="Tu video")
    t.solid(t.track("shape", "Sombra"), "#000000",
            layers=[gradient([(0, "#000000", 0.88), (0.55, "#000000", 0.4), (1, "#000000", 0.1)], angle=0),
                    no_stroke()])
    say(t, "ÚLTIMO EN", 0.0, 10.0, Box(80, 110, 1100, 170), "Luckiest Guy", 150, "#FFFFFF", weight=400,
        align="left", layers=heavy("#FFFFFF", 12), anim_in=tanim("slide-right", duration=0.4, distance=0.2),
        name="Título 1")
    say(t, "SALIR", 0.3, 9.7, Box(80, 270, 1100, 200), "Luckiest Guy", 180, "#FFFFFF", weight=400, align="left",
        layers=heavy("#FFFFFF", 12), anim_in=tanim("slide-right", duration=0.4, distance=0.2), name="Título 2")
    say(t, "GANA", 0.9, 9.1, Box(80, 460, 1100, 290), "Luckiest Guy", 270, "#FFE600", weight=400, align="left",
        layers=heavy("#FFE600", 16), anim_in=tanim("stamp", duration=0.4),
        anim_loop=tanim("pulse", amount=3, speed=1.0), name="Título 3")
    rrect(t, t.track("shape", "Premio"), "#111111", 1.2, 8.8, Box(1240, 560, 600, 360), 32,
          motion=slide_in(dx=700, length=0.5),
          layers=[shadow("#000000", 0, 14, 30, 0.5), fill("#111111", 0.9), stroke(6, "#FFE600")])
    say(t, "PREMIO", 1.5, 8.5, Box(1240, 590, 600, 80), "Montserrat", 50, "#FFE600", weight=900, spacing=12,
        anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    count_up(t, t.track("text", "Premio"), 0, 10_000, "$10.000", 1.6, 2.6, Box(1240, 670, 600, 210),
             big("Anton", 160, "#3DFF6E", weight=400, layers=heavy("#3DFF6E", 8, drop=6)), prefix="$",
             name="Premio",
             final_style=big("Anton", 160, "#3DFF6E", weight=400, layers=heavy("#3DFF6E", 8, drop=6),
                             anim_in=tanim("pop", duration=0.3)))
    say(t, "QUEDAN", 2.0, 8.0, Box(80, 830, 340, 110), "Montserrat", 70, "#FFFFFF", weight=900, align="left",
        anim_in=tanim("fade", duration=0.3), name="Quedan")
    count_fn(t, t.track("text", "Jugadores"), lambda f: 50 - 43 * ease_out(f, 2.2), lambda v: str(round(v)), 2.2,
             5.0, "7", Box(420, 770, 400, 230), big("Anton", 200, "#FF3B30", weight=400, align="left",
                                                    layers=heavy("#FF3B30", 10)),
             name="Jugadores", step=3,
             final_style=big("Anton", 200, "#FF3B30", weight=400, align="left", layers=heavy("#FF3B30", 10),
                             anim_in=tanim("stamp", duration=0.3)))
    say(t, "● GRABANDO", 0.0, 10.0, Box(1440, 40, 440, 70), "Montserrat", 40, "#FF3B30", weight=800,
        align="right", editable=False, opacity=blink(10.0, 1.0, 0.25))
    flash(t, 7.2, 0.3, colour="#FFE600", peak=0.4)
    punch(t, [0.9, 7.2], 0.4, 0.3)
    song(t, "epic", 5, 0.85)
    return t


def reto_dia1_dia100():
    t = mk(tall, 2, "yt-reto-dia-1-dia-100", "Día 1 vs día 100", "Day 1 vs day 100", 12.0,
           RT + ["100 días", "progreso", "day 1", "constancia"], thumb_at=10.9)
    cuts(t, ["outfit-04", "y5-outfit-01", "y5-outfit-02", "gym-01"], [0.0, 3.0, 6.0, 9.0], 12.0,
         transition="dip_white", tdur=0.3, labels=["Día 1", "Día 7", "Día 30", "Día 100"])
    shade_bottom(t, 950, 0.88)
    shade_top(t, 260, 0.6)
    for k in range(4):
        w = 1000 / 4 - 12
        x = 40 + k * (1000 / 4)
        rrect(t, t.track("shape", "Barra"), "#FFFFFF", 0.0, 12.0, Box(x, 60, w, 12), 6, alpha=0.3)
        line(t, t.track("shape", "Progreso"), "#C6FF00", k * 3.0, 12.0 - k * 3.0, Box(x, 60, w, 12), length=3.0,
             ease="linear")
    say(t, "DÍA", 0.2, 11.8, Box(60, 1220, 960, 190), "Bebas Neue", 180, "#FFFFFF", weight=400, align="left",
        layers=heavy("#FFFFFF", 8, drop=8), editable=False)
    num = lambda k=0: text_style("Bebas Neue", 430, heavy("#C6FF00", 10, drop=12), weight=400,  # noqa: E731
                                 align="left", anim_in=tanim("stamp", duration=0.3, **{"from": 160}))
    box = Box(60, 1380, 960, 440)
    track = t.track("text", "Día")
    seq(t, [(0.2, 2.8, "1"), (3.0, 3.0, "7"), (6.0, 3.0, "30")], box, num, track=track,
        labels=["Día etapa 1", "Día etapa 2", "Día etapa 3"])
    count_fn(t, track, lambda f: 30 + 70 * ease_out(f, 2.0), lambda v: str(int(round(v))), 9.0, 1.4, "100", box,
             lambda: text_style("Bebas Neue", 430, heavy("#C6FF00", 10, drop=12), weight=400, align="left"),
             step=2, name="Día final",
             final_style=lambda: text_style("Bebas Neue", 430, heavy("#C6FF00", 10, drop=12, glow_c="#C6FF00"),
                                            weight=400, align="left", anim_in=tanim("stamp", duration=0.3)))
    say(t, "MI RETO DE 100 DÍAS", 0.4, 11.6, Box(60, 1800, 960, 80), "Montserrat", 46, "#FFFFFF", weight=800,
        spacing=6, align="left", anim_in=tanim("fade", duration=0.4), name="Reto")
    flash(t, 10.4, 0.35, colour="#C6FF00", peak=0.45)
    punch(t, [3.0, 6.0, 9.0, 10.4], 0.35, 0.3)
    song(t, "epic", 1, 0.85)
    return t


def reto_24_horas():
    t = mk(wide, 3, "yt-reto-24-horas", "24 horas en…", "24 hours in…", 10.0,
           RT + ["24 horas", "temporizador", "24 hours", "reloj"], thumb_at=8.7)
    cuts(t, ["y2b-h-fun-03", "y2b-h-fun-01", "y2b-h-fun-02", "y2-h-shock-03", "y2b-h-fun-07"],
         [0.0, 2.0, 4.0, 6.0, 8.0], 10.0, transition="push_left", tdur=0.3, kbs=0.07)
    shade_bottom(t, 440, 0.8)
    shade_top(t, 240, 0.5)
    t.solid(t.track("shape", "REC"), "#FF2D2D", 0.0, 10.0, centered(90, 88, 34, 34), kind="ellipse",
            opacity=blink(10.0, 1.0, 0.1))
    say(t, "REC", 0.0, 10.0, Box(120, 56, 200, 64), "Montserrat", 44, "#FFFFFF", weight=800, align="left",
        editable=False)
    rrect(t, t.track("shape", "Reloj"), "#000000", 0.2, 9.8, Box(1430, 50, 440, 180), 24,
          layers=[fill("#000000", 0.72), stroke(4, "#FFE600")])
    say(t, "TIEMPO", 0.2, 9.8, Box(1430, 64, 440, 50), "Montserrat", 32, "#FFE600", weight=800, spacing=10,
        name="Etiqueta reloj")
    count_fn(t, t.track("text", "Reloj"), lambda f: 1440 * ease_out(f, 1.6),
             lambda v: f"{int(v) // 60:02d}:{int(v) % 60:02d}", 0.4, 7.6, "24:00", Box(1430, 104, 440, 120),
             big("Orbitron", 84, "#FFFFFF", weight=800), name="Tiempo final",
             final_style=big("Orbitron", 84, "#FFE600", weight=800, layers=[glow("#FFE600", 20, 0.6), fill("#FFE600")],
                             anim_in=tanim("pop", duration=0.3)))
    say(t, "24 HORAS EN EL PARQUE", 0.4, 9.6, Box(70, 840, 1500, 130), "Archivo Black", 84, "#111111", weight=400,
        align="left", box_bg=("#FFE600", 1.0), box_pad=22, anim_in=tanim("slide-right", duration=0.45, distance=0.2),
        name="Título")
    say(t, "¿quién aguanta más?", 0.8, 9.2, Box(80, 985, 1000, 70), "Montserrat", 48, "#FFFFFF", weight=700,
        align="left", anim_in=tanim("fade", duration=0.4), name="Subtítulo")
    flash(t, 8.0, 0.3, colour="#FFE600", peak=0.35)
    punch(t, [2.0, 4.0, 6.0, 8.0], 0.25, 0.3)
    song(t, "cine", 1, 0.85)
    return t


def reto_premio_gigante():
    t = mk(tall, 4, "yt-reto-premio-gigante", "Premio gigante", "Giant prize", 7.0,
           RT + ["premio", "dinero", "contador", "prize"], thumb_at=5.4, background="#04160A")
    photo_bg(t, "y2-shock-04", s1=1.1, label="Tu foto")
    shade_full(t, 0.55, colour="#04160A")
    rays(t, "#FFD54F", 4.0, 3.0, centered(540, 990, 1500, 1500), alpha=0.18)
    bills(t, 0.0, 7.0, seed=6004)
    say(t, "PREMIO", 0.3, 6.7, Box(60, 670, 960, 170), "Luckiest Guy", 130, "#FFFFFF", weight=400,
        layers=heavy("#FFFFFF", 10), anim_in=tanim("drop", duration=0.5), name="Antetítulo")
    burst(t, "#FFD54F", 4.0, centered(540, 1000, 1100, 1100), peak=0.4, length=0.9)
    count_up(t, t.track("text", "Contador"), 0, 50_000, "$50.000", 0.7, 3.3, Box(0, 840, 1080, 310),
             big("Luckiest Guy", 200, "#39FF6A", weight=400, layers=heavy("#39FF6A", 16, drop=14)), prefix="$",
             power=3.2, name="Premio",
             final_style=big("Luckiest Guy", 200, "#39FF6A", weight=400,
                             layers=heavy("#39FF6A", 16, drop=14, glow_c="#39FF6A"),
                             anim_in=tanim("pop", duration=0.35, **{"from": 80}),
                             anim_loop=tanim("pulse", amount=3, speed=1.0)))
    flash(t, 4.0, 0.35, colour="#FFF6C2", peak=0.6)
    say(t, "¡ES TODO TUYO!", 4.2, 2.8, Box(40, 1180, 1000, 170), "Bangers", 130, "#FFE600", weight=400,
        layers=heavy("#FFE600", 10), anim_in=tanim("stamp", duration=0.35), rotation=keys([(0, -4)]),
        name="Mensaje")
    punch(t, [4.0], 0.6, 0.35, shake=0.3)
    song(t, "upbeat", 1, 0.85)
    return t


def reto_eliminados():
    t = mk(tall, 5, "yt-reto-eliminados", "Solo puede quedar uno", "Only one can remain", 9.0,
           RT + ["eliminado", "ganador", "competencia", "eliminated"], thumb_at=7.4, background="#0A0000")
    bg_gradient(t, [(0, "#3A0000"), (0.6, "#120000"), (1, "#000000")], angle=90)
    say(t, "SOLO PUEDE QUEDAR UNO", 0.2, 8.8, Box(60, 110, 960, 320), "Bebas Neue", 150, "#FFFFFF", weight=400,
        layers=[glow("#FF1A1A", 30, 0.5), fill("#FFFFFF")], line=1.0,
        anim_in=tanim("pop", duration=0.35, unit="word", stagger=0.1), name="Título")
    centres = [(290, 720), (790, 720), (290, 1230), (790, 1230)]
    samples = ["man-01", "portrait-02", "y2-shock-05", "man-04"]
    elim = {1: 2.0, 2: 3.5, 0: 5.0}
    for i, ((cx, cy), s) in enumerate(zip(centres, samples)):
        box = centered(cx, cy, 400, 400)
        a = 0.3 + 0.12 * i
        disc(t, s, a, 9.0 - a, box, pop(0, 0.45), label=f"Jugador {i + 1}", ring_c="#FFFFFF", ring_w=8)
        if i in elim:
            at = elim[i]
            t.solid(t.track("shape", "Fuera"), "#000000", at, 9.0 - at, box, kind="ellipse", alpha=0.62,
                    opacity=keys([(0, 0.0, "out"), (0.3, 1.0)]))
            x = t.solid(t.track("shape", "Cruz"), "#FF1A1A", at, 9.0 - at, centered(cx, cy, 300, 300),
                        pop(0, 0.3, s0=1.8), kind="cross", rotation=keys([(0, 45)]),
                        layers=[shadow("#000000", 0, 8, 0, 0.9), fill("#FF1A1A"), no_stroke()])
            geo(x, thickness=0.22)
            say(t, "ELIMINADO", at + 0.1, 8.9 - at, centered(cx, cy + 170, 380, 90), "Bebas Neue", 70, "#FFFFFF",
                weight=400, box_bg=("#FF1A1A", 1.0), box_pad=10, rotation=keys([(0, -6)]),
                anim_in=tanim("stamp", duration=0.3), editable=False)
    ring(t, t.track("shape", "Ganador"), "#FFD23F", 18, 6.5, 2.5, centered(790, 1230, 440, 440), pop(0, 0.4))
    star = t.solid(t.track("shape", "Corona"), "#FFD23F", 6.6, 2.4, centered(790, 985, 170, 150), pop(0, 0.45),
                   kind="star", layers=[shadow("#000000", 0, 8, 0, 0.8), fill("#FFD23F"), no_stroke()])
    geo(star, points=5, innerRatio=0.45)
    say(t, "¡GANADOR!", 6.6, 2.4, Box(60, 1490, 960, 160), "Luckiest Guy", 120, "#FFD23F", weight=400,
        layers=heavy("#FFD23F", 10), anim_in=tanim("stamp", duration=0.35), name="Mensaje")
    seq(t, [(0.3, 1.7, "QUEDAN 4"), (2.0, 1.5, "QUEDAN 3"), (3.5, 1.5, "QUEDAN 2"), (5.0, 4.0, "QUEDA 1")],
        Box(60, 1700, 960, 130), lambda k: text_style("Bebas Neue", 110, [fill("#FFFFFF")], weight=400, spacing=6,
                                                       anim_in=tanim("pop", duration=0.25)), name="Quedan")
    confetti(t, ["#FFD23F", "#FFFFFF", "#FF1A1A"], 6.5, 2.5, seed=6005, lanes=3, density=0.25)
    for at in (2.0, 3.5, 5.0):
        flash(t, at, 0.25, colour="#FF1A1A", peak=0.3)
    punch(t, [2.0, 3.5, 5.0, 6.5], 0.35, 0.3, shake=0.2)
    song(t, "suspense", 0, 0.85)
    return t


def reto_barato_caro():
    t = mk(wide, 6, "yt-reto-barato-vs-caro", "$1 vs $100 vs $10.000", "$1 vs $100 vs $10,000", 10.0,
           RT + ["barato vs caro", "comparación", "cheap vs expensive", "dinero"], thumb_at=7.2,
           background="#111111")
    bg(t, "#111111")
    xs = [0, 650, 1300]
    reveal = [0.3, 1.8, 3.3]
    samples = ["y2-h-dish-02", "y2-h-dish-01", "y2-h-dish-03"]
    for i in range(3):
        t.photo(t.track("video", "Foto"), samples[i], reveal[i], 10.0 - reveal[i], Box(xs[i], 0, 620, 1080),
                slide_in(dy=1080, length=0.6), label=["Opción barata", "Opción media", "Opción cara"][i])
    shade_bottom(t, 420, 0.85)
    colours = [("#22C55E", "#FFFFFF"), ("#3B82F6", "#FFFFFF"), ("#FFC83D", "#111111")]
    prices = ["$1", "$100", None]
    for i in range(3):
        a = reveal[i] + 0.3
        pill(t, t.track("shape", "Precio"), colours[i][0], a, 10.0 - a, Box(xs[i] + 110, 60, 400, 130), pop(0, 0.35))
        if prices[i]:
            say(t, prices[i], a, 10.0 - a, Box(xs[i] + 110, 60, 400, 130), "Anton", 100, colours[i][1], weight=400,
                anim_in=tanim("pop", duration=0.3), name=f"Precio {i + 1}")
        say(t, ["COMIDA DE $1", "COMIDA DE $100", "COMIDA DE $10.000"][i], a + 0.2, 9.8 - a,
            Box(xs[i] + 30, 920, 560, 110), "Montserrat", 46, "#FFFFFF", weight=900,
            anim_in=tanim("rise", duration=0.4), name=f"Nombre {i + 1}")
    count_up(t, t.track("text", "Precio 3"), 100, 10_000, "$10.000", 3.6, 1.6, Box(1410, 60, 400, 130),
             big("Anton", 96, "#111111", weight=400), prefix="$", power=2.6, name="Precio 3",
             final_style=big("Anton", 96, "#111111", weight=400, anim_in=tanim("pop", duration=0.3)))
    t.solid(t.track("shape", "Banda"), "#000000", 5.5, 4.5, Box(-100, 410, 2120, 240),
            slide_in(dx=-2200, length=0.35), alpha=0.8, rotation=keys([(0, -3)]))
    say(t, "¿VALE LA PENA?", 5.7, 4.3, Box(160, 380, 1600, 300), "Luckiest Guy", 160, "#FFE600", weight=400,
        layers=heavy("#FFE600", 12), rotation=keys([(0, -3)]), anim_in=tanim("stamp", duration=0.35),
        name="Pregunta")
    flash(t, 5.6, 0.3, peak=0.5)
    punch(t, [0.3, 1.8, 3.3, 5.6], 0.3, 0.3)
    song(t, "jazz", 2, 0.85)
    return t


def reto_no_te_muevas():
    t = mk(tall, 7, "yt-reto-no-te-muevas", "No te muevas: 10 segundos", "Don't move: 10 seconds", 12.0,
           RT + ["temporizador", "cuenta regresiva", "timer", "10 segundos"], thumb_at=8.2)
    photo_bg(t, "y2-fun-01", s1=1.1, label="Tu foto o video")
    shade_full(t, 0.5)
    say(t, "¡NO TE MUEVAS!", 0.2, 11.8, Box(60, 150, 960, 320), "Russo One", 130, "#FFFFFF", weight=400,
        layers=heavy("#FFFFFF", 12, oc="#B00020"), line=1.05, anim_in=tanim("drop", duration=0.5), name="Título")
    box = centered(540, 1020, 700, 700)
    track_ring(t, "#FFFFFF", box, 0.3, 11.7, width=30, alpha=0.18)
    progress_ring(t, "#FF2D2D", box, 0.3, 11.7, keys([(0, 1.0, "hold"), (0.2, 1.0, "linear"), (10.2, 0.0)]))
    nums = t.track("text", "Segundos")
    for k in range(10):
        n = 10 - k
        colour = "#FFFFFF" if n > 3 else "#FF2D2D"
        t.text(nums, str(n), 0.5 + k, 1.0, centered(540, 1020, 700, 480),
               text_style("Russo One", 380, heavy(colour, 12), weight=400,
                          anim_in=tanim("pop", duration=0.2, **{"from": 140})), editable=False)
    say(t, "¡TIEMPO!", 10.5, 1.5, centered(540, 1020, 1000, 320), "Russo One", 210, "#FFE600", weight=400,
        layers=heavy("#FFE600", 14), anim_in=tanim("stamp", duration=0.3), name="Final")
    say(t, "el último en moverse gana $1.000", 0.6, 11.4, Box(60, 1480, 960, 150), "Montserrat", 54, "#FFFFFF",
        weight=800, anim_in=tanim("fade", duration=0.4), name="Regla")
    flash(t, 10.5, 0.35, peak=0.7)
    punch(t, [7.5, 8.5, 9.5, 10.5], 0.3, 0.3, shake=0.25)
    song(t, "suspense", 1, 0.85)
    return t


def reto_sobrevivi():
    t = mk(wide, 8, "yt-reto-sobrevivi-7-dias", "Sobreviví 7 días", "I survived 7 days", 12.0,
           RT + ["supervivencia", "7 días", "aventura", "survival"], thumb_at=10.0, background="#0B140A")
    bg_gradient(t, [(0, "#24361F"), (1, "#0B140A")], angle=90)
    say(t, "SOBREVIVÍ", 0.2, 11.8, Box(80, 120, 860, 160), "Permanent Marker", 120, "#F4E9D0", weight=400,
        align="left", anim_in=tanim("wipe", duration=0.5), name="Título 1")
    say(t, "7 DÍAS", 0.6, 11.4, Box(80, 260, 900, 280), "Permanent Marker", 210, "#FF7A1A", weight=400,
        align="left", layers=[shadow("#000000", 0, 8, 0, 0.6), fill("#FF7A1A")], anim_in=tanim("stamp", duration=0.4),
        name="Título 2")
    say(t, "en el bosque", 1.0, 11.0, Box(84, 540, 820, 100), "Kalam", 66, "#F4E9D0", weight=400, align="left",
        anim_in=tanim("fade", duration=0.5), name="Lugar")
    # Tally marks, one per day.
    tally = [(100, 0), (144, 0), (188, 0), (232, 0), (None, 65), (330, 0), (374, 0)]
    for i, (x, rot) in enumerate(tally):
        at = 1.2 + i * 1.15
        if x is None:
            line(t, t.track("shape", "Raya"), "#F4E9D0", at, 12.0 - at, centered(173, 790, 16, 250), grow="c",
                 length=0.25, rotation=keys([(0, rot)]))
        else:
            line(t, t.track("shape", "Raya"), "#F4E9D0", at, 12.0 - at, Box(x, 720, 16, 150), grow="y", length=0.25)
    days = [1, 3, 5, 7]
    times = [1.0, 3.6, 6.2, 8.8]
    samples = ["h-nature-01", "h-nature-03", "h-travel-02", "h-nature-05"]
    offsets = [(-30, -20, -5), (40, 10, 4), (-20, 30, -3), (20, 0, 2)]
    for d, at, s, (ox, oy, rot) in zip(days, times, samples, offsets):
        box = centered(1380 + ox, 470 + oy, 620, 450)
        drop = [(0, {"dy": -1000}, "out"), (0.6, {})]
        framed(t, s, at, 12.0 - at, box, drop, border=18, bottom=90, rotation=keys([(0, rot)]), label=f"Día {d}")
        # Caption on the white strip, turned about the print's centre like the print.
        r = box.h / 2 + 9  # centre of the white strip from the frame centre
        fcy = box.cy + 45
        th = math.radians(rot)
        dx, dy = -r * math.sin(th), r * math.cos(th)
        say(t, f"DÍA {d}", at, 12.0 - at, centered(box.cx + dx, fcy + dy, 600, 80), "Caveat", 66, "#333333",
            weight=700, rotation=keys([(0, rot)]), motion=drop, name=f"Pie día {d}")
    grain(t, 0.22)
    vignette(t, 0.45)
    song(t, "epic", 3, 0.85)
    return t


def reto_100_personas():
    t = mk(tall, 9, "yt-reto-100-personas", "100 personas, 1 ganador", "100 people, 1 winner", 10.0,
           RT + ["100 personas", "competencia", "ganador", "100 people"], thumb_at=8.4)
    photo_bg(t, "y2-fun-01", label="Tu foto", effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=8)])
    shade_full(t, 0.62, colour="#05060A")
    say(t, "100 PERSONAS", 0.1, 9.9, Box(60, 100, 960, 190), "Anton", 160, "#FFFFFF", weight=400,
        layers=heavy("#FFFFFF", 10), anim_in=tanim("slide-down", duration=0.4), name="Título")
    say(t, "1 GANADOR", 0.4, 9.6, Box(60, 290, 960, 140), "Anton", 110, "#FFE600", weight=400,
        layers=heavy("#FFE600", 8), anim_in=tanim("slide-up", duration=0.4), name="Subtítulo")
    t0, length = 1.0, 6.5
    alive = lambda f: max(1, round(100 - 99 * ease_out(f, 2.0)))  # noqa: E731
    style = lambda: text_style("Montserrat", 72, [fill("#FFFFFF", 0.2)], weight=800, spacing=4,  # noqa: E731
                               accent=accent("#FFE600"))
    fps = 30
    samples = [(0.0, 100)] + [((t0 + k / fps), alive(k / (length * fps))) for k in range(0, round(length * fps) + 1, 2)]
    for r in range(10):
        states = []
        for at, n in samples:
            a = max(0, min(10, n - r * 10))
            if not states or states[-1][1] != a:
                states.append((at, a))
        tr = t.track("text", f"Fila {r + 1}")
        for k, (at, a) in enumerate(states):
            end = states[k + 1][0] if k + 1 < len(states) else 10.0
            text = " ".join(["*●*"] * a + ["●"] * (10 - a))
            t.text(tr, text, at, end - at, Box(90, 470 + r * 80, 900, 80), style(), editable=False)
    say(t, "QUEDAN", 0.6, 9.4, Box(60, 1290, 960, 90), "Montserrat", 60, "#FFFFFF", weight=900, spacing=10,
        name="Quedan")
    count_fn(t, t.track("text", "Contador"), lambda f: 100 - 99 * ease_out(f, 2.0), lambda v: str(max(1, round(v))),
             t0, length, "1", Box(0, 1370, 1080, 330), big("Anton", 300, "#FFFFFF", weight=400,
                                                        layers=heavy("#FFFFFF", 12)),
             name="Número final", step=2,
             final_style=big("Anton", 300, "#FFE600", weight=400, layers=heavy("#FFE600", 12, glow_c="#FFE600"),
                             anim_in=tanim("stamp", duration=0.3)))
    say(t, "¡GANADOR!", 7.6, 2.4, Box(60, 1700, 960, 170), "Luckiest Guy", 130, "#FFE600", weight=400,
        layers=heavy("#FFE600", 10), anim_in=tanim("pop", duration=0.35), name="Mensaje")
    confetti(t, ["#FFE600", "#FFFFFF", "#FF3B30"], 7.5, 2.5, seed=6009, lanes=3, density=0.25)
    flash(t, 7.5, 0.3, colour="#FFE600", peak=0.45)
    punch(t, [7.5], 0.5, 0.35)
    song(t, "cine", 0, 0.85)
    return t


def reto_caja_misteriosa():
    t = mk(tall, 10, "yt-reto-caja-misteriosa", "Elige una caja", "Pick a box", 9.0,
           RT + ["caja misteriosa", "sorpresa", "mystery box", "premio"], thumb_at=7.0, background="#1B0040")
    bg_gradient(t, [(0, "#6A00F4"), (1, "#1B0040")], angle=90)
    dots(t, ["#FFFFFF", "#FFD60A"], 20, 0.0, 9.0, seed=6010, size=(6, 16), drift=120, alpha=0.7)
    say(t, "ELIGE UNA CAJA", 0.2, 8.8, Box(60, 190, 960, 200), "Lilita One", 130, "#FFFFFF", weight=400,
        layers=heavy("#FFFFFF", 10, oc="#2B0066"), anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.12),
        name="Título")
    xs = [200, 540, 880]
    cols = [("#FF3B5C", "#C2183A"), ("#00C2FF", "#0078B8"), ("#FFD60A", "#C99A00")]
    for i, (cx, (c1, c2)) in enumerate(zip(xs, cols)):
        a = 0.4 + 0.15 * i
        dur = 5.2 - a

        def motion(part_dy=0.0, lid=False, i=i, a=a, dur=dur):
            m = [(0, {"dy": 1200}, "back"), (0.55, {})]
            if i == 1:
                sh = 3.0 - a
                m += [(sh, {})]
                k = 0
                while sh + (k + 1) * 0.08 < 4.3 - a:
                    k += 1
                    m.append((sh + k * 0.08, {"dx": 18 if k % 2 else -18}))
                m += [(4.4 - a, {}, "in"), (dur, {"dy": -1600 if lid else 1600})]
            else:
                m += [(4.4 - a, {}, "in"), (5.0 - a, {"dx": -1200 if i == 0 else 1200})]
            return m
        rrect(t, t.track("shape", "Caja"), c1, a, dur, Box(cx - 140, 890, 280, 260), 24, motion=motion(),
              layers=[shadow("#000000", 0, 16, 30, 0.4), fill(c1), no_stroke()])
        t.solid(t.track("shape", "Cinta"), "#FFFFFF", a, dur, Box(cx - 20, 890, 40, 260), motion(), alpha=0.9)
        rrect(t, t.track("shape", "Tapa"), c2, a, dur, Box(cx - 160, 850, 320, 80), 18, motion=motion(lid=True))
        t.text(t.track("text", "Interrogación"), "?", a, dur, centered(cx, 1030, 280, 240),
               text_style("Lilita One", 170, heavy("#FFFFFF", 8, drop=8), weight=400), motion(), editable=False)
    arrow = t.solid(t.track("shape", "Flecha"), "#FFFFFF", 2.4, 2.0, centered(540, 700, 200, 130),
                    [(0, {"dy": -40}, "inout"), (0.4, {}, "inout"), (0.8, {"dy": -40}, "inout"), (1.2, {}, "inout"),
                     (1.6, {"dy": -40}, "inout"), (2.0, {})],
                    kind="arrow", rotation=keys([(0, 90)]),
                    layers=[shadow("#000000", 0, 8, 0, 0.6), fill("#FFFFFF"), no_stroke()])
    geo(arrow, headSize=0.5, thickness=0.45)
    burst(t, "#FFD60A", 4.4, centered(540, 1040, 1100, 1100), peak=0.5, length=1.0)
    rays(t, "#FFD60A", 4.4, 4.6, centered(540, 1040, 1400, 1400), alpha=0.16)
    rrect(t, t.track("shape", "Marco"), "#FFFFFF", 4.5, 4.5, centered(540, 1040, 700, 700), 40, motion=pop(0, 0.45),
          layers=[shadow("#000000", 0, 18, 40, 0.45), fill("#FFFFFF"), no_stroke()])
    t.photo(t.track("video", "Premio"), "y2-money-04", 4.5, 4.5, centered(540, 1040, 640, 640), pop(0, 0.45),
            label="Tu premio")
    count_up(t, t.track("text", "Contador"), 0, 5000, "$5.000", 4.7, 1.4, Box(0, 1400, 1080, 240),
             big("Lilita One", 200, "#FFD60A", weight=400, layers=heavy("#FFD60A", 12, oc="#2B0066")), prefix="$",
             name="Premio",
             final_style=big("Lilita One", 200, "#FFD60A", weight=400, layers=heavy("#FFD60A", 12, oc="#2B0066"),
                             anim_in=tanim("pop", duration=0.3), anim_loop=tanim("pulse", amount=3, speed=1.2)))
    say(t, "¡PREMIO!", 6.1, 2.9, Box(60, 1650, 960, 150), "Lilita One", 110, "#FFFFFF", weight=400,
        layers=heavy("#FFFFFF", 8, oc="#2B0066"), anim_in=tanim("stamp", duration=0.3), name="Mensaje")
    flash(t, 4.4, 0.35, colour="#FFF4B0", peak=0.7)
    punch(t, [4.4], 0.5, 0.35)
    song(t, "fun", 0, 0.85)
    return t


def reto_intro_hype():
    t = mk(tall, 11, "yt-reto-intro-hype", "Intro de reto explosiva", "Explosive challenge intro", 8.0,
           RT + ["intro", "hype", "ritmo", "energía"], thumb_at=5.3)
    samples = ["y2-shock-01", "y2-fun-01", "y2-shock-06", "y2-fun-03", "y2-shock-03", "y2b-h-fun-01", "y2-shock-05",
               "y2-fun-01"]
    starts = [k * 0.5 for k in range(8)]
    track = t.track("video", "Cortes")
    cuts(t, samples, starts, 4.0, punch_in=True, track=track)
    t.photo(track, "y2-shock-04", 4.0, 4.0, t.full, [(0, {"s": 1.2}, "snap"), (0.3, {}, "linear"), (4.0, {"s": 1.08})],
            label="Foto principal")
    shade_bottom(t, 1000, 0.85, t0=4.0, dur=4.0)
    words = ["ESTO", "ES", "EL", "RETO", "MÁS", "LOCO", "DEL", "AÑO"]
    wt = t.track("text", "Palabras")
    for k, w in enumerate(words):
        colour = "#FFE600" if k % 2 == 0 else "#FFFFFF"
        t.text(wt, w, k * 0.5, 0.5, Box(40, 700, 1000, 520),
               text_style("Luckiest Guy", 250, heavy(colour, 16, drop=14), weight=400,
                          anim_in=tanim("pop", duration=0.15, **{"from": 160})),
               label=f"Palabra {k + 1}", rotation=keys([(0, -4 if k % 2 else 4)]))
    say(t, "EL RETO MÁS LOCO DEL AÑO", 4.1, 3.9, Box(60, 1020, 960, 600), "Luckiest Guy", 150, "#FFE600",
        weight=400, layers=heavy("#FFE600", 14, drop=12), line=1.0,
        anim_in=tanim("pop", duration=0.3, unit="word", stagger=0.12), name="Título")
    say(t, "¡NO TE LO PIERDAS!", 5.0, 3.0, Box(90, 1650, 900, 130), "Montserrat", 64, "#FFFFFF", weight=900,
        box_bg=("#FF1F3D", 1.0), box_pad=20, box_radius=16, anim_in=tanim("slide-up", duration=0.35),
        name="Subtítulo")
    flash(t, 4.0, 0.3, peak=0.8)
    punch(t, starts + [4.0], 0.5, 0.25, rgb=18)
    song(t, "electro", 0, 0.85)
    return t


def reto_marcador():
    t = mk(wide, 12, "yt-reto-marcador", "Marcador del reto", "Challenge scoreboard", 10.0,
           RT + ["marcador", "equipos", "scoreboard", "competencia"], thumb_at=8.9)
    photo_bg(t, "y2b-h-fun-01", s1=1.08, label="Tu video")
    shade_top(t, 320, 0.7)
    rrect(t, t.track("shape", "Rojo"), "#E11D48", 0.2, 9.8, Box(560, 40, 310, 140), 20,
          motion=slide_in(dx=-900, length=0.45))
    rrect(t, t.track("shape", "Azul"), "#2563EB", 0.2, 9.8, Box(1050, 40, 310, 140), 20,
          motion=slide_in(dx=900, length=0.45))
    t.solid(t.track("shape", "Marcador"), "#0B0B0F", 0.2, 9.8, Box(860, 30, 200, 160), pop(0, 0.4),
            layers=[shadow("#000000", 0, 10, 24, 0.5), fill("#0B0B0F"), stroke(4, "#FFFFFF")])
    say(t, "ROJO", 0.4, 9.6, Box(560, 40, 290, 140), "Oswald", 64, "#FFFFFF", weight=700, spacing=4,
        name="Equipo 1")
    say(t, "AZUL", 0.4, 9.6, Box(1070, 40, 290, 140), "Oswald", 64, "#FFFFFF", weight=700, spacing=4,
        name="Equipo 2")
    t.solid(t.track("shape", "Separador"), "#FFFFFF", 0.4, 9.6, Box(957, 70, 6, 80), alpha=0.6)
    score = lambda colour="#FFFFFF": (lambda k: text_style("Teko", 130, [fill(colour)], weight=700,  # noqa: E731
                                                          anim_in=tanim("pop", duration=0.3, **{"from": 180})))
    seq(t, [(0.4, 2.6, "0"), (3.0, 5.5, "1"), (8.5, 1.5, "2")], Box(860, 40, 100, 150), score(),
        name="Puntos rojo", labels=[None, None, "Puntos rojo"])
    seq(t, [(0.4, 5.6, "0"), (6.0, 4.0, "1")], Box(960, 40, 100, 150), score(), name="Puntos azul",
        labels=[None, "Puntos azul"])
    for at, colour in [(3.0, "#E11D48"), (6.0, "#2563EB"), (8.5, "#E11D48")]:
        say(t, "¡PUNTO!", at, 1.3, Box(0, 800, 1920, 220), "Bebas Neue", 200, "#FFFFFF", weight=400,
            box_bg=(colour, 0.92), box_pad=16, layers=[shadow("#000000", 0, 8, 0, 0.6), fill("#FFFFFF")],
            anim_in=tanim("slide-left", duration=0.25, distance=0.6),
            anim_out=tanim("slide-left", duration=0.25, distance=0.6), editable=False)
        flash(t, at, 0.25, colour=colour, peak=0.35)
    say(t, "2° TIEMPO", 0.6, 9.4, Box(810, 200, 300, 50), "Oswald", 34, "#FFFFFF", weight=600, spacing=6,
        box_bg=("#000000", 0.6), box_pad=8, name="Tiempo")
    punch(t, [3.0, 6.0, 8.5], 0.35, 0.3, shake=0.2)
    t.song("bar-brawl", 0.0, 0.85)
    return t


def reto_aguanta_60():
    t = mk(tall, 13, "yt-reto-aguanta-60-minutos", "Si aguantas, ganas", "Last 60 minutes, win", 10.0,
           RT + ["temporizador", "aguantar", "minutos", "timer"], thumb_at=9.0, background="#000000")
    photo_bg(t, "beach-01", s1=1.08, label="Tu foto o video")
    shade_full(t, 0.6, colour="#001A0F")
    say(t, "SI AGUANTAS", 0.2, 9.8, Box(60, 160, 960, 120), "Orbitron", 84, "#FFFFFF", weight=800,
        anim_in=tanim("fade", duration=0.4), name="Antetítulo")
    say(t, "60 MINUTOS", 0.5, 9.5, Box(60, 280, 960, 170), "Orbitron", 120, "#00FF88", weight=900,
        layers=[glow("#00FF88", 30, 0.7), fill("#00FF88")], anim_in=tanim("flicker-in", duration=0.6),
        name="Título")
    say(t, "GANAS $1.000", 0.8, 9.2, Box(60, 450, 960, 130), "Orbitron", 88, "#FFE600", weight=900,
        anim_in=tanim("fade", duration=0.4), name="Premio")
    rrect(t, t.track("shape", "Panel"), "#000000", 0.6, 9.4, Box(110, 760, 860, 360), 34,
          layers=[fill("#000000", 0.65), stroke(5, "#00FF88"), glow("#00FF88", 24, 0.5)])
    count_fn(t, t.track("text", "Reloj"), lambda f: 3600 * ease_out(f, 1.5),
             lambda v: f"{int(v) // 60:02d}:{int(v) % 60:02d}", 1.0, 7.0, "60:00", Box(110, 780, 860, 320),
             big("Orbitron", 170, "#00FF88", weight=800, layers=[glow("#00FF88", 22, 0.6), fill("#00FF88")]),
             name="Tiempo final",
             final_style=big("Orbitron", 170, "#FFE600", weight=800, layers=[glow("#FFE600", 26, 0.7), fill("#FFE600")],
                             anim_in=tanim("pop", duration=0.3)))
    rrect(t, t.track("shape", "Carril"), "#FFFFFF", 0.8, 9.2, Box(140, 1180, 800, 30), 15, alpha=0.18)
    t.solid(t.track("shape", "Barra"), "#00FF88", 0.8, 9.2, Box(140, 1180, 800, 30),
            curve_motion(lambda f: 0.01 + 0.99 * ease_out(f, 1.5), 7.0, 800, at=0.2), radius=15,
            kind="rounded-rectangle", layers=[glow("#00FF88", 16, 0.6), fill("#00FF88"), no_stroke()])
    say(t, "¡LO LOGRÓ!", 8.1, 1.9, Box(60, 1300, 960, 180), "Orbitron", 120, "#FFE600", weight=900,
        layers=[shadow("#000000", 0, 8, 0, 0.9), fill("#FFE600")], anim_in=tanim("stamp", duration=0.3),
        name="Mensaje")
    confetti(t, ["#00FF88", "#FFE600", "#FFFFFF"], 8.0, 2.0, seed=6013, lanes=3, density=0.22)
    flash(t, 8.0, 0.3, colour="#00FF88", peak=0.4)
    song(t, "electro", 2, 0.85)
    return t


def reto_gasta_todo():
    t = mk(wide, 14, "yt-reto-gasta-1000", "Gasta $1.000 en 1 minuto", "Spend $1,000 in 1 minute", 10.0,
           RT + ["compras", "dinero", "shopping", "temporizador"], thumb_at=8.8, background="#FFE600")
    bg(t, "#FFE600")
    rrect(t, t.track("shape", "Marco"), "#111111", 0.0, 10.0, Box(66, 126, 1028, 828), 36,
          layers=[shadow("#000000", 0, 18, 0, 1.0), fill("#111111"), no_stroke()])
    cuts(t, ["shopping-01", "shopping-02", "shopping-03", "shopping-04"], [0.0, 2.4, 4.8, 7.2], 10.0,
         box=Box(80, 140, 1000, 800), kbs=0.0)
    say(t, "GASTA", 0.2, 9.8, Box(1150, 110, 720, 110), "Archivo Black", 88, "#111111", weight=400, align="left",
        anim_in=tanim("slide-left", duration=0.4, distance=0.2), name="Título 1")
    say(t, "$1.000", 0.4, 9.6, Box(1150, 200, 720, 220), "Archivo Black", 190, "#111111", weight=400, align="left",
        layers=[shadow("#FFFFFF", 8, 8, 0, 1.0), fill("#111111")],
        anim_in=tanim("slide-left", duration=0.4, distance=0.2), name="Título 2")
    say(t, "EN 1 MINUTO", 0.6, 9.4, Box(1150, 410, 720, 110), "Archivo Black", 82, "#111111", weight=400,
        align="left", anim_in=tanim("slide-left", duration=0.4, distance=0.2), name="Título 3")
    rrect(t, t.track("shape", "Panel"), "#111111", 0.8, 9.2, Box(1150, 560, 700, 400), 30,
          motion=slide_in(dy=600, length=0.45))
    say(t, "SALDO", 1.0, 9.0, Box(1190, 585, 300, 60), "Archivo Black", 40, "#FFE600", weight=400, align="left",
        spacing=6, name="Etiqueta saldo")
    count_fn(t, t.track("text", "Saldo"), lambda f: 1000 * (1 - ease_out(f, 1.2)), lambda v: f"${int(round(v))}",
             1.2, 7.0, "$0", Box(1190, 640, 640, 170), big("Archivo Black", 140, "#FFFFFF", weight=400, align="left"),
             name="Saldo final", step=3,
             final_style=big("Archivo Black", 140, "#FF3B30", weight=400, align="left",
                             anim_in=tanim("pop", duration=0.3)))
    say(t, "TIEMPO", 1.0, 9.0, Box(1190, 830, 300, 60), "Archivo Black", 40, "#FFE600", weight=400, align="left",
        spacing=6, name="Etiqueta tiempo")
    count_fn(t, t.track("text", "Tiempo"), lambda f: 60 * (1 - f), lambda v: mmss(math.ceil(v)), 1.2, 7.0, "0:00",
             Box(1450, 815, 380, 100), big("Archivo Black", 76, "#FFFFFF", weight=400, align="right"),
             name="Tiempo final", step=3)
    t.solid(t.track("shape", "Banda"), "#FF3B30", 8.3, 1.7, centered(580, 540, 820, 170), pop(0, 0.35),
            rotation=keys([(0, -6)]), layers=[shadow("#000000", 0, 10, 0, 1.0), fill("#FF3B30"), no_stroke()])
    say(t, "¡LO LOGRÉ!", 8.35, 1.65, centered(580, 540, 820, 170), "Archivo Black", 110, "#FFFFFF", weight=400,
        rotation=keys([(0, -6)]), anim_in=tanim("stamp", duration=0.3), name="Mensaje")
    punch(t, [2.4, 4.8, 7.2, 8.3], 0.25, 0.3)
    song(t, "jazz", 3, 0.85)
    return t


def reto_ganador():
    t = mk(wide, 15, "yt-reto-ganador", "Y el ganador es…", "And the winner is…", 8.0,
           RT + ["ganador", "revelación", "premio", "winner"], thumb_at=6.3, background="#000000")
    bg(t, "#000000")
    t.solid(t.track("shape", "Foco"), "#FFFFFF", 0.0, 2.7, centered(960, 560, 900, 900), kind="ellipse",
            layers=[glow("#FFF3C4", 120, 0.35), fill("#FFF3C4", 0.08), no_stroke()],
            opacity=keys([(0, 0.0, "smooth"), (0.6, 1.0)]))
    say(t, "Y EL GANADOR ES…", 0.2, 2.5, Box(0, 420, 1920, 240), "Bebas Neue", 170, "#FFFFFF", weight=400,
        spacing=8, anim_in=tanim("typewriter", duration=1.2, unit="character"), name="Antetítulo")
    rays(t, "#FFC83D", 2.6, 5.4, centered(560, 540, 1400, 1400), alpha=0.14, speed=15)
    framed(t, "y2-h-shock-04", 2.6, 5.4, Box(120, 140, 900, 780), pop(0, 0.5, s0=0.6), border=16,
           colour="#FFC83D", radius=10, label="Foto del ganador")
    say(t, "¡GANADOR!", 2.8, 5.2, Box(1070, 200, 830, 230), "Luckiest Guy", 136, "#FFC83D", weight=400,
        layers=gold_text(), anim_in=tanim("stamp", duration=0.35), name="Mensaje")
    say(t, "Carlos Méndez", 3.1, 4.9, Box(1090, 440, 800, 120), "Montserrat", 80, "#FFFFFF", weight=900,
        anim_in=tanim("rise", duration=0.4), name="Nombre")
    say(t, "SE LLEVA", 3.3, 4.7, Box(1090, 570, 800, 60), "Montserrat", 40, "#FFC83D", weight=800, spacing=10,
        name="Antes del premio")
    count_up(t, t.track("text", "Premio"), 0, 100_000, "$100.000", 3.4, 1.8, Box(1080, 620, 820, 220),
             big("Anton", 170, "#3DFF6E", weight=400, layers=heavy("#3DFF6E", 10)), prefix="$", name="Premio",
             final_style=big("Anton", 170, "#3DFF6E", weight=400, layers=heavy("#3DFF6E", 10, glow_c="#3DFF6E"),
                             anim_in=tanim("pop", duration=0.3)))
    confetti(t, ["#FFC83D", "#FFFFFF", "#3DFF6E", "#FF3B5C"], 2.6, 5.4, seed=6015, lanes=4, density=0.22)
    flash(t, 2.6, 0.4, peak=0.9)
    punch(t, [2.6], 0.5, 0.4)
    song(t, "epic", 0, 0.85)
    return t


def reto_1_vs_100():
    t = mk(tall, 16, "yt-reto-1-vs-100", "1 vs 100", "1 vs 100", 8.0,
           RT + ["1 vs 100", "versus", "duelo", "versus challenge"], thumb_at=4.5, background="#000000")
    bg(t, "#000000")
    t.photo(t.track("video", "Uno"), "y2-shock-06", 0.0, 8.0, Box(0, 0, 1080, 1000),
            [(0, {"dy": -1000}, "out"), (0.5, {}, "linear"), (8.0, {"s": 1.06})], label="Foto del 1")
    t.photo(t.track("video", "Cien"), "y2-fun-01", 0.2, 7.8, Box(0, 920, 1080, 1000),
            [(0, {"dy": 1000}, "out"), (0.5, {}, "linear"), (7.8, {"s": 1.06})], label="Foto de los 100")
    t.solid(t.track("shape", "Banda"), "#000000", 0.6, 7.4, centered(540, 960, 1500, 280),
            slide_in(dx=-1600, length=0.35), rotation=keys([(0, -8)]))
    t.solid(t.track("shape", "Filo"), "#FFE600", 0.7, 7.3, centered(540, 1092, 1500, 16),
            slide_in(dx=1600, length=0.35), rotation=keys([(0, -8)]))
    say(t, "¿QUIÉN GANA?", 1.6, 6.4, centered(380, 975, 760, 140), "Bebas Neue", 110, "#FFFFFF", weight=400,
        rotation=keys([(0, -8)]), anim_in=tanim("slide-right", duration=0.3, distance=0.3), name="Pregunta")
    say(t, "1", 0.5, 7.5, Box(40, 80, 520, 640), "Anton", 560, "#FFFFFF", weight=400, align="left",
        layers=heavy("#FFFFFF", 18, drop=16), anim_in=tanim("stamp", duration=0.35), name="Número 1")
    say(t, "100", 0.8, 7.2, Box(360, 1260, 680, 600), "Anton", 420, "#FFE600", weight=400, align="right",
        layers=heavy("#FFE600", 18, drop=16), anim_in=tanim("stamp", duration=0.35), name="Número 2")
    bolt = t.solid(t.track("shape", "Rayo"), "#FF1F3D", 1.2, 6.8, centered(860, 960, 230, 330), pop(0, 0.35, s0=2.0),
                   kind="lightning-bolt", layers=[shadow("#000000", 0, 10, 0, 1.0), stroke(8, "#FFFFFF"),
                                                  fill("#FF1F3D")])
    say(t, "VS", 1.3, 6.7, centered(860, 975, 260, 170), "Luckiest Guy", 130, "#FFFFFF", weight=400,
        layers=heavy("#FFFFFF", 8), anim_in=tanim("pop", duration=0.3), anim_loop=tanim("jitter", amount=1.5,
                                                                                         angle=3, speed=10),
        editable=False)
    flash(t, 1.2, 0.3, peak=0.6)
    punch(t, [0.5, 0.8, 1.2], 0.4, 0.3, shake=0.25)
    t.song("go-on-without-me", 0.0, 0.85)
    return t


def reto_10_dolares():
    t = mk(tall, 17, "yt-reto-10-dolares-7-dias", "Vivo con $10 por 7 días", "Living on $10 for 7 days", 12.0,
           RT + ["ahorro", "presupuesto", "budget", "7 días"], thumb_at=10.5)
    cuts(t, ["y2-dish-04", "food-02", "coffee-01", "y2-dish-06"], [0.0, 3.0, 6.0, 9.0], 12.0,
         transition="push_left", tdur=0.3, labels=["Día 1", "Día 3", "Día 5", "Día 7"])
    shade_top(t, 520, 0.7)
    shade_bottom(t, 700, 0.6)
    say(t, "VIVO CON $10", 0.2, 11.8, Box(60, 100, 960, 170), "Paytone One", 120, "#FFFFFF", weight=400,
        box_bg=("#16A34A", 1.0), box_pad=22, box_radius=24, anim_in=tanim("pop", duration=0.4), name="Título")
    say(t, "POR 7 DÍAS", 0.5, 11.5, Box(60, 300, 960, 110), "Paytone One", 80, "#FFFFFF", weight=400,
        layers=heavy("#FFFFFF", 6, drop=6), anim_in=tanim("rise", duration=0.4), name="Subtítulo")
    rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", 0.3, 11.7, Box(60, 1460, 960, 380), 40,
          motion=slide_in(dy=600, length=0.5), layers=[shadow("#000000", 0, 20, 40, 0.4), fill("#FFFFFF"), no_stroke()])
    t.solid(t.track("shape", "Divisor"), "#E5E7EB", 0.5, 11.5, Box(400, 1500, 4, 300))
    say(t, "DÍA", 0.5, 11.5, Box(100, 1490, 280, 70), "Paytone One", 50, "#6B7280", weight=400, name="Etiqueta día")
    say(t, "SALDO", 0.5, 11.5, Box(440, 1490, 540, 70), "Paytone One", 50, "#6B7280", weight=400,
        name="Etiqueta saldo")
    day = lambda k: text_style("Paytone One", 200, [fill("#111827")], weight=400,  # noqa: E731
                               anim_in=tanim("slide-up", duration=0.3))
    seq(t, [(0.5, 2.5, "1"), (3.0, 3.0, "3"), (6.0, 3.0, "5"), (9.0, 3.0, "7")], Box(100, 1550, 280, 260), day,
        name="Día", labels=[None, None, None, "Día final"])
    money = lambda k: text_style("Paytone One", 150, [fill("#16A34A" if k < 3 else "#DC2626")], weight=400,  # noqa: E731
                                 anim_in=tanim("pop", duration=0.3))
    seq(t, [(0.5, 2.5, "$10,00"), (3.0, 3.0, "$7,50"), (6.0, 3.0, "$4,20"), (9.0, 3.0, "$0,80")],
        Box(440, 1560, 560, 240), money, name="Saldo", labels=[None, None, None, "Saldo final"])
    for at, txt in [(3.0, "-$2,50"), (6.0, "-$3,30"), (9.0, "-$3,40")]:
        say(t, txt, at + 0.1, 1.2, Box(560, 1380, 420, 90), "Paytone One", 70, "#DC2626", weight=400,
            layers=heavy("#DC2626", 6, oc="#FFFFFF", drop=0), motion=[(0, {}, "out"), (1.2, {"dy": -120})],
            opacity=keys([(0, 1.0, "hold"), (0.8, 1.0, "smooth"), (1.2, 0.0)]), editable=False)
    punch(t, [3.0, 6.0, 9.0], 0.25, 0.3)
    song(t, "upbeat", 6, 0.85)
    return t


# =====================================================================================================
# 2. TOP 10 / RANKING
# =====================================================================================================

def top_10_rapido():
    t = mk(tall, 18, "yt-top-10-rapido", "Top 10 rápido", "Fast top 10", 13.0,
           TP + ["lista", "cuenta regresiva", "countdown"], thumb_at=11.6, background="#000000")
    bg(t, "#000000")
    say(t, "TOP", 0.0, 1.0, Box(60, 520, 960, 260), "Anton", 220, "#FFFFFF", weight=400, layers=heavy("#FFFFFF", 10),
        anim_in=tanim("slide-down", duration=0.3), name="Intro 1")
    say(t, "10", 0.15, 0.85, Box(60, 740, 960, 640), "Anton", 600, "#FFE600", weight=400,
        layers=heavy("#FFE600", 16), anim_in=tanim("stamp", duration=0.3), name="Intro 2")
    samples = ["y2-dish-01", "travel-01", "y2-dish-04", "beach-01", "y2-dish-06", "nature-02", "food-02", "city-01",
               "y2-dish-01", "travel-05"]
    starts = [1.0 + i for i in range(10)]
    starts[-1] = 10.0
    names = ["Pasta casera", "Un mirador", "Fideos salteados", "Playa escondida", "Brunch completo", "Montañas",
             "Tacos al paso", "Paseo de noche", "Cóctel de frutas", "El viaje de mi vida"]
    cuts(t, samples, starts, 13.0, punch_in=True, labels=[f"Puesto {10 - i}" for i in range(10)])
    shade_bottom(t, 900, 0.9, t0=1.0, dur=12.0)
    rays(t, "#FFC83D", 10.0, 3.0, centered(300, 1330, 1100, 1100), alpha=0.18)
    nt = t.track("text", "Número")
    tt = t.track("text", "Puesto")
    for i in range(10):
        n = 10 - i
        a = starts[i]
        d = (starts[i + 1] if i < 9 else 13.0) - a
        if n == 1:
            st = text_style("Anton", 380, gold_text(14), weight=400, align="left",
                            anim_in=tanim("stamp", duration=0.35))
        else:
            st = text_style("Anton", 300, heavy("#FFE600", 14, drop=12), weight=400, align="left",
                            anim_in=tanim("pop", duration=0.2, **{"from": 150}))
        t.text(nt, f"#{n}", a, d, Box(50, 1120, 900, 420), st, editable=False)
        t.text(tt, names[i], a + 0.05, d - 0.05, Box(60, 1520, 960, 240),
               text_style("Montserrat", 80, [shadow("#000000", 0, 6, 12, 0.6), fill("#FFFFFF")], weight=900,
                          align="left", valign="top", anim_in=tanim("slide-right", duration=0.25, distance=0.2)),
               label=f"Puesto {n}")
    say(t, "TOP 10", 1.0, 12.0, Box(50, 70, 260, 90), "Anton", 60, "#FFE600", weight=400,
        box_bg=("#000000", 0.75), box_pad=14, box_radius=12, name="Etiqueta")
    confetti(t, ["#FFC83D", "#FFFFFF", "#FF3B5C"], 10.0, 3.0, seed=6018, lanes=3, density=0.25)
    flash(t, 10.0, 0.35, colour="#FFE9A8", peak=0.7)
    punch(t, starts, 0.25, 0.25)
    song(t, "upbeat", 0, 0.85)
    return t


def top_podio():
    t = mk(wide, 19, "yt-top-3-podio", "Podio top 3", "Top 3 podium", 10.0,
           TP + ["podio", "top 3", "ganadores", "podium"], thumb_at=7.5, background="#0D0221")
    bg_gradient(t, [(0, "#2B0F54"), (1, "#0D0221")], angle=90)
    dots(t, ["#FFFFFF", "#FFC83D"], 22, 0.0, 10.0, seed=6019, size=(4, 12), drift=60, alpha=0.6)
    rays(t, "#FFC83D", 5.5, 4.5, centered(960, 560, 1500, 1500), alpha=0.12, speed=12)
    say(t, "TOP 3 DEL AÑO", 0.2, 9.8, Box(0, 40, 1920, 150), "Montserrat", 110, "#FFFFFF", weight=900, spacing=6,
        anim_in=tanim("pop", duration=0.4, unit="word", stagger=0.1), name="Título")
    podium = [  # place, centre x, height, colour, reveal
        (2, 660, 280, "#C0C7D1", 3.2), (1, 960, 380, "#FFC83D", 5.5), (3, 1260, 200, "#D08A4C", 1.5)]
    samples = {1: "h-portrait-01", 2: "h-man-02", 3: "h-portrait-04"}
    names = {1: "Lucía", 2: "Mateo", 3: "Sofía"}
    for place, cx, h, colour, at in podium:
        top = 1080 - h
        t.solid(t.track("shape", "Podio"), colour, 0.2, 9.8, Box(cx - 150, top, 300, h),
                [(0, {"dy": h + 40}, "out"), (0.6, {})],
                layers=[gradient([(0, colour), (1, "#000000", 0.0)], angle=90), fill(colour, 0.85), no_stroke()])
        say(t, str(place), 0.5, 9.5, Box(cx - 150, top + 10, 300, 170), "Montserrat", 140, "#1A1030", weight=900,
            anim_in=tanim("rise", duration=0.4), editable=False)
        box = centered(cx, top - 150, 250, 250)
        disc(t, samples[place], at, 10.0 - at, box, pop(0, 0.45), label=f"Puesto {place}", ring_c=colour, ring_w=10)
        say(t, names[place], at + 0.1, 9.9 - at, Box(cx - 260, top - 370, 520, 80), "Montserrat", 56, "#FFFFFF",
            weight=900, anim_in=tanim("rise", duration=0.35), name=f"Nombre {place}")
        flash(t, at, 0.25, colour=colour, peak=0.3)
    crown = t.solid(t.track("shape", "Corona"), "#FFC83D", 5.7, 4.3, centered(840, 440, 120, 100),
                    [(0, {"s": 0.0, "dy": -60}, "back"), (0.45, {})], kind="star",
                    layers=[shadow("#000000", 0, 6, 0, 0.6), fill("#FFC83D"), no_stroke()],
                    rotation=keys([(0, -8, "inout"), (1.0, 8, "inout"), (2.0, -8, "inout"), (3.0, 8, "inout"),
                                   (4.3, -8)]))
    geo(crown, points=5, innerRatio=0.45)
    confetti(t, ["#FFC83D", "#FFFFFF", "#C0C7D1", "#D08A4C"], 5.5, 4.5, seed=6019, lanes=4, density=0.22)
    punch(t, [1.5, 3.2, 5.5], 0.3, 0.3)
    song(t, "epic", 2, 0.85)
    return t


def top_tarjetas():
    t = mk(tall, 20, "yt-top-5-tarjetas", "Top 5 en tarjetas", "Top 5 cards", 12.0,
           TP + ["top 5", "favoritos", "tarjetas", "favorites"], thumb_at=10.6, background="#FFEFD6")
    bg(t, "#FFEFD6")
    dots(t, ["#FFB4A2", "#B5E2FA", "#FFE066"], 16, 0.0, 12.0, seed=6020, size=(16, 40), drift=80, alpha=0.7)
    say(t, "MIS 5 FAVORITOS", 0.1, 11.9, Box(60, 110, 960, 140), "Poppins", 90, "#2D1E4F", weight=800,
        anim_in=tanim("pop", duration=0.35, unit="word", stagger=0.1), name="Título")
    badges = ["#FF6B6B", "#4ECDC4", "#FFB703", "#8E7DFF", "#FF4D8D"]
    samples = ["cafe-01", "beach-01", "y2-dish-05", "night-01", "travel-07"]
    names = ["Café de la esquina", "Atardecer en la playa", "Desayuno del domingo", "Noche en la ciudad",
             "Mi viaje favorito"]
    angles = [-3, 2.5, -2, 3, 0]
    for k in range(5):
        n = 5 - k
        a = 0.6 + k * 2.2
        d = 12.0 - a
        m = [(0, {"dx": 1100}, "out"), (0.55, {})]
        rot = keys([(0, angles[k])])
        rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", a, d, Box(110, 330, 860, 1300), 48, motion=m,
              layers=[shadow("#5A3E2B", 0, 20, 50, 0.3), fill("#FFFFFF"), no_stroke()], rotation=rot)
        t.photo(t.track("video", "Foto"), samples[k], a, d, Box(150, 370, 780, 960), m, label=f"Puesto {n}",
                rotation=rot)
        t.solid(t.track("shape", "Insignia"), badges[k], a, d, centered(200, 390, 180, 180), m, kind="ellipse",
                layers=[shadow("#000000", 0, 8, 16, 0.3), stroke(8, "#FFFFFF"), fill(badges[k])])
        t.text(t.track("text", "Número"), str(n), a, d, centered(200, 392, 180, 180),
               text_style("Poppins", 110, [fill("#FFFFFF")], weight=900), m, editable=False)
        t.text(t.track("text", "Nombre"), names[k], a, d, Box(150, 1350, 780, 250),
               text_style("Poppins", 66, [fill("#2D1E4F")], weight=800, line=1.05), m, label=f"Nombre {n}",
               rotation=rot)
    t.adjust([effect("bling_sparkle", intensity=0.5, density=0.3, threshold=0.85)], 9.4, 2.6, name="Brillos")
    confetti(t, badges, 9.4, 2.6, seed=6020, lanes=3, density=0.3)
    song(t, "upbeat", 3, 0.85)
    return t


def top_lista_lateral():
    t = mk(wide, 21, "yt-top-10-lista", "Top 10 con lista", "Top 10 with list", 14.0,
           TP + ["lista", "top 10", "cuenta regresiva", "countdown"], thumb_at=12.6, background="#0B1020")
    bg(t, "#0B1020")
    samples = ["y2-h-place-01", "y2-h-place-02", "h-travel-02", "y2-h-place-05", "h-travel-03", "h-city-02",
               "y2-h-place-07", "h-beach-02", "y2-h-place-06", "y2-h-place-03"]
    starts = [0.6 + i * 1.2 for i in range(10)]
    cuts(t, samples, starts, 14.0, box=Box(760, 0, 1160, 1080), transition="crossfade", tdur=0.2, kbs=0.05,
         labels=[f"Puesto {10 - i}" for i in range(10)])
    t.solid(t.track("shape", "Sombra"), "#000000", 0.0, 14.0, Box(760, 700, 1160, 380),
            layers=[gradient([(0, "#000000", 0.0), (1, "#000000", 0.75)], angle=90), no_stroke()])
    t.solid(t.track("shape", "Panel"), "#0B1020", 0.0, 14.0, Box(0, 0, 760, 1080))
    say(t, "TOP 10", 0.0, 14.0, Box(60, 30, 640, 110), "Oswald", 90, "#FFFFFF", weight=700, align="left",
        anim_in=tanim("slide-right", duration=0.4, distance=0.2), name="Título")
    line(t, t.track("shape", "Línea"), "#FF3D71", 0.2, 13.8, Box(60, 138, 220, 8), length=0.5)
    names = ["Islas blancas", "La gran mezquita", "Desierto rojo", "Templo dorado", "Lago azul", "Ciudad de noche",
             "Castillo del lago", "Playa secreta", "Palacio blanco", "Maravilla del mundo"]
    hl = t.track("shape", "Resalte")
    for i in range(10):
        r = 10 - i
        a = starts[i]
        end = starts[i + 1] if i < 9 else 14.0
        y = 170 + (r - 1) * 88
        t.solid(hl, "#FFC83D" if r == 1 else "#FF3D71", a, end - a, Box(40, y + 4, 680, 80),
                [(0, {"sx": 0.0, "dx": -340}, "out"), (0.3, {})], radius=12, kind="rounded-rectangle")
    for r in range(1, 11):
        y = 170 + (r - 1) * 88
        a = starts[10 - r]
        say(t, f"{r:02d}", 0.3, 13.7, Box(60, y, 110, 88), "Oswald", 52, "#7C86A8", weight=700, align="left",
            editable=False, anim_in=tanim("fade", duration=0.3))
        say(t, names[10 - r], a, 14.0 - a, Box(170, y, 540, 88), "Oswald", 44, "#FFFFFF", weight=600, align="left",
            anim_in=tanim("slide-right", duration=0.3, distance=0.15), name=f"Puesto {r}")
    nt = t.track("text", "Número")
    for i in range(10):
        r = 10 - i
        a = starts[i]
        end = starts[i + 1] if i < 9 else 14.0
        t.text(nt, f"#{r}", a, end - a, Box(800, 760, 700, 300),
               text_style("Oswald", 230, [shadow("#000000", 0, 8, 20, 0.6), fill("#FFC83D" if r == 1 else "#FFFFFF")],
                          weight=700, align="left", anim_in=tanim("slide-up", duration=0.3)), editable=False)
    flash(t, starts[-1], 0.3, colour="#FFC83D", peak=0.4)
    confetti(t, ["#FFC83D", "#FF3D71", "#FFFFFF"], starts[-1], 14.0 - starts[-1], seed=6021, lanes=3, density=0.3)
    song(t, "electro", 1, 0.85)
    return t


def top_cine():
    t = mk(wide, 22, "yt-top-5-cine", "Top 5 cinematográfico", "Cinematic top 5", 13.0,
           TP + ["cine", "viajes", "elegante", "cinematic"], thumb_at=11.9, background="#000000")
    bg(t, "#000000")
    starts = [1.5 + k * 2.3 for k in range(5)]
    cuts(t, ["y2-h-place-01", "y2-h-place-02", "y2-h-place-05", "y2-h-place-06", "y2-h-place-03"], starts, 13.0,
         transition="dip", tdur=0.4, kbs=0.08, labels=[f"Puesto {5 - k}" for k in range(5)])
    t.solid(t.track("shape", "Velo"), "#000000", 1.5, 11.5, Box(0, 0, 1100, 1080),
            layers=[gradient([(0, "#000000", 0.7), (1, "#000000", 0.0)], angle=0), no_stroke()])
    say(t, "Cinco lugares que te cambian la vida", 0.1, 1.4, Box(260, 380, 1400, 320), "Cormorant Garamond", 96,
        "#F2E6C9", weight=500, italic=True, anim_in=tanim("blur-in", duration=0.8),
        anim_out=tanim("fade", duration=0.3), name="Título")
    places = [("Islas blancas", "GRECIA"), ("La gran mezquita", "TURQUÍA"), ("Templo del lago", "TAILANDIA"),
              ("Templo de cristal", "TAILANDIA"), ("El palacio de mármol", "INDIA")]
    nt, tt, ct = t.track("text", "Número"), t.track("text", "Lugar"), t.track("text", "País")
    for k in range(5):
        n = 5 - k
        a = starts[k] + 0.3
        d = (starts[k + 1] if k < 4 else 13.0) - a
        t.text(nt, f"0{n}", a, d, Box(110, 200, 700, 480),
               text_style("Cormorant Garamond", 420, [stroke(5, "#F2E6C9"), fill("#F2E6C9", 0.12)], weight=600,
                          align="left", anim_in=tanim("fade", duration=0.6)), editable=False)
        t.text(tt, places[k][0], a + 0.2, d - 0.2, Box(120, 690, 1200, 110),
               text_style("Cormorant Garamond", 84, [fill("#F2E6C9")], weight=500, italic=True, align="left",
                          anim_in=tanim("blur-in", duration=0.6)), label=f"Lugar {n}")
        t.text(ct, places[k][1], a + 0.4, d - 0.4, Box(124, 800, 900, 60),
               text_style("Montserrat", 30, [fill("#C9A86A")], weight=600, spacing=14, align="left",
                          anim_in=tanim("fade", duration=0.5)), label=f"País {n}")
    letterbox(t, 2.39)
    t.adjust([effect("cinematic_grade", strength=0.5), effect("stylize.film_grain", amount=0.2),
              effect("stylize.vignette", amount=0.5)], name="Look")
    song(t, "cine", 2, 0.85)
    return t


def top_neon():
    t = mk(tall, 23, "yt-top-5-neon", "Top 5 neón", "Neon top 5", 11.0,
           TP + ["neón", "gaming", "noche", "neon"], thumb_at=9.6, background="#07001A")
    bg_gradient(t, [(0, "#14002E"), (1, "#07001A")], angle=90)
    dots(t, ["#00F0FF", "#FF2BD6"], 24, 0.0, 11.0, seed=6023, size=(4, 10), drift=90, alpha=0.6)
    starts = [0.5 + k * 2.0 for k in range(5)]
    cuts(t, ["night-01", "concert-01", "city-03", "night-03", "concert-03"], starts, 11.0,
         box=Box(150, 650, 780, 980), kbs=0.05, labels=[f"Puesto {5 - k}" for k in range(5)],
         effects=[effect("color.basic", saturation=0.25, contrast=0.2)])
    t.solid(t.track("shape", "Neón"), "#FF2BD6", 0.3, 10.7, Box(130, 630, 820, 1020), radius=36,
            kind="rounded-rectangle",
            layers=[halo("#FF2BD6"), {"id": "fill", "kind": "fill", "enabled": False,
                                                "paint": {"kind": "solid", "color": "#00000000"}},
                    {"id": "stroke", "kind": "stroke", "enabled": True, "width": 10, "strokeAlign": "inside",
                     "paint": {"kind": "solid", "color": "#ffff2bd6"}, "opacity": 1.0}])
    nt, tt = t.track("text", "Número"), t.track("text", "Nombre")
    names = ["Neón azul", "El concierto", "Luces de ciudad", "Fiesta nocturna", "La mejor noche"]
    for k in range(5):
        n = 5 - k
        a = starts[k]
        d = (starts[k + 1] if k < 4 else 11.0) - a
        colour = "#FFE600" if n == 1 else "#00F0FF"
        t.text(nt, str(n), a, d, Box(60, 150, 960, 460),
               text_style("Monoton", 400, [glow(colour, 40, 0.9), fill(colour)], weight=400,
                          anim_in=tanim("flicker-in", duration=0.5), anim_loop=tanim("flicker", intensity=0.15, speed=3)),
               editable=False)
        t.text(tt, names[k], a + 0.2, d - 0.2, Box(60, 1690, 960, 170),
               text_style("Audiowide", 70, [glow("#FF2BD6", 20, 0.7), fill("#FFFFFF")], weight=400,
                          anim_in=tanim("glitch-in", duration=0.4)), label=f"Puesto {n}")
    flash(t, starts[-1], 0.3, colour="#00F0FF", peak=0.35)
    punch(t, starts, 0.25, 0.25, rgb=10)
    song(t, "electro", 3, 0.85)
    return t


def top_revelacion():
    t = mk(tall, 24, "yt-top-3-revelacion", "Revelación del número 1", "Number one reveal", 12.0,
           TP + ["top 3", "revelación", "número 1", "reveal"], thumb_at=9.7)
    track = t.track("video", "Fotos")
    cuts(t, ["travel-03", "travel-07"], [0.0, 3.0], 6.0, punch_in=True, labels=["Puesto 3", "Puesto 2"],
         track=track)
    t.photo(track, "travel-09", 6.0, 2.6, t.full, kb(2.6, 1.15, 1.2), label="Puesto 1",
            effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=40)])
    t.photo(track, "", 8.6, 3.4, t.full, [(0, {"s": 1.2}, "snap"), (0.3, {}, "linear"), (3.4, {"s": 1.06})],
            reuse="p3")
    shade_bottom(t, 900, 0.85)
    t.solid(t.track("shape", "Oscuro"), "#000000", 6.0, 2.6, alpha=0.45)
    say(t, "LOS 3 MEJORES", 0.1, 11.9, Box(60, 80, 600, 100), "Bangers", 70, "#FFFFFF", weight=400, align="left",
        box_bg=("#FF6B00", 1.0), box_pad=14, box_radius=12, name="Etiqueta")
    for k, (n, a, d, name) in enumerate([(3, 0.1, 2.9, "Montaña sagrada"), (2, 3.1, 2.9, "Mercado de colores")]):
        t.solid(t.track("shape", "Insignia"), "#FF6B00", a, d, centered(200, 1330, 260, 260), pop(0, 0.35),
                kind="ellipse", layers=[shadow("#000000", 0, 10, 0, 0.9), stroke(10, "#FFFFFF"), fill("#FF6B00")])
        say(t, str(n), a, d, centered(200, 1340, 260, 260), "Bangers", 210, "#FFFFFF", weight=400,
            layers=heavy("#FFFFFF", 6, drop=6), anim_in=tanim("pop", duration=0.3), editable=False)
        say(t, name, a + 0.1, d - 0.1, Box(60, 1520, 960, 260), "Bangers", 120, "#FFFFFF", weight=400,
            layers=heavy("#FFFFFF", 10), anim_in=tanim("slide-up", duration=0.3), name=f"Puesto {n}")
    say(t, "Y EL NÚMERO 1 ES…", 6.1, 2.5, Box(60, 650, 960, 380), "Bangers", 150, "#FFE600", weight=400,
        layers=heavy("#FFE600", 12), anim_in=tanim("typewriter", duration=1.0, unit="character"),
        name="Antes del 1")
    say(t, "?", 6.6, 2.0, Box(60, 1050, 960, 500), "Bangers", 420, "#FFFFFF", weight=400, layers=heavy("#FFFFFF", 14),
        anim_in=tanim("pop", duration=0.3), anim_loop=tanim("pulse", amount=6, speed=2), editable=False)
    rays(t, "#FFC83D", 8.6, 3.4, centered(260, 1330, 1000, 1000), alpha=0.2)
    say(t, "#1", 8.6, 3.4, Box(40, 1150, 700, 420), "Bangers", 380, "#FFC83D", weight=400, layers=gold_text(12),
        align="left", anim_in=tanim("stamp", duration=0.35), editable=False)
    say(t, "Playa de arena blanca", 8.8, 3.2, Box(60, 1560, 960, 260), "Bangers", 120, "#FFFFFF", weight=400,
        layers=heavy("#FFFFFF", 10), anim_in=tanim("slide-up", duration=0.3), name="Puesto 1")
    confetti(t, ["#FFC83D", "#FF6B00", "#FFFFFF"], 8.6, 3.4, seed=6024, lanes=4, density=0.22)
    flash(t, 8.6, 0.4, peak=0.9)
    punch(t, [3.0, 8.6], 0.45, 0.35, shake=0.2)
    t.song("stunted-adventure", 0.0, 0.85)
    return t


def top_comida():
    t = mk(tall, 25, "yt-top-5-comida", "Top 5 comidas", "Top 5 foods", 12.0,
           TP + ["comida", "calificación", "food", "estrellas"], thumb_at=10.5, background="#FFF3E0")
    bg(t, "#FFF3E0")
    t.solid(t.track("shape", "Cabecera"), "#E63946", 0.0, 12.0, Box(0, 0, 1080, 310),
            slide_in(dy=-310, length=0.4))
    say(t, "TOP 5", 0.2, 11.8, Box(60, 40, 960, 160), "Lilita One", 140, "#FFFFFF", weight=400,
        layers=[shadow("#8A1C24", 0, 8, 0, 1.0), fill("#FFFFFF")], anim_in=tanim("pop", duration=0.35),
        name="Título")
    say(t, "COMIDAS CALLEJERAS", 0.4, 11.6, Box(60, 200, 960, 80), "Poppins", 54, "#FFE8C2", weight=800, spacing=6,
        anim_in=tanim("fade", duration=0.4), name="Tema")
    samples = ["y2-dish-05", "y2-dish-04", "food-01", "y2-dish-06", "y2-dish-01"]
    names = ["Pan con todo", "Fideos de la calle", "Plato del día", "Picoteo para compartir", "La pasta de la abuela"]
    stars = [3, 4, 4, 5, 5]
    ring_t, photo_t = t.track("shape", "Plato"), t.track("video", "Foto")
    ban_t, num_t, name_t = t.track("shape", "Cinta"), t.track("text", "Número"), t.track("text", "Nombre")
    star_ts = [t.track("shape", f"Estrella {j + 1}") for j in range(5)]
    for k in range(5):
        n = 5 - k
        a = 0.6 + k * 2.2
        d = (0.6 + (k + 1) * 2.2 if k < 4 else 12.0) - a
        spin = keys([(0, -120, "out"), (0.5, 0)])
        m = [(0, {"s": 0.3}, "out"), (0.5, {})]
        t.solid(ring_t, "#FFFFFF", a, d, centered(540, 880, 800, 800), m, kind="ellipse",
                layers=[shadow("#7A4B2A", 0, 20, 40, 0.35), fill("#FFFFFF"), no_stroke()])
        c = t.photo(photo_t, samples[k], a, d, centered(540, 880, 720, 720), m, label=f"Puesto {n}", rotation=spin)
        t.mask(photo_t, c, "ellipse")
        b = t.solid(ban_t, "#E63946", a + 0.2, d - 0.2, centered(540, 1300, 420, 150), pop(0, 0.3), kind="banner",
                    layers=[shadow("#8A1C24", 0, 8, 0, 1.0), fill("#E63946"), no_stroke()])
        t.text(num_t, f"#{n}", a + 0.2, d - 0.2, centered(540, 1300, 420, 150),
               text_style("Lilita One", 110, [fill("#FFFFFF")], weight=400, anim_in=tanim("pop", duration=0.3)),
               editable=False)
        t.text(name_t, names[k], a + 0.3, d - 0.3, Box(60, 1410, 960, 200),
               text_style("Lilita One", 84, [fill("#3A1F12")], weight=400, line=1.0,
                          anim_in=tanim("rise", duration=0.35)), label=f"Puesto {n}")
        for j in range(5):
            on = j < stars[k]
            st = t.solid(star_ts[j], "#FFB703" if on else "#E7D8C3", a + 0.5 + j * 0.08, d - 0.5 - j * 0.08,
                         centered(340 + j * 100, 1680, 86, 86), pop(0, 0.3), kind="star",
                         layers=[fill("#FFB703" if on else "#E7D8C3"), no_stroke()])
            geo(st, points=5, innerRatio=0.45)
    confetti(t, ["#E63946", "#FFB703", "#FFFFFF"], 9.4, 2.6, seed=6025, lanes=3, density=0.3)
    song(t, "jazz", 1, 0.85)
    return t


def top_lugares():
    t = mk(wide, 26, "yt-top-5-lugares", "Top 5 lugares", "Top 5 places", 13.0,
           TP + ["viajes", "lugares", "travel", "destinos"], thumb_at=10.9)
    starts = [0.5 + k * 2.4 for k in range(5)]
    cuts(t, ["y2-h-place-04", "y2-h-place-07", "y2-h-place-08", "y2-h-place-06", "y2-h-place-03"], starts, 13.0,
         transition="slide_left", tdur=0.35, kbs=0.07, labels=[f"Puesto {5 - k}" for k in range(5)])
    shade_bottom(t, 460, 0.8)
    shade_top(t, 320, 0.45)
    names = [("Templo rojo", "TAILANDIA"), ("La isla del lago", "ESLOVENIA"), ("Fuerte entre palmeras", "INDIA"),
             ("Templo sobre el agua", "TAILANDIA"), ("Palacio de mármol", "INDIA")]
    circ, nt = t.track("shape", "Círculo"), t.track("text", "Número")
    pt, ct = t.track("text", "Lugar"), t.track("text", "País")
    for k in range(5):
        n = 5 - k
        a = starts[k] + 0.2
        d = (starts[k + 1] if k < 4 else 13.0) - a
        t.solid(circ, "#FFFFFF", a, d, centered(170, 160, 200, 200), pop(0, 0.35), kind="ellipse",
                layers=[shadow("#000000", 0, 8, 20, 0.4), fill("#FFFFFF"), no_stroke()])
        t.text(nt, str(n), a, d, centered(170, 166, 200, 200),
               text_style("DM Serif Display", 140, [fill("#1B2A41")], weight=400, anim_in=tanim("pop", duration=0.3)),
               editable=False)
        t.text(pt, names[k][0], a + 0.15, d - 0.15, Box(80, 780, 1300, 150),
               text_style("DM Serif Display", 110, [shadow("#000000", 0, 4, 16, 0.6), fill("#FFFFFF")], weight=400,
                          align="left", anim_in=tanim("rise-by-word", duration=0.4, unit="word", stagger=0.08)),
               label=f"Lugar {n}")
        t.text(ct, names[k][1], a + 0.35, d - 0.35, Box(84, 930, 900, 70),
               text_style("Montserrat", 40, [fill("#FFD27A")], weight=700, spacing=10, align="left",
                          anim_in=tanim("fade", duration=0.4)), label=f"País {n}")
    t.solid(t.track("shape", "Ruta"), "#FFFFFF", 0.3, 12.7, Box(1320, 997, 520, 6), alpha=0.5)
    for j in range(5):
        x = 1320 + j * 130
        t.solid(t.track("shape", "Parada"), "#FFFFFF", 0.3, 12.7, centered(x, 1000, 26, 26), kind="ellipse", alpha=0.6)
        a = starts[j] + 0.2
        t.solid(t.track("shape", "Parada"), "#FFD27A", a, 13.0 - a, centered(x, 1000, 40, 40), pop(0, 0.35),
                kind="ellipse", layers=[glow("#FFD27A", 16, 0.7), fill("#FFD27A"), no_stroke()])
    song(t, "cine", 3, 0.85)
    return t


def top_tabla():
    t = mk(tall, 27, "yt-top-10-tabla", "Tabla de posiciones", "Leaderboard", 8.0,
           TP + ["tabla", "posiciones", "puntos", "leaderboard"], thumb_at=5.0, background="#0F2027")
    bg_gradient(t, [(0, "#2C5364"), (0.5, "#203A43"), (1, "#0F2027")], angle=90)
    say(t, "TABLA DE POSICIONES", 0.1, 7.9, Box(60, 80, 960, 120), "Barlow Condensed", 96, "#FFFFFF", weight=800,
        spacing=2, anim_in=tanim("slide-down", duration=0.4), name="Título")
    say(t, "TEMPORADA 2026", 0.3, 7.7, Box(60, 190, 960, 60), "Barlow Condensed", 44, "#7FDBFF", weight=600,
        spacing=10, anim_in=tanim("fade", duration=0.4), name="Subtítulo")
    scores = [985, 940, 902, 870, 835, 790, 744, 700, 655, 610]
    names = ["Valentina", "Diego", "Camila", "Nicolás", "Isabella", "Samuel", "Martina", "Tomás", "Lucía", "Andrés"]
    for r in range(1, 11):
        y = 290 + (r - 1) * 156
        ap = 0.4 + (10 - r) * 0.3
        d = 8.0 - ap
        m = slide_in(dx=-1100, length=0.45)
        if r == 1:
            layers = [shadow("#000000", 0, 8, 20, 0.4), gradient([(0, "#FFE38A"), (1, "#FFB800")], angle=0),
                      no_stroke()]
        else:
            layers = [fill("#FFFFFF", 0.09), stroke(2, "#FFFFFF", 0.12)]
        rrect(t, t.track("shape", "Fila"), "#FFFFFF", ap, d, Box(40, y, 1000, 140), 22, motion=m, layers=layers)
        ink = "#1A1300" if r == 1 else "#FFFFFF"
        t.text(t.track("text", "Puesto"), str(r), ap, d, Box(50, y, 120, 140),
               text_style("Barlow Condensed", 84, [fill("#1A1300" if r == 1 else "#7FDBFF")], weight=800), m,
               editable=False)
        t.text(t.track("text", "Nombre"), names[r - 1], ap, d, Box(180, y + 12, 560, 70),
               text_style("Barlow Condensed", 58, [fill(ink)], weight=700, align="left"), m, label=f"Nombre {r}")
        bar = Box(180, y + 94, 560, 16)
        rrect(t, t.track("shape", "Carril"), "#FFFFFF", ap, d, bar, 8, motion=m,
              alpha=0.18 if r > 1 else 0.35)
        frac = scores[r - 1] / 1000
        t.solid(t.track("shape", "Barra"), "#1A1300" if r == 1 else "#7FDBFF", ap + 0.4, d - 0.4,
                Box(180, y + 94, 560 * frac, 16), [(0, {"sx": 0.0, "dx": -280 * frac}, "out"), (0.9, {})],
                radius=8, kind="rounded-rectangle")
        count_up(t, t.track("text", "Puntos"), 0, scores[r - 1], str(scores[r - 1]), ap + 0.3, 1.0,
                 Box(760, y, 250, 140), big("Barlow Condensed", 80, ink, weight=800, align="right"),
                 name=f"Puntos {r}", step=3)
    crown = t.solid(t.track("shape", "Corona"), "#FFE38A", 3.4, 4.6, centered(1010, 290, 90, 80), pop(0, 0.4),
                    kind="star", rotation=keys([(0, 15)]),
                    layers=[shadow("#000000", 0, 4, 0, 0.6), fill("#FFFFFF"), no_stroke()])
    geo(crown, points=5, innerRatio=0.45)
    flash(t, 3.4, 0.3, colour="#FFE38A", peak=0.35)
    t.song("downtown-boogie", 0.0, 0.85)
    return t


def top_papel():
    t = mk(tall, 28, "yt-top-5-cuaderno", "Top 5 en cuaderno", "Notebook top 5", 12.0,
           TP + ["cuaderno", "a mano", "polaroid", "handmade"], thumb_at=11.4, background="#FBF6EA")
    bg(t, "#FBF6EA")
    rules = t.track("shape", "Renglones")
    for k in range(20):
        t.solid(t.track("shape", "Renglón") if k else rules, "#9CC3E6", 0.0, 12.0, Box(0, 300 + k * 90, 1080, 3),
                alpha=0.55)
    t.solid(t.track("shape", "Margen"), "#E63946", 0.0, 12.0, Box(150, 0, 4, 1920), alpha=0.6)
    t.solid(t.track("shape", "Resaltador"), "#FFE066", 0.4, 11.6, Box(175, 175, 520, 70),
            [(0, {"sx": 0.0, "dx": -260}, "out"), (0.5, {})], alpha=0.7, rotation=keys([(0, -2)]))
    say(t, "MI TOP 5", 0.1, 11.9, Box(180, 80, 860, 180), "Permanent Marker", 130, "#222222", weight=400,
        align="left", rotation=keys([(0, -2)]), anim_in=tanim("wipe", duration=0.5), name="Título")
    samples = ["friends-03", "pet-02", "beach-01", "cake-01", "y4c-friends-05"]
    names = ["Las noches de juegos", "Mi perro durmiendo", "Ir a la playa", "Pastel de chocolate",
             "Mis amigos de siempre"]
    nt, rt, tt = t.track("text", "Número"), t.track("shape", "Círculo"), t.track("text", "Nombre")
    for k in range(5):
        n = 5 - k
        a = 0.7 + k * 2.2
        d = 12.0 - a
        rot = [-4, 3, -2, 4, -1][k]
        dx = [-30, 30, -10, 20, 0][k]
        box = centered(600 + dx, 820, 600, 680)
        drop = [(0, {"dy": -1500}, "back"), (0.6, {})]
        framed(t, samples[k], a, d, box, drop, border=18, bottom=90, rotation=keys([(0, rot)]), label=f"Puesto {n}")
        t.solid(t.track("shape", "Cinta"), "#FFE066", a + 0.3, d - 0.3, centered(box.cx, box.y - 30, 230, 70),
                pop(0, 0.25), alpha=0.75, rotation=keys([(0, rot - 6)]))
        end = (0.7 + (k + 1) * 2.2 if k < 4 else 12.0) - a
        t.text(nt, str(n), a + 0.4, end - 0.4, centered(250, 1470, 240, 260),
               text_style("Permanent Marker", 200, [fill("#E63946")], weight=400,
                          anim_in=tanim("pop", duration=0.25)), editable=False)
        t.solid(rt, "#E63946", a + 0.4, end - 0.4, centered(250, 1470, 250, 240), [(0, {"s": 0.0}, "out"), (0.3, {})],
                kind="ellipse", rotation=keys([(0, -12)]),
                layers=[{"id": "fill", "kind": "fill", "enabled": False,
                         "paint": {"kind": "solid", "color": "#00000000"}},
                        {"id": "stroke", "kind": "stroke", "enabled": True, "width": 8, "strokeAlign": "inside",
                         "paint": {"kind": "solid", "color": "#ffe63946"}, "opacity": 1.0}])
        t.text(tt, names[k], a + 0.5, end - 0.5, Box(400, 1360, 640, 260),
               text_style("Kalam", 76, [fill("#222222")], weight=700, align="left", line=1.0,
                          anim_in=tanim("typewriter", duration=0.6, unit="character")), label=f"Puesto {n}")
    song(t, "upbeat", 5, 0.85)
    return t


def top_retro():
    t = mk(wide, 29, "yt-top-5-retro", "Top 5 retro", "Retro top 5", 12.0,
           TP + ["retro", "80s", "vhs", "nostalgia"], thumb_at=10.4, background="#2B1055")
    bg_gradient(t, [(0, "#2B1055"), (0.55, "#D53A9D"), (1, "#FF9A3C")], angle=90)
    t.solid(t.track("shape", "Sol"), "#FFD23F", 0.0, 12.0, centered(1480, 640, 560, 560), kind="ellipse",
            layers=[gradient([(0, "#FFE66D"), (1, "#FF4D8D")], angle=90), no_stroke()])
    for k in range(5):
        t.solid(t.track("shape", "Franja"), "#D53A9D", 0.0, 12.0, Box(1180, 560 + k * 44, 600, 6 + k * 4))
    t.solid(t.track("shape", "Suelo"), "#1A0633", 0.0, 12.0, Box(0, 780, 1920, 300))
    for k in range(7):
        t.solid(t.track("shape", "Rejilla"), "#FF4D8D", 0.0, 12.0, Box(0, 790 + k * k * 7 + k * 12, 1920, 3),
                alpha=0.8)
    starts = [0.5 + k * 2.2 for k in range(5)]
    rrect(t, t.track("shape", "TV"), "#1E1E24", 0.2, 11.8, Box(130, 150, 880, 680), 40, motion=pop(0, 0.4),
          layers=[shadow("#000000", 0, 16, 30, 0.5), fill("#1E1E24"), stroke(5, "#00F0FF")])
    cuts(t, ["h-concert-01", "h-city-03", "h-beach-03", "h-concert-03", "h-city-05"], starts, 12.0,
         box=Box(170, 190, 800, 560), kbs=0.0, labels=[f"Puesto {5 - k}" for k in range(5)],
         effects=[effect("stylize.vhs", noise=24, chroma=4)])
    nt, tt = t.track("text", "Número"), t.track("text", "Nombre")
    names = ["CONCIERTO", "LUCES DE NEÓN", "VERANO", "LA GRAN NOCHE", "LA CIUDAD"]
    for k in range(5):
        n = 5 - k
        a = starts[k]
        d = (starts[k + 1] if k < 4 else 12.0) - a
        t.text(nt, f"#{n}", a, d, Box(1080, 120, 760, 380),
               text_style("Bungee Shade", 300, [shadow("#1A0633", 10, 10, 0, 1.0), fill("#00F0FF")], weight=400,
                          anim_in=tanim("zoom-in", duration=0.35)), editable=False)
        t.text(tt, names[k], a + 0.2, d - 0.2, Box(1080, 860, 800, 160),
               text_style("Press Start 2P", 44, [shadow("#000000", 4, 4, 0, 1.0), fill("#FFFFFF")], weight=400,
                          line=1.4, anim_in=tanim("typewriter", duration=0.5, unit="character")),
               label=f"Puesto {n}")
    say(t, "TOP 5", 0.0, 12.0, Box(170, 870, 600, 120), "Bungee Shade", 90, "#00F0FF", weight=400, align="left",
        name="Etiqueta")
    punch(t, starts, 0.2, 0.25, rgb=12)
    t.song("blippy-trance", 0.0, 0.85)
    return t


def top_split():
    t = mk(tall, 30, "yt-top-5-pantalla-dividida", "Top 5 pantalla dividida", "Split screen top 5", 12.0,
           TP + ["top 5", "colores", "pantalla dividida", "split screen"], thumb_at=10.6)
    pal = [("#FF4D00", "#FFFFFF"), ("#00B4D8", "#FFFFFF"), ("#8AC926", "#111111"), ("#9D4EDD", "#FFFFFF"),
           ("#FFD60A", "#111111")]
    samples = ["y2-fun-01", "travel-04", "y2-fun-03", "selfie-02", "beach-01"]
    names = ["Carrera de sacos", "Escapada al campo", "Juegos en el parque", "Selfies con amigos", "Playa con amigas"]
    pt, ft = t.track("video", "Foto"), t.track("shape", "Panel")
    nt, tt = t.track("text", "Número"), t.track("text", "Nombre")
    for k in range(5):
        n = 5 - k
        a = 0.5 + k * 2.3 if k else 0.0
        end = 0.5 + (k + 1) * 2.3 if k < 4 else 12.0
        d = end - a
        top_photo = k % 2 == 0
        pbox = Box(0, 0, 1080, 960) if top_photo else Box(0, 960, 1080, 960)
        fbox = Box(0, 960, 1080, 960) if top_photo else Box(0, 0, 1080, 960)
        sgn = 1 if k % 2 == 0 else -1
        t.photo(pt, samples[k], a, d, pbox, [(0, {"dx": -1080 * sgn}, "out"), (0.4, {}, "linear"), (d, {"s": 1.04})],
                label=f"Puesto {n}")
        bg_c, ink = pal[k]
        t.solid(ft, bg_c, a, d, fbox, [(0, {"dx": 1080 * sgn}, "out"), (0.4, {})])
        t.text(nt, str(n), a + 0.1, d - 0.1, Box(20, fbox.y - 40, 560, 1040),
               text_style("Anton", 820, [fill(ink)], weight=400, anim_in=tanim("slide-up", duration=0.35)),
               editable=False)
        t.text(tt, names[k], a + 0.2, d - 0.2, Box(560, fbox.y + 120, 480, 720),
               text_style("Anton", 96, [fill(ink)], weight=400, align="left", line=1.0,
                          anim_in=tanim("rise-by-word", duration=0.35, unit="word", stagger=0.08)),
               label=f"Puesto {n}")
    say(t, "TOP 5", 0.0, 12.0, centered(540, 960, 260, 90), "Anton", 64, "#111111", weight=400,
        box_bg=("#FFFFFF", 1.0), box_pad=12, box_radius=40, name="Etiqueta")
    punch(t, [0.5 + k * 2.3 for k in range(1, 5)], 0.3, 0.25)
    t.song("funky-energy-loop", 0.0, 0.85)
    return t


def top_datos():
    t = mk(tall, 31, "yt-top-5-datos-curiosos", "5 datos curiosos", "5 fun facts", 12.0,
           TP + ["datos curiosos", "curiosidades", "fun facts", "aprende"], thumb_at=10.8)
    starts = [0.0, 2.6, 4.9, 7.2, 9.5]
    cuts(t, ["nature-03", "y2-dish-01", "night-02", "nature-05", "beach-01"], starts, 12.0, transition="zoom_in",
         tdur=0.3, kbs=0.08, labels=[f"Dato {5 - k}" for k in range(5)])
    shade_full(t, 0.35)
    say(t, "5 DATOS QUE NO SABÍAS", 0.1, 11.9, Box(60, 120, 960, 230), "Fredoka", 92, "#FFFFFF", weight=700,
        box_bg=("#3A86FF", 1.0), box_pad=24, box_radius=30, anim_in=tanim("pop", duration=0.4), name="Título")
    facts = ["Los pulpos tienen tres corazones.", "La miel bien guardada no se echa a perder.",
             "Un día en Venus dura más que su año.", "Los plátanos son bayas; las fresas, no.",
             "Las nutrias se toman de la mano para dormir."]
    bt, bn, nn, ft = (t.track("shape", "Globo"), t.track("shape", "Estrella"), t.track("text", "Número"),
                      t.track("text", "Dato"))
    for k in range(5):
        n = 5 - k
        a = starts[k] + (0.3 if k == 0 else 0.0)
        d = (starts[k + 1] if k < 4 else 12.0) - a
        bub = t.solid(bt, "#FFFFFF", a, d, Box(90, 1060, 900, 560), pop(0, 0.4), kind="speech-bubble",
                      layers=[shadow("#000000", 0, 14, 30, 0.35), fill("#FFFFFF"), no_stroke()])
        geo(bub, tailX=0.75, tailSize=0.18)
        b = t.solid(bn, "#FFBE0B", a + 0.1, d - 0.1, centered(200, 1040, 250, 250), pop(0, 0.35), kind="burst",
                    layers=[shadow("#000000", 0, 8, 0, 0.6), fill("#FFBE0B"), no_stroke()],
                    rotation=keys([(0, 0), (d, 40)]))
        geo(b, points=12, innerRatio=0.72)
        t.text(nn, str(n), a + 0.1, d - 0.1, centered(200, 1046, 250, 250),
               text_style("Fredoka", 130, [fill("#1D1D1D")], weight=700, anim_in=tanim("pop", duration=0.3)),
               editable=False)
        t.text(ft, facts[k], a + 0.1, d - 0.1, Box(150, 1130, 780, 380),
               text_style("Fredoka", 72, [fill("#1D1D1D")], weight=600, line=1.08,
                          anim_in=tanim("fade-up-char", duration=0.4, unit="word", stagger=0.05)),
               label=f"Dato {n}")
    song(t, "fun", 2, 0.85)
    return t


def top_peor_mejor():
    t = mk(wide, 32, "yt-top-5-peor-a-mejor", "Del peor al mejor", "Worst to best", 12.0,
           TP + ["calificación", "reseña", "rating", "nota"], thumb_at=10.6, background="#111111")
    bg(t, "#111111")
    starts = [0.6 + k * 2.2 for k in range(5)]
    starts[0] = 0.0
    cuts(t, ["y2-h-dish-04", "h-food-02", "y2-h-dish-01", "y2-h-dish-02", "y2-h-dish-03"], starts, 12.0,
         box=Box(0, 0, 1150, 1080), kbs=0.05, labels=[f"Puesto {5 - k}" for k in range(5)])
    t.solid(t.track("shape", "Panel"), "#111111", 0.0, 12.0, Box(1150, 0, 770, 1080))
    say(t, "DEL PEOR AL MEJOR", 0.1, 11.9, Box(1190, 60, 700, 90), "Kanit", 60, "#FFFFFF", weight=800, align="left",
        spacing=2, name="Título")
    rows = [("#FF3B30", "Hamburguesa tibia", 0.31, "3,1/10"), ("#FF9500", "Papas sin sal", 0.54, "5,4/10"),
            ("#FFCC00", "Tacos de la esquina", 0.68, "6,8/10"), ("#A3E635", "Pollo a la brasa", 0.82, "8,2/10"),
            ("#22C55E", "El plato de la casa", 0.96, "9,6/10")]
    nt, tt, st = t.track("text", "Número"), t.track("text", "Nombre"), t.track("text", "Nota")
    rrect(t, t.track("shape", "Carril"), "#FFFFFF", 0.3, 11.7, Box(1190, 770, 690, 40), 20, alpha=0.12)
    bt = t.track("shape", "Barra")
    for k, (colour, name, frac, score) in enumerate(rows):
        n = 5 - k
        a = starts[k] + (0.3 if k == 0 else 0.0)
        d = (starts[k + 1] if k < 4 else 12.0) - a
        t.text(nt, f"#{n}", a, d, Box(1190, 160, 700, 320),
               text_style("Kanit", 260, [fill(colour)], weight=900, align="left", anim_in=tanim("pop", duration=0.3)),
               editable=False)
        t.text(tt, name, a + 0.1, d - 0.1, Box(1190, 480, 700, 260),
               text_style("Kanit", 70, [fill("#FFFFFF")], weight=700, align="left", valign="top", line=1.05,
                          anim_in=tanim("slide-left", duration=0.3, distance=0.15)), label=f"Puesto {n}")
        t.solid(bt, colour, a + 0.2, d - 0.2, Box(1190, 770, 690 * frac, 40),
                [(0, {"sx": 0.0, "dx": -345 * frac}, "out"), (0.7, {})], radius=20, kind="rounded-rectangle")
        t.text(st, score, a + 0.3, d - 0.3, Box(1190, 840, 690, 160),
               text_style("Kanit", 110, [fill(colour)], weight=800, align="left", anim_in=tanim("pop", duration=0.3)),
               label=f"Nota {n}")
    confetti(t, ["#22C55E", "#FFFFFF", "#A3E635"], starts[-1], 12.0 - starts[-1], seed=6032, lanes=3, density=0.3)
    song(t, "jazz", 0, 0.85)
    return t


def top_medallas():
    t = mk(tall, 33, "yt-top-3-medallas", "Top 3 con medallas", "Top 3 medals", 10.0,
           TP + ["medallas", "top 3", "oro", "medals"], thumb_at=8.4, background="#000814")
    bg_gradient(t, [(0, "#0B1736"), (1, "#000814")], angle=90)
    dots(t, ["#FFD166", "#FFFFFF"], 26, 0.0, 10.0, seed=6033, size=(5, 12), drift=60, kinds=("star", "ellipse"),
         alpha=0.6)
    say(t, "LOS 3 MEJORES", 0.1, 9.9, Box(60, 90, 960, 130), "Cinzel", 86, "#FFD166", weight=700, spacing=6,
        anim_in=tanim("fade", duration=0.6), name="Título")
    medals = [("#CD7F32", "#8C4F1A", "#E7A766", "Bronce"), ("#C0C0C0", "#7A7A7A", "#F0F0F0", "Plata"),
              ("#FFD166", "#B8860B", "#FFF2B8", "Oro")]
    samples = ["concert-02", "sunset-02", "travel-08"]
    names = ["El concierto", "Atardecer perfecto", "El mejor viaje"]
    times = [0.5, 3.4, 6.3]
    for k, ((c1, c2, c3, metal), a) in enumerate(zip(medals, times)):
        n = 3 - k
        d = (times[k + 1] if k < 2 else 10.0) - a
        framed(t, samples[k], a, d, centered(540, 760, 760, 860), [(0, {"s": 0.85, "dy": 60}, "out"), (0.5, {})],
               border=12, colour=c1, radius=8, label=f"Puesto {n}")
        drop = [(0, {"dy": 700}, "out"), (0.6, {})]
        t.solid(t.track("shape", "Cinta"), "#C1121F", a + 0.3, d - 0.3, centered(470, 1210, 90, 220), drop,
                rotation=keys([(0, 20)]))
        t.solid(t.track("shape", "Cinta"), "#1D4ED8", a + 0.3, d - 0.3, centered(610, 1210, 90, 220), drop,
                rotation=keys([(0, -20)]))
        t.solid(t.track("shape", "Medalla"), c1, a + 0.3, d - 0.3, centered(540, 1410, 300, 300), drop, kind="ellipse",
                layers=[shadow("#000000", 0, 12, 24, 0.5), gradient([(0, c3), (0.5, c1), (1, c2)], angle=45),
                        stroke(10, c2)])
        t.text(t.track("text", "Número"), str(n), a + 0.3, d - 0.3, centered(540, 1418, 300, 300),
               text_style("Cinzel", 160, [shadow(c3, 0, -3, 0, 0.8), fill(c2)], weight=900), drop, editable=False)
        say(t, names[k], a + 0.6, d - 0.6, Box(60, 1600, 960, 150), "Cinzel", 76, "#FFFFFF", weight=700,
            anim_in=tanim("rise", duration=0.4), name=f"Puesto {n}")
    rays(t, "#FFD166", 6.3, 3.7, centered(540, 1410, 900, 900), alpha=0.18)
    t.adjust([effect("bling_sparkle", intensity=0.7, density=0.4, threshold=0.75)], 6.6, 3.4, name="Brillos")
    flash(t, 6.3, 0.3, colour="#FFF2B8", peak=0.5)
    song(t, "epic", 4, 0.85)
    return t


def top_ranking_vacio():
    t = mk(tall, 34, "yt-top-5-ranking-rellenar", "Ranking a rellenar", "Fill-in ranking", 14.0,
           TP + ["ranking", "elige", "rank it", "postres"], thumb_at=13.3, background="#111111")
    bg(t, "#111111")
    starts = [0.6 + k * 2.6 for k in range(5)]
    starts[0] = 0.0
    cuts(t, ["icecream-01", "cake-01", "cake-02", "bakery-02", "icecream-02"], starts, 14.0,
         box=Box(0, 820, 1080, 1100), punch_in=True, kbs=0.04, labels=[f"Opción {k + 1}" for k in range(5)])
    t.solid(t.track("shape", "Panel"), "#111111", 0.0, 14.0, Box(0, 0, 1080, 820))
    say(t, "RANKING DE POSTRES", 0.1, 13.9, Box(60, 40, 960, 100), "Montserrat", 64, "#FFFFFF", weight=900,
        anim_in=tanim("fade", duration=0.4), name="Título")
    medal = ["#FFD166", "#D9D9D9", "#E0A46B", "#FFFFFF", "#FFFFFF"]
    for r in range(1, 6):
        y = 170 + (r - 1) * 126
        say(t, f"{r}.", 0.2, 13.8, Box(60, y, 120, 110), "Montserrat", 80, medal[r - 1], weight=900, align="left",
            editable=False)
        t.solid(t.track("shape", "Línea"), "#FFFFFF", 0.2, 13.8, Box(190, y + 96, 830, 4), alpha=0.3)
    order = [3, 1, 5, 2, 4]
    items = ["Helado", "Tarta de queso", "Pastel de cumpleaños", "Pan dulce", "Helado de pistacho"]
    for k, r in enumerate(order):
        at = starts[k] + 1.7
        y = 170 + (r - 1) * 126
        t.solid(t.track("shape", "Resalte"), "#FFE600", at, 0.8, Box(180, y, 860, 110),
                opacity=keys([(0, 0.5, "out"), (0.8, 0.0)]))
        say(t, items[k], at, 14.0 - at, Box(200, y, 820, 110), "Montserrat", 66, "#FFFFFF", weight=800, align="left",
            layers=[shadow("#000000", 0, 4, 0, 1.0), fill("#FFFFFF")], anim_in=tanim("pop", duration=0.3),
            name=f"Puesto {r}")
    say(t, "¿EN QUÉ PUESTO?", 0.3, 13.7, Box(240, 870, 600, 90), "Montserrat", 46, "#111111", weight=900,
        box_bg=("#FFE600", 1.0), box_pad=12, box_radius=40, name="Pregunta")
    punch(t, starts, 0.2, 0.25)
    song(t, "upbeat", 7, 0.85)
    return t


def top_intro():
    t = mk(wide, 35, "yt-top-10-intro", "Intro de top 10", "Top 10 intro", 6.0,
           TP + ["intro", "apertura", "opener", "cuenta regresiva"], thumb_at=4.2)
    photo_bg(t, "y2-h-place-05", s1=1.15, label="Tu foto de fondo",
             effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=14)])
    shade_full(t, 0.55)
    nt = t.track("text", "Cuenta")
    for k in range(10):
        n = 10 - k
        a = k * 0.25
        t.text(nt, str(n), a, 0.25, centered(960, 540, 1400, 1000),
               text_style("Big Shoulders Display", 760, [fill("#FFE600" if k % 2 else "#FFFFFF")], weight=900),
               [(0, {"s": 1.8}, "out"), (0.25, {"s": 0.7})], editable=False,
               opacity=keys([(0, 0.0, "out"), (0.08, 0.9, "linear"), (0.25, 0.2)]))
    rays(t, "#FFE600", 2.6, 3.4, centered(960, 480, 1700, 1700), alpha=0.12, speed=10)
    say(t, "TOP 10", 2.6, 3.4, Box(0, 120, 1920, 560), "Big Shoulders Display", 480, "#FFFFFF", weight=900,
        layers=heavy("#FFFFFF", 14, drop=16), anim_in=tanim("stamp", duration=0.35), name="Título")
    say(t, "LOS MEJORES MOMENTOS DEL AÑO", 3.0, 3.0, Box(260, 720, 1400, 130), "Montserrat", 64, "#111111",
        weight=900, box_bg=("#FFE600", 1.0), box_pad=18, anim_in=tanim("wipe", duration=0.4), name="Subtítulo")
    t.adjust([effect("light_leak", intensity=0.5, speed=1.2)], 2.6, 3.4, name="Luz")
    flash(t, 2.6, 0.35, peak=0.85)
    punch(t, [k * 0.25 for k in range(10)] + [2.6], 0.25, 0.2)
    t.song("city-run", 10.0, 0.85)
    return t


# =====================================================================================================
# 3. FITNESS
# =====================================================================================================

def fit_reps():
    t = mk(tall, 36, "yt-fit-contador-reps", "Contador de repeticiones", "Rep counter", 10.0,
           FT + ["repeticiones", "reps", "gym", "serie"], thumb_at=8.2)
    photo_bg(t, "gym-01", s1=1.06, label="Tu video de ejercicio")
    shade_bottom(t, 1050, 0.88)
    shade_top(t, 360, 0.6)
    say(t, "EJERCICIO", 0.2, 9.8, Box(60, 80, 960, 70), "Teko", 60, "#C6FF00", weight=600, spacing=10,
        align="left", name="Antetítulo")
    say(t, "SENTADILLAS", 0.3, 9.7, Box(60, 130, 960, 170), "Teko", 170, "#FFFFFF", weight=700, align="left",
        anim_in=tanim("slide-right", duration=0.35, distance=0.2), name="Ejercicio")
    box = centered(540, 1300, 540, 540)
    track_ring(t, "#FFFFFF", box, 0.3, 9.7, width=26, alpha=0.15)
    pts = [(0, 0.0, "hold")]
    for i in range(12):
        a = 0.5 + i * 0.6
        pts += [(a, i / 12, "out"), (a + 0.15, (i + 1) / 12, "hold")]
    progress_ring(t, "#C6FF00", box, 0.3, 9.7, keys(pts), width=26)
    rt = t.track("text", "Repeticiones")
    for i in range(12):
        a = 0.8 + i * 0.6
        last = i == 11
        t.text(rt, str(i + 1), a, (10.0 - a) if last else 0.6, centered(540, 1300, 520, 340),
               text_style("Teko", 320, [shadow("#000000", 0, 8, 20, 0.5), fill("#C6FF00" if last else "#FFFFFF")],
                          weight=700, anim_in=tanim("pop", duration=0.15, **{"from": 130})),
               editable=last, label="Número final" if last else None)
    say(t, "REPS", 0.3, 9.7, Box(60, 1440, 960, 80), "Teko", 64, "#C6FF00", weight=600, spacing=14,
        editable=False)
    say(t, "¡SERIE COMPLETA!", 7.5, 2.5, Box(60, 1640, 960, 170), "Teko", 130, "#C6FF00", weight=700,
        layers=heavy("#C6FF00", 6, drop=6), anim_in=tanim("stamp", duration=0.3), name="Mensaje")
    flash(t, 7.4, 0.3, colour="#C6FF00", peak=0.4)
    punch(t, [0.8 + i * 0.6 for i in range(12)], 0.12, 0.2)
    t.song("action-strike", 12.0, 0.85)
    return t


def fit_tabata():
    t = mk(tall, 37, "yt-fit-tabata", "Temporizador tabata", "Tabata timer", 15.0,
           FT + ["tabata", "temporizador", "hiit", "timer"], thumb_at=6.3)
    photo_bg(t, "beach-01", s1=1.08, label="Tu video de ejercicio")
    t.solid(t.track("shape", "Color"), "#E63946", 0.0, 10.5, alpha=0.62)
    t.solid(t.track("shape", "Color"), "#1D4ED8", 10.5, 4.5, alpha=0.62,
            opacity=keys([(0, 0.0, "out"), (0.3, 1.0)]))
    say(t, "TRABAJO", 0.2, 10.3, Box(60, 200, 960, 200), "Oswald", 170, "#FFFFFF", weight=700, spacing=6,
        anim_in=tanim("slide-down", duration=0.35), name="Fase trabajo")
    say(t, "DESCANSO", 10.5, 4.5, Box(60, 200, 960, 200), "Oswald", 170, "#FFFFFF", weight=700, spacing=6,
        anim_in=tanim("slide-down", duration=0.35), name="Fase descanso")
    box = centered(540, 960, 760, 760)
    track_ring(t, "#FFFFFF", box, 0.3, 14.7, width=34, alpha=0.2)
    progress_ring(t, "#FFFFFF", box, 0.5, 10.0, keys([(0, 1.0, "linear"), (10.0, 0.0)]), width=34)
    progress_ring(t, "#FFFFFF", box, 10.5, 4.5, keys([(0, 1.0, "linear"), (4.5, 0.0)]), width=34)
    nt = t.track("text", "Tiempo")
    for k in range(10):
        t.text(nt, mmss(10 - k), 0.5 + k, 1.0, centered(540, 960, 760, 380),
               text_style("Oswald", 300, [shadow("#000000", 0, 8, 20, 0.4), fill("#FFFFFF")], weight=700),
               editable=False)
    for k in range(5):
        t.text(nt, mmss(5 - k), 10.5 + k * 0.9, 0.9, centered(540, 960, 760, 380),
               text_style("Oswald", 300, [shadow("#000000", 0, 8, 20, 0.4), fill("#FFFFFF")], weight=700),
               editable=False)
    say(t, "RONDA 1/8", 0.3, 14.7, Box(60, 1460, 960, 130), "Oswald", 100, "#FFFFFF", weight=700, spacing=4,
        name="Ronda")
    say(t, "SIGUIENTE: BURPEES", 10.7, 4.3, Box(60, 1620, 960, 100), "Oswald", 64, "#FFFFFF", weight=500,
        box_bg=("#000000", 0.45), box_pad=14, box_radius=14, anim_in=tanim("rise", duration=0.35),
        name="Siguiente")
    flash(t, 10.5, 0.3, peak=0.5)
    song(t, "electro", 1, 0.85)
    return t


def fit_antes_despues():
    t = mk(tall, 38, "yt-fit-antes-despues-kilos", "Antes y después con kilos", "Before and after with kilos", 10.0,
           FT + ["antes y después", "transformación", "kilos", "before after"], thumb_at=6.0)
    t.photo(t.track("video", "Antes"), "outfit-04", 0.0, 10.0, t.full, kb(10.0, 1.0, 1.05), label="Antes",
                     effects=[effect("color.basic", saturation=-0.6, contrast=-0.1, exposure=-0.1)])
    after_t = t.track("video", "Después")
    after = t.photo(after_t, "gym-01", 0.0, 10.0, t.full, kb(10.0, 1.0, 1.05), label="Después")
    t.mask(after_t, after, "rectangle", x=0.0, w=0.0,
           keyframes={"w": keys([(0, 0.0, "hold"), (2.0, 0.0, "inout"), (4.5, 1.0)]),
                      "x": keys([(0, 0.0, "hold"), (2.0, 0.0, "inout"), (4.5, 0.5)])})
    t.solid(t.track("shape", "Divisor"), "#FFFFFF", 0.0, 10.0, centered(540, 960, 10, 1920),
            [(0, {"dx": -545}, "hold"), (2.0, {"dx": -545}, "inout"), (4.5, {"dx": 545})],
            layers=[shadow("#000000", 0, 0, 20, 0.5), fill("#FFFFFF"), no_stroke()])
    shade_bottom(t, 700, 0.85)
    pill(t, t.track("shape", "Antes"), "#1F2937", 0.3, 9.7, Box(60, 110, 320, 100), pop(0, 0.35))
    say(t, "ANTES", 0.3, 9.7, Box(60, 110, 320, 100), "Montserrat", 52, "#FFFFFF", weight=900, spacing=6,
        name="Etiqueta antes")
    pill(t, t.track("shape", "Después"), "#00C2A8", 0.5, 9.5, Box(660, 110, 360, 100), pop(0, 0.35))
    say(t, "DESPUÉS", 0.5, 9.5, Box(660, 110, 360, 100), "Montserrat", 52, "#FFFFFF", weight=900, spacing=6,
        name="Etiqueta después")
    count_fn(t, t.track("text", "Kilos"), lambda f: 92 - 14 * ease_out(f, 1.8), lambda v: f"{round(v)} KG", 2.0, 2.5,
             "78 KG", Box(0, 1440, 1080, 280), big("Montserrat", 220, "#FFFFFF", weight=900,
                                                   layers=heavy("#FFFFFF", 8, drop=8)),
             name="Peso final", step=3,
             final_style=big("Montserrat", 220, "#00C2A8", weight=900, layers=heavy("#00C2A8", 8, drop=8),
                             anim_in=tanim("pop", duration=0.3)))
    say(t, "92 KG", 0.4, 1.6, Box(0, 1440, 1080, 280), "Montserrat", 220, "#FFFFFF", weight=900,
        layers=heavy("#FFFFFF", 8, drop=8), anim_in=tanim("fade", duration=0.3), name="Peso inicial")
    say(t, "12 SEMANAS", 4.6, 5.4, Box(60, 1730, 960, 110), "Montserrat", 70, "#00C2A8", weight=800, spacing=10,
        anim_in=tanim("rise", duration=0.4), name="Tiempo")
    flash(t, 4.5, 0.3, colour="#00C2A8", peak=0.4)
    song(t, "upbeat", 3, 0.85)
    return t


def fit_plan_semana():
    t = mk(wide, 39, "yt-fit-plan-semanal", "Plan de entrenamiento semanal", "Weekly workout plan", 12.0,
           FT + ["plan", "semana", "rutina", "weekly plan"], thumb_at=7.4, background="#0B1220")
    photo_bg(t, "y2-h-gym-01", s1=1.08, label="Tu foto de fondo",
             effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=6)])
    shade_full(t, 0.65, colour="#0B1220")
    say(t, "MI PLAN DE ENTRENAMIENTO", 0.1, 11.9, Box(74, 50, 1500, 100), "Sora", 72, "#FFFFFF", weight=800,
        align="left", anim_in=tanim("slide-right", duration=0.4, distance=0.15), name="Título")
    say(t, "SEMANA 1", 0.3, 11.7, Box(78, 140, 800, 60), "Sora", 40, "#7CFFCB", weight=600, spacing=8, align="left",
        name="Semana")
    days = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
    work = [("PIERNA", "50 min"), ("PECHO", "45 min"), ("CARDIO", "30 min"), ("ESPALDA", "45 min"),
            ("HOMBROS", "40 min"), ("CORE", "25 min"), ("DESCANSO", "")]
    cw, gap, x0 = 236, 20, 74
    for d in range(7):
        x = x0 + d * (cw + gap)
        a = 0.4 + d * 0.15
        m = slide_in(dy=500, length=0.5)
        rest = work[d][0] == "DESCANSO"
        rrect(t, t.track("shape", "Día"), "#FFFFFF", a, 12.0 - a, Box(x, 230, cw, 760), 26, motion=m,
              layers=[fill("#FFFFFF", 0.05 if rest else 0.1), stroke(2, "#FFFFFF", 0.25)])
        t.text(t.track("text", "Día"), days[d], a, 12.0 - a, Box(x, 260, cw, 80),
               text_style("Sora", 52, [fill("#7CFFCB")], weight=800), m, editable=False)
        t.text(t.track("text", "Entreno"), work[d][0], a, 12.0 - a, Box(x + 10, 520, cw - 20, 120),
               text_style("Sora", 30 if rest else 38, [fill("#9AA3B2" if rest else "#FFFFFF")], weight=700), m,
               label=f"Entreno {days[d].lower()}")
        if work[d][1]:
            t.text(t.track("text", "Duración"), work[d][1], a, 12.0 - a, Box(x, 640, cw, 70),
                   text_style("Sora", 36, [fill("#9AA3B2")], weight=500), m, label=f"Duración {days[d].lower()}")
        at = 3.0 + (d + 1) * 1.1
        if at < 11.8:
            t.text(t.track("text", "Hecho"), "✓", at, 12.0 - at, Box(x, 840, cw, 120),
                   text_style("Sora", 90, [fill("#7CFFCB")], weight=800, anim_in=tanim("pop", duration=0.3)),
                   editable=False)
    hl = [(0, {"dx": 0}, "hold")]
    for d in range(1, 7):
        at = 3.0 + d * 1.1 - 2.6
        hl += [(at - 0.35, {"dx": (d - 1) * (cw + gap)}, "inout"), (at, {"dx": d * (cw + gap)})]
    t.solid(t.track("shape", "Hoy"), "#7CFFCB", 2.6, 9.4, Box(x0 - 6, 224, cw + 12, 772), hl,
            radius=30, kind="rounded-rectangle",
            layers=[halo("#7CFFCB"), {"id": "fill", "kind": "fill", "enabled": False,
                                                "paint": {"kind": "solid", "color": "#00000000"}},
                    {"id": "stroke", "kind": "stroke", "enabled": True, "width": 6, "strokeAlign": "inside",
                     "paint": {"kind": "solid", "color": "#ff7cffcb"}, "opacity": 1.0}],
            opacity=keys([(0, 0.0, "out"), (0.4, 1.0)]))
    song(t, "upbeat", 2, 0.85)
    return t


def fit_rutina_pasos():
    t = mk(tall, 40, "yt-fit-rutina-4-pasos", "Rutina en 4 pasos", "4-step workout", 13.0,
           FT + ["rutina", "pasos", "en casa", "ejercicios"], thumb_at=11.5)
    starts = [0.0, 3.2, 6.4, 9.6]
    cuts(t, ["beach-01", "h-beach-01", "outfit-04", "y5-outfit-01"], starts, 13.0, transition="push_left",
         tdur=0.3, kbs=0.06, labels=[f"Ejercicio {k + 1}" for k in range(4)])
    shade_bottom(t, 760, 0.7)
    shade_top(t, 300, 0.5)
    for k in range(4):
        x = 660 + k * 95
        t.solid(t.track("shape", "Paso"), "#FFFFFF", 0.2, 12.8, Box(x, 140, 80, 14), radius=7,
                kind="rounded-rectangle", alpha=0.35)
        a = starts[k] + 0.2
        t.solid(t.track("shape", "Paso hecho"), "#FF7A00", a, 13.0 - a, Box(x, 140, 80, 14),
                [(0, {"sx": 0.0, "dx": -40}, "out"), (0.4, {})], radius=7, kind="rounded-rectangle")
    rrect(t, t.track("shape", "Tarjeta"), "#111111", 0.3, 12.7, Box(40, 1470, 1000, 400), 40,
          motion=slide_in(dy=700, length=0.5), layers=[fill("#111111", 0.88), no_stroke()])
    names = ["FLEXIONES", "FONDOS EN BANCO", "SENTADILLA", "PLANCHA"]
    reps = ["3 × 12", "3 × 15", "3 × 20", "3 × 30 s"]
    step_t, name_t, pill_t, reps_t = (t.track("text", "Paso"), t.track("text", "Nombre"), t.track("shape", "Reps"),
                                      t.track("text", "Reps"))
    for k in range(4):
        a = starts[k] + (0.4 if k == 0 else 0.15)
        d = (starts[k + 1] if k < 3 else 13.0) - a
        t.text(step_t, f"PASO {k + 1}/4", a, d, Box(60, 110, 330, 80),
               text_style("Kanit", 48, [fill("#FFFFFF")], weight=700, box=("#FF7A00", 1.0), box_pad=14,
                          box_radius=40, anim_in=tanim("pop", duration=0.3)), editable=False)
        t.text(name_t, names[k], a + 0.1, d - 0.1, Box(80, 1500, 920, 150),
               text_style("Kanit", 100, [fill("#FFFFFF")], weight=900, align="left",
                          anim_in=tanim("slide-right", duration=0.3, distance=0.15)), label=f"Ejercicio {k + 1}")
        pill(t, pill_t, "#FF7A00", a + 0.2, d - 0.2, Box(80, 1670, 320, 110), pop(0, 0.3))
        t.text(reps_t, reps[k], a + 0.2, d - 0.2, Box(80, 1670, 320, 110),
               text_style("Kanit", 64, [fill("#FFFFFF")], weight=800, anim_in=tanim("pop", duration=0.3)),
               label=f"Series {k + 1}")
    say(t, "descanso 45 s", 0.6, 12.4, Box(430, 1690, 580, 80), "Kanit", 50, "#B8B8B8", weight=500, align="left",
        name="Descanso")
    punch(t, starts[1:], 0.2, 0.25)
    song(t, "calm", 4, 0.85)
    return t


def fit_serie_hud():
    t = mk(wide, 41, "yt-fit-serie-hud", "Serie con temporizador", "Set with timer", 12.0,
           FT + ["serie", "temporizador", "gym", "press de banca"], thumb_at=9.2)
    photo_bg(t, "y2-h-gym-01", s1=1.06, label="Tu video de ejercicio")
    shade_bottom(t, 400, 0.8)
    shade_top(t, 360, 0.55)
    rrect(t, t.track("shape", "Serie"), "#000000", 0.2, 11.8, Box(60, 60, 420, 260), 24,
          motion=slide_in(dx=-500, length=0.4), layers=[fill("#000000", 0.65), no_stroke()])
    say(t, "SERIE", 0.4, 11.6, Box(90, 75, 360, 70), "Barlow Condensed", 54, "#FFB800", weight=700, spacing=10,
        align="left", name="Etiqueta serie")
    say(t, "2/4", 0.4, 11.6, Box(90, 120, 360, 190), "Barlow Condensed", 170, "#FFFFFF", weight=800, align="left",
        anim_in=tanim("pop", duration=0.3), name="Serie")
    rrect(t, t.track("shape", "Tiempo"), "#000000", 0.2, 11.8, Box(1440, 60, 420, 260), 24,
          motion=slide_in(dx=500, length=0.4), layers=[fill("#000000", 0.65), no_stroke()])
    say(t, "TIEMPO", 0.4, 11.6, Box(1470, 75, 360, 70), "Barlow Condensed", 54, "#FFB800", weight=700, spacing=10,
        align="right", name="Etiqueta tiempo")
    nt = t.track("text", "Reloj")
    for k in range(11):
        v = 10 - k
        a = 0.5 + k
        d = 1.0 if v else 12.0 - a
        t.text(nt, mmss(v), a, d, Box(1470, 120, 360, 190),
               text_style("Barlow Condensed", 170, [fill("#FF3B30" if v <= 3 else "#FFFFFF")], weight=800,
                          align="right"), editable=False)
    say(t, "PRESS DE BANCA", 0.5, 11.5, Box(60, 800, 1300, 140), "Barlow Condensed", 120, "#FFFFFF", weight=800,
        align="left", anim_in=tanim("slide-right", duration=0.4, distance=0.15), name="Ejercicio")
    pill(t, t.track("shape", "Peso"), "#FFB800", 0.7, 11.3, Box(60, 950, 380, 80), pop(0, 0.3))
    say(t, "60 KG × 10", 0.7, 11.3, Box(60, 950, 380, 80), "Barlow Condensed", 54, "#111111", weight=800,
        name="Peso y reps")
    for i in range(10):
        x = 1460 + i * 41
        t.solid(t.track("shape", "Rep"), "#FFFFFF", 0.4, 11.6, Box(x, 980, 34, 50), radius=6,
                kind="rounded-rectangle", alpha=0.25)
        a = 1.0 + i
        t.solid(t.track("shape", "Rep hecha"), "#FFB800", a, 12.0 - a, Box(x, 980, 34, 50), pop(0, 0.25), radius=6,
                kind="rounded-rectangle")
    say(t, "REPS", 0.4, 11.6, Box(1460, 920, 400, 50), "Barlow Condensed", 40, "#FFB800", weight=700, spacing=8,
        align="left", editable=False)
    t.solid(t.track("shape", "Banda"), "#000000", 10.5, 1.5, Box(0, 400, 1920, 260), slide_in(dx=-1920, length=0.3),
            alpha=0.75)
    say(t, "¡DESCANSA!", 10.6, 1.4, Box(0, 400, 1920, 260), "Barlow Condensed", 220, "#FFB800", weight=800,
        anim_in=tanim("stamp", duration=0.3), name="Mensaje")
    flash(t, 10.5, 0.3, colour="#FFB800", peak=0.4)
    t.song("go-on-without-me", 10.0, 0.85)
    return t


def fit_hiit_neon():
    t = mk(tall, 42, "yt-fit-hiit-neon", "HIIT neón", "Neon HIIT", 12.0,
           FT + ["hiit", "cardio", "neón", "intervalos"], thumb_at=6.6, background="#050014")
    bg(t, "#050014")
    say(t, "HIIT", 0.0, 12.0, Box(60, 80, 960, 240), "Audiowide", 210, "#00F0FF", weight=400,
        layers=[glow("#00F0FF", 40, 0.9), fill("#00F0FF")], anim_in=tanim("flicker-in", duration=0.6),
        anim_loop=tanim("flicker", intensity=0.12, speed=2), name="Título")
    starts = [0.0, 4.0, 8.0]
    tints = [("#12002B", "#FF2BD6"), ("#001A2B", "#00F0FF"), ("#12002B", "#FFE600")]
    cuts(t, ["beach-01", "h-beach-01", "outfit-04"], starts, 12.0, box=Box(100, 520, 880, 980), kbs=0.06,
         labels=["Ejercicio 1", "Ejercicio 2", "Ejercicio 3"],
         effects=lambda i: [effect("duotone", strength=0.85, shadowColor=tints[i][0], highlightColor=tints[i][1])])
    names = ["SPRINT", "FLEXIONES", "SENTADILLAS"]
    nt, ft = t.track("text", "Ejercicio"), t.track("shape", "Marco")
    bar_t = t.track("shape", "Tiempo")
    for k in range(3):
        a = starts[k]
        colour = tints[k][1]
        t.solid(ft, colour, a, 4.0, Box(100, 520, 880, 980), radius=30, kind="rounded-rectangle",
                layers=[halo(colour), {"id": "fill", "kind": "fill", "enabled": False,
                                                 "paint": {"kind": "solid", "color": "#00000000"}},
                        {"id": "stroke", "kind": "stroke", "enabled": True, "width": 8, "strokeAlign": "inside",
                         "paint": {"kind": "solid", "color": argb(colour)}, "opacity": 1.0}])
        t.text(nt, names[k], a + 0.1, 3.9, Box(60, 330, 960, 150),
               text_style("Audiowide", 90, [glow(colour, 24, 0.8), fill("#FFFFFF")], weight=400,
                          anim_in=tanim("glitch-in", duration=0.4)), label=f"Ejercicio {k + 1}")
        t.solid(bar_t, colour, a, 4.0, Box(100, 1560, 880, 26),
                [(0, {}, "linear"), (4.0, {"sx": 0.0, "dx": 440})], radius=13, kind="rounded-rectangle",
                layers=[glow(colour, 16, 0.8), fill(colour), no_stroke()])
    say(t, "40 s TRABAJO · 20 s DESCANSO", 0.3, 11.7, Box(60, 1620, 960, 80), "Orbitron", 40, "#FFFFFF",
        weight=700, name="Intervalos")
    say(t, "RONDA 1 DE 4", 0.3, 11.7, Box(60, 1720, 960, 90), "Orbitron", 56, "#FF2BD6", weight=800,
        layers=[glow("#FF2BD6", 20, 0.7), fill("#FF2BD6")], name="Ronda")
    punch(t, [4.0, 8.0], 0.3, 0.3, rgb=14)
    t.song("beat-one", 8.0, 0.85)
    return t


def fit_30_dias():
    t = mk(tall, 43, "yt-fit-reto-30-dias", "Reto de 30 días", "30-day challenge", 10.0,
           FT + ["30 días", "reto", "calendario", "challenge"], thumb_at=8.0, background="#101010")
    bg(t, "#101010")
    say(t, "RETO 30 DÍAS", 0.1, 9.9, Box(60, 70, 960, 180), "Anton", 150, "#FFFFFF", weight=400,
        anim_in=tanim("slide-down", duration=0.4), name="Título")
    say(t, "SENTADILLAS DIARIAS", 0.3, 9.7, Box(60, 245, 960, 70), "Montserrat", 50, "#C6FF00", weight=800,
        spacing=6, name="Subtítulo")
    disc(t, "gym-01", 0.3, 9.7, centered(540, 470, 260, 260), pop(0, 0.4), label="Tu foto", ring_c="#C6FF00",
         ring_w=8)
    td = lambda d: 1.0 + (d - 1) * 0.2  # noqa: E731
    style = lambda: text_style("Anton", 84, [fill("#FFFFFF", 0.22)], weight=400, accent=accent("#C6FF00"))  # noqa
    for r in range(6):
        tr = t.track("text", f"Semana {r + 1}")
        days = list(range(5 * r + 1, 5 * r + 6))
        changes = [0.3] + [td(d) for d in days]
        for c in range(6):
            a = changes[c]
            end = changes[c + 1] if c < 5 else 10.0
            text = "   ".join((f"*{d:02d}*" if j < c else f"{d:02d}") for j, d in enumerate(days))
            t.text(tr, text, a, end - a, Box(90, 650 + r * 125, 900, 120), style(), editable=False)
    ct = t.track("text", "Contador")
    t.text(ct, "0/30", 0.3, td(1) - 0.3, Box(0, 1400, 1080, 300),
           text_style("Anton", 260, [fill("#C6FF00")], weight=400), editable=False)
    for d in range(1, 31):
        a = td(d)
        end = td(d + 1) if d < 30 else 10.0
        last = d == 30
        t.text(ct, f"{d}/30", a, end - a, Box(0, 1400, 1080, 300),
               text_style("Anton", 260, [glow("#C6FF00", 30, 0.6) if last else fill("#C6FF00", 0.0),
                                         fill("#C6FF00")], weight=400,
                          anim_in=tanim("stamp", duration=0.3) if last else None),
               editable=last, label="Número final" if last else None)
    say(t, "¡RETO CUMPLIDO!", 7.0, 3.0, Box(60, 1740, 960, 130), "Anton", 100, "#101010", weight=400,
        box_bg=("#C6FF00", 1.0), box_pad=16, anim_in=tanim("pop", duration=0.3), name="Mensaje")
    flash(t, 6.8, 0.3, colour="#C6FF00", peak=0.4)
    confetti(t, ["#C6FF00", "#FFFFFF"], 6.8, 3.2, seed=6043, lanes=3, density=0.25)
    song(t, "electro", 0, 0.85)
    return t


def fit_transformacion():
    t = mk(wide, 44, "yt-fit-transformacion", "Mi transformación", "My transformation", 10.0,
           FT + ["transformación", "antes y después", "kilos", "transformation"], thumb_at=6.0, background="#000000")
    bg(t, "#000000")
    t.photo(t.track("video", "Antes"), "y2-h-gym-01", 0.0, 10.0, Box(0, 0, 950, 1080), slide_in(dx=-950, length=0.5),
            label="Antes", effects=[effect("color.basic", saturation=-1.0, contrast=0.15)])
    t.photo(t.track("video", "Después"), "y2-h-gym-01", 0.2, 9.8, Box(970, 0, 950, 1080),
            slide_in(dx=950, length=0.5), label="Después", effects=[effect("color.basic", saturation=0.15,
                                                                           contrast=0.15)])
    t.solid(t.track("shape", "Rayo"), "#FF2D2D", 1.0, 9.0, centered(960, 300, 200, 420), pop(0, 0.35, s0=2.0),
                   kind="lightning-bolt", layers=[glow("#FF2D2D", 30, 0.7), stroke(6, "#FFFFFF"), fill("#FF2D2D")])
    say(t, "SEMANA 1", 0.6, 9.4, Box(60, 60, 500, 120), "Anton", 90, "#FFFFFF", weight=400, align="left",
        box_bg=("#000000", 0.85), box_pad=18, anim_in=tanim("slide-right", duration=0.3, distance=0.2),
        name="Antes")
    say(t, "SEMANA 12", 0.8, 9.2, Box(1360, 60, 500, 120), "Anton", 90, "#FFFFFF", weight=400, align="right",
        box_bg=("#FF2D2D", 1.0), box_pad=18, anim_in=tanim("slide-left", duration=0.3, distance=0.2),
        name="Después")
    rrect(t, t.track("shape", "Panel"), "#000000", 1.8, 8.2, Box(580, 680, 760, 340), 30, motion=pop(0, 0.35),
          layers=[fill("#000000", 0.85), stroke(4, "#FF2D2D")])
    say(t, "MI TRANSFORMACIÓN", 1.9, 8.1, Box(580, 700, 760, 90), "Anton", 64, "#FFFFFF", weight=400, spacing=4,
        name="Título")
    count_fn(t, t.track("text", "Kilos"), lambda f: -14 * ease_out(f, 2.0), lambda v: f"{round(v)} KG", 2.2, 2.4,
             "-14 KG", Box(580, 780, 760, 230), big("Anton", 190, "#FFFFFF", weight=400),
             name="Número final", step=3,
             final_style=big("Anton", 190, "#FF2D2D", weight=400, layers=[glow("#FF2D2D", 24, 0.6), fill("#FF2D2D")],
                             anim_in=tanim("stamp", duration=0.3)))
    flash(t, 4.6, 0.3, colour="#FF2D2D", peak=0.4)
    punch(t, [1.0, 4.6], 0.35, 0.3, shake=0.2)
    song(t, "calm", 3, 0.85)
    return t


def fit_calorias():
    t = mk(tall, 45, "yt-fit-calorias", "Calorías quemadas", "Calories burned", 9.0,
           FT + ["calorías", "cardio", "estadísticas", "calories"], thumb_at=6.0)
    photo_bg(t, "beach-01", s1=1.08, label="Tu foto o video")
    shade_full(t, 0.55, colour="#1A0800")
    box = centered(540, 820, 660, 660)
    track_ring(t, "#FFFFFF", box, 0.3, 8.7, width=36, alpha=0.15)
    progress_ring(t, "#FF6B00", box, 0.3, 8.7,
                  keys([(0, 0.0, "hold"), (0.3, 0.0, "out"), (4.3, 0.87)]), width=36)
    count_up(t, t.track("text", "Calorías"), 0, 520, "520", 0.6, 4.0, centered(540, 790, 600, 280),
             big("Sora", 230, "#FFFFFF", weight=800), name="Número final", power=3.0,
             final_style=big("Sora", 230, "#FFFFFF", weight=800, layers=[glow("#FF6B00", 30, 0.6), fill("#FFFFFF")],
                             anim_in=tanim("pop", duration=0.3)))
    say(t, "KCAL QUEMADAS", 0.6, 8.4, centered(540, 960, 600, 80), "Sora", 50, "#FF9A3C", weight=700, spacing=8,
        name="Unidad")
    stats = [("TIEMPO", "32:10"), ("PULSO", "148"), ("RITMO", "5:40")]
    for k, (lab, val) in enumerate(stats):
        cx = 190 + k * 350
        a = 1.2 + k * 0.2
        say(t, lab, a, 9.0 - a, centered(cx, 1290, 320, 60), "Sora", 38, "#C9C9C9", weight=600, spacing=6,
            anim_in=tanim("fade", duration=0.4), name=f"Etiqueta {k + 1}")
        say(t, val, a, 9.0 - a, centered(cx, 1380, 320, 120), "Sora", 92, "#FFFFFF", weight=800,
            anim_in=tanim("rise", duration=0.4), name=f"Dato {k + 1}")
    beat = [(0, {}, "hold")]
    at = 1.4
    while at < 8.8:
        beat += [(at, {}, "out"), (at + 0.12, {"s": 1.25}, "in"), (at + 0.3, {})]
        at += 0.4
    t.solid(t.track("shape", "Corazón"), "#FF3B5C", 1.2, 7.8, centered(540, 1470, 60, 54),
            [(p[0] - 1.2 if p[0] else 0,) + p[1:] for p in beat], kind="heart",
            layers=[fill("#FF3B5C"), no_stroke()])
    say(t, "ENTRENAMIENTO DE HOY", 0.4, 8.6, Box(60, 1640, 960, 100), "Sora", 66, "#FFFFFF", weight=800,
        anim_in=tanim("rise", duration=0.4), name="Título")
    say(t, "Martes · 7:00", 0.6, 8.4, Box(60, 1740, 960, 70), "Sora", 44, "#FF9A3C", weight=600, name="Fecha")
    song(t, "upbeat", 4, 0.85)
    return t


def _segment(t, p, q, at, length, colour, width=12):
    (x1, y1), (x2, y2) = p, q
    L = math.hypot(x2 - x1, y2 - y1)
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    m = [(0, {"sx": 0.001, "dx": -ux * L / 2, "dy": -uy * L / 2}, "linear"), (length, {})]
    t.solid(t.track("shape", "Ruta"), colour, at, t.duration - at, centered(cx, cy, L + width, width), m,
            radius=width / 2, kind="rounded-rectangle", rotation=keys([(0, ang)]))


def fit_correr_km():
    t = mk(tall, 46, "yt-fit-carrera-km", "Mi carrera en km", "My run in km", 10.0,
           FT + ["correr", "running", "kilómetros", "carrera"], thumb_at=8.0)
    photo_bg(t, "beach-01", s1=1.06, label="Tu foto o video")
    shade_bottom(t, 1100, 0.9)
    rrect(t, t.track("shape", "Mapa"), "#0E1A2B", 0.2, 9.8, Box(60, 110, 960, 560), 36,
          motion=slide_in(dy=-700, length=0.5), layers=[fill("#0E1A2B", 0.85), stroke(2, "#FFFFFF", 0.15)])
    for k in range(1, 6):
        t.solid(t.track("shape", "Cuadrícula"), "#FFFFFF", 0.7, 9.3, Box(60 + k * 160, 130, 2, 520), alpha=0.07)
    for k in range(1, 4):
        t.solid(t.track("shape", "Cuadrícula"), "#FFFFFF", 0.7, 9.3, Box(80, 110 + k * 140, 920, 2), alpha=0.07)
    pts = [(150, 590), (300, 520), (380, 380), (560, 330), (700, 430), (860, 260), (940, 200)]
    seg_t = 0.8
    for i in range(len(pts) - 1):
        _segment(t, pts[i], pts[i + 1], seg_t + i * 0.9, 0.9, "#FF7A00", 14)
    t.solid(t.track("shape", "Salida"), "#22C55E", 0.7, 9.3, centered(150, 590, 40, 40), pop(0, 0.3), kind="ellipse",
            layers=[stroke(6, "#FFFFFF"), fill("#22C55E")])
    t.solid(t.track("shape", "Meta"), "#FF3B30", 6.2, 3.8, centered(940, 200, 46, 46), pop(0, 0.3), kind="ellipse",
            layers=[glow("#FF3B30", 20, 0.8), stroke(6, "#FFFFFF"), fill("#FF3B30")])
    count_up(t, t.track("text", "Distancia"), 0, 10, "10,00", 0.8, 5.4, Box(60, 1080, 960, 320),
             big("Barlow Condensed", 300, "#FFFFFF", weight=800, align="left"), decimals=2, power=1.6,
             name="Número final",
             final_style=big("Barlow Condensed", 300, "#FFFFFF", weight=800, align="left",
                             layers=[glow("#FF7A00", 24, 0.6), fill("#FFFFFF")], anim_in=tanim("pop", duration=0.3)))
    say(t, "KILÓMETROS", 0.8, 9.2, Box(66, 1380, 960, 90), "Barlow Condensed", 80, "#FF7A00", weight=700, spacing=10,
        align="left", name="Unidad")
    for k, (lab, val) in enumerate([("RITMO", "5:12 /km"), ("TIEMPO", "52:03")]):
        x = 66 + k * 480
        say(t, lab, 1.2, 8.8, Box(x, 1500, 440, 60), "Barlow Condensed", 44, "#BDBDBD", weight=600, spacing=8,
            align="left", name=f"Etiqueta {k + 1}")
        say(t, val, 1.2, 8.8, Box(x, 1550, 440, 110), "Barlow Condensed", 96, "#FFFFFF", weight=800, align="left",
            name=f"Dato {k + 1}")
    say(t, "¡NUEVA MARCA!", 6.4, 3.6, Box(60, 1730, 600, 110), "Barlow Condensed", 80, "#111111", weight=800,
        box_bg=("#FF7A00", 1.0), box_pad=16, box_radius=16, anim_in=tanim("pop", duration=0.3), name="Mensaje")
    song(t, "fun", 3, 0.85)
    return t


def fit_ejercicio_dia():
    t = mk(wide, 47, "yt-fit-ejercicio-del-dia", "Ejercicio del día", "Exercise of the day", 10.0,
           FT + ["ejercicio del día", "consejos", "técnica", "tips"], thumb_at=6.0, background="#E8FFF4")
    bg_gradient(t, [(0, "#E8FFF4"), (1, "#FFFFFF")], angle=0)
    rrect(t, t.track("shape", "Marco"), "#FFFFFF", 0.2, 9.8, Box(70, 140, 840, 820), 36, motion=pop(0, 0.45, s0=0.8),
          layers=[shadow("#0B2545", 0, 20, 40, 0.25), fill("#FFFFFF"), no_stroke()])
    t.photo(t.track("video", "Foto"), "y2-h-gym-01", 0.2, 9.8, Box(90, 160, 800, 780), pop(0, 0.45, s0=0.8),
            label="Tu foto del ejercicio")
    pill(t, t.track("shape", "Cinta"), "#0B2545", 0.1, 9.9, Box(70, 50, 540, 74), slide_in(dx=-700, length=0.4))
    say(t, "EJERCICIO DEL DÍA", 0.2, 9.8, Box(70, 50, 540, 74), "Outfit", 44, "#FFFFFF", weight=800, spacing=4,
        name="Etiqueta")
    say(t, "CURL DE BÍCEPS", 0.5, 9.5, Box(980, 140, 900, 190), "Outfit", 96, "#0B2545", weight=900, align="left",
        anim_in=tanim("slide-left", duration=0.4, distance=0.15), name="Ejercicio")
    pill(t, t.track("shape", "Series"), "#14B8A6", 0.8, 9.2, Box(980, 340, 340, 90), pop(0, 0.3))
    say(t, "3 × 12", 0.8, 9.2, Box(980, 340, 340, 90), "Outfit", 56, "#FFFFFF", weight=800, name="Series")
    tips = ["Codos pegados al cuerpo", "Sube en 1 segundo, baja en 3",
            "La espalda quieta, sin balancearte"]
    for k, tip in enumerate(tips):
        y = 480 + k * 130
        a = 1.5 + k * 0.8
        t.solid(t.track("shape", "Viñeta"), "#14B8A6", a, 10.0 - a, centered(1015, y + 50, 70, 70), pop(0, 0.3),
                kind="ellipse")
        say(t, str(k + 1), a, 10.0 - a, centered(1015, y + 52, 70, 70), "Outfit", 44, "#FFFFFF", weight=800,
            editable=False)
        say(t, tip, a + 0.1, 9.9 - a, Box(1080, y, 790, 100), "Outfit", 44, "#0B2545", weight=600, align="left",
            line=1.05, anim_in=tanim("slide-left", duration=0.35, distance=0.1), name=f"Consejo {k + 1}")
    say(t, "NIVEL", 4.0, 6.0, Box(980, 890, 200, 60), "Outfit", 40, "#0B2545", weight=800, spacing=6, align="left",
        name="Etiqueta nivel")
    for k in range(3):
        on = k < 2
        t.solid(t.track("shape", "Nivel"), "#14B8A6" if on else "#B6D9D2", 4.1 + k * 0.15, 5.9 - k * 0.15,
                Box(1140 + k * 70, 950 - (k + 1) * 22, 50, (k + 1) * 22 + 10), pop(0, 0.25), radius=6,
                kind="rounded-rectangle")
    song(t, "calm", 1, 0.85)
    return t


def fit_record():
    t = mk(tall, 48, "yt-fit-record-personal", "Nuevo récord personal", "New personal record", 8.0,
           FT + ["récord", "pr", "pesas", "personal record"], thumb_at=5.5, background="#000000")
    photo_bg(t, "gym-01", s1=1.08, label="Tu foto o video",
             effects=[effect("color.basic", saturation=-0.45, contrast=0.2)])
    shade_full(t, 0.55)
    say(t, "NUEVO RÉCORD", 0.2, 7.8, Box(30, 160, 1020, 150), "Black Ops One", 96, "#FFFFFF", weight=400,
        layers=heavy("#FFFFFF", 6, drop=8), anim_in=tanim("slide-down", duration=0.4), name="Título")
    say(t, "PERSONAL", 0.4, 7.6, Box(60, 310, 960, 130), "Black Ops One", 90, "#FFC83D", weight=400,
        anim_in=tanim("slide-up", duration=0.4), name="Subtítulo")
    t.solid(t.track("shape", "Barra"), "#B0B0B0", 0.3, 7.7, Box(60, 950, 960, 26), radius=13, kind="rounded-rectangle",
            motion=[(0, {"sx": 0.0}, "out"), (0.5, {})],
            layers=[gradient([(0, "#E0E0E0"), (1, "#7A7A7A")], angle=90), no_stroke()])
    plates = [(110, 60, 280, 0.6), (180, 46, 220, 1.0), (240, 36, 170, 1.4)]
    for x, w, h, at in plates:
        for side in (1, -1):
            px = x if side == 1 else 1080 - x - w
            t.solid(t.track("shape", "Disco"), "#1A1A1A", at, 8.0 - at, Box(px, 963 - h / 2, w, h),
                    [(0, {"dx": -500 * side}, "back"), (0.4, {})], radius=10, kind="rounded-rectangle",
                    layers=[shadow("#000000", 0, 6, 10, 0.5), fill("#1A1A1A"), stroke(4, "#FFC83D")])
    count_up(t, t.track("text", "Peso"), 60, 120, "120", 0.8, 3.0, Box(60, 1080, 700, 340),
             big("Black Ops One", 300, "#FFC83D", weight=400, align="right"), power=2.4, name="Número final",
             final_style=big("Black Ops One", 300, "#FFC83D", weight=400, align="right", layers=gold_text(10),
                             anim_in=tanim("stamp", duration=0.3)))
    say(t, "KG", 0.8, 7.2, Box(780, 1210, 260, 180), "Black Ops One", 150, "#FFFFFF", weight=400, align="left",
        name="Unidad")
    b = t.solid(t.track("shape", "Sello"), "#FF2D2D", 3.9, 4.1, centered(860, 720, 280, 280), pop(0, 0.35, s0=2.0),
                kind="burst", rotation=keys([(0, 12)]), layers=[shadow("#000000", 0, 10, 0, 0.9), fill("#FF2D2D"),
                                                                no_stroke()])
    geo(b, points=14, innerRatio=0.75)
    say(t, "PR", 3.9, 4.1, centered(860, 726, 280, 200), "Black Ops One", 120, "#FFFFFF", weight=400,
        rotation=keys([(0, 12)]), anim_in=tanim("pop", duration=0.3), editable=False)
    say(t, "+10 KG respecto al anterior", 4.2, 3.8, Box(60, 1460, 960, 100), "Montserrat", 54, "#FFFFFF", weight=800,
        anim_in=tanim("rise", duration=0.4), name="Mensaje")
    flash(t, 3.8, 0.3, colour="#FFC83D", peak=0.5)
    punch(t, [0.6, 1.0, 1.4, 3.8], 0.25, 0.25, shake=0.25)
    song(t, "epic", 1, 0.85)
    return t


def fit_calentamiento():
    t = mk(tall, 49, "yt-fit-calentamiento", "Calentamiento en 5 pasos", "5-step warm-up", 12.0,
           FT + ["calentamiento", "movilidad", "warm up", "pasos"], thumb_at=7.6, background="#F4F1EA")
    bg(t, "#F4F1EA")
    say(t, "CALENTAMIENTO", 0.1, 11.9, Box(60, 70, 960, 130), "Nunito", 104, "#1F4E3D", weight=900,
        anim_in=tanim("rise", duration=0.4), name="Título")
    say(t, "5 minutos antes de entrenar", 0.3, 11.7, Box(60, 195, 960, 70), "Nunito", 50, "#E76F51", weight=700,
        name="Subtítulo")
    starts = [0.6 + k * 2.2 for k in range(5)]
    starts[0] = 0.0
    rrect(t, t.track("shape", "Marco"), "#FFFFFF", 0.0, 12.0, Box(130, 290, 820, 660), 40,
          layers=[shadow("#1F4E3D", 0, 14, 30, 0.2), fill("#FFFFFF"), no_stroke()])
    cuts(t, ["outfit-04", "beach-01", "h-beach-01", "y5-outfit-01", "y5-outfit-02"], starts, 12.0,
         box=Box(150, 310, 780, 620), transition="crossfade", tdur=0.3, kbs=0.05,
         labels=[f"Paso {k + 1}" for k in range(5)])
    steps = [("Movilidad de cuello", "0:30"), ("Trote suave", "1:00"), ("Círculos de brazos", "0:45"),
             ("Sentadilla lenta", "1:00"), ("Estiramiento final", "0:45")]
    hl = [(0, {}, "hold")]
    for k in range(1, 5):
        hl += [(starts[k] - 0.3, {"dy": (k - 1) * 170}, "inout"), (starts[k], {"dy": k * 170})]
    rrect(t, t.track("shape", "Actual"), "#CDEBD9", 0.3, 11.7, Box(60, 1000, 960, 150), 30, motion=hl)
    for k, (name, time) in enumerate(steps):
        y = 1000 + k * 170
        a = 0.4 + k * 0.1
        t.solid(t.track("shape", "Número"), "#1F4E3D", a, 12.0 - a, centered(130, y + 75, 90, 90), pop(0, 0.3),
                kind="ellipse")
        done = starts[k + 1] if k < 4 else 99
        say(t, str(k + 1), a, min(done, 12.0) - a, centered(130, y + 78, 90, 90), "Nunito", 54, "#FFFFFF",
            weight=900, editable=False)
        if done < 12.0:
            say(t, "✓", done, 12.0 - done, centered(130, y + 78, 90, 90), "Nunito", 60, "#FFFFFF", weight=900,
                anim_in=tanim("pop", duration=0.25), editable=False)
        say(t, name, a, 12.0 - a, Box(210, y, 560, 150), "Nunito", 56, "#1F2A24", weight=800, align="left",
            anim_in=tanim("slide-left", duration=0.3, distance=0.1), name=f"Paso {k + 1}")
        pill(t, t.track("shape", "Tiempo"), "#E76F51", a, 12.0 - a, Box(820, y + 40, 170, 70))
        say(t, time, a, 12.0 - a, Box(820, y + 40, 170, 70), "Nunito", 44, "#FFFFFF", weight=800,
            name=f"Tiempo {k + 1}")
    song(t, "calm", 0, 0.8)
    return t


def fit_descanso():
    t = mk(wide, 50, "yt-fit-descanso", "Descanso entre series", "Rest between sets", 10.0,
           FT + ["descanso", "temporizador", "rest", "siguiente"], thumb_at=4.4, background="#0A1A33")
    photo_bg(t, "y2-h-gym-01", s1=1.06, label="Tu foto de fondo",
             effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=14)])
    shade_full(t, 0.62, colour="#0A1A33")
    say(t, "DESCANSO", 0.1, 9.9, Box(120, 120, 1000, 180), "Montserrat", 150, "#FFFFFF", weight=900, align="left",
        anim_in=tanim("slide-right", duration=0.4, distance=0.15), name="Título")
    say(t, "respira y toma agua", 0.3, 9.7, Box(124, 290, 1000, 80), "Montserrat", 54, "#9FD3FF", weight=500,
        align="left", name="Subtítulo")
    box = centered(420, 690, 380, 380)
    track_ring(t, "#FFFFFF", box, 0.0, 10.0, width=22, alpha=0.18)
    progress_ring(t, "#9FD3FF", box, 0.0, 10.0, keys([(0, 1.0, "linear"), (10.0, 0.0)]), width=22)
    nt = t.track("text", "Segundos")
    for k in range(10):
        t.text(nt, str(10 - k), k, 1.0, centered(420, 680, 380, 220),
               text_style("Montserrat", 170, [fill("#FFFFFF")], weight=900), editable=False)
    say(t, "SEGUNDOS", 0.0, 10.0, centered(420, 790, 380, 60), "Montserrat", 32, "#9FD3FF", weight=700, spacing=8,
        editable=False)
    rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", 0.4, 9.6, Box(1180, 260, 620, 640), 36,
          motion=slide_in(dx=800, length=0.5), layers=[shadow("#000000", 0, 20, 40, 0.4), fill("#FFFFFF"), no_stroke()])
    say(t, "SIGUIENTE", 0.6, 9.4, Box(1210, 290, 560, 60), "Montserrat", 40, "#1D4ED8", weight=800, spacing=10,
        align="left", name="Etiqueta")
    t.photo(t.track("video", "Siguiente"), "y2-h-gym-01", 0.6, 9.4, Box(1210, 360, 560, 340),
            slide_in(dx=800, length=0.5), label="Siguiente ejercicio")
    say(t, "SENTADILLAS", 0.8, 9.2, Box(1210, 720, 560, 90), "Montserrat", 66, "#0A1A33", weight=900, align="left",
        name="Siguiente ejercicio")
    say(t, "4 × 12", 0.8, 9.2, Box(1210, 805, 560, 70), "Montserrat", 48, "#6B7280", weight=700, align="left",
        name="Series")
    song(t, "calm", 2, 0.8)
    return t


def fit_macros():
    t = mk(tall, 51, "yt-fit-macros", "Macros de mi comida", "My meal macros", 10.0,
           FT + ["nutrición", "macros", "proteína", "dieta"], thumb_at=6.0, background="#F3FBF4")
    bg(t, "#F3FBF4")
    t.photo(t.track("video", "Comida"), "y2-dish-01", 0.0, 10.0, Box(60, 80, 960, 820), kb(10.0, 1.0, 1.06),
            label="Foto de tu comida")
    rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", 0.2, 9.8, Box(60, 860, 960, 1000), 44,
          motion=slide_in(dy=1100, length=0.5), layers=[shadow("#0F3D2E", 0, -10, 40, 0.18), fill("#FFFFFF"),
                                                         no_stroke()])
    say(t, "BOWL DE POLLO", 0.5, 9.5, Box(110, 900, 860, 100), "Plus Jakarta Sans", 76, "#10251C", weight=800,
        align="left", anim_in=tanim("rise", duration=0.4), name="Plato")
    count_up(t, t.track("text", "Calorías"), 0, 610, "610", 0.8, 2.0, Box(110, 1000, 420, 160),
             big("Plus Jakarta Sans", 140, "#16A34A", weight=800, align="left"), name="Calorías")
    say(t, "kcal", 0.8, 9.2, Box(450, 1060, 300, 90), "Plus Jakarta Sans", 60, "#16A34A", weight=700, align="left",
        editable=False)
    macros = [("Proteína", 42, 0.8, "#EF476F"), ("Carbohidratos", 55, 0.6, "#FFB703"), ("Grasas", 18, 0.35,
                                                                                       "#06D6A0")]
    for k, (name, g, frac, colour) in enumerate(macros):
        y = 1210 + k * 200
        a = 1.2 + k * 0.3
        say(t, name, a, 10.0 - a, Box(110, y, 560, 80), "Plus Jakarta Sans", 52, "#10251C", weight=700, align="left",
            name=f"Macro {k + 1}")
        count_up(t, t.track("text", "Gramos"), 0, g, f"{g} g", a, 1.6, Box(670, y, 300, 80),
                 big("Plus Jakarta Sans", 56, colour, weight=800, align="right"), suffix=" g", name=f"Gramos {k + 1}")
        rrect(t, t.track("shape", "Carril"), "#E8EFEA", a, 10.0 - a, Box(110, y + 95, 860, 34), 17)
        t.solid(t.track("shape", "Barra"), colour, a, 10.0 - a, Box(110, y + 95, 860 * frac, 34),
                [(0, {"sx": 0.0, "dx": -430 * frac}, "out"), (1.6, {})], radius=17, kind="rounded-rectangle")
    song(t, "fun", 1, 0.8)
    return t


def fit_sin_excusas():
    t = mk(tall, 52, "yt-fit-sin-excusas", "Sin excusas", "No excuses", 8.0,
           FT + ["motivación", "sin excusas", "hype", "motivation"], thumb_at=6.0)
    bw = [effect("color.basic", saturation=-1.0, contrast=0.35)]
    samples = ["y2-h-gym-01", "beach-01", "gym-01", "y2b-h-gym-01", "y2-h-gym-06", "y2-h-gym-07", "h-beach-01",
               "beach-01"]
    starts = [k * 0.5 for k in range(8)]
    track = t.track("video", "Cortes")
    cuts(t, samples, starts, 4.0, punch_in=True, track=track, effects=bw)
    t.photo(track, "gym-01", 4.0, 4.0, t.full, kb(4.0, 1.12, 1.0), label="Foto final", effects=bw)
    t.solid(t.track("shape", "Tinte"), "#E10600", 4.0, 4.0, alpha=0.25, opacity=keys([(0, 0.0, "out"), (0.4, 1.0)]))
    shade_bottom(t, 1100, 0.8, t0=4.0, dur=4.0)
    words = [("SIN", 400), ("EXCUSAS", 1250), ("SIN", 400), ("LÍMITES", 1250)]
    wt = t.track("text", "Palabras")
    for k, (w, y) in enumerate(words):
        t.text(wt, w, k * 1.0, 1.0, Box(60, y, 960, 260),
               text_style("Anton", 190, [fill("#FFFFFF")], weight=400, box=("#E10600", 1.0), box_pad=18,
                          anim_in=tanim("slide-right" if k % 2 else "slide-left", duration=0.2, distance=0.5)),
               label=f"Palabra {k + 1}", rotation=keys([(0, -3 if k % 2 else 3)]))
    lines = ["ENTRENA", "DURO.", "SIN", "EXCUSAS."]
    for k, ln in enumerate(lines):
        a = 4.0 + k * 0.35
        say(t, ln, a, 8.0 - a, Box(60, 900 + k * 230, 960, 240), "Anton", 220,
            "#E10600" if k % 2 else "#FFFFFF", weight=400, align="left", line=0.95,
            anim_in=tanim("slide-up", duration=0.25, distance=0.5), name=f"Línea {k + 1}")
    grain(t, 0.25)
    punch(t, starts + [4.0], 0.35, 0.25, shake=0.3)
    song(t, "epic", 5, 0.85)
    return t


def fit_en_casa():
    t = mk(wide, 53, "yt-fit-rutina-en-casa", "Rutina en casa", "Home workout", 12.0,
           FT + ["en casa", "rutina", "sin equipo", "home workout"], thumb_at=5.5, background="#1C1C1E")
    bg(t, "#1C1C1E")
    say(t, "RUTINA EN CASA", 0.1, 11.9, Box(60, 30, 1100, 110), "Rubik", 84, "#FFD60A", weight=900, align="left",
        anim_in=tanim("slide-right", duration=0.4, distance=0.15), name="Título")
    say(t, "3 ejercicios · 20 s cada uno", 0.3, 11.7, Box(1000, 55, 860, 70), "Rubik", 42, "#BDBDBD", weight=500,
        align="right", name="Subtítulo")
    samples = ["beach-01", "h-beach-01", "outfit-04"]
    names = ["FLEXIONES", "FONDOS", "SENTADILLAS"]
    xs = [60, 670, 1280]
    act = [1.0 + k * 3.3 for k in range(3)]
    for k in range(3):
        x = xs[k]
        a0 = 0.3 + k * 0.15
        t.photo(t.track("video", "Foto"), samples[k], a0, 12.0 - a0, Box(x, 170, 580, 620),
                slide_in(dy=900, length=0.5), label=f"Ejercicio {k + 1}")
        say(t, names[k], a0, 12.0 - a0, Box(x + 10, 810, 560, 90), "Rubik", 60, "#FFFFFF", weight=800, align="left",
            name=f"Ejercicio {k + 1}")
        rrect(t, t.track("shape", "Carril"), "#FFFFFF", a0, 12.0 - a0, Box(x + 10, 930, 420, 26), 13, alpha=0.15)
        a, b = act[k], act[k] + 3.3
        t.solid(t.track("shape", "Tiempo"), "#FFD60A", a, b - a, Box(x + 10, 930, 420, 26),
                [(0, {}, "linear"), (3.3, {"sx": 0.0, "dx": -210})], radius=13, kind="rounded-rectangle")
        say(t, "0:20", a0, 12.0 - a0, Box(x + 440, 905, 130, 70), "Rubik", 48, "#FFFFFF", weight=700, align="right",
            name=f"Tiempo {k + 1}")
        # Dim the panel when it is not its turn.
        if a > a0:
            t.solid(t.track("shape", "Espera"), "#000000", a0, a - a0, Box(x, 170, 580, 820), alpha=0.6)
        t.solid(t.track("shape", "Hecho"), "#000000", b, 12.0 - b, Box(x, 170, 580, 820), alpha=0.6,
                opacity=keys([(0, 0.0, "out"), (0.3, 1.0)]))
        t.solid(t.track("shape", "Check"), "#FFD60A", b, 12.0 - b, centered(x + 290, 480, 180, 180), pop(0, 0.35),
                kind="ellipse")
        say(t, "✓", b, 12.0 - b, centered(x + 290, 488, 180, 180), "Rubik", 120, "#1C1C1E", weight=900,
            anim_in=tanim("pop", duration=0.3), editable=False)
        outline(t, t.track("shape", "Activo"), "#FFD60A", 8, a, 3.3, Box(x - 8, 162, 596, 836), radius=12)
    t.solid(t.track("shape", "Banda"), "#FFD60A", 10.9, 1.1, centered(960, 560, 900, 220), pop(0, 0.3),
            rotation=keys([(0, -4)]), layers=[shadow("#000000", 0, 12, 0, 1.0), fill("#FFD60A"), no_stroke()])
    say(t, "¡HECHO!", 10.9, 1.1, centered(960, 560, 900, 220), "Rubik", 150, "#1C1C1E", weight=900,
        rotation=keys([(0, -4)]), anim_in=tanim("stamp", duration=0.3), name="Mensaje")
    song(t, "upbeat", 1, 0.85)
    return t


def _guarded(make):
    """Refuses to build a template that shows a blocked sample photo."""
    @functools.wraps(make)
    def build():
        t = make()
        bad = sorted({c["_sample"] for tr in t.tracks for c in tr.clips if c.get("_sample") in BLOCKED})
        if bad:
            raise SystemExit(f"{t.id}: blocked sample photos: {', '.join(bad)}")
        return t
    return build


TEMPLATES = [
    reto_1_vs_millon, reto_ultimo_gana, reto_dia1_dia100, reto_24_horas, reto_premio_gigante, reto_eliminados,
    reto_barato_caro, reto_no_te_muevas, reto_sobrevivi, reto_100_personas, reto_caja_misteriosa, reto_intro_hype,
    reto_marcador, reto_aguanta_60, reto_gasta_todo, reto_ganador, reto_1_vs_100, reto_10_dolares,
    top_10_rapido, top_podio, top_tarjetas, top_lista_lateral, top_cine, top_neon, top_revelacion, top_comida,
    top_lugares, top_tabla, top_papel, top_retro, top_split, top_datos, top_peor_mejor, top_medallas,
    top_ranking_vacio, top_intro,
    fit_reps, fit_tabata, fit_antes_despues, fit_plan_semana, fit_rutina_pasos, fit_serie_hud, fit_hiit_neon,
    fit_30_dias, fit_transformacion, fit_calorias, fit_correr_km, fit_ejercicio_dia, fit_record, fit_calentamiento,
    fit_descanso, fit_macros, fit_sin_excusas, fit_en_casa,
]
TEMPLATES = [_guarded(m) for m in TEMPLATES]
