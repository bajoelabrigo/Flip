"""TIKTOK folder video 2 as Stock templates (tk2-*). See docs/plan-tiktok.md.

«TikTok Intro Stories Pack» (35865129.mp4, 1920×1080 at 25 fps): fifteen vertical profile stories in blue, black and
red, shown inside tilted phones. Each screen was laid flat with ffmpeg's perspective filter (four measured corners,
540×1152) and studied on 10 fps sheets; the story is laid out on 1080×1920 (x × 2, y × 1.667: the phone screen is
taller than 9:16). Every story keeps the reference's interface: progress bars, the account row (the avatar is the
user's logo slot, «Motion Media Group» → «Your Channel») and the «Send Message» field. Kit de TikTok; ids `tk2-*`,
order 14200-. Study notes in tienda/plantillas/estudio-35865129/NOTAS.md.

Each story plays its entrance, holds, and leaves with its entrance backwards at 2.5× speed.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, tall
from llt_motion import mask_track
from scene import gradient, keys
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import EXIT, arc, fill, lin, poly
from templates_yp4 import T, photo, ring_path

W, H = 1080, 1920
BLUE, RED, WHITE, YELLOW = "#18BEFD", "#FE1A1D", "#FFFFFF", "#F2F01E"
DARK, NAVY, ASH, INK = "#121212", "#050A10", "#1B1B1B", "#101010"
A, I = "Archivo", "Inter"
for w, f in ((800, "ExtraBold"), (900, "Black")):
    f6._FILES[(A, w)] = f"fonts.extra/fonts/archivo/Archivo-{f}.ttf"
for w, f in ((500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"), (900, "Black")):
    f6._FILES[(I, w)] = f"fonts.basic/fonts/inter/Inter-{f}.ttf"

HEART = ("M 50 96 C 22 74 0 56 0 30 C 0 12 13 0 28 0 C 38 0 46 6 50 16 C 54 6 62 0 72 0 C 87 0 100 12 100 30 "
         "C 100 56 78 74 50 96 Z")
STAR = poly([(50 + (50 if i % 2 == 0 else 24) * math.cos(math.radians(-90 + 15 * i)),
              50 + (50 if i % 2 == 0 else 24) * math.sin(math.radians(-90 + 15 * i))) for i in range(24)])
ALMOND = "M 0 50 C 24 4 76 4 100 50 C 76 96 24 96 0 50 Z"
PLANE = "M 2 44 L 98 2 L 60 98 L 46 56 Z M 46 56 L 98 2"
ARROW_UR = "M 4 96 L 96 4 M 30 4 L 96 4 L 96 70"
# A music note with a flag (our own glyph, used small like a social icon).
NOTE = ("M 50 2 L 66 2 C 68 16 80 26 96 28 L 96 44 C 84 44 74 40 66 34 L 66 72 C 66 88 53 100 37 100 "
        "C 21 100 8 88 8 72 C 8 56 21 44 37 44 C 42 44 46 45 50 47 Z")
SHARE = "M 56 4 L 98 42 L 56 80 L 56 58 C 34 56 16 64 2 88 C 6 54 24 32 56 28 Z"
CAMERA = "M 0 18 L 64 18 L 64 40 L 100 18 L 100 82 L 64 60 L 64 82 L 0 82 Z"
BUBBLE_TAIL = "M 0 0 L 100 0 L 80 100 Z"


def _p(id, es, en, order, dur, tags=(), thumb=None):
    return tall(f"tk2-{id}", es, en, "tiktok", dur, order=order,
                tags=["tiktok", "historia", "reels"] + list(tags), thumb_at=thumb or round(dur * 0.55, 1))


def dur_for(frames, hold=2.4):
    e = frames / FPS
    return round(e + hold + e / EXIT, 1)


def stroke(colour, width, fill_colour=None, cap="round", alpha=1.0):
    layers = [{"id": "fill", "kind": "fill", "enabled": fill_colour is not None, "opacity": 1.0,
               "paint": {"kind": "solid", "color": "#ff" + (fill_colour or "#000000").lstrip("#").lower()}}]
    layers.append({"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "center",
                   "cap": cap, "join": "round", "opacity": alpha,
                   "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}})
    return layers


def pop(fr, at, n=9):
    """0 → 1 with a small overshoot."""
    x = lin(fr, at, n)
    return 0.0 if x <= 0 else min(1.0, x) * (1 + 0.16 * math.sin(math.pi * min(1.0, x)))


def knob(s, clip, name, fn):
    clip["shapeStyle"].setdefault("keyframes", {})[name] = keys([(u, round(fn(fr, u), 3), "linear")
                                                                 for u, fr in s.each()])


# --- text --------------------------------------------------------------------------------------------------------
def ink_w(text, cap, family, weight):
    """The ink width of `text` when its capitals are `cap` px tall."""
    f = f6._font(family, weight)
    hb = f.getbbox("H")
    bb = f.getbbox(text)
    ink = f.getlength(text[:-1]) + f.getbbox(text[-1])[2] - bb[0]
    return ink * cap / (hb[3] - hb[1])


def tx(s, text, x, top, cap, family, weight, colour, name, align="left", **kw):
    """A line whose capitals span [top, top + cap], starting at x (its centre / right with align)."""
    w = ink_w(text, cap, family, weight)
    x0 = x if align == "left" else x - w / 2 if align == "center" else x - w
    return s.say(text, (x0, top, x0 + w, top + cap), family, weight, colour, name, align=align, **kw)


def appear(s, clip, at, stagger=0.03, duration=0.12, preset="fade", unit="character", **kw):
    s.letters(clip, at, stagger=stagger, duration=duration, preset=preset, unit=unit, **kw)
    return clip


# --- pieces ------------------------------------------------------------------------------------------------------
def chrome(s, header=True, dim=0.4):
    """The story interface: progress bars, the account row with the user's logo, and the message field."""
    t = s.t
    if header:
        segs = [(30, 268), (282, 520), (534, 772), (786, 1050)]
        for i, (a, b) in enumerate(segs):
            s.rect(f"Progreso {i + 1}", solid(WHITE, dim), lambda fr, u, a=a, b=b: (a, 84, b, 89))
        s.rect("Progreso (avance)", solid(WHITE), lambda fr, u: (30, 84, 30 + 238 * min(1.0, u / s.dur), 89))
        s.obj("Avatar", solid(WHITE), lambda fr, u: (76, 153, 76, 76, 0, 1), kind="ellipse")
        box = Box(76 - 30, 153 - 30, 60, 60)
        logo = t.photo(t.track("video", "Logo"), "logo-flip", 0.0, s.dur, box, None, label="Tu logo",
                       brandRole="logo")
        t.mask(next(tr for tr in t.tracks if logo in tr.clips), logo, "ellipse")
        tx(s, "Your Channel", 138, 141, 24, I, 700, WHITE, "Cuenta")
        tx(s, "12h", 138 + ink_w("Your Channel", 24, I, 700) + 22, 141, 24, I, 500, WHITE, "Cuenta (hora)",
           op=lambda fr, u: 0.7)
    s.obj("Mensaje", stroke(WHITE, 3, alpha=0.9), lambda fr, u: (477, 1837, 854, 104, 0, 1), radius=52)
    tx(s, "Send Message", 100, 1825, 25, I, 500, WHITE, "Mensaje (texto)")
    s.obj("Enviar", stroke(WHITE, 4, cap="round"), lambda fr, u: (1000, 1837, 58, 58, 0, 1), path=PLANE)
    return logo if header else None


def heart(s, name, cx, cy, size, colour, at, n=9, op=1.0, drift=0.0, rot=0.0):
    s.obj(name, solid(colour), lambda fr, u: (cx, cy - drift * u, size * pop(fr, at, n), size * 0.94 * pop(fr, at, n),
                                              rot, op), path=HEART, base=(size, size * 0.94))


