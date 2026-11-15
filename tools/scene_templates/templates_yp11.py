"""Video 45549099.mp4 as Kit de YouTube Stock templates (yp11-*). See docs/plan-youtube-pack-2.md.

«YouTube titles & buttons» (1920×1080 at 30 fps): twenty small animated words and buttons shown in a 5×4 grid and
then, two to four at a time, big over footage. Each piece copies one of them (layout measured on the grid at 3 s,
moves studied frame by frame on the big uses; study notes in tienda/plantillas/estudio-45549099/NOTAS.md): the
shapes pop in with an overshoot, the letters pop in one by one, a small loop plays while it holds (a beating heart,
a blinking smiley, a ringing bell…), and on the way out every letter swells and shrinks away in reading order and
the shapes swell and vanish last. Transparent, to sit over the user's video. The year reads 2026.

Coordinates are written as measured on the grid frame and laid out bigger with Map (grid → screen).
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import wide
from scene import keys, tanim
from templates_tit_c import FPS
from templates_tit_e import solid
from templates_tit_h import TRIANGLE, lin, poly, ring
from templates_yp3 import B

P = "Poppins"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium"),
               (400, "Regular")):
    f6._FILES[(P, _w)] = f"fonts.basic/fonts/poppins/Poppins-{_f}.ttf"

WHITE, INK = "#FFFFFF", "#1C1C1C"
DARK = "#212121"
RED, BLUE, YELLOW = "#DE4456", "#84B5D5", "#EDE982"
GREY = "#707074"

# --- glyphs (paths in a 100 × 100 box, stretched to the shape's box) ------------------------------------------------
HEART = ("M 50 98 C 30 80 0 60 0 30 C 0 12 12 0 28 0 C 40 0 47 8 50 16 C 53 8 60 0 72 0 C 88 0 100 12 100 30 "
         "C 100 60 70 80 50 98 Z")
HAND = ("M 22 9 Q 22 0 32 0 Q 42 0 42 9 L 42 34 Q 42 27 51 27 Q 60 27 60 35 Q 60 30 69 30 Q 78 30 78 38 "
        "Q 78 34 87 34 Q 96 34 96 43 L 96 66 Q 96 77 85 77 L 16 77 Q 4 77 4 65 L 4 52 Q 4 44 13 44 L 22 44 Z "
        "M 12 81 L 90 81 L 90 100 L 12 100 Z")
POINTER = poly([(0, 0), (0, 80), (21, 62), (36, 100), (52, 93), (37, 57), (66, 57)])
DIAG = poly([(0, 100), (9, 46), (27, 61), (86, 2), (98, 14), (39, 73), (54, 91)])  # an arrow pointing down-left
THUMB = ("M 8 10 Q 8 0 20 0 Q 32 0 32 10 L 32 32 L 80 32 Q 92 32 92 41 Q 92 48 86 49 L 88 49 Q 99 49 99 58 "
         "Q 99 66 88 66 L 87 66 Q 97 66 97 75 Q 97 83 86 83 L 84 83 Q 93 83 93 91 Q 93 100 82 100 L 18 100 "
         "Q 8 100 8 90 Z")
THUMB_LINES = "M 58 49 L 88 49 M 58 66 L 87 66 M 58 83 L 85 83"
BELL = ("M 50 8 C 31 8 22 22 22 40 L 22 76 L 78 76 L 78 40 C 78 22 69 8 50 8 Z "
        "M 6 76 L 94 76 L 94 88 L 6 88 Z M 43 5 Q 43 0 50 0 Q 57 0 57 5 Q 57 10 50 10 Q 43 10 43 5 Z "
        "M 40 88 L 60 88 Q 60 100 50 100 Q 40 100 40 88 Z")
BOLT = poly([(64, 0), (8, 60), (44, 60), (26, 100), (92, 36), (54, 36), (78, 0)])
EYE = "M 0 50 Q 50 -38 100 50 Q 50 138 0 50 Z"
LBAR = "M 14 0 Q 28 0 28 14 L 28 76 L 100 76 L 100 100 L 12 100 Q 0 100 0 88 L 0 14 Q 0 0 14 0 Z"
DOWN = poly([(36, 0), (64, 0), (64, 52), (96, 52), (50, 100), (4, 52), (36, 52)])
SMILE = "M 22 54 Q 50 92 78 54"


def flower(n=8, depth=0.09, steps=96):
    return poly([(50 + 50 * (1 - depth + depth * math.cos(n * 2 * math.pi * i / steps)) * math.cos(2 * math.pi * i / steps),
                  50 + 50 * (1 - depth + depth * math.cos(n * 2 * math.pi * i / steps)) * math.sin(2 * math.pi * i / steps))
                 for i in range(steps)])


FLOWER = flower()


def half_ring(r0, r1, a0=180.0, a1=360.0, steps=40):
    """A band of a circle (radii r0 < r1 as fractions of 50) from angle a0 to a1 (degrees, y down)."""
    outer = [(50 + 50 * r1 * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
              50 + 50 * r1 * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]
    inner = [(50 + 50 * r0 * math.cos(math.radians(a1 - (a1 - a0) * i / steps)),
              50 + 50 * r0 * math.sin(math.radians(a1 - (a1 - a0) * i / steps))) for i in range(steps + 1)]
    return poly(outer + inner)


def fill(colour):
    return {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
            "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}


def stroke(width, colour=INK):
    return {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "outside",
            "opacity": 1.0, "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}


def lined(colour, width):
    return [fill(colour), stroke(width)]


# --- motion --------------------------------------------------------------------------------------------------------
def grow(fr, at, n=10, s=2.6):
    """0 → 1 with an overshoot (easeOutBack), from frame at over n frames."""
    q = lin(fr, at, n)
    if q <= 0:
        return 0.0
    return 1 + (s + 1) * (q - 1) ** 3 + s * (q - 1) ** 2


def leave(fr, at, n=14, s=2.0):
    """1 → 0: swells a little first, then shrinks away (easeInBack), from frame at over n frames."""
    q = lin(fr, at, n)
    if q <= 0:
        return 1.0
    if q >= 1:
        return 0.0
    return 1 - ((s + 1) * q ** 3 - s * q ** 2)


def smooth(fr, at, n):
    q = lin(fr, at, n)
    return q * q * (3 - 2 * q)


def on(fr, at):
    return 1.0 if fr >= at else 0.0


class Map:
    """Grid frame (measured) → screen: the element's grid box centre goes to (tx, ty), F times bigger."""

    def __init__(self, box, tx, ty, F):
        self.gx, self.gy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        self.tx, self.ty, self.F = tx, ty, F

    def x(self, v):
        return self.tx + (v - self.gx) * self.F

    def y(self, v):
        return self.ty + (v - self.gy) * self.F

    def ink(self, r):
        return (self.x(r[0]), self.y(r[1]), self.x(r[2]), self.y(r[3]))


