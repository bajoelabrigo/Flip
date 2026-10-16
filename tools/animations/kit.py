"""Shared motion and shape helpers for the third set of stickers (designs3.py onwards)."""

from __future__ import annotations

import math

from lottie import EASE_BACK, EASE_IN_OUT, EASE_OUT, LINEAR, anim, ellipse, fill, group, path, polar, rect, static, stroke, transform

C = 256
IN = ({"x": [0.7], "y": [0]}, {"x": [0.84], "y": [0]})        # ease-in, for exits
FALL = ({"x": [0.5], "y": [0]}, {"x": [0.8], "y": [1]})        # gravity: speeds up into the landing
HOLD = "hold"


def _v(value, dims):
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value, value] + ([100] if dims == 3 else [])


def scale_keys(keys, dims=3):
    """keys: [(frame, percent[, ease])] -> anim on uniform scale (dims 3 = layer, 2 = group)."""
    return anim([(k[0], _v(k[1], dims)) + tuple(k[2:]) for k in keys])


def pop(start=0, length=14, to=100, dims=3):
    """0 -> ~118 % -> 96 % -> 100 %: a pop that settles in one and a half oscillations."""
    a, b, c = round(length * 0.55), round(length * 0.8), length
    return scale_keys([(start, 0, EASE_OUT), (start + a, to * 1.18, EASE_IN_OUT), (start + b, to * 0.96, EASE_IN_OUT),
                       (start + c, to)], dims)


def pop_out(start, length=8, frm=100, dims=3):
    """100 % -> 108 % -> 0: the exit of a one-shot that clears itself."""
    return [(start, frm, EASE_IN_OUT), (start + round(length * 0.35), frm * 1.08, IN), (start + length, 0)]


def breathe(frames, lo=100, hi=106, dims=3, start=0):
    """A seamless scale pulse over the whole loop."""
    mid = start + frames // 2
    return scale_keys([(start, lo, EASE_IN_OUT), (mid, hi, EASE_IN_OUT), (start + frames, lo)], dims)


def bob(frames, x, y, dy=12, phase=0):
    """Seamless up-and-down float around (x, y); phase in frames."""
    return wave(frames, lambda u: [x, y + dy * math.cos(2 * math.pi * (u - phase / frames)), 0])


def wave(frames, fn, samples=16, cycles=1):
    """Samples fn(u), u in [0, 1] (cycles per loop), linearly: a smooth, seamless periodic motion."""
    keys = []
    for k in range(samples * cycles + 1):
        t = frames * k / (samples * cycles)
        keys.append((round(t, 2), fn((k / samples) % 1 if k < samples * cycles else 0), LINEAR))
    return anim(keys)


def wobble(frames, amp, cycles=1, start=0, end=None):
    """Seamless rotation that swings ±amp `cycles` times between start and end (default whole loop)."""
    end = frames if end is None else end
    keys = [(start, 0, EASE_IN_OUT)]
    steps = cycles * 4
    for k in range(1, steps + 1):
        t = start + round((end - start) * k / steps)
        a = [0, amp, 0, -amp][k % 4]
        keys.append((t, a, EASE_IN_OUT))
    if end < frames:
        keys.append((frames, 0))
    return anim(keys)


def swing(frames, amp, cycles, start=0):
    """Damped rotation around 0, ending at rest (frames = length of the swing)."""
    keys = []
    steps = cycles * 2
    for k in range(steps + 1):
        t = start + round(k * frames / steps)
        a = amp * (1 - k / steps) * (1 if k % 2 else -1) if k < steps else 0
        keys.append((t, a, EASE_IN_OUT))
    return anim(keys)


def draw_on(start, length=16, ease=EASE_IN_OUT):
    """Trim end 0 -> 100: a stroke drawn by hand."""
    from lottie import trim
    return trim(anim([(start, 0, ease), (start + length, 100)]))


def draw_on_off(start, length, hold, out=12):
    """Drawn, held, then erased from its start: a loopable doodle."""
    from lottie import trim
    return trim(anim([(start, 0, EASE_IN_OUT), (start + length, 100)]),
                start=anim([(start + length + hold, 0, EASE_IN_OUT), (start + length + hold + out, 100)]))


def bez(points, closed=True, smooth=1.0) -> dict:
    """The bezier dict of a smoothed polyline (for morph keyframes)."""
    return path(points, closed=closed, smooth=smooth)["ks"]["k"]


