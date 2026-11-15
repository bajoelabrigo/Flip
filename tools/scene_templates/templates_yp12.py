"""Video 38494344.mp4 (1920x1080, 60 fps, 91 s) as Kit de YouTube Stock templates (yp12-*). See
docs/plan-youtube-pack-2.md.

Subscribe widgets over footage, each one studied on 10 fps sheets and laid out where it sits in the reference: a
channel pill with SUBSCRIBE -> SUBSCRIBED and a bell, a bar with like / dislike / bell and a red SUBSCRIBE, cards with
the channel's picture, a channel card whose list fills in at each click, round pictures with like / YouTube / bell
circles around them (several choreographies, one with liquid necks), three round buttons, and two LIKE / SUBSCRIBE /
GET NOTIFIED lists. Overlays: no background of their own. Every geometry is a function of the reference's second v
(each piece starts at its own `o`), so the 60 fps source maps 1:1 in time. Study notes in
tienda/plantillas/estudio-38494344/NOTAS.md.
"""

from __future__ import annotations

import math
import random

from kit import Box, wide
from llt_motion import frames_of
from scene import keys
from templates_tit_c import FPS
from templates_tit_e import solid
from templates_tit_h import TRIANGLE, fill, ring
from templates_yp0 import BELL, THUMB, THUMB_DOWN, WAVES, E, L, W, ein, path_at, squeeze, stroke

WHITE, BLACK, RED = "#FFFFFF", "#000000", "#FF0000"
GREY = "#757575"
M = "Montserrat"

# The reference's pointer: a rounded white triangle, tip at the top left (box 0..100).
ARROW = ("M 4 1 C 1 -1 -1 1 0 5 L 18 94 C 19 100 24 101 27 97 L 46 66 C 48 63 51 61 55 60 L 95 52 C 101 51 101 45 "
         "96 42 Z")
# A liquid neck between two discs: full height at both ends, pinched in the middle.
NECK = "M 0 0 C 35 30 65 30 100 0 L 100 100 C 65 70 35 70 0 100 Z"


def bo(q, s=1.70158):
    """Back-out 0 -> 1 (a little past 1, then settles)."""
    q = max(0.0, min(1.0, q))
    r = q - 1
    return 1 + (s + 1) * r ** 3 + s * r ** 2


def bi(q, s=1.70158):
    """Back-in 0 -> 1 (dips below 0 first)."""
    q = max(0.0, min(1.0, q))
    return (s + 1) * q ** 3 - s * q ** 2


def popin(v, a, d=0.3, s=1.70158):
    return bo(L(v, a, d), s) if v > a else 0.0


def popout(v, a, d=0.25, s=1.70158):
    return max(0.0, 1 - bi(L(v, a, d), s))


def grow_shrink(v, a, up=0.12, peak=1.15, hold=0.0, down=0.18):
    """1 -> peak from a, then (after hold) -> 0: the reference's exit of a picture."""
    if v < a:
        return 1.0
    if v < a + up + hold:
        return 1 + (peak - 1) * E(v, a, up)
    return peak * (1 - ein(v, a + up + hold, down, 2.0))


