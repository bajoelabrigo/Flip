"""Colourful channel slides, fifth TITLE set redone (2026-11-08, Jorge: «lo más parecido posible, inclusive las
transiciones; usa un logo de YouTube»): the twenty of 2300019.mp4 (960×540 at 29.97 fps, laid out at 1920×1080),
each one with the transition that brings it in in the reference (stripes, diamonds, columns of blocks, circles,
hexagons, a lightning bolt, pills, blobs), studied on 10 fps sheets. Kit de YouTube › Títulos con estilo; ids
`tit5-*` (they replace the first version, `templates_tit_e`), order 8880-. Study notes in
tienda/plantillas/estudio-2300019/NOTAS.md.

Where the reference shows the video platform's play button, the piece draws a YouTube-style play button; its
words («#YOUTUBE», «YOUTUBECHANNEL»…) are kept as the reference has them. Outside the transition shape the slide is
transparent, so the transition works over the previous clip as in the reference. Each slide plays its entrance,
holds, and leaves with its entrance backwards at 2.5× speed.
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from scene import gradient, keys, no_stroke, tanim
from templates_tit_b import Slide
from templates_tit_c import FPS, k
from templates_tit_e import Piece5, solid

WHITE = "#FFFFFF"
NAME, M, LILITA = "Bebas Neue", "Montserrat", "Lilita One"
f6._FILES[(LILITA, 400)] = "fonts.extra/fonts/lilitaone/LilitaOne-Regular.ttf"
for w, f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium"),
             (400, "Regular")):
    f6._FILES[(M, w)] = f"fonts.basic/fonts/montserrat/Montserrat-{f}.ttf"
URL = "WWW.YOURWEBSITE.COM"
YT = "#F41D4E"
DIAMOND = "M 50 0 L 100 50 L 50 100 L 0 50 Z"
TRIANGLE = "M 0 0 L 100 50 L 0 100 Z"
EXIT = 2.5


def grad(c0, c1, angle=90):
    return [gradient([(0.0, c0), (1.0, c1)], angle=angle), no_stroke()]


def ring(colour, width):
    return [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
            {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "center",
             "opacity": 1.0, "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}]


def shadow(colour, dx, dy, blur=0, alpha=1.0):
    return {"id": "shadow", "kind": "shadow", "enabled": True,
            "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()},
            "offsetX": dx, "offsetY": dy, "blur": blur, "opacity": alpha}


def fill(colour):
    return {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
            "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}


def lin(fr, at, n):
    return min(1.0, max(0.0, (fr - at) / max(1e-6, n)))


def rot_pt(x, y, deg, px=960.0, py=540.0):
    a = math.radians(deg)
    dx, dy = x - px, y - py
    return px + dx * math.cos(a) - dy * math.sin(a), py + dx * math.sin(a) + dy * math.cos(a)


def poly(points):
    """A closed path (points in 0..100) for a custom shape."""
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in points) + " Z"


def regular(n, phase=-90.0):
    return poly([(50 + 50 * math.cos(math.radians(phase + 360 * i / n)),
                  50 + 50 * math.sin(math.radians(phase + 360 * i / n))) for i in range(n)])


def sectors(spans, steps=10):
    """Pie wedges (start, end degrees) of the circle in a 100 box, as one path."""
    out = []
    for a0, a1 in spans:
        pts = [(50, 50)] + [(50 + 50 * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
                             50 + 50 * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]
        out.append(poly(pts))
    return " ".join(out)


def arc(a0, a1, steps=24):
    pts = [(50 + 50 * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
            50 + 50 * math.sin(math.radians(a0 + (a1 - a0) * i / steps))) for i in range(steps + 1)]
    return "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts)


class S(Piece5):
    """A slide with no fixed background: every element follows geom(frame, u) per frame. The entrance plays at
    its speed; the exit is the entrance backwards, EXIT times faster."""

    def __init__(self, t, dur):
        Slide.__init__(self, t, dur)
        self.tilt, self.pivot = 0.0, (960, 540)

    def frame(self, u):
        return min(u * FPS, (self.dur - u) * FPS * EXIT)

    def each(self):
        return [(u, self.frame(u)) for u in frames_of(self.dur)]

    def obj(self, name, layers, geom, kind="rectangle", path=None, radius=0.0, base=None):
        """A shape whose geom(fr, u) = (cx, cy, w, h, rot, opacity) every frame; base = (w, h) of its box (the
        corner radius is given at that size)."""
        g = [(u, geom(fr, u)) for u, fr in self.each()]
        bw, bh = base or (max(1.0, max(v[2] for _, v in g)), max(1.0, max(v[3] for _, v in g)))
        box = Box(960 - bw / 2, 540 - bh / 2, bw, bh)
        motion = [(u, {"sx": max(1e-4, v[2] / bw), "sy": max(1e-4, v[3] / bh), "dx": v[0] - 960, "dy": v[1] - 540},
                   "linear") for u, v in g]
        clip = self.t.solid(self.t.track("shape", name), "#000000", 0.0, self.dur, box, motion, radius=radius,
                            kind=kind, layers=layers)
        clip["name"] = name
        if path:
            clip["shapeStyle"]["kind"] = "custom"
            clip["shapeStyle"]["customPath"] = path
            clip["shapeStyle"]["customEvenOdd"] = False
        if any(abs(v[4]) > 1e-6 for _, v in g):
            clip["rotation"] = keys([(u, round(v[4], 3), "linear") for u, v in g])
        if any(v[5] < 0.999 for _, v in g):
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, v[5])), 4), "linear") for u, v in g])
        return clip

    def rect(self, name, layers, r, op=None, rot=None, **kw):
        """A box covering r(fr, u) = (x0, y0, x1, y1)."""
        def geom(fr, u):
            x0, y0, x1, y1 = r(fr, u)
            return ((x0 + x1) / 2, (y0 + y1) / 2, max(0.0, x1 - x0), max(0.0, y1 - y0),
                    rot(fr, u) if rot else 0.0, op(fr, u) if op else 1.0)
        return self.obj(name, layers, geom, **kw)

    def say(self, content, ink, family, weight, colour, name="Título", geom=None, align="center", layers=None,
            reveal=None, italic=False, editable=True, shift=None, op=None, rot=None):
        """A line of text at ink; geom(fr, u) = (dx, dy, scale, rot, opacity) moves it (scale about its centre).
        With a reveal, move it with shift(fr) = (dx, dy) instead (the mask stays put) and op / rot(fr, u)."""
        clip = self.text(content, ink, family, weight, colour, name, align=align, layers=layers, reveal=reveal,
                         italic=italic, editable=editable, shift=shift)
        if geom:
            self.tmove(clip, geom)
        if op:
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, op(fr, u))), 4), "linear") for u, fr in self.each()])
        if rot:
            clip["rotation"] = keys([(u, round(rot(fr, u), 3), "linear") for u, fr in self.each()])
        return clip

    def tmove(self, clip, geom):
        x, y = clip["x"]["keyframes"][0]["value"], clip["y"]["keyframes"][0]["value"]
        w, h = clip["width"]["keyframes"][0]["value"], clip["height"]["keyframes"][0]["value"]
        size = clip.get("textStyle", {}).get("pixelSize")
        xs, ys, ws, hs, sizes, rots, ops = [], [], [], [], [], [], []
        for u, fr in self.each():
            dx, dy, sc, rot, op = geom(fr, u)
            sc = max(1e-3, sc)
            xs.append((u, x + w / 2 + dx - w * sc / 2, "linear"))
            ys.append((u, y + h / 2 + dy - h * sc / 2, "linear"))
            ws.append((u, w * sc, "linear"))
            hs.append((u, h * sc, "linear"))
            sizes.append((u, (size or 0) * sc, "linear"))
            rots.append((u, round(rot, 3), "linear"))
            ops.append((u, round(max(0.0, min(1.0, op)), 4), "linear"))
        clip["x"], clip["y"], clip["width"], clip["height"] = keys(xs), keys(ys), keys(ws), keys(hs)
        if size and any(abs(v[1] - size) > 1e-3 for v in sizes):
            clip["textStyle"].setdefault("keyframes", {})["pixelSize"] = keys(sizes)
        if any(abs(v[1]) > 1e-6 for v in rots):
            clip["rotation"] = keys(rots)
        if any(v[1] < 0.999 for v in ops):
            clip["opacity"] = keys(ops)

    def about(self, ink, px, py, sc, rot=0.0):
        """(dx, dy) that put ink's centre where scaling by sc and turning by rot about (px, py) puts it."""
        cx, cy = (ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2
        nx, ny = px + (cx - px) * sc, py + (cy - py) * sc
        nx, ny = rot_pt(nx, ny, rot, px, py)
        return nx - cx, ny - cy

    def typed(self, clip, at, stagger=0.06, duration=0.05, preset="typewriter", order="forward", unit="character"):
        n = len(clip.get("textContent", "")) if unit == "character" else len(clip.get("textContent", "").split())
        lead = round(at / FPS, 3)
        clip["textStyle"]["animation"] = {
            "in": tanim(preset, duration=duration, unit=unit, stagger=stagger, ease="easeOut", delay=lead,
                        order=order),
            "out": tanim(preset, duration=duration / EXIT, unit=unit, stagger=stagger / EXIT, ease="easeIn",
                         delay=round(lead / EXIT, 3), order="backward" if order == "forward" else order)}

    # --- engine features the slides use (2026-11-08) ------------------------------------------------------------
    def d3(self, clip, rx=None, ry=None, z=None, persp=None, occlude=False):
        """A 3D pose on a clip: rx / ry(fr, u) tilt it in degrees round its horizontal / vertical axis, z(fr, u) its
        depth in px, persp the eye distance in px (the engine's 3D layer: a real flip in perspective)."""
        clip["layer3d"] = True
        for key, fn in (("rotationX", rx), ("rotationY", ry), ("positionZ", z)):
            if fn is not None:
                clip[key] = keys([(u, round(fn(fr, u), 3), "linear") for u, fr in self.each()])
        if persp is not None:
            clip["perspective"] = keys([(0.0, float(persp), "hold")])
        if occlude:
            clip["depthOcclude"] = True
        return clip

    def fx(self, clip, catalog_id, animated=None, **params):
        """Adds an effect of the catalog (gaussian_blur → "stylize.blur"…) to a clip; animated = {param: fn(fr, u)}
        keys it every frame."""
        from scene import effect
        kf = None
        if animated:
            kf = {name: keys([(u, round(fn(fr, u), 4), "linear") for u, fr in self.each()])
                  for name, fn in animated.items()}
        clip.setdefault("effects", []).append(effect(catalog_id, kf, **params))
        return clip

    def mblur(self, clip):
        """Motion blur on a clip while it moves (the project's shutter)."""
        clip["motionBlur"] = True
        return clip

    def url(self, y=1014, colour=WHITE, cx=960, at=15, dashes=False):
        clip = self.say(URL, (cx - 132, y, cx + 132, y + 14), M, 700, colour, "Web",
                        geom=lambda fr, u: (0, 0, 1, 0, k(fr, at, 6)))
        if dashes:
            for i, x in enumerate((cx - 200, cx + 160)):
                self.rect(f"Web (raya {i + 1})", solid(colour), lambda fr, u, x=x: (x, y + 6, x + 40 * k(fr, at, 9),
                                                                                       y + 9))
        return clip

    def yt(self, name, geom, w=276, h=162, red=YT, tri=WHITE, tri_at=None):
        """A play button: geom(fr, u) = (cx, cy, scale, rot, opacity); the triangle pops at frame tri_at."""
        self.obj(name, solid(red), lambda fr, u: (lambda g: (g[0], g[1], w * g[2], h * g[2], g[3], g[4]))(
            geom(fr, u)), radius=h * 0.26, base=(w, h))

        def tg(fr, u):
            cx, cy, sc, rot, op = geom(fr, u)
            p = 1.0 if tri_at is None else k(fr, tri_at, 6)
            ox, oy = rot_pt(cx + w * 0.04 * sc, cy, rot, cx, cy)
            return ox, oy, w * 0.26 * sc * p, h * 0.4 * sc * p, rot, op
        self.obj(f"{name} (play)", solid(tri), tg, path=TRIANGLE)


def _p(id, es, en, order, dur, tags=()):
    return wide(f"tit5-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:titulos-estilo", "título", "canal", "colores"] + list(tags),
                thumb_at=round(dur * 0.55, 1))


