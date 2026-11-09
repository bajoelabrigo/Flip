"""YOUTUBE PACK video 2 as Stock templates (yp2-*). See docs/plan-youtube-pack.md.

The pieces of «pack youtube 2.mp4» (960×540 at 30 fps, laid out at 1920×1080), each studied on 10 and 30 fps sheets:
the red and white ring opening with the «Youtube Pack» logo, the subscribe bars over footage, the end screens, the
channel card, the red/white transitions, the social media bars, the red and white title labels and the line icons.
Order 12300-12499. Study notes in tienda/plantillas/estudio-pack-youtube-2/NOTAS.md.

Pieces over footage have no background (they go over the person's video); full-screen pieces have their own
«Fondo». Unless a piece says otherwise it plays its entrance, holds, and leaves with its entrance backwards at 2.5×.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import wide
from scene import gradient, keys, no_stroke, tanim
from templates_tit_c import k
from templates_tit_e import solid
from templates_tit_h import EXIT, TRIANGLE, S, fill, lin, poly, ring, rot_pt, shadow

F = 30.0
WHITE, BLACK, RED, DARK = "#FFFFFF", "#000000", "#FF0000", "#2B2A33"
R, M = "Roboto", "Montserrat"
for _w, _f in ((400, "Regular"), (500, "Medium"), (700, "Bold"), (900, "Black")):
    f6._FILES[(R, _w)] = f"fonts.basic/fonts/roboto/Roboto-{_f}.ttf"
f6._FILES[("Oswald", 500)] = "fonts.basic/fonts/oswald/Oswald-Medium.ttf"
for _w, _f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium"),
               (400, "Regular")):
    f6._FILES[(M, _w)] = f"fonts.basic/fonts/montserrat/Montserrat-{_f}.ttf"


class P(S):
    """S at the reference's 30 fps. plain=True: the frame is just the clock (no backward exit)."""

    def __init__(self, t, dur, plain=False):
        super().__init__(t, dur)
        self.plain = plain

    def frame(self, u):
        if self.plain:
            return u * F
        return min(u * F, (self.dur - u) * F * EXIT)

    def anim(self, clip, at, stagger, duration, preset="fade", unit="character", order="forward", out=True, **params):
        """Letters (or words) come in from frame `at`; with out, they leave the same way backwards at EXIT×."""
        lead = round(at / F, 3)
        a = {"in": tanim(preset, duration=duration, unit=unit, stagger=stagger, ease="easeOut", delay=lead,
                         order=order, **params)}
        if out and not self.plain:
            a["out"] = tanim(preset, duration=duration / EXIT, unit=unit, stagger=stagger / EXIT, ease="easeIn",
                             delay=round(lead / EXIT, 3), order="backward" if order == "forward" else order, **params)
        clip["textStyle"]["animation"] = a
        return clip


