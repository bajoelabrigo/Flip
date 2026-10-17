"""Path building blocks for the Stock shapes (tools/shapes_stock).

A *path* is a list of closed subpaths. A subpath is ``[start, seg, seg, ...]`` where ``start`` is
``(x, y)`` and each segment is ``("L", p)``, ``("Q", c, p)`` or ``("C", c1, c2, p)``. Every subpath
is closed (the serializer adds the closing ``Z``). Shapes are authored in any coordinate space;
``normalize`` scales them to the 0..100 box the app expects and gives the aspect (w / h).

Only absolute ``M L Q C Z`` reach the SVG string; arcs are turned into cubics here.
"""

from __future__ import annotations

import math
import random
from typing import Iterable, List, Sequence, Tuple

Point = Tuple[float, float]
K = 0.5522847498  # cubic handle length for a quarter circle


# --------------------------------------------------------------------------------------------
# Primitives

def poly(points: Sequence[Point]) -> list:
    pts = list(points)
    return [pts[0]] + [("L", p) for p in pts[1:]]


def rect(x: float, y: float, w: float, h: float) -> list:
    return poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])


def ellipse(cx: float, cy: float, rx: float, ry: float | None = None) -> list:
    ry = rx if ry is None else ry
    return [(cx + rx, cy)] + arc_segments(cx, cy, rx, ry, 0, 360)


def circle(cx: float, cy: float, r: float) -> list:
    return ellipse(cx, cy, r, r)


def arc_segments(cx, cy, rx, ry, a0, a1) -> list:
    """Cubic segments of an elliptical arc from angle a0 to a1 (degrees, y down, clockwise
    on screen when a1 > a0). The caller must already be at the arc's start point."""
    segs = []
    total = a1 - a0
    n = max(1, int(math.ceil(abs(total) / 90.0 - 1e-9)))
    step = math.radians(total / n)
    t = math.radians(a0)
    k = 4.0 / 3.0 * math.tan(step / 4.0)
    for _ in range(n):
        t2 = t + step
        p0 = (cx + rx * math.cos(t), cy + ry * math.sin(t))
        p3 = (cx + rx * math.cos(t2), cy + ry * math.sin(t2))
        c1 = (p0[0] - k * rx * math.sin(t), p0[1] + k * ry * math.cos(t))
        c2 = (p3[0] + k * rx * math.sin(t2), p3[1] - k * ry * math.cos(t2))
        segs.append(("C", c1, c2, p3))
        t = t2
    return segs


def arc_point(cx, cy, rx, ry, a) -> Point:
    return (cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)))


def ring_arc(cx, cy, r_out, r_in, a0, a1, round_caps=False) -> list:
    """A thick arc (annulus sector) as one subpath."""
    sp = [arc_point(cx, cy, r_out, r_out, a0)]
    sp += arc_segments(cx, cy, r_out, r_out, a0, a1)
    if round_caps:
        m = (r_out + r_in) / 2
        cr = (r_out - r_in) / 2
        ex, ey = arc_point(cx, cy, m, m, a1)
        sp += arc_segments(ex, ey, cr, cr, a1, a1 + 180)
    else:
        sp.append(("L", arc_point(cx, cy, r_in, r_in, a1)))
    sp += arc_segments(cx, cy, r_in, r_in, a1, a0)
    if round_caps:
        m = (r_out + r_in) / 2
        cr = (r_out - r_in) / 2
        sx, sy = arc_point(cx, cy, m, m, a0)
        sp += arc_segments(sx, sy, cr, cr, a0 + 180, a0 + 360)
    return sp


def regular(n: int, cx: float, cy: float, r: float, rot: float = -90.0, ry: float | None = None) -> List[Point]:
    ry = r if ry is None else ry
    return [(cx + r * math.cos(math.radians(rot + 360.0 * i / n)),
             cy + ry * math.sin(math.radians(rot + 360.0 * i / n))) for i in range(n)]