def star(s, name, cx, cy, size, at, n=9, spin=40.0, colour=YELLOW):
    s.obj(name, solid(colour), lambda fr, u: (cx, cy, size * pop(fr, at, n), size * pop(fr, at, n),
                                              spin * k(fr, at, n + 9), 1), path=STAR, base=(size, size))


def eye(s, name, cx, cy, w, at, n=10, rot=0.0, blink=None, outline=6, spin=None):
    """An eye sticker: a white almond with a black rim, a black iris and a yellow star; blink(fr) squashes it."""
    def g(fr, u, sw, sh):
        p = pop(fr, at, n)
        sq = blink(fr) if blink else 1.0
        r = rot + (spin(fr) if spin else 0.0)
        return cx, cy, sw * p, sh * p * sq, r, 1.0 if p > 0 else 0.0
    s.obj(name, stroke(INK, outline, WHITE), lambda fr, u: g(fr, u, w, w * 0.56), path=ALMOND, base=(w, w * 0.56))
    s.obj(f"{name} (iris)", solid(INK), lambda fr, u: g(fr, u, w * 0.44, w * 0.44), kind="ellipse",
          base=(w * 0.44, w * 0.44))
    s.obj(f"{name} (estrella)", solid(YELLOW), lambda fr, u: g(fr, u, w * 0.27, w * 0.27), path=STAR,
          base=(w * 0.27, w * 0.27))


def note(s, name, cx, cy, size, geom=None, at=0, n=9, white=WHITE):
    """A note with cyan and red copies offset behind it (the social icon of the reference)."""
    def g(fr, u, ox, oy):
        if geom:
            x, y, sc, op = geom(fr, u)
        else:
            x, y, sc, op = cx, cy, pop(fr, at, n), 1.0
        return x + ox * size * sc, y + oy * size * sc, size * 0.9 * sc, size * sc, 0, op
    s.obj(f"{name} (cian)", solid("#25F4EE"), lambda fr, u: g(fr, u, -0.05, -0.04), path=NOTE,
          base=(size * 0.9, size))
    s.obj(f"{name} (rojo)", solid("#FE2C55"), lambda fr, u: g(fr, u, 0.05, 0.04), path=NOTE, base=(size * 0.9, size))
    s.obj(name, solid(white), lambda fr, u: g(fr, u, 0, 0), path=NOTE, base=(size * 0.9, size))


def oval(s, name, cx, cy, w, h, rot, colour, at, n=9, text=None, ink=WHITE, cap=24, text_at=None, weight=800,
         outline=None, italic=False):
    """A filled (or outlined) ellipse that grows from its centre, with a word on it."""
    layers = stroke(outline, 3) if outline else solid(colour)
    s.obj(name, layers, lambda fr, u: (cx, cy, w * pop(fr, at, n), h * pop(fr, at, n), rot, 1), kind="ellipse",
          base=(w, h))
    if text:
        ta = text_at if text_at is not None else at + n // 2
        c = tx(s, text, cx, cy - cap / 2, cap, I, weight, ink, f"{name} (texto)", align="center",
               geom=lambda fr, u: (0, 0, 1, rot, 1), italic=italic)
        appear(s, c, ta, stagger=0.025, duration=0.08)
        return c


def ellipse_line(s, name, cx, cy, w, h, rot, colour, width, at, n=12, alpha=1.0):
    """A thin ellipse that draws itself."""
    c = s.obj(name, stroke(colour, width, alpha=alpha), lambda fr, u: (cx, cy, w, h, rot, 1), path=ring_path(48),
              base=(w, h))
    knob(s, c, "trimEnd", lambda fr, u: 100 * k(fr, at, n))
    return c


def card(s, sample, rect, radius, name="Foto", label="Tu foto", geom=None, reveal=None, op=None):
    """A photo slot with rounded corners (a track matte): geom(fr, u) = (dx, dy, scale) moves it; reveal(fr, u) =
    (x0, y0, x1, y1) shows only that part of the card."""
    x0, y0, x1, y1 = rect
    w, h = x1 - x0, y1 - y0

    def shape(fr, u):
        if reveal:
            a, b, c, d = reveal(fr, u)
            return (a + c) / 2, (b + d) / 2, max(0.0, c - a), max(0.0, d - b), 0, 1
        dx, dy, sc = geom(fr, u) if geom else (0, 0, 1)
        return (x0 + x1) / 2 + dx, (y0 + y1) / 2 + dy, w * sc, h * sc, 0, op(fr, u) if op else 1
    m = s.obj(f"{name} (forma)", solid(WHITE), shape, radius=radius, base=(w, h))
    ph = photo(s, sample, box=rect, name=name, label=label, geom=geom if not reveal else None)
    ph["matte"] = {"clip": m["id"], "mode": "alpha"}
    return ph


def round_photo(s, sample, cx, cy, d, name, label, geom):
    """A round photo: geom(fr, u) = (dx, dy, scale)."""
    ph = photo(s, sample, box=(cx - d / 2, cy - d / 2, cx + d / 2, cy + d / 2), name=name, label=label, geom=geom,
               oval=True)
    return ph


def bg(s, colour):
    return s.rect("Fondo", solid(colour), lambda fr, u: (-10, -10, W + 10, H + 10))


def layout(t):
    """In a normal (horizontal) video the story keeps its shape as one column; the background stretches."""
    for track in t.tracks:
        for clip in track.clips:
            if clip.get("type") in ("audio", "adjustment", "composite") or "layoutRole" in clip:
                continue
            name = clip.get("name") or track.name
            clip["layoutRole"] = "backdrop" if name.startswith("Fondo") else "art"
    return t


def arrow_ur(s, name, cx, cy, size, colour, at, width=5):
    s.obj(name, stroke(colour, width, cap="butt"), lambda fr, u: (cx, cy, size, size, 0, k(fr, at, 6)),
          path=ARROW_UR, base=(size, size))


def share_btn(s, name, cx, cy, d, at, back=RED, ink=WHITE):
    s.obj(name, solid(back), lambda fr, u: (cx, cy, d * pop(fr, at), d * pop(fr, at), 0, 1), kind="ellipse",
          base=(d, d))
    s.obj(f"{name} (flecha)", solid(ink), lambda fr, u: (cx, cy + d * 0.02, d * 0.46 * pop(fr, at + 2),
                                                          d * 0.36 * pop(fr, at + 2), 0, 1), path=SHARE,
          base=(d * 0.46, d * 0.36))


def cam_btn(s, name, cx, cy, d, at, back=RED):
    s.obj(name, solid(back), lambda fr, u: (cx, cy, d * pop(fr, at), d * pop(fr, at), 0, 1), kind="ellipse",
          base=(d, d))
    s.obj(f"{name} (cámara)", solid(WHITE), lambda fr, u: (cx, cy, d * 0.4 * pop(fr, at + 2),
                                                           d * 0.3 * pop(fr, at + 2), 0, 1), path=CAMERA,
          base=(d * 0.4, d * 0.3))


def bubble(s, name, cx, cy, w, h, colour, at, tail=(0.62, 0.42), ring_colour=None, tail_rot=20):
    """A speech bubble: an ellipse with a tail under its right side, popping from its centre."""
    tx_, ty_ = tail
    s.obj(f"{name} (pico)", solid(colour), lambda fr, u: (cx + w * (tx_ - 0.5 + 0.1) * pop(fr, at),
                                                         cy + h * ty_ * pop(fr, at), w * 0.22 * pop(fr, at),
                                                         h * 0.42 * pop(fr, at), tail_rot, 1), path=BUBBLE_TAIL,
          base=(w * 0.22, h * 0.42))
    s.obj(name, solid(colour), lambda fr, u: (cx, cy, w * pop(fr, at), h * pop(fr, at), 0, 1), kind="ellipse",
          base=(w, h))
    if ring_colour:
        s.obj(f"{name} (aro)", stroke(ring_colour, 2.5, alpha=0.8),
              lambda fr, u: (cx, cy, w * 0.84 * pop(fr, at), h * 0.74 * pop(fr, at), 0, 1), kind="ellipse",
              base=(w * 0.84, h * 0.74))


