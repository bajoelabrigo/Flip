"""INSTAGRAM folder video 23012546.mp4 as Stock templates (ig3-*). See docs/plan-instagram.md.

«Instagram pack» (960×540 at 60 fps, 70 s): twenty vertical stories shown three at a time inside phones over red /
blue blobs, five profile cards, and one «dynamic opener» played inside a feed post. Each story is laid out flat on
1080×1920 from the phone screens (155×281 px in the reference, ×6.97) and its moves are copied from 10 fps sheets of
each screen; the opener is a square post (1080×1080). Phones, glass reflections, the info labels, the pack cover,
the «INSTAGRAM STORIES» grid and the end card are skipped. The stories have no exit in the reference (the phones
leave): each one plays its entrance and holds. Frames below are 29.97 fps frames from the start of the story (the
10 fps sheet index × 3). Kit de Instagram; ids `ig3-*`, order 15300-. Study notes in
tienda/plantillas/estudio-23012546/NOTAS.md.

Brand words are neutral: «Instagram» in big type or as a wordmark → STORIES / Your Brand / Your Name (the camera
glyph stays only as a small icon), «JOHN WICK» → MARK STONE, «CS 6 Aftereffects» → V 6 Your program.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, label, square, tall
from llt_motion import frames_of
from scene import gradient, keys, no_stroke, tanim
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import S, arc, poly, ring
from templates_yp4 import art_except

W, H = 1080, 1920
WHITE, BLACK = "#FFFFFF", "#000000"
M = "Montserrat"
KAU, COOKIE, BOD, SLAB, VIBES = "Kaushan Script", "Cookie", "Bodoni Moda", "Alfa Slab One", "Great Vibes"
for _w, _f in ((400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"),
               (900, "Black")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"
f6._FILES[(KAU, 400)] = "fonts.basic/fonts/kaushanscript/KaushanScript-Regular.ttf"
f6._FILES[(COOKIE, 400)] = "fonts.extra/fonts/cookie/Cookie-Regular.ttf"
f6._FILES[(SLAB, 400)] = "fonts.extra/fonts/alfaslabone/AlfaSlabOne-Regular.ttf"
f6._FILES[(VIBES, 400)] = "fonts.basic/fonts/greatvibes/GreatVibes-Regular.ttf"
for _w, _f in ((500, "Medium"), (700, "Bold")):
    f6._FILES[(BOD, _w)] = f"fonts.extra/fonts/bodonimoda/BodoniModa-{_f}.ttf"

URL = "WWW.YOURSITE.COM"
TAGS = ["instagram", "historia", "reels"]


def _p(id, es, en, order, dur, tags=(), thumb=None, size=None):
    make = square if size == "square" else tall
    return make(f"ig3-{id}", es, en, "instagram", dur, order=order, tags=TAGS + list(tags),
                thumb_at=thumb or round(dur * 0.7, 1))


def grad(c0, c1, angle=90, a0=1.0, a1=1.0):
    return [gradient([(0.0, c0, a0), (1.0, c1, a1)], angle=angle), no_stroke()]


def lerp(a, b, q):
    return a + (b - a) * q


def wave(fr, period, phase=0.0):
    return math.sin(2 * math.pi * (fr / period + phase))


class St(S):
    """A story on 1080×1920 (or a square post): frames count straight from the start, no mirrored exit."""

    def __init__(self, t, dur, w=W, h=H):
        S.__init__(self, t, dur)
        self.w, self.h = w, h
        self.pivot = (w / 2, h / 2)

    def frame(self, u):
        return u * FPS

    # --- pieces -------------------------------------------------------------------------------------------------
    def ground(self, colour, name="Fondo", layers=None):
        return self.rect(name, layers or solid(colour), lambda fr, u: (-10, -10, self.w + 10, self.h + 10))

    def pic(self, name, sample, box=None, geom=None, rot=None, op=None, label=None, reuse=None):
        """A photo slot laid out in box (x0, y0, x1, y1; the whole frame by default); geom(fr) = (dx, dy, scale)."""
        x0, y0, x1, y1 = box or (0, 0, self.w, self.h)
        b = Box(x0, y0, x1 - x0, y1 - y0)
        motion = None
        if geom:
            motion = [(u, (lambda g: {"s": g[2], "dx": g[0], "dy": g[1]})(geom(fr)), "linear") for u, fr in self.each()]
        clip = self.t.photo(self.t.track("video", name), sample, 0.0, self.dur, b, motion, label=label or name,
                            reuse=reuse)
        clip["name"] = name
        if rot:
            clip["rotation"] = keys([(u, round(rot(fr), 3), "linear") for u, fr in self.each()])
        if op:
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, op(fr))), 4), "linear") for u, fr in self.each()])
        return clip

    def window(self, clip, name, geom, kind="ellipse", path=None, radius=0.0, base=None):
        """Shows clip only inside a shape that follows geom(fr, u) = (cx, cy, w, h, rot, op) (a track matte)."""
        win = self.obj(name, solid(WHITE), geom, kind=kind, path=path, radius=radius, base=base)
        clip["matte"] = {"clip": win["id"], "mode": "alpha"}
        return win

    def word(self, content, ink, family, weight, colour, name="Título", spacing=0.0, align="center", geom=None,
             reveal=None, shift=None, op=None, rot=None, layers=None):
        """A line whose ink is ink[2] - ink[0] wide (letter spacing `spacing` em included), centred on ink's
        height; geom(fr, u) = (dx, dy, scale, rot, opacity) moves it, or shift(fr) = (dx, dy) under a reveal."""
        x0, y0, x1, y1 = ink
        p = f6.Piece(self.t, self.dur, 0)
        p.frame = self.frame
        edge = (x0 + x1) / 2 if align == "center" else x0 if align == "left" else x1
        clip = p.text(content, edge, y0, y1, x1 - x0, family, weight, colour, name, align=align, spacing_em=spacing,
                      shift=shift, reveal=reveal, case="none", layers=layers)
        if geom:
            self.tmove(clip, geom)
        if op:
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, op(fr, u))), 4), "linear") for u, fr in self.each()])
        if rot:
            clip["rotation"] = keys([(u, round(rot(fr, u), 3), "linear") for u, fr in self.each()])
        return clip

    def come(self, clip, at, stagger=0.05, duration=0.3, preset="fade", order="forward", unit="character", **kw):
        """Letters (or words) come in from frame `at`; they stay (the stories have no exit)."""
        clip["textStyle"]["animation"] = {"in": tanim(preset, duration=duration, unit=unit, stagger=stagger,
                                                      ease="easeOut", delay=round(at / FPS, 3), order=order, **kw)}
        return clip

    def para(self, content, box, size, colour, name="Texto", font=M, weight=500, at=0, n=12, line=1.35):
        x0, y0, x1, y1 = box
        clip = label(self.t, self.t.track("text", name), content, 0.0, self.dur, Box(x0, y0, x1 - x0, y1 - y0), font,
                     size, colour, weight=weight, line=line, name=name)
        clip["opacity"] = keys([(u, round(k(fr, at, n), 4), "linear") for u, fr in self.each()])
        return clip

    def cam(self, name, geom, size, colour, width=None):
        """The camera glyph (a small social icon): geom(fr) = (cx, cy, scale, opacity)."""
        w = width or size * 0.09

        def part(rel, d):
            def g(fr, u):
                cx, cy, sc, op = geom(fr)
                return cx + rel[0] * size * sc, cy + rel[1] * size * sc, d * size * max(1e-3, sc), \
                    d * size * max(1e-3, sc), 0, op
            return g
        self.obj(name, ring(colour, w), part((0, 0), 1.0), radius=size * 0.28, base=(size, size))
        self.obj(f"{name} (lente)", ring(colour, w), part((0, 0), 0.46), kind="ellipse", base=(size * 0.46,) * 2)
        self.obj(f"{name} (punto)", solid(colour), part((0.26, -0.26), 0.11), kind="ellipse", base=(size * 0.11,) * 2)


def done(t, keep=("Fondo",)):
    return art_except(t, keep=keep)


# ======================================================================================================================
# 1. art 01 — «Stories» runs down the frame on its side, turns flat at the bottom; a square frame falls round «01»
# ======================================================================================================================
def arte():
    D = 5.6
    t = _p("arte", "Historia: art 01 Stories sobre pintura", "Story: art 01 Stories over a painting", 15300, D,
           ["arte", "pintura"])
    s = St(t, D)
    s.pic("Fondo (foto)", "ig3-paint-03", geom=lambda fr: (0, 0, 1.0 + 0.06 * fr / (D * FPS)), label="Foto")
    turn = lambda fr: k(fr, 45, 18)  # noqa: E731  the word turns flat and drops to the bottom

    def big(fr, u):
        q = turn(fr)
        dy0 = -1700 * (1 - k(fr, 0, 10))
        # from vertical (centre 560, 980, 1560 px long) to flat (centre 540, 1510, 700 px long)
        return lerp(0, -20, q), lerp(dy0, 530, q), lerp(1.0, 0.4, q), lerp(-90, 0, q), 1.0
    s.word("Stories", (-390, 760, 1510, 1200), M, 800, WHITE, "Título", geom=big)

    def small(fr, u):
        q = turn(fr)
        dy0 = -1700 * (1 - k(fr, 2, 10))
        # beside the big word while it stands, above it once it lies flat
        return lerp(0, -340, q), lerp(dy0, 140, q), lerp(1.0, 0.3, q), lerp(-90, 0, q), 1.0
    s.word("Instagram_", (365, 1210, 1315, 1290), M, 700, WHITE, "Texto", geom=small)
    fall = lambda fr: k(fr, 54, 39)  # noqa: E731
    s.obj("Marco", ring(WHITE, 12), lambda fr, u: (lerp(560, 515, fall(fr)), lerp(-500, 1023, fall(fr)), 720, 632,
                                                   lerp(35, 0, fall(fr)), 1.0 if fr >= 54 else 0.0), base=(720, 632))
    s.word("01", (220, 820, 810, 1230), M, 800, WHITE, "Número",
           geom=lambda fr, u: (0, 160 * (1 - k(fr, 75, 12)), 1, 0, k(fr, 75, 8)),
           )
    s.word("art", (180, 400, 880, 700), M, 800, WHITE, "Texto 2",
           geom=lambda fr, u: (0, 140 * (1 - k(fr, 70, 12)), 1, 0, k(fr, 70, 8)))
    return done(t)


# ======================================================================================================================
# 2. %100 Full — a brush «Full» writes itself over a kitten, the price and ENTERTAINMENT band come in
# ======================================================================================================================
def full():
    D = 5.6
    t = _p("full", "Historia: Full 100 % con letra de pincel", "Story: Full 100% in brush lettering", 15301, D,
           ["oferta", "mascotas"])
    s = St(t, D)
    s.pic("Fondo (foto)", "ig3-cat-03", geom=lambda fr: (0, 0, 1.12 - 0.08 * k(fr, 0, 40)), label="Foto")
    s.rect("Fondo (tono)", grad("#E8962A", "#E8962A", 90, 0.92, 0.0), lambda fr, u: (-10, -10, W + 10, 1250))
    s.word("Full", (20, 740, 1040, 1140), KAU, 400, WHITE, "Título",
           geom=lambda fr, u: (0, 0, 1.25 - 0.25 * k(fr, 0, 14), -8 * (1 - k(fr, 0, 14)), 1),
           reveal=None)
    full_clip = t.tracks[-1].clips[-1]
    track = t.tracks[-1]
    # written from the left: a rectangle mask that opens across the word
    mk = {"x": [], "w": []}
    for u, fr in s.each():
        q = k(fr, 0, 16)
        mk["x"].append((u, q / 2, "linear"))
        mk["w"].append((u, max(1e-3, q), "linear"))
    t.mask(track, full_clip, "rectangle", x=0.0, y=0.5, w=0.0, h=1.0,
           keyframes={"x": keys(mk["x"]), "w": keys(mk["w"])})
    s.word("%", (150, 290, 400, 520), M, 800, WHITE, "Signo",
           geom=lambda fr, u: (-160 * (1 - k(fr, 9, 10)), 0, 1, 0, k(fr, 9, 6)))
    s.word("100", (412, 405, 820, 520), M, 800, WHITE, "Número",
           geom=lambda fr, u: (-160 * (1 - k(fr, 12, 10)), 0, 1, 0, k(fr, 12, 6)))
    s.word("NOW!", (150, 560, 500, 642), M, 800, WHITE, "Texto",
           geom=lambda fr, u: (-160 * (1 - k(fr, 15, 10)), 0, 1, 0, k(fr, 15, 6)))
    s.rect("Franja", solid("#23272F", 0.75), lambda fr, u: (133, 1220, 133 + 861 * k(fr, 15, 12), 1288))
    c = s.word("ENTERTAINMENT", (160, 1230, 968, 1278), M, 600, "#E9E9E9", "Texto 2", spacing=0.3)
    s.come(c, 21, stagger=0.025, duration=0.2)
    return done(t)


# ======================================================================================================================
# 3. FASHION 45$ — a yellow photo band opens from the middle; a dark band carries a huge FASHION filled with the photo
# ======================================================================================================================
def fashion():
    D = 5.8
    t = _p("fashion", "Historia: FASHION 45 $ con letras de foto", "Story: FASHION 45$ with photo-filled letters", 15302,
           D, ["moda", "oferta"])
    s = St(t, D)
    s.ground(WHITE, "Fondo")
    ph = s.pic("Fondo (foto)", "ig3-headphones-03", geom=lambda fr: (0, 260, 1.1 - 0.06 * k(fr, 0, 60)), label="Foto")
    s.window(ph, "Fondo (ventana)", lambda fr, u: (540, lerp(790, 960, k(fr, 0, 30)), 1200,
                                                  lerp(460, 1940, k(fr, 0, 30)), 0, 1), kind="rectangle",
             base=(1200, 1940))
    s.rect("Fondo (banda)", solid("#1E2433", 0.82), lambda fr, u: (-10, lerp(1400, 1136, k(fr, 0, 18)), W + 10,
                                                           lerp(1500, 1890, k(fr, 0, 18))))
    slide = lambda fr: -760 * fr / (D * FPS)  # noqa: E731  the big word drifts left
    big = s.word("FASHION", (-400, 1290, 2700, 1690), BOD, 500, WHITE, "Fondo (texto grande)", spacing=0.15,
                 geom=lambda fr, u: (slide(fr), 0, 1, 0, k(fr, 6, 9)))
    fill = s.pic("Fondo (foto en letras)", "ig3-headphones-03", reuse=ph["placeholderId"],
                 geom=lambda fr: (0, 260, 1.1 - 0.06 * k(fr, 0, 60)))
    fill["matte"] = {"clip": big["id"], "mode": "alpha"}
    c = s.word("FASHION", (84, 197, 996, 293), BOD, 500, "#1A1A1A", "Título", spacing=0.2)
    s.come(c, 15, stagger=0.05, duration=0.2)
    s.word("MODERN FASHION SALE", (300, 322, 780, 346), M, 600, "#2A2A2A", "Texto", spacing=0.2,
           op=lambda fr, u: k(fr, 30, 9))
    s.word("45$", (330, 360, 750, 490), BOD, 700, "#1A1A1A", "Precio", spacing=0.15,
           geom=lambda fr, u: (0, 50 * (1 - k(fr, 36, 10)), 1, 0, k(fr, 36, 8)))
    return done(t)


# ======================================================================================================================
# 4. YOUR LIFE / PRO — colour bands sweep up off the photo; the cyan label rises; the photo rolls down and PRO drops
# ======================================================================================================================
def your_life():
    D = 5.6
    t = _p("your-life", "Historia: YOUR LIFE y PRO con franjas de color", "Story: YOUR LIFE and PRO with colour bands",
           15303, D, ["interiores"])
    s = St(t, D)
    roll = lambda fr: k(fr, 57, 18)  # noqa: E731  the photo rolls down and comes round again
    a = s.pic("Fondo (foto)", "ig3-lamp-03", geom=lambda fr: (0, H * roll(fr), 1.04), label="Foto")
    s.pic("Fondo (foto 2)", "ig3-lamp-03", reuse=a["placeholderId"], geom=lambda fr: (0, -H * (1 - roll(fr)), 1.04),
          op=lambda fr: 1.0 if fr >= 57 else 0.0)
    up = lambda fr: -2100 * k(fr, 0, 26)  # noqa: E731
    for name, colour, y0, y1 in (("Franja blanca", WHITE, -400, 270), ("Franja negra", "#141414", 270, 510),
                                 ("Franja roja", "#EF5A4B", 510, 1090), ("Franja cian", "#1ED3E6", 1090, 1700)):
        s.rect(name, solid(colour), lambda fr, u, y0=y0, y1=y1: (-10, y0 + up(fr), W + 10, y1 + up(fr)))
    lift = lambda fr: lerp(1700, 197, k(fr, 9, 66))  # noqa: E731  centre of the label
    s.rect("Etiqueta", solid("#1ED3E6"), lambda fr, u: (84, lift(fr) - 67, 994, lift(fr) + 67))
    s.word("YOUR LIFE", (150, 0, 930, 0), M, 700, WHITE, "Título", spacing=0.18,
           geom=lambda fr, u: (0, lift(fr), 1, 0, 1))
    s.word(URL, (260, 0, 820, 0), M, 600, WHITE, "Web", spacing=0.15,
           geom=lambda fr, u: (0, lift(fr) + 110, 1, 0, 1))
    drop = lambda fr: -1150 * (1 - k(fr, 78, 32))  # noqa: E731
    s.rect("Caja", solid(WHITE, 0.28), lambda fr, u: (0, 1320 + drop(fr), 980, 1880 + drop(fr)),
           op=lambda fr, u: k(fr, 90, 20))
    s.word("PRO", (126, 1590, 876, 1780), M, 500, WHITE, "Texto", spacing=0.12,
           geom=lambda fr, u: (0, drop(fr), 1, 0, k(fr, 78, 6)))
    return done(t)


# ======================================================================================================================
# 5. A-01 MODERN SCIENCE — a circle of ink opens over cyan, translucent circles pop, «A - 01» types
# ======================================================================================================================
def science():
    D = 6.0
    t = _p("ciencia", "Historia: A-01 MODERN SCIENCE con círculos", "Story: A-01 MODERN SCIENCE with circles", 15304,
           D, ["ciencia", "círculo"])
    s = St(t, D)
    cyan = "#38D3E6"
    s.ground(cyan, "Fondo")
    ink = s.pic("Fondo (foto)", "ig3-ink-01", geom=lambda fr: (0, 0, 1.15 - 0.1 * k(fr, 0, 60)), label="Foto")
    s.window(ink, "Fondo (círculo)", lambda fr, u: (540, lerp(900, 860, k(fr, 0, 30)), lerp(1250, 3300, k(fr, 0, 30)),
                                                  lerp(1250, 3300, k(fr, 0, 30)), 0, 1), base=(3300, 3300))
    s.obj("Esquina", solid(cyan), lambda fr, u: (170, 1790, 520, 400, 0, k(fr, 24, 9)),
          path=poly([(0, 30), (60, 100), (0, 100)]))
    s.obj("Esquina 2", solid(cyan), lambda fr, u: (960, 1830, 300, 260, 0, k(fr, 27, 9)),
          path=poly([(100, 0), (100, 100), (20, 100)]))
    s.obj("Raya", solid(WHITE), lambda fr, u: (130, 1820, 220, 30, -45, k(fr, 30, 9)))
    for i, (name, colour, alpha, cx, cy, d, at) in enumerate((
            ("Círculo rosa", "#F08BD8", 0.72, 329, 762, 700, 6), ("Círculo coral", "#F0607A", 0.82, 784, 1000, 630, 9),
            ("Círculo azul", "#1EA7FF", 1.0, 399, 1224, 315, 12), ("Círculo oscuro", "#3A1D4A", 0.55, 539, 1612, 490, 15),
            ("Círculo oscuro 2", "#3A1D4A", 0.45, 330, 1800, 380, 18))):
        s.obj(name, solid(colour, alpha), lambda fr, u, cx=cx, cy=cy, d=d, at=at: (
            cx, cy + 6 * wave(fr, 90, cx / 300), d * k(fr, at, 12), d * k(fr, at, 12), 0, 1), kind="ellipse",
            base=(d, d))
    c = s.word("A - 01", (84, 490, 1029, 674), M, 500, WHITE, "Título", spacing=0.15)
    s.come(c, 24, stagger=0.12, duration=0.2)
    s.word("MODERN", (119, 741, 959, 823), M, 500, WHITE, "Texto", spacing=0.35,
           geom=lambda fr, u: (0, 30 * (1 - k(fr, 6, 12)), 1, 0, k(fr, 6, 9)))
    s.word("SCIENCE", (119, 911, 994, 999), M, 500, WHITE, "Texto 2", spacing=0.35,
           geom=lambda fr, u: (0, 30 * (1 - k(fr, 10, 12)), 1, 0, k(fr, 10, 9)))
    s.rect("Web (fondo)", solid("#202020"), lambda fr, u: (300, 1036, 300 + 480 * k(fr, 18, 10), 1064))
    s.word("www.yoursite.com", (330, 1040, 750, 1060), M, 600, WHITE, "Web", spacing=0.1,
           op=lambda fr, u: k(fr, 24, 6))
    return done(t)


# ======================================================================================================================
# 6. Say what's on your mind — a lilac-ringed circle of food rises over purple rings; brackets close round the line
# ======================================================================================================================
def mind():
    D = 6.0
    t = _p("comida-circulo", "Historia: Say what's on your mind en círculo", "Story: Say what's on your mind in a circle",
           15305, D, ["comida", "círculo"])
    s = St(t, D)
    s.ground("#4B1690", "Fondo", layers=grad("#5B1FA6", "#3A1477", 90))
    pulse = lambda fr: 1.0 + 0.12 * (fr / (D * FPS))  # noqa: E731
    for i in range(10):
        d = 980 + 260 * i
        s.obj(f"Anillo {i + 1}", ring("#D63BC4", 26), lambda fr, u, d=d, i=i: (540, 966, d * pulse(fr), d * pulse(fr), 0,
                                                                              0.55 * k(fr, 2 * i, 12)),
              kind="ellipse", base=(d, d))
    go = lambda fr: k(fr, 0, 39)  # noqa: E731
    cy = lambda fr: lerp(1250, 966, go(fr))  # noqa: E731
    dd = lambda fr: lerp(480, 875, go(fr))  # noqa: E731
    s.obj("Aro", solid("#C99CF5"), lambda fr, u: (540, cy(fr), dd(fr) + 40, dd(fr) + 40, 0, 1), kind="ellipse",
          base=(915, 915))
    ph = s.pic("Foto", "ig3-fruit-03", geom=lambda fr: (0, cy(fr) - 966, lerp(0.6, 1.0, go(fr))))
    s.window(ph, "Foto (círculo)", lambda fr, u: (540, cy(fr), dd(fr), dd(fr), 0, 1), base=(875, 875))
    line = s.word("Say what's on your mind", (110, 0, 970, 0), M, 500, WHITE, "Título",
                  geom=lambda fr, u: (0, lerp(1790, 958, k(fr, 12, 36)), 1, 0, k(fr, 6, 6)))
    line["textStyle"]["runs"] = [{"start": 0, "end": 13, "boldEnabled": True, "bold": True}]
    for i, x in enumerate((40, 1040)):
        side = -1 if i == 0 else 1
        s.rect(f"Corchete {i + 1}", solid(WHITE, 0.8), lambda fr, u, x=x: (x - 2, 868, x + 2, 1048),
               op=lambda fr, u: k(fr, 54, 8))
        for j, y in enumerate((868, 1046)):
            s.rect(f"Corchete {i + 1} ({j + 1})", solid(WHITE, 0.8),
                   lambda fr, u, x=x, y=y, side=side: (min(x, x - side * 30 * k(fr, 54, 8)), y - 2,
                                                       max(x, x - side * 30 * k(fr, 54, 8)), y + 2))
    return done(t)


# ======================================================================================================================
# 7. INTRODUCING STORIES — over a snowy forest the lines rise, three dots; a white slant brings a huge running word
# ======================================================================================================================
def introducing():
    D = 6.8
    t = _p("introducing", "Historia: INTRODUCING STORIES en el bosque", "Story: INTRODUCING STORIES in the forest", 15306,
           D, ["invierno", "presentación"])
    s = St(t, D)
    s.pic("Fondo (foto)", "ig3-snow-01", geom=lambda fr: (0, 0, 1.0 + 0.08 * fr / (D * FPS)), label="Foto")
    s.rect("Fondo (degradado)", [gradient([(0.0, "#2BC8DD", 0.0), (0.45, "#2BC8DD", 0.55), (1.0, "#2BC8DD", 1.0)],
                                          angle=90), no_stroke()], lambda fr, u: (-10, 700, W + 10, H + 10))
    up = lambda fr: k(fr, 84, 15)  # noqa: E731  the block climbs when the white slant comes
    rows = (("INTRODUCING", (84, 660, 996, 741), 800, 0.0, 0, 205 - 700), ("OUR NEW", (230, 789, 850, 871), 400, 0.05, 4,
            354 - 830), ("STORIES", (84, 925, 1015, 1081), 800, 0.0, 8, 520 - 1003))
    for i, (txt, ink, wt, sp, at, dy) in enumerate(rows):
        s.word(txt, ink, M, wt, WHITE, ["Título", "Texto", "Texto 2"][i], spacing=sp,
               geom=lambda fr, u, at=at, dy=dy: (0, 900 * (1 - k(fr, at, 30)) + dy * up(fr), 1, 0, k(fr, at, 9)))
    for i in range(3):
        def dot(fr, u, i=i):
            q = up(fr)
            return lerp(540, 259 + 280 * i, q), lerp(1200 + 105 * i, 707, q), 56 * k(fr, 30 + 9 * i, 6), \
                56 * k(fr, 30 + 9 * i, 6), 0, 1
        s.obj(f"Punto {i + 1}", solid(WHITE), dot, kind="ellipse", base=(56, 56))
    slant = lambda fr: 1300 * (1 - k(fr, 84, 15))  # noqa: E731
    panel = s.obj("Fondo (panel)", solid(WHITE), lambda fr, u: (540 + slant(fr) * 0.4, 1440 + slant(fr), 1080, 970, 0, 1),
                  path=poly([(0, 60), (100, 0), (100, 100), (0, 100)]), base=(1080, 970))
    del panel
    run = lambda fr: -950 * k(fr, 84, 120)  # noqa: E731
    s.word("INTRODUCING", (60, 1272, 3460, 1646), M, 900, "#27C3D9", "Texto grande",
           geom=lambda fr, u: (run(fr), slant(fr), 1, 0, 0.9))
    return done(t)


# ======================================================================================================================
# 8. TRAVEL NEW — a balloon in a pink sky, a green brush stroke wipes in under a pink NEW
# ======================================================================================================================
def new():
    D = 5.6
    t = _p("new", "Historia: NEW de viaje con trazo de pincel", "Story: travel NEW with a brush stroke", 15307, D,
           ["viajes", "pincel"])
    s = St(t, D)
    s.pic("Fondo (foto)", "ig3-balloon-02", geom=lambda fr: (0, -120 * k(fr, 0, 40), 1.0 + 0.35 * k(fr, 0, 40)),
          label="Foto")
    s.rect("Fondo (tono)", [gradient([(0.0, "#FF5FA8", 0.0), (1.0, "#FF5FA8", 0.7)], angle=90), no_stroke()],
           lambda fr, u: (-10, 900, W + 10, H + 10))
    s.word("TRAVEL", (420, 1205, 660, 1240), M, 700, WHITE, "Texto", spacing=0.5, op=lambda fr, u: k(fr, 24, 9))
    brush = poly([(2, 30), (10, 14), (30, 8), (55, 4), (80, 2), (98, 6), (96, 20), (100, 32), (92, 52), (97, 66),
                  (88, 80), (60, 86), (40, 92), (18, 98), (4, 92), (8, 76), (0, 62), (6, 46)])
    wipe = lambda fr: k(fr, 15, 10)  # noqa: E731
    stroke = s.obj("Trazo", solid("#6BF04F"), lambda fr, u: (556, 1456, 950, 312, -4, 1), path=brush)
    t.mask(next(tr for tr in t.tracks if stroke in tr.clips), stroke, "rectangle", x=0.0, y=0.5, w=0.0, h=1.4,
           keyframes={"x": keys([(u, wipe(fr) / 2, "linear") for u, fr in s.each()]),
                      "w": keys([(u, max(1e-3, wipe(fr)), "linear") for u, fr in s.each()])})
    s.word("NEW", (170, 1345, 950, 1560), M, 900, "#F25AA5", "Título", spacing=-0.02,
           reveal=lambda fr: (0, 1200, 120 + 960 * k(fr, 18, 10), 1700))
    return done(t)


# ======================================================================================================================
# 9. TECH — TECHNOLOGY scattered in the corners, then a white bar drops with TECH on its side
# ======================================================================================================================
def tech():
    D = 6.0
    t = _p("tech", "Historia: TECH con letras sueltas", "Story: TECH with scattered letters", 15308, D,
           ["tecnología"])
    s = St(t, D)
    s.ground("#140C14", "Fondo")
    s.pic("Fondo (foto)", "ig3-tech-02", geom=lambda fr: (0, 0, 1.12 - 0.08 * k(fr, 0, 90)), label="Foto")
    s.rect("Fondo (tono)", [gradient([(0.0, "#C0402A", 0.25), (1.0, "#200A20", 0.35)], angle=45), no_stroke()],
           lambda fr, u: (-10, -10, W + 10, H + 10))
    sink = lambda fr: 990 * k(fr, 33, 15)  # noqa: E731
    spots = (("T", 40, 571), ("E", 504, 558), ("C", 1036, 558), ("H", 40, 660), ("N", 40, 741), ("O", 1036, 660),
             ("L", 889, 810), ("O", 962, 810), ("G", 1036, 810), ("Y", 1036, 880))
    for i, (ch, x, y) in enumerate(spots):
        s.word(ch, (x - 20, y - 26, x + 20, y + 26), M, 700, WHITE, "Letras" if i == 0 else f"Letras {i + 1}",
               geom=lambda fr, u, i=i: (0, sink(fr) - 20 * (1 - k(fr, 3 + 3 * i, 6)), 1, 0, k(fr, 3 + 3 * i, 6)))
    bar = lambda fr: (385, lerp(-1130, 265, k(fr, 30, 21)), 693, lerp(-10, 1387, k(fr, 30, 21)))  # noqa: E731
    s.rect("Barra", solid(WHITE), lambda fr, u: bar(fr))
    c = s.word("TECH", (340, 760, 1300, 900), M, 900, "#1A1A2E", "Título", spacing=0.35,
               geom=lambda fr, u: (-281, bar(fr)[1] - 265 + 0, 1, -90, 1))
    c["textStyle"]["runs"] = [{"start": 3, "end": 4, "colorEnabled": True, "color": "#ff8e1f2e"}]
    return done(t)


# ======================================================================================================================
# 10. SPORT — a pink badge pops, sinks to the bottom where a cyan disc rises with a huge running SPORT
# ======================================================================================================================
def sport():
    D = 6.0
    t = _p("sport", "Historia: SPORT con insignia rosa", "Story: SPORT with a pink badge", 15309, D, ["deporte"])
    s = St(t, D)
    s.pic("Fondo (foto)", "ig3-boxer-04", geom=lambda fr: (0, 0, 1.1 - 0.06 * k(fr, 0, 90)), label="Foto")
    rise = lambda fr: k(fr, 36, 15)  # noqa: E731
    dgeom = lambda fr, u: (540, lerp(3300, 2330, rise(fr)), 1800, 1800, 0, 1)  # noqa: E731
    s.obj("Disco", solid("#45D6E8"), dgeom, kind="ellipse")
    disc = s.obj("Disco (recorte)", solid(WHITE), dgeom, kind="ellipse")
    run = lambda fr: -700 * fr / (D * FPS)  # noqa: E731
    big = s.word("SPORT", (60, 1760, 1500, 2080), M, 900, "#1B2140", "Texto grande", spacing=0.1,
                 geom=lambda fr, u: (run(fr), 900 * (1 - rise(fr)), 1, 0, 1))
    big["matte"] = {"clip": disc["id"], "mode": "alpha"}
    sink = lambda fr: k(fr, 30, 30)  # noqa: E731
    by = lambda fr: lerp(966, 1455, sink(fr))  # noqa: E731
    pop = lambda fr: k(fr, 0, 8)  # noqa: E731
    s.obj("Insignia", solid("#F45BB0"), lambda fr, u: (539, by(fr), 665 * pop(fr), 665 * pop(fr), 0, 1),
          kind="ellipse", base=(665, 665))
    s.word("SPORT", (275, 0, 805, 0), M, 800, "#1B2140", "Título", spacing=0.25,
           geom=lambda fr, u: (0, by(fr), pop(fr), 0, k(fr, 4, 6)))
    for i, dy in enumerate((-82, 82)):
        s.word("GOOD TIMES", (420, 0, 660, 0), M, 700, WHITE, "Texto" if i == 0 else "Texto 2", spacing=0.3,
               geom=lambda fr, u, dy=dy: (0, by(fr) + dy, pop(fr), 0, k(fr, 6, 6)))
    c = s.word("SPORT", (870, 210, 1150, 250), M, 700, WHITE, "Texto 3", spacing=0.3, rot=lambda fr, u: 90)
    s.come(c, 33, stagger=0.06, duration=0.2)
    return done(t)


# ======================================================================================================================
# 11. FRIEND GREAT TRIP — a bright circle of the photo rises inside a thin ring over the darkened photo
# ======================================================================================================================
def friend():
    D = 6.0
    t = _p("friend", "Historia: FRIEND GREAT TRIP con círculo", "Story: FRIEND GREAT TRIP with a circle", 15310, D,
           ["amigos", "círculo"])
    s = St(t, D)
    zoom = lambda fr: (0, 0, 1.08 - 0.06 * k(fr, 0, 90))  # noqa: E731
    a = s.pic("Fondo (foto)", "ig3-sofa-02", geom=zoom, label="Foto")
    s.rect("Fondo (oscuro)", solid("#2E2E2E", 0.55), lambda fr, u: (-10, -10, W + 10, H + 10))
    go = lambda fr: k(fr, 0, 39)  # noqa: E731
    cy = lambda fr: lerp(1560, 993, go(fr))  # noqa: E731
    dd = lambda fr: lerp(280, 840, go(fr))  # noqa: E731
    lit = s.pic("Foto (círculo)", "ig3-sofa-02", reuse=a["placeholderId"], geom=zoom)
    s.window(lit, "Círculo", lambda fr, u: (540, cy(fr), dd(fr), dd(fr), 0, 1), base=(840, 840))
    s.obj("Aro", ring(WHITE, 3), lambda fr, u: (540, cy(fr), dd(fr) + 70, dd(fr) + 70, 0, 0.75), kind="ellipse",
          base=(910, 910))
    c = s.word("FRIEND", (119, 252, 961, 320), M, 700, WHITE, "Título", spacing=0.45)
    s.come(c, 15, stagger=0.05, duration=0.25, preset="rise")
    c = s.word("GREAT", (329, 388, 751, 436), M, 700, WHITE, "Texto", spacing=0.4)
    s.come(c, 39, stagger=0.05, duration=0.25, preset="rise")
    s.word("TRIP", (480, 462, 600, 484), M, 700, WHITE, "Texto 2", spacing=0.4, op=lambda fr, u: k(fr, 48, 9))
    for i in range(3):
        s.obj(f"Punto {i + 1}", solid(WHITE), lambda fr, u, i=i: (540, 1476 + 54 * i, 18, 18, 0, k(fr, 30 + 4 * i, 6)),
              kind="ellipse")
    return done(t)


# ======================================================================================================================
# 12. Product Promo — a yellow disc grows from the right, a round product photo, the two words stand up, a paragraph
# ======================================================================================================================
LOREM = ("Lorem ipsum dolor sit amet, consectetur\nadipiscing elit, sed do eiusmod tempor\nincididunt ut labore et "
         "dolore magna aliqua.\nUt enim ad minim veniam, quis nostrud\nexercitation ullamco laboris nisi ut")


def promo():
    D = 6.0
    t = _p("promo", "Historia: Product Promo con círculo amarillo", "Story: Product Promo with a yellow disc", 15311, D,
           ["producto", "promoción"])
    s = St(t, D)
    s.ground("#1C1C22", "Fondo")
    s.obj("Fondo granate", solid("#5A2A2E"), lambda fr, u: (300, 2350, 3600, 3400, 0, k(fr, 0, 9)), kind="ellipse")
    s.obj("Fondo azul", solid("#1D2236"), lambda fr, u: (1250, 1700, 900, 900, 0, k(fr, 3, 9)), kind="ellipse")
    s.rect("Raya roja", solid("#F0402F"), lambda fr, u: (1062, 600, 1090, 600 + 1320 * k(fr, 6, 15)))
    g = lambda fr: k(fr, 6, 18)  # noqa: E731
    s.obj("Círculo", solid("#FFC107"), lambda fr, u: (980, 890, 920 * g(fr), 920 * g(fr), 0, 1), kind="ellipse",
          base=(920, 920))
    p = lambda fr: k(fr, 24, 9)  # noqa: E731
    s.obj("Aro", solid("#FFC107"), lambda fr, u: (514, 917, 420 * p(fr), 420 * p(fr), 0, 1), kind="ellipse",
          base=(420, 420))
    ph = s.pic("Foto", "ig3-lamp-03", box=(284, 687, 744, 1147), geom=lambda fr: (0, 0, 1.0))
    s.window(ph, "Foto (círculo)", lambda fr, u: (514, 917, 385 * p(fr), 385 * p(fr), 0, 1), base=(385, 385))
    s.word("Product", (560, 590, 1140, 730), M, 800, WHITE, "Texto", rot=lambda fr, u: -90,
           geom=lambda fr, u: (0, 320 * (1 - k(fr, 27, 12)), 1, -90, k(fr, 27, 6)),
           reveal=None)
    s.word("Promo", (578, 960, 1312, 1110), M, 900, "#1C1C22", "Título",
           geom=lambda fr, u: (0, 320 * (1 - k(fr, 33, 12)), 1, -90, k(fr, 33, 6)))
    s.para(LOREM, (120, 1610, 960, 1860), 28, WHITE, at=39)
    return done(t)


# ======================================================================================================================
# 13. PORTFOLIO — the word drops in a wave on the photo; the picture splits into two columns that slide past; a name
# ======================================================================================================================
def portfolio():
    D = 6.0
    t = _p("portfolio", "Historia: PORTFOLIO con nombre", "Story: PORTFOLIO with a name", 15312, D, ["portafolio"])
    s = St(t, D)
    cut = lambda fr: k(fr, 51, 15)  # noqa: E731  the two columns slide
    a = s.pic("Fondo (foto)", "ig3-hood-01", geom=lambda fr: (0, 0, 1.06 + 0.04 * k(fr, 0, 51)), label="Foto")
    for i, (x0, x1, way) in enumerate(((0, 540, -1), (540, W, 1))):
        c = s.pic(f"Fondo (columna {i + 1})", "ig3-hood-01", reuse=a["placeholderId"],
                  geom=lambda fr, way=way: (0, way * H * (1 - cut(fr)), 1.25), op=lambda fr: 1.0 if fr >= 51 else 0.0)
        s.window(c, f"Columna {i + 1}", lambda fr, u, x0=x0, x1=x1, way=way: (
            (x0 + x1) / 2, H / 2 + way * H * (1 - cut(fr)), x1 - x0, H, 0, 1), kind="rectangle", base=(x1 - x0, H))
    s.rect("Fondo (oscuro)", solid(BLACK, 0.2), lambda fr, u: (-10, -10, W + 10, H + 10))
    c = s.word("PORTFOLIO", (105, 796, 975, 878), M, 800, WHITE, "Texto 3",
               op=lambda fr, u: 1 - k(fr, 51, 6))
    s.come(c, 0, stagger=0.04, duration=0.3, preset="drop")
    s.word("MARK", (150, 925, 930, 1068), M, 900, WHITE, "Título", reveal=lambda fr: (0, 860, W, 1080),
           shift=lambda fr: (0, 230 * (1 - k(fr, 69, 15))))
    s.word("STONE", (120, 1095, 960, 1238), M, 900, WHITE, "Texto", reveal=lambda fr: (0, 1080, W, 1260),
           shift=lambda fr: (0, 230 * (1 - k(fr, 63, 15))))
    s.obj("Caja", ring(WHITE, 4), lambda fr, u: (540, 1352, 560 * k(fr, 66, 12), 104, 0, 1), radius=14,
          base=(560, 104))
    s.word("PORTFOLIO", (340, 1332, 740, 1372), M, 800, WHITE, "Texto 2", op=lambda fr, u: k(fr, 72, 8))
    return done(t)


# ======================================================================================================================
# 14. Food 50% DISCOUNT — a pink square falls turning onto a donut; the photo darkens and the square becomes a label
# ======================================================================================================================
def food():
    D = 6.0
    t = _p("food", "Historia: Food 50 % de descuento", "Story: Food 50% discount", 15313, D, ["comida", "oferta"])
    s = St(t, D)
    s.ground("#0E0E10", "Fondo")
    ch = lambda fr: k(fr, 69, 15)  # noqa: E731  second look
    ph = s.pic("Fondo (foto)", "ig3-donut-02", geom=lambda fr: (0, 0, lerp(1.25, 1.0, ch(fr))), label="Foto")
    s.window(ph, "Fondo (ventana)", lambda fr, u: (540, lerp(1340, 960, ch(fr)), 1200, lerp(1160, 1940, ch(fr)), 0, 1),
             kind="rectangle", base=(1200, 1940))
    s.rect("Fondo (velo)", solid("#1E4A50", 0.6), lambda fr, u: (-10, -10, W + 10, H + 10), op=lambda fr, u: ch(fr))

    def sq(fr, u):
        q = k(fr, 6, 33)
        cx, cy, w, h = 556, lerp(-500, 931, q), 595, 595
        r = lerp(28, 0, q)
        return lerp(cx, 539, ch(fr)), lerp(cy, 452, ch(fr)), lerp(w, 630, ch(fr)), lerp(h, 238, ch(fr)), r, \
            1.0 if fr >= 6 else 0.0
    s.obj("Cuadrado", grad("#FF2A3E", "#FF2AA8", 135), lambda fr, u: (*sq(fr, u)[:5], sq(fr, u)[5] * (1 - ch(fr))),
          base=(630, 595))
    s.obj("Caja", solid(WHITE), lambda fr, u: (*sq(fr, u)[:5], ch(fr)), base=(630, 595))
    s.word("Food", (330, 0, 750, 0), SLAB, 400, "#2A2A2A", "Título",
           geom=lambda fr, u: (0, sq(fr, u)[1], 1, sq(fr, u)[4], k(fr, 42, 9)))
    s.word("50% DISCOUNT", (330, 625, 750, 660), M, 600, WHITE, "Texto", spacing=0.12, op=lambda fr, u: k(fr, 78, 9))
    s.obj("Web (caja)", ring(WHITE, 3), lambda fr, u: (540, 1544, 700 * k(fr, 75, 12), 84, 0, 1), base=(700, 84))
    s.word("www.yoursite.com", (330, 1530, 750, 1560), M, 600, WHITE, "Web", spacing=0.1, op=lambda fr, u: k(fr, 81, 9))
    return done(t)


# ======================================================================================================================
# 15. MODELS FASHION — a portrait under a red-to-cyan wash; a bracket grows round MODELS; dark tags slide in
# ======================================================================================================================
def models():
    D = 6.0
    t = _p("models", "Historia: MODELS FASHION con corchete", "Story: MODELS FASHION with a bracket", 15314, D,
           ["moda", "retrato"])
    s = St(t, D)
    s.pic("Fondo (foto)", "ig3-model-01", geom=lambda fr: (0, 0, 1.1 - 0.06 * k(fr, 0, 90)), label="Foto")
    s.rect("Fondo (degradado)", [gradient([(0.0, "#FF2A55", 0.55), (0.45, "#E85A8A", 0.55), (1.0, "#3FD9E8", 0.97)],
                                          angle=90), no_stroke()], lambda fr, u: (-10, -10, W + 10, H + 10))
    drift = lambda fr: 380 * k(fr, 75, 45)  # noqa: E731
    tall_ = lambda fr: 260 * k(fr, 99, 15)  # noqa: E731  the bracket grows up and the «1» bar comes

    def bracket(r):
        return lambda fr, u: (r[0], r[1] + drift(fr), r[2], r[3] + drift(fr))
    g = lambda fr: k(fr, 9, 21)  # noqa: E731
    s.rect("Corchete", solid(WHITE), lambda fr, u: (45, 1080 - (380 + tall_(fr)) * g(fr) + drift(fr), 55,
                                                     1080 + drift(fr)))
    s.rect("Corchete (abajo)", solid(WHITE), bracket((45, 1072, 45 + 140, 1082)), op=lambda fr, u: g(fr))
    s.rect("Corchete (arriba)", solid(WHITE), lambda fr, u: (45, 700 - tall_(fr) + drift(fr), 45 + 70 * g(fr),
                                                             710 - tall_(fr) + drift(fr)))
    s.rect("Barra", solid(WHITE), lambda fr, u: (105, 580 + drift(fr), 145, 580 + 270 * k(fr, 102, 12) + drift(fr)))
    s.word("MODELS", (119, 877, 996, 1013), M, 500, WHITE, "Título", spacing=0.1,
           geom=lambda fr, u: (120 * (1 - k(fr, 0, 27)), drift(fr), 1, 12 * (1 - k(fr, 0, 27)), k(fr, 0, 9)))
    sp = lambda fr: 150 * k(fr, 75, 45)  # noqa: E731
    s.rect("Etiqueta", solid("#2A2A3A", 0.85), lambda fr, u: (994 - 560 * k(fr, 15, 12), 1033 + drift(fr) + sp(fr),
                                                              994, 1115 + drift(fr) + sp(fr)))
    s.word("FASHION", (470, 1050, 970, 1098), M, 700, WHITE, "Texto", spacing=0.12,
           geom=lambda fr, u: (0, drift(fr) + sp(fr), 1, 0, k(fr, 21, 6)))
    s.rect("Etiqueta 2", solid("#2A2A3A", 0.85), lambda fr, u: (994 - 805 * k(fr, 27, 12), 1135 + drift(fr) + 1.4 * sp(fr),
                                                                994, 1183 + drift(fr) + 1.4 * sp(fr)))
    s.word("NEW YEAR CATALOGUE", (230, 1148, 960, 1170), M, 700, WHITE, "Texto 2", spacing=0.12,
           geom=lambda fr, u: (0, drift(fr) + 1.4 * sp(fr), 1, 0, k(fr, 33, 6)))
    return done(t)


# ======================================================================================================================
# 16. MUSIC EXCLUSIVE — thin rings turn round MUSIC over a blue concert; a little equaliser jumps
# ======================================================================================================================
def music():
    D = 6.0
    t = _p("music", "Historia: MUSIC EXCLUSIVE con aros", "Story: MUSIC EXCLUSIVE with rings", 15315, D,
           ["música", "círculo"])
    s = St(t, D)
    s.pic("Fondo (foto)", "ig3-concert-01", geom=lambda fr: (0, 0, 1.12 - 0.06 * k(fr, 0, 90)), label="Foto")
    s.rect("Fondo (tono)", grad("#2A1A70", "#0F1A60", 90, 0.55, 0.65), lambda fr, u: (-10, -10, W + 10, H + 10))
    g = lambda fr: k(fr, 3, 21)  # noqa: E731
    s.obj("Aro", ring(WHITE, 4), lambda fr, u: (539, 966, 805, 805, -120 * (1 - g(fr)), 1), path=None,
          kind="ellipse")
    for i, (d, a0, a1, speed) in enumerate(((940, 280, 360, 1.2), (1040, 300, 345, -0.8), (900, 130, 175, 0.9))):
        s.obj(f"Arco {i + 1}", ring(WHITE, 4), lambda fr, u, d=d, speed=speed: (
            539, 966, d * g(fr), d * g(fr), speed * fr * 2, 1), path=arc(a0, a1), base=(d, d))
    s.word("MUSIC", (259, 897, 821, 1013), M, 700, WHITE, "Título", reveal=lambda fr: (200, 850, 880, 1030),
           shift=lambda fr: (500 * (1 - k(fr, 3, 12)), 0))
    s.word("EXCLUSIVE", (300, 1032, 780, 1068), M, 600, "#B9B4D6", "Texto", spacing=0.35, op=lambda fr, u: k(fr, 12, 9))
    s.word("www.yoursite.com", (390, 1330, 690, 1350), M, 600, WHITE, "Web", spacing=0.12,
           op=lambda fr, u: k(fr, 18, 9))
    for i, x in enumerate((300, 340, 740, 780)):
        s.rect(f"Web (raya {i + 1})", solid(WHITE), lambda fr, u, x=x: (x, 1338, x + 22 * k(fr, 18, 9), 1342))
    for i in range(6):
        x = 470 + i * 30

        def eq(fr, u, i=i, x=x):
            h = 20 + 70 * abs(wave(fr, 9 + 2 * i, 0.17 * i)) * k(fr, 9, 9)
            return x, 1650 - h, x + 18, 1650
        s.rect(f"Barra {i + 1}", solid(WHITE), eq)
    return done(t)


# ======================================================================================================================
# 17. CITY LIFE — letters drop on a purple photo, a red panel falls and turns into a pink roof with circles
# ======================================================================================================================
def city_life():
    D = 5.6
    t = _p("city-life", "Historia: CITY LIFE con panel rosa", "Story: CITY LIFE with a pink panel", 15316, D,
           ["ciudad"])
    s = St(t, D)
    s.pic("Fondo (foto)", "ig3-sneakers-02", geom=lambda fr: (0, 0, 1.1 - 0.06 * k(fr, 0, 90)), label="Foto")
    s.rect("Fondo (tono)", solid("#6A2BE0", 0.42), lambda fr, u: (-10, -10, W + 10, H + 10),
           op=lambda fr, u: 1 - k(fr, 57, 15))
    red = lambda fr: (-10, -10, W + 10, lerp(-10, H + 10, k(fr, 33, 21)))  # noqa: E731
    s.rect("Panel rojo", grad("#FF1F4E", "#FF3A8A", 90), lambda fr, u: red(fr), op=lambda fr, u: 1 - k(fr, 60, 12))
    roof = poly([(0, 14), (50, 0), (100, 14), (100, 100), (0, 100)])
    top = lambda fr: lerp(-1900, 0, k(fr, 57, 18))  # noqa: E731
    s.obj("Techo", solid("#0F2E2C"), lambda fr, u: (540, 1220 + top(fr), 1080, 1500, 0, 1.0 if fr >= 57 else 0.0),
          path=roof, base=(1080, 1500))
    s.obj("Panel", grad("#FF2DA0", "#7B2BF0", 160), lambda fr, u: (540, 1290 + top(fr), 1080, 1380, 0,
                                                                   1.0 if fr >= 57 else 0.0), path=roof,
          base=(1080, 1380))
    move = lambda fr: lerp(0, 610, k(fr, 39, 27))  # noqa: E731
    c = s.word("CITY", (224, 184, 819, 330), SLAB, 400, WHITE, "Título", spacing=0.12,
               geom=lambda fr, u: (0, move(fr), 1, 0, 1))
    s.come(c, 3, stagger=0.08, duration=0.3, preset="drop")
    c = s.word("LIFE", (260, 345, 790, 470), SLAB, 400, WHITE, "Texto", spacing=0.12,
               geom=lambda fr, u: (0, move(fr), 1, 0, 1))
    s.come(c, 9, stagger=0.08, duration=0.3, preset="drop")
    s.word(URL, (360, 1100, 720, 1122), M, 700, WHITE, "Web", spacing=0.2, op=lambda fr, u: k(fr, 57, 9))
    for name, colours, cx, cy, d, at in (("Círculo", ("#FF3D6E", "#8E3BF0"), 539, 1544, 665, 60),
                                         ("Círculo verde", ("#3CC9A0", "#3CC9A0"), 504, 1238, 210, 66),
                                         ("Círculo cian", ("#44C8E8", "#44C8E8"), 644, 1306, 140, 69),
                                         ("Círculo amarillo", ("#FFB020", "#FFB020"), 434, 1360, 56, 72)):
        s.obj(name, grad(*colours, 135), lambda fr, u, cx=cx, cy=cy, d=d, at=at: (
            cx, cy, d * k(fr, at, 12), d * k(fr, at, 12), 0, 1), kind="ellipse", base=(d, d))
    return done(t)


# ======================================================================================================================
# 18. V 6 Your program — a pastel portrait, round bars slide across, a pink ring opens round the boxed title
# ======================================================================================================================
def program():
    D = 5.6
    t = _p("programa", "Historia: V 6 con barras redondas", "Story: V 6 with round bars", 15317, D,
           ["tecnología", "pastel"])
    s = St(t, D)
    s.pic("Fondo (foto)", "ig3-face-03", geom=lambda fr: (0, -200, 1.0 + 0.06 * k(fr, 0, 90)), label="Foto")
    s.rect("Fondo (degradado)", [gradient([(0.0, "#6EE6F0", 0.78), (0.45, "#E9C8F2", 0.72), (1.0, "#FFB6E0", 0.9)],
                                          angle=90), no_stroke()], lambda fr, u: (-10, -10, W + 10, H + 10))
    s.obj("Aro rosa", ring("#FF7AC8", 40), lambda fr, u: (540, 820, lerp(500, 1500, k(fr, 0, 15)),
                                                          lerp(500, 1500, k(fr, 0, 15)), 0, 1 - k(fr, 6, 9)),
          kind="ellipse", base=(1500, 1500))
    bars = (("Barra rosa clara", "#FFC6E6", (-200, 1900), (600, 1600), 380, 3),
            ("Barra magenta", "#FF3EA5", (200, 1950), (1300, 1550), 300, 6),
            ("Barra rosa", "#FF5FA8", (60, 1300), (520, 1130), 42, 9),
            ("Barra morada", "#8B2BF0", (470, 1250), (1150, 1000), 136, 12),
            ("Raya morada", "#3B2A8A", (420, 1800), (1150, 1590), 34, 15),
            ("Raya morada 2", "#7A3AE8", (700, 1170), (1150, 1010), 30, 18))
    for name, colour, p0, p1, th, at in bars:
        ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        cx, cy = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        s.obj(name, solid(colour), lambda fr, u, cx=cx, cy=cy, ln=ln, ang=ang, at=at, th=th: (
            cx + 900 * (1 - k(fr, at, 15)) * math.cos(math.radians(ang)),
            cy + 900 * (1 - k(fr, at, 15)) * math.sin(math.radians(ang)), ln, th, ang, 1),
            radius=th / 2, base=(ln, th))
    s.obj("Caja", ring("#4A3F55", 6), lambda fr, u: (578, 662, 490 * k(fr, 18, 12), 300, 0, 1), radius=30,
          base=(490, 300))
    s.word("V 6", (400, 560, 756, 700), M, 900, "#2E2A3A", "Título",
           geom=lambda fr, u: (0, -120 * (1 - k(fr, 3, 12)), 1, 0, k(fr, 3, 6)))
    s.word("Your program", (410, 728, 746, 766), M, 800, "#2E2A3A", "Texto",
           geom=lambda fr, u: (0, -80 * (1 - k(fr, 6, 12)), 1, 0, k(fr, 6, 6)))
    c = s.word("YOUR COMPANY", (870, 225, 1190, 255), M, 800, "#2E2A3A", "Texto 2", rot=lambda fr, u: -90)
    s.come(c, 24, stagger=0.04, duration=0.2)
    return done(t)


# ======================================================================================================================
# 19. Media Social — a TV photo turns in with a script word, then closes into a circle on white with turning arcs
# ======================================================================================================================
def tv():
    D = 5.6
    t = _p("tv", "Historia: Media Social con foto en círculo", "Story: Media Social with a round photo", 15318, D,
           ["redes", "círculo"])
    s = St(t, D)
    s.ground(WHITE, "Fondo")
    c = lambda fr: k(fr, 42, 15)  # noqa: E731  the photo closes into the circle
    ph = s.pic("Foto", "ig3-tv-01", geom=lambda fr: (0, lerp(0, -600, c(fr)), lerp(1.3 - 0.3 * k(fr, 0, 18), 0.9, c(fr))),
               rot=lambda fr: -22 * (1 - k(fr, 0, 18)))
    s.window(ph, "Foto (círculo)", lambda fr, u: (540, lerp(960, 838, c(fr)), lerp(2400, 727, c(fr)),
                                                  lerp(2400, 727, c(fr)), 0, 1), base=(2400, 2400))
    for i, (d, a0, a1, speed) in enumerate(((860, 200, 330, 1.4), (800, 60, 120, -1.0))):
        s.obj(f"Arco {i + 1}", ring("#8A8A8A", 5), lambda fr, u, d=d, speed=speed: (
            540, 838, d, d, speed * fr * 2, k(fr, 54, 9)), path=arc(a0, a1))
    s.word("Your Brand", (208, 0, 868, 0), COOKIE, 400, "#3A3A3A", "Título",
           geom=lambda fr, u: (-500 * (1 - k(fr, 3, 21)), lerp(415, 1545, c(fr)), lerp(1.0, 0.9, c(fr)),
                               -14 * (1 - k(fr, 3, 21)), k(fr, 3, 9)))
    m = s.word("Media Social", (104, 310, 976, 495), VIBES, 400, "#2A2A2A", "Texto")
    s.come(m, 54, stagger=0.06, duration=0.25)
    s.word(URL, (360, 1655, 720, 1675), M, 700, "#8A8A8A", "Web", spacing=0.2, op=lambda fr, u: k(fr, 66, 9))
    return done(t)


# ======================================================================================================================
# 20. TOYS — a flamingo float, a pale TOYS rises, a white veil and a gradient disc that takes the word
# ======================================================================================================================
def toys():
    D = 5.8
    t = _p("toys", "Historia: TOYS con disco degradado", "Story: TOYS with a gradient disc", 15319, D,
           ["juguetes", "círculo"])
    s = St(t, D)
    z = lambda fr: k(fr, 45, 18)  # noqa: E731
    s.pic("Fondo (foto)", "ig3-flamingo-02", geom=lambda fr: (0, lerp(0, 120, z(fr)), lerp(1.35, 1.1, z(fr))),
          label="Foto")
    s.rect("Velo", solid(WHITE, 0.55), lambda fr, u: (-10, -10, W + 10, H + 10), op=lambda fr, u: z(fr))
    g = lambda fr: k(fr, 54, 15)  # noqa: E731
    s.obj("Aro", solid("#BFF2F2"), lambda fr, u: (540, 935, 980 * g(fr), 980 * g(fr), 0, 0.9), kind="ellipse",
          base=(980, 980))
    s.obj("Disco", grad("#9B1FF0", "#FF1A3A", 90), lambda fr, u: (540, 935, 695 * g(fr), 695 * g(fr), 0, 1),
          kind="ellipse", base=(695, 695))
    mv = lambda fr: k(fr, 48, 15)  # noqa: E731
    s.word("TOYS", (180, 1557, 900, 1775), M, 900, "#CFF3F5", "Texto grande",
           geom=lambda fr, u: (0, 260 * (1 - k(fr, 18, 15)) - 600 * mv(fr), 1, 0, k(fr, 18, 9) * (1 - mv(fr))))
    s.word("TOYS", (290, 870, 790, 1000), M, 900, WHITE, "Título",
           geom=lambda fr, u: (0, 0, lerp(0.6, 1.0, g(fr)), 0, k(fr, 57, 6)))
    s.word("Your Brand", (330, 1380, 750, 1490), COOKIE, 400, "#6A6A6A", "Texto", op=lambda fr, u: k(fr, 63, 9))
    s.word("www.yoursite.com", (310, 1515, 770, 1560), M, 500, "#4A4A4A", "Web", op=lambda fr, u: k(fr, 66, 9))
    return done(t)


# ======================================================================================================================
# Profiles: five cards with an avatar, the camera icon and a name in script
# ======================================================================================================================
def avatar(s, sample, cx, cy, d, at, ring_w=12, ring_c=WHITE, n=9, move=None, label="Tu foto"):
    mv = move or (lambda fr: (0.0, 0.0))
    p = lambda fr: k(fr, at, n)  # noqa: E731
    if ring_w:
        s.obj("Avatar (aro)", solid(ring_c), lambda fr, u: (cx + mv(fr)[0], cy + mv(fr)[1], (d + 2 * ring_w) * p(fr),
                                                            (d + 2 * ring_w) * p(fr), 0, 1), kind="ellipse",
              base=(d + 2 * ring_w,) * 2)
    ph = s.pic("Avatar", sample, box=(cx - d / 2, cy - d / 2, cx + d / 2, cy + d / 2),
               geom=lambda fr: (mv(fr)[0], mv(fr)[1], 1.0), label=label)
    s.window(ph, "Avatar (círculo)", lambda fr, u: (cx + mv(fr)[0], cy + mv(fr)[1], d * p(fr), d * p(fr), 0, 1),
             base=(d, d))
    return ph


def dot(s, name, colour, cx, cy, d, at, alpha=1.0, move=None):
    mv = move or (lambda fr: (0.0, 0.0))
    s.obj(name, solid(colour, alpha), lambda fr, u: (cx + mv(fr)[0], cy + mv(fr)[1], d * k(fr, at, 12),
                                                     d * k(fr, at, 12), 0, 1), kind="ellipse", base=(d, d))


def profile_red():
    D = 5.6
    t = _p("perfil-rojo", "Perfil: tarjeta roja con avatar", "Profile: red card with an avatar", 15320, D,
           ["perfil"])
    s = St(t, D)
    s.ground("#2ED3E6", "Fondo")
    g = lambda fr: k(fr, 0, 18)  # noqa: E731
    s.obj("Fondo rojo", solid("#FF3B2F"), lambda fr, u: (548, 953, 2600 * g(fr), 2600 * g(fr), 0, 1), kind="ellipse",
          base=(2600, 2600))
    for i in range(9):
        d = 600 + 230 * i
        s.obj(f"Anillo {i + 1}", ring("#D92A20", 10), lambda fr, u, d=d: (548, 953, d * (1 + 0.04 * fr / (D * FPS)),
                                                                        d * (1 + 0.04 * fr / (D * FPS)), 0,
                                                                        0.5 * k(fr, 12, 12)), kind="ellipse",
              base=(d, d))
    s.cam("Ícono", lambda fr: (548, 756, k(fr, 9, 9), k(fr, 9, 6)), 160, "#38D1E3")
    s.word("Your Name", (190, 870, 910, 1000), COOKIE, 400, "#38D1E3", "Título",
           geom=lambda fr, u: (0, 260 * (1 - k(fr, 0, 15)), 1, 0, 1))
    s.word(URL, (390, 1020, 690, 1040), M, 600, "#38D1E3", "Web", spacing=0.2, op=lambda fr, u: k(fr, 15, 9))
    dot(s, "Círculo verde", "#2DB38C", 395, 1290, 420, 12)
    dot(s, "Círculo cian", "#4FD8EC", 745, 1400, 330, 15, 0.92)
    dot(s, "Círculo amarillo", "#FFB91F", 511, 1545, 130, 18)
    avatar(s, "portrait-02", 570, 1315, 400, 15)
    return done(t)


def profile_coral():
    D = 5.6
    t = _p("perfil-coral", "Perfil: tarjeta coral con manchas", "Profile: coral card with blobs", 15321, D, ["perfil"])
    s = St(t, D)
    s.ground("#F2564B", "Fondo")
    s.obj("Mancha morada", solid("#9B3FC9", 0.85), lambda fr, u: (lerp(-700, 60, k(fr, 21, 15)), 700, 1300, 1300, 0, 1),
          kind="ellipse")
    s.obj("Mancha cian", solid("#22B8E6"), lambda fr, u: (lerp(1800, 1080, k(fr, 24, 15)), 1500, 1400, 1400, 0, 1),
          kind="ellipse")
    s.obj("Mancha morada 2", solid("#9B3FC9", 0.7), lambda fr, u: (lerp(-400, 200, k(fr, 27, 15)), 1500, 360, 360, 0, 1),
          kind="ellipse")
    s.rect("Línea", solid(WHITE, 0.6), lambda fr, u: (539, 700, 541, 700 + 1220 * k(fr, 18, 21)))
    s.cam("Ícono", lambda fr: (548, 1341, k(fr, 21, 9), k(fr, 21, 6)), 160, WHITE)
    s.word("Your Name", (200, 1510, 900, 1650), COOKIE, 400, WHITE, "Título",
           geom=lambda fr, u: (0, -480 * (1 - k(fr, 6, 18)), 1, 0, k(fr, 0, 6)))
    avatar(s, "portrait-04", 548, 805, 690, 15, ring_w=10)
    return done(t)


def profile_yellow():
    D = 5.6
    t = _p("perfil-amarillo", "Perfil: tarjeta amarilla con foto", "Profile: yellow card with a photo", 15322, D,
           ["perfil"])
    s = St(t, D)
    s.ground("#FFC81E", "Fondo")
    drop = lambda fr: -1300 * (1 - k(fr, 0, 15))  # noqa: E731
    curve = [(0, 0), (100, 0), (100, 86)] + [(100 - 5 * i, 86 + 14 * math.sin(math.pi * i / 20)) for i in range(21)]
    ph = s.pic("Foto", "portrait-06", box=(0, 0, W, 1080), geom=lambda fr: (0, drop(fr), 1.0))
    s.window(ph, "Foto (ventana)", lambda fr, u: (540, 540 + drop(fr), 1080, 1080, 0, 1), path=poly(curve),
             base=(1080, 1080))
    s.obj("Borde", ring(WHITE, 8), lambda fr, u: (540, 540 + drop(fr), 1080, 1080, 0, 1),
          path="M 100 86 " + " ".join(f"L {100 - 5 * i:.1f} {86 + 14 * math.sin(math.pi * i / 20):.2f}"
                                      for i in range(1, 21)), base=(1080, 1080))
    s.word("Your Name", (300, 1195, 780, 1290), COOKIE, 400, "#1A1A1A", "Título",
           geom=lambda fr, u: (0, 300 * (1 - k(fr, 12, 18)), 1, 0, k(fr, 12, 6)))
    s.cam("Ícono", lambda fr: (540, 1405 + 300 * (1 - k(fr, 18, 18)), 1, k(fr, 18, 6)), 170, "#1A1A1A", width=16)
    s.word("LUISA MARTINEZ", (150, 1595, 930, 1640), M, 700, "#1A1A1A", "Texto", spacing=0.3,
           geom=lambda fr, u: (0, 300 * (1 - k(fr, 24, 18)), 1, 0, k(fr, 24, 6)))
    return done(t)


def profile_dark():
    D = 5.6
    t = _p("perfil-oscuro", "Perfil: tarjeta oscura con nombre rojo", "Profile: dark card with a red name", 15323, D,
           ["perfil"])
    s = St(t, D)
    s.ground("#17161E", "Fondo")
    up = lambda fr: k(fr, 54, 15)  # noqa: E731
    avatar(s, "portrait-03", 548, 990, 548, 0, ring_w=8, ring_c="#E9E2DA", move=lambda fr: (0, -432 * up(fr)))
    s.word("ERICA MARTINEZ", (240, 925, 840, 955), M, 700, WHITE, "Texto", spacing=0.3,
           geom=lambda fr, u: (0, 300 * (1 - k(fr, 57, 15)), 1, 0, k(fr, 57, 6)))
    s.word("Your Name", (130, 1030, 950, 1190), COOKIE, 400, "#E8231E", "Título",
           geom=lambda fr, u: (0, 400 * (1 - k(fr, 54, 15)), 1, 0, k(fr, 54, 6)))
    s.cam("Ícono", lambda fr: (lerp(1000, 971, k(fr, 57, 21)), lerp(1500, 141, k(fr, 57, 21)), 1, k(fr, 57, 6)), 110,
          WHITE)
    return done(t)


def profile_gradient():
    D = 5.6
    t = _p("perfil-degradado", "Perfil: tarjeta degradada con círculos", "Profile: gradient card with circles", 15324,
           D, ["perfil"])
    s = St(t, D)
    s.ground("#7A6CF2", "Fondo", layers=grad("#B44DEF", "#3E8EF5", 120))
    up = lambda fr: (0, -300 * (1 - k(fr, 6, 24)))  # noqa: E731
    mv = lambda fr: (0, 300 * (1 - k(fr, 6, 24)))  # noqa: E731
    dot(s, "Círculo verde", "#2EB88A", 438, 741, 510, 0, move=mv)
    dot(s, "Círculo cian", "#5AD2E8", 730, 882, 440, 3, 0.8, move=mv)
    dot(s, "Círculo amarillo", "#FFAE1A", 328, 1130, 160, 6, move=mv)
    del up
    s.obj("Avatar (aro fino)", ring(WHITE, 5), lambda fr, u: (548, 953 + mv(fr)[1], 490 * k(fr, 3, 12),
                                                              490 * k(fr, 3, 12), 0, 1), kind="ellipse",
          base=(490, 490))
    avatar(s, "portrait-07", 548, 953, 430, 3, ring_w=0, move=mv)
    s.cam("Ícono", lambda fr: (548, 1260, k(fr, 33, 9), k(fr, 33, 6)), 100, WHITE)
    s.word("Your Name", (240, 1400, 840, 1540), COOKIE, 400, WHITE, "Título",
           geom=lambda fr, u: (0, 80 * (1 - k(fr, 36, 12)), 1, 0, k(fr, 36, 6)))
    c = s.word("JESSICA", (255, 450, 825, 512), M, 600, WHITE, "Texto", spacing=0.35)
    s.come(c, 45, stagger=0.05, duration=0.25, preset="rise")
    c = s.word("BROWN", (310, 568, 770, 630), M, 600, WHITE, "Texto 2", spacing=0.35)
    s.come(c, 54, stagger=0.05, duration=0.25, preset="rise")
    return done(t)


# ======================================================================================================================
# 26. Dynamic opener — a square post: STO/RY/TIME blocks, STYLE, FAST, Dynamic, Kinetic, BIG, Typo, a script word
# ======================================================================================================================
def opener():
    D = 9.0
    t = _p("opener", "Opener dinámico para publicación cuadrada", "Dynamic opener for a square post", 15325, D,
           ["opener", "tipografía", "publicación"], thumb=1.4, size="square")
    s = St(t, D, 1080, 1080)
    S0 = 1080
    on = lambda a, b: (lambda fr: 1.0 if a <= fr < b else 0.0)  # noqa: E731
    s.ground("#141414", "Fondo")
    # scene 1 (0–48): the lips photo, three white blocks with the word cut out of them
    s.pic("Foto 1", "ig3-lips-02", geom=lambda fr: (0, 0, 1.1 + 0.08 * k(fr, 0, 48)), op=on(0, 54))
    climb = lambda fr: -150 * k(fr, 36, 15)  # noqa: E731
    for i, (txt, x1, y0, y1, at) in enumerate((("STO", 700, 180, 420, 0), ("RY", 520, 440, 625, 1),
                                               ("TIME", 1020, 640, 880, 2))):
        jig = lambda fr, at=at: (60 * math.sin(fr * 2.1) * (1 - k(fr, at, 9)))  # noqa: E731
        box = s.rect(f"Bloque {i + 1}", solid(WHITE), lambda fr, u, x1=x1, y0=y0, y1=y1, at=at, jig=jig: (
            180 + jig(fr), y0 + climb(fr), 180 + (x1 - 180) * k(fr, at, 6) + jig(fr), y1 + climb(fr)),
            op=lambda fr, u: on(0, 48)(fr))
        cut = s.word(txt, (205, y0 + 22, x1 - 22, y1 - 22), M, 900, "#2A0E10", ["Título", "Título 2", "Título 3"][i],
                     align="left", geom=lambda fr, u, at=at, jig=jig: (jig(fr), climb(fr), 1, 0, 1))
        # the word is cut out of its block: the photo shows through the letters
        box["matte"] = {"clip": cut["id"], "mode": "alphaInverted"}
    c = s.word("OPENER", (190, 915, 620, 941), M, 600, WHITE, "Texto", spacing=0.8, align="left",
               geom=lambda fr, u: (0, climb(fr), 1, 0, on(0, 48)(fr)))
    s.come(c, 27, stagger=0.05, duration=0.2)
    # scene 2 (48–93): blue smoke slides in; a white band with STYLE
    s.pic("Foto 2", "ig3-ink-02", geom=lambda fr: (S0 * (1 - k(fr, 48, 6)), 0, 1.1 + 0.1 * k(fr, 48, 50)),
          op=on(48, 123))
    s.rect("Banda", solid(WHITE), lambda fr, u: (-10, 360, -10 + 1100 * k(fr, 72, 6), 700), op=lambda fr, u: on(72, 96)(fr))
    c = s.word("STYLE", (40, 470, 1040, 590), M, 800, "#3A4FD0", "Texto 2", spacing=0.55, op=lambda fr, u: on(72, 96)(fr))
    s.come(c, 75, stagger=0.03, duration=0.12)
    # scene 3 (96–117): a black band with FAST
    s.rect("Banda negra", solid(BLACK, 0.88), lambda fr, u: (-10, 360, W + 10, 700), op=lambda fr, u: on(96, 120)(fr))
    c = s.word("FAST", (40, 470, 1040, 590), M, 800, WHITE, "Texto 3", spacing=0.6, op=lambda fr, u: on(96, 120)(fr))
    s.come(c, 96, stagger=0.15, duration=0.08)
    # scene 4 (120–162): the sunglasses photo slides in from the right; scene 5 (162–180): Dynamic on red
    s.pic("Foto 3", "ig3-sunglasses-02", geom=lambda fr: (S0 * (1 - k(fr, 120, 6)), -80 * k(fr, 120, 42), 1.15),
          op=on(120, 180))
    c = s.word("STORIES", (40, 30, 440, 70), M, 800, WHITE, "Texto 4", spacing=0.3, align="left",
               op=lambda fr, u: on(126, 162)(fr))
    s.come(c, 126, stagger=0.06, duration=0.12)
    s.rect("Rojo", solid("#F2321E", 0.9), lambda fr, u: (-10, -10, W + 10, lerp(-10, 760, k(fr, 159, 6))),
           op=lambda fr, u: on(159, 180)(fr))
    ride = lambda fr: -260 * k(fr, 162, 18)  # noqa: E731
    s.rect("Caja Dynamic", solid(WHITE), lambda fr, u: (-10, 420 + ride(fr), 800, 590 + ride(fr)),
           op=lambda fr, u: on(162, 180)(fr))
    s.word("Dynamic", (20, 440, 780, 570), M, 800, "#141414", "Texto 5", align="left",
           geom=lambda fr, u: (0, ride(fr), 1, 0, on(162, 180)(fr)))
    s.rect("Banda Dynamic", solid(WHITE), lambda fr, u: (-10, 640 + ride(fr), W + 10, 730 + ride(fr)),
           op=lambda fr, u: on(162, 180)(fr))
    s.word("STORIES", (20, 655, 420, 715), M, 800, "#141414", "Texto 6", align="left",
           geom=lambda fr, u: (0, ride(fr), 1, 0, on(162, 180)(fr)))
    # scene 6 (180–228): the TV photo; Kinetic, a typed word in a band, BIG, Typo
    s.pic("Foto 4", "ig3-tv-03", geom=lambda fr: (0, -150 - 80 * k(fr, 180, 45), 1.5), op=on(180, 228))
    s.word("Kinetic", (40, 40, 900, 230), M, 800, "#2A2A2A", "Texto 7", align="left",
           geom=lambda fr, u: (0, -220 * (1 - k(fr, 180, 6)), 1, 0, on(180, 192)(fr)))
    s.rect("Banda 2", solid(WHITE), lambda fr, u: (-10, 40, W + 10, 230), op=lambda fr, u: on(192, 213)(fr))
    c = s.word("CREATIVE", (40, 100, 1040, 170), M, 800, "#2A2A2A", "Texto 8", spacing=0.25,
               op=lambda fr, u: on(192, 213)(fr))
    s.come(c, 192, stagger=0.06, duration=0.05)
    s.rect("Caja BIG", solid(BLACK), lambda fr, u: (300, 30 - 200 * (1 - k(fr, 213, 4)), 800,
                                                    370 - 200 * (1 - k(fr, 213, 4))), op=lambda fr, u: on(213, 225)(fr))
    s.word("BIG", (360, 120, 740, 280), M, 800, WHITE, "Texto 9",
           geom=lambda fr, u: (0, -200 * (1 - k(fr, 213, 4)), 1, 0, on(213, 225)(fr)))
    s.rect("Caja Typo", solid(WHITE), lambda fr, u: (120, 60, 1000, 290), op=lambda fr, u: on(225, 228)(fr))
    s.word("Typo", (170, 90, 950, 260), M, 800, BLACK, "Texto 10", spacing=0.3, op=lambda fr, u: on(225, 228)(fr))
    # scene 7 (228–): the violin; the script word rises
    s.pic("Foto 5", "ig3-violin-01", geom=lambda fr: (0, 0, 1.2 - 0.1 * k(fr, 228, 40)), op=on(228, 999))
    s.word("Your Brand", (120, 0, 960, 0), COOKIE, 400, WHITE, "Texto 11",
           geom=lambda fr, u: (0, lerp(900, 560, k(fr, 228, 30)), 1, -6 * (1 - k(fr, 228, 30)), on(228, 999)(fr)))
    for i, (x, y, at) in enumerate(((250, 160, 0), (760, 420, 30), (520, 840, 60), (900, 220, 120), (180, 700, 180))):
        s.obj(f"Cruz {i + 1}", solid(WHITE, 0.85), lambda fr, u, x=x, y=y, at=at: (x + 0.4 * fr, y, 40, 4, 0,
                                                                                   k(fr, at, 6)))
        s.obj(f"Cruz {i + 1} (b)", solid(WHITE, 0.85), lambda fr, u, x=x, y=y, at=at: (x + 0.4 * fr, y, 4, 40, 0,
                                                                                       k(fr, at, 6)))
    return done(t, keep=("Fondo", "Foto"))


TEMPLATES = [arte, full, fashion, your_life, science, mind, introducing, new, tech, sport, friend, promo, portfolio,
             food, models, music, city_life, program, tv, toys, profile_red, profile_coral, profile_yellow,
             profile_dark, profile_gradient, opener]
