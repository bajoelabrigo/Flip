"""YouTuber-style templates (0.15.0, part B of docs/plan-stock.md): Gaming y streamer, Cocina, Misterio / true crime.
Category youtuber; order 6400-6499; ids `yt-game-*`, `yt-coc-*`, `yt-mist-*`.

- Gaming y streamer (6400-6417): gameplay slot with a face-cam frame, follower / subscriber alerts, «GG»,
  «VICTORIA» / «DERROTA», scoreboard, highlight reel, «Empezamos pronto» / «Vuelvo enseguida», kill-feed
  captions, MVP card, tournament bracket, level up. Mostly 16:9. No game names, logos or game screens.
- Cocina (6420-6437): ingredients that appear one by one, numbered steps, timer, the final plate reveal, recipe
  cards with portions and time, top-down layouts. 9:16 and 16:9.
- Misterio / true crime (6440-6457): case file, photos pinned with red string, typewriter text, redacted lines,
  timelines, map pins, «caso sin resolver», newspaper clipping, CCTV. Tasteful, no gore. 9:16 and 16:9.

Helpers live here (string between pins, face-cam frames, paper, stamps...). Boxes in project pixels of each
template's own size; tracks bottom-up (scene.py).
"""

from __future__ import annotations

from kit import (Box, appear, bg, bg_gradient, blink, centered, circle_photo, confetti, dots, effect, fill, flash,
                 framed, glow, gradient, grain, keys, kb, label, letterbox, line, math, no_stroke, outline, panels, photo_bg,
                 pill, pop, random, ring, rrect, shade_bottom, shade_full, shade_top, shadow, slide_in, slides, spike,
                 stroke, tall, tanim, text_style, vignette, wide)
from templates_c1 import big, count_fn, curve_motion, geo, group, hollow_ring, rays

O = 6400
CAT = "youtuber"
GAME = ["youtuber", "gaming", "streamer"]
COC = ["youtuber", "cocina", "cooking", "receta"]
MIST = ["youtuber", "misterio", "true crime"]


def _t(maker, id, es, en, i, tags, duration, **kw):
    return maker(id, es, en, CAT, duration, order=O + i, tags=tags, **kw)


def music(t, music_id: str, start: float, volume: float = 0.8):
    t.song(music_id, float(start), volume)


def rot(angle: float) -> dict:
    return keys([(0, angle)])


# --- shared pieces ----------------------------------------------------------------------------------

def hollow_layers(colour: str, width: float, alpha: float = 1.0, glow_c: str | None = None, glow_r: float = 22):
    # A glow layer on a hollow shape fills it (2026-10-17 render): glow_c only brightens the stroke.
    layers = hollow_ring(colour, width, alpha)
    if glow_c:
        layers = layers + [{"id": "stroke2", "kind": "stroke", "enabled": True, "width": width * 0.35,
                            "strokeAlign": "inside", "paint": {"kind": "solid", "color": "#ccffffff"}, "opacity": 1.0}]
    return layers


def facecam(t, sample: str, box: Box, colour: str, t0: float, dur: float, *, motion=None, width: float = 8,
            glow_c: str | None = None, radius: float = 8, label_="Tu cámara", backing: str = "#0A0A12",
            reuse=None):
    """A face-cam slot in a frame: a dark backing, the photo inset by the frame width, the frame on top."""
    t.solid(t.track("shape", "Cámara fondo"), backing, t0, dur, box, motion, radius=radius, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 10, 30, 0.5), fill(backing), no_stroke()])
    inner = Box(box.x + width * 0.5, box.y + width * 0.5, box.w - width, box.h - width)
    clip = t.photo(t.track("video", "Cámara"), sample, t0, dur, inner, motion, label=label_, reuse=reuse)
    t.solid(t.track("shape", "Marco cámara"), colour, t0, dur, box, motion, radius=radius, kind="rounded-rectangle",
            layers=hollow_layers(colour, width, glow_c=glow_c))
    return clip


def gameplay(t, sample: str, t0: float = 0.0, dur: float | None = None, box: Box | None = None, *, s1: float = 1.06,
             label_="Tu partida (gameplay)", effects=None, reuse=None, motion=None):
    dur = t.duration - t0 if dur is None else dur
    box = box or t.full
    extra = {"effects": effects} if effects else {}
    return t.photo(t.track("video", "Partida"), sample, t0, dur, box, motion or kb(dur, 1.0, s1), label=label_,
                   reuse=reuse, **extra)


def live_badge(t, x: float, y: float, t0: float, dur: float, text="EN VIVO", colour="#FF1F4B", font="Russo One",
               size=34, w=230, h=64):
    pill(t, t.track("shape", "En vivo"), colour, t0, dur, Box(x, y, w, h), pop(0, 0.35))
    t.solid(t.track("shape", "Punto"), "#FFFFFF", t0, dur, centered(x + h * 0.55, y + h / 2, h * 0.28, h * 0.28),
            kind="ellipse", opacity=blink(dur, 1.0, 0.2))
    label(t, t.track("text", "En vivo"), text, t0, dur, Box(x + h * 0.85, y, w - h * 0.95, h), font, size, "#FFFFFF",
          weight=400, align="left", editable=False, anim_in=tanim("fade", duration=0.3))


def grid_bg(t, colour: str, line_c: str, step: float = 80, alpha: float = 0.18, t0=0.0, dur=None, drift: float = 0):
    """A flat colour with a thin square grid (gaming HUD)."""
    dur = t.duration - t0 if dur is None else dur
    if colour:
        t.solid(t.track("shape", "Fondo"), colour, t0, dur)
    tr = t.track("shape", "Rejilla")
    n = 0
    x = 0.0
    while x <= t.w:
        t.solid(tr, line_c, t0, dur, Box(x, 0, 2, t.h), alpha=alpha,
                motion=[(0, {}), (dur, {"dx": drift})] if drift else None)
        x += step
        n += 1
        if n % 12 == 0:
            tr = t.track("shape", "Rejilla")
    y = 0.0
    tr = t.track("shape", "Rejilla")
    while y <= t.h:
        t.solid(tr, line_c, t0, dur, Box(0, y, t.w, 2), alpha=alpha,
                motion=[(0, {}), (dur, {"dy": drift})] if drift else None)
        y += step
        n += 1
        if n % 12 == 0:
            tr = t.track("shape", "Rejilla")


def slashes(t, colours: list[str], at: float, cy: float, angle: float = -12, h: float = 70, length: float = 0.5,
            dur: float | None = None):
    """Bars that slash across the frame at an angle and stay (or leave after dur)."""
    for i, c in enumerate(colours):
        y = cy + (i - (len(colours) - 1) / 2) * h * 1.25
        d = dur if dur else t.duration - at - i * 0.06
        mo = [(0, {"dx": -t.w * 1.4}, "out"), (length, {})]
        if dur:
            mo += [(d - length * 0.7, {}, "in"), (d, {"dx": t.w * 1.4})]
        t.solid(t.track("shape", "Franja"), c, at + i * 0.06, d, centered(t.w / 2, y, t.w * 1.3, h), mo, rotation=rot(angle))


def pin_string(t, p1, p2, t0: float, dur: float | None = None, colour: str = "#C1121F", width: float = 5,
               draw: float = 0.6, track=None):
    """A taut string from p1 to p2 that draws itself from p1 (the box turns about its centre)."""
    dur = t.duration - t0 if dur is None else dur
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy)
    angle = math.degrees(math.atan2(dy, dx))
    box = centered((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, length, width)
    motion = [(0, {"sx": 0.002, "dx": -dx / 2, "dy": -dy / 2}, "out"), (draw, {})]
    t.solid(track or t.track("shape", "Hilo"), colour, t0, dur, box, motion,
            layers=[shadow("#000000", 2, 4, 4, 0.45), fill(colour), no_stroke()], rotation=rot(angle))


def push_pin(t, x: float, y: float, t0: float, colour: str = "#D62828", size: float = 34, dur=None):
    dur = t.duration - t0 if dur is None else dur
    t.solid(t.track("shape", "Chinche"), colour, t0, dur, centered(x, y, size, size),
            [(0, {"s": 2.2, "dy": -30}, "snap"), (0.18, {})], kind="ellipse",
            layers=[shadow("#000000", 3, 6, 6, 0.55), fill(colour), stroke(2, "#000000", 0.25)])
    t.solid(t.track("shape", "Brillo"), "#FFFFFF", t0, dur, centered(x - size * 0.15, y - size * 0.15, size * 0.3, size * 0.3),
            [(0, {"s": 2.2, "dy": -30}, "snap"), (0.18, {})], kind="ellipse", alpha=0.7)


def paper(t, box: Box, t0: float, dur: float | None = None, colour: str = "#EFE6D2", motion=None, rotation=0.0,
          radius: float = 4, shadow_alpha: float = 0.45, name="Papel"):
    dur = t.duration - t0 if dur is None else dur
    return t.solid(t.track("shape", name), colour, t0, dur, box, motion, radius=radius, kind="rounded-rectangle",
                   layers=[shadow("#000000", 0, 10, 26, shadow_alpha), fill(colour), no_stroke()], rotation=rot(rotation))


def stamp(t, content: str, box: Box, at: float, colour: str = "#B3121B", size: int = 90, angle: float = -12,
          font: str = "Black Ops One", dur=None, name="Sello", editable=True, spacing: float = 6):
    """A rubber stamp: a hollow frame and the word, slammed on."""
    dur = t.duration - at if dur is None else dur
    mo = [(0, {"s": 2.4}, "snap"), (0.22, {})]
    t.solid(t.track("shape", "Sello"), colour, at, dur, box, mo, radius=10, kind="rounded-rectangle",
            layers=hollow_ring(colour, 9, 0.9), rotation=rot(angle), opacity=keys([(0, 0.0), (0.12, 0.92)]))
    clip = label(t, t.track("text", "Sello"), content, at, dur, box, font, size, colour, weight=400, spacing=spacing,
                 layers=[fill(colour, 0.9)], anim_in=tanim("stamp", duration=0.22), rotation=rot(angle), name=name,
                 editable=editable)
    clip["textStyle"]["wordWrap"] = False


def typed(t, content: str, box: Box, t0: float, duration: float, *, size: int = 40, colour: str = "#1E1B16",
          font: str = "Special Elite", align: str = "left", valign="top", line_h: float = 1.35, end=None, name=None,
          caret=False, editable=True, weight=400, spacing=0.0):
    """Typewriter text: characters come one by one over `duration`."""
    end = t.duration if end is None else end
    return label(t, t.track("text", "Máquina"), content, t0, end - t0, box, font, size, colour, weight=weight,
                 align=align, valign=valign, line=line_h, spacing=spacing,
                 anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=duration / max(1, len(content)) / 1.7,
                               caret=caret), name=name,
                 editable=editable)


def redact(t, box: Box, at: float, colour: str = "#0B0B0B", length: float = 0.35, end=None):
    end = t.duration if end is None else end
    line(t, t.track("shape", "Tachado"), colour, at, end - at, box, grow="x", length=length)


def step_badge(t, n: str, cx: float, cy: float, d: float, t0: float, dur: float, colour: str, ink: str,
               font="Lilita One", size=None, motion=None, ring_c=None):
    mo = motion or pop(0, 0.4)
    t.solid(t.track("shape", "Número"), colour, t0, dur, centered(cx, cy, d, d), mo, kind="ellipse",
            layers=[shadow("#000000", 0, 6, 14, 0.35), fill(colour)] + ([stroke(6, ring_c)] if ring_c else [no_stroke()]))
    label(t, t.track("text", "Número"), n, t0, dur, centered(cx, cy + d * 0.03, d, d), font, size or round(d * 0.58), ink,
          weight=400, editable=False, motion=mo)


# =====================================================================================================
# 1. GAMING Y STREAMER
# =====================================================================================================

NEON_C, NEON_M = "#22D3EE", "#F72585"


def game_overlay_neon():
    t = _t(wide, "yt-game-overlay-neon", "Overlay de directo neón", "Neon stream overlay", 0,
           GAME + ["overlay", "cámara", "facecam", "en vivo", "live"], 10.0, thumb_at=5.6, background="#05050A")
    gameplay(t, "y6-h-play-02", s1=1.04)
    shade_bottom(t, 260, 0.75)
    shade_top(t, 200, 0.55)
    # Top-left: live badge and viewers.
    live_badge(t, 40, 36, 0.2, 9.8)
    label(t, t.track("text", "Espectadores"), "👁 1.248", 0.4, 9.6, Box(290, 36, 260, 64), "Russo One", 34, "#FFFFFF",
          weight=400, align="left", anim_in=tanim("fade", duration=0.4), name="Espectadores")
    # Face-cam, bottom right.
    cam = Box(1420, 590, 460, 345)
    facecam(t, "y6-gamer-04", cam, NEON_C, 0.0, 10.0, width=8, glow_c=NEON_C,
            motion=[(0, {"dx": 520}, "out"), (0.6, {})])
    rrect(t, t.track("shape", "Nombre"), NEON_M, 0.5, 9.5, Box(1420, 945, 460, 62), 8,
          motion=[(0, {"dx": 520}, "out"), (0.6, {})], layers=[glow(NEON_M, 18, 0.7), fill(NEON_M), no_stroke()])
    label(t, t.track("text", "Canal"), "@TuCanal", 0.6, 9.4, Box(1420, 945, 460, 62), "Orbitron", 34, "#FFFFFF",
          weight=800, spacing=2, anim_in=tanim("fade", duration=0.4), name="Canal")
    # Bottom ticker: last follower and a goal bar.
    t.solid(t.track("shape", "Barra"), "#0B0B18", 0.3, 9.7, Box(40, 960, 1340, 80), [(0, {"dy": 140}, "out"), (0.5, {})],
            radius=12, kind="rounded-rectangle", layers=[fill("#0B0B18", 0.85), stroke(2, NEON_C, 0.6)])
    label(t, t.track("text", "Seguidor"), "ÚLTIMO SEGUIDOR: Luna_22", 0.6, 9.4, Box(70, 960, 700, 80), "Russo One", 32,
          NEON_C, weight=400, align="left", anim_in=tanim("slide-right", duration=0.4, distance=0.1), name="Último seguidor")
    label(t, t.track("text", "Meta"), "META 820 / 1.000", 0.7, 9.3, Box(760, 960, 300, 80), "Russo One", 30, "#FFFFFF",
          weight=400, align="left", anim_in=tanim("fade", duration=0.4), name="Meta")
    t.solid(t.track("shape", "Meta"), "#FFFFFF", 0.7, 9.3, Box(1070, 990, 280, 20), radius=10, kind="rounded-rectangle",
            alpha=0.2)
    t.solid(t.track("shape", "Meta"), NEON_M, 0.9, 9.1, Box(1070, 990, 230, 20),
            [(0, {"sx": 0.0, "dx": -115}, "out"), (1.2, {})], radius=10, kind="rounded-rectangle",
            layers=[glow(NEON_M, 12, 0.8), fill(NEON_M), no_stroke()])
    # A follow toast that comes in from the right at 3.5 s.
    toast = Box(1420, 140, 460, 110)
    mo = [(0, {"dx": 560}, "back"), (0.5, {}, "hold"), (3.6, {}, "in"), (4.0, {"dx": 560})]
    t.solid(t.track("shape", "Aviso"), "#120B24", 3.5, 4.0, toast, mo, radius=16, kind="rounded-rectangle",
            layers=[glow(NEON_M, 22, 0.8), fill("#120B24", 0.95), stroke(3, NEON_M)])
    label(t, t.track("text", "Aviso"), "♥", 3.5, 4.0, Box(1430, 140, 110, 110), "Inter", 60, NEON_M, weight=900,
          editable=False, motion=mo)
    label(t, t.track("text", "Aviso"), "Luna_22\nahora te sigue", 3.5, 4.0, Box(1540, 150, 330, 90), "Russo One", 34,
          "#FFFFFF", weight=400, align="left", line=1.15, motion=mo, name="Aviso de seguidor")
    music(t, "blippy-trance", 10, 0.75)
    return t


def game_alerta_sub():
    t = _t(wide, "yt-game-alerta-sub", "Alerta: nuevo suscriptor", "New subscriber alert", 1,
           GAME + ["alerta", "suscriptor", "subscriber alert"], 6.0, thumb_at=2.6, background="#0A0614")
    gameplay(t, "y6-h-fantasy-01", s1=1.05)
    shade_full(t, 0.3, colour="#0A0614")
    facecam(t, "y6-gamer-01", Box(40, 690, 400, 300), "#FACC15", 0.0, 6.0, width=7, radius=14)
    # The alert: a turning burst behind a card that drops in, waits and leaves.
    mo = [(0, {"dy": -560}, "back"), (0.55, {}, "hold"), (4.6, {}, "in"), (5.0, {"dy": -560})]
    card = Box(560, 150, 800, 330)
    clip = t.solid(t.track("shape", "Estallido"), "#FACC15", 0.6, 4.4, centered(960, 315, 900, 900),
                   [(0, {"s": 0.0}, "back"), (0.6, {})], kind="burst", alpha=0.35,
                   rotation=keys([(0, 0), (4.4, 70)]), opacity=keys([(0, 1.0, "hold"), (3.9, 1.0), (4.4, 0.0)]))
    geo(clip, points=16, innerRatio=0.55)
    t.solid(t.track("shape", "Alerta"), "#6D28D9", 0.5, 4.5, card, mo, radius=28, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 16, 40, 0.6), gradient([(0, "#7C3AED"), (1, "#C026D3")], angle=135),
                    stroke(6, "#FACC15")])
    t.solid(t.track("shape", "Estrella"), "#FACC15", 0.5, 4.5, centered(960, 150, 130, 130), group(mo, 0, -165),
            kind="star", layers=[shadow("#000000", 0, 6, 12, 0.5), fill("#FACC15"), stroke(5, "#FFFFFF")],
            rotation=keys([(0, -20), (0.8, 0, "out")]))
    label(t, t.track("text", "Alerta"), "¡NUEVO SUSCRIPTOR!", 0.6, 4.4, Box(580, 230, 760, 90), "Russo One", 66,
          "#FACC15", weight=400, motion=mo, layers=[shadow("#000000", 0, 5, 0, 0.6), fill("#FACC15")],
          anim_in=tanim("pop", duration=0.35), name="Alerta")
    label(t, t.track("text", "Nombre"), "@NombreDelFan", 0.8, 4.2, Box(580, 320, 760, 90), "Orbitron", 58, "#FFFFFF",
          weight=800, motion=mo, anim_in=tanim("slide-up", duration=0.35), name="Nombre")
    label(t, t.track("text", "Gracias"), "¡Gracias por unirte al equipo!", 1.0, 4.0, Box(580, 400, 760, 60), "Exo 2", 34,
          "#F5E9FF", weight=600, motion=mo, anim_in=tanim("fade", duration=0.4), name="Mensaje")
    dots(t, ["#FACC15", "#FFFFFF", "#F472B6"], 22, 0.7, 4.0, seed=6401, size=(14, 30), kinds=("star",), drift=120,
         area=Box(480, 80, 960, 480))
    flash(t, 0.55, 0.3, colour="#FACC15", peak=0.35)
    t.adjust([effect("zoom_pulse", animated={"punch": spike([0.55], 0.4, 0.35)})], name="Golpe")
    music(t, "funky-energy-loop", 4, 0.8)
    return t


def game_alerta_vertical():
    t = _t(tall, "yt-game-alerta-vertical", "Directo vertical con alerta", "Vertical stream with alert", 2,
           GAME + ["vertical", "seguidor", "follower alert", "en directo"], 8.0, thumb_at=3.0, background="#07070C")
    gameplay(t, "y6-h-play-01", box=Box(0, 700, 1080, 1220), s1=1.06)
    t.photo(t.track("video", "Cámara"), "y6-gamer-04", 0, 8.0, Box(0, 0, 1080, 700), kb(8.0, 1.0, 1.04),
            label="Tu cámara")
    shade_top(t, 260, 0.55)
    t.solid(t.track("shape", "Divisor"), "#A3E635", 0, 8.0, Box(0, 692, 1080, 16), [(0, {"sx": 0.0}, "out"), (0.5, {})],
            layers=[glow("#A3E635", 20, 0.9), fill("#A3E635"), no_stroke()])
    live_badge(t, 40, 50, 0.2, 7.8, text="EN DIRECTO", colour="#16A34A", w=290)
    label(t, t.track("text", "Canal"), "@TuCanal", 0.4, 7.6, Box(360, 50, 680, 64), "Russo One", 40, "#FFFFFF",
          weight=400, align="right", layers=[shadow("#000000", 0, 3, 10, 0.7), fill("#FFFFFF")],
          anim_in=tanim("fade", duration=0.4), name="Canal")
    # Alert on the divider at 1.6 s.
    mo = [(0, {"s": 0.0}, "back"), (0.45, {}, "hold"), (4.6, {}, "in"), (5.0, {"s": 0.0})]
    a = Box(110, 600, 860, 200)
    t.solid(t.track("shape", "Alerta"), "#0B0B0B", 1.6, 5.0, a, mo, radius=100, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 14, 30, 0.6), fill("#0B0B0B"), stroke(6, "#A3E635")])
    t.solid(t.track("shape", "Corazón"), "#A3E635", 1.6, 5.0, centered(225, 700, 120, 110), group(mo, -315, 0),
            kind="heart", layers=[glow("#A3E635", 16, 0.8), fill("#A3E635"), no_stroke()])
    label(t, t.track("text", "Alerta"), "NUEVO SEGUIDOR", 1.75, 4.85, Box(310, 612, 640, 80), "Russo One", 52, "#A3E635",
          weight=400, align="left", anim_in=tanim("slide-right", duration=0.3, distance=0.15),
          anim_out=tanim("fade", duration=0.2), name="Alerta")
    label(t, t.track("text", "Nombre"), "@gamer_sol", 1.9, 4.7, Box(310, 690, 640, 90), "Exo 2", 56, "#FFFFFF",
          weight=800, align="left", anim_in=tanim("slide-right", duration=0.3, distance=0.15),
          anim_out=tanim("fade", duration=0.2), name="Nombre")
    for k in range(6):
        ang = k * 60
        dx, dy = 260 * math.cos(math.radians(ang)), 140 * math.sin(math.radians(ang))
        t.solid(t.track("shape", "Chispa"), "#A3E635", 1.7, 0.8, centered(540, 700, 26, 26),
                [(0, {"s": 0.3}, "out"), (0.8, {"dx": dx * 1.8, "dy": dy * 1.8, "s": 1.0})], kind="heart",
                opacity=keys([(0, 1.0), (0.8, 0.0)]))
    label(t, t.track("text", "Pie"), "¡Gracias por el follow! 💚", 2.4, 5.2, Box(60, 1700, 960, 110), "Exo 2", 54,
          "#FFFFFF", weight=800, box_bg=("#000000", 0.6), box_pad=22, box_radius=20,
          anim_in=tanim("rise", duration=0.4), name="Pie")
    music(t, "funky-energy-loop", 20, 0.75)
    return t