def stroke_layers(colour, width, cap="round"):
    return [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
            {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "center", "cap": cap,
             "join": "round", "opacity": 1.0, "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}]


def circle_path(start=0.0, turns=2.0, step=4.0, ccw=True):
    n = int(360 * turns / step)
    sg = -1 if ccw else 1
    pts = [(50 + 50 * math.cos(math.radians(start + sg * step * i)), 50 + 50 * math.sin(math.radians(start + sg * step * i)))
           for i in range(n + 1)]
    return "M " + " L ".join(f"{x:.3f} {y:.3f}" for x, y in pts)


def worm(s, name, colour, geo, start=0.0, turns=2.0, ccw=True):
    """A round-capped stroke running along a circle: geo(fr) = (cx, cy, r, width, tail°, head°, opacity); tail and
    head are degrees travelled along the circle from `start` (CCW on screen when ccw)."""
    clip = s.obj(name, stroke_layers(colour, 10), lambda fr, u: (lambda g: (g[0], g[1], 2 * g[2], 2 * g[2], 0,
                                                                             g[6]))(geo(fr)),
                 path=circle_path(start, turns, ccw=ccw))
    span = 360.0 * turns
    tr0, tr1, wd = [], [], []
    for u, fr in s.each():
        g = geo(fr)
        tr0.append((u, round(100 * max(0.0, min(1.0, g[4] / span)), 3), "linear"))
        tr1.append((u, round(100 * max(0.0, min(1.0, g[5] / span)), 3), "linear"))
        wd.append((u, round(max(0.5, g[3]), 2), "linear"))
    clip["shapeStyle"]["keyframes"] = {"trimStart": keys(tr0), "trimEnd": keys(tr1), "layer.stroke.width": keys(wd)}
    return clip


def disc(s, name, colour, geo):
    """geo(fr, u) = (cx, cy, radius, opacity)."""
    return s.obj(name, solid(colour), lambda fr, u: (lambda g: (g[0], g[1], 2 * g[2], 2 * g[2], 0, g[3]))(geo(fr, u)),
                 kind="ellipse")


def yt_logo(s, name, geom, w=162, h=116, red=RED, tri=WHITE, tri_rot=None, radius=0.26):
    """A play button: geom(fr, u) = (cx, cy, scale, rot, opacity); tri_rot(fr) turns the triangle inside it."""
    box = s.obj(name, solid(red), lambda fr, u: (lambda g: (g[0], g[1], w * g[2], h * g[2], g[3], g[4]))(geom(fr, u)),
                radius=h * radius, base=(w, h))

    def tg(fr, u):
        cx, cy, sc, rot, op = geom(fr, u)
        ox, oy = rot_pt(cx + w * 0.03 * sc, cy, rot, cx, cy)
        return ox, oy, w * 0.27 * sc, h * 0.43 * sc, rot + (tri_rot(fr) if tri_rot else 0.0), op
    return box, s.obj(f"{name} (play)", solid(tri), tg, path=TRIANGLE)


def _p(id, es, en, order, dur, section, tags=(), thumb=None):
    return wide(f"yp2-{id}", es, en, "ytkit", dur, order=order,
                tags=[f"kit:{section}", "youtube", "rojo"] + list(tags),
                thumb_at=round(thumb if thumb is not None else dur * 0.55, 2))


def dur_for(entrance, hold=1.6):
    return round(entrance + hold + entrance / EXIT, 1)


# --- 1. Opening: a white and a red worm close a ring round a turning play button; the logo and the words come in --
def ring_intro(s, centre=BLACK, logo_w=162, logo_cx=651, words=(), end_shrink=True):
    """The worms (from frame 1), the ring that pushes in and opens from frame 41, the play button that turns and
    then moves left while `words` = [(text, ink, colour, weight, at)] slide in letter by letter."""
    def z(fr):  # the slow push-in of the ring before it opens
        return 1 + 0.23 * lin(fr, 24, 12) + 0.29 * lin(fr, 36, 6)

    T = lambda v: v * 6  # noqa: E731 - tile (320 px) to screen

    def white(fr):
        if fr < 1:
            return 960, 540, 1, 1, 0, 0.1, 0
        r = T(26 + 64 * k(fr, 1, 9) + 30 * k(fr, 9, 8))
        wd = T(9 + 12 * lin(fr, 1, 7) + 24 * lin(fr, 8, 8) + 15 * lin(fr, 16, 4))
        tail = 48 * lin(fr, 1, 8) + 41 * lin(fr, 9, 6) + 20 * lin(fr, 15, 4)
        head = tail + 2 + 22 * lin(fr, 1, 7) + 36 * lin(fr, 8, 1) + 102 * lin(fr, 9, 5) + 53 * lin(fr, 14, 1)             + 150 * lin(fr, 15, 3)
        if fr >= 18:  # closed: a whole ring whose outer edge runs past the corners
            inner = T(75) * z(fr)
            outer = T(135 + 50 * k(fr, 18, 12)) * z(fr)
            return 960, 540, (inner + outer) / 2, outer - inner, 0, 720, 1
        return 960, 540, r, wd, tail, head, 1
    worm(s, "Aro blanco", WHITE, white, start=86)
    disc(s, "Centro", centre, lambda fr, u: (960, 540, T(75) * z(fr), 1.0 if fr >= 18 else 0.0))

    def red(fr):
        if fr < 9:
            return 960, 540, 1, 1, 0, 0.1, 0
        zz = z(fr)
        r = T(60 + 14 * k(fr, 9, 15)) * zz
        wd = T(18 + 34 * lin(fr, 9, 15)) * zz
        head = 30 + 98 * lin(fr, 9, 3) + 192 * lin(fr, 12, 6) + 125 * lin(fr, 18, 6) + 60 * lin(fr, 24, 4)
        tail = 17 * lin(fr, 9, 2) + 12 * lin(fr, 11, 1) + 75 * lin(fr, 12, 6) + 36 * lin(fr, 18, 6) + 30 * lin(fr, 24, 4)
        if fr >= 28:
            return 960, 540, r, wd, 0, 720, 1
        return 960, 540, r, wd, tail, head, 1
    worm(s, "Aro rojo", RED, red, start=-103)
    # Then the red ring spreads over everything and the middle opens to fill the screen.
    disc(s, "Rojo (abre)", RED, lambda fr, u: (960, 540, T(155 + 160 * k(fr, 41, 4)) * (1 if fr >= 41 else 0),
                                               1.0 if fr >= 41 else 0.0))
    disc(s, "Centro (abre)", centre, lambda fr, u: (960, 540, T(48) * z(fr) + T(120) * k(fr, 42, 6),
                                                    1.0 if fr >= 41 else 0.0))

    # The button pops in at frame 14 and spins half a turn back in perspective (measured on the reference, one key
    # every few frames): size, turn in the plane, and a tilt round its vertical axis that settles by frame 38.
    size = lambda fr: ease_pts([(13, 0.0), (16, 0.3), (18, 0.67), (20, 0.75), (23, 0.83), (27, 0.9), (34, 1.0)],  # noqa: E731
                               fr)[0]
    spin = lambda fr: ease_pts([(14, -20), (15, -60), (16, -100), (17, -145), (18, -185), (20, -215), (23, -270),  # noqa: E731
                                (26, -315), (30, -345), (35, -360)], fr)[0]
    if end_shrink:
        zoom = lambda fr: 1 - 0.2 * k(fr, 69, 60) - 0.8 * k(fr, 129, 21)  # noqa: E731
    else:
        zoom = lambda fr: 1.0  # noqa: E731
    shift = 960 - logo_cx
    lx = lambda fr: 960 - shift * k(fr, 41, 19)  # noqa: E731

    def logo(fr, u):
        sc = size(fr) * zoom(fr)
        x = 960 + (lx(fr) - 960) * zoom(fr)
        return x, 540, max(1e-3, sc), spin(fr), 1.0 if fr >= 14 else 0.0
    # Once still, the triangle alone spins three turns back (fast at first) from frame 40.
    tri = lambda fr: -1080 * (1 - (1 - lin(fr, 40, 30)) ** 3)  # noqa: E731
    box, _ = yt_logo(s, "Logo", logo, w=logo_w, h=logo_w * 0.716, tri_rot=tri)
    # Only the red box turns in 3D. With both box and triangle as 3D layers the box hides the triangle on frames 17-21
    # whatever its depth (positionZ -2, +2, +4, +20; engine builds 0109 and 0109b), so the triangle stays flat: it is
    # small and flat on the box and reads the same.
    s.d3(box, ry=lambda fr, u: 35 * (1 - k(fr, 14, 24)), rx=lambda fr, u: -12 * (1 - k(fr, 14, 24)), persp=500)

    def place(ink):
        def g(fr, u):
            dx, dy = s.about(ink, 960, 540, zoom(fr))
            return dx + (lx(fr) - logo_cx) * zoom(fr), dy, zoom(fr), 0, 1
        return g
    for i, (text, ink, colour, weight, at) in enumerate(words):
        c = s.say(text, ink, R, weight, colour, "Título" if i == 0 else "Texto", align="left", geom=place(ink))
        s.anim(c, at, 0.045, 0.18, "slide-left", distance=0.6)


def opening():
    D = 5.0
    t = _p("apertura", "Apertura: aro rojo y blanco con botón de YouTube", "Opening: red and white ring with a YouTube "
           "button", 12300, D, "aperturas", ["apertura", "logo", "aro"], thumb=2.4)
    s = P(t, D, plain=True)
    s.rect("Fondo", solid(BLACK), lambda fr, u: (-10, -10, 1930, 1090))
    ring_intro(s, BLACK, 162, 651, (("Youtube", (753, 519, 1117, 587), WHITE, 700, 41),
                                    ("Pack", (1147, 519, 1363, 587), RED, 700, 50)))
    return t


# --- UI glyphs (paths in a 100 box) ------------------------------------------------------------------------------
def _flip_y(pts):
    return [(x, 100 - y) for x, y in pts]


def arc(a0, a1, steps=16):
    pts = [(50 + 50 * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
            50 + 50 * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts)


_HAND = [(30, 40), (44, 22), (50, 2), (60, 0), (66, 10), (64, 30), (60, 38), (94, 38), (100, 46), (98, 56), (94, 60),
         (96, 70), (90, 76), (90, 86), (84, 92), (80, 100), (30, 100)]
_CUFF = [(0, 40), (22, 40), (22, 100), (0, 100)]
GLYPH = {
    "like": poly(_CUFF) + " " + poly(_HAND),
    "dislike": poly(_flip_y(_CUFF)) + " " + poly(_flip_y(_HAND)),
    "bell": poly([(44, 6), (56, 6), (58, 13), (72, 20), (80, 38), (81, 60), (94, 76), (94, 84), (6, 84), (6, 76),
                  (19, 60), (20, 38), (28, 20), (42, 13)]) + " " + poly([(38, 88), (62, 88), (58, 98), (42, 98)]),
    "cursor": poly([(0, 0), (0, 78), (20, 62), (34, 94), (47, 88), (33, 58), (58, 58)]),
    "pause": poly([(10, 0), (38, 0), (38, 100), (10, 100)]) + " " + poly([(62, 0), (90, 0), (90, 100), (62, 100)]),
    "next": poly([(0, 0), (70, 50), (0, 100)]) + " " + poly([(78, 0), (100, 0), (100, 100), (78, 100)]),
    "volume": poly([(0, 32), (24, 32), (56, 0), (56, 100), (24, 68), (0, 68)]) + " "
    + poly([(66, 30), (74, 24), (84, 50), (74, 76), (66, 70), (72, 50)]),
    "gear": poly([(50 + (50 if i % 2 == 0 else 36) * math.cos(math.radians(i * 22.5)),
                   50 + (50 if i % 2 == 0 else 36) * math.sin(math.radians(i * 22.5))) for i in range(16)]),
    "full": " ".join(poly(p) for p in ([(0, 0), (36, 0), (36, 12), (12, 12), (12, 36), (0, 36)],
                                         [(100, 0), (64, 0), (64, 12), (88, 12), (88, 36), (100, 36)],
                                         [(0, 100), (36, 100), (36, 88), (12, 88), (12, 64), (0, 64)],
                                         [(100, 100), (64, 100), (64, 88), (88, 88), (88, 64), (100, 64)])),
}
GREY, INK, LIGHT = "#999999", "#222222", "#E3E3E3"


def ease_pts(pts, u):
    """Value at time u along [(t, a, b, ...)] keys, smooth between keys."""
    if u <= pts[0][0]:
        return pts[0][1:]
    for (t0, *a), (t1, *b) in zip(pts, pts[1:]):
        if u <= t1:
            q = (u - t0) / max(1e-6, t1 - t0)
            q = q * q * (3 - 2 * q)
            return tuple(x + (y - x) * q for x, y in zip(a, b))
    return pts[-1][1:]


class UI:
    """Shapes and words of a small interface that moves as one: off(fr, u) = (dx, dy, scale, px, py) — scaled by
    scale about (px, py) and moved by (dx, dy) (screen px)."""

    def __init__(self, s, off, appear=None):
        self.s, self.off, self.appear = s, off, appear

    def _op(self, op, x):
        """op times the fade-in of whatever sits at x (appear(x) = frame it shows from)."""
        if not self.appear:
            return op
        at = self.appear(x)
        return lambda fr, u: (op(fr, u) if op else 1.0) * k(fr, at, 4)

    def at(self, fr, u, x, y):
        dx, dy, sc, px, py = self.off(fr, u)
        return px + (x - px) * sc + dx, py + (y - py) * sc + dy, sc

    def box(self, name, layers, r, op=None, kind="rectangle", path=None, radius=0.0, grow=None):
        """r = (x0, y0, x1, y1) at rest; grow(fr, u) = (fx, fy, anchor_x 0..1) scales it about that point."""
        x0, y0, x1, y1 = r
        op = self._op(op, x0) if name != "Tarjeta" else op

        def g(fr, u):
            fx, fy, ax = grow(fr, u) if grow else (1.0, 1.0, 0.5)
            w, h = (x1 - x0) * fx, (y1 - y0) * fy
            cx = x0 + (x1 - x0) * ax + (0.5 - ax) * w
            X, Y, sc = self.at(fr, u, cx, (y0 + y1) / 2)
            return X, Y, w * sc, h * sc, 0, op(fr, u) if op else 1.0
        return self.s.obj(name, layers, g, kind=kind, path=path, radius=radius, base=(x1 - x0, y1 - y0))

    def glyph(self, name, kind, r, colour, op=None):
        return self.box(name, solid(colour), r, op=op, path=GLYPH[kind])

    def word(self, text, ink, family, weight, colour, name, op=None, align="left"):
        op = self._op(op, ink[0])

        def g(fr, u):
            cx, cy = (ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2
            X, Y, sc = self.at(fr, u, cx, cy)
            return X - cx, Y - cy, sc, 0, op(fr, u) if op else 1.0
        return self.s.say(text, ink, family, weight, colour, name, align=align, geom=g)


def cursor(s, keys_, clicks=(), show=(0.0, 99.0), name="Cursor", size=44):
    """An arrow pointer: keys_ = [(t, x, y)] (seconds; x, y = its tip); it dips at each click time."""
    w = size * 0.6

    def g(fr, u):
        x, y = ease_pts(keys_, u)
        sc = 0.82 if any(c - 0.05 <= u <= c + 0.12 for c in clicks) else 1.0
        op = 1.0 if show[0] <= u <= show[1] else 0.0
        return x + w * sc / 2, y + size * sc / 2, w * sc, size * sc, 0, op
    s.obj(name, [fill(WHITE), {"id": "stroke", "kind": "stroke", "enabled": True, "width": 2.5, "strokeAlign": "center",
                               "join": "round", "opacity": 1.0, "paint": {"kind": "solid", "color": "#ff111111"}}],
          g, path=GLYPH["cursor"], base=(w, size))


def card_layers(colour=WHITE, alpha=0.22):
    return [shadow("#000000", 0, 6, 18, alpha), fill(colour)]


def rise(at=0, n=12, by=330):
    """off() for a card that rises from below the frame (and leaves the same way)."""
    return lambda fr, u: (0.0, by * (1 - k(fr, at, n)), 1.0, 960.0, 540.0)


def ring_bell(ui, r, at, colour="#333333", op=None, name="Campana"):
    """A bell; from `at` (seconds) a ring mark on each side."""
    ui.glyph(name, "bell", r, colour, op=op)
    x0, y0, x1, y1 = r
    w = x1 - x0
    for i, cx in enumerate((x0 - w * 0.12, x1 + w * 0.12)):
        def opf(fr, u, op=op):
            return (op(fr, u) if op else 1.0) * (1.0 if at is not None and u >= at else 0.0)
        ui.box(f"{name} (sonido {i + 1})", ring(colour, max(2.0, w * 0.08)),
               (cx - w * 0.16, y0 + w * 0.05, cx + w * 0.16, y0 + w * 0.7), op=opf,
               path=arc(120, 240) if i == 0 else arc(-60, 60))


def subscribe_button(ui, r, label, ink, done_label, done_ink, t_click, grow_at=16, bell=None, bell_at=None,
                     done_colour=LIGHT, red=RED):
    """The red button grows from its left edge and its words appear; clicked at t_click it turns grey with
    «SUBSCRIBED» (and a bell beside the words, ringing after bell_at)."""
    on = lambda fr, u: 1.0 if u < t_click else 0.0  # noqa: E731
    off = lambda fr, u: 1.0 - on(fr, u)  # noqa: E731
    press = lambda fr, u: 0.94 if t_click - 0.04 <= u <= t_click + 0.1 else 1.0  # noqa: E731
    ui.box("Botón", solid(red), r, op=on, grow=lambda fr, u: (k(fr, grow_at, 6) * press(fr, u), press(fr, u), 0.0))
    ui.word(label, ink, R, 500, WHITE, "Botón (texto)", op=lambda fr, u: on(fr, u) * k(fr, grow_at + 5, 3))
    ui.box("Botón (suscrito)", solid(done_colour), r, op=off)
    ui.word(done_label, done_ink, R, 500, "#444444", "Botón (suscrito, texto)", op=off)
    if bell:
        ring_bell(ui, bell, bell_at, op=off)


def avatar(s, ui, sample, cx, cy, rr, name="Foto del canal"):
    t = s.t
    clip = t.photo(t.track("video", name), sample, 0.0, s.dur, None, None, label=name)
    track = next(tr for tr in t.tracks if clip in tr.clips)
    xs, ys, ws, hs = [], [], [], []
    for u, fr in s.each():
        X, Y, sc = ui.at(fr, u, cx, cy)
        xs.append((u, X - rr * sc, "linear"))
        ys.append((u, Y - rr * sc, "linear"))
        ws.append((u, 2 * rr * sc, "linear"))
        hs.append((u, 2 * rr * sc, "linear"))
    clip["x"], clip["y"], clip["width"], clip["height"] = keys(xs), keys(ys), keys(ws), keys(hs)
    t.mask(track, clip, "ellipse")
    return clip


def parts_of(s, ui, parts, t_click, bell_at):
    for part in parts:
        kind = part[0]
        if kind == "glyph":
            _, g, r, colour = part[:4]
            after = part[4] if len(part) > 4 else None
            name = {"like": "Me gusta", "dislike": "No me gusta"}.get(g, g)
            if after:
                ui.glyph(name, g, r, colour, op=lambda fr, u: 1.0 if u < t_click + 0.7 else 0.0)
                ui.glyph(f"{name} (activo)", g, r, after, op=lambda fr, u: 1.0 if u >= t_click + 0.7 else 0.0)
            else:
                ui.glyph(name, g, r, colour)
        elif kind == "word":
            _, text, ink, colour, weight = part
            ui.word(text, ink, R, weight, colour, "Texto" if text[0].isdigit() else "Canal")
        elif kind == "avatar":
            avatar(s, ui, part[4], part[1], part[2], part[3])
        elif kind == "button":
            _, r, label, ink, done, dink = part[:6]
            subscribe_button(ui, r, label, ink, done, dink, t_click, bell=part[6] if len(part) > 6 else None,
                             bell_at=bell_at)
        elif kind == "bell":
            ring_bell(ui, part[1], bell_at, colour=GREY)


def bar_piece(id, es, en, order, card, parts, t_click, D, cur, bell_at=None):
    """A white card with like / dislike / counts / subscribe that rises from below the frame; a pointer clicks."""
    t = _p(id, es, en, order, D, "elementos", ["suscribirse", "barra"], thumb=t_click + 0.5)
    s = P(t, D)
    ui = UI(s, rise(n=20), appear=lambda x: 6 + 12 * (x - card[0]) / (card[2] - card[0]))
    ui.box("Tarjeta", card_layers(), card, radius=10)
    parts_of(s, ui, parts, t_click, bell_at)
    cursor(s, cur, clicks=[t_click] + ([bell_at] if bell_at else []), show=(cur[0][0], D - 0.4))
    return t


# --- 2-5. Grid 1 (14.8-20.5 s) ------------------------------------------------------------------------------------
def bar_counts():
    """Bottom left: a white bar with likes, dislikes and SUBSCRIBE 1.7M; then the bell inside it rings."""
    return bar_piece("barra-contadores", "Barra: me gusta, contadores y suscribirse", "Bar: likes, counts and subscribe",
                     12310, (565, 745, 1355, 911),
                     [("glyph", "like", (608, 800, 676, 860), INK), ("word", "25K", (700, 815, 788, 848), GREY, 500),
                      ("glyph", "dislike", (836, 800, 902, 860), GREY), ("word", "17", (930, 815, 978, 848), GREY, 500),
                      ("button", (1043, 803, 1307, 872), "SUBSCRIBE  1.7M", (1068, 828, 1282, 850),
                       "SUBSCRIBED", (1066, 822, 1222, 848), (1240, 812, 1282, 860))],
                     2.3, 5.2, [(1.7, 1400, 960), (2.1, 1180, 850), (2.4, 1180, 850), (3.0, 1262, 846), (3.6, 1330, 900)],
                     bell_at=3.3)


# --- 6-9. Grid 2 (20.5-26.8 s): four bars --------------------------------------------------------------------------
def bar_likes():
    return bar_piece("barra-15k", "Barra: me gusta y suscribirse", "Bar: likes and subscribe", 12320,
                     (686, 746, 1234, 912),
                     [("glyph", "like", (722, 800, 790, 860), GREY, INK), ("word", "15K", (815, 813, 898, 850), GREY, 500),
                      ("button", (932, 797, 1196, 862), "SUBSCRIBE  1.7M", (958, 818, 1172, 842),
                       "SUBSCRIBED", (952, 816, 1120, 842), (1136, 806, 1178, 854))],
                     2.3, 5.0, [(1.4, 760, 860), (2.0, 1060, 850), (2.4, 1062, 846), (3.0, 1160, 840), (3.6, 1180, 900)],
                     bell_at=3.3)


def bar_channel():
    return bar_piece("barra-canal", "Barra del canal con foto y suscribirse", "Channel bar with photo and subscribe",
                     12321, (400, 746, 1518, 910),
                     [("avatar", 512, 830, 50, "portrait-02"),
                      ("word", "Channel Name", (586, 792, 840, 818), INK, 700),
                      ("word", "26156 views", (580, 838, 806, 866), GREY, 500),
                      ("glyph", "like", (1000, 812, 1066, 860), GREY, INK),
                      ("glyph", "dislike", (1103, 812, 1170, 860), GREY),
                      ("button", (1210, 803, 1472, 870), "SUBSCRIBE", (1248, 826, 1434, 852),
                       "SUBSCRIBED", (1240, 826, 1442, 852))],
                     2.3, 4.6, [(1.4, 1080, 930), (2.0, 1340, 860), (2.5, 1342, 850), (3.0, 1040, 850), (3.6, 1100, 940)])


def bar_simple():
    return bar_piece("barra-simple", "Barra: me gusta, no me gusta y suscribirse", "Bar: like, dislike and subscribe",
                     12322, (686, 746, 1234, 912),
                     [("glyph", "like", (722, 800, 790, 860), GREY, INK),
                      ("glyph", "dislike", (825, 800, 892, 860), GREY),
                      ("button", (932, 797, 1196, 862), "SUBSCRIBE", (970, 818, 1158, 844),
                       "SUBSCRIBED", (962, 818, 1166, 844))],
                     2.3, 4.6, [(1.4, 760, 860), (2.0, 1060, 850), (2.5, 1062, 846), (3.0, 1000, 900)])


def bar_bell():
    return bar_piece("barra-campana", "Barra: me gusta, suscribirse y campana", "Bar: like, subscribe and bell", 12323,
                     (686, 746, 1234, 912),
                     [("glyph", "like", (722, 800, 790, 860), GREY, INK),
                      ("button", (828, 797, 1092, 862), "SUBSCRIBE", (866, 818, 1053, 844),
                       "SUBSCRIBED", (858, 818, 1062, 844)),
                      ("bell", (1137, 800, 1188, 860))],
                     2.3, 5.0, [(1.4, 760, 860), (2.0, 960, 850), (2.5, 962, 846), (3.1, 1165, 840), (3.7, 1200, 900)],
                     bell_at=3.3)


def two_cards():
    """Grid 1 top right: two white cards rise (SUBSCRIBE / like and dislike); a pointer subscribes, then likes."""
    D = 3.8
    t = _p("dos-tarjetas", "Tarjetas: suscribirse y me gusta", "Cards: subscribe and like", 12311, D, "elementos",
           ["suscribirse", "me gusta"], thumb=2.4)
    s = P(t, D)
    a = UI(s, rise(0, 15, 380))
    b = UI(s, rise(2, 15, 380))
    t_sub, t_like = 1.5, 2.0
    a.box("Tarjeta", card_layers(), (538, 762, 906, 902), radius=10)
    on = lambda fr, u: 1.0 if u < t_sub else 0.0  # noqa: E731
    a.box("Botón", solid(RED), (590, 803, 855, 871), op=on,
          grow=lambda fr, u: (1.0, k(fr, 6, 6) * (0.92 if t_sub - 0.04 <= u <= t_sub + 0.1 else 1.0), 0.5))
    a.word("SUBSCRIBE", (628, 829, 815, 855), R, 500, WHITE, "Botón (texto)", op=lambda fr, u: on(fr, u) * k(fr, 12, 3))
    a.box("Botón (suscrito)", solid(LIGHT), (592, 797, 853, 865), op=lambda fr, u: 1 - on(fr, u))
    a.word("SUBSCRIBED", (618, 817, 825, 843), R, 500, "#444444", "Botón (suscrito, texto)",
           op=lambda fr, u: 1 - on(fr, u))
    b.box("Tarjeta 2", card_layers(), (1120, 765, 1395, 932), radius=10)
    b.glyph("Me gusta", "like", (1170, 812, 1240, 867), GREY, op=lambda fr, u: 1.0 if u < t_like else 0.0)
    b.glyph("Me gusta (activo)", "like", (1170, 812, 1240, 867), INK, op=lambda fr, u: 1.0 if u >= t_like else 0.0)
    b.glyph("No me gusta", "dislike", (1275, 812, 1342, 867), GREY)
    cursor(s, [(1.0, 1230, 990), (1.4, 720, 845), (1.6, 722, 842), (1.9, 1205, 845), (2.1, 1206, 843),
               (2.8, 1250, 960)], clicks=(t_sub, t_like), show=(1.0, D - 0.3))
    return t


def video_slot(s, rect, sample, name="Tu video"):
    """A photo slot (the person's video) that covers rect(fr, u) = (x0, y0, x1, y1) every frame."""
    t = s.t
    clip = t.photo(t.track("video", name), sample, 0.0, s.dur, None, None, label=name)
    xs, ys, ws, hs = [], [], [], []
    for u, fr in s.each():
        x0, y0, x1, y1 = rect(fr, u)
        xs.append((u, x0, "linear"))
        ys.append((u, y0, "linear"))
        ws.append((u, x1 - x0, "linear"))
        hs.append((u, y1 - y0, "linear"))
    clip["x"], clip["y"], clip["width"], clip["height"] = keys(xs), keys(ys), keys(ws), keys(hs)
    return clip


def lerp_rect(a, b, q):
    return tuple(x + (y - x) * q for x, y in zip(a, b))


def player(s, rest, now, controls):
    """The video slot shrinking from the whole frame to `rest`, with its controls riding on it."""
    def rect(fr, u):
        return now(fr, u)
    video_slot(s, rect, controls["sample"])

    def off(fr, u):
        x0, y0, x1, y1 = now(fr, u)
        sc = (x1 - x0) / (rest[2] - rest[0])
        return x0 - rest[0], y0 - rest[1], sc, rest[0], rest[1]
    v = UI(s, off)
    op = lambda fr, u: k(fr, 0, 6)  # noqa: E731
    bar = controls["bar"]
    v.box("Progreso", solid("#FFFFFF", 0.45), bar, op=op)
    v.box("Progreso (rojo)", solid(RED), (bar[0], bar[1], controls["red_to"], bar[3]), op=op)
    for g, r in controls["icons"]:
        v.glyph({"pause": "Pausa", "next": "Siguiente", "volume": "Volumen", "gear": "Ajustes",
                 "full": "Pantalla completa"}[g], g, r, WHITE, op=op)
    return v


def watch_page():
    """Grid 1 top left: the video shrinks into a watch page — the list of videos at the side, the channel row under
    it; the pointer subscribes and turns on the bell; the page keeps drawing back slowly."""
    D = 4.4
    t = _p("pagina-video", "Página de video: suscribirse y campana", "Watch page: subscribe and bell", 12310 - 1, D,
           "elementos", ["suscribirse", "página"], thumb=2.2)
    s = P(t, D)
    s.rect("Fondo", solid(WHITE), lambda fr, u: (-10, -10, 1930, 1090))
    rest = (67, 48, 1523, 866)
    zoom = lambda u: 1 - 0.05 * min(1.0, u / D)  # noqa: E731

    def scaled(r, u):
        z = zoom(u)
        return tuple((v - 40) * z + 40 for v in r)

    def now(fr, u):
        return scaled(lerp_rect((0, 0, 1920, 1080), rest, k(fr, 0, 18)), u)
    side = UI(s, lambda fr, u: (420 * (1 - k(fr, 3, 15)) * zoom(u), 0, zoom(u), 40, 40))
    row = UI(s, lambda fr, u: (0, 260 * (1 - k(fr, 3, 15)) * zoom(u), zoom(u), 40, 40))
    for i in range(6):
        y0 = 48 + 194.5 * i
        side.box(f"Video {i + 1}", solid("#A3A3A3"), (1567, y0, 1875, y0 + 172))
        for j, (yy, w) in enumerate(((14, 80), (44, 60), (74, 40))):
            side.box(f"Video {i + 1} (línea {j + 1})", solid("#A3A3A3"), (1895, y0 + yy, 1895 + w, y0 + yy + 14))
    player(s, rest, now, {"sample": "fx-walk-01", "bar": (90, 803, 1500, 808), "red_to": 190,
                          "icons": [("pause", (115, 825, 140, 852)), ("next", (180, 826, 205, 852)),
                                    ("volume", (232, 824, 262, 854)), ("gear", (1405, 822, 1437, 854)),
                                    ("full", (1455, 822, 1487, 854))]})
    t_sub, t_bell = 1.6, 2.8
    avatar(s, row, "portrait-03", 120, 965, 52)
    row.word("Channel Name", (190, 925, 385, 950), R, 500, "#333333", "Canal")
    row.word("Thank you so much for watching.", (192, 973, 728, 1003), R, 400, "#333333", "Texto")
    row.glyph("Me gusta", "like", (960, 975, 1000, 1012), INK)
    row.word("105K", (1010, 980, 1085, 1007), R, 400, GREY, "Texto 2")
    row.glyph("No me gusta", "dislike", (1145, 975, 1185, 1012), GREY)
    subscribe_button(row, (1223, 948, 1462, 1012), "SUBSCRIBE  1.7M", (1248, 971, 1440, 991), "SUBSCRIBED  1.7M",
                     (1240, 971, 1446, 991), t_sub, grow_at=12)
    ring_bell(row, (1488, 958, 1522, 1003), t_bell, colour=INK)
    row.box("Línea", solid("#DDDDDD"), (67, 1050, 1523, 1053))
    cursor(s, [(1.1, 1340, 1070), (1.5, 1330, 992), (1.7, 1332, 990), (2.6, 1505, 996), (2.9, 1506, 994),
               (3.5, 1560, 1060)], clicks=(t_sub, t_bell), show=(1.1, D - 0.3))
    return t


def card_page():
    """Grid 1 bottom right: the video shrinks into a white card on a light page — channel name, views, likes and
    SUBSCRIBE 1.7M; the pointer subscribes and turns on the bell."""
    D = 4.4
    t = _p("tarjeta-video", "Tarjeta de video: suscribirse y campana", "Video card: subscribe and bell", 12312, D,
           "elementos", ["suscribirse", "tarjeta"], thumb=2.2)
    s = P(t, D)
    s.rect("Fondo", solid("#F7F7F7"), lambda fr, u: (-10, -10, 1930, 1090))
    rest = (316, 104, 1603, 826)
    zoom = lambda u: 1 - 0.03 * min(1.0, u / D)  # noqa: E731

    def now(fr, u):
        z = zoom(u)
        return tuple((v - c) * z + c for v, c in zip(lerp_rect((0, 0, 1920, 1080), rest, k(fr, 0, 24)),
                                                      (960, 540, 960, 540)))

    def off(fr, u):
        x0, y0, x1, y1 = now(fr, u)
        sc = (x1 - x0) / (rest[2] - rest[0])
        return x0 - rest[0], y0 - rest[1], sc, rest[0], rest[1]
    ui = UI(s, off)
    ui.box("Tarjeta", card_layers(alpha=0.18), (316, 104, 1603, 975), radius=8)
    player(s, rest, now, {"sample": "fx-woman-02", "bar": (337, 770, 1582, 775), "red_to": 480,
                          "icons": [("pause", (360, 790, 380, 815)), ("next", (415, 790, 437, 815)),
                                    ("volume", (462, 788, 490, 817)), ("gear", (1492, 788, 1520, 817)),
                                    ("full", (1543, 788, 1571, 817))]})
    t_sub, t_bell = 1.7, 2.8
    ui.box("Foto del canal", solid("#808080"), (334, 859, 420, 945), kind="ellipse")
    ui.word("Channel Name", (437, 866, 655, 892), R, 500, "#333333", "Canal")
    ui.word("26156 views", (437, 914, 625, 942), R, 400, GREY, "Texto")
    ui.glyph("Me gusta", "like", (1098, 884, 1143, 922), INK)
    ui.word("125K", (1150, 888, 1230, 916), R, 400, GREY, "Texto 2")
    ui.glyph("No me gusta", "dislike", (1265, 884, 1310, 922), GREY)
    ui.word("15", (1322, 889, 1360, 915), R, 400, GREY, "Texto 3")
    subscribe_button(ui, (1393, 880, 1567, 924), "SUBSCRIBE  1.7M", (1408, 895, 1552, 910), "SUBSCRIBED",
                     (1410, 895, 1516, 910), t_sub, grow_at=18, bell=(1528, 888, 1552, 916), bell_at=t_bell)
    cursor(s, [(1.2, 1500, 1010), (1.6, 1470, 905), (1.8, 1472, 903), (2.6, 1541, 905), (2.9, 1542, 903),
               (3.5, 1600, 980)], clicks=(t_sub, t_bell), show=(1.2, D - 0.3), size=36)
    return t


def circle3(a, b, c):
    """Centre and radius of the circle through three points."""
    (ax, ay), (bx, by), (cx, cy) = a, b, c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    return ux, uy, math.hypot(ax - ux, ay - uy)


DESC = ("Motion Design, titles animation,", "shape animation and other...")


# --- 10-13. Grid 3 (26.8-29.9 s) ---------------------------------------------------------------------------------
def next_wave():
    """Top left: a navy panel with a round edge, a red and a white crescent behind it, sweeps in from the left and
    darkens the video; the next video's picture, NEXT VIDEO rising from a line, two lines of text, a red line and a
    typed «# trend»."""
    D = dur_for(1.9, 1.6)
    t = _p("siguiente-onda", "Pantalla final: siguiente video con onda roja", "End screen: next video with a red wave",
           12330, D, "pantallas-finales", ["pantalla final", "siguiente video"], thumb=2.4)
    s = P(t, D)
    s.rect("Oscurecer", solid(BLACK, 0.55), lambda fr, u: (-10, -10, 1930, 1090), op=lambda fr, u: k(fr, 0, 12))
    for name, colour, pts, at, n in (("Onda blanca", WHITE, ((1060, 0), (1100, 450), (1000, 680)), 1, 22),
                                     ("Onda roja", RED, ((790, 0), (1000, 540), (880, 1080)), 0, 20),
                                     ("Panel", "#0E0F1C", ((770, 0), (835, 430), (580, 1080)), 0, 18)):
        cx, cy, rr = circle3(*pts)
        disc(s, name, colour, lambda fr, u, cx=cx, cy=cy, rr=rr, at=at, n=n: (cx - 1500 * (1 - k(fr, at, n)), cy, rr, 1))
    video_slot(s, lambda fr, u: (97 - 900 * (1 - k(fr, 12, 12)), 185, 732 - 900 * (1 - k(fr, 12, 12)), 543),
               "fx-man-02", "Siguiente video")
    s.say("NEXT VIDEO", (95, 578, 728, 645), M, 800, WHITE, reveal=lambda fr: (0, 560, 1920, 652),
          shift=lambda fr: (0, 80 * (1 - k(fr, 27, 9))), op=lambda fr, u: k(fr, 27, 2), align="left")
    for i, (line, ink) in enumerate(zip(DESC, ((95, 672, 540, 695), (95, 705, 492, 728)))):
        s.say(line, ink, M, 600, WHITE, f"Texto {i + 1}" if i else "Texto", align="left",
              geom=lambda fr, u, i=i: (0, 0, 1, 0, k(fr, 39 + 3 * i, 6)))
    s.rect("Línea", solid(RED), lambda fr, u: (95, 752, 95 + 370 * k(fr, 45, 8), 760))
    c = s.say("# trend", (100, 1000, 260, 1032), M, 700, WHITE, "Etiqueta", align="left")
    s.anim(c, 51, 0.09, 0.05, "typewriter", order="random")
    return t


def channel_card():
    """Top right: a red disc opens over the video with a white hole that fills the screen; a play button spins in,
    then shrinks into a small logo beside «YouTube» as the channel photo pops in a red ring; red quarter circles grow
    from two corners."""
    D = dur_for(1.9, 1.6)
    t = _p("tarjeta-canal", "Tarjeta del canal con foto y logo", "Channel card with photo and logo", 12331, D,
           "pantallas-finales", ["canal", "logo", "foto"], thumb=2.6)
    s = P(t, D)
    disc(s, "Rojo", RED, lambda fr, u: (960, 540, 1300 * k(fr, 0, 9), 1))
    hole = [(0, 0), (3, 78), (6, 276), (9, 480), (12, 640), (15, 770), (18, 870), (21, 930), (27, 1120)]
    disc(s, "Fondo", WHITE, lambda fr, u: (960, 540, ease_pts(hole, fr)[0] if fr > 0 else 0, 1 if fr >= 2 else 0))
    for name, (cx, cy, rr), at in (("Esquina", (-330, 1540, 1160), 42), ("Esquina 2", (2370, -150, 824), 45)):
        disc(s, name, RED, lambda fr, u, cx=cx, cy=cy, rr=rr, at=at: (cx, cy, rr * k(fr, at, 12), 1))

    def logo(fr, u):
        big = ease_pts([(8, 30), (9, 84), (12, 100), (15, 180), (21, 210), (24, 216)], fr)[0]
        if fr < 36:
            rot = 30 * math.cos(math.pi * fr / 3) * (1 - k(fr, 9, 15))
            return 960, 540, big / 94, rot, 1.0 if fr >= 9 else 0.0
        q = k(fr, 36, 9)
        return 960 + (855 - 960) * q, 540, (216 + (94 - 216) * q) / 94, -25 * math.sin(math.pi * q), 1
    yt_logo(s, "Logo", logo, w=94, h=67)
    c = s.say("YouTube", (915, 510, 1112, 568), "Oswald", 500, "#222222", "Texto", align="left")
    s.anim(c, 42, 0.06, 0.08, "fade", order="backward")
    s.say("Channel Name", (780, 595, 1140, 635), R, 700, "#222222", "Título",
          geom=lambda fr, u: (0, 20 * (1 - k(fr, 42, 6)), 1, 0, k(fr, 42, 6)))
    rr = lambda fr: 152 * k(fr, 39, 12)  # noqa: E731
    disc(s, "Aro", RED, lambda fr, u: (960, 318, rr(fr), 1 if fr >= 39 else 0))
    ph = video_slot(s, lambda fr, u: (960 - (rr(fr) - 8), 318 - (rr(fr) - 8), 960 + max(1, rr(fr) - 8),
                                      318 + max(1, rr(fr) - 8)), "portrait-04", "Foto del canal")
    ph["opacity"] = keys([(u, round(k(fr, 44, 4), 3), "linear") for u, fr in s.each()])
    track = next(tr for tr in t.tracks if ph in tr.clips)
    t.mask(track, ph, "ellipse")
    return t


def ring_channel():
    """Bottom left: the white and red worms close a ring over the video, the middle is white; the ring opens and
    leaves the play button and CHANNEL."""
    D = 3.8
    t = _p("aro-canal", "Aro rojo y blanco que abre CHANNEL", "Red and white ring opening to CHANNEL", 12332, D,
           "aperturas", ["aro", "logo", "canal"], thumb=2.4)
    s = P(t, D)
    ring_intro(s, WHITE, 217, 716, (("CHANNEL", (849, 502, 1301, 573), "#222222", 500, 44),), end_shrink=False)
    return t


def next_bar():
    """Bottom right: a dark slanted band fades in over the video; the next video's picture slides in; a red bar sweeps
    left uncovering NEXT VIDEO; two lines and «# trend» are typed."""
    D = dur_for(1.6, 1.8)
    t = _p("siguiente-barra", "Pantalla final: siguiente video con barra roja", "End screen: next video with a red bar",
           12333, D, "pantallas-finales", ["pantalla final", "siguiente video"], thumb=2.4)
    s = P(t, D)
    s.rect("Sombra", solid("#05060F", 0.85),
           lambda fr, u: (-10, -10, 740, 1090), op=lambda fr, u: k(fr, 3, 9), path=poly([(0, 0), (100, 0), (52, 100), (0, 100)]))
    video_slot(s, lambda fr, u: (97 - 800 * (1 - k(fr, 12, 12)), 152, 635 - 800 * (1 - k(fr, 12, 12)), 455),
               "fx-man-02", "Siguiente video")
    bar = lambda fr: 600 - 502 * k(fr, 21, 15)  # noqa: E731
    s.say("NEXT", (128, 500, 323, 548), M, 800, WHITE, align="left", reveal=lambda fr: (bar(fr) + 6, 0, 1920, 1080))
    s.say("VIDEO", (348, 500, 588, 548), M, 800, RED, "Título 2", align="left",
          reveal=lambda fr: (bar(fr) + 6, 0, 1920, 1080))
    s.rect("Barra", solid(RED), lambda fr, u: (bar(fr), 497, bar(fr) + 12, 551), op=lambda fr, u: k(fr, 21, 2))
    for i, (line, ink) in enumerate(zip(("Motion Design, titles animation,", "shape animation and other ....."),
                                        ((98, 585, 550, 610), (98, 620, 535, 645)))):
        s.say(line, ink, M, 600, WHITE, f"Texto {i + 1}" if i else "Texto", align="left",
              geom=lambda fr, u, i=i: (0, 0, 1, 0, k(fr, 36 + 3 * i, 4)))
    c = s.say("# trend", (100, 1010, 240, 1040), M, 700, WHITE, "Etiqueta", align="left")
    s.anim(c, 39, 0.09, 0.05, "typewriter", order="random")
    return t


def band(s, name, colour, p_of, w_of, along, angle=45.0, length=3400.0, round_=True):
    """A long bar at `angle`° (its length runs that way): p_of(fr) = its centre's distance from the frame's centre,
    across the bar (screen px, + toward the top right for 45°); w_of(fr) its thickness; along(fr) how far it is slid
    along its length (0 = centred)."""
    a = math.radians(angle)
    d = (math.cos(a), math.sin(a))
    n = (math.sin(a), -math.cos(a))
    W = max(w_of(fr) for _, fr in s.each())

    def g(fr, u):
        p, sl, w = p_of(fr), along(fr), w_of(fr)
        return 960 + p * n[0] + sl * d[0], 540 + p * n[1] + sl * d[1], length, max(0.5, w), angle, 1.0 if w > 0.5 else 0
    return s.obj(name, solid(colour), g, radius=W / 2 if round_ else 0.0, base=(length, W))


def slide_keys(keys_):
    """along(fr) from [(frame, value)] eased between keys."""
    return lambda fr: ease_pts(keys_, fr)[0]


# --- Shapes redrawn every frame: one outline per frame in `pathShapes`, the `path` key held on each frame ----------
EMPTY = "M -50 -50 L -49 -50 L -49 -49 Z"


def svg_of(polys):
    """Polygons in 960×540 reference px → an SVG path on the 0..100 box of a full-frame shape."""
    out = [("M " + " L ".join(f"{x / 9.6:.2f} {y / 5.4:.2f}" for x, y in pts) + " Z") for pts in polys if len(pts) > 2]
    return " ".join(out) or EMPTY


def framed(s, name, colour, frames):
    """A full-frame shape whose outline is frames[fr] (a list of polygons) on each frame of the reference; nothing
    before or after."""
    order = sorted(frames)
    paths = [EMPTY] + [svg_of(frames[fr]) for fr in order]
    clip = s.obj(name, solid(colour), lambda fr, u: (960, 540, 1920, 1080, 0, 1), path=paths[1])
    kf = [(0.0, 0, "hold")] if order[0] > 0 else []
    for i, fr in enumerate(order):
        kf.append((round(fr / F, 4), i + 1, "hold"))
    if round((order[-1] + 1) / F, 4) < s.dur:
        kf.append((round((order[-1] + 1) / F, 4), 0, "hold"))
    clip["shapeStyle"]["customPath"] = paths[1]
    clip["shapeStyle"]["pathShapes"] = paths
    clip["shapeStyle"].setdefault("keyframes", {})["path"] = keys(kf)
    return clip


def clip_rect(pts, x0=-2.0, y0=-2.0, x1=962.0, y1=542.0):
    """Sutherland-Hodgman: a convex polygon cut to the frame."""
    def cut(poly, inside, cross):
        out = []
        for i, p in enumerate(poly):
            q = poly[i - 1]
            if inside(p):
                if not inside(q):
                    out.append(cross(q, p))
                out.append(p)
            elif inside(q):
                out.append(cross(q, p))
        return out

    def at_x(xv):
        return lambda q, p: (xv, q[1] + (p[1] - q[1]) * (xv - q[0]) / (p[0] - q[0]))

    def at_y(yv):
        return lambda q, p: (q[0] + (p[0] - q[0]) * (yv - q[1]) / (p[1] - q[1]), yv)
    for inside, cross in ((lambda p: p[0] >= x0, at_x(x0)), (lambda p: p[0] <= x1, at_x(x1)),
                          (lambda p: p[1] >= y0, at_y(y0)), (lambda p: p[1] <= y1, at_y(y1))):
        if not pts:
            break
        pts = cut(pts, inside, cross)
    return pts


def diag_band(c0, c1, tip=None):
    """A bar running down-right at 45° between the lines x - y = c0 and c1, from beyond the top-left corner; with a
    tip (x + y of its front) it ends in a half circle there."""
    r2 = math.sqrt(2)
    va, vb = c0 / r2, c1 / r2
    uv = [(-2000, va)]
    if tip is None:
        uv += [(2000, va), (2000, vb)]
    else:
        r, vm = (vb - va) / 2, (va + vb) / 2
        uc = tip / r2 - r
        uv += [(uc + r * math.cos(math.radians(a)), vm + r * math.sin(math.radians(a))) for a in range(-90, 91, 10)]
    uv.append((-2000, vb))
    return clip_rect([((u + v) / r2, (u - v) / r2) for u, v in uv])


DIAG = {  # frame: [(colour, c0, c1, tip s or None)], c = x - y and s = x + y on the 960×540 reference
    1: [('W', 50, 432, 298)],
    2: [('W', 50, 432, 634), ('D', -248, 314, 106), ('R', 380, 510, 659)],
    3: [('W', 50, 432, 890), ('D', -248, 314, 426), ('R', 390, 520, 827)],
    4: [('W', 50, 432, 1090), ('D', -248, 314, 722), ('R', 415, 566, 965), ('R', -330, -248, 360)],
    5: [('R', -400, -246, 690), ('D', -246, 314, 950), ('W', 50, 428, 1246), ('R', 428, 560, 1074), ('W', 560, 600, None)],
    6: [('R', -432, -246, None), ('D', -246, 312, 1124), ('W', 50, 438, 1400), ('R', 438, 558, 1168), ('W', 558, 892, None)],
    7: [('R', -464, -240, None), ('D', -240, 306, 1258), ('W', 306, 442, None), ('R', 442, 552, 1249), ('W', 552, 940, None)],
    8: [('R', -494, -232, None), ('D', -232, 300, 1358), ('W', 300, 446, None), ('R', 446, 550, 1314), ('W', 550, 948, None)],
    9: [('R', -526, -226, None), ('D', -226, 292, 1434), ('W', 292, 448, None), ('R', 448, 548, 1370), ('W', 548, 1100, None)],
    10: [('R', -700, -218, None), ('D', -218, 284, 1470), ('W', 284, 452, None), ('R', 452, 546, 1430), ('W', 546, 1100, None)],
    11: [('R', -700, -206, None), ('D', -206, 274, None), ('W', 274, 452, None), ('R', 452, 540, None), ('W', 540, 1100, None)],
    12: [('R', -700, -198, None), ('D', -198, 262, None), ('W', 262, 454, None), ('R', 454, 540, None), ('W', 540, 1100, None)],
    13: [('R', -700, -186, None), ('D', -186, 252, None), ('W', 252, 458, None), ('R', 458, 540, None), ('W', 540, 1100, None)],
    14: [('R', -700, -172, None), ('D', -172, 240, None), ('W', 240, 458, None), ('R', 458, 538, None), ('W', 538, 1100, None)],
    15: [('R', -700, -160, None), ('D', -160, 228, None), ('W', 228, 356, None), ('R', 356, 366, None), ('W', 366, 460, None), ('R', 460, 538, None), ('W', 538, 1100, None)],
    16: [('R', -700, -148, None), ('D', -148, 216, None), ('W', 216, 352, None), ('R', 352, 388, None), ('W', 388, 460, None), ('R', 460, 534, None), ('W', 534, 1100, None)],
    17: [('R', -700, -138, None), ('D', -138, 204, None), ('W', 204, 344, None), ('R', 344, 432, None), ('W', 432, 460, None), ('R', 460, 532, None), ('W', 532, 1100, None)],
    18: [('R', -700, -126, None), ('D', -126, 192, None), ('W', 192, 328, None), ('R', 328, 532, None), ('W', 532, 1100, None)],
    19: [('R', -700, -114, None), ('D', -114, 156, None), ('W', 156, 206, None), ('D', 206, 216, None), ('W', 216, 330, None), ('R', 330, 614, None), ('W', 614, 1100, None)],
    20: [('R', -700, -106, None), ('D', -106, 92, None), ('W', 92, 192, None), ('D', 192, 228, None), ('W', 228, 394, None), ('R', 394, 758, None), ('W', 758, 1100, None)],
    21: [('R', -700, -98, None), ('D', -98, 4, None), ('W', 4, 166, None), ('D', 166, 254, None), ('W', 254, 480, None), ('R', 480, 928, None), ('W', 928, 1100, None)],
    22: [('R', -700, -100, None), ('W', -100, 124, None), ('D', 124, 298, None), ('W', 298, 586, None), ('R', 586, 1100, None)],
    23: [('R', -700, -202, None), ('W', -202, 60, None), ('D', 60, 362, None), ('W', 362, 692, None), ('R', 692, 1100, None)],
    24: [('R', -700, -304, None), ('W', -304, -28, None), ('D', -28, 450, None), ('W', 450, 790, None), ('R', 790, 1100, None)],
    25: [('R', -700, -386, None), ('W', -386, -130, None), ('D', -130, 192, None), ('R', 192, 210, None), ('W', 210, 228, None), ('D', 228, 552, None), ('W', 552, 874, None), ('R', 874, 1100, None)],
    26: [('R', -700, -460, None), ('W', -460, -238, None), ('D', -238, 166, None), ('R', 166, 214, None), ('W', 214, 254, None), ('D', 254, 658, None), ('W', 658, 948, None), ('R', 948, 1100, None)],
    27: [('R', -700, -514, None), ('W', -514, -336, None), ('D', -336, 122, None), ('R', 122, 204, None), ('W', 216, 298, None), ('D', 298, 758, None), ('W', 758, 1100, None)],
    28: [('W', -700, -422, None), ('D', -422, 58, None), ('R', 58, 190, None), ('W', 230, 362, None), ('D', 362, 844, None), ('W', 844, 1100, None)],
    29: [('W', -700, -494, None), ('D', -494, -26, None), ('R', -26, 164, None), ('W', 256, 448, None), ('D', 448, 920, None), ('W', 920, 1100, None)],
    30: [('D', -700, -132, None), ('R', -132, 124, None), ('W', 298, 552, None), ('D', 552, 1100, None)],
    31: [('D', -700, -238, None), ('R', -238, 58, None), ('W', 362, 660, None), ('D', 660, 1100, None)],
    32: [('D', -700, -338, None), ('R', -338, -28, None), ('W', 448, 758, None), ('D', 758, 1100, None)],
    33: [('D', -700, -424, None), ('R', -424, -132, None), ('W', 552, 844, None), ('D', 844, 1100, None)],
    34: [('D', -700, -494, None), ('R', -494, -240, None), ('W', 658, 916, None), ('D', 916, 1100, None)],
    35: [('R', -700, -338, None), ('W', 756, 1100, None)],
    36: [('R', -700, -424, None), ('W', 842, 1100, None)],
    37: [('R', -700, -494, None), ('W', 914, 1100, None)],
}

STRIPES = {  # frame: (white, red, dark) outlines traced from the reference, 960×540 px, «x,y x,y;…»
    0: ('', '', '440,309 439,377 443,382 519,384 516,390 504,393 503,403 506,409 515,412 511,421 515,456 531,467 533,492 525,503 529,516 529,544 746,544 741,528 728,515 674,515 654,495 655,467 660,458 668,458 676,452 742,452 744,442 735,434 721,440 715,447 706,446 700,437 674,434 654,412 640,407 663,399 654,389 625,390 617,409 608,405 606,392 595,391 589,401 591,427 587,431 556,431 536,413 540,397 537,382 532,379 520,381 518,306 511,301 448,303'),
    1: ('939,-4 939,544 964,544 964,-4;-4,-4 -4,544 20,544 20,-4', '', '440,309 439,377 443,382 519,384 516,390 504,393 503,403 506,409 515,412 511,421 515,454 529,463 533,475 533,492 525,504 529,531 524,544 746,544 741,528 728,515 674,515 652,493 652,469 658,457 676,452 742,451 742,442 734,432 727,438 676,433 654,412 641,408 644,404 663,399 663,396 654,389 625,388 617,407 610,406 604,399 593,400 591,427 587,431 556,431 536,413 540,397 537,382 533,378 520,381 518,306 511,301 448,303'),
    2: ('912,-4 912,544 964,544 964,-4;-4,-4 -4,544 47,544 47,-4', '', '374,266 379,300 387,308 387,326 394,333 395,355 407,372 408,402 411,406 416,406 426,397 430,386 436,389 439,381 447,384 519,384 516,390 504,393 503,403 506,409 515,412 511,421 515,454 533,468 533,488 525,503 529,515 526,544 746,544 730,516 717,511 674,515 652,492 652,469 658,457 676,452 740,451 742,443 734,432 722,438 717,435 690,436 684,431 674,430 658,414 641,408 663,395 654,385 625,388 617,407 607,404 608,391 600,388 591,395 591,427 587,431 556,431 536,413 536,404 544,396 539,384 533,378 520,381 520,310 515,303 445,304 439,312 439,359 436,363 412,345 419,329 413,316 405,319 402,315 400,290 410,289 413,285 400,275 399,262 392,262 388,277 383,274 380,264'),
    3: ('882,-4 881,544 964,544 964,-4;-4,-4 -4,544 78,544 78,-4', '', '376,266 383,285 383,298 391,307 391,324 398,331 399,359 409,372 416,407 427,404 442,382 519,384 516,390 504,393 503,403 506,409 515,412 511,430 517,453 531,461 535,473 533,487 524,500 529,515 526,544 749,544 747,532 728,513 717,509 674,513 656,496 640,492 641,487 651,481 652,467 658,455 674,448 737,449 740,442 734,432 722,438 674,430 665,419 671,414 670,408 645,411 639,405 641,400 663,395 653,383 624,383 615,398 609,397 605,387 595,385 586,398 591,408 587,423 571,431 556,431 536,413 536,404 544,396 539,384 532,376 522,383 520,381 520,309 516,303 444,304 439,311 439,358 436,362 425,356 419,346 422,329 417,313 413,312 408,318 404,314 403,290 414,289 416,284 405,275 403,262 399,259 392,262 390,276 384,272 382,264'),
    4: ('849,-4 846,544 964,544 964,-4;-4,-4 -4,544 110,544 113,-4', '', '380,263 385,297 393,306 393,324 399,330 401,359 409,368 415,387 416,407 433,400 442,383 519,384 516,390 504,393 503,403 506,409 515,412 511,428 517,453 531,461 535,473 524,499 529,515 527,544 749,544 743,526 728,513 702,507 676,509 662,504 654,495 641,493 641,489 649,486 656,476 654,459 658,454 666,454 674,448 700,448 704,444 702,434 689,434 671,427 665,418 672,412 672,403 655,384 623,383 615,398 609,397 605,387 595,385 586,398 591,409 587,423 571,431 556,431 540,415 544,395 537,380 529,376 524,382 520,381 520,308 516,303 445,304 439,312 439,353 431,357 420,343 426,331 419,314 413,318 408,315 405,286 418,286 418,282 407,277 402,257 398,259 394,272 386,262'),
    5: ('815,-4 815,149 813,153 798,153 795,156 795,178 798,181 804,178 804,163 807,160 814,163 813,322 811,325 783,325 775,333 775,352 780,359 809,360 812,365 809,544 952,544 957,-4;7,-4 2,544 144,544 144,359 169,364 175,361 178,355 178,342 172,329 164,324 146,320 147,166 153,166 153,182 156,185 160,184 162,166 168,162 162,148 170,142 167,138 160,139 155,143 153,153 148,153 150,-4', '964,-4 951,544 964,544;8,-4 -4,-4 -4,544', '380,263 385,297 393,306 393,324 399,330 401,359 409,368 415,385 415,406 420,407 433,400 442,383 519,384 516,390 504,393 503,403 506,409 515,412 511,428 517,453 530,460 535,471 524,500 529,513 527,544 749,544 743,526 728,513 702,507 676,509 662,504 654,495 641,492 641,487 656,475 656,455 666,454 674,448 700,448 704,444 702,434 689,434 671,427 665,418 672,412 672,403 654,384 623,383 615,398 609,397 605,387 595,385 586,398 591,409 587,423 571,431 556,431 540,415 544,395 537,380 529,376 524,382 520,381 520,308 515,302 445,304 439,312 439,353 431,357 420,343 426,331 419,314 413,318 408,315 405,286 418,286 418,282 407,277 402,257 398,259 394,272 386,262'),
    6: ('781,-4 781,126 771,544 936,544 946,-4;23,-4 13,544 178,544 188,-4', '946,-4 935,544 964,544 964,-4;-4,-4 -4,544 13,544 24,-4', '384,262 389,296 397,305 403,357 411,366 417,385 416,407 435,400 444,384 519,384 516,390 504,393 503,403 506,409 515,412 511,428 517,453 530,459 535,471 524,497 529,513 529,544 749,544 743,526 726,513 702,507 676,509 662,504 654,495 641,492 641,487 654,475 656,455 666,454 674,448 700,448 704,444 702,434 676,431 665,418 672,412 672,403 654,384 622,381 615,396 611,396 605,387 595,385 588,395 591,411 587,423 571,431 556,431 540,415 544,395 537,380 529,376 524,382 520,381 520,308 515,302 444,304 439,311 439,351 434,355 423,343 423,338 430,331 423,314 415,319 410,314 410,286 422,281 410,274 406,257 402,258 397,270 390,266 389,261'),
    7: ('748,-4 732,544 916,544 934,-4;42,-4 25,544 211,544 228,-4', '934,-4 917,544 964,544 964,-4;-4,-4 -4,544 25,544 42,-4', '504,393 504,407 515,412 511,428 516,446 522,454 533,459 536,474 524,497 533,523 529,544 732,544 732,523 720,515 717,506 702,503 664,505 656,496 641,492 641,485 654,475 656,455 666,454 674,448 700,446 704,442 700,433 676,431 665,418 672,412 672,403 654,384 621,381 610,385 605,400 593,394 587,423 571,431 554,430 540,415 540,404 550,399 551,393 541,389 533,373 528,374 517,390'),
    8: ('716,-4 691,544 896,544 921,-4;63,-4 38,544 242,544 268,-4', '921,-4 896,544 964,544 964,-4;-4,-4 -4,544 38,544 63,-4', '392,257 390,271 394,276 395,292 403,301 407,340 421,377 418,406 427,406 438,399 448,384 519,384 516,390 504,393 503,403 506,409 515,412 511,428 516,446 522,454 533,459 536,474 524,497 534,527 531,544 691,544 692,523 681,516 692,510 691,504 664,503 657,495 638,488 650,473 650,456 654,452 664,452 672,446 690,446 694,442 692,432 674,430 663,417 671,412 672,403 656,382 619,380 610,385 605,400 597,394 592,395 591,411 583,427 556,431 540,415 540,404 550,399 551,393 533,372 524,382 520,381 519,306 512,301 446,303 439,311 439,326 434,330 429,312 421,317 416,312 417,285 428,282 429,278 418,272 415,255 410,255 403,266 397,257'),
    9: ('686,-4 650,544 874,544 910,-4;85,-4 49,544 274,544 309,-4', '909,-4 874,544 964,544 964,-4;-4,-4 -4,544 49,544 85,-4', '397,255 394,270 399,290 407,299 409,338 423,375 420,406 429,406 440,399 451,384 519,384 504,406 515,412 511,428 516,446 537,463 537,472 524,497 524,503 535,520 533,544 650,544 648,495 644,491 639,492 636,485 648,471 645,458 655,444 655,410 642,406 633,398 630,389 652,394 655,392 654,380 620,379 606,394 600,392 596,383 583,386 578,395 591,409 587,423 564,431 556,418 540,414 541,402 554,399 555,393 544,383 520,382 519,306 512,301 445,303 439,309 438,332 435,334 433,311 425,315 420,313 421,285 433,279 422,272 417,253 413,253 407,262'),
    10: ('654,-4 606,544 852,544 900,-4;108,-4 59,544 305,544 353,-4', '900,-4 851,544 964,544 964,-4;-4,-4 -4,544 59,544 108,-4', '397,255 394,270 398,276 399,291 407,301 409,338 423,375 420,406 429,406 440,399 451,384 518,383 519,387 510,393 504,406 515,412 511,428 516,447 537,463 537,472 524,497 524,503 535,520 533,544 606,544 607,520 604,514 609,501 608,475 601,466 606,460 608,432 614,424 614,385 609,383 604,394 596,383 579,389 579,397 591,409 587,423 571,431 562,430 556,418 540,414 541,402 554,399 555,393 544,383 520,382 519,306 510,301 445,303 439,309 438,332 435,334 433,311 425,315 420,313 421,285 433,279 422,272 417,253 413,253 407,262'),
    11: ('619,-4 555,544 826,544 891,-4;133,-4 69,544 340,544 404,-4', '891,-4 827,544 964,544 964,-4;-4,-4 -4,544 68,544 132,-4', '414,252 411,261 400,260 398,269 403,291 411,301 413,337 419,345 425,367 422,405 431,405 454,384 519,384 504,406 515,412 511,428 516,447 537,463 537,472 524,503 537,520 535,544 555,544 557,518 551,506 558,501 560,494 557,475 560,426 556,418 540,414 541,402 554,399 555,393 544,383 520,382 520,308 512,301 444,303 436,311 424,315 425,285 430,276 425,270 423,255'),
    12: ('575,-4 492,544 791,544 874,-4;168,-4 86,544 385,544 467,-4', '874,-4 791,544 964,544 964,-4;-4,-4 -4,544 85,544 168,-4', ''),
    13: ('226,-4 121,544 733,544 838,-4', '838,-4 733,544 964,544 964,-4;-4,-4 -4,544 121,544 226,-4', ''),
    14: ('306,-4 175,544 654,544 784,-4', '785,-4 654,544 964,544 964,-4;-4,-4 -4,544 174,544 305,-4', ''),
    15: ('391,-4 228,544 558,544 721,-4', '721,-4 559,544 964,544 964,-4;-4,-4 -4,544 228,544 390,-4', ''),
    16: ('654,-4 325,-4 124,544 452,544', '654,-4 453,544 964,544 964,-4;325,-4 -4,-4 -4,544 123,544', ''),
    17: ('586,-4 261,-4 255,11 255,20 244,34 239,53 231,63 223,86 208,112 205,125 200,129 198,139 178,176 175,188 128,284 127,293 122,297 11,544 338,544', '587,-4 338,544 873,544 930,413 964,356 964,-4;259,-4 86,-4 -4,183 -4,544 11,537', '964,361 903,474 901,491 892,499 875,544 964,544;81,-4 -4,-4 -4,168 5,168 16,152 17,139 32,117 34,98 43,92 44,83 65,46 74,19 81,12'),
    18: ('517,-4 192,-4 191,6 -4,333 -4,544 211,544 220,518 463,100 472,79 514,11', '964,-4 520,-4 212,544 752,544 936,217 964,182', '964,191 949,198 943,207 941,220 928,232 926,245 912,261 886,306 884,317 863,345 845,384 831,401 829,412 817,426 807,451 799,457 780,492 778,506 768,512 756,544 964,544;190,-4 -4,-4 -4,322 10,317 59,233 66,213 77,202 83,180 92,174 106,152 114,132 130,108 131,100 145,83 147,68 158,61'),
    19: ('450,-4 120,-4 14,150 -4,165 -4,544 64,544 200,351 204,340 212,334 240,292 252,279 292,218 299,213', '964,-4 452,-4 66,544 618,544 964,67', '964,74 934,100 933,107 920,121 919,129 909,136 879,178 879,186 864,198 853,219 842,229 837,243 820,259 809,278 796,291 782,316 753,352 752,359 742,367 725,397 671,465 662,483 625,529 621,544 964,544;114,-4 -4,-4 -4,162 10,154 53,94 67,68 81,55 97,32 98,22 109,16'),
    20: ('376,-4 32,-4 23,13 -4,35 -4,412 107,297 107,293 126,277 213,182 226,164 266,124 272,114 339,44', '955,-4 378,-4 -4,414 -4,544 465,544 930,31', '964,9 943,17 920,41 915,53 879,86 866,105 838,131 836,138 818,153 811,167 786,189 664,321 662,328 649,338 647,348 636,352 620,375 602,389 549,451 541,456 519,486 486,516 468,544 964,544'),
    21: ('-4,241 216,63 288,-4 -4,-4', '-4,544 277,544 917,-4 290,-4 -4,242', '964,-4 917,-4 893,29 886,29 875,36 735,158 702,182 692,196 676,203 648,229 645,238 633,240 595,274 586,278 547,317 538,319 504,351 480,368 474,378 455,388 443,405 430,409 408,432 386,446 376,460 368,462 343,486 336,488 313,509 309,517 300,525 290,527 279,544 926,544 964,511'),
    22: ('964,424 790,526 773,544 964,544;-4,96 7,95 33,77 46,72 159,-4 -4,-4', '-4,544 12,544 838,32 886,-4 161,-4 -4,99', '964,-4 886,-4 850,28 841,30 810,53 783,66 779,74 772,73 729,102 719,104 680,128 667,142 643,151 630,159 625,167 587,186 574,196 571,205 561,204 509,237 501,238 489,251 475,254 441,276 434,286 420,288 404,302 378,313 365,326 326,346 289,373 277,376 233,406 226,407 161,447 153,460 143,461 113,476 15,544 774,544 818,508 964,424'),
    23: ('964,369 619,508 550,544 802,544 858,512 867,511 964,472', '964,474 802,544 964,544;-4,358 854,5 860,-4 -4,-4', '964,-4 864,-4 862,9 857,13 836,13 828,20 808,24 787,33 776,44 755,46 738,54 733,61 715,63 698,79 675,79 642,94 637,101 626,100 620,109 599,111 590,120 551,130 539,139 519,144 508,154 498,153 490,159 481,159 457,175 442,175 427,189 419,187 405,191 392,201 371,206 363,214 346,215 314,229 310,234 291,238 276,249 251,255 229,267 171,288 163,295 149,297 91,325 76,327 30,350 17,351 -4,360 -4,544 551,544 560,532 851,413 869,402 889,397 902,386 918,385 949,370 964,369'),
    24: ('964,333 95,544 490,544 705,487 718,481 727,482 870,448 885,441 894,442 964,427', '964,427 534,527 493,544 964,544;-4,196 822,-4 -4,-4', '964,-4 828,-4 825,6 807,5 797,13 764,15 748,28 741,22 671,37 657,44 629,47 532,70 524,75 490,79 428,95 421,102 413,101 392,109 377,107 324,119 316,124 274,132 269,140 253,137 168,159 155,159 148,166 133,165 120,173 97,173 84,179 56,183 48,190 36,188 -4,197 -4,544 95,544 102,530 137,528 158,520 201,513 700,394 710,386 740,385 789,370 844,360 854,354 874,353 964,333'),
    25: ('964,307 -4,382 -4,468 821,404 826,400 830,403 964,394', '964,394 -4,468 -4,544 964,544;-4,48 429,16 529,6 557,6 606,-4 -4,-4', '964,-4 606,-4 602,3 531,7 524,14 453,13 383,19 377,29 318,29 306,25 302,28 271,27 207,35 -4,49 -4,382 75,377 86,370 100,375 118,370 140,372 267,362 278,354 292,360 310,354 332,357 354,352 372,354 715,327 726,322 744,325 964,306'),
    26: ('-4,222 -4,302 964,364 964,285', '-4,303 -4,490 714,536 717,544 964,544 964,365', '-4,493 -4,544 701,544 693,535 378,515 364,517 326,511 255,507 227,509 206,503 31,495 12,491;-4,-4 -4,222 267,240 316,240 330,244 512,256 571,256 588,261 757,272 827,272 835,277 964,285 964,-4'),
    27: ('-4,71 -4,148 28,150 34,154 246,196 259,196 286,204 323,209 387,224 964,336 964,259 490,167 474,166', '-4,148 -4,328 964,516 964,336', '-4,335 -4,544 964,544 964,519 926,509 823,492 814,487 791,485 774,479 747,478 733,471 709,469 694,463 670,459 659,461 651,455 582,442 571,443 510,427 492,428 485,423 454,421 436,413 413,415 398,405 382,405 307,388 296,390 286,383 222,374 206,367 169,365 162,359 140,360 122,351 106,351 22,331 8,331;-4,-4 -4,71 18,72 41,80 59,80 83,88 139,96 189,109 219,112 244,120 381,144 687,207 715,208 724,214 774,224 794,224 810,231 964,259 964,-4'),
    28: ('-4,237 -4,309 720,544 947,544 841,503 638,439 629,439 614,431 598,429 591,424 572,420 526,403 273,325 198,299 178,295 141,281 114,275 109,271 94,269 87,264;16,-4 24,6 964,301 964,230 339,34 240,-4', '-4,-4 -4,237 771,480 949,544 964,544 964,302 138,43 10,-4', '-4,310 -4,544 707,544 683,526 654,521 633,510 606,505 586,495 558,489 383,431 350,425 328,413 316,413 280,398 238,389 229,382 141,357;255,-4 258,7 336,32 347,32 357,39 395,48 469,75 945,226 964,227 964,-4'),
    29: ('-4,277 -4,346 448,544 606,544 598,532 579,527 565,518 519,498 502,493 433,461;352,-4 355,4 380,15 390,16 417,31 430,34 439,40 446,40 459,49 964,262 964,193 511,-4', '-4,107 -4,276 284,396 610,544 964,544 964,519;-4,-4 -4,21 964,432 964,263 513,73 349,-4', '-4,351 -4,544 441,544 438,534 378,508 360,505 346,494 282,470 93,385 29,361 15,352;527,-4 528,7 535,12 555,16 579,31 654,63 667,64 684,76 964,192 964,-4'),
    30: ('-4,322 -4,389 280,544 405,544 301,481;554,-4 964,217 964,150 683,4 680,-4', '-4,157 -4,321 398,532 406,544 712,544 694,527;247,-4 305,34 964,382 964,218 681,71 553,-4', '-4,393 -4,544 276,544 111,447 27,406 15,396;687,-4 689,6 701,13 717,17 735,31 749,33 768,49 964,150 964,-4'),
    31: ('-4,374 -4,438 82,488 158,544 256,544 253,533;699,-4 722,17 964,165 964,101 801,-4', '-4,213 -4,373 238,522 261,544 513,544 489,521;446,-4 505,40 964,326 964,166 721,17 698,-4', '-4,443 -4,544 154,544 148,531 29,459 14,446;806,-4 822,15 964,100 964,-4'),
    32: ('-4,432 -4,495 61,544 144,544 144,536;812,-4 964,107 964,45 897,-4', '-4,274 -4,431 46,462 148,544 363,544;596,-4 964,265 964,108 811,-4', ''),
    33: ('', '-4,343 -4,495 54,544 241,544 11,349;718,-4 948,190 964,196 964,44 905,-4', ''),
    34: ('', '-4,416 -4,544 137,544 85,489 9,421;822,-4 894,68 964,123 964,-4', ''),
    35: ('', '', ''),
    36: ('', '', ''),
}


# --- 14. A transition: rounded white, grey and red bars shoot in on the diagonal, open thin lines, and part ---------
def diagonal_bars():
    """Copied frame by frame (29.6-30.8 s): every frame's bars measured across the reference (DIAG), the round
    fronts while they come in, the lines that open inside them and the gap that shows the next video."""
    D = 1.3
    t = _p("transicion-diagonal", "Transición: barras diagonales roja, blanca y gris", "Transition: red, white and grey "
           "diagonal bars", 12340, D, "transiciones", ["transición", "diagonal"], thumb=0.5)
    s = P(t, D, plain=True)
    for colour, name, key in ((WHITE, "Barras blancas", "W"), (RED, "Barras rojas", "R"), (DARK, "Barras grises", "D")):
        frames = {fr: [diag_band(a - 1.5, b + 1.5, tip) for k, a, b, tip in row if k == key]
                  for fr, row in DIAG.items()}
        framed(s, name, colour, {fr: [p for p in v if p] for fr, v in frames.items()})
    return t


# --- Social network icons: a coloured rounded square with a simple white mark ------------------------------------
NETS = {  # name: (colour or gradient pair, mark kind, mark)
    "behance": ("#1769FF", "text", "Bē"), "instagram": (("#8A3AB9", "#F9A13A"), "insta", None),
    "pinterest": ("#D3202F", "text", "P"), "vimeo": ("#1AB7EA", "text", "v"),
    "blogger": ("#F57D00", "text", "B"), "linkedin": ("#0A66C2", "text", "in"),
    "skype": ("#00AFF0", "text", "S"), "whatsapp": ("#25D366", "whats", None),
    "facebook": ("#1877F2", "text", "f"), "periscope": ("#40A4C4", "pin", None),
    "twitter": ("#1DA1F2", "bird", None), "youtube": (RED, "play", None),
}
BIRD = poly([(0, 78), (22, 80), (36, 72), (14, 62), (8, 52), (18, 50), (4, 38), (4, 30), (16, 32), (6, 14), (12, 6),
             (34, 28), (50, 34), (50, 22), (58, 10), (72, 6), (86, 12), (98, 8), (92, 18), (100, 18), (92, 28), (90, 44),
             (80, 64), (60, 82), (34, 92), (12, 90)])
PIN = poly([(50 + 40 * math.cos(math.radians(a)), 40 + 40 * math.sin(math.radians(a))) for a in range(150, 400, 15)]
           + [(50, 100)])


def net_icon(s, net, geom, size=80, name=None):
    """A network's icon: geom(fr, u) = (cx, cy, scale, rot, opacity)."""
    colour, mark, text = NETS[net]
    name = name or net.capitalize()
    layers = solid(colour) if isinstance(colour, str) else \
        [gradient([(0.0, colour[0]), (0.55, "#E1306C"), (1.0, colour[1])], angle=45), no_stroke()]
    s.obj(name, layers, lambda fr, u: (lambda g: (g[0], g[1], size * g[2], size * g[2], g[3], g[4]))(geom(fr, u)),
          radius=size * 0.14, base=(size, size))

    def part(w, h, dx=0.0, dy=0.0):
        def g(fr, u):
            cx, cy, sc, rot, op = geom(fr, u)
            x, y = rot_pt(cx + dx * sc, cy + dy * sc, rot, cx, cy)
            return x, y, w * sc, h * sc, rot, op
        return g
    if mark == "text":
        ink = (-size * 0.3, -size * 0.27, size * 0.3, size * 0.27)
        width = {"Bē": 0.62, "in": 0.48, "f": 0.2, "P": 0.36, "B": 0.36, "S": 0.34, "v": 0.38}[text] * size
        ink = (-width / 2, -size * 0.27, width / 2, size * 0.27)

        def tg(fr, u):
            cx, cy, sc, rot, op = geom(fr, u)
            return cx, cy, sc, rot, op
        c = s.say(text, (960 + ink[0], 540 + ink[1], 960 + ink[2], 540 + ink[3]), M, 800, WHITE, f"{name} (marca)",
                  editable=False)
        s.tmove(c, lambda fr, u: (lambda g: (g[0] - 960, g[1] - 540, g[2], g[3], g[4]))(tg(fr, u)))
    elif mark == "insta":
        s.obj(f"{name} (marca)", ring(WHITE, 5), part(size * 0.56, size * 0.56), radius=size * 0.16, base=(size * 0.56,
                                                                                                       size * 0.56))
        s.obj(f"{name} (marca 2)", ring(WHITE, 5), part(size * 0.26, size * 0.26), kind="ellipse")
    elif mark == "whats":
        s.obj(f"{name} (marca)", ring(WHITE, 5), part(size * 0.6, size * 0.6), kind="ellipse")
        s.obj(f"{name} (marca 2)", solid(WHITE), part(size * 0.22, size * 0.22, -size * 0.02, 0), path=GLYPH["volume"])
    elif mark == "pin":
        s.obj(f"{name} (marca)", solid(WHITE), part(size * 0.46, size * 0.58), path=PIN)
        s.obj(f"{name} (marca 2)", solid(colour), part(size * 0.18, size * 0.18, 0, -size * 0.07), kind="ellipse")
    elif mark == "bird":
        s.obj(f"{name} (marca)", solid(WHITE), part(size * 0.6, size * 0.5), path=BIRD)
    elif mark == "play":
        s.obj(f"{name} (marca)", solid(WHITE), part(size * 0.62, size * 0.44), radius=size * 0.1,
              base=(size * 0.62, size * 0.44))
        s.obj(f"{name} (marca 2)", solid(colour), part(size * 0.18, size * 0.22, size * 0.02), path=TRIANGLE)


# --- 15. Social bars: diamonds pop in, turn into rounded squares, slide left and pull out a white bar ------------
SOC_LABEL = {"behance": "Behance", "instagram": "Instagram", "pinterest": "Pinterest", "vimeo": "Vimeo",
             "blogger": "Blogger", "linkedin": "Linkedin", "skype": "Skype", "whatsapp": "Whatsapp",
             "facebook": "Facebook", "periscope": "Periscope", "twitter": "Twitter", "youtube": "Youtube"}


def social_bars():
    D = dur_for(2.0, 2.8)
    t = _p("redes-barras", "Redes sociales: 12 barras con iconos", "Social media: 12 bars with icons", 12350, D, "redes",
           ["redes", "barras", "iconos"], thumb=2.6)
    s = P(t, D)
    cols = (("behance", "instagram", "pinterest", "vimeo"), ("blogger", "linkedin", "skype", "whatsapp"),
            ("facebook", "periscope", "twitter", "youtube"))
    for c, nets in enumerate(cols):
        ox = 643 * c
        for r, net in enumerate(nets):
            cy = 340 + 132 * r
            at = c + 0.5 * r

            def x_of(fr, ox=ox, at=at):
                return ox + 316 + (140 - 316) * k(fr, 36 + at, 22)

            def rot_of(fr, at=at):
                if fr < 30 + at:
                    return -15 + 60 * k(fr, 2 + at, 8) - 45 * k(fr, 10 + at, 8)
                return 45 * k(fr, 30 + at, 5) - 53 * k(fr, 36 + at, 12) + 8 * k(fr, 48 + at, 10)

            def geom(fr, u, x_of=x_of, rot_of=rot_of, cy=cy, at=at):
                return x_of(fr), cy, 0.3 + 0.7 * k(fr, 2 + at, 6), rot_of(fr), k(fr, 1 + at, 2)
            colour = NETS[net][0] if isinstance(NETS[net][0], str) else "#C13584"
            o = lambda fr, at=at: -347 * (1 - k(fr, 36 + at, 22))  # noqa: E731
            edge = lambda fr, x_of=x_of: x_of(fr) + 38  # noqa: E731
            x0, x1 = ox + 188, ox + 535
            s.rect(f"{SOC_LABEL[net]} (barra)", card_layers(alpha=0.18),
                   lambda fr, u, o=o, edge=edge, x0=x0, x1=x1, cy=cy: (max(x0 + o(fr), edge(fr)), cy - 24,
                                                                      max(x1 + o(fr), edge(fr) + 1), cy + 25))
            s.rect(f"{SOC_LABEL[net]} (raya)", solid(colour),
                   lambda fr, u, o=o, edge=edge, x0=x0, x1=x1, cy=cy: (max(x0 + o(fr), edge(fr)), cy - 25,
                                                                      max(x1 + o(fr), edge(fr) + 1), cy - 21))
            label = f"{SOC_LABEL[net]}.com/Channel"
            w = 266 * len(label) / 18
            s.say(label, (ox + 198, cy - 9, ox + 198 + w, cy + 13), M, 700, colour,
                  "Título" if (c, r) == (0, 0) else f"Red {4 * c + r + 1}", align="left",
                  reveal=lambda fr, edge=edge: (edge(fr), 0, 1920, 1080), shift=lambda fr, o=o: (o(fr), 0))
            net_icon(s, net, geom)
    return t


# --- 16-25. The red and white titles (37.5-42.2 s): each one alone, twice the reference's size, in the middle ----
def lit(colour=WHITE):
    return [shadow("#000000", 0, 4, 12, 0.3), fill(colour)]


class Big:
    """Draws a title measured on the reference frame (1920 px) scaled by sc about its centre (cx, cy), in the middle
    of the frame."""

    def __init__(self, s, cx, cy, sc=2.0):
        self.s, self.cx, self.cy, self.sc = s, cx, cy, sc

    def X(self, x):
        return 960 + (x - self.cx) * self.sc

    def Y(self, y):
        return 540 + (y - self.cy) * self.sc

    def R(self, r):
        return self.X(r[0]), self.Y(r[1]), self.X(r[2]), self.Y(r[3])

    def rect(self, name, layers, r, op=None):
        return self.s.rect(name, layers, lambda fr, u: self.R(r(fr) if callable(r) else r),
                           op=(lambda fr, u: op(fr)) if op else None)

    def line(self, name, pts, width, colour, at, n, closed=False):
        return self.s.outline(name, [(self.X(x), self.Y(y)) for x, y in pts], width * self.sc, colour, at=at, n=n,
                              closed=closed)

    def text(self, content, ink, family, weight, colour, name="Título", align="left", reveal=None, shift=None,
             op=None, spacing=0.0, layers=None, editable=True):
        x0, y0, x1, y1 = self.R(ink)
        p = f6.Piece(self.s.t, self.s.dur, 0)
        p.frame = self.s.frame
        edge = (x0 + x1) / 2 if align == "center" else x0 if align == "left" else x1
        sh = (lambda fr: (lambda v: (v[0] * self.sc, v[1] * self.sc))(shift(fr))) if shift else None
        rv = (lambda fr: self.R(reveal(fr))) if reveal else None
        clip = p.text(content, edge, y0, y1, x1 - x0, family, weight, colour, name, align=align, case="none",
                      layers=layers or lit(colour), reveal=rv, editable=editable, shift=sh, spacing_em=spacing)
        if op:
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, op(fr))), 4), "linear") for u, fr in self.s.each()])
        return clip


