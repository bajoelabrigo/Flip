"""LOGO folder video 3 as Stock templates (lg3-*). See docs/plan-logo.md.

`48635588.mp4` (1920×1080 at 29.97 fps): four logo reveals, each shown «ORIGINAL» and «CUSTOM» side by side (the
same motion in two colour sets; the colours here are editable). Studied on 10 fps sheets of the «ORIGINAL» half
(a 960×540 crop, ×2 to 1920×1080); notes in tienda/plantillas/estudio-48635588/NOTAS.md. Kit de YouTube ›
Aperturas, order 13900-.

1. a ring of dashes spins and closes, a pie fills from twelve o'clock and keeps changing colour, concentric discs pop
   into a target and the last one, red, carries the logo;
2. a sphere of curved stripes turns, goes blue and becomes a disc with the logo, which shrinks up over a tagline;
3. a square made of slats opens like a blind while it turns upright, goes flat and the logo glitches in;
4. three coloured waves flow along a line, flatten and leave the logo with its tagline.

The mark is always the user's logo (the `logo-flip` slot), revealed where and when the reference shows its brand;
the brand words become «YOUR BRAND» and the tagline is generic and editable. Each piece ends on the logo (the
reference cuts to the next one).
"""

from __future__ import annotations

import math
import random

from kit import Box, wide
from scene import gradient, keys, no_stroke
from templates_tit_c import FPS, k
from templates_tit_e import solid
from templates_tit_h import arc, fill, poly, ring, rot_pt
from templates_yp3 import B

WHITE = "#FFFFFF"
BEBAS, M = "Bebas Neue", "Montserrat"
TAGLINE = "YOUR TAGLINE"
CIRCLE = arc(-90, 270, 96)  # starts at twelve o'clock, clockwise


# --- time helpers (u in seconds) ---------------------------------------------------------------------------------
def e(u, a, n):
    """0 → 1 eased in and out from second a over n seconds."""
    return k(u * FPS, a * FPS, n * FPS)


def eo(u, a, n, p=3):
    """0 → 1 eased out (fast start) from second a over n seconds."""
    q = min(1.0, max(0.0, (u - a) / max(1e-6, n)))
    return 1 - (1 - q) ** p


def ln(u, a, n):
    return min(1.0, max(0.0, (u - a) / max(1e-6, n)))


def mix(c0, c1, q):
    a = [int(c0[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * q):02X}" for x, y in zip(a, b))


def radial(colour, a0, a1=0.0):
    from scene import argb
    return [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
             "paint": {"kind": "gradient", "color": argb(colour, a0),
                       "gradient": {"kind": "radial", "stops": [{"pos": 0, "color": argb(colour, a0)},
                                                                {"pos": 1, "color": argb(colour, a1)}],
                                    "angle": 0, "space": "block"}}}, no_stroke()]


def hline(colour, alpha=0.8):
    """A thin line that fades out at both ends."""
    return [gradient([(0.0, colour, 0.0), (0.5, colour, alpha), (1.0, colour, 0.0)], angle=0), no_stroke()]