class Y(B):
    def thing(self, m, name, layers, box, scale, rot=None, op=None, path=None, kind="rectangle", radius=0.0,
              anchor=None, dx=None):
        """A shape on the grid box (x0, y0, x1, y1), scaled by scale(fr) about anchor (grid; its centre by default),
        turned by rot(fr), moved by dx(fr) = (dx, dy) grid px."""
        x0, y0, x1, y1 = box
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        ax, ay = anchor or (cx, cy)
        w, h = (x1 - x0) * m.F, (y1 - y0) * m.F

        def g(fr, u):
            sc = max(0.0, scale(fr))
            ox, oy = dx(fr) if dx else (0.0, 0.0)
            px, py = ax + (cx - ax) * sc + ox, ay + (cy - ay) * sc + oy
            o = op(fr) if op else 1.0
            return m.x(px), m.y(py), w * sc, h * sc, rot(fr) if rot else 0.0, o if sc > 0.003 else 0.0
        return self.obj(name, layers, g, path=path, kind=kind, radius=radius * m.F, base=(w, h))

    def word(self, m, text, ink, weight, colour, at, stg, out_at, out_stg=None, name="Título", layers=None,
             runs=None, dur=0.33, odur=0.4, align="left", lead=0.0):
        """A line whose letters pop in one by one from frame at (stg frames apart) and swell and shrink away in
        reading order from frame out_at."""
        c = self.say(text, m.ink(ink), P, weight, colour, name, align=align, layers=layers)
        if runs:
            c["textStyle"]["runs"] = [{"start": a, "end": b, "colorEnabled": True,
                                       "color": "#ff" + col.lstrip("#").lower()} for a, b, col in runs]
        n = len(text)
        ostg = (out_stg if out_stg is not None else stg) / FPS
        # measured on the renders: the engine ends the way out ~0.2 s before its delay says
        out_end = out_at / FPS + (n - 1) * ostg + odur + 0.2
        c["textStyle"]["animation"] = {
            "in": tanim("pop", duration=dur, unit="character", stagger=stg / FPS, ease="back",
                        delay=round(at / FPS, 3), order="forward", **{"from": 0}),
            "out": tanim("pop", duration=odur, unit="character", stagger=ostg, ease="easeIn",
                         delay=round(max(0.0, self.dur - out_end), 3), order="forward", **{"from": 0})}
        return c


def _p(id, es, en, order, dur, section, tags=(), thumb=None):
    t = wide(f"yp11-{id}", es, en, "ytkit", round(dur + 0.15, 2), order=order, tags=[f"kit:{section}", "youtube"] + list(tags),
             thumb_at=round(thumb if thumb is not None else dur * 0.55, 1))
    # The pieces are transparent; the project's colour only shows on the Stock card and preview (the app inserts
    # the tracks, not the background): the reference's grey, so the dark words read there.
    t.background = GREY
    return t


def ow(m, px=1.6):
    """An outline width that scales with the piece."""
    return round(px * m.F, 1)


# --- 1. HIGH QUALITY: a blue pill with a white rim pops, the words pop in, a pointer slides up to it --------------
def high_quality():
    D = 6.0
    t = _p("high-quality", "Botón: alta calidad con puntero", "Button: high quality with pointer", 17600, D,
           "elementos", ["calidad", "botón", "puntero"])
    s = Y(t, t.duration)
    m = Map((111, 98, 407, 205), 1380, 820, 2.3)
    sc = lambda fr: grow(fr, 3, 9) * (1 + 0.12 * smooth(fr, 150, 6)) * leave(fr, 166, 12, 0.5)  # noqa: E731
    s.thing(m, "Píldora (borde)", lined(WHITE, ow(m, 1.4)), (111, 98, 407, 189), sc, radius=45, kind="rounded-rectangle")
    s.thing(m, "Píldora", lined(BLUE, ow(m, 1.0)), (121, 108, 397, 179), sc, radius=36, kind="rounded-rectangle",
            anchor=(259, 143.5))
    c = s.word(m, "HIGH QUALITY", (133, 128, 384, 156), 800, INK, 21, 1.4, 999, name="Texto")
    c["textStyle"]["animation"]["out"] = tanim("pop", duration=0.01, unit="block", ease="linear")
    s.tmove(c, lambda fr, u: (m.x(259) - m.x(258.5), 0,
                              max(1e-3, (1 + 0.12 * smooth(fr, 150, 6)) * leave(fr, 166, 12, 0.5)), 0, 1.0))

    def ptr(fr):
        q = smooth(fr, 18, 9)
        drift = 3 * math.sin((fr - 27) / 30 * math.pi) if fr > 27 else 0.0
        return 60 * (1 - q) + drift, 50 * (1 - q) + drift * 0.6
    s.thing(m, "Puntero", lined(WHITE, ow(m, 1.0)), (343, 162, 371, 204),
            lambda fr: on(fr, 18) * leave(fr, 166, 12, 0.5), path=POINTER, dx=ptr, anchor=(259, 143.5))
    return t


