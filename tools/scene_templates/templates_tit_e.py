"""Colourful channel slides, fifth TITLE set (2026-11-08): the twenty of 2300019.mp4 (960×540 at 29.97 fps, laid out
here at 1920×1080). Full-frame slides for a channel: a coloured or gradient background (its own «Fondo» layer),
sometimes a huge pale word behind, and a title on a tilted label, a diamond, a circle, a frame or a 3D stack, with
the small «www.yourwebsite.com». Bebas Neue, Oswald, Montserrat, Lilita One. Kit de YouTube › Títulos con estilo;
ids `tit5-*`, order 8880-. Study notes in tienda/plantillas/estudio-2300019/NOTAS.md.

Moves (from 2 fps sheets): the background is there from the start; shapes pop or swing in, words slide or rise in,
one after another; each slide leaves with its entrance backwards. The video platform's name and play button in
the reference are replaced by «MYCHANNEL» and a logo slot with our play symbol; a font name («HELVETICA BLACK») by
neutral words; «BY PROJECT AUTHOR» by «BY OUR TEAM». The «SMOOTH TRANSITIONS» thumbnail wall is not a title.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from scene import gradient, no_stroke
from templates_tit_b import Slide
from templates_tit_c import Piece3, k, rect_pts
from templates_tit_d import Piece4

WHITE = "#FFFFFF"
f6._FILES[("Lilita One", 400)] = "fonts.extra/fonts/lilitaone/LilitaOne-Regular.ttf"
f6._FILES[("Oswald", 600)] = "fonts.basic/fonts/oswald/Oswald-SemiBold.ttf"
f6._FILES[("Oswald", 700)] = "fonts.basic/fonts/oswald/Oswald-Bold.ttf"
NAME = "Bebas Neue"
URL = "WWW.YOURWEBSITE.COM"


def solid(colour, alpha=1.0):
    a = format(round(alpha * 255), "02x")
    return [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
             "paint": {"kind": "solid", "color": "#" + a + colour.lstrip("#").lower()}}, no_stroke()]


def grad(c0, c1, angle=90):
    return [gradient([(0.0, c0), (1.0, c1)], angle=angle), no_stroke()]


class Piece5(Piece4):
    """A slide on a background of colour c0 (to c1 when given, a gradient at `angle`)."""

    def __init__(self, t, dur, c0, c1=None, angle=90, tilt=0.0):
        Slide.__init__(self, t, dur)
        self.tilt, self.pivot = tilt, (960, 540)
        bg = self.background(c0)
        if c1:
            bg["shapeStyle"]["layers"] = grad(c0, c1, angle)

    def text(self, content, ink, family, weight, colour=WHITE, name="Título", **kw):
        """As Slide.text, but never taller than the reference's capitals (our faces run narrower)."""
        x0, y0, x1, y1 = ink
        f = f6._font(family, weight)
        shown = content.upper() if kw.get("case", "none") == "upper" else content
        bb, cap = f.getbbox(shown), f.getbbox("H")
        width = min(x1 - x0, (y1 - y0) * (bb[2] - bb[0]) / max(1, cap[3] - cap[1]))
        if width < x1 - x0:
            align = kw.get("align", "center")
            if align == "center":
                c = (x0 + x1) / 2
                x0, x1 = c - width / 2, c + width / 2
            elif align == "left":
                x1 = x0 + width
            else:
                x0 = x1 - width
        return Slide.text(self, content, (x0, y0, x1, y1), family, weight, colour, name, **kw)

    def shape(self, name, rect, layers, at=0, n=9, way="pop", fade=False, kind=None, path=None):
        clip = self.bar(name, rect, at, n, way, layers=layers, fade=fade)
        if kind:
            clip["shapeStyle"]["kind"] = kind
        if path:
            clip["shapeStyle"]["kind"] = "custom"
            clip["shapeStyle"]["customPath"] = path
            clip["shapeStyle"]["customEvenOdd"] = False
        return clip

    def ghost(self, text, ink, colour, alpha, at=0, n=15):
        """A huge pale word behind, drifting in from the right."""
        clip = self.text(text, ink, NAME, 400, colour, "Fondo (texto)", shift=lambda fr: ((1 - k(fr, at, n)) * 160, 0.0),
                         editable=False)
        self.fade(clip, lambda fr: alpha * k(fr, at, n))
        return clip

    def url(self, y=1020, colour=WHITE, x0=760, x1=1160):
        return self.word(URL, (x0, y, x1, y + 16), "Montserrat", 700, colour, "Web", at=12, n=9, slide=0)

    def turned(self, deg, fn):
        """Run fn(piece) with the clips it makes turned by deg about the frame's centre."""
        other = Piece5.__new__(Piece5)
        other.__dict__.update(self.__dict__)
        other.tilt = deg
        return fn(other)


