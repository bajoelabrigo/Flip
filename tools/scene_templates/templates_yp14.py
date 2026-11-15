"""Video 34019110.mp4 as Kit de YouTube Stock templates (yp14-*). See docs/plan-youtube-pack-2.md.

«YouTube Buttons 80+ elements» (1920×1080 at 25 fps): clean white cards with soft shadows, serif names (Roboto
Slab), Lato for the rest, YouTube red. The reference shows its elements four at a time in a 2×2 grid; each quarter
(816×459 px of the source) is one element laid out here at 1920×1080 (×2.353). Every piece was studied on 10 fps
sheets numbered with the source's frames; frames here are the source's (25 fps): `P.frame` = u × 25. Study notes
and the element list in tienda/plantillas/estudio-34019110/NOTAS.md.

Over a transparent frame (they sit on the user's video); photos are slots, avatars round slots; the green leaf of
the reference (a marketplace logo) is the `logo-flip` slot.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from scene import keys
from templates_tit_c import k
from templates_tit_e import solid
from templates_tit_h import S, fill, lin, ring, rot_pt, shadow
from templates_yp3 import BELL, HAND, RINGS, THUMB

WHITE, INK, GREY_TXT = "#FFFFFF", "#222222", "#555555"
RED = "#CC0000"
PILL_GREY = "#ECECEC"
BG = "#F7F7F9"
SLAB, LATO = "Roboto Slab", "Lato"
for _w, _f in ((700, "Bold"), (600, "SemiBold"), (500, "Medium"), (400, "Regular"), (800, "ExtraBold")):
    f6._FILES[(SLAB, _w)] = f"fonts.extra/fonts/robotoslab/RobotoSlab-{_f}.ttf"
for _w, _f in ((400, "Regular"), (700, "Bold"), (900, "Black")):
    f6._FILES[(LATO, _w)] = f"fonts.basic/fonts/lato/Lato-{_f}.ttf"

# --- glyphs (0..100 boxes) ------------------------------------------------------------------------------------------
SHARE = ("M 58 6 L 100 44 L 58 82 L 58 60 Q 22 58 2 92 Q 6 44 58 30 Z")
TICK = "M 8 52 L 38 80 L 92 18"
DOWNLOAD = "M 50 4 L 50 70 M 22 44 L 50 72 L 78 44 M 10 94 L 90 94"
SAVE = "M 8 8 L 92 8 L 92 92 L 8 92 Z M 50 28 L 50 72 M 28 50 L 72 50"
PLAYTRI = "M 0 0 L 100 50 L 0 100 Z"


def rounded_path(w, h, r):
    """A rounded rectangle on the 0..100 box of a w × h rect (corner radius r px), for path masks."""
    rx, ry = min(50.0, r / w * 100), min(50.0, r / h * 100)
    c = 0.4477  # 1 - kappa
    return (f"M {rx:.3f} 0 L {100 - rx:.3f} 0 C {100 - rx * c:.3f} 0 100 {ry * c:.3f} 100 {ry:.3f} "
            f"L 100 {100 - ry:.3f} C 100 {100 - ry * c:.3f} {100 - rx * c:.3f} 100 {100 - rx:.3f} 100 "
            f"L {rx:.3f} 100 C {rx * c:.3f} 100 0 {100 - ry * c:.3f} 0 {100 - ry:.3f} "
            f"L 0 {ry:.3f} C 0 {ry * c:.3f} {rx * c:.3f} 0 {rx:.3f} 0 Z")


def stroke(colour, width, cap="round"):
    return [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
            {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "center",
             "opacity": 1.0, "cap": cap, "join": "round",
             "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}]


def filled_line(fill_colour, line, width):
    return [fill(fill_colour),
            {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "center",
             "opacity": 1.0, "join": "round", "paint": {"kind": "solid", "color": "#ff" + line.lstrip("#").lower()}}]


def card_layers(colour=WHITE, alpha=0.16, blur=60, dy=22):
    return [shadow("#2A2F4A", 0, dy, blur, alpha), fill(colour)]


def on(fr, at):
    return 1.0 if fr >= at else 0.0


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


def pop(fr, at, n=5, over=0.15):
    """0 → 1 with a small overshoot from frame at over n frames."""
    if fr <= at:
        return 0.0
    q = (fr - at) / n
    if q >= 1.6:
        return 1.0
    if q <= 1.0:
        return k(fr, at, n) * (1 + over * q)
    return 1 + over * (1 - (q - 1) / 0.6)


class Rig:
    """A group's pose per frame: fn(fr) = (cx, cy, scale, rot, op). Points are given on screen where they sit at
    `rest` (the frame the reference was measured on) and follow the group from there."""

    def __init__(self, fn, rest):
        self.fn = fn
        self.rest = fn(rest)

    def __call__(self, fr):
        return self.fn(fr)

    def loc(self, x, y):
        cx, cy, sc, rot, _ = self.rest
        ux, uy = rot_pt(x, y, -rot, cx, cy)
        return (ux - cx) / sc, (uy - cy) / sc

    def scr(self, fr, lx, ly):
        cx, cy, sc, rot, _ = self.fn(fr)
        return rot_pt(cx + lx * sc, cy + ly * sc, rot, cx, cy)

    def m(self, fr):
        return self.fn(fr)[2] / self.rest[2]


STILL = Rig(lambda fr: (960.0, 540.0, 1.0, 0.0, 1.0), 0)


class P(S):
    """A piece played forwards in the source's frames (25 fps); each element codes its own way out."""

    def __init__(self, t, dur):
        S.__init__(self, t, dur)
        t.background = BG

    def frame(self, u):
        return u * 25.0

    def typed(self, clip, at, stagger=0.06, duration=0.05, preset="typewriter", order="forward", unit="character"):
        S.typed(self, clip, at * 30000 / 1001 / 25.0, stagger, duration, preset, order, unit)
        clip["textStyle"]["animation"]["out"].pop("delayUs", None)
        clip["textStyle"]["animation"].pop("out", None)

    # --- shapes and words on a rig ----------------------------------------------------------------------------------
    def part(self, name, layers, rig, x, y, w, h, op=None, size=None, wmul=None, hmul=None, turn=None, **kw):
        """A shape centred at (x, y) on screen at rest, w × h at rest; op / size / wmul / hmul / turn(fr) animate
        it on top of the rig."""
        lx, ly = rig.loc(x, y)

        def g(fr, u):
            cx, cy, sc, rot, rop = rig(fr)
            px, py = rig.scr(fr, lx, ly)
            mm = rig.m(fr) * (size(fr) if size else 1.0)
            return (px, py, w * mm * (wmul(fr) if wmul else 1.0), h * mm * (hmul(fr) if hmul else 1.0),
                    rot + (turn(fr) if turn else 0.0), rop * (op(fr) if op else 1.0))
        kw.setdefault("base", (w, h))
        return self.obj(name, layers, g, **kw)

    def left_bar(self, name, layers, rig, x0, y, w, h, frac, op=None, **kw):
        """A bar whose left end stays at (x0, y) (rest, screen) and whose length is w × frac(fr)."""
        lx, ly = rig.loc(x0, y)
        rot0 = rig.rest[3]

        def g(fr, u):
            cx, cy, sc, rot, rop = rig(fr)
            mm = rig.m(fr)
            ww = w * frac(fr)
            px, py = rig.scr(fr, lx + ww / 2 * math.cos(math.radians(0)) / rig.rest[2], ly)
            return px, py, ww * mm, h * mm, rot, rop * (op(fr) if op else 1.0)
        del rot0
        kw.setdefault("base", (w, h))
        return self.obj(name, layers, g, **kw)

    def icon(self, name, path, layers, rig, x, y, h, aspect=1.0, even_odd=False, **kw):
        c = self.part(name, layers, rig, x, y, h * aspect, h, path=path, **kw)
        c["shapeStyle"]["customEvenOdd"] = even_odd
        return c

    def word(self, content, rig, x, y, cap, family, weight, colour, name="Texto", align="left", op=None,
             size=None, slide=None, editable=True, x1=None, reveal=None):
        """A line whose capitals are `cap` px tall at rest, anchored at (x, y) on screen at rest (its left edge,
        centre or right edge per align; y = middle of the capitals). slide(fr) = (dx, dy) along the group."""
        ink = {"left": (x, y - cap / 2, x + 6000, y + cap / 2),
               "center": (x - 3000, y - cap / 2, x + 3000, y + cap / 2),
               "right": (x - 6000, y - cap / 2, x, y + cap / 2)}[align]
        if x1 is not None:  # never wider than the reference's ink (x .. x1)
            ink = {"left": (x, ink[1], x1, ink[3]), "center": (2 * x - x1, ink[1], x1, ink[3]),
                   "right": (x1, ink[1], x, ink[3])}[align]
        clip = self.text(content, ink, family, weight, colour, name, align=align, editable=editable, reveal=reveal)
        bx = clip["x"]["keyframes"][0]["value"] + clip["width"]["keyframes"][0]["value"] / 2
        by = clip["y"]["keyframes"][0]["value"] + clip["height"]["keyframes"][0]["value"] / 2
        lx, ly = rig.loc(x, y)
        rot0 = rig.rest[3]
        vx, vy = bx - x, by - y  # box centre from the anchor, unturned, at rest scale

        def g(fr, u):
            cx, cy, sc, rot, rop = rig(fr)
            mm = rig.m(fr) * (size(fr) if size else 1.0)
            sx, sy = slide(fr) if slide else (0.0, 0.0)
            ax, ay = rig.scr(fr, lx + sx / rig.rest[2], ly + sy / rig.rest[2])
            ox, oy = rot_pt(vx * mm, vy * mm, rot, 0, 0)
            return ax + ox - bx, ay + oy - by, mm, rot, rop * (op(fr) if op else 1.0)
        del rot0
        self.tmove(clip, g)
        return clip

    def photo(self, sample, rig, x, y, w, h, label="Tu video", name="Foto", op=None, round_=False, reuse=None,
              corner=0.0, **extra):
        """A photo slot centred at (x, y) at rest, w × h, turning with the rig (round_: an avatar)."""
        lx, ly = rig.loc(x, y)
        g = []
        for u, fr in self.each():
            cx, cy, sc, rot, rop = rig(fr)
            px, py = rig.scr(fr, lx, ly)
            mm = rig.m(fr)
            g.append((u, (px, py, w * mm, h * mm, rot, rop * (op(fr) if op else 1.0))))
        bw, bh = max(1.0, max(v[2] for _, v in g)), max(1.0, max(v[3] for _, v in g))
        box = Box(960 - bw / 2, 540 - bh / 2, bw, bh)
        motion = [(u, {"sx": max(1e-4, v[2] / bw), "sy": max(1e-4, v[3] / bh), "dx": v[0] - 960, "dy": v[1] - 540},
                   "linear") for u, v in g]
        track = self.t.track("video", name)
        clip = self.t.photo(track, sample, 0.0, self.dur, box, motion, label=label, reuse=reuse, **extra)
        if any(abs(v[4]) > 1e-6 for _, v in g):
            clip["rotation"] = keys([(u, round(v[4], 3), "linear") for u, v in g])
        if any(v[5] < 0.999 for _, v in g):
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, v[5])), 4), "linear") for u, v in g])
        if round_:
            self.t.mask(track, clip, "ellipse")
        elif corner:
            self.t.mask(track, clip, "path", pathData=rounded_path(w, h, corner))
        return clip

    def window(self, sample, box, rect, label="Tu video", name="Foto", op=None):
        """A still photo laid out in box (x0, y0, x1, y1, cover-cropped by the engine) seen only through
        rect(fr) = (x0, y0, x1, y1) on screen."""
        from llt_motion import mask_track
        x0, y0, x1, y1 = box
        w = max(x1 - x0, (y1 - y0) * 16 / 9)  # a 16:9 picture that covers the window
        h = w * 9 / 16
        b = Box((x0 + x1) / 2 - w / 2, (y0 + y1) / 2 - h / 2, w, h)
        clip = self.t.photo(self.t.track("video", name), sample, 0.0, self.dur, b, None, label=label)
        mask_track(self.t, clip, b, lambda u: rect(self.frame(u)), self.dur)
        if op:
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, op(fr))), 4), "linear") for u, fr in self.each()])
        return clip

    def logo(self, rig, x, y, d, op=None, size=None):
        """The channel's logo (the logo-flip slot) on a white disc with a soft shadow."""
        self.part("Logo (disco)", [shadow("#2A2F4A", 0, 10, 30, 0.15), fill(WHITE)], rig, x, y, d, d, kind="ellipse",
                  op=op, size=size)
        lop = (lambda fr: (op(fr) if op else 1.0) * min(1.0, max(0.0, (size(fr) if size else 1.0) * 2 - 0.4)))
        return self.photo("logo-flip", rig, x, y, d * 0.5, d * 0.5, label="Tu logo", name="Logo", op=lop,
                          brandRole="logo")

    def avatar(self, sample, rig, x, y, d, op=None, label="Tu foto de perfil", ring_=None):
        if ring_:
            self.part("Foto (aro)", solid(ring_), rig, x, y, d + 8, d + 8, op=op, kind="ellipse")
        return self.photo(sample, rig, x, y, d, d, label=label, name="Foto de perfil", op=op, round_=True)

    def cursor(self, at, name="Cursor", h=78):
        """The outline hand; at(fr) = (x, y, press 0..1, op) puts its fingertip."""
        w = h * 0.86

        def g(fr, u):
            x, y, press, op = at(fr)
            sc = 1 - 0.15 * press
            return x - w * sc * 0.3 + w * sc / 2, y + h * sc / 2, w * sc, h * sc, 0.0, op
        return self.obj(name, filled_line(WHITE, INK, max(2.5, h * 0.045)), g, path=HAND)

    def clicks(self, path, presses, enter, leave, h=78):
        """A cursor along path(fr) pressing at the given frames, showing from `enter` to `leave` (frames)."""
        def at(fr):
            press = max([math.sin(math.pi * lin(fr, p - 2, 5)) for p in presses] or [0.0])
            return (*path(fr), press, k(fr, enter, 3) * (1 - k(fr, leave, 3)))
        return self.cursor(at, h=h)

    # --- YouTube bits ---------------------------------------------------------------------------------------------
    def check(self, rig, x, y, d, op=None, colour="#606060"):
        self.part("Verificado", solid(colour), rig, x, y, d, d, op=op, kind="ellipse")
        self.part("Verificado (marca)", stroke(WHITE, d * 0.13), rig, x, y + d * 0.02, d * 0.5, d * 0.4, op=op,
                  path=TICK)

    def subscribe(self, rig, x, y, w, h, grow, click, cap=None, op=None, red=RED, label="SUBSCRIBE",
                  done="SUBSCRIBED", weight=400, done_grey=PILL_GREY, done_ink="#333333"):
        """The red pill that opens from its centre (grow(fr) 0..1) and turns grey «SUBSCRIBED» at frame click."""
        cap = cap or h * 0.4
        o = (lambda fr: op(fr)) if op else (lambda fr: 1.0)
        self.part("Suscribirse (gris)", solid(done_grey), rig, x, y, w, h, radius=h / 2,
                  op=lambda fr: o(fr) * on(fr, click), wmul=grow)
        self.part("Suscribirse", solid(red), rig, x, y, w, h, radius=h / 2,
                  op=lambda fr: o(fr) * (1 - on(fr, click)), wmul=grow)
        self.word(label, rig, x, y, cap, LATO, weight, WHITE, "Botón", align="center",
                  op=lambda fr: o(fr) * (1 - on(fr, click)) * k(fr, grow_at(grow), 4))
        self.word(done, rig, x, y, cap, LATO, 400, done_ink, "Botón (suscrito)", align="center",
                  op=lambda fr: o(fr) * on(fr, click))

    def thumb(self, rig, x, y, h, click=None, colour=INK, op=None, down=False, outline_w=None, name="Me gusta",
              solid_from_start=False):
        """Thumb up (down: the dislike one) in outline; filled from frame click (or always, solid_from_start)."""
        turn = (lambda fr: 180.0) if down else None
        o = op or (lambda fr: 1.0)
        lw = outline_w or max(2.0, h * 0.07)
        if solid_from_start:
            return self.icon(name, THUMB, solid(colour), rig, x, y, h, aspect=1.0, op=o, turn=turn)
        self.icon(name, THUMB, stroke(colour, lw), rig, x, y, h, aspect=1.0,
                  op=(lambda fr: o(fr) * (1 - on(fr, click))) if click is not None else o, turn=turn)
        if click is not None:
            self.icon(name + " (lleno)", THUMB, solid(colour), rig, x, y, h, aspect=1.0,
                      op=lambda fr: o(fr) * on(fr, click), turn=turn,
                      size=lambda fr: 1 + 0.18 * math.sin(math.pi * lin(fr, click, 6)))

    def bell(self, rig, x, y, h, click=None, colour=INK, op=None, filled=False, rings_always=False):
        o = op or (lambda fr: 1.0)
        lw = max(2.0, h * 0.07)
        sway = (lambda fr: 16 * math.sin(2 * math.pi * lin(fr, click, 20) * 2) * (1 - lin(fr, click, 20))) \
            if click is not None else None
        if not filled:
            self.icon("Campana", BELL, stroke(colour, lw), rig, x, y, h, aspect=0.92,
                      op=(lambda fr: o(fr) * (1 - on(fr, click))) if click is not None else o)
        if filled or click is not None:
            self.icon("Campana (llena)", BELL, solid(colour), rig, x, y, h, aspect=0.92,
                      op=(lambda fr: o(fr) * on(fr, click)) if click is not None else o, turn=sway)
            self.icon("Campana (ondas)", RINGS, stroke(colour, lw * 0.8), rig, x, y - h * 0.12, h * 0.8, aspect=1.7,
                      op=(lambda fr: o(fr) * k(fr, click, 3)) if click is not None else
                      ((lambda fr: o(fr)) if rings_always else (lambda fr: 0.0)),
                      size=(lambda fr: 0.85 + 0.15 * k(fr, click, 6)) if click is not None else None)

    def share(self, rig, x, y, h, colour=INK, op=None, outline=True, name="Compartir"):
        lw = max(2.0, h * 0.07)
        return self.icon(name, SHARE, stroke(colour, lw) if outline else solid(colour), rig, x, y, h, aspect=1.15,
                         op=op)

    def play(self, rig, x, y, w, h, op=None, red="#FF0000", tri=WHITE, size=None):
        """A YouTube play button (red rounded box, white triangle) centred at (x, y) at rest."""
        self.part("Play", solid(red), rig, x, y, w, h, op=op, radius=h * 0.28, size=size)
        self.part("Play (triángulo)", solid(tri), rig, x + w * 0.03, y, w * 0.24, h * 0.36, op=op, path=PLAYTRI,
                  size=size)

    def share_click(self, rig, x, y, h, click, op=None):
        """The share arrow in outline, filled from frame click."""
        o = op or (lambda fr: 1.0)
        self.share(rig, x, y, h, op=lambda fr: o(fr) * (1 - on(fr, click)))
        self.share(rig, x, y, h, op=lambda fr: o(fr) * on(fr, click), outline=False, name="Compartir (lleno)")

    def play_icon(self, rig, x, y, h, click=None, op=None, colour=INK):
        """The small play icon (rounded box with a triangle), in outline until click, then filled."""
        o = op or (lambda fr: 1.0)
        w = h * 1.38
        if click is not None:
            self.part("Play (contorno)", stroke(colour, max(2.0, h * 0.08)), rig, x, y, w, h, radius=h * 0.25,
                      op=lambda fr: o(fr) * (1 - on(fr, click)))
            self.part("Play (contorno, triángulo)", stroke(colour, max(2.0, h * 0.07)), rig, x + w * 0.03, y,
                      w * 0.22, h * 0.36, path=PLAYTRI, op=lambda fr: o(fr) * (1 - on(fr, click)))
        lit = (lambda fr: o(fr) * on(fr, click)) if click is not None else o
        sz = (lambda fr: 1 + 0.15 * math.sin(math.pi * lin(fr, click, 6))) if click is not None else None
        self.part("Play (icono)", solid(colour), rig, x, y, w, h, radius=h * 0.25, op=lit, size=sz)
        self.part("Play (icono, triángulo)", solid(WHITE), rig, x + w * 0.03, y, w * 0.22, h * 0.36, path=PLAYTRI,
                  op=lit, size=sz)

    def progress(self, rig, x0, y, length, h, frac, op=None):
        self.left_bar("Progreso", solid(WHITE), rig, x0, y, length, h, lambda fr: 1.0, op=op, radius=h / 2)
        self.left_bar("Progreso (rojo)", solid("#FF0000"), rig, x0, y, length, h * 1.15, frac, op=op,
                      radius=h * 0.6)


