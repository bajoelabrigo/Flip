"""Blue lower thirds, twelfth set (2026-11-07): the sixteen of 57730233.mp4 (1920×1080 at 30 fps, four at a time in
quadrants at half size), Montserrat ExtraBold with blue (#1B87F3 → #0751B9) and white. Moves: a thin line that opens
into a box (white ahead, blue behind), lines that rise from under their own baseline, letters that fade in one by
one, a bar that slides and uncovers the type, and two pieces turned a few degrees. Measured in the quadrants, scaled
×1.24 (0.62 of the reference's full size, as in the other sets) and laid out bottom-left (left 120, bottom 960),
with no background. Order 8690-8705. Not published until Jorge says the group is complete.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import wide
from scene import gradient, keys, tanim
from llt_motion import frames_of
from templates_llt_f import Piece, table

for w, file in ((700, "Montserrat-Bold"), (800, "Montserrat-ExtraBold"), (900, "Montserrat-Black")):
    f6._FILES[("Montserrat", w)] = f"fonts.basic/fonts/montserrat/{file}.ttf"
FONT = "Montserrat"
WHITE = "#FFFFFF"
BLUE = "#1B87F3"
DEEP = "#0751B9"
FPS = 30.0
S = 1.24
OPEN = table({50: 0.0, 53: 0.06, 56: 0.2, 59: 0.45, 62: 0.72, 65: 0.9, 68: 0.98, 70: 1.0})
EASE = table({0: 0.0, 2: 0.2, 4: 0.45, 6: 0.65, 8: 0.79, 10: 0.88, 12: 0.94, 14: 0.975, 16: 0.99, 18: 1.0})


def GRAD():
    return [gradient([(0.0, BLUE), (1.0, DEEP)], angle=0)]


def E(fr, start, frames):
    return EASE((fr - start) * 18 / frames)


class BluePiece(Piece):
    """Laid out in quadrant px: `bbox` (its ink in the quadrant) lands with its left at 120 and bottom at 960."""

    def __init__(self, t, dur, bbox):
        super().__init__(t, dur, 0)
        self.bx0, self.by1 = bbox[0], bbox[3]

    def frame(self, u):
        return min(u, self.dur - u) * FPS

    def X(self, x):
        return 120 + (x - self.bx0) * S

    def Y(self, y):
        return 960 - (self.by1 - y) * S

    def R(self, r):
        return (self.X(r[0]), self.Y(r[1]), self.X(r[2]), self.Y(r[3]))


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"llt12-{id}", es, en, "ytkit", dur, order=order, tags=["kit:lowerthirds", "tercio", "azul"] + tags,
                **kw)


def piece(id, es, en, order, D, bbox, tags=()):
    t = _kit(id, es, en, D, order, list(tags), thumb_at=round(D / 2, 1))
    return t, BluePiece(t, D, bbox)


def grow(p, full, kind, start, frames=18, line=0, thin=1.5):
    """fr -> screen rect of `full` (quadrant px) growing from frame `start`: h / v (out from the middle across /
    up and down), ltr, rtl, ttb, btt; with `line`, a thin line (thin px) waits that many frames first."""
    x0, y0, x1, y1 = p.R(full)
    th = thin * S

    def r(fr):
        if fr < start:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            return (cx, cy, cx, cy)
        k = E(fr, start + line, frames) if fr >= start + line else 0.0
        if kind == "h":
            cx, half = (x0 + x1) / 2, th / 2 + ((x1 - x0) / 2 - th / 2) * k
            return (cx - half, y0, cx + half, y1)
        if kind == "v":
            cy, half = (y0 + y1) / 2, th / 2 + ((y1 - y0) / 2 - th / 2) * k
            return (x0, cy - half, x1, cy + half)
        if kind == "ltr":
            return (x0, y0, x0 + th + (x1 - x0 - th) * k, y1)
        if kind == "rtl":
            return (x1 - th - (x1 - x0 - th) * k, y0, x1, y1)
        if kind == "ttb":
            return (x0, y0, x1, y0 + th + (y1 - y0 - th) * k)
        return (x0, y1 - th - (y1 - y0 - th) * k, x1, y1)
    return r


def inside(fn, rect):
    """fn's rect cut to `rect` (screen px)."""
    def r(fr):
        a = fn(fr)
        x0, y0 = max(a[0], rect[0]), max(a[1], rect[1])
        x1, y1 = min(a[2], rect[2]), min(a[3], rect[3])
        return (x0, y0, max(x0, x1), max(y0, y1))
    return r