class Y(W):
    """yp0's widget plus the pieces of this pack: arrow pointer, outline particles, round icons, pictures."""

    def __init__(self, t, dur, o):
        super().__init__(t, dur, o)
        self.seed = 0

    # --- small shapes -----------------------------------------------------------------------------------------
    def disc(self, name, layers, g):
        """g(v) = (cx, cy, diameter, op)."""
        return self.shp(name, layers, lambda v: (lambda o: (o[0], o[1], o[2], o[2], 0, o[3]))(g(v)),
                        kind="ellipse", base=(100, 100))

    def pill(self, name, colour, rect, radius, op=None, layers=None):
        """A box with rounded ends, rect(v) = (x0, y0, x1, y1) at its full size (it only moves, never squeezes)."""
        x0, y0, x1, y1 = rect(self.o)
        w, h = x1 - x0, y1 - y0

        def g(v):
            a0, b0, a1, b1 = rect(v)
            return (a0 + a1) / 2, (b0 + b1) / 2, a1 - a0, b1 - b0, 0, op(v) if op else 1.0
        return self.shp(name, layers or solid(colour), g, radius=radius, base=(w, h))

    def sparks(self, x, y, t, n=10, r0=40, r1=170, dur=0.7, size=(10, 22), kinds="sct", colour=WHITE, width=2.4,
               name="Partícula"):
        """Outline squares, circles and triangles that fly out from (x, y) at second t, turning and fading."""
        self.seed += 1
        rnd = random.Random(self.seed * 7919 + int(x) * 31 + int(y))
        for i in range(n):
            a = math.radians(rnd.uniform(0, 360))
            ra, rb = r0 * rnd.uniform(0.7, 1.2), r1 * rnd.uniform(0.6, 1.25)
            sz, spin = rnd.uniform(*size), rnd.uniform(-200, 200)
            dl, du = rnd.uniform(0, 0.1), dur * rnd.uniform(0.75, 1.25)
            kind = kinds[i % len(kinds)]

            def g(v, a=a, ra=ra, rb=rb, sz=sz, spin=spin, dl=dl, du=du):
                q = L(v, t + dl, du)
                r = ra + (rb - ra) * (1 - (1 - q) ** 2)
                on = t + dl <= v < t + dl + du
                s_ = sz * (1 - 0.35 * q)
                return x + math.cos(a) * r, y + math.sin(a) * r, s_, s_, spin * q, (min(1.0, 3 * (1 - q)) if on else 0)
            if kind == "c":
                self.shp(f"{name} {i + 1}", ring(colour, width), g, kind="ellipse", base=(20, 20))
            elif kind == "t":
                self.shp(f"{name} {i + 1}", ring(colour, width), g, path=TRIANGLE, base=(20, 20))
            elif kind == "d":
                self.shp(f"{name} {i + 1}", solid(colour), g, base=(20, 20))
            else:
                self.shp(f"{name} {i + 1}", ring(colour, width), g, base=(20, 20))

    def arrow(self, pts, t_in, t_out, clicks=(), size=(48, 55), name="Cursor"):
        """The pointer: its tip through waypoints [(second, x, y)]; it presses a little at each click."""
        def g(v):
            x, y = path_at(pts, v)
            sc = 1 - sum(0.16 * math.sin(math.pi * L(v, c - 0.08, 0.2)) for c in clicks)
            w, h = size[0] * sc, size[1] * sc
            return x + w / 2, y + h / 2, w, h, 0, E(v, t_in, 0.1) * (1 - E(v, t_out, 0.12))
        self.shp(name, [fill(WHITE), stroke("#3A3A3A", 2.6)], g, path=ARROW, base=size)

    # --- glyphs -----------------------------------------------------------------------------------------------
    def glyph(self, kind, g, size, colour, name, waves=True, tri=WHITE):
        """kind like / dislike / bell / yt; g(v) = (cx, cy, scale, rot, op); size = height of the glyph."""
        made = []
        if kind in ("like", "dislike"):
            path = THUMB if kind == "like" else THUMB_DOWN
            made.append(self.shp(name, solid(colour), lambda v: (lambda o: (o[0], o[1], size * o[2], size * o[2],
                                                                            o[3], o[4]))(g(v)),
                                 path=path, base=(size, size)))
        elif kind == "bell":
            bw, bh = size * 0.78, size * 0.86
            made.append(self.shp(name, solid(colour), lambda v: (lambda o: (o[0], o[1] + size * 0.06 * o[2],
                                                                            bw * o[2], bh * o[2], o[3], o[4]))(g(v)),
                                 path=BELL, base=(bw, bh)))
            if waves:
                f = size * 0.98
                made.append(self.shp(f"{name} (ondas)", [{"id": "fill", "kind": "fill", "enabled": False,
                                                          "paint": {"kind": "solid", "color": "#00000000"}},
                                                         stroke(colour, max(2.5, size * 0.075))],
                                     lambda v: (lambda o: (o[0], o[1] - size * 0.1 * o[2], f * o[2], f * o[2], 0,
                                                           o[4]))(g(v)), path=WAVES, base=(f, f)))
        else:  # yt
            w, h = size * 1.42, size
            made.append(self.shp(name, solid(colour), lambda v: (lambda o: (o[0], o[1], w * o[2], h * o[2], o[3],
                                                                            o[4]))(g(v)),
                                 radius=h * 0.28, base=(w, h)))
            made.append(self.shp(f"{name} (play)", solid(tri), lambda v: (lambda o: (o[0] + w * 0.03 * o[2], o[1],
                                                                                     w * 0.26 * o[2], h * 0.42 * o[2],
                                                                                     o[3], o[4]))(g(v)),
                                 path=TRIANGLE, base=(w * 0.26, h * 0.42)))
        return made

    def sym(self, kind, g, size, c, before, after, name, tri=WHITE, tri_after=None, press=True):
        """A glyph that swaps colour at second c (and squeezes); g(v) = (cx, cy, scale, rot, op)."""
        def gg(after_):
            def f(v):
                x, y, sc, rot, op = g(v)
                k = squeeze(v, c) if (c is not None and press) else 1.0
                on = c is not None and v >= c
                return x, y, sc * k, rot, op if on == after_ else 0.0
            return f
        made = self.glyph(kind, gg(False), size, before, name, tri=tri)
        if c is not None:
            made += self.glyph(kind, gg(True), size, after, f"{name} (activo)", tri=tri_after or tri)
        return made

    def icon(self, kind, r, g, c=None, before=GREY, after=None, size=None, disc=WHITE, name="Icono", tri=WHITE,
             tri_after=None, press_disc=False):
        """A round button: disc of radius r and a glyph; g(v) = (cx, cy, scale, op)."""
        size = size or r * 1.05

        def dg(v):
            x, y, sc, op = g(v)[:4]
            k = squeeze(v, c) if (press_disc and c is not None) else 1.0
            return x, y, 2 * r * sc * k, op
        made = [self.disc(f"{name} (círculo)", solid(disc), dg)]
        made += self.sym(kind, lambda v: (lambda o: (o[0], o[1], o[2], o[4] if len(o) > 4 else 0.0, o[3]))(g(v)),
                         size, c, before,
                         after or before, name, tri=tri, tri_after=tri_after)
        return made

    def picture(self, sample, cx, cy, R, rw, g, ring_col=WHITE, name="Foto del canal", rot=None, inner=None):
        """The channel's picture in a ring: g(v) = (dx, dy, scale, op); inner(v) = scale of the photo inside the
        ring (it shrinks to show a plain disc); rot(v) turns the photo."""
        def rg(v):
            dx, dy, sc, op = g(v)
            return cx + dx, cy + dy, 2 * R * sc, op
        self.disc("Aro", solid(ring_col), rg)
        rp = R - rw
        t = self.t
        track = t.track("video", name)
        mo, op, rt = [], [], []
        for u in frames_of(self.dur):
            v = u + self.o
            dx, dy, sc, o = g(v)
            s_ = sc * (inner(v) if inner else 1.0)
            mo.append((u, {"s": max(1e-3, s_), "dx": dx, "dy": dy}, "linear"))
            op.append((u, round(max(0.0, min(1.0, o if s_ > 0.01 else 0.0)), 4), "linear"))
            rt.append((u, round(rot(v) if rot else 0.0, 3), "linear"))
        clip = t.photo(track, sample, 0.0, self.dur, Box(cx - rp, cy - rp, 2 * rp, 2 * rp), mo, label="Tu foto")
        clip["opacity"] = keys(op)
        if rot:
            clip["rotation"] = keys(rt)
        t.mask(track, clip, "ellipse")
        return clip

    def neck(self, name, a, b, h, colour=WHITE):
        """A liquid neck between the centres a(v) and b(v) = (x, y), h(v) its height at the ends."""
        def g(v):
            (x0, y0), (x1, y1) = a(v), b(v)
            d = math.hypot(x1 - x0, y1 - y0)
            hh = h(v)
            return (x0 + x1) / 2, (y0 + y1) / 2, max(1e-3, d), hh, math.degrees(math.atan2(y1 - y0, x1 - x0)), (
                1.0 if hh > 0.5 else 0.0)
        return self.shp(name, solid(colour), g, path=NECK, base=(100, 100))


def _p(id, es, en, order, dur, thumb, tags=(), section="elementos"):
    return wide(f"yp12-{id}", es, en, "ytkit", dur, order=order,
                tags=[f"kit:{section}", "youtube", "suscríbete", "botón"] + list(tags), thumb_at=thumb)


def _cap(c, x0, x1):
    return lambda v: (x0, c[1], x1(v), c[3])


