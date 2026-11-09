"""Colourful kinetic titles, seventh TITLE set redone (2026-11-08, Jorge: «lo más parecido posible, no inventes»):
the pieces of 36160725.mp4 (960×540 at 25 fps, laid out at 1920×1080), the colour sibling of 35149534, each with
the moves of the reference studied on 10 fps sheets: a photo seen through huge letters (text masks), stripes and
panels that slide, letters typed, risen or lit out of order, glitch copies in red and cyan, tag boxes that fall,
walls of turned words, cards that pull back. Kit de YouTube › Tipografía; ids `tit7-*` (they replace
`templates_tit_g`), order 8920-. Study notes in tienda/plantillas/estudio-36160725/NOTAS.md.

Each slide plays its entrance, holds, and leaves with its entrance backwards at 2.5× speed.
"""

from __future__ import annotations

import math

from kit import Box, wide
from llt_motion import frames_of, mask_track
from scene import gradient, keys
from templates_tit_c import k
from templates_tit_e import solid
from templates_tit_f import outline_layers
from templates_tit_h import EXIT, S, fill, lin, ring, rot_pt, shadow
from templates_tit_i import bg, cam, masked_photo, with_op

import templates_llt_f as f6

WHITE, BLACK, RED, BLUE, YELLOW = "#FFFFFF", "#000000", "#F23A1D", "#40ADEB", "#FFD400"
M, NAME, SLAB, SERIF, KANIT = "Montserrat", "Bebas Neue", "Roboto Slab", "DM Serif Display", "Kanit"
f6._FILES[(SLAB, 900)] = "fonts.extra/fonts/robotoslab/RobotoSlab-Black.ttf"
f6._FILES[(SERIF, 400)] = "fonts.extra/fonts/dmserifdisplay/DMSerifDisplay-Regular.ttf"
f6._FILES[(KANIT, 700)] = "fonts.extra/fonts/kanit/Kanit-Bold.ttf"


def _p(id, es, en, order, dur, tags=()):
    return wide(f"tit7-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:tipografia", "tipografía", "colores", "cinético"] + list(tags), thumb_at=round(dur * 0.55, 1))


def dur_for(entrance, hold=1.4):
    return round(entrance + hold + entrance / EXIT, 1)


def photo(s, sample, rect=None, name="Foto", op=None):
    t = s.t
    clip = t.photo(t.track("video", name), sample, 0.0, s.dur, None, None, label="Tu foto")
    if rect:
        mask_track(t, clip, Box(0, 0, 1920, 1080), lambda u: rect(s.frame(u), u), s.dur)
    if op:
        clip["opacity"] = keys([(u, round(op(s.frame(u)), 4), "linear") for u in frames_of(s.dur)])
    return clip


def dots(s, x, y, colour, at, n=7, step=24, size=10):
    for i in range(n):
        s.obj(f"Punto {i + 1}", solid(colour), lambda fr, u, i=i: (x + step * i, y, size, size, 0, k(fr, at + i, 3)),
              kind="ellipse")


# --- 1. LOVE GRAPHIC DESIGN!: the word slides in over a pink photo, the second line rises from behind ------------
def love():
    D = dur_for(1.6)
    t = _p("love", "Título: palabra que se desliza sobre foto rosa", "Title: word sliding over a pink photo", 8920, D,
           ["foto"])
    s = S(t, D)
    photo(s, "fx-face-02")
    s.rect("Tinte", solid("#E8365D", 0.5), lambda fr, u: (-10, -10, 1930, 1090))
    s.say("LOVE", (582, 390, 1308, 612), M, 900, WHITE, geom=lambda fr, u: (450 * (1 - k(fr, 0, 18)), 0, 1, 0, 1))
    s.say("GRAPHIC DESIGN!", (600, 616, 1290, 720), NAME, 400, WHITE, "Texto", reveal=lambda fr: (0, 612, 1920, 1080),
          shift=lambda fr: (0, -104 * (1 - k(fr, 12, 12))), op=lambda fr, u: k(fr, 12, 2))
    c = s.say("PACKAGE 2 VERSION", (1500, 1000, 1800, 1018), M, 800, WHITE, "Texto 2")
    s.typed(c, 15, stagger=0.03, duration=0.03)
    dots(s, 180, 912, WHITE, 0)
    return t


# --- 2. SCENE 0.1: stripes, a white panel with the photo slides right, the outlined words follow ------------------
def scene():
    D = dur_for(2.4)
    t = _p("scene", "Título: rayas, panel blanco y número sobre foto", "Title: stripes, white panel and a number over a "
           "photo", 8921, D, ["rayas", "foto"])
    s = S(t, D)
    bg(s, WHITE)
    stripes = " ".join(f"M {i * 3.6:.2f} 0 L {i * 3.6 + 1.8:.2f} 0 L {i * 3.6 + 1.8:.2f} 100 L {i * 3.6:.2f} 100 Z"
                       for i in range(28))
    s.rect("Rayas", solid(BLACK), lambda fr, u: (-10, -10, 1930, 1090), path=stripes)
    move = lambda fr: 660 * k(fr, 0, 36)  # noqa: E731
    s.rect("Panel", solid(WHITE), lambda fr, u: (-10, 228, 1080 + move(fr), 852))
    photo(s, "fx-cyber-02", lambda fr, u: (240 + move(fr), 240, 1062 + move(fr), 828))
    s.say("0.1", (1080, 330, 1608, 750), M, 900, WHITE, geom=lambda fr, u: (move(fr) - 660, 0, 1, 0, 1))
    s.say("SCENE 0.1", (138, 438, 840, 570), M, 900, WHITE, "Texto", layers=outline_layers("#BBBBBB", 3),
          geom=lambda fr, u: (move(fr) - 660, 0, 1, 0, k(fr, 18, 6)))
    s.say("UPDATE 0.1 TITLES PACK", (390, 576, 840, 600), M, 800, BLACK, "Texto 2",
          geom=lambda fr, u: (move(fr) - 660, 0, 1, 0, k(fr, 24, 6)))
    return t


