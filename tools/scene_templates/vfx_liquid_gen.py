"""Liquid VFX of our own (Jorge, 2026-11-16: the RTFX look, drawn from scratch so we can ship it).

The six liquid families studied from RTFX (vfx_liquid_rtfx2.py) taught the look: a flat turquoise body with a light
rim, dark pockets low and right and where drops meet, a white shine up and left, drawn on twos. Nothing here is traced:
each piece comes out of a small simulation of our own —

- drops (particles) with a radius, thrown by a recipe per family and pulled by gravity and drag;
- elastic threads between drops that stretch, thin out (they keep their volume) and snap past a length, so a column
  necks and breaks into drops by itself;
- the liquid is the metaball field of drops and threads (they melt into each other where they touch);
- the dark side, the pockets and the shine come from that field and the shape, not from any picture.

Every frame gives three masks (liquid, dark, shine) that vfx_liquid_rtfx2's drawing turns into our shapes (a clipping
group: body with its rim, pockets and shine inside it), one drawing every 2 frames. A seed gives another piece of the
same family.

    py tools/scene_templates/vfx_liquid_gen.py --preview            # quick masks-only sheets, no app
    py tools/scene_templates/vfx_liquid_gen.py --exe <0.32 flipstudio.exe> [--only chorro,goteo] [--seed 3]

Output in E:\\FlipStudio\\tienda\\vfx-estudio\\liquido\\propios.
"""

from __future__ import annotations

import argparse
import math
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

import vfx_demo
from scene import Box, Template
from vfx_liquid_rtfx2 import BODY, DARK, K, RIM, SHINE, crops, outlines, page_frames, part, svg_of

OUT = Path(r"E:\FlipStudio\tienda\vfx-estudio\liquido\propios")
FPS = 30
FOAM, FOAM_RIM = "#f4fbfc", "#bfe0e6"
EMPTY = "M 0 0 L 0.01 0 L 0.01 0.01 Z"
ON = 2   # a new drawing every ON frames (animated on twos)


# --------------------------------------------------------------------------------------------- simulation
# What the study found (docs/plan-vfx.md, «Líquidos propios»): water never vanishes at once — every piece shrinks in
# proportion (8–10 % of the area a frame) while it splits into smaller drops; a thread that snaps leaves a satellite
# drop in its neck and the rest springs back; a falling drop stretches, and after it lets go it wobbles; on the
# ground it flattens into a puddle that spreads and draws back, throwing droplets in arcs that fade in turn.
@dataclass
class Drop:
    x: float
    y: float
    vx: float
    vy: float
    r: float
    born: int = 0          # frame it appears
    shrink: float = 0.0    # radius lost per frame once older than `hold`
    hold: int = 10**6
    pinned: bool = False   # a lip that stays put (goteo)
    drag: float = 0.02
    fade: float = 1.0      # radius kept per frame once older than `hold` (0.95 is about 10 % of the area a frame)
    grow: float = 0.0      # radius gained per frame until `grow_until` frames old (a hanging drop filling up)
    grow_until: int = 0
    sx: float = 1.0        # shape: >1 wider, set each frame from the motion, the wobble and the floor
    sy: float = 1.0
    wobble: float = 0.0    # amplitude of the oscillation after letting go (decays)
    wobble_t: int = 0
    on_floor: bool = False
    spread: float = 0.0    # puddle: how far it has flattened
    weight: float = 1.0    # gravity multiplier: a heavy tip stretches the thread it hangs from like elastic
    foam: bool = False     # white foam (its own layer, over the water, not clipped): cascade foam, ripples


@dataclass
class Thread:
    a: int
    b: int
    rest: float
    snap: float = 2.2      # breaks past rest * snap
    pull: float = 0.06     # how hard it pulls the drops back together
    alive: bool = True
    satellite: bool = True  # a small drop is left in the neck when it snaps
    recoil: float = 0.9     # how hard both ends spring back when it snaps (elastic: more)


