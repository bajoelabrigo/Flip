"""Counters (2026-10-17): money, followers, days, likes, percentages, timers, scores and odometers.
Category `counter` (es «Contadores», en "Counters"); order 5300-5399; ids `cont-*`.

Since 0.18 a number counts with the engine's animated counter: one editable text clip, «Número final», whose
style has `counter: true`, `counterFrom` (the first value) and `counterSeconds` (how long the count takes, so
flashes and bursts land with it); it eases out (cubic) and then holds. Change the final number and the count
follows. An older app shows the final number still (0.17: counting, landing at 85 % of the clip). Where the
pace is not an ease-out (the loading bar's stalls, a match clock) `cuts=True` keeps the old way: quick
successive text clips, one per value, and only the last one editable. Odometers roll digit strips (one multi-line text
per column) under plates of the background colour that leave a window open: masks are measured on their
host clip's box and would travel with the strip. When a strip stops, a flash hands over to the editable
final number.
"""

from __future__ import annotations

import re

from kit import (Box, bg, bg_gradient, centered, circle_photo, confetti, dots, effect, fill, flash, glow, gradient,
                 grain, keys, kb, label, line, no_stroke, photo_bg, pill, pop, random, rrect, shade_bottom, shade_full,
                 shade_top, shadow, song, spike, stroke, tall, tanim, text_style, vignette, wide)

O = 5300
FPS = 30
CAT = "counter"
BASE_TAGS = ["contador", "números", "counter", "conteo"]


def _t(maker, id, es, en, order, tags, duration, **kw):
    return maker(id, es, en, CAT, duration, order=O + order, tags=BASE_TAGS + tags, **kw)


def geo(clip: dict, **geometry) -> dict:
    """Shape geometry (points, innerRatio, tailX...) lives in the shapeStyle, not on the clip."""
    clip["shapeStyle"].update(geometry)
    return clip


def hollow_ring(colour: str, width: float, alpha: float = 1.0, trim: float | None = None) -> list:
    a = f"#{max(0, min(255, round(alpha * 255))):02x}{colour.lstrip('#').lower()}"
    st = {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "inside",
          "paint": {"kind": "solid", "color": a}, "opacity": 1.0}
    if trim is not None:
        st.update(trimStart=0.0, trimEnd=trim)
    return [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}, st]


# --- counting -------------------------------------------------------------------------------------

def thousands(v: float, decimals: int = 0) -> str:
    """1234567 -> '1.234.567'; with decimals the comma is the decimal mark ('42,2')."""
    s = f"{v:,.{decimals}f}"
    return s.replace(",", "#").replace(".", ",").replace("#", ".")


def ease_out(f: float, power: float = 3.0) -> float:
    return 1 - (1 - f) ** power


def smooth(f: float) -> float:
    f = max(0.0, min(1.0, f))
    return f * f * (3 - 2 * f)


def first_number(text: str) -> float:
    """The first number of a sample text, read as the templates write it ('1.000.000', '42,195', '0%')."""
    m = re.search(r"[0-9][0-9.,]*[0-9]|[0-9]", text)
    if not m:
        return 0.0
    return float(m.group(0).replace(".", "").replace(",", "."))


def landing_pop(size: int, at: float) -> dict:
    """pixelSize keys: a quick swell when the count lands at `at` (clip seconds), like the old final clip's pop."""
    return {"pixelSize": keys([(0, size, "hold"), (at, size, "out"), (at + 0.12, size * 1.12, "inout"),
                               (at + 0.32, size)])}


def count_fn(t, track, fn, fmt, t0: float, length: float, final: str, box: Box, style, *, step: int = 2,
             final_style=None, end: float | None = None, name: str = "Número final", motion=None, final_motion=None,
             cuts: bool = False, **extra) -> dict:
    """Counts from fmt(fn(0)) to `final` over `length` seconds from t0 and holds it until `end`: one editable
    text clip with the engine's counter (fn only gives the first value), or with cuts=True, fmt(fn(f)) as a new
    clip every `step` frames (equal values merge into one clip) and then `final`, the editable one."""
    end = t.duration if end is None else end
    if not cuts:
        st = (final_style or style)()
        st.update(counter=True, counterFrom=first_number(fmt(fn(0.0))), counterSeconds=round(length, 3))
        st["keyframes"] = {**st.get("keyframes", {}), **landing_pop(st["pixelSize"], length)}
        return t.text(track, final, t0, end - t0, box, st, final_motion or motion, label=name, **extra)
    frames = max(1, round(length * FPS))
    start_f = round(t0 * FPS)
    shown: list[tuple[int, str]] = []
    for k in range(0, frames, step):
        s = fmt(fn(k / frames))
        if s == final and k:
            break
        if not shown or shown[-1][1] != s:
            shown.append((start_f + k, s))
    stop_f = start_f + frames
    for i, (f0, s) in enumerate(shown):
        f1 = shown[i + 1][0] if i + 1 < len(shown) else stop_f
        if f1 > f0:
            t.text(track, s, f0 / FPS, (f1 - f0) / FPS, box, style(), motion, editable=False, name="Contando", **extra)
    return t.text(track, final, stop_f / FPS, end - stop_f / FPS, box, (final_style or style)(), final_motion,
                  label=name, **extra)


def count_up(t, track, start: float, final_value: float, final: str, t0: float, length: float, box: Box, style, *,
             power: float = 3.0, decimals: int = 0, prefix: str = "", suffix: str = "", **kw) -> dict:
    fn = lambda f: start + (final_value - start) * ease_out(f, power)  # noqa: E731
    fmt = lambda v: f"{prefix}{thousands(round(v, decimals), decimals)}{suffix}"  # noqa: E731
    return count_fn(t, track, fn, fmt, t0, length, final, box, style, **kw)


def curve_motion(fn, length: float, w: float, at: float = 0.0, steps: int = 24) -> list:
    """A bar (box width w, growing from its left edge) whose filled fraction is fn(f), f 0 -> 1 over length."""
    pts = [(0, {"sx": 0.0001, "dx": -w / 2}, "hold")] if at > 0 else []
    for k in range(steps + 1):
        frac = max(0.0001, fn(k / steps))
        pts.append((at + length * k / steps, {"sx": frac, "dx": -w * (1 - frac) / 2}))
    return pts


def curve_keys(fn, length: float, at: float = 0.0, steps: int = 24, scale: float = 1.0) -> dict:
    pts = [(0, fn(0) * scale, "hold")] if at > 0 else []
    pts += [(at + length * k / steps, fn(k / steps) * scale) for k in range(steps + 1)]
    return keys(pts)


def group(motion: list, ox: float, oy: float) -> list:
    """The same motion for a part whose centre is (ox, oy) from the group's centre: scaling about the group."""
    out = []
    for p in motion:
        m = dict(p[1])
        sx = m.get("sx", m.get("s", 1.0))
        sy = m.get("sy", m.get("s", 1.0))
        m["dx"] = m.get("dx", 0.0) + ox * (sx - 1)
        m["dy"] = m.get("dy", 0.0) + oy * (sy - 1)
        out.append((p[0], m) + tuple(p[2:]))
    return out


def big(font: str, size: int, colour: str, *, weight: int = 900, layers=None, **kw):
    return lambda: text_style(font, size, layers or [fill(colour)], weight=weight, **kw)


# --- odometers -------------------------------------------------------------------------------------

# Line pitch (x pixelSize at lineHeight 1) and the first digit's centre (x pixelSize from the box top),
# measured on renders of a 0-9 column (2026-10-17).
FONT_K = {"Oswald": (1.483, 0.785), "Bebas Neue": (1.30, 0.60), "Anton": (1.506, 0.75), "Teko": (1.433, 0.645)}


def odometer(t, digits: str, t0: float, length: float, x: float, cy: float, cw: float, ch: float, font: str,
             size: int, colour: str, *, swap_at: float, stagger: float = 0.18, weight: int = 400, layers=None,
             name: str = "Rodillo"):
    """One rolling strip per digit; window i is (x + i*cw, cy - ch/2, cw, ch). The strips must be hidden
    outside the windows by shapes drawn above them. The last column spins one extra turn and stops last."""
    k, c = FONT_K[font]
    n = len(digits)
    for i, d in enumerate(digits):
        target = int(d)
        spins = 1 if i >= n - 2 else 0
        seq = [str(j % 10) for j in range(spins * 10 + target + 1)]
        box = Box(x + i * cw, cy - c * size, cw, ch * (len(seq) + 1))
        style = text_style(font, size, layers or [fill(colour)], weight=weight, valign="top", line=ch / (k * size))
        stop = length - (n - 1 - i) * stagger
        travel = ch * (len(seq) - 1)
        t.text(t.track("text", name), "\n".join(seq), t0, swap_at - t0, box, style,
               [(0, {}, "inout"), (stop, {"dy": -travel})], editable=False, name=name)