def static(p, rect):
    r = p.R(rect)
    return lambda fr: r


def shape(p, name, colour, full, fn, grad=False, skew=0.0):
    clip = p.shape(name, colour, p.R(full), fn, skew=skew)
    if grad:
        clip["shapeStyle"]["layers"] = GRAD() + clip["shapeStyle"]["layers"][1:]
    return clip


def text(p, content, ink, colour, name, weight=800, align="left", reveal=None, shift=None, grad=False, anim=None):
    """A line whose ink is `ink` (quadrant px); shift(fr) = (dx, dy) in quadrant px."""
    x0, y0, x1, y1 = p.R(ink)
    edge = x0 if align == "left" else x1 if align == "right" else (x0 + x1) / 2
    sh = (lambda fr: tuple(v * S for v in shift(fr))) if shift else None
    clip = p.text(content, edge, y0, y1, x1 - x0, FONT, weight, colour, name, align=align, case="none", shift=sh,
                  reveal=reveal)
    if grad:
        clip["textStyle"]["layers"] = GRAD()
    if anim:
        clip["textStyle"]["animation"] = anim
    return clip


def per(preset, start, stagger, duration, unit="character", **params):
    """A per-unit entrance from frame `start`, and the same backwards to leave."""
    wait = round(start / FPS, 2)
    return {"in": tanim(preset, duration=duration, unit=unit, stagger=stagger, ease="easeOut", delay=wait,
                        order="forward", **params),
            "out": tanim(preset, duration=duration, unit=unit, stagger=stagger, ease="easeIn", delay=wait,
                         order="backward", **params)}


def rise_from(dist, start, frames=16):
    return lambda fr: (0.0, dist * (1 - E(fr, start, frames)))


def slide_from(dist, start, frames=16):
    return lambda fr: (-dist * (1 - E(fr, start, frames)), 0.0)


def turn(p, clips, pivot, deg):
    """Turns `clips` by deg (+ clockwise) about `pivot` (quadrant px): each box centre swings round the pivot and
    the clip turns about its own centre."""
    px, py = p.X(pivot[0]), p.Y(pivot[1])
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    for clip in clips:
        xs, ys = clip["x"]["keyframes"], clip["y"]["keyframes"]
        ws, hs = clip["width"]["keyframes"], clip["height"]["keyframes"]
        for kx, ky, kw, kh in zip(xs, ys, ws, hs):
            cx, cy = kx["value"] + kw["value"] / 2 - px, ky["value"] + kh["value"] / 2 - py
            kx["value"] = px + cx * c - cy * s - kw["value"] / 2
            ky["value"] = py + cx * s + cy * c - kh["value"] / 2
        if "rotation" in clip:
            for k in clip["rotation"]["keyframes"]:
                k["value"] += deg
        else:
            clip["rotation"] = keys([(0, deg)])


def unturn(pt, pivot, deg):
    """Where a point measured on the turned piece sits before turning by deg about pivot."""
    c, s = math.cos(math.radians(-deg)), math.sin(math.radians(-deg))
    dx, dy = pt[0] - pivot[0], pt[1] - pivot[1]
    return (pivot[0] + dx * c - dy * s, pivot[1] + dx * s + dy * c)


def zoom(p, clips, pivot, k):
    """Scales `clips` (laid out still) by k(frame) about `pivot` (quadrant px), type size and all."""
    px, py = p.X(pivot[0]), p.Y(pivot[1])
    for clip in clips:
        x, y = clip["x"]["keyframes"][0]["value"], clip["y"]["keyframes"][0]["value"]
        w, h = clip["width"]["keyframes"][0]["value"], clip["height"]["keyframes"][0]["value"]
        cx, cy = x + w / 2, y + h / 2
        xs, ys, ws, hs, sizes = [], [], [], [], []
        size = clip.get("textStyle", {}).get("pixelSize")
        for u in frames_of(p.dur):
            kk = k(p.frame(u))
            ncx, ncy = px + (cx - px) * kk, py + (cy - py) * kk
            xs.append((u, ncx - w * kk / 2))
            ys.append((u, ncy - h * kk / 2))
            ws.append((u, w * kk))
            hs.append((u, h * kk))
            sizes.append((u, (size or 0) * kk))
        clip["x"], clip["y"], clip["width"], clip["height"] = keys(xs), keys(ys), keys(ws), keys(hs)
        if size:
            clip["textStyle"]["keyframes"] = {"pixelSize": keys(sizes)}


