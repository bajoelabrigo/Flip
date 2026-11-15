"""Video 35450339.mp4 as Kit de YouTube Stock templates (yp13-*). See docs/plan-youtube-pack-2.md.

«Social Media Buttons, 70+ elements» (1920×1080 at 25 fps): flat cartoon pieces with thick black outlines and hard
drop shadows on light grey — post cards, chats, search bars, ratings and stars, counters, round badges, toggles,
progress, players, checklists — most of them shown in 2×2 grids (each quarter is one piece, laid out ×2 about its
panel's centre), a few full screen over footage. Each was studied on 10 fps sheets (study notes in
tienda/plantillas/estudio-35450339/NOTAS.md). The pieces have no background (transparent), so they sit on the user's
video; `t.background` is the reference's grey only for the Stock card.

Times are the reference's frames (25 fps). Q.frame(u) runs the reference's frames from the piece's first one; once the
hold ends it plays the entrance backwards (as the reference leaves), while clicks, counters and cursors keep to the
real time (Q.R(u)) so a liked heart stays red while the card folds away.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from scene import keys, tanim
from templates_tit_c import SMOOTH  # noqa: F401
from templates_tit_e import solid
from templates_tit_h import S, TRIANGLE, arc, poly, regular  # noqa: F401
from templates_yp0 import BELL, HAND, HAND_LINES, THUMB, THUMB_DOWN, _turn  # noqa: F401

M = "Montserrat"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium"),
               (400, "Regular")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"

SRC = 25.0
WHITE, INK, SHADOW = "#FFFFFF", "#151515", "#1B1B1B"
RED, BLUE, GREEN, YELLOW = "#F04A4E", "#1C9BD0", "#1DA35A", "#F9B91A"
GREY, PANEL = "#BDBDBD", "#E3E7EB"
QUARTERS = {"tl": (500, 287.5, 2.0), "tr": (1420, 287.5, 2.0), "bl": (500, 792.5, 2.0), "br": (1420, 792.5, 2.0),
            "full": (960, 540, 1.0)}


def k(fr, at, n):
    """Smooth 0 → 1 from frame at over n frames."""
    return SMOOTH(min(1.0, max(0.0, (fr - at) / max(1e-6, n))))


def lin(fr, at, n):
    return min(1.0, max(0.0, (fr - at) / max(1e-6, n)))


def pop(fr, at, n=6, over=0.18):
    """0 → 1 with an overshoot (a pop)."""
    q = lin(fr, at, n)
    if q <= 0:
        return 0.0
    if q < 0.6:
        return (1 + over) * math.sin(q / 0.6 * math.pi / 2)
    return 1 + over * (1 - SMOOTH((q - 0.6) / 0.4))


# --- paths (0..100 box) --------------------------------------------------------------------------------------------
def circ(cx, cy, r, n=28, ccw=False):
    pts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    return poly(pts[::-1] if ccw else pts)


HEART = ("M 50 92 C 22 72 3 54 3 31 C 3 15 15 5 29 5 C 39 5 46 11 50 19 C 54 11 61 5 71 5 C 85 5 97 15 97 31 "
         "C 97 54 78 72 50 92 Z")
BUBBLE = ("M 50 8 C 26 8 8 25 8 46 C 8 57 13 67 21 74 L 14 93 L 36 83 C 40 84 45 85 50 85 C 74 85 92 68 92 46 "
          "C 92 25 74 8 50 8 Z")
SQBUB = "M 8 10 L 92 10 L 92 72 L 44 72 L 24 92 L 26 72 L 8 72 Z"
RETWEET = ("M 14 46 L 14 22 L 74 22 M 62 8 L 76 22 L 62 36 M 86 54 L 86 78 L 26 78 M 38 64 L 24 78 L 38 92")
SHARE = (circ(78, 18, 12) + " " + circ(78, 82, 12) + " " + circ(20, 50, 12) + " M 30 44 L 68 24 M 30 56 L 68 76")
PLANE = "M 6 42 L 94 8 L 62 94 L 46 56 Z M 46 56 L 94 8"
ARROWR = "M 6 82 C 10 52 30 38 60 38 L 60 18 L 94 50 L 60 82 L 60 62 C 36 62 18 68 6 82 Z"
CHECK = "M 12 52 L 40 80 L 90 20"
STAR = poly([(50 + (50 if i % 2 == 0 else 21) * math.cos(math.radians(-90 + 36 * i)),
              54 + (50 if i % 2 == 0 else 21) * math.sin(math.radians(-90 + 36 * i))) for i in range(10)])
PERSON = circ(50, 28, 22) + " M 8 98 C 8 70 26 56 50 56 C 74 56 92 70 92 98 Z"
SEARCH = circ(42, 42, 30) + " M 64 64 L 92 92"
PIN = "M 50 98 C 40 80 14 58 14 36 C 14 16 30 2 50 2 C 70 2 86 16 86 36 C 86 58 60 80 50 98 Z " + circ(50, 36, 14, ccw=True)
PAUSE = "M 20 10 L 40 10 L 40 90 L 20 90 Z M 60 10 L 80 10 L 80 90 L 60 90 Z"
FFWD = "M 6 14 L 50 50 L 6 86 Z M 50 14 L 94 50 L 50 86 Z"
REW = "M 94 14 L 50 50 L 94 86 Z M 50 14 L 6 50 L 50 86 Z"
CART = ("M 4 10 L 20 10 L 32 66 L 84 66 L 94 26 L 24 26 M 38 88 L 38 88 M 76 88 L 76 88 "
        + circ(40, 86, 7) + " " + circ(78, 86, 7))
DOWNLOAD = "M 50 8 L 50 66 M 26 44 L 50 68 L 74 44 M 12 70 L 12 90 L 88 90 L 88 70"
SMILE = circ(50, 50, 46) + " M 30 60 C 38 74 62 74 70 60 M 34 36 L 34 42 M 66 36 L 66 42"
# The arrow pointer: tip at (0, 0) of its box (w:h = 0.66).
ARROW = poly([(4, 2), (4, 80), (24, 63), (38, 96), (54, 89), (40, 57), (68, 57)])
ARROW_TIP = (0.06, 0.02)
HAND_TIP = (0.35, 0.0)
BIRD = ("M 98 22 C 94 24 90 25 86 25 C 90 22 93 18 94 14 C 90 16 86 18 82 19 C 78 15 73 13 67 13 C 56 13 47 22 47 33 "
        "C 47 35 47 36 48 38 C 31 37 17 29 7 17 C 5 20 4 24 4 28 C 4 35 8 41 13 44 C 10 44 7 43 4 42 C 4 52 11 61 21 63 "
        "C 17 64 14 64 11 63 C 14 72 22 79 32 79 C 24 85 15 89 4 89 C 3 89 1 89 0 89 C 10 95 21 99 33 99 "
        "C 67 99 86 71 86 46 L 86 43 C 91 40 95 36 98 32 Z")
INSTA = ("M 30 6 L 70 6 C 84 6 94 16 94 30 L 94 70 C 94 84 84 94 70 94 L 30 94 C 16 94 6 84 6 70 L 6 30 "
         "C 6 16 16 6 30 6 Z " + circ(50, 50, 20) + " " + circ(74, 26, 3))


# --- layers --------------------------------------------------------------------------------------------------------
def _c(colour, alpha=1.0):
    return "#" + format(round(alpha * 255), "02x") + colour.lstrip("#").lower()[-6:]


def fill(colour, alpha=1.0):
    return {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0, "paint": {"kind": "solid",
                                                                                       "color": _c(colour, alpha)}}


def nofill():
    return {"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}


def stroke(colour, width, align="inside"):
    return {"id": "stroke", "kind": "stroke", "enabled": width > 0, "width": width, "strokeAlign": align,
            "opacity": 1.0, "paint": {"kind": "solid", "color": _c(colour)}}


def hard(dx, dy, colour=SHADOW):
    return {"id": "shadow", "kind": "shadow", "enabled": True, "paint": {"kind": "solid", "color": _c(colour)},
            "offsetX": dx, "offsetY": dy, "blur": 0, "opacity": 1.0}


class Q(S):
    """One piece; geometry in the reference's pixels of its quarter (or the full frame), times in its frames."""

    def __init__(self, t, f0, fe, h, quarter="full", speed=1.2, end=None):
        dur = span(f0, fe, h, speed, end)
        S.__init__(self, t, dur)
        self.f0, self.fe, self.h, self.sp = f0, fe, h, speed
        self.cx, self.cy, self.sc = QUARTERS[quarter]
        t.background = PANEL

    # time
    def frame(self, u):
        r = self.f0 + u * SRC
        if r <= self.h:
            return r
        return max(self.f0 - 1, self.fe - (r - self.h) * self.sp)

    def R(self, u):
        return self.f0 + u * SRC

    # space
    def X(self, x):
        return 960 + self.sc * (x - self.cx)

    def Y(self, y):
        return 540 + self.sc * (y - self.cy)

    def rect_(self, r):
        return (self.X(r[0]), self.Y(r[1]), self.X(r[2]), self.Y(r[3]))

    # layer helpers at the piece's scale
    def card_l(self, colour=WHITE, line=3.0, drop=9.0, ink=INK):
        out = []
        if drop:
            out.append(hard(drop * self.sc, drop * self.sc))
        out.append(fill(colour))
        out.append(stroke(ink, line * self.sc) if line else stroke(ink, 0))
        return out

    def line_l(self, colour=INK, width=2.5, cap_fill=None):
        return [fill(cap_fill) if cap_fill else nofill(), stroke(colour, width * self.sc, "center")]

    # shapes
    def shp(self, name, layers, g, kind="rectangle", path=None, radius=0.0, base=None):
        """g(fr, u) = (cx, cy, w, h, rot, op) in reference px."""
        def gg(fr, u):
            cx, cy, w, h, rot, op = g(fr, u)
            return self.X(cx), self.Y(cy), w * self.sc, h * self.sc, rot, op
        return self.obj(name, layers, gg, kind=kind, path=path, radius=radius * self.sc,
                        base=(base[0] * self.sc, base[1] * self.sc) if base else None)

    def box(self, name, layers, r, op=None, radius=0.0, kind="rectangle", path=None, base=None):
        """r(fr, u) = (x0, y0, x1, y1) in reference px."""
        def g(fr, u):
            x0, y0, x1, y1 = r(fr, u)
            return (x0 + x1) / 2, (y0 + y1) / 2, max(0.0, x1 - x0), max(0.0, y1 - y0), 0.0, op(fr, u) if op else 1.0
        return self.shp(name, layers, g, kind=kind, path=path, radius=radius, base=base)

    def icon(self, name, layers, cx, cy, w, h, g=None, path=None, kind="rectangle", radius=0.0):
        """A still shape at (cx, cy) w × h; g(fr, u) = (scale, op[, dx, dy, rot])."""
        def gg(fr, u):
            v = g(fr, u) if g else (1.0, 1.0)
            sc, op = v[0], v[1]
            dx, dy, rot = (v[2], v[3], v[4]) if len(v) > 2 else (0.0, 0.0, 0.0)
            return cx + dx, cy + dy, w * max(1e-3, sc), h * max(1e-3, sc), rot, op if sc > 0.01 else 0.0
        return self.shp(name, layers, gg, path=path, kind=kind, radius=radius, base=(w, h))

    # text
    def txt(self, content, ink, weight=800, colour=INK, name="Texto", align="left", g=None, op=None, slide=None,
            family=M, editable=True, layers=None):
        """ink = (x0, cap top, x1, baseline) in reference px. g(fr, u) = (dx, dy, scale, rot, op) in reference px;
        slide = (at, n, dist): it slides in from the left by dist px behind its own left edge, fading in."""
        sc = self.sc
        r = self.rect_(ink)
        kw = {}
        if slide:
            at, n, dist = slide
            edge = r[0] - 2 * sc
            kw["reveal"] = lambda fr: (edge, -2000, 4000, 4000)
            kw["shift"] = lambda fr: (-dist * sc * (1 - k(fr, at, n)), 0.0)
            kw["op"] = lambda fr, u: k(fr, at, n * 0.8)
        else:
            if g:
                kw["geom"] = lambda fr, u: (lambda v: (v[0] * sc, v[1] * sc, v[2], v[3], v[4]))(g(fr, u))
            if op:
                kw["op"] = op
        return self.say(content, r, family, weight, colour, name, align=align, editable=editable, layers=layers, **kw)

    def counter(self, clip, start, end, at_frame, frames):
        clip["textStyle"].update(counter=True, counterFrom=start, counterSeconds=round(frames / SRC, 3),
                                 counterCurve="linear")
        clip["textContent"] = str(end)
        return clip

    def typed(self, clip, at, stagger=0.04, duration=0.04, preset="typewriter", order="forward", unit="character"):
        """Letters come in from reference frame `at` (absolute); they leave backwards with the piece."""
        lead = round((at - self.f0) / SRC, 3)
        out_lead = round((self.h - self.f0) / SRC, 3)
        clip["textStyle"]["animation"] = {
            "in": tanim(preset, duration=duration, unit=unit, stagger=stagger, ease="easeOut", delay=lead,
                        order=order)}
        del out_lead
        # gone while its field is folded away (the exit plays the entrance backwards)
        us = frames_of(self.dur)
        old = clip.get("opacity", {}).get("keyframes")
        vals = [kf["value"] for kf in old] if old and len(old) == len(us) else [1.0] * len(us)
        clip["opacity"] = keys([(u, round(v * (1.0 if self.frame(u) >= at + 3 else 0.0), 4), "linear")
                                for u, v in zip(us, vals)])
        return clip

    # photos
    def pic(self, sample, rect, vis=None, shift=None, label="Tu foto", name="Foto", line=2.0, op=None):
        """A photo slot in rect (reference px) with a thin black frame; vis(fr, u) = the rect it shows in,
        shift(fr, u) = (dx, dy) moves the picture (reference px)."""
        t = self.t
        x0, y0, x1, y1 = self.rect_(rect)
        box = Box(x0, y0, x1 - x0, y1 - y0)
        track = t.track("video", name)
        motion = None
        us = frames_of(self.dur)
        if shift:
            motion = [(u, {"dx": shift(self.frame(u), u)[0] * self.sc, "dy": shift(self.frame(u), u)[1] * self.sc},
                       "linear") for u in us]
        clip = t.photo(track, sample, 0.0, self.dur, box, motion, label=label)
        if vis:
            mk = {"x": [], "y": [], "w": [], "h": []}
            for u in us:
                fr = self.frame(u)
                a, b, c, d = self.rect_(vis(fr, u))
                dx, dy = ((shift(fr, u)[0] * self.sc, shift(fr, u)[1] * self.sc) if shift else (0.0, 0.0))
                a, c = a - dx, c - dx
                b, d = b - dy, d - dy
                if c - a < 0.5 or d - b < 0.5:
                    a, b, c, d = -9000, -9000, -8999, -8999
                mk["x"].append((u, ((a + c) / 2 - box.x) / box.w, "linear"))
                mk["y"].append((u, ((b + d) / 2 - box.y) / box.h, "linear"))
                mk["w"].append((u, (c - a) / box.w, "linear"))
                mk["h"].append((u, (d - b) / box.h, "linear"))
            t.mask(track, clip, "rectangle", x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
                   keyframes={kk: keys(v) for kk, v in mk.items()})
        if op:
            clip["opacity"] = keys([(u, round(op(self.frame(u), u), 4), "linear") for u in us])
        if line and vis:
            self.box(f"{name} (borde)", self.line_l(INK, line), vis,
                     op=lambda fr, u: (1.0 if (lambda r: r[2] - r[0] > 1 and r[3] - r[1] > 1)(vis(fr, u)) else 0.0)
                     * (op(fr, u) if op else 1.0))
        elif line:
            def br(fr, u):
                dx, dy = shift(fr, u) if shift else (0.0, 0.0)
                return rect[0] + dx, rect[1] + dy, rect[2] + dx, rect[3] + dy
            self.box(f"{name} (borde)", self.line_l(INK, line), br, op=op)
        return clip

    def avatar(self, sample, cx, cy, r, g=None, line=2.0, ring_colour=INK, label="Tu foto", name="Avatar"):
        """A round picture; g(fr, u) = (scale, op)."""
        t = self.t
        gg = g or (lambda fr, u: (1.0, 1.0))
        d = 2 * r * self.sc
        box = Box(self.X(cx) - d / 2, self.Y(cy) - d / 2, d, d)
        track = t.track("video", name)
        us = frames_of(self.dur)
        motion = [(u, {"s": max(1e-3, gg(self.frame(u), u)[0])}, "linear") for u in us]
        clip = t.photo(track, sample, 0.0, self.dur, box, motion, label=label)
        clip["opacity"] = keys([(u, round(max(0.0, min(1.0, gg(self.frame(u), u)[1] if gg(self.frame(u), u)[0] > 0.02
                                                          else 0.0)), 4), "linear") for u in us])
        t.mask(track, clip, "ellipse")
        if line:
            self.icon(f"{name} (aro)", [nofill(), stroke(ring_colour, line * self.sc)], cx, cy, 2 * r, 2 * r,
                      g=gg, kind="ellipse")
        return clip

    # cursor and click
    def cursor(self, pts, clicks=(), hand=False, size=None, name="Cursor"):
        """The pointer's tip through [(frame, x, y)] (real frames), fading in at the first and out at the last; a
        little press at each click frame."""
        w, h = size or ((26, 34) if hand else (24, 36))
        tip = HAND_TIP if hand else ARROW_TIP
        f_in, f_out = pts[0][0], pts[-1][0]

        def at(rf):
            if rf <= pts[0][0]:
                return pts[0][1], pts[0][2]
            for (a, xa, ya), (b, xb, yb) in zip(pts, pts[1:]):
                if rf <= b:
                    q = k(rf, a, b - a)
                    return xa + (xb - xa) * q, ya + (yb - ya) * q
            return pts[-1][1], pts[-1][2]

        def g(fr, u):
            rf = self.R(u)
            x, y = at(rf)
            sc = 1 - sum(0.12 * math.sin(math.pi * lin(rf, c - 2, 4)) for c in clicks)
            cw, ch = w * sc, h * sc
            op = k(rf, f_in, 3) * (1 - k(rf, f_out - 3, 3))
            return x + (0.5 - tip[0]) * cw, y + (0.5 - tip[1]) * ch, cw, ch, 0, op
        if hand:
            self.shp(name, [fill(WHITE), stroke(INK, 1.6 * self.sc, "center")], g, path=HAND, base=(w, h))
            self.shp(f"{name} (líneas)", [nofill(), stroke(INK, 1.2 * self.sc, "center")], g, path=HAND_LINES,
                     base=(w, h))
        else:
            self.shp(name, [fill(WHITE), stroke(INK, 1.8 * self.sc, "center")], g, path=ARROW, base=(w, h))

    def burst(self, x, y, c, r0=14, r1=26, ln=8, n=8, colour=INK, width=1.6, frames=6, name="Destello"):
        """Short lines that fly out of (x, y) at real frame c (a click)."""
        for i in range(n):
            a = 360 * i / n - 90

            def g(fr, u, a=a):
                q = lin(self.R(u), c, frames)
                r = r0 + (r1 - r0) * (1 - (1 - q) ** 2)
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                on = 1.0 if c <= self.R(u) < c + frames else 0.0
                return x + ca * r, y + sa * r, ln * (1 - 0.5 * q), width, a, on
            self.shp(f"{name} {i + 1}", solid(colour), g)

    def after(self, c):
        """op(fr, u): 1 from real frame c on (a state that switches on with a click)."""
        return lambda fr, u: 1.0 if self.R(u) >= c else 0.0

    def before(self, c):
        return lambda fr, u: 0.0 if self.R(u) >= c else 1.0


def span(f0, fe, h, speed=1.2, end=None):
    """Seconds from frame f0 to the end of the exit (the entrance backwards from fe, `speed` times faster)."""
    return round(((h - f0) + (fe - f0) / speed + 1) / SRC, 2) if end is None else round((end - f0) / SRC, 2)


def _p(id, es, en, order, dur, section="elementos", tags=(), thumb=None):
    return wide(f"yp13-{id}", es, en, "ytkit", dur, order=order, tags=[f"kit:{section}", "youtube"] + list(tags),
                thumb_at=round(thumb if thumb is not None else dur * 0.6, 1))


# --- shared builders -----------------------------------------------------------------------------------------------
def unfold(s, rect, at, n, way="w", name="Tarjeta", layers=None, radius=0.0):
    """The cartoon card: it grows out of a thin strip at its left edge (way "w") or its bottom edge (way "h")."""
    x0, y0, x1, y1 = rect

    def r(fr, u):
        q = k(fr, at, n)
        if way == "w":
            return x0, y0, x0 + 12 + (x1 - x0 - 12) * q, y1
        if way == "c":
            cx, w = (x0 + x1) / 2, (x1 - x0) * (0.04 + 0.96 * q)
            return cx - w / 2, y0, cx + w / 2, y1
        return x0, y1 - 12 - (y1 - y0 - 12) * q, x1, y1
    return s.box(name, layers or s.card_l(), r, op=lambda fr, u: 1.0 if fr >= at else 0.0, radius=radius)


def badge(s, cx, cy, d, g, colour=BLUE, name="Verificado"):
    """A round badge with a white check (verified)."""
    s.icon(name, solid(colour), cx, cy, d, d, g=g, kind="ellipse")
    s.icon(f"{name} (marca)", [nofill(), stroke(WHITE, d * 0.14 * s.sc, "center")], cx, cy, d * 0.55, d * 0.55, g=g,
           path=CHECK)


def pop_g(at, n=6, over=0.18):
    return lambda fr, u: (pop(fr, at, n, over), 1.0)


def fade_g(at, n=4):
    return lambda fr, u: (1.0, k(fr, at, n))


def outline_icon(s, name, path, cx, cy, w, h, g=None, colour=INK, width=2.0, filled=None):
    layers = [fill(filled) if filled else nofill(), stroke(colour, width * s.sc, "center")]
    return s.icon(name, layers, cx, cy, w, h, g=g, path=path)


def toggled_icon(s, name, path, cx, cy, w, h, appear, click, on_colour=RED, width=2.0, burst=True):
    """An outline icon that turns into a solid `on_colour` one (with a pop and a burst) at real frame click."""
    off = s.before(click)
    outline_icon(s, name, path, cx, cy, w, h,
                 g=lambda fr, u: (pop(fr, appear, 5), off(fr, u)), width=width)

    def g_on(fr, u):
        q = lin(s.R(u), click, 6)
        bump = 1 + 0.3 * math.sin(math.pi * q) if q < 1 else 1.0
        return pop(fr, appear, 5) * bump, s.after(click)(fr, u)
    s.icon(f"{name} (activo)", [fill(on_colour), stroke(on_colour, width * s.sc * 0.6, "center")], cx, cy, w, h,
           g=g_on, path=path)
    if burst:
        s.burst(cx, cy, click, r0=w * 0.7, r1=w * 1.2, ln=w * 0.35)


def swap_text(s, a, b, ink, click, weight=500, colour=INK, colour_b=None, name="Número", align="left",
              appear=None):
    """Text a that becomes text b at real frame click (counts: 24 → 25)."""
    ap = appear if appear is not None else s.f0
    s.txt(a, ink, weight, colour, name, align=align,
          op=lambda fr, u: k(fr, ap, 4) * s.before(click)(fr, u))
    s.txt(b, ink, weight, colour_b or colour, f"{name} (nuevo)", align=align,
          op=lambda fr, u: k(fr, ap, 4) * s.after(click)(fr, u))


