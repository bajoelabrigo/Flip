"""YOUTUBE PACK video 1 as Stock templates (yp1-*). See docs/plan-youtube-pack.md.

The red and black YouTube pack of «pack youtube 1.mp4» (960×540 at 30 fps, laid out at 1920×1080), every element
studied on 10 fps sheets: subscribe bars and like overlays over footage, openers with the YouTube play button, big
titles, backgrounds, end cards, simple titles, quotations, call-outs, info graphics, social media links,
transitions and three typographic openers. Grid pieces (2×2) are measured inside their quarter and scaled ×2.
Study notes in tienda/plantillas/estudio-pack-youtube-1/NOTAS.md. Order 12100-.

Overlays over footage play their clicks forward; their base (bar, buttons) leaves with its entrance backwards at
2.5×. Titles and openers play their entrance, hold, and leave with the entrance backwards at 2.5× (`S`).
"""

from __future__ import annotations

import math

import templates_llt_f as f6
from kit import Box, wide
from llt_motion import frames_of
from scene import keys
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import EXIT, S, TRIANGLE, arc, fill, lin, poly, regular, ring, rot_pt, shadow
from templates_tit_i import bg

WHITE, BLACK, RED, DARK = "#FFFFFF", "#000000", "#E50914", "#141414"
YTRED = "#E62117"
BLUE, YELLOW = "#2196F3", "#FFC107"
M, NAME, ROBOTO, POP = "Montserrat", "Bebas Neue", "Roboto", "Poppins"
for w, f in ((900, "Black"), (700, "Bold"), (500, "Medium"), (400, "Regular")):
    f6._FILES[(ROBOTO, w)] = f"fonts.basic/fonts/roboto/Roboto-{f}.ttf"
for w, f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium"),
             (400, "Regular")):
    f6._FILES[(M, w)] = f"fonts.basic/fonts/montserrat/Montserrat-{f}.ttf"
for w, f in ((900, "Black"), (800, "ExtraBold"), (700, "Bold"), (600, "SemiBold"), (500, "Medium"),
             (400, "Regular")):
    f6._FILES[(POP, w)] = f"fonts.basic/fonts/poppins/Poppins-{f}.ttf"

# Icons drawn in a 100 × 100 box.
THUMB = ("M 4 44 L 24 44 L 24 96 L 4 96 Z "
         "M 30 46 L 46 24 C 50 18 52 10 52 4 C 60 1 70 8 67 22 L 63 38 L 90 38 C 99 38 101 47 95 52 "
         "C 100 57 99 64 92 66 C 97 71 95 79 88 80 C 93 86 89 95 80 95 L 30 95 Z")
BELL = ("M 50 4 C 55 4 57 8 57 11 C 72 15 80 29 80 47 L 80 66 L 93 80 L 7 80 L 20 66 L 20 47 C 20 29 28 15 43 11 "
        "C 43 8 45 4 50 4 Z M 39 85 C 39 98 61 98 61 85 Z")
HAND = ("M 34 6 C 34 -1 46 -1 46 6 L 46 40 C 46 34 58 34 58 40 L 58 46 C 58 40 70 40 70 46 L 70 52 C 70 46 82 46 "
        "82 52 L 82 76 C 82 90 72 100 58 100 L 46 100 C 36 100 30 94 24 86 L 8 64 C 3 57 12 50 18 56 L 34 70 Z")
QUOTE = ("M 4 50 C 4 24 16 8 38 4 L 40 14 C 28 18 22 28 22 40 L 40 40 L 40 92 L 4 92 Z "
         "M 58 50 C 58 24 70 8 92 4 L 94 14 C 82 18 76 28 76 40 L 94 40 L 94 92 L 58 92 Z")


def fs(colour, edge, width):
    """A filled shape with an outline."""
    return [fill(colour), {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "center",
                           "opacity": 1.0, "paint": {"kind": "solid", "color": "#ff" + edge.lstrip("#").lower()}}]


def _p(id, es, en, order, dur, section, tags=(), thumb=None):
    return wide(f"yp1-{id}", es, en, "ytkit", dur, order=order,
                tags=[f"kit:{section}", "youtube", "rojo"] + list(tags),
                thumb_at=round(thumb if thumb is not None else dur * 0.55, 1))


def dur_for(entrance, hold=1.4):
    return round(entrance + hold + entrance / EXIT, 1)


class O(S):
    """An overlay over footage: frames run forward (its clicks); `e(fr, u)` is the frame of the entrance that
    plays backwards at EXIT× at the end, for the parts that leave."""

    def frame(self, u):
        return u * FPS

    def e(self, fr, u):
        return min(fr, (self.dur - u) * FPS * EXIT)


def footage(s, sample, name="Tu video"):
    """The footage the overlay sits on (a slot the user fills with a video)."""
    t = s.t
    return t.photo(t.track("video", name), sample, 0.0, s.dur, None, None, label="Tu video")


def avatar(s, sample, geom, ring_colour=None, ring_w=8, name="Avatar"):
    """A round photo slot; geom(fr, u) = (cx, cy, diameter, opacity)."""
    t = s.t
    g = [(u, geom(fr, u)) for u, fr in s.each()]
    D = max(1.0, max(v[2] for _, v in g))
    cx0, cy0 = g[0][1][0], g[0][1][1]
    if ring_colour:
        s.obj(f"{name} (aro)", ring(ring_colour, ring_w), lambda fr, u: (lambda v: (v[0], v[1], v[2] + ring_w,
                                                                                    v[2] + ring_w, 0, v[3]))(
            geom(fr, u)), kind="ellipse", base=(D + ring_w, D + ring_w))
    box = Box(cx0 - D / 2, cy0 - D / 2, D, D)
    motion = [(u, {"s": max(1e-4, v[2] / D), "dx": v[0] - cx0, "dy": v[1] - cy0}, "linear") for u, v in g]
    track = t.track("video", name)
    clip = t.photo(track, sample, 0.0, s.dur, box, motion, label="Tu foto")
    t.mask(track, clip, "ellipse")
    if any(v[3] < 0.999 for _, v in g):
        clip["opacity"] = keys([(u, round(max(0.0, min(1.0, v[3])), 4), "linear") for u, v in g])
    return clip


def icon(s, name, path, layers, geom):
    """An icon: geom(fr, u) = (cx, cy, w, h, rot, opacity)."""
    return s.obj(name, layers, geom, path=path)


def cursor(s, pts, name="Cursor"):
    """A hand pointer that moves through pts = [(frame, x, y), ...] (its fingertip), shown between the first and the
    last; a click (frame, ...) is drawn by `click`."""
    def at(fr):
        if fr <= pts[0][0]:
            return pts[0][1:]
        for (a, xa, ya), (b, xb, yb) in zip(pts, pts[1:]):
            if fr <= b:
                q = 0.5 - 0.5 * math.cos(math.pi * (fr - a) / max(1e-6, b - a))
                return xa + (xb - xa) * q, ya + (yb - ya) * q
        return pts[-1][1:]
    first, last = pts[0][0], pts[-1][0]
    s.obj(name, fs(WHITE, BLACK, 3), lambda fr, u: (at(fr)[0] + 6, at(fr)[1] + 26, 46, 54, 0,
                                                    1.0 if first <= fr <= last else 0.0), path=HAND)


def ripple(s, name, cx, cy, at, size=90, colour=WHITE, n=9, width=4):
    s.obj(name, ring(colour, width), lambda fr, u: (cx, cy, size * k(fr, at, n), size * k(fr, at, n), 0,
                                                    (1 - lin(fr, at, n)) if fr >= at else 0.0), kind="ellipse",
          base=(size, size))


# --- 3D pieces (the engine's 3D layers: a real turn in perspective) -----------------------------------------------
PERSP = 1600.0
# Opacity of the 3D pieces: just under 1 so the engine keeps them in track order (it depth-tests only opaque 3D
# layers, and that drops the soft edges of text and lets a face bleed through the piece riding on it).
FLAT = 0.998
BELL_BODY = ("M 50 4 C 55 4 57 8 57 11 C 72 15 80 29 80 47 L 80 66 L 93 80 L 7 80 L 20 66 L 20 47 C 20 29 28 15 43 11 "
             "C 43 8 45 4 50 4 Z")
BELL_CLAP = "M 39 78 L 61 78 L 61 85 C 61 98 39 98 39 85 Z"


