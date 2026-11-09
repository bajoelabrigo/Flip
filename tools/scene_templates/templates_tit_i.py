"""Black and white kinetic titles, sixth TITLE set redone (2026-11-08, Jorge: «lo más parecido posible, no
inventes»): the pieces of 35149534.mp4 (960×540 at 25 fps, laid out at 1920×1080), each with the moves of the
reference studied on 10 fps sheets: words typed letter by letter, letters that rise or fall in, a camera that pulls
back once the words are written, frames and crossing lines that draw themselves, panels that wipe across and turn
the words from black to white, photos inside the letters (a text mask). Kit de YouTube › Tipografía; ids `tit6-*`
(they replace `templates_tit_f`), order 8900-. Study notes in tienda/plantillas/estudio-35149534/NOTAS.md.

Each slide plays its entrance, holds, and leaves with its entrance backwards at 2.5× speed (the reference cuts).
"""

from __future__ import annotations

import math

from kit import wide
from llt_motion import frames_of
from scene import keys
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_f import outline_layers
from templates_tit_h import EXIT, S, lin, ring, rot_pt

WHITE, BLACK, GREY = "#FFFFFF", "#000000", "#9A9A9A"
M, NAME = "Montserrat", "Bebas Neue"


def _p(id, es, en, order, dur, tags=()):
    return wide(f"tit6-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:tipografia", "tipografía", "blanco y negro", "cinético"] + list(tags),
                thumb_at=round(dur * 0.55, 1))


def dur_for(entrance, hold=1.4):
    return round(entrance + hold + entrance / EXIT, 1)


