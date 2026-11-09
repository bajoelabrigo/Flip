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
    s.obj(name, solid(red), lambda fr, u: (lambda g: (g[0], g[1], w * g[2], h * g[2], g[3], g[4]))(geom(fr, u)),
          radius=h * radius, base=(w, h))

    def tg(fr, u):
        cx, cy, sc, rot, op = geom(fr, u)
        ox, oy = rot_pt(cx + w * 0.03 * sc, cy, rot, cx, cy)
        return ox, oy, w * 0.27 * sc, h * 0.43 * sc, rot + (tri_rot(fr) if tri_rot else 0.0), op
    s.obj(f"{name} (play)", solid(tri), tg, path=TRIANGLE)


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

    size = lambda fr: min(1.0, max(0.0, (fr - 3) / 50)) ** 0.8  # noqa: E731
    if end_shrink:
        zoom = lambda fr: 1 - 0.2 * k(fr, 69, 60) - 0.8 * k(fr, 129, 21)  # noqa: E731
    else:
        zoom = lambda fr: 1.0  # noqa: E731
    shift = 960 - logo_cx
    lx = lambda fr: 960 - shift * k(fr, 41, 19)  # noqa: E731

    def logo(fr, u):
        sc = size(fr) * zoom(fr)
        x = 960 + (lx(fr) - 960) * zoom(fr)
        return x, 540, sc, -720 * (1 - k(fr, 5, 28)), 1.0 if fr >= 5 else 0.0
    yt_logo(s, "Logo", logo, w=logo_w, h=logo_w * 0.716, tri_rot=lambda fr: -990 * (1 - k(fr, 40, 22)) if fr >= 33 else 0.0)

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


# --- 14. A transition: rounded red, white and grey bars shoot in on the diagonal, shift, and slide away -----------
def diagonal_bars():
    D = 1.25
    t = _p("transicion-diagonal", "Transición: barras diagonales roja, blanca y gris", "Transition: red, white and grey "
           "diagonal bars", 12340, D, "transiciones", ["transición", "diagonal"], thumb=0.5)
    s = P(t, D, plain=True)
    q = 6 / math.sqrt(2)  # tile «x - y» units to px across the bars
    P0 = 70  # x - y at the centre of the tile
    OUT, IN = -3600.0, 3600.0

    def edges(a, b):  # a bar between two «x - y» lines
        return (lambda fr: ((a(fr) if callable(a) else a) + (b(fr) if callable(b) else b) - 2 * P0) / 2 * -q,
                lambda fr: abs((b(fr) if callable(b) else b) - (a(fr) if callable(a) else a)) * q)
    drift = lambda fr: -25 * k(fr, 12, 12)  # noqa: E731
    specs = [  # name, colour, left edge, right edge, enter (frame, length), leave (frame, length)
        ("Barra roja (fondo)", RED, -600, lambda fr: -70 + drift(fr), (2, 7), (27, 9)),
        ("Barra gris", DARK, lambda fr: -70 + drift(fr), lambda fr: 90 + drift(fr), (0, 8), (24, 10)),
        ("Barra blanca", WHITE, lambda fr: 90 + drift(fr), lambda fr: 155 + drift(fr) - 25 * k(fr, 18, 4), (2, 8),
         (22, 10)),
        ("Barra roja", RED, lambda fr: 155 + drift(fr) - 25 * k(fr, 18, 4), lambda fr: 205 + 115 * k(fr, 17, 5),
         (0, 7), (25, 10)),
        ("Barra blanca 2", WHITE, lambda fr: 205 + 115 * k(fr, 17, 5), 900, (3, 8), (28, 8)),
        ("Línea gris", DARK, lambda fr: 60 - 10 * k(fr, 19, 4), lambda fr: 62 + 18 * k(fr, 19, 4), (19, 3), (26, 8)),
        ("Línea blanca", WHITE, lambda fr: 112 - 6 * k(fr, 15, 4), lambda fr: 113 + 6 * k(fr, 15, 4), (15, 3), (23, 8)),
    ]
    for name, colour, a, b, (e0, en), (l0, ln) in specs:
        p_of, w_of = edges(a, b)
        along = slide_keys([(e0, OUT), (e0 + en, 0.0), (l0, 0.0), (l0 + ln, IN)])
        band(s, name, colour, p_of, w_of, along, angle=45.0, round_=name in ("Barra gris", "Barra roja", "Barra blanca"))
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


# --- 27. A transition: red and white stripes close in from both sides, turn round and slide away -----------------
def turning_stripes():
    D = 1.25
    t = _p("transicion-franjas", "Transición: franjas rojas y blancas que giran", "Transition: turning red and white "
           "stripes", 12341, D, "transiciones", ["transición", "franjas"], thumb=0.6)
    s = P(t, D, plain=True)
    ang = lambda fr: 100 - 125 * k(fr, 12, 18)  # noqa: E731
    specs = [("Franja oscura", DARK, (1500, 900), 900, (15, 8), (26, 10)),
             ("Franja roja", RED, (-1500, -700), 600, (0, 10), (24, 10)),
             ("Franja blanca", WHITE, (-1500, -200), 420, (1, 11), (25, 10)),
             ("Franja blanca 2", WHITE, (1500, 200), 420, (1, 11), (27, 9)),
             ("Franja roja 2", RED, (1500, 700), 600, (0, 10), (28, 9))]
    for name, colour, (p0, p1), w, (e0, en), (l0, ln) in specs:
        def p_of(fr, p0=p0, p1=p1, e0=e0, en=en, l0=l0, ln=ln):
            return p0 + (p1 - p0) * k(fr, e0, en) - 2600 * k(fr, l0, ln)
        g = lambda fr, u, p_of=p_of, w=w: (960 + p_of(fr) * math.sin(math.radians(ang(fr))),  # noqa: E731
                                          540 - p_of(fr) * math.cos(math.radians(ang(fr))), 5000, w, ang(fr), 1)
        s.obj(name, solid(colour), g)
    return t


