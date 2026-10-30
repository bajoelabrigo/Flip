"""Animaciones Extremas · Chispas (0.26), on the field engine of rtfx2_fire.py.

Sparks are many tiny hot drops: each a small puff with a white-gold heart, thrown out fast, slowed
by drag, pulled down a little, flickering and shrinking as they cool. A spark crown on the ground is
a ring of needles redrawn every third frame. Studied against RTFX's sparks previews frame by frame
(see feedback: study before generating).
"""

from __future__ import annotations

import math

import numpy as np

from rtfx2_fire import Mass, looped
from rtfx_field import render
from rtfx_engine import new

TONES = [("naranja chispa", "#ff7400"), ("dorado", "#ffc23a"), ("amarillo claro", "#fff4c4")]
GLOW = 14
HALO = [("#ff5a00", 46, 85), ("#ffa21c", 12, 95)]


def flight(t, v, drag, g):
    """Distance along a throw at speed v after t seconds with drag (1/s), and the drop under gravity g."""
    d = v * (1 - math.exp(-drag * t)) / drag
    return d, 0.5 * g * t * t


def burst(W, H, seed, size=1.0, n=46, spread=None, life=0.9):
    """Sparks bursting out of a point (RTFX's «Sparks Hit Explosion Radial»): drops thrown all ways at
    different speeds, slowing fast, sinking a little, each flickering and shrinking until it dies.
    spread, when given, is a list of directions (radians) the sparks keep close to, in streams."""
    m = Mass(W, H, seed, rough=0.0)
    rnd = np.random.default_rng(seed)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2
    sparks = []
    for i in range(n):
        if spread:
            a = spread[i % len(spread)] + rnd.normal(0, 0.12)
        else:
            a = rnd.uniform(0, 2 * math.pi)
        sparks.append((a, rnd.uniform(110, 400), rnd.uniform(0.6, 1.0) * life, rnd.uniform(2.4, 4.2), rnd.random()))

    def field(t):
        lobes = []
        for a, v, die, r, ph in sparks:
            if t > die:
                continue
            d, drop = flight(t, v * k, 4.5, 15 * k)
            f = 1 - t / die
            flick = 0.75 + 0.25 * math.sin(t * 40 + ph * 9)
            rr = r * k * (0.45 + 0.55 * f) * flick * min(1.0, t / 0.04 + 0.3)
            lobes.append((cx + math.cos(a) * d, cy + math.sin(a) * d + drop, rr, 1.0, 1.0, 0.0, 0.75 * f + 0.1))
        return m.field(lobes, t, "radial", (cx, cy), 90 * k, 9.0, 1.0, crown=0.0, life=0.0)

    return field


def make_burst():
    s = new("ex-chispas-estallido", "Chispas · Estallido", "Sparks · Burst", "chispas", 24, 8000,
            ["chispas", "sparks", "estallido", "burst", "golpe", "hit", "metal"], size=512, thumb=0.25)
    s.fps = 24
    return render(s, burst(512, 512, 5, size=1.3), tones=TONES, halo=HALO, slots=(70, 60, 60))


def make_streams():
    s = new("ex-chispas-chorros", "Chispas · Chorros en cruz", "Sparks · Cross streams", "chispas", 22, 8001,
            ["chispas", "sparks", "golpe", "hit", "soldadura", "welding", "metal"], size=512, thumb=0.25)
    s.fps = 24
    dirs = [-2.2, -1.1, -0.2, 0.9, 2.0, 2.9]
    return render(s, burst(512, 512, 7, size=1.3, n=40, spread=dirs, life=0.75), tones=TONES, halo=HALO,
                  slots=(60, 50, 50))


