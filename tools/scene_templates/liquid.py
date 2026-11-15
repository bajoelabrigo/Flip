"""Cartoon / liquid motion helpers for Stock templates (0.32 engine). See docs/plan-youtube-pack-2.md.

Native pieces instead of outlines drawn anew every frame:

- `brush`: a stroke that draws itself along a path (Trim Paths keys), thin at its tail and with a round head
  (Taper + round caps, 0.32), wobbling a little (Wiggle Paths). One small outline, a handful of keys.
- `rays`: short tapered strokes that shoot out from a point (a click, a sparkle), one shape, trimmed per contour.
- `splash`: drops that fly out, stretch along their speed and shrink away (path keys every frame with the
  0.32 smooth morph, so the shape stays round between keys).
- `smooth_path`: points → a smooth closed or open SVG path (Catmull-Rom → cubic Béziers) in a 0..100 box.

Everything is in screen px of the 1920×1080 design; the clips carry layoutRole "art" so a Short scales them (and
since 0.32 the fit scales stroke widths and wiggles too).
"""

from __future__ import annotations

import math
import random

from scene import keys
from templates_tit_c import FPS

EMPTY = "M 0 0 L 0.01 0 L 0.01 0.01 Z"


# ==== paths ========================================================================================================

def _n(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def smooth_path(contours, box):
    """contours: [(points, closed)] in screen px → SVG on the 0..100 box (x0, y0, w, h), Catmull-Rom curves."""
    x0, y0, w, h = box
    out = []
    for pts, closed in contours:
        p = [((x - x0) / w * 100, (y - y0) / h * 100) for x, y in pts]
        n = len(p)
        if n < 2:
            continue
        seg = [f"M {_n(p[0][0])} {_n(p[0][1])}"]
        last = n if closed else n - 1
        for i in range(last):
            a, b = p[i], p[(i + 1) % n]
            pa = p[(i - 1) % n] if closed else p[max(0, i - 1)]
            nb = p[(i + 2) % n] if closed else p[min(n - 1, i + 2)]
            c1 = (a[0] + (b[0] - pa[0]) / 6, a[1] + (b[1] - pa[1]) / 6)
            c2 = (b[0] - (nb[0] - a[0]) / 6, b[1] - (nb[1] - a[1]) / 6)
            seg.append(f"C {_n(c1[0])} {_n(c1[1])} {_n(c2[0])} {_n(c2[1])} {_n(b[0])} {_n(b[1])}")
        if closed:
            seg.append("Z")
        out.append(" ".join(seg))
    return " ".join(out)


def bounds(pts_lists, pad=2.0, minimum=4.0):
    xs = [x for pts in pts_lists for x, _ in pts]
    ys = [y for pts in pts_lists for _, y in pts]
    x0, x1, y0, y1 = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    if x1 - x0 < minimum:
        x0, x1 = (x0 + x1) / 2 - minimum / 2, (x0 + x1) / 2 + minimum / 2
    if y1 - y0 < minimum:
        y0, y1 = (y0 + y1) / 2 - minimum / 2, (y0 + y1) / 2 + minimum / 2
    return x0, y0, x1 - x0, y1 - y0


def _stroke(colour, width, profile):
    """A centred stroke whose width follows `profile`: head (thin tail → round head), lens (pointed both ends,
    fuller towards the head), tail (round start → thin end), flat."""
    taper = {"head": (85.0, 0.0, 18.0, 70.0), "lens": (55.0, 0.0, 30.0, 35.0), "tail": (18.0, 70.0, 85.0, 0.0),
             "flat": (0.0, 100.0, 0.0, 100.0), "spike": (50.0, 0.0, 50.0, 0.0)}[profile]
    layer = {"id": "stroke", "kind": "stroke", "enabled": True, "width": round(width, 2), "strokeAlign": "center",
             "cap": "round", "join": "round", "opacity": 1.0,
             "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}
    if profile != "flat":
        layer.update(taperStartLength=taper[0], taperStartWidth=taper[1], taperEndLength=taper[2],
                     taperEndWidth=taper[3], taperEase=60.0)
    return [{"id": "fill", "kind": "fill", "enabled": False, "paint": {"kind": "solid", "color": "#00000000"}}, layer]


def still(clip):
    """Tracks whose keys all hold one value become a single key (a piece that does not move)."""
    for key in ("x", "y", "width", "height", "rotation", "opacity"):
        kf = clip.get(key, {}).get("keyframes") if isinstance(clip.get(key), dict) else None
        if kf and len(kf) > 1 and all(abs(k["value"] - kf[0]["value"]) < 1e-6 for k in kf):
            clip[key] = {"keyframes": [{"timeUs": 0, "value": kf[0]["value"]}]}
    return clip


def _shape(s, name, layers, box, path):
    x0, y0, w, h = box
    clip = s.obj(name, layers, lambda fr, u: (x0 + w / 2, y0 + h / 2, w, h, 0, 1), path=path, base=(w, h))
    clip["layoutRole"] = "art"
    return still(clip)


# ==== brush: a stroke that draws itself ==============================================================================

def brush(s, name, colour, pts, at, n, width, lag=0.45, profile="head", wiggle=0.1, seed=1, ease="out",
          hold=None):
    """A brush stroke along pts (screen px, open): its head runs 0→1 over n frames from `at`, its tail follows
    `lag`·n frames later (hold = frames the whole stroke stays before the tail goes; then lag is ignored)."""
    box = bounds([pts], pad=0.0)
    clip = _shape(s, name, _stroke(colour, width, profile), box, smooth_path([(pts, False)], box))
    st = clip["shapeStyle"]
    tail_at = at + n + hold if hold is not None else at + n * lag
    st["trimEnd"] = 0.0
    kf = st.setdefault("keyframes", {})
    kf["trimEnd"] = keys([(max(0.0, at / FPS), 0.0, ease), ((at + n) / FPS, 100.0)])
    kf["trimStart"] = keys([(max(0.0, tail_at / FPS), 0.0, "smooth"),
                            ((tail_at + n) / FPS, 100.0)])
    if wiggle:
        st.update(wiggleSize=round(width * wiggle, 2), wiggleDetail=round(max(12.0, width * 1.6), 1),
                  wiggleSpeed=1.6, wiggleSeed=float(seed))
    return clip


def rays(s, name, colour, cx, cy, at, n, count, r0, r1, width, a0=0.0, spread=360.0, profile="spike", lag=0.5):
    """count strokes from r0 to r1 round (cx, cy), drawn out and wiped away along themselves."""
    lines = []
    for i in range(count):
        a = math.radians(a0 + spread * i / count)
        lines.append([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))])
    box = bounds(lines, pad=0.0)
    path = " ".join(smooth_path([(p, False)], box) for p in lines)
    clip = _shape(s, name, _stroke(colour, width, profile), box, path)
    st = clip["shapeStyle"]
    st["trimEnd"] = 0.0
    kf = st.setdefault("keyframes", {})
    kf["trimEnd"] = keys([(max(0.0, at / FPS), 0.0, "out"), ((at + n * 0.7) / FPS, 100.0)])
    kf["trimStart"] = keys([(max(0.0, (at + n * lag) / FPS), 0.0, "smooth"), ((at + n) / FPS, 100.0)])
    return clip


