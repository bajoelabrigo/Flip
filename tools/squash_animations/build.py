"""Squash & Stretch animations (0.26): rubbery cartoon motion for Animation › Squash & Stretch, in
the manner of the Squash & Stretch Pro script for After Effects (Jorge bought it). Nothing of its
content is used. Its motion was studied to learn how a rubber layer should move: the base stays
on the ground; it crouches with the top widening and the sides bulging; it takes off stretched and
narrow at the top; it hangs at the apex; it falls with gravity; it squashes on landing with the base
spreading; it bounces a little; it wobbles as it settles; and when it slides, the top lags as it
speeds up and swings past as it stops.

So these are not keyframes written by hand. Each animation is a path (beats: crouch, jump, fall,
slide, spin, pop...), and the body's shape comes out of a damped spring driven by that motion:
it stretches with speed, squashes on impacts, and lags and wobbles with acceleration. The frames
are then thinned to the keys that matter (Ramer-Douglas-Peucker on each channel) and written as
linear keys.

Channels, over the animation's progress (0 -> 1):
  x, y         offset as a fraction of the canvas (+ right, + down)
  rotation     degrees, clockwise
  opacity      percent
  zoom         percent of change about the box's centre (0 = as is, -100 = gone)
  stretch      percent taller from the ground edge (negative squashes)
  groundWidth  percent wider at the ground edge
  farWidth     percent wider at the top
  shear        lean of the top, in % of the width (+ right)
  bulge        sides bowing out halfway up, in %

    py tools/squash_animations/build.py [--preview <dir>]
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "presets", "squash-animations")
FPS = 30
DT = 1.0 / FPS


def clamp(v, a, b):
    return max(a, min(b, v))


def lerp(a, b, t):
    return a + (b - a) * t


EASES = {
    "linear": lambda u: u,
    "in": lambda u: u * u,
    "in3": lambda u: u * u * u,
    "out": lambda u: 1 - (1 - u) ** 2,
    "out3": lambda u: 1 - (1 - u) ** 3,
    "inout": lambda u: 3 * u * u - 2 * u * u * u,
    "inout3": lambda u: 4 * u ** 3 if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2,
    "back": lambda u: 1 + 2.70158 * (u - 1) ** 3 + 1.70158 * (u - 1) ** 2,
    "backin": lambda u: 2.70158 * u ** 3 - 1.70158 * u ** 2,
}


class Seq:
    """The path of the body, frame by frame, and what happens to it (crouches, impacts)."""

    def __init__(self, x=0.0, y=0.0, rot=0.0, zoom=0.0, op=100.0):
        self.s = dict(x=x, y=y, rot=rot, zoom=zoom, op=op)
        self.frames = []          # [{x, y, rot, zoom, op}]
        self.crouch = []          # per frame: target squash (negative stretch) or None
        self.impulses = {}        # frame -> stretch velocity kick (negative = squash)
        self.lean_kicks = {}      # frame -> lean velocity kick
        self.extra = []           # per frame: dict of channel offsets (spin wobble, pops)
        self.push()

    def push(self, crouch=None, extra=None):
        self.frames.append(dict(self.s))
        self.crouch.append(crouch)
        self.extra.append(extra or {})

    def n(self, sec):
        # A stretch of 0 s takes no frame (a jump out has no fall).
        return 0 if sec <= 0 else max(1, int(round(sec * FPS)))

    def hold(self, sec, crouch=None):
        for _ in range(self.n(sec)):
            self.push(crouch)
        return self

    def to(self, sec, ease="inout", crouch=None, **target):
        """Moves the given channels to `target` (absolute) over `sec`."""
        start = dict(self.s)
        steps = self.n(sec)
        fn = EASES[ease]
        for i in range(1, steps + 1):
            u = fn(i / steps)
            for k, v in target.items():
                self.s[k] = lerp(start[k], v, u)
            self.push(crouch)
        return self

    def by(self, sec, ease="inout", crouch=None, **delta):
        return self.to(sec, ease, crouch, **{k: self.s[k] + v for k, v in delta.items()})

    def squat(self, sec, depth):
        """Anticipation: the body crouches by `depth` (fraction of its height) and holds."""
        steps = self.n(sec)
        for i in range(1, steps + 1):
            self.push(crouch=-depth * 100 * EASES["out"](i / steps))
        return self

    def impact(self, strength):
        self.impulses[len(self.frames) - 1] = self.impulses.get(len(self.frames) - 1, 0.0) - strength

    def kick_lean(self, amount):
        self.lean_kicks[len(self.frames) - 1] = self.lean_kicks.get(len(self.frames) - 1, 0.0) + amount

    def jump(self, height, dx=0.0, rise=0.2, hang=0.12, fall=0.2, spin=0.0, land=True, impact=1.0):
        """Takes off (the crouch before it is up to the caller), rises easing out, hangs at the top,
        falls with gravity and lands with an impact."""
        y0 = self.s["y"]
        x0 = self.s["x"]
        r0 = self.s["rot"]
        total = rise + hang + fall
        steps_r, steps_h, steps_f = self.n(rise), self.n(hang), self.n(fall)
        allsteps = steps_r + steps_h + steps_f
        k = 0
        for i in range(1, steps_r + 1):
            k += 1
            u = EASES["out"](i / steps_r)
            self.s["y"] = y0 - height * u * 0.94
            self.s["x"] = x0 + dx * EASES["inout"](k / allsteps)
            self.s["rot"] = r0 + spin * EASES["inout"](k / allsteps)
            self.push()
        for i in range(1, steps_h + 1):
            k += 1
            u = EASES["inout"](i / max(1, steps_h))
            self.s["y"] = y0 - height * (0.94 + 0.06 * math.sin(math.pi * u))
            self.s["x"] = x0 + dx * EASES["inout"](k / allsteps)
            self.s["rot"] = r0 + spin * EASES["inout"](k / allsteps)
            self.push()
        for i in range(1, steps_f + 1):
            k += 1
            u = EASES["in"](i / steps_f)
            self.s["y"] = y0 - height * 0.94 * (1 - u)
            self.s["x"] = x0 + dx * EASES["inout"](k / allsteps)
            self.s["rot"] = r0 + spin * EASES["inout"](k / allsteps)
            self.push()
        if land:
            self.s["y"] = y0
            self.impact(impact * (0.6 + 2.2 * height))
        return self

    def hop(self, height, dx=0.0, sec=0.3, impact=0.5):
        """A small bounce: no crouch, short air time."""
        return self.jump(height, dx, rise=sec * 0.45, hang=sec * 0.1, fall=sec * 0.45, impact=impact)

    def fall_from(self, height, sec, impact=1.0):
        """Starts `height` above and falls with gravity to where it rests."""
        y0 = self.s["y"]
        self.s["y"] = y0 - height
        self.frames[-1] = dict(self.s)
        steps = self.n(sec)
        for i in range(1, steps + 1):
            self.s["y"] = y0 - height * (1 - EASES["in"](i / steps))
            self.push()
        self.impact(impact * (0.8 + 1.8 * min(height, 1.0)))
        return self


# ------------------------------------------------------------------ the body's spring
def simulate(seq, intensity=1.0, wobble=1.0):
    """Turns the path into the body's shape, frame by frame."""
    n = len(seq.frames)
    xs = [f["x"] for f in seq.frames]
    ys = [f["y"] for f in seq.frames]
    vx = [0.0] * n
    vy = [0.0] * n
    for i in range(1, n):
        vx[i] = (xs[i] - xs[i - 1]) / DT
        vy[i] = (ys[i] - ys[i - 1]) / DT
    ax = [0.0] * n
    for i in range(1, n):
        ax[i] = (vx[i] - vx[i - 1]) / DT
    # Springs: stretch (height) and lean (top offset), each a damped oscillator.
    s, sv = 0.0, 0.0
    lean, lv = 0.0, 0.0
    w_s = 2 * math.pi * 3.2      # how fast the body springs back (Hz)
    z_s = 0.32 / wobble          # damping: lower wobbles longer
    w_l = 2 * math.pi * 2.6
    z_l = 0.28 / wobble
    out = []
    for i in range(n):
        crouch = seq.crouch[i]
        speed_y = abs(vy[i])
        airborne = ys[i] < -0.004
        if crouch is not None:
            target = crouch
        else:
            # Stretched along the way it moves fast (up or down); a slide barely stretches. Off the
            # ground it stays drawn out, hanging at the top as Squash & Stretch Pro keeps it.
            target = clamp(speed_y * 9.0, 0.0, 38.0) - clamp(abs(vx[i]) * 1.2, 0.0, 6.0)
            if airborne:
                target = max(target, 16.0)
        # The top trails a little while it travels (more on a fast jump than on a slide).
        lean_target = clamp(-vx[i] * (14.0 if airborne else 5.0), -35.0, 35.0)
        if i in seq.impulses:
            sv += seq.impulses[i] * 900.0
        if i in seq.lean_kicks:
            lv += seq.lean_kicks[i] * 400.0
        sub = 6
        for _ in range(sub):
            h = DT / sub
            if crouch is not None:
                # A crouch is held by the muscles, not left to wobble: follow it closely.
                sv += (-(w_s * 1.4) ** 2 * (s - target) - 2 * 0.9 * (w_s * 1.4) * sv) * h
            else:
                sv += (-(w_s ** 2) * (s - target) - 2 * z_s * w_s * sv) * h
            s += sv * h
            # The top lags behind when it speeds up and swings past when it stops.
            lv += (-(w_l ** 2) * (lean - lean_target) - 2 * z_l * w_l * lv - ax[i] * 1.2) * h
            lean += lv * h
        st = clamp(s, -75.0, 60.0)
        if st >= 0:
            gw, fw, bu = 0.18 * st, -0.62 * st, -0.2 * st
        else:
            gw, fw, bu = -0.75 * st, -0.18 * st, -0.6 * st
        sh = clamp(lean, -60.0, 60.0)
        frame = seq.frames[i]
        extra = seq.extra[i]
        out.append({
            "x": frame["x"], "y": frame["y"], "rotation": frame["rot"], "opacity": frame["op"],
            "zoom": frame["zoom"] + extra.get("zoom", 0.0),
            "stretch": st * intensity + extra.get("stretch", 0.0),
            "groundWidth": gw * intensity, "farWidth": fw * intensity,
            "shear": sh * intensity, "bulge": bu * intensity + extra.get("bulge", 0.0),
        })
    return out


