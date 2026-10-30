"""Animaciones Extremas · Humo (0.26): one element of our own for each of RTFX's 61 smoke ones, by kind,
direction, timing and palette (their names and previews only told us what each one does).

Cartoon smoke: round puffs that billow, swell and fade by shrinking, in a light tone over a grey
shade set down and to the right (no glow). Bursts out of a hit, a ring of puffs, trails left behind
something moving, columns rising, thin wisps curling up, a wall of smoke along the bottom.
"""

from __future__ import annotations

import math
import random

from rtfx_engine import STEP, Layers, Particle, Sim, new, particle_outline
from rtfx_fire import emit

PALETTES = {
    "blanco": ("#8f949c", "#f4f4f2"),
    "gris": ("#5d6168", "#b9bcc2"),
    "azul": ("#7fa3bd", "#e6f4ff"),
    "oscuro": ("#2c2f35", "#5f636b"),
}
DIRS = {"up": -math.pi / 2, "down": math.pi / 2, "right": 0.0, "left": math.pi}


def puffs(sim, rnd, n, t0, t1, origin, angle, spread, speed, size, life, lift=60.0, drag=3.0, grow=0.35):
    emit(sim, rnd, n, t0, t1, origin, angle, spread, speed, size, life, lift=lift, drag=drag, shape="puff",
         grow=grow)


