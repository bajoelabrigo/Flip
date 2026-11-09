"""YOUTUBE PACK video 3 as Stock templates (yp3-*). See docs/plan-youtube-pack.md.

`pack youtube 3.mp4` (960×540 at 30 fps, laid out at 1920×1080): subscribe buttons clicked by a cursor (like and
bell that turn red, pills that swap «Subscribe» for «Subscribed», round bell buttons, channel avatar pills) and end
screens («Thanks for Watching!» with slots for the next videos, the channel avatar and social icons). Each piece was
studied on 10 fps sheets; study notes in tienda/plantillas/estudio-pack-youtube-3/NOTAS.md. Kit de YouTube ›
Elementos (buttons, transparent over the user's footage) and › Pantallas finales (own background).

The reference cuts into most buttons halfway (the pack's After Effects shots come before them); where the entrance
is not shown, the piece opens with its exit played forwards, which is how the pack's other buttons come in.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from scene import effect, gradient, keys
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import S, fill, grad, lin, poly, regular, ring, rot_pt, shadow

WHITE = "#FFFFFF"
M, P = "Montserrat", "Poppins"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium"),
               (400, "Regular")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"
f6._FILES[(P, 400)] = "fonts.basic/fonts/poppins/Poppins-Regular.ttf"

# --- glyphs (paths in a 100 × 100 box, stretched to the shape's box) ------------------------------------------------
THUMB = ("M 0 38 Q 0 34 4 34 L 23 34 Q 27 34 27 38 L 27 94 Q 27 98 23 98 L 4 98 Q 0 98 0 94 Z "
         "M 33 40 L 49 21 Q 55 13 55 5 Q 57 -1 63 1 Q 72 5 70 17 L 66 34 L 93 34 Q 100 34 100 41 Q 100 47 95 49 "
         "Q 100 52 99 58 Q 98 63 93 64 Q 98 67 96 73 Q 94 79 89 80 Q 93 84 90 90 Q 87 97 80 97 L 39 97 "
         "Q 33 97 33 91 Z")
BELL = ("M 44 12 Q 44 1 50 1 Q 56 1 56 12 Z "
        "M 50 9 C 28 9 21 28 21 48 L 21 67 L 8 82 Q 6 86 11 86 L 89 86 Q 94 86 92 82 L 79 67 L 79 48 C 79 28 72 9 50 9 Z "
        "M 39 90 L 61 90 Q 59 100 50 100 Q 41 100 39 90 Z")
RINGS = "M 20 10 Q 4 26 6 50 M 80 10 Q 96 26 94 50"  # stroked, in a box 1.3× the bell's width
HAND = ("M 30 0 Q 40 0 40 10 L 40 40 Q 44 34 52 36 Q 58 38 58 44 Q 62 38 70 40 Q 76 43 76 50 Q 80 45 88 47 "
        "Q 95 50 95 58 L 95 75 Q 95 90 85 100 L 40 100 Q 30 90 22 80 L 5 60 Q 0 52 7 48 Q 14 44 20 52 L 20 10 "
        "Q 20 0 30 0 Z")
PLAY = "M 0 0 L 100 50 L 0 100 Z"
FB = ("M 58 100 L 58 56 L 72 56 L 75 40 L 58 40 L 58 30 Q 58 22 66 22 L 76 22 L 76 6 Q 70 4 62 4 Q 40 4 40 28 "
      "L 40 40 L 26 40 L 26 56 L 40 56 L 40 100 Z")
IG = ("M 30 6 L 70 6 Q 94 6 94 30 L 94 70 Q 94 94 70 94 L 30 94 Q 6 94 6 70 L 6 30 Q 6 6 30 6 Z "
      "M 72 50 C 72 62 62 72 50 72 C 38 72 28 62 28 50 C 28 38 38 28 50 28 C 62 28 72 38 72 50 Z")
TW = ("M 100 19 Q 95 22 88 23 Q 95 18 97 11 Q 90 15 84 16 Q 77 8 66 9 Q 50 11 49 28 L 50 34 Q 27 33 10 13 "
      "Q 3 28 15 40 Q 10 40 6 38 Q 7 52 21 57 Q 16 59 11 58 Q 17 70 30 71 Q 17 81 0 80 Q 15 90 32 90 "
      "Q 70 90 86 55 Q 91 43 90 30 Q 96 25 100 19 Z")


def stroked(fill_colour, line, width):
    return [fill(fill_colour),
            {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "outside",
             "opacity": 1.0, "paint": {"kind": "solid", "color": "#ff" + line.lstrip("#").lower()}}]


def pts(*marks):
    """marks = (frame, x, y), ...: an eased path through them; f(fr) -> (x, y)."""
    def f(fr):
        if fr <= marks[0][0]:
            return marks[0][1], marks[0][2]
        for (a, xa, ya), (b, xb, yb) in zip(marks, marks[1:]):
            if fr <= b:
                q = k(fr, a, b - a)
                return xa + (xb - xa) * q, ya + (yb - ya) * q
        return marks[-1][1], marks[-1][2]
    return f


def pop(fr, at, n=6, over=0.12):
    """0 → 1 with a small overshoot from frame at over n frames."""
    if fr <= at:
        return 0.0
    q = (fr - at) / n
    if q >= 1.6:
        return 1.0
    if q <= 1.0:
        return k(fr, at, n) * (1 + over * q)
    return 1 + over * (1 - (q - 1) / 0.6)


def out3(q):
    return 1 - (1 - q) ** 3


class B(S):
    """A piece whose frames run forwards (fr = u × FPS); each element codes its own exit."""

    def frame(self, u):
        return u * FPS

    def typed(self, clip, at, stagger=0.06, duration=0.05, preset="typewriter", order="forward", unit="character"):
        """As S.typed, but the way out is left to the piece's own exit (it plays only in the last instant)."""
        S.typed(self, clip, at, stagger, duration, preset, order, unit)
        clip["textStyle"]["animation"]["out"].pop("delayUs", None)

    def icon(self, name, path, layers, geom, aspect=1.0, even_odd=False):
        """A glyph: geom(fr, u) = (cx, cy, height, rot, op); width = height × aspect."""
        c = self.obj(name, layers, lambda fr, u: (lambda g: (g[0], g[1], g[2] * aspect, g[2], g[3], g[4]))(geom(fr, u)),
                     path=path)
        c["shapeStyle"]["customEvenOdd"] = even_odd
        return c

    def cursor(self, at, name="Cursor", size=120):
        """A white pointing hand whose fingertip follows at(fr) = (x, y, press 0..1, op)."""
        def g(fr, u):
            x, y, press, op = at(fr)
            sc = 1 - 0.18 * press
            w, h = size * 0.85 * sc, size * sc
            cx, cy = rot_pt(x + w * 0.2, y + h / 2, -14, x, y)
            return cx, cy, w, h, -14, op
        return self.obj(name, ring(WHITE, 6), g, path=HAND)

    def burst(self, name, cx, cy, at, colour, n=10, r=90, size=10, life=14, seed=0, r0=0.0):
        """Specks thrown out from (cx, cy) at frame at, fading as they go."""
        for i in range(n):
            a = math.radians(360 * i / n + 17 * seed + (i % 3) * 9)
            rr = r * (0.7 + 0.3 * ((i * 7 + seed) % 5) / 4) - r0
            sz = size * (0.6 + 0.4 * ((i * 3 + seed) % 4) / 3)
            self.obj(f"{name} {i + 1}", solid(colour), lambda fr, u, a=a, rr=rr, sz=sz: (
                cx + math.cos(a) * (r0 + rr * out3(lin(fr, at, life))), cy + math.sin(a) * (r0 + rr * out3(lin(fr, at, life))),
                sz, sz, 0,
                (1.0 if at < fr else 0.0) * (1 - k(fr, at + life * 0.4, life * 0.6))), kind="ellipse")

    def avatar(self, sample, geom, name="Foto", label="Tu foto"):
        """A round photo: geom(fr, u) = (cx, cy, diameter, op)."""
        g = [(u, geom(fr, u)) for u, fr in self.each()]
        d = max(1.0, max(v[2] for _, v in g))
        box = Box(960 - d / 2, 540 - d / 2, d, d)
        motion = [(u, {"sx": max(1e-4, v[2] / d), "sy": max(1e-4, v[2] / d), "dx": v[0] - 960, "dy": v[1] - 540},
                   "linear") for u, v in g]
        track = self.t.track("video", name)
        clip = self.t.photo(track, sample, 0.0, self.dur, box, motion, label=label)
        self.t.mask(track, clip, "ellipse")
        if any(v[3] < 0.999 for _, v in g):
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, v[3])), 4), "linear") for u, v in g])
        return clip

    def picture(self, sample, geom, name="Foto", label="Tu video"):
        """A rectangular photo slot: geom(fr, u) = (cx, cy, w, h, op)."""
        g = [(u, geom(fr, u)) for u, fr in self.each()]
        bw, bh = max(1.0, max(v[2] for _, v in g)), max(1.0, max(v[3] for _, v in g))
        box = Box(960 - bw / 2, 540 - bh / 2, bw, bh)
        motion = [(u, {"sx": max(1e-4, v[2] / bw), "sy": max(1e-4, v[3] / bh), "dx": v[0] - 960, "dy": v[1] - 540},
                   "linear") for u, v in g]
        clip = self.t.photo(self.t.track("video", name), sample, 0.0, self.dur, box, motion, label=label)
        if any(v[4] < 0.999 for _, v in g):
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, v[4])), 4), "linear") for u, v in g])
        return clip


class E(B):
    """An end screen: the entrance, a hold, and the entrance backwards at 2.5× (as the title slides)."""

    def frame(self, u):
        return S.frame(self, u)

    typed = S.typed


def social(s, kind, cx, cy, d, disc, glyph, size=lambda fr: 1.0, op=lambda fr, u: 1.0, ring_only=False):
    """A round social button: a disc (or ring) of colour `disc` with the network's glyph in `glyph`."""
    name = {"fb": "Facebook", "ig": "Instagram", "tw": "Twitter", "yt": "YouTube"}[kind]
    if disc:
        s.obj(f"{name} (fondo)", ring(disc, 4) if ring_only else solid(disc),
              lambda fr, u: (cx, cy, d * size(fr), d * size(fr), 0, op(fr, u)), kind="ellipse", base=(d, d))

    def g(h):
        return lambda fr, u: (cx, cy, h * size(fr), 0, op(fr, u))
    if kind == "fb":
        s.icon(name, FB, solid(glyph), g(d * 0.6), aspect=0.62)
    elif kind == "tw":
        s.icon(name, TW, solid(glyph), g(d * 0.46), aspect=1.22)
    elif kind == "ig":
        s.icon(name, IG, ring(glyph, max(2.0, d * 0.07)), g(d * 0.5))
        s.obj(f"{name} (punto)", solid(glyph), lambda fr, u: (cx + d * 0.13 * size(fr), cy - d * 0.13 * size(fr),
                                                              d * 0.07 * size(fr), d * 0.07 * size(fr), 0, op(fr, u)),
              kind="ellipse")
    elif kind == "yt":
        s.obj(name, solid(glyph), lambda fr, u: (cx, cy, d * 0.56 * size(fr), d * 0.4 * size(fr), 0, op(fr, u)),
              radius=d * 0.1, base=(d * 0.56, d * 0.4))
        s.obj(f"{name} (play)", solid(disc or WHITE), lambda fr, u: (cx + d * 0.02 * size(fr), cy, d * 0.16 * size(fr),
                                                                    d * 0.18 * size(fr), 0, op(fr, u)), path=PLAY)


def neo_layers(colour, depth=14, dark="#A3B1C6"):
    """Soft-plastic look: a dark shadow down-right, a white glow up-left."""
    return [shadow(dark, depth, depth, depth * 2.2, 0.75),
            {"id": "glow", "kind": "shadow", "enabled": True, "paint": {"kind": "solid", "color": "#ffffffff"},
             "offsetX": -depth, "offsetY": -depth, "blur": depth * 2.2, "opacity": 0.9},
            fill(colour)]


def bg(s, layers, name="Fondo"):
    return s.rect(name, layers, lambda fr, u: (-10, -10, 1930, 1090))


def _btn(id, es, en, order, dur, tags=(), thumb=None):
    return wide(f"yp3-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:elementos", "youtube", "suscribirse", "botón"] + list(tags),
                thumb_at=thumb if thumb is not None else round(dur * 0.6, 1))


def _end(id, es, en, order, dur, tags=(), thumb=None):
    return wide(f"yp3-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:pantallas-finales", "youtube", "pantalla final", "suscribirse"] + list(tags),
                thumb_at=thumb if thumb is not None else round(dur * 0.6, 1))


