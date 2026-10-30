"""Animaciones Extremas · Líquido (0.26): one element of our own for each of RTFX's 68 liquid ones, by
kind, direction, timing and palette (their names and previews only told us what each one does).

Liquid is flat and glossy, with no glow: fat drops in a dark tone with a lighter body over it and a
small white shine up and to the left, so drops of one colour that touch run together. Splashes
thrown up fall back with gravity; drops drip; ripples spread on the ground; bubbles rise; some are
red (the paint / blood splats).
"""

from __future__ import annotations

import math
import random

from rtfx_energy import ring, crescent
from rtfx_engine import STEP, Layers, Particle, Sim, blob, new, particle_outline
from rtfx_fire import emit

PALETTES = {
    "agua": ("#14707a", "#4cc9c9", "#f2ffff"),
    "azul": ("#1c4fa8", "#4aa8ff", "#f2f8ff"),
    "rojo": ("#8a0f14", "#e8343a", "#ffe9e9"),
    "verde": ("#2a7a1c", "#7ad64a", "#f4fff0"),
}
DIRS = {"up": -math.pi / 2, "down": math.pi / 2, "right": 0.0, "left": math.pi}
G = -1500.0


def splash(sim, rnd, o, a, spread, n, k, t0=0.0, speed=(300, 750), grav=G):
    emit(sim, rnd, n, t0, t0 + 0.06, o, a, spread, speed, (14 * k, 30 * k), (0.6, 1.0), lift=grav, drag=0.6,
         shape="drop", grow=0.08)
    emit(sim, rnd, 4, t0, t0 + 0.03, o, a, spread * 0.5, (40, 160), (36 * k, 50 * k), (0.3, 0.5), lift=grav * 0.3,
         drag=2.0, shape="puff", grow=0.1)


def build(kind, d, loop, W, H, dur, seed, k):
    rnd = random.Random(seed)
    sim = Sim(dur, loop=loop)
    cx, cy = W / 2, H / 2
    a = DIRS.get(d, 0.0)
    marks = []  # (t0, what, x, y)
    radial = d == "radial"
    ground = (cx, H * 0.8)
    if kind == "splash":
        o = ground if d == "up" else (cx - math.cos(a) * W * 0.2, cy - math.sin(a) * H * 0.2) if not radial else (cx, cy)
        splash(sim, rnd, o, a, math.pi if radial else rnd.uniform(0.35, 0.8), int(26 * rnd.uniform(0.7, 1.4)), k,
               speed=(300 * rnd.uniform(0.8, 1.3), 800 * rnd.uniform(0.8, 1.3)), grav=G * (0.3 if d == "right" else 1.0))
        if d == "up" and rnd.random() < 0.5:
            marks.append((0.0, "ripple", o[0], o[1] + 10))
    elif kind == "explosion":
        o = (cx, cy) if radial else ground if d == "up" else (cx, H * 0.2)
        splash(sim, rnd, o, a, math.pi if radial else 0.9, 40, k, speed=(400, 1000), grav=G * 0.6)
    elif kind == "slash":
        r = min(W, H) * 0.3
        a0 = a - math.pi / 2 - 1.1 if not radial else rnd.uniform(0, 6.28)
        sweep = 2.2 if not radial else 5.0
        marks.append((0.0, "slash", r, (a0, sweep)))
        for i in range(18):
            ang = a0 + sweep * i / 18
            b = 0.25 * i / 18
            sim.add(Particle(cx + math.cos(ang) * r, cy + math.sin(ang) * r, -math.sin(ang) * 260, math.cos(ang) * 260,
                             b + 0.1, rnd.uniform(0.4, 0.7), rnd.uniform(7 * k, 13 * k), rnd.randrange(1 << 20),
                             lift=G * 0.5, drag=1.5, shape="drop"))
    elif kind in ("ray", "shot"):
        o = ground if d == "up" else (cx - math.cos(a) * W * 0.35, cy - math.sin(a) * H * 0.35)
        n = 40 if kind == "ray" else 14
        emit(sim, rnd, n, 0, dur * (0.95 if loop else 0.35), o, a, 0.06, (700, 1000), (12 * k, 20 * k), (0.4, 0.7),
             lift=G * 0.3, drag=0.4, shape="drop")
        if kind == "shot":
            end = (o[0] + math.cos(a) * W * 0.6, o[1] + math.sin(a) * H * 0.6)
            splash(sim, rnd, end, a + math.pi, 1.0, 20, k, t0=0.4, grav=G * 0.7)
    elif kind == "down":
        x = cx + rnd.uniform(-40, 40)
        n = 6 if not loop else 8
        for i in range(n):
            b = (dur * 0.9 if loop else dur * 0.5) * i / n
            sim.add(Particle(x, H * 0.08, 0, 30, b, 0.8, rnd.uniform(12 * k, 18 * k), rnd.randrange(1 << 20),
                             lift=G * 0.7, drag=0.0, grow=0.3, shape="drop"))
        marks.append((0.55, "ripple", x, H * 0.92))
    elif kind == "cry":
        for side in (-1, 1):
            emit(sim, rnd, 30, 0, dur, (cx + side * 60, H * 0.2), math.pi / 2 + side * 0.9, 0.15, (200, 300),
                 (8 * k, 13 * k), (0.6, 0.9), lift=G * 0.6, drag=0.3, shape="drop")
    elif kind == "ripple":
        for i in range(3):
            marks.append((i * 0.25, "ripple", cx, H * 0.75))
    elif kind == "bubbles":
        emit(sim, rnd, 26, 0, dur * 0.8, lambda t: (cx + rnd.uniform(-90, 90), H * 0.85), -math.pi / 2, 0.2,
             (120, 260), (8 * k, 22 * k), (0.6, 1.1), lift=80, drag=0.8, shape="bubble", grow=0.2)
    elif kind == "trail":
        def at(t):
            u = (t / dur) % 1.0
            return W * (0.1 + 0.8 * u), cy + math.sin(u * 2 * math.pi * 1.5) * 50
        emit(sim, rnd, 70, 0, dur, at, math.pi, 0.5, (30, 120), (10 * k, 20 * k), (0.25, 0.45), lift=G * 0.2,
             drag=1.0, shape="drop")
    elif kind == "charge":
        for i in range(36):
            b = (dur if loop else dur * 0.6) * (i + rnd.random()) / 36
            ang = rnd.uniform(0, 2 * math.pi)
            r = min(W, H) * rnd.uniform(0.3, 0.42)
            life = rnd.uniform(0.35, 0.55)
            v = r / life * 1.4
            sim.add(Particle(cx + math.cos(ang) * r, cy + math.sin(ang) * r, -math.cos(ang) * v, -math.sin(ang) * v,
                             b, life, rnd.uniform(9 * k, 16 * k), rnd.randrange(1 << 20), drag=1.6, grow=0.5,
                             shape="drop"))
    elif kind == "vertical":
        sim.add(Particle(cx, H * 0.15, 0, 20, 0, dur, 26 * k, rnd.randrange(1 << 20), lift=G * 0.25, drag=0.0,
                         grow=0.4, shape="drop"))
    return sim, marks