def title_piece(id, es, en, order, centre, build, entrance=1.4):
    D = dur_for(entrance, 2.0)
    t = _p(id, es, en, order, D, "titulos-estilo", ["título", "etiqueta"], thumb=entrance + 0.6)
    s = P(t, D)
    build(s, Big(s, *centre))
    return t


def t_new_project():
    def build(s, b):
        bar = lambda fr: 553 - 433 * k(fr, 2, 24)  # noqa: E731
        b.text("NEW PROJECT", (130, 182, 553, 222), M, 800, WHITE, reveal=lambda fr: (bar(fr) + 9, 0, 1920, 1080))
        b.rect("Barra", solid(RED), lambda fr: (bar(fr), 182, bar(fr) + 9, 221), op=lambda fr: k(fr, 2, 2))
        b.text("YOUR SUBTITLE", (345, 225, 551, 243), M, 600, RED, "Texto", align="right",
               reveal=lambda fr: (0, 223, 1920, 260), shift=lambda fr: (0, -20 * (1 - k(fr, 24, 8))),
               op=lambda fr: k(fr, 24, 2))
    return title_piece("titulo-new-project", "Título con barra roja que descubre el texto", "Title uncovered by a red bar",
                       12360, (336, 212), build)


def t_animation():
    def build(s, b):
        top = lambda fr: 246 - 63 * k(fr, 2, 12)  # noqa: E731
        b.rect("Caja", lit(RED), lambda fr: (782, top(fr), 1137, 246), op=lambda fr: k(fr, 2, 2))
        b.text("ANIMATION", (797, 195, 1127, 236), M, 800, WHITE, reveal=lambda fr: (782, top(fr), 1137, 246),
               shift=lambda fr: (0, 50 * (1 - k(fr, 8, 10))))
        c = b.text("MOTION DESIGN", (782, 157, 1140, 176), M, 500, WHITE, "Texto", spacing=0.42)
        s.anim(c, 22, 0.03, 0.12)
    return title_piece("titulo-animation", "Título en caja roja que crece", "Title in a growing red box", 12361,
                       (960, 202), build)


