"""INSTAGRAM folder video 22025898.mp4 as Stock templates (ig2-*). See docs/plan-instagram.md.

A colourful pack of twelve vertical stories (960×540 at 25 fps, 40 s) shown three at a time side by side
(each story ≈ 214×382 px, laid out here ×5.05 on 1080×1920): a black-and-white face with colour bands and circles,
a cooking opener, «Fashion» on mint and red, «YOUR LIFE», «MODERN INTERIOR DESIGN» / «PERFECT STYLE», a purple
«Say what's on your mind», «INTRODUCING OUR STORIES», a city with a «%» badge, «DARK», «R / HAPPY», «GREAT TRIP
SUMMER» in a cloud of circles and a yellow «Stories» poster. Each story copies the layout, colours, type and moves of
the reference (studied on 10 fps sheets; times below in seconds from the story's start), photos are slots (B/W,
purple or yellow looks are effects on the slot, so any photo takes the look). The pack cover, the phone mockup and
the grid of all twelve are skipped; the author mark «RENN» and the word «Instagram» became neutral words.
Kit de Instagram; ids `ig2-*`, order 15200-. Study notes in tienda/plantillas/estudio-22025898/NOTAS.md.

Every story plays straight through and leaves pushed up (as the reference's columns scroll away).
"""

from __future__ import annotations

import math

import templates_llt_f as f6
import templates_tit_h  # noqa: F401  (registers the Montserrat files)
from kit import Box, tall
from llt_motion import frames_of
from scene import argb, effect, fill, gradient, keys, no_stroke, tanim, us
from templates_tit_h import S, ring
from templates_yp4 import art_except

W, H = 1080, 1920
WHITE = "#FFFFFF"
M = "Montserrat"
AS = "Alfa Slab One"
f6._FILES[(AS, 400)] = "fonts.extra/fonts/alfaslabone/AlfaSlabOne-Regular.ttf"
GRAY = effect("stylize.grayscale")
LOREM = ["Lorem ipsum dolor sit amet, consectetur", "adipiscing elit, sed do eiusmod tempor",
         "incididunt ut labore et dolore magna aliqua.", "Ut enim ad minim veniam, quis nostrud",
         "exercitation ullamco laboris nisi ut", "aliquip ex ea commodo consequat."]


def duo(dark, light, strength=1.0, contrast=0.5):
    return effect("duotone", shadowColor=dark, highlightColor=light, strength=strength, contrast=contrast)


def col(c, a=1.0):
    return [fill(c, a), no_stroke()]


def grad(stops, angle=90):
    return [gradient(stops, angle=angle), no_stroke()]


# --- easing ----------------------------------------------------------------------------------------------------

def cl(x):
    return max(0.0, min(1.0, x))


def eo(t, a, n):
    x = cl((t - a) / max(1e-6, n))
    return 1 - (1 - x) ** 3


def ei(t, a, n):
    x = cl((t - a) / max(1e-6, n))
    return x ** 3


def es(t, a, n):
    x = cl((t - a) / max(1e-6, n))
    return x * x * (3 - 2 * x)


def eb(t, a, n):
    """0 → 1 with a little overshoot."""
    x = cl((t - a) / max(1e-6, n))
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def tab(points, ease=es):
    """A value through (time, value) keys, eased between them; held before the first and after the last."""
    def f(t):
        if t <= points[0][0]:
            return points[0][1]
        for (a, va), (b, vb) in zip(points, points[1:]):
            if t <= b:
                return va + (vb - va) * ease(t, a, b - a)
        return points[-1][1]
    return f


# --- the story -------------------------------------------------------------------------------------------------

class St(S):
    """A story on 1080×1920; frame(u) = u in seconds (no mirrored exit): it leaves pushed up in its last 0.4 s."""

    def __init__(self, t, dur):
        S.__init__(self, t, dur)
        self.pivot = (W / 2, H / 2)
        self.oa = dur - 0.4

    def frame(self, u):
        return u

    def off(self, t):
        return -(H + 60) * ei(t, self.oa, 0.4)


def _p(id, es_, en, order, dur, tags=(), thumb=None):
    return tall(f"ig2-{id}", es_, en, "instagram", dur, order=order,
                tags=["instagram", "historia", "reels", "colores"] + list(tags),
                thumb_at=thumb if thumb is not None else round(dur * 0.6, 1))


def shp(s, name, layers, g, kind="rectangle", path=None, base=None, radius=0.0):
    """A shape: g(t) = (cx, cy, w, h, rot, op)."""
    def gg(t, u):
        cx, cy, w, h, rot, op = g(t)
        return cx, cy + s.off(t), w, h, rot, op
    return s.obj(name, layers, gg, kind=kind, path=path, base=base, radius=radius)


def rct(s, name, layers, r, op=None, rot=None, **kw):
    """A box covering r(t) = (x0, y0, x1, y1)."""
    def g(t):
        x0, y0, x1, y1 = r(t)
        return ((x0 + x1) / 2, (y0 + y1) / 2, max(0.0, x1 - x0), max(0.0, y1 - y0), rot(t) if rot else 0.0,
                op(t) if op else 1.0)
    return shp(s, name, layers, g, **kw)


def bg(s, colour, name="Fondo"):
    return rct(s, name, col(colour), lambda t: (-10, -10, W + 10, H + 10))


def ink_width(content, family, weight, cap, sp=0.0):
    """Width of a line whose capitals are `cap` px tall (letter spacing sp em)."""
    f = f6._font(family, weight)
    bb, hb = f.getbbox(content), f.getbbox("H")
    size = 400 * cap / max(1, hb[3] - hb[1])
    ink = (f.getlength(content[:-1]) + f.getbbox(content[-1])[2] - bb[0]) / 400
    return size * (ink + sp * (len(content) - 1))


def txt(s, content, x, cy, family, weight, colour, name, width=None, cap=None, align="center", sp=0.0, geom=None,
        bold=(), editable=True):
    """A line centred on cy whose ink is `width` wide (or whose capitals are `cap` tall) from x (its centre, left
    or right edge by align); geom(t) = (dx, dy, scale, rot, op)."""
    if width is None:
        width = ink_width(content, family, weight, cap, sp)
    p = f6.Piece(s.t, s.dur, 0, mirror=False)
    p.frame = s.frame
    clip = p.text(content, x, cy - 1, cy + 1, width, family, weight, colour, name, align=align, spacing_em=sp,
                  editable=editable, case="none", bold=bold)

    def g(fr, u):
        dx, dy, sc, rot, op = geom(fr) if geom else (0.0, 0.0, 1.0, 0.0, 1.0)
        return dx, dy + s.off(fr), sc, rot, op
    s.tmove(clip, g)
    return clip


def tin(clip, at, preset="fade", stagger=0.04, dur=0.3, unit="character", order="forward", **kw):
    """The text comes in (only) from `at` s."""
    clip["textStyle"]["animation"] = {"in": tanim(preset, duration=dur, unit=unit, stagger=stagger, ease="easeOut",
                                                  delay=at, order=order, **kw)}
    return clip


