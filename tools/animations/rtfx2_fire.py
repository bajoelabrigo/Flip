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

from rtfx_field import HOT, RIM, Tex, bump, render
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

    def field(self, lobes, t, flow, origin, reach, die_at, die_len, crown=0.35, life=1.0, char=0.0):
        """lobes: (cx, cy, r, sx, sy, ang, heart) in grid cells; heart is the yellow ball's size (0 = none).
        flow 'radial' or 'up'; the shredding front starts at die_at seconds and takes die_len.
        char (0..1): the mass burns out from the inside instead, the back first, leaving a glowing
        line along its outer edge and the seams between puffs that thins and breaks up."""
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
            own = None
            if len(lobe) > 10 and lobe[10] and lobe[7] > 0:
                # lobe[10]: the hollow cuts this puff only, so it leaves a crescent even over its
                # neighbours (a hit's dome burning out puff by puff).
                kk, off = lobe[7], lobe[9]
                own = bump(X, Y, cx + math.cos(lobe[8]) * r * off * sx, cy + math.sin(lobe[8]) * r * off * sy,
                           r * (0.3 + 0.9 * kk), sx, sy, ang)
                own = np.clip((own - 0.25) * 3.0, 0, 1)  # a sharp cut, so the crescent left is the size asked
                g = g - 1.5 * own
            mx = np.maximum(mx, g)
            sm += np.maximum(g, 0)
            if heart > 0.05:
                c = bump(X, Y, cx, cy, r * heart, sx, sy, ang)
                mc = np.maximum(mc, c if own is None else c + 0.14 - 1.3 * own)
            # A hollow opening in the puff as it burns out (lobe[7] 0..1), on the side lobe[8] points
            # to (radians; the back of a puff thrown forward, so it curls into a C).
            if len(lobe) > 7 and lobe[7] > 0 and own is None:
                k = lobe[7]
                # lobe[9], when given: how far off centre the hollow sits, and it then takes the
                # puff's own shape, so a flat puff becomes a ring (a coil of a tornado).
                off = lobe[9] if len(lobe) > 9 else 0.55
                hx = cx + math.cos(lobe[8]) * r * off * (sx if len(lobe) > 9 else 1.0)
                hy = cy + math.sin(lobe[8]) * r * off * (sy if len(lobe) > 9 else 1.0)
                if len(lobe) > 9:
                    holes = np.maximum(holes, bump(X, Y, hx, hy, r * (0.3 + 0.9 * k), sx, sy, ang))
                else:
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
        if char > 0:
            d, core = self.charred(d, core, far, t, char)
        return d, core

    def charred(self, d, core, far, t, ch):
        # The band kept is the part of the mass whose level is under m: the flat inside of every puff
        # is above it and goes, the edges and the dips where puffs meet stay. m drops to the rim.
        n = self.cell.fbm(self.xx * 0.06 + 31, self.yy * 0.06 - t * 0.8, 2) - 0.5
        b = 0.6 * max(0.0, 1 - ch) ** 1.5 + 0.13 - 0.3 * ch * ch + 0.5 * n - 0.25 * ch * (1 - far)
        m = RIM + np.maximum(b, -0.3)
        over = d - m
        nd = np.where(over > 0, m - 4.0 * over, d)
        mid = (RIM + m) / 2
        half = np.maximum((m - RIM) / 2, 0.01)
        band = HOT + 0.12 - 0.3 * ch - 0.3 * np.abs(d - mid) / half
        k = min(1.0, ch * 3)
        return nd, (1 - k) * core + k * np.minimum(core + 0.2, band)


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


