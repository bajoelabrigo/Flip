"""Video 27720858.mp4 as Kit de YouTube Stock templates (yp9-*). See docs/plan-youtube-pack-2.md.

A creator pack on dark grey (1920×1080, 30 fps, 48 s), every element studied on 10 fps sheets and laid out where it
sits in the reference: a lightning bolt, a phone with hearts and likes floating out of it, a play button wiped
clockwise into a photo window that grows to full screen, a yellow «TREND VIDEO» tape over footage with a typed title,
two like buttons (one clicked by a mouse into a burst of doodles, one by an arrow cursor), rising outline hearts over
footage, four subscribe pieces (a play button that turns into a «SUBSCRIBED» sticker, a «CHANNEL NAME» bar with a
bell, a channel card with a round picture, a SUBSCRIBE button clicked into SUBSCRIBED), a profile card with a spinning
logo, an @name badge over footage, a phone feed, two LIVE STREAM titles, social link bars (one grid of twelve and each
network alone), three doodle bursts and a glitch block. Times are the reference's seconds (each piece starts at its
own `O`). Kit de YouTube › Elementos / Redes / Tipografía; order 17200-. Study notes in
tienda/plantillas/estudio-27720858/NOTAS.md.

Brands: the pack's name → «yourname»; the TikTok logo only as a small note glyph, the big spinning logo is the
`logo-flip` slot; the YouTube wordmark of the sticker → the play button; «facebook» on the phone → «social».
"""

from __future__ import annotations

import math
import random

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from scene import gradient, keys, no_stroke, tanim
from templates_tit_c import FPS
from templates_tit_e import solid
from templates_tit_h import TRIANGLE, fill, poly, ring
from templates_yp0 import BELL, BIRD, THUMB, E, L, W, ein, path_at, stroke

WHITE, BLACK = "#FFFFFF", "#000000"
M, AE = "Montserrat", "Anybody Expanded"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium"),
               (400, "Regular")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold")):
    f6._FILES[(AE, _w)] = f"fonts.extra/fonts/anybodyexpanded/AnybodyExpanded-{_f}.ttf"