@dataclass
class Sim:
    w: int
    h: int
    frames: int
    gravity: float = 0.35
    floor: float | None = None   # the ground (y), or none
    drops: list = field(default_factory=list)
    threads: list = field(default_factory=list)
    hooks: list = field(default_factory=list)   # f(sim, frame) run before each step
    ones_until: int = 0          # drawn on ones (every frame) from ones_from to before this frame, on twos else
    ones_from: int = 0
    palette: tuple | None = None  # (body, dark, shine, rim) for another water than the turquoise
    skip: int = 0                 # frames simulated before the recording starts (a loop that opens already full)
    raster: object = None         # f -> (liquid, foam) masks drawn directly (a shape that stays: cascade, wave)
    rng: np.random.Generator = field(default_factory=lambda: np.random.default_rng(0))

    def add(self, *a, **k) -> int:
        self.drops.append(Drop(*a, **k))
        return len(self.drops) - 1

    def link(self, a, b, **k):
        d = math.dist((self.drops[a].x, self.drops[a].y), (self.drops[b].x, self.drops[b].y))
        self.threads.append(Thread(a, b, max(d, 1.0), **k))

    def live(self, d: Drop, f: int) -> bool:
        return f >= d.born and d.r > 0.6

    def threads_of(self, i: int):
        return [t for t in self.threads if t.alive and (t.a == i or t.b == i)]

    def _snap(self, t: Thread, f: int):
        t.alive = False
        a, b = self.drops[t.a], self.drops[t.b]
        if t.satellite and min(a.r, b.r) > 3.0:
            # The neck breaks next to the big drop and, before it springs back, near the other end: a satellite.
            u = 0.45 + 0.1 * float(self.rng.random())
            self.drops.append(Drop(a.x + u * (b.x - a.x), a.y + u * (b.y - a.y), 0.5 * (a.vx + b.vx),
                                   0.5 * (a.vy + b.vy), 0.32 * min(a.r, b.r), born=f, hold=2, fade=0.9, drag=0.02))
        # Both ends spring back toward themselves, and whichever is now loose wobbles.
        dx, dy = b.x - a.x, b.y - a.y
        dist = math.hypot(dx, dy) or 1.0
        for i, d, s in ((t.a, a, -1.0), (t.b, b, 1.0)):
            if not d.pinned:
                d.vx += s * t.recoil * dx / dist
                d.vy += s * t.recoil * dy / dist
            if not self.threads_of(i):
                d.wobble, d.wobble_t = 0.28, f

    def _impact(self, d: Drop, f: int):
        """A drop reaching the ground: a puddle that spreads and draws back, droplets thrown out by the speed."""
        v = max(d.vy, 0.0)
        d.on_floor = True
        d.y = self.floor - 0.3 * d.r
        d.vx *= 0.25
        d.vy = 0.0
        d.spread = 0.0
        d.hold = min(d.hold, f - d.born + 3)
        d.fade = min(d.fade, 0.93)
        n = int(min(8, v / 2.2))
        for k in range(n):
            side = -1 if k % 2 == 0 else 1
            ang = math.radians(float(self.rng.uniform(35, 75)))
            sp = v * float(self.rng.uniform(0.35, 0.6))
            self.drops.append(Drop(d.x + side * 0.9 * d.r, self.floor - 0.6 * d.r, side * sp * math.cos(ang),
                                   -sp * math.sin(ang), d.r * float(self.rng.uniform(0.18, 0.32)), born=f, hold=3,
                                   fade=0.92, drag=0.02, foam=d.foam))

    def step(self, f: int):
        for hook in self.hooks:
            hook(self, f)
        for t in self.threads:
            if not t.alive:
                continue
            a, b = self.drops[t.a], self.drops[t.b]
            if not (self.live(a, f) and self.live(b, f)):
                continue
            dx, dy = b.x - a.x, b.y - a.y
            dist = math.hypot(dx, dy) or 1e-6
            if dist > t.rest * t.snap:
                self._snap(t, f)
                continue
            # Water that thin cannot hold: once either end has shrunk to a speck the thread lets go (otherwise a
            # fading neck lingers as a hairline).
            if min(a.r, b.r) < 2.6 and t.rest < 999:
                sat, t.satellite = t.satellite, False
                self._snap(t, f)
                t.satellite = sat
                continue
            # A thread pulls both ends back toward its rest length (surface tension), never pushes them apart.
            if dist > t.rest:
                k = t.pull * (dist - t.rest) / dist
                for d, s in ((a, 1.0), (b, -1.0)):
                    if not d.pinned:
                        d.vx += s * k * dx * 0.5
                        d.vy += s * k * dy * 0.5
        for d in list(self.drops):
            if not self.live(d, f) or d.pinned:
                continue
            if d.on_floor:
                # The puddle flattens out fast, then draws back as it shrinks.
                d.spread = min(1.0, d.spread + 0.35)
                d.x += d.vx
                d.vx *= 0.8
                continue
            d.vy += self.gravity * d.weight
            d.vx *= 1.0 - d.drag
            d.vy *= 1.0 - d.drag
            d.x += d.vx
            d.y += d.vy
            if self.floor is not None and d.vy > 0 and d.y + d.r * d.sy >= self.floor:
                self._impact(d, f)
        for d in self.drops:
            age = f - d.born
            if d.grow and 0 <= age < d.grow_until:
                d.r += d.grow
            if age > d.hold:
                d.r = max(0.0, d.r * d.fade - d.shrink)
                if d.r < 3.0:
                    d.r *= 0.82   # the last specks go quicker: they read as dust, not water
            # The shape: stretched along a fast fall, wobbling after letting go, flat on the ground.
            if d.on_floor:
                d.sx = 1.0 + 1.3 * d.spread * (0.6 + 0.4 * min(1.0, d.r / 8.0))
                d.sy = 0.5
            else:
                speed = math.hypot(d.vx, d.vy)
                st = 1.0 + min(0.35, 0.02 * speed) if not d.pinned else 1.0
                if d.wobble:
                    t = f - d.wobble_t
                    st *= 1.0 + d.wobble * math.exp(-t / 9.0) * math.cos(t * 0.7)
                d.sy, d.sx = st, 1.0 / math.sqrt(st)

    def field(self, f: int, scale: float = 1.0, foam: bool = False):
        """The metaball field on a w x h grid (1 = the liquid's edge), of the water or of the foam drops."""
        H, W = int(self.h * scale), int(self.w * scale)
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float32) / scale
        fld = np.zeros((H, W), np.float32)
        for d in self.drops:
            if not self.live(d, f) or d.foam != foam:
                continue
            fld += d.r * d.r / (((xs - d.x) / d.sx) ** 2 + ((ys - d.y) / d.sy) ** 2 + 1e-3)
        for t in self.threads:
            if not t.alive:
                continue
            a, b = self.drops[t.a], self.drops[t.b]
            if not (self.live(a, f) and self.live(b, f)) or a.foam != foam or b.foam != foam:
                continue
            dx, dy = b.x - a.x, b.y - a.y
            dist2 = dx * dx + dy * dy
            if dist2 < 1e-6:
                continue
            # The thread keeps its volume: the longer, the thinner (the neck before a drop lets go).
            r = 0.62 * min(a.r, b.r) * min(1.0, math.sqrt(t.rest / math.sqrt(dist2)))
            u = np.clip(((xs - a.x) * dx + (ys - a.y) * dy) / dist2, 0.0, 1.0)
            px, py = a.x + u * dx, a.y + u * dy
            fld += r * r / ((xs - px) ** 2 + (ys - py) ** 2 + 1e-3)
        if self.floor is not None:
            fld[int(self.floor * scale) + 1:, :] = 0.0   # nothing below the ground
        return fld