def wings(W, H, seed, size=1.0, dur=2.2):
    """Wings of fire opening up (RTFX's «Wings Up»): from a burst at the base two wings unfold, each a
    chain of puffs swelling towards the tip and leaning out; they hold, then fray from the tips
    inward into a lacy edge and burn out."""
    m = Mass(W, H, seed)
    rnd = np.random.default_rng(seed)
    k = size * m.gw / 256
    cx, base = m.gw / 2, m.gh * 0.78
    feathers = [(i / 7, rnd.uniform(-1, 1), rnd.uniform(0.85, 1.1)) for i in range(8)]

    def field(t):
        e = 1 - (1 - min(1, t / 0.3)) ** 3
        lobes = []
        for side in (-1, 1):
            for u, j, js in feathers:
                # Along a curve from the base out and up to the tip.
                ang = -math.pi / 2 + side * (0.22 + 0.38 * u)
                reach = (14 + 95 * u) * k * e
                x = cx + math.cos(ang) * reach * 0.95 + side * 8 * k
                y = base + math.sin(ang) * reach - 20 * k * u * u * e
                r = (11 + 34 * u) * js * k * (0.4 + 0.6 * e)
                lean = ang + math.pi / 2
                heart = 0.85 * max(0.0, min(1.0, 1 - max(0.0, t - 0.7 - 0.5 * (1 - u)) * 1.2))
                lobes.append((x, y, r, 0.95, 1.25, lean, heart))
        return m.field(lobes, t, "radial", (cx, base + 10 * k), 150 * k, 0.75, 1.3, crown=0.0, life=0.0)

    return field


def make_wings():
    s = new("ex-fuego-alas-arriba", "Fuego · Alas de fuego", "Fire · Wings of fire", "fuego", 52, 6003,
            ["fuego", "fire", "alas", "wings"], size=512, thumb=0.35)
    s.fps = 24
    return render(s, wings(512, 512, 13, size=1.05))


def ring(W, H, seed, size=1.0, dur=1.3):
    """A swirling ring of fire (RTFX's «Hit Radial»): a hot ball bursts into a ring that spins as it
    widens, its puffs drawn round the circle and hollowed from the inside, the centre going dark,
    then the ring frays into sparks round the rim."""
    m = Mass(W, H, seed)
    rnd = np.random.default_rng(seed)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2
    n = 11
    jit = [(rnd.uniform(-0.15, 0.15), rnd.uniform(0.8, 1.2)) for _ in range(n)]

    def field(t):
        e = 1 - (1 - min(1, t / 0.35)) ** 3
        R = (6 + 52 * e) * k
        spin = 1.6 * e + 0.4 * t
        lobes = []
        # The hot ball, gone by the time the ring has opened.
        core = max(0.0, 1 - t / 0.3)
        if core > 0:
            lobes.append((cx, cy, (14 + 20 * e) * k * core ** 0.5, 1.0, 1.0, 0.0, 0.9 * core))
        # Two spiral arms inside, winding in as the ring spins, gone soon after it opens.
        arms = max(0.0, 1 - max(0.0, t - 0.2) / 0.35)
        if arms > 0 and t > 0.05:
            for arm in (0, math.pi):
                for j in range(6):
                    u = (j + 1) / 7
                    a = arm + spin * 1.3 + u * 3.2
                    x, y = cx + math.cos(a) * R * u * 0.85, cy + math.sin(a) * R * u * 0.85
                    lobes.append((x, y, (3 + 5 * u) * k * arms, 1.8, 0.55, a + math.pi / 2, 0.75 * arms))
        for i, (ja, js) in enumerate(jit):
            a = 2 * math.pi * i / n + ja + spin
            x, y = cx + math.cos(a) * R, cy + math.sin(a) * R
            r = (7 + 14 * e) * js * k * (1 - 0.35 * max(0, t - 0.5))
            heart = 0.8 * max(0.0, 1 - max(0.0, t - 0.25) * 1.6)
            hole = min(1.0, max(0.0, (t - 0.12) / 0.4)) * 0.8
            lobes.append((x, y, r, 1.6, 0.8, a + math.pi / 2, heart, hole, a + math.pi))
        return m.field(lobes, t, "radial", (cx, cy), 75 * k, 0.45, 0.75, crown=0.0, life=0.0)

    return field


def make_ring():
    s = new("ex-fuego-anillo-radial", "Fuego · Anillo de fuego", "Fire · Ring of fire", "fuego", 30, 6004,
            ["fuego", "fire", "anillo", "ring", "golpe", "hit"], size=512, thumb=0.3)
    s.fps = 24
    return render(s, ring(512, 512, 17, size=1.0))