QO = {"TL": (124, 61), "TR": (980, 61), "BL": (124, 560), "BR": (980, 560)}
S16 = 1.2 * 1920 / 816  # a length on the 1600 px still → template px


def Q(quad, x, y):
    """A point read on the 1600 px still of the grid → the template's frame."""
    ox, oy = QO[quad]
    return (x * 1.2 - ox) * 1920 / 816, (y * 1.2 - oy) * 1920 / 816


def G(quad, x, y):
    """A point read on the 2×2 study image (each quarter cropped at 300..1700 × 150..950 of the template and
    shown at 0.91) → the template's frame."""
    ox = 1274 if quad in ("TR", "BR") else 0
    oy = 728 if quad in ("BL", "BR") else 0
    return (x - ox) / 0.91 + 300, (y - oy) / 0.91 + 150


def GB(quad, x0, y0, x1, y1, r=40):
    a, b = G(quad, x0, y0), G(quad, x1, y1)
    return (a[0], a[1], b[0], b[1], r)


def L(v):
    """A length read on the 2×2 study image → template px."""
    return v / 0.91


def grow_at(grow):
    """The first frame where grow() passes 0.6 (for the text inside a pill)."""
    for f in range(0, 400):
        if grow(f) > 0.6:
            return f
    return 0


def _t(id, es, en, order, dur, section="redes", tags=(), thumb=None):
    return wide(f"yp14-{id}", es, en, "ytkit", dur, order=order,
                tags=[f"kit:{section}", "youtube"] + list(tags),
                thumb_at=thumb if thumb is not None else round(dur * 0.55, 1))


# --- G1 (source 16.0–21.3): a full-frame photo shrinks into a channel card, the cursor clicks; it grows back -------
PHOTO_W, PHOTO_H = 1060.0, 598.0


def card_rig(cx, cy, rot, d0=7, n=13, out_at=105, out_n=12):
    """The photo's centre: full frame (1920 wide) until d0, into (cx, cy, rot) over n frames; back from out_at."""
    full = 1920.0 / PHOTO_W

    def fn(fr):
        q = k(fr, d0, n) * (1 - k(fr, out_at, out_n))
        return (960 + (cx - 960) * q, 540 + (cy - 540) * q, full + (1 - full) * q, rot * q, min(1.0, fr / 3.0))
    return Rig(fn, 60)


def photo_card(id, es, en, order, sample, rig_at, margin, radius, bar_h, items, clicks, cursor_path, enter, leave,
               dur=5.2, progress=None, tags=()):
    t = _t(id, es, en, order, dur, "redes", ["tarjeta", "canal", "suscribirse", "foto"] + list(tags))
    s = P(t, dur)
    cx, cy, rot = rig_at
    rig = card_rig(cx, cy, rot, out_at=dur * 25 - 22)
    # the card: photo + white bar below (+ a white margin round both)
    lx, ly = 0.0, (bar_h) / 2
    ccx, ccy = rot_pt(cx + lx, cy + ly, rot, cx, cy)
    s.part("Tarjeta", card_layers(), rig, ccx, ccy, PHOTO_W + 2 * margin, PHOTO_H + bar_h + 2 * margin,
           radius=radius, op=lambda fr: k(fr, 8, 4))
    s.photo(sample, rig, cx, cy, PHOTO_W, PHOTO_H, label="Tu video")
    if progress:
        x0, y0, length, frac = progress
        s.progress(rig, x0, y0, length, 12, frac, op=lambda fr: k(fr, 10, 4))
    for item in items:
        item(s, rig)
    if cursor_path:
        s.clicks(cursor_path, clicks, enter, leave)
    return t


# The bar items, measured on the reference's held frame (template px). Each returns item(s, rig).
def it_avatar(sample, x, y, d, at=12):
    return lambda s, rig: s.avatar(sample, rig, x, y, d, op=lambda fr: k(fr, at, 5))


def it_name(content, x, y, cap=36, at=13, check=None, x1=None):
    def f(s, rig):
        end = x1 if x1 is not None else (check[0] - cap * 0.75 if check else None)
        s.word(content, rig, x, y, cap, SLAB, 700, INK, "Canal", op=lambda fr: k(fr, at, 5),
               slide=lambda fr: (-50 * (1 - k(fr, at, 8)), 0), x1=end)
        if check:
            s.check(rig, check[0], check[1], cap * 0.8, op=lambda fr: k(fr, at + 4, 4))
    return f


def it_subs(content, x, y, cap=26, at=15, count_from=100, secs=1.3):
    def f(s, rig):
        c = s.word(content, rig, x, y, cap, LATO, 400, "#333333", "Suscriptores", op=lambda fr: k(fr, at, 5))
        c["textStyle"].update(counter=True, counterFrom=count_from, counterSeconds=secs, counterCurve="easeOut")
    return f


def it_sub(x, y, w, h, click, at=17, cap=26):
    return lambda s, rig: s.subscribe(rig, x, y, w, h, lambda fr: k(fr, at, 8), click, cap=cap)


def it_bell(x, y, h, click=None, at=23):
    return lambda s, rig: s.bell(rig, x, y, h, click, op=lambda fr: pop(fr, at, 5))


def it_like(x, y, h, click=None, at=21, solid_=False, count=None):
    def f(s, rig):
        s.thumb(rig, x, y, h, click, op=lambda fr: pop(fr, at, 5), solid_from_start=solid_)
        if count:
            c = s.word(count[0], rig, count[1], y, 24, LATO, 400, "#333333", "Me gusta (número)",
                       op=lambda fr: k(fr, at + 2, 5))
            c["textStyle"].update(counter=True, counterFrom=0, counterSeconds=1.4, counterCurve="easeOut")
    return f


def it_dislike(x, y, h, click=None, at=22):
    return lambda s, rig: s.thumb(rig, x, y, h, click, op=lambda fr: pop(fr, at, 5), down=True, name="No me gusta")


def lorraine():
    items = [it_avatar("tk8-girl-02", 560, 875, 110),
             it_name("Lorraine Porter", 648, 846, check=(1040, 816)),
             it_subs("321K subscribers", 652, 894),
             it_sub(1265, 815, 265, 62, 39),
             it_bell(1452, 800, 52, click=66)]
    path = pts((22, 1640, 1060), (32, 1262, 828), (40, 1264, 830), (50, 1460, 812), (74, 1462, 814), (86, 1600, 1100))
    return photo_card("tarjeta-foto-inclinada", "Tarjeta del canal: foto inclinada con suscribirse y campana",
                      "Channel card: tilted photo with subscribe and bell", 18300, "fx-woman-07", (955, 440, -4.9), 0, 6,
                      200, items, [33, 62], path, 22, 86)


def mary_lee():
    items = [it_avatar("portrait-02", 537, 887, 130),
             it_name("Mary Lee", 646, 859, check=(905, 840)),
             it_subs("116K subscribers", 652, 905),
             it_like(1066, 843, 52, click=40),
             it_dislike(1147, 833, 52),
             it_sub(1350, 815, 262, 64, 62)]
    path = pts((22, 1500, 1100), (32, 1066, 862), (44, 1068, 864), (52, 1330, 830), (64, 1332, 832), (80, 1500, 1100))
    return photo_card("tarjeta-foto-marco", "Tarjeta del canal: foto con marco blanco y barra de progreso",
                      "Channel card: photo in a white frame with a progress bar", 18301, "fx-woman-04", (964, 439, -4.9),
                      45, 40, 210, items, [40, 62], path, 22, 80,
                      progress=(515, 745, 946, lambda fr: 0.25 + 0.3 * lin(fr, 10, 110)))


def diana_allen():
    cx, cy, rot = 955, 443, 0.0
    items = [it_avatar("selfie-03", 490, 853, 130),
             it_name("Diana Allen", 600, 836, check=(916, 836)),
             it_subs("925K subscribers", 602, 886),
             it_like(1087, 853, 52, click=40),
             it_sub(1275, 853, 262, 64, 60),
             it_bell(1462, 851, 54, click=88, at=25)]
    path = pts((22, 1500, 1100), (32, 1090, 880), (44, 1092, 882), (52, 1300, 880), (64, 1302, 882), (78, 1462, 870),
               (92, 1464, 872), (104, 1560, 1100))
    return photo_card("tarjeta-foto-recta", "Tarjeta del canal: foto con marco, me gusta, suscribirse y campana",
                      "Channel card: framed photo with like, subscribe and bell", 18302, "h-portrait-06",
                      (cx, cy, rot), 45, 40, 210, items, [40, 60, 88], path, 22, 104)


def sally_love():
    cx, cy, rot = 964, 443, 0.0
    items = [it_avatar("ig3-model-01", 533, 841, 112),
             it_name("Sally Love", 622, 824, check=(904, 824)),
             it_subs("514K subscribers", 624, 874),
             it_like(1042, 840, 52, solid_=True, count=("86K", 1090)),
             it_sub(1317, 842, 254, 62, 62)]
    path = pts((22, 1500, 1100), (40, 1320, 880), (60, 1322, 882), (80, 1480, 1100))
    return photo_card("tarjeta-foto-progreso", "Tarjeta del canal: foto con barra de progreso y me gusta",
                      "Channel card: photo with progress bar and likes", 18303, "fx-woman-05", (cx, cy, rot), 0, 0,
                      200, items, [60], path, 22, 80,
                      progress=(512, 708, 948, lambda fr: 0.3 + 0.1 * lin(fr, 10, 110)))



# --- G2 (source 21.4–26.6): the photo stays as the background; a card with the same photo rises from below ---------
def rise_card(id, es, en, order, sample, rig_at, margin, radius, bar_h, items, clicks, cursor_path, enter, leave,
              dur=5.1, progress=None, frosted=False, tags=()):
    t = _t(id, es, en, order, dur, "redes", ["tarjeta", "canal", "suscribirse", "foto"] + list(tags))
    s = P(t, dur)
    cx, cy, rot = rig_at
    end = dur * 25

    def fn(fr):
        dy = 1000 * (1 - k(fr, 7, 14)) + 1000 * k(fr, end - 19, 10)
        return cx, cy + dy, 1.0, rot, 1.0
    rig = Rig(fn, 60)
    full = Rig(lambda fr: (960.0, 540.0, 1.0 + 0.08 * lin(fr, 0, end), 0.0, min(1.0, fr / 3.0)), 0)
    s.photo(sample, full, 960, 540, 1920, 1080, label="Tu video", name="Fondo")
    ccx, ccy = rot_pt(cx, cy + bar_h / 2, rot, cx, cy)
    W, H = PHOTO_W + 2 * margin, PHOTO_H + bar_h + 2 * margin
    if not frosted:
        s.part("Tarjeta", card_layers(alpha=0.22), rig, ccx, ccy, W, H, radius=radius)
    s.photo(sample, rig, cx, cy, PHOTO_W, PHOTO_H, name="Foto", reuse="p1",
            ) if margin else s.photo(sample, rig, cx, cy, PHOTO_W, PHOTO_H, name="Foto", reuse="p1")
    if frosted:
        s.part("Cristal", solid(WHITE, 0.22), rig, cx, cy - 1, PHOTO_W, PHOTO_H + 2, radius=radius)
        bx, by = rot_pt(cx, cy + PHOTO_H / 2 + bar_h / 2, rot, cx, cy)
        s.part("Barra", card_layers(alpha=0.2), rig, bx, by, PHOTO_W, bar_h, radius=radius)
        tx, ty = rot_pt(cx, cy + PHOTO_H / 2 + radius / 2, rot, cx, cy)
        s.part("Barra (borde)", solid(WHITE), rig, tx, ty, PHOTO_W, radius, )
    if progress:
        x0, y0, length, frac = progress
        s.progress(rig, x0, y0, length, 12, frac)
    for item in items:
        item(s, rig)
    if cursor_path:
        s.clicks(cursor_path, clicks, enter, leave)
    return t


def gail_ford():
    items = [it_avatar("fx-woman-02", 560, 875, 110, at=9),
             it_name("Gail Ford", 648, 845, check=(895, 830), at=10),
             it_subs("384K subscribers", 652, 892, at=10),
             it_like(1062, 833, 50, click=45, at=12),
             it_dislike(1143, 822, 50, at=13),
             it_sub(1342, 803, 262, 62, 62, at=12)]
    path = pts((24, 1400, 1100), (38, 1062, 855), (48, 1064, 857), (56, 1300, 830), (66, 1302, 832), (84, 1450, 1100))
    return rise_card("tarjeta-cristal-inclinada", "Tarjeta del canal: cristal inclinado sobre la foto",
                     "Channel card: tilted glass over the photo", 18304, "fx-fashion-01", (957, 443, -4.9), 0, 40, 195,
                     items, [45, 62], path, 24, 84, frosted=True,
                     progress=(507, 745, 950, lambda fr: 0.38 + 0.25 * lin(fr, 10, 110)))


def amy_taylor():
    items = [it_avatar("tk8-girl-01", 533, 838, 110, at=9),
             it_name("Amy Taylor", 622, 824, check=(936, 823), at=10),
             it_subs("321K subscribers", 624, 872, at=10),
             it_like(1047, 840, 50, click=40, at=12),
             it_sub(1240, 838, 250, 62, 62, at=12),
             it_bell(1428, 838, 52, at=14)]
    path = pts((24, 1400, 1100), (34, 1047, 862), (44, 1049, 864), (54, 1250, 862), (66, 1252, 864), (84, 1400, 1100))
    return rise_card("tarjeta-cristal", "Tarjeta del canal: cristal sobre la foto con campana",
                     "Channel card: glass over the photo with bell", 18305, "fx-woman-08", (965, 445, 0.0), 0, 40, 195,
                     items, [40, 62], path, 24, 84, frosted=True)


def jean_lewis():
    items = [it_avatar("selfie-02", 528, 890, 130, at=9),
             it_name("Jean Lewis", 640, 862, cap=38, check=(940, 838), at=10),
             it_subs("2246K subscribers", 642, 910, at=10),
             it_sub(1265, 826, 262, 64, 45, at=12),
             it_bell(1452, 808, 56, click=70, at=14)]
    path = pts((24, 1400, 1100), (34, 1265, 850), (48, 1267, 852), (60, 1460, 830), (74, 1462, 832), (90, 1560, 1100))
    return rise_card("tarjeta-marco-inclinado", "Tarjeta del canal: marco blanco inclinado sobre la foto",
                     "Channel card: tilted white frame over the photo", 18306, "fx-woman-05", (955, 440, -4.9), 45, 40,
                     178, items, [45, 70], path, 24, 90)


def vivian_kim():
    items = [it_avatar("portrait-04", 500, 853, 130, at=9),
             it_name("Vivian Kim", 612, 835, cap=38, check=(915, 835), at=10),
             it_subs("256K subscribers", 612, 886, at=10),
             it_like(1035, 850, 50, solid_=True, count=("95K", 1085), at=12),
             it_sub(1317, 853, 265, 66, 78, at=12)]
    path = pts((24, 1400, 1100), (40, 1300, 880), (80, 1302, 882), (96, 1450, 1100))
    return rise_card("tarjeta-marco", "Tarjeta del canal: marco blanco sobre la foto con barra de progreso",
                     "Channel card: white frame over the photo with progress bar", 18307, "fx-woman-06",
                     (965, 443, 0.0), 45, 40, 178, items, [78], path, 24, 96,
                     progress=(490, 709, 948, lambda fr: 0.25 + 0.2 * lin(fr, 10, 110)))



# --- G3 (source 26.7–31.0): a white band slides in at the top or bottom and pushes the photo --------------------------
def band_card(id, es, en, order, sample, top, bar_h, items, clicks, cursor_path, enter, leave, dur=4.2, tags=()):
    t = _t(id, es, en, order, dur, "redes", ["barra", "canal", "suscribirse", "foto"] + list(tags))
    s = P(t, dur)
    end = dur * 25
    sign = 1 if top else -1
    q = lambda fr: k(fr, 8, 10) * (1 - k(fr, end - 19, 8))  # noqa: E731
    shove = Rig(lambda fr: (960.0, 540.0 + sign * bar_h * q(fr), 1.0, 0.0, min(1.0, fr / 3.0)), 60)
    band = Rig(lambda fr: (960.0, 540.0 - sign * bar_h * (1 - q(fr)), 1.0, 0.0, 1.0), 60)
    s.photo(sample, shove, 960, 540 + sign * bar_h, 1920, 1080, label="Tu video")
    y = bar_h / 2 if top else 1080 - bar_h / 2
    s.part("Barra", solid(WHITE), band, 960, y, 1940, bar_h)
    for item in items:
        item(s, band)
    if cursor_path:
        s.clicks(cursor_path, clicks, enter, leave)
    return t