# --- 2. Like with a heart: the heart pops and beats, «Like» pops letter by letter ----------------------------------
def like_heart():
    D = 5.95
    t = _p("like-heart", "Texto: Like con corazón", "Text: Like with a heart", 17601, D, "redes",
           ["me gusta", "corazón"])
    s = Y(t, t.duration)
    m = Map((491, 105, 729, 179), 430, 860, 2.6)
    s.word(m, "Like", (491, 114, 657, 178), 700, DARK, 12, 4, 147, 4, runs=[(3, 4, WHITE)],
           layers=[fill(DARK), stroke(ow(m, 0.7))])

    def beat(fr):
        return 1 + 0.06 * math.sin(max(0.0, fr - 40) / 30 * 2 * math.pi)
    s.thing(m, "Corazón", lined(RED, ow(m, 1.3)), (657, 105, 729, 167),
            lambda fr: grow(fr, 2, 10) * beat(fr) * leave(fr, 160, 16), rot=lambda fr: 12.0, path=HEART)
    return t


# --- 3. FOLLOW ME with a switch: a pill pops, the words pop, the pill clicks on (two echoes, a dot) -----------------
def follow_me():
    D = 5.9
    t = _p("follow-me", "Botón: síguenos con interruptor", "Button: follow me with a switch", 17602, D, "redes",
           ["seguir", "interruptor"])
    s = Y(t, t.duration)
    m = Map((885, 95, 1088, 176), 1440, 860, 2.6)
    sc = lambda fr: grow(fr, 2, 9) * leave(fr, 162, 12, 0.8)  # noqa: E731
    anchor = (1088, 157)
    for i, (x0, at) in enumerate(((963, 61), (972, 63))):
        s.thing(m, f"Interruptor (eco {i + 1})", lined(WHITE, ow(m, 1.0)), (980, 140, 1088, 174), sc,
                kind="rounded-rectangle", radius=17, anchor=anchor,
                dx=lambda fr, x0=x0, at=at: ((x0 - 980) * smooth(fr, at, 8), 0.0))
    s.thing(m, "Interruptor", lined(WHITE, ow(m, 1.0)), (980, 140, 1088, 174), sc, kind="rounded-rectangle",
            radius=17, anchor=anchor)
    s.thing(m, "Interruptor (punto)", solid(INK), (1064, 150, 1078, 164),
            lambda fr: grow(fr, 63, 6) * leave(fr, 162, 12, 0.8), kind="ellipse", anchor=anchor)
    s.word(m, "FOLLOW", (887, 95, 1086, 128), 800, DARK, 14, 3.4, 128, 5)
    s.word(m, "ME", (885, 141, 954, 173), 800, DARK, 32, 4, 154, 5, name="Texto")
    return t


# --- 4. Play: a red play button pops, «Play» pops under it -----------------------------------------------------------
def play_button():
    D = 5.95
    t = _p("play", "Botón: play rojo", "Button: red play", 17603, D, "elementos", ["play", "botón"])
    s = Y(t, t.duration)
    m = Map((1278, 67, 1414, 228), 1440, 640, 2.4)
    sc = lambda fr: grow(fr, 3, 9) * (1 + 0.14 * smooth(fr, 150, 9)) * leave(fr, 164, 13, 0.6)  # noqa: E731
    s.thing(m, "Botón", lined(RED, ow(m, 1.2)), (1278, 67, 1414, 165), sc, kind="rounded-rectangle", radius=20)
    s.thing(m, "Botón (play)", solid(WHITE), (1330, 97, 1372, 137),
            lambda fr: grow(fr, 5, 8) * (1 + 0.14 * smooth(fr, 150, 9)) * leave(fr, 164, 13, 0.6),
            path=TRIANGLE, anchor=(1346, 116))
    s.word(m, "Play", (1283, 176, 1410, 218), 700, WHITE, 24, 3.5, 159, 4, layers=[fill(WHITE), stroke(ow(m, 0.6))])
    return t


