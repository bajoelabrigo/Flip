"""Animaciones Extremas · Fuego (0.26): one element of our own for each of RTFX's fire elements, by the
same family, motion, direction, timing and palette (Jorge: «repliques todas las de RTFX»; nothing of
theirs is used — their names only told us what each one does).

Every element is a particle system from rtfx_engine drawn in three cel tones (red rim, orange body,
yellow core) on twos, with a soft glow. The kinds:
  ray        a jet of flame shooting one way and dying out
  trail      a fireball crossing, leaving flame behind
  radial     a ring of flame swirling round
  projectile a fireball in place with flame streaming back (loops)
  hit        a burst out of one point, one way (or all ways)
  torch      a rising fireball column (loops when named so)
  slash      a crescent of fire swept across
  explosion  a big round burst of blobs
  splash     flame thrown up that falls back
  wide       a row of flames along the bottom (loops)
  thrower    a flamethrower cone
  charge     flame drawn in to the centre (loops when named so)
  stroke     a brush stroke of fire
  candle     a calm or windy torch flame (loops)
  wings      two flame wings opening
  shot       a muzzle burst and the shot leaving
"MIX" ones get bright white-blue sparks on top; "Simple" ones are two tones with no glow.
"""

from __future__ import annotations

import math
import random

from rtfx_engine import Particle, Sim, new, render_sim

RED, ORANGE, YELLOW = "#d4220a", "#ff7a12", "#ffe27a"
WHITE_BLUE = "#d8f0ff"
DIRS = {"up": -math.pi / 2, "down": math.pi / 2, "right": 0.0, "left": math.pi, "diag": -math.pi / 4}


def emit(sim, rnd, n, t0, t1, origin, angle, spread, speed, size, life, lift=0.0, drag=1.5, shape="flame",
         grow=0.25, spin=0.0):
    """n particles born evenly over [t0, t1] (jittered); `origin` is (x, y) or a function of t."""
    for k in range(n):
        b = t0 + (t1 - t0) * (k + rnd.random()) / max(1, n)
        ox, oy = origin(b) if callable(origin) else origin
        a = (angle(b) if callable(angle) else angle) + rnd.uniform(-spread, spread)
        v = rnd.uniform(*speed)
        sim.add(Particle(ox + rnd.uniform(-4, 4), oy + rnd.uniform(-4, 4), math.cos(a) * v, math.sin(a) * v, b,
                         rnd.uniform(*life), rnd.uniform(*size), rnd.randrange(1 << 20), lift=lift, drag=drag,
                         grow=grow, spin=spin, shape=shape))


