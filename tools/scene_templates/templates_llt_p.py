"""Flat lower thirds, sixteenth set (2026-11-08): the nine of 38277673.mp4 (1920×1080 at 60 fps, in the TITLE
folder), condensed Oswald names on red, blue, cyan, teal and orange boxes with white lines. The reference shows
the nine in a grid and then each over footage, bottom left: here at that place, with no background. Ids
`llt16-*`, order 8760-. Study notes in tienda/plantillas/estudio-38277673/NOTAS.md.

Not made: the fire, electricity, smoke and light-burst particles that bring each one in (VFX are on hold); a
white streak that sweeps across before the boxes open stands in for them. Names changed to ordinary ones.
"""

from __future__ import annotations

import templates_llt_f as f6
from kit import wide
from templates_tit_c import k
from templates_tit_e import Piece5, solid
from templates_tit_b import Slide

WHITE, RED, BLUE, CYAN, TEAL, ORANGE, GREY = ("#FFFFFF", "#E8553A", "#3A9BE8", "#4BB8CC", "#3ECFB5", "#F08A1C",
                                              "#6F7378")
O = "Oswald"
for w, file in ((300, "Oswald-Light"), (400, "Oswald-Regular"), (500, "Oswald-Medium"), (600, "Oswald-SemiBold")):
    f6._FILES.setdefault((O, w), f"fonts.basic/fonts/oswald/{file}.ttf")
D = 3.0


class Lower(Piece5):
    """A piece with no background (it goes over the user's footage)."""

    def __init__(self, t, dur):
        Slide.__init__(self, t, dur)
        self.tilt, self.pivot = 0.0, (960, 540)


def _p(id, es, en, order, tags=()):
    return wide(f"llt16-{id}", es, en, "ytkit", D, order=order,
                tags=["kit:lowerthirds", "tercio", "plano"] + list(tags), thumb_at=1.5)


def streak(s, y, x0, x1, at=0):
    """A white streak that sweeps across and fades (in place of the reference's energy burst)."""
    clip = s.shape("Destello", (x0, y - 3, x1, y + 3), solid(WHITE, 0.9), at, 6, "ltr")
    s.fade(clip, lambda fr: k(fr, at, 2) * (1 - k(fr, at + 6, 6)))


def director():
    t = _p("director", "Tercio: cargo en blanco y nombre en rojo", "Lower third: white role, red name", 8760)
    s = Lower(t, D)
    streak(s, 835, 100, 700)
    s.shape("Caja", (120, 780, 470, 822), solid(WHITE), 4, 8, "ltr")
    s.word("CREATIVE DIRECTOR", (135, 788, 450, 815), O, 500, RED, "Texto", at=9, n=8, slide=-30, align="left")
    s.shape("Caja 2", (245, 822, 620, 882), solid(RED), 6, 8, "ltr")
    s.word("MARTA SALINAS", (275, 830, 600, 874), O, 400, WHITE, at=11, n=8, slide=-30, align="right")
    s.shape("Línea", (245, 887, 625, 891), solid(WHITE), 10, 8, "ltr")
    s.shape("Tope", (620, 822, 627, 891), solid(WHITE), 12, 6, "ttb")
    return t


def bar_name():
    t = _p("barra-nombre", "Tercio: barra roja y nombre fino", "Lower third: red bar and a light name", 8761)
    s = Lower(t, D)
    streak(s, 850, 100, 620)
    s.shape("Barra", (120, 790, 131, 905), solid(RED), 4, 8, "ttb")
    s.word("NORA BLAKE", (150, 790, 490, 852), O, 300, WHITE, at=8, n=9, slide=-50, align="left")
    s.word("2D ANIMATOR", (150, 862, 360, 902), O, 400, WHITE, "Texto", at=11, n=9, slide=-50, align="left")
    return t


def blue_role():
    t = _p("cargo-azul", "Tercio: nombre y cargo en caja azul", "Lower third: name and role in a blue box", 8762)
    s = Lower(t, D)
    streak(s, 860, 100, 640)
    s.word("DANIEL REYES", (155, 790, 525, 852), O, 600, WHITE, at=8, n=9, slide=0)
    s.shape("Línea", (120, 856, 560, 860), solid(WHITE), 4, 8, "ltr")
    s.shape("Caja", (120, 860, 560, 905), solid(BLUE), 6, 8, "ltr")
    s.word("LEAD SOUND DESIGNER", (165, 867, 515, 899), O, 400, WHITE, "Texto", at=11, n=8, slide=0)
    return t


