"""Animaciones Extremas · Energía (0.26): one element of our own for each of RTFX's 89 energy ones, by
kind, direction, timing and palette (their names and previews only told us what each one does).

Energy is drawn as thin glowing line work, not particles: rings that burst out, four-point stars,
crescents swept like a blade, beams that shoot and thin away, orbs with streaks, rays, auras. Each
piece is a closed outline drawn three times — a coloured rim, a light body and a white core, each
thinner than the last — on twos, with a glow behind (rtfx_engine.Layers).
"""

from __future__ import annotations

import math
import random

from rtfx_engine import STEP, Layers, Particle, Sharp, Sim, new, particle_outline

PALETTES = {
    "azul": ("#2f6bff", "#8fd8ff", "#ffffff"),
    "cian": ("#00b4d8", "#9ff6ff", "#ffffff"),
    "violeta": ("#7a2cff", "#d4a8ff", "#ffffff"),
    "oro": ("#ff9a00", "#ffe27a", "#ffffff"),
    "rosa": ("#ff2fa8", "#ffb0e2", "#ffffff"),
}
WIDTHS = (1.0, 0.55, 0.22)  # rim, body, core: thickness of each tone


def ease_out(u):
    u = max(0.0, min(1.0, u))
    return 1 - (1 - u) ** 3


def bump(u):
    """0 → 1 → 0 over u in 0..1, quick in, slow out."""
    u = max(0.0, min(1.0, u))
    return min(1.0, u / 0.15) * (1 - u) ** 0.8


# ------------------------------------------------------------------ outlines
def ring(cx, cy, r, w, n=28, sx=1.0, sy=1.0, rot=0.0, sides=0):
    """An annulus as one keyhole outline (outer round, inner back): a ring with a hole. `sides` > 0
    makes it a polygon frame."""
    if w <= 0.3 or r <= 0.5:
        return None
    outer, inner = [], []
    m = sides if sides else n
    for i in range(m + 1):
        a = rot + 2 * math.pi * i / m
        for rr, out in ((r + w / 2, outer), (max(0.1, r - w / 2), inner)):
            out.append((cx + math.cos(a) * rr * sx, cy + math.sin(a) * rr * sy))
    pts = outer + inner[::-1]
    return Sharp(pts) if sides else pts


def spindle(x0, y0, x1, y1, w, bulge=0.5):
    """A pointed streak from (x0, y0) to (x1, y1), widest at `bulge` along it."""
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 1 or w < 0.3:
        return None
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    pts = []
    n = 6
    for i in range(n + 1):
        u = i / n
        prof = (u / bulge) ** 0.7 if u < bulge else ((1 - u) / (1 - bulge)) ** 0.7
        pts.append((x0 + ux * L * u + nx * w / 2 * prof, y0 + uy * L * u + ny * w / 2 * prof))
    for i in range(n - 1, 0, -1):
        u = i / n
        prof = (u / bulge) ** 0.7 if u < bulge else ((1 - u) / (1 - bulge)) ** 0.7
        pts.append((x0 + ux * L * u - nx * w / 2 * prof, y0 + uy * L * u - ny * w / 2 * prof))
    return pts


def crescent(cx, cy, r, a0, sweep, w, sy=1.0):
    """A blade: the arc from a0 over `sweep` radians, `w` thick in the middle and pointed at both ends."""
    if w < 0.3 or abs(sweep) < 0.02:
        return None
    n = 10
    outer, inner = [], []
    for i in range(n + 1):
        u = i / n
        a = a0 + sweep * u
        t = w * math.sin(math.pi * u) ** 0.8
        outer.append((cx + math.cos(a) * (r + t / 2), cy + math.sin(a) * (r + t / 2) * sy))
        inner.append((cx + math.cos(a) * (r - t / 2), cy + math.sin(a) * (r - t / 2) * sy))
    return outer + inner[-2:0:-1]


def star(cx, cy, size, w, rot=0.0, points=4):
    if size < 1:
        return None
    pts = []
    for i in range(points * 2):
        a = rot + math.pi * i / points
        r = size if i % 2 == 0 else max(1.0, w)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return Sharp(pts)


