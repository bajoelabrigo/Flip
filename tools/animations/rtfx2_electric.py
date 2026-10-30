"""Animaciones Extremas · Electricidad (0.26), on the field engine of rtfx2_fire.py.

Electricity is thin jagged lines: a bolt is a polyline whose points are jittered across it, drawn as
short capsules with a white heart, and redrawn on every second frame so it crackles. Bolts run in
lines, round circles and rings. Studied against RTFX's electricity previews frame by frame (see
feedback: study before generating).
"""

from __future__ import annotations

import math

import numpy as np

from rtfx2_fire import Mass, looped
from rtfx_field import render
from rtfx_engine import new

TONES = [("azul eléctrico", "#2f5bff"), ("celeste", "#8fb8ff"), ("blanco", "#f4f8ff")]
GLOW = 26
HALO = [("#1d45ff", 60, 90), ("#5a8cff", 16, 95)]


def bolt(pts, k, w=2.3, heart=0.72):
    """Capsules along the polyline pts, w (grid cells at k=1) thick."""
    lobes = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0) / 2
        if L < 0.1:
            continue
        # Long enough that its white heart (heart × its length) still reaches the next segment.
        r = L / heart + w * k * 0.5
        lobes.append(((x0 + x1) / 2, (y0 + y1) / 2, r, 1.0, w * k / r, math.atan2(y1 - y0, x1 - x0), heart))
    return lobes


def jagged(path, n, amp, rnd):
    """n + 1 points along path(u) -> (x, y, angle), each pushed across the path by up to amp."""
    pts = []
    for i in range(n + 1):
        x, y, a = path(i / n)
        o = rnd.uniform(-amp, amp) if 0 < i < n else 0.0
        pts.append((x - math.sin(a) * o, y + math.cos(a) * o))
    return pts


def ray(W, H, seed, size=1.0):
    """A bolt of lightning shooting right (RTFX's «Electricity Ray Right»): a jagged line flickers
    across, redrawn every second frame, its far end thrashing, gone after a moment."""
    m = Mass(W, H, seed, rough=0.0)
    k = size * m.gw / 256
    x0, x1, y = m.gw * 0.2, m.gw * 0.8, m.gh / 2

    def field(t):
        n = int(round(t * 24)) // 2
        rnd = np.random.default_rng(seed * 100 + n)
        lobes = []
        if t < 0.3:
            reach = min(1.0, t / 0.08)
            line = lambda u: (x0 + (x1 - x0) * u * reach, y, 0.0)
            pts = jagged(line, 16, 9 * k, rnd)
            # The end thrashes: a zigzag that grows towards it.
            pts = [(x, y + (yy - y) * (0.6 + 1.6 * (i / 16) ** 3)) for i, (x, yy) in enumerate(pts)]
            lobes = bolt(pts, k)
        return m.field(lobes, t, "radial", (m.gw / 2, y), 100 * k, 9.0, 1.0, crown=0.0, life=0.0)

    return field


def make_ray():
    s = new("ex-electricidad-rayo-derecha", "Electricidad · Rayo a la derecha", "Electricity · Bolt right",
            "electricidad", 14, 9000, ["electricidad", "electricity", "rayo", "lightning", "bolt", "chispa"],
            size=512, thumb=0.3)
    s.fps = 24
    return render(s, ray(512, 512, 3, size=1.4), tones=TONES, halo=HALO)


def charge(W, H, seed, size=1.0, period=1.5):
    """Crackling charge, looping (RTFX's «Electricity Charge Radial Loop»): jagged arcs of lightning
    flicker round a centre, one or two at a time, each drawing on a new part of the circle."""
    m = Mass(W, H, seed, rough=0.0)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2

    def lobes_at(t):
        n = int(round(t * 24)) // 2
        rnd = np.random.default_rng(seed * 100 + n % int(round(period * 12)))
        lobes = []
        if n % 5 == 3:
            return lobes  # a dark frame now and then
        for _ in range(int(rnd.integers(1, 3))):
            a0 = rnd.uniform(0, 2 * math.pi)
            span = rnd.uniform(1.4, 2.6)
            R = rnd.uniform(30, 38) * k
            arc = lambda u, a0=a0, span=span, R=R: (cx + math.cos(a0 + span * u) * R, cy + math.sin(a0 + span * u) * R,
                                                    a0 + span * u + math.pi / 2)
            lobes += bolt(jagged(arc, 14, 5 * k, rnd), k)
        return lobes

    return looped(m, lobes_at, period, "radial", (cx, cy), 60 * k)