def fountain(W, H, seed, size=1.0, n=40):
    """A fountain of sparks (RTFX's «Sparks Explosion Up»): thrown up from the ground in a fan, they arc
    over and fall, and the ones that land skitter along the floor and glow there before going out."""
    m = Mass(W, H, seed, rough=0.0)
    rnd = np.random.default_rng(seed)
    k = size * m.gw / 256
    cx, ground = m.gw / 2, m.gh * 0.82
    sparks = [(-math.pi / 2 + rnd.normal(0, 0.25), rnd.uniform(70, 170), rnd.uniform(0.0, 0.12),
               rnd.uniform(2.0, 3.5), rnd.random(), rnd.uniform(1.1, 1.8)) for _ in range(n)]

    def field(t):
        lobes = []
        for a, v, born, r, ph, die in sparks:
            tt = t - born
            if tt <= 0 or tt > die:
                continue
            vx, vy = math.cos(a) * v * k, math.sin(a) * v * k
            g = 260 * k
            # Up and over, landing when it gets back to the ground, then sliding on with friction.
            t_land = -2 * vy / g
            if tt < t_land:
                x = cx + vx * tt
                y = ground + vy * tt + 0.5 * g * tt * tt
            else:
                s_ = tt - t_land
                x = cx + vx * t_land + vx * (1 - math.exp(-6 * s_)) / 12
                y = ground
            f = 1 - tt / die
            flick = 0.7 + 0.3 * math.sin(tt * 37 + ph * 9)
            lobes.append((x, y - r * k * 0.3, r * k * (0.5 + 0.5 * f) * flick, 1.0, 1.0, 0.0, 0.7 * f + 0.1))
        return m.field(lobes, t, "up", (cx, ground), 120 * k, 9.0, 1.0, crown=0.0, life=0.0)

    return field


def make_fountain():
    s = new("ex-chispas-fuente", "Chispas · Fuente de chispas", "Sparks · Spark fountain", "chispas", 48, 8002,
            ["chispas", "sparks", "fuente", "fountain", "metal", "soldadura", "welding"], size=512, thumb=0.2)
    s.fps = 24
    return render(s, fountain(512, 512, 11, size=1.3), tones=TONES, halo=HALO, slots=(60, 50, 50))


def crown(W, H, seed, size=1.0, period=1.5):
    """A crown of sparks on the ground, looping (RTFX's «Sparks loop Up»): a burst of flame needles fans
    up from a point on the floor, a different set every third frame, now low and wide, now with one
    long spike shooting up, as when metal is ground."""
    m = Mass(W, H, seed, rough=0.0)
    k = size * m.gw / 256
    cx, ground = m.gw / 2, m.gh * 0.7

    def lobes_at(t):
        n = int(round(t * 24)) // 3
        rnd = np.random.default_rng(seed * 100 + n % int(round(period * 8)))
        lobes = [(cx, ground - 3 * k, 36 * k, 1.0, 0.17, 0.0, 0.9)]  # the bright bed
        for i in range(rnd.integers(10, 15)):
            a = -math.pi / 2 + rnd.uniform(-1.45, 1.45)
            L = rnd.uniform(8, 22) * k * (1.6 if abs(a + math.pi / 2) > 1.1 else 1.0)
            if i == 0 and rnd.random() < 0.5:
                a, L = -math.pi / 2 + rnd.uniform(-0.6, 0.6), rnd.uniform(34, 46) * k  # the long spike
            x0 = cx + rnd.uniform(-12, 12) * k
            lobes.append((x0 + math.cos(a) * L * 0.55, ground - 3 * k + math.sin(a) * L * 0.55, L * 0.55, 1.0,
                          rnd.uniform(0.16, 0.26), a, 0.85))
        return lobes

    return looped(m, lobes_at, period, "up", (cx, ground), 60 * k)


def make_crown():
    s = new("ex-chispas-corona-suelo", "Chispas · Corona en el suelo (bucle)", "Sparks · Ground crown (loop)",
            "chispas", 36, 8003, ["chispas", "sparks", "suelo", "ground", "esmeril", "grinder", "metal", "bucle",
                                  "loop"], loop=True, size=512, thumb=0.5)
    s.fps = 24
    return render(s, crown(512, 512, 13, size=1.6),
                  tones=[("rojo chispa", "#ff3a0a"), ("naranja", "#ff9a1f"), ("amarillo claro", "#fff4c4")],
                  halo=[("#ff3a00", 60, 85), ("#ff8a10", 18, 95)])


STICKERS = [make_burst, make_streams, make_fountain, make_crown]