def orb(cx, cy, r):
    if r < 0.5:
        return None
    return [(cx + math.cos(2 * math.pi * i / 12) * r, cy + math.sin(2 * math.pi * i / 12) * r) for i in range(12)]


# ------------------------------------------------------------------ kinds
DIRS = {"up": -math.pi / 2, "down": math.pi / 2, "right": 0.0, "left": math.pi}


def pieces(kind, d, t, dur, loop, W, H, rnd_seed, k):
    """The outlines at time t, as a function of the tone's thickness factor: [(fn(wf) -> outline)]."""
    cx, cy = W / 2, H / 2
    a = DIRS.get(d, 0.0)
    u = t / dur
    R = random.Random(rnd_seed)
    out = []
    S = min(W, H)

    if kind in ("hit", "hitstar", "dissapear", "ripple"):
        e = ease_out(u / 0.5)
        fade = 1 - min(1.0, max(0.0, (u - 0.2) / 0.5))
        rings = 2 if kind == "ripple" else 1 + R.randrange(2)
        for i in range(rings):
            r = S * (0.08 + 0.3 * e) * (1 - 0.25 * i)
            sy = 0.35 if kind == "ripple" else 1.0
            ry = cy + (S * 0.3 if kind == "ripple" else 0)
            out.append(lambda wf, r=r, sy=sy, ry=ry: ring(cx, ry, r, 10 * k * fade * wf, sy=sy))
        if kind == "hitstar":
            sz = S * 0.42 * bump(u / 0.6)
            rot = R.uniform(0, 1) + u * 0.6
            out.append(lambda wf: star(cx, cy, sz * (0.6 + 0.4 * wf), 6 * wf * k, rot))
        if kind == "dissapear":
            r = S * 0.3 * (1 - ease_out(u / 0.6))
            out.append(lambda wf: ring(cx, cy, r, 12 * k * wf * (1 - u)))
        for i in range(10):
            ang = R.uniform(0, 2 * math.pi)
            r0 = S * (0.1 + 0.32 * e)
            ln = S * 0.08 * fade
            out.append(lambda wf, ang=ang, r0=r0, ln=ln: spindle(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0,
                                                               cx + math.cos(ang) * (r0 + ln), cy + math.sin(ang) * (r0 + ln),
                                                               7 * k * wf))
    elif kind == "glare":
        e = ease_out(u / 0.55)
        fade = 1 - min(1.0, max(0.0, (u - 0.3) / 0.5))
        sides = 4
        sy = 0.4 if d in ("up", "down") else 1.0
        oy = cy + (S * 0.25 if d == "up" else -S * 0.25 if d == "down" else 0)
        rot = math.pi / 4 if d != "right" else 0
        r = S * (0.1 + 0.25 * e)
        out.append(lambda wf: ring(cx, oy - (S * 0.2 * e if d == "up" else -S * 0.2 * e if d == "down" else 0), r,
                                   9 * k * fade * wf, sy=sy, rot=rot, sides=sides))
    elif kind == "explosion":
        e = ease_out(u / 0.4)
        fade = 1 - min(1.0, max(0.0, (u - 0.15) / 0.55))
        for i in range(14):
            ang = 2 * math.pi * i / 14 + R.uniform(-0.2, 0.2)
            r0 = S * 0.04 + S * 0.25 * e
            ln = S * R.uniform(0.08, 0.2) * fade
            out.append(lambda wf, ang=ang, r0=r0, ln=ln: spindle(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0,
                                                               cx + math.cos(ang) * (r0 + ln), cy + math.sin(ang) * (r0 + ln),
                                                               9 * k * wf, 0.3))
        out.append(lambda wf: ring(cx, cy, S * 0.38 * e, 8 * k * fade * wf))
        out.append(lambda wf: orb(cx, cy, S * 0.1 * bump(u / 0.4) * (0.5 + wf)))
    elif kind == "ray":
        grow = ease_out(u / 0.25)
        thin = 1 - min(1.0, max(0.0, (u - 0.3) / 0.6)) if not loop else 0.75 + 0.25 * math.sin(u * 2 * math.pi * 4)
        L = S * 0.8 * grow
        x0, y0 = cx - math.cos(a) * S * 0.4, cy - math.sin(a) * S * 0.4
        out.append(lambda wf: spindle(x0, y0, x0 + math.cos(a) * L, y0 + math.sin(a) * L, 40 * k * thin * wf, 0.15))
        out.append(lambda wf: ring(x0, y0, S * 0.1 * grow, 8 * k * thin * wf, sx=1.0 if d in ("up", "down") else 0.35,
                                   sy=0.35 if d in ("up", "down") else 1.0))
    elif kind == "slash":
        radial = d == "radial"
        sw = ease_out(u / 0.3)
        fade = 1 - min(1.0, max(0.0, (u - 0.25) / 0.5))
        r = S * R.uniform(0.25, 0.36)
        a0 = (a - math.pi / 2 - 1.2) if not radial else R.uniform(0, 6.28)
        sweep = (2.4 if not radial else 4.6) * sw
        tail = sweep * 0.35 * u
        out.append(lambda wf: crescent(cx, cy, r, a0 + tail, sweep - tail, 26 * k * fade * wf))
    elif kind == "charge":
        e = u if loop else min(1.0, u / 0.7)
        for i in range(12):
            ang = 2 * math.pi * i / 12 + R.uniform(-0.3, 0.3)
            ph = (e * 2 + i / 12) % 1.0 if loop else e
            r0 = S * 0.45 * (1 - ph)
            ln = S * 0.12 * (1 - ph)
            out.append(lambda wf, ang=ang, r0=r0, ln=ln: spindle(cx + math.cos(ang) * (r0 + ln), cy + math.sin(ang) * (r0 + ln),
                                                               cx + math.cos(ang) * r0, cy + math.sin(ang) * r0, 7 * k * wf))
        rr = S * (0.05 + 0.08 * (0.5 + 0.5 * math.sin(u * 2 * math.pi * 3)) if loop else 0.05 + 0.12 * e)
        out.append(lambda wf: orb(cx, cy, rr * (0.6 + 0.4 * wf)))
    elif kind in ("projectile", "shot"):
        if kind == "shot":
            p = ease_out(u / 0.45)
            x = cx - S * 0.45 + S * 0.9 * p
        else:
            x = cx + math.sin(u * 2 * math.pi * 2) * 4
        y = cy
        r = S * 0.07 * k
        out.append(lambda wf: orb(x, y, r * (0.5 + 0.5 * wf)))
        out.append(lambda wf: spindle(x - S * 0.35, y, x + r * 0.5, y, 2 * r * wf, 0.85))
        out.append(lambda wf: crescent(x - r * 0.4, y, r * 1.6, -1.0, 2.0, 10 * k * wf))
        if kind == "shot":
            mz = bump(u / 0.3)
            out.append(lambda wf: ring(cx - S * 0.45, cy, S * 0.12 * (1 - mz) + 4, 8 * k * mz * wf, sx=0.4))
    elif kind == "shield":
        pulse = 0.92 + 0.08 * math.sin(u * 2 * math.pi * 2)
        grow = ease_out(u / 0.3) if not loop else 1.0
        out.append(lambda wf: ring(cx, cy, S * 0.3 * grow * pulse, 14 * k * wf))
        for i in range(2):
            rot = u * 2 * math.pi + i * math.pi / 2
            out.append(lambda wf, rot=rot: ring(cx, cy, S * 0.22 * grow, 6 * k * wf, sx=1.0, sy=0.35, rot=rot))
    elif kind == "aura":
        for i in range(18):
            ang = 2 * math.pi * i / 18
            ph = (u * 3 + R.random()) % 1.0
            r0 = S * 0.22
            ln = S * 0.18 * math.sin(math.pi * ph)
            out.append(lambda wf, ang=ang, r0=r0, ln=ln: spindle(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0,
                                                               cx + math.cos(ang) * (r0 + ln), cy + math.sin(ang) * (r0 + ln),
                                                               9 * k * wf))
    elif kind == "rays":
        for i in range(7):
            off = R.uniform(-0.42, 0.42)
            ph = (u * 1.5 + R.random()) % 1.0
            ln = S * R.uniform(0.3, 0.6)
            p = -0.6 + 1.6 * ph
            if d == "up":
                x = cx + off * W
                y1 = H * (1 - p)
                out.append(lambda wf, x=x, y1=y1, ln=ln: spindle(x, y1 + ln, x, y1, 12 * k * wf))
            else:
                y = cy + off * H
                x1 = W * p
                out.append(lambda wf, y=y, x1=x1, ln=ln: spindle(x1 - ln, y, x1, y, 12 * k * wf))
    return out