def cam(ink, sc, px, py, extra=(0.0, 0.0)):
    """geom for a text that a camera scales by sc about (px, py)."""
    def g(fr, u):
        s_ = sc(fr) if callable(sc) else sc
        cx, cy = (ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2
        e = extra(fr) if callable(extra) else extra
        return px + (cx + e[0] - px) * s_ - cx, py + (cy + e[1] - py) * s_ - cy, s_, 0, 1
    return g


def with_op(g, op):
    return lambda fr, u: (lambda v: (v[0], v[1], v[2], v[3], op(fr, u)))(g(fr, u))


def masked_photo(s, sample, word, rect, name="Foto"):
    """A photo slot over the whole frame, cut to the shape of `word` fitted to rect(fr) = (x0, y0, x1, y1)."""
    t = s.t
    clip = t.photo(t.track("video", name), sample, 0.0, s.dur, None, None, label="Tu foto")
    track = next(tr for tr in t.tracks if clip in tr.clips)
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u in frames_of(s.dur):
        x0, y0, x1, y1 = rect(s.frame(u))
        mk["x"].append((u, (x0 + x1) / 2 / 1920, "linear"))
        mk["y"].append((u, (y0 + y1) / 2 / 1080, "linear"))
        mk["w"].append((u, max(1e-3, (x1 - x0) / 1920), "linear"))
        mk["h"].append((u, max(1e-3, (y1 - y0) / 1080), "linear"))
    t.mask(track, clip, "text", text=word, x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
           keyframes={kk: keys(v) for kk, v in mk.items()})
    return clip


def bg(s, colour):
    return s.rect("Fondo", solid(colour), lambda fr, u: (-10, -10, 1930, 1090))


# --- 1. YOU: the photo inside the letters pulls back from the O to the word ---------------------------------------
def you():
    D = dur_for(1.8)
    t = _p("you", "Título: palabra rellena con una foto", "Title: word filled with a photo", 8900, D, ["foto"])
    s = S(t, D)
    bg(s, WHITE)
    final = (528, 420, 1290, 690)
    ox, oy = 960, 555

    def rect(fr):
        z = 1 + 9 * (1 - k(fr, 0, 18))
        return tuple(ox + (v - ox) * z if i % 2 == 0 else oy + (v - oy) * z for i, v in enumerate(final))
    masked_photo(s, "fx-face-01", "YOU", rect)
    s.rect("Cursor", solid(BLACK), lambda fr, u: (1180, 712, 1186, 760), op=lambda fr, u: k(fr, 27, 2) * (1 - k(fr, 36, 2)))
    s.rect("Raya", solid(BLACK), lambda fr, u: (1158 - 228 * k(fr, 36, 9), 708, 1186 + 146 * k(fr, 36, 9), 738))
    c = s.say("AND GRAPHIC DESIGN!", (1020, 780, 1344, 810), NAME, 400, BLACK, "Texto")
    s.typed(c, 39, stagger=0.03, duration=0.03)
    return t


# --- 2. 0.1 BIG TEXT: the number, the outlined words typed, the camera pulls back, a pill draws, a photo opens ----
def big_text():
    D = dur_for(2.9)
    t = _p("big-text", "Título: número, texto con contorno y foto", "Title: number, outlined words and a photo",
           8901, D, ["contorno", "foto"])
    s = S(t, D)
    bg(s, WHITE)
    sc = lambda fr: 1.37 - 0.37 * k(fr, 30, 18)  # noqa: E731
    px, py = 930, 600
    spread = lambda fr: (228 * (1 - k(fr, 66, 15)) + 300 * (1 - lin(fr, 6, 24)), 0)  # noqa: E731
    s.say("0.1", (336, 480, 528, 600), M, 800, BLACK, "Número", geom=cam((336, 480, 528, 600), sc, px, py, spread))
    big = s.say("BIG TEXT", (528, 480, 1188, 600), M, 800, BLACK, layers=outline_layers(BLACK, 3),
                geom=cam((528, 480, 1188, 600), sc, px, py, spread))
    s.typed(big, 6, stagger=0.1, duration=0.04)
    s.say("UPDATE 0.1 TITLES PACK", (720, 618, 1170, 642), M, 800, BLACK, "Texto",
          geom=with_op(cam((720, 618, 1170, 642), sc, px, py, spread), lambda fr, u: k(fr, 39, 6)))
    r, x0, x1, cy = 78, 270, 1524, 858
    pts = [(x1 - r + r * math.cos(a * math.pi / 12), cy + r * math.sin(a * math.pi / 12)) for a in range(0, 7)]
    pts += [(x0 + r + r * math.cos(a * math.pi / 12), cy + r * math.sin(a * math.pi / 12)) for a in range(6, 19)]
    pts += [(x1 - 260, cy - r)]
    s.outline("Píldora", pts, 4, BLACK, at=18, n=27, closed=False)
    for i in range(3):
        cx = 360 + 80 * i
        s.obj(f"Punto {i + 1}", ring(BLACK, 3), lambda fr, u, cx=cx, i=i: (cx, 858, 56, 56, 0, k(fr, 33 + 3 * i, 6)),
              kind="ellipse")
    s.rect("Raya", solid(BLACK), lambda fr, u: (342, 1036, 342 + 246 * k(fr, 18, 9), 1040))
    s.rect("Barra", solid(BLACK), lambda fr, u: (1500 - 24 * k(fr, 66, 3), 372, 1524, 732), op=lambda fr, u: k(fr, 66, 2))
    ph = s.t.photo(s.t.track("video", "Foto"), "portrait-04", 0.0, D, None, None, label="Tu foto")
    ph["opacity"] = keys([(u, round(k(s.frame(u), 69, 2), 4), "linear") for u in frames_of(D)])
    from llt_motion import mask_track
    from kit import Box
    mask_track(t, ph, Box(0, 0, 1920, 1080), lambda u: (1572 - 348 * k(s.frame(u), 69, 18), 372, 1572, 732), D)
    return t


# --- 3. never give up!: a photo strip, the words typed with the letters popping in --------------------------------
def never_give_up():
    D = dur_for(1.6)
    t = _p("never-give-up", "Título: frase tecleada sobre una franja de foto", "Title: phrase typed over a photo strip",
           8902, D, ["foto"])
    s = S(t, D)
    bg(s, BLACK)
    ph = s.t.photo(s.t.track("video", "Foto"), "portrait-01", 0.0, D, None, None, label="Tu foto")
    from llt_motion import mask_track
    from kit import Box
    mask_track(t, ph, Box(0, 0, 1920, 1080), lambda u: (768, -10, 1158, 1090), D)
    c = s.say("never give up!", (396, 462, 1530, 612), M, 900, WHITE)
    s.typed(c, 0, stagger=0.06, duration=0.12, preset="pop")
    c = s.say("Always stand tall.", (438, 588, 990, 642), M, 800, WHITE, "Texto", align="left")
    s.typed(c, 3, stagger=0.06, duration=0.05)
    for i in range(7):
        s.obj(f"Punto {i + 1}", solid(WHITE), lambda fr, u, i=i: (186 + 28 * i, 906, 10, 10, 0, k(fr, 3 + i, 3)),
              kind="ellipse")
    c = s.say("Do not surrender to circumstances. You create them.", (600, 910, 1320, 928), M, 500, WHITE, "Texto 2")
    s.typed(c, 9, stagger=0.01, duration=0.03)
    return t


# --- 4. ALWAYS STRIVE TO SUCCESS: the letters fall in, then the exclamation sign fades in beside them -------------
def always_strive():
    D = dur_for(1.8)
    t = _p("always-strive", "Título: letras que caen y signo de exclamación", "Title: falling letters and an exclamation "
           "sign", 8903, D, ["condensada"])
    s = S(t, D)
    bg(s, BLACK)
    shift = lambda fr: 276 * (1 - k(fr, 27, 12))  # noqa: E731
    for i, (line, x1, y0, y1, at) in enumerate((("ALWAYS", 780, 258, 378, 0), ("STR", 570, 402, 528, 3),
                                                ("IVE", 552, 546, 666, 6), ("TO SUCCESS", 978, 690, 828, 9))):
        c = s.say(line, (378, y0, x1, y1), NAME, 400, WHITE, f"Título {i + 1}" if i else "Título", align="left",
                  geom=lambda fr, u: (shift(fr), 0, 1, 0, 1))
        s.typed(c, at, stagger=0.05, duration=0.2, preset="drop")
    grey = lambda fr: k(fr, 27, 3) * (0.35 + 0.65 * k(fr, 33, 12))  # noqa: E731
    s.rect("Signo", solid(WHITE), lambda fr, u: (240, 240, 348, 732), op=lambda fr, u: grey(fr),
           path="M 0 0 L 100 0 L 80 100 L 20 100 Z")
    s.rect("Signo (punto)", solid(WHITE), lambda fr, u: (240, 822, 348, 918), op=lambda fr, u: grey(fr))
    s.say("BELIEVE YOU CAN!", (390, 840, 768, 888), NAME, 400, WHITE, "Texto", align="left",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 30, 3) * (0.3 + 0.7 * k(fr, 36, 12))))
    s.say("Success is never accidental!", (390, 900, 870, 924), M, 700, WHITE, "Texto 2", align="left",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 33, 3) * (0.3 + 0.7 * k(fr, 39, 12))))
    return t


