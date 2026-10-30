"""Animaciones Extremas · Energía (0.26), on the field engine of rtfx2_fire.py.

Energy is drawn like fire but clean: the same field (a blue rim, a cyan edge, a white heart, the rim
blurred behind as the glow) with the licking and boiling of the edges turned almost off, so rings,
stars, beams and blades keep crisp, smooth outlines. Studied against RTFX's energy previews frame by
frame (see feedback: study before generating).
"""

from __future__ import annotations

import math

import numpy as np

from rtfx2_fire import Mass, looped, ribbon, traced
from rtfx_field import render
from rtfx_engine import new

# A thin coloured rim, the white reaching almost to it, and a strong glow round it (RTFX's energy).
TONES = [("azul", "#3a6bff"), ("cian", "#8fd9ff", 0.2), ("blanco", "#f4fbff", 0.34)]
CYAN = [("cian", "#18b4ff"), ("celeste", "#7deaff", 0.2), ("blanco", "#f2fdff", 0.34)]
HALO = [("#1d45ff", 70, 90), ("#4f8dff", 22, 95)]
HALO_CYAN = [("#0097ff", 70, 90), ("#3fd2ff", 22, 95)]
GLOW = 30


def ring(x, y, r, w, heart=0.95):
    """A ring of radius r and width w, as lobes: a thick one is a puff hollowed from its centre, a
    thin one a band of small puffs round the circle (a hollowed puff loses a thin rim altogether)."""
    if w > r * 0.35:
        k = max(0.0, (1 - w / max(r, 1e-3)) - 0.3) / 0.9
        return [(x, y, r, 1.0, 1.0, 0.0, heart, k, 0.0, 0.0, True) if k > 0 else (x, y, r, 1.0, 1.0, 0.0, heart)]
    return ribbon(lambda u: (x + math.cos(2 * math.pi * u) * r, y + math.sin(2 * math.pi * u) * r), lambda u: w / 2,
                  max(24, int(4 * math.pi * r / max(w, 0.5))), lambda u: heart)


def hit_rings(W, H, seed, size=1.0):
    """An energy hit of rings (RTFX's «Energy Hit Radial»): a white flash bursts into several rings,
    a big one and small ones off centre, that widen and thin to blue lines and vanish."""
    m = Mass(W, H, seed, rough=0.12)
    rnd = np.random.default_rng(seed)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2
    # (dx, dy, final radius, delay)
    rings = [(0, 0, 52, 0.0), (-6, 6, 36, 0.03), (-36, -34, 13, 0.07), (-10, 40, 10, 0.09), (30, -6, 20, 0.05),
             (rnd.uniform(-40, 40), rnd.uniform(-40, 40), 6, 0.12)]

    def field(t):
        lobes = []
        flash = max(0.0, 1 - t / 0.12)
        if flash > 0:
            lobes.append((cx, cy, (10 + 16 * (1 - flash)) * k, 1.0, 1.0, 0.0, 0.9))
        for dx, dy, R, delay in rings:
            a = t - delay
            if a <= 0:
                continue
            e = 1 - (1 - min(1.0, a / 0.45)) ** 2.5
            r = R * k * (0.35 + 0.65 * e) * (1 + 0.15 * max(0.0, a - 0.45))
            w = (r * (0.5 - 0.44 * min(1.0, a / 0.4)) + 3.0 * k) * max(0.0, 1 - max(0.0, a - 0.45) / 0.3)
            if w > 0.5:
                lobes.extend(ring(cx + dx * k * e, cy + dy * k * e, r, w, 0.97 - 0.4 * min(1.0, max(0.0, a - 0.3) / 0.4)))
        return m.field(lobes, t, "radial", (cx, cy), 60 * k, 9.0, 1.0, crown=0.0, life=0.0)

    return field


def make_hit_rings():
    s = new("ex-energia-golpe-anillos", "Energía · Golpe de anillos", "Energy · Ring hit", "energia", 16, 7000,
            ["energía", "energy", "golpe", "hit", "anillos", "rings", "impacto"], size=512, thumb=0.25)
    s.fps = 24
    return render(s, hit_rings(512, 512, 3, size=1.4), tones=TONES, halo=HALO)


