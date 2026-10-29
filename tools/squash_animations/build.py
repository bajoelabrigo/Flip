"""Squash & Stretch animations (0.26): our own rubbery cartoon motions for Animation › Squash &
Stretch, in the manner of the Squash & Stretch Pro script for After Effects (Jorge bought it;
nothing of its content is copied: these follow the classic principles instead — anticipation,
stretch on the way, squash on the landing, overshoot and settle).

Writes presets/squash-animations/<id>.json. Curves run over the animation's progress (0 -> 1):
  x, y      offset as a fraction of the canvas (+ right, + down)
  rotation  degrees, clockwise
  opacity   percent
  zoom      percent of change about the box's centre (0 = as is, -100 = gone)
  stretch   percent taller from the ground edge (negative squashes; the width keeps the volume)
  bend      lean of the far end, in % of the width
  bulge     sides bowing out halfway up, in %

    py tools/squash_animations/build.py
"""
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "presets", "squash-animations")

ANIMS = []


def anim(id, label, category, duration, keys, place="playhead", ground=100):
    ANIMS.append({"format": 1, "id": "sq-" + id, "label": label, "category": category,
                  "duration": duration, "place": place, "ground": ground, "keys": keys})


def k(*points):
    """[(t, v, ease), ...] with the ease defaulting to easeInOut."""
    return [[round(p[0], 4), round(p[1], 3), p[2] if len(p) > 2 else "easeInOut"] for p in points]


def landing(t0, span, depth=35, bulge=15, rebound=12):
    """Squash on touching down at t0, a small rebound stretch, then rest: stretch and bulge keys."""
    a, b, c = t0 + span * 0.25, t0 + span * 0.6, t0 + span
    return ([(t0, -depth, "easeOut"), (a, rebound, "easeInOut"), (b, -rebound * 0.4, "easeInOut"), (c, 0)],
            [(t0, bulge, "easeOut"), (a, -bulge * 0.3, "easeInOut"), (c, 0)])


def decaying(t0, t1, amp, cycles, ease="easeInOut", end=0.0):
    """An oscillation from t0 to t1 that dies away, ending on `end`."""
    pts = [(t0, end, ease)]
    n = max(1, int(cycles * 2))
    for i in range(1, n + 1):
        t = t0 + (t1 - t0) * i / (n + 1)
        a = amp * (1 - i / (n + 1)) * (1 if i % 2 else -1)
        pts.append((t, end + a, ease))
    pts.append((t1, end))
    return pts


# ---------------------------------------------------------------- In (at the clip's start)
anim("drop-in", "Drop In", "in", 1.1, {
    "y": k((0, -0.75, "easeIn"), (0.42, 0)),
    "stretch": k((0, 25, "easeIn"), (0.4, 45, "easeOut"), (0.44, -38, "easeOut"), (0.62, 14), (0.8, -5), (1, 0)),
    "bulge": k((0.4, 0), (0.44, 18, "easeOut"), (0.62, -4), (1, 0)),
    "opacity": k((0, 100, "linear"), (1, 100)),
}, place="start")

anim("bounce-in", "Bounce In", "in", 1.5, {
    "y": k((0, -0.7, "easeIn"), (0.32, 0, "easeOut"), (0.5, -0.12, "easeIn"), (0.66, 0, "easeOut"),
           (0.76, -0.035, "easeIn"), (0.84, 0)),
    "stretch": k((0, 20, "easeIn"), (0.3, 40, "easeOut"), (0.33, -40, "easeOut"), (0.42, 22), (0.5, 0, "easeIn"),
                 (0.64, 18, "easeOut"), (0.67, -24, "easeOut"), (0.74, 8), (0.84, -10, "easeOut"), (0.92, 3), (1, 0)),
    "bulge": k((0.3, 0), (0.33, 18), (0.42, 0), (0.64, 0), (0.67, 12), (0.74, 0), (0.84, 6), (1, 0)),
}, place="start")

anim("pop-in", "Pop In", "in", 0.8, {
    "zoom": k((0, -100, "easeOut"), (0.45, 18, "easeInOut"), (0.7, -6), (1, 0)),
    "stretch": k((0, 0), (0.3, 25), (0.5, -15), (0.72, 6), (1, 0)),
    "bulge": k((0, 0), (0.45, 12), (0.7, -4), (1, 0)),
}, place="start", ground=50)