def mix(c0, c1, q):
    a = [int(c0[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * q) for x, y in zip(a, b))


def turn3(ox, oy, oz, rx, ry, rot=0.0):
    """Where a point (ox, oy, oz) of a piece (from its centre, z toward the viewer) goes when the piece spins rot in
    its plane and tilts ry about its vertical axis, then rx about its horizontal one (the engine's order)."""
    a = math.radians(rot)
    ox, oy = ox * math.cos(a) - oy * math.sin(a), ox * math.sin(a) + oy * math.cos(a)
    ax, ay = math.radians(rx), math.radians(ry)
    x1 = math.cos(ay) * ox + math.sin(ay) * oz
    z1 = -math.sin(ay) * ox + math.cos(ay) * oz
    return x1, math.cos(ax) * oy - math.sin(ax) * z1, math.sin(ax) * oy + math.cos(ax) * z1


def g9(geom):
    """geom(fr, u) = (cx, cy, w, h, rot, op, rx, ry[, z]) with z filled in."""
    return lambda fr, u: (lambda v: v if len(v) == 9 else (*v, 0.0))(geom(fr, u))


def solid3d(s, name, path, face, sides, geom, depth, n=6, back=None, kind="rectangle", radius=0.0, base=None,
            slab=None, oz=0.0, persp=PERSP, evenodd=False):
    """A shape with thickness that turns in 3D: geom(fr, u) = (cx, cy, w, h, rot, op, rx, ry[, z]); depth in px at
    base size. Copies of the shape across the thickness, the sides from sides[0] (near) to sides[1] (far), drawn
    far to near: when the back turns to the viewer the copies swap ends, and the near face shows `back` (the far
    end is then the front). slab = (oy, h) in fractions of the box: a plane across the thickness shown while the
    shape stands edge-on to a turn about its vertical axis. oz shifts the piece along its own depth."""
    G = g9(geom)
    bw = (base or (100, 100))[0]
    facing = lambda v: math.cos(math.radians(v[6])) * math.cos(math.radians(v[7]))  # noqa: E731
    sgn = lambda v: 1.0 if facing(v) >= 0 else -1.0  # noqa: E731

    def place(z0, show):
        def where(fr, u):
            v = G(fr, u)
            cx, cy, w, h, rot, op, rx, ry, z = v
            sc = w / bw
            dx, dy, dz = turn3(0, 0, (sgn(v) * z0 + oz) * sc, rx, ry, rot)
            return cx + dx, cy + dy, w, h, rot, FLAT if op >= 0.5 and show(v) else 0.0, rx, ry, z + dz
        return where

    def put(nm, lay, where, kind=kind, path=path, base=base):
        clip = s.obj(nm, solid(lay) if isinstance(lay, str) else lay, lambda fr, u: where(fr, u)[:6], kind=kind,
                     path=path, radius=radius, base=base)
        if path and evenodd:
            clip["shapeStyle"]["customEvenOdd"] = True
        s.d3(clip, rx=lambda fr, u: where(fr, u)[6], ry=lambda fr, u: where(fr, u)[7], z=lambda fr, u: where(fr, u)[8],
             persp=persp)
    for i in range(n + 1):
        z0 = depth * (-0.5 + i / (n + 1))
        put(f"{name} (canto {i + 1})", mix(sides[0], sides[1], 1 - i / (n + 1)), place(z0, lambda v: True))
    if slab:
        soy, sh = slab

        def sg(fr, u):
            v = G(fr, u)
            cx, cy, w, h, rot, op, rx, ry, z = v
            sc = w / bw
            dx, dy, dz = turn3(0, soy * h, oz * sc, rx, ry, 0)
            on = FLAT if op >= 0.5 and abs(math.cos(math.radians(ry))) < 0.35 else 0.0
            return cx + dx, cy + dy, 0.9 * depth * sc, sh * h, 0, on, rx, ry + 90, z + dz
        put(f"{name} (canto)", sides[0], sg, kind="rectangle", path=None, base=(depth, 100))
    put(name, face, place(depth / 2, lambda v: facing(v) >= 0))
    put(f"{name} (atrás)", back or face, place(depth / 2, lambda v: facing(v) < 0))


def ride(s, clip, geom, centre, oz, rest):
    """Puts a text or photo clip on the front of a turning piece: geom as solid3d's, centre = the clip's (x, y) when
    the piece rests at rest = (cx, cy, w); oz = how far in front of the piece's centre."""
    G = g9(geom)
    cx0, cy0, w0 = rest
    ox, oy = centre[0] - cx0, centre[1] - cy0

    def where(fr, u):
        cx, cy, w, h, rot, op, rx, ry, z = G(fr, u)
        sc = w / w0
        dx, dy, dz = turn3(ox * sc, oy * sc, oz * sc, rx, ry, rot)
        front = math.cos(math.radians(rx)) * math.cos(math.radians(ry)) >= 0
        return cx + dx - centre[0], cy + dy - centre[1], sc, rot, min(op, FLAT) if front else 0.0, rx, ry, z + dz
    s.tmove(clip, lambda fr, u: where(fr, u)[:5])
    s.d3(clip, rx=lambda fr, u: where(fr, u)[5], ry=lambda fr, u: where(fr, u)[6], z=lambda fr, u: where(fr, u)[7],
         persp=PERSP)
    return clip


def badge3d(s, sample, geom, border=WHITE, bw=10, w=300, h=210, depth=34, sides=("#F2F2F2", "#9A9A9A"), back=None,
            name="Avatar"):
    """A photo slot on a rounded plate with thickness that turns in 3D: geom(fr, u) = (cx, cy, scale, rot, opacity,
    rx, ry); the back of the plate shows `back` (the border colour by default)."""
    W, H = w + 2 * bw, h + 2 * bw

    def plate(fr, u):
        cx, cy, sc, rot, op, rx, ry = geom(fr, u)
        return cx, cy, W * sc, H * sc, rot, op, rx, ry
    solid3d(s, f"{name} (borde)", None, border, sides, plate, depth, n=6, back=back, radius=H * 0.24, base=(W, H))
    t = s.t
    track = t.track("video", name)
    clip = t.photo(track, sample, 0.0, s.dur, Box(960 - w / 2, 540 - h / 2, w, h), None, label="Tu foto")
    t.mask(track, clip, "path", pathData=rr_path(w, h, h * 0.22))
    return ride(s, clip, plate, (960, 540), depth / 2 + 1, (960, 540, W))


# --- 1. Subscribe bar over footage: avatar, name, like, SUBSCRIBE and bell; the cursor clicks each ---------------
def subscribe_bar():
    D = 6.3
    t = _p("barra-suscribir", "Suscribirse: barra con avatar, me gusta y campana", "Subscribe: bar with avatar, like "
           "and bell", 12100, D, "elementos", ["suscribirse", "me gusta", "campana"], thumb=4.6)
    s = O(t, D)
    footage(s, "h-portrait-02")
    ent = s.e
    s.rect("Barra", solid("#F2F2F2", 0.92), lambda fr, u: (0, 1080 - 210 * k(ent(fr, u), 0, 6), 1920, 1090))
    avatar(s, "h-portrait-04", lambda fr, u: (220, 864 + 330 * (1 - k(ent(fr, u), 6, 6)), 340, 1.0),
           ring_colour="#C4001A", ring_w=8)
    c = s.say("@YOUR_CHANNEL", (416, 940, 840, 974), ROBOTO, 700, "#212121", "Canal", align="left")
    s.typed(c, 12, stagger=0.04, duration=0.06, preset="fade", order="random")
    c = s.say("Description", (390, 992, 562, 1018), ROBOTO, 400, "#555555", "Texto", align="left")
    s.typed(c, 15, stagger=0.04, duration=0.06, preset="fade", order="random")
    liked = lambda fr: k(fr, 66, 2)  # noqa: E731
    pop = lambda fr, u, at: min(1.0, k(ent(fr, u), at, 5) * (1 + 0.2 * math.sin(math.pi * lin(ent(fr, u), at, 7))))  # noqa
    for nm, colour, op in (("Me gusta", "#9E9E9E", lambda fr: 1 - liked(fr)), ("Me gusta (azul)", "#1E88E5", liked)):
        icon(s, nm, THUMB, solid(colour), lambda fr, u, op=op: (990, 972, 66 * pop(fr, u, 18), 62 * pop(fr, u, 18),
                                                                0, op(fr)))
    sub = lambda fr: k(fr, 96, 3)  # noqa: E731
    rise = lambda fr, u: 120 * (1 - k(ent(fr, u), 21, 6))  # noqa: E731
    s.rect("Suscribirse", solid(YTRED), lambda fr, u: (1134, 924 + rise(fr, u), 1634, 1024 + rise(fr, u)),
           op=lambda fr, u: 1 - sub(fr), radius=8, base=(500, 100))
    s.rect("Suscrito", solid("#3A3A3A"), lambda fr, u: (1134, 924 + rise(fr, u), 1634, 1024 + rise(fr, u)),
           op=lambda fr, u: sub(fr), radius=8, base=(500, 100))
    s.say("SUBSCRIBE", (1222, 952, 1546, 996), ROBOTO, 700, WHITE, "Botón",
          geom=lambda fr, u: (0, rise(fr, u), 1, 0, 1 - sub(fr)))
    c = s.say("SUBSCRIBED", (1196, 952, 1572, 996), ROBOTO, 700, "#C8C8C8", "Botón 2",
              geom=lambda fr, u: (0, rise(fr, u), 1, 0, 1.0 if fr >= 96 else 0.0))
    s.typed(c, 96, stagger=0.05, duration=0.08, preset="fade", order="random")
    # The bell: small in the bar, it grows above it, rings and goes back.
    big = lambda fr: k(fr, 126, 9) * (1 - k(fr, 168, 6))  # noqa: E731

    def bell(fr, u):
        q = big(fr)
        sc = pop(fr, u, 27)
        cx, cy = 1725 + (1770 - 1725) * q, 970 + (520 - 970) * q
        size = 80 + 190 * q
        swing = 16 * math.sin(2 * math.pi * (fr - 135) / 9) * k(fr, 135, 3) * (1 - k(fr, 165, 3))
        return cx, cy, size * sc, size * sc, swing, 1
    # A white bell with thickness, tipped to show its lip; the clapper is a yellow piece behind it (reference 10.2 s).
    bell3 = lambda fr, u: (*bell(fr, u), 22 * big(fr), 0)  # noqa: E731
    solid3d(s, "Campana (badajo)", BELL_CLAP, YELLOW, ("#E0A400", "#B07E00"), bell3, 14, n=3, base=(100, 100),
            oz=-4)
    solid3d(s, "Campana", BELL_BODY, WHITE, ("#E4E4E4", "#B4B4B4"), bell3, 14, n=4, base=(100, 100))
    for i, a in enumerate((-60, -40, 40, 60)):
        def arc_(fr, u, a=a):
            cx, cy, w, h, rot, _ = bell(fr, u)
            ox, oy = rot_pt(cx + 0.62 * w * math.cos(math.radians(a - 90)) * (1 if a > 0 else -1),
                            cy - 0.25 * h, 0)
            on = k(fr, 138, 3) * (1 - k(fr, 165, 3)) * (0.5 + 0.5 * math.sin(2 * math.pi * (fr - 138) / 9))
            return ox, oy, 12, 0.22 * h, a * 0.5, on
        s.obj(f"Campana (onda {i + 1})", solid(YELLOW), arc_, radius=6, base=(12, 66))
    # The like: a big blue thumb with white sides flies out of the small one, turns a whole turn about its vertical
    # axis (its back shows, mirrored) and goes back (reference 8.3-10.0 s).
    def thumb(fr, u):
        out = k(fr, 69, 9)
        back = k(fr, 108, 12)
        q = out * (1 - back)
        cx, cy = 990 + (960 - 990) * q, 972 + (370 - 972) * q
        size = 66 + 254 * q
        ry = -28 * k(fr, 69, 12) * (1 - k(fr, 108, 9)) - 332 * k(fr, 84, 27)
        return cx, cy, size, size * 0.94, -8 * q * math.sin(math.pi * lin(fr, 69, 18)), \
            1.0 if 69 <= fr < 120 else 0.0, 0, ry
    solid3d(s, "Me gusta (grande)", THUMB, "#2E9BF0", ("#F4F6F9", "#B4BEC9"), thumb, 52, n=12, back="#4BAAF4",
            base=(320, 300), slab=(0.1, 0.7))
    for i, (r, at) in enumerate(((0.62, 87), (0.55, 90))):
        sw = s.obj(f"Estela {i + 1}", ring(WHITE, 4), lambda fr, u, r=r, at=at: (
            thumb(fr, u)[0] - 30, thumb(fr, u)[1] + 30 - 40 * i, 320 * r * 2.4, 320 * r * 0.5, -8,
            k(fr, at, 3) * (1 - k(fr, at + 12, 6))), kind="ellipse", base=(320, 80))
        sw["shapeStyle"]["trimStart"] = 0.0
        knob(s, sw, "trimEnd", lambda fr, u, at=at: 15 + 35 * k(fr, at, 12))
        knob(s, sw, "trimOffset", lambda fr, u, at=at: 160 + 180 * k(fr, at, 15))
    ripple(s, "Clic 1", 990, 972, 66)
    ripple(s, "Clic 2", 1384, 974, 96, 140)
    ripple(s, "Clic 3", 1725, 970, 123)
    cursor(s, [(45, 1290, 780), (60, 1000, 990), (66, 996, 984), (78, 1180, 1000), (90, 1380, 990), (96, 1384, 984),
               (110, 1600, 1000), (123, 1730, 985), (150, 1740, 1000), (174, 1760, 1000)])
    return t


def flip_btn(s, name, rect, states, at, n=9, radius=10, shift=None, op=None, icons=()):
    """A button that flips about its horizontal axis at frame `at` (n frames) from states[0] to states[1]; each
    state = (colour, text, family, weight, text colour, ink). shift(fr, u) = (dx, dy) moves it in. A real 3D flip
    with thickness: the top comes toward the viewer, the button tilts a little while it turns (reference 14.4 s)."""
    x0, y0, x1, y1 = rect
    cx, cy, w, h = (x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0
    sh = shift or (lambda fr, u: (0, 0))
    opf = op or (lambda fr, u: 1.0)
    A = lambda fr: 180 * k(fr, at, n)  # noqa: E731
    depth = 22
    for i, (colour, text, fam, wt, tc, ink) in enumerate(states):
        nm = name if i == 0 else f"{name} ({i + 1})"

        def geom(fr, u, i=i):
            a = A(fr)
            on = opf(fr, u) * (1.0 if (a < 90) == (i == 0) else 0.0)
            return (cx + sh(fr, u)[0], cy + sh(fr, u)[1], w, h, -6 * math.sin(math.pi * lin(fr, at, n)), on,
                    -a if i == 0 else 180 - a, 0)
        solid3d(s, nm, None, colour, (mix(colour, WHITE, 0.5), mix(colour, BLACK, 0.35)), geom, depth, n=3,
                radius=radius, base=(w, h))
        c = s.say(text, ink, fam, wt, tc, f"{nm} (texto)")
        ride(s, c, geom, ((ink[0] + ink[2]) / 2, (ink[1] + ink[3]) / 2), depth / 2 + 1, (cx, cy, w))
        for j, (path, ix, iy, size, cols) in enumerate(icons):
            def ig(fr, u, geom=geom, ix=ix, iy=iy, size=size):
                bx, by, _, _, rot, on, rx, ry = geom(fr, u)
                dx, dy, dz = turn3(ix - cx, iy - cy, depth / 2 + 1, rx, ry, rot)
                return bx + dx, by + dy, size, size, rot, on, rx, ry, dz
            solid3d(s, f"{nm} (icono {j + 1})", path, cols[i], (cols[i], cols[i]), ig, 1, n=0, base=(size, size))


def burst(s, name, cx, cy, at, r0=60, r1=200, n=10, colour=RED, seed=0):
    """Little squares and rings that fly out of (cx, cy) at frame `at` and fade."""
    for j in range(n):
        a = math.radians(360 * j / n + 17 * seed)
        kind = ("rectangle", "ellipse")[j % 2]
        col = colour if j % 3 else WHITE
        s.obj(f"{name} {j + 1}", ring(col, 3), lambda fr, u, a=a, j=j: (
            cx + math.cos(a) * (r0 + (r1 - r0) * k(fr, at, 12)) * (0.8 + 0.2 * (j % 3)),
            cy + math.sin(a) * (r0 + (r1 - r0) * k(fr, at, 12)) * (0.8 + 0.2 * (j % 3)), 22, 22, 45 * (j % 2),
            k(fr, at, 2) * (1 - k(fr, at + 9, 9))), kind=kind)


ARC_R = "M 70 0 C 100 30 100 70 70 100"
ARC_L = "M 30 0 C 0 30 0 70 30 100"


# --- 2. Like overlay: a dark column at the right with avatar, like, bell and SUBSCRIBE (grid, top left) ---------
def like_column():
    D = 5.2
    t = _p("columna-suscribir", "Suscribirse: columna con avatar, me gusta y campana", "Subscribe: column with avatar, "
           "like and bell", 12101, D, "elementos", ["suscribirse", "me gusta", "campana"], thumb=3.4)
    s = O(t, D)
    footage(s, "h-interior-02")
    ent = s.e
    drop = lambda fr, u: -760 * (1 - k(ent(fr, u), 0, 12))  # noqa: E731
    s.rect("Columna", solid("#1A1A1A", 0.82), lambda fr, u: (1416, -10 + drop(fr, u), 1800, 730 + drop(fr, u)))
    avatar(s, "h-portrait-04", lambda fr, u: (1608, 150 + drop(fr, u), max(1.0, 262 * k(ent(fr, u), 6, 6)), 1.0),
           ring_colour="#D0021B", ring_w=10)
    c = s.say("YOUR_CHANNEL", (1460, 346, 1756, 374), M, 800, WHITE, "Canal",
              geom=lambda fr, u: (0, drop(fr, u), 1, 0, 1))
    s.typed(c, 12, stagger=0.03, duration=0.06, preset="fade", order="random")
    c = s.say("description", (1530, 394, 1686, 420), M, 500, "#BBBBBB", "Texto",
              geom=lambda fr, u: (0, drop(fr, u), 1, 0, 1))
    s.typed(c, 15, stagger=0.03, duration=0.06, preset="fade", order="random")
    pop = lambda fr, u, at: k(ent(fr, u), at, 6)  # noqa: E731
    liked = lambda fr: k(fr, 63, 2)  # noqa: E731
    for nm, colour, opf in (("Me gusta", "#BDBDBD", lambda fr: 1 - liked(fr)), ("Me gusta (azul)", "#2E9BF0", liked)):
        icon(s, nm, THUMB, solid(colour), lambda fr, u, opf=opf: (1536, 510 + drop(fr, u), 84 * pop(fr, u, 15),
                                                                  80 * pop(fr, u, 15), 0, opf(fr)))
    sub = lambda fr: k(fr, 93, 3)  # noqa: E731
    s.rect("Suscribirse", solid("#D0021B"), lambda fr, u: (1440, 604 + drop(fr, u), 1776, 668 + drop(fr, u)),
           op=lambda fr, u: (1 - sub(fr)) * pop(fr, u, 21), radius=4, base=(336, 64))
    s.say("SUBSCRIBE", (1500, 618, 1716, 652), M, 800, WHITE, "Botón",
          geom=lambda fr, u: (0, drop(fr, u), 1, 0, (1 - sub(fr)) * pop(fr, u, 21)))
    c = s.say("SUBSCRIBED", (1486, 618, 1730, 652), M, 800, "#9A9A9A", "Botón 2",
              geom=lambda fr, u: (0, drop(fr, u), 1, 0, 1.0 if fr >= 93 else 0.0))
    s.typed(c, 93, stagger=0.04, duration=0.08, preset="fade", order="random")
    big = lambda fr: k(fr, 117, 9)  # noqa: E731

    def bell(fr, u):
        q = big(fr)
        sw = 14 * math.sin(2 * math.pi * (fr - 126) / 8) * k(fr, 126, 3)
        size = (76 + 170 * q) * pop(fr, u, 18)
        return 1692 + (1680 - 1692) * q, 510 + drop(fr, u) + 300 * q, size, size, sw, 1
    icon(s, "Campana", BELL, fs(WHITE, "#333333", 3), bell)
    s.obj("Campana (aro)", ring(YELLOW, 8), lambda fr, u: (1692, 510 + drop(fr, u), 110, 110, 0,
                                                          k(fr, 117, 2) * (1 - k(fr, 123, 4))), kind="ellipse")
    for i, a in enumerate((-1, 1)):
        s.obj(f"Campana (onda {i + 1})", ring(YELLOW, 10), lambda fr, u, a=a: (
            bell(fr, u)[0] + a * 150, bell(fr, u)[1] - 60, 120, 160, 0, k(fr, 129, 3)), path=ARC_R if a > 0 else ARC_L)

    def thumb(fr, u):
        q = k(fr, 66, 9) * (1 - k(fr, 108, 9))
        size = 84 + 270 * q
        ry = -385 * k(fr, 68, 22) + 25 * k(fr, 90, 18)
        return 1536 + (1150 - 1536) * q, 510 + (500 - 510) * q, size, size * 0.95, 0, \
            1.0 if 66 <= fr < 117 else 0.0, 0, ry
    solid3d(s, "Me gusta (grande)", THUMB, "#2E9BF0", ("#F4F6F9", "#B4BEC9"), thumb, 58, n=12, back="#4BAAF4",
            base=(354, 336), slab=(0.1, 0.7))
    burst(s, "Chispa", 1150, 500, 90, 140, 260)
    ripple(s, "Clic 1", 1536, 510, 63)
    ripple(s, "Clic 2", 1608, 636, 93, 140)
    cursor(s, [(30, 1560, 860), (60, 1540, 520), (63, 1536, 512), (80, 1580, 640), (93, 1600, 636),
               (110, 1690, 560), (117, 1692, 512), (150, 1700, 560)])
    return t


# --- 3. Like overlay: LIKE, SUBSCRIBE and NOTIFY slide in; each one flips over when clicked (grid, top right) -----
def like_stack():
    D = 5.1
    t = _p("pila-botones", "Suscribirse: me gusta, suscribirse y notificar que se dan vuelta", "Subscribe: like, "
           "subscribe and notify buttons that flip", 12102, D, "elementos", ["suscribirse", "me gusta", "botones"],
           thumb=4.0)
    s = O(t, D)
    footage(s, "h-city-03")
    ent = s.e
    sl = lambda at: lambda fr, u: (700 * (1 - k(ent(fr, u), at, 7)), 0)  # noqa: E731
    flip_btn(s, "Me gusta", (1262, 252, 1781, 354),
             [("#F4F4F4", "LIKE", M, 800, "#1E5BB8", (1441, 279, 1597, 332)),
              ("#1E5BB8", "LIKED", M, 800, WHITE, (1425, 279, 1613, 332))], 51, 15, radius=6, shift=sl(0),
             icons=[(THUMB, x, 303, 44, ("#1E5BB8", WHITE)) for x in (1376, 1668)])
    flip_btn(s, "Suscribirse", (1262, 398, 1781, 500),
             [("#D20F0F", "SUBSCRIBE", M, 800, WHITE, (1330, 422, 1714, 476)),
              ("#3C3C3C", "SUBSCRIBED", M, 800, "#BBBBBB", (1316, 422, 1728, 476))], 75, 15, radius=6, shift=sl(3))
    flip_btn(s, "Notificar", (1262, 540, 1781, 646),
             [("#222222", "NOTIFY", M, 800, "#E6A817", (1414, 566, 1630, 620)),
              ("#E6A817", "NOTIFIED", M, 800, "#222222", (1400, 566, 1644, 620))], 96, 15, radius=6, shift=sl(9),
             icons=[(BELL, x, 593, 44, ("#E6A817", "#222222")) for x in (1376, 1668)])
    s.say("+1", (1180, 210, 1230, 240), M, 800, WHITE, "Más uno",
          geom=lambda fr, u: (0, -60 * k(fr, 63, 30), 1, 0, k(fr, 63, 4)))
    ripple(s, "Clic 1", 1550, 310, 51, 120)
    ripple(s, "Clic 2", 1550, 459, 75, 120)
    ripple(s, "Clic 3", 1550, 606, 96, 120)
    cursor(s, [(18, 1300, 200), (48, 1540, 318), (51, 1550, 310), (70, 1560, 470), (75, 1550, 459), (92, 1560, 600),
               (96, 1550, 606), (130, 1660, 760)])
    return t


# --- 4. Like overlay: a red badge with the avatar pops, spins into a blue like and then a bell (grid, bottom left)
def like_badge():
    D = 5.5
    t = _p("insignia-me-gusta", "Suscribirse: insignia que gira a me gusta y campana", "Subscribe: badge that spins "
           "into a like and a bell", 12103, D, "elementos", ["suscribirse", "me gusta", "campana"], thumb=1.4)
    s = O(t, D)
    footage(s, "h-office-02")
    ent = s.e
    grow = lambda fr: 1 + 0.25 * k(fr, 42, 6)  # noqa: E731
    # One tumble about the horizontal axis (reference 14.0-15.0 s): the badge's bottom comes forward, a red like
    # passes by, and the blue like lands; the like then turns about its vertical axis into the bell.
    A = lambda fr: 360 * k(fr, 48, 27)  # noqa: E731

    def badge(fr, u):
        sc = k(ent(fr, u), 0, 6) * (1 + 0.15 * math.sin(math.pi * lin(fr, 0, 9))) * grow(fr)
        return 960, 540, 300 * sc, 216 * sc, -10 * math.sin(math.pi * lin(fr, 48, 27)), \
            1.0 if A(fr) < 90 else 0.0, A(fr), 0
    solid3d(s, "Insignia", None, YTRED, ("#F4F4F4", "#B8B8B8"), badge, 56, n=8, radius=50, base=(300, 216))
    t_ = s.t
    track = t_.track("video", "Avatar")
    ph = t_.photo(track, "h-portrait-04", 0.0, s.dur, Box(876, 456, 168, 168), None, label="Tu foto")
    t_.mask(track, ph, "ellipse")
    ride(s, ph, badge, (960, 540), 29, (960, 540, 300))
    burst(s, "Chispa", 960, 540, 3, 120, 300)
    c = s.say("@YOUR CHANNEL", (848, 708, 1072, 730), M, 800, WHITE, "Canal",
              geom=lambda fr, u: (0, 0, 1, 0, 1 - k(fr, 42, 6)))
    s.typed(c, 6, stagger=0.03, duration=0.06, preset="fade", order="random")

    def size(fr):
        return (440 - 260 * k(fr, 76, 9)) * (1 + 1.6 * k(fr, 90, 9))

    def red_like(fr, u):
        return 960, 540, size(fr), size(fr) * 0.95, 0, 1.0 if 90 <= A(fr) < 270 else 0.0, A(fr) - 180, 0

    def like(fr, u):
        on = 1.0 if A(fr) >= 270 and fr < 105 else 0.0
        return 960, 540, size(fr), size(fr) * 0.95, 0, on, A(fr) - 360 if fr < 80 else 0, 90 * k(fr, 99, 6)
    solid3d(s, "Me gusta (rojo)", THUMB, "#E3101E", ("#F4F4F4", "#B8B8B8"), red_like, 60, n=10, base=(440, 418))
    solid3d(s, "Me gusta", THUMB, "#2E9BF0", ("#F4F6F9", "#B4BEC9"), like, 60, n=10, back="#4BAAF4",
            base=(440, 418), slab=(0.1, 0.7))
    s.obj("Clic (disco)", solid(WHITE, 0.8), lambda fr, u: (960, 540, 300 * k(fr, 87, 3), 300 * k(fr, 87, 3), 0,
                                                             1 - k(fr, 90, 4)), kind="ellipse")
    s.obj("Clic (aro)", ring(WHITE, 14), lambda fr, u: (960, 540, 480 + 80 * k(fr, 90, 15), 480 + 80 * k(fr, 90, 15),
                                                        0, k(fr, 88, 2) * (1 - k(fr, 106, 6))), kind="ellipse")

    def bell(fr, u):
        size = 440 - 290 * k(fr, 117, 12) + 170 * k(fr, 135, 6)
        sw = 14 * math.sin(2 * math.pi * (fr - 141) / 8) * k(fr, 141, 3)
        return 960, 540, size, size, sw, 1.0 if fr >= 105 else 0.0, 0, -90 * (1 - k(fr, 105, 9))
    solid3d(s, "Campana (badajo)", BELL_CLAP, YELLOW, ("#E0A400", "#B07E00"), bell, 40, n=4, base=(440, 440),
            oz=-10)
    solid3d(s, "Campana", BELL_BODY, "#2E2E2E", ("#8C8C8C", "#4A4A4A"), bell, 40, n=6, base=(440, 440),
            slab=(0.0, 0.6))
    s.obj("Campana (disco)", solid(WHITE, 0.8), lambda fr, u: (960, 540, 300 * k(fr, 132, 3), 300 * k(fr, 132, 3), 0,
                                                                1 - k(fr, 135, 4)), kind="ellipse")
    s.obj("Campana (aro)", ring(WHITE, 12), lambda fr, u: (960, 540, 380 + 60 * k(fr, 135, 12),
                                                           380 + 60 * k(fr, 135, 12), 0,
                                                           k(fr, 134, 2) * (1 - k(fr, 150, 6))), kind="ellipse")
    for i, a in enumerate((-1, 1)):
        s.obj(f"Campana (onda {i + 1})", ring(YELLOW, 16), lambda fr, u, a=a: (
            960 + a * 190, 470, 120, 220, 0, k(fr, 141, 3)), path=ARC_R if a > 0 else ARC_L)
    cursor(s, [(30, 1100, 760), (45, 1000, 600), (87, 990, 600), (132, 990, 600), (164, 1010, 640)])
    return t


# --- 5. Like overlay: like, SUBSCRIBE and bell rise at the bottom; each one clicked (grid, bottom right) ----------
def like_row():
    D = 5.4
    t = _p("fila-suscribir", "Suscribirse: me gusta, suscribirse y campana abajo", "Subscribe: like, subscribe and bell "
           "at the bottom", 12104, D, "elementos", ["suscribirse", "me gusta", "campana"], thumb=4.2)
    s = O(t, D)
    footage(s, "h-city-05")
    ent = s.e
    up = lambda at: lambda fr, u: 260 * (1 - k(ent(fr, u), at, 7))  # noqa: E731
    liked = lambda fr: k(fr, 72, 2)  # noqa: E731
    for nm, colour, opf in (("Me gusta", WHITE, lambda fr: 1 - liked(fr)), ("Me gusta (azul)", "#2E9BF0", liked)):
        icon(s, nm, THUMB, solid(colour), lambda fr, u, opf=opf: (570, 866 + up(0)(fr, u), 120, 116, 0, opf(fr)))
    flip_btn(s, "Suscribirse", (700, 812, 1222, 920),
             [("#D20F0F", "SUBSCRIBE", M, 800, WHITE, (770, 840, 1155, 894)),
              ("#333333", "SUBSCRIBED", M, 800, "#CFCFCF", (750, 840, 1175, 894))], 102, 15, radius=6,
             shift=lambda fr, u: (0, up(6)(fr, u)))
    sw = lambda fr: 16 * math.sin(2 * math.pi * (fr - 126) / 8) * k(fr, 126, 2) * (1 - k(fr, 150, 6))  # noqa: E731
    icon(s, "Campana", BELL, solid(WHITE), lambda fr, u: (1330, 862 + up(12)(fr, u), 116, 116, sw(fr), 1))
    for i, a in enumerate((-1, 1)):
        s.obj(f"Campana (onda {i + 1})", ring("#D20F0F", 10), lambda fr, u, a=a: (
            1320 + a * 80, 870, 60, 110, 0, k(fr, 126, 3)), path=ARC_R if a > 0 else ARC_L)
    s.say("+1", (628, 770, 670, 796), M, 800, WHITE, "Más uno",
          geom=lambda fr, u: (0, -40 * k(fr, 72, 24), 1, 0, k(fr, 72, 4)))
    ripple(s, "Clic 1", 580, 876, 72)
    ripple(s, "Clic 2", 954, 878, 102, 140)
    ripple(s, "Clic 3", 1320, 876, 126)
    cursor(s, [(40, 760, 700), (69, 590, 880), (72, 584, 876), (96, 950, 900), (102, 954, 880), (122, 1320, 900),
               (126, 1320, 880), (160, 1360, 940)])
    return t


# --- helpers for the openers -------------------------------------------------------------------------------------
def knob(s, clip, name, fn):
    """Keys a shape knob (cornerRadius, wiggleSize, trimEnd…) as fn(fr, u) every frame."""
    clip["shapeStyle"].setdefault("keyframes", {})[name] = keys([(u, round(fn(fr, u), 3), "linear")
                                                                 for u, fr in s.each()])


def wiggle(clip, size, detail=40.0, speed=2.0, seed=0.0):
    clip["shapeStyle"].update(wiggleSize=size, wiggleDetail=detail, wiggleSpeed=speed, wiggleSeed=seed)


def rr_path(w, h, r):
    """A rounded rectangle w × h with corner r, as a path on the 100 box."""
    rx, ry = 100 * r / w, 100 * r / h
    return (f"M {rx:.2f} 0 L {100 - rx:.2f} 0 Q 100 0 100 {ry:.2f} L 100 {100 - ry:.2f} Q 100 100 {100 - rx:.2f} 100 "
            f"L {rx:.2f} 100 Q 0 100 0 {100 - ry:.2f} L 0 {ry:.2f} Q 0 0 {rx:.2f} 0 Z")


def badge(s, sample, geom, border=RED, bw=10, w=300, h=210, name="Avatar"):
    """A photo slot in a rounded box with a border; geom(fr, u) = (cx, cy, scale, scale_x, rot, opacity) — scale_x
    narrows it as it turns (a flat 3D turn)."""
    t = s.t

    def box(fr, u):
        cx, cy, sc, sx, rot, op = geom(fr, u)
        return cx, cy, (w + 2 * bw) * sc * sx, (h + 2 * bw) * sc, rot, op
    s.obj(f"{name} (borde)", solid(border), box, radius=(h + 2 * bw) * 0.24, base=(w + 2 * bw, h + 2 * bw))
    g = [(u, geom(fr, u)) for u, fr in s.each()]
    cx0, cy0 = g[0][1][0], g[0][1][1]
    b = Box(cx0 - w / 2, cy0 - h / 2, w, h)
    motion = [(u, {"sx": max(1e-4, v[2] * v[3]), "sy": max(1e-4, v[2]), "dx": v[0] - cx0, "dy": v[1] - cy0}, "linear")
              for u, v in g]
    track = t.track("video", name)
    clip = t.photo(track, sample, 0.0, s.dur, b, motion, label="Tu foto")
    t.mask(track, clip, "path", pathData=rr_path(w, h, h * 0.22))
    if any(abs(v[4]) > 1e-6 for _, v in g):
        clip["rotation"] = keys([(u, round(v[4], 3), "linear") for u, v in g])
    if any(v[5] < 0.999 for _, v in g):
        clip["opacity"] = keys([(u, round(max(0.0, min(1.0, v[5])), 4), "linear") for u, v in g])
    return clip


def confetti_field(s, at, n=34, seed=1, colours=(RED, WHITE), drift=40):
    """Little outlined squares, rings and crosses scattered over the frame, popping at `at` and drifting out."""
    import random
    rnd = random.Random(seed)
    for j in range(n):
        x, y = rnd.uniform(80, 1840), rnd.uniform(60, 1020)
        if abs(x - 960) < 300 and abs(y - 540) < 200:
            x += 500 if x > 960 else -500
        size = rnd.uniform(22, 40)
        col = colours[j % len(colours)]
        kind = ("rectangle", "ellipse", "cross")[j % 3]
        dx, dy = (x - 960) / 960 * drift, (y - 540) / 540 * drift
        d = rnd.randint(0, 6)
        geom = (lambda fr, u, x=x, y=y, dx=dx, dy=dy, d=d, size=size: (
            x + dx * lin(fr, at, 90), y + dy * lin(fr, at, 90), size * k(fr, at + d, 6), size * k(fr, at + d, 6), 45,
            1.0))
        if kind == "cross":
            s.obj(f"Partícula {j + 1}", solid(col), geom, path=poly([(40, 0), (60, 0), (60, 40), (100, 40), (100, 60),
                                                                     (60, 60), (60, 100), (40, 100), (40, 60), (0, 60),
                                                                     (0, 40), (40, 40)]))
        else:
            s.obj(f"Partícula {j + 1}", ring(col, 3), geom, kind=kind)


def letters_in(s, clip, at, stagger=0.04, duration=0.1):
    s.typed(clip, at, stagger=stagger, duration=duration, preset="fade", order="random")


YT_LOGO = (rr_path(100, 72, 20).replace("Z", "Z ") + "M 40 32 L 66 50 L 40 68 Z")
REDS = ("#B30013", "#8E0010", "#A80012", "#6E000B", "#94000F")


# --- 6. Opener: white blobs gather into a disc, the disc turns into the play button, the name scatters in ---------
def op_blobs():
    D = dur_for(2.8, 1.0)
    t = _p("apertura-gotas", "Apertura: gotas que forman el botón de YouTube", "Opener: blobs that form the YouTube "
           "button", 12110, D, "aperturas", ["apertura", "logo"], thumb=3.0)
    s = S(t, D)
    for i, (x, y, at) in enumerate(((700, 560, 0), (820, 480, 2), (930, 590, 4), (1010, 500, 6))):
        c = s.obj(f"Gota {i + 1}", solid(WHITE), lambda fr, u, x=x, y=y, at=at: (
            x + (960 - x) * k(fr, at + 6, 9), y + (540 - y) * k(fr, at + 6, 9), 300 * k(fr, at, 9) * (1 - k(fr, 15, 3)),
            300 * k(fr, at, 9) * (1 - k(fr, 15, 3)), 0, 1), kind="ellipse")
        wiggle(c, 22, 30, 3, i)
        s.obj(f"Gota {i + 1} (punto)", solid(RED), lambda fr, u, x=x, y=y, at=at: (
            x + (960 - x) * k(fr, at + 6, 9), y + (540 - y) * k(fr, at + 6, 9), 110 * k(fr, at + 3, 6) * (1 - k(fr, 15, 3)),
            110 * k(fr, at + 3, 6) * (1 - k(fr, 15, 3)), 0, 1), kind="ellipse")
    c = s.obj("Disco blanco", solid(WHITE), lambda fr, u: (960, 540, 3000 * k(fr, 6, 12), 3000 * k(fr, 6, 12), 0, 1),
              kind="ellipse")
    wiggle(c, 40, 60, 2, 3)
    c = s.obj("Fondo", solid(RED), lambda fr, u: (960, 540, 2800 * k(fr, 15, 12), 2800 * k(fr, 15, 12), 0, 1),
              kind="ellipse")
    wiggle(c, 40, 60, 2, 5)
    small = lambda fr: k(fr, 48, 6)  # noqa: E731

    def btn(fr, u):
        q = k(fr, 39, 9)
        w = (1060 + (930 - 1060) * q) * (1 - small(fr)) + 420 * small(fr)
        h = (1060 + (630 - 1060) * q) * (1 - small(fr)) + 288 * small(fr)
        w, h = w * k(fr, 21, 12), h * k(fr, 21, 12)
        return 960, 540 - 48 * k(fr, 66, 6), w, h, 0, 1
    c = s.obj("Botón", solid(WHITE), btn, base=(1060, 1060))
    knob(s, c, "cornerRadius", lambda fr, u: (lambda g: min(g[2], g[3]) * (0.5 - 0.2 * k(fr, 39, 9)))(btn(fr, u)))
    wiggle(c, 10, 40, 3, 7)
    knob(s, c, "wiggleSize", lambda fr, u: 30 * (1 - k(fr, 30, 9)))

    def tri(fr, u):
        cx, cy, w, h, _, _ = btn(fr, u)
        size = min(w, h) * 0.42 * k(fr, 24, 12)
        turn = -150 * (1 - k(fr, 24, 18))
        return cx + size * 0.08, cy, size, size, turn, 1
    s.obj("Botón (play)", solid(RED), tri, path=TRIANGLE)
    confetti_field(s, 51, colours=(BLACK, WHITE, "#FF8A8A"))
    c = s.say("@YOUR_CHANNEL", (630, 650, 1290, 692), M, 800, WHITE, "Canal")
    s.typed(c, 69, stagger=0.03, duration=0.15, preset="pop", order="random")
    c = s.say("100K SUBSCRIBERS", (840, 712, 1080, 728), M, 600, "#FFD0D0", "Texto")
    letters_in(s, c, 75, 0.02)
    return t


# --- 7. Opener: a dark red target opens, a white disc with a turning play sign, the name types in -------------
def op_target():
    D = dur_for(1.8, 1.6)
    t = _p("apertura-diana", "Apertura: botón redondo sobre círculos rojos", "Opener: round button on red circles",
           12111, D, "aperturas", ["apertura", "logo"], thumb=2.8)
    s = S(t, D)
    for i, (d, c0, c1) in enumerate(((3400, "#C4001A", "#3A0005"), (2300, "#D0021B", "#4A0006"),
                                     (1500, "#B3001A", "#3A0005"), (820, "#8E0010", "#2A0004"))):
        s.obj(f"Fondo {i + 1}" if i else "Fondo", grad_(c0, c1, 315),
              lambda fr, u, d=d, i=i: (900, 540, d * k(fr, i, 9), d * k(fr, i, 9), 0, 1), kind="ellipse")
    angles = [(9, 0), (15, 0), (18, 90), (21, 135), (24, 270), (27, 90), (30, 0), (33, 180), (36, 270), (42, 0)]

    def turn(fr):
        a = 0.0
        for (f0, a0), (f1, a1) in zip(angles, angles[1:]):
            if fr >= f1:
                a = a1
            elif fr >= f0:
                a = a0 + (a1 - a0) * k(fr, f0, f1 - f0)
                break
        return a
    x = lambda fr: 960 - 384 * k(fr, 33, 9)  # noqa: E731
    s.obj("Botón", solid(WHITE), lambda fr, u: (x(fr), 540, max(12, 400 * k(fr, 6, 9)), max(12, 400 * k(fr, 6, 9)),
                                                0, k(fr, 3, 2)), kind="ellipse")
    s.obj("Botón (play)", solid(RED), lambda fr, u: (x(fr) + 10 * math.cos(math.radians(turn(fr))),
                                                     540 + 10 * math.sin(math.radians(turn(fr))), 150 * k(fr, 9, 6),
                                                     150 * k(fr, 9, 6), turn(fr), 1), path=TRIANGLE)
    c = s.say("@your_channel", (822, 506, 1548, 566), ROBOTO, 700, WHITE, "Canal", align="left",
              geom=lambda fr, u: (0, 0, 1, 0, 1))
    s.typed(c, 36, stagger=0.05, duration=0.15, preset="fade")
    c = s.say("100k subscribers", (822, 586, 1050, 608), ROBOTO, 400, "#FFD6D6", "Texto", align="left")
    s.typed(c, 45, stagger=0.02, duration=0.1, preset="fade")
    return t


# --- 8. Opener: the 3D play logo flies out of the camera, spins and lands among particles; the name types in ------
def op_logo_fly():
    D = dur_for(2.7, 1.0)
    t = _p("apertura-logo-vuela", "Apertura: logo que se aleja girando", "Opener: logo flying back and spinning",
           12112, D, "aperturas", ["apertura", "logo", "youtube"], thumb=2.6)
    s = S(t, D)
    footage(s, "h-portrait-05")
    s.rect("Fondo", solid("#2A2A2A"), lambda fr, u: (-10, -10, 1930, 1090), op=lambda fr, u: k(fr, 15, 3))
    confetti_field(s, 18, seed=4, drift=30)
    x = lambda fr: 960 - 300 * k(fr, 69, 9)  # noqa: E731
    depth = 70

    # The logo comes out of the camera (huge, shrinking) with the play sign cut out, turns a whole turn
    # about its vertical axis while it tilts, and settles (reference 19.2-20.8 s).
    def logo(fr, u):
        sc = 1 + 11 * (1 - k(fr, 0, 33)) ** 2
        return x(fr), 540, 330 * sc, 240 * sc, -32 * (1 - k(fr, 0, 45)), 1, 0, 360 * k(fr, 6, 39)

    def tri(fr, u):
        cx, cy, w, h, rot, op, rx, ry = logo(fr, u)
        dx, dy, dz = turn3(w * 0.03, 0, (-depth / 2 + 3) * w / 330, rx, ry, rot)
        return cx + dx, cy + dy, w * 0.26, h * 0.36, rot, 1.0 if fr >= 15 else 0.0, rx, ry, dz
    solid3d(s, "Logo (play)", TRIANGLE, WHITE, (WHITE, "#D8D8D8"), tri, 2, n=0, base=(86, 86))
    solid3d(s, "Logo", YT_LOGO, grad_("#FF1A2A", "#B5000E", 135), ("#F2F2F2", "#9C9C9C"), logo, depth, n=12,
            base=(330, 240), slab=(0.0, 0.62), evenodd=True)
    c = s.say("@YOUR_CHANNEL", (840, 512, 1440, 556), M, 700, "#E8E8E8", "Canal", align="left")
    s.typed(c, 72, stagger=0.03, duration=0.12, preset="fade", order="random")
    return t


def grad_(c0, c1, angle=90):
    from templates_tit_h import grad
    return grad(c0, c1, angle)


# --- 9. Opener: an avatar tumbles in, a white and a black circle open, red sparks; the name slides out -----------
def op_avatar_iris():
    D = dur_for(2.6, 0.8)
    t = _p("apertura-avatar-circulo", "Apertura: avatar y círculos que se abren", "Opener: avatar and opening circles",
           12113, D, "aperturas", ["apertura", "avatar"], thumb=2.9)
    s = S(t, D)
    footage(s, "h-portrait-03")
    # Both circles have soft edges (reference 22.4-22.6 s).
    c = s.obj("Círculo blanco", solid(WHITE), lambda fr, u: (960, 540, 3700 * k(fr, 30, 9), 3700 * k(fr, 30, 9), 0, 1),
              kind="ellipse")
    soft(s, c, 9.0)
    c["shapeStyle"]["kind"] = "custom"
    c["shapeStyle"]["customPath"] = INSET_DISC
    c = s.obj("Fondo", grad_("#2E2E2E", "#050505", 180), lambda fr, u: (960, 540, 3700 * k(fr, 35, 10),
                                                                        3700 * k(fr, 35, 10), 0, 1), kind="ellipse")
    soft(s, c, 11.0, lambda fr: 1 - k(fr, 42, 6))
    c["shapeStyle"]["kind"] = "custom"
    c["shapeStyle"]["customPath"] = INSET_DISC
    import random
    rnd = random.Random(9)
    for j in range(14):
        a = math.radians(360 * j / 14 + rnd.uniform(-8, 8))
        s.obj(f"Destello {j + 1}", solid(RED if j % 3 else WHITE), lambda fr, u, a=a: (
            960 + math.cos(a) * (180 + 380 * k(fr, 39, 12)), 540 + math.sin(a) * (180 + 380 * k(fr, 39, 12)),
            70, 6, math.degrees(a), k(fr, 39, 2) * (1 - k(fr, 48, 6))))
    for j in range(8):
        bx, by, d = rnd.uniform(200, 1700), rnd.uniform(200, 1000), rnd.uniform(60, 120)
        s.obj(f"Burbuja {j + 1}", solid("#262626"), lambda fr, u, bx=bx, by=by, d=d, j=j: (
            bx, by - 40 * lin(fr, 45, 60), d * k(fr, 45 + j, 9), d * k(fr, 45 + j, 9), 0, 1), kind="ellipse")
    cx = lambda fr: 960 - 330 * k(fr, 63, 12)  # noqa: E731

    # The avatar tumbles in: it spins in its plane while it tilts in 3D (reference 22.0-22.9 s).
    def g(fr, u):
        q = k(fr, 0, 27)
        x0 = 540 + (960 - 540) * q
        y0 = 600 - 60 * math.sin(math.pi * q)
        rot = 35 * (1 - q) * math.cos(3 * math.pi * q) - 200 * (1 - q)
        return (cx(fr) if fr >= 27 else x0), y0 if fr < 27 else 540, 1.0, rot, k(fr, 0, 1), \
            35 * (1 - q), 60 * (1 - q) * math.cos(2 * math.pi * q)
    badge3d(s, "h-portrait-04", g, border="#F2A7B0", bw=6, depth=18, sides=("#FFFFFF", "#C8C8C8"), back=WHITE)
    s.say("@yourchannel", (810, 494, 1500, 566), ROBOTO, 700, WHITE, "Canal", align="left",
          reveal=lambda fr: (cx(fr) + 170, 0, 1920, 1080), shift=lambda fr: (-500 * (1 - k(fr, 63, 12)), 0),
          op=lambda fr, u: k(fr, 63, 2))
    return t


# --- 10. Opener: dark chevrons sweep in, a red button rolls in with its trail -------------------------------------
def op_chevrons():
    D = dur_for(2.6, 1.0)
    t = _p("apertura-flechas", "Apertura: flechas oscuras y botón que rueda", "Opener: dark chevrons and a rolling "
           "button", 12114, D, "aperturas", ["apertura", "logo", "youtube"], thumb=2.7)
    s = S(t, D)
    footage(s, "h-portrait-03")
    chev = poly([(0, 0), (50, 0), (100, 50), (50, 100), (0, 100), (50, 50)])
    for i, (shade, at, tip) in enumerate((("#2C2C2C", 3, 2400), ("#232323", 6, 2000), ("#1B1B1B", 9, 1600),
                                          ("#141414", 12, 1240))):
        s.obj(f"Flecha {i + 1}", solid(shade), lambda fr, u, at=at, tip=tip: (
            -2600 + (tip + 600 + 2600 - 1900) * k(fr, at, 36) - 600, 540, 3800, 3800, 0, 1), path=chev)
    for i, d in enumerate((2400, 1500, 760)):
        s.obj(f"Rombo {i + 1}", solid(("#262626", "#1F1F1F", "#191919")[i]), lambda fr, u, d=d, i=i: (
            960, 540, d, d, 45, k(fr, 42 + 3 * i, 9)))

    def roll(fr, u, lag=0):
        f = fr - lag
        q = k(f, 30, 21)
        return -200 + (960 + 200) * q, 540, 270, 270, -360 * (1 - q) + 0, 1.0 if f >= 30 else 0.0
    for i, lag in enumerate((6, 4, 2)):
        s.obj(f"Estela {i + 1}", solid("#7A0010", 0.4 + 0.2 * i), lambda fr, u, lag=lag: (lambda g: (
            *g[:5], g[5] * (1 - k(fr, 54, 9))))(roll(fr, u, lag)), radius=30, base=(270, 270))
    s.obj("Botón", solid(RED), roll, radius=30, base=(270, 270))
    s.obj("Botón (play)", solid(WHITE), lambda fr, u: (lambda g: (g[0] + 8, g[1], 96, 110, g[4], g[5]))(roll(fr, u)),
          path=TRIANGLE)
    c = s.say("@yourchannel", (880, 712, 1040, 728), M, 600, "#9A9A9A", "Canal")
    letters_in(s, c, 66, 0.03)
    c = s.say("DESIGN", (920, 352, 1000, 364), M, 600, "#777777", "Texto")
    letters_in(s, c, 63, 0.03)
    return t


# --- 11. Opener: an avatar drops in, white and red bands rise, it turns and shrinks over dark grey --------------
def op_avatar_bands():
    D = dur_for(2.9, 0.6)
    t = _p("apertura-avatar-bandas", "Apertura: avatar que cae y bandas que suben", "Opener: falling avatar and "
           "rising bands", 12115, D, "aperturas", ["apertura", "avatar"], thumb=3.3)
    s = S(t, D)
    footage(s, "h-portrait-05")
    vee = poly([(0, 30), (50, 0), (100, 30), (100, 100), (0, 100)])
    for i, (col, at) in enumerate(((WHITE, 21), (RED, 25), ("#1C1C1C", 29))):
        layers = solid(col) if i < 2 else grad_("#3A3A3A", "#0A0A0A", 180)
        c = s.obj(f"Banda {i + 1}" if i < 2 else "Fondo", layers, lambda fr, u, at=at: (
            960, 1080 + 1400 - 2600 * k(fr, at, 12), 2400, 2600, 0, 1), path=vee)
        s.mblur(c)

    # The avatar drops in on a thick white plate, tumbles a whole turn about its horizontal axis (its back is red)
    # and settles small (reference 22.1-23.4 s).
    def g(fr, u):
        q = k(fr, 0, 18)
        y = -300 + (480 + 300) * q
        rot = 40 * (1 - q) - 12 * math.sin(math.pi * lin(fr, 18, 12))
        sc = 2.0 - 1.0 * k(fr, 33, 15)
        return 960, y - 30 * k(fr, 33, 15), sc, rot, 1, 20 * (1 - q) + 360 * k(fr, 24, 18), 0
    badge3d(s, "h-portrait-04", g, border="#D9D9D9", bw=8, depth=40, back=RED)
    c = s.say("@yourchannel", (850, 556, 1070, 584), M, 700, RED, "Canal")
    letters_in(s, c, 51, 0.04)
    return t


# --- 12. Opener: slanted bands wipe up, the button tumbles in on white, the name types, the button flips big -------
def op_white():
    D = dur_for(2.7, 0.5)
    t = _p("apertura-blanca", "Apertura: bandas inclinadas y botón sobre blanco", "Opener: slanted bands and a button "
           "on white", 12116, D, "aperturas", ["apertura", "logo", "youtube"], thumb=1.8)
    s = S(t, D)
    footage(s, "h-portrait-01")
    for i, (col, at) in enumerate((("#F27A86", 0), (RED, 2), ("#1E1E1E", 4), (WHITE, 6))):
        c = s.obj(f"Banda {i + 1}" if i < 3 else "Fondo", solid(col), lambda fr, u, at=at: (
            960, 1080 + 1300 - 2000 * k(fr, at, 6), 2600, 2000, -5, 1))
        s.mblur(c)
    for g_, (ox, oy) in enumerate(((180, 160), (1700, 900))):
        for j in range(5):
            col = (RED, "#1E1E1E", "#1E1E1E", RED, "#1E1E1E")[j]
            ln = (220, 160, 260, 120, 180)[j]
            off = (j - 2) * 34
            s.obj(f"Línea {g_ + 1}.{j + 1}", solid(col), lambda fr, u, ox=ox, oy=oy, ln=ln, off=off, j=j: (
                ox + off * 0.7 + 60 * math.sin(u * 1.4 + j), oy - off * 0.7 + 60 * math.sin(u * 1.4 + j), ln,
                6 if j % 2 == 0 else 4, -45, k(fr, 12 + j, 6)))
    depth = 70

    # The button flies in from the lower left tumbling in 3D (seen from below, three quarters of a turn about its
    # vertical axis), lands; at the end it grows and tips its top back (reference 19.6-21.5 s).
    def btn(fr, u):
        q = k(fr, 6, 27)
        grow = 1 + 1.5 * k(fr, 57, 12)
        y = 540 - 180 * k(fr, 60, 6) + 260 * k(fr, 66, 12)
        return 960 + 100 * k(fr, 66, 12) - 420 * (1 - q), y + 300 * (1 - q), 330 * grow, 240 * grow, \
            -30 * (1 - q), k(fr, 6, 1), 55 * (1 - q) + 78 * k(fr, 60, 10), -270 * (1 - q)

    def tri(fr, u):
        cx, cy, w, h, rot, op, rx, ry = btn(fr, u)
        dx, dy, dz = turn3(w * 0.03, 0, (depth / 2 + 1) * w / 330, rx, ry, rot)
        front = math.cos(math.radians(rx)) * math.cos(math.radians(ry)) >= 0
        return cx + dx, cy + dy, w * 0.27, h * 0.38, rot, op if front else 0.0, rx, ry, dz
    solid3d(s, "Botón", rr_path(100, 72, 20), grad_("#FF1A2A", "#C0000F", 180), ("#F2F2F2", "#A8A8A8"), btn, depth,
            n=12, base=(330, 240), back=solid("#B0000E"), slab=(0.0, 0.62))
    solid3d(s, "Botón (play)", TRIANGLE, WHITE, (WHITE, WHITE), tri, 1, n=0, base=(89, 91))
    c = s.say("@yourchannel", (850, 634, 1070, 656), M, 800, "#222222", "Canal")
    s.typed(c, 48, stagger=0.04, duration=0.04)
    cursor(s, [(30, 1100, 700), (45, 980, 560), (60, 980, 400), (78, 1240, 760)])
    return t


SWIRL_RED = ("#E0102A", "#0A0A0A", "#F05A70", "#9A0012", "#151515", "#E8243C", "#5A0008", "#C81E3C", "#0A0A0A",
             "#F27A8A", "#2A0004")
SWIRL_BLUE = ("#1E1A70", "#06041C", "#3E1C8A", "#0E0838", "#25368A", "#06041C", "#4E1C90", "#0A0628", "#1E2C80",
              "#06041C", "#3A1A80")


def adjust_fx(s, name, specs):
    """An adjustment layer over everything made so far: specs = [(catalog id, {param: fn(fr, u)}, {param: value})]."""
    from scene import effect
    effects = []
    for cid, animated, params in specs:
        kf = {nm: keys([(u, round(fn(fr, u), 4), "linear") for u, fr in s.each()]) for nm, fn in animated.items()}
        effects.append(effect(cid, kf or None, **params))
    return s.t.adjust(effects, name=name)


GB = "builtin.effects.gaussian_blur"
# The engine's blur radius is in pixels of the render, not of the project: the 640 × 360 previews were judged with
# these radii. When the blur shader scales by u_unitPx (project px), set BLUR_PX = 3 to keep the same look.
BLUR_PX = 1.0
# A disc in the middle 70 % of its box: a blurred shape needs room in its box (the blur stops at the box's edge).
INSET_DISC = ("M 85 50 C 85 69.33 69.33 85 50 85 C 30.67 85 15 69.33 15 50 C 15 30.67 30.67 15 50 15 "
              "C 69.33 15 85 30.67 85 50 Z")


def soft_specs(r, gate=None):
    """A smooth blur of about r px as three gaussian blurs of r, r/2 and r/4 (one pass of the engine's blur takes 5
    taps r × 1.4 and r × 3.2 apart: past a few px it doubles the picture instead of softening it). gate(fr) 0..1
    scales it."""
    g = gate or (lambda fr: 1.0)
    return [(GB, {"u_blurRadius": lambda fr, u, q=q: BLUR_PX * r * q * g(fr)}, {}) for q in (1.0, 0.5, 0.25)]


def soft(s, clip, r, gate=None):
    """soft_specs on one clip."""
    for cid, animated, params in soft_specs(r, gate):
        s.fx(clip, cid, animated=animated, **params)
    return clip


def swirl(s, at=0, n=22, name="Onda", turn=-58.0, cols=SWIRL_RED, base="#0A0A0A", blur=9.0, twirl=None):
    """Stripes curving across the frame, drifting, softened by a gaussian blur over them (the silk / liquid
    background); twirl = angle of a twirl over them too (stylize.twirl, from the build after 0.30.2: without it the
    stripes stay waves)."""
    s.rect(f"{name} (fondo)", solid(base), lambda fr, u: (-10, -10, 1930, 1090), op=lambda fr, u: k(fr, at, 6))
    for i in range(n):
        y0 = -700 + 2500 * i / n
        pts = [(x, y0 + 380 * math.sin(x / 700.0 + i * 0.25)) for x in range(-900, 2900, 160)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        bx0, by0, bw, bh = min(xs), min(ys) - 80, max(xs) - min(xs), max(ys) - min(ys) + 160
        top = [((x - bx0) / bw * 100, (y - 80 - by0) / bh * 100) for x, y in pts]
        bot = [((x - bx0) / bw * 100, (y + 80 - by0) / bh * 100) for x, y in pts][::-1]
        s.obj(f"{name} {i + 1}", grad_(cols[i % len(cols)], cols[(i + 4) % len(cols)], 90), lambda fr, u, bx0=bx0, by0=by0, bw=bw, bh=bh, i=i: (
            bx0 + bw / 2 - 80 * u, by0 + bh / 2 + 30 * math.sin(u * 1.3 + i), bw, bh, turn, k(fr, at, 6)),
            path=poly(top + bot))
    specs = soft_specs(blur, lambda fr: 1.0 if fr >= at else 0.0)
    if twirl:
        specs.append(("stylize.twirl", {"angle": lambda fr, u: (twirl + 12 * u) * (1.0 if fr >= at else 0.0)},
                      {"radius": 1.0, "centerX": 0.5, "centerY": 0.5}))
    adjust_fx(s, f"{name} (suave)", specs)


# --- 13. Opener: arcs swirl around a spinning logo; it becomes a window onto red waves; the name slides out -----
def op_waves():
    D = dur_for(2.9, 0.6)
    t = _p("apertura-ondas", "Apertura: logo con arcos y fondo de ondas rojas", "Opener: logo, swirling arcs and red "
           "waves", 12117, D, "aperturas", ["apertura", "logo", "ondas"], thumb=3.5)
    s = S(t, D)
    footage(s, "h-portrait-01")
    win = lambda fr: k(fr, 54, 6)  # noqa: E731
    full = lambda fr: k(fr, 60, 2)  # noqa: E731
    swirl(s, 54, twirl=70.0)
    # The window: outside it the footage still shows until the waves fill the frame; its edge is soft
    # (reference 24.2 s).
    mk = s.t.photo(s.t.track("video", "Tu video (borde)"), "h-portrait-01", 0.0, D, None, None,
                   reuse=s.t.slots[0].id)
    ws = {"x": [], "y": [], "w": [], "h": [], "feather": []}
    for u, fr in s.each():
        q = win(fr) if fr >= 54 else 0.0
        w, h = (300 + 1900 * q) * (1 + 2 * full(fr)), (210 + 1100 * q) * (1 + 2 * full(fr))
        for key, v in (("x", 0.5), ("y", 0.5), ("w", w / 1920), ("h", h / 1080), ("feather", 10 + 70 * q)):
            ws[key].append((u, v, "linear"))
    s.t.mask(next(tr for tr in s.t.tracks if mk in tr.clips), mk, "rectangle", feather=10, x=0.5, y=0.5, w=0.0,
             h=0.0, invert=True, keyframes={key: keys(v) for key, v in ws.items()})
    for i, (r, col, at, a0) in enumerate(((620, RED, 0, 0), (720, WHITE, 3, 120), (540, BLACK, 6, 240),
                                          (820, RED, 9, 60), (660, WHITE, 12, 200))):
        s.obj(f"Arco {i + 1}", ring(col, 10 + 4 * (i % 2)), lambda fr, u, r=r, at=at, a0=a0: (
            960, 540, r * (0.6 + 0.4 * k(fr, at, 15)), r * (0.6 + 0.4 * k(fr, at, 15)), a0 + 280 * lin(fr, at, 54),
            k(fr, at, 4) * (1 - k(fr, 48, 6))), path="M 50 0 C 80 0 100 20 100 50")

    # The logo pops and turns about its vertical axis in 3D (white sides), tilting, until its red back faces the
    # camera and opens into the window (reference 22.3-24.1 s).
    depth = 72

    def logo(fr, u):
        rot = -40 * math.sin(math.pi * lin(fr, 6, 42))
        return 960, 540, 360 * k(fr, 3, 6), 300 * k(fr, 3, 6), rot, 1.0 if fr < 54 else 0.0, 0, \
            360 * k(fr, 3, 20) + 180 * k(fr, 38, 16)

    def tri(fr, u):
        cx, cy, w, h, rot, op, rx, ry = logo(fr, u)
        sc = w / 360
        dx, dy, dz = turn3(w * 0.03, 0, (depth / 2 + 5) * sc, rx, ry, rot)
        front = math.cos(math.radians(ry)) >= 0
        return cx + dx, cy + dy, w * 0.3, h * 0.36, rot, op if front else 0.0, rx, ry, dz
    solid3d(s, "Logo", rr_path(100, 84, 22), grad_("#FF1A2A", "#B5000E", 135), ("#F0F0F0", "#A0A0A0"), logo,
            depth, n=12, base=(360, 300), back=solid("#C0000F"), slab=(0.0, 0.62))
    solid3d(s, "Logo (play)", TRIANGLE, WHITE, ("#C8C8C8", "#9A9A9A"), tri, 10, n=2, base=(108, 108))
    s.rect("Ventana (borde)", ring(RED, 14), lambda fr, u: (960 - (150 + 850 * win(fr)), 540 - (105 + 475 * win(fr)),
                                                            960 + (150 + 850 * win(fr)), 540 + (105 + 475 * win(fr))),
           op=lambda fr, u: k(fr, 51, 2) * (1 - full(fr)), radius=40, base=(300, 210))
    cx = lambda fr: 960 - 312 * k(fr, 72, 12)  # noqa: E731
    badge(s, "h-portrait-04", lambda fr, u: (cx(fr), 540, 1.0, 1.0, 0, k(fr, 54, 4)), border="#E0E0E0", bw=6)
    s.say("@yourchannel", (870, 510, 1530, 570), ROBOTO, 700, WHITE, "Canal", align="left",
          reveal=lambda fr: (cx(fr) + 170, 0, 1920, 1080), shift=lambda fr: (-560 * (1 - k(fr, 72, 12)), 0),
          op=lambda fr, u: k(fr, 72, 2))
    for i, y in enumerate((470, 610)):
        s.rect(f"Línea {i + 1}", solid(WHITE, 0.8), lambda fr, u, y=y, i=i: (
            800 + 300 * i, y, 800 + 300 * i + 360 * k(fr, 75 + 3 * i, 9), y + 3))
    return t


# --- helpers for the titles ---------------------------------------------------------------------------------------
def anim(s, clip, at, preset, stagger=0.05, duration=0.4, unit="character", order="forward", out="fade", **params):
    """A text animation in (any preset) from frame `at`; it leaves with `out` backwards at EXIT×."""
    from scene import tanim
    lead = round(at / FPS, 3)
    clip["textStyle"]["animation"] = {
        "in": tanim(preset, duration=duration, unit=unit, stagger=stagger, ease="easeOut", delay=lead, order=order,
                    **params),
        "out": tanim(out, duration=duration / EXIT, unit=unit, stagger=stagger / EXIT, ease="easeIn",
                     delay=round(lead / EXIT, 3), order="backward" if order == "forward" else order)}


def smooth(points, n=8):
    """A Catmull-Rom curve through points, as a dense polyline."""
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for j in range(n):
            t = j / n
            out.append(tuple(0.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t * t
                                    + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t ** 3) for c in (0, 1)))
    out.append(points[-1])
    return out


def spacing(s, clip, em):
    """Letter spacing em(fr, u) (in em) every frame; the line no longer wraps."""
    size = clip["textStyle"]["pixelSize"]
    clip["textStyle"]["wordWrap"] = False
    clip["textStyle"].setdefault("keyframes", {})["letterSpacing"] = keys(
        [(u, round(em(fr, u) * size, 2), "linear") for u, fr in s.each()])
    # The spread line is wider than its box: widen the box (it stays where it is aligned).
    align = clip["textStyle"].get("align", "center")
    for kf_w, kf_x in zip(clip["width"]["keyframes"], clip["x"]["keyframes"]):
        extra = kf_w["value"] * 1.5
        kf_w["value"] += extra
        kf_x["value"] -= {"left": 0.0, "right": extra}.get(align, extra / 2)


def tight(clip, em):
    """Letters closer (em < 0) like the reference's tight bold type."""
    clip["textStyle"]["letterSpacing"] = round(em * clip["textStyle"]["pixelSize"], 2)


SOFT = [shadow("#000000", 0, 12, 24, 0.35), fill(WHITE)]


def outline_text(colour, width=3):
    return [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
            {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "outside",
             "opacity": 1.0, "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}]


def dot_grid(s, x0, y0, cols, rows, step, at, colour=WHITE, size=6, name="Puntos"):
    for r in range(rows):
        for c in range(cols):
            s.obj(f"{name} {r + 1}.{c + 1}", solid(colour), lambda fr, u, r=r, c=c: (
                x0 + c * step, y0 + r * step, size, size, 0, k(fr, at + c + r, 4)), kind="ellipse")


def _t(id, es, en, order, dur, tags=(), thumb=None):
    return _p(id, es, en, order, dur, "titulos-estilo", ["título"] + list(tags), thumb)


# --- 14. BIG TITLE: a red slanted band, a black bar crosses; the words fly in letter by letter --------------------
def big_title():
    D = dur_for(1.2, 1.6)
    t = _t("big-title", "Título grande sobre banda roja inclinada", "Big title on a slanted red band", 12120, D,
           ["grande"])
    s = S(t, D)
    bg(s, "#262626")
    s.obj("Banda", solid("#D9001B"), lambda fr, u: (960, 540, 1920 * (2.4 - 1.4 * k(fr, 6, 12)), 1080 * (2.4 - 1.4 * k(fr, 6, 12)), 0, 1),
          path=poly([(0, 0), (66, 0), (100, 33), (100, 100), (19, 100), (0, 72)]))
    s.obj("Barra", solid("#111111"), lambda fr, u: (-600 + 3200 * k(fr, 0, 12), 540, 160, 2600, 30,
                                                    1 - k(fr, 10, 3)))
    zoom = lambda fr: 1.16 - 0.16 * k(fr, 9, 60)  # noqa: E731
    for i, (text, ink, at) in enumerate((("TITLE", (60, 450, 1500, 810), 12), ("BIG", (60, 60, 930, 390), 18))):
        c = s.say(text, ink, M, 900, WHITE, "Título" if i else "Título 2", align="left", layers=SOFT,
                  geom=lambda fr, u, ink=ink: (*s.about(ink, 40, 540, zoom(fr)), zoom(fr), 0, 1))
        anim(s, c, at, "im-motion-blur-slide", stagger=0.06, duration=0.35, order="backward")
        tight(c, -0.05)
    s.say("YOUR TEXT HERE", (1560, 1010, 1860, 1026), M, 600, "#7A0010", "Texto", align="right",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 30, 9)))
    return t


# --- 15. STRONG TITLES: a red wave comes down; the spread letters close up --------------------------------------
def strong_titles():
    D = dur_for(1.2, 1.4)
    t = _t("strong-titles", "Título fuerte bajo una ola roja", "Strong title under a red wave", 12121, D, ["ola"])
    s = S(t, D)
    bg(s, "#262626")
    wave = [(0, 0), (100, 0)] + [(x / 19.2, (760 + 160 * math.sin(x / 330 + 0.6)
                                                                - 260 * x / 1920) / 10.8) for x in range(1920, -1, -160)]
    for i, (col, dy) in enumerate((("#9E0018", 50), ("#D9001B", 0))):
        c = s.obj("Ola (sombra)" if i == 0 else "Ola", solid(col), lambda fr, u, dy=dy: (
            960, 540 + dy - 1150 * (1 - k(fr, 3, 15)) + 10 * math.sin(u * 2), 1920, 1080, 0, 1), path=poly(wave))
        wiggle(c, 14, 80, 0.6, i)
    zoom = lambda fr, u: 1 + 0.04 * u  # noqa: E731
    for i, (text, ink, at) in enumerate((("STRONG", (120, 210, 1710, 510), 6), ("TITLES", (480, 510, 1710, 750), 9))):
        c = s.say(text, ink, M, 900, WHITE, "Título" if i == 0 else "Título 2", layers=SOFT,
                  geom=lambda fr, u, ink=ink: (*s.about(ink, 960, 480, zoom(fr, u)), zoom(fr, u), 0, 1))
        anim(s, c, at, "converge", stagger=0.03, duration=0.6, order="forward", spread=1.2, blur=6)
        tight(c, -0.06)
    s.say("YOUR TEXT HERE", (60, 1050, 360, 1064), M, 600, "#5A5A5A", "Texto", align="left",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 24, 9)))
    return t