def star_hit(W, H, seed, size=1.0):
    """An energy star hit (RTFX's «Hit Star Radial»): a white flash opens into a four-pointed glint
    with a ring round it; the glint grows and turns while its points thin to blue needles."""
    m = Mass(W, H, seed, rough=0.08)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2

    def field(t):
        lobes = []
        e = 1 - (1 - min(1.0, t / 0.22)) ** 2
        fade = max(0.0, 1 - max(0.0, t - 0.45) / 0.35)
        ball = max(0.0, 1 - max(0.0, t - 0.1) / 0.18)
        if ball > 0:
            lobes.append((cx, cy, (6 + 14 * min(1.0, t / 0.08)) * k * ball ** 0.5, 1.0, 1.0, 0.0, 0.9))
        if t > 0.04:
            turn = 0.35 * min(1.0, t / 0.6) + 0.05
            L = (14 + 60 * e) * k
            W0 = (5 + 7 * e) * k * (1 - 0.65 * min(1.0, max(0.0, t - 0.2) / 0.45)) * fade
            # Four tapering arms: a star with hollow sides, the long pair a little longer.
            for j in range(4):
                a = turn + j * math.pi / 2
                ln = L * (1.0 if j % 2 == 0 else 0.82)
                lobes += ribbon(lambda sv, a=a, ln=ln: (cx + math.cos(a) * ln * sv, cy + math.sin(a) * ln * sv),
                                lambda sv: W0 * (1 - sv) ** 1.4 + 0.7 * k * fade, 26, lambda sv: 0.95 * fade)
            # The ring round it, gone by the time the points are needles.
            ra = max(0.0, 1 - max(0.0, t - 0.3) / 0.4)
            if ra > 0:
                r = (12 + 30 * e) * k
                lobes.extend(ring(cx, cy, r, (2.0 + 3.0 * ra) * k * ra, 0.9))
        return m.field(lobes, t, "radial", (cx, cy), 60 * k, 9.0, 1.0, crown=0.0, life=0.0)

    return field


def make_star_hit():
    s = new("ex-energia-golpe-estrella", "Energía · Golpe de estrella", "Energy · Star hit", "energia", 16, 7001,
            ["energía", "energy", "golpe", "hit", "estrella", "star", "brillo", "glint"], size=512, thumb=0.3)
    s.fps = 24
    return render(s, star_hit(512, 512, 5, size=1.3), tones=TONES, halo=HALO)


def ray_up(W, H, seed, size=1.0):
    """An energy ray going up (RTFX's «Energy Ray Up»): a thin line shoots up and swells into a beam
    with a flare licking at its foot, holds, then narrows and breaks into dashes that fade upward."""
    m = Mass(W, H, seed, rough=0.15)
    k = size * m.gw / 256
    cx, base = m.gw / 2, m.gh * 0.9
    top = m.gh * 0.08

    def field(t):
        lobes = []
        grow = min(1.0, t / 0.2)
        L = (base - top) * (0.35 + 0.65 * grow)
        w = (2.5 + 8 * min(1.0, max(0.0, t - 0.1) / 0.15)) * (1 - 0.6 * min(1.0, max(0.0, t - 0.6) / 0.2)) * k
        end = max(0.0, (t - 0.75) / 0.35)
        if end < 1:
            # The beam, cut into dashes as it ends: the gaps open from the top down.
            def width(sv):
                if end <= 0:
                    return w
                seg = (sv * 11) % 1.0
                gap = min(1.0, end * 2.2 - (1 - sv) * 0.8)
                return w if seg > gap else 0.0
            lobes += ribbon(lambda sv: (cx, base - L * sv), width, 70, lambda sv: 0.55)
        flare = min(1.0, max(0.0, t - 0.08) / 0.12) * max(0.0, 1 - max(0.0, t - 0.55) / 0.2)
        if flare > 0:
            for dx, h in ((-7, 16), (0, 24), (7, 14)):
                lick = math.sin(t * 30 + dx) * 2 * k
                lobes.append((cx + dx * k * flare + lick, base - h * k * flare * 0.55, (6 + h * 0.4) * k * flare, 0.55, 1.0,
                              0.0, 0.8))
        return m.field(lobes, t, "up", (cx, base), base - top, 9.0, 1.0, crown=0.0, life=0.0)

    return field