def _p(id, es, en, order, tags=(), dur=3.6):
    return wide(f"tit5-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:titulos-estilo", "título", "canal", "colores"] + list(tags), thumb_at=round(dur / 2, 1))


def hashtag():
    t = _p("hashtag", "Título: hashtag sobre amarillo", "Title: hashtag on yellow", 8880, ["hashtag"])
    s = Piece5(t, 3.6, "#FFD54A")
    s.shape("Flecha", (-400, -80, 1500, 1160), solid("#FFE07A"), 0, 15, "ltr",
            path="M 0 0 L 45 0 L 100 50 L 45 100 L 0 100 L 55 50 Z")
    s.word("#MYCHANNEL", (460, 420, 1460, 600), NAME, 400, "#E8113B", at=6, n=10, slide=-80)
    s.text("SOCIAL MEDIA MARKETING", (620, 606, 1392, 646), NAME, 400, "#E8113B", "Texto",
           reveal=lambda fr: (0, 604, 1920, 700), shift=lambda fr: (0.0, -(1 - k(fr, 15, 9)) * 50))
    return t


def grow():
    t = _p("rombo", "Título: rombo blanco sobre rojo", "Title: white diamond on red", 8881, ["rombo"])
    s = Piece5(t, 3.6, "#D80F4B")
    s.shape("Rombo", (560, 140, 1360, 940), solid(WHITE), 0, 12, "pop", path="M 50 0 L 100 50 L 50 100 L 0 50 Z")
    s.word("YOUR", (804, 420, 932, 470), NAME, 400, "#1B1B1B", "Texto", at=9, n=8, slide=0)
    s.word("GROW", (768, 474, 1144, 606), NAME, 400, "#D80F4B", at=12, n=9, slide=0)
    s.word("BUSINESS", (892, 610, 1128, 662), NAME, 400, "#1B1B1B", "Texto 2", at=15, n=8, slide=0)
    for i, (x, y) in enumerate(((1640, 100), (1690, 100), (130, 900), (180, 900))):
        s.shape(f"Raya {i + 1}", (x, y, x + 6, y + 90), solid(WHITE), 6 + 2 * i, 9, "ttb")
    s.url(1030, WHITE, 1480, 1880)
    return t


def channel_label():
    t = _p("etiqueta", "Título: etiqueta inclinada sobre azul", "Title: tilted label on blue", 8882, ["etiqueta"])
    s = Piece5(t, 3.6, "#1446C8")
    s.ghost("CHANNEL", (-40, 40, 2100, 1040), "#3A6BE0", 0.45)
    s.turned(-8.0, lambda p: (p.shape("Etiqueta", (480, 450, 1440, 610), solid(WHITE), 3, 9, "ltr"),
                              p.word("MYCHANNEL", (540, 470, 1380, 590), NAME, 400, "#1446C8", at=6, n=9, slide=-60),
                              p.shape("Línea", (900, 626, 1460, 634), solid(WHITE), 12, 9, "ltr")))
    s.url(1015, WHITE)
    return t