# --- 16. The best video template: a red squiggle draws itself; the spread lines close up --------------------------
def squiggle_lines():
    D = dur_for(1.6, 1.2)
    t = _t("trazo-rojo", "Título en tres líneas con trazo rojo", "Three-line title with a red squiggle", 12122, D,
           ["trazo"])
    s = S(t, D)
    bg(s, "#262626")
    lines = (("The best video", (270, 360, 1410, 450), 15), ("template for your", (180, 480, 1110, 570), 18),
             ("youtube channel", (90, 630, 990, 720), 21))
    for i, (text, ink, at) in enumerate(lines):
        c = s.say(text, ink, M, 700, WHITE, f"Título {i + 1}" if i else "Título", align="left",
                  geom=lambda fr, u, i=i: (0, 165 * (i - 1) * (1 - k(fr, 39, 24)), 1, 0, 1))
        spacing(s, c, lambda fr, u: 0.4 * (1 - k(fr, 39, 24)))
        anim(s, c, at - 9, "fade", stagger=0.04, duration=0.12, order="backward")
    pts = smooth([(-150, 1000), (300, 700), (750, 330), (1150, 60), (1420, -30), (1560, 120), (1350, 420),
                  (950, 760), (760, 1000), (950, 1110), (1350, 930), (1750, 640), (2100, 420)], 10)
    s.outline("Trazo", pts, 100, "#E3061F", at=0, n=24, closed=False)
    return t


