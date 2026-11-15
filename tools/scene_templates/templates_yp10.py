"""Video 52531334.mp4 as Kit de YouTube Stock templates (yp10-*). See docs/plan-youtube-pack-2.md.

Hand-drawn / cartoon social media titles (36 s, 1920x1080 at 30 fps): organic blobs that pop and wobble, liquid
swooshes that wipe words in and out, splashes, a cursor that clicks and drags. Fifteen elements, each studied on
10 fps sheets (tienda/plantillas/estudio-52531334/NOTAS.md). Elements shown in a 2x2 grid are laid out from their
quarter at 1.6x round the frame centre; the two shown over footage keep a transparent background.

Liquid shapes (swooshes, splashes, drops, bursts) are drawn per frame: one outline per frame in `pathShapes` with the
`path` key held on each frame, in a box round what they cover (layoutRole "art", so a Short scales them with the
design). The pack's drop motif is a generic drop; where it stands for «your logo» it is the user's `logo-flip` slot.
Korean lines of the reference are Spanish words of the same layout.
"""

from __future__ import annotations

import math
import os
import random

import liquid as lq
import templates_llt_f as f6
from kit import wide
from scene import keys, tanim
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import fill, lin, poly, ring
from templates_yp7 import Y, step

WHITE = "#FFFFFF"
M, ANTON = "Montserrat", "Anton"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"
f6._FILES[(ANTON, 400)] = "fonts.basic/fonts/anton/Anton-Regular.ttf"

EMPTY = "M 0 0 L 0.01 0 L 0.01 0.01 Z"
CURSOR = poly([(0, 0), (0, 82), (21, 64), (34, 96), (49, 90), (36, 59), (64, 59)])


# ==== geometry (screen px) =========================================================================================

def chaikin(pts, it=3, closed=True):
    for _ in range(it):
        out = []
        n = len(pts)
        rng = range(n) if closed else range(n - 1)
        if not closed:
            out.append(pts[0])
        for i in rng:
            a, b = pts[i], pts[(i + 1) % n]
            out.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            out.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        if not closed:
            out.append(pts[-1])
        pts = out
    return pts


def xform(pts, cx, cy, sx, sy=None, rot=0.0, ox=50.0, oy=50.0):
    """Points of a 0..100 design → screen: scaled sx×sy px per 100, turned rot° about the design centre."""
    sy = sx if sy is None else sy
    a = math.radians(rot)
    c, s = math.cos(a), math.sin(a)
    out = []
    for x, y in pts:
        dx, dy = (x - ox) / 100 * sx, (y - oy) / 100 * sy
        out.append((cx + dx * c - dy * s, cy + dx * s + dy * c))
    return out


def ell(cx, cy, rx, ry, rot=0.0, n=28):
    return xform([(50 + 50 * math.cos(2 * math.pi * i / n), 50 + 50 * math.sin(2 * math.pi * i / n))
                  for i in range(n)], cx, cy, 2 * rx, 2 * ry, rot)


def blob(cx, cy, rx, ry, rot=0.0, amp=0.07, seed=1, ph=0.0, n=30):
    rnd = random.Random(seed)
    comp = [(m, rnd.uniform(0, 6.283), rnd.uniform(0.5, 1.0), rnd.uniform(-1, 1)) for m in (2, 3, 4)]
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = 1 + amp * sum(a * math.sin(m * t + p + ph * v * 3) for m, p, a, v in comp)
        pts.append((50 + 50 * r * math.cos(t), 50 + 50 * r * math.sin(t)))
    return xform(pts, cx, cy, 2 * rx, 2 * ry, rot)


