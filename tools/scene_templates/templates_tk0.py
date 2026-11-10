"""TIKTOK folder video 0 as Stock templates (tk0-*). See docs/plan-tiktok.md.

«TikTok Stories Pack» (30653429.mp4, 1920×1080 at 29.97 fps): sixteen vertical stories in blue, black, red and pink
with stickers (smileys, eyes, hearts, «LIKE!» tickets, chat bubbles, play buttons), shown in the reference three at a
time, in phones and in a scrolling grid. Each story is laid out on 1080×1920 (measured on crops of the screen scaled
to 1080×1920) with the moves studied on 10 fps sheets. Kit de TikTok; ids `tk0-*`, order 14000-. Study notes in
tienda/plantillas/estudio-30653429/NOTAS.md.

Brand words are neutral («TIK-TOK PROMO» → «SUPER PROMO», «MOTION MEDIA GROUP» → «YOUR BRAND NAME», «#MMG» →
«#SALE»); the note glyph stays only as a small social icon. Photos and videos are photo slots. Each story plays its
entrance, holds, and leaves with its entrance backwards at 2.5× speed.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, tall
from llt_motion import frames_of
from scene import keys
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import EXIT, S, TRIANGLE, lin, ring, rot_pt
from templates_yp4 import HEART, art_except

W, H = 1080, 1920
BLUE, PINK, RED, SKY = "#003AD1", "#FEA4DA", "#FE0933", "#65D1FC"
BLACK, WHITE, INK = "#000000", "#FFFFFF", "#111111"
LG, M = "League Gothic", "Montserrat"
f6._FILES[(LG, 400)] = "fonts.extra/fonts/leaguegothic/LeagueGothic-Regular.ttf"
for _w, _f in ((500, "Medium"), (600, "SemiBold"), (700, "Bold"), (800, "ExtraBold"), (900, "Black")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"

TICKET = "M 0 0 L 100 0 L 100 34 C 88 37 88 63 100 66 L 100 100 L 0 100 L 0 66 C 12 63 12 37 0 34 Z"
EYE = "M 0 50 C 22 8 64 -4 100 40 C 74 92 30 100 0 50 Z"
TAIL = "M 0 0 L 100 0 L 15 100 Z"
TAIL_R = "M 0 0 L 100 0 L 85 100 Z"
NOTE = ("M 50 4 L 66 4 C 68 18 77 27 92 28 L 92 43 C 82 43 73 40 66 35 L 66 70 C 66 85 55 96 40 96 "
        "C 25 96 14 85 14 70 C 14 55 25 45 40 45 L 45 45 L 45 60 C 36 58 30 64 30 70 C 30 77 35 81 41 81 "
        "C 47 81 50 76 50 70 Z")
SMILE = "M 0 0 Q 50 70 100 0"


def _p(id, es, en, order, dur, tags=(), thumb=0.55):
    return tall(f"tk0-{id}", es, en, "tiktok", dur, order=order,
                tags=["tiktok", "historia", "reels", "vertical"] + list(tags), thumb_at=round(dur * thumb, 1))


def dur_for(entrance, hold=2.0):
    return round(entrance + hold + entrance / EXIT, 1)


def bo(fr, at, n=8):
    """0 → 1 with a small overshoot (a sticker that pops)."""
    x = lin(fr, at, n)
    if x <= 0:
        return 0.0
    c1 = 1.70158
    return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2


def cap_width(text, cap, family=LG, weight=400):
    """Ink width of `text` whose capitals are `cap` px tall."""
    f = f6._font(family, weight)
    hb = f.getbbox("H")
    bb = f.getbbox(text)
    ink = f.getlength(text[:-1]) + f.getbbox(text[-1])[2] - bb[0]
    return ink * cap / (hb[3] - hb[1])


def hollow(colour, width):
    return ring(colour, width)


class T(S):
    """A story on 1080×1920."""

    def __init__(self, t, dur):
        S.__init__(self, t, dur)
        self.pivot = (W / 2, H / 2)

    def title(self, content, x, y0, y1, colour, name="Título", family=LG, weight=400, align="left", maxw=None, **kw):
        """A line whose capitals span y0..y1, from x (its left, centre or right with align), at most maxw wide (the
        reference's face is narrower than League Gothic: the width wins and the letters come out a bit shorter)."""
        w = cap_width(content, y1 - y0, family, weight)
        w = min(w, maxw) if maxw else w
        x0 = x if align == "left" else x - w / 2 if align == "center" else x - w
        return self.say(content, (x0, y0, x0 + w, y1), family, weight, colour, name, align=align, **kw)

    def bg(self, colour, name="Fondo"):
        return self.rect(name, solid(colour), lambda fr, u: (-10, -10, W + 10, H + 10))


class G:
    """A group of parts that move together: m(fr, u) = (dx, dy, scale, rot, opacity) about the rest centre (cx, cy)."""

    def __init__(self, s, cx, cy, m):
        self.s, self.cx, self.cy, self.m = s, cx, cy, m

    def at(self, fr, u, ox=0.0, oy=0.0):
        dx, dy, sc, rot, op = self.m(fr, u)
        X, Y = self.cx + dx, self.cy + dy
        px, py = rot_pt(X + ox * sc, Y + oy * sc, rot, X, Y)
        return px, py, sc, rot, op

    def shape(self, name, layers, ox, oy, w, h, rot0=0.0, op=None, **kw):
        def g(fr, u):
            px, py, sc, rot, o = self.at(fr, u, ox, oy)
            return px, py, w * sc, h * sc, rot + rot0, o * (op(fr, u) if op else 1.0)
        return self.s.obj(name, layers, g, base=(w, h), **kw)

    def text(self, content, ox, oy, cap, colour, name, family=LG, weight=400, rot0=0.0, width=None, align="center",
             op=None, maxw=None):
        w = width or cap_width(content, cap, family, weight)
        w = min(w, maxw) if maxw else w
        x = self.cx + ox
        x0 = x - w / 2 if align == "center" else x
        ink = (x0, self.cy + oy - cap / 2, x0 + w, self.cy + oy + cap / 2)
        icx = (ink[0] + ink[2]) / 2

        def g(fr, u):
            px, py, sc, rot, o = self.at(fr, u, icx - self.cx, oy)
            return px - icx, py - (self.cy + oy), sc, rot + rot0, o * (op(fr, u) if op else 1.0)
        return self.s.say(content, ink, family, weight, colour, name, align=align, geom=g)


def popm(at, n=8, rot0=0.0, spin=0.0):
    """A sticker that pops in at frame `at` (turning `spin` degrees as it grows)."""
    return lambda fr, u: (0, 0, bo(fr, at, n), rot0 + spin * (1 - k(fr, at, n)), 1.0 if fr >= at else 0.0)


# --- stickers -------------------------------------------------------------------------------------------------------
def smiley(s, name, cx, cy, d, colour, m, wink=None):
    g = G(s, cx, cy, m)
    g.shape(name, solid(colour), 0, 0, d, d, kind="ellipse")
    g.shape(f"{name} (aro)", ring(INK, max(2, d * 0.012)), 0, 0, d * 0.8, d * 0.8, kind="ellipse")
    for i, ex in enumerate((-0.12, 0.12)):
        eh = (lambda fr, u: 1.0 - 0.85 * (k(fr, wink, 3) - k(fr, wink + 4, 3))) if wink is not None else None
        g.shape(f"{name} (ojo {i + 1})", solid(INK), ex * d, -0.1 * d, 0.065 * d, 0.16 * d, kind="ellipse",
                op=None) if eh is None else _eye_dot(g, f"{name} (ojo {i + 1})", ex * d, -0.1 * d, d, eh)
    g.shape(f"{name} (sonrisa)", ring(INK, max(2, d * 0.014)), 0, 0.15 * d, 0.48 * d, 0.2 * d, path=SMILE)
    return g


def _eye_dot(g, name, ox, oy, d, eh):
    def geom(fr, u):
        px, py, sc, rot, o = g.at(fr, u, ox, oy)
        return px, py, 0.065 * d * sc, 0.16 * d * sc * eh(fr, u), rot, o
    return g.s.obj(name, solid(INK), geom, kind="ellipse", base=(0.065 * d, 0.16 * d))


def eye(s, name, cx, cy, w, m, white=WHITE, pupil=BLACK, look=None, blink=None, flip=False):
    """An almond eye; look(fr, u) = (dx, dy) of the pupil in px, blink = frame it closes."""
    g = G(s, cx, cy, m)
    hb = (lambda fr, u: 1.0 - 0.92 * (k(fr, blink, 3) - k(fr, blink + 4, 3))) if blink is not None else (lambda fr, u: 1)

    def lid(fr, u):
        px, py, sc, rot, o = g.at(fr, u)
        return px, py, w * sc * (-1 if flip else 1), w * 0.5 * sc * hb(fr, u), rot, o
    s.obj(name, solid(white), lid, path=EYE, base=(w, w * 0.5))

    def dot(fr, u):
        lx, ly = look(fr, u) if look else (0, 0)
        px, py, sc, rot, o = g.at(fr, u, lx, ly)
        return px, py, w * 0.3 * sc, w * 0.3 * sc * hb(fr, u), rot, o
    s.obj(f"{name} (pupila)", solid(pupil), dot, kind="ellipse", base=(w * 0.3, w * 0.3))
    return g


def heart(s, name, cx, cy, d, colour, m, inner=BLACK, rot0=0.0):
    g = G(s, cx, cy, m)
    g.shape(name, solid(colour), 0, 0, d, d * 0.9, rot0=rot0, path=HEART)
    if inner:
        g.shape(f"{name} (centro)", solid(inner), 0, 0.02 * d, d * 0.28, d * 0.25, rot0=rot0, path=HEART)
    return g


def ticket(s, name, text, cx, cy, w, h, back, ink, m, rot0=0.0, family=M, weight=800, cap=None, lines=None):
    g = G(s, cx, cy, m)
    weight = 400 if family == LG else weight
    g.shape(name, solid(back), 0, 0, w, h, rot0=rot0, path=TICKET)
    rows = lines or [text]
    cap = cap or h * (0.36 if len(rows) == 1 else 0.2)
    step = cap * 1.55
    for i, row in enumerate(rows):
        oy = (i - (len(rows) - 1) / 2) * step
        ox, oy2 = rot_pt(0, oy, rot0, 0, 0)
        g.text(row, ox, oy2, cap, ink, f"{name} (texto)" if i == 0 else f"{name} (texto {i + 1})", family, weight,
               rot0=rot0, maxw=w * 0.76)
    return g


def note(s, name, cx, cy, d, m):
    g = G(s, cx, cy, m)
    g.shape(name, solid(BLACK), 0, 0, d, d, kind="ellipse")
    for colour, o in (("#25F4EE", -0.025), ("#FE2C55", 0.025), (WHITE, 0.0)):
        g.shape(f"{name} (nota)", solid(colour), o * d + 0.01 * d, o * d, d * 0.48, d * 0.56, path=NOTE)
    return g


def tri_path(angle):
    """The play triangle pointing `angle` degrees (clockwise from the right), drawn turned in its own square box:
    a triangle clip turned with the clip's rotation came out at other angles in the render (see NOTAS)."""
    pts = ((40.0, 0.0), (-20.0, -36.0), (-20.0, 36.0))  # about its centroid, tip to the right
    out = [rot_pt(x, y, angle, 0, 0) for x, y in pts]
    return "M " + " L ".join(f"{50 + x:.2f} {50 + y:.2f}" for x, y in out) + " Z"


def play(s, name, cx, cy, d, back, m, tri=WHITE, line=WHITE, angle=0.0, angle_from=None):
    """A round play button whose triangle points `angle` degrees; angle_from = (angle0, at, n) shows it first at
    angle0 and turns it to `angle` at frame `at` over n frames (a quick cross-fade between the two)."""
    g = G(s, cx, cy, m)
    g.shape(name, solid(back), 0, 0, d, d, kind="ellipse")
    g.shape(f"{name} (aro)", ring(line, max(2, d * 0.014)), 0, 0, d * 0.8, d * 0.8, kind="ellipse")
    if angle_from:
        a0, at, n = angle_from
        g.shape(f"{name} (triángulo 0)", solid(tri), 0, 0, d * 0.42, d * 0.42, path=tri_path(a0),
                op=lambda fr, u: 1 - lin(fr, at, n))
        g.shape(f"{name} (triángulo)", solid(tri), 0, 0, d * 0.42, d * 0.42, path=tri_path(angle),
                op=lambda fr, u: lin(fr, at, n))
    else:
        g.shape(f"{name} (triángulo)", solid(tri), 0, 0, d * 0.42, d * 0.42, path=tri_path(angle))
    return g


def dots(s, name, xs, y, d, colour, ats, n=6):
    for i, (x, at) in enumerate(zip(xs, ats)):
        s.obj(f"{name} {i + 1}", solid(colour), lambda fr, u, x=x, at=at: (x, y, d * bo(fr, at, n), d * bo(fr, at, n), 0,
                                                                          1.0 if fr >= at else 0.0),
              kind="ellipse", base=(d, d))


def bubble(s, name, x0, y0, x1, y1, colour, m, tail=None, radius=None, tail_right=False):
    """A chat bubble (x0, y0, x1, y1) with a tail = (x, w, depth) under its bottom edge; m moves it about its centre."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    g = G(s, cx, cy, m)
    r = radius if radius is not None else (y1 - y0) / 2
    if tail:
        tx, tw, td = tail
        g.shape(f"{name} (cola)", solid(colour), tx + tw / 2 - cx, y1 - cy + td / 2 - 2, tw, td + 4,
                path=TAIL_R if tail_right else TAIL)
    g.shape(name, solid(colour), 0, 0, x1 - x0, y1 - y0, radius=r)
    return g


def ticker(s, name, text, y0, y1, colour, back, speed=110.0, rot=0.0, cx=540.0, cap=None, width=2600, reverse=False):
    """A band with a line of words that scrolls."""
    cy = (y0 + y1) / 2
    hh = y1 - y0
    s.obj(name, solid(back), lambda fr, u: (cx, cy, width, hh, rot, 1.0), base=(width, hh))
    cap = cap or hh * 0.45
    words = (text + "   ") * 8
    w = cap_width(words, cap, M, 800)
    sign = 1 if reverse else -1
    x0 = cx - w / 2

    def g(fr, u):
        d = sign * speed * u
        ox, oy = rot_pt(d, 0, rot, 0, 0)
        return ox, oy, 1, rot, 1
    return s.say(words, (x0, cy - cap / 2, x0 + w, cy + cap / 2), M, 800, colour, f"{name} (texto)", geom=g)


def photo(s, sample, box, name="Foto", label=None, m=None, radius=0.0, matte=True):
    """A photo slot in box (x0, y0, x1, y1); m(fr, u) = (dx, dy, scale, rot, opacity) about its centre; with a radius
    it is shown through a rounded box (a track matte) that moves with it."""
    t = s.t
    x0, y0, x1, y1 = box
    b = Box(x0, y0, x1 - x0, y1 - y0)
    motion = None
    vals = [(u, m(fr, u)) for u, fr in s.each()] if m else None
    if vals:
        motion = [(u, {"s": max(1e-3, v[2]), "dx": v[0], "dy": v[1]}, "linear") for u, v in vals]
    clip = t.photo(t.track("video", name), sample, 0.0, s.dur, b, motion, label=label or name)
    clip["name"] = name
    if vals and any(abs(v[3]) > 1e-6 for _, v in vals):
        clip["rotation"] = keys([(u, round(v[3], 3), "linear") for u, v in vals])
    if vals and any(v[4] < 0.999 for _, v in vals):
        clip["opacity"] = keys([(u, round(max(0.0, min(1.0, v[4])), 4), "linear") for u, v in vals])
    if radius and matte:
        mm = m or (lambda fr, u: (0, 0, 1, 0, 1))
        g = G(s, b.cx, b.cy, mm)
        shape = g.shape(f"{name} (forma)", solid(WHITE), 0, 0, b.w, b.h, radius=radius)
        clip["matte"] = {"clip": shape["id"], "mode": "alpha"}
    return clip


def phone(s, name, sample, cx, cy, w, h, m, label=None):
    """A phone with a photo on its screen (w × h is the screen), moved by m about (cx, cy)."""
    g = G(s, cx, cy, m)
    g.shape(f"{name} (cuerpo)", solid("#151515"), 0, 0, w + 34, h + 34, radius=62)
    g.shape(f"{name} (borde)", ring("#B9BCC2", 4), 0, 0, w + 38, h + 38, radius=65)
    photo(s, sample, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), name, label, m=m, radius=46)
    g.shape(f"{name} (cámara)", solid("#151515"), 0, -h / 2 + 22, w * 0.36, 44, radius=22)
    return g


# --- A. WHAT DO YOU LIKE TO WATCH?: a white bubble types the question, a light-blue answer pops under it ------------
def watch():
    D = dur_for(3.4, 1.6)
    t = _p("que-ves", "Historia: ¿qué te gusta ver? con burbujas de chat", "Story: what do you like to watch? chat",
           14000, D, ["chat", "pregunta", "azul"])
    s = T(t, D)
    s.bg(BLUE)
    smiley(s, "Carita", 845, 220, 245, PINK, popm(0, 9, spin=-30))
    rise = lambda fr: -382 * k(fr, 40, 10)  # noqa: E731  the question goes up when the answer comes
    pop_q = lambda fr: bo(fr, 4, 9)  # noqa: E731
    bubble(s, "Burbuja", 95, 922, 990, 1112, WHITE, lambda fr, u: (0, rise(fr), pop_q(fr), 0, 1.0 if fr >= 4 else 0),
           tail=(230, 70, 62))
    q = s.title("WHAT DO YOU LIKE TO WATCH?", 540, 970, 1066, INK, align="center", maxw=755,
                geom=lambda fr, u: (0, rise(fr), 1, 0, 1))
    s.typed(q, 16, stagger=0.028, duration=0.03)
    ticket(s, "LIKE!", "LIKE!", 265, 315, 360, 165, RED, WHITE, popm(12, 9, -20, -25))
    eye(s, "Ojo", 870, 1440, 300, popm(22, 8), blink=45)
    note(s, "Nota", 300, 1650, 250, popm(26, 8))
    ticker(s, "Cinta", "SUPER PROMO", 1832, 1920, WHITE, BLACK)
    bubble(s, "Respuesta", 180, 825, 995, 1015, SKY, lambda fr, u: (0, 0, bo(fr, 43, 9), 0, 1.0 if fr >= 43 else 0),
           tail=(800, 60, 64), tail_right=True)
    a = s.title("I LIKE MUSIC", 272, 875, 965, BLUE, "Texto")
    s.typed(a, 68, stagger=0.06, duration=0.03)
    s.rect("Cursor", solid(BLUE), lambda fr, u: (258, 870, 266, 970),
           op=lambda fr, u: 1.0 if (52 <= fr < 68 and (fr // 8) % 2 == 0) else 0.0)
    heart(s, "Corazón", 460, 1225, 170, RED, popm(50, 8, 18, 30))
    return t


# --- B. SUPER PROMO on black: a big smiley shrinks to its corner, the blue bubble grows, the count goes up --------
def promo_black():
    D = dur_for(2.2, 2.0)
    t = _p("promo-negro", "Historia: SUPER PROMO en burbuja azul sobre negro", "Story: SUPER PROMO in a blue bubble on black",
           14001, D, ["promo", "negro", "contador"])
    s = T(t, D)
    s.bg(BLACK)
    x = f6.curve([(0, 450), (12, 450), (21, 845)])
    y = f6.curve([(0, 520), (12, 560), (21, 1585)])
    d = f6.curve([(0, 760), (9, 820), (21, 240)])
    smiley(s, "Carita", 845, 1585, 240, PINK, lambda fr, u: (x(fr) - 845, y(fr) - 1585, d(fr) / 240,
                                                             8 * math.sin(u * 2.4), 1), wink=6)
    gm = lambda fr, u: (0, 0, bo(fr, 12, 10), 0, 1.0 if fr >= 12 else 0)  # noqa: E731
    bubble(s, "Burbuja", 115, 770, 985, 1100, BLUE, gm, tail=(705, 110, 95), radius=26, tail_right=False)
    g = G(s, 550, 940, gm)
    g.text("SUPER PROMO", 0, 0, 205, WHITE, "Título", maxw=780)
    m2 = popm(25, 8, 2)
    bubble(s, "Marca", 108, 545, 795, 695, WHITE, m2, tail=(200, 60, 40))
    G(s, 451, 620, m2).text("YOUR BRAND NAME", 0, 0, 34, INK, "Texto", M, 800)
    G(s, 970, 770, popm(30, 7)).shape("Insignia", solid(RED), 0, 0, 130, 130, kind="ellipse")
    num = s.title("21", 970, 745, 795, WHITE, "Número", M, 800, align="center",
                  geom=lambda fr, u: (0, 0, 1, 0, 1.0 if fr >= 32 else 0.0))
    num["textStyle"].update(counter=True, counterFrom=0, counterSeconds=2.0)
    play(s, "Play", 235, 270, 190, RED, popm(42, 8, 0, -60))
    eye(s, "Ojo", 1005, 325, 280, lambda fr, u: (180 * (1 - k(fr, 45, 9)), 0, 1, -28, 1.0 if fr >= 45 else 0),
        white=SKY, pupil=BLACK, blink=72)
    dots(s, "Puntos", (830, 885, 940), 175, 34, PINK, (48, 50, 52))
    ticket(s, "LIKE!", "LIKE!", 360, 1470, 400, 190, SKY, INK, popm(40, 9, 25, 30))
    return t


# --- C. OUR MISSION on red: the photo slides down, the title rises, the bubble types the mission ---------------------
def mission():
    D = dur_for(3.0, 1.8)
    t = _p("mision", "Historia: nuestra misión con foto sobre rojo", "Story: our mission with a photo on red", 14002, D,
           ["misión", "rojo", "foto"])
    s = T(t, D)
    s.bg(RED)
    photo(s, "portrait-04", (155, 135, 670, 965), "Foto", m=lambda fr, u: (0, -1100 * (1 - k(fr, 0, 15)), 1, 0, 1),
          radius=42)
    w1 = cap_width("OUR ", 150)
    ink_all = cap_width("OUR MISSION", 150)
    x0 = 540 - ink_all / 2
    s.title("OUR", x0, 1065, 1215, INK, "Título", reveal=lambda fr: (0, 1040, W, 1240),
            shift=lambda fr: (0, 200 * (1 - k(fr, 14, 9))))
    s.title("MISSION", x0 + w1, 1065, 1215, INK, "Título 2", reveal=lambda fr: (0, 1040, W, 1240),
            shift=lambda fr: (0, 200 * (1 - k(fr, 18, 9))))
    gb = lambda fr, u: (0, 0, bo(fr, 16, 10), 0, 1.0 if fr >= 16 else 0)  # noqa: E731
    bubble(s, "Burbuja", 115, 1290, 960, 1515, WHITE, gb, tail=(225, 80, 85), radius=26)
    for i, line in enumerate(("Support creativity and", "bring joy to users")):
        c = s.title(line, 175, 1352 + 64 * i, 1390 + 64 * i, INK, f"Texto {i + 1}" if i else "Texto", M, 600)
        s.typed(c, 42 + 22 * i, stagger=0.035, duration=0.03)
    smiley(s, "Carita", 105, 630, 215, SKY, popm(30, 8, 0, 40))
    eye(s, "Ojo", 870, 720, 245, popm(33, 8, -15), blink=78)
    heart(s, "Corazón", 905, 185, 160, BLUE, popm(36, 8, -12, 30))
    s.rect("Franja rosa", solid(PINK), lambda fr, u: (-10, 1780, W + 10, H + 10))
    ticker(s, "Cinta 2", "SUPER PROMO", 1640, 1840, WHITE, BLACK, speed=90, rot=-8, cx=540, reverse=True, cap=40)
    ticker(s, "Cinta", "SUPER PROMO", 1690, 1782, WHITE, BLACK, speed=120)
    return t


# --- D. Blue and black collage: three photos slide in, LIKE!, a white heart and a red pill pop --------------------
def collage_blue():
    D = dur_for(1.6, 2.4)
    t = _p("collage-azul", "Historia: collage de tres fotos en azul y negro", "Story: three-photo collage in blue and black",
           14003, D, ["collage", "fotos", "azul"])
    s = T(t, D)
    s.bg(BLACK)
    s.rect("Fondo azul", solid(BLUE), lambda fr, u: (-10, -10, W + 10, 930 * k(fr, 0, 10)))
    photo(s, "kids-03", (568, 107, 1017, 892), "Foto", m=lambda fr, u: (0, -1000 * (1 - k(fr, 3, 12)), 1, 0, 1))
    photo(s, "selfie-04", (74, 442, 520, 1231), "Foto 2", m=lambda fr, u: (-700 * (1 - k(fr, 6, 12)), 0, 1, 0, 1))
    photo(s, "friends-03", (560, 1003, 996, 1750), "Foto 3", m=lambda fr, u: (0, 1000 * (1 - k(fr, 9, 12)), 1, 0, 1))
    ticket(s, "LIKE!", "LIKE!", 251, 240, 325, 140, BLACK, WHITE, popm(21, 8, -8, -25))
    heart(s, "Corazón", 564, 763, 170, WHITE, popm(24, 8, 0, 25))
    g = G(s, 416, 1378, popm(27, 9))
    g.shape("Píldora (cola)", solid(RED), -230, 80, 60, 70, rot0=-10, path=TAIL)
    g.shape("Píldora", solid(RED), 0, 0, 700, 130, rot0=-10, radius=65)
    g.text("Change the text in one click", 0, 0, 34, WHITE, "Texto", M, 700, rot0=-10)
    eye(s, "Ojo", 241, 1709, 230, popm(30, 8, -5), white=SKY, pupil=BLACK)
    play(s, "Play", 872, 1776, 200, PINK, popm(33, 8), tri=INK, line=INK, angle=180)
    return t


# --- E. BIG PROMO DAY: two blue tapes cross, the red PROMO label tilts, BIG drops and DAY rises ------------------
def promo_x():
    D = dur_for(1.6, 2.4)
    t = _p("promo-x", "Historia: PROMO con cintas en X", "Story: PROMO with crossed tapes", 14004, D,
           ["promo", "negro", "cintas"])
    s = T(t, D)
    s.bg(BLACK)
    for i, (rot, rev) in enumerate(((54, False), (-54, True))):
        def band(fr, u):
            return 0.0, 0.0  # the tapes are there from the first frame, as in the reference
        s.obj(f"Cinta {i + 1}", solid(BLUE), lambda fr, u, band=band, rot=rot: (
            540 + band(fr, u)[0], 975 + band(fr, u)[1], 2600, 135, rot, 1), base=(2600, 135))
        words = "#SALE   " * 12
        w = cap_width(words, 58, M, 800)

        def tg(fr, u, band=band, rot=rot, rev=rev):
            d = (1 if rev else -1) * 70 * u
            ox, oy = rot_pt(d, 0, rot, 0, 0)
            bx, by = band(fr, u)
            return ox + bx, oy + by, 1, rot, 1
        s.say(words, (540 - w / 2, 946, 540 + w / 2, 1004), M, 800, INK, f"Cinta {i + 1} (texto)", geom=tg)
    tilt = lambda fr: -10 * k(fr, 24, 9)  # noqa: E731
    s.title("BIG", 540, 580, 790, WHITE, "Título", align="center",
            geom=lambda fr, u: (0, -900 * (1 - k(fr, 12, 12)), 1, 0, 1))
    s.title("DAY", 540, 1110, 1450, WHITE, "Título 2", align="center",
            geom=lambda fr, u: (0, 1000 * (1 - k(fr, 15, 12)), 1, 0, 1))
    gl = G(s, 540, 975, lambda fr, u: (0, 0, bo(fr, 0, 9), tilt(fr), 1))
    gl.shape("Etiqueta", solid(RED), 0, 0, 800, 290)
    for side in (-1, 1):
        gl.shape("Etiqueta (lado)", solid(RED), side * 400, 0, 200, 210, kind="ellipse")
    gl.text("PROMO", 0, 0, 120, INK, "Texto", M, 800)
    return t


# --- F. TRENDY STYLE: three bands slide in, the words type, an eye wanders over the title ------------------------
def trendy():
    D = dur_for(2.0, 2.2)
    t = _p("trendy", "Historia: TRENDY STYLE con franjas de colores", "Story: TRENDY STYLE with colour bands", 14005, D,
           ["tendencia", "azul", "franjas"])
    s = T(t, D)
    s.bg(BLUE)
    for i, (colour, y0, y1, at, e) in enumerate(((SKY, 1040, 1312, 0, 1.0), (RED, 1310, 1592, 2, 0.92),
                                                (PINK, 1590, 1880, 4, 0.8))):
        s.rect(f"Franja {i + 1}", solid(colour), lambda fr, u, y0=y0, y1=y1, at=at: (-10, y0, -10 + 1100 * k(fr, at, 12), y1))
    top = s.title("SUPER PROMO FOR EVERYONE", 540, 125, 155, PINK, "Texto", M, 700, align="center")
    s.typed(top, 18, stagger=0.02, duration=0.03)
    c = s.title("TRENDY", 530, 180, 500, WHITE, align="center", maxw=600)
    s.typed(c, 3, stagger=0.06, duration=0.12, preset="rise")
    c = s.title("STYLE", 545, 530, 960, WHITE, "Título 2", align="center", maxw=630)
    s.typed(c, 7, stagger=0.06, duration=0.12, preset="rise")
    ex = lambda fr, u: -260 * (1 - k(fr, 6, 9)) + (0 if fr < 45 else 210 * (1 - math.cos((u - 45 / FPS) * 1.7)))  # noqa
    eye(s, "Ojo", 290, 375, 260, lambda fr, u: (ex(fr, u), 0, 1, -10, 1.0 if fr >= 6 else 0), white=SKY)
    note(s, "Nota", 540, 680, 200, popm(12, 8))
    for i, (word, x0, y0, y1, at, mw) in enumerate((("FLASHY &", 215, 1080, 1280, 21, 475),
                                                    ("CLASSY &", 375, 1360, 1560, 27, 475),
                                                    ("SIMPLY COOL", 215, 1640, 1840, 30, 635))):
        c = s.title(word, x0, y0, y1, INK, f"Texto {i + 2}", maxw=mw)
        s.typed(c, at, stagger=0.05, duration=0.08, preset="rise")
    heart(s, "Corazón", 780, 1175, 140, RED, popm(36, 8, -15, 30))
    play(s, "Play", 240, 1440, 150, WHITE, popm(27, 8), tri=RED, line=RED, angle=180)
    ticket(s, "Sello", "IT'S LIT!", 875, 1690, 250, 110, BLUE, WHITE,
           lambda fr, u: (500 * (1 - k(fr, 33, 9)), 0, 1, -15, 1.0 if fr >= 33 else 0))
    return art_except(t, keep=("Fondo", "Franja"))


# --- G. Black collage of six photos: the blue tag pops first, the photos slide in, the stickers follow -------------
def collage_black():
    D = dur_for(1.8, 2.2)
    t = _p("collage-negro", "Historia: collage de seis fotos con stickers", "Story: six-photo collage with stickers",
           14006, D, ["collage", "fotos", "negro"])
    s = T(t, D)
    s.bg(BLACK)
    boxes = (((55, -10, 500, 590), "friends-01", (-1, 0)), ((575, -10, 1035, 590), "dance-01", (1, 0)),
             ((55, 670, 500, 1445), "friends-10", (-1, 0)), ((575, 650, 1035, 1445), "pet-01", (1, 0)),
             ((55, 1535, 500, 1930), "friends-08", (-1, 0)), ((575, 1515, 1035, 1930), "selfie-02", (1, 0)))
    for i, (box, sample, (sx, sy)) in enumerate(boxes):
        at = 6 + 2 * i
        photo(s, sample, box, "Foto" if i == 0 else f"Foto {i + 1}",
              m=lambda fr, u, at=at, sx=sx: (sx * 700 * (1 - k(fr, at, 12)), -14 * u, 1, 0, 1))
    smiley(s, "Carita", 550, 210, 220, PINK, popm(24, 8, 30, 40))
    ticket(s, "Reto", "#CHALLENGE", 350, 575, 340, 150, SKY, INK, popm(27, 8, 15, 25), family=LG, weight=400, cap=74)
    eye(s, "Ojo", 720, 655, 300, popm(30, 8, 8), blink=70)
    g = G(s, 550, 1110, lambda fr, u: (0, 0, bo(fr, 2, 10), -12, 1.0 if fr >= 2 else 0))
    g.shape("Etiqueta", solid(BLUE), 0, 0, 700, 270, radius=60)
    g.text("Millions of videos", 0, -38, 44, WHITE, "Texto", M, 700)
    g.text("for every taste", 0, 38, 44, WHITE, "Texto 2", M, 700)
    heart(s, "Corazón", 205, 1500, 210, PINK, popm(33, 8, -10, 25))
    play(s, "Play", 910, 1780, 200, RED, popm(36, 8))
    return t


# --- H. Tapes and a phone: four word tapes cross the blue, a phone with your video comes in tilted -------------------
def tapes_phone():
    D = dur_for(1.6, 2.4)
    t = _p("cintas-telefono", "Historia: cintas de palabras y teléfono con video", "Story: word tapes and a phone",
           14007, D, ["cintas", "teléfono", "azul"])
    s = T(t, D)
    s.bg(BLUE)
    for i, (word, x) in enumerate((("FLASHY TRENDY", 270), ("STYLISH COOL", 810))):
        s.say(word, (x - 960, 690, x + 960, 1230), LG, 400, BLUE, f"Fondo (texto {i + 1})", layers=hollow("#2A5CF0", 3),
              editable=False, geom=lambda fr, u, i=i: (0, (1 if i else -1) * 25 * u, 1, 90, 1))
    tapes = ((SKY, BLUE, "FLASHY", 540, 390, -21), (WHITE, INK, "TRENDY", 540, 690, -34),
             (BLACK, WHITE, "STYLISH", 540, 980, 20), (PINK, RED, "CLASSY", 540, 1430, -27))
    for i, (back, ink, word, cx, cy, rot) in enumerate(tapes):
        at = 2 * i

        def m(fr, u, rot=rot, at=at, i=i):
            e = (2400 if i % 2 else -2400) * (1 - k(fr, at, 12))
            ox, oy = rot_pt(e, 0, rot, 0, 0)
            return ox, oy

        def band(fr, u, m=m, cx=cx, cy=cy, rot=rot):
            ox, oy = m(fr, u)
            return cx + ox, cy + oy, 2600, 120, rot, 1
        s.obj(f"Cinta {i + 1}", solid(back), band, base=(2600, 120))
        words = (word + "   ") * 10
        w = cap_width(words, 54, M, 800)

        def tg(fr, u, m=m, rot=rot, i=i):
            ox, oy = m(fr, u)
            sx, sy = rot_pt((60 if i % 2 else -60) * u, 0, rot, 0, 0)
            return ox + sx, oy + sy, 1, rot, 1
        s.say(words, (cx - w / 2, cy - 27, cx + w / 2, cy + 27), M, 800, ink, f"Cinta {i + 1} (texto)", geom=tg)
    wob = lambda u: 2.5 * math.sin(u * 2.2)  # noqa: E731
    phone(s, "Teléfono", "fx-dancer-02", 540, 990, 640, 1380,
          lambda fr, u: (-700 * (1 - k(fr, 6, 15)), 1100 * (1 - k(fr, 6, 15)), 1, 8 + 14 * (1 - k(fr, 6, 15)) + wob(u),
                         1.0 if fr >= 6 else 0), label="Tu video")
    return t


# --- I. DO YOU CREATE TRENDS?: the red bubble types its words and tilts, the stickers pop around it ----------------
def create_trends():
    D = dur_for(2.0, 2.2)
    t = _p("creas-tendencias", "Historia: ¿creas tendencias? en burbuja roja", "Story: do you create trends? red bubble",
           14008, D, ["pregunta", "rosa", "tendencia"])
    s = T(t, D)
    s.bg(PINK)
    tilt = lambda fr: -15 * k(fr, 12, 12)  # noqa: E731
    grow = lambda fr: 0.82 + 0.18 * k(fr, 12, 12)  # noqa: E731
    gm = lambda fr, u: (0, 0, bo(fr, 0, 8) * grow(fr), tilt(fr), 1)  # noqa: E731
    g = G(s, 540, 920, gm)
    g.shape("Burbuja (cola)", solid(RED), 400, 205, 110, 120, path=TAIL_R)
    g.shape("Burbuja", solid(RED), 0, 0, 1000, 470, radius=40)
    c1 = g.text("DO YOU", -330, -48, 84, INK, "Texto", maxw=190)
    c2 = g.text("CREATE", -320, 48, 84, INK, "Texto 2", maxw=210)
    c3 = g.text("TRENDS?", 110, 0, 300, INK, "Título", maxw=600)
    s.typed(c1, 0, stagger=0.06, duration=0.03)
    s.typed(c2, 9, stagger=0.05, duration=0.03)
    s.typed(c3, 15, stagger=0.06, duration=0.04)
    smiley(s, "Carita", 705, 320, 200, SKY, popm(9, 8, 0, 30))
    eye(s, "Ojo", 340, 530, 270, popm(12, 8, 15))
    ticket(s, "LIKE!", "LIKE!", 730, 1370, 400, 210, BLUE, WHITE, popm(21, 9, 12, 30))
    note(s, "Nota", 300, 1650, 250, popm(23, 8))
    dots(s, "Puntos", (765, 852, 940), 1705, 46, WHITE, (26, 28, 30))
    return art_except(t)


# --- J. NEW TEMPLATE FOR EVERYBODY: the photo opens, the title rises, the light-blue bubble types --------------------
def template_story():
    D = dur_for(2.2, 1.8)
    t = _p("plantilla", "Historia: plantilla para todos con foto", "Story: template for everybody with a photo", 14009, D,
           ["plantilla", "azul", "foto"])
    s = T(t, D)
    s.bg(BLUE)
    photo(s, "friends-09", (280, 205, 815, 1070), "Foto", radius=42,
          m=lambda fr, u: (0, 60 * (1 - k(fr, 0, 12)), 0.85 + 0.15 * k(fr, 0, 12), 0, k(fr, 0, 6)))
    play(s, "Play", 290, 200, 200, PINK, popm(36, 8), tri=INK, line=INK, angle=90)
    ticket(s, "Reto", "#CHALLENGE", 740, 1015, 330, 140, BLACK, WHITE, popm(24, 8, -10, -25), family=LG, cap=70)
    dots(s, "Puntos", (120, 195, 270), 1140, 40, RED, (33, 36, 39))
    s.title("NEW TEMPLATE", 95, 1230, 1400, WHITE, maxw=865, reveal=lambda fr: (0, 1200, W, 1420),
            shift=lambda fr: (0, 220 * (1 - k(fr, 6, 10))))
    c = s.title("FOR EVERYBODY", 95, 1450, 1505, PINK, "Texto", M, 800)
    s.typed(c, 12, stagger=0.03, duration=0.04)
    bubble(s, "Burbuja", 95, 1550, 965, 1735, SKY, lambda fr, u: (0, 0, bo(fr, 18, 9), 0, 1.0 if fr >= 18 else 0),
           tail=(220, 70, 70))
    c = s.title("Change the text in one click", 530, 1620, 1665, BLUE, "Texto 2", M, 700, align="center", maxw=790)
    s.typed(c, 27, stagger=0.03, duration=0.03)
    heart(s, "Corazón", 740, 1760, 150, RED, popm(57, 8, 10, 30))
    return t


# --- K. NEW VIDEO: NEW types big and goes up, a red panel rises with VIDEO, a phone with your video comes in -------
def new_video():
    D = dur_for(2.4, 2.0)
    t = _p("nuevo-video", "Historia: NEW VIDEO con teléfono", "Story: NEW VIDEO with a phone", 14010, D,
           ["video", "nuevo", "rojo", "teléfono"])
    s = T(t, D)
    s.bg(BLACK)
    up = lambda fr: -440 * k(fr, 22, 10)  # noqa: E731
    c = s.title("NEW", 572, 690, 1140, RED, align="center", maxw=570, geom=lambda fr, u: (0, up(fr), 1, 0, 1))
    s.typed(c, 0, stagger=0.1, duration=0.03)
    edge = lambda fr: 1930 - 970 * k(fr, 22, 10)  # noqa: E731
    s.rect("Panel", solid(RED), lambda fr, u: (-10, edge(fr), W + 10, H + 10))
    s.title("VIDEO", 520, 1180, 1650, INK, "Título 2", align="center", maxw=720, reveal=lambda fr: (0, edge(fr), W, H),
            shift=lambda fr: (0, 700 * (1 - k(fr, 23, 10))))
    phone(s, "Teléfono", "dance-03", 540, 1000, 580, 1280,
          lambda fr, u: (120 * (1 - k(fr, 38, 12)), 1300 * (1 - k(fr, 38, 12)), 1, 12 + 10 * (1 - k(fr, 38, 12)), 1.0 if fr >= 38 else 0),
          label="Tu video")
    play(s, "Play", 820, 250, 260, BLUE, popm(55, 8), angle=75)
    smiley(s, "Carita", 225, 935, 270, PINK, popm(58, 8, 30, 40))
    ticket(s, "Sello", "TRENDS", 745, 1640, 440, 190, SKY, INK, popm(61, 9, 18, 30))
    return t


# --- L. REMINDER: a white page folds into a card over your video, #DANCING drops in, the count goes up -------------
def reminder():
    D = dur_for(1.8, 2.4)
    t = _p("recordatorio", "Historia: recordatorio con encuesta sobre video", "Story: reminder poll over a video", 14011,
           D, ["encuesta", "recordatorio", "video"])
    s = T(t, D)
    photo(s, "friends-10", (0, 0, W, H), "Video", label="Tu video")
    top = lambda fr: 735 * k(fr, 6, 15)  # noqa: E731
    bot = lambda fr: 1920 - 675 * k(fr, 12, 15)  # noqa: E731
    side = lambda fr: k(fr, 15, 12)  # noqa: E731
    s.rect("Tarjeta", solid(WHITE), lambda fr, u: (155 * side(fr), top(fr), W - 140 * side(fr), bot(fr)),
           radius=30 * 1, base=None) if False else \
        s.obj("Tarjeta", solid(WHITE), lambda fr, u: ((155 * side(fr) + W - 140 * side(fr)) / 2, (top(fr) + bot(fr)) / 2,
                                                       W - 295 * side(fr), bot(fr) - top(fr), 0, 1), radius=30,
              base=(785, 510))
    rem_y = lambda fr: (830 - 0) * 1  # noqa: E731
    s.title("REMINDER", 540, 828, 862, INK, "Título", M, 800, align="center",
            geom=lambda fr, u: (0, 900 * (1 - k(fr, 6, 15)) * 0 + 0, 1, 0, 1))
    for i, line in enumerate(("Do you want to be", "a popular dancer?")):
        s.title(line, 540, 925 + 60 * i, 960 + 60 * i, INK, f"Texto {i + 1}" if i else "Texto", M, 600, align="center",
                geom=lambda fr, u: (0, 0, 1, 0, k(fr, 24, 6)))
    s.rect("Línea", solid("#F6B8D8"), lambda fr, u: (160, 1083, 160 + 770 * k(fr, 24, 8), 1086))
    s.rect("Línea 2", solid("#F6B8D8"), lambda fr, u: (548, 1085, 551, 1085 + 160 * k(fr, 26, 8)))
    s.title("YES", 350, 1150, 1185, BLUE, "Respuesta", M, 800, align="center", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 27, 6)))
    s.title("OF COURSE", 745, 1150, 1185, BLUE, "Respuesta 2", M, 800, align="center",
            geom=lambda fr, u: (0, 0, 1, 0, k(fr, 29, 6)))
    G(s, 920, 755, popm(30, 7)).shape("Insignia", solid(RED), 0, 0, 120, 120, kind="ellipse")
    num = s.title("16", 920, 732, 778, WHITE, "Número", M, 800, align="center",
                  geom=lambda fr, u: (0, 0, 1, 0, 1.0 if fr >= 32 else 0.0))
    num["textStyle"].update(counter=True, counterFrom=0, counterSeconds=2.2)
    ticket(s, "Etiqueta", "#DANCING", 475, 300, 470, 210, BLUE, WHITE,
           lambda fr, u: (-600 * (1 - k(fr, 18, 10)), -500 * (1 - k(fr, 18, 10)), 1, 18, 1.0 if fr >= 18 else 0),
           family=LG, cap=120)
    eye(s, "Ojo", 240, 1550, 270, popm(33, 8), white=SKY, pupil=BLACK, look=lambda fr, u: (-20 + 20 * math.sin(u * 2), 0))
    smiley(s, "Carita", 810, 1665, 210, PINK, popm(36, 8, 30, 40))
    return t


# --- M. TRULY NEW PLATFORM: the title rises, two phones with your videos come up, three blue eyes and hearts pop ---
def platform():
    D = dur_for(1.8, 2.2)
    t = _p("plataforma", "Historia: nueva plataforma con dos teléfonos", "Story: new platform with two phones", 14012, D,
           ["plataforma", "negro", "teléfono"])
    s = T(t, D)
    s.bg(BLACK)
    c = s.title("TRULY", 115, 150, 190, PINK, "Texto", M, 800)
    s.typed(c, 0, stagger=0.05, duration=0.04)
    s.title("NEW", 115, 225, 460, WHITE, maxw=255, reveal=lambda fr: (0, 200, W, 470), shift=lambda fr: (0, 270 * (1 - k(fr, 3, 9))))
    s.title("PLATFORM", 115, 485, 705, WHITE, "Título 2", maxw=580, reveal=lambda fr: (0, 470, W, 720),
            shift=lambda fr: (0, 250 * (1 - k(fr, 6, 9))))
    for i, (cx, cy, sample, at) in enumerate(((315, 1185, "kids-04", 15), (775, 1378, "portrait-06", 18))):
        phone(s, "Teléfono" if i == 0 else "Teléfono 2", sample, cx, cy, 380, 820,
              lambda fr, u, at=at, cy=cy: (0, (1990 - cy) * (1 - k(fr, at, 15)), 0.6 + 0.4 * k(fr, at, 15), 0,
                                           1.0 if fr >= at else 0), label="Tu video" if i == 0 else "Tu video 2")
    ticket(s, "Sello", "FOR USERS", 710, 250, 380, 165, SKY, INK, popm(27, 8, 15, 30), lines=["FOR USERS", "OF ANY AGE"],
           cap=34)
    for i in range(3):
        y = 535 + 145 * i
        at = 30 + 3 * i
        g = G(s, 855, y, popm(at, 7))
        g.shape(f"Ojo {i + 1}", solid(BLUE), 0, 0, 230, 110, path=EYE)
        g.shape(f"Ojo {i + 1} (pupila)", solid(BLACK), 0, 0, 82, 82, kind="ellipse")
        g.shape(f"Ojo {i + 1} (aro)", ring(BLUE, 8), 0, 0, 82, 82, kind="ellipse")
    heart(s, "Corazón", 340, 1715, 170, RED, popm(39, 8))
    heart(s, "Corazón 2", 340, 1880, 150, RED, popm(42, 8))
    return t


# --- N. TRENDS START HERE: a light-blue chain of tickets slides across, a pill with the social icon and a play pop ---
def start_here():
    D = dur_for(1.4, 2.4)
    t = _p("empieza-aqui", "Historia: las tendencias empiezan aquí", "Story: trends start here", 14013, D,
           ["tendencia", "azul", "boletos"])
    s = T(t, D)
    s.bg(BLUE)
    for i, word in enumerate(("EXACTLY", "VIDEO AGE", "IS EXACTLY", "NEW VIDEO")):
        y = 40 + 470 * i
        s.say(word, (-40, y, 1120, y + 430), LG, 400, BLUE, f"Fondo (texto {i + 1})", layers=hollow("#2A5CF0", 3),
              editable=False, geom=lambda fr, u, i=i: ((-1) ** i * 18 * u, 0, 1, 4, k(fr, 0, 9)))
    rot = 12
    step = 780

    def slide(fr, u):
        return -1400 * (1 - k(fr, 0, 12)) + 45 * u
    s.obj("Boletos", solid(SKY), lambda fr, u: (540 + rot_pt(slide(fr, u), 0, rot, 0, 0)[0],
                                               880 + rot_pt(slide(fr, u), 0, rot, 0, 0)[1], 3000, 330, rot, 1),
          base=(3000, 330))
    for j in range(-2, 3):
        base_x = j * step

        def at(fr, u, ox=0.0, oy=0.0, base_x=base_x):
            px, py = rot_pt(base_x + ox + slide(fr, u), oy, rot, 0, 0)
            return 540 + px, 880 + py
        for side in (-1,):
            s.obj(f"Boletos (muesca {j + 3})", solid(BLUE), lambda fr, u, at=at: (*at(fr, u, -400, 0), 100, 100, rot, 1),
                  kind="ellipse", base=(100, 100))
            s.obj(f"Boletos (línea {j + 3})", solid(BLUE), lambda fr, u, at=at: (*at(fr, u, -400, 0), 3, 330, rot, 1),
                  base=(3, 330))
        for li, line in enumerate(("TRENDS", "START HERE")):
            oy = -32 + 66 * li
            w = cap_width(line, 46, M, 800)
            x0 = 540 - w / 2

            def tg(fr, u, at=at, oy=oy):
                px, py = at(fr, u, 0, oy)
                return px - 540, py - (880 + oy), 1, rot, 1
            s.say(line, (x0, 880 + oy - 23, x0 + w, 880 + oy + 23), M, 800, INK,
                  "Texto" if (j == 0 and li == 0) else f"Texto {j + 3}-{li + 1}", geom=tg, editable=(j == 0))
    gp = G(s, 845, 222, popm(9, 8))
    gp.shape("Píldora", solid(WHITE), 0, 0, 360, 185, radius=92)
    gp.text("IN", -110, 0, 82, INK, "Píldora (texto)")
    note(s, "Nota", 925, 222, 150, popm(12, 8))
    play(s, "Play", 295, 1450, 240, RED, popm(15, 8))
    return t


# --- O. IT IS REALLY A NEW VIDEO AGE: the line types, a giant pink ticket slides up, the big words rise -------------
def video_age():
    D = dur_for(2.3, 2.0)
    t = _p("nueva-era", "Historia: una nueva era del video", "Story: a new video age", 14014, D,
           ["video", "rojo", "rosa"])
    s = T(t, D)
    s.bg(RED)
    tk = lambda fr, u: (0, 1700 * (1 - k(fr, 27, 15)), 1, 0, 1)  # noqa: E731
    g = G(s, 560, 1000, tk)
    g.shape("Boleto", solid(PINK), 0, 0, 900, 2500, rot0=-24)
    for ox, oy, d in ((-330, -690, 250), (390, 720, 290)):
        px, py = rot_pt(ox, oy, 0, 0, 0)
        g.shape("Boleto (muesca)", solid(RED), px, py, d, d, kind="ellipse")
    up = lambda fr: -80 * k(fr, 27, 9)  # noqa: E731
    c = s.title("IT IS REALLY A", 70, 820, 862, INK, "Texto", M, 800, geom=lambda fr, u: (0, up(fr), 1, 0, 1))
    s.typed(c, 0, stagger=0.065, duration=0.03)
    cap = 200 * min(1.0, 940 / cap_width("NEW VIDEO AGE", 200))
    x = 70
    for i, word in enumerate("NEW VIDEO AGE".split()):
        s.title(word, x, 1000 - cap, 1000, INK, "Título" if i == 0 else f"Título {i + 1}", reveal=lambda fr: (0, 780, W, 1010),
                shift=lambda fr, i=i: (0, 240 * (1 - k(fr, 30 + 3 * i, 9))))
        x += cap_width(word + " ", cap)
    bubble(s, "Burbuja", 770, 1065, 1010, 1190, WHITE, popm(33, 8), tail=(800, 50, 50), radius=20)
    g2 = G(s, 900, 1600, popm(45, 8))
    g2.shape("Flecha", solid(SKY), 0, 0, 170, 170, kind="ellipse")
    g2.shape("Flecha (aro)", ring(INK, 3), 0, 0, 140, 140, kind="ellipse")
    g2.shape("Flecha (triángulo)", solid(INK), 0, 0, 80, 80, path=tri_path(-120))
    ticket(s, "Etiqueta", "#TRENDS", 860, 560, 300, 130, BLUE, WHITE, popm(57, 9, 8, 25), family=LG, cap=72)
    return t


# --- P. VIRAL TRENDS: the giant red word comes out of the screen, the blue panel rises, the play turns --------------
def trends():
    D = dur_for(2.5, 1.8)
    t = _p("tendencias", "Historia: tendencias virales en rosa y azul", "Story: viral trends in pink and blue", 14015, D,
           ["tendencia", "rosa", "azul"])
    s = T(t, D)
    s.bg(PINK)
    zoom = lambda fr: 1 + 1.6 * (1 - k(fr, 0, 12))  # noqa: E731
    s.title("VIRAL", 540, 250, 710, RED, align="center", maxw=820, geom=lambda fr, u: (0, 0, zoom(fr), 0, 1))
    edge = lambda fr: 1930 - 970 * k(fr, 5, 10)  # noqa: E731
    s.rect("Panel", solid(BLUE), lambda fr, u: (-10, edge(fr), W + 10, H + 10))
    s.title("TRENDS", 545, 1210, 1670, WHITE, "Título 2", align="center", maxw=880, reveal=lambda fr: (0, edge(fr), W, H),
            shift=lambda fr: (0, 600 * (1 - k(fr, 6, 12))))
    play(s, "Play", 475, 195, 260, BLUE, popm(39, 8), angle=0, angle_from=(90, 66, 6))
    smiley(s, "Carita", 240, 980, 280, SKY, popm(42, 8, 0, 30))
    ticket(s, "Reto", "CHALLENGE", 800, 1660, 470, 200, PINK, RED, popm(42, 9, -20, -30), weight=700, cap=50)
    return t


TEMPLATES = [watch, promo_black, mission, collage_blue, promo_x, trendy, collage_black, tapes_phone, create_trends,
             template_story, new_video, reminder, platform, start_here, video_age, trends]