# --- 1. Picture + name pill, grey SUBSCRIBE clicked into SUBSCRIBED, white bell clicked orange (8.15-14.05 s) ------
def name_bar():
    O, D = 8.15, 5.9
    t = _p("nombre-suscrito", "Canal con nombre, suscrito y campana", "Channel name, subscribed and bell", 17800, D,
           3.6, ["nombre", "campana", "clic"])
    s = Y(t, D, O)
    BG, OR = "#ABABAB", "#FFA02F"

    def ax(v):
        return 567 - 190 * E(v, 8.86, 0.3)

    def reach(v):  # right end of the pill
        out = ein(v, 12.15, 0.3, 2.0)
        return ax(v) + 581 * E(v, 8.86, 0.32) * (1 - out)
    s.pill("Nombre (fondo)", WHITE, lambda v: (reach(v) - 581 + 62, 769, reach(v) + 2, 927), 79,
           op=lambda v: 1.0 if reach(v) - ax(v) > 4 else 0.0)
    s.mask_to(t.tracks[-1].clips[-1], lambda v: (ax(v), 760, 1920, 940))
    name = s.txt("TAYLOR SMITH", (552, 833, 885, 865), M, 800, RED, "Nombre del canal")
    s.mask_to(name, lambda v: (ax(v), 760, reach(v) - 40, 940))

    def av(v):
        sc = popin(v, 8.3, 0.28) * (1 if v < 12.6 else grow_shrink(v, 12.6, 0.08, 1.1, 0.0, 0.18))
        return ax(v) - 377, 0, sc, 1.0 if v > 8.3 else 0.0
    s.picture("h-man-04", 377, 848, 125, 12, av)
    s.sparks(567, 848, 8.42, n=12, r0=110, r1=230, dur=0.8)
    s.sparks(377, 848, 12.78, n=10, r0=40, r1=200, dur=0.75)

    # The button: it opens from a thin line, is clicked at 10.1 and pops away at 13.05.
    def bsc(v):
        if v >= 12.85:
            return grow_shrink(v, 12.85, 0.18, 1.06, 0.02, 0.22)
        return squeeze(v, 10.1)

    def bg(v):
        sx = (0.35 + 0.65 * E(v, 9.4, 0.25)) * bsc(v)
        sy = (0.04 + 0.96 * E(v, 9.47, 0.2)) * bsc(v)
        return 1240.5, 848, 449 * sx, 102 * sy, 0, 1.0 if v > 9.4 else 0.0
    s.shp("Botón", solid(BG), bg, radius=6, base=(449, 102))

    def tg(after):
        def f(v):
            q = E(v, 9.47, 0.2)
            on = v >= 10.1
            return 0, 0, max(1e-3, (0.35 + 0.65 * q) * bsc(v)), 0, (q if on == after else 0.0)
        return f
    s.txt("SUBSCRIBE", (1090, 827, 1390, 867), M, 700, WHITE, "Suscribirse", g=tg(False))
    s.txt("SUBSCRIBED", (1070, 827, 1410, 867), M, 700, WHITE, "Suscrito", g=tg(True))
    s.sparks(1240, 848, 13.18, n=8, r0=120, r1=260, dur=0.6, kinds="tcs")

    def bell_g(v):
        sc = popin(v, 10.3, 0.26) * (popout(v, 13.55, 0.22) if v > 13.55 else 1.0)
        wig = 18 * math.sin(2 * math.pi * (v - 11.12) / 0.26) * math.exp(-(v - 11.12) * 3.5) if v > 11.12 else 0.0
        return 1574, 851, sc, wig, 1.0 if v > 10.3 else 0.0
    s.sym("bell", bell_g, 104, 11.12, WHITE, OR, "Campana", press=False)
    s.sparks(1574, 851, 13.72, n=8, r0=40, r1=150, dur=0.6)
    s.arrow([(9.45, 1100, 990), (9.85, 1050, 905), (10.25, 1050, 900), (10.55, 1440, 925), (10.85, 1585, 900),
             (11.65, 1585, 900), (11.85, 1610, 950)], 9.45, 11.72, clicks=(10.05, 11.08))
    return t


# --- 2. YOGA TEACHER bar: picture in the middle, like / dislike / bell and a red SUBSCRIBE (14.12-19.82 s) ----------
def teacher_bar():
    O, D = 14.12, 5.7
    t = _p("barra-profesora", "Barra con foto, me gusta, campana y suscribirse", "Bar with picture, like, bell and "
           "subscribe", 17801, D, 4.4, ["barra", "me gusta", "campana", "clic"])
    s = Y(t, D, O)
    CX, CY = 956, 840
    BLUE, OR = "#1A5CF0", "#FFA02F"

    def half(v):  # half width of the white bar
        return 131 + 373 * E(v, 14.74, 0.24) * (1 - ein(v, 18.92, 0.18, 1.6))
    s.pill("Barra", WHITE, lambda v: (CX - half(v), 752, CX + half(v), 928), 88,
           op=lambda v: 1.0 if half(v) > 132 else 0.0)
    bar = lambda v: (CX - half(v) + 30, 752, CX + half(v) - 30, 928)  # noqa: E731
    title = s.txt("YOGA TEACHER", (490, 790, 791, 817), M, 800, RED, "Nombre del canal")
    s.typed(title, (14.95 - O) * FPS, stagger=0.012, duration=0.08, preset="fade", order="random")
    s.mask_to(title, bar)
    line = s.rect("Barra de me gusta", solid(BLUE), lambda fr, u: (lambda v: (516, 908, 516 + 185 * E(v, 15.0, 0.3),
                                                                              913))(u + O))
    s.mask_to(line, bar)
    gs = lambda v: popin(v, 14.95, 0.2)  # noqa: E731
    made = []
    made += s.sym("like", lambda v: (557, 873, gs(v), 0, 1.0), 54, 15.75, GREY, BLUE, "Me gusta")
    made += s.sym("dislike", lambda v: (652, 875, gs(v), 0, 1.0), 54, None, GREY, GREY, "No me gusta")
    made += s.sym("bell", lambda v: (760, 872, gs(v), 0, 1.0), 62, 16.85, GREY, OR, "Campana")
    for m in made:
        s.mask_to(m, bar)
    bsc = lambda v: popin(v, 14.98, 0.2) * squeeze(v, 17.95)  # noqa: E731

    def btn(after):
        def g(v):
            ok = v >= 17.95
            return 1257.5, 840.5, 301 * bsc(v), 51 * bsc(v), 0, 1.0 if ok == after else 0.0
        return g
    made = [s.shp("Suscribirse (fondo)", solid(RED), btn(False), radius=12, base=(301, 51)),
            s.shp("Suscrito (fondo)", [fill(WHITE), stroke(RED, 3.5, "inside")], btn(True), radius=12, base=(301, 51))]
    tg = lambda after: (lambda v: (0, 0, max(1e-3, bsc(v)), 0, 1.0 if (v >= 17.95) == after else 0.0))  # noqa: E731
    made.append(s.txt("SUBSCRIBE", (1137, 826, 1377, 857), M, 800, WHITE, "Suscribirse", g=tg(False)))
    made.append(s.txt("SUBSCRIBED", (1124, 826, 1391, 857), M, 800, RED, "Suscrito", g=tg(True)))
    for m in made:
        s.mask_to(m, bar)

    def av(v):
        sc = popin(v, 14.2, 0.28) * (1.0 if v < 19.48 else popout(v, 19.48, 0.12))
        return 0, 0, sc, 1.0 if v > 14.2 else 0.0
    s.picture("y5-yoga-01", CX, CY, 131, 12, av, inner=lambda v: popin(v, 14.26, 0.26) * (1 - E(v, 19.26, 0.2)))
    s.sparks(CX, CY, 14.45, n=12, r0=120, r1=260, dur=0.8)
    s.sparks(CX, CY, 19.46, n=12, r0=40, r1=220, dur=0.7)
    s.arrow([(14.9, 600, 975), (15.25, 565, 895), (15.95, 565, 895), (16.4, 765, 895), (17.0, 765, 895),
             (17.45, 1080, 875), (18.15, 1080, 872), (18.45, 1180, 960)], 14.9, 18.38, clicks=(15.72, 16.82, 17.92))
    return t