anim("spring-up", "Spring Up", "in", 1.0, {
    "y": k((0, 0.6, "easeOut"), (0.45, -0.06, "easeInOut"), (0.7, 0.01), (1, 0)),
    "stretch": k((0, -60, "easeOut"), (0.2, 55, "easeInOut"), (0.45, 15), (0.55, -22), (0.75, 8), (1, 0)),
    "bulge": k((0, 25), (0.2, -10), (0.55, 10), (1, 0)),
}, place="start")

anim("slide-in-left", "Slide In Left", "in", 1.0, {
    "x": k((0, -0.75, "easeOut"), (0.5, 0.03, "easeInOut"), (0.75, -0.008), (1, 0)),
    "bend": k((0, 35, "easeOut"), (0.45, 18, "easeInOut"), (0.55, -28), (0.72, 12), (0.86, -5), (1, 0)),
    "stretch": k((0, -10), (0.5, -18), (0.62, 8), (1, 0)),
}, place="start")

anim("slide-in-right", "Slide In Right", "in", 1.0, {
    "x": k((0, 0.75, "easeOut"), (0.5, -0.03, "easeInOut"), (0.75, 0.008), (1, 0)),
    "bend": k((0, -35, "easeOut"), (0.45, -18, "easeInOut"), (0.55, 28), (0.72, -12), (0.86, 5), (1, 0)),
    "stretch": k((0, -10), (0.5, -18), (0.62, 8), (1, 0)),
}, place="start")

anim("jelly-in", "Jelly In", "in", 1.2, {
    "zoom": k((0, -100, "back"), (0.35, 0)),
    "stretch": k(*decaying(0.25, 1.0, 34, 3)),
    "bulge": k(*decaying(0.25, 1.0, -18, 3)),
}, place="start", ground=50)

anim("grow-up", "Grow Up", "in", 0.9, {
    "stretch": k((0, -90, "easeOut"), (0.45, 22, "easeInOut"), (0.68, -8), (1, 0)),
    "bulge": k((0, 0), (0.45, -10), (0.68, 6), (1, 0)),
    "opacity": k((0, 0, "linear"), (0.12, 100)),
}, place="start")

anim("rise-wobble", "Rise and Wobble", "in", 1.1, {
    "y": k((0, 0.15, "easeOut"), (0.45, 0)),
    "opacity": k((0, 0, "easeOut"), (0.35, 100)),
    "bend": k(*decaying(0.3, 1.0, 22, 2.5)),
}, place="start")

anim("swing-in", "Swing In", "in", 1.2, {
    "y": k((0, -0.6, "easeOut"), (0.4, 0)),
    "rotation": k((0, -35, "easeOut"), (0.4, 14), (0.6, -7), (0.78, 3), (1, 0)),
    "bend": k((0, -15), (0.4, 18), (0.6, -8), (1, 0)),
}, place="start", ground=0)

# ---------------------------------------------------------------- Out (at the clip's end)
anim("jump-out", "Jump Out", "out", 1.0, {
    "stretch": k((0, 0, "easeOut"), (0.28, -35, "easeIn"), (0.4, 50, "easeOut"), (0.7, 30), (1, 40)),
    "bulge": k((0, 0), (0.28, 18, "easeIn"), (0.4, -8), (1, 0)),
    "y": k((0, 0, "hold"), (0.36, 0, "easeIn"), (1, -1.1)),
}, place="end")

anim("fall-out", "Fall Out", "out", 0.9, {
    "stretch": k((0, 0), (0.2, -18, "easeIn"), (0.35, 10, "easeIn"), (1, 45)),
    "y": k((0, 0, "easeOut"), (0.2, -0.04, "easeIn"), (1, 1.0)),
}, place="end")

anim("pop-out", "Pop Out", "out", 0.7, {
    "zoom": k((0, 0, "easeOut"), (0.45, 20, "easeIn"), (1, -100)),
    "stretch": k((0, 0), (0.3, -18), (0.55, 20), (1, 0)),
    "bulge": k((0, 0), (0.3, 15), (1, 0)),
}, place="end", ground=50)

anim("slide-out-left", "Slide Out Left", "out", 0.9, {
    "x": k((0, 0, "easeInOut"), (0.3, 0.04, "easeIn"), (1, -0.85)),
    "bend": k((0, 0), (0.3, -22, "easeIn"), (0.45, 35), (1, 25)),
    "stretch": k((0, 0), (0.3, -15), (0.5, -8), (1, -8)),
}, place="end")