def dont_waste():
    t = _p("no-pierdas", "Título: frase en un marco rojo", "Title: phrase in a red frame", 8883, ["marco"])
    s = Piece5(t, 3.6, "#111111")
    s.outline("Marco", rect_pts(684, 264, 1236, 816), 9, "#E8113B", at=0, n=12)
    for i, line in enumerate(("D O N ' T", "W A S T E", "Y O U R", "T I M E")):
        y = 404 + 84 * i
        s.word(line, (820, y, 1112 - (60 if len(line) < 9 else 0), y + 40), "Montserrat", 700, WHITE,
               f"Título {i + 1}" if i else "Título", at=9 + 3 * i, n=8, slide=0, align="left")
    s.url(1015, WHITE)
    return t


def social_media():
    t = _p("social-media", "Título: círculo sobre amarillo", "Title: circle on yellow", 8884, ["círculo"])
    s = Piece5(t, 3.6, "#FFD54A")
    s.outline("Aro", [(960 + 280 * math.cos(math.pi * 1.5 + 2 * math.pi * i / 64),
                       540 + 280 * math.sin(math.pi * 1.5 + 2 * math.pi * i / 64)) for i in range(64)], 12, WHITE,
              at=0, n=12)
    s.word("SOCIAL", (884, 422, 1036, 466), NAME, 400, WHITE, "Texto", at=9, n=8, slide=0)
    s.word("MEDIA", (820, 476, 1100, 600), NAME, 400, "#E8113B", at=12, n=9, slide=0)
    s.word("MARKETING", (852, 614, 1068, 664), NAME, 400, WHITE, "Texto 2", at=15, n=8, slide=0)
    return t


def follow_us():
    t = _p("seguinos", "Título: círculo azul con frase", "Title: blue circle with a phrase", 8885, ["círculo"])
    s = Piece5(t, 3.6, "#00D2E6", "#4B4BEF")
    s.shape("Sombra", (800, 880, 1120, 920), solid("#1E2A80", 0.35), 6, 9, "mid", kind="ellipse")
    s.shape("Círculo", (720, 300, 1200, 780), grad("#1EA8F5", "#1068F0"), 0, 12, "pop", kind="ellipse")
    for i, line in enumerate(("FOLLOW US", "FOR", "NEW CREATIVE", "ITEMS")):
        w = {9: 240, 3: 90, 12: 310, 5: 130}[len(line)]
        y = 444 + 64 * i
        s.word(line, (960 - w / 2, y, 960 + w / 2, y + 44), NAME, 400, WHITE, f"Título {i + 1}" if i else "Título",
               at=12 + 2 * i, n=8, slide=0)
    s.url(1040, WHITE)
    return t


def your_channel():
    t = _p("tu-canal", "Título: caja blanca sobre celeste", "Title: white box on cyan", 8886, ["caja"])
    s = Piece5(t, 3.6, "#1BC3E0")
    s.shape("Flecha", (300, -200, 1200, 1280), solid("#3FD0EA"), 0, 15, "ltr",
            path="M 0 0 L 45 0 L 100 50 L 45 100 L 0 100 L 55 50 Z")
    s.shape("Caja", (468, 472, 1452, 608), solid(WHITE), 6, 9, "mid")
    s.word("YOUR CHANNEL NAME", (520, 488, 1400, 592), NAME, 400, "#1BC3E0", at=12, n=9, slide=0)
    s.word(URL, (760, 630, 1160, 646), "Montserrat", 700, WHITE, "Web", at=15, n=9, slide=0)
    return t