# =============================================================================================================
# GRID 1 (17.9-21.2 s): post cards
# =============================================================================================================
def post_charles():
    """TL 447-530: a tweet card: avatar, CHARLES @CHARLES, photo, comment/retweet/heart/share; a click likes it."""
    f0, fe, h = 446, 460, 518
    t = _p("post-tuit", "Publicación tipo tuit con me gusta", "Tweet-style post with a like", 18000,
           span(f0, fe, h), "redes", ["publicación", "me gusta", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "tl")
    unfold(s, (307, 130, 722, 417), f0, 11, "w")
    s.avatar("fx-woman-07", 349, 174, 27, g=pop_g(449, 5))
    s.txt("CHARLES @CHARLES", (392, 149, 654, 167), 800, slide=(451, 7, 60), name="Nombre")
    s.txt("Reminder for Twitter", (390, 174, 567, 188), 500, slide=(453, 7, 60), name="Texto")
    s.txt("#party", (571, 174, 628, 188), 500, BLUE, slide=(455, 6, 40), name="Etiqueta")
    s.pic("fx-woman-07", (394, 201, 705, 371), vis=lambda fr, u: (394 + 260 * (1 - k(fr, 451, 7)), 201,
                                                               705 + 60 * (1 - k(fr, 451, 7)), 371),
          shift=lambda fr, u: (60 * (1 - k(fr, 451, 7)), 0), op=lambda fr, u: 1.0 if fr >= 451 else 0.0)
    outline_icon(s, "Comentar", BUBBLE, 404, 393, 20, 19, g=pop_g(452, 5))
    s.txt("5", (420, 387, 431, 399), 500, op=lambda fr, u: k(fr, 455, 3), name="Comentarios")
    outline_icon(s, "Compartir de nuevo", RETWEET, 484, 393, 24, 19, g=pop_g(453, 5))
    s.txt("3", (500, 387, 510, 399), 500, op=lambda fr, u: k(fr, 456, 3), name="Reenvíos")
    toggled_icon(s, "Me gusta", HEART, 564, 393, 21, 19, 454, 478)
    swap_text(s, "24", "25", (578, 387, 598, 399), 478, colour_b=RED, appear=456, name="Me gusta (número)")
    outline_icon(s, "Compartir", SHARE, 652, 393, 19, 18, g=pop_g(455, 5))
    s.txt("1", (665, 387, 671, 399), 500, op=lambda fr, u: k(fr, 457, 3), name="Compartidos")
    s.cursor([(459, 700, 440), (467, 575, 403), (478, 570, 400), (486, 572, 404), (494, 600, 450)], clicks=(478,))
    return t


def post_jason():
    """TR 452-525: an Instagram-style post; a hand clicks the heart (201 → 202)."""
    f0, fe, h = 451, 466, 515
    t = _p("post-insta", "Publicación con foto grande y me gusta", "Photo post with a like", 18001,
           span(f0, fe, h), "redes", ["publicación", "me gusta", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "tr")
    unfold(s, (1236, 118, 1571, 433), f0, 9, "h")
    s.pic("fx-man-04", (1236, 197, 1571, 383),
          vis=lambda fr, u: (1236 - 30 * (1 - k(fr, 454, 8)), 197, 1236 - 30 * (1 - k(fr, 454, 8)) + 335 * k(fr, 454, 8),
                             383), shift=lambda fr, u: (-30 * (1 - k(fr, 454, 8)), 0), line=2.0)
    s.avatar("fx-man-04", 1276, 157, 23, g=pop_g(458, 5))
    s.txt("JASON DAVIS", (1314, 136, 1481, 155), 800, slide=(460, 7, 50), name="Nombre")
    badge(s, 1503, 145, 13, pop_g(465, 4), BLUE)
    s.txt("A good day on Instagram", (1316, 164, 1531, 179), 500, slide=(459, 7, 50))
    toggled_icon(s, "Me gusta", HEART, 1262, 408, 22, 20, 457, 484)
    outline_icon(s, "Comentar", BUBBLE, 1297, 408, 20, 20, g=pop_g(458, 5))
    outline_icon(s, "Enviar", PLANE, 1334, 408, 21, 19, g=pop_g(459, 5))
    s.txt("Likes:", (1471, 400, 1520, 415), 500, op=lambda fr, u: k(fr, 460, 4), name="Me gusta")
    swap_text(s, "201", "202", (1527, 400, 1556, 415), 484, appear=461, name="Me gusta (número)")
    s.cursor([(465, 1290, 450), (475, 1262, 414), (484, 1262, 412), (490, 1263, 416), (497, 1268, 455)],
             clicks=(484,), hand=True)
    return t


def post_lisa():
    """BL 455-530: a vertical (TikTok-style) post with the like, comment and share column; a hand likes it."""
    f0, fe, h = 454, 470, 517
    t = _p("post-vertical", "Publicación vertical con me gusta", "Vertical post with a like", 18002,
           span(f0, fe, h), "redes", ["publicación", "me gusta", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "bl")
    unfold(s, (348, 606, 668, 973), f0, 10, "h")
    s.pic("fx-woman-04", (436, 677, 597, 958),
          vis=lambda fr, u: (lambda q: (516 - 80 * q, 817 - 140 * (0.3 + 0.7 * q), 516 + 80 * q,
                                        817 + 140 * (0.3 + 0.7 * q)))(k(fr, 459, 6)),
          op=lambda fr, u: 1.0 if fr >= 459 else 0.0)
    s.avatar("fx-woman-04", 391, 650, 27, g=pop_g(464, 5))
    s.txt("LISA", (434, 625, 489, 643), 800, slide=(466, 6, 40), name="Nombre")
    badge(s, 505, 633, 13, pop_g(468, 4), BLUE)
    s.txt("Luishow", (520, 627, 591, 642), 500, slide=(467, 6, 40), name="Usuario")
    s.txt("Fame begins on TikTok", (434, 650, 630, 665), 500, slide=(464, 7, 50))
    for i, (cy, path, num, ny) in enumerate(((806, HEART, None, 778), (874, BUBBLE, "5", 846),
                                             (942, ARROWR, "3", 914))):
        if i == 0:
            s.icon("Me gusta (fondo)", [fill(WHITE), stroke(INK, 2 * s.sc)], 628, cy, 32, 32,
                   g=pop_g(460, 5), kind="ellipse")
            s.icon("Me gusta (rojo)", [fill(RED), stroke(INK, 2 * s.sc)], 628, cy, 32, 32,
                   g=lambda fr, u: (pop(fr, 460, 5) * (1 + 0.25 * math.sin(math.pi * lin(s.R(u), 488, 6))),
                                    s.after(488)(fr, u)), kind="ellipse")
            s.icon("Me gusta", solid(INK), 628, cy, 16, 14, g=lambda fr, u: (pop(fr, 460, 5), s.before(488)(fr, u)),
                   path=HEART)
            s.icon("Me gusta (blanco)", solid(WHITE), 628, cy, 16, 14,
                   g=lambda fr, u: (pop(fr, 460, 5), s.after(488)(fr, u)), path=HEART)
            s.burst(628, cy, 486, r0=22, r1=34, ln=9)
            swap_text(s, "411", "412", (615, ny - 6, 641, ny + 7), 488, appear=463, align="center",
                      name="Me gusta (número)")
        else:
            s.icon(f"Botón {i + 1}", [fill(WHITE), stroke(INK, 2 * s.sc)], 628, cy, 32, 32, g=pop_g(460 + i, 5),
                   kind="ellipse")
            s.icon(f"Botón {i + 1} (icono)", solid(INK), 628, cy, 14, 14, g=pop_g(461 + i, 5), path=path)
            s.txt(num, (623, ny - 6, 633, ny + 7), 500, align="center", op=lambda fr, u, i=i: k(fr, 463 + i, 3),
                  name=f"Número {i + 1}")
    s.cursor([(467, 720, 840), (477, 632, 812), (487, 630, 808), (493, 633, 812), (500, 660, 860)], clicks=(487,),
             hand=True)
    return t


def post_rockystar():
    """BR 460-530: a video post with title, channel and SUBSCRIBE; the arrow clicks it into SUBSCRIBED."""
    f0, fe, h = 459, 477, 517
    t = _p("post-video-suscribir", "Video publicado con botón suscribirse", "Video post with a subscribe button",
           18003, span(f0, fe, h), "redes", ["publicación", "suscribirse", "cursor"], thumb=2.6)
    s = Q(t, f0, fe, h, "br")
    unfold(s, (1196, 612, 1596, 940), f0, 10, "h")
    s.pic("fx-man-02", (1196, 612, 1596, 836),
          vis=lambda fr, u: (1196, 836 - 224 * k(fr, 463, 9), 1596, 836), op=lambda fr, u: 1.0 if fr >= 463 else 0.0)
    s.txt("How to make a top video on YouTube", (1211, 849, 1527, 862), 500, slide=(466, 8, 60), name="Título")
    s.avatar("fx-man-02", 1236, 899, 23, g=pop_g(462, 5))
    s.txt("ROCKYSTAR", (1275, 889, 1423, 908), 800, slide=(463, 7, 50), name="Canal")
    badge(s, 1438, 900, 13, pop_g(468, 4), INK)
    btn = (1460, 884, 1580, 915)

    def bg(fr, u):
        q = k(fr, 464, 6)
        p = 1 - 0.08 * math.sin(math.pi * lin(s.R(u), 486, 6))
        cx, cy = (btn[0] + btn[2]) / 2, (btn[1] + btn[3]) / 2
        return cx, cy, 120 * q * p, 31 * p, 0, 1.0 if q > 0.02 else 0.0
    s.shp("Botón", [fill(RED), stroke(INK, 2 * s.sc)], lambda fr, u: (lambda g: g[:5] + (g[5] * s.before(489)(fr, u),))(
        bg(fr, u)), base=(120, 31))
    s.shp("Botón (suscrito)", [fill(GREY), stroke(INK, 2 * s.sc)],
          lambda fr, u: (lambda g: g[:5] + (g[5] * s.after(489)(fr, u),))(bg(fr, u)), base=(120, 31))
    s.txt("SUBSCRIBE", (1480, 895, 1561, 905), 500, WHITE, "Suscribirse", align="left",
          op=lambda fr, u: k(fr, 468, 4) * s.before(489)(fr, u))
    s.txt("SUBSCRIBED", (1472, 895, 1567, 905), 500, "#3A3A3A", "Suscrito",
          op=lambda fr, u: s.after(489)(fr, u))
    s.cursor([(472, 1600, 950), (480, 1530, 905), (489, 1528, 902), (495, 1530, 906), (505, 1545, 945)],
             clicks=(489,))
    return t


# =============================================================================================================
# GRID 2 (21.4-24.6 s): post cards
# =============================================================================================================
def post_skatergirl():
    """TL 536-612: a tweet sharing a link card (photo + three lines); the arrow likes it (41 → 42)."""
    f0, fe, h = 536, 551, 598
    t = _p("post-tuit-enlace", "Tuit con enlace y me gusta", "Tweet with a link card and a like", 18004,
           span(f0, fe, h, 1.1), "redes", ["publicación", "me gusta", "cursor"], thumb=2.6)
    s = Q(t, f0, fe, h, "tl", 1.1)
    unfold(s, (292, 168, 756, 388), f0, 11, "w")
    s.avatar("fx-woman-03", 332, 212, 23, g=pop_g(539, 5))
    s.txt("SKATERGIRL @SKATERGIRL", (372, 191, 709, 209), 800, slide=(542, 7, 60), name="Nombre")
    s.txt("My new favorite twitter account", (371, 215, 640, 229), 500, slide=(544, 7, 60))
    s.box("Enlace", [fill(WHITE), stroke(INK, 2 * s.sc)],
          lambda fr, u: (lambda q: (372, 243, 468 + 272 * q, 341))(k(fr, 542, 8)),
          op=lambda fr, u: 1.0 if fr >= 541 else 0.0)
    s.pic("fx-woman-03", (372, 243, 468, 341), vis=lambda fr, u: (372, 243, 468, 341),
          shift=lambda fr, u: (90 * (1 - k(fr, 540, 7)), 0), op=lambda fr, u: 1.0 if fr >= 540 else 0.0)
    for i, (line, x1) in enumerate((("This popular place holds", 699), ("unique sentimental", 660),
                                    ("value to visitors", 623))):
        s.txt(line, (492, 263 + 20 * i, x1, 277 + 20 * i), 500, slide=(545 + i, 7, 40), name=f"Enlace {i + 1}")
    outline_icon(s, "Comentar", BUBBLE, 380, 363, 20, 19, g=pop_g(544, 5))
    s.txt("3", (398, 357, 408, 369), 500, op=lambda fr, u: k(fr, 547, 3), name="Comentarios")
    outline_icon(s, "Compartir de nuevo", RETWEET, 476, 363, 24, 19, g=pop_g(545, 5))
    s.txt("1", (494, 357, 499, 369), 500, op=lambda fr, u: k(fr, 548, 3), name="Reenvíos")
    toggled_icon(s, "Me gusta", HEART, 572, 363, 21, 19, 546, 568)
    swap_text(s, "41", "42", (588, 357, 610, 369), 568, colour_b=RED, appear=548, name="Me gusta (número)")
    outline_icon(s, "Compartir", SHARE, 667, 363, 19, 18, g=pop_g(547, 5))
    s.txt("5", (684, 357, 694, 369), 500, op=lambda fr, u: k(fr, 549, 3), name="Compartidos")
    s.cursor([(550, 620, 420), (560, 578, 372), (568, 573, 366), (576, 576, 370), (586, 600, 430)], clicks=(568,))
    return t


def post_lillie():
    """TR 539-616: a Facebook-style post (name, date, text, photo, Like · Comment · Share); a hand clicks Like."""
    f0, fe, h = 539, 553, 601
    t = _p("post-muro", "Publicación de muro con Me gusta", "Wall post with Like, Comment and Share", 18005,
           span(f0, fe, h, 1.1), "redes", ["publicación", "me gusta", "cursor"], thumb=2.6)
    s = Q(t, f0, fe, h, "tr", 1.1)
    unfold(s, (1230, 114, 1582, 444), f0, 6, "h")
    s.pic("fx-woman-06", (1230, 209, 1582, 394),
          vis=lambda fr, u: (lambda q: (1230 - 30 * (1 - q), 209, 1230 - 30 * (1 - q) + 352 * q, 394))(k(fr, 544, 8)),
          shift=lambda fr, u: (-30 * (1 - k(fr, 544, 8)), 0),
          op=lambda fr, u: 1.0 if fr >= 544 else 0.0)
    s.avatar("fx-woman-06", 1266, 149, 20, g=pop_g(542, 5))
    s.txt("LILLIE BROOKS", (1300, 129, 1487, 147), 800, slide=(543, 7, 50), name="Nombre")
    badge(s, 1502, 139, 13, pop_g(549, 4), BLUE)
    s.txt("7 June at 12:40", (1301, 157, 1425, 171), 500, slide=(545, 6, 40), name="Fecha")
    s.txt("Facebook for Fashion workshop", (1246, 180, 1517, 194), 500, slide=(546, 7, 50))
    toggled_icon(s, "Me gusta", THUMB, 1266, 420, 19, 19, 549, 572, on_colour=BLUE)
    s.txt("Like", (1285, 414, 1316, 428), 500, op=lambda fr, u: k(fr, 550, 3) * s.before(572)(fr, u),
          name="Me gusta")
    s.txt("Like", (1285, 414, 1316, 428), 500, BLUE, "Me gusta (activo)",
          op=lambda fr, u: k(fr, 550, 3) * s.after(572)(fr, u))
    outline_icon(s, "Comentar", SQBUB, 1348, 420, 22, 20, g=pop_g(550, 5))
    s.txt("Comment", (1368, 414, 1454, 428), 500, op=lambda fr, u: k(fr, 551, 3), name="Comentar (texto)")
    outline_icon(s, "Compartir", ARROWR, 1486, 420, 22, 18, g=pop_g(551, 5))
    s.txt("Share", (1506, 414, 1555, 428), 500, op=lambda fr, u: k(fr, 552, 3), name="Compartir (texto)")
    s.cursor([(552, 1300, 470), (562, 1270, 428), (572, 1268, 424), (580, 1270, 428), (590, 1285, 475)],
             clicks=(572,), hand=True)
    return t


def post_jasmine():
    """BL 544-620: a post with a blue name, date, text and a wide photo; a hand likes it (81 → 82)."""
    f0, fe, h = 544, 558, 604
    t = _p("post-noticia", "Publicación con nombre azul y me gusta", "Post with a blue name and a like", 18006,
           span(f0, fe, h, 1.1), "redes", ["publicación", "me gusta", "cursor"], thumb=2.6)
    s = Q(t, f0, fe, h, "bl", 1.1)
    unfold(s, (336, 632, 704, 940), f0, 10, "w")
    s.pic("ig3-headphones-01", (336, 735, 704, 888),
          vis=lambda fr, u: (336 + 220 * (1 - k(fr, 547, 7)), 735, 704, 888),
          shift=lambda fr, u: (90 * (1 - k(fr, 547, 7)), 0), op=lambda fr, u: 1.0 if fr >= 547 else 0.0)
    s.avatar("ig3-headphones-01", 376, 671, 23, g=pop_g(547, 5))
    s.txt("JASMINE REED", (416, 651, 600, 669), 800, BLUE, slide=(549, 7, 50), name="Nombre")
    s.txt("29 jun 11:10", (416, 677, 506, 691), 500, slide=(551, 6, 40), name="Fecha")
    s.txt("Top 3 news sources for fashion lovers", (352, 708, 665, 722), 500, slide=(552, 7, 60))
    toggled_icon(s, "Me gusta", HEART, 362, 914, 20, 18, 551, 577)
    swap_text(s, "81", "82", (381, 908, 399, 921), 577, colour_b=RED, appear=553, name="Me gusta (número)")
    outline_icon(s, "Comentar", SQBUB, 435, 914, 21, 19, g=pop_g(552, 5))
    s.txt("5", (456, 908, 464, 921), 500, op=lambda fr, u: k(fr, 554, 3), name="Comentarios")
    outline_icon(s, "Compartir", ARROWR, 498, 914, 22, 18, g=pop_g(553, 5))
    s.txt("2", (518, 908, 528, 921), 500, op=lambda fr, u: k(fr, 555, 3), name="Compartidos")
    s.cursor([(557, 390, 965), (567, 366, 922), (577, 364, 918), (585, 366, 922), (595, 380, 965)],
             clicks=(577,), hand=True)
    return t


def post_beatrice():
    """BR 549-622: a video post with likes and dislikes; the arrow likes it (81 → 82)."""
    f0, fe, h = 549, 565, 606
    t = _p("post-video-votos", "Video publicado con me gusta y no me gusta", "Video post with like and dislike",
           18007, span(f0, fe, h, 1.1), "redes", ["publicación", "me gusta", "cursor"], thumb=2.6)
    s = Q(t, f0, fe, h, "br", 1.1)
    unfold(s, (1200, 615, 1600, 940), f0, 9, "h")
    s.pic("ig3-sunglasses-01", (1200, 615, 1600, 837),
          vis=lambda fr, u: (1200, 837 - 222 * k(fr, 553, 9), 1600, 837), op=lambda fr, u: 1.0 if fr >= 553 else 0.0)
    s.txt("The most original video on YouTube", (1215, 850, 1520, 864), 500, slide=(556, 8, 60), name="Título")
    s.avatar("ig3-sunglasses-01", 1240, 902, 23, g=pop_g(551, 5))
    s.txt("BEATRICE", (1279, 892, 1401, 910), 800, slide=(553, 7, 50), name="Canal")
    badge(s, 1417, 902, 13, pop_g(558, 4), INK)
    toggled_icon(s, "Me gusta", THUMB, 1488, 900, 19, 19, 556, 580, on_colour=INK)
    swap_text(s, "81", "82", (1505, 894, 1521, 907), 580, appear=558, name="Me gusta (número)")
    outline_icon(s, "No me gusta", THUMB_DOWN, 1550, 902, 19, 19, g=pop_g(557, 5))
    s.txt("5", (1567, 894, 1576, 907), 500, op=lambda fr, u: k(fr, 559, 3), name="No me gusta (número)")
    s.cursor([(564, 1600, 960), (572, 1500, 915), (580, 1492, 908), (587, 1495, 912), (596, 1520, 960)],
             clicks=(580,))
    return t


# =============================================================================================================
# GRID 3 (24.6-28.4 s): post cards
# =============================================================================================================
def press(s, c, amount=0.08):
    """A button's scale around a click at real frame c."""
    return lambda u: 1 - amount * math.sin(math.pi * lin(s.R(u), c - 3, 6))


def button(s, rect, word_a, word_b, ink_a, ink_b, appear, click, col_a=RED, col_b=GREY, txt_a=WHITE,
           txt_b="#3A3A3A", weight=500, name="Botón", grow=True, radius=0.0):
    """A flat outlined button that widens in at frame appear and swaps colour and word at real frame click."""
    x0, y0, x1, y1 = rect
    cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    pr = press(s, click) if click else (lambda u: 1.0)

    def g(fr, u, after):
        q = k(fr, appear, 6) if grow else 1.0
        on = 1.0 if click is None else (s.after(click) if after else s.before(click))(fr, u)
        return cx, cy, w * q * pr(u), h * pr(u), 0, (1.0 if q > 0.02 and fr >= appear else 0.0) * on
    s.shp(name, [fill(col_a), stroke(INK, 2 * s.sc)], lambda fr, u: g(fr, u, False), base=(w, h), radius=radius)
    s.txt(word_a, ink_a, weight, txt_a, f"{name} (texto)", op=lambda fr, u: k(fr, appear + 3, 4) * (
        s.before(click)(fr, u) if click else 1.0))
    if click:
        s.shp(f"{name} (activo)", [fill(col_b), stroke(INK, 2 * s.sc)], lambda fr, u: g(fr, u, True), base=(w, h),
              radius=radius)
        s.txt(word_b, ink_b, weight, txt_b, f"{name} (texto activo)", op=s.after(click))


def post_pearl():
    """TL 619-700: a video post: title, channel, SUBSCRIBE and a bell; the arrow subscribes, then rings the bell."""
    f0, fe, h = 619, 637, 704
    t = _p("post-video-campana", "Video publicado: suscribirse y campana", "Video post: subscribe and bell", 18008,
           span(f0, fe, h, 1.1), "redes", ["publicación", "suscribirse", "campana", "cursor"], thumb=2.6)
    s = Q(t, f0, fe, h, "tl", 1.1)
    unfold(s, (318, 112, 718, 440), f0, 10, "h")
    s.pic("h-portrait-05", (318, 112, 718, 336),
          vis=lambda fr, u: (318, 112, 718, 112 + 224 * k(fr, 626, 9)), op=lambda fr, u: 1.0 if fr >= 626 else 0.0)
    s.txt("5 Easy ways to get to Success on YouTube", (333, 349, 687, 362), 500, slide=(628, 8, 60), name="Título")
    s.avatar("h-portrait-05", 357, 400, 23, g=pop_g(622, 5))
    s.txt("PEARL", (397, 391, 478, 409), 800, slide=(624, 7, 40), name="Canal")
    badge(s, 493, 400, 13, pop_g(630, 4), INK)
    button(s, (537, 384, 658, 415), "SUBSCRIBE", "SUBSCRIBED", (559, 395, 637, 405), (550, 395, 645, 405), 624, 652)
    outline_icon(s, "Campana", BELL, 684, 399, 20, 24, g=lambda fr, u: (pop(fr, 626, 5), s.before(674)(fr, u)))

    def ring(fr, u):
        rf = s.R(u)
        wob = 18 * math.sin(2 * math.pi * (rf - 674) / 6) * math.exp(-(rf - 674) / 8) if rf >= 674 else 0.0
        return pop(fr, 626, 5), s.after(674)(fr, u), 0, 0, wob
    s.icon("Campana (activa)", [fill(INK), stroke(INK, 1.5 * s.sc, "center")], 684, 399, 20, 24, g=ring, path=BELL)
    s.cursor([(637, 740, 470), (645, 600, 410), (652, 598, 402), (660, 620, 410), (668, 686, 406), (674, 684, 402),
              (682, 690, 410)], clicks=(652, 674))
    return t


def post_connie():
    """TR 621-704: a profile with followers, FOLLOW and six photos; a hand follows (7319 → 7320)."""
    f0, fe, h = 621, 640, 708
    t = _p("perfil-seguir", "Perfil con fotos y botón seguir", "Profile with photos and a follow button", 18009,
           span(f0, fe, h, 1.1), "redes", ["perfil", "seguir", "cursor", "fotos"], thumb=2.6)
    s = Q(t, f0, fe, h, "tr", 1.1)
    unfold(s, (1278, 106, 1542, 473), f0, 9, "h")
    samples = ("fx-woman-04", "ig3-headphones-01", "fx-woman-07", "fx-woman-05", "fx-woman-06", "fx-woman-08")
    for i, smp in enumerate(samples):
        x0, y0 = 1278 + 88 * (i % 3), 266 + 88 * (i // 3)
        at = 627 + 2 * i
        s.pic(smp, (x0, y0, x0 + 88, y0 + 88), name=f"Foto {i + 1}",
              vis=lambda fr, u, x0=x0, y0=y0, at=at: (x0, y0 + 88 * (1 - k(fr, at, 6)), x0 + 88, y0 + 88),
              op=lambda fr, u, at=at: 1.0 if fr >= at else 0.0, label=f"Foto {i + 1}")
    s.avatar("fx-woman-07", 1325, 162, 31, g=pop_g(626, 5), name="Foto de perfil", label="Tu foto de perfil")
    s.txt("Followers:", (1389, 133, 1474, 147), 500, op=lambda fr, u: k(fr, 630, 4), name="Seguidores")
    swap_text(s, "7319", "7320", (1481, 133, 1519, 147), 653, appear=630, name="Seguidores (número)")
    button(s, (1390, 162, 1510, 194), "FOLLOW", "FOLLOWING", (1421, 173, 1480, 183), (1405, 173, 1495, 183), 630, 653,
           col_a=BLUE)
    s.txt("CONNIE", (1293, 212, 1390, 230), 800, slide=(631, 7, 40), name="Nombre")
    badge(s, 1406, 220, 14, pop_g(636, 4), BLUE)
    s.txt("instagramfashion.com", (1293, 238, 1484, 252), 500, slide=(633, 7, 50), name="Web")
    s.cursor([(638, 1560, 260), (646, 1462, 190), (653, 1458, 186), (660, 1462, 190), (672, 1540, 240)],
             clicks=(653,), hand=True)
    return t


def pill_icon(s, name, rect, path, num_a, num_b, appear, click=None, iw=19, ih=17):
    """A rounded pill with an outline icon and a number; a click fills it red (number white, plus one)."""
    x0, y0, x1, y1 = rect
    cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    pr = press(s, click, 0.12) if click else (lambda u: 1.0)
    s.icon(name, [fill(WHITE), stroke(INK, 2 * s.sc)], cx, cy, w, h, g=lambda fr, u: (pop(fr, appear, 5) * pr(u), 1.0),
           radius=h / 2)
    if click:
        s.icon(f"{name} (activo)", [fill(RED), stroke(RED, 2 * s.sc)], cx, cy, w, h,
               g=lambda fr, u: (pop(fr, appear, 5) * pr(u), s.after(click)(fr, u)), radius=h / 2)
    ix = x0 + 20
    outline_icon(s, f"{name} (icono)", path, ix, cy, iw, ih,
                 g=lambda fr, u: (pop(fr, appear + 1, 5), s.before(click)(fr, u) if click else 1.0))
    if click:
        s.icon(f"{name} (icono activo)", [fill(WHITE), stroke(WHITE, 1.2 * s.sc, "center")], ix, cy, iw, ih,
               g=lambda fr, u: (pop(fr, appear + 1, 5) * (1 + 0.3 * math.sin(math.pi * lin(s.R(u), click, 6))),
                                s.after(click)(fr, u)), path=path)
        s.burst(cx, cy, click, r0=w * 0.55, r1=w * 0.85, ln=8)
        s.txt(num_a, (x0 + 34, cy - 7, x0 + 34 + 9 * len(num_a), cy + 7), 500,
              op=lambda fr, u: k(fr, appear + 3, 3) * s.before(click)(fr, u), name=f"{name} (número)")
        s.txt(num_b, (x0 + 34, cy - 7, x0 + 34 + 9 * len(num_b), cy + 7), 500, WHITE,
              op=lambda fr, u: k(fr, appear + 3, 3) * s.after(click)(fr, u), name=f"{name} (número nuevo)")
    else:
        s.txt(num_a, (x0 + 38, cy - 7, x0 + 38 + 9 * len(num_a), cy + 7), 500,
              op=lambda fr, u: k(fr, appear + 3, 3), name=f"{name} (número)")


def post_richard():
    """BL 629-708: a post with a blue name, photo and three pill buttons; a hand likes it (19 → 20, red pill)."""
    f0, fe, h = 629, 644, 711
    t = _p("post-botones", "Publicación con botones redondeados", "Post with rounded buttons", 18010,
           span(f0, fe, h, 1.1), "redes", ["publicación", "me gusta", "cursor"], thumb=2.6)
    s = Q(t, f0, fe, h, "bl", 1.1)
    unfold(s, (340, 628, 708, 947), f0, 9, "w")
    s.pic("fx-man-05", (340, 731, 708, 885), vis=lambda fr, u: (340 + 220 * (1 - k(fr, 632, 7)), 731, 708, 885),
          shift=lambda fr, u: (90 * (1 - k(fr, 632, 7)), 0), op=lambda fr, u: 1.0 if fr >= 632 else 0.0)
    s.avatar("fx-man-05", 379, 668, 23, g=pop_g(633, 5))
    s.txt("RICHARD BOWMAN", (419, 646, 663, 665), 800, BLUE, slide=(633, 7, 60), name="Nombre")
    s.txt("03 sep 14:20", (420, 673, 521, 687), 500, slide=(635, 6, 40), name="Fecha")
    s.txt("Music is the strongest form of magic!", (356, 704, 672, 719), 500, slide=(636, 7, 60))
    pill_icon(s, "Me gusta", (356, 901, 416, 931), HEART, "19", "20", 636, 663, iw=17, ih=15)
    pill_icon(s, "Comentar", (430, 901, 491, 931), SQBUB, "4", "4", 637)
    pill_icon(s, "Compartir", (503, 901, 564, 931), ARROWR, "6", "6", 638)
    s.cursor([(645, 400, 975), (655, 378, 925), (663, 376, 918), (670, 378, 922), (684, 395, 975)], clicks=(663,),
             hand=True)
    return t


def post_frank():
    """BR 631-710: a tweet with a link card (photo, two lines); the arrow likes it (36 → 37)."""
    f0, fe, h = 631, 646, 713
    t = _p("post-tuit-foto", "Tuit con foto enlazada y me gusta", "Tweet with a linked photo and a like", 18011,
           span(f0, fe, h, 1.1), "redes", ["publicación", "me gusta", "cursor"], thumb=2.6)
    s = Q(t, f0, fe, h, "br", 1.1)
    unfold(s, (1185, 624, 1600, 945), f0, 10, "w")
    s.box("Enlace", [fill(WHITE), stroke(INK, 2 * s.sc)], lambda fr, u: (1281, 703, 1281 + 302 * k(fr, 636, 8), 895),
          op=lambda fr, u: 1.0 if fr >= 636 else 0.0)
    s.pic("fx-man-03", (1281, 703, 1583, 833), vis=lambda fr, u: (1281, 703, 1281 + 302 * k(fr, 637, 8), 833),
          op=lambda fr, u: 1.0 if fr >= 637 else 0.0)
    s.avatar("fx-man-03", 1231, 672, 31, g=pop_g(634, 5))
    s.txt("FRANK @FRANK", (1280, 651, 1482, 669), 800, slide=(636, 7, 50), name="Nombre")
    s.txt("· 15m", (1492, 655, 1533, 669), 500, op=lambda fr, u: k(fr, 640, 4), name="Hora")
    s.txt("Epitome of italian", (1279, 677, 1429, 691), 500, slide=(638, 7, 50))
    s.txt("#style", (1434, 677, 1485, 691), 500, BLUE, slide=(640, 6, 30), name="Etiqueta")
    s.txt("Melvin Johnson: It's his world!", (1295, 848, 1547, 862), 500, slide=(641, 7, 50), name="Enlace 1")
    s.txt("fashionontwitter.com", (1295, 868, 1477, 882), 500, slide=(642, 7, 50), name="Enlace 2")
    outline_icon(s, "Comentar", BUBBLE, 1290, 919, 21, 19, g=pop_g(640, 5))
    s.txt("5", (1308, 913, 1318, 926), 500, op=lambda fr, u: k(fr, 643, 3), name="Comentarios")
    outline_icon(s, "Compartir de nuevo", RETWEET, 1370, 919, 24, 19, g=pop_g(641, 5))
    s.txt("9", (1388, 913, 1398, 926), 500, op=lambda fr, u: k(fr, 644, 3), name="Reenvíos")
    toggled_icon(s, "Me gusta", HEART, 1450, 919, 21, 19, 642, 664)
    swap_text(s, "37", "38", (1469, 913, 1488, 926), 664, colour_b=RED, appear=644, name="Me gusta (número)")
    outline_icon(s, "Compartir", SHARE, 1530, 919, 19, 18, g=pop_g(643, 5))
    s.txt("1", (1547, 913, 1553, 926), 500, op=lambda fr, u: k(fr, 645, 3), name="Compartidos")
    s.cursor([(647, 1500, 980), (656, 1456, 930), (664, 1452, 924), (672, 1456, 930), (686, 1480, 980)],
             clicks=(664,))
    return t


# =============================================================================================================
# GRID 4 (28.9-32.2 s): text posts and comments
# =============================================================================================================
def post_seth():
    """TL 726-808: a text tweet (name, time, two lines); the arrow likes it (17 → 18)."""
    f0, fe, h = 726, 741, 797
    t = _p("tuit-texto", "Tuit de texto con me gusta", "Text tweet with a like", 18012, span(f0, fe, h, 1.1), "redes",
           ["publicación", "me gusta", "cursor", "comentario"], thumb=2.6)
    s = Q(t, f0, fe, h, "tl", 1.1)
    unfold(s, (307, 198, 722, 338), f0, 10, "w")
    s.avatar("h-portrait-02", 354, 245, 31, g=pop_g(729, 5))
    s.txt("SETH @SETH", (401, 221, 559, 239), 800, slide=(731, 7, 50), name="Nombre")
    s.txt("· 19M", (570, 226, 610, 239), 500, op=lambda fr, u: k(fr, 735, 4), name="Hora")
    s.txt("Plunge into changes, move with it,", (401, 251, 696, 265), 500, slide=(733, 7, 60), name="Texto 1")
    s.txt("and join the dance!", (401, 271, 565, 285), 500, slide=(734, 7, 50), name="Texto 2")
    outline_icon(s, "Comentar", SQBUB, 412, 310, 22, 20, g=pop_g(733, 5))
    s.txt("5", (430, 304, 440, 317), 500, op=lambda fr, u: k(fr, 736, 3), name="Comentarios")
    outline_icon(s, "Compartir de nuevo", RETWEET, 492, 310, 24, 19, g=pop_g(734, 5))
    s.txt("2", (510, 304, 520, 317), 500, op=lambda fr, u: k(fr, 737, 3), name="Reenvíos")
    toggled_icon(s, "Me gusta", HEART, 572, 310, 21, 19, 735, 758)
    swap_text(s, "17", "18", (590, 304, 607, 317), 758, colour_b=RED, appear=737, name="Me gusta (número)")
    outline_icon(s, "Compartir", SHARE, 652, 310, 19, 18, g=pop_g(736, 5))
    s.txt("1", (669, 304, 675, 317), 500, op=lambda fr, u: k(fr, 738, 3), name="Compartidos")
    s.cursor([(742, 600, 380), (750, 576, 322), (758, 573, 315), (765, 576, 320), (778, 590, 380)], clicks=(758,))
    return t


def post_madeline():
    """TR 729-810: a text post with a blue name and date; a hand likes it (81 → 82)."""
    f0, fe, h = 729, 744, 799
    t = _p("post-texto", "Publicación de texto con me gusta", "Text post with a like", 18013, span(f0, fe, h, 1.1),
           "redes", ["publicación", "me gusta", "cursor"], thumb=2.6)
    s = Q(t, f0, fe, h, "tr", 1.1)
    unfold(s, (1210, 192, 1578, 355), f0, 10, "w")
    s.avatar("h-portrait-06", 1250, 232, 23, g=pop_g(732, 5))
    s.txt("MADELINE CLARK", (1289, 214, 1511, 232), 800, BLUE, slide=(734, 7, 60), name="Nombre")
    s.txt("2  aug 18:45", (1290, 244, 1388, 258), 500, slide=(736, 6, 40), name="Fecha")
    s.txt("Dwell on the beauty of life. Watch the", (1226, 272, 1545, 286), 500, slide=(737, 7, 60), name="Texto 1")
    s.txt("stars, see yourself running with them", (1226, 292, 1542, 306), 500, slide=(738, 7, 60), name="Texto 2")
    toggled_icon(s, "Me gusta", HEART, 1237, 329, 20, 18, 738, 761)
    swap_text(s, "81", "82", (1253, 323, 1273, 336), 761, colour_b=RED, appear=740, name="Me gusta (número)")
    outline_icon(s, "Comentar", SQBUB, 1301, 329, 22, 20, g=pop_g(739, 5))
    s.txt("3", (1320, 323, 1330, 336), 500, op=lambda fr, u: k(fr, 741, 3), name="Comentarios")
    outline_icon(s, "Compartir", ARROWR, 1358, 329, 23, 19, g=pop_g(740, 5))
    s.txt("7", (1378, 323, 1388, 336), 500, op=lambda fr, u: k(fr, 742, 3), name="Compartidos")
    s.cursor([(745, 1270, 400), (753, 1240, 340), (761, 1238, 335), (768, 1240, 340), (782, 1255, 400)],
             clicks=(761,), hand=True)
    return t


def comment_irea():
    """BL 736-814: a comment beside its avatar (name, Follow, three lines, LIKE · REPLY); a hand clicks LIKE."""
    f0, fe, h = 736, 751, 802
    t = _p("comentario-like", "Comentario con LIKE y REPLY", "Comment with LIKE and REPLY", 18014,
           span(f0, fe, h, 1.1), "redes", ["comentario", "me gusta", "cursor"], thumb=2.6)
    s = Q(t, f0, fe, h, "bl", 1.1)
    s.avatar("ig3-sunglasses-01", 312, 741, 23, g=pop_g(f0, 5))
    unfold(s, (352, 718, 736, 862), f0 + 2, 10, "w")
    s.txt("IREA REED", (367, 734, 499, 752), 800, slide=(741, 7, 50), name="Nombre")
    badge(s, 513, 743, 13, pop_g(746, 4), BLUE)
    s.txt("Follow", (528, 738, 584, 752), 500, BLUE, op=lambda fr, u: k(fr, 747, 4), name="Seguir")
    for i, (line, x1) in enumerate((("OMG what an idea, I'm so going to try", 688),
                                    ("it, I've never seen this done before and", 694),
                                    ("makes so much sense, thank you!", 654))):
        s.txt(line, (367, 766 + 20 * i, x1, 780 + 20 * i), 500, slide=(743 + i, 7, 60), name=f"Comentario {i + 1}")
    s.txt("LIKE", (367, 835, 406, 846), 700, "#A9A9A9", op=lambda fr, u: k(fr, 747, 4) * s.before(766)(fr, u),
          name="Me gusta")
    s.txt("LIKE", (367, 835, 406, 846), 700, BLUE, "Me gusta (activo)",
          op=lambda fr, u: k(fr, 747, 4) * s.after(766)(fr, u))
    s.txt("REPLY", (418, 835, 474, 846), 700, "#A9A9A9", op=lambda fr, u: k(fr, 748, 4), name="Responder")
    s.cursor([(750, 410, 900), (758, 390, 852), (766, 387, 845), (773, 390, 850), (786, 410, 900)], clicks=(766,),
             hand=True)
    return t


def comment_jonathan():
    """BR 739-817: a comment (name, time, two lines, like · dislike · to Answer); the arrow likes it (384 → 385)."""
    f0, fe, h = 739, 754, 804
    t = _p("comentario-votos", "Comentario con me gusta y responder", "Comment with like and reply", 18015,
           span(f0, fe, h, 1.1), "redes", ["comentario", "me gusta", "cursor"], thumb=2.6)
    s = Q(t, f0, fe, h, "br", 1.1)
    unfold(s, (1147, 702, 1658, 830), f0, 10, "w")
    s.avatar("h-portrait-02", 1190, 746, 27, g=pop_g(742, 5))
    s.txt("JONATHAN", (1234, 716, 1372, 734), 800, slide=(744, 7, 50), name="Nombre")
    s.txt("3 days ago", (1386, 722, 1476, 736), 500, op=lambda fr, u: k(fr, 748, 4), name="Fecha")
    s.txt("Wow I didn't realise how many people liked the", (1234, 750, 1637, 764), 500, slide=(746, 7, 60),
          name="Comentario 1")
    s.txt("video, probably all his fans! I've never seen that", (1234, 770, 1632, 784), 500, slide=(747, 7, 60),
          name="Comentario 2")
    toggled_icon(s, "Me gusta", THUMB, 1244, 803, 19, 19, 748, 770, on_colour=BLUE)
    swap_text(s, "385", "386", (1262, 798, 1291, 811), 770, appear=750, name="Me gusta (número)")
    outline_icon(s, "No me gusta", THUMB_DOWN, 1323, 805, 19, 19, g=pop_g(749, 5))
    s.txt("1", (1342, 798, 1347, 811), 500, op=lambda fr, u: k(fr, 751, 3), name="No me gusta (número)")
    s.txt("to Answer", (1378, 799, 1463, 812), 500, op=lambda fr, u: k(fr, 751, 4), name="Responder")
    s.cursor([(753, 1290, 880), (762, 1250, 820), (770, 1246, 812), (777, 1250, 818), (790, 1275, 880)],
             clicks=(770,))
    return t


# =============================================================================================================
# GRID 5 (32.6-35.7 s): search bars
# =============================================================================================================
def field(s, rect, at, n=5, colour=WHITE, name="Campo", radius=6.0, drop=8.0, way="w"):
    return unfold(s, rect, at, n, way, name, s.card_l(colour, 3.0, drop), radius)


def search_loading():
    """TL 814-884: a search bar types a web address; the arrow clicks the magnifier and it turns grey, «loading...»."""
    f0, fe, h = 814, 830, 874
    t = _p("buscar-cargando", "Buscador que pasa a «cargando»", "Search bar that turns to loading", 18016,
           span(f0, fe, h, 1.1), "elementos", ["buscador", "cursor", "web"], thumb=2.2)
    s = Q(t, f0, fe, h, "tl", 1.1)
    r = (354, 250, 714, 310)
    field(s, r, f0, 5)
    s.box("Campo (cargando)", s.card_l(GREY, 3.0, 8.0), lambda fr, u: r, op=lambda fr, u: s.after(841)(fr, u),
          radius=6)
    c = s.txt("yourwebsite.com", (381, 270, 615, 292), 500, op=lambda fr, u: s.before(841)(fr, u), name="Dirección")
    s.typed(c, 817, stagger=0.05, duration=0.03)
    s.txt("loading...", (381, 270, 512, 292), 500, WHITE, "Cargando",
          op=lambda fr, u: k(s.R(u), 842, 3))
    outline_icon(s, "Lupa", SEARCH, 675, 278, 24, 24, g=pop_g(819, 5), colour=BLUE, width=3)
    s.burst(675, 278, 840, r0=26, r1=46, ln=10)
    s.cursor([(822, 760, 300), (832, 690, 290), (840, 678, 282), (848, 680, 288), (860, 700, 330)], clicks=(840,))
    return t


def search_button():
    """TR 816-887: a field types «video templates», a blue SEARCH button; a hand clicks it and both turn grey."""
    f0, fe, h = 816, 833, 877
    t = _p("buscar-boton", "Buscador con botón SEARCH", "Search field with a SEARCH button", 18017,
           span(f0, fe, h, 1.1), "elementos", ["buscador", "cursor", "botón"], thumb=2.2)
    s = Q(t, f0, fe, h, "tr", 1.1)
    field(s, (1126, 256, 1486, 316), f0, 5)
    c = s.txt("video templates", (1156, 275, 1392, 298), 500, op=lambda fr, u: s.before(845)(fr, u), name="Búsqueda")
    s.typed(c, 819, stagger=0.045, duration=0.03)
    s.txt("search templates", (1156, 275, 1400, 298), 500, "#B5B5B5", "Búsqueda (vacía)", op=s.after(846))
    pr = press(s, 845)

    def bg(fr, u, after):
        q = k(fr, 822, 5)
        on = (s.after(845) if after else s.before(845))(fr, u)
        return 1596, 286, 180 * q * pr(u), 60 * pr(u), 0, (1.0 if fr >= 822 else 0.0) * on
    s.shp("Botón", s.card_l(BLUE, 3.0, 8.0), lambda fr, u: bg(fr, u, False), base=(180, 60), radius=6)
    s.shp("Botón (gris)", s.card_l(GREY, 3.0, 8.0), lambda fr, u: bg(fr, u, True), base=(180, 60), radius=6)
    s.txt("SEARCH", (1533, 275, 1660, 298), 800, WHITE, "Botón (texto)", op=lambda fr, u: k(fr, 825, 3))
    s.cursor([(830, 1660, 380), (838, 1602, 312), (845, 1598, 304), (852, 1600, 310), (862, 1620, 360)],
             clicks=(845,), hand=True)
    return t


def search_map():
    """BL 821-890: a map card with «Event Name»; a hand clicks the magnifier, a pin drops, the address shows."""
    f0, fe, h = 821, 834, 881
    t = _p("buscar-mapa", "Mapa con buscador y pin", "Map with a search field and a pin", 18018,
           span(f0, fe, h, 1.1), "elementos", ["mapa", "buscador", "cursor", "ubicación"], thumb=2.4)
    s = Q(t, f0, fe, h, "bl", 1.1)
    m = (382, 665, 670, 858)

    def mr(fr, u):
        q = k(fr, 821, 6)
        cx, w = 526, 288 * (0.15 + 0.85 * q)
        return cx - w / 2, m[1], cx + w / 2, m[3]
    on = lambda fr, u: 1.0 if fr >= 821 else 0.0  # noqa: E731
    s.box("Mapa", [fill("#DADADA"), stroke(INK, 2.5 * s.sc)], mr, op=on, radius=8)

    def inside(x0, y0, x1, y1):
        def r(fr, u):
            a = mr(fr, u)
            return max(a[0], x0), y0, min(a[2], x1), y1
        return r
    for i, (x0, y0, x1, y1) in enumerate(((384, 727, 668, 733), (384, 811, 668, 817), (484, 667, 490, 856),
                                          (652, 667, 658, 856), (398, 667, 403, 856))):
        s.box(f"Calle {i + 1}", solid("#F2DD5A"), inside(x0, y0, x1, y1), op=lambda fr, u: k(fr, 825, 4))
    for i, (x0, y0, x1, y1) in enumerate(((384, 735, 398, 810), (528, 775, 552, 805), (594, 690, 610, 712),
                                          (434, 778, 454, 800), (500, 704, 506, 720))):
        s.box(f"Parque {i + 1}", solid("#5FC56E"), inside(x0, y0, x1, y1), op=lambda fr, u: k(fr, 826, 4))
    for i, (x0, y0, x1, y1) in enumerate(((494, 790, 528, 810), (440, 670, 470, 700))):
        s.box(f"Manzana {i + 1}", solid("#F5F0C0"), inside(x0, y0, x1, y1), op=lambda fr, u: k(fr, 827, 4))

    def pin(fr, u):
        rf = s.R(u)
        q = k(rf, 851, 5)
        return 0.4 + 0.6 * q, s.after(851)(fr, u), 0, -40 * (1 - q), 0
    s.icon("Pin", [fill(RED), stroke(INK, 2 * s.sc, "center")], 526, 752, 30, 40, g=pin, path=PIN)
    field(s, (382, 866, 670, 914), 823, 5)
    c = s.txt("Event Name", (396, 881, 541, 899), 500, op=lambda fr, u: s.before(851)(fr, u), name="Lugar")
    s.typed(c, 826, stagger=0.05, duration=0.03)
    s.txt("57 St, New York", (396, 881, 590, 899), 500, "#9A9A9A", "Dirección", op=s.after(852))
    outline_icon(s, "Lupa", SEARCH, 641, 889, 22, 22, g=pop_g(827, 5), width=3)
    s.cursor([(832, 700, 960), (842, 646, 902), (850, 643, 896), (857, 646, 902), (870, 665, 960)], clicks=(850,),
             hand=True)
    return t


def search_square():
    """BR 824-893: a field types «social buttons» beside a square blue magnifier; a click turns it to «searching…»."""
    f0, fe, h = 824, 840, 884
    t = _p("buscar-lupa", "Buscador con lupa cuadrada", "Search field with a square magnifier", 18019,
           span(f0, fe, h, 1.1), "elementos", ["buscador", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "br", 1.1)
    field(s, (1207, 752, 1517, 812), f0, 5)
    c = s.txt("social buttons", (1231, 771, 1437, 794), 500, op=lambda fr, u: s.before(853)(fr, u), name="Búsqueda")
    s.typed(c, 828, stagger=0.05, duration=0.03)
    s.txt("searching...", (1231, 771, 1400, 794), 500, "#B5B5B5", "Buscando", op=s.after(854))
    pr = press(s, 853)

    def bg(fr, u, after):
        on = (s.after(853) if after else s.before(853))(fr, u)
        return 1567, 782, 60 * pop(fr, 830, 6) * pr(u), 60 * pop(fr, 830, 6) * pr(u), 0, on
    s.shp("Botón", s.card_l(BLUE, 3.0, 8.0), lambda fr, u: bg(fr, u, False), base=(60, 60), radius=6)
    s.shp("Botón (gris)", s.card_l(GREY, 3.0, 8.0), lambda fr, u: bg(fr, u, True), base=(60, 60), radius=6)
    outline_icon(s, "Lupa", SEARCH, 1566, 781, 26, 26, g=pop_g(831, 6), colour=WHITE, width=3.5)
    s.cursor([(836, 1640, 860), (845, 1580, 800), (853, 1570, 790), (860, 1574, 796), (872, 1600, 850)],
             clicks=(853,))
    return t


# =============================================================================================================
# GRID 6 (35.6-38.9 s): comment, chat and message buttons
# =============================================================================================================
def grow_btn(s, rect, colour, appear, n=6, until=None, since=None, name="Botón", drop=8.0, radius=6.0):
    """A filled outlined button that widens from its centre at frame appear; until / since = real click frames."""
    x0, y0, x1, y1 = rect
    cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    pr = press(s, until or since) if (until or since) else (lambda u: 1.0)

    def g(fr, u):
        q = k(fr, appear, n)
        on = s.before(until)(fr, u) if until else s.after(since)(fr, u) if since else 1.0
        return cx, cy, w * (0.12 + 0.88 * q) * pr(u), h * pr(u), 0, (1.0 if fr >= appear else 0.0) * on
    return s.shp(name, s.card_l(colour, 3.0, drop), g, base=(w, h), radius=radius)


def centre_text(s, content, ink, appear, n=6, weight=800, colour=WHITE, name="Texto", until=None, since=None):
    """Text that opens from its centre (a mask widening) as its button grows."""
    x0, y0, x1, y1 = ink
    cx = (x0 + x1) / 2
    r = s.rect_((x0, y0, x1, y1))
    sc = s.sc
    st = (s.before(until) if until else s.after(since) if since else (lambda fr, u: 1.0))
    return s.say(content, r, M, weight, colour, name,
                 reveal=lambda fr: (s.X(cx) - (x1 - x0 + 20) * sc / 2 * k(fr, appear, n), -2000,
                                    s.X(cx) + (x1 - x0 + 20) * sc / 2 * k(fr, appear, n), 4000),
                 op=lambda fr, u: st(fr, u))


def add_comment():
    """TL 889-970: ADD COMMENT; the arrow clicks it, it turns grey (POSTED) and the comment opens above it."""
    f0, fe, h = 889, 930, 952
    t = _p("agregar-comentario", "Botón agregar comentario que se publica", "Add comment button that posts", 18020,
           span(f0, fe, h, 2.2), "redes", ["comentario", "botón", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "tl", 2.2)
    c = 917
    grow_btn(s, (373, 320, 655, 380), BLUE, 889, 7, until=c)
    grow_btn(s, (373, 320, 655, 380), GREY, 889, 7, since=c, name="Botón (publicado)")
    centre_text(s, "ADD COMMENT", (394, 338, 634, 361), 891, 7, until=c)
    s.txt("POSTED", (451, 338, 576, 361), 800, WHITE, "Publicado",
          op=lambda fr, u: s.after(c)(fr, u) * k(fr, f0 + 3, 2))
    unfold(s, (374, 180, 654, 299), 919, 6, "h", "Comentario", radius=6)
    for i, (line, x1) in enumerate((("Just what I'm looking", 632), ("for.  Thanks for the", 602),
                                    ("great video!", 530))):
        cl = s.txt(line, (404, 203 + 25 * i, x1, 222 + 25 * i), 500, name=f"Comentario {i + 1}")
        s.typed(cl, 921 + 6 * i, stagger=0.02, duration=0.02)
    s.cursor([(897, 600, 430), (906, 530, 372), (917, 525, 360), (923, 528, 368), (932, 560, 420)], clicks=(c,))
    return t


def send_comment():
    """TR 894-975: a comment field types a message beside a round send button; a hand sends it."""
    f0, fe, h = 894, 910, 960
    t = _p("enviar-comentario", "Campo de comentario con enviar", "Comment field with a send button", 18021,
           span(f0, fe, h, 1.3), "redes", ["comentario", "chat", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "tr", 1.3)
    c = 916
    unfold(s, (1256, 238, 1536, 328), f0, 6, "w", "Campo", radius=6)
    for i, (line, x1) in enumerate((("Thanks for the short,", 1505), ("quick tutorial!", 1430))):
        cl = s.txt(line, (1286, 261 + 25 * i, x1, 280 + 25 * i), 500, op=lambda fr, u: s.before(c)(fr, u),
                   name=f"Mensaje {i + 1}")
        s.typed(cl, 897 + 8 * i, stagger=0.03, duration=0.02)
    s.txt("Sending a message", (1286, 261, 1495, 281), 500, "#BDBDBD", "Enviando", op=s.after(c + 4))
    pr = press(s, c, 0.12)
    for col, st, nm in ((BLUE, s.before(c), "Enviar"), (GREY, s.after(c), "Enviar (enviado)")):
        s.icon(nm, [fill(col), stroke(INK, 2.5 * s.sc)], 1532, 321, 50, 50,
               g=lambda fr, u, st=st: (pop(fr, 900, 6) * pr(u), st(fr, u)), kind="ellipse")
    s.icon("Enviar (flecha)", solid(WHITE), 1534, 321, 24, 22, g=lambda fr, u: (pop(fr, 901, 6) * pr(u), 1.0),
           path=poly([(0, 0), (100, 50), (0, 100), (18, 50)]))
    s.cursor([(902, 1620, 400), (910, 1545, 340), (916, 1538, 330), (922, 1542, 336), (934, 1580, 390)],
             clicks=(c,), hand=True)
    return t


def avatar_comment():
    """BL 899-978: a round picture with a «1»; a hand clicks it and a comment bubble slides out beside it."""
    f0, fe, h = 899, 937, 962
    t = _p("avatar-comentario", "Foto con aviso que abre un comentario", "Avatar with a badge that opens a comment",
           18022, span(f0, fe, h, 2.0), "redes", ["comentario", "avatar", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "bl", 2.0)
    c = 920
    x0 = 418
    vis = lambda fr, u: (x0 - 40, 700, x0 - 40 + 360 * k(fr, 922, 8), 870)  # noqa: E731
    card = s.box("Comentario", s.card_l(WHITE, 3.0, 0.0), lambda fr, u: (lambda r: (r[0] + 40 if r[2] > x0 + 4 else r[2],
                                                                               713, min(729, r[2]), 855))(vis(fr, u)),
                 op=lambda fr, u: 1.0 if fr >= 922 else 0.0, radius=6)
    del card
    s.icon("Comentario (pico)", [fill(WHITE), stroke(INK, 3 * s.sc, "center")], 404, 718, 30, 16,
           g=lambda fr, u: (1.0, 1.0 if fr >= 925 else 0.0), path=poly([(0, 0), (100, 0), (100, 100), (40, 100)]))
    s.txt("LUCAS GRIFF", (447, 740, 648, 764), 800, slide=(926, 7, 60), name="Nombre")
    s.txt("Yes! I needed this video!", (448, 778, 703, 797), 500, slide=(928, 7, 60), name="Comentario 1")
    s.txt("Love your tutorials ))", (448, 803, 664, 822), 500, slide=(930, 7, 60), name="Comentario 2")
    s.icon("Foto (sombra)", solid(SHADOW), 337, 793, 142, 142, g=pop_g(f0, 6), kind="ellipse")
    s.avatar("ig3-headphones-01", 331, 787, 70, g=lambda fr, u: (pop(fr, f0, 6) * press(s, c, 0.06)(u), 1.0),
             line=3.0)
    s.icon("Aviso", [fill(BLUE), stroke(INK, 2.5 * s.sc)], 373, 729, 50, 50,
           g=lambda fr, u: (pop(fr, 905, 6), 1.0 - k(s.R(u), c + 2, 4)), kind="ellipse")
    s.txt("1", (367, 717, 379, 741), 500, WHITE, "Aviso (número)",
          op=lambda fr, u: k(fr, 907, 3) * (1.0 - k(s.R(u), c + 2, 4)))
    s.cursor([(905, 480, 840), (913, 360, 805), (920, 345, 795), (926, 350, 805), (936, 420, 870)], clicks=(c,),
             hand=True)
    return t


def message_opening():
    """BR 901-982: a MESSAGE button with a red «1»; the arrow clicks it and it opens as OPENING with the message."""
    f0, fe, h = 901, 938, 965
    t = _p("mensaje-abrir", "Botón de mensaje que se abre", "Message button that opens", 18023,
           span(f0, fe, h, 2.0), "redes", ["mensaje", "chat", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "br", 2.0)
    c = 924
    grow_btn(s, (1230, 650, 1462, 721), "#5FD3E6", f0, 6, until=c, radius=6)
    centre_text(s, "MESSAGE", (1260, 672, 1431, 701), f0 + 2, 6, colour=INK, until=c)
    s.icon("Aviso", [fill(RED), stroke(WHITE, 1.5 * s.sc)], 1441, 661, 26, 26,
           g=lambda fr, u: (pop(fr, 909, 5), s.before(c)(fr, u)), kind="ellipse")
    s.txt("1", (1438, 655, 1445, 667), 500, WHITE, "Aviso (número)", op=lambda fr, u: k(fr, 910, 3) * s.before(c)(fr, u))
    unfold(s, (1245, 745, 1577, 876), 929, 6, "h", "Mensaje", radius=6)
    s.icon("Mensaje (pico)", [fill(WHITE), stroke(INK, 3 * s.sc, "center")], 1258, 735, 26, 24,
           g=lambda fr, u: (1.0, 1.0 if fr >= 933 else 0.0), path=poly([(0, 0), (30, 0), (100, 100), (0, 100)]))
    grow_btn(s, (1246, 655, 1446, 715), GREEN, 926, 5, name="Abierto", radius=6)
    centre_text(s, "OPENING", (1275, 674, 1417, 698), 927, 5, name="Abierto (texto)")
    s.txt("JUAN EVANS", (1277, 767, 1474, 792), 800, slide=(932, 7, 60), name="Nombre")
    s.txt("Wow! You make it look", (1277, 804, 1518, 823), 500, slide=(934, 7, 60), name="Mensaje 1")
    s.txt("so easy. Looks really nice!", (1277, 829, 1543, 848), 500, slide=(935, 7, 60), name="Mensaje 2")
    s.cursor([(910, 1560, 700), (917, 1460, 700), (924, 1450, 695), (929, 1455, 700), (940, 1530, 760)],
             clicks=(c,))
    return t


# =============================================================================================================
# GRID 7 (38.8-43.6 s): chats
# =============================================================================================================
def bubble_path(w, h, tail="bl", t=14.0, r=None):
    """A chat bubble (w × h px including its tail of width t) as a path on 0..100: a rounded body with a pointed
    tail at one corner (bl / br at the bottom, tl / tr at the top)."""
    r = r if r is not None else h / 2
    c = 0.45
    X = lambda x: 100 * x / w  # noqa: E731
    Y = lambda y: 100 * y / h  # noqa: E731
    a, b = t, w  # body x range
    pts = [f"M {X(a):.2f} {Y(r):.2f}",
           f"C {X(a):.2f} {Y(r * c):.2f} {X(a + r * c):.2f} {Y(0):.2f} {X(a + r):.2f} {Y(0):.2f}",
           f"L {X(b - r):.2f} {Y(0):.2f}",
           f"C {X(b - r * c):.2f} {Y(0):.2f} {X(b):.2f} {Y(r * c):.2f} {X(b):.2f} {Y(r):.2f}",
           f"L {X(b):.2f} {Y(h - r):.2f}",
           f"C {X(b):.2f} {Y(h - r * c):.2f} {X(b - r * c):.2f} {Y(h):.2f} {X(b - r):.2f} {Y(h):.2f}",
           f"L {X(a + r * 0.7):.2f} {Y(h):.2f}",
           f"L {X(0):.2f} {Y(h):.2f}",
           f"C {X(a * 0.7):.2f} {Y(h - 2):.2f} {X(a):.2f} {Y(h - r * 0.4):.2f} {X(a):.2f} {Y(h - r * 0.9):.2f}",
           "Z"]
    path = " ".join(pts)
    if tail == "bl":
        return path
    return _turn(path, fx=tail in ("br", "tr"), fy=tail in ("tl", "tr"))


def bubble(s, name, rect, tail, colour, appear, n=6, op=None, drop=7.0, line=2.5, clock=None):
    """A chat bubble in rect (tail included) that pops from its tail corner at frame appear."""
    x0, y0, x1, y1 = rect
    w, h = x1 - x0, y1 - y0
    path = bubble_path(w, h, tail, t=min(16.0, w * 0.1))
    ax = x0 if tail in ("bl", "tl") else x1
    ay = y1 if tail in ("bl", "br") else y0

    def g(fr, u):
        fr = clock(fr, u) if clock else fr
        q = pop(fr, appear, n, 0.08)
        cx, cy = ax + ((x0 + x1) / 2 - ax) * q, ay + ((y0 + y1) / 2 - ay) * q
        o = (1.0 if fr >= appear else 0.0) * (op(fr, u) if op else 1.0)
        return cx, cy, w * max(q, 1e-3), h * max(q, 1e-3), 0, o
    layers = ([hard(drop * s.sc, drop * s.sc)] if drop else []) + [fill(colour), stroke(INK, line * s.sc, "center")]
    return s.shp(name, layers, g, path=path, base=(w, h))


def btn_swap(s, rect, word_a, ink_a, word_b, ink_b, appear, click, col_a=WHITE, col_b=GREY, txt_a=INK, txt_b=WHITE,
             name="Botón"):
    """A pill button (pops at appear) that swaps colour and word at real frame click."""
    x0, y0, x1, y1 = rect
    cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    pr = press(s, click, 0.1)
    for col, st, nm in ((col_a, s.before(click), name), (col_b, s.after(click), f"{name} (activo)")):
        s.icon(nm, [fill(col), stroke(INK, 2.5 * s.sc)], cx, cy, w, h,
               g=lambda fr, u, st=st: (pop(fr, appear, 6, 0.1) * pr(u), st(fr, u)), radius=h / 2)
    centre_text(s, word_a, ink_a, appear + 1, 6, colour=txt_a, name=f"{name} (texto)", until=click)
    s.txt(word_b, ink_b, 800, txt_b, f"{name} (texto activo)", op=s.after(click))


def chat_two():
    """TL 971-1088: «How are you?» from one side; the arrow clicks ANSWER and «Excellent!» comes from the other."""
    f0, fe, h = 971, 1012, 1074
    t = _p("chat-dos", "Chat de dos con hora y responder", "Two-person chat with times and answer", 18024,
           span(f0, fe, h, 2.2), "redes", ["chat", "mensaje", "cursor"], thumb=3.6)
    s = Q(t, f0, fe, h, "tl", 2.2)
    c = 999
    bubble(s, "Mensaje 1", (358, 155, 575, 207), "bl", YELLOW, 972, 6)
    s.avatar("h-portrait-06", 324, 181, 26, g=pop_g(974, 5))
    m = s.txt("How are you?", (402, 172, 546, 190), 500, name="Mensaje 1 (texto)")
    s.typed(m, 976, stagger=0.03, duration=0.02)
    s.txt("2:40 PM", (373, 131, 458, 146), 500, op=lambda fr, u: k(fr, 979, 4), name="Hora 1")
    bubble(s, "Mensaje 2", (493, 265, 670, 317), "br", RED, c + 2, 6, op=s.after(c + 2))
    s.avatar("fx-man-05", 704, 291, 26, g=lambda fr, u: (pop(fr, 1006, 5), 1.0))
    m2 = s.txt("Excellent!", (522, 284, 624, 302), 500, op=s.after(c + 4), name="Mensaje 2 (texto)")
    s.typed(m2, c + 4, stagger=0.03, duration=0.02)
    s.txt("2:47 PM", (573, 241, 655, 256), 500, op=lambda fr, u: k(fr, 1009, 4), name="Hora 2")
    btn_swap(s, (444, 386, 584, 426), "ANSWER", (470, 399, 558, 413), "SEND", (483, 398, 544, 414), 978, c)
    s.cursor([(982, 640, 460), (992, 525, 418), (999, 518, 408), (1005, 522, 414), (1016, 560, 470)], clicks=(c,))
    return t


def chat_names():
    """TR 976-1092: ELWIN says «Awesome!»; a hand clicks ANSWER and CLAIRE replies «Thank you!»."""
    f0, fe, h = 976, 1016, 1077
    t = _p("chat-nombres", "Chat con nombres y responder", "Chat with names and answer", 18025,
           span(f0, fe, h, 2.2), "redes", ["chat", "mensaje", "cursor"], thumb=3.6)
    s = Q(t, f0, fe, h, "tr", 2.2)
    c = 1004
    bubble(s, "Mensaje 1", (1226, 161, 1413, 213), "tl", "#5FD3E6", 977, 6)
    s.txt("ELWIN", (1242, 136, 1315, 153), 800, op=lambda fr, u: k(fr, 979, 4), name="Nombre 1")
    m = s.txt("Awesome!", (1272, 178, 1382, 195), 500, name="Mensaje 1 (texto)")
    s.typed(m, 980, stagger=0.03, duration=0.02)
    bubble(s, "Mensaje 2", (1386, 271, 1585, 323), "tr", BLUE, c + 2, 6, op=s.after(c + 2))
    m2 = s.txt("Thank you!", (1416, 290, 1532, 307), 500, WHITE, op=s.after(c + 4), name="Mensaje 2 (texto)")
    s.typed(m2, c + 4, stagger=0.03, duration=0.02)
    s.txt("CLAIRE", (1481, 246, 1562, 263), 800, op=lambda fr, u: k(fr, 1011, 4), name="Nombre 2")
    btn_swap(s, (1331, 392, 1472, 432), "ANSWER", (1358, 405, 1446, 419), "SEND", (1371, 404, 1432, 420), 983, c)
    s.cursor([(987, 1540, 470), (996, 1410, 424), (1004, 1404, 416), (1010, 1408, 422), (1020, 1450, 480)],
             clicks=(c,), hand=True)
    return t


def phone_chat(s, card, colour, msgs, field_r, send, square, typed_at, pitch=80.0):
    """A chat window: the card unfolds; msgs = dicts (appear, rect, tail, col, text, ink, tcol, extras); each message
    that arrives later pushes the earlier ones up by `pitch` (they start at the bottom, by the field). The messages
    typed in the field are sent with the button (typed_at = [(start, send frame, text, ink)])."""
    unfold(s, card, s.f0, 7, "h", "Ventana", s.card_l(colour, 3.0, 9.0))
    fx0, fy0, fx1, fy1 = field_r
    gate = s.f0 + 8
    s.icon("Campo", [fill(WHITE), stroke(INK, 2.5 * s.sc)], (fx0 + fx1) / 2, (fy0 + fy1) / 2, fx1 - fx0, fy1 - fy0,
           g=lambda fr, u: (1.0, k(fr, gate, 4)), radius=(fy1 - fy0) / 2 if not square else 6)
    sx, sy, sd = send
    sends = [c for _, c, _, _ in typed_at]

    def ready(fr, u):
        rf = s.R(u)
        return 1.0 if any(c - 5 <= rf < c + 1 for c in sends) else 0.0
    kind, rad = ("rectangle", 6) if square else ("ellipse", 0)
    s.icon("Enviar", [fill(GREY), stroke(INK, 2.5 * s.sc)], sx, sy, sd, sd,
           g=lambda fr, u: (pop(fr, gate, 5) * (1 - 0.12 * sum(math.sin(math.pi * lin(s.R(u), c - 2, 4))
                                                              for c in sends)), 1.0), kind=kind, radius=rad)
    s.icon("Enviar (listo)", [fill(BLUE if square else RED), stroke(INK, 2.5 * s.sc)], sx, sy, sd, sd,
           g=lambda fr, u: (pop(fr, gate, 5), ready(fr, u)), kind=kind, radius=rad)
    s.icon("Enviar (flecha)", solid(INK), sx + 1, sy, sd * 0.45, sd * 0.45, g=pop_g(gate + 1, 5),
           path=poly([(0, 0), (100, 50), (0, 100)]))
    for i, (start, c, text, ink) in enumerate(typed_at):
        cl = s.txt(text, ink, 500, name=f"Escribiendo {i + 1}",
                   op=lambda fr, u, start=start, c=c: 1.0 if start <= s.R(u) < c and fr >= gate else 0.0)
        cl["textStyle"]["animation"] = {"in": tanim("typewriter", duration=0.02, unit="character", stagger=0.03,
                                                    ease="easeOut", delay=round((start - s.f0) / SRC, 3))}
    arrivals = [m["appear"] for m in msgs]

    def dy(i):
        return lambda u: sum(pitch * (1 - k(s.R(u), a, 5)) for a in arrivals[i + 1:])

    def shown(a, first):
        if first:
            return lambda fr, u: 1.0 if fr >= a else 0.0
        return lambda fr, u: 1.0 if s.R(u) >= a and fr >= gate else 0.0

    for i, m in enumerate(msgs):
        a, first = m["appear"], i == 0
        d = dy(i)
        x0, y0, x1, y1 = m["rect"]
        w, h = x1 - x0, y1 - y0
        tail = m["tail"]
        path = bubble_path(w, h, tail, t=min(16.0, w * 0.1))
        ax = x0 if tail in ("bl", "tl") else x1
        ay = y1 if tail in ("bl", "br") else y0

        def g(fr, u, a=a, first=first, d=d, x0=x0, y0=y0, x1=x1, y1=y1, w=w, h=h, ax=ax, ay=ay):
            clock = fr if first else (s.R(u) if fr >= gate else -1e9)
            q = pop(clock, a, 6, 0.08)
            cx, cy = ax + ((x0 + x1) / 2 - ax) * q, ay + ((y0 + y1) / 2 - ay) * q + d(u)
            return cx, cy, w * max(q, 1e-3), h * max(q, 1e-3), 0, 1.0 if clock >= a else 0.0
        s.shp(f"Mensaje {i + 1}", [hard(7 * s.sc, 7 * s.sc), fill(m["col"]), stroke(INK, 2.5 * s.sc, "center")], g,
              path=path, base=(w, h))
        vis = shown(a + 2, first)
        s.txt(m["text"], m["ink"], 500, m["tcol"], f"Mensaje {i + 1} (texto)",
              g=lambda fr, u, d=d, vis=vis: (0, d(u), 1, 0, vis(fr, u)))
        for j, (word, ink, weight) in enumerate(m.get("labels", ())):
            vis2 = shown(a + 3, first)
            s.txt(word, ink, weight, INK, f"Mensaje {i + 1} (rótulo {j + 1})",
                  g=lambda fr, u, d=d, vis2=vis2: (0, d(u), 1, 0, vis2(fr, u)))
        av = m.get("avatar")
        if av:
            smp, cx, cy, r, sq, label = av
            vis3 = shown(a + 2, first)
            if sq:
                s.pic(smp, (cx - r, cy - r, cx + r, cy + r), name=f"Foto {i + 1}", line=2.0, label=label,
                      shift=lambda fr, u, d=d: (0, d(u)), op=vis3)
            else:
                n0 = len(s.t.tracks)
                s.avatar(smp, cx, cy, r, g=lambda fr, u, vis3=vis3: (1.0, vis3(fr, u)), name=f"Foto {i + 1}",
                         label=label)
                for tr in s.t.tracks[n0:]:
                    for clip in tr.clips:
                        _shift_clip(s, clip, d)


def _shift_clip(s, clip, d):
    """Adds a vertical offset d(u) (reference px) to a clip's position, key by key."""
    us = frames_of(s.dur)
    ys = clip["y"]["keyframes"]
    if len(ys) == 1:
        y = ys[0]["value"]
        clip["y"] = keys([(u, y + d(u) * s.sc, "linear") for u in us])
    else:
        clip["y"] = keys([(u, kf["value"] + d(u) * s.sc, "linear") for u, kf in zip(us, ys)])


def chat_phone_blue():
    """BL 981-1095: a blue chat window; «Hi! How r u?» arrives, then «Excellent!» and «See u later!» are typed and
    sent, each pushing the earlier messages up."""
    f0, fe, h = 981, 995, 1080
    t = _p("chat-ventana-azul", "Ventana de chat azul", "Blue chat window", 18026, span(f0, fe, h, 1.6), "redes",
           ["chat", "mensaje", "ventana"], thumb=3.6)
    s = Q(t, f0, fe, h, "bl", 1.6)
    phone_chat(s, (374, 608, 679, 952), "#69D6E8", [
        dict(appear=989, rect=(446, 663, 590, 704), tail="bl", col=YELLOW, text="Hi! How r u?",
             ink=(472, 676, 575, 690), tcol=INK, avatar=("fx-woman-06", 418, 684, 21, False, "Foto 1"),
             labels=[("2:40 PM", (458, 647, 506, 656), 500)]),
        dict(appear=1024, rect=(482, 744, 607, 785), tail="br", col=RED, text="Excellent!",
             ink=(497, 757, 578, 771), tcol=INK, avatar=("ig3-model-01", 634, 764, 21, False, "Foto 2"),
             labels=[("2:41 PM", (550, 727, 595, 736), 500)]),
        dict(appear=1048, rect=(446, 823, 583, 864), tail="bl", col=YELLOW, text="See u later!",
             ink=(472, 836, 566, 850), tcol=INK, avatar=("fx-woman-06", 418, 843, 21, False, "Foto 1"),
             labels=[("2:42 PM", (458, 807, 505, 816), 500)])],
        (398, 896, 606, 928), (638, 912, 32), False,
        [(1010, 1022, "Excellent!", (412, 906, 492, 919)), (1033, 1046, "See u later!", (412, 906, 506, 919))])
    s.cursor([(1012, 700, 960), (1018, 642, 918), (1022, 640, 914), (1027, 645, 920), (1036, 642, 916),
              (1046, 640, 914), (1054, 690, 960)], clicks=(1022, 1046))
    return t


def chat_phone_yellow():
    """BR 986-1098: a yellow chat window with names and square pictures; two messages are typed and sent."""
    f0, fe, h = 986, 1000, 1082
    t = _p("chat-ventana-amarilla", "Ventana de chat amarilla con nombres", "Yellow chat window with names", 18027,
           span(f0, fe, h, 1.6), "redes", ["chat", "mensaje", "ventana"], thumb=3.6)
    s = Q(t, f0, fe, h, "br", 1.6)
    phone_chat(s, (1250, 612, 1554, 956), "#FBB614", [
        dict(appear=994, rect=(1321, 667, 1442, 708), tail="tl", col="#5FD3E6", text="Hey, sup?",
             ink=(1348, 680, 1428, 694), tcol=INK, avatar=("h-portrait-02", 1294, 688, 20, True, "Foto 1"),
             labels=[("JOHN", (1335, 647, 1385, 661), 800)]),
        dict(appear=1028, rect=(1337, 748, 1482, 789), tail="tr", col=BLUE, text="Just chilling",
             ink=(1352, 761, 1454, 775), tcol=WHITE, avatar=("fx-man-05", 1510, 768, 20, True, "Foto 2"),
             labels=[("DAN", (1431, 728, 1470, 742), 800)]),
        dict(appear=1058, rect=(1321, 827, 1494, 868), tail="tl", col="#5FD3E6", text="I'll catch u later",
             ink=(1348, 840, 1477, 854), tcol=INK, avatar=("h-portrait-02", 1294, 848, 20, True, "Foto 1"),
             labels=[("JOHN", (1335, 808, 1385, 822), 800)])],
        (1274, 900, 1482, 932), (1514, 916, 32), True,
        [(1014, 1026, "Just chilling", (1288, 910, 1386, 923)),
         (1044, 1056, "I'll catch u later", (1288, 910, 1418, 923))])
    s.cursor([(1016, 1580, 960), (1022, 1518, 922), (1026, 1516, 918), (1031, 1520, 924), (1046, 1518, 922),
              (1056, 1516, 918), (1064, 1570, 965)], clicks=(1026, 1056), hand=True)
    return t


# =============================================================================================================
# GRID 8 (43.4-47.6 s): ratings
# =============================================================================================================
STAR_ON = None


def star(s, name, cx, cy, size, g, on=True, rot=0.0):
    layers = [fill(YELLOW) if on else nofill(), stroke(INK, 2.0 * s.sc, "center")]
    if rot:
        base = g
        g = lambda fr, u: (lambda v: (v[0], v[1], 0.0, 0.0, rot))(base(fr, u))  # noqa: E731
    return s.icon(name, layers, cx, cy, size, size * 0.96, g=g, path=STAR)


def rate_ring():
    """TL 1096-1180: a red RATE disc; the arrow clicks it, it turns white «10/10» and ten stars pop round it."""
    f0, fe, h = 1096, 1140, 1163
    t = _p("valorar-10", "Valoración 10/10 con estrellas", "10/10 rating with stars", 18028, span(f0, fe, h, 2.0),
           "elementos", ["valoración", "estrellas", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "tl", 2.0)
    c = 1122
    cx, cy = 505, 272
    for i in range(10):
        a = math.radians(-90 + 36 * i)
        x, y = cx + 106 * math.cos(a), cy + 106 * math.sin(a)
        at = 1124 + i * 1.2

        def g(fr, u, at=at, x=x, y=y):
            q = pop(fr, at, 6, 0.2)
            return q, 1.0 if fr >= at else 0.0, (cx - x) * (1 - min(1.0, q)), (cy - y) * (1 - min(1.0, q)), 0
        star(s, f"Estrella {i + 1}", x, y, 56, g)
    pr = press(s, c, 0.1)
    s.icon("Disco (sombra)", solid(SHADOW), cx + 9, cy + 9, 120, 120, g=lambda fr, u: (pop(fr, f0, 6) * pr(u), 1.0),
           kind="ellipse")
    s.icon("Disco", [fill(RED), stroke(INK, 3 * s.sc)], cx, cy, 120, 120,
           g=lambda fr, u: (pop(fr, f0, 6) * pr(u), s.before(c)(fr, u)), kind="ellipse")
    s.icon("Disco (blanco)", [fill(WHITE), stroke(INK, 3 * s.sc)], cx, cy, 120, 120,
           g=lambda fr, u: (pop(fr, f0, 6) * pr(u), s.after(c)(fr, u)), kind="ellipse")
    s.txt("RATE", (482, 263, 528, 281), 800, WHITE, "Valorar", align="left",
          g=lambda fr, u: (0, 0, pop(fr, f0 + 2, 6), 0, s.before(c)(fr, u) * (1.0 if fr >= f0 + 2 else 0.0)))
    s.txt("10/10", (469, 262, 541, 284), 800, INK, "Nota", g=lambda fr, u: (0, 0, pop(fr, c + 1, 5), 0,
                                                                           s.after(c)(fr, u)))
    s.cursor([(1104, 620, 330), (1114, 530, 292), (1122, 522, 286), (1128, 530, 296), (1138, 590, 360)],
             clicks=(c,))
    return t


def rate_us():
    """TR 1104-1182: RATE US! with five empty stars (5 stars … 1 star); a hand clicks the top one and they fill."""
    f0, fe, h = 1104, 1114, 1166
    t = _p("valoranos", "Valóranos: lista de estrellas", "Rate us: list of stars", 18029, span(f0, fe, h, 1.4),
           "elementos", ["valoración", "estrellas", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "tr", 1.4)
    c = 1127
    s.txt("RATE US!", (1327, 152, 1465, 175), 800, op=lambda fr, u: k(fr, 1107, 4), name="Título")
    for i, (y, word) in enumerate(((223, "5 stars"), (273, "4 stars"), (323, "3 stars"), (373, "2 stars"),
                                   (423, "1 star"))):
        at = 1104 + 1.5 * i
        star(s, f"Estrella {i + 1}", 1346, y, 44, lambda fr, u, at=at: (pop(fr, at, 5), 1.0), on=False)
        fill_at = c + 2 + 2 * (4 - i)

        def g(fr, u, at=at, fa=fill_at):
            q = lin(s.R(u), fa, 4)
            return pop(fr, at, 5) * (1 + 0.25 * math.sin(math.pi * q)), 1.0 if s.R(u) >= fa else 0.0
        star(s, f"Estrella {i + 1} (llena)", 1346, y, 44, g)
        x1 = 1386 + (67 if word != "1 star" else 52)
        s.txt(word, (1386, y - 9, x1, y + 8), 500, slide=(at + 2, 6, 30), name=f"Opción {i + 1}")
    s.cursor([(1110, 1460, 300), (1118, 1360, 260), (1123, 1352, 232), (1127, 1350, 228), (1133, 1355, 236),
              (1145, 1420, 300)], clicks=(c,), hand=True)
    return t


def rate_template():
    """BL 1104-1186: a RATE TEMPLATE card with a logo and five empty stars; the hand fills them one by one."""
    f0, fe, h = 1104, 1115, 1171
    t = _p("valorar-plantilla", "Tarjeta para valorar con estrellas", "Rating card with stars", 18030,
           span(f0, fe, h, 1.0), "elementos", ["valoración", "estrellas", "cursor", "logo"], thumb=2.6)
    s = Q(t, f0, fe, h, "bl", 1.0)
    unfold(s, (330, 692, 720, 872), f0, 7, "w")
    s.icon("Logo (aro)", [fill(GREEN), stroke(INK, 2.5 * s.sc)], 389, 751, 60, 60, g=pop_g(1109, 5), kind="ellipse")
    clip = s.avatar("logo-flip", 389, 751, 25, g=pop_g(1110, 5), line=0, label="Tu logo", name="Logo")
    clip["brandRole"] = "logo"
    s.txt("RATE TEMPLATE", (439, 721, 690, 743), 800, slide=(1110, 7, 50), name="Título")
    s.txt("Social Buttons Pack", (439, 759, 650, 777), 500, slide=(1112, 7, 50), name="Subtítulo")
    fills = (1128, 1131, 1134, 1137, 1140)
    for i, x in enumerate((405, 465, 525, 585, 645)):
        at = 1111 + i
        star(s, f"Estrella {i + 1}", x, 820, 48, lambda fr, u, at=at: (pop(fr, at, 5), 1.0), on=False)

        def g(fr, u, at=at, fa=fills[i]):
            q = lin(s.R(u), fa, 4)
            return pop(fr, at, 5) * (1 + 0.25 * math.sin(math.pi * q)), 1.0 if s.R(u) >= fa else 0.0
        star(s, f"Estrella {i + 1} (llena)", x, 820, 48, g)
    s.cursor([(1115, 760, 870), (1124, 410, 832), (1128, 408, 828), (1131, 468, 828), (1134, 528, 828),
              (1137, 588, 828), (1140, 648, 828), (1146, 655, 834), (1156, 700, 900)], clicks=(1140,), hand=True)
    return t


def rate_great():
    """BR 1106-1190: a red RATE ITEM button; the arrow clicks it, it turns grey GREAT! and five stars pop above."""
    f0, fe, h = 1106, 1150, 1176
    t = _p("valorar-genial", "Botón valorar que da estrellas", "Rate button that gives stars", 18031,
           span(f0, fe, h, 2.6), "elementos", ["valoración", "estrellas", "cursor", "botón"], thumb=2.4)
    s = Q(t, f0, fe, h, "br", 2.6)
    c = 1137
    grow_btn(s, (1288, 762, 1508, 822), RED, f0, 7, until=c)
    grow_btn(s, (1288, 762, 1508, 822), GREY, f0, 7, since=c, name="Botón (genial)")
    centre_text(s, "RATE ITEM", (1323, 781, 1473, 803), f0 + 2, 7, until=c)
    s.txt("GREAT!", (1343, 781, 1453, 803), 800, WHITE, "Genial",
          op=lambda fr, u: s.after(c)(fr, u) * k(fr, f0 + 3, 2))
    for i, (x, y, size, rot) in enumerate(((1287, 720, 48, -12), (1337, 690, 48, -6), (1398, 680, 50, 0),
                                           (1458, 690, 52, 8), (1508, 720, 52, 14))):
        at = c + 1 + 2 * i

        def g(fr, u, at=at, x=x, y=y, rot=rot):
            q = pop(fr, at, 6, 0.25)
            return q, 1.0 if fr >= at else 0.0, 0, 50 * (1 - min(1.0, q)), rot
        star(s, f"Estrella {i + 1}", x, y, size, g)
    s.cursor([(1114, 1500, 900), (1126, 1410, 812), (1137, 1402, 800), (1144, 1410, 830), (1160, 1425, 910)],
             clicks=(c,))
    return t


# =============================================================================================================
# GRID 9 (47.4-50.4 s): rating rows
# =============================================================================================================
EYES = "M 34 36 L 34 46 M 66 36 L 66 46"
MOUTHS = ("M 32 76 C 38 60 62 60 68 76", "M 34 72 C 42 63 58 63 66 72", "M 33 68 L 67 68",
          "M 32 62 C 40 74 60 74 68 62", "M 28 56 L 72 56 C 68 82 32 82 28 56 Z")


def rating_row(s, title, ink, xs, y, size, path, on_colour, appear, click, cursor, hand, faces=False):
    """A title and five outline icons that pop in from the left; a click on the last one fills them left to right."""
    s.txt(title, ink, 800, op=lambda fr, u: k(fr, appear, 4), name="Título")
    for i, x in enumerate(xs):
        at = appear + 1.5 * i
        fa = click + 1 + 2 * i
        g_off = lambda fr, u, at=at: (pop(fr, at, 5), 1.0)  # noqa: E731

        def g_on(fr, u, at=at, fa=fa):
            q = lin(s.R(u), fa, 5)
            return pop(fr, at, 5) * (1 + 0.28 * math.sin(math.pi * q)), 1.0 if s.R(u) >= fa else 0.0
        if faces:
            col = YELLOW if i == len(xs) - 1 else "#B9B9B9"
            s.icon(f"Cara {i + 1}", [fill(WHITE), stroke(INK, 2 * s.sc)], x, y, size, size, g=g_off, kind="ellipse")
            s.icon(f"Cara {i + 1} (color)", [fill(col), stroke(INK, 2 * s.sc)], x, y, size, size, g=g_on,
                   kind="ellipse")
            gm = lambda fr, u, at=at, fa=fa: (pop(fr, at, 5) * (1 + 0.28 * math.sin(math.pi * lin(s.R(u), fa, 5))),  # noqa: E731
                                               1.0)
            outline_icon(s, f"Cara {i + 1} (ojos)", EYES, x, y, size, size, g=gm, width=2.2)
            filled = INK if i == len(xs) - 1 else None
            outline_icon(s, f"Cara {i + 1} (boca)", MOUTHS[i], x, y, size, size, g=gm, width=2.0, filled=filled)
        else:
            s.icon(f"Icono {i + 1}", [nofill(), stroke(INK, 2.0 * s.sc, "center")], x, y, size, size * 0.95, g=g_off,
                   path=path)
            s.icon(f"Icono {i + 1} (lleno)", [fill(on_colour), stroke(INK, 2.0 * s.sc, "center")], x, y, size,
                   size * 0.95, g=g_on, path=path)
    if faces:
        s.burst(xs[-1], y, click + 9, r0=size * 0.8, r1=size * 1.3, ln=8)
    s.cursor(cursor, clicks=(click,), hand=hand)


def rate_item():
    """TL 1187-1258: RATE THIS ITEM and five stars; the arrow clicks the last and they fill one by one."""
    f0, fe, h = 1187, 1198, 1243
    t = _p("valorar-articulo", "Valorar con cinco estrellas", "Rate with five stars", 18032, span(f0, fe, h, 1.1),
           "elementos", ["valoración", "estrellas", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "tl", 1.1)
    rating_row(s, "RATE THIS ITEM", (399, 200, 641, 221), [399, 459, 519, 579, 639], 268, 48, STAR, YELLOW, 1189,
               1212, [(1196, 730, 330), (1205, 650, 285), (1212, 642, 276), (1220, 650, 290), (1232, 700, 330)],
               False)
    return t


def recommend():
    """TR 1192-1262: I RECOMMEND and five hearts; a hand clicks the last and they turn red one by one."""
    f0, fe, h = 1192, 1203, 1246
    t = _p("recomiendo", "Recomiendo: cinco corazones", "I recommend: five hearts", 18033, span(f0, fe, h, 1.1),
           "elementos", ["valoración", "corazones", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "tr", 1.1)
    rating_row(s, "I RECOMMEND", (1287, 201, 1512, 222), [1280, 1340, 1400, 1460, 1520], 271, 50, HEART, RED, 1193,
               1215, [(1199, 1600, 330), (1208, 1530, 292), (1215, 1522, 282), (1222, 1528, 300), (1236, 1532, 360)],
               True)
    return t


def advise_friends():
    """BL 1195-1265: ADVISE FRIENDS and five thumbs; a hand clicks the last and they turn blue one by one."""
    f0, fe, h = 1195, 1206, 1249
    t = _p("aconseja-amigos", "Recomienda a tus amigos: pulgares", "Advise friends: thumbs up", 18034,
           span(f0, fe, h, 1.1), "elementos", ["valoración", "me gusta", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "bl", 1.1)
    rating_row(s, "ADVISE FRIENDS", (389, 697, 647, 718), [398, 458, 518, 578, 638], 768, 46, THUMB, BLUE, 1196,
               1220, [(1204, 720, 840), (1213, 646, 790), (1220, 640, 782), (1227, 646, 800), (1240, 700, 850)],
               True)
    return t


def like_faces():
    """BR 1198-1268: LIKE THIS VIDEO and five faces from sad to happy; the arrow picks the happiest."""
    f0, fe, h = 1198, 1209, 1251
    t = _p("caras-valorar", "¿Te gustó el video? Caras", "Did you like the video? Faces", 18035,
           span(f0, fe, h, 1.1), "elementos", ["valoración", "caras", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "br", 1.1)
    rating_row(s, "LIKE THIS VIDEO", (1271, 699, 1524, 720), [1278, 1338, 1398, 1458, 1518], 770, 46, None, None,
               1199, 1222, [(1206, 1600, 840), (1215, 1528, 790), (1222, 1520, 778), (1229, 1526, 790),
                            (1242, 1560, 850)], False, faces=True)
    return t


# =============================================================================================================
# GRID 10 (50.3-53.6 s): reaction buttons with rising icons
# =============================================================================================================
DOLLAR = "M 64 34 C 60 24 38 25 38 37 C 38 50 64 48 63 63 C 62 76 38 76 35 65 M 50 18 L 50 82"


def reaction(s, rect, colour, word, ink, word2, ink2, click, kind, cursor, hand, txt=WHITE, n=8):
    """A coloured button that, clicked, turns white with a new word while little icons rise from it, wobbling,
    growing and fading."""
    x0, y0, x1, y1 = rect
    cx = (x0 + x1) / 2
    grow_btn(s, rect, colour, s.f0, 8, until=click)
    grow_btn(s, rect, WHITE, s.f0, 8, since=click, name="Botón (respuesta)")
    centre_text(s, word, ink, s.f0 + 2, 8, colour=txt, until=click)
    s.txt(word2, ink2, 800, INK, "Respuesta", g=lambda fr, u: (0, 0, pop(s.R(u), click, 5, 0.1) if s.R(u) >= click
                                                                else 1.0, 0, s.after(click)(fr, u)
                                                                * (1.0 if fr >= s.f0 + 6 else 0.0)))
    rng = __import__("random").Random(sum(map(ord, word)))
    for i in range(n):
        at = click + 2 + 4 * i
        side = rng.uniform(-1, 1)
        size = rng.uniform(34, 50)
        life = 22

        def g(fr, u, at=at, side=side, size=size):
            rf = s.R(u)
            q = lin(rf, at, life)
            if rf < at or q >= 1 or fr < s.fe - 1:
                return 0.0, 0.0, 0, 0, 0
            dy = -170 * (1 - (1 - q) ** 1.6)
            dx = side * 40 * math.sin(q * math.pi * 1.2)
            op = min(1.0, q * 6) * (1 - max(0.0, (q - 0.45) / 0.55)) * 0.95 + 0.05 * (q < 0.45)
            return (0.5 + 0.7 * q) * size / 46, op, dx, dy, side * 18 * q
        if kind == "heart":
            s.icon(f"Icono {i + 1}", [fill(RED), stroke(INK, 1.8 * s.sc, "center")], cx, y0 - 22, 46, 42, g=g,
                   path=HEART)
        elif kind == "thumb":
            s.icon(f"Icono {i + 1}", [fill(BLUE), stroke(INK, 1.8 * s.sc, "center")], cx, y0 - 22, 46, 46, g=g,
                   path=THUMB)
        elif kind == "star":
            s.icon(f"Icono {i + 1}", [fill(GREEN), stroke(INK, 1.8 * s.sc, "center")], cx, y0 - 22, 46, 44, g=g,
                   path=STAR)
        else:
            s.icon(f"Icono {i + 1}", [fill(YELLOW), stroke(INK, 1.8 * s.sc)], cx, y0 - 22, 46, 46, g=g,
                   kind="ellipse")
            outline_icon(s, f"Icono {i + 1} ($)", DOLLAR, cx, y0 - 22, 46, 46, g=g, width=1.8)
    s.cursor(cursor, clicks=(click,), hand=hand)


def react_zowie():
    """TL 1259-1332: LOVE IT! → ZOWIE! with hearts rising."""
    f0, fe, h = 1259, 1268, 1315
    t = _p("reaccion-corazones", "Botón LOVE IT! con corazones que suben", "LOVE IT! button with rising hearts",
           18036, span(f0, fe, h, 0.9), "redes", ["reacción", "corazones", "cursor", "botón"], thumb=2.0)
    s = Q(t, f0, fe, h, "tl", 0.9)
    reaction(s, (430, 288, 606, 348), RED, "LOVE IT!", (461, 307, 575, 329), "ZOWIE!", (460, 307, 575, 329), 1285,
             "heart", [(1268, 560, 400), (1278, 525, 330), (1285, 520, 322), (1292, 525, 332), (1302, 545, 380)],
             False)
    return t


def react_done():
    """TR 1264-1336: LIKE THIS → DONE! with thumbs rising."""
    f0, fe, h = 1264, 1273, 1318
    t = _p("reaccion-pulgares", "Botón LIKE THIS con pulgares que suben", "LIKE THIS button with rising thumbs",
           18037, span(f0, fe, h, 0.9), "redes", ["reacción", "me gusta", "cursor", "botón"], thumb=2.0)
    s = Q(t, f0, fe, h, "tr", 0.9)
    reaction(s, (1297, 290, 1487, 350), BLUE, "LIKE THIS", (1330, 309, 1454, 331), "DONE!", (1342, 309, 1441, 331),
             1290, "thumb", [(1272, 1440, 410), (1282, 1396, 336), (1290, 1392, 326), (1297, 1396, 336),
                            (1307, 1420, 390)], True)
    return t


def react_cool():
    """BL 1266-1340: YOUR ICON → ITS COOL! with green stars rising."""
    f0, fe, h = 1266, 1275, 1322
    t = _p("reaccion-estrellas", "Botón con estrellas verdes que suben", "Button with rising green stars", 18038,
           span(f0, fe, h, 0.9), "redes", ["reacción", "estrellas", "cursor", "botón"], thumb=2.0)
    s = Q(t, f0, fe, h, "bl", 0.9)
    reaction(s, (415, 788, 625, 848), GREEN, "YOUR ICON", (444, 807, 595, 829), "ITS COOL!", (444, 807, 595, 829),
             1295, "star", [(1278, 560, 910), (1288, 524, 834), (1295, 520, 826), (1302, 524, 836),
                            (1312, 550, 890)], True)
    return t


def react_thanks():
    """BR 1269-1342: DONATE → THANKS! with coins rising."""
    f0, fe, h = 1269, 1278, 1325
    t = _p("reaccion-monedas", "Botón DONATE con monedas que suben", "DONATE button with rising coins", 18039,
           span(f0, fe, h, 0.9), "redes", ["reacción", "donar", "cursor", "botón"], thumb=2.0)
    s = Q(t, f0, fe, h, "br", 0.9)
    reaction(s, (1308, 790, 1484, 850), YELLOW, "DONATE", (1340, 809, 1452, 831), "THANKS!", (1328, 809, 1463, 831),
             1298, "coin", [(1282, 1480, 910), (1291, 1405, 840), (1298, 1400, 830), (1305, 1405, 845),
                            (1316, 1420, 900)], False, txt=INK)
    return t


# =============================================================================================================
# GRID 11 (53.3-56.6 s): counters (icon + tag that counts up)
# =============================================================================================================
def _rebase(obj, cut):
    """Moves every keyframe list in obj (recursively) `cut` µs earlier, dropping those before 0."""
    if isinstance(obj, dict):
        if "keyframes" in obj and isinstance(obj["keyframes"], list) and obj["keyframes"] and \
                isinstance(obj["keyframes"][0], dict) and "timeUs" in obj["keyframes"][0]:
            kfs = obj["keyframes"]
            kept = [dict(kf, timeUs=kf["timeUs"] - cut) for kf in kfs if kf["timeUs"] - cut >= 0]
            if not kept or kept[0]["timeUs"] > 0:
                before = [kf for kf in kfs if kf["timeUs"] - cut < 0]
                if before:
                    kept.insert(0, dict(before[-1], timeUs=0))
            obj["keyframes"] = kept
        for v in obj.values():
            _rebase(v, cut)
    elif isinstance(obj, list):
        for v in obj:
            _rebase(v, cut)


def delay_clip(s, clip, frame):
    """Starts a full-length clip at reference frame `frame` (its keys stay where they were on the timeline), so a
    text counter starts counting there."""
    t0 = max(0.0, (frame - s.f0) / SRC)
    cut = round(t0 * 1_000_000)
    clip["timelineStartUs"] += cut
    clip["timelineDurationUs"] -= cut
    clip["srcOutUs"] = clip["timelineDurationUs"]
    for key in ("x", "y", "width", "height", "opacity", "rotation", "textStyle"):
        if key in clip:
            _rebase(clip[key], cut)
    return clip


def counter_icon(s, name, cx, cy, w, h, path, colour, tag, tag_ink, value, click, frames, cursor, hand,
                 kind="rectangle"):
    """A white outline icon pops in; a click fills it with colour and a white tag pops at its corner, counting up."""
    pr = press(s, click, 0.12)
    s.icon(f"{name} (sombra)", solid(SHADOW), cx + 8, cy + 8, w, h,
           g=lambda fr, u: (pop(fr, s.f0, 6) * pr(u), s.after(click)(fr, u)), path=path, kind=kind)
    s.icon(name, [fill(WHITE), stroke(INK, 2.5 * s.sc, "center")], cx, cy, w, h,
           g=lambda fr, u: (pop(fr, s.f0, 6) * pr(u), s.before(click)(fr, u)), path=path, kind=kind)
    s.icon(f"{name} (color)", [fill(colour), stroke(INK, 2.5 * s.sc, "center")], cx, cy, w, h,
           g=lambda fr, u: (pop(fr, s.f0, 6) * pr(u) * (1 + 0.15 * math.sin(math.pi * lin(s.R(u), click, 6))),
                            s.after(click)(fr, u)), path=path, kind=kind)
    x0, y0, x1, y1 = tag
    tcx, tcy = (x0 + x1) / 2, (y0 + y1) / 2

    def tg(fr, u):
        q = pop(s.R(u), click + 1, 6, 0.15) if fr >= s.fe - 1 else 0.0
        return q, 1.0 if q > 0.01 else 0.0, -(tcx - cx) * 0.3 * (1 - min(1, q)), -(tcy - cy) * 0.3 * (1 - min(1, q)), 0
    s.icon(f"{name} (etiqueta)", [fill(WHITE), stroke(INK, 2 * s.sc)], tcx, tcy, x1 - x0, y1 - y0, g=tg, radius=6)
    c = s.txt(str(value), tag_ink, 800, INK, "Número", align="center",
              op=lambda fr, u: (1.0 if s.R(u) >= click + 3 else 0.0) * (1.0 if fr >= s.fe - 1 else 0.0))
    s.counter(c, 1, value, click + 3, frames)
    delay_clip(s, c, click + 3)
    s.cursor(cursor, clicks=(click,), hand=hand)


def count_heart():
    """TL 1334-1400: a white heart; the arrow clicks it, it turns red and a tag counts up to 200."""
    f0, fe, h = 1334, 1341, 1388
    t = _p("contador-corazon", "Corazón con contador de me gusta", "Heart with a likes counter", 18040,
           span(f0, fe, h, 1.2), "redes", ["contador", "me gusta", "corazón", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "tl", 1.2)
    counter_icon(s, "Corazón", 515, 290, 118, 105, HEART, RED, (542, 231, 628, 270), (557, 241, 608, 260), 200, 1361,
                 11, [(1340, 600, 330), (1352, 525, 300), (1361, 518, 292), (1368, 525, 305), (1378, 560, 350)],
                 False)
    return t


def count_follower():
    """TR 1339-1405: a white person; a hand clicks it, it turns blue and a tag counts up to 80 followers."""
    f0, fe, h = 1339, 1346, 1393
    t = _p("contador-seguidores", "Persona con contador de seguidores", "Person with a followers counter", 18041,
           span(f0, fe, h, 1.2), "redes", ["contador", "seguidores", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "tr", 1.2)
    counter_icon(s, "Persona", 1393, 290, 90, 115, PERSON, BLUE, (1402, 220, 1469, 260), (1417, 230, 1454, 250), 80,
                 1364, 11, [(1345, 1470, 330), (1356, 1400, 305), (1364, 1395, 298), (1371, 1400, 310),
                            (1381, 1430, 350)], True)
    return t


def count_comments():
    """BL 1343-1410: a white comment bubble; a hand clicks it, it turns light blue and a tag counts up to 40."""
    f0, fe, h = 1343, 1350, 1397
    t = _p("contador-comentarios", "Burbuja con contador de comentarios", "Bubble with a comments counter", 18042,
           span(f0, fe, h, 1.2), "redes", ["contador", "comentarios", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "bl", 1.2)
    path = poly([(0, 8), (8, 0), (92, 0), (100, 8), (100, 82), (92, 88), (16, 88), (4, 100), (6, 88), (0, 82)])
    counter_icon(s, "Comentarios", 520, 790, 128, 108, path, "#69D6E8", (541, 720, 609, 760), (556, 730, 594, 750),
                 40, 1367, 11, [(1350, 600, 840), (1360, 528, 800), (1367, 522, 792), (1374, 528, 805),
                                (1384, 560, 850)], True)
    return t


def count_thumbs():
    """BR 1346-1415: a white thumb; the arrow clicks it, it turns yellow and a tag counts up to 800."""
    f0, fe, h = 1346, 1353, 1402
    t = _p("contador-pulgar", "Pulgar con contador de me gusta", "Thumb with a likes counter", 18043,
           span(f0, fe, h, 1.2), "redes", ["contador", "me gusta", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "br", 1.2)
    counter_icon(s, "Pulgar", 1395, 792, 115, 105, THUMB, YELLOW, (1420, 750, 1510, 790), (1436, 760, 1494, 780),
                 800, 1370, 12, [(1352, 1480, 840), (1362, 1405, 805), (1370, 1398, 796), (1377, 1405, 810),
                                 (1388, 1440, 850)], False)
    return t


# =============================================================================================================
# GRID 12 (56.3-59.8 s): notification tags
# =============================================================================================================
def tag_path(w, h, tail_x, tail_h, r=8.0, tw=26.0):
    """A rounded box w × h with a pointed tail tail_h below at tail_x (all px), on 0..100 of (w, h + tail_h)."""
    H = h + tail_h
    X = lambda x: 100 * x / w  # noqa: E731
    Y = lambda y: 100 * y / H  # noqa: E731
    c = 0.45
    return " ".join([
        f"M {X(0):.2f} {Y(r):.2f}",
        f"C {X(0):.2f} {Y(r * c):.2f} {X(r * c):.2f} {Y(0):.2f} {X(r):.2f} {Y(0):.2f}",
        f"L {X(w - r):.2f} {Y(0):.2f}",
        f"C {X(w - r * c):.2f} {Y(0):.2f} {X(w):.2f} {Y(r * c):.2f} {X(w):.2f} {Y(r):.2f}",
        f"L {X(w):.2f} {Y(h - r):.2f}",
        f"C {X(w):.2f} {Y(h - r * c):.2f} {X(w - r * c):.2f} {Y(h):.2f} {X(w - r):.2f} {Y(h):.2f}",
        f"L {X(tail_x + tw / 2):.2f} {Y(h):.2f}", f"L {X(tail_x):.2f} {Y(H):.2f}",
        f"L {X(tail_x - tw / 2):.2f} {Y(h):.2f}",
        f"L {X(r):.2f} {Y(h):.2f}",
        f"C {X(r * c):.2f} {Y(h):.2f} {X(0):.2f} {Y(h - r * c):.2f} {X(0):.2f} {Y(h - r):.2f}", "Z"])


CHATICON = poly([(0, 10), (10, 0), (90, 0), (100, 10), (100, 70), (90, 80), (30, 80), (8, 100), (12, 80), (10, 80),
                 (0, 70)])
PERSON_F = circ(50, 26, 24) + " M 6 100 C 6 68 24 56 50 56 C 76 56 94 68 94 100 Z"


def notif(s, body, tail_tip, colour, items, cursor, hand):
    """A notification tag that pops in tilted and settles; items = [(kind, cx, cy, w, h, colour, a, b, ink, txt,
    click)]: an icon and a number that goes a → b when the icon is clicked."""
    x0, y0, x1, y1 = body
    tx, ty = tail_tip
    w, h, th = x1 - x0, y1 - y0, ty - y1
    cx, cy = (x0 + x1) / 2, (y0 + ty) / 2
    px, py = tx, ty  # it pops about its tail tip

    def tilt(fr):
        q = lin(fr, s.f0, 10)
        return -18 * (1 - q) * math.cos(q * math.pi * 1.5) if q < 1 else 0.0

    def place(x, y, fr):
        sc = pop(fr, s.f0, 8, 0.12)
        a = math.radians(tilt(fr))
        dx, dy = (x - px) * sc, (y - py) * sc
        return px + dx * math.cos(a) - dy * math.sin(a), py + dx * math.sin(a) + dy * math.cos(a), sc

    def g(fr, u):
        x, y, sc = place(cx, cy, fr)
        return x, y, w * max(sc, 1e-3), (h + th) * max(sc, 1e-3), tilt(fr), 1.0 if fr >= s.f0 else 0.0
    s.shp("Etiqueta", [hard(8 * s.sc, 8 * s.sc), fill(colour), stroke(INK, 2.5 * s.sc, "center")], g,
          path=tag_path(w, h, tx - x0, th), base=(w, h + th))
    for j, (kind, ix, iy, iw, ih, icol, a, b, ink, tcol, click) in enumerate(items):
        path = {"heart": HEART, "chat": CHATICON, "person": PERSON_F}[kind]

        def ig(fr, u, ix=ix, iy=iy, iw=iw, ih=ih, click=click):
            x, y, sc = place(ix, iy, fr)
            bump = 1 + 0.3 * math.sin(math.pi * lin(s.R(u), click, 6))
            return x, y, iw * max(sc, 1e-3) * bump, ih * max(sc, 1e-3) * bump, tilt(fr), 1.0 if fr >= s.f0 + 3 else 0.0
        s.shp(f"Icono {j + 1}", solid(icol), ig, path=path, base=(iw, ih))
        mx, my = (ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2
        for word, st, nm in ((a, s.before(click), f"Número {j + 1}"), (b, s.after(click), f"Número {j + 1} (nuevo)")):
            s.txt(word, ink, 800, tcol, nm,
                  g=lambda fr, u, st=st, mx=mx, my=my: (lambda p: (p[0] - mx, p[1] - my, p[2], tilt(fr),
                                                                   st(fr, u) * (1.0 if fr >= s.f0 + 3 else 0.0)))(
                      place(mx, my, fr)))
    s.cursor(cursor, clicks=tuple(it[-1] for it in items), hand=hand)


def notif_likes():
    """TL 1406-1495: a red tag with a heart and 85; the arrow clicks the heart: 86."""
    f0, fe, h = 1406, 1416, 1478
    t = _p("aviso-me-gusta", "Aviso de me gusta", "Likes notification", 18044, span(f0, fe, h, 1.4), "redes",
           ["notificación", "me gusta", "contador", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "tl", 1.4)
    notif(s, (423, 209, 605, 291), (520, 325), RED,
          [("heart", 474, 249, 44, 40, WHITE, "85", "86", (520, 234, 577, 266), WHITE, 1435)],
          [(1414, 540, 330), (1426, 480, 262), (1435, 476, 254), (1442, 482, 262), (1455, 520, 320)], False)
    return t


def notif_comments():
    """TR 1410-1498: a blue tag with a comment icon and 15; a hand clicks it: 16."""
    f0, fe, h = 1410, 1420, 1481
    t = _p("aviso-comentarios", "Aviso de comentarios", "Comments notification", 18045, span(f0, fe, h, 1.4),
           "redes", ["notificación", "comentarios", "contador", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "tr", 1.4)
    notif(s, (1311, 211, 1493, 293), (1408, 327), BLUE,
          [("chat", 1362, 253, 42, 36, WHITE, "15", "16", (1408, 237, 1453, 269), WHITE, 1440)],
          [(1418, 1420, 330), (1430, 1368, 266), (1440, 1364, 258), (1447, 1370, 266), (1460, 1400, 330)], True)
    return t


def notif_followers():
    """BL 1414-1502: a light blue tag with a person and 26; a hand clicks it: 27."""
    f0, fe, h = 1414, 1424, 1485
    t = _p("aviso-seguidores", "Aviso de seguidores", "Followers notification", 18046, span(f0, fe, h, 1.4), "redes",
           ["notificación", "seguidores", "contador", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "bl", 1.4)
    notif(s, (429, 709, 611, 791), (526, 826), "#69D6E8",
          [("person", 480, 750, 32, 40, WHITE, "26", "27", (525, 735, 578, 767), WHITE, 1442)],
          [(1424, 520, 830), (1434, 484, 762), (1442, 482, 756), (1449, 486, 764), (1460, 520, 830)], True)
    return t


def notif_double():
    """BR 1417-1505: a yellow tag with a heart (71) and a person (14); the arrow clicks both: 72 and 15."""
    f0, fe, h = 1417, 1427, 1487
    t = _p("aviso-doble", "Aviso de me gusta y seguidores", "Likes and followers notification", 18047,
           span(f0, fe, h, 1.4), "redes", ["notificación", "me gusta", "seguidores", "cursor"], thumb=2.6)
    s = Q(t, f0, fe, h, "br", 1.4)
    notif(s, (1249, 709, 1551, 791), (1406, 826), YELLOW,
          [("heart", 1300, 750, 44, 40, WHITE, "71", "72", (1339, 735, 1393, 767), WHITE, 1447),
           ("person", 1435, 750, 32, 40, INK, "14", "15", (1464, 735, 1512, 767), INK, 1470)],
          [(1428, 1360, 830), (1438, 1304, 762), (1447, 1302, 756), (1456, 1380, 770), (1463, 1438, 760),
           (1470, 1436, 756), (1476, 1440, 764), (1486, 1470, 830)], False)
    return t


# =============================================================================================================
# GRID 13 (59.7-62.8 s): round social badges that swap on a click
# =============================================================================================================
ZIG = poly([(50 + (50 if i % 2 == 0 else 44) * math.cos(math.radians(-90 + 360 * i / 56)),
             50 + (50 if i % 2 == 0 else 44) * math.sin(math.radians(-90 + 360 * i / 56))) for i in range(56)])
FB = ("M 56 100 L 56 58 L 70 58 L 72 42 L 56 42 L 56 32 C 56 27 58 24 64 24 L 72 24 L 72 9 C 69 8 63 8 58 8 "
      "C 45 8 38 16 38 29 L 38 42 L 26 42 L 26 58 L 38 58 L 38 100 Z")


def badge_face(s, cx, cy, d, shape, colour, appear, st, name, spin=True):
    """One face of a round badge (circle or zigzag): pops in turning; st(fr, u) = shown or not."""
    def g(fr, u):
        return pop(fr, appear, 8, 0.15), st(fr, u) * (1.0 if fr >= appear else 0.0), 0, 0, \
            (-90 * (1 - min(1.0, lin(fr, appear, 8)))) if spin else 0
    s.icon(f"{name} (sombra)", solid(SHADOW), cx + 7, cy + 7, d, d, g=g,
           kind="ellipse" if shape == "circle" else "rectangle", path=None if shape == "circle" else ZIG)
    s.icon(name, [fill(colour), stroke(INK, 2.5 * s.sc, "center")], cx, cy, d, d, g=g,
           kind="ellipse" if shape == "circle" else "rectangle", path=None if shape == "circle" else ZIG)
    return g


def swap_badge(s, cx, cy, d, a, b, click, cursor, hand):
    """a / b = (shape, colour, content): content is ("path", path, w, h, colour) or ("text", lines, colour).
    The badge shows a; a click flips it to b with a little press and pop."""
    pr = press(s, click, 0.12)
    for side, st in ((a, s.before(click)), (b, s.after(click))):
        shape, colour, content = side
        g0 = badge_face(s, cx, cy, d, shape, colour, s.f0, st, "Insignia" if side is a else "Insignia (después)")

        def g(fr, u, g0=g0):
            v = g0(fr, u)
            q = lin(s.R(u), click, 7)
            bump = 1 + 0.12 * math.sin(math.pi * q) if s.R(u) >= click else pr(u)
            return (v[0] * bump,) + v[1:]
        if content[0] == "path":
            _, path, w, h, col = content
            s.icon("Glifo" if side is a else "Glifo (después)", solid(col), cx, cy, w, h, g=g, path=path)
        elif content[0] == "insta":
            col = content[1]
            outline_icon(s, "Glifo" if side is a else "Glifo (después)", INSTA, cx, cy, 64, 64, g=g, colour=col,
                         width=6)
        else:
            _, lines, col = content
            for i, (word, ink) in enumerate(lines):
                s.txt(word, ink, 800, col, f"Texto {i + 1}" if side is a else f"Texto {i + 1} (después)",
                      g=lambda fr, u, g=g, ink=ink: (lambda v: (0, 0, v[0], 0, v[1]))(g(fr, u)))
    s.cursor(cursor, clicks=(click,), hand=hand)


def badge_bird():
    """TL 1499-1570: a blue round bird badge; the arrow clicks it and it turns white with a grey bird."""
    f0, fe, h = 1499, 1508, 1553
    t = _p("insignia-pajaro", "Botón redondo con pájaro", "Round bird button", 18048, span(f0, fe, h, 1.4), "redes",
           ["insignia", "redes", "cursor"], thumb=1.8)
    s = Q(t, f0, fe, h, "tl", 1.4)
    swap_badge(s, 515, 290, 140, ("circle", "#5FCDE4", ("path", BIRD, 74, 62, WHITE)),
               ("circle", WHITE, ("path", BIRD, 74, 62, "#9A9A9A")), 1528,
               [(1510, 600, 330), (1520, 545, 310), (1528, 540, 304), (1536, 548, 315), (1548, 600, 360)], False)
    return t


def badge_follow():
    """TR 1504-1575: a white zigzag badge with a green play sign; a hand clicks it and it turns green: FOLLOW."""
    f0, fe, h = 1504, 1513, 1557
    t = _p("insignia-seguir", "Insignia que se vuelve FOLLOW", "Badge that turns into FOLLOW", 18049,
           span(f0, fe, h, 1.4), "redes", ["insignia", "seguir", "cursor"], thumb=1.8)
    s = Q(t, f0, fe, h, "tr", 1.4)
    swap_badge(s, 1400, 290, 135, ("zig", WHITE, ("path", TRIANGLE, 44, 50, GREEN)),
               ("zig", GREEN, ("text", [("FOLLOW", (1352, 280, 1448, 300))], WHITE)), 1533,
               [(1515, 1480, 340), (1525, 1430, 318), (1533, 1426, 312), (1541, 1432, 320), (1552, 1470, 360)],
               True)
    return t


def badge_join():
    """BL 1507-1580: a blue zigzag JOIN US! badge; a hand clicks it and it turns white with an «f»."""
    f0, fe, h = 1507, 1516, 1561
    t = _p("insignia-unete", "Insignia ÚNETE con clic", "JOIN US badge with a click", 18050, span(f0, fe, h, 1.4),
           "redes", ["insignia", "únete", "cursor"], thumb=1.8)
    s = Q(t, f0, fe, h, "bl", 1.4)
    swap_badge(s, 515, 790, 150, ("zig", BLUE, ("text", [("JOIN", (476, 760, 556, 783)), ("US!", (490, 795, 544, 818))],
                                                 WHITE)),
               ("zig", WHITE, ("path", FB, 36, 62, BLUE)), 1537,
               [(1519, 600, 850), (1529, 540, 818), (1537, 536, 812), (1545, 542, 820), (1556, 580, 870)], True)
    return t


def badge_insta():
    """BR 1512-1585: a red round camera badge; the arrow clicks it and it turns into a red JOIN US! badge."""
    f0, fe, h = 1512, 1521, 1564
    t = _p("insignia-camara", "Botón redondo con cámara", "Round camera button", 18051, span(f0, fe, h, 1.4), "redes",
           ["insignia", "redes", "cursor"], thumb=1.8)
    s = Q(t, f0, fe, h, "br", 1.4)
    swap_badge(s, 1398, 790, 145, ("circle", RED, ("insta", WHITE)),
               ("zig", RED, ("text", [("JOIN", (1360, 762, 1436, 784)), ("US!", (1374, 796, 1424, 818))], WHITE)),
               1540, [(1524, 1490, 850), (1533, 1428, 822), (1540, 1424, 816), (1548, 1430, 824), (1560, 1470, 870)],
               False)
    return t


# =============================================================================================================
# GRID 14 (62.5-65.8 s): badges with pictures and words
# =============================================================================================================
def face(s, cx, cy, d, shape, colour, st, name, spin=-90.0):
    """A badge face (circle, zigzag or rounded square) that pops in turning; returns its g(fr, u)."""
    def g(fr, u):
        return pop(fr, s.f0, 8, 0.15), st(fr, u) * (1.0 if fr >= s.f0 else 0.0), 0, 0, \
            spin * (1 - min(1.0, lin(fr, s.f0, 8)))
    kw = {"ellipse": dict(kind="ellipse"), "zig": dict(path=ZIG), "square": dict(radius=8)}[shape]
    s.icon(f"{name} (sombra)", solid(SHADOW), cx + 7, cy + 7, d, d, g=g, **kw)
    if colour:
        s.icon(name, [fill(colour), stroke(INK, 2.5 * s.sc, "center")], cx, cy, d, d, g=g, **kw)
    return g


def words_on(s, lines, colour, g, suffix=""):
    for i, (word, ink) in enumerate(lines):
        s.txt(word, ink, 800, colour, f"Texto {i + 1}{suffix}",
              g=lambda fr, u, ink=ink: (lambda v: (0, 0, v[0], v[4], v[1]))(g(fr, u)))


def bumped(s, g0, click):
    pr = press(s, click, 0.12)

    def g(fr, u):
        v = g0(fr, u)
        q = lin(s.R(u), click, 7)
        bump = 1 + 0.12 * math.sin(math.pi * q) if s.R(u) >= click else pr(u)
        return (v[0] * bump,) + v[1:]
    return g


def photo_in(s, sample, cx, cy, d, g, square=False, name="Foto", label="Tu foto"):
    """A photo slot (round or square) that follows a badge's g (scale, op, _, _, rot)."""
    t = s.t
    D = d * s.sc
    box = Box(s.X(cx) - D / 2, s.Y(cy) - D / 2, D, D)
    track = t.track("video", name)
    us = frames_of(s.dur)
    clip = t.photo(track, sample, 0.0, s.dur, box, [(u, {"s": max(1e-3, g(s.frame(u), u)[0])}, "linear") for u in us],
                   label=label)
    clip["opacity"] = keys([(u, round(g(s.frame(u), u)[1], 3), "linear") for u in us])
    if any(abs(g(s.frame(u), u)[4]) > 1e-3 for u in us):
        clip["rotation"] = keys([(u, round(g(s.frame(u), u)[4], 3), "linear") for u in us])
    if square:
        t.mask(track, clip, "rectangle")
    else:
        t.mask(track, clip, "ellipse")
    s.icon(f"{name} (borde)", [nofill(), stroke(INK, 2.5 * s.sc, "center")], cx, cy, d, d, g=g,
           kind="rectangle" if square else "ellipse", radius=8 if square else 0)


def badge_like_this():
    """TL 1574-1640: a white zigzag badge with a round picture; the arrow clicks it: red LIKE THIS!."""
    f0, fe, h = 1574, 1583, 1624
    t = _p("insignia-like-this", "Insignia con foto que pasa a LIKE THIS!", "Picture badge that turns LIKE THIS!",
           18052, span(f0, fe, h, 1.4), "redes", ["insignia", "me gusta", "cursor", "foto"], thumb=2.0)
    s = Q(t, f0, fe, h, "tl", 1.4)
    c = 1601
    ga = bumped(s, face(s, 522, 290, 165, "zig", WHITE, s.before(c), "Insignia"), c)
    photo_in(s, "ig3-donut-01", 522, 290, 96, ga)
    gb = bumped(s, face(s, 522, 290, 165, "zig", RED, s.after(c), "Insignia (después)"), c)
    words_on(s, [("LIKE", (487, 259, 554, 280)), ("THIS!", (482, 296, 560, 318))], WHITE, gb)
    s.cursor([(1583, 620, 380), (1593, 562, 352), (1601, 556, 344), (1609, 560, 355), (1620, 590, 400)], clicks=(c,))
    return t


def badge_photo():
    """TR 1578-1645: a square picture that turns in; a hand taps it."""
    f0, fe, h = 1578, 1587, 1629
    t = _p("insignia-foto", "Foto cuadrada con clic", "Square picture with a tap", 18053, span(f0, fe, h, 1.4),
           "redes", ["foto", "avatar", "cursor"], thumb=2.0)
    s = Q(t, f0, fe, h, "tr", 1.4)
    c = 1605
    g = bumped(s, face(s, 1400, 291, 140, "square", None, lambda fr, u: 1.0, "Foto", spin=-45), c)
    photo_in(s, "h-portrait-03", 1400, 291, 140, g, square=True)
    s.burst(1420, 340, c, r0=20, r1=34, ln=9)
    s.cursor([(1588, 1480, 400), (1597, 1428, 352), (1605, 1424, 346), (1613, 1430, 354), (1625, 1460, 400)],
             clicks=(c,), hand=True)
    return t


def badge_click_here():
    """BL 1583-1650: a light blue CLICK HERE square that turns in; a hand clicks it: grey GOOD JOB!."""
    f0, fe, h = 1583, 1592, 1632
    t = _p("insignia-click-here", "Cuadro CLICK HERE que pasa a GOOD JOB!", "CLICK HERE square that turns GOOD JOB!",
           18054, span(f0, fe, h, 1.4), "redes", ["botón", "cursor"], thumb=2.0)
    s = Q(t, f0, fe, h, "bl", 1.4)
    c = 1612
    ga = bumped(s, face(s, 520, 790, 140, "square", "#5FCDE4", s.before(c), "Cuadro", spin=-45), c)
    words_on(s, [("CLICK", (478, 766, 562, 786)), ("HERE", (482, 797, 558, 817))], INK, ga)
    gb = bumped(s, face(s, 520, 790, 140, "square", GREY, s.after(c), "Cuadro (después)", spin=-45), c)
    words_on(s, [("GOOD", (473, 766, 567, 786)), ("JOB!", (484, 797, 555, 817))], WHITE, gb, " (después)")
    s.burst(530, 800, c, r0=44, r1=70, ln=10)
    s.cursor([(1594, 620, 870), (1604, 548, 830), (1612, 542, 822), (1620, 548, 832), (1630, 590, 880)],
             clicks=(c,), hand=True)
    return t


def badge_get_ready():
    """BR 1587-1655: a yellow GET READY zigzag; the arrow clicks it and it shows a round picture."""
    f0, fe, h = 1587, 1596, 1635
    t = _p("insignia-get-ready", "Insignia GET READY con foto", "GET READY badge with a picture", 18055,
           span(f0, fe, h, 1.4), "redes", ["insignia", "cursor", "foto"], thumb=2.0)
    s = Q(t, f0, fe, h, "br", 1.4)
    c = 1615
    ga = bumped(s, face(s, 1400, 792, 150, "zig", YELLOW, s.before(c), "Insignia"), c)
    words_on(s, [("GET", (1370, 769, 1424, 789)), ("READY", (1350, 796, 1445, 816))], INK, ga)
    gb = bumped(s, face(s, 1400, 792, 150, "zig", "#C8B8E8", s.after(c), "Insignia (después)"), c)
    photo_in(s, "h-portrait-04", 1400, 792, 100, gb)
    s.burst(1400, 805, c, r0=46, r1=72, ln=10)
    s.cursor([(1598, 1480, 860), (1607, 1428, 828), (1615, 1422, 820), (1623, 1428, 830), (1634, 1470, 880)],
             clicks=(c,))
    return t


# =============================================================================================================
# GRID 15 (65.7-69.0 s): switches
# =============================================================================================================
def slide_knob(s, click, a, b, n=6):
    """x of a knob that slides from a to b after the click (real time)."""
    return lambda u: a + (b - a) * k(s.R(u), click, n)


def toggle_on():
    """TL 1645-1715: TURN ON over a grey switch; the arrow clicks it, it turns red and the knob slides right."""
    f0, fe, h = 1645, 1657, 1700
    t = _p("interruptor-encender", "Interruptor TURN ON", "TURN ON switch", 18056, span(f0, fe, h, 1.1),
           "elementos", ["interruptor", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "tl", 1.1)
    c = 1673
    pr = press(s, c, 0.06)
    for col, st, nm in ((GREY, s.before(c), "Interruptor"), (RED, s.after(c), "Interruptor (encendido)")):
        s.icon(nm, s.card_l(col, 3.0, 8.0), 516, 259, 132, 76, g=lambda fr, u, st=st: (pop(fr, f0, 7) * pr(u),
                                                                                      st(fr, u)), radius=38)
    kx = slide_knob(s, c, 488, 544)
    s.shp("Perilla", [fill(WHITE), stroke(INK, 2.5 * s.sc)],
          lambda fr, u: (516 + (kx(u) - 516) * pop(fr, f0, 7), 259, 60 * pop(fr, f0 + 2, 7), 60 * pop(fr, f0 + 2, 7),
                         0, 1.0 if fr >= f0 + 2 else 0.0), kind="ellipse", base=(60, 60))
    s.txt("TURN ON", (438, 171, 593, 193), 800, op=lambda fr, u: k(fr, 1653, 4), name="Título")
    s.cursor([(1655, 600, 330), (1665, 525, 275), (1673, 520, 266), (1680, 526, 280), (1692, 560, 330)], clicks=(c,))
    return t


def radio_select():
    """TR 1650-1720: a round option and SELECT; a hand clicks it and a blue dot fills it."""
    f0, fe, h = 1650, 1660, 1705
    t = _p("opcion-seleccionar", "Opción SELECT", "SELECT option", 18057, span(f0, fe, h, 1.1), "elementos",
           ["opción", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "tr", 1.1)
    c = 1678
    pr = press(s, c, 0.1)
    s.icon("Opción", s.card_l(WHITE, 3.0, 7.0), 1290, 270, 68, 68, g=lambda fr, u: (pop(fr, f0, 6) * pr(u), 1.0),
           kind="ellipse")
    s.icon("Opción (punto)", [fill(BLUE)], 1290, 270, 30, 30,
           g=lambda fr, u: (pop(s.R(u), c + 1, 5, 0.25) if fr >= f0 + 3 else 0.0, s.after(c)(fr, u)), kind="ellipse")
    s.burst(1290, 270, c, r0=42, r1=62, ln=10)
    s.txt("SELECT", (1366, 255, 1522, 286), 800, slide=(1653, 7, 60), name="Texto")
    s.cursor([(1660, 1330, 360), (1670, 1295, 290), (1678, 1292, 280), (1685, 1296, 292), (1697, 1320, 340)],
             clicks=(c,), hand=True)
    return t


def checkbox_checked():
    """BL 1652-1722: CHECKED and an empty box that turns in; a hand clicks it: green with a check."""
    f0, fe, h = 1652, 1665, 1708
    t = _p("casilla-marcada", "Casilla CHECKED", "CHECKED checkbox", 18058, span(f0, fe, h, 1.1), "elementos",
           ["casilla", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "bl", 1.1)
    c = 1682
    pr = press(s, c, 0.1)
    s.txt("CHECKED", (343, 756, 548, 786), 800, slide=(1653, 8, 80), name="Texto")
    for col, st, nm in ((WHITE, s.before(c), "Casilla"), (GREEN, s.after(c), "Casilla (marcada)")):
        s.icon(nm, s.card_l(col, 3.0, 7.0), 613, 770, 66, 66,
               g=lambda fr, u, st=st: (pop(fr, 1656, 7) * pr(u), st(fr, u), 0, 0, -30 * (1 - lin(fr, 1656, 9))),
               radius=6)
    s.icon("Marca", [nofill(), stroke(INK, 5 * s.sc, "center")], 613, 769, 40, 36,
           g=lambda fr, u: (pop(s.R(u), c + 1, 5, 0.2) if fr >= 1658 else 0.0, s.after(c)(fr, u)), path=CHECK)
    s.cursor([(1665, 660, 860), (1674, 620, 790), (1682, 616, 782), (1690, 622, 800), (1702, 640, 880)],
             clicks=(c,), hand=True)
    return t


def switch_start():
    """BR 1657-1727: START KEY over a grey OFF switch; the arrow clicks it: yellow, ON, the knob slides right."""
    f0, fe, h = 1657, 1670, 1712
    t = _p("interruptor-on-off", "Interruptor START KEY ON/OFF", "START KEY ON/OFF switch", 18059,
           span(f0, fe, h, 1.1), "elementos", ["interruptor", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "br", 1.1)
    c = 1688
    pr = press(s, c, 0.05)
    for col, st, nm in (("#D9D9D9", s.before(c), "Interruptor"), (YELLOW, s.after(c), "Interruptor (encendido)")):
        s.icon(nm, s.card_l(col, 3.0, 8.0), 1396, 773, 188, 86,
               g=lambda fr, u, st=st: (pop(fr, f0, 7, 0.1) * pr(u), st(fr, u) * (1.0 if fr >= f0 else 0.0)), radius=10)
    kx = slide_knob(s, c, 1357, 1435)

    def knob(fr, u):
        q = k(fr, f0 + 3, 6)
        return kx(u), 773, 94 * q, 70 * q, 0, 1.0 if fr >= f0 + 3 else 0.0
    s.shp("Perilla (apagada)", [fill("#BDBDBD"), stroke(INK, 2.5 * s.sc)],
          lambda fr, u: knob(fr, u)[:5] + (knob(fr, u)[5] * s.before(c)(fr, u),), base=(94, 70), radius=8)
    s.shp("Perilla", [fill(WHITE), stroke(INK, 2.5 * s.sc)],
          lambda fr, u: knob(fr, u)[:5] + (knob(fr, u)[5] * s.after(c)(fr, u),), base=(94, 70), radius=8)
    s.txt("OFF", (1418, 765, 1460, 781), 500, op=lambda fr, u: k(fr, f0 + 6, 3) * s.before(c)(fr, u), name="Apagado")
    s.txt("ON", (1330, 762, 1373, 783), 500, op=lambda fr, u: s.after(c + 2)(fr, u) * (1.0 if fr >= f0 + 6 else 0.0),
          name="Encendido")
    s.txt("START KEY", (1282, 675, 1509, 704), 800, op=lambda fr, u: k(fr, f0 + 4, 4), name="Título")
    s.cursor([(1668, 1480, 880), (1679, 1405, 830), (1688, 1398, 822), (1696, 1404, 836), (1706, 1430, 890)],
             clicks=(c,))
    return t


# =============================================================================================================
# GRID 16 (68.8-72.3 s): buy, download and progress
# =============================================================================================================
def counting(s, text, ink, start, frames, weight=800, colour=INK, name="Porcentaje", gate=None):
    """A text that counts from 0 up to its number (suffix kept) from real frame start over `frames`."""
    gate = gate if gate is not None else s.fe - 1
    c = s.txt(text, ink, weight, colour, name, align="center",
              op=lambda fr, u: (1.0 if s.R(u) >= start else 0.0) * (1.0 if fr >= gate else 0.0))
    s.counter(c, 0, text, start, frames)
    c["textContent"] = text
    delay_clip(s, c, start)
    return c


def buy_now():
    """TL 1721-1806: a yellow BUY NOW; the arrow clicks it: grey THANK YOU, and «$250» floats up and fades."""
    f0, fe, h = 1721, 1730, 1794
    t = _p("comprar-gracias", "Botón comprar que da las gracias", "Buy button that says thank you", 18060,
           span(f0, fe, h, 1.0), "elementos", ["botón", "compra", "cursor"], thumb=2.0)
    s = Q(t, f0, fe, h, "tl", 1.0)
    c = 1748
    grow_btn(s, (397, 246, 639, 312), YELLOW, f0, 7, until=c)
    grow_btn(s, (397, 246, 639, 312), GREY, f0, 7, since=c, name="Botón (gracias)")
    centre_text(s, "BUY NOW", (446, 266, 590, 291), f0 + 2, 7, colour=INK, until=c)
    s.txt("THANK YOU", (418, 266, 619, 291), 800, WHITE, "Gracias",
          op=lambda fr, u: s.after(c)(fr, u) * k(fr, f0 + 3, 2))

    def rise(fr, u):
        rf = s.R(u)
        q = lin(rf, c + 1, 14)
        return 0, -30 * q, 1, 0, (min(1.0, q * 4) * (1 - max(0.0, (q - 0.5) / 0.5))) if rf >= c + 1 else 0.0
    s.txt("$250", (500, 196, 536, 208), 600, INK, "Precio", g=rise)
    s.cursor([(1730, 600, 350), (1740, 522, 296), (1748, 518, 288), (1755, 524, 300), (1765, 560, 350)], clicks=(c,))
    return t


def download_bar():
    """TR 1724-1810: a white DOWNLOAD button; a hand clicks it and it fills green 0 → 100 %."""
    f0, fe, h = 1724, 1732, 1798
    t = _p("descargar-barra", "Botón descargar con barra de progreso", "Download button with a progress bar", 18061,
           span(f0, fe, h, 1.0), "elementos", ["descarga", "progreso", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "tr", 1.0)
    c = 1752
    grow_btn(s, (1264, 248, 1528, 314), WHITE, f0, 7)
    centre_text(s, "DOWNLOAD", (1330, 270, 1462, 292), f0 + 2, 7, colour=INK, until=c)
    def bar(fr, u):
        half = 132 * (0.12 + 0.88 * k(fr, f0, 7))
        return 1396 - half, 248, 1396 - half + 2 * half * k(s.R(u), c + 2, 22), 314
    s.box("Progreso", [fill(GREEN), stroke(INK, 3 * s.sc)], bar,
          op=lambda fr, u: (1.0 if s.R(u) >= c + 2 else 0.0) * (1.0 if fr >= f0 else 0.0), radius=6)
    counting(s, "100%", (1366, 270, 1427, 295), c + 2, 22, gate=f0 + 5)
    s.cursor([(1733, 1460, 360), (1743, 1404, 296), (1752, 1398, 288), (1759, 1404, 300), (1770, 1440, 350)],
             clicks=(c,), hand=True)
    return t


def download_ring():
    """BL 1729-1815: a green round download button; a hand clicks it and a ring fills 0 → 100 %."""
    f0, fe, h = 1729, 1737, 1802
    t = _p("descargar-anillo", "Botón descargar con anillo de progreso", "Download button with a progress ring",
           18062, span(f0, fe, h, 1.0), "elementos", ["descarga", "progreso", "cursor"], thumb=2.6)
    s = Q(t, f0, fe, h, "bl", 1.0)
    c = 1755
    pr = press(s, c, 0.1)
    s.icon("Botón", s.card_l(GREEN, 3.0, 8.0), 520, 790, 132, 132,
           g=lambda fr, u: (pop(fr, f0, 7) * pr(u), s.before(c)(fr, u)), kind="ellipse")
    outline_icon(s, "Flecha", DOWNLOAD, 520, 790, 54, 54, g=lambda fr, u: (pop(fr, f0 + 2, 6) * pr(u),
                                                                         s.before(c)(fr, u)), colour=WHITE, width=5)
    s.icon("Anillo (fondo)", s.card_l(WHITE, 3.0, 8.0), 520, 790, 132, 132,
           g=lambda fr, u: (pop(s.R(u), c, 6, 0.1) if fr >= fe - 1 else 0.0, s.after(c)(fr, u)), kind="ellipse")
    n = 40
    for i in range(n):
        at = c + 2 + 22 * i / n
        s.icon(f"Anillo {i + 1}", [nofill(), stroke(GREEN, 14 * s.sc, "center")], 520, 790, 112, 112,
               g=lambda fr, u, at=at: (1.0, (1.0 if s.R(u) >= at else 0.0) * (1.0 if fr >= fe - 1 else 0.0)),
               path=arc(-90 + 360 * i / n - 0.6, -90 + 360 * (i + 1) / n + 0.6, 3))
    s.icon("Anillo (borde)", [nofill(), stroke(INK, 2.5 * s.sc, "center")], 520, 790, 84, 84,
           g=lambda fr, u: (1.0, s.after(c)(fr, u) * (1.0 if fr >= fe - 1 else 0.0)), kind="ellipse")
    counting(s, "100%", (488, 778, 552, 802), c + 2, 22)
    s.cursor([(1738, 620, 880), (1747, 528, 806), (1755, 524, 798), (1763, 530, 812), (1776, 565, 935)],
             clicks=(c,), hand=True)
    return t


def cart_price():
    """BR 1733-1818: a yellow cart button; the arrow clicks it: white with a yellow cart and «$100» above."""
    f0, fe, h = 1733, 1742, 1804
    t = _p("carrito-precio", "Botón de carrito con precio", "Cart button with a price", 18063,
           span(f0, fe, h, 1.0), "elementos", ["carrito", "compra", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "br", 1.0)
    c = 1762
    pr = press(s, c, 0.08)
    for col, st, nm in ((YELLOW, s.before(c), "Botón"), (WHITE, s.after(c), "Botón (después)")):
        s.icon(nm, s.card_l(col, 3.0, 8.0), 1396, 779, 132, 88,
               g=lambda fr, u, st=st: (pop(fr, f0, 7) * pr(u), st(fr, u)), radius=8)
    basket = "M 24 24 L 96 24 L 86 66 L 32 66 Z"
    for col, st, nm in ((WHITE, s.before(c), "Carrito"), (YELLOW, s.after(c), "Carrito (después)")):
        outline_icon(s, nm, basket, 1393, 778, 70, 55, g=lambda fr, u, st=st: (pop(fr, f0 + 2, 6) * pr(u), st(fr, u)),
                     colour=INK, width=3, filled=col)
    outline_icon(s, "Carrito (asa)", "M 2 8 L 18 8 L 32 66 " + circ(40, 86, 8) + " " + circ(78, 86, 8), 1393, 778,
                 70, 55, g=lambda fr, u: (pop(fr, f0 + 2, 6) * pr(u), 1.0), colour=INK, width=3)

    def price(fr, u):
        rf = s.R(u)
        q = k(rf, c + 1, 6)
        out = 1 - k(rf, c + 12, 6)
        return 0, 20 * (1 - q), 1, 0, (q * out) if fr >= fe - 1 else 0.0
    s.txt("$100", (1349, 657, 1443, 686), 800, INK, "Precio", g=price)
    s.cursor([(1745, 1480, 880), (1754, 1424, 820), (1762, 1420, 812), (1770, 1426, 826), (1782, 1460, 880)],
             clicks=(c,))
    return t


# =============================================================================================================
# GRID 17 (72.2-76.4 s): slider, subscribe bar, dialog, channel card
# =============================================================================================================
SPEAKER = "M 6 34 L 26 34 L 50 12 L 50 88 L 26 66 L 6 66 Z"
WAVES2 = "M 64 34 C 72 42 72 58 64 66 M 76 22 C 92 38 92 62 76 78"
MUTE = "M 64 38 L 88 62 M 88 38 L 64 62"


def make_noise():
    """TL 1809-1915: MAKE SOME NOISE over a volume slider; the arrow drags the knob all the way up."""
    f0, fe, h = 1809, 1820, 1908
    t = _p("volumen", "Control de volumen MAKE SOME NOISE", "MAKE SOME NOISE volume slider", 18064,
           span(f0, fe, h, 1.5), "elementos", ["volumen", "deslizador", "cursor"], thumb=3.0)
    s = Q(t, f0, fe, h, "tl", 1.5)
    unfold(s, (365, 240, 663, 318), f0, 7, "w", radius=8)
    s.txt("MAKE SOME", (353, 178, 560, 203), 800, op=lambda fr, u: k(fr, 1815, 4), name="Título")
    s.txt("NOISE", (571, 178, 675, 203), 800, BLUE, op=lambda fr, u: k(fr, 1816, 4), name="Título 2")
    drag0, drag1 = 1838, 1852
    kx = lambda u: 474 + (609 - 474) * k(s.R(u), drag0, drag1 - drag0)  # noqa: E731
    gate = lambda fr: 1.0 if fr >= 1814 else 0.0  # noqa: E731
    s.box("Riel", [fill(WHITE), stroke(INK, 2.5 * s.sc)], lambda fr, u: (459, 275, 459 + 181 * k(fr, 1814, 6), 283),
          op=lambda fr, u: gate(fr), radius=4)
    s.box("Riel (lleno)", [fill(BLUE), stroke(INK, 2.5 * s.sc)], lambda fr, u: (459, 275, max(461, kx(u)), 283),
          op=lambda fr, u: gate(fr), radius=4)
    s.icon("Perilla", [fill(BLUE), stroke(INK, 2.5 * s.sc)], 474, 279, 30, 30,
           g=lambda fr, u: (pop(fr, 1816, 5), 1.0, kx(u) - 474, 0, 0), kind="ellipse")
    s.icon("Altavoz", [fill(INK), stroke(INK, 1.5 * s.sc, "center")], 405, 279, 40, 36, g=pop_g(1814, 5), path=SPEAKER)
    outline_icon(s, "Altavoz (mudo)", MUTE, 405, 279, 40, 36,
                 g=lambda fr, u: (pop(fr, 1814, 5), 1.0 - k(s.R(u), drag0 + 2, 3)), width=3)
    outline_icon(s, "Altavoz (sonido)", WAVES2, 405, 279, 40, 36,
                 g=lambda fr, u: (pop(fr, 1814, 5), k(s.R(u), drag0 + 2, 3)), width=3)
    s.cursor([(1825, 520, 330), (1834, 478, 290), (1838, 476, 284), (1852, 611, 284), (1858, 615, 292),
              (1870, 650, 340)], clicks=(drag0,))
    return t


def subscribe_bar():
    """TR 1812-1915: a bar with like, SUBSCRIBE and bell; a hand likes, subscribes and rings the bell."""
    f0, fe, h = 1812, 1822, 1909
    t = _p("barra-suscribir", "Barra me gusta, suscribirse y campana", "Like, subscribe and bell bar", 18065,
           span(f0, fe, h, 1.5), "redes", ["suscribirse", "me gusta", "campana", "cursor"], thumb=3.4)
    s = Q(t, f0, fe, h, "tr", 1.5)
    c1, c2, c3 = 1842, 1863, 1885
    unfold(s, (1233, 246, 1563, 333), f0, 7, "c", radius=8)
    toggled_icon(s, "Me gusta", THUMB, 1276, 290, 36, 34, 1817, c1, on_colour=INK)
    button(s, (1315, 268, 1480, 312), "SUBSCRIBE", "SUBSCRIBED", (1340, 283, 1455, 298), (1330, 283, 1465, 298),
           1818, c2, txt_a=INK, txt_b="#333333")
    outline_icon(s, "Campana", BELL, 1518, 289, 34, 40, g=lambda fr, u: (pop(fr, 1819, 5), s.before(c3)(fr, u)))

    def ring_(fr, u):
        rf = s.R(u)
        wob = 18 * math.sin(2 * math.pi * (rf - c3) / 6) * math.exp(-(rf - c3) / 8) if rf >= c3 else 0.0
        return pop(fr, 1819, 5), s.after(c3)(fr, u), 0, 0, wob
    s.icon("Campana (activa)", [fill(INK), stroke(INK, 1.5 * s.sc, "center")], 1518, 289, 34, 40, g=ring_, path=BELL)
    s.cursor([(1828, 1330, 380), (1836, 1282, 306), (1842, 1278, 298), (1850, 1350, 320), (1856, 1400, 304),
              (1863, 1398, 296), (1870, 1440, 320), (1878, 1520, 304), (1885, 1520, 296), (1892, 1525, 306),
              (1900, 1560, 360)], clicks=(c1, c2, c3), hand=True)
    return t


def coffee_dialog():
    """BL 1818-1915: a «COFFEE IS OVER» dialog with an OK button; a hand clicks OK."""
    f0, fe, h = 1818, 1833, 1909
    t = _p("aviso-cafe", "Ventana de aviso con OK", "Alert window with OK", 18066, span(f0, fe, h, 1.5),
           "elementos", ["aviso", "ventana", "cursor"], thumb=3.0)
    s = Q(t, f0, fe, h, "bl", 1.5)
    unfold(s, (311, 681, 721, 900), f0, 8, "w", radius=8)
    s.icon("Cerrar", [fill(RED), stroke(INK, 2.5 * s.sc)], 356, 720, 34, 34, g=pop_g(1824, 5), kind="ellipse")
    outline_icon(s, "Cerrar (x)", "M 30 30 L 70 70 M 70 30 L 30 70", 356, 720, 34, 34, g=pop_g(1825, 5), width=2.5)
    s.txt("COFFEE IS OVER", (390, 708, 642, 731), 800, slide=(1824, 7, 60), name="Título")
    s.txt("Have another cup to continue", (342, 756, 660, 773), 500, slide=(1826, 7, 60), name="Texto 1")
    s.txt("working.", (342, 781, 434, 798), 500, slide=(1827, 7, 40), name="Texto 2")
    pr = press(s, 1907, 0.06)
    s.box("OK", [fill(BLUE), stroke(INK, 2.5 * s.sc)],
          lambda fr, u: (lambda q: (516 - 174 * q * pr(u), 830, 516 + 174 * q * pr(u), 870))(k(fr, 1826, 7)),
          op=lambda fr, u: 1.0 if fr >= 1826 else 0.0)
    s.txt("OK", (499, 842, 532, 858), 800, WHITE, "OK (texto)", op=lambda fr, u: k(fr, 1829, 3))
    s.cursor([(1892, 560, 940), (1902, 520, 862), (1907, 518, 856), (1911, 520, 862)], clicks=(1907,), hand=True)
    return t


def paul_card():
    """BR 1823-1915: a round picture; the arrow clicks it and the card opens: PAUL LEE, subscribers, SUBSCRIBE."""
    f0, fe, h = 1823, 1862, 1914
    t = _p("tarjeta-canal", "Tarjeta de canal que se abre", "Channel card that opens", 18067, span(f0, fe, h, 2.5),
           "redes", ["canal", "suscribirse", "cursor", "avatar"], thumb=3.2)
    s = Q(t, f0, fe, h, "br", 2.5)
    c1, c2 = 1848, 1877

    def card(fr, u):
        q = k(fr, c1 + 1, 9)
        x1 = 1250 + (1638 - 1250) * q
        return 1128, 726, x1, 845
    s.box("Tarjeta", s.card_l(WHITE, 3.0, 9.0), card, op=lambda fr, u: 1.0 if fr >= f0 else 0.0, radius=8)
    tile_q = lambda fr: pop(fr, f0, 7)  # noqa: E731
    s.avatar("h-portrait-02", 1188, 786, 40, g=lambda fr, u: (tile_q(fr) * press(s, c1, 0.08)(u), 1.0), line=2.5)
    s.txt("PAUL LEE", (1255, 756, 1427, 783), 800, slide=(c1 + 5, 7, 60), name="Nombre")
    sub = s.txt("622 subscribers", (1254, 791, 1420, 808), 500, name="Suscriptores")
    s.typed(sub, c1 + 7, stagger=0.03, duration=0.02)
    button(s, (1467, 768, 1599, 803), "SUBSCRIBE", "SUBSCRIBED", (1490, 780, 1576, 792), (1482, 780, 1586, 792),
           c1 + 8, c2, txt_a=INK)
    s.cursor([(1838, 1260, 860), (1844, 1214, 822), (1848, 1210, 814), (1858, 1300, 840), (1870, 1530, 806),
              (1877, 1534, 798), (1884, 1538, 806), (1896, 1580, 860)], clicks=(c1, c2))
    return t


# =============================================================================================================
# GRID 18 (76.0-80.0 s): player controls
# =============================================================================================================
PLAY_ICON = poly([(14, 4), (96, 50), (14, 96)])


def player_row(s, xs, y, shape, colour, icon_colour, filled_icons, hit, hit_colour, hit_icon, click, cursor, hand):
    """Four player buttons (rewind, pause, play, forward) that pop in one by one; the clicked one swaps colours."""
    icons = (REW, PAUSE, PLAY_ICON, FFWD)
    kw = dict(kind="ellipse") if shape == "circle" else dict(radius=10)
    for i, x in enumerate(xs):
        at = s.f0 + 2 * i
        pr = press(s, click, 0.1) if i == hit else (lambda u: 1.0)
        for col, st, nm in ((colour, s.before(click) if i == hit else (lambda fr, u: 1.0), f"Botón {i + 1}"),
                            (hit_colour, s.after(click), f"Botón {i + 1} (activo)")):
            if nm.endswith("(activo)") and i != hit:
                continue
            s.icon(nm, s.card_l(col, 2.5, 8.0), x, y, 72, 72,
                   g=lambda fr, u, at=at, st=st, pr=pr: (pop(fr, at, 6, 0.15) * pr(u), st(fr, u)), **kw)
        size = 34 if i != 1 else 28
        for col, st, nm in ((icon_colour, s.before(click) if i == hit else (lambda fr, u: 1.0), f"Icono {i + 1}"),
                            (hit_icon, s.after(click), f"Icono {i + 1} (activo)")):
            if nm.endswith("(activo)") and i != hit:
                continue
            g = (lambda fr, u, at=at, st=st, pr=pr: (pop(fr, at + 1, 6, 0.15) * pr(u), st(fr, u)))
            if filled_icons:
                s.icon(nm, [fill(col), stroke(col, 1.0 * s.sc, "center")], x + (3 if i == 2 else 0), y, size, size,
                       g=g, path=icons[i])
            else:
                s.icon(nm, [nofill(), stroke(col, 2.6 * s.sc, "center")], x + (3 if i == 2 else 0), y, size, size,
                       g=g, path=icons[i])
    s.burst(xs[hit], y, click, r0=46, r1=74, ln=12)
    s.cursor(cursor, clicks=(click,), hand=hand)


def player_round():
    """TL 1928-1995: four round white player buttons; the arrow clicks rewind and it turns red."""
    f0, fe, h = 1928, 1937, 1983
    t = _p("reproductor-redondo", "Botones de reproductor redondos", "Round player buttons", 18068,
           span(f0, fe, h, 1.0), "elementos", ["reproductor", "botones", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "tl", 1.0)
    player_row(s, [378, 468, 558, 648], 290, "circle", WHITE, INK, True, 0, RED, WHITE, 1954,
               [(1938, 430, 380), (1947, 384, 300), (1954, 380, 292), (1961, 384, 302), (1972, 420, 360)], False)
    return t


def player_blue():
    """TR 1932-1998: four blue square player buttons; a hand clicks pause and it turns white."""
    f0, fe, h = 1932, 1941, 1986
    t = _p("reproductor-azul", "Botones de reproductor azules", "Blue player buttons", 18069, span(f0, fe, h, 1.0),
           "elementos", ["reproductor", "botones", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "tr", 1.0)
    player_row(s, [1257, 1347, 1437, 1527], 288, "square", BLUE, WHITE, False, 1, WHITE, INK, 1960,
               [(1942, 1400, 380), (1952, 1352, 304), (1960, 1348, 296), (1967, 1352, 306), (1978, 1380, 360)], True)
    return t


def player_square():
    """BL 1935-2000: four white square player buttons; a hand clicks play and it turns light blue."""
    f0, fe, h = 1935, 1944, 1988
    t = _p("reproductor-cuadrado", "Botones de reproductor cuadrados", "Square player buttons", 18070,
           span(f0, fe, h, 1.0), "elementos", ["reproductor", "botones", "cursor"], thumb=2.2)
    s = Q(t, f0, fe, h, "bl", 1.0)
    player_row(s, [380, 470, 560, 650], 788, "square", WHITE, INK, True, 2, "#5FCDE4", INK, 1965,
               [(1946, 620, 880), (1956, 566, 806), (1965, 562, 798), (1972, 566, 808), (1982, 600, 860)], True)
    return t


def player_yellow():
    """BR 1939-2002: four yellow round player buttons; the arrow clicks forward and it turns white."""
    f0, fe, h = 1939, 1948, 1990
    t = _p("reproductor-amarillo", "Botones de reproductor amarillos", "Yellow player buttons", 18071,
           span(f0, fe, h, 1.0), "elementos", ["reproductor", "botones", "cursor"], thumb=2.4)
    s = Q(t, f0, fe, h, "br", 1.0)
    player_row(s, [1266, 1356, 1446, 1536], 788, "circle", YELLOW, INK, False, 3, WHITE, INK, 1974,
               [(1952, 1620, 860), (1964, 1545, 800), (1974, 1540, 792), (1980, 1546, 802), (1988, 1580, 850)], False)
    return t


# =============================================================================================================
# GRID 19 (79.8-86.5 s): lists
# =============================================================================================================
def todo_list():
    """TL 2000-2140: TO-DO LIST FOR TODAY; each task appears, the arrow clicks it and it turns yellow «Done!»."""
    f0, fe, h = 2000, 2058, 2125
    t = _p("lista-tareas", "Lista de tareas para hoy", "To-do list for today", 18072, span(f0, fe, h, 5.0),
           "elementos", ["lista", "tareas", "cursor"], thumb=4.6)
    s = Q(t, f0, fe, h, "tl", 5.0)
    s.txt("TO-DO LIST", (431, 134, 605, 157), 800, op=lambda fr, u: k(fr, 2003, 4), name="Título")
    s.txt("FOR TODAY", (428, 169, 608, 192), 800, op=lambda fr, u: k(fr, 2004, 4), name="Título 2")
    tasks = (("Push the button", 2005, 2030), ("Write text", 2034, 2050), ("And this one too", 2054, 2075))
    for i, (word, at, c) in enumerate(tasks):
        y0 = 210 + 65 * i
        rect = (410, y0, 626, y0 + 50)
        grow_btn(s, rect, WHITE, at, 5, until=c, name=f"Tarea {i + 1}", radius=8)
        grow_btn(s, rect, YELLOW, at, 5, since=c, name=f"Tarea {i + 1} (hecha)", radius=8)
        x1 = 432 + {0: 150, 1: 100, 2: 166}[i]
        cl = s.txt(word, (432, y0 + 17, x1, y0 + 31), 500, "#9A9A9A", f"Tarea {i + 1} (texto)",
                   op=lambda fr, u, c=c, at=at: s.before(c)(fr, u) * (1.0 if fr >= at + 3 else 0.0))
        s.typed(cl, at + 3, stagger=0.03, duration=0.02)
        s.txt("Done!", (487, y0 + 16, 549, y0 + 33), 500, INK, f"Tarea {i + 1} (hecha, texto)",
              op=lambda fr, u, c=c, at=at: s.after(c)(fr, u) * (1.0 if fr >= at + 3 else 0.0))
    s.cursor([(2012, 700, 300), (2022, 600, 248), (2030, 596, 240), (2040, 610, 300), (2050, 598, 306),
              (2062, 640, 380), (2070, 600, 372), (2075, 598, 370), (2083, 610, 380), (2095, 680, 450)],
             clicks=(2030, 2050, 2075))
    return t


def top_video():
    """TR 2008-2142: HOW TO MAKE A TOP VIDEO with three switches; a hand turns each one on."""
    f0, fe, h = 2008, 2020, 2128
    t = _p("lista-interruptores", "Lista con interruptores", "List with switches", 18073, span(f0, fe, h, 1.5),
           "elementos", ["lista", "interruptor", "cursor"], thumb=4.6)
    s = Q(t, f0, fe, h, "tr", 1.5)
    s.txt("HOW TO MAKE", (1267, 168, 1498, 191), 800, op=lambda fr, u: k(fr, 2009, 4), name="Título")
    s.txt("A TOP VIDEO", (1269, 203, 1470, 226), 800, op=lambda fr, u: k(fr, 2010, 4), name="Título 2")
    rows = (("Uniqueness", 1403, 2022), ("Relevance", 1384, 2042), ("Recognizability", 1444, 2062))
    for i, (word, x1, c) in enumerate(rows):
        y = 277 + 50 * i
        s.txt(word, (1266, y - 10, x1, y + 7), 500, slide=(2012 + 2 * i, 7, 40), name=f"Opción {i + 1}")
        for col, st, nm in ((WHITE, s.before(c), f"Interruptor {i + 1}"), (BLUE, s.after(c),
                                                                           f"Interruptor {i + 1} (encendido)")):
            s.icon(nm, s.card_l(col, 2.5, 5.0), 1498, y, 56, 28,
                   g=lambda fr, u, st=st, i=i: (pop(fr, 2013 + 2 * i, 6), st(fr, u)), radius=14)
        kx = slide_knob(s, c, 1484, 1508)
        s.icon(f"Perilla {i + 1}", [fill(WHITE), stroke(INK, 2.5 * s.sc)], 1484, y, 32, 32,
               g=lambda fr, u, i=i, kx=kx: (pop(fr, 2014 + 2 * i, 6), 1.0, kx(u) - 1484, 0, 0), kind="ellipse")
    s.cursor([(2015, 1560, 320), (2022, 1505, 286), (2028, 1510, 296), (2036, 1508, 330), (2042, 1505, 336),
              (2048, 1510, 346), (2056, 1508, 380), (2062, 1505, 386), (2070, 1520, 420)],
             clicks=(2022, 2042, 2062), hand=True)
    return t


def dont_forget():
    """BL 2012-2145: PLEASE DON'T FORGET with three items; a hand ticks each one with a red check."""
    f0, fe, h = 2012, 2026, 2130
    t = _p("lista-no-olvides", "Lista no olvides: suscribirse, campana, me gusta",
           "Please don't forget list: subscribe, notify, like", 18074, span(f0, fe, h, 1.5), "redes",
           ["lista", "suscribirse", "cursor"], thumb=4.6)
    s = Q(t, f0, fe, h, "bl", 1.5)
    s.txt("PLEASE", (399, 632, 517, 655), 800, op=lambda fr, u: k(fr, 2013, 4), name="Título")
    s.txt("DON’T FORGET", (399, 667, 629, 690), 800, op=lambda fr, u: k(fr, 2014, 4), name="Título 2")
    items = (("Subscribe", 574, 2036), ("Get notified", 596, 2049), ("Like the video", 616, 2062))
    for i, (word, x1, c) in enumerate(items):
        y0 = 708 + 65 * i
        at = 2016 + 3 * i
        s.icon(f"Opción {i + 1}", s.card_l(WHITE, 2.5, 8.0), 520, y0 + 25, 240, 50,
               g=lambda fr, u, at=at: (1.0, 1.0 if fr >= at else 0.0, -60 * (1 - k(fr, at, 6)), 0, 0), radius=25)
        s.txt(word, (469, y0 + 18, x1, y0 + 34), 500, slide=(at + 2, 6, 40), name=f"Opción {i + 1} (texto)")
        outline_icon(s, f"Marca {i + 1}", CHECK, 440, y0 + 25, 30, 26,
                     g=lambda fr, u, c=c, at=at: (pop(s.R(u), c, 5, 0.3) if fr >= at else 0.0, 1.0), colour=RED,
                     width=5)
    s.cursor([(2028, 520, 820), (2034, 446, 740), (2036, 444, 736), (2043, 446, 790), (2049, 444, 800),
              (2056, 446, 856), (2062, 444, 866), (2070, 470, 930)], clicks=(2036, 2049, 2062), hand=True)
    return t


def welcome_channel():
    """BR 2015-2148: WELCOME TO MY CHANNEL with four buttons; the arrow clicks each and it turns green."""
    f0, fe, h = 2015, 2030, 2133
    t = _p("lista-bienvenida", "Bienvenido a mi canal: lista de botones", "Welcome to my channel button list",
           18075, span(f0, fe, h, 1.5), "redes", ["lista", "suscribirse", "cursor", "bienvenida"], thumb=4.8)
    s = Q(t, f0, fe, h, "br", 1.5)
    s.txt("WELCOME", (1314, 604, 1486, 627), 800, op=lambda fr, u: k(fr, 2016, 4), name="Título")
    s.txt("TO MY CHANNEL", (1271, 639, 1528, 662), 800, op=lambda fr, u: k(fr, 2017, 4), name="Título 2")
    items = (("Subscribe", (1280, 680, 1520, 730), (1348, 698, 1452, 714), 2042),
             ("Get notified", (1280, 745, 1520, 795), (1337, 763, 1463, 779), 2062),
             ("Like the video", (1280, 810, 1520, 860), (1326, 828, 1473, 844), 2085),
             ("Leave a comment", (1293, 875, 1507, 920), (1315, 890, 1483, 905), 2105))
    for i, (word, rect, ink, c) in enumerate(items):
        at = 2019 + 3 * i
        sx = -60 if i % 2 == 0 else 60
        x0, y0, x1, y1 = rect
        for col, st, nm in ((WHITE, s.before(c), f"Botón {i + 1}"), (GREEN, s.after(c), f"Botón {i + 1} (hecho)")):
            pr = press(s, c, 0.06)
            s.icon(nm, s.card_l(col, 2.5, 8.0), (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0,
                   g=lambda fr, u, at=at, st=st, pr=pr, sx=sx: (pr(u), st(fr, u) * (1.0 if fr >= at else 0.0),
                                                                sx * (1 - k(fr, at, 6)), 0, 0), radius=8)
        mx = 0
        del mx
        s.txt(word, ink, 500, INK, f"Botón {i + 1} (texto)",
              g=lambda fr, u, at=at, c=c, sx=sx: (sx * (1 - k(fr, at, 6)), 0, 1, 0,
                                                  s.before(c)(fr, u) * k(fr, at + 2, 3)))
        s.txt(word, ink, 500, WHITE, f"Botón {i + 1} (texto hecho)",
              g=lambda fr, u, at=at, c=c, sx=sx: (sx * (1 - k(fr, at, 6)), 0, 1, 0,
                                                  s.after(c)(fr, u) * k(fr, at + 2, 3)))
    s.cursor([(2032, 1560, 760), (2038, 1480, 714), (2042, 1478, 708), (2054, 1480, 772), (2062, 1478, 774),
              (2076, 1480, 836), (2085, 1478, 838), (2097, 1482, 900), (2105, 1480, 904), (2114, 1500, 950)],
             clicks=(2042, 2062, 2085, 2105))
    return t


# =============================================================================================================
# FULL SCREEN over footage (8.9-17.9 s)
# =============================================================================================================
def alice_card():
    """223-300: a round picture in a little tile; the arrow clicks it, the card opens (ALICE LEWIS, subscribers
    counting up, SUBSCRIBE) and the arrow subscribes."""
    f0, fe, h = 223, 262, 288
    t = _p("tarjeta-suscribir-grande", "Tarjeta grande de canal con suscribirse", "Big channel card with subscribe",
           18076, span(f0, fe, h, 2.5), "redes", ["canal", "suscribirse", "cursor", "avatar", "tercio"], thumb=2.2)
    s = Q(t, f0, fe, h, "full", 2.5)
    c1, c2 = 244, 276

    def card(fr, u):
        if fr < 247:
            q = pop(fr, f0, 6, 0.12)
            return 638 - 89 * q, 852 - 89 * q, 638 + 89 * q, 852 + 89 * q
        q = k(fr, 247, 10)
        return 549, 762, 727 + (1404 - 727) * q, 941
    tilt = lambda fr: -12 * (1 - lin(fr, f0, 7)) if fr < f0 + 7 else 0.0  # noqa: E731
    s.box("Tarjeta", s.card_l(WHITE, 3.0, 12.0), card, op=lambda fr, u: 1.0 if fr >= f0 else 0.0, radius=10)
    s.avatar("h-portrait-04", 638, 852, 58, g=lambda fr, u: (pop(fr, f0 + 1, 6) * press(s, c1, 0.06)(u), 1.0),
             line=3.0)
    del tilt
    s.txt("ALICE LEWIS", (741, 808, 1088, 845), 800, slide=(249, 7, 80), name="Nombre")
    sub = s.txt("920K subscribers", (742, 859, 1015, 881), 500, name="Suscriptores",
                op=lambda fr, u: 1.0 if fr >= 252 else 0.0)
    s.counter(sub, 59, "920K subscribers", 252, 18)
    sub["textContent"] = "920K subscribers"
    delay_clip(s, sub, 252)
    button(s, (1126, 820, 1352, 882), "SUBSCRIBE", "SUBSCRIBED", (1162, 843, 1316, 861), (1150, 843, 1328, 861), 254,
           c2, txt_a=INK)
    s.cursor([(229, 760, 960), (238, 664, 900), (244, 660, 892), (252, 700, 900), (266, 1240, 870), (276, 1236, 862),
              (282, 1240, 870), (288, 1280, 930)], clicks=(c1, c2), size=(40, 60))
    return t


def chat_window():
    """273-345: a chat window: «will your concert in NY take place?», «of course!» is typed and sent, then
    «yippee!» arrives; each message pushes the others up."""
    f0, fe, h = 273, 288, 334
    t = _p("chat-ventana-grande", "Ventana de chat sobre el video", "Chat window over the video", 18077,
           span(f0, fe, h, 1.5), "redes", ["chat", "mensaje", "ventana"], thumb=1.9)
    s = Q(t, f0, fe, h, "full", 1.5)
    phone_chat(s, (158, 132, 651, 689), WHITE, [
        dict(appear=281, rect=(274, 178, 574, 278), tail="tl", col="#5FD3E6", text="will your concert",
             ink=(316, 199, 545, 221), tcol=INK, avatar=("h-portrait-02", 228, 211, 34, True, "Foto 1"),
             labels=[("CHAD R.", (295, 147, 414, 166), 800), ("in NY take place?", (316, 232, 553, 253), 500)]),
        dict(appear=302, rect=(330, 331, 556, 397), tail="tr", col=BLUE, text="of course!",
             ink=(357, 352, 489, 375), tcol=WHITE, avatar=("fx-woman-08", 580, 364, 34, True, "Foto 2"),
             labels=[("ROCKY FM", (364, 298, 515, 318), 800)]),
        dict(appear=330, rect=(274, 481, 440, 547), tail="tl", col="#5FD3E6", text="yippee!",
             ink=(310, 502, 404, 525), tcol=INK, avatar=("h-portrait-02", 228, 514, 34, True, "Foto 1"),
             labels=[("CHAD R.", (295, 449, 414, 468), 800)])],
        (195, 599, 534, 651), (586, 625, 53), True,
        [(283, 296, "of course!", (215, 615, 335, 637)), (318, 328, "yippee!", (215, 615, 310, 637))],
        pitch=150.0)
    s.cursor([(288, 640, 720), (292, 590, 640), (296, 588, 632), (304, 610, 680), (318, 600, 660), (328, 588, 632),
              (334, 600, 660)], clicks=(296, 328), size=(40, 60))
    return t


def video_card_bell():
    """334-400: a video card (picture, title, channel, SUBSCRIBE, bell); the arrow subscribes and rings the bell."""
    f0, fe, h = 334, 350, 390
    t = _p("video-suscribir-campana", "Tarjeta de video con suscribirse y campana",
           "Video card with subscribe and bell", 18078, span(f0, fe, h, 1.5), "redes",
           ["publicación", "suscribirse", "campana", "cursor"], thumb=2.0)
    s = Q(t, f0, fe, h, "full", 1.5)
    c1, c2 = 362, 385
    unfold(s, (141, 420, 788, 953), f0, 8, "h", radius=10, layers=s.card_l(WHITE, 3.0, 12.0))
    s.pic("y3-shock-01", (141, 420, 788, 782), vis=lambda fr, u: (141, 782 - 362 * k(fr, 338, 10), 788, 782),
          op=lambda fr, u: 1.0 if fr >= 338 else 0.0, line=3.0)
    s.txt("3 secrets of mysterious seductresses", (165, 803, 668, 826), 500, slide=(341, 8, 80), name="Título")
    s.avatar("y3-shock-01", 204, 888, 39, g=pop_g(336, 5), line=3.0)
    s.txt("GEISHA", (268, 872, 417, 903), 800, slide=(338, 7, 60), name="Canal")
    badge(s, 446, 888, 22, pop_g(343, 4), INK)
    button(s, (497, 861, 692, 915), "SUBSCRIBE", "SUBSCRIBED", (532, 879, 657, 897), (517, 879, 671, 897), 339, c1,
           txt_a=WHITE)
    outline_icon(s, "Campana", BELL, 733, 885, 34, 40, g=lambda fr, u: (pop(fr, 341, 5), s.before(c2)(fr, u)),
                 width=3)

    def ring_(fr, u):
        rf = s.R(u)
        wob = 18 * math.sin(2 * math.pi * (rf - c2) / 6) * math.exp(-(rf - c2) / 8) if rf >= c2 else 0.0
        return pop(fr, 341, 5), s.after(c2)(fr, u), 0, 0, wob
    s.icon("Campana (activa)", [fill(INK), stroke(INK, 2 * s.sc, "center")], 733, 885, 34, 40, g=ring_, path=BELL)
    s.cursor([(346, 760, 1000), (355, 610, 900), (362, 604, 892), (370, 660, 900), (379, 736, 896), (385, 734, 890),
              (390, 740, 900)], clicks=(c1, c2), size=(40, 60))
    return t


def channel_list():
    """391-460: ROCKYSTAR CHANNEL with four white buttons; the arrow clicks Subscribe, Get notified and Like the
    video, and each turns blue."""
    f0, fe, h = 391, 405, 446
    t = _p("lista-canal-grande", "Lista del canal sobre el video", "Channel list over the video", 18079,
           span(f0, fe, h, 1.5), "redes", ["lista", "suscribirse", "cursor"], thumb=2.0)
    s = Q(t, f0, fe, h, "full", 1.5)
    s.txt("ROCKYSTAR", (230, 161, 489, 194), 800, op=lambda fr, u: k(fr, f0, 4), name="Título")
    s.txt("CHANNEL", (254, 211, 464, 243), 800, op=lambda fr, u: k(fr, f0 + 1, 4), name="Título 2")
    items = (("Subscribe", (191, 270, 527, 338), (324, 293, 470, 315), 397),
             ("Get notified", (191, 361, 527, 429), (271, 384, 448, 406), 418),
             ("Like the video", (191, 453, 527, 520), (256, 475, 462, 498), 440),
             ("Leave a comment", (191, 544, 527, 611), (225, 566, 491, 589), None))
    for i, (word, rect, ink, c) in enumerate(items):
        at = f0 + 2 * i
        x0, y0, x1, y1 = rect
        sx = -60
        for col, st, nm in ((WHITE, s.before(c) if c else (lambda fr, u: 1.0), f"Botón {i + 1}"),
                            (BLUE, s.after(c) if c else (lambda fr, u: 0.0), f"Botón {i + 1} (hecho)")):
            pr = press(s, c, 0.06) if c else (lambda u: 1.0)
            s.icon(nm, s.card_l(col, 3.0, 10.0), (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0,
                   g=lambda fr, u, at=at, st=st, pr=pr: (pr(u), st(fr, u) * (1.0 if fr >= at else 0.0),
                                                         sx * (1 - k(fr, at, 6)), 0, 0), radius=10)
        for colour, st, nm in ((INK, s.before(c) if c else (lambda fr, u: 1.0), f"Botón {i + 1} (texto)"),
                               (WHITE, s.after(c) if c else (lambda fr, u: 0.0), f"Botón {i + 1} (texto hecho)")):
            s.txt(word, ink, 500, colour, nm,
                  g=lambda fr, u, at=at, st=st: (sx * (1 - k(fr, at, 6)), 0, 1, 0, st(fr, u) * k(fr, at + 2, 3)))
    s.cursor([(393, 470, 380), (397, 452, 320), (402, 460, 330), (412, 456, 400), (418, 454, 412), (426, 458, 440),
              (436, 454, 500), (440, 452, 504), (446, 470, 540)], clicks=(397, 418, 440), size=(40, 60))
    return t


TEMPLATES = [post_charles, post_jason, post_lisa, post_rockystar, post_skatergirl, post_lillie, post_jasmine,
             post_beatrice, post_pearl, post_connie, post_richard, post_frank, post_seth, post_madeline, comment_irea,
             comment_jonathan, search_loading, search_button, search_map, search_square,
             add_comment, send_comment, avatar_comment, message_opening, chat_two, chat_names, chat_phone_blue,
             chat_phone_yellow, rate_ring, rate_us, rate_template, rate_great,
             rate_item, recommend, advise_friends, like_faces,
             react_zowie, react_done, react_cool, react_thanks,
             count_heart, count_follower, count_comments, count_thumbs,
             notif_likes, notif_comments, notif_followers, notif_double,
             badge_bird, badge_follow, badge_join, badge_insta,
             badge_like_this, badge_photo, badge_click_here, badge_get_ready,
             toggle_on, radio_select, checkbox_checked, switch_start,
             buy_now, download_bar, download_ring, cart_price,
             make_noise, subscribe_bar, coffee_dialog, paul_card,
             player_round, player_blue, player_square, player_yellow,
             todo_list, top_video, dont_forget, welcome_channel,
             alice_card, chat_window, video_card_bell, channel_list]