anim("slide-out-right", "Slide Out Right", "out", 0.9, {
    "x": k((0, 0, "easeInOut"), (0.3, -0.04, "easeIn"), (1, 0.85)),
    "bend": k((0, 0), (0.3, 22, "easeIn"), (0.45, -35), (1, -25)),
    "stretch": k((0, 0), (0.3, -15), (0.5, -8), (1, -8)),
}, place="end")

anim("squash-down", "Squash Down", "out", 0.8, {
    "stretch": k((0, 0, "easeOut"), (0.3, 18, "easeIn"), (1, -90)),
    "bulge": k((0, 0), (0.3, -6), (1, 30)),
    "opacity": k((0, 100), (0.75, 100, "linear"), (1, 0)),
}, place="end")

anim("launch-spin", "Launch and Spin", "out", 1.1, {
    "stretch": k((0, 0, "easeOut"), (0.25, -40, "easeIn"), (0.35, 45), (1, 20)),
    "y": k((0, 0, "hold"), (0.32, 0, "easeIn"), (1, -1.2)),
    "rotation": k((0, 0, "hold"), (0.32, 0, "easeIn"), (1, 540)),
}, place="end")

anim("blow-away", "Blow Away", "out", 1.1, {
    "x": k((0, 0, "easeIn"), (1, 0.9)),
    "y": k((0, 0, "easeInOut"), (0.4, -0.08), (1, -0.45)),
    "rotation": k((0, 0, "easeIn"), (1, 70)),
    "bend": k((0, 0), (0.2, -25), (0.5, 20), (0.8, -15), (1, 10)),
    "opacity": k((0, 100), (0.8, 100, "linear"), (1, 0)),
}, place="end")

anim("melt-out", "Melt", "out", 1.0, {
    "stretch": k((0, 0, "easeIn"), (1, -85)),
    "bulge": k((0, 0, "easeIn"), (1, 60)),
    "bend": k((0, 0), (0.3, 6), (0.6, -6), (1, 0)),
}, place="end")

# ---------------------------------------------------------------- Moves (at the playhead)
def hop(t0, t1, height, depth=30, x0=0.0, x1=0.0):
    """One hop from t0 to t1: crouch, launch stretched, fly, land squashed."""
    up = t0 + (t1 - t0) * 0.22
    top = t0 + (t1 - t0) * 0.55
    land = t0 + (t1 - t0) * 0.88
    y = [(t0, 0, "hold"), (up, 0, "easeOut"), (top, -height, "easeIn"), (land, 0, "hold")]
    x = [(t0, x0, "hold"), (up, x0, "easeInOut"), (land, x1, "hold")]
    s = [(t0, 0, "easeOut"), (up, -depth, "easeOut"), (up + (top - up) * 0.4, depth * 1.2, "easeInOut"),
         (top, 0, "easeIn"), (land - 0.0001, depth * 0.8, "easeOut"), (land, -depth, "easeOut"),
         (t1, 0)]
    b = [(t0, 0), (up, depth * 0.5), (up + (top - up) * 0.4, -depth * 0.2), (top, 0), (land, depth * 0.5),
         (t1, 0)]
    return x, y, s, b


def hops(specs, total):
    xs, ys, ss, bs = [], [], [], []
    for (t0, t1, h, d, xa, xb) in specs:
        x, y, s, b = hop(t0, t1, h, d, xa, xb)
        xs += x
        ys += y
        ss += s
        bs += b
    keys = {"y": k(*ys), "stretch": k(*ss), "bulge": k(*bs)}
    if any(abs(p[1]) > 1e-6 for p in xs):
        keys["x"] = k(*xs)
    return keys


anim("hop", "Hop", "moves", 0.9, hops([(0, 1, 0.16, 30, 0, 0)], 1))
anim("double-hop", "Double Hop", "moves", 1.5, hops([(0, 0.5, 0.14, 26, 0, 0), (0.5, 1, 0.1, 22, 0, 0)], 1))
anim("hop-forward", "Hop Forward", "moves", 1.0, hops([(0, 1, 0.18, 32, 0, 0.2)], 1))
anim("hop-back", "Hop Back", "moves", 1.0, hops([(0, 1, 0.18, 32, 0, -0.2)], 1))
anim("sack-race", "Sack Race", "moves", 2.1,
     hops([(0, 0.34, 0.08, 25, 0, 0.07), (0.33, 0.67, 0.08, 25, 0.07, 0.14), (0.66, 1, 0.08, 25, 0.14, 0.21)], 1))