def make_ray_up():
    s = new("ex-energia-rayo-arriba", "Energía · Rayo hacia arriba", "Energy · Ray up", "energia", 30, 7002,
            ["energía", "energy", "rayo", "ray", "haz", "beam", "láser", "laser"], size=512, thumb=0.45)
    s.fps = 24
    return render(s, ray_up(512, 512, 7, size=1.0), tones=CYAN, halo=HALO_CYAN)


def slash(W, H, seed, size=1.0):
    """An energy slash (RTFX's «Energy Slash Right»): a crescent blade of light sweeps across in an
    instant, then crumbles into blue bits from the back while its tip runs on."""
    m = Mass(W, H, seed, rough=0.25)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2 + 190 * k
    R = 200 * k

    def arc(u):
        a = -math.pi / 2 - 0.45 + 0.9 * u
        return cx + math.cos(a) * R, cy + math.sin(a) * R, a + math.pi / 2

    def field(t):
        rnd = np.random.default_rng(seed + int(round(t * 24)) // 2)
        head = 5.0 * t + 0.4
        lobes = traced(arc, head, t, k, width=8.0, life=2.3, lick=0.0, rnd=rnd, end=1.0, fade=0.9, hot=0.95,
                       thick=lambda u: 0.25 + 1.0 * math.sin(math.pi * min(1.0, u * 1.1)))
        return m.field(lobes, t, "radial", (cx, cy), R, 9.0, 1.0, crown=0.0, life=0.0)

    return field


def make_slash():
    s = new("ex-energia-corte-derecha", "Energía · Corte a la derecha", "Energy · Slash right", "energia", 18, 7003,
            ["energía", "energy", "corte", "slash", "espada", "sword"], size=512, thumb=0.1)
    s.fps = 24
    return render(s, slash(512, 512, 9, size=1.2), tones=TONES, halo=HALO)


def orb_shot(W, H, seed, size=1.0):
    """An energy projectile, looping (RTFX's «Energy Projectile Right Loop»): a blunt-nosed drop of
    light flying right, its back tapering into licks that flicker on every second frame, with jagged
    white inside and specks of light left in its wake."""
    m = Mass(W, H, seed, rough=0.9)
    k = size * m.gw / 256
    cx, cy = m.gw / 2 + 20 * k, m.gh / 2

    def field(t):
        n = int(round(t * 24)) // 2
        rnd = np.random.default_rng(seed * 1000 + n)
        sc = rnd.uniform(0.85, 1.1)
        lobes = [(cx, cy, 22 * k * sc, 1.0, 1.0, 0.0, 0.62)]  # the nose
        for j in range(6):  # licks fanning back from the nose to points, each its own length
            v = (j - 2.5) / 2.5
            L = (30 + 22 * (1 - abs(v))) * k * rnd.uniform(0.8, 1.2) * sc
            ang = math.pi + v * 0.32 + rnd.uniform(-0.06, 0.06)
            lobes.append((cx + math.cos(ang) * L * 0.75, cy + math.sin(ang) * L * 0.75, L, 1.0,
                          (0.2 + 0.08 * (1 - abs(v))) * rnd.uniform(0.85, 1.15), ang, 0.62))
        for _ in range(5):  # the wake
            lobes.append((cx - rnd.uniform(70, 110) * k, cy + rnd.uniform(-10, 10) * k, rnd.uniform(2, 3.5) * k, 1.0,
                          1.0, 0.0, 0.9))
        return m.field(lobes, n * 0.37, math.pi, (cx + 25 * k, cy), 120 * k, 99.0, 1.0, crown=0.0, life=0.0)

    return field


def make_projectile():
    s = new("ex-energia-proyectil-derecha", "Energía · Proyectil a la derecha (bucle)", "Energy · Projectile right (loop)",
            "energia", 48, 7004, ["energía", "energy", "proyectil", "projectile", "bola", "orb", "bucle", "loop"],
            loop=True, size=512, thumb=0.3)
    s.fps = 24
    return render(s, orb_shot(512, 512, 83, size=1.3), tones=CYAN, halo=HALO_CYAN)


def crackle(rnd, cx, cy, r0, r1, k):
    """A lightning crackle round a centre: a jagged arc of thin segments between radii r0 and r1."""
    a = rnd.uniform(0, 2 * math.pi)
    span = rnd.uniform(1.2, 2.6)
    n = 9
    pts = []
    for i in range(n + 1):
        b = a + span * i / n
        r = rnd.uniform(r0, r1)
        pts.append((cx + math.cos(b) * r, cy + math.sin(b) * r))
    lobes = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0) / 2
        lobes.append(((x0 + x1) / 2, (y0 + y1) / 2, L + 1.5 * k, 1.0, 1.6 * k / (L + 1.5 * k), math.atan2(y1 - y0, x1 - x0),
                      0.9))
    return lobes