def drop_pts(n=40):
    """A drop in a 0..100 box: round below, a point on top leaning right (the pack's motif)."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 0.86 * math.sin(t) * math.sin(t / 2) ** 0.55
        y = -math.cos(t)
        lean = 0.3 * max(0.0, -y) ** 2
        pts.append((50 + 50 * (x + lean), 50 + 50 * y))
    return pts


DROP = drop_pts()
DROP_PATH = poly(DROP)


def drop(cx, cy, h, rot=0.0):
    return xform(DROP, cx, cy, h, h, rot)


def notch(cx, cy, h, rot=0.0):
    """The bite inside the drop (a crescent near its left side), for an even-odd hole."""
    pts = arc_pts(50, 58, 26, 30, 110, 230, 10)
    return xform(ribbon(pts, 7, "lens"), cx, cy, h, h, rot)


def arc_pts(cx, cy, rx, ry, a0, a1, n=24, rot=0.0):
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        r = math.radians(rot)
        out.append((cx + x * math.cos(r) - y * math.sin(r), cy + x * math.sin(r) + y * math.cos(r)))
    return out


def sub(pts, t0, t1):
    """The part of a polyline between fractions t0 < t1 of its length."""
    t0, t1 = max(0.0, min(1.0, t0)), max(0.0, min(1.0, t1))
    if t1 - t0 < 1e-3:
        return []
    seg = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    total = sum(seg) or 1.0

    def at(t):
        d = t * total
        for (a, b), s in zip(zip(pts, pts[1:]), seg):
            if d <= s or s == seg[-1]:
                q = 0 if s == 0 else min(1.0, d / s)
                return a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q
            d -= s
        return pts[-1]
    n = max(4, int(24 * (t1 - t0)) + 2)
    return [at(t0 + (t1 - t0) * i / n) for i in range(n + 1)]


def ribbon(pts, w, profile="lens"):
    """A stroke with tapered ends round a polyline: half-width w × profile(t)."""
    if len(pts) < 2:
        return []
    shape = {"lens": lambda t: math.sin(math.pi * t) ** 0.8,
             "head": lambda t: math.sin(math.pi * min(1.0, t * 0.62 + 0.05)) ** 0.7,
             "tail": lambda t: math.sin(math.pi * max(0.0, t * 0.62 + 0.33)) ** 0.7,
             "flat": lambda t: 1.0}[profile]
    left, right = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / d, dx / d
        hw = w * shape(i / (n - 1))
        left.append((x + nx * hw, y + ny * hw))
        right.append((x - nx * hw, y - ny * hw))
    return left + right[::-1]


class _Native:
    """A liquid piece the 0.32 engine draws itself (see liquid.py); swoosh / burst / rays hand these to morph(),
    which makes one clip per distinct piece instead of an outline per frame."""

    def __init__(self, kind, **args):
        self.kind, self.args = kind, args
        self.key = (kind,) + tuple(sorted((k, tuple(map(tuple, v)) if k == "path" else v) for k, v in args.items()))

    def make(self, s, name, colour):
        a = self.args
        if self.kind == "brush":
            w = a["w"]
            return lq.brush(s, name, colour, a["path"], a["at"], a["n"], min(1.3 * w, 30 + 0.6 * w), lag=a["lag"],
                            profile=a["profile"], seed=int(a["at"]) % 97)
        if self.kind == "splash":
            # Fewer, bigger, uneven drops that fall a little, as the hand-drawn splashes (not a ring of dots).
            return lq.splash(s, name, colour, a["cx"], a["cy"], a["at"], a["n"], max(4, round(a["count"] * 0.55)),
                             a["r0"], a["r1"], a["size"] * 1.25, seed=a["seed"], spread=a["spread"], a0=a["a0"],
                             ry=a["ry"], gravity=0.2 * (a["r1"] - a["r0"]))
        return lq.rays(s, name, colour, a["cx"], a["cy"], a["at"], a["n"], a["count"], a["r0"], a["r1"] + a["length"],
                       1.6 * a["w"], a0=a["a0"], spread=a["spread"], profile="lens")


def swoosh(path, fr, at, n, w, lag=0.45, profile="lens"):
    """A liquid stroke running along path: its head goes 0→1 over n frames from at, its tail follows lag later."""
    return [_Native("brush", path=[(round(x, 1), round(y, 1)) for x, y in path], at=at, n=n, w=w, lag=lag,
                    profile=profile)]


def burst(cx, cy, fr, at, n, count, r0, r1, size, seed=3, spread=360.0, a0=0.0, ry=1.0):
    """Drops flying out from (cx, cy) and shrinking away."""
    return [_Native("splash", cx=cx, cy=cy, at=at, n=n, count=count, r0=r0, r1=r1, size=size, seed=seed,
                    spread=spread, a0=a0, ry=ry)]


def rays(cx, cy, fr, at, n, count, r0, r1, length, w, a0=0.0, spread=360.0):
    """Short tapered strokes shooting outwards (a click)."""
    return [_Native("rays", cx=cx, cy=cy, at=at, n=n, count=count, r0=r0, r1=r1, length=length, w=w, a0=a0,
                    spread=spread)]


def heart(cx, cy, s, rot=0.0):
    pts = []
    for i in range(32):
        t = 2 * math.pi * i / 32
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((50 + x * 3, 50 + y * 3))
    return xform(pts, cx, cy, s, s, rot)


def star(cx, cy, r, rot=0.0):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        a = math.radians(rot - 90 + 36 * i)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return chaikin(pts, 1)


def arrow_pts(cx, cy, s, rot=0.0):
    """A chunky arrow pointing up (rot turns it)."""
    pts = [(50, 0), (100, 48), (68, 48), (68, 100), (32, 100), (32, 48), (0, 48)]
    return xform(chaikin(pts, 1), cx, cy, s * 0.8, s, rot)


# ==== the per-frame shape and helpers on the slide ================================================================

def _svg(polys, box):
    x0, y0, w, h = box
    out = []
    for pts in polys:
        if len(pts) > 2:
            out.append("M " + " L ".join(f"{(x - x0) / w * 100:.2f} {(y - y0) / h * 100:.2f}" for x, y in pts) + " Z")
    return " ".join(out)


def morph(s, name, colour, fn, evenodd=False, alpha=1.0):
    """Outlines that change shape: fn(fr) → polygons (screen px), keyed every other frame and blended with the
    0.32 smooth morph (liquid.morph_keys). Strokes, splashes and rays in the list become native pieces
    (_Native: tapered strokes with Trim keys, drops), one clip each. Returns the outline clip (None without one)."""
    natives = {}

    def polys(fr):
        out = []
        for p in fn(fr):
            if isinstance(p, _Native):
                natives.setdefault(p.key, p)
            elif len(p) > 2 and max(x for x, _ in p) - min(x for x, _ in p) > 1.5 \
                    and max(y for _, y in p) - min(y for _, y in p) > 1.5:
                out.append(p)
        return out
    for _, fr in s.each():
        polys(fr)  # every frame once, so no piece is missed between keys
    clip = lq.morph_keys(s, name, colour, polys, evenodd=evenodd, alpha=alpha)
    for i, piece in enumerate(natives.values()):
        piece.make(s, name if clip is None and i == 0 else f"{name} {i + 1}", colour)
    return clip


def word(s, text, cx, cy, cap, colour=WHITE, family=M, weight=800, name="Título", align="center", geom=None,
         layers=None, op=None, rot=None, editable=True):
    """A line whose capitals are `cap` px tall, centred on cx (align left: starts at cx; right: ends at cx)."""
    if align == "center":
        ink = (cx - 2400, cy - cap / 2, cx + 2400, cy + cap / 2)
    elif align == "left":
        ink = (cx, cy - cap / 2, cx + 4800, cy + cap / 2)
    else:
        ink = (cx - 4800, cy - cap / 2, cx, cy + cap / 2)
    return s.say(text, ink, family, weight, colour, name, geom=geom, align=align, layers=layers, op=op, rot=rot,
                 editable=editable)


def letters(s, clip, inn=None, out=None):
    """Per-letter entrance inn = (preset, frame, stagger s, duration s[, order]) and exit out = (preset, last frame,
    stagger, duration[, order]): the exit ends on that frame."""
    anim = {}
    if inn:
        p, at, st, du = inn[:4]
        anim["in"] = tanim(p, duration=du, unit="character", stagger=st, ease="easeOut", delay=round(at / FPS, 3),
                           order=inn[4] if len(inn) > 4 else "forward")
    if out:
        p, end, st, du = out[:4]
        anim["out"] = tanim(p, duration=du, unit="character", stagger=st, ease="easeIn",
                            delay=round(max(0.0, s.dur - end / FPS), 3), order=out[4] if len(out) > 4 else "forward")
    clip["textStyle"]["animation"] = anim
    return clip


def cursor(s, path):
    """The pointer of the reference: path(fr) → (x, y, opacity, pressed)."""
    def g(fr, u):
        x, y, op, press = path(fr)
        sc = 1 - 0.18 * press
        return x + 17 * sc, y + 24 * sc, 34 * sc, 48 * sc, 0, op
    c = s.obj("Cursor", [fill(WHITE), ring("#111111", 3)[1]], g, path=CURSOR, base=(34, 48))
    c["layoutRole"] = "art"
    return c


def press(fr, at, n=4):
    """1 while a click is held (a quick dip)."""
    return math.sin(math.pi * lin(fr, at, n)) if at <= fr <= at + n else 0.0


def pop(fr, at, n, over=0.14):
    return step(fr, [(at, 0.0), (at + n * 0.6, 1 + over), (at + n, 1.0)])


def wob(fr, period=24, amp=0.03, ph=0.0):
    return 1 + amp * math.sin(2 * math.pi * fr / period + ph)


def _p(id, es, en, order, dur, section, tags=(), thumb=None):
    return wide(f"yp10-{id}", es, en, "ytkit", round(dur, 2), order=order,
                tags=[f"kit:{section}", "youtube", "a mano", "dibujo", "redes"] + list(tags),
                thumb_at=round(thumb if thumb is not None else dur * 0.6, 2))


# The templates follow (one function per element of the reference).


def spacing(s, clip, fn):
    """Letter spacing (px) per frame."""
    Y.spacing(s, clip, fn)


def arched(s, clip, cx, cy, bend, rot=0.0):
    """Sets a text on a gentle arc through (cx, cy): bend > 0 bulges up (a frown), < 0 down (a smile)."""
    st = clip["textStyle"]
    f = f6._font(st["fontFamily"], st.get("fontWeight", 700))
    natural = f.getlength(clip["textContent"]) * st["pixelSize"] / f.size
    w, h = natural * 1.25, st["pixelSize"] * 3
    st["wordWrap"] = False
    y0 = 50 + 100 * bend / h * 0.75
    y1 = 50 - 100 * bend / h * 0.75
    st["pathSvg"] = f"M 0 {y0:.2f} C 30 {y1:.2f} 70 {y1:.2f} 100 {y0:.2f}"
    for key, v in (("x", cx - w / 2), ("y", cy - h / 2 + st["pixelSize"] * 0.35), ("width", w), ("height", h)):
        clip[key] = keys([(0.0, v, "hold")])
    if rot:
        clip["rotation"] = keys([(0.0, rot, "hold")])
    return clip


# ==== 1. LIKE NEW VIDEO (yellow): a red disc is clicked into a thumb; the words open; a white splash wipes it away ==

def like_yellow():
    D = 4.9
    t = _p("me-gusta-amarillo", "Like New Video con pulgar amarillo", "Like New Video with a yellow thumb", 17400, D,
           "redes", ["me gusta", "pulgar"], thumb=2.4)
    s = Y(t, D)
    R = lambda f: f - 444  # noqa: E731  (reference frame → frame here)
    yellow, red = "#FAF168", "#E5485A"
    dcx, dcy = 1032, 490

    def disc(fr, u):
        sc = 432 * pop(fr, R(447), 9) * (1 - k(fr, R(471), 4))
        sq = R(470) <= fr < R(474)
        return dcx, dcy, sc * (1.05 if sq else 1), sc * (0.85 if sq else 1) * wob(fr, 14, 0.02), 0, 1
    s.obj("Disco", solid(red), disc, kind="ellipse", base=(432, 432))
    s.obj("Disco (borde)", ring(yellow, 14), lambda fr, u: (dcx, dcy, 440 * (1 - k(fr, R(471), 4)),
                                                            440 * (1 - k(fr, R(471), 4)), 0, k(fr, R(465), 3)),
          kind="ellipse", base=(440, 440))
    hand = poly(chaikin([(5, 48), (28, 44), (36, 20), (42, 3), (55, 0), (62, 10), (58, 32), (56, 42), (92, 44),
                         (100, 54), (94, 62), (100, 72), (93, 80), (97, 90), (86, 100), (5, 100)], 2))
    grow = lambda fr: pop(fr, R(471), 9, 0.1)  # noqa: E731
    gone = lambda fr: 1 - k(fr, R(549), 6)  # noqa: E731
    turn = lambda fr: -25 * (1 - k(fr, R(471), 9)) + 30 * k(fr, R(549), 6)  # noqa: E731
    for name, colour, op in (("Pulgar (paso)", yellow, lambda fr: 1.0 if fr < R(489) else 0.0),
                             ("Pulgar", WHITE, lambda fr: 1.0 if fr >= R(489) else 0.0)):
        s.obj(name, solid(colour), lambda fr, u, op=op: (1244, 432, 317 * grow(fr) * gone(fr),
                                                         528 * grow(fr) * gone(fr), turn(fr), op(fr)),
              path=hand, base=(317, 528))
        s.obj(name.replace("Pulgar", "Puño"), solid(colour),
              lambda fr, u, op=op: (1036, 492 + 204 * (1 - k(fr, R(474), 6)), 77 * gone(fr),
                                    max(1.0, 408 * k(fr, R(474), 6) * gone(fr)), 0, op(fr) * k(fr, R(474), 2)),
              radius=38, base=(77, 408))
    lines = (("Like", 377, R(474)), ("New", 607, R(477)), ("Video", 840, R(480)))
    for i, (txt, cy, at) in enumerate(lines):
        out = R(549) + 3 * i
        for name, colour, op in ((f"Título {i + 1} (paso)", WHITE, lambda fr: 1.0 if fr < R(489) else 0.0),
                                 (f"Título {i + 1}" if i else "Título", yellow,
                                  lambda fr: 1.0 if fr >= R(489) else 0.0)):
            c = word(s, txt, 528, cy, 150, colour, M, 800, name, align="left", editable=colour == yellow,
                     geom=lambda fr, u, at=at, out=out, op=op: (0, 0, 1, 0, op(fr) * k(fr, at, 3) * (1 - k(fr, out, 5))))
            spacing(s, c, lambda fr, at=at, out=out: 60 * (1 - k(fr, at, 7)) + 70 * k(fr, out, 5))
    morph(s, "Destellos", WHITE, lambda fr: rays(1244, 432, fr, R(489), 8, 7, 300, 380, 90, 12, a0=-150, spread=300))
    morph(s, "Salpicadura", WHITE, lambda fr: (
        swoosh(arc_pts(900, 520, 430, 300, 175, 340, 30), fr, R(543), 12, 80)
        + swoosh(arc_pts(1250, 430, 250, 280, 215, 400, 24), fr, R(549), 10, 90)
        + burst(980, 650, fr, R(555), 18, 16, 60, 420, 22, seed=5)))
    cursor(s, lambda fr: (step(fr, [(R(456), 1260), (R(462), 1060), (R(476), 1060), (R(484), 440)]),
                          step(fr, [(R(456), 300), (R(462), 500), (R(476), 500), (R(484), 360)]),
                          k(fr, R(453), 4) * (1 - k(fr, R(543), 4)), press(fr, R(464))))
    return t


# ==== 2. SOCIAL MEDIA TITLE: a red oval pops among white swirls; the words arch round it, then straighten =========

def social_title():
    D = 5.0
    t = _p("social-media", "Social Media Title con óvalo rojo", "Social Media Title round a red oval", 17401, D,
           "tipografia", ["título", "óvalo"], thumb=1.6)
    s = Y(t, D)
    R = lambda f: f - 171  # noqa: E731
    red = "#C3290A"

    def oval(fr, u):
        sc = pop(fr, R(175), 9, 0.08) * (1 - k(fr, R(228), 8))
        return (958, 543 + 40 * k(fr, R(228), 8), 630 * sc * (1 - 0.3 * k(fr, R(228), 8)),
                330 * sc * wob(fr, 20, 0.025), 0, 1)
    s.obj("Óvalo", solid(red), oval, kind="ellipse", base=(630, 330))
    morph(s, "Remolinos", WHITE, lambda fr: (
        swoosh(arc_pts(958, 543, 380, 230, 110, 260, 30), fr, R(174), 10, 26)
        + swoosh(arc_pts(958, 560, 320, 170, 20, 160, 24), fr, R(177), 9, 22)
        + swoosh(arc_pts(958, 543, 170, 120, 180, 560, 40), fr, R(181), 14, 34)
        + rays(900, 400, fr, R(192), 9, 6, 40, 160, 120, 16, a0=-160, spread=140)))
    for i, (x, y) in enumerate(((732, 210), (960, 168), (1212, 228))):
        def person(fr, x=x, y=y, i=i):
            sc = pop(fr, R(176) + 2 * i, 6) * (1 - k(fr, R(192) + i, 4))
            if sc <= 0.01:
                return []
            return [ell(x, y - 18 * sc, 13 * sc, 13 * sc, n=14),
                    [(x - 24 * sc, y + 22 * sc)] + arc_pts(x, y + 22 * sc, 24 * sc, 26 * sc, 180, 360, 10)]
        morph(s, f"Persona {i + 1}", WHITE, person)
    c = word(s, "SOCIAL", 958, 305, 105, WHITE, M, 800, "Título",
             geom=lambda fr, u: (0, 0, 1, 0, 1 - k(fr, R(231), 4)))
    arched(s, c, 958, 305, 34, 2)
    letters(s, c, ("pop", R(194), 0.035, 0.18, "random"))
    c = word(s, "MEDIA TITLE", 958, 785, 112, WHITE, M, 800, "Título 2",
             geom=lambda fr, u: (0, 0, 1, 0, 1 - k(fr, R(231), 4)))
    arched(s, c, 958, 785, -30, -4)
    spacing(s, c, lambda fr: 50 * (1 - k(fr, R(203), 7)))
    letters(s, c, ("fade", R(203), 0.04, 0.1))
    morph(s, "Gotas", red, lambda fr: (
        [ell(958 + dx, 600 + 40 * k(fr, R(230), 6) + 160 * k(fr, R(232) + j, 8), 12 * (1 - lin(fr, R(236) + j, 6)),
             18 * (1 - lin(fr, R(236) + j, 6)), n=12) for j, dx in enumerate((-60, 10, 70))
         if R(230) <= fr <= R(242) + j]
        + swoosh(arc_pts(958, 560, 330, 100, 160, 400, 30), fr, R(234), 12, 10)))
    for name, txt, cy in (("Texto", "SOCIAL", 470), ("Texto 2", "MEDIA TITLE", 605)):
        out = R(288) if name == "Texto" else R(295)
        c = word(s, txt, 958, cy, 95, WHITE, M, 800, name,
                 geom=lambda fr, u, out=out, first=name == "Texto": (0, 30 * k(fr, out, 6) if first else 0,
                                                                     1.08 - 0.08 * k(fr, R(234), 9), 0,
                                                                     k(fr, R(232), 4) * (1 - k(fr, out, 6))))
        spacing(s, c, lambda fr, out=out: 40 * k(fr, out, 8))
    swirl = [(958 + (40 + 240 * (1 - i / 50)) * math.cos(math.radians(250 - 9 * i)),
              640 + (40 + 240 * (1 - i / 50)) * 0.8 * math.sin(math.radians(250 - 9 * i))) for i in range(51)]
    morph(s, "Remolino de salida", WHITE, lambda fr: swoosh(swirl, fr, R(291), 22, 60, lag=0.55)
          + burst(958, 640, fr, R(306), 10, 8, 40, 180, 12, seed=9))
    return t




def drop_with_notch(s, name, colour, geom, hole=True):
    """The pack's drop (white on a button) with its bite; geom(fr) → (cx, cy, h, rot, opacity)."""
    path = lq.smooth_path([(DROP, True)], (0, 0, 100, 100))
    if hole:
        path += " " + poly(ribbon(arc_pts(50, 58, 26, 30, 110, 230, 10), 7, "lens"))

    def g(fr, u):
        cx, cy, h, rot, op = geom(fr)
        return cx, cy, max(0.01, h), max(0.01, h), rot, op if h >= 2 else 0.0
    clip = s.obj(name, solid(colour), g, path=path, base=(100, 100))
    clip["shapeStyle"]["customEvenOdd"] = hole
    clip["layoutRole"] = "art"
    return clip