def new_clips(t, before):
    return [c for tr in t.tracks for c in tr.clips if id(c) not in before]


def seen(t):
    return {id(c) for tr in t.tracks for c in tr.clips}


# --- The sixteen --------------------------------------------------------------------------------------------------


def jacob():
    t, p = piece("jacob", "Tercio azul: caja que se abre con franja blanca", "Blue lower third: opening box, white band",
                 8690, 4.4, (147, 215, 797, 320), ["caja"])
    W = grow(p, (147, 215, 797, 320), "v", 1, frames=18, line=17)
    shape(p, "Caja", WHITE, (147, 215, 797, 289), inside(W, p.R((147, 215, 797, 289))), grad=True)
    shape(p, "Franja", WHITE, (147, 287, 797, 320), inside(W, p.R((147, 287, 797, 320))))
    text(p, "JACOB FOREST", (191, 227, 753, 277), WHITE, "Nombre", align="center", reveal=W)
    text(p, "CREATIVE DIRECTOR", (300, 292, 644, 315), BLUE, "Cargo", align="center", reveal=W)
    return t


def watson():
    t, p = piece("john-watson", "Tercio azul: caja inclinada que se abre", "Blue lower third: slanted opening box",
                 8691, 5.0, (125, 217, 842, 340), ["caja", "inclinado"])
    full = (125, 217, 842, 309)
    shape(p, "Destello", WHITE, full, grow(p, full, "h", 1, frames=20, line=13), skew=-18)
    blue = grow(p, full, "h", 17, frames=22)
    shape(p, "Caja", WHITE, full, blue, grad=True, skew=-18)
    text(p, "JOHN WATSON", (169, 234, 798, 291), WHITE, "Nombre", align="center", reveal=blue)
    text(p, "PROFESSIONAL IT MANAGER", (232, 315, 734, 340), BLUE, "Cargo", align="center",
         reveal=grow(p, (225, 310, 740, 345), "ltr", 38, frames=14, thin=0))
    return t


def titles():
    t, p = piece("titulos", "Tercio azul: caja que baja con franja blanca", "Blue lower third: box down, white band",
                 8692, 6.3, (140, 185, 804, 335), ["caja"])
    shape(p, "Franja", WHITE, (141, 185, 803, 335), grow(p, (141, 185, 803, 335), "ttb", 0, frames=16, line=8))
    blue = grow(p, (140, 185, 804, 318), "ttb", 10, frames=22)
    shape(p, "Caja", WHITE, (140, 185, 804, 318), blue, grad=True)
    text(p, "LOWER THIRDS", (157, 211, 787, 268), WHITE, "Nombre", reveal=blue, shift=rise_from(70, 34))
    text(p, "TITLES", (158, 273, 300, 301), WHITE, "Cargo", reveal=blue, shift=rise_from(45, 40))
    return t


def minimal():
    t, p = piece("minimal", "Tercio azul: caja que se abre desde el centro", "Blue lower third: box from the middle",
                 8693, 6.4, (152, 208, 808, 317), ["caja"])
    full = (152, 208, 808, 286)
    shape(p, "Destello", WHITE, full, grow(p, full, "h", 0, frames=26, line=8))
    blue = grow(p, full, "h", 14, frames=26)
    shape(p, "Caja", WHITE, full, blue, grad=True)
    text(p, "LOWER THIRDS", (165, 219, 795, 275), WHITE, "Nombre", align="center", reveal=blue)
    text(p, "MINIMAL AND CREATIVE", (278, 294, 680, 317), BLUE, "Cargo", align="center",
         reveal=static(p, (260, 290, 700, 318)), anim=per("rise-by-word", 42, 0.2, 0.4, unit="word", rise=1.0, blur=0))
    return t


