"""Animaciones Extremas, second try (0.26): the first set (particle soups, rtfx_*.py) was rejected and taken
down. Prototype of the field engine — one mass per effect, tones cut from it, torn into strands as it
dies — matched side by side against RTFX Fire 037. Run: python rtfx_field_proto.py boom|torch out.png"""
import math, sys
import numpy as np
import cv2

G = 256
SIZE = 512
yy, xx = np.mgrid[0:G, 0:G].astype(np.float32)


class Tex:
    """A wrapping value-noise texture sampled anywhere (cubic)."""
    def __init__(self, seed, n=64):
        self.t = np.random.default_rng(seed).random((n, n)).astype(np.float32)
        self.n = n

    def __call__(self, u, v):
        return cv2.remap(self.t, (u % self.n).astype(np.float32), (v % self.n).astype(np.float32),
                         cv2.INTER_CUBIC, borderMode=cv2.BORDER_WRAP)

    def fbm(self, u, v, octaves=3):
        out = np.zeros_like(u)
        a, f, tot = 1.0, 1.0, 0.0
        for o in range(octaves):
            out += a * self(u * f + o * 17.3, v * f + o * 9.1)
            tot += a
            a *= 0.5
            f *= 2.0
        return out / tot


def gauss(X, Y, cx, cy, r, sx=1.0, sy=1.0, ang=0.0):
    dx, dy = X - cx, Y - cy
    if ang:
        c, s = math.cos(ang), math.sin(ang)
        dx, dy = c * dx + s * dy, -s * dx + c * dy
    q = (dx / (r * sx)) ** 2 + (dy / (r * sy)) ** 2
    # Flat-topped with a steep edge: puffs keep their round edge where they meet (scallops).
    return np.exp(-q * q)


class Fire:
    def __init__(self, seed):
        self.cell = Tex(seed)
        self.streak = Tex(seed + 1)
        self.warp = Tex(seed + 2)

    def field(self, lobes, t, life, flow, origin, reach):
        """lobes: [(cx, cy, r, sx, sy, ang)]. flow: 'up' or 'radial'. Returns (outer, core) fields."""
        wx = (self.warp.fbm(xx * 0.022, yy * 0.022 + t * 1.5, 2) - 0.5) * 12
        wy = (self.warp.fbm(xx * 0.022 + 40, yy * 0.022 + t * 1.5, 2) - 0.5) * 8
        X, Y = xx + wx, yy + wy
        mx = np.zeros((G, G), np.float32)
        sm = np.zeros((G, G), np.float32)
        holes = np.zeros((G, G), np.float32)
        mc = np.zeros((G, G), np.float32)
        for lobe in lobes:
            cx, cy, r, sx, sy, ang = lobe[:6]
            g = gauss(X, Y, cx, cy, r, sx, sy, ang)
            mx = np.maximum(mx, g)
            sm += g
            # Each puff has its own yellow ball; between balls the red shows through.
            cf = lobe[8] if len(lobe) > 8 else 0.85
            if cf > 0.05:
                mc = np.maximum(mc, gauss(X, Y, cx, cy, r * cf, sx, sy, ang))
            if len(lobe) > 6 and lobe[6] > 0:
                k = lobe[6]
                holes = np.maximum(holes, gauss(X, Y, cx + lobe[7] * r * 0.3, cy + r * 0.5, r * (0.3 + 0.9 * k), 1.0, 1.1))
        d = mx + 0.05 * np.clip(sm, 0, 2) - 1.5 * holes
        dc = mc - 1.5 * holes
        # Tearing: noise stretched along the flow, eating the outside first.
        ox, oy = origin
        if flow == "radial":
            ang = np.arctan2(yy - oy, xx - ox)
            rad = np.hypot(xx - ox, yy - oy)
            bend = (self.warp.fbm(xx * 0.03 + 7, yy * 0.03 + 3, 2) - 0.5) * 6
            su, sv = ang * 32 / math.pi + rad * 0.05 + bend, rad * 0.02 - t * 1.6
            far = np.clip(rad / reach, 0, 1)
        else:
            su, sv = xx * 0.16, yy * 0.022 + t * 2.0
            far = np.clip((oy - yy) / reach, 0, 1)
        st = self.streak.fbm(su, sv, 2)
        # A shredding front runs in from the outside: past it the mass tears into strands along the
        # flow; behind it the mass is whole. At the end everything goes.
        prog = min(1.0, max(0.0, (t - 0.5) / 0.8))
        front = np.clip((far - (1.0 - prog * 1.35)) / 0.3, 0, 1)
        # Gaps open where the streak noise is high; where it is low the strands stay, drawn out.
        cut = 0.47 - 0.12 * prog
        gap = np.clip((st - cut) / 0.07, 0, 1)
        keep = np.clip((cut - st) / 0.07, 0, 1)
        eat = front * (1.6 * gap - 0.15 * keep * (1 - prog)) + prog ** 3 * 0.9
        d = d - eat
        dc = dc - 0.08 * eat
        # The core: the same mass with cauliflower bumps, shrinking as it burns out.
        cauli = self.cell.fbm(xx * 0.07, yy * 0.07 - t * 1.2, 2) - 0.5
        # The top of the mass runs red (the crown), the middle stays hot longest.
        top = np.clip((oy - yy) / reach, 0, 1) if flow == 'radial' else 0.0
        d = d + 0.18 * cauli
        core = dc + 0.5 * cauli + 0.06 - 0.05 * life - 0.9 * life * far - 0.35 * top * min(1.0, t / 0.4)
        return d, core