def plates(t, colour: str, window: Box, t0: float = 0.0, dur: float | None = None, layers=None):
    """Four shapes of the background colour around `window` (hide what rolls outside it)."""
    W_, H_ = t.w, t.h
    for b in (Box(0, 0, W_, window.y), Box(0, window.y + window.h, W_, H_ - window.y - window.h),
              Box(0, window.y, window.x, window.h), Box(window.x + window.w, window.y, W_ - window.x - window.w, window.h)):
        t.solid(t.track("shape", "Tapa"), colour, t0, dur, b, layers=layers)


# --- decorations -------------------------------------------------------------------------------------

def burst(t, colour: str, at: float, box: Box, *, points: int = 14, peak: float = 0.9, length: float = 0.8,
          track=None, inner: float = 0.6):
    """A star burst that blows up behind a number and fades."""
    track = track or t.track("shape", "Estallido")
    clip = t.solid(track, colour, at, length, box, [(0, {"s": 0.2}, "out"), (length, {"s": 1.2})], kind="burst",
                   opacity=keys([(0, peak, "linear"), (length * 0.4, peak, "in"), (length, 0.0)]))
    geo(clip, points=points, innerRatio=inner)
    return track


def rays(t, colour: str, t0: float, dur: float, box: Box, alpha: float = 0.25, points: int = 18, speed: float = 25):
    """A slowly turning star of light rays behind a hero number."""
    clip = t.solid(t.track("shape", "Rayos"), colour, t0, dur, box, [(0, {"s": 0.0}, "out"), (0.6, {})], kind="burst",
                   alpha=alpha, rotation=keys([(0, 0), (dur, speed * dur)]))
    geo(clip, points=points, innerRatio=0.15)


def bills(t, t0: float, dur: float, seed: int, lanes: int = 2, every: float = 0.7):
    """Green notes that tumble down the frame."""
    rng = random.Random(seed)
    for lane in range(lanes):
        track = t.track("shape", "Billetes")
        start = t0 + lane * every / lanes
        while start < t0 + dur - 0.5:
            fall = rng.uniform(2.6, 3.8)
            d = min(fall, t0 + dur - start)
            w = rng.uniform(130, 170)
            t.solid(track, "#2E7D32", start, d, centered(rng.uniform(40, t.w - 40), -120, w, w * 0.48),
                    [(0, {}, "linear"), (fall, {"dy": t.h + 260, "dx": rng.uniform(-160, 160)})],
                    kind="rounded-rectangle", radius=8,
                    layers=[fill(rng.choice(["#2E7D32", "#388E3C", "#43A047"])), stroke(5, "#A5D6A7", 0.9)],
                    rotation=keys([(0, rng.uniform(-40, 40)), (fall, rng.uniform(-300, 300))]),
                    opacity=keys([(0, 0.55)]))
            start += rng.uniform(every * 0.7, every * 1.3)


def hearts(t, colours, t0, dur, seed, n=14, area=None, size=(50, 110), drift=320):
    dots(t, colours, n, t0, dur, seed=seed, size=size, kinds=("heart",), drift=drift, area=area)


# --- 1. Money (9:16) ------------------------------------------------------------------------------

def dinero_millon():
    t = _t(tall, "cont-dinero-millon", "Contador de dinero", "Money counter", 0,
           ["dinero", "millón", "ventas", "meta", "money", "ganancias"], 7.0, thumb_at=5.4, background="#06210F")
    bg_gradient(t, [(0, "#0D4723"), (0.55, "#06210F"), (1, "#020A05")], angle=90)
    rays(t, "#FFD54F", 4.2, 2.8, centered(540, 1060, 1500, 1500), alpha=0.12)
    bills(t, 0.0, 7.0, seed=5301)
    shade_full(t, 0.3, colour="#02140A")
    label(t, t.track("text", "Antetítulo"), "VENTAS TOTALES", 0.3, 6.7, Box(60, 820, 960, 90), "Montserrat", 54,
          "#B8F5C8", weight=800, spacing=14, anim_in=tanim("fade", duration=0.5), name="Antetítulo")
    gold = lambda: [shadow("#000000", 0, 10, 26, 0.7), glow("#FFD54F", 30, 0.45),  # noqa: E731
                    gradient([(0, "#FFF6C2"), (0.5, "#FFD54F"), (1, "#E0A100")], angle=90)]
    burst(t, "#FFD54F", 4.2, centered(540, 1040, 1200, 1200), peak=0.35, length=0.9)
    count_up(t, t.track("text", "Contador"), 0, 1_000_000, "$1.000.000", 0.6, 3.6, Box(0, 920, 1080, 260),
             big("Anton", 210, "#FFD54F", weight=400, layers=gold()), prefix="$", power=3.2,
             final_style=big("Anton", 210, "#FFD54F", weight=400, layers=gold(),
                             anim_in=tanim("pop", duration=0.35, **{"from": 80}), anim_loop=tanim("pulse", amount=3, speed=1.0)))
    flash(t, 4.2, 0.35, colour="#FFF6C2", peak=0.55)
    label(t, t.track("text", "Mensaje"), "¡META CUMPLIDA!", 4.35, 2.65, Box(60, 1210, 960, 120), "Montserrat", 76,
          "#FFFFFF", weight=900, anim_in=tanim("pop", duration=0.4), name="Mensaje")
    song(t, "upbeat", 4, 0.85)
    return t


# --- 2. Followers 100K (9:16) -------------------------------------------------------------------------

def seguidores_100k():
    t = _t(tall, "cont-seguidores-100k", "100 mil seguidores", "100K followers", 1,
           ["seguidores", "100k", "hito", "gracias", "redes", "followers"], 7.0, thumb_at=5.3, background="#1B0B33")
    bg_gradient(t, [(0, "#FF5F6D"), (0.5, "#8E2DE2"), (1, "#2A0B4F")], angle=120)
    dots(t, ["#FFFFFF"], 22, 0, 7.0, seed=5302, size=(6, 16), drift=140)
    circle_photo(t, "selfie-03", 0.2, 6.8, centered(540, 560, 380, 380), pop(0, 0.5), ring_colour="#FFFFFF",
                 ring_width=12, label="Tu foto de perfil")
    burst(t, "#FFE66D", 4.1, centered(540, 1000, 900, 900), peak=0.25, length=0.8)
    count_up(t, t.track("text", "Contador"), 0, 100_000, "100.000", 0.8, 3.3, Box(0, 880, 1080, 240),
             big("Poppins", 200, "#FFFFFF", weight=800, layers=[shadow("#2A0B4F", 0, 10, 26, 0.6), fill("#FFFFFF")]),
             power=3.0, final_style=big("Poppins", 200, "#FFFFFF", weight=800,
                                        layers=[shadow("#2A0B4F", 0, 10, 26, 0.6), glow("#FFE66D", 30, 0.6), fill("#FFFFFF")],
                                        anim_in=tanim("pop", duration=0.4, **{"from": 70})))
    label(t, t.track("text", "Unidad"), "SEGUIDORES", 0.6, 6.4, Box(60, 1120, 960, 100), "Poppins", 64, "#FFE66D",
          weight=700, spacing=16, anim_in=tanim("fade", duration=0.5), name="Unidad")
    confetti(t, ["#FFE66D", "#FFFFFF", "#4ECDC4", "#FF5F6D"], 4.1, 2.9, seed=5302, lanes=4, density=0.22)
    label(t, t.track("text", "Mensaje"), "¡Gracias por tanto!", 4.4, 2.6, Box(60, 1300, 960, 120), "Pacifico", 90,
          "#FFFFFF", weight=400, layers=[shadow("#2A0B4F", 0, 6, 16, 0.6), fill("#FFFFFF")],
          anim_in=tanim("rise", duration=0.5), name="Mensaje")
    flash(t, 4.1, 0.25, peak=0.3)
    song(t, "upbeat", 0, 0.85)
    return t


# --- 3. Subscribers 1M (16:9) ------------------------------------------------------------------------

