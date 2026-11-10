"""Black and white kinetic titles, sixth TITLE set (2026-11-08): twenty-one of 35149534.mp4 (960×540 at 25 fps, laid
out at 1920×1080), a «titles pack 0.1»: heavy Montserrat and Bebas Neue words, outlined words, struck-through
words, frames, crossing lines, pills with dots and photo slots, on white or black (the background is its own
«Fondo» layer). Kit de YouTube › Tipografía; ids `tit6-*`, order 8900-. Study notes in
tienda/plantillas/estudio-35149534/NOTAS.md.

Moves (from 2 fps sheets): words type in or slide in one after another, lines and frames draw, boxes open, big
letters zoom down into place; each slide leaves with its entrance backwards. Not made: the two split screens that
show several pieces at once, the spinning 3D cube and the very short «01 compact» flash.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from scene import gradient, no_stroke
from templates_tit_c import k, rect_pts
from templates_tit_e import Piece5, solid

WHITE, BLACK, GREY = "#FFFFFF", "#000000", "#BDBDBD"
NAME = "Bebas Neue"
f6._FILES[("Montserrat", 900)] = "fonts.basic/fonts/montserrat/Montserrat-Black.ttf"
f6._FILES[("Montserrat", 800)] = "fonts.basic/fonts/montserrat/Montserrat-ExtraBold.ttf"
f6._FILES[("Montserrat", 700)] = "fonts.basic/fonts/montserrat/Montserrat-Bold.ttf"
f6._FILES[("Montserrat", 600)] = "fonts.basic/fonts/montserrat/Montserrat-SemiBold.ttf"
f6._FILES[("Montserrat", 500)] = "fonts.basic/fonts/montserrat/Montserrat-Medium.ttf"
M = "Montserrat"


def outline_layers(colour, width=4):
    return [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
            {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "outside",
             "opacity": 1.0, "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}]


def _p(id, es, en, order, tags=(), dur=3.8):
    return wide(f"tit6-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:tipografia", "tipografía", "blanco y negro", "cinético"] + list(tags),
                thumb_at=round(dur / 2, 1))


def slot(t, s, sample, box, at=0):
    clip = t.photo(t.track("video", "Foto"), sample, 0.0, s.dur, Box(*box), None, label="Tu foto")
    s.fade(clip, lambda fr: k(fr, at, 9))
    return clip


def pill(s, rect, colour, at, dots=True):
    x0, y0, x1, y1 = rect
    r = (y1 - y0) / 2
    pts = [(x0 + r, y0), (x1 - r, y0)]
    pts += [(x1 - r + r * math.sin(a / 12 * math.pi), y0 + r - r * math.cos(a / 12 * math.pi)) for a in range(1, 12)]
    pts += [(x1 - r, y1), (x0 + r, y1)]
    pts += [(x0 + r - r * math.sin(a / 12 * math.pi), y1 - r + r * math.cos(a / 12 * math.pi)) for a in range(1, 12)]
    s.outline("Píldora", pts, 4, colour, at=at, n=12)
    if dots:
        for i in range(3):
            cx = x0 + r + 10 + 52 * i
            s.outline(f"Punto {i + 1}", [(cx + 16 * math.cos(2 * math.pi * j / 16), (y0 + y1) / 2 +
                                          16 * math.sin(2 * math.pi * j / 16)) for j in range(16)], 3, colour,
                      at=at + 6 + 2 * i, n=6)


def you():
    t = _p("you", "Título: palabra enorme que se acerca", "Title: huge word zooming in", 8900, ["zoom"])
    s = Piece5(t, 3.8, WHITE)
    w = s.word("YOU", (500, 410, 1310, 700), M, 900, "#2A2A2A", at=0, n=1, slide=0,
               layers=[gradient([(0.0, "#555555"), (1.0, "#111111")], angle=90)])
    s.move(w, scale=lambda fr: 1 + 5 * (1 - k(fr, 0, 15)))
    s.shape("Raya", (1050, 700, 1310, 730), solid(BLACK), 15, 9, "ltr")
    s.word("AND GRAPHIC DESIGN", (1025, 790, 1350, 822), M, 800, BLACK, "Texto", at=18, n=9, slide=0)
    return t


def big_text():
    t = _p("big-text", "Título: número y texto con contorno", "Title: number and outlined words", 8901, ["contorno"])
    s = Piece5(t, 3.8, WHITE)
    s.word("0.1", (380, 475, 560, 600), M, 800, BLACK, "Número", at=0, n=9, slide=0)
    s.word("BIG TEXT", (720, 475, 1390, 610), M, 800, BLACK, at=6, n=12, slide=-60, layers=outline_layers(BLACK))
    s.shape("Barra", (1420, 360, 1440, 725), solid(BLACK), 3, 9, "ttb")
    s.word("UPDATE 0.1 TITLES PACK", (755, 612, 1205, 648), M, 800, BLACK, "Texto", at=15, n=9, slide=0)
    pill(s, (270, 775, 1520, 940), BLACK, 18)
    return t


def never_give_up():
    t = _p("never-give-up", "Título: frase sobre una franja de foto", "Title: phrase over a photo strip", 8902,
           ["foto"])
    s = Piece5(t, 3.8, BLACK)
    slot(t, s, "portrait-02", (770, 40, 375, 1000), 0)
    s.word("never give up!", (395, 460, 1535, 600), M, 900, WHITE, at=6, n=12, slide=-80)
    s.word("Always stand tall", (445, 592, 960, 646), M, 800, WHITE, "Texto", at=12, n=9, slide=0, align="left")
    s.word("Do not surrender to circumstances. You create them.", (600, 908, 1320, 936), M, 500, WHITE, "Texto 2",
           at=15, n=9, slide=0)
    for i in range(6):
        s.shape(f"Punto {i + 1}", (180 + 32 * i, 905, 196 + 32 * i, 921), solid(WHITE), 15 + i, 4, "pop",
                kind="ellipse")
    return t


def always_strive():
    t = _p("always-strive", "Título: frase partida con signo", "Title: split phrase with a sign", 8903,
           ["condensada"])
    s = Piece5(t, 3.8, BLACK)
    s.shape("Signo", (240, 240, 350, 825), solid(WHITE), 0, 12, "ttb")
    s.shape("Signo (punto)", (240, 850, 350, 925), solid(WHITE), 9, 6, "pop")
    for i, (line, x1, y0, y1) in enumerate((("ALWAYS", 780, 260, 390), ("STR", 575, 410, 540), ("IVE", 540, 550, 680),
                                            ("TO SUCCESS", 985, 690, 825))):
        s.word(line, (380, y0, x1, y1), NAME, 400, WHITE, f"Título {i + 1}" if i else "Título", at=6 + 3 * i, n=8,
               slide=-60, align="left")
    s.word("BELIEVE YOU CAN!", (390, 832, 770, 878), NAME, 400, WHITE, "Texto", at=18, n=8, align="left")
    s.word("Success is never accidental!", (390, 900, 930, 928), M, 600, WHITE, "Texto 2", at=21, n=8, align="left")
    return t


def be_strong():
    t = _p("be-strong", "Título: frase tachada en un marco", "Title: struck-through phrase in a frame", 8904,
           ["marco", "tachado"])
    s = Piece5(t, 3.8, BLACK)
    s.shape("Tachado", (560, 520, 1320, 534), solid(WHITE), 0, 9, "ltr")
    s.word("Be strong!", (595, 460, 1305, 590), M, 800, WHITE, at=6, n=12, slide=60)
    s.outline("Marco", [(1395, 360), (1395, 800), (520, 800), (520, 250), (1300, 250)], 6, WHITE, at=15, n=12,
              closed=False)
    return t


def create_ideas():
    t = _p("create-ideas", "Título: almohadilla e ideas nuevas", "Title: hash and new ideas", 8905, ["hashtag"])
    s = Piece5(t, 3.8, WHITE)
    s.word("#", (390, 420, 575, 645), M, 900, GREY, "Signo", at=9, n=9, slide=0)
    s.word("create", (590, 410, 1025, 530), M, 800, BLACK, at=0, n=9, slide=0, align="left")
    s.word("new ideas!", (590, 530, 1325, 660), M, 800, BLACK, "Título 2", at=3, n=9, slide=0, align="left")
    s.word("You must have ideas for life.", (600, 662, 1125, 700), M, 600, BLACK, "Texto", at=15, n=9, slide=0,
           align="left")
    return t


def health():
    t = _p("health", "Título: mitad negra con palabra repetida", "Title: black half with a repeated word", 8906,
           ["doble"])
    s = Piece5(t, 3.8, WHITE)
    s.shape("Mitad", (960, 0, 1920, 1080), solid(BLACK), 0, 12, "ttb")
    for i, (y0, y1) in enumerate(((60, 300), (720, 960))):
        pat = s.text("important is important", (700, y0, 2300, y1), M, 900, WHITE, f"Trama {i + 1}",
                     align="left", reveal=lambda fr: (960, 0, 1920, 1080), editable=False)
        s.fade(pat, lambda fr, i=i: 0.9 * k(fr, 6 + 3 * i, 9))
    s.word("Health is important", (1050, 485, 1805, 570), M, 800, WHITE, at=18, n=9, slide=60)
    s.outline("Etiqueta", rect_pts(305, 490, 680, 585), 6, BLACK, at=9, n=8)
    s.word("take care of yourself", (335, 518, 650, 558), M, 600, BLACK, "Texto", at=12, n=6, slide=0)
    s.outline("Casilla", rect_pts(395, 620, 585, 805), 6, BLACK, at=12, n=9)
    s.outline("Visto", [(445, 715), (480, 750), (540, 680)], 8, BLACK, at=18, n=6, closed=False)
    return t


def deal_science():
    t = _p("ciencia", "Título: frase en un marco con líneas en cruz", "Title: phrase in a frame, crossing lines", 8907,
           ["marco"])
    s = Piece5(t, 3.8, BLACK)
    s.outline("Línea", [(740, 160), (1180, 920)], 3, WHITE, at=0, n=12, closed=False)
    s.outline("Línea 2", [(1180, 160), (740, 920)], 3, WHITE, at=0, n=12, closed=False)
    s.shape("Caja", (525, 455, 1400, 620), solid(BLACK), 6, 6, "mid")
    s.outline("Marco", rect_pts(525, 455, 1400, 620), 5, WHITE, at=6, n=9)
    s.word("deal with science", (575, 480, 1350, 580), M, 800, WHITE, at=12, n=9, slide=0)
    s.word("expands ideas.", (830, 588, 1090, 612), M, 600, WHITE, "Texto", at=15, n=8, slide=0)
    return t


def big_visual():
    t = _p("big", "Título: palabra gigante con sombra", "Title: giant word with a shadow", 8908, ["sombra"])
    s = Piece5(t, 3.8, BLACK)
    s.shape("Panel", (0, 0, 1065, 1080), solid(WHITE), 0, 9, "ltr")
    s.word("big", (215, 215, 1040, 665), M, 900, GREY, "Título (sombra)", at=6, n=9, slide=0)
    s.word("big", (190, 195, 1015, 645), M, 900, BLACK, at=6, n=9, slide=0)
    s.word("and visual.", (665, 262, 1030, 328), M, 800, BLACK, "Texto", at=12, n=8, slide=0)
    s.shape("Barra", (205, 745, 1040, 870), solid(BLACK), 12, 9, "ltr")
    s.word("QUALITY DESIGNS", (240, 776, 900, 840), M, 800, WHITE, "Texto 2", at=18, n=8, slide=0)
    s.outline("Cuadro", rect_pts(1365, 420, 1565, 645), 5, WHITE, at=15, n=9)
    return t


def enjoy_design():
    t = _p("enjoy", "Título: palabra partida y cuadro", "Title: split word and a square", 8909, ["cuadro"])
    s = Piece5(t, 3.8, BLACK)
    for i, (line, x1, y0, y1) in enumerate((("DE", 995, 295, 445), ("SIG", 995, 455, 620), ("N-", 880, 645, 780))):
        s.word(line, (520, y0, x1, y1), NAME, 400, WHITE, f"Título {i + 1}" if i else "Título", at=3 * i, n=8,
               slide=0, align="left")
    box = s.shape("Cuadro", (1010, 280, 1470, 780), solid(WHITE), 6, 9, "pop")
    s.swing(box, 6, 12, deg=45, dx=0, dy=0)
    s.shape("Cuadro 2", (1085, 380, 1395, 680), solid(BLACK), 12, 6, "pop")
    s.word("en", (1180, 410, 1300, 520), M, 800, WHITE, "Texto", at=15, n=6, slide=0)
    s.word("joy", (1150, 530, 1330, 650), M, 800, WHITE, "Texto 2", at=15, n=6, slide=0)
    s.word("Graphic design", (520, 830, 700, 860), M, 500, WHITE, "Texto 3", at=18, n=8, slide=0, align="left")
    return t


def fashion():
    t = _p("fashion", "Título: tres fotos y caja de texto", "Title: three photos and a text box", 8910,
           ["foto", "moda"])
    s = Piece5(t, 3.8, WHITE)
    s.shape("Abajo", (0, 525, 1920, 1080), solid(BLACK), 0, 9, "btt")
    for i, x in enumerate((364, 708, 1154)):
        slot(t, s, f"fashion-0{i + 2}", (x, 250, 320, 540), 3 + 3 * i)
    s.shape("Caja", (364, 395, 1556, 684), solid(WHITE), 9, 9, "ltr")
    for i, (line, x1, y0, y1) in enumerate((("UNIVERSAL", 896, 404, 472), ("FASHION", 780, 482, 550),
                                            ("SENSE", 660, 562, 630))):
        s.word(line, (364, y0, x1, y1), M, 900, BLACK,
               f"Título {i + 1}" if i else "Título", at=12 + 2 * i, n=8, slide=0, align="left")
    s.word("GLOBAL FASHION UNDERSTANDING", (364, 640, 742, 662), M, 800, BLACK, "Texto", at=18, n=8, slide=0,
           align="left")
    return t


def typography():
    t = _p("typography", "Título: caja blanca sobre foto", "Title: white box over a photo", 8911, ["foto"])
    s = Piece5(t, 3.8, BLACK)
    slot(t, s, "portrait-03", (0, 0, 1920, 1080), 0)
    s.shape("Caja", (300, 255, 1625, 825), solid(WHITE), 6, 9, "mid")
    s.shape("Etiqueta", (400, 305, 635, 395), solid(BLACK), 12, 6, "ltr")
    s.word("Ver 0.1", (420, 325, 600, 375), M, 800, WHITE, "Texto", at=15, n=6, slide=0)
    s.word("typography", (535, 465, 1395, 605), M, 800, BLACK, at=15, n=9, slide=-60)
    s.word("Typography is a fundamental element of graphic art.", (560, 440, 1300, 460), M, 600, BLACK,
           "Texto 2", at=18, n=8, slide=0)
    return t


def art_always():
    t = _p("art-always", "Título: rayas, contorno y palabra grande", "Title: stripes, outline and a big word", 8912,
           ["rayas", "contorno"])
    s = Piece5(t, 3.8, BLACK)
    s.shape("Panel", (0, 0, 1920, 540), solid(WHITE), 0, 9, "ttb")
    for i in range(16):
        x = -60 + 130 * i
        s.shape(f"Raya {i + 1}", (x, 0, x + 60, 170), solid(BLACK), 3 + i * 0.5, 6, "ttb",
                path="M 40 0 L 100 0 L 60 100 L 0 100 Z")
    s.word("ART", (140, 200, 690, 340), M, 900, BLACK, "Texto", at=9, n=9, slide=0, align="left",
           layers=outline_layers(BLACK, 3))
    s.word("ALWAYS!", (140, 355, 1310, 515), M, 900, BLACK, at=6, n=9, slide=-60, align="left")
    s.word("GRAPHICS IS THE FOREMOST ART FORM.", (150, 555, 1590, 595), M, 900, WHITE, "Texto 2", at=15, n=9,
           slide=0, align="left")
    for i in range(3):
        s.word("Lorem ipsum dolor sit amet, consectetur adipiscing elit.", (150, 630 + 34 * i, 900, 654 + 34 * i),
               M, 500, WHITE, f"Texto {i + 3}", at=18 + i, n=8, slide=0, align="left")
    return t


def dynamism():
    t = _p("dynamism", "Título: palabra condensada en marco con cruz", "Title: condensed word in a frame, cross",
           8913, ["marco"])
    s = Piece5(t, 3.8, BLACK)
    s.outline("Línea", [(700, 190), (1270, 1000)], 3, WHITE, at=0, n=12, closed=False)
    s.outline("Línea 2", [(1270, 190), (700, 1000)], 3, WHITE, at=0, n=12, closed=False)
    s.shape("Caja", (595, 440, 1335, 655), solid(BLACK), 6, 6, "mid")
    s.outline("Marco", rect_pts(595, 440, 1335, 655), 7, WHITE, at=6, n=9)
    s.word("DYNAMISM", (625, 465, 1310, 630), NAME, 400, WHITE, at=12, n=9, slide=0)
    s.word("MOTION GRAPHIC DESIGN", (700, 672, 1225, 726), NAME, 400, WHITE, "Texto", at=15, n=8, slide=0)
    s.word("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod", (550, 980, 1380, 1000),
           M, 500, WHITE, "Texto 2", at=18, n=8, slide=0)
    return t


def look():
    t = _p("look", "Título: arcos y caja gris", "Title: arches and a grey box", 8914, ["arcos"])
    s = Piece5(t, 3.8, WHITE)
    s.shape("Arco", (-600, -200, 520, 1500), solid(BLACK), 0, 12, "pop", kind="ellipse")
    s.shape("Arco 2", (1500, -200, 2600, 1500), solid(BLACK), 0, 12, "pop", kind="ellipse")
    s.shape("Caja", (340, 395, 1580, 685), solid("#D0D0D0"), 6, 9, "mid")
    s.word("graphic", (355, 435, 780, 535), M, 800, BLACK, "Texto", at=12, n=8, slide=0)
    s.word("design", (355, 545, 780, 650), M, 800, BLACK, "Texto 2", at=14, n=8, slide=0)
    s.shape("Barra", (830, 420, 845, 670), solid(BLACK), 9, 6, "ttb")
    s.word("look", (905, 420, 1470, 670), M, 800, BLACK, at=9, n=9, slide=-60)
    s.outline("Etiqueta", rect_pts(860, 695, 1460, 775), 4, BLACK, at=18, n=8)
    s.word("/ modern compact design", (890, 715, 1430, 755), M, 600, BLACK, "Texto 3", at=21, n=8, slide=0)
    return t


def color_change():
    t = _p("color-change", "Título: palabra tachada grande", "Title: big struck-through word", 8915, ["tachado"])
    s = Piece5(t, 3.8, BLACK)
    s.word("Color", (235, 210, 1125, 500), M, 600, WHITE, at=0, n=9, slide=0, align="left")
    s.word("change", (160, 535, 1475, 860), M, 600, WHITE, "Título 2", at=6, n=12, slide=0, align="left")
    s.shape("Tachado", (0, 706, 1460, 726), solid(WHITE), 12, 9, "ltr")
    s.outline("Etiqueta", rect_pts(1135, 470, 1445, 520), 3, WHITE, at=15, n=8)
    s.word("NO PLUGINS REQUIRED", (1150, 482, 1430, 508), M, 600, WHITE, "Texto", at=18, n=6, slide=0)
    for i in range(6):
        s.shape(f"Punto {i + 1}", (180 + 30 * i, 880, 194 + 30 * i, 894), solid(WHITE), 15 + i, 4, "pop",
                kind="ellipse")
    return t


def corporate():
    t = _p("corporate", "Título: banda con marca sobre foto", "Title: band with a brand over a photo", 8916,
           ["foto"])
    s = Piece5(t, 3.8, BLACK)
    slot(t, s, "portrait-04", (0, 735, 1920, 345), 6)
    s.shape("Banda", (0, 0, 1920, 335), solid(WHITE), 0, 9, "ttb")
    pill(s, (372, 260, 1624, 440), WHITE, 9)
    s.word("corporate brand", (640, 500, 1280, 585), M, 600, WHITE, at=12, n=12, slide=0)
    s.shape("Raya", (800, 600, 1036, 610), solid(WHITE), 18, 6, "ltr")
    return t


def wonderful():
    t = _p("wonderful", "Título: tres palabras con líneas", "Title: three words with lines", 8917, ["líneas"])
    s = Piece5(t, 3.8, WHITE)
    s.shape("Línea", (0, 260, 1670, 275), solid(BLACK), 0, 12, "ltr")
    s.shape("Línea 2", (220, 800, 1920, 815), solid(BLACK), 3, 12, "rtl")
    for i, (line, x1, y0, y1) in enumerate((("WONDERFUL", 1060, 350, 470), ("AND", 560, 480, 600),
                                            ("AESTHETIC", 1040, 615, 735))):
        s.word(line, (100, y0, x1, y1), M, 900, BLACK, f"Título {i + 1}" if i else "Título", at=6 + 3 * i, n=9,
               slide=-60, align="left")
    s.shape("Globo", (1245, 420, 1460, 480), solid(BLACK), 12, 6, "ltr")
    s.word("01", (1420, 500, 1500, 560), M, 800, BLACK, "Número", at=15, n=6, slide=0)
    for i, x in enumerate((100, 820, 1500)):
        s.word("Lorem ipsum dolor sit amet,", (x, 880, x + 260, 902), M, 500, BLACK, f"Texto {i + 1}", at=18 + i,
               n=8, slide=0, align="left")
    return t


def awesome():
    t = _p("awesome", "Título: caja blanca y globo sobre foto", "Title: white box and a bubble over a photo", 8918,
           ["foto"])
    s = Piece5(t, 3.8, BLACK)
    slot(t, s, "portrait-01", (0, 0, 1920, 1080), 0)
    s.outline("Globo", [(560, 370), (560, 700), (500, 700), (500, 760), (450, 700), (310, 700), (310, 370)], 6, WHITE,
              at=6, n=12)
    s.word("A", (380, 470, 480, 600), M, 800, WHITE, "Texto", at=12, n=6, slide=0)
    s.shape("Línea", (950, 0, 956, 1080), solid(WHITE, 0.7), 3, 12, "ttb")
    s.shape("Caja", (600, 370, 1325, 705), solid(WHITE), 9, 9, "ltr")
    s.word("Awesome", (665, 470, 1240, 605), M, 800, BLACK, at=12, n=9, slide=0)
    s.word("FOR GREAT PRESENTATIONS...", (720, 1010, 1180, 1034), M, 800, WHITE, "Texto 2", at=15, n=8, slide=0)
    return t


def visuality():
    t = _p("visuality", "Título: tres líneas con palabras en contorno", "Title: three lines, outlined words", 8919,
           ["contorno"])
    s = Piece5(t, 3.8, BLACK)
    s.word("VISUALITY", (320, 390, 855, 470), M, 900, WHITE, at=0, n=9, slide=-60, align="left")
    s.word("TO LIFE", (320, 505, 690, 580), M, 900, WHITE, "Texto", at=4, n=9, slide=-60, align="left",
           layers=outline_layers("#9A9A9A", 2))
    s.word("IT", (320, 605, 420, 695), M, 900, WHITE, "Texto 2", at=8, n=9, slide=-60, align="left",
           layers=outline_layers("#9A9A9A", 2))
    s.word("PROVIDES", (440, 605, 960, 695), M, 900, WHITE, "Título 2", at=9, n=9, slide=-60, align="left")
    s.word("BEAUTY.", (985, 605, 1415, 695), M, 900, WHITE, "Texto 3", at=10, n=9, slide=-60, align="left",
           layers=outline_layers("#9A9A9A", 2))
    s.shape("Línea", (220, 765, 1000, 770), solid(WHITE), 12, 9, "ltr")
    s.word("Lorem ipsum dolor sit amet, consectetur adipiscing elit.", (320, 728, 1000, 752), M, 500, WHITE,
           "Texto 4", at=15, n=8, slide=0, align="left")
    pill(s, (1460, 80, 1795, 165), WHITE, 6)
    return t


TEMPLATES = [you, big_text, never_give_up, always_strive, be_strong, create_ideas, health, deal_science, big_visual,
             enjoy_design, fashion, typography, art_always, dynamism, look, color_change, corporate, wonderful, awesome,
             visuality]