# --- 3. Card: picture, pink SUBSCRIBE that turns into an outline, bell and like light up (19.85-24.6 s) -------------
def card_pink():
    O, D = 19.85, 4.75
    t = _p("tarjeta-rosa", "Tarjeta con foto y suscribirse rosado", "Card with picture and pink subscribe", 17802, D,
           3.0, ["tarjeta", "rosa"])
    s = Y(t, D, O)
    PINK, OR, BLUE = "#F0245B", "#FEA32D", "#1C8CE9"
    CX, CY = 1000, 708

    def sc(v):
        q = L(v, 19.98, 0.42)
        return (1 - (1 - q) ** 2) * (1 + 0.04 * math.sin(math.pi * L(v, 20.25, 0.5))) if v > 19.98 else 0.0

    def at(x, y, v):
        k = sc(v)
        return CX + (x - CX) * k, CY + (y - CY) * k, k

    def card(v):
        x0, y0, x1, y1 = 805, 460, 1196, 956
        q1, q2 = E(v, 24.24, 0.1), E(v, 24.32, 0.12)
        y1 = y1 - 250 * q1
        x0, x1 = x0 + 90 * q2, x1 - 90 * q2
        cx, cy, k = at((x0 + x1) / 2, (y0 + y1) / 2, v)
        return cx, cy, (x1 - x0) * k, (y1 - y0) * k, 0, (1.0 if v > 19.95 else 0.0) * (1 - E(v, 24.38, 0.1))
    s.shp("Tarjeta", solid(WHITE), card, radius=118, base=(391, 496))
    fade = lambda v: 1.0 - E(v, 24.08, 0.1)  # noqa: E731

    def btn(after):
        def g(v):
            x, y, k = at(1000.5, 763.5, v)
            p = squeeze(v, 22.42)
            return x, y, 335 * k * p, 73 * k * p, 0, fade(v) if (v >= 22.42) == after else 0.0
        return g
    s.shp("Suscribirse (fondo)", solid(PINK), btn(False), radius=36.5, base=(335, 73))
    s.shp("Suscrito (fondo)", [fill(WHITE), stroke(PINK, 3.5, "inside")], btn(True), radius=36.5, base=(335, 73))

    def tg(after):
        def g(v):
            x, y, k = at(1000, 765, v)
            p = squeeze(v, 22.42)
            return x - 1000, y - 765, max(1e-3, k * p), 0, fade(v) if (v >= 22.42) == after else 0.0
        return g
    s.txt("SUBSCRIBE", (921, 752, 1079, 778), M, 600, WHITE, "Suscribirse", g=tg(False))
    s.txt("SUBSCRIBE", (921, 752, 1079, 778), M, 600, PINK, "Suscrito", g=tg(True))
    ig = lambda x, y: (lambda v: (lambda a: (a[0], a[1], a[2], 0, fade(v)))(at(x, y, v)))  # noqa: E731
    s.sym("bell", ig(945, 866), 62, 22.42, GREY, OR, "Campana")
    s.sym("like", ig(1053, 866), 58, 22.42, GREY, BLUE, "Me gusta")

    def av(v):
        x, y, k = at(1000, 592, v)
        k *= 1.0 if v < 24.42 else popout(v, 24.42, 0.14)
        return x - 1000, y - 592, k, 1.0 if v > 19.95 else 0.0
    s.picture("y2-gym-01", 1000, 592, 112, 4, av, ring_col=PINK)
    s.sparks(1000, 700, 20.12, n=12, r0=150, r1=300, dur=0.7)
    s.sparks(1000, 592, 24.55, n=10, r0=20, r1=110, dur=0.5, size=(6, 12))
    return t


# --- 4. CHANNEL NAME pill that opens into a card: LIKE / SUBSCRIBE / GET NOTIFIED fill in at each click (24.95-30.6 s)
def channel_card():
    O, D = 24.95, 5.65
    t = _p("tarjeta-lista", "Nombre del canal que se abre en tarjeta", "Channel name that opens into a card", 17803, D,
           4.3, ["tarjeta", "lista", "me gusta", "campana", "clic"])
    s = Y(t, D, O)
    MAROON, CARD, BLUE, OR = "#642020", "#E3E3E3", "#1575D1", "#FEA32D"
    up = lambda v: -107 * E(v, 25.98, 0.22)  # noqa: E731

    def bottom(v):
        return 377 + 378 * E(v, 26.08, 0.28) - 378 * E(v, 29.98, 0.26)
    s.shp("Tarjeta", solid(CARD), lambda v: (609, (340 + bottom(v)) / 2, 598, max(1e-3, bottom(v) - 340), 0,
                                              1.0 if bottom(v) > 380 else 0.0), radius=40, base=(598, 415))
    box = lambda v: (300, 330, 920, bottom(v))  # noqa: E731
    sh = lambda v: bottom(v) - 755 if v > 29.9 else 0.0  # noqa: E731
    rows = (("like", 442, 74, 27.25, "LIKE", (528, 435, 628, 467), BLUE),
            ("yt", 560, 66, 27.9, "SUBSCRIBE", (526, 545, 770, 577), RED),
            ("bell", 675, 80, 28.78, "GET NOTIFIED", (507, 660, 804, 692), OR))
    for i, (kind, y, size, c, word, ink, col) in enumerate(rows):
        g = (lambda v, y=y, i=i: (426, y + sh(v), popin(v, 26.15 + 0.06 * i, 0.22), 0, 1.0))
        for m in s.sym(kind, g, size, c, RED if kind == "yt" else GREY, col, word.title()):
            s.mask_to(m, box)
        w = s.txt(word, ink, M, 800, MAROON, word.title(), g=lambda v: (0, sh(v), 1, 0, 1.0))
        s.mask_to(w, lambda v, ink=ink, c=c: (ink[0] - 4, 330, ink[0] - 4 + (ink[2] - ink[0] + 8) *
                                              E(v, c + 0.07, 0.2), bottom(v)))

    def reach(v):
        return 581 * E(v, 25.38, 0.22) * (1 - E(v, 30.37, 0.1))

    def pill(v):
        return 353 + reach(v) - 581 + 21, 374 + up(v), 353 + reach(v) + 2, 486 + up(v)
    s.pill("Nombre (fondo)", WHITE, pill, 56, op=lambda v: 1.0 if reach(v) > 4 else 0.0)
    s.mask_to(t.tracks[-1].clips[-1], lambda v: (353, 200, 1920, 560))
    name = s.txt("CHANNEL NAME", (486, 415, 851, 447), M, 800, MAROON, "Nombre del canal",
                 g=lambda v: (0, up(v), 1, 0, 1.0))
    s.mask_to(name, lambda v: (353, 250, 353 + reach(v) - 40, 520))

    def av(v):
        sc = popin(v, 25.03, 0.26) * (1.0 if v < 30.47 else popout(v, 30.47, 0.12))
        return 0, up(v), sc, 1.0 if v > 25.03 else 0.0
    s.picture("fx-man-02", 353, 430, 80, 6, av)
    s.sparks(353, 430, 25.2, n=10, r0=80, r1=180, dur=0.7)
    s.sparks(353, 323, 30.56, n=8, r0=20, r1=120, dur=0.5, size=(6, 14))
    s.arrow([(26.35, 722, 626), (26.55, 589, 542), (26.9, 455, 455), (27.4, 452, 458), (27.65, 450, 575),
             (28.1, 450, 578), (28.45, 448, 690), (28.95, 448, 692), (29.3, 370, 770)], 26.33, 29.25,
            clicks=(27.22, 27.87, 28.75))
    return t