# ------------------------------------------------------------------ thinning to keys
def rdp(points, eps):
    """Ramer-Douglas-Peucker on (t, v): the keys a linear curve needs to stay within eps."""
    if len(points) < 3:
        return points
    (t0, v0), (t1, v1) = points[0], points[-1]
    best, idx = 0.0, 0
    for i in range(1, len(points) - 1):
        t, v = points[i]
        expected = v0 + (v1 - v0) * (t - t0) / (t1 - t0) if t1 != t0 else v0
        d = abs(v - expected)
        if d > best:
            best, idx = d, i
    if best <= eps:
        return [points[0], points[-1]]
    return rdp(points[: idx + 1], eps)[:-1] + rdp(points[idx:], eps)


TOLERANCE = {"x": 0.0015, "y": 0.0015, "rotation": 0.5, "opacity": 1.0, "zoom": 0.6, "stretch": 0.6,
             "groundWidth": 0.5, "farWidth": 0.5, "shear": 0.6, "bulge": 0.5}
REST = {"x": 0.0, "y": 0.0, "rotation": 0.0, "opacity": 100.0, "zoom": 0.0, "stretch": 0.0, "groundWidth": 0.0,
        "farWidth": 0.0, "shear": 0.0, "bulge": 0.0}


def keys_of(frames):
    n = len(frames)
    keys = {}
    for ch in REST:
        pts = [(i / (n - 1), frames[i][ch]) for i in range(n)]
        if all(abs(v - REST[ch]) < TOLERANCE[ch] * 0.5 for _, v in pts):
            continue
        thin = rdp(pts, TOLERANCE[ch])
        keys[ch] = [[round(t, 4), round(v, 4 if ch in ("x", "y") else 2), "linear"] for t, v in thin]
    return keys