# --- 3. never give up: four photos rise in steps, the words are typed, a black box slides in -------------------
def never_give_up():
    D = dur_for(1.8)
    t = _p("never-give-up", "Título: cuatro fotos en escalera y frase", "Title: four stepped photos and a phrase",
           8922, D, ["foto"])
    s = S(t, D)
    bg(s, WHITE)
    for i, (x, top) in enumerate(((180, 150), (570, 192), (960, 270), (1350, 348))):
        photo(s, f"portrait-0{i + 5}", lambda fr, u, x=x, top=top, i=i: (x, 948 - (948 - top) * k(fr, 3 * i, 12), x + 360,
                                                                       948), name=f"Foto {i + 1}")
    c = s.say("never give up", (180, 480, 1740, 690), M, 900, WHITE, layers=[shadow(BLACK, 0, 6, 14, 0.5), fill(WHITE)])
    s.typed(c, 3, stagger=0.06, duration=0.12, preset="pop")
    s.rect("Caja", solid(BLACK), lambda fr, u: (1920 - 840 * k(fr, 18, 9), 690, 1930, 852))
    c = s.say("never give up!", (1182, 720, 1740, 822), M, 900, WHITE, "Texto", align="left")
    s.typed(c, 24, stagger=0.06, duration=0.12, preset="pop")
    s.rect("Caja 2", solid(BLACK), lambda fr, u: (1920 - 420 * k(fr, 27, 9), 870, 1930, 948))
    c = s.say("Always stand tall.", (1530, 888, 1880, 930), M, 800, WHITE, "Texto 2", align="left")
    s.typed(c, 30, stagger=0.04, duration=0.03)
    c = s.say("Do not surrender to circumstances. You create them.", (360, 172, 1080, 190), M, 600, BLACK, "Texto 3")
    s.typed(c, 36, stagger=0.015, duration=0.03)
    return t


# --- 4. ALWAYS STRIVE TO SUCCESS: the words move aside for a growing exclamation box; a bracket draws ------------
def always_strive():
    D = dur_for(1.8)
    t = _p("always-strive", "Título: frase con sombra roja y signo", "Title: phrase with a red shadow and a sign",
           8923, D, ["sombra"])
    s = S(t, D)
    bg(s, WHITE)
    shift = lambda fr: 300 * (1 - k(fr, 6, 12))  # noqa: E731
    for i, (line, x1, y0, y1) in enumerate((("ALWAYS", 1050, 318, 450), ("STRIVE", 990, 450, 582),
                                            ("TO SUCCESS", 1410, 582, 720))):
        s.say(line, (432, y0, x1, y1), KANIT, 700, BLACK, f"Título {i + 1}" if i else "Título", align="left",
              layers=[shadow(RED, 8, 8), fill(BLACK)], geom=lambda fr, u: (shift(fr), 0, 1, 0, 1))
    s.rect("Signo (caja)", solid(BLACK), lambda fr, u: (90, 318, 90 + 318 * k(fr, 6, 12), 702))
    s.say("!", (200, 360, 300, 660), M, 900, WHITE, "Signo", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 15, 4)))
    c = s.say("BELIEVE YOU CAN!", (432, 726, 810, 750), M, 900, BLACK, "Texto", align="left")
    s.typed(c, 21, stagger=0.04, duration=0.03, order="backward")
    s.say("Success is never accidental!", (432, 772, 790, 788), M, 600, BLACK, "Texto 2", align="left",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 0, 6)))
    s.outline("Etiqueta", [(1650, 360), (1632, 360), (1632, 720), (1758, 720), (1758, 360), (1740, 360)], 6, BLACK,
              at=21, n=12, closed=False)
    lab = s.say("BELIEVE YOU CAN!", (1540, 528, 1850, 552), M, 800, BLACK, "Texto 3",
                geom=lambda fr, u: (0, 0, 1, 0, k(fr, 27, 6)))
    s.turn(lab, -90)
    return t


# --- 5. Newest: the outlined word unrolls from the right along a line, a green bar grows -------------------------
def newest():
    D = dur_for(1.6)
    t = _p("newest", "Título: palabra en contorno con barra verde", "Title: outlined word with a green bar", 8924, D,
           ["contorno"])
    s = S(t, D)
    bg(s, BLACK)
    s.rect("Línea", solid("#BBBBBB"), lambda fr, u: (1920 - 1930 * k(fr, 0, 9), 538, 1930, 541))
    s.say("Newest", (330, 360, 1662, 648), M, 500, WHITE, layers=outline_layers("#9A9A9A", 2),
          reveal=lambda fr: (1700 - 1500 * k(fr, 0, 15), 0, 1930, 1080))
    s.rect("Barra", solid("#1ED52A"), lambda fr, u: (270, 510, 270 + 450 * k(fr, 9, 9) + 330 * k(fr, 18, 30), 570),
           op=lambda fr, u: k(fr, 9, 1))
    dots(s, 180, 918, WHITE, 3)
    return t


