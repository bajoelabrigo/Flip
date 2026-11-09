"""INSTAGRAM folder video 60629101.mp4 as Stock templates (ig12-*). See docs/plan-instagram.md.

60629101.mp4 (960×540 at 25 fps, 27 s; `instagram.mp4` is the same file): five orange / red / black stories on a pale
pink page, shown side by side and then one by one (the story is 223×396 px there, x 264 y 72; laid out ×4.84 on
1080×1920). Colour bands that stack up, a red box that grows round a vertical word, diagonal stripes with a photo
band, rings round a round photo with giant letters that change colour on each ring, a giant word sliding up a red
panel. Moves copied from 10 fps sheets (frames at 29.97 fps from each story's start). The reference's big brand type
(«Instagram», «Insta», «stagram») is a neutral editable word («Stories», «Style»), its marketplace addresses are
«www.yoursite.com»; B/W photos are slots with a black-and-white look. Kit de Instagram; ids `ig12-*`, order 16500-.
Notes in tienda/plantillas/estudio-60629101/NOTAS.md.

Each story plays its entrance, holds, and leaves with its entrance backwards at 2.5× speed (S.frame).
"""

from __future__ import annotations

import math

from kit import tall
from scene import effect
from templates_ig9 import Story, URB, dur_for, finish, ko, table, word_metrics
from templates_tit_c import k
from templates_tit_e import solid

W, H = 1080, 1920
WHITE, PINK, RED, ORANGE, GREYB, DARK1, DARK = "#FFFFFF", "#EFE4E2", "#FF2C00", "#FF9800", "#C3C3C3", "#1F1F1F", \
    "#292929"
WEB = "www.yoursite.com"
BW = [effect("color.basic", saturation=-1.0, contrast=0.1)]


def _p(id, es, en, order, dur, tags=(), thumb=None):
    return tall(f"ig12-{id}", es, en, "instagram", dur, order=order,
                tags=["instagram", "historia", "reels", "naranja", "rojo"] + list(tags),
                thumb_at=thumb if thumb is not None else round(dur * 0.6, 1))


def vword(s, text, cx, cy, length, cap, colour, name, geom=None, weight=700, family=URB):
    """A word reading upwards (turned −90°) centred at (cx, cy); geom(fr) = (dx, dy, scale, op)."""
    g = geom or (lambda fr: (0.0, 0.0, 1.0, 1.0))
    return s.line(text, (cx - length / 2, cy - cap / 2, cx + length / 2, cy + cap / 2), family, weight, colour, name,
                  geom=lambda fr, u: (g(fr)[0], g(fr)[1], g(fr)[2], -90.0, g(fr)[3]))