# ==== splash: drops flying out ======================================================================================

def _drop(cx, cy, r, vx, vy, stretch):
    """A drop of radius r at (cx, cy) moving along (vx, vy): round in front, drawn out behind by `stretch`."""
    sp = math.hypot(vx, vy) or 1.0
    dx, dy = vx / sp, vy / sp
    pts = []
    for i in range(10):
        t = 2 * math.pi * i / 10
        along, across = math.cos(t), math.sin(t)
        if along < 0:
            along *= 1 + stretch
            across *= 1 - 0.25 * min(1.0, stretch)
        x, y = along * r, across * r
        pts.append((cx + x * dx - y * dy, cy + x * dy + y * dx))
    return pts


def splash(s, name, colour, cx, cy, at, n, count, r0, r1, size, seed=3, spread=360.0, a0=0.0, ry=1.0, every=1,
           gravity=0.0, goo=0.7):
    """count drops thrown out from (cx, cy) between r0 and r1 (px), size px radius, decelerating and shrinking
    away over n frames; ry squashes the throw vertically, gravity (px) pulls them down by the end."""
    rnd = random.Random(seed)
    drops = []
    for i in range(count):
        a = math.radians(a0 + spread * (i + rnd.uniform(-0.45, 0.45)) / count)
        drops.append((a, rnd.uniform(0.3, 1.0), size * rnd.uniform(0.45, 1.35), rnd.uniform(0.0, 0.35)))
    frames = list(range(int(math.floor(at)), int(math.ceil(at + n)) + 1, every))
    if frames[-1] < at + n:
        frames.append(int(math.ceil(at + n)))

    def at_frame(fr):
        out = []
        for a, far, sz, late in drops:
            q = min(1.0, max(0.0, (fr - at) / n - late) / (1 - late))
            e = 1 - (1 - q) ** 3
            v = 3 * (1 - q) ** 2  # d e / d q
            d = r0 + (r1 - r0) * far * e
            x = cx + d * math.cos(a)
            y = cy + d * math.sin(a) * ry + gravity * q * q
            vx, vy = math.cos(a), math.sin(a) * ry + 2 * gravity * q / max(1.0, (r1 - r0) * far)
            r = max(0.4, sz * (1 - q) ** 0.7 * (0.35 if q <= 0 else 1.0))
            out.append(_drop(x, y, r, vx, vy, min(1.2, 0.9 * v)))
        return out

    shapes = [(fr, at_frame(fr)) for fr in frames]
    box = bounds([p for _, ps in shapes for p in ps])
    paths = [EMPTY] + [smooth_path([(p, True) for p in ps], box) for _, ps in shapes]
    clip = _shape(s, name, [{"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
                             "paint": {"kind": "solid", "color": "#ff" + colour.lstrip("#").lower()}}],
                  box, paths[1])
    st = clip["shapeStyle"]
    st["pathShapes"] = paths
    st["smoothMorph"] = 1.0
    kf = [(0.0, 0, "hold")] if frames[0] > 0 else []
    kf += [(fr / FPS, i + 1, "linear") for i, (fr, _) in enumerate(shapes)]
    kf[-1] = (kf[-1][0], kf[-1][1], "hold")
    kf.append((kf[-1][0] + 1 / FPS, 0, "hold"))
    st.setdefault("keyframes", {})["path"] = keys(kf)
    st["customPath"] = EMPTY if frames[0] > 0 else paths[1]
    if goo:
        # Drops still close together melt into one another, as liquid does (the gooey trick), flat colour.
        s.fx(clip, "liquid.gooey", goo=round(min(16.0, size * goo), 1), threshold=0.5, shine=0.0)
    return clip


