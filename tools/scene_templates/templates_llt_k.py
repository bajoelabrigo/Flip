"""Gradient lower thirds, eleventh set (2026-11-07): the twenty of 65200053.mp4 (1920×1080 at 60 fps), Montserrat
(Bold capitals, light italic first names) with a pink-to-blue gradient on boxes, bars, frames and some names; four
with a photo slot. The reference shows each one in the middle of the frame: here at the same size, moved to the
bottom left (left 120, bottom 960), with no background. Shared moves (boxes and bars grow, frames draw, names and
roles slide up into place, photos open), the entrance played backwards to leave. Order 8670-8689.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from scene import gradient, no_stroke
from templates_llt_f import Piece, fit, table

for w, file in ((400, "Montserrat-Italic"), (700, "Montserrat-Bold")):
    f6._FILES[("Montserrat", w)] = f"fonts.basic/fonts/montserrat/{file}.ttf"
FONT = "Montserrat"
WHITE = "#FFFFFF"
PINK, BLUE = "#E8457A", "#2B2BD8"
GRAD = [gradient([(0.0, PINK), (1.0, BLUE)], angle=0), no_stroke()]
FPS = 30.0
EASE = table({0: 0.0, 2: 0.22, 4: 0.48, 6: 0.68, 8: 0.82, 10: 0.91, 12: 0.96, 14: 0.99, 16: 1.0})
D = 3.2


class GradPiece(Piece):
    """A piece laid out in reference px, moved by (dx, dy) so its box lands bottom left."""

    def __init__(self, t, dur, dx, dy):
        super().__init__(t, dur, 0)
        self.dx, self.dy = dx, dy

    def frame(self, u):
        return min(u, self.dur - u) * FPS


def _kit(id, es, en, order, tags, dur=D):
    return wide(f"llt11-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:lowerthirds", "tercio", "degradado"] + tags, thumb_at=round(min(1.6, dur / 2), 1))


def _rect(p, r):
    return (r[0] + p.dx, r[1] + p.dy, r[2] + p.dx, r[3] + p.dy)


def box(p, name, r, grows="ltr", at=0, layers=None, colour=PINK):
    x0, y0, x1, y1 = _rect(p, r)

    def rr(fr):
        k = EASE(fr - at)
        if grows == "ltr":
            return (x0, y0, x0 + (x1 - x0) * k, y1)
        if grows == "rtl":
            return (x1 - (x1 - x0) * k, y0, x1, y1)
        if grows == "ttb":
            return (x0, y0, x1, y0 + (y1 - y0) * k)
        if grows == "btt":
            return (x0, y1 - (y1 - y0) * k, x1, y1)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        return (cx - (cx - x0) * k, cy - (cy - y0) * k, cx + (x1 - cx) * k, cy + (y1 - cy) * k)
    clip = p.shape(name, colour, (x0, y0, x1, y1), rr)
    clip["shapeStyle"]["layers"] = layers if layers is not None else GRAD
    return clip


def frame(p, r, at=0, w=6):
    """A gradient frame drawn as four bars: top and bottom run to the right, the sides come down."""
    x0, y0, x1, y1 = r
    box(p, "Marco", (x0, y0, x1, y0 + w), "ltr", at)
    box(p, "Marco 2", (x0, y1 - w, x1, y1), "ltr", at + 4)
    box(p, "Marco 3", (x0, y0, x0 + w, y1), "ttb", at + 2)
    box(p, "Marco 4", (x1 - w, y0, x1, y1), "ttb", at + 6)


class StepPiece(GradPiece):
    """A piece whose words enter and leave one by one in the same order (first in, first out): its frame is the
    plain frame count, and each word works out its own entrance and exit."""

    def frame(self, u):
        return u * FPS


def words(p, x0, y0, x1, y1, parts, at=0, name="Nombre", align="left", steps=None, speed=16):
    """A line made of words [(text, weight, italic, fill)] side by side with a word space between, sized so the
    whole line spans x0..x1 (its capitals centred on y0..y1), sliding up into place from frame `at`; fill is a
    colour or "grad"."""
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

    def lifter(a_in, a_out):
        """Up into place from frame a_in; down out of it, gone a_out frames before the end (StepPiece only)."""
        def k(fr):
            if steps is None:
                return EASE(fr - at)
            return min(EASE((fr - a_in) * 16 / speed), EASE((end - a_out - fr) * 16 / speed))
        # Far enough down to clear the reveal box (its bottom is 12 px under the line).
        return lambda fr: (0.0, (1 - k(fr)) * ((y1 - y0) + 26))
    for i, ((text, weight, italic, fill), em) in enumerate(zip(parts, ems)):
        lift = lifter(*(steps[i] if steps else (at, 0)))
        w = em * size
        clip = p.text(text, x + p.dx, ct + p.dy, cb + p.dy, w, FONT, weight, WHITE if fill == "grad" else fill,
                      name if i == 0 else f"{name} {i + 1}", shift=lift,
                      reveal=lambda fr: (rx0 - 40, ry0 - 14, rx1 + 60, ry1 + 12))
        if italic:
            clip["textStyle"]["italic"] = True
        if fill == "grad":
            clip["textStyle"]["layers"] = [gradient([(0.0, PINK), (1.0, BLUE)], angle=0)]
        x += w + space * size


def photo(p, r, at=0):
    """The photo slot, uncovered from its left by a mask (scaling a still would stretch its decode)."""
    from llt_motion import mask_track
    x0, y0, x1, y1 = _rect(p, r)
    b = Box(x0, y0, x1 - x0, y1 - y0)
    clip = p.t.photo(p.t.track("video", "Foto"), "man-04", 0.0, p.dur, b, None, label="Tu foto")
    mask_track(p.t, clip, b, lambda u: (x0, y0, x0 + (x1 - x0) * max(0.002, EASE(p.frame(u) - at)), y1), p.dur)


def piece(id, es, en, order, bounds, tags=()):
    t = _kit(id, es, en, order, list(tags))
    x0, _, _, y1 = bounds
    return t, GradPiece(t, D, 120 - x0, 960 - y1)


def p1():
    t, p = piece("1", "Tercio degradado: apellido en degradado y ficha", "Gradient lower third: gradient last name, tag",
                 8670, (510, 361, 1410, 720))
    words(p, 512, 364, 896, 452, [("Aleix", 400, True, WHITE)], 0)
    words(p, 510, 492, 1410, 587, [("Richardson", 700, False, "grad")], 4, "Apellido")
    box(p, "Ficha", (510, 618, 1410, 720), "ltr", 6)
    words(p, 542, 652, 1040, 685, [("Television reporter", 700, False, WHITE)], 10, "Cargo")
    return t


def p2():
    t, p = piece("2", "Tercio degradado: subrayado", "Gradient lower third: underline", 8671, (449, 449, 1468, 658))
    words(p, 450, 452, 1468, 545, [("Aleix", 700, False, WHITE), ("Richard", 700, False, WHITE)], 0)
    box(p, "Subrayado", (449, 573, 1142, 591), "ltr", 4)
    words(p, 450, 626, 948, 658, [("Television reporter", 700, False, WHITE)], 8, "Cargo")
    return t


def p3():
    t, p = piece("3", "Tercio degradado: caja con el cargo a la derecha", "Gradient lower third: role box on the right",
                 8672, (420, 432, 1500, 648))
    words(p, 640, 434, 1020, 528, [("Aleix", 700, False, WHITE)], 0)
    words(p, 425, 552, 1020, 646, [("Richard", 700, False, WHITE)], 3, "Apellido")
    box(p, "Caja", (1060, 432, 1500, 648), "ltr", 4)
    words(p, 1100, 462, 1290, 486, [("Live", 700, False, WHITE)], 10, "Cargo")
    words(p, 1100, 502, 1290, 526, [("Television", 700, False, WHITE)], 12, "Cargo 2")
    words(p, 1100, 542, 1290, 566, [("Reporter", 700, False, WHITE)], 14, "Cargo 3")
    return t


def p4():
    t, p = piece("4", "Tercio degradado: marco y ficha", "Gradient lower third: frame and tag", 8673,
                 (360, 372, 1560, 692))
    frame(p, (360, 372, 1560, 652), 0)
    words(p, 463, 460, 1481, 558, [("Aleix", 700, False, WHITE), ("Richard", 700, False, WHITE)], 4)
    box(p, "Ficha", (460, 600, 1128, 692), "ltr", 8)
    words(p, 499, 632, 997, 664, [("Television reporter", 700, False, WHITE)], 12, "Cargo")
    return t


def p5():
    t, p = piece("5", "Tercio degradado: barra vertical", "Gradient lower third: upright bar", 8674,
                 (424, 432, 1496, 648))
    box(p, "Barra", (424, 432, 454, 648), "ttb", 0)
    words(p, 479, 462, 1496, 560, [("Aleix", 700, False, WHITE), ("Richard", 700, False, WHITE)], 3)
    words(p, 479, 590, 977, 622, [("Television reporter", 700, False, WHITE)], 8, "Cargo")
    return t


def p6():
    t, p = piece("6", "Tercio degradado: nombre en una línea y ficha", "Gradient lower third: one-line name, tag",
                 8675, (306, 442, 1608, 678))
    words(p, 308, 444, 1608, 538, [("Aleix", 400, True, WHITE), ("Richardson", 700, False, WHITE)], 0)
    box(p, "Ficha", (306, 576, 1206, 678), "ltr", 5)
    words(p, 337, 613, 835, 645, [("Television reporter", 700, False, WHITE)], 9, "Cargo")
    return t


def p7():
    t, p = piece("7", "Tercio degradado: nombre en caja y cargo en marco", "Gradient lower third: name box, role frame",
                 8676, (399, 388, 1516, 698))
    box(p, "Caja", (988, 388, 1516, 584), "ltr", 0, layers=[gradient([(0.0, PINK), (1.0, BLUE)], angle=0),
                                                             no_stroke()])
    box(p, "Caja 2", (399, 388, 1000, 584), "ltr", 0, layers=[gradient([(0.0, PINK), (1.0, "#C33F95")], angle=0),
                                                              no_stroke()])
    words(p, 448, 434, 1466, 532, [("Aleix", 700, False, WHITE), ("Richard", 700, False, WHITE)], 4)
    frame(p, (399, 600, 1090, 698), 8, w=5)
    words(p, 436, 626, 934, 659, [("Television reporter", 700, False, WHITE)], 12, "Cargo")
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
                 (380, 362, 1548, 720))
    box(p, "Ficha", (380, 364, 1072, 452), "ltr", 0)
    words(p, 412, 394, 910, 427, [("Television reporter", 700, False, WHITE)], 4, "Cargo")
    frame(p, (380, 460, 1548, 720), 4)
    words(p, 448, 542, 1466, 636, [("Aleix", 700, False, WHITE), ("Richard", 700, False, WHITE)], 8)
    return t


def p10():
    t, p = piece("10", "Tercio degradado: apellido en caja y subrayado", "Gradient lower third: last name box, underline",
                 8679, (510, 432, 1410, 652))
    words(p, 516, 442, 892, 536, [("Aleix", 700, False, WHITE)], 0)
    box(p, "Caja", (920, 432, 1408, 540), "ltr", 3)
    words(p, 940, 468, 1390, 508, [("Richardson", 400, True, WHITE)], 7, "Apellido")
    box(p, "Subrayado", (510, 568, 1410, 586), "ltr", 5)
    words(p, 511, 620, 1009, 652, [("Television reporter", 700, False, WHITE)], 9, "Cargo")
    return t


def p11():
    t, p = piece("11", "Tercio degradado: barra alta y apellido en caja", "Gradient lower third: tall bar, last name box",
                 8680, (453, 333, 1472, 748))
    box(p, "Barra", (453, 333, 483, 748), "ttb", 0)
    words(p, 514, 370, 898, 460, [("Aleix", 400, True, WHITE)], 3)
    box(p, "Caja", (514, 486, 1472, 665), "ltr", 4)
    words(p, 550, 528, 1434, 623, [("Richardson", 700, False, WHITE)], 8, "Apellido")
    words(p, 514, 696, 1012, 728, [("Television reporter", 700, False, WHITE)], 10, "Cargo")
    return t


def p12():
    t, p = piece("12", "Tercio degradado: ficha arriba, marco y apellido en degradado",
                 "Gradient lower third: tag, frame, gradient last name", 8681, (380, 372, 1540, 712))
    box(p, "Ficha", (380, 372, 1060, 460), "ltr", 0)
    words(p, 406, 401, 904, 430, [("Television reporter", 700, False, WHITE)], 4, "Cargo")
    frame(p, (380, 468, 1540, 712), 4)
    words(p, 449, 547, 1464, 638, [("Aleix", 400, True, WHITE), ("Richard", 700, False, "grad")], 8)
    return t


def p13():
    t, p = piece("13", "Tercio degradado: etiqueta y cuadro", "Gradient lower third: tag and square", 8682,
                 (574, 426, 1342, 642))
    words(p, 574, 429, 960, 519, [("Aleix", 700, False, WHITE)], 0)
    box(p, "Etiqueta", (978, 426, 1342, 522), "ltr", 3)
    words(p, 1000, 458, 1320, 490, [("TV Reporter", 700, False, WHITE)], 8, "Cargo")
    box(p, "Cuadro", (574, 546, 722, 642), "pop", 4)
    words(p, 749, 546, 1342, 640, [("Richard", 700, False, WHITE)], 6, "Apellido")
    return t


def p14():
    t, p = piece("14", "Tercio degradado: subrayado y cargo a la derecha", "Gradient lower third: underline, role right",
                 8683, (452, 477, 1464, 625))
    words(p, 454, 479, 1464, 569, [("Aleix", 400, True, WHITE), ("Richard", 700, False, "grad")], 0)
    box(p, "Subrayado", (452, 602, 926, 620), "ltr", 4)
    words(p, 955, 593, 1453, 625, [("Television reporter", 700, False, WHITE)], 8, "Cargo")
    return t


def p15():
    t, p = piece("15", "Tercio degradado: cuadros y ficha", "Gradient lower third: squares and tag", 8684,
                 (572, 390, 1344, 726))
    words(p, 575, 394, 958, 484, [("Aleix", 400, True, WHITE)], 0)
    box(p, "Caja", (992, 390, 1344, 486), "ltr", 2)
    box(p, "Cuadro", (572, 510, 722, 606), "pop", 4)
    words(p, 749, 512, 1342, 606, [("Richard", 700, False, WHITE)], 5, "Apellido")
    box(p, "Ficha", (572, 630, 1343, 726), "ltr", 6)
    words(p, 604, 663, 903, 695, [("TV Reporter", 700, False, WHITE)], 10, "Cargo")
    return t


def p16():
    t, p = piece("16", "Tercio degradado con foto: apellido en degradado", "Gradient lower third with photo", 8685,
                 (300, 404, 1624, 676), ["foto"])
    photo(p, (300, 404, 568, 676), 0)
    words(p, 608, 451, 1624, 541, [("Aleix", 400, True, WHITE), ("Richard", 700, False, "grad")], 4)
    words(p, 607, 598, 1105, 630, [("Television reporter", 700, False, WHITE)], 8, "Cargo")
    return t


def p17():
    t, p = piece("17", "Tercio degradado con foto: nombre en dos líneas y ficha", "Gradient lower third with photo, tag",
                 8686, (520, 368, 1394, 738), ["foto"])
    photo(p, (520, 388, 752, 616), 0)
    words(p, 790, 370, 1167, 460, [("Aleix", 700, False, WHITE)], 3)
    words(p, 797, 499, 1390, 593, [("Richard", 700, False, WHITE)], 5, "Apellido")
    box(p, "Ficha", (526, 636, 1394, 738), "ltr", 6)
    words(p, 556, 672, 1054, 704, [("Television reporter", 700, False, WHITE)], 10, "Cargo")
    return t


def p18():
    t, p = piece("18", "Tercio degradado con foto y barra", "Gradient lower third with photo and bar", 8687,
                 (472, 388, 1446, 690), ["foto"])
    photo(p, (472, 388, 768, 688), 0)
    box(p, "Barra", (800, 390, 818, 690), "ttb", 2)
    words(p, 846, 393, 1223, 483, [("Aleix", 700, False, WHITE)], 4)
    words(p, 854, 511, 1446, 605, [("Richard", 700, False, WHITE)], 6, "Apellido")
    words(p, 846, 647, 1344, 679, [("Television reporter", 700, False, WHITE)], 9, "Cargo")
    return t


def p19():
    t, p = piece("19", "Tercio degradado con foto en marco", "Gradient lower third with photo in a frame", 8688,
                 (248, 396, 1660, 684), ["foto"])
    photo(p, (248, 400, 532, 676), 0)
    frame(p, (248, 396, 1660, 684), 2)
    words(p, 583, 458, 1601, 552, [("Aleix", 700, False, WHITE), ("Richard", 700, False, WHITE)], 5)
    words(p, 583, 586, 1081, 618, [("Television reporter", 700, False, WHITE)], 9, "Cargo")
    return t


def p20():
    t, p = piece("20", "Tercio degradado con foto, marco y ficha", "Gradient lower third with photo, frame and tag",
                 8689, (300, 386, 1616, 692), ["foto"])
    photo(p, (300, 386, 504, 590), 0)
    frame(p, (502, 386, 1616, 590), 2)
    words(p, 542, 438, 1558, 532, [("Aleix", 400, True, WHITE), ("Richard", 700, False, WHITE)], 5)
    box(p, "Ficha", (300, 600, 976, 692), "ltr", 6)
    words(p, 331, 626, 829, 658, [("Television reporter", 700, False, WHITE)], 10, "Cargo")
    return t


TEMPLATES = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20]