def fly(clip, at, dx, dy, rot, stagger=0.06, dur=0.5, blur=0, order="forward"):
    """Letters fly in one after another from (dx, dy) px away, turned rot degrees."""
    sel = {"driver": "stagger", "domain": "character", "staggerUs": us(stagger), "durationUs": us(dur),
           "ease": "easeOut", "order": order, "seed": 7}
    props = {"opacity": 0, "position": {"x": dx, "y": dy, "unit": "px"}, "rotation": rot}
    if blur:
        props["blur"] = blur
    clip["textStyle"]["animation"] = {"in": {"animators": [{"name": "Entrada", "selectors": [sel], "props": props}],
                                             "delayUs": us(at)}}
    return clip


def pic(s, name, sample, box=(0, 0, W, H), win=None, geom=None, fx=(), label=None, reuse=None, op=None):
    """A photo slot laid out over box; geom(t) = (dx, dy, scale). win = a window clip (made by the caller with
    `window`) the photo shows through (track matte)."""
    t = s.t
    b = Box(box[0], box[1], box[2] - box[0], box[3] - box[1])
    motion = []
    for u in frames_of(s.dur):
        dx, dy, sc = geom(u) if geom else (0.0, 0.0, 1.0)
        motion.append((u, {"s": sc, "dx": dx, "dy": dy + s.off(u)}, "linear"))
    clip = t.photo(t.track("video", name), sample, 0.0, s.dur, b, motion, label=label or name, reuse=reuse)
    clip["name"] = name
    if fx:
        clip["effects"] = [dict(e) for e in fx]
    if win is not None:
        clip["matte"] = {"clip": win["id"], "mode": "alpha"}
    if op:
        clip["opacity"] = keys([(u, round(cl(op(u)), 4), "linear") for u in frames_of(s.dur)])
    return clip


def window(s, name, r=None, g=None, kind="rectangle", path=None, base=None):
    """A white shape used only as a matte: r(t) = rect, or g(t) = (cx, cy, w, h, rot, op)."""
    if r is not None:
        return rct(s, f"{name} (ventana)", col(WHITE), r, kind=kind, path=path, base=base)
    return shp(s, f"{name} (ventana)", col(WHITE), g, kind=kind, path=path, base=base)


def outline(s, name, rect, w, colour, at, n, alpha=1.0, dy=None, dx=None):
    """A thin rectangle outline that draws itself from its top-left corner (its four sides growing together)."""
    x0, y0, x1, y1 = rect
    ox = dx or (lambda t: 0.0)
    oy = dy or (lambda t: 0.0)
    p = lambda t: es(t, at, n)  # noqa: E731
    lay = col(colour, alpha)
    rct(s, f"{name} (arriba)", lay, lambda t: (x0 + ox(t), y0 - w / 2 + oy(t), x0 + (x1 - x0) * p(t) + ox(t),
                                                y0 + w / 2 + oy(t)))
    rct(s, f"{name} (izquierda)", lay, lambda t: (x0 - w / 2 + ox(t), y0 + oy(t), x0 + w / 2 + ox(t),
                                                   y0 + (y1 - y0) * p(t) + oy(t)))
    rct(s, f"{name} (derecha)", lay, lambda t: (x1 - w / 2 + ox(t), y1 - (y1 - y0) * p(t) + oy(t), x1 + w / 2 + ox(t),
                                                 y1 + oy(t)))
    rct(s, f"{name} (abajo)", lay, lambda t: (x1 - (x1 - x0) * p(t) + ox(t), y1 - w / 2 + oy(t), x1 + ox(t),
                                               y1 + w / 2 + oy(t)))


def circle_path(a0=-90.0, turn=360.0, steps=96):
    pts = [(50 + 50 * math.cos(math.radians(a0 + turn * i / steps)),
            50 + 50 * math.sin(math.radians(a0 + turn * i / steps))) for i in range(steps + 1)]
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts)


def dashes(p0, p1, dash, gap, width):
    """One custom path (on its own 0..100 box) of dashes along p0 → p1; returns (path, box)."""
    (ax, ay), (bx, by) = p0, p1
    L = math.hypot(bx - ax, by - ay)
    ux, uy = (bx - ax) / L, (by - ay) / L
    nx, ny = -uy * width / 2, ux * width / 2
    x0, y0 = min(ax, bx) - width, min(ay, by) - width
    bw, bh = abs(bx - ax) + 2 * width, abs(by - ay) + 2 * width
    parts, d = [], 0.0
    while d < L:
        e = min(L, d + dash)
        q = [(ax + ux * d + nx, ay + uy * d + ny), (ax + ux * e + nx, ay + uy * e + ny),
             (ax + ux * e - nx, ay + uy * e - ny), (ax + ux * d - nx, ay + uy * d - ny)]
        parts.append("M " + " L ".join(f"{(x - x0) / bw * 100:.3f} {(y - y0) / bh * 100:.3f}" for x, y in q) + " Z")
        d += dash + gap
    return " ".join(parts), (x0, y0, x0 + bw, y0 + bh)


def art(make):
    """In a horizontal video the story keeps its shape (one column of art); only the plain backgrounds stretch."""
    def wrapped():
        return art_except(make(), keep=("Fondo",))
    wrapped.__name__ = make.__name__
    wrapped.__module__ = make.__module__
    return wrapped


