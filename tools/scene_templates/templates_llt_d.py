"""Logo lower thirds, fourth set (2026-11-07): the four of 50962342.mp4 (1920×1080 at 60 fps), a near-black rounded
bar (#1A1A1A), a white logo badge and Poppins in green (name #85BE46, role #506932). Every edge plays the curve
measured at 60 fps with llt4_measure.py (lt_ref/lt4*.json; notes in tienda/plantillas/estudio-50962342/NOTAS.md).
Laid out where the reference shows each one alone over a video (bottom left of a 1920×1080 frame), with no
background: the user's video is the background, and the app fits a lower third into a Short (fitLowerThirdLayout).
The logo is a slot («Tu logo», the Flip play symbol as the sample, Jorge 2026-11-07). Order 8580-8583. Not published until Jorge says
the group is complete.
"""

from __future__ import annotations

from pathlib import Path

from kit import Box, label, wide
from llt_motion import frames_of, mask_track
from scene import fill, keys, no_stroke, shadow

FONT = "Poppins"
DARK = "#1A1A1A"
GREEN = "#85BE46"  # the name, lit
DIM = "#506932"    # the role, and the name before the light runs over it
WHITE = "#FFFFFF"
GREY = "#8A8A8A"   # B's role, and its name before the dark light runs over it
INK = "#161616"    # B's name, lit
FPS = 60.0  # the measurements' rate: frame numbers below are 60 fps frames
CAP = 0.698  # Poppins' capitals, em
_FONT_DIR = Path(__file__).resolve().parents[4] / "codigo" / "flip-addons" / "build" / "stage" / "fonts.basic" / \
    "fonts" / "poppins"
_FACES = {400: "Regular", 600: "SemiBold", 700: "Bold"}


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"llt4-{id}", es, en, "ytkit", dur, order=order, tags=["kit:lowerthirds", "tercio", "logo"] + tags,
                **kw)


def _ink(text: str, size: float, weight: int, spacing: float = 0.0):
    """(left, right) of `text`'s ink at `size`, each letter followed by `spacing` px."""
    from PIL import ImageFont
    f = ImageFont.truetype(str(_FONT_DIR / f"Poppins-{_FACES[weight]}.ttf"), 400)
    k = size / 400
    bb = f.getbbox(text)
    return bb[0] * k, (f.getlength(text[:-1]) + f.getbbox(text[-1])[2]) * k + spacing * (len(text) - 1)


def curve(points):
    """[(frame, value), ...] at 60 fps -> f(frame), linear between, held outside."""
    def f(fr):
        if fr <= points[0][0]:
            return points[0][1]
        for (a, va), (b, vb) in zip(points, points[1:]):
            if fr <= b:
                return va + (vb - va) * (fr - a) / (b - a)
        return points[-1][1]
    return f


def rects(table):
    """{frame: (x0, y0, x1, y1)} -> f(frame) -> the rectangle, each edge linear between the measured frames."""
    frames = sorted(table)
    edges = [curve([(fr, table[fr][i]) for fr in frames]) for i in range(4)]
    return lambda fr: tuple(e(fr) for e in edges)


class Piece:
    """One lower third over the clip time: u = 0 plays reference frame `start` (60 fps frames)."""

    def __init__(self, t, dur, start, mirror=False):
        self.t, self.dur, self.start, self.mirror = t, dur, start, mirror

    def frame(self, u):
        """mirror: the entrance, then the same backwards to leave (as the reference does for B, C and D)."""
        return self.start + (min(u, self.dur - u) if self.mirror else u) * FPS

    def shape(self, name, colour, full, rect, radius, kind="rounded-rectangle", layers=None, track=None):
        """A shape laid out in `full` (x0, y0, x1, y1) covering rect(frame) every frame; radius is a number or a
        function of the frame (keyed corner radius, project px)."""
        box = Box(full[0], full[1], full[2] - full[0], full[3] - full[1])
        motion = []
        for u in frames_of(self.dur):
            x0, y0, x1, y1 = rect(self.frame(u))
            w, h = max(0.0, x1 - x0), max(0.0, y1 - y0)
            motion.append((u, {"sx": w / box.w, "sy": h / box.h, "dx": (x0 + x1) / 2 - box.cx,
                               "dy": (y0 + y1) / 2 - box.cy}, "linear"))
        r0 = radius if not callable(radius) else radius(self.frame(0))
        clip = self.t.solid(track or self.t.track("shape", name), colour, 0.0, self.dur, box, motion, radius=r0,
                            kind=kind, layers=layers or [fill(colour), no_stroke()])
        clip["name"] = name
        if callable(radius):
            clip["shapeStyle"]["keyframes"] = {"cornerRadius": keys([(u, radius(self.frame(u)), "linear")
                                                                     for u in frames_of(self.dur)])}
        return clip

    def text(self, content, ink_left, caps_top, caps_bottom, weight, colour, name, width=None, shift=None,
             reveal=None, opacity=None, editable=True):
        """A Poppins line in capitals whose ink starts at `ink_left` with its capitals on [caps_top, caps_bottom];
        `width` (the ink's) sets the letter spacing. shift(frame) = dx moves it, reveal(frame) = (x0, y0, x1, y1)
        shows only that part of the frame, opacity(frame) fades it."""
        size = round((caps_bottom - caps_top - 0.8) / CAP, 1)
        up = content.upper()
        lo, hi = _ink(up, size, weight)
        spacing = round((width - (hi - lo)) / (len(up) - 1), 2) if width else 0.0
        h = size * 1.6
        w = (hi - lo) + spacing * len(up) + size * 2
        box = Box(ink_left - lo, (caps_top + caps_bottom) / 2 - h / 2, w, h)
        motion = [(u, {"dx": shift(self.frame(u))}, "linear") for u in frames_of(self.dur)] if shift else None
        clip = label(self.t, self.t.track("text", name), content, 0.0, self.dur, box, FONT, size, colour,
                     weight=weight, align="left", name=name, line=1.0, editable=editable, motion=motion,
                     spacing=spacing, case="upper")
        if opacity:
            clip["opacity"] = keys([(u, opacity(self.frame(u)), "linear") for u in frames_of(self.dur)])
        if reveal:
            def local(u):
                x0, y0, x1, y1 = reveal(self.frame(u))
                if x1 - x0 < 0.5 or y1 - y0 < 0.5:
                    # An empty mask still draws a one-pixel line: put it far from the text instead.
                    return (-4000.0, -4000.0, -3999.0, -3999.0)
                dx = shift(self.frame(u)) if shift else 0.0
                return (x0 - dx, y0, x1 - dx, y1)
            mask_track(self.t, clip, box, local, self.dur)
        return clip