# --- 5. Round picture with like / YouTube / bell circles that fly out and orbit back in (30.75-36.4 s) -------------
def orbit_sunset():
    O, D = 30.75, 5.65
    t = _p("foto-orbita", "Foto redonda con iconos que giran", "Round picture with orbiting icons", 17804, D, 3.6,
           ["foto", "círculo", "me gusta", "campana"])
    s = Y(t, D, O)
    CX, CY = 1423, 493
    BLUE, OR = "#1252F7", "#F78D12"
    spots = (("yt", 1726, 650, 33.25, GREY, RED, 64), ("bell", 1150, 682, 33.92, GREY, OR, 82),
             ("like", 1406, 194, 32.2, BLUE, BLUE, 88))
    for kind, fx, fy, c, b, a, size in spots:
        a0 = math.atan2(fy - CY, fx - CX)
        d0 = math.hypot(fx - CX, fy - CY)

        def g(v, a0=a0, d0=d0):
            q = E(v, 31.12, 0.4)
            turn = -100 * (1 - E(v, 31.12, 0.75)) + 230 * E(v, 34.75, 0.9)
            ang = a0 + math.radians(turn)
            d = d0 * (0.45 + 0.55 * q) * (1 - ein(v, 35.48, 0.24, 1.8))
            sc = (0.4 + 0.6 * q) * (1 - 0.5 * E(v, 35.48, 0.24))
            return CX + math.cos(ang) * d, CY + math.sin(ang) * d, sc, (1.0 if 31.12 < v < 35.72 else 0.0), turn
        s.icon(kind, 82, g, c=c, before=b, after=a, size=size, name={"yt": "YouTube", "bell": "Campana",
                                                                     "like": "Me gusta"}[kind])

    def av(v):
        sc = popin(v, 30.95, 0.3) * (grow_shrink(v, 35.5, 0.15, 1.15, 0.6, 0.18) if v > 35.5 else 1.0)
        return 0, 0, sc, 1.0 if v > 30.95 else 0.0
    s.picture("fx-couple-01", CX, CY, 146, 13, av, rot=lambda v: -150 * E(v, 34.85, 0.8))
    s.sparks(CX, CY, 31.12, n=12, r0=120, r1=280, dur=0.8)
    s.sparks(CX, CY, 36.3, n=10, r0=30, r1=180, dur=0.6, size=(6, 14))
    return t


# --- 6. Bigger picture: the three circles burst out of it, light up one by one (36.7-42.2 s) -----------------------
def orbit_skater():
    O, D = 36.7, 5.5
    t = _p("foto-iconos", "Foto con iconos que salen de ella", "Picture with icons bursting out", 17805, D, 3.0,
           ["foto", "círculo", "me gusta", "campana"])
    s = Y(t, D, O)
    CX, CY = 1256, 474
    BLUE, OR = "#1A5CF0", "#FEA32D"
    spots = (("yt", 1034, 200, 38.4, "#111111", RED, 64), ("bell", 1624, 380, 39.1, GREY, OR, 82),
             ("like", 990, 652, 37.8, GREY, BLUE, 86))
    for kind, fx, fy, c, b, a, size in spots:
        def g(v, fx=fx, fy=fy):
            q = popin(v, 36.98, 0.34, 1.2)
            p = ein(v, 41.52, 0.2, 1.5)
            k = (0.08 + 0.92 * q) * (1 - p)
            return CX + (fx - CX) * k, CY + (fy - CY) * k, (0.4 + 0.6 * E(v, 36.9, 0.2)) * (1 - 0.5 * p), (
                1.0 if 36.88 < v < 41.72 else 0.0)
        s.icon(kind, 82, g, c=c, before=b, after=a, size=size, name={"yt": "YouTube", "bell": "Campana",
                                                                     "like": "Me gusta"}[kind])

    def av(v):
        sc = popin(v, 37.02, 0.28) * (grow_shrink(v, 41.55, 0.14, 1.2, 0.3, 0.16) if v > 41.55 else 1.0)
        return 0, 0, sc, 1.0 if v > 37.02 else 0.0
    s.picture("fx-skater-01", CX, CY, 178, 12, av)
    s.sparks(CX, CY, 36.8, n=8, r0=20, r1=120, dur=0.5, size=(5, 10))
    s.sparks(CX, CY, 42.05, n=10, r0=30, r1=200, dur=0.6, size=(6, 14))
    return t


# --- 7. Three round buttons like / YouTube / bell, grey, clicked into colour (42.35-47.3 s) -----------------------
def three_buttons():
    O, D = 42.35, 4.95
    t = _p("tres-botones", "Tres botones redondos", "Three round buttons", 17806, D, 3.5,
           ["me gusta", "campana", "clic", "grande"])
    s = Y(t, D, O)
    PALE, BLUE, OR = "#F1F1F1", "#419CFB", "#FEA32D"
    Y_ = 860

    def bell_g(v):
        sc = 1.0 if v < 46.5 else 1 - E(v, 46.5, 0.1)
        x = 1210 - 234 * E(v, 46.48, 0.14)
        return x, Y_, sc, 1.0 if 43.06 < v < 46.62 else 0.0

    def yt_g(v):
        x = 1210 - 234 * E(v, 43.2, 0.22)
        if v < 46.6:
            sc = 1.0
        else:
            sc = grow_shrink(v, 46.6, 0.18, 1.3, 0.25, 0.2)
        return x, Y_, sc, 1.0 if v > 43.16 else 0.0

    def like_g(v):
        sc = popin(v, 42.55, 0.22)
        x = 1210 - 472 * E(v, 43.06, 0.3) + 238 * E(v, 46.48, 0.14)
        return x, Y_, sc, 1.0 if 42.55 < v < 46.62 else 0.0
    s.icon("bell", 104, bell_g, c=45.62, before=GREY, after=OR, size=100, disc=PALE, name="Campana", press_disc=True)
    made = s.icon("yt", 104, yt_g, c=44.72, before=GREY, after="#FF0202", size=70, disc=PALE, name="YouTube",
                  press_disc=True)
    tilt = [m for m in made]
    for m in tilt:
        m["rotation"] = keys([(u, round(-20 * E(u + O, 46.62, 0.18), 3), "linear") for u in frames_of(D)])
    for m in s.icon("like", 104, like_g, c=43.75, before=GREY, after=BLUE, size=98, disc=PALE, name="Me gusta",
                    press_disc=True):
        s.mblur(m)
    for x, c in ((738, 43.78), (976, 44.75), (1210, 45.65)):
        s.sparks(x, Y_, c, n=6, r0=95, r1=150, dur=0.35, size=(8, 12), kinds="d")
    s.sparks(976, Y_, 47.15, n=8, r0=20, r1=150, dur=0.5, size=(6, 12))
    s.arrow([(43.3, 775, 930), (43.55, 760, 895), (44.1, 760, 895), (44.4, 960, 885), (44.5, 990, 900),
             (44.95, 990, 900), (45.3, 1180, 935), (45.45, 1228, 905), (45.95, 1228, 905), (46.2, 1295, 985)],
            43.3, 46.12, clicks=(43.72, 44.69, 45.59))
    return t