def dur_for(entrance, hold=1.4):
    return round(entrance + hold + entrance / EXIT, 1)


# --- 1. #YOUTUBE: three stripes sweep across, a red line drops and types the hashtag -----------------------------
def hashtag():
    D = dur_for(2.0)
    t = _p("hashtag", "Título: hashtag tecleado sobre amarillo", "Title: typed hashtag on yellow", 8880, D,
           ["hashtag"])
    s = S(t, D)
    red, yellow = "#E2134A", "#FDD445"
    edge = lambda fr: -1150 + 2300 * k(fr, 0, 15)  # noqa: E731

    def band(d0, th, rot=-45):
        return lambda fr, u: (960 + (edge(fr) + d0) * 0.7071, 540 + (edge(fr) + d0) * 0.7071, 6000, th, rot, 1.0)
    s.obj("Fondo", solid(yellow), band(-2000, 4000))
    chev = poly([(0, 0), (31, 0), (100, 50), (31, 100), (0, 100), (69, 50)])
    for i, cx in enumerate((520, 1260)):
        s.obj(f"Flecha {i + 1}", solid("#FDE48A"), lambda fr, u, cx=cx: (cx, 540, 700, 1240, 0, k(fr, 9, 9)),
              path=chev)
    tag = s.say("# YOUTUBE", (480, 430, 1430, 620), "Oswald", 700, red)
    s.typed(tag, 27, stagger=0.09, duration=0.04)

    def cursor(fr, u):
        if fr < 9:
            return 960, 396, 0, 8, 0, 0
        if fr < 24:
            return 960, 396 + 236 * k(fr, 12, 12), 330, 8, 0, 1
        x = 480 + 950 * lin(fr, 27, 24)
        return x + 34, 632, 68, 8, 0, 1 - k(fr, 54, 4)
    s.obj("Cursor", solid(red), cursor)
    s.say("SOCIAL MEDIA MARKETING", (650, 640, 1370, 668), NAME, 400, "#FFF3C4", "Texto",
          reveal=lambda fr: (0, 634, 1920, 720), shift=lambda fr: (0, 40 * (1 - k(fr, 54, 8))),
          op=lambda fr, u: k(fr, 54, 3))
    s.obj("Raya roja", solid(red), band(190, 380))
    s.obj("Raya blanca", solid(WHITE), band(570, 380))
    s.obj("Raya negra", solid("#111111"), band(760 + 1500, 3000))
    return t


# --- 2. GROW: a white diamond and the red background open from the centre -----------------------------------------
def grow():
    D = dur_for(1.4, 2.4)
    t = _p("rombo", "Título: rombo blanco sobre rojo", "Title: white diamond on red", 8881, D, ["rombo"])
    s = S(t, D)
    red = "#D60A4B"
    s.obj("Rombo (paso)", solid(WHITE), lambda fr, u: (960, 540, 3400 * k(fr, 0, 12), 3400 * k(fr, 0, 12), 0, 1),
          path=DIAMOND)
    s.obj("Fondo", solid(red), lambda fr, u: (960, 540, 3200 * k(fr, 3, 12), 3200 * k(fr, 3, 12), 0, 1),
          path=DIAMOND)
    zoom = lambda u: 1 + 0.14 * k(u * FPS, 75, 45)  # noqa: E731
    size = lambda fr, u: k(fr, 9, 15) * zoom(u)  # noqa: E731
    s.obj("Rombo", solid(WHITE), lambda fr, u: (960, 540, 800 * size(fr, u), 800 * size(fr, u), 0, 1),
          path=DIAMOND)

    def inside(ink, at=None, dy0=0.0):
        def g(fr, u):
            sc = size(fr, u)
            dx, dy = s.about(ink, 960, 540, sc)
            return (dx, dy + (dy0 * (1 - k(fr, at, 9)) if at is not None else 0), sc, 0,
                    k(fr, at, 4) if at is not None else min(1.0, sc * 3))
        return g
    s.say("GROW", (768, 474, 1150, 606), NAME, 400, red, geom=inside((768, 474, 1150, 606)))
    s.say("YOUR", (800, 422, 930, 462), NAME, 400, "#1B1B1B", "Texto",
          geom=inside((800, 422, 930, 462), 18, 50))
    s.say("BUSINESS", (890, 618, 1128, 658), NAME, 400, "#1B1B1B", "Texto 2",
          geom=inside((890, 618, 1128, 658), 24, -50))
    for i, (x, y) in enumerate(((1560, 170), (1600, 170), (330, 870), (370, 870))):
        s.obj(f"Raya {i + 1}", solid(WHITE), lambda fr, u, x=x, y=y: (x + 30 * k(u * FPS, 40, 60), y + 30,
                                                                      4, 70 * k(fr, 30 + (i % 2) * 3, 9), 30, 1))
    s.url(1020, WHITE, 1630, 18)
    return t