def arrow(s, name, colour, edge, geom):
    """A chunky arrow with a coloured edge offset behind; geom(fr) → (cx, cy, size, rot, scale)."""
    path = poly(chaikin([(50, 0), (100, 48), (68, 48), (68, 100), (32, 100), (32, 48), (0, 48)], 1))

    def g(off):
        def f(fr, u):
            cx, cy, sz, rot, sc = geom(fr)
            sc = max(0.0, sc)
            return cx + off, cy + off, max(0.01, sz * sc * 0.8), max(0.01, sz * sc), rot, 1.0 if sc > 0.01 else 0.0
        return f
    for nm, col, off in ((f"{name} (borde)", edge, 7), (name, colour, 0)):
        c = s.obj(nm, solid(col), g(off), path=path, base=(80, 100))
        c["layoutRole"] = "art"


# ==== 3. @YOURACCOUNT: a blue drop, a white smear writes «Social», which turns into the account name ============

def account():
    D = 3.8
    t = _p("cuenta", "@youraccount con gota azul", "@youraccount with a blue drop", 17402, D, "redes",
           ["cuenta", "gota"], thumb=2.2)
    s = Y(t, D)
    R = lambda f: f - 444  # noqa: E731
    blue = "#12B1F3"

    def dg(fr):
        sc = pop(fr, R(447), 8) * (1 - k(fr, R(540), 6))
        return 586, 516, 269 * sc, -10 * (1 - k(fr, R(447), 8)), 1
    morph(s, "Gota", blue, lambda fr: [drop(*dg(fr)[:4])] if dg(fr)[2] > 2 else [])
    soc = word(s, "Social", 778, 540, 160, blue, M, 700, "Texto (paso)", align="left", editable=False)
    letters(s, soc, ("fade", R(451), 0.035, 0.06))
    s.d3(soc, ry=lambda fr, u: 88 * k(fr, R(472), 6), persp=1600)
    soc["opacity"] = keys([(u, 1.0 if fr < R(478) else 0.0, "hold") for u, fr in s.each()])
    acc = word(s, "@youraccount", 840, 540, 62, WHITE, M, 700, "Título", align="left")
    s.d3(acc, ry=lambda fr, u: 88 * (1 - k(fr, R(478), 8)), persp=1600)
    acc["opacity"] = keys([(u, 1.0 if fr >= R(478) else 0.0, "hold") for u, fr in s.each()])
    letters(s, acc, None, ("fade", R(552), 0.03, 0.08))
    morph(s, "Gotas azules", blue, lambda fr: burst(1150, 540, fr, R(479), 16, 12, 40, 380, 16, seed=4, ry=0.5))
    smear = chaikin([(560, 600), (800, 560), (1100, 545), (1420, 560)], 2, closed=False)
    morph(s, "Trazo", WHITE, lambda fr: (
        swoosh(smear, fr, R(450), 12, 46, lag=0.5, profile="head")
        + burst(1330, 540, fr, R(456), 10, 10, 30, 200, 12, seed=2)
        + swoosh(arc_pts(586, 516, 200, 180, 150, 420, 30), fr, R(534), 9, 26)
        + swoosh(arc_pts(586, 520, 270, 130, 200, 470, 30), fr, R(537), 9, 20)
        + swoosh(arc_pts(1170, 560, 400, 90, 170, 10, 24), fr, R(541), 10, 20)))
    return t


