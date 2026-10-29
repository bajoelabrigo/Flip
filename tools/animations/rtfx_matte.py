"""Animaciones Extremas · Mates (0.26): one element of our own for each of RTFX's 45 transition mattes,
by kind, direction and timing (their names and previews only told us what each one does).

A matte is a full-frame 16:9 wipe in white: shapes grow from an edge or the centre until the whole
frame is covered (an «In», used as the alpha of the next shot), or the frame starts covered and the
shapes eat it away (the inverted ones). Spikes shooting across, a spiky burst, a swirl, liquid blobs
that run together, diagonal slashes, bubbles that split. White on transparent, so it works as a
track matte and as a flash on its own.
"""

from __future__ import annotations

import math
import random

from rtfx_engine import STEP, Layers, Sharp, blob, new

W, H = 768, 432
FULL = Sharp([(-20, -20), (W + 20, -20), (W + 20, H + 20), (-20, H + 20)])
DIRS = {"right": 0.0, "left": math.pi, "up": -math.pi / 2, "down": math.pi / 2, "diagonal": -math.pi / 5}


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def spike(x0, y0, ang, length, width):
    """A tapered spike from (x0, y0) along `ang`."""
    ca, sa = math.cos(ang), math.sin(ang)
    nx, ny = -sa, ca
    return Sharp([(x0 + nx * width / 2, y0 + ny * width / 2), (x0 + ca * length * 0.55 + nx * width * 0.3,
                   y0 + sa * length * 0.55 + ny * width * 0.3), (x0 + ca * length, y0 + sa * length),
                  (x0 + ca * length * 0.55 - nx * width * 0.3, y0 + sa * length * 0.55 - ny * width * 0.3),
                  (x0 - nx * width / 2, y0 - ny * width / 2)])


def shapes(kind, d, u, R, f):
    """The white outlines at progress u (0 = nothing, 1 = the frame covered)."""
    e = ease(u)
    if e >= 0.97:
        return [FULL]
    out = []
    diag = math.hypot(W, H)
    if kind == "streaks":
        a = DIRS.get(d, 0.0)
        # From the edge the wipe comes from: the spikes start beyond it and run across.
        nx, ny = -math.sin(a), math.cos(a)
        bx, by = W / 2 - math.cos(a) * diag * 0.55, H / 2 - math.sin(a) * diag * 0.55
        for j in range(18):
            off = (j / 17 - 0.5) * diag * 1.1 + R[j] * 30
            length = diag * (0.2 + 1.3 * e) * (0.7 + 0.5 * R[j + 20])
            out.append(spike(bx + nx * off, by + ny * off, a + (R[j + 40] - 0.5) * 0.12, length,
                             diag / 14 * (0.6 + 0.8 * R[j + 60]) * (0.6 + e)))
    elif kind == "burst":
        n = 22
        r = diag * 0.62 * e
        pts = []
        for i in range(n * 2):
            ang = math.pi * i / n + R[i % 40] * 0.15 + (f * 0.002 if d == "ccw" else 0)
            rr = r * (1.0 if i % 2 == 0 else 0.45 + 0.25 * R[(i + 7) % 80])
            pts.append((W / 2 + math.cos(ang) * rr, H / 2 + math.sin(ang) * rr))
        out.append(Sharp(pts))
    elif kind == "swirl":
        sign = -1 if d == "ccw" else 1
        for arm in range(4):
            for i in range(16):
                t = i / 15
                ang = sign * (arm * math.pi / 2 + t * 3.5 + e * 2.5)
                rr = diag * 0.55 * t
                size = diag * 0.04 + diag * 0.22 * e * t
                out.append(blob(W / 2 + math.cos(ang) * rr, H / 2 + math.sin(ang) * rr, size, arm * 100 + i,
                                rough=0.1, n=10))
    elif kind == "liquid":
        for j in range(14):
            cx = W * R[j]
            cy = H * R[j + 20]
            if d in ("right", "left", "up", "down"):
                a = DIRS[d]
                # Blobs arrive from that side in order.
                lag = (cx / W if d == "right" else 1 - cx / W if d == "left" else 1 - cy / H if d == "up" else cy / H)
                g = ease((u - lag * 0.5) / 0.5)
            else:
                g = ease((u - R[j + 40] * 0.4) / 0.6)
            if g <= 0:
                continue
            out.append(blob(cx, cy, diag * 0.28 * g * (0.6 + 0.6 * R[j + 60]), j * 31 + 7, rough=0.18, n=14))
    elif kind == "diagonal":
        for j in range(9):
            off = (j / 8 - 0.5) * diag * 1.2
            g = ease((u - j / 8 * 0.45) / 0.55)
            if g <= 0:
                continue
            a = -math.pi / 4
            cx = W / 2 + math.cos(a + math.pi / 2) * off
            cy = H / 2 + math.sin(a + math.pi / 2) * off
            out.append(spike(cx - math.cos(a) * diag * 0.6, cy - math.sin(a) * diag * 0.6, a, diag * 1.2,
                             diag * 0.17 * g))
    elif kind == "bubbles":
        for j in range(30):
            cx, cy = W * R[j], H * R[j + 30]
            g = ease((u - R[j + 50] * 0.5) / 0.5)
            if g > 0:
                out.append(blob(cx, cy, diag * 0.16 * g * (0.5 + R[j + 10]), j, rough=0.04, n=10))
    elif kind == "drip":
        # Liquid running down (or up) from one edge like paint.
        up = d == "up"
        for j in range(12):
            x = W * (j + 0.5) / 12
            length = H * 1.3 * ease((u - R[j] * 0.3) / 0.7)
            w = W / 12 * 1.3
            y0 = H + 10 if up else -10
            y1 = y0 - length if up else y0 + length
            pts = [(x - w / 2, y0), (x + w / 2, y0), (x + w / 2, y1 + (w / 2 if up else -w / 2)), (x, y1),
                   (x - w / 2, y1 + (w / 2 if up else -w / 2))]
            out.append(pts)
    return out


