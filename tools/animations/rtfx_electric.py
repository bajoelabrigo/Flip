"""Animaciones Extremas · Electricidad (0.26): one element of our own for each of RTFX's 40 electricity
ones, by kind, direction, timing and palette (their names and previews only told us what each one
does).

Electricity is thin jagged line work that glows and is redrawn on every drawing (on twos), so it
crackles: bolts from one point to another, bolts thrown out of a hit, a crackling ring round a
charge, arcs crawling up, a bolt shot across. Each bolt is a strip that narrows to its tips, drawn
as a coloured rim, a light body and a white core, with a glow behind (rtfx_engine.Layers).
"""

from __future__ import annotations

import math
import random

from rtfx_energy import orb, ring
from rtfx_engine import STEP, Layers, Sharp, new

PALETTES = {
    "azul": ("#2f6bff", "#9fd8ff", "#ffffff"),
    "cian": ("#00b4d8", "#a6f6ff", "#ffffff"),
    "violeta": ("#7a2cff", "#d9b0ff", "#ffffff"),
    "oro": ("#ff9a00", "#ffe27a", "#ffffff"),
}
WIDTHS = (1.0, 0.5, 0.2)
DIRS = {"up": -math.pi / 2, "down": math.pi / 2, "right": 0.0, "left": math.pi}


def jag(points, rnd, amount, splits=3):
    """The polyline cut and pushed sideways at random, `splits` times over, so it zigzags."""
    pts = list(points)
    a = amount
    for _ in range(splits):
        out = [pts[0]]
        for p, q in zip(pts, pts[1:]):
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            dx, dy = q[0] - p[0], q[1] - p[1]
            L = math.hypot(dx, dy) or 1.0
            off = rnd.uniform(-a, a)
            out += [(mx - dy / L * off, my + dx / L * off), q]
        pts = out
        a *= 0.55
    return pts


def strip(pts, w):
    """A polyline as a filled strip `w` wide in the middle and pointed at both ends."""
    if len(pts) < 2 or w < 0.3:
        return None
    n = len(pts)
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        p0 = pts[max(0, i - 1)]
        p1 = pts[min(n - 1, i + 1)]
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy) or 1.0
        u = i / (n - 1)
        h = w / 2 * math.sin(math.pi * u) ** 0.5
        left.append((x - dy / L * h, y + dx / L * h))
        right.append((x + dy / L * h, y - dx / L * h))
    return Sharp(left + right[::-1])


def bolt(x0, y0, x1, y1, rnd, amount, w):
    return lambda wf: strip(jag([(x0, y0), (x1, y1)], random.Random(rnd), amount), w * wf)