def star_points(n: int, cx: float, cy: float, r_out: float, r_in: float, rot: float = -90.0) -> List[Point]:
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + 180.0 * i / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def rounded_poly(points: Sequence[Point], radius: float | Sequence[float]) -> list:
    """Polygon with each corner rounded by a quadratic through the corner (radius per corner or one)."""
    pts = list(points)
    n = len(pts)
    radii = [radius] * n if isinstance(radius, (int, float)) else list(radius)
    entries, exits = [], []
    for i in range(n):
        p, a, b = pts[i], pts[i - 1], pts[(i + 1) % n]
        la = math.dist(p, a)
        lb = math.dist(p, b)
        r = min(radii[i], la * 0.49, lb * 0.49)
        entries.append(lerp(p, a, r / la) if la else p)
        exits.append(lerp(p, b, r / lb) if lb else p)
    sp = [exits[0]]
    for i in range(1, n + 1):
        j = i % n
        sp.append(("L", entries[j]))
        sp.append(("Q", pts[j], exits[j]))
    return sp


def smooth(points: Sequence[Point], tension: float = 1.0) -> list:
    """Closed Catmull-Rom curve through the points (tangent = (next - prev) / 6 * tension)."""
    pts = list(points)
    n = len(pts)
    sp = [pts[0]]
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * tension, p1[1] + (p2[1] - p0[1]) / 6 * tension)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * tension, p2[1] - (p3[1] - p1[1]) / 6 * tension)
        sp.append(("C", c1, c2, p2))
    return sp


def smooth_open_segs(points: Sequence[Point]) -> list:
    """Cubic segments of an open Catmull-Rom curve through the points (the caller is at points[0])."""
    pts = list(points)
    n = len(pts)
    segs = []
    for i in range(n - 1):
        p0, p1, p2 = pts[max(0, i - 1)], pts[i], pts[i + 1]
        p3 = pts[min(n - 1, i + 2)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        segs.append(("C", c1, c2, p2))
    return segs


def lerp(a: Point, b: Point, t: float) -> Point:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def wobble(points: Sequence[Point], amount: float, seed: int) -> List[Point]:
    rnd = random.Random(seed)
    return [(x + rnd.uniform(-amount, amount), y + rnd.uniform(-amount, amount)) for x, y in points]


def resample(points: Sequence[Point], step: float, closed: bool = True) -> List[Point]:
    """Points every `step` along a polyline (keeps the corners)."""
    pts = list(points) + ([points[0]] if closed else [])
    out = []
    for a, b in zip(pts, pts[1:]):
        d = math.dist(a, b)
        n = max(1, int(d / step))
        for i in range(n):
            out.append(lerp(a, b, i / n))
    if not closed:
        out.append(pts[-1])
    return out


def torn(points: Sequence[Point], step: float, depth: float, seed: int) -> List[Point]:
    """A polygon outline with a ragged, torn-paper edge (jitter perpendicular-ish)."""
    rnd = random.Random(seed)
    return [(x + rnd.uniform(-depth, depth) * 0.5, y + rnd.uniform(-depth, depth)) for x, y in resample(points, step)]


def radial(n: int, cx: float, cy: float, f, rot: float = -90.0) -> List[Point]:
    """Points around a centre with radius f(angle_degrees)."""
    out = []
    for i in range(n):
        a = rot + 360.0 * i / n
        r = f(a)
        out.append((cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))))
    return out