# ==== 4. SUBSCRIBE: four dots, a scribble becomes a magenta button; a dot dragged in turns it red ===============

def subscribe_dots():
    D = 4.4
    t = _p("suscribete-puntos", "Subscribe con puntos de color y @yourchannel",
           "Subscribe with colour dots and @yourchannel", 17403, D, "redes", ["suscribirse", "botón"], thumb=2.5)
    s = Y(t, D)
    R = lambda f: f - 444  # noqa: E731
    mag, pink = "#C820D5", "#E9495B"
    x0, x1, y0, y1 = 618, 1296, 452, 604
    shut = lambda fr: k(fr, R(551), 10)  # noqa: E731
    morph(s, "Garabato", mag, lambda fr: swoosh(chaikin([(700, 470), (1250, 500), (760, 560), (1220, 590)], 2,
                                                        closed=False), fr, R(450), 7, 18, lag=1.2, profile="flat")
          if fr < R(458) else [])
    s.rect("Botón", solid(mag), lambda fr, u: (x0 + (x1 - x0) * shut(fr), y0, x1, y1),
           op=lambda fr, u: k(fr, R(456), 2))
    s.rect("Botón (rojo)", solid(pink), lambda fr, u: (max(x0 + (x1 - x0) * shut(fr),
                                                         x1 - (x1 - x0) * k(fr, R(495), 6)), y0, x1, y1))
    drop_with_notch(s, "Gota", WHITE, lambda fr: (676, 528, 108, 0, k(fr, R(457), 2) * (1 - shut(fr))), hole=False)
    c = word(s, "Subscribe", 736, 528, 74, WHITE, M, 700, "Título", align="left",
             geom=lambda fr, u: (0, 0, 1, 0, k(fr, R(457), 2)))
    letters(s, c, None, ("fade", R(562), 0.03, 0.06))
    c = word(s, "@yourchannel", 962, 405, 58, WHITE, M, 700, "Texto",
             geom=lambda fr, u: (0, 0, 1, 0, k(fr, R(500), 3) * (1 - k(fr, R(561), 4))))
    spacing(s, c, lambda fr: 30 * (1 - k(fr, R(500), 5)) + 30 * k(fr, R(561), 4))
    drag = lambda fr: (step(fr, [(R(468), 715), (R(492), 1250)]), step(fr, [(R(468), 420), (R(480), 470),  # noqa: E731
                                                                          (R(492), 528)]))
    for i, (x, colour) in enumerate(((638, "#5B7BFF"), (715, "#F2464E"), (792, "#47D86A"), (869, "#F2C24C"))):
        def dot(fr, x=x, i=i):
            sc = pop(fr, R(450) + 2 * i, 5)
            if i == 1:
                if fr >= R(492):
                    sc *= 1 - k(fr, R(492), 3)
                cx, cy = drag(fr) if fr >= R(468) else (x, 420)
            else:
                sc *= 1 - k(fr, R(486) + 2 * i, 6)
                cx, cy = x, 420
            return [ell(cx, cy, 17 * sc, 17 * sc, n=16)] if sc > 0.02 else []
        morph(s, f"Punto {i + 1}", colour, dot)
    morph(s, "Salpicadura", pink, lambda fr: (
        rays(1300, 528, fr, R(497), 8, 8, 40, 120, 50, 9, a0=-90, spread=180)
        + burst(957, 528, fr, R(503), 14, 26, 300, 520, 9, seed=6, ry=0.35)
        + swoosh(chaikin([(1300, 600), (1200, 640), (1100, 600), (1000, 650)], 2, closed=False), fr, R(562), 6, 7)))
    morph(s, "Remolino", WHITE, lambda fr: swoosh(chaikin([(560, 640), (800, 690), (1100, 600), (1360, 520)], 2,
                                                          closed=False), fr, R(548), 13, 60, lag=0.4)
          + burst(1300, 560, fr, R(560), 9, 8, 20, 140, 10, seed=8))
    cursor(s, lambda fr: (*(drag(fr) if fr >= R(466) else (step(fr, [(R(456), 1200), (R(466), 715)]),
                                                           step(fr, [(R(456), 560), (R(466), 420)]))),
                          k(fr, R(455), 3) * (1 - k(fr, R(560), 4)), press(fr, R(465), 3)))
    return t


# ==== 5. NEW VIDEO: a purple box opens, the words close up, a «Like» tab drops below; crescents wipe it =========

def new_video_purple():
    D = 4.6
    t = _p("nuevo-video-morado", "NEW VIDEO en caja morada con Like", "NEW VIDEO in a purple box with Like", 17404,
           D, "tipografia", ["nuevo video", "caja"], thumb=2.4)
    s = Y(t, D)
    R = lambda f: f - 444  # noqa: E731
    purple, lav = "#35207B", "#94C1FB"
    s.obj("Pestaña", solid(purple), lambda fr, u: (1351, 556 + 78 * (k(fr, R(480), 6) - k(fr, R(549), 6)), 270,
                                                   max(1.0, 157 * (k(fr, R(480), 6) - k(fr, R(549), 6))), 0, 1),
          radius=16, base=(270, 157))

    def box(fr, u):
        w = 1054 * (0.3 + 0.7 * k(fr, R(447), 9))
        if fr >= R(566):
            w = 1054 - (1054 - 150) * k(fr, R(566), 6) - 110 * k(fr, R(572), 6)
        h = 165 * (1 - k(fr, R(574), 6))
        return 959, 481, w, max(1.0, h), 0, k(fr, R(447), 2) * (1 - k(fr, R(578), 3))
    s.obj("Caja", solid(purple), box, radius=16, base=(1054, 165))
    squish = lambda fr: 1 - 0.06 * math.sin(math.pi * lin(fr, R(474), 8))  # noqa: E731
    c = word(s, "NEW", 464, 479, 104, lav, M, 800, "Título", align="left",
             geom=lambda fr, u: (0, 0, squish(fr), 0, k(fr, R(459), 2) * (1 - k(fr, R(562), 4))))
    spacing(s, c, lambda fr: 50 * (1 - k(fr, R(459), 4)) + 40 * k(fr, R(559), 5))
    c = word(s, "VIDEO", 1456, 479, 104, lav, M, 800, "Título 2", align="right",
             geom=lambda fr, u: (0, 0, squish(fr), 0, k(fr, R(465), 2) * (1 - k(fr, R(568), 4))))
    spacing(s, c, lambda fr: 40 * (1 - k(fr, R(465), 4)) + 40 * k(fr, R(564), 5))
    c = word(s, "Like", 1347, 624, 78, WHITE, M, 800, "Texto",
             geom=lambda fr, u: (0, 0, 1, 0, 1 if fr >= R(483) else 0))
    letters(s, c, ("fade", R(483), 0.08, 0.15, "random"), ("fade", R(549), 0.06, 0.12, "random"))
    morph(s, "Destellos", lav, lambda fr: (
        rays(959, 481, fr, R(474), 10, 6, 560, 640, 60, 5, a0=-20, spread=40)
        + rays(959, 481, fr, R(474), 10, 6, 560, 640, 60, 5, a0=160, spread=40)
        + burst(959, 481, fr, R(477), 12, 22, 540, 700, 7, seed=3, ry=0.3)))
    morph(s, "Lunas", WHITE, lambda fr: (
        swoosh(arc_pts(700, 520, 130, 150, 220, 400, 24), fr, R(556), 9, 40)
        + swoosh(arc_pts(1120, 500, 150, 160, 200, 380, 24), fr, R(561), 9, 40)
        + swoosh(arc_pts(959, 480, 190, 170, 0, 300, 30), fr, R(568), 10, 40)
        + burst(959, 480, fr, R(576), 8, 8, 60, 200, 10, seed=11)))
    cursor(s, lambda fr: (step(fr, [(R(456), 1500), (R(468), 1180), (R(474), 1180), (R(500), 790)]),
                          step(fr, [(R(456), 640), (R(468), 520), (R(474), 520), (R(500), 680)]),
                          k(fr, R(453), 3) * (1 - k(fr, R(552), 3)), press(fr, R(473), 3)))
    return t


# ==== 6. MY CHANNEL: «Subscribe» flares into «My Channel»; it is selected and grows inside glowing rings ========