def eva_atkins():
    items = [it_avatar("tk8-girl-03", 533, 127, 160, at=14),
             it_name("Eva Atkins", 653, 97, cap=44, check=(1005, 97), at=15),
             lambda s, rig: s.word("How to catch positive", rig, 655, 155, 28, LATO, 400, "#333333", "Texto",
                                   op=lambda fr: k(fr, 17, 5)),
             it_sub(1297, 129, 320, 74, 40, at=17, cap=30)]
    path = pts((24, 1450, 420), (34, 1300, 150), (44, 1302, 152), (56, 1420, 420))
    return band_card("barra-arriba", "Barra del canal arriba que empuja la foto", "Channel bar on top pushing the photo",
                     18308, "fx-woman-06", True, 258, items, [40], path, 24, 56)


def christopher():
    items = [it_avatar("man-01", 498, 949, 158, at=14),
             it_name("Christopher", 621, 918, cap=40, at=15),
             lambda s, rig: s.word("Game News channel", rig, 623, 974, 26, LATO, 400, "#333333", "Texto",
                                   op=lambda fr: k(fr, 17, 5)),
             it_sub(1224, 949, 316, 73, 26, at=17, cap=30),
             it_bell(1452, 949, 62, click=50, at=20)]
    path = pts((24, 1600, 1150), (40, 1458, 975), (54, 1460, 977), (70, 1600, 1150))
    return band_card("barra-abajo-campana", "Barra del canal abajo con suscrito y campana",
                     "Channel bar at the bottom with subscribed and bell", 18309, "h-man-05", False, 261, items, [50],
                     path, 24, 70)


def katie_tina():
    def labels(s, rig):
        for i, (x, word, num) in enumerate(((835, "280K", True), (1035, "114", True), (1237, "Share", False),
                                            (1437, "Download", False), (1638, "Save", False))):
            c = s.word(word, rig, x, 995, 24, LATO, 400, "#444444", f"Texto {i + 1}", align="center",
                       op=lambda fr, i=i: k(fr, 16 + 2 * i, 5))
            if num:
                c["textStyle"].update(counter=True, counterFrom=0, counterSeconds=1.6, counterCurve="easeOut")
        o = lambda i: (lambda fr: pop(fr, 15 + 2 * i, 5))  # noqa: E731
        s.thumb(rig, 835, 928, 56, None, op=o(0), solid_from_start=True)
        s.thumb(rig, 1035, 925, 56, None, op=o(1), down=True, name="No me gusta")
        s.share(rig, 1237, 925, 52, op=o(2))
        s.icon("Descargar", DOWNLOAD, stroke(INK, 4), rig, 1437, 925, 52, aspect=0.7, op=o(3))
        s.icon("Guardar", SAVE, stroke(INK, 4), rig, 1638, 925, 50, aspect=1.0, op=o(4))
    items = [it_name("Katie and Tina", 250, 925, cap=46, at=14),
             it_subs("117615 views", 252, 983, cap=30, at=15, count_from=0),
             labels]
    path = pts((24, 1500, 1150), (40, 1165, 960), (60, 1167, 962), (76, 1350, 1150))
    return band_card("barra-abajo-acciones", "Barra del video abajo con me gusta, compartir, descargar y guardar",
                     "Video bar at the bottom with like, share, download and save", 18310, "friends-02", False, 255,
                     items, [44], path, 24, 76)


def leonard_jones():
    items = [it_avatar("man-04", 258, 952, 158, at=14),
             it_name("Leonard Jones", 379, 924, cap=40, check=(720, 924), at=15),
             lambda s, rig: s.word("Fitness & Sport tutorials", rig, 381, 977, 26, LATO, 400, "#333333", "Texto",
                                   op=lambda fr: k(fr, 17, 5)),
             it_like(1043, 945, 60, click=40, at=17, count=("53K", 1092)),
             it_dislike(1218, 945, 60, at=18),
             lambda s, rig: s.word("6K", rig, 1270, 945, 24, LATO, 400, "#333333", "No me gusta (número)",
                                   op=lambda fr: k(fr, 20, 5)),
             it_sub(1585, 952, 322, 73, 999, at=17, cap=30)]
    path = pts((24, 1400, 1150), (36, 1045, 975), (48, 1047, 977), (66, 1300, 1150))
    return band_card("barra-abajo-me-gusta", "Barra del canal abajo con me gusta y suscribirse",
                     "Channel bar at the bottom with likes and subscribe", 18311, "fx-fashion-01", False, 257, items,
                     [40], path, 24, 66)



# --- G4 (source 31.2–34.9): comment and like/dislike bands --------------------------------------------------------
def it_text(content, xy, cap, colour="#333333", at=17, weight=400, family=LATO, name="Texto", x1=None, count=None):
    def f(s, rig):
        c = s.word(content, rig, xy[0], xy[1], cap, family, weight, colour, name, op=lambda fr: k(fr, at, 5), x1=x1)
        if count is not None:
            c["textStyle"].update(counter=True, counterFrom=count[0], counterSeconds=count[1], counterCurve="linear")
    return f


def it_rating(x0, x1, y, frac_dark, colour_dark="#333333", at=18, start=None):
    """The thin like/dislike ratio bar: grey track, dark part from the left (frac(fr))."""
    def f(s, rig):
        s.left_bar("Valoración", solid("#C8C8C8"), rig, x0, y, x1 - x0, 7, lambda fr: k(fr, at, 8), radius=3)
        s.left_bar("Valoración (oscura)", solid(colour_dark), rig, x0, y, x1 - x0, 8,
                   lambda fr: frac_dark(fr) * k(fr, at, 8), radius=3)
    return f


def melissa():
    q = "TL"
    items = [it_avatar("tk8-girl-04", *Q(q, 257, 95), 52 * S16, at=12),
             it_name("Melissa Clarke", *Q(q, 299, 85), cap=14 * S16, at=13, x1=Q(q, 423, 0)[0]),
             it_text("Europe travel channel", Q(q, 299, 104), 10 * S16, at=15, x1=Q(q, 434, 0)[0]),
             it_like(*Q(q, 488, 86), 22 * S16, solid_=True, at=15),
             it_text("Like", Q(q, 512, 87), 10 * S16, at=16),
             it_dislike(*Q(q, 563, 86), 22 * S16, at=16),
             it_text("Dislike", Q(q, 586, 87), 10 * S16, at=17),
             it_rating(Q(q, 477, 0)[0], Q(q, 627, 0)[0], Q(q, 0, 106)[1], lambda fr: 0.75)]
    return band_card("barra-valoracion-arriba", "Barra del canal arriba con me gusta, no me gusta y valoración",
                     "Channel bar on top with like, dislike and rating", 18312, "fx-woman-07", True, 258, items, [],
                     None, 0, 0, dur=3.5)


def miss_patricia():
    items = [it_avatar("portrait-06", 282, 127, 160, at=12),
             it_name("Miss Patricia", 402, 70, cap=40, at=13, x1=712),
             it_text("3 days ago", (738, 78), 22, "#777777", at=15, x1=873),
             it_text("The video is too loud! My dog got scared and hid", (402, 127), 30, at=15, x1=1238),
             it_text("under the couch! I am not satisfied!", (402, 176), 30, at=16, x1=1015),
             lambda s, rig: s.thumb(rig, 1397, 118, 64, None, op=lambda fr: pop(fr, 16, 5)),
             it_text("144", (1455, 125), 32, at=17, x1=1522),
             it_dislike(1628, 118, 64, click=37, at=17),
             it_text("30", (1695, 125), 32, at=18, x1=1740, count=(29, 37 / 25.0 + 0.04))]
    path = pts((14, 1700, -120), (28, 1632, 140), (40, 1634, 142), (52, 1660, -140))
    return band_card("comentario-arriba", "Comentario arriba con me gusta y no me gusta",
                     "Comment on top with like and dislike", 18313, "fx-woman-05", True, 258, items, [37], path, 14,
                     52, dur=3.5)


def nancy_lee():
    q = "BL"
    items = [it_avatar("portrait-03", *Q(q, 192, 804), 56 * S16, at=12),
             it_name("Nancy Lee", *Q(q, 235, 787), cap=15 * S16, at=13, x1=Q(q, 340, 0)[0]),
             it_text("3 days ago", Q(q, 350, 790), 8 * S16, "#777777", at=15, x1=Q(q, 398, 0)[0]),
             it_text("Love you and your fabulous videos! Thanks for", Q(q, 235, 807), 11 * S16, at=15,
                     x1=Q(q, 520, 0)[0]),
             it_text("another great tutorial) Awesome!", Q(q, 235, 825), 11 * S16, at=16, x1=Q(q, 443, 0)[0]),
             it_like(*Q(q, 608, 801), 22 * S16, click=37, at=16),
             it_text("512", Q(q, 630, 801), 11 * S16, at=17, x1=Q(q, 654, 0)[0], count=(511, 37 / 25.0 + 0.04)),
             it_dislike(*Q(q, 693, 800), 22 * S16, at=17),
             it_text("1", Q(q, 714, 801), 11 * S16, at=18)]
    path = pts((14, 1500, 1200), (28, Q(q, 610, 0)[0], Q(q, 0, 812)[1]), (42, Q(q, 612, 0)[0], Q(q, 0, 813)[1]),
               (56, 1500, 1200))
    return band_card("comentario-abajo", "Comentario abajo con me gusta", "Comment at the bottom with like", 18314,
                     "fx-woman-04", False, 257, items, [37], path, 14, 56, dur=3.5)


def susan_maxwell():
    q = "BR"
    items = [it_avatar("selfie-01", *Q(q, 987, 804), 56 * S16, at=12),
             it_name("Susan Maxwell", *Q(q, 1030, 793), cap=16 * S16, at=13, x1=Q(q, 1183, 0)[0]),
             it_text("Cooking lessons", Q(q, 1030, 814), 10 * S16, at=15, x1=Q(q, 1130, 0)[0]),
             lambda s, rig: s.thumb(rig, *Q(q, 1240, 795), 22 * S16, None, op=lambda fr: pop(fr, 16, 5)),
             it_text("Like", Q(q, 1262, 797), 10 * S16, at=17),
             it_dislike(*Q(q, 1315, 796), 22 * S16, click=37, at=17),
             it_text("Dislike", Q(q, 1336, 797), 10 * S16, at=18),
             it_rating(Q(q, 1230, 0)[0], Q(q, 1378, 0)[0], Q(q, 0, 817)[1],
                       lambda fr: 0.36 - 0.06 * k(fr, 37, 8))]
    path = pts((14, 1700, 1200), (28, Q(q, 1317, 0)[0], Q(q, 0, 806)[1]), (42, Q(q, 1319, 0)[0], Q(q, 0, 807)[1]),
               (56, 1700, 1200))
    return band_card("valoracion-abajo", "Barra del canal abajo con me gusta, no me gusta y valoración",
                     "Channel bar at the bottom with like, dislike and rating", 18315, "fx-fashion-01", False, 257,
                     items, [37], path, 14, 56, dur=3.5)


# --- G5 (source 35.1–39.3): a small card whose video is clicked and fills the frame; a side list of videos -----------
def follow(base, local, full_w, at, n=10):
    """The photo's rig: on the card (base) until frame at, then out to fill the frame (full_w wide)."""
    def fn(fr):
        cx, cy, sc, rot, op = base(fr)
        px, py = base.scr(fr, *local)
        q = k(fr, at, n)
        m = sc / base.rest[2]
        return (px + (960 - px) * q, py + (540 - py) * q, m + (1920 / full_w - m) * q, rot * (1 - q), 1.0)
    return fn


def card_full(id, es, en, order, sample, card, photo, items, play, click, path, enter, leave, dur=4.0,
              tags=()):
    t = _t(id, es, en, order, dur, "redes", ["tarjeta", "video", "play"] + list(tags))
    s = P(t, dur)
    (x0, y0, x1, y1, radius) = card
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    gone = lambda fr: 1 - k(fr, click + 3, 5)  # noqa: E731
    base = Rig(lambda fr: (cx, cy, 0.25 + 0.75 * pop(fr, 0, 8, 0.06), 0.0, k(fr, 0, 3) * gone(fr)), 60)
    s.part("Tarjeta", card_layers(), base, cx, cy, x1 - x0, y1 - y0, radius=radius)
    px0, py0, px1, py1, pr = photo
    pcx, pcy, pw, ph = (px0 + px1) / 2, (py0 + py1) / 2, px1 - px0, py1 - py0
    prig = Rig(follow(base, base.loc(pcx, pcy), pw, click + 2), click - 4)
    full = Rig(lambda fr: prig(fr)[:4] + (k(fr, 3, 4),), click - 4)
    s.photo(sample, full, pcx, pcy, pw, ph, label="Tu video")
    for item in items:
        item(s, base)
    s.play(base, play[0], play[1], play[2], play[3], op=lambda fr: k(fr, 6, 4),
           size=lambda fr: 1 + 0.12 * math.sin(math.pi * lin(fr, click - 2, 5)))
    s.clicks(path, [click], enter, leave)
    return t


def sandra_rodney():
    items = [it_avatar("man-02", 653, 740, 120, at=6),
             it_name("Sandra and Rodney", 752, 725, cap=42, at=7, x1=1212),
             it_subs("256K subscribers", 754, 780, cap=30, at=8, secs=1.0)]
    path = pts((18, 1150, 900), (28, 960, 470), (40, 962, 472), (56, 1100, 1150))
    return card_full("tarjeta-video-play", "Tarjeta de video: clic en play y el video llena la pantalla",
                     "Video card: click play and the video fills the frame", 18316, "couple-02",
                     (535, 180, 1378, 862, 50), (595, 237, 1318, 643, 20), items, (953, 440, 92, 66), 30, path, 18,
                     40, dur=4.0)


def nicole_friends():
    def title(s, rig):
        s.word("Top Tips from Blogging Experts", rig, 662, 873, 26, SLAB, 700, INK, "Título",
               op=lambda fr: k(fr, 9, 5), x1=1115)
        s.word("12:20", rig, 1138, 873, 26, LATO, 400, "#777777", "Duración", op=lambda fr: k(fr, 10, 5), x1=1207)
    items = [it_avatar("tk8-girl-02", 723, 280, 120, at=6),
             it_name("Nicole and friends", 822, 262, cap=42, at=7, x1=1257),
             it_subs("804K subscribers", 822, 313, cap=30, at=8, secs=1.0),
             title]
    path = pts((18, 1150, 1000), (28, 968, 630), (40, 970, 632), (56, 1100, 1150))
    return card_full("tarjeta-video-titulo", "Tarjeta de video con canal arriba y título: clic en play",
                     "Video card with channel on top and title: click play", 18317, "friends-01",
                     (600, 155, 1328, 945, 40), (600, 398, 1328, 805, 0), items, (963, 600, 92, 66), 32, path, 18,
                     40, dur=4.0)


def side_list(id, es, en, order, main, thumbs, titles, metas, clicks, path, enter, leave, dur=4.0, open_first=None,
              watch_later=False, tags=()):
    """The photo is pushed left as a white list of two videos slides in from the right (and back)."""
    t = _t(id, es, en, order, dur, "redes", ["lista", "videos"] + list(tags))
    s = P(t, dur)
    end = dur * 25
    q = lambda fr: k(fr, 13, 8) * (1 - k(fr, end - 12, 9))  # noqa: E731
    shove = Rig(lambda fr: (960 - 320 * q(fr), 540.0, 1.0, 0.0, k(fr, 0, 3)), 60)
    panel = Rig(lambda fr: (960 + 642 * (1 - q(fr)), 540.0, 1.0, 0.0, 1.0), 60)
    s.photo(main, shove, 640, 540, 1920, 1080, label="Tu video")
    s.part("Lista", [shadow("#2A2F4A", -10, 0, 40, 0.12), fill(WHITE)], panel, 1600, 540, 642, 1100)
    for i, (sample, y0) in enumerate(zip(thumbs, (120, 585))):
        rig = panel
        if open_first is not None and i == 0:
            rig = Rig(follow(panel, panel.loc(1578, y0 + 136), 483, open_first), open_first - 4)
        s.photo(sample, rig, 1578, y0 + 136, 483, 272, label=f"Video {i + 1}", name=f"Video {i + 1}")
        ty = y0 + 307
        for j, line in enumerate(titles[i]):
            s.word(line[0], panel, 1337, ty + 36 * j, 24, SLAB, 700, INK, f"Título {i + 1}" + (f".{j + 1}" if j else ""),
                   op=lambda fr, i=i: k(fr, 18 + 2 * i, 5), x1=line[1])
        s.word(metas[i][0], panel, 1337, ty + 77, 22, LATO, 400, "#777777", f"Datos {i + 1}",
               op=lambda fr, i=i: k(fr, 19 + 2 * i, 5), x1=metas[i][1])
        if watch_later:
            at = clicks[i]
            s.part(f"Ver más tarde {i + 1}", solid("#333333"), panel, 1785, y0 + 35, 70, 70, radius=6,
                   op=lambda fr: k(fr, 20, 4))
            s.part(f"Reloj {i + 1}", stroke(WHITE, 5), panel, 1785, y0 + 35, 40, 40, kind="ellipse",
                   op=lambda fr, at=at: k(fr, 20, 4) * (1 - on(fr, at)))
            s.part(f"Reloj {i + 1} (aguja)", stroke(WHITE, 5), panel, 1789, y0 + 31, 10, 18,
                   path="M 0 0 L 0 100 L 100 100", op=lambda fr, at=at: k(fr, 20, 4) * (1 - on(fr, at)))
            s.part(f"Hecho {i + 1}", stroke(WHITE, 7), panel, 1785, y0 + 35, 44, 34, path=TICK,
                   op=lambda fr, at=at: on(fr, at))
    if watch_later:
        a = clicks[0] + 4
        toast = Rig(lambda fr: (644.0, 946.0, 1.0, 0.0, k(fr, a, 4) * (1 - k(fr, end - 14, 4))), 60)
        s.part("Aviso", solid("#333333", 0.92), toast, 644, 946, 462, 78, radius=10)
        s.word("Saved to Watch Later", toast, 644, 946, 30, LATO, 400, WHITE, "Aviso (texto)", align="center",
               x1=830)
    s.clicks(path, clicks, enter, leave)
    return t


def watch_later():
    path = pts((22, 1700, 700), (30, 1790, 165), (40, 1792, 167), (48, 1790, 630), (60, 1792, 632), (74, 1950, 900))
    return side_list("lista-ver-mas-tarde", "Lista de videos: «Saved to Watch Later»",
                     "Video list: «Saved to Watch Later»", 18318, "tk8-girl-02", ["tk8-girl-03", "tk8-girl-01"],
                     [[("My favorite milkshake recipes -", 1790), ("Quick and easy", 1553)],
                      [("The most interesting news in the", 1807), ("world of fashion", 1567)]],
                     [("62K views · 4 days ago", 1627), ("121K views · 7 days ago", 1644)], [30, 52], path, 22, 74,
                     watch_later=True)