# --- 17. LIQUID TITLE: a red-to-purple circle opens, a soft blob wobbles, the outlined letters come one by one -----
def liquid_title():
    D = dur_for(1.6, 1.0)
    t = _t("liquid-title", "Título con contorno sobre mancha líquida", "Outlined title on a liquid blob", 12123, D,
           ["líquido", "contorno"])
    s = S(t, D)
    s.obj("Fondo", grad_("#E8002A", "#2E0A6E", 45), lambda fr, u: (960, 540, 2400 * k(fr, 0, 9), 2400 * k(fr, 0, 9),
                                                                    0, 1), kind="ellipse")
    c = s.obj("Mancha", grad_("#E0103A", "#2A0C6A", 0), lambda fr, u: (960 + 30 * math.sin(u * 1.5), 540,
                                                                       1250 * k(fr, 6, 15), 560 * k(fr, 6, 15),
                                                                       -6 + 4 * math.sin(u), 1), kind="ellipse")
    wiggle(c, 36, 320, 1.0, 2)
    for i, (text, ink, at) in enumerate((("LIQUID", (650, 420, 1290, 510), 21), ("TITLE", (708, 570, 1230, 660), 33))):
        c = s.say(text, ink, M, 700, WHITE, "Título" if i == 0 else "Título 2", layers=outline_text(WHITE, 3))
        anim(s, c, at, "fade", stagger=0.1, duration=0.15)
    dot_grid(s, 1500, 60, 10, 3, 34, 30, size=6)
    dot_grid(s, 60, 900, 10, 3, 34, 33, size=6, name="Puntos 2")
    return t


# --- 18. BIG TEXT: a dark room of grid lines; red glowing BIG slides in, grey TEXT rises behind ------------------
def big_text():
    D = dur_for(1.4, 1.4)
    t = _t("big-text", "Texto grande rojo en una sala oscura", "Big red text in a dark room", 12124, D, ["grande"])
    s = S(t, D)
    bg(s, "#121212")
    for i, xb in enumerate(range(-1200, 3200, 400)):
        x0, y0, x1, y1 = 960 + (xb - 960) * 0.3, 780, xb, 1080
        ang = math.degrees(math.atan2(y1 - y0, x1 - x0))
        ln = math.hypot(x1 - x0, y1 - y0)
        s.obj(f"Línea {i + 1}", solid("#2E2E2E"), lambda fr, u, x0=x0, x1=x1, ang=ang, ln=ln: (
            (x0 + x1) / 2, 930 + 200 * (1 - k(fr, 0, 12)), ln, 3, ang, k(fr, 0, 6)))
    for i, y in enumerate((780, 900, 1040)):
        s.rect(f"Piso {i + 1}", solid("#2E2E2E"), lambda fr, u, y=y: (0, y + 200 * (1 - k(fr, 0, 12)), 1920,
                                                                      y + 3 + 200 * (1 - k(fr, 0, 12))))
    zoom = lambda fr: 1.12 - 0.12 * k(fr, 15, 30)  # noqa: E731
    c = s.say("TEXT", (420, 480, 1540, 840), M, 900, "#2E2E2E", "Título 2",
              geom=lambda fr, u: (*s.about((420, 480, 1540, 840), 960, 480, zoom(fr)), zoom(fr), 0, 1))
    anim(s, c, 24, "rise", stagger=0.05, duration=0.35)
    tight(c, -0.04)
    c = s.say("BIG", (580, 140, 1360, 480), M, 900, "#E3061F", layers=[shadow("#E3061F", 0, 0, 60, 0.6),
                                                                       fill("#E3061F")],
              geom=lambda fr, u: (*s.about((580, 140, 1360, 480), 960, 480, zoom(fr)), zoom(fr), 0, 1))
    anim(s, c, 15, "im-motion-blur-slide", stagger=0.08, duration=0.35, order="backward")
    tight(c, -0.05)
    return t


# --- 19. BEST VIDEO: blue and purple waves; the letters crash in from big; a red WATCH NOW tag -------------------
def best_video():
    D = dur_for(1.8, 1.0)
    t = _t("best-video", "Título grande sobre ondas azules", "Big title on blue waves", 12125, D, ["ondas"])
    s = S(t, D)
    swirl(s, 0, n=18, turn=-20.0, cols=SWIRL_BLUE, base="#0A0628")
    zoom = lambda fr: 1.08 - 0.08 * k(fr, 15, 36)  # noqa: E731
    for i, (text, ink, at) in enumerate((("BEST", (420, 240, 1500, 510), 15), ("VIDEO", (300, 540, 1620, 870), 21))):
        c = s.say(text, ink, M, 900, WHITE, "Título" if i == 0 else "Título 2", layers=SOFT,
                  geom=lambda fr, u, ink=ink: (*s.about(ink, 960, 540, zoom(fr)), zoom(fr), 0, 1))
        anim(s, c, at, "im-crash-from-big", stagger=0.12, duration=0.3, order="forward")
        tight(c, -0.04)
    s.obj("Etiqueta", solid("#E0145A"), lambda fr, u: (960, 540, 540 * k(fr, 42, 6), 92, 0, 1))
    s.say("WATCH NOW", (846, 522, 1074, 560), M, 500, "#FF7AA0", "Texto",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 46, 4)))
    return t


# --- 20. MODERN BOLD TITLE: a pink box rises; the outlined words close up; hatched circles pop around ------------
def modern_bold():
    D = dur_for(1.6, 1.0)
    t = _t("modern-bold", "Título con contorno en caja rosa", "Outlined title in a pink box", 12126, D, ["caja"])
    s = S(t, D)
    bg(s, "#161616")

    def box(fr, u):
        top = 1080 - (1080 - 168) * k(fr, 0, 15)
        w = 480 + 240 * k(fr, 9, 21) + 60 * k(fr, 30, 30)
        return 960 - w / 2, top, 960 + w / 2, top + 732 * k(fr, 0, 9)
    s.rect("Caja", [__import__("scene").gradient([(0.0, "#F0124A"), (0.75, "#D400D0"), (1.0, "#161616", 0.0)],
                                                 angle=90), __import__("scene").no_stroke()], box)
    for i, (text, ink, at) in enumerate((("MODERN", (580, 340, 1360, 460), 21), ("BOLD", (720, 480, 1220, 600), 33),
                                         ("TITLE", (760, 640, 1180, 760), 45))):
        c = s.say(text, ink, M, 700, WHITE, f"Título {i + 1}" if i else "Título", layers=outline_text(WHITE, 3))
        anim(s, c, at, "converge", stagger=0.04, duration=0.6, spread=0.8, blur=0)
    for i, (x, y, d, kind, at) in enumerate(((1310, 120, 90, "ring", 36), (120, 300, 200, "hatch", 39),
                                             (1800, 760, 240, "hatch", 42), (260, 1010, 120, "ring", 45),
                                             (1760, 1040, 60, "ring", 48))):
        if kind == "ring":
            s.obj(f"Aro {i + 1}", ring("#E0145A" if i % 2 else "#C000C0", 8), lambda fr, u, x=x, y=y, d=d, at=at: (
                x, y, d * k(fr, at, 6), d * k(fr, at, 6), 0, 1), kind="ellipse", base=(d, d))
        else:
            segs = []
            for j in range(-6, 7):
                c_ = j * 7.0
                h_ = math.sqrt(max(0.0, 50 ** 2 - c_ ** 2))
                a_ = (50 + c_ / math.sqrt(2) - h_ / math.sqrt(2), 50 + c_ / math.sqrt(2) + h_ / math.sqrt(2))
                b_ = (50 + c_ / math.sqrt(2) + h_ / math.sqrt(2), 50 + c_ / math.sqrt(2) - h_ / math.sqrt(2))
                segs.append(f"M {a_[0]:.2f} {a_[1]:.2f} L {b_[0]:.2f} {b_[1]:.2f}")
            hatch = " ".join(segs)
            s.obj(f"Círculo {i + 1}", ring("#C000C0", 3), lambda fr, u, x=x, y=y, d=d, at=at: (
                x, y, d * k(fr, at, 8), d * k(fr, at, 8), 30 * u, 1), path=hatch)
    return t


# --- 21. The world's best motion graphic design: dark red waves; three spread lines close up ------------------
def worlds_best():
    D = dur_for(1.6, 1.2)
    t = _t("frase-ondas-rojas", "Frase en tres líneas sobre ondas rojas", "Three-line phrase on red waves", 12127, D,
           ["ondas", "frase"])
    s = S(t, D)
    bg(s, "#D80026")
    for i in range(8):
        x0 = -900 + 380 * i
        pts = [(x0 + 140 * math.sin(y / 300 + i * 0.6), y) for y in range(-900, 2000, 100)]
        poly_pts = pts + [(3600, 2000), (3600, -900)]
        xs, ys = [p[0] for p in poly_pts], [p[1] for p in poly_pts]
        bx0, by0 = min(xs), min(ys)
        bw, bh = max(xs) - bx0, max(ys) - by0
        path = poly([((x - bx0) / bw * 100, (y - by0) / bh * 100) for x, y in poly_pts])
        col = ("#D00024", "#BC0020", "#A8001D", "#94001A", "#800017", "#6C0014", "#580010", "#44000C")[i]
        s.obj(f"Onda {i + 1}", solid(col), lambda fr, u, bx0=bx0, by0=by0, bw=bw, bh=bh, i=i: (
            *rot_pt(bx0 + bw / 2 - 30 * u + 400 * (1 - k(fr, i, 15)), by0 + bh / 2, -35), bw, bh, -35, 1), path=path)
    lines = (("The world's", (200, 360, 960, 448), 15), ("best motion", (200, 486, 920, 568), 18),
             ("graphic design.", (200, 604, 1160, 700), 21))
    for i, (text, ink, at) in enumerate(lines):
        c = s.say(text, ink, M, 700, WHITE, f"Título {i + 1}" if i else "Título", align="left")
        spacing(s, c, lambda fr, u: 0.32 * (1 - k(fr, 48, 12)))
        anim(s, c, at, "blur-in", stagger=0.03, duration=0.3, blur=16)
    c = s.say("INTRODUCING", (200, 232, 420, 244), M, 600, "#5A0010", "Texto 2", align="left")
    anim(s, c, 24, "fade", stagger=0.03, duration=0.1)
    s.say("LEARN MORE", (200, 812, 400, 826), M, 600, "#5A0010", "Texto", align="left",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 36, 9)))
    return t


TEMPLATES = [subscribe_bar, like_column, like_stack, like_badge, like_row, op_blobs, op_target, op_logo_fly,
             op_avatar_iris, op_chevrons, op_avatar_bands, op_white, op_waves, big_title, strong_titles, squiggle_lines,
             liquid_title, big_text, best_video, modern_bold, worlds_best]

# --- social glyphs ----------------------------------------------------------------------------------------------
BIRD = ("M 100 18 C 96 20 92 21 88 22 C 92 19 95 15 96 11 C 92 13 88 15 83 16 C 76 8 63 8 56 16 C 52 21 51 27 52 32 "
        "C 35 31 20 23 9 10 C 3 20 6 32 15 38 C 12 38 9 37 6 36 C 6 46 13 54 22 56 C 19 57 16 57 13 57 "
        "C 16 65 23 70 31 70 C 23 77 13 80 2 79 C 12 85 23 88 35 88 C 72 88 92 57 91 30 C 95 27 98 23 100 18 Z")


def social(s, kind, cx, cy, size, colour, at, name=None, n=6):
    """A simple glyph of a social network (drawn, not a logo file): ig, tw, fb, in, be, pin, wa, yt."""
    nm = name or f"Icono ({kind})"
    sc = lambda fr: k(fr, at, n)  # noqa: E731
    if kind == "ig":
        s.obj(nm, ring(colour, size * 0.1), lambda fr, u: (cx, cy, size * sc(fr), size * sc(fr), 0, 1),
              radius=size * 0.28, base=(size, size))
        s.obj(f"{nm} 2", ring(colour, size * 0.1), lambda fr, u: (cx, cy, size * 0.46 * sc(fr), size * 0.46 * sc(fr), 0,
                                                                  1), kind="ellipse", base=(size * 0.46, size * 0.46))
        s.obj(f"{nm} 3", solid(colour), lambda fr, u: (cx + size * 0.27, cy - size * 0.27, size * 0.12 * sc(fr),
                                                       size * 0.12 * sc(fr), 0, 1), kind="ellipse")
    elif kind == "tw":
        s.obj(nm, solid(colour), lambda fr, u: (cx, cy, size * sc(fr), size * 0.82 * sc(fr), 0, 1), path=BIRD)
    elif kind == "yt":
        s.obj(nm, solid(colour), lambda fr, u: (cx, cy, size * sc(fr), size * 0.7 * sc(fr), 0, 1), radius=size * 0.18,
              base=(size, size * 0.7))
        s.obj(f"{nm} 2", solid(WHITE), lambda fr, u: (cx + size * 0.04, cy, size * 0.3 * sc(fr), size * 0.32 * sc(fr),
                                                      0, 1), path=TRIANGLE)
    elif kind == "wa":
        s.obj(nm, ring(colour, size * 0.1), lambda fr, u: (cx, cy, size * sc(fr), size * sc(fr), 0, 1), kind="ellipse",
              base=(size, size))
        s.obj(f"{nm} 2", solid(colour), lambda fr, u: (cx, cy, size * 0.42 * sc(fr), size * 0.42 * sc(fr), -30, 1),
              path="M 20 0 L 40 0 L 45 25 L 35 35 C 45 55 55 65 70 70 L 80 60 L 100 65 L 100 85 C 60 100 0 40 20 0 Z")
    else:
        text = {"fb": "f", "in": "in", "be": "Bē", "pin": "P"}[kind]
        w = size * (0.5 if kind == "fb" else 0.9)
        s.say(text, (cx - w / 2, cy - size * 0.42, cx + w / 2, cy + size * 0.42), M, 800, colour, nm,
              geom=lambda fr, u: (0, 0, max(0.01, sc(fr)), 0, 1))


def handle_rows(s, items, at, size=34, colour=RED, text_colour=WHITE, step=3):
    """Rows of glyph + «@YourName»: items = [(kind, x, y), ...]."""
    for i, (kind, x, y) in enumerate(items):
        social(s, kind, x, y, size, colour, at + step * i, name=f"Red {i + 1}")
        c = s.say("@YourName", (x + size * 0.9, y - size * 0.32, x + size * 0.9 + size * 3.4, y + size * 0.32), M,
                  600, text_colour, f"Red {i + 1} (nombre)", align="left")
        anim(s, c, at + step * i + 2, "fade", stagger=0.03, duration=0.1, order="random")


def drawn_box(s, name, rect, at, n=15, colour=RED, width=5, fill_at=None, fill_colour="#3A3A3A"):
    """A video box: its outline draws itself from its top-left corner; then it fills grey."""
    x0, y0, x1, y1 = rect
    if fill_at is not None:
        s.rect(f"{name} (relleno)", solid(fill_colour), lambda fr, u: rect, op=lambda fr, u: k(fr, fill_at, 6))
    s.outline(name, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], width, colour, at=at, n=n, closed=True)


def subscribe_disc(s, cx, cy, d, at, outer=True, ring_col=RED, disc="#3A3A3A", name="Suscribirse"):
    """The end screen's round subscribe slot: a grey disc with a red ring and an outer grey ring that breathes."""
    if outer:
        s.obj(f"{name} (aro exterior)", ring("#555555", 10), lambda fr, u: (
            cx, cy, d * (1.3 + 0.06 * math.sin(u * 3)) * k(fr, at + 6, 9), d * (1.3 + 0.06 * math.sin(u * 3))
            * k(fr, at + 6, 9), 0, 1), kind="ellipse", base=(d * 1.4, d * 1.4))
    s.obj(name, solid(disc), lambda fr, u: (cx, cy, d * k(fr, at + 3, 9), d * k(fr, at + 3, 9), 0, 1), kind="ellipse")
    c = s.obj(f"{name} (aro)", ring(ring_col, 6), lambda fr, u: (cx, cy, d, d, -90, 1), kind="ellipse")
    knob(s, c, "trimEnd", lambda fr, u: 100 * k(fr, at, 12))


ARROW = "M 70 0 C 30 20 20 60 40 92 L 28 92 L 48 100 L 56 80 L 46 88 C 30 60 38 26 76 6 Z"


def _e(id, es, en, order, dur, tags=(), thumb=None):
    return _p(id, es, en, order, dur, "pantallas-finales", ["pantalla final"] + list(tags), thumb)


# --- 22. End card: a red tint rises over the footage, a dark column opens, two video boxes and a subscribe disc ---
def end_column():
    D = dur_for(2.6, 1.2)
    t = _e("final-columna", "Pantalla final: columna oscura sobre video teñido", "End screen: dark column over tinted "
           "video", 12140, D, ["video"], thumb=3.6)
    s = S(t, D)
    footage(s, "h-portrait-03")
    from scene import gradient, no_stroke
    s.rect("Tinte", [gradient([(0.0, "#3A0008", 0.35), (1.0, "#C0001A", 0.9)], angle=180), no_stroke()],
           lambda fr, u: (-10, 1090 - 1100 * k(fr, 0, 9), 1930, 1090))
    s.rect("Columna", solid("#1E1E1E"), lambda fr, u: (960 - 372 * k(fr, 15, 9), -10, 960 + 372 * k(fr, 15, 9), 1090),
           op=lambda fr, u: k(fr, 12, 2))
    subscribe_disc(s, 960, 312, 330, 24)
    for i, (rect, label, ink) in enumerate((((48, 360, 672, 720), "NEWEST VIDEO", (180, 752, 540, 782)),
                                            ((1248, 360, 1872, 720), "NEXT VIDEO", (1410, 752, 1710, 782)))):
        drawn_box(s, f"Video {i + 1}", rect, 30 + 3 * i, 18, fill_at=51)
        c = s.say(label, ink, M, 600, WHITE, f"Video {i + 1} (texto)")
        anim(s, c, 36, "fade", stagger=0.04, duration=0.1, order="random")
    s.rect("Línea", solid(WHITE), lambda fr, u: (960 - 120 * k(fr, 45, 12), 618, 960 + 120 * k(fr, 45, 12), 622))
    c = s.say("Your Name", (840, 650, 1080, 700), M, 800, RED, "Canal")
    anim(s, c, 66, "fade", stagger=0.05, duration=0.12, order="random")
    for i, kind in enumerate(("ig", "fb", "tw")):
        social(s, kind, 900 + 60 * i, 740, 40, RED, 60 + 4 * i)
    return t