# --- 5. TITLES & BUTTONS with a smiley that changes colour -----------------------------------------------------------
def titles_smiley():
    D = 6.0
    t = _p("titles-smiley", "Título: TITLES & BUTTONS con carita", "Title: TITLES & BUTTONS with a smiley", 17604, D,
           "tipografia", ["carita", "título"])
    s = Y(t, t.duration)
    m = Map((1598, 66, 1817, 185), 800, 540, 3.4)
    # three discs behind each other; their colours turn (white face, yellow face, black) every ~18 frames
    states = [(0, (WHITE, YELLOW, DARK)), (56, (YELLOW, WHITE, DARK)), (72, (DARK, WHITE, YELLOW)),
              (92, (WHITE, YELLOW, DARK)), (108, (YELLOW, WHITE, DARK)), (128, (DARK, WHITE, YELLOW)),
              (148, (WHITE, YELLOW, DARK))]

    def colour_at(fr, i):
        c = states[0][1][i]
        for at, cols in states:
            if fr >= at:
                c = cols[i]
        return c
    out = lambda fr: leave(fr, 154, 10)  # noqa: E731
    anchor = (1759, 131)
    for i, (gx, at) in reversed(list(enumerate(((1759, 30), (1784, 40), (1806, 46))))):
        for col in (WHITE, YELLOW, DARK):
            def op(fr, col=col, i=i):
                return 1.0 if colour_at(fr, i) == col else 0.0
            dx = (lambda fr: (120 * (1 - smooth(fr, 30, 8)), 0.0)) if i == 0 else \
                (lambda fr, gx=gx, at=at: ((1759 - gx) * (1 - smooth(fr, at, 6)), 0.0))
            sc = (lambda fr: grow(fr, 30, 8) * out(fr)) if i == 0 else (lambda fr, at=at: on(fr, at) * out(fr))
            s.thing(m, f"Carita {i + 1} ({ {WHITE: 'blanca', YELLOW: 'amarilla', DARK: 'negra'}[col] })",
                    lined(col, ow(m, 0.8)), (gx - 25, 106, gx + 25, 156), sc, op=op, kind="ellipse",
                    anchor=anchor if i == 0 else (gx, 131), dx=dx)
    face_op = lambda fr: 1.0 if colour_at(fr, 0) != DARK else 0.0  # noqa: E731
    sc0 = lambda fr: grow(fr, 30, 8) * out(fr)  # noqa: E731
    dx0 = lambda fr: (120 * (1 - smooth(fr, 30, 8)), 0.0)  # noqa: E731
    for i, ex in enumerate((1751, 1767)):
        s.thing(m, f"Carita (ojo {i + 1})", ring(INK, ow(m, 0.6)), (ex - 2.6, 120, ex + 2.6, 125.2), sc0, op=face_op,
                kind="ellipse", anchor=anchor, dx=dx0)
    s.thing(m, "Carita (boca)", ring(INK, ow(m, 0.6)), (1743, 122, 1775, 147), sc0, op=face_op, path=SMILE,
            anchor=anchor, dx=dx0)
    lay = [fill(WHITE), stroke(ow(m, 0.5))]
    s.word(m, "YOUTUBE", (1599, 66, 1788, 93), 800, WHITE, 8, 1.8, 154, 2.2, layers=lay, name="Título")
    s.word(m, "TITLES", (1598, 112, 1739, 142), 800, WHITE, 14, 1.8, 158, 2.2, layers=lay, name="Título 2")
    s.word(m, "BUTTONS", (1600, 153, 1790, 185), 800, WHITE, 20, 1.8, 162, 2.2, layers=lay, name="Título 3")
    return t


# --- 6. WATCH NOW: three yellow flowers pop and hop, the words pop --------------------------------------------------
def watch_now():
    D = 6.4
    t = _p("watch-now", "Texto: míralo ahora con flores", "Text: watch now with flowers", 17605, D, "elementos",
           ["ver", "nuevo video"])
    s = Y(t, t.duration)
    m = Map((124, 379, 392, 453), 520, 880, 2.4)
    for i, cx in enumerate((145, 185, 225)):
        at = 3 + 3 * i

        def hop(fr, i=i):
            return (0.0, -8 * math.sin(math.pi * lin(fr, 27 + 3 * i, 6)))
        sc = lambda fr, at=at, i=i: grow(fr, at, 8) * leave(fr, 162 + 3 * i, 12)  # noqa: E731
        s.thing(m, f"Flor {i + 1}", lined(YELLOW, ow(m, 0.8)), (cx - 16, 421, cx + 16, 453), sc, path=FLOWER,
                dx=hop, rot=lambda fr, i=i: 30 * smooth(fr, 27 + 3 * i, 8))
        s.thing(m, f"Flor {i + 1} (centro)", lined(WHITE, ow(m, 0.7)), (cx - 8.5, 428.5, cx + 8.5, 445.5), sc, kind="ellipse",
                dx=hop, anchor=(cx, 437))
    s.word(m, "WATCH NOW", (124, 379, 391, 407), 800, WHITE, 42, 1.5, 166, 2)
    s.word(m, "NEW Video", (258, 429, 392, 447), 700, WHITE, 48, 1.5, 170, 2, name="Texto")
    return t


# --- 7. 2026 Brand New -----------------------------------------------------------------------------------------------
def brand_new_year():
    D = 6.4
    t = _p("brand-new-year", "Título: año 2026 Brand New", "Title: year 2026 Brand New", 17606, D, "tipografia",
           ["año", "nuevo"])
    s = Y(t, t.duration)
    m = Map((504, 362, 702, 492), 480, 760, 2.4)
    s.word(m, "2026", (504, 362, 702, 422), 700, DARK, 9, 4, 165, 3.5, runs=[(1, 2, WHITE)],
           layers=[fill(DARK), stroke(ow(m, 0.8))])
    lay = [fill(WHITE), stroke(ow(m, 0.5))]
    # Brand New comes in under the «2» and drifts right under «026» (frames 36–66)
    slide = lambda fr, u: (-80 * m.F * (1 - smooth(fr, 36, 30)), 0, 1, 0, 1)  # noqa: E731
    s.tmove(s.word(m, "Brand", (602, 442, 694, 463), 700, WHITE, 18, 2, 153, 2.5, layers=lay, name="Texto"), slide)
    s.tmove(s.word(m, "New", (602, 472, 668, 492), 700, WHITE, 27, 2, 163, 2.5, layers=lay, name="Texto 2"), slide)
    return t