# --- 8. Picture with bubbles; like, YouTube and bell pop out of bubbles beside it (47.3-54.85 s) ------------------
def bubbles():
    O, D = 47.3, 7.55
    t = _p("foto-burbujas", "Foto con burbujas e iconos", "Picture with bubbles and icons", 17807, D, 3.5,
           ["foto", "burbujas", "me gusta", "campana"])
    s = Y(t, D, O)
    CX, CY = 420, 566
    BLUE, OR = "#2D8CF8", "#FEA32D"
    rnd = random.Random(1212)
    for i in range(26):
        x, y = rnd.uniform(160, 960), rnd.uniform(160, 960)
        if math.hypot(x - CX, y - CY) < 200:
            continue
        a = rnd.uniform(47.7, 50.6)
        life = rnd.uniform(0.8, 1.7)
        d = rnd.uniform(8, 34)

        def g(v, x=x, y=y, a=a, life=life, d=d):
            q = L(v, a, life)
            on = a <= v < a + life
            return x, y - 50 * q, d * (0.3 + 0.7 * min(1.0, 4 * q)), (min(1.0, 3 * (1 - q)) if on else 0.0)
        s.disc(f"Burbuja {i + 1}", ring(WHITE, 2.4), g)
    spots = (("like", 880, 340, 48.5, 52.35, BLUE, 74), ("yt", 726, 524, 49.35, 53.35, RED, 50),
             ("bell", 800, 744, 50.05, 54.28, OR, 72))
    for kind, x, y, a, b, col, size in spots:
        s.disc(f"Burbuja ({kind})", ring(WHITE, 3), lambda v, a=a, x=x, y=y: (x, y, 60 + 40 * L(v, a - 0.15, 0.15),
                                                                               1.0 if a - 0.15 <= v < a else 0.0))

        def g(v, a=a, b=b, x=x, y=y):
            sc = popin(v, a, 0.24) * (1.0 if v < b else popout(v, b, 0.16))
            return x, y, max(1e-3, sc), 1.0 if a < v < b + 0.16 else 0.0
        s.icon(kind, 72, g, c=None, before=col, size=size, name={"yt": "YouTube", "bell": "Campana",
                                                                 "like": "Me gusta"}[kind])
        s.disc(f"Punto ({kind})", ring(WHITE, 2.4), lambda v, b=b, x=x, y=y: (x, y, 16 + 14 * L(v, b + 0.12, 0.3),
                                                                             1.0 if b + 0.12 <= v < b + 0.42 else 0.0))

    def av(v):
        sc = popin(v, 47.52, 0.36, 1.0) * (grow_shrink(v, 54.25, 0.2, 1.25, 0.15, 0.15) if v > 54.25 else 1.0)
        return 0, 0, sc, 1.0 if v > 47.52 else 0.0
    s.picture("fx-woman-05", CX, CY, 164, 13, av)
    s.sparks(CX, CY, 54.72, n=8, r0=20, r1=120, dur=0.5, size=(6, 12))
    return t


# --- 9. Picture with like and bell sliding out to its sides and YouTube above; clicked one by one (54.97-59.6 s) ---
def side_icons():
    O, D = 54.97, 4.65
    t = _p("foto-lados", "Foto con iconos a los lados", "Picture with icons at its sides", 17808, D, 3.2,
           ["foto", "me gusta", "campana", "clic"])
    s = Y(t, D, O)
    CX, CY = 970, 796
    BLUE, OR = "#1A5CF0", "#FEA32D"
    back = lambda v: E(v, 59.04, 0.12)  # noqa: E731
    spots = (("like", 712, 796, 55.5, 56.62, GREY, BLUE, 68), ("bell", 1228, 796, 55.5, 58.45, GREY, OR, 70),
             ("yt", 972, 540, 56.0, 57.52, RED, "#111111", 46))
    for kind, x, y, a, c, b, col, size in spots:
        def g(v, x=x, y=y, a=a):
            k = E(v, a, 0.18) * (1 - back(v))
            return CX + (x - CX) * k, CY + (y - CY) * k, 0.6 + 0.4 * E(v, a, 0.18), 1.0 if a < v < 59.16 else 0.0
        s.icon(kind, 72, g, c=c, before=b, after=col, size=size, name={"yt": "YouTube", "bell": "Campana",
                                                                       "like": "Me gusta"}[kind])

    def av(v):
        sc = popin(v, 55.15, 0.3) * (grow_shrink(v, 59.12, 0.16, 1.25, 0.12, 0.15) if v > 59.12 else 1.0)
        return 0, 0, sc, 1.0 if v > 55.15 else 0.0
    s.picture("fx-hair-02", CX, CY, 144, 12, av)
    s.sparks(CX, CY, 55.35, n=10, r0=110, r1=230, dur=0.7)
    s.sparks(CX, CY, 59.5, n=8, r0=20, r1=140, dur=0.5, size=(6, 12))
    s.arrow([(55.95, 760, 945), (56.4, 730, 830), (56.85, 730, 830), (57.2, 985, 580), (57.75, 985, 580),
             (58.15, 1245, 830), (58.6, 1250, 832), (58.85, 1310, 900)], 55.93, 58.75, clicks=(56.58, 57.48, 58.42))
    return t