def logo_channel():
    t = _p("logo-canal", "Título: logo y nombre del canal", "Title: logo and channel name", 8887, ["logo"])
    s = Piece5(t, 3.6, "#E6E2DF")
    logo = t.photo(t.track("video", "Logo"), "logo-flip", 0.0, 3.6, Box(500, 452, 180, 180), None, label="Tu logo",
                   brandRole="logo")
    s.fade(logo, lambda fr: k(fr, 0, 9))
    s.text("YOURCHANNEL", (788, 492, 1432, 588), NAME, 400, "#1B1B1B", "Título", align="left",
           reveal=lambda fr: (760, 400, 1700, 700), shift=lambda fr: (-(1 - k(fr, 9, 12)) * 680, 0.0))
    s.word("NAME SURNAME", (804, 600, 1040, 630), "Montserrat", 700, "#1B1B1B", "Texto", at=18, n=8, align="left")
    s.shape("Línea", (1300, 500, 1440, 504), solid("#1B1B1B"), 18, 8, "ltr")
    return t


def creative():
    t = _p("creative", "Título: palabra lila sobre morado", "Title: lilac word on purple", 8888, ["morado"])
    s = Piece5(t, 3.6, "#6A12C8")
    s.ghost("NALLY", (-60, 120, 1980, 980), "#8A3AE0", 0.45)
    s.word("CREATIVE", (492, 408, 1428, 592), NAME, 400, "#C8A6FF", at=3, n=12, slide=0)
    s.word("PROFESSIONALLY DESIGNED", (628, 632, 1300, 684), "Montserrat", 700, WHITE, "Texto", at=12, n=9, slide=0)
    s.url(1040, WHITE)
    return t


def livestream():
    t = _p("directo", "Título: transmisión en vivo inclinada", "Title: tilted livestream", 8889, ["directo"])
    s = Piece5(t, 3.6, "#2A4FF0", "#08D6A0", angle=135)
    s.turned(-8.0, lambda p: (p.outline("Marco", rect_pts(480, 420, 1440, 660), 8, WHITE, at=0, n=12),
                              p.word("LIVESTREAM", (520, 430, 1400, 650), NAME, 400, WHITE, at=9, n=10, slide=0),
                              p.shape("Etiqueta", (668, 352, 1252, 412), solid(WHITE), 6, 8, "ltr"),
                              p.word("M Y   C H A N N E L", (720, 360, 1200, 404), "Montserrat", 800, "#2A4FF0",
                                     "Texto", at=9, n=8, slide=0),
                              p.word("10:30PM", (1240, 670, 1420, 714), "Montserrat", 800, WHITE, "Texto 2", at=15,
                                     n=8, slide=0)))
    return t


def share_tag():
    t = _p("compartir", "Título: etiqueta morada sobre amarillo", "Title: purple tag on yellow", 8890, ["etiqueta"])
    s = Piece5(t, 3.6, "#FFD54A")
    s.shape("Círculo", (120, -100, 1800, 1180), solid("#FFCC00"), 0, 15, "pop", kind="ellipse")
    s.shape("Sombra", (400, 840, 1520, 900), solid("#B08A00", 0.4), 6, 9, "mid", kind="ellipse")
    tag = s.shape("Etiqueta", (588, 440, 1372, 640), grad("#B314C8", "#8A10B0", 0), 0, 1, "pop")
    s.swing(tag, 3, 10, deg=-25, dx=0, dy=-80)
    s.turned(-5.0, lambda p: p.word("SHARE", (800, 480, 1160, 600), "Lilita One", 400, WHITE, at=10, n=8,
                                    slide=0))
    return t


def free_support():
    t = _p("soporte", "Título: banda con dos líneas", "Title: band with two lines", 8891, ["banda"])
    s = Piece5(t, 3.6, "#3A2A8C")
    s.ghost("SUPPORT", (40, 120, 1880, 960), "#4A3AA0", 0.45)
    s.shape("Banda", (0, 360, 1920, 720), solid(WHITE, 0.14), 0, 12, "ltr")
    s.shape("Línea", (200, 320, 1600, 324), solid(WHITE, 0.6), 6, 12, "ltr")
    s.word("FREE SUPPORT", (184, 460, 628, 520), NAME, 400, WHITE, "Texto", at=9, n=9, align="left")
    s.word("BY OUR TEAM", (232, 540, 860, 660), NAME, 400, WHITE, at=12, n=9, align="left")
    s.shape("Línea 2", (1000, 1000, 1880, 1004), solid(WHITE, 0.8), 12, 9, "rtl")
    s.url(1015, WHITE, 1480, 1880)
    return t


