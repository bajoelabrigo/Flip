"""Morphings and Liquids (0.26): animated shape elements of our own for Motion Tools › Elements, in
the manner of the Super Morphings and Super Liquids scripts for After Effects (Jorge bought them;
they come compiled, so nothing of theirs is used: these are drawn from scratch).

Each element is one or more shape layers whose outline is animated: a list of outlines sampled
over time (12 a second), which the app morphs between with linear path keys. Every outline of a
layer has the same contours and the same number of points, so the morph is clean.

Outlines are SVG paths on a 0..100 square. The square sits on the canvas:
  "center": a square of `size` x the canvas's short side, in the middle;
  "cover":  a square as big as the canvas's diagonal, in the middle (full-screen transitions).

Writes presets/shape-elements/<id>.json.

    py tools/shape_elements/build.py
"""
import json
import math
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "presets", "shape-elements")
FPS = 12
N = 48  # points per contour

ELEMENTS = []


# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def ease_in_out(t):
    t = clamp(t)
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def ease_out(t):
    return 1 - (1 - clamp(t)) ** 3


def ease_in(t):
    return clamp(t) ** 3


def back_out(t):
    t = clamp(t)
    c1 = 1.70158
    return 1 + (c1 + 1) * (t - 1) ** 3 + c1 * (t - 1) ** 2


def elastic_out(t):
    t = clamp(t)
    if t in (0.0, 1.0):
        return t
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1


def seg(t, a, b, fn=ease_in_out):
    """0 before a, 1 after b, eased in between."""
    if b <= a:
        return 1.0 if t >= b else 0.0
    return fn((t - a) / (b - a))


# ------------------------------------------------------------------ outlines (polar, N angles)
ANGLES = [2 * math.pi * i / N - math.pi / 2 for i in range(N)]


def polar(fn):
    return [fn(a) for a in ANGLES]


def circle():
    return polar(lambda a: 1.0)


def regular(sides, rot=0.0):
    k = math.pi / sides

    def r(a):
        x = (a - rot + math.pi / 2) % (2 * k) - k
        return math.cos(k) / math.cos(x)
    return polar(r)


def square():
    return regular(4, math.pi / 4)


def star(points=5, inner=0.45):
    k = math.pi / points

    def r(a):
        x = ((a + math.pi / 2) % (2 * k)) / k  # 0..2 between two tips
        f = abs(1 - x)  # 1 at a tip, 0 halfway
        return lerp(inner, 1.0, f)
    return polar(r)


def flower(petals=5, depth=0.3):
    return polar(lambda a: (1 - depth) + depth * abs(math.cos(petals * (a + math.pi / 2) / 2)))


def heart():
    # Sampled parametrically, then read along each angle from its middle.
    pts = []
    for i in range(1440):
        t = 2 * math.pi * i / 1440
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x / 17, (y + 2.5) / 17))
    out = []
    for a in ANGLES:
        def gap(p):
            d = math.atan2(p[1], p[0]) - a
            return abs(math.atan2(math.sin(d), math.cos(d)))
        out.append(math.hypot(*min(pts, key=gap)))
    return out


def drop():
    # A teardrop pointing up (y grows downward): a circle and the two lines from the tip that touch
    # it, read along each angle from the circle's middle.
    L = 1.9  # tip's distance above the middle
    alpha = math.asin(1 / L)
    pts = []
    tangent = math.pi / 2 - alpha  # where the lines meet the circle, from the vertical
    for i in range(1440):
        u = 2 * math.pi * i / 1440
        # Arc: everything but the cap between the two tangent points.
        ang = u - math.pi / 2  # 0 = up
        d = math.atan2(math.sin(ang), math.cos(ang))
        if abs(d) >= tangent:
            pts.append((math.sin(d), -math.cos(d)))
    tip = (0.0, -L)
    for side in (-1, 1):
        ex, ey = math.sin(side * tangent), -math.cos(side * tangent)
        for k in range(200):
            f = k / 199
            pts.append((lerp(tip[0], ex, f), lerp(tip[1], ey, f)))
    out = []
    for a in ANGLES:
        def gap(p):
            dd = math.atan2(p[1], p[0]) - a
            return abs(math.atan2(math.sin(dd), math.cos(dd)))
        out.append(math.hypot(*min(pts, key=gap)) / 1.3)
    return out