def game_gg():
    t = _t(wide, "yt-game-gg", "GG: buena partida", "GG: good game", 3,
           GAME + ["gg", "final", "buena partida", "good game"], 5.0, thumb_at=2.4, background="#000000")
    gameplay(t, "y6-h-play-03", s1=1.1)
    t.adjust([effect("builtin.effects.gaussian_blur", animated={"u_blurRadius": keys([(0, 0.0, "hold"), (0.5, 0.0, "out"),
                                                                                       (1.0, 16.0)])}),
              effect("color.basic", saturation=-0.4, exposure=-0.2)], name="Desenfoque")
    shade_full(t, 0.35)
    slashes(t, [NEON_C, NEON_M], 0.5, 560, angle=-10, h=180)
    label(t, t.track("text", "GG"), "GG", 0.6, 4.4, Box(0, 170, 1920, 560), "Black Ops One", 470, "#FFFFFF", weight=400,
          layers=[shadow("#000000", 0, 16, 0, 0.9), glow(NEON_M, 40, 0.8), stroke(14, "#111111"), fill("#FFFFFF")],
          anim_in=tanim("stamp", duration=0.3, **{"from": 300}), anim_loop=tanim("jitter", amount=0.6, speed=10),
          name="GG")
    label(t, t.track("text", "Sub"), "BUENA PARTIDA", 1.0, 4.0, Box(0, 740, 1920, 100), "Orbitron", 70, "#FFFFFF",
          weight=900, spacing=18, layers=[glow(NEON_C, 18, 0.8), fill("#FFFFFF")],
          anim_in=tanim("wipe", duration=0.5, angle=0), name="Subtítulo")
    label(t, t.track("text", "Pie"), "nos vemos en la próxima", 1.5, 3.5, Box(0, 850, 1920, 70), "Exo 2", 40, "#E0F7FF",
          weight=600, anim_in=tanim("fade", duration=0.4), name="Pie")
    flash(t, 0.6, 0.3, peak=0.8)
    t.adjust([effect("rgb_split", animated={"amount": spike([0.6, 2.6], 26.0, 0.35)}),
              effect("beat_shake", animated={"amount": spike([0.6], 0.8, 0.35)})], name="Golpe")
    music(t, "action-strike", 4, 0.85)
    return t


def game_victoria():
    t = _t(wide, "yt-game-victoria", "Pantalla de victoria", "Victory screen", 4,
           GAME + ["victoria", "ganador", "victory", "estadísticas"], 7.0, thumb_at=3.6, background="#0B1026")
    gameplay(t, "y6-h-fantasy-03", s1=1.08, effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=12)])
    shade_full(t, 0.55, colour="#0B1026")
    rays(t, "#FCD34D", 0.3, 6.7, centered(960, 300, 1500, 1500), alpha=0.16, points=20, speed=8)
    label(t, t.track("text", "Puesto"), "#1", 0.4, 6.6, centered(960, 120, 300, 120), "Russo One", 90, "#0B1026",
          weight=400, box_bg=("#FCD34D", 1.0), box_pad=16, box_radius=16, anim_in=tanim("pop", duration=0.35),
          name="Puesto")
    label(t, t.track("text", "Victoria"), "VICTORIA", 0.6, 6.4, Box(0, 190, 1920, 280), "Russo One", 230, "#FCD34D",
          weight=400, layers=[shadow("#000000", 0, 14, 20, 0.7), glow("#F59E0B", 30, 0.6),
                              gradient([(0, "#FFF7D1"), (0.5, "#FCD34D"), (1, "#D97706")], angle=90)],
          anim_in=tanim("zoom-out", duration=0.6, **{"from": 170}), name="Título")
    label(t, t.track("text", "Jugador"), "JugadorPro · Equipo Nova", 1.0, 6.0, Box(0, 470, 1920, 80), "Exo 2", 46,
          "#FFFFFF", weight=700, spacing=4, anim_in=tanim("fade", duration=0.5), name="Jugador")
    stats = [("ELIMINACIONES", "12"), ("PRECISIÓN", "68 %"), ("TIEMPO", "18:42")]
    for i, (k, v) in enumerate(stats):
        at = 1.4 + i * 0.2
        box = Box(300 + i * 460, 620, 400, 260)
        mo = [(0, {"dy": 120}, "out"), (0.45, {})]
        t.solid(t.track("shape", "Dato"), "#111833", at, 7.0 - at, box, mo, radius=20, kind="rounded-rectangle",
                layers=[shadow("#000000", 0, 10, 24, 0.5), fill("#111833", 0.9), stroke(3, "#FCD34D", 0.8)],
                opacity=keys([(0, 0.0), (0.3, 1.0)]))
        label(t, t.track("text", "Dato"), v, at + 0.1, 6.9 - at, Box(box.x, box.y + 30, box.w, 140), "Russo One", 100,
              "#FFFFFF", weight=400, anim_in=tanim("pop", duration=0.3), name=f"Valor {i + 1}")
        label(t, t.track("text", "Dato"), k, at + 0.15, 6.85 - at, Box(box.x, box.y + 170, box.w, 60), "Exo 2", 34,
              "#FCD34D", weight=800, spacing=4, anim_in=tanim("fade", duration=0.3), name=f"Dato {i + 1}")
    confetti(t, ["#FCD34D", "#FFFFFF", "#F59E0B"], 0.6, 6.4, seed=6404, lanes=3, density=0.35, size=(14, 30))
    flash(t, 0.6, 0.35, colour="#FFF7D1", peak=0.6)
    music(t, "new-hero-in-town", 0, 0.85)
    return t


def game_derrota():
    t = _t(wide, "yt-game-derrota", "Pantalla de derrota", "Defeat screen", 5,
           GAME + ["derrota", "perdí", "defeat", "revancha"], 6.0, thumb_at=2.8, background="#0A0000")
    gameplay(t, "y6-h-play-03", s1=1.03, effects=[effect("color.basic", saturation=-0.85, contrast=0.2, exposure=-0.15)])
    t.solid(t.track("shape", "Rojo"), "#7F1D1D", 0, 6.0, blendMode="multiply", opacity=keys([(0, 0.0), (0.5, 0.85)]))
    # Cracks from a point, drawn quickly.
    cx, cy = 1380, 300
    rng = random.Random(6405)
    for k in range(7):
        ang = k * 51 + rng.uniform(-12, 12)
        ln = rng.uniform(260, 520)
        p2 = (cx + ln * math.cos(math.radians(ang)), cy + ln * math.sin(math.radians(ang)))
        pin_string(t, (cx, cy), p2, 0.5, 5.5, colour="#FFFFFF", width=rng.uniform(2, 5), draw=0.25)
    label(t, t.track("text", "Derrota"), "DERROTA", 0.6, 5.4, Box(0, 330, 1920, 300), "Black Ops One", 250, "#EF4444",
          weight=400, spacing=10, layers=[shadow("#000000", 0, 12, 0, 0.9), stroke(8, "#1A0000"), fill("#EF4444")],
          anim_in=tanim("glitch-in", duration=0.5), anim_loop=tanim("flicker", intensity=0.25, speed=6), name="Título")
    label(t, t.track("text", "Sub"), "esta vez no fue…", 1.2, 4.8, Box(0, 630, 1920, 90), "Exo 2", 54, "#FCA5A5",
          weight=600, italic=True, anim_in=tanim("fade", duration=0.5), name="Subtítulo")
    label(t, t.track("text", "Revancha"), "REVANCHA EN", 2.4, 3.6, Box(560, 780, 560, 100), "Russo One", 52, "#FFFFFF",
          weight=400, align="right", anim_in=tanim("fade", duration=0.3), name="Revancha")
    for i, n in enumerate(["3", "2", "1"]):
        label(t, t.track("text", "Cuenta"), n, 2.6 + i, 1.0, Box(1150, 760, 200, 140), "Russo One", 120, "#EF4444",
              weight=400, align="left", editable=False, anim_in=tanim("pop", duration=0.2),
              anim_out=tanim("fade", duration=0.15))
    t.adjust([effect("stylize.vhs", noise=22, chroma=4, saturation=0.9),
              effect("digital_glitch", intensity=0.35, frequency=0.25, rgbAmount=10,
                     animated={"intensity": keys([(0, 0.9), (0.7, 0.15)])}),
              effect("stylize.vignette", amount=0.7)], name="Glitch")
    music(t, "behind-enemy-lines", 2, 0.8)
    return t


def game_marcador():
    t = _t(wide, "yt-game-marcador", "Marcador de equipos", "Team scoreboard", 6,
           GAME + ["marcador", "equipos", "scoreboard", "competitivo"], 8.0, thumb_at=4.9, background="#000000")
    gameplay(t, "y6-h-play-04", s1=1.05)
    shade_top(t, 300, 0.65)
    move = [(0, {"dy": -220}, "out"), (0.5, {})]
    t.solid(t.track("shape", "Local"), "#2563EB", 0.2, 7.8, Box(420, 34, 520, 96), move, kind="parallelogram",
            layers=[shadow("#000000", 0, 8, 20, 0.5), gradient([(0, "#1D4ED8"), (1, "#3B82F6")], angle=0), no_stroke()])
    t.solid(t.track("shape", "Visita"), "#DC2626", 0.2, 7.8, Box(980, 34, 520, 96), move, kind="parallelogram",
            layers=[shadow("#000000", 0, 8, 20, 0.5), gradient([(0, "#F87171"), (1, "#B91C1C")], angle=0), no_stroke()],
            flipH=True)
    t.solid(t.track("shape", "Centro"), "#0B0B0F", 0.2, 7.8, Box(830, 20, 260, 124), move, radius=14,
            kind="rounded-rectangle", layers=[shadow("#000000", 0, 8, 20, 0.6), fill("#0B0B0F"), stroke(3, "#FFFFFF", 0.7)])
    team = dict(font="Teko", size=66, colour="#FFFFFF", weight=600, spacing=4, motion=move)
    label(t, t.track("text", "Local"), "EQUIPO ALFA", 0.2, 7.8, Box(470, 34, 360, 96), **team, name="Equipo local")
    label(t, t.track("text", "Visita"), "EQUIPO NOVA", 0.2, 7.8, Box(1090, 34, 360, 96), **team, name="Equipo visitante")
    sc = lambda c="#FFFFFF", anim=None: (lambda: text_style("Teko", 104, [fill(c)], weight=700, anim_in=anim))  # noqa: E731
    la, lb = t.track("text", "Puntos local"), t.track("text", "Puntos visita")
    t.text(la, "2", 0.2, 3.8, Box(830, 20, 110, 124), sc()(), move, editable=False, name="Puntos")
    t.text(la, "3", 4.0, 4.0, Box(830, 20, 110, 124), sc("#60A5FA", tanim("pop", duration=0.3))(),
           label="Puntos local")
    t.text(lb, "1", 0.2, 7.8, Box(980, 20, 110, 124), sc()(), move, label="Puntos visita")
    label(t, t.track("text", "Guion"), ":", 0.2, 7.8, Box(915, 20, 90, 124), "Teko", 90, "#FFFFFF", weight=600,
          motion=move, editable=False)
    pill(t, t.track("shape", "Ronda"), "#FACC15", 0.5, 7.5, Box(840, 156, 240, 48), [(0, {"dy": -60}, "out"), (0.4, {})])
    label(t, t.track("text", "Ronda"), "RONDA 4", 0.5, 7.5, Box(840, 156, 240, 48), "Teko", 40, "#111111", weight=700,
          spacing=4, motion=[(0, {"dy": -60}, "out"), (0.4, {})], name="Ronda")
    # The point banner, through the middle.
    ban = Box(0, 470, 1920, 150)
    mo = [(0, {"dx": -1920}, "out"), (0.35, {}, "hold"), (1.9, {}, "in"), (2.2, {"dx": 1920})]
    t.solid(t.track("shape", "Banda"), "#2563EB", 3.9, 2.2, ban, mo,
            layers=[shadow("#000000", 0, 10, 26, 0.5), gradient([(0, "#1E3A8A", 0.0), (0.2, "#1D4ED8"), (0.8, "#1D4ED8"),
                                                                   (1, "#1E3A8A", 0.0)], angle=0), no_stroke()])
    label(t, t.track("text", "Banda"), "¡PUNTO PARA ALFA!", 3.95, 2.15, ban, "Russo One", 92, "#FFFFFF", weight=400,
          italic=True, motion=mo, layers=[shadow("#000000", 0, 6, 0, 0.6), fill("#FFFFFF")], name="Anuncio")
    flash(t, 4.0, 0.25, colour="#60A5FA", peak=0.4)
    music(t, "strength-of-the-titans", 2, 0.8)
    return t


def game_highlights():
    t = _t(wide, "yt-game-highlights", "Mejores jugadas", "Best plays highlight reel", 7,
           GAME + ["mejores jugadas", "highlights", "top", "momentos"], 10.5, thumb_at=1.4, background="#06060D")
    grid_bg(t, "#06060D", NEON_C, step=96, alpha=0.12, dur=2.3, drift=96)
    label(t, t.track("text", "Título"), "MEJORES\nJUGADAS", 0.15, 2.1, Box(0, 230, 1920, 470), "Audiowide", 190, "#FFFFFF",
          weight=400, line=1.0, layers=[glow(NEON_M, 34, 0.9), stroke(4, NEON_M), fill("#FFFFFF")],
          anim_in=tanim("glitch-in", duration=0.5), anim_out=tanim("fade-scale", duration=0.25), name="Título")
    label(t, t.track("text", "Semana"), "— DE LA SEMANA —", 0.4, 1.85, Box(0, 720, 1920, 80), "Orbitron", 48, NEON_C,
          weight=700, spacing=12, anim_in=tanim("fade", duration=0.4), anim_out=tanim("fade", duration=0.2),
          name="Subtítulo")
    clips = slides(t, ["y6-h-play-01", "y6-h-fantasy-02", "y6-h-fantasy-03", "y6-h-play-05"], 2.0, 2.0,
                   transition="rgb_displacement", tdur=0.3, kb_amount=0.1,
                   labels=["Jugada 4", "Jugada 3", "Jugada 2", "Jugada 1"])
    caps = ["Remontada imposible", "Salto de fe", "Por un pelo", "La jugada del año"]
    for i, n in enumerate(["#4", "#3", "#2", "#1"]):
        at = 2.0 + i * 2.0 + (0.15 if i else 0.0)
        d = 2.0 - 0.3 if i < 3 else 10.5 - at
        gold = i == 3
        label(t, t.track("text", "Número"), n, at, d, Box(50, 40, 300, 200), "Teko", 200, "#FACC15" if gold else "#FFFFFF",
              weight=700, align="left", editable=False,
              layers=[shadow("#000000", 0, 8, 0, 0.9), stroke(6, "#000000"), fill("#FACC15" if gold else "#FFFFFF")],
              anim_in=tanim("stamp", duration=0.2))
        label(t, t.track("text", "Pie"), caps[i], at + 0.1, d - 0.1, Box(60, 900, 1100, 110), "Russo One", 58, "#FFFFFF",
              weight=400, align="left", box_bg=(NEON_M if not gold else "#FACC15", 1.0), box_pad=18, box_radius=8,
              layers=[fill("#FFFFFF" if not gold else "#111111")], anim_in=tanim("skew-slide", duration=0.3),
              name=f"Pie {4 - i}")
    t.adjust([effect("strobe_flash", animated={"flash": spike([2.0, 4.0, 6.0, 8.0], 0.7, 0.25)}),
              effect("zoom_pulse", animated={"punch": spike([2.0, 4.0, 6.0, 8.0], 0.45, 0.3)})], name="Golpes")
    music(t, "action-strike", 20, 0.85)
    return t


def game_empezamos():
    t = _t(wide, "yt-game-empezamos", "Empezamos pronto", "Starting soon screen", 8,
           GAME + ["empezamos pronto", "starting soon", "pantalla de espera", "directo"], 12.0, thumb_at=6.2,
           background="#120724")
    t.photo(t.track("video", "Fondo"), "y6-h-play-04", 0, 12.0, t.full, kb(12.0, 1.1, 1.0), label="Fondo",
            effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=18)])
    t.solid(t.track("shape", "Tinte"), "#2E1065", 0, 12.0, layers=[gradient([(0, "#4C1D95", 0.82), (1, "#0F172A", 0.9)],
                                                                            angle=135), no_stroke()])
    dots(t, ["#A78BFA", NEON_C, "#F0ABFC"], 26, 0, 12.0, seed=6408, size=(6, 16), drift=160, alpha=0.8)
    # A turning ring.
    clip = t.solid(t.track("shape", "Anillo"), NEON_C, 0, 12.0, centered(960, 330, 230, 230), kind="ellipse",
                   layers=hollow_ring(NEON_C, 12, trim=0.7), rotation=keys([(0, 0), (12.0, 1440)]))
    t.solid(t.track("shape", "Anillo"), "#F0ABFC", 0, 12.0, centered(960, 330, 170, 170), kind="ellipse",
            layers=hollow_ring("#F0ABFC", 8, 0.8, trim=0.45), rotation=keys([(0, 360), (12.0, -720)]))
    label(t, t.track("text", "Mando"), "🎮", 0.2, 11.8, centered(960, 330, 160, 160), "Inter", 90, "#FFFFFF",
          editable=False, anim_loop=tanim("float", amount=0.1, speed=0.7))
    label(t, t.track("text", "Título"), "EMPEZAMOS PRONTO", 0.3, 11.7, Box(0, 480, 1920, 190), "Bungee", 140, "#FFFFFF",
          weight=400, layers=[shadow("#000000", 0, 10, 0, 0.5), glow("#A78BFA", 26, 0.7), fill("#FFFFFF")],
          anim_in=tanim("rise-by-word", duration=0.6, unit="word", stagger=0.15),
          anim_loop=tanim("breathe", amount=0.15, speed=0.4), name="Título")
    label(t, t.track("text", "Sub"), "ve por tus snacks, ya casi arrancamos 🍿", 0.8, 11.2, Box(0, 680, 1920, 80),
          "Exo 2", 48, "#E9D5FF", weight=600, anim_in=tanim("fade", duration=0.6), name="Subtítulo")
    # Loading bar over the whole wait.
    bar = Box(560, 810, 800, 26)
    t.solid(t.track("shape", "Carga"), "#FFFFFF", 0.5, 11.5, bar, radius=13, kind="rounded-rectangle", alpha=0.18)
    t.solid(t.track("shape", "Carga"), NEON_C, 0.5, 11.5, bar, curve_motion(lambda f: 0.04 + 0.96 * f, 11.0, bar.w),
            radius=13, kind="rounded-rectangle", layers=[glow(NEON_C, 14, 0.8),
                                                         gradient([(0, NEON_C), (1, "#A78BFA")], angle=0), no_stroke()])
    label(t, t.track("text", "Redes"), "@tucanal  ·  directo todos los viernes 20:00", 1.2, 10.8, Box(0, 930, 1920, 70),
          "Russo One", 36, "#FFFFFF", weight=400, spacing=2, anim_in=tanim("fade", duration=0.6), name="Redes")
    music(t, "arpent", 8, 0.7)
    return t


def game_vuelvo():
    t = _t(wide, "yt-game-vuelvo", "Vuelvo enseguida", "Be right back screen", 9,
           GAME + ["vuelvo enseguida", "be right back", "pausa", "brb"], 10.0, thumb_at=5.0, background="#0E1B2B")
    bg_gradient(t, [(0, "#0E1B2B"), (0.6, "#1F2A44"), (1, "#3B1E54")], angle=120)
    dots(t, ["#FDE68A", "#FFFFFF", "#93C5FD"], 30, 0, 10.0, seed=6409, size=(4, 10), kinds=("star",), drift=30,
         alpha=0.8)
    # Photo of the set, in a tilted card on the left.
    framed(t, "h-gaming-01", 0.2, 9.8, Box(140, 200, 700, 520), [(0, {"s": 0.9}, "out"), (0.6, {}, "linear"), (9.6, {"s": 1.02})],
           border=14, colour="#FDE68A", radius=10, rotation=rot(-3), label="Foto de tu set")
    label(t, t.track("text", "Taza"), "☕", 0.6, 9.4, centered(800, 740, 220, 220), "Inter", 150, "#FFFFFF",
          editable=False, motion=pop(0, 0.5), anim_loop=tanim("sway", angle=4, speed=0.5))
    for k in range(3):
        t.solid(t.track("shape", "Vapor"), "#FFFFFF", 0.9 + k * 0.5, 9.1 - k * 0.5, centered(770 + k * 30, 600, 14, 70),
                [(0, {"dy": 30}, "linear"), (9.1 - k * 0.5, {"dy": -60})], radius=7, kind="rounded-rectangle",
                opacity=keys([(0, 0.0), (0.8, 0.5, "smooth"), (1.6, 0.15, "smooth"), (2.4, 0.5, "smooth"),
                              (3.2, 0.15, "smooth"), (4.0, 0.5)]))
    label(t, t.track("text", "Título"), "VUELVO\nENSEGUIDA", 0.4, 9.6, Box(980, 220, 860, 380), "Righteous", 140,
          "#FDE68A", weight=400, line=1.0, align="left", layers=[shadow("#000000", 0, 8, 0, 0.4), fill("#FDE68A")],
          anim_in=tanim("bounce", duration=0.6, unit="line", stagger=0.15), name="Título")
    label(t, t.track("text", "Sub"), "no te vayas, solo voy por un café", 0.9, 9.1, Box(985, 610, 860, 70), "Exo 2", 44,
          "#E0E7FF", weight=600, align="left", anim_in=tanim("fade", duration=0.5), name="Subtítulo")
    # Chat bubbles that come up one by one.
    msgs = [("@Luna_22", "¡te esperamos! ✨"), ("@NoobMaster", "trae galletas 🍪"), ("@Kai", "aquí sigo 👀")]
    for i, (who, msg) in enumerate(msgs):
        at = 2.0 + i * 1.6
        y = 730 + i * 100
        mo = [(0, {"dy": 40}, "out"), (0.35, {})]
        rrect(t, t.track("shape", "Chat"), "#FFFFFF", at, 10.0 - at, Box(985, y, 720, 80), 40, motion=mo,
              layers=[fill("#FFFFFF", 0.12), stroke(2, "#FFFFFF", 0.25)], opacity=keys([(0, 0.0), (0.3, 1.0)]))
        label(t, t.track("text", "Chat"), f"{who}  {msg}", at, 10.0 - at, Box(1015, y, 680, 80), "Exo 2", 36, "#FFFFFF",
              weight=600, align="left", motion=mo, anim_in=tanim("fade", duration=0.3), name=f"Mensaje {i + 1}")
    music(t, "infinite-peace", 0, 0.7)
    return t