def bell_and_like(s, lx, bx, cy, h, like_on, bell_on, size=lambda fr: 1.0, bsize=None, sway=lambda fr: 0.0,
                  rings_on=None, grey="#5B5B5B", red="#DB2128"):
    """The thumbs-up at lx and the bell at bx (centres, height h), grey until like_on / bell_on (frames)."""
    bsize = bsize or size
    for colour, name, when in ((grey, "Me gusta (gris)", lambda fr: 1.0 if fr < like_on else 0.0),
                               (red, "Me gusta", lambda fr: 1.0 if fr >= like_on else 0.0)):
        def lg(fr, u, when=when):
            pp = 1 + 0.18 * math.sin(math.pi * lin(fr, like_on, 6)) if fr >= like_on else 1.0
            tilt = -12 * math.sin(math.pi * lin(fr, like_on, 8)) if fr >= like_on else 0.0
            return lx, cy, h * size(fr) * pp, tilt, when(fr)
        s.icon(name, THUMB, solid(colour), lg, aspect=1.25)
    for colour, name, when in ((grey, "Campana (gris)", lambda fr: 1.0 - k(fr, bell_on, 4)),
                               (red, "Campana", lambda fr: k(fr, bell_on, 4))):
        s.icon(name, BELL, solid(colour), lambda fr, u, when=when: (bx, cy, h * 1.04 * bsize(fr), sway(fr), when(fr)),
               aspect=0.92)
    on = rings_on if rings_on is not None else bell_on
    s.icon("Campana (ondas)", RINGS, ring(red, 9), lambda fr, u: (bx, cy - h * 0.12, h * 0.75 * bsize(fr),
                                                                  sway(fr) * 0.4, k(fr, on, 4)), aspect=1.7)


# --- 1. Like, bell and a red «Subscribe» clicked by the cursor (29.2–33.0) --------------------------------------
def subscribe_red():
    D = 6.0
    t = _btn("suscribirse-rojo", "Botón: suscribirse rojo con me gusta y campana",
             "Button: red subscribe with like and bell", 12500, D, ["me gusta", "campana", "cursor"], thumb=4.0)
    s = B(t, D)
    END = 160
    x0, x1, y0, y1 = 638, 1220, 614, 750
    cx = (x0 + x1) / 2

    def pill(fr, u):
        w = (x1 - x0) * k(fr, 0, 9) * (1 - k(fr, END + 3, 10))
        return cx, (y0 + y1) / 2, w, y1 - y0, 0, 1.0 if w > 1 else 0.0
    s.obj("Botón", grad("#B11A1B", "#E9242D", 0), pill, radius=24, base=(x1 - x0, y1 - y0))
    rect = lambda fr: (cx - pill(fr, 0)[2] / 2, y0, cx + pill(fr, 0)[2] / 2, y1)  # noqa: E731
    swap = lambda fr: k(fr, 66, 6)  # noqa: E731
    s.say("Subscribe", (744, 664, 1112, 722), M, 800, WHITE, "Texto", reveal=rect,
          shift=lambda fr: (-(x1 - x0) * swap(fr), 0))
    s.say("Subscribed", (716, 664, 1126, 722), M, 800, WHITE, "Texto (suscrito)", reveal=rect,
          shift=lambda fr: ((x1 - x0) * (1 - swap(fr)), 0))
    icon_size = lambda fr: pop(fr, 4, 6) * (1 - k(fr, END, 6))  # noqa: E731
    bell_size = lambda fr: pop(fr, 6, 6) * (1 - k(fr, END + 6, 6))  # noqa: E731
    sway = lambda fr: 18 * math.sin(2 * math.pi * lin(fr, 66, 24) * 2.5) * (1 - lin(fr, 66, 24)) if fr > 66 else 0  # noqa: E731
    bell_and_like(s, 815, 1034, 530, 136, 30, 66, size=icon_size, bsize=bell_size, sway=sway)
    s.burst("Chispa", 815, 520, 30, "#E2262E", n=12, r=110, size=12, life=16)
    s.burst("Chispa (campana)", 1034, 520, 78, "#E2262E", n=10, r=120, size=10, life=18, seed=3)
    cur = pts((12, 1260, 980), (27, 812, 548), (54, 812, 548), (60, 1040, 560), (75, 1040, 560), (79, 1080, 700),
              (87, 1110, 1150))
    s.cursor(lambda fr: (*cur(fr), max(math.sin(math.pi * lin(fr, 28, 5)), math.sin(math.pi * lin(fr, 63, 5))),
                         k(fr, 12, 3)))
    return t


# --- 2. A round bell button: clicked, the bell turns white and «Subscribed» slides out of it (33.4–38.7) ------------
def bell_round():
    D = 5.8
    t = _btn("campana-redonda", "Botón: campana redonda que se vuelve «Subscribed»",
             "Button: round bell that turns into «Subscribed»", 12501, D, ["campana", "cursor"], thumb=3.6)
    s = B(t, D)
    pos = lambda fr: 956 - 264 * k(fr, 75, 12) + 264 * k(fr, 145, 6)  # noqa: E731
    size = lambda fr: 256 * pop(fr, 3, 4, 0.08) * (1 - k(fr, 158, 8))  # noqa: E731
    s.obj("Botón", grad("#BD1D20", "#D72026", 0), lambda fr, u: (pos(fr), 535, size(fr), size(fr), 0, 1),
          kind="ellipse", base=(256, 256))
    sway = lambda fr: 16 * math.sin(2 * math.pi * lin(fr, 33, 24) * 2.5) * (1 - lin(fr, 33, 24)) if fr > 33 else 0  # noqa: E731
    sc = lambda fr: size(fr) / 256  # noqa: E731
    s.icon("Campana (oscura)", BELL, solid("#9A1713"), lambda fr, u: (pos(fr), 532, 140 * sc(fr), 0,
                                                                     1 - k(fr, 33, 4)), aspect=0.92)
    s.icon("Campana", BELL, solid(WHITE), lambda fr, u: (pos(fr), 532, 140 * sc(fr), sway(fr), k(fr, 33, 4)),
           aspect=0.92)
    s.icon("Campana (ondas)", RINGS, ring(WHITE, 9), lambda fr, u: (pos(fr), 514, 108 * sc(fr), sway(fr) * 0.4,
                                                                   k(fr, 33, 4)), aspect=1.7)
    s.burst("Destello", 956, 535, 36, "#D8D8D8", n=12, r=200, size=16, life=20, r0=120)
    back = lambda fr: 1 - k(fr, 75, 12) + k(fr, 145, 6)  # noqa: E731
    s.say("Subscribed", (870, 502, 1284, 560), M, 700, WHITE, "Texto", align="left",
          reveal=lambda fr: (pos(fr) + 110, 0, 1920, 1080), shift=lambda fr: (-264 * back(fr), 0),
          op=lambda fr, u: 1.0 if 75 < fr < 152 else 0.0)
    cur = pts((24, 1010, 760), (32, 972, 590), (44, 972, 590), (58, 1010, 900))
    s.cursor(lambda fr: (*cur(fr), math.sin(math.pi * lin(fr, 31, 5)), k(fr, 24, 3) * (1 - k(fr, 54, 4))))
    return t


# --- 3. Channel avatar with a red pill: «yourchannel» and a «Subscribe» box the cursor clicks (38.9–42.0) ----------
def avatar_pill():
    D = 5.8
    t = _btn("avatar-rojo", "Botón: avatar del canal con suscribirse rojo",
             "Button: channel avatar with red subscribe", 12502, D, ["avatar", "campana", "cursor"], thumb=3.6)
    s = B(t, D)
    X = 2.5
    ex = lambda fr, at, n: k(fr, at, n)  # noqa: E731
    out = lambda fr, a: k(fr, 150 + a, 30 / X)  # noqa: E731
    cx, cy = 695, 570
    reach = lambda fr: 800 + 632 * k(fr, 9, 14) * (1 - out(fr, 6))  # noqa: E731
    s.rect("Barra", grad("#A81A20", "#DA2027", 0), lambda fr, u: (780, 428, reach(fr), 712),
           op=lambda fr, u: 1.0 if reach(fr) > 802 else 0.0, radius=20)
    ring_d = lambda fr: (264 * k(fr, 0, 3) + 96 * k(fr, 3, 6)) * (1 - out(fr, 12))  # noqa: E731
    s.obj("Aro", solid("#A8171C"), lambda fr, u: (cx, cy, ring_d(fr), ring_d(fr), 0, 1), kind="ellipse",
          base=(360, 360))
    s.avatar("fx-woman-02", lambda fr, u: (cx, cy, max(0.5, 320 * k(fr, 3, 7) * (1 - out(fr, 12))), 1.0),
             label="Tu foto de perfil")
    s.obj("Punto", solid(WHITE), lambda fr, u: (cx, cy, 30 * k(fr, 1, 2), 30 * k(fr, 1, 2), 0, 1 - k(fr, 4, 3)),
          kind="ellipse")
    name = s.say("yourchannel", (1002, 483, 1346, 545), M, 700, WHITE, "Canal", align="left",
                 op=lambda fr, u: 1 - out(fr, 0))
    s.typed(name, 12, stagger=0.015, duration=0.03)
    for i, side in enumerate(([(1175, 660), (990, 660), (990, 560), (1176, 560)],
                              [(1175, 660), (1360, 660), (1360, 560), (1174, 560)])):
        box = s.outline(f"Recuadro {i + 1}", side, 5, WHITE, at=15, n=12, closed=False)
        s.fade(box, lambda fr: 1 - out(fr, 0))
    swap = lambda fr: k(fr, 45, 6)  # noqa: E731
    op_in = lambda fr, u: k(fr, 24, 6) * (1 - out(fr, 0))  # noqa: E731
    s.icon("Campana", BELL, solid(WHITE), lambda fr, u: (1059, 612, 64, 14 * math.sin(math.pi * 4 * lin(fr, 45, 20))
                                                          * (1 - lin(fr, 45, 20)), op_in(fr, u)), aspect=0.92)
    s.icon("Campana (ondas)", RINGS, ring(WHITE, 5), lambda fr, u: (1059, 604, 48, 0, k(fr, 45, 4) * op_in(fr, u)),
           aspect=1.7)
    inner = lambda fr: (1096, 562, 1356, 658)  # noqa: E731
    s.say("Subscribe", (1105, 597, 1306, 628), M, 700, WHITE, "Botón", align="left", reveal=inner,
          shift=lambda fr: (-260 * swap(fr), 0), op=op_in)
    s.say("Subscribed", (1105, 597, 1330, 628), M, 700, WHITE, "Botón (suscrito)", align="left", reveal=inner,
          shift=lambda fr: (260 * (1 - swap(fr)), 0), op=op_in)
    cur = pts((30, 1150, 860), (36, 1074, 640), (64, 1074, 640), (72, 1100, 900))
    s.cursor(lambda fr: (*cur(fr), math.sin(math.pi * lin(fr, 40, 5)), k(fr, 30, 3) * (1 - k(fr, 68, 4))))
    del ex
    return t



# --- 4. Soft grey end screen: two video frames, the round avatar, the name and a «Subscribe» pill (42.0–44.9) ------
def end_soft():
    D = 5.2
    t = _end("final-gris", "Pantalla final: gris suave con dos videos y avatar",
             "End screen: soft grey with two videos and avatar", 12503, D, ["gris", "neumórfico"])
    s = E(t, D)
    BG = "#E0E5EC"
    bg(s, solid(BG))
    for i, (y0, y1, sample) in enumerate(((182, 510, "h-nature-02"), (580, 906, "h-nature-04"))):
        cy = (y0 + y1) / 2
        sz = lambda fr, i=i: 0.06 + 0.94 * k(fr, i, 9)  # noqa: E731
        s.obj(f"Marco {i + 1}", neo_layers(BG), lambda fr, u, cy=cy, sz=sz, h=y1 - y0: (624, cy, 584 * sz(fr), h * sz(fr),
                                                                                    0, 1), base=(584, y1 - y0))
        s.picture(sample, lambda fr, u, cy=cy, h=y1 - y0, i=i: (624, cy, 556, h - 28, k(fr, 12 + 3 * i, 15)),
                  name=f"Video {i + 1}", label=f"Video {i + 1}")
    s.obj("Aro", neo_layers(BG, 12), lambda fr, u: (1434, 368, 384, 384, 0, 1), kind="ellipse")
    s.avatar("fx-face-05", lambda fr, u: (1434, 368, 340, k(fr, 6, 9)), label="Tu foto de perfil")
    s.say("Your Channel", (1210, 600, 1656, 650), M, 700, "#111111", "Canal", reveal=lambda fr: (0, 580, 1920, 664),
          shift=lambda fr: (0, 70 * (1 - k(fr, 9, 6))))
    s.say("www.yourweb.com", (1262, 680, 1616, 700), M, 500, "#4A4F5A", "Web",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 9, 6)))
    s.obj("Botón", neo_layers(BG, 10), lambda fr, u: (1465, 838, 430 * k(fr, 12, 6), 72, 0, 1), radius=36,
          base=(430, 72))
    c = s.say("Subscribe", (1340, 824, 1590, 852), M, 800, "#111111", "Botón")
    s.typed(c, 15, stagger=0.04, duration=0.04)
    return t