# --- 23. End card: silky dark waves, a recommended video box, LIKE COMMENT SHARE and a subscribe disc ------------
def end_like():
    D = dur_for(2.6, 1.0)
    t = _e("final-like-share", "Pantalla final: video recomendado y like, comment, share", "End screen: recommended "
           "video and like, comment, share", 12141, D, ["redes"], thumb=3.6)
    s = S(t, D)
    swirl(s, 0, n=14, turn=-8.0, cols=("#1A1A1A", "#2A2A2A", "#141414", "#333333", "#1E1E1E", "#262626", "#101010"),
          base="#141414")
    drawn_box(s, "Video", (152, 144, 1032, 704), 12, 15, fill_at=30)
    s.rect("Video (barra)", solid(RED), lambda fr, u: (152, 144, 152 + 880 * k(fr, 30, 9), 200))
    c = s.say("RECOMMENDED VIDEO", (200, 156, 980, 188), M, 600, WHITE, "Video (texto)", align="left")
    anim(s, c, 33, "fade", stagger=0.03, duration=0.1, order="random")
    subscribe_disc(s, 1540, 740, 320, 6, outer=False)
    arc = s.obj("Suscribirse (vuelta)", ring(WHITE, 6), lambda fr, u: (1540, 740, 370, 370, 140 * u, k(fr, 24, 3)),
                kind="ellipse")
    knob(s, arc, "trimEnd", lambda fr, u: 35 + 25 * math.sin(u * 2))
    for i, (text, ink, wt, at) in enumerate((("DON'T FORGET TO", (1332, 162, 1740, 180), 700, 21),
                                             ("LIKE", (1332, 198, 1740, 348), 800, 27),
                                             ("COMMENT", (1332, 360, 1740, 420), 700, 33),
                                             ("SHARE", (1332, 438, 1740, 540), 800, 39))):
        c = s.say(text, ink, M, wt, WHITE, f"Texto {i + 1}" if i else "Texto", align="left")
        anim(s, c, at, "converge", stagger=0.03, duration=0.4, spread=0.5, blur=0)
    s.obj("Flecha", solid(WHITE), lambda fr, u: (1272, 580, 60 * k(fr, 45, 6), 110 * k(fr, 45, 6), 10, 1), path=ARROW)
    handle_rows(s, [("tw", 232, 772), ("ig", 664, 772), ("be", 232, 856), ("in", 664, 856)], 42, size=50, colour=WHITE)
    return t


def streaks(s, at=0, name="Raya", colours=("#C0001A", "#7A0010", "#E3061F", "#4A0008"), base="#0E0E0E", n=14):
    """Soft red streaks running diagonally (blurred light)."""
    import random
    rnd = random.Random(5)
    bg(s, base)
    for i in range(n):
        x, y = rnd.uniform(-200, 2100), rnd.uniform(-200, 1300)
        w, h = rnd.uniform(900, 2000), rnd.uniform(80, 260)
        col = colours[i % len(colours)]
        sp = rnd.uniform(40, 120)
        s.obj(f"{name} {i + 1}", [shadow(col, 0, 0, 120, 1.0), fill(col)], lambda fr, u, x=x, y=y, w=w, h=h, sp=sp: (
            x + sp * u, y - sp * u, w, h, -40, 0.5 * k(fr, at, 9)), radius=h / 2, base=(w, h))


# --- 24. End card: red streaks; subscribe disc with CLICK HERE TO SUBSCRIBE, THANKS FOR WATCHING and a video box --
def end_thanks():
    D = dur_for(2.6, 1.0)
    t = _e("final-gracias", "Pantalla final: gracias por ver y suscribirse", "End screen: thanks for watching and "
           "subscribe", 12142, D, ["gracias"], thumb=3.6)
    s = S(t, D)
    streaks(s)
    subscribe_disc(s, 390, 360, 300, 15, outer=False)
    arc = s.obj("Suscribirse (vuelta)", ring(WHITE, 5), lambda fr, u: (390, 360, 340, 340, 150 * u, k(fr, 39, 3)),
                kind="ellipse")
    knob(s, arc, "trimEnd", lambda fr, u: 40 + 20 * math.sin(u * 2))
    s.obj("Flecha", solid(WHITE), lambda fr, u: (640, 410, 70 * k(fr, 54, 6), 130 * k(fr, 54, 6), 20, 1), path=ARROW)
    c = s.say("CLICK HERE TO", (132, 528, 648, 572), M, 600, WHITE, "Texto")
    anim(s, c, 27, "fade", stagger=0.04, duration=0.1, order="random")
    c = s.say("SUBSCRIBE", (132, 600, 648, 672), M, 900, "#E3061F", "Título 2")
    anim(s, c, 33, "fade", stagger=0.04, duration=0.1, order="random")
    s.rect("Línea", solid(WHITE), lambda fr, u: (130, 742, 130 + 460 * k(fr, 57, 12), 746))
    for i, kind in enumerate(("fb", "tw", "ig")):
        social(s, kind, 290 + 90 * i, 810, 56, WHITE, 63 + 3 * i)
    c = s.say("THANKS FOR WATCHING!", (900, 162, 1758, 228), M, 800, WHITE)
    anim(s, c, 24, "fade", stagger=0.04, duration=0.1, order="random")
    c = s.say("Don't forget to like, subscribe and share", (920, 262, 1740, 290), M, 500, "#DDDDDD", "Texto 2")
    anim(s, c, 30, "fade", stagger=0.01, duration=0.1, order="random")
    drawn_box(s, "Video", (900, 360, 1770, 858), 21, 18, fill_at=39)
    s.rect("Video (etiqueta)", solid(RED), lambda fr, u: (1335 - 120 * k(fr, 42, 6), 846, 1335 + 120 * k(fr, 42, 6),
                                                          884))
    c = s.say("NEXT VIDEO", (1260, 858, 1410, 872), M, 700, WHITE, "Video (texto)")
    anim(s, c, 45, "fade", stagger=0.03, duration=0.1)
    return t


# --- 25. End card: a dark band slides over the footage; subscribe disc, thanks text with name and icons, video box -
def end_band():
    D = dur_for(2.6, 1.0)
    t = _e("final-banda", "Pantalla final: banda oscura sobre el video", "End screen: dark band over the video", 12143,
           D, ["video"], thumb=3.6)
    s = S(t, D)
    footage(s, "h-city-02")
    s.rect("Banda", solid("#1C1C1C", 0.96), lambda fr, u: (-10, 120, -10 + 1940 * k(fr, 0, 15), 960))
    subscribe_disc(s, 270, 540, 330, 12)
    s.rect("Divisor", solid(WHITE), lambda fr, u: (550, 540 - 180 * k(fr, 18, 9), 554, 540 + 180 * k(fr, 18, 9)))
    c = s.say("Thanks for watching!", (690, 372, 1068, 398), M, 600, WHITE, "Título")
    anim(s, c, 24, "fade", stagger=0.03, duration=0.1, order="random")
    for i, (line, y) in enumerate((("Please subscribe my channel", 488), ("and follow me on social media", 528))):
        c = s.say(line, (600, y, 1160, y + 28), M, 500, "#DDDDDD", f"Texto {i + 1}" if i else "Texto")
        anim(s, c, 30 + 3 * i, "fade", stagger=0.01, duration=0.1, order="random")
    c = s.say("@YourName", (700, 640, 1060, 690), M, 800, RED, "Canal")
    anim(s, c, 42, "fade", stagger=0.04, duration=0.1, order="random")
    for i, kind in enumerate(("tw", "pin", "ig")):
        social(s, kind, 780 + 100 * i, 742, 58, RED, 36 + 4 * i)
    drawn_box(s, "Video", (1200, 360, 1830, 720), 21, 18, fill_at=39)
    return t


TEMPLATES += [end_column, end_like, end_thanks, end_band]


# --- Backgrounds (35–37 s: a 2×2 grid, a 4×4 grid, then two full screen): loops that drift ------------------------
BG_D = 6.0


def _bgt(id, es, en, order, tags=()):
    t = _p(id, es, en, order, BG_D, "elementos", ["fondo"] + list(tags), thumb=3.0)
    return t, O(t, BG_D)


def bg_chevrons():
    t, s = _bgt("fondo-flechas", "Fondo: flechas rojas que avanzan", "Background: red chevrons moving on", 12160,
                ["flechas"])
    bg(s, "#2A2A2A")
    chev = poly([(0, 0), (40, 0), (100, 50), (40, 100), (0, 100), (60, 50)])
    for i in range(8):
        s.obj(f"Flecha {i + 1}", solid("#E3061F"), lambda fr, u, i=i: (
            -360 + ((i * 360 + 120 * u) % 2880), 540, 300, 1300, 0, 1), path=chev)
    return t


def bg_play_dots():
    t, s = _bgt("fondo-botones", "Fondo: botones de play en filas", "Background: rows of play buttons", 12161,
                ["youtube"])
    bg(s, "#5A0010")
    for r in range(8):
        for c in range(14):
            x0, y0 = c * 170 - 60 + (85 if r % 2 else 0), r * 160 - 40
            s.obj(f"Botón {r + 1}.{c + 1}", solid("#E3061F"), lambda fr, u, x0=x0, y0=y0: (
                x0 + 40 * u, y0 - 40 * u, 120, 120, 0, 1), kind="ellipse")
            s.obj(f"Botón {r + 1}.{c + 1} (play)", solid(WHITE), lambda fr, u, x0=x0, y0=y0: (
                x0 + 6 + 40 * u, y0 - 40 * u, 42, 46, 0, 1), path=TRIANGLE)
    return t


def bg_blocks():
    t, s = _bgt("fondo-bloques", "Fondo: bloques blancos con cuadros rojos", "Background: white blocks with red "
                "squares", 12162, ["bloques"])
    bg(s, "#5A5A5A")
    for r in range(-2, 9):
        for c in range(-1, 12):
            cx, cy = c * 200 + (100 if r % 2 else 0), r * 150
            g = (lambda fr, u, cx=cx, cy=cy: (*rot_pt(cx + 50 * u, cy, -18), 170, 110, -18, 1))
            s.obj(f"Bloque {r + 3}.{c + 2}", [shadow("#000000", 0, 10, 6, 0.4), fill("#F2F2F2")], g, radius=10,
                  base=(170, 110))
            s.obj(f"Bloque {r + 3}.{c + 2} (rojo)", solid("#E3061F"), lambda fr, u, g=g: (
                lambda v: (v[0], v[1], 70, 50, v[4], 1))(g(fr, u)), radius=6, base=(70, 50))
    return t


def bg_dark_liquid():
    t, s = _bgt("fondo-liquido-oscuro", "Fondo: líquido rojo oscuro", "Background: dark red liquid", 12163,
                ["líquido"])
    swirl(s, 0, n=16, turn=-75.0, cols=("#1A0004", "#7A0010", "#0A0A0A", "#C0001A", "#2A2A2A", "#5A0010", "#E0102A",
                                        "#0A0A0A", "#9A9A9A"), base="#0A0A0A")
    return t


def bg_torn_stripes():
    t, s = _bgt("fondo-rayas-onduladas", "Fondo: rayas rojas onduladas", "Background: wavy red stripes", 12164,
                ["ondas"])
    bg(s, "#3A0008")
    for i in range(8):
        y = -60 + 150 * i
        c = s.obj(f"Raya {i + 1}", solid("#E3061F" if i % 2 else "#B5001A"), lambda fr, u, y=y, i=i: (
            960, y + 20 * math.sin(u + i), 2300, 96, 0, 1))
        wiggle(c, 14, 30, 1.5, i)
    return t


def bg_thin_lines():
    t, s = _bgt("fondo-lineas", "Fondo: líneas rojas finas onduladas", "Background: thin wavy red lines", 12165,
                ["líneas"])
    bg(s, "#1E1E1E")
    import random
    rnd = random.Random(2)
    for i in range(130):
        x, y, ln = rnd.uniform(-200, 2100), rnd.uniform(-100, 1180), rnd.uniform(200, 520)
        pts = smooth([(0, 0), (ln * 0.33, -30), (ln * 0.66, 20), (ln, -10)], 6)
        ys = [p[1] for p in pts]
        bh = max(ys) - min(ys)
        path = "M " + " L ".join(f"{p[0] / ln * 100:.2f} {(p[1] - min(ys)) / bh * 100:.2f}" for p in pts)
        s.obj(f"Línea {i + 1}", ring("#E0102A", 4), lambda fr, u, x=x, y=y, ln=ln, bh=bh: (
            x + 70 * u, y + 40 * u, ln, bh, -25, 1), path=path)
    return t


def bg_thick_waves():
    t, s = _bgt("fondo-ondas-gruesas", "Fondo: ondas rojas gruesas", "Background: thick red waves", 12166, ["ondas"])
    bg(s, "#222222")
    pts = smooth([(x, 50 * math.sin(x / 140.0)) for x in range(-200, 2600, 140)], 4)
    bot = [(p[0], p[1] + 110) for p in pts][::-1]
    xs = [p[0] for p in pts]
    bw = max(xs) - min(xs)
    path = poly([((x - min(xs)) / bw * 100, (y + 55) / 220 * 100) for x, y in pts + bot])
    for i in range(7):
        y0 = -200 + 230 * i
        for j, (col, off) in enumerate((("#8A0012", 18), ("#E3061F", 0))):
            s.obj(f"Onda {i + 1}" + (" (sombra)" if j == 0 else ""), solid(col), lambda fr, u, y0=y0, off=off: (
                *rot_pt(960 - 60 * u + off, y0 + off, -30), bw, 220, -30, 1), path=path)
    return t


def bg_social_grid():
    t, s = _bgt("fondo-redes", "Fondo: iconos de redes sociales", "Background: social media icons", 12167, ["redes"])
    bg(s, "#24183A")
    kinds = ("ig", "tw", "fb", "yt", "in", "pin", "wa", "be")
    for r in range(6):
        for c in range(10):
            x, y = 130 + c * 186, 120 + r * 170
            col = ("#7A3BD0", "#C02BA0", "#5A2BB8", "#9A3BE0")[(r + c) % 4]
            s.obj(f"Círculo {r + 1}.{c + 1}", solid(col), lambda fr, u, x=x, y=y, r=r, c=c: (
                x, y, 120 + 8 * math.sin(u * 2 + r + c), 120 + 8 * math.sin(u * 2 + r + c), 0, 1), kind="ellipse")
            social(s, kinds[(r * 3 + c) % len(kinds)], x, y, 56, "#1A1030", -10, name=f"Icono {r + 1}.{c + 1}")
    return t


def bg_scatter_c():
    t, s = _bgt("fondo-arcos", "Fondo: arcos y rayas rojas sueltas", "Background: scattered red arcs and dashes",
                12168, ["formas"])
    bg(s, "#262626")
    import random
    rnd = random.Random(7)
    for i in range(40):
        x, y = rnd.uniform(0, 1920), rnd.uniform(0, 1080)
        a = rnd.uniform(0, 360)
        if i % 3 == 0:
            s.obj(f"Arco {i + 1}", ring("#E3061F", 20), lambda fr, u, x=x, y=y, a=a: (
                x + 30 * u, y - 20 * u, 96, 96, a + 40 * u, 1), path=arc(30, 300))
        else:
            s.obj(f"Raya {i + 1}", solid("#E3061F"), lambda fr, u, x=x, y=y, a=a: (
                x + 30 * u, y - 20 * u, 60, 16, a, 1), radius=8, base=(60, 16))
    return t


def bg_dots():
    t, s = _bgt("fondo-puntos", "Fondo: puntos rojos que laten", "Background: pulsing red dots", 12169, ["puntos"])
    bg(s, "#1E1E1E")
    for r in range(9):
        for c in range(17):
            x, y = 40 + c * 116 + (58 if r % 2 else 0), 40 + r * 124
            s.obj(f"Punto {r + 1}.{c + 1}", solid("#D0001E"), lambda fr, u, x=x, y=y, r=r, c=c: (
                x, y, 46 + 26 * math.sin(u * 2 + (r + c) * 0.7), 46 + 26 * math.sin(u * 2 + (r + c) * 0.7), 0, 1),
                kind="ellipse")
    return t


def bg_layers():
    t, s = _bgt("fondo-capas", "Fondo: capas rojas onduladas", "Background: layered red waves", 12170, ["ondas"])
    bg(s, "#3A0008")
    for i in range(7):
        x0 = 200 + 280 * i
        pts = [(x0 + 90 * math.sin(y / 120 + i), y) for y in range(-200, 1400, 80)]
        poly_pts = pts + [(3000, 1400), (3000, -200)]
        xs, ys = [p[0] for p in poly_pts], [p[1] for p in poly_pts]
        bx0, by0, bw, bh = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
        path = poly([((x - bx0) / bw * 100, (y - by0) / bh * 100) for x, y in poly_pts])
        col = ("#5A000E", "#760012", "#920016", "#AE001A", "#C8001E", "#DC0022", "#EE1030")[i]
        s.obj(f"Capa {i + 1}", [shadow("#000000", -12, 0, 30, 0.35), fill(col)], lambda fr, u, bx0=bx0, by0=by0,
              bw=bw, bh=bh, i=i: (*rot_pt(bx0 + bw / 2 + 30 * math.sin(u + i), by0 + bh / 2, 25), bw, bh, 25, 1),
              path=path)
    return t


def bg_stripes():
    t, s = _bgt("fondo-rayas", "Fondo: rayas rojas diagonales", "Background: diagonal red stripes", 12171, ["rayas"])
    bg(s, "#2A2A2A")
    for i in range(30):
        s.obj(f"Raya {i + 1}", solid("#E3061F"), lambda fr, u, i=i: (
            -600 + ((i * 110 + 60 * u) % 3300), 540, 40, 2600, 45, 1))
    return t


def bg_text_pattern():
    t, s = _bgt("fondo-texto", "Fondo: texto editable repetido", "Background: repeated editable text", 12172,
                ["texto"])
    bg(s, "#2A0A3A")
    for r in range(9):
        y = -60 + r * 140
        c = s.say("EDITABLE TEXT EDITABLE TEXT EDITABLE TEXT", (-400 + (r % 2) * 200, y, 2400 + (r % 2) * 200, y + 90),
                  M, 900, ("#C0127A", "#7A1AA0", "#E0145A")[r % 3], f"Texto {r + 1}" if r else "Texto",
                  geom=lambda fr, u, r=r: (((-1) ** r) * 80 * u, 0, 1, -12, 1))
        c["textStyle"]["wordWrap"] = False
    return t


def bg_crosses():
    t, s = _bgt("fondo-cruces", "Fondo: cruces rosas y blancas", "Background: pink and white crosses", 12173,
                ["formas"])
    bg(s, "#262626")
    cross = poly([(38, 0), (62, 0), (62, 38), (100, 38), (100, 62), (62, 62), (62, 100), (38, 100), (38, 62), (0, 62),
                   (0, 38), (38, 38)])
    cols = ("#F07A9A", "#FFFFFF", "#C8C8C8", "#E0145A", "#F4A0B8")
    for r in range(8):
        for c in range(13):
            x, y = 80 + c * 150, 70 + r * 135
            s.obj(f"Cruz {r + 1}.{c + 1}", solid(cols[(r * 5 + c * 3) % len(cols)]), lambda fr, u, x=x, y=y, r=r, c=c: (
                x, y, 70, 70, 45 + 90 * k(fr % 60, ((r + c) % 6) * 5, 12), 1), path=cross)
    return t


def bg_dashes():
    t, s = _bgt("fondo-guiones", "Fondo: guiones rojos que vuelan", "Background: flying red dashes", 12174, ["formas"])
    bg(s, "#262626")
    import random
    rnd = random.Random(11)
    for i in range(36):
        x, y, ln, sp = rnd.uniform(-200, 2000), rnd.uniform(0, 1080), rnd.uniform(40, 140), rnd.uniform(80, 220)
        s.obj(f"Guion {i + 1}", solid("#E3061F"), lambda fr, u, x=x, y=y, ln=ln, sp=sp: (
            (x + sp * u * 0.94) % 2200 - 100, y - sp * u * 0.34, ln, 14, -20, 1), radius=7, base=(ln, 14))
    return t


def bg_blue_liquid():
    t, s = _bgt("fondo-liquido-azul", "Fondo: líquido azul", "Background: blue liquid", 12175, ["líquido"])
    swirl(s, 0, n=16, turn=-70.0, cols=("#0A1AA0", "#1A4AE0", "#3A0A8A", "#18C0F0", "#0A0A40", "#5A2BD0", "#0A2A90",
                                        "#2A8AF0"), base="#0A0A40")
    return t


def bg_spiral():
    t, s = _bgt("fondo-espiral", "Fondo: espiral roja, blanca y gris", "Background: red, white and grey spiral", 12176,
                ["espiral"])
    bg(s, "#1A1A1A")
    for i, (r, col) in enumerate(((2600, "#3A3A3A"), (2200, WHITE), (1800, "#C0001A"), (1500, "#8A8A8A"),
                                  (1200, WHITE), (900, "#E3061F"), (650, "#5A5A5A"), (420, WHITE), (220, "#C0001A"))):
        s.obj(f"Espiral {i + 1}", ring(col, r * 0.12), lambda fr, u, r=r, i=i: (
            960, 540, r, r, 40 * i + 60 * u * (1 if i % 2 else 0.8), 1), path=arc(0, 200))
    # The reference (36.6 s) is a soft twirl: the bands blurred and twisted about the centre.
    adjust_fx(s, "Espiral (suave)", soft_specs(12.0) + [
        ("stylize.twirl", {"angle": lambda fr, u: 140 + 20 * u}, {"radius": 0.9, "centerX": 0.5, "centerY": 0.5})])
    return t


def bg_streaks():
    t, s = _bgt("fondo-destellos", "Fondo: destellos rojos diagonales", "Background: diagonal red streaks", 12177,
                ["luz"])
    streaks(s, -10, n=18)
    return t


TEMPLATES += [bg_chevrons, bg_play_dots, bg_blocks, bg_dark_liquid, bg_torn_stripes, bg_thin_lines, bg_thick_waves,
              bg_social_grid, bg_scatter_c, bg_dots, bg_layers, bg_stripes, bg_text_pattern, bg_crosses, bg_dashes,
              bg_blue_liquid, bg_spiral, bg_streaks]


# --- Simple titles (37–43 s, the TITLE grid; the «BOLD TITLES / TITLES ARE RESPONSIVE / CHANGE DURATION EASILY» of the
# After Effects shots at 43–68 s are these same templates with other words) -----------------------------------------
def _s(id, es, en, order, dur, tags=(), thumb=None):
    return _p(id, es, en, order, dur, "titulos-estilo", ["título", "simple"] + list(tags), thumb)


def t_boxes():
    D = dur_for(1.2, 1.2)
    t = _s("cajas-tecleadas", "Título en caja roja y caja blanca tecleadas", "Title typed in a red and a white box",
           12190, D, ["caja"])
    s = S(t, D)
    s.rect("Caja", solid("#E3061F"), lambda fr, u: (960 - (60 + 588 * lin(fr, 0, 30)), 378,
                                                    960 + (60 + 588 * lin(fr, 0, 30)), 522), op=lambda fr, u: k(fr, 0, 1))
    s.rect("Caja 2", solid(WHITE), lambda fr, u: (960 - (40 + 458 * lin(fr, 6, 27)), 570,
                                                  960 + (40 + 458 * lin(fr, 6, 27)), 696), op=lambda fr, u: k(fr, 6, 1))
    c = s.say("LUCA'S ADVENTURE", (348, 420, 1572, 480), M, 500, WHITE)
    spacing(s, c, lambda fr, u: 0.32)
    s.typed(c, 1, stagger=0.06, duration=0.04)
    c = s.say("This week: desert adventure", (510, 612, 1410, 650), M, 500, "#E3061F", "Texto")
    spacing(s, c, lambda fr, u: 0.12)
    s.typed(c, 7, stagger=0.033, duration=0.03)
    return t