HOLLOW = {"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}


# --- shapes ---------------------------------------------------------------------------------------------------------
def circle_pts(cx, cy, r, n=28, a0=0.0, a1=360.0):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def path_of(*polys):
    return " ".join(poly(p) for p in polys)


def star_pts(n=5, inner=0.46):
    return [(50 + (50 if i % 2 == 0 else 50 * inner) * math.cos(math.radians(-90 + 180 * i / n)),
             50 + (50 if i % 2 == 0 else 50 * inner) * math.sin(math.radians(-90 + 180 * i / n))) for i in range(2 * n)]


def _moon():
    """A crescent: the circle (50, 50) r 48 minus the circle (68, 34) r 40."""
    (x1, y1, r1), (x2, y2, r2) = (50.0, 50.0, 48.0), (68.0, 34.0, 40.0)
    d = math.hypot(x2 - x1, y2 - y1)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(r1 * r1 - a * a)
    mx, my = x1 + a * (x2 - x1) / d, y1 + a * (y2 - y1) / d
    p = [(mx + h * (y2 - y1) / d, my - h * (x2 - x1) / d), (mx - h * (y2 - y1) / d, my + h * (x2 - x1) / d)]

    def ang(cx, cy, q):
        return math.degrees(math.atan2(q[1] - cy, q[0] - cx))

    def arc(cx, cy, r, q0, q1, outside):
        a0, a1 = ang(cx, cy, q0), ang(cx, cy, q1)
        for sweep in ((a1 - a0) % 360, (a1 - a0) % 360 - 360):
            mid = math.radians(a0 + sweep / 2)
            mxx, myy = cx + r * math.cos(mid), cy + r * math.sin(mid)
            if (math.hypot(mxx - x2, myy - y2) > r2) == outside if (cx, cy) == (x1, y1) else                     (math.hypot(mxx - x1, myy - y1) < r1):
                return [(cx + r * math.cos(math.radians(a0 + sweep * i / 40)),
                         cy + r * math.sin(math.radians(a0 + sweep * i / 40))) for i in range(41)]
        return []
    return arc(x1, y1, r1, p[0], p[1], True) + arc(x2, y2, r2, p[1], p[0], False)


HEART = ("M 50 94 C 22 74 2 56 2 32 C 2 14 15 4 29 4 C 39 4 46 10 50 18 C 54 10 61 4 71 4 C 85 4 98 14 98 32 "
         "C 98 56 78 74 50 94 Z")
STAR = poly(star_pts())
PLUS = poly([(37, 0), (63, 0), (63, 37), (100, 37), (100, 63), (63, 63), (63, 100), (37, 100), (37, 63), (0, 63),
             (0, 37), (37, 37)])
BOLT = poly([(58, 0), (8, 58), (44, 58), (30, 100), (92, 38), (56, 38), (76, 0)])
MOON = poly(_moon())
TRI = poly([(50, 4), (98, 92), (2, 92)])
DOODLES = {"heart": HEART, "star": STAR, "plus": PLUS, "x": PLUS, "bolt": BOLT, "moon": MOON, "tri": TRI}
# Arrow cursor: the tip at (0, 0) of its 100 box.
ARROW = poly([(2, 2), (2, 80), (22, 62), (36, 96), (50, 90), (36, 58), (62, 58)])
# A small note glyph (the social icon), drawn as a ring, a stem and a flag.
NOTE = path_of([(56, 2), (72, 2), (72, 74), (56, 74)],
               [(70, 2), (80, 2), (84, 12), (100, 24), (100, 38), (84, 32), (70, 24)],
               circle_pts(40, 72, 27, 24), list(reversed(circle_pts(40, 72, 12, 16))))


def superellipse(n=4.0, k=48):
    pts = []
    for i in range(k):
        a = 2 * math.pi * i / k
        c, s_ = math.cos(a), math.sin(a)
        pts.append((50 + 50 * math.copysign(abs(c) ** (2 / n), c), 50 + 50 * math.copysign(abs(s_) ** (2 / n), s_)))
    return poly(pts)


SQUIRCLE = superellipse(4.2)


def glow(s, clip, colour, size=14, op=0.85, spread=0.25):
    s.fx(clip, "layer.outer_glow", color=colour, opacity=op, size=size, spread=spread)
    return clip


def keyed(points):
    """f(v) linear through [(v, value)], held outside."""
    def f(v):
        if v <= points[0][0]:
            return points[0][1]
        for (a, va), (b, vb) in zip(points, points[1:]):
            if v <= b:
                return va + (vb - va) * (v - a) / max(1e-6, b - a)
        return points[-1][1]
    return f


EMPTY = "M -50 -50 L -49 -50 L -49 -49 Z"


class P(W):
    """A widget of this video (no background, no automatic exit; every geometry of the reference's second v)."""

    def rtxt(self, content, ink, family, weight, colour, name, reveal, shift, op=None, align="center", layers=None):
        """Text that slides (shift(v) = (dx, dy)) inside a still screen rect reveal(v)."""
        o = self.o
        return self.say(content, ink, family, weight, colour, name, align=align, layers=layers,
                        reveal=lambda fr: reveal(fr / FPS + o), shift=lambda fr: shift(fr / FPS + o),
                        op=(lambda fr, u: op(u + o)) if op else None)

    def type_in(self, clip, at, stagger, duration=0.04, preset="typewriter"):
        """The text types in from second `at` (no exit animation)."""
        clip["textStyle"]["animation"] = {"in": tanim(preset, duration=duration, unit="character", stagger=stagger,
                                                      ease="easeOut", delay=round(max(0.0, at - self.o), 3),
                                                      order="forward")}

    def frames(self, name, layers, box, polys):
        """A shape redrawn every frame: polys(v) = polygons in screen px inside the still box (x0, y0, x1, y1)."""
        x0, y0, x1, y1 = box
        bw, bh = x1 - x0, y1 - y0
        paths, index, kf, last = [], {}, [], None
        for u in frames_of(self.dur):
            ps = polys(u + self.o)
            p = " ".join("M " + " L ".join(f"{(x - x0) / bw * 100:.2f} {(y - y0) / bh * 100:.2f}" for x, y in pts)
                         + " Z" for pts in ps if len(pts) > 2) or EMPTY
            if p not in index:
                index[p] = len(paths)
                paths.append(p)
            if index[p] != last:
                kf.append((u, index[p], "hold"))
                last = index[p]
        clip = self.obj(name, layers, lambda fr, u: ((x0 + x1) / 2, (y0 + y1) / 2, bw, bh, 0, 1), path=paths[0])
        clip["shapeStyle"]["pathShapes"] = paths
        clip["shapeStyle"].setdefault("keyframes", {})["path"] = keys(kf)
        clip["layoutRole"] = "art"
        return clip

    def photo(self, sample, g, base, name="Tu video", label="Tu video", **extra):
        """A photo slot whose box g(v) = (cx, cy, w, h, op) keeps the aspect of base = (w, h)."""
        bw, bh = base
        track = self.t.track("video", name)
        mo, op = [], []
        for u in frames_of(self.dur):
            cx, cy, w, h, o = g(u + self.o)
            mo.append((u, {"sx": max(1e-4, w / bw), "sy": max(1e-4, h / bh), "dx": cx - 960, "dy": cy - 540},
                       "linear"))
            op.append((u, round(max(0.0, min(1.0, o)), 4), "linear"))
        clip = self.t.photo(track, sample, 0.0, self.dur, Box(960 - bw / 2, 540 - bh / 2, bw, bh), mo, label=label,
                            **extra)
        clip["name"] = name
        if any(v[1] < 0.999 for v in op):
            clip["opacity"] = keys(op)
        return clip

    def full_video(self, sample):
        clip = self.photo(sample, lambda v: (960, 540, 1920, 1080, 1.0), (1920, 1080))
        clip["layoutRole"] = "backdrop"
        return clip

    def doodle(self, name, kind, colour, g, size_wh=None, glow_size=12):
        """One doodle; g(v) = (cx, cy, size, rot, op)."""
        w, h = size_wh or (1.0, 1.0)
        extra = 45.0 if kind == "x" else 0.0
        c = self.shp(name, solid(colour), lambda v: (lambda q: (q[0], q[1], q[2] * w, q[2] * h, q[3] + extra, q[4]))(
            g(v)), path=DOODLES[kind])
        if glow_size:
            glow(self, c, colour, glow_size, 0.8)
        return c

    def burst(self, cx, cy, items, cycles, grow=0.3, life=0.6, r0=0.25, name="Destello"):
        """Doodles flying out of (cx, cy): items = (kind, colour, x, y, size) where they sit at the burst's peak;
        each cycle start c: from r0 of the way out to all the way in `grow` s, then a little further while they
        shrink away by c + life."""
        def at(v):
            for c in cycles:
                if c <= v < c + life:
                    return v - c
            return None
        for i, (kind, colour, x, y, size) in enumerate(items):
            spin = (i % 3 - 1) * 25

            def g(v, x=x, y=y, size=size, spin=spin):
                p = at(v)
                if p is None:
                    return cx, cy, 0.0, 0.0, 0.0
                rf = r0 + (1 - r0) * E(p, 0, grow) + 0.15 * L(p, grow, life - grow)
                sc = (0.4 + 0.6 * E(p, 0, 0.12)) * (1 - E(p, life - 0.22, 0.22))
                return cx + (x - cx) * rf, cy + (y - cy) * rf, size * sc, spin * p, 1.0
            self.doodle(f"{name} {i + 1}", kind, colour, g)

    def arrow(self, pts, t_in, t_out, clicks=(), size=(64, 92), name="Cursor"):
        """The arrow pointer: its tip through waypoints [(v, x, y)]."""
        def g(v):
            x, y = path_at(pts, v)
            sc = 1 - sum(0.1 * math.sin(math.pi * L(v, c - 0.08, 0.16)) for c in clicks)
            w, h = size[0] * sc, size[1] * sc
            return x + w / 2 - 0.02 * w, y + h / 2 - 0.02 * h, w, h, 0, E(v, t_in, 0.08) * (1 - E(v, t_out, 0.08))
        self.shp(name, [fill(BLACK), stroke(WHITE, 3.5)], g, path=ARROW, base=size)

    def mouse(self, pts, t_in, t_out, clicks=(), size=(52, 100), name="Mouse"):
        """A black computer mouse (pill with a white wheel) through waypoints [(v, cx, cy)]."""
        def g(v, f=1.0):
            x, y = path_at(pts, v)
            sc = 1 - sum(0.12 * math.sin(math.pi * L(v, c - 0.08, 0.16)) for c in clicks)
            return x, y, size[0] * sc * f, size[1] * sc * f, -8, E(v, t_in, 0.08) * (1 - E(v, t_out, 0.08))
        self.shp(name, [fill("#101010"), stroke("#2A2A2A", 2)], g, radius=size[0] / 2, base=size)
        self.shp(f"{name} (rueda)", solid(WHITE), lambda v: (lambda q: (q[0] + 1, q[1] - size[1] * 0.2, 4, 18, -8,
                                                                         q[5]))(g(v)), radius=2)

    def click_lines(self, x, y, c, r0=40, r1=70, ln=18, colour=WHITE, n=8, name="Clic"):
        for i in range(n):
            a = 360 * i / n - 90

            def g(v, a=a):
                q = L(v, c, 0.3)
                r = r0 + (r1 - r0) * (1 - (1 - q) ** 2)
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                return x + ca * r, y + sa * r, ln * (1 - 0.6 * q), 3, a, 1.0 if c <= v < c + 0.3 else 0.0
            self.shp(f"{name} {i + 1}", solid(colour), g)


def _p(id, es, en, order, O, end, thumb, tags=(), section="elementos"):
    return wide(f"yp9-{id}", es, en, "ytkit", round(end - O, 2), order=order,
                tags=[f"kit:{section}", "youtube"] + list(tags), thumb_at=round(thumb - O, 2))


# --- 1. A line opens into a slanted bar that breaks into a lightning bolt (0.0–2.45 s) -------------------------------
def bolt():
    O, end = 0.0, 2.45
    t = _p("rayo", "Rayo que se arma desde una línea", "Lightning bolt built from a line", 17200, O, end, 1.6,
           ["rayo", "intro"])
    s = P(t, end - O, O)
    # the slanted bar (6 points: top-left, top-middle, top-right, bottom-right, bottom-middle, bottom-left) and the
    # bolt (top tip, inner corner, right tooth, bottom tip, inner corner, left tooth) at full size
    axis = ((1017.5, 447), (918.5, 612))

    def bar(w):
        (ax, ay), (bx, by) = axis
        h = w / 2
        return [(ax - h, ay), (ax, ay), (ax + h, ay), (bx + h, by), (bx, by), (bx - h, by)]
    bolt_pts = [(993, 428), (961, 518), (1024, 518), (930, 650), (958, 568), (892, 568)]

    def polys(v):
        if v < 0.0 or v >= 2.42:
            return []
        if v < 1.0:
            return [bar(max(2.0, 70 * E(v, 0.17, 0.26)))]
        m = E(v, 1.0, 0.22)
        sc = 1 - 0.16 * L(v, 1.25, 0.95)
        pts = [(p[0] + (q[0] - p[0]) * m, p[1] + (q[1] - p[1]) * m) for p, q in zip(bar(70), bolt_pts)]
        return [[(959 + (x - 959) * sc, 539 + (y - 539) * sc) for x, y in pts]]
    c = s.frames("Rayo", solid(WHITE), (860, 400, 1070, 680), polys)
    c["opacity"] = keys([(u, round(E(u + O, 0.0, 0.12) * (1 - E(u + O, 2.22, 0.18)), 4), "linear")
                         for u in frames_of(s.dur)])
    return t


# --- 2. A phone grows from its corner; hearts and likes float out of it (4.15–7.45 s) -------------------------------
def phone_reactions():
    O, end = 4.15, 7.45
    t = _p("telefono-reacciones", "Teléfono con corazones y me gusta", "Phone with hearts and likes", 17201, O, end,
           6.3, ["teléfono", "me gusta", "corazones", "redes"], section="redes")
    s = P(t, end - O, O)
    q = lambda v: max(1e-3, E(v, 4.17, 0.62))  # noqa: E731

    def at(x, y, v):
        k = q(v)
        return 777 + (x - 777) * k, 857 + (y - 857) * k

    def box(x0, y0, x1, y1, op=None, radius=0.0):
        def g(v):
            k = q(v)
            cx, cy = at((x0 + x1) / 2, (y0 + y1) / 2, v)
            return cx, cy, (x1 - x0) * k, (y1 - y0) * k, 0, op(v) if op else E(v, 4.15, 0.05)
        return g
    body = s.shp("Teléfono", solid("#F7F8FA"), box(777, 222, 1143, 857), radius=34, base=(366, 635))
    s.mblur(body)
    s.shp("Pantalla", solid("#E3E6EB"), box(795, 283, 1125, 768), radius=6, base=(330, 485))
    s.shp("Altavoz", solid("#DADDE2"), box(920, 248, 1000, 260), radius=6, base=(80, 12))
    s.shp("Botón", solid("#DADDE2"), box(931, 789, 983, 841), kind="ellipse")
    s.shp("Fondo de la publicación", solid(WHITE), box(802, 362, 1117, 760), base=(315, 398))
    s.rect("Barra", solid("#4267B2"), lambda fr, u: (lambda v: (*at(802, 291, v), *at(
        802 + 315 * E(v, 4.72, 0.22), 358, v)))(u + O))
    s.txt("social", (906, 312, 1014, 338), M, 800, WHITE, "Red", g=lambda v: (0, 0, 1, 0, E(v, 4.9, 0.1)))
    s.shp("Perfil", solid("#D3D7DD"), box(822, 373, 862, 413, op=lambda v: E(v, 4.95, 0.1)))
    for i, (x1, y) in enumerate(((945, 385), (998, 405))):
        s.shp(f"Línea {i + 1}", solid("#D3D7DD"), box(876, y, x1, y + 8, op=lambda v: E(v, 4.98, 0.1)), radius=4)
    ph = s.photo("h-couple-01", lambda v: (960, 590, 290 * 16 / 9, 290, 1.0), (290 * 16 / 9, 290), name="Tu foto",
                 label="Tu foto")
    s.mask_to(ph, lambda v: (815, 735 - 290 * E(v, 4.95, 0.25), 815 + 290 * E(v, 4.95, 0.25), 735))
    rng = random.Random(9)
    # hearts: born on the phone's edges, drift a little outward; likes: born at its sides, fly out to the sides
    hearts, likes = [], []
    tt = 4.45
    while tt < 7.4:
        side = rng.choice((-1, 1))
        x = 960 + side * rng.uniform(150, 230)
        y = rng.uniform(380, 830)
        hearts.append((tt, x, y, side * rng.uniform(30, 90), -rng.uniform(20, 70), rng.uniform(1.3, 2.2)))
        tt += rng.uniform(0.09, 0.16)
    tt = 4.55
    while tt < 7.4:
        side = rng.choice((-1, 1))
        y = rng.uniform(380, 760)
        likes.append((tt, 960 + side * 190, y, side * rng.uniform(220, 380), rng.uniform(-80, 80),
                      rng.uniform(1.6, 2.6)))
        tt += rng.uniform(0.12, 0.2)

    def particle(i, born, x, y, vx, vy, life, colour, kind, r):
        def g(v):
            p = v - born
            if p < 0 or p > life:
                return x, y, 0, 0, 0, 0.0
            sc = E(p, 0, 0.18) * (1 + 0.15 * math.sin(math.pi * L(p, 0, 0.25)))
            op = 1 - E(p, life - 0.3, 0.3)
            return x + vx * p, y + vy * p, 2 * r * sc, 2 * r * sc, 0, op
        s.shp(f"{kind} {i + 1}", solid(colour), g, kind="ellipse", base=(2 * r, 2 * r))
        glyph = HEART if kind == "Corazón" else THUMB
        s.shp(f"{kind} {i + 1} (icono)", solid(WHITE), lambda v: (lambda q_: (q_[0], q_[1] + (2 if glyph == HEART else
                                                                                        -1), q_[2] * 0.52,
                                                                            q_[3] * (0.46 if glyph == HEART else 0.5),
                                                                            0, q_[5]))(g(v)), path=glyph)
    for i, (born, x, y, vx, vy, life) in enumerate(likes):
        particle(i, born, x, y, vx, vy, life, "#3D5FBE", "Me gusta", 40)
    for i, (born, x, y, vx, vy, life) in enumerate(hearts):
        particle(i, born, x, y, vx, vy, life, "#EE2A64", "Corazón", 42)
    return t


# --- 3. A play button slides in, is wiped clockwise into a photo window that grows to full screen (7.85–11.45 s) ----
def button_window():
    O, end = 7.85, 11.45
    t = _p("boton-ventana", "Botón de play que se abre en una ventana de video", "Play button opening into a video "
           "window", 17202, O, end, 9.8, ["youtube", "play", "ventana", "transición"])
    s = P(t, end - O, O)
    cx, cy, bw, bh = 948, 534, 324, 228

    def win(v):
        k = L(v, 10.45, 0.5) ** 3.0
        w = bw + (3000 - bw) * k
        return cx + (960 - cx) * k, cy + (540 - cy) * k, w, w * bh / bw

    def wg(v):
        x, y, w, h = win(v)
        return x, y, w, h, 0, 1.0 if v >= 8.6 else 0.0
    window = s.shp("Ventana", solid(WHITE), wg, path=SQUIRCLE, base=(bw, bh))

    def pg(v):
        x, y, w, h = win(v)
        hh = min(1080.0, max(h, w * 9 / 16))
        return x, y, hh * 16 / 9, hh, 1.0 if v >= 8.6 else 0.0
    ph = s.photo("h-couple-01", pg, (1920, 1080))
    ph["matte"] = {"clip": window["id"], "mode": "alpha"}
    ph["layoutRole"] = "backdrop"
    slide = lambda v: -130 * (1 - E(v, 7.88, 0.24))  # noqa: E731

    def angle(v):
        return -90 + 360 * L(v, 8.63, 0.8) ** 2.2

    def sector(v):
        a0 = angle(v)
        if a0 >= 269.5:
            return []
        return [[(cx, cy)] + circle_pts(cx, cy, 420, 40, a0, 270)]
    red = s.shp("Botón", [gradient([(0.0, "#FF9A00"), (0.42, "#FF1A0E"), (1.0, "#F20000")], angle=45), no_stroke()],
                lambda v: (cx + slide(v), cy, bw, bh, 0, E(v, 7.88, 0.05)), path=SQUIRCLE, base=(bw, bh))
    s.fx(red, "builtin.effects.gaussian_blur", animated={"u_blurRadius": lambda fr, u: 28 * (1 - E(u + O, 7.88, 0.2))})
    s.fx(red, "rgb_split", animated={"amount": lambda fr, u: 22 * (1 - E(u + O, 7.92, 0.42))}, angle=0)
    tri = s.shp("Botón (play)", solid(WHITE), lambda v: (cx + 12 + slide(v), cy, 76, 84, 0, E(v, 8.05, 0.08)),
                path=TRIANGLE)
    for c in (red, tri):
        m = s.frames(f"{c['name']} (barrido)", solid(WHITE), (cx - 430, cy - 430, cx + 430, cy + 430),
                     lambda v: sector(v) if v >= 8.6 else [circle_pts(cx, cy, 420, 40)])
        c["matte"] = {"clip": m["id"], "mode": "alpha"}
    return t


# --- 4. A yellow «TREND VIDEO» tape scrolls over the video; the title types in (11.5–13.8 s) -------------------------
def _tape_text():
    from PIL import ImageFont
    font = ImageFont.truetype(str(f6._STAGE / f6._FILES[(AE, 900)]), 400)
    word = "TREND VIDEO"
    gap = "   "
    size = 580 / (font.getlength(word + gap) / 400)
    content = gap.join([word] * 5)
    bb = font.getbbox(content)
    return content, (bb[2] - bb[0]) / 400 * size, size


def trend_tape():
    O, end = 11.5, 13.8
    t = _p("cinta-tendencia", "Cinta amarilla de tendencia con título", "Yellow trend tape with a title", 17203, O,
           end, 13.0, ["cinta", "tendencia", "título"], section="tipografia")
    s = P(t, end - O, O)
    s.full_video("fx-man-02")
    ang = math.degrees(math.atan(0.4667))
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    s.shp("Cinta", solid("#FFF200"), lambda v: (1200, 138.5, 2700, 110, ang, 1.0))
    content, width, size = _tape_text()
    c0 = -139.0  # the text's centre along the tape at the cut, from the tape's point at x 1200
    cap = size * 0.72
    ink = (1200 - width / 2, 138.5 - cap / 2, 1200 + width / 2, 138.5 + cap / 2)

    def g(v):
        d = c0 + 265 * (v - 11.5)
        return d * ca, d * sa, 1, ang, 1.0
    s.txt(content, ink, AE, 900, "#111111", "Cinta (texto)", g=g)
    late = s.txt("LATEST RELEASE", (193, 840, 562, 862), AE, 800, "#F7E600", "Texto", align="left")
    s.type_in(late, 11.95, 0.03)
    title = s.txt("The Art & Personal Branding", (193, 912, 1697, 975), AE, 900, WHITE, "Título", align="left")
    s.type_in(title, 11.88, 0.026)
    return t


# --- 5. A big like flies in glowing; a mouse clicks it into a burst of doodles; it turns blue and drops (14–17.7 s) --
LIKE_BURST = [("heart", "#F0104A", 1170, 470, 90), ("star", "#1EE6F0", 1255, 460, 80), ("plus", WHITE, 1330, 480, 90),
              ("bolt", "#F5EB14", 1420, 440, 70), ("plus", WHITE, 1320, 395, 50), ("heart", "#F0104A", 1400, 545, 75),
              ("plus", WHITE, 1220, 570, 70), ("star", "#1EE6F0", 1190, 615, 65), ("star", "#1EE6F0", 1425, 630, 95),
              ("bolt", "#F5EB14", 1220, 695, 70), ("plus", WHITE, 1335, 700, 85)]


def like_burst():
    O, end = 13.95, 17.7
    t = _p("me-gusta-destello", "Me gusta que brilla y estalla con un clic", "Glowing like that bursts on a click",
           17204, O, end, 16.1, ["me gusta", "clic", "destello"])
    s = P(t, end - O, O)

    def pos(v):
        k = E(v, 14.0, 0.7)
        return 810 + 477 * k, 708 - 168 * k + 450 * ein(v, 16.8, 0.75), 30 + 175 * k

    def lg(state):
        def g(v):
            x, y, sz = pos(v)
            on = {"white": v < 15.9, "lilac": 15.9 <= v < 16.0, "blue": v >= 16.0}[state]
            pop = 1 + 0.12 * math.sin(math.pi * L(v, 15.95, 0.25))
            return x, y, sz * pop, sz * pop, 0, E(v, 14.0, 0.05) if on else 0.0
        return g
    glow(s, s.shp("Me gusta", solid(WHITE), lg("white"), path=THUMB), WHITE, 110, 0.55, 0.0)
    s.shp("Me gusta (clic)", solid("#C9C6FF"), lg("lilac"), path=THUMB)
    glow(s, s.shp("Me gusta (azul)", solid("#2828F0"), lg("blue"), path=THUMB), "#2828F0", 40, 0.9, 0.1)
    s.mouse([(15.1, 1362, 790), (15.35, 1348, 650), (15.95, 1348, 650)], 15.1, 15.92, clicks=(15.85,))
    s.burst(1300, 560, LIKE_BURST, (16.0,), grow=0.28, life=0.55, r0=0.2)
    return t


# --- 6. A small like pops in; an arrow cursor clicks it blue with sparkles (14.7–17.7 s) -----------------------------
def like_cursor():
    O, end = 14.7, 17.7
    t = _p("me-gusta-cursor", "Me gusta que un cursor vuelve azul", "Like turned blue by a cursor", 17205, O, end,
           16.5, ["me gusta", "clic", "cursor"])
    s = P(t, end - O, O)

    def lg(blue):
        def g(v):
            k = E(v, 14.75, 0.25)
            pop = 1 + 0.15 * math.sin(math.pi * L(v, 16.15, 0.25))
            sz = 152 * (0.15 + 0.85 * k) * pop
            on = (v >= 16.2) == blue
            return 576 + 120 * k, 588 - 48 * k, sz, sz, 0, E(v, 14.72, 0.05) if on else 0.0
        return g
    s.shp("Me gusta", solid(WHITE), lg(False), path=THUMB)
    s.shp("Me gusta (azul)", solid("#2C2CF2"), lg(True), path=THUMB)
    s.click_lines(700, 540, 16.02, r0=95, r1=125, ln=22)
    small = [("heart", "#F0104A", 640, 470, 26), ("star", "#1EE6F0", 690, 455, 24), ("plus", WHITE, 740, 470, 24),
             ("bolt", "#F5EB14", 770, 520, 22), ("star", "#1EE6F0", 770, 590, 24), ("plus", WHITE, 720, 625, 22),
             ("heart", "#F0104A", 660, 620, 22), ("star", "#2EE070", 625, 575, 22), ("plus", "#F5EB14", 615, 515, 20)]
    s.burst(696, 545, small, (16.2,), grow=0.25, life=0.55)
    s.arrow([(15.0, 972, 900), (15.3, 942, 870), (15.4, 798, 726), (15.5, 768, 672), (15.6, 762, 648),
             (15.9, 750, 630), (17.0, 755, 640), (17.1, 798, 690), (17.2, 858, 792), (17.3, 942, 942)], 15.0, 17.27,
            clicks=(16.0,), size=(66, 96))
    return t


# --- 7. Outline hearts rise over the video and go out one by one (17.7–20.1 s) ----------------------------------------
HEARTS = [(318, 360), (626, 440), (864, 415), (1283, 488), (1673, 465), (273, 640), (675, 655), (953, 630), (1548, 755),
          (416, 830), (1180, 825), (715, 950), (997, 990), (1418, 990), (1712, 1020), (428, 1018), (150, 1180),
          (560, 1210), (1030, 1250), (1350, 1180), (1800, 1260), (820, 1330), (300, 1360), (1560, 1380),
          (100, 470), (1880, 640), (1950, 330)]


def rising_hearts():
    O, end = 17.7, 20.1
    t = _p("corazones-flotando", "Corazones que suben sobre el video", "Hearts rising over the video", 17206, O, end,
           18.6, ["corazones", "amor", "video"])
    s = P(t, end - O, O)
    s.full_video("fx-beach-02")
    rng = random.Random(27)
    for i, (x, y) in enumerate(HEARTS):
        ph, amp, off = rng.uniform(0, 6.28), rng.uniform(6, 30), rng.uniform(19.3, 19.95)

        def g(v, x=x, y=y, ph=ph, amp=amp, off=off):
            p = v - 17.7
            return (x + amp * math.sin(ph + p * 2.6), y - 107 * p, 145, 130, 0, 1 - E(v, off, 0.12))
        c = s.shp(f"Corazón {i + 1}", [HOLLOW, stroke(WHITE, 3.2)], g, path=HEART, base=(145, 130))
        glow(s, c, WHITE, 6, 0.5)
    return t


# --- 8. A play button is clicked into a black «SUBSCRIBED» sticker with doodles (20.1–23.35 s) -----------------------
STICKER_BURST = [("moon", "#26E05A", 380, 195, 90), ("star", "#1EE6F0", 478, 182, 80), ("plus", "#F0284A", 548, 190, 100),
                 ("tri", "#F5E11E", 630, 195, 80), ("plus", "#2EE6F0", 540, 115, 55), ("tri", "#F5E11E", 430, 380, 80),
                 ("plus", "#6A2CF0", 556, 418, 95), ("star", "#1EE6F0", 640, 355, 95),
                 ("star", "#1EE6F0", 405, 345, 60)]


def sticker():
    O, end = 20.1, 23.35
    t = _p("sticker-suscrito", "Botón de play que se vuelve sticker de suscrito", "Play button turning into a "
           "subscribed sticker", 17207, O, end, 22.4, ["suscríbete", "sticker", "clic"])
    s = P(t, end - O, O)
    s.yt("YouTube", lambda fr, u: (lambda v: (522, 282, E(v, 20.15, 0.3) * (1 - E(v, 21.92, 0.12)), 0,
                                                1.0 if v < 22.05 else 0.0))(u + O), w=150, h=105, red="#FF0000")
    s.burst(518, 280, STICKER_BURST, (22.15,), grow=0.22, life=0.6, r0=0.3)

    def sg(v):
        k = E(v, 22.05, 0.2)
        pop = 1 + 0.08 * math.sin(math.pi * L(v, 22.12, 0.25))
        sc = (0.3 + 0.7 * k) * pop * (1 - E(v, 23.12, 0.18))
        return sc, 1.0 if v >= 22.05 else 0.0
    s.shp("Sticker", solid("#141414"), lambda v: (518.5, 280.5, 347 * sg(v)[0], 105 * sg(v)[0], -1, sg(v)[1]),
          radius=24, base=(347, 105))
    s.txt("SUBSCRIBED", (386, 266, 650, 296), M, 800, WHITE, "Suscrito",
          g=lambda v: (0, 0, sg(v)[0], -1, sg(v)[1]))
    s.mouse([(21.2, 252, 600), (21.7, 580, 355), (21.9, 582, 352), (22.1, 640, 470)], 21.2, 22.02, clicks=(21.85,))
    return t


# --- 9. A white bar opens leftward into «CHANNEL NAME» with a bell; it turns purple and falls away (20.1–24.15 s) -----
def channel_bar():
    O, end = 20.1, 24.15
    t = _p("barra-canal", "Barra del canal con campana", "Channel name bar with a bell", 17208, O, end, 22.6,
           ["barra", "canal", "campana", "suscríbete"])
    s = P(t, end - O, O)
    purple = "#6A00F4"
    white_l = keyed([(20.6, 1606), (20.7, 1572), (20.8, 1470), (20.9, 1260), (21.0, 1188), (21.1, 1152),
                     (21.2, 1116), (21.3, 1097)])
    lead_l = keyed([(20.15, 1600), (20.6, 1590), (20.7, 1512), (20.8, 1338), (20.9, 1188), (21.0, 1140),
                    (21.1, 1116), (21.2, 1100), (21.3, 1097)])
    cx0, cy0 = 1351.5, 292

    def out(v):
        k = ein(v, 23.6, 0.5)
        return 22 * k, 268 * k, 1 - 0.75 * k, 1.0 if v < 24.08 else 0.0

    def place(x, y, v):
        rot, dy, sc, _ = out(v)
        a = math.radians(rot)
        dx_, dy_ = (x - cx0) * sc, (y - cy0) * sc
        return cx0 + dx_ * math.cos(a) - dy_ * math.sin(a), cy0 + dy + dx_ * math.sin(a) + dy_ * math.cos(a)

    def rect_g(x0, x1, colour_on):
        def g(v):
            a, b = x0(v), x1(v)
            rot, _, sc, op = out(v)
            x, y = place((a + b) / 2, 292, v)
            return x, y, max(0.0, b - a) * sc, 84 * sc, rot, op * colour_on(v)
        return g
    s.shp("Barra", solid(WHITE), rect_g(white_l, lambda v: 1606, lambda v: 1.0 if 20.6 <= v < 22.2 else 0.0))
    s.shp("Barra (borde)", solid(purple), rect_g(lead_l, white_l, lambda v: 1.0 if 20.15 <= v < 22.2 else 0.0))
    s.shp("Barra (lila)", solid("#D6C6FF"), rect_g(lambda v: 1097, lambda v: 1606, lambda v: 1.0 if 22.2 <= v < 22.3
                                                    else 0.0))
    s.shp("Barra (morada)", solid(purple), rect_g(lambda v: 1097, lambda v: 1606, lambda v: 1.0 if v >= 22.3 else 0.0))
    ink = (1208, 278, 1484, 306)

    def tg(on):
        def g(v):
            rot, _, sc, op = out(v)
            x, y = place(1346, 292, v)
            return x - 1346, y - 292, sc, rot, op * on(v)
        return g
    s.txt("CHANNEL NAME", ink, M, 800, purple, "Nombre del canal (oscuro)", editable=False,
          g=tg(lambda v: E(v, 21.2, 0.12) if v < 22.3 else 0.0))
    s.txt("CHANNEL NAME", ink, M, 800, WHITE, "Nombre del canal", g=tg(lambda v: 1.0 if v >= 22.3 else 0.0))

    def bell(v):
        rot, _, sc, op = out(v)
        x, y = place(1652, 292, v)
        k = E(v, 21.45, 0.15)
        wig = 18 * math.sin(2 * math.pi * (v - 22.2) / 0.25) * math.exp(-(v - 22.2) * 4) if v > 22.2 else 0
        return x, y, 44 * k * sc, 52 * k * sc, rot + wig, op
    s.shp("Campana", solid(WHITE), bell, path=BELL)
    rng = random.Random(5)
    for i in range(16):
        x = rng.uniform(1110, 1600)
        y = rng.choice((rng.uniform(195, 235), rng.uniform(350, 395)))
        a = 22.2 + rng.uniform(0, 0.15)
        sz = rng.uniform(12, 24)
        s.shp(f"Chispa {i + 1}", solid("#8E8984"), lambda v, x=x, y=y, a=a, sz=sz: (
            x, y - 15 * L(v, a, 0.6), sz * math.sin(math.pi * L(v, a, 0.6)), sz * math.sin(math.pi * L(v, a, 0.6)) * 0.9,
            0, 0.8 if a <= v < a + 0.6 else 0.0), path=HEART)
    return t


# --- 10. Channel card: a round picture pops, the name and line type in, SUBSCRIBE swings in and is clicked -----------
def channel_card():
    O, end = 20.55, 24.25
    t = _p("tarjeta-canal", "Tarjeta del canal con foto redonda y suscribirse", "Channel card with a round picture "
           "and subscribe", 17209, O, end, 23.4, ["tarjeta", "canal", "suscríbete", "clic"])
    s = P(t, end - O, O)
    px, py = 492, 700

    def out(v):
        k = E(v, 23.85, 0.35)
        return 1 - 0.35 * k, 230 * k, 1.0 if v < 24.2 else 0.0

    def place(x, y, v):
        sc, dy, _ = out(v)
        return px + (x - px) * sc, py + (y - py) * sc + dy
    pop = lambda v: E(v, 20.6, 0.25) * (1 + 0.06 * math.sin(math.pi * L(v, 20.72, 0.25)))  # noqa: E731

    def ag(v, d):
        sc, _, op = out(v)
        x, y = place(492, 642, v)
        return x, y, d * pop(v) * sc, d * pop(v) * sc, 0, op * (1.0 if v >= 20.6 else 0.0)
    s.shp("Aro", [fill("#2EF0A0")], lambda v: ag(v, 212), kind="ellipse", base=(212, 212))
    av = s.photo("fx-man-01", lambda v: (lambda g: (g[0], g[1], g[2], g[3], g[5]))(ag(v, 190)), (190, 190),
                 name="Foto del canal", label="Tu foto")
    s.t.mask(next(tr for tr in s.t.tracks if av in tr.clips), av, "ellipse")

    def tg(cx, cy):
        def g(v):
            sc, _, op = out(v)
            x, y = place(cx, cy, v)
            return x - cx, y - cy, sc, 0, op
        return g
    name = s.txt("Daniel Ramos", (230, 768, 810, 832), M, 700, WHITE, "Nombre", g=tg(520, 800))
    s.type_in(name, 20.6, 0.075)
    line = s.txt("News | Business & Economics", (217, 850, 813, 884), M, 500, WHITE, "Texto", g=tg(515, 867))
    s.type_in(line, 21.1, 0.045)

    def bg_(after):
        def g(v):
            sc, _, op = out(v)
            k = E(v, 22.2, 0.25)
            rot = 8 * (1 - k) + 3 * k * (1 - E(v, 22.45, 0.2))
            press = 1 - 0.06 * math.sin(math.pi * L(v, 22.62, 0.16))
            x, y = place(517.5, 962 + 70 * (1 - k), v)
            hit = v >= 22.7
            return x, y, 359 * sc * press, 80 * sc * press, rot, op * (E(v, 22.2, 0.05) if hit == after else 0.0)
        return g
    s.shp("Botón", solid("#E00000"), bg_(False), base=(359, 80))
    s.shp("Botón (suscrito)", solid("#C4C4C4"), bg_(True), base=(359, 80))

    def btg(after):
        def g(v):
            x, y, w, h, rot, op = bg_(after)(v)
            return x - 517.5, y - 970, w / 359, rot, op
        return g
    s.txt("SUBSCRIBE", (399, 951, 636, 989), M, 800, WHITE, "Suscribirse", g=btg(False))
    s.txt("SUBSCRIBED", (380, 944, 655, 982), M, 800, "#333333", "Suscrito", g=btg(True))
    s.mouse([(22.3, 690, 1120), (22.5, 665, 1030), (22.75, 665, 1030), (23.1, 700, 1160)], 22.3, 23.05,
            clicks=(22.65,))
    return t


# --- 11. SUBSCRIBE: a black bar opens, red fills it; an arrow clicks it into a grey SUBSCRIBED (20.15–24.45 s) --------
def subscribe_button():
    O, end = 20.15, 24.45
    t = _p("boton-suscribirse", "Botón suscribirse que se rellena y se clica", "Subscribe button that fills and is "
           "clicked", 17210, O, end, 22.9, ["suscríbete", "botón", "clic", "cursor"])
    s = P(t, end - O, O)
    black_r = keyed([(20.2, 1292), (20.5, 1295), (20.6, 1332), (20.7, 1512), (20.8, 1590), (20.9, 1615), (21.0, 1632)])
    red_r = keyed([(20.85, 1290), (20.9, 1350), (21.0, 1380), (21.1, 1572), (21.2, 1640)])

    def out(v):
        k = E(v, 24.2, 0.25)
        return 1 - 0.85 * k, 1.0 if v < 24.43 else 0.0

    def place(x, y, v):
        sc, _ = out(v)
        return 1570 + (x - 1570) * sc, 870 + (y - 870) * sc
    s.rect("Barra negra", solid("#0E0E0E"), lambda fr, u: (lambda v: (1290, 765, black_r(v), 832))(u + O),
           op=lambda fr, u: (lambda v: (1.0 if 20.2 <= v < 21.25 else 0.0))(u + O))

    def bt(v, after):
        sc, op = out(v)
        press = 1 - 0.06 * math.sin(math.pi * L(v, 22.27, 0.16))
        if after:
            x, y = place(1463.5, 795.5, v)
            k = 1 + 0.08 * math.sin(math.pi * L(v, 22.45, 0.25))
            return x, y, 359 * sc * k, 79 * sc * k, 0, op * (1.0 if v >= 22.45 else 0.0)
        r = red_r(v)
        x, y = place((1290 + r) / 2, 798.5, v)
        return x, y, (r - 1290) * sc * press, 67 * sc * press, 0, op * (1.0 if 20.85 <= v < 22.45 else 0.0)
    s.shp("Botón", solid("#E00000"), lambda v: bt(v, False))
    s.shp("Botón (suscrito)", solid("#C4C4C4"), lambda v: bt(v, True))

    def tg(cx, cy, after):
        def g(v):
            sc, op = out(v)
            x, y = place(cx, cy, v)
            on = (v >= 22.45) == after
            return x - cx, y - cy, sc, 0, op * ((E(v, 21.15, 0.1) if not after else 1.0) if on else 0.0)
        return g
    s.txt("SUBSCRIBE", (1381, 786, 1588, 812), M, 800, WHITE, "Suscribirse", g=tg(1484.5, 799, False))
    s.txt("SUBSCRIBED", (1327, 781, 1601, 811), M, 800, "#3A3A3A", "Suscrito", g=tg(1464, 796, True))
    s.click_lines(1612, 790, 22.33, r0=36, r1=62, ln=18)
    small = [("star", "#2EE070", 1300, 740, 30), ("plus", "#F5E11E", 1380, 720, 26), ("moon", "#2EE070", 1520, 725, 28),
             ("tri", "#F5E11E", 1610, 745, 30), ("star", "#1EE6F0", 1650, 830, 30), ("plus", "#2EE070", 1560, 870, 26),
             ("star", "#F5E11E", 1420, 875, 28), ("moon", "#2EE070", 1290, 850, 26)]
    s.burst(1463, 795, small, (22.45,), grow=0.25, life=0.5, r0=0.4)
    s.arrow([(21.7, 1632, 920), (21.85, 1620, 870), (22.2, 1606, 815), (22.3, 1612, 805), (22.6, 1612, 805),
             (23.4, 1660, 960)], 21.7, 23.45, clicks=(22.3,), size=(70, 100))
    return t


# --- 12. Profile card: a spinning logo, round picture, @name, Follow, counters (24.45–27.25 s) ------------------------
def profile():
    O, end = 24.45, 27.25
    t = _p("perfil", "Perfil con foto, seguir y contadores", "Profile with picture, follow button and counters",
           17211, O, end, 26.2, ["perfil", "seguir", "contador", "redes"], section="redes")
    s = P(t, end - O, O)
    s.rect("Fondo", solid("#282828"), lambda fr, u: (-10, -10, 1930, 1090))
    logo = s.photo("logo-flip", lambda v: (680, 550, 190, 190, 1.0), (190, 190), name="Logo", label="Tu logo",
                   brandRole="logo")
    logo["layoutRole"] = "art"
    s.d3(logo, ry=lambda fr, u: 360 * u / 1.6, persp=1400)
    av = s.photo("fx-woman-05", lambda v: (938, 351, 200 * E(v, 24.85, 0.25), 200 * E(v, 24.85, 0.25),
                                           1.0 if v >= 24.85 else 0.0), (200, 200), name="Foto del perfil",
                 label="Tu foto")
    s.t.mask(next(tr for tr in s.t.tracks if av in tr.clips), av, "ellipse")
    name = s.txt("@yourname", (838, 488, 1000, 516), M, 700, WHITE, "Usuario", align="left")
    s.type_in(name, 25.0, 0.07)
    s.rect("Seguir", solid("#EE1D52"), lambda fr, u: (lambda v: (845, 551, 845 + 326 * E(v, 24.95, 0.35), 647))(u + O),
           op=lambda fr, u: (lambda v: (1.0 if 24.8 <= v < 26.7 else 0.0))(u + O))
    s.rect("Seguir (gris)", solid("#4D4D4D"), lambda fr, u: (845, 551, 1171, 647),
           op=lambda fr, u: (lambda v: (1.0 if v >= 26.7 else 0.0))(u + O))
    s.txt("Follow", (960, 588, 1053, 612), M, 600, WHITE, "Seguir (texto)", g=lambda v: (0, 0, 1, 0, E(v, 25.3, 0.1)))
    for i, x0 in enumerate((1204, 1332)):
        s.rect(f"Cuadro {i + 1}", solid(WHITE), lambda fr, u, x0=x0: (lambda v: (
            x0 + 51 - 51 * max(0.04, E(v, 25.2, 0.3)), 548, x0 + 51 + 51 * max(0.04, E(v, 25.2, 0.3)), 650))(u + O),
            op=lambda fr, u: (lambda v: (1.0 if v >= 24.8 else 0.0))(u + O))
    gop = lambda v: E(v, 25.45, 0.1)  # noqa: E731
    s.shp("Instagram (marco)", [HOLLOW, stroke(BLACK, 5.5)], lambda v: (1255, 599, 52, 52, 0, gop(v)), radius=15)
    s.shp("Instagram (lente)", ring(BLACK, 5.5), lambda v: (1255, 599, 24, 24, 0, gop(v)), kind="ellipse")
    s.shp("Instagram (punto)", solid(BLACK), lambda v: (1269, 585, 7, 7, 0, gop(v)), kind="ellipse")
    s.shp("Más", solid(BLACK), lambda v: (1383, 598, 18, 14, 180, gop(v)), path="M 50 0 L 100 100 L 0 100 Z")
    for num, ink, lab, link in (("500", (857, 724, 911, 750), "Following", (836, 760, 930, 780)),
                                ("4300", (1017, 724, 1093, 750), "Followers", (1009, 760, 1100, 780)),
                                ("74840", (1168, 724, 1263, 750), "Likes", (1191, 760, 1240, 780))):
        c = s.txt(num, ink, M, 700, WHITE, lab, g=lambda v: (0, 0, 1, 0, E(v, 24.9, 0.1)))
        c["textStyle"].update(counter=True, counterFrom=0, counterSeconds=1.15, counterCurve="linear")
        s.txt(lab, link, M, 400, "#CFCFCF", f"{lab} (texto)", g=lambda v: (0, 0, 1, 0, E(v, 25.0, 0.15)))
    return t


# --- 13. @name badge: a black square rises with the note glyph, a black bar opens with the name (27.35–30.95 s) ------
def name_badge():
    O, end = 27.35, 30.95
    t = _p("etiqueta-usuario", "Etiqueta con icono y @usuario", "Badge with an icon and @username", 17212, O, end,
           29.6, ["usuario", "redes", "etiqueta"], section="redes")
    s = P(t, end - O, O)
    s.full_video("fx-face-04")
    shift = lambda v: -44 * E(v, 29.15, 0.35)  # noqa: E731
    half = keyed([(27.4, 40), (27.5, 80)])
    top = keyed([(27.4, 946), (27.45, 946), (27.6, 939), (27.75, 908), (27.9, 836), (28.0, 809), (28.1, 793),
                 (28.2, 788)])
    s.rect("Cuadro", solid(BLACK), lambda fr, u: (lambda v: (266 - half(v) + shift(v), top(v), 266 + half(v) + shift(v),
                                                              948))(u + O),
           op=lambda fr, u: (lambda v: (1.0 if v >= 27.4 else 0.0))(u + O))
    sq = lambda v: (186 + shift(v), 788, 346 + shift(v), 948)  # noqa: E731
    rise = lambda v: 90 * (1 - E(v, 27.85, 0.25))  # noqa: E731
    for name, colour, d in (("Icono (cian)", "#25F4EE", (-3, -3)), ("Icono (rosa)", "#FE2C55", (3, 3)),
                            ("Icono", WHITE, (0, 0))):
        c = s.shp(name, solid(colour), lambda v, d=d: (266 + d[0] + shift(v), 840 + d[1] + rise(v), 60, 74, 0,
                                                       1.0 if v >= 27.8 else 0.0), path=NOTE)
        s.mask_to(c, sq)
    s.txt("FOLLOW", (216, 905, 316, 925), M, 800, WHITE, "Etiqueta", g=lambda v: (shift(v), 0, 1, 0, E(v, 28.1, 0.1)))
    bar_r = keyed([(28.1, 360), (28.2, 365), (28.4, 395), (28.6, 505), (28.8, 760), (29.0, 914)])
    s.rect("Barra", solid(BLACK), lambda fr, u: (lambda v: (359 + shift(v), 788, bar_r(v) + shift(v), 948))(u + O),
           op=lambda fr, u: (lambda v: (1.0 if v >= 28.1 else 0.0))(u + O))
    s.rtxt("@yourname", (395, 842, 765, 905), M, 600, WHITE, "Usuario",
           reveal=lambda v: (359 + shift(v), 788, bar_r(v) + shift(v), 948),
           shift=lambda v: (shift(v), 90 * (1 - E(v, 28.5, 0.22))), align="left")
    return t


# --- 14. A phone feed on white: the icons pop, the caption types, the video fades in (30.95–33.8 s) -------------------
def phone_feed():
    O, end = 30.95, 33.8
    t = _p("telefono-feed", "Teléfono con video vertical y botones", "Phone with a vertical video and buttons", 17213,
           O, end, 33.0, ["teléfono", "vertical", "redes", "me gusta"], section="redes")
    s = P(t, end - O, O)
    s.rect("Fondo", solid(WHITE), lambda fr, u: (-10, -10, 1930, 1090))
    s.shp("Teléfono", solid("#0B0B0B"), lambda v: (960, 539.5, 452, 929, 0, 1.0), radius=28)
    vid = s.photo("h-couple-01", lambda v: (960, 531, 782 * 16 / 9, 782, 1.0), (782 * 16 / 9, 782), name="Tu video")
    s.mask_to(vid, lambda v: (734, 140, 1186, 922))
    s.rect("Pantalla gris", solid("#8E8E8E"), lambda fr, u: (734, 140, 1186, 922),
           op=lambda fr, u: 1 - E(u + O, 31.6, 0.4))
    s.txt("Following", (872, 100, 960, 118), M, 500, "#BDBDBD", "Pestaña")
    s.txt("For You", (990, 100, 1058, 118), M, 700, WHITE, "Pestaña 2")
    s.shp("Punto", solid("#FE2C55"), lambda v: (963, 99, 8, 8, 0, 1.0), kind="ellipse")

    def pop(at, x, y, w, h):
        return lambda v: (x, y, w * E(v, at, 0.15) * (1 + 0.12 * math.sin(math.pi * L(v, at + 0.05, 0.2))),
                          h * E(v, at, 0.15) * (1 + 0.12 * math.sin(math.pi * L(v, at + 0.05, 0.2))), 0,
                          1.0 if v >= at else 0.0)
    s.shp("Perfil (aro)", solid(WHITE), pop(31.25, 1130, 433, 68, 68), kind="ellipse")
    face = s.photo("fx-man-01", lambda v: (lambda g: (g[0], g[1], g[2] * 62 / 68, g[3] * 62 / 68, g[5]))(
        pop(31.25, 1130, 433, 68, 68)(v)), (62, 62), name="Foto del perfil", label="Tu foto")
    s.t.mask(next(tr for tr in s.t.tracks if face in tr.clips), face, "ellipse")
    s.shp("Seguir", solid("#FE2C55"), pop(31.3, 1130, 467, 26, 26), kind="ellipse")
    s.shp("Seguir (+)", solid(WHITE), pop(31.3, 1130, 467, 13, 13), path=PLUS)
    s.shp("Corazón", solid(WHITE), pop(31.35, 1130, 550, 56, 50), path=HEART)
    s.shp("Comentario", solid(WHITE), pop(31.45, 1130, 660, 56, 50), kind="ellipse")
    for i in range(3):
        s.shp(f"Comentario (punto {i + 1})", solid("#111111"), pop(31.5, 1117 + 13 * i, 660, 7, 7), kind="ellipse")
    s.shp("Compartir", solid(WHITE), pop(31.55, 1130, 775, 54, 44),
          path=poly([(55, 0), (100, 45), (55, 90), (55, 64), (24, 66), (0, 100), (4, 62), (24, 34), (55, 30)]))
    s.shp("Disco", solid("#2A2A2A"), pop(31.65, 1130, 877, 66, 66), kind="ellipse")
    s.shp("Disco (centro)", [gradient([(0.0, "#F5A623"), (0.5, "#D0021B"), (1.0, "#4A90E2")], angle=45), no_stroke()],
          pop(31.7, 1130, 877, 34, 34), kind="ellipse")
    for txt, ink, at in (("1378", (1115, 581, 1145, 594), 31.4), ("47", (1121, 697, 1138, 709), 31.5),
                         ("234", (1117, 804, 1142, 817), 31.6)):
        s.txt(txt, ink, M, 700, WHITE, f"Contador {txt}", g=lambda v, at=at: (0, 0, 1, 0, E(v, at, 0.1)))
    user = s.txt("@yourname", (759, 752, 880, 774), M, 600, WHITE, "Usuario", align="left")
    s.type_in(user, 31.45, 0.02)
    for i, (line, x1) in enumerate((("What is going on here?", 960), ("I think it's a great opportunity", 1000),
                                    ("for everybody in this", 932), ("world.", 812))):
        y = 792 + 22 * i
        c = s.txt(line, (759, y, x1, y + 14), M, 400, WHITE, f"Texto {i + 1}", align="left")
        s.type_in(c, 31.55 + 0.12 * i, 0.012)
    s.txt("♫  original   Audiotrack - yourname", (762, 895, 1036, 909), M, 500, WHITE, "Música", align="left",
          g=lambda v: (0, 0, 1, 0, E(v, 31.7, 0.15)))
    # the bar at the bottom: home, search, the plus, inbox, profile
    s.shp("Inicio", solid(WHITE), lambda v: (780, 958, 38, 36, 0, 1.0),
          path=poly([(50, 0), (100, 45), (88, 45), (88, 100), (12, 100), (12, 45), (0, 45)]))
    s.shp("Buscar", ring(WHITE, 4), lambda v: (867, 954, 28, 28, 0, 1.0), kind="ellipse")
    s.shp("Buscar (mango)", solid(WHITE), lambda v: (882, 970, 14, 4, 45, 1.0))
    for name, colour, dx in (("Crear (cian)", "#25F4EE", -5), ("Crear (rosa)", "#FE2C55", 5), ("Crear", WHITE, 0)):
        s.shp(name, solid(colour), lambda v, dx=dx: (960 + dx, 958, 54, 36, 0, 1.0), radius=8)
    s.shp("Crear (+)", solid(BLACK), lambda v: (960, 958, 18, 18, 0, 1.0), path=PLUS)
    s.shp("Mensajes", [HOLLOW, stroke(WHITE, 3.5)], lambda v: (1053, 955, 38, 30, 0, 1.0), radius=4)
    s.shp("Perfil (cabeza)", ring(WHITE, 3.5), lambda v: (1144, 949, 16, 16, 0, 1.0), kind="ellipse")
    s.shp("Perfil (hombros)", [HOLLOW, stroke(WHITE, 3.5)], lambda v: (1144, 972, 30, 14, 0, 1.0),
          path="M 0 100 C 0 20 100 20 100 100")
    return t


# --- 15. LIVE / STREAM in red and black boxes rising off two lines, with an antenna (33.85–38.0 s) --------------------
def live_red():
    O, end = 33.85, 38.0
    t = _p("live-stream-rojo", "Título LIVE STREAM en cajas roja y negra", "LIVE STREAM title in red and black boxes",
           17214, O, end, 36.5, ["directo", "live", "transmisión"], section="tipografia")
    s = P(t, end - O, O)
    s.rect("Línea roja", solid("#E00000"), lambda fr, u: (lambda v: (354, 536, 354 + 270 * E(v, 33.9, 0.2), 540))(u + O),
           op=lambda fr, u: 1.0 if u + O >= 33.9 else 0.0)
    up1 = lambda v: 100 * (1 - E(v, 34.05, 0.3))  # noqa: E731
    s.rect("Caja roja", solid("#E00000"), lambda fr, u: (lambda v: (354, min(540, 440 + up1(v)), 624, 540))(u + O))
    s.rtxt("LIVE", (376, 456, 598, 525), M, 900, WHITE, "Título", reveal=lambda v: (0, 0, 1920, 540),
           shift=lambda v: (0, up1(v)))
    s.rect("Línea negra", solid("#000000"), lambda fr, u: (lambda v: (354, 636, 354 + 464 * E(v, 34.2, 0.2), 640))(u + O),
           op=lambda fr, u: 1.0 if u + O >= 34.2 else 0.0)
    up2 = lambda v: 100 * (1 - E(v, 34.55, 0.3))  # noqa: E731
    s.rect("Caja negra", solid("#000000"), lambda fr, u: (lambda v: (354, max(540, min(640, 540 + up2(v))), 818,
                                                                      640))(u + O))
    s.rtxt("STREAM", (370, 556, 797, 625), M, 900, WHITE, "Título 2", reveal=lambda v: (0, 540, 1920, 640),
           shift=lambda v: (0, up2(v)))
    s.rect("Antena", solid("#000000"), lambda fr, u: (lambda v: (748, 540 - 90 * E(v, 35.15, 0.15), 756, 540))(u + O))
    s.shp("Antena (punto)", solid(BLACK), lambda v: (752, 452, 18 * E(v, 35.2, 0.12), 18 * E(v, 35.2, 0.12), 0, 1.0),
          kind="ellipse")
    for i, (r, w) in enumerate(((17, 4), (30, 4), (45, 3.5), (60, 3), (74, 1.6))):
        s.shp(f"Onda {i + 1}", ring(WHITE, w), lambda v, r=r, i=i: (
            752, 452, 2 * r * (0.6 + 0.4 * E(v, 35.25 + 0.06 * i, 0.15)), 2 * r * (0.6 + 0.4 * E(v, 35.25 + 0.06 * i,
                                                                                                0.15)), 0,
            E(v, 35.25 + 0.06 * i, 0.08) * (0.75 + 0.25 * math.cos(2 * math.pi * (v - 35.6 - 0.12 * i) / 1.2))),
            kind="ellipse", base=(2 * r, 2 * r))
    return t


# --- 16. LIVE / STREAM in white rising from below, a small play dot between them (34.35–38.0 s) ----------------------
def live_white():
    O, end = 34.35, 38.0
    t = _p("live-stream-blanco", "Título LIVE STREAM blanco con botón", "White LIVE STREAM title with a button",
           17215, O, end, 36.5, ["directo", "live", "transmisión"], section="tipografia")
    s = P(t, end - O, O)
    s.rtxt("LIVE", (1205, 438, 1427, 508), M, 900, WHITE, "Título", reveal=lambda v: (0, 0, 1920, 512),
           shift=lambda v: (0, 80 * (1 - E(v, 34.4, 0.3))))
    s.rtxt("STREAM", (1103, 556, 1527, 626), M, 900, WHITE, "Título 2", reveal=lambda v: (0, 0, 1920, 630),
           shift=lambda v: (0, 80 * (1 - E(v, 34.75, 0.3))))
    k = lambda v: E(v, 35.35, 0.15) * (1 + 0.1 * math.sin(math.pi * L(v, 35.42, 0.2)))  # noqa: E731
    s.shp("Botón", solid("#1E1E1E"), lambda v: (1314, 533, 76 * k(v), 76 * k(v), 0, 1.0 if v >= 35.35 else 0.0),
          kind="ellipse")
    s.shp("Botón (play)", solid("#D10000"), lambda v: (1318, 533, 26 * k(v), 30 * k(v), 0, 1.0 if v >= 35.35 else 0.0),
          path=TRIANGLE)
    return t


# --- 17. Social link bars: each opens from a line in its middle and closes back into it (38.05–43.75 s) -------------
NETS = [("behance", "#0A4FD8", (57, 322)), ("google", "#D63B3F", (55, 450)), ("patreon", "#E0242C", (59, 576)),
        ("telegram", "#2FA9DE", (57, 710)), ("dribbble", "#E0457B", (675, 322)), ("instagram", "#D60DBA", (677, 444)),
        ("soundcloud", "#F26B11", (677, 572)), ("twitter", "#1DA1F2", (677, 710)), ("facebook", "#1877F2", (1291, 320)),
        ("itunes", "#A23BEB", (1293, 440)), ("spotify", "#2EDB64", (1293, 572)), ("vimeo", "#1AB7EA", (1297, 710))]
OPEN = keyed([(38.1, 2), (38.2, 8), (38.3, 20), (38.4, 40), (38.5, 62), (38.6, 105), (38.7, 310), (38.75, 480),
              (38.8, 580)])
CLOSE = keyed([(43.05, 580), (43.2, 470), (43.3, 195), (43.4, 85), (43.5, 45), (43.6, 20), (43.7, 4)])


def _glyph(s, net, x, y, op, dx=lambda v: 0.0):
    """The network's sign, white, in its 80 px square at (x, y)."""
    cx, cy = x + 40, y + 40
    made = []

    def sh(name, layers, gx, gy, w, h, **kw):
        made.append(s.shp(f"Icono {net}{name}", layers, lambda v: (cx + gx + dx(v), cy + gy, w, h, 0, op(v)), **kw))

    def tx(content, ink, weight=900, family=M):
        made.append(s.txt(content, ink, family, weight, WHITE, f"Icono {net} (letra)", editable=False,
                          g=lambda v: (dx(v), 0, 1, 0, op(v))))
    if net == "behance":
        tx("Bē", (x + 8, y + 22, x + 72, y + 58))
    elif net == "google":
        sh("", solid(WHITE), 0, 0, 56, 40)
        sh(" (M)", [HOLLOW, stroke(BLACK, 6)], 0, 0, 52, 36, path="M 0 100 L 0 0 L 50 60 L 100 0 L 100 100")
    elif net == "patreon":
        sh(" (barra)", solid(BLACK), -26, 2, 10, 58)
        sh(" (círculo)", solid(WHITE), 8, -6, 44, 44, kind="ellipse")
    elif net == "telegram":
        sh("", solid(WHITE), -2, 2, 52, 44, path=poly([(0, 45), (100, 0), (80, 100), (48, 72), (36, 100), (30, 64)]))
    elif net == "dribbble":
        sh("", ring(WHITE, 5), 0, 0, 58, 58, kind="ellipse")
        sh(" (curva)", [HOLLOW, stroke(WHITE, 4)], 0, 0, 52, 52, path="M 15 10 C 45 40 70 70 75 100")
        sh(" (curva 2)", [HOLLOW, stroke(WHITE, 4)], 0, 0, 52, 52, path="M 0 45 C 35 50 75 35 95 15")
        sh(" (curva 3)", [HOLLOW, stroke(WHITE, 4)], 0, 0, 52, 52, path="M 15 90 C 30 60 70 50 100 62")
    elif net == "instagram":
        sh(" (marco)", [HOLLOW, stroke(WHITE, 6)], 0, 0, 54, 54, radius=15)
        sh(" (lente)", ring(WHITE, 6), 0, 0, 24, 24, kind="ellipse")
        sh(" (punto)", solid(WHITE), 14, -14, 7, 7, kind="ellipse")
    elif net == "soundcloud":
        for i in range(4):
            sh(f" (barra {i + 1})", solid(WHITE), -30 + 7 * i, 6 - 3 * i / 2, 4, 16 + 6 * i)
        sh(" (nube)", solid(WHITE), 12, 2, 42, 34,
           path="M 0 100 L 0 40 C 10 0 50 -5 62 30 C 80 20 100 40 100 66 C 100 86 90 100 75 100 Z")
    elif net == "twitter":
        sh("", solid(WHITE), 0, 2, 56, 46, path=BIRD)
    elif net == "facebook":
        tx("f", (x + 26, y + 16, x + 52, y + 76), 800)
    elif net == "itunes":
        sh("", ring(WHITE, 4), 0, 0, 56, 56, kind="ellipse")
        sh(" (nota)", solid(WHITE), 0, 2, 28, 30, path=path_of([(22, 10), (100, 0), (100, 75), (88, 75), (88, 22),
                                                                (34, 30), (34, 85), (22, 85)],
                                                               circle_pts(16, 85, 15, 14), circle_pts(82, 75, 15, 14)))
    elif net == "spotify":
        sh("", solid(WHITE), 0, 0, 58, 58, kind="ellipse")
        for i, (w, dy) in enumerate(((40, -9), (32, 2), (24, 12))):
            sh(f" (onda {i + 1})", [HOLLOW, stroke("#2EDB64", 5)], 0, dy, w, 10,
               path="M 0 100 C 30 0 70 0 100 100")
    elif net == "vimeo":
        tx("v", (x + 22, y + 26, x + 58, y + 62), 900)
    return made


def social_bars(nets, order, id_, es, en, tags, at_y=None):
    O, end = 38.05, 43.75
    t = _p(id_, es, en, order, O, end, 40.5, ["redes", "enlace", "barra"] + tags, section="redes")
    s = P(t, end - O, O)
    for net, colour, (x, y) in nets:
        if at_y is not None:
            x, y = 670, at_y
        cx = x + 290

        def hw(v):
            if v < 38.1 or v >= 43.72:
                return 0.0
            return (OPEN(v) if v < 43.0 else CLOSE(v)) / 2

        def window(v, cx=cx, y=y):
            h = hw(v)
            return (cx - h, y, cx + h, y + 80)
        iw = lambda v: 80 * min(1.0, 2 * hw(v) / 580) ** 0.7  # noqa: E731  the square, squeezed while it opens
        dx = lambda v, cx=cx, x=x: (cx - hw(v)) - x if hw(v) > 0 else 0.0  # noqa: E731
        dt = lambda v, dx=dx: dx(v) + iw(v) - 80  # noqa: E731
        pieces = [s.shp(f"Barra {net}", solid(WHITE), lambda v, x=x, y=y, dt=dt: (x + 330 + dt(v), y + 40, 500, 80, 0,
                                                                                   1.0 if hw(v) > 0 else 0.0)),
                  s.shp(f"Icono {net} (fondo)", solid(colour), lambda v, x=x, y=y, dx=dx: (
                      x + dx(v) + iw(v) / 2, y + 40, max(1.0, iw(v)), 80, 0, 1.0 if hw(v) > 0 else 0.0))]
        pieces += _glyph(s, net, x, y, lambda v: min(1.0, max(0.0, (2 * hw(v) - 450) / 120)),
                         lambda v, dx=dx: dx(v) + (iw(v) - 80) / 2)
        link = s.txt(f"{net}.com/yourname", (x + 120, y + 27, x + 560, y + 55), M, 600, "#1A1A1A", f"Enlace {net}",
                     g=lambda v, dt=dt: (dt(v), 0, 1, 0, min(1.0, max(0.0, (2 * hw(v) - 180) / 100))))
        link["textStyle"]["runs"] = [{"start": len(net) + 5, "end": len(net) + 13, "colorEnabled": True,
                                      "color": "#ff" + colour.lstrip("#").lower()}]
        pieces.append(link)
        for p in pieces:
            s.mask_to(p, window)
        s.shp(f"Sombra {net}", solid("#151515"), lambda v, cx=cx, y=y: (
            lambda h, q: (cx + h + 15 * q, y + 40, 30 * q, 80, 0, 1.0 if h > 0 and q > 0.02 else 0.0))(
            hw(v), 1 - hw(v) / 290))
    return t


def bars_grid():
    return social_bars(NETS, 17216, "redes-enlaces", "Doce barras de redes con enlace", "Twelve social link bars",
                       ["behance", "instagram", "facebook", "twitter"])


def _single(i):
    net, colour, pos = NETS[i]

    def make():
        return social_bars([NETS[i]], 17217 + i, f"enlace-{net}", f"Barra de enlace: {net}", f"Link bar: {net}",
                           [net], at_y=900)
    make.__name__ = f"bar_{net}"
    return make


# --- 18. Three doodle bursts and a glitch block that beat every second (44.05–48.0 s) -------------------------------
BURST_A = [("heart", "#FF1744", 418, 253, 50), ("star", "#19E6F0", 465, 235, 40), ("plus", WHITE, 523, 212, 25),
           ("bolt", "#F2E51A", 580, 233, 45), ("plus", WHITE, 510, 268, 45), ("heart", "#FF1744", 557, 297, 35),
           ("plus", WHITE, 435, 315, 30), ("star", "#19E6F0", 580, 345, 50), ("star", "#19E6F0", 422, 346, 30),
           ("bolt", "#F2E51A", 442, 388, 45), ("x", WHITE, 515, 375, 45)]
BURST_B = [("moon", "#22E35A", 1005, 173, 45), ("star", "#19E6F0", 1057, 152, 38), ("plus", "#2EC9F0", 1116, 127, 25),
           ("x", "#F0284A", 1103, 183, 45), ("tri", "#F5E11E", 1158, 170, 50), ("moon", "#22E35A", 1148, 215, 35),
           ("plus", "#F5E11E", 1027, 230, 30), ("star", "#19E6F0", 1012, 262, 25), ("tri", "#F5E11E", 1040, 282, 50),
           ("x", "#6A2CF0", 1107, 292, 45), ("star", "#19E6F0", 1173, 262, 50)]
BURST_C = [("heart", "#F01EE0", 1393, 563, 50), ("star", "#19E8A0", 1442, 543, 40), ("plus", "#28E0F0", 1500, 518, 25),
           ("bolt", "#F5B014", 1557, 543, 45), ("x", "#28E0F0", 1487, 575, 45), ("heart", "#F01EE0", 1535, 603, 35),
           ("plus", "#28E0F0", 1412, 622, 30), ("star", "#19E8A0", 1557, 653, 50), ("star", "#19E8A0", 1398, 655, 30),
           ("bolt", "#F5B014", 1420, 697, 45), ("x", "#28E0F0", 1490, 683, 45)]
CYCLES = (44.07, 45.07, 46.07, 47.07)


def _burst_piece(letter, items, centre, order):
    def make():
        O, end = 44.05, 48.0
        t = _p(f"destello-{letter}", f"Destello de garabatos {letter.upper()}", f"Doodle burst {letter.upper()}",
               order, O, end, 44.4, ["destello", "garabatos", "brillo"])
        s = P(t, end - O, O)
        s.burst(*centre, [(k_, c_, x_, y_, sz * 0.85) for k_, c_, x_, y_, sz in items], CYCLES, grow=0.22, life=0.62,
                r0=0.55)
        return t
    make.__name__ = f"burst_{letter}"
    return make


GLITCH = ["#FFF000", "#FF1050", WHITE, "#4F6EF0", "#3CF070", "#30F5F5", "#F020E0"]


def glitch_block():
    O, end = 44.05, 48.0
    t = _p("bloques-glitch", "Bloques de colores con falla digital", "Glitch colour blocks", 17232, O, end, 44.45,
           ["glitch", "colores", "falla"])
    s = P(t, end - O, O)
    box = (735, 535, 1110, 840)
    frames = {}
    for u in frames_of(s.dur):
        v = u + O
        p = (v - 44.1) % 1.0
        n = 0 if v < 44.1 else int(round(26 * math.sin(math.pi * min(1.0, p / 0.9)) ** 0.8))
        rng = random.Random(int(round(v * 30)))
        out = {c: [] for c in GLITCH}
        for _ in range(n):
            c = rng.choices(GLITCH, weights=(5, 3, 4, 2, 2, 2, 1))[0]
            h = rng.choice((5, 8, 14, 22, 34, 48)) if p < 0.6 else rng.choice((4, 6, 14, 26, 34))
            w = rng.uniform(40, 320) if h > 12 else rng.uniform(20, 300)
            x0 = rng.uniform(box[0], box[2] - 20)
            y0 = rng.uniform(box[1], box[3] - h)
            x1 = min(box[2], x0 + w)
            out[c].append([(x0, y0), (x1, y0), (x1, y0 + h), (x0, y0 + h)])
        frames[round(v, 4)] = out
    for c in GLITCH:
        clip = s.frames(f"Bloques {c}", solid(c), box, lambda v, c=c: frames.get(round(v, 4), {}).get(c, []))
        glow(s, clip, c, 8, 0.6)
    return t


TEMPLATES = [bolt, phone_reactions, button_window, trend_tape, like_burst, like_cursor, rising_hearts, sticker,
             channel_bar, channel_card, subscribe_button, profile, name_badge, phone_feed, live_red, live_white,
             bars_grid] + [_single(i) for i in range(len(NETS))] + [
    _burst_piece("a", BURST_A, (505, 305), 17229), _burst_piece("b", BURST_B, (1095, 215), 17230),
    _burst_piece("c", BURST_C, (1475, 615), 17231), glitch_block]