anim("inchworm", "Inchworm", "moves", 2.4, {
    "stretch": k((0, 0), (0.17, 35), (0.33, -15), (0.5, 0), (0.67, 35), (0.83, -15), (1, 0)),
    "bend": k((0, 0), (0.17, 20), (0.33, -8), (0.5, 0), (0.67, 20), (0.83, -8), (1, 0)),
    "x": k((0, 0, "hold"), (0.2, 0), (0.4, 0.06, "hold"), (0.7, 0.06), (0.9, 0.12, "hold"), (1, 0.12)),
})
anim("stumble", "Stumble", "moves", 1.3, {
    "bend": k((0, 0, "easeIn"), (0.25, 45, "easeOut"), (0.4, -20), (0.6, 12), (0.8, -5), (1, 0)),
    "x": k((0, 0, "easeIn"), (0.25, 0.04, "easeOut"), (0.5, 0.06), (1, 0.06)),
    "stretch": k((0, 0), (0.25, -18), (0.45, 8), (1, 0)),
})
anim("fall-bounce", "Fall and Bounce", "moves", 1.6, {
    "y": k((0, 0, "easeIn"), (0.35, 0.3, "easeOut"), (0.55, 0.2, "easeIn"), (0.72, 0.3, "easeOut"),
           (0.82, 0.27, "easeIn"), (0.9, 0.3)),
    "stretch": k((0, 0, "easeIn"), (0.33, 35), (0.36, -40, "easeOut"), (0.45, 15), (0.55, 0, "easeIn"),
                 (0.71, 15), (0.73, -25), (0.8, 5), (0.9, -10), (1, 0)),
    "bulge": k((0.33, 0), (0.36, 20), (0.45, 0), (0.71, 0), (0.73, 12), (0.8, 0), (0.9, 6), (1, 0)),
})
anim("dash-right", "Dash Right", "moves", 1.0, {
    "x": k((0, 0, "easeInOut"), (0.2, -0.025, "easeIn"), (0.55, 0.3, "easeOut"), (0.75, 0.31), (1, 0.3)),
    "bend": k((0, 0), (0.2, 18, "easeIn"), (0.35, -40, "easeOut"), (0.55, 30), (0.7, -12), (0.85, 5), (1, 0)),
    "stretch": k((0, 0), (0.2, -15), (0.4, -25), (0.6, 10), (1, 0)),
})
anim("dash-left", "Dash Left", "moves", 1.0, {
    "x": k((0, 0, "easeInOut"), (0.2, 0.025, "easeIn"), (0.55, -0.3, "easeOut"), (0.75, -0.31), (1, -0.3)),
    "bend": k((0, 0), (0.2, -18, "easeIn"), (0.35, 40, "easeOut"), (0.55, -30), (0.7, 12), (0.85, -5), (1, 0)),
    "stretch": k((0, 0), (0.2, -15), (0.4, -25), (0.6, 10), (1, 0)),
})

# ---------------------------------------------------------------- Jumps (cartoon)
anim("big-jump", "Big Jump", "jumps", 1.4, hops([(0, 1, 0.42, 45, 0, 0)], 1))
anim("trampoline", "Trampoline", "jumps", 2.4,
     hops([(0, 0.25, 0.1, 25, 0, 0), (0.25, 0.55, 0.22, 35, 0, 0), (0.55, 1, 0.38, 45, 0, 0)], 1))
_spin = hops([(0, 1, 0.35, 40, 0, 0)], 1)
_spin["rotation"] = k((0, 0, "hold"), (0.22, 0, "easeInOut"), (0.88, 360, "hold"), (1, 360))
anim("jump-spin", "Jump Spin", "jumps", 1.3, _spin)
_flip = hops([(0, 1, 0.35, 40, 0, 0)], 1)
_flip["rotation"] = k((0, 0, "hold"), (0.22, 0, "easeInOut"), (0.88, -360, "hold"), (1, -360))
anim("backflip", "Backflip", "jumps", 1.3, _flip)
anim("leap-over", "Leap Over", "jumps", 1.4, hops([(0, 1, 0.3, 40, 0, 0.35)], 1))
anim("tiny-hops", "Tiny Hops", "jumps", 1.6,
     hops([(i / 4, (i + 1) / 4, 0.05, 18, 0, 0) for i in range(4)], 1))
anim("super-squash", "Super Squash Landing", "jumps", 1.5, {
    "y": k((0, -0.5, "easeIn"), (0.3, 0)),
    "stretch": k((0, 30, "easeIn"), (0.28, 55, "easeOut"), (0.31, -70, "easeOut"), (0.5, 30), (0.65, -15),
                 (0.8, 6), (1, 0)),
    "bulge": k((0.28, 0), (0.31, 40, "easeOut"), (0.5, -10), (0.65, 6), (1, 0)),
})