def morph(frames_points, closed=True, smooth=1.0, ease=EASE_IN_OUT) -> dict:
    """Animated path: [(frame, points)], all with the same vertex count."""
    keys = {"a": 1, "k": []}
    for i, (t, pts) in enumerate(frames_points):
        key = {"t": t, "s": [bez(pts, closed, smooth)]}
        if i < len(frames_points) - 1:
            key["o"] = {"x": ease[0]["x"], "y": ease[0]["y"]}
            key["i"] = {"x": ease[1]["x"], "y": ease[1]["y"]}
        keys["k"].append(key)
    return {"ty": "sh", "ks": keys}


def blob(radius, n=10, jitter=0.0, seed=0, rot=0.0):
    import random
    rng = random.Random(seed)
    return [polar(0, 0, radius * (1 + rng.uniform(-jitter, jitter)), rot + k * 360 / n) for k in range(n)]


def circle_pts(r, n=12, cx=0.0, cy=0.0, start=-90.0, sweep=360.0, closed=True):
    count = n if closed else n + 1
    step = sweep / n
    return [polar(cx, cy, r, start + k * step) for k in range(count)]


def arc(r, a0, a1, n=8, cx=0.0, cy=0.0):
    return path([polar(cx, cy, r, a0 + (a1 - a0) * k / n) for k in range(n + 1)], smooth=1.0)


def line(*pts):
    return path(list(pts))


def solid(shape, colour, slot=None, o=100, tr=None, name="g"):
    return group(shape, fill(colour, slot, o), tr=tr, name=name)


def outline(shape, colour, width, slot=None, o=100, tr=None, name="g", cap=2):
    return group(shape, stroke(colour, width, slot, o, cap), tr=tr, name=name)


def at(x, y, r=0, s=100, a=(0, 0), o=100):
    return transform(p=(x, y), r=r, s=s, a=a, o=o)


def rrect(w, h, r, x=0, y=0):
    return rect((w, h), p=(x, y), r=r)


def circle(d, x=0, y=0):
    return ellipse((d, d), p=(x, y))


def oval(w, h, x=0, y=0):
    return ellipse((w, h), p=(x, y))


def heart_path(size=100, x=0, y=0) -> dict:
    """A proper bezier heart (notch at the top, sharp tip), size = width; starts at the notch."""
    k = size / 200
    pts = [((0, -48), (-10, -25), (10, -25)), ((52, -92), (-28, 0), (28, 0)), ((100, -35), (0, -35), (0, 40)),
           ((0, 95), (45, -40), (-45, -40)), ((-100, -35), (0, 40), (0, -35)), ((-52, -92), (28, 0), (-28, 0))]
    return {"ty": "sh", "ks": static({"c": True, "v": [[x + vx * k, y + vy * k] for (vx, vy), _, _ in pts],
                                      "i": [[ix * k, iy * k] for _, (ix, iy), _ in pts],
                                      "o": [[ox * k, oy * k] for _, _, (ox, oy) in pts]})}


def arrow_head(tip, frm, size=50, spread=32):
    """Open chevron head at `tip`, pointing away from `frm`."""
    dx, dy = tip[0] - frm[0], tip[1] - frm[1]
    ang = math.degrees(math.atan2(dy, dx))
    a = polar(tip[0], tip[1], size, ang + 180 - spread)
    b = polar(tip[0], tip[1], size, ang + 180 + spread)
    return path([a, tip, b])


def cyclic(s, frames, start, length, make):
    """Adds the layer(s) of something living [start, start+length) on a loop of `frames`, wrapping
    past the end with a copy shifted back a loop, so the loop has no gap. make(offset) -> (shapes, ks)."""
    shapes, ks = make(start)
    s.layer(*shapes, ks=ks, ip=start, op=min(frames, start + length))
    if start + length > frames:
        shapes, ks = make(start - frames)
        s.layer(*shapes, ks=ks, ip=0, op=start + length - frames)


def spikes(points):
    """Stagger helper: [(frame, value)] -> pairs for hold-like steps (unused frames ease)."""
    return points


def seq_opacity(frames, on, off, fade=3):
    """Opacity 0 -> 100 at `on`, 100 -> 0 at `off` (fades `fade` frames), 0 elsewhere."""
    keys = []
    if on > 0:
        keys.append((0, 0, LINEAR))
    keys += [(on, 0, EASE_OUT), (on + fade, 100), (max(on + fade, off - fade), 100, IN), (off, 0)]
    if off < frames:
        keys.append((frames, 0))
    return anim(keys)