def t_rendering():
    def build(s, b):
        y = lambda fr: 140 + 50 * k(fr, 14, 10)  # noqa: E731
        b.rect("Línea", solid(RED), lambda fr: (1395, y(fr), 1395 + 345 * k(fr, 2, 10), y(fr) + 6))
        b.text("RENDERING", (1395, 203, 1738, 242), M, 800, WHITE, reveal=lambda fr: (0, y(fr) + 6, 1920, 1080),
               shift=lambda fr: (0, -55 * (1 - k(fr, 14, 12))))
        c = b.text("VERY FAST", (1397, 158, 1737, 185), M, 500, WHITE, "Texto", spacing=0.55)
        s.anim(c, 30, 0.03, 0.12)
    return title_piece("titulo-rendering", "Título bajo una línea roja que baja", "Title under a red line that drops",
                       12362, (1567, 200), build)


def t_your_channel():
    def build(s, b):
        x0, y0, x1, y1 = 120, 375, 550, 457
        b.line("Marco", [(x0, y1), (x0, y0), (x1, y0)], 4, RED, 6, 16)
        b.line("Marco 2", [(x1, y0), (x1, y1), (x0, y1)], 4, RED, 6, 16)
        box = lambda fr: (x0, y0, x1, y1)  # noqa: E731
        b.text("YOUR", (137, 398, 300, 434), M, 700, WHITE, reveal=box, shift=lambda fr: (0, -16 * (1 - k(fr, 12, 12))),
               op=lambda fr: k(fr, 12, 4))
        b.text("CHANNEL", (318, 398, 535, 434), M, 700, WHITE, "Texto", reveal=box,
               shift=lambda fr: (0, 14 * (1 - k(fr, 12, 12))), op=lambda fr: k(fr, 12, 4))
    return title_piece("titulo-your-channel", "Título en marco rojo", "Title in a red frame", 12363, (335, 416), build)