def side_open():
    path = pts((24, 1750, 700), (34, 1580, 280), (42, 1582, 282), (56, 1700, 1100))
    return side_list("lista-videos-abrir", "Lista de videos: clic en uno y llena la pantalla",
                     "Video list: click one and it fills the frame", 18319, "fx-woman-04",
                     ["ig3-model-03", "fx-woman-06"],
                     [[("TOP 10 places to stay in the city", 1798), ("this summer", 1527)],
                      [("How do we spend time with", 1737), ("friends", 1447)]],
                     [("121K views · 7 days ago", 1653), ("96K views · 14 days ago", 1653)], [36], path, 24, 56,
                     open_first=40, dur=3.8)


# --- G6 (source 39.5–43.1): comment cards; the card opens from its left edge, a reply can open below ---------------
def comment(id, es, en, order, card, head, lines, counts, like_click=None, dislike_click=None, answer=None,
            reply=None, dur=3.5, tags=()):
    """card = (x0, y0, x1, y1 before a reply); head = (avatar sample, (x, y, d), name, (x, y, x1), time, (x, y, x1));
    lines = [(text, x, y, x1)]; counts = (like (x, y, h), likes (txt, x, x1), dislike (x, y), dislikes (txt, x, x1),
    answer (x, y, x1)); reply = (y1 after, avatar, (x, y, d), name, (x, y, x1), time, (x, y, x1), text, (x, y, x1),
    like (x, y, h), dislike (x, y), open_at)."""
    t = _t(id, es, en, order, dur, "redes", ["comentario", "comentarios"] + list(tags))
    s = P(t, dur)
    end = dur * 25
    x0, y0, x1, y1 = card
    wide_ = lambda fr: 0.06 + 0.94 * k(fr, 2, 10) * (1 - k(fr, end - 10, 8))  # noqa: E731
    gone = lambda fr: 1 - k(fr, end - 3, 3)  # noqa: E731
    tall = (lambda fr: y1 + (reply[0] - y1) * k(fr, reply[-1], 6)) if reply else (lambda fr: y1)  # noqa: E731
    s.rect("Tarjeta", card_layers(alpha=0.13, blur=50, dy=18), lambda fr, u: (x0, y0, x0 + (x1 - x0) * wide_(fr),
                                                                               tall(fr)), op=lambda fr, u: gone(fr) *
           k(fr, 0, 2), radius=30, base=(x1 - x0, reply[0] - y0 if reply else y1 - y0))
    show = lambda fr: (x0, y0 - 40, x0 + (x1 - x0) * wide_(fr) - 10, 1100)  # noqa: E731
    fade = lambda at: (lambda fr: k(fr, at, 4) * (1 - k(fr, end - 11, 5)))  # noqa: E731
    sample, (ax, ay, ad), name, (nx, ny, nx1), when, (wx, wy, wx1) = head
    s.avatar(sample, STILL, ax, ay, ad, op=lambda fr: pop(fr, 2, 5) * (1 - k(fr, end - 8, 5)))
    s.word(name, STILL, nx, ny, 36, SLAB, 700, INK, "Nombre", x1=nx1, reveal=show, op=fade(4))
    s.word(when, STILL, wx, wy, 24, LATO, 400, "#888888", "Hace", x1=wx1, reveal=show, op=fade(5))
    for i, (text, lx, ly, lx1) in enumerate(lines):
        s.word(text, STILL, lx, ly, 32, LATO, 400, "#333333", f"Comentario {i + 1}" if i else "Comentario", x1=lx1,
               reveal=show, op=fade(6 + i))
    (lkx, lky, lkh), (ltxt, ltx, ltx1), (dkx, dky), (dtxt, dtx, dtx1), (anx, any_, anx1) = counts
    o = fade(10)
    s.thumb(STILL, lkx, lky, lkh, like_click, op=o)
    c = s.word(ltxt, STILL, ltx, lky, 26, LATO, 400, "#333333", "Me gusta (número)", x1=ltx1, op=o)
    if like_click:
        c["textStyle"].update(counter=True, counterFrom=int(ltxt) - 1, counterSeconds=like_click / 25 + 0.04,
                              counterCurve="linear")
    s.thumb(STILL, dkx, dky, lkh, dislike_click, op=o, down=True, name="No me gusta")
    c = s.word(dtxt, STILL, dtx, dky, 26, LATO, 400, "#333333", "No me gusta (número)", x1=dtx1, op=o)
    if dislike_click:
        c["textStyle"].update(counter=True, counterFrom=int(dtxt) - 1, counterSeconds=dislike_click / 25 + 0.04,
                              counterCurve="linear")
    s.word("TO ANSWER", STILL, anx, any_, 26, LATO, 700, "#555555", "Responder", x1=anx1, op=o)
    clicks = [c_ for c_ in (like_click, dislike_click) if c_]
    if reply:
        (_, rs, (rax, ray, rad), rname, (rnx, rny, rnx1), rwhen, (rwx, rwy, rwx1), rtext, (rtx, rty, rtx1),
         (rlx, rly, rlh), (rdx, rdy), at) = reply
        s.avatar(rs, STILL, rax, ray, rad, op=lambda fr: pop(fr, at + 1, 5) * (1 - k(fr, end - 8, 5)),
                 label="Foto de quien responde")
        s.word(rname, STILL, rnx, rny, 34, SLAB, 700, INK, "Respuesta (nombre)", x1=rnx1, reveal=show, op=fade(at + 2))
        s.word(rwhen, STILL, rwx, rwy, 24, LATO, 400, "#888888", "Respuesta (hace)", x1=rwx1, reveal=show,
               op=fade(at + 3))
        c = s.word(rtext, STILL, rtx, rty, 32, LATO, 400, "#333333", "Respuesta", x1=rtx1, reveal=show,
                   op=fade(at + 3))
        s.typed(c, at + 4, stagger=0.045, duration=0.03)
        s.thumb(STILL, rlx, rly, rlh, None, op=fade(at + 4))
        s.thumb(STILL, rdx, rdy, rlh, None, op=fade(at + 4), down=True, name="Respuesta (no me gusta)")
        clicks.append(at - 2)
        tx, ty = anx + (anx1 - anx) * 0.45, any_ + 18
    else:
        c_ = clicks[0]
        tx, ty = (lkx, lky + 20) if like_click else (dkx, dky + 20)
        del c_
    first = min(clicks)
    path = pts((first - 14, tx + 160, ty + 330), (first - 4, tx, ty), (first + 10, tx + 2, ty + 2),
               (first + 26, tx + 140, ty + 380))
    s.clicks(path, clicks, first - 14, first + 24)
    return t


def jonathan():
    return comment("comentario-me-gusta", "Comentario con me gusta que se marca", "Comment with a like clicked",
                   18320, (315, 320, 1600, 622),
                   ("fx-face-03", (422, 430, 140), "Jonathan", (532, 385, 710), "3 days ago", (742, 389, 877)),
                   [("Wow I didn't realise how many people liked the video,", 534, 437, 1463),
                    ("probably all his fans! I've never seen that done before", 534, 486, 1459)],
                   ((553, 562, 46), ("386", 600, 651), (752, 560), ("11", 802, 834), (895, 562, 1068)),
                   like_click=30)


def betty_griffin():
    return comment("comentario-no-me-gusta", "Comentario con no me gusta que se marca",
                   "Comment with a dislike clicked", 18321, (315, 320, 1600, 622),
                   ("tk8-girl-04", (422, 430, 140), "Betty Griffin", (532, 385, 777), "2 days ago", (806, 389, 941)),
                   [("Too hard lesson! I can not do it ((  I began to hiccup with", 534, 437, 1497),
                    ("tension. Need more information!", 534, 486, 1113)],
                   ((563, 562, 46), ("86", 610, 650), (760, 560), ("6", 810, 830), (905, 562, 1078)),
                   dislike_click=30)


def patience():
    return comment("comentario-respuesta", "Comentario con respuesta que se escribe",
                   "Comment with a reply being typed", 18322, (352, 245, 1560, 545),
                   ("fx-face-06", (462, 352, 140), "Patience", (572, 309, 735), "1 day ago", (767, 313, 888)),
                   [("Awesome tutorial thanks! You made that quite easy", 574, 361, 1471),
                    ("to follow for a rookie", 574, 409, 936)],
                   ((591, 483, 40), ("518", 630, 682), (733, 483), ("4", 770, 787), (938, 483, 1112)),
                   reply=(765, "tk8-girl-01", (623, 613, 100), "Ethel Lopez", (713, 591, 935), "2 days ago",
                          (966, 594, 1101), "Thanks I really appreciate this )", (715, 641, 1254), (731, 706, 36),
                          (871, 704), 29))


def paul_bailey():
    return comment("comentario-respuesta-2", "Comentario con respuesta (2)", "Comment with a reply (2)", 18323,
                   (352, 245, 1560, 545),
                   ("man-03", (462, 352, 140), "Paul Bailey", (572, 309, 794), "5 hours ago", (825, 313, 1048)),
                   [("My computer is very slow. I look at the screen for", 574, 361, 1432),
                    ("half a day and I feel sad...", 574, 409, 1003)],
                   ((591, 483, 40), ("5", 630, 646), (733, 483), ("35", 770, 805), (938, 483, 1112)),
                   reply=(765, "man-06", (623, 613, 100), "Russell Johnson", (713, 591, 1037), "1 hour ago",
                          (1071, 594, 1207), "Nothing works for me ei", (715, 641, 1142), (731, 706, 36),
                          (871, 704), 29))


# --- G7 (source 43.2–47.0): white cards that open (up from their bar, or from a strip in the middle) ---------------
def open_card(id, es, en, order, sample, card, photo, build, clicks, path, enter, leave, mode="up", reply=None,
              dur=3.5, tags=()):
    """card = (x0, y0, x1, y1, radius); photo = (x0, y0, x1, y1) of the picture's window. The card opens over
    frames 0-10 (mode "up": its top rises from the bar; "mid": from a strip at its middle) and closes the same way
    at the end; reply = (y1 after, frame) grows its bottom for a reply. build(s, show, vis) draws the rest: show is
    the card's rect per frame (for reveals) and vis(y) an opacity that is 1 where the card covers y."""
    t = _t(id, es, en, order, dur, "redes", ["tarjeta", "canal"] + list(tags))
    s = P(t, dur)
    end = dur * 25
    x0, y0, x1, y1, radius = card
    q = lambda fr: k(fr, 1, 10) * (1 - (k(fr, end - 12, 10) if mode == "up" else k(fr, end - 9, 8)))  # noqa: E731
    bottom = (lambda fr: y1 + (reply[0] - y1) * k(fr, reply[1], 7)) if reply else (lambda fr: y1)  # noqa: E731
    if mode == "up":
        bar = y1 - 230
        rect = lambda fr: (x0, bar + (y0 - bar) * q(fr), x1, bottom(fr))  # noqa: E731
    else:
        mid = (y0 + y1) / 2
        rect = lambda fr: (x0, mid + (y0 - mid) * q(fr), x1, mid + (bottom(fr) - mid) * q(fr))  # noqa: E731
    alive = lambda fr: k(fr, 0, 2) * (1 - k(fr, end - 3, 3))  # noqa: E731
    s.rect("Tarjeta", card_layers(alpha=0.13, blur=50, dy=18), lambda fr, u: rect(fr),
           op=lambda fr, u: alive(fr), radius=radius, base=(x1 - x0, (reply[0] if reply else y1) - y0))
    px0, py0, px1, py1 = photo
    s.window(sample, photo, lambda fr: (px0, max(py0, rect(fr)[1]), px1, min(py1, rect(fr)[3])), op=alive)

    def vis(y, pad=20):
        return lambda fr: alive(fr) * max(0.0, min(1.0, (min(y - rect(fr)[1], rect(fr)[3] - y) + pad) / pad))
    build(s, rect, vis)
    if path:
        s.clicks(path, clicks, enter, leave)
    return t


def matthew():
    def build(s, show, vis):
        s.word("Matthew - Superman", STILL, 352, 688, 32, LATO, 400, "#333333", "Título", x1=718, reveal=show)
        s.thumb(STILL, 998, 690, 46, 27, op=vis(690))
        c = s.word("58K", STILL, 1048, 690, 26, LATO, 400, "#444444", "Me gusta (número)", x1=1100, reveal=show)
        s.thumb(STILL, 1175, 690, 46, None, op=vis(690), down=True, name="No me gusta")
        s.word("1K", STILL, 1228, 690, 26, LATO, 400, "#444444", "No me gusta (número)", x1=1263, reveal=show)
        s.share(STILL, 1345, 690, 44, op=vis(690))
        s.word("SHARE THIS", STILL, 1392, 690, 26, LATO, 400, "#444444", "Compartir", x1=1558, reveal=show)
        s.avatar("man-05", STILL, 412, 802, 120, op=vis(802, 60))
        s.word("Matthew", STILL, 512, 780, 42, SLAB, 700, INK, "Canal", x1=720, reveal=show)
        s.check(STILL, 765, 779, 30, op=vis(779))
        s.word("5.86 million subscribers", STILL, 512, 835, 30, LATO, 400, "#333333", "Suscriptores", x1=873,
               reveal=show)
        s.subscribe(STILL, 1397, 808, 320, 74, lambda fr: 1.0, 47, cap=30, op=vis(808, 40))
        del c
    path = pts((14, 1300, 1150), (22, 1000, 715), (32, 1002, 717), (40, 1400, 830), (52, 1402, 832), (66, 1450, 1150))
    return open_card("tarjeta-video-compartir", "Tarjeta de video con me gusta, compartir y suscribirse",
                     "Video card with like, share and subscribe", 18324, "fx-man-01", (312, 158, 1600, 900, 30),
                     (352, 198, 1557, 622), build, [27, 47], path, 14, 66)


def linda_butler():
    def build(s, show, vis):
        s.avatar("selfie-04", STILL, 482, 742, 160, op=vis(742, 80))
        s.word("Linda Butler", STILL, 622, 714, 42, SLAB, 700, INK, "Canal", x1=915, reveal=show)
        s.check(STILL, 965, 714, 36, op=vis(714))
        s.word("1.25 million subscribers", STILL, 622, 770, 30, LATO, 400, "#333333", "Suscriptores", x1=983,
               reveal=show)
        s.subscribe(STILL, 1265, 742, 318, 74, lambda fr: 1.0, 30, cap=30, op=vis(742, 40))
        s.bell(STILL, 1487, 740, 64, click=52, op=vis(740, 40))
    path = pts((14, 1400, 1150), (22, 1270, 770), (34, 1272, 772), (44, 1490, 770), (58, 1492, 772), (72, 1600, 1150))
    return open_card("tarjeta-campana", "Tarjeta del canal con suscribirse y campana",
                     "Channel card with subscribe and bell", 18325, "fx-woman-02", (362, 218, 1567, 862, 40),
                     (362, 218, 1567, 622), build, [30, 52], path, 14, 72)


def rosa_cox():
    def build(s, show, vis):
        s.avatar("ig3-model-03", STILL, 583, 713, 100, op=vis(713, 50))
        s.word("Rosa Cox", STILL, 674, 692, 38, SLAB, 700, INK, "Canal", x1=890, reveal=show)
        s.check(STILL, 930, 693, 30, op=vis(693))
        s.word("122K subscribers", STILL, 674, 742, 28, LATO, 400, "#333333", "Suscriptores", x1=940, reveal=show)
        s.thumb(STILL, 1115, 715, 46, None, op=vis(715))
        s.word("254K", STILL, 1165, 715, 28, LATO, 400, "#444444", "Me gusta (número)", x1=1237, reveal=show)
        s.thumb(STILL, 1293, 713, 46, 22, op=vis(713), down=True, name="No me gusta")
        c = s.word("6", STILL, 1343, 715, 28, LATO, 400, "#444444", "No me gusta (número)", x1=1360, reveal=show)
        c["textStyle"].update(counter=True, counterFrom=5, counterSeconds=22 / 25 + 0.04, counterCurve="linear")
        at = 32
        s.avatar("man-01", STILL, 713, 845, 80, op=lambda fr: pop(fr, at + 2, 5) * vis(845, 40)(fr),
                 label="Foto de quien comenta")
        s.word("Carl Brown", STILL, 794, 829, 32, SLAB, 700, INK, "Comentario (nombre)", x1=976, reveal=show,
               op=lambda fr: k(fr, at + 3, 4))
        s.word("3 days ago", STILL, 995, 833, 22, LATO, 400, "#888888", "Comentario (hace)", x1=1108, reveal=show,
               op=lambda fr: k(fr, at + 4, 4))
        for i, (txt, y, x1) in enumerate((("The video has too many likes! Let there", 872, 1300),
                                          ("be one bad rating ))", 909, 1043))):
            c = s.word(txt, STILL, 794, y, 28, LATO, 400, "#333333", f"Comentario {i + 1}", x1=x1, reveal=show)
            s.typed(c, at + 5 + 18 * i, stagger=0.03, duration=0.03)
    path = pts((10, 1450, 1150), (18, 1296, 735), (28, 1298, 737), (40, 1450, 1150))
    return open_card("tarjeta-comentario", "Tarjeta de video con no me gusta y comentario",
                     "Video card with a dislike and a comment", 18326, "fx-woman-04", (473, 80, 1437, 795, 30),
                     (473, 80, 1437, 625), build, [22], path, 10, 40, mode="mid", reply=(985, 32))


def sue_evans():
    def build(s, show, vis):
        s.avatar("selfie-03", STILL, 612, 710, 90, op=vis(710, 45))
        s.word("Sue Evans", STILL, 702, 683, 42, SLAB, 700, INK, "Canal", x1=947, reveal=show)
        s.check(STILL, 990, 684, 30, op=vis(684))
        s.word("122K subscribers", STILL, 702, 733, 30, LATO, 400, "#333333", "Suscriptores", x1=969, reveal=show)
        s.thumb(STILL, 1105, 700, 46, 22, op=vis(700))
        c = s.word("58K", STILL, 1155, 700, 28, LATO, 400, "#444444", "Me gusta (número)", x1=1208, reveal=show)
        del c
        s.thumb(STILL, 1281, 698, 46, None, op=vis(698), down=True, name="No me gusta")
        s.word("1K", STILL, 1330, 700, 28, LATO, 400, "#444444", "No me gusta (número)", x1=1366, reveal=show)
        at = 32
        s.avatar("tk8-girl-02", STILL, 743, 845, 80, op=lambda fr: pop(fr, at + 2, 5) * vis(845, 40)(fr),
                 label="Foto de quien comenta")
        s.word("Edna White", STILL, 823, 829, 32, SLAB, 700, INK, "Comentario (nombre)", x1=1015, reveal=show,
               op=lambda fr: k(fr, at + 3, 4))
        s.word("1 hour ago", STILL, 1035, 833, 22, LATO, 400, "#888888", "Comentario (hace)", x1=1148, reveal=show,
               op=lambda fr: k(fr, at + 4, 4))
        for i, (txt, y, x1) in enumerate((("Thank you so very much on such a great", 872, 1340),
                                          ("tutorial on exactly what I", 909, 1148))):
            c = s.word(txt, STILL, 823, y, 28, LATO, 400, "#333333", f"Comentario {i + 1}", x1=x1, reveal=show)
            s.typed(c, at + 5 + 18 * i, stagger=0.03, duration=0.03)
    path = pts((10, 1350, 1150), (18, 1108, 720), (28, 1110, 722), (40, 1350, 1150))
    return open_card("tarjeta-comentario-2", "Tarjeta de video con me gusta y comentario",
                     "Video card with a like and a comment", 18327, "fx-woman-06", (502, 82, 1425, 795, 30),
                     (562, 142, 1367, 594), build, [22], path, 10, 40, mode="mid", reply=(985, 32))