def centred_role():
    t = _p("cargo-rojo", "Tercio: nombre fino y cargo en rojo", "Lower third: light name, red role", 8763)
    s = Lower(t, D)
    streak(s, 860, 100, 560)
    s.word("LUCAS MORENO", (120, 790, 480, 856), O, 300, WHITE, at=6, n=9, slide=-40)
    s.shape("Caja", (160, 862, 440, 912), solid(RED), 4, 8, "mid")
    s.word("LEAD DESIGNER", (180, 868, 420, 906), O, 500, WHITE, "Texto", at=9, n=8, slide=0)
    return t


def time_date():
    t = _p("hora", "Tercio: hora y fecha", "Lower third: time and date", 8764, ["fecha"])
    s = Lower(t, D)
    streak(s, 865, 100, 560)
    s.shape("Caja", (120, 830, 360, 902), solid(BLUE), 4, 8, "ltr")
    s.word("04:00 PM", (145, 842, 335, 890), O, 500, WHITE, at=9, n=8, slide=-30)
    s.word("16 APRIL", (378, 830, 490, 862), O, 400, WHITE, "Texto", at=11, n=8, slide=-30, align="left")
    s.word("MONDAY", (378, 870, 480, 900), O, 400, WHITE, "Texto 2", at=13, n=8, slide=-30, align="left")
    return t


def photographer():
    t = _p("fotografa", "Tercio: cargo pequeño y nombre en caja celeste", "Lower third: small role, name on cyan",
           8765)
    s = Lower(t, D)
    streak(s, 840, 100, 640)
    s.shape("Borde", (120, 790, 124, 892), solid(WHITE), 4, 6, "ttb")
    s.shape("Caja", (124, 790, 380, 818), solid(WHITE), 6, 8, "ltr")
    s.word("PHOTOGRAPHER", (136, 794, 280, 814), O, 500, CYAN, "Texto", at=10, n=8, slide=-20, align="left")
    s.shape("Caja 2", (124, 818, 560, 878), solid(CYAN), 8, 8, "ltr")
    s.word("ELENA CRUZ", (140, 824, 420, 874), O, 300, WHITE, at=12, n=8, slide=-30, align="left")
    s.shape("Línea", (120, 886, 535, 890), solid(WHITE), 10, 8, "ltr")
    return t


def title_red():
    t = _p("titulo-rojo", "Tercio: título y subtítulo en rojo", "Lower third: title and red subtitle", 8766)
    s = Lower(t, D)
    streak(s, 850, 100, 560)
    s.word("LOWER THIRDS", (120, 780, 480, 852), O, 600, WHITE, at=6, n=9, slide=-40)
    s.shape("Caja", (165, 860, 435, 897), solid(RED), 4, 8, "mid")
    s.word("TEXT ANIMATIONS", (190, 865, 410, 892), O, 500, "#3A1A14", "Texto", at=9, n=8, slide=0)
    return t


def show():
    t = _p("show", "Tercio: título entre dos líneas", "Lower third: title between two lines", 8767)
    s = Lower(t, D)
    streak(s, 840, 100, 640)
    s.shape("Línea", (120, 770, 125, 912), solid(WHITE), 4, 8, "ttb")
    s.shape("Línea 2", (600, 770, 605, 912), solid(WHITE), 4, 8, "btt")
    s.word("ELECTRICITY SHOW", (160, 784, 565, 842), O, 600, WHITE, at=8, n=9, slide=0)
    s.shape("Raya", (160, 848, 565, 851), solid(WHITE), 10, 8, "mid")
    s.shape("Caja", (212, 862, 512, 902), solid(TEAL), 10, 8, "mid")
    s.word("LIGHT PRODUCTION", (235, 866, 490, 898), O, 400, WHITE, "Texto", at=13, n=8, slide=0)
    return t


def your_text():
    t = _p("tu-texto", "Tercio: caja naranja y gris", "Lower third: orange and grey box", 8768)
    s = Lower(t, D)
    streak(s, 845, 100, 560)
    s.shape("Caja", (120, 800, 480, 850), solid(ORANGE), 4, 8, "ltr")
    s.shape("Caja 2", (120, 850, 480, 892), solid(GREY), 6, 8, "ltr")
    s.outline("Marco", [(120, 800), (480, 800), (480, 892), (120, 892)], 3, ORANGE, at=8, n=10)
    s.word("YOUR TEXT", (132, 806, 330, 846), O, 600, WHITE, at=9, n=8, slide=-30, align="left")
    s.word("PLACE YOUR TEXT HERE", (132, 860, 350, 884), O, 500, WHITE, "Texto", at=11, n=8, slide=-30,
           align="left")
    return t


TEMPLATES = [director, bar_name, blue_role, centred_role, time_date, photographer, title_red, show, your_text]