# ---------------------------------------------------------------- Highlights (at the playhead)
anim("pulse", "Pulse", "highlights", 0.7, {
    "zoom": k((0, 0, "easeOut"), (0.4, 14, "easeInOut"), (0.7, -3), (1, 0)),
    "bulge": k((0, 0), (0.4, 10), (1, 0)),
}, ground=50)
anim("heartbeat", "Heartbeat", "highlights", 1.0, {
    "zoom": k((0, 0, "easeOut"), (0.15, 12, "easeIn"), (0.3, 0, "easeOut"), (0.45, 16, "easeIn"), (0.7, 0)),
    "bulge": k((0, 0), (0.15, 8), (0.3, 0), (0.45, 10), (0.7, 0)),
}, ground=50)
anim("jelly", "Jelly", "highlights", 1.2, {
    "stretch": k(*decaying(0, 1, 32, 3.5)),
    "bulge": k(*decaying(0, 1, -18, 3.5)),
})
anim("rubber-band", "Rubber Band", "highlights", 1.0, {
    "stretch": k((0, 0, "easeOut"), (0.3, -32, "easeInOut"), (0.45, 22), (0.6, -14), (0.75, 6), (1, 0)),
    "bulge": k((0, 0), (0.3, 18), (0.45, -8), (1, 0)),
}, ground=50)
anim("tada", "Ta-da", "highlights", 1.0, {
    "zoom": k((0, 0, "easeOut"), (0.15, -10), (0.3, 12), (0.85, 12, "easeInOut"), (1, 0)),
    "rotation": k((0, 0), (0.15, -4), (0.3, 4), (0.4, -4), (0.5, 4), (0.6, -4), (0.7, 4), (0.8, -4), (0.9, 0)),
}, ground=50)
anim("nod", "Nod", "highlights", 1.0, {
    "bend": k((0, 0, "easeInOut"), (0.25, 28), (0.5, -10), (0.7, 14), (1, 0)),
    "stretch": k((0, 0), (0.25, -12), (0.5, 4), (0.7, -6), (1, 0)),
})
anim("shake-no", "Shake No", "highlights", 1.0, {
    "x": k(*decaying(0, 1, 0.03, 3)),
    "bend": k(*decaying(0, 1, -25, 3)),
})
anim("attention", "Attention", "highlights", 1.3, dict(hops([(0, 0.6, 0.1, 25, 0, 0)], 1), **{
    "zoom": k((0, 0), (0.6, 0, "easeOut"), (0.78, 12), (1, 0)),
}))

# ---------------------------------------------------------------- Rotations
anim("spin-squash", "Spin with Squash", "rotations", 1.2, {
    "rotation": k((0, 0, "back"), (0.85, 360, "linear"), (1, 360)),
    "stretch": k((0, 0), (0.2, -20), (0.5, 25), (0.85, -15), (1, 0)),
}, ground=50)
anim("swing", "Swing", "rotations", 1.6, {
    "rotation": k(*decaying(0, 1, 28, 3)),
    "bend": k(*decaying(0, 1, -12, 3)),
}, ground=0)
anim("wobble-turn", "Wobble Turn", "rotations", 1.2, {
    "rotation": k((0, 0, "easeInOut"), (0.45, 190), (0.65, 170), (0.82, 182), (1, 180)),
    "stretch": k((0, 0), (0.45, 18), (0.65, -10), (1, 0)),
}, ground=50)
anim("topple", "Topple", "rotations", 1.3, {
    "rotation": k((0, 0, "easeIn"), (0.45, 90, "easeOut"), (0.6, 80), (0.75, 92), (0.88, 88), (1, 90)),
    "stretch": k((0, 0), (0.45, 0), (0.5, -25), (0.65, 8), (1, 0)),
})
anim("flip-around", "Flip Around", "rotations", 1.0, {
    "rotation": k((0, 0, "easeInOut"), (0.7, -360, "easeOut"), (1, -360)),
    "zoom": k((0, 0), (0.35, -25), (0.7, 6), (1, 0)),
}, ground=50)