def stroke_polyline(points: Sequence[Point], width: float | Sequence[float], cap: str = "round") -> list:
    """Outline of a thick open polyline (one subpath). Width may vary per point (taper)."""
    pts = list(points)
    n = len(pts)
    widths = [width] * n if isinstance(width, (int, float)) else list(width)
    left, right = [], []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / L, dx / L
        h = widths[i] / 2
        left.append((p[0] + nx * h, p[1] + ny * h))
        right.append((p[0] - nx * h, p[1] - ny * h))
    sp = [left[0]] + [("L", q) for q in left[1:]]
    if cap == "round" and widths[-1] > 0.01:
        e = pts[-1]
        h = widths[-1] / 2
        ang = math.degrees(math.atan2(left[-1][1] - e[1], left[-1][0] - e[0]))
        sp += arc_segments(e[0], e[1], h, h, ang, ang - 180)
    sp += [("L", q) for q in reversed(right)]
    if cap == "round" and widths[0] > 0.01:
        s = pts[0]
        h = widths[0] / 2
        ang = math.degrees(math.atan2(right[0][1] - s[1], right[0][0] - s[0]))
        sp += arc_segments(s[0], s[1], h, h, ang, ang - 180)
    return sp


def heart_sub(cx: float, cy: float, w: float, h: float, fat: float = 1.0) -> list:
    """Classic heart in a w×h box centred at (cx, cy): two lobes and a point at the bottom."""
    x0, y0 = cx - w / 2, cy - h / 2
    X = lambda f: x0 + f * w  # noqa: E731
    Y = lambda f: y0 + f * h  # noqa: E731
    k = fat
    return [
        (X(0.5), Y(0.28)),
        ("C", (X(0.5), Y(0.12)), (X(0.62), Y(0.0)), (X(0.76), Y(0.0))),
        ("C", (X(0.93), Y(0.0)), (X(1.0), Y(0.14)), (X(1.0), Y(0.3))),
        ("C", (X(1.0), Y(0.56 * k)), (X(0.7), Y(0.78)), (X(0.5), Y(1.0))),
        ("C", (X(0.3), Y(0.78)), (X(0.0), Y(0.56 * k)), (X(0.0), Y(0.3))),
        ("C", (X(0.0), Y(0.14)), (X(0.07), Y(0.0)), (X(0.24), Y(0.0))),
        ("C", (X(0.38), Y(0.0)), (X(0.5), Y(0.12)), (X(0.5), Y(0.28))),
    ]


# --------------------------------------------------------------------------------------------
# Transforms

def _map_sub(sp, f):
    out = [f(sp[0])]
    for seg in sp[1:]:
        out.append((seg[0],) + tuple(f(p) for p in seg[1:]))
    return out


def transform(path, f):
    return [_map_sub(sp, f) for sp in path]


def translate(path, dx, dy):
    return transform(path, lambda p: (p[0] + dx, p[1] + dy))


def scale(path, sx, sy=None, cx=0.0, cy=0.0):
    sy = sx if sy is None else sy
    return transform(path, lambda p: (cx + (p[0] - cx) * sx, cy + (p[1] - cy) * sy))


def rotate(path, deg, cx=0.0, cy=0.0):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return transform(path, lambda p: (cx + (p[0] - cx) * c - (p[1] - cy) * s, cy + (p[0] - cx) * s + (p[1] - cy) * c))


def reverse_sub(sp):
    """The same closed subpath walked the other way."""
    start = sp[0]
    segs = list(sp[1:])
    end = segs[-1][-1] if segs else start
    if math.dist(end, start) > 1e-9:
        segs.append(("L", start))
    pts = [start] + [s[-1] for s in segs]
    out = [pts[-1]]
    for i in range(len(segs) - 1, -1, -1):
        s = segs[i]
        prev = pts[i]
        if s[0] == "L":
            out.append(("L", prev))
        elif s[0] == "Q":
            out.append(("Q", s[1], prev))
        else:
            out.append(("C", s[2], s[1], prev))
    return out


# --------------------------------------------------------------------------------------------
# Flattening, normalising, serialising