ANIMS = []


def anim(id, label, category, seq, place="playhead", intensity=1.0, wobble=1.0, ground=100):
    frames = simulate(seq, intensity, wobble)
    ANIMS.append({"id": "sq-" + id, "label": label, "category": category, "place": place, "ground": ground,
                  "frames": frames})


# ================================================================== In
anim("drop-in", "Drop In", "in", Seq().fall_from(1.1, 0.42, 1.2).hold(0.05).hop(0.07, sec=0.26, impact=0.5)
     .hold(0.6), place="start")
anim("bounce-in", "Bounce In", "in", Seq().fall_from(1.1, 0.42, 1.3).hop(0.16, sec=0.42, impact=0.8)
     .hop(0.05, sec=0.24, impact=0.4).hold(0.55), place="start")
anim("jump-in", "Jump In", "in", Seq(y=0.9).squat(0.01, 0.0).jump(1.15, rise=0.32, hang=0.1, fall=0.26)
     .hold(0.05).hop(0.05, sec=0.22, impact=0.4).hold(0.5), place="start")
_pop = Seq(zoom=-100).to(0.22, "back", zoom=0)
_pop.impact(0.9)
anim("pop-in", "Pop In", "in", _pop.hold(0.8), place="start", ground=50, wobble=1.4)
anim("slide-in-left", "Slide In Left", "in", Seq(x=-0.75).to(0.45, "out", x=0.03).to(0.28, "inout", x=0.0)
     .hold(0.7), place="start")