def pieces(kind, d, t, f, dur, loop, W, H, seed, k):
    cx, cy = W / 2, H / 2
    S = min(W, H)
    a = DIRS.get(d, -math.pi / 2)
    u = t / dur
    R = random.Random(seed)            # stable choices
    F = seed * 1000 + f // STEP         # what changes every drawing
    life = 1.0 if loop else max(0.0, 1.0 - max(0.0, u - 0.35) / 0.5)
    if life <= 0:
        return []
    out = []
    w = 9 * k * life

    if kind == "ray":
        L = S * 0.85 * min(1.0, u / 0.15 if not loop else 1.0)
        x0, y0 = cx - math.cos(a) * S * 0.42, cy - math.sin(a) * S * 0.42
        for j in range(R.randint(1, 3)):
            out.append(bolt(x0, y0, x0 + math.cos(a) * L, y0 + math.sin(a) * L, F * 7 + j, S * 0.12, w * (1 - 0.3 * j)))
    elif kind in ("hit", "explosion"):
        n = R.randint(5, 9)
        reach = S * (0.2 + 0.25 * min(1.0, u / 0.25))
        o = (cx, cy) if d == "radial" else (cx - math.cos(a) * S * 0.15, cy - math.sin(a) * S * 0.15)
        spread = math.pi if d == "radial" else 0.7
        for j in range(n):
            ang = (a if d != "radial" else 0) + (2 * math.pi * j / n if d == "radial" else R.uniform(-spread, spread))
            ang += random.Random(F + j).uniform(-0.2, 0.2)
            out.append(bolt(o[0], o[1], o[0] + math.cos(ang) * reach, o[1] + math.sin(ang) * reach, F * 13 + j,
                            S * 0.06, w))
        if kind == "explosion":
            out.append(lambda wf: ring(o[0], o[1], min(reach * 0.9, S * 0.3), 6 * k * life * wf))
        if u < 0.25:
            out.append(lambda wf: orb(o[0], o[1], S * 0.08 * (1 - u / 0.25) * (0.5 + wf)))
    elif kind == "charge":
        # A crackling ring (or band) round the centre, with an orb that pulses.
        horizontal = d == "horizontal"
        vertical = d == "vertical"
        r = S * (0.22 + 0.04 * math.sin(u * 2 * math.pi * 3))
        if horizontal or vertical:
            for j in range(2):
                off = (j - 0.5) * S * 0.2
                if horizontal:
                    out.append(bolt(W * 0.12, cy + off, W * 0.88, cy + off, F * 17 + j, S * 0.11, w))
                else:
                    out.append(bolt(cx + off, H * 0.12, cx + off, H * 0.88, F * 17 + j, S * 0.11, w))
        else:
            # Each charge its own: ring size, how many rings, how rough, the orb, how many spokes.
            r *= R.uniform(0.6, 1.5)
            rings = R.choice([1, 1, 2])
            rough = R.uniform(0.02, 0.07)
            orb_r = R.uniform(0.0, 0.11)
            spokes = R.randint(0, 6)
            m = 14
            for g in range(rings):
                rg = r * (1 - 0.35 * g)
                pts = [(cx + math.cos(2 * math.pi * i / m) * rg, cy + math.sin(2 * math.pi * i / m) * rg)
                       for i in range(m + 1)]
                out.append(lambda wf, pts=pts, g=g: strip(jag(pts, random.Random(F * 19 + g), S * rough, 2),
                                                          w * 0.9 * wf))
            if orb_r > 0.02:
                out.append(lambda wf: orb(cx, cy, S * orb_r * (0.8 + 0.2 * math.sin(u * 30)) * (0.6 + 0.4 * wf)))
            for j in range(spokes):
                ang = random.Random(F + 31 * j).uniform(0, 2 * math.pi)
                out.append(bolt(cx, cy, cx + math.cos(ang) * r, cy + math.sin(ang) * r, F * 23 + j, S * 0.04, w * 0.7))
        if not loop and u > 0.7:
            # The charge lets go.
            for j in range(8):
                ang = 2 * math.pi * j / 8
                reach = S * 0.45
                out.append(bolt(cx, cy, cx + math.cos(ang) * reach, cy + math.sin(ang) * reach, F * 29 + j, S * 0.05,
                                w * (1 - (u - 0.7) / 0.3)))
    elif kind == "crawl":
        # Arcs crawling up a line, each a short bolt that jumps from spot to spot.
        for j in range(3):
            y = H * (0.85 - ((u * 1.5 + j / 3) % 1.0) * 0.7)
            x = cx + random.Random(F + j).uniform(-S * 0.15, S * 0.15)
            out.append(bolt(x - S * 0.12, y, x + S * 0.12, y - S * 0.08, F * 37 + j, S * 0.05, w * 0.8))
    elif kind == "shot":
        p = min(1.0, u / 0.4)
        x = W * 0.1 + W * 0.75 * p
        y = cy
        out.append(bolt(x - S * 0.4, y, x, y, F * 41, S * 0.06, w))
        out.append(lambda wf: orb(x, y, S * 0.05 * (0.6 + 0.4 * wf)))
        if d == "horizontal" and p >= 1.0:
            for j in range(6):
                ang = math.pi + random.Random(F + j).uniform(-1.2, 1.2)
                out.append(bolt(x, y, x + math.cos(ang) * S * 0.25, y + math.sin(ang) * S * 0.25, F * 43 + j,
                                S * 0.04, w * 0.8))
    return out


