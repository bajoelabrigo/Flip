"""Animaciones Extremas · Fuego, second try (0.26), on the field engine (rtfx_field.py).

A fire element is a mass of puffs ("lobes"): each puff a flat-topped bump with its own yellow ball
inside, so between balls the red shows through; the mass is warped a little so the edges lick; a
cauliflower noise breaks the heart's edge; and as it dies a shredding front runs in from the outside
along the flow (out from the centre for a burst, upward for a column), tearing the mass into strands
while the heart holds on longest. Studied against RTFX's fire previews frame by frame.
"""

from __future__ import annotations

import math

import numpy as np

from rtfx_field import Tex, bump, render
from rtfx_engine import new

G = 256  # grid columns; rows follow the canvas aspect


class Mass:
    def __init__(self, W, H, seed):
        self.gw = G
        self.gh = int(round(G * H / W))
        self.yy, self.xx = np.mgrid[0:self.gh, 0:self.gw].astype(np.float32)
        self.cell = Tex(seed)
        self.streak = Tex(seed + 1)
        self.warp = Tex(seed + 2)

    def field(self, lobes, t, flow, origin, reach, die_at, die_len, crown=0.35, life=1.0):
        """lobes: (cx, cy, r, sx, sy, ang, heart) in grid cells; heart is the yellow ball's size (0 = none).
        flow 'radial' or 'up'; the shredding front starts at die_at seconds and takes die_len."""
        xx, yy = self.xx, self.yy
        wx = (self.warp.fbm(xx * 0.022, yy * 0.022 + t * 1.5, 2) - 0.5) * 12
        wy = (self.warp.fbm(xx * 0.022 + 40, yy * 0.022 + t * 1.5, 2) - 0.5) * 8
        X, Y = xx + wx, yy + wy
        mx = np.zeros_like(xx)
        sm = np.zeros_like(xx)
        mc = np.zeros_like(xx)
        holes = np.zeros_like(xx)
        for lobe in lobes:
            cx, cy, r, sx, sy, ang, heart = lobe[:7]
            if r <= 0.5:
                continue
            g = bump(X, Y, cx, cy, r, sx, sy, ang)
            mx = np.maximum(mx, g)
            sm += g
            if heart > 0.05:
                mc = np.maximum(mc, bump(X, Y, cx, cy, r * heart, sx, sy, ang))
            # A hollow opening in the puff as it burns out (lobe[7] 0..1), on the side lobe[8] points
            # to (radians; the back of a puff thrown forward, so it curls into a C).
            if len(lobe) > 7 and lobe[7] > 0:
                k = lobe[7]
                hx = cx + math.cos(lobe[8]) * r * 0.55
                hy = cy + math.sin(lobe[8]) * r * 0.55
                holes = np.maximum(holes, bump(X, Y, hx, hy, r * (0.3 + 0.9 * k), 1.0, 1.1))
        d = mx + 0.05 * np.clip(sm, 0, 2) - 1.5 * holes
        dc = mc - 1.5 * holes
        ox, oy = origin
        if flow == "radial":
            ang = np.arctan2(yy - oy, xx - ox)
            rad = np.hypot(xx - ox, yy - oy)
            bend = (self.warp.fbm(xx * 0.03 + 7, yy * 0.03 + 3, 2) - 0.5) * 6
            su, sv = ang * 32 / math.pi + rad * 0.05 + bend, rad * 0.02 - t * 1.6
            far = np.clip(rad / reach, 0, 1)
        else:
            a = -math.pi / 2 if flow == "up" else flow
            # Along the flow: v runs with it, u across it.
            ca, sa = math.cos(a), math.sin(a)
            along = (xx - ox) * ca + (yy - oy) * sa
            across = -(xx - ox) * sa + (yy - oy) * ca
            bend = (self.warp.fbm(xx * 0.03 + 7, yy * 0.03 + 3, 2) - 0.5) * 4
            su, sv = across * 0.16 + bend, along * 0.02 - t * 2.0
            far = np.clip(along / reach, 0, 1)
        st = self.streak.fbm(su, sv, 2)
        prog = min(1.0, max(0.0, (t - die_at) / die_len))
        front = np.clip((far - (1.0 - prog * 1.35)) / 0.3, 0, 1)
        cut = 0.47 - 0.12 * prog
        gap = np.clip((st - cut) / 0.07, 0, 1)
        keep = np.clip((cut - st) / 0.07, 0, 1)
        eat = front * (1.6 * gap - 0.15 * keep * (1 - prog)) + prog ** 3 * 0.9
        d = d - eat
        dc = dc - 0.08 * eat
        cauli = self.cell.fbm(xx * 0.07, yy * 0.07 - t * 1.2, 2) - 0.5
        top = np.clip((oy - yy) / reach, 0, 1) if flow == "radial" else 0.0
        d = d + 0.18 * cauli
        core = dc + 0.5 * cauli + 0.06 - 0.05 * life - 0.9 * life * far - crown * top * min(1.0, t / 0.4)
        return d, core