# --- 6. dynamic title concept: a line becomes a frame, the words rise in, a blue exclamation sign --------------
def dynamic():
    D = dur_for(2.6)
    t = _p("dynamic", "Título: marco que se cierra y signo azul", "Title: closing frame and a blue sign", 8925, D,
           ["marco"])
    s = S(t, D)
    bg(s, WHITE)
    left = lambda fr: 168 * (1 - k(fr, 30, 24))  # noqa: E731
    right = lambda fr: 1590 - 330 * k(fr, 36, 30)  # noqa: E731
    s.rect("Marco (arriba)", solid(BLACK), lambda fr, u: (right(fr) - (right(fr) - 342 - left(fr)) * k(fr, 0, 9), 336,
                                                          right(fr), 344))
    s.rect("Marco (izq.)", solid(BLACK), lambda fr, u: (342 + left(fr), 336, 350 + left(fr), 336 + 396 * k(fr, 9, 6)))
    s.rect("Marco (abajo)", solid(BLACK), lambda fr, u: (342 + left(fr), 724, 342 + left(fr) + (right(fr) - 342 - left(fr))
                                                         * k(fr, 12, 9), 732))
    s.rect("Marco (der.)", solid(BLACK), lambda fr, u: (right(fr) - 8, 732 - 396 * k(fr, 30, 9), right(fr), 732))
    c = s.say("dynamic", (420, 408, 948, 510), M, 900, BLACK, align="left", geom=lambda fr, u: (left(fr), 0, 1, 0, 1))
    s.typed(c, 6, stagger=0.08, duration=0.25, preset="rise")
    c = s.say("title concept", (420, 528, 1182, 642), M, 900, BLACK, "Título 2", align="left",
              geom=lambda fr, u: (left(fr), 0, 1, 0, 1))
    s.typed(c, 30, stagger=0.12, duration=0.3, preset="rise")
    c = s.say("You must have ideas for life.", (432, 650, 948, 670), M, 600, BLACK, "Texto", align="left",
              geom=lambda fr, u: (left(fr), 0, 1, 0, 1))
    s.typed(c, 36, stagger=0.03, duration=0.03)
    s.rect("Signo", solid("#1531F0"), lambda fr, u: (1344, 342, 1440, 342 + 270 * k(fr, 66, 6)),
           path="M 0 0 L 100 0 L 80 100 L 20 100 Z")
    s.obj("Signo (punto)", solid("#1531F0"), lambda fr, u: (1392, 690, 66 * k(fr, 69, 4), 66 * k(fr, 69, 4), 0, 1),
          kind="ellipse")
    return t


# --- 7. HEALTH IS IMPORTANT: a full-screen wall of turned words drifting row by row ------------------------------
def health_wall():
    D = dur_for(1.6, 2.4)
    t = _p("health-wall", "Título: muro de palabras en diagonal", "Title: diagonal wall of words", 8926, D,
           ["diagonal"])
    s = S(t, D)
    bg(s, BLACK)
    for i in range(7):
        d = -1050 + 350 * i

        def g(fr, u, d=d, i=i):
            drift = (160 * u + 400 * (1 - k(fr, 0, 18))) * (1 if i % 2 else -1)
            a = math.radians(-35)
            return (-math.sin(a) * d + math.cos(a) * drift, math.cos(a) * d + math.sin(a) * drift, 1, 0,
                    k(fr, 2 * i, 6))
        s.say("HEALTH IS IMPORTANT HEALTH IS IMPORTANT", (-1200, 400, 3120, 680), M, 900, WHITE, f"Trama {i + 1}",
              editable=False, geom=g, rot=lambda fr, u: -35)
    return t


# --- 8. health square: two rows of words scroll behind a square holding the wall, with a gradient border --------
def health_box():
    D = dur_for(1.8)
    t = _p("health-box", "Título: cuadro con muro de palabras entre dos filas", "Title: square holding a word wall "
           "between two rows", 8927, D, ["cuadro"])
    s = S(t, D)
    bg(s, BLACK)
    for i, y in enumerate((240, 600)):
        s.say("HEALTH IS IMPORTANT HEALTH IS IMPORTANT", (-1500, y, 3400, y + 300), M, 900, WHITE, f"Fila {i + 1}",
              editable=False, geom=lambda fr, u, i=i: ((1 if i else -1) * (220 * u + 300 * (1 - k(fr, 0, 18))), 0, 1,
                                                        0, k(fr, 0, 6)))
    size = lambda fr: 540 + 1500 * (1 - k(fr, 0, 21))  # noqa: E731
    s.obj("Cuadro (borde)", [gradient([(0.0, YELLOW), (1.0, "#2F6BFF")], angle=135)],
          lambda fr, u: (960, 540, size(fr) + 24, size(fr) + 24, 0, 1))
    s.obj("Cuadro", solid(BLACK), lambda fr, u: (960, 540, size(fr), size(fr), 0, 1))
    for i in range(5):
        d = -200 + 100 * i
        s.say("HEALTH IS IMPORTANT", (720, 506, 1200, 574), M, 900, WHITE, f"Trama {i + 1}", editable=False,
              reveal=lambda fr: (960 - size(fr) / 2, 540 - size(fr) / 2, 960 + size(fr) / 2, 540 + size(fr) / 2),
              shift=lambda fr, d=d, i=i: (-math.sin(math.radians(-45)) * d, math.cos(math.radians(-45)) * d),
              rot=lambda fr, u: -45)
    s.say("HEALTH IS IMPORTANT", (1290, 440, 1650, 474), M, 900, WHITE, "Texto", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 21, 6)))
    c = s.say("take care of yourself", (1340, 482, 1600, 504), M, 500, WHITE, "Texto 2", italic=True)
    s.typed(c, 24, stagger=0.03, duration=0.03)
    return t