# --- 10. Picture whose circles drip out of it like liquid and are swallowed back (59.9-64.75 s) -------------------
def liquid():
    O, D = 59.9, 4.85
    t = _p("foto-liquida", "Foto con iconos líquidos", "Picture with liquid icons", 17809, D, 3.3,
           ["foto", "líquido", "me gusta", "campana", "clic"])
    s = Y(t, D, O)
    BLUE, OR = "#1A5CF0", "#FEA32D"
    IX = 1652
    ys = {"like": 380, "yt": 610, "bell": 840}
    gone = {"yt": 63.62, "like": 64.04, "bell": 64.42}

    def apos(v):
        x = 1292 + (IX - 1292) * E(v, 63.3, 0.36)
        y = 606 + (610 - 606) * E(v, 63.3, 0.36)
        y += (380 - 610) * E(v, 63.93, 0.13) + (840 - 380) * E(v, 64.3, 0.14)
        return x, y

    def ipos(kind, v):
        q = E(v, 60.05, 0.26)
        return 1292 + 120 + (IX - 1292 - 120) * q, 606 + (ys[kind] - 606) * q

    def neck_h(kind):
        def h(v):
            if v < 60.05 or v > gone[kind]:
                return 0.0
            if v < 61:
                return 150 * (1 - E(v, 60.22, 0.26))
            if kind == "yt":
                return 0.0
            near = E(v, 63.15, 0.25)
            if kind == "bell":
                near *= 1 - E(v, 63.92, 0.1)
            return 170 * near
        return h
    for kind in ("like", "yt", "bell"):
        s.neck(f"Unión ({kind})", apos, lambda v, kind=kind: ipos(kind, v), neck_h(kind))
    spots = (("like", 60.72, BLUE, 92), ("yt", 61.7, RED, 62), ("bell", 62.5, OR, 90))
    for kind, c, col, size in spots:
        def g(v, kind=kind):
            x, y = ipos(kind, v)
            return x, y, 0.2 + 0.8 * E(v, 60.05, 0.26), 1.0 if 60.05 < v < gone[kind] else 0.0
        s.icon(kind, 92, g, c=c, before=GREY, after=col, size=size, name={"yt": "YouTube", "bell": "Campana",
                                                                          "like": "Me gusta"}[kind])
        s.sparks(IX, ys[kind], c + 0.03, n=6, r0=90, r1=140, dur=0.35, size=(8, 12), kinds="d")

    def av(v):
        x, y = apos(v)
        sc = popin(v, 59.95, 0.22) * (1.0 if v < 64.55 else popout(v, 64.55, 0.16))
        return x - 1292, y - 606, sc, 1.0 if v > 59.95 else 0.0
    s.picture("portrait-03", 1292, 606, 168, 12, av)
    s.sparks(IX, 840, 64.68, n=8, r0=20, r1=120, dur=0.5, size=(6, 12))
    s.arrow([(60.08, 1740, 520), (60.5, 1680, 410), (60.95, 1680, 410), (61.35, 1680, 640), (61.95, 1680, 642),
             (62.3, 1680, 870), (62.75, 1685, 872), (63.0, 1760, 960)], 60.06, 62.9, clicks=(60.68, 61.66, 62.46))
    return t


# --- 11. LIKE / SUBSCRIBE / GET NOTIFIED white pills that swing in, icons clicked into colour (64.95-69.4 s) -------
def pill_list():
    O, D = 64.95, 4.45
    t = _p("lista-botones", "Lista me gusta, suscribirse y notificaciones", "Like, subscribe and get notified list",
           17810, D, 3.2, ["lista", "me gusta", "campana", "clic"], section="redes")
    s = Y(t, D, O)
    INK, BLUE, OR, YR = "#5C5C5C", "#15AAE3", "#FEA32D", "#ED1C33"
    rows = (("like", 290, 598, 64.95, -1, 66.2, BLUE, "LIKE", (420, 332, 545, 368), 90),
            ("yt", 445, 738, 65.25, 1, 67.05, YR, "SUBSCRIBE", (416, 487, 698, 523), 66),
            ("bell", 600, 803, 65.55, -1, 67.75, OR, "GET NOTIFIED", (420, 642, 757, 678), 88))
    for i, (kind, y0, x1, a, side, c, col, word, ink, size) in enumerate(rows):
        y1 = y0 + 117
        cy = (y0 + y1) / 2
        fall = 600 + 58.5 - cy  # down to the last row

        def off(v, a=a, side=side, fall=fall, i=i):
            q = E(v, a, 0.25)
            dx = side * 260 * (1 - q)
            rot = side * 11 * (1 - q)
            dy = fall * (E(v, 68.95, 0.15) if i == 0 else E(v, 68.92, 0.12)) if i < 2 else 0.0
            dy -= 55 * E(v, 68.38, 0.14) * (1 - E(v, 68.95, 0.15)) if i == 0 else 0.0
            op = (1.0 if v > a else 0.0) * (1.0 if (i == 2 or v < 69.12) else 0.0)
            return dx, dy, rot, op

        def gate(v, i=i):  # the last pill shrinks to its bell
            return 1.0 if i < 2 else 1 - E(v, 69.12, 0.12)

        def pg(v, y0=y0, y1=y1, x1=x1, off=off, gate=gate):
            dx, dy, rot, op = off(v)
            w = 58 + (x1 - 236 - 58) * gate(v)
            return 236 + w / 2 + dx, (y0 + y1) / 2 + dy, w, y1 - y0, rot, op * (1 - E(v, 69.28, 0.08))
        s.shp(f"Fila {i + 1}", solid(WHITE), pg, radius=58.5, base=(x1 - 236, y1 - y0))
        for m in s.sym(kind, lambda v, off=off, cy=cy: (lambda o: (330 + o[0], cy + o[1], 1 - E(v, 69.26, 0.1), o[2],
                                                                   o[3]))(off(v)), size, c, GREY, col, word.title()):
            s.mblur(m)
        w = s.txt(word, ink, M, 800, INK, word.title(),
                  g=lambda v, off=off: (lambda o: (o[0], o[1], 1, o[2], o[3]))(off(v)))
        s.mblur(w)
        s.mask_to(w, lambda v, pg=pg: (lambda r: (r[0] - r[2] / 2, r[1] - r[3] / 2, r[0] + r[2] / 2 - 30,
                                                  r[1] + r[3] / 2))(pg(v)))
    for m in t.tracks:
        for c_ in m.clips:
            if c_.get("name", "").startswith("Fila"):
                s.mblur(c_)
    s.arrow([(65.15, 220, 442), (65.5, 300, 400), (66.0, 345, 375), (66.4, 345, 378), (66.8, 345, 532),
             (67.25, 345, 535), (67.55, 345, 690), (68.0, 348, 692), (68.3, 420, 790)], 65.15, 68.2,
            clicks=(66.17, 67.02, 67.72))
    return t