def t_top10():
    D = dur_for(1.2, 1.4)
    t = _s("top-10", "Título con dos rayas rojas debajo", "Title with two red lines under it", 12191, D, ["lista"])
    s = S(t, D)
    c = s.say("TOP 10 VIDEOS", (420, 432, 1500, 540), M, 800, WHITE)
    s.typed(c, 0, stagger=0.04, duration=0.12, preset="pop")
    s.rect("Raya", solid("#E3061F"), lambda fr, u: (420, 596, 420 + 330 * k(fr, 12, 9), 608))
    s.rect("Raya 2", solid("#E3061F"), lambda fr, u: (1500 - 330 * k(fr, 12, 9), 596, 1500, 608))
    c = s.say("on youtube", (810, 576, 1110, 616), M, 500, WHITE, "Texto")
    s.typed(c, 21, stagger=0.04, duration=0.06, preset="fade")
    return t


def t_popular():
    D = dur_for(1.4, 1.2)
    t = _s("barra-vertical", "Título en cuatro líneas sobre barra roja", "Four-line title over a red bar", 12192, D,
           ["barra"])
    s = S(t, D)
    s.rect("Barra", solid("#E3061F"), lambda fr, u: (510 + 120 * (1 - k(fr, 3, 6)) * 0, 948 - 738 * k(fr, 6, 15)
                                                     - 12 * k(fr, 0, 3), 750, 960), op=lambda fr, u: k(fr, 0, 2))
    lines = (("ON YOUTUBE", (630, 672, 1410, 768), 15), ("VIDEOS", (630, 552, 1068, 648), 21),
             ("POPULAR", (630, 432, 1188, 528), 21), ("THE MOST", (642, 330, 1230, 408), 24))
    for i, (text, ink, at) in enumerate(lines):
        c = s.say(text, ink, M, 800, WHITE, f"Título {i + 1}" if i else "Título", align="left")
        spacing(s, c, lambda fr, u, at=at: 0.45 * (1 - k(fr, at, 9)))
        anim(s, c, at, "fade", stagger=0.02, duration=0.12)
    c = s.say("By Your Name", (630, 862, 800, 880), M, 500, WHITE, "Texto", align="left")
    anim(s, c, 30, "fade", stagger=0.03, duration=0.1)
    return t


def t_modern():
    D = dur_for(1.2, 1.2)
    t = _s("modern-title", "Título entre rayas rojas", "Title between red lines", 12193, D, ["rayas"])
    s = S(t, D)
    s.rect("Raya", solid("#E3061F"), lambda fr, u: (960 - 420 * k(fr, 0, 6), 270 + 498 * k(fr, 6, 15),
                                                    960 + 420 * k(fr, 0, 6), 282 + 498 * k(fr, 6, 15)))
    for i, (x0, x1) in enumerate(((540, 792), (1122, 1380))):
        s.rect(f"Raya {i + 2}", solid("#E3061F"), lambda fr, u, x0=x0, x1=x1: (
            x0, 276, x0 + (x1 - x0) * k(fr, 21, 6), 288))
    c = s.say("THIS IS", (880, 290, 1040, 308), M, 600, "#E3061F", "Texto")
    anim(s, c, 24, "fade", stagger=0.04, duration=0.1)
    for i, (text, ink, at) in enumerate((("MODERN", (528, 360, 1392, 522), 18), ("TITLE", (690, 570, 1230, 720), 21))):
        c = s.say(text, ink, M, 800, WHITE, "Título" if i == 0 else "Título 2")
        anim(s, c, at, "fade", stagger=0.04, duration=0.2, order="random")
    return t


def t_rate():
    D = dur_for(1.4, 1.2)
    t = _s("no-olvides-calificar", "Título: no olvides calificar, en un marco rojo", "Title: don't forget to rate, in a "
           "red frame", 12194, D, ["marco"])
    s = S(t, D)
    for i, (text, ink, col, at) in enumerate((("DON'T", (660, 342, 1140, 450), WHITE, 0),
                                              ("FORGET", (660, 492, 1242, 600), "#F27A9A", 6),
                                              ("TO RATE", (660, 642, 1272, 750), "#E8264A", 12))):
        c = s.say(text, ink, M, 800, col, f"Título {i + 1}" if i else "Título", align="left")
        s.typed(c, at, stagger=0.04, duration=0.06)
    pts = [(1368, 270), (552, 270), (552, 798), (1368, 798), (1368, 260)]
    s.outline("Marco", pts, 8, "#E3061F", at=24, n=15, closed=False)
    c = s.say("CLICK ON THE BELL TO GET NOTIFICATIONS", (552, 842, 1368, 868), M, 500, WHITE, "Texto")
    s.typed(c, 21, stagger=0.015, duration=0.03)
    return t


def t_pro():
    D = dur_for(1.2, 1.2)
    t = _s("como-un-pro", "Título escalonado bajo una línea roja", "Stepped title under a red line", 12195, D,
           ["escalonado"])
    s = S(t, D)
    s.rect("Raya", solid("#E3061F"), lambda fr, u: (1422 - 990 * k(fr, 3, 18), 278, 1422, 292))
    s.say("HOW TO BE A MOTION DESIGNER", (432, 252, 1230, 274), M, 600, WHITE, "Texto", align="left",
              reveal=lambda fr: (1422 - 990 * k(fr, 3, 18), 0, 1430, 1080), shift=lambda fr: (300 * (1 - k(fr, 3, 18)), 0))
    for i, (text, ink, at) in enumerate((("ANIMATE", (510, 318, 1182, 438), 21), ("LIKE A", (690, 468, 1140, 588), 27),
                                         ("PRO", (870, 618, 1170, 738), 27))):
        c = s.say(text, ink, M, 800, WHITE, f"Título {i + 1}" if i else "Título", align="right")
        spacing(s, c, lambda fr, u, at=at: 0.5 * (1 - k(fr, at, 6)))
        anim(s, c, at, "fade", stagger=0.02, duration=0.1)
    return t


def t_design():
    D = dur_for(1.2, 1.0)
    t = _s("design", "Título rojo de letras que caen", "Red title with falling letters", 12196, D, ["caída"])
    s = S(t, D)
    c = s.say("DESIGN", (372, 378, 1548, 540), M, 800, "#E3061F")
    spacing(s, c, lambda fr, u: 0.22)
    anim(s, c, 0, "drop", stagger=0.06, duration=0.3, order="random")
    s.rect("Raya", solid("#E3061F"), lambda fr, u: (1548 - 396 * k(fr, 18, 9), 606, 1548, 630))
    c = s.say("YOUR TEXT", (372, 604, 600, 628), M, 600, WHITE, "Texto", align="left")
    spacing(s, c, lambda fr, u: 0.3)
    s.typed(c, 27, stagger=0.05, duration=0.05)
    return t


def t_watch_box():
    D = dur_for(1.5, 1.2)
    t = _s("ver-siguiente-caja", "Título: mira el siguiente, en caja blanca", "Title: watch next, in a white box",
           12197, D, ["caja"])
    s = S(t, D)

    def box(fr, u, dx=0, dy=0):
        w = 30 + 822 * k(fr, 3, 12)
        h = 336 + 84 * k(fr, 9, 6)
        return 570 + dx, 270 + 420 / 2 - h / 2 + dy, 570 + w + dx, 270 + 420 / 2 + h / 2 + dy
    s.rect("Caja (sombra)", solid("#E3061F"), lambda fr, u: box(fr, u, 24 * k(fr, 39, 6), 24 * k(fr, 39, 6)),
           op=lambda fr, u: k(fr, 39, 2))
    s.rect("Caja", solid(WHITE), box, op=lambda fr, u: k(fr, 0, 1))
    for i, (text, ink, at) in enumerate((("WATCH", (600, 288, 1200, 402), 15), ("NEXT", (600, 438, 1068, 552), 12))):
        c = s.say(text, ink, M, 800, "#E3061F", "Título" if i == 0 else "Título 2", align="left")
        spacing(s, c, lambda fr, u, at=at: 0.12 + 0.2 * (1 - k(fr, at, 12)))
        anim(s, c, at, "fade", stagger=0.04, duration=0.15, order="random")
    c = s.say("How to be a motion designer", (600, 586, 1188, 622), M, 500, "#333333", "Texto", align="left")
    s.typed(c, 21, stagger=0.03, duration=0.03)
    return t


def t_bold():
    D = dur_for(1.9, 1.0)
    t = _s("bold-titles", "Título con raya roja y marco que se dibuja", "Title with a red line and a frame drawing "
           "itself", 12198, D, ["marco"])
    s = S(t, D)
    s.rect("Raya", solid("#E3061F"), lambda fr, u: (960 - 252 * k(fr, 0, 15), 714, 960 + 252 * k(fr, 0, 15), 730))
    for i, (text, ink, at) in enumerate((("TITLES", (708, 552, 1218, 678), 18), ("BOLD", (708, 408, 1188, 522), 27))):
        c = s.say(text, ink, M, 800, WHITE, "Título 2" if i == 0 else "Título", align="left")
        anim(s, c, at, "blur-in", stagger=0.06, duration=0.25, order="backward", blur=12)
    c = s.say("THE BEST", (708, 346, 830, 362), M, 700, WHITE, "Texto", align="left")
    s.typed(c, 36, stagger=0.04, duration=0.04)
    s.outline("Marco", [(1302, 258), (1302, 828), (618, 828), (618, 258), (1302, 258)], 4, WHITE, at=39, n=18,
              closed=False)
    return t


def t_studio():
    D = dur_for(1.0, 1.2)
    t = _s("motion-studio", "Título sobre dos barras rojas cruzadas", "Title on two crossing red bars", 12199, D,
           ["barras"])
    s = S(t, D)
    s.rect("Barra", grad_("#E3061F", "#8E0016", 0), lambda fr, u: (-10, 432, -10 + 1822 * k(fr, 9, 12), 540))
    s.rect("Barra 2", solid("#E3061F"), lambda fr, u: (1930 - 1822 * k(fr, 12, 12), 540, 1930, 636))
    c = s.say("MOTION STUDIO", (462, 402, 1458, 510), M, 800, WHITE)
    anim(s, c, 0, "fade", stagger=0.06, duration=0.1)
    c = s.say("www.yourwebsite.com", (618, 582, 1302, 618), M, 500, WHITE, "Texto")
    s.typed(c, 3, stagger=0.03, duration=0.03)
    return t


def t_watch_split():
    D = dur_for(1.6, 1.0)
    t = _s("ver-siguiente-dos-colores", "Título: mira el siguiente, en caja blanca y roja", "Title: watch next, in a "
           "white and red box", 12200, D, ["caja"])
    s = S(t, D)
    half = lambda fr: 456 * k(fr, 0, 15)  # noqa: E731
    s.rect("Caja", solid(WHITE), lambda fr, u: (960 - half(fr) * 480 / 456, 462, 960, 618), op=lambda fr, u: k(fr, 0, 1))
    s.rect("Caja 2", solid("#E3061F"), lambda fr, u: (960, 462, 960 + half(fr) * 432 / 456, 618),
           op=lambda fr, u: k(fr, 0, 1))
    for i, (text, ink, col) in enumerate((("WATCH", (640, 518, 860, 562), "#E3061F"),
                                          ("NEXT!", (1012, 518, 1232, 562), WHITE))):
        c = s.say(text, ink, M, 500, col, "Título" if i == 0 else "Título 2")
        spacing(s, c, lambda fr, u: 0.3)
        anim(s, c, 6, "fade", stagger=0.05, duration=0.12, order="random")

    def corner(fr, u, which):
        q = lin(fr, 24, 27)
        if which == 0:
            return 1392 - 140 * math.sin(math.pi * q), 432 + 60 * math.sin(math.pi * q)
        return 432 + 160 * math.sin(math.pi * q), 648 - 40 * math.sin(math.pi * q)
    for i, path in enumerate(("M 0 0 L 100 0 L 100 100", "M 0 0 L 0 100 L 100 100")):
        s.obj(f"Esquina {i + 1}", ring(WHITE, 4), lambda fr, u, i=i: (*corner(fr, u, i), 100, 70, 0,
                                                                      k(fr, 21, 3) * (1 - k(fr, 48, 6))), path=path)
    return t


def t_game():
    D = dur_for(1.6, 1.2)
    t = _s("mejor-juego", "Título en caja gris bajo un bloque rojo", "Title in a grey box under a red block", 12201, D,
           ["caja"])
    s = S(t, D)
    s.rect("Bloque", solid("#E3061F"), lambda fr, u: (960 - 540 * k(fr, 0, 9), 522 - 222 * k(fr, 12, 9) + 102 * k(fr, 42, 9),
                                                      960 + 540 * k(fr, 0, 9), 530 - 122 * k(fr, 12, 9) + 12 * k(fr, 42, 9)))
    s.rect("Caja", solid("#3A3A3A"), lambda fr, u: (420, 420, 1500, 420 + 132 * k(fr, 21, 6)),
           op=lambda fr, u: k(fr, 21, 2))
    c = s.say("BEST GAME", (540, 420, 1380, 540), M, 800, WHITE)
    s.typed(c, 15, stagger=0.06, duration=0.05)
    c = s.say("OF THE YEAR", (672, 570, 1428, 696), M, 800, WHITE, "Título 2", align="right")
    anim(s, c, 27, "fade", stagger=0.05, duration=0.08, order="backward")
    return t


TEMPLATES += [t_boxes, t_top10, t_popular, t_modern, t_rate, t_pro, t_design, t_watch_box, t_bold, t_studio,
              t_watch_split, t_game]


# --- Quotations (67.5–75 s, two 2×2 grids): famous authors' names replaced by ordinary ones ------------------------
def _q(id, es, en, order, dur, thumb=None):
    return _p(id, es, en, order, dur, "frases", ["cita", "frase"], thumb)


def quote_mark(s, name, cx, cy, w, colour, at, n=6, closing=False):
    s.obj(name, solid(colour), lambda fr, u: (cx, cy, w * k(fr, at, n), w * 0.7 * k(fr, at, n), 180 if closing else 0,
                                              1), path=QUOTE)


def lines_in(s, lines, x, y0, step, cap, colour, at, gap=3, align="left", weight=500, spread=0.0, name="Texto",
             width=None, preset="fade", stagger=0.02, order="forward"):
    """Several lines of a paragraph, each its own text, coming in one after another (gap frames apart)."""
    out = []
    for i, line in enumerate(lines):
        y = y0 + step * i
        f = f6._font(M, weight)
        bb, hb = f.getbbox(line), f.getbbox("H")
        w = cap * (bb[2] - bb[0]) / max(1, hb[3] - hb[1]) if width is None else width
        x0 = x if align == "left" else x - w / 2
        c = s.say(line, (x0, y, x0 + w, y + cap), M, weight, colour, f"{name} {i + 1}" if i else name, align=align)
        if spread:
            spacing(s, c, lambda fr, u, i=i: spread * (1 - k(fr, at + gap * i, 9)))
        anim(s, c, at + gap * i, preset, stagger=stagger, duration=0.12, order=order)
        out.append(c)
    return out


def q_tag():
    D = dur_for(1.5, 1.4)
    t = _q("cita-etiqueta", "Cita con etiqueta roja del autor", "Quote with a red author tag", 12210, D)
    s = S(t, D)
    quote_mark(s, "Comillas", 570, 348, 64, "#E3061F", 3)
    lines_in(s, ["The most difficult thing is the decision to act,", "the rest is merely tenacity. The fears are paper",
                 "tigers. You can do anything you decide to do.", "You can act to change and control your life",
                 "and the procedure, the process is its own reward."], 540, 432, 46, 24, WHITE, 12, gap=3, spread=0.3)
    s.rect("Etiqueta", solid("#E3061F"), lambda fr, u: (540, 696 + 12 * k(fr, 33, 3) * 0 - 0 * fr, 540 + 180 *
                                                        k(fr, 27, 6) + 180 * k(fr, 33, 6),
                                                        702 + 60 * k(fr, 33, 6)))
    c = s.say("MARIA LOPEZ", (556, 722, 860, 744), M, 700, "#4A0008", "Autor", align="left")
    s.typed(c, 39, stagger=0.05, duration=0.04)
    return t


def q_dream():
    D = dur_for(2.0, 1.2)
    t = _q("cita-centrada", "Cita centrada entre dos líneas", "Centred quote between two lines", 12211, D)
    s = S(t, D)
    for i, (line, y, at) in enumerate((("All that we see", 426, 0), ("or seem is but a dream", 516, 12),
                                       ("within a dream.", 606, 24))):
        f = f6._font(M, 400)
        bb, hb = f.getbbox(line), f.getbbox("H")
        w = 44 * (bb[2] - bb[0]) / (hb[3] - hb[1])
        c = s.say(line, (960 - w / 2, y, 960 + w / 2, y + 44), M, 400, WHITE, f"Texto {i + 1}" if i else "Texto")
        s.typed(c, at, stagger=0.05, duration=0.04)
    quote_mark(s, "Comillas", 960, 276, 120, "#E3061F", 24)
    s.rect("Línea", solid("#5A5A5A"), lambda fr, u: (570, 340, 570 + 780 * k(fr, 27, 12), 344))
    s.rect("Línea 2", solid("#5A5A5A"), lambda fr, u: (1350 - 780 * k(fr, 27, 12), 732, 1350, 736))
    c = s.say("JAMES CARTER", (870, 812, 1050, 830), M, 700, "#E3061F", "Autor")
    spacing(s, c, lambda fr, u: 0.3)
    s.typed(c, 45, stagger=0.05, duration=0.04)
    return t


def q_badge():
    D = dur_for(1.8, 1.2)
    t = _q("cita-marco-fino", "Cita en marco rojo fino con insignia", "Quote in a thin red frame with a badge", 12212, D)
    s = S(t, D)
    s.obj("Insignia", solid("#E3061F"), lambda fr, u: (960, 468 - 108 * k(fr, 9, 6), 30 + 54 * k(fr, 0, 21),
                                                       30 + 54 * k(fr, 0, 21), 0, k(fr, 0, 2)), kind="ellipse")
    quote_mark(s, "Comillas", 960, 360, 40, "#3A0006", 24)
    s.outline("Marco", [(510, 0), (510, 816), (1416, 816), (1416, 100)], 4, "#E3061F", at=21, n=24, closed=False)
    lines_in(s, ["Permanence, perseverance and persistence", "in spite of all obstacles, discouragements,",
                 "and impossibilities: it is this, that in all things", "distinguishes the strong soul from the weak."],
             960, 456, 44, 22, WHITE, 24, gap=4, align="center")
    s.rect("Etiqueta", solid("#E3061F"), lambda fr, u: (957 - 165 * k(fr, 48, 9), 708 - 36 * k(fr, 45, 6),
                                                        963 + 159 * k(fr, 48, 9), 708 + 36 * k(fr, 45, 6)))
    c = s.say("DAVID MILLER", (850, 698, 1070, 718), M, 700, "#4A0008", "Autor")
    s.typed(c, 57, stagger=0.05, duration=0.04)
    return t


def q_panel():
    D = dur_for(1.6, 1.2)
    t = _q("cita-panel-rojo", "Cita en caja oscura junto a un panel rojo", "Quote in a dark box beside a red panel",
           12213, D)
    s = S(t, D)
    s.rect("Panel", solid("#E3061F"), lambda fr, u: (1920 - 540 * k(fr, 0, 12), -10, 1930, 1090))
    s.rect("Caja", solid("#1C1C1C"), lambda fr, u: (1740 - 720 * k(fr, 9, 9), 660 - 150 * k(fr, 18, 9) - 162 *
                                                    k(fr, 27, 9), 1740, 672 + 138 * k(fr, 18, 9) + 150 * k(fr, 27, 9)))
    quote_mark(s, "Comillas", 1728, 150, 180, WHITE, 21)
    lines_in(s, ["If you cannot do", "great things,", "do small things", "in a great way."], 1098, 448, 64, 40, WHITE,
             27, gap=3, weight=600, spread=0.5)
    c = s.say("- JOHN SMITH", (1098, 862, 1300, 878), M, 600, "#E3061F", "Autor", align="left")
    s.typed(c, 45, stagger=0.05, duration=0.04)
    return t


def q_frame():
    D = dur_for(2.0, 1.2)
    t = _q("cita-marco-rojo", "Cita tecleada con marco rojo", "Typed quote with a red frame", 12214, D)
    s = S(t, D)
    for i, (line, at) in enumerate((("Let us be grateful to people who", 0), ("make us happy, they are the", 12),
                                    ("charming gardeners who make", 21), ("our souls blossom.", 30))):
        f = f6._font(M, 700)
        bb, hb = f.getbbox(line), f.getbbox("H")
        w = 30 * (bb[2] - bb[0]) / (hb[3] - hb[1])
        y = 392 + 60 * i
        c = s.say(line, (960 - w / 2, y, 960 + w / 2, y + 30), M, 700, WHITE, f"Texto {i + 1}" if i else "Texto")
        s.typed(c, at, stagger=0.03, duration=0.03)
    quote_mark(s, "Comillas", 570, 228, 80, WHITE, 15)
    quote_mark(s, "Comillas 2", 1350, 840, 80, WHITE, 15, closing=True)
    s.outline("Marco", [(1452, 228), (1452, 840), (468, 840), (468, 228), (1460, 228)], 6, "#E3061F", at=24, n=24,
              closed=False)
    c = s.say("Anna Brown", (850, 672, 1070, 708), M, 500, "#E3061F", "Autor")
    s.typed(c, 48, stagger=0.05, duration=0.04)
    return t


def q_circle():
    D = dur_for(2.0, 1.2)
    t = _q("cita-circulo", "Cita en círculo rojo", "Quote in a red circle", 12215, D)
    s = S(t, D)
    s.obj("Aro", solid("#1E1E1E"), lambda fr, u: (960, 540, 560 * k(fr, 0, 6) - 0 * k(fr, 9, 3), 560 * k(fr, 0, 6),
                                                  0, 1 - k(fr, 12, 4)), kind="ellipse")
    s.obj("Círculo", solid("#E3061F"), lambda fr, u: (960, 540, 80 + 520 * k(fr, 4, 9), 80 + 520 * k(fr, 4, 9), 0,
                                                      k(fr, 3, 2)), kind="ellipse")
    quote_mark(s, "Comillas", 960, 362, 96, "#3A0006", 15)
    for i, (line, at) in enumerate((("Whoever is happy", 21), ("will make others", 33), ("happy too.", 42))):
        f = f6._font(M, 700)
        bb, hb = f.getbbox(line), f.getbbox("H")
        w = 32 * (bb[2] - bb[0]) / (hb[3] - hb[1])
        y = 460 + 60 * i
        c = s.say(line, (960 - w / 2, y, 960 + w / 2, y + 32), M, 700, WHITE, f"Texto {i + 1}" if i else "Texto")
        s.typed(c, at, stagger=0.05, duration=0.03)
    s.rect("Banda", solid("#1E1E1E"), lambda fr, u: (960 - 270 * k(fr, 48, 9), 672, 960 + 270 * k(fr, 48, 9), 732))
    c = s.say("Laura Diaz", (880, 688, 1040, 716), M, 500, WHITE, "Autor")
    s.typed(c, 54, stagger=0.05, duration=0.04)
    return t


def q_square():
    D = dur_for(1.8, 1.2)
    t = _q("cita-cuadro-rojo", "Cita en cuadro rojo con pestaña", "Quote in a red square with a side tab", 12216, D)
    s = S(t, D)
    s.rect("Pestaña", solid("#1E1E1E"), lambda fr, u: (720 - 72 * k(fr, 33, 9), 300, 724, 780))
    c = s.say("PETER LEWIS", (590, 528, 778, 546), M, 600, "#555555", "Autor",
              geom=lambda fr, u: (-30 * (1 - k(fr, 36, 9)) - 0, 0, 1, 0, k(fr, 36, 6)))
    c["rotation"] = keys([(0.0, -90.0, "hold")])
    s.rect("Cuadro", solid("#E3061F"), lambda fr, u: (720, 540 - 6 - 252 * k(fr, 6, 9), 1272,
                                                      540 + 6 + 252 * k(fr, 6, 9)),
           op=lambda fr, u: k(fr, 0, 2))
    for i, (line, at) in enumerate((("Think in the morning.", 24), ("Act in the noon.", 21), ("Eat in the evening.", 18),
                                    ("Sleep in the night.", 15))):
        f = f6._font(M, 500)
        bb, hb = f.getbbox(line), f.getbbox("H")
        w = 28 * (bb[2] - bb[0]) / (hb[3] - hb[1])
        y = 432 + 60 * i
        c = s.say(line, (756, y, 756 + w, y + 28), M, 500, WHITE, f"Texto {i + 1}" if i else "Texto", align="left")
        anim(s, c, at, "fade", stagger=0.02, duration=0.15)
    quote_mark(s, "Comillas", 800, 348, 56, "#4A0006", 21)
    quote_mark(s, "Comillas 2", 1200, 740, 56, "#4A0006", 21, closing=True)
    return t