# --- 5. Be strong!: a strike line, the words unroll from the right, the camera pulls back into a frame -----------
def be_strong():
    D = dur_for(2.0)
    t = _p("be-strong", "Título: frase tachada que se escribe hacia atrás", "Title: struck phrase unrolling backwards",
           8904, D, ["marco", "tachado"])
    s = S(t, D)
    bg(s, BLACK)
    sc = lambda fr: 1.42 - 0.42 * k(fr, 36, 18)  # noqa: E731
    px, py = 954, 528
    ink = (612, 474, 1308, 588)
    big = tuple(px + (v - px) * 1.42 if i % 2 == 0 else py + (v - py) * 1.42 for i, v in enumerate(ink))
    s.say("Be strong!", big, M, 800, WHITE, "Título (entrada)", editable=False,
          reveal=lambda fr: (1700 - 2400 * k(fr, 3, 18), 0, 1930, 1080), op=lambda fr, u: 1.0 if fr < 36 else 0.0)
    s.say("Be strong!", ink, M, 800, WHITE, geom=with_op(cam(ink, sc, px, py), lambda fr, u: 1.0 if fr >= 36 else 0.0))
    s.obj("Tachado", solid(WHITE), lambda fr, u: (px + (960 - px) * sc(fr), py + (531 - py) * sc(fr),
                                                  740 * sc(fr) * k(fr, 0, 3), 7 * sc(fr), 0, 1))
    s.rect("Marco (bajada)", solid(WHITE), lambda fr, u: (1376, 258, 1382, 258 + 300 * k(fr, 24, 12)),
           op=lambda fr, u: 1 - k(fr, 42, 2))
    fr_pts = [(1380, 258), (1380, 792), (528, 792), (528, 258), (1300, 258)]
    c = s.outline("Marco", fr_pts, 5, WHITE, at=42, n=12, closed=False)
    s.fade(c, lambda fr: k(fr, 42, 1))
    c = s.say("Life is for the strong.", (840, 736, 1080, 752), M, 600, WHITE, "Texto")
    s.typed(c, 54, stagger=0.02, duration=0.03)
    return t


# --- 6. #create new ideas!: the letters rise in, a big hash, the camera pulls back, a line is typed ---------------
def create_ideas():
    D = dur_for(3.4)
    t = _p("create-ideas", "Título: letras que suben y almohadilla", "Title: rising letters and a hash", 8905, D,
           ["hashtag"])
    s = S(t, D)
    bg(s, WHITE)
    sc = lambda fr: 1 - 0.39 * k(fr, 57, 9)  # noqa: E731
    px, py = 945, 542
    c = s.say("create", (360, 342, 1068, 522), M, 800, BLACK, align="left", geom=cam((360, 342, 1068, 522), sc, px, py))
    s.typed(c, 6, stagger=0.1, duration=0.25, preset="rise")
    c = s.say("new ideas!", (360, 528, 1560, 732), M, 800, BLACK, "Título 2", align="left",
              geom=cam((360, 528, 1560, 732), sc, px, py))
    s.typed(c, 27, stagger=0.08, duration=0.25, preset="rise")
    hink = (60, 402, 360, 720)
    s.say("#", hink, M, 900, BLACK, "Signo",
          geom=with_op(cam(hink, sc, px, py), lambda fr, u: k(fr, 57, 2) * (0.6 if fr < 63 else 0.15 + 0.85 * k(fr, 63, 6))))
    c = s.say("You must have ideas for life.", (600, 648, 1176, 696), M, 600, BLACK, "Texto", align="left")
    s.typed(c, 69, stagger=0.06, duration=0.03)
    s.say("Always have new and beautiful projects.", (750, 906, 1158, 918), M, 500, "#555555", "Texto 2")
    return t


# --- 7. Health is important: a strip of turned words between a white half and a black half ----------------------
def health():
    D = dur_for(2.2)
    t = _p("health", "Título: franja de palabras giradas entre blanco y negro", "Title: strip of turned words between "
           "white and black", 8906, D, ["doble"])
    s = S(t, D)
    bg(s, BLACK)
    for i in range(7):
        d = -780 + 260 * i

        def g(fr, u, d=d, i=i):
            drift = 120 * u * (1 if i % 2 else -1)
            return d * 0.866 + drift * 0.5, d * 0.5 - drift * 0.866, 1, 0, 1
        s.say("is important is important", (100, 440, 2300, 640), M, 900, WHITE, f"Trama {i + 1}", editable=False,
              geom=g, rot=lambda fr, u: -60)
    s.rect("Negro", solid(BLACK), lambda fr, u: (1440, -10, 1930, 1090))
    s.rect("Negro 2", solid(BLACK), lambda fr, u: (-10, -10, 960, 1090))
    s.rect("Blanco", solid(WHITE), lambda fr, u: (-10, -10, 960 * k(fr, 18, 6), 1090))
    c = s.say("Health", (1050, 488, 1290, 560), M, 300, WHITE, "Texto", italic=True, align="left")
    s.typed(c, 24, stagger=0.05, duration=0.04)
    c = s.say("is important", (1310, 488, 1800, 560), M, 700, WHITE, align="left")
    s.typed(c, 30, stagger=0.05, duration=0.04)
    c = s.say("take care of yourself", (335, 520, 650, 556), M, 500, BLACK, "Texto 2", italic=True)
    s.typed(c, 30, stagger=0.04, duration=0.03)
    c = s.outline("Etiqueta", [(305, 490), (680, 490), (680, 585), (305, 585)], 6, BLACK, at=54, n=9)
    c = s.outline("Casilla", [(395, 620), (585, 620), (585, 805), (395, 805)], 6, BLACK, at=57, n=9)
    s.obj("Visto (aro)", ring(BLACK, 6), lambda fr, u: (490, 712, 100, 100, 0, k(fr, 60, 4)), kind="ellipse")
    s.outline("Visto", [(465, 712), (485, 732), (518, 694)], 7, BLACK, at=63, n=6, closed=False)
    return t


