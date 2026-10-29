"""The engine behind the Animaciones Extremas families (0.26): a particle system drawn as flat cel
tones, frame by frame on twos, with a soft glow, written as Lottie.

Jorge: «repliques todas las de RTFX». Its 1035 elements were studied in their previews (nothing of
them is used). What they are made of, and what this engine draws:
  - particles thrown by emitters: born at a point (or along a moving path), flying with a speed,
    rising (fire, smoke) or falling (liquid), slowing with drag, growing then shrinking to nothing;
  - each particle a stretched blob (along its speed) in three tones — a dark rim, the body, a light
    core — the core drawn smaller on top;
  - a glow: the rim tone again, blurred, behind everything (Lottie's Gaussian Blur, which Skottie
    draws).
Loops: a particle born at time b in a loop of length T is drawn at b and at b - T, so the end meets
the start.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from lottie import Sticker, fill, group, layer_transform, static, transform

STEP = 2


def bez(points, smooth=1.0):
    # Every outline turns the same way round: overlapping outlines of one tone add up instead of
    # cancelling into a hole under the non-zero fill rule (rings are one keyhole outline, so they keep
    # their hole).
    area = sum(points[i - 1][0] * points[i][1] - points[i][0] * points[i - 1][1] for i in range(len(points)))
    if area < 0:
        points = list(points)[::-1]
    n = len(points)
    ins, outs = [], []
    for i in range(n):
        px, py = points[i - 1]
        nx, ny = points[(i + 1) % n]
        tx, ty = (nx - px) * smooth / 6, (ny - py) * smooth / 6
        ins.append([round(-tx), round(-ty)])
        outs.append([round(tx), round(ty)])
    return {"c": True, "v": [[round(x), round(y)] for x, y in points], "i": ins, "o": outs}


class Sharp(list):
    """An outline with straight sides (bolts, shards, lines)."""


def blob(cx, cy, r, seed, rough=0.2, n=12, stretch=(1.0, 1.0), angle=0.0, spikes=0.0, spike_n=0, tail=0.0):
    """A wobbly cel blob round (cx, cy). `tail` draws it out behind like a flame tongue (along -x
    before turning by `angle`)."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.283) for _ in range(4)]
    pts = []
    ca, sa = math.cos(angle), math.sin(angle)
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + rough * (0.6 * math.sin(2 * a + ph[0]) + 0.3 * math.sin(3 * a + ph[1]) + 0.2 * math.sin(5 * a + ph[2]))
        if spikes and spike_n:
            k += spikes * max(0.0, math.cos(spike_n * a + ph[3])) ** 6
        x = math.cos(a) * r * k * stretch[0]
        y = math.sin(a) * r * k * stretch[1]
        if tail and math.cos(a) < 0:
            x *= 1 + tail * (-math.cos(a)) ** 2
            y *= 1 - 0.5 * tail * (-math.cos(a)) ** 2 / (1 + tail)
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return pts


# ------------------------------------------------------------------ particles
@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    born: float
    life: float
    size: float
    seed: int
    lift: float = 0.0       # px/s² upward (negative falls)
    drag: float = 1.5       # 1/s
    grow: float = 0.25      # fraction of life spent growing
    spin: float = 0.0
    shape: str = "flame"    # flame | puff | spark | drop | shard | ring


@dataclass
class Sim:
    """Particles over [0, duration]; `loop` wraps them for a seamless loop."""
    duration: float
    loop: bool = False
    fps: int = 30
    particles: list = field(default_factory=list)

    def add(self, p: Particle):
        self.particles.append(p)

    def state(self, p: Particle, t: float):
        """Where `p` is at time t (None when not alive)."""
        age = t - p.born
        if age < 0 or age > p.life:
            return None
        d = p.drag
        f = (1 - math.exp(-d * age)) / d if d > 1e-6 else age
        x = p.x + p.vx * f
        y = p.y + p.vy * f - 0.5 * p.lift * age * age
        u = age / p.life
        g = min(1.0, u / max(1e-3, p.grow)) if p.grow > 0 else 1.0
        s = p.size * (1 - (1 - g) ** 2) * (1 - u) ** 0.7
        vx = p.vx * math.exp(-d * age)
        vy = p.vy * math.exp(-d * age) - p.lift * age
        return x, y, vx, vy, s, u

    def frame(self, t: float):
        out = []
        for p in self.particles:
            for shift in ((0.0, -self.duration) if self.loop else (0.0,)):
                st = self.state(p, t - shift)
                if st and st[4] > 0.6:
                    out.append((p, st))
        return out


def particle_outline(p: Particle, st, scale, frame_seed):
    x, y, vx, vy, s, u = st
    r = s * scale
    speed = math.hypot(vx, vy)
    ang = math.atan2(vy, vx)
    boil = frame_seed * 7 + p.seed
    if p.shape == "flame":
        # A tongue licking up: drawn out behind its motion (or upwards when slow).
        a = ang if speed > 60 else -math.pi / 2
        return blob(x, y, r, boil, rough=0.28, stretch=(1.0 + min(1.2, speed / 900), 0.85), angle=a,
                    tail=1.1 + min(1.5, speed / 700))
    if p.shape == "puff":
        return blob(x, y, r, boil, rough=0.18)
    if p.shape == "spark":
        ln = 1.0 + min(5.0, speed / 160)
        return blob(x, y, r * 0.55, p.seed, rough=0.0, stretch=(ln, 0.55), angle=ang)
    if p.shape == "drop":
        return blob(x, y, r, p.seed, rough=0.06, stretch=(1.0 + min(1.0, speed / 900), 0.85), angle=ang, tail=0.6)
    if p.shape == "shard":
        rnd = random.Random(p.seed)
        rot = p.spin * (u * p.life) + rnd.uniform(0, 6.28)
        pts = [(x + math.cos(rot + k * 2.1 + rnd.uniform(-0.3, 0.3)) * r * rnd.uniform(0.6, 1.3),
                y + math.sin(rot + k * 2.1 + rnd.uniform(-0.3, 0.3)) * r * rnd.uniform(0.6, 1.3)) for k in range(3)]
        return Sharp(pts)
    return blob(x, y, r, boil, rough=0.2)