# --- 5. Pink end screen: a pink slant slides in; «Thanks for Watching!», next video, avatar and networks (44.9–47.1)
def end_pink():
    D = 5.6
    t = _end("final-rosa", "Pantalla final: rosa con «Thanks for Watching!»",
             "End screen: pink «Thanks for Watching!»", 12504, D, ["rosa", "redes"])
    s = E(t, D)
    bg(s, solid("#262626"))
    for i in range(7):
        s.obj(f"Raya {i + 1}", solid("#2B2B2B"), lambda fr, u, i=i: (-200 + 330 * i, 540, 120, 1500, -24, 1))
    off = lambda fr: 1500 * (1 - k(fr, 6, 12))  # noqa: E731
    s.obj("Panel", grad("#FF7590", "#FC7AA8", 90), lambda fr, u: (1605 + off(fr), 540, 1470, 1100, 0, 1),
          path=poly([(0, 0), (100, 0), (100, 100), (28.6, 100)]))
    s.obj("Aro", [shadow("#C2405F", 0, 14, 30, 0.6), fill("#FF8FAA")],
          lambda fr, u: (1476, 370, 340 * pop(fr, 12, 5), 340 * pop(fr, 12, 5), 0, 1), kind="ellipse", base=(340, 340))
    s.avatar("fx-face-03", lambda fr, u: (1476, 370, 300, k(fr, 36, 6)), label="Tu foto de perfil")
    arrow = [(1290, 700), (1220, 650), (1190, 560), (1205, 460), (1262, 382)]
    s.outline("Flecha", arrow, 5, WHITE, at=27, n=9, closed=False)
    s.outline("Flecha (punta)", [(1234, 392), (1262, 382), (1262, 412)], 5, WHITE, at=34, n=3, closed=False)
    s.say("your channel", (1322, 578, 1632, 616), M, 800, "#1A1A1A", "Canal",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 15, 4)))
    s.say("second text here", (1358, 626, 1588, 650), M, 500, WHITE, "Texto",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 24, 6)))
    s.obj("Botón", solid(WHITE), lambda fr, u: (1488, 709, 324 * k(fr, 24, 6), 74, 0, 1), radius=37, base=(324, 74))
    s.say("Click to Subscribe", (1366, 698, 1610, 720), M, 700, "#FF7693", "Botón",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 28, 4)))
    for i, (kind, x) in enumerate((("fb", 1394), ("ig", 1488), ("tw", 1586))):
        social(s, kind, x, 826, 84, WHITE, "#1A1A1A", size=lambda fr, i=i: pop(fr, 15 + 3 * i, 5))
    for i, (x, sign, a) in enumerate(((204, 1, 0), (964, -1, 1))):
        s.rect(f"Corchete {i + 1}", solid(WHITE),
               lambda fr, u, x=x, a=a: (x - 2, 494 if a == 0 else 948 - 454 * k(fr, 12, 6),
                                        x + 2, 494 + 454 * k(fr, 12, 6) if a == 0 else 948))
        for j, y in enumerate((494, 946)):
            s.rect(f"Corchete {i + 1}.{j + 1}", solid(WHITE),
                   lambda fr, u, x=x, sign=sign, y=y: (min(x, x + sign * 38), y - 2, max(x, x + sign * 38), y + 2),
                   op=lambda fr, u: k(fr, 12, 3))
    s.picture("h-nature-04", lambda fr, u: (584, 724, 688, 388, k(fr, 21, 6)), name="Video", label="Siguiente video")
    s.rect("Siguiente", solid("#FF7693"), lambda fr, u: (575 - 173 * k(fr, 18, 6), 428, 575 + 173 * k(fr, 18, 6), 494))
    s.say("Next Video", (482, 448, 668, 474), M, 700, "#2B2124", "Siguiente (texto)",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 22, 4)))
    c = s.say("Thanks for", (400, 196, 746, 250), M, 700, WHITE, "Título")
    s.typed(c, 15, stagger=0.03, duration=0.15, preset="fade", order="random")
    c = s.say("Watching!", (334, 268, 826, 350), M, 800, WHITE, "Título 2")
    s.typed(c, 15, stagger=0.04, duration=0.15, preset="fade", order="random")
    return t



# --- 6. Red blobs end screen: two red blobs sweep in; avatar, slogan, next video and networks (47.1–50.3) ----------
def end_red_blobs():
    D = 5.8
    t = _end("final-manchas-rojas", "Pantalla final: manchas rojas con avatar y siguiente video",
             "End screen: red blobs with avatar and next video", 12505, D, ["rojo", "redes"])
    s = E(t, D)
    bg(s, solid("#151515"))
    left = poly([(0, 0), (100, 0), (96, 18), (84, 40), (70, 62), (54, 80), (36, 92), (18, 94), (6, 88), (0, 84)])
    right = ("M 34 0 L 100 0 L 100 100 L 8 100 C 0 90 0 72 6 58 C 12 44 18 36 20 24 C 22 10 26 2 34 0 Z")
    s.obj("Mancha", [shadow("#000000", 0, 20, 60, 0.45), fill("#A3131A")],
          lambda fr, u: (650 - 1500 * (1 - k(fr, 3, 12)), 470, 1300, 940, 0, 1), path=left)
    s.obj("Mancha 2", [shadow("#3A0003", -24, 0, 60, 0.6), grad("#B3161C", "#8E0E13", 160)[0]],
          lambda fr, u: (1345 + 900 * (1 - k(fr, 6, 12)), 540, 1330, 1160, 6 * (1 - k(fr, 6, 12)), 1), path=right)
    s.obj("Aro", [shadow("#4A0004", 0, 10, 26, 0.6), fill("#8A0C10")],
          lambda fr, u: (392, 356, 384 * pop(fr, 15, 6), 384 * pop(fr, 15, 6), 0, 1), kind="ellipse", base=(384, 384))
    s.avatar("fx-face-05", lambda fr, u: (392, 356, 336 * k(fr, 18, 4), k(fr, 27, 9)), label="Tu foto de perfil")
    c = s.say("your channel", (230, 600, 552, 640), M, 700, WHITE, "Canal")
    s.typed(c, 18, stagger=0.03, duration=0.12, preset="fade", order="random")
    s.rect("Lema (fondo)", solid(WHITE), lambda fr, u: (393 - 161 * k(fr, 18, 6), 658, 393 + 161 * k(fr, 18, 6), 708))
    s.say("slogan here", (280, 670, 504, 696), M, 700, "#8A0C10", "Lema", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 22, 4)))
    s.rect("Video (marco)", [shadow("#3A0003", 0, 16, 40, 0.6), fill("#A8141A")],
           lambda fr, u: (1400 - 370 * k(fr, 33, 9), 526 - 210 * k(fr, 33, 9), 1400 + 370 * k(fr, 33, 9),
                          526 + 210 * k(fr, 33, 9)), op=lambda fr, u: k(fr, 33, 3))
    s.picture("h-nature-03", lambda fr, u: (1413, 519, 710, 398, k(fr, 42, 9)), name="Video", label="Siguiente video")
    s.rect("Siguiente", [shadow("#3A0003", 0, 12, 30, 0.5), fill("#A8141A")],
           lambda fr, u: (1226, 736, 1586, 736 + 102 * k(fr, 42, 6)))
    s.say("next video", (1300, 776, 1518, 804), M, 700, WHITE, "Siguiente (texto)",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 46, 4)))
    for i, (kind, x) in enumerate((("fb", 1242), ("tw", 1404), ("ig", 1564))):
        sz = lambda fr, i=i: pop(fr, 24 + 3 * i, 5)  # noqa: E731
        s.obj(f"Red {i + 1}", solid(WHITE), lambda fr, u, x=x, sz=sz: (x, 946, 104 * sz(fr), 104 * sz(fr), 0, 1),
              radius=26, base=(104, 104))
        social(s, kind, x, 946, 112, None, "#8A0C10", size=sz)
    return t


def waves(s, colour, n=7, amp=28, tilt=-8):
    """The white page's soft diagonal waves."""
    for i in range(n):
        pts_ = [(x, 50 + 40 * math.sin(x / 100 * 2 * math.pi * 1.5 + i)) for x in range(0, 101, 5)]
        pts_ += [(x, 50 + 40 * math.sin(x / 100 * 2 * math.pi * 1.5 + i) + 14) for x in range(100, -1, -5)]
        s.obj(f"Onda {i + 1}", solid(colour), lambda fr, u, i=i: (960, -60 + 200 * i, 2400, amp * 5, tilt, 1),
              path=poly(pts_))


# --- 7. Purple card end screen: «Thanks for watching!», avatar, «Subscribe» and two videos (50.3–52.7) -------------
def end_purple_card():
    D = 5.6
    t = _end("final-tarjeta-morada", "Pantalla final: tarjeta morada con dos videos",
             "End screen: purple card with two videos", 12506, D, ["morado"])
    s = E(t, D)
    bg(s, solid("#F4F4F4"))
    waves(s, "#E8E8E8")
    w = lambda fr: 1766 * k(fr, 0, 6)  # noqa: E731
    h = lambda fr: 300 + 626 * k(fr, 6, 9)  # noqa: E731
    s.obj("Tarjeta", [shadow("#6A6A8A", 0, 30, 60, 0.45), grad("#7B5BD0", "#6B80EE", 0)[0]],
          lambda fr, u: (967, 547, w(fr), h(fr), 0, 1.0 if w(fr) > 2 else 0.0), radius=150, base=(1766, 926))
    for i, (x0, x1, sample) in enumerate(((298, 878, "h-nature-02"), (1060, 1642, "sunset-02"))):
        cx = (x0 + x1) / 2
        hh = lambda fr: 344 * k(fr, 6, 6)  # noqa: E731
        ww = lambda fr, i=i: 40 + (x1 - x0 - 40) * k(fr, 12 + 2 * i, 8)  # noqa: E731
        s.obj(f"Marco {i + 1}", [shadow("#3B2F8A", 0, 10, 24, 0.45), fill("#6E6FE0")],
              lambda fr, u, cx=cx, ww=ww: (cx, 934 - hh(fr) / 2, ww(fr), hh(fr), 0, 1.0 if fr > 6 else 0.0),
              base=(x1 - x0, 344))
        s.picture(sample, lambda fr, u, cx=cx, x0=x0, x1=x1, i=i: (cx, 760, x1 - x0 - 36, 308, k(fr, 15 + 3 * i, 12)),
                  name=f"Video {i + 1}", label=f"Video {i + 1}")
    s.obj("Aro", [shadow("#3B2F8A", 0, 12, 30, 0.5), fill("#7C78E6")],
          lambda fr, u: (960, 348, 340 * pop(fr, 9, 6), 340 * pop(fr, 9, 6), 0, 1), kind="ellipse", base=(340, 340))
    s.avatar("h-nature-05", lambda fr, u: (960, 348, 296, k(fr, 12, 9)), label="Tu foto de perfil")
    c = s.say("Thanks", (334, 280, 664, 336), M, 800, WHITE, "Título")
    s.typed(c, 18, stagger=0.04, duration=0.15, preset="fade", order="random")
    c = s.say("for watching!", (276, 362, 722, 412), M, 700, WHITE, "Título 2")
    s.typed(c, 21, stagger=0.03, duration=0.15, preset="fade", order="random")
    c = s.say("your channel", (1262, 270, 1630, 310), M, 700, WHITE, "Canal")
    s.typed(c, 18, stagger=0.03, duration=0.15, preset="fade", order="random")
    s.say("slogan here", (1320, 326, 1572, 350), M, 500, "#E4E0FF", "Lema", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 24, 6)))
    s.obj("Botón", solid(WHITE), lambda fr, u: (1445, 432, 390 * k(fr, 15, 6), 100, 0, 1), radius=50, base=(390, 100))
    s.say("Subscribe", (1352, 410, 1556, 446), M, 700, "#6B6FD8", "Botón", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 19, 4)))
    s.outline("Flecha", [(1240, 492), (1200, 530), (1140, 552), (1080, 550), (1046, 540)], 4, WHITE, at=27, n=9,
              closed=False)
    s.outline("Flecha (punta)", [(1066, 522), (1046, 540), (1070, 554)], 4, WHITE, at=35, n=3, closed=False)
    return t


# --- 8. Pink «next video» end screen: blocks across the top and bottom, a framed video, ringed avatar (52.7–54.1) ---
def end_pink_next():
    D = 5.0
    t = _end("final-rosa-siguiente", "Pantalla final: rosa con «next video» y bloques",
             "End screen: pink «next video» with blocks", 12507, D, ["rosa", "bloques"])
    s = E(t, D)
    bg(s, solid("#1A1A1A"))
    for row, (y0, y1) in enumerate(((0, 172), (870, 1080))):
        for j in range(9):
            x = (j * 233 + row * 97) % 2100 - 90
            hh = (y1 - y0) * (0.35 + 0.25 * ((j * 5 + row) % 3))
            yy = y0 + ((j * 37 + row * 11) % max(1, int(y1 - y0 - hh)))
            s.rect(f"Bloque {row + 1}.{j + 1}", solid("#F6C2C0" if j % 2 else "#E9B1B0"),
                   lambda fr, u, x=x, yy=yy, hh=hh, j=j, row=row: (x - 160 * (u if row else -u), yy,
                                                                   x + 150 + 40 * (j % 3) - 160 * (u if row else -u),
                                                                   yy + hh),
                   op=lambda fr, u, j=j: k(fr, j % 4, 6) * (0.55 + 0.45 * ((j * 3) % 2)))
    s.rect("Banda", grad("#F5DADC", "#FBA7A0", 0), lambda fr, u: (-10, 540 - 349 * k(fr, 0, 9), 1930,
                                                                    540 + 349 * k(fr, 0, 9)))
    s.say("next video", (3, 528, 265, 568), M, 800, "#1A1A1A", "Siguiente", rot=lambda fr, u: -90,
          op=lambda fr, u: k(fr, 6, 3))
    s.picture("h-nature-02", lambda fr, u: (588, 551, 628, 350, k(fr, 9, 9)), name="Video", label="Siguiente video")
    for i, side in enumerate(([(588, 362), (260, 362), (260, 746), (588, 746)],
                              [(588, 746), (916, 746), (916, 362), (588, 362)])):
        s.outline(f"Marco {i + 1}", side, 6, "#1A1A1A", at=3, n=9, closed=False)
    ring_pts = [(1212 + 180 * math.cos(math.radians(a)), 540 + 180 * math.sin(math.radians(a))) for a in range(-80, 285, 10)]
    s.outline("Aro", ring_pts, 6, "#1A1A1A", at=9, n=9, closed=False)
    s.avatar("h-nature-04", lambda fr, u: (1212, 540, 330, k(fr, 12, 6)), label="Tu foto de perfil")
    c = s.say("your channel", (1472, 380, 1786, 420), M, 800, "#222222", "Canal")
    s.typed(c, 3, stagger=0.03, duration=0.15, preset="fade", order="random")
    s.say("slogan here", (1536, 436, 1726, 462), M, 400, "#444444", "Lema", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 15, 6)))
    s.icon("Me gusta", THUMB, solid("#555555"), lambda fr, u: (1559, 549, 102 * pop(fr, 21, 5), 0, 1), aspect=1.15)
    s.icon("Campana", BELL, solid("#555555"), lambda fr, u: (1720, 551, 106 * pop(fr, 24, 5), 0, 1), aspect=0.92)
    c = s.say("Please like and", (1508, 650, 1766, 676), M, 400, "#333333", "Texto")
    s.typed(c, 18, stagger=0.02, duration=0.1, preset="fade")
    c = s.say("Subscribe", (1556, 686, 1716, 710), M, 400, "#333333", "Texto 2")
    s.typed(c, 24, stagger=0.02, duration=0.1, preset="fade")
    return t