def suscriptores_millon():
    t = _t(wide, "cont-suscriptores-millon", "Un millón de suscriptores", "One million subscribers", 2,
           ["suscriptores", "millón", "canal", "hito", "celebración", "subscribers"], 7.0, thumb_at=5.4,
           background="#0E0E12")
    bg_gradient(t, [(0, "#1E1E28"), (1, "#0A0A0E")], angle=90)
    rays(t, "#FF8C42", 0.4, 6.6, centered(560, 540, 1300, 1300), alpha=0.1, speed=12)
    circle_photo(t, "h-portrait-05", 0.2, 6.8, centered(560, 540, 520, 520), pop(0, 0.5), ring_colour="#FF8C42",
                 ring_width=14, label="Tu foto de perfil")
    label(t, t.track("text", "Antetítulo"), "LLEGAMOS A", 0.5, 6.5, Box(940, 250, 900, 80), "Montserrat", 50, "#FF8C42",
          weight=800, spacing=14, align="left", anim_in=tanim("slide-right", duration=0.5, distance=0.15),
          name="Antetítulo")
    burst(t, "#FF8C42", 4.3, centered(1340, 520, 900, 900), peak=0.2, length=0.9)
    count_up(t, t.track("text", "Contador"), 0, 1_000_000, "1.000.000", 0.8, 3.5, Box(930, 360, 960, 240),
             big("Archivo Black", 150, "#FFFFFF", weight=400, align="left"), power=3.2,
             final_style=big("Archivo Black", 150, "#FFFFFF", weight=400, align="left",
                             layers=[glow("#FF8C42", 26, 0.6), fill("#FFFFFF")], anim_in=tanim("pop", duration=0.35)))
    label(t, t.track("text", "Unidad"), "suscriptores", 0.7, 6.3, Box(940, 600, 900, 110), "Montserrat", 76, "#FFFFFF",
          weight=500, align="left", anim_in=tanim("fade", duration=0.5), name="Unidad")
    line(t, t.track("shape", "Línea"), "#FF8C42", 4.3, 2.7, Box(944, 730, 520, 8), length=0.5)
    label(t, t.track("text", "Mensaje"), "¡GRACIAS A TODOS!", 4.5, 2.5, Box(940, 760, 900, 90), "Montserrat", 54,
          "#FF8C42", weight=900, spacing=4, align="left", anim_in=tanim("rise", duration=0.4), name="Mensaje")
    confetti(t, ["#FF8C42", "#FFFFFF", "#FFD23F"], 4.3, 2.7, seed=5303, lanes=3, density=0.25)
    flash(t, 4.3, 0.3, peak=0.5)
    song(t, "epic", 0, 0.85)
    return t


# --- 4. Day 1 -> Day 100 (9:16) ---------------------------------------------------------------------

def dias_100():
    t = _t(tall, "cont-dias-100", "Del día 1 al día 100", "Day 1 to day 100", 3,
           ["días", "reto", "100 días", "progreso", "constancia", "challenge"], 8.0, thumb_at=6.2, background="#000000")
    photo_bg(t, "gym-01", s1=1.12, label="Tu foto o video")
    shade_full(t, 0.25)
    shade_bottom(t, 1100, 0.85)
    label(t, t.track("text", "Reto"), "MI RETO", 0.3, 7.7, Box(60, 900, 960, 90), "Bebas Neue", 90, "#C6FF00", weight=400,
          spacing=14, anim_in=tanim("fade", duration=0.5), name="Reto")
    label(t, t.track("text", "Día"), "DÍA", 0.3, 7.7, Box(60, 990, 960, 150), "Bebas Neue", 160, "#FFFFFF", weight=400,
          spacing=10, anim_in=tanim("slide-up", duration=0.4), editable=False)
    num = lambda: text_style("Bebas Neue", 420, [shadow("#000000", 0, 8, 24, 0.5), fill("#FFFFFF")], weight=400)  # noqa: E731
    count_fn(t, t.track("text", "Contador"), lambda f: 1 + 99 * ease_out(f, 2.4), lambda v: str(int(v)), 0.6, 5.0,
             "100", Box(0, 1110, 1080, 420), num, step=3,
             final_style=lambda: text_style("Bebas Neue", 420, [shadow("#000000", 0, 8, 24, 0.5), glow("#C6FF00", 30, 0.6),
                                                               fill("#C6FF00")], weight=400,
                                            anim_in=tanim("stamp", duration=0.35)))
    # Progress bar under the number, in step with the count.
    rrect(t, t.track("shape", "Barra"), "#FFFFFF", 0.3, 7.7, Box(140, 1580, 800, 22), 11, alpha=0.25)
    t.solid(t.track("shape", "Progreso"), "#C6FF00", 0.3, 7.7, Box(140, 1580, 800, 22),
            curve_motion(lambda f: 0.01 + 0.99 * ease_out(f), 5.0, 800, at=0.3), radius=11, kind="rounded-rectangle")
    label(t, t.track("text", "Pie"), "y no pienso parar", 5.8, 2.2, Box(60, 1640, 960, 100), "Montserrat", 56, "#FFFFFF",
          weight=600, anim_in=tanim("rise", duration=0.5), name="Mensaje")
    flash(t, 5.6, 0.3, colour="#C6FF00", peak=0.45)
    song(t, "epic", 1, 0.85)
    return t


# --- 5. Likes (9:16) ---------------------------------------------------------------------------------

def me_gusta():
    t = _t(tall, "cont-me-gusta", "Contador de me gusta", "Likes counter", 4,
           ["me gusta", "likes", "corazón", "publicación", "viral"], 6.0, thumb_at=4.6, background="#FFE3EC")
    bg_gradient(t, [(0, "#FFE3EC"), (1, "#FFC2D4")], angle=90)
    card = Box(110, 300, 860, 1180)
    rrect(t, t.track("shape", "Tarjeta"), "#FFFFFF", 0.0, 6.0, card, 44, motion=[(0, {"dy": 900}, "out"), (0.6, {})],
          layers=[shadow("#B03060", 0, 24, 50, 0.3), fill("#FFFFFF"), no_stroke()])
    t.photo(t.track("video", "Foto"), "selfie-04", 0.0, 6.0, Box(140, 330, 800, 860),
            [(0, {"dy": 900}, "out"), (0.6, {})], label="Tu foto")
    hearts(t, ["#FF2D55", "#FF6F91", "#FFFFFF"], 1.0, 5.0, seed=5305, n=9, area=Box(700, 1250, 300, 300), size=(40, 80))
    # Heart that beats with the count.
    beat = [(0, {"s": 0.0}, "hold"), (0.7, {"s": 0.0}, "back"), (1.0, {})]
    for k in range(6):
        a = 1.2 + k * 0.5
        beat += [(a, {}, "out"), (a + 0.1, {"s": 1.18}, "in"), (a + 0.25, {})]
    beat += [(4.1, {}, "out"), (4.25, {"s": 1.35}, "back"), (4.6, {})]
    t.solid(t.track("shape", "Corazón"), "#FF2D55", 0.0, 6.0, centered(230, 1300, 120, 110), beat, kind="heart",
            layers=[fill("#FF2D55"), no_stroke()])
    burst(t, "#FF2D55", 4.1, centered(230, 1300, 260, 260), peak=0.5, length=0.6)
    count_up(t, t.track("text", "Contador"), 0, 25_384, "25.384", 0.8, 3.3, Box(320, 1230, 600, 140),
             big("Poppins", 104, "#111111", weight=800, align="left"), power=2.6,
             final_style=big("Poppins", 104, "#FF2D55", weight=800, align="left", anim_in=tanim("pop", duration=0.3)))
    label(t, t.track("text", "Unidad"), "me gusta", 0.8, 5.2, Box(324, 1360, 600, 80), "Poppins", 52, "#7A7A86",
          weight=600, align="left", anim_in=tanim("fade", duration=0.4), name="Unidad")
    label(t, t.track("text", "Mensaje"), "¡GRACIAS!", 4.3, 1.7, Box(60, 1560, 960, 180), "Lilita One", 150, "#FF2D55",
          weight=400, layers=[shadow("#FFFFFF", 0, 6, 0, 1.0), fill("#FF2D55")], anim_in=tanim("pop", duration=0.4),
          name="Mensaje")
    song(t, "fun", 0, 0.8)
    return t


# --- 6. Loading bar (16:9) ---------------------------------------------------------------------------

def _loading(f: float) -> float:
    """0 -> 1 in three pushes with short stalls, like a real loading bar."""
    legs = [(0.0, 0.0), (0.28, 0.38), (0.4, 0.42), (0.66, 0.79), (0.78, 0.82), (1.0, 1.0)]
    for (f0, v0), (f1, v1) in zip(legs, legs[1:]):
        if f <= f1:
            return v0 + (v1 - v0) * smooth((f - f0) / (f1 - f0))
    return 1.0