# --- 8. deal with science: a black panel wipes in and turns the words white, a frame and crossing lines draw ------
def deal_science():
    D = dur_for(3.0)
    t = _p("ciencia", "Título: panel que invierte la frase, marco y cruz", "Title: panel that inverts the phrase, "
           "frame and cross", 8907, D, ["marco"])
    s = S(t, D)
    bg(s, WHITE)
    edge = lambda fr: 1920 - 1940 * k(fr, 12, 15)  # noqa: E731
    s.rect("Panel", solid(BLACK), lambda fr, u: (edge(fr), -10, 1930, 1090))
    sc = lambda fr: 1.22 - 0.22 * k(fr, 0, 15) - 0.25 * k(fr, 27, 18)  # noqa: E731
    ink = (558, 492, 1368, 588)
    s.say("deal with science", ink, M, 800, BLACK, "Título (negro)", reveal=lambda fr: (-10, 0, edge(fr), 1080),
          editable=False, geom=lambda fr, u: (0, 0, sc(fr), 0, 1 - k(fr, 27, 1)))
    s.say("deal with science", ink, M, 800, WHITE, reveal=lambda fr: (edge(fr) - 400 * k(fr, 27, 1), 0, 1930, 1080),
          geom=lambda fr, u: (0, 0, sc(fr), 0, 1))
    c = s.say("Science expands ideas.", (800, 590, 1120, 610), M, 800, WHITE, "Texto")
    s.typed(c, 54, stagger=0.04, duration=0.03)
    s.outline("Marco", [(1410, 630), (1410, 462), (522, 462), (522, 630), (1410, 630)], 5, WHITE, at=48, n=12,
              closed=False)
    for i, (a, b) in enumerate((((840, 432), (648, 222)), ((1038, 432), (1218, 222)), ((870, 648), (672, 888)),
                                ((1032, 648), (1242, 888)))):
        s.outline(f"Línea {i + 1}", [a, b], 3, WHITE, at=72 + 6 * (i // 2), n=24, closed=False)
    return t



# --- 9. big and visual.: the spaced letters close up, a black panel slides in, a box is typed ------------------
def big_visual():
    D = dur_for(2.4)
    t = _p("big", "Título: palabra gigante con sombra y panel negro", "Title: giant word with a shadow and a black panel",
           8908, D, ["sombra"])
    s = S(t, D)
    bg(s, WHITE)
    from templates_tit_h import fill, shadow
    move = lambda fr: (240 * (1 - k(fr, 12, 15)), 15 * (1 - k(fr, 12, 15)))  # noqa: E731
    sc = lambda fr: 1.08 - 0.08 * k(fr, 12, 15)  # noqa: E731
    ink = (210, 210, 1020, 690)
    c = s.say("big", ink, M, 900, BLACK, layers=[shadow("#BDBDBD", 18, 22), fill(BLACK)],
              geom=lambda fr, u: (move(fr)[0], move(fr)[1], sc(fr), 0, 1))
    s.typed(c, 0, stagger=0.06, duration=0.2, preset="fade")
    c = s.say("and visual.", (672, 270, 1092, 318), M, 800, BLACK, "Texto", align="left")
    s.typed(c, 18, stagger=0.05, duration=0.03)
    s.rect("Panel", solid(BLACK), lambda fr, u: (1920 - 852 * k(fr, 27, 12), -10, 1930, 1090))
    s.rect("Cursor", solid(BLACK), lambda fr, u: (600, 760, 606, 860), op=lambda fr, u: k(fr, 30, 2) * (1 - k(fr, 36, 2)))
    s.rect("Caja", solid(BLACK), lambda fr, u: (210, 750, 210 + 828 * k(fr, 36, 12), 870))
    c = s.say("QUALITY DESIGNS", (250, 784, 990, 836), M, 800, WHITE, "Texto 2", align="left")
    s.typed(c, 42, stagger=0.05, duration=0.03, preset="fade", order="random")
    s.outline("Cuadro", [(1560, 420), (1560, 630), (1350, 630), (1350, 420), (1560, 420)], 6, WHITE, at=48, n=15,
              closed=False)
    s.outline("Cuadro (raya)", [(1410, 480), (1500, 570)], 6, WHITE, at=54, n=9, closed=False)
    for i in range(4):
        s.obj(f"Punto {i + 1}", solid(WHITE), lambda fr, u, i=i: (1266 + 26 * i, 906, 8, 8, 0, k(fr, 57 + i, 3)),
              kind="ellipse")
    return t


# --- 10. DESIGN enjoy: a small diamond grows and turns into a square, the word comes in beside it -----------------
def enjoy_design():
    D = dur_for(2.2)
    t = _p("enjoy", "Título: cuadro que gira y palabra partida", "Title: turning square and a split word", 8909, D,
           ["cuadro"])
    s = S(t, D)
    bg(s, BLACK)
    size = lambda fr: 480 * k(fr, 0, 21)  # noqa: E731
    turn = lambda fr: 45 * (1 - k(fr, 12, 18))  # noqa: E731
    cx = lambda fr: 960 + 291 * k(fr, 54, 9)  # noqa: E731
    s.obj("Cuadro", solid(WHITE), lambda fr, u: (cx(fr), 540, size(fr), size(fr), turn(fr), 1))
    s.say("GRAPHIC", (300, 340, 2000, 740), M, 900, WHITE, "Trama (cuadro)", editable=False,
          layers=outline_layers("#9A9A9A", 3),
          reveal=lambda fr: (cx(fr) - size(fr) / 2, 540 - size(fr) / 2, cx(fr) + size(fr) / 2, 540 + size(fr) / 2),
          op=lambda fr, u: k(fr, 9, 6))
    s.obj("Cuadro negro", solid(BLACK), lambda fr, u: (cx(fr), 540, 282 * k(fr, 24, 12), 300 * k(fr, 24, 12),
                                                       turn(fr) * 0.8, 1))
    for line, ink in (("en", (1180, 400, 1300, 470)), ("joy", (1170, 470, 1320, 560))):
        s.say(line, ink, M, 900, WHITE, "Texto" if line == "en" else "Texto 2",
              geom=lambda fr, u, ink=ink: ((cx(fr) - 1251), 0, 1, 0, k(fr, 33, 6)))
    for i, (line, x0, x1, y0, y1) in enumerate((("DE", 690, 990, 300, 450), ("SIG", 630, 1008, 468, 618),
                                                ("N-", 750, 1008, 648, 798))):
        c = s.say(line, (x0, y0, x1, y1), M, 900, WHITE, f"Título {i + 1}" if i else "Título", align="right")
        s.typed(c, 57 + 4 * i, stagger=0.06, duration=0.15, preset="drop")
    c = s.say("Graphic design", (492, 762, 750, 780), M, 500, WHITE, "Texto 3", align="left")
    s.typed(c, 60, stagger=0.03, duration=0.03)
    s.rect("Franja", solid(WHITE), lambda fr, u: (1920 - 420 * k(fr, 54, 12), -10, 1930, 1090))
    s.say("GRAPHIC", (1300, 200, 2700, 880), M, 900, BLACK, "Trama (franja)", editable=False,
          layers=outline_layers("#555555", 3), rot=lambda fr, u: 60,
          reveal=lambda fr: (1920 - 420 * k(fr, 54, 12), 0, 1930, 1080), op=lambda fr, u: k(fr, 57, 6))
    return t


# --- 11. UNIVERSAL FASHION SENSE: a photo, a black half rises, a white box and the photo in three ----------------
def fashion():
    D = dur_for(2.6)
    t = _p("fashion", "Título: caja con tres fotos detrás", "Title: box with three photos behind", 8910, D,
           ["foto", "moda"])
    s = S(t, D)
    bg(s, WHITE)
    from llt_motion import mask_track
    from kit import Box
    one = s.t.photo(s.t.track("video", "Foto"), "fashion-02", 0.0, D, Box(288, 108, 480, 804), None, label="Tu foto")
    one["opacity"] = keys([(u, round(k(s.frame(u), 0, 12) * (1 - k(s.frame(u), 30, 3)), 4), "linear") for u in frames_of(D)])
    s.rect("Negro", solid(BLACK), lambda fr, u: (-10, 1090 - 514 * k(fr, 21, 9), 1930, 1090))
    for i, x in enumerate((360, 780, 1230)):
        ph = s.t.photo(s.t.track("video", f"Foto {i + 2}"), "fashion-02", 0.0, D, Box(x, 252, 330, 528), None,
                       label="Tu foto", reuse=one.get("placeholderId"))
        ph["opacity"] = keys([(u, round(k(s.frame(u), 30 + 3 * i, 6), 4), "linear") for u in frames_of(D)])
    s.rect("Caja", solid(WHITE), lambda fr, u: (360, 390, 360 + 1200 * k(fr, 27, 9), 678))
    for i, (line, x1, y0, y1) in enumerate((("UNIVERSAL", 900, 408, 480), ("FASHION", 828, 480, 558),
                                            ("SENSE", 660, 558, 636))):
        c = s.say(line, (360, y0, x1, y1), M, 900, BLACK, f"Título {i + 1}" if i else "Título", align="left")
        s.typed(c, 30 + 3 * i, stagger=0.04, duration=0.1, preset="fade")
    c = s.say("GLOBAL FASHION UNDERSTANDING", (360, 642, 828, 656), M, 800, BLACK, "Texto", align="left")
    s.typed(c, 45, stagger=0.02, duration=0.03)
    return t


# --- 12. typography: the photo pulls in to a frame, a white box grows, a label and the word are typed -------------
def typography():
    D = dur_for(2.0)
    t = _p("typography", "Título: caja blanca sobre foto con etiqueta", "Title: white box with a label over a photo",
           8911, D, ["foto"])
    s = S(t, D)
    bg(s, BLACK)
    from llt_motion import mask_track
    from kit import Box
    ph = s.t.photo(s.t.track("video", "Foto"), "portrait-03", 0.0, D, None, None, label="Tu foto")
    mask_track(t, ph, Box(0, 0, 1920, 1080), lambda u: (lambda q: (210 * q, 120 * q, 1920 - 210 * q, 1080 - 120 * q))(
        k(s.frame(u), 0, 18)), D)
    box = lambda fr: (lambda q: (1060 - 760 * q, 540 - 282 * q, 1060 + 560 * q, 540 + 282 * q))(k(fr, 18, 12))  # noqa: E731
    s.rect("Caja", solid(WHITE), lambda fr, u: box(fr), op=lambda fr, u: k(fr, 18, 1))
    s.rect("Etiqueta", solid(BLACK), lambda fr, u: (396, 300, 396 + 216 * k(fr, 27, 6), 384))
    s.obj("Etiqueta (pico)", solid(BLACK), lambda fr, u: (566, 404, 46, 44 * k(fr, 30, 4), 0, 1),
          path="M 0 0 L 100 0 L 100 100 Z")
    c = s.say("Ver 0.1", (416, 322, 590, 362), M, 800, WHITE, "Texto")
    s.typed(c, 30, stagger=0.05, duration=0.03)
    c = s.say("typography", (540, 468, 1398, 618), M, 900, BLACK)
    s.typed(c, 36, stagger=0.06, duration=0.2, preset="rise")
    c = s.say("Typography is a fundamental element of graphic art.", (588, 446, 1230, 462), M, 700, BLACK, "Texto 2")
    s.typed(c, 48, stagger=0.015, duration=0.03)
    return t


# --- 13. ART ALWAYS!: stripes pull up, a black half rises, the letters rise in ------------------------------------
def art_always():
    D = dur_for(2.4)
    t = _p("art-always", "Título: rayas, contorno y letras que suben", "Title: stripes, outline and rising letters",
           8912, D, ["rayas", "contorno"])
    s = S(t, D)
    bg(s, WHITE)
    AE = "Anybody Expanded"
    import templates_llt_f as f6
    f6._FILES[(AE, 900)] = "fonts.extra/fonts/anybodyexpanded/AnybodyExpanded-Black.ttf"
    stripes = " ".join(f"M {i * 6.0:.1f} 0 L {i * 6.0 + 2.4:.1f} 0 L {i * 6.0 - 3.6:.1f} 100 L {i * 6.0 - 6:.1f} 100 Z"
                       for i in range(0, 19))
    s.rect("Rayas", solid(BLACK), lambda fr, u: (-60, -10, 1980, 1090 - 940 * k(fr, 0, 15)), path=stripes)
    s.rect("Negro", solid(BLACK), lambda fr, u: (-10, 1090 - 562 * k(fr, 12, 12), 1930, 1090))
    c = s.say("ART", (132, 192, 708, 348), AE, 900, BLACK, "Texto", layers=outline_layers(BLACK, 3), align="left")
    s.typed(c, 24, stagger=0.06, duration=0.12, preset="fade")
    c = s.say("ALWAYS!", (132, 360, 1308, 528), AE, 900, BLACK, align="left")
    s.typed(c, 30, stagger=0.1, duration=0.25, preset="rise")
    c = s.say("GRAPHICS IS THE FOREMOST ART FORM.", (150, 558, 1590, 600), AE, 900, WHITE, "Texto 2", align="left")
    s.typed(c, 33, stagger=0.03, duration=0.03)
    for i, line in enumerate(("Lorem ipsum dolor sit amet,", "consectetur adipiscing elit, sed do eiusmod",
                              "tempor incididunt ut labore et dolore magna aliqua.")):
        c = s.say(line, (150, 654 + 22 * i, 798, 670 + 22 * i), M, 500, WHITE, f"Texto {i + 3}", align="left")
        s.typed(c, 42 + 3 * i, stagger=0.01, duration=0.03)
    return t


# --- 14. DYNAMISM: the letters light up one by one, a frame and crossing lines draw, the camera pulls back --------
def dynamism():
    D = dur_for(2.1)
    t = _p("dynamism", "Título: palabra que se enciende en un marco con cruz", "Title: word lighting up in a frame "
           "with a cross", 8913, D, ["marco"])
    s = S(t, D)
    bg(s, BLACK)
    sc = lambda fr: 1.5 - 0.5 * k(fr, 45, 12)  # noqa: E731
    px, py = 963, 543
    c = s.say("DYNAMISM", (642, 468, 1284, 630), NAME, 400, WHITE, geom=cam((642, 468, 1284, 630), sc, px, py))
    s.typed(c, 3, stagger=0.12, duration=0.3, preset="fade")
    fr_pts = [(1326, 438), (1326, 648), (600, 648), (600, 438), (1326, 438)]
    fr_pts = [(px + (x - px) * 1.5, py + (y - py) * 1.5) for x, y in fr_pts]
    c = s.outline("Marco", fr_pts, 6, WHITE, at=9, n=24, closed=False)
    s.tmove(c, lambda fr, u: (0, 0, sc(fr) / 1.5, 0, 1))
    for i, (a, b) in enumerate((((852, 408), (678, 222)), ((1056, 402), (1224, 186)), ((858, 672), (702, 900)),
                                ((1056, 672), (1284, 888)))):
        c = s.outline(f"Línea {i + 1}", [a, b], 3, WHITE, at=6 + 3 * i, n=18, closed=False)
    c = s.say("MOTION GRAPHIC DESIGN", (708, 660, 1188, 708), NAME, 400, WHITE, "Texto")
    s.typed(c, 51, stagger=0.03, duration=0.03)
    c = s.say("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod", (540, 940, 1368, 956), M, 500,
              WHITE, "Texto 2")
    s.typed(c, 39, stagger=0.01, duration=0.03)
    s.rect("Barra", solid(WHITE), lambda fr, u: (-10, 1080 - 14 * k(fr, 30, 6), 1930, 1090))
    return t


# --- 15. graphic design look: a grey box over giant black letters, the word pops in, the rest is typed -----------
def look():
    D = dur_for(2.4)
    t = _p("look", "Título: caja gris sobre letras gigantes", "Title: grey box over giant letters", 8914, D, ["caja"])
    s = S(t, D)
    bg(s, WHITE)
    s.say("look", (-700, -500, 2900, 1700), M, 900, BLACK, "Fondo (texto)", editable=False,
          geom=lambda fr, u: (-160 * u, -60 * u, 1, 0, 1))
    s.rect("Caja", solid("#D0D0D0"), lambda fr, u: (lambda q: (963 - 615 * q, 534 - 144 * q, 963 + 615 * q, 534 + 144 * q))(
        k(fr, 0, 6)))
    c = s.say("look", (900, 450, 1452, 660), M, 900, BLACK)
    s.typed(c, 6, stagger=0.1, duration=0.15, preset="pop", order="random")
    s.rect("Barra", solid(BLACK), lambda fr, u: (840 + 60 * (1 - k(fr, 30, 9)), 420, 852 + 60 * (1 - k(fr, 30, 9)), 660),
           op=lambda fr, u: k(fr, 18, 3))
    for i, (line, y0, y1) in enumerate((("graphic", 432, 528), ("design", 528, 630))):
        c = s.say(line, (372, y0, 820, y1), M, 800, BLACK, f"Texto {i + 1}", align="right")
        s.typed(c, 45 + 3 * i, stagger=0.05, duration=0.03)
    s.outline("Etiqueta", [(864, 702), (1464, 702), (1464, 768), (864, 768), (864, 702)], 3, BLACK, at=48, n=12,
              closed=False)
    c = s.say("/ modern compact design", (900, 722, 1430, 748), M, 600, BLACK, "Texto 3")
    s.typed(c, 51, stagger=0.03, duration=0.03, preset="fade", order="random")
    return t


# --- 16. Color change: the letters light up out of order, a strike line runs through -----------------------------
def color_change():
    D = dur_for(2.2)
    t = _p("color-change", "Título: palabra tachada que se enciende", "Title: struck word lighting up", 8915, D,
           ["tachado"])
    s = S(t, D)
    bg(s, BLACK)
    c = s.say("Color", (222, 210, 1128, 510), M, 600, WHITE, align="left")
    s.typed(c, 3, stagger=0.08, duration=0.3, preset="fade", order="random")
    c = s.say("change", (150, 528, 1476, 900), M, 600, WHITE, "Título 2", align="left")
    s.typed(c, 3, stagger=0.08, duration=0.3, preset="fade", order="random")
    s.rect("Tachado", solid(WHITE), lambda fr, u: (-10, 708, 1160 * k(fr, 6, 15), 724))
    s.outline("Etiqueta", [(1122, 420), (1452, 420), (1452, 462), (1122, 462), (1122, 420)], 3, WHITE, at=27, n=12,
              closed=False)
    c = s.say("NO PLUGINS REQUIRED", (1140, 432, 1434, 452), M, 700, WHITE, "Texto")
    s.typed(c, 27, stagger=0.03, duration=0.05, preset="fade", order="random")
    s.rect("Caja", solid(WHITE), lambda fr, u: (1758 - 420 * k(fr, 39, 9), 1008, 1758, 1074))
    c = s.say("TITLES TEMPLATE", (1380, 1032, 1716, 1050), M, 800, BLACK, "Texto 2")
    s.typed(c, 45, stagger=0.03, duration=0.05, preset="fade", order="random")
    for i in range(7):
        s.obj(f"Punto {i + 1}", solid(WHITE), lambda fr, u, i=i: (186 + 28 * i, 915, 10, 10, 0, k(fr, 12 + i, 3)),
              kind="ellipse")
    return t


# --- 17. corporate brand: the letters rise in, a black band grows behind them, a photo rises below ---------------
def corporate():
    D = dur_for(2.4)
    t = _p("corporate", "Título: banda negra que crece tras la frase", "Title: black band growing behind the phrase",
           8916, D, ["foto"])
    s = S(t, D)
    bg(s, WHITE)
    from llt_motion import mask_track
    from kit import Box
    band = lambda fr: (lambda a, b: (120 * (1 - b), 534 - 30 * (1 - a) - 166 * a, 1800 + 120 * b,
                                     534 + 30 * (1 - a) + 174 * a))(k(fr, 45, 6), k(fr, 51, 6))  # noqa: E731
    s.rect("Banda", solid(BLACK), lambda fr, u: (lambda r: (r[0], r[1], r[2], r[3]))(band(fr)),
           op=lambda fr, u: k(fr, 39, 2))
    ph = s.t.photo(s.t.track("video", "Foto"), "portrait-04", 0.0, D, None, None, label="Tu foto")
    mask_track(t, ph, Box(0, 0, 1920, 1080), lambda u: (0, 1090 - 342 * k(s.frame(u), 54, 9), 1920, 1090), D)
    c = s.say("corporate", (640, 500, 1060, 572), M, 500, BLACK, "Título (negro)", align="right", editable=False,
              op=lambda fr, u: 1 - k(fr, 39, 2))
    s.typed(c, 0, stagger=0.08, duration=0.25, preset="rise")
    c = s.say("brand", (1080, 500, 1290, 572), M, 700, BLACK, "Texto (negro)", align="left", editable=False,
              op=lambda fr, u: 1 - k(fr, 39, 2))
    s.typed(c, 24, stagger=0.08, duration=0.25, preset="rise")
    s.say("corporate", (640, 500, 1060, 572), M, 500, WHITE, align="right", op=lambda fr, u: k(fr, 39, 2))
    s.say("brand", (1080, 500, 1290, 572), M, 700, WHITE, "Texto", align="left", op=lambda fr, u: k(fr, 39, 2))
    s.rect("Raya", solid(WHITE), lambda fr, u: (816, 584, 816 + 228 * k(fr, 57, 6), 590))
    r, x0, x1, cy = 84, 372, 1626, 354
    pts = [(x0 + r + r * math.cos(a * math.pi / 12), cy + r * math.sin(a * math.pi / 12)) for a in range(12, 6, -1)]
    pts += [(x1 - r + r * math.cos(a * math.pi / 12), cy + r * math.sin(a * math.pi / 12)) for a in range(6, -1, -1)]
    s.outline("Píldora", pts, 4, WHITE, at=57, n=12, closed=False)
    return t


# --- 18. WONDERFUL AND AESTHETIC: spaced letters close up, lean and straighten, lines draw, a label is typed -------
def wonderful():
    D = dur_for(2.8)
    t = _p("wonderful", "Título: tres palabras que se juntan y líneas", "Title: three words closing up, and lines",
           8917, D, ["líneas"])
    s = S(t, D)
    bg(s, WHITE)
    from templates_tit_h import fill, shadow
    sc = lambda fr: 1.33 - 0.33 * k(fr, 36, 15)  # noqa: E731
    px, py = 108, 540
    lean = lambda fr: 0.0  # noqa: E731
    for i, (line, x1, y0, y1) in enumerate((("WONDERFUL", 1050, 348, 480), ("AND", 450, 480, 600),
                                            ("AESTHETIC", 930, 600, 732))):
        ink = (108, y0, x1, y1)
        c = s.say(line, ink, M, 900, BLACK, f"Título {i + 1}" if i else "Título", align="left",
                  layers=[shadow("#BDBDBD", 8, 10), fill(BLACK)],
                  geom=lambda fr, u, ink=ink: (*cam(ink, sc, px, py)(fr, u)[:3], 0, 1))
        c["rotation"] = keys([(u, round(-lean(s.frame(u)), 3), "linear") for u in frames_of(D)])
        s.typed(c, 0, stagger=0.03, duration=0.25, preset="fade", order="random")
    s.rect("Línea", solid(BLACK), lambda fr, u: (0, 268, 1860 * k(fr, 36, 12), 274))
    s.rect("Línea 2", solid(BLACK), lambda fr, u: (1920 - 1890 * k(fr, 36, 12), 806, 1920, 812))
    s.rect("Etiqueta", solid(BLACK), lambda fr, u: (1230, 408, 1230 + 228 * k(fr, 51, 6), 498))
    s.obj("Etiqueta (pico)", solid(BLACK), lambda fr, u: (1440, 520, 40, 44 * k(fr, 54, 4), 0, 1),
          path="M 0 0 L 100 100 L 0 100 Z")
    c = s.say("NEWVISION", (1244, 438, 1440, 468), M, 800, WHITE, "Texto")
    s.typed(c, 57, stagger=0.05, duration=0.03)
    s.say("01", (1482, 570, 1578, 660), M, 900, BLACK, "Número", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 48, 4)))
    for i, x in enumerate((162, 822, 1482)):
        c = s.say("Lorem ipsum dolor sit amet,", (x, 948, x + 288, 966), M, 500, BLACK, f"Texto {i + 2}", align="left")
        s.typed(c, 54 + 3 * i, stagger=0.02, duration=0.03)
    return t