# --- 3. YOUTUBECHANNEL: columns of white blocks, a label that opens and tilts --------------------------------------
def channel_label():
    D = dur_for(2.0)
    t = _p("etiqueta", "Título: etiqueta que se abre y se inclina", "Title: label that opens and tilts", 8882, D,
           ["etiqueta"])
    s = S(t, D)
    blue = "#1747C5"
    for i in range(3):
        x0, x1 = 640 * i, 640 * i + 642

        def col(fr, u, down=(i != 1), white=False, x0=x0, x1=x1):
            e = -420 + 1920 * k(fr, i, 12)
            if down:
                return (x0, e - 420, x1, e) if white else (x0, -10, x1, e - 420)
            e2 = 1080 + 420 - 1920 * k(fr, i, 12)
            return (x0, e2, x1, e2 + 420) if white else (x0, e2 + 420, x1, 1090)
        s.rect(f"Fondo {i + 1}" if i else "Fondo", solid(blue), col)
        s.rect(f"Bloque {i + 1}", solid(WHITE), lambda fr, u, col=col: col(fr, u, white=True))
    ghost = s.say("YOUTUBECHANNEL", (-1700, 30, 4300, 1050), NAME, 400, "#2C5BD6", "Fondo (texto)", editable=False,
                  geom=lambda fr, u: (-150 * u, 0, 1, 0, k(fr, 9, 9)))
    del ghost
    for i, x in enumerate((300, 1620, 1650)):
        s.rect(f"Línea {i + 1}", solid(WHITE), lambda fr, u, x=x, i=i: (x, 0, x + 3, 1080 * k(fr, 12 + 2 * i, 9)),
               op=lambda fr, u: 1 - k(fr, 27, 9))
    tilt = lambda fr: -8 * k(fr, 27, 9)  # noqa: E731
    grow_ = lambda fr: 1 + 0.23 * k(fr, 27, 9)  # noqa: E731
    s.obj("Etiqueta", solid(WHITE), lambda fr, u: (960, 540, 780 * k(fr, 15, 9) * grow_(fr), 120 * grow_(fr),
                                                   tilt(fr), 1))
    ink = (620, 494, 1300, 586)
    s.say("YOUTUBECHANNEL", ink, NAME, 400, blue, reveal=lambda fr: (960 - 392 * k(fr, 15, 9), 0,
                                                                     960 + 392 * k(fr, 15, 9), 1080),
          geom=lambda fr, u: (*s.about(ink, 960, 540, grow_(fr), tilt(fr)), grow_(fr), tilt(fr), 1))

    def line(fr, u):
        q = k(fr, 51, 9)
        cx, cy = rot_pt(1010 + 260 * q, 640, tilt(fr))
        return cx, cy, 520 * q, 5, tilt(fr), 1
    s.obj("Línea", solid(WHITE), line)
    s.url(1012, WHITE, 960, 15, dashes=True)
    return t


# --- 4. DON'T WASTE YOUR TIME: a red band, then a circle that turns into a hexagon, a pentagon and a frame ---------
def dont_waste():
    D = dur_for(1.6)
    t = _p("no-pierdas", "Título: frase en un marco que cambia de forma", "Title: phrase in a shape-shifting frame",
           8883, D, ["marco"])
    s = S(t, D)
    red = "#E8113B"
    s.rect("Fondo", solid("#0E0E0E"), lambda fr, u: (0, -10, 1920, 1090 * k(fr, 4, 9)))
    s.rect("Banda", solid(red), lambda fr, u: (0, 1080 * k(fr, 4, 9), 1920, 1100 * k(fr, 0, 12)))
    turn = lambda fr: 0 if fr < 12 else 25 * k(fr, 12, 6) if fr < 18 else 25 - 40 * k(fr, 18, 6) if fr < 24 \
        else -15 * (1 - k(fr, 24, 12))  # noqa: E731
    s.obj("Aro", ring(red, 10), lambda fr, u: (960, 528, 156, 156, 0, 1.0 if 9 <= fr < 12 else 0.0), kind="ellipse")
    for name, sides, a, b in (("Hexágono", 6, 12, 18), ("Pentágono", 5, 18, 24)):
        s.obj(name, ring(red, 10), lambda fr, u, a=a, b=b: (960, 540, 540, 540, turn(fr), 1.0 if a <= fr < b else 0),
              path=regular(sides))
        s.obj(f"{name} (blanco)", ring(WHITE, 3), lambda fr, u, a=a, b=b: (966, 534, 560, 560, turn(fr) + 4,
                                                                           1.0 if a <= fr < b else 0),
              path=regular(sides))
    s.obj("Marco", ring(red, 10), lambda fr, u: (960, 540, 550 - 40 * (1 - k(fr, 24, 9)), 540, turn(fr),
                                                 1.0 if fr >= 24 else 0), radius=30, base=(550, 540))
    for i, line in enumerate(("D O N ' T", "W A S T E", "Y O U R", "T I M E")):
        y = 384 + 84 * i
        x1 = 1098 if len(line) >= 9 else 1040
        ink = (822, y, x1, y + 36)
        clip = s.say(line, ink, M, 800, WHITE, f"Título {i + 1}" if i else "Título", align="left",
                     geom=lambda fr, u, ink=ink: (*s.about(ink, 960, 540, 1, turn(fr)), 1, turn(fr), 1))
        s.typed(clip, 15 + 5 * i, stagger=0.03, duration=0.03)
    for i, (x, y) in enumerate(((560, 760), (1420, 300), (520, 880), (1460, 420))):
        s.obj(f"Destello {i + 1}", solid(WHITE),
              lambda fr, u, x=x, y=y, i=i: (x + 220 * lin(fr, 45 + 2 * i, 21), y - 220 * lin(fr, 45 + 2 * i, 21),
                                            260, 3, -45, k(fr, 45 + 2 * i, 4) * (1 - k(fr, 60 + 2 * i, 6))))
    s.url(1016, WHITE, 960, 18)
    return t