# ==================================================================================================================
# 1. Red, orange, grey and black bands stack up from the bottom, a giant word rises and shrinks to the corner,
#    a tag slides in, the photo opens from the right, «photo» comes
def bands():
    D = dur_for(98)
    t = _p("franjas", "Historia: franjas de color y palabra vertical", "Story: colour bands and a vertical word",
           16500, D, ["franjas", "foto", "vertical"])
    s = Story(t, D)
    s.bg(PINK)
    finals = ((RED, 0, -1, 25), (ORANGE, 204, 4, 25), (GREYB, 441, 8, 27), (DARK1, 570, 14, 29))
    for i, (c, fin, at, n) in enumerate(finals):
        s.bar("Fondo (franja)" if i == 0 else f"Fondo (franja {i + 1})", c,
              lambda fr, u, fin=fin, at=at, n=n: (-10, fin + (1930 - fin) * (1 - ko(fr, at, n)), W + 10, H + 10))
    # The giant word: rises big, then shrinks into the lower right.
    _, ln, _ = word_metrics("Stories", URB, 700, 190)
    big, small = (489, 1760 - ln / 2, 1.0), (835, 1812 - ln * 0.55 / 2, 0.55)

    def wg(fr):
        rise = 1100 * (1 - ko(fr, 22, 24))
        p = k(fr, 54, 27)
        return (small[0] - big[0]) * p, (small[1] - big[1]) * p + rise, 1 + (small[2] - 1) * p, 1.0 if fr > 22 else 0.0
    vword(s, "Stories", big[0], big[1], ln, 190, WHITE, "Título", geom=wg)
    # The tag slides in from the right edge.
    tx = lambda fr: 140 * (1 - ko(fr, 72, 10))  # noqa: E731
    s.bar("Etiqueta", ORANGE, lambda fr, u: (963 + tx(fr), 1515, 1056 + tx(fr), 1815),
          op=lambda fr, u: 1.0 if fr > 72 else 0.0)
    vword(s, "nature", 1010, 1665, 260, 46, DARK1, "Etiqueta (texto)", weight=700,
          geom=lambda fr: (tx(fr), 0, 1.0, 1.0 if fr > 72 else 0.0))
    # The photo opens from its right edge leftwards; «photo» uncovers left to right.
    m = s.rect("Foto (forma)", solid(WHITE), lambda fr, u: (714 - 450 * ko(fr, 81, 15), 480, 714, 1599),
               op=lambda fr, u: 1.0 if fr > 81 else 0.0)
    s.pic("Foto", "portrait-07", (264, 480, 714, 1599), matte_clip=m, look=BW, label="Foto")
    s.line("photo", (60, 1655, 470, 1745), URB, 700, WHITE, "Texto", reveal=lambda fr: (0, 1600, 60 + 440 * ko(fr, 84, 12),
                                                                                       1800))
    return finish(t)


# 2. A red box grows from a point round a vertical word on orange, giant orange letters behind, the dark falls
#    from the top, the box drops and stretches, the photo grows inside it, the address
def red_box():
    D = dur_for(72)
    t = _p("caja-roja", "Historia: caja roja con palabra vertical y letras gigantes",
           "Story: red box with a vertical word and giant letters", 16501, D, ["caja", "letras", "foto"])
    s = Story(t, D)
    s.bg(PINK)
    s.bar("Fondo (oscuro)", DARK, lambda fr, u: (-10, -10, W + 10, table([(30, -10), (31.5, 15), (37.5, 90), (43.5, 360),
                                                                         (49.5, 1335), (58.5, 1845),
                                                                         (67.5, 1930)])(fr)))
    # Giant orange letters behind (two rows of the word), growing from the middle and drifting up.
    for i, (txt, cy, x0) in enumerate((("sty", 420, -120), ("le", 1480, -60))):
        size, ink, _ = word_metrics(txt, URB, 800, 700)
        c = s.line(txt, (x0, cy - 350, x0 + ink, cy + 350), URB, 800, ORANGE, f"Letras {i + 1}",
                   geom=lambda fr, u, cy=cy, x0=x0, ink=ink: (
                       (540 - (x0 + ink / 2)) * (1 - ko(fr, 12, 12)), (960 - cy) * (1 - ko(fr, 12, 12)) - 3 * max(0, fr - 12),
                       0.25 + 0.75 * ko(fr, 12, 12), 0, 1.0 if fr > 12 else 0.0))
        c["layoutRole"] = "backdrop"
    w = table([(2, 0), (13.5, 120), (19.5, 510), (25.5, 741), (31.5, 801), (37.5, 816)])
    h = table([(2, 0), (13.5, 234), (19.5, 1020), (25.5, 1500), (31.5, 1614), (37.5, 1638)])
    y0 = table([(40, 975 - 819), (58, 294)])
    y1 = table([(40, 975 + 819), (58, 1940)])

    def box(fr, u):
        if fr <= 40:
            return 543 - w(fr) / 2, 975 - h(fr) / 2, 543 + w(fr) / 2, 975 + h(fr) / 2
        return 138, y0(fr), 948, y1(fr)
    s.bar("Caja", RED, box, op=lambda fr, u: 1.0 if fr > 2 else 0.0)
    iw = table([(14, 0), (19.5, 60), (25.5, 225), (31.5, 432), (37.5, 480)])
    ih = table([(14, 0), (19.5, 120), (25.5, 555), (31.5, 1095), (37.5, 1206)])
    iy0 = table([(40, 360), (58, 0)])
    iy1 = table([(40, 1566), (58, 1230)])

    def inner(fr, u):
        if fr <= 40:
            return 546 - iw(fr) / 2, 963 - ih(fr) / 2, 546 + iw(fr) / 2, 963 + ih(fr) / 2
        return 300, iy0(fr) - 10, 790, iy1(fr)
    s.bar("Caja (dentro)", ORANGE, inner, op=lambda fr, u: 1.0 if fr > 14 else 0.0)
    sc = table([(14, 0.05), (19.5, 0.12), (25.5, 0.45), (31.5, 0.92), (37.5, 1.0)])
    vy = table([(40, 963), (58, 640)])
    vword(s, "Style", 545, 640, 980, 300, DARK, "Título", weight=800,
          geom=lambda fr: (0, vy(fr) - 640, sc(fr), 1.0 if fr > 14 else 0.0))
    g = lambda fr: ko(fr, 49, 10)  # noqa: E731
    m = s.rect("Foto (forma)", solid(WHITE), lambda fr, u: (552 - 238 * g(fr), 1495 - 235 * g(fr), 552 + 238 * g(fr),
                                                         1495 + 235 * g(fr)), op=lambda fr, u: 1.0 if fr > 49 else 0.0)
    s.pic("Foto", "h-nature-02", (314, 1260, 790, 1730), matte_clip=m, look=BW, label="Foto")
    s.line(WEB, (320, 1790, 770, 1832), URB, 700, WHITE, "Web", op=lambda fr, u: k(fr, 60, 9))
    return finish(t)