anim("slide-in-right", "Slide In Right", "in", Seq(x=0.75).to(0.45, "out", x=-0.03).to(0.28, "inout", x=0.0)
     .hold(0.7), place="start")
anim("dash-in", "Dash In", "in", Seq(x=-0.8).to(0.3, "out", x=0.025).to(0.2, "inout", x=0.0).hold(0.8),
     place="start")
anim("hop-in-left", "Hop In Left", "in",
     Seq(x=-0.6).hop(0.12, dx=0.2, sec=0.32, impact=0.7).hop(0.12, dx=0.2, sec=0.32, impact=0.7)
     .hop(0.12, dx=0.2, sec=0.32, impact=0.8).hold(0.6), place="start")
anim("rise-in", "Rise Up", "in", Seq(y=0.5, op=0).to(0.12, "linear", op=100).to(0.35, "out3", y=-0.03)
     .to(0.25, "inout", y=0.0).hold(0.6), place="start")
anim("spring-in", "Spring Up", "in", Seq(zoom=-100).to(0.01, "linear", zoom=0).squat(0.12, 0.45)
     .jump(0.18, rise=0.18, hang=0.06, fall=0.18).hold(0.6), place="start")

# ================================================================== Out
anim("jump-out", "Jump Out", "out", Seq().hold(0.1).squat(0.22, 0.32).hold(0.06, crouch=-32)
     .jump(1.3, rise=0.38, hang=0.0, fall=0.0, land=False), place="end")
anim("fall-out", "Fall Out", "out", Seq().squat(0.14, 0.12).by(0.12, "out", y=-0.04)
     .by(0.45, "in", y=1.1), place="end")
anim("pop-out", "Pop Out", "out", Seq().to(0.15, "out", zoom=15).to(0.18, "in3", zoom=-100), place="end",
     ground=50)
anim("slide-out-left", "Slide Out Left", "out", Seq().to(0.18, "inout", x=0.03).to(0.38, "in3", x=-0.85),
     place="end")