def stroke_only(colour, width, cap="butt"):
    return [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}},
            {"id": "stroke", "kind": "stroke", "enabled": True, "width": width, "strokeAlign": "center",
             "opacity": 1.0, "cap": cap, "join": "round", "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}]


class L(B):
    """A logo piece: frames run forwards (fr = u × FPS); every element is keyed per frame."""

    def background(self, layers, name="Fondo"):
        c = self.rect(name, layers, lambda fr, u: (-10, -10, 1930, 1090))
        c["layoutRole"] = "cover"
        return c

    def glow(self, name, colour, cx, cy, w, h, a0, op=None):
        c = self.obj(name, radial(colour, a0), lambda fr, u: (cx, cy, w, h, 0, op(u) if op else 1.0), kind="ellipse")
        c["layoutRole"] = "cover"
        return c

    def trim(self, clip, end, start=None):
        """Trim Paths keyed per frame: end(u) / start(u) from 0 to 1."""
        st = clip["shapeStyle"].setdefault("keyframes", {})
        st["trimEnd"] = keys([(u, round(100 * max(0.0, min(1.0, end(u))), 3), "linear") for u, fr in self.each()])
        st["trimStart"] = keys([(u, round(100 * max(0.0, min(1.0, start(u))), 3), "linear")
                                for u, fr in self.each()]) if start else keys([(0.0, 0.0, "hold")])
        return clip

    def morphing(self, name, layers, box, path_at, step=1):
        """A shape in the fixed screen box (x0, y0, x1, y1) whose outline is path_at(u) -> [(x, y) screen px]
        (always the same number of points), morphed frame by frame; returns the clip."""
        x0, y0, x1, y1 = box
        w, h = x1 - x0, y1 - y0
        frames = [u for u, fr in self.each()][::step]
        shapes, marks = [], []
        for i, u in enumerate(frames):
            pts = path_at(u)
            shapes.append("M " + " L ".join(f"{(x - x0) / w * 100:.2f} {(y - y0) / h * 100:.2f}" for x, y in pts)
                          + (" Z" if getattr(path_at, "closed", True) else ""))
            marks.append((u, i))
        c = self.obj(name, layers, lambda fr, u: ((x0 + x1) / 2, (y0 + y1) / 2, w, h, 0, 1), path=shapes[0])
        st = c["shapeStyle"]
        st["pathShapes"] = shapes
        st.setdefault("keyframes", {})["path"] = keys([(u, i, "linear") for u, i in marks])
        return c

    def logo(self, geom, name="Logo", reuse=None, matte=None):
        """The user's logo: geom(fr, u) = (cx, cy, size, op); matte = a clip whose alpha shows it (kept on screen)."""
        g = [(u, geom(fr, u)) for u, fr in self.each()]
        d = max(1.0, max(v[2] for _, v in g))
        box = Box(960 - d / 2, 540 - d / 2, d, d)
        motion = [(u, {"s": max(1e-4, v[2] / d), "dx": v[0] - 960, "dy": v[1] - 540}, "linear") for u, v in g]
        clip = self.t.photo(self.t.track("video", name), "logo-flip", 0.0, self.dur, box, motion, label="Tu logo",
                            brandRole="logo", reuse=reuse)
        if any(v[3] < 0.999 for _, v in g):
            clip["opacity"] = keys([(u, round(max(0.0, min(1.0, v[3])), 4), "linear") for u, v in g])
        if matte is not None:
            clip["matte"] = {"clip": matte["id"], "mode": "alpha", "keepSource": True}
        return clip


def art_except(t, keep=("Fondo", "Destello")):
    """Every clip is design ("art", scaled and placed together in a Short) except the backgrounds named with `keep`,
    which stretch with the frame: the waves and the dash ring are wider than tall and the layout guess would take
    them for backdrops (as templates_yp4.art_except)."""
    for track in t.tracks:
        for clip in track.clips:
            if clip.get("type") in ("audio", "adjustment", "composite") or "layoutRole" in clip:
                continue
            name = clip.get("name") or track.name
            clip["layoutRole"] = "backdrop" if name.startswith(tuple(keep)) else "art"
    return t


def _p(id, es, en, order, dur, tags=(), thumb=None):
    return wide(f"lg3-{id}", es, en, "ytkit", dur, order=order,
                tags=["kit:aperturas", "logo", "revelado de logo", "intro"] + list(tags),
                thumb_at=thumb if thumb is not None else round(dur * 0.8, 1))


# --- 1. Ring of dashes → pie → target → red disc with the logo (9.0–12.6 s) ------------------------------------------
def pie_target():
    D = 5.0
    t = _p("torta-diana", "Logo: anillo de rayas, torta de colores y diana",
           "Logo: dash ring, colour pie and target", 13900, D, ["torta", "círculo", "pastel"], thumb=4.0)
    s = L(t, D)
    CX, CY = 960, 540
    PEACH, CORAL, YELLOW, BLUE, ORANGE, REDOR, RED = ("#FABE95", "#FE9894", "#F2FD91", "#C1D3FB", "#FFC479",
                                                      "#FF9E84", "#FA6A6B")
    LINE = "#F2A48C"
    s.background(solid("#F2F2F2"))
    s.glow("Fondo (luz)", WHITE, 960, 540, 1500, 1100, 0.45)
    rise = lambda u: -45 * e(u, 2.45, 0.9)  # noqa: E731  the disc climbs over the tagline

    # Thin circle and arcs (drawn on, turning, gone by 2.4 s).
    c = s.obj("Círculo fino", stroke_only(LINE, 3), lambda fr, u: (CX, CY, 560, 560, 0, 1 - e(u, 1.9, 0.3)),
              path=CIRCLE)
    s.trim(c, lambda u: eo(u, 0.4, 0.45))
    for i, (r, span, a0, spin, at) in enumerate(((340, 230, 160, 90, 0.55), (378, 140, -30, -70, 0.65),
                                                 (356, 100, 60, 120, 1.0))):
        c = s.obj(f"Arco {i + 1}", stroke_only(LINE, 3),
                  lambda fr, u, r=r, a0=a0, spin=spin, at=at: (CX, CY, 2 * r, 2 * r, a0 + spin * eo(u, at, 1.6),
                                                              (1 - e(u, 2.0 + 0.1 * i, 0.4))),
                  path=arc(-90, -90 + span, 48))
        s.trim(c, lambda u, at=at: eo(u, at, 0.4))

    # The ring of dashes: an arc that closes while it spins clockwise and gathers, peach turning coral.
    rnd = random.Random(48635588)
    N = 30
    dash = [(360 * i / N + rnd.uniform(-3, 3), rnd.uniform(40, 130), rnd.uniform(26, 44)) for i in range(N)]

    def dash_geom(i, which):
        a_i, L_, W_ = dash[i]

        def g(fr, u):
            sweep = 360 * eo(u, 0.05, 0.6, 2)
            rel = (a_i + 200) % 360  # the arc grows from the lower left
            show = min(1.0, max(0.0, (sweep - rel) / 25))
            gone = e(u, 0.78 + 0.32 * (a_i / 360), 0.14)  # they leave as the pie sweeps past them
            theta = a_i - 90 - 150 * (1 - eo(u, 0.0, 1.1))
            r = 470 - 120 * eo(u, 0.0, 0.8) - 40 * gone
            ln_ = L_ * (1 - gone) * (0.6 + 0.4 * eo(u, 0.0, 0.5))
            x = CX + math.cos(math.radians(theta)) * (r + ln_ / 2)
            y = CY + math.sin(math.radians(theta)) * (r + ln_ / 2)
            tint = e(u, 0.35, 0.35)
            op = show * (1 - gone) * (1 - tint if which == 0 else tint)
            return x, y, W_, max(0.0, ln_), theta - 90, op
        return g
    for which, colour in ((0, PEACH), (1, CORAL)):
        for i in range(N):
            s.obj(f"Raya {i + 1}" + (" (coral)" if which else ""), solid(colour), dash_geom(i, which))

    # Satellites: small rings and dots riding round the dashes.
    for i, (r, a0, d, kind) in enumerate(((470, 200, 40, "ring"), (430, 20, 22, "dot"), (400, 110, 30, "ring"),
                                          (360, 300, 14, "dot"), (450, 330, 28, "ring"))):
        def sg(fr, u, r=r, a0=a0, d=d):
            a = math.radians(a0 - 90 + 70 * eo(u, 0.1, 1.2))
            rr = r - 30 * eo(u, 0.2, 1.0)
            return CX + math.cos(a) * rr, CY + math.sin(a) * rr, d, d, 0, e(u, 0.1 + 0.1 * i, 0.2) * (1 - e(u, 1.0, 0.3))
        s.obj(f"Satélite {i + 1}", ring(CORAL, 5) if kind == "ring" else solid(CORAL), sg, kind="ellipse")

    # The pie: each slice enters at twelve o'clock and pushes the others round (a wide stroke on a circle, trimmed).
    R = lambda u: 300 - 36 * e(u, 1.55, 0.4)  # noqa: E731
    slices = [(CORAL, 0.80, 0.32, 150, "out"), (PEACH, 0.95, 0.28, 140, "out"), (BLUE, 1.07, 0.26, 130, "out"),
              (YELLOW, 1.30, 0.30, 150, "out"), (REDOR, 1.48, 0.50, 370, "lin")]

    def span(j, u):
        colour, born, grow, full, how = slices[j]
        return full * (ln(u, born, grow) if how == "lin" else eo(u, born, grow, 2))

    def bounds(j, u):
        a0 = sum(span(i, u) for i in range(j + 1, len(slices)))
        return a0, a0 + span(j, u)
    for j, (colour, born, *_rest) in enumerate(slices):
        c = s.obj(f"Porción {j + 1}", stroke_only(colour, 300),
                  lambda fr, u: (CX, CY, R(u), R(u), 0, (1.0 if u >= 0.8 else 0.0) * (1 - ln(u, 2.12, 0.05))),
                  path=CIRCLE, base=(300, 300))
        s.trim(c, lambda u, j=j: min(1.0, bounds(j, u)[1] / 360), lambda u, j=j: min(1.0, bounds(j, u)[0] / 360))

    # The target: discs grow from the centre one over the other; the last, red, carries the logo.
    shrink = lambda u: 1 - 0.11 * e(u, 1.85, 0.75)  # noqa: E731
    discs = [(ORANGE, 1.70, 262), ("#C9D2F8", 1.86, 258), (YELLOW, 1.98, 254), (RED, 2.12, 262)]
    red = None
    for i, (colour, born, rf) in enumerate(discs):
        last = i == len(discs) - 1

        def dg(fr, u, born=born, rf=rf, last=last, i=i):
            r = rf * shrink(u) * eo(u, born, 0.5, 2)
            covered = 1.0 if last else 1 - ln(u, discs[i + 1][1] + 0.38, 0.06)
            return CX, CY + rise(u), 2 * r, 2 * r, 0, (1.0 if u >= born else 0.0) * covered
        layers = [fill(colour), {"id": "stroke", "kind": "stroke", "enabled": True, "width": 5, "strokeAlign": "inside",
                                 "opacity": 1.0, "paint": {"kind": "solid", "color": "#fff3a07c"}}] if last \
            else solid(colour)
        c = s.obj("Disco" if last else f"Diana {i + 1}", layers, dg, kind="ellipse", base=(2 * rf, 2 * rf))
        if last:
            red = c
    s.logo(lambda fr, u: (CX, CY + rise(u), 250, 1.0 if u >= 2.12 else 0.0), matte=red)

    # Ripples out of the disc.
    for i in range(3):
        at = 2.45 + 0.16 * i

        def rg(fr, u, at=at):
            r = (236 + 120 * eo(u, at, 1.0)) * (1.0 if u < 2.6 else 1.0)
            return CX, CY + rise(u), 2 * r, 2 * r, 0, (0.9 if u >= at else 0.0) * (1 - ln(u, at + 0.2, 0.8))
        s.obj(f"Onda {i + 1}", ring("#F59A93", 3 - 0.6 * i), rg, kind="ellipse", base=(712, 712))

    # The tagline and its line.
    ink = (800, 800, 1120, 846)
    s.say(TAGLINE, ink, BEBAS, 400, "#5C5C5C", "Lema", geom=lambda fr, u: (0, 14 * (1 - eo(u, 2.35, 0.6)), 1, 0,
                                                                         e(u, 2.35, 0.5)))
    s.rect("Lema (línea)", hline("#8C8C8C", 0.7), lambda fr, u: (960 - 280 * eo(u, 2.6, 0.6), 868,
                                                                  960 + 280 * eo(u, 2.6, 0.6), 871))
    return t


# --- 2. Sphere of curved stripes → blue disc → logo over a tagline (13.1–16.6 s) --------------------------------------
def _band_outline(R, axis, h0, h1, front, n=72, m=96):
    """The part of the band h0..h1 (heights along `axis`, -1..1) of a sphere of radius R that faces the viewer
    (front) or away from it, as an outline of m screen points (orthographic, centre at 0, z toward the viewer)."""
    ax, ay, az = axis
    # Two unit vectors perpendicular to the axis.
    ux, uy, uz = (-ay, ax, 0.0) if abs(az) < 0.9 else (0.0, -az, ay)
    nn = math.sqrt(ux * ux + uy * uy + uz * uz)
    ux, uy, uz = ux / nn, uy / nn, uz / nn
    vx, vy, vz = ay * uz - az * uy, az * ux - ax * uz, ax * uy - ay * ux
    sign = 1.0 if front else -1.0

    def point(h, th):
        rho = math.sqrt(max(0.0, 1 - h * h))
        wx, wy, wz = (ux * math.cos(th) + vx * math.sin(th), uy * math.cos(th) + vy * math.sin(th),
                      uz * math.cos(th) + vz * math.sin(th))
        return R * (h * ax + rho * wx), R * (h * ay + rho * wy), R * (h * az + rho * wz)

    hs = [h0 + (h1 - h0) * j / 16 for j in range(17)]
    spans = []
    for i in range(n):
        th = 2 * math.pi * i / n
        vis = [h for h in hs if sign * point(h, th)[2] >= 0]
        spans.append((min(vis), max(vis)) if vis else None)
    if all(sp is None for sp in spans):
        # Nothing shows: a speck instead of a collapsed outline (a path of one repeated point draws as its box).
        return [(0.3 * math.cos(2 * math.pi * j / m), 0.3 * math.sin(2 * math.pi * j / m)) for j in range(m)]
    # Start right after a hidden meridian so the visible run is contiguous.
    start = next((i for i in range(n) if spans[i] is None and spans[(i + 1) % n] is not None), None)
    order = [(start + 1 + j) % n for j in range(n)] if start is not None else list(range(n))
    run = [(i, 2 * math.pi * i / n) for i in order if spans[i] is not None]
    if start is None:  # a whole ring: close it (a keyhole outline, filled as a ring)
        run.append((run[0][0], run[0][1] + 2 * math.pi))
    top = [point(spans[i][1], th)[:2] for i, th in run]
    bot = [point(spans[i][0], th)[:2] for i, th in reversed(run)]
    pts = top + bot
    # Resample to m points by length so every frame has the same count.
    seg = [math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    total = sum(seg) or 1.0
    out, acc, i = [], 0.0, 0
    for j in range(m):
        target = total * j / m
        while acc + seg[i] < target and i < len(pts) - 1:
            acc += seg[i]
            i += 1
        q = (target - acc) / (seg[i] or 1.0)
        a, b = pts[i], pts[(i + 1) % len(pts)]
        out.append((a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q))
    return out


def sphere_disc():
    D = 5.0
    t = _p("esfera", "Logo: esfera de franjas que se vuelve disco", "Logo: striped sphere that becomes a disc",
           13901, D, ["esfera", "azul", "corporativo"], thumb=4.0)
    s = L(t, D)
    CX, CY = 960, 540
    BLUE, PALE, DEEP, INNER = "#8EC4EC", "#C9CFE4", "#68AAD6", "#5E6F86"
    s.background([gradient([(0.0, "#F4F2F5"), (0.55, "#EFE6EA"), (1.0, "#B9979F")], angle=90), no_stroke()])
    s.glow("Fondo (bruma)", "#F2C3A8", 260, 860, 1300, 900, 0.75)
    s.glow("Fondo (luz)", WHITE, 1000, 470, 1700, 1000, 0.85)
    for i, r in enumerate((150, 210, 260)):
        s.obj(f"Fondo (aro {i + 1})", ring("#FFFFFF", 4), lambda fr, u, r=r: (230, 560, 2 * r, 2 * r, 0, 0.18),
              kind="ellipse")

    Rs = lambda u: 425 - 45 * eo(u, 0.1, 0.9)  # noqa: E731

    def axis(u):
        psi = math.radians(140 * (1 - eo(u, 0.0, 1.3, 2)) + 15)
        a0 = (0.5, -0.56, 0.68)
        x, y, z = a0[0] * math.cos(psi) + a0[2] * math.sin(psi), a0[1], -a0[0] * math.sin(psi) + a0[2] * math.cos(psi)
        n = math.sqrt(x * x + y * y + z * z)
        return x / n, y / n, z / n
    bands = [(-0.92, -0.58), (-0.40, 0.06), (0.24, 0.60), (0.74, 0.96)]
    WIDE = 1  # this stripe widens over the whole front and becomes the disc

    def band_at(j, front):
        def f(u):
            h0, h1 = bands[j]
            if j == WIDE:
                q = e(u, 0.72, 0.36)
                h0, h1 = h0 + (-1.0 - h0) * q, h1 + (1.0 - h1) * q
            else:
                thin = e(u, 0.55 + 0.08 * j, 0.35)  # the other stripes thin away
                mid = (h0 + h1) / 2
                h0, h1 = mid + (h0 - mid) * (1 - thin), mid + (h1 - mid) * (1 - thin) + 0.004
            return [(CX + x, CY + y) for x, y in _band_outline(Rs(u), axis(u), h0, h1, front)]
        return f
    box = (CX - 440, CY - 440, CX + 440, CY + 440)
    for j in range(len(bands)):
        c = s.morphing(f"Franja {j + 1} (dentro)", [gradient([(0.0, "#8D9AAE"), (1.0, INNER)], angle=90),
                                                      no_stroke()], box, band_at(j, False))
        gone = (0.45, 0.2) if j == WIDE else (1.05 + 0.1 * j, 0.35)  # the widening stripe's inside is never seen
        c["opacity"] = keys([(u, round((1 - e(u, *gone)) * e(u, 0.05, 0.3), 4), "linear")
                             for u, fr in s.each()])
    s.obj("Esfera (contorno)", ring("#FFFFFF", 3), lambda fr, u: (CX, CY, 2 * Rs(u) + 24, 2 * Rs(u) + 24, 0,
                                                                 0.8 * e(u, 0.0, 0.2) * (1 - e(u, 0.4, 0.3))),
          kind="ellipse", base=(874, 874))
    # The disc: blue as it forms, pale, then deep blue; it shrinks up with a blur at the end.
    dr = lambda u: (300 + 60 * eo(u, 0.95, 0.3)) - 120 * e(u, 2.35, 0.32)  # noqa: E731
    dy = lambda u: -60 * e(u, 2.35, 0.32)  # noqa: E731
    disc = s.obj("Disco", [fill(PALE), {"id": "stroke", "kind": "stroke", "enabled": True, "width": 4,
                                        "strokeAlign": "inside", "opacity": 1.0,
                                        "paint": {"kind": "solid", "color": "#ffdce8f6"}}],
                 lambda fr, u: (CX, CY + dy(u), 2 * dr(u), 2 * dr(u), 0, e(u, 0.95, 0.2)), kind="ellipse",
                 base=(720, 720))
    deep = s.obj("Disco (azul)", solid(DEEP), lambda fr, u: (CX, CY + dy(u), 2 * dr(u) - 6, 2 * dr(u) - 6, 0,
                                                             max(0.85 * e(u, 0.95, 0.12) * (1 - e(u, 1.1, 0.25)),
                                                                 e(u, 1.75, 0.65))),
                 kind="ellipse", base=(714, 714))
    blur = {"u_blurRadius": lambda fr, u: 26 * math.sin(math.pi * ln(u, 2.33, 0.36))}
    s.fx(disc, "builtin.effects.gaussian_blur", animated=blur)
    s.fx(deep, "builtin.effects.gaussian_blur", animated=blur)
    lg = s.logo(lambda fr, u: (CX, CY + dy(u), 0.78 * dr(u), e(u, 0.4, 0.4)))
    s.fx(lg, "builtin.effects.gaussian_blur", animated=blur)
    for j in range(len(bands)):
        c = s.morphing(f"Franja {j + 1}", [gradient([(0.0, "#F4F7FB"), (1.0, BLUE)], angle=90), no_stroke()], box,
                       band_at(j, True))
        c["opacity"] = keys([(u, round((1 - e(u, 0.95 + 0.06 * j, 0.25)) * e(u, 0.05, 0.3), 4), "linear")
                             for u, fr in s.each()])
        tint = s.morphing(f"Franja {j + 1} (cristal)", [gradient([(0.0, "#FFFFFF"), (1.0, "#E9C2A8")], angle=90),
                                                         no_stroke()], box, band_at(j, True), step=1)
        tint["opacity"] = keys([(u, round(0.65 * e(u, 0.05, 0.25) * (1 - e(u, 0.32, 0.3)) *
                                          (1 - e(u, 0.95 + 0.06 * j, 0.25)), 4), "linear") for u, fr in s.each()])
    # A thin swoosh left from the last stripe.
    sw = s.obj("Trazo", stroke_only("#7D8798", 5, "round"),
               lambda fr, u: (CX + 30, CY + 40, 760, 760, 40 + 30 * eo(u, 0.9, 0.8),
                              e(u, 0.9, 0.15) * (1 - e(u, 1.25, 0.35))), path=arc(10, 100, 32))
    s.trim(sw, lambda u: 1.0, lambda u: e(u, 1.0, 0.6))
    # The tagline lands with a few specks.
    ink = (845, 810, 1075, 840)
    s.say(TAGLINE, ink, BEBAS, 400, "#4F6F8F", "Lema", geom=lambda fr, u: (0, 0, 1, 0, e(u, 2.6, 0.3)))
    s.burst("Chispa", 960, 846, 2.55 * FPS, "#5D7896", n=12, r=150, size=7, life=16, seed=3, r0=40)
    s.rect("Lema (línea)", hline("#6F86A0", 0.6), lambda fr, u: (960 - 120 * eo(u, 2.7, 0.5), 872,
                                                                  960 + 120 * eo(u, 2.7, 0.5), 874))
    return t


# --- 3. Slatted square that opens like a blind and shows the logo (17.0–20.6 s) ---------------------------------------
def slat_square():
    D = 5.0
    t = _p("persiana", "Logo: cuadrado de lamas que se abre", "Logo: slatted square that opens", 13902, D,
           ["cuadrado", "gris", "minimalista"], thumb=4.0)
    s = L(t, D)
    GREY, BEIGE = "#CACED2", "#D9C6BA"
    s.background(solid("#E4E8EC"))
    s.glow("Fondo (mancha 1)", "#B7CBE0", 1760, 960, 1100, 800, 0.8)
    s.glow("Fondo (mancha 2)", "#C2D3E6", 80, 640, 800, 900, 0.7)
    s.glow("Fondo (luz)", "#F4F6F8", 900, 400, 1500, 900, 0.8)
    s.rect("Fondo (línea)", hline("#BFCDDC", 0.9), lambda fr, u: (-10, 298, 1930, 301))
    for i, x in enumerate((240, 560, 1150, 1700)):
        s.obj(f"Fondo (punto {i + 1})", solid("#C3D0DE", 0.8), lambda fr, u, x=x: (x, 300, 22, 22, 0, 1),
              kind="ellipse")
    for i in range(24):
        s.obj(f"Fondo (trazo {i + 1})", solid("#C9D3DE"), lambda fr, u, i=i: (40 + 80 * i, 842, 10, 3, 0, 0.8))

    C = lambda u: (630 + 330 * eo(u, 0.3, 1.0, 2), 600 - 130 * eo(u, 0.3, 1.7, 2))  # noqa: E731
    rho = lambda u: -25 + 25 * eo(u, 0.35, 1.75, 1.5)  # noqa: E731
    W, H, N = 500, 492, 12
    sw_ = W / N
    sc = lambda u: 1 + 0.3 * (1 - eo(u, 0.35, 1.3, 2))  # noqa: E731  nearer while it turns

    def at(u, lx, ly):
        cx, cy = C(u)
        return rot_pt(cx + lx, cy + ly, rho(u), cx, cy)

    # A thin slanted line and a big frame that lag behind the square.
    s.obj("Línea", solid("#C4CCD6"), lambda fr, u: (580, 670, 3, 700, -24, e(u, 0.1, 0.2) * (1 - e(u, 0.45, 0.3))))
    s.obj("Marco", ring("#D3DAE2", 3), lambda fr, u: (*at(u, 40, 10), 640, 640, rho(u) - 10 * (1 - e(u, 0.3, 1.2)),
                                                      e(u, 0.2, 0.3) * (1 - e(u, 1.2, 0.4))))
    for i, (lx, ly, d) in enumerate(((-330, -260, 26), (300, 280, 22), (-310, 300, 18))):
        s.obj(f"Cuadradito {i + 1}", ring("#C2C9D2", 3),
              lambda fr, u, lx=lx, ly=ly, d=d: (*at(u, lx * (1 + 0.2 * u), ly), d, d, rho(u) + 30 * u,
                                                e(u, 0.3, 0.3) * (1 - e(u, 1.4, 0.4))))

    # The slats: each turns from edge-on to flat about its own vertical axis, left first, packed side by side (so
    # the square starts as a narrow bundle and widens as they open, as a blind does).
    def slat_widths(u):
        out = []
        for i in range(N):
            a = math.radians(90 * (1 - eo(u, 0.3 + 0.05 * i, 0.62, 2)))
            out.append((sc(u) * sw_ * math.cos(a), sc(u) * 12 * math.sin(a)))
        return out

    def slat(i, face):
        def g(fr, u):
            ws = slat_widths(u)
            tot = sum(f + d for f, d in ws)
            left = -tot / 2 + sum(f + d for f, d in ws[:i])
            fw, sd = ws[i]
            op = e(u, 0.3, 0.12) * (1 - ln(u, 1.42, 0.06))
            if face:
                x, y = at(u, left + sd + fw / 2, 0)
                return x, y, max(0.0, fw), H * sc(u), rho(u), op
            x, y = at(u, left + sd / 2, 0)
            return x, y, max(0.0, sd), H * sc(u), rho(u), op
        return g
    for i in range(N):
        s.obj(f"Lama {i + 1} (canto)", solid("#C6CACF"), slat(i, False))
        s.obj(f"Lama {i + 1}", [gradient([(0.0, "#E6E7E9"), (1.0, "#B9BDC2")], angle=0), no_stroke()], slat(i, True))

    def flat(colour, op, name):
        s.obj(name, solid(colour), lambda fr, u: (*at(u, 0, 0), W * sc(u), H * sc(u), rho(u), op(u)), radius=10,
              base=(W, H))
        s.obj(f"{name} (pico)", solid(colour), lambda fr, u: (*at(u, (W / 2 - 12) * sc(u), (H / 2 + 12) * sc(u)), 24 * sc(u),
                                                                 24 * sc(u), rho(u), op(u)),
              path=poly([(0, 0), (100, 0), (100, 100)]))
    flat(BEIGE, lambda u: e(u, 1.18, 0.22), "Cuadrado (beige)")
    sq_op = lambda u: e(u, 1.65, 0.35)  # noqa: E731
    s.obj("Cuadrado", solid(GREY), lambda fr, u: (*at(u, 0, 0), W, H, rho(u), sq_op(u)), radius=10, base=(W, H))
    s.obj("Cuadrado (pico)", solid(GREY), lambda fr, u: (*at(u, W / 2 - 12, H / 2 + 12), 24, 24, rho(u), sq_op(u)),
          path=poly([(0, 0), (100, 0), (100, 100)]))

    # The logo glitches in: strips of it (each a track matte) flicker on in random order.
    rnd = random.Random(17)
    K = 6
    first = None
    for i in range(K):
        flick = sorted(rnd.uniform(0.8, 2.15) for _ in range(6))

        def sop(u, flick=flick):
            if u >= 2.25:
                return 1.0
            on = sum(1 for f in flick if f <= u) % 2 == 1
            return (0.55 if u < 1.3 else 1.0) if on else 0.0
        strip = s.obj(f"Logo (franja {i + 1})", solid(WHITE),
                      lambda fr, u, i=i: (*at(u, (-150 + 300 * (i + 0.5) / K) * sc(u), 0), (300 / K + 1) * sc(u), 320 * sc(u),
                                         rho(u), sop(u)))
        clip = s.logo(lambda fr, u: (*at(u, 0, 0), 270 * sc(u), 1.0), name=f"Logo {i + 1}" if i else "Logo",
                      reuse=first["placeholderId"] if first else None)
        clip["rotation"] = keys([(u, round(rho(u), 3), "linear") for u, fr in s.each()])
        clip["matte"] = {"clip": strip["id"], "mode": "alpha"}
        first = first or clip

    # A grey bar grows under the square and pulls back to the right, leaving the tagline.
    bar = lambda u: (710 + 500 * e(u, 2.5, 0.35), 710 + 500 * eo(u, 2.1, 0.35))  # noqa: E731
    s.rect("Barra", solid("#BFC3C8"), lambda fr, u: (bar(u)[0], 852, bar(u)[1], 884),
           op=lambda fr, u: 1.0 if 2.1 <= u < 2.86 else 0.0)
    ink = (845, 855, 1075, 882)
    s.say(TAGLINE, ink, BEBAS, 400, "#2A2C30", "Lema", reveal=lambda fr: (700, 840, bar(fr / FPS)[0], 900)
          if fr / FPS >= 2.5 else (0, 0, 0, 0))
    s.rect("Lema (línea)", hline("#8E959E", 0.8), lambda fr, u: (960 - 200 * eo(u, 2.7, 0.5), 902,
                                                                  960 + 200 * eo(u, 2.7, 0.5), 904))
    return t


# --- 4. Coloured waves along a line → the logo with its tagline (21.0–24.6 s) -----------------------------------------
def wave_line():
    D = 5.0
    t = _p("ondas", "Logo: ondas de colores que se vuelven línea", "Logo: colour waves that settle into a line",
           13903, D, ["ondas", "colores", "línea"], thumb=4.0)
    s = L(t, D)
    AXIS = 540
    s.background([gradient([(0.0, "#F1EEEE"), (0.5, "#E9EAEE"), (1.0, "#93A6C8")], angle=90), no_stroke()])
    s.glow("Fondo (bruma)", "#F7D6C8", 120, 60, 1100, 700, 0.85)
    s.glow("Fondo (bruma 2)", "#F2D2D6", 1880, 120, 900, 600, 0.6)
    s.glow("Fondo (luz)", WHITE, 960, 560, 1900, 760, 0.9)
    s.glow("Destello", WHITE, 1150, 520, 1700, 1200, 1.0, op=lambda u: e(u, 0.1, 0.2) * (1 - e(u, 0.45, 0.4)))

    Lx = lambda u: 40 + 120 * e(u, 0.5, 1.7)  # noqa: E731
    Rx = lambda u: 1880 - 120 * e(u, 0.5, 1.7)  # noqa: E731
    A = lambda u: 225 * eo(u, 0.25, 0.75) * (1 - e(u, 1.95, 0.75))  # noqa: E731
    NP = 90

    def wave(x, u, lam, w, ph, a):
        span = Rx(u) - Lx(u)
        env = max(0.0, math.sin(math.pi * min(1.0, max(0.0, (x - Lx(u)) / span)))) ** 0.9
        return AXIS - A(u) * a * env * math.sin(2 * math.pi * x / lam - w * u + ph)

    def ribbon(lam, w, ph, a):
        def f(u):
            xs = [Lx(u) + (Rx(u) - Lx(u)) * i / (NP - 1) for i in range(NP)]
            return [(x, wave(x, u, lam, w, ph, a)) for x in xs] + [(Rx(u), AXIS), (Lx(u), AXIS)]
        return f

    def strand(lam, w, ph, a):
        def f(u):
            xs = [Lx(u) - 40 + (Rx(u) - Lx(u) + 80) * i / (NP - 1) for i in range(NP)]
            return [(x, wave(x, u, lam, w, ph, a)) for x in xs]
        f.closed = False
        return f
    box = (0, 200, 1920, 880)
    # The soft shadow under the waves.
    sh = s.obj("Sombra", radial("#3E4454", 1.0),
               lambda fr, u: (960, 800, (Rx(u) - Lx(u)) * 0.85, 50 + 24 * A(u) / 225, 0,
                              e(u, 0.3, 0.4) * (0.4 + 0.6 * A(u) / 225) * (1 - e(u, 2.4, 0.5))), kind="ellipse")
    s.fx(sh, "builtin.effects.gaussian_blur", u_blurRadius=12.0)
    for name, colour, args in (("Onda verde", "#A6C35A", (1650, 2.1, 2.3, 0.85)),
                               ("Onda amarilla", "#F5BE3B", (1250, -2.4, 0.4, 0.85)),
                               ("Onda naranja", "#EB9446", (860, 3.4, 1.2, 1.0))):
        c = s.morphing(name, solid(colour), box, ribbon(*args))
        c["opacity"] = keys([(u, round(e(u, 0.15, 0.2) * 0.96, 4), "linear") for u, fr in s.each()])
    for i, (colour, args) in enumerate((("#E9B14A", (1100, 2.8, 2.0, 1.25)), ("#E8963C", (760, -3.0, 0.3, 1.15)),
                                        ("#B5CE74", (1400, 2.2, 4.0, 0.9)))):
        c = s.morphing(f"Hebra {i + 1}", stroke_only(colour, 3, "round"), box, strand(*args))
        c["opacity"] = keys([(u, round(e(u, 0.45, 0.3) * 0.85 * (1 - e(u, 2.2, 0.3)), 4), "linear")
                             for u, fr in s.each()])

    # When the waves flatten: two thin lines that pull back to the right and fade.
    def flat_line(dy, colour, name):
        def g(u):
            x0 = Lx(u) + (1250 - Lx(u)) * e(u, 2.55, 0.5)
            x1 = Rx(u) - (Rx(u) - 1620) * e(u, 2.55, 0.5)
            return x0, AXIS + dy - 4 * (1 - e(u, 2.4, 0.5)), x1, AXIS + dy + 4 * (1 - e(u, 2.4, 0.5)) + 1.5
        s.rect(name, solid(colour), lambda fr, u: g(u), op=lambda fr, u: e(u, 1.95, 0.25) * (1 - e(u, 2.9, 0.25)))
    flat_line(-3, "#F5BE3B", "Línea amarilla")
    flat_line(3, "#A6C35A", "Línea verde")

    # The logo: the mark pops where the reference's leaf is, the brand name unrolls left to right.
    def pop_(u, at, n=0.3, over=0.14):
        q = (u - at) / n
        if q <= 0:
            return 0.0
        if q >= 1.6:
            return 1.0
        return eo(u, at, n) * (1 + over * q) if q <= 1 else 1 + over * (1.6 - q) / 0.6
    s.logo(lambda fr, u: (586, 506, 190 * pop_(u, 2.2), 1.0 if u >= 2.2 else 0.0))
    word = (690, 444, 1450, 568)
    s.say("Your Brand", word, M, 600, "#2E2E2E", "Marca",
          reveal=lambda fr: (680, 380, 680 + 800 * e(fr / FPS, 2.25, 0.6), 640))
    tag = (850, 630, 1070, 664)
    s.say(TAGLINE, tag, BEBAS, 400, "#2E2E2E", "Lema",
          geom=lambda fr, u: (0, 10 * (1 - e(u, 2.35, 0.5)), 1, -7 * (1 - e(u, 2.35, 0.55)), e(u, 2.3, 0.3)))
    s.rect("Lema (línea)", hline("#7C8597", 0.7), lambda fr, u: (960 - 280 * eo(u, 2.7, 0.5), 700,
                                                                  960 + 280 * eo(u, 2.7, 0.5), 702))
    refl = s.say("Your Brand", (690, 770, 1450, 830), M, 600, "#59607A", "Marca (reflejo)", editable=False,
                 geom=lambda fr, u: (0, 0, 1, 0, 0.45 * e(u, 2.6, 0.5)))
    s.fx(refl, "builtin.effects.gaussian_blur", u_blurRadius=10.0)
    return t


def _laid_out(fn):
    def build():
        return art_except(fn())
    build.__name__ = fn.__name__
    return build


TEMPLATES = [_laid_out(f) for f in (pie_target, sphere_disc, slat_square, wave_line)]
