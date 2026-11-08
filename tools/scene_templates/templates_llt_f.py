"""Type lower thirds, sixth set (2026-11-07): the ten of 38940869.mp4 (1920×1080 at 60 fps), shown over videos at
their real place and size, so laid out exactly where the reference has them, with no background. Big names in
Archivo Black, roles in letter-spaced Poppins, white slanted bars, red blocks and thin lines. Every edge plays the
curve measured at 60 fps (notes in tienda/plantillas/estudio-38940869/NOTAS.md); a piece leaves with its entrance
played backwards when the reference does. Order 8600-. Not published until Jorge says the group is complete.
"""

from __future__ import annotations

import math
from pathlib import Path

from kit import Box, label, wide
from llt_motion import frames_of, mask_track
from scene import fill, gradient, keys, no_stroke, tanim

NAME_FONT = "Archivo"
ROLE_FONT = "Poppins"
WHITE = "#FFFFFF"
INK = "#151515"
RED = "#E3262B"
# Some names fade from white at the top to grey at the bottom (Oliver, O'Sullivan).
SHADED = [gradient([(0.0, "#FFFFFF"), (0.45, "#FFFFFF"), (1.0, "#8E8E8E")], angle=90)]
FPS = 60.0
_STAGE = Path(__file__).resolve().parents[4] / "codigo" / "flip-addons" / "build" / "stage"
_FILES = {("Archivo", 900): "fonts.extra/fonts/archivo/Archivo-Black.ttf",
          ("Poppins", 500): "fonts.basic/fonts/poppins/Poppins-Medium.ttf",
          ("Poppins", 600): "fonts.basic/fonts/poppins/Poppins-SemiBold.ttf",
          ("Poppins", 700): "fonts.basic/fonts/poppins/Poppins-Bold.ttf"}


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"llt6-{id}", es, en, "ytkit", dur, order=order, tags=["kit:lowerthirds", "tercio"] + tags, **kw)


def curve(points):
    """[(frame, value), ...] -> f(frame), linear between, held outside."""
    def f(fr):
        if fr <= points[0][0]:
            return points[0][1]
        for (a, va), (b, vb) in zip(points, points[1:]):
            if fr <= b:
                return va + (vb - va) * (fr - a) / (b - a)
        return points[-1][1]
    return f


def _font(family, weight, size=400):
    from PIL import ImageFont
    return ImageFont.truetype(str(_STAGE / _FILES[(family, weight)]), size)


def fit(text, width, family, weight, spacing_em=0.0):
    """The size at which `text`'s ink (each letter followed by spacing_em × size) is `width` px wide."""
    f = _font(family, weight)
    bb = f.getbbox(text)
    ink = (f.getlength(text[:-1]) + f.getbbox(text[-1])[2] - bb[0]) / 400
    return round(width / (ink + spacing_em * (len(text) - 1)), 1), bb[0] / 400