# 3. Diagonal stripes sweep up from the corner, a photo band opens, a giant word slides down it, the name and the
#    address slide along the red stripe
def diagonal():
    D = dur_for(68)
    t = _p("diagonal", "Historia: franjas diagonales con palabra gigante", "Story: diagonal stripes with a giant word",
           16502, D, ["diagonal", "franjas", "foto"])
    s = Story(t, D)
    s.bg(PINK)
    nx, ny = math.sqrt(0.5), math.sqrt(0.5)   # normal, pointing down-right
    dx, dy = math.sqrt(0.5), -math.sqrt(0.5)  # along the stripes, up-right
    L = 5000.0

    def band(top):
        """A stripe from normal offset top(fr) on (it covers everything past it)."""
        def g(fr, u):
            n = top(fr) + L / 2
            return 540 + n * nx, 960 + n * ny, 4000, L, -45.0, 1.0
        return g
    red_top = table([(0, 1400), (9.5, 140), (13.5, -212), (19.5, -752), (25.5, -1400)])
    dark_top = table([(0, 1500), (1.5, 424), (7.5, 120), (13.5, 40), (19.5, 20), (31.5, 14)])
    red2_top = table([(0, 1600), (7.5, 600), (13.5, 300), (19.5, 220), (25.5, 196), (31.5, 192)])
    orange_top = table([(0, 1800), (7.5, 1300), (13.5, 712), (19.5, 496), (25.5, 432), (31.5, 414)])
    photo_top = table([(0, 3000), (27, 3000), (28, 14), (31.5, -356), (37.5, -512), (48, -600)])
    s.obj("Fondo (franja)", solid(RED), band(red_top))
    m = s.obj("Foto (forma)", solid(WHITE), band(photo_top))
    s.pic("Foto", "city-01", (0, 0, W, H), matte_clip=m, look=BW, label="Foto")
    # The giant word lies on the photo band, sliding down it from the upper right.
    size, ink, lets = word_metrics("create", URB, 800, 500)
    off = table([(29, 1800), (31.5, 1460), (37.5, 550), (43.5, 200), (55.5, 40), (67.5, 0)])
    a0, n0 = -760 + ink / 2, -60 - 180   # ink centre along the stripe, centre of its x-height across
    cx, cy = 540 + a0 * dx + n0 * nx, 960 + a0 * dy + n0 * ny
    word = s.line("create", (cx - ink / 2, cy - 250, cx + ink / 2, cy + 250), URB, 800, RED, "Título",
                  geom=lambda fr, u: (off(fr) * dx, off(fr) * dy, 1.0, -45.0, 1.0 if fr > 29 else 0.0))
    word["matte"] = {"clip": m["id"], "mode": "alpha"}
    s.obj("Franja oscura", solid(DARK), band(dark_top))
    s.obj("Franja roja", solid(RED), band(red2_top))
    s.obj("Franja naranja", solid(ORANGE), band(orange_top))

    def along(text, a, n, length, cap, name, start, at, frames, weight=700):
        x, y = 540 + a * dx + n * nx, 960 + a * dy + n * ny
        o = lambda fr: start * (1 - ko(fr, at, frames))  # noqa: E731
        return s.line(text, (x - length / 2, y - cap / 2, x + length / 2, y + cap / 2), URB, weight, WHITE, name,
                      geom=lambda fr, u: (o(fr) * dx, o(fr) * dy, 1.0, -45.0, 1.0 if fr > at else 0.0))
    along("@yourname", -560, 300, 560, 62, "Nombre", -700, 30, 16)
    along(WEB, 160, 320, 640, 40, "Web", 900, 30, 16)
    return finish(t)