def classify(name):
    n = name.lower()
    inv = "inv" in n
    d = ("ccw" if "ccw" in n else "cw" if " cw" in n else "diagonal" if "diagonal" in n else "radial" if "radial" in n
         else "right" if "right" in n else "left" if "left" in n else "up" if "up" in n else "down" if "down" in n
         else "radial")
    if n.startswith("liquid"):
        kind = "drip" if d in ("up", "down") else "liquid"
    elif n.startswith("fission"):
        kind = "bubbles"
    elif n.startswith("energy"):
        kind = "streaks" if "vertical" in n else "burst"
        if "vertical" in n:
            d = "up"
    elif d in ("ccw", "cw"):
        kind = "swirl"
    elif d == "diagonal":
        kind = "diagonal"
    elif d == "radial" or " in " in f" {n} " or " out " in f" {n} ":
        kind = "burst"
    else:
        kind = "streaks"
    return kind, d, inv


ES_KIND = {"streaks": "Púas", "burst": "Estallido", "swirl": "Remolino", "liquid": "Manchas", "diagonal": "Cortes",
           "bubbles": "Burbujas", "drip": "Chorreo"}
EN_KIND = {"streaks": "Spikes", "burst": "Burst", "swirl": "Swirl", "liquid": "Blobs", "diagonal": "Slashes",
           "bubbles": "Bubbles", "drip": "Drip"}
ES_DIR = {"right": "derecha", "left": "izquierda", "up": "arriba", "down": "abajo", "radial": "radial",
          "diagonal": "diagonal", "cw": "horario", "ccw": "antihorario"}

NAMES = """001 Inv Right|001 Inv Up|001 Left Inv|001 Right Inv|002 Inv Left|002 Inv Right|002 Right Inv|003 Diagonal Inv|
004 Down|004 Up Inv|005 In|005 Out Inv|006 In CCW|007 Inv Out|007 Out Inv|008 Inv Out Inv|008 Out|009 Diagonal|
009 Down Inv|009 Right|010 Diagonal|010 Diagonal B|011 Right|012 Right Inv|013 Radial In|014 Radial Out Inv|
Energy 095 Vertical|Energy 133 Inv|Fission 001 Right Inv|Fission 002 Radial Out Inv|Fission 003 Diagonal Inv|
Fission 004 Horizontal Inv|Liquid 073 Radial CW|Liquid 074 Radial Out CW|Liquid 075 Radial Out Inv|
Liquid 077 Right Inv|Liquid 078 Down Inv|Liquid 079 Down Inv|Liquid 080 Up Inv|Liquid 081 Radial CCW Inv|
Liquid 082 Up Inv|Liquid 083 Radial Out|Liquid 084 Right|Liquid 086 CCW|Liquid 089 Up Inv"""


def make_one(index, entry):
    kind, d, inv = classify(entry)
    if kind == "liquid" and d in ("cw", "ccw"):
        d = "radial"
    dur = 1.0
    frames = 30
    R = [random.Random(4400 + index * 61 + i).random() for i in range(100)]
    words = entry.split(" ")
    num = next(w for w in words if w[:1].isdigit())
    fam = "" if entry[:1].isdigit() else words[0].lower() + "-"
    variant = "b" if entry.endswith(" B") else ""
    slug = f"{fam}{num}{variant}-{kind}" + ("" if d in ("radial", kind) else "-" + d) + ("-inv" if inv else "")
    id = "ex-mate-" + slug
    # RTFX has two of some (one with the alpha, one inverted, of the same move): the second is «B».
    twin = sum(1 for e in ENTRIES[:index] if classify(e) == classify(entry) and e.split(" ")[0] == words[0]
               and next(w for w in e.split(" ") if w[:1].isdigit()) == num)
    if twin:
        id += "-b"
        variant = "b"
    label = (words[0] + " " if fam else "") + num + (" B" if variant else "")
    es = f"Mate {label} · {ES_KIND[kind]} {ES_DIR[d]}" + (" (invertido)" if inv else "")
    en = f"Matte {label} · {EN_KIND[kind]} {d}" + (" (inverted)" if inv else "")
    s = new(id, es, en, "mates", frames, 5400 + index, ["mate", "matte", "transición", "transition", "máscara"],
            loop=False, size=W, height=H, thumb=0.5)
    lay = Layers(s, [("mate", "#ffffff")], 80, glow=False)
    for f in range(0, frames, STEP):
        u = f / (frames - 2)
        lay.draw(f, 0, shapes(kind, d, 1 - u if inv else u, R, f))
    lay.build()
    return s


ENTRIES = [e.strip() for e in NAMES.replace("\n", "").split("|") if e.strip()]
STICKERS = [lambda i=i, e=e: make_one(i, e) for i, e in enumerate(ENTRIES)]