# --- 1. Face with colour bands and circles (8.6-13.6 s of the video) ------------------------------------------
def face_bands():
    D = 5.6
    t = _p("rostro-franjas", "Historia: rostro con franjas y círculos de color", "Story: face with colour bands and "
           "circles", 15200, D, ["retrato", "marca", "blanco y negro"], thumb=2.9)
    s = St(t, D)
    DARK = "#434248"
    bg(s, WHITE)
    # The face pans from the mouth to the eyes while the bands sweep up.
    pic(s, "Foto", "portrait-04", geom=lambda t: (0.0, -560 * (1 - eo(t, 0, 1.6)), 1.0 + 0.6 * (1 - eo(t, 0, 1.6))),
        fx=[GRAY], label="Foto 1")
    # 3.3 s: a yellow-toned photo sweeps in from the right.
    w2 = window(s, "Foto 2", r=lambda t: (W * (1 - eo(t, 3.3, 0.45)), 0, W + 4, H))
    pic(s, "Foto 2", "portrait-01", win=w2, fx=[duo("#3A2600", "#FFD52E", contrast=0.6)], label="Foto 2",
        geom=lambda t: (0.0, 0.0, 1.06 - 0.06 * es(t, 3.3, 2.0)))
    ty = tab([(0.35, 1650), (0.9, 260), (1.6, 110), (2.8, 0)])
    txt(s, "The", 276, 257, M, 700, DARK, "Título (arriba)", width=88, align="left",
        geom=lambda t: (0, ty(t), 1, 0, 1))
    txt(s, "STUDIO", 279, 341, M, 800, DARK, "Título", width=560, align="left", geom=lambda t: (0, ty(t), 1, 0, 1))
    rct(s, "Línea", col(DARK), lambda t: (536 - 330 * es(t, 0.6, 0.45), 466 + ty(t), 536 + 330 * es(t, 0.6, 0.45),
                                          479 + ty(t)))
    sy = tab([(0.85, 800), (1.5, 220), (2.8, 0)])
    txt(s, "YOUR CREATIVE PROJECT", 534, 568, M, 700, DARK, "Subtítulo", width=725, sp=0.12,
        geom=lambda t: (0, sy(t), 1, 0, es(t, 0.85, 0.25)))
    cg = tab([(0.9, 260), (1.6, 110), (2.8, 0)])
    circles = [("Círculo menta", "#6DD3B0", 412, 1186, 608, 0.9), ("Círculo celeste", "#6FD9E2", 793, 1386, 430, 1.05)]
    wins = []
    for name, c, x, y, d, at in circles:
        g = (lambda x, y, d, at: lambda t: (x, y + cg(t), d * max(0.0, eb(t, at, 0.4)), d * max(0.0, eb(t, at, 0.4)),
                                            0, 1))(x, y, d, at)
        shp(s, name, col(c), g, kind="ellipse", base=(d, d))
        wins.append((name, g, d))
    for i, (name, g, d) in enumerate(wins):
        w = window(s, f"Letras {i + 1}", g=g, kind="ellipse", base=(d, d))
        c = txt(s, "HEY", 552, 1255, M, 900, WHITE, "Letras" if i == 0 else f"Letras {i + 1}", width=840,
                geom=lambda t: (0, cg(t), 1, 0, 1), editable=(i == 0))
        c["matte"] = {"clip": w["id"], "mode": "alpha"}
    shp(s, "Punto amarillo", col("#FFB300"), lambda t: (469, 1556 + cg(t), 264 * max(0.0, eb(t, 1.2, 0.35)),
                                                         264 * max(0.0, eb(t, 1.2, 0.35)), 0, 1), kind="ellipse",
        base=(264, 264))
    # The three bands sweep up over the face and close into thin stripes at the top.
    e0 = tab([(0.0, 1960), (0.45, 200), (1.0, -150)])
    e1 = tab([(0.0, 2090), (0.45, 300), (1.0, -12), (1.4, -12)])
    e2 = tab([(0.0, 2230), (0.45, 430), (1.0, 48), (1.5, -4)])
    e3 = tab([(0.0, 2600), (0.3, 1960), (0.45, 560), (1.0, 125), (1.6, -4)])
    bands = [("Franja oscura", "#4C4B51", e0, e1), ("Franja coral", "#EA827D", e1, e2), ("Franja menta", "#8FE4D2", e2, e3)]
    for name, c, top, bot in bands:
        rct(s, name, col(c), lambda t, top=top, bot=bot: (-10, top(t), W + 10, max(top(t), bot(t))))
        cap = lambda t, top=top, bot=bot: min(150.0, 0.5 * max(0.0, bot(t) - top(t)))  # noqa: E731
        shp(s, f"{name} (curva)", col(c), lambda t, top=top, cap=cap: (540, top(t), W, 2 * cap(t), 0, 1),
            kind="ellipse", base=(W, 300))
    return t


# --- 2. Cooking opener (8.4-13.6 s) ----------------------------------------------------------------------------
def cooking():
    D = 5.6
    t = _p("cocina", "Historia: apertura de programa de cocina", "Story: cooking show opener", 15201, D,
           ["cocina", "comida", "apertura"], thumb=4.8)
    s = St(t, D)
    bg(s, "#121212")
    pic(s, "Foto", "cooking-05", geom=lambda t: (0.0, (H + 20) * eo(t, 3.5, 0.45), 1.1 - 0.1 * es(t, 0, 3.5)),
        label="Foto 1")
    pic(s, "Foto 2", "y6-dish-02", geom=lambda t: (0.0, -(H + 20) * (1 - eo(t, 3.5, 0.45)), 1.0), label="Foto 2")
    rct(s, "Sombra", grad([(0.0, "#000000", 0.0), (1.0, "#000000", 0.75)]), lambda t: (-10, 1050, W + 10, H + 10))
    path, box = dashes((1062, 0), (0, 1900), 30, 22, 5)
    rct(s, "Línea punteada", col(WHITE, 0.9), lambda t: box, path=path, base=(box[2] - box[0], box[3] - box[1]))
    rct(s, "Cuadro", col(WHITE, 0.42), lambda t: (156, 952 - 455 * eo(t, 0.2, 0.6), 954, 952 + 456 * eo(t, 0.2, 0.6)))
    for i, sign in enumerate((-1, 1)):
        rct(s, f"Raya {i + 1}", col(WHITE, 0.85), lambda t, sign=sign: (-10, 950 + sign * 830 * eo(t, 0.05, 0.8) - 3,
                                                                          W + 10, 950 + sign * 830 * eo(t, 0.05, 0.8) + 3),
            op=lambda t: 1 - es(t, 0.65, 0.3))
    c = txt(s, "COOKING", 546, 913, AS, 400, WHITE, "Título", width=750)
    tin(c, 0.35, "glitch-in", stagger=0.05, dur=0.35, order="random")
    c = txt(s, "Show Opener", 553, 1019, AS, 400, WHITE, "Subtítulo", width=590)
    tin(c, 0.5, "glitch-in", stagger=0.04, dur=0.35, order="random")
    for i, (word, w, y) in enumerate((("Perfect", 213, 1480), ("Cooking", 236, 1530), ("Show", 112, 1578),
                                      ("Stories", 214, 1628))):
        c = txt(s, word, 540, y, M, 800, WHITE, "Texto" if i == 0 else f"Texto {i + 1}", width=w)
        tin(c, 0.4 + 0.1 * i, "drop", stagger=0.03, dur=0.3)
    for i, x in enumerate((470, 538, 606)):
        shp(s, f"Punto {i + 1}", col(WHITE), lambda t, i=i, x=x: (x, 1777, 20 * max(0.0, eb(t, 1.0 + 0.08 * i, 0.25)),
                                                                  20 * max(0.0, eb(t, 1.0 + 0.08 * i, 0.25)), 0, 1),
            kind="ellipse", base=(20, 20))
    # The band: big vertical COOKING on yellow that closes into a thin line.
    half = tab([(0.0, 1100), (0.35, 113), (0.8, 15), (1.0, 0)])
    band = lambda t: (-10, 950 - half(t), W + 10, 950 + half(t))  # noqa: E731
    rct(s, "Franja amarilla", col("#FFD21F"), band)
    w = window(s, "Franja", r=band)
    c = txt(s, "COOKING", 540, 950, AS, 400, "#1B1B1B", "Franja (texto)", width=2500, editable=False,
            geom=lambda t: (0, 700 - 1400 * es(t, 0, 1.0), 1, -90, 1))
    c["matte"] = {"clip": w["id"], "mode": "alpha"}
    # 3.4 s: a white outline square spins in round the title.
    sz = tab([(3.4, 0.5), (4.0, 1.04), (4.5, 1.0)])
    rot = tab([(3.4, 45), (4.0, -8), (4.5, 3)])
    shp(s, "Marco", ring(WHITE, 16), lambda t: (548, 927, 866 * sz(t), 986 * sz(t), rot(t), 1.0 if t >= 3.4 else 0.0),
        base=(866, 986))
    return t