def classify(name):
    n = name.lower()
    d = ("radial" if "radial" in n else "up" if " up" in n or n.startswith("up") else "down" if "down" in n else
         "left" if "left" in n else "right" if "right" in n else "radial")
    loop = "loop" in n
    for words, kind in (("dissapear", "dissapear"), ("shield", "shield"), ("aura", "aura"), ("hit rays", "explosion"),
                        ("rays", "rays"), ("glare", "glare"), ("star", "hitstar"), ("ripple", "ripple"),
                        ("charge", "charge"), ("explosion", "explosion"), ("slash", "slash"), ("projectile", "projectile"),
                        ("shot", "shot"), ("ray", "ray"), ("hit", "hit")):
        if words in n:
            break
    else:
        kind = "hit"
    if kind in ("aura", "shield") and "loop" in n:
        loop = True
    return kind, d, loop


ES_KIND = {"hit": "Impacto", "hitstar": "Estrella", "dissapear": "Desaparecer", "ripple": "Onda", "glare": "Destello",
           "explosion": "Estallido", "ray": "Haz", "slash": "Corte", "charge": "Carga", "projectile": "Proyectil",
           "shot": "Disparo", "shield": "Escudo", "aura": "Aura", "rays": "Rayos"}
EN_KIND = {"hit": "Hit", "hitstar": "Star", "dissapear": "Vanish", "ripple": "Ripple", "glare": "Glare",
           "explosion": "Burst", "ray": "Beam", "slash": "Slash", "charge": "Charge", "projectile": "Projectile",
           "shot": "Shot", "shield": "Shield", "aura": "Aura", "rays": "Rays"}