def pop_bar():
    """A: a white disc with the logo pops and a dark capsule grows down from it; the capsule opens sideways into the
    bar while the disc flies to its top right corner and turns into a rounded square; the name and the role slide in
    from the left inside the bar and a light runs over the name. It leaves closing to the left, the badge shrinking
    into the bar."""
    # Reference frames: 0 = 3.0 s of the video; the piece plays frames 8 (the first dot) to 369 (the bar gone).
    start, end = 8, 369
    D = round((end - start) / FPS, 2)
    t = _kit("pastilla-barra", "Tercio con logo: pastilla que se abre en barra",
             "Logo lower third: capsule that opens into a bar", D, 8580, ["nombre", "barra", "verde", "pastilla"],
             thumb_at=3.0)
    p = Piece(t, D, start)
    out = 276  # the exit was measured from 7.6 s: its frame g is entrance frame g + 276
    # The capsule: centred on x 547.5, its top circle concentric with the disc (centre y 867).
    width = curve([(9, 0), (10, 18), (11, 30), (12, 46), (13, 59), (14, 69), (15, 77), (16, 83), (17, 86), (18, 88),
                   (19, 92), (20, 94), (21, 96), (22, 99), (23, 100), (24, 102), (26, 104), (28, 106)])
    bottom = curve([(9, 867), (10, 904), (11, 914), (12, 926), (13, 936), (14, 942), (15, 948), (16, 952), (17, 954),
                    (18, 958), (19, 960), (20, 962), (21, 964), (22, 966), (24, 968), (26, 970), (30, 972)])
    left = curve([(52, 494), (54, 492), (55, 488), (56, 486), (57, 484), (58, 482), (59, 478), (60, 476), (61, 472),
                  (62, 466), (63, 458), (64, 450), (65, 441), (66, 431), (67, 416), (68, 392), (69, 360), (70, 314),
                  (71, 280), (72, 254), (73, 234), (74, 220), (75, 212), (76, 208), (77, 200), (78, 194), (79, 190),
                  (80, 188), (81, 186), (82, 184), (83, 182), (84, 180),
                  (out + 62, 180), (out + 70, 176), (out + 72, 174), (out + 74, 172), (out + 75, 170), (out + 77, 166),
                  (out + 78, 162), (out + 79, 158), (out + 80, 154), (out + 81, 144), (out + 82, 128),
                  (out + 83, 110), (out + 84, 100), (out + 85, 94), (out + 86, 90), (out + 87, 88), (out + 88, 86),
                  (out + 89, 84), (out + 90, 82), (out + 91, 80), (out + 92, 80)])
    right = curve([(52, 600), (53, 604), (55, 606), (56, 608), (57, 610), (58, 612), (59, 616), (60, 620), (61, 625),
                   (62, 630), (63, 636), (64, 644), (65, 652), (66, 664), (67, 680), (68, 702), (69, 732), (70, 779),
                   (71, 818), (72, 844), (73, 861), (74, 872), (75, 882), (76, 890), (77, 896), (78, 901), (79, 904),
                   (80, 908), (81, 911), (82, 912), (83, 914), (84, 915), (85, 916),
                   (out + 62, 916), (out + 63, 914), (out + 65, 912), (out + 66, 909), (out + 67, 906),
                   (out + 68, 902), (out + 69, 898), (out + 70, 892), (out + 71, 884), (out + 72, 874),
                   (out + 73, 864), (out + 74, 852), (out + 75, 837), (out + 76, 822), (out + 77, 797),
                   (out + 78, 770), (out + 79, 736), (out + 80, 686), (out + 81, 614), (out + 82, 495),
                   (out + 83, 343), (out + 84, 254), (out + 85, 204), (out + 86, 168), (out + 87, 144),
                   (out + 88, 126), (out + 89, 112), (out + 90, 100), (out + 91, 93), (out + 92, 86), (out + 93, 80)])
    top = curve([(52, 813), (86, 810)])
    base = curve([(52, 972), (86, 974)])

    def bar(fr):
        if fr < 52:
            w = width(fr)
            return (547.5 - w / 2, 867 - w / 2, 547.5 + w / 2, max(867 + w / 2, bottom(fr)))
        if fr >= out + 93:
            return (80, 810, 80, 974)
        return (left(fr), top(fr), right(fr), base(fr))
    REST_R = 48
    bar_r = lambda fr: width(fr) / 2 if fr < 52 else 53 + (REST_R - 53) * min(1, (fr - 52) / 34)  # noqa: E731
    p.shape("Barra", DARK, (180, 810, 916, 974), bar, bar_r)
    # The texts ride inside the bar (masked by it): the name, then the role a little later.
    name_dx = curve([(58, -150), (64, -89), (65, -79), (66, -69), (67, -59), (68, -51), (69, -43), (70, -37),
                     (71, -31), (72, -27), (73, -21), (74, -18), (75, -15), (76, -11), (77, -9), (78, -7), (79, -5),
                     (80, -3), (82, -1), (86, 0)])
    role_dx = curve([(60, -150), (69, -82), (71, -64), (73, -50), (75, -38), (77, -26), (79, -20), (83, -8),
                     (89, -4), (100, -2), (120, 0)])
    inside = lambda fr: (bar(fr)[0], 800, bar(fr)[2], 990)  # noqa: E731
    p.text("Murad Guliyev", 238, 856, 885, 600, DIM, "Nombre", width=324, shift=name_dx, reveal=inside)
    # The light: the same name lit from the left, frames 84-94 (on top, so it is not a field of its own).
    lit = curve([(84, 238), (85, 268), (86, 319), (87, 364), (88, 403), (89, 435), (90, 464), (91, 493), (92, 517),
                 (93, 538), (94, 557), (95, 562)])
    p.text("Murad Guliyev", 238, 856, 885, 600, GREEN, "Nombre encendido", width=324, shift=name_dx, editable=False,
           reveal=lambda fr: (max(238.0, bar(fr)[0]), 800, min(lit(fr), bar(fr)[2]), 990))
    p.text("Motion designer", 238, 910, 932, 400, DIM, "Cargo", width=282, shift=role_dx, reveal=inside)
    # The badge: a disc that pops (centre 547.5, 867), then flies to the corner and squares off.
    disc = curve([(8, 1), (9, 8), (10, 14), (11, 23), (12, 36), (13, 46), (14, 54), (15, 59), (16, 64), (17, 67),
                  (18, 70), (19, 72), (20, 74), (22, 78), (24, 80), (26, 82), (28, 83), (30, 84), (52, 85)])
    fly = rects({52: (505.5, 825, 590.5, 910), 54: (508, 824, 593, 909), 56: (511, 823, 596, 908),
                 58: (515, 822, 600, 908), 60: (521, 821, 607, 907), 62: (530, 819, 616, 905), 64: (542, 816, 629, 903),
                 66: (561, 811, 650, 900), 68: (594, 803, 686, 894), 69: (623, 797, 716, 890), 70: (662, 787, 759, 883),
                 71: (698, 779, 796, 877), 72: (721, 773, 821, 873), 73: (736, 770, 837, 871),
                 74: (747, 767, 850, 869), 75: (756, 765, 859, 868), 76: (763, 763, 865, 867),
                 78: (772, 761, 876, 865), 80: (778, 760, 882, 864), 82: (782, 759, 886, 863),
                 84: (784, 758, 889, 863), 86: (785, 758, 890, 863),
                 out + 59: (785, 758, 890, 863), out + 60: (786, 759, 889, 862), out + 62: (787, 760, 888, 861),
                 out + 63: (787, 761, 887, 860), out + 64: (788, 762, 886, 860), out + 65: (790, 764, 885, 859),
                 out + 66: (791, 766, 883, 858), out + 67: (793, 769, 881, 857), out + 68: (796, 773, 879, 856),
                 out + 69: (799, 778, 876, 854), out + 70: (803, 784, 872, 852), out + 71: (808, 791, 867, 850),
                 out + 72: (814, 799, 862, 847), out + 73: (818, 807, 857, 846), out + 74: (822, 814, 853, 846),
                 out + 75: (825, 822, 850, 847), out + 76: (828, 830, 848, 850), out + 77: (830, 839, 838, 852),
                 out + 78: (834, 845, 834, 845)})

    def badge(fr):
        if fr < 52:
            d = disc(fr)
            return (547.5 - d / 2, 867 - d / 2, 547.5 + d / 2, 867 + d / 2)
        return fly(fr)
    BADGE_R = 27
    badge_r = lambda fr: (badge(fr)[2] - badge(fr)[0]) / 2 if fr < 60 else \
        (BADGE_R + (42.5 - BADGE_R) * max(0.0, (78 - fr) / 18) if fr < out else  # noqa: E731
         min(BADGE_R, (badge(fr)[2] - badge(fr)[0]) / 2))
    p.shape("Insignia", WHITE, (785, 758, 890, 863), badge, badge_r)
    # The logo: 0.46 of the badge (the leaf measures 34 of 84 in the disc, 43-50 of 105 in the square).
    logo_box = Box(813.5, 786.5, 48, 48)
    motion = []
    for u in frames_of(D):
        x0, y0, x1, y1 = badge(p.frame(u))
        s = (x1 - x0) * 0.46 / logo_box.w
        motion.append((u, {"s": s, "dx": (x0 + x1) / 2 - logo_box.cx, "dy": (y0 + y1) / 2 - logo_box.cy}, "linear"))
    t.photo(t.track("video", "Logo"), "logo-flip", 0.0, D, logo_box, motion, label="Tu logo", brandRole="logo")
    return t