# --- 3. Fashion (8.4-13.6 s) -----------------------------------------------------------------------------------
def fashion():
    D = 5.8
    t = _p("moda", "Historia: Fashion sobre menta y rojo", "Story: Fashion on mint and red", 15202, D,
           ["moda", "perfil", "empresa"], thumb=5.0)
    s = St(t, D)
    bg(s, "#86DDE1")
    pic(s, "Foto", "fx-hair-05", geom=lambda t: (0.0, -380, 1.0), label="Foto 1")
    teal = tab([(0.0, 1930), (0.35, 853)], ease=eo)
    rct(s, "Menta", col("#86DDE1"), lambda t: (-10, teal(t), W + 10, H + 10))
    w2 = window(s, "Foto 2", r=lambda t: (-10, -10, -10 + (W + 20) * eo(t, 3.8, 0.5), H + 10))
    pic(s, "Foto 2", "man-04", win=w2, fx=[GRAY], label="Foto 2")
    rct(s, "Círculo rojo", col("#E8473E"), lambda t: (540 - 1002, 1108 + 950 * (1 - eo(t, 3.6, 0.6)),
                                                      540 + 1002, 1108 + 950 * (1 - eo(t, 3.6, 0.6)) + 2004),
        kind="ellipse", base=(2004, 2004))
    sp_ = lambda t: 240 * (1 - eo(t, 0, 0.9)) + 700 * es(t, 3.7, 0.7)  # noqa: E731
    rct(s, "Foto pequeña (borde)", col(WHITE), lambda t: (319, 1241 + sp_(t), 804, 1726 + sp_(t)))
    w3 = window(s, "Foto pequeña", r=lambda t: (349, 1271 + sp_(t), 774, 1696 + sp_(t)))
    pic(s, "Foto pequeña", None, box=(349, 1271, 774, 1696), win=w3, reuse="p1",
        geom=lambda t: (0.0, sp_(t), 1.0))
    gy = lambda t: 518 * es(t, 3.7, 0.7)  # noqa: E731
    outline(s, "Caja", (123, 712, 952, 955), 4, WHITE, 0.7, 0.5, alpha=0.9, dy=gy)
    c = txt(s, "Fashion", 537, 842, M, 900, WHITE, "Título", width=739, geom=lambda t: (0, gy(t), 1, 0, 1))
    fly(c, 0.1, 260, -460, -70, stagger=0.06, dur=0.55)
    txt(s, "COMPANY PROFILE", 540, 1008, M, 600, "#EFFFFF", "Subtítulo", width=540, sp=0.25,
        geom=lambda t: (0, 610 * es(t, 3.7, 0.7), 1, 0, es(t, 1.1, 0.4)))
    y0 = tab([(0.0, 1500), (0.3, 0)], ease=eo)
    th = tab([(0.0, 700), (0.3, 160), (0.8, 12)])
    rct(s, "Franja amarilla", col("#FFE500"), lambda t: (-10, y0(t) - 10, W + 10, y0(t) + th(t)))
    return t


# --- 4. YOUR LIFE (13.8-19 s) ----------------------------------------------------------------------------------
def your_life():
    D = 5.4
    t = _p("tu-vida", "Historia: YOUR LIFE con franjas amarillas", "Story: YOUR LIFE with yellow bands", 15203, D,
           ["vida", "consejos", "amarillo"], thumb=1.6)
    s = St(t, D)
    bg(s, "#26272C")
    inn = lambda t: H * (1 - eo(t, 0, 0.55))  # noqa: E731
    out = lambda t: -W * es(t, 3.0, 0.45)  # noqa: E731
    Y = "#FFCE00"

    def at(r):
        # clamped to the frame: in a horizontal video the story is a column and nothing may show beside it
        return lambda t: (max(0.0, r[0] + out(t)), r[1] + inn(t), max(0.0, r[2] + out(t)), r[3] + inn(t))
    rct(s, "Franja de arriba", col(Y), at((-10, -10, W + 10, 276)))
    rct(s, "Blanco", col(WHITE), at((-10, 276, W + 10, 781)))
    w1 = window(s, "Foto", r=at((0, 276, W, 781)))
    pic(s, "Foto", "fx-face-03", box=(0, 276, W, 781), win=w1, fx=[GRAY], label="Foto 1",
        geom=lambda t: (out(t), inn(t), 1.0))
    rct(s, "Banda", col("#26272C"), at((-10, 781, W + 10, 1165)))
    txt(s, "YOUR LIFE", 546, 963, M, 600, WHITE, "Título", width=633, sp=0.25,
        geom=lambda t: (out(t), inn(t), 1, 0, 1))
    w2 = window(s, "Foto 2", r=at((0, 1165, W, 1677)))
    pic(s, "Foto 2", "beach-02", box=(0, 1165, W, 1677), win=w2, label="Foto 2", geom=lambda t: (out(t), inn(t), 1.0))
    rct(s, "Franja de abajo", col(Y), at((-10, 1677, W + 10, H + 10)))
    # 3.0 s: the next photo pushes it out to the left.
    nx = lambda t: W * (1 - es(t, 3.0, 0.45))  # noqa: E731
    w3 = window(s, "Foto 3", r=lambda t: (min(W, nx(t)), 0, W, H))
    pic(s, "Foto 3", "y6-fog-01", label="Foto 3", win=w3, geom=lambda t: (nx(t), 0.0, 1.08 - 0.08 * es(t, 3.0, 2.4)))
    outline(s, "Marco", (90, 77, 996, 1830), 4, WHITE, 3.0, 0.01, alpha=0.85, dx=nx)
    bar = lambda t: 140 * es(t, 3.3, 2.0)  # noqa: E731
    rct(s, "Barra blanca", col(WHITE), lambda t: (901 + nx(t), 837 + bar(t), 996 + nx(t), 1052 + bar(t)))
    dr = lambda t: 40 * es(t, 3.4, 2.0)  # noqa: E731
    txt(s, "WAYS TO GROW", 553, 246, M, 400, WHITE, "Texto", width=670, sp=0.12, bold=("WAYS",),
        geom=lambda t: (nx(t), dr(t), 1, 0, es(t, 3.35, 0.3)))
    txt(s, "YOUR PROFILE", 558, 317, M, 400, WHITE, "Texto 2", width=722, sp=0.12, bold=("PROFILE",),
        geom=lambda t: (nx(t), dr(t), 1, 0, es(t, 3.45, 0.3)))
    return t