# --- 9. deal with science: a black box opens with the words huge inside, they settle; a line and a sentence -----
def science():
    D = dur_for(2.0)
    t = _p("ciencia", "Título: caja negra con letra de molde", "Title: black box with slab letters", 8928, D, ["slab"])
    s = S(t, D)
    bg(s, WHITE)
    box = lambda fr: (lambda q: (960 - 324 * q, 498 - 180 * q, 960 + 324 * q, 498 + 180 * q))(k(fr, 0, 9))  # noqa: E731
    s.rect("Caja", solid(BLACK), lambda fr, u: box(fr))
    s.say("with", (720, 380, 1200, 620), SLAB, 900, WHITE, "Título (entrada)", editable=False, reveal=lambda fr: box(fr),
          shift=lambda fr: (0, 120 - 120 * k(fr, 3, 36)), op=lambda fr, u: 1.0 if fr < 42 else 0.0)
    for i, (line, x1, y0, y1) in enumerate((("deal", 930, 330, 440), ("with", 930, 440, 550),
                                            ("science", 1230, 550, 668))):
        s.say(line, (690, y0, x1, y1), SLAB, 900, WHITE, f"Título {i + 1}" if i else "Título", align="left",
              geom=lambda fr, u: (0, 0, 1, 0, 1.0 if fr >= 42 else 0.0))
    s.rect("Raya", solid(BLACK), lambda fr, u: (690, 744, 690 + 540 * k(fr, 42, 6), 756))
    c = s.say("Science expands ideas.", (750, 804, 1272, 828), M, 800, BLACK, "Texto")
    s.typed(c, 48, stagger=0.04, duration=0.03, preset="fade", order="random")
    s.outline("Casilla", [(1860, 450), (1860, 570), (1740, 570), (1740, 450), (1860, 450)], 5, BLACK, at=21, n=15,
              closed=False)
    s.outline("Visto", [(1772, 512), (1792, 532), (1828, 492)], 6, BLACK, at=30, n=6, closed=False)
    dots(s, 180, 150, "#2F6BFF", 0)
    dots(s, 180, 918, RED, 3)
    return t


# --- 10. DESIGN enjoy: squares inside squares turn and grow, the word comes in beside, the card pulls back ------
def enjoy():
    D = dur_for(2.6)
    t = _p("enjoy", "Título: cuadros que giran y palabra partida", "Title: turning squares and a split word", 8929, D,
           ["cuadro"])
    s = S(t, D)
    bg(s, BLACK)
    card = lambda fr: 1 - 0.07 * k(fr, 57, 18)  # noqa: E731
    s.obj("Tarjeta", solid(WHITE), lambda fr, u: (954, 546, 1920 * card(fr), 1080 * card(fr), 0, 1))
    cx = lambda fr: 960 - 195 * k(fr, 57, 12)  # noqa: E731
    big = lambda fr: 480 * k(fr, 0, 27)  # noqa: E731
    s.obj("Cuadro", solid(BLACK), lambda fr, u: (cx(fr), 540, big(fr), big(fr), 20 * (1 - k(fr, 0, 27)), 1))
    s.obj("Cuadro 2", solid(WHITE), lambda fr, u: (cx(fr), 540, big(fr) * 0.72 * (1 - k(fr, 18, 9)),
                                                   big(fr) * 0.72 * (1 - k(fr, 18, 9)), 35 * (1 - k(fr, 0, 27)), 1))
    s.obj("Cuadro 3", solid(BLACK), lambda fr, u: (cx(fr), 540, big(fr) * 0.4 * (1 - k(fr, 18, 9)),
                                                   big(fr) * 0.4 * (1 - k(fr, 18, 9)), 50 * (1 - k(fr, 0, 27)), 1))
    s.say("PA", (cx(0) - 230, 330, cx(0) + 200, 760), M, 900, WHITE, "Trama", editable=False,
          reveal=lambda fr: (cx(fr) - 240, 300, cx(fr) + 240, 780), rot=lambda fr, u: 30,
          shift=lambda fr: (cx(fr) - 960, 0), op=lambda fr, u: k(fr, 21, 6))
    for line, ink in (("en", (1110, 312, 1190, 352)), ("joy", (1100, 348, 1196, 392))):
        s.say(line, ink, M, 900, WHITE, "Texto" if line == "en" else "Texto 2",
              geom=lambda fr, u: (cx(fr) - 960, 0, 1, 0, k(fr, 24, 6)))
    for i, (line, y0, y1) in enumerate((("DE", 300, 420), ("SIG", 420, 600), ("N", 600, 780))):
        c = s.say(line, (1032, y0 + 10, 1380 if i == 1 else 1260 if i == 0 else 1130, y1 - 10), M, 900, BLACK,
                  f"Título {i + 1}" if i else "Título", align="left")
        s.typed(c, 60 + 3 * i, stagger=0.06, duration=0.15, preset="fade")
    c = s.say("Graphic design", (540, 812, 780, 832), M, 600, BLACK, "Texto 3", align="left")
    s.typed(c, 60, stagger=0.03, duration=0.03)
    return t


