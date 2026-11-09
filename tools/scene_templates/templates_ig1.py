"""INSTAGRAM folder video 1 as Stock templates (ig1-*). See docs/plan-instagram.md.

21692676.mp4 (1920×1080 at 30 fps, 50 s): a big stories pack shown three stories side by side (screens at x 99 /
673 / 1248, y 30–1052, 575×1022 each). Each of the 30 stories is laid out flat on 1080×1920 (×1.878 from the
reference; `R(col, …)` converts a rect measured on the reference frame) and its moves copied from 10 fps sheets
(sheet index i = reference frame 3·i). Photos are slots; famous names → ordinary names. Kit de Instagram; ids
`ig1-*`, order 15100-. Study notes in tienda/plantillas/estudio-21692676/NOTAS.md.

Each story plays its entrance, holds, and leaves with its entrance backwards at 2.5× speed.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, tall
from llt_motion import frames_of
from scene import effect, gradient, keys, no_stroke
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_f import outline_layers
from templates_tit_h import EXIT, S, fill, ring, rot_pt, shadow
from templates_yp4 import art_except

W, H = 1080, 1920
SC = 1080 / 575
COLX = {"L": 99, "M": 673, "R": 1248}
WHITE, INK = "#FFFFFF", "#141414"
RAL, OUT, MON, PF, KAU, SAT = "Raleway", "Outfit", "Montserrat", "Playfair Display", "Kaushan Script", "Satisfy"
for _w, _f in ((400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"),
               (900, "Black")):
    f6._FILES[(RAL, _w)] = f"fonts.basic/fonts/raleway/Raleway-{_f}.ttf"
    f6._FILES[(MON, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"
    if _w >= 500:
        f6._FILES[(OUT, _w)] = f"fonts.extra/fonts/outfit/Outfit-{_f}.ttf"
for _w, _f in ((400, "Regular"), (700, "Bold"), (900, "Black")):
    f6._FILES[(PF, _w)] = f"fonts.basic/fonts/playfairdisplay/PlayfairDisplay-{_f}.ttf"
f6._FILES[(KAU, 400)] = "fonts.basic/fonts/kaushanscript/KaushanScript-Regular.ttf"
f6._FILES[(SAT, 400)] = "fonts.basic/fonts/satisfy/Satisfy-Regular.ttf"

HEART = ("M 50 96 C 22 76 0 58 0 30 C 0 12 13 0 28 0 C 39 0 46 6 50 15 C 54 6 61 0 72 0 C 87 0 100 12 100 30 "
         "C 100 58 78 76 50 96 Z")
CHEV = "M 0 0 L 50 70 L 100 0"


def R(col, x0, y0, x1, y1):
    """A rect measured on the reference frame (column col) → story px."""
    c = COLX[col]
    return ((x0 - c) * SC, (y0 - 30) * SC, (x1 - c) * SC, (y1 - 30) * SC)


def P(col, x, y):
    return (x - COLX[col]) * SC, (y - 30) * SC


def lerp(a, b, t):
    return a + (b - a) * t


def dur_for(entrance_frames, hold=2.4):
    e = entrance_frames / FPS
    return round(e + hold + e / EXIT, 1)


def grad(c0, c1, angle=90):
    return [gradient([(0.0, c0), (1.0, c1)], angle=angle), no_stroke()]


class Story(S):
    def __init__(self, t, dur):
        S.__init__(self, t, dur)
        self.pivot = (W / 2, H / 2)

    # --- backgrounds and photos -------------------------------------------------------------------------------------
    def bg(self, colour, c1=None, name="Fondo"):
        c = self.rect(name, grad(colour, c1) if c1 else solid(colour), lambda fr, u: (-10, -10, W + 10, H + 10))
        c["layoutRole"] = "backdrop"
        return c

    def pic(self, name, sample, box=(0, 0, W, H), geom=None, matte=None, kind="rectangle", path=None, rot=None,
            op=None, look=None, label=None, reuse=None, matte_clip=None):
        """A photo slot laid out in box (x0, y0, x1, y1); geom(fr, u) = (dx, dy, scale) moves it, rot(fr, u) turns it;
        matte(fr, u) = (cx, cy, w, h, rot, op) is a white shape (kind / path) it shows through (a track matte)."""
        x0, y0, x1, y1 = box
        b = Box(x0, y0, x1 - x0, y1 - y0)
        m = None
        if matte is not None:
            m = self.obj(f"{name} (forma)", solid(WHITE), matte, kind=kind, path=path)
        motion = None
        if geom:
            motion = [(u, (lambda g: {"s": g[2], "dx": g[0], "dy": g[1]})(geom(fr, u)), "linear")
                      for u, fr in self.each()]
        clip = self.t.photo(self.t.track("video", name), sample, 0.0, self.dur, b, motion, label=label, reuse=reuse)
        clip["name"] = name
        if rot:
            clip["rotation"] = keys([(u, round(rot(fr, u), 3), "linear") for u, fr in self.each()])
        if op:
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, op(fr, u))), 4), "linear") for u, fr in self.each()])
        if look:
            clip["effects"] = [dict(e) for e in look]
        if m is not None or matte_clip is not None:
            clip["matte"] = {"clip": (m or matte_clip)["id"], "mode": "alpha"}
        clip["_matte"] = m
        return clip

    def bar(self, name, colour, r, op=None, alpha=1.0, **kw):
        return self.rect(name, solid(colour, alpha), r, op=op, **kw)

    # --- words --------------------------------------------------------------------------------------------------
    def words(self, content, ink, family, weight, colour, name="Título", at=0, n=8, how="fade", dy=40.0,
              align="center", rot=0.0, layers=None, editable=True, extra=None):
        """A line whose ink is ink = (x0, top, x1, bottom); how = fade | rise | type | none from frame at;
        extra(fr) = (dx, dy) moves it as well."""
        x0, y0, x1, y1 = ink
        if rot:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            ln, th = (y1 - y0), (x1 - x0)
            ink = (cx - ln / 2, cy - th / 2, cx + ln / 2, cy + th / 2)
        ex = extra or (lambda fr: (0.0, 0.0))

        def g(fr, u):
            dx, dy0 = ex(fr)
            if how in ("fade", "rise"):
                p = k(fr, at, n)
                return dx, dy0 + (dy * (1 - p) if how == "rise" else 0.0), 1.0, rot, p
            return dx, dy0, 1.0, rot, 1.0
        clip = self.say(content, ink, family, weight, colour, name, align=align, layers=layers, editable=editable)
        if how != "none" or rot or extra:
            self.tmove(clip, g)
        if how == "type":
            self.typed(clip, at, stagger=n / FPS / max(1, len(content)), duration=0.08, preset="fade")
        return clip

    # --- small pieces -------------------------------------------------------------------------------------------
    def chevron(self, cx, cy, at=0, r=124):
        """The round «scroll down» button: a light ring, a darker arc on it and a chevron."""
        op = lambda fr, u: k(fr, at, 8)  # noqa: E731
        self.obj("Botón (aro)", ring("#D8D8D8", 5), lambda fr, u: (cx, cy, r, r, 0, op(fr, u)), kind="ellipse")
        arc = " L ".join(f"{50 + 50 * math.sin(a / 10):.2f} {50 - 50 * math.cos(a / 10):.2f}" for a in range(0, 11))
        self.obj("Botón (arco)", ring("#9A9A9A", 5), lambda fr, u: (cx, cy, r, r, 0, op(fr, u)), path="M " + arc)
        self.obj("Botón (flecha)", ring("#5A5A5A", 5), lambda fr, u: (cx, cy + 3, r * 0.42, r * 0.22, 0, op(fr, u)),
                 path=CHEV)

    def circle05(self, cx, cy, r, colour, at, n=8, off=None, text="05"):
        o = off or (lambda fr: (0.0, 0.0))
        self.obj("Círculo", solid(colour), lambda fr, u: (cx + o(fr)[0], cy + o(fr)[1], 2 * r * k(fr, at, n),
                                                          2 * r * k(fr, at, n), 0, 1.0 if fr > at else 0.0),
                 kind="ellipse", base=(2 * r, 2 * r))
        return self.words(text, (cx - r * 0.5, cy - r * 0.37, cx + r * 0.5, cy + r * 0.37), RAL, 700, WHITE,
                          "Número", at=at + n - 2, n=5, extra=o)

    def polaroid(self, name, sample, cx, cy, w, h, motion, caption, cap_font=RAL, cap_colour="#9A9A9A", label=None,
                 cap_weight=500):
        """A white polaroid card (photo on top, caption below) centred at (cx, cy); motion(fr) = (dx, dy, rot, op)."""
        m = 0.055 * w
        ph = h * 0.78
        pcy = -h / 2 + m + ph / 2  # photo centre below the card centre (card units)
        ccy = -h / 2 + m + ph + (h - m - ph) / 2
        lay = [shadow("#000000", 0, 8, 26, 0.22), fill(WHITE)]

        def card(fr, u):
            dx, dy, r, op = motion(fr)
            return cx + dx, cy + dy, w, h, r, op
        self.obj(f"{name} (marco)", lay, card)

        def at_(off):
            def f(fr):
                dx, dy, r, op = motion(fr)
                x, y = rot_pt(cx + dx, cy + dy + off, r, cx + dx, cy + dy)
                return x, y, r, op
            return f
        pp = at_(pcy)
        pw = w - 2 * m
        box = (cx - pw / 2, cy + pcy - ph / 2, cx + pw / 2, cy + pcy + ph / 2)
        clip = self.pic(name, sample, box, geom=lambda fr, u: (pp(fr)[0] - cx, pp(fr)[1] - (cy + pcy), 1.0),
                        rot=lambda fr, u: pp(fr)[2], op=lambda fr, u: pp(fr)[3], label=label)
        cp = at_(ccy)
        cw = w * 0.62
        ink = (cx - cw / 2, cy + ccy - 0.035 * h, cx + cw / 2, cy + ccy + 0.035 * h)
        c = self.say(caption, ink, cap_font, cap_weight, cap_colour, f"{name} (texto)")
        self.tmove(c, lambda fr, u: (cp(fr)[0] - cx, cp(fr)[1] - (cy + ccy), 1.0, cp(fr)[2], cp(fr)[3]))
        return clip


def _p(id, es, en, order, dur, tags=(), thumb=None):
    return tall(f"ig1-{id}", es, en, "instagram", dur, order=order,
                tags=["instagram", "historia", "reels"] + list(tags),
                thumb_at=thumb if thumb is not None else round(dur * 0.5, 1))


def story(id, es, en, order, entrance, tags=(), hold=2.4):
    D = dur_for(entrance, hold)
    t = _p(id, es, en, order, D, tags)
    return t, Story(t, D)


def finish(t):
    return art_except(t, keep=("Fondo", "Foto de fondo", "Velo"))


def BW(contrast=0.1, brightness=0.0):
    return [effect("color.basic", saturation=-1.0, contrast=contrast, brightness=brightness)]


def DARK(b=-0.25, sat=0.0):
    return [effect("color.basic", brightness=b, saturation=sat)]


def zoom(a, b, at, n):
    return lambda fr, u: (0.0, 0.0, lerp(a, b, k(fr, at, n)))


# ==================================================================================================================
# 1. #AMAZING NEON CITY: the city at night, the hashtag types, the neon letters flicker on
def neon():
    t, s = story("neon", "Historia: NEON CITY en neón turquesa", "Story: NEON CITY in teal neon", 15100, 54,
                 ["neón", "ciudad", "noche"])
    s.pic("Foto de fondo", "fx-citynight-02", geom=zoom(1.12, 1.0, 0, 90), look=DARK(-0.15, -0.2), label="Tu foto")
    s.bar("Velo", "#2A1640", lambda fr, u: (-10, -10, W + 10, H + 10), alpha=0.35)
    s.words("#AMAZING", R("L", 268, 388, 505, 418), MON, 400, WHITE, "Texto", at=12, n=24, how="type")

    def flick(fr, u):
        seq = [(6, 0.0), (8, 0.35), (12, 0.2), (15, 0.9), (17, 0.3), (19, 1.0), (21, 0.55), (23, 1.0)]
        v = 0.0
        for f, o in seq:
            if fr >= f:
                v = o
        return v
    for i, (word, ink) in enumerate((("NEON", R("L", 222, 447, 550, 535)), ("CITY", R("L", 252, 552, 520, 635)))):
        c = s.say(word, ink, MON, 700, "#3BE8D8", "Título" if i == 0 else "Título 2",
                  layers=outline_layers("#3BE8D8", 5))
        s.tmove(c, lambda fr, u: (0, 0, 1, 0, flick(fr, u)))
        s.fx(c, "layer.outer_glow", color="#1FD6C8", size=26, spread=0.25, opacity=0.9)
    return finish(t)


# 2. #beautiful: the photo drops from the top, the green 05 pops on its edge, the lines fade in one after another
def beautiful():
    t, s = story("beautiful", "Historia: #beautiful con foto arriba y cita", "Story: #beautiful with photo and quote",
                 15101, 40, ["cita", "foto"])
    s.bg("#FFFFFF")
    top = R("M", 673, 30, 1248, 645)
    hh = top[3]
    s.pic("Foto", "y6-flatlay-03", top, geom=lambda fr, u: (0, -hh * (1 - k(fr, 0, 14)), 1.0))
    cx, cy = P("M", 960, 645)
    s.circle05(cx, cy, 45 * SC, "#4CAE8C", 12)
    s.words("#beautiful", R("M", 798, 728, 1128, 775), RAL, 700, INK, "Título", at=15, n=8)
    s.words("All you", R("M", 893, 820, 1028, 855), RAL, 500, INK, "Texto", at=21, n=8)
    s.words("need is love.", R("M", 837, 868, 1085, 905), RAL, 500, INK, "Texto 2", at=26, n=8)
    s.words("Laura Bennett", R("M", 880, 962, 1042, 984), RAL, 600, "#B4B4B4", "Autor", at=32, n=8)
    return finish(t)


# 3. WE MUST BELIEVE: the dancer fades in on black, a white line splits round the words, the words rise one by one
def believe():
    t, s = story("believe", "Historia: WE MUST BELIEVE con línea partida", "Story: WE MUST BELIEVE with a split line",
                 15102, 66, ["frase", "foto", "negro"])
    s.bg("#0C0B12")
    s.pic("Foto", "fx-dancer-02", op=lambda fr, u: k(fr, 0, 15), look=DARK(-0.1))
    lx = P("R", 1535, 0)[0]
    th = 9 * SC
    gt, gb = P("R", 0, 285)[1], P("R", 0, 795)[1]
    s.bar("Línea", WHITE, lambda fr, u: (lx - th / 2, -10, lx + th / 2, gt * k(fr, 15, 15)))
    s.bar("Línea 2", WHITE, lambda fr, u: (lx - th / 2, H - (H - gb) * k(fr, 15, 15), lx + th / 2, H + 10))
    s.words("WE", R("R", 1468, 425, 1600, 488), OUT, 800, WHITE, "Título", at=42, n=9, how="rise")
    s.words("MUST", R("R", 1440, 503, 1630, 566), OUT, 800, WHITE, "Título 2", at=50, n=9, how="rise")
    s.words("BELIEVE", R("R", 1412, 581, 1658, 644), OUT, 800, WHITE, "Título 3", at=57, n=9, how="rise")
    return finish(t)


# 4. Love is friendship: two polaroids fly in on pink, the words write themselves underneath
def love_friendship():
    t, s = story("love-friendship", "Historia: polaroids y «Love is friendship» manuscrito",
                 "Story: polaroids and handwritten «Love is friendship»", 15103, 112, ["polaroid", "rosa", "cita"])
    s.bg("#F7D0CB")
    cw, ch = 480 * SC, 560 * SC
    s.polaroid("Foto 1", "y6-flatlay-05", *P("L", 395, 392), cw, ch,
               lambda fr: (-700 * (1 - k(fr, 9, 14)), 900 * (1 - k(fr, 9, 14)), 14 - 50 * (1 - k(fr, 9, 14)),
                           1.0 if fr > 9 else 0.0), "#instagood", label="Foto 1")
    s.polaroid("Foto 2", "portrait-03", *P("L", 386, 390), cw, ch,
               lambda fr: (-900 * (1 - k(fr, 54, 16)), 300 * (1 - k(fr, 54, 16)), 2 - 35 * (1 - k(fr, 54, 16)),
                           1.0 if fr > 54 else 0.0), "#photooftheday", label="Foto 2")
    rose = "#C28E8A"
    s.words("Love is", R("L", 250, 690, 510, 760), KAU, 400, rose, "Texto", at=70, n=14, how="type", rot=0)
    s.words("friendship", R("L", 185, 780, 590, 870), KAU, 400, rose, "Texto 2", at=84, n=22, how="type")
    s.words("set on fire", R("L", 205, 885, 590, 965), KAU, 400, rose, "Texto 3", at=100, n=18, how="type")
    return finish(t)


# 5. Conquer from within: titles fade in, a strip of photos slides left twice, the photography button
def conquer():
    t, s = story("conquer", "Historia: Conquer from within con carrusel de fotos",
                 "Story: Conquer from within with a photo carousel", 15104, 114, ["carrusel", "foto", "blanco"])
    s.bg("#FFFFFF")
    s.words("#repost", R("M", 900, 125, 1020, 150), RAL, 600, "#9A9A9A", "Texto", at=21, n=14, how="type")
    s.words("Conquer", R("M", 850, 170, 1068, 212), RAL, 700, INK, "Título", at=4, n=8)
    s.words("from within", R("M", 815, 232, 1100, 275), RAL, 700, INK, "Título 2", at=21, n=8)
    y0, y1 = P("M", 0, 342)[1], P("M", 0, 740)[1]
    tw, gap = 400 * SC, 12 * SC
    x_first = P("M", 838, 0)[0]
    shift = lambda fr: (tw + gap) * (k(fr, 9, 15) + k(fr, 96, 15))  # noqa: E731
    for i, smp in enumerate(("fx-woman-05", "fx-fashion-03", "fx-woman-07", "fx-fashion-05")):
        x = x_first + (i - 1) * (tw + gap)
        s.pic(f"Foto {i + 1}", smp, (x, y0, x + tw, y1), geom=lambda fr, u: (-shift(fr), 0, 1.0),
              look=BW() if i == 0 else None, label=f"Foto {i + 1}")
    bx0, by0, bx1, by1 = R("M", 788, 835, 1133, 960)
    op = lambda fr, u: k(fr, 0, 6)  # noqa: E731
    s.obj("Botón", ring("#A8A8A8", 7), lambda fr, u: ((bx0 + bx1) / 2, (by0 + by1) / 2, bx1 - bx0, by1 - by0, 0,
                                                       op(fr, u)))
    s.bar("Botón (sombra)", INK, lambda fr, u: (bx1 - 4, by0, bx1 + 6, by1 + 6), op=op)
    s.bar("Botón (sombra 2)", INK, lambda fr, u: ((bx0 + bx1) / 2 + 30, by1 - 4, bx1 + 6, by1 + 6), op=op)
    s.words("photography", R("M", 828, 875, 1090, 918), RAL, 700, INK, "Botón (texto)", at=0, n=6)
    return finish(t)


# 6. Success quote on rock: «01» between two lines, the quote's lines rise one after another, the author
def success():
    t, s = story("success", "Historia: cita sobre roca con 01", "Story: quote on rock with 01", 15105, 96,
                 ["cita", "frase", "oscuro"])
    s.pic("Foto de fondo", "y5-h-volcano-01", look=BW(0.0, -0.3), label="Tu foto")
    s.words("01", R("R", 1515, 296, 1555, 321), RAL, 700, WHITE, "Número", at=18, n=6)
    lt = 6 * SC
    for i, (a, b) in enumerate(((1350, 1497), (1575, 1720))):
        x0, x1 = P("R", a, 0)[0], P("R", b, 0)[0]
        y = P("R", 0, 309)[1]
        if i == 0:
            s.bar("Línea", WHITE, lambda fr, u, x0=x0, x1=x1, y=y: (x1 - (x1 - x0) * k(fr, 21, 10), y - lt / 2, x1,
                                                                    y + lt / 2))
        else:
            s.bar("Línea 2", WHITE, lambda fr, u, x0=x0, x1=x1, y=y: (x0, y - lt / 2, x0 + (x1 - x0) * k(fr, 21, 10),
                                                                      y + lt / 2))
    lines = [("Success", (1432, 360, 1638, 402)), ("is not the key", (1368, 425, 1702, 468)),
             ("to happiness.", (1368, 488, 1702, 530)), ("Happiness", (1402, 552, 1668, 594)),
             ("is the key", (1418, 615, 1652, 660)), ("to success.", (1396, 680, 1674, 720))]
    for i, (txt, r) in enumerate(lines):
        s.words(txt, R("R", *r), RAL, 700, WHITE, "Cita" if i == 0 else f"Cita {i + 1}", at=30 + 9 * i, n=9,
                how="rise", dy=30)
    s.words("Kate Morgan", R("R", 1457, 770, 1613, 795), RAL, 700, WHITE, "Autor", at=84, n=8)
    for i, (a, b) in enumerate(((1350, 1440), (1632, 1720))):
        x0, x1 = P("R", a, 0)[0], P("R", b, 0)[0]
        y = P("R", 0, 782)[1]
        s.bar(f"Línea {3 + i}", WHITE, lambda fr, u, x0=x0, x1=x1, y=y: (x0, y - lt / 2, x1, y + lt / 2),
              op=lambda fr, u: k(fr, 84, 8))
    return finish(t)


# 7. STYLISH DESIGN: on dark leaves a red-to-purple frame grows from a thin bar, the words fade in over it
def stylish_design():
    t, s = story("stylish-design", "Historia: STYLISH DESIGN en marco degradado",
                 "Story: STYLISH DESIGN in a gradient frame", 15106, 64, ["marco", "degradado", "oscuro"])
    s.pic("Foto de fondo", "fx-nature-02", look=DARK(-0.35), label="Tu foto")
    x0, y0, x1, y1 = R("L", 245, 335, 527, 748)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    th = 10 * SC
    red, purple = "#E2405C", "#8E5CE6"

    def box(fr):
        w = lerp(th * 2, x1 - x0, k(fr, 12, 8))
        h = lerp((y1 - y0) * 0.45, y1 - y0, k(fr, 7, 8))
        return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    op = lambda fr, u: 1.0 if fr > 7 else 0.0  # noqa: E731
    s.bar("Marco (arriba)", red, lambda fr, u: (box(fr)[0], box(fr)[1], box(fr)[2], box(fr)[1] + th), op=op)
    s.bar("Marco (abajo)", purple, lambda fr, u: (box(fr)[0], box(fr)[3] - th, box(fr)[2], box(fr)[3]), op=op)
    s.rect("Marco (izquierda)", grad(red, purple), lambda fr, u: (box(fr)[0], box(fr)[1], box(fr)[0] + th, box(fr)[3]),
           op=op)
    s.rect("Marco (derecha)", grad(red, purple), lambda fr, u: (box(fr)[2] - th, box(fr)[1], box(fr)[2], box(fr)[3]),
           op=op)
    s.words("STYLISH", R("L", 205, 465, 568, 535), OUT, 700, WHITE, "Título", at=18, n=8)
    s.words("DESIGN", R("L", 217, 548, 555, 618), OUT, 700, WHITE, "Título 2", at=24, n=8)
    s.words("#amazing", R("L", 300, 675, 470, 705), OUT, 600, WHITE, "Texto", at=46, n=14, how="type")
    return finish(t)


def mirror_window(s, name, first, matte, veil=0.2, kind="rectangle"):
    """The same photo turned upside down, shown through a shape, under a white veil (the reflection window)."""
    s.pic(name, first["_sample"], geom=lambda fr, u: (0, 0, 1.0), rot=lambda fr, u: 180.0, matte=matte, kind=kind,
          reuse=first["placeholderId"])
    s.obj(f"{name} (velo)", solid(WHITE, veil), matte, kind=kind)


# 8. WE MUST BELIEVE in a circle: a disc with the mirrored landscape grows, the words come one by one
def must_believe():
    t, s = story("must-believe", "Historia: WE MUST BELIEVE en círculo reflejado",
                 "Story: WE MUST BELIEVE in a mirrored circle", 15107, 56, ["frase", "círculo", "paisaje"])
    first = s.pic("Foto de fondo", "nature-02", label="Tu foto")
    cx, cy = P("M", 960, 541)
    r = 212 * SC
    mirror_window(s, "Círculo", first, lambda fr, u: (cx, cy, 2 * r * k(fr, 27, 15), 2 * r * k(fr, 27, 15), 0,
                                                      1.0 if fr > 27 else 0.0), kind="ellipse")
    s.words("WE", R("M", 905, 420, 1012, 475), OUT, 700, "#F2F2F2", "Título", at=36, n=8)
    s.words("MUST", R("M", 868, 505, 1050, 560), OUT, 700, "#F2F2F2", "Título 2", at=41, n=8)
    s.words("BELIEVE", R("M", 832, 590, 1088, 645), OUT, 700, "#DADADA", "Título 3", at=45, n=8)
    s.words("#photooftheday", R("M", 833, 940, 1103, 975), OUT, 700, WHITE, "Texto", at=48, n=8)
    return finish(t)


# 9. Alison Stanley: the photo shrinks into a framed panel while the outside turns red, the name rises
def alison():
    t, s = story("alison", "Historia: nombre sobre foto con marco rojo", "Story: name on a photo with a red frame",
                 15108, 54, ["nombre", "perfil", "rojo"])
    first = s.pic("Foto de fondo", "fx-fashion-04", label="Tu foto")
    s.bar("Velo", "#8A0E18", lambda fr, u: (-10, -10, W + 10, H + 10), op=lambda fr, u: 0.62 * k(fr, 15, 9))
    ix0, iy0, ix1, iy1 = R("R", 1320, 158, 1750, 925)
    icx, icy = (ix0 + ix1) / 2, (iy0 + iy1) / 2
    sc = (ix1 - ix0) / W
    g = lambda fr, u: (lerp(0, icx - W / 2, k(fr, 15, 9)), lerp(0, icy - H / 2, k(fr, 15, 9)),  # noqa: E731
                       lerp(1.0, sc, k(fr, 15, 9)))
    s.pic("Foto", first["_sample"], geom=g, reuse=first["placeholderId"],
          matte=lambda fr, u: (W / 2 + g(fr, u)[0], H / 2 + g(fr, u)[1], W * g(fr, u)[2], H * g(fr, u)[2], 0, 1.0))
    s.rect("Sombra", solid("#140A18", 0.45),
           lambda fr, u: (W / 2 + g(fr, u)[0] - W * g(fr, u)[2] / 2, H / 2 + g(fr, u)[1] + H * g(fr, u)[2] / 6,
                          W / 2 + g(fr, u)[0] + W * g(fr, u)[2] / 2, H / 2 + g(fr, u)[1] + H * g(fr, u)[2] / 2),
           op=lambda fr, u: k(fr, 18, 9))
    s.words("Alison", R("R", 1383, 665, 1688, 740), OUT, 600, WHITE, "Título", at=33, n=9, how="rise")
    s.words("Stanley", R("R", 1350, 765, 1725, 848), OUT, 600, WHITE, "Título 2", at=42, n=9, how="rise")
    s.words("#photooftheday", R("R", 1407, 955, 1678, 990), OUT, 700, WHITE, "Texto", at=21, n=8)
    return finish(t)


# 10. happy thoughts: the colour photo shrinks and tilts into a polaroid over itself in black and white
def happy_thoughts():
    t, s = story("happy-thoughts", "Historia: polaroid inclinada «happy thoughts»",
                 "Story: tilted polaroid «happy thoughts»", 15109, 56, ["polaroid", "boda", "manuscrito"])
    first = s.pic("Foto de fondo", "wedding-01", look=BW(0.05, 0.05), label="Tu foto")
    fcx, fcy = P("L", 388, 540)
    cw, ch, rot = 480 * SC, 560 * SC, 4.0
    m = 0.055 * cw
    ph = ch * 0.78
    pw = cw - 2 * m
    p = lambda fr: k(fr, 18, 18)  # noqa: E731

    def card(fr, u):
        q = p(fr)
        return (lerp(W / 2, fcx, q), lerp(H / 2, fcy, q), lerp(W * 1.3, cw, q), lerp(H * 1.3, ch, q), rot * q, 1.0)
    s.obj("Polaroid", [shadow("#000000", 0, 10, 30, 0.25), fill(WHITE)], card)

    def win(fr, u):
        cx, cy, w, h, r, _ = card(fr, u)
        q = p(fr)
        ww, hh = lerp(W, pw, q), lerp(H, ph, q)
        off = lerp(0, -ch / 2 + m + ph / 2, q)
        x, y = rot_pt(cx, cy + off, r, cx, cy)
        return x, y, ww, hh, r, 1.0
    sc = pw / W
    s.pic("Foto", first["_sample"], geom=lambda fr, u: (win(fr, u)[0] - W / 2, win(fr, u)[1] - H / 2,
                                                        lerp(1.0, sc, p(fr))),
          rot=lambda fr, u: win(fr, u)[4], matte=win, reuse=first["placeholderId"])
    ccy = -ch / 2 + m + ph + (ch - m - ph) / 2
    x, y = rot_pt(fcx, fcy + ccy, rot, fcx, fcy)
    s.words("happy thoughts", (x - cw * 0.36, y - 40, x + cw * 0.36, y + 40), SAT, 400, "#3A3A3A", "Texto",
            at=24, n=26, how="type", rot=0)["rotation"] = keys([(0.0, rot, "hold")])
    return finish(t)


def grid4(s, rects, samples, centre_y, at=0, n=18, stagger=0):
    """Four photos whose windows open up and down from the line y = centre_y (each from its own middle when None)."""
    for i, (r, smp) in enumerate(zip(rects, samples)):
        x0, y0, x1, y1 = r
        mid = (y0 + y1) / 2 if centre_y is None else centre_y

        def m(fr, u, x0=x0, y0=y0, x1=x1, y1=y1, mid=mid, i=i):
            q = k(fr, at + stagger * i, n)
            a, b = lerp(mid, y0, q), lerp(mid, y1, q)
            a, b = max(a, min(mid, y0)), b
            return (x0 + x1) / 2, (a + b) / 2, x1 - x0, max(0.0, b - a), 0, 1.0 if q > 0 else 0.0
        s.pic(f"Foto {i + 1}", smp, r, matte=m, label=f"Foto {i + 1}")


# 11. So it goes: four photos open from two thin strips, the title fades in, a white label types #beautiful
def so_it_goes():
    t, s = story("so-it-goes", "Historia: So it goes con cuadrícula 2×2", "Story: So it goes with a 2×2 grid", 15110,
                 78, ["cuadrícula", "collage", "rosa"])
    s.bg("#FCFBF9")
    rects = [R("M", 687, 188, 952, 533), R("M", 968, 188, 1233, 533), R("M", 687, 548, 952, 893),
             R("M", 968, 548, 1233, 893)]
    grid4(s, rects, ["flowers-01", "fx-woman-02", "flowers-02", "flowers-03"], None, at=2, n=16)
    s.words("So it goes", R("M", 812, 85, 1107, 135), RAL, 700, "#CFCBCB", "Título", at=18, n=8)
    bx0, by0, bx1, by1 = R("M", 800, 477, 1118, 607)
    s.obj("Etiqueta", solid("#FCFBF9"), lambda fr, u: ((bx0 + bx1) / 2, (by0 + by1) / 2, (bx1 - bx0) * k(fr, 45, 6),
                                                      by1 - by0, 0, 1.0 if fr > 45 else 0.0), base=(bx1 - bx0, by1 - by0))
    s.words("#beautiful", R("M", 852, 520, 1068, 560), RAL, 700, INK, "Texto", at=50, n=26, how="type")
    s.chevron(*P("M", 960, 972), at=0)
    return finish(t)


# 12. Catherine Heath: the round photo pops, the name, then the quote rises from its last line up
def catherine():
    t, s = story("catherine", "Historia: foto redonda, nombre y cita en degradado",
                 "Story: round photo, name and quote on a gradient", 15111, 84, ["cita", "perfil", "degradado"])
    s.bg("#9EC4FB", "#D8C3F8")
    cx, cy = P("R", 1535, 217)
    r = 133 * SC
    s.pic("Foto", "portrait-06", (cx - r, cy - r, cx + r, cy + r), kind="ellipse",
          matte=lambda fr, u: (cx, cy, 2 * r * k(fr, 12, 12), 2 * r * k(fr, 12, 12), 0, 1.0 if fr > 12 else 0.0))
    s.words("Catherine Heath", R("R", 1378, 380, 1700, 418), PF, 700, WHITE, "Nombre", at=15, n=8)
    s.words("“", R("R", 1515, 478, 1565, 515), PF, 900, "#9B8CF0", "Comillas", at=45, n=8)
    s.words("”", R("R", 1515, 848, 1565, 885), PF, 900, "#9B8CF0", "Comillas 2", at=48, n=8)
    s.words("set on fire", R("R", 1368, 735, 1712, 800), PF, 900, WHITE, "Cita 3", at=51, n=10, how="rise")
    s.words("friendship", R("R", 1355, 645, 1722, 712), PF, 900, WHITE, "Cita 2", at=63, n=10, how="rise")
    s.words("Love is", R("R", 1422, 560, 1658, 618), PF, 900, WHITE, "Cita", at=74, n=10, how="rise")
    s.words("Jeremy Taylor", R("R", 1452, 948, 1625, 975), PF, 700, "#958AD8", "Autor", at=0, n=8)
    return finish(t)


# 13. Spring Sale 30%: the red box rises from below, «Spring» and «Sale» fade in above it
def spring_sale():
    t, s = story("spring-sale", "Historia: Spring Sale 30%", "Story: Spring Sale 30%", 15112, 70,
                 ["rebajas", "descuento", "moda"])
    s.pic("Foto de fondo", "outfit-03", label="Tu foto")
    up = lambda fr: (0.0, 900 * (1 - k(fr, 0, 21)))  # noqa: E731
    s.bar("Caja", "#E3191C", lambda fr, u: (lambda r: (r[0], r[1] + up(fr)[1], r[2], r[3] + up(fr)[1]))(
        R("L", 157, 555, 515, 715)))
    s.words("30%", R("L", 180, 575, 495, 695), OUT, 700, WHITE, "Descuento", how="none", extra=up)
    s.words("Spring", R("L", 170, 350, 445, 435), OUT, 700, "#1A1A1A", "Título", at=51, n=12, align="left")
    s.words("Sale", R("L", 170, 440, 350, 515), OUT, 700, "#1A1A1A", "Título 2", at=62, n=8, align="left")
    return finish(t)


# 14. #lifestyle: the hashtag types, two columns of photos slide in from opposite ends, a white label behind it
def lifestyle():
    t, s = story("lifestyle", "Historia: #lifestyle con mosaico de fotos", "Story: #lifestyle with a photo mosaic",
                 15113, 84, ["collage", "verano", "mosaico"])
    s.bg("#FFFFFF")
    left = [(30, 188), (208, 472), (490, 755), (772, 1037)]
    right = [(45, 310), (328, 595), (616, 882), (898, 1163)]
    smp = ["summer-01", "beach-02", "food-01", "summer-02", "beach-04", "summer-03", "fx-beach-02", "food-02"]
    n = 0
    for col, rows, sign in (((687, 952), left, 1), ((968, 1233), right, -1)):
        for a, b in rows:
            r = R("M", col[0], a, col[1], b)
            s.pic(f"Foto {n + 1}", smp[n], r, label=f"Foto {n + 1}",
                  geom=lambda fr, u, sign=sign: (0, sign * (2100 * (1 - k(fr, 40, 40)) + 40 * (1 - k(fr, 80, 20))),
                                                 1.0))
            n += 1
    bx0, by0, bx1, by1 = R("M", 800, 450, 1118, 633)
    s.obj("Etiqueta", solid(WHITE), lambda fr, u: ((bx0 + bx1) / 2, (by0 + by1) / 2, bx1 - bx0,
                                                   (by1 - by0) * k(fr, 66, 8), 0, 1.0 if fr > 66 else 0.0),
          base=(bx1 - bx0, by1 - by0))
    s.words("#lifestyle", R("M", 850, 515, 1068, 565), RAL, 700, INK, "Texto", at=3, n=30, how="type")
    return finish(t)


# 15. ELEGANT TYPO DESIGN: the words fade in, a window with the mirrored sea opens and TYPO spreads out
def elegant():
    t, s = story("elegant", "Historia: ELEGANT TYPO DESIGN con ventana reflejada",
                 "Story: ELEGANT TYPO DESIGN with a mirrored window", 15114, 70, ["tipografía", "mar", "elegante"])
    first = s.pic("Foto de fondo", "beach-05", label="Tu foto")
    x0, y0, x1, y1 = R("R", 1322, 328, 1748, 760)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

    def win(fr, u):
        return cx, cy, lerp(8, x1 - x0, k(fr, 48, 12)), (y1 - y0) * k(fr, 40, 8), 0, 1.0 if fr > 40 else 0.0
    mirror_window(s, "Ventana", first, win, veil=0.18)
    s.words("ELEGANT", R("R", 1368, 428, 1702, 475), MON, 600, WHITE, "Título", at=18, n=8)
    c = s.words("TYPO", R("R", 1450, 518, 1622, 565), MON, 600, WHITE, "Título 2", at=21, n=8)
    size = c["textStyle"]["pixelSize"]
    for key, sign in (("x", -1), ("width", 2)):
        for kf in c[key]["keyframes"]:
            kf["value"] += sign * 300
    wide = (322 - 172) / 3 * SC
    c["textStyle"].setdefault("keyframes", {})["letterSpacing"] = keys(
        [(u, round(lerp(size * 0.06, wide, k(fr, 57, 12)), 3), "linear") for u, fr in s.each()])
    s.words("DESIGN", R("R", 1368, 603, 1702, 650), MON, 600, WHITE, "Título 3", at=24, n=8)
    s.words("#photography", R("R", 1420, 935, 1665, 972), OUT, 700, WHITE, "Texto", at=0, n=6)
    return finish(t)


def arrow(s, name, pts, at, n, colour=WHITE, width=10):
    """A hand-drawn arrow: a curve through pts that draws itself and its head."""
    s.outline(name, pts, width, colour, at=at, n=n, closed=False)
    (ax, ay), (bx, by) = pts[-2], pts[-1]
    a = math.atan2(by - ay, bx - ax)
    head = [(bx - 46 * math.cos(a - 0.6), by - 46 * math.sin(a - 0.6)), (bx, by),
            (bx - 46 * math.cos(a + 0.6), by - 46 * math.sin(a + 0.6))]
    s.outline(f"{name} (punta)", head, width, colour, at=at + n - 2, n=5, closed=False)


def curve_pts(p0, c, p1, steps=14):
    return [((1 - q) ** 2 * p0[0] + 2 * (1 - q) * q * c[0] + q * q * p1[0],
             (1 - q) ** 2 * p0[1] + 2 * (1 - q) * q * c[1] + q * q * p1[1]) for q in [i / steps for i in range(steps + 1)]]


# 16. Love loves to love love: two polaroids drop in, white arrows draw round them, the words write themselves
def love_loves():
    t, s = story("love-loves", "Historia: dos polaroids con flechas y frase manuscrita",
                 "Story: two polaroids with arrows and a handwritten line", 15115, 96, ["polaroid", "rosa", "flechas"])
    s.bg("#F7D0CB")
    s.polaroid("Foto 1", "portrait-04", *P("L", 363, 288), 343 * SC, 400 * SC,
               lambda fr: (-600 * (1 - k(fr, 15, 12)), -700 * (1 - k(fr, 15, 12)), -2 - 20 * (1 - k(fr, 15, 12)),
                           1.0 if fr > 15 else 0.0), "#photooftheday", label="Foto 1")
    s.polaroid("Foto 2", "fx-woman-06", *P("L", 420, 582), 376 * SC, 415 * SC,
               lambda fr: (600 * (1 - k(fr, 27, 12)), 800 * (1 - k(fr, 27, 12)), 4 + 25 * (1 - k(fr, 27, 12)),
                           1.0 if fr > 27 else 0.0), "#photooftheday", label="Foto 2")
    arrow(s, "Flecha", curve_pts(P("L", 552, 218), P("L", 630, 270), P("L", 600, 372)), 54, 14)
    arrow(s, "Flecha 2", curve_pts(P("L", 182, 412), P("L", 140, 520), P("L", 215, 598)), 60, 14)
    rose = "#C59A95"
    s.words("Love loves", R("L", 195, 785, 570, 875), KAU, 400, rose, "Texto", at=45, n=20, how="type")
    s.words("to love love", R("L", 182, 885, 600, 980), KAU, 400, rose, "Texto 2", at=66, n=24, how="type")
    return finish(t)


# 17. 40% Sale: the photo panel slides in from the right, the turned 40% and the blue Sale box follow
def forty_sale():
    t, s = story("forty-sale", "Historia: 40% Sale vertical con foto", "Story: vertical 40% Sale with a photo", 15116,
                 54, ["rebajas", "descuento", "moda"])
    s.bg("#FFFFFF")
    pr = R("M", 673, 30, 960, 1052)
    s.pic("Foto", "fashion-03", pr, geom=lambda fr, u: (W * (1 - k(fr, 0, 21)), 0, 1.0))
    sl = lambda fr: (700 * (1 - k(fr, 6, 18)), 0.0)  # noqa: E731
    s.words("40%", R("M", 1015, 180, 1175, 620), OUT, 800, "#111111", "Descuento", how="none", rot=90, extra=sl)
    s.bar("Caja", "#1F3FE3", lambda fr, u: (lambda r: (r[0] + sl(fr)[0], r[1], r[2] + sl(fr)[0], r[3]))(
        R("M", 998, 665, 1190, 757)))
    s.words("Sale", R("M", 1016, 678, 1175, 744), OUT, 700, WHITE, "Título", how="none", extra=sl)
    s.words("only today,", R("M", 1003, 795, 1196, 830), RAL, 600, "#8C8C8C", "Texto", at=36, n=8, align="left")
    s.words("for you", R("M", 1003, 840, 1125, 875), RAL, 600, "#8C8C8C", "Texto 2", at=46, n=8, align="left")
    return finish(t)


# 18. Nature: a white box with the word on dark sea, an outer frame lands round the story, the hashtag
def nature():
    t, s = story("nature", "Historia: Nature en recuadro con marco", "Story: Nature in a box with a frame", 15117, 62,
                 ["naturaleza", "marco", "mar"])
    s.pic("Foto de fondo", "y5-h-ocean-02", look=DARK(-0.1), label="Tu foto")
    th = 5 * SC
    x0, y0, x1, y1 = R("R", 1378, 447, 1692, 562)
    s.obj("Recuadro", ring(WHITE, th), lambda fr, u: ((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 0, k(fr, 0, 6)))
    s.words("Nature", R("R", 1405, 470, 1663, 540), RAL, 700, WHITE, "Título", at=9, n=12)
    X0, Y0, X1, Y1 = R("R", 1272, 52, 1800, 1030)

    def frame(fr, u):
        g = lerp(1.06, 1.0, k(fr, 21, 7))
        return (X0 + X1) / 2, (Y0 + Y1) / 2, (X1 - X0) * g, (Y1 - Y0) * g, 0, k(fr, 21, 5)
    s.obj("Marco", ring(WHITE, th), frame, base=(X1 - X0, Y1 - Y0))
    s.words("#photography", R("R", 1410, 582, 1660, 618), RAL, 500, WHITE, "Texto", at=54, n=8)
    return finish(t)


# 19. #photooftheday card: a white line grows into a tall card, a window opens in it from the middle, the hashtag types
def photo_frame():
    t, s = story("photo-frame", "Historia: tarjeta blanca que abre una ventana", "Story: white card opening a window",
                 15118, 78, ["marco", "comida", "foto"])
    first = s.pic("Foto de fondo", "y6-dessert-02", label="Tu foto")
    x0, y0, x1, y1 = R("L", 145, 115, 625, 968)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

    def card(fr, u):
        return cx, cy, (x1 - x0) * k(fr, 3, 8), lerp(6, y1 - y0, k(fr, 9, 12)), 0, 1.0 if fr > 3 else 0.0
    s.obj("Tarjeta", solid(WHITE), card, base=(x1 - x0, y1 - y0))
    ix0, iy0, ix1, iy1 = R("L", 158, 128, 612, 848)
    mid = (iy0 + iy1) / 2
    s.pic("Foto", first["_sample"], reuse=first["placeholderId"],
          matte=lambda fr, u: ((ix0 + ix1) / 2, mid, ix1 - ix0, (iy1 - iy0) * k(fr, 24, 21), 0,
                               1.0 if fr > 24 else 0.0))
    s.words("#photooftheday", R("L", 228, 885, 545, 928), OUT, 700, INK, "Texto", at=45, n=30, how="type")
    return finish(t)


# 20. DO YOUR BEST: on a blue city a ribbon outline draws itself, the words fade in yellow and turn white
def do_your_best():
    t, s = story("do-your-best", "Historia: DO YOUR BEST en cinta", "Story: DO YOUR BEST in a ribbon", 15119, 76,
                 ["frase", "ciudad", "motivación"])
    s.pic("Foto de fondo", "h-city-03", label="Tu foto",
          look=[effect("duotone", strength=1.0, shadowColor="#141938", highlightColor="#D9DCE6", contrast=0.5)])
    th = 5 * SC
    half = [(961, 288), (1110, 288), (1110, 800), (960, 688)]
    other = [(959, 288), (812, 288), (812, 800), (960, 688)]
    s.outline("Cinta", [P("M", *p) for p in half], th, WHITE, at=3, n=33, closed=False)
    s.outline("Cinta 2", [P("M", *p) for p in other], th, WHITE, at=3, n=33, closed=False)
    for i, (w, r, at) in enumerate((("DO", (905, 375, 1015, 430), 18), ("YOUR", (855, 470, 1068, 525), 27),
                                    ("BEST", (865, 565, 1055, 620), 33))):
        c = s.words(w, R("M", *r), MON, 600, WHITE, "Título" if i == 0 else f"Título {i + 1}", at=at, n=8)
        s.fx(c, "layer.color_overlay", color="#F4D21C", animated={"opacity": lambda fr, u: 1 - k(fr, 60, 15)})
    return finish(t)


# 21. happy thoughts with a heart: the words fade in, slide down as a heart photo and three small hearts pop
def heart():
    t, s = story("heart", "Historia: foto en corazón «happy thoughts»", "Story: heart photo «happy thoughts»", 15120,
                 76, ["corazón", "amor", "melocotón"])
    s.bg("#F7CEC1", "#F2B57C")
    down = lambda fr: (0.0, 230 * SC * (k(fr, 48, 24) - 1))  # noqa: E731
    s.words("happy", R("R", 1425, 745, 1648, 810), PF, 700, WHITE, "Título", at=6, n=10, extra=down)
    s.words("thoughts", R("R", 1375, 828, 1697, 895), PF, 700, WHITE, "Título 2", at=16, n=10, extra=down)
    cx, cy = P("R", 1540, 330)
    w, h = 370 * SC, 335 * SC
    s.pic("Foto", "fx-woman-08", (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), path=HEART,
          matte=lambda fr, u: (cx, cy, w * k(fr, 54, 18), h * k(fr, 54, 18), 0, 1.0 if fr > 54 else 0.0))
    for i, (x, y, a, b, at) in enumerate(((1580, 560, 95, 85, 57), (1492, 598, 65, 58, 63), (1537, 665, 50, 45, 69))):
        px, py = P("R", x, y)
        s.obj(f"Corazón {i + 1}", solid("#EE8A46"),
              lambda fr, u, px=px, py=py, a=a, b=b, at=at: (px, py, a * SC * k(fr, at, 8), b * SC * k(fr, at, 8),
                                                             -12 + 24 * i, 1.0 if fr > at else 0.0),
              path=HEART, base=(a * SC, b * SC))
    s.words("photography", R("R", 1462, 950, 1617, 975), PF, 700, "#D9A27A", "Texto", at=0, n=6)
    return finish(t)


# 22. SEEK THE SEEKER: a white line opens into a white box; the words show the photo through their letters
def seek():
    t, s = story("seek", "Historia: SEEK THE SEEKER con letras de foto", "Story: SEEK THE SEEKER with photo letters",
                 15121, 50, ["frase", "hojas", "recorte"])
    first = s.pic("Foto de fondo", "fx-nature-01", label="Tu foto")
    x0, y0, x1, y1 = R("L", 173, 275, 598, 807)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

    def box(fr, u):
        h = lerp(4, 70 * SC, k(fr, 9, 6)) if fr < 18 else lerp(70 * SC, y1 - y0, k(fr, 18, 7))
        return cx, cy, (x1 - x0) * k(fr, 2, 7), h, 0, 1.0 if fr > 2 else 0.0
    s.obj("Caja", solid(WHITE), box, base=(x1 - x0, y1 - y0))
    for i, (w, r, at) in enumerate((("SEEK", (268, 420, 482, 490), 21), ("THE", (305, 505, 462, 575), 31),
                                    ("SEEKER", (225, 590, 547, 660), 38))):
        c = s.words(w, R("L", *r), OUT, 800, "#2E4A2A", "Título" if i == 0 else f"Título {i + 1}", at=at, n=8)
        s.pic(f"Letras {i + 1}", first["_sample"], reuse=first["placeholderId"], matte_clip=c)
    return finish(t)


# 23. Stylish: the skate photo slides in from the right with a giant turned word, the motto types beside it
def stylish_skate():
    t, s = story("stylish-skate", "Historia: Stylish vertical gigante con lema", "Story: giant vertical Stylish with a motto",
                 15122, 56, ["vertical", "patineta", "tipografía"])
    s.bg("#FFFFFF")
    pr = R("M", 673, 30, 1125, 1052)
    off = lambda fr: W * (1 - k(fr, 6, 18))  # noqa: E731
    ph = s.pic("Foto", "fx-skater-02", pr, geom=lambda fr, u: (off(fr), 0, 1.0),
               matte=lambda fr, u: ((pr[0] + pr[2]) / 2 + off(fr), (pr[1] + pr[3]) / 2, pr[2] - pr[0], pr[3] - pr[1],
                                    0, 1.0))
    c = s.words("Stylish", R("M", 965, 180, 1145, 890), OUT, 700, WHITE, "Título", how="none", rot=-90,
                extra=lambda fr: (off(fr), 0.0))
    c["matte"] = {"clip": ph["_matte"]["id"], "mode": "alpha"}
    s.words("BE HAPPY BE BRIGHT BE YOU", R("M", 1175, 215, 1210, 860), MON, 600, INK, "Texto", at=28, n=24,
            how="type", rot=-90)
    return finish(t)


# 24. WORK HARD. DREAM BIG.: the photo wipes down over a black panel, the two lines light up
def work_hard():
    t, s = story("work-hard", "Historia: WORK HARD. DREAM BIG. en panel negro", "Story: WORK HARD. DREAM BIG. on black",
                 15123, 34, ["frase", "motivación", "negro"])
    s.bg("#FFFFFF")
    s.bar("Panel", "#0A0A0A", lambda fr, u: R("R", 1248, 30, 1823, 918))
    x0, y0, x1, y1 = R("R", 1248, 30, 1823, 600)
    s.pic("Foto", "fx-face-04", (x0, y0, x1, y1),
          matte=lambda fr, u: ((x0 + x1) / 2, y0 + (y1 - y0) * k(fr, 9, 12) / 2, x1 - x0,
                               (y1 - y0) * k(fr, 9, 12), 0, 1.0 if fr > 9 else 0.0))
    s.words("WORK HARD.", R("R", 1305, 690, 1762, 745), OUT, 700, WHITE, "Título", at=9, n=12)
    s.words("DREAM BIG.", R("R", 1335, 765, 1733, 820), OUT, 700, WHITE, "Título 2", at=22, n=8)
    s.chevron(*P("R", 1535, 985), at=0)
    return finish(t)


# 25. S T Y L I S H: a cut-out photo swings in on teal, the letters pop in any order, «Link in Bio»
def stylish_bike():
    t, s = story("stylish-bike", "Historia: S T Y L I S H con recorte", "Story: S T Y L I S H with a cut-out", 15124, 40,
                 ["recorte", "turquesa", "enlace"])
    s.bg("#7FC6BC")
    letters = [("S", (152, 478, 228, 565)), ("T", (238, 555, 272, 600)), ("Y", (293, 478, 372, 565)),
               ("L", (395, 555, 425, 600)), ("I", (430, 478, 460, 565)), ("S", (482, 555, 536, 600)),
               ("H", (548, 478, 622, 565))]
    order = [0, 3, 1, 5, 2, 6, 4]
    for j, (ch, r) in enumerate(letters):
        if j in (1, 3, 5):  # the small letters go under the photo
            s.words(ch, R("L", *r), OUT, 700, WHITE, f"Letra {j + 1}", at=12 + 3 * order[j], n=6, how="rise", dy=30)
    x0, y0, x1, y1 = R("L", 185, 265, 620, 800)
    s.pic("Foto", "fx-skater-05", (x0, y0, x1, y1), label="Tu recorte",
          geom=lambda fr, u: (-700 * (1 - k(fr, 0, 30)), 200 * (1 - k(fr, 0, 30)), 1.0),
          rot=lambda fr, u: -70 * (1 - k(fr, 0, 30)))
    for j, (ch, r) in enumerate(letters):
        if j not in (1, 3, 5):
            s.words(ch, R("L", *r), OUT, 700, WHITE, f"Letra {j + 1}", at=12 + 3 * order[j], n=6, how="rise", dy=30)
    cx, cy = P("L", 385, 962)
    s.obj("Flecha", ring("#5E9C93", 5), lambda fr, u: (cx, cy, 30 * SC, 14 * SC, 0, 1.0), path="M 0 100 L 50 0 L 100 100")
    s.words("Link in Bio", R("L", 307, 985, 462, 1012), RAL, 600, "#5E9C93", "Texto", at=0, n=6)
    return finish(t)


# 26. Live what you love: the titles fade in, four photos open from the middle line, the scroll button
def live_what():
    t, s = story("live-what", "Historia: Live what you love con 2×2", "Story: Live what you love with a 2×2 grid", 15125,
                 36, ["cuadrícula", "collage", "blanco"])
    s.bg("#FFFFFF")
    rects = [R("M", 713, 265, 953, 583), R("M", 967, 265, 1207, 583), R("M", 713, 598, 953, 917),
             R("M", 967, 598, 1207, 917)]
    grid4(s, rects, ["fx-woman-01", "fx-fashion-02", "fx-woman-03", "fx-fashion-06"], P("M", 0, 590)[1], at=0, n=21)
    s.words("#photography", R("M", 850, 70, 1070, 98), RAL, 600, "#8E8E8E", "Texto", at=12, n=8)
    s.words("Live what", R("M", 836, 115, 1080, 160), RAL, 700, INK, "Título", at=15, n=8)
    s.words("you love", R("M", 850, 178, 1065, 225), RAL, 700, INK, "Título 2", at=28, n=8)
    s.chevron(*P("M", 960, 985), at=0)
    return finish(t)


# 27. #photooftheday band: a white band opens across the middle of the photo with the hashtag
def dog():
    t, s = story("dog", "Historia: foto partida por banda #photooftheday", "Story: photo split by a #photooftheday band",
                 15126, 58, ["mascota", "foto", "banda"])
    s.bg("#FFFFFF")
    pr = R("R", 1268, 52, 1802, 1030)
    s.pic("Foto", "puppy-01", pr, geom=zoom(1.1, 1.0, 0, 90))
    by0, by1 = P("R", 0, 488)[1], P("R", 0, 593)[1]
    mid = (by0 + by1) / 2
    s.bar("Banda", WHITE, lambda fr, u: (pr[0] - 2, mid - (mid - by0) * lerp(0.03, 1, k(fr, 39, 12)), pr[2] + 2,
                                         mid + (by1 - mid) * lerp(0.03, 1, k(fr, 39, 12))),
          op=lambda fr, u: 1.0 if fr > 36 else 0.0)
    s.words("#photooftheday", R("R", 1375, 520, 1693, 560), OUT, 700, INK, "Texto", at=48, n=9)
    return finish(t)


# 28. #instalove LIVE WHAT YOU LOVE: a line under the tag opens down into the photo, the name and words come in
def instalove():
    t, s = story("instalove", "Historia: #instalove LIVE WHAT YOU LOVE", "Story: #instalove LIVE WHAT YOU LOVE", 15127,
                 40, ["frase", "bosque", "nombre"])
    s.bg("#FFFFFF")
    x0, x1 = P("L", 112, 0)[0], P("L", 658, 0)[0]
    top, bot = P("L", 0, 220)[1], P("L", 0, 1038)[1]
    s.pic("Foto", "y5-h-forest-02", (x0, top, x1, bot),
          matte=lambda fr, u: ((x0 + x1) / 2, top + (bot - top) * lerp(0.004, 1, k(fr, 6, 30)) / 2,
                               (x1 - x0) * k(fr, 0, 6), (bot - top) * lerp(0.004, 1, k(fr, 6, 30)), 0, 1.0))
    s.bar("Etiqueta", "#0A0A0A", lambda fr, u: R("L", 285, 192, 485, 245))
    s.words("#instalove", R("L", 300, 204, 472, 236), OUT, 700, WHITE, "Etiqueta (texto)", at=0, n=4)
    s.words("Jo Daniels", R("L", 218, 108, 552, 148), OUT, 500, INK, "Nombre", at=12, n=18, how="type")
    s.words("LIVE", R("L", 300, 300, 468, 360), OUT, 800, WHITE, "Título", at=15, n=8)
    s.words("WHAT", R("L", 262, 385, 512, 445), OUT, 800, WHITE, "Título 2", at=24, n=8)
    s.words("YOU LOVE", R("L", 175, 468, 598, 530), OUT, 800, WHITE, "Título 3", at=30, n=8)
    return finish(t)


# 29. Anna Fletcher: on blue the tag rises while the photo opens upwards behind it, the name fades in
def anna():
    t, s = story("anna", "Historia: nombre con foto en degradado azul", "Story: name with a photo on a blue gradient",
                 15128, 64, ["nombre", "perfil", "degradado"])
    s.bg("#7DD0F5", "#4C4699")
    x0, y0, x1, y1 = R("M", 748, 165, 1173, 805)
    s.pic("Foto", "portrait-07", (x0, y0, x1, y1),
          matte=lambda fr, u: ((x0 + x1) / 2, y1 - (y1 - y0) * lerp(0.02, 1, k(fr, 24, 33)) / 2, x1 - x0,
                               (y1 - y0) * lerp(0.02, 1, k(fr, 24, 33)), 0, 1.0 if fr > 24 else 0.0))
    up = lambda fr: (0.0, (P("M", 0, 541)[1] - P("M", 0, 168)[1]) * (1 - k(fr, 27, 30)))  # noqa: E731
    s.bar("Etiqueta", "#7EC6EE", lambda fr, u: (lambda r: (r[0], r[1] + up(fr)[1], r[2], r[3] + up(fr)[1]))(
        R("M", 810, 137, 1110, 200)))
    s.words("#photooftheday", R("M", 826, 151, 1094, 187), OUT, 700, WHITE, "Etiqueta (texto)", how="none", extra=up)
    s.words("Anna", R("M", 825, 760, 1090, 835), OUT, 700, WHITE, "Título", at=48, n=9)
    s.words("Fletcher", R("M", 768, 860, 1158, 950), OUT, 700, WHITE, "Título 2", at=55, n=9)
    return finish(t)


# 30. Work hard. Dream big.: the red photo slides in from the right with the green 05, the words read upwards
def work_dream():
    t, s = story("work-dream", "Historia: Work hard. Dream big. vertical con 05",
                 "Story: vertical Work hard. Dream big. with 05", 15129, 48, ["frase", "vertical", "número"])
    s.bg("#FFFFFF")
    pr = R("R", 1408, 30, 1823, 1052)
    off = lambda fr: (W * (1 - k(fr, 0, 24)), 0.0)  # noqa: E731
    s.pic("Foto", "y6-dish-04", pr, geom=lambda fr, u: (off(fr)[0], 0, 1.0))
    cx, cy = P("R", 1405, 541)
    s.circle05(cx, cy, 45 * SC, "#3DA63A", 0, n=1, off=off)
    c = s.words("Work hard. Dream big.", R("R", 1295, 258, 1345, 822), OUT, 600, "#A8A8A8", "Texto", how="none",
                rot=-90)
    s.typed(c, 21, stagger=0.22, duration=0.25, preset="fade", unit="word")
    return finish(t)


TEMPLATES = [neon, beautiful, believe, love_friendship, conquer, success, stylish_design, must_believe, alison,
             happy_thoughts, so_it_goes, catherine, spring_sale, lifestyle, elegant, love_loves, forty_sale, nature,
             photo_frame, do_your_best, heart, seek, stylish_skate, work_hard, stylish_bike, live_what, dog, instalove,
             anna, work_dream]