def barra_carga():
    t = _t(wide, "cont-barra-carga", "Barra de carga", "Loading bar", 5,
           ["porcentaje", "cargando", "progreso", "barra", "loading", "intro"], 6.0, thumb_at=4.9, background="#0B0F1A")
    bg_gradient(t, [(0, "#111827"), (1, "#05070D")], angle=90)
    dots(t, ["#38BDF8", "#A78BFA"], 18, 0, 6.0, seed=5306, size=(4, 10), drift=80, alpha=0.6)
    label(t, t.track("text", "Estado"), "CARGANDO", 0.3, 3.9, Box(260, 330, 1000, 90), "Orbitron", 58, "#38BDF8",
          weight=700, spacing=14, align="left", anim_in=tanim("fade", duration=0.4),
          anim_loop=tanim("flicker", intensity=0.25, speed=2), name="Estado")
    label(t, t.track("text", "Listo"), "¡LISTO!", 4.2, 1.8, Box(260, 330, 1000, 90), "Orbitron", 58, "#C6FF00",
          weight=900, spacing=14, align="left", anim_in=tanim("pop", duration=0.3), name="Mensaje final")
    track = Box(260, 560, 1400, 64)
    rrect(t, t.track("shape", "Carril"), "#1F2937", 0.3, 5.7, Box(250, 550, 1420, 84), 42,
          layers=[fill("#1F2937"), stroke(3, "#38BDF8", 0.6)])
    t.solid(t.track("shape", "Barra"), "#38BDF8", 0.5, 5.5, track,
            curve_motion(lambda f: 0.045 + 0.955 * _loading(f), 3.6, track.w, at=0.0, steps=40), radius=32,
            kind="rounded-rectangle", layers=[gradient([(0, "#38BDF8"), (1, "#A78BFA")], angle=0), no_stroke()])
    count_fn(t, t.track("text", "Contador"), _loading, lambda v: f"{int(v * 100)}%", 0.5, 3.6, "100%",
             Box(1060, 650, 600, 200), big("Orbitron", 140, "#FFFFFF", weight=800, align="right"), cuts=True,
             final_style=big("Orbitron", 140, "#C6FF00", weight=800, align="right",
                             layers=[glow("#C6FF00", 22, 0.6), fill("#C6FF00")]))
    label(t, t.track("text", "Detalle"), "preparando algo grande…", 0.6, 5.2, Box(260, 680, 800, 80), "Montserrat", 44,
          "#94A3B8", weight=500, align="left", anim_in=tanim("fade", duration=0.5), name="Detalle")
    flash(t, 4.1, 0.25, colour="#C6FF00", peak=0.35)
    song(t, "electro", 3, 0.8)
    return t


# --- 7. Progress ring (9:16) -------------------------------------------------------------------------

def anillo_meta():
    t = _t(tall, "cont-anillo-meta", "Anillo de progreso", "Progress ring", 6,
           ["porcentaje", "progreso", "meta", "anillo", "logro"], 6.0, thumb_at=4.7, background="#14112B")
    bg_gradient(t, [(0, "#2B1F66"), (1, "#0D0B1E")], angle=90)
    box = centered(540, 900, 760, 760)
    t.solid(t.track("shape", "Pista"), "#FFFFFF", 0, 6.0, box, kind="ellipse", layers=hollow_ring("#FFFFFF", 48, 0.12))
    fn = ease_out  # the counter's own curve
    clip = t.solid(t.track("shape", "Progreso"), "#00E5A0", 0, 6.0, box, kind="ellipse",
                   layers=hollow_ring("#00E5A0", 48, trim=0.0), rotation=keys([(0, -90)]))
    clip["shapeStyle"]["keyframes"] = {"layer.stroke.trimEnd": curve_keys(fn, 3.2, at=0.5)}
    count_fn(t, t.track("text", "Contador"), fn, lambda v: f"{int(v * 100)}%", 0.5, 3.2, "100%",
             centered(540, 900, 700, 260), big("Poppins", 190, "#FFFFFF", weight=800),
             final_style=big("Poppins", 190, "#FFFFFF", weight=800, anim_in=tanim("pop", duration=0.35, **{"from": 85})))
    label(t, t.track("text", "Antetítulo"), "OBJETIVO DEL MES", 0.3, 5.7, Box(60, 360, 960, 80), "Poppins", 52, "#00E5A0",
          weight=700, spacing=12, anim_in=tanim("fade", duration=0.5), name="Antetítulo")
    label(t, t.track("text", "Mensaje"), "¡Completado!", 3.9, 2.1, Box(60, 1350, 960, 120), "Poppins", 88, "#FFFFFF",
          weight=700, anim_in=tanim("rise", duration=0.45), name="Mensaje")
    burst(t, "#00E5A0", 3.7, centered(540, 900, 1000, 1000), peak=0.3, length=0.8)
    confetti(t, ["#00E5A0", "#FFFFFF", "#B388FF"], 3.7, 2.3, seed=5307, lanes=3, density=0.25)
    song(t, "electro", 0, 0.8)
    return t


# --- 8. On-screen timer (9:16) -----------------------------------------------------------------------

def temporizador():
    t = _t(tall, "cont-temporizador", "Temporizador en pantalla", "On-screen timer", 7,
           ["temporizador", "cronómetro", "cuenta regresiva", "minutos", "timer", "reto"], 16.0, thumb_at=6.5,
           background="#0A0A0A")
    bg(t, "#0A0A0A")
    box = centered(540, 900, 820, 820)
    t.solid(t.track("shape", "Pista"), "#FFFFFF", 0, 16.0, box, kind="ellipse", layers=hollow_ring("#FFFFFF", 30, 0.1))
    clip = t.solid(t.track("shape", "Tiempo"), "#FF3B30", 0, 16.0, box, kind="ellipse",
                   layers=hollow_ring("#FF3B30", 30, trim=1.0), rotation=keys([(0, -90)]))
    clip["shapeStyle"]["keyframes"] = {"layer.stroke.trimEnd": keys([(0, 1.0), (15.0, 0.0)])}
    nums = t.track("text", "Contador")
    for s in range(15, 0, -1):
        at = 15 - s
        colour = "#FF3B30" if s <= 5 else "#FFFFFF"
        style = text_style("Orbitron", 170, [fill(colour)], weight=700,
                           anim_in=tanim("pop", duration=0.25, **{"from": 90}) if s <= 5 else None)
        t.text(nums, f"00:{s:02d}", at, 1.0, centered(540, 900, 760, 240), style, editable=False, name="Contando")
    t.text(nums, "00:00", 15.0, 1.0, centered(540, 900, 760, 240),
           text_style("Orbitron", 170, [glow("#FF3B30", 24, 0.7), fill("#FF3B30")], weight=900,
                      anim_in=tanim("stamp", duration=0.3)), label="Número final")
    label(t, t.track("text", "Título"), "TIENES 15 SEGUNDOS", 0.2, 14.8, Box(60, 300, 960, 90), "Orbitron", 50,
          "#FFFFFF", weight=700, spacing=6, anim_in=tanim("fade", duration=0.5), name="Título")
    label(t, t.track("text", "Mensaje"), "¡TIEMPO!", 15.0, 1.0, Box(60, 1400, 960, 160), "Orbitron", 120, "#FF3B30",
          weight=900, anim_in=tanim("pop", duration=0.25), name="Mensaje final")
    flash(t, 15.0, 0.3, colour="#FF3B30", peak=0.5)
    t.adjust([effect("zoom_pulse", animated={"punch": spike([float(k) for k in range(10, 16)], 0.18, 0.3)})],
             name="Pulso")
    song(t, "suspense", 0, 0.75)
    return t


# --- 9. Scoreboard (16:9) ----------------------------------------------------------------------------