# --- 9. White play icon: it pops with scribbles, flips, «your channel» and a «Subscribed» pill clicked (54.1–57.5) --
def play_outline():
    D = 3.6
    t = _btn("play-contorno", "Botón: icono de video blanco que gira y «Subscribed»",
             "Button: white play icon that flips and «Subscribed»", 12508, D, ["youtube", "cursor", "blanco"],
             thumb=2.6)
    s = B(t, D)
    flip = lambda fr: abs(math.cos(math.pi * k(fr, 39, 9))) if fr < 84 else \
        abs(math.cos(math.pi / 2 * k(fr, 84, 15)))  # noqa: E731
    lift = lambda fr: k(fr, 39, 9)  # noqa: E731
    sc = lambda fr: (0.85 + 0.15 * lift(fr)) * pop(fr, 0, 6)  # noqa: E731
    cy = lambda fr: 780 - 135 * lift(fr)  # noqa: E731
    s.obj("Icono", ring(WHITE, 22),
          lambda fr, u: (928, cy(fr), 224 * sc(fr) * flip(fr), 208 * sc(fr), 0, 1.0 if fr < 99 else 0.0), radius=52,
          base=(224, 208))
    s.obj("Icono (play)", [shadow("#9A9A9A", 3, 4, 3, 1.0), fill(WHITE)],
          lambda fr, u: (934, cy(fr), 96 * sc(fr) * flip(fr), 90 * sc(fr), 0, 1.0 if fr < 99 else 0.0), path=PLAY)
    for i in range(9):
        a = math.radians(40 * i + 10)
        s.obj(f"Trazo {i + 1}", solid(WHITE), lambda fr, u, a=a, i=i: (
            928 + math.cos(a) * (120 + 50 * k(fr, 0, 12)), 780 + math.sin(a) * (110 + 50 * k(fr, 0, 12)),
            70 * math.sin(math.pi * lin(fr, i % 3, 14)), 4, math.degrees(a), 1.0 if fr < 16 else 0.0))
    out = lambda fr, u: 1.0 if fr < 99 else 0.0  # noqa: E731
    c = s.say("your channel", (750, 780, 1110, 835), M, 700, WHITE, "Canal", op=out)
    s.typed(c, 45, stagger=0.03, duration=0.05)
    pw = lambda fr: 320 * k(fr, 51, 12)  # noqa: E731
    s.obj("Botón", solid(WHITE), lambda fr, u: (932, 888, max(20 * k(fr, 51, 2), pw(fr)), 86 * k(fr, 51, 6), 0, out(fr, u)),
          radius=43, base=(320, 86))
    s.say("Subscribed", (858, 873, 1010, 900), M, 700, "#222222", "Botón (texto)",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 62, 4) * out(fr, u)))
    cur = pts((48, 960, 1120), (56, 940, 896), (66, 940, 896), (76, 980, 1140))
    s.cursor(lambda fr: (*cur(fr), math.sin(math.pi * lin(fr, 58, 5)), k(fr, 48, 3) * (1 - k(fr, 72, 4))), size=90)
    return t


# --- 10. White pill with a gradient bell: clicked, the colour stretches across and «Subscribed» (57.5–59.9) --------
def gradient_bell_pill():
    D = 3.6
    t = _btn("pildora-degradado", "Botón: píldora blanca con campana en degradado",
             "Button: white pill with a gradient bell", 12509, D, ["campana", "cursor", "degradado"], thumb=2.4)
    s = B(t, D)
    END = 90
    gone = lambda fr: 1 - k(fr, END, 9)  # noqa: E731
    s.obj("Botón", [shadow("#000000", 0, 8, 20, 0.35), fill(WHITE)],
          lambda fr, u: (920, 792, 560 * k(fr, 0, 8) * gone(fr), 180 * gone(fr), 0, 1), radius=90, base=(560, 180))

    def blob(fr, u):
        q = k(fr, 30, 10)
        cx = 735 + 355 * q
        stretch = 1 + 1.4 * math.sin(math.pi * q)
        d = 190 * pop(fr, 0, 6) * gone(fr)
        return cx, 792, d * stretch, d, 0, 1
    s.obj("Círculo", [shadow("#5B1A9A", 0, 10, 24, 0.5), grad("#33A6E8", "#E0218A", 315)[0]], blob, radius=95,
          base=(190, 190))
    pos = lambda fr: blob(fr, 0)[0]  # noqa: E731
    sway = lambda fr: 14 * math.sin(math.pi * 4 * lin(fr, 36, 20)) * (1 - lin(fr, 36, 20)) if fr > 36 else 0  # noqa: E731
    s.icon("Campana (clara)", BELL, solid("#E6D9F5"), lambda fr, u: (pos(fr), 792, 96 * gone(fr), 0,
                                                                    k(fr, 4, 4) * (1 - k(fr, 32, 4))), aspect=0.92)
    s.icon("Campana", BELL, solid(WHITE), lambda fr, u: (pos(fr), 792, 96 * gone(fr), sway(fr), k(fr, 36, 4)),
           aspect=0.92)
    s.icon("Campana (ondas)", RINGS, ring(WHITE, 6), lambda fr, u: (pos(fr), 780, 72 * gone(fr), 0, k(fr, 36, 4)),
           aspect=1.7)
    words = [gradient([(0.0, "#4F5FD0"), (1.0, "#6A2A6A")], angle=0)]
    c = s.say("Subscribe", (878, 763, 1135, 812), M, 700, "#5A4FC0", "Botón", layers=words,
              op=lambda fr, u: (1 - k(fr, 30, 4)) * gone(fr))
    s.typed(c, 3, stagger=0.03, duration=0.12, preset="fade", order="random")
    c = s.say("Subscribed", (700, 763, 980, 812), M, 700, "#5A4FC0", "Botón (suscrito)", layers=words,
              op=lambda fr, u: gone(fr))
    s.typed(c, 36, stagger=0.02, duration=0.1, preset="fade", order="random")
    for i in range(8):
        a = math.radians(-80 + 14 * i)
        s.obj(f"Gota {i + 1}", solid("#E040C8" if i % 3 else "#40C8F0"), lambda fr, u, a=a, i=i: (
            1090 + math.cos(a) * (110 + 120 * out3(lin(fr, 40, 36)) * (0.6 + 0.1 * (i % 4))),
            792 + math.sin(a) * (110 + 120 * out3(lin(fr, 40, 36)) * (0.6 + 0.1 * (i % 4))),
            18 - 2 * (i % 3), 30 - 4 * (i % 3), math.degrees(a) + 90,
            (1.0 if fr > 40 else 0.0) * (1 - k(fr, 64, 16))), kind="ellipse")
    cur = pts((10, 620, 1060), (18, 740, 812), (26, 740, 812), (40, 780, 1100))
    s.cursor(lambda fr: (*cur(fr), math.sin(math.pi * lin(fr, 22, 5)), k(fr, 10, 3) * (1 - k(fr, 36, 4))), size=96)
    return t


# --- 11. A bell flies into a red box that turns to face us; «your channel / Subscribed» slides out (60.0–63.3) ------
def red_box_bell():
    D = 4.6
    t = _btn("caja-roja-campana", "Botón: caja roja con campana y «Subscribed» inclinado",
             "Button: red box with a bell and tilted «Subscribed»", 12510, D, ["campana", "3d"], thumb=3.0)
    s = B(t, D)
    END = 120
    face = lambda fr: 0.08 + 0.92 * k(fr, 3, 18)  # noqa: E731
    cx = lambda fr: 710 - 422 * k(fr, 66, 9) + 422 * k(fr, END + 4, 6)  # noqa: E731
    size = lambda fr: 1 - k(fr, END + 8, 6)  # noqa: E731
    rot = lambda fr: -25 * (1 - k(fr, 3, 18)) - 5  # noqa: E731
    s.obj("Caja (lado)", solid("#A80F14"), lambda fr, u: (cx(fr) + 12, 822, 250 * face(fr) * size(fr), 240 * size(fr),
                                                          rot(fr), 1), radius=10, base=(250, 240))
    s.obj("Caja", [shadow("#FF2A2A", 0, 0, 40, 0.45), grad("#F23A3A", "#D8161C", 0)[0]],
          lambda fr, u: (cx(fr), 810, 250 * face(fr) * size(fr), 240 * size(fr), rot(fr), 1), radius=10,
          base=(250, 240))
    bx = lambda fr: 520 + (cx(fr) - 520) * k(fr, 6, 15)  # noqa: E731
    by = lambda fr: 790 + 14 * k(fr, 6, 15)  # noqa: E731
    s.icon("Campana", BELL, solid(WHITE), lambda fr, u: (bx(fr), by(fr), 120 * (0.6 + 0.4 * k(fr, 6, 15)) * size(fr),
                                                         rot(fr) + 40 * (1 - k(fr, 6, 15)), k(fr, 0, 3)), aspect=0.92)
    s.icon("Campana (ondas)", RINGS, ring(WHITE, 8), lambda fr, u: (cx(fr), by(fr) - 14, 92 * size(fr), rot(fr),
                                                                   k(fr, 21, 4)), aspect=1.7)
    arc_pts = [(cx(0) + 200 * math.cos(math.radians(a)), 810 + 120 * math.sin(math.radians(a))) for a in range(100, 220, 10)]
    c = s.outline("Estela", arc_pts, 4, WHITE, at=54, n=9, closed=False)
    s.fade(c, lambda fr: 1 - k(fr, 63, 6))
    reveal = lambda fr: (cx(fr) + 110, 0, 1920, 1080)  # noqa: E731
    back = lambda fr: -422 * (1 - k(fr, 66, 9) + k(fr, END + 4, 6))  # noqa: E731
    s.say("your channel", (462, 750, 822, 800), M, 700, WHITE, "Canal", align="left", reveal=reveal,
          shift=lambda fr: (back(fr), 0), rot=lambda fr, u: -10, op=lambda fr, u: 1.0 if 66 < fr < END + 10 else 0.0)
    s.say("Subscribed", (438, 806, 840, 860), M, 800, "#E8202A", "Texto", align="left", reveal=reveal,
          shift=lambda fr: (back(fr), 0), rot=lambda fr, u: -10, op=lambda fr, u: 1.0 if 66 < fr < END + 10 else 0.0)
    return t


# --- 12. Pink-purple tab with a ringed avatar, «your channel» and an outlined «Subscribe» (63.6–66.4) --------------
def gradient_tab():
    D = 5.0
    t = _btn("pestana-degradado", "Botón: pestaña rosa y morada con avatar", "Button: pink and purple tab with avatar",
             12511, D, ["avatar", "degradado"], thumb=3.0)
    s = E(t, D)
    top = lambda fr: 1080 - 295 * k(fr, 0, 9)  # noqa: E731
    s.rect("Pestaña", grad("#E0105A", "#8A10D8", 315), lambda fr, u: (512, top(fr), 1300, top(fr) + 400), radius=110)
    s.obj("Aro (sombra)", solid("#1E1E1E", 0.8), lambda fr, u: (1262, 850, 318 * pop(fr, 6, 6), 318 * pop(fr, 6, 6),
                                                                0, 1), kind="ellipse", base=(318, 318))
    s.obj("Aro", solid(WHITE), lambda fr, u: (1262, 850, 288 * pop(fr, 6, 6), 288 * pop(fr, 6, 6), 0, 1),
          kind="ellipse", base=(288, 288))
    s.obj("Aro (centro)", solid("#1E1E1E"), lambda fr, u: (1262, 850, 252 * k(fr, 15, 6), 252 * k(fr, 15, 6), 0, 1),
          kind="ellipse", base=(252, 252))
    s.avatar("fx-woman-06", lambda fr, u: (1262, 850, 252, k(fr, 18, 9)), label="Tu foto de perfil")
    c = s.say("your channel", (704, 844, 1025, 881), M, 700, WHITE, "Canal")
    s.typed(c, 6, stagger=0.03, duration=0.15, preset="fade", order="random")
    c = s.say("Slogan here", (720, 898, 990, 926), M, 500, "#5A0A7A", "Lema")
    s.typed(c, 15, stagger=0.03, duration=0.15, preset="fade", order="random")
    r, x0, x1, y0, y1 = 44, 727, 1046, 948, 1037
    loop = [(x0 + r + r * math.cos(math.radians(a)), (y0 + y1) / 2 + r * math.sin(math.radians(a))) for a in range(90, 271, 15)]
    loop += [(x1 - r + r * math.cos(math.radians(a)), (y0 + y1) / 2 + r * math.sin(math.radians(a))) for a in range(-90, 91, 15)]
    loop += [loop[0]]
    s.outline("Botón", loop, 5, WHITE, at=9, n=12, closed=False)
    c = s.say("Subscribe", (812, 978, 962, 1005), M, 700, WHITE, "Botón (texto)")
    s.typed(c, 12, stagger=0.03, duration=0.15, preset="fade", order="random")
    return t



