"""Animaciones Extremas · Chispas (0.26): one element of our own for each of RTFX's 77 spark ones, by
kind, direction, timing and palette (their names and previews only told us what each one does).

Sparks are small glowing dots and dashes in gold (MIX ones in cyan, violet or pink): thrown out of
a hit and falling with gravity, shot across and bursting, rising as embers, showering down, drawn
in to a charge, with a ring or a four-point star at the hit where the name says so.
"""

from __future__ import annotations

import math
import random

from rtfx_energy import ring, star
from rtfx_engine import Particle, Sim, new, render_sim
from rtfx_fire import emit

PALETTES = {
    "oro": ("#ff7a00", "#ffcf5a", "#fff7da"),
    "cian": ("#0091ff", "#8fe3ff", "#ffffff"),
    "violeta": ("#7a2cff", "#cfa6ff", "#ffffff"),
    "rosa": ("#ff2f7a", "#ffb0cc", "#ffffff"),
}
DIRS = {"up": -math.pi / 2, "down": math.pi / 2, "right": 0.0, "left": math.pi}
G = -1100.0  # gravity as `lift` (negative falls)


def burst(sim, rnd, o, a, spread, n, k, t0=0.0, speed=(300, 900), grav=G):
    emit(sim, rnd, n, t0, t0 + 0.05, o, a, spread, speed, (4 * k, 7 * k), (0.5, 1.0), lift=grav, drag=1.8,
         shape="spark", grow=0.05)
    emit(sim, rnd, n // 2, t0, t0 + 0.08, o, a, spread, (speed[0] * 0.4, speed[1] * 0.6), (5 * k, 9 * k),
         (0.5, 1.1), lift=grav * 0.6, drag=2.2, shape="dot", grow=0.05)