def classify(name):
    n = name.lower()
    d = ("radial" if "radial" in n else "horizontal" if "horizontal" in n else "vertical" if "vertical" in n else
         "up" if "up" in n else "down" if "down" in n else "right" if "right" in n else "radial")
    loop = "loop" in n
    for words, kind in (("charge", "charge"), ("shot", "shot"), ("explosion", "explosion"), ("ray", "ray"),
                        ("hit", "hit"), ("loop up", "crawl"), ("up loop", "crawl")):
        if words in n:
            break
    else:
        kind = "crawl"
    if kind == "shot" and d not in ("right", "horizontal"):
        d = "right"
    return kind, d, loop


ES_KIND = {"ray": "Rayo", "hit": "Chispazo", "explosion": "Descarga", "charge": "Carga", "crawl": "Arcos",
           "shot": "Disparo"}
EN_KIND = {"ray": "Bolt", "hit": "Zap", "explosion": "Discharge", "charge": "Charge", "crawl": "Arcs", "shot": "Shot"}
ES_DIR = {"up": "arriba", "down": "abajo", "right": "derecha", "radial": "radial", "horizontal": "horizontal",
          "vertical": "vertical"}

NAMES = """001 Hit Explosion Up|003 Ray Down|004 Ray Up|005 Shot Ray Up|006 Hit Ray Up|007 Ray Right|009 Loop Up|
010 Explosion Radial|011 Ray Up|013 Up Loop|014 Charge Radial Loop|015 Charge Radial Loop|016 Charge Right|
017 Ray Right|018 Ray Up Loop|019 Ray Hit Up|020 Ray Shot Up|021 Explosion Radial|022 Hit Explosion Right|
025 Hit Explosion Radial|026 Ray Up|027 Hit Explosion Radial|032 Hit Explosion Radial|033 Ray Right|034 Charge Radial|
036 Explosion Right MIX|037 Shot Right MIX|038 Charge Radial MIX|040 Shot Hit Horizontal|042 Charge loop|
043 Charge Horizontal|044 Charge Radial|045 Charge Vertical|046 Charge Vertical|047 Charge Horizontal|
048 Charge Horizontal|049 Charge Radial|050 Charge Radial|051 Charge Radial|052 Charge Radial"""


def make_one(index, entry):
    num, name = entry.split(" ", 1)
    kind, d, loop = classify(name)
    mix = "mix" in name.lower()
    W, H = 512, 512
    dur = 2.0 if loop else 1.2
    seed = 9700 + index * 59
    R = random.Random(seed)
    k = 0.9 + 0.5 * R.random()
    pal = R.choice(["azul", "azul", "cian"]) if not mix else R.choice(["violeta", "oro", "cian"])
    rim, body, core = PALETTES[pal]
    slug = f"{num}-{kind}" + ("" if d == "radial" else "-" + d)
    id = "ex-electricidad-" + slug + ("-mix" if mix else "") + ("-bucle" if loop else "")
    es = f"Electricidad {num} · {ES_KIND[kind]} {ES_DIR[d]}" + (" (mezcla)" if mix else "") + (" (bucle)" if loop else "")
    en = f"Electricity {num} · {EN_KIND[kind]} {d}" + (" (mix)" if mix else "") + (" (loop)" if loop else "")
    frames = int(round(dur * 30))
    s = new(id, es, en, "electricidad", frames, 5100 + index, ["electricidad", "electricity", "rayo", pal], loop=loop,
            thumb=0.5 if loop else 0.25)
    lay = Layers(s, [("borde", rim), ("cuerpo", body), ("nucleo", core)], 16, glow_blur=18, glow_opacity=95)
    for f in range(0, frames, STEP):
        t = f / 30
        ps = pieces(kind, d, t, f, dur, loop, W, H, seed, k)
        for tone, wf in enumerate(WIDTHS):
            lay.draw(f, tone, [o for o in (fn(wf) for fn in ps) if o])
    lay.build()
    return s


ENTRIES = [e.strip() for e in NAMES.replace("\n", "").split("|") if e.strip()]
STICKERS = [lambda i=i, e=e: make_one(i, e) for i, e in enumerate(ENTRIES)]