def white_card():
    """B: a white rounded square pops with the dark logo square inside; the square opens sideways into a white card
    while the logo square slides to its right end; the name and the role slide in from the left inside the card and
    a dark light runs over the grey name. It leaves with its entrance played backwards."""
    # Reference frames: 0 = 9.15 s of the video; the white dot shows at frame 3, the exit ends 15.72 s.
    start = 3
    D = 6.52
    t = _kit("ficha-blanca", "Tercio con logo: ficha blanca que se abre", "Logo lower third: white card that opens",
             D, 8581, ["nombre", "blanco", "ficha"], thumb_at=3.0)
    p = Piece(t, D, start, mirror=True)
    side = curve([(2, 0), (3, 9), (4, 18), (5, 29), (6, 46), (7, 69), (8, 89), (9, 104), (10, 115), (11, 123),
                  (12, 129), (13, 135), (14, 139), (15, 143), (16, 147), (17, 150), (18, 153), (19, 155), (20, 157),
                  (22, 159), (23, 161), (26, 163)])
    left = curve([(38, 466), (39, 465), (40, 464), (41, 463), (42, 461), (43, 459), (44, 456), (45, 451), (46, 446),
                  (47, 439), (48, 429), (49, 415), (50, 394), (51, 362), (52, 325), (53, 296), (54, 276), (55, 261),
                  (56, 250), (57, 240), (58, 232), (59, 226), (60, 220), (61, 215), (62, 210), (63, 207), (64, 203),
                  (65, 200), (66, 198), (67, 196), (68, 194), (69, 192), (70, 190), (72, 188), (74, 186), (77, 185)])
    right = curve([(38, 629), (39, 630), (40, 631), (41, 632), (42, 634), (43, 636), (44, 640), (45, 644), (46, 649),
                   (47, 656), (48, 666), (49, 680), (50, 700), (51, 732), (52, 770), (53, 798), (54, 819), (55, 834),
                   (56, 845), (57, 855), (58, 863), (59, 869), (60, 875), (61, 880), (62, 884), (63, 888), (64, 891),
                   (65, 894), (66, 897), (67, 899), (68, 901), (69, 903), (70, 904), (71, 906), (72, 907), (73, 908),
                   (75, 909), (77, 910)])

    def card(fr):
        if fr < 38:
            s = side(fr)
            return (547.5 - s / 2, 891.5 - s / 2, 547.5 + s / 2, 891.5 + s / 2)
        return (left(fr), 810, right(fr), 973)
    CARD_R = 34
    p.shape("Ficha", WHITE, (185, 810, 910, 973), card, lambda fr: min(CARD_R, 0.21 * (card(fr)[2] - card(fr)[0])),
            layers=[shadow("#000000", 0, 8, 24, 0.18), fill(WHITE), no_stroke()])
    name_dx = curve([(46, -260), (52, -177), (56, -121), (60, -77), (64, -43), (68, -23), (72, -9), (75, -3),
                     (79, 0)])
    role_dx = curve([(48, -300), (52, -260), (56, -207), (60, -157), (64, -101), (68, -61), (72, -33), (76, -18),
                     (79, -9), (82, -4), (85, -1), (88, 0)])
    inside = lambda fr: (card(fr)[0], 800, card(fr)[2], 990)  # noqa: E731
    p.text("Murad Guliyev", 242, 856, 885, 600, GREY, "Nombre", width=325, shift=name_dx, reveal=inside)
    lit = curve([(80, 242), (81, 323), (82, 365), (83, 407), (84, 440), (85, 471), (86, 496), (87, 521), (88, 541),
                 (89, 561), (90, 565), (91, 568)])
    p.text("Murad Guliyev", 242, 856, 885, 600, INK, "Nombre encendido", width=325, shift=name_dx, editable=False,
           reveal=lambda fr: (max(242.0, card(fr)[0]), 800, min(lit(fr), card(fr)[2]), 990))
    p.text("Motion designer", 245, 909, 932, 400, GREY, "Cargo", width=282, shift=role_dx, reveal=inside)
    # The logo square: grows inside the white one (centre 547, 892), then slides to the card's right end.
    size = curve([(10, 0), (11, 15), (12, 22), (13, 36), (14, 60), (15, 73), (16, 81), (17, 89), (18, 93), (19, 97),
                  (20, 101), (21, 105), (22, 107), (23, 109), (24, 111), (25, 113), (26, 114), (27, 115), (28, 117),
                  (30, 118), (31, 119), (34, 120)])
    slide = curve([(42, 487), (43, 487), (44, 488), (45, 489), (46, 491), (47, 492), (48, 495), (49, 498), (50, 503),
                   (51, 508), (52, 516), (53, 526), (54, 541), (55, 564), (56, 599), (57, 635), (58, 662), (59, 681),
                   (60, 695), (61, 707), (62, 716), (63, 724), (64, 730), (65, 736), (66, 741), (67, 745), (68, 749),
                   (69, 752), (70, 755), (71, 757), (72, 760), (73, 762), (74, 763), (75, 765), (76, 766), (77, 767),
                   (78, 768), (80, 769), (82, 770)])

    def square(fr):
        if fr < 42:
            d = size(fr)
            return (547 - d / 2, 892 - d / 2, 547 + d / 2, 892 + d / 2)
        return (slide(fr), 832, slide(fr) + 120, 952)
    p.shape("Fondo del logo", DARK, (770, 832, 890, 952), square,
            lambda fr: min(20, 0.17 * (square(fr)[2] - square(fr)[0])),
            layers=[shadow("#000000", -14, 0, 40, 0.22), fill(DARK), no_stroke()])
    logo_box = Box(803, 865, 54, 54)
    motion = []
    for u in frames_of(D):
        x0, y0, x1, y1 = square(p.frame(u))
        motion.append((u, {"s": (x1 - x0) * 0.45 / logo_box.w, "dx": (x0 + x1) / 2 - logo_box.cx,
                           "dy": (y0 + y1) / 2 - logo_box.cy}, "linear"))
    t.photo(t.track("video", "Logo"), "logo-flip", 0.0, D, logo_box, motion, label="Tu logo", brandRole="logo")
    return t