# ==== outlines that change shape ======================================================================================

def morph_keys(s, name, colour, frames_fn, every=1, evenodd=False, alpha=1.0, smooth=True):
    """A shape whose outline is frames_fn(fr) → [points (closed, screen px)] (empty = hidden), keyed every
    `every` frames and blended between keys (smooth morph): blobs that grow, wobble and split."""
    each = [(u, fr) for u, fr in s.each()]
    picked = [(u, fr) for i, (u, fr) in enumerate(each) if i % every == 0 or i == len(each) - 1]
    shapes = [(u, [p for p in frames_fn(fr) if len(p) > 2]) for u, fr in picked]
    pts = [p for _, ps in shapes for p in ps]
    if not pts:
        return None
    box = bounds(pts)
    paths, kf = [EMPTY], []
    last_empty = None
    for u, ps in shapes:
        svg = (smooth_path([(p, True) for p in ps], box) if smooth else
               " ".join("M " + " L ".join(f"{_n((x - box[0]) / box[2] * 100)} {_n((y - box[1]) / box[3] * 100)}"
                                          for x, y in p) + " Z" for p in ps)) if ps else ""
        if ps and kf and kf[-1][1] and paths[kf[-1][1]] == svg:
            kf.append((u, kf[-1][1], "linear"))  # the same outline again: no new entry
            last_empty = False
            continue
        empty = not ps
        if empty:
            if last_empty is not True:
                if kf:
                    kf[-1] = (kf[-1][0], kf[-1][1], "hold")
                kf.append((u, 0, "hold"))
        else:
            paths.append(svg)
            if last_empty is True and kf:
                kf[-1] = (kf[-1][0], 0, "hold")
            kf.append((u, len(paths) - 1, "linear"))
        last_empty = empty
    fill = {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1.0,
            "paint": {"kind": "solid", "color": "#" + format(round(alpha * 255), "02x") + colour.lstrip("#").lower()}}
    clip = _shape(s, name, [fill], box, paths[1] if len(paths) > 1 else EMPTY)
    st = clip["shapeStyle"]
    st["customPath"] = paths[kf[0][1]] if kf[0][1] else EMPTY
    st["pathShapes"] = paths
    st["customEvenOdd"] = evenodd
    st["smoothMorph"] = 1.0
    st.setdefault("keyframes", {})["path"] = keys(kf)
    return clip