def q_boxes():
    D = dur_for(2.0, 1.2)
    t = _q("cita-cajas-grises", "Cita en cajas grises con comillas rojas", "Quote in grey boxes with red quote marks",
           12217, D)
    s = S(t, D)
    s.obj("Comillas", solid("#E3061F"), lambda fr, u: (960, 480 - 150 * k(fr, 3, 9), 20 + 124 * k(fr, 0, 6),
                                                       14 + 86 * k(fr, 0, 6), 0, 1), path=QUOTE)
    s.rect("Caja", solid("#1E1E1E"), lambda fr, u: (960 - 30 - 402 * k(fr, 9, 9) - 150 * k(fr, 27, 9),
                                                    540 - 108 * k(fr, 6, 6), 960 + 30 + 402 * k(fr, 9, 9) +
                                                    150 * k(fr, 27, 9), 540 + 108 * k(fr, 6, 6)))
    s.rect("Caja 2", solid("#1E1E1E"), lambda fr, u: (960 - 30 - 522 * k(fr, 15, 9), 708, 960 + 30 + 522 *
                                                      k(fr, 15, 9), 708 + 84 * k(fr, 12, 6)))
    lines_in(s, ["Make every day a little better", "than the one before."], 960, 488, 58, 32, WHITE, 24, gap=6,
             align="center", preset="fade", stagger=0.02)
    c = s.say("EMMA WILSON", (880, 740, 1040, 758), M, 700, "#E3061F", "Autor")
    spacing(s, c, lambda fr, u: 0.3)
    s.typed(c, 39, stagger=0.05, duration=0.04)
    return t


TEMPLATES += [q_tag, q_dream, q_badge, q_panel, q_frame, q_circle, q_square, q_boxes]


# --- Call-out titles and info graphics (74.5–80.7 s): a dot, a leader line, a label; counters use the engine's -----
LOREM4 = ["Lorem ipsum dolor sit amet, consectetur", "adipiscing elit. Praesent cursus tempus tellus.",
          "Duis urna urna, consequat eu."]


def _c(id, es, en, order, dur, tags=(), thumb=None):
    return _p(id, es, en, order, dur, "elementos", ["llamada", "señalador"] + list(tags), thumb)


def pin(s, x, y, at, colour=WHITE, centre=RED):
    """The leader's dot: a white ring with a red centre that pops."""
    s.obj("Punto", solid(centre), lambda fr, u: (x, y, 22 * k(fr, at, 4), 22 * k(fr, at, 4), 0, 1), kind="ellipse")
    s.obj("Punto (aro)", ring(colour, 7), lambda fr, u: (x, y, 40 * k(fr, at, 4), 40 * k(fr, at, 4), 0, 1),
          kind="ellipse", base=(40, 40))


def leader(s, pts, at, n=12, colour=WHITE, width=4):
    return s.outline("Línea", pts, width, colour, at=at, n=n, closed=False)


def counter(clip, start, seconds):
    """The engine's counter: the number counts from `start` to the clip's text over `seconds` from the clip start."""
    clip["textStyle"].update(counter=True, counterFrom=start, counterSeconds=round(seconds, 3))


def co_screen():
    D = dur_for(1.6, 1.2)
    t = _c("llamada-pantalla", "Llamada: etiqueta roja y recuadro", "Call-out: red label and outlined box", 12230, D,
           ["etiqueta"])
    s = S(t, D)
    pin(s, 720, 768, 0)
    leader(s, [(720, 768), (882, 450), (882, 162)], 15, 12)
    s.rect("Etiqueta", solid("#E3061F"), lambda fr, u: (900, 168, 900 + 468 * k(fr, 24, 6), 306))
    c = s.say("SCREEN", (930, 204, 1320, 270), ROBOTO, 400, WHITE, "Título", align="left")
    anim(s, c, 27, "fade", stagger=0.05, duration=0.1, order="random")
    c = s.say("IPS, 4K resolution", (930, 386, 1490, 424), ROBOTO, 400, WHITE, "Texto", align="left")
    anim(s, c, 30, "fade", stagger=0.03, duration=0.1, order="random")
    s.outline("Recuadro", [(1512, 348), (900, 348), (900, 462), (1512, 462)], 4, "#E3061F", at=36, n=12, closed=True)
    return t


def co_spec():
    D = dur_for(1.6, 1.0)
    t = _c("llamada-especificacion", "Llamada: título rojo sobre una línea", "Call-out: red title over a line", 12231,
           D, ["especificación"])
    s = S(t, D)
    pin(s, 1308, 708, 0)
    leader(s, [(1308, 708), (1170, 408), (480, 408)], 15, 15)
    c = s.say("PROCESSOR", (540, 288, 1140, 366), ROBOTO, 700, "#E3061F", "Título")
    anim(s, c, 24, "fade", stagger=0.05, duration=0.15, order="random")
    for i, line in enumerate(("Octa-core 2.8 GHz", "8 GB RAM, 128 GB")):
        c = s.say(line, (600, 450 + 90 * i, 1120, 492 + 90 * i), ROBOTO, 400, "#D0D0D0", f"Texto {i + 1}" if i else
                  "Texto")
        anim(s, c, 30 + 3 * i, "fade", stagger=0.03, duration=0.1, order="random")
    return t


def co_percent_bar():
    D = dur_for(2.8, 1.0)
    t = _c("info-porcentaje", "Infografía: porcentaje grande con etiqueta", "Info graphic: big percentage with a "
           "label", 12232, D, ["porcentaje", "contador"])
    s = S(t, D)
    pin(s, 1788, 654, 0)
    leader(s, [(1788, 654), (1572, 348), (1548, 348)], 12, 9)
    s.rect("Etiqueta", solid("#E3061F"), lambda fr, u: (1548 - 708 * k(fr, 24, 9), 288, 1548, 420),
           op=lambda fr, u: k(fr, 21, 2))
    s.rect("Barra", solid("#6A6A6A"), lambda fr, u: (1548 - 708 * k(fr, 27, 9), 450, 1548, 476))
    s.rect("Barra (relleno)", solid("#E3061F"), lambda fr, u: (1548 - 708 * k(fr, 27, 9) * 0.45 * (0.2 + 0.8 * lin(fr, 39, 45)),
                                                               450, 1548, 476))
    c = s.say("PROCESSOR", (900, 312, 1500, 396), ROBOTO, 700, WHITE, "Título")
    anim(s, c, 30, "fade", stagger=0.05, duration=0.12, order="random")
    c = s.say("70%", (228, 270, 780, 492), ROBOTO, 700, WHITE, "Número", align="right",
              geom=lambda fr, u: (0, 0, 1, 0, k(fr, 39, 3)))
    counter(c, 0, 2.8)
    for i, line in enumerate(LOREM4):
        c = s.say(line, (84, 520 + 80 * i, 1560, 568 + 80 * i), ROBOTO, 400, "#CFCFCF", f"Texto {i + 1}" if i else
                  "Texto", align="right")
        anim(s, c, 36 + 3 * i, "fade", stagger=0.02, duration=0.1, order="random")
    return t


def ring_progress(s, cx, cy, d, at, n, final, name="Progreso"):
    """A thin white ring and a dashed red arc that fills to `final` (0..1)."""
    c = s.obj(f"{name} (aro)", ring(WHITE, 5), lambda fr, u: (cx, cy, d, d, -90, 1), kind="ellipse")
    knob(s, c, "trimEnd", lambda fr, u: 100 * k(fr, at - 9, 15))
    r = s.obj(name, ring("#E3061F", 14), lambda fr, u: (cx, cy, d, d, -90, 1), kind="ellipse")
    r["shapeStyle"]["layers"][1].update(dash="dash", dashPattern=[18, 10], cap="butt")
    knob(s, r, "trimEnd", lambda fr, u: 100 * final * lin(fr, at, n))


def co_ring():
    D = dur_for(2.6, 1.0)
    t = _c("info-anillo", "Infografía: anillo de porcentaje con texto", "Info graphic: percentage ring with text",
           12233, D, ["porcentaje", "contador"])
    s = S(t, D)
    pin(s, 270, 798, 0)
    leader(s, [(270, 798), (420, 498), (520, 498)], 12, 9)
    ring_progress(s, 720, 495, 450, 30, 48, 0.67)
    c = s.say("67", (620, 360, 820, 480), ROBOTO, 700, WHITE, "Número", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 30, 3)))
    counter(c, 0, 2.6)
    s.say("%", (680, 530, 760, 610), ROBOTO, 700, WHITE, "Número (signo)", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 30, 3)))
    c = s.say("PROCESSOR", (1020, 270, 1520, 350), ROBOTO, 700, "#E3061F", "Título", align="left")
    anim(s, c, 36, "fade", stagger=0.05, duration=0.12, order="random")
    for i, line in enumerate(("Lorem ipsum dolor sit", "amet, consectetur", "adipiscing elit. Praesent",
                              "cursus tempus tellus.")):
        c = s.say(line, (1020, 400 + 90 * i, 1760, 446 + 90 * i), ROBOTO, 400, "#CFCFCF", f"Texto {i + 1}" if i else
                  "Texto", align="left")
        anim(s, c, 42 + 3 * i, "fade", stagger=0.02, duration=0.1, order="random")
    return t


def co_red_bar():
    D = dur_for(1.5, 1.2)
    t = _c("llamada-barra-roja", "Llamada: barra roja con párrafo", "Call-out: red bar with a paragraph", 12234, D,
           ["párrafo"])
    s = S(t, D)
    pin(s, 240, 678, 0)
    leader(s, [(240, 678), (468, 378), (480, 378)], 12, 9)
    s.rect("Barra", solid("#E3061F"), lambda fr, u: (468, 300, 480 + 1200 * k(fr, 24, 6), 462),
           op=lambda fr, u: k(fr, 18, 2))
    c = s.say("PROCESSOR", (768, 336, 1380, 426), ROBOTO, 700, WHITE, "Título")
    anim(s, c, 27, "fade", stagger=0.05, duration=0.12, order="random")
    for i, line in enumerate(("Lorem ipsum dolor sit amet,", "consectetur adipiscing elit. Praesent",
                              "cursus tempus tellus.", "Duis urna urna, consequat eu.")):
        c = s.say(line, (480, 508 + 90 * i, 1700, 556 + 90 * i), ROBOTO, 400, "#DDDDDD", f"Texto {i + 1}" if i else
                  "Texto", align="left")
        anim(s, c, 24 + 2 * i, "fade", stagger=0.02, duration=0.1, order="random")
    return t


def co_gpu():
    D = dur_for(2.4, 1.0)
    t = _c("info-barra-porcentaje", "Infografía: porcentaje en caja gris y etiqueta roja", "Info graphic: percentage "
           "in a grey box and a red label", 12235, D, ["porcentaje", "contador"])
    s = S(t, D)
    pin(s, 1680, 660, 0)
    leader(s, [(1680, 660), (1476, 360), (1458, 360)], 12, 9)
    s.rect("Etiqueta", solid("#E3061F"), lambda fr, u: (1458 - 726 * k(fr, 21, 6), 288, 1458, 420))
    s.rect("Caja", solid("#7A7A7A"), lambda fr, u: (360, 288, 702, 420), op=lambda fr, u: k(fr, 27, 3))
    s.rect("Caja (relleno)", solid(WHITE), lambda fr, u: (360, 288, 360 + 342 * 0.53 * lin(fr, 30, 42), 420),
           op=lambda fr, u: k(fr, 27, 3))
    c = s.say("GPU", (990, 318, 1200, 390), ROBOTO, 700, WHITE, "Título")
    anim(s, c, 27, "fade", stagger=0.05, duration=0.12, order="random")
    c = s.say("53%", (430, 320, 632, 388), ROBOTO, 700, "#E3061F", "Número", geom=lambda fr, u: (0, 0, 1, 0,
                                                                                                k(fr, 30, 3)))
    counter(c, 0, 2.4)
    for i, line in enumerate(("Lorem ipsum dolor sit amet,", "consecteturadipiscing elit. Praesent",
                              "cursus tempus tellus.", "Duis urna urna, consequat eu.")):
        f = f6._font(ROBOTO, 400)
        bb, hb = f.getbbox(line), f.getbbox("H")
        w = 46 * (bb[2] - bb[0]) / (hb[3] - hb[1])
        c = s.say(line, (888 - w / 2, 498 + 90 * i, 888 + w / 2, 544 + 90 * i), ROBOTO, 400, "#DDDDDD",
                  f"Texto {i + 1}" if i else "Texto")
        anim(s, c, 33 + 2 * i, "fade", stagger=0.02, duration=0.1, order="random")
    return t


def co_headline():
    D = dur_for(1.5, 1.2)
    t = _c("llamada-titular", "Llamada: titular en recuadro rojo", "Call-out: headline in a red outline", 12236, D,
           ["titular"])
    s = S(t, D)
    pin(s, 1488, 660, 0, centre=RED)
    leader(s, [(1488, 660), (1368, 420), (1300, 300)], 12, 9, colour="#E3061F")
    for i, off in enumerate((24, 12)):
        s.outline(f"Recuadro (eco {i + 1})", [(1272 - 80 + off, 276 - off), (1272 + off, 276 - off),
                                               (1272 + off, 360 - off)], 4, "#E3061F", at=18, n=9, closed=False)
    s.outline("Recuadro", [(1272, 276), (432, 276), (432, 438), (1272, 438), (1272, 270)], 5, "#E3061F", at=18, n=12,
              closed=False)
    c = s.say("HEADLINE", (612, 318, 1098, 402), ROBOTO, 700, WHITE, "Título")
    anim(s, c, 27, "fade", stagger=0.05, duration=0.12, order="random")
    for i, line in enumerate(("Lorem ipsum dolor sit", "amet, consectetur adipiscing", "elit. Praesent cursus tempus",
                              "tellus. Duis urna urna")):
        f = f6._font(ROBOTO, 400)
        bb, hb = f.getbbox(line), f.getbbox("H")
        w = 46 * (bb[2] - bb[0]) / (hb[3] - hb[1])
        c = s.say(line, (852 - w / 2, 486 + 90 * i, 852 + w / 2, 532 + 90 * i), ROBOTO, 400, "#DDDDDD",
                  f"Texto {i + 1}" if i else "Texto")
        anim(s, c, 24 + 2 * i, "fade", stagger=0.02, duration=0.1, order="random")
    return t


def co_ring_line():
    D = dur_for(2.6, 1.0)
    t = _c("info-anillo-linea", "Infografía: título sobre la línea y anillo de porcentaje", "Info graphic: title on "
           "the line and a percentage ring", 12237, D, ["porcentaje", "contador"])
    s = S(t, D)
    pin(s, 264, 756, 0)
    leader(s, [(264, 756), (408, 456), (1290, 456)], 12, 15)
    ring_progress(s, 1515, 465, 450, 36, 45, 0.56)
    c = s.say("56", (1415, 330, 1615, 450), ROBOTO, 700, WHITE, "Número", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 36, 3)))
    counter(c, 0, 2.6)
    s.say("%", (1475, 500, 1555, 580), ROBOTO, 700, WHITE, "Número (signo)",
          geom=lambda fr, u: (0, 0, 1, 0, k(fr, 36, 3)))
    c = s.say("PROCESSOR", (552, 348, 1152, 432), ROBOTO, 700, "#E3061F", "Título")
    anim(s, c, 33, "fade", stagger=0.05, duration=0.12, order="random")
    c = s.say("Lorem ipsum dolor sit", (540, 486, 1200, 540), ROBOTO, 400, "#CFCFCF", "Texto")
    anim(s, c, 39, "fade", stagger=0.02, duration=0.1, order="random")
    return t


def co_number_circle():
    D = dur_for(1.2, 1.4)
    t = _c("llamada-numero", "Llamada: número en círculo con dos textos", "Call-out: number in a circle with two texts",
           12238, D, ["número"])
    s = S(t, D)
    pin(s, 210, 630, 0)
    leader(s, [(210, 630), (420, 330)], 6, 9)
    s.obj("Círculo", fs("#8A0010", WHITE, 6), lambda fr, u: (612, 330, 300 * k(fr, 9, 6), 300 * k(fr, 9, 6), 0, 1),
          kind="ellipse")
    c = s.say("1", (570, 270, 654, 390), ROBOTO, 700, WHITE, "Número", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 12, 3)))
    s.rect("Línea 2", solid(WHITE), lambda fr, u: (762, 340, 762 + 920 * k(fr, 12, 9), 345))
    c = s.say("PRIMARY TEXT", (792, 210, 1680, 312), ROBOTO, 700, "#E3061F", "Título", align="left")
    anim(s, c, 15, "fade", stagger=0.05, duration=0.15, order="random")
    c = s.say("SECONDARY TEXT", (810, 372, 1680, 462), ROBOTO, 700, WHITE, "Título 2", align="left")
    anim(s, c, 18, "fade", stagger=0.05, duration=0.15, order="random")
    for i, line in enumerate(("Lorem ipsum dolor sit amet, consectetur", "adipiscing elit. Praesent cursus tempus",
                              "Lorem ipsum dolor sit amet, consectetur", "adipiscing elit. Praesent cursus tempus")):
        f = f6._font(ROBOTO, 400)
        bb, hb = f.getbbox(line), f.getbbox("H")
        w = 40 * (bb[2] - bb[0]) / (hb[3] - hb[1])
        c = s.say(line, (990 - w / 2, 508 + 90 * i, 990 + w / 2, 548 + 90 * i), ROBOTO, 400, "#BBBBBB",
                  f"Texto {i + 1}" if i else "Texto")
        anim(s, c, 21 + 2 * i, "fade", stagger=0.02, duration=0.1, order="random")
    return t


def co_number_square():
    D = dur_for(1.2, 1.4)
    t = _c("llamada-numero-cuadro", "Llamada: número en cuadro rojo y cajas blancas", "Call-out: number in a red "
           "square and white boxes", 12239, D, ["número"])
    s = S(t, D)
    pin(s, 150, 660, 0)
    leader(s, [(150, 660), (300, 360), (378, 360)], 6, 9)
    s.rect("Cuadro", solid("#E3061F"), lambda fr, u: (378, 192, 378 + 330 * k(fr, 9, 6), 528))
    s.say("2", (488, 268, 598, 452), ROBOTO, 700, WHITE, "Número", geom=lambda fr, u: (0, 0, 1, 0, k(fr, 12, 3)))
    for i, (y0, y1) in enumerate(((192, 342), (372, 522))):
        s.rect(f"Caja {i + 1}", solid(WHITE), lambda fr, u, y0=y0, y1=y1, i=i: (738, y0, 738 + 960 * k(fr, 12 + 3 * i, 9),
                                                                              y1))
    c = s.say("PRIMARY TEXT", (768, 230, 1500, 304), ROBOTO, 700, "#E3061F", "Título", align="left")
    anim(s, c, 18, "fade", stagger=0.05, duration=0.15, order="random")
    c = s.say("SECONDARY TEXT", (768, 410, 1580, 484), ROBOTO, 700, "#E3061F", "Título 2", align="left")
    anim(s, c, 21, "fade", stagger=0.05, duration=0.15, order="random")
    for i, line in enumerate(("Lorem ipsum dolor sit amet, consectetur", "adipiscing elit. Praesent cursus tempus",
                              "tellus. Duis urna urna, consequat eu.", "Lorem ipsum dolor sit amet, consectetur")):
        f = f6._font(ROBOTO, 400)
        bb, hb = f.getbbox(line), f.getbbox("H")
        w = 40 * (bb[2] - bb[0]) / (hb[3] - hb[1])
        c = s.say(line, (1050 - w / 2, 568 + 90 * i, 1050 + w / 2, 608 + 90 * i), ROBOTO, 400, "#BBBBBB",
                  f"Texto {i + 1}" if i else "Texto")
        anim(s, c, 21 + 2 * i, "fade", stagger=0.02, duration=0.1, order="random")
    return t


def co_headline_box():
    D = dur_for(1.2, 1.4)
    t = _c("llamada-dato", "Llamada: titular, texto y dato en caja roja", "Call-out: headline, text and a figure in a "
           "red box", 12240, D, ["dato"])
    s = S(t, D)
    pin(s, 540, 900, 0)
    leader(s, [(540, 900), (720, 600), (1122, 600)], 6, 12)
    c = s.say("MAIN HEADLINE", (702, 138, 1482, 228), ROBOTO, 700, "#E3061F", "Título", align="left")
    spacing(s, c, lambda fr, u: 0.08)
    anim(s, c, 12, "fade", stagger=0.04, duration=0.15, order="random")
    s.rect("Subrayado", solid("#E3061F"), lambda fr, u: (1482 - 780 * k(fr, 15, 9), 248, 1482, 254))
    c = s.say("ADDITIONAL TEXT", (702, 288, 1482, 378), ROBOTO, 400, WHITE, "Título 2", align="left")
    anim(s, c, 15, "fade", stagger=0.04, duration=0.15, order="random")
    s.rect("Caja", solid("#E3061F"), lambda fr, u: (696, 408, 696 + 366 * k(fr, 18, 6), 558))
    c = s.say("25 sqm", (726, 444, 1032, 522), ROBOTO, 400, WHITE, "Dato", align="left")
    anim(s, c, 21, "fade", stagger=0.05, duration=0.12)
    return t


TEMPLATES += [co_screen, co_spec, co_percent_bar, co_ring, co_red_bar, co_gpu, co_headline, co_ring_line,
              co_number_circle, co_number_square, co_headline_box]


# --- Social media links (80.7–84 s): each starts as the YouTube one the reference opens with --------------------
def _r(id, es, en, order, dur, thumb=None):
    return _p(id, es, en, order, dur, "redes", ["redes sociales", "enlace"], thumb)


def play_disc(s, name, geom, disc=YTRED, tri=WHITE):
    """A round play button: geom(fr, u) = (cx, cy, d, rot, op)."""
    s.obj(name, solid(disc), lambda fr, u: (lambda g: (g[0], g[1], g[2], g[2], 0, g[4]))(geom(fr, u)), kind="ellipse")
    s.obj(f"{name} (play)", solid(tri), lambda fr, u: (lambda g: (g[0] + g[2] * 0.04, g[1], g[2] * 0.36, g[2] * 0.4,
                                                                  g[3], g[4]))(geom(fr, u)), path=TRIANGLE)


def social_pill():
    D = dur_for(1.9, 1.2)
    t = _r("red-circulo-barra", "Redes: icono redondo que gira y barra con la web", "Social: spinning round icon and a "
           "bar with the website", 12260, D, thumb=3.0)
    s = S(t, D)
    x = lambda fr: 1428 - 858 * k(fr, 30, 12)  # noqa: E731
    s.rect("Barra", [shadow("#000000", 0, 6, 12, 0.3), fill(WHITE)], lambda fr, u: (x(fr), 402, x(fr) + 1080 * k(fr, 36, 12),
                                                                                 618), radius=108, base=(1080, 216))
    s.rect("Pestaña", solid(YTRED), lambda fr, u: (690, 600, 690 + 420 * k(fr, 45, 6), 672), radius=36, base=(420, 72))
    c = s.say("your description", (740, 624, 1010, 648), M, 500, WHITE, "Texto", align="left")
    anim(s, c, 48, "fade", stagger=0.02, duration=0.1)
    s.say("website.com/YourName", (798, 468, 1470, 540), M, 700, YTRED, "Título", align="left",
          reveal=lambda fr: (690, 0, x(fr) + 1080 * k(fr, 36, 12), 1080), op=lambda fr, u: k(fr, 40, 3))
    for i, r in enumerate((420, 500)):
        c = s.obj(f"Trazo {i + 1}", ring(WHITE, 5), lambda fr, u, r=r, i=i: (x(fr), 528, r, r, 200 * lin(fr, 6, 36) +
                                                                            180 * i, k(fr, 6, 3) * (1 - k(fr, 36, 6))),
                  path=arc(-30, 60))
    play_disc(s, "Icono", lambda fr, u: (x(fr), 528, 348 * k(fr, 0, 6), 0, 1))
    return t


def social_square():
    D = dur_for(1.8, 1.2)
    t = _r("red-cuadro-follow", "Redes: cuadro que rueda y FOLLOW US", "Social: tumbling square and FOLLOW US", 12261,
           D, thumb=3.0)
    s = S(t, D)
    q = lambda fr: k(fr, 0, 36)  # noqa: E731
    burst(s, "Chispa", 1300, 540, 9, 60, 240, n=8, colour=YTRED)
    s.rect("Barra", solid(YTRED), lambda fr, u: (528, 588, 528 + 1014 * k(fr, 39, 9), 708))
    c = s.say("youtube.com/yourchannelname", (560, 632, 1060, 662), M, 500, WHITE, "Texto", align="left")
    anim(s, c, 45, "fade", stagger=0.02, duration=0.1)
    s.say("FOLLOW US", (570, 420, 1560, 558), M, 800, WHITE, "Título", align="left",
          reveal=lambda fr: (520, 0, 520 + 1100 * k(fr, 36, 12), 1080))
    geo = lambda fr, u: (1440 + (360 - 1440) * q(fr), 540 + 12 * q(fr), 300 * k(fr, 0, 9), 220 * (1 - q(fr)),  # noqa
                         1.0)
    s.obj("Icono", solid(YTRED), lambda fr, u: (lambda g: (g[0], g[1], g[2], g[2], g[3], 1))(geo(fr, u)))
    s.obj("Icono (play)", solid(WHITE), lambda fr, u: (lambda g: (g[0] + 6, g[1], g[2] * 0.36, g[2] * 0.4, g[3], 1))(
        geo(fr, u)), path=TRIANGLE)
    return t