def rojers():
    t, p = piece("john-rojers", "Tercio azul: nombre girado con caja", "Blue lower third: turned name in a box", 8694,
                 6.3, (262, 171, 666, 388), ["caja", "girado"])
    before = seen(t)
    text(p, "JOHN", (290, 205, 639, 285), WHITE, "Nombre azul", grad=True, reveal=static(p, (270, 190, 660, 286)),
         anim=per("rise-by-word", 5, 0.13, 0.3, rise=1.0, blur=0))
    box = (266, 188.5, 662, 301.5)
    shape(p, "Destello", WHITE, box, grow(p, box, "h", 40, frames=14, line=3, thin=3))
    blue = grow(p, box, "h", 44, frames=16)
    shape(p, "Caja", WHITE, box, blue, grad=True)
    text(p, "JOHN", (290, 205, 639, 285), WHITE, "Nombre", reveal=blue)
    text(p, "ROJERS", (273.6, 310.3, 637.6, 371.9), WHITE, "Apellido", reveal=static(p, (250, 304, 660, 373)),
         shift=rise_from(70, 50, 14))
    turn(p, new_clips(t, before), (464, 245), -5)
    return t


def alexandra():
    t, p = piece("alexandra", "Tercio azul: barra que descubre el nombre", "Blue lower third: bar uncovers the name",
                 8695, 3.5, (124, 227, 832, 335), ["barra", "derecha"])
    bx = lambda fr: 124 + (769 - 124) * E(fr, 6, 16)  # noqa: E731
    bw = lambda fr: 0.0 if fr < 2 else max(3.0, 63 * min(1.0, (fr - 2) / 4))  # noqa: E731
    shape(p, "Barra", WHITE, (769, 227, 832, 335), lambda fr: p.R((bx(fr), 227, bx(fr) + bw(fr), 335)), grad=True)
    shown = lambda fr: p.R((90, 215, bx(fr), 345))  # noqa: E731
    text(p, "ALEXANDRA", (124, 229, 760, 295), WHITE, "Nombre", grad=True, reveal=shown)
    text(p, "CREATIVE DIRECTOR", (342, 307, 761, 334), WHITE, "Cargo", align="right", reveal=shown)
    return t