def hatch(s, name, cx, cy, r, colour, at, width=10, gap=24, angle=45.0, spin=0.0):
    """A disc of parallel stripes (r = radius), each stripe a thin bar across the disc's chord."""
    n = int(2 * r / gap)
    for i in range(n):
        d = -r + gap * (i + 0.5)
        ln = 2 * math.sqrt(max(0.0, r * r - d * d))
        a = math.radians(angle + 90)
        s.obj(f"{name} {i + 1}", solid(colour), lambda fr, u, d=d, ln=ln: (
            *rot_pt(cx + d * math.cos(a), cy + d * math.sin(a), spin * u, cx, cy), ln * k(fr, at + i % 4, 9), width,
            angle + spin * u, 1))


# --- 13. «Click to Subscribe» on soft white rings: avatar, a framed video, like and bell buttons (66.4–68.9) -------
def end_click_rings():
    D = 5.4
    t = _end("final-anillos-blancos", "Pantalla final: «Click to Subscribe» sobre anillos blancos",
             "End screen: «Click to Subscribe» on white rings", 12512, D, ["blanco", "rosa"])
    s = E(t, D)
    BG = "#EFEFEF"
    bg(s, solid(BG))
    for i, d in enumerate((1900, 1450, 1050, 680)):
        s.obj(f"Anillo {i + 1}", neo_layers(BG, 10, "#C8C8C8"),
              lambda fr, u, d=d, i=i: (950, 540, d * k(fr, i, 9), d * k(fr, i, 9), 0, 1), kind="ellipse",
              base=(d, d))
    pink = "#E8457A"
    s.obj("Aro", [shadow("#B03060", 0, 10, 24, 0.4), fill(pink)],
          lambda fr, u: (952, 546, 330 * pop(fr, 3, 6), 330 * pop(fr, 3, 6), 0, 1), kind="ellipse", base=(330, 330))
    s.avatar("fx-woman-03", lambda fr, u: (952, 546, 300, k(fr, 24, 6)), label="Tu foto de perfil")
    s.say("Click to", (834, 160, 1052, 200), M, 700, pink, "Texto", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 3, 6)))
    c = s.say("Subscribe", (738, 216, 1166, 278), M, 800, pink, "Título",
              layers=[gradient([(0.0, "#E8457A"), (1.0, "#E03DB0")], angle=0)])
    s.typed(c, 9, stagger=0.03, duration=0.12, preset="fade", order="random")
    s.say("↓", (936, 300, 958, 340), M, 700, pink, "Flecha", editable=False, geom=lambda fr, u: (0, 0, 1, 0, k(fr, 15, 4)))
    s.rect("Video (marco)", [shadow("#B03060", 0, 12, 30, 0.35), fill(pink)],
           lambda fr, u: (1750 - 560 * k(fr, 12, 9), 380, 1750, 700))
    s.picture("h-nature-04", lambda fr, u: (1470, 540, 536, 296, k(fr, 27, 6)), name="Video", label="Siguiente video")
    s.say("Channel Name", (266, 432, 678, 476), M, 700, pink, "Canal", reveal=lambda fr: (0, 420, 690, 490),
          shift=lambda fr: (420 * (1 - k(fr, 12, 9)), 0))
    s.say("slogan here", (360, 494, 676, 530), M, 500, "#333333", "Lema", reveal=lambda fr: (0, 486, 690, 540),
          shift=lambda fr: (330 * (1 - k(fr, 15, 9)), 0))
    for i, (x, glyph) in enumerate(((436, THUMB), (603, BELL))):
        sz = lambda fr, i=i: pop(fr, 15 + 4 * i, 6)  # noqa: E731
        s.obj(f"Botón {i + 1}", [shadow("#B03060", 0, 10, 20, 0.4), grad("#D63CC8", "#F0407A", 0)[0]],
              lambda fr, u, x=x, sz=sz: (x, 631, 140 * sz(fr), 138 * sz(fr), 0, 1), radius=30, base=(140, 138))
        s.icon("Me gusta" if i == 0 else "Campana", glyph, solid(WHITE),
               lambda fr, u, x=x, sz=sz: (x, 631, 76 * sz(fr), 0, 1), aspect=1.2 if i == 0 else 0.92)
    s.icon("Campana (ondas)", RINGS, ring(WHITE, 6), lambda fr, u: (603, 622, 58 * pop(fr, 19, 6), 0, 1), aspect=1.7)
    c = s.say("W e e k l y   v i d e o s", (700, 832, 1236, 866), M, 800, "#111111", "Texto 2")
    s.typed(c, 21, stagger=0.015, duration=0.1, preset="fade")
    return t


# --- 14. Black end screen with a big gradient ring: avatar, next video, hatched discs, networks (68.9–71.0) ---------
def end_gradient_ring():
    D = 5.6
    t = _end("final-aro-degradado", "Pantalla final: aro en degradado sobre negro",
             "End screen: gradient ring on black", 12513, D, ["negro", "degradado", "redes"])
    s = E(t, D)
    bg(s, solid("#111111"))
    hatch(s, "Rayas", 580, -20, 230, "#E8203A", 0, width=10, gap=26, spin=8)
    hatch(s, "Rayas 2", 80, 830, 200, "#E020B0", 3, width=10, gap=26, spin=-8)
    hatch(s, "Rayas 3", 650, 1090, 150, "#E020B0", 6, width=10, gap=26, spin=8)
    s.obj("Punto", grad("#FF3A8A", "#E020F0", 90), lambda fr, u: (60, 570, 240 * pop(fr, 0, 9), 240 * pop(fr, 0, 9),
                                                                  0, 1), kind="ellipse", base=(240, 240))
    ring_d = lambda fr: 180 + 1070 * k(fr, 0, 9)  # noqa: E731
    s.obj("Aro", [gradient([(0.0, "#FF9A00"), (0.45, "#FF2D8A"), (1.0, "#B000FF")], angle=45)],
          lambda fr, u: (1480, 560, ring_d(fr), ring_d(fr), 0, 1), kind="ellipse", base=(1250, 1250))
    s.obj("Aro (centro)", solid("#111111"), lambda fr, u: (1480, 560, ring_d(fr) * 0.7, ring_d(fr) * 0.7, 0, 1),
          kind="ellipse", base=(875, 875))
    s.obj("Avatar (aro)", grad("#FF3A8A", "#E020F0", 90), lambda fr, u: (1480, 414, 300 * pop(fr, 12, 9),
                                                                        300 * pop(fr, 12, 9), 0, 1),
          kind="ellipse", base=(300, 300))
    s.obj("Avatar (centro)", solid("#111111"), lambda fr, u: (1480, 414, 270 * k(fr, 30, 3), 270 * k(fr, 30, 3), 0, 1),
          kind="ellipse", base=(270, 270))
    s.avatar("fx-face-05", lambda fr, u: (1480, 414, 270, k(fr, 33, 6)), label="Tu foto de perfil")
    s.say("channel name", (1256, 616, 1710, 676), M, 700, WHITE, "Canal", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 24, 6)))
    s.say("slogan here", (1344, 680, 1626, 716), M, 500, "#9A9A9A", "Lema", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 30, 6)))
    s.obj("Botón", grad("#FF3A8A", "#E020F0", 0), lambda fr, u: (1484, 782, 328 * k(fr, 33, 6), 84, 0, 1), radius=42,
          base=(328, 84))
    s.say("Subscribe", (1408, 768, 1560, 796), M, 700, "#1A1A1A", "Botón", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 36, 4)))
    s.rect("Video (marco)", [shadow("#FF2D8A", 0, 0, 30, 0.6), fill("#F0306A")],
           lambda fr, u: (230, 344, 230 + 724 * k(fr, 21, 9), 770))
    s.picture("h-nature-04", lambda fr, u: (593, 555, 694, 390, k(fr, 33, 6)), name="Video", label="Siguiente video")
    c = s.say("Thanks for", (366, 152, 728, 212), M, 700, WHITE, "Título")
    s.typed(c, 33, stagger=0.03, duration=0.15, preset="fade", order="random")
    c = s.say("Watching!", (370, 220, 730, 280), M, 700, WHITE, "Título 2")
    s.typed(c, 33, stagger=0.03, duration=0.15, preset="fade", order="random")
    for i, (kind, label, y) in enumerate((("fb", "/yourfbid", 854), ("ig", "/yourinsta", 932), ("tw", "/yourtwitter",
                                                                                                 1010))):
        sz = lambda fr, i=i: pop(fr, 33 + 4 * i, 5)  # noqa: E731
        s.obj(f"Red {i + 1}", solid(WHITE), lambda fr, u, y=y, sz=sz: (440, y, 68 * sz(fr), 68 * sz(fr), 0, 1),
              radius=16, base=(68, 68))
        social(s, kind, 440, y, 74, None, "#111111", size=sz)
        c = s.say(label, (516, y - 22, 516 + 18 * len(label), y + 14), M, 500, WHITE, f"Red {i + 1} (texto)",
                  align="left")
        s.typed(c, 36 + 4 * i, stagger=0.03, duration=0.05)
    return t


# --- 15. Blue-cyan band over a night photo: «Click here to Subscribe», avatar, two framed videos (71.0–72.7) -------
def end_blue_band():
    D = 5.2
    t = _end("final-banda-azul", "Pantalla final: banda azul sobre foto con dos videos",
             "End screen: blue band over a photo with two videos", 12514, D, ["azul", "foto"])
    s = E(t, D)
    bgp = s.picture("h-nature-06", lambda fr, u: (960, 540, 1920, 1080, 1.0), name="Fondo (foto)", label="Tu fondo")
    bgp["effects"] = [effect("color.basic", saturation=-1.0)]
    s.rect("Banda", [shadow("#000000", 0, 10, 30, 0.4), grad("#5A4FF0", "#10E0F8", 0)[0]],
           lambda fr, u: (-10, -10, 1930, 470 * k(fr, 0, 9)))
    s.rect("Banda (borde)", solid("#7AA8FF", 0.6), lambda fr, u: (-10, 470 * k(fr, 0, 9) - 8, 1930, 470 * k(fr, 0, 9)))
    s.say("Click here to", (220, 286, 584, 330), M, 700, WHITE, "Texto", reveal=lambda fr: (0, 270, 960, 420),
          shift=lambda fr: (-620 * (1 - k(fr, 9, 9)), 0))
    s.say("Subscribe", (194, 340, 610, 404), M, 800, WHITE, "Título", reveal=lambda fr: (0, 270, 960, 420),
          shift=lambda fr: (-620 * (1 - k(fr, 9, 9)), 0))
    s.outline("Flecha", [(620, 318), (680, 292), (740, 292), (782, 306)], 4, WHITE, at=18, n=6, closed=False)
    s.outline("Flecha (punta)", [(760, 290), (782, 306), (758, 316)], 4, WHITE, at=23, n=3, closed=False)
    s.say("Channel Name", (1256, 316, 1720, 364), M, 700, WHITE, "Canal", reveal=lambda fr: (960, 290, 1920, 430),
          shift=lambda fr: (620 * (1 - k(fr, 9, 9)), 0))
    s.say("slogan here", (1330, 376, 1644, 416), M, 500, "#2A4FA0", "Lema", reveal=lambda fr: (960, 290, 1920, 430),
          shift=lambda fr: (620 * (1 - k(fr, 12, 9)), 0))
    s.obj("Aro", grad("#7A5AF0", "#20D0F8", 0), lambda fr, u: (944, 446, 376 * pop(fr, 15, 6), 376 * pop(fr, 15, 6),
                                                             0, 1), kind="ellipse", base=(376, 376))
    s.avatar("fx-woman-04", lambda fr, u: (944, 446, 330, k(fr, 30, 6)), label="Tu foto de perfil")
    s.outline("Marco", [(44, 506), (1874, 506), (1874, 1036), (44, 1036), (44, 506)], 4, "#6A9AF8", at=21, n=9,
              closed=False)
    for i, (x0, x1, colour, sample) in enumerate(((128, 766, "#6A4FF0", "fx-face-05"),
                                                  (1146, 1784, "#20C8F0", "y5-night-01"))):
        cx = (x0 + x1) / 2
        s.obj(f"Video {i + 1} (marco)", ring(colour, 8), lambda fr, u, cx=cx, x0=x0, x1=x1, i=i: (
            cx, 777, (x1 - x0) * k(fr, 12 + 6 * i, 6), 366 * k(fr, 12 + 6 * i, 6), 0, 1), base=(x1 - x0, 366))
        s.obj(f"Video {i + 1} (relleno)", solid(colour), lambda fr, u, cx=cx, x0=x0, x1=x1, i=i: (
            cx, 777, (x1 - x0) * k(fr, 12 + 6 * i, 6), 366 * k(fr, 12 + 6 * i, 6), 0, 1 - k(fr, 24, 9)),
            base=(x1 - x0, 366))
        s.picture(sample, lambda fr, u, cx=cx, x0=x0, x1=x1: (cx, 777, x1 - x0 - 16, 350, k(fr, 24, 9)),
                  name=f"Video {i + 1}", label=f"Video {i + 1}")
    return t