def slash(W, H, seed, angle=0.0, size=1.0):
    """A fire slash (RTFX's «Slash»): a comet of flame shooting across, a round hot head and a tail
    of licks behind it that tears away from the back while the head runs on."""
    m = Mass(W, H, seed)
    rnd = np.random.default_rng(seed)
    k = size * m.gw / 256
    ca, sa = math.cos(angle), math.sin(angle)
    tail = [(i / 6, rnd.uniform(-1, 1), rnd.uniform(0.8, 1.2)) for i in range(7)]

    def field(t):
        e = 1 - (1 - min(1, t / 0.18)) ** 2
        run = -60 * k + 150 * k * (1 - math.exp(-t * 2.2))
        hx, hy = m.gw / 2 + ca * run, m.gh / 2 + sa * run
        lobes = []
        for u, j, js in tail:
            back = (8 + 110 * u) * k * e
            off = j * 5 * k * u
            x = hx - ca * back - sa * off
            y = hy - sa * back + ca * off
            r = (28 - 18 * u) * js * k * (0.4 + 0.6 * e)
            heart = 0.72 * max(0.0, min(1.0, 1.0 - max(0.0, t - 0.35 - 0.3 * (1 - u)) * 2.0))
            hole = 0.35 * max(0.0, min(1.0, (t - 0.1) / 0.5)) if u > 0.15 else 0.0
            lobes.append((x, y, r, 1.5 - 0.5 * u, 0.9, angle, heart, hole, angle + math.pi / 2 * (1 if j > 0 else -1)))
        # Tears from the tail: the flow points back along the tail from the head.
        return m.field(lobes, t, angle + math.pi, (hx + ca * 20 * k, hy + sa * 20 * k), 150 * k, 0.25, 0.6,
                       crown=0.0, life=0.0)

    return field


def make_slash():
    s = new("ex-fuego-corte-derecha", "Fuego · Corte a la derecha", "Fire · Slash right", "fuego", 26, 6005,
            ["fuego", "fire", "corte", "slash"], size=512, thumb=0.25)
    s.fps = 24
    return render(s, slash(512, 512, 19, size=1.0))


def ray(W, H, seed, size=1.0):
    """A fire ray going up (RTFX's «Ray Up»): flat coils of flame wound round a rising column, like a
    tornado seen from the side, each a C-shaped lick hollowed on alternate sides, the top ones
    curling over; it burns out upward into hooked wisps."""
    m = Mass(W, H, seed)
    rnd = np.random.default_rng(seed)
    k = size * m.gw / 256
    cx, base = m.gw / 2, m.gh * 0.8
    coils = [(i / 7, rnd.uniform(-1, 1), rnd.uniform(0.85, 1.15)) for i in range(8)]

    def field(t):
        lobes = []
        for i, (h, j, js) in enumerate(coils):
            born = h * 0.3
            age = t - born
            if age < 0 or age > 1.0:
                continue
            rise = (h * 90 + age * 40) * k
            sway = math.sin(age * 7 + i * 1.3) * 16 * k
            w = (44 + 14 * h) * js * k * min(1, age / 0.15)
            x = cx + sway + j * 6 * k
            y = base - rise
            heart = 0.8 * max(0.0, 1 - max(0.0, age - 0.45) * 2.0)
            side = 1 if i % 2 else -1
            hole = 0.33 + 0.17 * max(0.0, min(1.0, (age - 0.1) / 0.5))
            lobes.append((x, y, w, 1.0, 0.32, 0.08 * side, heart, hole, -math.pi / 2 + side * 0.5, 0.35))
        return m.field(lobes, t, "up", (cx, base + 10 * k), 200 * k, 0.6, 0.6, crown=0.0, life=0.0)

    return field


def make_ray():
    s = new("ex-fuego-rayo-arriba", "Fuego · Rayo hacia arriba", "Fire · Ray up", "fuego", 32, 6006,
            ["fuego", "fire", "rayo", "ray", "remolino"], size=512, thumb=0.35)
    s.fps = 24
    return render(s, ray(512, 512, 23, size=1.0))