def marcador():
    t = _t(wide, "cont-marcador", "Marcador del partido", "Match scoreboard", 8,
           ["marcador", "fútbol", "partido", "goles", "deporte", "score"], 9.0, thumb_at=7.4, background="#000000")
    photo_bg(t, "h-soccer-03", s1=1.08, label="Tu video del partido")
    shade_top(t, 360, 0.6)
    bar_box = Box(80, 70, 980, 110)
    move = [(0, {"dy": -260}, "out"), (0.5, {})]
    tr = t.track("shape", "Marcador")
    t.solid(tr, "#0F172A", 0.2, 8.8, bar_box, move, radius=14, kind="rounded-rectangle",
            layers=[shadow("#000000", 0, 8, 22, 0.5), fill("#0F172A", 0.92), no_stroke()])
    t.solid(t.track("shape", "Local"), "#E11D48", 0.2, 8.8, Box(80, 70, 18, 110), move)
    t.solid(t.track("shape", "Visita"), "#2563EB", 0.2, 8.8, Box(1042, 70, 18, 110), move)
    t.solid(t.track("shape", "Goles"), "#FFFFFF", 0.2, 8.8, Box(430, 82, 280, 86), move, radius=10,
            kind="rounded-rectangle")
    t.solid(t.track("shape", "Reloj"), "#22C55E", 0.2, 8.8, Box(1080, 82, 210, 86), move, radius=10,
            kind="rounded-rectangle", layers=[shadow("#000000", 0, 6, 16, 0.4), fill("#22C55E"), no_stroke()])
    team = dict(font="Oswald", size=58, colour="#FFFFFF", weight=600, spacing=4, motion=move)
    label(t, t.track("text", "Local"), "TIGRES", 0.2, 8.8, Box(110, 70, 310, 110), **team, name="Equipo local")
    label(t, t.track("text", "Visita"), "HALCONES", 0.2, 8.8, Box(720, 70, 310, 110), **team, name="Equipo visitante")
    score = lambda: text_style("Oswald", 72, [fill("#0F172A")], weight=700)  # noqa: E731
    goal = lambda: text_style("Oswald", 72, [fill("#E11D48")], weight=700, anim_in=tanim("pop", duration=0.3))  # noqa: E731
    goal_b = lambda: text_style("Oswald", 72, [fill("#2563EB")], weight=700, anim_in=tanim("pop", duration=0.3))  # noqa: E731
    sa, sb = t.track("text", "Goles local"), t.track("text", "Goles visita")
    ba, bb = Box(430, 70, 120, 110), Box(590, 70, 120, 110)
    t.text(sa, "0", 0.2, 2.0, ba, score(), move, editable=False, name="Goles")
    t.text(sa, "1", 2.2, 3.4, ba, goal(), editable=False, name="Goles")
    t.text(sa, "2", 5.6, 3.4, ba, goal(), label="Goles local (final)")
    t.text(sb, "0", 0.2, 3.7, bb, score(), move, editable=False, name="Goles")
    t.text(sb, "1", 3.9, 5.1, bb, goal_b(), label="Goles visitante (final)")
    label(t, t.track("text", "Guion"), "-", 0.2, 8.8, Box(540, 70, 60, 110), "Oswald", 60, "#0F172A", weight=700,
          motion=move, editable=False)
    count_fn(t, t.track("text", "Minuto"), lambda f: 90 * f, lambda v: f"{int(v):02d}:00", 0.7, 6.8, "90:00",
             Box(1080, 70, 210, 110), big("Oswald", 56, "#FFFFFF", weight=600), step=3, name="Minuto final", cuts=True)
    for at, who, colour in ((2.2, "¡GOOOL!", "#E11D48"), (3.9, "¡GOOOL!", "#2563EB"), (5.6, "¡GOOOL!", "#E11D48")):
        label(t, t.track("text", "Gol"), who, at, 1.3, Box(0, 640, 1920, 260), "Anton", 230, "#FFFFFF", weight=400,
              layers=[shadow("#000000", 0, 10, 30, 0.6), stroke(10, colour), fill("#FFFFFF")],
              anim_in=tanim("zoom-in", duration=0.3, **{"from": 40}), anim_out=tanim("fade-scale", duration=0.3),
              editable=False)
        flash(t, at, 0.25, peak=0.5)
    label(t, t.track("text", "Final"), "FINAL DEL PARTIDO", 7.6, 1.4, Box(0, 820, 1920, 120), "Oswald", 80, "#FFFFFF",
          weight=700, spacing=10, layers=[shadow("#000000", 0, 6, 20, 0.7), fill("#FFFFFF")],
          anim_in=tanim("rise", duration=0.4), name="Mensaje final")
    song(t, "epic", 1, 0.8)
    return t


# --- 10. Odometer: kilometres (9:16) -----------------------------------------------------------------

def _odometer_scene(t, digits: str, final: str, cy: float, cw: float, ch: float, font: str, size: int, colour: str,
                    bg_colour: str, window_colour: str, t0: float, length: float, swap: float, *, weight=400,
                    radius=26, sep_colour="#2A2A2A", shine=0.16, final_colour=None, final_glow=None, spacing=0.0,
                    final_dy=0.0):
    n = len(digits)
    x0 = t.w / 2 - cw * n / 2
    window = Box(x0 - 20, cy - ch / 2 - 20, cw * n + 40, ch + 40)
    rrect(t, t.track("shape", "Ventana"), window_colour, 0, t.duration, window, radius,
          layers=[gradient([(0, window_colour), (0.5, "#000000" if window_colour != "#FFFFFF" else "#E9E9EE"),
                            (1, window_colour)], angle=90), no_stroke()])
    odometer(t, digits, t0, length, x0, cy, cw, ch, font, size, colour, swap_at=swap, weight=weight)
    plates(t, bg_colour, window)
    for i in range(1, n):
        t.solid(t.track("shape", "Separador"), sep_colour, 0, swap, Box(x0 + i * cw - 2, window.y, 4, window.h))
    t.solid(t.track("shape", "Brillo"), "#FFFFFF", 0, t.duration, Box(window.x, window.y, window.w, window.h / 2),
            radius=radius, kind="rounded-rectangle",
            layers=[gradient([(0, "#FFFFFF", shine), (1, "#FFFFFF", 0.0)], angle=90), no_stroke()])
    t.solid(t.track("shape", "Destello"), "#FFFFFF", swap - 0.05, 0.35, window,
            radius=radius, kind="rounded-rectangle", opacity=keys([(0, 0.0), (0.05, 0.8, "out"), (0.35, 0.0)]))
    layers = ([glow(final_glow, 22, 0.6)] if final_glow else []) + [fill(final_colour or colour)]
    return t.text(t.track("text", "Número"), final, swap, t.duration - swap, Box(window.x - 200, cy - ch / 2 + final_dy,
                  window.w + 400, ch), text_style(font, size, layers, weight=weight, spacing=spacing,
                                                  anim_loop=tanim("pulse", amount=2, speed=0.8)), label="Número final")


def odometro_km():
    t = _t(tall, "cont-odometro-km", "Odómetro de kilómetros", "Mileage odometer", 9,
           ["odómetro", "kilómetros", "viaje", "ruta", "auto", "road trip"], 7.0, thumb_at=4.0, background="#111316")
    bg(t, "#111316")
    _odometer_scene(t, "012480", "012480", 960, 150, 230, "Oswald", 180, "#F5F5F5", "#111316", "#1A1A1A", 0.5, 3.6, 4.5,
                    weight=600, final_colour="#FFFFFF", final_glow="#FF9F1C", spacing=58, final_dy=6)
    label(t, t.track("text", "Antetítulo"), "KILÓMETROS RECORRIDOS", 0.3, 6.7, Box(60, 700, 960, 80), "Oswald", 56,
          "#FF9F1C", weight=600, spacing=10, anim_in=tanim("fade", duration=0.5), name="Antetítulo")
    label(t, t.track("text", "Mensaje"), "y seguimos rodando", 4.7, 2.3, Box(60, 1170, 960, 100), "Montserrat", 60,
          "#FFFFFF", weight=600, anim_in=tanim("rise", duration=0.5), name="Mensaje")
    song(t, "cine", 1, 0.8)
    return t


# --- 11. Odometer: website visits (16:9, light) --------------------------------------------------------

def odometro_visitas():
    t = _t(wide, "cont-odometro-visitas", "Odómetro de visitas", "Visits odometer", 10,
           ["odómetro", "visitas", "web", "tráfico", "estadísticas", "negocio"], 7.0, thumb_at=4.1, background="#F4F1EA")
    bg(t, "#F4F1EA")
    _odometer_scene(t, "0058730", "0058730", 560, 170, 250, "Bebas Neue", 220, "#FFFFFF", "#F4F1EA", "#1D1D1F", 0.5, 3.6,
                    4.5, final_colour="#FFFFFF", spacing=86, sep_colour="#3A3A3C", shine=0.12, final_dy=22)
    label(t, t.track("text", "Antetítulo"), "VISITAS ESTE MES", 0.3, 6.7, Box(0, 230, 1920, 90), "Bebas Neue", 84,
          "#E4572E", weight=400, spacing=18, anim_in=tanim("fade", duration=0.5), name="Antetítulo")
    label(t, t.track("text", "Mensaje"), "gracias por visitarnos", 4.7, 2.3, Box(0, 760, 1920, 100), "Montserrat", 56,
          "#1D1D1F", weight=600, anim_in=tanim("rise", duration=0.5), name="Mensaje")
    song(t, "jazz", 1, 0.75)
    return t