def gear(teeth=10):
    return polar(lambda a: 0.82 + 0.18 * (1 if math.cos(teeth * a) > 0 else 0))


def plus(width=0.36):
    def r(a):
        c, s = abs(math.cos(a)), abs(math.sin(a))
        # The boundary of a plus of arm half-width w and length 1.
        w = width
        cand = []
        if c > 1e-9:
            cand.append(min(1 / c, w / s if s > 1e-9 else 1e9))
        if s > 1e-9:
            cand.append(min(1 / s, w / c if c > 1e-9 else 1e9))
        return max(cand)
    return polar(r)


def blob(seed, amount=0.12, lobes=(2, 3, 5), phase=0.0):
    rnd = random.Random(seed)
    parts = [(k, rnd.uniform(0.4, 1.0) * amount, rnd.uniform(0, 2 * math.pi)) for k in lobes]
    return polar(lambda a: 1 + sum(m * math.sin(k * a + p + phase * (1 + k * 0.3)) for k, m, p in parts))


def mix(ra, rb, t):
    return [lerp(a, b, t) for a, b in zip(ra, rb)]


# ------------------------------------------------------------------ to SVG
def contour(radii, cx=50, cy=50, scale=40, rot=0.0, sx=1.0, sy=1.0, smooth=1.0):
    pts = []
    for a, r in zip(ANGLES, radii):
        x = math.cos(a + rot) * r * scale * sx
        y = math.sin(a + rot) * r * scale * sy
        pts.append((cx + x, cy + y))
    return pts


def contour_points(pts, smooth=1.0):
    """Closed smooth outline through pts: Catmull-Rom tangents as Bezier handles ((next-prev)/6)."""
    n = len(pts)
    d = "M %.1f %.1f" % pts[0]
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6 * smooth, p1[1] + (p2[1] - p0[1]) / 6 * smooth)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6 * smooth, p2[1] - (p3[1] - p1[1]) / 6 * smooth)
        d += " C %.1f %.1f %.1f %.1f %.1f %.1f" % (c1 + c2 + p2)
    return d + " Z"


def svg(*contours):
    return " ".join(contours)


def element(id, label, category, duration, fit, size, layers):
    """layers: [(color_index, fn(t) -> svg)]; t in seconds."""
    frames = max(2, int(round(duration * FPS)) + 1)
    out_layers = []
    for color, fn in layers:
        keys = []
        for i in range(frames):
            t = duration * i / (frames - 1)
            keys.append({"t": round(t / duration, 4), "svg": fn(t)})
        out_layers.append({"color": color, "keys": keys})
    ELEMENTS.append({"format": 1, "id": "el-" + id, "label": label, "category": category,
                     "duration": duration, "fit": fit, "size": size, "layers": out_layers})


def single(radii_at, scale_at=lambda t: 1.0, rot_at=lambda t: 0.0, smooth_at=lambda t: 1.0, base=40):
    def fn(t):
        return contour_points(contour(radii_at(t), scale=base * scale_at(t), rot=rot_at(t)), smooth_at(t))
    return fn


def sequence(shapes, times, t):
    """The outline along a list of shapes held and morphed at `times` [(hold_until, morph_until), ...]."""
    for i in range(len(shapes) - 1):
        hold, until = times[i]
        if t < hold:
            return shapes[i]
        if t < until:
            return mix(shapes[i], shapes[i + 1], ease_in_out((t - hold) / (until - hold)))
    return shapes[-1]


# ================================================================== Morphings
SHAPES = {"circle": circle(), "square": square(), "triangle": regular(3), "star": star(),
          "hexagon": regular(6), "heart": heart(), "flower": flower(), "gear": gear(), "plus": plus(),
          "drop": drop(), "sparkle": star(4, 0.3)}