# --- 8. Looking Perfect with three turning dots ---------------------------------------------------------------------
def looking_perfect():
    D = 5.4
    t = _p("looking-perfect", "Texto: Looking Perfect con puntos", "Text: Looking Perfect with dots", 17607, D,
           "tipografia", ["puntos"])
    s = Y(t, t.duration)
    m = Map((848, 290, 1105, 473), 520, 690, 2.3)
    cx, cy, r = 900, 332, 25
    for i, (col, a0) in enumerate(((YELLOW, -90), (YELLOW, 150), (WHITE, 30))):
        def dx(fr, a0=a0):
            spin = 360 * max(0.0, fr - 30) / 70 + 540 * smooth(fr, 132, 24)
            a = math.radians(a0 + spin)
            sq = 0.55 + 0.45 * abs(math.cos(math.radians(spin * 0.5)))
            return (r * math.cos(a) - r * math.cos(math.radians(a0)), r * math.sin(a) * sq - r * math.sin(math.radians(a0)))
        px, py = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
        s.thing(m, f"Punto {i + 1}", lined(col, ow(m, 0.8)), (px - 17, py - 17, px + 17, py + 17),
                lambda fr, i=i: grow(fr, 3 + i, 7) * leave(fr, 140, 14), kind="ellipse", dx=dx)
    s.thing(m, "Punto final", lined(YELLOW, ow(m, 0.8)), (1074, 442, 1105, 473),
            lambda fr: grow(fr, 18, 7) * leave(fr, 150, 12), kind="ellipse")
    lay = [fill(WHITE), stroke(ow(m, 0.6))]
    s.word(m, "Looking", (854, 374, 1067, 411), 700, WHITE, 9, 2.2, 141, 2.4, layers=lay)
    s.word(m, "Perfect", (860, 435, 1062, 472), 700, WHITE, 21, 2.2, 147, 2.4, layers=lay, name="Título 2")
    return t


# --- 9. CLICK: a hand slides in, clicks on the word and slides away -------------------------------------------------
def click_hand():
    D = 5.6
    t = _p("click", "Botón: CLICK con mano", "Button: CLICK with a hand", 17608, D, "elementos", ["clic", "mano"])
    s = Y(t, t.duration)
    m = Map((1194, 373, 1457, 441), 960, 220, 2.4)
    s.word(m, "CLICK", (1194, 398, 1378, 441), 800, YELLOW, 9, 3, 141, 4, layers=[fill(YELLOW), stroke(ow(m, 0.6))])

    def at(fr):
        # comes in from the right (22–34), rests over «IC», clicks at 54, goes back beside the word (78–90)
        q_in, q_back = smooth(fr, 22, 12), smooth(fr, 78, 12)
        return 260 * (1 - q_in) - 125 * q_in * (1 - q_back), 26 * q_in * (1 - q_back)
    s.thing(m, "Mano", lined(WHITE, ow(m, 1.0)), (1398, 361, 1468, 449),
            lambda fr: (1 - 0.14 * math.sin(math.pi * lin(fr, 52, 6))) * leave(fr, 150, 10), path=HAND, dx=at,
            op=lambda fr: on(fr, 22))
    return t


# --- 10. AMAZING with a rainbow --------------------------------------------------------------------------------------
def amazing_rainbow():
    D = 5.6
    t = _p("amazing", "Texto: AMAZING con arcoíris", "Text: AMAZING with a rainbow", 17609, D, "tipografia",
           ["arcoíris", "increíble"])
    s = Y(t, t.duration)
    m = Map((1536, 334, 1816, 438), 470, 860, 2.3)
    arch = (1698, 334, 1812, 448)  # the arch's circle (its lower half hides under the word)
    sc = lambda fr: grow(fr, 3, 7) * (1 + 0.15 * smooth(fr, 132, 9)) * leave(fr, 145, 10, 0.6)  # noqa: E731
    anchor = (1755, 391)
    s.thing(m, "Arcoíris (amarillo)", lined(YELLOW, ow(m, 1.0)), arch, sc, path=half_ring(0.5, 1.0), anchor=anchor)
    n = 12
    for i in range(n):
        a0, a1 = 180 + 180 * i / n - 0.6, 180 + 180 * (i + 1) / n + 0.6
        s.thing(m, f"Arcoíris (rojo {i + 1})", solid(RED), arch,
                lambda fr, i=i: on(fr, 45 + i) * sc(fr), path=half_ring(0.5, 0.82, a0, a1, 4), anchor=anchor)
    s.thing(m, "Arcoíris (borde rojo)", ring(INK, ow(m, 0.8)), arch, lambda fr: on(fr, 57) * sc(fr),
            path=half_ring(0.5, 0.82), anchor=anchor)
    s.word(m, "AMAZING", (1536, 397, 1816, 438), 800, WHITE, 15, 2.6, 135, 3)
    return t