# --- G8–G12: small white widgets that open from a sliver, are clicked, and close again ------------------------------
def widget(id, es, en, order, card, build, clicks, path, enter, leave, dur=3.9, axis="x", section="redes",
           tags=()):
    """card = (x0, y0, x1, y1, radius): opens from a sliver along `axis` over frames 0-8 and closes over the last
    10. build(s, show, vis): show = the card's rect per frame, vis(x, y) = 1 where the card covers the point."""
    t = _t(id, es, en, order, dur, section, ["botón", "suscribirse"] + list(tags))
    s = P(t, dur)
    end = dur * 25
    x0, y0, x1, y1, radius = card
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    q = lambda fr: k(fr, 0, 8) * (1 - k(fr, end - 10, 9))  # noqa: E731
    if axis == "x":
        rect = lambda fr: (cx - (cx - x0) * (0.06 + 0.94 * q(fr)), cy - (cy - y0) * (0.85 + 0.15 * q(fr)),  # noqa: E731
                           cx + (x1 - cx) * (0.06 + 0.94 * q(fr)), cy + (y1 - cy) * (0.85 + 0.15 * q(fr)))
    else:
        rect = lambda fr: (cx - (cx - x0) * (0.85 + 0.15 * q(fr)), cy - (cy - y0) * (0.06 + 0.94 * q(fr)),  # noqa: E731
                           cx + (x1 - cx) * (0.85 + 0.15 * q(fr)), cy + (y1 - cy) * (0.06 + 0.94 * q(fr)))
    alive = lambda fr: k(fr, 0, 2) * (1 - k(fr, end - 2, 2))  # noqa: E731
    s.rect("Tarjeta", card_layers(alpha=0.14, blur=50, dy=18), lambda fr, u: rect(fr),
           op=lambda fr, u: alive(fr), radius=radius, base=(x1 - x0, y1 - y0))

    def vis(x, y, pad=24):
        def f(fr):
            a, b, c, d = rect(fr)
            m = min(x - a, c - x, y - b, d - y)
            return alive(fr) * max(0.0, min(1.0, (m + pad) / pad))
        return f
    build(s, lambda fr: rect(fr) if q(fr) > 0.15 else (0.0, 0.0, 0.0, 0.0), vis)
    if path:
        s.clicks(path, clicks, enter, leave)
    return t


def w_photo(s, sample, x0, y0, x1, y1, vis, r=20, label="Tu foto"):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    s.photo(sample, STILL, cx, cy, x1 - x0, y1 - y0, label=label, name="Foto", op=vis(cx, cy, (x1 - x0) / 2),
            corner=r)


def w_sub(s, x, y, w, h, click, vis, cap=32, at=6):
    s.subscribe(STILL, x, y, w, h, lambda fr: k(fr, at, 6), click, cap=cap, op=vis(x, y, w / 2))


def nicole_mitchell():
    def build(s, show, vis):
        w_photo(s, "tk8-girl-04", 603, 451, 784, 632, vis)
        s.word("Nicole Mitchell", STILL, 833, 490, 48, SLAB, 700, INK, "Canal", x1=1268, reveal=show)
        w_sub(s, 995, 595, 320, 74, 16, vis)
        s.bell(STILL, 1236, 592, 70, click=44, op=vis(1236, 592))
    path = pts((2, 1150, 800), (10, 1000, 615), (20, 1002, 617), (32, 1240, 615), (48, 1242, 617), (60, 1300, 860))
    return widget("canal-foto-campana", "Botón del canal: foto, suscribirse y campana",
                  "Channel button: photo, subscribe and bell", 18328, (553, 402, 1355, 683, 50), build, [16, 44],
                  path, 2, 60)


def photo_column():
    def build(s, show, vis):
        w_photo(s, "ig3-model-01", 804, 320, 1125, 540, vis)
        w_sub(s, 965, 622, 320, 72, 44, vis)
        s.thumb(STILL, 875, 733, 62, 20, op=vis(875, 733))
        s.bell(STILL, 1065, 727, 66, click=70, op=vis(1065, 727))
    path = pts((4, 1000, 950), (12, 878, 760), (24, 880, 762), (36, 965, 645), (48, 967, 647), (60, 1068, 750),
               (74, 1070, 752), (84, 1150, 950))
    return widget("canal-foto-vertical", "Botón del canal vertical: foto, suscribirse, me gusta y campana",
                  "Vertical channel button: photo, subscribe, like and bell", 18329, (755, 268, 1175, 812, 50), build,
                  [20, 44, 70], path, 4, 84, axis="y")


def daniel_kevin():
    def build(s, show, vis):
        w_photo(s, "fx-man-02", 634, 362, 955, 563, vis)
        for i, (word, y, x1) in enumerate((("Daniel", 400, 1197), ("Kevin", 472, 1178), ("Bailey", 542, 1192))):
            s.word(word, STILL, 1013, y, 48, SLAB, 700, INK, f"Canal {i + 1}" if i else "Canal", x1=x1, reveal=show)
        w_sub(s, 793, 643, 320, 74, 22, vis)
        s.thumb(STILL, 1050, 645, 62, 47, op=vis(1050, 645))
        s.bell(STILL, 1200, 645, 70, click=72, op=vis(1200, 645))
    path = pts((6, 900, 900), (14, 795, 668), (26, 797, 670), (38, 1052, 670), (50, 1054, 672), (62, 1203, 670),
               (76, 1205, 672), (86, 1300, 900))
    return widget("canal-nombre-largo", "Botón del canal: foto, nombre en tres líneas, me gusta y campana",
                  "Channel button: photo, three-line name, like and bell", 18330, (585, 312, 1288, 735, 50), build,
                  [22, 47, 72], path, 6, 86)


def ariana_fox():
    def build(s, show, vis):
        w_photo(s, "fx-woman-07", 462, 463, 623, 623, vis)
        s.word("Ariana Fox", STILL, 673, 518, 48, SLAB, 700, INK, "Canal", x1=983, reveal=show)
        c = s.word("620K subscribers", STILL, 673, 575, 34, LATO, 400, "#333333", "Suscriptores", x1=983,
                   reveal=show)
        c["textStyle"].update(counter=True, counterFrom=0, counterSeconds=1.0, counterCurve="easeOut")
        w_sub(s, 1215, 543, 320, 74, 23, vis, at=8)
        s.bell(STILL, 1450, 540, 70, click=48, op=vis(1450, 540))
    path = pts((8, 1350, 800), (16, 1215, 568), (28, 1217, 570), (40, 1452, 565), (52, 1454, 567), (64, 1500, 800))
    return widget("canal-horizontal", "Botón del canal horizontal: foto, suscriptores, suscribirse y campana",
                  "Horizontal channel button: photo, subscribers, subscribe and bell", 18331,
                  (412, 412, 1537, 673, 50), build, [23, 48], path, 8, 64)


def lily_channel():
    def build(s, show, vis):
        s.word("Lily's Channel", STILL, 652, 460, 44, SLAB, 700, INK, "Canal", x1=1056, reveal=show)
        w_sub(s, 813, 561, 319, 73, 19, vis)
        s.share_click(STILL, 1075, 561, 62, 47, op=vis(1075, 561))
        s.bell(STILL, 1196, 559, 66, click=72, op=vis(1196, 559))
        s.avatar("tk8-girl-01", STILL, 1215, 381, 200, op=lambda fr: pop(fr, 5, 6) * vis(1100, 450, 300)(fr))
    path = pts((2, 900, 800), (10, 815, 585), (22, 817, 587), (36, 1078, 585), (50, 1080, 587), (62, 1198, 585),
               (76, 1200, 587), (88, 1300, 800))
    return widget("canal-avatar-esquina", "Botón del canal con avatar en la esquina, compartir y campana",
                  "Channel button with a corner avatar, share and bell", 18332, (597, 381, 1276, 661, 40), build,
                  [19, 47, 72], path, 2, 88, dur=4.0)


def vanessa_perry():
    def build(s, show, vis):
        s.word("Vanessa", STILL, 964, 562, 44, SLAB, 700, INK, "Canal", align="center", x1=1081, reveal=show)
        s.word("Perry", STILL, 964, 630, 44, SLAB, 700, INK, "Canal 2", align="center", x1=1041, reveal=show)
        w_sub(s, 964, 732, 319, 72, 20, vis)
        s.avatar("tk8-girl-02", STILL, 964, 359, 264, op=lambda fr: pop(fr, 5, 6) * vis(964, 450, 300)(fr))
    path = pts((6, 1080, 950), (14, 966, 757), (26, 968, 759), (40, 1100, 950))
    return widget("canal-avatar-arriba", "Botón del canal vertical con avatar arriba",
                  "Vertical channel button with the avatar on top", 18333, (755, 359, 1173, 842, 40), build, [20],
                  path, 6, 40, dur=4.0, axis="y")


def jackson_stewart():
    def build(s, show, vis):
        for i, (word, y, x1) in enumerate((("Jackson", 504, 690), ("Stewart", 573, 670))):
            s.word(word, STILL, 451, y, 46, SLAB, 700, INK, f"Canal {i + 1}" if i else "Canal", x1=x1, reveal=show)
        s.share_click(STILL, 1264, 482, 62, 22, op=vis(1264, 482))
        s.bell(STILL, 1429, 480, 66, click=75, op=vis(1429, 480))
        w_sub(s, 1336, 593, 321, 75, 42, vis)
        s.avatar("man-02", STILL, 956, 542, 319, op=lambda fr: pop(fr, 0, 6))
    path = pts((6, 1400, 800), (14, 1266, 505), (26, 1268, 507), (36, 1338, 618), (48, 1340, 620), (64, 1432, 505),
               (78, 1434, 507), (90, 1550, 800))
    return widget("canal-avatar-centro", "Botón del canal con avatar al centro, compartir y campana",
                  "Channel button with a centred avatar, share and bell", 18334, (353, 414, 1555, 674, 40), build,
                  [22, 42, 75], path, 6, 90, dur=4.0)


def alexis_watson():
    t = _t("lista-suscribirse", "Lista: suscribirse, recibir avisos y me gusta",
           "List: subscribe, get notified and like", 18335, 4.0, "redes", ["botón", "suscribirse", "lista"])
    s = P(t, 4.0)
    end = 4.0 * 25
    s.avatar("ig3-model-02", STILL, 801, 323, 192, op=lambda fr: pop(fr, 2, 6) * (1 - k(fr, end - 8, 6)))
    for i, (word, y, x1) in enumerate((("Alexis", 281, 1122), ("Watson", 351, 1153))):
        s.word(word, STILL, 944, y, 44, SLAB, 700, INK, f"Canal {i + 1}" if i else "Canal", x1=x1,
               reveal=lambda fr, i=i: (870, 0, 870 + 340 * k(fr, 5 + 2 * i, 8) * (1 - k(fr, end - 10, 8)), 1080))
    rows = (("Subscribe", 494, 934), ("Get notified", 605, 971), ("Like the video", 716, 1000))
    for i, (word, y, x1) in enumerate(rows):
        a = 6 + 3 * i
        grow = lambda fr, a=a: k(fr, a, 8) * (1 - k(fr, end - 12 + i, 8))  # noqa: E731
        s.rect(f"Fila {i + 1}", card_layers(alpha=0.12, blur=30, dy=10),
               lambda fr, u, y=y, grow=grow: (704, y - 44, 704 + 490 * grow(fr), y + 44),
               op=lambda fr, u, grow=grow: 1.0 if grow(fr) > 0.02 else 0.0, radius=44, base=(490, 88))
        s.word(word, STILL, 762, y, 30, LATO, 400, "#222222", f"Fila {i + 1} (texto)", x1=x1,
               reveal=lambda fr, grow=grow: (704, 0, 704 + 490 * grow(fr) - 20, 1080))
        o = lambda fr, grow=grow: max(0.0, min(1.0, (grow(fr) - 0.8) / 0.2))  # noqa: E731
        if i == 0:
            s.play_icon(STILL, 1105, y, 46, click=15, op=o)
        elif i == 1:
            s.bell(STILL, 1105, y, 64, click=50, op=o)
        else:
            s.thumb(STILL, 1105, y, 60, 70, op=o)
    path = pts((6, 1250, 700), (12, 1108, 515), (22, 1110, 517), (40, 1108, 628), (54, 1110, 630), (62, 1108, 740),
               (74, 1110, 742), (86, 1250, 900))
    s.clicks(path, [15, 50, 70], 6, 86)
    return t


def riley_channel():
    def build(s, show, vis):
        s.word("Riley's", STILL, 955, 320, 44, SLAB, 700, INK, "Canal", align="center", x1=1049, reveal=show)
        s.word("Channel", STILL, 955, 387, 44, SLAB, 700, INK, "Canal 2", align="center", x1=1073, reveal=show)
        w_photo(s, "tk8-girl-03", 795, 451, 1115, 650, vis, r=22)
        w_sub(s, 955, 727, 319, 73, 22, vis)
    path = pts((4, 1080, 950), (14, 957, 752), (26, 959, 754), (40, 1080, 950))
    return widget("canal-tarjeta-vertical", "Tarjeta vertical del canal: nombre, foto y suscribirse",
                  "Vertical channel card: name, photo and subscribe", 18336, (734, 240, 1176, 823, 40), build, [22],
                  path, 4, 40, dur=4.1, axis="y")


def julia_flores():
    t = _t("canal-sin-tarjeta", "Canal: avatar, nombre, suscriptores y suscribirse",
           "Channel: avatar, name, subscribers and subscribe", 18337, 4.0, "redes", ["botón", "suscribirse"])
    s = P(t, 4.0)
    end = 100
    out = lambda fr: 1 - k(fr, end - 10, 8)  # noqa: E731
    s.avatar("tk8-girl-04", STILL, 964, 364, 220, op=lambda fr: pop(fr, 0, 6) * out(fr))
    s.word("Julia Flores", STILL, 964, 542, 46, SLAB, 700, INK, "Canal", align="center", x1=1148,
           reveal=lambda fr: (964 - 200 * k(fr, 3, 7) * out(fr), 400, 964 + 200 * k(fr, 3, 7) * out(fr), 700))
    c = s.word("520K subscribers", STILL, 964, 605, 32, LATO, 400, "#333333", "Suscriptores", align="center",
               x1=1137, op=lambda fr: k(fr, 5, 5) * out(fr))
    c["textStyle"].update(counter=True, counterFrom=0, counterSeconds=0.8, counterCurve="easeOut")
    s.subscribe(STILL, 964, 709, 319, 75, lambda fr: k(fr, 4, 7) * (1 - k(fr, end - 10, 8)), 20, cap=32)
    path = pts((4, 1100, 950), (14, 966, 734), (24, 968, 736), (40, 990, 880), (92, 992, 882))
    s.clicks(path, [20], 4, 92)
    return t


def abigail_diaz():
    t = _t("canal-circulo", "Canal en un círculo con campana, me gusta y compartir",
           "Channel in a circle with bell, like and share", 18338, 3.8, "redes", ["botón", "campana", "me gusta"])
    s = P(t, 3.8)
    end = 95
    q = lambda fr: k(fr, 0, 8) * (1 - k(fr, end - 9, 8))  # noqa: E731
    s.part("Círculo", card_layers(alpha=0.14, blur=50, dy=18), STILL, 955, 482, 440, 440, kind="ellipse",
           size=lambda fr: max(0.02, q(fr)), op=lambda fr: 1.0 if q(fr) > 0.01 else 0.0)
    s.avatar("tk8-girl-02", STILL, 955, 390, 201, op=lambda fr: pop(fr, 3, 6) * (1 - k(fr, end - 10, 6)))
    for i, (word, y, x1) in enumerate((("Abigail", 542, 1057), ("Diaz", 614, 1016))):
        s.word(word, STILL, 955, y, 44, SLAB, 700, INK, f"Canal {i + 1}" if i else "Canal", align="center", x1=x1,
               op=lambda fr, i=i: k(fr, 6 + i, 4) * (1 - k(fr, end - 11, 5)))
    o = lambda at: (lambda fr: pop(fr, at, 5) * (1 - k(fr, end - 9, 5)))  # noqa: E731
    s.bell(STILL, 814, 721, 66, click=17, op=o(8))
    s.thumb(STILL, 956, 768, 60, 45, op=o(9))
    s.share_click(STILL, 1094, 724, 60, 70, op=o(10))
    path = pts((4, 900, 950), (12, 816, 745), (24, 818, 747), (38, 958, 792), (52, 960, 794), (62, 1096, 748),
               (76, 1098, 750), (88, 1200, 950))
    s.clicks(path, [17, 45, 70], 4, 88)
    return t


def morgan_simmons():
    def build(s, show, vis):
        s.avatar("fx-woman-02", STILL, 702, 383, 201, op=lambda fr: pop(fr, 2, 6) * (1 - k(fr, 97 - 10, 6)))
        for i, (word, y, x1) in enumerate((("Morgan", 473, 1032), ("Simmons", 545, 1081))):
            s.word(word, STILL, 813, y, 44, SLAB, 700, INK, f"Canal {i + 1}" if i else "Canal", x1=x1, reveal=show)
        c = s.word("95K subscribers", STILL, 813, 610, 30, LATO, 400, "#333333", "Suscriptores", x1=1103,
                   reveal=show)
        c["textStyle"].update(counter=True, counterFrom=0, counterSeconds=0.9, counterCurve="easeOut")
        o = lambda at: (lambda fr: pop(fr, at, 5) * (1 - k(fr, 97 - 9, 5)))  # noqa: E731
        s.bell(STILL, 1268, 416, 64, click=20, op=o(6))
        s.thumb(STILL, 1268, 537, 58, 42, op=o(7))
        s.share_click(STILL, 1268, 645, 58, 67, op=o(8))
    path = pts((4, 1400, 800), (12, 1270, 440), (24, 1272, 442), (36, 1270, 560), (48, 1272, 562), (60, 1270, 668),
               (74, 1272, 670), (86, 1400, 850))
    return widget("canal-iconos-columna", "Canal con iconos en columna: campana, me gusta y compartir",
                  "Channel with a column of icons: bell, like and share", 18339, (702, 383, 1186, 685, 40), build,
                  [20, 42, 67], path, 4, 86, dur=3.9)