def t_simple():
    def build(s, b):
        b.line("Cuadro", [(806, 388), (806, 437), (770, 437), (770, 388), (806, 388)], 5, RED, 4, 10)
        b.text("SIMPLE TITLES", (812, 407, 1150, 440), M, 700, WHITE, reveal=lambda fr: (809, 0, 1920, 1080),
               shift=lambda fr: (-345 * (1 - k(fr, 26, 16)), 0))
        b.text("ANIMATION", (812, 386, 950, 404), M, 600, RED, "Texto", reveal=lambda fr: (809, 0, 1920, 1080),
               shift=lambda fr: (-145 * (1 - k(fr, 34, 10)), 0))
    return title_piece("titulo-simple", "Título que sale de un cuadro rojo", "Title sliding out of a red square", 12364,
                       (960, 413), build, entrance=1.6)


def t_clean():
    def build(s, b):
        for i, y in enumerate((380, 447)):
            b.rect(f"Línea {i + 1}", solid(RED), lambda fr, y=y, i=i: (1378, y, 1378 + 387 * k(fr, 2 + 2 * i, 12), y + 4))
        band = lambda fr: (0, 384, 1920, 447)  # noqa: E731
        b.text("CLEAN", (1378, 396, 1560, 436), M, 400, WHITE, reveal=band,
               shift=lambda fr: (0, -40 * (1 - k(fr, 14, 12))), op=lambda fr: k(fr, 14, 3))
        b.text("TITLES", (1572, 396, 1765, 436), M, 800, WHITE, "Texto", reveal=band,
               shift=lambda fr: (0, 40 * (1 - k(fr, 14, 12))), op=lambda fr: k(fr, 14, 3))
        b.text("MOTION DESIGN", (1382, 363, 1577, 376), M, 600, RED, "Texto 2", spacing=0.3,
               reveal=lambda fr: (0, 300, 1920, 380), shift=lambda fr: (0, 18 * (1 - k(fr, 24, 8))))
    return title_piece("titulo-clean", "Título entre dos líneas rojas", "Title between two red lines", 12365,
                       (1571, 407), build)