def outlines(sim, marks, t, f, scale, W, H, k):
    out = []
    for p, st in sim.frame(t):
        if p.shape == "bubble":
            x, y, vx, vy, s, u = st
            o = ring(x, y, s * 1.0, max(1.0, s * 0.35 * scale))
        else:
            o = particle_outline(p, st, scale, f // STEP)
        if o:
            out.append(o)
    for t0, what, x, y in marks:
        u = (t - t0) / 0.6
        if u < 0 or u > 1:
            continue
        if what == "ripple":
            o = ring(x, y, 20 + 120 * (1 - (1 - u) ** 2) * k, 10 * k * (1 - u) * scale, sy=0.28)
            if o:
                out.append(o)
        elif what == "slash":
            a0, sweep = y
            r = x
            uu = min(1.0, (t - t0) / 0.3)
            o = crescent(W / 2, H / 2, r, a0 + sweep * 0.3 * uu, sweep * uu * (1 - 0.3 * uu),
                         34 * k * (1 - max(0.0, (t - t0 - 0.3) / 0.4)) * scale)
            if o:
                out.append(o)
    return out


def classify(name):
    n = name.lower()
    d = ("radial" if "radial" in n else "up" if " up" in n else "down" if "down" in n else "left" if "left" in n
         else "right" if "right" in n else "up")
    loop = "loop" in n
    for words, kind in (("crying", "cry"), ("simple vertical", "vertical"), ("charge", "charge"), ("bubbles", "bubbles"),
                        ("trail", "trail"), ("ripple", "ripple"), ("explosion", "explosion"), ("slash", "slash"),
                        ("shot", "shot"), ("ray", "ray"), ("splash", "splash"), ("hit", "explosion"), ("down", "down")):
        if words in n:
            break
    else:
        kind = "splash"
    if kind in ("cry",):
        loop = True
    return kind, d, loop


ES_KIND = {"splash": "Salpicadura", "explosion": "Estallido", "slash": "Latigazo", "ray": "Chorro", "shot": "Disparo",
           "down": "Goteo", "cry": "Llanto", "ripple": "Ondas", "bubbles": "Burbujas", "trail": "Estela",
           "charge": "Carga", "vertical": "Gota"}
EN_KIND = {"splash": "Splash", "explosion": "Burst", "slash": "Lash", "ray": "Jet", "shot": "Shot", "down": "Drip",
           "cry": "Tears", "ripple": "Ripples", "bubbles": "Bubbles", "trail": "Trail", "charge": "Charge",
           "vertical": "Drop"}
ES_DIR = {"up": "arriba", "down": "abajo", "right": "derecha", "left": "izquierda", "radial": "radial"}

NAMES = """001 Splash Up|002 Splash Right|003 Slash Right|004 Splash Up|005 Splash Up|006 Hit Ray Up|007 Splash Right|
008 Splash Up|009 Splash Right|010 Splash Up|011 Splash Up|012 Shot Splash Up|013 Splash Up|014 Splash Right|
015 Slash Right|016 Splash Hit Ray Up|017 Shot Up|018 Splash Explosion Down|020 Splash Right|021 Splash Right|
022 Shot Bubbles Up|023 Splash Trail Right Loop|024 Splash Slash Right|025 Splash Shot Hit Up|026 Slash Up|027 Down|
028 Splash Up|029 Splash Hit Explosion Radial|031 Ripple Ray Up|032 Down|033 Hit Radial|034 Hit Splash Explosion Radial|
035 Ripple Up|036 Splash Explosion Down|037 Bubbles Up|038 Slash Up|039 Splash Hit Explosion Right|040 Splash Up|
042 Hit Splash Explosion Up|047 Shot Hit Splash Right MIX|048 Splash Hit Explosion Up MIX|049 Splash Slash Right MIX|
050 Explosion Radial MIX|055 Splash Up MIX|056 Splash Up|057 Splash Up|058 Splash Right|059 Ray Right loop|
060 Splash Shot Up|062 Splash Radial|063 Splash Right|064 Splash Right|065 Splash Right|066 Splash Right|
067 Splash Right|068 Splash Hit Radial|069 Splash Right|070 Slash Radial MIX|070b Splash Radial|
071 Slash Charge Radial MIX|071b Splash Radial|072 Charge Radial Loop MIX|072b Splash Up|085 Simple Vertical|087 Down|
088 Down Loop|089 Crying Loop Down"""


def make_one(index, entry):
    num, name = entry.split(" ", 1)
    kind, d, loop = classify(name)
    mix = "mix" in name.lower()
    n = int(num.rstrip("b"))
    W, H = 512, 512
    dur = 2.0 if loop else 1.4
    seed = 5300 + index * 47
    R = random.Random(seed)
    k = 1.0 + 0.5 * R.random()
    pal = "rojo" if 62 <= n <= 71 and not mix else (R.choice(["azul", "verde", "rojo"]) if mix else "agua")
    dark, body, shine = PALETTES[pal]
    sim, marks = build(kind, d, loop, W, H, dur, seed, k)
    slug = f"{num}-{kind}" + ("" if d == "radial" else "-" + d)
    id = "ex-liquido-" + slug + ("-mix" if mix else "") + ("-bucle" if loop else "")
    label = num.rstrip("b") + (" B" if num.endswith("b") else "")
    es = f"Líquido {label} · {ES_KIND[kind]} {ES_DIR[d]}" + (" (mezcla)" if mix else "") + (" (bucle)" if loop else "")
    en = f"Liquid {label} · {EN_KIND[kind]} {d}" + (" (mix)" if mix else "") + (" (loop)" if loop else "")
    frames = int(round(dur * 30))
    s = new(id, es, en, "liquidos", frames, 4700 + index, ["líquido", "liquid", ES_KIND[kind].lower(), pal], loop=loop,
            thumb=0.5 if loop else 0.3)
    lay = Layers(s, [("oscuro", dark), ("liquido", body), ("brillo", shine)], 36, glow=False)
    for f in range(0, frames, STEP):
        t = f / 30
        lay.draw(f, 0, outlines(sim, marks, t, f, 1.0, W, H, k))
        # The body a touch smaller and up, so the dark tone shows as the shaded underside.
        body_out = []
        for o in outlines(sim, marks, t, f, 0.84, W, H, k):
            body_out.append(type(o)((x - 1.5, y - 3.0) for x, y in o))
        lay.draw(f, 1, body_out)
        # A shine on each drop, up and to the left.
        shines = []
        for p, st in sim.frame(t):
            x, y, vx, vy, sz, u = st
            if p.shape != "bubble" and sz > 5:
                shines.append(blob(x - sz * 0.35, y - sz * 0.4, sz * 0.2, p.seed, rough=0.0, n=8, stretch=(1.3, 0.8),
                                   angle=-0.6))
        lay.draw(f, 2, shines)
    lay.build()
    return s


ENTRIES = [e.strip() for e in NAMES.replace("\n", "").split("|") if e.strip()]
STICKERS = [lambda i=i, e=e: make_one(i, e) for i, e in enumerate(ENTRIES)]