# A hit's cloud: a dome of puffs (offsets in units of the puff radius, each puff's size, and whether
# it makes the outline or sits inside it).
DOME = [(0.0, -1.55, 1.0, 1), (-0.85, -1.05, 0.9, 1), (0.85, -1.05, 0.9, 1), (-1.3, -0.25, 0.85, 1),
        (1.3, -0.25, 0.85, 1), (-0.5, -1.55, 0.6, 1), (0.5, -1.5, 0.6, 1), (-1.3, -0.8, 0.6, 1), (1.3, -0.8, 0.6, 1),
        (-0.45, -0.45, 0.85, 0), (0.45, -0.45, 0.85, 0), (0.0, 0.15, 0.8, 0), (-0.75, 0.35, 0.7, 0),
        (0.75, 0.35, 0.7, 0)]


def dome(cx, cy, R, a, t, e, jit, lift=0.0, sy=1.05, speed=1.0):
    """A hit's dome of puffs facing direction a (radians), grown to e (0..1), lifted along a by lift.
    t counts from the hit: each puff burns out from the back (a sharp hollow of its own shape opening
    behind it, the back ones first), leaving crescents along the front that thin out."""
    rot = a + math.pi / 2
    c, s_ = math.cos(rot), math.sin(rot)
    lobes = []
    for (px, py, s, rim), (jx, jy, js) in zip(DOME, jit):
        ox, oy = (px + jx) * R * (0.4 + 0.6 * e), (py + jy) * sy * R * (0.4 + 0.6 * e) - lift
        x, y = cx + ox * c - oy * s_, cy + ox * s_ + oy * c
        r = R * s * js * (0.3 + 0.7 * e)
        hole = max(0.0, (t * speed - 0.17 - 0.1 * (0.4 - py)) / 0.4)
        heart = 0.97 * max(0.0, 1 - max(0.0, hole - 0.9) * 1.5)
        lobes.append((x, y, r, 1.0, 0.95, rot, heart, (0.5 if rim else 0.75) + 0.33 * min(1.0, hole) if hole > 0 else 0.0,
                      a + math.pi + jx, 0.55 - 0.25 * min(1.0, hole), True))
    return lobes


def hit_up(W, H, seed, size=1.0):
    """A fire hit going up (RTFX's «Hit Up»): a pointed tongue shoots up and swells into a dome of
    puffs with flame dripping from its underside, then each puff burns out from below (a hollow of its
    own shape rising inside it, the bottom ones first), leaving glowing crescents along the tops that
    thin and break into embers."""
    m = Mass(W, H, seed)
    rnd = np.random.default_rng(seed)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh * 0.62
    R = 33 * k
    jit = [(rnd.uniform(-0.12, 0.12), rnd.uniform(-0.12, 0.12), rnd.uniform(0.9, 1.1)) for _ in DOME]
    drips = [(-0.85, 0.7), (-0.3, 1.1), (0.25, 0.8), (0.8, 0.6)]

    def field(t):
        lobes = []
        # The tongue, the first frames only: pointed, swelling into the dome.
        tg = max(0.0, 1 - t / 0.12)
        if tg > 0:
            lobes.append((cx, cy + 0.7 * R, R * (1.0 + 0.4 * (1 - tg)), 0.3 + 0.5 * (1 - tg), 1.0, 0.0, 0.75))
        e = 1 - (1 - min(1.0, max(0.0, (t - 0.03) / 0.18))) ** 3
        if e > 0:
            lift = 12 * k * t
            lobes += dome(cx, cy, R, -math.pi / 2, t - 0.03, e, jit, lift)
            dr = max(0.0, 1 - max(0.0, t - 0.12) / 0.3) * e
            for px, ln in drips:
                if dr > 0:
                    lobes.append((cx + px * R, cy + (0.45 + 0.5 * ln * dr) * R - lift, R * 0.55 * ln * dr, 0.3, 1.0,
                                  0.0, 0.5 * dr))
        ch = max(0.0, (t - 0.55) / 0.45)
        return m.field(lobes, t, "up", (cx, cy + 1.4 * R), 2.6 * R, 9.0, 1.0, crown=0.0, life=0.0, char=ch)

    return field