# ==== drips (0.32 Drip operator) =====================================================================================

def _track_at(clip, key, i, default):
    kf = (clip.get(key) or {}).get("keyframes") if isinstance(clip.get(key), dict) else None
    if not kf:
        return default
    return kf[min(i, len(kf) - 1)]["value"]


def drip(clip, at, length, width, count, seed=1, fall=None, goo=True):
    """Thick liquid that runs down from the bottom of a shape clip as it comes in (the 0.32 Drip operator): fingers
    grow to `length` px in ~7 frames from frame `at`, sag back, their bulbs let go and fall (`fall` px) while they
    shrink away. goo adds the Liquid effect so the necks melt into the body."""
    from scene import effect
    st = clip["shapeStyle"]
    fall = length * 0.9 if fall is None else fall
    a = max(0.0, at)
    st.update(dripLength=0.0, dripWidth=round(width, 2), dripCount=float(count), dripSeed=float(seed))
    kf = st.setdefault("keyframes", {})
    kf["dripLength"] = keys([(a / FPS, 0.0, "out"), ((a + 7) / FPS, length, "smooth"),
                             ((a + 16) / FPS, length * 0.7, "smooth"), ((a + 26) / FPS, length * 0.2)])
    kf["dripFall"] = keys([((a + 9) / FPS, 0.0, "in"), ((a + 24) / FPS, fall)])
    kf["dripWidth"] = keys([((a + 17) / FPS, width, "in"), ((a + 27) / FPS, 0.0)])
    if goo:
        clip.setdefault("effects", []).append(effect("liquid.gooey", goo=round(min(16.0, width * 0.5), 1),
                                                     threshold=0.5, shine=0.0))
    return clip


def liquefy(t, names, seed=1):
    """Every shape clip of template t named in `names` drips as it comes in: the frame it first shows (box over 4 px,
    opacity over 5 %) starts the drip; length, width and count follow its size."""
    for track in t.tracks:
        for clip in track.clips:
            if clip.get("type") != "shape" or clip.get("name") not in names:
                continue
            n = len((clip.get("width") or {}).get("keyframes") or [1])
            appear, w_max, h_max = None, 0.0, 0.0
            for i in range(n):
                w, h = _track_at(clip, "width", i, 0.0), _track_at(clip, "height", i, 0.0)
                op = _track_at(clip, "opacity", i, 1.0)
                if op > 0.05 and w > 4 and h > 4:
                    if appear is None:
                        appear = i
                    w_max, h_max = max(w_max, w), max(h_max, h)
            if appear is None:
                continue
            kfw = (clip.get("width") or {}).get("keyframes") or [{"timeUs": 0}]
            at = kfw[min(appear, len(kfw) - 1)]["timeUs"] / 1e6 * FPS
            side = min(w_max, h_max)
            width = max(10.0, min(34.0, side * 0.09))
            length = max(40.0, min(170.0, h_max * 0.5))
            count = max(3, min(8, round(w_max / 110)))
            seed += 1
            drip(clip, at, length, width, count, seed=seed)