# --- 19. Awesome: the letters rise in, the white turns into a box over a photo, a bubble and lines ---------------
def awesome():
    D = dur_for(2.6)
    t = _p("awesome", "Título: caja blanca y globo sobre foto", "Title: white box and a bubble over a photo", 8918, D,
           ["foto"])
    s = S(t, D)
    bg(s, BLACK)
    s.t.photo(s.t.track("video", "Foto"), "portrait-01", 0.0, D, None, None, label="Tu foto")
    box = lambda fr: (lambda a, b: (-10 + 520 * a + 90 * b, -10 + 334 * a + 48 * b, 1930 - 510 * a - 90 * b,
                                     1090 - 334 * a - 48 * b))(k(fr, 54, 12), k(fr, 69, 9))  # noqa: E731
    s.rect("Caja", solid(WHITE), lambda fr, u: box(fr))
    sc = lambda fr: 1 - 0.48 * k(fr, 54, 12)  # noqa: E731
    ink = (240, 390, 1632, 720)
    c = s.say("Awesome", ink, M, 800, BLACK,
              geom=lambda fr, u: (*cam(ink, sc, 960, 540, lambda fr: (0, 0))(fr, u)[:3], 0, 1))
    s.typed(c, 0, stagger=0.1, duration=0.3, preset="rise")
    s.outline("Globo", [(570, 372), (570, 708), (450, 708), (440, 768), (400, 708), (318, 708), (318, 372), (570, 372)],
              5, WHITE, at=69, n=12, closed=False)
    s.say("A", (390, 470, 500, 600), M, 800, WHITE, "Texto", layers=outline_layers(WHITE, 2),
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 75, 6)))
    s.rect("Línea", solid(WHITE), lambda fr, u: (940, 180, 945, 180 + 160 * k(fr, 72, 9)))
    s.rect("Línea 2", solid(WHITE), lambda fr, u: (940, 810, 945, 810 + 120 * k(fr, 72, 9)))
    c = s.say("FOR GREAT PRESENTATIONS...", (720, 970, 1200, 988), M, 800, WHITE, "Texto 2")
    s.typed(c, 75, stagger=0.02, duration=0.03)
    return t