class Piece:
    """One lower third in screen px; u = 0 plays reference frame `start`; mirror: the entrance backwards to leave."""

    def __init__(self, t, dur, start, mirror=True):
        self.t, self.dur, self.start, self.mirror = t, dur, start, mirror

    def frame(self, u):
        return self.start + (min(u, self.dur - u) if self.mirror else u) * FPS

    def shape(self, name, colour, full, rect, skew=0.0, alpha=1.0):
        """A shape laid out in `full` (x0, y0, x1, y1) covering rect(frame) every frame (a parallelogram leaning
        `skew` degrees, + to the right at the top, inside that rect)."""
        box = Box(full[0], full[1], full[2] - full[0], full[3] - full[1])
        motion = []
        for u in frames_of(self.dur):
            x0, y0, x1, y1 = rect(self.frame(u))
            w, h = max(0.0, x1 - x0), max(0.0, y1 - y0)
            motion.append((u, {"sx": max(1e-4, w / box.w), "sy": max(1e-4, h / box.h), "dx": (x0 + x1) / 2 - box.cx,
                               "dy": (y0 + y1) / 2 - box.cy}, "linear"))
        clip = self.t.solid(self.t.track("shape", name), colour, 0.0, self.dur, box, motion,
                            layers=[fill(colour, alpha), no_stroke()])
        clip["name"] = name
        if skew:
            clip["shapeStyle"]["skew"] = skew
        return clip

    def text(self, content, edge, caps_top, caps_bottom, width, family, weight, colour, name, align="left",
             spacing_em=0.0, shift=None, reveal=None, editable=True, case="upper", bold=(), layers=None):
        """A line whose capitals span [caps_top, caps_bottom] and whose ink is `width` wide from `edge` (its left,
        or its right with align right); shift(frame) = dx slides it, reveal(frame) = (x0, y0, x1, y1) screen
        rect shows only that part."""
        size, bearing = fit(content.upper() if case == "upper" else content, width, family, weight, spacing_em)
        h = size * 1.6
        w = width + size * 3
        cy = (caps_top + caps_bottom) / 2
        x = edge - bearing * size if align == "left" else edge - w + size * 0.02
        box = Box(x, cy - h / 2, w, h)
        two = (lambda fr: (lambda v: v if isinstance(v, tuple) else (v, 0.0))(shift(fr))) if shift else None
        motion = [(u, {"dx": two(self.frame(u))[0], "dy": two(self.frame(u))[1]}, "linear")
                  for u in frames_of(self.dur)] if shift else None
        clip = label(self.t, self.t.track("text", name), content, 0.0, self.dur, box, family, size, colour,
                     weight=weight, align=align, name=name, line=1.0, editable=editable, motion=motion,
                     spacing=spacing_em * size, case=case, layers=layers)
        # Bold words (runs): each given substring of `content` in Bold.
        runs = []
        for word in bold:
            i = content.lower().find(word.lower())
            if i >= 0:
                runs.append({"start": i, "end": i + len(word), "boldEnabled": True, "bold": True})
        if runs:
            clip["textStyle"]["runs"] = runs
        if reveal:
            def local(u):
                x0, y0, x1, y1 = reveal(self.frame(u))
                if x1 - x0 < 0.5 or y1 - y0 < 0.5:
                    return (-4000.0, -4000.0, -3999.0, -3999.0)
                dx, dy = two(self.frame(u)) if shift else (0.0, 0.0)
                return (x0 - dx, y0 - dy, x1 - dx, y1 - dy)
            mask_track(self.t, clip, box, local, self.dur)
        return clip