def draw(d, core, life):
    up = cv2.resize(d, (SIZE, SIZE), interpolation=cv2.INTER_CUBIC)
    cu = cv2.resize(core, (SIZE, SIZE), interpolation=cv2.INTER_CUBIC)
    img = np.zeros((SIZE, SIZE, 3), np.float32)
    red, orange, yellow = (0.03, 0.08, 1.0), (0.02, 0.42, 1.0), (0.6, 0.97, 1.0)
    rim = up > 0.45
    img[rim] = red
    # Orange is only a thin edge round the yellow, as RTFX draws it.
    img[cu > 0.55] = orange
    img[cu > 0.62] = yellow
    glow = cv2.GaussianBlur(rim.astype(np.float32), (0, 0), 16)
    out = img + (~rim)[..., None] * glow[..., None] * np.array(red) * 1.0
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


def torch_lobes(t, rnd):
    lobes = []
    for i, p in enumerate(rnd):
        h = p[0]
        born = h * 0.28
        age = t - born
        if age < 0 or age > 1.25:
            continue
        side = 1 if i % 2 else -1
        cx = G / 2 + math.sin(h * 4.0 + 0.4) * 26 * h + side * 9 * (1 - h) + p[1] * 4
        cy = G * 0.8 - h * 140 - age * 40
        r = (5 + 17 * min(1, age / 0.18)) * p[2] * (1.1 - 0.5 * h) * (1 - 0.3 * max(0, age - 0.6))
        lean = 1.6 * (h - 0.7) / 0.3 if h > 0.7 else 0.0
        hole = max(0.0, (age / 1.25 - 0.4) / 0.6)
        lobes.append((cx, cy, r, 1.0, 1.15 + 0.7 * h * h, lean, hole, p[1]))
    return lobes


# A cartoon explosion is a pyramid of puffs: three at the base, two above, one on top, small ones
# filling the gaps (offsets in units of the final radius).
PYRAMID = [(0.0, 0.3, 0.7), (-1.05, 0.55, 1.0), (0.0, 0.62, 1.05), (1.05, 0.55, 1.0), (-0.55, -0.15, 1.0), (0.55, -0.15, 1.0),
           (0.0, -0.85, 1.0), (-0.5, 0.25, 0.7), (0.5, 0.25, 0.7), (0.0, 0.1, 0.8), (-0.3, -0.55, 0.65),
           (0.3, -0.55, 0.65), (-1.3, 0.85, 0.5), (1.3, 0.85, 0.5)]


def boom_lobes(t, rnd):
    lobes = []
    R = 31
    e = 1 - (1 - min(1, t / 0.22)) ** 3
    for i, (ox, oy, k) in enumerate(PYRAMID):
        jx, jy, js = rnd[i]
        cx = G / 2 + (ox + jx * 0.12) * R * 1.25 * e
        cy = G * 0.6 + (oy + jy * 0.12) * R * 1.15 * e - 14 * t
        r = (4 + R * 0.85 * e) * k * (0.9 + 0.2 * js) * (1 - 0.15 * max(0, t - 0.6))
        # The yellow leaves the puffs far from the heart first, the top ones soonest (the red crown).
        dist = math.hypot(ox, oy - 0.3) * 0.8 + (0.5 if oy < -0.3 else 0.0)
        cf = 0.85 * max(0.0, min(1.0, 1.0 - max(0.0, t - 0.62 + 0.08 * dist) * (0.6 + 1.4 * dist)))
        lobes.append((cx, cy, r, 1.0, 0.95, 0.0, 0.0, 0.0, cf))
    return lobes


def run(kind, out_path):
    fire = Fire(5)
    rng = np.random.default_rng(12)
    if kind == "torch":
        rnd = [(i / 9, rng.uniform(-1, 1), rng.uniform(0.8, 1.15)) for i in range(10)]
    else:
        rnd = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.random()) for i in range(14)]
    frames = []
    for f in range(0, 46, 2):
        t = f / 24
        life = min(1.0, t / (1.5 if kind == "torch" else 1.6))
        if kind == "torch":
            d, c = fire.field(torch_lobes(t, rnd), t, life, "up", (G / 2, G * 0.85), 170)
        else:
            d, c = fire.field(boom_lobes(t, rnd), t, life, "radial", (G / 2, G * 0.58), 110)
        frames.append(draw(d, c, life))
    crop = [fr[0:480, 66:446] for fr in frames]
    rows = [np.hstack(crop[i:i + 8] + [np.zeros_like(crop[0])] * (8 - len(crop[i:i + 8]))) for i in range(0, len(crop), 8)]
    cv2.imwrite(out_path, np.vstack(rows))


run(sys.argv[1], sys.argv[2])