# --- 16. Teal waves: a recommended video, ringed avatar, «Thanks for watching!» (72.7–74.5) -----------------------
def end_teal_waves():
    D = 5.0
    t = _end("final-olas-turquesa", "Pantalla final: olas turquesa con video recomendado",
             "End screen: teal waves with a recommended video", 12515, D, ["turquesa", "olas"])
    s = E(t, D)
    bg(s, solid(WHITE))
    for i, (y, c0, c1, ph) in enumerate(((520, "#BFE6E6", "#9ED8D8", 0.0), (560, "#4AA8C8", "#8ED8D0", 1.8))):
        pts_ = [(x, 8 + 6 * math.sin(x / 100 * 2 * math.pi * 1.2 + ph)) for x in range(0, 101, 5)] + [(100, 100), (0, 100)]
        s.obj(f"Ola {i + 1}", grad(c0, c1, 0), lambda fr, u, y=y, i=i: (960 - 40 * u * (1 - 2 * i), y + 300 + 500 * (1 - k(fr, i * 2, 9)),
                                                                     2100, 640, 0, 1), path=poly(pts_))
    s.obj("Video (marco)", [shadow("#2A7A8A", 0, 12, 30, 0.35), fill("#6CC4C4")],
          lambda fr, u: (672, 505, 20 + 732 * k(fr, 9, 6), 430 * k(fr, 6, 6), 0, 1), base=(752, 430))
    s.picture("fx-face-06", lambda fr, u: (672, 505, 720, 402, k(fr, 27, 6)), name="Video", label="Video recomendado")
    s.obj("Aro", [shadow("#2A7A8A", 0, 12, 30, 0.35), fill("#7CCFC8")],
          lambda fr, u: (1410, 490, 432 * pop(fr, 9, 6), 432 * pop(fr, 9, 6), 0, 1), kind="ellipse", base=(432, 432))
    s.avatar("fx-face-03", lambda fr, u: (1410, 490, 380, k(fr, 21, 6)), label="Tu foto de perfil")
    s.say("Channel Name", (1236, 768, 1592, 804), M, 700, WHITE, "Canal", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 18, 6)))
    s.say("slogan here", (1284, 816, 1530, 844), M, 500, WHITE, "Lema", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 24, 6)))
    c = s.say("Recommended Video", (452, 780, 894, 810), M, 700, WHITE, "Texto")
    s.typed(c, 27, stagger=0.02, duration=0.08)
    c = s.say("T h a n k s", (494, 116, 834, 164), M, 700, "#7FD3D0", "Título")
    s.typed(c, 30, stagger=0.03, duration=0.2, preset="fade", order="random")
    c = s.say("f o r   w a t c h i n g !", (426, 186, 922, 214), M, 700, "#7FD3D0", "Título 2")
    s.typed(c, 33, stagger=0.02, duration=0.2, preset="fade", order="random")
    return t



# --- 17. «DON'T FORGET TO SUBSCRIBE» over a photo: a blue slant and blobs, avatar, «Follow me», networks (74.5–77.6)
def end_dont_forget():
    D = 5.6
    t = _end("final-no-olvides", "Pantalla final: «Don't forget to subscribe» con franja azul",
             "End screen: «Don't forget to subscribe» with a blue slant", 12516, D, ["azul", "foto", "redes"])
    s = E(t, D)
    s.picture("h-nature-02", lambda fr, u: (960, 540, 1920, 1080, 1.0), name="Fondo (foto)", label="Tu fondo")
    s.rect("Sombra", solid("#0A1A3A"), lambda fr, u: (-10, -10, 1930, 1090), op=lambda fr, u: 0.62 * k(fr, 6, 9))
    off = lambda fr: 900 * (1 - k(fr, 6, 12))  # noqa: E731
    s.obj("Franja", grad("#20F0E0", "#7A30F0", 20), lambda fr, u: (960 + off(fr), 860 + off(fr) * 0.5, 2200, 760, 0, 1),
          path=poly([(0, 30), (100, 0), (100, 100), (0, 100)]))
    blob = "M 40 0 C 80 0 100 20 100 50 C 100 85 80 100 45 100 C 15 100 0 80 0 50 C 0 20 10 0 40 0 Z"
    s.obj("Mancha", grad("#30F0F0", "#2A9AF8", 0), lambda fr, u: (90 - 400 * (1 - k(fr, 18, 9)), 760, 420, 760, -10, 1),
          path=blob)
    s.obj("Mancha 2", grad("#3A80F8", "#2040E0", 0), lambda fr, u: (1800 + 400 * (1 - k(fr, 27, 9)), 960, 440, 400, 10,
                                                                    1), path=blob)
    blue = [gradient([(0.0, "#3A6AF0"), (1.0, "#6A4AE8")], angle=0)]
    c = s.say("DON'T", (190, 140, 536, 220), M, 400, "#3A5AE0", "Texto")
    s.typed(c, 18, stagger=0.04, duration=0.15, preset="fade", order="random")
    c = s.say("FORGET TO", (190, 262, 724, 330), M, 400, "#3A5AE0", "Texto 2")
    s.typed(c, 24, stagger=0.04, duration=0.15, preset="fade", order="random")
    c = s.say("SUBSCRIBE", (186, 356, 806, 442), M, 800, "#3A5AE0", "Título", layers=blue)
    s.typed(c, 27, stagger=0.04, duration=0.15, preset="fade", order="random")
    s.obj("Aro", grad("#3A6AF0", "#7A4AF0", 0), lambda fr, u: (1280, 600, 360 * pop(fr, 27, 6), 360 * pop(fr, 27, 6),
                                                             0, 1), kind="ellipse", base=(360, 360))
    s.avatar("fx-face-05", lambda fr, u: (1280, 600, 316, k(fr, 45, 6)), label="Tu foto de perfil")
    c = s.say("yourchannel", (1116, 820, 1464, 876), M, 700, WHITE, "Canal")
    s.typed(c, 33, stagger=0.03, duration=0.1, preset="fade", order="random")
    s.say("slogan here", (1158, 890, 1428, 930), M, 500, "#14204A", "Lema", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 42, 6)))
    s.outline("Seguir", [(643, 840), (772, 840), (772, 910), (514, 910), (514, 840), (643, 840)], 4, WHITE, at=21, n=9,
              closed=False)
    s.say("Follow me", (566, 862, 720, 888), M, 600, WHITE, "Seguir (texto)", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 27, 4)))
    for i, (kind, x, label) in enumerate((("fb", 310, "/yourname"), ("ig", 598, "@yourname"), ("tw", 902, "@yourname"))):
        social(s, kind, x, 990, 76, WHITE, "#2A6AE8", size=lambda fr, i=i: pop(fr, 12 + 12 * i, 5))
        c = s.say(label, (x + 64, 978, x + 64 + 15 * len(label), 1002), M, 600, WHITE, f"Red {i + 1} (texto)",
                  align="left")
        s.typed(c, 15 + 12 * i, stagger=0.02, duration=0.05)
    return t


# --- 18. A glowing gradient hexagon over a dark city: avatar, «Click to Subscribe», framed video (77.6–79.7) -------
def end_hexagon():
    D = 5.2
    t = _end("final-hexagono", "Pantalla final: hexágono en degradado con «Click to Subscribe»",
             "End screen: gradient hexagon with «Click to Subscribe»", 12517, D, ["hexágono", "degradado", "redes"])
    s = E(t, D)
    s.picture("fx-citynight-02", lambda fr, u: (960, 540, 1920, 1080, 1.0), name="Fondo (foto)", label="Tu fondo")
    s.rect("Sombra", solid("#05050C"), lambda fr, u: (-10, -10, 1930, 1090), op=lambda fr, u: 0.55 * k(fr, 3, 9))
    hexa = regular(6)
    size = lambda fr: 888 * (0.08 * k(fr, 2, 2) + 0.92 * k(fr, 4, 9))  # noqa: E731
    s.obj("Hexágono (aro)", ring("#6A60F0", 10), lambda fr, u: (490, 556, size(fr) * 1.08, size(fr) * 1.08, 0,
                                                               1 - k(fr, 12, 4)), path=hexa)
    s.obj("Hexágono", [shadow("#7A4AF8", 0, 0, 80, 0.8),
                       gradient([(0.0, "#FF4A90"), (0.5, "#7A6AF8"), (1.0, "#3AF0F0")], angle=90)],
          lambda fr, u: (490, 556, size(fr), size(fr), 0, 1), path=hexa)
    pts_ = [(476 + 175 * math.cos(math.radians(a)), 430 + 175 * math.sin(math.radians(a))) for a in range(-90, 275, 10)]
    s.obj("Avatar (fondo)", solid("#2A0A4A"), lambda fr, u: (476, 430, 330 * k(fr, 18, 6), 330 * k(fr, 18, 6), 0, 1),
          kind="ellipse", base=(330, 330))
    s.outline("Avatar (aro)", pts_, 16, "#B0A0FF", at=18, n=9, closed=False)
    s.avatar("fx-man-06", lambda fr, u: (476, 430, 300, k(fr, 27, 6)), label="Tu foto de perfil")
    c = s.say("yourchannel", (322, 650, 640, 700), M, 700, WHITE, "Canal")
    s.typed(c, 21, stagger=0.03, duration=0.1, preset="fade", order="random")
    s.say("follow me", (364, 710, 596, 756), M, 400, "#1A1A3A", "Lema", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 27, 6)))
    for i, (kind, x) in enumerate((("fb", 410), ("ig", 484), ("tw", 562))):
        social(s, kind, x, 812, 64, WHITE, "#7A5AF0", size=lambda fr, i=i: pop(fr, 30 + 3 * i, 5))
    s.outline("Flecha", [(1100, 310), (1040, 270), (960, 250), (900, 252), (850, 262)], 4, WHITE, at=15, n=9,
              closed=False)
    s.outline("Flecha (punta)", [(872, 244), (850, 262), (874, 280)], 4, WHITE, at=23, n=3, closed=False)
    c = s.say("Click to", (1190, 190, 1556, 270), M, 400, "#B0A0C8", "Texto")
    s.typed(c, 15, stagger=0.04, duration=0.15, preset="fade", order="random")
    c = s.say("Subscribe", (1134, 300, 1630, 390), M, 700, "#8A90C0", "Título",
              layers=[gradient([(0.0, "#B0A8C8"), (1.0, "#5A60D0")], angle=0)])
    s.typed(c, 21, stagger=0.04, duration=0.15, preset="fade", order="random")
    s.outline("Video (marco)", [(1028, 920), (1028, 516), (1714, 516), (1714, 920), (1028, 920)], 8, "#5AC8F0", at=27,
              n=9, closed=False)
    s.picture("fx-woman-08", lambda fr, u: (1372, 718, 632, 356, k(fr, 30, 6)), name="Video", label="Siguiente video")
    return t