# --- 11. BIG: grey bands rise, a black box drops with a blue shadow, two coloured squares pop and straighten ------
def big():
    D = dur_for(2.0)
    t = _p("big", "Título: caja con sombra y dos cuadros de color", "Title: box with a shadow and two colour squares",
           8930, D, ["cuadros"])
    s = S(t, D)
    for i, colour in enumerate(("#3A3A3A", "#9A9A9A", "#E5E5E5")):
        s.rect(f"Fondo {i + 1}" if i else "Fondo", solid(colour), lambda fr, u, i=i: (-10, 1090 - 1100 * k(fr, 3 * i, 12),
                                                                                   1930, 1090))
    drop = lambda fr: -540 * (1 - k(fr, 9, 12))  # noqa: E731
    s.obj("Sombra", [gradient([(0.0, "#2F2BFF"), (1.0, "#14C8E8")], angle=0)],
          lambda fr, u: (963 + 30 * k(fr, 21, 9), 534 + drop(fr) + 30 * k(fr, 21, 9), 354, 348, 0, 1))
    s.rect("Caja", solid(BLACK), lambda fr, u: (786, 360 + drop(fr), 1140, 708 + drop(fr)))
    s.say("BIG", (840, 470, 1086, 600), M, 900, WHITE, geom=lambda fr, u: (0, drop(fr), 1, 0, 1))
    for i, (rect, colour, deg, at) in enumerate((((414, 498, 768, 852), "#2F2BEF", -15, 30),
                                                 ((1188, 210, 1536, 558), "#F2384A", 15, 30))):
        x0, y0, x1, y1 = rect
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        sz = lambda fr, at=at: k(fr, at, 9)  # noqa: E731
        tilt = lambda fr, deg=deg, at=at: deg * (1 - k(fr, at + 6, 9))  # noqa: E731
        start = (960 + (cx - 960) * 0.6, 540 + (cy - 540) * 0.6)
        pos = lambda fr, cx=cx, cy=cy, start=start, at=at: (start[0] + (cx - start[0]) * k(fr, at, 12),
                                                             start[1] + (cy - start[1]) * k(fr, at, 12))  # noqa: E731
        s.obj(f"Cuadro {i + 1}", solid(colour), lambda fr, u, pos=pos, sz=sz, tilt=tilt, w=x1 - x0: (
            pos(fr)[0], pos(fr)[1], w * sz(fr), w * sz(fr), tilt(fr), 1))
        ink = (cx - 120, cy - 64, cx + 120, cy + 64)
        s.say("BIG", ink, M, 900, WHITE, f"Texto {i + 1}",
              geom=lambda fr, u, ink=ink, pos=pos, sz=sz, tilt=tilt: (pos(fr)[0] - (ink[0] + ink[2]) / 2,
                                                                      pos(fr)[1] - (ink[1] + ink[3]) / 2,
                                                                      max(0.01, sz(fr)), tilt(fr), 1))
    c = s.say("BIG GRAPHIC DESIGN", (234, 92, 738, 112), M, 800, BLACK, "Texto 3", align="left")
    s.typed(c, 39, stagger=0.04, duration=0.03)
    dots(s, 180, 912, "#2F2BEF", 15)
    c = s.say("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore.",
              (440, 1032, 1480, 1046), M, 700, BLACK, "Texto 4")
    s.typed(c, 24, stagger=0.006, duration=0.03)
    return t


# --- 12. UNIVERSAL FASHION SENSE: a photo seen through three rows of huge letters, a white box is typed ----------
def fashion():
    D = dur_for(2.4)
    t = _p("fashion", "Título: foto dentro de letras gigantes y caja", "Title: photo inside giant letters and a box",
           8931, D, ["foto", "moda"])
    s = S(t, D)
    bg(s, BLACK)
    rows = (("FASHION", 240, 1900, 400, 680, 6), ("UNIVERSAL", -80, 2300, 120, 400, 21),
            ("SENSE", 420, 1700, 680, 960, 24))
    for i, (word, x0, x1, y0, y1, at) in enumerate(rows):
        cy = (y0 + y1) / 2
        masked_photo(s, "fx-car-01", word, lambda fr, x0=x0, x1=x1, y0=y0, y1=y1, cy=cy, at=at, i=i: (
            x0, cy - (cy - y0) * (k(fr, at, 18) if i == 0 else 1), x1, cy + (y1 - cy) * (k(fr, at, 18) if i == 0 else 1)),
            name=f"Foto {i + 1}")
        if i:
            s.t.tracks[-1].clips[-1]["opacity"] = keys([(u, round(k(s.frame(u), at, 9), 4), "linear")
                                                        for u in frames_of(D)])
    s.rect("Línea", solid(WHITE), lambda fr, u: (-10, 552, 678 * k(fr, 24, 18), 560),
           op=lambda fr, u: 1 - k(fr, 42, 2))
    s.rect("Caja", solid(WHITE), lambda fr, u: (-10, 556 - 286 * k(fr, 42, 6), 678, 556 + 296 * k(fr, 42, 6)))
    for i, (line, x1, y0, y1) in enumerate((("UNIVERSAL", 648, 420, 492), ("FASHION", 528, 492, 570),
                                            ("SENSE", 390, 570, 654))):
        c = s.say(line, (48, y0, x1, y1), M, 900, "#F5A300", f"Texto {i + 1}", align="left")
        s.typed(c, 48 + 3 * i, stagger=0.05, duration=0.05, preset="fade")
    c = s.say("AUTO UNDERSTANDING", (48, 672, 360, 700), M, 900, BLACK, "Texto 4", align="left")
    s.typed(c, 57, stagger=0.03, duration=0.03)
    dots(s, 180, 1032, WHITE, 6)
    return t


# --- 13. TYPOGRAPHY: the word is typed over the photo, the photo pulls back to a card among turned letters -------
def typography():
    D = dur_for(2.2)
    t = _p("typography", "Título: tarjeta rosa y letras alrededor", "Title: pink card with letters around", 8932, D,
           ["foto"])
    s = S(t, D)
    bg(s, WHITE)
    for i, (x, colour, deg) in enumerate(((100, "#1B1F4A", -90), (1800, "#E8365D", 90), (1880, "#1B1F4A", 90))):
        s.say("TYPOGRAPHY TYPOGRAPHY", (x - 700, 470, x + 700, 610), M, 900, colour, f"Trama {i + 1}", editable=False,
              geom=lambda fr, u, i=i: (0, (1 if i % 2 else -1) * 140 * u, 1, 0, 1), rot=lambda fr, u, deg=deg: deg)
    for i, (y, colour) in enumerate(((1000, "#E8365D"),)):
        s.say("YOYOYOYOYOYOYOYOYO", (-100, y - 70, 2000, y + 90), M, 900, colour, "Trama 4", editable=False,
              geom=lambda fr, u: (-140 * u, 0, 1, 0, 1))
    card = lambda fr: (lambda q: (-10 + 220 * q, -10 + 142 * q, 1930 - 220 * q, 1090 - 130 * q))(k(fr, 0, 15))  # noqa: E731
    photo(s, "fx-concert-02", lambda fr, u: card(fr))
    s.rect("Tinte", solid("#E8365D", 0.55), lambda fr, u: card(fr))
    c = s.say("TYPOGRAPHY", (588, 450, 1440, 612), NAME, 400, WHITE)
    s.typed(c, 0, stagger=0.05, duration=0.15, preset="drop")
    c = s.say("Typography is a fundamental element of graphic art.", (700, 624, 1330, 642), M, 700, WHITE, "Texto")
    s.typed(c, 15, stagger=0.015, duration=0.03)
    s.outline("Casilla", [(1632, 270), (1632, 432), (1452, 432), (1452, 270), (1632, 270)], 4, WHITE, at=33, n=18,
              closed=False)
    s.obj("Visto (aro)", ring(WHITE, 4), lambda fr, u: (1542, 351, 70, 70, 0, k(fr, 42, 4)), kind="ellipse")
    s.outline("Visto", [(1522, 352), (1538, 368), (1564, 336)], 5, WHITE, at=45, n=6, closed=False)
    return t