def social_diamond():
    D = dur_for(1.8, 1.2)
    t = _r("red-rombo", "Redes: rombo que se dibuja y nombre del canal", "Social: diamond drawing itself and the channel "
           "name", 12262, D, thumb=3.0)
    s = S(t, D)
    x = lambda fr: 1368 - 840 * k(fr, 33, 12)  # noqa: E731
    para = poly([(6, 0), (100, 0), (94, 100), (0, 100)])
    s.rect("Barra", solid(WHITE), lambda fr, u: (x(fr) + 60, 450, x(fr) + 60 + 918 * k(fr, 39, 12), 612), path=para)
    s.rect("Pestaña", solid("#9A0012"), lambda fr, u: (630, 588, 630 + 420 * k(fr, 45, 6), 648), path=para)
    c = s.say("description", (680, 604, 860, 632), M, 500, WHITE, "Texto", align="left")
    anim(s, c, 48, "fade", stagger=0.02, duration=0.1)
    s.say("Channel Name", (732, 468, 1428, 552), M, 700, "#9A0012", "Título", align="left",
          reveal=lambda fr: (x(fr) + 100, 0, x(fr) + 60 + 918 * k(fr, 39, 12), 1080), op=lambda fr, u: k(fr, 42, 3))
    c = s.obj("Rombo (trazo)", ring(WHITE, 6), lambda fr, u: (x(fr), 534, 230, 230, 45, 1 - k(fr, 15, 3)))
    knob(s, c, "trimEnd", lambda fr, u: 100 * k(fr, 0, 12))
    s.obj("Rombo", fs("#7A0010", WHITE, 6), lambda fr, u: (x(fr), 534, 230 * k(fr, 12, 6), 230 * k(fr, 12, 6), 45,
                                                          k(fr, 12, 2)))
    s.obj("Rombo (play)", solid(WHITE), lambda fr, u: (x(fr) + 8, 534, 96 * k(fr, 15, 6), 110 * k(fr, 15, 6), 0, 1),
          path=TRIANGLE)
    return t


def social_centre():
    D = dur_for(1.6, 1.2)
    t = _r("red-pastilla", "Redes: icono al centro de una pastilla", "Social: icon in the middle of a pill", 12263, D,
           thumb=2.6)
    s = S(t, D)
    burst(s, "Chispa", 960, 528, 6, 120, 420, n=14, colour=YTRED)
    s.rect("Pastilla", solid(YTRED), lambda fr, u: (960 - 663 * k(fr, 18, 9), 420, 960 + 663 * k(fr, 18, 9), 636),
           radius=108, base=(1326, 216))
    s.rect("Pastilla (blanca)", solid(WHITE), lambda fr, u: (960 - 633 * k(fr, 27, 9), 438, 960 + 633 * k(fr, 27, 9),
                                                             618), radius=90, base=(1266, 180))
    c = s.say("Follow us", (468, 500, 768, 556), M, 700, YTRED, "Texto", align="left")
    anim(s, c, 33, "fade", stagger=0.04, duration=0.1)
    c = s.say("@UserName", (1152, 500, 1548, 556), M, 700, YTRED, "Título", align="left")
    anim(s, c, 36, "fade", stagger=0.04, duration=0.1)
    s.obj("Icono (aro)", solid(WHITE), lambda fr, u: (960, 528, 330 * k(fr, 0, 9), 330 * k(fr, 0, 9), 0, 1),
          kind="ellipse")
    play_disc(s, "Icono", lambda fr, u: (960, 528, 290 * k(fr, 3, 9), 0, 1))
    return t


TEMPLATES += [social_pill, social_square, social_diamond, social_centre]


# --- Transitions (84–92 s): red, white and black layers that cover the cut; clip 1 before, clip 2 after ------------
TR_RED, TR_WHITE, TR_BLACK = "#E3061F", "#FFFFFF", "#1C1C1C"


def _tr(id, es, en, order, dur, tags=()):
    t = _p(id, es, en, order, dur, "transiciones", ["transición"] + list(tags), thumb=round(dur * 0.45, 1))
    return t, O(t, dur)


def two_clips(s, cut, a="h-portrait-02", b="h-city-03"):
    """Clip 1 until frame `cut`, clip 2 after it (two video slots)."""
    t = s.t
    for i, (sample, on) in enumerate(((a, lambda fr: 1.0 if fr < cut else 0.0), (b, lambda fr: 1.0 if fr >= cut
                                                                                  else 0.0))):
        clip = t.photo(t.track("video", f"Video {i + 1}"), sample, 0.0, s.dur, None, None, label=f"Video {i + 1}")
        clip["opacity"] = keys([(u, on(fr), "hold") for u, fr in s.each()])


def band_path(kind, W, d, H):
    """A band W long (travel axis = x, moving to -x) and H across, with a leading/trailing edge of kind."""
    L = W + d
    X = lambda x: x / L * 100  # noqa: E731
    if kind == "chevron":
        pts = [(0, 50), (X(d), 0), (X(W + d), 0), (X(W), 50), (X(W + d), 100), (X(d), 100)]
    else:
        pts = [(0, 0), (X(W), 0), (X(W), 100), (0, 100)]
    return poly(pts)


def sweep(s, bands, direction="left", kind="chevron", d=420, n=14, name="Banda"):
    """Bands = [(colour, enter_frame, exit_frame)] that cross the frame toward `direction`; each band's leading edge
    enters at enter_frame and its trailing edge at exit_frame; an edge crosses in n frames."""
    horiz = direction in ("left", "right")
    Lscr = 1920 if horiz else 1080
    H = (1080 if horiz else 1920) + 200
    v = (Lscr + d + 20) / n
    for i, (col, a, b) in enumerate(bands):
        W = v * (b - a)
        path = band_path(kind, W, d, H)

        def geom(fr, u, a=a, W=W):
            lead = Lscr + 10 - v * (fr - a)
            p = lead + (W + d) / 2
            if direction == "left":
                return p, 540, W + d, H, 0, 1
            if direction == "right":
                return 1920 - p, 540, W + d, H, 180, 1
            if direction == "up":
                return 960, p, W + d, H, 90, 1
            return 960, 1080 - p, W + d, H, -90, 1
        s.mblur(s.obj(f"{name} {i + 1}", solid(col), geom, path=path))


def tr_chevrons(direction, order, es_dir, en_dir, idx):
    def make():
        D = 1.4
        t, s = _tr(f"transicion-flechas-{idx}", f"Transición: flechas roja, blanca y negra {es_dir}",
                   f"Transition: red, white and black chevrons {en_dir}", order, D, ["flechas"])
        two_clips(s, 18)
        sweep(s, [(TR_RED, 0, 25), (TR_WHITE, 2, 28), (TR_BLACK, 4, 22)], direction, "chevron")
        return t
    make.__name__ = f"tr_chevrons_{idx}"
    return make


def tr_bars(direction, order, es_dir, en_dir, idx):
    def make():
        D = 1.4
        t, s = _tr(f"transicion-barras-{idx}", f"Transición: barras roja, blanca y negra {es_dir}",
                   f"Transition: red, white and black bars {en_dir}", order, D, ["barras"])
        two_clips(s, 18)
        sweep(s, [(TR_RED, 0, 24), (TR_WHITE, 3, 28), (TR_BLACK, 6, 22)], direction, "bar", d=0, n=12)
        return t
    make.__name__ = f"tr_bars_{idx}"
    return make


def tr_pills(direction, order, es_dir, en_dir, idx):
    def make():
        D = 1.5
        t, s = _tr(f"transicion-capsulas-{idx}", f"Transición: cápsulas {es_dir}", f"Transition: capsules {en_dir}",
                   order, D, ["cápsulas"])
        two_clips(s, 21)
        horiz = direction in ("left", "right")
        rows = 3
        cross = (1080 if horiz else 1920) / rows
        Lscr = 1920 if horiz else 1080
        v = (Lscr + 40) / 12
        for r in range(rows):
            for j, (col, a, b) in enumerate(((TR_RED, 0, 22), (TR_WHITE, 3, 26), (TR_BLACK, 6, 21))):
                lag = (1, 0, 2)[r] * 2
                a, b = a + lag, b + lag
                W = v * (b - a)
                c0 = cross * (r + 0.5)

                def geom(fr, u, a=a, W=W, c0=c0):
                    lead = Lscr + 10 - v * (fr - a)
                    p = lead + W / 2
                    if direction == "left":
                        return p, c0, W, cross + 4, 0, 1
                    return c0, 1080 - p, cross + 4, W, 0, 1
                s.mblur(s.obj(f"Cápsula {r + 1}.{j + 1}", solid(col), geom, radius=cross / 2,
                              base=((v * 22, cross + 4) if horiz else (cross + 4, v * 22))))
        return t
    make.__name__ = f"tr_pills_{idx}"
    return make


def tr_blocks(seed, order, idx):
    def make():
        import random
        D = 1.5
        t, s = _tr(f"transicion-bloques-{idx}", "Transición: bloques rojos, blancos y negros",
                   "Transition: red, white and black blocks", order, D, ["bloques"])
        two_clips(s, 21)
        rnd = random.Random(seed)
        cols, rows = 4, 3
        cw, rh = 1920 / cols, 1080 / rows
        for r in range(rows):
            for c in range(cols):
                base = (cols - 1 - c) * 2 + rnd.randint(0, 3)
                for j, (col, a, b) in enumerate(((TR_RED, 0, 24), (TR_WHITE, 3, 27), (TR_BLACK, 6, 21))):
                    a_, b_ = a + base * 0.6, b + base * 0.6
                    x0, y0 = c * cw, r * rh

                    def rect(fr, u, a_=a_, b_=b_, x0=x0, y0=y0):
                        grow = k(fr, a_, 5)
                        shrink = k(fr, b_, 5)
                        return (x0 + cw * (1 - grow), y0, x0 + cw * (1 - shrink) + 1, y0 + rh + 1) if fr < b_ else \
                            (x0, y0, x0 + cw * (1 - shrink) + 1, y0 + rh + 1)
                    s.mblur(s.rect(f"Bloque {r + 1}.{c + 1}.{j + 1}", solid(col), rect))
        return t
    make.__name__ = f"tr_blocks_{idx}"
    return make


SHAPES = {"circulo": ("ellipse", None, "círculo", "circle"),
          "hexagono": ("custom", regular(6, 0), "hexágono", "hexagon"),
          "cuadrado": ("custom", poly([(0, 0), (100, 0), (100, 100), (0, 100)]), "cuadrado", "square"),
          "estrella": ("custom", poly([(50 + (50 if i % 2 == 0 else 22) * math.cos(math.radians(-90 + 30 * i)),
                                       50 + (50 if i % 2 == 0 else 22) * math.sin(math.radians(-90 + 30 * i)))
                                      for i in range(12)]), "estrella", "star")}


def tr_shape(key, order):
    kind, path, es, en = SHAPES[key]

    def make():
        D = 1.9
        t, s = _tr(f"transicion-{key}", f"Transición: {es} rojo, blanco y negro que se abre",
                   f"Transition: opening red, white and black {en}", order, D, ["formas", es])
        two_clips(s, 27)
        turn = 0 if key == "circulo" else 1
        for j, (col, at) in enumerate(((TR_RED, 3), (TR_WHITE, 9), (TR_BLACK, 15))):
            s.mblur(s.obj(f"Forma {j + 1}", solid(col), lambda fr, u, at=at: (
                960, 540, 3000 * k(fr, at, 15), 3000 * k(fr, at, 15), 40 * turn * k(fr, at, 15),
                1.0 if fr < 42 else 0.0), kind="ellipse" if kind == "ellipse" else "rectangle", path=path))
        for j, (col, at) in enumerate(((TR_WHITE, 29), (TR_RED, 33))):
            s.mblur(s.obj(f"Forma (salida {j + 1})", solid(col), lambda fr, u, at=at: (
                960, 540, 3000 * k(fr, at, 12), 3000 * k(fr, at, 12), -40 * turn * k(fr, at, 12),
                1.0 if 29 <= fr < 50 else 0.0), kind="ellipse" if kind == "ellipse" else "rectangle", path=path))
        clip = s.t.photo(s.t.track("video", "Video 2 (encima)"), "h-city-03", 0.0, D, None, None,
                         reuse=s.t.slots[1].id)
        track = next(tr for tr in s.t.tracks if clip in tr.clips)
        mk = {"x": [], "y": [], "w": [], "h": []}
        for u, fr in s.each():
            sz = max(1e-3, 3000 * k(fr, 37, 12) / 1920)
            mk["x"].append((u, 0.5, "linear"))
            mk["y"].append((u, 0.5, "linear"))
            mk["w"].append((u, sz, "linear"))
            mk["h"].append((u, sz * 1920 / 1080, "linear"))
        geo = {"shape": "ellipse"} if kind == "ellipse" else {"shape": "path", "pathData": path}
        s.t.mask(track, clip, geo.pop("shape"), x=0.5, y=0.5, w=1e-3, h=1e-3,
                 keyframes={kk: keys(v) for kk, v in mk.items()}, **geo)
        return t
    make.__name__ = f"tr_shape_{key}"
    return make


def tr_swirl():
    D = 1.6
    t, s = _tr("transicion-remolino", "Transición: remolino rojo y blanco", "Transition: red and white swirl", 12270, D,
               ["líquido"])
    two_clips(s, 24)
    for i, (r, at) in enumerate(((2600, 0), (1900, 2), (1300, 4))):
        c = s.obj(f"Remolino {i + 1}", ring(TR_RED, 260 - 50 * i), lambda fr, u, r=r, at=at: (
            960 + 600 * (1 - k(fr, at, 12)), 540 - 300 * (1 - k(fr, at, 12)), r * k(fr, at, 15), r * k(fr, at, 15),
            300 * lin(fr, at, 30), 1.0 if fr < 27 else 0.0), path=arc(0, 300))
        wiggle(c, 30, 80, 2, i)
        s.fx(c, "stylize.twirl", animated={"angle": lambda fr, u, at=at: 160 * k(fr, at, 18)}, radius=0.7,
             centerX=0.5, centerY=0.5)
        s.mblur(c)
    c = s.obj("Rojo", solid(TR_RED), lambda fr, u: (960, 540, 2600 * k(fr, 6, 12), 2600 * k(fr, 6, 12), 0,
                                                    1.0 if fr < 30 else 0.0), kind="ellipse")
    wiggle(c, 60, 120, 2, 2)
    c = s.obj("Blanco", solid(TR_WHITE), lambda fr, u: (960, 540, 2600 * k(fr, 12, 12), 2600 * k(fr, 12, 12), 0,
                                                        1.0 if fr < 42 else 0.0), kind="ellipse")
    wiggle(c, 60, 120, 2, 3)
    clip = s.t.photo(s.t.track("video", "Video 2 (encima)"), "h-city-03", 0.0, D, None, None, reuse=s.t.slots[1].id)
    track = next(tr for tr in s.t.tracks if clip in tr.clips)
    mk = {"x": [], "y": [], "w": [], "h": []}
    for u, fr in s.each():
        sz = max(1e-3, 2.6 * k(fr, 24, 14))
        mk["x"].append((u, 0.45, "linear"))
        mk["y"].append((u, 0.6, "linear"))
        mk["w"].append((u, sz, "linear"))
        mk["h"].append((u, sz * 1920 / 1080, "linear"))
    s.t.mask(track, clip, "ellipse", x=0.45, y=0.6, w=1e-3, h=1e-3, keyframes={kk: keys(v) for kk, v in mk.items()})
    return t


TEMPLATES += [tr_swirl,
              tr_chevrons("left", 12271, "hacia la izquierda", "to the left", 1),
              tr_chevrons("down", 12272, "hacia abajo", "downward", 2),
              tr_chevrons("up", 12273, "hacia arriba", "upward", 3),
              tr_chevrons("right", 12274, "hacia la derecha", "to the right", 4),
              tr_blocks(3, 12275, 1), tr_blocks(8, 12276, 2),
              tr_bars("left", 12277, "hacia la izquierda", "to the left", 1),
              tr_bars("down", 12278, "hacia abajo", "downward", 2),
              tr_pills("left", 12279, "hacia la izquierda", "to the left", 1),
              tr_pills("down", 12280, "hacia abajo", "downward", 2),
              tr_shape("circulo", 12281), tr_shape("hexagono", 12282), tr_shape("cuadrado", 12283),
              tr_shape("estrella", 12284)]


# --- Typographic openers (95–117 s): one word at a time, flashes of the background ---------------------------------
def word(s, text, ink, a, b, colour, name, preset="fade", out="fade", stagger=0.04, duration=0.25, order="forward",
         geom=None, weight=900, family=M, **params):
    """A word shown from frame a to frame b: it comes in with `preset` and leaves with `out` (the clip ends at b)."""
    from scene import tanim, us
    c = s.say(text, ink, family, weight, colour, name, geom=geom)
    end = b / FPS
    c["timelineDurationUs"] = us(end)
    c["srcOutUs"] = us(end)
    c["textStyle"]["animation"] = {
        "in": tanim(preset, duration=duration, unit="character", stagger=stagger, ease="easeOut",
                    delay=round(a / FPS, 3), order=order, **params),
        "out": tanim(out, duration=0.15, unit="character", stagger=0.01, ease="easeIn", order="forward")}
    if weight >= 900:
        tight(c, -0.05)
    return c


def greys(clip, seed, lo=90, hi=255):
    """Each letter in its own grey (runs)."""
    import random
    rnd = random.Random(seed)
    runs = []
    for i, ch in enumerate(clip["textContent"]):
        if ch.strip():
            g = rnd.randint(lo, hi)
            runs.append({"start": i, "end": i + 1, "colorEnabled": True, "color": "#ff%02x%02x%02x" % (g, g, g)})
    clip["textStyle"]["runs"] = runs


def flashes(s, frames, colours, name="Destello"):
    """Full-frame flashes: [(frame, n_frames), ...]."""
    for i, ((f0, n), col) in enumerate(zip(frames, colours)):
        s.rect(f"{name} {i + 1}", solid(col), lambda fr, u: (-10, -10, 1930, 1090),
               op=lambda fr, u, f0=f0, n=n: 1.0 if f0 <= fr < f0 + n else 0.0)


def _o(id, es, en, order, dur):
    return _p(id, es, en, order, dur, "aperturas", ["apertura", "tipografía", "cinético"], thumb=round(dur * 0.82, 1))


def typo_subscribe():
    D = 7.4
    t = _o("apertura-tipografica-suscribete", "Apertura tipográfica: mira el episodio y suscríbete",
           "Typographic opener: watch the episode and subscribe", 12290, D)
    s = O(t, D)
    bg(s, "#000000")
    flashes(s, [(12, 3), (15, 3), (51, 3), (54, 3), (102, 3), (105, 3), (123, 3), (126, 6), (132, 6)],
            [WHITE, "#5A5A5A", "#4A4A4A", "#9A9A9A", "#A0A0A0", "#7A7A7A", "#E0E0E0", "#4A4A4A", "#9A9A9A"])
    words = (("WATCH", (550, 450, 1360, 640), 0, 24, 1), ("NEXT", (690, 450, 1250, 640), 24, 39, 2),
             ("EPISODE", (523, 440, 1390, 650), 39, 60, 3), ("AND", (720, 450, 1200, 640), 60, 75, 4),
             ("DON'T", (593, 450, 1295, 640), 75, 93, 5))
    for i, (text, ink, a, b, seed) in enumerate(words):
        c = word(s, text, ink, a, b, WHITE, f"Palabra {i + 1}", preset="ibs-scatter-gather", stagger=0.03,
                 duration=0.3, order="random")
        greys(c, seed)
    for i, (text, ink, a, b, seed) in enumerate((("FORGET", (543, 121, 1385, 325), 93, 132, 6),
                                                 ("TO", (817, 440, 1123, 645), 105, 135, 7),
                                                 ("SUBSCRIBE", (364, 715, 1563, 919), 114, 141, 8))):
        c = word(s, text, ink, a, b, WHITE, f"Palabra {i + 6}", preset="ibs-scatter-gather", stagger=0.03,
                 duration=0.3, order="random")
        greys(c, seed)
    c = word(s, "@YourChannel", (223, 428, 1723, 657), 138, D * FPS, WHITE, "Canal", preset="ibs-scatter-gather",
             stagger=0.04, duration=0.45, order="random")
    greys(c, 9, 140)
    return t


def typo_gaming():
    D = 7.4
    t = _o("apertura-tipografica-gaming", "Apertura tipográfica: el mejor canal de juegos",
           "Typographic opener: the best gaming channel", 12291, D)
    s = O(t, D)
    bg(s, "#FAFAFA")
    flashes(s, [(33, 3), (36, 3), (102, 3), (105, 3), (123, 3), (126, 3), (135, 6), (141, 6), (168, 3), (171, 3)],
            ["#1A1A1A", "#B0B0B0", "#4A4A4A", "#E0E0E0", "#1A1A1A", "#B0B0B0", "#1A1A1A", "#9A9A9A", "#4A4A4A",
             "#E0E0E0"])

    def zoom(a, n=24, x0=0.0):
        return lambda fr, u: (x0 * (1 - k(fr, a, n)), 0, 1 + 6 * (1 - k(fr, a, n)) ** 2, 0, 1)
    seq = (("THIS", (510, 410, 1410, 676), 3, 45, zoom(3, 27, -900)), ("IS", (820, 420, 1100, 660), 51, 75, None),
           ("THE BEST", (330, 420, 1590, 660), 75, 117, zoom(75, 27, 1500)),
           ("CHANNEL", (420, 440, 1500, 640), 117, 153, None), ("ABOUT", (590, 440, 1330, 640), 153, 177, None),
           ("GAMING", (500, 430, 1420, 650), 180, 219, None))
    for i, (text, ink, a, b, g) in enumerate(seq):
        c = word(s, text, ink, a, b, "#1A1A1A", f"Palabra {i + 1}", preset="fade" if g else "ibs-scatter-gather",
                 stagger=0.03, duration=0.25, order="random", geom=g)
        greys(c, i + 20, 20, 120)
        if g:
            s.mblur(c)
    word(s, "@channel", (560, 450, 1360, 640), 219, D * FPS, "#1A1A1A", "Canal", preset="fade", stagger=0.02,
         duration=0.15)
    return t


def typo_red():
    D = 7.6
    t = _o("apertura-tipografica-roja", "Apertura tipográfica roja: nuevo video, dale like y suscríbete",
           "Red typographic opener: new video, like and subscribe", 12292, D)
    s = O(t, D)
    bg(s, "#1A1A1A")
    s.rect("Fondo rojo", solid("#E3061F"), lambda fr, u: (-10, -10, -10 + 1940 * k(fr, 72, 9), 1090),
           op=lambda fr, u: 1.0 if 72 <= fr < 168 else 0.0)
    s.rect("Fondo rojo (salida)", solid("#E3061F"), lambda fr, u: (-10, 540 - 550 * (1 - k(fr, 165, 6)), 1930,
                                                                    540 + 550 * (1 - k(fr, 165, 6))),
           op=lambda fr, u: 1.0 if 165 <= fr < 172 else 0.0)
    red_words = (("NEW", (650, 450, 1270, 650), 15, 33), ("VIDEO", (600, 450, 1370, 650), 36, 51),
                 ("ON", (800, 450, 1120, 650), 51, 63), ("MY", (790, 450, 1130, 650), 63, 72))
    for i, (text, ink, a, b) in enumerate(red_words):
        word(s, text, ink, a, b, "#E3061F", f"Palabra {i + 1}", preset="blur-in", stagger=0.0, duration=0.2, blur=24,
             geom=(lambda fr, u, a=a, b=b: (0, 0, 1 + 0.6 * k(fr, b - 3, 3), 0, 1)) if i == 0 else None)
    dark = (("CHANNEL", (335, 470, 1540, 640), 75, 105, "im-motion-blur-slide"),
            ("LIKE", (570, 440, 1370, 670), 105, 132, "drop"), ("AND", (700, 450, 1220, 650), 135, 150, "im-roll-in"),
            ("SUBSCRIBE", (330, 470, 1545, 640), 150, 171, "ibs-pancake-pop"))
    for i, (text, ink, a, b, pre) in enumerate(dark):
        word(s, text, ink, a, b, "#1A1A1A", f"Palabra {i + 5}", preset=pre, stagger=0.05, duration=0.3,
             order="backward" if i == 0 else "forward")
    word(s, "@yourname", (234, 420, 1686, 655), 177, D * FPS, "#E3061F", "Canal", preset="blur-in", stagger=0.0,
         duration=0.3, blur=30, geom=lambda fr, u: (0, 0, 1 + 0.5 * (1 - k(fr, 177, 9)), 0, 1 - 0.7 * k(fr, 195, 30)))
    return t


TEMPLATES += [typo_subscribe, typo_gaming, typo_red]