# --- 12. Monthly sales (16:9) ------------------------------------------------------------------------

def ventas_mes():
    t = _t(wide, "cont-ventas-semestre", "Ventas del semestre", "Half-year sales", 11,
           ["ventas", "gráfico", "negocio", "crecimiento", "resultados", "barras"], 8.0, thumb_at=6.2, background="#FFFFFF")
    bg_gradient(t, [(0, "#FFFFFF"), (1, "#EEF2FF")], angle=90)
    months = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN"]
    heights = [0.32, 0.45, 0.41, 0.6, 0.78, 1.0]
    base, maxh, bw = 930, 560, 120
    t.solid(t.track("shape", "Eje"), "#CBD5E1", 0.2, 7.8, Box(120, base, 1000, 4), [(0, {"sx": 0.0, "dx": -500}, "out"),
                                                                                   (0.6, {})])
    for i, (m, h) in enumerate(zip(months, heights)):
        x = 160 + i * 160
        hh = maxh * h
        at = 0.6 + i * 0.35
        colour = "#4F46E5" if i == len(months) - 1 else "#A5B4FC"
        t.solid(t.track("shape", "Barra"), colour, 0.2, 7.8, Box(x, base - hh, bw, hh),
                [(0, {"sy": 0.0, "dy": hh / 2}, "hold"), (at - 0.2, {"sy": 0.0, "dy": hh / 2}, "out"), (at + 0.5, {})],
                radius=12, kind="rounded-rectangle")
        label(t, t.track("text", "Mes"), m, 0.4, 7.6, Box(x - 20, base + 16, bw + 40, 60), "Montserrat", 34, "#64748B",
              weight=700, anim_in=tanim("fade", duration=0.4), name=f"Mes {i + 1}")
    label(t, t.track("text", "Antetítulo"), "VENTAS DEL SEMESTRE", 0.3, 7.7, Box(1180, 280, 700, 70), "Montserrat", 42,
          "#4F46E5", weight=800, spacing=6, align="left", anim_in=tanim("fade", duration=0.5), name="Antetítulo")
    count_up(t, t.track("text", "Contador"), 0, 48_750, "$48.750", 0.6, 3.8, Box(1170, 350, 740, 200),
             big("Montserrat", 150, "#0F172A", weight=900, align="left"), prefix="$", power=2.6,
             final_style=big("Montserrat", 150, "#0F172A", weight=900, align="left", anim_in=tanim("pop", duration=0.3)))
    pill(t, t.track("shape", "Insignia"), "#22C55E", 4.6, 3.4, Box(1180, 580, 330, 80), pop(0, 0.4))
    label(t, t.track("text", "Insignia"), "▲ 38 %", 4.6, 3.4, Box(1180, 580, 330, 80), "Montserrat", 42, "#FFFFFF",
          weight=800, anim_in=tanim("pop", duration=0.4), name="Crecimiento")
    label(t, t.track("text", "Detalle"), "más que el semestre anterior", 4.9, 3.1, Box(1180, 680, 700, 120), "Montserrat",
          40, "#475569", weight=500, align="left", anim_in=tanim("fade", duration=0.5), name="Detalle")
    song(t, "upbeat", 3, 0.75)
    return t


# --- 13. Steps (9:16) --------------------------------------------------------------------------------

def pasos():
    t = _t(tall, "cont-pasos", "Contador de pasos", "Step counter", 12,
           ["pasos", "caminar", "salud", "meta diaria", "fitness", "deporte"], 7.0, thumb_at=5.4, background="#000000")
    photo_bg(t, "hike-03", s1=1.1, label="Tu foto o video")
    shade_bottom(t, 1200, 0.9, colour="#04121F")
    box = centered(540, 1260, 560, 560)
    t.solid(t.track("shape", "Pista"), "#FFFFFF", 0.2, 6.8, box, kind="ellipse", layers=hollow_ring("#FFFFFF", 34, 0.2))
    fn = ease_out  # the counter's own curve
    clip = t.solid(t.track("shape", "Progreso"), "#FFB703", 0.2, 6.8, box, kind="ellipse",
                   layers=hollow_ring("#FFB703", 34, trim=0.0), rotation=keys([(0, -90)]))
    clip["shapeStyle"]["keyframes"] = {"layer.stroke.trimEnd": curve_keys(fn, 3.6, at=0.4)}
    count_fn(t, t.track("text", "Contador"), fn, lambda v: thousands(round(v * 10000)), 0.6, 3.6, "10.000",
             centered(540, 1230, 520, 170), big("Montserrat", 120, "#FFFFFF", weight=900),
             final_style=big("Montserrat", 120, "#FFB703", weight=900, anim_in=tanim("pop", duration=0.3)))
    label(t, t.track("text", "Unidad"), "pasos", 0.6, 6.4, centered(540, 1340, 400, 80), "Montserrat", 52, "#FFFFFF",
          weight=600, anim_in=tanim("fade", duration=0.4), name="Unidad")
    label(t, t.track("text", "Título"), "META DE HOY", 0.3, 6.7, Box(60, 860, 960, 90), "Montserrat", 60, "#FFB703",
          weight=900, spacing=10, anim_in=tanim("fade", duration=0.5), name="Título")
    label(t, t.track("text", "Mensaje"), "¡Cumplida!", 4.5, 2.5, Box(60, 1600, 960, 120), "Montserrat", 80, "#FFFFFF",
          weight=800, anim_in=tanim("rise", duration=0.4), name="Mensaje")
    burst(t, "#FFB703", 4.2, centered(540, 1260, 760, 760), peak=0.35, length=0.7)
    song(t, "upbeat", 2, 0.8)
    return t


# --- 14. Kilometres run (9:16) -----------------------------------------------------------------------

def maraton_km():
    t = _t(tall, "cont-maraton-km", "Kilómetros corridos", "Kilometres run", 13,
           ["maratón", "correr", "kilómetros", "running", "carrera", "deporte"], 7.0, thumb_at=5.5, background="#0B132B")
    bg_gradient(t, [(0, "#1C2541"), (1, "#0B132B")], angle=90)
    # A running track seen from above: the red oval, its lanes, the field and a runner going round.
    grow = [(0, {"s": 0.0}, "back"), (0.7, {})]
    t.solid(t.track("shape", "Pista"), "#C1440E", 0.2, 6.8, centered(540, 1430, 940, 500), grow, radius=250,
            kind="rounded-rectangle", layers=[shadow("#000000", 0, 16, 30, 0.4), fill("#C1440E"), no_stroke()])
    for w, h in ((860, 420), (780, 340)):
        t.solid(t.track("shape", "Carril"), "#FFFFFF", 0.2, 6.8, centered(540, 1430, w, h), grow, radius=h / 2,
                kind="rounded-rectangle", layers=hollow_ring("#FFFFFF", 4, 0.7))
    t.solid(t.track("shape", "Campo"), "#2D6A4F", 0.2, 6.8, centered(540, 1430, 700, 260), grow, radius=130,
            kind="rounded-rectangle")
    lap = [(0, {"dx": 0, "dy": 190}, "linear")]
    for k, (dx, dy) in enumerate([(-300, 150), (-390, 0), (-300, -150), (0, -190), (300, -150), (390, 0), (300, 150),
                                  (0, 190)]):
        lap.append((0.45 * (k + 1), {"dx": dx, "dy": dy}, "linear"))
    lap2 = lap + [(p[0] + 3.6, p[1], "linear") for p in lap[1:]]
    t.solid(t.track("shape", "Corredor"), "#5BC0BE", 0.9, 6.1, centered(540, 1430, 34, 34), lap2, kind="ellipse",
            layers=[shadow("#000000", 0, 4, 8, 0.4), fill("#FFFFFF"), stroke(6, "#5BC0BE")])
    label(t, t.track("text", "Antetítulo"), "HOY CORRÍ", 0.3, 6.7, Box(60, 420, 960, 100), "Teko", 110, "#5BC0BE",
          weight=600, spacing=10, anim_in=tanim("slide-up", duration=0.4), name="Antetítulo")
    count_up(t, t.track("text", "Contador"), 0, 42.195, "42,195", 0.6, 3.8, Box(0, 510, 1080, 380),
             big("Teko", 360, "#FFFFFF", weight=600), decimals=3, power=2.8,
             final_style=big("Teko", 360, "#FFFFFF", weight=600, layers=[glow("#5BC0BE", 28, 0.5), fill("#FFFFFF")],
                             anim_in=tanim("pop", duration=0.3, **{"from": 85})))
    label(t, t.track("text", "Unidad"), "KILÓMETROS", 0.6, 6.4, Box(60, 880, 960, 110), "Teko", 110, "#FFFFFF",
          weight=500, spacing=16, anim_in=tanim("fade", duration=0.5), name="Unidad")
    pill(t, t.track("shape", "Tiempo"), "#5BC0BE", 4.6, 2.4, centered(540, 1070, 520, 100), pop(0, 0.4))
    label(t, t.track("text", "Tiempo"), "3 h 58 min", 4.6, 2.4, centered(540, 1070, 520, 100), "Teko", 76, "#0B132B",
          weight=600, anim_in=tanim("pop", duration=0.4), name="Tiempo")
    song(t, "epic", 3, 0.85)
    return t