ES_DIR = {"up": "arriba", "down": "abajo", "right": "derecha", "left": "izquierda", "radial": "radial"}

NAMES = """001 Hit Radial|002 Hit Star Radial|003 Glare Hit Up|005 Hit Radial|006 Hit Explosion Radial|008 Hit Radial|
011 Ray Up Loop|012 Slash Right|014 Slash Up|015 Slash Radial|016 Hit Explosion Radial|017 Charge Up|018 Ray Right|
019 Ray Up|020 Slash1 Ray Right|021 Ray Right|022 Slash Right|023 Projectile Right Loop|025 Ray Hit Up|027 Ray Left|
028 Slash Radial|029 Slash Right|030 Slash Right|031 Slash Up|032 Slash Right|034 Slash Radial|037 Ray Ripple Hit Up|
038 Ray Hit Explosion Up|039 Ray Radial Wide|045 Shot Right MIX|047 Shot Right Loop MIX|049 Shot Right Loop MIX|
050 Shot Right MIX|053 Shot Right MIX|055 Shot Right MIX|057 Shot Right Loop MIX|058 Glare Radial|
059 Hit Explosion Radial|060 Up Ray MIX|063 Ray Up|064 Ray Up|065 Ray Up|067 Ray Up|068 Ray Up MIX|069 Ray Up MIX|
070 Ray Up|071 Ray Up|073 Ray Up|075 Ray Up|076 Ray Up MIX|077 Ray Radial|078 Shield Radial|079 Ray Right|
080 Charge Ray Up MIX|084 Ray Right MIX|086 Charge Explosion Radial MIX|087 Charge Radial Loop MIX|
088 Projectile Right Loop MIX|089 Shot Right MIX|091 Projectile Shot Right Loop MIX|093 Ray Up MIX|
096 Hit Explosion Radial MIX|097 Hit Explosion Radial MIX|100 Ray Right Loop MIX|102 Shot Right MIX|
103 Radial Hit Custom Wide|105 Ray Left Loop|106 Hit Radial MIX|108 Explosion Hit Radial MIX|
109 Explosion Hit Radial MIX|111 Shot Right MIX|114 Slash Radial MIX|115 Slash Charge Radial Loop MIX|118 Hit Radial|
119 Dissapear|120 Dissapear|121 Hit Star Radial|122 Hit Star Radial|123 Glare Down|124 Glare Down|125 Glare Down|
125 Glare Right|126 Aura Radial Loop|127 Aura Radial Loop|128 Aura Radial Loop|129 Hit Rays Radial|
130 Hit Rays Radial|131 Rays Up|132 Rays Right"""