def charge_orb(W, H, seed, size=1.0, period=2.0):
    """An energy charge, looping (RTFX's «Charge Radial Loop»): a white orb with a soft halo that swells
    and a ring that pulses out from it, while crackles of lightning flicker round it now and then."""
    m = Mass(W, H, seed, rough=0.05)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2

    def lobes_at(t):
        n = int(round(t * 24)) // 2
        rnd = np.random.default_rng(seed * 100 + n)
        beat = 0.5 + 0.5 * math.sin(2 * math.pi * t / period * 2)
        lobes = [(cx, cy, (17 + 2 * beat) * k, 1.0, 1.0, 0.0, 0.97)]
        for ph in (0.0, 0.5):
            a = (t / period * 2 + ph) % 1.0
            r = (22 + 34 * a) * k
            w = 1.6 * k * (1 - a)
            if w > 0.6:
                lobes.extend(ring(cx, cy, r, w, 0.0))
        if n % 4 != 1:
            for _ in range(1 + (n % 2)):
                lobes += crackle(rnd, cx, cy, 24 * k, 44 * k, k)
        return lobes

    return looped(m, lobes_at, period, "radial", (cx, cy), 60 * k)


def make_charge_orb():
    s = new("ex-energia-carga-esfera", "Energía · Carga de energía (bucle)", "Energy · Charge orb (loop)", "energia", 48,
            7005, ["energía", "energy", "carga", "charge", "esfera", "orb", "poder", "power", "bucle", "loop"], loop=True,
            size=512, thumb=0.5)
    s.fps = 24
    return render(s, charge_orb(512, 512, 89, size=1.5), tones=TONES, halo=HALO)


def halo(W, H, seed, size=1.0, period=2.0):
    """A halo of energy, looping (RTFX's «Ray Up Loop»): a flat ring seen at an angle, its rim licking
    with little flames that run round it, the inside a thin blue sheet."""
    m = Mass(W, H, seed, rough=0.35)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2
    rx, ry = 52 * k, 12 * k

    def lobes_at(t):
        lobes = [(cx, cy, rx, 1.0, ry / rx, 0.0, 0.0)]  # the sheet: rim only
        n = 90
        for i in range(n):
            a = 2 * math.pi * i / n
            x, y = cx + math.cos(a) * rx, cy + math.sin(a) * ry
            lick = 0.5 + 0.5 * math.sin(a * 5 + 2 * math.pi * t / period * 3)
            lobes.append((x, y - lick * 1.6 * k, (1.8 + 0.9 * lick) * k, 1.0, 1.0 + 0.9 * lick, 0.0, 0.92))
        return lobes

    return looped(m, lobes_at, period, "up", (cx, cy + ry), 40 * k)


def make_halo():
    s = new("ex-energia-halo", "Energía · Halo de energía (bucle)", "Energy · Energy halo (loop)", "energia", 48, 7006,
            ["energía", "energy", "halo", "anillo", "ring", "aura", "bucle", "loop"], loop=True, size=512, thumb=0.5)
    s.fps = 24
    return render(s, halo(512, 512, 97, size=1.1), tones=TONES, halo=HALO)