# --- 15. Savings goal (9:16) -------------------------------------------------------------------------

def ahorro_meta():
    t = _t(tall, "cont-ahorro-meta", "Meta de ahorro", "Savings goal", 14,
           ["ahorro", "dinero", "meta", "finanzas", "alcancía", "logro"], 7.0, thumb_at=5.6, background="#FFF4E0")
    bg_gradient(t, [(0, "#FFF4E0"), (1, "#FFE1B3")], angle=90)
    # Coins drop on to a pile, one per beat.
    rng = random.Random(5315)
    stacks = [(320, 0), (540, 0), (760, 0)]
    for k in range(15):
        col = k % 3
        cx, n = stacks[col]
        stacks[col] = (cx, n + 1)
        y = 1340 - n * 50
        at = 0.6 + k * 0.24
        tr = t.track("shape", "Monedas") if k % 5 == 0 else tr
        t.solid(tr, "#F4B400", at, 7.0 - at, centered(cx + rng.uniform(-6, 6), y, 210, 66),
                [(0, {"dy": -(y + 80)}, "in"), (0.32, {}, "back"), (0.44, {})], kind="ellipse",
                layers=[shadow("#8A5A00", 0, 6, 0, 1.0), fill("#FFC93C"), stroke(4, "#C98A00")])
    t.solid(t.track("shape", "Suelo"), "#E8B66B", 0, 7.0, centered(540, 1390, 860, 50), kind="ellipse", alpha=0.6)
    label(t, t.track("text", "Antetítulo"), "AHORRÉ", 0.3, 6.7, Box(60, 360, 960, 110), "Fredoka", 100, "#7A4B00",
          weight=700, spacing=8, anim_in=tanim("bounce", duration=0.5), name="Antetítulo")
    count_up(t, t.track("text", "Contador"), 0, 5_000, "$5.000", 0.6, 3.6, Box(0, 470, 1080, 280),
             big("Fredoka", 240, "#2D6A4F", weight=700), prefix="$", power=2.4,
             final_style=big("Fredoka", 240, "#2D6A4F", weight=700, layers=[shadow("#FFFFFF", 0, 8, 0, 1.0),
                             fill("#2D6A4F")], anim_in=tanim("pop", duration=0.3)))
    rrect(t, t.track("shape", "Barra"), "#FFFFFF", 0.3, 6.7, Box(140, 800, 800, 44), 22,
          layers=[fill("#FFFFFF"), stroke(4, "#7A4B00", 0.3)])
    t.solid(t.track("shape", "Progreso"), "#2D6A4F", 0.3, 6.7, Box(140, 800, 800, 44),
            curve_motion(lambda f: 0.03 + 0.97 * ease_out(f), 3.6, 800, at=0.3), radius=22, kind="rounded-rectangle")
    label(t, t.track("text", "Meta"), "meta: $5.000", 0.6, 6.4, Box(140, 860, 800, 70), "Fredoka", 46, "#7A4B00",
          weight=500, align="right", anim_in=tanim("fade", duration=0.4), name="Meta")
    label(t, t.track("text", "Mensaje"), "¡lo logré!", 4.5, 2.5, Box(60, 1450, 960, 150), "Fredoka", 120, "#7A4B00",
          weight=700, anim_in=tanim("pop", duration=0.4), name="Mensaje")
    confetti(t, ["#2D6A4F", "#FFC93C", "#FF8C42"], 4.2, 2.8, seed=5315, lanes=3, density=0.3)
    song(t, "fun", 3, 0.8)
    return t


# --- 16. A million views (9:16, neon) ----------------------------------------------------------------

def vistas_millon():
    t = _t(tall, "cont-vistas-millon", "Un millón de vistas", "One million views", 15,
           ["vistas", "millón", "viral", "video", "neón", "views"], 7.0, thumb_at=5.4, background="#050510")
    bg(t, "#050510")
    dots(t, ["#00F5FF", "#FF00E5"], 30, 0, 7.0, seed=5316, size=(4, 12), drift=200, alpha=0.7)
    # An eye: a neon almond, the iris and the pupil.
    eye = centered(540, 620, 420, 230)
    t.solid(t.track("shape", "Ojo"), "#00F5FF", 0.2, 6.8, eye, pop(0, 0.5), kind="ellipse",
            layers=[glow("#00F5FF", 30, 0.8)] + hollow_ring("#00F5FF", 14))
    t.solid(t.track("shape", "Iris"), "#FF00E5", 0.4, 6.6, centered(540, 620, 160, 160),
            [(0, {"s": 0.0}, "back"), (0.4, {}, "smooth"), (2.0, {"dx": -40}, "smooth"), (3.4, {"dx": 40}, "smooth"),
             (4.0, {})], kind="ellipse", layers=[glow("#FF00E5", 26, 0.8), fill("#FF00E5"), no_stroke()])
    t.solid(t.track("shape", "Pupila"), "#050510", 0.5, 6.5, centered(540, 620, 70, 70),
            [(0, {"s": 0.0}, "back"), (0.3, {}, "smooth"), (1.9, {"dx": -40}, "smooth"), (3.3, {"dx": 40}, "smooth"),
             (3.9, {})], kind="ellipse")
    neon = lambda c: [glow(c, 26, 0.9), stroke(4, c), fill("#FFFFFF")]  # noqa: E731
    count_up(t, t.track("text", "Contador"), 0, 1_000_000, "1.000.000", 0.8, 3.4, Box(0, 820, 1080, 260),
             big("Bebas Neue", 230, "#FFFFFF", weight=400, layers=neon("#00F5FF")), power=3.4,
             final_style=big("Bebas Neue", 230, "#FFFFFF", weight=400, layers=neon("#FF00E5"),
                             anim_loop=tanim("flicker", intensity=0.2, speed=3)))
    label(t, t.track("text", "Unidad"), "VISTAS", 0.6, 6.4, Box(60, 1080, 960, 140), "Bebas Neue", 140, "#FFFFFF",
          weight=400, spacing=30, layers=neon("#FF00E5"), anim_in=tanim("flicker-in", duration=0.8), name="Unidad")
    label(t, t.track("text", "Mensaje"), "y contando…", 4.4, 2.6, Box(60, 1320, 960, 100), "Montserrat", 60, "#B9F9FF",
          weight=600, anim_in=tanim("fade", duration=0.5), name="Mensaje")
    t.adjust([effect("rgb_split", animated={"amount": spike([4.2], 18, 0.4)}, angle=20),
              effect("bloom_glow", threshold=0.6, intensity=0.5)], name="Brillo")
    song(t, "electro", 1, 0.85)
    return t


# --- 17. Birthday age (9:16) -------------------------------------------------------------------------

def edad_cumple():
    t = _t(tall, "cont-edad-cumple", "Cumpleaños: cuenta los años", "Birthday age counter", 16,
           ["cumpleaños", "años", "edad", "fiesta", "celebración", "birthday"], 7.0, thumb_at=5.4, background="#000000")
    photo_bg(t, "cake-01", s1=1.1, label="Foto del cumpleañero")
    shade_full(t, 0.25, colour="#2A0A2E")
    shade_bottom(t, 1000, 0.85, colour="#2A0A2E")
    label(t, t.track("text", "Antetítulo"), "HOY CUMPLO", 0.3, 6.7, Box(60, 1000, 960, 100), "Montserrat", 64, "#FFD6E8",
          weight=800, spacing=14, anim_in=tanim("fade", duration=0.5), name="Antetítulo")
    count_fn(t, t.track("text", "Contador"), lambda f: 30 * ease_out(f, 2.2), lambda v: str(int(v)), 0.6, 3.4, "30",
             Box(0, 1080, 1080, 480), big("Shrikhand", 380, "#FFFFFF", weight=400,
                                          layers=[shadow("#FF4FA3", 10, 12, 0, 1.0), fill("#FFFFFF")]), step=3,
             final_style=big("Shrikhand", 380, "#FFFFFF", weight=400, layers=[shadow("#FF4FA3", 10, 12, 0, 1.0),
                             fill("#FFE14D")], anim_in=tanim("pop", duration=0.35, **{"from": 60}),
                             anim_loop=tanim("swing", angle=3, speed=0.8)))
    label(t, t.track("text", "Mensaje"), "¡Feliz cumple a mí!", 4.3, 2.7, Box(60, 1580, 960, 140), "Pacifico", 90,
          "#FFFFFF", weight=400, anim_in=tanim("rise", duration=0.5), name="Mensaje")
    confetti(t, ["#FF4FA3", "#FFE14D", "#FFFFFF", "#7DF9FF"], 4.0, 3.0, seed=5317, lanes=4, density=0.22)
    flash(t, 4.0, 0.3, colour="#FFE14D", peak=0.5)
    song(t, "fun", 4, 0.85)
    return t