# --- 5. MODERN INTERIOR DESIGN / PERFECT STYLE (13.8-19 s) ----------------------------------------------------
def interior():
    D = 5.4
    t = _p("interior", "Historia: diseño de interiores con círculos de color", "Story: interior design with colour "
           "circles", 15204, D, ["interiores", "diseño", "hogar"], thumb=3.6)
    s = St(t, D)
    bg(s, "#E2524A")
    up = lambda t: -(H + 20) * es(t, 1.3, 0.45)  # noqa: E731
    rct(s, "Fondo rojo", grad([(0.0, "#C93B3D"), (1.0, "#F06A57")], angle=135), lambda t: (-10, -10 + up(t), W + 10,
                                                                                          H + 10 + up(t)))
    for i, (d, c, a) in enumerate(((2300, "#F07A62", 0.5), (1700, "#D84846", 0.6), (1150, "#B83137", 0.6))):
        shp(s, f"Arco {i + 1}", col(c, a), lambda t, d=d: (1000, 260 + up(t), d, d, 0, 1), kind="ellipse",
            base=(d, d))
    for name, c, x, y, d, at in (("Círculo menta", "#6DD3AE", 437, 793, 1236, 0.0),
                                 ("Círculo celeste", "#6BD8DF", 902, 1203, 880, 0.15),
                                 ("Círculo naranja", None, 328, 1597, 634, 0.3)):
        layers = col(c) if c else grad([(0.0, "#FFB300"), (1.0, "#FF7A00")])
        shp(s, name, layers, lambda t, x=x, y=y, d=d, at=at: (x, y + up(t), d * max(0.0, eb(t, at, 0.5)),
                                                              d * max(0.0, eb(t, at, 0.5)), 0, 1),
            kind="ellipse", base=(d, d))
    for i, (word, w, y) in enumerate((("MODERN", 593, 657), ("INTERIOR", 676, 812), ("DESIGN", 533, 964))):
        c = txt(s, word, 32, y, AS, 400, WHITE, "Título" if i == 0 else f"Título {i + 1}", width=w, align="left",
                geom=lambda t: (0, up(t), 1, 0, 1))
        tin(c, 0.25 + 0.12 * i, "rise", stagger=0.03, dur=0.3)
    # 1.3 s: everything scrolls up; the room photo with a red photo band on top comes in.
    inn = lambda t: (H + 20) * (1 - es(t, 1.3, 0.45))  # noqa: E731
    pic(s, "Foto", "interior-03", label="Foto 1", geom=lambda t: (0.0, inn(t), 1.0))
    redb = lambda t: 880 * (1 - es(t, 1.85, 0.75))  # noqa: E731
    w = window(s, "Foto 2", r=lambda t: (-10, -10 + inn(t), W + 10, redb(t) + inn(t)))
    pic(s, "Foto 2", "food-02", win=w, fx=[duo("#7A0A14", "#FF7062", contrast=0.6)], label="Foto 2",
        geom=lambda t: (0.0, inn(t) - 400, 1.0))
    sz = tab([(1.55, 300), (2.3, 750)], ease=eo)
    rot = tab([(1.5, 0), (1.95, 45), (2.7, 0)])
    rct(s, "Cuadrado menta", col("#8DDCD5", 0.82), lambda t: (540 - sz(t) / 2, 940 - sz(t) / 2 + inn(t),
                                                              540 + sz(t) / 2, 940 + sz(t) / 2 + inn(t)),
        rot=rot, op=lambda t: es(t, 1.45, 0.15))
    c = txt(s, "PERFECT", 543, 900, M, 700, "#3B3A48", "Texto", width=484, sp=0.3, geom=lambda t: (0, inn(t), 1, 0, 1))
    tin(c, 1.55, "fade", stagger=0.04, dur=0.25)
    c = txt(s, "STYLE", 543, 982, M, 700, "#3B3A48", "Texto 2", width=333, sp=0.3,
            geom=lambda t: (0, inn(t), 1, 0, 1))
    tin(c, 1.75, "rise", stagger=0.05, dur=0.3)
    for i, (a, b) in enumerate((((300, 330), (912, 565)), ((900, 1640), (174, 1323)))):
        g = lambda t, a=a, b=b, i=i: (a[0] + (b[0] - a[0]) * es(t, 1.8 + 0.1 * i, 1.2),
                                       a[1] + (b[1] - a[1]) * es(t, 1.8 + 0.1 * i, 1.2) + inn(t),
                                       156, 156, 45 * (1 - es(t, 1.8 + 0.1 * i, 1.2)), es(t, 1.7, 0.15))
        shp(s, f"Cuadradito {i + 1}", col("#F2404A", 0.85), g)
    return t


# --- 6. Say what's on your mind (13.8-19 s) -------------------------------------------------------------------
def your_mind():
    D = 5.0
    t = _p("tu-mente", "Historia: Say what's on your mind en violeta", "Story: Say what's on your mind in purple",
           15205, D, ["frase", "violeta", "pregunta"], thumb=3.0)
    s = St(t, D)
    bg(s, "#4B1E86")
    PURPLE = duo("#2E0B63", "#E7A8F5", contrast=0.55)
    push = lambda t: es(t, 0.5, 0.9)  # noqa: E731
    pic(s, "Foto", "portrait-06", label="Foto 1", fx=[PURPLE], geom=lambda t: (0.0, -300 * push(t), 1.05))
    top = lambda t: 1520 - 887 * push(t)  # noqa: E731
    w = window(s, "Foto 2", r=lambda t: (-10, top(t), W + 10, H + 10))
    pic(s, "Foto 2", "tk7-bloom-01", win=w, fx=[duo("#3A0F7A", "#F2A7E6", contrast=0.6)], label="Foto 2",
        geom=lambda t: (0.0, 600 * (1 - push(t)), 1.1))
    ty = lambda t: 270 * (1 - push(t))  # noqa: E731
    c = txt(s, "Say what's on your mind", 543, 961, M, 400, WHITE, "Texto", width=827, bold=("Say what's on",),
            geom=lambda t: (0, ty(t), 1, 0, 1))
    tin(c, 0.05, "fade", stagger=0.02, dur=0.3, unit="word")
    br = lambda t: eo(t, 1.25, 0.35)  # noqa: E731
    for side in (-1, 1):
        x = lambda t, side=side: 541 + side * (330 + 140 * br(t))  # noqa: E731
        rct(s, "Corchete" + (" 2" if side > 0 else ""), col(WHITE), lambda t, x=x: (x(t) - 3, 873, x(t) + 3, 1054),
            op=br)
        for y in (873, 1048):
            rct(s, "Corchete (punta)", col(WHITE), lambda t, x=x, y=y, side=side: (
                min(x(t), x(t) - side * 30), y, max(x(t), x(t) - side * 30), y + 6), op=br)
    sq = lambda t: max(0.0, eb(t, 1.55, 0.35))  # noqa: E731
    pos = lambda t: es(t, 1.9, 0.8)  # noqa: E731
    side_ = lambda t: (376 + 63 * pos(t)) * sq(t)  # noqa: E731
    cx = lambda t: 577 + (575 - 577) * pos(t)  # noqa: E731
    cy = lambda t: 1289 + (1560 - 1289) * pos(t)  # noqa: E731
    rct(s, "Foto pequeña (borde)", col(WHITE), lambda t: (cx(t) - side_(t) / 2, cy(t) - side_(t) / 2,
                                                         cx(t) + side_(t) / 2, cy(t) + side_(t) / 2))
    inner = lambda t: (cx(t) - side_(t) / 2 + 14, cy(t) - side_(t) / 2 + 14, cx(t) + side_(t) / 2 - 14,  # noqa: E731
                       cy(t) + side_(t) / 2 - 14)
    w3 = window(s, "Foto pequeña", r=inner)
    pic(s, "Foto pequeña", "fx-hair-03", box=(355, 1340, 795, 1780), win=w3, label="Foto 3",
        geom=lambda t: (cx(t) - 575, cy(t) - 1560, max(0.3, (376 + 63 * pos(t)) / 440)))
    return t