def game_killfeed():
    t = _t(wide, "yt-game-killfeed", "Racha de eliminaciones", "Kill-feed streak", 10,
           GAME + ["eliminaciones", "racha", "kill feed", "jugada"], 8.0, thumb_at=4.4, background="#000000")
    gameplay(t, "y6-h-fantasy-02", s1=1.08)
    shade_top(t, 340, 0.45)
    rows = [("TúJugador", "Rival_07"), ("TúJugador", "SombraX"), ("TúJugador", "ElCapi99")]
    for i, (a, b) in enumerate(rows):
        at = 0.8 + i * 1.1
        y = 40 + i * 76
        mo = [(0, {"dx": 640}, "out"), (0.3, {}, "hold"), (6.6 - at, {}, "in"), (7.0 - at, {"dx": 640})]
        t.solid(t.track("shape", "Fila"), "#000000", at, 7.0 - at, Box(1240, y, 640, 64), mo, radius=6,
                kind="rounded-rectangle", layers=[fill("#000000", 0.6), stroke(2, "#FACC15" if i == 2 else "#FFFFFF", 0.4)])
        label(t, t.track("text", "Fila"), a, at, 7.0 - at, Box(1260, y, 270, 64), "Russo One", 32, NEON_C, weight=400,
              align="right", motion=mo, name=f"Jugador {i + 1}")
        label(t, t.track("text", "Fila"), "✕", at, 7.0 - at, Box(1530, y, 70, 64), "Inter", 32, "#FFFFFF", weight=900,
              motion=mo, editable=False)
        label(t, t.track("text", "Fila"), b, at, 7.0 - at, Box(1600, y, 270, 64), "Russo One", 32, "#FCA5A5", weight=400,
              align="left", motion=mo, name=f"Rival {i + 1}")
    # Triple banner.
    at = 3.3
    slashes(t, ["#111111"], at, 690, angle=-6, h=60, dur=3.6)
    slashes(t, ["#FACC15"], at, 540, angle=-6, h=230, dur=3.6)
    label(t, t.track("text", "Racha"), "¡TRIPLE ELIMINACIÓN!", at + 0.1, 3.4, Box(0, 440, 1920, 200), "Russo One", 116,
          "#111111", weight=400, italic=True, layers=[fill("#111111")], rotation=rot(-6),
          anim_in=tanim("zoom-in", duration=0.3, **{"from": 220}), anim_out=tanim("fade", duration=0.2), name="Racha")
    label(t, t.track("text", "XP"), "+300 XP", at + 0.5, 3.0, Box(0, 760, 1920, 110), "Teko", 110, "#FACC15", weight=700,
          layers=[shadow("#000000", 0, 6, 0, 0.9), stroke(5, "#111111"), fill("#FACC15")],
          anim_in=tanim("pop", duration=0.3), anim_out=tanim("fade", duration=0.2), name="Puntos")
    flash(t, at, 0.25, colour="#FACC15", peak=0.45)
    t.adjust([effect("zoom_pulse", animated={"punch": spike([0.8, 1.9, 3.0, at], 0.3, 0.25)}),
              effect("beat_shake", animated={"amount": spike([at], 0.6, 0.35)})], name="Golpes")
    music(t, "experimental-test-subject", 30, 0.8)
    return t


def game_fin_stream():
    t = _t(wide, "yt-game-fin-stream", "Fin del directo", "Stream ending screen", 11,
           GAME + ["fin del directo", "pantalla final", "end screen", "gracias por ver"], 10.0, thumb_at=5.0,
           background="#0B0B12")
    grid_bg(t, "#0B0B12", "#7C3AED", step=120, alpha=0.14, drift=120)
    label(t, t.track("text", "Título"), "¡GRACIAS POR VER!", 0.2, 9.8, Box(0, 70, 1920, 170), "Bungee", 120, "#FFFFFF",
          weight=400, layers=[glow("#7C3AED", 24, 0.9), fill("#FFFFFF")], anim_in=tanim("drop", duration=0.6),
          name="Título")
    for i, (lab, s) in enumerate([("ÚLTIMO DIRECTO", "y6-h-play-03"), ("MEJORES MOMENTOS", "y6-h-fantasy-04")]):
        box = Box(150 + i * 880, 330, 740, 416)
        at = 0.5 + i * 0.2
        mo = [(0, {"dy": 160}, "out"), (0.5, {})]
        t.solid(t.track("shape", "Marco"), "#7C3AED", at, 10.0 - at, Box(box.x - 10, box.y - 10, box.w + 20, box.h + 20),
                mo, radius=16, kind="rounded-rectangle",
                layers=[glow("#7C3AED" if i == 0 else NEON_C, 26, 0.8), fill("#7C3AED" if i == 0 else NEON_C), no_stroke()],
                opacity=keys([(0, 0.0), (0.3, 1.0)]))
        t.photo(t.track("video", "Video"), s, at, 10.0 - at, box, mo, label=f"Video {i + 1}",
                opacity=keys([(0, 0.0), (0.3, 1.0)]))
        label(t, t.track("text", "Video"), lab, at + 0.3, 9.7 - at, Box(box.x, box.y + box.h + 20, box.w, 70), "Russo One",
              44, "#FFFFFF", weight=400, spacing=3, anim_in=tanim("fade", duration=0.4), name=f"Título video {i + 1}")
    pill(t, t.track("shape", "Botón"), "#FF1F4B", 1.4, 8.6, centered(960, 960, 520, 100), pop(0, 0.4))
    label(t, t.track("text", "Botón"), "SUSCRÍBETE 🔔", 1.4, 8.6, centered(960, 960, 520, 100), "Russo One", 48,
          "#FFFFFF", weight=400, anim_loop=tanim("pulse", amount=4, speed=1.2), name="Botón")
    label(t, t.track("text", "Próximo"), "Próximo directo: viernes 20:00", 1.8, 8.2, Box(1300, 930, 580, 60), "Exo 2", 34,
          "#C4B5FD", weight=600, align="right", anim_in=tanim("fade", duration=0.4), name="Próximo directo")
    music(t, "arpent", 30, 0.7)
    return t


def game_intro_pixel():
    t = _t(wide, "yt-game-intro-pixel", "Intro retro de 8 bits", "8-bit retro intro", 12,
           GAME + ["retro", "8 bits", "pixel", "intro", "arcade"], 6.0, thumb_at=3.6, background="#0D0221")
    bg(t, "#0D0221")
    rng = random.Random(6412)
    tr = t.track("shape", "Estrellas")
    for k in range(40):
        s = rng.choice([6, 6, 10, 14])
        at = rng.uniform(0, 1.5)
        if k % 10 == 9:
            tr = t.track("shape", "Estrellas")
        t.solid(tr, rng.choice(["#FFFFFF", "#F9C80E", "#43BCCD"]), at, 6.0 - at, centered(rng.uniform(0, 1920),
                                                                                          rng.uniform(0, 1080), s, s),
                opacity=blink(6.0 - at, rng.uniform(0.6, 1.4), 0.3))
    # Pixel ground: a row of blocks.
    for i in range(0, 1920, 80):
        if i % 640 == 0:
            tr = t.track("shape", "Suelo")
        t.solid(tr, "#2EC4B6" if (i // 80) % 2 else "#1B998B", 0.2 + i / 4000, 5.8 - i / 4000, Box(i, 960, 80, 120),
                [(0, {"dy": 140}, "out"), (0.3, {})])
    label(t, t.track("text", "Start"), "PULSA START", 0.2, 2.2, Box(0, 520, 1920, 100), "Press Start 2P", 56, "#FFFFFF",
          weight=400, editable=False, anim_loop=tanim("flicker", intensity=0.9, speed=3))
    t.photo(t.track("video", "Avatar"), "y6-gamer-05", 2.5, 3.5, centered(960, 330, 260, 260), pop(0, 0.35),
            label="Tu avatar o logo")
    outline(t, t.track("shape", "Avatar"), "#F9C80E", 12, 2.5, 3.5, centered(960, 330, 284, 284), pop(0, 0.35))
    label(t, t.track("text", "Canal"), "TU CANAL", 2.6, 3.4, Box(0, 500, 1920, 170), "Press Start 2P", 120, "#F9C80E",
          weight=400, layers=[shadow("#F72585", 10, 10, 0, 1.0), fill("#F9C80E")],
          anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name="Canal")
    label(t, t.track("text", "Nivel"), "NIVEL 1 · ¡A JUGAR!", 3.3, 2.7, Box(0, 720, 1920, 80), "Press Start 2P", 40,
          "#43BCCD", weight=400, anim_in=tanim("fade", duration=0.3), name="Lema")
    # Coins that hop.
    for k in range(5):
        x = 560 + k * 200
        at = 3.6 + k * 0.12
        t.solid(t.track("shape", "Moneda"), "#F9C80E", at, 6.0 - at, centered(x, 880, 46, 60),
                [(0, {"dy": 0}, "out"), (0.25, {"dy": -90}, "in"), (0.5, {})], kind="ellipse",
                layers=[fill("#F9C80E"), stroke(5, "#B8860B")])
    flash(t, 2.5, 0.2, peak=0.8)
    t.adjust([effect("stylize.vhs", noise=12, chroma=2, saturation=1.1), grain_eff(0.12)], name="Retro")
    music(t, "bit-bit-loop", 0, 0.8)
    return t


def grain_eff(amount: float):
    return effect("stylize.film_grain", amount=amount, grainSize=1.6)


def game_facecam_vertical():
    t = _t(tall, "yt-game-facecam-vertical", "Short de gaming con cámara", "Gaming short with face-cam", 13,
           GAME + ["short", "vertical", "reacción", "facecam"], 10.0, thumb_at=2.6, background="#05050A")
    gameplay(t, "y6-h-play-02", box=Box(0, 0, 1080, 1120), s1=1.08)
    t.photo(t.track("video", "Cámara"), "y6-gamer-01", 0, 10.0, Box(0, 1120, 1080, 800), kb(10.0, 1.04, 1.0),
            label="Tu cámara")
    t.solid(t.track("shape", "Divisor"), NEON_M, 0, 10.0, Box(0, 1110, 1080, 20),
            layers=[glow(NEON_M, 24, 0.9), gradient([(0, NEON_M), (1, NEON_C)], angle=0), no_stroke()])
    pill(t, t.track("shape", "Canal"), "#000000", 0.3, 9.7, Box(40, 50, 340, 70), alpha=0.65)
    label(t, t.track("text", "Canal"), "@TuCanal", 0.3, 9.7, Box(40, 50, 340, 70), "Russo One", 36, "#FFFFFF",
          weight=400, name="Canal")
    for i, (txt, at, d, c) in enumerate([("NO LO PUEDO CREER 😱", 0.4, 3.6, "#FACC15"),
                                         ("¿CÓMO HICE ESO?", 4.4, 2.8, NEON_C), ("¡SÍIII! 🔥", 7.4, 2.6, NEON_M)]):
        label(t, t.track("text", "Pie"), txt, at, d, Box(60, 960, 960, 300), "Luckiest Guy", 96, "#FFFFFF", weight=400,
              line=1.0, layers=[shadow("#000000", 0, 10, 0, 1.0), stroke(12, "#000000"), fill(c)],
              anim_in=tanim("pop", duration=0.25, unit="word", stagger=0.08), anim_out=tanim("fade", duration=0.15),
              rotation=rot(-3 if i % 2 == 0 else 3), name=f"Pie {i + 1}")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([0.4, 4.4, 7.4], 0.4, 0.3)})], name="Golpes")
    music(t, "funky-energy-loop", 40, 0.75)
    return t


def game_clip_viral():
    t = _t(tall, "yt-game-clip-viral", "Clip vertical de partida", "Vertical gameplay clip", 14,
           GAME + ["clip", "short", "vertical", "viral"], 8.0, thumb_at=3.2, background="#000000")
    first = gameplay(t, "y6-h-play-05", s1=1.12, effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=30),
                                                          effect("color.basic", exposure=-0.35)])
    gameplay(t, "", box=Box(0, 650, 1080, 608), reuse=first["placeholderId"], s1=1.05)
    outline(t, t.track("shape", "Marco"), "#FFFFFF", 6, 0, 8.0, Box(0, 647, 1080, 614), alpha=0.9)
    label(t, t.track("text", "Título"), "¿CÓMO SOBREVIVÍ A ESTO?", 0.2, 7.8, Box(50, 180, 980, 400), "Luckiest Guy", 124,
          "#FFFFFF", weight=400, line=1.0, layers=[shadow("#000000", 0, 10, 0, 1.0), stroke(12, "#000000"), fill("#FFFFFF")],
          anim_in=tanim("pop", duration=0.3, unit="word", stagger=0.1), name="Título")
    circle_photo(t, "y6-gamer-02", 0.6, 7.4, centered(540, 1540, 380, 380), pop(0, 0.4), ring_colour="#FACC15",
                 ring_width=12, label="Tu cara")
    label(t, t.track("text", "Parte"), "PARTE 1", 1.0, 7.0, centered(540, 1790, 300, 80), "Russo One", 44, "#111111",
          weight=400, box_bg=("#FACC15", 1.0), box_pad=14, box_radius=40, anim_in=tanim("pop", duration=0.3), name="Parte")
    music(t, "behind-enemy-lines", 20, 0.8)
    return t


def game_mvp():
    t = _t(wide, "yt-game-mvp", "Jugador MVP", "MVP player card", 15,
           GAME + ["mvp", "jugador de la semana", "estadísticas", "player card"], 7.0, thumb_at=3.8,
           background="#0A0A0A")
    bg_gradient(t, [(0, "#0A0A0A"), (1, "#1C1917")], angle=135)
    t.solid(t.track("shape", "Franja"), "#F59E0B", 0.1, 6.9, Box(80, 0, 760, 1080), [(0, {"dx": -900}, "out"), (0.5, {})],
            kind="parallelogram", layers=[gradient([(0, "#F59E0B"), (1, "#B45309")], angle=90), no_stroke()])
    t.photo(t.track("video", "Jugador"), "y6-gamer-05", 0.3, 6.7, Box(170, 130, 600, 820),
            [(0, {"dx": -700}, "out"), (0.5, {}, "linear"), (6.7, {"s": 1.03})], label="Foto del jugador")
    outline(t, t.track("shape", "Marco"), "#FFFFFF", 6, 0.3, 6.7, Box(170, 130, 600, 820),
            [(0, {"dx": -700}, "out"), (0.5, {}, "linear"), (6.7, {"s": 1.03})])
    label(t, t.track("text", "MVP"), "MVP", 0.6, 6.4, Box(900, 90, 900, 330), "Bungee", 300, "#F59E0B", weight=400,
          align="left", layers=[shadow("#000000", 0, 12, 0, 0.6), gradient([(0, "#FDE68A"), (1, "#F59E0B")], angle=90)],
          anim_in=tanim("slide-left", duration=0.45, distance=0.3), name="MVP")
    label(t, t.track("text", "Nombre"), "JUGADORPRO", 0.9, 6.1, Box(910, 420, 900, 100), "Russo One", 80, "#FFFFFF",
          weight=400, align="left", spacing=4, anim_in=tanim("fade", duration=0.4), name="Nombre")
    label(t, t.track("text", "Semana"), "JUGADOR DE LA SEMANA", 1.1, 5.9, Box(910, 520, 900, 60), "Exo 2", 38, "#F59E0B",
          weight=800, align="left", spacing=8, anim_in=tanim("fade", duration=0.4), name="Subtítulo")
    for i, (k, v, f) in enumerate([("ELIMINACIONES", "48", 0.92), ("ASISTENCIAS", "31", 0.7), ("OBJETIVOS", "12", 0.45)]):
        at = 1.5 + i * 0.25
        y = 640 + i * 120
        label(t, t.track("text", "Dato"), k, at, 7.0 - at, Box(910, y, 500, 50), "Exo 2", 34, "#D6D3D1", weight=700,
              align="left", anim_in=tanim("fade", duration=0.3), name=f"Dato {i + 1}")
        label(t, t.track("text", "Dato"), v, at, 7.0 - at, Box(1560, y - 6, 240, 60), "Russo One", 50, "#FFFFFF",
              weight=400, align="right", anim_in=tanim("pop", duration=0.3), name=f"Valor {i + 1}")
        t.solid(t.track("shape", "Barra"), "#FFFFFF", at, 7.0 - at, Box(910, y + 58, 890, 14), radius=7,
                kind="rounded-rectangle", alpha=0.15)
        t.solid(t.track("shape", "Barra"), "#F59E0B", at + 0.1, 6.9 - at, Box(910, y + 58, 890 * f, 14),
                [(0, {"sx": 0.0, "dx": -890 * f / 2}, "out"), (0.9, {})], radius=7, kind="rounded-rectangle")
    music(t, "honor-bound", 12, 0.8)
    return t


def game_torneo():
    t = _t(wide, "yt-game-torneo", "Torneo semanal", "Weekly tournament bracket", 16,
           GAME + ["torneo", "llaves", "bracket", "competencia"], 9.0, thumb_at=6.4, background="#020617")
    gameplay(t, "y6-h-fantasy-04", s1=1.05, effects=[effect("color.basic", exposure=-0.3, saturation=-0.3)])
    shade_full(t, 0.6, colour="#020617")
    label(t, t.track("text", "Título"), "TORNEO SEMANAL", 0.2, 8.8, Box(0, 40, 1920, 140), "Black Ops One", 110, "#FFFFFF",
          weight=400, spacing=6, layers=[glow("#38BDF8", 20, 0.8), fill("#FFFFFF")],
          anim_in=tanim("wipe", duration=0.6, angle=0), name="Título")
    teams = ["EQUIPO ALFA", "LOS LOBOS", "NOVA", "TITANES"]
    c1, c2, c3 = 160, 760, 1360
    ys = [280, 440, 640, 800]
    bw, bh = 420, 100

    def team_box(x, y, name, at, win=False, nm=None):
        c = "#FACC15" if win else "#38BDF8"
        t.solid(t.track("shape", "Equipo"), "#0F172A", at, 9.0 - at, Box(x, y - bh / 2, bw, bh), slide_in(dx=-80, length=0.35),
                radius=12, kind="rounded-rectangle", layers=[fill("#0F172A", 0.92), stroke(4, c)],
                opacity=keys([(0, 0.0), (0.25, 1.0)]))
        label(t, t.track("text", "Equipo"), name, at, 9.0 - at, Box(x, y - bh / 2, bw, bh), "Russo One", 42,
              "#FFFFFF" if not win else "#FACC15", weight=400, motion=slide_in(dx=-80, length=0.35), name=nm or name)

    for i, n in enumerate(teams):
        team_box(c1, ys[i], n, 0.6 + i * 0.15, nm=f"Equipo {i + 1}")
    semis = [(ys[0] + ys[1]) / 2, (ys[2] + ys[3]) / 2]
    for k in range(2):
        a, b, m = ys[2 * k], ys[2 * k + 1], semis[k]
        at = 1.6 + k * 0.3
        for y in (a, b):
            pin_string(t, (c1 + bw, y), (c1 + bw + 90, y), at, colour="#38BDF8", width=4, draw=0.2)
        pin_string(t, (c1 + bw + 90, a), (c1 + bw + 90, b), at + 0.2, colour="#38BDF8", width=4, draw=0.25)
        pin_string(t, (c1 + bw + 90, m), (c2, m), at + 0.4, colour="#38BDF8", width=4, draw=0.2)
    team_box(c2, semis[0], "EQUIPO ALFA", 2.6, nm="Semifinal 1")
    team_box(c2, semis[1], "TITANES", 2.8, nm="Semifinal 2")
    fy = (semis[0] + semis[1]) / 2
    for y in semis:
        pin_string(t, (c2 + bw, y), (c2 + bw + 90, y), 3.4, colour="#FACC15", width=4, draw=0.2)
    pin_string(t, (c2 + bw + 90, semis[0]), (c2 + bw + 90, semis[1]), 3.6, colour="#FACC15", width=4, draw=0.3)
    pin_string(t, (c2 + bw + 90, fy), (c3, fy), 3.9, colour="#FACC15", width=4, draw=0.2)
    team_box(c3, fy, "¿CAMPEÓN?", 4.2, win=True, nm="Final")
    label(t, t.track("text", "Copa"), "🏆", 4.4, 4.6, centered(c3 + bw / 2, fy - 150, 160, 160), "Inter", 110, "#FACC15",
          editable=False, motion=pop(0, 0.45), anim_loop=tanim("float", amount=0.1, speed=0.6))
    t.solid(t.track("shape", "Pie"), "#FACC15", 5.0, 4.0, Box(0, 960, 1920, 80), slide_in(dy=90, length=0.4))
    label(t, t.track("text", "Pie"), "SÁBADO 18:00  ·  INSCRIPCIONES ABIERTAS  ·  LINK EN LA DESCRIPCIÓN", 5.1, 3.9,
          Box(0, 960, 1920, 80), "Russo One", 36, "#111111", weight=400, spacing=2,
          anim_in=tanim("fade", duration=0.3), name="Datos")
    music(t, "honor-bound", 30, 0.8)
    return t