def build_sim(kind, direction, loop, W, H, dur, seed, k=1.0):
    """The particles for one element. `k` scales sizes (bigger or smaller variants)."""
    rnd = random.Random(seed)
    sim = Sim(dur, loop=loop)
    cx, cy = W / 2, H / 2
    a = DIRS.get(direction, 0.0)
    radial = direction == "radial"
    both = direction == "horizontal"
    # Where a one-way effect starts: the opposite side, so it travels across.
    back = (cx - math.cos(a) * W * 0.32, cy - math.sin(a) * H * 0.32)
    span = dur * (0.92 if loop else 0.5)

    if kind == "ray":
        emit(sim, rnd, 70, 0, span, back, a, 0.2, (500, 900), (14 * k, 26 * k), (0.35, 0.6), drag=0.8)
    elif kind == "trail":
        def at(t):
            u = t / max(1e-3, span)
            if radial:
                r = W * 0.28
                return cx + math.cos(u * 2 * math.pi) * r, cy + math.sin(u * 2 * math.pi) * r
            return (back[0] + math.cos(a) * W * 0.64 * u, back[1] + math.sin(a) * H * 0.64 * u
                    + math.sin(u * 7 + seed) * 18)
        emit(sim, rnd, 70, 0, span, at, a + math.pi, 0.5, (40, 160), (12 * k, 28 * k), (0.3, 0.6), lift=120)
        emit(sim, rnd, 14, 0, span, at, a, 0.3, (10, 40), (26 * k, 36 * k), (0.12, 0.2), grow=0.1)
    elif kind == "radial":
        def ring(t):
            u = t / dur
            ang = u * 2 * math.pi * 1.5
            r = W * (0.12 + 0.18 * u)
            return cx + math.cos(ang) * r, cy + math.sin(ang) * r
        emit(sim, rnd, 70, 0, span, ring, lambda t: t / dur * 3 * math.pi + math.pi / 2, 0.3, (60, 200),
             (12 * k, 24 * k), (0.3, 0.55), lift=60)
    elif kind == "projectile":
        emit(sim, rnd, 80, 0, dur, (cx + math.cos(a) * W * 0.12, cy + math.sin(a) * H * 0.12), a + math.pi, 0.35,
             (250, 520), (14 * k, 30 * k), (0.25, 0.45), drag=1.0)
        emit(sim, rnd, 20, 0, dur, (cx + math.cos(a) * W * 0.14, cy + math.sin(a) * H * 0.14), a, 0.6, (5, 30),
             (34 * k, 44 * k), (0.1, 0.16), grow=0.1, shape="puff")
    elif kind == "hit":
        spread = math.pi if radial else (0.6 if not both else 0.45)
        angles = [a] if not both else [0.0, math.pi]
        o = (cx, cy) if radial or both else (cx - math.cos(a) * W * 0.12, cy - math.sin(a) * H * 0.12)
        for ang in angles:
            emit(sim, rnd, 40 // len(angles), 0, 0.18, o, ang, spread, (300, 900), (16 * k, 34 * k), (0.35, 0.7),
                 lift=150, drag=3.0)
        emit(sim, rnd, 6, 0, 0.06, o, a, math.pi, (10, 60), (40 * k, 60 * k), (0.2, 0.35), grow=0.1, shape="puff")
        emit(sim, rnd, 18, 0, 0.12, o, a, spread, (500, 1100), (5 * k, 8 * k), (0.3, 0.6), shape="spark", drag=2.0)
    elif kind == "torch":
        base = (cx - math.cos(a) * H * 0.3, cy - math.sin(a) * H * 0.3) if direction in ("left", "right") else (cx, H * 0.82)
        ang = a if direction in ("left", "right") else -math.pi / 2
        emit(sim, rnd, 90, 0, span, base, ang, 0.45, (180, 420), (16 * k, 36 * k), (0.45, 0.8), lift=160, drag=1.2)
    elif kind == "slash":
        def arc(t):
            u = min(1.0, t / 0.3)
            sweep = -1.4 + 2.8 * u
            r = W * 0.3
            base = a if not radial else u * 2 * math.pi
            ang = base + sweep if not radial else base
            return cx + math.cos(ang) * r - math.cos(a) * r * 0.5, cy + math.sin(ang) * r - math.sin(a) * r * 0.5
        emit(sim, rnd, 60, 0, 0.3, arc, a, 0.6, (20, 120), (12 * k, 26 * k), (0.3, 0.55), lift=80)
    elif kind == "explosion":
        o = (cx, cy) if radial else (cx - math.cos(a) * W * 0.1, cy - math.sin(a) * H * 0.1)
        spread = math.pi if radial else 0.7
        emit(sim, rnd, 30, 0, 0.1, o, a, spread, (150, 520), (34 * k, 60 * k), (0.5, 0.9), lift=90, drag=3.5,
             shape="puff", grow=0.15)
        emit(sim, rnd, 30, 0.02, 0.2, o, a, spread, (400, 1000), (12 * k, 22 * k), (0.4, 0.7), lift=200, drag=2.5)
        emit(sim, rnd, 16, 0, 0.1, o, a, spread, (600, 1200), (5 * k, 8 * k), (0.4, 0.8), shape="spark", drag=1.5)
    elif kind == "splash":
        emit(sim, rnd, 50, 0, 0.25, (cx, H * 0.72), -math.pi / 2, 0.55, (450, 850), (12 * k, 24 * k), (0.6, 1.0),
             lift=-900, drag=0.6, shape="drop")
        emit(sim, rnd, 10, 0, 0.1, (cx, H * 0.72), -math.pi / 2, 1.2, (60, 200), (30 * k, 44 * k), (0.25, 0.4),
             shape="puff")
    elif kind == "wide":
        for i in range(7):
            x = W * (0.08 + 0.84 * i / 6)
            emit(sim, rnd, 14, 0, dur, (x, H * 0.92), -math.pi / 2, 0.3, (160, 380), (30 * k, 52 * k),
                 (0.4, 0.75), lift=180)
    elif kind == "thrower":
        o = (cx - math.cos(a) * W * 0.4, cy - math.sin(a) * H * 0.4)
        emit(sim, rnd, 90, 0, span, o, a, 0.18, (700, 1100), (10 * k, 34 * k), (0.4, 0.7), lift=140, drag=1.6,
             grow=0.6)
    elif kind == "charge":
        for i in range(70):
            b = (dur if loop else dur * 0.6) * (i + rnd.random()) / 70
            ang = rnd.uniform(0, 2 * math.pi)
            r = W * rnd.uniform(0.32, 0.45)
            life = rnd.uniform(0.35, 0.55)
            v = r / life * 1.4
            sim.add(Particle(cx + math.cos(ang) * r, cy + math.sin(ang) * r, -math.cos(ang) * v, -math.sin(ang) * v,
                             b, life, rnd.uniform(10 * k, 20 * k), rnd.randrange(1 << 20), drag=1.6, grow=0.7))
        emit(sim, rnd, 24, 0, dur, (cx, cy), 0, math.pi, (5, 30), (28 * k, 42 * k), (0.15, 0.25), shape="puff",
             grow=0.2)
    elif kind == "stroke":
        def path(t):
            u = min(1.0, t / 0.35)
            x = back[0] + math.cos(a) * W * 0.64 * u - math.sin(a) * math.sin(u * math.pi) * W * 0.12
            y = back[1] + math.sin(a) * H * 0.64 * u + math.cos(a) * math.sin(u * math.pi) * H * 0.12
            return x, y
        emit(sim, rnd, 70, 0, 0.35, path, a + math.pi / 2, 0.4, (20, 80), (14 * k, 30 * k), (0.4, 0.75), lift=90)
    elif kind == "candle":
        windy = direction == "windy"
        base = (cx, H * 0.85)
        for i in range(70):
            b = dur * (i + rnd.random()) / 70
            v = rnd.uniform(140, 260)
            sway = math.sin(b * 2 * math.pi * (3 if windy else 1)) * (0.5 if windy else 0.12)
            ang = -math.pi / 2 + sway + (0.35 if windy else 0) + rnd.uniform(-0.1, 0.1)
            sim.add(Particle(base[0] + rnd.uniform(-10, 10), base[1], math.cos(ang) * v, math.sin(ang) * v, b,
                             rnd.uniform(0.5, 0.8), rnd.uniform(22 * k, 34 * k), rnd.randrange(1 << 20),
                             lift=120, drag=1.0, grow=0.2))
    elif kind == "wings":
        for side in (-1, 1):
            def wing(t, side=side):
                u = min(1.0, t / 0.4)
                ang = -math.pi / 2 - side * (0.3 + 1.2 * u) if direction == "up" else side * u * math.pi
                r = W * 0.32
                return cx + math.cos(ang) * r * 0.9, cy + 30 + math.sin(ang) * r
            emit(sim, rnd, 40, 0, 0.4, wing, -math.pi / 2, 0.5, (40, 160), (12 * k, 26 * k), (0.35, 0.7), lift=140)
    elif kind == "shot":
        o = (cx - math.cos(a) * W * 0.3, cy - math.sin(a) * H * 0.3)
        emit(sim, rnd, 20, 0, 0.06, o, a, 0.7, (200, 600), (18 * k, 32 * k), (0.2, 0.35), drag=4.0)
        emit(sim, rnd, 30, 0.04, 0.3, lambda t: (o[0] + math.cos(a) * 1400 * (t - 0.04), o[1] + math.sin(a) * 1400 * (t - 0.04)),
             a + math.pi, 0.3, (50, 150), (12 * k, 24 * k), (0.18, 0.3))
    return sim