SHARP = {"square", "triangle", "star", "hexagon", "gear", "plus", "sparkle"}


def morph_chain(names, hold=0.35, morph=0.45, spin=0.0, pop=True):
    shapes = [SHAPES[n] for n in names]
    times = []
    t = 0.45 if pop else 0.0
    for _ in names[:-1]:
        times.append((t + hold, t + hold + morph))
        t += hold + morph
    duration = t + hold + (0.4 if pop else 0.0)

    def smooth(tt):
        # Sharp shapes keep their corners: the handles shrink while one of them shows.
        for i in range(len(names) - 1):
            h, u = times[i]
            if tt < u:
                a = 0.0 if names[i] in SHARP else 1.0
                b = 0.0 if names[i + 1] in SHARP else 1.0
                return lerp(a, b, ease_in_out((tt - h) / (u - h))) if tt > h else a
        return 0.0 if names[-1] in SHARP else 1.0

    def scale(tt):
        if not pop:
            return 1.0
        return back_out(tt / 0.45) * (1 - seg(tt, duration - 0.4, duration, ease_in))

    return duration, single(lambda tt: sequence(shapes, times, tt), scale,
                            lambda tt: spin * tt / duration, smooth)


for id_, label, names, spin in [
    ("shape-shuffle", "Shape Shuffle", ["circle", "square", "triangle", "star", "circle"], 0.0),
    ("circle-star", "Circle to Star", ["circle", "star"], math.pi * 0.4),
    ("square-circle", "Square to Circle", ["square", "circle"], math.pi / 2),
    ("circle-heart", "Circle to Heart", ["circle", "heart"], 0.0),
    ("star-flower", "Star to Flower", ["star", "flower"], math.pi * 0.4),
    ("triangle-hexagon", "Triangle to Hexagon", ["triangle", "hexagon"], math.pi / 3),
    ("plus-cross", "Plus to Cross", ["plus", "plus"], math.pi / 4),
    ("drop-circle", "Drop to Circle", ["drop", "circle"], 0.0),
    ("gear-circle", "Gear to Circle", ["gear", "circle"], math.pi),
    ("sparkle-star", "Sparkle to Star", ["sparkle", "star"], math.pi / 2),
    ("heart-star", "Heart to Star", ["heart", "star", "heart"], 0.0),
    ("geometry", "Geometry", ["triangle", "square", "hexagon", "circle"], math.pi),
]:
    d, fn = morph_chain(names, spin=spin)
    element(id_, label, "morph", round(d, 3), "center", 0.4, [(0, fn)])

# A heart that beats.
element("heart-beat", "Heart Beat", "morph", 1.6, "center", 0.4, [(0, single(
    lambda t: SHAPES["heart"],
    lambda t: 1 + 0.18 * math.exp(-((t % 0.8) - 0.12) ** 2 / 0.004) + 0.1 * math.exp(-((t % 0.8) - 0.32) ** 2 / 0.004),
))])
# A blob that never sits still.
element("blob-morph", "Blob", "morph", 3.0, "center", 0.4, [(0, single(
    lambda t: blob(7, 0.14, phase=t * 2.2), lambda t: back_out(t / 0.5)))])
# A flower that opens, turning.
element("flower-bloom", "Flower Bloom", "morph", 2.0, "center", 0.4, [(0, single(
    lambda t: mix(SHAPES["circle"], SHAPES["flower"], seg(t, 0.2, 1.2, back_out)),
    lambda t: ease_out(t / 0.6), lambda t: t * 0.8))])
# A gear spinning in, then out.
element("gear-spin", "Gear Spin", "morph", 2.2, "center", 0.4, [(0, single(
    lambda t: SHAPES["gear"], lambda t: back_out(t / 0.5) * (1 - seg(t, 1.8, 2.2, ease_in)),
    lambda t: t * 2.4, lambda t: 0.0))])
# A sparkle that twinkles.
element("twinkle", "Twinkle", "morph", 1.4, "center", 0.3, [(0, single(
    lambda t: SHAPES["sparkle"], lambda t: math.sin(math.pi * clamp(t / 1.4)) ** 2 * (1 + 0.15 * math.sin(t * 18)),
    lambda t: t * 1.2, lambda t: 0.0))])