def shot_hit(W, H, seed, angle=0.0, size=1.0):
    """A fireball shot that hits (RTFX's «Hit Shot»): a ball streaks in trailing a thin tail, bursts
    into a dome facing the way it flew, and the dome burns out from the back, leaving crescents at the
    front while the tail breaks into beads."""
    m = Mass(W, H, seed)
    rnd = np.random.default_rng(seed)
    k = size * m.gw / 256
    ca, sa = math.cos(angle), math.sin(angle)
    hx, hy = m.gw / 2 + ca * 33 * k, m.gh / 2 + sa * 33 * k
    R = 13 * k
    jit = [(rnd.uniform(-0.12, 0.12), rnd.uniform(-0.12, 0.12), rnd.uniform(0.9, 1.1)) for _ in DOME]
    beads = [(0.25 + 0.17 * i + rnd.uniform(-0.04, 0.04), rnd.uniform(-1, 1)) for i in range(5)]
    hit = 0.12

    def field(t):
        lobes = []
        go = min(1.0, t / hit)
        bx, by = hx - ca * 80 * k * (1 - go), hy - sa * 80 * k * (1 - go)
        # The tail: long and thin behind the ball, thinning to beads after the hit.
        tl = max(0.0, 1 - max(0.0, t - hit) / 0.35)
        if tl > 0:
            L = 100 * k * min(1.0, t / 0.1)
            lobes.append((bx - ca * L * 0.5, by - sa * L * 0.5, L * 0.5, 1.0, (0.05 + 0.12 * max(0.0, 1 - t / hit)) * tl,
                          angle, 0.6 * tl))
            if t < hit + 0.08:
                # The body of flame right behind the ball, swallowed by the burst.
                fb = max(0.0, 1 - max(0.0, t - hit) / 0.08)
                lobes.append((bx - ca * 22 * k, by - sa * 22 * k, 20 * k * fb, 1.0, 0.45, angle, 0.8 * fb))
            for u, j in beads:
                rr = (3 + 3 * (1 - u)) * k * min(1.0, t / 0.12) * (0.5 + 0.5 * tl)
                if t > hit:
                    lobes.append((bx - ca * L * u - sa * j * 3 * k, by - sa * L * u + ca * j * 3 * k, rr * (1.6 - tl),
                                  1.8, 0.8, angle, 0.6))
        if t < hit + 0.05:
            lobes.append((bx, by, (9 + 5 * go) * k, 1.8, 0.9, angle, 0.8))
        e = 1 - (1 - min(1.0, max(0.0, (t - hit + 0.03) / 0.14))) ** 3
        if t > hit - 0.03:
            lobes += dome(hx, hy, R, angle, t - hit, e, jit, -6 * k * (t - hit), sy=1.3, speed=1.5)
        ch = max(0.0, (t - hit - 0.35) / 0.4)
        return m.field(lobes, t, angle, (hx - ca * 1.5 * R, hy - sa * 1.5 * R), 3.0 * R, 9.0, 1.0, crown=0.0,
                       life=0.0, char=ch)

    return field


def make_hit_up():
    s = new("ex-fuego-golpe-arriba", "Fuego · Golpe hacia arriba", "Fire · Hit up", "fuego", 30, 6007,
            ["fuego", "fire", "golpe", "hit", "impacto"], size=512, thumb=0.2)
    s.fps = 24
    return render(s, hit_up(512, 512, 29, size=1.0))


def make_shot_hit():
    s = new("ex-fuego-disparo-golpe-derecha", "Fuego · Disparo con golpe a la derecha", "Fire · Shot hit right", "fuego",
            26, 6008, ["fuego", "fire", "disparo", "shot", "golpe", "hit", "bola de fuego", "fireball"], size=512,
            thumb=0.2)
    s.fps = 24
    return render(s, shot_hit(512, 512, 31, size=1.4))