def your_text():
    t, p = piece("your-text", "Tercio azul: dos líneas que salen de una barra", "Blue lower third: lines out of a bar",
                 8696, 4.0, (228, 180, 686, 366), ["barra", "girado"])
    C, A = (457, 273), -3

    def at(centre, w, h):
        x, y = unturn(centre, C, A)
        return (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
    before = seen(t)
    bar = at((261.5, 285.5), 10, 161)
    shape(p, "Barra", WHITE, bar, grow(p, bar, "v", 0, frames=10))
    side = at((241, 287), 155, 18)
    tag = text(p, "YOUR TEXT", side, BLUE, "Etiqueta", align="center", grad=True,
               anim=per("fade", 0, 0.03, 0.2))
    tag["rotation"] = keys([(0, -90)])
    lower, thirds = at((479.5, 228.5), 402, 76), at((480, 312), 409, 77)
    cut = (bar[2], 150, 760, 400)
    text(p, "LOWER", lower, WHITE, "Nombre", reveal=static(p, cut), shift=slide_from(420, 2, 22))
    text(p, "THIRDS", thirds, WHITE, "Apellido", grad=True, reveal=static(p, cut), shift=slide_from(430, 4, 26))
    turn(p, new_clips(t, before), C, A)
    return t


def general():
    t, p = piece("cajas", "Tercio azul: tres cajas que crecen", "Blue lower third: three growing boxes", 8697, 5.1,
                 (239, 144, 780, 385), ["caja"])
    top, mid, low = (240, 144, 641, 235), (240, 242, 641, 333), (239, 341, 780, 385)
    shape(p, "Destello", WHITE, top, grow(p, top, "ltr", 0, frames=24, line=10, thin=3))
    w1 = grow(p, top, "ltr", 14, frames=24)
    shape(p, "Caja", WHITE, top, w1, grad=True)
    shape(p, "Destello 2", WHITE, mid, grow(p, mid, "ltr", 3, frames=26, line=11, thin=3), grad=True)
    w2 = grow(p, mid, "ltr", 20, frames=24)
    shape(p, "Caja 2", WHITE, mid, w2)
    w3 = grow(p, low, "ltr", 16, frames=36)
    shape(p, "Ficha", WHITE, low, w3, grad=True)
    text(p, "LOWER", (251, 155, 628, 225), WHITE, "Nombre", reveal=w1, shift=slide_from(120, 14, 24))
    text(p, "THIRDS", (248, 252, 632, 322), WHITE, "Apellido", grad=True, reveal=w2, shift=slide_from(120, 20, 24))
    text(p, "General Creative Director", (245, 347, 765, 379), WHITE, "Cargo", reveal=w3)
    return t


def corni():
    t, p = piece("corni", "Tercio azul: nombre en caja y cargo en ficha blanca", "Blue lower third: name box, white tag",
                 8698, 4.7, (150, 219, 794, 329), ["caja"])
    name, tag = (150, 263, 794, 329), (151, 219, 519, 257)
    shape(p, "Destello", WHITE, name, grow(p, name, "ltr", 0, frames=24, line=10, thin=3))
    w1 = grow(p, name, "ltr", 14, frames=26)
    shape(p, "Caja", WHITE, name, w1, grad=True)
    shape(p, "Destello 2", WHITE, tag, grow(p, tag, "rtl", 6, frames=24, line=10, thin=3), grad=True)
    w2 = grow(p, tag, "rtl", 20, frames=24)
    shape(p, "Ficha", WHITE, tag, w2)
    text(p, "CORNI CERPSOM", (161, 270, 784, 321), WHITE, "Nombre", reveal=w1)
    text(p, "MOTION DESIGNER", (158, 225, 512, 251), WHITE, "Cargo", grad=True, reveal=w2)
    return t


def marketing():
    t, p = piece("marketing", "Tercio azul: letras que aparecen y barra", "Blue lower third: letters fade in, bar",
                 8699, 6.2, (154, 229, 806, 329), ["barra"])
    bar = (154, 293, 806, 329)
    shape(p, "Destello", WHITE, bar, grow(p, bar, "h", 6, frames=22, line=4, thin=3))
    shape(p, "Barra", WHITE, bar, grow(p, bar, "h", 12, frames=24), grad=True)
    text(p, "LOWER THIRDS", (154, 229, 805, 286), WHITE, "Nombre", align="center",
         anim=per("fade-up-char", 4, 0.1, 0.3))
    text(p, "CREATIVE MARKETING DESIGNER", (180, 299, 778, 324), WHITE, "Cargo", align="center",
         anim=per("fade", 40, 0.05, 0.25))
    return t


def rosanda():
    t, p = piece("rosanda", "Tercio azul: barra que barre un nombre girado", "Blue lower third: bar sweeps a turned name",
                 8700, 3.6, (134, 189, 832, 352), ["barra", "girado"])
    bx = lambda fr: 955 + (134 - 955) * E(fr, 7, 20)  # noqa: E731
    bw = lambda fr: 0.0 if fr < 3 else (2.0 if fr < 6 else 21.0)  # noqa: E731
    shape(p, "Barra", WHITE, (134, 237, 155, 352), lambda fr: p.R((bx(fr), 237, bx(fr) + bw(fr), 352)), grad=True)
    shown = lambda fr: p.R((bx(fr) + bw(fr), 150, 1000, 380))  # noqa: E731
    for content, centre, w, caps, colour, grad, nm in (
            ("ROSANDA SMITH", (498, 243.5), 671, 50, WHITE, False, "Nombre"),
            ("CONTENT CREATOR", (360, 309.5), 391, 24, WHITE, True, "Cargo")):
        ink = (centre[0] - w / 2, centre[1] - caps / 2, centre[0] + w / 2, centre[1] + caps / 2)
        clip = text(p, content, ink, colour, nm, align="center", grad=grad, reveal=shown)
        turn(p, [clip], centre, -5.3)
    return t


def brackets():
    t, p = piece("corchetes", "Tercio azul: dos barras que se abren", "Blue lower third: two bars open apart", 8701,
                 6.6, (130, 197, 838, 303), ["barra"])
    lx = lambda fr: 462 + (130 - 462) * OPEN(fr)  # noqa: E731
    rx = lambda fr: 486 + (818 - 486) * OPEN(fr)  # noqa: E731

    def left(fr):
        k = E(fr, 0, 28) if fr >= 0 else 0
        return p.R((lx(fr), 197, lx(fr) + 20, 197 + 106 * max(0.03, k)))

    def right(fr):
        k = E(fr, 3, 28) if fr >= 3 else 0.03
        return p.R((rx(fr), 303 - 106 * max(0.03, k), rx(fr) + 20, 303))
    shape(p, "Barra", WHITE, (130, 197, 150, 303), left, grad=True)
    shape(p, "Barra 2", WHITE, (818, 197, 838, 303), right, grad=True)
    shown = lambda fr: p.R((lx(fr) + 20, 190, rx(fr), 310))  # noqa: E731
    text(p, "LOWER THIRDS", (158, 205, 810, 263), WHITE, "Nombre", align="center", grad=True, reveal=shown)
    text(p, "MOTION DESIGNER", (283, 269, 684, 299), WHITE, "Cargo", align="center", reveal=shown)
    return t


def modern():
    t, p = piece("modern", "Tercio azul: dos líneas que suben y subrayado", "Blue lower third: two rising lines, underline",
                 8702, 6.1, (93, 229, 854, 348), ["subrayado"])
    line = (96, 337, 474, 348)
    shape(p, "Subrayado", WHITE, line, grow(p, line, "h", 8, frames=24, thin=8), grad=True)
    text(p, "MODERN DESIGN", (93, 229, 704, 279), WHITE, "Nombre", grad=True, reveal=static(p, (80, 200, 870, 280)),
         shift=rise_from(55, 8))
    text(p, "TYPOGRAPHY TITLES", (94, 283, 854, 333), WHITE, "Cargo", reveal=static(p, (80, 281, 870, 334)),
         shift=rise_from(55, 11))
    return t


def jeremy():
    t, p = piece("jeremy", "Tercio azul: nombre en dos líneas y subrayado", "Blue lower third: two-line name, underline",
                 8703, 6.2, (233, 187, 724, 389), ["subrayado"])
    text(p, "JEREMY", (233, 187, 671, 259), WHITE, "Nombre", grad=True, reveal=static(p, (220, 150, 740, 260)),
         shift=rise_from(80, 5, 18))
    text(p, "WATSON", (240, 265, 724, 339), WHITE, "Apellido", grad=True, reveal=static(p, (220, 262, 740, 340)),
         shift=rise_from(80, 11, 18))
    line = (250, 343, 556, 351)
    shape(p, "Destello", WHITE, line, grow(p, line, "ltr", 30, frames=26, thin=0))
    shape(p, "Subrayado", WHITE, line, grow(p, line, "ltr", 38, frames=26, thin=0), grad=True)
    text(p, "DIRECTOR", (251, 356, 492, 389), WHITE, "Cargo", anim=per("fade", 30, 0.12, 0.3))
    return t


def jeremi():
    t, p = piece("jeremi", "Tercio azul: línea que baja y descubre el nombre", "Blue lower third: line slides down, name",
                 8704, 5.9, (167, 206, 797, 316), ["subrayado"])
    ly = lambda fr: 206 + (282 - 206) * E(fr, 10, 12)  # noqa: E731

    def line(fr):
        k = E(fr, 0, 6)
        cx, half = (171 + 797) / 2, (797 - 171) / 2 * k
        return p.R((cx - half, ly(fr), cx + half, ly(fr) + 10))
    shape(p, "Línea", WHITE, (171, 282, 797, 292), line)
    text(p, "JEREMI SMITH", (167, 215, 794, 275), WHITE, "Nombre", grad=True,
         reveal=lambda fr: p.R((150, 150, 810, ly(fr))))
    text(p, "SUCCESSFUL ENGINEER", (170, 298, 470, 316), WHITE, "Cargo", anim=per("fade", 13, 0.06, 0.3))
    return t


def suzanna():
    t, p = piece("suzanna", "Tercio azul: letras que aparecen y se acercan", "Blue lower third: letters fade in, zoom",
                 8705, 6.0, (158, 163, 756, 353), ["derecha"])
    before = seen(t)
    text(p, "SHARP", (459, 163, 756, 222), WHITE, "Nombre", align="right", anim=per("fade", 0, 0.1, 0.4))
    text(p, "SUZANNA", (158, 227, 723, 305), WHITE, "Apellido", grad=True, anim=per("fade", 27, 0.12, 0.4))
    text(p, "ACCOUNTANT", (346, 313, 718, 353), WHITE, "Cargo", align="right", anim=per("fade", 27, 0.1, 0.4))
    zoom(p, new_clips(t, before), (179, 346), table({0: 0.535, 30: 0.76, 45: 0.86, 51: 0.95, 60: 1.0}))
    return t


TEMPLATES = [jacob, watson, titles, minimal, rojers, alexandra, your_text, general, corni, marketing, rosanda,
             brackets, modern, jeremy, jeremi, suzanna]