# --- 5. SOCIAL MEDIA MARKETING: white wedges and a yellow circle spin open; MEDIA turns into place --------------
def social_media():
    D = dur_for(1.4)
    t = _p("social-media", "Título: aro que gira sobre amarillo", "Title: spinning ring on yellow", 8884, D,
           ["círculo"])
    s = S(t, D)
    yellow, red = "#FDD248", "#E8333B"
    s.obj("Cuñas", solid(WHITE), lambda fr, u: (960, 540, 3000 * k(fr, 0, 18), 3000 * k(fr, 0, 18),
                                                200 * k(fr, 0, 18), 1), path=sectors(((0, 70), (180, 250))))
    s.obj("Fondo", solid(yellow), lambda fr, u: (960, 540, 2400 * k(fr, 0, 18), 2400 * k(fr, 0, 18), 0, 1),
          kind="ellipse")
    for i, r in enumerate((780, 880)):
        s.obj(f"Arco {i + 1}", ring(WHITE, 4), lambda fr, u, r=r, i=i: (960, 540, r, r, 140 * k(fr, 15, 21) * (1 - 2 * i),
                                                                       k(fr, 15, 3) * (1 - k(fr, 27, 9))),
              path=arc(200, 330))
    size = lambda fr: 0.42 + 0.58 * k(fr, 15, 12)  # noqa: E731
    s.obj("Aro", ring(WHITE, 12), lambda fr, u: (960, 540, 576 * size(fr), 576 * size(fr), 0, k(fr, 15, 3)),
          kind="ellipse", base=(576, 576))
    ink = (798, 486, 1122, 606)
    s.say("MEDIA", ink, NAME, 400, red, geom=lambda fr, u: (0, 0, size(fr), -60 * (1 - k(fr, 15, 12)), k(fr, 15, 3)))
    s.say("SOCIAL", (900, 420, 1020, 466), NAME, 400, WHITE, "Texto",
          geom=lambda fr, u: (0, 30 * (1 - k(fr, 24, 6)), 1, 0, k(fr, 24, 6)))
    s.say("MARKETING", (868, 624, 1052, 670), NAME, 400, WHITE, "Texto 2",
          geom=lambda fr, u: (0, -30 * (1 - k(fr, 26, 6)), 1, 0, k(fr, 26, 6)))
    return t


# --- 6. FOLLOW US: a white band comes down; a blue coin flips in --------------------------------------------------
def follow_us():
    D = dur_for(1.5)
    t = _p("seguinos", "Título: moneda azul que gira", "Title: flipping blue coin", 8885, D, ["círculo"])
    s = S(t, D)
    e = lambda fr: 1400 * k(fr, 3, 12)  # noqa: E731
    s.rect("Fondo", grad("#00D2E6", "#4A3BF0"), lambda fr, u: (0, -10, 1920, e(fr) - 320))
    s.rect("Banda", solid(WHITE), lambda fr, u: (0, e(fr) - 320, 1920, e(fr)))
    s.obj("Sombra", solid("#1E2A80", 0.35), lambda fr, u: (960, 940, 300 * k(fr, 12, 18), 26, 0, 1), kind="ellipse")
    wob = lambda fr, u: 1 - 0.05 * (0.5 + 0.5 * math.sin(2 * math.pi * u / 1.3)) * k(fr, 30, 9)  # noqa: E731
    width = lambda fr, u: 480 * k(fr, 12, 18) * wob(fr, u)  # noqa: E731
    s.obj("Moneda (canto)", solid("#0B57C8"), lambda fr, u: (960 + 14 * (1 - k(fr, 27, 6)), 540, width(fr, u) + 10,
                                                             480, 0, k(fr, 12, 2)), kind="ellipse")
    s.obj("Moneda", grad("#1E9BFF", "#1270F0"), lambda fr, u: (960, 540, width(fr, u), 480, 0, 1), kind="ellipse")
    for i, (line, w) in enumerate((("FOLLOW US", 234), ("FOR", 78), ("NEW CREATIVE", 312), ("ITEMS", 144))):
        y = 424 + 62 * i
        s.say(line, (960 - w / 2, y, 960 + w / 2, y + 44), NAME, 400, WHITE, f"Título {i + 1}" if i else "Título",
              geom=lambda fr, u: (0, 0, 1, 0, k(fr, 21, 9)))
    curves = (((520, 420), (700, 380), (860, 470), (980, 560)), ((1500, 300), (1300, 360), (1180, 520)),
              ((560, 700), (760, 760), (960, 700), (1100, 640)))
    for i, pts in enumerate(curves):
        c = s.outline(f"Trazo {i + 1}", list(pts), 3, WHITE, at=15 + 2 * i, n=9, closed=False)
        s.fade(c, lambda fr, i=i: 1 - k(fr, 27 + 2 * i, 6))
    clip = s.url(1020, WHITE, 960, 24)
    s.typed(clip, 24, stagger=0.02, duration=0.03)
    return t


# --- 7. YOUR YOUTUBE CHANNEL: white diamonds sweep across; a line becomes a frame, the words fall in, it flips -----
def your_channel():
    D = dur_for(2.1)
    t = _p("tu-canal", "Título: marco que se da vuelta y queda blanco", "Title: frame that flips to a white box",
           8886, D, ["caja"])
    s = S(t, D)
    cyan = "#0BC3E0"
    front = lambda fr: -500 + 4000 * k(fr, 0, 12)  # noqa: E731
    s.rect("Fondo", solid(cyan), lambda fr, u: (-10, -10, front(fr) - 300, 1090))
    zig = poly([(0, 0), (40, 0), (100, 25), (40, 50), (100, 75), (40, 100), (0, 100), (60, 75), (0, 50), (60, 25)])
    s.obj("Zigzag", solid("#35CFEA"), lambda fr, u: (700, 540, 640, 1400, 0, k(fr, 9, 9)), path=zig)
    for i, (dy, size) in enumerate(((0, 760), (540, 620), (1080, 760))):
        s.obj(f"Rombo {i + 1}", solid(WHITE), lambda fr, u, dy=dy, size=size, i=i: (front(fr) - 300 + 160 * (i % 2),
                                                                                 dy, size, size, 45, 1))
    flip = lambda fr: abs(math.cos(math.pi * k(fr, 51, 9)))  # noqa: E731
    after = lambda fr: k(fr, 51, 9) >= 0.5  # noqa: E731

    def line(fr, u):
        if fr < 12 or fr >= 39:
            return 960, 612, 0, 4, 0, 0
        return 960, 612, 1200 * k(fr, 12, 21) - 204 * k(fr, 33, 6), 4, 0, 1
    s.obj("Línea", solid(WHITE), line)
    s.obj("Marco", ring(WHITE, 4), lambda fr, u: (960, 549, 996, 126 * k(fr, 33, 9) * (flip(fr) if fr >= 51 else 1),
                                                  0, 0 if fr < 33 or after(fr) else 1))
    s.obj("Caja", solid(WHITE), lambda fr, u: (960, 549, 996, 126 * flip(fr), 0, 1 if after(fr) else 0))
    words = s.say("YOUR YOUTUBE CHANNEL", (500, 504, 1420, 594), NAME, 400, WHITE, "Título (paso)", editable=False,
                  geom=lambda fr, u: (0, 0, 1, 0, 1 if fr < 51 or (fr < 54 and not after(fr)) else 0))
    s.typed(words, 42, stagger=0.06, duration=0.12, preset="drop", unit="word")
    s.say("YOUR YOUTUBE CHANNEL", (500, 504, 1420, 594), NAME, 400, cyan,
          geom=lambda fr, u: (0, 0, 1, 0, 1 if after(fr) and flip(fr) > 0.4 else 0))
    s.say(URL, (830, 630, 1090, 644), M, 700, WHITE, "Web", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 57, 6)))
    return t


# --- 8. YOURCHANNEL: pills zoom out from the centre and leave a play button; the name slides out of it -------------
def logo_channel():
    D = dur_for(2.0)
    t = _p("logo-canal", "Título: botón de YouTube y nombre del canal", "Title: YouTube button and channel name", 8887,
           D, ["logo", "youtube"])
    s = S(t, D)
    grey = "#E6E2DF"
    for name, colour, at in (("Píldora (paso)", grey, -2), ("Píldora roja", YT, 2), ("Fondo", grey, 6)):
        s.obj(name, solid(colour), lambda fr, u, at=at: (960, 540, 3600 * k(fr, at, 14), 2100 * k(fr, at, 14), 0, 1),
              radius=1050, base=(3600, 2100))
    cx = lambda fr: 960 - 348 * k(fr, 33, 18)  # noqa: E731
    s.yt("Logo", lambda fr, u: (cx(fr), 540, 0.25 + 0.75 * k(fr, 0, 15), 0, 1), tri_at=21)
    s.say("YOURCHANNEL", (786, 498, 1434, 582), NAME, 400, "#2A2A2A", reveal=lambda fr: (cx(fr) + 120, 0, 1920, 1080),
          align="left", shift=lambda fr: (-560 * (1 - k(fr, 33, 18)), 0), op=lambda fr, u: k(fr, 33, 2))
    s.say("NAME SURNAME", (804, 600, 1038, 624), M, 700, "#2A2A2A", "Texto", align="left",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 45, 9)))
    s.rect("Línea", solid("#2A2A2A"), lambda fr, u: (870 + 588 * k(fr, 57, 9), 460, 870 + 588 * k(fr, 45, 9), 464))
    return t