def slanted_bar():
    """1: a thin slanted line draws up, opens to the left into a white slanted bar with the role in it, and the name
    slides out to the right from behind the slanted edge."""
    start = 2
    D = 5.08  # its entrance played backwards ends at 5.12 s of the video
    t = _kit("barra-inclinada", "Tercio: barra blanca inclinada y nombre grande",
             "Lower third: white slanted bar, big name", D, 8600, ["nombre", "blanco", "inclinado"], thumb_at=2.5)
    p = Piece(t, D, start)
    TOP, BOT, RIGHT_TOP = 793, 932, 1025
    lean = 61 / (BOT - TOP)  # px to the right per px up
    skew = math.degrees(math.atan(lean))
    draw = curve([(2, BOT), (4, 900), (6, 860), (8, 820), (10, TOP)])  # the line's top as it draws up
    left = curve([(10, 1022), (14, 1022), (16, 1021), (18, 1018), (20, 1016), (22, 1014), (24, 1012), (26, 1009),
                  (28, 1006), (30, 1003), (32, 999), (34, 995), (36, 990), (38, 985), (40, 979), (42, 973),
                  (44, 965), (46, 957), (48, 948), (50, 938), (52, 927), (54, 914), (55, 906), (56, 898), (57, 890),
                  (58, 881), (59, 871), (60, 860), (61, 848), (62, 834), (63, 819), (64, 802), (65, 782), (66, 758),
                  (67, 729), (68, 692), (69, 644), (70, 583), (71, 523), (72, 475), (73, 438), (74, 409), (75, 385),
                  (76, 365), (77, 348), (78, 332), (79, 319), (80, 307), (82, 286), (84, 268), (86, 253), (88, 240),
                  (90, 229), (92, 218), (94, 209), (96, 201), (98, 194), (100, 188), (102, 182), (104, 177),
                  (106, 172), (108, 168), (110, 164), (112, 160), (114, 158), (116, 155), (118, 152), (120, 150),
                  (122, 148), (124, 147), (126, 146), (128, 144), (130, 143), (134, 142)])

    def bar(fr):
        """The parallelogram's bounding rect: its top edge from left(fr) to RIGHT_TOP."""
        if fr < 10:
            top = draw(fr)
            if top >= BOT - 0.5:
                return (RIGHT_TOP, BOT, RIGHT_TOP, BOT)
            x1 = RIGHT_TOP - (top - TOP) * lean
            return (x1 - (BOT - top) * lean - 3, top, x1, BOT)
        return (left(fr) - 61, TOP, RIGHT_TOP, BOT)
    p.shape("Barra", WHITE, (81, TOP, RIGHT_TOP, BOT), bar, skew=skew)
    # The role, dark on the bar, rides left with the bar's left edge (a little behind it: 0.85 of its travel) and
    # shows only on the bar (cut by its slanted right edge as it goes).
    ride = lambda fr: 0.85 * (bar(fr)[0] + 61 - 142) if fr >= 10 else 900.0  # noqa: E731
    p.text("Media relations coordinator & vice", 959, 840, 857, 660, ROLE_FONT, 500, INK, "Cargo",
           align="right", spacing_em=0.1, shift=ride, bold=("& vice",),
           reveal=lambda fr: (bar(fr)[0] + 30, TOP, RIGHT_TOP - (848 - TOP) * lean, BOT))
    p.text("President of marketing", 929, 871, 888, 430, ROLE_FONT, 500, INK, "Cargo 2", align="right",
           spacing_em=0.1, shift=ride, bold=("president",),
           reveal=lambda fr: (bar(fr)[0] + 15, TOP, RIGHT_TOP - (880 - TOP) * lean, BOT))
    # The name slides out to the right from behind the slanted edge.
    slide = curve([(50, -720), (54, -680), (55, -612), (60, -586), (65, -541), (70, -373), (75, -206), (80, -140), (82, -122),
                   (84, -107), (86, -94), (88, -83), (90, -73), (92, -65), (94, -57), (96, -50), (98, -44),
                   (100, -39), (102, -34), (104, -29), (106, -25), (108, -22), (110, -19), (112, -16), (114, -13),
                   (116, -11), (118, -9), (120, -7), (122, -6), (124, -4), (126, -3), (128, -2), (130, -1),
                   (134, 0)])
    p.text("Michael", 1030, 800, 857, 432, NAME_FONT, 900, WHITE, "Nombre", spacing_em=-0.01, shift=slide,
           reveal=lambda fr: (RIGHT_TOP - (828 - TOP) * lean, 780, 1920, 862))
    p.text("Richardson", 984, 869, 931, 660, NAME_FONT, 900, WHITE, "Apellido", spacing_em=-0.01, shift=slide,
           reveal=lambda fr: (RIGHT_TOP - (900 - TOP) * lean, 862, 1920, 945))
    return t


def table(rows):
    """{frame: value} -> f(frame) (linear)."""
    return curve(sorted(rows.items()))