def _logo(t, p, D, badge, rest, k=0.45, clip_left=None):
    """The logo slot inside badge(frame), `k` of its width; clip_left hides what passes left of that x."""
    logo_box = Box((rest[0] + rest[2]) / 2 - 27, (rest[1] + rest[3]) / 2 - 27, 54, 54)
    motion = []
    for u in frames_of(D):
        x0, y0, x1, y1 = badge(p.frame(u))
        motion.append((u, {"s": max(1e-4, (x1 - x0) * k / logo_box.w), "dx": (x0 + x1) / 2 - logo_box.cx,
                           "dy": (y0 + y1) / 2 - logo_box.cy}, "linear"))
    clip = t.photo(t.track("video", "Logo"), "logo-flip", 0.0, D, logo_box, motion, label="Tu logo", brandRole="logo")
    if clip_left is not None:
        _clip_left(t, clip, logo_box, motion, clip_left, D)
    return clip


def _clip_left(t, clip, box, motion, x, D):
    """A mask that hides what of `clip` (laid out in `box`, moved and scaled by `motion`) passes left of screen x."""
    moves = {round(u, 4): m for u, m, _ in motion}

    def rect(u):
        m = moves.get(round(u, 4), {})
        s = m.get("s", m.get("sx", 1.0)) or 1e-6
        # The mask lives in the clip's own frame: undo its move and its scale about the box centre.
        cx = box.cx + m.get("dx", 0.0)
        left = box.cx + (x - cx) / s
        return (left, box.y - 4000, box.x + box.w + 4000, box.y + box.h + 4000)
    mask_track(t, clip, box, rect, D)