# 4. A dark disc and a red disc open from the middle, an orange ring with giant letters that change colour on it,
#    a grey ring with a round photo, «awesome» and a line drop from the top, the address rises
def rings():
    D = dur_for(85)
    t = _p("anillos", "Historia: anillos con foto redonda y letras gigantes",
           "Story: rings with a round photo and giant letters", 16503, D, ["círculos", "anillos", "foto"])
    s = Story(t, D)
    s.bg(PINK)
    C = (540, 963)

    def disc(name, colour, d):
        return s.obj(name, solid(colour), lambda fr, u: (C[0], C[1], d(fr), d(fr), 0, 1.0 if d(fr) > 1 else 0.0),
                     kind="ellipse", base=(1700, 1700))
    s.obj("Fondo (disco)", solid(DARK), lambda fr, u: (C[0], C[1], table([(0, 0), (1.5, 20), (7.5, 192), (13.5, 1260),
                                                                         (19.5, 2500), (25, 4400)])(fr),
                                                      table([(0, 0), (1.5, 20), (7.5, 192), (13.5, 1260), (19.5, 2500),
                                                             (25, 4400)])(fr), 0, 1.0 if fr > 0.5 else 0.0),
          kind="ellipse", base=(4400, 4400))
    dr = table([(7.5, 0), (8, 10), (13.5, 141), (19.5, 918), (25.5, 1530), (31.5, 1680)])
    do = table([(22, 0), (31.5, 1035), (52.5, 1245)])
    disc("Disco rojo", RED, dr)
    disc("Disco naranja", ORANGE, do)
    red = disc("Disco rojo (máscara)", WHITE, dr)
    orange = disc("Disco naranja (máscara)", WHITE, do)
    # The giant word slides left: orange where it lies on red, red where it lies on orange.
    size, ink, lets = word_metrics("awesome", URB, 800, 520)
    x0 = 20 - lets[1][0]   # its «w» at the left edge when it comes
    for colour, matte, name in ((ORANGE, red, "Letras"), (RED, orange, "Letras 2")):
        c = s.line("awesome", (x0, 960 - 260, x0 + ink, 960 + 260), URB, 800, colour, name,
                   geom=lambda fr, u: (-14 * max(0.0, fr - 22), 0, 1.0, 0, 1.0 if fr > 22 else 0.0))
        c["matte"] = {"clip": matte["id"], "mode": "alpha"}
    grey = table([(30, 0), (31.5, 90), (37.5, 540), (43.5, 735), (52.5, 795), (64, 804)])
    s.obj("Aro", solid(GREYB), lambda fr, u: (540, 921, grey(fr), grey(fr), 0, 1.0 if grey(fr) > 1 else 0.0),
          kind="ellipse", base=(804, 804))
    ph = table([(38, 0), (43.5, 300), (52.5, 540), (64.5, 555)])
    m = s.obj("Foto (forma)", solid(WHITE), lambda fr, u: (540, 921, ph(fr), ph(fr), 0, 1.0 if ph(fr) > 1 else 0.0),
              kind="ellipse", base=(555, 555))
    s.pic("Foto", "h-city-03", (540 - 420, 921 - 300, 540 + 420, 921 + 300), matte_clip=m, look=BW, label="Foto")
    ay = table([(56, -120), (58.5, 50), (61.5, 231), (64.5, 303), (67.5, 346), (70.5, 361), (80, 390)])
    s.line("awesome", (171, 390 - 52, 879, 390 + 52), URB, 700, WHITE, "Título",
           geom=lambda fr, u: (0, ay(fr) - 390, 1, 0, 1.0 if fr > 56 else 0.0))
    ny = table([(64, -60), (67.5, 15), (70.5, 123), (73.5, 202), (76.5, 225), (85, 240)])
    s.line("new post", (334, 240 - 36, 794, 240 + 36), URB, 600, WHITE, "Texto",
           geom=lambda fr, u: (0, ny(fr) - 240, 1, 0, 1.0 if fr > 64 else 0.0))
    uy = table([(64, 1990), (67.5, 1910), (70.5, 1848), (73.5, 1812), (80, 1797)])
    s.line(WEB, (174, 1797 - 30, 990, 1797 + 30), URB, 700, WHITE, "Web",
           geom=lambda fr, u: (0, uy(fr) - 1797, 1, 0, 1.0 if fr > 64 else 0.0))
    return finish(t)