def game_nivel():
    t = _t(tall, "yt-game-nivel", "¡Subí de nivel!", "Level up!", 17,
           GAME + ["nivel", "level up", "logro", "xp"], 6.0, thumb_at=3.4, background="#04130A")
    gameplay(t, "y6-h-fantasy-01", s1=1.1, effects=[effect("color.basic", exposure=-0.25)])
    shade_full(t, 0.45, colour="#04130A")
    rays(t, "#4ADE80", 2.2, 3.8, centered(540, 820, 1500, 1500), alpha=0.18, points=22, speed=12)
    label(t, t.track("text", "Arriba"), "¡SUBISTE DE NIVEL!", 0.3, 5.7, Box(40, 360, 1000, 140), "Russo One", 76,
          "#FFFFFF", weight=400, layers=[shadow("#000000", 0, 6, 0, 0.8), fill("#FFFFFF")],
          anim_in=tanim("slide-down", duration=0.4), name="Título")
    label(t, t.track("text", "Nivel"), "NIVEL", 0.5, 5.5, Box(0, 530, 1080, 100), "Orbitron", 70, "#4ADE80", weight=900,
          spacing=20, anim_in=tanim("fade", duration=0.4), name="Etiqueta")
    style = big("Orbitron", 300, "#FFFFFF", layers=[glow("#4ADE80", 30, 0.8), fill("#FFFFFF")])
    t.text(t.track("text", "Número"), "49", 0.5, 1.7, Box(0, 630, 1080, 360), style(), editable=False, name="Contando")
    t.text(t.track("text", "Número"), "50", 2.2, 3.8, Box(0, 630, 1080, 360),
           text_style("Orbitron", 300, [glow("#4ADE80", 40, 1.0), fill("#4ADE80")], weight=900,
                      anim_in=tanim("stamp", duration=0.3)), label="Nivel nuevo")
    bar = Box(140, 1080, 800, 44)
    t.solid(t.track("shape", "XP"), "#FFFFFF", 0.6, 5.4, bar, radius=22, kind="rounded-rectangle", alpha=0.2)
    t.solid(t.track("shape", "XP"), "#4ADE80", 0.7, 1.5, bar, [(0, {"sx": 0.55, "dx": -bar.w * 0.225}, "inout"), (1.45, {})],
            radius=22, kind="rounded-rectangle", layers=[glow("#4ADE80", 16, 0.8), fill("#4ADE80"), no_stroke()])
    t.solid(t.track("shape", "XP"), "#4ADE80", 2.2, 3.8, bar, [(0, {"sx": 0.02, "dx": -bar.w * 0.49}, "out"),
                                                               (1.2, {"sx": 0.2, "dx": -bar.w * 0.4})],
            radius=22, kind="rounded-rectangle", layers=[glow("#4ADE80", 16, 0.8), fill("#4ADE80"), no_stroke()])
    label(t, t.track("text", "XP"), "+1.500 XP", 2.4, 3.6, Box(0, 1150, 1080, 120), "Teko", 110, "#FACC15", weight=700,
          layers=[shadow("#000000", 0, 6, 0, 0.9), fill("#FACC15")], anim_in=tanim("rise", duration=0.35), name="XP")
    dots(t, ["#4ADE80", "#FACC15", "#FFFFFF"], 26, 2.2, 3.8, seed=6417, size=(14, 34), kinds=("star",), drift=260,
         area=Box(80, 500, 920, 800))
    flash(t, 2.2, 0.35, colour="#BBF7D0", peak=0.75)
    t.adjust([effect("zoom_pulse", animated={"punch": spike([2.2], 0.6, 0.4)})], name="Golpe")
    music(t, "new-hero-in-town", 10, 0.85)
    return t


GAMING = [game_overlay_neon, game_alerta_sub, game_alerta_vertical, game_gg, game_victoria, game_derrota, game_marcador,
          game_highlights, game_empezamos, game_vuelvo, game_killfeed, game_fin_stream, game_intro_pixel,
          game_facecam_vertical, game_clip_viral, game_mvp, game_torneo, game_nivel]


# =====================================================================================================
# 2. COCINA
# =====================================================================================================

def round_mask(t, track, clip, radius: float):
    """Rounded corners on a photo: a freeform mask traced around them (masks have no rounded rectangle)."""
    w = clip["width"]["keyframes"][0]["value"]
    h = clip["height"]["keyframes"][0]["value"]
    rx, ry, n = radius / w, radius / h, 8
    pts = []
    for cx, cy, a0 in ((1 - rx, ry, -90), (1 - rx, 1 - ry, 0), (rx, 1 - ry, 90), (rx, ry, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append([cx + rx * math.cos(a), cy + ry * math.sin(a)])
    t.mask(track, clip, "freeform", points=pts, smooth=False)


def rphoto(t, sample, t0, dur, box, radius=36, motion=None, label_=None, **extra):
    track = t.track("video", "Foto")
    clip = t.photo(track, sample, t0, dur, box, motion, label=label_, **extra)
    round_mask(t, track, clip, radius)
    return clip


CREAM, INK, TOMATO, BASIL = "#FFF8EE", "#2B2118", "#E4572E", "#2F6B3B"


def coc_ingredientes_lista():
    t = _t(tall, "yt-coc-ingredientes-lista", "Lista de ingredientes", "Ingredient checklist", 20,
           COC + ["ingredientes", "lista", "ingredients"], 12.0, thumb_at=9.2, background=CREAM)
    bg(t, CREAM)
    t.photo(t.track("video", "Foto"), "y6-flatlay-02", 0, 12.0, Box(0, 0, 1080, 980), kb(12.0, 1.0, 1.08),
            label="Ingredientes desde arriba")
    card = Box(50, 820, 980, 1040)
    t.solid(t.track("shape", "Tarjeta"), CREAM, 0.2, 11.8, card, [(0, {"dy": 900}, "out"), (0.7, {})], radius=44,
            kind="rounded-rectangle", layers=[shadow("#000000", 0, -8, 40, 0.25), fill(CREAM), no_stroke()])
    label(t, t.track("text", "Título"), "INGREDIENTES", 0.6, 11.4, Box(110, 870, 860, 110), "Lilita One", 96, TOMATO,
          weight=400, align="left", anim_in=tanim("rise", duration=0.4), name="Título")
    label(t, t.track("text", "Porciones"), "para 4 personas", 0.9, 11.1, Box(110, 975, 860, 70), "Caveat", 58, BASIL,
          weight=700, align="left", anim_in=tanim("fade", duration=0.4), name="Porciones")
    items = ["2 tazas de harina", "3 huevos", "1 taza de leche", "2 cdas. de azúcar", "1 pizca de sal", "Mantequilla al gusto"]
    for i, item in enumerate(items):
        at = 1.6 + i * 1.15
        y = 1080 + i * 122
        outline(t, t.track("shape", "Casilla"), INK, 5, at, 12.0 - at, Box(120, y + 22, 64, 64), pop(0, 0.3), radius=12,
                kind="rounded-rectangle")
        t.solid(t.track("shape", "Marca"), BASIL, at + 0.35, 11.65 - at, Box(120, y + 22, 64, 64), pop(0, 0.3),
                radius=12, kind="rounded-rectangle")
        label(t, t.track("text", "Marca"), "✓", at + 0.35, 11.65 - at, Box(120, y + 22, 64, 64), "Inter", 46, "#FFFFFF",
              weight=900, editable=False, motion=pop(0, 0.3))
        label(t, t.track("text", "Ingrediente"), item, at, 12.0 - at, Box(215, y, 800, 108), "Patrick Hand", 62, INK,
              weight=400, align="left", anim_in=tanim("slide-right", duration=0.35, distance=0.12),
              name=f"Ingrediente {i + 1}")
        if i < len(items) - 1:
            t.solid(t.track("shape", "Línea"), INK, at, 12.0 - at, Box(120, y + 116, 880, 2), alpha=0.12)
    music(t, "happy-whistling-ukulele", 2, 0.7)
    return t


def coc_ingredientes_flotan():
    t = _t(wide, "yt-coc-ingredientes-flotan", "Lo que necesitas", "What you need", 21,
           COC + ["ingredientes", "lo que necesitas", "ingredients"], 10.0, thumb_at=6.4, background="#E9EDE4")
    bg(t, "#E9EDE4")
    dots(t, ["#C8D5B9", "#F4D6CC"], 14, 0, 10.0, seed=6421, size=(40, 120), drift=40, alpha=0.6)
    label(t, t.track("text", "Título"), "Lo que necesitas", 0.2, 9.8, Box(0, 90, 1920, 180), "DM Serif Display", 130,
          "#3F5E4A", weight=400, anim_in=tanim("rise-by-word", duration=0.6, unit="word", stagger=0.12), name="Título")
    line(t, t.track("shape", "Línea"), "#C8553D", 0.7, 9.3, centered(960, 285, 260, 6), grow="c", length=0.5)
    items = [("Legumbres", "y6-flatlay-07"), ("Cebolla", "cooking-03"), ("Aceite y ajo", "y6-flatlay-05"),
             ("Tomates", "cooking-06"), ("Huevos", "y6-flatlay-08")]
    for i, (name, s) in enumerate(items):
        at = 1.0 + i * 0.9
        cx = 260 + i * 350
        cy = 600 + (30 if i % 2 else -30)
        mo = [(0, {"s": 0.0}, "back"), (0.5, {}, "linear"), (10.0 - at, {"dy": -16})]
        circle_photo(t, s, at, 10.0 - at, centered(cx, cy, 280, 280), mo, ring_colour="#FFFFFF", ring_width=12,
                     label=name)
        step_badge(t, str(i + 1), cx + 110, cy - 110, 76, at + 0.2, 9.8 - at, "#C8553D", "#FFFFFF", font="DM Serif Display",
                   size=46)
        label(t, t.track("text", "Nombre"), name, at + 0.25, 9.75 - at, Box(cx - 170, cy + 160, 340, 80), "Caveat", 64,
              "#3F5E4A", weight=700, anim_in=tanim("pop", duration=0.35), name=f"Ingrediente {i + 1}")
    label(t, t.track("text", "Pie"), "¡y nada más!", 6.0, 4.0, Box(0, 930, 1920, 90), "Caveat", 70, "#C8553D", weight=700,
          anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name="Pie")
    music(t, "groovin", 6, 0.7)
    return t


def coc_pasos():
    t = _t(tall, "yt-coc-pasos", "Receta paso a paso", "Step-by-step recipe", 22,
           COC + ["pasos", "paso a paso", "steps", "tutorial"], 15.0, thumb_at=5.4, background="#111111")
    steps = ["Pica la cebolla y el ajo", "Sofríe 5 minutos a fuego medio", "Agrega el tomate y la albahaca",
             "Sirve con queso rallado"]
    samples = ["y6-hands-01", "y6-hands-03", "y6-hands-02", "y6-dish-04"]
    each = 15.0 / 4
    slides(t, samples, 0.0, each, transition="slide_left", tdur=0.35, kb_amount=0.07,
           labels=[f"Paso {i + 1}" for i in range(4)])
    shade_bottom(t, 700, 0.55)
    for i in range(4):
        x = 300 + i * 140
        t.solid(t.track("shape", "Progreso"), "#FFFFFF", 0, 15.0, Box(x, 80, 100, 12), radius=6, kind="rounded-rectangle",
                alpha=0.35)
        t.solid(t.track("shape", "Progreso"), "#FFD166", i * each, 15.0 - i * each, Box(x, 80, 100, 12),
                [(0, {"sx": 0.0, "dx": -50}, "linear"), (each, {})], radius=6, kind="rounded-rectangle")
    label(t, t.track("text", "Gancho"), "PASO A PASO", 0.1, each - 0.3, Box(60, 150, 960, 140), "Lilita One", 110,
          "#FFFFFF", weight=400, layers=[shadow("#000000", 0, 6, 18, 0.6), fill("#FFFFFF")],
          anim_in=tanim("pop", duration=0.35), anim_out=tanim("fade", duration=0.2), name="Título")
    for i, st in enumerate(steps):
        at = i * each + 0.25
        d = each - 0.45 if i < 3 else 15.0 - at
        card = Box(60, 1420, 960, 330)
        mo = [(0, {"dy": 420}, "out"), (0.45, {})]
        t.solid(t.track("shape", "Tarjeta"), "#FFFFFF", at, d, card, mo, radius=40, kind="rounded-rectangle",
                layers=[shadow("#000000", 0, 12, 30, 0.35), fill("#FFFFFF"), no_stroke()])
        step_badge(t, str(i + 1), 190, 1420, 150, at + 0.2, d - 0.2, "#FFD166", INK, size=96, ring_c="#FFFFFF")
        label(t, t.track("text", "Paso"), f"PASO {i + 1}", at + 0.25, d - 0.25, Box(300, 1440, 680, 70), "Lilita One", 46,
              TOMATO, weight=400, align="left", anim_in=tanim("fade", duration=0.3), editable=False)
        label(t, t.track("text", "Paso"), st, at + 0.3, d - 0.3, Box(110, 1520, 880, 210), "Poppins", 62, INK, weight=700,
              align="left", line=1.12, anim_in=tanim("rise-by-word", duration=0.35, unit="word", stagger=0.05),
              name=f"Paso {i + 1}")
    music(t, "bebop-for-joey", 6, 0.7)
    return t


def coc_pasos_wide():
    t = _t(wide, "yt-coc-pasos-wide", "Pasos con video y ficha", "Steps with video and card", 23,
           COC + ["pasos", "tutorial", "steps", "horizontal"], 15.0, thumb_at=5.6, background="#F7F1E8")
    bg(t, "#F7F1E8")
    each = 15.0 / 4
    slides(t, ["y6-h-hands-03", "y6-h-hands-02", "y6-h-hands-04", "y6-h-dish-05"], 0.0, each,
           box=Box(0, 0, 1180, 1080), transition="crossfade", tdur=0.4, kb_amount=0.06,
           labels=[f"Video paso {i + 1}" for i in range(4)])
    t.solid(t.track("shape", "Borde"), "#C8553D", 0, 15.0, Box(1180, 0, 14, 1080))
    steps = [("Bate los huevos con sal", "2 min"), ("Calienta la sartén con aceite", "1 min"),
             ("Vierte y mueve con espátula", "3 min"), ("Sirve caliente", "¡listo!")]
    for i, (st, tm) in enumerate(steps):
        at = i * each + 0.2
        d = each - 0.35 if i < 3 else 15.0 - at
        x0 = 1260
        label(t, t.track("text", "De"), f"PASO {i + 1} DE 4", at, d, Box(x0, 120, 600, 60), "Montserrat", 34, "#8A6E5A",
              weight=700, spacing=6, align="left", anim_in=tanim("fade", duration=0.3),
              anim_out=tanim("fade", duration=0.2), editable=False)
        label(t, t.track("text", "Número"), f"0{i + 1}", at, d, Box(x0 - 10, 180, 600, 300), "DM Serif Display", 260,
              "#C8553D", weight=400, align="left", anim_in=tanim("slide-up", duration=0.4, distance=0.2),
              anim_out=tanim("fade", duration=0.2), editable=False)
        label(t, t.track("text", "Paso"), st, at + 0.15, d - 0.15, Box(x0, 500, 600, 260), "Montserrat", 60, INK,
              weight=800, align="left", line=1.12, anim_in=tanim("rise-by-word", duration=0.35, unit="word", stagger=0.06),
              anim_out=tanim("fade", duration=0.2), name=f"Paso {i + 1}")
        pill(t, t.track("shape", "Tiempo"), "#3F5E4A", at + 0.3, d - 0.3, Box(x0, 800, 260, 80), pop(0, 0.3))
        label(t, t.track("text", "Tiempo"), f"⏱ {tm}", at + 0.3, d - 0.3, Box(x0, 800, 260, 80), "Montserrat", 38,
              "#FFFFFF", weight=700, motion=pop(0, 0.3), name=f"Tiempo {i + 1}")
    music(t, "martini-sunset", 6, 0.7)
    return t


def coc_temporizador():
    t = _t(tall, "yt-coc-temporizador", "Temporizador de horno", "Oven timer", 24,
           COC + ["temporizador", "horno", "timer", "tiempo"], 10.0, thumb_at=4.6, background="#1A0F0A")
    t.photo(t.track("video", "Foto"), "y6-dish-02", 0, 10.0, t.full, kb(10.0, 1.12, 1.0), label="Foto del horno o plato",
            effects=[effect("builtin.effects.gaussian_blur", u_blurRadius=8)])
    shade_full(t, 0.55, colour="#1A0F0A")
    label(t, t.track("text", "Arriba"), "AL HORNO", 0.2, 9.8, Box(0, 330, 1080, 130), "Lilita One", 110, "#FFB703",
          weight=400, spacing=6, anim_in=tanim("drop", duration=0.5), name="Título")
    pill(t, t.track("shape", "Grados"), "#FFB703", 0.5, 9.5, centered(540, 520, 300, 84), pop(0, 0.35))
    label(t, t.track("text", "Grados"), "180 °C", 0.5, 9.5, centered(540, 520, 300, 84), "Lilita One", 52, "#1A0F0A",
          weight=400, motion=pop(0, 0.35), name="Temperatura")
    box = centered(540, 1000, 680, 680)
    t.solid(t.track("shape", "Pista"), "#000000", 0.4, 9.6, box, pop(0, 0.4), kind="ellipse", alpha=0.35)
    t.solid(t.track("shape", "Pista"), "#FFFFFF", 0.4, 9.6, box, pop(0, 0.4), kind="ellipse",
            layers=hollow_ring("#FFFFFF", 26, 0.18))
    clip = t.solid(t.track("shape", "Tiempo"), "#FFB703", 0.6, 9.4, box, kind="ellipse",
                   layers=hollow_ring("#FFB703", 26, trim=1.0), rotation=rot(-90))
    clip["shapeStyle"]["keyframes"] = {"layer.stroke.trimEnd": keys([(0, 1.0, "hold"), (0.4, 1.0, "inout"), (7.8, 0.0)])}
    count_fn(t, t.track("text", "Reloj"), lambda f: 25 * 60 * (1 - f) ** 1.3,
             lambda v: f"{int(v) // 60:02d}:{int(v) % 60:02d}", 1.0, 7.2, "00:00", centered(540, 1000, 600, 220),
             big("Lilita One", 170, "#FFFFFF", weight=400), step=2, end=8.2, name="Tiempo final")
    label(t, t.track("text", "Listo"), "¡LISTO!", 8.2, 1.8, centered(540, 1000, 640, 240), "Lilita One", 170, "#FFB703",
          weight=400, layers=[shadow("#000000", 0, 8, 20, 0.6), fill("#FFB703")], anim_in=tanim("stamp", duration=0.3),
          name="Listo")
    label(t, t.track("text", "Pie"), "hasta que esté dorado", 0.9, 9.1, Box(0, 1440, 1080, 100), "Caveat", 76, "#FFFFFF",
          weight=700, anim_in=tanim("fade", duration=0.5), name="Pie")
    flash(t, 8.2, 0.3, colour="#FFB703", peak=0.5)
    t.adjust([effect("zoom_pulse", animated={"punch": spike([8.2], 0.5, 0.35)})], name="Golpe")
    music(t, "frogs-legs-rag", 4, 0.7)
    return t


def coc_plato_final():
    t = _t(wide, "yt-coc-plato-final", "Revelación del plato final", "Final dish reveal", 25,
           COC + ["plato final", "resultado", "reveal", "y listo"], 8.0, thumb_at=4.0, background="#000000")
    t.photo(t.track("video", "Plato"), "y6-h-dish-04", 0.9, 7.1, t.full,
            [(0, {"s": 1.25}, "out"), (1.2, {"s": 1.04}, "linear"), (7.1, {"s": 1.0})], label="Tu plato final")
    shade_bottom(t, 380, 0.6, 0.9, 7.1)
    for side, colour in ((-1, "#C8553D"), (1, "#F2CC8F")):
        x = 0 if side < 0 else 960
        t.solid(t.track("shape", "Cortina"), colour, 0, 2.2, Box(x, 0, 960, 1080),
                [(0, {}, "hold"), (1.0, {}, "inout"), (1.8, {"dx": side * 1000})])
    label(t, t.track("text", "Antes"), "el resultado…", 0.15, 0.95, Box(0, 440, 1920, 200), "Caveat", 130, "#FFFFFF",
          weight=700, layers=[shadow("#000000", 0, 4, 14, 0.4), fill("#FFFFFF")],
          anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), editable=False)
    label(t, t.track("text", "Listo"), "¡Y LISTO!", 1.7, 6.3, Box(0, 330, 1920, 300), "Shrikhand", 210, "#FFFFFF", weight=400,
          layers=[shadow("#000000", 0, 10, 26, 0.5), fill("#FFFFFF")], anim_in=tanim("pop", duration=0.45),
          name="Título")
    pill(t, t.track("shape", "Nombre"), "#C8553D", 2.2, 5.8, centered(960, 880, 760, 110), pop(0, 0.4))
    label(t, t.track("text", "Nombre"), "Pasta al pomodoro", 2.2, 5.8, centered(960, 880, 760, 110), "DM Serif Display", 64,
          "#FFFFFF", weight=400, motion=pop(0, 0.4), name="Nombre del plato")
    dots(t, ["#FFFFFF", "#FFE8A3"], 20, 1.8, 6.2, seed=6425, size=(14, 30), kinds=("star",), drift=80,
         area=Box(200, 200, 1520, 600))
    t.adjust([effect("bling_sparkle", intensity=0.5, threshold=0.75, density=0.3)], t0=1.8, name="Brillos")
    music(t, "fake-it-til-you-fake-it", 6, 0.75)
    return t


def coc_receta_card():
    t = _t(wide, "yt-coc-receta-card", "Ficha de receta", "Recipe card", 26,
           COC + ["ficha", "porciones", "tiempo", "recipe card"], 10.0, thumb_at=6.8, background="#FBF6EE")
    bg(t, "#FBF6EE")
    t.photo(t.track("video", "Foto"), "y6-h-dish-01", 0, 10.0, Box(0, 0, 880, 1080),
            [(0, {"dx": -300}, "out"), (0.7, {}, "linear"), (10.0, {"s": 1.05})], label="Foto del plato")
    t.solid(t.track("shape", "Borde"), "#B5651D", 0.2, 9.8, Box(880, 0, 10, 1080), [(0, {"sy": 0.0}, "out"), (0.6, {})])
    x0 = 980
    label(t, t.track("text", "Tipo"), "RECETA DE LA SEMANA", 0.5, 9.5, Box(x0, 80, 860, 50), "Montserrat", 30, "#B5651D",
          weight=800, spacing=8, align="left", anim_in=tanim("fade", duration=0.4), name="Etiqueta")
    label(t, t.track("text", "Título"), "Lasaña de verduras", 0.7, 9.3, Box(x0, 130, 880, 240), "Playfair Display", 100,
          INK, weight=800, align="left", line=1.0, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.1),
          name="Título")
    chips = [("⏱", "45 min", "TIEMPO"), ("🍽", "6", "PORCIONES"), ("🔥", "Media", "DIFICULTAD")]
    for i, (ic, v, k) in enumerate(chips):
        at = 1.4 + i * 0.25
        x = x0 + i * 290
        rrect(t, t.track("shape", "Dato"), "#F1E3CF", at, 10.0 - at, Box(x, 410, 260, 160), 22, motion=pop(0, 0.35))
        label(t, t.track("text", "Dato"), f"{ic} {v}", at, 10.0 - at, Box(x, 425, 260, 80), "Montserrat", 46, INK,
              weight=800, motion=pop(0, 0.35), name=k.capitalize())
        label(t, t.track("text", "Dato"), k, at, 10.0 - at, Box(x, 500, 260, 50), "Montserrat", 24, "#8A6E5A", weight=700,
              spacing=3, motion=pop(0, 0.35), editable=False)
    label(t, t.track("text", "Ingredientes"), "INGREDIENTES", 2.3, 7.7, Box(x0, 620, 860, 50), "Montserrat", 32, "#B5651D",
          weight=800, spacing=6, align="left", anim_in=tanim("fade", duration=0.4), editable=False)
    items = ["Láminas de lasaña", "2 calabacines", "1 berenjena", "Salsa de tomate", "Queso mozzarella", "Albahaca fresca"]
    for i, it in enumerate(items):
        at = 2.6 + i * 0.3
        x = x0 + (i % 2) * 440
        y = 690 + (i // 2) * 90
        t.solid(t.track("shape", "Punto"), "#B5651D", at, 10.0 - at, centered(x + 12, y + 40, 14, 14), pop(0, 0.3),
                kind="ellipse")
        label(t, t.track("text", "Ingrediente"), it, at, 10.0 - at, Box(x + 36, y, 400, 80), "Montserrat", 36, INK,
              weight=500, align="left", anim_in=tanim("slide-right", duration=0.3, distance=0.1),
              name=f"Ingrediente {i + 1}")
    music(t, "martini-sunset", 40, 0.7)
    return t


def coc_receta_vertical():
    t = _t(tall, "yt-coc-receta-vertical", "Tarjeta de receta vertical", "Vertical recipe card", 27,
           COC + ["ficha", "saludable", "recipe card", "guardar"], 10.0, thumb_at=5.8, background="#F1FFE7")
    bg(t, "#F1FFE7")
    t.photo(t.track("video", "Foto"), "y6-dish-05", 0, 10.0, Box(0, 0, 1080, 1060), kb(10.0, 1.08, 1.0),
            label="Foto del plato")
    card = Box(40, 900, 1000, 980)
    t.solid(t.track("shape", "Tarjeta"), "#FFFFFF", 0.3, 9.7, card, [(0, {"dy": 900}, "out"), (0.7, {})], radius=56,
            kind="rounded-rectangle", layers=[shadow("#14532D", 0, -6, 40, 0.25), fill("#FFFFFF"), no_stroke()])
    pill(t, t.track("shape", "Etiqueta"), "#84CC16", 0.9, 9.1, Box(100, 960, 330, 70), pop(0, 0.35))
    label(t, t.track("text", "Etiqueta"), "SALUDABLE", 0.9, 9.1, Box(100, 960, 330, 70), "Montserrat", 32, "#14532D",
          weight=800, spacing=4, motion=pop(0, 0.35), name="Etiqueta")
    label(t, t.track("text", "Título"), "Berenjena asada con yogur", 1.0, 9.0, Box(100, 1050, 880, 270), "DM Serif Display",
          108, "#14532D", weight=400, align="left", line=1.0,
          anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.1), name="Título")
    chips = [("⏱", "30 min"), ("🍽", "2 porc."), ("🌱", "Vegana")]
    for i, (ic, v) in enumerate(chips):
        at = 1.8 + i * 0.25
        cx = 230 + i * 310
        t.solid(t.track("shape", "Dato"), "#ECFCCB", at, 10.0 - at, centered(cx, 1440, 150, 150), pop(0, 0.35),
                kind="ellipse")
        label(t, t.track("text", "Icono"), ic, at, 10.0 - at, centered(cx, 1440, 150, 150), "Inter", 70, "#14532D",
              editable=False, motion=pop(0, 0.35))
        label(t, t.track("text", "Dato"), v, at + 0.1, 9.9 - at, Box(cx - 150, 1530, 300, 70), "Montserrat", 42, "#14532D",
              weight=700, anim_in=tanim("fade", duration=0.3), name=f"Dato {i + 1}")
    label(t, t.track("text", "Guardar"), "Guárdala para después 🔖", 3.0, 7.0, Box(100, 1680, 880, 100), "Caveat", 72,
          "#65A30D", weight=700, anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name="Llamada")
    music(t, "adding-the-sun", 6, 0.7)
    return t


