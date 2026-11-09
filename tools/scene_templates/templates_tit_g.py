"""Colourful kinetic titles, seventh TITLE set (2026-11-08): twenty-two of 36160725.mp4 (960×540 at 25 fps, laid
out at 1920×1080), a «titles pack 0.2», the colour sibling of 35149534 (`templates_tit_f`): heavy Montserrat,
Bebas Neue and slab or serif words, stripes, glitch copies, diagonal word walls, coloured boxes with shadows and
photo slots. Kit de YouTube › Tipografía; ids `tit7-*`, order 8920-. Study notes in
tienda/plantillas/estudio-36160725/NOTAS.md.

Not made: the opening and middle split screens (several pieces at once), the spinning word globe and the closing
«titles pack 0.2» card.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import Box, wide
from scene import gradient
from templates_tit_c import k, rect_pts
from templates_tit_e import Piece5, solid
from templates_tit_f import outline_layers, slot

WHITE, BLACK, RED, BLUE, YELLOW = "#FFFFFF", "#000000", "#F23A1D", "#3FA9E8", "#FFD21F"
NAME, M, SLAB, SERIF = "Bebas Neue", "Montserrat", "Roboto Slab", "DM Serif Display"
f6._FILES[(SLAB, 900)] = "fonts.extra/fonts/robotoslab/RobotoSlab-Black.ttf"
f6._FILES[(SERIF, 400)] = "fonts.extra/fonts/dmserifdisplay/DMSerifDisplay-Regular.ttf"


def shadow(colour, dx, dy, blur=0, alpha=1.0):
    return {"id": "shadow", "kind": "shadow", "enabled": True,
            "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()},
            "offsetX": dx, "offsetY": dy, "blur": blur, "opacity": alpha}


def fill(colour):
    return {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
            "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}


def _p(id, es, en, order, tags=(), dur=3.8):
    return wide(f"tit7-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:tipografia", "tipografía", "colores", "cinético"] + list(tags), thumb_at=round(dur / 2, 1))


def dots(s, x, y, colour, at, n=7, step=22, size=10):
    for i in range(n):
        s.shape(f"Punto {i + 1}", (x + step * i, y, x + step * i + size, y + size), solid(colour), at + i * 0.6, 4,
                "pop", kind="ellipse")


def wall(s, text, rows, colour, deg, at, size=300, alpha=1.0, name="Trama", layers=None):
    """Rows of a huge word, turned by deg about the centre, sliding in turn left and right."""
    def make(p):
        for i, y in enumerate(rows):
            way = 1 if i % 2 == 0 else -1
            clip = p.text(f"{text} {text} {text}", (-900, y, 2820, y + size), M, 900, colour, f"{name} {i + 1}",
                          layers=layers, editable=False,
                          shift=lambda fr, w=way: (w * (1 - k(fr, at + 2 * i, 18)) * 500, 0.0))
            p.fade(clip, lambda fr, i=i: alpha * k(fr, at + 2 * i, 9))
            p._turned(clip)
    s.turned(deg, make)


def love():
    t = _p("love", "Título: palabra enorme sobre foto", "Title: huge word over a photo", 8920, ["foto"])
    s = Piece5(t, 3.8, BLACK)
    slot(t, s, "fx-face-02", (0, 0, 1920, 1080), 0)
    s.shape("Tinte", (0, 0, 1920, 1080), solid("#E8365D", 0.45), 0, 9, "pop", fade=True)
    w = s.word("LOVE", (980, 250, 1760, 520), M, 900, WHITE, at=6, n=9, slide=0)
    s.move(w, scale=lambda fr: 1 + 0.6 * (1 - k(fr, 6, 12)))
    s.word("GRAPHIC DESIGN!", (1010, 520, 1730, 630), NAME, 400, WHITE, "Texto", at=12, n=9, slide=-60)
    s.word("TITLES PACK", (1620, 980, 1840, 1000), M, 800, WHITE, "Texto 2", at=15, n=8, slide=0)
    dots(s, 90, 980, WHITE, 15)
    return t


def scene():
    t = _p("scene", "Título: rayas, foto y número", "Title: stripes, a photo and a number", 8921, ["rayas", "foto"])
    s = Piece5(t, 3.8, WHITE)
    stripes = " ".join(f"M {i * 5.2:.2f} 0 L {i * 5.2 + 2.6:.2f} 0 L {i * 5.2 + 2.6:.2f} 100 L {i * 5.2:.2f} 100 Z"
                       for i in range(20))
    s.shape("Rayas", (0, 0, 1920, 1080), solid(BLACK), 0, 12, "ttb", path=stripes)
    s.shape("Panel", (0, 170, 1920, 910), solid(WHITE), 6, 9, "mid")
    slot(t, s, "fx-cyber-02", (1150, 210, 680, 660), 9)
    s.word("0.1", (1190, 330, 1790, 760), M, 900, WHITE, at=12, n=9, slide=0)
    s.word("SCENE 0.1", (170, 420, 1080, 560), M, 900, BLACK, "Texto", at=9, n=9, slide=-60,
           layers=outline_layers("#BBBBBB", 3))
    s.word("UPDATE 0.1 TITLES PACK", (420, 580, 1060, 620), M, 800, BLACK, "Texto 2", at=15, n=8, slide=0)
    return t


def never_give_up():
    t = _p("never-give-up", "Título: cuatro fotos en escalera y frase", "Title: four stepped photos and a phrase",
           8922, ["foto"])
    s = Piece5(t, 3.8, WHITE)
    for i in range(4):
        slot(t, s, f"portrait-0{i + 5}", (90 + 330 * i, 110 + 40 * i, 300, 640), 2 * i)
    s.word("never give up", (60, 300, 1790, 520), M, 900, WHITE, at=9, n=12, slide=-120,
           layers=[shadow(BLACK, 0, 6, 14, 0.6), fill(WHITE)])
    s.shape("Caja", (1280, 600, 1890, 740), solid(BLACK), 12, 9, "ltr")
    s.word("never give up!", (1320, 620, 1860, 715), M, 900, WHITE, "Texto", at=15, n=9, slide=-40)
    s.shape("Caja 2", (1490, 760, 1890, 840), solid(BLACK), 15, 9, "ltr")
    s.word("Always stand tall.", (1515, 780, 1865, 820), M, 800, WHITE, "Texto 2", at=18, n=8, slide=0)
    return t


def always_strive():
    t = _p("always-strive", "Título: frase con sombra roja y signo", "Title: phrase with a red shadow and a sign",
           8923, ["sombra"])
    s = Piece5(t, 3.8, WHITE)
    s.shape("Signo (caja)", (330, 300, 560, 640), solid(BLACK), 0, 9, "ttb")
    s.word("!", (400, 340, 490, 600), M, 900, WHITE, "Signo", at=6, n=8, slide=0)
    red = [shadow(RED, 8, 8), fill(BLACK)]
    for i, (line, x1, y0, y1) in enumerate((("ALWAYS", 1250, 300, 410), ("STRIVE", 1210, 410, 520),
                                            ("TO SUCCESS", 1580, 520, 640))):
        s.word(line, (590, y0, x1, y1), "Kanit", 700, BLACK, f"Título {i + 1}" if i else "Título", at=6 + 3 * i,
               n=9, slide=-80, align="left", layers=red)
    s.word("BELIEVE YOU CAN!", (600, 660, 900, 690), M, 900, BLACK, "Texto", at=15, n=8, slide=0, align="left")
    s.word("Success is never accidental!", (600, 702, 860, 718), M, 600, BLACK, "Texto 2", at=18, n=8, slide=0,
           align="left")
    s.outline("Etiqueta", rect_pts(1640, 260, 1700, 680), 5, BLACK, at=12, n=9)
    lab = s.word("BELIEVE YOU CAN!", (1460, 455, 1880, 485), M, 800, BLACK, "Texto 3", at=15, n=8, slide=0)
    s.turn(lab, -90)
    return t


def newest():
    t = _p("newest", "Título: palabra en contorno con barra verde", "Title: outlined word with a green bar", 8924,
           ["contorno"])
    s = Piece5(t, 3.8, BLACK)
    s.shape("Línea", (0, 538, 1920, 542), solid(WHITE), 0, 12, "ltr")
    s.word("Newest", (170, 380, 1720, 700), M, 500, WHITE, at=6, n=12, slide=-80, layers=outline_layers(WHITE, 3))
    s.shape("Barra", (250, 520, 1100, 580), solid("#1ED52A"), 12, 9, "ltr")
    dots(s, 90, 980, WHITE, 15)
    return t


def dynamic():
    t = _p("dynamic", "Título: dos líneas en un marco abierto", "Title: two lines in an open frame", 8925, ["marco"])
    s = Piece5(t, 3.8, WHITE)
    s.outline("Marco", [(1320, 320), (1440, 320), (1440, 760), (480, 760), (480, 320), (1240, 320)], 10, BLACK,
              at=0, n=15, closed=False)
    s.word("dynamic", (560, 380, 1010, 490), M, 800, BLACK, at=6, n=9, slide=-40, align="left")
    s.word("title concept", (560, 480, 1360, 600), M, 800, BLACK, "Título 2", at=9, n=9, slide=-40, align="left")
    s.word("You must have ideas for life.", (560, 610, 940, 640), M, 500, BLACK, "Texto", at=15, n=8, slide=0,
           align="left")
    lab = s.word("Always have new and beautiful projects.", (1310, 528, 1630, 548), M, 500, BLACK, "Texto 2", at=15,
                 n=8, slide=0)
    s.turn(lab, 90)
    return t


def health_wall():
    t = _p("health-wall", "Título: muro de palabras en diagonal", "Title: diagonal wall of words", 8926,
           ["diagonal"])
    s = Piece5(t, 3.8, BLACK)
    wall(s, "HEALTH IS IMPORTANT", (-160, 160, 480, 800, 1120), WHITE, -35, 0)
    return t


def health_box():
    t = _p("health-box", "Título: cuadro de colores entre palabras", "Title: colour square between words", 8927,
           ["cuadro"])
    s = Piece5(t, 3.8, BLACK)
    for i, y in enumerate((270, 560)):
        row = s.text("HEALTH IS IMPORTANT HEALTH", (-700, y, 2700, y + 250), M, 900, WHITE, f"Trama {i + 1}",
                     editable=False, shift=lambda fr, i=i: ((1 if i else -1) * (1 - k(fr, 0, 18)) * 400, 0.0))
        s.fade(row, lambda fr: k(fr, 0, 9))
    s.shape("Cuadro", (690, 250, 1200, 830), [gradient([(0.0, YELLOW), (1.0, "#2F6BFF")], angle=135)], 6, 9, "pop")
    s.shape("Cuadro (marco)", (720, 280, 1170, 800), solid(BLACK), 9, 9, "pop")
    inner = s.turned(-45, lambda p: p.word("IMPORTANT", (700, 470, 1190, 610), M, 900, YELLOW, "Texto", at=12, n=9,
                                           slide=0))
    del inner
    s.shape("Caja", (1260, 470, 1760, 610), solid(BLACK), 12, 6, "ltr")
    s.word("HEALTH IS IMPORTANT", (1290, 495, 1730, 535), M, 900, WHITE, "Texto 2", at=15, n=8, slide=0)
    s.word("take care of yourself", (1360, 545, 1660, 575), M, 500, WHITE, "Texto 3", at=18, n=8, slide=0,
           italic=True)
    return t


def science():
    t = _p("ciencia", "Título: caja negra con letra de molde", "Title: black box with slab letters", 8928, ["slab"])
    s = Piece5(t, 3.8, WHITE)
    s.shape("Caja", (330, 260, 870, 780), solid(BLACK), 0, 9, "ttb")
    for i, (line, x1, y0, y1) in enumerate((("deal", 640, 300, 440), ("with", 640, 440, 580),
                                            ("science", 840, 580, 720))):
        s.word(line, (370, y0, x1, y1), SLAB, 900, WHITE, f"Título {i + 1}" if i else "Título", at=6 + 3 * i, n=9,
               slide=-40, align="left")
    s.shape("Raya", (370, 735, 560, 748), solid(WHITE), 15, 6, "ltr")
    s.word("Science expands ideas.", (380, 800, 860, 840), M, 800, BLACK, "Texto", at=15, n=9, slide=0, align="left")
    s.outline("Casilla", rect_pts(1150, 545, 1240, 635), 5, BLACK, at=12, n=9)
    s.outline("Visto", [(1172, 590), (1192, 610), (1222, 570)], 6, BLACK, at=18, n=6, closed=False)
    dots(s, 90, 120, "#2F6BFF", 6)
    dots(s, 90, 950, RED, 9)
    return t


def enjoy():
    t = _p("enjoy", "Título: cuadro negro y palabra partida", "Title: black square and a split word", 8929,
           ["cuadro"])
    s = Piece5(t, 3.8, "#1A1A1A")
    s.shape("Tarjeta", (180, 120, 1740, 960), solid(WHITE), 0, 9, "mid")
    box = s.shape("Cuadro", (560, 290, 1000, 760), solid(BLACK), 6, 9, "pop")
    s.swing(box, 6, 12, deg=45, dx=0, dy=0)
    s.word("en", (880, 310, 970, 370), M, 900, WHITE, "Texto", at=12, n=6, slide=0)
    s.word("joy", (870, 365, 980, 435), M, 900, WHITE, "Texto 2", at=12, n=6, slide=0)
    for i, (line, y0, y1) in enumerate((("DE", 300, 450), ("SIG", 450, 610), ("N", 610, 760))):
        s.word(line, (1020, y0, 1290 if i != 2 else 1110, y1), M, 900, BLACK, f"Título {i + 1}" if i else "Título",
               at=9 + 2 * i, n=8, slide=-60, align="left")
    s.word("Graphic design", (570, 790, 760, 815), M, 600, BLACK, "Texto 3", at=15, n=8, slide=0, align="left")
    return t


def big():
    t = _p("big", "Título: caja con sombra azul y rombos", "Title: box with a blue shadow and diamonds", 8930,
           ["rombos"])
    s = Piece5(t, 3.8, "#E6E6E6")
    s.shape("Sombra", (835, 365, 1145, 655), solid("#2F4BFF"), 3, 9, "pop")
    s.shape("Caja", (800, 330, 1110, 620), solid(BLACK), 0, 9, "pop")
    s.word("BIG", (840, 410, 1070, 540), M, 900, WHITE, at=9, n=9, slide=0)
    for i, (x, colour) in enumerate(((560, "#2F4BFF"), (1300, "#F2384A"))):
        d = s.shape(f"Rombo {i + 1}", (x, 410, x + 130, 540), solid(colour), 12 + 2 * i, 9, "pop")
        s.turn(d, 45)
        s.word("BIG", (x + 30, 455, x + 100, 495), M, 900, WHITE, f"Texto {i + 1}", at=15 + 2 * i, n=8, slide=0)
    dots(s, 90, 840, "#2F4BFF", 15)
    s.word("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore.",
           (360, 1000, 1560, 1016), M, 700, BLACK, "Texto 3", at=18, n=8, slide=0)
    return t


def fashion():
    t = _p("fashion", "Título: palabra en contorno sobre foto", "Title: outlined word over a photo", 8931,
           ["foto", "moda"])
    s = Piece5(t, 3.8, BLACK)
    slot(t, s, "fx-car-01", (160, 160, 1600, 760), 0)
    s.shape("Oscuro", (160, 160, 1760, 920), solid(BLACK, 0.35), 0, 9, "pop", fade=True)
    s.word("FASHION", (380, 300, 1780, 620), M, 900, WHITE, at=6, n=12, slide=-120, layers=outline_layers(WHITE, 4))
    s.word("SENSE", (380, 640, 1180, 900), M, 900, WHITE, "Título 2", at=9, n=12, slide=-120,
           layers=outline_layers(WHITE, 4))
    s.shape("Caja", (0, 420, 640, 640), solid(WHITE), 12, 9, "ltr")
    s.word("UNIVERSAL", (60, 495, 580, 565), M, 900, "#F5A300", "Texto", at=15, n=9, slide=-40)
    dots(s, 90, 1000, WHITE, 15)
    return t


def typography():
    t = _p("typography", "Título: tarjeta rosa y letras alrededor", "Title: pink card with letters around", 8932,
           ["foto"])
    s = Piece5(t, 3.8, WHITE)
    for i, (x, colour) in enumerate(((60, "#E8365D"), (1740, "#1B1F4A"))):
        col = s.text("TYPOGRAPHY", (x - 600, 470, x + 720, 610), M, 900, colour, f"Trama {i + 1}", editable=False,
                     shift=lambda fr, i=i: (0.0, (1 if i else -1) * (1 - k(fr, 0, 18)) * 400))
        s.turn(col, 90 if i else -90)
        s.fade(col, lambda fr: k(fr, 0, 9))
    for i, (y, colour) in enumerate(((-30, "#1B1F4A"), (960, "#E8365D"))):
        row = s.text("TYPOGRAPHY TYPOGRAPHY", (-200, y, 2100, y + 150), M, 900, colour, f"Trama {i + 3}",
                     editable=False, shift=lambda fr, i=i: ((1 if i else -1) * (1 - k(fr, 0, 18)) * 400, 0.0))
        s.fade(row, lambda fr: k(fr, 0, 9))
    slot(t, s, "fx-concert-02", (230, 120, 1460, 840), 6)
    s.shape("Tinte", (230, 120, 1690, 960), solid("#E8365D", 0.6), 6, 9, "ltr")
    s.word("TYPOGRAPHY", (560, 420, 1360, 640), NAME, 400, WHITE, at=12, n=9, slide=-60)
    s.word("Typography is a fundamental element of graphic art.", (650, 660, 1270, 685), M, 700, WHITE, "Texto",
           at=15, n=8, slide=0)
    s.outline("Casilla", rect_pts(1520, 170, 1620, 270), 4, WHITE, at=15, n=9)
    s.outline("Visto", [(1545, 220), (1565, 240), (1598, 200)], 6, WHITE, at=18, n=6, closed=False)
    return t


def art_always():
    t = _p("art-always", "Título: palabras con efecto glitch", "Title: words with a glitch", 8933, ["glitch"])
    s = Piece5(t, 3.8, BLACK)
    for name, colour, dx in (("rojo", "#FF2A3D", -14), ("cian", "#2AE8FF", 14)):
        for line, ink in (("ART", (840, 330, 1300, 470)), ("ALWAYS!", (560, 480, 1360, 640))):
            ghost = s.text(line, ink, M, 900, colour, f"Glitch {name} {line}", editable=False,
                           shift=lambda fr, dx=dx: (dx * (1 - k(fr, 6, 12)) * 3, 0.0))
            s.fade(ghost, lambda fr: 0.9 * (1 - k(fr, 9, 9)) * k(fr, 0, 3))
    s.word("ART", (840, 330, 1300, 470), M, 900, WHITE, "Texto", at=6, n=6, slide=0)
    s.word("ALWAYS!", (560, 480, 1360, 640), M, 900, WHITE, at=6, n=6, slide=0)
    s.outline("Icono", rect_pts(700, 350, 800, 450), 4, WHITE, at=9, n=9)
    s.word("GRAPHICS IS THE FOREMOST ART FORM.", (660, 670, 1260, 692), M, 900, WHITE, "Texto 2", at=12, n=8, slide=0)
    for i, line in enumerate(("Lorem ipsum dolor sit amet,", "consectetur adipiscing elit, sed do eiusmod",
                              "tempor incididunt ut labore et dolore magna aliqua.")):
        s.word(line, (720, 715 + 26 * i, 1200, 733 + 26 * i), M, 500, WHITE, f"Texto {i + 3}", at=15 + i, n=8,
               slide=0)
    return t


def concept_blue():
    t = _p("concept-azul", "Título: palabra ancha sobre azul", "Title: wide word on blue", 8934, ["azul"])
    s = Piece5(t, 3.8, BLUE)
    w = s.word("CONCEPT", (500, 470, 1420, 620), M, 900, "#111111", at=0, n=9, slide=0)
    s.letters(w, 0, 0.06, 0.4, preset="fade")
    s.word("MOTION GRAPHIC DESIGN", (1080, 432, 1400, 452), NAME, 400, "#111111", "Texto", at=12, n=8, slide=0)
    dots(s, 90, 960, WHITE, 12)
    return t


def concept_dark():
    t = _p("concept-oscuro", "Título: caja azul sobre fondo oscuro", "Title: blue box on a dark ground", 8935,
           ["azul"])
    s = Piece5(t, 3.8, "#2A2A2A", "#0D0D0D", angle=90)
    s.ghost("CONCEPT", (-100, 100, 2000, 980), WHITE, 0.06)
    s.shape("Caja", (470, 470, 1450, 600), solid(BLUE), 3, 9, "mid")
    s.word("CONCEPT", (510, 480, 1410, 590), M, 900, "#111111", at=9, n=9, slide=0)
    s.word("MOTION GRAPHIC DESIGN", (1170, 432, 1430, 452), NAME, 400, WHITE, "Texto", at=12, n=8, slide=0)
    s.word("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod", (520, 618, 1400, 638), M, 600,
           WHITE, "Texto 2", at=15, n=8, slide=0)
    for i in range(5):
        x = 300 + 95 * i
        s.outline(f"Icono {i + 1}", rect_pts(x, 930, x + 64, 994), 3, WHITE, at=15 + i, n=8)
    dots(s, 90, 860, WHITE, 15)
    return t


def modern():
    t = _p("modern", "Título: serif elegante con número", "Title: elegant serif with a number", 8936, ["serif"])
    s = Piece5(t, 3.8, WHITE)
    s.word("01", (500, 280, 640, 380), M, 900, BLACK, "Número", at=0, n=9, slide=0, align="left")
    s.word("modern", (500, 400, 760, 450), SERIF, 400, BLACK, "Texto", at=3, n=9, slide=-40, align="left")
    s.word("typography", (500, 455, 1350, 580), SERIF, 400, BLACK, at=6, n=9, slide=-40, align="left")
    s.word("titles", (500, 610, 720, 670), SERIF, 400, BLACK, "Texto 2", at=9, n=9, slide=-40, align="left")
    w = s.word("modern compact design", (500, 690, 820, 710), M, 700, RED, "Texto 3", at=12, n=6, slide=0,
               align="left")
    s.letters(w, 12, 0.03, 0.3, preset="fade", order_in="random")
    return t


def look():
    t = _p("look", "Título: letras gigantes y marco azul", "Title: giant letters and a blue frame", 8937, ["marco"])
    s = Piece5(t, 3.8, BLACK)
    big = s.word("LOOK", (-300, -150, 1700, 1250), M, 900, WHITE, "Fondo (texto)", at=0, n=12, slide=-200)
    del big
    hatch = " ".join(f"M {i * 6:.1f} 0 L {i * 6 + 1.5:.1f} 0 L {i * 6 - 18.5:.1f} 100 L {i * 6 - 20:.1f} 100 Z"
                     for i in range(4, 21))
    s.shape("Rayas", (1300, 0, 1680, 1080), solid(WHITE), 3, 12, "ttb", path=hatch)
    s.shape("Caja", (1360, 340, 1600, 740), solid(WHITE), 9, 9, "pop")
    s.outline("Marco", rect_pts(1350, 330, 1610, 750), 8, "#18B7F2", at=12, n=12)
    s.word("LO", (1400, 380, 1570, 530), M, 900, BLACK, "Texto", at=15, n=8, slide=0)
    s.word("OK", (1400, 560, 1570, 710), M, 900, BLACK, "Texto 2", at=15, n=8, slide=0)
    s.shape("Etiqueta", (0, 610, 320, 660), solid(BLACK), 12, 9, "ltr")
    s.word("graphicdesign", (40, 620, 290, 650), M, 600, WHITE, "Texto 3", at=15, n=8, slide=0)
    lab = s.word("/ modern compact design", (1660, 528, 1960, 548), M, 500, RED, "Texto 4", at=15, n=8, slide=0)
    s.turn(lab, -90)
    return t


def easy_editing():
    t = _p("easy-editing", "Título: letras rojas sobre trama amarilla", "Title: red words on a yellow pattern",
           8938, ["amarillo"])
    s = Piece5(t, 3.8, YELLOW)
    wall(s, "EASY", (-200, 140, 480, 820), WHITE, -15, 0, size=280, layers=[shadow(BLACK, 0, 22), fill(WHITE)],
         name="Trama")
    s.word("EASY", (240, 300, 900, 500), M, 900, RED, at=6, n=9, slide=-80, align="left")
    s.word("EDITING", (240, 500, 1340, 700), M, 900, RED, "Título 2", at=9, n=9, slide=-80, align="left")
    s.word("AFTER EFFECTS TEMPLATE", (930, 395, 1210, 415), NAME, 400, BLACK, "Texto", at=12, n=8, slide=0,
           align="left")
    s.word("NO PLUGINS REQUIRED", (930, 420, 1260, 450), NAME, 400, BLACK, "Texto 2", at=12, n=8, slide=0,
           align="left")
    s.shape("Línea", (240, 735, 1400, 745), solid(BLACK), 12, 9, "ltr")
    s.word("EASY", (60, 800, 1860, 1260), M, 900, BLACK, "Texto 3", at=15, n=12, slide=0)
    return t


def colorful():
    t = _p("colorful", "Título: banda blanca con letras de colores", "Title: white band with colourful letters",
           8939, ["foto", "degradado"])
    s = Piece5(t, 3.8, BLACK)
    slot(t, s, "fx-cyber-04", (0, 0, 1920, 1080), 0)
    s.shape("Banda", (0, 200, 1920, 880), solid(WHITE), 3, 9, "mid")
    rainbow = [gradient([(0.0, "#2F6BFF"), (0.5, "#C23BFF"), (1.0, "#FF4A7A")], angle=0)]
    s.word("Colorful", (950, 290, 1790, 470), M, 800, WHITE, at=9, n=9, slide=60, align="right", layers=rainbow)
    s.word("scenes", (1150, 480, 1790, 640), M, 800, "#111111", "Título 2", at=12, n=9, slide=60, align="right")
    for i, line in enumerate(("Sed ut perspiciatis unde omnis iste natus error", "sit voluptatem accusantium doloremque",
                              "laudantium, totam rem aperiam")):
        s.word(line, (1250, 660 + 24 * i, 1790, 678 + 24 * i), M, 500, BLACK, f"Texto {i + 1}", at=15 + i, n=8,
               slide=0, align="right")
    dots(s, 90, 960, WHITE, 15)
    return t


def create():
    t = _p("create", "Título: tres palabras enormes", "Title: three huge words", 8940)
    s = Piece5(t, 3.8, WHITE)
    s.word("01", (40, 40, 110, 90), M, 900, BLACK, "Número", at=0, n=9, slide=0, align="left")
    for i, (line, x0, x1, y0, y1) in enumerate((("CREATE", 260, 1340, 120, 360), ("AND", 470, 1100, 380, 620),
                                                ("AESTHETIC", 10, 1540, 650, 900))):
        s.word(line, (x0, y0, x1, y1), M, 900, BLACK, f"Título {i + 1}" if i else "Título", at=3 + 3 * i, n=9,
               slide=-80)
    s.word("NEWVISION", (1450, 480, 1760, 520), M, 900, BLACK, "Texto", at=12, n=8, slide=0, align="left")
    s.word("Lorem ipsum dolor sit amet,", (1450, 535, 1760, 555), M, 500, BLACK, "Texto 2", at=15, n=8, slide=0,
           align="left")
    s.word("consectetur adipiscing elit.", (1450, 562, 1760, 582), M, 500, BLACK, "Texto 3", at=15, n=8, slide=0,
           align="left")
    dots(s, 100, 990, RED, 15)
    return t


def text_animation():
    t = _p("text-animation", "Título: filas de texto sobre foto", "Title: rows of text over a photo", 8941,
           ["foto"])
    s = Piece5(t, 3.8, BLACK)
    slot(t, s, "fx-concert-03", (0, 0, 1920, 1080), 0)
    for i in range(3):
        y = 140 + 280 * i
        row = s.text("TEXT ANIMATION", (-60, y, 1980, y + 240), M, 900, BLACK, f"Título {i + 1}" if i else "Título",
                     shift=lambda fr, i=i: ((1 if i % 2 else -1) * (1 - k(fr, 3 + 2 * i, 15)) * 900, 0.0))
        s.fade(row, lambda fr, i=i: k(fr, 3 + 2 * i, 6))
    s.outline("Línea", [(980, 1080), (1640, 0)], 4, WHITE, at=12, n=12, closed=False)
    return t


TEMPLATES = [love, scene, never_give_up, always_strive, newest, dynamic, health_wall, health_box, science, enjoy, big,
             fashion, typography, art_always, concept_blue, concept_dark, modern, look, easy_editing, colorful, create,
             text_animation]