def red_sweep():
    """2: a thin red line stands up, widens into a red block that sweeps right uncovering the last name behind it
    and goes; the first name slides in from the right letter by letter above; the role shows word by word."""
    start = 4  # frames from 5.25 s of the video
    D = 4.88
    t = _kit("barrido-rojo", "Tercio: bloque rojo que barre y descubre el nombre",
             "Lower third: red block sweeps to uncover the name", D, 8601, ["nombre", "rojo"], thumb_at=2.4)
    p = Piece(t, D, start)
    lx = table({4: 258, 26: 258, 28: 260, 30: 262, 34: 264, 36: 268, 38: 270, 40: 273, 42: 276, 44: 280, 46: 284,
                48: 290, 50: 296, 52: 302, 54: 310, 56: 318, 58: 328, 60: 340, 62: 352, 64: 368, 66: 386, 68: 410,
                70: 441, 72: 486, 74: 560, 76: 674, 78: 750, 80: 794, 82: 825, 84: 848, 86: 868, 88: 883, 90: 896,
                92: 908, 94: 917, 96: 925, 98: 933, 100: 940, 102: 945, 104: 950, 106: 954, 108: 958, 110: 962,
                112: 966, 114: 968, 116: 970, 118: 972, 119: 974})
    rx = table({4: 259, 6: 260, 8: 262, 12: 264, 14: 266, 16: 268, 18: 272, 20: 274, 22: 278, 24: 282, 26: 286,
                28: 292, 30: 297, 32: 304, 34: 310, 36: 320, 38: 328, 40: 340, 42: 352, 44: 368, 46: 386, 48: 410,
                50: 442, 52: 486, 54: 560, 56: 672, 58: 746, 60: 790, 62: 821, 64: 844, 66: 863, 68: 878, 70: 892,
                72: 902, 74: 912, 76: 920, 78: 928, 80: 934, 82: 940, 84: 944, 86: 949, 88: 953, 90: 956, 92: 960,
                94: 962, 96: 964, 98: 966, 100: 968, 102: 970, 104: 971, 106: 972, 110: 974, 119: 974})
    grow = table({3: 916, 4: 814, 6: 808, 12: 806})

    def block(fr):
        if fr < 3.5 or fr > 119:
            return (258, 916, 258, 916)
        return (lx(fr), grow(fr), rx(fr), 916)
    # The thin white line the last name comes out of (x 255), there while the block sweeps.
    p.shape("Línea", WHITE, (255, 830, 258, 910), lambda fr: (255, 830, 258, 910) if 50 <= fr <= 112
            else (256.5, 870, 256.5, 870))
    # The last name rides on the block's left edge (its end just behind it) and shows right of the line.
    last_shift = lambda fr: min(0.0, lx(fr) - 967) if fr <= 119 else 0.0  # noqa: E731
    p.text("Stockham", 268, 836, 905, 694, NAME_FONT, 900, WHITE, "Apellido", spacing_em=-0.01, shift=last_shift,
           reveal=lambda fr: (255, 820, max(255.0, min(lx(fr), 1920)) if fr <= 119 else 1920, 920))
    p.shape("Bloque", RED, (258, 806, 974, 916), block)
    first_shift = table({60: 260, 62: 200, 66: 183, 70: 166, 74: 129, 78: 71, 80: 57, 84: 40, 90: 26, 100: 12,
                         110: 5, 120: 1, 126: 0})
    first = p.text("Oliver", 189, 745, 814, 424, NAME_FONT, 900, WHITE, "Nombre", spacing_em=-0.01, shift=first_shift,
                   layers=SHADED)
    # Letter by letter, each coming in big and see-through and settling (its block starts at frame 58).
    first["timelineStartUs"] = int(round((58 - start) / FPS * 1e6))
    first["timelineDurationUs"] = int(round((D - 2 * (58 - start) / FPS) * 1e6))
    first["textStyle"]["animation"] = {
        "in": tanim("pop", duration=0.33, unit="character", stagger=0.07, ease="easeOut", **{"from": 170}),
        "out": tanim("pop", duration=0.33, unit="character", stagger=0.07, ease="easeIn", order="backward",
                     **{"from": 170})}
    shown = table({64: 189, 66: 399, 72: 400, 74: 812, 76: 868})
    p.text("Network administrator &", 189, 934, 953, 678, ROLE_FONT, 500, WHITE, "Cargo", spacing_em=0.42,
           reveal=lambda fr: (180, 925, shown(fr), 960))
    p.text("Computer programmer", 188, 966, 985, 598, ROLE_FONT, 500, WHITE, "Cargo 2", spacing_em=0.42,
           reveal=lambda fr: (180, 960, shown(fr - 20), 995))
    return t