def coc_cenital():
    t = _t(wide, "yt-coc-cenital", "Tres platos desde arriba", "Three plates from above", 28,
           COC + ["desde arriba", "top down", "ideas", "comidas"], 12.0, thumb_at=7.0, background="#6B4226")
    bg_gradient(t, [(0, "#7A4B2A"), (0.5, "#6B4226"), (1, "#563318")], angle=100)
    rng = random.Random(6428)
    tr = t.track("shape", "Vetas")
    for k in range(9):
        y = 60 + k * 120 + rng.uniform(-20, 20)
        t.solid(tr, "#3E2511", 0, 12.0, Box(0, y, 1920, rng.uniform(2, 5)), alpha=0.35)
    label(t, t.track("text", "Título"), "3 comidas fáciles", 0.2, 11.8, Box(0, 40, 1920, 170), "Amatic SC", 150, "#FFF4E0",
          weight=700, layers=[shadow("#000000", 0, 6, 14, 0.4), fill("#FFF4E0")],
          anim_in=tanim("wipe", duration=0.7, angle=0), name="Título")
    meals = [("DESAYUNO", "Tostadas con palta", "y6-dish-03"), ("ALMUERZO", "Ensalada tibia", "y6-h-dish-05"),
             ("CENA", "Pasta cremosa", "y6-h-dish-02")]
    for i, (k, v, s) in enumerate(meals):
        at = 0.8 + i * 1.6
        cx = 360 + i * 600
        cy = 560
        mo = [(0, {"dy": -900, "s": 1.2}, "out"), (0.6, {}, "linear"), (12.0 - at, {"s": 1.03})]
        t.solid(t.track("shape", "Plato"), "#FFFFFF", at, 12.0 - at, centered(cx, cy, 470, 470), mo, kind="ellipse",
                layers=[shadow("#000000", 0, 18, 30, 0.45), fill("#F7F5F0"), stroke(2, "#DDD6CA")])
        circle_photo(t, s, at, 12.0 - at, centered(cx, cy, 380, 380), mo, label=f"Plato {i + 1}")
        label(t, t.track("text", "Comida"), k, at + 0.5, 11.5 - at, Box(cx - 260, 820, 520, 90), "Amatic SC", 84, "#FFD166",
              weight=700, anim_in=tanim("fade", duration=0.4), name=f"Comida {i + 1}")
        label(t, t.track("text", "Plato"), v, at + 0.7, 11.3 - at, Box(cx - 300, 910, 600, 90), "Caveat", 66, "#FFF4E0",
              weight=700, anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name=f"Plato {i + 1}")
    t.adjust([effect("stylize.vignette", amount=0.3, softness=1.0)], name="Viñeta")
    music(t, "hillbilly-swing", 6, 0.65)
    return t


def coc_intro_canal():
    t = _t(wide, "yt-coc-intro-canal", "Intro de canal de cocina", "Cooking channel intro", 29,
           COC + ["intro", "canal", "presentación", "channel intro"], 6.0, thumb_at=3.4, background="#FFF3E2")
    bg(t, "#FFF3E2")
    track = t.track("video", "Cocinero")
    clip = t.photo(track, "y6-h-cook-01", 0, 6.0, Box(760, 0, 1160, 1080),
                   [(0, {"dx": 900}, "out"), (0.7, {}, "linear"), (6.0, {"s": 1.04})], label="Tu foto cocinando")
    t.mask(track, clip, "freeform", points=[[0.2, 0], [1, 0], [1, 1], [0, 1]], smooth=False)
    label(t, t.track("text", "Saludo"), "bienvenidos a", 0.6, 5.4, Box(100, 250, 780, 90), "Caveat", 80, TOMATO, weight=700,
          align="left", anim_in=tanim("fade", duration=0.4), name="Saludo")
    label(t, t.track("text", "Canal"), "La Cocina\nde Sofía", 0.9, 5.1, Box(100, 340, 820, 360), "Pacifico", 130, INK,
          weight=400, align="left", line=0.8, anim_in=tanim("rise-by-word", duration=0.5, unit="word", stagger=0.1),
          name="Nombre del canal")
    label(t, t.track("text", "Lema"), "recetas fáciles para todos los días", 1.5, 4.5, Box(105, 720, 760, 70), "Quicksand",
          42, "#5A4632", weight=700, align="left", anim_in=tanim("fade", duration=0.5), name="Lema")
    for i, ic in enumerate(["🍳", "🥄", "🧄", "🍅"]):
        at = 1.8 + i * 0.15
        label(t, t.track("text", "Icono"), ic, at, 6.0 - at, centered(150 + i * 130, 880, 120, 120), "Inter", 76, "#000000",
              editable=False, motion=pop(0, 0.4), anim_loop=tanim("float", amount=0.12, speed=0.6 + i * 0.1))
    music(t, "happy-whistling-ukulele", 20, 0.75)
    return t


def coc_crudo_listo():
    t = _t(tall, "yt-coc-crudo-listo", "De crudo a listo", "Raw to ready", 30,
           COC + ["antes y después", "crudo", "listo", "before after"], 8.0, thumb_at=5.2, background="#FAF3E0")
    bg(t, "#FAF3E0")
    t.photo(t.track("video", "Crudo"), "y6-flatlay-04", 0, 8.0, Box(0, 0, 1080, 950), kb(8.0, 1.0, 1.06),
            label="Ingredientes crudos")
    t.photo(t.track("video", "Listo"), "y6-dish-06", 2.4, 5.6, Box(0, 970, 1080, 950),
            [(0, {"dy": 950}, "out"), (0.6, {}, "linear"), (5.6, {"s": 1.05})], label="Plato listo")
    t.solid(t.track("shape", "Divisor"), "#FAF3E0", 0, 8.0, Box(0, 945, 1080, 30))
    for (txt, y, at, c) in (("CRUDO", 60, 0.3, "#3D405B"), ("LISTO", 1010, 2.8, "#E07A5F")):
        pill(t, t.track("shape", "Etiqueta"), c, at, 8.0 - at, Box(60, y, 300, 90), pop(0, 0.35))
        label(t, t.track("text", "Etiqueta"), txt, at, 8.0 - at, Box(60, y, 300, 90), "Lilita One", 56, "#FFFFFF",
              weight=400, motion=pop(0, 0.35), name=txt.capitalize())
    step_badge(t, "↓", 540, 960, 150, 1.4, 6.6, "#E07A5F", "#FFFFFF", font="Inter", size=90, ring_c="#FAF3E0")
    label(t, t.track("text", "Tiempo"), "en 20 minutos", 3.4, 4.6, Box(60, 1720, 960, 130), "Pacifico", 90, "#FFFFFF",
          weight=400, layers=[shadow("#000000", 0, 4, 16, 0.7), fill("#FFFFFF")], anim_in=tanim("pop", duration=0.4),
          name="Tiempo")
    flash(t, 2.4, 0.25, peak=0.5)
    music(t, "funshine", 6, 0.75)
    return t


def coc_receta_60s():
    t = _t(tall, "yt-coc-receta-60s", "Receta en 60 segundos", "60-second recipe", 31,
           COC + ["rápida", "60 segundos", "quick recipe", "short"], 15.0, thumb_at=6.2, background="#111111")
    samples = ["y6-hands-02", "cooking-01", "y6-hands-04", "y6-hands-05", "cooking-03", "y6-dish-01"]
    caps = ["corta", "mezcla", "pica", "corta fino", "a la sartén", "¡a comer!"]
    each = 15.0 / 6
    slides(t, samples, 0.0, each, transition=None, kb_amount=0.0, labels=[f"Toma {i + 1}" for i in range(6)],
           motion_fn=lambda i, d: [(0, {"s": 1.18}, "snap"), (0.3, {"s": 1.04}, "linear"), (d, {"s": 1.0})])
    shade_top(t, 360, 0.6)
    shade_bottom(t, 420, 0.5)
    t.solid(t.track("shape", "Barra"), "#FF006E", 0, 15.0, Box(0, 70, 1080, 150), [(0, {"dx": -1080}, "out"), (0.4, {})])
    label(t, t.track("text", "Título"), "RECETA EN\n60 SEGUNDOS", 0.2, 14.8, Box(40, 70, 760, 150), "Lilita One", 64,
          "#FFFFFF", weight=400, align="left", line=1.0, anim_in=tanim("slide-right", duration=0.4, distance=0.2),
          name="Título")
    t.solid(t.track("shape", "Reloj"), "#FFFFFF", 0.3, 14.7, Box(810, 85, 230, 120), pop(0, 0.35), radius=60,
            kind="rounded-rectangle")
    count_fn(t, t.track("text", "Reloj"), lambda f: 60 * f, lambda v: f"0:{int(v):02d}" if v < 60 else "1:00", 0.3, 14.5,
             "1:00", Box(810, 85, 230, 120), big("Lilita One", 64, "#FF006E", weight=400), step=3, name="Tiempo final")
    for i, c in enumerate(caps):
        at = i * each + 0.15
        label(t, t.track("text", "Pie"), c, at, each - 0.3 if i < 5 else 15.0 - at, Box(60, 1560, 960, 200),
              "Lilita One", 130, "#FFFFFF", weight=400,
              layers=[shadow("#000000", 0, 8, 0, 0.9), stroke(8, "#111111"), fill("#FFFFFF" if i < 5 else "#FFBE0B")],
              anim_in=tanim("pop", duration=0.25), name=f"Pie {i + 1}")
    t.adjust([effect("zoom_pulse", animated={"punch": spike([each * k for k in range(1, 6)], 0.3, 0.25)})], name="Golpes")
    music(t, "funky-energy-loop", 60, 0.8)
    return t


def coc_menu_semana():
    t = _t(wide, "yt-coc-menu-semana", "Menú de la semana", "Weekly meal plan", 32,
           COC + ["menú", "semana", "meal prep", "planificación"], 12.0, thumb_at=7.5, background="#FFFDF7")
    bg(t, "#FFFDF7")
    label(t, t.track("text", "Título"), "MENÚ DE LA SEMANA", 0.2, 11.8, Box(0, 50, 1920, 130), "Archivo Black", 96, INK,
          weight=400, spacing=4, anim_in=tanim("fade-up-char", duration=0.5, unit="character", stagger=0.02),
          name="Título")
    line(t, t.track("shape", "Línea"), "#F4A261", 0.6, 11.4, centered(960, 190, 420, 8), grow="c", length=0.5)
    days = [("LUN", "Lentejas", "y6-h-dish-01"), ("MAR", "Tacos", "h-food-02"), ("MIÉ", "Ensalada", "y6-h-dish-05"),
            ("JUE", "Pasta", "y6-h-dish-02"), ("VIE", "Pizza casera", "y6-h-flatlay-06")]
    colours = ["#E76F51", "#F4A261", "#E9C46A", "#2A9D8F", "#264653"]
    for i, (d, dish, s) in enumerate(days):
        at = 0.8 + i * 0.5
        x = 75 + i * 360
        mo = [(0, {"dy": 200}, "out"), (0.5, {})]
        op = keys([(0, 0.0), (0.3, 1.0)])
        t.solid(t.track("shape", "Tarjeta"), "#FFFFFF", at, 12.0 - at, Box(x, 250, 330, 720), mo, radius=26,
                kind="rounded-rectangle", layers=[shadow("#000000", 0, 10, 24, 0.15), fill("#FFFFFF"), no_stroke()],
                opacity=op)
        t.solid(t.track("shape", "Día"), colours[i], at, 12.0 - at, Box(x, 250, 330, 100), mo, radius=26,
                kind="rounded-rectangle", opacity=op)
        t.solid(t.track("shape", "Día"), colours[i], at, 12.0 - at, Box(x, 300, 330, 50), mo, opacity=op)
        label(t, t.track("text", "Día"), d, at, 12.0 - at, Box(x, 250, 330, 100), "Archivo Black", 54, "#FFFFFF", weight=400,
              motion=mo, spacing=4, name=f"Día {i + 1}")
        t.photo(t.track("video", "Foto"), s, at, 12.0 - at, Box(x + 20, 370, 290, 400), mo, label=f"Plato {i + 1}",
                opacity=op)
        label(t, t.track("text", "Plato"), dish, at + 0.2, 11.8 - at, Box(x + 10, 790, 310, 150), "Patrick Hand", 54, INK,
              weight=400, line=1.0, anim_in=tanim("fade", duration=0.4), name=f"Plato {i + 1}")
    label(t, t.track("text", "Pie"), "lista de compras en la descripción ↓", 3.8, 8.2, Box(0, 990, 1920, 70),
          "Patrick Hand", 48, "#8A6E5A", weight=400, anim_in=tanim("fade", duration=0.5), name="Pie")
    music(t, "city-sunshine", 30, 0.65)
    return t


def coc_nutricion():
    t = _t(tall, "yt-coc-nutricion", "Información nutricional", "Nutrition facts", 33,
           COC + ["nutrición", "calorías", "macros", "nutrition"], 8.0, thumb_at=5.0, background="#F5F5F0")
    bg(t, "#F5F5F0")
    rphoto(t, "y6-dish-04", 0, 8.0, Box(60, 60, 960, 820), 44, kb(8.0, 1.0, 1.05), label_="Foto del plato")
    panel = Box(60, 920, 960, 940)
    t.solid(t.track("shape", "Etiqueta"), "#FFFFFF", 0.3, 7.7, panel, [(0, {"dy": 300}, "out"), (0.5, {})],
            layers=[shadow("#000000", 0, 8, 24, 0.15), fill("#FFFFFF"), stroke(6, "#111111")],
            opacity=keys([(0, 0.0), (0.3, 1.0)]))
    label(t, t.track("text", "Título"), "Información nutricional", 0.5, 7.5, Box(100, 950, 880, 90), "Archivo Black", 58,
          "#111111", weight=400, align="left", anim_in=tanim("fade", duration=0.4), name="Título")
    t.solid(t.track("shape", "Raya"), "#111111", 0.6, 7.4, Box(100, 1050, 880, 14))
    label(t, t.track("text", "Porción"), "Por porción", 0.7, 7.3, Box(100, 1075, 500, 70), "Archivo", 40, "#111111",
          weight=700, align="left", name="Porción")
    count_fn(t, t.track("text", "Calorías"), lambda f: 420 * (1 - (1 - f) ** 3), lambda v: f"{int(v)} kcal", 0.8, 1.4,
             "420 kcal", Box(460, 1060, 520, 100), big("Archivo Black", 76, "#111111", weight=400, align="right"),
             name="Calorías")
    t.solid(t.track("shape", "Raya"), "#111111", 0.9, 7.1, Box(100, 1170, 880, 6))
    rows = [("Proteína", "32 g", 0.64, "#E63946"), ("Carbohidratos", "40 g", 0.8, "#F4A261"),
            ("Grasas", "12 g", 0.3, "#2A9D8F"), ("Fibra", "8 g", 0.2, "#6A994E")]
    for i, (k, v, f, c) in enumerate(rows):
        at = 1.4 + i * 0.35
        y = 1200 + i * 165
        label(t, t.track("text", "Dato"), k, at, 8.0 - at, Box(100, y, 600, 70), "Archivo", 46, "#111111", weight=700,
              align="left", anim_in=tanim("fade", duration=0.3), name=f"Nutriente {i + 1}")
        label(t, t.track("text", "Dato"), v, at, 8.0 - at, Box(700, y, 280, 70), "Archivo Black", 46, "#111111", weight=400,
              align="right", anim_in=tanim("fade", duration=0.3), name=f"Cantidad {i + 1}")
        t.solid(t.track("shape", "Barra"), "#111111", at, 8.0 - at, Box(100, y + 80, 880, 26), radius=13,
                kind="rounded-rectangle", alpha=0.08)
        t.solid(t.track("shape", "Barra"), c, at + 0.1, 7.9 - at, Box(100, y + 80, 880 * f, 26),
                [(0, {"sx": 0.0, "dx": -880 * f / 2}, "out"), (0.8, {})], radius=13, kind="rounded-rectangle")
    music(t, "fresh-focus", 6, 0.65)
    return t