# --- 9. CREATIVE: a white ring with purple inside grows from the top; the word straightens --------------------------
def creative():
    D = dur_for(1.6)
    t = _p("creative", "Título: palabra lila que se endereza", "Title: lilac word straightening", 8888, D, ["morado"])
    s = S(t, D)
    purple = "#6A00A0"
    s.obj("Aro (paso)", solid(WHITE), lambda fr, u: (960, -60, 3400 * k(fr, 0, 15), 3400 * k(fr, 0, 15), 0, 1),
          kind="ellipse")
    s.obj("Fondo", solid(purple), lambda fr, u: (960, -60, 3000 * k(fr, 2, 15), 3000 * k(fr, 2, 15), 0, 1),
          kind="ellipse")
    s.say("PROFESSIONALLY", (-3600, 60, 2300, 1080), NAME, 400, "#7A1AB4", "Fondo (texto)", editable=False,
          geom=lambda fr, u: (-120 * u, 0, 1, 0, k(fr, 15, 9)))
    ink = (492, 402, 1428, 606)
    turn = lambda fr: -12 * (1 - k(fr, 3, 15))  # noqa: E731
    s.say("CREATIVE", ink, NAME, 400, "#D6B8FF",
          geom=lambda fr, u: (*s.about(ink, 960, 540, 1, turn(fr)), 1, turn(fr), k(fr, 0, 6)))
    s.obj("Corte", solid(WHITE), lambda fr, u: (rot_pt(492 + 936 * lin(fr, 6, 30), 612, turn(fr))[0],
                                                rot_pt(492 + 936 * lin(fr, 6, 30), 612, turn(fr))[1], 90, 5, turn(fr),
                                                k(fr, 3, 3) * (1 - k(fr, 36, 3))))
    s.say("PROFESSIONALLY DESIGNED", (630, 630, 1296, 670), NAME, 400, WHITE, "Texto",
          reveal=lambda fr: (0, 620, 1920, 1080), shift=lambda fr: (0, -44 * (1 - k(fr, 39, 9))),
          op=lambda fr, u: k(fr, 39, 2))
    s.url(1020, WHITE, 960, 24)
    return t


# --- 10. LIVESTREAM: a white band rises; two brackets close a frame; the group tilts -------------------------------
def livestream():
    D = dur_for(2.4)
    t = _p("directo", "Título: transmisión en vivo que se inclina", "Title: livestream that tilts", 8889, D,
           ["directo", "youtube"])
    s = S(t, D)
    e = lambda fr: 1080 - 1520 * k(fr, 3, 12)  # noqa: E731
    s.rect("Fondo", grad("#1E36E8", "#00D9A5", 225), lambda fr, u: (0, e(fr) + 420, 1920, 1090))
    s.rect("Banda", solid(WHITE), lambda fr, u: (0, e(fr), 1920, e(fr) + 420))
    tilt = lambda fr: -8 * k(fr, 57, 12)  # noqa: E731

    def follow(x, y, w, h, fr, extra=(0, 0)):
        cx, cy = rot_pt(x + extra[0], y + extra[1], tilt(fr))
        return cx, cy, w, h, tilt(fr), 1
    s.obj("Marco (izquierda)", ring(WHITE, 5), lambda fr, u: (*follow(960, 540, 864, 180, fr,
                                                                    (-220 * (1 - k(fr, 9, 9)), 30 * (1 - k(fr, 9, 9))))[:4],
                                                             tilt(fr), k(fr, 9, 3)),
          path="M 50 0 L 0 0 L 0 100 L 60 100")
    s.obj("Marco (derecha)", ring(WHITE, 5), lambda fr, u: (*follow(960, 540, 864, 180, fr,
                                                                   (220 * (1 - k(fr, 9, 9)), -30 * (1 - k(fr, 9, 9))))[:4],
                                                            tilt(fr), k(fr, 9, 3)),
          path="M 40 0 L 100 0 L 100 100 L 50 100")
    ink = (582, 480, 1344, 600)
    s.say("LIVESTREAM", ink, NAME, 400, WHITE, reveal=lambda fr: (0, 452, 1920, 628),
          shift=lambda fr: (0, 120 * (1 - k(fr, 18, 9))), op=lambda fr, u: k(fr, 18, 2), rot=lambda fr, u: tilt(fr))
    s.obj("Etiqueta", solid(WHITE), lambda fr, u: (*follow(1020, 414, 420 * k(fr, 30, 6), 46, fr)[:4], tilt(fr), 1))
    tag = (850, 400, 1190, 428)
    lab = s.say("Y O U T U B E", tag, M, 800, "#1E36E8", "Texto",
                geom=lambda fr, u: (*s.about(tag, 960, 540, 1, tilt(fr)), 1, tilt(fr), 1))
    s.typed(lab, 33, stagger=0.04, duration=0.03)
    pm = (1218, 636, 1392, 664)
    s.say("10:30PM", pm, M, 800, WHITE, "Texto 2",
          geom=lambda fr, u: (*s.about(pm, 960, 540, 1, tilt(fr)), 1, tilt(fr), k(fr, 42, 6)))
    return t


# --- 11. #YOUTUBECHANNEL / LIKE / SHARE: circles open from the centre; a purple tag rolls its words ---------------
def share_tag():
    D = dur_for(1.4, 3.0)
    t = _p("compartir", "Título: etiqueta morada que cambia de palabra", "Title: purple tag changing words", 8890, D,
           ["etiqueta", "youtube"])
    s = S(t, D)
    yellow, purple = "#FFD400", "#A100B8"
    s.obj("Aro (paso)", ring(WHITE, 240), lambda fr, u: (960, 540, 2600 * k(fr, 0, 12), 2600 * k(fr, 0, 12), 0, 1),
          kind="ellipse", base=(2600, 2600))
    s.obj("Fondo", solid(yellow), lambda fr, u: (960, 540, 2400 * k(fr, 4, 12), 2400 * k(fr, 4, 12), 0, 1),
          kind="ellipse")
    s.obj("Aro claro", ring("#FFDF4A", 160), lambda fr, u: (960, 540, 1560 * k(fr, 8, 12), 1560 * k(fr, 8, 12), 0, 1),
          kind="ellipse", base=(1560, 1560))
    s.obj("Sombra", solid("#B08A00", 0.35), lambda fr, u: (960, 880, 640 * k(fr, 21, 9), 26, 0, 1), kind="ellipse")
    for i, (w, h) in enumerate(((3, 900), (1100, 3))):
        s.obj(f"Mira {i + 1}", solid(WHITE), lambda fr, u, w=w, h=h: (960, 540, w * (k(fr, 21, 6) if w > 3 else 1),
                                                                     h * (k(fr, 21, 6) if h > 3 else 1), -8,
                                                                     1 - k(fr, 30, 6)))
    size = lambda fr: 0.3 + 0.7 * k(fr, 21, 9)  # noqa: E731
    s.obj("Etiqueta (lado)", solid("#6E0080"), lambda fr, u: (948, 556, 762 * size(fr), 112 * size(fr), -8,
                                                             k(fr, 18, 3)))
    s.obj("Etiqueta", solid(purple), lambda fr, u: (960, 540, 762 * size(fr), 112 * size(fr), -8, k(fr, 18, 3)))
    words = ((0.0, "#YOUTUBECHANNEL"), (1.6, "LIKE"), (2.3, "SHARE"), (3.4, "LIKE"))
    for i, (start, word) in enumerate(words):
        end = words[i + 1][0] if i + 1 < len(words) else 99
        ink = (700, 506, 1220, 574) if i == 0 else (880, 506, 1040, 574)

        def op(fr, u, start=start, end=end, i=i):
            on = min(1.0, max(0.0, (u - start) / 0.1)) if i else 1.0
            off = 1 - min(1.0, max(0.0, (u - end) / 0.1))
            return on * off * k(fr, 27, 3)
        s.say(word, ink, NAME, 400, WHITE, ["Título", "Texto", "Texto 2", "Texto 3"][i], op=op,
              rot=lambda fr, u: -8)
    return t