def t_motion_design():
    def build(s, b):
        half = lambda fr: 85 * k(fr, 2, 10)  # noqa: E731
        b.text("MOTION DESIGN", (117, 607, 553, 644), M, 800, WHITE, reveal=lambda fr: (0, 500, 1920, 647),
               shift=lambda fr: (0, 45 * (1 - k(fr, 6, 12))))
        b.rect("Etiqueta", lit(RED), lambda fr: (335 - half(fr), 648, 335 + half(fr), 680), op=lambda fr: k(fr, 2, 2))
        b.text("YOUR BRAND", (258, 655, 413, 673), M, 700, WHITE, "Texto", op=lambda fr: k(fr, 14, 6))
    return title_piece("titulo-motion-design", "Título con etiqueta roja", "Title with a red tag", 12366, (335, 643),
                       build)


def t_just_edit():
    def build(s, b):
        x0, y0, x1, y1 = 768, 613, 1152, 684
        b.line("Marco", [(900, y1), (x0, y1), (x0, y0), (960, y0)], 5, RED, 4, 14)
        b.line("Marco 2", [(1030, y1), (x1, y1), (x1, y0), (960, y0)], 5, RED, 4, 14)
        b.text("JUST EDIT", (795, 625, 1125, 670), M, 800, WHITE, reveal=lambda fr: (x0, y0, x1, y1),
               shift=lambda fr: (0, 60 * (1 - k(fr, 14, 14))))
        b.text("TEMPLATE", (902, 676, 1020, 692), M, 500, WHITE, "Texto", op=lambda fr: k(fr, 28, 6))
    return title_piece("titulo-just-edit", "Título en marco con texto abajo", "Title in a frame with a word below",
                       12367, (960, 650), build)