# 5. An orange panel and a red panel slide in from the right, a giant word slides up the red one, a photo panel opens
#    from the left with the address up its side
def red_panel():
    D = dur_for(76)
    t = _p("panel-rojo", "Historia: palabra gigante que sube en panel rojo",
           "Story: giant word sliding up a red panel", 16504, D, ["panel", "letras", "foto"])
    s = Story(t, D)
    s.bg(DARK)
    P = table([(50, 0), (52.5, 30), (64.5, 372), (76, 420)])
    m = s.rect("Foto (forma)", solid(WHITE), lambda fr, u: (0, 0, P(fr), H), op=lambda fr, u: 1.0 if fr > 50 else 0.0)
    s.pic("Foto", "food-01", (0, 0, 440, H), matte_clip=m, look=BW, label="Foto")
    lo = table([(6, 1080), (7.5, 1056), (13.5, 924), (19.5, 510), (25.5, 276), (31.5, 207), (40.5, 201), (52.5, 201),
                (64.5, 372), (76, 420)])
    lr = table([(12, 1080), (19.5, 1056), (25.5, 729), (31.5, 498), (40.5, 420)])
    s.rect("Panel naranja", solid(ORANGE), lambda fr, u: (lo(fr), -10, W + 10, H + 10),
           op=lambda fr, u: 1.0 if lo(fr) < 1079 else 0.0)
    s.rect("Panel rojo", solid(RED), lambda fr, u: (lr(fr), -10, W + 10, H + 10),
           op=lambda fr, u: 1.0 if lr(fr) < 1079 else 0.0)
    # The giant word reads upwards across the red panel and slides up.
    size, ink, lets = word_metrics("stories", URB, 800, 690)
    c = s.line("stories", (645 - ink / 2, 960 - 345, 645 + ink / 2, 960 + 345), URB, 800, ORANGE, "Título",
               geom=lambda fr, u: (0, 1950 - ink / 2 - 960 + 2.7 * (76 - fr), 1.0, -90.0, 1.0))
    s.matte(c, "Título (máscara)", lambda fr, u: (lo(fr), -10, W + 10, H + 10))
    vword(s, WEB, 87, 472, 735, 46, WHITE, "Web", geom=lambda fr: (0, 0, 1.0, k(fr, 64, 8)))
    return finish(t)


TEMPLATES = [bands, red_box, diagonal, rings, red_panel]