def wipe(shape, rot_speed=0.0, sharp=False):
    """Grows from nothing to cover the screen, holds, then shrinks away (in and out)."""
    def fn(t):
        grow = seg(t, 0.0, 0.7, ease_in_out)
        shrink = seg(t, 1.3, 2.0, ease_in_out)
        s = grow * (1 - shrink) * 1.6
        return contour_points(contour(SHAPES[shape], scale=50 * s, rot=rot_speed * t), 0.0 if sharp else 1.0)
    return fn


element("wipe-circle", "Circle Transition", "morph", 2.0, "cover", 1.0, [(0, wipe("circle"))])
element("wipe-square", "Square Transition", "morph", 2.0, "cover", 1.0, [(0, wipe("square", 1.2, True))])
element("wipe-star", "Star Transition", "morph", 2.0, "cover", 1.0, [(0, wipe("star", 1.5, True))])
element("wipe-heart", "Heart Transition", "morph", 2.0, "cover", 1.0, [(0, wipe("heart"))])
# Two colours, one after the other.
element("wipe-double", "Double Circle Transition", "morph", 2.2, "cover", 1.0, [
    (0, lambda t: contour_points(contour(SHAPES["circle"], scale=50 * 1.6 * seg(t, 0.0, 0.7) * (1 - seg(t, 1.3, 2.0))))),
    (1, lambda t: contour_points(contour(SHAPES["circle"], scale=50 * 1.6 * seg(t, 0.2, 0.9) * (1 - seg(t, 1.5, 2.2))))),
])


# ================================================================== Liquids
def wobble_blob(seed, t, amount, speed=2.0):
    return blob(seed, amount, (2, 3, 4, 6), phase=t * speed)


# A blob of liquid that wobbles, appearing and going.
element("liquid-blob", "Liquid Blob", "liquid", 2.6, "center", 0.45, [(0, single(
    lambda t: wobble_blob(3, t, 0.12, 3.0), lambda t: elastic_out(t / 0.8) * (1 - seg(t, 2.2, 2.6, ease_in))))])


def droplets(count, seed, t, t0, spread=38, size=4.5, gravity=60, cx=50, cy=50):
    """Small drops thrown out from (cx, cy) at t0, flying and shrinking: one contour each."""
    rnd = random.Random(seed)
    out = []
    for i in range(count):
        ang = -math.pi / 2 + rnd.uniform(-1.3, 1.3)
        speed = rnd.uniform(0.6, 1.0) * spread
        r = rnd.uniform(0.6, 1.0) * size
        dt = max(0.0, t - t0)
        life = clamp(dt / 0.9)
        x = cx + math.cos(ang) * speed * ease_out(life) * 1.4
        y = cy + math.sin(ang) * speed * ease_out(life) * 1.4 + gravity * life * life * 0.5
        k = (1 - life) if t >= t0 else 0.0
        out.append(contour_points(contour(circle(), cx=x, cy=y, scale=r * k * (1 + 0.3 * (1 - life)), sx=1.0, sy=1.0)))
    return svg(*out)


def splat_puddle(t, t_hit, cy=72):
    """The drop's body: falling (stretched), then flattening into a puddle that wobbles."""
    if t < t_hit:
        k = t / t_hit
        y = lerp(-10, cy - 6, ease_in(k))
        return contour_points(contour(SHAPES["drop"], cx=50, cy=y, scale=9, sx=0.9, sy=1.25))
    k = clamp((t - t_hit) / 0.7)
    flat = elastic_out(k)
    radii = wobble_blob(11, t, 0.06 * (1 - k * 0.5), 4.0)
    return contour_points(contour(radii, cx=50, cy=cy, scale=9 + 13 * flat, sx=1.0 + 0.6 * flat, sy=1.0 - 0.55 * flat))


element("drop-splash", "Drop and Splash", "liquid", 2.0, "center", 0.6, [
    (0, lambda t: splat_puddle(t, 0.55)),
    (1, lambda t: droplets(7, 5, t, 0.55, cy=68)),
])