def mix_sparks(sim, W, H, seed, dur):
    rnd = random.Random(seed + 7)
    emit(sim, rnd, 26, 0, dur * 0.7, (W / 2, H / 2), 0, math.pi, (400, 1000), (4, 7), (0.25, 0.5), shape="spark",
         drag=1.5)


# (number, RTFX kind words → our kind, direction, loop, wide canvas)
def classify(name):
    n = name.lower()
    direction = ("radial" if "radial" in n else "up" if " up" in n else "down" if "down" in n else
                 "left" if "left" in n else "horizontal" if "horizontal" in n else "right" if "right" in n else
                 "diag" if "diagonal" in n else "radial")
    loop = "loop" in n
    for words, kind in (("flamethrower", "thrower"), ("charge", "charge"), ("wings", "wings"), ("torch calm", "candle"),
                        ("torch windy", "candle"), ("torch", "torch"), ("fireball", "torch"), ("slash", "slash"),
                        ("explosion", "explosion"), ("exposion", "explosion"), ("splash", "splash"),
                        ("projectile", "projectile"), ("shot", "shot"), ("ray", "ray"), ("trail", "trail"),
                        ("hit", "hit"), ("stroke", "stroke"), ("wide", "wide")):
        if words in n:
            kind = kind
            break
    else:
        kind = "torch" if direction == "up" else "radial" if direction == "radial" else "trail"
    if kind == "candle":
        direction = "windy" if "windy" in n else "calm"
        loop = loop or True
    if kind == "wide":
        loop = True
        direction = "up"
    return kind, direction, loop