# ------------------------------------------------------------------ writing
GLOW_BLUR = 28


def gaussian_blur(amount):
    return {"ty": 29, "nm": "Gaussian Blur", "np": 5, "mn": "ADBE Gaussian Blur 2", "ix": 1, "en": 1,
            "ef": [{"ty": 0, "nm": "Blurriness", "mn": "ADBE Gaussian Blur 2-0001", "ix": 1, "v": static(amount)},
                   {"ty": 7, "nm": "Blur Dimensions", "mn": "ADBE Gaussian Blur 2-0002", "ix": 2, "v": static(1)},
                   {"ty": 7, "nm": "Repeat Edge Pixels", "mn": "ADBE Gaussian Blur 2-0003", "ix": 3, "v": static(0)}]}


class Layers:
    """Tone layers with a fixed number of path slots, keyed on twos; hold keys."""

    def __init__(self, sticker: Sticker, tones, slots, glow=True, glow_blur=GLOW_BLUR, glow_tone=0, glow_opacity=80):
        self.s = sticker
        self.tones = [(sticker.slot(sid, colour), colour) for sid, colour in tones]
        self.slots = slots
        self.glow = glow
        self.glow_blur = glow_blur
        self.glow_tone = glow_tone
        self.glow_opacity = glow_opacity
        self.keys = {k: [] for k in range(len(tones))}

    def draw(self, frame, tone, outlines):
        self.keys[tone].append((frame, outlines[: self.slots]))

    def _paths(self, keyed):
        paths = []
        for slot in range(self.slots):
            shapes = []
            for _, outs in keyed:
                if slot < len(outs):
                    o = outs[slot]
                    shapes.append(bez(o, 0.0 if isinstance(o, Sharp) else 1.0))
                else:
                    shapes.append(None)
            if not any(shapes):
                continue
            n = max(len(sh["v"]) for sh in shapes if sh)
            ks = []
            for (frame, _), sh in zip(keyed, shapes):
                if sh is None:
                    sh = {"c": True, "v": [[-9999, -9999]] * n, "i": [[0, 0]] * n, "o": [[0, 0]] * n}
                elif len(sh["v"]) < n:
                    e = n - len(sh["v"])
                    sh = {"c": True, "v": sh["v"] + [sh["v"][-1]] * e, "i": sh["i"] + [[0, 0]] * e,
                          "o": sh["o"] + [[0, 0]] * e}
                ks.append({"t": frame, "s": [sh], "h": 1})
            paths.append({"ty": "sh", "ks": {"a": 1, "k": ks} if len(ks) > 1 else static(ks[0]["s"][0])})
        return paths

    def build(self):
        order = list(range(len(self.tones)))
        if self.glow and self.keys[self.glow_tone]:
            sid, colour = self.tones[self.glow_tone]
            lay = self.s.layer(group(*self._paths(self.keys[self.glow_tone]), fill(colour, sid, o=self.glow_opacity),
                                     tr=transform()), ks=layer_transform((0, 0)), name="resplandor")
            lay["ef"] = [gaussian_blur(self.glow_blur)]
        for tone in order:
            keyed = self.keys[tone]
            if not keyed:
                continue
            sid, colour = self.tones[tone]
            paths = self._paths(keyed)
            if paths:
                self.s.layer(group(*paths, fill(colour, sid), tr=transform()), ks=layer_transform((0, 0)),
                             name=f"tono {tone + 1}")


def render_sim(sticker: Sticker, sim: Sim, tones, scales=(1.0, 0.7, 0.4), slots=40, glow=True, glow_blur=GLOW_BLUR,
               extra=None):
    """Draws `sim` into `sticker`: one layer per tone (each particle at that tone's scale), plus the glow.
    `extra(frame, t)` may return {tone: [outlines]} drawn before the particles (bodies, rings)."""
    lay = Layers(sticker, tones, slots, glow=glow, glow_blur=glow_blur)
    frames = sticker.frames
    for f in range(0, frames, STEP):
        t = f / sticker.fps
        alive = sim.frame(t)
        # Big ones first so they stay when the slots run out.
        alive.sort(key=lambda ps: -ps[1][4])
        pre = extra(f, t) if extra else {}
        for tone, sc in enumerate(scales[: len(tones)]):
            outs = list(pre.get(tone, []))
            for p, st in alive:
                outs.append(particle_outline(p, st, sc, f // STEP))
            lay.draw(f, tone, outs)
    lay.build()
    return sticker


def new(id, es, en, cat, frames, order, tags, loop=False, size=512, height=0, thumb=None):
    s = Sticker(id, es, en, "extremas-" + cat, frames=frames, order=order, tags=tags + ["extremas", "anime", "cartoon"],
                loop=loop, size=size, height=height)
    s.thumb = thumb if thumb is not None else (0.5 if loop else 0.3)
    return s