# --- 18. Days together (9:16) ------------------------------------------------------------------------

def dias_juntos():
    t = _t(tall, "cont-dias-juntos", "Días juntos", "Days together", 17,
           ["pareja", "aniversario", "amor", "días juntos", "novios", "romántico"], 8.0, thumb_at=6.2,
           background="#000000")
    photo_bg(t, "couple-07", s1=1.1, label="Foto de ustedes")
    shade_full(t, 0.2, colour="#3B0A1E")
    shade_bottom(t, 1000, 0.85, colour="#3B0A1E")
    hearts(t, ["#FF8FAB", "#FFFFFF", "#FB6F92"], 0.5, 7.5, seed=5318, n=7, area=Box(60, 1720, 960, 180), size=(30, 56), drift=90)
    count_up(t, t.track("text", "Contador"), 0, 1_825, "1.825", 0.6, 4.4, Box(0, 1060, 1080, 300),
             big("DM Serif Display", 250, "#FFFFFF", weight=400), power=2.8,
             final_style=big("DM Serif Display", 250, "#FFFFFF", weight=400,
                             layers=[glow("#FF8FAB", 26, 0.6), fill("#FFFFFF")], anim_in=tanim("blur-in", duration=0.5)))
    label(t, t.track("text", "Unidad"), "días juntos", 0.8, 7.2, Box(60, 1340, 960, 170), "Great Vibes", 140, "#FFC2D1",
          weight=400, anim_in=tanim("fade", duration=0.8), name="Unidad")
    label(t, t.track("text", "Mensaje"), "y quiero todos los que faltan", 5.4, 2.6, Box(80, 1560, 920, 100),
          "Playfair Display", 52, "#FFFFFF", weight=500, italic=True, anim_in=tanim("fade", duration=0.6), name="Mensaje")
    song(t, "romantic", 0, 0.85)
    return t


# --- 19. Books this year (9:16) ----------------------------------------------------------------------

def libros_anio():
    t = _t(tall, "cont-libros-anio", "Libros del año", "Books this year", 18,
           ["libros", "lectura", "año", "reto de lectura", "leer", "booktok"], 7.0, thumb_at=5.5, background="#F3ECE0")
    bg(t, "#F3ECE0")
    rng = random.Random(5319)
    colours = ["#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51", "#6D597A", "#B56576", "#355070"]
    y = 1800
    for k in range(13):
        h = rng.uniform(46, 70)
        w = rng.uniform(420, 560)
        at = 0.6 + k * 0.27
        tr = t.track("shape", "Libros") if k % 6 == 0 else tr
        c = colours[k % len(colours)]
        t.solid(tr, c, at, 7.0 - at, centered(540 + rng.uniform(-40, 40), y - h / 2, w, h),
                [(0, {"dx": 1200 if k % 2 else -1200}, "out"), (0.4, {})], radius=6, kind="rounded-rectangle",
                layers=[shadow("#000000", 0, 4, 6, 0.25), fill(c), no_stroke()],
                rotation=keys([(0, rng.uniform(-3, 3))]))
        y -= h
    label(t, t.track("text", "Antetítulo"), "este año leí", 0.3, 6.7, Box(60, 240, 960, 120), "Caveat", 110, "#3D3027",
          weight=700, anim_in=tanim("typewriter", duration=0.6, unit="character"), name="Antetítulo")
    count_fn(t, t.track("text", "Contador"), lambda f: 52 * ease_out(f, 1.6), lambda v: str(int(v)), 0.6, 3.6, "52",
             Box(0, 330, 1080, 360), big("Abril Fatface", 320, "#E76F51", weight=400), step=2,
             final_style=big("Abril Fatface", 320, "#E76F51", weight=400, anim_in=tanim("pop", duration=0.3)))
    label(t, t.track("text", "Unidad"), "libros", 0.6, 6.4, Box(60, 670, 960, 120), "Abril Fatface", 100, "#3D3027",
          weight=400, anim_in=tanim("fade", duration=0.5), name="Unidad")
    label(t, t.track("text", "Mensaje"), "¿cuál me recomiendas?", 4.6, 2.4, Box(60, 800, 960, 100), "Caveat", 80,
          "#6D597A", weight=700, anim_in=tanim("fade", duration=0.5), name="Mensaje")
    song(t, "calm", 1, 0.8)
    return t


# --- 20. Price drop (9:16) ---------------------------------------------------------------------------

def precio_baja():
    t = _t(tall, "cont-precio-baja", "Precio que baja", "Price drop", 19,
           ["precio", "oferta", "descuento", "rebaja", "tienda", "promoción"], 7.0, thumb_at=5.4, background="#FFFFFF")
    bg(t, "#FFFFFF")
    t.photo(t.track("video", "Producto"), "icecream-01", 0, 7.0, Box(0, 0, 1080, 1100), kb(7.0, 1.0, 1.06),
            label="Foto del producto")
    t.solid(t.track("shape", "Panel"), "#111111", 0, 7.0, Box(0, 1060, 1080, 860), [(0, {"dy": 860}, "out"), (0.5, {})])
    pill(t, t.track("shape", "Insignia"), "#FFD600", 0.6, 6.4, Box(60, 120, 330, 96), pop(0, 0.4))
    label(t, t.track("text", "Insignia"), "OFERTA", 0.6, 6.4, Box(60, 120, 330, 96), "Anton", 64, "#111111", weight=400,
          spacing=4, anim_in=tanim("pop", duration=0.4), name="Insignia")
    label(t, t.track("text", "Producto"), "Helado artesanal", 0.6, 6.4, Box(60, 1120, 960, 100), "Montserrat", 60,
          "#FFFFFF", weight=700, anim_in=tanim("fade", duration=0.4), name="Producto")
    label(t, t.track("text", "Antes"), "antes $199", 3.9, 3.1, Box(60, 1240, 960, 80), "Montserrat", 52, "#9CA3AF",
          weight=600, anim_in=tanim("fade", duration=0.3), name="Precio anterior")
    t.solid(t.track("shape", "Tachado"), "#FF3B30", 4.1, 2.9, centered(540, 1282, 400, 8),
            [(0, {"sx": 0.0, "dx": -200}, "out"), (0.3, {})])
    count_fn(t, t.track("text", "Contador"), lambda f: 199 - 100 * ease_out(f, 2.6), lambda v: f"${int(round(v))}", 0.8,
             3.0, "$99", Box(0, 1330, 1080, 320), big("Anton", 280, "#FFFFFF", weight=400),
             final_style=big("Anton", 280, "#FFD600", weight=400, anim_in=tanim("stamp", duration=0.35),
                             anim_loop=tanim("pulse", amount=3, speed=1.2)))
    pill(t, t.track("shape", "Descuento"), "#FF3B30", 4.0, 3.0, centered(860, 1400, 240, 100), pop(0, 0.4),
         rotation=keys([(0, 10)]))
    label(t, t.track("text", "Descuento"), "-50 %", 4.0, 3.0, centered(860, 1400, 240, 100), "Anton", 60, "#FFFFFF",
          weight=400, anim_in=tanim("pop", duration=0.4), rotation=keys([(0, 10)]), name="Descuento")
    label(t, t.track("text", "Llamada"), "solo por hoy", 4.3, 2.7, Box(60, 1680, 960, 90), "Montserrat", 54, "#FFD600",
          weight=800, spacing=6, case="upper", anim_in=tanim("rise", duration=0.4), name="Llamada")
    song(t, "upbeat", 5, 0.85)
    return t


TEMPLATES = [dinero_millon, seguidores_100k, suscriptores_millon, dias_100, me_gusta, barra_carga, anillo_meta,
             temporizador, marcador, odometro_km, odometro_visitas, ventas_mes, pasos, maraton_km, ahorro_meta,
             vistas_millon, edad_cumple, dias_juntos, libros_anio, precio_baja]
