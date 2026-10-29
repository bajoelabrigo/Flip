"""Animaciones Extremas (0.26, Jorge: «lo de RTFX entra en Stock como Animaciones Extremas»): our own
hand-drawn-looking cartoon / anime FX in the manner of the RTFX pack, studied in its demos (nothing
of its content is used). What makes that look, and what these copy:
  - frame by frame, "on twos" (a new drawing every 2 frames at 30 fps), the shapes boiling a little
    from drawing to drawing;
  - flat cel colours in two or three tones (a body, a light core, a dark rim), no gradients;
  - big anticipation and fast release: bursts that pop out in a few frames and break up slowly;
  - every colour a slot, so each one can be recoloured in Flip.

    py tools/animations/build.py --designs extremas [--only id,id] [--no-render]

Categories (Stock › Animaciones › «Extremas · …»): extremas-fuego, -explosiones, -humo, -energia,
-electricidad, -chispas, -liquidos, -lineas, -destellos, -transiciones.
"""

from __future__ import annotations

import math
import random

from lottie import Sticker, fill, group, layer_transform, static, transform

C = 256
STEP = 2  # on twos


# ------------------------------------------------------------------ drawing helpers
class Sharp(list):
    """An outline drawn with straight sides (bolts, speed lines): no rounding."""


def _bez(points, smooth=1.0):
    """A closed smooth outline through points (Catmull-Rom handles), as a Lottie shape value."""
    n = len(points)
    ins, outs = [], []
    for i in range(n):
        px, py = points[i - 1]
        nx, ny = points[(i + 1) % n]
        tx, ty = (nx - px) * smooth / 6, (ny - py) * smooth / 6
        ins.append([round(-tx, 2), round(-ty, 2)])
        outs.append([round(tx, 2), round(ty, 2)])
    return {"c": True, "v": [[round(x, 2), round(y, 2)] for x, y in points], "i": ins, "o": outs}


NPTS = 24
_EMPTY = _bez([(-9999 + i * 0.01, -9999) for i in range(NPTS)], 0)