def projectile(W, H, seed, angle=0.0, size=1.0):
    """A fireball in flight, looping (RTFX's «Projectile Loop»): a flame drawn out into a lens, pointed
    at the nose and the tail, redrawn on every second frame so it boils, with thin slivers peeling
    off above and below."""
    m = Mass(W, H, seed)
    k = size * m.gw / 256
    ca, sa = math.cos(angle), math.sin(angle)
    cx, cy = m.gw / 2, m.gh / 2

    def at(u, v):  # along the flight, across it
        return cx + ca * u * k - sa * v * k, cy + sa * u * k + ca * v * k

    def field(t):
        n = int(round(t * 24)) // 2
        rnd = np.random.default_rng(seed * 1000 + n)
        lobes = []
        sc = rnd.uniform(0.7, 1.15)  # each drawing a size of its own, so it pulses as it boils
        # The body: a few drawn-out puffs along the axis, the biggest behind the nose.
        for u, r, sy in ((14, 32, 1.05), (-10, 30, 1.0), (-36, 22, 0.85)):
            x, y = at(sc * u + rnd.uniform(-5, 5), rnd.uniform(-5, 5))
            lobes.append((x, y, sc * r * k * rnd.uniform(0.85, 1.15), 1.8, sy * rnd.uniform(0.8, 1.2),
                          angle + rnd.uniform(-0.1, 0.1), rnd.uniform(0.62, 0.78)))
        # The nose and the tail drawn out to points: a chain of ever smaller drops along the axis.
        for u0, d, n_ in ((60, 1, 4), (-62, -1, 5)):
            v = rnd.uniform(-3, 3)
            for j in range(n_):
                x, y = at(sc * (u0 + d * j * 9) + rnd.uniform(-2, 2), v * (1 + j * 0.4))
                f = 1 - j / n_
                lobes.append((x, y, sc * (5 + 9 * f) * k, 1.8, 0.5, angle, 0.7 * f))
        # Slivers peeling off above and below, swept back.
        for _ in range(rnd.integers(1, 4)):
            side = 1 if rnd.random() < 0.5 else -1
            x, y = at(sc * rnd.uniform(-40, 10), side * sc * rnd.uniform(17, 27))
            lobes.append((x, y, sc * rnd.uniform(16, 28) * k, 1.0, 0.13, angle - side * rnd.uniform(0.05, 0.3), 0.0))
        return m.field(lobes, n * 0.37, angle + math.pi, at(60, 0), 120 * k, 99.0, 1.0, crown=0.0, life=0.0)

    return field


def make_projectile():
    s = new("ex-fuego-proyectil-derecha", "Fuego · Proyectil a la derecha (bucle)", "Fire · Projectile right (loop)",
            "fuego", 48, 6009, ["fuego", "fire", "proyectil", "projectile", "bola de fuego", "fireball", "bucle", "loop"],
            size=512, thumb=0.3)
    s.fps = 24
    return render(s, projectile(512, 512, 37, size=1.3))