def build(kind, d, loop, W, H, dur, seed, k):
    rnd = random.Random(seed)
    sim = Sim(dur, loop=loop)
    cx, cy = W / 2, H / 2
    a = DIRS.get(d, -math.pi / 2)
    radial = d == "radial"
    S = min(W, H)
    if kind == "explosion":
        o = (cx, cy) if radial else (cx, H * 0.78) if d == "up" else (cx - math.cos(a) * W * 0.2, cy - math.sin(a) * H * 0.2)
        spread = math.pi if radial else rnd.uniform(0.5, 0.9)
        puffs(sim, rnd, int(22 * rnd.uniform(0.8, 1.3)), 0, 0.12, o, a, spread, (320, 820), (40 * k, 70 * k),
              (0.9, 1.4), lift=40 if radial else 120, drag=3.2)
        if d == "up" and rnd.random() < 0.6:
            # A mushroom: the stem rising under the cap.
            puffs(sim, rnd, 10, 0.05, 0.4, o, -math.pi / 2, 0.15, (120, 260), (22 * k, 34 * k), (0.7, 1.1),
                  lift=80, drag=2.0)
    elif kind == "hit":
        o = (cx, cy) if radial else (cx - math.cos(a) * W * 0.12, cy - math.sin(a) * H * 0.12)
        puffs(sim, rnd, 12, 0, 0.08, o, a, math.pi if radial else 0.6, (200, 500), (24 * k, 42 * k), (0.6, 0.9),
              lift=30, drag=4.0)
    elif kind == "radial":
        n = rnd.randint(9, 14)
        r0 = S * rnd.uniform(0.05, 0.12)
        for i in range(n):
            ang = 2 * math.pi * i / n + rnd.uniform(-0.1, 0.1)
            v = rnd.uniform(380, 520)
            sim.add(Particle(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0, math.cos(ang) * v, math.sin(ang) * v,
                             rnd.uniform(0, 0.05), rnd.uniform(0.9, 1.3), rnd.uniform(26 * k, 40 * k),
                             rnd.randrange(1 << 20), lift=20, drag=4.0, grow=0.3, shape="puff"))
        if loop:
            for i in range(n):
                ang = 2 * math.pi * (i + 0.5) / n
                sim.add(Particle(cx, cy, math.cos(ang) * 400, math.sin(ang) * 400, dur / 2, 1.2, 30 * k,
                                 rnd.randrange(1 << 20), lift=20, drag=4.0, grow=0.3, shape="puff"))
    elif kind == "trail":
        def at(t):
            u = min(1.0, t / (dur * (0.95 if loop else 0.5)))
            if loop:
                u = (t / dur) % 1.0
            return (W * (0.1 + 0.8 * u) if d != "left" else W * (0.9 - 0.8 * u),
                    cy + math.sin(u * math.pi * 2 + seed) * 18)
        puffs(sim, rnd, 40, 0, dur * (0.95 if loop else 0.5), at, -math.pi / 2, 1.0, (10, 50), (14 * k, 28 * k),
              (0.6, 1.0), lift=40, drag=2.0)
    elif kind == "slash":
        r = S * 0.3
        a0 = -2.4 if d == "right" else -0.8
        for i in range(24):
            ang = a0 + 2.0 * i / 24
            sim.add(Particle(cx + math.cos(ang) * r, cy + math.sin(ang) * r * 0.8, -math.sin(ang) * 60, math.cos(ang) * 60,
                             0.25 * i / 24, rnd.uniform(0.6, 0.9), rnd.uniform(12 * k, 22 * k), rnd.randrange(1 << 20),
                             lift=30, drag=2.0, grow=0.4, shape="puff"))
    elif kind == "column":
        puffs(sim, rnd, 40, 0, dur * (0.95 if loop else 0.6), (cx, H * 0.88), -math.pi / 2, 0.25, (120, 260),
              (34 * k, 62 * k), (1.0, 1.5), lift=50, drag=1.0, grow=0.45)
    elif kind == "wisp":
        # A thin curl rising: small puffs born along an S that sways as it climbs.
        for i in range(60):
            b = (dur * (0.95 if loop else 0.5)) * i / 60
            x = cx + math.sin(b * 6 + seed) * 30
            sim.add(Particle(x, H * 0.9, math.sin(b * 9 + seed) * 60, -rnd.uniform(260, 340), b, rnd.uniform(0.8, 1.1),
                             rnd.uniform(11 * k, 17 * k), rnd.randrange(1 << 20), lift=0, drag=0.6, grow=0.6,
                             shape="puff"))
    elif kind == "shot":
        start = (cx, H * 0.85) if d == "up" else (W * 0.1, cy)
        ang = -math.pi / 2 if d == "up" else 0.0
        puffs(sim, rnd, 30, 0, 0.35, lambda t: (start[0] + math.cos(ang) * 1100 * t, start[1] + math.sin(ang) * 1100 * t),
              ang + math.pi, 0.6, (20, 80), (10 * k, 20 * k), (0.4, 0.7), lift=30, drag=2.5)
        end = (start[0] + math.cos(ang) * 1100 * 0.35, start[1] + math.sin(ang) * 1100 * 0.35)
        end = (min(max(end[0], W * 0.2), W * 0.8), min(max(end[1], H * 0.2), H * 0.8))
        puffs(sim, rnd, 14, 0.35, 0.45, end, ang + math.pi, math.pi, (150, 400), (28 * k, 44 * k), (0.7, 1.0),
              lift=40, drag=3.5)
    elif kind == "wide":
        for i in range(12):
            x = W * (0.04 + 0.92 * i / 11)
            puffs(sim, rnd, 5 if loop else 3, 0 if not loop else 0, dur * (0.95 if loop else 0.2), (x, H * 0.98),
                  -math.pi / 2, 0.5, (80, 220), (40 * k, 70 * k), (1.0, 1.6), lift=40, drag=1.5)
    return sim


def classify(name):
    n = name.lower()
    d = ("radial" if "radial" in n else "up" if "up" in n else "left" if "left" in n else "right" if "right" in n
         else "horizontal" if "horizontal" in n else "up")
    loop = "loop" in n
    for words, kind in (("wide", "wide"), ("explosi", "explosion"), ("slash", "slash"), ("trail", "trail"),
                        ("shot", "shot"), ("ray", "wisp"), ("hit", "hit"), ("radial", "radial"), ("right", "trail")):
        if words in n:
            break
    else:
        kind = "column" if loop or "up" in n else "wisp"
    if kind == "shot" and d not in ("up", "right"):
        d = "up"
    return kind, d, loop


ES_KIND = {"explosion": "Estallido", "hit": "Golpe", "radial": "Anillo", "trail": "Estela", "slash": "Barrido",
           "column": "Columna", "wisp": "Voluta", "shot": "Disparo", "wide": "Muro"}