# --- 7. INTRODUCING OUR STORIES (19-25.6 s) --------------------------------------------------------------------
def introducing():
    D = 6.2
    t = _p("presentamos", "Historia: INTRODUCING OUR STORIES con franjas de degradado", "Story: INTRODUCING OUR "
           "STORIES with gradient stripes", 15206, D, ["presentación", "degradado"], thumb=4.6)
    s = St(t, D)
    bg(s, WHITE)
    push = lambda t: es(t, 3.15, 0.5)  # noqa: E731
    up = lambda t: -(H + 20) * push(t)  # noqa: E731
    w = window(s, "Foto", r=lambda t: (152, -10 + up(t), W + 10, H + 10 + up(t)))
    pic(s, "Foto", "fx-woman-07", box=(152, 0, W, H), win=w, label="Foto 1",
        geom=lambda t: (0.0, up(t), 1.5 - 0.5 * eo(t, 0.0, 2.2)))
    # The gradient breaks into stripes that thin out and leave the photo.
    n = 7
    hh = H / n
    for i in range(n):
        at = 0.35 + 0.18 * ((i * 3) % n) / n
        c0 = (hh * i, hh * (i + 1))

        def r(t, i=i, at=at, c0=c0):
            th = (c0[1] - c0[0]) * (1 - es(t, at, 1.6 + 0.1 * i))
            mid = (c0[0] + c0[1]) / 2 + 60 * math.sin(i * 1.7) * es(t, at, 1.6)
            return (152, mid - th / 2 + up(t), W + 10, mid + th / 2 + up(t))
        top = i / n
        rct(s, f"Franja {i + 1}", grad([(0.0, mix_hex("#86EC5A", "#F2C80E", top)),
                                       (1.0, mix_hex("#86EC5A", "#F2C80E", top + 1 / n))], angle=90), r)
    c = txt(s, "INTRODUCING OUR STORIES", 106, 1015, M, 400, "#2A2A2A", "Texto", width=1600,
            bold=("INTRODUCING", "STORIES"), geom=lambda t: (0, up(t), 1, -90, 1))
    tin(c, 0.1, "fade", stagger=0.02, dur=0.2)
    # 3.15 s: the next photo comes up with the pink and orange circles.
    inn = lambda t: (H + 20) * (1 - push(t))  # noqa: E731
    pic(s, "Foto 2", "friends-02", label="Foto 2", geom=lambda t: (0.0, inn(t), 1.08 - 0.08 * es(t, 3.2, 2.5)),
        fx=[duo("#3A1500", "#FFE3A0", strength=0.35)])
    d1 = lambda t: 860 * eo(t, 3.4, 0.6)  # noqa: E731
    shp(s, "Círculo rosa", grad([(0.0, "#FF2BD6"), (1.0, "#FF5FA8")], angle=45),
        lambda t: (150, 240, d1(t), d1(t), 0, 1), kind="ellipse", base=(860, 860))
    d2 = lambda t: 560 * eo(t, 3.5, 0.6)  # noqa: E731
    shp(s, "Círculo naranja", grad([(0.0, "#FFD21A"), (1.0, "#FF3FA6")], angle=90),
        lambda t: (885, 1735, d2(t), d2(t), 0, 1), kind="ellipse", base=(560, 560))
    rot = tab([(3.5, 45), (4.3, 0)])
    shp(s, "Marco", ring(WHITE, 5), lambda t: (538, 964, 544 * (0.6 + 0.4 * eo(t, 3.5, 0.7)),
                                               544 * (0.6 + 0.4 * eo(t, 3.5, 0.7)), rot(t), es(t, 3.45, 0.2)),
        base=(544, 544))
    c = txt(s, "INTRODUCING OUR STORIES", 532, 959, M, 400, WHITE, "Texto 2", width=987,
            bold=("INTRODUCING", "STORIES"))
    tin(c, 3.6, "fade", stagger=0.03, dur=0.25)
    return t


def mix_hex(a, b, x):
    x = cl(x)
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(pa[i] + (pb[i] - pa[i]) * x):02X}" for i in range(3))


# --- 8. % YOUR CITY NEW (19-25.6 s) ----------------------------------------------------------------------------
def city_sale():
    D = 5.8
    t = _p("ciudad-oferta", "Historia: oferta en tu ciudad con círculo %", "Story: city offer with a % circle", 15207,
           D, ["oferta", "descuento", "ciudad", "nuevo"], thumb=3.4)
    s = St(t, D)
    bg(s, WHITE)
    pic(s, "Foto", "city-04", label="Foto 1", fx=[GRAY], geom=lambda t: (0.0, 120, 1.12 - 0.08 * es(t, 0, 5.0)))
    rct(s, "Niebla", grad([(0.0, WHITE, 1.0), (0.45, WHITE, 0.9), (1.0, WHITE, 0.0)]), lambda t: (-10, -10, W + 10,
                                                                                                  1050))
    rct(s, "Sombra", grad([(0.0, "#000000", 0.0), (1.0, "#000000", 0.7)]), lambda t: (-10, 1300, W + 10, H + 10))
    # Coral leftovers of the transition.
    rct(s, "Cuña", col("#E8606A"), lambda t: (1040, 50, 1062, 50 + 1050 * (1 - es(t, 0.0, 0.6))))
    tri = "M 0 0 L 100 0 L 0 100 Z"
    shp(s, "Cuña 2", col("#E8606A"), lambda t: (130 * (1 - es(t, 0, 0.4)), 130 * (1 - es(t, 0, 0.4)),
                                                 260 * (1 - es(t, 0, 0.4)) + 1e-3, 260 * (1 - es(t, 0, 0.4)) + 1e-3, 0, 1),
        path=tri, base=(260, 260))
    d = lambda t: 720 * max(0.0, eb(t, 1.15, 0.55))  # noqa: E731
    cx = lambda t: 492 + 48 * es(t, 1.15, 0.9)  # noqa: E731
    cy = lambda t: 940 - 20 * es(t, 1.15, 0.9)  # noqa: E731
    shp(s, "Círculo", grad([(0.0, "#EE6A6E", 0.92), (1.0, "#3A0E16", 0.8)]), lambda t: (cx(t), cy(t), d(t), d(t), 0, 1),
        kind="ellipse", base=(720, 720))
    ringc = shp(s, "Aro", ring(WHITE, 5), lambda t: (cx(t), cy(t), 645 * max(0.0, eb(t, 1.15, 0.55)),
                                                     645 * max(0.0, eb(t, 1.15, 0.55)), 0, 1),
                path=circle_path(), base=(645, 645))
    ringc["shapeStyle"]["keyframes"] = {"trimEnd": keys([(u, round(100 * es(u, 1.3, 0.6), 3), "linear")
                                                         for u in frames_of(D)])}
    pc = lambda t: max(0.0, eb(t, 1.5, 0.35))  # noqa: E731
    txt(s, "%", 540, 908, M, 500, WHITE, "Descuento", width=322, geom=lambda t: (cx(t) - 540, cy(t) - 920, pc(t), 0,
                                                                                 1 if t > 1.5 else 0))
    cyy = tab([(0.85, -520), (1.6, -100), (2.2, 0)])
    c = txt(s, "YOUR CITY", 540, 1499, M, 500, WHITE, "Texto", width=610, sp=0.4, geom=lambda t: (0, cyy(t), 1, 0, 1))
    tin(c, 0.85, "fade", stagger=0.05, dur=0.3)
    ny = lambda t: -760 * (1 - eo(t, 0.0, 1.3))  # noqa: E731
    txt(s, "NEW", 540, 1678, M, 800, WHITE, "Título", width=332, geom=lambda t: (0, ny(t), 1, 0, 1))
    outline(s, "Caja", (297, 1571, 783, 1802), 5, WHITE, 1.0, 0.5)
    return t