# --- 14. ART ALWAYS!: each letter appears red, then cyan, then white ---------------------------------------------
def art_always():
    D = dur_for(1.8)
    t = _p("art-always", "Título: letras en rojo, celeste y blanco", "Title: letters in red, cyan and white", 8933, D,
           ["glitch"])
    s = S(t, D)
    bg(s, BLACK)
    for name, colour, dx, lag in (("rojo", "#FF3A1A", -12, 0), ("cian", "#22C8F0", -6, 3), ("blanco", WHITE, 0, 6)):
        for line, ink, at in (("ART", (720, 348, 1152, 492), 0), ("ALWAYS!", (516, 528, 1416, 684), 6)):
            main = name == "blanco"
            c = s.say(line, ink, M, 900, colour, ("Texto" if line == "ART" else "Título") if main else
                      f"Glitch {name} {line}", editable=main,
                      geom=lambda fr, u, dx=dx: (dx * (1 - k(fr, 30, 9)), 0, 1, 0, 1))
            s.typed(c, at + lag, stagger=0.08, duration=0.05)
    s.outline("Icono", [(552, 372), (690, 372), (690, 480), (552, 480), (552, 372)], 4, WHITE, at=24, n=12,
              closed=False)
    c = s.say("GRAPHICS IS THE FOREMOST ART FORM", (630, 712, 1320, 730), M, 900, WHITE, "Texto 2")
    s.typed(c, 15, stagger=0.03, duration=0.03)
    for i, line in enumerate(("Lorem ipsum dolor sit amet,", "consectetur adipiscing elit, sed do eiusmod",
                              "tempor incididunt ut labore et dolore magna aliqua.")):
        c = s.say(line, (732, 768 + 20 * i, 1188, 782 + 20 * i), M, 500, WHITE, f"Texto {i + 3}")
        s.typed(c, 21 + 3 * i, stagger=0.01, duration=0.03)
    return t


# --- 15. CONCEPT (blue): the word is typed letter by letter, the letters darken in ---------------------------------
def concept_blue():
    D = dur_for(1.6)
    t = _p("concept-azul", "Título: palabra ancha sobre azul", "Title: wide word on blue", 8934, D, ["azul"])
    s = S(t, D)
    bg(s, BLUE)
    c = s.say("CONCEPT", (570, 468, 1338, 618), M, 900, "#111111")
    s.typed(c, 6, stagger=0.12, duration=0.3, preset="fade")
    c = s.say("MOTION GRAPHIC DESIGN", (1080, 440, 1320, 458), NAME, 400, WHITE, "Texto")
    s.typed(c, 12, stagger=0.03, duration=0.03)
    dots(s, 180, 912, WHITE, 6)
    s.outline("Icono", [(570, 930), (630, 930), (630, 966), (570, 966), (570, 930)], 3, WHITE, at=15, n=9, closed=False)
    return t


# --- 16. CONCEPT (dark): the blue screen pulls back into a box over big pale letters; icons draw ---------------
def concept_dark():
    D = dur_for(1.8)
    t = _p("concept-oscuro", "Título: caja azul sobre letras grandes", "Title: blue box over big letters", 8935, D,
           ["azul"])
    s = S(t, D)
    bg(s, "#151515")
    s.say("CONCEPT", (-400, -100, 2400, 1180), M, 900, "#262626", "Fondo (texto)", editable=False,
          geom=lambda fr, u: (-60 * u, 0, 1, 0, 1))
    sc = lambda fr: 1 - 0.47 * k(fr, 0, 21)  # noqa: E731
    s.obj("Caja", solid(BLUE), lambda fr, u: (960, 537, 1920 * (1 - 0.53 * k(fr, 0, 21)), 1080 * (1 - 0.81 * k(fr, 0, 21)),
                                              0, 1))
    s.say("CONCEPT", (570, 468, 1338, 618), M, 900, "#111111", geom=lambda fr, u: (0, 0, 1 - 0.0 * sc(fr), 0, 1))
    s.say("MOTION GRAPHIC DESIGN", (1080, 440, 1320, 458), NAME, 400, WHITE, "Texto")
    for i in range(5):
        x = 600 + 170 * i
        s.outline(f"Icono {i + 1}", [(x, 920), (x + 64, 920), (x + 64, 980), (x, 980), (x, 920)], 3, WHITE,
                  at=18 + 4 * i, n=9, closed=False)
    dots(s, 180, 912, WHITE, 0)
    return t