def splash_up(W, H, seed, size=1.0):
    """A splash of fire going up (RTFX's «Splash Up»): a narrow flame leaps up in wavy tongues, drops
    break off its tips and fly on up, and it sinks back into the ground leaving a few drops."""
    m = Mass(W, H, seed)
    rnd = np.random.default_rng(seed)
    k = size * m.gw / 256
    cx, base = m.gw / 2, m.gh * 0.96
    tongues = [(-12, 0.55, rnd.uniform(0, 6)), (0, 1.0, rnd.uniform(0, 6)), (13, 0.42, rnd.uniform(0, 6))]
    drops = [(rnd.uniform(0.1, 0.4), rnd.uniform(-26, 26), rnd.uniform(0.6, 1.0), rnd.uniform(3, 6))
             for _ in range(7)]

    def field(t):
        lobes = []
        grow = 1 - (1 - min(1.0, 0.25 + t / 0.17)) ** 2
        sink = max(0.0, (t - 0.38) / 0.25)
        tall = 230 * k * grow * (1 - 0.85 * min(1.0, sink))
        if tall > 2:
            for x0, h, ph in tongues:
                th = tall * h
                # A tongue: a stack of drawn-up drops narrowing to the tip, swaying as it rises.
                n = 9
                for j in range(n):
                    u = j / (n - 1)
                    sway = math.sin(t * 9 + ph + u * 3.2) * 12 * k * u
                    w = (46 - 34 * u) * k * (0.7 + 0.3 * grow)
                    lobes.append((cx + x0 * k + sway, base - th * u * 0.85, w, 0.75, 1.2 + 0.6 * u, sway * 0.01 / k,
                                  0.8 - 0.35 * u))
        for born, x0, s, v in drops:
            age = t - born
            if age < 0 or age > 0.6:
                continue
            # Drops leave the tips and fly on up, slowing and shrinking.
            y = base - tall * 0.95 - (v * 80 * age - 40 * age * age) * k
            r = (8 + 6 * s) * k * (1 - age / 0.6)
            lobes.append((cx + x0 * k * 0.6 + math.sin(age * 8) * 5 * k, y, r, 0.9, 1.15, 0.0, 0.55))
        return m.field(lobes, t, "up", (cx, base + 5 * k), 260 * k, 0.4, 0.45, crown=0.0, life=0.0)

    return field


def make_splash_up():
    s = new("ex-fuego-salpicadura-arriba", "Fuego · Salpicadura hacia arriba", "Fire · Splash up", "fuego", 28, 6010,
            ["fuego", "fire", "salpicadura", "splash", "llama", "flame"], size=512, thumb=0.2)
    s.fps = 24
    return render(s, splash_up(512, 512, 41, size=0.72))


def traced(curve, head, t, k, width=11.0, life=0.4, step=0.012, lick=0.0, rnd=None, thick=None, end=1.0, fade=0.8, hot=0.62):
    """Lobes along a path being drawn: curve(u) -> (x, y, tangent angle) for u in 0..1, the head at
    head (0..1+) of it. Each point flares up as the head passes, thickest just behind it, and thins
    away over life (in units of the path), so the tail breaks up as it goes. thick(u) shapes the line;
    the path ends at end (a closed curve can be run on past 1)."""
    lobes = []
    u = max(0.0, head - life * 1.3)
    while u <= min(head, end):
        age = (head - u) / life
        # Along the line it wobbles and, as it ages, breaks where it is weakest.
        nz = 0.5 + 0.5 * math.sin(u * 41 + 1.3) * math.sin(u * 17 + t * 3 + 0.4)
        gate = min(1.0, max(0.0, (nz + 0.55 - age * 1.1) * 3))
        w = width * k * min(1.0, age * 6 + 0.25) * max(0.0, 1 - age) ** fade * gate
        if thick:  # the line's shape shows while it is fresh
            w *= 1 + (thick(u) - 1) * max(0.0, 1 - age * 1.5)
        if w > 0.6:
            x, y, a = curve(u)
            wob = (math.sin(u * 140 + t * 5) + 0.7 * math.sin(u * 61 - t * 4)) * 1.6 * k
            x, y = x + math.cos(a + math.pi / 2) * wob, y + math.sin(a + math.pi / 2) * wob
            j = rnd.uniform(-1, 1) if rnd is not None else 0.0
            lobes.append((x, y, w * 2.2, 1.0, (0.42 + 0.1 * j) * (rnd.uniform(0.6, 1.3) if rnd is not None else 1.0),
                          a, hot * max(0.0, 1 - age * 1.4)))
            if lick and rnd.random() < lick:
                # A lick standing off the line, outward.
                o = a - math.pi / 2
                lobes.append((x + math.cos(o) * w * 1.2, y + math.sin(o) * w * 1.2, w * 1.4, 0.35, 1.0, a, 0.4))
        u += step
    return lobes


