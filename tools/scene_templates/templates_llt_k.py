"""Gradient lower thirds, eleventh set (2026-11-07, moves redone 2026-11-08): the twenty of 65200053.mp4 (1920×1080
at 60 fps), Montserrat (Bold capitals, light italic first names) with a pink-to-blue gradient on boxes, bars, frames
and some names; four with a photo slot. The reference shows each one in the middle of the frame: here at the same
size, moved to the bottom left (left 120, bottom 960), with no background. Order 8670-8689.

The moves, studied frame by frame (2026-11-08, Jorge: the start and the end of the whole series):
- a box is born as a thin white line, then opens with a white panel in front of the gradient; a white sliver stays
  on its leading edge for a moment;
- underlines, bars and frames draw with a white head ahead of the gradient; a frame starts at a corner and runs
  round both ways;
- names rise from under a line, slide out from behind a box or bar, or fade in; text inside a box shows as the box
  opens;
- a photo slot first opens as a gradient square, then a white band runs across it and leaves the photo behind;
- each piece lasts what it lasts in the reference (2.2-3.2 s) and leaves with its entrance played backwards.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of, mask_track
from scene import gradient, keys, no_stroke
from templates_llt_f import Piece, table

for w, file in ((400, "Montserrat-Italic"), (700, "Montserrat-Bold")):
    f6._FILES[("Montserrat", w)] = f"fonts.basic/fonts/montserrat/{file}.ttf"
FONT = "Montserrat"
WHITE = "#FFFFFF"
PINK, BLUE = "#E8457A", "#2B2BD8"
PB = [gradient([(0.0, PINK), (1.0, BLUE)], angle=0), no_stroke()]  # pink on the left
BP = [gradient([(0.0, BLUE), (1.0, PINK)], angle=0), no_stroke()]  # blue on the left
VPB = [gradient([(0.0, PINK), (1.0, BLUE)], angle=90), no_stroke()]  # pink on top
SOLID_PINK = [gradient([(0.0, PINK), (1.0, PINK)], angle=0), no_stroke()]
SOLID_BLUE = [gradient([(0.0, BLUE), (1.0, BLUE)], angle=0), no_stroke()]
FPS = 30.0
EASE = table({0: 0.0, 2: 0.22, 4: 0.48, 6: 0.68, 8: 0.82, 10: 0.91, 12: 0.96, 14: 0.99, 16: 1.0})
D = 3.2
HIDE = (-4000.0, -4000.0, -4000.0, -4000.0)


def ease(fr, at, speed):
    """0 → 1 from frame `at` over `speed` frames."""
    return EASE((fr - at) * 16 / speed)


class GradPiece(Piece):
    """A piece laid out in reference px, moved by (dx, dy) so its box lands bottom left."""

    def __init__(self, t, dur, dx, dy):
        super().__init__(t, dur, 0)
        self.dx, self.dy = dx, dy

    def frame(self, u):
        return min(u, self.dur - u) * FPS


class StepPiece(GradPiece):
    """A piece whose words enter and leave one by one in the same order (first in, first out): its frame is the
    plain frame count, and each word works out its own entrance and exit."""

    def frame(self, u):
        return u * FPS


def _kit(id, es, en, order, tags, dur=D):
    return wide(f"llt11-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:lowerthirds", "tercio", "degradado"] + tags, thumb_at=round(min(1.6, dur / 2), 1))


def _rect(p, r):
    return (r[0] + p.dx, r[1] + p.dy, r[2] + p.dx, r[3] + p.dy)


def _seg(r, way, a, b):
    """The part of rect r between fractions a..b along `way` (ltr, rtl, ttb, btt)."""
    x0, y0, x1, y1 = r
    w, h = x1 - x0, y1 - y0
    if way == "ltr":
        return (x0 + w * a, y0, x0 + w * b, y1)
    if way == "rtl":
        return (x1 - w * b, y0, x1 - w * a, y1)
    if way == "ttb":
        return (x0, y0 + h * a, x1, y0 + h * b)
    return (x0, y1 - h * b, x1, y1 - h * a)


def _shape(p, name, r, rect, layers):
    clip = p.shape(name, PINK, r, lambda fr: (lambda q: q if q[2] - q[0] > 0.05 and q[3] - q[1] > 0.05
                                              else (r[0], r[1], r[0] + 0.01, r[1] + 0.01))(rect(fr)))
    clip["shapeStyle"]["layers"] = layers
    return clip


def wipe(p, name, r, at, way="ltr", layers=PB, line=True, speed=10, lag=4, sliver=6.0, cut=None):
    """A box (or a bar with line=False) that opens along `way` from frame `at`: a box is first a thin white line
    across its starting side (4 frames), then a white panel runs ahead of the gradient, leaving a sliver on the edge
    for a moment. Returns edge(frame) = the screen rect of the gradient so far (text inside shows there)."""
    full = _rect(p, r)
    x0, y0, x1, y1 = full
    across = way in ("ltr", "rtl")
    span = (x1 - x0) if across else (y1 - y0)
    t0 = at + (4 if line else 0)
    lead = lambda fr: ease(fr, t0, speed)  # noqa: E731
    body = lambda fr: ease(fr, t0 + lag, speed)  # noqa: E731
    th = min(0.5, sliver / max(span, 1.0))

    def white(fr):
        if fr < t0:
            if not line or fr < at:
                return HIDE
            g = ease(fr, at, 4)
            if across:
                xo = x0 if way == "ltr" else x1 - 4
                cy, hh = (y0 + y1) / 2, (y1 - y0) / 2 * g
                return (xo, cy - hh, xo + 4, cy + hh)
            yo = y0 if way == "ttb" else y1 - 4
            cx, hw = (x0 + x1) / 2, (x1 - x0) / 2 * g
            return (cx - hw, yo, cx + hw, yo + 4)
        a, b = body(fr), lead(fr)
        if b - a < th:
            if fr > t0 + lag + speed + 4:
                return HIDE
            a = max(0.0, b - th)
        return _seg(full, way, a, b)

    def grad(fr):
        # cut(frame) = how much of it, from its start, something on top has already taken (a photo).
        c = cut(fr) if cut else 0.0
        return _seg(full, way, c, body(fr)) if fr >= t0 and body(fr) > c else HIDE
    _shape(p, name, full, grad, layers)
    _shape(p, f"{name} (brillo)", full, white, [gradient([(0.0, WHITE), (1.0, WHITE)], angle=0), no_stroke()])
    return grad


def frame(p, r, at=0, w=6, start="top", speed=8):
    """A gradient frame drawn with a white head from a corner: from the top left along the top, down the right
    and back along the bottom while the left side comes down (start="top"), or from the top left down the left
    side and along the bottom first (start="left")."""
    x0, y0, x1, y1 = r
    top, bottom = (x0, y0, x1, y0 + w), (x0, y1 - w, x1, y1)
    left, right = (x0, y0, x0 + w, y1), (x1 - w, y0, x1, y1)
    kw = dict(line=False, speed=speed, lag=3)
    if start == "top":
        wipe(p, "Marco", top, at, "ltr", PB, **kw)
        wipe(p, "Marco 2", right, at + 5, "ttb", SOLID_BLUE, **kw)
        wipe(p, "Marco 3", bottom, at + 8, "rtl", PB, **kw)
        wipe(p, "Marco 4", left, at + 7, "ttb", SOLID_PINK, **kw)
    else:
        wipe(p, "Marco", left, at, "ttb", SOLID_PINK, **kw)
        wipe(p, "Marco 2", bottom, at + 4, "ltr", PB, **kw)
        wipe(p, "Marco 3", right, at + 8, "btt", SOLID_BLUE, **kw)
        wipe(p, "Marco 4", top, at + 6, "ltr", PB, **kw)


def words(p, x0, y0, x1, y1, parts, at=0, name="Nombre", align="left", how="up", speed=8, stagger=0, fade=False,
          edge=None, inside=None, steps=None, dist=None):
    """A line made of words [(text, weight, italic, fill)] side by side with a word space between, sized so the
    whole line spans x0..x1 (its capitals centred on y0..y1); fill is a colour or "grad". From frame `at` (each
    next word `stagger` frames later) it comes in as `how`:
    - "up": rises from under its own line;
    - "left" / "right": slides out from behind a box or bar whose edge is at x = edge (reference px), from that
      side;
    - "fade": fades in where it stands (also with fade=True on the others);
    - "box": shows as the box it sits in opens (inside = that box's edge function, from wipe()).
    steps = [(in, out)] per word plays first in, first out (StepPiece only)."""
    ems = []
    for text, weight, italic, _ in parts:
        f = f6._font(FONT, weight)
        bb = f.getbbox(text.upper())
        ems.append((bb[2] - bb[0]) / 400)
    space = 0.26
    size = (x1 - x0) / (sum(ems) + space * (len(parts) - 1))
    cy = (y0 + y1) / 2
    ct, cb = cy - 0.35 * size, cy + 0.35 * size
    x = x0
    rx0, ry0, rx1, ry1 = _rect(p, (x0, y0, x1, y1))
    end = p.dur * FPS
    dist = dist if dist is not None else (x1 - x0) + 40

    def k_of(i):
        if steps is not None:
            a_in, a_out = steps[i]
            return lambda fr: min(ease(fr, a_in, speed), ease(end - a_out - fr, 0, speed))
        a = at + i * stagger
        return lambda fr: ease(fr, a, speed)
    for i, ((text, weight, italic, fill), em) in enumerate(zip(parts, ems)):
        k = k_of(i)
        shift, reveal = None, None
        if how == "up":
            # Far enough down to clear the reveal box (its bottom is 12 px under the line).
            shift = (lambda k: lambda fr: (0.0, (1 - k(fr)) * ((y1 - y0) + 26)))(k)
            reveal = lambda fr: (rx0 - 60, ry0 - 400, rx1 + 80, ry1 + 12)  # noqa: E731
        elif how in ("left", "right"):
            sign = -1 if how == "left" else 1
            shift = (lambda k, s: lambda fr: (s * (1 - k(fr)) * dist, 0.0))(k, sign)
            ex = edge + p.dx
            reveal = (lambda e: lambda fr: (e, -4000.0, 8000.0, 8000.0))(ex) if how == "left" else \
                (lambda e: lambda fr: (-4000.0, -4000.0, e, 8000.0))(ex)
        elif how == "box":
            reveal = (lambda fr: (lambda g: (g[0] - 4, ry0 - 30, g[2], ry1 + 30) if g != HIDE else HIDE)(inside(fr)))
        w = em * size
        clip = p.text(text, x + p.dx, ct + p.dy, cb + p.dy, w, FONT, weight, WHITE if fill == "grad" else fill,
                      name if i == 0 else f"{name} {i + 1}", shift=shift, reveal=reveal)
        if italic:
            clip["textStyle"]["italic"] = True
        if fill == "grad":
            clip["textStyle"]["layers"] = [gradient([(0.0, PINK), (1.0, BLUE)], angle=0)]
        if how == "fade" or fade:
            clip["opacity"] = keys([(u, round(k(p.frame(u)), 4), "linear") for u in frames_of(p.dur)])
        x += w + space * size


def photo(p, r, at=0, show=18, way="ttb", layers=PB):
    """The photo slot: a gradient square opens over it (a box, from `at`), then from `show` a white band runs
    across and leaves the photo behind it (a mask: scaling a still would stretch its decode)."""
    full = _rect(p, r)
    x0, y0, x1, y1 = full
    b = Box(x0, y0, x1 - x0, y1 - y0)
    clip = p.t.photo(p.t.track("video", "Foto"), "man-04", 0.0, p.dur, b, None, label="Tu foto")
    shown = lambda fr: ease(fr, show, 10)  # noqa: E731
    mask_track(p.t, clip, b, lambda u: _seg(full, way, 0.0, max(0.002, shown(p.frame(u)))), p.dur)
    band = 0.3
    # The square keeps only the part ahead of the white band; the photo under it shows behind the band.
    grad = wipe(p, "Cuadro", r, at, way, layers, cut=lambda fr: min(1.0, shown(fr) + band) if shown(fr) > 0.001 else 0.0)
    _shape(p, "Cuadro (barrido)", full,
           lambda fr: _seg(full, way, shown(fr), min(1.0, shown(fr) + band)) if 0.001 < shown(fr) < 0.999 else HIDE,
           [gradient([(0.0, WHITE), (1.0, WHITE)], angle=0), no_stroke()])
    return grad


def piece(id, es, en, order, bounds, dur, tags=()):
    t = _kit(id, es, en, order, list(tags), dur=dur)
    x0, _, _, y1 = bounds
    return t, GradPiece(t, dur, 120 - x0, 960 - y1)


def p1():
    t, p = piece("1", "Tercio degradado: apellido en degradado y ficha", "Gradient lower third: gradient last name, tag",
                 8670, (510, 361, 1410, 720), 2.8)
    edge = wipe(p, "Ficha", (510, 618, 1410, 720), 0, "ltr", BP)
    words(p, 542, 652, 1040, 685, [("Television reporter", 700, False, WHITE)], 7, "Cargo", how="box", inside=edge)
    words(p, 512, 364, 896, 452, [("Aleix", 400, True, WHITE)], 3, how="fade", speed=10)
    words(p, 510, 492, 1410, 587, [("Richardson", 700, False, "grad")], 5, "Apellido", how="left", edge=-2000, dist=60,
          fade=True, speed=10)
    return t


def p2():
    t, p = piece("2", "Tercio degradado: subrayado", "Gradient lower third: underline", 8671, (449, 449, 1468, 658), 2.47)
    wipe(p, "Subrayado", (449, 573, 1142, 591), 0, "rtl", PB, line=False, speed=14, lag=3)
    words(p, 450, 452, 1468, 545, [("Aleix", 700, False, WHITE), ("Richard", 700, False, WHITE)], 5)
    words(p, 450, 626, 948, 658, [("Television reporter", 700, False, WHITE)], 1, "Cargo", how="fade", speed=12)
    return t


def p3():
    t, p = piece("3", "Tercio degradado: caja con el cargo a la derecha", "Gradient lower third: role box on the right",
                 8672, (420, 432, 1500, 648), 2.87)
    edge = wipe(p, "Caja", (1060, 432, 1500, 648), 0, "ltr", PB)
    words(p, 1100, 462, 1290, 486, [("Live", 700, False, WHITE)], 9, "Cargo", how="box", inside=edge, fade=True)
    words(p, 1100, 502, 1290, 526, [("Television", 700, False, WHITE)], 10, "Cargo 2", how="box", inside=edge,
          fade=True)
    words(p, 1100, 542, 1290, 566, [("Reporter", 700, False, WHITE)], 11, "Cargo 3", how="box", inside=edge,
          fade=True)
    # The name slides out to the left from behind the box.
    words(p, 640, 434, 1020, 528, [("Aleix", 700, False, WHITE)], 13, how="right", edge=1060, speed=12)
    words(p, 425, 552, 1020, 646, [("Richard", 700, False, WHITE)], 11, "Apellido", how="right", edge=1060, speed=12)
    return t


def p4():
    t, p = piece("4", "Tercio degradado: marco y ficha", "Gradient lower third: frame and tag", 8673,
                 (360, 372, 1560, 692), 3.03)
    frame(p, (360, 372, 1560, 652), 0)
    edge = wipe(p, "Ficha", (460, 600, 1128, 692), 3, "ltr", BP)
    words(p, 499, 632, 997, 664, [("Television reporter", 700, False, WHITE)], 9, "Cargo", how="box", inside=edge)
    words(p, 463, 460, 1481, 558, [("Aleix", 700, False, WHITE), ("Richard", 700, False, WHITE)], 15)
    return t


def p5():
    t, p = piece("5", "Tercio degradado: barra vertical", "Gradient lower third: upright bar", 8674,
                 (424, 432, 1496, 648), 2.7)
    wipe(p, "Barra", (424, 432, 454, 648), 0, "ttb", VPB, line=False, speed=10, lag=3)
    words(p, 479, 590, 977, 622, [("Television reporter", 700, False, WHITE)], 5, "Cargo", how="left", edge=456,
          speed=12)
    words(p, 479, 462, 1496, 560, [("Aleix", 700, False, WHITE), ("Richard", 700, False, WHITE)], 13)
    return t


def p6():
    t, p = piece("6", "Tercio degradado: nombre en una línea y ficha", "Gradient lower third: one-line name, tag",
                 8675, (306, 442, 1608, 678), 3.07)
    edge = wipe(p, "Ficha", (306, 576, 1206, 678), 0, "ltr", BP)
    words(p, 337, 613, 835, 645, [("Television reporter", 700, False, WHITE)], 7, "Cargo", how="box", inside=edge,
          fade=True)
    words(p, 308, 444, 1608, 538, [("Aleix", 400, True, WHITE), ("Richardson", 700, False, WHITE)], 17, stagger=2)
    return t


def p7():
    t, p = piece("7", "Tercio degradado: nombre en caja y cargo en marco", "Gradient lower third: name box, role frame",
                 8676, (399, 388, 1516, 698), 3.17)
    edge = wipe(p, "Caja", (399, 388, 1516, 584), 0, "ltr", PB)
    words(p, 448, 434, 1466, 532, [("Aleix", 700, False, WHITE), ("Richard", 700, False, WHITE)], 7, how="box",
          inside=edge, fade=True, speed=10)
    frame(p, (399, 600, 1090, 698), 1, w=5, start="left")
    words(p, 436, 626, 934, 659, [("Television reporter", 700, False, WHITE)], 21, "Cargo")
    return t


def p8():
    # Measured at 30 fps: each word rises in 7 frames, Aleix first, Richard 3 frames later, the role's two words 6
    # and 7 later; they drop out in the same order (Aleix and Television first, Richard last).
    # The reference shows it for 2.2 s (from the first letter in to the last out), shorter than the rest.
    t = _kit("8", "Tercio degradado: apellido en degradado", "Gradient lower third: gradient last name", 8677, [],
             dur=2.2)
    p = StepPiece(t, 2.2, 120 - 453, 960 - 627)
    words(p, 454, 457, 1472, 550, [("Aleix", 400, True, WHITE), ("Richard", 700, False, "grad")],
          steps=[(0, 4), (3, 0)], speed=7)
    words(p, 453, 594, 951, 627, [("Television", 700, False, WHITE), ("reporter", 700, False, WHITE)], name="Cargo",
          steps=[(6, 4), (7, 3)], speed=7)
    return t


def p9():
    t, p = piece("9", "Tercio degradado: ficha arriba y marco", "Gradient lower third: tag above, frame", 8678,
                 (380, 362, 1548, 720), 3.1)
    frame(p, (380, 460, 1548, 720), 0)
    edge = wipe(p, "Ficha", (380, 364, 1072, 452), 5, "ltr", PB)
    words(p, 412, 394, 910, 427, [("Television reporter", 700, False, WHITE)], 9, "Cargo", how="box", inside=edge)
    words(p, 448, 542, 1466, 636, [("Aleix", 700, False, WHITE), ("Richard", 700, False, WHITE)], 13)
    return t


def p10():
    t, p = piece("10", "Tercio degradado: apellido en caja y subrayado", "Gradient lower third: last name box, underline",
                 8679, (510, 432, 1410, 652), 2.8)
    wipe(p, "Subrayado", (510, 568, 1410, 586), 0, "ltr", BP, line=False, speed=14, lag=3)
    words(p, 516, 442, 892, 536, [("Aleix", 700, False, WHITE)], 3, how="fade")
    edge = wipe(p, "Caja", (920, 432, 1408, 540), 1, "ltr", PB)
    words(p, 940, 468, 1390, 508, [("Richardson", 400, True, WHITE)], 11, "Apellido", how="box", inside=edge,
          fade=True)
    words(p, 511, 620, 1009, 652, [("Television reporter", 700, False, WHITE)], 15, "Cargo")
    return t


def p11():
    t, p = piece("11", "Tercio degradado: barra alta y apellido en caja", "Gradient lower third: tall bar, last name box",
                 8680, (453, 333, 1472, 748), 3.13)
    wipe(p, "Barra", (453, 333, 483, 748), 0, "ttb", VPB, line=False, speed=10, lag=3)
    edge = wipe(p, "Caja", (514, 486, 1472, 665), 1, "ltr", BP)
    words(p, 550, 528, 1434, 623, [("Richardson", 700, False, WHITE)], 9, "Apellido", how="box", inside=edge)
    words(p, 514, 370, 898, 460, [("Aleix", 400, True, WHITE)], 19)
    words(p, 514, 696, 1012, 728, [("Television reporter", 700, False, WHITE)], 19, "Cargo")
    return t


def p12():
    t, p = piece("12", "Tercio degradado: ficha arriba, marco y apellido en degradado",
                 "Gradient lower third: tag, frame, gradient last name", 8681, (380, 372, 1540, 712), 2.9)
    frame(p, (380, 468, 1540, 712), 0)
    edge = wipe(p, "Ficha", (380, 372, 1060, 460), 5, "ltr", PB)
    words(p, 406, 401, 904, 430, [("Television reporter", 700, False, WHITE)], 9, "Cargo", how="box", inside=edge)
    words(p, 449, 547, 1464, 638, [("Aleix", 400, True, WHITE), ("Richard", 700, False, "grad")], 13, stagger=2)
    return t


def p13():
    t, p = piece("13", "Tercio degradado: etiqueta y cuadro", "Gradient lower third: tag and square", 8682,
                 (574, 426, 1342, 642), 2.67)
    edge = wipe(p, "Etiqueta", (978, 426, 1342, 522), 0, "ltr", PB)
    words(p, 1000, 458, 1320, 490, [("TV Reporter", 700, False, WHITE)], 7, "Cargo", how="box", inside=edge)
    words(p, 574, 429, 960, 519, [("Aleix", 700, False, WHITE)], 1)
    wipe(p, "Cuadro", (574, 546, 722, 642), 5, "ltr", PB)
    words(p, 749, 546, 1342, 640, [("Richard", 700, False, WHITE)], 3, "Apellido")
    return t


def p14():
    t, p = piece("14", "Tercio degradado: subrayado y cargo a la derecha", "Gradient lower third: underline, role right",
                 8683, (452, 477, 1464, 625), 2.47)
    wipe(p, "Subrayado", (452, 602, 926, 620), 0, "ltr", PB, line=False, speed=14, lag=3)
    words(p, 454, 479, 1464, 569, [("Aleix", 400, True, WHITE), ("Richard", 700, False, "grad")], 5, stagger=2)
    words(p, 955, 593, 1453, 625, [("Television reporter", 700, False, WHITE)], 3, "Cargo", how="fade", speed=12)
    return t


def p15():
    t, p = piece("15", "Tercio degradado: cuadros y ficha", "Gradient lower third: squares and tag", 8684,
                 (572, 390, 1344, 726), 2.83)
    edge = wipe(p, "Ficha", (572, 630, 1343, 726), 0, "ltr", BP)
    words(p, 604, 663, 903, 695, [("TV Reporter", 700, False, WHITE)], 7, "Cargo", how="box", inside=edge)
    wipe(p, "Caja", (992, 390, 1344, 486), 5, "ltr", BP)
    wipe(p, "Cuadro", (572, 510, 722, 606), 9, "ltr", PB)
    words(p, 575, 394, 958, 484, [("Aleix", 400, True, WHITE)], 15)
    words(p, 749, 512, 1342, 606, [("Richard", 700, False, WHITE)], 17, "Apellido")
    return t


def p16():
    t, p = piece("16", "Tercio degradado con foto: apellido en degradado", "Gradient lower third with photo", 8685,
                 (300, 404, 1624, 676), 2.97, ["foto"])
    photo(p, (300, 404, 568, 676), 0, 21, "ttb")
    words(p, 608, 451, 1624, 541, [("Aleix", 400, True, WHITE), ("Richard", 700, False, "grad")], 13, stagger=2)
    words(p, 607, 598, 1105, 630, [("Television reporter", 700, False, WHITE)], 19, "Cargo")
    return t


def p17():
    t, p = piece("17", "Tercio degradado con foto: nombre en dos líneas y ficha", "Gradient lower third with photo, tag",
                 8686, (520, 368, 1394, 738), 2.87, ["foto"])
    photo(p, (520, 388, 752, 616), 0, 19, "ltr")
    edge = wipe(p, "Ficha", (526, 636, 1394, 738), 5, "ltr", BP)
    words(p, 556, 672, 1054, 704, [("Television reporter", 700, False, WHITE)], 11, "Cargo", how="box", inside=edge)
    words(p, 790, 370, 1167, 460, [("Aleix", 700, False, WHITE)], 11)
    words(p, 797, 499, 1390, 593, [("Richard", 700, False, WHITE)], 13, "Apellido")
    return t


def p18():
    t, p = piece("18", "Tercio degradado con foto y barra", "Gradient lower third with photo and bar", 8687,
                 (472, 388, 1446, 690), 3.0, ["foto"])
    photo(p, (472, 388, 768, 688), 0, 19, "ttb")
    wipe(p, "Barra", (800, 390, 818, 690), 3, "ttb", VPB, line=False, speed=10, lag=3)
    words(p, 846, 393, 1223, 483, [("Aleix", 700, False, WHITE)], 9)
    words(p, 854, 511, 1446, 605, [("Richard", 700, False, WHITE)], 11, "Apellido")
    words(p, 846, 647, 1344, 679, [("Television reporter", 700, False, WHITE)], 15, "Cargo")
    return t


def p19():
    t, p = piece("19", "Tercio degradado con foto en marco", "Gradient lower third with photo in a frame", 8688,
                 (248, 396, 1660, 684), 2.97, ["foto"])
    frame(p, (248, 396, 1660, 684), 0)
    photo(p, (248, 400, 532, 676), 1, 19, "ltr")
    words(p, 583, 458, 1601, 552, [("Aleix", 700, False, WHITE), ("Richard", 700, False, WHITE)], 13)
    words(p, 583, 586, 1081, 618, [("Television reporter", 700, False, WHITE)], 15, "Cargo", how="fade", speed=10)
    return t


def p20():
    t, p = piece("20", "Tercio degradado con foto, marco y ficha", "Gradient lower third with photo, frame and tag",
                 8689, (300, 386, 1616, 692), 2.97, ["foto"])
    photo(p, (300, 386, 504, 590), 1, 19, "ltr")
    frame(p, (502, 386, 1616, 590), 0)
    words(p, 542, 438, 1558, 532, [("Aleix", 400, True, WHITE), ("Richard", 700, False, WHITE)], 15, stagger=2)
    edge = wipe(p, "Ficha", (300, 600, 976, 692), 13, "ltr", BP)
    words(p, 331, 626, 829, 658, [("Television reporter", 700, False, WHITE)], 17, "Cargo", how="box", inside=edge)
    return t


TEMPLATES = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20]