def make_one(index, entry):
    num, name = entry.split(" ", 1)
    kind, d, loop = classify(name)
    mix = "mix" in name.lower()
    wide = "wide" in name.lower() or kind == "rays"
    W, H = (768, 432) if wide else (512, 512)
    dur = 2.0 if loop else (1.0 if kind in ("hit", "hitstar", "glare", "slash") else 1.3)
    seed = 7300 + index * 41
    R = random.Random(seed)
    k = 0.9 + 0.4 * R.random()
    pal = R.choice(["azul", "azul", "azul", "cian", "violeta"]) if not mix else R.choice(["cian", "oro", "rosa", "violeta"])
    rim, body, core = PALETTES[pal]
    slug = f"{num}-{kind}" + ("" if d == "radial" else "-" + d)
    id = "ex-energia-" + slug + ("-mix" if mix else "") + ("-bucle" if loop else "")
    if name.lower().startswith("125 glare"):
        pass
    es = f"Energía {num} · {ES_KIND[kind]} {ES_DIR[d]}" + (" (mezcla)" if mix else "") + (" (bucle)" if loop else "")
    en = f"Energy {num} · {EN_KIND[kind]} {d}" + (" (mix)" if mix else "") + (" (loop)" if loop else "")
    frames = int(round(dur * 30))
    s = new(id, es, en, "energia", frames, 4300 + index, ["energía", "energy", ES_KIND[kind].lower(), pal], loop=loop,
            size=W, height=H if wide else 0, thumb=0.5 if loop else 0.3)
    lay = Layers(s, [("borde", rim), ("cuerpo", body), ("nucleo", core)], 36, glow_blur=22, glow_opacity=90)
    sparks = Sim(dur, loop=loop)
    if mix:
        for i in range(22):
            ang = R.uniform(0, 2 * math.pi)
            v = R.uniform(300, 800)
            sparks.add(Particle(W / 2, H / 2, math.cos(ang) * v, math.sin(ang) * v, R.uniform(0, dur * 0.6),
                                R.uniform(0.3, 0.6), R.uniform(4, 7), R.randrange(1 << 20), drag=1.5, shape="spark"))
    for f in range(0, frames, STEP):
        t = f / 30
        ps = pieces(kind, d, t, dur, loop, W, H, seed, k)
        extra = [particle_outline(p, st, 1.0, f // STEP) for p, st in sparks.frame(t)]
        for tone, wf in enumerate(WIDTHS):
            outs = [o for o in (fn(wf) for fn in ps) if o]
            if tone == 0:
                outs += extra
            elif tone == 2:
                outs += [particle_outline(p, st, 0.5, f // STEP) for p, st in sparks.frame(t)]
            lay.draw(f, tone, outs)
    lay.build()
    return s


ENTRIES = [e.strip() for e in NAMES.replace("\n", "").split("|") if e.strip()]
STICKERS = [lambda i=i, e=e: make_one(i, e) for i, e in enumerate(ENTRIES)]