# --- 17. modern typography titles: the serif words are typed, the number pops, a red line --------------------------
def modern():
    D = dur_for(1.8)
    t = _p("modern", "Título: serif elegante con número", "Title: elegant serif with a number", 8936, D, ["serif"])
    s = S(t, D)
    bg(s, WHITE)
    shift = lambda fr: (66 * k(fr, 30, 9), 36 * k(fr, 30, 9))  # noqa: E731
    for name, text, ink, at in (("Texto", "modern", (444, 384, 756, 450), 0),
                                ("Título", "typography", (444, 462, 1290, 612), 3),
                                ("Texto 2", "titles", (444, 600, 642, 684), 21)):
        c = s.say(text, ink, SERIF, 400, BLACK, name, align="left",
                  geom=lambda fr, u: (shift(fr)[0] - 66, shift(fr)[1] - 36, 1, 0, 1))
        s.typed(c, at, stagger=0.06, duration=0.2, preset="fade")
    c = s.say("01", (498, 198, 750, 408), M, 900, BLACK, "Número", align="left")
    s.typed(c, 39, stagger=0.1, duration=0.15, preset="pop")
    c = s.say("modern compact design", (510, 740, 930, 762), M, 600, RED, "Texto 3", align="left")
    s.typed(c, 27, stagger=0.04, duration=0.05, preset="fade", order="random")
    return t


# --- 18. LOOK: giant white letters on black, a hatched panel, LO OK typed in it and a blue frame ---------------
def look():
    D = dur_for(2.4)
    t = _p("look", "Título: letras gigantes y marco azul", "Title: giant letters and a blue frame", 8937, D, ["marco"])
    s = S(t, D)
    bg(s, WHITE)
    slide = lambda fr: 300 * (1 - k(fr, 0, 36))  # noqa: E731
    s.rect("Negro", solid(BLACK), lambda fr, u: (450 + slide(fr), -10, 1530 + slide(fr), 1090))
    s.say("OK", (300, -120, 1700, 1300), M, 900, WHITE, "Fondo (texto)", editable=False,
          reveal=lambda fr: (450 + slide(fr), -10, 1530 + slide(fr), 1090), shift=lambda fr: (slide(fr), -40 * (1 - k(fr, 0, 36))))
    hatch = " ".join(f"M {i * 4.0:.1f} 0 L {i * 4.0 + 1.0:.1f} 0 L {i * 4.0 - 14:.1f} 100 L {i * 4.0 - 15:.1f} 100 Z"
                     for i in range(4, 30))
    s.rect("Panel", solid(WHITE), lambda fr, u: (990 + slide(fr), -10, 1530 + slide(fr), 1090))
    s.rect("Rayas", solid(BLACK), lambda fr, u: (990 + slide(fr), -10, 1530 + slide(fr), 1090), path=hatch)
    s.rect("Caja", solid(WHITE), lambda fr, u: (1110 + slide(fr), 330, 1446 + slide(fr), 750), op=lambda fr, u: k(fr, 24, 3))
    for name, text, ink, at in (("Texto", "LO", (1152, 390, 1392, 528), 27), ("Texto 2", "OK", (1152, 552, 1392, 708), 30)):
        c = s.say(text, ink, M, 900, BLACK, name, geom=lambda fr, u: (slide(fr), 0, 1, 0, 1))
        s.typed(c, at, stagger=0.1, duration=0.1, preset="fade")
    c = s.outline("Marco", [(1458, 312), (1458, 768), (1098, 768), (1098, 312), (1458, 312)], 8, "#18B7F2", at=57, n=15,
                  closed=False)
    s.rect("Negro 2", solid(BLACK), lambda fr, u: (1530 + slide(fr), -10, 1930, 1090))
    s.rect("Etiqueta", solid(BLACK), lambda fr, u: (-10, 528, 390 * k(fr, 54, 9), 576))
    c = s.say("graphicdesign", (60, 538, 330, 566), M, 600, WHITE, "Texto 3", align="left")
    s.typed(c, 57, stagger=0.03, duration=0.03)
    lab = s.say("/ modern compact design", (1700, 528, 2000, 548), M, 500, RED, "Texto 4",
                geom=lambda fr, u: (0, 0, 1, 0, k(fr, 18, 6)))
    s.turn(lab, -90)
    return t


# --- 19. EASY EDITING: the red letters light up out of order over a yellow word pattern; a giant word rises ------
def easy_editing():
    D = dur_for(2.6)
    t = _p("easy-editing", "Título: letras rojas sobre trama amarilla", "Title: red letters on a yellow pattern",
           8938, D, ["amarillo"])
    s = S(t, D)
    bg(s, WHITE)
    for i in range(6):
        d = -900 + 330 * i
        s.say("EFFECTS PRESETS EFFECTS", (-900, 420, 2820, 690), M, 900, YELLOW, f"Trama {i + 1}", editable=False,
              layers=[shadow(BLACK, 0, 16), fill(YELLOW)],
              geom=lambda fr, u, d=d, i=i: (math.sin(math.radians(15)) * d + (1 if i % 2 else -1) * 90 * u,
                                            math.cos(math.radians(15)) * d, 1, 0, 1), rot=lambda fr, u: -75)
    lift = lambda fr: 0  # noqa: E731
    c = s.say("EASY", (132, 270, 870, 540), M, 900, RED, align="left", geom=lambda fr, u: (0, lift(fr), 1, 0, 1))
    s.typed(c, 3, stagger=0.12, duration=0.3, preset="fade", order="random")
    c = s.say("EDITING", (132, 570, 1320, 810), M, 900, RED, "Título 2", align="left",
              geom=lambda fr, u: (0, lift(fr), 1, 0, 1))
    s.typed(c, 6, stagger=0.1, duration=0.3, preset="fade", order="random")
    s.rect("Subrayado", solid("#1531F0"), lambda fr, u: (132, 814, 132 + 1188 * k(fr, 18, 18), 826))
    s.rect("Línea", solid(BLACK), lambda fr, u: (-10, 838, 1930 * k(fr, 42, 12), 846))
    s.say("EASY", (60, 870, 1860, 1400), M, 900, BLACK, "Texto 3", reveal=lambda fr: (-10, 846, 1930, 1090),
          shift=lambda fr: (0, 300 * (1 - k(fr, 42, 30))), op=lambda fr, u: k(fr, 42, 2))
    for i, line in enumerate(("AFTER EFFECTS TEMPLATE", "NO PLUGINS REQUIRED")):
        c = s.say(line, (880, 450 + 32 * i, 1200, 474 + 32 * i), NAME, 400, BLACK, f"Texto {i + 4}", align="left")
        s.typed(c, 45 + 3 * i, stagger=0.04, duration=0.03)
    return t


