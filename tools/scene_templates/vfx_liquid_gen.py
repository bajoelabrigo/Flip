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
from vfx_liquid_rtfx2 import BODY, DARK, K, RIM, SHINE, crops, outlines, part, svg_of

OUT = Path(r"E:\FlipStudio\tienda\vfx-estudio\liquido\propios")
FPS = 30
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
    ones_until: int = 0          # drawn on ones (every frame) before this frame, on twos after
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
                                   fade=0.92, drag=0.02))

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

    def field(self, f: int, scale: float = 1.0):
        """The metaball field on a w x h grid (1 = the liquid's edge)."""
        H, W = int(self.h * scale), int(self.w * scale)
        ys, xs = np.mgrid[0:H, 0:W].astype(np.float32) / scale
        fld = np.zeros((H, W), np.float32)
        for d in self.drops:
            if not self.live(d, f):
                continue
            fld += d.r * d.r / (((xs - d.x) / d.sx) ** 2 + ((ys - d.y) / d.sy) ** 2 + 1e-3)
        for t in self.threads:
            if not t.alive:
                continue
            a, b = self.drops[t.a], self.drops[t.b]
            if not (self.live(a, f) and self.live(b, f)):
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
        body.append(s.add(x, 70 + (8 if centre else 0) + rng.uniform(-2, 2), 0, 0,
                          (17.0 if centre else 12.5) + rng.uniform(-1.5, 1.5), pinned=True, hold=66, fade=0.93,
                          drag=0.06))
    for a, b in zip(body, body[1:]):
        s.link(a, b, snap=3.2, pull=0.05, recoil=2.2)
    # Hidden in the middle of the body: drops stacked under one another, heavier toward the bottom. When the body
    # lets go they pull apart like elastic into a string of bulbs and necks that part one by one.
    column, prev_c = [], body[4]
    for i, (r, w) in enumerate(((14.5, 1.0), (13.0, 1.12), (12.0, 1.25), (11.0, 1.4), (10.0, 1.6))):
        idx = s.add(s.drops[body[4]].x + rng.uniform(-1, 1), 80 + 5 * i, 0, 0, r + rng.uniform(-0.8, 0.8),
                    pinned=True, drag=0.03, hold=10**6, fade=0.95)
        s.drops[idx].weight = w
        s.link(prev_c, idx, snap=3.4 + 0.3 * rng.random(), pull=0.05, recoil=2.0)
        column.append(idx)
        prev_c = idx
    # The tongue: a string of thin drops hanging from the middle, a bulb at its tip that fills up and pulls.
    prev = body[4]
    tongue = []
    for i in range(7):
        r = 7.5 - 0.35 * i
        idx = s.add(s.drops[body[4]].x + rng.uniform(-0.8, 0.8), 92 + 7 * i, 0, 0, r, drag=0.08, hold=60, fade=0.93)
        s.link(prev, idx, snap=4.2, pull=0.32 - 0.03 * i, recoil=2.0, satellite=i > 3)
        tongue.append(idx)
        prev = idx
    tip = s.add(s.drops[body[4]].x, 142, 0, 0, 8.0, grow=0.36, grow_until=18, weight=1.6, drag=0.02, hold=10**6,
                fade=0.95)
    s.link(prev, tip, snap=3.0, pull=0.12, recoil=2.4)

    def let_go(sim, f):
        # A beat after the bulb has gone, the middle of the body lets go too and falls stretching; its ends stay.
        if f == 30:
            sim.drops[body[4]].pinned = False
            for i in column:
                sim.drops[i].pinned = False
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


def salpicadura(rng: np.random.Generator):
    """Two crowns of drops thrown up and out from a point, falling back and shrinking to specks."""
    s = Sim(440, 300, 26, gravity=0.42)
    for cx, n, power in ((150 + rng.uniform(-10, 10), 9, 1.0), (300 + rng.uniform(-10, 10), 7, 0.8)):
        core = s.add(cx, 262, 0, -3.0 * power, 30 * power, shrink=1.6, hold=6, pinned=False, drag=0.25)
        for i in range(n):
            ang = math.radians(-160 + 140 * (i + rng.uniform(0.2, 0.8)) / n)
            sp = rng.uniform(9.0, 13.5) * power
            idx = s.add(cx + 10 * math.cos(ang), 258 + 10 * math.sin(ang), sp * math.cos(ang), sp * math.sin(ang),
                        rng.uniform(9, 17) * power, born=int(rng.integers(0, 3)), shrink=rng.uniform(0.35, 0.6),
                        hold=9, drag=0.03)
            s.link(core, idx, snap=rng.uniform(1.5, 2.0), pull=0.012)
    return s


def racimo(rng: np.random.Generator):
    """Three fat drops stuck together that pull apart, wobble on their own and shrink away."""
    s = Sim(240, 200, 18, gravity=0.05)
    ids = []
    base = rng.uniform(0, 2 * math.pi)
    for i in range(3):
        a = base + i * 2 * math.pi / 3
        ids.append(s.add(120 + 14 * math.cos(a), 100 + 14 * math.sin(a), 5.2 * math.cos(a), 5.2 * math.sin(a),
                         rng.uniform(24, 30), shrink=rng.uniform(1.3, 1.8), hold=8, drag=0.07))
    for i in range(3):
        s.link(ids[i], ids[(i + 1) % 3], snap=rng.uniform(1.5, 1.8), pull=0.015)
    # A few small drops riding along the necks.
    for i in range(3):
        a = base + (i + 0.5) * 2 * math.pi / 3
        idx = s.add(120 + 22 * math.cos(a), 100 + 22 * math.sin(a), 3.6 * math.cos(a), 3.6 * math.sin(a),
                    rng.uniform(6, 9), shrink=0.5, hold=8, drag=0.05)
        s.link(ids[i], idx, snap=1.8, pull=0.05)
    return s