def trail_ring(W, H, seed, size=1.0):
    """A ring of fire being drawn (RTFX's «Trail Radial»): a flame runs round a circle from the top,
    thickest just behind its head, and the line it leaves thins and breaks into wisps behind it."""
    m = Mass(W, H, seed)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2
    R = 62 * k

    def circle(u):
        a = -math.pi / 2 + 2 * math.pi * u
        return cx + math.cos(a) * R, cy + math.sin(a) * R, a + math.pi / 2

    def field(t):
        rnd = np.random.default_rng(seed + int(round(t * 24)) // 2)
        head = 2.1 * t - 0.36 * (1 - math.exp(-t / 0.17))  # eases in, then runs on so the tail keeps dying
        lobes = traced(circle, head, t, k, width=8.0, life=0.85, lick=0.06, rnd=rnd, end=1.25, fade=0.7,
                       thick=lambda u: 0.6 + 1.0 * math.exp(-((u - 0.8) / 0.18) ** 2))
        return m.field(lobes, t, "radial", (cx, cy),
                       R * 1.2, 9.0, 1.0, crown=0.0, life=0.0)

    return field


def make_trail_ring():
    s = new("ex-fuego-estela-circular", "Fuego · Estela circular", "Fire · Ring trail", "fuego", 30, 6011,
            ["fuego", "fire", "estela", "trail", "círculo", "circle", "anillo", "ring"], size=512, thumb=0.45)
    s.fps = 24
    return render(s, trail_ring(512, 512, 43, size=1.5))


def charge(W, H, seed, size=1.0):
    """A fire charge (RTFX's «Charge Radial»): flaming loops whip round a centre on tilted orbits, one
    after another, crossing as they gather, then burn out from their tails leaving an arc on top."""
    m = Mass(W, H, seed)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2
    # (rx, ry, tilt, start angle, delay, width, centre offset)
    orbits = [(70, 52, -0.45, -2.6, 0.0, 6.5, (-6, 4)), (84, 36, 0.75, -0.6, 0.12, 6.0, (10, 2)),
              (56, 72, 0.1, 2.0, 0.24, 5.5, (-4, -8))]

    def orbit(rx, ry, tilt, a0, off):
        ox, oy = cx + off[0] * k, cy + off[1] * k

        def curve(u):
            a = a0 + 2 * math.pi * u
            x, y = math.cos(a) * rx * k, math.sin(a) * ry * k
            c, s_ = math.cos(tilt), math.sin(tilt)
            tx, ty = -math.sin(a) * rx, math.cos(a) * ry
            return ox + x * c - y * s_, oy + x * s_ + y * c, math.atan2(tx * s_ + ty * c, tx * c - ty * s_)
        return curve

    curves = [orbit(rx, ry, tilt, a0, off) for rx, ry, tilt, a0, _, _, off in orbits]

    def field(t):
        rnd = np.random.default_rng(seed + int(round(t * 24)) // 2)
        lobes = []
        for (rx, ry, tilt, a0, delay, w, off), curve in zip(orbits, curves):
            tt = t - delay
            if tt <= 0:
                continue
            head = 2.0 * tt - 0.3 * (1 - math.exp(-tt / 0.15))
            lobes += traced(curve, head, tt, k, width=w, life=0.7, lick=0.08, rnd=rnd, end=1.1, fade=0.7, hot=0.85,
                            thick=lambda u: 0.7 + 0.7 * math.exp(-((u - 0.55) / 0.25) ** 2))
        return m.field(lobes, t, "radial", (cx, cy), 70 * k, 9.0, 1.0, crown=0.0, life=0.0)

    return field


def make_charge():
    s = new("ex-fuego-carga-circular", "Fuego · Carga circular", "Fire · Radial charge", "fuego", 34, 6012,
            ["fuego", "fire", "carga", "charge", "poder", "power", "aura"], size=512, thumb=0.45)
    s.fps = 24
    return render(s, charge(512, 512, 47, size=1.25))


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


STICKERS = [make_explosion, make_torch, make_thrower, make_wings, make_ring, make_slash, make_ray, make_hit_up, make_shot_hit, make_projectile, make_splash_up, make_trail_ring, make_charge]