def my_channel():
    D = 4.6
    t = _p("mi-canal", "My Channel que se selecciona y crece", "My Channel selected and growing", 17405, D,
           "tipografia", ["canal", "selección"], thumb=3.0)
    s = Y(t, D)
    R = lambda f: f - 582  # noqa: E731
    red = "#ED2A42"
    sc = lambda fr: 0.71 + 0.29 * k(fr, R(655), 7)  # noqa: E731
    left, right = 542, 1377
    hl = s.rect("Selección", solid("#0B1C54"), lambda fr, u: (left - 10, 470, left + (right - left + 20) *
                                                             k(fr, R(630), 21), 588),
                op=lambda fr, u: 1.0 if R(630) <= fr < R(653) else 0.0)
    c = word(s, "Subscribe", 960, 528, 92, red, M, 700, "Texto (paso)", editable=False,
             geom=lambda fr, u: (0, 0, pop(fr, R(586), 5, 0.1), 0, 1.0 if fr < R(608) else 0.0))
    del c
    main = word(s, "My Channel", 960, 528, 130, red, M, 700, "Título",
                geom=lambda fr, u: (0, 0, sc(fr), 0, 1.0 if fr >= R(608) else 0.0))
    letters(s, main, None, ("fade", R(714), 0.06, 0.08))
    lit = word(s, "My Channel", 960, 528, 130, "#7A3FA0", M, 700, "Título (selección)", editable=False,
               geom=lambda fr, u: (0, 0, sc(fr), 0, 1.0 if R(630) <= fr < R(653) else 0.0))
    s.clipped(lit, lambda fr: (left - 10, 460, left + 10 + (right - left + 20) * k(fr, R(630), 21), 600))
    del hl
    morph(s, "Llamas", red, lambda fr: rays(960, 500, fr, R(607), 8, 7, 30, 170, 110, 16, a0=-160, spread=140))
    morph(s, "Marcas", WHITE, lambda fr: (
        swoosh(arc_pts(960, 528, 340, 70, 20, 160, 20), fr, R(596), 8, 12)
        + swoosh(arc_pts(960, 528, 340, 70, 200, 340, 20), fr, R(598), 8, 12)
        + rays(980, 528, fr, R(603), 6, 6, 8, 50, 70, 10, a0=30)
        + burst(960, 560, fr, R(607), 9, 10, 40, 260, 12, seed=7)))
    morph(s, "Aros", "#FFD9B0", lambda fr: (
        swoosh(arc_pts(960, 528, 700, 110, 160, 520, 40), fr, R(651), 14, 9)
        + swoosh(arc_pts(960, 540, 640, 90, 340, 700, 40), fr, R(654), 12, 7)))

    def s_curve(fr):
        if not R(689) <= fr <= R(720):
            return []
        x = 400 + 1300 * lin(fr, R(689), 28)
        pts = [(x - 40 * math.sin(math.pi * i / 12) + 60 * (i / 12 - 0.5), 420 + 230 * i / 12) for i in range(13)]
        return [ribbon(pts, 26 * (1 - k(fr, R(712), 8)) + 2, "lens")]
    morph(s, "Barrido", WHITE, s_curve)
    cursor(s, lambda fr: (step(fr, [(R(615), 700), (R(627), 540), (R(630), 540), (R(651), 1390)]),
                          step(fr, [(R(615), 640), (R(627), 545), (R(651), 560)]),
                          k(fr, R(614), 3) * (1 - k(fr, R(656), 3)), press(fr, R(628), 3)))
    return t


# ==== 7. SUBSCRIBE MY CHANNEL: a red scribble becomes a button with a drop; a white tab opens; arrows point =====

def subscribe_sticker():
    D = 5.5
    t = _p("boton-suscribete", "Botón SUBSCRIBE MY CHANNEL con flechas", "SUBSCRIBE MY CHANNEL button with arrows",
           17406, D, "redes", ["suscribirse", "botón", "flechas"], thumb=2.8)
    s = Y(t, D)
    R = lambda f: f - 582  # noqa: E731
    red = "#D22E41"
    bx = lambda fr: step(fr, [(R(626), 970), (R(636), 564), (R(717), 564), (R(726), 970)])  # noqa: E731
    morph(s, "Trazo rojo", red, lambda fr: (
        swoosh(chaikin([(880, 470), (960, 500), (1060, 530)], 2, closed=False), fr, R(586), 6, 18, lag=1)
        + swoosh(chaikin([(860, 480), (900, 600), (960, 520), (1020, 600), (1080, 480)], 2, closed=False), fr,
                 R(590), 6, 26, lag=1)) if fr < R(596) else [])
    pill = lambda fr: k(fr, R(626), 6) * (1 - k(fr, R(713), 8))  # noqa: E731
    s.rect("Pestaña", solid(WHITE), lambda fr, u: (bx(fr) + 100, 406, bx(fr) + 100 + 848 * pill(fr), 650),
           op=lambda fr, u: 1.0 if pill(fr) > 0.01 else 0.0, radius=34)

    def box(fr, u):
        g = pop(fr, R(594), 6, 0.12) * (1 - k(fr, R(735), 10))
        click = 1 - 0.15 * math.sin(math.pi * lin(fr, R(611), 7))
        w = 408 * g * click * wob(fr, 9, 0.04 * (1 - k(fr, R(604), 6)))
        return bx(fr), 530, w, 288 * g * click, 4 * math.sin(fr / 3) * (1 - k(fr, R(604), 6)) - 25 * k(fr, R(735), 10), 1
    s.obj("Botón", solid(red), box, radius=60, base=(408, 288))
    drop_with_notch(s, "Gota", WHITE, lambda fr: (bx(fr) - 2, 530, 190 * pop(fr, R(604), 5) * (1 - k(fr, R(734), 9))
                                                  * (1 - 0.15 * math.sin(math.pi * lin(fr, R(611), 7))), -8, 1),
                    hole=False)
    for name, txt, cy, at, end in (("Título", "SUBSCRIBE", 487, R(629), R(707)),
                                   ("Título 2", "MY CHANNEL", 597, R(631), R(713))):
        c = word(s, txt, 1110, cy, 68, red, M, 800, name,
                 geom=lambda fr, u, at=at: (0, 0, 1, 0, 1 if fr >= at else 0))
        letters(s, c, ("fade", at, 0.03, 0.06), ("fade", end, 0.03, 0.06))
        spacing(s, c, lambda fr, end=end: 30 * k(fr, end - 9, 9))
    bob = lambda fr, ph=0.0: math.sin(2 * math.pi * fr / 20 + ph)  # noqa: E731
    out = lambda fr: 1 - k(fr, R(735), 6)  # noqa: E731
    arrow(s, "Flecha 1", WHITE, "#F0A878", lambda fr: (758 + 14 * bob(fr), 242 + 14 * bob(fr), 250, 135,
                                                       pop(fr, R(630), 6) * out(fr)))
    arrow(s, "Flecha 2", WHITE, "#F0A878", lambda fr: (1310 - 14 * bob(fr, 2), 252 + 14 * bob(fr, 2), 250, -135,
                                                       pop(fr, R(627), 6) * out(fr)))
    arrow(s, "Flecha 3", WHITE, "#F0A878", lambda fr: (1018, 818 - 16 * bob(fr, 4), 250, 0,
                                                       pop(fr, R(630), 6) * out(fr)))
    morph(s, "Salpicadura", WHITE, lambda fr: (
        swoosh(chaikin([(700, 560), (850, 500), (960, 530)], 2, closed=False), fr, R(600), 6, 40, lag=0.8,
               profile="head")
        + rays(970, 530, fr, R(611), 9, 10, 230, 330, 60, 10)
        + swoosh(chaikin([(760, 580), (970, 520), (1200, 540)], 2, closed=False), fr, R(620), 6, 22)
        + swoosh(arc_pts(970, 530, 300, 260, 0, 300, 30), fr, R(722), 12, 60)
        + swoosh(arc_pts(970, 530, 340, 300, 180, 480, 30), fr, R(728), 10, 40)
        + burst(970, 530, fr, R(733), 12, 12, 200, 420, 22, seed=12)))
    cursor(s, lambda fr: (step(fr, [(R(597), 1150), (R(608), 990), (R(616), 990), (R(632), 700)]),
                          step(fr, [(R(597), 680), (R(608), 560), (R(616), 560), (R(632), 720)]),
                          k(fr, R(596), 3) * (1 - k(fr, R(700), 4)), press(fr, R(610), 3)))
    return t


# ==== 8. SUSCRÍBETE / YA / A MI CANAL: a red splash settles into a box; swooshes write the two lines ==========