def anillo(rng: np.random.Generator):
    """A ring of liquid that spins out, tears into arcs, the arcs into beads, and the beads fade."""
    s = Sim(260, 260, 18, gravity=0.0)
    n = 22
    ids = []
    spin = rng.uniform(0.04, 0.07) * (1 if rng.random() < 0.5 else -1)
    for i in range(n):
        a = 2 * math.pi * i / n
        r0, out = 40.0, rng.uniform(4.2, 5.4)
        ids.append(s.add(130 + r0 * math.cos(a), 130 + r0 * math.sin(a), out * math.cos(a) - spin * r0 * math.sin(a),
                         out * math.sin(a) + spin * r0 * math.cos(a), rng.uniform(7.5, 10.5), shrink=0.55, hold=7,
                         drag=0.07))
    for i in range(n):
        s.link(ids[i], ids[(i + 1) % n], snap=rng.uniform(1.25, 1.9), pull=0.02)
    return s


def gota(rng: np.random.Generator):
    """A drop that shoots up, stretches into a tail and splits: the head flies on, the tail falls back."""
    s = Sim(150, 260, 20, gravity=0.6)
    v = rng.uniform(14.0, 15.5)
    ids = []
    for i, (r, dv) in enumerate(((25, 0.0), (19, -1.6), (14, -3.0), (10, -4.2))):
        ids.append(s.add(75 + rng.uniform(-1, 1), 235 + i * 12, rng.uniform(-0.4, 0.4), -v - dv, r + rng.uniform(-1, 1),
                         shrink=0.9, hold=9 + i, drag=0.01))
        if i:
            s.link(ids[i - 1], ids[i], snap=rng.uniform(1.6, 2.1), pull=0.03)
    return s


RECIPES = {"chorro": (chorro, "Chorro que se parte en gotas", "columna"),
           "goteo": (goteo, "Goteo", "goteo"),
           "salpicadura": (salpicadura, "Salpicadura doble", "salpicadura"),
           "racimo": (racimo, "Racimo que se separa", "racimo"),
           "anillo": (anillo, "Anillo que se rompe en gotas", "anillo"),
           "gota": (gota, "Gota que salta y se parte", "gota")}


# ----------------------------------------------------------------------------------------- masks per frame
def shift(m, dx, dy):
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(m.astype(np.uint8), M, (m.shape[1], m.shape[0]), flags=cv2.INTER_NEAREST).astype(bool)


def masks_at(sim: Sim, f: int):
    """liquid, dark (low-right side and the pockets where drops meet) and shine (up-left crescents) of frame f."""
    fld = sim.field(f)
    liquid = fld > 1.0
    if not liquid.any():
        return liquid, liquid, liquid
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
    return liquid, dark, shine


def drawn_frames(sim: Sim, n: int) -> list[int]:
    """The frames that get a drawing: every one while it is fast (sim.ones_until), every ON after (on twos)."""
    return [i for i in range(n) if i < sim.ones_until or (i - sim.ones_until) % ON == 0]


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
    for liquid, dark, shine in frames:
        img = np.zeros((h, w, 3), np.uint8)
        img[liquid] = (0x5e, 0xba, 0xb1)
        img[dark] = (0x21, 0x6b, 0x66)
        img[shine] = (0xec, 0xfb, 0xfb)
        tiles.append(cv2.resize(img, (w * scale, h * scale), interpolation=cv2.INTER_NEAREST))
    return tiles


# ----------------------------------------------------------------------------------------------- template
def build(name: str, seed: int):
    sim, frames = simulate(name, seed)
    w, h = sim.w, sim.h
    W, H = (w * K) // 2 * 2, (h * K) // 2 * 2
    box = (0.0, 0.0, float(w), float(h))
    bodies, darks, shines, times = [], [], [], []
    last = None
    for i in drawn_frames(sim, len(frames)):
        liquid, dark, shine = frames[i]
        body = outlines(liquid, 3, 0.005)
        b, d, s = svg_of(body, box), svg_of(outlines(dark, 6, 0.02, False), box), svg_of(outlines(shine, 3, 0.03), box)
        if (b, d, s) == last:
            continue
        last = (b, d, s)
        bodies.append(b)
        darks.append(d)
        shines.append(s)
        times.append(i / FPS)
    dur = len(frames) / FPS
    es = RECIPES[name][1]
    t = Template(f"vfx-liquido-propio-{name}-{seed}", es, name, "vfx", dur, size=(W, H), background="#000000")
    tr = t.track("video")
    clip = t.solid(tr, "#ffffff", 0.0, dur, box=Box(0, 0, W, H), kind="rectangle")
    st = clip["shapeStyle"]
    st["layers"] = []
    st["partsRef"] = [W, H]
    st["parts"] = [{"id": "g1", "name": "Gota", "group": True, "clip": True, "children": [
        part("p1", "Brillo", W, H, SHINE, shines, times),
        part("p2", "Lado oscuro", W, H, DARK, darks, times),
        part("p3", "Cuerpo", W, H, BODY, bodies, times, rim=(1.0 * K, RIM)),
    ]}]
    return t, dur, len(times)


FONT = "C\\:/Windows/Fonts/arialbd.ttf"


def side_by_side(name: str, ours: Path, out: Path, seconds: float = 4.0) -> Path:
    """RTFX's element (quality reference only) beside ours, each looping, same height."""
    ref_name = RECIPES[name][2]
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