# --- 1. Austin Grant: a red name, a photo, «new video» and a white «follow» pill sliding in -------------------------
def austin():
    E = 66
    D = dur_for(E)
    t = _p("austin", "Historia: Austin Grant con video nuevo", "Story: Austin Grant with a new video", 14200, D,
           ["nombre", "foto", "negro", "rojo"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, DARK)
    chrome(s)
    card(s, "man-03", (440, 567, 1020, 1425), 40, geom=lambda fr, u: (200 * (1 - k(fr, 0, 12)), 0, 1),
         op=lambda fr, u: k(fr, 0, 6))
    appear(s, s.say("Austin", (70, 317, 940, 450), A, 900, RED, "Nombre", align="left"), 0, 0.04, 0.12)
    appear(s, s.say("Grant", (60, 483, 830, 617), A, 900, RED, "Apellido", align="left"), 6, 0.04, 0.12)
    c = s.say("new", (30, 1225, 306, 1292), A, 900, WHITE, "Texto", align="left", reveal=lambda fr: (0, 1190, 420, 1296))
    appear(s, c, 15, 0.0, 0.25, preset="rise", unit="word")
    c = s.say("video", (30, 1297, 380, 1363), A, 900, WHITE, "Texto 2", align="left",
              reveal=lambda fr: (0, 1296, 420, 1380))
    appear(s, c, 21, 0.0, 0.25, preset="rise", unit="word")
    appear(s, tx(s, "fashion", 30, 1470, 27, I, 800, WHITE, "Texto 3"), 21, 0.03, 0.08)
    appear(s, tx(s, "inspiration", 30, 1508, 27, I, 800, WHITE, "Texto 4"), 24, 0.03, 0.08)
    s.obj("Punto", solid(RED), lambda fr, u: (210, 950, 18 * pop(fr, 54), 18 * pop(fr, 54), 0, 1), kind="ellipse",
          base=(18, 18))
    slide = lambda fr: 720 * (1 - k(fr, 48, 12))  # noqa: E731
    s.obj("Botón", solid(WHITE), lambda fr, u: (740 + slide(fr), 1497, 720, 122, 0, 1), radius=61)
    s.obj("Botón (punto)", solid(RED), lambda fr, u: (600 + slide(fr), 1500, 16 * pop(fr, 54), 16 * pop(fr, 54), 0, 1),
          kind="ellipse", base=(16, 16))
    c = tx(s, "follow", 650, 1482, 34, I, 800, INK, "Botón (texto)", shift=lambda fr: (slide(fr), 0),
           reveal=lambda fr: (380, 1430, W, 1560))
    appear(s, c, 54, 0.06, 0.05, preset="typewriter")
    return layout(t)


# --- 2. follow: the red word typed over a grey heart, a SHARE bubble, the channel in an oval, tags below -----------
def follow():
    E = 51
    D = dur_for(E)
    t = _p("follow", "Historia: follow con corazón", "Story: follow with a heart", 14201, D,
           ["seguir", "corazón", "negro", "rojo"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, "#0B0B0B")
    chrome(s)
    s.obj("Corazón grande", solid("#2A2A2A"), lambda fr, u: (520, 900, 820 * k(fr, 0, 9), 760 * k(fr, 0, 9), -8,
                                                              k(fr, 0, 6)), path=HEART, base=(820, 760))
    s.obj("Corazón chico", solid("#2A2A2A"), lambda fr, u: (790, 1283, 170 * k(fr, 3, 9), 150 * k(fr, 3, 9), 6,
                                                             k(fr, 3, 6)), path=HEART, base=(170, 150))
    c = s.say("follow", (20, 817, 1000, 1000), A, 900, RED, "Título", align="left")
    appear(s, c, 6, 0.08, 0.12, preset="pop")
    star(s, "Chispa", 250, 842, 120, 18)
    share_btn(s, "Compartir", 790, 663, 110, 21)
    s.obj("Punto rojo", solid(RED), lambda fr, u: (860, 613, 20 * pop(fr, 24), 20 * pop(fr, 24), 0, 1),
          kind="ellipse", base=(20, 20))
    bubble(s, "Burbuja", 150, 492, 230, 130, BLUE, 18, ring_colour=WHITE)
    c = tx(s, "SHARE", 150, 483, 18, I, 900, WHITE, "Burbuja (texto)", align="center")
    appear(s, c, 22, 0.03, 0.08)
    ellipse_line(s, "Óvalo", 654, 380, 630, 167, -3, BLUE, 3, 21, 9)
    c = tx(s, "@yourchannel", 640, 362, 26, I, 700, WHITE, "Canal", align="center", geom=lambda fr, u: (0, 0, 1, -3, 1))
    appear(s, c, 30, 0.04, 0.05, preset="typewriter")
    s.obj("Punto amarillo", solid(YELLOW), lambda fr, u: (968, 400, 24 * pop(fr, 36), 24 * pop(fr, 36), 0, 1),
          kind="ellipse", base=(24, 24))
    oval(s, "Etiqueta 1", 160, 1505, 270, 80, -5, BLUE, 36, text="#follow", cap=24)
    oval(s, "Etiqueta 2", 536, 1478, 240, 76, -4, BLUE, 39, text="#share", cap=24, outline=WHITE)
    appear(s, tx(s, "#like", 900, 1442, 24, I, 700, WHITE, "Etiqueta 3", align="center"), 45, 0.04, 0.06,
           preset="typewriter")
    return layout(t)


# --- 3. the logo card: rings and a photo, a black card opens wide with the logo, stickers pop round it ------------
def logo_card():
    E = 57
    D = dur_for(E)
    t = _p("tarjeta", "Historia: tarjeta con tu logo y stickers", "Story: a card with your logo and stickers", 14202,
           D, ["logo", "stickers", "azul"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, BLUE)
    logo = chrome(s)
    for i, d in enumerate((1120, 800)):
        s.obj(f"Anillo {i + 1}", stroke(WHITE, 2.5, alpha=0.65), lambda fr, u, d=d, i=i: (540, 950, d * (0.9 + 0.1 * k(
            fr, 3 * i, 12)), d * (0.9 + 0.1 * k(fr, 3 * i, 12)), 0, k(fr, 3 * i, 9)), kind="ellipse", base=(d, d))
    card(s, "portrait-01", (296, 625, 730, 1292), 40, geom=lambda fr, u: (0, 60 * (1 - k(fr, 0, 12)), 1),
         op=lambda fr, u: k(fr, 0, 6))
    cw = lambda fr: 140 + 580 * k(fr, 27, 15)  # noqa: E731
    ch = lambda fr: 420 - 0 * fr  # noqa: E731
    on = lambda fr: 1.0 if fr >= 24 else 0.0  # noqa: E731
    s.obj("Tarjeta (borde)", stroke(BLUE, 4), lambda fr, u: (540 + 20, 937 - 17, cw(fr) * pop(fr, 24, 6) ** 0,
                                                            ch(fr) * pop(fr, 24, 6), 0, on(fr)), radius=60,
          base=(720, 420))
    s.obj("Tarjeta", stroke("#0E0E0E", 1, "#0E0E0E"), lambda fr, u: (520, 937, cw(fr), ch(fr) * pop(fr, 24, 6), 0,
                                                                    on(fr)), radius=60, base=(720, 420))
    box = Box(520 - 115, 937 - 115, 230, 230)
    t.photo(t.track("video", "Logo grande"), "logo-flip", 0.0, D, box,
            [(u, {"s": max(1e-4, pop(fr, 33, 12))}, "linear") for u, fr in s.each()], label="Tu logo",
            brandRole="logo", reuse=logo["placeholderId"])
    star(s, "Chispa", 720, 592, 180, 30)
    s.obj("Comentario", stroke(WHITE, 4), lambda fr, u: (950, 675, 104 * pop(fr, 27), 92 * pop(fr, 27), 0, 1),
          kind="ellipse", base=(104, 92))
    for i, dx in enumerate((-22, 0, 22)):
        s.obj(f"Comentario (punto {i + 1})", solid(WHITE), lambda fr, u, dx=dx: (950 + dx, 675, 12 * pop(fr, 30),
                                                                                12 * pop(fr, 30), 0, 1),
              kind="ellipse", base=(12, 12))
    s.obj("Ojo (fondo)", solid(RED), lambda fr, u: (900, 1083, 260 * pop(fr, 30), 230 * pop(fr, 30), -15, 1),
          kind="ellipse", base=(260, 230))
    eye(s, "Ojo", 900, 1083, 170, 33, rot=-10)
    s.obj("Diana", stroke(INK, 18), lambda fr, u: (96, 405, 100 * pop(fr, 33), 100 * pop(fr, 33), 0, 1),
          kind="ellipse", base=(100, 100))
    s.obj("Diana (centro)", solid(BLUE), lambda fr, u: (96, 405, 30 * pop(fr, 36), 30 * pop(fr, 36), 0, 1),
          kind="ellipse", base=(30, 30))
    share_btn(s, "Flecha", 1026, 345, 100, 33, back=WHITE, ink=INK)
    bubble(s, "Burbuja", 130, 730, 230, 150, WHITE, 51, tail=(0.6, 0.38))
    appear(s, tx(s, "#NEW", 120, 718, 22, I, 800, INK, "Burbuja (texto)", align="center"), 54, 0.03, 0.06)
    c = tx(s, "#", 64, 1222, 110, A, 900, BLUE, "Numeral", align="center",
           geom=lambda fr, u: (0, 0, max(0.001, pop(fr, 30)), -8, 1))
    c["textStyle"]["layers"] = stroke(WHITE, 5, BLUE)
    s.obj("Corazón (botón)", solid(WHITE), lambda fr, u: (40, 1460, 76 * pop(fr, 27), 76 * pop(fr, 27), 0, 1),
          kind="ellipse", base=(76, 76))
    heart(s, "Corazón", 40, 1460, 36, RED, 29)
    s.obj("Punto negro", solid(INK), lambda fr, u: (320, 1467, 90 * pop(fr, 30), 90 * pop(fr, 30), 0, 1),
          kind="ellipse", base=(90, 90))
    s.obj("Más", solid(WHITE), lambda fr, u: (874, 1458, 100 * pop(fr, 36), 100 * pop(fr, 36), 0, 1), kind="ellipse",
          base=(100, 100))
    for i, (w, h) in enumerate(((34, 4), (4, 34))):
        s.obj(f"Más (signo {i + 1})", solid(RED), lambda fr, u, w=w, h=h: (874, 1458, w * pop(fr, 39), h * pop(fr, 39),
                                                                          0, 1), base=(w, h))
    return layout(t)


# --- 4. Isabella Walker: the name types, the photo rises, hearts, an eye sticker and two hashtags ----------------
def isabella():
    E = 66
    D = dur_for(E)
    t = _p("isabella", "Historia: Isabella Walker con foto", "Story: Isabella Walker with a photo", 14203, D,
           ["nombre", "foto", "azul"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, BLUE)
    chrome(s)
    heart(s, "Corazón claro 1", 120, 1200, 280, "#63D5FF", 21, 12)
    heart(s, "Corazón claro 2", 930, 1410, 230, "#63D5FF", 24, 12)
    card(s, "fx-woman-02", (230, 625, 840, 1617), 50, geom=lambda fr, u: (0, 260 * (1 - k(fr, 9, 15)), 1),
         op=lambda fr, u: k(fr, 9, 6))
    appear(s, s.say("Isabella", (34, 340, 820, 467), A, 900, INK, "Nombre", align="left"), 0, 0.035, 0.1)
    appear(s, s.say("Walker", (50, 483, 750, 600), A, 900, INK, "Apellido", align="left"), 9, 0.035, 0.1)
    heart(s, "Corazón 1", 30, 552, 44, WHITE, 24, drift=40)
    heart(s, "Corazón 2", 975, 1300, 52, WHITE, 30, drift=50)
    heart(s, "Corazón 3", 160, 1570, 36, WHITE, 36, drift=30)
    eye(s, "Ojo", 830, 717, 280, 36, n=12, rot=-15, spin=lambda fr: -40 * (1 - k(fr, 36, 12)))
    oval(s, "Etiqueta roja", 780, 1542, 430, 190, -25, RED, 45, n=12, text="#makeup", cap=34, text_at=51)
    ellipse_line(s, "Óvalo", 250, 1050, 480, 158, -8, WHITE, 3, 54, 12)
    appear(s, tx(s, "#skincare", 290, 1038, 28, I, 800, WHITE, "Etiqueta", align="center",
                 geom=lambda fr, u: (0, 0, 1, -8, 1)), 57, 0.03, 0.06)
    return layout(t)


# --- 5. trends: a red band whose words run left, a photo, side counters, hearts and a #dancechallenge oval -------
def trends():
    E = 45
    D = dur_for(E)
    t = _p("tendencias", "Historia: tendencias con franja roja", "Story: trends with a red band", 14204, D,
           ["tendencias", "foto", "azul", "rojo"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, BLUE)
    chrome(s)
    heart(s, "Corazón claro 1", 40, 770, 220, "#63D5FF", 15, 12)
    heart(s, "Corazón claro 2", 950, 1270, 220, "#63D5FF", 18, 12)
    sc = lambda fr: 0.85 + 0.15 * k(fr, 0, 12)  # noqa: E731
    card(s, "fx-dancer-03", (160, 417, 860, 1483), 50, geom=lambda fr, u: (0, 0, sc(fr)), op=lambda fr, u: k(fr, 0, 6))
    band = lambda fr: (-20, 304, -20 + 1140 * k(fr, 0, 9), 420)  # noqa: E731
    s.rect("Franja", solid(RED), lambda fr, u: band(fr), rot=lambda fr, u: -2)
    words = "trends • challenges • trends • challenges • trends • challenges • trends • challenges"
    w = ink_w(words, 34, I, 800)
    c = s.say(words, (-60, 345, -60 + w, 379), I, 800, WHITE, "Franja (texto)", align="left",
              reveal=lambda fr: band(fr), shift=lambda fr: (-160 * fr / FPS, 0), rot=lambda fr, u: -2)
    del c
    for i, (y, label) in enumerate(((1067, "3.5k"), (1170, "250"), (1265, "520"))):
        at = 12 + 3 * i
        if i == 0:
            heart(s, "Contador (corazón)", 800, y, 52, WHITE, at)
        elif i == 1:
            s.obj("Contador (comentario)", solid(WHITE), lambda fr, u, at=at, y=y: (800, y, 52 * pop(fr, at),
                                                                                    46 * pop(fr, at), 0, 1),
                  kind="ellipse", base=(52, 46))
        else:
            s.obj("Contador (compartir)", solid(WHITE), lambda fr, u, at=at, y=y: (800, y, 52 * pop(fr, at),
                                                                                   44 * pop(fr, at), 0, 1),
                  path=SHARE, base=(52, 44))
        appear(s, tx(s, label, 800, y + 34, 16, I, 700, WHITE, f"Contador {i + 1}", align="center"), at + 3,
               0.03, 0.06)
    heart(s, "Corazón 1", 120, 533, 100, WHITE, 15, drift=40)
    heart(s, "Corazón 2", 1000, 833, 70, WHITE, 21, drift=50)
    oval(s, "Etiqueta", 420, 1450, 680, 233, -12, RED, 33, n=12, text="#dancechallenge", cap=40, text_at=39)
    return layout(t)


# --- 6. Alice Braun: the photo rises, hearts float, the name types, a description -------------------------------
def alice():
    E = 36
    D = dur_for(E)
    t = _p("alice", "Historia: Alice Braun con foto", "Story: Alice Braun with a photo", 14205, D,
           ["nombre", "foto", "azul"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, BLUE)
    chrome(s)
    rise = lambda fr: 700 * (1 - k(fr, 0, 21))  # noqa: E731
    card(s, "portrait-06", (244, 242, 864, 1058), 40, geom=lambda fr, u: (0, rise(fr), 1))
    for i, (x, y, sz, at) in enumerate(((230, 1015, 140, 9), (900, 960, 130, 12), (40, 520, 110, 15))):
        heart(s, f"Corazón claro {i + 1}", x, y, sz, "#9BE6FF", at, 12, op=0.75, drift=60)
    for i, (x, y, sz, at) in enumerate(((540, 590, 44, 6), (676, 800, 40, 12), (946, 1105, 52, 15), (560, 1175, 34, 18),
                                        (720, 1700, 40, 24))):
        heart(s, f"Corazón {i + 1}", x, y, sz, WHITE, at, drift=70)
    appear(s, s.say("Alice", (70, 1175, 596, 1295), A, 900, INK, "Nombre", align="left"), 18, 0.035, 0.1)
    appear(s, s.say("Braun", (70, 1325, 704, 1445), A, 900, INK, "Apellido", align="left"), 24, 0.035, 0.1)
    appear(s, tx(s, "@username Description   # colors", 70, 1512, 30, I, 800, WHITE, "Texto"), 21, 0.012, 0.05)
    appear(s, tx(s, "See translation", 70, 1585, 30, I, 800, WHITE, "Texto 2"), 30, 0.012, 0.05)
    note(s, "Nota", 372, 1600, 34, at=33)
    appear(s, tx(s, "Original sound", 410, 1585, 30, I, 800, WHITE, "Texto 3"), 33, 0.012, 0.05)
    return layout(t)


# --- 7. Social blogger: a round photo settles, notes burst out, rings and blue/red arcs grow round it ------------
def blogger():
    E = 60
    D = dur_for(E)
    t = _p("blogger", "Historia: Social blogger con anillos", "Story: Social blogger with rings", 14206, D,
           ["anillos", "foto", "negro"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, "#030303")
    chrome(s)
    cx, cy = 550, 900
    for i, x in enumerate((60, 210, 890, 1040)):
        s.rect(f"Línea {i + 1}", solid("#6A0000"), lambda fr, u, x=x, i=i: (x - 1.5, H - (H - 1350) * k(fr, 27 + 3 * i, 15),
                                                                           x + 1.5, H))
    for i, (r, colour, wd, at) in enumerate(((780, "#5A0000", 2, 27), (580, "#7A0000", 2, 24), (380, RED, 2.5, 24),
                                             (250, BLUE, 2.5, 27))):
        s.obj(f"Anillo {i + 1}", stroke(colour, wd), lambda fr, u, r=r, at=at: (cx, cy, 2 * r * (0.6 + 0.4 * k(fr, at, 12)),
                                                                              2 * r * (0.6 + 0.4 * k(fr, at, 12)), 0,
                                                                              k(fr, at, 6)),
              kind="ellipse", base=(2 * r, 2 * r))
    R = 410
    for name, colour, a0, a1, at in (("Arco azul", BLUE, -112, -5, 30), ("Arco rojo", RED, 10, 88, 33)):
        c = s.obj(name, stroke(colour, 50), lambda fr, u, at=at: (cx, cy, 2 * R, 2 * R, 0, 1.0 if fr >= at else 0.0),
                  path=arc(a0, a1), base=(2 * R, 2 * R))
        c["shapeStyle"]["keyframes"] = {"trimStart": keys([(0.0, 0.0, "hold")])}
        knob(s, c, "trimEnd", lambda fr, u, at=at: 3 + 97 * k(fr, at, 27))
    sc = lambda fr: 1.8 - 0.8 * k(fr, 0, 24)  # noqa: E731
    round_photo(s, "selfie-02", cx, cy, 360, "Foto", "Tu foto", lambda fr, u: (0, 260 * (1 - k(fr, 0, 24)), sc(fr)))
    a = math.radians(80)
    s.obj("Punto azul", solid(BLUE), lambda fr, u: (cx + 250 * math.cos(a), cy + 250 * math.sin(a), 18 * pop(fr, 36),
                                                    18 * pop(fr, 36), 0, 1), kind="ellipse", base=(18, 18))
    a = math.radians(-58)
    bx, by = cx + R * math.cos(a), cy + R * math.sin(a)
    s.obj("Botón (fondo)", solid("#151515"), lambda fr, u: (bx, by, 171 * pop(fr, 39), 171 * pop(fr, 39), 0, 1),
          kind="ellipse", base=(171, 171))
    cam_btn(s, "Botón", bx, by, 86, 42)
    a = math.radians(-88)
    nx, ny = cx + 253 * math.cos(a), cy + 253 * math.sin(a)
    s.obj("Nota (fondo)", solid(RED), lambda fr, u: (nx, ny, 105 * pop(fr, 39), 105 * pop(fr, 39), 0, 1),
          kind="ellipse", base=(105, 105))
    note(s, "Nota chica", nx, ny, 50, at=42)

    def burst(x1, y1, at, fade=False):
        def g(fr, u):
            p = k(fr, at, 9)
            op = 1.0 if fr >= at else 0.0
            if fade:
                op *= 1 - k(fr, at + 6, 6)
            return cx + (x1 - cx) * p, cy + (y1 - cy) * p, max(0.001, 0.3 + 0.7 * p), op
        return g
    note(s, "Nota grande", 790, 330, 170, geom=burst(790, 330, 18))
    note(s, "Nota", 454, 300, 56, geom=burst(454, 300, 20))
    note(s, "Nota que cae", 250, 1250, 90, geom=burst(250, 1250, 18, fade=True))
    appear(s, tx(s, "Social", 90, 250, 40, A, 800, RED, "Texto"), 45, 0.05, 0.05, preset="typewriter")
    appear(s, tx(s, "blogger", 104, 300, 40, A, 800, RED, "Texto 2"), 51, 0.05, 0.05, preset="typewriter")
    return layout(t)


# --- 8. NEW: a blue bubble grows from a dot, red hearts pop, a share button, a «Do you like it?» card -----------
def new():
    E = 30
    D = dur_for(E)
    t = _p("new", "Historia: NEW con corazones", "Story: NEW with hearts", 14207, D,
           ["nuevo", "foto", "negro", "corazón"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, ASH)
    chrome(s)
    card(s, "makeup-01", (294, 450, 786, 1440), 40)
    s.obj("Punto azul", solid(BLUE), lambda fr, u: (264, 200, 30 * pop(fr, 6), 30 * pop(fr, 6), 0, 1),
          kind="ellipse", base=(30, 30))
    bubble(s, "Burbuja", 310, 333, 280, 125, BLUE, 9, ring_colour=WHITE)
    c = tx(s, "NEW", 300, 314, 38, A, 900, WHITE, "Burbuja (texto)", align="center",
           geom=lambda fr, u: (0, 0, max(0.001, pop(fr, 12)), 8, 1), italic=True)
    del c
    for i, (x, y, sz, at) in enumerate(((970, 240, 100, 9), (880, 360, 72, 12), (750, 275, 42, 15), (910, 535, 26, 18),
                                        (860, 215, 22, 21), (640, 420, 20, 24), (930, 760, 18, 27))):
        heart(s, f"Corazón {i + 1}", x, y, sz, RED, at, drift=30, rot=-10 + 7 * i)
    share_btn(s, "Compartir", 890, 650, 140, 6)
    rc = lambda fr: max(0.001, pop(fr, 3))  # noqa: E731
    s.obj("Pregunta", solid(WHITE), lambda fr, u: (800, 821, 240 * rc(fr), 108 * rc(fr), -10, 1), radius=10,
          base=(240, 108))
    appear(s, tx(s, "Do you like it?", 795, 790, 15, I, 600, INK, "Pregunta (texto)", align="center",
                 geom=lambda fr, u: (0, 0, 1, -10, 1)), 9, 0.02, 0.05)
    s.obj("Pregunta (línea)", solid("#D8D8D8"), lambda fr, u: (806, 838, 180 * k(fr, 9, 9), 4, -10, 1), base=(180, 4))
    heart(s, "Pregunta (corazón)", 880, 824, 26, RED, 12)
    oval(s, "Etiqueta", 290, 1008, 340, 90, -8, RED, 0, n=12, text="#MARKETING", cap=22, text_at=6, weight=900)
    return layout(t)


# --- 9. new video: a red bar pushes the photo down, «new video» rises in it, «alice trendy» rises below ----------
def new_video():
    E = 30
    D = dur_for(E)
    t = _p("nuevo-video", "Historia: new video con foto", "Story: new video with a photo", 14208, D,
           ["video nuevo", "foto", "rojo"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, DARK)
    chrome(s)
    e = lambda fr: k(fr, 6, 9)  # noqa: E731
    down = lambda fr: -108 * (1 - e(fr))  # noqa: E731
    s.rect("Panel", solid("#F6F4F2"), lambda fr, u: (0, 1400 + down(fr), W, 1750 + down(fr)))
    top = lambda fr: 225 + 175 * e(fr)  # noqa: E731
    card(s, "portrait-04", (0, 300, W, 1542), 90,
         reveal=lambda fr, u: (0, 300 + down(fr), W, 1542 + down(fr)))
    s.rect("Franja", solid(RED), lambda fr, u: (0, 222, W, top(fr)))
    c = s.say("new video", (50, 245, 850, 345), A, 800, WHITE, "Título", align="left",
              reveal=lambda fr: (0, 222, W, top(fr)))
    appear(s, c, 15, 0.3, 0.25, preset="rise", unit="word")
    heart(s, "Corazón", 980, 288, 66, WHITE, 6)
    appear(s, tx(s, "105", 980, 332, 12, I, 700, WHITE, "Corazón (cuenta)", align="center"), 9, 0.03, 0.06)
    panel = lambda fr: (0, 1542 + down(fr), W, 1750 + down(fr))  # noqa: E731
    c = s.say("alice trendy", (56, 1597, 856, 1683), A, 800, INK, "Nombre", align="left", reveal=panel,
              shift=lambda fr: (0, down(fr)))
    appear(s, c, 9, 0.3, 0.25, preset="rise", unit="word")
    s.obj("Flecha", stroke(INK, 6, cap="butt"), lambda fr, u: (968, 1640 + down(fr), 84, 84, 0, k(fr, 6, 6)),
          path=ARROW_UR, base=(84, 84))
    return layout(t)


# --- 10. #lifestyle: a red band with an eye that blinks and a blue #lifestyle oval over a video ------------------
def lifestyle():
    E = 30
    D = dur_for(E)
    t = _p("lifestyle", "Historia: #lifestyle con video", "Story: #lifestyle with a video", 14209, D,
           ["estilo de vida", "video", "rojo"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, DARK)
    chrome(s)
    photo(s, "interior-03", box=(0, 558, W, 1742), name="Foto", label="Tu video o foto")
    s.rect("Sombra", [gradient([(0.0, "#000000", 0.0), (1.0, "#000000", 0.6)], angle=90)],
           lambda fr, u: (0, 1150, W, 1742))
    s.rect("Franja", solid(RED), lambda fr, u: (0, 217, W, 558))
    blink = lambda fr: 1 - 0.9 * math.sin(math.pi * lin(fr, 24, 6))  # noqa: E731
    eye(s, "Ojo", 250, 395, 240, 3, rot=-10, blink=blink, outline=8)
    oval(s, "Etiqueta", 786, 413, 430, 125, -8, BLUE, 6, text="#lifestyle", cap=28, text_at=12)
    for i, (y, line) in enumerate(((1255, "@username  ·  5h ago"), (1307, "Description   # cake"),
                                   (1360, "See translation"), (1412, "     Original sound"))):
        appear(s, tx(s, line, 100, y, 26, I, 700, WHITE, f"Texto {i + 1}"), 3 + 3 * i, 0.012, 0.05)
    note(s, "Nota", 112, 1425, 30, at=12)
    s.obj("Panel", solid("#141414"), lambda fr, u: (515, 1640, 710, 250, 0, 1), radius=60)
    heart(s, "Me gusta", 326, 1662, 58, WHITE, 0)
    s.obj("Comentar", solid(WHITE), lambda fr, u: (516, 1662, 58 * pop(fr, 3), 52 * pop(fr, 3), 0, 1), kind="ellipse",
          base=(58, 52))
    for i, dx in enumerate((-14, 0, 14)):
        s.obj(f"Comentar (punto {i + 1})", solid("#141414"), lambda fr, u, dx=dx: (516 + dx, 1662, 9 * pop(fr, 6),
                                                                                  9 * pop(fr, 6), 0, 1),
              kind="ellipse", base=(9, 9))
    s.obj("Compartir", solid(WHITE), lambda fr, u: (704, 1662, 60 * pop(fr, 6), 50 * pop(fr, 6), 0, 1), path=SHARE,
          base=(60, 50))
    cam_btn(s, "Grabar", 890, 1522, 170, 0)
    return layout(t)


# --- 11. profile: typed counters on red, a round photo, the name card and #foodblogger ---------------------------
def profile():
    E = 40
    D = dur_for(E)
    t = _p("perfil", "Historia: perfil con seguidores", "Story: a profile with followers", 14210, D,
           ["perfil", "seguidores", "foto", "rojo", "azul"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, DARK)
    chrome(s)
    photo(s, "cooking-04", box=(0, 437, W, 867), name="Foto", label="Foto 1")
    rise = lambda fr: 433 * k(fr, 24, 12)  # noqa: E731
    photo(s, "cake-02", box=(0, 1317, 540, 1750), name="Foto 2", label="Foto 2",
          rect=lambda fr, u: (0, 1750 - rise(fr), 540, 1750))
    s.rect("Panel blanco", solid(WHITE), lambda fr, u: (540, 1433, W, 1750))
    appear(s, tx(s, "#foodblogger", 815, 1672, 32, I, 800, INK, "Etiqueta", align="center"), 0, 0.05, 0.05,
           preset="typewriter")
    s.rect("Franja", solid(RED), lambda fr, u: (0, 225, W, 437))
    for i, (x, num, lab) in enumerate(((200, "235", "Following"), (554, "370K", "Followers"), (886, "980K", "Likes"))):
        appear(s, tx(s, num, x, 258, 50, I, 800, WHITE, f"Número {i + 1}", align="center"), 3 * i, 0.08, 0.05,
               preset="typewriter")
        appear(s, tx(s, lab, x, 330, 19, I, 700, WHITE, f"Número {i + 1} (texto)", align="center"), 3 + 3 * i,
               0.03, 0.05, preset="typewriter")
    ellipse_line(s, "Óvalo", 554, 315, 310, 183, 0, WHITE, 3, 9, 9)
    s.obj("Tarjeta", solid(DARK), lambda fr, u: (272, 1092, 545, 450, 0, 1), radius=70)
    s.obj("Aro", solid(RED), lambda fr, u: (254, 1063, 252 * pop(fr, 24, 12), 252 * pop(fr, 24, 12), 0, 1),
          kind="ellipse", base=(252, 252))
    round_photo(s, "garden-02", 254, 1063, 228, "Foto 3", "Foto 3",
                lambda fr, u: (0, 0, max(0.001, pop(fr, 24, 12))))
    appear(s, tx(s, "@emilyroberts", 254, 1186, 22, I, 700, WHITE, "Usuario", align="center"), 27, 0.04, 0.05,
           preset="typewriter")
    s.obj("Verificado", solid(BLUE), lambda fr, u: (424, 1197, 24 * pop(fr, 36), 24 * pop(fr, 36), 0, 1),
          kind="ellipse", base=(24, 24))
    s.obj("Tarjeta azul", solid(BLUE), lambda fr, u: (805, 1150, 510, 566, 0, 1), radius=70)
    s.say("Emily", (584, 963, 814, 1025), A, 800, WHITE, "Nombre", align="left")
    s.say("Roberts", (584, 1053, 930, 1113), A, 800, WHITE, "Apellido", align="left")
    for i, line in enumerate(("Chef, wife, mom", "genius food hacks", "to do when you're", "bored at home")):
        tx(s, line, 584, 1150 + 36 * i, 21, I, 700, WHITE, f"Descripción {i + 1}")
    heart(s, "Corazón", 630, 1553, 66, RED, 0)
    arrow_ur(s, "Flecha", 1006, 1558, 34, WHITE, 0, width=3)
    return layout(t)


# --- 12. Different content: a red title, a photo with a Discover pill, a grid of four photos with tags ----------
def different():
    E = 36
    D = dur_for(E)
    t = _p("contenido", "Historia: contenido variado con cuadrícula", "Story: different content in a grid", 14211,
           D, ["cuadrícula", "fotos", "negro", "rojo"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, DARK)
    chrome(s)
    appear(s, s.say("Different content", (120, 287, 980, 350), I, 800, RED, "Título"), 0, 0.025, 0.12)
    card(s, "fx-face-03", (136, 488, 970, 825), 40, label="Foto 1", geom=lambda fr, u: (0, 120 * (1 - k(fr, 3, 12)), 1),
         op=lambda fr, u: k(fr, 3, 6))
    for i, (sample, r, at) in enumerate((("fx-man-01", (24, 943, 554, 1263), 9),
                                         ("concert-02", (604, 943, 1070, 1263), 12),
                                         ("fx-walk-02", (24, 1305, 446, 1647), 15),
                                         ("creator-02", (494, 1305, 1070, 1647), 18))):
        photo(s, sample, box=r, name=f"Foto {i + 2}", label=f"Foto {i + 2}",
              geom=lambda fr, u, at=at: (0, 0, max(0.001, 0.6 + 0.4 * k(fr, at, 9))),
              op=lambda fr, u, at=at: k(fr, at, 6))
    pw = lambda fr: 336 * k(fr, 21, 9)  # noqa: E731
    s.rect("Discover", solid(RED), lambda fr, u: (104, 745, 104 + pw(fr), 805), radius=30)
    s.obj("Discover (lupa)", stroke(WHITE, 4), lambda fr, u: (146, 771, 26 * pop(fr, 27), 26 * pop(fr, 27), 0, 1),
          kind="ellipse", base=(26, 26))
    s.obj("Discover (mango)", solid(WHITE), lambda fr, u: (160, 788, 4, 14 * pop(fr, 27), -45, 1), base=(4, 14))
    appear(s, tx(s, "Discover", 180, 764, 24, I, 700, WHITE, "Discover (texto)"), 27, 0.04, 0.05,
           preset="typewriter")
    s.obj("Etiqueta 1 (fondo)", solid(WHITE, 0.35), lambda fr, u: (450, 1158, 160 * pop(fr, 24), 74 * pop(fr, 24), -10,
                                                                   1), kind="ellipse", base=(160, 74))
    appear(s, tx(s, "#fun", 450, 1148, 20, I, 800, YELLOW, "Etiqueta 1", align="center",
                 geom=lambda fr, u: (0, 0, 1, -10, 1)), 27, 0.03, 0.05)
    s.obj("Etiqueta 2 (fondo)", solid(WHITE, 0.35), lambda fr, u: (190, 1483, 190 * pop(fr, 27), 74 * pop(fr, 27), -20,
                                                                   1), kind="ellipse", base=(190, 74))
    appear(s, tx(s, "#coollife", 190, 1473, 20, I, 800, YELLOW, "Etiqueta 2", align="center",
                 geom=lambda fr, u: (0, 0, 1, -20, 1)), 30, 0.03, 0.05)
    oval(s, "Etiqueta 3", 636, 1480, 236, 86, -15, BLUE, 30, text="#lessons", cap=20)
    return layout(t)


# --- 13. About Beauty for You: red words, a photo rises, a white pill opens to an @user, a red oval with a list ---
def beauty():
    E = 60
    D = dur_for(E)
    t = _p("belleza", "Historia: About Beauty for You", "Story: About Beauty for You", 14212, D,
           ["belleza", "foto", "negro", "rojo"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, NAVY)
    chrome(s)
    card(s, "makeup-02", (516, 500, 1016, 1275), 40, geom=lambda fr, u: (0, 250 * (1 - k(fr, 0, 12)), 1),
         op=lambda fr, u: k(fr, 0, 6))
    for i, (word, ink, at) in enumerate((("About", (84, 628, 464, 708), 0), ("Beauty", (84, 742, 524, 828), 3),
                                         ("for You", (90, 853, 534, 940), 6))):
        appear(s, s.say(word, ink, A, 900, RED, ("Título", "Título 2", "Título 3")[i], align="left"), at,
               0.18 if i == 2 else 0.03, 0.08, unit="word" if i == 2 else "character")
    ellipse_line(s, "Óvalo azul", 450, 895, 370, 133, -10, BLUE, 2.5, 24, 12)

    def pill(fr, u):
        d = 92 * pop(fr, 6, 15)
        x0 = 668 - 592 * k(fr, 27, 12)
        return (x0 + 760) / 2, 341, max(d, 760 - x0), d, 0, 1.0 if fr >= 6 else 0.0
    s.obj("Usuario", solid(WHITE), pill, radius=46, base=(684, 92))
    s.obj("Usuario (azul)", solid(BLUE), lambda fr, u: (672, 341, 26 * pop(fr, 33), 26 * pop(fr, 33), 0, 1),
          kind="ellipse", base=(26, 26))
    s.obj("Usuario (rojo)", solid(RED), lambda fr, u: (692, 341, 26 * pop(fr, 34), 26 * pop(fr, 34), 0, 1),
          kind="ellipse", base=(26, 26))
    appear(s, tx(s, "@alicebraun99", 136, 327, 27, I, 600, RED, "Usuario (texto)"), 45, 0.04, 0.05,
           preset="typewriter")
    oval(s, "Lista", 426, 1195, 610, 233, -8, RED, 24, n=15)
    for i, (dot, word, at) in enumerate(((WHITE, "fashion", 51), (INK, "health", 54), (WHITE, "sport and yoga", 57))):
        x, y = 330 + 12 * i, 1146 + 46 * i
        s.obj(f"Lista (punto {i + 1})", solid(dot), lambda fr, u, x=x, y=y, at=at: (x, y, 15 * pop(fr, at),
                                                                                    15 * pop(fr, at), 0, 1),
              kind="ellipse", base=(15, 15))
        appear(s, tx(s, word, x + 30, y - 11, 22, I, 700, WHITE, f"Lista {i + 1}", geom=lambda fr, u: (0, 0, 1, -8, 1)),
               at, 0.03, 0.05, preset="typewriter")
    oval(s, "Etiqueta", 796, 1437, 330, 108, 5, BLUE, 12, n=6, text="#lifestyle", cap=26)
    appear(s, tx(s, "#alicelife", 260, 1484, 24, I, 700, BLUE, "Etiqueta 2", align="center",
                 geom=lambda fr, u: (0, 0, 1, -35, 1)), 21, 0.04, 0.05, preset="typewriter")
    ellipse_line(s, "Etiqueta 3 (óvalo)", 480, 1567, 140, 62, -25, BLUE, 2, 27, 6)
    appear(s, tx(s, "#fun", 480, 1555, 24, I, 700, BLUE, "Etiqueta 3", align="center",
                 geom=lambda fr, u: (0, 0, 1, -25, 1)), 27, 0.04, 0.05, preset="typewriter")
    appear(s, tx(s, "#new fashion", 390, 1685, 24, I, 700, RED, "Etiqueta 4", align="center",
                 geom=lambda fr, u: (0, 0, 1, 10, 1)), 39, 0.04, 0.05, preset="typewriter")
    return layout(t)


# --- 14. Just dance: two photos open from their edges, the words rise, an eye, a sparkle, a paragraph, a pill ----
def just_dance():
    E = 60
    D = dur_for(E)
    t = _p("baile", "Historia: Just dance con tres fotos", "Story: Just dance with three photos", 14213, D,
           ["baile", "fotos", "azul"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, BLUE)
    chrome(s)
    e1 = lambda fr: k(fr, 3, 12)  # noqa: E731
    photo(s, "dance-01", box=(520, 345, 890, 830), name="Foto", label="Foto 1",
          rect=lambda fr, u: (520, 345, 890, 345 + 485 * e1(fr)))
    photo(s, "dance-03", box=(37, 1244, 375, 1691), name="Foto 2", label="Foto 2",
          rect=lambda fr, u: (37, 1691 - 447 * e1(fr), 375, 1691))
    photo(s, "dance-02", box=(648, 1202, 1080, 1728), name="Foto 3", label="Foto 3",
          geom=lambda fr, u: (450 * (1 - k(fr, 51, 9)), 0, 1))
    for i, (word, x, y) in enumerate((("PROFILE", 70, 256), ("FOLLOWING", 480, 271), ("FOR YOU", 900, 288))):
        appear(s, tx(s, word, x, y, 15, I, 700, "#0E3A52", f"Menú {i + 1}"), 48 + 3 * i, 0.04, 0.05,
               preset="typewriter")
    c = s.say("Just dance", (20, 862, 930, 964), A, 800, INK, "Título", align="left",
              reveal=lambda fr: (0, 800, W, 995))
    appear(s, c, 12, 0.3, 0.25, preset="rise", unit="word")
    ellipse_line(s, "Óvalo", 675, 925, 560, 150, -4, INK, 2, 51, 9, alpha=0.7)
    star(s, "Chispa", 68, 790, 110, 36)
    blink = lambda fr: 1 - 0.85 * math.sin(math.pi * lin(fr, 54, 6))  # noqa: E731
    eye(s, "Ojo", 270, 563, 150, 33, rot=0, blink=blink, outline=5)
    for i, line in enumerate(("Dance is such a fundamental aspect of", "the app that many of its dances have become",
                              "a ubiquitous part of youth culture today")):
        appear(s, tx(s, line, 22, 997 + 36 * i, 20, I, 700, INK, f"Párrafo {i + 1}"), 42 + 3 * i, 0.008, 0.05)
    s.rect("Etiqueta", solid(INK), lambda fr, u: (20, 1140, 20 + 240 * k(fr, 48, 6), 1196), radius=28)
    appear(s, tx(s, "#streetdance", 140, 1157, 20, I, 800, WHITE, "Etiqueta (texto)", align="center"), 51, 0.03,
           0.05, preset="typewriter")
    return layout(t)


# --- 15. Get new Subscribers: round photos pop with thin rings and «+» buttons, the red words type --------------
def subscribers():
    E = 48
    D = dur_for(E)
    t = _p("suscriptores", "Historia: nuevos suscriptores", "Story: get new subscribers", 14214, D,
           ["suscriptores", "fotos", "negro", "rojo"], thumb=round(E / FPS + 0.6, 1))
    s = T(t, D)
    bg(s, ASH)
    chrome(s, header=False)
    ellipse_line(s, "Anillo 1", 356, 340, 490, 490, 0, BLUE, 2, 6, 15)
    ellipse_line(s, "Anillo 2", 770, 973, 460, 460, 0, WHITE, 2, 9, 15, alpha=0.8)
    for i, (sample, cx, cy, d, at) in enumerate((("portrait-03", 356, 340, 340, 0), ("fx-man-05", 770, 973, 320, 4),
                                                 ("portrait-08", 444, 698, 280, 9), ("couple-03", 790, 515, 380, 21))):
        round_photo(s, sample, cx, cy, d, f"Foto {i + 1}", f"Foto {i + 1}",
                    lambda fr, u, at=at: (0, 0, max(0.001, pop(fr, at, 12))))
    heart(s, "Corazón", 156, 225, 40, RED, 12)
    s.obj("Punto blanco", solid(WHITE), lambda fr, u: (994, 1017, 22 * pop(fr, 15), 22 * pop(fr, 15), 0, 1),
          kind="ellipse", base=(22, 22))
    s.obj("Nota (fondo)", solid("#2A2A2A"), lambda fr, u: (780, 265, 160 * pop(fr, 27), 160 * pop(fr, 27), 0, 1),
          kind="ellipse", base=(160, 160))
    note(s, "Nota", 780, 265, 72, at=29)
    for name, colour, x, y, d, at in (("Más azul", BLUE, 786, 682, 90, 33), ("Más rojo", RED, 464, 827, 70, 39)):
        s.obj(name, solid(colour), lambda fr, u, x=x, y=y, d=d, at=at: (x, y, d * pop(fr, at), d * pop(fr, at), 0, 1),
              kind="ellipse", base=(d, d))
        for j, (w, h) in enumerate(((d * 0.36, 4), (4, d * 0.36))):
            s.obj(f"{name} ({j + 1})", solid(WHITE), lambda fr, u, x=x, y=y, w=w, h=h, at=at: (
                x, y, w * pop(fr, at + 2), h * pop(fr, at + 2), 0, 1), base=(w, h))
    appear(s, tx(s, "#follow", 210, 842, 22, I, 700, BLUE, "Etiqueta", align="center",
                 geom=lambda fr, u: (0, 0, 1, -15, 1)), 39, 0.04, 0.05, preset="typewriter")
    appear(s, tx(s, "#like", 406, 998, 20, I, 800, WHITE, "Etiqueta 2", align="center",
                 geom=lambda fr, u: (0, 0, 1, 8, 1)), 42, 0.04, 0.05, preset="typewriter")
    c = s.say("Get new", (124, 1132, 540, 1198), A, 800, RED, "Título", align="left")
    appear(s, c, 24, 0.2, 0.06, unit="word")
    appear(s, s.say("Subscribers", (124, 1215, 736, 1273), A, 800, RED, "Título 2", align="left"), 36, 0.03, 0.05,
           preset="typewriter")
    return layout(t)


TEMPLATES = [austin, follow, logo_card, isabella, trends, alice, blogger, new, new_video, lifestyle, profile, different,
             beauty, just_dance, subscribers]