def tutorial():
    t = _p("tutorial", "Título: tutorial en verde agua", "Title: aqua tutorial", 8892, ["tutorial"])
    s = Piece5(t, 3.6, "#C400F0", "#5A20F0", angle=45)
    s.word("VIDEO", (696, 420, 1004, 500), "Lilita One", 400, "#3DF5C8", at=0, n=9, slide=0)
    s.word("TUTORIAL", (640, 520, 1280, 632), "Lilita One", 400, "#3DF5C8", "Título 2", at=4, n=9, slide=0)
    s.word("INCLUDED", (928, 652, 1272, 712), "Lilita One", 400, "#FF5ACD", "Texto", at=9, n=9, slide=0)
    return t


def summer():
    t = _p("verano", "Título: este verano con fecha", "Title: this summer with a date", 8893, ["verano"])
    s = Piece5(t, 3.6, "#1E3A8A", "#0E1A50", angle=135)
    s.word("THIS", (680, 372, 912, 480), NAME, 400, "#22C8F0", "Texto", at=3, n=9, slide=0)
    s.word("SUMMER", (600, 482, 1320, 658), NAME, 400, "#22C8F0", at=6, n=10, slide=0)
    s.word("AUGUST 10", (1024, 662, 1308, 712), "Montserrat", 800, WHITE, "Texto 2", at=12, n=8, slide=0)
    return t


def logo_dark():
    t = _p("logo-negro", "Título: logo y nombre sobre negro", "Title: logo and name on black", 8894, ["logo"])
    s = Piece5(t, 3.6, "#141414")
    dot = s.shape("Punto", (520, 500, 600, 580), solid("#E8113B"), 0, 6, "pop", kind="rectangle")
    s.fade(dot, lambda fr: 1.0 - k(fr, 6, 4))
    logo = t.photo(t.track("video", "Logo"), "logo-flip", 0.0, 3.6, Box(452, 452, 176, 176), None, label="Tu logo",
                   brandRole="logo")
    s.fade(logo, lambda fr: k(fr, 6, 9))
    s.text("YOURCHANNELNAME", (732, 500, 1484, 580), "Montserrat", 500, WHITE, "Título", align="left",
           reveal=lambda fr: (700, 400, 1700, 700), shift=lambda fr: (-(1 - k(fr, 12, 12)) * 780, 0.0))
    s.url(1040, WHITE)
    return t


def condensed():
    t = _p("condensada", "Título: letra condensada con subrayado", "Title: condensed type, underline", 8895,
           ["condensada"])
    s = Piece5(t, 3.6, "#5000D2", "#3A00B0", angle=135)
    s.word("BOLD AND BLACK", (228, 472, 928, 560), NAME, 400, WHITE, "Texto", at=6, n=9, align="left")
    s.word("CONDENSED", (224, 568, 1084, 712), NAME, 400, WHITE, at=3, n=12, align="left")
    s.shape("Subrayado", (212, 728, 1200, 744), solid("#2A9DF4"), 9, 12, "ltr")
    s.word("PROFESSIONAL ANIMATED TITLES", (228, 760, 960, 806), "Montserrat", 500, WHITE, "Texto 2", at=15, n=9,
           align="left")
    s.url(1040, WHITE, 1480, 1880)
    return t