# ---------------------------------------------------------------- Wiggles (loops you can repeat)
anim("wiggle-soft", "Soft Wiggle", "wiggles", 2.0, {
    "bend": k((0, 0), (0.125, 14), (0.375, -14), (0.625, 14), (0.875, -14), (1, 0)),
})
anim("jelly-shake", "Jelly Shake", "wiggles", 1.6, {
    "bulge": k((0, 0), (0.125, 22), (0.375, -16), (0.625, 22), (0.875, -16), (1, 0)),
    "stretch": k((0, 0), (0.125, -10), (0.375, 10), (0.625, -10), (0.875, 10), (1, 0)),
})
anim("dance", "Dance", "wiggles", 2.0, {
    "bend": k((0, 0), (0.25, 22), (0.5, 0), (0.75, -22), (1, 0)),
    "stretch": k((0, 0), (0.125, -15), (0.25, 10), (0.375, -15), (0.5, 0), (0.625, -15), (0.75, 10),
                 (0.875, -15), (1, 0)),
    "y": k((0, 0), (0.125, 0.01), (0.25, -0.02), (0.375, 0.01), (0.5, 0), (0.625, 0.01), (0.75, -0.02),
           (0.875, 0.01), (1, 0)),
})
anim("breathe", "Breathe", "wiggles", 2.4, {
    "stretch": k((0, 0), (0.5, 9), (1, 0)),
    "bulge": k((0, 0), (0.5, -4), (1, 0)),
})
anim("wobble", "Wobble", "wiggles", 1.4, {
    "rotation": k((0, 0), (0.25, 6), (0.5, -6), (0.75, 6), (1, 0)),
    "bend": k((0, 0), (0.25, -10), (0.5, 10), (0.75, -10), (1, 0)),
}, ground=50)

# ---------------------------------------------------------------- Glitch (hard steps)
def steps(values, ease="hold"):
    n = len(values)
    return [(i / max(1, n - 1), v, ease) for i, v in enumerate(values)]


anim("glitch-jump", "Glitch Jump", "glitch", 0.8, {
    "x": k(*steps([0, 0.02, -0.03, 0.04, -0.01, 0.025, 0, -0.02, 0])),
    "stretch": k(*steps([0, 30, -20, 45, 0, -25, 15, 0, 0])),
    "bend": k(*steps([0, -20, 25, 0, 30, -15, 0, 10, 0])),
})
anim("glitch-in", "Glitch In", "glitch", 0.7, {
    "opacity": k(*steps([0, 100, 0, 100, 30, 100, 100])),
    "x": k(*steps([0.05, -0.03, 0.02, -0.04, 0.01, 0, 0])),
    "stretch": k(*steps([60, -30, 40, -20, 10, 0, 0])),
}, place="start")
anim("glitch-out", "Glitch Out", "glitch", 0.7, {
    "opacity": k(*steps([100, 100, 30, 100, 0, 100, 0])),
    "x": k(*steps([0, 0.01, -0.04, 0.02, -0.03, 0.05, 0.05])),
    "stretch": k(*steps([0, 10, -20, 40, -30, 60, 60])),
}, place="end")
anim("jitter", "Jitter", "glitch", 1.0, {
    "x": k(*steps([0, 0.006, -0.008, 0.004, -0.006, 0.008, -0.004, 0.006, 0])),
    "y": k(*steps([0, -0.005, 0.004, 0.007, -0.006, 0.002, 0.006, -0.004, 0])),
    "bend": k(*steps([0, 6, -8, 4, -6, 8, -4, 6, 0])),
})
anim("glitch-squash", "Glitch Squash", "glitch", 0.9, {
    "stretch": k(*steps([0, -40, 30, -55, 20, -10, 0])),
    "bulge": k(*steps([0, 25, -15, 35, -10, 5, 0])),
    "zoom": k(*steps([0, 6, -4, 8, 0, 3, 0])),
})

ORDER = ["in", "out", "moves", "jumps", "highlights", "rotations", "wiggles", "glitch"]


def main():
    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(OUT):
        if name.endswith(".json"):
            os.remove(os.path.join(OUT, name))
    counters = {}
    for a in ANIMS:
        cat = a["category"]
        counters[cat] = counters.get(cat, 0) + 1
        a["order"] = ORDER.index(cat) * 100 + counters[cat]
        with open(os.path.join(OUT, a["id"] + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(a, f, ensure_ascii=False, indent=1)
            f.write("\n")
    print("%d animations -> %s" % (len(ANIMS), os.path.relpath(OUT, ROOT)))
    for cat in ORDER:
        print("  %-11s %d" % (cat, counters.get(cat, 0)))


if __name__ == "__main__":
    main()