anim("slide-out-right", "Slide Out Right", "out", Seq().to(0.18, "inout", x=-0.03).to(0.38, "in3", x=0.85),
     place="end")
anim("hop-out-right", "Hop Out Right", "out",
     Seq().squat(0.14, 0.2).hop(0.12, dx=0.25, sec=0.32, impact=0.6).hop(0.14, dx=0.3, sec=0.32, impact=0.6)
     .hop(0.16, dx=0.5, sec=0.34, impact=0.0), place="end")
anim("squash-out", "Squash Down", "out", Seq().squat(0.1, -0.1).squat(0.35, 0.85)
     .to(0.12, "in", op=0), place="end")
anim("launch-out", "Launch and Spin", "out", Seq().squat(0.2, 0.35).hold(0.05, crouch=-35)
     .jump(1.3, rise=0.42, hang=0.0, fall=0.0, spin=420, land=False), place="end")
anim("blow-away", "Blow Away", "out", Seq().to(0.15, "inout", x=-0.02).to(0.6, "in", x=0.9, y=-0.3, rot=60)
     .to(0.01, "linear", op=0), place="end")

# ================================================================== Moves
anim("hop", "Hop", "moves", Seq().squat(0.16, 0.22).hold(0.04, crouch=-22).jump(0.16, rise=0.16, hang=0.08,
     fall=0.16).hold(0.5))
anim("double-hop", "Double Hop", "moves", Seq().squat(0.14, 0.2).jump(0.13, rise=0.15, hang=0.06, fall=0.15)
     .hop(0.11, sec=0.3, impact=0.8).hold(0.5))
anim("hop-forward", "Hop Forward", "moves", Seq().squat(0.16, 0.28).jump(0.16, dx=0.22, rise=0.18, hang=0.08,
     fall=0.18).hold(0.55))
anim("hop-back", "Hop Back", "moves", Seq().squat(0.16, 0.28).jump(0.16, dx=-0.22, rise=0.18, hang=0.08,
     fall=0.18).hold(0.55))
anim("sack-race", "Sack Race", "moves", Seq().squat(0.12, 0.2).hop(0.08, dx=0.08, sec=0.3, impact=0.7)
     .hop(0.08, dx=0.08, sec=0.3, impact=0.7).hop(0.08, dx=0.08, sec=0.3, impact=0.7).hold(0.5))
_fb = Seq().by(0.38, "in", y=0.3)
_fb.impact(1.4)
anim("fall-bounce", "Fall and Bounce", "moves", _fb.hop(0.1, sec=0.34, impact=0.7).hop(0.03, sec=0.2, impact=0.4)
     .hold(0.5))
anim("dash-right", "Dash Right", "moves", Seq().to(0.15, "inout", x=-0.025).to(0.3, "out", x=0.33)
     .to(0.22, "inout", x=0.3).hold(0.6))
anim("dash-left", "Dash Left", "moves", Seq().to(0.15, "inout", x=0.025).to(0.3, "out", x=-0.33)
     .to(0.22, "inout", x=-0.3).hold(0.6))
anim("stumble", "Stumble", "moves", Seq().to(0.2, "in", x=0.05).to(0.12, "out", x=0.08).hold(0.05)
     .to(0.25, "inout", x=0.07).hold(0.6))
anim("inchworm", "Inchworm", "moves", Seq().squat(0.25, 0.3).to(0.25, "out", x=0.05).hold(0.1)
     .squat(0.25, 0.3).to(0.25, "out", x=0.1).hold(0.5))

# ================================================================== Jumps
anim("big-jump", "Big Jump", "jumps", Seq().squat(0.2, 0.32).hold(0.06, crouch=-32)
     .jump(0.42, rise=0.24, hang=0.14, fall=0.24).hop(0.04, sec=0.22, impact=0.4).hold(0.55))