def make_charge():
    s = new("ex-electricidad-carga", "Electricidad · Carga eléctrica (bucle)", "Electricity · Electric charge (loop)",
            "electricidad", 36, 9001, ["electricidad", "electricity", "carga", "charge", "rayo", "lightning", "bucle",
                                       "loop"], loop=True, size=512, thumb=0.5)
    s.fps = 24
    return render(s, charge(512, 512, 5, size=1.6), tones=TONES, halo=HALO)


def blast(W, H, seed, size=1.0):
    """An electric blast (RTFX's «Electricity Explosion Radial»): a knot of lightning swells into a
    crackling ring whose jagged edge grows outward, with a few bolts left inside, then it vanishes."""
    m = Mass(W, H, seed, rough=0.0)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2

    def field(t):
        n = int(round(t * 24)) // 2
        rnd = np.random.default_rng(seed * 100 + n)
        lobes = []
        if t < 0.45:
            e = 1 - (1 - min(1.0, t / 0.4)) ** 2
            R = (6 + 34 * e) * k
            loop_ = lambda u: (cx + math.cos(2 * math.pi * u) * R, cy + math.sin(2 * math.pi * u) * R * 0.92,
                               2 * math.pi * u + math.pi / 2)
            lobes += bolt(jagged(loop_, 20, (3 + 5 * e) * k, rnd), k, w=2.4)
            for _ in range(int(rnd.integers(1, 4))):  # bolts inside
                a = rnd.uniform(0, 2 * math.pi)
                r0, r1 = rnd.uniform(0, 0.4) * R, rnd.uniform(0.5, 0.9) * R
                seg = lambda u, a=a, r0=r0, r1=r1: (cx + math.cos(a) * (r0 + (r1 - r0) * u),
                                                     cy + math.sin(a) * (r0 + (r1 - r0) * u), a)
                lobes += bolt(jagged(seg, 5, 3 * k, rnd), k, w=1.3)
        return m.field(lobes, t, "radial", (cx, cy), 60 * k, 9.0, 1.0, crown=0.0, life=0.0)

    return field


def make_blast():
    s = new("ex-electricidad-estallido", "Electricidad · Estallido eléctrico", "Electricity · Electric blast",
            "electricidad", 14, 9002, ["electricidad", "electricity", "estallido", "blast", "explosión", "explosion",
                                       "golpe", "hit"], size=512, thumb=0.6)
    s.fps = 24
    return render(s, blast(512, 512, 7, size=1.6), tones=TONES, halo=HALO)


def coil(W, H, seed, size=1.0, period=1.33):
    """An electric coil, looping (RTFX's «Electricity Up Loop»): flat rings of lightning seen from the
    side, stacked up a column, flickering on and off and climbing as they are redrawn."""
    m = Mass(W, H, seed, rough=0.0)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2

    def lobes_at(t):
        n = int(round(t * 24)) // 2
        rnd = np.random.default_rng(seed * 100 + n % int(round(period * 12)))
        lobes = []
        for j in range(2):
            if rnd.random() < 0.2:
                continue
            y = cy + (j - 0.5) * 30 * k - ((n % 4) * 6) * k
            rx = 30 * k * rnd.uniform(0.85, 1.15)
            a0, span = rnd.uniform(0, math.pi), rnd.uniform(3.4, 5.6)
            ell = lambda u, y=y, rx=rx, a0=a0, span=span: (cx + math.cos(a0 + span * u) * rx,
                                                           y + math.sin(a0 + span * u) * rx * 0.28,
                                                           a0 + span * u + math.pi / 2)
            lobes += bolt(jagged(ell, 14, 3 * k, rnd), k, w=2.4)
        return lobes

    return looped(m, lobes_at, period, "up", (cx, cy + 30 * k), 60 * k)


def make_coil():
    s = new("ex-electricidad-espiral", "Electricidad · Espiral eléctrica (bucle)", "Electricity · Electric coil (loop)",
            "electricidad", 32, 9003, ["electricidad", "electricity", "espiral", "coil", "anillos", "rings", "bucle",
                                       "loop"], loop=True, size=512, thumb=0.5)
    s.fps = 24
    return render(s, coil(512, 512, 9, size=1.6), tones=TONES, halo=HALO)


STICKERS = [make_ray, make_charge, make_blast, make_coil]