def burst(W, H, seed, size=1.0):
    """An energy explosion hit (RTFX's «Energy Hit Explosion Radial»): a flower of puffs bursts open
    round a centre with needles of light shooting out between them, then the puffs hollow out from
    the middle into a lacy rim that breaks into specks."""
    m = Mass(W, H, seed, rough=0.45)
    rnd = np.random.default_rng(seed)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2
    petals = [(2 * math.pi * i / 7 + rnd.uniform(-0.2, 0.2), rnd.uniform(0.85, 1.15)) for i in range(7)]
    needles = [(rnd.uniform(0, 2 * math.pi), rnd.uniform(0.8, 1.3)) for _ in range(7)]

    def field(t):
        e = 1 - (1 - min(1.0, t / 0.3)) ** 3
        lobes = []
        R = (10 + 26 * e) * k
        for a, js in petals:
            hole = max(0.0, (t - 0.1) / 0.35)
            lobes.append((cx + math.cos(a) * R, cy + math.sin(a) * R, (9 + 14 * e) * js * k * max(0.0, 1 - max(0.0, t - 0.55) / 0.35), 1.0, 1.0, a, 0.9,
                          min(0.9, 0.45 + 0.5 * hole) if hole > 0 else 0.0, a + math.pi, 0.42 - 0.2 * min(1.0, hole), True))
        core = max(0.0, 1 - t / 0.18)
        if core > 0:
            lobes.append((cx, cy, 20 * k * core, 1.0, 1.0, 0.0, 0.9))
        nd = max(0.0, 1 - max(0.0, t - 0.2) / 0.3) * min(1.0, t / 0.08)
        if nd > 0:
            for a, ln in needles:
                L = (6 + 12 * e) * ln * k
                d = R + L * 0.8
                lobes.append((cx + math.cos(a) * d, cy + math.sin(a) * d, L, 1.0, 0.07, a, 0.9 * nd))
        ch = max(0.0, (t - 0.35) / 0.9)
        return m.field(lobes, t, "radial", (cx, cy), 60 * k, 9.0, 1.0, crown=0.0, life=0.0, char=ch)

    return field


def make_burst():
    s = new("ex-energia-explosion", "Energía · Explosión de energía", "Energy · Energy burst", "energia", 20, 7007,
            ["energía", "energy", "explosión", "explosion", "golpe", "hit", "impacto"], size=512, thumb=0.2)
    s.fps = 24
    return render(s, burst(512, 512, 101, size=1.35), tones=TONES, halo=HALO)


def flash(W, H, seed, size=1.0):
    """A flash hit (RTFX's «Energy Hit Radial» 005): a white ball with spikes swells for a few frames,
    opens into a ring with specks thrown off it, and a thin crescent is left, turning and fading."""
    m = Mass(W, H, seed, rough=0.05)
    k = size * m.gw / 256
    cx, cy = m.gw / 2, m.gh / 2

    def field(t):
        lobes = []
        g = min(1.0, t / 0.17)
        R = (14 + 22 * g) * k
        if t < 0.17:
            lobes.append((cx, cy, R, 1.0, 1.0, 0.0, 0.95))
        elif t < 0.26:
            o = (t - 0.17) / 0.09
            lobes.extend(ring(cx, cy, R * (1 + 0.15 * o), R * (0.6 - 0.5 * o), 0.95))
        sp = 1 - abs(t - 0.15) / 0.12
        if sp > 0:
            for j in range(5):
                a = j * 2 * math.pi / 5 + 0.3
                d = R + 6 * k + 12 * k * max(0.0, t - 0.15) / 0.1
                lobes.append((cx + math.cos(a) * d, cy + math.sin(a) * d, 8 * k * sp, 1.0, 0.22, a, 0.9))
        c = max(0.0, (t - 0.24) / 0.14)
        if 0 < c < 1:
            def arc(u, c=c):
                a = -1.2 + 0.4 * c + 1.7 * u
                return cx + math.cos(a) * R * 1.12, cy + math.sin(a) * R * 1.12
            lobes += ribbon(arc, lambda u: 3.0 * k * math.sin(math.pi * u) * (1 - c * 0.7), 40, lambda u: 0.95)
        return m.field(lobes, t, "radial", (cx, cy), 60 * k, 9.0, 1.0, crown=0.0, life=0.0)

    return field