# --- 12. FREE SUPPORT: rows of blocks slide across; the words drift left -------------------------------------------
def free_support():
    D = dur_for(1.6, 1.8)
    t = _p("soporte", "Título: filas de bloques y banda", "Title: rows of blocks and a band", 8891, D, ["banda"])
    s = S(t, D)
    purple, band = "#37217F", "#56459B"
    for i in range(3):
        y0, y1 = 360 * i, 360 * i + 362
        right = i == 1

        def row(fr, u, white=False, y0=y0, y1=y1, right=right, i=i):
            q = k(fr, 2 * i, 14)
            if right:
                e = -600 + 3120 * q
                return (e - 600, y0, e, y1) if white else (-10, y0, e - 600, y1)
            e = 2520 - 3120 * q
            return (e, y0, e + 600, y1) if white else (e + 600, y0, 1930, y1)
        s.rect(f"Fondo {i + 1}" if i else "Fondo", solid(band if i == 1 else purple), row)
        s.rect(f"Bloque {i + 1}", solid(WHITE), lambda fr, u, row=row: row(fr, u, True))
    s.say("FOOT", (-200, 40, 2200, 1040), NAME, 400, "#3C2687", "Fondo (texto)", editable=False,
          geom=lambda fr, u: (-80 * u, 0, 1, 0, 0.6 * k(fr, 12, 9)))
    drift = lambda u: 120 - 170 * u  # noqa: E731
    s.say("BY PROJECT AUTHOR", (504, 540, 1578, 648), NAME, 400, WHITE,
          geom=lambda fr, u: (drift(u), 0, 1, 0, 1 if fr >= 6 else 0))
    s.say("FREE SUPPORT", (516, 462, 960, 516), NAME, 400, WHITE, "Texto",
          geom=lambda fr, u: (drift(u), 40 * (1 - k(fr, 18, 6)), 1, 0, k(fr, 18, 6)))
    for i, (x0, x1, y) in enumerate(((0, 1900, 762), (1000, 1880, 1000))):
        s.rect(f"Línea {i + 1}", solid(WHITE, 0.7), lambda fr, u, x0=x0, x1=x1, y=y: (x1 - (x1 - x0) * k(fr, 12, 12)
                                                                                        - 60 * u, y,
                                                                                        x1 - 60 * u, y + 3))
    s.url(1014, WHITE, 1680, 24)
    return t


# --- 13. VIDEO TUTORIAL INCLUDED: a white hexagon and the gradient open turning; the letters pop -------------------
def tutorial():
    D = dur_for(1.6)
    t = _p("tutorial", "Título: tutorial que salta letra por letra", "Title: tutorial popping letter by letter",
           8892, D, ["tutorial"])
    s = S(t, D)
    hexa = regular(6, 0)
    s.obj("Hexágono (paso)", solid(WHITE), lambda fr, u: (960, 540, 3000 * k(fr, 0, 15), 3000 * k(fr, 0, 15),
                                                          30 * k(fr, 0, 15), 1), path=hexa)
    s.obj("Fondo", grad("#C300FF", "#4A2BFF", 135), lambda fr, u: (960, 540, 2900 * k(fr, 3, 15), 2900 * k(fr, 3, 15),
                                                                  20 * k(fr, 3, 15), 1), path=hexa)
    mint, pink = "#5BF0C9", "#FF6AD5"
    turn = lambda fr: -10 * (1 - k(fr, 18, 18))  # noqa: E731
    for name, text, ink, colour, edge, at in (("Texto", "VIDEO", (708, 420, 1008, 510), mint, "#1F8E8A", 27),
                                              ("Título", "TUTORIAL", (648, 528, 1278, 648), mint, "#1F8E8A", 18),
                                              ("Texto 2", "INCLUDED", (924, 660, 1272, 720), pink, "#9A1E8C", 30)):
        c = s.say(text, ink, LILITA, 400, colour, name, layers=[shadow(edge, 4, 6), fill(colour)],
                  geom=lambda fr, u, ink=ink: (*s.about(ink, 960, 560, 1, turn(fr)), 1, turn(fr), 1))
        s.typed(c, at, stagger=0.04, duration=0.15, preset="pop")
    for i, (x, y) in enumerate(((1170, 540), (830, 410))):
        for j in range(6):
            a = math.radians(60 * j)
            s.obj(f"Chispa {i + 1}.{j + 1}", solid(WHITE),
                  lambda fr, u, x=x, y=y, a=a, i=i: (x + math.cos(a) * 40 * k(fr, 27 + 3 * i, 6),
                                                     y + math.sin(a) * 40 * k(fr, 27 + 3 * i, 6), 22, 3, math.degrees(a),
                                                     k(fr, 27 + 3 * i, 2) * (1 - k(fr, 30 + 3 * i, 4))))
    pts = [(960 + 520 * math.cos(math.radians(a)), 560 + 240 * math.sin(math.radians(a))) for a in range(110, 380, 15)]
    c = s.outline("Trazo", pts, 3, WHITE, at=36, n=12, closed=False)
    s.fade(c, lambda fr: 1 - k(fr, 48, 9))
    return t


# --- 14. THIS SUMMER: a lightning bolt opens the navy background; SUMMER falls in ---------------------------------
def summer():
    D = dur_for(2.2)
    t = _p("verano", "Título: rayo y palabra que cae", "Title: lightning bolt and a falling word", 8893, D,
           ["verano"])
    s = S(t, D)
    bolt = poly([(30, 0), (100, 0), (62, 42), (88, 42), (22, 100), (42, 56), (12, 56)])
    s.obj("Rayo (paso)", solid(WHITE), lambda fr, u: (960, 540, 11000 * k(fr, 0, 15), 11000 * k(fr, 0, 15), 0, 1),
          path=bolt)
    s.obj("Rayo morado", solid("#8A2BFF"), lambda fr, u: (960, 540, 10400 * k(fr, 2, 15), 10400 * k(fr, 2, 15), 0, 1),
          path=bolt)
    s.obj("Fondo", grad("#2A3277", "#141B5C"), lambda fr, u: (960, 540, 10000 * k(fr, 4, 15), 10000 * k(fr, 4, 15), 0, 1),
          path=bolt)
    cyan = "#3CCDF5"
    grow_ = lambda fr: 0.7 + 0.3 * k(fr, 36, 30)  # noqa: E731
    ink = (594, 480, 1320, 648)
    s.say("SUMMER", ink, NAME, 400, cyan,
          geom=lambda fr, u: (*(lambda d: (d[0], d[1] - 520 * (1 - k(fr, 9, 12))))(s.about(ink, 960, 560, grow_(fr))),
                              grow_(fr), 10 * (1 - k(fr, 9, 15)), k(fr, 9, 3)))
    this = (678, 378, 912, 468)
    s.say("THIS", this, NAME, 400, cyan, "Texto",
          geom=lambda fr, u: (*s.about(this, 960, 560, grow_(fr)), grow_(fr), 0, k(fr, 18, 6)))
    aug = (1020, 660, 1314, 708)
    s.say("AUGUST 10", aug, NAME, 400, WHITE, "Texto 2",
          geom=lambda fr, u: (*(lambda d: (d[0] + 300 * (1 - k(fr, 36, 6)), d[1]))(s.about(aug, 960, 560, grow_(fr))),
                              grow_(fr), 0, k(fr, 36, 4)))
    for i, (y, w) in enumerate(((694, 700), (704, 300))):
        s.rect(f"Línea {i + 1}", solid(WHITE), lambda fr, u, y=y, w=w, i=i: (
            400 + 1600 * k(fr, 42 + 3 * i, 21), y, 400 + 1600 * k(fr, 36 + 3 * i, 18), y + 3))
    for j in range(10):
        a = math.radians(200 + 14 * j)
        s.obj(f"Chispa {j + 1}", solid("#9FB4FF"), lambda fr, u, a=a, j=j: (
            960 + math.cos(a) * 260 * k(fr, 24, 12), 640 - math.sin(a) * 120 * k(fr, 24, 12), 4, 4, 0,
            k(fr, 24, 3) * (1 - k(fr, 33, 9))), kind="ellipse")
    return t


