"""Yellow titles on black, fourth TITLE set (2026-11-08): the twenty of 1197825.mp4 (1920×1080 at 29.97 fps), the
same author's pack as 18722056 but its own designs: a golden gradient on boxes, frames, a pin, circles and a
triangle, white Montserrat / Bebas Neue / Oswald type, over a near-black background (its own «Fondo» layer). Laid
out where the reference has them. Kit de YouTube › Títulos con estilo; ids `tit4-*`, order 8860-. Study notes in
tienda/plantillas/estudio-1197825/NOTAS.md.

Moves as in templates_tit_c (fades with a short slide, lines from the middle, boxes opening, frames drawing, pops),
plus boxes that swing in turned; each piece leaves with its entrance backwards. The stock site's brand («#ENVATO»,
«ENVATO AUTUMN FEST», its leaf logo, «AFTER EFFECTS THEMPLATE», «AE CS5 AND ABOVE») is replaced by neutral words
and a logo slot with our play symbol; «ETHAN HUNT» (a film character) by an ordinary name.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box
from scene import gradient, keys, no_stroke
from templates_tit_b import Slide
from templates_tit_c import Piece3, k, rect_pts, _kit as _kit3  # noqa: F401

YEL, GOLD = "#FFF15A", "#EDB53C"
YG = [gradient([(0.0, YEL), (1.0, GOLD)], angle=0), no_stroke()]
INK = "#1E1400"
WHITE = "#FFFFFF"
DARK = "#0B0C0F"
f6._FILES[("Oswald", 300)] = "fonts.basic/fonts/oswald/Oswald-Light.ttf"
f6._FILES[("Oswald", 400)] = "fonts.basic/fonts/oswald/Oswald-Regular.ttf"
f6._FILES[("Montserrat", 300)] = "fonts.basic/fonts/montserrat/Montserrat-Regular.ttf"
NAME, SMALL = "Bebas Neue", "Montserrat"


class Piece4(Piece3):
    """A Piece3 on black, golden by default."""

    def __init__(self, t, dur, tilt=0.0, pivot=(960, 540)):
        Slide.__init__(self, t, dur)
        self.tilt, self.pivot = tilt, pivot
        self.background(DARK)

    def gbar(self, name, rect, at=0, n=9, way="ltr", fade=False):
        return self.bar(name, rect, at, n, way, layers=YG, fade=fade)

    def swing(self, clip, at, n=9, deg=-18.0, dx=-120.0, dy=60.0):
        """The clip swings in turned and lands flat (a box flung onto the screen)."""
        from llt_motion import frames_of
        # Its full size (a box made with "pop" starts at nothing): the widest keyframe, centred where it is.
        kf = max(zip(clip["x"]["keyframes"], clip["y"]["keyframes"], clip["width"]["keyframes"],
                     clip["height"]["keyframes"]), key=lambda q: q[2]["value"])
        w, h = kf[2]["value"], kf[3]["value"]
        x, y = kf[0]["value"], kf[1]["value"]
        xs, ys, rs = [], [], []
        for u in frames_of(self.dur):
            q = k(self.frame(u), at, n)
            xs.append((u, x + (1 - q) * dx, "linear"))
            ys.append((u, y + (1 - q) * dy, "linear"))
            rs.append((u, (1 - q) * deg, "linear"))
        clip["x"], clip["y"], clip["rotation"] = keys(xs), keys(ys), keys(rs)
        if "width" in clip:
            clip["width"], clip["height"] = keys([(0.0, w, "hold")]), keys([(0.0, h, "hold")])
        self.fade(clip, lambda fr: k(fr, at, max(1, n / 3)))
        return clip


def _p(id, es, en, dur, order, tags=()):
    from kit import wide
    return wide(f"tit4-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:titulos-estilo", "título", "amarillo", "negro"] + list(tags), thumb_at=round(dur / 2, 1))


def presents():
    t = _p("presents", "Título: presenta en un marco", "Title: presents in a frame", 4.6, 8860, ["marco"])
    s = Piece4(t, 4.6)
    s.outline("Marco", rect_pts(579, 479, 1341, 603), 6, YEL, at=0, n=12)
    s.word("EUGENE FARADAY", (599, 400, 1325, 455), SMALL, 600, WHITE, at=9, n=10, slide=0)
    s.word("PRESENTS", (759, 513, 1162, 567), SMALL, 300, WHITE, "Texto", at=30, n=10, slide=0)
    return t


def lower_triangle():
    t = _p("triangulo", "Título: número en un triángulo", "Title: number in a triangle", 4.6, 8861, ["triángulo"])
    s = Piece4(t, 4.6)
    s.outline("Triángulo", [(960, 768), (701, 428), (1219, 428)], 6, YEL, at=0, n=10)
    s.word("20", (853, 334, 1070, 546), NAME, 400, WHITE, "Número", at=9, n=9, slide=0)
    s.word("LOWER", (798, 567, 1127, 629), SMALL, 700, WHITE, "Título", at=21, n=8, slide=0)
    s.word("THIRDS", (797, 648, 1119, 710), SMALL, 700, WHITE, "Título 2", at=33, n=9, slide=0)
    return t


def location():
    t = _p("ubicacion", "Título: ubicación en un pin", "Title: location in a pin", 4.2, 8862, ["pin", "ubicación"])
    s = Piece4(t, 4.2)
    cx, cy, r, tip = 963, 492, 158, 756
    # The pin: an arc over the top and two straight sides down to the tip.
    a = math.acos(r / (tip - cy))
    pts = [(cx, tip)]
    for i in range(41):
        ang = math.pi / 2 + a + (2 * math.pi - 2 * a) * i / 40
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    s.outline("Pin", pts, 6, YEL, at=0, n=12)
    s.word("YOUR CURRENT", (731, 479, 1186, 550), "Oswald", 300, WHITE, at=6, n=12, slide=-60)
    s.word("LOCATION", (744, 568, 1175, 629), SMALL, 300, WHITE, "Título 2", at=9, n=12, slide=-60)
    return t


def producer():
    t = _p("productor", "Título: nombre en marco y etiqueta", "Title: name in a frame and a tag", 4.4, 8863,
           ["marco", "nombre"])
    s = Piece4(t, 4.4)
    s.outline("Marco", [(960, 479), (579, 479), (579, 603), (720, 603)], 6, YEL, at=12, n=12, closed=False)
    s.outline("Marco 2", [(960, 479), (1341, 479), (1341, 603), (1200, 603)], 6, YEL, at=12, n=12, closed=False)
    tag = s.gbar("Etiqueta", (720, 610, 1200, 674), 0, 1, "pop")
    s.swing(tag, 0, 12)
    lab = s.word("PRODUCER", (760, 618, 1160, 666), SMALL, 700, INK, "Texto", at=0, n=1, slide=0)
    s.swing(lab, 0, 12)
    s.word("OWEN DAVIAN", (618, 508, 1297, 573), SMALL, 600, WHITE, at=21, n=9, slide=0)
    return t


def name_box():
    t = _p("nombre-caja", "Título: nombre en caja amarilla", "Title: name in a yellow box", 4.6, 8864, ["nombre"])
    s = Piece4(t, 4.6)
    s.gbar("Caja", (580, 480, 1340, 600), 0, 9, "ltr", fade=True)
    s.word("JOHN MUSGRAVE", (596, 488, 1324, 592), "Oswald", 400, INK, at=3, n=9, slide=0)
    s.gbar("Línea", (580, 610, 1340, 620), 6, 9, "ltr")
    s.word("MOTION DESIGNER", (580, 631, 1030, 663), SMALL, 300, WHITE, "Texto", at=24, n=9, slide=-60, align="left")
    return t


def year():
    t = _p("anio", "Título: año con paralelogramo", "Title: year with a parallelogram", 4.0, 8865, ["año"])
    s = Piece4(t, 4.0)
    a = s.gbar("Forma", (672, 336, 900, 784), 0, 6, "pop", fade=True)
    a["shapeStyle"]["kind"] = "custom"
    a["shapeStyle"]["customPath"] = "M 0 0 L 55 0 L 100 100 L 45 100 Z"
    a["shapeStyle"]["customEvenOdd"] = False
    s.outline("Contorno", [(800, 336), (900, 336), (1000, 784), (900, 784)], 5, YEL, at=3, n=9)
    s.word("2016", (794, 356, 1363, 622), NAME, 400, WHITE, "Número", at=9, n=10, slide=-80)
    s.word("BEST YEAR", (796, 639, 1238, 694), SMALL, 600, WHITE, "Título", at=21, n=8, slide=-60)
    s.word("FOR A CHANGE", (798, 708, 1387, 763), SMALL, 600, WHITE, "Título 2", at=24, n=8, slide=-60)
    return t


def something_new():
    t = _p("algo-nuevo", "Título: caja con trama y texto", "Title: patterned box and words", 4.4, 8866, ["marco"])
    s = Piece4(t, 4.4)
    s.gbar("Caja", (574, 450, 968, 630), 0, 3, "pop", fade=True)
    # The box's pattern: the word over and over in rows, cut to the box (the reference runs them on a slant).
    for i, y in enumerate((464, 506, 548, 590)):
        pat = s.text("CREATE CREATE CREATE", (560 - 60 * (i % 2), y, 1000 - 60 * (i % 2), y + 30), NAME, 400, INK,
                     f"Trama {i + 1}", align="left", reveal=lambda fr: (574, 450, 968, 630), editable=False)
        s.fade(pat, lambda fr, i=i: k(fr, 3 + 2 * i, 9))
    s.outline("Marco", rect_pts(968, 453, 1345, 627, "tl"), 6, YEL, at=15, n=9)
    s.word("SOMETHING", (985, 486, 1318, 520), SMALL, 700, WHITE, "Texto", at=27, n=9)
    s.word("REALLY NEW", (985, 536, 1318, 596), NAME, 400, WHITE, at=30, n=9)
    return t


def festival_info():
    t = _p("festival-info", "Título: fecha y datos del festival", "Title: festival date and details", 4.4, 8867,
           ["evento", "fecha"])
    s = Piece4(t, 4.4)
    s.gbar("Fecha", (1010, 398, 1164, 466), 0, 6, "pop")
    s.word("16", (1064, 406, 1110, 458), NAME, 400, INK, "Número", at=3, n=6, slide=0)
    s.word("SEPTEMBER", (682, 398, 990, 466), NAME, 400, YEL, at=6, n=12, slide=60)
    s.gbar("Línea", (682, 660, 1164, 668), 6, 9, "ltr")
    s.word("AUTUMN MUSIC FEST", (682, 490, 1423, 534), SMALL, 700, WHITE, "Título 2", at=24, n=9, align="left")
    s.word("IN CENTRAL PARK", (682, 556, 1252, 600), SMALL, 700, WHITE, "Título 3", at=30, n=9, align="left")
    s.word("MORE INFORMATION AND TICKETS AT YOURSITE.COM", (682, 624, 1344, 637), SMALL, 500, WHITE, "Texto",
           at=36, n=9, align="left")
    return t


def tag_name():
    t = _p("etiqueta-nombre", "Título: etiqueta, nombre y cargo", "Title: tag, name and role", 4.3, 8868, ["nombre"])
    s = Piece4(t, 4.3)
    s.gbar("Etiqueta", (694, 415, 1074, 490), 0, 12, "ltr")
    s.word("#CREATOR", (775, 430, 1050, 478), NAME, 400, INK, "Texto", at=6, n=9, slide=0)
    s.gbar("Línea", (694, 576, 1074, 586), 9, 6, "ltr")
    s.word("ETHAN HAYES", (694, 512, 1111, 554), SMALL, 600, WHITE, at=12, n=12, slide=-80, align="left")
    s.word("VIDEO ENGINEER", (694, 607, 1018, 632), SMALL, 300, WHITE, "Texto 2", at=15, n=9, align="left")
    return t


def logo_name():
    t = _p("logo-nombre", "Título: logo, etiqueta y nombre", "Title: logo, tag and name", 4.8, 8869,
           ["logo", "nombre"])
    s = Piece4(t, 4.8)
    s.gbar("Línea", (813, 470, 1192, 478), 0, 9, "mid")
    s.gbar("Etiqueta", (813, 415, 1192, 470), 12, 6, "ltr")
    s.word("#CREATOR", (912, 431, 1165, 462), NAME, 400, INK, "Texto", at=12, n=6, slide=0)
    s.word("LUTHER STICKELL", (813, 507, 1381, 559), SMALL, 600, WHITE, at=15, n=9, slide=0, align="left")
    s.word("TECHNO BLOGGER", (813, 603, 1179, 634), SMALL, 300, WHITE, "Texto 2", at=18, n=9, slide=0, align="left")
    frame = s.outline("Marco", rect_pts(578, 420, 787, 628, "tl"), 6, YEL, at=33, n=9)
    logo = t.photo(t.track("video", "Logo"), "logo-flip", 0.0, 4.8, Box(612, 454, 141, 141), None, label="Tu logo",
                   brandRole="logo")
    s.fade(logo, lambda fr: k(fr, 36, 9))
    del frame
    return t


def name_tags():
    t = _p("nombre-cajas", "Título: nombre y cargo en cajas", "Title: name and role in boxes", 3.8, 8870, ["nombre"])
    s = Piece4(t, 3.8)
    a = s.gbar("Caja", (628, 485, 1292, 594), 0, 1, "pop")
    s.swing(a, 0, 12, deg=-12, dx=-80, dy=-60)
    b = s.gbar("Caja 2", (886, 606, 1293, 670), 0, 1, "pop")
    s.swing(b, 2, 12, deg=-12, dx=-60, dy=-80)
    for clip, at in ((s.word("EUGENE FARADAY", (644, 491, 1276, 588), "Oswald", 400, INK, at=0, n=1, slide=0), 0),
                     (s.word("MOTION DESIGNER", (910, 620, 1270, 656), SMALL, 700, INK, "Texto", at=0, n=1, slide=0),
                      2)):
        s.swing(clip, at, 12, deg=-12, dx=-70, dy=-70)
    return t


def twenty_titles():
    t = _p("twenty", "Título: Twenty creative titles", "Title: Twenty creative titles", 4.8, 8871, ["número"])
    s = Piece4(t, 4.8)
    s.gbar("Línea", (743, 765, 1176, 774), 0, 9, "mid")
    s.word("TITLES", (743, 528, 1172, 682), NAME, 400, YEL, "Título 3", at=6, n=12, slide=0,
           layers=[gradient([(0.0, YEL), (1.0, GOLD)], angle=90)])
    s.gbar("Línea 2", (743, 703, 1176, 712), 9, 9, "mid")
    s.word("EDIT IN FLIP STUDIO", (743, 725, 1176, 753), SMALL, 300, WHITE, "Texto", at=12, n=9, slide=0)
    s.word("CREATIVE", (743, 445, 1175, 507), SMALL, 600, WHITE, "Título 2", at=15, n=9, slide=0)
    s.word("TWENTY", (745, 304, 1174, 422), NAME, 400, YEL, "Título", at=21, n=12, slide=0,
           layers=[gradient([(0.0, YEL), (1.0, GOLD)], angle=90)])
    return t


def dont_stop():
    t = _p("dont-stop", "Título: frase en un círculo", "Title: phrase in a circle", 4.4, 8872, ["círculo"])
    s = Piece4(t, 4.4)
    cx, cy, r = 960, 540, 258
    s.outline("Círculo", [(cx + r * math.cos(math.pi / 2 + 2 * math.pi * i / 64),
                           cy + r * math.sin(math.pi / 2 + 2 * math.pi * i / 64)) for i in range(64)], 7, YEL,
              at=3, n=14)
    box = s.gbar("Caja", (795, 490, 1125, 590), 0, 1, "pop")
    s.swing(box, 0, 9, deg=-20, dx=0, dy=-30)
    stop = s.word("STOP", (812, 496, 1110, 584), SMALL, 800, INK, at=0, n=1, slide=0)
    s.swing(stop, 0, 9, deg=-20, dx=0, dy=-30)
    s.word("DONT", (789, 393, 1132, 479), SMALL, 300, WHITE, "Título 2", at=18, n=8, slide=0)
    s.word("DANCING", (790, 601, 1132, 654), SMALL, 300, WHITE, "Título 3", at=18, n=8, slide=0)
    return t


def information():
    t = _p("informacion", "Título: información en un círculo", "Title: information in a circle", 4.1, 8873,
           ["círculo"])
    s = Piece4(t, 4.1)
    cx, cy, r = 960, 540, 258
    s.outline("Círculo", [(cx + r * math.cos(math.pi * 0.75 + 2 * math.pi * i / 64),
                           cy + r * math.sin(math.pi * 0.75 + 2 * math.pi * i / 64)) for i in range(64)], 7, YEL,
              at=0, n=12)
    s.gbar("Etiqueta", (788, 452, 1112, 506), 21, 15, "ltr")
    s.word("INFORMATION", (800, 460, 1100, 498), SMALL, 700, INK, "Título", at=30, n=6, slide=0)
    lines = ["LOREM IPSUM DOLOR SIT", "AMET, VIX STET DOLOR", "SEMPER ID, NISL LAUDEM", "MANDAMUS EAM EX, DICIT",
             "MOLLIS SENSERIT EU MEL."]
    for i, line in enumerate(lines):
        y = 517 + 29 * i
        s.word(line, (792, y, 1104, y + 18), SMALL, 400, WHITE, f"Texto {i + 1}", at=30 + 2 * i, n=8, slide=0,
               align="left")
    return t


def easy_edit():
    t = _p("facil", "Título: texto y barra amarilla", "Title: words and a yellow bar", 4.1, 8874, ["barra"])
    s = Piece4(t, 4.1)
    s.word("EASY CUSTOMIZATION", (568, 484, 1080, 538), NAME, 400, YEL, at=0, n=12, slide=0)
    s.gbar("Barra", (518, 550, 1402, 610), 0, 15, "ltr", fade=True)
    s.word("EASY TO EDIT TEMPLATE", (538, 562, 900, 598), SMALL, 700, INK, "Texto", at=9, n=9, slide=0, align="left")
    return t


def simple_design():
    t = _p("simple-design", "Título: dos cajas que caen", "Title: two boxes thrown in", 3.4, 8875, ["cajas"])
    s = Piece4(t, 3.4)
    for rect, text, ink, font, w, at, name in (((678, 383, 1078, 538), "SIMPLE", (694, 393, 1062, 528), NAME, 400, 0,
                                                "Título"),
                                               ((838, 548, 1238, 667), "DESIGN", (860, 560, 1216, 655), SMALL, 700, 6,
                                                "Título 2")):
        b = s.gbar(f"Caja {name}", rect, 0, 1, "pop")
        s.swing(b, at, 9, deg=-15, dx=-40, dy=60)
        c = s.word(text, ink, font, w, INK, name, at=0, n=1, slide=0)
        s.swing(c, at, 9, deg=-15, dx=-40, dy=60)
    return t


def autumn_event():
    t = _p("autumn-event", "Título: palabra en caja y debajo", "Title: boxed word and one below", 4.8, 8876,
           ["evento"])
    s = Piece4(t, 4.8)
    s.gbar("Caja", (678, 383, 1078, 538), 0, 15, "ltr")
    s.word("AUTUMN", (694, 393, 1062, 528), NAME, 400, INK, at=3, n=12, slide=0)
    s.word("EVENT", (869, 556, 1214, 626), SMALL, 700, WHITE, "Título 2", at=27, n=9, slide=-80)
    s.gbar("Línea", (868, 644, 1210, 654), 30, 6, "rtl")
    return t


def art_festival():
    t = _p("art-festival", "Título: arte, caja y festival", "Title: art, a box and festival", 4.8, 8877, ["evento"])
    s = Piece4(t, 4.8)
    s.gbar("Caja", (650, 462, 1155, 618), 0, 12, "mid")
    s.word("AUTUMN", (665, 472, 1140, 608), NAME, 400, INK, at=3, n=12, slide=0)
    s.gbar("Línea", (1160, 608, 1270, 618), 12, 6, "ltr")
    s.gbar("Línea 2", (650, 344, 842, 354), 15, 6, "ltr")
    s.word("ART", (648, 377, 837, 437), SMALL, 700, WHITE, "Título 2", at=15, n=8, slide=0)
    s.word("FESTIVAL", (908, 645, 1293, 701), SMALL, 700, WHITE, "Título 3", at=30, n=8, slide=0)
    s.gbar("Línea 3", (928, 724, 1270, 734), 30, 6, "ltr")
    return t


def date_boxes():
    t = _p("fecha-cajas", "Título: fecha y hora en cajas", "Title: date and time in boxes", 4.4, 8878,
           ["evento", "fecha"])
    s = Piece4(t, 4.4)
    s.gbar("Caja", (540, 422, 949, 536), 0, 9, "ltr", fade=True)
    s.word("SEPTEMBER 16", (556, 432, 935, 526), NAME, 400, INK, "Texto", at=0, n=9, slide=0)
    s.gbar("Caja 2", (734, 542, 949, 656), 3, 9, "ltr", fade=True)
    s.word("19:30", (750, 552, 935, 646), NAME, 400, INK, "Texto 2", at=3, n=9, slide=0)
    for i, (text, ink) in enumerate((("MUSIC", (960, 424, 1189, 493)), ("AUTUMN FEST", (957, 504, 1381, 573)),
                                     ("IN CENTRAL PARK", (960, 584, 1496, 653)))):
        s.text(text, ink, NAME, 400, WHITE, ["Título", "Título 2", "Título 3"][i], align="left",
               reveal=lambda fr: (952, 380, 1600, 700),
               shift=lambda fr, a=27 + 3 * i: (-(1 - k(fr, a, 12)) * 520, 0.0))
    return t


def speakers():
    t = _p("speakers", "Título: hashtag en caja grande", "Title: hashtag in a big box", 3.8, 8879, ["evento"])
    s = Piece4(t, 3.8)
    s.gbar("Caja", (600, 467, 1329, 612), 0, 9, "ltr", fade=True)
    s.word("#CREATORS", (780, 475, 1315, 604), NAME, 400, INK, at=0, n=9, slide=0)
    s.word("BEST SPEAKERS AT THE", (600, 384, 1325, 455), NAME, 400, WHITE, "Título 2", at=15, n=9, slide=0)
    s.word("CREATORS AUTUMN FEST", (600, 620, 1328, 696), NAME, 400, WHITE, "Título 3", at=24, n=9, slide=0)
    s.gbar("Línea", (600, 705, 1329, 714), 24, 9, "ltr")
    return t


TEMPLATES = [presents, lower_triangle, location, producer, name_box, year, something_new, festival_info, tag_name,
             logo_name, name_tags, twenty_titles, dont_stop, information, easy_edit, simple_design, autumn_event,
             art_festival, date_boxes, speakers]