def flatten_sub(sp, steps: int = 16) -> List[Point]:
    pts = [sp[0]]
    cur = sp[0]
    for seg in sp[1:]:
        if seg[0] == "L":
            pts.append(seg[1])
        elif seg[0] == "Q":
            c, p = seg[1], seg[2]
            for i in range(1, steps + 1):
                t = i / steps
                u = 1 - t
                pts.append((u * u * cur[0] + 2 * u * t * c[0] + t * t * p[0], u * u * cur[1] + 2 * u * t * c[1] + t * t * p[1]))
        else:
            c1, c2, p = seg[1], seg[2], seg[3]
            for i in range(1, steps + 1):
                t = i / steps
                u = 1 - t
                pts.append((u ** 3 * cur[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * p[0],
                            u ** 3 * cur[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * p[1]))
        cur = seg[-1]
    return pts


def signed_area(pts: Sequence[Point]) -> float:
    return 0.5 * sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, list(pts[1:]) + [pts[0]]))


def bbox(path) -> Tuple[float, float, float, float]:
    xs, ys = [], []
    for sp in path:
        for x, y in flatten_sub(sp, 24):
            xs.append(x)
            ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def normalize(path, nonzero: bool = True):
    """Scales the path to fill 0..100 on both axes; returns (path, aspect). For nonzero, every
    subpath is turned to the same direction so overlapping parts add up instead of cancelling."""
    x0, y0, x1, y1 = bbox(path)
    w, h = x1 - x0, y1 - y0
    out = transform(path, lambda p: ((p[0] - x0) / w * 100.0, (p[1] - y0) / h * 100.0))
    if nonzero:
        out = [sp if signed_area(flatten_sub(sp, 8)) >= 0 else reverse_sub(sp) for sp in out]
    return out, w / h


def fmt(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def to_svg(path) -> str:
    parts = []
    for sp in path:
        parts.append(f"M {fmt(sp[0][0])} {fmt(sp[0][1])}")
        for seg in sp[1:]:
            parts.append(seg[0] + " " + " ".join(f"{fmt(p[0])} {fmt(p[1])}" for p in seg[1:]))
        parts.append("Z")
    return " ".join(parts)


def parse_svg(d: str):
    """Parser for the subset we write (absolute M L Q C Z); the validator round-trips through it."""
    toks = d.replace(",", " ").split()
    path, sp, i = [], None, 0
    arity = {"M": 1, "L": 1, "Q": 2, "C": 3}

    def num(j):
        return float(toks[j])

    while i < len(toks):
        c = toks[i]
        i += 1
        if c == "Z":
            if sp is None:
                raise ValueError("Z without M")
            path.append(sp)
            sp = None
            continue
        if c not in arity:
            raise ValueError(f"unsupported command {c!r}")
        pts = []
        for _ in range(arity[c]):
            pts.append((num(i), num(i + 1)))
            i += 2
        if c == "M":
            if sp is not None:
                path.append(sp)
            sp = [pts[0]]
        else:
            if sp is None:
                raise ValueError(f"{c} before M")
            sp.append((c,) + tuple(pts))
    if sp is not None:
        path.append(sp)
    return path


def union(*paths: Iterable) -> list:
    out = []
    for p in paths:
        out.extend(p)
    return out


def torn_edges(points: Sequence[Point], step: float, depth: float, seed: int, edges=None) -> List[Point]:
    """Polygon whose chosen edges (indices; all by default) get a ragged torn edge, jittered
    along each edge's normal so the rip reads on horizontal and vertical sides alike."""
    rnd = random.Random(seed)
    pts = list(points)
    n = len(pts)
    out = []
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        out.append(a)
        if edges is not None and i not in edges:
            continue
        d = math.dist(a, b)
        m = max(2, int(d / step))
        nx, ny = -(b[1] - a[1]) / d, (b[0] - a[0]) / d
        for j in range(1, m):
            t = j / m + rnd.uniform(-0.3, 0.3) / m
            off = rnd.uniform(-depth, depth)
            p = lerp(a, b, t)
            out.append((p[0] + nx * off, p[1] + ny * off))
    return out