# --- 20. Colorful scenes: a photo band opens from a line, a white band grows, the photo shows through the word ----
def colorful():
    D = dur_for(2.0)
    t = _p("colorful", "Título: banda blanca con la foto dentro de la palabra", "Title: white band with the photo inside "
           "the word", 8939, D, ["foto"])
    s = S(t, D)
    bg(s, BLACK)
    photo(s, "fx-cyber-04", lambda fr, u: (-10, 534 - 414 * k(fr, 0, 27), 1930, 546 + 402 * k(fr, 0, 27)))
    s.rect("Banda", solid(WHITE), lambda fr, u: (-10, 538 - 268 * k(fr, 21, 9), 1930, 542 + 268 * k(fr, 21, 9)))
    masked_photo(s, "fx-cyber-04", "Colorful", lambda fr: (978, 318, 1860, 498) if fr >= 27 else (1418, 408, 1420, 409),
                 name="Foto (palabra)")
    c = s.say("scenes", (1050, 528, 1860, 720), M, 800, "#0E0E2A", "Título 2")
    s.typed(c, 30, stagger=0.1, duration=0.2, preset="rise")
    for i, line in enumerate(("Sed ut perspiciatis unde omnis iste natus error", "sit voluptatem accusantium doloremque",
                              "laudantium, totam rem aperiam")):
        c = s.say(line, (1300, 726 + 18 * i, 1860, 740 + 18 * i), M, 600, BLACK, f"Texto {i + 1}", align="right")
        s.typed(c, 42 + 2 * i, stagger=0.01, duration=0.03)
    dots(s, 180, 900, WHITE, 6)
    return t


# --- 21. CREATE AND AESTHETIC: grey words light up around, a white card opens with the black words -------------
def create():
    D = dur_for(2.6)
    t = _p("create", "Título: palabras grises y tarjeta blanca", "Title: grey words and a white card", 8940, D)
    s = S(t, D)
    bg(s, BLACK)
    for i, (y, line) in enumerate(((60, "CREATE   AESTHETIC   AND"), (330, "AND   CREATE   AESTHETIC"),
                                   (600, "AESTHETIC   AND   CREATE"), (870, "CREATE   AND   AESTHETIC"))):
        c = s.say(line, (-200, y, 2200, y + 220), M, 900, "#5A5A5A", f"Trama {i + 1}", editable=False)
        s.typed(c, 0, stagger=0.04, duration=0.3, preset="fade", order="random")
    card = lambda fr: (lambda q: (960 - 970 * q, 540 - 550 * q, 960 + 970 * q, 540 + 550 * q))(k(fr, 39, 15))  # noqa: E731
    s.rect("Tarjeta", solid(WHITE), lambda fr, u: card(fr))
    sc = lambda fr: 1.4 - 0.4 * k(fr, 45, 18)  # noqa: E731
    for i, (line, x0, x1, y0, y1) in enumerate((("CREATE", 210, 1308, 108, 360), ("AND", 390, 1050, 390, 630),
                                                ("AESTHETIC", 0, 1530, 660, 912))):
        ink = (x0, y0, x1, y1)
        s.say(line, ink, M, 900, BLACK, f"Título {i + 1}" if i else "Título",
              geom=with_op(cam(ink, sc, 765, 510), lambda fr, u: k(fr, 42, 3)))
    c = s.say("NEWVISION", (1350, 456, 1710, 486), M, 900, BLACK, "Texto", align="left")
    s.typed(c, 60, stagger=0.05, duration=0.03)
    for i, line in enumerate(("Lorem ipsum dolor sit amet,", "consectetur adipiscing elit,")):
        c = s.say(line, (1350, 504 + 22 * i, 1710, 520 + 22 * i), M, 500, BLACK, f"Texto {i + 2}", align="left")
        s.typed(c, 66 + 3 * i, stagger=0.01, duration=0.03)
    s.say("01", (30, 30, 96, 70), M, 900, BLACK, "Número", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 57, 4)))
    dots(s, 180, 1008, RED, 57)
    return t


# --- 22. TEXT ANIMATION: white curves draw over a photo, the rows are typed in black --------------------------
def text_animation():
    D = dur_for(1.8)
    t = _p("text-animation", "Título: filas de texto sobre foto", "Title: rows of text over a photo", 8941, D,
           ["foto"])
    s = S(t, D)
    photo(s, "fx-cyber-03")
    for i, pts in enumerate(([(560, 1080), (480, 760), (620, 520), (1180, 420), (1420, 620), (1340, 980)],
                             [(1900, 120), (1500, 300), (1300, 700), (1500, 1080)])):
        s.outline(f"Curva {i + 1}", pts, 4, WHITE, at=3 * i, n=15, closed=False)
    for i in range(3):
        y = 140 + 300 * i
        c = s.say("TEXT ANIMATION", (-30, y, 1980, y + 250), M, 900, BLACK, f"Título {i + 1}" if i else "Título",
                  align="left")
        s.typed(c, 9 + 3 * i, stagger=0.06, duration=0.1, preset="fade")
    return t


TEMPLATES = [love, scene, never_give_up, always_strive, newest, dynamic, health_wall, health_box, science, enjoy, big,
             fashion, typography, art_always, concept_blue, concept_dark, modern, look, easy_editing, colorful, create,
             text_animation]