# --- 9. DARK (19-25.6 s) ---------------------------------------------------------------------------------------
def grid_spacing(content, family, weight, size, width):
    f = f6._font(family, weight)
    bb = f.getbbox(content)
    ink = (f.getlength(content[:-1]) + f.getbbox(content[-1])[2] - bb[0]) / 400
    return (width / size - ink) / max(1, len(content) - 1)


def dark():
    D = 5.8
    t = _p("oscuro", "Historia: DARK con letras en rejilla", "Story: DARK with grid letters", 15208, D,
           ["oscuro", "moda", "tipografía"], thumb=3.8)
    s = St(t, D)
    bg(s, "#15222A")
    split = lambda t: es(t, 1.85, 0.6)  # noqa: E731
    for i, side in enumerate((-1, 1)):
        r = (lambda side: lambda t: (max(0.0, (0 if side < 0 else 540) + side * 400 * split(t)), -10,
                                     min(float(W), (540 if side < 0 else W) + side * 400 * split(t)), H + 10))(side)
        w = window(s, f"Foto{'' if i == 0 else ' (derecha)'}", r=r)
        pic(s, "Foto" if i == 0 else "Foto (derecha)", "man-03" if i == 0 else None, win=w,
            reuse=None if i == 0 else "p1", fx=[duo("#071116", "#B9CCD0", contrast=0.6)], label="Foto 1",
            geom=lambda t, side=side: (side * 400 * split(t), 0.0, 1.0 + 0.12 * split(t)))
    bx = tab([(0.55, 0.0), (1.0, 1.0)], ease=eo)
    down = lambda t: 576 * es(t, 1.9, 0.55)  # noqa: E731
    rct(s, "Caja", col(WHITE), lambda t: (543 - 362 * bx(t), 958 - 262 * bx(t) + down(t), 543 + 362 * bx(t),
                                          958 + 262 * bx(t) + down(t)))
    # The words spread over the photo in big white letters, then (on the box) small and dark: the white rows fade
    # out shrinking towards the box while the dark rows fade in (the reference shrinks one set of letters).
    rows = ("DARKNE", "SSAND", "STYLIST", "DESIGN")
    for i, word in enumerate(rows):
        yb, ys = 675 + 177 * i, 772 + 116 * i
        sb, ss = 56 / 0.7, 36 / 0.7  # font sizes from the capitals (Montserrat caps ≈ 0.7 em)
        c = txt(s, word, 538, yb, M, 700, WHITE, f"Texto (grande) {i + 1}", width=1025,
                sp=grid_spacing(word, M, 700, sb, 1025), editable=False,
                geom=lambda t, yb=yb, ys=ys: (0, (ys - yb) * 0.5 * es(t, 0.55, 0.35), 1, 0, 1 - es(t, 0.55, 0.3)))
        tin(c, 0.0, "flicker-in", stagger=0.03, dur=0.3, order="random")
        txt(s, word, 543, ys, M, 700, "#1C2A31", "Texto" if i == 0 else f"Texto {i + 1}", width=651,
            sp=grid_spacing(word, M, 700, ss, 651), geom=lambda t: (0, down(t), 1, 0, es(t, 0.65, 0.3)))
    # DARK rises from behind the box, turned to read upwards.
    wtop = window(s, "Título", r=lambda t: (-10, -10, W + 10, 696 + down(t)))
    c = txt(s, "DARK", 538, 666, M, 800, WHITE, "Título", width=1123, sp=0.32,
            geom=lambda t: (0, 1200 * (1 - eo(t, 2.0, 1.1)), 1, -90, 1 if t > 2.0 else 0))
    c["matte"] = {"clip": wtop["id"], "mode": "alpha"}
    return t


# --- 10. R / HAPPY (25.8-31.6 s) -------------------------------------------------------------------------------
def happy():
    D = 5.6
    t = _p("feliz", "Historia: HAPPY con letra gigante y rectángulo menta", "Story: HAPPY with a giant letter and a "
           "mint box", 15209, D, ["feliz", "blanco y negro", "letra"], thumb=4.2)
    s = St(t, D)
    bg(s, "#CFCFD2")
    pic(s, "Foto", "portrait-02", label="Foto 1", fx=[GRAY], geom=lambda t: (0.0, 0.0, 1.06 - 0.06 * es(t, 0.4, 4.0)))
    # Opening: the photo tiled in teal / coral / teal columns that scroll, then wipe away to the right.
    wipe = lambda t: (W + 20) * es(t, 0.45, 0.4)  # noqa: E731
    tints = (duo("#14504C", "#74E8DF", contrast=0.6), duo("#6A1C1A", "#F27872", contrast=0.6),
             duo("#14504C", "#74E8DF", contrast=0.6))
    for c in range(3):
        x0, x1 = 360 * c, 360 * (c + 1)
        sign = -1 if c == 1 else 1
        for r in range(4):
            def rr(t, x0=x0, x1=x1, r=r, sign=sign):
                y = -640 + 640 * r + sign * 320 * es(t, 0.0, 0.6) + (320 if sign < 0 else 0)
                return (max(x0, wipe(t)), y, x1, y + 640)
            w = window(s, f"Mosaico {c + 1}-{r + 1}", r=rr)
            pic(s, f"Mosaico {c + 1}-{r + 1}", None, box=(x0, -640 + 640 * r, x1, 640 * r), win=w, reuse="p1",
                fx=[tints[c]], geom=lambda t, sign=sign: (0.0, sign * 320 * es(t, 0.0, 0.6) + (320 if sign < 0 else 0),
                                                         1.0),
                op=lambda t: 1.0 if t < 0.9 else 0.0)
    # The giant R comes in from the right and flies to the corner.
    k = lambda t: es(t, 1.3, 0.6)  # noqa: E731
    gx = lambda t: 667 + (908 - 667) * k(t) + 900 * (1 - eo(t, 0.5, 0.35))  # noqa: E731
    gy = lambda t: 943 + (201 - 943) * k(t)  # noqa: E731
    sc = lambda t: 1 + (95 / 1012 - 1) * k(t)  # noqa: E731
    txt(s, "R", 667, 943, M, 800, WHITE, "Letra", width=804, geom=lambda t: (gx(t) - 667, gy(t) - 943, sc(t), 0,
                                                                              1 if t > 0.45 else 0))
    hy = lambda t: 600 * (1 - eo(t, 1.3, 0.55))  # noqa: E731
    rct(s, "Caja", col(WHITE), lambda t: (153, 1251 + hy(t), 867, 1376 + hy(t)), op=lambda t: es(t, 1.3, 0.1))
    txt(s, "HAPPY", 510, 1316, M, 800, "#1F1F24", "Título", width=650, sp=0.45, geom=lambda t: (0, hy(t), 1, 0, 1))
    gyy = lambda t: 400 * (1 - eo(t, 1.5, 0.55))  # noqa: E731
    rct(s, "Caja 2", col(WHITE), lambda t: (264, 1412 + gyy(t), 742, 1459 + gyy(t)), op=lambda t: es(t, 1.5, 0.1))
    txt(s, "GOOD TIMES", 503, 1436, M, 600, "#1F1F24", "Subtítulo", width=420, sp=0.4,
        geom=lambda t: (0, gyy(t), 1, 0, 1))
    # 3.2 s: a white line drops, the mint box grows out of it, the frame draws round it.
    rct(s, "Línea", col(WHITE), lambda t: (957, 600, 963, 600 + 594 * es(t, 3.2, 0.2)),
        op=lambda t: 1 - es(t, 3.6, 0.15))
    mint = rct(s, "Rectángulo menta", col("#7FD6A8", 0.95),
               lambda t: (971 - 909 * es(t, 3.35, 0.25), 1150 - 548 * es(t, 3.6, 0.3), 971,
                          1194 if t > 3.35 else 1150))
    mint["blendMode"] = "multiply"
    outline(s, "Marco", (56, 594, 977, 1200), 6, WHITE, 3.75, 0.4)
    return t