# --- 20. VISUALITY TO LIFE IT PROVIDES BEAUTY.: letters light up out of order, the camera pulls back, a line ------
def visuality():
    D = dur_for(2.6)
    t = _p("visuality", "Título: tres líneas que se encienden y cursor", "Title: three lines lighting up and a pointer",
           8919, D, ["contorno"])
    s = S(t, D)
    bg(s, BLACK)
    sc = lambda fr: 1.37 - 0.37 * k(fr, 45, 12)  # noqa: E731
    px, py = 318, 540
    out = outline_layers("#9A9A9A", 2)
    for name, text, ink, layers in (("Título", "VISUALITY", (318, 390, 852, 480), None),
                                    ("Texto", "TO LIFE", (318, 492, 696, 582), out),
                                    ("Texto 2", "IT", (318, 600, 420, 696), out),
                                    ("Título 2", "PROVIDES", (432, 600, 960, 696), None),
                                    ("Texto 3", "BEAUTY.", (978, 600, 1410, 696), out)):
        c = s.say(text, ink, M, 900, WHITE, name, align="left", layers=layers, geom=cam(ink, sc, px, py))
        s.typed(c, 0, stagger=0.08, duration=0.3, preset="fade", order="random")
    c = s.say("Lorem ipsum dolor sit amet, consectetur adipiscing elit.", (318, 712, 1020, 728), M, 500, WHITE, "Texto 4",
              align="left")
    s.typed(c, 42, stagger=0.01, duration=0.03)
    s.rect("Línea", solid(WHITE), lambda fr, u: (300 * k(fr, 54, 15) - 10, 760, 300 + 720 * k(fr, 54, 15), 764))
    s.obj("Cursor", solid(WHITE), lambda fr, u: (300 + 735 * k(fr, 54, 15), 806, 54, 78, -20, k(fr, 18, 6)),
          path="M 0 0 L 0 80 L 22 62 L 38 100 L 52 94 L 36 58 L 64 58 Z")
    r, x0, x1, cy = 36, 1458, 1794, 126
    pts = [(x1 - r + r * math.cos(a * math.pi / 12), cy + r * math.sin(a * math.pi / 12)) for a in range(0, 7)]
    pts += [(x0 + r + r * math.cos(a * math.pi / 12), cy + r * math.sin(a * math.pi / 12)) for a in range(6, 19)]
    pts += [(x1 - r, cy - r)]
    s.outline("Píldora", pts, 4, WHITE, at=48, n=21, closed=False)
    for i in range(3):
        s.obj(f"Punto {i + 1}", ring(WHITE, 3), lambda fr, u, i=i: (1520 + 106 * i, 126, 30, 30, 0, k(fr, 48 + 3 * i, 4)),
              kind="ellipse")
    return t


TEMPLATES = [you, big_text, never_give_up, always_strive, be_strong, create_ideas, health, deal_science, big_visual,
             enjoy_design, fashion, typography, art_always, dynamism, look, color_change, corporate, wonderful, awesome,
             visuality]
