"""INSTAGRAM folder videos as Stock templates (ig13-*). See docs/plan-instagram.md.

1) «Typo Instagram story» (63756849.mp4, 960×540 at 25 fps, 38 s): seven yellow / black / grey typography stories
   shown one by one on a 244×432 screen at (173, 54), 7.0–31.6 s (the intro and outro grids show the same seven).
   Laid out flat on 1080×1920 (×4.43; ×4 from the 270×480 study crops in estudio-63756849/holds). The giant
   letters were fragments of «INSTAGRAM»; here they are fragments of «BRAND» and the title is «YOUR BRAND», the
   url «www.yourwebsite.com». The 3D balls are ellipses with a lit gradient.
2) instagram 2.mp4 (1920×1080 at 29.97 fps, 22 s): the vertical half (11–22 s) — a wall of photo posts that zooms
   out, then a window that closes into the logo with an avatar and a typed user name. The Instagram glyph was the
   brand: the window is a plain rounded square and the logo is the user's `logo-flip` slot.

Times inside a story are seconds of its reference video. Study notes in tienda/plantillas/estudio-63756849/NOTAS.md.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, tall
from scene import fill, gradient, keys, no_stroke
from templates_ig7 import (Story, clamp, curve, eio, eo, lerp, lrect, matte, outline, r_)

W, H = 1080, 1920
U = "Urbanist"
for _w, _f in ((400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"),
               (900, "Black")):
    f6._FILES[(U, _w)] = f"fonts.extra/fonts/urbanist/Urbanist-{_f}.ttf"

GREY, YEL, INK, DARK, DARK2 = "#CAC4C4", "#D19A06", "#141414", "#131313", "#292929"
LET, GLET = "#171717", "#7A7A7A"
TAGS = ["instagram", "historia", "reels", "tipografía", "amarillo", "negro"]
LOREM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit,\nsed do eiusmod tempor incididunt ut labore\net dolore magna aliqua."
URL = "www.yourwebsite.com"


def story(sid, es, en, start, end, order, tags=(), thumb=None):
    t = tall(f"ig13-{sid}", es, en, "instagram", round(end - start, 2), order=order, tags=TAGS + list(tags),
             thumb_at=round((thumb if thumb is not None else end - 0.5) - start, 2))
    return Story(t, start, end)


def ball_layers(grey=False):
    if grey:
        stops = [(0.0, "#A8A8A8"), (0.45, "#6E6E6E"), (1.0, "#262626")]
    else:
        stops = [(0.0, "#FFD21A"), (0.45, "#E2A900"), (1.0, "#6A4700")]
    return [gradient(stops, angle=135), no_stroke()]


def ball(s, t0, t1, pts, grey=False):
    """A lit sphere along pts = [(T, x, y, r), ...] (eased between points)."""
    def r(T):
        x = curve(T, [(p[0], p[1]) for p in pts], eio)
        y = curve(T, [(p[0], p[2]) for p in pts], eio)
        rr = curve(T, [(p[0], p[3]) for p in pts], eio)
        return x - rr, y - rr, x + rr, y + rr
    return s.box(t0, t1, YEL, r, kind="ellipse", layers=ball_layers(grey), key="deco", name="Esfera")


def enter(s, A, B, colour="#000000"):
    """The black strip at the top as each story slides in."""
    s.box(A, A + 0.2, colour, lambda T: (-20, -20, W + 20, lerp(110, -20, r_(T, A, 0.18))), key="cover",
          name="Entrada")


def small(s, text, t0, t1, width, colour, cx, cy, **kw):
    return s.txt(text, t0, t1, width, colour, cx=cx, cy=cy, font=(U, 600), **kw)


def lorem(s, t0, t1, colour, cx, cy, width=560, dy=None, op=None, key="txt"):
    """Three lines of placeholder copy, centred."""
    lines = LOREM.split("\n")
    out = []
    for i, ln in enumerate(lines):
        w = width * len(ln) / len(lines[0])
        out.append(s.txt(ln, t0, t1, w, colour, cx=cx, cy=cy + i * 26, font=(U, 500), dy=dy, op=op, key=key,
                         editable=i == 0, name="Texto"))
    return out


# ====================================================================================================================
# A — giant yellow letters on grey (7.0 – 10.5)
# ====================================================================================================================

def grey_letters():
    A, B = 7.0, 10.5
    s = story("letras-grises", "Historia tipográfica: letras amarillas", "Typography story: yellow letters", A, B,
              16600, ["letras gigantes", "gris"], thumb=9.9)
    s.full(A, B, GREY)
    zoom = lambda T: curve(T, [(A, 2.2), (9.6, 1.0)], eo)  # noqa: E731
    pan = lambda T: curve(T, [(A, 260), (9.6, 0)], eo)  # noqa: E731
    for text, cx, cy, w in (("BRA", 600, 330, 1700), ("AND", 470, 1170, 1650)):
        s.txt(text, A, B, w, YEL, cx=cx, cy=cy, font=(U, 700), key="big", editable=False, name="Letras gigantes",
              s=zoom, dx=lambda T, cx=cx: (cx - 540) * (zoom(T) - 1) + pan(T),
              dy=lambda T, cy=cy: (cy - 900) * (zoom(T) - 1))
    for pts in ([(A, 660, 340, 140), (9.0, 80, 400, 100), (B, 60, 360, 96)],
                [(A, 920, 1740, 200), (9.0, 140, 1640, 260), (B, 120, 1600, 270)],
                [(A, 120, 1720, 60), (9.0, 640, 280, 48), (B, 650, 250, 46)],
                [(A, 1060, 900, 30), (9.0, 1020, 1480, 80), (B, 1010, 1440, 84)],
                [(7.6, 600, 2100, 120), (9.0, 900, 1700, 60), (B, 940, 1650, 40)]):
        ball(s, A, B, pts)
    rise = lambda a, d: (lambda T: curve(T, [(a, d), (a + 1.3, 0)], eo))  # noqa: E731
    s.txt("YOUR BRAND", 7.6, B, 640, INK, cy=960, font=(U, 800), dy=rise(7.6, 900), name="Marca")
    small(s, "Typography", 7.9, B, 360, INK, 540, 1046, dy=rise(7.9, 900), name="Subtítulo")
    lorem(s, 8.1, B, INK, 540, 1112, 440, dy=rise(8.1, 900))
    s.box(8.65, B, INK, lambda T: (lerp(1100, 580, r_(T, 8.65, 0.35)), 1200, W + 20, 1280), key="fr", name="Barra")
    small(s, URL, A, B, 460, INK, 80, 830, rot=lambda T: 90.0, name="Web")
    enter(s, A, B)
    return s.done()


# ====================================================================================================================
# B — yellow with giant grey letters (10.5 – 15.0)
# ====================================================================================================================

def yellow_typography():
    A, B = 10.5, 15.0
    s = story("amarilla", "Historia tipográfica: amarilla", "Typography story: yellow", A, B, 16601,
              ["letras gigantes"], thumb=13.9)
    s.full(A, B, YEL)
    s.txt("BRAND", 11.35, B, 2500, GREY, cx=170, cy=1100, font=(U, 800), key="big", editable=False,
          name="Letras gigantes", rot=lambda T: curve(T, [(11.35, -40), (12.4, -84), (B, -90)], eo),
          dx=lambda T: curve(T, [(11.35, -500), (12.4, -40), (B, 0)], eo),
          dy=lambda T: curve(T, [(11.35, 900), (12.4, 60), (B, 0)], eo))
    for pts in ([(A, 100, 720, 80), (B, 130, 600, 80)], [(A, 520, 680, 40), (B, 500, 560, 40)],
                [(A, 1000, 900, 120), (B, 1060, 760, 130)], [(A, 580, 1260, 72), (B, 620, 1180, 70)],
                [(A, 840, 1272, 32), (B, 880, 1240, 30)], [(A, 100, 1640, 80), (B, 140, 1500, 90)],
                [(A, 800, 580, 18), (B, 820, 420, 18)], [(11.6, 230, 2050, 60), (B, 240, 1280, 64)],
                [(11.8, 900, 2100, 50), (B, 860, 1400, 56)]):
        ball(s, A, B, pts)
    rise = lambda T: curve(T, [(11.35, 1100), (11.6, 700), (12.0, 280), (12.8, 60), (13.1, 0)], eo)  # noqa: E731
    s.txt("Typography", 11.35, B, 960, INK, cx=540, cy=868, font=(U, 700), dy=rise, name="Título")
    lorem(s, 11.4, B, INK, 400, 1032, 640, dy=rise)
    s.box(11.4, B, INK, lambda T: (740, 992 + rise(T), 1012, 1100 + rise(T)), key="fr", name="Barra")
    small(s, "YOUR BRAND", 11.3, B, 400, INK, 972, 440, rot=lambda T: -90.0,
          dy=lambda T: curve(T, [(11.3, 1300), (12.0, 400), (12.8, 60), (13.1, 0)], eo), name="Marca")
    up = lambda T: curve(T, [(12.65, 260), (13.0, 0)], eo)  # noqa: E731
    s.box(12.65, B, "#FFFFFF", lambda T: (192, 1740 + up(T), 912, 1860 + up(T)), key="fr", name="Caja")
    small(s, URL, 12.65, B, 660, INK, 552, 1802, dy=up, key="toptxt", name="Web")
    enter(s, A, B)
    return s.done()


# ====================================================================================================================
# C — diagonal giant lowercase letters on black (15.0 – 19.0)
# ====================================================================================================================

def black_diagonal():
    A, B = 15.0, 19.0
    s = story("negra", "Historia tipográfica: negra en diagonal", "Typography story: black diagonal", A, B, 16602,
              ["letras en diagonal", "negro"], thumb=18.9)
    s.full(A, B, DARK)
    ang = -38.0
    ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    nx, ny = -uy, ux
    for i, (colour, off, speed) in enumerate(((GLET, -1240, -60), (YEL, -620, 90), (GLET, 0, -70), (YEL, 620, 80),
                                              (GLET, 1240, -60))):
        cx, cy = 540 + nx * off, 960 + ny * off
        s.txt("brandbrand", A, B, 3300, colour, cx=cx, cy=cy, font=(U, 700), key="big", editable=False,
              name="Letras gigantes", rot=lambda T: ang,
              dx=lambda T, sp=speed, i=i: ux * (sp * (T - A) + 300 * (i % 2 - 0.5)),
              dy=lambda T, sp=speed, i=i: uy * (sp * (T - A) + 300 * (i % 2 - 0.5)))
    ball(s, 15.3, B, [(15.3, 540, 2150, 300), (15.8, 760, 1800, 320), (16.3, 150, 1780, 330), (17.5, 300, 1760, 340),
                      (18.0, 250, 1650, 350), (18.6, 950, 1720, 350), (B, 1000, 1700, 350)])
    ball(s, 16.0, B, [(16.0, 1150, 260, 50), (B, 980, 160, 56)])
    ball(s, 16.2, B, [(16.2, -60, 980, 40), (B, 90, 900, 44)])

    def lab(T):
        k = r_(T, 15.3, 0.6, eo)
        return 540 - 396 * k, 896, 540 + 396 * k, 1032
    s.box(15.3, B, YEL, lab, key="fr", name="Etiqueta")
    mat = s.box(15.3, B, "#FFFFFF", lab, key="mat", name="Mate")
    t = s.txt("YOUR BRAND", 15.3, B, 700, INK, cy=964, font=(U, 800), key="toptxt", name="Marca")
    matte(t, mat)
    rise = lambda T: curve(T, [(16.2, 700), (16.9, 80), (17.4, 0)], eo)  # noqa: E731
    small(s, "Typography", 16.2, B, 460, YEL, 540, 1088, dy=rise, key="toptxt", name="Subtítulo")
    lorem(s, 16.3, B, YEL, 540, 1152, 470, dy=rise, key="toptxt")
    small(s, URL, 16.6, B, 520, YEL, 992, 1500, rot=lambda T: -90.0,
          dy=lambda T: curve(T, [(16.6, 600), (17.3, 0)], eo), key="toptxt", name="Web")
    enter(s, A, B)
    return s.done()


# ====================================================================================================================
# D — rows of giant letters and a stack of «Typography» (19.0 – 23.15)
# ====================================================================================================================

def stacked():
    A, B = 19.0, 23.15
    s = story("filas", "Historia tipográfica: filas de letras", "Typography story: rows of letters", A, B, 16603,
              ["letras gigantes", "gris"], thumb=22.5)
    s.full(A, B, "#D6CFD1")
    for text, colour, cx, cy, w, sp in (("RA", "#3A3A3A", 640, 230, 1500, 30), ("BRAN", YEL, 700, 980, 2200, -36),
                                        ("ND", "#3A3A3A", 560, 1690, 1450, 28)):
        s.txt(text, A, B, w, colour, cx=cx, cy=cy, font=(U, 700), key="big", editable=False, name="Letras gigantes",
              dx=lambda T, sp=sp: sp * (T - A) - sp * 2)
    small(s, URL, A, B, 520, INK, 64, 380, rot=lambda T: -90.0, name="Web")
    ys = [272, 648, 1060, 1380]
    for i, y in enumerate(ys):
        a = 19.35 + 0.22 * i
        s.txt("Typography", a, B, 720, INK, cy=y, font=(U, 700), op=lambda T, a=a: r_(T, a, 0.15),
              dy=lambda T, a=a, y=y: curve(T, [(a, -(y - 100) * 0.5), (a + 0.6, 0)], eo), editable=i == 0,
              name="Título" if i == 0 else "Copia")
    lorem(s, 20.4, B, INK, 540, 1490, 520, op=lambda T: r_(T, 20.4, 0.3))
    by = lambda T: curve(T, [(A, 1050), (19.5, 960), (19.8, 1380), (20.1, 1580), (20.6, 1708)], eo)  # noqa: E731
    bw = lambda T: curve(T, [(A, 0.0), (19.15, 1.0)], eo)  # noqa: E731
    s.box(A, B, INK, lambda T: (540 - 416 * bw(T), by(T) - 100, 540 + 416 * bw(T), by(T) + 100), key="fr",
          name="Caja")
    s.txt("Typography", 19.1, B, 700, "#FFFFFF", cy=1708, font=(U, 700), dy=lambda T: by(T) - 1708, key="toptxt",
          name="Título 2")
    enter(s, A, B)
    return s.done()


# ====================================================================================================================
# E — dark, giant vertical letters, yellow balls (23.15 – 27.0)
# ====================================================================================================================

def dark_vertical():
    A, B = 23.15, 27.0
    s = story("oscura", "Historia tipográfica: oscura con esferas", "Typography story: dark with spheres", A, B,
              16604, ["letras gigantes", "esferas"], thumb=26.5)
    s.full(A, B, DARK2)
    s.txt("BRAND", A, B, 2400, GLET, cx=640, cy=960, font=(U, 700), key="big", editable=False,
          name="Letras de fondo", rot=lambda T: -90.0, dy=lambda T: -60 * (T - A))
    s.txt("brand", A, B, 3000, LET, cx=430, cy=1000, font=(U, 800), key="big", editable=False,
          name="Letras gigantes", rot=lambda T: 90.0, dy=lambda T: 80 * (T - A) - 150)
    for pts in ([(A, 120, 2100, 120), (24.0, 120, 800, 110), (25.0, 60, 520, 100), (B, 40, 540, 100)],
                [(A, 900, 2300, 300), (24.3, 700, 1750, 330), (25.5, 300, 1700, 330), (B, 600, 1600, 340)],
                [(23.6, 200, 2100, 60), (24.5, 330, 160, 64), (B, 340, 88, 56)],
                [(23.9, 700, 2100, 40), (25.0, 980, 1500, 60), (B, 1030, 1300, 60)],
                [(24.2, 500, 2100, 30), (B, 1000, 120, 40)]):
        ball(s, A, B, pts)
    rise = lambda a: (lambda T: curve(T, [(a, 760), (a + 0.3, 330), (a + 0.9, 30), (a + 1.6, 0)], eo))  # noqa: E731
    s.txt("YOUR BRAND", 23.7, B, 760, YEL, cy=1200, font=(U, 800), dy=rise(23.7), key="toptxt", name="Marca")
    small(s, "Typography", 23.85, B, 660, YEL, 540, 1330, dy=rise(23.85), key="toptxt", name="Subtítulo")
    lorem(s, 23.95, B, YEL, 540, 1420, 480, dy=rise(23.95), key="toptxt")
    small(s, URL, 24.9, B, 860, YEL, 540, 1860, dy=lambda T: curve(T, [(24.9, 200), (25.3, 0)], eo), key="toptxt",
          name="Web")
    enter(s, A, B)
    return s.done()


# ====================================================================================================================
# F — yellow with a black box and the vertical name (27.0 – 29.4)
# ====================================================================================================================

def yellow_box():
    A, B = 27.0, 29.4
    s = story("caja-negra", "Historia tipográfica: caja negra", "Typography story: black box", A, B, 16605,
              ["caja", "esferas"], thumb=28.9)
    s.full(A, B, YEL)
    shade = [fill("#000000", 0.2), no_stroke()]
    for ch, cx, cy, w, rot, sp in (("A", 260, 520, 900, 28, (30, 10)), ("B", 900, 300, 760, -22, (-20, 20)),
                                   ("R", 780, 1300, 900, 32, (20, -20)), ("N", 200, 1500, 820, -30, (-15, -10)),
                                   ("D", 620, 820, 700, 12, (10, 25))):
        s.txt(ch, A, B, w, "#000000", cx=cx, cy=cy, font=(U, 700), layers=shade, key="big", editable=False,
              name="Letras de fondo", rot=lambda T, rot=rot: rot + 4 * (T - A),
              dx=lambda T, sp=sp: sp[0] * (T - A), dy=lambda T, sp=sp: sp[1] * (T - A))
    for pts in ([(A, 1000, 300, 110), (B, 960, 360, 110)], [(A, 160, 1640, 140), (B, 220, 1600, 140)],
                [(A, 1060, 1400, 90), (B, 1000, 1450, 90)], [(A, 880, 1860, 160), (B, 860, 1820, 170)],
                [(A, 60, 860, 50), (B, 90, 830, 50)]):
        ball(s, A, B, pts, grey=True)
    s.txt(URL, A, B, 900, INK, cy=132, font=(U, 700), dy=lambda T: curve(T, [(A, -120), (27.3, 0)], eo),
          key="toptxt", name="Web")
    box = [(27.15, (540, 960, 540, 960)), (27.4, (410, 480, 648, 960)), (27.6, (356, 384, 724, 1248)),
           (27.8, (356, 192, 724, 1344)), (27.9, (292, 192, 788, 1440)), (28.0, (216, 230, 864, 1498)),
           (28.4, (172, 292, 912, 1620))]
    br = lambda T: tuple(curve(T, [(t_, r[i]) for t_, r in box], eo) for i in range(4))  # noqa: E731
    s.box(27.15, B, INK, br, key="fr", name="Caja")
    mat = s.box(27.15, B, "#FFFFFF", br, key="mat", name="Mate")
    t = s.txt("YOUR BRAND", 27.15, B, 1000, YEL, cx=540, cy=946, font=(U, 800), rot=lambda T: -90.0, key="toptxt",
              name="Marca")
    matte(t, mat)
    up = lambda T: curve(T, [(28.1, 300), (28.5, 0)], eo)  # noqa: E731
    small(s, "Typography", 28.1, B, 520, INK, 546, 1748, dy=up, key="toptxt", name="Subtítulo")
    lorem(s, 28.15, B, INK, 546, 1820, 500, dy=up, key="toptxt")
    enter(s, A, B)
    return s.done()


# ====================================================================================================================
# G — grey with giant «RA» (29.4 – 31.6)
# ====================================================================================================================

def grey_ra():
    A, B = 29.4, 31.6
    s = story("gris-ra", "Historia tipográfica: gris con RA", "Typography story: grey RA", A, B, 16606,
              ["letras gigantes", "gris"], thumb=31.4)
    s.full(A, B, GREY)
    s.txt("RA", A, B, 1240, INK, cx=600, cy=660, font=(U, 800), key="big", editable=False, name="Letras gigantes",
          dx=lambda T: curve(T, [(A, 260), (31.2, 0)], eo))
    for pts in ([(A, 300, 300, 110), (B, 248, 308, 128)], [(A, 980, 40, 50), (B, 968, 80, 56)],
                [(A, -40, 1520, 230), (B, 0, 1480, 240)], [(A, 900, 1660, 60), (B, 848, 1580, 88)],
                [(A, 620, 2050, 180), (30.4, 620, 1990, 180), (31.0, 560, 2200, 160)]):
        ball(s, A, B, pts)
    rise = lambda a: (lambda T: curve(T, [(a, 600), (a + 0.3, 330), (a + 0.6, 170), (a + 1.0, 0)], eo))  # noqa: E731
    s.txt("YOUR BRAND", 30.0, B, 840, INK, cy=1260, font=(U, 800), dy=rise(30.0), name="Marca")
    small(s, "Typography", 30.1, B, 440, INK, 540, 1404, dy=rise(30.1), name="Subtítulo")
    lorem(s, 30.2, B, INK, 540, 1512, 520, dy=rise(30.2))
    small(s, URL, A, B, 420, INK, 1020, 360, rot=lambda T: 90.0, name="Web")
    enter(s, A, B)
    return s.done()


# ====================================================================================================================
# instagram 2.mp4, vertical half (11.0 – 22.0): a wall of posts zooms out, a window closes on the logo
# ====================================================================================================================

FEED_SAMPLES = ["fx-woman-03", "portrait-02", "fx-nature-02", "fx-woman-06", "beach-02", "fx-fashion-04",
                "h-travel-02", "portrait-04"]
CW, PH, HB, FB, GAP, CP = 1000, 1250, 110, 150, 30, 1060   # card width, photo, header, footer, gap, column pitch
RP = HB + PH + FB + GAP                                    # row pitch
HEART = ("M 50 96 C 22 76 0 58 0 30 C 0 12 13 0 28 0 C 39 0 46 6 50 15 C 54 6 61 0 72 0 C 87 0 100 12 100 30 "
         "C 100 58 78 76 50 96 Z")


def feed():
    from scene import tanim
    A, B = 11.0, 22.0
    t = tall("ig13-muro-de-fotos", "Muro de fotos con tu logo", "Photo wall with your logo", "instagram", B - A,
             order=16610, tags=["instagram", "historia", "reels", "fotos", "logo", "perfil"], thumb_at=5.2)
    t.layout_roles = True
    END = 18.3
    zoom = lambda T: math.exp(curve(T, [(11.0, math.log(1.3)), (11.25, math.log(0.75)), (11.6, math.log(0.42)),  # noqa: E731
                                        (12.5, math.log(0.36)), (13.4, math.log(0.33)), (14.0, math.log(0.24)),
                                        (15.0, math.log(0.2)), (15.5, math.log(0.16)), (16.0, math.log(0.135)),
                                        (17.4, math.log(0.125)), (END, math.log(0.115))], lambda x: x))
    speed = lambda c: (-230 if c % 2 == 0 else 190) * (1 + 0.15 * (abs(c) % 3))  # noqa: E731
    camy = 520  # the first post's photo sits a little above the centre

    def card(c, r, T):
        """Screen rect of post (c, r): header + photo + footer."""
        z = zoom(T)
        wx = c * CP
        wy = r * RP + speed(c) * (T - A) - camy
        x0, y0 = 540 + (wx - CW / 2) * z, 960 + wy * z
        return x0, y0, x0 + CW * z, y0 + (HB + PH + FB) * z, z

    step = 1 / 15
    times = [A + i * step for i in range(int(round((END - A) / step)) + 1)]
    bgt = t.track("shape", "Fondo")
    clip = t.solid(bgt, "#1A1024", 0.0, B - A)
    clip["layoutRole"] = "cover"
    pools = {}

    def alloc(kind, name, t0, t1):
        """A track of `kind` free over [t0, t1] (created bottom-up as the passes go)."""
        pool = pools.setdefault(name, [])
        for tr, spans in pool:
            if all(b <= t0 + 1e-6 or a >= t1 - 1e-6 for a, b in spans):
                spans.append((t0, t1))
                return tr
        tr = t.track(kind, name)
        pool.append((tr, [(t0, t1)]))
        return tr
    slots = {}

    def window(rects):
        vis = [i for i, (x0, y0, x1, y1, z) in enumerate(rects) if x1 > -40 and x0 < W + 40 and y1 > -40 and y0 < H + 40]
        return (vis[0], vis[-1]) if vis else None

    def put(what, rects, i0, i1, sub=lambda R: R[:4], tname="Forma", **kw):
        """A clip over times[i0..i1] following sub(rect), on a free track of its pass."""
        t0, t1 = times[i0], times[i1]
        r0 = sub(rects[i0])
        box = Box(r0[0], r0[1], r0[2] - r0[0], r0[3] - r0[1])
        motion = []
        for i in range(i0, i1 + 1):
            x0, y0, x1, y1 = sub(rects[i])
            motion.append((times[i] - t0, {"s": (x1 - x0) / box.w, "dx": (x0 + x1) / 2 - box.cx,
                                           "dy": (y0 + y1) / 2 - box.cy}, "linear"))
        if what == "photo":
            track = alloc("video", tname, t0, t1)
            sample = kw.pop("sample")
            reuse = slots.get(sample)
            c_ = t.photo(track, sample, t0 - A, t1 - t0, box, motion, label=kw.pop("label", None), reuse=reuse)
            slots.setdefault(sample, c_["placeholderId"])
        elif what == "text":
            track = alloc("text", tname, t0, t1)
            c_ = t.text(track, kw.pop("content"), t0 - A, t1 - t0, box, kw.pop("style"), motion,
                        editable=kw.pop("editable", False))
        else:
            track = alloc("shape", tname, t0, t1)
            c_ = t.solid(track, kw.pop("colour"), t0 - A, t1 - t0, box, motion, **kw)
        c_["layoutRole"] = "cover"
        return c_

    posts = []
    for c in range(-4, 5):
        for r in range(-8, 9):
            rects = [card(c, r, T) for T in times]
            w = window(rects)
            if w:
                posts.append((c, r, rects, w))
    # pass 1: one white strip per column (the cards' header and footer)
    for c in range(-4, 5):
        col = [p for p in posts if p[0] == c]
        if not col:
            continue
        i0, i1 = min(p[3][0] for p in col), max(p[3][1] for p in col)

        def strip(T, c=c):
            z = zoom(T)
            return 540 + (c * CP - CW / 2) * z, -40, 540 + (c * CP + CW / 2) * z, H + 40, z
        rects = [strip(T) for T in times]
        put("solid", rects, i0, i1, tname="Columna", colour="#F4F2F7")
    # pass 2: the photos (and the dark gaps between posts while they are big)
    order = 0
    for c, r, rects, (i0, i1) in posts:
        sample = FEED_SAMPLES[(c * 3 + r * 5) % len(FEED_SAMPLES)]
        if c == 0 and r == 0:
            sample = FEED_SAMPLES[0]
        label = None
        if sample not in slots:
            order += 1
            label = f"Foto {order}"
        put("photo", rects, i0, i1, sample=sample, label=label, tname="Fotos",
            sub=lambda R: (R[0], R[1] + HB * R[4], R[2], R[1] + (HB + PH) * R[4]))
    for c, r, rects, (i0, i1) in posts:
        if abs(c) > 1:
            continue
        put("solid", rects, i0, i1, tname="Separación", colour="#1A1024",
            sub=lambda R: (R[0] - 2, R[1] - GAP * R[4], R[2] + 2, R[1]))
    # pass 3: icons and the user name on the posts near the centre while they are big
    st = {"fontFamily": U, "pixelSize": 44, "fontWeight": 600, "italic": False,
          "layers": [fill("#1A1A1A"), no_stroke()], "align": "left", "valign": "middle", "wordWrap": False,
          "lineHeight": 1.0, "letterSpacing": 0, "textCase": "none", "boxEnabled": False,
          "boxColor": "#80000000", "boxPadding": 0, "boxRadius": 0, "accent": {"rule": "none"}, "animation": {}}
    for c, r, rects, (i0, i1) in posts:
        if abs(c) > 1:
            continue
        big = [i for i in range(i0, i1 + 1) if rects[i][4] > 0.3]
        if len(big) < 2:
            continue
        j0, j1 = big[0], big[-1]
        for dx, sz, path in ((40, 60, HEART), (130, 60, None), (220, 60, "M 0 0 L 100 45 L 0 100 L 25 50 Z")):
            sub = lambda R, dx=dx, sz=sz: (R[0] + dx * R[4], R[1] + (HB + PH + 30) * R[4], R[0] + (dx + sz) * R[4],
                                           R[1] + (HB + PH + 30 + sz) * R[4])
            cc = put("solid", rects, j0, j1, sub=sub, tname="Iconos", colour="#1A1A1A",
                     kind="ellipse" if path is None else "rectangle", layers=outline("#1A1A1A", 5))
            if path:
                cc["shapeStyle"]["kind"] = "custom"
                cc["shapeStyle"]["customPath"] = path
                cc["shapeStyle"]["customEvenOdd"] = False
        sub = lambda R: (R[0] + (CW - 90) * R[4], R[1] + (HB + PH + 30) * R[4], R[0] + (CW - 45) * R[4],
                         R[1] + (HB + PH + 90) * R[4])
        put("solid", rects, j0, j1, sub=sub, tname="Iconos", colour="#1A1A1A", layers=outline("#1A1A1A", 5))
        sub = lambda R: (R[0] + 30 * R[4], R[1] + 22 * R[4], R[0] + 96 * R[4], R[1] + 88 * R[4])
        put("solid", rects, j0, j1, sub=sub, tname="Iconos", colour="#B44AA0", kind="ellipse")
        sub = lambda R: (R[0] + 120 * R[4], R[1] + 10 * R[4], R[0] + 620 * R[4], R[1] + 100 * R[4])
        cl = put("text", rects, j0, j1, sub=sub, tname="Nombres", content="yourname", style=dict(st))
        cl["textStyle"] = dict(st)
        cl["textStyle"]["keyframes"] = {"pixelSize": keys([(times[i] - times[j0], round(44 * rects[i][4], 2), "linear")
                                                           for i in range(j0, j1 + 1)])}
    # purple tint and a dark vignette, as the reference
    tint = t.track("shape", "Tono")
    c_ = t.solid(tint, "#DCC6F6", 0.0, END - A + 0.2)
    c_["blendMode"] = "multiply"
    c_["layoutRole"] = "cover"
    vig = t.track("shape", "Viñeta")
    c_ = t.solid(vig, "#12081E", 0.0, END - A + 0.2,
                 layers=[{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                          "paint": {"kind": "gradient", "color": "#0012081e",
                                    "gradient": {"kind": "radial", "space": "block", "angle": 0,
                                                 "stops": [{"pos": 0.0, "color": "#0012081e"},
                                                           {"pos": 0.55, "color": "#0012081e"},
                                                           {"pos": 1.0, "color": "#d012081e"}]}}}, no_stroke()])
    c_["layoutRole"] = "cover"
    # the white page with a rounded window that closes on the logo
    win = [(17.1, 3200), (17.25, 1250), (17.4, 720), (17.6, 480), (17.8, 380), (18.0, 330)]
    wsize = lambda T: curve(T, win, eo)  # noqa: E731
    wt = t.track("shape", "Ventana")
    step2 = 1 / 30
    tw = [17.1 + i * step2 for i in range(int(round((B - 17.1) / step2)) + 1)]
    s0 = wsize(17.1)
    mot = [(T - 17.1, {"s": wsize(T) / s0, "dx": 0, "dy": -2}, "linear") for T in tw if T <= 18.05] + [(B - 17.1, {"s": 330 / s0, "dx": 0, "dy": -2})]
    wclip = t.solid(wt, "#FFFFFF", 17.1 - A, B - 17.1, Box(540 - s0 / 2, 960 - s0 / 2, s0, s0), mot,
                    kind="rounded-rectangle", radius=s0 * 0.24)
    wclip["shapeStyle"]["keyframes"] = {"cornerRadius": keys([(m[0], round(0.24 * s0 * m[1]["s"], 2), "linear") for m in mot])}
    wclip["layoutRole"] = "art"
    page = t.track("shape", "Página")
    pc = t.solid(page, "#F2EEFA", 17.1 - A, B - 17.1,
                 layers=[{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                          "paint": {"kind": "gradient", "color": "#fff6f2fc",
                                    "gradient": {"kind": "radial", "space": "block", "angle": 0,
                                                 "stops": [{"pos": 0.0, "color": "#fff8f6fc"},
                                                           {"pos": 0.7, "color": "#ffeee8f8"},
                                                           {"pos": 1.0, "color": "#ffc8bce0"}]}}}, no_stroke()])
    pc["matte"] = {"clip": wclip["id"], "mode": "alphaInverted"}
    pc["layoutRole"] = "cover"
    # the logo fills the window, the avatar and the typed name come under it
    lt = t.track("video", "Logo")
    logo = t.photo(lt, "logo-flip", 17.85 - A, B - 17.85, Box(375, 793, 330, 330), None, label="Tu logo",
                   brandRole="logo")
    logo["opacity"] = keys([(0.0, 0.0, "linear"), (0.5, 1.0)])
    logo["layoutRole"] = "art"
    at = t.track("video", "Perfil")
    av = t.photo(at, "portrait-02", 18.1 - A, B - 18.1, Box(330, 1150, 112, 112),
                 [(0.0, {"s": 0.0}, "back"), (0.3, {})], label="Foto de perfil")
    t.mask(at, av, "ellipse")
    av["layoutRole"] = "art"
    nt = t.track("text", "Usuario")
    st = {"fontFamily": U, "pixelSize": 60, "fontWeight": 600, "italic": False,
          "layers": [fill("#3A3550"), no_stroke()], "align": "left", "valign": "middle", "wordWrap": False,
          "lineHeight": 1.0, "letterSpacing": 0, "textCase": "none", "boxEnabled": False, "boxColor": "#80000000",
          "boxPadding": 0, "boxRadius": 0, "accent": {"rule": "none"},
          "animation": {"in": tanim("typewriter", duration=0.06, unit="character", stagger=0.06, ease="easeOut")}}
    nc = t.text(nt, "yourname", 18.2 - A, B - 18.2, Box(462, 1162, 440, 92), st, label="Usuario")
    nc["layoutRole"] = "art"
    return t


TEMPLATES = [grey_letters, yellow_typography, black_diagonal, stacked, dark_vertical, yellow_box, grey_ra, feed]
