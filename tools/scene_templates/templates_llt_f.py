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
from scene import fill, keys, no_stroke, tanim

NAME_FONT = "Archivo"
ROLE_FONT = "Poppins"
WHITE = "#FFFFFF"
INK = "#151515"
RED = "#E3262B"
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
             spacing_em=0.0, shift=None, reveal=None, editable=True, case="upper", bold=()):
        """A line whose capitals span [caps_top, caps_bottom] and whose ink is `width` wide from `edge` (its left,
        or its right with align right); shift(frame) = dx slides it, reveal(frame) = (x0, y0, x1, y1) screen
        rect shows only that part."""
        size, bearing = fit(content.upper() if case == "upper" else content, width, family, weight, spacing_em)
        h = size * 1.6
        w = width + size * 3
        cy = (caps_top + caps_bottom) / 2
        x = edge - bearing * size if align == "left" else edge - w + size * 0.02
        box = Box(x, cy - h / 2, w, h)
        motion = [(u, {"dx": shift(self.frame(u))}, "linear") for u in frames_of(self.dur)] if shift else None
        clip = label(self.t, self.t.track("text", name), content, 0.0, self.dur, box, family, size, colour,
                     weight=weight, align=align, name=name, line=1.0, editable=editable, motion=motion,
                     spacing=spacing_em * size, case=case)
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
                dx = shift(self.frame(u)) if shift else 0.0
                return (x0 - dx, y0, x1 - dx, y1)
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
    first = p.text("Oliver", 189, 745, 814, 424, NAME_FONT, 900, WHITE, "Nombre", spacing_em=-0.01, shift=first_shift)
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


TEMPLATES = [slanted_bar, red_sweep]