def build(kind, d, loop, W, H, dur, seed, k):
    rnd = random.Random(seed)
    sim = Sim(dur, loop=loop)
    cx, cy = W / 2, H / 2
    a = DIRS.get(d, 0.0)
    marks = []  # (t0, kind, x, y): a ring or a star drawn at a hit
    radial = d == "radial"
    if kind in ("hit", "explosion"):
        o = (cx, cy) if radial else (cx - math.cos(a) * W * 0.15, cy - math.sin(a) * H * 0.15)
        # Each burst its own: how many, how fast, how heavy, and a second wave or not.
        n = int((50 if kind == "explosion" else 34) * rnd.uniform(0.6, 1.5))
        fast = rnd.uniform(0.6, 1.4)
        heavy = rnd.uniform(0.15, 1.4)
        burst(sim, rnd, o, a, math.pi if radial else rnd.uniform(0.4, 0.9), n, k,
              speed=(400 * fast, 1100 * fast) if kind == "explosion" else (300 * fast, 800 * fast), grav=G * heavy)
        if rnd.random() < 0.4:
            burst(sim, rnd, o, a, math.pi if radial else 0.8, n // 2, k * 0.8, t0=rnd.uniform(0.12, 0.3),
                  speed=(200, 600), grav=G * heavy)
        if rnd.random() < 0.5:
            marks.append((0.0, "ring", o[0], o[1]))
    elif kind == "star":
        burst(sim, rnd, (cx, cy), 0, math.pi, 40, k)
        marks.append((0.0, "star", cx, cy))
    elif kind in ("shot", "shothit"):
        start = (cx - math.cos(a) * W * 0.4, cy - math.sin(a) * H * 0.4) if not radial else (cx, cy)
        end = (cx + math.cos(a) * W * 0.25, cy + math.sin(a) * H * 0.25) if not radial else (cx, cy)
        fly = 0.35
        def at(t):
            u = min(1.0, t / fly)
            return start[0] + (end[0] - start[0]) * u, start[1] + (end[1] - start[1]) * u
        if loop:
            emit(sim, rnd, 60, 0, dur, lambda t: (cx + math.cos(a) * W * 0.15, cy + math.sin(a) * H * 0.15),
                 a + math.pi, 0.25, (300, 700), (4 * k, 7 * k), (0.2, 0.4), drag=1.5, shape="spark")
            emit(sim, rnd, 20, 0, dur, (cx + math.cos(a) * W * 0.17, cy + math.sin(a) * H * 0.17), a, math.pi,
                 (5, 40), (12 * k, 16 * k), (0.08, 0.14), shape="dot", grow=0.1)
        else:
            emit(sim, rnd, 30, 0, fly, at, a + math.pi, 0.3, (100, 300), (4 * k, 6 * k), (0.2, 0.35), shape="spark")
            emit(sim, rnd, 10, 0, fly, at, a, 0.4, (5, 20), (11 * k, 14 * k), (0.05, 0.08), shape="dot", grow=0.1)
            if kind == "shothit":
                burst(sim, rnd, end, a + math.pi, 1.4, 34, k, t0=fly)
                marks.append((fly, "ring" if rnd.random() < 0.6 else "star", end[0], end[1]))
    elif kind == "ray":
        o = (cx - math.cos(a) * W * 0.4, cy - math.sin(a) * H * 0.4) if d != "horizontal" else (cx, cy)
        angles = [a] if d != "horizontal" else [0.0, math.pi]
        for ang in angles:
            emit(sim, rnd, 70 // len(angles), 0, dur * (0.95 if loop else 0.5), o, ang, 0.08, (600, 1000),
                 (4 * k, 7 * k), (0.3, 0.6), drag=0.6, shape="spark")
    elif kind == "down":
        emit(sim, rnd, 60, 0, dur * 0.9, lambda t: (rnd.uniform(W * 0.25, W * 0.75), H * 0.05), math.pi / 2, 0.2,
             (100, 300), (4 * k, 7 * k), (0.6, 1.0), lift=G * 0.6, drag=0.5, shape="spark")
    elif kind in ("rise", "projectile"):
        x0 = cx
        emit(sim, rnd, 70, 0, dur, (x0, H * 0.85) if kind == "rise" else (cx, cy), -math.pi / 2 if d != "left" else math.pi,
             0.35, (150, 400), (4 * k, 8 * k), (0.5, 0.9), lift=120, drag=0.8, shape="dot")
    elif kind == "wide":
        emit(sim, rnd, 90, 0, dur, lambda t: (rnd.uniform(0, W), H * 0.95), -math.pi / 2, 0.3, (100, 260),
             (3 * k, 6 * k), (0.8, 1.4), lift=80, drag=0.4, shape="dot")
    elif kind == "slash":
        for i in range(36):
            ang = 2 * math.pi * i / 36
            r = min(W, H) * 0.3
            b = 0.3 * i / 36
            sim.add(Particle(cx + math.cos(ang) * r, cy + math.sin(ang) * r, -math.sin(ang) * 200, math.cos(ang) * 200,
                             b, rnd.uniform(0.35, 0.6), rnd.uniform(4 * k, 7 * k), rnd.randrange(1 << 20), drag=2.0,
                             shape="spark", grow=0.05))
    elif kind == "charge":
        for i in range(60):
            b = (dur if loop else dur * 0.6) * (i + rnd.random()) / 60
            ang = rnd.uniform(0, 2 * math.pi)
            r = min(W, H) * rnd.uniform(0.3, 0.45)
            life = rnd.uniform(0.3, 0.5)
            v = r / life * 1.4
            sim.add(Particle(cx + math.cos(ang) * r, cy + math.sin(ang) * r, -math.cos(ang) * v, -math.sin(ang) * v,
                             b, life, rnd.uniform(4 * k, 7 * k), rnd.randrange(1 << 20), drag=1.6, grow=0.5,
                             shape="spark"))
        if not loop:
            burst(sim, rnd, (cx, cy), -math.pi / 2, math.pi if radial else 0.5, 40, k, t0=dur * 0.62)
            marks.append((dur * 0.62, "star", cx, cy))
    elif kind == "fireworks":
        top = (cx, H * 0.3)
        emit(sim, rnd, 20, 0, 0.45, lambda t: (cx, H * 0.95 - (H * 0.65) * min(1, t / 0.45)), math.pi / 2, 0.2,
             (40, 120), (3 * k, 5 * k), (0.2, 0.4), shape="spark")
        burst(sim, rnd, top, 0, math.pi, 60, k, t0=0.45, speed=(300, 700), grav=G * 0.4)
        marks.append((0.45, "star", top[0], top[1]))
    return sim, marks


def classify(name):
    n = name.lower()
    d = ("radial" if "radial" in n else "up" if "up" in n else "down" if "down" in n else "left" if "left" in n
         else "horizontal" if "horizontal" in n else "right" if "right" in n else "radial")
    loop = "loop" in n
    for words, kind in (("fireworks", "fireworks"), ("particles wide", "wide"), ("charge", "charge"),
                        ("star", "star"), ("slash", "slash"), ("projectile", "projectile"), ("shot ray hit", "shothit"),
                        ("shot hit", "shothit"), ("hit explosion shot", "shothit"), ("shot", "shot"), ("ray", "ray"),
                        ("explosion", "explosion"), ("hit", "hit"), ("down", "down"), ("loop up", "rise")):
        if words in n:
            break
    else:
        kind = "rise"
    return kind, d, loop


ES_KIND = {"hit": "Impacto", "explosion": "Estallido", "star": "Estrella", "shot": "Disparo", "shothit": "Disparo e impacto",
           "ray": "Chorro", "down": "Lluvia", "rise": "Ascenso", "projectile": "Proyectil", "wide": "Brasas",
           "slash": "Anillo", "charge": "Carga", "fireworks": "Fuegos artificiales"}
EN_KIND = {"hit": "Hit", "explosion": "Burst", "star": "Star", "shot": "Shot", "shothit": "Shot and hit", "ray": "Stream",
           "down": "Shower", "rise": "Rise", "projectile": "Projectile", "wide": "Embers", "slash": "Ring",
           "charge": "Charge", "fireworks": "Fireworks"}
ES_DIR = {"up": "arriba", "down": "abajo", "right": "derecha", "left": "izquierda", "radial": "radial",
          "horizontal": "horizontal"}