def coc_pizarra():
    t = _t(wide, "yt-coc-pizarra", "Pizarra: hoy cocinamos", "Chalkboard: today we cook", 34,
           COC + ["pizarra", "hoy cocinamos", "chalkboard", "menú"], 12.0, thumb_at=8.0, background="#2F3A33")
    t.solid(t.track("shape", "Marco"), "#8B5A2B", 0, 12.0, layers=[gradient([(0, "#A0703F"), (1, "#6E4521")], angle=45),
                                                                  no_stroke()])
    t.solid(t.track("shape", "Pizarra"), "#2F3A33", 0, 12.0, Box(40, 40, 1840, 1000),
            layers=[gradient([(0, "#36443B"), (1, "#26302A")], angle=120), no_stroke()])
    chalk = "#F2F2EC"
    label(t, t.track("text", "Título"), "HOY COCINAMOS", 0.3, 11.7, Box(120, 90, 1000, 150), "Amatic SC", 140, chalk,
          weight=700, align="left", layers=[fill(chalk, 0.92)], anim_in=tanim("wipe", duration=0.9, angle=0), name="Título")
    label(t, t.track("text", "Plato"), "Tacos de pescado", 1.2, 10.8, Box(120, 240, 1000, 120), "Caveat", 100, "#FFD166",
          weight=700, align="left", anim_in=tanim("wipe", duration=0.8, angle=0), name="Plato")
    line(t, t.track("shape", "Subrayado"), "#FFD166", 2.0, 10.0, Box(125, 365, 560, 6), length=0.6, alpha=0.85)
    steps = ["1. Marina el pescado con limón", "2. Dóralo 3 min por lado", "3. Arma con col y salsa",
             "4. ¡Unas gotas de lima y listo!"]
    for i, st in enumerate(steps):
        at = 2.6 + i * 1.3
        label(t, t.track("text", "Paso"), st, at, 12.0 - at, Box(130, 420 + i * 130, 1050, 110), "Amatic SC", 84, chalk,
              weight=700, align="left", layers=[fill(chalk, 0.88)], anim_in=tanim("wipe", duration=0.9, angle=0),
              name=f"Paso {i + 1}")
    framed(t, "y6-dish-03", 0.8, 11.2, Box(1290, 200, 480, 600), [(0, {"dy": -900}, "out"), (0.6, {})], border=18,
           bottom=70, colour="#FAFAF5", radius=4, rotation=rot(4), label="Foto del plato")
    t.solid(t.track("shape", "Cinta"), "#E9E4C9", 1.3, 10.7, centered(1530, 190, 190, 54), pop(0, 0.3), alpha=0.8,
            rotation=rot(-6))
    label(t, t.track("text", "Nota"), "¡riquísimo!", 1.6, 10.4, Box(1290, 820, 480, 90), "Caveat", 64, INK, weight=700,
          rotation=rot(4), anim_in=tanim("fade", duration=0.4), name="Nota")
    grain(t, 0.22, 2.0)
    music(t, "bebop-for-joey", 40, 0.65)
    return t


def coc_reto_3():
    t = _t(wide, "yt-coc-reto-3", "Reto: solo 3 ingredientes", "Challenge: only 3 ingredients", 35,
           COC + ["reto", "3 ingredientes", "challenge", "fácil"], 8.0, thumb_at=5.6, background="#FF7F11")
    bg_gradient(t, [(0, "#FF7F11"), (1, "#FF3F00")], angle=135)
    rays(t, "#FFFFFF", 0, 8.0, centered(960, 540, 2400, 2400), alpha=0.08, points=24, speed=6)
    label(t, t.track("text", "Reto"), "RETO", 0.2, 7.8, Box(80, 40, 600, 140), "Shrikhand", 110, "#FFE14D", weight=400,
          align="left", layers=[shadow("#7A1E00", 0, 8, 0, 1.0), fill("#FFE14D")], anim_in=tanim("pop", duration=0.4),
          rotation=rot(-4), name="Reto")
    label(t, t.track("text", "Título"), "solo 3 ingredientes", 0.5, 7.5, Box(80, 170, 1300, 130), "Shrikhand", 96,
          "#FFFFFF", weight=400, align="left", layers=[shadow("#7A1E00", 0, 6, 0, 1.0), fill("#FFFFFF")],
          anim_in=tanim("slide-right", duration=0.45, distance=0.15), rotation=rot(-4), name="Título")
    items = [("Harina", "y6-flatlay-03"), ("Huevos", "y6-flatlay-08"), ("Aceite", "y6-flatlay-05")]
    for i, (n, s) in enumerate(items):
        at = 1.0 + i * 0.7
        cx = 240 + i * 380
        circle_photo(t, s, at, 8.0 - at, centered(cx, 650, 300, 300), pop(0, 0.45), ring_colour="#FFFFFF", ring_width=12,
                     label=n)
        label(t, t.track("text", "Ingrediente"), n, at + 0.2, 7.8 - at, Box(cx - 170, 830, 340, 80), "Lilita One", 56,
              "#FFFFFF", weight=400, anim_in=tanim("pop", duration=0.3), name=f"Ingrediente {i + 1}")
        label(t, t.track("text", "Signo"), "+" if i < 2 else "=", at + 0.35, 7.65 - at, centered(cx + 190, 650, 120, 140),
              "Lilita One", 110, "#FFE14D", weight=400, editable=False, anim_in=tanim("pop", duration=0.25))
    at = 3.4
    circle_photo(t, "food-03", at, 8.0 - at, centered(1560, 620, 460, 460),
                 [(0, {"s": 0.0}, "back"), (0.55, {}, "linear"), (8.0 - at, {"s": 1.04})], ring_colour="#FFE14D",
                 ring_width=16, label="Resultado")
    label(t, t.track("text", "Resultado"), "¡a comer!", at + 0.4, 4.2, Box(1260, 870, 600, 100), "Shrikhand", 70,
          "#FFE14D", weight=400, layers=[shadow("#7A1E00", 0, 5, 0, 1.0), fill("#FFE14D")],
          anim_in=tanim("pop", duration=0.35), name="Resultado")
    flash(t, at, 0.3, peak=0.6)
    t.adjust([effect("zoom_pulse", animated={"punch": spike([1.0, 1.7, 2.4, at], 0.25, 0.25)})], name="Golpes")
    music(t, "funkeriffic", 8, 0.75)
    return t


def coc_postre():
    t = _t(tall, "yt-coc-postre", "Postre sin horno", "No-bake dessert", 36,
           COC + ["postre", "dulce", "sin horno", "dessert"], 10.0, thumb_at=5.2, background="#FDE2E4")
    bg_gradient(t, [(0, "#FDE2E4"), (1, "#FAD2E1")], angle=90)
    rng = random.Random(6436)
    tr = t.track("shape", "Grageas")
    for k in range(36):
        if k % 9 == 8:
            tr = t.track("shape", "Grageas")
        at = rng.uniform(0, 1.2)
        t.solid(tr, rng.choice(["#FF8FAB", "#A0C4FF", "#FDFFB6", "#CAFFBF", "#BDB2FF"]), at, 10.0 - at,
                centered(rng.uniform(30, 1050), rng.uniform(30, 1890), 46, 14), pop(0, 0.4), radius=7,
                kind="rounded-rectangle", rotation=keys([(0, rng.uniform(0, 180)), (10.0 - at, rng.uniform(0, 180))]))
    label(t, t.track("text", "Título"), "Postre\nsin horno", 0.3, 9.7, Box(60, 120, 960, 400), "Shrikhand", 140, "#6D597A",
          weight=400, line=0.98, layers=[shadow("#FFFFFF", 0, 8, 0, 1.0), fill("#6D597A")],
          anim_in=tanim("bounce", duration=0.6, unit="line", stagger=0.15), name="Título")
    doily = t.solid(t.track("shape", "Blonda"), "#FFFFFF", 0.6, 9.4, centered(540, 930, 720, 720),
                    [(0, {"s": 0.0}, "back"), (0.6, {})], kind="burst", rotation=keys([(0, 0), (9.4, 30)]))
    geo(doily, points=36, innerRatio=0.9)
    circle_photo(t, "y6-dessert-01", 0.8, 9.2, centered(540, 930, 600, 600),
                 [(0, {"s": 0.0}, "back"), (0.6, {}, "linear"), (9.2, {"s": 1.03})], label="Foto del postre")
    steps = [("1", "Mezcla"), ("2", "Refrigera"), ("3", "¡Disfruta!")]
    for i, (n, st) in enumerate(steps):
        at = 2.0 + i * 1.0
        cx = 200 + i * 340
        step_badge(t, n, cx, 1420, 130, at, 10.0 - at, "#FF8FAB", "#FFFFFF", font="Shrikhand", size=70, ring_c="#FFFFFF")
        label(t, t.track("text", "Paso"), st, at + 0.15, 9.85 - at, Box(cx - 170, 1500, 340, 90), "Fredoka", 54,
              "#6D597A", weight=700, anim_in=tanim("pop", duration=0.3), name=f"Paso {i + 1}")
    pill(t, t.track("shape", "Tiempo"), "#6D597A", 5.0, 5.0, centered(540, 1720, 560, 100), pop(0, 0.35))
    label(t, t.track("text", "Tiempo"), "listo en 15 min ✨", 5.0, 5.0, centered(540, 1720, 560, 100), "Fredoka", 50,
          "#FFFFFF", weight=700, motion=pop(0, 0.35), name="Tiempo")
    music(t, "my-giant-bunny-friend", 4, 0.7)
    return t


def coc_cierre():
    t = _t(wide, "yt-coc-cierre", "Cierre: buen provecho", "Outro: enjoy your meal", 37,
           COC + ["cierre", "pantalla final", "end screen", "buen provecho"], 10.0, thumb_at=5.0, background="#FFF8EE")
    bg(t, CREAM)
    dots(t, ["#F4D6CC", "#E9EDE4", "#FFE8A3"], 16, 0, 10.0, seed=6437, size=(60, 160), drift=30, alpha=0.7)
    label(t, t.track("text", "Título"), "¡Buen provecho!", 0.2, 9.8, Box(0, 40, 1920, 200), "Pacifico", 130, TOMATO,
          weight=400, anim_in=tanim("pop", duration=0.5), name="Título")
    for i, (lab, s, r) in enumerate([("Siguiente receta", "y6-h-dish-04", -2.5), ("La más vista", "y6-h-flatlay-05", 2.5)]):
        at = 0.6 + i * 0.25
        box = Box(170 + i * 880, 300, 700, 400)
        framed(t, s, at, 10.0 - at, box, [(0, {"s": 0.0}, "back"), (0.5, {})], border=16, colour="#FFFFFF", radius=8,
               rotation=rot(r), label=f"Video {i + 1}")
        label(t, t.track("text", "Video"), lab, at + 0.4, 9.6 - at, Box(box.x, 740, box.w, 80), "Caveat", 72, INK,
              weight=700, anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name=f"Título video {i + 1}")
    pill(t, t.track("shape", "Botón"), TOMATO, 1.4, 8.6, centered(960, 890, 520, 100), pop(0, 0.4))
    label(t, t.track("text", "Botón"), "SUSCRÍBETE 🔔", 1.4, 8.6, centered(960, 890, 520, 100), "Lilita One", 52, "#FFFFFF",
          weight=400, anim_loop=tanim("pulse", amount=4, speed=1.2), name="Botón")
    label(t, t.track("text", "Pie"), "cuéntame en los comentarios qué receta quieres ver 👇", 2.0, 8.0,
          Box(0, 970, 1920, 70), "Quicksand", 40, "#5A4632", weight=700, anim_in=tanim("fade", duration=0.5), name="Pie")
    music(t, "happy-whistling-ukulele", 60, 0.7)
    return t


COCINA = [coc_ingredientes_lista, coc_ingredientes_flotan, coc_pasos, coc_pasos_wide, coc_temporizador, coc_plato_final,
          coc_receta_card, coc_receta_vertical, coc_cenital, coc_intro_canal, coc_crudo_listo, coc_receta_60s,
          coc_menu_semana, coc_nutricion, coc_pizarra, coc_reto_3, coc_postre, coc_cierre]


# =====================================================================================================
# 3. MISTERIO / TRUE CRIME
# =====================================================================================================

PAPER, INK_T, RED, MANILA, NIGHT = "#EFE6D2", "#1E1B16", "#B3121B", "#D2B074", "#0E0F12"


def desk_bg(t, colour: str = "#1B1612"):
    bg_gradient(t, [(0, colour), (1, "#0B0907")], angle=110)
    rng = random.Random(len(t.id))
    tr = t.track("shape", "Vetas")
    for k in range(10):
        t.solid(tr, "#000000", 0, t.duration, Box(0, rng.uniform(0, t.h), t.w, rng.uniform(2, 6)), alpha=0.25)


def cork_bg(t, seed: int, frame: float = 34):
    t.solid(t.track("shape", "Marco"), "#5C3A1E", 0, t.duration,
            layers=[gradient([(0, "#6E4826"), (1, "#3F2712")], angle=45), no_stroke()])
    t.solid(t.track("shape", "Corcho"), "#B07D4F", 0, t.duration, Box(frame, frame, t.w - 2 * frame, t.h - 2 * frame),
            layers=[gradient([(0, "#C08A57"), (1, "#9C6B3F")], angle=120), no_stroke()])
    rng = random.Random(seed)
    tr = t.track("shape", "Grano")
    for k in range(70):
        if k % 35 == 34:
            tr = t.track("shape", "Grano")
        s = rng.uniform(5, 14)
        t.solid(tr, rng.choice(["#7A512B", "#D9A774"]), 0, t.duration,
                centered(rng.uniform(frame, t.w - frame), rng.uniform(frame, t.h - frame), s, s * rng.uniform(0.6, 1)),
                kind="ellipse", alpha=0.5)


def pinned(t, sample: str, box: Box, at: float, angle: float, label_: str, *, bottom: float = 60, colour="#F4F1EA",
           pin="#D62828", sepia=True):
    """A print pinned on the board: drops in, the pin goes in after it."""
    mo = [(0, {"s": 1.25, "dy": -40}, "out"), (0.35, {})]
    clip = framed(t, sample, at, t.duration - at, box, mo, border=14, bottom=bottom, colour=colour, radius=2,
                  rotation=rot(angle), label=label_, shadow_alpha=0.5)
    if sepia:
        clip["effects"] = [effect("color.basic", saturation=-0.55, contrast=0.1, temperature=0.12, fade=0.1)]
    push_pin(t, box.cx, box.y + 6, at + 0.3, pin)
    return (box.cx, box.y + 6)


def note_card(t, content: str, box: Box, at: float, angle: float, *, colour="#FFF7B8", ink="#1E1B16",
              font="Permanent Marker", size=44, name=None, pin=None):
    mo = [(0, {"s": 1.2}, "out"), (0.3, {})]
    paper(t, box, at, motion=mo, rotation=angle, colour=colour, shadow_alpha=0.4, name="Nota")
    label(t, t.track("text", "Nota"), content, at + 0.15, t.duration - at - 0.15, box, font, size, ink, weight=400,
          line=1.05, rotation=rot(angle), anim_in=tanim("fade", duration=0.3), name=name or content)
    if pin:
        push_pin(t, box.cx, box.y + 4, at + 0.25, pin, size=28)
    return (box.cx, box.y + 4)


def mood(t, grain_amount=0.22, vig=0.65, extra=None):
    t.adjust((extra or []) + [effect("stylize.film_grain", amount=grain_amount, grainSize=1.8),
                              effect("stylize.vignette", amount=vig * 0.55, softness=1.0)], name="Ambiente")


def mist_expediente():
    t = _t(wide, "yt-mist-expediente", "Expediente del caso", "Case file", 40,
           MIST + ["expediente", "caso", "case file", "confidencial"], 10.0, thumb_at=6.2, background="#1B1612")
    desk_bg(t)
    # The folder: back cover with its tab, the sheet that slides out, the front flap lower down.
    mo = [(0, {"dy": 700}, "out"), (0.7, {})]
    t.solid(t.track("shape", "Carpeta"), MANILA, 0, 10.0, Box(230, 130, 330, 90), mo, radius=14, kind="rounded-rectangle",
            layers=[fill("#C7A266"), no_stroke()])
    t.solid(t.track("shape", "Carpeta"), MANILA, 0, 10.0, Box(230, 180, 1460, 860), mo, radius=10, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 16, 40, 0.6), fill("#C7A266"), no_stroke()])
    label(t, t.track("text", "Pestaña"), "CASO 0427", 0.1, 9.9, Box(230, 130, 330, 60), "Special Elite", 38, "#5B4220",
          weight=400, motion=mo, name="Pestaña")
    sheet = Box(300, 230, 1320, 800)
    smo = [(0, {"dy": 700}, "hold"), (0.7, {"dy": 700}, "out"), (1.4, {})]
    t.solid(t.track("shape", "Hoja"), PAPER, 0, 10.0, sheet, smo, radius=4, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 6, 16, 0.35), fill(PAPER), no_stroke()])
    label(t, t.track("text", "Encabezado"), "EXPEDIENTE N.º 0427", 1.5, 8.5, Box(360, 270, 760, 80), "Special Elite", 58,
          INK_T, weight=400, align="left", anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name="Expediente")
    t.solid(t.track("shape", "Raya"), INK_T, 2.2, 7.8, Box(360, 360, 740, 4), [(0, {"sx": 0.0, "dx": -370}, "out"),
                                                                            (0.5, {})])
    typed(t, "NOMBRE:   Elena Varga\nEDAD:     24 años\nFECHA:    14/03/1996\nLUGAR:    Valle Hondo", Box(360, 400, 760, 340),
          2.4, 2.4, size=44, line_h=1.55, name="Datos del caso")
    label(t, t.track("text", "Estado"), "ESTADO:", 4.9, 5.1, Box(360, 742, 260, 70), "Special Elite", 44, INK_T, weight=400,
          align="left", anim_in=tanim("fade", duration=0.3), editable=False)
    stamp(t, "SIN RESOLVER", Box(630, 735, 480, 90), 5.4, size=58, angle=-4, font="Special Elite", spacing=4,
          name="Estado")
    framed(t, "y6-oldphoto-05", 1.6, 8.4, Box(1180, 330, 360, 470), [(0, {"dx": 400, "s": 1.1}, "out"), (0.6, {})],
           border=14, bottom=50, colour="#F7F3EA", radius=2, rotation=rot(4), label="Foto del caso", shadow_alpha=0.45)
    t.tracks[-1].clips[-1]["effects"] = [effect("color.basic", saturation=-1.0, contrast=0.15, fade=0.12)]
    outline(t, t.track("shape", "Clip"), "#A8A8A8", 6, 2.2, 7.8, Box(1300, 290, 70, 150), pop(0, 0.3), radius=30,
            kind="rounded-rectangle")
    stamp(t, "CONFIDENCIAL", Box(1080, 860, 520, 110), 6.4, size=70, angle=-10, name="Sello")
    mood(t, 0.25, 0.75)
    music(t, "hidden-truth", 4, 0.75)
    return t


def mist_tablero():
    t = _t(wide, "yt-mist-tablero", "Tablero de pistas con hilo rojo", "Clue board with red string", 41,
           MIST + ["pistas", "hilo rojo", "investigación", "evidence board"], 12.0, thumb_at=9.0, background="#5C3A1E")
    cork_bg(t, 6441)
    pts = [pinned(t, "y6-oldphoto-03", Box(150, 140, 300, 380), 0.3, -4, "Foto 1"),
           pinned(t, "y6-h-house-02", Box(780, 110, 420, 300), 0.7, 3, "Foto 2"),
           pinned(t, "y6-h-street-01", Box(1440, 170, 380, 280), 1.1, -3, "Foto 3"),
           pinned(t, "y6-shadow-02", Box(1050, 560, 290, 370), 1.5, 5, "Foto 4")]
    notes = [note_card(t, "¿quién llamó a las 22:15?", Box(260, 660, 360, 220), 1.9, 3, name="Nota 1", pin="#1D4ED8"),
             note_card(t, "el auto azul", Box(1500, 640, 330, 170), 2.2, -4, colour="#FFFFFF", name="Nota 2",
                       pin="#16A34A")]
    links = [(pts[0], pts[1]), (pts[1], pts[2]), (pts[1], pts[3]), (pts[0], notes[0]), (pts[3], notes[0]),
             (pts[2], notes[1]), (pts[3], notes[1])]
    for i, (a, b) in enumerate(links):
        pin_string(t, a, b, 2.8 + i * 0.55, draw=0.45)
    paper(t, Box(620, 930, 680, 110), 0.5, rotation=-1.5, colour="#111111", name="Rótulo")
    label(t, t.track("text", "Título"), "LAS PISTAS", 0.6, 11.4, Box(620, 930, 680, 110), "Special Elite", 74, "#F2EDE2",
          weight=400, spacing=10, rotation=rot(-1.5), anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03),
          name="Título")
    mood(t, 0.18, 0.7)
    music(t, "dark-hallway", 0, 0.7)
    return t