EN_KIND = {"explosion": "Burst", "hit": "Hit", "radial": "Ring", "trail": "Trail", "slash": "Sweep",
           "column": "Column", "wisp": "Wisp", "shot": "Shot", "wide": "Wall"}
ES_DIR = {"up": "arriba", "right": "derecha", "left": "izquierda", "radial": "radial", "horizontal": "horizontal"}

NAMES = """001 Hit Explosion Up|002 Hit Explosion Radial|003 Up|004 Hit Explosion Radial|005 Trail Right|
006 Explosion Radial|007 Trail Right|008 Radial|009 Hit Explosion Up|010 Slash Right|011 Slash Right|012 Hit Radial|
013 Radial|014 Hit Up|015 Hit Left|016 Shot Up|017 Up Loop|018 Hit Right|019 Shot Right|020 Trail Right loop|
021 Explosion Up|022 Hit Explosion Radial|025 Explosion Up|026 Up|027 Explosion Up|028 Explosion Up|
029 Hit Explosion Up|030 Shot Hit Explosion Up|031 Hit Explosion Radial|034 Up|035 Hit Left|036 Shot Up|
040 Ray Up Loop|041 Explosion Up MIX|042 Radial MIX|043 Explosion Up|044 Explosion Up|047 Explosion Radial MIX|
050 Trail Right|051 Trail Right|052 Trail Right|057 Hit Ray Explosion Up|059 Explosion Up MIX|060 Explosion Up MIX|
062 Explosion Up MIX|064 Hit Radial|065 Up Loop|066 Up|067 Up loop|068 Radial|070 Up|071 Right|072 Hit Radial|
073 Hit Radial|074 Wide loop Horizontal|076 Wide Horizontal Explosion|080 Right|084 Hit Radial|085 Radial loop|
086 Radial|087 Trail MIX"""


def make_one(index, entry):
    num, name = entry.split(" ", 1)
    kind, d, loop = classify(name)
    mix = "mix" in name.lower()
    wide = kind == "wide"
    W, H = (768, 432) if wide else (512, 512)
    dur = 2.0 if loop else (1.6 if kind in ("explosion", "column", "wisp") else 1.3)
    seed = 8300 + index * 53
    R = random.Random(seed)
    k = 1.0 + 0.4 * R.random()
    if mix:
        pal = R.choice(["azul", "oscuro", "gris"])
    else:
        pal = "gris" if R.random() < 0.15 else "blanco"
    shade, body = PALETTES[pal]
    sim = build(kind, d, loop, W, H, dur, seed, k)
    slug = f"{num}-{kind}" + ("" if d == "radial" else "-" + d)
    id = "ex-humo-" + slug + ("-mix" if mix else "") + ("-bucle" if loop else "")
    es = f"Humo {num} · {ES_KIND[kind]} {ES_DIR[d]}" + (" (mezcla)" if mix else "") + (" (bucle)" if loop else "")
    en = f"Smoke {num} · {EN_KIND[kind]} {d}" + (" (mix)" if mix else "") + (" (loop)" if loop else "")
    frames = int(round(dur * 30))
    s = new(id, es, en, "humo", frames, 4900 + index, ["humo", "smoke", ES_KIND[kind].lower()], loop=loop,
            size=W, height=H if wide else 0, thumb=0.5 if loop else 0.3)
    lay = Layers(s, [("sombra", shade), ("humo", body)], 40, glow=False)
    for f in range(0, frames, STEP):
        t = f / 30
        alive = sorted(sim.frame(t), key=lambda ps: -ps[1][4])
        shadow, light = [], []
        for p, st in alive:
            o = particle_outline(p, st, 1.0, f // STEP)
            shadow.append(type(o)((x + 2.0, y + 3.0) for x, y in o))
            o2 = particle_outline(p, st, 0.82, f // STEP)
            light.append(type(o2)((x - 2.5, y - 3.5) for x, y in o2))
        lay.draw(f, 0, shadow)
        lay.draw(f, 1, light)
    lay.build()
    return s


ENTRIES = [e.strip() for e in NAMES.replace("\n", "").split("|") if e.strip()]
STICKERS = [lambda i=i, e=e: make_one(i, e) for i, e in enumerate(ENTRIES)]