# --- 11. Use Any Language on a black disc -----------------------------------------------------------------------------
def any_language():
    D = 6.4
    t = _p("any-language", "Texto: Use Any Language en círculo", "Text: Use Any Language on a disc", 17610, D,
           "tipografia", ["círculo", "idioma"])
    s = Y(t, t.duration)
    m = Map((158, 614, 349, 743), 400, 260, 2.2)
    s.thing(m, "Círculo", solid(DARK), (190, 614, 318, 742), lambda fr: grow(fr, 3, 13, 1.6) * leave(fr, 176, 14),
            kind="ellipse")
    lay = [fill(WHITE), stroke(ow(m, 0.7))]
    s.word(m, "Use", (220, 616, 286, 640), 700, WHITE, 24, 3, 147, 3, layers=lay)
    s.word(m, "Any", (217, 661, 289, 686), 700, WHITE, 30, 3, 153, 3, layers=lay, name="Título 2")
    s.word(m, "Language", (158, 707, 349, 732), 700, WHITE, 36, 2.5, 160, 2.5, layers=lay, name="Título 3")
    return t


# --- 12. Like my video with a blue thumb ----------------------------------------------------------------------------
def like_my_video():
    D = 5.7
    t = _p("like-my-video", "Texto: Like my video con pulgar", "Text: Like my video with a thumb", 17611, D, "redes",
           ["me gusta", "pulgar"])
    s = Y(t, t.duration)
    m = Map((423, 640, 759, 718), 1420, 920, 2.0)
    wag = lambda fr: 10 * math.sin(math.pi * lin(fr, 60, 16)) * math.sin(4 * math.pi * lin(fr, 60, 16))  # noqa: E731
    sc = lambda fr: grow(fr, 3, 7) * leave(fr, 160, 10)  # noqa: E731
    s.thing(m, "Pulgar", lined(BLUE, ow(m, 1.2)), (703, 640, 759, 710), sc, rot=wag, path=THUMB, anchor=(731, 710))
    s.thing(m, "Pulgar (dedos)", ring(INK, ow(m, 1.0)), (703, 640, 759, 710), sc, rot=wag, path=THUMB_LINES,
            anchor=(731, 710))
    s.word(m, "Like my video", (423, 680, 694, 709), 700, WHITE, 9, 1.6, 144, 1.8)
    return t


# --- 13. CHANNEL NAME: a red pill with a white rim and a pointing arrow ----------------------------------------------
def channel_name():
    D = 5.4
    t = _p("channel-name", "Botón: nombre del canal", "Button: channel name", 17612, D, "elementos",
           ["canal", "botón", "flecha"])
    s = Y(t, t.duration)
    m = Map((826, 621, 1126, 726), 470, 900, 2.0)
    sc = lambda fr: grow(fr, 3, 7) * (1 + 0.15 * smooth(fr, 140, 8)) * leave(fr, 150, 9, 0.5)  # noqa: E731
    anchor = (976, 685)
    s.thing(m, "Píldora (borde)", lined(WHITE, ow(m, 1.2)), (826, 645, 1126, 726), sc, kind="rounded-rectangle",
            radius=40, anchor=anchor)
    s.thing(m, "Píldora", solid(RED), (836, 656, 1116, 714), sc, kind="rounded-rectangle", radius=29, anchor=anchor)
    c = s.word(m, "CHANNEL NAME", (840, 676, 1105, 697), 700, WHITE, 12, 1.5, 999, name="Texto")
    c["textStyle"]["animation"]["out"] = tanim("pop", duration=0.01, unit="block", ease="linear")
    s.tmove(c, lambda fr, u: (m.x(976) - m.x(972.5), 0, max(1e-3, (1 + 0.15 * smooth(fr, 140, 8)) *
                                                          leave(fr, 150, 9, 0.5)), 0, 1.0))

    def where(fr):
        # comes in at the left pointing down-right, crosses to the right half pointing down-left
        q = smooth(fr, 42, 15)
        bob = 4 * math.sin(max(0.0, fr - 57) / 24 * math.pi)
        return (-110 * (1 - q) + bob, -20 * (1 - smooth(fr, 12, 8)) + bob)
    s.thing(m, "Flecha", lined(WHITE, ow(m, 1.0)), (1003, 621, 1059, 656),
            lambda fr: grow(fr, 12, 6) * (1 + 0.15 * smooth(fr, 140, 8)) * leave(fr, 150, 9, 0.5), path=DIAG,
            rot=lambda fr: -90 * (1 - smooth(fr, 42, 15)), dx=where)
    return t


# --- 14. Rate ♥ Us ---------------------------------------------------------------------------------------------------
def rate_us():
    D = 5.7
    t = _p("rate-us", "Texto: Rate Us con corazón", "Text: Rate Us with a heart", 17613, D, "redes",
           ["calificar", "corazón"])
    s = Y(t, t.duration)
    m = Map((1246, 607, 1421, 743), 320, 240, 2.4)
    beat = lambda fr: 1 + 0.08 * max(0.0, math.sin(max(0.0, fr - 36) / 28 * 2 * math.pi))  # noqa: E731
    s.thing(m, "Corazón", solid(RED), (1246, 690, 1305, 739),
            lambda fr: grow(fr, 3, 7) * beat(fr) * leave(fr, 150, 15), path=HEART)
    s.word(m, "Rate", (1247, 607, 1421, 658), 700, WHITE, 9, 3, 141, 4)
    s.word(m, "Us", (1336, 691, 1421, 743), 700, WHITE, 12, 6, 147, 6, name="Título 2")
    return t