def mist_tablero_vertical():
    t = _t(tall, "yt-mist-tablero-vertical", "Tablero vertical: ¿qué pasó?", "Vertical clue board", 42,
           MIST + ["pistas", "hilo rojo", "vertical", "short"], 12.0, thumb_at=8.0, background="#5C3A1E")
    cork_bg(t, 6442)
    paper(t, Box(120, 110, 840, 220), 0.2, rotation=-2, colour="#F4EEDF", name="Título")
    label(t, t.track("text", "Título"), "¿QUÉ PASÓ?", 0.3, 11.7, Box(120, 110, 840, 220), "Permanent Marker", 120, RED,
          weight=400, rotation=rot(-2), anim_in=tanim("pop", duration=0.4), name="Título")
    push_pin(t, 540, 120, 0.6)
    pts = [pinned(t, "y6-oldphoto-06", Box(110, 470, 380, 480), 0.8, -5, "Foto 1"),
           pinned(t, "y6-house-02", Box(600, 520, 380, 480), 1.3, 4, "Foto 2"),
           pinned(t, "y6-fog-01", Box(330, 1180, 420, 330), 1.8, -2, "Foto 3")]
    n = note_card(t, "visto por última vez\n22:15", Box(560, 1600, 420, 200), 2.3, 3, name="Nota", pin="#1D4ED8", size=40)
    n2 = note_card(t, "?", Box(140, 1620, 160, 160), 2.6, -6, colour="#FFFFFF", size=110, name="Pregunta",
                   ink=RED)
    for i, (a, b) in enumerate([(pts[0], pts[1]), (pts[1], pts[2]), (pts[0], pts[2]), (pts[2], n), (pts[2], n2)]):
        pin_string(t, a, b, 3.0 + i * 0.6, draw=0.45)
    mood(t, 0.18, 0.7)
    music(t, "hidden-truth", 30, 0.7)
    return t


def mist_maquina():
    t = _t(wide, "yt-mist-maquina", "Máquina de escribir", "Typewriter opening", 43,
           MIST + ["máquina de escribir", "typewriter", "relato", "intro"], 9.0, thumb_at=6.5, background="#0E0D0B")
    desk_bg(t, "#16120E")
    paper(t, Box(170, 70, 1580, 940), 0.0, rotation=-1, colour=PAPER, motion=kb(9.0, 1.0, 1.03), name="Hoja")
    t.solid(t.track("shape", "Margen"), RED, 0.0, 9.0, Box(300, 70, 3, 940), kb(9.0, 1.0, 1.03), alpha=0.5,
            rotation=rot(-1))
    typed(t, "La noche del 14 de marzo,\nnadie vio salir a Elena.", Box(380, 260, 1250, 360), 0.6, 3.6, size=84,
          line_h=1.4, align="left", caret=True, name="Relato")
    typed(t, "Valle Hondo, 1996", Box(1000, 700, 640, 70), 5.0, 1.2, size=44, colour="#5A5145", align="right", name="Lugar")
    framed(t, "y6-oldphoto-01", 5.6, 3.4, Box(420, 660, 240, 300), [(0, {"dy": -300, "s": 1.2}, "out"), (0.5, {})],
           border=10, bottom=36, colour="#F7F3EA", radius=2, rotation=rot(-6), label="Foto", shadow_alpha=0.5)
    t.tracks[-1].clips[-1]["effects"] = [effect("color.basic", saturation=-1.0, contrast=0.1)]
    mood(t, 0.28, 0.75, [effect("stylize.sepia")])
    music(t, "cursed-intro", 0, 0.7)
    return t


def mist_censurado():
    t = _t(wide, "yt-mist-censurado", "Documento censurado", "Redacted document", 44,
           MIST + ["censurado", "clasificado", "redacted", "secreto"], 9.0, thumb_at=5.8, background="#141210")
    desk_bg(t, "#141210")
    paper(t, Box(240, 50, 1440, 980), 0.0, rotation=0.6, colour="#F1EBDD", motion=[(0, {"dy": 900}, "out"), (0.6, {})],
          name="Hoja")
    label(t, t.track("text", "Cabecera"), "INFORME 12-B  ·  USO INTERNO", 0.6, 8.4, Box(320, 100, 1000, 70), "Special Elite",
          44, INK_T, weight=400, align="left", anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name="Cabecera")
    lines = ["El 14 de marzo a las 22:15 se recibió una llamada", "desde el teléfono de la casa del lago. La persona",
             "que habló dijo llamarse Tomás Ibarra y pidió ayuda", "para encontrar a su hermana. La patrulla llegó a",
             "las 23:40. No había nadie. En la mesa quedaban dos", "tazas de café, todavía tibias, y una nota que decía:",
             "«no me busquen». El caso se archivó en 1997."]
    for i, ln in enumerate(lines):
        typed(t, ln, Box(320, 220 + i * 92, 1300, 80), 1.0 + i * 0.25, 0.6, size=44, name=f"Línea {i + 1}",
              editable=(i in (0, 6)))
    bars = [(860, 220, 300), (320, 312, 700), (1130, 404, 330), (320, 496, 520), (930, 680, 420), (320, 772, 360)]
    for i, (x, y, w) in enumerate(bars):
        redact(t, Box(x, y + 2, w, 54), 3.2 + i * 0.3, length=0.25)
    stamp(t, "CLASIFICADO", Box(1060, 860, 600, 110), 5.2, size=60, angle=-8)
    t.solid(t.track("shape", "Oscurecer"), "#000000", 6.4, 2.6, opacity=keys([(0, 0.0), (0.4, 0.6)]))
    label(t, t.track("text", "Pregunta"), "¿QUÉ OCULTABAN?", 6.5, 2.5, Box(0, 410, 1920, 220), "Bebas Neue", 200, "#FFFFFF",
          weight=400, spacing=8, layers=[shadow("#000000", 0, 8, 26, 0.8), fill("#FFFFFF")],
          anim_in=tanim("blur-in", duration=0.6), name="Pregunta")
    mood(t, 0.22, 0.7)
    music(t, "horroriffic", 8, 0.7)
    return t


def mist_linea_tiempo():
    t = _t(wide, "yt-mist-linea-tiempo", "Línea de tiempo del caso", "Case timeline", 45,
           MIST + ["línea de tiempo", "cronología", "timeline", "hechos"], 14.0, thumb_at=11.4, background=NIGHT)
    grid_bg(t, NIGHT, "#FFFFFF", step=90, alpha=0.04)
    label(t, t.track("text", "Título"), "LÍNEA DE TIEMPO", 0.2, 13.8, Box(80, 30, 1000, 140), "Bebas Neue", 110, "#FFFFFF",
          weight=400, spacing=6, align="left", anim_in=tanim("wipe", duration=0.6, angle=0), name="Título")
    label(t, t.track("text", "Fecha"), "14 DE MARZO, 1996", 0.5, 13.5, Box(84, 160, 1000, 60), "Special Elite", 42, RED,
          weight=400, align="left", anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name="Fecha")
    line(t, t.track("shape", "Línea"), "#FFFFFF", 0.8, 13.2, Box(120, 690, 1680, 4), length=1.2, alpha=0.6)
    events = [("21:40", "Sale de casa sola", "y6-h-street-03"), ("22:15", "Última llamada", "y6-h-house-04"),
              ("23:40", "La patrulla no encuentra a nadie", "y6-h-fog-03"), ("06:30", "Hallan el auto en el camino", "y6-h-fog-01")]
    for i, (tm, txt, s) in enumerate(events):
        at = 1.6 + i * 2.4
        cx = 330 + i * 420
        framed(t, s, at, 14.0 - at, Box(cx - 170, 290, 340, 240), [(0, {"dy": 60}, "out"), (0.5, {})], border=8,
               colour="#E8E2D4", radius=2, rotation=rot((-1) ** i * 2), label=f"Foto {i + 1}", shadow_alpha=0.6)
        t.tracks[-1].clips[-1]["effects"] = [effect("color.basic", saturation=-0.8, contrast=0.15)]
        line(t, t.track("shape", "Guía"), "#FFFFFF", at + 0.3, 13.7 - at, Box(cx - 1, 545, 2, 140), grow="y", length=0.3,
             alpha=0.5)
        t.solid(t.track("shape", "Nodo"), RED, at + 0.2, 13.8 - at, centered(cx, 692, 36, 36), pop(0, 0.35), kind="ellipse",
                layers=[glow(RED, 14, 0.8), fill(RED), stroke(4, "#FFFFFF")])
        label(t, t.track("text", "Hora"), tm, at + 0.3, 13.7 - at, Box(cx - 200, 720, 400, 110), "Bebas Neue", 100, RED,
              weight=400, anim_in=tanim("pop", duration=0.3), name=f"Hora {i + 1}")
        typed(t, txt, Box(cx - 195, 830, 390, 130), at + 0.6, 0.9, size=38, colour="#E8E2D4", align="center",
              name=f"Hecho {i + 1}")
    mood(t, 0.18, 0.6)
    music(t, "alien-invasion", 6, 0.7)
    return t


def mist_linea_vertical():
    t = _t(tall, "yt-mist-linea-vertical", "Cronología vertical", "Vertical timeline", 46,
           MIST + ["línea de tiempo", "cronología", "vertical", "short"], 14.0, thumb_at=11.0, background="#101114")
    bg_gradient(t, [(0, "#16181D"), (1, "#0A0B0D")], angle=90)
    label(t, t.track("text", "Título"), "LA ÚLTIMA NOCHE", 0.2, 13.8, Box(60, 100, 960, 175), "Bebas Neue", 140, "#FFFFFF",
          weight=400, spacing=4, anim_in=tanim("wipe", duration=0.6, angle=0), name="Título")
    label(t, t.track("text", "Sub"), "cronología del caso", 0.5, 13.5, Box(60, 260, 960, 70), "Special Elite", 46, RED,
          weight=400, anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name="Subtítulo")
    line(t, t.track("shape", "Línea"), "#FFFFFF", 0.8, 13.2, Box(168, 420, 4, 1380), grow="y", length=1.4, alpha=0.5)
    events = [("21:40", "Sale de casa", "y6-oldphoto-03"), ("22:15", "Llama desde\nel lago", "y6-house-01"),
              ("23:40", "La casa\nestá vacía", "y6-house-03"), ("06:30", "Aparece\nel auto", "y6-fog-02")]
    for i, (tm, txt, s) in enumerate(events):
        at = 1.4 + i * 2.6
        cy = 520 + i * 350
        t.solid(t.track("shape", "Nodo"), RED, at, 14.0 - at, centered(170, cy, 44, 44), pop(0, 0.35), kind="ellipse",
                layers=[glow(RED, 14, 0.8), fill(RED), stroke(5, "#FFFFFF")])
        label(t, t.track("text", "Hora"), tm, at + 0.1, 13.9 - at, Box(230, cy - 120, 360, 120), "Bebas Neue", 120, RED,
              weight=400, align="left", anim_in=tanim("slide-right", duration=0.3, distance=0.15), name=f"Hora {i + 1}")
        typed(t, txt, Box(232, cy, 380, 130), at + 0.4, 0.8, size=44, colour="#E8E2D4", name=f"Hecho {i + 1}")
        framed(t, s, at + 0.3, 13.7 - at, Box(640, cy - 130, 340, 250), [(0, {"dx": 400}, "out"), (0.5, {})], border=8,
               colour="#E8E2D4", radius=2, rotation=rot((-1) ** i * 3), label=f"Foto {i + 1}", shadow_alpha=0.6)
        t.tracks[-1].clips[-1]["effects"] = [effect("color.basic", saturation=-0.85, contrast=0.15)]
    mood(t, 0.2, 0.6)
    music(t, "dark-hallway", 6, 0.7)
    return t


def mist_mapa():
    t = _t(wide, "yt-mist-mapa", "Mapa del caso", "Case map", 47,
           MIST + ["mapa", "ubicación", "ruta", "map"], 12.0, thumb_at=9.0, background="#0B1416")
    t.photo(t.track("video", "Mapa"), "y6-h-map-01", 0, 12.0, t.full, kb(12.0, 1.0, 1.12, dx=-60, dy=-30),
            label="Tu mapa", effects=[effect("duotone", strength=0.85, shadowColor="#0b1416", highlightColor="#9fc9c4",
                                             contrast=0.55)])
    shade_full(t, 0.25, colour="#0B1416")
    stops = [((420, 760), "CASA · 21:40"), ((930, 470), "ÚLTIMO AVISTAMIENTO · 22:15"), ((1480, 640), "AUTO · 06:30")]
    for i, ((x, y), txt) in enumerate(stops):
        at = 1.0 + i * 2.6
        if i:
            px, py = stops[i - 1][0]
            n = 9
            for k in range(n):
                f0 = (k + 0.15) / n
                f1 = (k + 0.65) / n
                pin_string(t, (px + (x - px) * f0, py + (y - py) * f0), (px + (x - px) * f1, py + (y - py) * f1),
                           at - 1.2 + k * 0.12, colour="#FFD23F", width=6, draw=0.12)
        mo = [(0, {"dy": -220}, "out"), (0.35, {"dy": 10}, "smooth"), (0.5, {})]
        t.solid(t.track("shape", "Pin"), RED, at, 12.0 - at, centered(x, y - 46, 70, 70), mo, kind="ellipse",
                layers=[shadow("#000000", 0, 8, 10, 0.6), fill(RED), stroke(4, "#FFFFFF")])
        t.solid(t.track("shape", "Pin"), RED, at, 12.0 - at, centered(x, y - 8, 34, 34), mo, kind="triangle",
                rotation=rot(180))
        t.solid(t.track("shape", "Pin"), "#FFFFFF", at, 12.0 - at, centered(x, y - 46, 24, 24), mo, kind="ellipse")
        lab = Box(x + 50, y - 120, 560, 70)
        t.solid(t.track("shape", "Etiqueta"), "#000000", at + 0.3, 11.7 - at, lab, slide_in(dx=-40, length=0.3), radius=6,
                kind="rounded-rectangle", alpha=0.75)
        label(t, t.track("text", "Etiqueta"), txt, at + 0.35, 11.65 - at, Box(lab.x + 20, lab.y, lab.w - 30, lab.h),
              "Special Elite", 34, "#FFFFFF", weight=400, align="left",
              anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name=f"Lugar {i + 1}")
    ring(t, t.track("shape", "Radar"), RED, 6, 6.4, 5.6, centered(1480, 640, 160, 160),
         [(0, {"s": 0.3}, "out"), (1.4, {"s": 2.4})], opacity=keys([(0, 1.0), (1.4, 0.0, "hold"), (1.5, 0.0)]))
    pill(t, t.track("shape", "Distancia"), "#FFD23F", 7.4, 4.6, Box(80, 940, 380, 90), pop(0, 0.35))
    label(t, t.track("text", "Distancia"), "4,2 km en 9 horas", 7.4, 4.6, Box(80, 940, 380, 90), "Special Elite", 38,
          "#111111", weight=400, motion=pop(0, 0.35), name="Distancia")
    label(t, t.track("text", "Título"), "EL RECORRIDO", 0.3, 11.7, Box(80, 50, 900, 110), "Bebas Neue", 110, "#FFFFFF",
          weight=400, spacing=8, align="left", layers=[shadow("#000000", 0, 4, 16, 0.8), fill("#FFFFFF")],
          anim_in=tanim("wipe", duration=0.6, angle=0), name="Título")
    mood(t, 0.15, 0.6)
    music(t, "hidden-truth", 40, 0.7)
    return t


def mist_sin_resolver():
    t = _t(wide, "yt-mist-sin-resolver", "Caso sin resolver", "Unsolved case", 48,
           MIST + ["caso sin resolver", "unsolved", "intro", "documental"], 8.0, thumb_at=5.0, background="#000000")
    t.photo(t.track("video", "Foto"), "y6-h-fog-02", 0, 8.0, t.full, kb(8.0, 1.0, 1.12), label="Foto del lugar",
            effects=[effect("color.basic", saturation=-0.85, contrast=0.2, exposure=-0.2)])
    shade_full(t, 0.35)
    letterbox(t, 2.39)
    label(t, t.track("text", "Año"), "1987  ·  VALLE HONDO", 0.8, 7.2, Box(0, 330, 1920, 70), "Special Elite", 46, "#D9D2C3",
          weight=400, spacing=6, anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name="Año y lugar")
    label(t, t.track("text", "Título"), "CASO SIN RESOLVER", 1.6, 6.4, Box(0, 410, 1920, 200), "Cinzel", 140, "#FFFFFF",
          weight=700, spacing=8, layers=[shadow("#000000", 0, 6, 24, 0.9), fill("#F5F0E6")],
          anim_in=tanim("blur-in", duration=1.2, blur=20), anim_loop=tanim("flicker", intensity=0.15, speed=4),
          name="Título")
    line(t, t.track("shape", "Línea"), RED, 2.6, 5.4, centered(960, 640, 520, 4), grow="c", length=0.8)
    label(t, t.track("text", "Sub"), "treinta años después, seguimos sin respuestas", 3.0, 5.0, Box(0, 670, 1920, 70),
          "Libre Baskerville", 40, "#D9D2C3", weight=400, italic=True, anim_in=tanim("fade", duration=0.8), name="Subtítulo")
    t.adjust([effect("super8_film", intensity=0.45, grain=0.5, scratches=0.3, weave=0.15, flicker=0.25),
              effect("stylize.vignette", amount=0.8, softness=0.9)], name="Película")
    music(t, "cursed-intro", 10, 0.75)
    return t


def mist_sin_resolver_vertical():
    t = _t(tall, "yt-mist-sin-resolver-vertical", "Sin resolver vertical", "Unsolved, vertical", 49,
           MIST + ["caso sin resolver", "vertical", "short", "parte 1"], 8.0, thumb_at=4.6, background="#000000")
    t.photo(t.track("video", "Foto"), "y6-house-01", 0, 8.0, t.full, kb(8.0, 1.1, 1.0), label="Foto del lugar",
            effects=[effect("color.basic", saturation=-0.6, contrast=0.2), effect("duotone", strength=0.5,
                                                                                   shadowColor="#05080c",
                                                                                   highlightColor="#c9b98f")])
    shade_top(t, 700, 0.85)
    shade_bottom(t, 700, 0.85)
    label(t, t.track("text", "Caso"), "CASO N.º 1187", 0.3, 7.7, Box(60, 160, 960, 90), "Special Elite", 62, "#D9D2C3",
          weight=400, spacing=6, anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name="Caso")
    paper(t, Box(110, 330, 860, 380), 1.2, rotation=-5, colour=MANILA, motion=[(0, {"s": 1.4}, "snap"), (0.25, {})],
          name="Etiqueta")
    label(t, t.track("text", "Título"), "SIN\nRESOLVER", 1.3, 6.7, Box(110, 330, 860, 380), "Black Ops One", 150, RED,
          weight=400, line=0.95, rotation=rot(-5), anim_in=tanim("stamp", duration=0.25), name="Título")
    label(t, t.track("text", "Parte"), "PARTE 1", 2.4, 5.6, centered(540, 1500, 340, 90), "Special Elite", 52, "#111111",
          weight=400, box_bg=("#D9D2C3", 1.0), box_pad=16, box_radius=4, anim_in=tanim("fade", duration=0.4), name="Parte")
    label(t, t.track("text", "Pie"), "¿tienes una teoría?\ncomenta abajo 👇", 3.0, 5.0, Box(60, 1600, 960, 200),
          "Special Elite", 52, "#FFFFFF", weight=400, line=1.3, anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03),
          name="Pie")
    t.adjust([effect("super8_film", intensity=0.4, grain=0.5, scratches=0.25, weave=0.1, flicker=0.3)], name="Película")
    music(t, "horroriffic", 30, 0.7)
    return t


def mist_se_busca():
    t = _t(tall, "yt-mist-se-busca", "Se busca información", "Seeking information poster", 50,
           MIST + ["se busca", "desaparecida", "cartel", "missing"], 8.0, thumb_at=6.6, background="#1A1A1A")
    bg_gradient(t, [(0, "#2A2622"), (1, "#121110")], angle=90)
    poster = Box(80, 100, 920, 1720)
    mo = [(0, {"dy": 40, "s": 1.04}, "out"), (0.6, {})]
    t.solid(t.track("shape", "Cartel"), "#F3EEE2", 0, 8.0, poster, mo, radius=2, kind="rectangle",
            layers=[shadow("#000000", 0, 16, 40, 0.6), fill("#F3EEE2"), no_stroke()], rotation=rot(1.2))
    for (x, y, a) in ((120, 110, -30), (960, 110, 30), (120, 1810, 30), (960, 1810, -30)):
        t.solid(t.track("shape", "Cinta"), "#E8DFC0", 0.4, 7.6, centered(x, y, 180, 50), pop(0, 0.3), alpha=0.75,
                rotation=rot(a))
    label(t, t.track("text", "Título"), "SE BUSCA\nINFORMACIÓN", 0.5, 7.5, Box(120, 160, 840, 330), "Bebas Neue", 170,
          INK_T, weight=400, line=0.92, rotation=rot(1.2), anim_in=tanim("stamp", duration=0.3), name="Título")
    t.photo(t.track("video", "Foto"), "y6-oldphoto-05", 0.8, 7.2, Box(200, 520, 680, 760), pop(0, 0.4, 0.8),
            label="Foto de la persona", rotation=rot(1.2), effects=[effect("color.basic", saturation=-1.0, contrast=0.1)])
    typed(t, "Elena Varga, 24 años", Box(130, 1320, 820, 90), 1.6, 0.9, size=62, align="center", name="Nombre")
    typed(t, "Vista por última vez el 14 de marzo\nen la estación de Valle Hondo.", Box(110, 1415, 860, 190), 2.3, 2.2,
          size=36, align="center", line_h=1.3, name="Detalles")
    t.solid(t.track("shape", "Raya"), INK_T, 4.2, 3.8, Box(200, 1610, 680, 4), [(0, {"sx": 0.0}, "out"), (0.5, {})])
    label(t, t.track("text", "Contacto"), "Si sabes algo: 555 012 345", 4.4, 3.6, Box(130, 1640, 820, 100), "Bebas Neue", 76,
          RED, weight=400, rotation=rot(1.2), anim_in=tanim("fade", duration=0.4), name="Contacto")
    t.solid(t.track("shape", "Luz"), "#FFF2CC", 0, 8.0, blendMode="soft-light",
            opacity=keys([(0, 0.0), (0.5, 0.35), (1.0, 0.1), (1.1, 0.35), (4.0, 0.3), (4.1, 0.05), (4.2, 0.35)]))
    mood(t, 0.2, 0.75)
    music(t, "isolation-waltz", 10, 0.65)
    return t