# --- 15. YOURCHANNELNAME: red arcs spin, a black circle opens; a red drop bounces into a play button ------------
def logo_dark():
    D = dur_for(2.4)
    t = _p("logo-negro", "Título: botón de YouTube sobre negro", "Title: YouTube button on black", 8894, D,
           ["logo", "youtube"])
    s = S(t, D)
    red = "#DC0A50"
    s.obj("Rojo (paso)", solid(red), lambda fr, u: (960, 540, 2400 * k(fr, 0, 12), 2400 * k(fr, 0, 12), 0, 1),
          kind="ellipse")
    for i, r in enumerate((900, 1300, 1700)):
        s.obj(f"Arco {i + 1}", ring(WHITE if i != 1 else "#1E2A6A", 40),
              lambda fr, u, r=r, i=i: (960, 540, r * k(fr, 0, 12), r * k(fr, 0, 12), 240 * k(fr, 0, 15) * (1 - 2 * (i % 2)),
                                       1 - k(fr, 12, 3)), path=arc(0, 160), base=(r, r))
    s.obj("Fondo", solid("#141414"), lambda fr, u: (960, 540, 2400 * k(fr, 9, 12), 2400 * k(fr, 9, 12), 0, 1),
          kind="ellipse")

    def drop(fr):
        if fr < 18:
            return 540
        if fr < 30:
            return 540 - 270 * math.sin(math.pi * lin(fr, 18, 12))
        return 540
    cx = lambda fr: 960 - 372 * k(fr, 54, 15)  # noqa: E731
    s.yt("Logo", lambda fr, u: (cx(fr), drop(fr) - 9, (0.3 + 0.57 * k(fr, 18, 6)), 0, k(fr, 18, 3)), w=276, h=186,
         red=red, tri_at=39)
    s.rect("Línea", solid(WHITE), lambda fr, u: (1100 + 600 * k(fr, 60, 9), 600, 1100 + 600 * k(fr, 45, 9), 603))
    s.say("YOURCHANNELNAME", (708, 510, 1470, 570), M, 500, WHITE, align="left",
          reveal=lambda fr: (cx(fr) + 120, 0, 1920, 1080), shift=lambda fr: (-620 * (1 - k(fr, 54, 15)), 0),
          op=lambda fr, u: k(fr, 54, 2))
    s.url(1020, WHITE, 960, 21)
    return t


# --- 16. CONDENSED: purple and white blobs sweep across; the word types itself and drifts left --------------------
def condensed():
    D = dur_for(1.6)
    t = _p("condensada", "Título: letra condensada que se escribe", "Title: condensed type writing itself", 8895, D,
           ["condensada"])
    s = S(t, D)
    violet = "#4B00D4"
    e = lambda fr: -300 + 2700 * k(fr, 0, 12)  # noqa: E731
    s.rect("Fondo", solid(violet), lambda fr, u: (-10, -10, e(fr) - 500, 1090))
    s.obj("Mancha", solid(violet), lambda fr, u: (e(fr) - 500, 540, 900, 1700, 8, 1), radius=450, base=(900, 1700))
    s.obj("Mancha blanca", solid(WHITE), lambda fr, u: (e(fr) + 140, 380, 560, 1300, 8, 1), radius=280,
          base=(560, 1300))
    s.obj("Sombra", solid("#4300BC"), lambda fr, u: (960, 540, 1920, 1080, 0, k(fr, 9, 6)),
          path=poly([(0, 20), (60, 100), (0, 100)]))
    drift = lambda fr: 230 * (1 - k(fr, 6, 66))  # noqa: E731
    g = lambda at: lambda fr, u: (drift(fr), 0, 1, 0, k(fr, at, 3))  # noqa: E731
    c = s.say("CONDENSED", (222, 576, 1080, 720), NAME, 400, WHITE, align="left", geom=g(6))
    s.typed(c, 6, stagger=0.06, duration=0.03)
    s.say("HELVETICA BLACK", (222, 480, 924, 558), NAME, 400, WHITE, "Texto", align="left",
          geom=lambda fr, u: (drift(fr), 30 * (1 - k(fr, 21, 6)), 1, 0, k(fr, 21, 6)))
    s.rect("Subrayado", solid("#1BC8F6"), lambda fr, u: (210 + drift(fr), 732, 210 + drift(fr) + 990 * k(fr, 12, 21),
                                                         746))
    s.say("PROFESSIONAL ANIMATED TITLES", (222, 774, 960, 806), M, 600, WHITE, "Texto 2", align="left",
          geom=lambda fr, u: (drift(fr), 0, 1, 0, k(fr, 33, 6)))
    for i, (y, x0) in enumerate(((470, 1000), (764, 1100))):
        s.rect(f"Línea {i + 1}", solid(WHITE), lambda fr, u, y=y, x0=x0, i=i: (
            x0 - 700 * k(fr, 9 + 3 * i, 30), y, x0 + 300 - 900 * k(fr, 15 + 3 * i, 27), y + 3))
    s.url(1014, WHITE, 1640, 24)
    s.rect("Web (línea)", solid(WHITE), lambda fr, u: (1520 + 380 * (1 - k(fr, 24, 9)), 1004, 1900, 1006))
    return t


# --- 17. DYNAMIC CREATIVE STYLISH: orange blocks, a double frame that straightens ---------------------------------
def dynamic():
    D = dur_for(1.8)
    t = _p("dinamico", "Título: marco naranja doble que se endereza", "Title: double orange frame straightening",
           8896, D, ["marco"])
    s = S(t, D)
    orange = "#FFA800"
    for i in range(3):
        x0, x1 = 640 * i, 640 * i + 642

        def col(fr, u, white=False, x0=x0, x1=x1, i=i):
            down = i != 1
            e = -420 + 1920 * k(fr, i, 12)
            if down:
                return (x0, e - 420, x1, e) if white else (x0, -10, x1, e - 420)
            e2 = 1500 - 1920 * k(fr, i, 12)
            return (x0, e2, x1, e2 + 420) if white else (x0, e2 + 420, x1, 1090)
        s.rect(f"Fondo {i + 1}" if i else "Fondo", solid("#0E0E0E"), col)
        s.rect(f"Bloque {i + 1}", solid(orange), lambda fr, u, col=col: col(fr, u, True))
    turn = lambda fr: -9 * (1 - k(fr, 12, 24))  # noqa: E731
    size = lambda fr: 0.7 + 0.3 * k(fr, 12, 24)  # noqa: E731
    s.obj("Marco", ring(orange, 6), lambda fr, u: (960, 540, 732 * size(fr), 408 * size(fr), turn(fr),
                                                   k(fr, 12, 3)), base=(732, 408))
    s.obj("Marco 2", ring(orange, 4), lambda fr, u: (960 + 14 * (1 - k(fr, 30, 12)), 540 + 12 * (1 - k(fr, 30, 12)),
                                                     732 * size(fr), 408 * size(fr), turn(fr) + 3 * (1 - k(fr, 30, 12)),
                                                     k(fr, 15, 3) * (1 - k(fr, 42, 6))), base=(732, 408))
    for i, (line, w) in enumerate((("D Y N A M I C", 370), ("C R E A T I V E", 400), ("S T Y L I S H", 370))):
        y = 418 + 102 * i
        ink = (960 - w / 2, y, 960 + w / 2, y + 40)
        c = s.say(line, ink, M, 800, WHITE, f"Título {i + 1}" if i else "Título",
                  geom=lambda fr, u, ink=ink: (*s.about(ink, 960, 540, size(fr), turn(fr)), size(fr), turn(fr), 1))
        s.typed(c, 24 + 3 * i, stagger=0.02, duration=0.05, preset="fade")
    s.url(1016, WHITE, 960, 30)
    return t