# A cartoon explosion is a pyramid of puffs: a heart, three at the base, two above, one on top, small
# ones in the gaps (offsets in units of the puff radius).
PYRAMID = [(0.0, 0.3, 0.7), (-1.05, 0.55, 1.0), (0.0, 0.62, 1.05), (1.05, 0.55, 1.0), (-0.55, -0.15, 1.0),
           (0.55, -0.15, 1.0), (0.0, -0.85, 1.0), (-0.5, 0.25, 0.7), (0.5, 0.25, 0.7), (0.0, 0.1, 0.8),
           (-0.3, -0.55, 0.65), (0.3, -0.55, 0.65), (-1.3, 0.85, 0.5), (1.3, 0.85, 0.5)]


def explosion(W, H, seed, size=1.0, grow=0.22, dur=1.9):
    m = Mass(W, H, seed)
    rnd = np.random.default_rng(seed)
    jit = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.random()) for _ in PYRAMID]
    R = 31 * size * m.gw / 256
    ox, oy = m.gw / 2, m.gh * 0.6

    def field(t):
        e = 1 - (1 - min(1, t / grow)) ** 3
        lobes = []
        for (px, py, k), (jx, jy, js) in zip(PYRAMID, jit):
            cx = ox + (px + jx * 0.12) * R * 1.25 * e
            cy = oy + (py + jy * 0.12) * R * 1.15 * e - 14 * t
            r = (4 + R * 0.85 * e) * k * (0.9 + 0.2 * js) * (1 - 0.15 * max(0, t - 0.6))
            dist = math.hypot(px, py - 0.3) * 0.8 + (0.5 if py < -0.3 else 0.0)
            heart = 0.85 * max(0.0, min(1.0, 1.0 - max(0.0, t - 0.62 + 0.08 * dist) * (0.6 + 1.4 * dist)))
            lobes.append((cx, cy, r, 1.0, 0.95, 0.0, heart))
        return m.field(lobes, t, "radial", (ox, oy), 110 * size * m.gw / 256, 0.5, 0.8,
                       life=min(1.0, t / 1.6))

    return field


def torch(W, H, seed, size=1.0, dur=1.9):
    """A fireball column rising (RTFX's «Torch Fireball Up»): puffs born up a sinuous tongue, the top
    ones leaning and drawn out into licks, hollows opening as they age, torn upward as it dies."""
    m = Mass(W, H, seed)
    rnd = np.random.default_rng(seed)
    puffs = [(i / 9, rnd.uniform(-1, 1), rnd.uniform(0.8, 1.15)) for i in range(10)]
    k = size * m.gw / 256
    ox, base = m.gw / 2, m.gh * 0.74

    def field(t):
        t *= 1.55  # RTFX's torch is over in under a second
        lobes = []
        for i, (h, jx, js) in enumerate(puffs):
            age = t - h * 0.28
            if age < 0 or age > 1.25:
                continue
            side = 1 if i % 2 else -1
            cx = ox + (math.sin(h * 4.0 + 0.4) * 34 * h + side * 13 * (1 - h) + jx * 5) * k
            cy = base - (h * 120 + age * 45) * k
            r = (7 + 25 * min(1, age / 0.15)) * js * (1.1 - 0.45 * h) * (1 - 0.3 * max(0, age - 0.6)) * k
            lean = 1.6 * (h - 0.7) / 0.3 if h > 0.7 else 0.0
            heart = 0.85 * max(0.0, min(1.0, 1.0 - max(0.0, age - 0.55) * 1.6))
            hole = 0.7 * max(0.0, (age / 1.25 - 0.55) / 0.45)
            lobes.append((cx, cy, r, 1.0, 1.05 + 0.6 * h * h, lean, heart, hole, math.pi / 2 + jx * 0.6))
        return m.field(lobes, t, "up", (ox, base + 6 * k), 170 * k, 0.75, 0.75, crown=0.0,
                       life=min(1.0, t / 1.5))

    return field