def make_flash():
    s = new("ex-energia-destello", "Energía · Destello", "Energy · Flash", "energia", 14, 7008,
            ["energía", "energy", "destello", "flash", "golpe", "hit", "brillo"], size=512, thumb=0.15)
    s.fps = 24
    return render(s, flash(512, 512, 103, size=1.5), tones=TONES, halo=HALO)


VIOLET = [("violeta", "#8a3cff"), ("lila", "#d29cff", 0.2), ("blanco lila", "#fcf4ff", 0.34)]
AQUA = [("turquesa", "#00c9b6"), ("aguamarina", "#79ffec", 0.2), ("blanco agua", "#f2fffc", 0.34)]


def muzzle(W, H, seed, size=1.0, period=1.0):
    """A shot fired, looping (RTFX's «Energy Shot Right MIX»): at the muzzle a flash is drawn anew on
    every second frame, each drawing in one of three colours: now an arrow-shaped burst with chevrons
    and sparks flying off it, now a row of dashes shooting right. Returns one field per colour, each
    empty on the drawings that are not its own."""
    m = Mass(W, H, seed, rough=0.2)
    k = size * m.gw / 256
    mx, my = m.gw * 0.3, m.gh / 2
    empty = (np.zeros_like(m.xx), np.zeros_like(m.xx))
    per = int(round(period * 12))

    def drawing(n):
        rnd = np.random.default_rng(seed * 1000 + n % per)
        colour = (n % per) % 3
        lobes = []
        if (n % per) % 2 == 0:  # the burst
            r = rnd.uniform(13, 18) * k
            lobes.append((mx, my, r, 1.35, 0.85, 0.0, 0.9))
            lobes.append((mx + r * 0.9, my, r * 0.8, 1.0, 0.35, 0.0, 0.9))  # drawn to a point
            for j in range(rnd.integers(2, 4)):
                x = mx + r * 1.2 + j * 9 * k
                for side in (-1, 1):
                    lobes.append((x, my + side * 5 * k, 7 * k, 1.0, 0.22, -side * 0.7, 0.9))
            for _ in range(rnd.integers(1, 3)):
                side = 1 if rnd.random() < 0.5 else -1
                lobes.append((mx - rnd.uniform(0, 8) * k, my + side * rnd.uniform(14, 22) * k, rnd.uniform(2.5, 4.5) * k,
                              0.7, 1.4, 0.0, 0.85))
        else:  # the dashes
            lobes.append((mx, my, 9 * k, 1.2, 1.0, 0.0, 0.9))
            x = mx + 12 * k
            for j in range(rnd.integers(3, 5)):
                L = rnd.uniform(5, 12) * k
                x += L + rnd.uniform(4, 8) * k
                lobes.append((x, my + rnd.uniform(-1.5, 1.5) * k, L, 1.0, 0.35, 0.0, 0.85))
                x += L
        return colour, lobes

    def field_for(c):
        def field(t):
            n = int(round(t * 24)) // 2
            colour, lobes = drawing(n)
            if colour != c:
                return empty
            return m.field(lobes, n * 0.37, math.pi, (mx + 60 * k, my), 120 * k, 99.0, 1.0, crown=0.0, life=0.0)
        return field

    return [field_for(c) for c in range(3)]


def make_muzzle():
    s = new("ex-energia-disparo-colores", "Energía · Disparo de colores (bucle)", "Energy · Colour shot (loop)",
            "energia", 24, 7009, ["energía", "energy", "disparo", "shot", "colores", "colors", "láser", "laser", "bucle",
                                  "loop"], loop=True, size=512, thumb=0.5)
    s.fps = 24
    for f, tones, halo in zip(muzzle(512, 512, 107, size=1.6), (TONES, AQUA, VIOLET),
                              (HALO, [("#00b39f", 70, 90), ("#3ff0d8", 22, 95)], [("#6a1fff", 70, 90), ("#b070ff", 22, 95)])):
        render(s, f, tones=tones, halo=halo)
    return s


STICKERS = [make_hit_rings, make_star_hit, make_ray_up, make_slash, make_projectile, make_charge_orb, make_halo, make_burst, make_flash, make_muzzle]