anim("jump-forward", "Jump Forward", "jumps", Seq().squat(0.16, 0.48).jump(0.2, dx=0.28, rise=0.2, hang=0.06,
     fall=0.2).hold(0.6))
anim("trampoline", "Trampoline", "jumps", Seq().squat(0.14, 0.2).jump(0.12, rise=0.14, hang=0.04, fall=0.14)
     .jump(0.26, rise=0.2, hang=0.08, fall=0.2).jump(0.42, rise=0.25, hang=0.12, fall=0.25)
     .hop(0.05, sec=0.22).hold(0.5))
anim("jump-spin", "Jump Spin", "jumps", Seq().squat(0.18, 0.32).jump(0.38, rise=0.24, hang=0.1, fall=0.24,
     spin=360).hold(0.55))
anim("backflip", "Backflip", "jumps", Seq().squat(0.18, 0.32).jump(0.38, rise=0.24, hang=0.1, fall=0.24,
     spin=-360).hold(0.55))
anim("leap-over", "Leap Over", "jumps", Seq().squat(0.16, 0.36).jump(0.3, dx=0.4, rise=0.24, hang=0.08,
     fall=0.24).hold(0.6))
anim("tiny-hops", "Tiny Hops", "jumps", Seq().hop(0.05, sec=0.24, impact=0.5).hop(0.05, sec=0.24, impact=0.5)
     .hop(0.05, sec=0.24, impact=0.5).hop(0.05, sec=0.24, impact=0.5).hold(0.4))
anim("heavy-jump", "Heavy Jump", "jumps", Seq().squat(0.3, 0.42).hold(0.1, crouch=-42)
     .jump(0.18, rise=0.22, hang=0.04, fall=0.16, impact=1.8).hold(0.7), wobble=0.7)
anim("excited-jumps", "Excited Jumps", "jumps", Seq().squat(0.08, 0.15).hop(0.14, sec=0.28, impact=0.9)
     .hop(0.14, sec=0.28, impact=0.9).hop(0.14, sec=0.28, impact=0.9).hold(0.5), wobble=1.3)

# ================================================================== Highlights
anim("pulse", "Pulse", "highlights", Seq().to(0.14, "out", zoom=12).to(0.3, "back", zoom=0).hold(0.4), ground=50)
anim("heartbeat", "Heartbeat", "highlights", Seq().to(0.1, "out", zoom=10).to(0.12, "in", zoom=0)
     .to(0.1, "out", zoom=14).to(0.3, "back", zoom=0).hold(0.4), ground=50)


def jelly(amount, sec):
    seq = Seq()
    seq.impact(amount)
    return seq.hold(sec)


anim("jelly", "Jelly", "highlights", jelly(1.4, 1.4), wobble=1.6)
anim("rubber-band", "Rubber Band", "highlights", Seq().squat(0.16, 0.3).hold(0.04, crouch=-30).hold(0.9),
     wobble=1.5)
anim("tada", "Ta-da", "highlights", Seq().to(0.12, "out", zoom=-8).to(0.14, "out", zoom=12)
     .by(0.08, rot=-4).by(0.08, rot=8).by(0.08, rot=-8).by(0.08, rot=8).by(0.08, rot=-4).to(0.2, "inout", zoom=0)
     .hold(0.3), ground=50)
anim("nod", "Nod", "highlights", Seq().to(0.16, "out", x=0.012).to(0.2, "inout", x=-0.006).to(0.2, "inout", x=0)
     .hold(0.6))
anim("shake-no", "Shake No", "highlights", Seq().by(0.07, x=0.02).by(0.08, x=-0.04).by(0.08, x=0.035)
     .by(0.08, x=-0.025).by(0.08, x=0.01).hold(0.6))
anim("attention", "Attention", "highlights", Seq().squat(0.12, 0.25).jump(0.1, rise=0.12, hang=0.04, fall=0.12)
     .to(0.12, "out", zoom=10).to(0.25, "back", zoom=0).hold(0.4))