# --- 11. GREAT TRIP SUMMER (25.8-31.6 s) -----------------------------------------------------------------------
def summer_trip():
    D = 5.6
    t = _p("viaje-verano", "Historia: GREAT TRIP SUMMER con nube de fotos", "Story: GREAT TRIP SUMMER with a photo "
           "cloud", 15210, D, ["viaje", "verano", "nube"], thumb=3.8)
    s = St(t, D)
    bg(s, "#3DE4E4")
    rct(s, "Coral", col("#E5625F"), lambda t: (-10, -10, W + 10, 883))
    k = lambda t: es(t, 1.2, 0.8)  # noqa: E731
    first = ((366, 680, 350), (846, 992, 220), (452, 1225, 156))
    last = ((361, 810, 363), (841, 1043, 247), (451, 1251, 130))

    def circ(i):
        a, b = first[i], last[i]
        return lambda t: (a[0] + (b[0] - a[0]) * k(t), a[1] + (b[1] - a[1]) * k(t) - 120 * es(t, 1.2, 0.4)
                          * (1 - es(t, 1.6, 0.6)), 2 * (a[2] + (b[2] - a[2]) * k(t)), 2 * (a[2] + (b[2] - a[2]) * k(t)),
                          0, 1)
    for n, (sample, slot, op) in enumerate((("beach-05", None, None),
                                            ("nature-02", None, lambda t: es(t, 1.35, 0.4)))):
        for i in range(3):
            g = circ(i)
            w = window(s, f"Nube {n + 1}-{i + 1}", g=g, kind="ellipse", base=(800, 800))
            first_clip = (i == 0)
            pic(s, f"Foto {n + 1}" + ("" if first_clip else f" ({i + 1})"), sample if first_clip else None,
                box=(0, 360, W, 1500), win=w, reuse=None if first_clip else f"p{n + 1}", label=f"Foto {n + 1}",
                geom=lambda t: (0.0, -60 * k(t), 1.0), op=op)
        if n == 0:
            for i in range(3):
                g = circ(i)
                shp(s, f"Nube oscura {i + 1}", col("#2A3550"),
                    lambda t, g=g: (lambda v: (v[0], v[1], v[2], v[3], 0, es(t, 1.2, 0.15) * (1 - es(t, 1.6, 0.4))))(
                        g(t)), kind="ellipse", base=(800, 800))
    outline(s, "Marco", (42, 39, 1033, 1874), 5, WHITE, 0.0, 0.01, alpha=0.8)
    # SUMMER: cyan / coral letters in the cloud that go down and turn white.
    sy = lambda t: 700 * es(t, 1.2, 0.9)  # noqa: E731
    c = txt(s, "SUMMER", 535, 953, M, 700, "#3DE4E4", "Texto (color)", width=831, sp=0.5, editable=False,
            geom=lambda t: (0, sy(t), 1, 0, 1 - es(t, 1.6, 0.4)))
    c["textStyle"]["runs"] = [{"start": 3, "end": 6, "colorEnabled": True, "color": argb("#E5625F")}]
    txt(s, "SUMMER", 535, 953, M, 700, WHITE, "Texto", width=831, sp=0.5,
        geom=lambda t: (0, sy(t), 1, 0, es(t, 1.6, 0.4)))
    wg = window(s, "Título", r=lambda t: (-10, -10, W + 10, 300))
    gy_ = lambda t: 210 * (1 - eo(t, 1.15, 0.6))  # noqa: E731
    c = txt(s, "GREAT", 537, 222, M, 800, WHITE, "Título", width=805, sp=0.5, geom=lambda t: (0, gy_(t), 1, 0, 1))
    c["matte"] = {"clip": wg["id"], "mode": "alpha"}
    ty_ = lambda t: 90 * (1 - eo(t, 1.45, 0.5))  # noqa: E731
    w2 = window(s, "Título 2", r=lambda t: (-10, 270, W + 10, 360))
    c = txt(s, "TRIP", 540, 311, M, 800, WHITE, "Título 2", width=306, sp=0.5, geom=lambda t: (0, ty_(t), 1, 0, 1))
    c["matte"] = {"clip": w2["id"], "mode": "alpha"}
    return t


# --- 12. Yellow Stories poster (25.8-31.6 s) ------------------------------------------------------------------
def stories_poster():
    D = 5.6
    t = _p("cartel-amarillo", "Historia: cartel amarillo Your Stories", "Story: yellow Your Stories poster", 15211, D,
           ["cartel", "amarillo", "texto"], thumb=1.8)
    s = St(t, D)
    bg(s, "#FFD400")
    pic(s, "Foto", "interior-05", label="Foto 1", fx=[duo("#2A1E00", "#FFD630", contrast=0.4)],
        geom=lambda t: (0.0, 0.0, 1.05 - 0.05 * es(t, 0, 5.0)))
    dn = lambda t: 300 * (1 - eo(t, 0.0, 0.8)) + 260 * es(t, 2.3, 0.9) + 384 * es(t, 3.3, 0.6)  # noqa: E731
    txt(s, "Your", 540, 511, M, 800, "#121212", "Título (arriba)", cap=88, geom=lambda t: (0, dn(t), 1, 0, 1))
    txt(s, "Stories", 532, 706, M, 900, "#121212", "Título", width=1040, geom=lambda t: (0, dn(t), 1, 0, 1))
    for i, ln in enumerate(LOREM):
        txt(s, ln, 540, 885 + 40 * i, M, 500, "#1A1A1A", "Texto" if i == 0 else f"Texto {i + 1}", cap=19,
            geom=lambda t: (0, dn(t), 1, 0, 1))
    # 3.3 s: a red photo comes down from the top.
    inn = lambda t: -1000 * (1 - es(t, 3.3, 0.6))  # noqa: E731
    w = window(s, "Foto 2", r=lambda t: (-10, -10 + inn(t), W + 10, 992 + inn(t)))
    pic(s, "Foto 2", "food-03", box=(0, 0, W, 992), win=w, fx=[duo("#5A0008", "#FF6E62", contrast=0.6)],
        label="Foto 2", geom=lambda t: (0.0, inn(t), 1.0))
    return t


TEMPLATES = [art(f) for f in (face_bands, cooking, fashion, your_life, interior, your_mind, introducing, city_sale,
                              dark, happy, summer_trip, stories_poster)]