# --- G11 (source 59.7–64.0): the channel's logo with subscribe, bell and share ---------------------------------------
def logo_pill():
    def build(s, show, vis):
        s.logo(STILL, 745, 540, 154, op=lambda fr: pop(fr, 4, 6) * vis(745, 540, 80)(fr))
        w_sub(s, 1044, 542, 352, 79, 20, vis, cap=34)
    path = pts((2, 1200, 800), (12, 1046, 568), (24, 1048, 570), (36, 1150, 800))
    return widget("logo-suscribirse", "Logo del canal con suscribirse", "Channel logo with subscribe", 18340,
                  (624, 430, 1286, 650, 110), build, [20], path, 2, 36, dur=4.1, section="elementos")


def logo_above():
    t = _t("logo-arriba-suscribirse", "Logo arriba y suscribirse", "Logo above and subscribe", 18341, 4.1,
           "elementos", ["botón", "suscribirse", "logo"])
    s = P(t, 4.1)
    end = 102
    out = lambda fr: 1 - k(fr, end - 12, 8)  # noqa: E731
    s.logo(STILL, 964, 430, 220, op=lambda fr: out(fr), size=lambda fr: pop(fr, 5, 6))
    s.part("Botón (sombra)", [shadow("#2A2F4A", 0, 8, 24, 0.15), fill(PILL_GREY)], STILL, 964, 607, 352, 79,
           radius=39, op=lambda fr: on(fr, 20) * out(fr))
    s.subscribe(STILL, 964, 607, 352, 79, lambda fr: k(fr, 0, 7) * out(fr), 20, cap=34)
    path = pts((2, 1100, 900), (12, 966, 633), (24, 968, 635), (36, 1100, 900))
    s.clicks(path, [20], 2, 36)
    return t


def logo_card_vertical():
    def build(s, show, vis):
        s.logo(STILL, 955, 403, 165, op=lambda fr: pop(fr, 4, 6) * vis(955, 403, 80)(fr))
        s.word("Channel", STILL, 955, 553, 44, SLAB, 700, INK, "Canal", align="center", x1=1073, reveal=show)
        s.word("Name", STILL, 955, 622, 44, SLAB, 700, INK, "Canal 2", align="center", x1=1037, reveal=show)
        s.bell(STILL, 885, 729, 66, click=22, op=vis(885, 729))
        s.share_click(STILL, 1025, 729, 62, 47, op=vis(1025, 729))
    path = pts((4, 1000, 950), (12, 888, 753), (26, 890, 755), (36, 1028, 753), (52, 1030, 755), (64, 1150, 950))
    return widget("logo-tarjeta-vertical", "Logo del canal en tarjeta vertical con campana y compartir",
                  "Channel logo on a vertical card with bell and share", 18342, (754, 260, 1154, 823, 50), build,
                  [22, 47], path, 4, 64, dur=4.0, axis="y", section="elementos")


def logo_card():
    def build(s, show, vis):
        s.logo(STILL, 765, 462, 165, op=lambda fr: pop(fr, 4, 6) * vis(765, 462, 80)(fr))
        s.word("Channel", STILL, 881, 432, 44, SLAB, 700, INK, "Canal", x1=1120, reveal=show)
        s.word("Name", STILL, 881, 502, 44, SLAB, 700, INK, "Canal 2", x1=1048, reveal=show)
        w_sub(s, 845, 608, 319, 77, 17, vis)
        s.bell(STILL, 1076, 614, 66, click=42, op=vis(1076, 614))
        s.share_click(STILL, 1186, 608, 60, 67, op=vis(1186, 608))
    path = pts((2, 1000, 900), (10, 847, 633), (22, 849, 635), (32, 1078, 638), (46, 1080, 640), (58, 1188, 632),
               (72, 1190, 634), (84, 1300, 900))
    return widget("logo-tarjeta", "Logo del canal en tarjeta con suscribirse, campana y compartir",
                  "Channel logo on a card with subscribe, bell and share", 18343, (623, 322, 1287, 702, 60), build,
                  [17, 42, 67], path, 2, 84, dur=3.9, section="elementos")


# --- G12 (source 64.0–68.9): rows of like / subscribe / bell, and name cards -----------------------------------------
def row_like_sub_bell():
    q = "TL"

    def build(s, show, vis):
        x, y = G(q, 385, 347)
        s.thumb(STILL, x, y, L(60), 12, op=vis(x, y))
        x, y = G(q, 596, 346)
        w_sub(s, x, y, L(290), L(66), 43, vis, cap=L(28))
        x, y = G(q, 806, 343)
        s.bell(STILL, x, y, L(66), click=65, op=vis(x, y))
    a, b, c = G(q, 385, 372), G(q, 596, 372), G(q, 806, 372)
    path = pts((2, a[0] + 120, a[1] + 300), (8, *a), (16, a[0] + 2, a[1] + 2), (32, *b), (48, b[0] + 2, b[1] + 2),
               (58, *c), (72, c[0] + 2, c[1] + 2), (90, c[0] + 140, c[1] + 330))
    return widget("fila-me-gusta-suscribirse", "Fila: me gusta, suscribirse y campana",
                  "Row: like, subscribe and bell", 18344, GB(q, 305, 268, 888, 428, 50), build, [12, 43, 65], path, 2,
                  90, dur=4.7, section="elementos")


def subscribed_icons():
    q = "TR"

    def build(s, show, vis):
        x, y = G(q, 1878, 296)
        w_sub(s, x, y, L(290), L(66), 22, vis, cap=L(28))
        for i, (fn, dx, at) in enumerate(((s.thumb, 1770, 45), (s.bell, 1878, 70), (s.share_click, 1987, 95))):
            x, y = G(q, dx, 395)
            if fn == s.thumb:
                fn(STILL, x, y, L(60), at, op=vis(x, y))
            elif fn == s.bell:
                fn(STILL, x, y, L(64), click=at, op=vis(x, y))
            else:
                fn(STILL, x, y, L(58), at, op=vis(x, y))
    pts_ = [G(q, 1878, 320), G(q, 1770, 420), G(q, 1878, 420), G(q, 1987, 420)]
    path = pts((6, pts_[0][0] + 100, pts_[0][1] + 300), (14, *pts_[0]), (26, pts_[0][0] + 2, pts_[0][1] + 2),
               (38, *pts_[1]), (50, pts_[1][0] + 2, pts_[1][1] + 2), (62, *pts_[2]), (74, pts_[2][0] + 2, pts_[2][1] + 2),
               (88, *pts_[3]), (100, pts_[3][0] + 2, pts_[3][1] + 2), (110, pts_[3][0] + 150, pts_[3][1] + 300))
    return widget("suscrito-iconos", "Suscrito con me gusta, campana y compartir",
                  "Subscribed with like, bell and share", 18345, GB(q, 1680, 210, 2080, 485, 50), build,
                  [22, 45, 70, 95], path, 6, 110, dur=4.7, axis="y", section="elementos")


def dylan_smith():
    q = "BL"

    def build(s, show, vis):
        x, y = G(q, 212, 1040)
        s.word("Dylan Smith", STILL, x, y, L(42), SLAB, 700, INK, "Canal", x1=G(q, 533, 0)[0], reveal=show)
        x, y = G(q, 212, 1100)
        c = s.word("820K subscribers", STILL, x, y, L(28), LATO, 400, "#333333", "Suscriptores", x1=G(q, 495, 0)[0],
                   reveal=show)
        c["textStyle"].update(counter=True, counterFrom=0, counterSeconds=1.0, counterCurve="easeOut")
        x, y = G(q, 742, 1068)
        w_sub(s, x, y, L(290), L(66), 20, vis, cap=L(28))
        x, y = G(q, 953, 1065)
        s.bell(STILL, x, y, L(66), click=45, op=vis(x, y))
    a, c = G(q, 742, 1092), G(q, 953, 1090)
    path = pts((4, a[0] + 150, a[1] + 300), (12, *a), (24, a[0] + 2, a[1] + 2), (36, *c), (50, c[0] + 2, c[1] + 2),
               (64, c[0] + 150, c[1] + 300))
    return widget("nombre-suscrito-campana", "Nombre del canal con suscrito y campana",
                  "Channel name with subscribed and bell", 18346, GB(q, 160, 968, 1032, 1168, 50), build, [20, 45],
                  path, 4, 64, dur=4.6)


def william_robinson():
    q = "BR"

    def build(s, show, vis):
        x, y = G(q, 1614, 985)
        s.word("William Robinson", STILL, x, y, L(42), SLAB, 700, INK, "Canal", x1=G(q, 2077, 0)[0], reveal=show)
        x, y = G(q, 1614, 1046)
        s.word("920K subscribers, 510K liked", STILL, x, y, L(28), LATO, 400, "#333333", "Suscriptores",
               x1=G(q, 2078, 0)[0], reveal=show)
        x, y = G(q, 1760, 1132)
        w_sub(s, x, y, L(290), L(66), 18, vis, cap=L(28))
        x, y = G(q, 1980, 1132)
        s.thumb(STILL, x, y, L(60), 46, op=vis(x, y))
        x, y = G(q, 2080, 1132)
        s.thumb(STILL, x, y, L(60), None, op=vis(x, y), down=True, name="No me gusta")
    a, c = G(q, 1760, 1156), G(q, 1980, 1156)
    path = pts((4, a[0] + 150, a[1] + 300), (10, *a), (22, a[0] + 2, a[1] + 2), (36, *c), (52, c[0] + 2, c[1] + 2),
               (66, c[0] + 150, c[1] + 300))
    return widget("nombre-suscrito-me-gusta", "Nombre del canal con suscrito, me gusta y no me gusta",
                  "Channel name with subscribed, like and dislike", 18347, GB(q, 1560, 912, 2195, 1225, 50), build,
                  [18, 46], path, 4, 66, dur=4.5)


# --- G13 (source 69.1–72.4): words with buttons, no card ----------------------------------------------------------
def _bare(id, es, en, order, dur, tags=()):
    t = _t(id, es, en, order, dur, "elementos", ["botón", "texto"] + list(tags))
    return t, P(t, dur)


def like_notified():
    q = "TL"
    t, s = _bare("me-gusta-avisos", "Me gusta y campana con «Like this / Notified»",
                 "Like and bell with «Like this / Notified»", 18348, 3.2, ["me gusta", "campana"])
    end = 80
    bx, by0 = G(q, 560, 262)
    _, by1 = G(q, 560, 448)
    grow = lambda fr: k(fr, 0, 6) * (1 - k(fr, end - 6, 5))  # noqa: E731
    s.rect("Barra", solid(RED), lambda fr, u: (bx - 8, (by0 + by1) / 2 - (by1 - by0) / 2 * grow(fr), bx + 8,
                                                (by0 + by1) / 2 + (by1 - by0) / 2 * grow(fr)), radius=8,
           base=(16, by1 - by0))
    wipe = lambda fr: k(fr, 3, 8) * (1 - k(fr, end - 14, 8))  # noqa: E731
    for i, (word, y, x1) in enumerate((("Like this", 305, 920), ("Notified", 398, 903))):
        x, yy = G(q, 630, y)
        s.word(word, STILL, x, yy, L(54), SLAB, 700, INK, f"Título {i + 1}" if i else "Título", x1=G(q, x1, 0)[0],
               reveal=lambda fr: (bx + 8, 0, bx + 8 + 800 * wipe(fr), 1080))
    out = lambda fr: 1 - k(fr, end - 12, 6)  # noqa: E731
    x, y = G(q, 310, 355)
    s.thumb(STILL, x, y, L(75), None, op=lambda fr: pop(fr, 4, 5) * out(fr), solid_from_start=True)
    xb, yb = G(q, 453, 350)
    s.bell(STILL, xb, yb, L(80), click=43, op=lambda fr: pop(fr, 6, 5) * out(fr))
    path = pts((8, xb + 120, yb + 300), (16, x, y + 30), (24, x + 2, y + 32), (36, xb, yb + 30), (48, xb + 2, yb + 32),
               (62, xb + 150, yb + 320))
    s.clicks(path, [20, 43], 8, 62)
    return t


def like_this_bar():
    q = "TR"
    t, s = _bare("me-gusta-barra", "«Like this» con barra de valoración", "«Like this» with a rating bar", 18349, 3.2,
                 ["me gusta", "valoración"])
    end = 80
    out = lambda fr: 1 - k(fr, end - 10, 6)  # noqa: E731
    x, y = G(q, 1878, 237)
    s.word("Like this", STILL, x, y, L(56), SLAB, 700, INK, "Título", align="center", x1=G(q, 2025, 0)[0],
           op=out, reveal=lambda fr: (0, y - 60 + 120 * (1 - k(fr, 2, 6)), 1920, y + 60))
    x0, ly = G(q, 1712, 326)
    x1 = G(q, 2045, 0)[0]
    s.left_bar("Valoración", solid("#B5B5B5"), STILL, x0, ly, x1 - x0, 10, lambda fr: k(fr, 4, 8), op=out, radius=5)
    s.left_bar("Valoración (oscura)", solid("#333333"), STILL, x0, ly, x1 - x0, 11,
               lambda fr: k(fr, 4, 8) * (0.62 + 0.24 * k(fr, 21, 8)), op=out, radius=5)
    xl, yl = G(q, 1757, 415)
    s.thumb(STILL, xl, yl, L(75), 21, op=lambda fr: pop(fr, 6, 5) * out(fr))
    xd, yd = G(q, 1996, 415)
    s.thumb(STILL, xd, yd, L(75), None, op=lambda fr: pop(fr, 7, 5) * out(fr), down=True, name="No me gusta")
    path = pts((6, xl + 150, yl + 300), (14, xl, yl + 25), (28, xl + 2, yl + 27), (40, xl + 140, yl + 330))
    s.clicks(path, [21], 6, 40)
    return t


def subscribe_done():
    q = "BL"
    t, s = _bare("suscribirse-hecho", "«Subscribe Channel» con «DO IT!» que pasa a «DONE»",
                 "«Subscribe Channel» with «DO IT!» turning «DONE»", 18350, 3.2, ["suscribirse"])
    end = 80
    out = lambda fr: 1 - k(fr, end - 12, 6)  # noqa: E731
    for i, (word, y, x1) in enumerate((("Subscribe", 957, 762), ("Channel", 1040, 735))):
        x, yy = G(q, 596, y)
        c = s.word(word, STILL, x, yy, L(58), SLAB, 700, INK, f"Título {i + 1}" if i else "Título", align="center",
                   x1=G(q, x1, 0)[0], op=out)
        s.typed(c, 5 + 3 * i, stagger=0.03, duration=0.12, preset="fade")
    x, y = G(q, 596, 1160)
    s.subscribe(STILL, x, y, L(284), L(86), lambda fr: k(fr, 0, 7) * (1 - k(fr, end - 3, 3)), 25, cap=L(34),
                label="DO IT!", done="DONE")
    path = pts((6, x + 150, y + 300), (14, x, y + 25), (30, x + 2, y + 27), (44, x + 150, y + 330))
    s.clicks(path, [25], 6, 44)
    return t


def subscribe_tick():
    q = "BR"
    t, s = _bare("suscribirse-casilla", "Casilla marcada con «Subscribe Youtube Channel»",
                 "Ticked box with «Subscribe Youtube Channel»", 18351, 3.0, ["suscribirse", "casilla"])
    end = 75
    out = lambda fr: 1 - k(fr, end - 8, 6)  # noqa: E731
    x, y = G(q, 1680, 1078)
    s.part("Casilla", [shadow("#2A2F4A", 0, 6, 20, 0.12), fill("#EFEFEF")], STILL, x, y, L(140), L(140),
           radius=20, op=lambda fr: k(fr, 33, 4) * out(fr))
    s.part("Marca", stroke(RED, 9), STILL, x, y, L(64), L(52), path=TICK,
           op=lambda fr: (1 - on(fr, 33)) * out(fr), size=lambda fr: pop(fr, 1, 5))
    s.part("Marca (hecha)", stroke(INK, 9), STILL, x, y, L(64), L(52), path=TICK, op=lambda fr: on(fr, 33) * out(fr))
    for i, (word, yy, x1) in enumerate((("Subscribe", 995, 2155), ("Youtube", 1078, 2103), ("Channel", 1160, 2103))):
        tx, ty = G(q, 1822, yy)
        s.word(word, STILL, tx, ty, L(56), SLAB, 700, INK, f"Título {i + 1}" if i else "Título", x1=G(q, x1, 0)[0],
               op=lambda fr, i=i: k(fr, 6 - 2 * i, 5) * out(fr), slide=lambda fr, i=i: (-60 * (1 - k(fr, 6 - 2 * i, 8)), 0))
    path = pts((4, x + 150, y + 300), (12, x, y + 25), (36, x + 2, y + 27), (48, x + 150, y + 330))
    s.clicks(path, [33], 4, 48)
    return t


# --- G14 (source 72.4–76.0): red pills that turn white when clicked ------------------------------------------------
def toggle_pill(s, x, y, w, h, click, grow, out, contents, name="Botón", white_first=False):
    """A pill (radius h/2) that opens from its centre with grow(fr), red with white contents until click, then
    white with a soft shadow and dark contents. contents(colour, op) draws what is inside."""
    red_op = (lambda fr: on(fr, click) * out(fr)) if white_first else (lambda fr: (1 - on(fr, click)) * out(fr))
    white_op = (lambda fr: (1 - on(fr, click)) * out(fr)) if white_first else (lambda fr: on(fr, click) * out(fr))
    press = lambda fr: 1 - 0.06 * math.sin(math.pi * lin(fr, click - 2, 5))  # noqa: E731
    s.part(f"{name} (blanco)", [shadow("#2A2F4A", 0, 10, 30, 0.14), fill(WHITE)], STILL, x, y, w, h, radius=h / 2,
           op=white_op, wmul=grow, size=press)
    s.part(name, solid(RED), STILL, x, y, w, h, radius=h / 2, op=red_op, wmul=grow, size=press)
    ready = lambda fr: max(0.0, min(1.0, (grow(fr) - 0.75) / 0.25))  # noqa: E731
    contents(WHITE, lambda fr: ready(fr) * red_op(fr))
    contents(INK, lambda fr: ready(fr) * white_op(fr))