def splash(seed, t, t0=0.15):
    k = clamp((t - t0) / 0.5)
    body = elastic_out(k) * (1 - seg(t, 1.3, 1.9, ease_in))
    rnd = random.Random(seed)
    spikes = [rnd.uniform(0.0, 0.5) for _ in range(9)]
    radii = polar(lambda a: 1 + 0.35 * max(0.0, math.sin(9 * a / 2 + seed)) ** 8 * (1 - k * 0.6)
                  + 0.08 * math.sin(3 * a + t * 5))
    return contour_points(contour(radii, scale=30 * body))


element("splash", "Splash", "liquid", 1.9, "center", 0.55, [
    (0, lambda t: splash(2, t)),
    (1, lambda t: droplets(9, 8, t, 0.2, spread=46, gravity=30)),
])


def liquid_cover(seed, t, start, end_hold, leave, cx=50, cy=50, origin=(10, 90)):
    """A wobbly blob that grows from `origin` to cover the square, holds, and drains back."""
    grow = seg(t, start, start + 0.8, ease_in_out)
    back = seg(t, end_hold, leave, ease_in_out)
    s = grow * (1 - back)
    ox, oy = origin
    x = lerp(ox, cx, s)
    y = lerp(oy, cy, s)
    radii = wobble_blob(seed, t, 0.1, 3.5)
    return contour_points(contour(radii, cx=x, cy=y, scale=95 * s))


element("liquid-transition", "Liquid Transition", "liquid", 2.4, "cover", 1.0, [
    (0, lambda t: liquid_cover(4, t, 0.0, 1.5, 2.3)),
    (1, lambda t: liquid_cover(9, t, 0.15, 1.6, 2.4, origin=(15, 85))),
])
element("liquid-transition-right", "Liquid Transition Right", "liquid", 2.4, "cover", 1.0, [
    (0, lambda t: liquid_cover(6, t, 0.0, 1.5, 2.3, origin=(95, 15))),
    (1, lambda t: liquid_cover(12, t, 0.15, 1.6, 2.4, origin=(90, 20))),
])


def wave_rise(t, delay, phase, top_from=100, top_to=-5, hold=1.3, leave=2.2):
    """A sheet of liquid rising with a wavy top, holding, then falling away."""
    up = seg(t, delay, delay + 0.8, ease_in_out)
    down = seg(t, hold + delay, leave + delay, ease_in_out)
    level = lerp(top_from, top_to, up * (1 - down))
    pts = []
    n_top = N - 4
    for i in range(n_top):
        x = -5 + 110 * i / (n_top - 1)
        amp = 5 * (1 - abs(up - 0.5) * 1.2) + 1.5
        pts.append((x, level + amp * math.sin(x / 100 * 2 * math.pi * 1.5 + t * 6 + phase)))
    pts += [(105, 105), (105, 106), (-5, 106), (-5, 105)]
    # Straight bottom: sharp corners there, smooth wave on top.
    return contour_points(pts, 1.0)


element("wave-rise", "Wave Transition", "liquid", 2.6, "cover", 1.0, [
    (0, lambda t: wave_rise(t, 0.0, 0.0)),
    (1, lambda t: wave_rise(t, 0.18, 1.7)),
])


def drip(t, x=50, t0=0.1):
    """From the top edge a drip stretches down and lets a drop go."""
    k = seg(t, t0, t0 + 0.9, ease_in_out)
    let_go = seg(t, t0 + 0.9, t0 + 1.0)
    length = lerp(5, 45, k) * (1 - 0.6 * let_go)
    width = lerp(10, 7, k)
    pts = []
    for i in range(N):
        a = ANGLES[i]
        u = math.cos(a)
        v = math.sin(a)
        # A rounded tongue hanging from y=0.
        if v < 0:
            pts.append((x + u * width * 1.4, 0 + v * 2))
        else:
            bulb = 1 + 0.35 * v ** 6
            pts.append((x + u * width * bulb * (1 - 0.3 * v), v * length))
    body = contour_points(pts)
    fall = clamp((t - (t0 + 0.95)) / 0.9)
    r = 6 * (1 if t >= t0 + 0.95 else 0) * (1 - seg(fall, 0.85, 1.0))
    drop_y = 45 + 70 * ease_in(fall)
    drop_c = contour_points(contour(SHAPES["drop"], cx=x, cy=drop_y, scale=r, sx=0.9, sy=1.2))
    return svg(body, drop_c)