# ================================================================== Rotations
anim("spin-squash", "Spin with Squash", "rotations", Seq().squat(0.16, 0.25).to(0.5, "inout", rot=360)
     .hold(0.6), ground=50)
anim("swing", "Swing", "rotations", Seq().to(0.3, "inout", rot=25).to(0.4, "inout", rot=-18)
     .to(0.35, "inout", rot=10).to(0.3, "inout", rot=-4).to(0.25, "inout", rot=0).hold(0.3), ground=0)
anim("topple", "Topple", "rotations", Seq().to(0.4, "in", rot=90).to(0.12, "out", rot=82).to(0.12, "inout", rot=90)
     .hold(0.6))
anim("flip-around", "Flip Around", "rotations", Seq().squat(0.14, 0.25).jump(0.25, rise=0.2, hang=0.08,
     fall=0.2, spin=360).hold(0.5))
anim("wobble-turn", "Wobble Turn", "rotations", Seq().to(0.4, "inout3", rot=200).to(0.2, "inout", rot=172)
     .to(0.18, "inout", rot=184).to(0.16, "inout", rot=180).hold(0.4), ground=50)

# ================================================================== Wiggles (they loop)
def wiggle(beats, sec, **amp):
    seq = Seq()
    for i in range(beats):
        sign = 1 if i % 2 == 0 else -1
        seq.to(sec, "inout", **{k: v * sign for k, v in amp.items()})
    return seq.to(sec, "inout", **{k: 0.0 for k in amp})


anim("wiggle-soft", "Soft Wiggle", "wiggles", wiggle(4, 0.3, x=0.012))
anim("dance", "Dance", "wiggles", Seq().hop(0.03, dx=0.03, sec=0.3, impact=0.5).hop(0.03, dx=-0.03, sec=0.3,
     impact=0.5).hop(0.03, dx=-0.03, sec=0.3, impact=0.5).hop(0.03, dx=0.03, sec=0.3, impact=0.5))
anim("breathe", "Breathe", "wiggles", Seq().squat(0.8, -0.08).squat(0.8, 0.0))
anim("wobble", "Wobble", "wiggles", wiggle(3, 0.25, rot=5), ground=50)
anim("jelly-shake", "Jelly Shake", "wiggles", wiggle(4, 0.12, x=0.008), wobble=1.6)


# ================================================================== Glitch (hard steps)
def glitch(values, sec_per, channel_list):
    seq = Seq()
    for vals in values:
        for k, v in zip(channel_list, vals):
            seq.s[k] = v
        for _ in range(seq.n(sec_per)):
            seq.push(extra={"stretch": vals[-1]} if len(vals) > len(channel_list) else None)
    return seq


anim("glitch-jump", "Glitch Jump", "glitch", glitch([(0, 0, 0), (0.02, 0, 30), (-0.03, -0.02, -20), (0.04, 0, 40),
                                                      (-0.01, 0.01, 0), (0, 0, 0)], 0.07, ["x", "y"]))
anim("glitch-in", "Glitch In", "glitch", glitch([(0.05, 0, 0, 60), (-0.03, 100, 0, -30), (0.02, 0, 0, 40),
                                                  (-0.04, 100, 0, -20), (0.0, 100, 0, 0)], 0.07,
                                                 ["x", "op", "rot"]), place="start")
anim("glitch-out", "Glitch Out", "glitch", glitch([(0, 100, 0, 0), (0.02, 100, 0, 20), (-0.04, 30, 0, -30),
                                                    (0.03, 100, 0, 40), (0.05, 0, 0, 60)], 0.07, ["x", "op", "rot"]),
     place="end")
anim("jitter", "Jitter", "glitch", glitch([(0, 0), (0.006, -0.004), (-0.008, 0.004), (0.004, 0.006),
                                           (-0.006, -0.005), (0.008, 0.002), (0, 0)], 0.07, ["x", "y"]))

ORDER = ["in", "out", "moves", "jumps", "highlights", "rotations", "wiggles", "glitch"]


