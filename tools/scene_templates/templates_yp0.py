"""YOUTUBE PACK video 0 as Stock templates (yp0-*). See docs/plan-youtube-pack.md.

The subscribe widgets of 38664567.mp4 (1920×1080, 54 s), each one studied on 10 fps sheets and laid out where it
sits in the reference: a card with the channel's picture and «SUBSCRIBE» that a hand cursor clicks into a grey
«SUBSCRIBED», cards and bars with like / dislike / bell icons the cursor also clicks (the like turns red, the bell
rings), a bar with a followers counter that keeps rolling, a big like–subscribe–bell row with three cursors, and
three social bars with «FOLLOW». Overlays: no background of their own. Times are the reference's seconds (each
piece starts at its own `o`). Kit de YouTube › Elementos / Redes; order 12000-. Study notes in
tienda/plantillas/estudio-38664567/NOTAS.md.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from scene import gradient, keys, no_stroke
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import S, arc, fill, lin, poly, ring

WHITE, BLACK, RED = "#FFFFFF", "#000000", "#FF0000"
INK = "#232323"
GREY = "#B0B0B0"
YELLOW = "#FED700"
M, ROBOTO = "Montserrat", "Roboto"
for _w, _f in ((900, "Black"), (700, "Bold"), (500, "Medium"), (400, "Regular")):
    f6._FILES[(ROBOTO, _w)] = f"fonts.basic/fonts/roboto/Roboto-{_f}.ttf"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"

# A pointing hand (the reference's cursor): grid 20 × 26, the finger tip at (7, 0).
_HAND = [(5, 1.2), (5.6, 0.2), (7, 0), (8.4, 0.2), (9, 1.2), (9, 8), (9.6, 7.5), (11.6, 7.5), (12.4, 8.4), (13.2, 8),
         (15.2, 8), (16, 9), (16.8, 9.2), (18.8, 9.6), (19.6, 10.8), (20, 12), (20, 18), (18, 22), (18, 26), (7, 26),
         (7, 23), (3, 18.5), (0.3, 14), (0, 12.6), (0.6, 11.2), (2, 10.8), (3.2, 11.4), (5, 13.6)]
HAND = poly([(x * 5, y * 100 / 26) for x, y in _HAND])
HAND_LINES = " ".join(f"M {x0 * 5:.2f} {y0 * 100 / 26:.2f} L {x1 * 5:.2f} {y1 * 100 / 26:.2f}" for x0, y0, x1, y1 in
                      ((9, 8, 9, 12.5), (12.8, 8.6, 12.8, 12.6), (16.4, 9.4, 16.4, 13), (7, 23, 18, 23)))
TIP = 0.35
THUMB = ("M 30 45 L 50 8 C 60 8 64 16 62 26 L 58 40 L 88 40 C 96 40 100 48 98 56 L 90 88 C 88 94 84 96 78 96 "
         "L 30 96 Z M 5 45 L 22 45 L 22 96 L 5 96 Z")
BELL = ("M 50 10 C 30 10 20 26 20 46 L 20 64 L 8 80 L 92 80 L 80 64 L 80 46 C 80 26 70 10 50 10 Z "
        "M 38 86 C 38 99 62 99 62 86 Z M 43 9 C 43 0 57 0 57 9 Z")
WAVES = arc(200, 248, 12) + " " + arc(-68, -20, 12)
BIRD = ("M 98 22 C 94 24 90 25 86 25 C 90 22 93 18 94 14 C 90 16 86 18 82 19 C 78 15 73 13 67 13 C 56 13 47 22 47 33 "
        "C 47 35 47 36 48 38 C 31 37 17 29 7 17 C 5 20 4 24 4 28 C 4 35 8 41 13 44 C 10 44 7 43 4 42 C 4 52 11 61 21 63 "
        "C 17 64 14 64 11 63 C 14 72 22 79 32 79 C 24 85 15 89 4 89 C 3 89 1 89 0 89 C 10 95 21 99 33 99 "
        "C 67 99 86 71 86 46 L 86 43 C 91 40 95 36 98 32 Z")


def _turn(path, fx=True, fy=True):
    """The path turned half a turn (a thumbs-down from the thumbs-up)."""
    out, nums = [], []
    for tok in path.replace(",", " ").split():
        if tok.isalpha():
            out.append(tok)
        else:
            out.append(tok)
            nums.append(len(out) - 1)
    for j, idx in enumerate(nums):
        v = float(out[idx])
        flip = fx if j % 2 == 0 else fy
        out[idx] = f"{100 - v:.2f}" if flip else f"{v:.2f}"
    return " ".join(out)


THUMB_DOWN = _turn(THUMB)


def stroke(colour, width, align="center"):
    return {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": align, "opacity": 1.0,
            "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}


def E(v, a, d):
    """Smooth 0 → 1 from second a over d seconds."""
    return k(v * FPS, a * FPS, max(1e-3, d) * FPS)


def L(v, a, d):
    return lin(v, a, max(1e-3, d))


def ein(v, a, d, p=2.4):
    return L(v, a, d) ** p


def path_at(pts, v):
    """A point moving through waypoints [(second, x, y)], easing between each pair."""
    if v <= pts[0][0]:
        return pts[0][1], pts[0][2]
    for (a, xa, ya), (b, xb, yb) in zip(pts, pts[1:]):
        if v <= b:
            q = E(v, a, b - a)
            return xa + (xb - xa) * q, ya + (yb - ya) * q
    return pts[-1][1], pts[-1][2]


def squeeze(v, c):
    """A button pressed at second c: it shrinks, swaps, springs a little bigger and settles."""
    if c is None or v < c - 0.18:
        return 1.0
    if v < c:
        return 1 - 0.14 * E(v, c - 0.18, 0.18)
    if v < c + 0.12:
        return 0.86 + 0.19 * E(v, c, 0.12)
    return 1.05 - 0.05 * E(v, c + 0.12, 0.15)


def _vals(prop, n):
    kf = prop["keyframes"]
    return [kf[0]["value"]] * n if len(kf) == 1 else [p["value"] for p in kf]


class W(S):
    """A widget: no background, no automatic exit; every geometry is a function of the reference's second v."""

    def __init__(self, t, dur, o):
        super().__init__(t, dur)
        self.o = o

    def frame(self, u):
        return u * FPS

    def shp(self, name, layers, g, **kw):
        return self.obj(name, layers, lambda fr, u: g(u + self.o), **kw)

    def txt(self, content, ink, family, weight, colour, name, g=None, op=None, align="center", editable=True,
            layers=None):
        return self.say(content, ink, family, weight, colour, name, align=align, editable=editable, layers=layers,
                        geom=(lambda fr, u: g(u + self.o)) if g else None,
                        op=(lambda fr, u: op(u + self.o)) if op else None)

    def mask_to(self, clip, rect):
        """Shows the clip only inside rect(v) = (x0, y0, x1, y1) on screen (the clip may move and scale)."""
        us_ = frames_of(self.dur)
        n = len(us_)
        X, Y, Wd, H = (_vals(clip[p], n) for p in ("x", "y", "width", "height"))
        mk = {"x": [], "y": [], "w": [], "h": []}
        for i, u in enumerate(us_):
            x0, y0, x1, y1 = rect(u + self.o)
            bw, bh = max(1e-3, Wd[i]), max(1e-3, H[i])
            mk["x"].append((u, ((x0 + x1) / 2 - X[i]) / bw, "linear"))
            mk["y"].append((u, ((y0 + y1) / 2 - Y[i]) / bh, "linear"))
            mk["w"].append((u, max(1e-4, (x1 - x0) / bw), "linear"))
            mk["h"].append((u, max(1e-4, (y1 - y0) / bh), "linear"))
        track = next(tr for tr in self.t.tracks if clip in tr.clips)
        self.t.mask(track, clip, "rectangle", x=mk["x"][0][1], y=mk["y"][0][1], w=mk["w"][0][1], h=mk["h"][0][1],
                    keyframes={kk: keys(v) for kk, v in mk.items()})

    # --- pieces ------------------------------------------------------------------------------------------------
    def card(self, rect, off, radius=12, name="Tarjeta"):
        """off(v) = (dx, dy, op)."""
        x0, y0, x1, y1 = rect
        return self.shp(name, solid(WHITE), lambda v: (lambda d: ((x0 + x1) / 2 + d[0], (y0 + y1) / 2 + d[1], x1 - x0,
                                                                  y1 - y0, 0, d[2]))(off(v)),
                        radius=radius, base=(x1 - x0, y1 - y0))

    def avatar(self, sample, cx, cy, r, rw, off, name="Foto del canal"):
        """off(v) = (dx, dy, ring scale, photo scale, op, rot): the channel's picture in a red ring."""
        d = 2 * r - rw
        self.shp("Aro", [fill(WHITE), stroke(RED, rw)],
                 lambda v: (lambda o: (cx + o[0], cy + o[1], d * o[2], d * o[2], o[5], o[4]))(off(v)),
                 kind="ellipse", base=(d, d))
        rp = r - rw - 3
        t = self.t
        track = t.track("video", name)
        mo, op, rot = [], [], []
        for u in frames_of(self.dur):
            o = off(u + self.o)
            mo.append((u, {"s": max(1e-3, o[3]), "dx": o[0], "dy": o[1]}, "linear"))
            op.append((u, round(max(0.0, min(1.0, o[4] if o[3] > 0.02 else 0.0)), 4), "linear"))
            rot.append((u, round(o[5], 3), "linear"))
        clip = t.photo(track, sample, 0.0, self.dur, Box(cx - rp, cy - rp, 2 * rp, 2 * rp), mo, label="Tu foto")
        clip["opacity"] = keys(op)
        if any(abs(v[1]) > 1e-6 for v in rot):
            clip["rotation"] = keys(rot)
        t.mask(track, clip, "ellipse")
        return clip

    def badge(self, cx, cy, w, h, off, tri_at, name="YouTube", clip=None):
        """A small YouTube play button; off(v) = (dx, dy, scale, rot, op); its triangle pops at second tri_at."""
        n0 = len(self.t.tracks)
        self.yt(name, lambda fr, u: (lambda o: (cx + o[0], cy + o[1], o[2], o[3], o[4]))(off(u + self.o)), w=w, h=h,
                red=RED, tri=WHITE, tri_at=None if tri_at is None else (tri_at - self.o) * FPS)
        if clip:
            for tr in self.t.tracks[n0:]:
                for c in list(tr.clips):
                    self.mask_to(c, clip)

    def button(self, rect, cap, c, off, radius=12, clip=None, words=("SUBSCRIBE", "SUBSCRIBED"), text_off=None,
               red=RED, grey=GREY, ink=INK, weight=800):
        """A subscribe button pressed at second c; off(v) = (dx, dy, op); text_off(v) = extra dy of its words."""
        x0, y0, x1, y1 = rect
        cx, cy, bw, bh = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0

        def g(v, after):
            dx, dy, op = off(v)
            sc = squeeze(v, c)
            on = c is not None and v >= c
            return cx + dx, cy + dy, bw * sc, bh * sc, 0, op if on == after else 0.0

        def tg(v, after):
            dx, dy, op = off(v)
            sc = squeeze(v, c)
            on = c is not None and v >= c
            return dx, dy + (text_off(v) if text_off else 0.0), sc, 0, op if on == after else 0.0
        made = [self.shp("Botón", solid(red), lambda v: g(v, False), radius=radius, base=(bw, bh))]
        if c is not None:
            made.append(self.shp("Botón (suscrito)", solid(grey), lambda v: g(v, True), radius=radius, base=(bw, bh)))
        pad = bh * 0.25
        made.append(self.txt(words[0], (x0 + pad, cap[0], x1 - pad, cap[1]), M, weight, WHITE, "Suscribirse",
                             g=lambda v: tg(v, False)))
        if c is not None:
            made.append(self.txt(words[1], (x0 + pad * 0.6, cap[0], x1 - pad * 0.6, cap[1]), M, weight, ink,
                                 "Suscrito", g=lambda v: tg(v, True)))
        if clip:
            for m in made:
                self.mask_to(m, clip)
        if text_off:
            for m in made[len(made) // 2:]:
                self.mask_to(m, lambda v: (lambda gg: (gg[0] - gg[2] / 2, gg[1] - gg[3] / 2, gg[0] + gg[2] / 2,
                                                       gg[1] + gg[3] / 2))(g(v, False)))
        return made

    def thumb(self, name, cx, cy, size, c, off, base=INK, on=RED, down=False):
        """A like (or dislike) icon; clicked at second c it turns `on` and pops. off(v) = (dx, dy, rot, op)."""
        path = THUMB_DOWN if down else THUMB

        def g(v, after):
            dx, dy, rot, op = off(v)
            hit = c is not None and v >= c
            p = 1 + (0.22 * math.sin(math.pi * L(v, c, 0.3)) if hit else 0.0)
            return cx + dx, cy + dy, size * p, size * p, rot, op if hit == after else 0.0
        made = [self.shp(name, solid(base), lambda v: g(v, False), path=path, base=(size, size))]
        if c is not None:
            made.append(self.shp(f"{name} (activo)", solid(on), lambda v: g(v, True), path=path, base=(size, size)))
        return made

    def bell(self, cx, cy, bw, bh, c, off, base=INK, on=None, wave_w=None, name="Campana"):
        """A bell; clicked at second c it swings and its waves show (on = its new colour). off = (dx, dy, rot, op)."""
        on = on or base

        def wig(v):
            if c is None or v < c:
                return 0.0
            return 20 * math.sin(2 * math.pi * (v - c) / 0.24) * math.exp(-(v - c) * 3.0)

        def g(v, after):
            dx, dy, rot, op = off(v)
            hit = c is not None and v >= c
            return cx + dx, cy + dy, bw, bh, rot + wig(v), op if hit == after else 0.0
        made = [self.shp(name, solid(base), lambda v: g(v, False), path=BELL, base=(bw, bh))]
        if c is not None:
            made.append(self.shp(f"{name} (sonando)", solid(on), lambda v: g(v, True), path=BELL, base=(bw, bh)))
            ww = wave_w or max(3.0, bh * 0.065)
            for i, f in enumerate((1.0, 1.32)):
                def wg(v, f=f, i=i):
                    dx, dy, rot, op = off(v)
                    q = E(v, c + 0.05 + 0.05 * i, 0.15)
                    s_ = bh * f * (0.8 + 0.2 * q)
                    return cx + dx, cy + dy - bh * 0.08, s_, s_, 0, op * q
                self.shp(f"{name} (ondas {i + 1})", [{"id": "fill", "kind": "fill", "enabled": False,
                                                      "paint": {"kind": "solid", "color": "#00000000"}},
                                                     stroke(on, ww)], wg, path=WAVES, base=(bh * f, bh * f))
        return made

    def burst(self, x, y, c, r0=34, r1=72, ln=16, cols=(RED, INK), width=3.0, dur=0.42, n=8, wave=True,
              name="Destello"):
        """The click: short lines that fly out from (x, y) and a ring that opens."""
        for i in range(n):
            a = 360 * i / n - 90

            def g(v, a=a):
                q = L(v, c, dur)
                r = r0 + (r1 - r0) * (1 - (1 - q) ** 2)
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                return x + ca * r, y + sa * r, ln * (1 - 0.6 * q), width, a, 1.0 if c <= v < c + dur else 0.0
            self.shp(f"{name} {i + 1}", solid(cols[i % len(cols)]), g)
        if wave:
            def wg(v):
                q = L(v, c - 0.03, 0.4)
                d = 16 + 64 * (1 - (1 - q) ** 2)
                return x, y, d, d, 0, (1 - q) if c - 0.03 <= v < c + 0.37 else 0.0
            self.shp(f"{name} (onda)", ring("#F2F2F2", 3), wg, kind="ellipse", base=(80, 80))

    def cursor(self, pts, t_in, t_out, clicks=(), size=(54, 70), name="Cursor"):
        """The hand pointer: its tip through waypoints [(second, x, y)], a small press at each click."""
        def g(v):
            x, y = path_at(pts, v)
            y -= 22
            sc = 1 - sum(0.08 * math.sin(math.pi * L(v, c - 0.1, 0.2)) for c in clicks)
            cw, ch = size[0] * sc, size[1] * sc
            return x + (0.5 - TIP) * cw, y + 0.5 * ch, cw, ch, 0, E(v, t_in, 0.1) * (1 - E(v, t_out, 0.1))
        self.shp(name, [fill(WHITE), stroke(BLACK, 2.6)], g, path=HAND, base=size)
        self.shp(f"{name} (líneas)", ring(BLACK, 2), g, path=HAND_LINES, base=size)


def _p(id, es, en, order, dur, thumb, tags=(), section="elementos"):
    return wide(f"yp0-{id}", es, en, "ytkit", dur, order=order,
                tags=[f"kit:{section}", "youtube", "suscríbete", "botón"] + list(tags), thumb_at=thumb)


def _card_off(v0, rise, out_at, out_by, fade=0.35, rise_d=0.6, out_d=0.42):
    """A card that rises `rise` px fading in from second v0 and drops out `out_by` px from out_at."""
    def off(v):
        dy = rise * (1 - E(v, v0, rise_d)) + out_by * ein(v, out_at, out_d)
        return 0.0, dy, E(v, v0, fade)
    return off


# --- 1. Card: picture, channel name, SUBSCRIBE clicked into SUBSCRIBED (0.05–5.0 s) -------------------------------
def card_name():
    O, D = 0.05, 4.95
    t = _p("tarjeta-canal", "Tarjeta del canal con suscribirse", "Channel card with subscribe", 12000, D, 3.4,
           ["tarjeta", "clic"])
    s = W(t, D, O)
    co = _card_off(0.05, 65, 4.55, 640)
    rect = (190, 520, 540, 938)
    s.card(rect, co)
    cr = lambda v: (rect[0], rect[1] + co(v)[1], rect[2], rect[3] + co(v)[1])  # noqa: E731
    s.avatar("fx-woman-04", 365, 662, 122, 6,
             lambda v: (0, co(v)[1], 0.35 + 0.65 * E(v, 0.12, 0.45), E(v, 0.15, 0.5), E(v, 0.12, 0.06), 0))
    s.badge(440, 753, 68, 46, lambda v: (140 * (1 - E(v, 0.25, 0.4)), co(v)[1], 1, 35 * (1 - E(v, 0.25, 0.4)),
                                         E(v, 0.25, 0.08)), tri_at=0.7)
    s.txt("Youtube/Channel", (200, 805, 530, 831), ROBOTO, 700, INK, "Nombre del canal",
          g=lambda v: (0, co(v)[1] + 32 * (1 - E(v, 0.3, 0.5)), 1, 0, E(v, 0.35, 0.5)))
    s.button((253, 848, 478, 905), (866, 888), 2.32,
             lambda v: (0, co(v)[1] + 91 * (1 - E(v, 0.38, 0.42)), 1.0), radius=10, clip=cr)
    s.burst(378, 858, 2.33)
    s.cursor([(1.2, 480, 1010), (1.6, 395, 905), (2.15, 378, 880), (2.6, 378, 880), (2.8, 470, 995)], 1.15, 2.7,
             clicks=(2.2,))
    return t


# --- 2. Card: picture, SUBSCRIBE and bell / YouTube / like; the cursor clicks the three (5.75–12.7 s) -------------
def card_icons():
    O, D = 5.75, 6.95
    t = _p("tarjeta-iconos", "Tarjeta con suscribirse, me gusta y campana", "Card with subscribe, like and bell",
           12001, D, 6.2, ["tarjeta", "clic", "me gusta", "campana"])
    s = W(t, D, O)
    co = _card_off(5.75, 60, 12.32, 640)
    rect = (190, 485, 540, 975)
    s.card(rect, co)
    cr = lambda v: (rect[0], rect[1] + co(v)[1], rect[2], rect[3] + co(v)[1])  # noqa: E731
    s.avatar("fx-man-01", 367, 636, 122, 6,
             lambda v: (0, co(v)[1], 0.35 + 0.65 * E(v, 5.85, 0.4), E(v, 5.9, 0.45), E(v, 5.85, 0.06), 0))
    side = lambda v: 1 - E(v, 6.85, 0.3)  # noqa: E731
    bell = s.bell(268, 910, 50, 58, 10.85, lambda v: (98 * side(v), co(v)[1], -40 * side(v), E(v, 6.8, 0.05)))
    like = s.thumb("Me gusta", 464, 910, 50, 9.65, lambda v: (-98 * side(v), co(v)[1], 40 * side(v), E(v, 6.8, 0.05)))
    for m in bell + like:
        s.mask_to(m, cr)
    s.badge(366, 910, 84, 58, lambda v: (0, co(v)[1] + 100 * (1 - E(v, 6.3, 0.4)), 1, 0, 1.0), tri_at=6.75, clip=cr)
    s.button((242, 787, 490, 850), (808, 831), 8.72,
             lambda v: (0, co(v)[1] + 188 * (1 - E(v, 5.95, 0.55)), 1.0), radius=12, clip=cr)
    s.burst(392, 840, 8.73)
    s.burst(464, 905, 9.66, r0=30, r1=56, ln=12, cols=(INK,), wave=False)
    s.burst(268, 905, 10.86, r0=32, r1=58, ln=12, cols=(INK,), wave=False)
    s.cursor([(7.6, 427, 1000), (7.9, 400, 902), (8.2, 385, 845), (8.55, 378, 835), (8.95, 400, 860),
              (9.3, 465, 910), (9.85, 470, 912), (10.2, 340, 925), (10.5, 277, 912), (10.95, 275, 908),
              (11.25, 387, 1000)], 7.55, 11.15, clicks=(8.65, 9.6, 10.8))
    return t


# --- 3. Bar along the bottom: picture, name, followers rolling up, like, bell, SUBSCRIBE (12.93–19.93 s) ---------
def bar_followers():
    O, D = 12.93, 7.0
    t = _p("barra-seguidores", "Barra del canal con contador de seguidores", "Channel bar with a followers counter",
           12002, D, 5.6, ["barra", "contador", "seguidores", "me gusta", "campana"])
    s = W(t, D, O)
    out = lambda v: 330 * ein(v, 19.62, 0.28)  # noqa: E731
    s.rect("Barra", solid(WHITE), lambda fr, u: (lambda v: (0, 1080 - 222 * E(v, 12.9, 0.42) + out(v), 1920,
                                                            1090 + out(v)))(u + O))
    s.avatar("fx-woman-02", 195, 920, 137, 8,
             lambda v: (-200 * (1 - E(v, 12.95, 0.6)), out(v), 0.5 + 0.5 * E(v, 12.95, 0.6),
                        0.5 + 0.5 * E(v, 12.95, 0.6), E(v, 12.93, 0.1), -90 * (1 - E(v, 12.95, 0.6))))
    s.txt("Your Channel Name", (360, 915, 1000, 948), ROBOTO, 400, "#2B2B2B", "Nombre del canal", align="left",
          g=lambda v: (105 * (1 - E(v, 13.3, 0.45)), out(v), 1, 0, E(v, 13.3, 0.4)))
    num = s.txt("129704", (358, 993, 520, 1027), ROBOTO, 500, BLACK, "Seguidores", align="left",
                g=lambda v: (0, out(v) + 50 * (1 - E(v, 13.33, 0.35)), 1, 0, E(v, 13.33, 0.15)))
    num["textStyle"].update(counter=True, counterFrom=119600, counterSeconds=6.8)
    s.txt("followers", (545, 999, 687, 1023), ROBOTO, 400, INK, "Texto", align="left",
          g=lambda v: (0, out(v) + 50 * (1 - E(v, 13.4, 0.35)), 1, 0, E(v, 13.45, 0.25)))
    s.thumb("Me gusta", 1145, 969, 70, 17.2,
            lambda v: (0, out(v) + 100 * (1 - E(v, 13.27, 0.5)), -30 * (1 - E(v, 13.27, 0.45)), E(v, 13.27, 0.1)),
            base="#2B2B2B")
    s.txt("256K", (1203, 952, 1318, 988), ROBOTO, 400, "#2B2B2B", "Me gusta (número)", align="left",
          g=lambda v: (20 * (1 - E(v, 13.43, 0.35)), out(v), 1, 0, E(v, 13.43, 0.3)))
    s.bell(1417, 964, 60, 68, 18.25,
           lambda v: (110 * (1 - E(v, 13.6, 0.5)), out(v), 30 * (1 - E(v, 13.6, 0.5)), E(v, 13.58, 0.05)),
           base="#272727")
    s.button((1503, 923, 1862, 1017), (952, 988), 15.82,
             lambda v: (0, out(v) + 110 * (1 - E(v, 13.1, 0.45)), 1.0), radius=14)
    s.burst(1690, 975, 15.83, r0=50, r1=95, ln=20)
    s.burst(1150, 972, 17.21, r0=40, r1=70, ln=14, cols=(INK,), wave=False)
    s.burst(1420, 965, 18.26, r0=42, r1=72, ln=14, cols=(INK,), wave=False)
    s.cursor([(14.75, 1700, 1060), (15.1, 1690, 990), (15.6, 1680, 975), (16.0, 1685, 990), (16.6, 1360, 1010),
              (17.05, 1160, 985), (17.4, 1165, 990), (17.75, 1385, 1000), (18.15, 1420, 978), (18.45, 1425, 985),
              (18.8, 1520, 1080)], 14.7, 18.72, clicks=(15.72, 17.15, 18.2))
    return t


# --- 4. Small card at the right: channel name and SUBSCRIBE (20.05–24.45 s) ----------------------------------------
def card_small():
    O, D = 20.05, 4.4
    t = _p("tarjeta-mini", "Tarjeta pequeña con suscribirse", "Small subscribe card", 12003, D, 3.2,
           ["tarjeta", "clic"])
    s = W(t, D, O)

    def co(v):
        dy = 95 * (1 - E(v, 20.05, 0.6)) + 280 * ein(v, 24.05, 0.36)
        return 0.0, dy, E(v, 20.05, 0.35) * (1 - L(v, 24.33, 0.06))
    rect = (1377, 800, 1726, 975)
    s.card(rect, co)
    cr = lambda v: (rect[0], rect[1] + co(v)[1], rect[2], rect[3] + co(v)[1])  # noqa: E731
    s.txt("Your Channel", (1388, 828, 1715, 863), ROBOTO, 700, INK, "Nombre del canal",
          g=lambda v: (0, co(v)[1] + 20 * (1 - E(v, 20.15, 0.4)), 1, 0, E(v, 20.15, 0.35) * co(v)[2]))
    s.button((1427, 878, 1677, 944), (901, 923), 22.55,
             lambda v: (0, co(v)[1] + 97 * (1 - E(v, 20.38, 0.35)), co(v)[2]), radius=12, clip=cr)
    s.burst(1565, 912, 22.56)
    s.cursor([(21.4, 1632, 1035), (21.6, 1607, 997), (21.8, 1595, 970), (22.3, 1568, 912), (22.65, 1568, 912),
              (22.85, 1632, 1010)], 21.35, 22.8, clicks=(22.45,))
    return t


# --- 5. Bar: picture, like, dislike, SUBSCRIBE (24.75–30.25 s) -------------------------------------------------------
def bar_dislike():
    O, D = 24.75, 5.5
    t = _p("barra-me-gusta", "Barra con me gusta, no me gusta y suscribirse", "Bar with like, dislike and subscribe",
           12004, D, 4.6, ["barra", "clic", "me gusta"])
    s = W(t, D, O)
    co = _card_off(24.75, 100, 30.05, 320, fade=0.3, rise_d=0.5, out_d=0.25)
    rect = (597, 760, 1323, 958)
    s.card(rect, co, radius=16)
    cr = lambda v: (rect[0], rect[1] + co(v)[1], rect[2], rect[3] + co(v)[1])  # noqa: E731
    s.avatar("fx-woman-03", 702, 858, 85, 5,
             lambda v: (0, co(v)[1], 0.2 + 0.8 * E(v, 25.15, 0.35), E(v, 25.2, 0.35), E(v, 25.15, 0.05), 0))
    s.badge(756, 925, 58, 40, lambda v: (0, co(v)[1] - 110 * (1 - E(v, 25.55, 0.4)), 1, 40 * (1 - E(v, 25.55, 0.4)),
                                         E(v, 25.55, 0.05)), tri_at=26.15)
    s.thumb("Me gusta", 867, 858, 60, 29.02,
            lambda v: (-55 * (1 - E(v, 25.5, 0.45)), co(v)[1], -30 * (1 - E(v, 25.5, 0.45)), E(v, 25.5, 0.1)))
    s.thumb("No me gusta", 955, 862, 60, None,
            lambda v: (60 * (1 - E(v, 25.55, 0.45)), co(v)[1], 30 * (1 - E(v, 25.55, 0.45)), E(v, 25.5, 0.05)),
            down=True)
    s.button((1017, 822, 1302, 896), (847, 872), 27.68,
             lambda v: (0, co(v)[1] + 136 * (1 - E(v, 24.98, 0.35)), 1.0), radius=12, clip=cr)
    s.burst(1185, 880, 27.69, r0=44, r1=84, ln=18)
    s.burst(867, 858, 29.03, r0=40, r1=66, ln=12, cols=(INK,), wave=False)
    s.cursor([(26.6, 1207, 976), (26.9, 1196, 920), (27.1, 1185, 901), (27.4, 1185, 883), (27.95, 1185, 883),
              (28.2, 1117, 904), (28.6, 960, 901), (28.95, 885, 880), (29.2, 890, 885), (29.5, 982, 996)],
             26.55, 29.42, clicks=(27.58, 28.97))
    return t


# --- 6. Bar: like, bell, SUBSCRIBE; the cursor clicks the three (30.55–37.3 s) -------------------------------------
def bar_bell():
    O, D = 30.55, 6.75
    t = _p("barra-campana", "Barra con me gusta, campana y suscribirse", "Bar with like, bell and subscribe", 12005,
           D, 5.8, ["barra", "clic", "me gusta", "campana"])
    s = W(t, D, O)
    co = _card_off(30.55, 116, 36.9, 330, fade=0.33, rise_d=0.75, out_d=0.35)
    rect = (690, 758, 1228, 957)
    s.card(rect, co, radius=16)
    cr = lambda v: (rect[0], rect[1] + co(v)[1], rect[2], rect[3] + co(v)[1])  # noqa: E731
    for m in s.thumb("Me gusta", 747, 860, 66, 34.62,
                     lambda v: (0, co(v)[1] + 75 * (1 - E(v, 31.43, 0.4)), -35 * (1 - E(v, 31.43, 0.4)),
                                E(v, 31.43, 0.05))):
        s.mask_to(m, cr)
    s.bell(847, 860, 56, 64, 35.65, lambda v: (70 * (1 - E(v, 31.55, 0.45)), co(v)[1], 35 * (1 - E(v, 31.55, 0.45)),
                                               E(v, 31.5, 0.05)))
    s.button((917, 822, 1200, 896), (847, 872), 33.45,
             lambda v: (0, co(v)[1] + 135 * (1 - E(v, 30.97, 0.35)), 1.0), radius=12, clip=cr)
    s.burst(1062, 860, 33.46, r0=44, r1=84, ln=18)
    s.burst(747, 860, 34.63, r0=40, r1=66, ln=12, cols=(INK,), wave=False)
    s.burst(847, 860, 35.66, r0=40, r1=66, ln=12, cols=(INK,), wave=False)
    s.cursor([(32.3, 1124, 1000), (32.6, 1095, 925), (32.9, 1072, 892), (33.3, 1062, 885), (33.55, 1062, 885),
              (34.0, 915, 907), (34.4, 775, 885), (34.65, 757, 880), (35.0, 820, 885), (35.3, 852, 880),
              (35.75, 852, 880), (36.1, 915, 1036)], 32.25, 36.02, clicks=(33.35, 34.58, 35.6))
    return t


# --- 7. Bar: picture, like, SUBSCRIBE, bell (37.75–45.15 s) --------------------------------------------------------
def bar_channel():
    O, D = 37.75, 7.4
    t = _p("barra-canal", "Barra del canal con me gusta, suscribirse y campana",
           "Channel bar with like, subscribe and bell", 12006, D, 6.2, ["barra", "clic", "me gusta", "campana"])
    s = W(t, D, O)
    co = _card_off(37.75, 120, 44.95, 340, fade=0.35, rise_d=0.6, out_d=0.25)
    rect = (596, 760, 1325, 958)
    s.card(rect, co, radius=16)
    cr = lambda v: (rect[0], rect[1] + co(v)[1], rect[2], rect[3] + co(v)[1])  # noqa: E731
    s.avatar("fx-face-03", 703, 860, 85, 5,
             lambda v: (0, co(v)[1], E(v, 38.15, 0.45), E(v, 38.25, 0.4), E(v, 38.15, 0.05), 0))
    s.badge(755, 923, 58, 40, lambda v: (-120 * (1 - E(v, 38.45, 0.45)), co(v)[1], 1, -60 * (1 - E(v, 38.45, 0.45)),
                                         E(v, 38.45, 0.05)), tri_at=38.9)
    s.thumb("Me gusta", 865, 860, 64, 41.93,
            lambda v: (0, co(v)[1] + 60 * (1 - E(v, 38.35, 0.35)), -40 * (1 - E(v, 38.35, 0.35)), E(v, 38.35, 0.05)))
    s.bell(1273, 860, 52, 62, 43.25, lambda v: (-60 * (1 - E(v, 38.9, 0.5)), co(v)[1], 30 * (1 - E(v, 38.9, 0.5)),
                                                E(v, 38.88, 0.05)))
    s.button((929, 822, 1213, 896), (847, 872), 40.68,
             lambda v: (0, co(v)[1] + 136 * (1 - E(v, 38.35, 0.45)), 1.0), radius=12, clip=cr)
    s.burst(1078, 878, 40.69, r0=44, r1=84, ln=18)
    s.burst(865, 860, 41.94, r0=40, r1=66, ln=12, cols=(INK,), wave=False)
    s.burst(1273, 860, 43.26, r0=38, r1=62, ln=12, cols=(INK,), wave=False)
    s.cursor([(39.6, 1135, 975), (39.9, 1110, 925), (40.2, 1097, 880), (40.55, 1078, 875), (40.85, 1072, 875),
              (41.3, 972, 900), (41.6, 897, 900), (41.95, 872, 880), (42.2, 897, 875), (42.6, 1147, 912),
              (42.9, 1247, 887), (43.25, 1282, 875), (43.4, 1290, 880), (43.6, 1310, 962)], 39.55, 43.55,
             clicks=(40.55, 41.88, 43.2))
    return t


# --- 8. Big row in the middle: white like, SUBSCRIBE, white bell; three cursors click them (45.65–50.4 s) ---------
def big_row():
    O, D = 45.65, 4.75
    t = _p("fila-grande", "Me gusta, suscribirse y campana grandes", "Big like, subscribe and bell", 12007, D, 3.6,
           ["clic", "me gusta", "campana", "grande"])
    s = W(t, D, O)
    lout = lambda v: (150 * ein(v, 49.75, 0.35), 1 - L(v, 49.85, 0.25))  # noqa: E731
    bout = lambda v: (150 * ein(v, 49.85, 0.35), 1 - L(v, 49.95, 0.25))  # noqa: E731
    cout = lambda v: (150 * ein(v, 50.0, 0.35), 1 - L(v, 50.1, 0.25))  # noqa: E731
    s.thumb("Me gusta", 461, 836, 148, 48.05,
            lambda v: (-25 * (1 - E(v, 45.95, 0.55)), 150 * (1 - E(v, 45.95, 0.55)) + lout(v)[0],
                       -45 * (1 - E(v, 45.95, 0.55)), E(v, 45.95, 0.2) * lout(v)[1]), base=WHITE)
    s.bell(1454, 850, 122, 150, 48.55,
           lambda v: (-135 * (1 - E(v, 45.95, 0.55)), cout(v)[0], 28 * (1 - E(v, 45.95, 0.5)),
                      E(v, 45.95, 0.2) * cout(v)[1]), base=WHITE, on=YELLOW, wave_w=9)
    bo = lambda v: (0, 150 * (1 - E(v, 45.62, 0.55)) + bout(v)[0], E(v, 45.62, 0.25) * bout(v)[1])  # noqa: E731
    s.button((745, 793, 1175, 907), (830, 868), 47.9, bo, radius=22, text_off=lambda v: 30 * (1 - E(v, 45.7, 0.5)))
    s.burst(975, 862, 47.91, r0=70, r1=120, ln=24, cols=(RED, WHITE), width=4)
    s.burst(470, 850, 48.06, r0=80, r1=120, ln=20, cols=(RED, WHITE), width=4)
    s.burst(1460, 860, 48.56, r0=85, r1=125, ln=20, cols=(RED, WHITE), width=4)
    s.cursor([(46.7, 975, 1015), (47.0, 975, 925), (47.3, 975, 870), (47.95, 975, 870), (48.35, 1050, 1006)],
             46.65, 48.28, clicks=(47.8,), name="Cursor 1")
    s.cursor([(47.0, 480, 960), (47.3, 480, 885), (48.1, 482, 880), (48.45, 510, 955), (48.9, 540, 1015)],
             46.95, 48.75, clicks=(48.0,), name="Cursor 2")
    s.cursor([(47.5, 1515, 964), (47.9, 1470, 880), (48.6, 1470, 865), (48.95, 1530, 940)], 47.45, 48.85,
             clicks=(48.5,), name="Cursor 3")
    return t


# --- 9. Three social bars with FOLLOW (50.55–54.6 s) ---------------------------------------------------------------
def socials():
    O, D = 50.55, 4.05
    t = _p("redes", "Barras de redes sociales con seguir", "Social bars with follow", 12008, D, 2.5,
           ["redes", "facebook", "instagram", "twitter", "seguir"], section="redes")
    s = W(t, D, O)
    fade = lambda v: 1 - E(v, 53.95, 0.6)  # noqa: E731
    nets = (("Facebook.com/YourName", "#1877F2", "#1877F2", "#3A3D48", "facebook"),
            ("Instagram.com/YourName", None, "#FF0091", "#512D41", "instagram"),
            ("Twitter.com/YourName", "#1DA1F2", "#1DA1F2", "#333333", "twitter"))
    for i, (link, circle, pill, ink, kind) in enumerate(nets):
        dx, a = 605 * i, 50.55 + 0.07 * i
        cx, cy = 147 + dx, 887
        x0 = 185 + dx
        s.rect(f"Barra {kind} (color)", solid(pill), lambda fr, u, dx=dx, a=a: (lambda v: (
            x0, 868, x0 + 1e-3 + (612 + dx - x0) * E(v, a + 0.17, 0.35), 937))(u + O),
            op=lambda fr, u, x0=x0: fade(u + O), radius=34.5, base=(427, 69))
        fo = lambda v, a=a: (0, -37 * (1 - E(v, a + 0.8, 0.35)), fade(v) * E(v, a + 0.75, 0.05))  # noqa: E731
        s.shp(f"Seguir {kind}", solid(pill), lambda v, fo=fo, dx=dx: (540 + dx, 951.5 + fo(v)[1], 150, 37, 0, fo(v)[2]),
              radius=18.5, base=(150, 37))
        s.txt("FOLLOW", (490 + dx, 947, 588 + dx, 961), M, 800, WHITE, f"Seguir {kind} (texto)",
              g=lambda v, fo=fo: (0, fo(v)[1], 1, 0, fo(v)[2]))
        s.rect(f"Barra {kind}", solid(WHITE), lambda fr, u, dx=dx, a=a, x0=x0: (lambda v: (
            x0, 872, x0 + 1e-3 + (600 + dx - x0) * E(v, a + 0.22, 0.38), 937))(u + O),
            op=lambda fr, u: fade(u + O), radius=32.5, base=(415, 65))
        s.txt(link, (210 + dx, 897, 590 + dx, 919), M, 700, ink, f"Enlace {kind}", align="left",
              g=lambda v, a=a: (0, 0, 1, 0, E(v, a + 0.6, 0.3) * fade(v)))

        def cg(v, a=a, cx=cx):
            q = E(v, a - 0.05, 0.3)
            d = 104 * (0.1 + 0.9 * q)
            return cx, cy + 60 * (1 - E(v, a - 0.05, 0.35)), d, d, 0, E(v, a - 0.05, 0.08) * fade(v)
        layers = solid(circle) if circle else [gradient([(0.0, "#FEC053"), (0.5, "#F2203E"), (1.0, "#B729A8")],
                                                        angle=45), no_stroke()]
        s.shp(f"Icono {kind}", layers, cg, kind="ellipse", base=(104, 104))
        up = lambda v, a=a: 40 * (1 - E(v, a + 0.25, 0.4))  # noqa: E731
        circ = lambda v, cg=cg: (lambda g: (g[0] - g[2] / 2, g[1] - g[3] / 2, g[0] + g[2] / 2, g[1] + g[3] / 2))(cg(v))  # noqa: E731
        if kind == "facebook":
            m = s.txt("f", (cx - 8, cy - 40, cx + 20, cy + 40), ROBOTO, 900, WHITE, "Icono facebook (letra)",
                      editable=False, g=lambda v, up=up: (6, 12 + up(v), 1, 0, fade(v) * E(v, a + 0.2, 0.05)))
            s.mask_to(m, circ)
        elif kind == "instagram":
            parts = [s.shp("Icono instagram (marco)", [{"id": "fill", "kind": "fill", "enabled": False,
                                                       "paint": {"kind": "solid", "color": "#00000000"}},
                                                      stroke(WHITE, 6)],
                           lambda v, up=up: (cx, cy + up(v), 52, 52, 0, fade(v) * E(v, a + 0.2, 0.05)), radius=15,
                           base=(52, 52)),
                     s.shp("Icono instagram (lente)", ring(WHITE, 6),
                           lambda v, up=up: (cx, cy + up(v), 24, 24, 0, fade(v) * E(v, a + 0.2, 0.05)), kind="ellipse",
                           base=(24, 24)),
                     s.shp("Icono instagram (punto)", solid(WHITE),
                           lambda v, up=up: (cx + 14, cy - 14 + up(v), 7, 7, 0, fade(v) * E(v, a + 0.2, 0.05)),
                           kind="ellipse")]
            for m in parts:
                s.mask_to(m, circ)
        else:
            m = s.shp("Icono twitter (pájaro)", solid(WHITE),
                      lambda v, up=up: (cx + 2, cy + 2 + up(v), 56, 46, 0, fade(v) * E(v, a + 0.2, 0.05)), path=BIRD)
            s.mask_to(m, circ)
    return t


TEMPLATES = [card_name, card_icons, bar_followers, card_small, bar_dislike, bar_bell, bar_channel, big_row, socials]