def dynamic():
    t = _p("dinamico", "Título: palabras espaciadas en marco naranja", "Title: spaced words in an orange frame", 8896,
           ["marco"])
    s = Piece5(t, 3.6, "#0E0E0E")
    s.outline("Marco", rect_pts(592, 332, 1320, 748), 9, "#F0A020", at=0, n=12)
    for i, line in enumerate(("D Y N A M I C", "C R E A T I V E", "S T Y L I S H")):
        y = 410 + 104 * i
        s.word(line, (700, y, 1220, y + 50), "Montserrat", 700, WHITE, f"Título {i + 1}" if i else "Título",
               at=9 + 3 * i, n=8, slide=0)
    s.url(1040, WHITE)
    return t


def stack():
    t = _p("pila", "Título: like, share, subscribe en bloques", "Title: like, share, subscribe blocks", 8897,
           ["bloques", "suscribirse"])
    s = Piece5(t, 3.6, "#E020D0", "#7010D8", angle=90)
    for i, (text, rect, at) in enumerate((("SUBSCRIBE", (628, 540, 1288, 860), 0), ("SHARE", (720, 380, 1100, 580), 6),
                                          ("LIKE", (780, 248, 1040, 400), 12))):
        x0, y0, x1, y1 = rect
        side = s.shape(f"Bloque {i + 1} (lado)", (x0 + 20, y0 + 20, x1 + 20, y1 + 20), solid("#0B4FC0"), 0, 1, "pop")
        s.swing(side, at, 9, deg=-6, dx=0, dy=-200)
        face = s.shape(f"Bloque {i + 1}", rect, grad("#3AA8FF", "#1A78F0"), 0, 1, "pop")
        s.swing(face, at, 9, deg=-6, dx=0, dy=-200)
        w = s.word(text, (x0 + 30, y0 + 20, x1 - 30, y1 - 20), NAME, 400, WHITE,
                   ["Título", "Título 2", "Título 3"][i], at=0, n=1, slide=0)
        s.swing(w, at, 9, deg=-6, dx=0, dy=-200)
    return t


def modern():
    t = _p("moderno", "Título: círculo rojo con tres palabras", "Title: red circle with three words", 8898,
           ["círculo"])
    s = Piece5(t, 3.6, "#E6E2DF")
    s.outline("Aro", [(960 + 250 * math.cos(math.pi * 1.2 + 1.6 * math.pi * i / 48),
                       540 + 250 * math.sin(math.pi * 1.2 + 1.6 * math.pi * i / 48)) for i in range(49)], 5,
              "#E8113B", at=6, n=12, closed=False)
    s.shape("Círculo", (760, 340, 1160, 740), solid("#E8113B"), 0, 12, "pop", kind="ellipse")
    for i, line in enumerate(("MODERN", "STYLISH", "CREATIVE")):
        y = 450 + 64 * i
        s.word(line, (880, y, 1040, y + 50), NAME, 400, WHITE, f"Título {i + 1}" if i else "Título", at=12 + 2 * i,
               n=8, slide=0)
    return t


def channel_card():
    t = _p("canal-tarjeta", "Título: tarjeta morada con marco", "Title: purple card with a frame", 8899, ["marco"])
    s = Piece5(t, 3.6, "#4A2AC0")
    s.shape("Tarjeta", (120, 60, 1800, 1020), grad("#5A3AE0", "#7A5AF0", 0), 0, 12, "pop")
    s.ghost("ANNEL", (100, 160, 1820, 920), "#6A4AE8", 0.45)
    s.turned(-20.0, lambda p: p.outline("Cuadro", rect_pts(640, 420, 940, 720), 14, "#1A1050", at=6, n=12))
    s.word("CHANNEL", (760, 472, 1280, 592), NAME, 400, WHITE, at=12, n=10, slide=-60)
    s.word("GRAPHICDESIGN", (980, 594, 1280, 626), "Montserrat", 800, "#1A1050", "Texto", at=15, n=8, slide=0)
    return t


TEMPLATES = [hashtag, grow, channel_label, dont_waste, social_media, follow_us, your_channel, logo_channel, creative,
             livestream, share_tag, free_support, tutorial, summer, logo_dark, condensed, dynamic, stack, modern,
             channel_card]