# ------------------------------------------------------------------ preview (same map as the shader)
def render_strip(a, path, count=14, size=110):
    from PIL import Image, ImageDraw
    frames = a["frames"]
    n = len(frames)
    pick = [int(i * (n - 1) / (count - 1)) for i in range(count)]
    img = Image.new("RGB", (size * count, size * 2), (18, 20, 24))
    d = ImageDraw.Draw(img)
    for c, fi in enumerate(pick):
        f = frames[fi]
        ox = c * size
        groundy = size * 1.6
        d.line([(ox, groundy), (ox + size, groundy)], fill=(70, 70, 70))
        bw = size * 0.36
        gy = a["ground"] / 100
        sy = max(0.05, 1 + f["stretch"] / 100)
        gw, fw = 1 + f["groundWidth"] / 100, 1 + f["farWidth"] / 100
        sh, bu = f["shear"] / 100, f["bulge"] / 100
        z = max(0.0, 1 + f["zoom"] / 100)
        cx = ox + size / 2 + f["x"] * size * 1.0
        base_y = groundy + f["y"] * size * 1.0

        def m(u, v):
            far = max(gy, 1e-4) if v < gy else max(1 - gy, 1e-4)
            t = min(1.0, abs(v - gy) / far)
            w = (gw + (fw - gw) * t) * (1 + bu * 4 * t * (1 - t))
            x = 0.5 + (u - 0.5) * w + sh * t
            y = gy + (v - gy) * sy
            x = 0.5 + (x - 0.5) * z
            y = 0.5 + (y - 0.5) * z
            px, py = (x - 0.5) * bw, (y - 1.0) * bw
            r = math.radians(f["rotation"])
            # turn about the box's centre
            qx, qy = px, py + bw / 2
            rx = qx * math.cos(r) - qy * math.sin(r)
            ry = qx * math.sin(r) + qy * math.cos(r)
            return (cx + rx, base_y + ry - bw / 2)
        pts = [m(i / 8, 0) for i in range(9)] + [m(1, i / 8) for i in range(1, 9)] + \
              [m(1 - i / 8, 1) for i in range(1, 9)] + [m(0, 1 - i / 8) for i in range(1, 8)]
        col = (31, 209, 184) if f["opacity"] > 50 else (20, 90, 80)
        d.polygon(pts, fill=col)
        for u in (0.35, 0.65):
            ex, ey = m(u, 0.35)
            d.ellipse([ex - 2.5, ey - 2.5, ex + 2.5, ey + 2.5], fill=(10, 10, 14))
        d.text((ox + 4, 4), str(fi), fill=(150, 150, 150))
    d.text((4, size * 2 - 14), a["label"], fill=(220, 220, 220))
    img.save(path)


def main():
    preview = None
    if "--preview" in sys.argv:
        preview = sys.argv[sys.argv.index("--preview") + 1]
        os.makedirs(preview, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(OUT):
        if name.endswith(".json"):
            os.remove(os.path.join(OUT, name))
    counters = {}
    total_keys = 0
    for a in ANIMS:
        cat = a["category"]
        counters[cat] = counters.get(cat, 0) + 1
        keys = keys_of(a["frames"])
        total_keys += sum(len(v) for v in keys.values())
        out = {"format": 2, "id": a["id"], "label": a["label"], "category": cat,
               "order": ORDER.index(cat) * 100 + counters[cat],
               "duration": round((len(a["frames"]) - 1) / FPS, 4), "place": a["place"], "ground": a["ground"],
               "keys": keys}
        with open(os.path.join(OUT, a["id"] + ".json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        if preview:
            render_strip(a, os.path.join(preview, a["id"] + ".png"))
    print("%d animations -> %s, %d keys" % (len(ANIMS), os.path.relpath(OUT, ROOT), total_keys))
    for cat in ORDER:
        print("  %-11s %d" % (cat, counters.get(cat, 0)))


if __name__ == "__main__":
    main()