# --- 19. Round like button clicked: «Liked» slides out; a bell appears below, clicked, «Subscribed» (79.7–83.6) ----
def liked_round():
    D = 4.8
    t = _btn("me-gusta-redondo", "Botón: me gusta redondo y campana con «Liked» y «Subscribed»",
             "Button: round like and bell with «Liked» and «Subscribed»", 12518, D, ["me gusta", "campana", "cursor"],
             thumb=3.8)
    s = B(t, D)
    END = 126
    gone = lambda fr: 1 - k(fr, END, 9)  # noqa: E731
    red, dark = "#E8283E", "#B8162C"
    lx = lambda fr: 936 - 161 * k(fr, 48, 12)  # noqa: E731
    bx = lambda fr: 930 + 150 * k(fr, 87, 12)  # noqa: E731
    # pills first (under the circles)
    s.rect("Me gusta (barra)", [shadow("#000000", 0, 8, 20, 0.4), grad(dark, red, 0)[0]],
           lambda fr, u: (lx(fr), 375, lx(fr) + 4 + (1160 - 775) * k(fr, 48, 18) * gone(fr), 490), radius=30)
    s.rect("Campana (barra)", [shadow("#000000", 0, 8, 20, 0.4), grad(dark, red, 0)[0]],
           lambda fr, u: (bx(fr) - 4 - (1080 - 730) * k(fr, 87, 18) * gone(fr), 568, bx(fr), 690), radius=30)
    s.say("Liked", (918, 410, 1076, 460), M, 700, WHITE, "Me gusta (texto)",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 60, 6) * gone(fr)))
    s.say("Subscribed", (766, 612, 968, 642), M, 700, WHITE, "Campana (texto)",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 99, 6) * gone(fr)))
    for name, cx, cy, at, click in (("Me gusta", lx, 430, 0, 24), ("Campana", bx, 630, 39, 78)):
        sz = lambda fr, at=at: pop(fr, at, 8) * (1 - k(fr, END + 4, 8))  # noqa: E731
        s.obj(f"{name} (halo)", solid("#9A9A9A", 0.55), lambda fr, u, cx=cx, cy=cy, click=click, sz=sz: (
            cx(fr), cy, 240 * sz(fr) * k(fr, click, 4), 240 * sz(fr) * k(fr, click, 4), 0, 1 - k(fr, click + 12, 9)),
            kind="ellipse", base=(240, 240))
        s.obj(f"{name} (botón)", [shadow("#000000", 0, 8, 24, 0.45), grad("#F04050", dark, 90)[0]],
              lambda fr, u, cx=cx, cy=cy, sz=sz: (cx(fr), cy, 180 * sz(fr), 180 * sz(fr), 0, 1), kind="ellipse",
              base=(180, 180))
        s.obj(f"{name} (aro)", ring(WHITE, 5), lambda fr, u, cx=cx, cy=cy, sz=sz: (cx(fr), cy, 150 * sz(fr),
                                                                                   150 * sz(fr), 0, 1),
              kind="ellipse", base=(150, 150))
        if name == "Me gusta":
            s.icon(name, THUMB, solid(WHITE), lambda fr, u, cx=cx, cy=cy, sz=sz: (cx(fr), cy - 4, 74 * sz(fr), 0, 1),
                   aspect=1.25)
        else:
            s.icon(name, BELL, solid(WHITE), lambda fr, u, cx=cx, cy=cy, sz=sz: (cx(fr), cy, 80 * sz(fr),
                                                                         14 * math.sin(math.pi * 4 * lin(fr, 78, 20)) *
                                                                         (1 - lin(fr, 78, 20)), 1), aspect=0.92)
            s.icon("Campana (ondas)", RINGS, ring(WHITE, 6), lambda fr, u, cx=cx, cy=cy, sz=sz: (cx(fr), cy - 8, 60 * sz(fr),
                                                                                         0, k(fr, 80, 4)), aspect=1.7)
    sw = s.outline("Remolino", [(930 + 34 * math.cos(math.radians(a)) * (1 - a / 900),
                                 640 + 34 * math.sin(math.radians(a)) * (1 - a / 900)) for a in range(0, 541, 30)],
                   6, red, at=27, n=9, closed=False)
    s.fade(sw, lambda fr: 1 - k(fr, 39, 4))
    cur = pts((12, 1040, 760), (21, 950, 452), (30, 950, 452), (48, 940, 655), (66, 940, 655), (75, 950, 655),
              (90, 1020, 960))
    s.cursor(lambda fr: (*cur(fr), max(math.sin(math.pi * lin(fr, 22, 5)), math.sin(math.pi * lin(fr, 76, 5))),
                         k(fr, 12, 3) * (1 - k(fr, 86, 4))), size=100)
    return t


# --- 20. A white 3D card: the avatar ring draws itself, a red like, «channel name» typed (83.7–86.4) --------------
def white_card():
    D = 4.2
    t = _btn("tarjeta-blanca", "Botón: tarjeta blanca con avatar y me gusta",
             "Button: white card with avatar and like", 12519, D, ["me gusta", "avatar", "3d"], thumb=3.0)
    s = E(t, D)
    w = lambda fr: 245 * (0.2 + 0.8 * k(fr, 0, 12))  # noqa: E731
    s.obj("Tarjeta (lado)", solid("#C9C9C9"), lambda fr, u: (820, 572, w(fr), 400, 0, k(fr, 0, 3)), radius=40,
          base=(245, 400))
    s.obj("Tarjeta", [shadow("#000000", 0, 16, 30, 0.45), grad("#FFFFFF", "#ECECEC", 90)[0]],
          lambda fr, u: (832 + 8 * k(fr, 0, 12), 565, w(fr), 400, 0, k(fr, 0, 3)), radius=40, base=(245, 400))
    s.obj("Aro (hueco)", [shadow("#9A9A9A", 4, 6, 12, 0.6), fill("#F2F2F2")],
          lambda fr, u: (885, 490, 180 * k(fr, 12, 6), 180 * k(fr, 12, 6), 0, 1), kind="ellipse", base=(180, 180))
    pts_ = [(885 + 74 * math.cos(math.radians(a)), 490 + 74 * math.sin(math.radians(a))) for a in range(-90, 275, 10)]
    c = s.outline("Aro (trazo)", pts_, 6, "#E01818", at=24, n=9, closed=False)
    s.fade(c, lambda fr: 1 - k(fr, 36, 4))
    s.avatar("fx-face-06", lambda fr, u: (885, 490, 140, k(fr, 36, 9)), label="Tu foto de perfil")
    s.icon("Me gusta (lado)", THUMB, solid("#A00000"), lambda fr, u: (888, 662, 86 * pop(fr, 12, 6), 0, 1), aspect=1.28)
    s.icon("Me gusta", THUMB, solid("#FF1010"), lambda fr, u: (880, 655, 86 * pop(fr, 12, 6), 0, 1), aspect=1.28)
    c = s.say("Like", (990, 650, 1070, 680), M, 800, "#E01818", "Me gusta (texto)")
    s.typed(c, 24, stagger=0.05, duration=0.1, preset="fade")
    c = s.say("channel name", (985, 470, 1255, 500), M, 600, WHITE, "Canal")
    s.typed(c, 39, stagger=0.04, duration=0.06)
    s.say("s l o g a n   h e r e", (985, 510, 1245, 530), M, 500, "#B01010", "Lema",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 45, 6)))
    return t



# --- 21. Teal pattern end screen: a capsule rises with the avatar, like and bell; two videos (86.4–89.2) ------------
def end_teal_capsule():
    D = 5.4
    t = _end("final-capsula-turquesa", "Pantalla final: cápsula turquesa con dos videos",
             "End screen: teal capsule with two videos", 12520, D, ["turquesa", "me gusta", "campana"])
    s = E(t, D)
    bg(s, grad("#9EE0D8", "#2FA89A", 330))
    for i in range(9):
        for j in range(5):
            s.obj(f"Patrón {i + 1}.{j + 1}", ring("#C6F0EA", 3), lambda fr, u, i=i, j=j: (
                110 + 220 * i + 110 * (j % 2), 60 + 240 * j, 300, 300, 0, 0.35), kind="ellipse")
    top = lambda fr: 1080 - 790 * k(fr, 0, 12)  # noqa: E731
    s.rect("Cápsula", [shadow("#1A6A60", 0, 20, 50, 0.45), grad("#B6EEE6", "#7ED6CA", 90)[0]],
           lambda fr, u: (244, top(fr), 664, top(fr) + 1000), radius=210)
    pts_ = [(454 + 180 * math.cos(math.radians(a)), 498 + 180 * math.sin(math.radians(a))) for a in range(-90, 275, 10)]
    s.outline("Aro", pts_, 6, WHITE, at=18, n=9, closed=False)
    s.avatar("fx-woman-01", lambda fr, u: (454, 498, 330, k(fr, 39, 6)), label="Tu foto de perfil")
    c = s.say("yourchannel", (310, 722, 590, 762), M, 700, WHITE, "Canal")
    s.typed(c, 27, stagger=0.03, duration=0.06)
    s.say("slogan here", (330, 778, 572, 812), M, 500, "#1A1A1A", "Lema", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 45, 6)))
    s.icon("Me gusta", THUMB, solid(WHITE), lambda fr, u: (378, 900, 90 * pop(fr, 36, 6), 0, 1), aspect=1.25)
    s.icon("Campana", BELL, solid(WHITE), lambda fr, u: (526, 900, 92 * pop(fr, 39, 6), 0, 1), aspect=0.92)
    s.icon("Campana (ondas)", RINGS, ring(WHITE, 7), lambda fr, u: (526, 888, 70 * pop(fr, 39, 6), 0, 1), aspect=1.7)
    s.say("Like", (352, 966, 410, 990), M, 600, WHITE, "Me gusta (texto)", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 42, 4)))
    s.say("Subscribe", (464, 968, 594, 990), M, 600, WHITE, "Campana (texto)",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 45, 4)))
    for i, (y0, y1, sample, at) in enumerate(((140, 530, "h-nature-04", 30), (574, 964, "fx-nature-02", 36))):
        s.rect(f"Video {i + 1} (marco)", [shadow("#1A6A60", 0, 14, 30, 0.4), fill("#7ED6CA")],
               lambda fr, u, y0=y0, y1=y1, at=at: (1006, y0, 1680, y0 + 14 + (y1 - y0 - 14) * k(fr, at, 9)))
        s.picture(sample, lambda fr, u, y0=y0, y1=y1, at=at: (1343, (y0 + y1) / 2, 644, y1 - y0 - 32,
                                                             k(fr, at + 21, 12)), name=f"Video {i + 1}",
                  label=f"Video {i + 1}")
    c = s.say("Thanks for", (270, 126, 600, 176), M, 700, "#111111", "Título")
    s.typed(c, 36, stagger=0.03, duration=0.15, preset="fade", order="random")
    c = s.say("Watching!", (290, 192, 600, 244), M, 700, "#111111", "Título 2")
    s.typed(c, 36, stagger=0.03, duration=0.15, preset="fade", order="random")
    return t


# --- 22. A pink line over a photo opens into a lilac card: avatar, next video, «Please Don't Forget to Subscribe» --
def end_lilac_card():
    D = 5.4
    t = _end("final-tarjeta-lila", "Pantalla final: tarjeta lila «Please don't forget to subscribe»",
             "End screen: lilac card «Please don't forget to subscribe»", 12521, D, ["lila", "foto"])
    s = E(t, D)
    bgp = s.picture("fx-man-05", lambda fr, u: (960, 540, 1920, 1080, 1.0), name="Fondo (foto)", label="Tu fondo")
    bgp["effects"] = [effect("color.basic", saturation=-1.0)]
    h = lambda fr: 6 + 934 * k(fr, 6, 9)  # noqa: E731
    w = lambda fr: 1750 * k(fr, 0, 6)  # noqa: E731
    s.obj("Tarjeta", [shadow("#3A2A5A", 0, 20, 50, 0.45), grad("#F0A8D8", "#C0A0F0", 0)[0]],
          lambda fr, u: (70 + w(fr) / 2, 530, w(fr), h(fr), -2 * math.sin(math.pi * k(fr, 6, 9)), 1),
          base=(1750, 940))
    s.rect("Panel", grad("#E8B4EC", "#C8A8F4", 0), lambda fr, u: (900, 1000 - 930 * k(fr, 15, 6), 1750, 1000),
           op=lambda fr, u: 0.7)
    for i, d in enumerate((440, 380)):
        s.obj(f"Onda {i + 1}", ring("#F6D0F0", 2), lambda fr, u, d=d: (414, 480, d * k(fr, 12, 9), d * k(fr, 12, 9), 0,
                                                                      0.6), kind="ellipse", base=(d, d))
    pts_ = [(414 + 160 * math.cos(math.radians(a)), 480 + 160 * math.sin(math.radians(a))) for a in range(-90, 275, 10)]
    s.outline("Aro", pts_, 6, WHITE, at=12, n=9, closed=False)
    s.avatar("fx-woman-02", lambda fr, u: (414, 480, 290, k(fr, 18, 6)), label="Tu foto de perfil")
    c = s.say("yourchannel", (264, 680, 560, 724), M, 700, WHITE, "Canal")
    s.typed(c, 21, stagger=0.03, duration=0.15, preset="fade", order="random")
    s.say("slogan here", (290, 738, 540, 776), M, 500, "#2A2A3A", "Lema", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 27, 6)))
    s.obj("Botón", solid(WHITE), lambda fr, u: (415, 832, 258 * k(fr, 18, 6), 60, 0, 1), radius=30, base=(258, 60))
    s.say("Subscribe", (366, 820, 464, 844), M, 600, "#E080C8", "Botón", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 21, 4)))
    s.say("next video", (1158, 196, 1366, 226), M, 500, WHITE, "Siguiente", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 21, 6)))
    s.say("↓", (1260, 240, 1280, 280), M, 500, WHITE, "Flecha", editable=False, geom=lambda fr, u: (0, 0, 1, 0, k(fr, 24, 6)))
    s.picture("h-nature-06", lambda fr, u: (1184, 499, 630, 350, k(fr, 33, 9)), name="Video", label="Siguiente video")
    s.outline("Video (marco)", [(1184, 308), (1516, 308), (1516, 690), (852, 690), (852, 308), (1184, 308)], 6, WHITE,
              at=18, n=12, closed=False)
    c = s.say("Please Don't Forget", (998, 742, 1458, 782), M, 800, "#111111", "Título")
    s.typed(c, 21, stagger=0.02, duration=0.15, preset="fade", order="random")
    c = s.say("to Subscribe", (1004, 800, 1458, 876), M, 800, WHITE, "Título 2")
    s.typed(c, 24, stagger=0.03, duration=0.15, preset="fade", order="random")
    return t