# --- 29-37. Line icons that loop (45.5-49.7 s): each alone, twice the size, in the middle --------------------------
def icon_piece(id, es, en, order, build, D=3.2):
    t = _p(id, es, en, order, D, "elementos", ["icono", "animado"], thumb=1.2)
    s = P(t, D, plain=True)
    fade = lambda fr, u: k(fr, 0, 5) * (1 - k(fr, D * F - 6, 6))  # noqa: E731
    build(s, fade)
    return t


def wave(u, period, phase=0.0):
    return math.sin(2 * math.pi * (u / period + phase))


def ic_arrow():
    def build(s, fade):
        dy = lambda u: -50 * wave(u, 1.2, 0.25)  # noqa: E731
        s.obj("Flecha", solid(WHITE), lambda fr, u: (960, 450 + dy(u), 24, 300, 0, fade(fr, u)))
        s.obj("Flecha (punta)", solid(WHITE), lambda fr, u: (960, 655 + dy(u), 96, 110, 0, fade(fr, u)),
              path=poly([(0, 0), (50, 22), (100, 0), (50, 100)]))
    return icon_piece("icono-flecha", "Icono: flecha que baja", "Icon: arrow pointing down", 12380, build)


def ic_cursor():
    def build(s, fade):
        clicks = (1.0, 2.3)

        def g(fr, u):
            sc = 0.7 if any(c <= u <= c + 0.15 for c in clicks) else 1.0
            return 960 + 8 * wave(u, 1.3), 540 + 8 * wave(u, 1.3, 0.25), 84 * sc, 140 * sc, -30, fade(fr, u)
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
                gap = 45 - 18 * k(u * F, 6, 24)
                a = math.radians(360 * u / 1.1 - gap * i)
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
        s.fade(c, lambda fr: fade(fr, fr / F))
        s.obj("Lupa", ring(RED, 6), lambda fr, u: (1150, 535, 26, 26, 0, fade(fr, u) * k(fr, 18, 4)), kind="ellipse")
        s.obj("Lupa 2", solid(RED), lambda fr, u: (1166, 551, 16, 6, 45, fade(fr, u) * k(fr, 18, 4)))
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
        burst(s, "Raya", 12, WHITE, fade, period=0.7, r0=20, r1=190, length=40)
    return icon_piece("icono-destello", "Icono: destello de rayas", "Icon: burst of strokes", 12386, build)


def ic_circle():
    def build(s, fade):
        burst(s, "Rayo", 8, "#E23B3B", fade, period=1.0, r0=60, r1=220, length=40, width=5, offset=22.5)
        s.obj("Aro", ring(WHITE, 6), lambda fr, u: (960, 540, 120 * (0.3 + 0.7 * k(((u % 1.0) * F), 0, 6)),
                                                    120 * (0.3 + 0.7 * k(((u % 1.0) * F), 0, 6)), 0,
                                                    fade(fr, u) * (1 - k(((u % 1.0) * F), 22, 6))), kind="ellipse")
        s.obj("Punto", solid(WHITE), lambda fr, u: (960, 540, 22, 22, 0, fade(fr, u) * (1 - k(((u % 1.0) * F), 4, 3))),
              kind="ellipse")
    return icon_piece("icono-aro-blanco", "Icono: aro blanco que estalla", "Icon: white ring burst", 12387, build)


def ic_red_circle():
    def build(s, fade):
        burst(s, "Rayo", 6, RED, fade, period=1.0, r0=70, r1=230, length=36, width=5)
        for i in range(4):
            a = 90 * i + 45

            def g(fr, u, a=a):
                ph = (u % 1.0)
                x, y = rot_pt(960 + 90 + 80 * ph, 540, a - 30 * ph)
                return x, y, 24, 24, 0, fade(fr, u) * (1 - ph)
            s.obj(f"Bolita {i + 1}", ring(RED, 4), g, kind="ellipse")
        s.obj("Aro", ring(RED, 7), lambda fr, u: (960, 540, 130 * (0.3 + 0.7 * k(((u % 1.0) * F), 0, 6)),
                                                  130 * (0.3 + 0.7 * k(((u % 1.0) * F), 0, 6)), 0,
                                                  fade(fr, u) * (1 - k(((u % 1.0) * F), 22, 6))), kind="ellipse")
    return icon_piece("icono-aro-rojo", "Icono: aro rojo que estalla", "Icon: red ring burst", 12388, build)


TEMPLATES = [opening, watch_page, bar_counts, two_cards, card_page, bar_likes, bar_channel, bar_simple, bar_bell,
             next_wave, channel_card, ring_channel, next_bar, diagonal_bars, social_bars,
             t_new_project, t_animation, t_rendering, t_your_channel, t_simple, t_clean, t_motion_design, t_just_edit,
             t_best, t_brand, social_icons, turning_stripes, ic_arrow, ic_cursor, ic_like, ic_dots, ic_bell, ic_search,
             ic_ticks, ic_circle, ic_red_circle]