# --- 12. Grey card under a big picture: SUBSCRIBE fills into an outline, like and bell (70.2-75.95 s) ------------
def card_grey():
    O, D = 70.2, 5.75
    t = _p("tarjeta-gris", "Tarjeta gris con foto grande", "Grey card with a big picture", 17811, D, 4.2,
           ["tarjeta", "me gusta", "campana", "clic"])
    s = Y(t, D, O)
    PINK, CARD, BLUE, OR = "#F2295B", "#EBEBEB", "#198AC5", "#FEA32D"

    def card(v):
        q = E(v, 70.22, 0.32)
        c = E(v, 75.4, 0.14)
        y1 = 380 + (826 - 380) * q - (826 - 400) * c
        x0, x1 = 240, 752
        return (x0 + x1) / 2, (307 + y1) / 2, x1 - x0, max(1e-3, y1 - 307), 0, (
            1.0 if v > 70.22 else 0.0) * (1 - E(v, 75.56, 0.08))
    s.shp("Tarjeta", solid(CARD), card, radius=60, base=(512, 519))
    box = lambda v: (lambda g: (g[0] - g[2] / 2, g[1] - g[3] / 2, g[0] + g[2] / 2, g[1] + g[3] / 2))(card(v))  # noqa
    wipe = lambda v: 280 + 431 * E(v, 70.44, 0.18) if v < 75.2 else 280 + 431 * (1 - E(v, 75.22, 0.16))  # noqa

    def btn(after):
        def g(v):
            p = squeeze(v, 72.1)
            return 495.5, 573, 431 * p, 96 * p, 0, 1.0 if (v >= 72.1) == after and v > 70.44 else 0.0
        return g
    made = [s.shp("Suscribirse (fondo)", solid(PINK), btn(False), radius=10, base=(431, 96)),
            s.shp("Suscrito (fondo)", [fill(CARD), stroke(PINK, 5, "inside")], btn(True), radius=10, base=(431, 96))]
    tg = lambda after: (lambda v: (0, 0, max(1e-3, squeeze(v, 72.1)), 0, 1.0 if (v >= 72.1) == after else 0.0))  # noqa
    made.append(s.txt("SUBSCRIBE", (327, 553, 664, 593), M, 800, WHITE, "Suscribirse", g=tg(False)))
    made.append(s.txt("SUBSCRIBED", (310, 553, 682, 593), M, 800, PINK, "Suscrito", g=tg(True)))
    for m in made:
        s.mblur(m)
        s.mask_to(m, lambda v: (240, 500, wipe(v), 650))
    gi = lambda x, y: (lambda v: (x, y, popin(v, 70.5, 0.2), 0, 1.0 if v < 75.38 else 0.0))  # noqa: E731
    for m in s.sym("like", gi(405, 717), 90, 73.2, GREY, BLUE, "Me gusta") + s.sym("bell", gi(595, 714), 96, 74.2,
                                                                                 "#838383", OR, "Campana"):
        s.mask_to(m, box)

    def av(v):
        sc = popin(v, 70.4, 0.32, 1.0) * (1.0 if v < 75.82 else popout(v, 75.82, 0.14))
        return 0, 0, sc, 1.0 if v > 70.4 else 0.0
    s.picture("y6-gamer-01", 496, 344, 148, 12, av, ring_col="#A3A3A3")
    s.sparks(496, 344, 75.92, n=8, r0=30, r1=170, dur=0.55, size=(6, 14))
    s.arrow([(71.25, 245, 640), (71.7, 290, 610), (72.35, 300, 600), (72.7, 400, 735), (73.4, 410, 740),
             (73.8, 600, 735), (74.45, 605, 740), (74.85, 780, 760)], 71.25, 74.75, clicks=(72.07, 73.17, 74.17))
    return t


# --- 13. Grey capsule with three circles; each click opens its LIKE / SUBSCRIBE / GET NOTIFIED pill (76.45-84.9 s) -
def capsule_list():
    O, D = 76.45, 8.45
    t = _p("lista-capsula", "Lista en cápsula con me gusta, suscribirse y notificaciones",
           "Capsule list with like, subscribe and get notified", 17812, D, 6.0,
           ["lista", "me gusta", "campana", "clic"], section="redes")
    s = Y(t, D, O)
    CAP, INK, BLUE, OR, YR = "#B7B7B7", "#979797", "#065FD3", "#FEBA17", "#FF0000"
    X = 372

    def gather(v):  # 1 while open; the circles come together at the end
        return 1 - E(v, 83.95, 0.4)

    def cy(i, v):
        return 520 + (i - 1) * 200 * gather(v)

    def capsule(v):
        h = 198 + (593 - 198) * E(v, 76.95, 0.4)
        h = 198 + (h - 198) * gather(v) if v > 83.9 else h
        w = 198 * popin(v, 76.6, 0.24, 1.2)
        k = 1.0 if v < 84.45 else popout(v, 84.45, 0.16)
        return X, 518.5, w * k, h * k, 0, 1.0 if 76.6 < v else 0.0
    s.shp("Cápsula", solid(CAP, 0.85), capsule, radius=99, base=(198, 593))
    rows = (("like", 78.25, BLUE, "LIKE", 710, (520, 296, 642, 340), 83.6, 100),
            ("yt", 79.0, YR, "SUBSCRIBE", 865, (505, 500, 823, 542), 83.38, 70),
            ("bell", 80.05, OR, "GET NOTIFIED", 922, (498, 700, 885, 743), 83.12, 98))
    for i, (kind, c, col, word, x1, ink, back, size) in enumerate(rows):
        y = 320 + 200 * i

        def reach(v, c=c, back=back, x1=x1):
            return (x1 - X) * E(v, c + 0.1, 0.25) * (1 - E(v, back, 0.2))

        def pg(v, y=y, reach=reach, x1=x1):
            r = reach(v)
            return X + r - (x1 - X) / 2, y, x1 - X, 131, 0, 1.0 if r > 3 else 0.0
        s.shp(f"Fila {i + 1}", solid(WHITE), pg, radius=65.5, base=(x1 - X, 131))
        s.mask_to(t.tracks[-1].clips[-1], lambda v: (X, 0, 1920, 1080))
        w = s.txt(word, ink, M, 800, INK, word.title())
        s.mask_to(w, lambda v, reach=reach, y=y: (X, y - 70, X + reach(v) - 50, y + 70))
    for i in range(3):  # the three dots of the closed capsule
        s.disc(f"Punto {i + 1}", solid(WHITE), lambda v, i=i: (X, 520 + (i - 1) * 34 * (1 + 4 * E(v, 76.95, 0.3)),
                                                             26 * popin(v, 76.66 + 0.04 * i, 0.2),
                                                             1.0 - E(v, 77.05, 0.12)))
    for i, (kind, c, col, word, x1, ink, back, size) in reversed(list(enumerate(rows))):
        alive = lambda v, i=i: 1.0 if v > 77.05 and (i == 0 or v < 84.35) else 0.0  # noqa: E731
        k_ = lambda v: 1.0 if v < 84.45 else popout(v, 84.45, 0.16)  # noqa: E731
        s.disc(f"{word.title()} (círculo)", solid(WHITE),
               lambda v, i=i, c=c: (X, cy(i, v), 168 * popin(v, c, 0.22) * k_(v), alive(v)))
        g = (lambda v, i=i: (X, cy(i, v), max(1e-3, (0.5 + 0.5 * E(v, 77.05, 0.2)) * k_(v)), 0.0,
                             alive(v) * E(v, 77.05, 0.08)))
        s.sym(kind, g, size, c, YR if kind == "yt" else WHITE, col, word.title())
    s.sparks(X, 520, 84.55, n=8, r0=20, r1=120, dur=0.5, size=(6, 12))
    s.arrow([(77.15, 430, 620), (77.6, 395, 365), (78.45, 395, 365), (78.75, 395, 560), (79.2, 395, 562),
             (79.6, 395, 762), (80.25, 398, 765), (80.55, 470, 860)], 77.15, 80.45, clicks=(78.22, 78.97, 80.02))
    return t


TEMPLATES = [name_bar, teacher_bar, card_pink, channel_card, orbit_sunset, orbit_skater, three_buttons, bubbles,
             side_icons, liquid, pill_list, card_grey, capsule_list]