element("drip", "Drip", "liquid", 2.2, "center", 0.6, [(0, lambda t: drip(t))])
element("drips", "Drips", "liquid", 2.4, "cover", 1.0, [
    (0, lambda t: drip(t, 25, 0.0)),
    (0, lambda t: drip(t, 52, 0.25)),
    (1, lambda t: drip(t, 78, 0.12)),
])


def bubble_pop(t):
    grow = elastic_out(t / 0.9)
    popped = t > 1.2
    radii = wobble_blob(21, t, 0.05 + 0.05 * seg(t, 0.9, 1.2), 5.0)
    s = 26 * grow * (0 if popped else 1)
    return contour_points(contour(radii, scale=s))


element("bubble-pop", "Bubble Pop", "liquid", 2.0, "center", 0.5, [
    (0, bubble_pop),
    (1, lambda t: droplets(10, 31, t, 1.2, spread=40, gravity=20)),
])


def goo_merge(t):
    """Two blobs that come together into one: one outline with two lobes merging."""
    k = seg(t, 0.3, 1.4, ease_in_out)
    lobes = lerp(0.55, 0.0, k)
    radii = polar(lambda a: 1 + lobes * math.cos(2 * a) - 0.2 * lobes * (1 - abs(math.cos(a))) * 2
                  + 0.04 * math.sin(4 * a + t * 6))
    s = back_out(t / 0.4) * (1 - seg(t, 2.0, 2.4, ease_in))
    return contour_points(contour(radii, scale=28 * s, sx=1.0 + 0.5 * (1 - k), sy=1.0 - 0.15 * (1 - k)))


element("goo-merge", "Goo Merge", "liquid", 2.4, "center", 0.55, [(0, goo_merge)])


def puddle(t):
    k = elastic_out(t / 1.0)
    radii = wobble_blob(17, t, 0.08, 2.5)
    s = k * (1 - seg(t, 2.0, 2.5, ease_in))
    return contour_points(contour(radii, cy=60, scale=36 * s, sx=1.3, sy=0.55))


element("puddle", "Puddle", "liquid", 2.5, "center", 0.6, [(0, puddle)])


def burst(t):
    k = seg(t, 0.0, 0.35, ease_out)
    fade = 1 - seg(t, 0.9, 1.5, ease_in)
    rnd = random.Random(44)
    tips = [rnd.uniform(0.5, 1.0) for _ in range(N)]
    radii = [lerp(0.4, 0.4 + 0.9 * tips[i] * (1 if i % 3 == 0 else 0.35), k) for i in range(N)]
    return contour_points(contour(radii, scale=40 * fade * (0.4 + 0.6 * k), rot=t * 0.3), 0.6)


element("liquid-burst", "Liquid Burst", "liquid", 1.5, "center", 0.55, [
    (0, burst),
    (1, lambda t: droplets(8, 61, t, 0.1, spread=45, gravity=15)),
])


def main():
    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(OUT):
        if name.endswith(".json"):
            os.remove(os.path.join(OUT, name))
    counts = {}
    order = 0
    for e in ELEMENTS:
        counts[e["category"]] = counts.get(e["category"], 0) + 1
        order += 1
        e["order"] = order
        with open(os.path.join(OUT, e["id"] + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(e, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
    size = sum(os.path.getsize(os.path.join(OUT, n)) for n in os.listdir(OUT))
    print("%d elements -> %s (%d KB)" % (len(ELEMENTS), os.path.relpath(OUT, ROOT), size // 1024))
    for k, v in counts.items():
        print("  %-7s %d" % (k, v))


if __name__ == "__main__":
    main()