NAMES = """002 Hit Explosion Radial|003 Shot Hit Right|004 Shot Hit Explosion up|005 Shot Ray Hit Explosion Up|
006 Shot Hit Up|007 Down|008 Projectile Up loop|009 Shot Hit Explosion Down|010 Shot Right|011 Explosion Up|
012 Explosion right|013 Hit Explosion Radial|015 Hit Explosion Radial|016 Hit Explosion Radial|019 Shot Hit Right|
020 Shot Hit Explosion Right|021 Shot Hit Explosion Right|022 Shot Ray Hit Explosion Right|023 Slash Radial|
024 Shot Hit Explosion Right|025 Hit Explosion Radial|026 loop Up|027 Hit Explosion Radial|028 Shot Hit Explosion Up|
029 Shot Hit Explosion Up|030 Hit Explosion Radial|031 Hit Explosion Radial|032 Hit Star Explosion Radial|
033 Hit Explosion Shot Up|034 Hit Ray Up|035 Hit Ray Up|036 Hit Explosion Radial|037 Shot Right Loop|
039 Shot Right Loop|052 Shot Right loop|053 Shot Ray Right|055 Shot Right|059 Shot Right loop|060 Shot up loop|
061 Ray up loop|062 Ray Up Loop|063 Ray Up|067 Down|068 Shot Ray Hit Explosion Right|069 Hit Star Explosion Radial|
070 Shot Ray Hit Explosion Up|071 Hit Explosion Radial|072 Shot Ray Hit Explosion Right|073 Hit Explosion Radial|
074 Shot Ray Hit Up|075 Hit Explosion Radial|076 Hit Explosion Radial|077 Charge Hit Up|078 Ray Left|
079 Shot Hit Explosion Radial|080 Charge Radial|081 Shot Right Loop|082 Shot Right Loop|083 Projectile Left Loop|
084 Charge Radial|086 Hit Up MIX|087 Hit Explosion Radial MIX|088 Fireworks Ray Up MIX|089 Explosion Radial MIX|
090 Explosion Radial MIX|091 Ray Horizontal|093 Explosion Radial MIX|096 Explosion Up MIX|097 Explosion Hit Radial MIX|
098 Hit Explosion Radial MIX|099 Shot Ray Hit Radial MIX|100 Shot Radial Loop|101 Hit Radial|102 Hit Star Radial|
103 Shot Horizontal|104 Hit Radial|105 Up Particles Wide"""


def make_one(index, entry):
    num, name = entry.split(" ", 1)
    kind, d, loop = classify(name)
    if kind == "wide":
        loop, d = True, "up"
    mix = "mix" in name.lower()
    wide = kind == "wide"
    W, H = (768, 432) if wide else (512, 512)
    dur = 2.0 if loop else (1.8 if kind in ("fireworks", "charge", "shothit") else 1.4)
    seed = 6100 + index * 43
    R = random.Random(seed)
    k = 1.0 + 0.5 * R.random()
    pal = "oro" if not mix else R.choice(["cian", "violeta", "rosa", "oro"])
    rim, body, core = PALETTES[pal]
    sim, marks = build(kind, d, loop, W, H, dur, seed, k)

    def extra(f, t):
        out = {0: [], 1: [], 2: []}
        for t0, what, x, y in marks:
            u = (t - t0) / 0.45
            if u < 0 or u > 1:
                continue
            for tone, wf in enumerate((1.0, 0.55, 0.22)):
                if what == "ring":
                    o = ring(x, y, 20 + 110 * (1 - (1 - u) ** 3) * k, 9 * k * (1 - u) * wf)
                else:
                    o = star(x, y, 90 * k * math.sin(math.pi * min(1, u * 1.4)) * (0.6 + 0.4 * wf), 5 * wf * k,
                             0.2 + u * 0.5)
                if o:
                    out[tone].append(o)
        return out

    slug = f"{num}-{kind}" + ("" if d == "radial" else "-" + d)
    id = "ex-chispas-" + slug + ("-mix" if mix else "") + ("-bucle" if loop else "")
    es = f"Chispas {num} · {ES_KIND[kind]} {ES_DIR[d]}" + (" (mezcla)" if mix else "") + (" (bucle)" if loop else "")
    en = f"Sparks {num} · {EN_KIND[kind]} {d}" + (" (mix)" if mix else "") + (" (loop)" if loop else "")
    frames = int(round(dur * 30))
    s = new(id, es, en, "chispas", frames, 4500 + index, ["chispas", "sparks", ES_KIND[kind].lower()], loop=loop,
            size=W, height=H if wide else 0, thumb=0.5 if loop else 0.3)
    render_sim(s, sim, [("borde", rim), ("cuerpo", body), ("nucleo", core)], scales=(1.0, 0.62, 0.3), slots=40,
               glow_blur=16, extra=extra)
    return s


ENTRIES = [e.strip() for e in NAMES.replace("\n", "").split("|") if e.strip()]
STICKERS = [lambda i=i, e=e: make_one(i, e) for i, e in enumerate(ENTRIES)]