ES_KIND = {"ray": "Rayo", "trail": "Estela", "radial": "Remolino", "projectile": "Proyectil", "hit": "Golpe",
           "torch": "Antorcha", "slash": "Corte", "explosion": "Explosión", "splash": "Salpicadura", "wide": "Hilera",
           "thrower": "Lanzallamas", "charge": "Carga", "stroke": "Trazo", "candle": "Llama", "wings": "Alas",
           "shot": "Disparo"}
EN_KIND = {"ray": "Ray", "trail": "Trail", "radial": "Swirl", "projectile": "Projectile", "hit": "Hit",
           "torch": "Torch", "slash": "Slash", "explosion": "Explosion", "splash": "Splash", "wide": "Row",
           "thrower": "Flamethrower", "charge": "Charge", "stroke": "Stroke", "candle": "Flame", "wings": "Wings",
           "shot": "Shot"}
ES_DIR = {"up": "arriba", "down": "abajo", "right": "derecha", "left": "izquierda", "radial": "radial",
          "horizontal": "horizontal", "diag": "diagonal", "calm": "en calma", "windy": "con viento"}
EN_DIR = {"up": "up", "down": "down", "right": "right", "left": "left", "radial": "radial",
          "horizontal": "horizontal", "diag": "diagonal", "calm": "calm", "windy": "windy"}