def red_box_lines():
    D = 4.7
    t = _p("caja-roja", "SUSCRÍBETE YA en caja roja", "SUSCRÍBETE YA in a red box", 17407, D, "tipografia",
           ["suscribirse", "caja", "español"], thumb=2.6)
    s = Y(t, D)
    R = lambda f: f - 582  # noqa: E731
    red = "#E70001"
    path = [(624, 612), (700, 470), (800, 400), (900, 390), (967, 531)]

    def splash(fr):
        if not R(586) <= fr < R(598):
            return []
        q = lin(fr, R(586), 11)
        pts = sub(chaikin(path, 2, closed=False), max(0.0, q - 0.35), q)
        out = [ribbon(pts, 34 + 90 * q, "head")] if pts else []
        for j in range(3):
            a = math.radians(200 + 50 * j)
            d = 60 + 140 * q
            out.append(ell(870 + d * math.cos(a), 420 + d * math.sin(a) + 120 * q * q, 30 * (1 - q) + 6,
                           44 * (1 - q) + 6, n=10))
        return out

    def box(fr):
        if fr < R(597) or fr > R(703):
            return []
        tall = 1 + 0.8 * math.sin(math.pi * lin(fr, R(607), 10))
        h = 202 * tall
        wav = 18 * (1 - k(fr, R(597), 8))
        top, bot = 531 - h / 2, 531 + h / 2
        pts = [(744, top), (1190, top)]
        for i in range(21):
            x = 1190 - 446 * i / 20
            pts.append((x, bot + wav * (0.5 + 0.5 * math.sin(i * 1.9 + fr * 0.7)) + (40 * wav / 18 if i % 6 == 3 else 0)))
        return [chaikin(pts, 1)]
    morph(s, "Salpicadura roja", red, splash)
    morph(s, "Caja", red, box)
    tall = lambda fr: 1 + 0.6 * math.sin(math.pi * lin(fr, R(607), 10))  # noqa: E731
    c = word(s, "YA", 967, 531, 110, WHITE, ANTON, 400, "Título",
             geom=lambda fr, u: (0, 0, tall(fr), 0, 1.0 if R(599) <= fr < R(700) else 0.0))
    del c
    for name, txt, cy, at, end, order in (("Texto", "SUSCRÍBETE", 343, R(617), R(708), "forward"),
                                          ("Texto 2", "A MI CANAL", 740, R(621), R(712), "backward")):
        c = word(s, txt, 960, cy, 112, WHITE, ANTON, 400, name,
                 geom=lambda fr, u, at=at: (0, 0, 1, 0, 1 if fr >= at else 0))
        letters(s, c, ("fade", at, 0.03, 0.05, order), ("fade", end, 0.025, 0.05))
        spacing(s, c, lambda fr, at=at: 14 + 30 * (1 - k(fr, at + 3, 12)))

    def wave(fr):
        out = swoosh([(600, 343), (960, 330), (1320, 343)], fr, R(616), 10, 26, profile="head")
        out += swoosh([(1330, 740), (960, 755), (600, 740)], fr, R(620), 10, 26, profile="head")
        if R(689) <= fr <= R(708):
            q = lin(fr, R(689), 14)
            r = 40 + 300 * q
            out.append(blob(760 + 200 * q, 560 - 20 * q, r * (1 + 0.2 * k(fr, R(702), 5)), r * 0.85, 0, 0.12, 3,
                            fr * 0.2))
        return out + burst(960, 640, fr, R(704), 18, 22, 80, 460, 30, seed=13, spread=200, a0=-10)
    morph(s, "Ola", WHITE, wave)
    return t


# ==== 9. SUBSCRIBE (small) with arrows: the box paints itself white and drains; arrows bob ==================

def subscribe_arrows():
    D = 5.6
    t = _p("suscribete-flechas", "Botón Subscribe rojo con flechas", "Red Subscribe button with arrows", 17408, D,
           "redes", ["suscribirse", "botón", "flechas"], thumb=3.0)
    s = Y(t, D)
    R = lambda f: f - 582  # noqa: E731
    red = "#E9001A"
    wf = lambda fr: step(fr, [(R(586), 0.4), (R(591), 1.35), (R(596), 0.95), (R(600), 1.0)]) * \
        (1 - k(fr, R(737), 10))  # noqa: E731
    s.obj("Botón", solid(red), lambda fr, u: (902, 535, 672 * wf(fr), 182, 0, 1 if fr >= R(586) else 0),
          base=(672, 182))
    c = word(s, "SUBSCRIBE", 977, 535, 40, WHITE, M, 800, "Título",
             geom=lambda fr, u: (0, 0, 1, 0, 1 if fr >= R(614) else 0))
    letters(s, c, ("fade", R(614), 0.02, 0.1), ("fade", R(737), 0.03, 0.08, "random"))
    drop_with_notch(s, "Gota", WHITE, lambda fr: (682, 535, 120 * pop(fr, R(625), 4) * (1 - k(fr, R(736), 6)), 0, 1),
                    hole=False)

    def paint(fr):
        out = []
        if R(593) <= fr <= R(604):
            q = lin(fr, R(593), 10)
            for j in range(9):
                a = math.radians(40 * j + 300 * q)
                out.append(ell(902 + 420 * math.cos(a), 535 + 170 * math.sin(a), 12 * (1 - q * 0.6), 7, a * 57, 10))
        if R(601) <= fr <= R(612):
            q = lin(fr, R(601), 6)
            out.append(ribbon([(950, 220), (950, 220 + 230 * q)], 14, "flat"))
        if R(605) <= fr <= R(620):
            bot = 444 + 182 * k(fr, R(605), 4) * (1 - k(fr, R(612), 8))
            pts = [(566, 444), (1238, 444)]
            for i in range(25):
                x = 1238 - 672 * i / 24
                pts.append((x, bot + (30 if i % 3 == 1 else 0) * (1 - k(fr, R(616), 4))))
            out.append(pts)
        if R(618) <= fr < R(626):
            q = lin(fr, R(618), 7)
            out.append(ribbon([(690, 300 + 220 * q), (686, 360 + 175 * q)], 16 * (1 - q * 0.5), "lens"))
        out += swoosh(arc_pts(902, 535, 420, 200, 200, 420, 30), fr, R(728), 10, 10)
        out += swoosh(arc_pts(902, 535, 420, 200, 20, 240, 30), fr, R(731), 10, 10)
        return out
    morph(s, "Pintura", WHITE, paint)
    bob = lambda fr, ph=0.0: math.sin(2 * math.pi * fr / 22 + ph)  # noqa: E731
    out = lambda fr: 1 - k(fr, R(740), 6)  # noqa: E731
    arrow(s, "Flecha 1", WHITE, red, lambda fr: (850, 250 + 22 * bob(fr), 230, 180, pop(fr, R(627), 6) * out(fr)))
    arrow(s, "Flecha 2", WHITE, red, lambda fr: (912, 840 - 22 * bob(fr), 230, 0, pop(fr, R(645), 6) * out(fr)))
    return t


# ==== 10. LIKE → NEW VIDEO: a pink blob pops, «Like» types in, a click turns it into «New Video»; hearts =======

def new_video_pink():
    D = 4.4
    t = _p("nuevo-video-rosa", "New Video con mancha rosa y corazones", "New Video with a pink blob and hearts",
           17409, D, "redes", ["nuevo video", "corazones"], thumb=2.6)
    s = Y(t, D)
    R = lambda f: f - 759  # noqa: E731
    pink, light = "#F48C99", "#FAC6CB"
    size = lambda fr: (step(fr, [(R(762), 0.1), (R(765), 1.4), (R(767), 1.25), (R(771), 1.05), (R(773), 1.0)])  # noqa: E731
                       * (1 - 0.1 * math.sin(math.pi * lin(fr, R(786), 5))) * (1 - k(fr, R(875), 4)))
    cx = lambda fr: step(fr, [(R(762), 638), (R(765), 667)])  # noqa: E731
    morph(s, "Brillo", pink, lambda fr: [blob(667, 516, 300, 260, 0, 0.1, 5, fr * 0.1)] if R(788) <= fr < R(796)
          else [], alpha=0.35)
    morph(s, "Mancha", pink, lambda fr: [blob(cx(fr), 516, 221 * size(fr), 192 * size(fr), 0, 0.09, 2, fr * 0.06)]
          if fr >= R(762) and size(fr) > 0.02 else [])
    morph(s, "Gota", light, lambda fr: [drop(cx(fr) - 6 * size(fr), 504, 216 * size(fr), 12)]
          if fr >= R(763) and size(fr) > 0.05 else [])
    c = word(s, "Like", 994, 550, 115, WHITE, M, 800, "Texto (paso)", align="left", editable=False,
             geom=lambda fr, u: (0, 0, 1, 0, 1 if fr < R(787) else 0))
    letters(s, c, ("pop", R(765), 0.1, 0.15))
    c = word(s, "New Video", 792, 516, 120, WHITE, M, 800, "Título", align="left",
             geom=lambda fr, u: (0, 0, 1, 0, 1 if fr >= R(788) else 0))
    letters(s, c, None, ("fade", R(877), 0.04, 0.08, "random"))

    def hearts(fr):
        out = []
        for j, (x, at) in enumerate(((1100, 822), (1180, 824), (1260, 821), (1330, 826), (1220, 829), (1150, 831))):
            q = lin(fr, R(at), 12)
            if 0 < q < 1:
                out.append(heart(x + 20 * math.sin(q * 6 + j), 470 - 220 * q, 40 * (1 - q) + 8, 10 * math.sin(j)))
        if R(872) <= fr <= R(879):
            out.append(heart(1000, 516, 260 * pop(fr, R(872), 5), 0))
        rnd = random.Random(4)
        if R(878) <= fr <= R(890):
            q = lin(fr, R(878), 12)
            for j in range(18):
                a = rnd.uniform(0, 6.28)
                d = rnd.uniform(60, 420) * (1 - (1 - q) ** 2)
                out.append(heart(800 + d * math.cos(a), 516 + d * math.sin(a) * 0.6, 44 * (1 - q) + 4, 0))
        return out
    morph(s, "Corazones", pink, hearts)
    morph(s, "Destellos", WHITE, lambda fr: (
        rays(1100, 550, fr, R(786), 6, 7, 40, 140, 70, 10)
        + burst(900, 516, fr, R(788), 10, 18, 250, 520, 14, seed=14, ry=0.5)
        + rays(800, 516, fr, R(878), 8, 14, 160, 320, 60, 6)))
    cursor(s, lambda fr: (step(fr, [(R(767), 1400), (R(782), 720)]), step(fr, [(R(767), 760), (R(782), 560)]),
                          k(fr, R(766), 3) * (1 - k(fr, R(870), 4)), press(fr, R(785), 3)))
    return t