# --- 23. A glowing red like box spins up from a dot, then turns round to a bell; «Channel name» (91.1–97.0) --------
def red_box_flip():
    D = 6.3
    t = _btn("caja-me-gusta-campana", "Botón: caja roja que gira de me gusta a campana",
             "Button: red box turning from like to bell", 12522, D, ["me gusta", "campana", "3d"], thumb=2.4)
    s = B(t, D)
    END = 178
    gone = lambda fr: 1 - k(fr, END, 9)  # noqa: E731
    grow = lambda fr: pop(fr, 6, 15, 0.06) * gone(fr)  # noqa: E731
    turn = lambda fr: abs(math.cos(math.pi * k(fr, 99, 12)))  # noqa: E731
    bell = lambda fr: k(fr, 99, 12) >= 0.5  # noqa: E731
    spin = lambda fr: -160 * (1 - k(fr, 6, 18))  # noqa: E731
    s.obj("Estela", ring("#E8202E", 10), lambda fr, u: (952, 452, 300 * k(fr, 6, 12), 300 * k(fr, 6, 12),
                                                        spin(fr) - 40, 1 - k(fr, 18, 6)), path="M 50 0 Q 100 0 100 50")
    s.obj("Caja (lado)", solid("#9A0E1A"), lambda fr, u: (952 + 12 * (1 - turn(fr)) + 4, 460, 265 * grow(fr) *
                                                          max(0.08, turn(fr)), 265 * grow(fr), spin(fr), 1),
          radius=50, base=(265, 265))
    s.obj("Caja", [shadow("#FF1A2A", 0, 0, 60, 0.7), grad("#F23A44", "#D8182C", 90)[0]],
          lambda fr, u: (952, 453, 265 * grow(fr) * max(0.08, turn(fr)), 265 * grow(fr), spin(fr), 1), radius=50,
          base=(265, 265))
    s.icon("Me gusta", THUMB, solid(WHITE), lambda fr, u: (955, 450, 120 * grow(fr), spin(fr),
                                                           0.0 if bell(fr) else 1.0), aspect=1.15)
    s.icon("Campana", BELL, solid(WHITE), lambda fr, u: (952, 456, 112 * grow(fr), 0, 1.0 if bell(fr) else 0.0),
           aspect=0.92)
    s.icon("Campana (ondas)", RINGS, ring(WHITE, 8), lambda fr, u: (952, 440, 84 * grow(fr), 0,
                                                                   1.0 if bell(fr) else 0.0), aspect=1.7)
    c = s.say("Channel name", (765, 668, 1165, 716), M, 700, "#C8182C", "Canal", op=lambda fr, u: gone(fr))
    s.typed(c, 24, stagger=0.03, duration=0.12, preset="fade")
    c = s.say("S l o g a n   h e r e", (820, 740, 1095, 766), M, 500, "#8A8A8A", "Lema", op=lambda fr, u: gone(fr))
    s.typed(c, 30, stagger=0.02, duration=0.12, preset="fade")
    return t


# --- 24. A gradient blob pill grows lobe by lobe: like, bell, «Channel name» and the avatar (97.1–100.0) ----------
def blob_pill():
    D = 4.8
    t = _btn("pildora-burbujas", "Botón: píldora de burbujas en degradado con avatar",
             "Button: gradient bubble pill with avatar", 12523, D, ["avatar", "degradado", "me gusta", "campana"],
             thumb=2.4)
    s = E(t, D)
    lobes = ((640, 560, 280, 3, "#FF6A30", "#FF4A40"), (770, 560, 250, 9, "#FF5A40", "#FF4A80"),
             (1000, 530, 300, 15, "#FF4AA0", "#C050F0"), (1150, 575, 240, 18, "#E040D0", "#A050F0"))
    for i, (x, y, d, at, c0, c1) in enumerate(lobes):
        s.obj(f"Burbuja {i + 1} (sombra)", solid("#B02A40"), lambda fr, u, x=x, y=y, d=d, at=at: (
            x - 70 * (1 - k(fr, at, 9)) + 6, y + 18, d * pop(fr, at, 9), d * pop(fr, at, 9), 0, 1), kind="ellipse",
            base=(d, d))
    for i, (x, y, d, at, c0, c1) in enumerate(lobes):
        s.obj(f"Burbuja {i + 1}", grad(c0, c1, 330), lambda fr, u, x=x, y=y, d=d, at=at: (
            x - 70 * (1 - k(fr, at, 9)), y, d * pop(fr, at, 9), d * pop(fr, at, 9), 0, 1), kind="ellipse", base=(d, d))
    s.obj("Avatar (aro)", grad("#FF40C0", "#7A50F0", 300), lambda fr, u: (1270, 560, 280 * pop(fr, 21, 9),
                                                                         280 * pop(fr, 21, 9), 0, 1),
          kind="ellipse", base=(280, 280))
    s.avatar("fx-face-03", lambda fr, u: (1270, 560, 240, k(fr, 30, 6)), label="Tu foto de perfil")
    s.icon("Me gusta", THUMB, solid(WHITE), lambda fr, u: (655, 575, 80 * pop(fr, 18, 5), 0, 1), aspect=1.15)
    s.icon("Campana", BELL, solid(WHITE), lambda fr, u: (770, 580, 76 * pop(fr, 24, 5), 0, 1), aspect=0.92)
    s.icon("Campana (ondas)", RINGS, ring(WHITE, 6), lambda fr, u: (770, 570, 58 * pop(fr, 24, 5), 0, 1), aspect=1.7)
    c = s.say("Channel name", (860, 548, 1138, 590), M, 700, WHITE, "Canal")
    s.typed(c, 27, stagger=0.03, duration=0.12, preset="fade", order="random")
    c = s.say("S l o g a n   h e r e", (918, 605, 1130, 630), M, 500, "#4A2A4A", "Lema")
    s.typed(c, 33, stagger=0.02, duration=0.12, preset="fade", order="random")
    return t


# --- 25. Red bubbles: two dots drift apart, the bell bubble glows, the avatar and a like bubble pop (100.1–101.6) ---
def red_bubbles():
    D = 4.6
    t = _btn("burbujas-rojas", "Botón: burbujas rojas con campana, avatar y me gusta",
             "Button: red bubbles with bell, avatar and like", 12524, D, ["avatar", "campana", "me gusta"], thumb=2.4)
    s = E(t, D)
    glow = [shadow("#FF1A1A", 0, 0, 50, 0.8), grad("#FF3A3A", "#C8101A", 120)[0]]
    s.obj("Burbuja", glow, lambda fr, u: (930 - 161 * k(fr, 6, 12), 504 - 127 * k(fr, 6, 12), 50 * k(fr, 0, 4),
                                          50 * k(fr, 0, 4), 0, 1), kind="ellipse", base=(50, 50))
    s.obj("Burbuja 2", glow, lambda fr, u: (930 + 176 * k(fr, 6, 15), 594 + 115 * k(fr, 6, 15), 60 * k(fr, 0, 4),
                                            60 * k(fr, 0, 4), 0, 1), kind="ellipse", base=(60, 60))
    s.obj("Avatar (aro)", [shadow("#FF1A1A", 0, 0, 40, 0.7), fill("#E8202A")],
          lambda fr, u: (962, 527, 338 * pop(fr, 33, 6), 338 * pop(fr, 33, 6), 0, 1), kind="ellipse", base=(338, 338))
    s.obj("Avatar (fondo)", solid(WHITE), lambda fr, u: (962, 527, 300 * k(fr, 34, 5), 300 * k(fr, 34, 5), 0, 1),
          kind="ellipse", base=(300, 300))
    s.avatar("fx-man-02", lambda fr, u: (962, 527, 300, k(fr, 36, 6)), label="Tu foto de perfil")
    s.obj("Me gusta (burbuja)", glow, lambda fr, u: (1181, 471, 150 * pop(fr, 36, 6), 150 * pop(fr, 36, 6), 0, 1),
          kind="ellipse", base=(150, 150))
    s.icon("Me gusta", THUMB, solid(WHITE), lambda fr, u: (1181, 471, 60 * pop(fr, 36, 6), 0, 1), aspect=1.15)
    bell_d = lambda fr: 238 * (0.25 * k(fr, 12, 6) + 0.75 * pop(fr, 18, 12))  # noqa: E731
    s.obj("Campana (burbuja)", glow, lambda fr, u: (719 + 211 * (1 - k(fr, 18, 15)), 565 + 30 * (1 - k(fr, 18, 15)),
                                                    bell_d(fr), bell_d(fr), 0, 1), kind="ellipse", base=(238, 238))
    s.icon("Campana", BELL, solid(WHITE), lambda fr, u: (719 + 211 * (1 - k(fr, 18, 15)), 565 + 30 * (1 - k(fr, 18, 15)),
                                                         bell_d(fr) * 0.4, 0, 1), aspect=0.92)
    s.icon("Campana (ondas)", RINGS, ring(WHITE, 7), lambda fr, u: (719 + 211 * (1 - k(fr, 18, 15)),
                                                                   555 + 30 * (1 - k(fr, 18, 15)), bell_d(fr) * 0.3,
                                                                   0, 1), aspect=1.7)
    c = s.say("Channel name", (750, 715, 1156, 760), M, 700, WHITE, "Canal")
    s.typed(c, 39, stagger=0.03, duration=0.1, preset="fade")
    return t


# --- 26. An avatar bubble clicked: a chain drops a like and a bell; each clicked, «Liked» and «Subscribed» --------
def avatar_chain():
    D = 6.2
    t = _btn("avatar-cadena", "Botón: avatar con cadena de me gusta y campana",
             "Button: avatar with a chain of like and bell", 12525, D, ["avatar", "me gusta", "campana", "cursor"],
             thumb=5.0)
    s = B(t, D)
    END = 164
    gone = lambda fr: 1 - k(fr, END, 9)  # noqa: E731
    red = "#E8202A"
    s.rect("Cadena", solid(red), lambda fr, u: (1034, 410, 1046, 410 + 346 * k(fr, 51, 18) * gone(fr)))
    for name, cy, at, d in (("Me gusta", 610, 54, 114), ("Campana", 756, 63, 114)):
        sz = lambda fr, at=at: (0.25 * k(fr, at, 3) + 0.75 * pop(fr, at + 6, 6)) * gone(fr)  # noqa: E731
        s.obj(f"{name} (borde)", solid("#F0A0A8"), lambda fr, u, cy=cy, sz=sz, d=d: (1040, cy, (d + 12) * sz(fr),
                                                                                  (d + 12) * sz(fr), 0, 1),
              kind="ellipse", base=(d + 12, d + 12))
        s.obj(name + " (botón)", solid(red), lambda fr, u, cy=cy, sz=sz, d=d, at=at: (
            1040, cy, d * sz(fr), d * sz(fr), 0, k(fr, at + 6, 3)), kind="ellipse", base=(d, d))
        if name == "Me gusta":
            s.icon(name, THUMB, solid(WHITE), lambda fr, u, cy=cy, sz=sz: (1040, cy, 46 * sz(fr), 0, 1), aspect=1.15)
        else:
            s.icon(name, BELL, solid(WHITE), lambda fr, u, cy=cy, sz=sz: (1040, cy, 48 * sz(fr), 0, 1), aspect=0.92)
            s.icon("Campana (ondas)", RINGS, ring(WHITE, 4), lambda fr, u, cy=cy, sz=sz: (1040, cy - 6, 36 * sz(fr), 0,
                                                                                         k(fr, 117, 4)), aspect=1.7)
    av = lambda fr: (0.15 * k(fr, 0, 3) + 0.85 * pop(fr, 3, 6)) * gone(fr)  # noqa: E731
    s.obj("Avatar (borde)", solid("#F0A0A8"), lambda fr, u: (1040, 410, 205 * av(fr), 205 * av(fr), 0, 1),
          kind="ellipse", base=(205, 205))
    s.obj("Avatar (aro)", [shadow("#FF1A1A", 0, 0, 30, 0.6), fill(red)],
          lambda fr, u: (1040, 410, 193 * av(fr), 193 * av(fr), 0, 1), kind="ellipse", base=(193, 193))
    s.avatar("fx-woman-05", lambda fr, u: (1040, 410, 165 * av(fr), k(fr, 9, 4)), label="Tu foto de perfil")
    c = s.say("Channel name", (614, 363, 914, 403), M, 700, red, "Canal", op=lambda fr, u: gone(fr))
    s.typed(c, 51, stagger=0.03, duration=0.1, preset="fade")
    c = s.say("S l o g a n   h e r e", (680, 418, 940, 448), M, 500, "#9A9A9A", "Lema", op=lambda fr, u: gone(fr))
    s.typed(c, 57, stagger=0.02, duration=0.1, preset="fade")
    c = s.say("Liked", (850, 590, 954, 630), M, 700, WHITE, "Me gusta (texto)", align="right", op=lambda fr, u: gone(fr))
    s.typed(c, 87, stagger=0.05, duration=0.1, preset="fade", order="backward")
    c = s.say("Subscribed", (750, 736, 954, 776), M, 700, WHITE, "Campana (texto)", align="right",
              op=lambda fr, u: gone(fr))
    s.typed(c, 123, stagger=0.04, duration=0.1, preset="fade", order="backward")
    cur = pts((24, 1120, 600), (33, 1052, 430), (45, 1052, 430), (72, 1052, 630), (93, 1052, 630), (108, 1052, 775),
              (126, 1052, 775), (140, 1130, 1100))
    s.cursor(lambda fr: (*cur(fr), max(math.sin(math.pi * lin(fr, 36, 5)), math.sin(math.pi * lin(fr, 80, 5)),
                                       math.sin(math.pi * lin(fr, 114, 5))), k(fr, 24, 3) * (1 - k(fr, 136, 4))),
             size=80)
    return t


TEMPLATES = [subscribe_red, bell_round, avatar_pill, end_soft, end_pink, end_red_blobs, end_purple_card, end_pink_next, play_outline, gradient_bell_pill, red_box_bell, gradient_tab, end_click_rings, end_gradient_ring, end_blue_band, end_teal_waves, end_dont_forget, end_hexagon, liked_round, white_card, end_teal_capsule, end_lilac_card, red_box_flip, blob_pill, red_bubbles, avatar_chain]