# Our numbering follows the family list (the same order, so Jorge finds each counterpart).
NAMES = """001 Ray Up|002 Trail Right|003 Radial|004 Projectile Right Loop|005 Hit Up|006 Hit Right|007 Torch Fireball Up|
008 Up Projectile Loop|009 Hit Horizontal|010 Hit Trail Up|011 Slash Right|012 Slash Right|013 Torch Fireball Up|
014 Hit Explosion Right|015 Hit Radial|016 Hit Up|017 Trail Right|018 Torch Fireball Up Loop|019 Trail Radial|
020 Ray Right|021 Trail Right|022 Up Loop|023 Hit Shot Right|024 Hit Shot Up|025 Ray Up|026 Hit Up|027 Slash Up|
028 Ray Shot Up|029 Ray Shot Right|030 Hit Explosion Up|031 Ray Shot Right|032 Slash Radial|033 Hit Explosion Radial|
035 Hit Explosion Radial|036 Projectile Down|037 Explosion Radial|038 Ray Trail Right|039 Radial|040 Shot Hit Up|
041 Fireball Torch Right|042 Splash Up|047 Up Wide loop|048 Up Wide loop|050 Explosion Radial|
053 Fireball Torch Right Loop|055 Hit Shot Up|056 Fireball Radial|058 Radial MIX|059 Flamethrower Right MIX|
060 Flamethrower Right MIX|061 Projectile Right Loop MIX|062 Slash Down MIX|063 Explosion Radial MIX|064 Hit Up|
065 Flamethrower Right MIX|067 Right Projectile Loop|068 Right MIX|070 Flamethrower Right MIX|071 Ray Shot Up MIX|
072 Hit Left MIX|073 Explosion Right MIX|074 Ray Up MIX|075 Hit Right MIX|076 Shot MIX|079 Wide MIX loop|
081 Ray Right MIX|083 Ray Up MIX|084 Torch Fireball Up MIX|085 Torch Fireball Left MIX|086 Hit Radial MIX|
087 Torch Fireball Left MIX|089 Hit Radial MIX|090 Explosion Hit Radial MIX|091 Torch Fireball Right MIX|
092 Charge Radial Loop MIX|093 Charge Radial MIX|094 Charge Radial Loop MIX|100 Up MIX Wide|102 Right|103 Left|
104 Right|105 Up|106 Left|107 Stroke Up|108 Stroke Right|110 Wide Up loop|112 Torch Calm End|112 Torch Calm loop|
112 Torch Windy End|113 Torch Windy loop|114 Torch Windy loop|115 Torch Windy loop|116 Wings Up|117 Hit Exposion|
118 Trail MIX|119 Wings Radial MIX|S003 Radial|S007 Torch Fireball Up|S011 Slash Right|S012 Slash Right|
S013 Torch Fireball Up|S014 Hit Right|S015 Hit Radial|S019 Trail Radial|S020 Ray Right|S024 Hit Shot Up|S025 Ray Up|
S027 Slash Up|S030 Hit Up|S032 Slash Radial|S033 Hit Radial|S041 Fireball Torch Right|S058 Radial|S060 Right"""


def make_one(index, entry):
    num, name = entry.split(" ", 1)
    simple = num.startswith("S")
    mix = "mix" in name.lower()
    kind, direction, loop = classify(name)
    if "end" in name.lower():
        loop = False
    wide = kind == "wide" or "wide" in name.lower()
    W, H = (768, 432) if wide else (512, 512)
    dur = 2.0 if loop else (1.6 if kind in ("explosion", "splash", "charge") else 1.3)
    seed = 9100 + index * 37
    k = 1.2 + 0.45 * random.Random(seed).random()
    sim = build_sim(kind, direction, loop, W, H, dur, seed, k)
    if mix:
        mix_sparks(sim, W, H, seed, dur)
    slug = num.lower() + "-" + kind + ("-" + direction if direction not in ("radial",) or kind != "radial" else "")
    id = ("ex-fuego-simple-" if simple else "ex-fuego-") + slug.replace("s0", "0", 1) + ("-mix" if mix else "") + (
        "-bucle" if loop else "")
    label = num.lstrip("S")
    es = ("Fuego simple " if simple else "Fuego ") + f"{label} · {ES_KIND[kind]} {ES_DIR[direction]}" + (
        " (mezcla)" if mix else "") + (" (bucle)" if loop else "")
    en = ("Simple fire " if simple else "Fire ") + f"{label} · {EN_KIND[kind]} {EN_DIR[direction]}" + (
        " (mix)" if mix else "") + (" (loop)" if loop else "")
    frames = int(round(dur * 30))
    s = new(id, es, en, "fuego", frames, 4000 + index, ["fuego", "fire", ES_KIND[kind].lower()], loop=loop,
            size=W, height=H if wide else 0, thumb=0.5 if loop else 0.28)
    if simple:
        render_sim(s, sim, [("rim", RED), ("body", ORANGE)], scales=(1.0, 0.6), glow=False, slots=28)
    else:
        render_sim(s, sim, [("rim", RED), ("body", ORANGE), ("core", YELLOW)], slots=28)
    if mix:
        # The sparks' second pass in white-blue over the top.
        spark_sim = Sim(dur, loop=loop)
        mix_sparks(spark_sim, W, H, seed + 1, dur)
        render_sim(s, spark_sim, [("chispa", WHITE_BLUE)], scales=(1.0,), slots=26, glow_blur=12)
    return s


ENTRIES = [e.strip() for e in NAMES.replace("\n", "").split("|") if e.strip()]
STICKERS = [lambda i=i, e=e: make_one(i, e) for i, e in enumerate(ENTRIES)]