# ------------------------------------------------------------------------------------------------ recipes
def chorro(rng: np.random.Generator):
    """A column shot up from the ground: up in three frames (drawn on ones), it slows and hangs, its necks thin and
    snap (satellites between the bulges), and the pieces fall back, splash on the ground and fade away."""
    s = Sim(170, 340, 46, gravity=1.0, floor=332.0, ones_until=5, rng=rng)
    sway, phase = rng.uniform(0.6, 1.2), rng.uniform(0, 2 * math.pi)
    sizes = [rng.uniform(15, 19) if i in (1, 5, 9) else rng.uniform(5.5, 7.5) for i in range(12)]
    prev = None
    for i in range(12):
        # The first out is the fastest: the head flies on, the tail falls back, the middle stretches.
        speed = 17.5 - 1.1 * (11 - i) + rng.uniform(-0.3, 0.3)
        # Stacked from the ground up and shown a third at a time: the column shoots up in three frames.
        idx = s.add(85 + 6 * math.sin(phase + i * 0.7), 322 - 14 * i, sway * math.sin(phase + i * 0.9), -speed,
                    sizes[i], born=i // 4,
                    hold=11 + i // 3, fade=0.945, drag=0.012)
        if prev is not None:
            s.link(prev, idx, snap=rng.uniform(1.45, 1.8), pull=0.008)
        prev = idx
    return s


def goteo(rng: np.random.Generator):
    """Liquid that drips like elastic (Jorge, 2026-11-16: «que caiga como elástico y se rompa»): a thin tongue with a
    heavy bulb at its tip stretches far down from the body before the bulb lets go and the rest springs back up; then
    the body itself lets go and falls, stretching into a string of bulbs with thin necks that part into drops, while
    the two ends left on top stretch into arms that snap and draw back to their sides. Drops splash on the ground;
    everything shrinks away little by little."""
    s = Sim(240, 520, 94, gravity=0.62, floor=505.0, rng=rng)
    cx = 120 + rng.uniform(-12, 12)
    # The body: a fat lump of liquid on top, its middle over the drip.
    body = []
    for i in range(9):
        x = cx - 64 + i * 16 + rng.uniform(-1.5, 1.5)
        centre = abs(i - 4) <= 1
        # A rounded lump: fuller in the middle but no lower, so it does not start as a downward point.
        body.append(s.add(x, 70 + rng.uniform(-1.5, 1.5), 0, 0,
                          (15.0 if centre else 12.5 + 1.2 * (abs(i - 4) <= 2)) + rng.uniform(-1, 1), pinned=True,
                          hold=66, fade=0.93,
                          drag=0.06))
    for a, b in zip(body, body[1:]):
        s.link(a, b, snap=3.2, pull=0.05, recoil=2.2)
    # Hidden in the middle of the body: drops stacked under one another, heavier toward the bottom. When the body
    # lets go they pull apart like elastic into a string of bulbs and necks that part one by one.
    column, prev_c, sizes_full = [], body[4], []
    for i, (r, w) in enumerate(((14.5, 1.0), (13.0, 1.12), (12.0, 1.25), (11.0, 1.4), (10.0, 1.6))):
        # Small and inside the body until it lets go (full size, it pushed the body into a downward point).
        full = r + rng.uniform(-0.8, 0.8)
        idx = s.add(s.drops[body[4]].x + rng.uniform(-1, 1), 70 + 2 * i, 0, 0, 0.45 * full,
                    pinned=True, drag=0.03, hold=10**6, fade=0.95)
        s.drops[idx].weight = w
        sizes_full.append(full)
        s.link(prev_c, idx, snap=3.4 + 0.3 * rng.random(), pull=0.05, recoil=2.0)
        column.append(idx)
        prev_c = idx
    # The tongue: a string of thin drops hanging from the middle, a bulb at its tip that fills up and pulls.
    prev = body[4]
    tongue = []
    for i in range(7):
        r = 7.5 - 0.35 * i
        # Gathered inside the body at first (their rest length set apart): the bulb pulls them out one by one, so
        # the tongue grows out of the lump instead of starting as a point under it.
        idx = s.add(s.drops[body[4]].x + rng.uniform(-0.8, 0.8), 74 + 1.5 * i, 0, 0, r, drag=0.08, hold=60, fade=0.93)
        s.link(prev, idx, snap=4.2, pull=0.32 - 0.03 * i, recoil=2.0, satellite=i > 3)
        s.threads[-1].rest = 7.0
        tongue.append(idx)
        prev = idx
    tip = s.add(s.drops[body[4]].x, 86, 0, 0, 8.0, grow=0.36, grow_until=18, weight=1.6, drag=0.02, hold=10**6,
                fade=0.95)
    s.link(prev, tip, snap=3.0, pull=0.12, recoil=2.4)
    s.threads[-1].rest = 9.0

    def let_go(sim, f):
        # A beat after the bulb has gone, the middle of the body lets go too and falls stretching; its ends stay.
        if f == 30:
            sim.drops[body[4]].pinned = False
            for i, full in zip(column, sizes_full):
                d = sim.drops[i]
                d.pinned = False
                # It fills out to its size over a few frames as it pulls away.
                # (grow runs while age < grow_until, age counted from its birth: six more frames from now)
                d.grow, d.grow_until = (full - d.r) / 6.0, (f - d.born) + 6
            # The falling middle thins into bulbs and necks: its threads to the ends become long elastic arms.
            for t in sim.threads:
                if t.a in body and t.b in body:
                    t.snap, t.pull = 3.6, 0.03
            for i in tongue:
                sim.drops[i].weight = 1.15
        if f == 54:
            for i in (2, 3, 5, 6):
                sim.drops[body[i]].pinned = False
    s.hooks.append(let_go)
    return s


def _splash_sheets(s: Sim, cx: float, floor: float, f: int, rng: np.random.Generator, power: float = 1.0):
    """The splash itself: two sheets thrown out sideways from where the drop hit, their thick rim tearing into
    droplets, a few droplets flung off at once (prompt splash), a short bump in the middle."""
    for side in (-1, 1):
        prev = None
        n = 9
        for i in range(n):
            u = i / (n - 1)
            ang = math.radians(90 - side * (8 + 32 * u) + rng.uniform(-3, 3))
            sp = (9.0 + 8.0 * u) * rng.uniform(0.92, 1.08) * power
            r = ((9.5 + 6.0 * u * u) * rng.uniform(0.85, 1.1) if i < n - 1 else rng.uniform(13, 16)) * power
            idx = s.add(cx + side * 6 * u, floor - 5 - 4 * u, sp * math.cos(ang), -sp * math.sin(ang), r,
                        born=f + i // 4, hold=7 + i // 3, fade=0.93, drag=0.035)
            if prev is not None:
                s.link(prev, idx, snap=rng.uniform(1.5, 2.1), pull=0.02, recoil=1.2)
            prev = idx
        for k in range(3):
            ang = math.radians(90 - side * rng.uniform(40, 60))
            sp = rng.uniform(13, 17) * power
            s.add(cx + side * 8, floor - 9, sp * math.cos(ang), -sp * math.sin(ang), rng.uniform(4, 6.5) * power,
                  born=f + 1, hold=6, fade=0.92, drag=0.02)
    s.add(cx, floor - 5, 0, -3.0, 16 * power, born=f, hold=3, fade=0.88, drag=0.2)


def salpicadura(rng: np.random.Generator):
    """A drop falls from above, hits the ground, and the splash opens there: two sheets thrown out sideways, their
    rims tearing into droplets that fall back, splash in turn and fade away (a story: cause, splash, the end)."""
    floor = 305.0
    s = Sim(440, 360, 42, gravity=0.7, floor=floor, rng=rng)
    cx = 220 + rng.uniform(-10, 10)
    # The cause: a drop falling into the frame, stretched by its speed.
    drop = s.add(cx, 20, 0, 9.0, 13.0, drag=0.0)
    s.drops[drop].weight = 1.4
    state = {"done": False}

    def hit(sim, f):
        d = sim.drops[drop]
        if not state["done"] and d.y + d.r * d.sy >= floor - 4:
            state["done"] = True
            d.r = 0.0                                   # it becomes the splash
            sim.ones_from, sim.ones_until = f, f + 4    # the burst drawn on ones
            _splash_sheets(sim, d.x, floor, f, rng)
    s.hooks.append(hit)
    return s


def racimo(rng: np.random.Generator):
    """A lump of liquid thrown in from one side: as it flies its lobes pull apart (a Y), the necks stretch thin and
    snap, and the drops fly on in an arc, round up and shrink away."""
    s = Sim(320, 240, 30, gravity=0.18, rng=rng)
    cx, cy = 40.0, 150 + rng.uniform(-6, 6)
    throw_x, throw_y = rng.uniform(7.0, 8.0), rng.uniform(-4.2, -3.6)
    core = s.add(cx, cy, throw_x, throw_y, rng.uniform(24, 27), hold=12, fade=0.92, drag=0.025)
    base = rng.uniform(0, 2 * math.pi)
    for i in range(3):
        a = base + i * 2 * math.pi / 3 + rng.uniform(-0.25, 0.25)
        dist, sp = rng.uniform(26, 32), rng.uniform(1.9, 2.6)
        lobe = s.add(cx + dist * math.cos(a), cy + dist * math.sin(a), throw_x + sp * math.cos(a),
                     throw_y + sp * math.sin(a), rng.uniform(15, 20), hold=12, fade=0.92, drag=0.025)
        prev = core
        for j, u in enumerate((0.38, 0.68)):
            nk = s.add(cx + u * dist * math.cos(a), cy + u * dist * math.sin(a), throw_x + u * sp * math.cos(a),
                       throw_y + u * sp * math.sin(a), rng.uniform(9, 11) * (1 - 0.2 * j), hold=10, fade=0.9,
                       drag=0.025)
            s.link(prev, nk, snap=rng.uniform(1.5, 1.8), pull=0.03, recoil=1.4)
            prev = nk
        s.link(prev, lobe, snap=rng.uniform(1.5, 1.8), pull=0.03, recoil=1.4)
    return s


def anillo(rng: np.random.Generator):
    """Seen from above: a drop falls toward the ground (it grows as it comes closer), hits a thin film of water and
    the impact throws out a ring, thicker in places, that tears into arcs, dashes and specks; a little of the drop
    stays in the middle and fades."""
    s = Sim(280, 280, 30, gravity=0.0, rng=rng)
    cx, cy = 140.0, 140.0
    drop = s.add(cx, cy, 0, 0, 5.0, grow=1.6, grow_until=7, drag=0.0)
    state = {"done": False}

    def hit(sim, f):
        if state["done"] or f < 7:
            return
        state["done"] = True
        d = sim.drops[drop]
        r_hit = d.r
        d.r, d.grow = 0.62 * r_hit, 0.0
        d.hold, d.fade = 0, 0.9                       # what is left in the middle shrinks away
        sim.ones_from, sim.ones_until = f, f + 4
        n = 40
        ids = []
        spin = rng.uniform(0.01, 0.03) * (1 if rng.random() < 0.5 else -1)
        p1, p2 = rng.uniform(0, 2 * math.pi), rng.uniform(0, 2 * math.pi)
        for i in range(n):
            a = 2 * math.pi * i / n
            thick = 4.2 + 2.0 * math.sin(3 * a + p1) + 1.2 * math.sin(5 * a + p2)
            r0, out = r_hit * 0.9, rng.uniform(8.0, 9.5)
            ids.append(sim.add(cx + r0 * math.cos(a), cy + r0 * math.sin(a),
                               out * math.cos(a) - spin * r0 * math.sin(a), out * math.sin(a) + spin * r0 * math.cos(a),
                               max(2.2, thick), born=f, hold=4, fade=0.88, drag=0.16))
        for i in range(n):
            sim.link(ids[i], ids[(i + 1) % n], snap=rng.uniform(1.25, 1.7), pull=0.01, recoil=0.6, satellite=False)
    s.hooks.append(hit)
    return s


def gota(rng: np.random.Generator):
    """A drop thrown up out of a little puddle (Jorge, 2026-11-16: «no entiendo si el agua cae o si la tiran de
    abajo a arriba», and at the top it looked like it hit something): the puddle is there from the start, a jet rises
    out of it still joined to it (a Worthington jet), lets go of the puddle, its round head slows to a stop at the top
    — no flattening, nothing up there — and falls back speeding up, the tail breaking into droplets on the way, all of
    it landing in the puddle with a small splash and fading away."""
    floor = 268.0
    s = Sim(150, 290, 50, gravity=1.15, floor=floor, ones_until=4, rng=rng)
    # The puddle: flat drops on the ground from the first frame.
    puddle = []
    for dx, r in ((-22, 9.0), (0, 12.0), (22, 9.0)):
        d = s.add(75 + dx + rng.uniform(-2, 2), floor - 0.3 * r, 0, 0, r, hold=36, fade=0.93)
        s.drops[d].on_floor, s.drops[d].spread = True, 1.0
        puddle.append(d)
    # The jet: stacked on the puddle, the top one fastest; its foot stays in the puddle for a few frames.
    v = rng.uniform(18.5, 19.5)
    ids = []
    for i in range(6):
        r = 9.5 if i == 0 else 7.2 - 0.6 * i
        d = s.add(75 + rng.uniform(-0.5, 0.5), floor - 14 - 7 * (5 - i), rng.uniform(-0.15, 0.15),
                  -(v - 2.3 * i), r, hold=20 if i else 10**6, fade=0.92, drag=0.008)
        ids.append(d)
        if i:
            s.link(ids[i - 1], d, snap=rng.uniform(2.4, 2.9), pull=0.025, recoil=1.0)
    foot = ids[-1]
    s.drops[foot].pinned = True
    s.link(puddle[1], foot, snap=9.0, pull=0.05, satellite=False)
    head = s.drops[ids[0]]
    head.grow, head.grow_until = 0.55, 8

    def lift(sim, f):
        # The foot lets go of the puddle once the jet has stretched out of it.
        if f == 5:
            sim.drops[foot].pinned = False
            sim.drops[foot].vy = -4.0
        # The head fades only after it has fallen back into the puddle (on_floor turns its fade on).
    s.hooks.append(lift)
    return s


BLUE = ("#3c9ed0", "#1f6a98", "#e8f6ff", "#8fcbe8")   # the cascade's water: deeper blue


def _bez(p0, p1, p2, s):
    a = (1 - s) * (1 - s)
    b = 2 * (1 - s) * s
    c = s * s
    return (a * p0[0] + b * p1[0] + c * p2[0], a * p0[1] + b * p1[1] + c * p2[1])


def _bez_d(p0, p1, p2, s):
    return (2 * (1 - s) * (p1[0] - p0[0]) + 2 * s * (p2[0] - p1[0]),
            2 * (1 - s) * (p1[1] - p0[1]) + 2 * s * (p2[1] - p1[1]))


def cascada(rng: np.random.Generator):
    """A spout pouring without end (a loop): thin at the spout at the top right, the water curves down and spreads
    into a horn-shaped curtain; bands of white foam with a scalloped lower edge run down across it; at the foot it
    boils into white foam; little splashes at the spout. Drawn from its centre line (not drops): the shape stays,
    the foam runs — as a pour does."""
    W_, H_ = 270, 430
    period = 36                                          # frames for the foam to move one band down: the loop
    s = Sim(W_, H_, 2 * period, gravity=0.5, floor=420.0, rng=rng)
    s.palette = BLUE
    s.skip = 14                                          # the spray and the falling drops already going
    p0, p1, p2 = (236.0, 42.0), (92.0, 52.0), (98.0, 372.0)
    blobs = [(rng.uniform(-0.45, 0.45), rng.uniform(0, 1), rng.uniform(7, 15)) for _ in range(12)]
    specks = [(rng.uniform(0, 1), rng.uniform(-1, 1)) for _ in range(4)]

    def frame(f):
        liquid = np.zeros((H_, W_), np.uint8)
        foam = np.zeros((H_, W_), np.uint8)
        t = (f % period) / period
        N = 70

        def edge_pt(si, w, wob=0.0):
            x, y = _bez(p0, p1, p2, si)
            dx, dy = _bez_d(p0, p1, p2, si)
            n = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / n, dx / n
            width = 7 + 112 * si ** 1.2
            k = (w - 0.5) * width + wob
            return x + nx * k, y + ny * k

        wob = lambda si, side: 2.2 * math.sin(11 * si - 2 * math.pi * f / period + side) * si
        left = [edge_pt(i / N, 0.0, wob(i / N, 0.0)) for i in range(N + 1)]
        right = [edge_pt(i / N, 1.0, wob(i / N, 1.7)) for i in range(N + 1)]
        poly = np.array(left + right[::-1], np.int32)
        cv2.fillPoly(liquid, [poly], 1)
        # The bands of foam running down: one every 0.2 of the length, a band a frame-exact loop.
        for kb in range(-1, 7):
            st = 0.12 + 0.2 * (kb + t)
            if st < 0.1 or st > 0.9:
                continue
            h = 0.03 + 0.025 * st
            # Both edges wavy; the lower one hangs in tongues (longer lower down).
            top = [edge_pt(st - 0.012 * math.sin(2.6 * math.pi * (w / 16) + kb * 1.3), w / 16) for w in range(17)]
            bottom = []
            for w in range(16, -1, -1):
                ww = w / 16
                drip = 0.045 * max(0.0, math.sin(3.6 * math.pi * ww + kb * 0.9)) ** 1.6 * (0.5 + 1.0 * st)
                bottom.append(edge_pt(min(1.0, st + h + drip), ww))
            cv2.fillPoly(foam, [np.array(top + bottom, np.int32)], 1)
        # The foot: the last of the curtain is foam, and it boils into blobs that pulse with the loop.
        foot_top = [edge_pt(0.9 - 0.015 * math.sin(3 * math.pi * w / 16 + 2 * math.pi * t), w / 16) for w in range(17)]
        foot_bot = []
        for w in range(16, -1, -1):
            ww = w / 16
            tongue = 0.045 * max(0.0, math.sin(4.2 * math.pi * ww + 2 * math.pi * t)) ** 1.5
            foot_bot.append(edge_pt(1.0, ww)[0:1] + (edge_pt(1.0, ww)[1] + 260 * tongue,))
        cv2.fillPoly(foam, [np.array(foot_top + foot_bot, np.int32)], 1)
        bx, by = _bez(p0, p1, p2, 1.0)
        foam &= cv2.dilate(liquid, np.ones((3, 3), np.uint8)) | (np.arange(H_)[:, None] > by - 26)
        return liquid.astype(bool), foam.astype(bool)
    def physics(sim, f):
        # Where the water is born: a fan of droplets and spikes flung out of the spout every frame.
        dx, dy = _bez_d(p0, p1, p2, 0.0)
        base = math.atan2(dy, dx)
        for _ in range(3):
            # Born already apart from the stream (or they melt into it and the spout looks like a trumpet).
            a = base + math.pi + rng.uniform(-1.5, 1.5) if rng.random() < 0.6 else base + rng.uniform(-1.4, 1.4)
            sp = rng.uniform(2.5, 5.0)
            off = rng.uniform(9, 14)
            sim.add(p0[0] + off * math.cos(a), p0[1] + off * math.sin(a), sp * math.cos(a), sp * math.sin(a) - 1.0,
                    rng.uniform(2.0, 3.4), born=f, hold=3, fade=0.83, drag=0.02)
        # Where it lands: the foot keeps pouring drops down; they hit the ground (Sim.floor: puddle + bounce).
        bx, by = _bez(p0, p1, p2, 1.0)
        for _ in range(2):
            u = rng.uniform(-0.5, 0.5)
            e = sim.add(bx + u * 110, by + rng.uniform(12, 24), rng.uniform(-0.6, 0.6) + u * 1.5, rng.uniform(4.0, 6.5),
                        rng.uniform(3.0, 5.0), born=f, hold=6, fade=0.9, drag=0.01)
            sim.drops[e].foam = True
        # What has landed splashes and is gone at once: it must not pile up into a mound.
        for d in sim.drops:
            if d.on_floor:
                d.fade = min(d.fade, 0.6)
    s.hooks.append(physics)
    s.raster = frame
    return s


def ondas(rng: np.random.Generator):
    """A drop falls into still water: a small jet jumps back up and drops again, and thin white rings open on the
    water one after another, growing and fading."""
    s = Sim(420, 260, 64, gravity=0.8, rng=rng)
    cx, surface = 210.0, 196.0
    drop = s.add(cx, 10, 0, 6.0, 9.0, drag=0.0)
    state = {"hit": None}

    def ring(sim, f, speed, thick):
        # Starts wide enough not to fill in, and its drops are held by threads that never break, so it stays a
        # line as it grows (thinner and thinner) instead of turning into dots.
        n = 48
        ids = []
        for i in range(n):
            a = 2 * math.pi * i / n
            d = sim.add(cx + 34 * math.cos(a), surface + 0.3 * 34 * math.sin(a), speed * math.cos(a),
                        0.3 * speed * math.sin(a), thick, born=f, hold=10, fade=0.93, drag=0.035)
            sim.drops[d].foam = True
            sim.drops[d].weight = 0.0
            ids.append(d)
        for i in range(n):
            sim.link(ids[i], ids[(i + 1) % n], snap=60.0, pull=0.0, satellite=False)
            # A long rest length: the line keeps its thickness (a thread thins as it stretches past its rest).
            sim.threads[-1].rest, sim.threads[-1].snap = 1000.0, 1.0

    def hit(sim, f):
        d = sim.drops[drop]
        if state["hit"] is None and d.y >= surface:
            state["hit"] = f
            d.r = 0.0
            sim.ones_from, sim.ones_until = f, f + 4
            j = sim.add(cx, surface, 0, -10.0, 6.5, born=f + 2, hold=8, fade=0.9, drag=0.01)
            t = sim.add(cx, surface + 6, 0, -6.5, 4.8, born=f + 2, hold=6, fade=0.88, drag=0.01)
            sim.link(j, t, snap=2.0, pull=0.03)
            for side in (-1, 1):
                sim.add(cx + side * 6, surface - 2, side * 3.4, -5.8, 3.4, born=f + 1, hold=5, fade=0.88, drag=0.02)
        h = state["hit"]
        if h is not None and f in (h, h + 8, h + 17):
            k = (f - h) // 8
            ring(sim, f, 7.5 - 1.6 * k, 2.4 - 0.3 * k)
        # What falls back sinks into the water.
        if h is not None:
            for e in sim.drops:
                if sim.live(e, f) and not e.foam and e.vy > 0 and e.y > surface:
                    e.r *= 0.45
    s.hooks.append(hit)
    return s


def corona(rng: np.random.Generator):
    """A drop falls into a shallow pool: a hollow crown rises out of it — two walls leaning out — and a droplet forms
    at the tip of each of its points and flies off; the crown sinks back into the pool, which settles and fades."""
    floor = 270.0
    s = Sim(420, 300, 58, gravity=0.62, floor=floor, rng=rng)
    cx = 210.0
    for dx, r in ((-75, 9), (-45, 11), (-15, 12), (15, 12), (45, 11), (75, 9)):
        p = s.add(cx + dx, floor - 0.3 * r, 0, 0, r, hold=46, fade=0.92)
        s.drops[p].on_floor, s.drops[p].spread = True, 1.0
    drop = s.add(cx, 14, 0, 7.0, 11.0, drag=0.0)
    state = {"done": False}

    def hit(sim, f):
        d = sim.drops[drop]
        if state["done"] or d.y + d.r < floor - 8:
            return
        state["done"] = True
        d.r = 0.0
        sim.ones_from, sim.ones_until = f, f + 4
        for side in (-1, 1):
            # The wall: a thin sheet leaning out, thicker at its rim.
            prev = None
            for i in range(5):
                u = i / 4
                ang = math.radians(90 - side * (10 + 14 * u))
                sp = 6.0 + 6.0 * u
                w = sim.add(cx + side * (18 + 5 * u), floor - 4 - 3 * u, sp * math.cos(ang), -sp * math.sin(ang),
                            7.5 + 2.0 * u, born=f, hold=10, fade=0.9, drag=0.05)
                if prev is not None:
                    sim.link(prev, w, snap=2.6, pull=0.02, satellite=False)
                prev = w
            # The points on the rim, each throwing its droplet.
            for j in range(3):
                a = math.radians(90 - side * (12 + 12 * j) + rng.uniform(-3, 3))
                sp = rng.uniform(12.0, 14.0)
                tip = sim.add(cx + side * (20 + 6 * j), floor - 8, sp * math.cos(a), -sp * math.sin(a),
                              rng.uniform(6.0, 7.5), born=f, hold=12, fade=0.93, drag=0.02)
                sim.link(prev, tip, snap=rng.uniform(2.6, 3.4), pull=0.015, recoil=1.0)
    s.hooks.append(hit)
    return s


TONGUE = 24   # frames in a tongue's life on the wave


def ola(rng: np.random.Generator):
    """Water rocking in place (a loop): a long low sheet tapering at both ends, a big pointed crest leaning forward
    with a curl at its tip and a smaller one beside it, rising and falling out of step; spray at each peak. Drawn
    as a profile over the ground."""
    W_, H_ = 460, 230
    floor = 205
    period = 24
    s = Sim(W_, H_, 2 * period, gravity=0.55, rng=rng)
    s.skip = 12                                         # tongues already in the air
    xs = np.arange(W_, dtype=np.float32)
    crests = ((185.0, 1.0, 0.0), (305.0, 0.6, math.pi * 0.85))

    def frame(f):
        liquid = np.zeros((H_, W_), np.uint8)
        # The sheet: thickest in the middle, tapering to points at both ends.
        u = np.clip((xs - 20) / 420.0, 0, 1)
        prof = 16.0 * np.maximum(0.0, np.sin(np.pi * u)) ** 0.9
        tips = []
        for cx, size, phase in crests:
            t = 2 * math.pi * f / period + phase
            h = (56 + 20 * math.sin(t)) * size
            lean = (14 + 8 * math.sin(t + 0.7)) * size
            cx = cx + 10 * size * math.sin(t * 0.5)          # the crest wanders a little
            # A crest: a broad mound under a pointed peak, long at the back, steep at the front, its peak pushed
            # forward by the lean.
            pk = cx + lean
            back = np.clip(1 - np.maximum(0, pk - xs) / (95 * size), 0, 1) ** 1.6
            front = np.clip(1 - np.maximum(0, xs - pk) / (26 * size), 0, 1) ** 0.8
            mound = 0.35 * np.exp(-((xs - cx) / (70 * size)) ** 2)
            prof = np.maximum(prof, h * np.maximum(np.minimum(back, front), mound))
            tips.append((cx + lean, floor - h, size, t))
        # The edge boils a little from drawing to drawing.
        wav = 2.6 * np.sin(xs * 0.09 + f * 0.55) + 1.6 * np.sin(xs * 0.23 - f * 0.31)
        prof = np.where(prof > 3, np.maximum(1.0, prof + wav * np.clip(prof / 20, 0, 1)), prof)
        top = floor - prof
        for x in range(W_):
            if prof[x] > 0.6:
                liquid[int(top[x]):floor, x] = 1
        for k, (tx, ty, size, t) in enumerate(tips):
            # A tongue: a flat sheet growing out of the tip along a curve (up, then forward and over), thick at its
            # root and tapering; at the end of its life its tip has let go (the drops fly on with physics) and it
            # draws back into the crest.
            life = ((f + 9 * k) % TONGUE) / TONGUE
            grow = min(1.0, life / 0.55)
            shrink = 1.0 if life < 0.7 else max(0.0, 1 - (life - 0.7) / 0.3)
            L = 70 * size * grow * shrink
            if L < 4:
                continue
            pts_l, pts_r = [], []
            n = 14
            for i in range(n + 1):
                u = i / n
                ang = math.radians(78 - 115 * u ** 1.4)           # starts steep, curls forward and over
                x = tx + sum(math.cos(math.radians(78 - 115 * (j / n) ** 1.4)) for j in range(i)) * L / n
                y = ty - sum(math.sin(math.radians(78 - 115 * (j / n) ** 1.4)) for j in range(i)) * L / n
                wdt = (9 * size) * (1 - u) ** 0.8 + 1.0
                nx, ny = -math.sin(ang), -math.cos(ang)
                pts_l.append((x + nx * wdt, y + ny * wdt))
                pts_r.append((x - nx * wdt, y - ny * wdt))
            cv2.fillPoly(liquid, [np.array(pts_l + pts_r[::-1], np.int32)], 1)
        return liquid.astype(bool), np.zeros_like(liquid, bool)

    def spray(sim, f):
        # When a tongue's tip lets go (life 0.55), its end flies on as real drops; spray at the crest now and then.
        for k, (cx, size, phase) in enumerate(crests):
            t = 2 * math.pi * f / period + phase
            cxx = cx + 10 * size * math.sin(t * 0.5)
            h = (56 + 20 * math.sin(t)) * size
            lean = (14 + 8 * math.sin(t + 0.7)) * size
            if (f + 9 * k) % TONGUE == int(0.55 * TONGUE):
                L = 70 * size
                n = 14
                x = cxx + lean + sum(math.cos(math.radians(78 - 115 * (j / n) ** 1.4)) for j in range(n)) * L / n
                y = floor - h - sum(math.sin(math.radians(78 - 115 * (j / n) ** 1.4)) for j in range(n)) * L / n
                for j in range(3):
                    sim.add(x - 4 * j, y + 3 * j, rng.uniform(2.5, 4.0), rng.uniform(-3.5, -1.5) + j,
                            (5.5 - 1.3 * j) * size + 1.2, born=f, hold=5, fade=0.9, drag=0.01)
            if (f + 5 * k) % 6 == 0:
                a = math.radians(rng.uniform(60, 110))
                sp = rng.uniform(4, 6.5) * size + 1
                sim.add(cxx + lean + 3, floor - h, sp * math.cos(a), -sp * math.sin(a), rng.uniform(2.0, 3.4), born=f,
                        hold=4, fade=0.88, drag=0.02)
        # What falls back melts into the sheet.
        for d in sim.drops:
            if sim.live(d, f) and d.vy > 0 and d.y > floor - 14:
                d.r *= 0.55
    s.hooks.append(spray)
    s.raster = frame
    return s


RECIPES = {"chorro": (chorro, "Chorro que se parte en gotas", "columna"),
           "goteo": (goteo, "Goteo", "goteo"),
           "salpicadura": (salpicadura, "Gota que cae y salpica", "salpicadura"),
           "racimo": (racimo, "Racimo lanzado que se separa", "racimo"),
           "anillo": (anillo, "Gota que cae y abre un anillo", "anillo"),
           "gota": (gota, "Gota que salta del charco", "gota"),
           # Reference cells of the study page as (w, h, x, y, first frame, last frame), for the comparison only.
           "cascada": (cascada, "Cascada", (267, 402, 378, 158, 140, 240)),
           "ondas": (ondas, "Gota que cae y abre ondas", None),
           "corona": (corona, "Corona", (386, 207, 1452, 618, 145, 240)),
           "ola": (ola, "Ola baja", (317, 185, 378, 785, 145, 240))}


# ----------------------------------------------------------------------------------------- masks per frame
def shift(m, dx, dy):
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(m.astype(np.uint8), M, (m.shape[1], m.shape[0]), flags=cv2.INTER_NEAREST).astype(bool)


def masks_at(sim: Sim, f: int):
    """liquid, dark (low-right side and the pockets where drops meet), shine (up-left crescents) and foam (white,
    its own layer) of frame f."""
    fld = sim.field(f)
    liquid = fld > 1.0
    foam = (sim.field(f, foam=True) > 1.0) if any(d.foam for d in sim.drops) else np.zeros_like(liquid)
    if sim.raster is not None:
        # A drawn shape (and whatever drops fly off it): the field is then the distance into the shape.
        r_liq, r_foam = sim.raster(f)
        liquid = liquid | r_liq
        foam = foam | r_foam
        fld = np.maximum(fld, 1.0 + cv2.distanceTransform(liquid.astype(np.uint8), cv2.DIST_L2, 3) / 8.0)
    if not liquid.any():
        return liquid, liquid, liquid, foam
    dist = cv2.distanceTransform(liquid.astype(np.uint8), cv2.DIST_L2, 3)
    thick = float(np.percentile(dist[liquid], 90)) if liquid.sum() > 20 else 1.0
    # Each bulge (a local thickest point of the body) gets one big dark pocket low and right and one wide shine up
    # and left, both as big as the bulge; pockets of bulges next to each other run together. Inside only, with a
    # rim of light left around them.
    o = max(1.5, 0.55 * thick)
    k = max(3, int(1.6 * thick) | 1)
    peaks = (dist >= cv2.dilate(dist, np.ones((k, k), np.float32)) - 1e-3) & (dist > max(2.5, 0.5 * thick))
    n, lab, stats, cents = cv2.connectedComponentsWithStats(peaks.astype(np.uint8), 8)
    pockets = np.zeros(liquid.shape, np.uint8)
    shines = np.zeros(liquid.shape, np.uint8)
    for j in range(1, n):
        cx, cy = cents[j]
        R = float(dist[int(round(cy)), int(round(cx))])
        cv2.ellipse(pockets, (int(cx + 0.22 * R), int(cy + 0.38 * R)), (int(0.95 * R), int(0.68 * R)), -15, 0, 360, 1, -1)
        cv2.ellipse(shines, (int(cx - 0.38 * R), int(cy - 0.42 * R)), (int(0.5 * R), max(1, int(0.2 * R))), -55, 0, 360,
                    1, -1)
    inner = dist > max(1.6, 0.16 * thick)
    dark = inner & (pockets.astype(bool) | ~shift(liquid, -0.35 * o, -o))
    dark = cv2.morphologyEx(dark.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)).astype(bool)
    shine = shines.astype(bool) & (dist > max(1.8, 0.2 * thick)) & ~dark
    # Specks too small to draw cleanly go: a shine is at least a few pixels.
    n, lab, stats, _ = cv2.connectedComponentsWithStats(shine.astype(np.uint8), 8)
    for k in range(1, n):
        if stats[k, cv2.CC_STAT_AREA] < 6:
            shine[lab == k] = False
    return liquid, dark, shine, foam


def drawn_frames(sim: Sim, n: int) -> list[int]:
    """The frames that get a drawing: every one while it is fast (sim.ones_until), every ON after (on twos)."""
    return [i for i in range(sim.skip, n) if sim.ones_from <= i < sim.ones_until or (i - sim.skip) % ON == 0]


def simulate(name: str, seed: int):
    make = RECIPES[name][0]
    sim = make(np.random.default_rng(seed))
    frames = []
    for f in range(sim.frames):
        frames.append(masks_at(sim, f))
        sim.step(f)
    return sim, frames


def preview_image(frames, w, h, scale=2):
    """The masks drawn flat (body, dark, shine, rim), for a quick look without the app."""
    tiles = []
    for liquid, dark, shine, foam in frames:
        img = np.zeros((h, w, 3), np.uint8)
        img[liquid] = (0x5e, 0xba, 0xb1)
        img[dark] = (0x21, 0x6b, 0x66)
        img[shine] = (0xec, 0xfb, 0xfb)
        img[foam] = (0xf2, 0xfb, 0xfb)
        tiles.append(cv2.resize(img, (w * scale, h * scale), interpolation=cv2.INTER_NEAREST))
    return tiles


# ----------------------------------------------------------------------------------------------- template
def build(name: str, seed: int):
    sim, frames = simulate(name, seed)
    w, h = sim.w, sim.h
    W, H = (w * K) // 2 * 2, (h * K) // 2 * 2
    box = (0.0, 0.0, float(w), float(h))
    bodies, darks, shines, foams, times = [], [], [], [], []
    last = None
    for i in drawn_frames(sim, len(frames)):
        liquid, dark, shine, foam = frames[i]
        # Our own pieces may run off the frame (a pour, a wave): keep them, cut by the edge.
        body = outlines(liquid, 3, 0.005, keep_edges=True)
        b = svg_of(body, box)
        d = svg_of(outlines(dark, 6, 0.02, False, keep_edges=True), box)
        s = svg_of(outlines(shine, 3, 0.03, keep_edges=True), box)
        fo = svg_of(outlines(foam, 3, 0.006, keep_edges=True), box)
        if (b, d, s, fo) == last:
            continue
        last = (b, d, s, fo)
        bodies.append(b)
        darks.append(d)
        shines.append(s)
        foams.append(fo)
        times.append((i - sim.skip) / FPS)
    dur = (len(frames) - sim.skip) / FPS
    es = RECIPES[name][1]
    t = Template(f"vfx-liquido-propio-{name}-{seed}", es, name, "vfx", dur, size=(W, H), background="#000000")
    tr = t.track("video")
    clip = t.solid(tr, "#ffffff", 0.0, dur, box=Box(0, 0, W, H), kind="rectangle")
    st = clip["shapeStyle"]
    st["layers"] = []
    st["partsRef"] = [W, H]
    body_c, dark_c, shine_c, rim_c = sim.palette or (BODY, DARK, SHINE, RIM)
    st["parts"] = [{"id": "g1", "name": "Gota", "group": True, "clip": True, "children": [
        part("p1", "Brillo", W, H, shine_c, shines, times),
        part("p2", "Lado oscuro", W, H, dark_c, darks, times),
        part("p3", "Cuerpo", W, H, body_c, bodies, times, rim=(1.0 * K, rim_c)),
    ]}]
    if any(fo != EMPTY for fo in foams):
        # Foam over the water (the first part is drawn on top): white with a pale rim.
        st["parts"].insert(0, part("p0", "Espuma", W, H, FOAM, foams, times, rim=(1.0 * K, FOAM_RIM)))
    return t, dur, len(times)


FONT = "C\\:/Windows/Fonts/arialbd.ttf"


def side_by_side(name: str, ours: Path, out: Path, seconds: float = 4.0) -> Path:
    """RTFX's element (quality reference only) beside ours, each looping, same height."""
    ref_name = RECIPES[name][2]
    if ref_name is None:
        return ours
    if isinstance(ref_name, tuple):
        w, h, x, y, f0, f1 = ref_name
        refs = [fr[y:y + h, x:x + w].copy() for fr in page_frames(f0, f1)]
    else:
        refs = crops(ref_name)
    tmp = tempfile.mkdtemp(prefix="vfxgen_")
    for i, f in enumerate(refs):
        cv2.imwrite(os.path.join(tmp, f"r{i:04d}.png"), cv2.cvtColor(f, cv2.COLOR_RGB2BGR))
    HH = 760
    lab = lambda s: (f"drawtext=fontfile='{FONT}':text='{s}':fontcolor=white:fontsize=28:x=(w-text_w)/2:y=12:"
                     "box=1:boxcolor=black@0.7:boxborderw=8")
    flt = (f"[0:v]scale=-2:{HH}:flags=lanczos,setsar=1,pad=iw+40:ih+60:20:60:black,{lab('RTFX (calidad)')}[l];"
           f"[1:v]scale=-2:{HH},setsar=1,fps=30,pad=iw+40:ih+60:20:60:black,{lab('Nuestro (original)')}[r];"
           f"[l][r]hstack=inputs=2,trim=duration={seconds}[v]")
    target = out / f"lado-a-lado-{name}.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-stream_loop", "-1", "-framerate", "30",
                    "-i", os.path.join(tmp, "r%04d.png"), "-stream_loop", "-1", "-i", str(ours),
                    "-filter_complex", flt, "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt",
                    "yuv420p", "-t", str(seconds), str(target)], check=True)
    return target


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exe", default="")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--only", default="")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--preview", action="store_true", help="masks only, as sheets: no app")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    names = [n for n in RECIPES if not args.only or n in args.only.split(",")]
    if args.preview:
        for name in names:
            sim, frames = simulate(name, args.seed)
            tiles = preview_image([frames[i] for i in drawn_frames(sim, len(frames))], sim.w, sim.h, scale=1)
            cols = min(8, len(tiles))
            rows = (len(tiles) + cols - 1) // cols
            sheet = np.full((rows * (sim.h + 4), cols * (sim.w + 4), 3), 40, np.uint8)
            for k, tile in enumerate(tiles):
                y, x = (k // cols) * (sim.h + 4), (k % cols) * (sim.w + 4)
                sheet[y:y + sim.h, x:x + sim.w] = tile
            cv2.imwrite(str(out / f"vista-{name}-{args.seed}.png"), cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR))
            print(name, len(tiles), "drawings", flush=True)
        return 0
    if not args.exe:
        raise SystemExit("--exe is needed to render (or --preview)")
    work = out / "_proyectos"
    work.mkdir(parents=True, exist_ok=True)
    jobs = []
    for name in names:
        t, dur, nkeys = build(name, args.seed)
        tag = f"{name}-{args.seed}"
        print(f"{tag}: {dur:.2f} s, {nkeys} drawings", flush=True)
        jobs.append((tag, vfx_demo.write_doc(t, work, tag), dur))
    vfx_demo.render(jobs, args.exe, out, capture_at=0.3)
    for name in names:
        ours = out / f"{name}-{args.seed}.mp4"
        if ours.exists():
            print("side by side", side_by_side(name, ours, out), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
