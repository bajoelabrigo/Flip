"""Cartoon VFX helpers for Stock templates (the 0.32 VFX engine, docs/plan-vfx.md A–E and H).

Small, dict-level helpers over a shape clip's JSON (the format `scene.py` writes), so a pack module can write:

    st = clip["shapeStyle"]
    smooth_morph(st, corners=40, from_centre=True)        # A, D: tips stay sharp, new holes open from their centre
    posterize(clip, 12)                                   # B: the whole clip drawn 12 times a second («on twos»)
    st["layers"].append(inner_tone("#a8a8a8", dy=-14))   # C: the grey belly of smoke, hard-edged
    break_apart(st, [(0.0, 0), (0.6, 100)], size=36)      # D: holes open inside until the shape is gone
    stepped_wiggle(st, size=6, detail=18, rate=12)       # E: a fresh wobble every other frame (boil)
    jagged_zigzag(st, size=14, ridges=9, jitter=80, rate=24)  # E: electricity, redrawn every frame
    group["merge"] = MERGE["subtract"]                   # H: live Merge Paths between the parts of a group

`smooth_path` is the corner-aware version of liquid.smooth_path: points → SVG on the 0..100 box, Catmull-Rom curves
except at the corners (the indices given, or every turn sharper than `corner_angle` degrees), which stay pointed.
The engine finds those corners again (`morphCorners`) and keeps them while morphing between path keys.

Everything needs the app 0.32 (or the version that ships the VFX engine): publish with that `minAppVersion`.
"""

from __future__ import annotations

import math

from scene import keys

MERGE = {"off": 0, "add": 1, "subtract": 2, "intersect": 3, "exclude": 4}


