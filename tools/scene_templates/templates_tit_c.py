"""Cyan corporate titles, third TITLE set (2026-11-08): the twenty of 18722056.mp4 (1920×1080 at 29.97 fps; the
same pack in yellow is 1197825.mp4). Names in Bebas Neue, small words in Montserrat, a cyan-to-teal gradient on
boxes, circles, triangles and frames, near-black type, over a light background (its own «Fondo» layer, which the
user can hide). Laid out where the reference has them. Kit de YouTube › Títulos con estilo; ids `tit3-*`, order
8840-. Study notes in tienda/plantillas/estudio-18722056/NOTAS.md.

The moves (measured on 10 fps sheets): elements fade in with a short slide (the reference blurs them as they move),
lines grow from their middle, boxes open from the left, circles and triangles pop, frames draw themselves; each
piece leaves with its entrance backwards, as the reference does. The famous names of the reference are replaced
by ordinary ones, the stock site's brand by neutral words, and «SUCESS» / «GHANGES» are spelled right.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from scene import gradient, keys, layout, no_stroke, shape_style
from templates_llt_f import table
from templates_tit_b import Slide

FPS = 30000 / 1001
INK = "#231F20"
WHITE = "#FFFFFF"
CYAN, TEAL = "#00AEEF", "#10A39A"
BG = "#F4EBE8"
GRAD = [gradient([(0.0, CYAN), (1.0, TEAL)], angle=0), no_stroke()]
f6._FILES[("Bebas Neue", 400)] = "fonts.basic/fonts/bebasneue/BebasNeue-Regular.ttf"
f6._FILES[("Montserrat", 500)] = "fonts.basic/fonts/montserrat/Montserrat-Medium.ttf"
f6._FILES[("Montserrat", 600)] = "fonts.basic/fonts/montserrat/Montserrat-SemiBold.ttf"
NAME, SMALL = "Bebas Neue", "Montserrat"
SMOOTH = table({0.0: 0.0, 0.25: 0.15, 0.5: 0.5, 0.75: 0.85, 1.0: 1.0})


def k(fr, at, n):
    """0 → 1 from frame at over n frames (smooth)."""
    return SMOOTH(min(1.0, max(0.0, (fr - at) / max(1e-6, n))))


def _kit(id, es, en, dur, order, tags, **kw):
    return wide(f"tit3-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:titulos-estilo", "título", "celeste", "corporativo"] + tags, **kw)


class Piece3(Slide):
    """A slide whose clips can turn about a common pivot (the tilted pieces)."""

    def __init__(self, t, dur, tilt=0.0, pivot=(960, 540)):
        super().__init__(t, dur)
        self.tilt, self.pivot = tilt, pivot
        self.background(BG)

    def _turned(self, clip):
        if not self.tilt:
            return clip
        # Turn the clip about the piece's pivot: its centre moves round the pivot, and it turns by the tilt.
        a = math.radians(self.tilt)
        px, py = self.pivot
        for key_x, key_y, key_w, key_h in (("x", "y", "width", "height"),):
            xs, ys = clip[key_x]["keyframes"], clip[key_y]["keyframes"]
            ws, hs = clip[key_w]["keyframes"], clip[key_h]["keyframes"]
            for kx, ky, kw, kh in zip(xs, ys, ws, hs):
                cx, cy = kx["value"] + kw["value"] / 2, ky["value"] + kh["value"] / 2
                dx, dy = cx - px, cy - py
                nx, ny = px + dx * math.cos(a) - dy * math.sin(a), py + dx * math.sin(a) + dy * math.cos(a)
                kx["value"], ky["value"] = nx - kw["value"] / 2, ny - kh["value"] / 2
        clip["rotation"] = keys([(0.0, self.tilt, "hold")])
        return clip

    # --- elements -------------------------------------------------------------------------------------------------
    def word(self, text, ink, family=NAME, weight=400, colour=INK, name="Título", at=0, n=9, slide=40, align="center",
             italic=False, layers=None):
        """Words that fade in sliding `slide` px from the left from frame at."""
        clip = self.text(text, ink, family, weight, colour, name, align=align, italic=italic, layers=layers,
                         shift=lambda fr: (-(1 - k(fr, at, n)) * slide, 0.0))
        self.fade(clip, lambda fr: k(fr, at, n))
        return self._turned(clip)

    def bar(self, name, rect, at=0, n=9, way="ltr", layers=None, colour=CYAN, fade=False):
        """A solid (gradient) box opening `way` (ltr, rtl, mid = from its middle, ttb, btt, pop = from its
        centre) from frame at."""
        x0, y0, x1, y1 = rect

        def r(fr):
            q = k(fr, at, n)
            if way == "ltr":
                return (x0, y0, x0 + (x1 - x0) * q, y1)
            if way == "rtl":
                return (x1 - (x1 - x0) * q, y0, x1, y1)
            if way == "ttb":
                return (x0, y0, x1, y0 + (y1 - y0) * q)
            if way == "btt":
                return (x0, y1 - (y1 - y0) * q, x1, y1)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if way == "mid":
                return (cx - (cx - x0) * q, y0, cx + (x1 - cx) * q, y1)
            return (cx - (cx - x0) * q, cy - (cy - y0) * q, cx + (x1 - cx) * q, cy + (y1 - cy) * q)
        clip = self.box(name, colour, r)
        clip["shapeStyle"]["layers"] = layers if layers is not None else GRAD
        if fade:
            self.fade(clip, lambda fr: k(fr, at, n))
        return self._turned(clip)

    def outline(self, name, pts, width, colour=CYAN, at=0, n=12, closed=True):
        """A frame (polygon, screen px) that draws itself from its first point from frame at."""
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        bx0, by0 = min(xs) - width, min(ys) - width
        bw, bh = max(xs) - min(xs) + 2 * width, max(ys) - min(ys) + 2 * width
        P = lambda x, y: f"{(x - bx0) / bw * 100:.3f} {(y - by0) / bh * 100:.3f}"  # noqa: E731
        path = "M " + " L ".join(P(*p) for p in (pts + [pts[0]] if closed else pts))
        s = {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "opacity": 1.0, "cap": "butt",
             "join": "miter", "strokeAlign": "center", "paint": {"kind": "solid", "color": "#ff" + colour[1:].lower()}}
        hollow = {"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}
        style = shape_style("custom", [hollow, s], customPath=path, customEvenOdd=False)
        style["keyframes"] = {"trimStart": keys([(0.0, 0.0, "hold")]),
                              "trimEnd": keys([(u, round(100 * k(self.frame(u), at, n), 3), "linear")
                                               for u in frames_of(self.dur)])}
        clip = self.t._clip("shape", 0.0, self.dur, shapeStyle=style, **layout(Box(bx0, by0, bw, bh), None))
        clip["name"] = name
        self.t.track("shape", name).clips.append(clip)
        return self._turned(clip)

    def blob(self, name, kind, rect, at=0, n=9, layers=None):
        """A circle or triangle (kind) popping from its centre."""
        clip = self.bar(name, rect, at, n, "pop", layers=layers)
        if kind == "circle":
            clip["shapeStyle"]["kind"] = "ellipse"
        else:
            clip["shapeStyle"]["kind"] = "custom"
            clip["shapeStyle"]["customPath"] = "M 0 0 L 100 0 L 50 100 Z"
            clip["shapeStyle"]["customEvenOdd"] = False
        return clip


def rect_pts(x0, y0, x1, y1, start="tl"):
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    i = {"tl": 0, "tr": 1, "br": 2, "bl": 3}[start]
    return pts[i:] + pts[:i]


def _p(id, es, en, dur, order, tags=(), **kw):
    return _kit(id, es, en, dur, order, list(tags), thumb_at=round(dur / 2, 1), **kw)


def name_box():
    t = _p("nombre-caja", "Título: nombre en caja y dos líneas", "Title: name box, two lines", 4.4, 8840, ["nombre"])
    s = Piece3(t, 4.4)
    s.bar("Caja", (610, 480, 1310, 600), 0, 12, "ltr", fade=True)
    s.word("DANIEL RICHARDS", (632, 494, 1290, 586), colour=WHITE, at=4, n=10)
    s.word("WONDERFUL ACTING", (608, 612, 1081, 668), name="Texto", at=14, n=9, align="left")
    s.word("IN THE MOVIES", (610, 678, 953, 734), name="Texto 2", at=24, n=9, align="left")
    flag = s.blob("Bandera", "triangle", (1096, 612, 1148, 666), 33, 6)
    flag["shapeStyle"]["customPath"] = "M 0 0 L 100 0 L 0 100 Z"
    return t


def name_role_above():
    t = _p("nombre-cargo-arriba", "Título: nombre en caja, cargo arriba", "Title: name box, role above", 4.4, 8841,
           ["nombre"])
    s = Piece3(t, 4.4)
    s.bar("Línea", (610, 459, 1310, 469), 0, 12, "ltr", fade=True)
    s.bar("Caja", (610, 480, 1310, 600), 2, 12, "ltr", fade=True)
    s.word("RICHARD HAYES", (632, 494, 1290, 586), colour=WHITE, at=6, n=10)
    s.word("motion designer", (612, 404, 985, 440), SMALL, 500, name="Texto", at=33, n=12, align="left")
    return t


def name_lines():
    t = _p("nombre-lineas", "Título: nombre entre dos líneas", "Title: name between two lines", 4.9, 8842,
           ["nombre", "líneas"])
    s = Piece3(t, 4.9)
    # One line grows from the middle, then splits into the two that frame the name.
    s.bar("Línea", (608, 475, 1310, 486), 0, 18, "mid")
    s.bar("Línea 2", (608, 588, 1310, 599), 0, 18, "mid")
    s.word("ROBBIE COLLINS", (643, 496, 1277, 578), at=24, n=18, slide=0)
    s.word("layout artist", (818, 613, 1102, 646), SMALL, 500, name="Texto", at=42, n=10, slide=0)
    s.bar("Línea 3", (750, 666, 1170, 676), 44, 10, "mid")
    return t


def twenty_animation():
    t = _p("20-animation", "Título: 20 Animation", "Title: 20 Animation", 4.8, 8843, ["número"])
    s = Piece3(t, 4.8)
    s.bar("Línea", (750, 532, 1171, 542), 0, 18, "mid")
    s.word("ANIMATION", (760, 555, 1155, 637), at=21, n=9, slide=0)
    s.bar("Línea 2", (750, 648, 1171, 658), 24, 10, "mid")
    s.word("20", (772, 308, 1152, 524), SMALL, 600, CYAN, "Número", at=27, n=15, slide=0,
           layers=[gradient([(0.0, TEAL), (1.0, CYAN)], angle=0)])
    s.word("CORPORATE TITLES", (752, 671, 1169, 699), SMALL, 600, name="Texto", at=36, n=9, slide=0)
    return t


def twenty_square():
    t = _p("20-cuadro", "Título: 20 Animated en un marco", "Title: 20 Animated in a frame", 4.2, 8844, ["marco"])
    s = Piece3(t, 4.2)
    s.outline("Marco", rect_pts(760, 338, 1164, 742), 6, at=0, n=10)
    s.word("20", (919, 390, 1007, 442), SMALL, 600, name="Número", at=12, n=8, slide=0)
    s.bar("Raya", (845, 410, 905, 418), 14, 8, "mid")
    s.bar("Raya 2", (1021, 410, 1081, 418), 14, 8, "mid")
    tilt = Piece3.__new__(Piece3)
    tilt.__dict__.update(s.__dict__)
    tilt.tilt = -4.0
    tilt.word("ANIMATED", (701, 460, 1222, 617), at=21, n=10, slide=80)
    tilt.word("TITLES", (880, 641, 1044, 685), SMALL, 600, name="Texto", at=27, n=8, slide=40)
    s.bar("Raya 3", (930, 622, 970, 630), 27, 8, "mid")
    return t


def name_offset_box():
    t = _p("nombre-sombra", "Título: caja con marco desplazado", "Title: box with an offset frame", 4.8, 8845,
           ["nombre", "marco"])
    s = Piece3(t, 4.8)
    s.bar("Caja", (626, 440, 1294, 640), 0, 12, "ltr")
    s.outline("Marco", rect_pts(610, 460, 1272, 660, "bl"), 6, INK, at=18, n=10)
    s.word("MATTHEW LANE", (650, 452, 1270, 545), colour=WHITE, at=4, n=10)
    s.word("COSTUME DESIGNER", (652, 565, 1060, 610), colour=INK, name="Texto", at=27, n=9)
    return t


def circle_name():
    t = _p("circulo", "Título: nombre sobre un círculo", "Title: name over a circle", 4.9, 8846, ["círculo", "nombre"])
    s = Piece3(t, 4.9)
    ring = s.blob("Anillo", "circle", (735, 380, 1124, 744), 0, 12, layers=[gradient([(0.0, INK), (1.0, INK)], angle=0),
                                                                           no_stroke()])
    s.blob("Círculo", "circle", (775, 355, 1144, 724), 0, 12)
    s.word("EMMA WALKER", (840, 430, 1382, 520), at=24, n=10)
    s.word("AUTOGRAPH SESSION", (840, 532, 1300, 575), name="Texto", at=33, n=9)
    s.word("30.11.2026", (840, 588, 1010, 632), colour=WHITE, name="Texto 2", at=38, n=8)
    return t


def triangle_name():
    t = _p("triangulo", "Título: nombre sobre un triángulo", "Title: name over a triangle", 4.8, 8847,
           ["triángulo", "nombre"])
    s = Piece3(t, 4.8)
    s.blob("Sombra", "triangle", (740, 436, 1146, 785), 0, 12, layers=[gradient([(0.0, INK), (1.0, INK)], angle=0),
                                                                      no_stroke()])
    s.blob("Triángulo", "triangle", (758, 423, 1162, 772), 0, 12)
    s.word("ALAN RIVERS", (870, 438, 1379, 520), at=18, n=12)
    s.word("TECHNO BLOGGER", (900, 532, 1180, 572), name="Texto", at=27, n=9)
    s.word("2026", (940, 590, 990, 612), SMALL, 600, WHITE, "Texto 2", at=33, n=8, slide=0)
    s.word("OCT", (945, 620, 985, 642), SMALL, 600, WHITE, "Texto 3", at=35, n=8, slide=0)
    s.word("30", (952, 650, 978, 672), SMALL, 600, WHITE, "Texto 4", at=37, n=8, slide=0)
    return t


def two_triangles():
    t = _p("dos-triangulos", "Título: nombre entre dos triángulos", "Title: name between two triangles", 4.6, 8848,
           ["triángulo", "nombre"])
    s = Piece3(t, 4.6)
    a = s.bar("Triángulo", (626, 422, 1000, 638), 0, 12, "ltr", fade=True)
    a["shapeStyle"]["kind"] = "custom"
    a["shapeStyle"]["customPath"] = "M 0 0 L 100 0 L 0 100 Z"
    b = s.bar("Triángulo 2", (914, 422, 1288, 638), 0, 12, "rtl", fade=True)
    b["shapeStyle"]["kind"] = "custom"
    b["shapeStyle"]["customPath"] = "M 100 0 L 100 100 L 0 100 Z"
    s.word("ADRIAN ROWE", (644, 447, 1250, 528), at=18, n=9)
    s.word("MOTION DESIGNER", (648, 551, 1068, 581), SMALL, 500, name="Texto", at=27, n=9)
    s.bar("Línea", (646, 603, 1268, 613), 36, 9, "ltr", layers=[gradient([(0.0, INK), (1.0, INK)], angle=0),
                                                              no_stroke()])
    return t


def epic_event():
    t = _p("evento", "Título: evento inclinado con marcos", "Title: tilted event with frames", 4.8, 8849,
           ["evento", "marco", "inclinado"])
    s = Piece3(t, 4.8, tilt=-5.0)
    s.outline("Marco", rect_pts(790, 470, 1180, 560, "tr"), 6, CYAN, at=0, n=14)
    s.outline("Marco 2", rect_pts(745, 495, 1150, 595, "bl"), 6, INK, at=6, n=14)
    s.bar("Caja", (760, 478, 1165, 585), 30, 9, "ltr", fade=True)
    s.word("EPIC EVENT", (790, 482, 1170, 548), at=33, n=10)
    s.word("ONLY TODAY", (800, 556, 1010, 580), SMALL, 600, WHITE, "Texto", at=42, n=8)
    return t


def unique_pack():
    t = _p("titles-pack", "Título: dos marcos inclinados", "Title: two tilted frames", 4.8, 8850,
           ["marco", "inclinado"])
    s = Piece3(t, 4.8, tilt=-5.0)
    s.outline("Marco", rect_pts(830, 388, 1215, 470, "tr"), 6, CYAN, at=0, n=12)
    s.word("20 UNIQUE", (850, 396, 1200, 462), colour=CYAN, at=14, n=9)
    s.outline("Marco 2", rect_pts(660, 520, 1120, 610, "br"), 6, INK, at=9, n=12)
    s.word("TITLES PACK", (680, 528, 1105, 600), at=24, n=9)
    return t


def unique_animated():
    t = _p("unique-animated", "Título: tres partes en cursiva", "Title: three italic parts", 4.8, 8851, ["cursiva"])
    s = Piece3(t, 4.8)
    s.bar("Caja", (514, 410, 926, 530), 0, 9, "ltr")
    s.word("20 UNIQUE", (530, 420, 912, 520), colour=WHITE, at=2, n=9, italic=True)
    s.word("ANIMATED", (932, 428, 1305, 508), at=18, n=10, italic=True)
    s.outline("Marco", rect_pts(824, 540, 1318, 658, "tl"), 6, CYAN, at=27, n=9)
    s.word("TITLES PACK", (845, 552, 1300, 648), colour=CYAN, at=30, n=9, italic=True)
    return t


def best_day():
    t = _p("best-day", "Título: caja y marco en cursiva", "Title: italic box and frame", 4.4, 8852, ["cursiva"])
    s = Piece3(t, 4.4)
    s.bar("Caja", (520, 480, 915, 600), 0, 12, "ltr", fade=True)
    s.word("BEST DAY TO", (536, 492, 900, 588), colour=WHITE, at=2, n=12, italic=True)
    s.outline("Marco", rect_pts(930, 480, 1408, 600, "bl"), 6, CYAN, at=21, n=9)
    s.word("CHANGES", (950, 492, 1390, 588), colour=CYAN, at=24, n=9, italic=True)
    return t


def best_event():
    t = _p("best-event", "Título: caja inclinada y mercado", "Title: tilted box and market", 4.9, 8853,
           ["inclinado", "evento"])
    s = Piece3(t, 4.9, tilt=-4.0)
    s.outline("Marco", rect_pts(740, 470, 1180, 560, "tr"), 6, CYAN, at=0, n=10)
    s.bar("Caja", (740, 470, 1180, 560), 10, 9, "ltr")
    s.word("BEST EVENT", (760, 476, 1165, 556), colour=WHITE, at=12, n=9)
    s.word("CITY MARKET", (742, 572, 1178, 610), SMALL, 600, name="Texto", at=33, n=9)
    s.bar("Línea", (740, 620, 1180, 630), 27, 9, "ltr")
    return t


def holiday():
    t = _p("holiday", "Título: fiesta con fecha", "Title: holiday with a date", 4.5, 8854, ["evento", "inclinado"])
    s = Piece3(t, 4.5, tilt=-4.0)
    s.word("SUMMER", (734, 350, 1184, 520), at=0, n=10)
    s.bar("Línea", (734, 528, 1184, 538), 12, 8, "ltr")
    s.word("HOLIDAY EVENT", (736, 546, 1184, 590), SMALL, 600, name="Texto", at=18, n=9)
    s.bar("Caja", (730, 600, 1190, 666), 30, 9, "ltr", fade=True)
    s.word("30.11.2026", (745, 606, 960, 660), SMALL, 600, WHITE, "Texto 2", at=33, n=9)
    return t


def designer():
    t = _p("disenador", "Título: cargo en caja y nombre", "Title: role box and name", 4.2, 8855, ["nombre", "inclinado"])
    s = Piece3(t, 4.2, tilt=-4.0)
    s.bar("Caja", (676, 424, 1136, 470), 0, 12, "ltr", fade=True)
    s.word("MOTION DESIGNER", (690, 428, 1000, 466), colour=WHITE, name="Texto", at=2, n=10)
    s.word("EUGENE FARLEY", (677, 478, 1299, 576), at=9, n=10)
    s.bar("Línea", (676, 586, 1134, 596), 15, 9, "ltr")
    return t


def life():
    t = _p("life", "Título: Life is life en un marco", "Title: Life is life in a frame", 5.0, 8856, ["marco"])
    s = Piece3(t, 5.0)
    # A thin line first, which turns into the frame (it goes as the frame draws).
    line = s.bar("Línea", (770, 532, 1150, 548), 0, 3, "mid")
    s.fade(line, lambda fr: 1.0 - k(fr, 3, 4))
    s.outline("Marco", rect_pts(770, 350, 1150, 730), 6, CYAN, at=2, n=6)
    s.word("LIFE", (837, 387, 1084, 531), at=6, n=8, slide=0)
    s.word("LIFE", (837, 554, 1084, 698), name="Título 2", at=18, n=8, slide=0)
    s.bar("Caja", (880, 480, 1000, 600), 30, 9, "pop")
    s.word("IS", (905, 505, 975, 575), SMALL, 600, WHITE, "Texto", at=36, n=8, slide=0)
    return t


def bubble():
    t = _p("globo", "Título: globo de diálogo", "Title: speech bubble", 4.9, 8857, ["globo", "marco"])
    s = Piece3(t, 4.9)
    pts = [(1250, 341), (1250, 750), (980, 750), (970, 796), (930, 750), (670, 750), (670, 341)]
    s.outline("Globo", pts, 6, CYAN, at=0, n=12)
    s.word("GREAT DAY", (727, 505, 1188, 607), colour=CYAN, name="Título 2", at=15, n=12, slide=60)
    s.word("TODAY", (727, 397, 1188, 493), SMALL, 600, name="Título", at=30, n=9, slide=0)
    s.word("FOR CHANGES", (727, 622, 1188, 666), SMALL, 600, name="Texto", at=33, n=9, slide=0)
    return t


def diamond():
    t = _p("rombo", "Título: evento en un rombo", "Title: event in a diamond", 4.9, 8858, ["rombo", "evento"])
    s = Piece3(t, 4.9)
    cx, cy, r = 940, 492, 200
    s.outline("Rombo", [(cx, cy + r), (cx + r, cy), (cx, cy - r), (cx - r, cy)], 6, TEAL, at=0, n=15)
    s.word("30", (928, 382, 993, 415), SMALL, 600, name="Texto", at=15, n=6, slide=0)
    s.word("OCT", (910, 429, 1012, 462), SMALL, 600, name="Texto 2", at=17, n=6, slide=0)
    tilt = Piece3.__new__(Piece3)
    tilt.__dict__.update(s.__dict__)
    tilt.tilt = -5.0
    tilt.word("CITY EVENT", (700, 473, 1223, 599), at=21, n=12, slide=80)
    tilt.word("TITLES", (790, 596, 1125, 690), SMALL, 600, name="Título 2", at=27, n=12, slide=80)
    return t


def design_success():
    t = _p("design-success", "Título: Design for success con círculo", "Title: Design for success with a circle", 4.7,
           8859, ["círculo"])
    s = Piece3(t, 4.7)
    s.blob("Círculo", "circle", (874, 454, 1046, 626), 0, 9)
    s.word("FOR", (905, 510, 1015, 570), colour=WHITE, name="Texto", at=6, n=8, slide=0)
    s.word("DESIGN", (607, 497, 862, 580), at=6, n=12, slide=-60)
    s.word("SUCCESS", (1058, 497, 1330, 580), name="Título 2", at=6, n=12, slide=60)
    return t


TEMPLATES = [name_box, name_role_above, name_lines, twenty_animation, twenty_square, name_offset_box, circle_name,
             triangle_name, two_triangles, epic_event, unique_pack, unique_animated, best_day, best_event, holiday,
             designer, life, bubble, diamond, design_success]