def divider():
    """3: a white divider line grows down while it flies in from the right; the role comes out of it to the left
    and the name to the right, riding with it until it lands."""
    start = 30  # frames from 10.6 s of the video
    D = 2.95  # the reference leaves a little sooner than a mirror of 3.2 s
    t = _kit("divisor", "Tercio: línea divisoria con cargo y nombre a los lados",
             "Lower third: divider line, role and name either side", D, 8602, ["nombre", "linea"], thumb_at=1.6)
    p = Piece(t, D, start)
    lx = table({30: 1390, 34: 1367, 36: 1351, 38: 1330, 40: 1302, 42: 1258, 44: 1181, 46: 1100, 48: 1060, 50: 1030,
                52: 1005, 54: 990, 56: 980, 58: 971, 62: 955, 66: 935, 70: 922, 74: 917, 78: 914, 82: 912, 86: 909,
                90: 906, 94: 904, 96: 903, 102: 902})
    bottom = table({30: 770, 34: 800, 36: 806, 38: 814, 40: 824, 42: 840, 44: 869, 58: 900, 62: 953, 82: 968,
                    92: 971, 100: 972})

    def line(fr):
        if fr < 30:
            return (1390, 766, 1390, 766)
        return (lx(fr), 766, lx(fr) + 3, bottom(fr))
    p.shape("Línea", WHITE, (902, 766, 905, 972), line)
    name_off = table({46: -460, 48: -412, 58: -180, 62: -136, 70: -66, 78: -37, 90: -10, 100: 0})
    role_off = table({46: 230, 48: 200, 50: 166, 54: 122, 58: 87, 62: 64, 66: 59, 70: 44, 78: 20, 90: 4, 100: 0})
    name_slide = lambda fr: lx(fr) - 902 + name_off(fr)  # noqa: E731
    role_slide = lambda fr: lx(fr) - 902 + role_off(fr)  # noqa: E731
    right_of_line = lambda fr: (line(fr)[2] + 1, 780, 1920, 960) if fr >= 44 else (0, 0, 0, 0)  # noqa: E731
    left_of_line = lambda fr: (0, 780, line(fr)[0] - 1, 960) if fr >= 44 else (0, 0, 0, 0)  # noqa: E731
    p.text("Martin", 924, 801, 866, 386, NAME_FONT, 900, WHITE, "Nombre", spacing_em=-0.01, shift=name_slide,
           reveal=right_of_line)
    p.text("Stewardson", 924, 873, 942, 697, NAME_FONT, 900, WHITE, "Apellido", spacing_em=-0.01,
           shift=name_slide, reveal=right_of_line)
    p.text("Media relations coordinator & vice", 874, 843, 860, 627, ROLE_FONT, 500, WHITE, "Cargo",
           align="right", shift=role_slide, reveal=left_of_line)
    p.text("President of marketing", 874, 879, 896, 407, ROLE_FONT, 500, WHITE, "Cargo 2", align="right",
           shift=role_slide, reveal=left_of_line)
    return t