def bar_logo_left():
    """C: a thin dark line stands up and opens sideways into the bar; the name slides in from the left inside it;
    a white logo badge flies in from the left with a bounce, pushing the bar, and the role follows; a light runs
    over the name. It leaves to the left: the role and the name drift right as the bar closes into a line on the
    left and the badge slides out past a straight edge."""
    # Reference frames: 0 = 15.5 s of the video; the line shows at 16; the exit (measured from 20.6 s) ends at 381.
    start, end, out = 16, 381, 306
    D = round((end - start) / FPS, 2)
    t = _kit("logo-izquierda", "Tercio con logo: barra oscura y logo a la izquierda",
             "Logo lower third: dark bar, logo on the left", D, 8582, ["nombre", "barra", "verde"], thumb_at=3.0)
    p = Piece(t, D, start)
    o = {15: (554, 554), 16: (553, 555), 17: (552.5, 555.5), 18: (551.5, 556.5), 19: (551, 557), 20: (549, 559),
         21: (546, 562), 22: (542, 565), 23: (537, 570), 24: (532, 576), 25: (523, 585), 26: (512, 596),
         27: (497, 611), 28: (474, 640), 29: (439, 688), 30: (393, 730), 31: (355, 762), 32: (328, 796),
         33: (308, 809), 34: (293, 815), 35: (281, 827), 36: (270, 839), 37: (264, 848), 38: (254, 855),
         39: (248, 861), 40: (244, 866), 41: (238, 874), 42: (234, 876), 43: (231, 880), 44: (227, 882),
         45: (224, 888), 46: (222, 890), 47: (220, 890), 48: (218, 890), 49: (216, 892), 50: (215, 896),
         52: (213, 896), 54: (211, 896), 57: (211, 897), 60: (211, 897)}
    opening = rects({k: (a, 788, b, 952) for k, (a, b) in o.items()})
    # The badge's landing pushes the bar right and lets it back (its right edge measured).
    push = curve([(60, 897), (62, 896), (63, 902), (64, 914), (65, 920), (66, 924), (67, 926), (68, 927), (69, 928),
                  (70, 928), (71, 925), (72, 923), (73, 920), (74, 916), (75, 914), (76, 912), (77, 909), (78, 906),
                  (79, 902), (80, 900), (81, 898), (84, 897)])
    lv = {44: (224, 897), 46: (224, 894), 48: (224, 890), 49: (223, 886), 50: (222, 882), 51: (221, 876),
          52: (220, 870), 53: (218, 862), 54: (216, 852), 55: (215, 848), 56: (212, 832), 57: (209, 818),
          58: (207, 804), 59: (204, 790), 60: (200, 770), 61: (194, 750), 62: (190, 726), 63: (183, 702),
          64: (176, 658), 65: (168, 600), 66: (156, 546), 67: (144, 477), 68: (127, 390), 69: (109, 288),
          70: (90, 194), 71: (78, 132), 72: (70, 104), 73: (63, 72), 74: (60, 66), 75: (59, 60), 76: (59, 59)}
    leaving = rects({out + k: (a, 788, b, 952) for k, (a, b) in lv.items()})

    def bar(fr):
        if fr < 60:
            return opening(fr)
        if fr < out + 44:
            dx = push(fr) - 897
            return (211 + dx, 788, 897 + dx, 952)
        return leaving(fr)
    p.shape("Barra", DARK, (211, 788, 897, 952), bar, lambda fr: min(46.0, (bar(fr)[2] - bar(fr)[0]) / 2))
    dx = lambda fr: push(fr) - 897 if 60 <= fr < out + 44 else 0.0  # noqa: E731
    name_in = curve([(32, -330), (36, -248), (40, -148), (44, -68), (48, -38), (52, -18), (56, -8), (60, -4),
                     (64, 0), (out + 52, 0), (out + 57, 12), (out + 59, 17), (out + 61, 25), (out + 63, 35),
                     (out + 65, 49), (out + 67, 69), (out + 69, 100), (out + 71, 140)])
    role_in = curve([(40, -700), (56, -600), (60, -260), (64, -172), (68, -106), (72, -48), (76, -22), (80, -9), (84, -4),
                     (90, 0), (out + 48, 0), (out + 52, 15), (out + 55, 45), (out + 57, 76), (out + 59, 102),
                     (out + 61, 140), (out + 63, 200), (out + 65, 280)])
    name_dx = lambda fr: name_in(fr) + dx(fr)  # noqa: E731
    role_dx = lambda fr: role_in(fr) + dx(fr)  # noqa: E731
    inside = lambda fr: (bar(fr)[0], 760, bar(fr)[2], 990)  # noqa: E731
    p.text("Murad Guliyev", 298, 836, 866, 600, DIM, "Nombre", width=324, shift=name_dx, reveal=inside)
    lit = curve([(63, 298), (64, 310), (66, 380), (68, 444), (70, 540), (72, 624)])
    p.text("Murad Guliyev", 298, 836, 866, 600, GREEN, "Nombre encendido", width=324, shift=name_dx, editable=False,
           reveal=lambda fr: (max(bar(fr)[0], 298 + name_dx(fr)), 760, min(bar(fr)[2], lit(fr) + name_dx(fr)), 990))
    p.text("Motion designer", 298, 890, 913, 400, DIM, "Cargo", width=279, shift=role_dx, reveal=inside)
    fl = {56: (72, 861, 72, 861), 57: (72, 858, 84, 864), 58: (89, 847, 127, 893), 59: (105, 837, 165, 903),
          60: (118, 829, 199, 911), 61: (128, 822, 219, 918), 62: (136, 817, 238, 922), 63: (142, 814, 253, 927),
          64: (146, 811, 264, 929), 65: (149, 809, 271, 931), 66: (150, 807, 275, 932), 67: (151, 807, 277, 933),
          68: (152, 807, 278, 933), 69: (151, 807, 278, 933), 70: (151, 807, 277, 933), 71: (150, 807, 275, 933),
          72: (149, 808, 273, 932), 73: (148, 808, 272, 932), 74: (147, 808, 270, 931), 75: (146, 809, 268, 931),
          76: (145, 809, 266, 931), 77: (143, 809, 264, 930), 78: (142, 810, 262, 930), 79: (140, 810, 260, 930),
          80: (138, 810, 258, 930), 81: (136, 810, 256, 930), 82: (135, 810, 255, 930), 83: (134, 810, 253, 930),
          84: (133, 810, 252, 930), 85: (132, 810, 252, 930), 86: (132, 810, 253, 930)}
    for k, right in {44: 253, 47: 251, 49: 250, 50: 248, 51: 247, 52: 245, 53: 243, 54: 241, 55: 238, 56: 235,
                     57: 232, 58: 228, 59: 223, 60: 218, 61: 212, 62: 205, 63: 197, 64: 187, 65: 176, 66: 162,
                     67: 144, 68: 121, 69: 95, 70: 70, 71: 54, 72: 40}.items():
        fl[out + k] = (right - 121, 810, right, 930)
    fly = rects(fl)
    rest = (132, 810, 253, 930)
    badge = p.shape("Insignia", WHITE, rest, fly, lambda fr: min(30.0, 0.25 * min(fly(fr)[2] - fly(fr)[0],
                                                                                  fly(fr)[3] - fly(fr)[1])))
    # The reference cuts the badge with a straight edge at x 48 as it leaves.
    bbox = Box(rest[0], rest[1], rest[2] - rest[0], rest[3] - rest[1])
    bmotion = []
    for u in frames_of(D):
        x0, y0, x1, y1 = fly(p.frame(u))
        bmotion.append((u, {"sx": max(1e-6, x1 - x0) / bbox.w, "dx": (x0 + x1) / 2 - bbox.cx}, "linear"))
    _clip_left(t, badge, bbox, bmotion, 48, D)
    _logo(t, p, D, fly, rest, clip_left=48)
    return t