def blob(cx, cy, r, seed, rough=0.18, n=0, stretch=(1.0, 1.0), angle=0.0, spikes=0.0, spike_n=0):
    """A wobbly cel blob: polar noise round (cx, cy); `spikes` adds pointed lobes (flames, bursts)."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.283) for _ in range(4)]
    if not n:
        n = max(NPTS, spike_n * 8) if spikes else NPTS
    pts = []
    ca, sa = math.cos(angle), math.sin(angle)
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + rough * (0.6 * math.sin(2 * a + ph[0]) + 0.3 * math.sin(3 * a + ph[1]) + 0.2 * math.sin(5 * a + ph[2]))
        if spikes and spike_n:
            k += spikes * max(0.0, math.cos(spike_n * a + ph[3])) ** 6
        x = math.cos(a) * r * k * stretch[0]
        y = math.sin(a) * r * k * stretch[1]
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return pts


def star4(cx, cy, r, points=4, inner=0.22, angle=0.0):
    """A clean, symmetric star (anime shine): sharp tips, concave sides."""
    pts = []
    for i in range(points * 2):
        a = angle - math.pi / 2 + math.pi * i / points
        rad = r if i % 2 == 0 else r * inner
        pts.append((cx + math.cos(a) * rad, cy + math.sin(a) * rad))
    return Sharp(pts)


def flame(cx, base, w, h, seed, lean=0.0):
    """A flame tongue: round at the base, drawn to a flickering point at the top."""
    rnd = random.Random(seed)
    pts = []
    for i in range(NPTS):
        a = 2 * math.pi * i / NPTS - math.pi / 2  # start at the tip
        u = math.sin(a)  # -1 tip .. +1 bottom
        rad = (1 - (1 - u) / 2 * 0.95)
        x = math.cos(a) * w / 2 * rad ** 0.6
        y = (u * 0.5) * h * 0.55
        wob = rnd.uniform(-0.12, 0.12) * w * (1 - u) / 2
        tip = (1 - u) / 2
        pts.append((cx + x + wob + lean * tip * h * 0.4, base - h * 0.45 + y - tip * h * 0.25))
    return pts


class Cel:
    """Layers of flat tones, each a fixed number of outlines that change on twos (hold keys)."""

    def __init__(self, sticker: Sticker, tones: list[tuple[str, str]], slots: int):
        self.s = sticker
        self.tones = [(sticker.slot(sid, colour), colour) for sid, colour in tones]
        self.slots = slots
        self.frames = {k: [] for k in range(len(tones))}  # tone -> [(frame, [outlines])]

    def draw(self, frame: int, tone: int, outlines: list):
        self.frames[tone].append((frame, outlines[: self.slots]))

    def build(self):
        # The first tone is drawn at the back: add it first (layers are added bottom-up).
        for tone, (sid, colour) in enumerate(self.tones):
            keyed = self.frames[tone]
            if not keyed:
                continue
            paths = []
            for slot in range(self.slots):
                ks = []
                for frame, outs in keyed:
                    if slot < len(outs):
                        o = outs[slot]
                        shape = _bez(o, 0.0 if isinstance(o, Sharp) else 1.0)
                    else:
                        shape = _EMPTY
                    ks.append({"t": frame, "s": [shape], "h": 1})
                paths.append({"ty": "sh", "ks": {"a": 1, "k": ks} if len(ks) > 1 else static(ks[0]["s"][0])})
            self.s.layer(group(*paths, fill(colour, sid), tr=transform()), ks=layer_transform((0, 0)),
                         name=f"tono {tone + 1}")


def sticker(id, es, en, cat, frames, order, tags, loop=False, size=512, height=0, thumb=0.5):
    s = Sticker(id, es, en, "extremas-" + cat, frames=frames, order=order, tags=tags + ["extremas", "anime", "cartoon"],
                loop=loop, size=size, height=height, thumb=thumb if loop else 0.35)
    return s


def frames_of(total):
    return range(0, total, STEP)


# ================================================================== Fuego
def fuego_bucle() -> Sticker:
    s = sticker("ex-fuego-bucle", "Fuego en bucle", "Fire loop", "fuego", 48, 3001, ["fuego", "llamas", "loop"], loop=True)
    cel = Cel(s, [("borde", "#C2181B"), ("fuego", "#FF6A13"), ("centro", "#FFD23F")], 7)
    for f in frames_of(48):
        u = f / 48
        for tone, (scale, n) in enumerate([(1.0, 7), (0.72, 6), (0.42, 4)]):
            outs = []
            for k in range(n):
                ph = (u + k / n) % 1
                x = C + (k - (n - 1) / 2) * 52 * scale + 10 * math.sin(2 * math.pi * (u * 2 + k * 0.37))
                h = (150 + 140 * math.sin(math.pi * ph)) * scale
                outs.append(flame(x, 430, 110 * scale, h, seed=f * 13 + k * 7 + tone, lean=0.25 * math.sin(2 * math.pi * (u + k * 0.2))))
            outs.append(blob(C, 430, 170 * scale, seed=f + tone * 99, rough=0.1, stretch=(1, 0.35)))
            cel.draw(f, tone, outs)
    cel.build()
    return s


def fuego_estallido() -> Sticker:
    s = sticker("ex-fuego-estallido", "Estallido de fuego", "Fire burst", "fuego", 36, 3002, ["fuego", "explosión", "estallido"])
    cel = Cel(s, [("borde", "#B5121B"), ("fuego", "#FF7417"), ("centro", "#FFE45C")], 9)
    rnd = random.Random(4)
    tongues = [(rnd.uniform(0, 6.283), rnd.uniform(0.7, 1.15)) for _ in range(9)]
    for f in frames_of(36):
        u = f / 35
        grow = 1 - (1 - min(1, u / 0.25)) ** 3
        fade = max(0.0, 1 - max(0.0, u - 0.45) / 0.55)
        for tone, scale in enumerate([1.0, 0.7, 0.4]):
            outs = []
            for k, (a, l) in enumerate(tongues):
                d = 110 * grow * l * scale + 40 * u
                r = 70 * scale * fade * (0.8 + 0.4 * math.sin(f * 0.7 + k))
                if r < 3:
                    continue
                outs.append(blob(C + math.cos(a) * d, C + math.sin(a) * d - 30 * u, r, seed=f * 3 + k + tone * 50, rough=0.25,
                                 stretch=(1.0, 1.25), angle=a + math.pi / 2, spikes=0.35, spike_n=3))
            core = 120 * grow * scale * fade
            if core > 4:
                outs.insert(0, blob(C, C, core, seed=f + tone, rough=0.2, spikes=0.4, spike_n=5))
            cel.draw(f, tone, outs)
    cel.build()
    return s


def fuego_anillo() -> Sticker:
    s = sticker("ex-fuego-anillo", "Anillo de fuego", "Fire ring", "fuego", 48, 3003, ["fuego", "anillo", "círculo"], loop=True)
    cel = Cel(s, [("borde", "#C2181B"), ("fuego", "#FF6A13"), ("centro", "#FFD23F")], 12)
    for f in frames_of(48):
        u = f / 48
        for tone, scale in enumerate([1.0, 0.7, 0.42]):
            outs = []
            for k in range(12):
                a = 2 * math.pi * (k / 12 + u / 6)
                x, y = C + math.cos(a) * 140, C + math.sin(a) * 140
                h = (105 + 45 * math.sin(2 * math.pi * (u * 2 + k / 3))) * scale
                pts = flame(0, 0, 95 * scale, h, seed=f * 7 + k + tone * 31)
                ca, sa = math.cos(a + math.pi / 2), math.sin(a + math.pi / 2)
                outs.append([(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts])
            cel.draw(f, tone, outs)
    cel.build()
    return s


def fuego_suelo() -> Sticker:
    s = sticker("ex-fuego-suelo", "Llamarada del suelo", "Ground flare", "fuego", 40, 3004, ["fuego", "llamarada", "suelo"])
    cel = Cel(s, [("borde", "#B5121B"), ("fuego", "#FF7417"), ("centro", "#FFE45C")], 6)
    for f in frames_of(40):
        u = f / 39
        rise = 1 - (1 - min(1, u / 0.3)) ** 3
        die = max(0.0, 1 - max(0.0, u - 0.5) / 0.5)
        for tone, scale in enumerate([1.0, 0.7, 0.4]):
            outs = []
            for k in range(6):
                x = C + (k - 2.5) * 60
                h = 380 * rise * die * scale * (0.6 + 0.4 * math.sin(k * 1.7 + f * 0.4)) + 1
                if h < 8:
                    continue
                outs.append(flame(x, 470, 120 * scale, h, seed=f * 5 + k + tone * 11, lean=0.3 * math.sin(f * 0.3 + k)))
            cel.draw(f, tone, outs)
    cel.build()
    return s


# ================================================================== Explosiones
def explosion(id, es, en, order, size_k=1.0, frames=40, smoke=True, tags=None):
    s = sticker(id, es, en, "explosiones", frames, order, (tags or []) + ["explosión", "boom"])
    cel = Cel(s, [("humo", "#3B3340"), ("borde", "#C2181B"), ("fuego", "#FF7417"), ("centro", "#FFF0A3")], 10)
    rnd = random.Random(order)
    puffs = [(rnd.uniform(0, 6.283), rnd.uniform(0.55, 1.0), rnd.uniform(0.7, 1.2)) for _ in range(10)]
    for f in frames_of(frames):
        u = f / (frames - 1)
        pop = 1 - (1 - min(1, u / 0.18)) ** 3
        fire = max(0.0, 1 - max(0.0, u - 0.25) / 0.4)
        smk = max(0.0, 1 - max(0.0, u - 0.55) / 0.45)
        layers = [("humo", 1.15, smk if smoke else 0, 30 * u), ("borde", 1.0, fire, 0), ("fuego", 0.75, fire, 0),
                  ("centro", 0.45, fire * fire, 0)]
        for tone, (_, scale, alive, rise) in enumerate(layers):
            outs = []
            for k, (a, d, r) in enumerate(puffs):
                rad = 90 * r * scale * size_k * (0.35 + 0.65 * pop) * (0.2 + 0.8 * alive)
                if rad < 4 or alive <= 0:
                    continue
                dist = 120 * d * size_k * pop * (1 + 0.4 * u)
                outs.append(blob(C + math.cos(a) * dist, C + math.sin(a) * dist - rise * 3, rad, seed=f + k * 17 + tone,
                                 rough=0.22))
            core = 140 * scale * size_k * pop * alive
            if core > 5:
                outs.insert(0, blob(C, C - rise * 2, core, seed=f * 9 + tone, rough=0.2, spikes=0.3, spike_n=6))
            cel.draw(f, tone, outs)
    cel.build()
    return s


def explosion_hongo() -> Sticker:
    s = sticker("ex-explosion-hongo", "Explosión en hongo", "Mushroom blast", "explosiones", 50, 3104, ["explosión", "hongo", "nube"])
    cel = Cel(s, [("humo", "#3B3340"), ("fuego", "#FF7417"), ("centro", "#FFE45C")], 8)
    for f in frames_of(50):
        u = f / 49
        up = 1 - (1 - min(1, u / 0.45)) ** 3
        fade = max(0.0, 1 - max(0.0, u - 0.6) / 0.4)
        for tone, scale in enumerate([1.0, 0.75, 0.45]):
            outs = []
            cap_y = 400 - 250 * up
            for k in range(5):
                a = math.pi + k * math.pi / 4
                outs.append(blob(C + math.cos(a) * 90 * up, cap_y + math.sin(a) * 40 * up, (70 + 30 * up) * scale * fade + 1,
                                 seed=f + k * 5 + tone, rough=0.2))
            outs.append(blob(C, (cap_y + 470) / 2, 45 * scale * fade + 1, seed=f + 77 + tone, rough=0.15,
                             stretch=(0.55, max(0.3, (470 - cap_y) / 90))))
            outs.append(blob(C, 470, 120 * scale * up * fade + 1, seed=f + 88 + tone, rough=0.2, stretch=(1.4, 0.35)))
            cel.draw(f, tone, outs)
    cel.build()
    return s


# ================================================================== Humo
def humo_puff(id, es, en, order, frames=36, ground=False, poof=False, tags=None):
    s = sticker(id, es, en, "humo", frames, order, (tags or []) + ["humo", "nube"])
    cel = Cel(s, [("sombra", "#8C8A99"), ("humo", "#E6E4EE"), ("luz", "#FFFFFF")], 9)
    rnd = random.Random(order)
    pf = [(rnd.uniform(-0.3, 0.3) + (math.pi if ground and i % 2 else 0) if ground else rnd.uniform(0, 6.283),
           rnd.uniform(0.6, 1.0)) for i in range(9)]
    for f in frames_of(frames):
        u = f / (frames - 1)
        grow = 1 - (1 - min(1, u / 0.3)) ** 2
        fade = max(0.0, 1 - max(0.0, u - (0.3 if poof else 0.5)) / (0.7 if poof else 0.5))
        for tone, (scale, dy) in enumerate([(1.0, 0), (0.85, -10), (0.45, -30)]):
            outs = []
            for k, (a, d) in enumerate(pf):
                if ground:
                    x = C + (k - 4) * 26 * grow * (1 + 0.6 * u)
                    y = 440 - 40 * d * grow - 30 * u
                else:
                    x = C + math.cos(a) * 110 * d * grow
                    y = C + math.sin(a) * 90 * d * grow - 40 * u
                r = (60 + 30 * d) * scale * (0.5 + 0.5 * grow) * (0.25 + 0.75 * fade)
                if fade <= 0 or r < 3:
                    continue
                outs.append(blob(x, y + dy * scale, r, seed=f + k * 7 + tone, rough=0.15))
            cel.draw(f, tone, outs)
    cel.build()
    return s


def humo_columna() -> Sticker:
    s = sticker("ex-humo-columna", "Columna de humo", "Smoke column", "humo", 60, 3204, ["humo", "loop", "columna"], loop=True)
    cel = Cel(s, [("sombra", "#6E6B7B"), ("humo", "#CFCCDA"), ("luz", "#F4F3F8")], 7)
    for f in frames_of(60):
        u = f / 60
        for tone, scale in enumerate([1.0, 0.8, 0.45]):
            outs = []
            for k in range(7):
                ph = (u + k / 7) % 1
                y = 470 - 420 * ph
                x = C + 40 * math.sin(2 * math.pi * (ph * 1.3 + k * 0.1))
                r = (60 + 90 * ph) * scale * (1 - ph) ** 0.35
                if r > 3:
                    outs.append(blob(x, y, r, seed=f + k * 5 + tone, rough=0.15))
            cel.draw(f, tone, outs)
    cel.build()
    return s


# ================================================================== Energía
def ring_contour(cx, cy, r, w, seed, n=NPTS * 2, rough=0.08):
    """A ring is drawn as many small lobes round a circle (Lottie fills have no holes here)."""
    return blob(cx, cy, r, seed, rough=rough, n=n)


def energia_onda() -> Sticker:
    s = sticker("ex-energia-onda", "Onda de energía", "Energy shockwave", "energia", 30, 3301, ["energía", "onda", "impacto"])
    cel = Cel(s, [("borde", "#1B4BFF"), ("energia", "#3FD5FF"), ("centro", "#FFFFFF")], 16)
    for f in frames_of(30):
        u = f / 29
        r = 40 + 210 * (1 - (1 - u) ** 3)
        thick = 40 * (1 - u) + 4
        for tone, k in enumerate([1.0, 0.6, 0.3]):
            outs = []
            for i in range(16):
                a = 2 * math.pi * i / 16 + f * 0.05
                outs.append(blob(C + math.cos(a) * r, C + math.sin(a) * r, thick * k * (0.8 + 0.4 * math.sin(i * 1.9 + f)),
                                 seed=f + i + tone * 40, rough=0.3, stretch=(0.5, 1.8), angle=a))
            if u < 0.2:
                outs.insert(0, blob(C, C, 90 * (1 - u / 0.2) * k + 1, seed=f, rough=0.3, spikes=0.6, spike_n=4))
            cel.draw(f, tone, outs)
    cel.build()
    return s


def energia_carga() -> Sticker:
    s = sticker("ex-energia-carga", "Carga de energía", "Energy charge", "energia", 48, 3302, ["energía", "carga", "poder"], loop=True)
    cel = Cel(s, [("borde", "#7A1BFF"), ("energia", "#C15CFF"), ("centro", "#FFFFFF")], 12)
    rnd = random.Random(7)
    streaks = [(rnd.uniform(0, 6.283), rnd.uniform(0, 1)) for _ in range(10)]
    for f in frames_of(48):
        u = f / 48
        for tone, k in enumerate([1.0, 0.6, 0.35]):
            outs = [blob(C, C, (70 + 12 * math.sin(2 * math.pi * u * 4)) * k + 2, seed=f + tone, rough=0.25, spikes=0.3, spike_n=5)]
            for i, (a, ph) in enumerate(streaks):
                p = (u * 2 + ph) % 1
                d = 230 * (1 - p)
                outs.append(blob(C + math.cos(a) * d, C + math.sin(a) * d, 14 * k * (0.4 + p), seed=i + f + tone,
                                 rough=0.1, stretch=(3.5, 0.6), angle=a))
            cel.draw(f, tone, outs)
    cel.build()
    return s


def energia_aura() -> Sticker:
    s = sticker("ex-energia-aura", "Aura de poder", "Power aura", "energia", 36, 3303, ["energía", "aura", "anime"], loop=True)
    cel = Cel(s, [("borde", "#FF9F1C"), ("energia", "#FFE14D"), ("centro", "#FFFFF0")], 9)
    for f in frames_of(36):
        u = f / 36
        for tone, k in enumerate([1.0, 0.75, 0.5]):
            outs = []
            for i in range(9):
                x = C + (i - 4) * 34 * k
                h = (260 + 90 * math.sin(2 * math.pi * (u * 3 + i * 0.37))) * k
                outs.append(flame(x, 470, 70 * k, h, seed=f * 3 + i + tone * 13, lean=0.15 * math.sin(i + f * 0.5)))
            cel.draw(f, tone, outs)
    cel.build()
    return s


def energia_corte() -> Sticker:
    s = sticker("ex-energia-corte", "Corte de energía", "Energy slash", "energia", 24, 3304, ["energía", "corte", "espada"])
    cel = Cel(s, [("borde", "#1B4BFF"), ("energia", "#5CE1FF"), ("centro", "#FFFFFF")], 3)
    for f in frames_of(24):
        u = f / 23
        sweep = min(1.0, u / 0.35)
        fade = max(0.0, 1 - max(0.0, u - 0.35) / 0.65)
        for tone, k in enumerate([1.0, 0.6, 0.25]):
            pts_out, pts_in = [], []
            n = NPTS // 2
            a0, a1 = math.radians(200), math.radians(200 + 160 * sweep)
            for i in range(n):
                a = a0 + (a1 - a0) * i / (n - 1)
                taper = math.sin(math.pi * i / (n - 1))
                w = 34 * k * taper * fade + 0.5
                pts_out.append((C + math.cos(a) * (190 + w), C + 40 + math.sin(a) * (150 + w)))
                pts_in.append((C + math.cos(a) * (190 - w), C + 40 + math.sin(a) * (150 - w)))
            cel.draw(f, tone, [pts_out + pts_in[::-1]] if fade > 0 else [])
    cel.build()
    return s


def energia_orbe() -> Sticker:
    s = sticker("ex-energia-orbe", "Orbe de energía", "Energy orb", "energia", 40, 3305, ["energía", "orbe", "bola"], loop=True)
    cel = Cel(s, [("borde", "#0E8A5F"), ("energia", "#2EE6A8"), ("centro", "#E8FFF6")], 6)
    for f in frames_of(40):
        u = f / 40
        for tone, k in enumerate([1.0, 0.72, 0.38]):
            outs = [blob(C, C, (120 + 10 * math.sin(2 * math.pi * u * 2)) * k, seed=f + tone, rough=0.12, spikes=0.25, spike_n=7)]
            for i in range(4):
                a = 2 * math.pi * (u + i / 4)
                outs.append(blob(C + math.cos(a) * 170, C + math.sin(a) * 60, 16 * k, seed=f + i, rough=0.2))
            cel.draw(f, tone, outs)
    cel.build()
    return s


# ================================================================== Electricidad
def bolt_points(x0, y0, x1, y1, seed, segs=7, jag=40):
    rnd = random.Random(seed)
    pts = [(x0, y0)]
    for i in range(1, segs):
        t = i / segs
        pts.append((x0 + (x1 - x0) * t + rnd.uniform(-jag, jag), y0 + (y1 - y0) * t + rnd.uniform(-jag * 0.3, jag * 0.3)))
    pts.append((x1, y1))
    return pts


def bolt_shape(pts, w):
    """A zigzag bolt as a thin closed outline (both sides), sharp."""
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        nx, ny = pts[min(i + 1, len(pts) - 1)]
        px, py = pts[max(i - 1, 0)]
        dx, dy = nx - px, ny - py
        l = math.hypot(dx, dy) or 1
        ww = w * (1 - i / (len(pts) - 1) * 0.8)
        left.append((x - dy / l * ww, y + dx / l * ww))
        right.append((x + dy / l * ww, y - dx / l * ww))
    return Sharp(left + right[::-1])


def rayo() -> Sticker:
    s = sticker("ex-rayo", "Rayo", "Lightning strike", "electricidad", 24, 3401, ["rayo", "electricidad", "tormenta"])
    cel = Cel(s, [("borde", "#3B2BFF"), ("rayo", "#8FE8FF"), ("centro", "#FFFFFF")], 4)
    for f in frames_of(24):
        u = f / 23
        on = u < 0.55 and (f // 2) % 3 != 2
        for tone, k in enumerate([1.0, 0.55, 0.22]):
            outs = []
            if on:
                main = bolt_points(C + 30, 20, C - 20, 470, seed=f // 4)
                outs.append(bolt_shape(main[:7], 26 * k))
                outs.append(bolt_shape(bolt_points(*main[3], main[3][0] + 120, main[3][1] + 120, seed=f // 4 + 9, segs=6, jag=25)[:7], 12 * k))
            if u < 0.6:
                outs.append(blob(C - 20, 470, 60 * k * (1 - u / 0.6) + 1, seed=f, rough=0.3, spikes=0.6, spike_n=5, stretch=(1.6, 0.6)))
            cel.draw(f, tone, outs)
    cel.build()
    return s


def chispazo() -> Sticker:
    s = sticker("ex-chispazo", "Chispazo eléctrico", "Electric crackle", "electricidad", 36, 3402, ["electricidad", "chispa", "loop"], loop=True)
    cel = Cel(s, [("borde", "#3B2BFF"), ("rayo", "#8FE8FF"), ("centro", "#FFFFFF")], 6)
    for f in frames_of(36):
        for tone, k in enumerate([1.0, 0.5, 0.2]):
            outs = []
            rnd = random.Random(f // 2)
            for i in range(5):
                a = rnd.uniform(0, 6.283)
                r = rnd.uniform(90, 200)
                outs.append(bolt_shape(bolt_points(C, C, C + math.cos(a) * r, C + math.sin(a) * r, seed=f * 7 + i, segs=6, jag=22)[:7], 10 * k))
            outs.append(blob(C, C, 40 * k, seed=f, rough=0.35, spikes=0.5, spike_n=6))
            cel.draw(f, tone, outs)
    cel.build()
    return s


def anillo_electrico() -> Sticker:
    s = sticker("ex-anillo-electrico", "Anillo eléctrico", "Electric ring", "electricidad", 36, 3403, ["electricidad", "anillo"], loop=True)
    cel = Cel(s, [("borde", "#3B2BFF"), ("rayo", "#8FE8FF"), ("centro", "#FFFFFF")], 10)
    for f in frames_of(36):
        for tone, k in enumerate([1.0, 0.5, 0.2]):
            outs = []
            for i in range(10):
                a0 = 2 * math.pi * i / 10 + f * 0.04
                a1 = a0 + 2 * math.pi / 10
                p0 = (C + math.cos(a0) * 180, C + math.sin(a0) * 180)
                p1 = (C + math.cos(a1) * 180, C + math.sin(a1) * 180)
                outs.append(bolt_shape(bolt_points(*p0, *p1, seed=f * 3 + i, segs=6, jag=16)[:7], 9 * k))
            cel.draw(f, tone, outs)
    cel.build()
    return s


# ================================================================== Chispas
def chispas_estallido() -> Sticker:
    s = sticker("ex-chispas-estallido", "Estallido de chispas", "Spark burst", "chispas", 30, 3501, ["chispas", "estallido", "impacto"])
    cel = Cel(s, [("borde", "#FF6A13"), ("chispa", "#FFD23F"), ("centro", "#FFFFFF")], 14)
    rnd = random.Random(11)
    sp = [(rnd.uniform(0, 6.283), rnd.uniform(0.5, 1.0)) for _ in range(14)]
    for f in frames_of(30):
        u = f / 29
        for tone, k in enumerate([1.0, 0.6, 0.3]):
            outs = []
            for i, (a, v) in enumerate(sp):
                d = 230 * v * (1 - (1 - u) ** 2)
                y = C + math.sin(a) * d + 120 * u * u
                ln = 30 * (1 - u) * v + 2
                outs.append(blob(C + math.cos(a) * d, y, 10 * k * (1 - u) + 1, seed=i, rough=0.0, stretch=(ln / 10 + 1, 0.6),
                                 angle=a))
            if u < 0.25:
                outs.insert(0, blob(C, C, 70 * (1 - u / 0.25) * k + 1, seed=f, rough=0.3, spikes=0.8, spike_n=4))
            cel.draw(f, tone, outs)
    cel.build()
    return s


def destello_estrella() -> Sticker:
    s = sticker("ex-destello-estrella", "Destello", "Twinkle", "chispas", 36, 3502, ["brillo", "destello", "estrella"], loop=True)
    cel = Cel(s, [("borde", "#FFD23F"), ("centro", "#FFFFFF")], 5)
    rnd = random.Random(3)
    stars = [(rnd.uniform(80, 432), rnd.uniform(80, 432), rnd.uniform(0, 1), rnd.uniform(40, 90)) for _ in range(5)]
    for f in frames_of(36):
        u = f / 36
        for tone, k in enumerate([1.0, 0.45]):
            outs = []
            for i, (x, y, ph, sz) in enumerate(stars):
                g = max(0.0, math.sin(math.pi * ((u + ph) % 1)))
                outs.append(star4(x, y, sz * g * k + 0.5, inner=0.2 + 0.1 * tone))
            cel.draw(f, tone, outs)
    cel.build()
    return s


def impacto() -> Sticker:
    s = sticker("ex-impacto", "Impacto", "Impact", "chispas", 20, 3503, ["impacto", "golpe", "pow"])
    cel = Cel(s, [("borde", "#111111"), ("impacto", "#FFD23F"), ("centro", "#FFFFFF")], 2)
    for f in frames_of(20):
        u = f / 19
        g = (1 - (1 - min(1, u / 0.2)) ** 3) * max(0.0, 1 - max(0.0, u - 0.5) / 0.5)
        for tone, k in enumerate([1.05, 0.95, 0.55]):
            cel.draw(f, tone, [blob(C, C, 170 * g * k + 0.5, seed=f // 4, rough=0.08, spikes=0.9, spike_n=9)])
    cel.build()
    return s


# ================================================================== Líquidos
def salpicadura() -> Sticker:
    s = sticker("ex-salpicadura", "Salpicadura", "Splash", "liquidos", 34, 3601, ["agua", "salpicadura", "líquido"])
    cel = Cel(s, [("borde", "#0B5ED7"), ("liquido", "#2EA8FF"), ("brillo", "#CFF0FF")], 12)
    rnd = random.Random(21)
    drops = [(rnd.uniform(-2.6, -0.5), rnd.uniform(0.5, 1.0)) for _ in range(10)]
    for f in frames_of(34):
        u = f / 33
        for tone, k in enumerate([1.0, 0.78, 0.35]):
            outs = []
            crown = 1 - (1 - min(1, u / 0.3)) ** 3
            fade = max(0.0, 1 - max(0.0, u - 0.35) / 0.65)
            outs.append(blob(C, 430, 150 * crown * k * (0.4 + 0.6 * fade) + 1, seed=f + tone, rough=0.15, stretch=(1.4, 0.35),
                             spikes=0.6 * fade, spike_n=7))
            for i, (a, v) in enumerate(drops):
                d = 260 * v * u
                x = C + math.cos(a) * d
                y = 420 + math.sin(a) * d + 380 * u * u
                r = 22 * v * k * (1 - u * 0.6)
                if y < 520:
                    outs.append(blob(x, y, r + 0.5, seed=i, rough=0.1, stretch=(0.8, 1.3), angle=a + math.pi / 2))
            cel.draw(f, tone, outs)
    cel.build()
    return s


def goteo_bucle() -> Sticker:
    s = sticker("ex-goteo", "Goteo", "Drip loop", "liquidos", 48, 3602, ["gota", "goteo", "loop"], loop=True)
    cel = Cel(s, [("borde", "#5C1BB5"), ("liquido", "#A64DFF"), ("brillo", "#E9D6FF")], 6)
    for f in frames_of(48):
        u = f / 48
        for tone, k in enumerate([1.0, 0.75, 0.3]):
            outs = [blob(C, 30, 200 * k, seed=tone, rough=0.05, stretch=(1.3, 0.35))]
            for i, x in enumerate([C - 120, C, C + 110]):
                ph = (u + i * 0.33) % 1
                if ph < 0.6:
                    ln = 60 + 200 * ph / 0.6
                    outs.append(blob(x, 60 + ln / 2, 26 * k, seed=i + f, rough=0.06, stretch=(1, ln / 52)))
                else:
                    y = 260 + 600 * (ph - 0.6) ** 2 / 0.16 * 0.4
                    outs.append(blob(x, 60 + 40, 22 * k, seed=i, rough=0.05, stretch=(1, 1.6)))
                    outs.append(blob(x, y, 24 * k, seed=i + 3, rough=0.05, stretch=(0.85, 1.25)))
            cel.draw(f, tone, outs)
    cel.build()
    return s


def mancha_estallido() -> Sticker:
    s = sticker("ex-mancha", "Mancha líquida", "Liquid blob burst", "liquidos", 36, 3603, ["mancha", "líquido", "pintura"])
    cel = Cel(s, [("borde", "#C2185B"), ("liquido", "#FF4D8D"), ("brillo", "#FFD6E6")], 10)
    rnd = random.Random(5)
    arms = [(rnd.uniform(0, 6.283), rnd.uniform(0.6, 1.1)) for _ in range(8)]
    for f in frames_of(36):
        u = f / 35
        g = 1 - (1 - min(1, u / 0.25)) ** 3
        for tone, k in enumerate([1.0, 0.8, 0.3]):
            outs = [blob(C, C, 110 * g * k + 1, seed=f // 6 + tone, rough=0.2, spikes=0.5, spike_n=6)]
            for i, (a, v) in enumerate(arms):
                d = 170 * v * g
                outs.append(blob(C + math.cos(a) * d, C + math.sin(a) * d, 26 * v * g * k + 0.5, seed=i, rough=0.15))
            cel.draw(f, tone, outs)
    cel.build()
    return s


# ================================================================== Líneas
def lineas_velocidad() -> Sticker:
    s = sticker("ex-lineas-velocidad", "Líneas de velocidad", "Speed lines", "lineas", 24, 3701, ["líneas", "velocidad", "anime"],
                loop=True, size=1920, height=1080)
    cel = Cel(s, [("lineas", "#FFFFFF")], 22)
    for f in frames_of(24):
        rnd = random.Random(f // 2)
        outs = []
        for i in range(22):
            a = rnd.uniform(0, 6.283)
            r0 = rnd.uniform(380, 520)
            w = rnd.uniform(6, 18)
            x0, y0 = 960 + math.cos(a) * r0, 540 + math.sin(a) * r0 * 0.75
            x1, y1 = 960 + math.cos(a) * 1300, 540 + math.sin(a) * 1000
            nx, ny = -math.sin(a), math.cos(a)
            pts = [(x0, y0)] * 0 + [(x0 + (x1 - x0) * t + nx * w * t * (1 if j else -1), y0 + (y1 - y0) * t + ny * w * t * (1 if j else -1))
                                    for j in (0, 1) for t in ([0.0, 0.15, 0.35, 0.6, 0.8, 1.0, 1.0] if j == 0 else [1.0, 1.0, 0.8, 0.6, 0.35, 0.15, 0.0])]
            outs.append(Sharp(pts))
        cel.draw(f, 0, outs)
    cel.build()
    return s


def lineas_horizontales() -> Sticker:
    s = sticker("ex-lineas-horizontales", "Líneas de carrera", "Dash lines", "lineas", 20, 3702, ["líneas", "velocidad", "carrera"],
                loop=True, size=1920, height=1080)
    cel = Cel(s, [("lineas", "#FFFFFF")], 16)
    for f in frames_of(20):
        rnd = random.Random(1000 + f // 2)
        outs = []
        for i in range(16):
            y = rnd.uniform(60, 1020)
            x = rnd.uniform(-200, 1900)
            ln = rnd.uniform(300, 900)
            w = rnd.uniform(3, 10)
            outs.append(blob(x + ln / 2, y, w, seed=i, rough=0.0, stretch=(ln / (2 * w), 1)))
        cel.draw(f, 0, outs)
    cel.build()
    return s


def latigazo() -> Sticker:
    s = sticker("ex-latigazo", "Latigazo", "Swoosh", "lineas", 20, 3703, ["swoosh", "movimiento", "estela"])
    cel = Cel(s, [("borde", "#FFFFFF")], 3)
    for f in frames_of(20):
        u = f / 19
        head = min(1.0, u / 0.5)
        tail = max(0.0, (u - 0.25) / 0.75)
        outs = []
        for j, off in enumerate([0, 26, 52]):
            n = NPTS // 2
            top, bot = [], []
            for i in range(n):
                t = tail + (head - tail) * i / (n - 1)
                a = math.radians(210 - 150 * t)
                w = 10 * math.sin(math.pi * i / (n - 1)) * (1 - j * 0.25) + 0.5
                r = 200 - off
                top.append((C + math.cos(a) * (r + w), C + 60 + math.sin(a) * (r + w)))
                bot.append((C + math.cos(a) * (r - w), C + 60 + math.sin(a) * (r - w)))
            if head - tail > 0.02:
                outs.append(top + bot[::-1])
        cel.draw(f, 0, outs)
    cel.build()
    return s


def sorpresa_manga() -> Sticker:
    s = sticker("ex-sorpresa", "Líneas de sorpresa", "Surprise lines", "lineas", 30, 3704, ["sorpresa", "manga", "énfasis"], loop=True)
    cel = Cel(s, [("lineas", "#FFFFFF")], 8)
    for f in frames_of(30):
        g = 1 + 0.12 * math.sin(2 * math.pi * f / 30 * 2)
        outs = []
        for i in range(8):
            a = -math.pi / 2 + (i - 3.5) * 0.32
            r0, r1 = 150 * g, 240 * g
            x0, y0 = C + math.cos(a) * r0, C + 40 + math.sin(a) * r0
            x1, y1 = C + math.cos(a) * r1, C + 40 + math.sin(a) * r1
            outs.append(blob((x0 + x1) / 2, (y0 + y1) / 2, 9, seed=i, rough=0.0, stretch=((r1 - r0) / 18, 1), angle=a))
        cel.draw(f, 0, outs)
    cel.build()
    return s


# ================================================================== Destellos
def flash_impacto() -> Sticker:
    s = sticker("ex-flash", "Flash de impacto", "Impact flash", "destellos", 16, 3801, ["flash", "luz", "impacto"])
    cel = Cel(s, [("luz", "#FFF4C2"), ("centro", "#FFFFFF")], 3)
    for f in frames_of(16):
        u = f / 15
        g = (1 - (1 - min(1, u / 0.15)) ** 3) * max(0.0, 1 - u)
        for tone, k in enumerate([1.0, 0.5]):
            cel.draw(f, tone, [star4(C, C, 230 * g * k + 0.5, inner=0.16),
                               star4(C, C, 140 * g * k + 0.5, inner=0.2, angle=math.pi / 4),
                               blob(C, C, 70 * g * k + 0.5, seed=2, rough=0.1)])
    cel.build()
    return s


def brillo_anime() -> Sticker:
    s = sticker("ex-brillo-anime", "Brillo anime", "Anime shine", "destellos", 30, 3802, ["brillo", "anime", "estrella"], loop=True)
    cel = Cel(s, [("luz", "#FFFFFF")], 3)
    for f in frames_of(30):
        u = f / 30
        g = max(0.0, math.sin(math.pi * u)) ** 0.5
        cel.draw(f, 0, [star4(C, C, 210 * g + 0.5, inner=0.12, angle=u * 0.5),
                        star4(C, C, 110 * g + 0.5, inner=0.16, angle=math.pi / 4 + u * 0.5)])
    cel.build()
    return s


# ================================================================== Transiciones (pantalla completa)
def transicion(id, es, en, order, tones, kind):
    """Full frame: covers the picture by the middle and clears it by the end (cut there)."""
    s = sticker(id, es, en, "transiciones", 36, order, ["transición", kind], size=1920, height=1080)
    s.thumb = 0.45
    cel = Cel(s, tones, 40)
    W, H = 1920, 1080
    for f in frames_of(36):
        u = f / 35
        cover = 1 - (1 - min(1, u / 0.45)) ** 3
        clear = max(0.0, (u - 0.55) / 0.45) ** 1.5
        for tone in range(len(tones)):
            lag = tone * 0.06
            c = max(0.0, cover - lag)
            outs = []
            if kind == "liquido":
                # A sheet falling from the top with a wavy, dripping edge, then draining off the bottom.
                edge = -200 + (H + 500) * c
                top = -200 + (H + 500) * clear
                pts = [(-50, top)]
                for i in range(33):
                    x = -50 + (W + 100) * i / 32
                    drip = 70 * max(0.0, math.sin(i * 1.7 + tone)) ** 3
                    pts.append((x, edge + 35 * math.sin(i * 0.9 + f * 0.35) + drip))
                pts.append((W + 50, top))
                outs.append(Sharp(pts))
            elif kind == "fuego":
                # A solid body of fire rising from the bottom, its top edge all flames.
                level = H + 300 - (H + 700) * c + (H + 900) * clear
                outs.append(Sharp([(-50, H + 400), (-50, level), (W + 50, level), (W + 50, H + 400)]))
                for i in range(16):
                    x = -60 + (W + 120) * i / 15
                    h = 300 + 120 * math.sin(i * 1.3 + f * 0.6)
                    outs.append(flame(x, level + 40, 210, h, seed=f + i * 5 + tone, lean=0.2 * math.sin(i + f * 0.3)))
            else:  # humo
                # Puffs on a grid, swelling from the middle outwards, then shrinking away the same way.
                for gx in range(7):
                    for gy in range(4):
                        x = -60 + (W + 120) * gx / 6
                        y = -40 + (H + 80) * gy / 3
                        d = math.hypot((x - W / 2) / W, (y - H / 2) / H)
                        grow = min(1.0, max(0.0, c * 1.8 - d))
                        shrink = min(1.0, max(0.0, clear * 1.8 - d))
                        r = 300 * grow * (1 - shrink)
                        if r > 2:
                            outs.append(blob(x, y, r * (1 - tone * 0.12), seed=f + gx * 7 + gy + tone, rough=0.16))
            cel.draw(f, tone, outs)
    cel.build()
    return s


STICKERS = [
    fuego_bucle, fuego_estallido, fuego_anillo, fuego_suelo,
    lambda: explosion("ex-explosion", "Explosión cartoon", "Cartoon explosion", 3101),
    lambda: explosion("ex-explosion-grande", "Gran explosión", "Big boom", 3102, size_k=1.25, frames=48),
    lambda: explosion("ex-explosion-pop", "Mini explosión", "Small pop", 3103, size_k=0.7, frames=26, smoke=False),
    explosion_hongo,
    lambda: humo_puff("ex-humo-puff", "Bocanada de humo", "Smoke puff", 3201),
    lambda: humo_puff("ex-humo-polvo", "Nube de polvo", "Dust cloud", 3202, ground=True, tags=["polvo", "aterrizaje"]),
    lambda: humo_puff("ex-humo-desaparecer", "Desaparecer (poof)", "Poof", 3203, frames=28, poof=True, tags=["poof", "desaparecer"]),
    humo_columna,
    energia_onda, energia_carga, energia_aura, energia_corte, energia_orbe,
    rayo, chispazo, anillo_electrico,
    chispas_estallido, destello_estrella, impacto,
    salpicadura, goteo_bucle, mancha_estallido,
    lineas_velocidad, lineas_horizontales, latigazo, sorpresa_manga,
    flash_impacto, brillo_anime,
    lambda: transicion("ex-transicion-fuego", "Transición de fuego", "Fire transition", 3901,
                       [("borde", "#C2181B"), ("fuego", "#FF6A13"), ("centro", "#FFD23F")], "fuego"),
    lambda: transicion("ex-transicion-humo", "Transición de humo", "Smoke transition", 3902,
                       [("sombra", "#6E6B7B"), ("humo", "#CFCCDA"), ("luz", "#F4F3F8")], "humo"),
    lambda: transicion("ex-transicion-liquida", "Transición líquida", "Liquid transition", 3903,
                       [("borde", "#0B5ED7"), ("liquido", "#2EA8FF")], "liquido"),
]