def _n(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def turn_corners(pts, closed, angle):
    """Indices of the points where the polyline turns by more than `angle` degrees (ends of an open one excluded)."""
    out = []
    n = len(pts)
    for i in range(n):
        if not closed and (i == 0 or i == n - 1):
            continue
        ax, ay = pts[(i - 1) % n]
        bx, by = pts[i]
        cx, cy = pts[(i + 1) % n]
        ux, uy, vx, vy = bx - ax, by - ay, cx - bx, cy - by
        lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
        if lu < 1e-9 or lv < 1e-9:
            continue
        cos = max(-1.0, min(1.0, (ux * vx + uy * vy) / (lu * lv)))
        if math.degrees(math.acos(cos)) > angle:
            out.append(i)
    return out


def smooth_path(contours, box, corner_angle=None):
    """contours: [(points, closed)] or [(points, closed, corner_indices)] in screen px → SVG on the 0..100 box
    (x0, y0, w, h). Catmull-Rom curves; at a corner the curve arrives and leaves straight at the point (no handle on
    that side), so it stays sharp. With `corner_angle`, every turn sharper than that is a corner too."""
    x0, y0, w, h = box
    out = []
    for contour in contours:
        pts, closed = contour[0], contour[1]
        corners = set(contour[2]) if len(contour) > 2 and contour[2] else set()
        if corner_angle:
            corners |= set(turn_corners(pts, closed, corner_angle))
        p = [((x - x0) / w * 100, (y - y0) / h * 100) for x, y in pts]
        n = len(p)
        if n < 2:
            continue
        seg = [f"M {_n(p[0][0])} {_n(p[0][1])}"]
        last = n if closed else n - 1
        for i in range(last):
            j = (i + 1) % n
            a, b = p[i], p[j]
            pa = p[(i - 1) % n] if closed else p[max(0, i - 1)]
            nb = p[(i + 2) % n] if closed else p[min(n - 1, i + 2)]
            c1 = a if i in corners else (a[0] + (b[0] - pa[0]) / 6, a[1] + (b[1] - pa[1]) / 6)
            c2 = b if j in corners else (b[0] - (nb[0] - a[0]) / 6, b[1] - (nb[1] - a[1]) / 6)
            if i in corners and j in corners:
                seg.append(f"L {_n(b[0])} {_n(b[1])}")
            else:
                seg.append(f"C {_n(c1[0])} {_n(c1[1])} {_n(c2[0])} {_n(c2[1])} {_n(b[0])} {_n(b[1])}")
        if closed:
            seg.append("Z")
        out.append(" ".join(seg))
    return " ".join(out)


# ==== A, D: the smooth morph's options ===============================================================================

def smooth_morph(style, corners=40.0, from_centre=False):
    """Path keys blend smoothly (smoothMorph); turns sharper than `corners` degrees stay pointed and pair up between
    keys (morphCorners, 0 = round everything); a contour only one key has grows from its own centre (from_centre)."""
    style["smoothMorph"] = 1.0
    if corners:
        style["morphCorners"] = float(corners)
    if from_centre:
        style["morphFromCentre"] = 1.0
    return style


# ==== B: Posterize Time ==============================================================================================

def posterize(clip, fps=12.0):
    """The whole clip (transform, keys, morph, wiggles, effects) drawn `fps` times a second and held in between."""
    clip["posterizeFps"] = float(fps)
    return clip


# ==== C: inner tone ==================================================================================================

def inner_tone(colour, dx=0.0, dy=-12.0, scale=100.0, rotation=0.0, invert=False, lid="tone", alpha=1.0):
    """A fill layer drawn inside the outline only, where a copy moved by (dx, dy) px (scaled %, turned °) does not
    reach: dy < 0 leaves a band along the bottom (smoke's belly, a liquid's dark side). invert paints where the copy
    reaches instead. Hard-edged; it follows the outline as it morphs. Put it after (above) the main fill."""
    layer = {"id": lid, "kind": "fill", "enabled": True, "opacity": 1.0, "innerTone": True,
             "offsetX": float(dx), "offsetY": float(dy),
             "paint": {"kind": "solid", "color": "#" + format(round(alpha * 255), "02x") + colour.lstrip("#").lower()}}
    if abs(scale - 100.0) > 1e-9:
        layer["toneScale"] = float(scale)
    if rotation:
        layer["toneRotation"] = float(rotation)
    if invert:
        layer["toneInvert"] = True
    return layer


# ==== D: break apart =================================================================================================

def break_apart(style, amount, size=40.0, seed=0, angle=0.0, stretch=1.0):
    """Holes open from their own centres inside the shape and grow until nothing is left. `amount`: a number (%), or
    [(t seconds, %[, ease])] keys (clip-relative). stretch > 1: strips that long along `angle` degrees."""
    style.update(erodeSize=float(size), erodeSeed=float(seed), erodeAngle=float(angle), erodeStretch=float(stretch))
    if isinstance(amount, (int, float)):
        style["erodeAmount"] = float(amount)
    else:
        style["erodeAmount"] = float(amount[0][1])
        style.setdefault("keyframes", {})["erodeAmount"] = keys(amount)
    return style


# ==== E: on twos =====================================================================================================

def stepped_wiggle(style, size=6.0, detail=20.0, rate=12.0, seed=1):
    """Wiggle Paths that draws a fresh random wobble `rate` times a second (12 = on twos at 24 fps), held between."""
    style.update(wiggleSize=float(size), wiggleDetail=float(detail), wiggleStepRate=float(rate),
                 wiggleSeed=float(seed))
    return style


def jagged_zigzag(style, size=12.0, ridges=10, jitter=80.0, rate=24.0, seed=1, smooth=False):
    """Zig Zag with uneven points (each its own size and a nudge along the path, `jitter` %), redrawn `rate` times a
    second (0 = still): a bolt of electricity."""
    style.update(zigzagSize=float(size), zigzagRidges=float(ridges), zigzagJitter=float(jitter),
                 zigzagStepRate=float(rate), zigzagSeed=float(seed), zigzagSmooth=1.0 if smooth else 0.0)
    return style