# --- 15. Subscribe with a ringing bell --------------------------------------------------------------------------------
def subscribe_bell():
    D = 5.7
    t = _p("subscribe-bell", "Texto: Subscribe con campana", "Text: Subscribe with a bell", 17614, D, "redes",
           ["suscribirse", "campana"])
    s = Y(t, t.duration)
    m = Map((1570, 621, 1811, 725), 1460, 860, 2.4)
    ring_ = lambda fr: 14 * math.sin(math.pi * lin(fr, 60, 18)) * math.sin(5 * math.pi * lin(fr, 60, 18))  # noqa: E731
    s.thing(m, "Campana", lined(YELLOW, ow(m, 0.8)), (1570, 621, 1621, 682),
            lambda fr: grow(fr, 3, 7) * (1 + 0.2 * smooth(fr, 144, 8)) * leave(fr, 152, 8, 0.3), path=BELL,
            rot=ring_, anchor=(1595.5, 621))
    s.word(m, "Subscribe", (1570, 690, 1811, 725), 700, RED, 18, 2.4, 150, 2.2,
           layers=[fill(RED), stroke(ow(m, 0.7))])
    return t


# --- 16. Trendy Style with two flickering bolts ---------------------------------------------------------------------
def trendy_style():
    D = 5.95
    t = _p("trendy-style", "Texto: Trendy Style con rayos", "Text: Trendy Style with bolts", 17615, D, "tipografia",
           ["rayo", "tendencia"])
    s = Y(t, t.duration)
    m = Map((120, 916, 402, 981), 1420, 880, 2.4)
    jit = lambda fr, a: ((a * 3 * ((int(fr) // 4) % 2 * 2 - 1)) if fr > 30 else 0.0, 0.0)  # noqa: E731
    out = lambda fr: leave(fr, 150, 9)  # noqa: E731
    s.thing(m, "Rayo amarillo", lined(YELLOW, ow(m, 0.6)), (144, 912, 174, 961),
            lambda fr: grow(fr, 3, 7) * out(fr), path=BOLT, dx=lambda fr: jit(fr, 1))
    s.thing(m, "Rayo blanco", lined(WHITE, ow(m, 0.6)), (118, 924, 152, 975),
            lambda fr: grow(fr, 5, 7) * out(fr), path=BOLT, dx=lambda fr: jit(fr, -1))
    s.word(m, "Trendy Style", (145, 930, 402, 970), 700, WHITE, 15, 2.2, 150, 2.4,
           layers=[fill(WHITE), stroke(ow(m, 0.4))])
    return t


# --- 17. New Video: a blue box with a blinking smiley ---------------------------------------------------------------
def new_video_box():
    D = 5.4
    t = _p("new-video", "Etiqueta: New Video con carita", "Label: New Video with a smiley", 17616, D, "elementos",
           ["nuevo video", "carita"])
    s = Y(t, t.duration)
    m = Map((511, 906, 696, 1004), 1500, 210, 2.0)
    sc = lambda fr: grow(fr, 6, 15, 3.4) * (1 + 0.15 * smooth(fr, 138, 9)) * leave(fr, 150, 10, 0.4)  # noqa: E731
    s.thing(m, "Caja", lined(BLUE, ow(m, 0.8)), (511, 906, 696, 1004), sc, kind="rounded-rectangle", radius=6)
    sm = lambda fr: grow(fr, 33, 6) * leave(fr, 140, 12)  # noqa: E731
    anchor = (541, 934)
    s.thing(m, "Carita", lined(WHITE, ow(m, 0.6)), (524, 917, 558, 951), sm, kind="ellipse")

    def blink(fr):
        return 0.0 if any(b <= fr < b + 8 for b in (72, 117)) else 1.0
    for i, ex in enumerate((535, 547)):
        s.thing(m, f"Carita (ojo {i + 1})", ring(INK, ow(m, 0.5)), (ex - 2.2, 927, ex + 2.2, 931.4), sm,
                op=lambda fr: blink(fr), kind="ellipse", anchor=anchor)
        s.thing(m, f"Carita (ojo cerrado {i + 1})", solid(INK), (ex - 2.8, 928.6, ex + 2.8, 929.8), sm,
                op=lambda fr: 1.0 - blink(fr), anchor=anchor)
    s.thing(m, "Carita (boca)", ring(INK, ow(m, 0.5)), (530, 929, 552, 946), sm, path=SMILE, anchor=anchor)
    s.word(m, "New", (562, 913, 679, 950), 800, WHITE, 9, 2, 138, 2.5, layers=[fill(WHITE), stroke(ow(m, 0.5))])
    s.word(m, "Video", (521, 955, 679, 993), 800, WHITE, 15, 2.5, 141, 2.5, layers=[fill(WHITE), stroke(ow(m, 0.5))],
           name="Título 2")
    return t


# --- 18. Comment with a bouncing down arrow -------------------------------------------------------------------------
def comment_arrow():
    D = 5.7
    t = _p("comment", "Texto: Comment con flecha", "Text: Comment with an arrow", 17617, D, "redes",
           ["comentar", "flecha"])
    s = Y(t, t.duration)
    m = Map((849, 935, 1115, 978), 520, 880, 2.6)
    bob = lambda fr: (0.0, 4 * math.sin(max(0.0, fr - 21) / 15 * math.pi))  # noqa: E731
    sc = lambda fr: grow(fr, 15, 7) * leave(fr, 160, 10)  # noqa: E731
    white_time = lambda fr: 84 <= fr < 111  # noqa: E731
    s.thing(m, "Flecha (azul)", lined(BLUE, ow(m, 0.6)), (1086, 936, 1115, 978), sc, path=DOWN, dx=bob,
            op=lambda fr: 0.0 if white_time(fr) else 1.0)
    s.thing(m, "Flecha (blanca)", lined(WHITE, ow(m, 0.6)), (1086, 936, 1115, 978), sc, path=DOWN, dx=bob,
            op=lambda fr: 1.0 if white_time(fr) else 0.0)
    s.word(m, "Comment", (849, 935, 1083, 970), 700, WHITE, 9, 2.4, 144, 2.6, runs=[(2, 4, BLUE)],
           layers=[fill(WHITE), stroke(ow(m, 0.5))])
    return t


# --- 19. Thanks for Watching with a blinking eye ---------------------------------------------------------------------
def thanks_eye():
    D = 6.4
    t = _p("thanks-watching", "Texto: gracias por ver con ojo", "Text: thanks for watching with an eye", 17618, D,
           "tipografia", ["gracias", "ojo", "agradecimiento"])
    s = Y(t, t.duration)
    m = Map((1250, 886, 1434, 1011), 960, 540, 3.0)
    sc = lambda fr: grow(fr, 3, 7) * leave(fr, 182, 12)  # noqa: E731

    def lid(fr):  # 1 open, 0 closed: one blink at 42–60
        if 42 <= fr < 60:
            return 0.06 + 0.94 * abs(math.cos(math.pi * (fr - 42) / 18))
        return 1.0

    def look(fr):  # the pupil glances left and right while it holds
        return (6 * math.sin(math.pi * lin(fr, 96, 22)) - 6 * math.sin(math.pi * lin(fr, 118, 22)), 0.0)
    s.obj("Ojo", lined(WHITE, ow(m, 0.8)), lambda fr, u: (m.x(1347), m.y(948.5), 62 * m.F * sc(fr),
                                                         27 * m.F * sc(fr) * lid(fr), 0, 1.0 if sc(fr) > 0.003 else 0),
          path=EYE, base=(62 * m.F, 27 * m.F))
    for name, col, d in (("Ojo (iris)", YELLOW, 19), ("Ojo (pupila)", INK, 8)):
        s.obj(name, solid(col), lambda fr, u, d=d: (m.x(1347 + look(fr)[0] * sc(fr)), m.y(948.5), d * m.F * sc(fr),
                                                   d * m.F * sc(fr) * min(1.0, lid(fr) * 1.4), 0,
                                                   1.0 if sc(fr) > 0.003 and lid(fr) > 0.3 else 0.0),
              kind="ellipse", base=(d * m.F, d * m.F))
    s.word(m, "Thanks", (1250, 886, 1385, 913), 700, DARK, 20, 2.8, 147, 2.4)
    s.word(m, "for", (1250, 931, 1303, 958), 700, DARK, 28, 3, 152, 2.4, name="Título 2")
    s.word(m, "Watching", (1250, 976, 1434, 1003), 700, DARK, 34, 2.8, 157, 2.4, name="Título 3")
    return t


# --- 20. SHARE with an L arrow that draws itself --------------------------------------------------------------------
def share_arrow():
    D = 5.6
    t = _p("share", "Texto: SHARE con flecha", "Text: SHARE with an arrow", 17619, D, "redes",
           ["compartir", "flecha"])
    s = Y(t, t.duration)
    m = Map((1547, 927, 1830, 1001), 1430, 900, 2.4)
    out = lambda fr: leave(fr, 152, 9)  # noqa: E731
    lbox = (1742, 927, 1795, 983)
    L = s.thing(m, "Flecha", lined(WHITE, ow(m, 1.0)), lbox, lambda fr: on(fr, 14) * out(fr), path=LBAR,
                anchor=(1795, 970))
    from templates_yp5 import screen_mask

    def reveal(fr):
        q1, q2 = smooth(fr, 14, 4), smooth(fr, 18, 4)
        pad = 8
        return (m.x(lbox[0] - pad), m.y(lbox[1] - pad), m.x(lbox[0] + 15 + (lbox[2] - lbox[0] - 15 + pad) * q2),
                m.y(lbox[1] - pad + (lbox[3] - lbox[1] + 2 * pad) * max(q1, 1e-3)))
    x0, y0 = m.x(lbox[0]), m.y(lbox[1])
    w, h = (lbox[2] - lbox[0]) * m.F, (lbox[3] - lbox[1]) * m.F
    screen_mask(s, L, (m.x((lbox[0] + lbox[2]) / 2) - w / 2, m.y((lbox[1] + lbox[3]) / 2) - h / 2, w, h),
                lambda fr: reveal(fr) if fr < 22 else (x0 - 40, y0 - 40, x0 + w + 40, y0 + h + 40))
    s.thing(m, "Flecha (punta)", lined(WHITE, ow(m, 1.0)), (1790, 952, 1830, 1001),
            lambda fr: grow(fr, 21, 6) * out(fr), path=TRIANGLE, anchor=(1795, 976),
            dx=lambda fr: (3 * math.sin(max(0.0, fr - 30) / 20 * math.pi) if fr > 30 else 0.0, 0.0))
    s.word(m, "SHARE", (1547, 947, 1726, 985), 800, BLUE, 9, 3, 144, 4, layers=[fill(BLUE), stroke(ow(m, 0.4))])
    return t


TEMPLATES = [high_quality, like_heart, follow_me, play_button, titles_smiley, watch_now, brand_new_year,
             looking_perfect, click_hand, amazing_rainbow, any_language, like_my_video, channel_name, rate_us,
             subscribe_bell, trendy_style, new_video_box, comment_arrow, thanks_eye, share_arrow]