def square_rises():
    """D: a thin line draws on the bottom left and thickens up into a dark rounded square; a white logo badge rises
    inside it; the badge lifts to the top left corner as the square opens to the right into the bar; the name slides
    in from the left and lights up, the role follows. It leaves closing the bar back into the badge, which sinks."""
    # Reference frames: 0 = 21.8 s of the video; the line shows at 4; the exit (measured from 26.8 s) ends at 361.
    start, end, out = 4, 361, 300
    D = round((end - start) / FPS, 2)
    t = _kit("cuadro-sube", "Tercio con logo: cuadro oscuro y logo que sube",
             "Logo lower third: dark square, logo lifts", D, 8583, ["nombre", "barra", "verde", "cuadro"],
             thumb_at=3.0)
    p = Piece(t, D, start)
    left = curve([(4, 152), (14, 158), (16, 190), (17, 170), (22, 168), (42, 169)])
    top = curve([(3, 897), (4, 897), (8, 896.5), (12, 894), (15, 890), (16, 888), (17, 885), (18, 879), (19, 866),
                 (20, 844), (21, 837), (22, 832), (23, 830), (24, 827), (25, 826), (26, 824), (27, 822), (28, 821),
                 (29, 820), (31, 819), (33, 818), (35, 817)])
    bottom = curve([(3, 897), (4, 899), (8, 900), (12, 902), (15, 906), (17, 912), (18, 916), (19, 926), (20, 948),
                    (21, 958), (22, 962), (23, 966), (24, 968), (25, 970), (27, 972), (29, 976), (33, 978), (42, 980)])
    right = curve([(4, 346), (14, 343), (16, 339), (17, 337), (22, 334), (28, 332), (56, 332), (57, 333), (58, 334),
                   (59, 336), (60, 339), (61, 341), (62, 345), (63, 349), (64, 354), (65, 359), (66, 366), (67, 373),
                   (68, 382), (69, 393), (70, 404), (71, 419), (72, 436), (73, 458), (74, 485), (75, 518), (76, 565),
                   (77, 666), (78, 744), (79, 802), (80, 848), (81, 878), (82, 894), (83, 902), (84, 911), (85, 918),
                   (86, 922), (87, 925), (88, 926), (89, 928)])
    lv = {29: (169, 928), 30: (170, 926), 33: (170, 922), 34: (170, 920), 35: (172, 914), 36: (172, 910),
          37: (172, 906), 38: (174, 900), 39: (174, 892), 40: (176, 884), 41: (178, 874), 42: (180, 862),
          43: (182, 850), 44: (186, 840), 45: (188, 824), 46: (190, 802), 47: (194, 779), 48: (204, 753),
          49: (210, 723), 50: (216, 688), 51: (224, 643), 52: (232, 585), 53: (246, 516), 54: (258, 434),
          55: (266, 364), 56: (266, 320), 57: (268, 291), 58: (272, 277), 59: (272, 272)}
    leaving = rects({out + k: (a, 817, b, 980) for k, (a, b) in lv.items()})

    def bar(fr):
        if fr < 3:
            return (249, 897, 249, 897)
        if fr >= out + 29:
            return leaving(fr)
        return (left(fr), top(fr), right(fr), bottom(fr))
    p.shape("Barra", DARK, (169, 817, 928, 980), bar,
            lambda fr: min(46.0, (bar(fr)[3] - bar(fr)[1]) / 2, (bar(fr)[2] - bar(fr)[0]) / 2))
    inside = lambda fr: (bar(fr)[0], 800, bar(fr)[2], 1000)  # noqa: E731
    # Leaving, both drift right out of the closing bar (the role first and faster).
    name_dx = curve([(68, -40), (72, -30), (76, -16), (80, -10), (84, -6), (88, -2), (92, 0), (out + 38, 0),
                     (out + 44, 34), (out + 48, 80), (out + 52, 164), (out + 56, 300)])
    role_dx = curve([(80, -60), (84, -44), (88, -26), (92, -12), (96, -6), (100, -2), (104, 0), (out + 36, 0),
                     (out + 44, 98), (out + 50, 250), (out + 54, 400)])
    p.text("Murad Guliyev", 386, 864, 894, 600, DIM, "Nombre", width=324, shift=name_dx, reveal=inside)
    lit = curve([(78, 386), (80, 420), (82, 480), (84, 540), (86, 600), (88, 660), (90, 712)])
    p.text("Murad Guliyev", 386, 864, 894, 600, GREEN, "Nombre encendido", width=324, shift=name_dx, editable=False,
           reveal=lambda fr: (max(bar(fr)[0], 386 + name_dx(fr)), 800, min(bar(fr)[2], lit(fr) + name_dx(fr)), 1000))
    p.text("Motion designer", 386, 918, 942, 400, DIM, "Cargo", width=276, shift=role_dx, reveal=inside,
           opacity=curve([(82, 0.0), (92, 1.0)]))
    rs = {18: (249.5, 926, 249.5, 926), 19: (234, 920, 265, 926), 20: (218, 899, 280, 951), 21: (210, 881, 289, 959),
          22: (203, 867, 296, 959), 23: (198, 855, 301, 958), 24: (194, 847, 305, 958), 25: (190, 840, 308, 958),
          26: (188, 836, 310, 957), 27: (187, 833, 312, 957), 28: (186, 832, 312, 957), 29: (186, 831, 313, 957),
          32: (187, 832, 312, 957), 34: (187, 834, 311, 957), 36: (188, 835, 311, 957), 38: (188, 836, 310, 957),
          40: (189, 837, 310, 958), 63: (189, 837, 309, 957), 66: (189, 836, 310, 956), 68: (190, 835, 310, 955),
          69: (190, 834, 310, 954), 70: (190, 833, 310, 953), 71: (190, 832, 311, 952), 72: (191, 831, 311, 951),
          73: (191, 829, 311, 949), 74: (192, 827, 312, 946), 75: (192, 823, 313, 943), 76: (194, 819, 314, 936),
          77: (198, 802, 317, 916), 78: (201, 785, 321, 904), 79: (202, 780, 322, 900), 80: (203, 777, 323, 897),
          81: (204, 775, 324, 895), 82: (204, 773, 324, 894), 83: (204, 772, 325, 893), 84: (204, 771, 325, 892),
          85: (204, 770, 325, 891), 86: (205, 770, 325, 890), 87: (205, 769, 326, 890), 89: (205, 769, 326, 889),
          91: (205, 768, 326, 889)}
    for k, r in {30: (205, 768, 325, 889), 31: (205, 769, 325, 889), 33: (205, 769, 325, 890),
                 35: (205, 771, 325, 891), 36: (204, 771, 325, 892), 37: (204, 772, 325, 893),
                 38: (204, 774, 324, 894), 39: (203, 775, 324, 896), 40: (203, 777, 323, 898),
                 41: (202, 781, 323, 901), 42: (200, 788, 321, 907), 43: (195, 810, 316, 927),
                 44: (192, 818, 315, 939), 45: (191, 822, 314, 944), 46: (190, 823, 314, 947),
                 47: (189, 825, 314, 949), 48: (188, 826, 314, 951), 49: (187, 826, 314, 952),
                 50: (187, 827, 314, 953), 51: (187, 828, 313, 954), 52: (187, 830, 313, 955),
                 53: (188, 833, 311, 956), 54: (190, 837, 309, 956), 55: (193, 844, 306, 957),
                 56: (197, 853, 302, 958), 57: (202, 865, 296, 959), 58: (210, 880, 289, 959),
                 59: (218, 900, 280, 960), 60: (229, 922, 270, 961), 61: (249.5, 961, 249.5, 961)}.items():
        rs[out + k] = r
    rise = rects(rs)
    rest = (205, 768, 326, 889)
    p.shape("Insignia", WHITE, rest, rise, lambda fr: min(30.0, 0.25 * min(rise(fr)[2] - rise(fr)[0],
                                                                          rise(fr)[3] - rise(fr)[1])))
    _logo(t, p, D, rise, rest)
    return t


TEMPLATES = [pop_bar, white_card, bar_logo_left, square_rises]