def mist_perfil():
    t = _t(wide, "yt-mist-perfil", "Perfil de la persona clave", "Key person profile", 51,
           MIST + ["perfil", "dossier", "persona clave", "profile"], 10.0, thumb_at=7.0, background="#14181D")
    bg_gradient(t, [(0, "#1D242C"), (1, "#0D1013")], angle=135)
    grid_bg(t, None, "#9FB3C8", step=60, alpha=0.05)
    framed(t, "y6-oldphoto-04", 0.3, 9.7, Box(140, 150, 560, 720), [(0, {"dx": -700}, "out"), (0.6, {})], border=12,
           colour="#E5E0D5", radius=2, rotation=rot(-2), label="Foto de la persona", shadow_alpha=0.6)
    t.tracks[-1].clips[-1]["effects"] = [effect("color.basic", saturation=-1.0, contrast=0.2)]
    for (x, y) in ((140, 150), (700, 150), (140, 870), (700, 870)):
        outline(t, t.track("shape", "Esquina"), "#E5484D", 4, 0.9, 9.1, centered(x, y, 60, 60), pop(0, 0.3))
    label(t, t.track("text", "Tipo"), "PERFIL", 0.6, 9.4, Box(820, 120, 900, 70), "Special Elite", 46, "#E5484D", weight=400,
          align="left", spacing=12, anim_in=tanim("fade", duration=0.4), name="Tipo")
    label(t, t.track("text", "Nombre"), "Tomás Ibarra", 0.8, 9.2, Box(820, 165, 1000, 175), "Bebas Neue", 140, "#FFFFFF",
          weight=400, align="left", anim_in=tanim("wipe", duration=0.6, angle=0), name="Nombre")
    rows = [("EDAD", "31 años"), ("OCUPACIÓN", "guardabosques"), ("RELACIÓN", "hermano de Elena"),
            ("COARTADA", "estaba en el pueblo… ¿o no?")]
    for i, (k, v) in enumerate(rows):
        at = 1.8 + i * 0.9
        y = 380 + i * 120
        label(t, t.track("text", "Campo"), k, at, 10.0 - at, Box(822, y, 330, 60), "Special Elite", 34, "#9FB3C8", weight=400,
              align="left", spacing=4, anim_in=tanim("fade", duration=0.3), name=f"Campo {i + 1}")
        typed(t, v, Box(1160, y - 4, 700, 70), at + 0.1, 0.7, size=44, colour="#F2EDE2", name=f"Dato {i + 1}")
        t.solid(t.track("shape", "Raya"), "#9FB3C8", at, 10.0 - at, Box(822, y + 76, 1000, 2), alpha=0.25)
    stamp(t, "PERSONA CLAVE", Box(1120, 880, 680, 110), 6.0, colour="#E5484D", size=58, angle=-6)
    mood(t, 0.15, 0.6)
    music(t, "hidden-truth", 60, 0.7)
    return t


def mist_evidencia():
    t = _t(wide, "yt-mist-evidencia", "Las evidencias", "The evidence", 52,
           MIST + ["evidencias", "pruebas", "evidence", "marcadores"], 10.0, thumb_at=7.6, background="#0F1012")
    bg(t, "#0F1012")
    t.solid(t.track("shape", "Foco"), "#FFFFFF", 0, 10.0, centered(960, 560, 2000, 1300), kind="ellipse",
            layers=[{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                     "paint": {"kind": "gradient", "color": "#33ffffff",
                               "gradient": {"kind": "radial", "stops": [{"pos": 0, "color": "#2effffff"},
                                                                        {"pos": 1, "color": "#00ffffff"}],
                                            "angle": 0, "space": "block"}}}, no_stroke()])
    label(t, t.track("text", "Título"), "LAS EVIDENCIAS", 0.2, 9.8, Box(0, 40, 1920, 120), "Bebas Neue", 120, "#FFFFFF",
          weight=400, spacing=12, anim_in=tanim("blur-in", duration=0.7), name="Título")
    items = [("y6-h-desk-02", "Nota sin firma"), ("y6-h-street-04", "Huella de neumático"), ("y6-oldphoto-06", "Foto rota")]
    for i, (s, cap) in enumerate(items):
        at = 1.0 + i * 1.8
        box = Box(130 + i * 580, 260, 500, 560)
        rot_a = (-3, 2, -1)[i]
        mo = [(0, {"dy": -60, "s": 1.08}, "out"), (0.4, {})]
        t.solid(t.track("shape", "Bolsa"), "#FFFFFF", at, 10.0 - at, Box(box.x - 24, box.y - 70, box.w + 48, box.h + 100), mo,
                radius=10, kind="rounded-rectangle", rotation=rot(rot_a),
                layers=[shadow("#000000", 0, 14, 30, 0.6), fill("#DCE3E8", 0.18), stroke(3, "#FFFFFF", 0.45)])
        t.photo(t.track("video", "Evidencia"), s, at, 10.0 - at, box, mo, label=f"Evidencia {i + 1}", rotation=rot(rot_a),
                effects=[effect("color.basic", saturation=-0.5, contrast=0.1)])
        t.solid(t.track("shape", "Brillo"), "#FFFFFF", at, 10.0 - at, box, mo, rotation=rot(rot_a),
                layers=[gradient([(0, "#FFFFFF", 0.22), (0.4, "#FFFFFF", 0.0), (1, "#FFFFFF", 0.06)], angle=135), no_stroke()])
        t.solid(t.track("shape", "Cierre"), RED, at, 10.0 - at, Box(box.x - 24, box.y - 66, box.w + 48, 46), mo,
                rotation=rot(rot_a))
        label(t, t.track("text", "Cierre"), f"EVIDENCIA N.º {12 + i}", at, 10.0 - at, Box(box.x - 24, box.y - 66, box.w + 48, 46),
              "Special Elite", 30, "#FFFFFF", weight=400, spacing=4, motion=mo, rotation=rot(rot_a), name=f"Número {i + 1}")
        tent = Box(box.x + box.w - 70, box.y + box.h - 40, 120, 110)
        t.solid(t.track("shape", "Marcador"), "#FACC15", at + 0.4, 9.6 - at, tent, pop(0, 0.3), kind="triangle",
                layers=[shadow("#000000", 0, 8, 12, 0.6), fill("#FACC15"), stroke(3, "#111111")])
        label(t, t.track("text", "Marcador"), str(i + 1), at + 0.4, 9.6 - at, Box(tent.x, tent.y + 30, tent.w, 80), "Bebas Neue",
              64, "#111111", weight=400, motion=pop(0, 0.3), editable=False)
        typed(t, cap, Box(box.x - 20, 900, box.w + 40, 80), at + 0.5, 0.6, size=40, colour="#E8E2D4", align="center",
              name=f"Descripción {i + 1}")
        flash(t, at, 0.18, peak=0.7)
    mood(t, 0.2, 0.7)
    music(t, "dark-hallway", 20, 0.7)
    return t


def mist_podcast():
    t = _t(wide, "yt-mist-podcast", "Intro de podcast de misterio", "Mystery podcast intro", 53,
           MIST + ["podcast", "episodio", "intro", "presentador"], 8.0, thumb_at=5.0, background="#0B0B0D")
    bg(t, "#0B0B0D")
    t.photo(t.track("video", "Presentador"), "y6-h-host-04", 0, 8.0, Box(0, 0, 1000, 1080), kb(8.0, 1.06, 1.0),
            label="Tu foto (presentador)", effects=[effect("color.basic", saturation=-0.4, contrast=0.15)])
    t.solid(t.track("shape", "Fundido"), "#0B0B0D", 0, 8.0, Box(600, 0, 400, 1080),
            layers=[gradient([(0, "#0B0B0D", 0.0), (1, "#0B0B0D", 1.0)], angle=0), no_stroke()])
    label(t, t.track("text", "Episodio"), "EPISODIO 12", 0.6, 7.4, Box(1060, 200, 800, 70), "Special Elite", 48, RED,
          weight=400, align="left", spacing=10, anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name="Episodio")
    label(t, t.track("text", "Programa"), "EXPEDIENTES\nOCULTOS", 1.0, 7.0, Box(1060, 290, 840, 300), "Cinzel", 86,
          "#F2EDE2", weight=700, align="left", line=1.0, layers=[shadow("#000000", 0, 6, 20, 0.8), fill("#F2EDE2")],
          anim_in=tanim("blur-in", duration=1.0, blur=18), name="Programa")
    line(t, t.track("shape", "Línea"), RED, 1.8, 6.2, Box(1064, 620, 360, 5), length=0.6)
    label(t, t.track("text", "Tema"), "La casa del lago", 2.2, 5.8, Box(1060, 650, 840, 90), "Libre Baskerville", 60,
          "#D9D2C3", weight=400, italic=True, align="left", anim_in=tanim("fade", duration=0.6), name="Tema")
    rng = random.Random(6453)
    for k in range(24):
        x = 1064 + k * 32
        h = rng.uniform(30, 120)
        pts = [(0, {"sy": 0.1}, "smooth")]
        tt = 0.0
        while tt < 5.0:
            tt += rng.uniform(0.18, 0.35)
            pts.append((tt, {"sy": rng.uniform(0.15, 1.0)}, "smooth"))
        t.solid(t.track("shape", "Onda") if k % 12 == 0 else t.tracks[-1], RED if k % 5 == 0 else "#F2EDE2", 2.6, 5.4,
                centered(x, 880, 14, h), pts, radius=7, kind="rounded-rectangle", alpha=0.85)
    mood(t, 0.18, 0.6)
    music(t, "hidden-truth", 70, 0.75)
    return t


def mist_teorias():
    t = _t(tall, "yt-mist-teorias", "Tres teorías", "Three theories", 54,
           MIST + ["teorías", "hipótesis", "theories", "short"], 10.0, thumb_at=4.6, background="#1B1612")
    desk_bg(t)
    label(t, t.track("text", "Título"), "3 TEORÍAS", 0.2, 9.8, Box(60, 110, 960, 170), "Bebas Neue", 170, "#F2EDE2",
          weight=400, spacing=8, anim_in=tanim("stamp", duration=0.3), name="Título")
    theories = [("TEORÍA #1", "Se fue por su cuenta", "y6-h-street-02", -3),
                ("TEORÍA #2", "Alguien la esperaba en el lago", "y6-fog-03", 2),
                ("TEORÍA #3", "Nunca salió de la casa", "y6-house-02", -1)]
    for i, (k, v, s, a) in enumerate(theories):
        at = 0.6 + i * 3.0
        d = 10.0 - at
        flip = [(0, {"sx": 0.02}, "out"), (0.45, {})]
        card = Box(120, 360, 840, 1300)
        paper(t, card, at, d, colour="#F3EEE2", motion=flip, rotation=a, name="Tarjeta")
        t.photo(t.track("video", "Foto"), s, at, d, Box(180, 420, 720, 760), flip, label=f"Foto teoría {i + 1}",
                rotation=rot(a), effects=[effect("color.basic", saturation=-0.7, contrast=0.15)])
        label(t, t.track("text", "Teoría"), k, at + 0.3, d - 0.3, Box(160, 1210, 760, 120), "Permanent Marker", 96, RED,
              weight=400, rotation=rot(a), anim_in=tanim("pop", duration=0.3), name=f"Etiqueta {i + 1}")
        label(t, t.track("text", "Teoría"), v, at + 0.5, d - 0.5, Box(170, 1340, 740, 260), "Special Elite", 58, INK_T,
              weight=400, line=1.15, rotation=rot(a), anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03),
              name=f"Teoría {i + 1}")
    label(t, t.track("text", "Pie"), "¿cuál crees tú? 👇", 7.4, 2.6, Box(60, 1720, 960, 110), "Permanent Marker", 72,
          "#F2EDE2", weight=400, anim_in=tanim("fade", duration=0.4), name="Pie")
    mood(t, 0.2, 0.7)
    music(t, "alien-invasion", 40, 0.7)
    return t


def mist_periodico():
    t = _t(wide, "yt-mist-periodico", "Recorte de periódico", "Newspaper clipping", 55,
           MIST + ["periódico", "noticia", "newspaper", "titular"], 10.0, thumb_at=6.8, background="#1B1612")
    desk_bg(t)
    page = Box(160, 40, 1600, 1000)
    mo = [(0, {"dy": 900}, "out"), (0.7, {})]
    t.solid(t.track("shape", "Página"), "#E8E1D0", 0, 10.0, page, mo, rotation=rot(-1),
            layers=[shadow("#000000", 0, 16, 40, 0.6), fill("#E8E1D0"), no_stroke()])
    label(t, t.track("text", "Cabecera"), "El Diario de la Tarde", 0.5, 9.5, Box(220, 70, 1480, 130), "Bodoni Moda", 104,
          "#1A1714", weight=700, italic=True, rotation=rot(-1), motion=mo, name="Periódico")
    for y in (210, 270):
        t.solid(t.track("shape", "Filete"), "#1A1714", 0.0, 10.0, Box(220, y, 1480, 3), mo, rotation=rot(-1))
    label(t, t.track("text", "Fecha"), "MARTES 15 DE MARZO DE 1996  ·  EDICIÓN VESPERTINA", 0.6, 9.4, Box(220, 214, 1480, 56),
          "Libre Baskerville", 30, "#3A342C", weight=400, spacing=3, rotation=rot(-1), motion=mo, name="Fecha")
    label(t, t.track("text", "Titular"), "MISTERIOSA DESAPARICIÓN EN VALLE HONDO", 1.2, 8.8, Box(220, 290, 1480, 230),
          "Bodoni Moda", 92, "#111111", weight=900, line=1.0, rotation=rot(-1),
          anim_in=tanim("fade-up-char", duration=0.8, unit="word", stagger=0.08), name="Titular")
    t.photo(t.track("video", "Foto"), "y6-h-house-03", 1.6, 8.4, Box(240, 550, 700, 440), label="Foto de la noticia",
            rotation=rot(-1), effects=[effect("color.basic", saturation=-1.0, contrast=0.3, fade=0.15)])
    rng = random.Random(6455)
    for col in range(2):
        tr = t.track("shape", "Texto")
        for k in range(10):
            w = 340 if k < 9 else rng.uniform(140, 260)
            t.solid(tr, "#5A5246", 1.8, 8.2, Box(990 + col * 370, 565 + k * 42, w, 14), alpha=0.55, rotation=rot(-1))
    # A yellow marker sweeps over the headline, a red ring goes round the photo.
    t.solid(t.track("shape", "Marcador"), "#FFE14D", 4.0, 6.0, Box(230, 410, 1300, 100),
            [(0, {"sx": 0.0, "dx": -650}, "inout"), (0.8, {})], alpha=0.45, blendMode="multiply", rotation=rot(-1))
    ring(t, t.track("shape", "Círculo"), RED, 8, 5.4, 4.6, centered(590, 770, 620, 520), pop(0, 0.4), rotation=rot(-4))
    label(t, t.track("text", "Nota"), "¡¿la misma casa?!", 6.0, 4.0, Box(980, 920, 700, 100), "Permanent Marker", 64, RED,
          weight=400, rotation=rot(-4), anim_in=tanim("wipe", duration=0.6, angle=0), name="Nota")
    mood(t, 0.22, 0.7)
    music(t, "isolation-waltz", 40, 0.65)
    return t


def mist_testigo():
    t = _t(tall, "yt-mist-testigo", "Declaración del testigo", "Witness statement", 56,
           MIST + ["testigo", "declaración", "witness", "cita"], 10.0, thumb_at=6.8, background="#08090B")
    bg(t, "#08090B")
    t.photo(t.track("video", "Testigo"), "y6-shadow-01", 0, 10.0, Box(0, 0, 1080, 1100), kb(10.0, 1.0, 1.08),
            label="Testigo (silueta)", effects=[effect("color.basic", exposure=-0.2, contrast=0.2)])
    t.solid(t.track("shape", "Fundido"), "#08090B", 0, 10.0, Box(0, 700, 1080, 420),
            layers=[gradient([(0, "#08090B", 0.0), (1, "#08090B", 1.0)], angle=90), no_stroke()])
    pill(t, t.track("shape", "Rec"), "#000000", 0.3, 9.7, Box(60, 70, 420, 80), alpha=0.7)
    t.solid(t.track("shape", "Rec"), "#FF2D2D", 0.3, 9.7, centered(105, 110, 28, 28), kind="ellipse", opacity=blink(9.7, 1.0, 0.15))
    count_fn(t, t.track("text", "Rec"), lambda f: 14 + 9.4 * f, lambda v: f"REC 00:{int(v):02d}", 0.3, 9.4, "REC 00:23",
             Box(140, 70, 330, 80), big("VT323", 56, "#FFFFFF", weight=400, align="left"), step=30, name="Grabación")
    label(t, t.track("text", "Etiqueta"), "DECLARACIÓN DEL TESTIGO", 0.6, 9.4, Box(60, 1140, 960, 70), "Special Elite", 46,
          RED, weight=400, spacing=4, anim_in=tanim("fade", duration=0.4), name="Etiqueta")
    typed(t, "«Vi una luz en la casa del lago… y después, nada.»", Box(60, 1240, 960, 380), 1.2, 3.6, size=68,
          colour="#F2EDE2", align="left", line_h=1.25, caret=True, name="Cita")
    label(t, t.track("text", "Quién"), "— testigo anónimo, 2019", 5.4, 4.6, Box(60, 1640, 960, 70), "Special Elite", 44,
          "#9A9387", weight=400, align="right", anim_in=tanim("fade", duration=0.5), name="Quién")
    rng = random.Random(6456)
    tr = t.track("shape", "Onda")
    for k in range(30):
        if k % 15 == 14:
            tr = t.track("shape", "Onda")
        pts = [(0, {"sy": 0.2}, "smooth")]
        tt = 0.0
        while tt < 9.0:
            tt += rng.uniform(0.15, 0.3)
            pts.append((tt, {"sy": rng.uniform(0.1, 1.0) if 1.2 < tt < 4.8 else 0.12}, "smooth"))
        t.solid(tr, "#F2EDE2", 0.6, 9.4, centered(105 + k * 30, 1800, 12, 90), pts, radius=6, kind="rounded-rectangle",
                alpha=0.6)
    mood(t, 0.22, 0.6)
    music(t, "dark-hallway", 12, 0.7)
    return t


def mist_camara():
    t = _t(wide, "yt-mist-camara", "Cámara de seguridad", "Security camera footage", 57,
           MIST + ["cámara de seguridad", "cctv", "grabación", "pista"], 8.0, thumb_at=5.6, background="#000000")
    t.photo(t.track("video", "Cámara"), "y6-h-street-02", 0, 8.0, t.full, kb(8.0, 1.0, 1.04), label="Tu grabación",
            effects=[effect("color.basic", saturation=-1.0, contrast=0.25, exposure=0.1)])
    t.adjust([effect("duotone", strength=0.35, shadowColor="#020a05", highlightColor="#c8f0d0", contrast=0.5),
              effect("stylize.vhs", noise=30, chroma=2, saturation=0.6),
              effect("stylize.film_grain", amount=0.35, grainSize=2.2)], name="Vigilancia")
    hud = "#E8F5E9"
    label(t, t.track("text", "Cámara"), "CAM 03 · ENTRADA", 0, 8.0, Box(60, 40, 800, 80), "VT323", 72, hud, weight=400,
          align="left", name="Cámara")
    t.solid(t.track("shape", "Rec"), "#FF2D2D", 0, 8.0, centered(1690, 80, 30, 30), kind="ellipse", opacity=blink(8.0, 1.0, 0.1))
    label(t, t.track("text", "Rec"), "REC", 0, 8.0, Box(1720, 40, 160, 80), "VT323", 72, hud, weight=400, align="left",
          editable=False)
    for (x, y, sx, sy) in ((40, 30, 1, 1), (1880, 30, -1, 1), (40, 1050, 1, -1), (1880, 1050, -1, -1)):
        t.solid(t.track("shape", "Esquina"), hud, 0, 8.0, Box(x if sx > 0 else x - 80, y if sy > 0 else y - 6, 80, 6))
        t.solid(t.track("shape", "Esquina"), hud, 0, 8.0, Box(x if sx > 0 else x - 6, y if sy > 0 else y - 80, 6, 80))
    tr = t.track("text", "Hora")
    for k in range(8):
        txt = f"14/03/1996  23:47:{12 + k:02d}"
        if k < 7:
            t.text(tr, txt, k, 1.0, Box(60, 960, 900, 80), text_style("VT323", 66, [fill(hud)], weight=400, align="left"),
                   editable=False, name="Hora")
        else:
            t.text(tr, txt, k, 1.0, Box(60, 960, 900, 80), text_style("VT323", 66, [fill(hud)], weight=400, align="left"),
                   label="Fecha y hora")
    ring(t, t.track("shape", "Señal"), "#FF2D2D", 8, 3.6, 4.4, centered(1240, 560, 260, 260),
         [(0, {"s": 2.2}, "snap"), (0.3, {})], opacity=blink(4.4, 0.8, 0.5))
    label(t, t.track("text", "Pregunta"), "¿QUIÉN ES?", 3.9, 4.1, Box(1380, 380, 480, 110), "VT323", 96, "#FF2D2D",
          weight=400, align="left", anim_in=tanim("typewriter", duration=0.05, unit="character", stagger=0.03), name="Pregunta")
    t.adjust([effect("zoom_pulse", centerX=0.645, centerY=0.52, animated={"punch": spike([3.6], 0.35, 0.4)}),
              effect("digital_glitch", intensity=0.0, rgbAmount=6,
                     animated={"intensity": spike([1.2, 3.55, 6.3], 0.8, 0.2)})], name="Golpe")
    music(t, "cursed-intro", 30, 0.7)
    return t


MISTERIO = [mist_expediente, mist_tablero, mist_tablero_vertical, mist_maquina, mist_censurado, mist_linea_tiempo,
            mist_linea_vertical, mist_mapa, mist_sin_resolver, mist_sin_resolver_vertical, mist_se_busca, mist_perfil,
            mist_evidencia, mist_podcast, mist_teorias, mist_periodico, mist_testigo, mist_camara]

TEMPLATES = GAMING + COCINA + MISTERIO