def youtube_channel():
    q = "TL"
    t, s = _bare("youtube-channel", "«YOUTUBE CHANNEL» que se vuelve rojo al hacer clic",
                 "«YOUTUBE CHANNEL» turning red on click", 18352, 3.2, ["título"])
    end = 80
    for i, (word, y, x1) in enumerate((("YOUTUBE", 296, 770), ("CHANNEL", 380, 772))):
        x, yy = G(q, 597, y)
        for colour, op, nm in (("#333333", lambda fr: 1 - on(fr, 22), ""), (RED, lambda fr: on(fr, 22), " (rojo)")):
            s.word(word, STILL, x, yy, L(54), SLAB, 800, colour, (f"Título {i + 1}" if i else "Título") + nm,
                   align="center", x1=G(q, x1, 0)[0],
                   op=lambda fr, op=op, i=i: op(fr) * k(fr, 2 * i, 6) * (1 - k(fr, end - 10 + 2 * i, 6)),
                   slide=lambda fr, i=i: (60 * k(fr, end - 10 + 2 * i, 8) - 40 * (1 - k(fr, 2 * i, 8)) * i, 0))
    x, y = G(q, 597, 340)
    path = pts((4, x + 140, y + 300), (14, x, y + 40), (30, x + 2, y + 42), (44, x + 150, y + 330))
    s.clicks(path, [22], 4, 44)
    return t


def subscribe_counter():
    q = "TR"
    t, s = _bare("suscribirse-contador", "Suscribirse con contador que pasa de 19999 a 20000",
                 "Subscribe with a counter going from 19999 to 20000", 18353, 3.1, ["suscribirse", "contador"])
    end = 78
    out = lambda fr: 1 - k(fr, end - 8, 6)  # noqa: E731
    x0, y = G(q, 1575, 352)
    x1 = G(q, 2190, 0)[0]
    h = L(118)
    back = lambda fr: k(fr, 6, 8)  # noqa: E731
    s.left_bar("Contador (fondo)", [shadow("#2A2F4A", 0, 10, 30, 0.12), fill(WHITE)], STILL, x0, y, x1 - x0, h,
               back, op=lambda fr: (1 - on(fr, 22)) * out(fr), radius=h / 2)
    s.left_bar("Contador (gris)", solid("#A8A8A8"), STILL, x0, y, x1 - x0, h, back,
               op=lambda fr: on(fr, 22) * out(fr), radius=h / 2)
    cx = G(q, 2000, 0)[0]
    for colour, op, nm, txt in (("#333333", lambda fr: 1 - on(fr, 22), "Contador", "19999"),
                                (WHITE, lambda fr: on(fr, 22), "Contador (nuevo)", "20000")):
        s.word(txt, STILL, cx, y, L(38), LATO, 400, colour, nm, x1=G(q, 2135, 0)[0],
               op=lambda fr, op=op: op(fr) * k(fr, 10, 4) * out(fr))
    px, _ = G(q, 1765, 0)
    pw = G(q, 1952, 0)[0] - G(q, 1575, 0)[0]

    def contents(colour, op):
        s.word("SUBSCRIBE" if colour == WHITE else "SUBSCRIBED", STILL, px, y, L(38), LATO, 400, colour,
               "Botón" if colour == WHITE else "Botón (suscrito)", align="center", x1=G(q, 1907, 0)[0], op=op)
    toggle_pill(s, px, y, pw, h, 22, lambda fr: k(fr, 0, 7), out, contents)
    path = pts((4, px + 140, y + 300), (14, px, y + 30), (30, px + 2, y + 32), (44, px + 150, y + 330))
    s.clicks(path, [22], 4, 44)
    return t


def like_share_pills():
    q = "BL"
    t, s = _bare("me-gusta-compartir-botones", "Botones «Like it» y «Share» que pasan de rojo a blanco",
                 "«Like it» and «Share» buttons turning from red to white", 18354, 3.2, ["me gusta", "compartir"])
    end = 80
    out = lambda fr: 1 - k(fr, end - 8, 6)  # noqa: E731
    lx, ly = G(q, 597, 985)
    sx, sy = G(q, 596, 1147)

    def like(colour, op):
        x, y = G(q, 475, 987)
        if colour == WHITE:
            s.thumb(STILL, x, y, L(60), None, colour=WHITE, op=op, name="Me gusta (blanco)")
        else:
            s.thumb(STILL, x, y, L(60), None, colour=INK, op=op, solid_from_start=True)
        x, y = G(q, 557, 987)
        s.word("Like it", STILL, x, y, L(44), LATO, 400, colour, "Me gusta" + (" (rojo)" if colour == WHITE else ""),
               x1=G(q, 712, 0)[0], op=op)

    def share(colour, op):
        x, y = G(q, 500, 1147)
        s.word("Share", STILL, x, y, L(44), LATO, 400, colour, "Compartir" + (" (rojo)" if colour == WHITE else ""),
               x1=G(q, 645, 0)[0], op=op)
        x, y = G(q, 715, 1147)
        s.share(STILL, x, y, L(56), colour=colour, op=op, outline=colour == WHITE,
                name="Compartir (icono)" + (" (rojo)" if colour == WHITE else ""))
    toggle_pill(s, lx, ly, L(400), L(120), 22, lambda fr: k(fr, 0, 7), out, like, name="Me gusta (botón)")
    toggle_pill(s, sx, sy, L(387), L(118), 49, lambda fr: k(fr, 3, 7), out, share, name="Compartir (botón)")
    path = pts((4, lx + 160, ly + 300), (14, lx - 40, ly + 20), (30, lx - 38, ly + 22), (40, sx - 30, sy + 20),
               (56, sx - 28, sy + 22), (68, sx + 160, sy + 330))
    s.clicks(path, [22, 49], 4, 68)
    return t


def share_this():
    q = "BR"
    t, s = _bare("compartir-esto", "Botón «Share This» que pasa de rojo a blanco",
                 "«Share This» button turning from red to white", 18355, 3.1, ["compartir"])
    end = 78
    out = lambda fr: 1 - k(fr, end - 6, 5)  # noqa: E731
    x, y = G(q, 1876, 1073)

    def contents(colour, op):
        ax, ay = G(q, 1805, 1068)
        s.share(STILL, ax, ay, L(80), colour=colour, op=op, outline=colour == WHITE,
                name="Compartir" + (" (rojo)" if colour == WHITE else ""))
        for i, (word, wy, x1) in enumerate((("Share", 1048, 1995), ("This", 1101, 1962))):
            tx, ty = G(q, 1878, wy)
            s.word(word, STILL, tx, ty, L(36), LATO, 400, colour,
                   f"Texto {i + 1}" + (" (rojo)" if colour == WHITE else ""), x1=G(q, x1, 0)[0], op=op)
    toggle_pill(s, x, y, L(327), L(165), 20, lambda fr: k(fr, 0, 8), out, contents)
    path = pts((4, x + 160, y + 300), (14, x, y + 30), (28, x + 2, y + 32), (40, x + 150, y + 330))
    s.clicks(path, [20], 4, 40)
    return t


# --- G15 / G16 (source 75.9–80.9): a thumb with a counter, «Like it!» / «Dislike!», the red pill, «Advise friends» --
def thumb_counter(down=False):
    q = "TL"
    id_ = "no-me-gusta-contador" if down else "me-gusta-contador"
    t, s = _bare(id_, ("No me gusta" if down else "Me gusta") + " grande con contador",
                 ("Big dislike" if down else "Big like") + " with a counter", 18357 if down else 18356, 2.2,
                 ["no me gusta" if down else "me gusta", "contador"])
    end = 55
    click = 20 if down else 19
    out = lambda fr: 1 - k(fr, end - 8, 6)  # noqa: E731
    x, y = G(q, 590, 330)
    s.thumb(STILL, x, y, L(130), click, op=lambda fr: k(fr, 0, 4) * out(fr), down=down,
            outline_w=L(130) * 0.045, name="No me gusta" if down else "Me gusta")
    bx, by = G(q, 705, 300)
    s.part("Contador (globo)", [shadow("#2A2F4A", 0, 6, 20, 0.12), fill(WHITE)], STILL, bx, by, L(160), L(90),
           radius=L(45), op=lambda fr: k(fr, click + 1, 4) * out(fr), size=lambda fr: pop(fr, click + 1, 5))
    num = "33" if down else "200"
    c = s.word(num, STILL, bx, by, L(36), LATO, 400, "#333333", "Contador", align="center",
               x1=bx + L(60 if len(num) == 3 else 40), op=lambda fr: k(fr, click + 3, 3) * out(fr))
    c["textStyle"].update(counter=True, counterFrom=int(num) - (12 if not down else 3),
                          counterSeconds=(click + 12) / 25.0, counterCurve="linear")
    path = pts((2, x + 160, y + 260), (12, x + 10, y + 30), (26, x + 12, y + 32), (40, x + 170, y + 300))
    s.clicks(path, [click], 2, 40)
    return t


def like_it_pill(down=False):
    q = "TR"
    id_ = "no-me-gusta-boton" if down else "me-gusta-boton"
    word = "Dislike!" if down else "Like it!"
    t, s = _bare(id_, f"Botón «{word}» que suelta pulgares", f"«{word}» button releasing thumbs",
                 18359 if down else 18358, 2.3, ["no me gusta" if down else "me gusta"])
    end = 57
    click = 25
    out = lambda fr: 1 - k(fr, end - 6, 5)  # noqa: E731
    x, y = G(q, 1878, 412)

    def contents(colour, op):
        s.word(word, STILL, x, y, L(40), LATO, 400, colour, "Botón" + (" (rojo)" if colour == WHITE else ""),
               align="center", x1=x + L(76), op=op)
    toggle_pill(s, x, y, L(290), L(110), click, lambda fr: k(fr, 2, 7), out, contents)
    for i, (dx, at) in enumerate(((0, click), (-40, click + 4), (30, click + 8))):
        def g(fr, u, dx=dx, at=at):
            q_ = lin(fr, at, 18)
            return (x + dx * q_, y - L(60) - L(220) * q_, L(76), L(76), 180.0 if down else 0.0,
                    (1.0 if fr > at else 0.0) * (1 - q_) * 0.9)
        s.obj(f"Pulgar {i + 1}", solid("#555555"), g, path=THUMB)
    path = pts((4, x + 160, y + 300), (14, x, y + 20), (32, x + 2, y + 22), (46, x + 150, y + 320))
    s.clicks(path, [click], 4, 46)
    return t


def red_like_pill(down=False):
    q = "BL"
    id_ = "pildora-no-me-gusta" if down else "pildora-me-gusta"
    t, s = _bare(id_, "Píldora roja de me gusta y no me gusta: clic en " + ("no me gusta" if down else "me gusta"),
                 "Red like / dislike pill: click on " + ("dislike" if down else "like"), 18361 if down else 18360, 2.4,
                 ["me gusta", "no me gusta"])
    end = 60
    click = 27
    out = lambda fr: 1 - k(fr, end - 6, 5)  # noqa: E731
    x, y = G(q, 596, 1085)
    lx, ly = G(q, 540, 1085)
    dx, dy = G(q, 655, 1085)

    def contents(colour, op):
        if colour == WHITE:
            s.thumb(STILL, lx, ly, L(72), None, colour=WHITE, op=op, name="Me gusta (blanco)")
            s.thumb(STILL, dx, dy, L(72), None, colour=WHITE, op=op, down=True, name="No me gusta (blanco)")
        else:
            s.thumb(STILL, lx, ly, L(72), None, colour=INK, op=op, solid_from_start=not down)
            s.thumb(STILL, dx, dy, L(72), None, colour=INK, op=op, down=True, solid_from_start=down,
                    name="No me gusta")
    toggle_pill(s, x, y, L(334), L(166), click, lambda fr: k(fr, 2, 7), out, contents)
    tx, ty = (dx, dy) if down else (lx, ly)
    path = pts((4, tx + 160, ty + 300), (14, tx, ty + 20), (34, tx + 2, ty + 22), (48, tx + 150, ty + 320))
    s.clicks(path, [click], 4, 48)
    return t


def advise_friends(down=False):
    q = "BR"
    id_ = "no-recomendar" if down else "recomendar-amigos"
    title = "Don't recommend" if down else "Advise friends"
    t, s = _bare(id_, f"«{title}» con cinco pulgares que se marcan", f"«{title}» with five thumbs being marked",
                 18363 if down else 18362, 2.5, ["valoración", "no me gusta" if down else "me gusta"])
    end = 62
    out = lambda fr: 1 - k(fr, end - 12, 6)  # noqa: E731
    x, y = G(q, 1878, 1003)
    c = s.word(title, STILL, x, y, L(52), SLAB, 700, INK, "Título", align="center",
               x1=x + (L(270) if down else L(244)), op=lambda fr: k(fr, 7, 4) * out(fr))
    s.typed(c, 7, stagger=0.02, duration=0.12, preset="fade", order="random")
    marks = []
    for i in range(5):
        tx, ty = G(q, 1680 + 100 * i, 1113)
        at = 20 + 3 * i
        marks.append((tx, ty, at))
        o = lambda fr, i=i: pop(fr, 3 + 1.5 * i, 5) * out(fr)  # noqa: E731
        s.icon(f"Pulgar {i + 1}", THUMB, solid("#A0A0A0"), STILL, tx, ty, L(72),
               op=lambda fr, o=o, at=at: o(fr) * (1 - on(fr, at)), turn=(lambda fr: 180.0) if down else None)
        s.icon(f"Pulgar {i + 1} (marcado)", THUMB, solid(INK), STILL, tx, ty, L(72),
               op=lambda fr, o=o, at=at: o(fr) * on(fr, at), turn=(lambda fr: 180.0) if down else None,
               size=lambda fr, at=at: 1 + 0.15 * math.sin(math.pi * lin(fr, at, 5)))
    path = pts((4, marks[4][0] + 120, marks[4][1] + 200), (16, marks[0][0], marks[0][1] + 15),
               *[(at + 1, mx, my + 15) for mx, my, at in marks[1:]], (40, marks[4][0] + 2, marks[4][1] + 17),
               (50, marks[4][0] + 150, marks[4][1] + 300))
    s.clicks(path, [at for _, _, at in marks], 4, 50)
    return t


# --- G17 (source 80.9–83.7): a round red button; clicked it turns white and a label slides out --------------------
def glyph(s, kind, x, y, h, colour, op, outline, name):
    """One of the round buttons' glyphs: bell, like, share or play, in outline or filled."""
    if kind == "bell":
        s.icon(name, BELL, stroke(colour, h * 0.07) if outline else solid(colour), STILL, x, y, h, aspect=0.92, op=op)
    elif kind == "like":
        s.icon(name, THUMB, stroke(colour, h * 0.07) if outline else solid(colour), STILL, x, y, h, op=op)
    elif kind == "share":
        s.icon(name, SHARE, stroke(colour, h * 0.07) if outline else solid(colour), STILL, x, y, h, aspect=1.15,
               op=op)
    else:
        w = h * 1.38
        s.part(name, stroke(colour, h * 0.08) if outline else solid(colour), STILL, x, y, w, h, radius=h * 0.25,
               op=op)
        s.part(name + " (triángulo)", stroke(colour, h * 0.07) if outline else solid(WHITE), STILL, x + w * 0.03, y,
               w * 0.22, h * 0.36, path=PLAYTRI, op=op)


def round_button(kind, label, id_, es, en, order, x=740, y=535, d=210):
    t, s = _bare(id_, es, en, order, 2.8, ["botón", kind])
    end = 70
    click = 20
    gone = lambda fr: 1 - k(fr, end - 4, 3)  # noqa: E731
    lab = lambda fr: k(fr, click + 3, 8) * (1 - k(fr, end - 14, 8))  # noqa: E731
    lw, lh = 440.0, 92.0
    s.left_bar("Etiqueta", solid(PILL_GREY), STILL, x, y, lw + d / 2, lh, lambda fr: max(0.001, lab(fr)),
               op=lambda fr: 1.0 if lab(fr) > 0.01 else 0.0, radius=lh / 2)
    s.word(label, STILL, x + d / 2 + 30, y, 36, LATO, 400, "#333333", "Etiqueta (texto)", x1=x + d / 2 + lw - 20,
           reveal=lambda fr: (x + d / 2, 0, x + d / 2 + (lw + 10) * lab(fr), 1080))
    press = lambda fr: 1 - 0.08 * math.sin(math.pi * lin(fr, click - 2, 5))  # noqa: E731
    s.part("Botón (blanco)", [shadow("#2A2F4A", 0, 8, 26, 0.16), fill(WHITE)], STILL, x, y, d, d, kind="ellipse",
           op=lambda fr: on(fr, click) * gone(fr), size=press)
    s.part("Botón", [shadow("#2A2F4A", 0, 8, 26, 0.16), fill(RED)], STILL, x, y, d, d, kind="ellipse",
           op=lambda fr: (1 - on(fr, click)), size=lambda fr: pop(fr, 0, 6) * press(fr))
    gh = d * (0.36 if kind == "play" else 0.42)
    glyph(s, kind, x, y, gh, WHITE, lambda fr: (1 - on(fr, click)) * k(fr, 4, 3), True, "Icono")
    glyph(s, kind, x, y, gh, INK, lambda fr: on(fr, click) * gone(fr), False, "Icono (oscuro)")
    path = pts((2, x + 150, y + 160), (12, x + 8, y + 20), (28, x + 10, y + 22), (42, x + 120, y + 330))
    s.clicks(path, [click], 2, 42)
    return t


def round_bell():
    return round_button("bell", "Get notified", "boton-redondo-campana", "Botón redondo rojo: campana y «Get notified»",
                        "Round red button: bell and «Get notified»", 18364)


def round_like():
    return round_button("like", "Like the video", "boton-redondo-me-gusta",
                        "Botón redondo rojo: me gusta y «Like the video»", "Round red button: like and «Like the video»",
                        18365)


def round_share():
    return round_button("share", "Share this", "boton-redondo-compartir",
                        "Botón redondo rojo: compartir y «Share this»", "Round red button: share and «Share this»",
                        18366, x=750, y=537)


def round_play():
    return round_button("play", "Subscribe", "boton-redondo-suscribirse",
                        "Botón redondo rojo: play y «Subscribe»", "Round red button: play and «Subscribe»", 18367,
                        x=760, y=537, d=243)