# ==== 11. SUBSCRIBE under a moon that turns into a sleepy thumb with a night cap: Like New Video ===============

THUMB_B = poly(chaikin([(20, 0), (45, 0), (48, 40), (75, 42), (95, 55), (100, 75), (92, 95), (70, 100), (15, 100),
                        (0, 85), (5, 40)], 2))
CAP = chaikin([(100, 100), (98, 60), (80, 30), (55, 8), (25, 0), (5, 10), (22, 20), (45, 40), (50, 70), (40, 100)], 2)


def moon_thumb():
    D = 4.9
    t = _p("luna", "SUBSCRIBE con luna y Like New Video", "SUBSCRIBE with a moon and Like New Video", 17410, D,
           "redes", ["suscribirse", "luna", "me gusta"], thumb=1.4)
    s = Y(t, D)
    R = lambda f: f - 759  # noqa: E731
    orange, blue = "#F49338", "#0EA4C7"
    mx = lambda fr: step(fr, [(R(788), 902), (R(801), 624)])  # noqa: E731

    def moon(fr):
        sc = pop(fr, R(762), 4) * (1 - k(fr, R(817), 5))
        if sc < 0.02:
            return []
        return [ribbon(arc_pts(mx(fr) + 60 * sc, 530, 240 * sc, 264 * sc, 115, 245, 30), 70 * sc, "lens")]
    morph(s, "Luna", orange, moon)
    stars = ((542, 324), (648, 454), (710, 300), (782, 324), (1176, 324), (1272, 564))

    def star_pts(fr):
        out = []
        for j, (x, y) in enumerate(stars):
            sc = pop(fr, R(762) + j % 3, 4)
            q = k(fr, R(816), 6)
            x2, y2 = x + (560 - x) * q, y + (300 - y) * q
            if fr >= R(822):
                continue
            out.append(star(x2, y2, 52 * sc * (1 - 0.6 * q), 12 * math.sin(fr / 6 + j)))
        return out
    morph(s, "Estrellas", blue, star_pts)
    c = word(s, "SUBSCRIBE", 1121, 540, 120, WHITE, M, 800, "Título",
             geom=lambda fr, u: (0, 0, 1, 0, k(fr, R(787), 2) * (1 - k(fr, R(817), 4))))
    spacing(s, c, lambda fr: 60 * (1 - k(fr, R(788), 9)) + 50 * k(fr, R(816), 5))
    thumb = lambda fr: pop(fr, R(818), 9, 0.1) * (1 - k(fr, R(898), 6))  # noqa: E731
    tilt = lambda fr: 20 * k(fr, R(896), 6)  # noqa: E731
    s.obj("Pulgar", solid(orange), lambda fr, u: (679, 559, 254 * thumb(fr), 470 * thumb(fr), tilt(fr), 1),
          path=THUMB_B, base=(254, 470))

    def cap(fr):
        sc = pop(fr, R(820), 7) * (1 - k(fr, R(898), 6))
        if sc < 0.02:
            return []
        return [xform(CAP, 576, 300, 240 * sc, 192 * sc, tilt(fr))]
    morph(s, "Gorro", blue, cap)

    def pom(fr):
        sc = pop(fr, R(822), 6) * (1 - k(fr, R(898), 6))
        if sc < 0.02:
            return []
        dots = [ell(468, 214, 20 * sc, 20 * sc, n=12)]
        for x, y in ((560, 260), (610, 300), (600, 350), (520, 250)):
            dots.append(ell(x, y, 6 * sc, 6 * sc, n=8))
        return dots
    morph(s, "Pompón", WHITE, pom)
    for i, (txt, cy, at, end) in enumerate((("Like", 353, R(816), R(897)), ("New", 550, R(818), R(895)),
                                            ("Video", 732, R(822), R(891)))):
        c = word(s, txt, 1363, cy, 130, WHITE, M, 800, "Título 2" if i == 0 else f"Texto {i}" if i > 1 else "Texto",
                 align="right", geom=lambda fr, u, at=at, end=end: (0, 0, 1, 0, k(fr, at, 3) * (1 - k(fr, end - 5, 5))))
        spacing(s, c, lambda fr, at=at: 50 * (1 - k(fr, at, 8)))
    morph(s, "Burbujas", WHITE, lambda fr: (
        burst(1000, 540, fr, R(786), 12, 9, 40, 260, 28, seed=15)
        + burst(1100, 540, fr, R(815), 12, 6, 100, 300, 50, seed=16)
        + swoosh(chaikin([(1460, 780), (1150, 790), (900, 740), (720, 600)], 2, closed=False), fr, R(882), 14, 80,
                 lag=0.5)
        + burst(679, 560, fr, R(899), 8, 12, 60, 300, 26, seed=17)))
    cursor(s, lambda fr: (step(fr, [(R(767), 1300), (R(782), 930)]), step(fr, [(R(767), 800), (R(782), 600)]),
                          k(fr, R(765), 3) * (1 - k(fr, R(800), 4)), press(fr, R(785), 3)))
    return t


# ==== 12. CHECK NEW VIDEO: green and white brush strokes swirl into a green tick; a white splash wipes it ========

VEE = chaikin([(0, 2), (30, 0), (50, 62), (82, 0), (100, 3), (56, 100), (38, 100)], 1)


def check_video():
    D = 3.7
    t = _p("check", "Check New Video con visto verde", "Check New Video with a green tick", 17411, D, "redes",
           ["visto", "nuevo video"], thumb=1.9)
    s = Y(t, D)
    R = lambda f: f - 759  # noqa: E731
    green = "#49FE57"
    pulse = lambda fr: 1 - 0.1 * math.sin(math.pi * lin(fr, R(814), 8))  # noqa: E731

    def vee(fr):
        sc = pop(fr, R(779), 6) * pulse(fr)
        if sc < 0.02 or fr > R(848):
            return []
        sx = 1 - 0.85 * k(fr, R(836), 6)
        return [xform(VEE, 668, 420, 259 * sc * sx, 336 * sc, -10 * (1 - k(fr, R(779), 6)))]
    morph(s, "Visto", green, vee)
    morph(s, "Pinceladas", green, lambda fr: (
        swoosh([(560, 300), (566, 440), (580, 570)], fr, R(764), 8, 14, lag=1.0)
        + swoosh(arc_pts(950, 520, 420, 200, 200, 470, 30), fr, R(773), 10, 22)
        + rays(668, 420, fr, R(780), 6, 6, 160, 240, 50, 9)
        + ([ribbon([(668, 300), (668, 560)], 8 * (1 - lin(fr, R(842), 6)), "lens")] if R(842) <= fr <= R(848) else [])))
    for i, (txt, cy, at, end) in enumerate((("Check", 372, R(767), R(848)), ("New", 550, R(771), R(851)),
                                            ("Video", 727, R(773), R(855)))):
        c = word(s, txt, 1368, cy, 118, WHITE, M, 800, "Título" if i == 0 else f"Texto {i}" if i > 1 else "Texto",
                 align="right", geom=lambda fr, u, at=at: (0, 0, pulse(fr), 0, k(fr, at, 3)))
        spacing(s, c, lambda fr, at=at: 50 * (1 - k(fr, at, 7)))
        letters(s, c, None, ("fade", end, 0.03, 0.06))
    morph(s, "Trazos", WHITE, lambda fr: (
        swoosh([(640, 420), (820, 412), (1000, 410)], fr, R(763), 7, 16)
        + swoosh([(600, 700), (750, 696), (900, 690)], fr, R(765), 7, 12)
        + swoosh(arc_pts(900, 540, 380, 120, 120, 420, 30), fr, R(766), 10, 22)
        + swoosh(arc_pts(960, 560, 420, 300, 200, 380, 30), fr, R(843), 10, 90)
        + burst(960, 560, fr, R(850), 16, 18, 100, 420, 20, seed=18)))
    return t


# ==== 13. YOUR LOGO: the logo pops inside orbiting arcs and blue ink; «Your Logo» rises below =================