# --- 18. LIKE SHARE SUBSCRIBE: white and magenta bars sweep in; blue blocks fall and stack ------------------------
def stack():
    D = dur_for(1.6)
    t = _p("pila", "Título: like, share, subscribe en bloques que caen", "Title: falling like, share, subscribe blocks",
           8897, D, ["bloques", "suscribirse", "youtube"])
    s = S(t, D)
    e = lambda fr: -300 + 2500 * k(fr, 0, 15)  # noqa: E731
    s.rect("Fondo", grad("#D61CF6", "#7C00A8"), lambda fr, u: (-10, -10, e(fr) - 300, 1090))
    s.rect("Barra", solid(WHITE), lambda fr, u: (e(fr) - 300, -10, e(fr), 1090))
    for i, (text, rect, at) in enumerate((("SUBSCRIBE", (600, 540, 1290, 858), 12),
                                          ("SHARE", (720, 408, 1110, 570), 18), ("LIKE", (768, 252, 1032, 420), 24))):
        x0, y0, x1, y1 = rect
        cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0

        def fall(fr, at=at):
            q = lin(fr, at, 7)
            bounce = 18 * math.sin(math.pi * lin(fr, at + 7, 4)) if fr > at + 7 else 0
            return -900 * (1 - q) ** 2 - bounce, -16 * (1 - k(fr, at, 9)), 1.0 if fr >= at else 0.0
        s.obj(f"Sombra {i + 1}", solid("#3A0060", 0.35), lambda fr, u, cx=cx, y1=y1, w=w, at=at: (
            cx + 40, y1 + 14, w * 0.9 * k(fr, at + 4, 4), 20, 0, 1), kind="ellipse")
        s.obj(f"Bloque {i + 1} (lado)", solid("#0B4FC0"), lambda fr, u, cx=cx, cy=cy, w=w, h=h, fall=fall: (
            cx + 18, cy + fall(fr)[0] + 14, w, h, fall(fr)[1], fall(fr)[2]))
        s.obj(f"Bloque {i + 1}", grad("#3AA8FF", "#1468F0"), lambda fr, u, cx=cx, cy=cy, w=w, h=h, fall=fall: (
            cx, cy + fall(fr)[0], w, h, fall(fr)[1], fall(fr)[2]))
        ink = (x0 + 40, y0 + h * 0.2, x1 - 40, y1 - h * 0.2)
        s.say(text, ink, NAME, 400, WHITE, ["Título", "Título 2", "Título 3"][i],
              geom=lambda fr, u, ink=ink, cx=cx, cy=cy, fall=fall: (
                  *(lambda d: (d[0], d[1] + fall(fr)[0]))(s.about(ink, cx, cy, 1, fall(fr)[1])), 1, fall(fr)[1],
                  fall(fr)[2]))
    return t


# --- 19. MODERN STYLISH CREATIVE: a red circle fills the screen, a white play button, then the red shrinks --------
def modern():
    D = dur_for(2.0)
    t = _p("moderno", "Título: botón de YouTube que se vuelve círculo", "Title: YouTube button turning into a circle",
           8898, D, ["círculo", "youtube"])
    s = S(t, D)
    red, grey = "#DC0A50", "#E5E1DE"
    for j in range(8):
        a = 45 * j
        s.obj(f"Destello {j + 1}", solid(red if j % 2 else WHITE), lambda fr, u, a=a: (
            *rot_pt(960 + 180 * k(fr, 0, 6), 540, a), 120, 4, a, 1 - k(fr, 6, 3)))
    s.rect("Fondo", solid(grey), lambda fr, u: (-10, -10, 1930, 1090), op=lambda fr, u: 1.0 if fr >= 12 else 0.0)

    def radius(fr):
        if fr < 27:
            return 1200 * k(fr, 3, 9)
        return 1200 - 930 * k(fr, 27, 12) - 60 * k(fr, 42, 6)
    flip = lambda fr: abs(math.cos(math.pi * k(fr, 45, 6)))  # noqa: E731
    s.obj("Aro (paso)", solid(WHITE), lambda fr, u: (960, 540, 2 * radius(fr) + 80, 2 * radius(fr) + 80, 0,
                                                     1.0 if fr < 15 else 0.0), kind="ellipse")
    s.obj("Círculo", solid(red), lambda fr, u: (960, 540, 2 * radius(fr) * (flip(fr) if fr >= 45 else 1),
                                                2 * radius(fr), 0, 1), kind="ellipse")
    show = lambda fr: 1.0 if 18 <= fr < 48 else 0.0  # noqa: E731
    s.yt("Logo", lambda fr, u: (960, 534, (k(fr, 18, 6)) * (flip(fr) if fr >= 45 else 1), 0, show(fr)), w=240, h=132,
         red=WHITE, tri=red, tri_at=27)
    for i, line in enumerate(("MODERN", "STYLISH", "CREATIVE")):
        y = 440 + 70 * i
        s.say(line, (858, y, 1062, y + 48), NAME, 400, WHITE, f"Título {i + 1}" if i else "Título",
              geom=lambda fr, u: (0, 0, 1, 0, 1.0 if fr >= 48 else 0.0))
    s.obj("Órbita", ring(red, 3), lambda fr, u: (960, 540, 500, 500, 300 * k(fr, 54, 24), k(fr, 54, 3)),
          path=arc(0, 250))
    return t


# --- 20. CHANNEL: a white band comes down; a dark square draws, turns and lets the word out -----------------------
def channel_card():
    D = dur_for(2.0)
    t = _p("canal-tarjeta", "Título: cuadro que gira y suelta la palabra", "Title: square that turns and lets the word "
           "out", 8899, D, ["marco"])
    s = S(t, D)
    e = lambda fr: 1500 * k(fr, 3, 12)  # noqa: E731
    s.rect("Fondo", grad("#7A6CFF", "#3F2DD9", 225), lambda fr, u: (-10, -10, 1930, e(fr) - 400))
    s.rect("Banda", solid(WHITE), lambda fr, u: (-10, e(fr) - 400, 1930, e(fr)))
    s.say("CHANNEL", (-900, 60, 3000, 1080), NAME, 400, "#8478FF", "Fondo (texto)", editable=False,
          geom=lambda fr, u: (-100 * u, 0, 1, 0, 0.35 * k(fr, 15, 9)))
    turn = lambda fr: -25 * k(fr, 33, 9)  # noqa: E731
    pos = lambda fr: (960 - 260 * k(fr, 33, 9), 552 + 48 * k(fr, 33, 9))  # noqa: E731
    sq = s.outline("Cuadro", [(1098, 402), (1098, 702), (810, 702), (810, 402)], 16, "#1F1B3A", at=9, n=18)
    s.tmove(sq, lambda fr, u: (pos(fr)[0] - 954, pos(fr)[1] - 552, 1, turn(fr), 1))
    s.say("CHANNEL", (720, 462, 1308, 600), NAME, 400, WHITE,
          reveal=lambda fr: ((pos(fr)[0] + 120) * (1 - k(fr, 46, 4)), 0, 1920, 1080),
          align="left", shift=lambda fr: (-520 * (1 - k(fr, 36, 12)), 0), op=lambda fr, u: k(fr, 36, 2))
    s.say("GRAPHICDESIGN", (990, 600, 1290, 622), M, 800, "#1F1B3A", "Texto", align="left",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 60, 6)))
    for i, (y, x0, x1) in enumerate(((402, 900, 1620), (630, 1290, 1782))):
        s.rect(f"Línea {i + 1}", solid(WHITE), lambda fr, u, y=y, x0=x0, x1=x1, i=i: (
            x0 + (x1 - x0) * k(fr, 54 + 3 * i, 12), y, x0 + (x1 - x0) * k(fr, 45 + 3 * i, 9), y + 3))
    return t


TEMPLATES = [hashtag, grow, channel_label, dont_waste, social_media, follow_us, your_channel, logo_channel, creative,
             livestream, share_tag, free_support, tutorial, summer, logo_dark, condensed, dynamic, stack, modern,
             channel_card]