def t_best():
    def build(s, b):
        x1 = 1560
        b.rect("Etiqueta", lit(RED), lambda fr: (x1 - 174 * k(fr, 2, 10), 645, x1, 668), op=lambda fr: k(fr, 2, 2))
        b.text("MARKETPLACE", (1393, 649, 1552, 664), M, 700, WHITE, "Texto", op=lambda fr: k(fr, 10, 6))
        b.text("BEST", (1565, 610, 1785, 668), M, 800, WHITE, reveal=lambda fr: (0, 0, 1860, 1080),
               shift=lambda fr: (270 * (1 - k(fr, 4, 16)), 0))
        b.text("MOTION", (1385, 610, 1563, 640), M, 400, WHITE, "Texto 2", reveal=lambda fr: (0, 0, 1563, 1080),
               shift=lambda fr: (180 * (1 - k(fr, 30, 10)), 0))
    return title_piece("titulo-best", "Título con etiqueta y palabra que entra", "Title with a tag and a sliding word",
                       12368, (1585, 639), build)


def t_brand():
    def build(s, b):
        b.text("MOTION", (910, 853, 1025, 868), M, 500, WHITE, "Texto", spacing=0.3, op=lambda fr: k(fr, 4, 8))
        b.text("YOUR BRAND", (752, 882, 1182, 930), M, 800, WHITE, reveal=lambda fr: (0, 866, 1920, 1080),
               shift=lambda fr: (0, -60 * (1 - k(fr, 8, 12))))
        b.rect("Línea", solid(RED), lambda fr: (905 - 153 * k(fr, 18, 12), 860, 905, 864))
        b.rect("Línea 2", solid(RED), lambda fr: (1030, 860, 1030 + 152 * k(fr, 18, 12), 864))
    return title_piece("titulo-brand", "Título grande con líneas rojas", "Big title with red lines", 12369, (967, 891),
                       build)