def your_logo():
    D = 4.9
    t = _p("tu-logo", "Your Logo con tinta azul", "Your Logo with blue ink", 17412, D, "aperturas",
           ["logo", "tinta"], thumb=2.6)
    s = Y(t, D)
    R = lambda f: f - 759  # noqa: E731
    blue = "#3B9BF5"
    ly = lambda fr: step(fr, [(R(792), 574), (R(801), 353)])  # noqa: E731
    lsc = lambda fr: pop(fr, R(762), 5) * step(fr, [(R(890), 1.0), (R(893), 1.15), (R(897), 0.0)])  # noqa: E731
    s.pic("Tu logo", "logo-flip", lambda fr, u: (955, ly(fr), 300 * lsc(fr), 300 * lsc(fr), 0,
                                                 1 if lsc(fr) > 0.01 else 0),
          label="Tu logo", base=(300, 300), brandRole="logo")

    def white(fr):
        out = []
        if R(762) <= fr <= R(786):
            r = 170 + 60 * k(fr, R(765), 8)
            span = 60 + 80 * k(fr, R(765), 8)
            for off in (0, 180):
                a0 = off + 8 * (fr - R(762))
                out.append(ribbon(arc_pts(955, 574, r, r, a0, a0 + span, 16), 7 * (1 - k(fr, R(782), 4)) + 1, "flat"))
        if R(762) <= fr <= R(766):
            out += [ell(715, 574, 14, 14, n=10), ell(1195, 574, 14, 14, n=10)]
        out += burst(955, 574, fr, R(784), 12, 16, 200, 300, 8, seed=19)
        out += burst(955, 760, fr, R(893), 12, 10, 60, 360, 40, seed=20)
        return out
    morph(s, "Arcos", WHITE, white)

    def ink(fr):
        out = swoosh([(955, 250), (955, 330), (955, 420)], fr, R(772), 6, 14, lag=1.0)
        out += swoosh(arc_pts(955, 574, 235, 235, -90, 200, 30), fr, R(777), 10, 16)
        if R(782) <= fr <= R(792):
            q = lin(fr, R(782), 10)
            for x in (890, 1015):
                out.append(ribbon([(x, 780), (x, 780 + 140 * q)], 12 * (1 - q) + 2, "lens"))
        out += swoosh(arc_pts(955, 640, 330, 220, 150, 230, 20), fr, R(797), 10, 40)
        out += swoosh(arc_pts(955, 640, 330, 220, 30, -50, 20), fr, R(797), 10, 40)
        out += burst(955, 770, fr, R(886), 12, 7, 20, 200, 34, seed=21)
        return out
    morph(s, "Tinta", blue, ink)
    bounce = lambda fr: 1 + 0.08 * math.sin(math.pi * lin(fr, R(878), 7))  # noqa: E731
    c = word(s, "Your", 960, 593, 106, WHITE, M, 800, "Título",
             geom=lambda fr, u: (0, 0, bounce(fr), -4, 1 if fr >= R(800) else 0))
    letters(s, c, ("rise", R(801), 0.08, 0.2), ("rise", R(890), 0.05, 0.15, "backward"))
    c = word(s, "Logo", 960, 766, 100, WHITE, M, 800, "Texto",
             geom=lambda fr, u: (0, 0, bounce(fr), 3, 1 if fr >= R(804) else 0))
    spacing(s, c, lambda fr: 36)
    letters(s, c, ("drop", R(805), 0.08, 0.2), ("fade", R(893), 0.05, 0.1))
    return t


# ==== 14. NUEVO / VIDEO / AQUÍ with a beige thumb that rises up; white swooshes write and wipe the lines ========

THUMB_UP = poly(chaikin([(30, 0), (48, 4), (52, 30), (80, 40), (100, 62), (96, 90), (78, 100), (25, 100), (8, 80),
                         (10, 45), (22, 30)], 2))


def thumb_lines():
    D = 3.8
    t = _p("pulgar-beige", "NUEVO VIDEO AQUÍ con pulgar", "NUEVO VIDEO AQUÍ with a thumb", 17413, D, "tipografia",
           ["pulgar", "español"], thumb=1.8)
    s = Y(t, D)
    R = lambda f: f - 324  # noqa: E731
    beige = "#E5CC91"

    def thumb(fr, u):
        up = k(fr, R(327), 9)
        fall = k(fr, R(421), 6)
        wig = 6 * math.sin(2 * math.pi * fr / 30) * k(fr, R(358), 6) * (1 - k(fr, R(405), 6))
        rot = 80 * (1 - up) + wig + 80 * fall
        flat = 1 - 0.8 * k(fr, R(427), 4)
        return (1159 + 60 * (1 - up), 693 + 120 * (1 - up) + 120 * fall, 216 * (0.5 + 0.5 * up), 370 * flat,
                rot, (1 if fr >= R(326) else 0) * (1 - k(fr, R(429), 4)))
    s.obj("Pulgar", solid(beige), thumb, path=THUMB_UP, base=(216, 370))
    rows = (("Título", "NUEVO", 589, R(337), R(418)), ("Texto", "VIDEO", 719, R(343), R(421)),
            ("Texto 2", "AQUÍ", 841, R(345), R(424)))
    for name, txt, cy, at, end in rows:
        c = word(s, txt, 653, cy, 86, WHITE, ANTON, 400, name, align="left",
                 geom=lambda fr, u, at=at: (0, 0, 1, 0, 1 if fr >= at else 0))
        letters(s, c, ("fade", at, 0.04, 0.06), ("fade", end, 0.03, 0.05))
        spacing(s, c, lambda fr, at=at, end=end: 30 * (1 - k(fr, at, 7)) + 30 * k(fr, end - 6, 6))
    morph(s, "Trazos", WHITE, lambda fr: (
        burst(1060, 760, fr, R(336), 8, 8, 30, 160, 12, seed=22)
        + swoosh([(640, 600), (800, 585), (950, 590)], fr, R(337), 6, 20)
        + ([blob(720, 719, 70 * pop(fr, R(341), 4), 50 * pop(fr, R(341), 4), 0, 0.15, 6, fr)]
           if R(341) <= fr <= R(347) else [])
        + swoosh([(640, 850), (820, 838), (1000, 845)], fr, R(349), 6, 18)
        + ([ell(1120, 560, 40 * pop(fr, R(408), 4), 32 * pop(fr, R(408), 4), n=14)] if R(408) <= fr < R(414) else [])
        + swoosh(arc_pts(790, 620, 200, 120, 200, 340, 20), fr, R(414), 8, 50)
        + swoosh(arc_pts(800, 780, 240, 160, 180, 360, 24), fr, R(417), 8, 70)
        + burst(1100, 820, fr, R(426), 9, 10, 40, 220, 14, seed=23)))
    return t


# ==== 15. NEW PODCAST: a white drop splashes the words in; a red drop is clicked away; a splash wipes them =====

def podcast():
    D = 3.4
    t = _p("podcast", "NEW PODCAST con salpicadura", "NEW PODCAST with a splash", 17414, D, "tipografia",
           ["podcast"], thumb=2.0)
    s = Y(t, D)
    R = lambda f: f - 324  # noqa: E731
    red = "#EE4B5A"
    for name, txt, cy, at, end in (("Título", "NEW", 450, R(327), R(414)), ("Título 2", "PODCAST", 625, R(330), R(421))):
        c = word(s, txt, 960, cy, 125, WHITE, M, 700, name,
                 geom=lambda fr, u, at=at: (0, 0, 1, 0, 1 if fr >= at else 0))
        letters(s, c, ("drop", at, 0.05, 0.15), ("fade", end, 0.04, 0.06, "random"))
        spacing(s, c, lambda fr, at=at, end=end: 50 * (1 - k(fr, at, 7)) + 40 * k(fr, end - 7, 7))

    def red_drop(fr):
        if R(338) <= fr < R(356):
            sc = pop(fr, R(338), 4) * (1 - k(fr, R(353), 3))
            return [drop(1250, 440, 128 * sc, 8)] if sc > 0.02 else []
        if R(358) <= fr < R(376):
            sc = pop(fr, R(358), 4) * (1 - k(fr, R(373), 3))
            return [drop(656, 466, 128 * sc, 8)] if sc > 0.02 else []
        return []
    morph(s, "Gota roja", red, red_drop)
    morph(s, "Chispas", red, lambda fr: rays(1250, 440, fr, R(355), 6, 6, 40, 110, 50, 7)
          + rays(656, 466, fr, R(375), 8, 7, 40, 130, 60, 8))

    def white(fr):
        out = []
        if R(325) <= fr < R(331):
            q = lin(fr, R(325), 5)
            out.append(drop(960, 150 + 330 * q, 80, 0))
        out += rays(960, 520, fr, R(330), 8, 7, 20, 180, 140, 20, a0=-170, spread=160)
        out += swoosh(arc_pts(860, 470, 120, 90, 180, 330, 16), fr, R(333), 6, 18)
        out += swoosh(arc_pts(1060, 470, 120, 90, 210, 360, 16), fr, R(334), 6, 18)
        out += rays(960, 520, fr, R(406), 6, 6, 20, 160, 120, 16, a0=-150, spread=120)
        if R(409) <= fr < R(415):
            out.append(drop(960, 520, 230 * pop(fr, R(409), 4), 0))
        out += burst(960, 540, fr, R(414), 12, 16, 60, 460, 36, seed=24)
        return out
    morph(s, "Salpicadura", WHITE, white)
    cursor(s, lambda fr: (step(fr, [(R(340), 1400), (R(346), 1262), (R(356), 1262), (R(366), 668)]),
                          step(fr, [(R(340), 620), (R(346), 460), (R(356), 460), (R(366), 490)]),
                          k(fr, R(339), 3) * (1 - k(fr, R(390), 4)), max(press(fr, R(352), 3), press(fr, R(372), 3))))
    return t


TEMPLATES = [like_yellow, social_title, account, subscribe_dots, new_video_purple, my_channel, subscribe_sticker,
             red_box_lines, subscribe_arrows, new_video_pink, moon_thumb, check_video, your_logo, thumb_lines, podcast]

_ONLY = os.environ.get("YP10_ONLY")
if _ONLY:
    TEMPLATES = [f for f in TEMPLATES if f.__name__ in _ONLY.split(",")]