def thrower(W, H, seed, angle=0.0, size=1.0, dur=1.3):
    """A flamethrower (RTFX's «Flamethrower»): a thin jet from the nozzle, puffs thrown out along it
    that slow, swell and drift to either side, each hollowed from the back into a curling C."""
    m = Mass(W, H, seed)
    rnd = np.random.default_rng(seed)
    k = size * m.gw / 256
    ca, sa = math.cos(angle), math.sin(angle)
    nx, ny = m.gw / 2 - ca * 80 * k, m.gh / 2 - sa * 80 * k
    puffs = [(i * 0.13 + rnd.uniform(0, 0.03), rnd.uniform(0.85, 1.15), (1 if i % 2 else -1) * rnd.uniform(0.5, 1.0))
             for i in range(4)]

    def field(t):
        lobes = []
        # The jet: a long thin lobe along the throw while the puffs leave.
        jet = max(0.0, 1 - max(0.0, t - 0.55) / 0.15)
        if jet > 0:
            L = 110 * k * min(1, t / 0.1)
            lobes.append((nx + ca * L * 0.5, ny + sa * L * 0.5, L * 0.5, 1.0, 0.06, angle, 0.7 * jet))
        for born, js, side in puffs:
            age = t - born
            if age < 0 or age > 1.3:
                continue
            go = 150 * k * (1 - math.exp(-age * 3.5)) + 25 * k * age
            drift = side * 48 * k * (1 - math.exp(-age * 3))
            cx = nx + ca * go - sa * drift
            cy = ny + sa * go + ca * drift
            r = (7 + 36 * min(1, age / 0.25)) * js * k * (1 - 0.3 * max(0, age - 0.7))
            heart = 0.8 * max(0.0, 1 - max(0.0, age - 0.75) * 1.8)
            hole = 0.6 * max(0.0, min(1.0, (age - 0.2) / 0.7))
            # The hollow opens at the back, turned the way the puff drifts so it curls.
            back = math.atan2(-sa, -ca) + side * 0.9
            lobes.append((cx, cy, r, 1.0, 1.0, 0.0, heart, hole, back))
        return m.field(lobes, t, angle, (nx, ny), 260 * k, 0.95, 0.6, crown=0.0, life=0.0)

    return field


def make_thrower():
    s = new("ex-fuego-lanzallamas-derecha", "Fuego · Lanzallamas a la derecha", "Fire · Flamethrower right", "fuego",
            40, 6002, ["fuego", "fire", "lanzallamas", "flamethrower"], size=512, thumb=0.35)
    s.fps = 24
    return render(s, thrower(512, 512, 11, size=0.75))


def make_torch():
    s = new("ex-fuego-antorcha-arriba", "Fuego · Antorcha hacia arriba", "Fire · Torch up", "fuego", 32, 6001,
            ["fuego", "fire", "antorcha", "torch"], size=512, thumb=0.3)
    s.fps = 24
    return render(s, torch(512, 512, 7, size=0.95))


def make_explosion():
    s = new("ex-fuego-explosion-radial", "Fuego · Explosión radial", "Fire · Radial explosion", "fuego", 46, 6000,
            ["fuego", "fire", "explosión", "explosion"], size=512, thumb=0.25)
    s.fps = 24
    return render(s, explosion(512, 512, 5, size=1.35))


STICKERS = [make_explosion, make_torch, make_thrower]