def red_underline():
    """4: a red underline draws to the right; the last name slides in from the right as its letters fade in one by
    one, the first name comes down into place above it, and the bold role slides in from the left."""
    start = 4  # frames from 15.0 s of the video
    D = 4.1
    t = _kit("subrayado-rojo", "Tercio: nombre grande y subrayado rojo", "Lower third: big name, red underline", D,
             8603, ["nombre", "rojo", "subrayado"], thumb_at=2.0)
    p = Piece(t, D, start)
    under = table({3: 124, 24: 187, 33: 220, 36: 280, 39: 317, 42: 370, 45: 448, 48: 589, 51: 700, 54: 900,
                   60: 1150, 66: 1300, 75: 1380, 90: 1408})
    p.shape("Subrayado", RED, (124, 944, 1408, 956), lambda fr: (124, 944, under(fr), 956))
    role_slide = table({30: -1500, 40: -1360, 45: -1172, 48: -991, 51: -661, 54: -448, 57: -341, 60: -263, 63: -208, 66: -171,
                        72: -111, 78: -78, 84: -45, 90: -30, 96: -18, 105: -6, 112: 0})
    p.text("Help desk worker - desktop support", 128, 880, 916, 1350, ROLE_FONT, 700, WHITE, "Cargo",
           shift=role_slide, reveal=lambda fr: (124, 860, 1920, 935))
    last_slide = table({6: 380, 12: 368, 24: 336, 30: 325, 33: 314, 36: 307, 39: 303, 42: 281, 45: 255, 48: 227,
                        51: 151, 54: 97, 57: 64, 60: 60, 63: 53, 66: 38, 72: 31, 81: 10, 93: 5, 105: 0})
    last = p.text("Anderson", 123, 767, 850, 669, NAME_FONT, 900, WHITE, "Apellido", spacing_em=-0.01,
                  shift=last_slide)
    last["textStyle"]["animation"] = {
        "in": tanim("fade", duration=0.4, unit="character", stagger=0.08, ease="easeInOut", delay=0.3),
        "out": tanim("fade", duration=0.4, unit="character", stagger=0.08, ease="easeInOut", order="backward",
                     delay=0.3)}
    drop = table({44: -110, 45: -70, 48: -45, 51: -22, 54: -10, 57: -4, 63: 0})
    p.text("William", 124, 675, 754, 535, NAME_FONT, 900, WHITE, "Nombre", spacing_em=-0.01,
           shift=lambda fr: (0.0, drop(fr)), reveal=lambda fr: (100, 668, 1920, 762))
    return t


def white_label():
    """5: a thin white line on the left opens to the right into a label with the role in it; the last name slides in
    from the right as its letters fade in, and the first name comes down into place above it."""
    start = 4  # frames from 19.4 s of the video
    D = 4.26
    t = _kit("etiqueta-blanca", "Tercio: nombre grande y etiqueta blanca con el cargo",
             "Lower third: big name, white label with the role", D, 8604, ["nombre", "blanco", "etiqueta"],
             thumb_at=2.1)
    p = Piece(t, D, start)
    right = table({4: 122, 16: 122, 20: 146, 24: 187, 28: 209, 32: 228, 36: 241, 40: 282, 44: 323, 48: 391,
                   52: 494, 56: 726, 60: 989, 64: 1106, 68: 1161, 72: 1207, 76: 1248, 80: 1256, 88: 1284})
    label_ = lambda fr: (119, 926, right(fr), 974) if fr >= 3 else (119, 950, 119, 950)  # noqa: E731
    p.shape("Etiqueta", WHITE, (119, 926, 1284, 974), label_)
    p.text("Marketing research analyst & marketing manager", 1268, 943, 958, 1110, ROLE_FONT, 600, INK, "Cargo",
           align="right", spacing_em=0.3, shift=lambda fr: right(fr) - 1284, reveal=label_)
    slide = table({20: 400, 40: 387, 44: 373, 48: 333, 52: 319, 56: 170, 60: 115, 64: 74, 68: 61, 76: 61, 80: 47,
                   84: 34, 96: 20, 110: 0})
    last = p.text("O'Sullivan", 128, 842, 921, 684, NAME_FONT, 900, WHITE, "Apellido", spacing_em=-0.01, shift=slide,
                  layers=SHADED)
    last["textStyle"]["animation"] = {
        "in": tanim("fade", duration=0.45, unit="character", stagger=0.08, ease="easeInOut", delay=0.3),
        "out": tanim("fade", duration=0.45, unit="character", stagger=0.08, ease="easeInOut", order="backward",
                     delay=0.3)}
    drop = table({42: -110, 44: -70, 48: -45, 52: -22, 56: -8, 60: 0})
    p.text("Natalie", 123, 759, 837, 474, NAME_FONT, 900, WHITE, "Nombre", spacing_em=-0.01,
           shift=lambda fr: (0.0, drop(fr)), reveal=lambda fr: (100, 750, 1920, 842))
    return t


TEMPLATES = [slanted_bar, red_sweep, divider, red_underline, white_label]