# --- G18 (source 83.7–89.1): columns and rows of round buttons clicked one by one ----------------------------------
def button_set(s, buttons, end, label_mode, enter_step=3, white=False, cursor=True):
    """buttons = [(kind, x, y, d, click, label)]: red circles that pop in turn, each clicked (white, dark icon) and
    labelled (label_mode "pill": a grey pill slides out to the right and stays; "right" / "up": a word shows by it
    for a moment)."""
    n = len(buttons)
    for i, (kind, x, y, d, click, label) in enumerate(buttons):
        gone = lambda fr, i=i: 1 - k(fr, end - 8 + 1.5 * (n - 1 - i), 4)  # noqa: E731
        if label_mode == "pill":
            lab = lambda fr, click=click, i=i: k(fr, click + 3, 8) * (1 - k(fr, end - 22 + 2 * i, 8))  # noqa: E731
            lw = label[1]
            s.left_bar(f"Etiqueta {i + 1}", solid(PILL_GREY), STILL, x, y, lw + d / 2, d * 0.52,
                       lambda fr, lab=lab: max(0.001, lab(fr)), op=lambda fr, lab=lab: 1.0 if lab(fr) > 0.01 else 0.0,
                       radius=d * 0.26)
            s.word(label[0], STILL, x + d / 2 + 28, y, d * 0.17, LATO, 400, "#333333", f"Etiqueta {i + 1} (texto)",
                   x1=x + d / 2 + lw - 16, reveal=lambda fr, lab=lab, x=x, d=d, lw=lw: (x + d / 2, 0,
                                                                                       x + d / 2 + lw * lab(fr), 1080))
        elif label_mode in ("right", "up"):
            tip = lambda fr, click=click: k(fr, click + 2, 4) * (1 - k(fr, click + 16, 6))  # noqa: E731
            if label_mode == "right":
                s.word(label, STILL, x + d * 0.75, y, d * 0.16, LATO, 400, "#333333", f"Etiqueta {i + 1}", op=tip,
                       x1=x + d * 0.75 + d * 1.6)
            else:
                s.word(label, STILL, x, y - d * 0.78, d * 0.15, LATO, 400, "#333333", f"Etiqueta {i + 1}",
                       align="center", op=tip, x1=x + d * 0.8)
        press = lambda fr, click=click: 1 - 0.08 * math.sin(math.pi * lin(fr, click - 2, 5))  # noqa: E731
        s.part(f"Botón {i + 1} (blanco)", [shadow("#2A2F4A", 0, 8, 24, 0.15), fill(WHITE)], STILL, x, y, d, d,
               kind="ellipse", op=lambda fr, click=click, gone=gone: on(fr, click) * gone(fr), size=press)
        s.part(f"Botón {i + 1}", [shadow("#2A2F4A", 0, 8, 24, 0.15), fill(WHITE if white else RED)], STILL, x, y, d,
               d, kind="ellipse", op=lambda fr, click=click: 1 - on(fr, click),
               size=lambda fr, i=i, press=press: pop(fr, enter_step * i, 6) * press(fr))
        gh = d * (0.32 if kind == "play" else 0.4)
        glyph(s, kind, x, y, gh, INK if white else WHITE,
              lambda fr, click=click, i=i: (1 - on(fr, click)) * k(fr, enter_step * i + 3, 3), True, f"Icono {i + 1}")
        glyph(s, kind, x, y, gh, INK, lambda fr, click=click, gone=gone: on(fr, click) * gone(fr), False,
              f"Icono {i + 1} (oscuro)")
    if not cursor:
        return
    marks = [(b[4], b[1] + 8, b[2] + 20) for b in buttons]
    seq = [(marks[0][0] - 10, marks[0][1] + 150, marks[0][2] + 200)]
    for c, x, y in marks:
        seq += [(c - 4, x, y), (c + 6, x + 2, y + 2)]
    seq.append((marks[-1][0] + 20, marks[-1][1] + 150, marks[-1][2] + 300))
    s.clicks(pts(*seq), [m[0] for m in marks], seq[0][0], seq[-1][0])


def column_labels():
    t, s = _bare("columna-botones-etiquetas", "Columna de botones redondos con etiquetas: suscribirse, avisos, me gusta",
                 "Column of round buttons with labels: subscribe, notifications, like", 18368, 5.3, ["columna"])
    button_set(s, [("play", 761, 311, 175, 20, ("Subscribe", 418)), ("bell", 761, 511, 175, 45, ("Get notified", 463)),
                   ("like", 761, 709, 175, 70, ("Like the video", 494))], 133, "pill")
    return t


def column_icons():
    t, s = _bare("columna-botones", "Columna de botones redondos: suscribirse, me gusta y campana",
                 "Column of round buttons: subscribe, like and bell", 18369, 5.3, ["columna"])
    button_set(s, [("play", 780, 331, 175, 25, "Subscribe"), ("like", 780, 534, 175, 48, "Like the video"),
                   ("bell", 780, 729, 175, 73, "Get notified")], 133, "right")
    return t


def row_icons():
    t, s = _bare("fila-botones", "Fila de botones redondos: suscribirse, campana, compartir y me gusta",
                 "Row of round buttons: subscribe, bell, share and like", 18370, 5.3, ["fila"])
    button_set(s, [("play", 623, 540, 175, 28, "Subscribe"), ("bell", 843, 540, 175, 53, "Get notified"),
                   ("share", 1066, 540, 175, 78, "Share"), ("like", 1287, 540, 175, 103, "Like it")], 133, "up",
               enter_step=2)
    return t


def row_subscribe():
    t, s = _bare("fila-suscribirse", "Fila: me gusta, suscribirse, compartir y campana",
                 "Row: like, subscribe, share and bell", 18371, 5.3, ["fila", "suscribirse"])
    end = 133
    gone = lambda fr: 1 - k(fr, end - 9, 5)  # noqa: E731

    def contents(colour, op):
        s.word("SUBSCRIBE" if colour == WHITE else "SUBSCRIBED", STILL, 801, 540, 44, LATO, 400, colour,
               "Botón" if colour == WHITE else "Botón (suscrito)", align="center", x1=801 + 190, op=op)
    toggle_pill(s, 801, 540, 480, 158, 55, lambda fr: k(fr, 4, 8), gone, contents)
    button_set(s, [("like", 501, 540, 158, 30, None), ("share", 1103, 540, 158, 80, None),
                   ("bell", 1302, 540, 158, 105, None)], end, None, enter_step=4)
    return t


# --- G19 (source 89.2–92.3): two or three round buttons ------------------------------------------------------------
def three_white():
    t, s = _bare("tres-botones-blancos", "Tres botones blancos: me gusta, campana y compartir, clic a la vez",
                 "Three white buttons: like, bell and share, clicked at once", 18372, 3.0, ["fila"])
    end = 75
    bs = [("like", *G("TL", 253, 350), 209, 20, None), ("bell", *G("TL", 596, 355), 209, 20, None),
          ("share", *G("TL", 938, 358), 209, 20, None)]
    button_set(s, bs, end, None, enter_step=1, white=True, cursor=False)
    for i, (_, x, y, _, c, _) in enumerate(bs):
        path = pts((2 + i, x + 90, y + 220), (12, x + 8, y + 22), (26, x + 10, y + 24), (36, x + 100, y + 320))
        s.clicks(path, [c], 2 + i, 36)
    return t


def two_buttons(id_, es, en, order, quad, a, b, dur, start=0):
    t, s = _bare(id_, es, en, order, dur, ["fila"])
    pos = {"L": (478, 1085) if quad == "BL" else (1760, 1085 if quad == "BR" else 358),
           "R": (715, 1085) if quad == "BL" else (1998, 1085 if quad == "BR" else 358)}
    x1, y1 = G(quad, *pos["L"])
    x2, y2 = G(quad, *pos["R"])
    button_set(s, [(a, x1, y1, 209, 20 + start, None), (b, x2, y2, 209, 43 + start, None)], int(dur * 25), None,
               enter_step=2)
    return t


def like_share():
    return two_buttons("me-gusta-compartir-redondos", "Dos botones rojos: me gusta y compartir",
                       "Two red buttons: like and share", 18373, "TR", "like", "share", 3.0)


def like_bell():
    return two_buttons("me-gusta-campana-redondos", "Dos botones rojos: me gusta y campana",
                       "Two red buttons: like and bell", 18374, "BL", "like", "bell", 3.0)


def bell_share():
    return two_buttons("campana-compartir-redondos", "Dos botones rojos: campana y compartir",
                       "Two red buttons: bell and share", 18375, "BR", "bell", "share", 2.9)


# --- G20 (source 92.4–96.5): subscribe pills with like and bell ----------------------------------------------------
def play_subscribe():
    t, s = _bare("suscribirse-play", "Botón rojo «SUBSCRIBE» con play que pasa a «SUBSCRIBED»",
                 "Red «SUBSCRIBE» button with play turning «SUBSCRIBED»", 18376, 4.1, ["suscribirse"])
    end = 102
    out = lambda fr: 1 - k(fr, end - 6, 5)  # noqa: E731
    x, y = 951, 523

    def contents(colour, op):
        glyph(s, "play", 790, y, 60, colour, op, colour == WHITE, "Play" + (" (rojo)" if colour == WHITE else ""))
        s.word("SUBSCRIBE" if colour == WHITE else "SUBSCRIBED", STILL, 1021, y, 38, LATO, 400, colour,
               "Botón" if colour == WHITE else "Botón (suscrito)", align="center", x1=1021 + 140, op=op)
    toggle_pill(s, x, y, 573, 155, 22, lambda fr: k(fr, 0, 7), out, contents)
    path = pts((4, x + 160, y + 320), (14, x, y + 30), (30, x + 2, y + 32), (44, x + 150, y + 330))
    s.clicks(path, [22], 4, 44)
    return t


def sub_row(id_, es, en, order, dur, pill, like=None, bell=None, clicks=(), start_like=4):
    t, s = _bare(id_, es, en, order, dur, ["suscribirse"])
    end = int(dur * 25)
    out = lambda fr: 1 - k(fr, end - 8, 6)  # noqa: E731
    x, y, w, h, sub_click = pill
    s.subscribe(STILL, x, y, w, h, lambda fr: k(fr, 0, 7) * (1 - k(fr, end - 4, 4)), sub_click, cap=h * 0.36)
    marks = []
    if like:
        s.thumb(STILL, like[0], like[1], like[2], like[3], op=lambda fr: pop(fr, start_like, 5) * out(fr))
        marks.append((like[3], like[0] + 6, like[1] + 22))
    marks.append((sub_click, x, y + 22))
    if bell:
        s.bell(STILL, bell[0], bell[1], bell[2], click=bell[3], op=lambda fr: pop(fr, start_like + 1, 5) * out(fr))
        marks.append((bell[3], bell[0] + 4, bell[1] + 24))
    marks.sort()
    seq = [(marks[0][0] - 10, marks[0][1] + 150, marks[0][2] + 260)]
    for c, mx, my in marks:
        seq += [(c - 4, mx, my), (c + 8, mx + 2, my + 2)]
    seq.append((marks[-1][0] + 22, marks[-1][1] + 150, marks[-1][2] + 300))
    s.clicks(pts(*seq), [m[0] for m in marks], seq[0][0], seq[-1][0])
    return t


def like_sub_bell_row():
    return sub_row("me-gusta-suscribirse-campana", "Me gusta, suscribirse y campana sin tarjeta",
                   "Like, subscribe and bell without a card", 18377, 3.9, (964, 534, 410, 93, 42),
                   like=(650, 539, 85, 22), bell=(1263, 534, 85, 65))


def like_sub_row():
    return sub_row("me-gusta-suscribirse", "Me gusta y suscribirse sin tarjeta", "Like and subscribe without a card",
                   18378, 3.8, (1024, 538, 458, 105, 45), like=(705, 540, 85, 23))


def sub_bell_row():
    return sub_row("suscribirse-campana", "Suscribirse y campana sin tarjeta", "Subscribe and bell without a card",
                   18379, 3.6, (964, 540, 418, 96, 23), bell=(1266, 540, 85, 45))


# --- The promo shots over footage (source 8.0–15.9): elements the grids do not show -----------------------------------
ARROW = "M 0 0 L 0 84 L 22 66 L 36 100 L 52 93 L 38 60 L 66 60 Z"


def change_it_all():
    """8.0–11.0: the photo shrinks into a tilted video card with a square avatar and a square red button that an
    arrow pointer clicks; the card's corners round off. The pack's «CUSTOMIZE» promo word is a plain «SUBSCRIBE»."""
    dur = 3.0
    t = _t("tarjeta-video-cuadrada", "Tarjeta de video inclinada con avatar cuadrado y botón rojo",
           "Tilted video card with a square avatar and a red button", 18380, dur, "redes",
           ["tarjeta", "video", "suscribirse", "foto"])
    s = P(t, dur)
    cx, cy, rot, pw, ph = 961, 456, -4.95, 1321, 560
    full = 1920.0 / pw

    def fn(fr):
        q = k(fr, 7, 13)
        return (960 + (cx - 960) * q, 540 + (cy - 540) * q, full + (1 - full) * q, rot * q,
                min(1.0, fr / 2.0) * (1 - k(fr, dur * 25 - 4, 4)))
    rig = Rig(fn, 60)
    bar = 194
    ccx, ccy = rot_pt(cx, cy + bar / 2, rot, cx, cy)
    s.part("Tarjeta", card_layers(), rig, ccx, ccy, pw, ph + bar, radius=6, op=lambda fr: k(fr, 9, 4))
    s.photo("fx-woman-02", rig, cx, cy, pw, ph, label="Tu video")
    a = 14
    s.part("Avatar (borde)", solid(WHITE), rig, 566, 870, 130, 130, op=lambda fr: k(fr, a, 4))
    s.photo("fx-woman-02", rig, 566, 870, 126, 126, label="Tu foto de perfil", name="Foto de perfil",
            op=lambda fr: k(fr, a, 4), reuse="p1")
    s.word("Change it all", rig, 652, 850, 40, SLAB, 700, INK, "Canal", x1=1003, op=lambda fr: k(fr, a + 1, 5),
           slide=lambda fr: (-50 * (1 - k(fr, a + 1, 8)), 0))
    s.check(rig, 1039, 830, 36, op=lambda fr: k(fr, a + 4, 4))
    s.thumb(rig, 1140, 823, 53, None, op=lambda fr: pop(fr, a + 5, 5))
    s.thumb(rig, 1222, 814, 53, None, op=lambda fr: pop(fr, a + 6, 5), down=True, name="No me gusta")
    click = 66
    grow = lambda fr: k(fr, a + 3, 7)  # noqa: E731
    s.part("Botón (gris)", solid(PILL_GREY), rig, 1408, 797, 274, 94, radius=6, wmul=grow,
           op=lambda fr: on(fr, click))
    s.part("Botón", solid(RED), rig, 1408, 797, 274, 94, radius=6, wmul=grow, op=lambda fr: 1 - on(fr, click))
    s.word("SUBSCRIBE", rig, 1408, 797, 34, LATO, 400, WHITE, "Botón (texto)", align="center", x1=1408 + 110,
           op=lambda fr: k(fr, a + 8, 3) * (1 - on(fr, click)))
    s.word("SUBSCRIBED", rig, 1408, 797, 34, LATO, 400, "#333333", "Botón (suscrito)", align="center",
           x1=1408 + 120, op=lambda fr: on(fr, click))
    path = pts((24, 1900, 1000), (36, 1440, 812), (60, 1442, 814), (72, 1446, 816))

    def at(fr):
        x, y = path(fr)
        return x, y, math.sin(math.pi * lin(fr, click - 2, 5)), k(fr, 24, 3)

    def g(fr, u):
        x, y, press, op = at(fr)
        sc = 1 - 0.12 * press
        return x + 33 * sc, y + 50 * sc, 66 * sc, 100 * sc, 0.0, op
    s.obj("Cursor", filled_line(WHITE, INK, 4), g, path=ARROW)
    return t


def barbara_ellis():
    items = [it_avatar("portrait-08", 499, 950, 157, at=12),
             it_name("Barbara Ellis", 619, 942, cap=41, at=13, x1=982),
             lambda s, rig: s.word("Fashion channel", rig, 619, 982, 28, LATO, 400, "#333333", "Texto",
                                   op=lambda fr: k(fr, 15, 5), x1=900),
             it_sub(1219, 950, 319, 74, 30, at=14, cap=30),
             it_bell(1488, 950, 54, at=16)]
    path = pts((14, 1560, 1150), (24, 1225, 975), (36, 1227, 977), (50, 1400, 1150))
    return band_card("barra-video-suscribirse", "Barra blanca abajo sobre el video: avatar, nombre y suscribirse",
                     "White bar at the bottom over the video: avatar, name and subscribe", 18381, "fx-walk-02", False,
                     254, items, [30], path, 14, 50, dur=3.0)


def robert_noel():
    return comment("comentario-sobre-video", "Comentario de una línea sobre el video",
                   "One-line comment over the video", 18382, (450, 770, 1474, 977),
                   ("man-06", (535, 857, 110), "Robert Noel", (623, 823, 802), "1 hour ago", (828, 823, 935)),
                   [("I love your videos and interviews. Great sense of humor!", 614, 863, 1390)],
                   ((642, 930, 40), ("1103", 661, 714), (798, 928), ("2", 840, 852), (914, 930, 1051)),
                   like_click=28, dur=3.0)


def leprechaun():
    def build(s, show, vis):
        w_photo(s, "man-01", 510, 808, 654, 952, vis, r=20)
        s.word("Leprechaun", STILL, 698, 857, 40, SLAB, 700, INK, "Canal", x1=1001, reveal=show)
        c = s.word("692K subscriber", STILL, 698, 908, 28, LATO, 400, "#333333", "Suscriptores", x1=960,
                   reveal=show)
        c["textStyle"].update(counter=True, counterFrom=0, counterSeconds=1.0, counterCurve="easeOut")
        w_sub(s, 1184, 880, 288, 66, 22, vis, cap=26, at=6)
        s.bell(STILL, 1392, 877, 52, op=vis(1392, 877))
    path = pts((4, 1400, 1150), (12, 1186, 905), (28, 1188, 907), (40, 1300, 1150))
    return widget("canal-sobre-video", "Botón del canal sobre el video: foto, suscriptores y suscribirse",
                  "Channel button over the video: photo, subscribers and subscribe", 18383, (476, 774, 1462, 986, 40),
                  build, [22], path, 4, 40, dur=3.0)


TEMPLATES: list = [lorraine, mary_lee, diana_allen, sally_love, gail_ford, amy_taylor, jean_lewis, vivian_kim,
                   eva_atkins, christopher, katie_tina, leonard_jones, melissa, miss_patricia, nancy_lee,
                   susan_maxwell, sandra_rodney, nicole_friends, watch_later, side_open, jonathan, betty_griffin,
                   patience, paul_bailey, matthew, linda_butler, rosa_cox, sue_evans, nicole_mitchell,
                   photo_column, daniel_kevin, ariana_fox, lily_channel, vanessa_perry, jackson_stewart,
                   alexis_watson, riley_channel, julia_flores, abigail_diaz, morgan_simmons, logo_pill, logo_above,
                   logo_card_vertical, logo_card, row_like_sub_bell, subscribed_icons, dylan_smith,
                   william_robinson, like_notified, like_this_bar, subscribe_done, subscribe_tick,
                   youtube_channel, subscribe_counter, like_share_pills, share_this, thumb_counter,
                   lambda: thumb_counter(True), like_it_pill, lambda: like_it_pill(True), red_like_pill,
                   lambda: red_like_pill(True), advise_friends, lambda: advise_friends(True), round_bell,
                   round_like, round_share, round_play, column_labels, column_icons, row_icons, row_subscribe,
                   three_white, like_share, like_bell, bell_share, play_subscribe, like_sub_bell_row, like_sub_row,
                   sub_bell_row, change_it_all, barbara_ellis, robert_noel, leprechaun]