# --- 26. Six network icons with a search box under each ------------------------------------------------------------
def social_icons():
    D = dur_for(1.4, 2.0)
    t = _p("redes-iconos", "Redes sociales: 6 iconos con buscador", "Social media: 6 icons with search boxes", 12370,
           D, "redes", ["redes", "iconos", "buscador"], thumb=2.0)
    s = P(t, D)
    nets = ("facebook", "instagram", "linkedin", "skype", "twitter", "youtube")
    for i, net in enumerate(nets):
        cx, cy = (316, 960, 1603)[i % 3], (325, 686)[i // 3]
        at = 16 + i
        net_icon(s, net, lambda fr, u, cx=cx, cy=cy, at=at: (cx, cy, 0.4 + 0.6 * k(fr, at, 18), -50 * (1 - k(fr, at, 18)),
                                                             k(fr, at, 3)), size=160)
        x0, y0, x1, y1 = cx - 198, cy + 113, cx + 199, cy + 161
        r = 24
        pts = [(x1 - r, y1), (x0 + r, y1)]
        pts += [(x0 + r - r * math.sin(a / 8 * math.pi), y1 - r + r * math.cos(a / 8 * math.pi)) for a in range(1, 8)]
        pts += [(x0 + r, y0), (x1 - r, y0)]
        pts += [(x1 - r + r * math.sin(a / 8 * math.pi), y0 + r - r * math.cos(a / 8 * math.pi)) for a in range(1, 8)]
        s.outline(f"{SOC_LABEL[net]} (buscador)", pts, 3, WHITE, at=at + 2, n=12)
        s.obj(f"{SOC_LABEL[net]} (lupa)", ring(WHITE, 4), lambda fr, u, x1=x1, y0=y0: (x1 - 44, y0 + 21, 18, 18, 0,
                                                                                       k(fr, at + 12, 4)), kind="ellipse")
        s.obj(f"{SOC_LABEL[net]} (lupa 2)", solid(WHITE), lambda fr, u, x1=x1, y0=y0: (x1 - 32, y0 + 33, 12, 4, 45,
                                                                                       k(fr, at + 12, 4)))
        label = f"{SOC_LABEL[net]}.com/Channel"
        s.say(label, (x0 + 17, y0 + 15, x0 + 17 + 306 * len(label) / 19, y0 + 40), M, 400, WHITE,
              "Título" if i == 0 else f"Red {i + 1}", align="left", reveal=lambda fr, y0=y0, y1=y1: (0, y0, 1920, y1),
              shift=lambda fr, at=at: (0, 40 * (1 - k(fr, at + 14, 8))))
    return t


# --- 27. A transition: red and white stripes close in from both sides, bend as they turn round and slide away ------
def turning_stripes():
    """Copied frame by frame (44.4-45.6 s): the outlines of the stripes on every frame of the reference (STRIPES),
    with the bends they take while they turn."""
    D = 1.25
    t = _p("transicion-franjas", "Transición: franjas rojas y blancas que giran", "Transition: turning red and white "
           "stripes", 12341, D, "transiciones", ["transición", "franjas"], thumb=0.8)
    s = P(t, D, plain=True)

    def polys(text):
        return [[tuple(int(v) for v in pt.split(",")) for pt in poly.split()] for poly in text.split(";") if poly]
    for i, colour, name in ((2, DARK, "Franjas grises"), (0, WHITE, "Franjas blancas"), (1, RED, "Franjas rojas")):
        framed(s, name, colour, {fr: polys(row[i]) for fr, row in STRIPES.items()})
    return t


# --- 29-37. Line icons that loop (45.5-49.7 s): each alone, twice the size, in the middle --------------------------
def icon_piece(id, es, en, order, build, D=3.2):
    t = _p(id, es, en, order, D, "elementos", ["icono", "animado"], thumb=1.2)
    s = P(t, D, plain=True)
    # A seamless loop: no fade in or out, every move repeats a whole number of times in D, so the last frame leads
    # straight into the first.
    fade = lambda fr, u: 1.0  # noqa: E731
    build(s, fade)
    return t


def wave(u, period, phase=0.0):
    return math.sin(2 * math.pi * (u / period + phase))


def ic_arrow():
    def build(s, fade):
        dy = lambda u: -50 * wave(u, 3.2 / 3, 0.25)  # noqa: E731
        s.obj("Flecha", solid(WHITE), lambda fr, u: (960, 450 + dy(u), 24, 300, 0, fade(fr, u)))
        s.obj("Flecha (punta)", solid(WHITE), lambda fr, u: (960, 655 + dy(u), 96, 110, 0, fade(fr, u)),
              path=poly([(0, 0), (50, 22), (100, 0), (50, 100)]))
    return icon_piece("icono-flecha", "Icono: flecha que baja", "Icon: arrow pointing down", 12380, build)


def ic_cursor():
    def build(s, fade):
        clicks = (1.0, 2.3)

        def g(fr, u):
            sc = 0.7 if any(c <= u <= c + 0.15 for c in clicks) else 1.0
            return 960 + 8 * wave(u, 1.6), 540 + 8 * wave(u, 1.6, 0.25), 84 * sc, 140 * sc, -30, fade(fr, u)
        s.obj("Cursor", solid(WHITE), g, path=GLYPH["cursor"])
    return icon_piece("icono-cursor", "Icono: cursor que hace clic", "Icon: clicking pointer", 12381, build)


def ic_like():
    def build(s, fade):
        red_from, red_to = 0.8, 2.5

        def g(fr, u):
            if u < 0.6:
                sc = 1.0
            elif u < red_from:
                sc = 1 - 0.3 * (u - 0.6) / 0.2
            else:
                sc = 1 + 0.15 * math.exp(-6 * (u - red_from)) * math.cos(14 * (u - red_from))
            return 960, 540, 162 * sc, 144 * sc, 0, fade(fr, u)
        s.obj("Me gusta", solid(WHITE), lambda fr, u: (lambda v: v[:5] + ((v[5] if not red_from <= u < red_to else 0),))(
            g(fr, u)), path=GLYPH["like"])
        s.obj("Me gusta (rojo)", solid(RED), lambda fr, u: (lambda v: v[:5] + ((v[5] if red_from <= u < red_to else 0),))(
            g(fr, u)), path=GLYPH["like"])
    return icon_piece("icono-me-gusta", "Icono: me gusta que se vuelve rojo", "Icon: like turning red", 12382, build)


def ic_dots():
    def build(s, fade):
        for i in range(8):
            def g(fr, u, i=i):
                gap = 36 + 9 * math.cos(2 * math.pi * u / 3.2)
                a = math.radians(360 * u / (3.2 / 3) - gap * i)
                d = 24 - 1.6 * i
                return 960 + 120 * math.cos(a), 540 + 120 * math.sin(a), d, d, 0, fade(fr, u)
            s.obj(f"Punto {i + 1}", solid(WHITE), g, kind="ellipse")
    return icon_piece("icono-cargando", "Icono: puntos de carga que giran", "Icon: spinning loading dots", 12383, build)


def ic_bell():
    def build(s, fade):
        red_from, red_to = 1.4, 2.7

        def g(fr, u, red):
            on = red_from <= u < red_to
            rot = 14 * wave(u, 0.35) * (1 if (0.2 < u < 1.2 or red_from < u < 2.2) else 0)
            return 960, 540, 152, 154, rot, fade(fr, u) * (1 if on == red else 0)
        s.obj("Campana", solid(WHITE), lambda fr, u: g(fr, u, False), path=GLYPH["bell"])
        s.obj("Campana (roja)", solid(RED), lambda fr, u: g(fr, u, True), path=GLYPH["bell"])
        for i, (cx, a0, a1) in enumerate(((880, 150, 230), (1040, -50, 30))):
            s.obj(f"Campana (sonido {i + 1})", ring(RED, 7), lambda fr, u, cx=cx: (
                cx, 500, 70, 90, 0, fade(fr, u) * (1 if red_from + 0.1 <= u < red_to else 0)), path=arc(a0, a1))
    return icon_piece("icono-campana", "Icono: campana que suena y se vuelve roja", "Icon: bell ringing red", 12384,
                      build)


def ic_search():
    def build(s, fade):
        x0, y0, x1, y1, r = 700, 507, 1212, 573, 33
        pts = [(x0 + r, y1), (x1 - r, y1)]
        pts += [(x1 - r + r * math.sin(a / 8 * math.pi), y1 - r + r * math.cos(a / 8 * math.pi)) for a in range(1, 8)]
        pts += [(x1 - r, y0), (x0 + r, y0)]
        pts += [(x0 + r - r * math.sin(a / 8 * math.pi), y0 + r - r * math.cos(a / 8 * math.pi)) for a in range(1, 8)]
        c = s.outline("Buscador", pts + [(x0 + r, y1)], 5, "#BBBBBB", at=0, n=30, closed=False)
        out = lambda fr: 1 - k(fr, 3.2 * F - 8, 7)  # noqa: E731 - back to empty for the next loop
        s.fade(c, out)
        s.obj("Lupa", ring(RED, 6), lambda fr, u: (1150, 535, 26, 26, 0, out(fr) * k(fr, 18, 4)), kind="ellipse")
        s.obj("Lupa 2", solid(RED), lambda fr, u: (1166, 551, 16, 6, 45, out(fr) * k(fr, 18, 4)))
    return icon_piece("icono-buscador", "Icono: buscador que se dibuja", "Icon: search box drawing itself", 12385, build)


def burst(s, name, n, colour, fade, period=0.6, r0=20, r1=180, length=36, width=4, delay=0.0, offset=0.0):
    for i in range(n):
        a = 360 * i / n + offset

        def g(fr, u, a=a):
            ph = ((u - delay) / period) % 1.0 if u >= delay else 0.0
            r = r0 + (r1 - r0) * ph
            x, y = rot_pt(960 + r, 540, a)
            return x, y, length * (1 - 0.5 * ph), width, a, fade(fr, u) * (1 - ph) * (1 if u >= delay else 0)
        s.obj(f"{name} {i + 1}", solid(colour), g)


def ic_ticks():
    def build(s, fade):
        burst(s, "Raya", 12, WHITE, fade, period=0.64, r0=20, r1=190, length=40)
    return icon_piece("icono-destello", "Icono: destello de rayas", "Icon: burst of strokes", 12386, build)


def ic_circle():
    def build(s, fade):
        burst(s, "Rayo", 8, "#E23B3B", fade, period=0.64, r0=60, r1=220, length=40, width=5, offset=22.5)
        s.obj("Aro", ring(WHITE, 6), lambda fr, u: (960, 540, 120 * (0.3 + 0.7 * k((((u % 0.64) / 0.64) * F), 0, 6)),
                                                    120 * (0.3 + 0.7 * k((((u % 0.64) / 0.64) * F), 0, 6)), 0,
                                                    fade(fr, u) * (1 - k((((u % 0.64) / 0.64) * F), 22, 6))), kind="ellipse")
        s.obj("Punto", solid(WHITE), lambda fr, u: (960, 540, 22, 22, 0, fade(fr, u) * (1 - k((((u % 0.64) / 0.64) * F), 4, 3))),
              kind="ellipse")
    return icon_piece("icono-aro-blanco", "Icono: aro blanco que estalla", "Icon: white ring burst", 12387, build)


def ic_red_circle():
    def build(s, fade):
        burst(s, "Rayo", 6, RED, fade, period=0.64, r0=70, r1=230, length=36, width=5)
        for i in range(4):
            a = 90 * i + 45

            def g(fr, u, a=a):
                ph = (u % 0.64) / 0.64
                x, y = rot_pt(960 + 90 + 80 * ph, 540, a - 30 * ph)
                return x, y, 24, 24, 0, fade(fr, u) * (1 - ph)
            s.obj(f"Bolita {i + 1}", ring(RED, 4), g, kind="ellipse")
        s.obj("Aro", ring(RED, 7), lambda fr, u: (960, 540, 130 * (0.3 + 0.7 * k((((u % 0.64) / 0.64) * F), 0, 6)),
                                                  130 * (0.3 + 0.7 * k((((u % 0.64) / 0.64) * F), 0, 6)), 0,
                                                  fade(fr, u) * (1 - k((((u % 0.64) / 0.64) * F), 22, 6))), kind="ellipse")
    return icon_piece("icono-aro-rojo", "Icono: aro rojo que estalla", "Icon: red ring burst", 12388, build)


TEMPLATES = [opening, watch_page, bar_counts, two_cards, card_page, bar_likes, bar_channel, bar_simple, bar_bell,
             next_wave, channel_card, ring_channel, next_bar, diagonal_bars, social_bars,
             t_new_project, t_animation, t_rendering, t_your_channel, t_simple, t_clean, t_motion_design, t_just_edit,
             t_best, t_brand, social_icons, turning_stripes, ic_arrow, ic_cursor, ic_like, ic_dots, ic_bell, ic_search,
             ic_ticks, ic_circle, ic_red_circle]
