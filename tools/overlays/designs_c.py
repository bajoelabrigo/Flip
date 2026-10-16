"""Third batch: particles, celebration and love, with factories so each family has real variants."""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw

import fx
from fx import TAU, Canvas
from designs import GOLD, PARTY, _falling, _rising, _snow, design, wrap

PASTEL = [fx.hex_rgb(c) for c in ("#ffb3c7", "#ffe0a3", "#b5e8ff", "#c8f7c5", "#e0c3ff", "#fff3b0")]
SILVER = [fx.hex_rgb(c) for c in ("#e8ecf2", "#c9d0db", "#ffffff", "#aab4c3")]
REDS = [fx.hex_rgb(c) for c in ("#ff3d6e", "#ff6f91", "#ff9ec0", "#e8174f", "#ffc2d6")]


# ---------------------------------------------------------------- multi-colour sprites (PIL, 4x supersampled)

SS = 4


def _canvas(size):
    n = size * SS
    return n, Image.new("L", (n, n), 0)


def _down(im, size, angle=0.0, sx=1.0):
    if sx < 0.999:
        n = im.width
        im = im.resize((max(int(n * sx), 1), n), Image.LANCZOS)
        pad = Image.new("L", (n, n), 0)
        pad.paste(im, ((n - im.width) // 2, 0))
        im = pad
    if angle:
        im = im.rotate(math.degrees(angle), resample=Image.BICUBIC)
    return np.asarray(im.resize((size, size), Image.LANCZOS), np.float32) / 255.0


@lru_cache(maxsize=4096)
def coin(size, qa, qs):
    n, body = _canvas(size)
    _, rim = _canvas(size)
    _, mark = _canvas(size)
    m = n * 0.08
    ImageDraw.Draw(body).ellipse([m, m, n - m, n - m], fill=255)
    ImageDraw.Draw(rim).ellipse([m, m, n - m, n - m], outline=255, width=int(n * 0.06))
    d = ImageDraw.Draw(mark)
    d.ellipse([n * 0.28, n * 0.28, n * 0.72, n * 0.72], outline=255, width=int(n * 0.05))
    d.polygon([(n * 0.5, n * 0.36), (n * 0.56, n * 0.48), (n * 0.68, n * 0.5), (n * 0.56, n * 0.53), (n * 0.5, n * 0.64),
               (n * 0.44, n * 0.53), (n * 0.32, n * 0.5), (n * 0.44, n * 0.48)], fill=255)
    a, sx = qa / fx.ANGLES * TAU, max(qs / 8, 0.1)
    return tuple(_down(im, size, a, sx) for im in (body, rim, mark))


@lru_cache(maxsize=4096)
def bill(size, qa, qs):
    n, body = _canvas(size)
    _, inner = _canvas(size)
    _, seal = _canvas(size)
    w2, h2 = n * 0.46, n * 0.22
    cx, cy = n / 2, n / 2
    ImageDraw.Draw(body).rectangle([cx - w2, cy - h2, cx + w2, cy + h2], fill=255)
    ImageDraw.Draw(inner).rectangle([cx - w2 * 0.88, cy - h2 * 0.78, cx + w2 * 0.88, cy + h2 * 0.78], outline=255,
                                    width=int(n * 0.018))
    ImageDraw.Draw(seal).ellipse([cx - h2 * 0.6, cy - h2 * 0.6, cx + h2 * 0.6, cy + h2 * 0.6], fill=255)
    a, sy = qa / fx.ANGLES * TAU, max(qs / 8, 0.2)
    out = []
    for im in (body, inner, seal):
        if sy < 0.999:   # flutter: squash vertically
            sq = im.resize((n, max(int(n * sy), 1)), Image.LANCZOS)
            pad = Image.new("L", (n, n), 0)
            pad.paste(sq, (0, (n - sq.height) // 2))
            im = pad
        out.append(_down(im, size, a))
    return tuple(out)


@lru_cache(maxsize=2048)
def gift(size, qa):
    n, box = _canvas(size)
    _, ribbon = _canvas(size)
    d = ImageDraw.Draw(box)
    d.rectangle([n * 0.18, n * 0.38, n * 0.82, n * 0.86], fill=255)
    d.rectangle([n * 0.13, n * 0.27, n * 0.87, n * 0.4], fill=255)
    r = ImageDraw.Draw(ribbon)
    r.rectangle([n * 0.45, n * 0.27, n * 0.55, n * 0.86], fill=255)
    r.ellipse([n * 0.26, n * 0.1, n * 0.5, n * 0.3], outline=255, width=int(n * 0.06))
    r.ellipse([n * 0.5, n * 0.1, n * 0.74, n * 0.3], outline=255, width=int(n * 0.06))
    a = qa / fx.ANGLES * TAU
    return _down(box, size, a), _down(ribbon, size, a)


@lru_cache(maxsize=1024)
def emoji(size, kind, qa):
    """Our own round faces: smile, love (heart eyes), laugh, wow, cool."""
    n, face = _canvas(size)
    _, ink = _canvas(size)
    _, red = _canvas(size)
    m = n * 0.06
    ImageDraw.Draw(face).ellipse([m, m, n - m, n - m], fill=255)
    d = ImageDraw.Draw(ink)
    rr = ImageDraw.Draw(red)
    lw = int(n * 0.06)
    if kind == "love":
        for cx in (0.33, 0.67):
            pts = [((cx + 0.11 * (16 * math.sin(t) ** 3) / 16) * n,
                    (0.4 - 0.11 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16) * n)
                   for t in np.linspace(0, TAU, 40)]
            rr.polygon(pts, fill=255)
    elif kind == "laugh":
        for cx in (0.33, 0.67):
            d.arc([(cx - 0.1) * n, 0.32 * n, (cx + 0.1) * n, 0.48 * n], 200, 340, fill=255, width=lw)
    elif kind == "cool":
        d.rounded_rectangle([0.18 * n, 0.32 * n, 0.48 * n, 0.48 * n], radius=int(n * 0.05), fill=255)
        d.rounded_rectangle([0.52 * n, 0.32 * n, 0.82 * n, 0.48 * n], radius=int(n * 0.05), fill=255)
        d.line([(0.46 * n, 0.36 * n), (0.54 * n, 0.36 * n)], fill=255, width=lw)
    else:
        for cx in (0.35, 0.65):
            d.ellipse([(cx - 0.055) * n, 0.32 * n, (cx + 0.055) * n, 0.47 * n], fill=255)
    if kind == "wow":
        d.ellipse([0.4 * n, 0.58 * n, 0.6 * n, 0.8 * n], fill=255)
    elif kind == "laugh":
        d.chord([0.25 * n, 0.45 * n, 0.75 * n, 0.85 * n], 0, 180, fill=255)
    else:
        d.arc([0.27 * n, 0.4 * n, 0.73 * n, 0.78 * n], 20, 160, fill=255, width=lw)
    a = qa / fx.ANGLES * TAU
    return _down(face, size, a), _down(ink, size, a), _down(red, size, a)


@lru_cache(maxsize=1024)
def streamer(size, qa, phase_q):
    n, im = _canvas(size)
    ph = phase_q / 8 * TAU
    pts = [(n * 0.5 + math.sin(t * 3 + ph) * n * 0.16, n * 0.06 + t / TAU * n * 0.88) for t in np.linspace(0, TAU, 60)]
    ImageDraw.Draw(im).line(pts, fill=255, width=int(n * 0.07), joint="curve")
    return _down(im, size, qa / fx.ANGLES * TAU)


@lru_cache(maxsize=1024)
def heart_outline(size, qa, width=0.09):
    full = fx.heart(size, qa)
    inner = fx.heart(max(int(size * (1 - width * 2.4)), 2), qa)
    pad = (size - inner.shape[0]) // 2
    hole = np.zeros_like(full)
    hole[pad:pad + inner.shape[0], pad:pad + inner.shape[1]] = inner
    return np.clip(full - hole, 0, 1)


@lru_cache(maxsize=512)
def neon_heart(size, qa):
    return fx.blur_sprite(heart_outline(size, qa), max(size / 14, 1.5))


@lru_cache(maxsize=256)
def balloon_parts(size, shape):
    bw = int(size)
    bh = int(size * 1.22)
    H = int(bh * 2.9)
    ss = 3
    body = Image.new("L", (bw * ss, H * ss), 0)
    dr = ImageDraw.Draw(body)
    kx = bw * ss // 2
    if shape == "heart":
        pts = []
        for i in range(64):
            t = i / 64 * TAU
            x = 16 * math.sin(t) ** 3
            y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts.append((kx + x / 17 * bw * ss / 2, (y + 4) / 17 * bh * ss / 2 + bh * ss * 0.42))
        dr.polygon(pts, fill=255)
        top = bh * ss * 0.92
    else:
        dr.ellipse([0, 0, bw * ss - 1, bh * ss], fill=255)
        top = bh * ss - 2
    dr.polygon([(kx - 8 * ss, top), (kx + 8 * ss, top), (kx, top + 14 * ss)], fill=255)
    string = Image.new("L", (bw * ss, H * ss), 0)
    pts = [(kx + math.sin(v / 40) * 14 * ss, top + 14 * ss + v * ss) for v in range(0, H - bh - 16, 6)]
    ImageDraw.Draw(string).line(pts, fill=200, width=2 * ss)
    hi = Image.new("L", (bw * ss, H * ss), 0)
    ImageDraw.Draw(hi).ellipse([bw * ss * 0.2, bh * ss * 0.12, bw * ss * 0.42, bh * ss * 0.38], fill=170)
    return tuple(np.asarray(im.resize((bw, H), Image.LANCZOS), np.float32) / 255 for im in (body, string, hi))


# ================================================================ Partículas

design("part-chispas", "Chispas", "Sparks", "particulas", 6, res=(540, 960),
       tags=["chispas", "sparks", "fuego", "bengala", "energia", "fire"], sample="gym-02.jpg")(
    _rising(90, [fx.hex_rgb(c) for c in ("#ffb347", "#ff7a1a", "#ffd27a")], 9, (2, 3), 1, 36, 120, sway=30))
design("part-chispas-azules", "Chispas azules", "Blue sparks", "particulas", 6, res=(540, 960),
       tags=["chispas", "azules", "sparks", "blue", "energia", "electrico", "magia"], sample="gym-04.jpg")(
    _rising(90, [fx.hex_rgb(c) for c in ("#5fb0ff", "#2fd8ff", "#b8e6ff")], 9, (2, 3), 1, 36, 120, sway=30))
design("part-brasas-azules", "Brasas azules", "Blue embers", "particulas", 8, res=(540, 960),
       tags=["brasas", "azules", "embers", "magia", "fantasia", "hielo"], sample="man-06.jpg")(
    _rising(70, [fx.hex_rgb(c) for c in ("#3d7bff", "#2fd8ff", "#8a6bff")], 11, (1, 2), 1, 48, 0, sway=60))
design("part-ascendentes", "Luces que suben", "Rising lights", "particulas", 10, res=(540, 960),
       tags=["luces", "subiendo", "rising", "espiritual", "paz", "calma", "memorial", "recuerdo"],
       sample="church-02.jpg")(
    _rising(50, [(1, 1, 1), (1, 0.97, 0.88)], 13, (1, 1), 1, 56, 0, sway=50))


def _twinkles(palette, n, rmin, rmax, star5=False):
    def make(w, h, T, rng):
        s = w / 1080
        xs, ys = rng.uniform(0, w, n), rng.uniform(0, h, n)
        ph = rng.uniform(0, TAU, n)
        k = rng.integers(1, 4, n)
        big = rng.uniform(rmin, rmax, n) * s
        cols = [palette[i] for i in rng.integers(0, len(palette), n)]
        spin = rng.integers(-1, 2, n)

        def frame(t):
            u = t / T
            c = Canvas(w, h)
            for i in range(n):
                b = max(0.0, math.sin(TAU * k[i] * u + ph[i])) ** 3
                if b < 0.02:
                    continue
                r = max(int(big[i] * (0.4 + 0.6 * b)), 3)
                if star5:
                    c.splat(fx.glow(r), xs[i], ys[i], cols[i], 0.35 * b, add=True)
                    c.splat(fx.star5(r, fx._q(ph[i] + TAU * spin[i] * u)), xs[i], ys[i], cols[i], b)
                else:
                    c.splat(fx.sparkle(r), xs[i], ys[i], cols[i], b, add=True)
            return c
        return frame
    return make


design("part-brillos", "Destellos", "Twinkles", "particulas", 6,
       tags=["brillos", "destellos", "twinkle", "sparkle", "magia", "estrellas", "glitter", "belleza"],
       sample="makeup-01.jpg")(_twinkles([(1, 1, 1), (1, 1, 1), GOLD[0]], 55, 30, 75))
design("part-brillos-dorados", "Destellos dorados", "Gold twinkles", "particulas", 6,
       tags=["brillos", "dorados", "gold", "sparkle", "elegante", "boda", "lujo"], sample="wedding-01.jpg")(
    _twinkles(GOLD, 60, 30, 80))
design("part-brillos-rosa", "Destellos rosa", "Pink twinkles", "particulas", 6,
       tags=["brillos", "rosa", "pink", "sparkle", "aesthetic", "belleza", "kawaii"], sample="makeup-03.jpg")(
    _twinkles([fx.hex_rgb(c) for c in ("#ff9ec7", "#ffc2d6", "#ffffff", "#ff6fa8")], 60, 30, 80))
design("part-brillos-azules", "Destellos azules", "Blue twinkles", "particulas", 6,
       tags=["brillos", "azules", "blue", "sparkle", "hielo", "invierno", "magia"], sample="portrait-01.jpg")(
    _twinkles([fx.hex_rgb(c) for c in ("#9fd8ff", "#5fb0ff", "#ffffff")], 60, 30, 80))
design("part-destellos-grandes", "Destellos grandes", "Big sparkles", "particulas", 6,
       tags=["destellos", "grandes", "sparkle", "brillo", "producto", "limpio", "nuevo"], sample="coffee-03.jpg")(
    _twinkles([(1, 1, 1)], 9, 110, 210))
design("part-estrellitas", "Estrellitas", "Little stars", "particulas", 6,
       tags=["estrellitas", "stars", "infantil", "kids", "magia", "dulce", "kawaii"], sample="baby-01.jpg")(
    _twinkles([fx.hex_rgb(c) for c in ("#ffd23f", "#fff1c2", "#ff9ec7", "#9fd8ff")], 45, 26, 52, star5=True))


def _dust(palette, n=260, rmin=2, rmax=7, drift=(0, 1)):
    def make(w, h, T, rng):
        s = w / 1080
        x0, y0 = rng.uniform(0, w, n), rng.uniform(0, h, n)
        lx = rng.integers(drift[0], drift[1] + 1, n) if drift[0] != drift[1] else np.full(n, drift[0])
        ly = rng.integers(1, 2, n)
        ph = rng.uniform(0, TAU, n)
        tw = rng.integers(2, 6, n)
        r = rng.uniform(rmin, rmax, n) * s
        cols = [palette[i] for i in rng.integers(0, len(palette), n)]

        def frame(t):
            u = t / T
            c = Canvas(w, h)
            for i in range(n):
                x = wrap(x0[i] + lx[i] * w * u, 0, w)
                y = wrap(y0[i] - ly[i] * h * u + 20 * s * math.sin(TAU * u + ph[i]), 0, h)
                b = 0.35 + 0.65 * max(0.0, math.sin(TAU * tw[i] * u + ph[i]))
                c.splat(fx.glow(max(int(r[i] * 2.5), 2)), x, y, cols[i], 0.35 * b, add=True)
                c.splat(fx.glow(max(int(r[i]), 1)), x, y, (1, 0.97, 0.85), b, add=True)
            return c
        return frame
    return make


design("part-polvo-dorado", "Polvo dorado", "Gold dust", "particulas", 8, res=(540, 960),
       tags=["polvo", "dorado", "gold", "dust", "magia", "elegante", "boda", "particulas"], sample="couple-07.jpg")(
    _dust(GOLD))
design("part-polvo-plateado", "Polvo plateado", "Silver dust", "particulas", 8, res=(540, 960),
       tags=["polvo", "plateado", "silver", "dust", "invierno", "elegante", "magia"], sample="wedding-02.jpg")(
    _dust(SILVER))
design("part-polvo-rosa", "Polvo rosa", "Pink dust", "particulas", 8, res=(540, 960),
       tags=["polvo", "rosa", "pink", "dust", "aesthetic", "quince", "magia"], sample="quince-05.jpg")(
    _dust([fx.hex_rgb(c) for c in ("#ff9ec7", "#ffc2d6", "#ff6fa8", "#ffe0f0")]))
design("part-motas-luz", "Motas de luz", "Sunlit dust motes", "particulas", 10, res=(540, 960),
       tags=["motas", "polvo", "luz", "dust motes", "sol", "calma", "nostalgia", "hogar"], sample="church-01.jpg")(
    _dust([fx.hex_rgb("#ffe6b0"), fx.hex_rgb("#fff4dc")], n=170, rmin=3, rmax=7, drift=(0, 0)))


@design("part-burbujas", "Burbujas", "Bubbles", "particulas", 8,
        tags=["burbujas", "bubbles", "jabon", "agua", "niños", "infantil", "kids"], sample="baby-02.jpg")
def _bubbles(w, h, T, rng):
    return _bubbles_f(False)(w, h, T, rng)


def _bubbles_f(iridescent):
    def make(w, h, T, rng):
        s = w / 1080
        n = 34
        x0, y0 = rng.uniform(0, w, n), rng.uniform(0, h, n)
        rad = rng.uniform(18, 75, n) * s
        laps = np.where(rad > 50 * s, 1, rng.integers(1, 3, n))
        sway = rng.uniform(20, 70, n) * s
        ph = rng.uniform(0, TAU, n)
        hue = rng.uniform(0, 1, n)
        m = 90 * s

        def frame(t):
            u = t / T
            c = Canvas(w, h)
            for i in range(n):
                y = wrap(y0[i] - laps[i] * (h + 2 * m) * u, -m, h + m)
                x = x0[i] + sway[i] * math.sin(TAU * 2 * u + ph[i])
                col = fx.hsv(hue[i] + u, 0.35, 1.0) if iridescent else (0.95, 0.98, 1.0)
                c.splat(fx.bubble(int(rad[i])), x, y, col, 0.9)
                if iridescent:
                    c.splat(fx.ring(int(rad[i] * 0.92), max(3 * s, 1.5)), x, y, fx.hsv(hue[i] + u + 0.4, 0.6, 1.0), 0.35,
                            add=True)
            return c
        return frame
    return make


design("part-burbujas-arcoiris", "Burbujas tornasol", "Iridescent bubbles", "particulas", 8,
       tags=["burbujas", "tornasol", "iridescent", "arcoiris", "jabon", "aesthetic"], sample="friends-04.jpg")(
    _bubbles_f(True))


def _meteors(k, sn, dur=0.8):
    def make(w, h, T, rng):
        s = w / 1080
        starts = np.sort(rng.uniform(0, T, k))
        starts[0] = T * 0.5 - dur * 0.45   # one crossing at the middle: the card shows it
        p0 = np.c_[rng.uniform(0.2, 1.1, k) * w, rng.uniform(-0.05, 0.45, k) * h]
        ang = rng.uniform(math.radians(115), math.radians(135), k)
        dist = rng.uniform(0.55, 0.85, k) * w
        sx, sy = rng.uniform(0, w, sn), rng.uniform(0, h * 0.6, sn)
        sph = rng.uniform(0, TAU, sn)

        def frame(t):
            c = Canvas(w, h)
            for i in range(sn):
                b = 0.3 + 0.3 * math.sin(TAU * 2 * t / T + sph[i])
                c.splat(fx.glow(int(5 * s)), sx[i], sy[i], (1, 1, 1), b, add=True)
            for i in range(k):
                age = ((t - starts[i]) % T) / dur
                if age >= 1:
                    continue
                d = fx.ease_out(age) * dist[i]
                x = p0[i, 0] + math.cos(ang[i]) * d
                y = p0[i, 1] + math.sin(ang[i]) * d
                op = math.sin(math.pi * age)
                c.splat(fx.streak_at(320 * s, 5 * s, math.pi / 2 - ang[i]), x, y, (1, 0.97, 0.9), op, add=True)
                c.splat(fx.glow(int(24 * s)), x, y, (1, 1, 1), op, add=True)
            return c
        return frame
    return make


design("part-estrellas-fugaces", "Estrellas fugaces", "Shooting stars", "particulas", 6,
       tags=["estrellas fugaces", "shooting stars", "cielo", "noche", "deseo", "meteoro", "magia"],
       sample="fashion-01.jpg")(_meteors(5, 40))
design("part-lluvia-meteoros", "Lluvia de meteoros", "Meteor shower", "particulas", 6,
       tags=["meteoros", "meteor shower", "estrellas fugaces", "cielo", "noche", "espacio"], sample="friends-10.jpg")(
    _meteors(16, 60, dur=0.6))


@design("part-polvo-magico", "Polvo mágico", "Magic dust trail", "particulas", 4, res=(540, 960),
        tags=["magia", "magic", "varita", "wand", "polvo", "estela", "hada", "fantasia", "trail"],
        sample="baby-03.jpg")
def _magic_trail(w, h, T, rng):
    s = w / 1080
    n = 220
    born = rng.uniform(0, 1, n)
    jit = rng.normal(0, 18, (n, 2)) * s
    fall = rng.uniform(80, 260, n) * s
    cols = [GOLD[i % len(GOLD)] if rng.random() < 0.7 else (1, 1, 1) for i in range(n)]

    def path(p):   # a figure eight around the subject
        return (w * (0.5 + 0.38 * math.sin(TAU * p)), h * (0.5 + 0.28 * math.sin(2 * TAU * p)))

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        for i in range(n):
            age = (u - born[i]) % 1.0
            if age > 0.45:
                continue
            x, y = path(born[i])
            life = age / 0.45
            x += jit[i, 0] * life
            y += jit[i, 1] * life + fall[i] * life
            op = (1 - life) ** 1.3
            c.splat(fx.glow(int(9 * s)), x, y, cols[i], op, add=True)
            if i % 6 == 0:
                c.splat(fx.sparkle(int(34 * s * (1 - life))), x, y, (1, 1, 1), op, add=True)
        hx, hy = path(u)
        c.splat(fx.glow(int(60 * s)), hx, hy, GOLD[0], 0.6, add=True)
        c.splat(fx.sparkle(int(90 * s)), hx, hy, (1, 1, 1), 1.0, add=True)
        return c
    return frame


@design("part-velocidad-luz", "Viaje a la velocidad de la luz", "Warp speed", "particulas", 3, res=(540, 960),
        tags=["velocidad", "warp", "espacio", "space", "estrellas", "hiperespacio", "intro", "zoom"],
        sample="concert-03.jpg")
def _warp(w, h, T, rng):
    s = w / 1080
    n = 260
    ang = rng.uniform(0, TAU, n)
    ph = rng.uniform(0, 1, n)
    laps = rng.integers(1, 3, n)
    R = math.hypot(w, h) / 2

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        for i in range(n):
            p = (u * laps[i] + ph[i]) % 1.0
            r = R * p ** 2.2
            x, y = w / 2 + math.cos(ang[i]) * r, h / 2 + math.sin(ang[i]) * r
            length = 20 * s + 520 * s * p ** 2
            c.splat(fx.streak_at(length, (2 + 4 * p) * s, math.pi / 2 - ang[i]), x, y, (0.85, 0.92, 1), min(p * 3, 1) * 0.9,
                    add=True)
        return c
    return frame


@design("part-orbes", "Orbes de luz", "Light orbs", "particulas", 10, res=(270, 480),
        tags=["orbes", "orbs", "luz", "suave", "sueño", "dreamy", "aesthetic", "calma"], sample="diwali-02.jpg")
def _orbs(w, h, T, rng):
    s = w / 1080
    n = 9
    cx, cy = rng.uniform(0, w, n), rng.uniform(0, h, n)
    ax, ay = rng.uniform(40, 160, n) * s, rng.uniform(60, 220, n) * s
    f = rng.integers(1, 3, (n, 2))
    ph = rng.uniform(0, TAU, (n, 3))
    r = rng.uniform(120, 260, n) * s
    cols = [fx.hex_rgb(c) for c in ("#ff9ec7", "#9fd8ff", "#ffd27a", "#c8a0ff", "#a0ffd8")]

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        for i in range(n):
            x = cx[i] + ax[i] * math.sin(TAU * f[i, 0] * u + ph[i, 0])
            y = cy[i] + ay[i] * math.sin(TAU * f[i, 1] * u + ph[i, 1])
            op = 0.6 + 0.25 * math.sin(TAU * u + ph[i, 2])
            c.splat(fx.glow(int(r[i])), x, y, cols[i % len(cols)], op, add=True)
        return c
    return frame


@design("part-explosion-chispas", "Explosión de chispas", "Spark burst", "particulas", 1.8, loop=False, res=(540, 960),
        thumb_at=0.18, tags=["explosion", "chispas", "burst", "impacto", "golpe", "transicion", "energia"],
        sample="gym-04.jpg")
def _spark_burst(w, h, T, rng):
    s = w / 1080
    n = 180
    ang = rng.uniform(0, TAU, n)
    spd = rng.uniform(600, 1800, n) * s
    kd = rng.uniform(2.0, 3.5, n)
    cols = [fx.hex_rgb(c) for c in ("#ffd27a", "#ffb347", "#ffffff")]
    g = 500 * s

    def frame(t):
        c = Canvas(w, h)
        if t < 0.12:
            c.splat(fx.glow(int(260 * s)), w / 2, h / 2, (1, 0.9, 0.7), 1 - t / 0.12, add=True)
        for i in range(n):
            e = (1 - math.exp(-kd[i] * t)) / kd[i]
            vx = math.cos(ang[i]) * spd[i] * math.exp(-kd[i] * t)
            vy = math.sin(ang[i]) * spd[i] * math.exp(-kd[i] * t) + g * t
            x = w / 2 + math.cos(ang[i]) * spd[i] * e
            y = h / 2 + math.sin(ang[i]) * spd[i] * e + 0.5 * g * t * t
            op = max(0.0, 1 - t / T) ** 1.2
            speed = math.hypot(vx, vy)
            c.splat(fx.streak_at(max(speed * 0.06, 8 * s), 7 * s, math.atan2(vx, vy)), x, y, cols[i % 3], op, add=True)
        return c
    return frame


@design("part-bengala", "Bengala", "Sparkler", "particulas", 3, res=(540, 960),
        tags=["bengala", "sparkler", "chispas", "año nuevo", "boda", "celebracion", "fiesta"], sample="newyear-01.jpg")
def _sparkler(w, h, T, rng):
    s = w / 1080
    n = 160
    born = rng.uniform(0, 1, n)
    ang = rng.uniform(0, TAU, n)
    spd = rng.uniform(250, 700, n) * s
    life = rng.uniform(0.12, 0.3, n)
    ox, oy = w * 0.5, h * 0.62

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        c.splat(fx.glow(int(120 * s)), ox, oy, (1, 0.85, 0.55), 0.55, add=True)
        c.splat(fx.glow(int(30 * s)), ox, oy, (1, 1, 1), 1, add=True)
        for i in range(n):
            age = ((u - born[i]) % 1.0) * T
            if age > life[i]:
                continue
            p = age / life[i]
            d = spd[i] * age
            x, y = ox + math.cos(ang[i]) * d, oy + math.sin(ang[i]) * d + 300 * s * age * age
            c.splat(fx.streak_at(40 * s * (1 - p) + 8 * s, 3 * s, math.pi / 2 - ang[i]), x, y, (1, 0.9, 0.6), 1 - p, add=True)
            if p > 0.7 and i % 3 == 0:   # the little forks at the end
                c.splat(fx.sparkle(int(26 * s)), x, y, (1, 0.95, 0.8), (1 - p) * 3, add=True)
        return c
    return frame


@design("part-lluvia-luces", "Lluvia de luces", "Light rain", "particulas", 6, res=(540, 960),
        tags=["lluvia de luces", "light rain", "luces", "fiesta", "discoteca", "noche", "neon"], sample="concert-04.jpg")
def _light_rain(w, h, T, rng):
    s = w / 1080
    n = 70
    x0, y0 = rng.uniform(0, w, n), rng.uniform(0, h, n)
    laps = rng.integers(1, 4, n)
    ln = rng.uniform(120, 320, n) * s
    cols = [PARTY[i] for i in rng.integers(0, 6, n)]

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        for i in range(n):
            m = ln[i]
            y = wrap(y0[i] + laps[i] * (h + 2 * m) * u, -m, h + m)
            c.splat(fx.streak_at(ln[i], 6 * s, 0), x0[i], y, cols[i], 0.8, add=True)
            c.splat(fx.glow(int(14 * s)), x0[i], y + ln[i] / 2, (1, 1, 1), 0.8, add=True)
        return c
    return frame


@design("part-nieve-brillante", "Nieve brillante", "Glitter snow", "particulas", 8, res=(540, 960),
        tags=["nieve", "brillante", "glitter", "invierno", "navidad", "magia", "snow"], sample="christmas-04.jpg")
def _glitter_snow(w, h, T, rng):
    snow = _snow([(160, 5, 9, 1, 0.8), (60, 10, 16, 1, 0.95)])(w, h, T, rng)
    tw = _twinkles([(1, 1, 1), fx.hex_rgb("#cfe8ff")], 40, 40, 80)(w, h, T, rng)

    def frame(t):
        c = snow(t)
        c.merge(tw(t))
        return c
    return frame


# ================================================================ Celebración

design("cel-confeti-pastel", "Confeti pastel", "Pastel confetti", "celebracion", 6,
       tags=["confeti", "pastel", "baby shower", "bebe", "cumpleaños", "suave", "celebracion"], sample="pregnant-01.jpg")(
    _falling("confetti", 150, PASTEL, (16, 32), (1, 2)))
design("cel-confeti-plata", "Confeti plateado", "Silver confetti", "celebracion", 6,
       tags=["confeti", "plateado", "silver", "boda", "aniversario", "elegante", "celebracion"], sample="wedding-03.jpg")(
    _falling("confetti", 140, SILVER, (16, 30), (1, 2)))
design("cel-confeti-grande", "Confeti grande", "Big confetti", "celebracion", 6,
       tags=["confeti", "grande", "big", "fiesta", "alegre", "celebracion", "party"], sample="friends-03.jpg")(
    _falling("confetti", 45, PARTY, (40, 70), (1, 1), sway=90))
design("cel-confeti-corazones", "Confeti de corazones", "Heart confetti", "celebracion", 6,
       tags=["confeti", "corazones", "hearts", "boda", "amor", "san valentin", "celebracion"], sample="wedding-04.jpg")(
    _falling("heart", 90, REDS + [(1, 1, 1)], (20, 38), (1, 2)))
design("cel-confeti-circulos", "Confeti de puntos", "Dot confetti", "celebracion", 6,
       tags=["confeti", "puntos", "dots", "circulos", "fiesta", "minimal", "celebracion"], sample="birthday-02.jpg")(
    _falling("disc", 160, PARTY, (14, 28), (1, 2)))
design("cel-estrellas-doradas", "Estrellas doradas", "Gold stars", "celebracion", 6,
       tags=["estrellas", "doradas", "gold", "stars", "premio", "logro", "graduacion", "celebracion"],
       sample="graduation-02.jpg")(
    _falling("star", 55, GOLD, (26, 54), (1, 1)))


def _burst_f(palette, origin="corners", kind="confetti", n=280):
    def make(w, h, T, rng):
        s = w / 1080
        if origin == "corners":
            side = rng.choice([-1, 1], n)
            x0 = np.where(side < 0, -20 * s, w + 20 * s)
            y0 = np.full(n, h * 0.95)
            ang = np.where(side < 0, rng.uniform(math.radians(-80), math.radians(-40), n),
                           rng.uniform(math.radians(-140), math.radians(-100), n))
            spd = rng.uniform(1700, 3200, n) * s
        elif origin == "center":
            x0, y0 = np.full(n, w / 2), np.full(n, h * 0.55)
            ang = rng.uniform(0, TAU, n)
            spd = rng.uniform(600, 2200, n) * s
        else:   # top: cannons pointing down from the top corners
            side = rng.choice([-1, 1], n)
            x0 = np.where(side < 0, -20 * s, w + 20 * s)
            y0 = np.full(n, -20 * s)
            ang = np.where(side < 0, rng.uniform(math.radians(20), math.radians(60), n),
                           rng.uniform(math.radians(120), math.radians(160), n))
            spd = rng.uniform(1200, 2400, n) * s
        vx, vy = np.cos(ang) * spd, np.sin(ang) * spd
        kd = rng.uniform(1.6, 2.6, n)
        g = 900 * s
        ph = rng.uniform(0, TAU, (n, 3))
        rot = rng.uniform(2, 6, n) * rng.choice([-1, 1], n)
        sz = rng.uniform(16, 32, n) * s * (1.4 if kind == "heart" else 1)
        cols = [palette[i] for i in rng.integers(0, len(palette), n)]
        aspect = rng.uniform(0.35, 0.7, n)
        delay = rng.uniform(0, 0.12, n)

        def frame(t):
            c = Canvas(w, h)
            fade = 1 - fx.smooth(T - 0.8, T, t)
            for i in range(n):
                tt = t - delay[i]
                if tt <= 0:
                    continue
                e = (1 - math.exp(-kd[i] * tt)) / kd[i]
                x = x0[i] + vx[i] * e + 40 * s * math.sin(TAU * 0.7 * tt + ph[i, 0]) * min(tt, 1)
                y = y0[i] + vy[i] * e + g / kd[i] * (tt - e)
                a = ph[i, 1] + rot[i] * tt
                f = math.cos(ph[i, 2] + 7 * tt)
                shade = 0.72 + 0.28 * abs(f)
                col = tuple(v * shade for v in cols[i])
                if kind == "heart":
                    spr = fx.heart(max(int(sz[i]), 4), fx._q(0.4 * math.sin(a)))
                elif kind == "star":
                    spr = fx.star5(max(int(sz[i]), 4), fx._q(a))
                else:
                    spr = fx.confetti(max(int(sz[i]), 4), aspect[i], a, f)
                c.splat(spr, x, y, col, fade)
            return c
        return frame
    return make


BURST_TAGS = ["confeti", "explosion", "burst", "cañon", "sorpresa", "fiesta", "celebracion", "transicion"]
design("cel-confeti-explosion", "Explosión de confeti", "Confetti burst", "celebracion", 4, loop=False, thumb_at=0.32,
       tags=BURST_TAGS + ["cumpleaños"], sample="birthday-05.jpg")(_burst_f(PARTY))
design("cel-explosion-dorada", "Explosión dorada", "Gold burst", "celebracion", 4, loop=False, thumb_at=0.32,
       tags=BURST_TAGS + ["dorado", "gold", "año nuevo", "graduacion"], sample="graduation-04.jpg")(
    _burst_f(GOLD + [(0.95, 0.95, 1)]))
design("cel-explosion-centro", "Explosión al centro", "Centre burst", "celebracion", 3.5, loop=False, thumb_at=0.22,
       tags=BURST_TAGS + ["centro", "revelacion", "reveal"], sample="pregnant-02.jpg")(_burst_f(PARTY, "center", n=240))
design("cel-confeti-desde-arriba", "Confeti desde arriba", "Confetti from above", "celebracion", 4, loop=False,
       thumb_at=0.35, tags=BURST_TAGS + ["arriba", "caida"], sample="birthday-06.jpg")(_burst_f(PARTY, "top"))
design("cel-explosion-estrellas", "Explosión de estrellas", "Star burst", "celebracion", 3.5, loop=False, thumb_at=0.25,
       tags=BURST_TAGS + ["estrellas", "stars", "premio", "logro"], sample="graduation-03.jpg")(
    _burst_f(GOLD, "center", "star", n=120))
design("amor-explosion-corazones", "Explosión de corazones", "Heart burst", "amor", 3.5, loop=False, thumb_at=0.25,
       tags=["corazones", "explosion", "burst", "amor", "love", "propuesta", "boda", "sorpresa"], sample="couple-01.jpg")(
    _burst_f(REDS, "center", "heart", n=110))


def _fireworks_f(palette_pool, k=6, pn=80, scale=1.0):
    def make(w, h, T, rng):
        s = w / 1080 * scale
        starts = np.arange(k) * T / k + rng.uniform(0, 0.4, k)
        centers = np.c_[rng.uniform(0.2, 0.8, k) * w, rng.uniform(0.12, 0.45, k) * h]
        palettes = [palette_pool[i % len(palette_pool)] for i in rng.permutation(max(k, len(palette_pool)))[:k]]
        dirs = [rng.uniform(0, TAU, pn) for _ in range(k)]
        spds = [rng.uniform(0.7, 1.0, pn) * 520 * s for _ in range(k)]
        rocket, life = 0.7, 2.2
        g = 160 * s

        def pos(i, j, a):
            e = (1 - math.exp(-2.2 * a)) / 2.2
            return (centers[i, 0] + math.cos(dirs[i][j]) * spds[i][j] * e,
                    centers[i, 1] + math.sin(dirs[i][j]) * spds[i][j] * e + 0.5 * g * a * a)

        def frame(t):
            c = Canvas(w, h)
            for i in range(k):
                age = (t - starts[i]) % T
                col = palettes[i]
                if age < rocket:
                    p = age / rocket
                    x = centers[i, 0]
                    y = h + 20 * s - (h + 20 * s - centers[i, 1]) * fx.ease_out(p)
                    c.splat(fx.streak_at(90 * s, 4 * s, math.pi), x, y + 30 * s, (1, 0.9, 0.7), 0.6, add=True)
                    c.splat(fx.glow(int(10 * s) + 1), x, y, (1, 0.95, 0.8), 0.9, add=True)
                    continue
                a = age - rocket
                if a > life:
                    continue
                fade = (1 - a / life) ** 1.5
                if a < 0.15:
                    c.splat(fx.glow(int(120 * s)), centers[i, 0], centers[i, 1], col, 0.6 * (1 - a / 0.15), add=True)
                for j in range(pn):
                    for trail in range(4):
                        ta = a - trail * 0.05
                        if ta < 0:
                            break
                        x, y = pos(i, j, ta)
                        tw = 0.6 + 0.4 * math.sin(40 * a + j)
                        c.splat(fx.glow(max(int((9 - trail * 1.6) * s), 1) + 1), x, y, col,
                                fade * tw * (1 - trail * 0.22), add=True)
            return c
        return frame
    return make


FW_TAGS = ["fuegos artificiales", "fireworks", "año nuevo", "new year", "fiesta", "celebracion", "noche"]
design("cel-fuegos-artificiales", "Fuegos artificiales", "Fireworks", "celebracion", 8, res=(540, 960),
       tags=FW_TAGS, sample="newyear-04.jpg")(_fireworks_f(PARTY))
design("cel-fuegos-dorados", "Fuegos artificiales dorados", "Gold fireworks", "celebracion", 8, res=(540, 960),
       tags=FW_TAGS + ["dorado", "gold", "elegante"], sample="newyear-03.jpg")(
    _fireworks_f([GOLD[0], GOLD[2], GOLD[1], (1, 1, 1)]))
design("cel-fuegos-final", "Gran final de fuegos", "Fireworks finale", "celebracion", 6, res=(540, 960),
       tags=FW_TAGS + ["final", "finale", "muchos"], sample="newyear-05.jpg")(_fireworks_f(PARTY, k=12, pn=70))
design("cel-fuegos-lejanos", "Fuegos lejanos", "Distant fireworks", "celebracion", 8, res=(540, 960),
       tags=FW_TAGS + ["lejos", "distant", "ciudad"], sample="fashion-01.jpg")(_fireworks_f(PARTY, k=8, pn=50, scale=0.55))


def _balloons_f(palette, shape="round", n=14):
    def make(w, h, T, rng):
        s = w / 1080
        x0, y0 = rng.uniform(0.05, 0.95, n) * w, rng.uniform(0, 1, n) * h
        sz = rng.uniform(110, 190, n) * s
        cols = [palette[i] for i in rng.integers(0, len(palette), n)]
        ph = rng.uniform(0, TAU, n)
        m = 520 * s

        def frame(t):
            u = t / T
            c = Canvas(w, h)
            for i in np.argsort(sz):
                y = wrap(y0[i] - (h + 2 * m) * u, -m, h + m)
                x = x0[i] + 35 * s * math.sin(TAU * u + ph[i])
                body, string, hi = balloon_parts(int(sz[i]), shape)
                yc = y + body.shape[0] / 2 - sz[i] * 0.6
                c.splat(string, x, yc, (0.85, 0.85, 0.88), 0.8)
                c.splat(body, x, yc, cols[i], 0.97)
                c.splat(fx.glow(int(sz[i] * 0.3)), x - sz[i] * 0.18, y - sz[i] * 0.25, (1, 1, 1), 0.18, add=True)
                c.splat(hi, x, yc, (1, 1, 1), 0.5)
            return c
        return frame
    return make


BAL_TAGS = ["globos", "balloons", "cumpleaños", "birthday", "fiesta", "celebracion"]
design("cel-globos", "Globos", "Balloons", "celebracion", 10, tags=BAL_TAGS + ["infantil"], sample="birthday-01.jpg")(
    _balloons_f(PARTY[:6]))
design("cel-globos-dorados", "Globos dorados y plateados", "Gold and silver balloons", "celebracion", 10,
       tags=BAL_TAGS + ["dorado", "plateado", "elegante", "aniversario"], sample="birthday-07.jpg")(
    _balloons_f([GOLD[1], GOLD[0], SILVER[0], SILVER[1]]))
design("cel-globos-pastel", "Globos pastel", "Pastel balloons", "celebracion", 10,
       tags=BAL_TAGS + ["pastel", "baby shower", "bebe"], sample="baby-01.jpg")(_balloons_f(PASTEL))
design("amor-globos-corazon", "Globos de corazón", "Heart balloons", "amor", 10,
       tags=["globos", "corazon", "heart balloons", "amor", "san valentin", "aniversario", "propuesta"],
       sample="couple-05.jpg")(_balloons_f([REDS[0], REDS[3], REDS[1]], shape="heart", n=12))


def _rain_of(kind, n, palette, size, laps=(1, 2), spin=(1, 2)):
    """Falling multi-colour objects: coins, bills, gifts, emoji faces, streamers."""
    def make(w, h, T, rng):
        s = w / 1080
        x0, y0 = rng.uniform(0, w, n), rng.uniform(0, h, n)
        lp = rng.integers(laps[0], laps[1] + 1, n)
        ph = rng.uniform(0, TAU, (n, 3))
        rot = rng.integers(spin[0], spin[1] + 1, n) * rng.choice([-1, 1], n)
        flip = rng.integers(1, 4, n)
        sz = rng.uniform(size[0], size[1], n) * s
        faces = ["smile", "love", "laugh", "wow", "cool"]
        cols = [palette[i] for i in rng.integers(0, len(palette), n)]
        m = size[1] * s

        def frame(t):
            u = t / T
            c = Canvas(w, h)
            for i in range(n):
                y = wrap(y0[i] + lp[i] * (h + 2 * m) * u, -m, h + m)
                x = x0[i] + 40 * s * math.sin(TAU * u + ph[i, 0])
                a = ph[i, 1] + TAU * rot[i] * u
                f = math.cos(TAU * flip[i] * u + ph[i, 2])
                k = max(int(sz[i]), 8)
                if kind == "coin":
                    body, rim, mark = coin(k, fx._q(a * 0.3), fx._qs(f))
                    shade = 0.75 + 0.25 * abs(f)
                    c.splat(body, x, y, tuple(v * shade for v in fx.hex_rgb("#f5c542")))
                    c.splat(rim, x, y, fx.hex_rgb("#c8901a"))
                    c.splat(mark, x, y, fx.hex_rgb("#fff0b0"), 0.8 * abs(f))
                elif kind == "bill":
                    body, inner, seal = bill(k, fx._q(a * 0.25), fx._qs(f))
                    c.splat(body, x, y, fx.hex_rgb("#5fbf6b"))
                    c.splat(inner, x, y, fx.hex_rgb("#2f7a3a"))
                    c.splat(seal, x, y, fx.hex_rgb("#d9f2c8"), 0.85)
                elif kind == "gift":
                    box, ribbon = gift(k, fx._q(0.5 * math.sin(a)))
                    c.splat(box, x, y, cols[i])
                    c.splat(ribbon, x, y, (1, 0.92, 0.5) if cols[i] != GOLD[1] else (1, 1, 1))
                elif kind == "emoji":
                    face, ink, red = emoji(k, faces[i % len(faces)], fx._q(0.4 * math.sin(a)))
                    c.splat(face, x, y, fx.hex_rgb("#ffcc33"))
                    c.splat(ink, x, y, fx.hex_rgb("#5a3a12"))
                    c.splat(red, x, y, fx.hex_rgb("#ff2b4b"))
                elif kind == "streamer":
                    c.splat(streamer(k, fx._q(a * 0.3), int(u * 16 + i) % 8), x, y, cols[i])
            return c
        return frame
    return make


design("cel-lluvia-monedas", "Lluvia de monedas", "Coin rain", "celebracion", 6,
       tags=["monedas", "coins", "dinero", "money", "ganar", "premio", "negocio", "ofertas"], sample="shopping-01.jpg")(
    _rain_of("coin", 45, GOLD, (60, 110)))
design("cel-lluvia-billetes", "Lluvia de billetes", "Money rain", "celebracion", 6,
       tags=["billetes", "dinero", "money", "rico", "ganar", "negocio", "ventas", "exito"], sample="office-02.jpg")(
    _rain_of("bill", 40, GOLD, (120, 190)))
design("cel-lluvia-regalos", "Lluvia de regalos", "Gift rain", "celebracion", 6,
       tags=["regalos", "gifts", "navidad", "cumpleaños", "sorteo", "giveaway", "premio"], sample="christmas-06.jpg")(
    _rain_of("gift", 26, [REDS[0], fx.hex_rgb("#2fa84f"), fx.hex_rgb("#3d7bff"), GOLD[1], fx.hex_rgb("#b26bff")],
             (80, 130)))
design("cel-lluvia-emojis", "Lluvia de emojis", "Emoji rain", "celebracion", 6,
       tags=["emojis", "caritas", "felicidad", "humor", "divertido", "reaccion", "risa"], sample="friends-05.jpg")(
    _rain_of("emoji", 30, GOLD, (70, 120)))
design("cel-serpentinas", "Serpentinas", "Streamers", "celebracion", 6,
       tags=["serpentinas", "streamers", "fiesta", "carnaval", "cumpleaños", "celebracion"], sample="birthday-04.jpg")(
    _rain_of("streamer", 34, PARTY[:6], (90, 150)))


@design("cel-purpurina", "Purpurina", "Glitter", "celebracion", 6,
        tags=["purpurina", "glitter", "brillo", "dorado", "fiesta", "elegante", "belleza"], sample="quince-08.jpg")
def _glitter(w, h, T, rng):
    s = w / 1080
    n = 260
    x0, y0 = rng.uniform(0, w, n), rng.uniform(0, h, n)
    laps = rng.integers(1, 3, n)
    ph = rng.uniform(0, TAU, n)
    tw = rng.integers(3, 8, n)
    sz = rng.uniform(5, 11, n) * s
    cols = [(GOLD + [(0.95, 0.95, 1.0), fx.hex_rgb("#ffb0d8")])[i] for i in rng.integers(0, 7, n)]

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        for i in range(n):
            y = wrap(y0[i] + laps[i] * h * u, 0, h)
            x = x0[i] + 15 * s * math.sin(TAU * u + ph[i])
            b = max(0.0, math.sin(TAU * tw[i] * u + ph[i]))
            c.splat(fx.disc(max(int(sz[i] / 2), 1)), x, y, cols[i], 0.85)
            if b > 0.75:
                c.splat(fx.sparkle(int(sz[i] * 4)), x, y, (1, 1, 1), (b - 0.75) * 4, add=True)
        return c
    return frame


# ================================================================ Amor

def _hearts_f(palette, style="solid", n=34, size=(34, 100), rising=True, sparkle=False):
    def make(w, h, T, rng):
        s = w / 1080
        x0, y0 = rng.uniform(0.03, 0.97, n) * w, rng.uniform(0, h, n)
        sz = rng.uniform(size[0], size[1], n) * s
        laps = rng.integers(1, 3, n)
        sway = rng.uniform(20, 60, n) * s
        ph = rng.uniform(0, TAU, n)
        cols = [palette[i] for i in rng.integers(0, len(palette), n)]
        m = size[1] * s * 1.2

        def frame(t):
            u = t / T
            c = Canvas(w, h)
            for i in np.argsort(sz):
                dy = (h + 2 * m) * u * laps[i]
                y = wrap(y0[i] + (-dy if rising else dy), -m, h + m)
                x = x0[i] + sway[i] * math.sin(TAU * 2 * u + ph[i])
                tilt = 0.25 * math.sin(TAU * 2 * u + ph[i] + 1)
                fade = fx.smooth(-m, h * 0.25, y) if rising else 1.0
                k = int(sz[i])
                if style == "outline":
                    c.splat(heart_outline(k, fx._q(tilt)), x, y, cols[i], 0.95 * fade)
                elif style == "neon":
                    c.splat(neon_heart(k, fx._q(tilt)), x, y, cols[i], 0.9 * fade,
                            add=True)
                    c.splat(heart_outline(k, fx._q(tilt), 0.05), x, y, (1, 1, 1), 0.9 * fade)
                else:
                    c.splat(fx.heart(k, fx._q(tilt)), x, y, cols[i], 0.92 * fade)
                    c.splat(fx.glow(int(k * 0.22)), x - k * 0.18, y - k * 0.18, (1, 1, 1), 0.3 * fade, add=True)
                if sparkle and (i + int(u * 24)) % 5 == 0:
                    c.splat(fx.sparkle(int(k * 0.7)), x + k * 0.3, y - k * 0.3, (1, 1, 1), 0.9 * fade, add=True)
            return c
        return frame
    return make


AMOR = ["corazones", "hearts", "amor", "love", "san valentin", "valentine", "pareja", "romantico"]
design("amor-corazones", "Corazones flotando", "Floating hearts", "amor", 8, tags=AMOR, sample="couple-01.jpg")(
    _hearts_f(REDS))
design("amor-corazones-rojos", "Corazones rojos", "Red hearts", "amor", 8, tags=AMOR + ["rojo"], sample="couple-03.jpg")(
    _hearts_f([fx.hex_rgb("#e8174f"), fx.hex_rgb("#c8102e"), fx.hex_rgb("#ff2b4b")], n=28, size=(50, 120)))
design("amor-corazones-contorno", "Corazones de contorno", "Outline hearts", "amor", 8,
       tags=AMOR + ["contorno", "outline", "minimal", "blanco"], sample="couple-06.jpg")(
    _hearts_f([(1, 1, 1), fx.hex_rgb("#ffc2d6")], style="outline", n=26, size=(50, 120)))
design("amor-corazones-brillo", "Corazones con brillo", "Sparkly hearts", "amor", 8,
       tags=AMOR + ["brillo", "sparkle", "glitter", "quince"], sample="quince-06.jpg")(
    _hearts_f(REDS, sparkle=True))
design("amor-corazones-neon", "Corazones de neón", "Neon hearts", "amor", 8,
       tags=AMOR + ["neon", "luces", "noche", "aesthetic"], sample="couple-08.jpg")(
    _hearts_f([fx.hex_rgb("#ff2fb3"), fx.hex_rgb("#ff4d6d")], style="neon", n=18, size=(70, 150)))
design("amor-lluvia-corazones", "Lluvia de corazones", "Falling hearts", "amor", 8,
       tags=AMOR + ["lluvia", "caida", "falling"], sample="wedding-05.jpg")(
    _hearts_f(REDS + [(1, 1, 1)], n=50, size=(26, 70), rising=False))


@design("amor-likes", "Corazones de transmisión", "Live likes", "amor", 6,
        tags=AMOR + ["likes", "live", "en vivo", "me gusta", "redes", "transmision", "tiktok"], sample="creator-01.jpg")
def _likes(w, h, T, rng):
    s = w / 1080
    n = 40
    born = np.sort(rng.uniform(0, 1, n))
    drift = rng.uniform(-160, 60, n) * s
    wob = rng.uniform(30, 70, n) * s
    ph = rng.uniform(0, TAU, n)
    sz = rng.uniform(60, 100, n) * s
    cols = [fx.hex_rgb(c) for c in ("#ff2b4b", "#ff6f91", "#ffb800", "#b26bff", "#3ec1ff", "#ff8c42")]
    ox, oy = w - 150 * s, h - 260 * s
    life = 0.45

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        for i in range(n):
            age = (u - born[i]) % 1.0
            if age > life:
                continue
            p = age / life
            x = ox + drift[i] * p + wob[i] * math.sin(TAU * 1.5 * p + ph[i])
            y = oy - 900 * s * p
            pop = min(p / 0.08, 1)
            op = (1 - p) ** 0.8
            k = int(sz[i] * (0.4 + 0.6 * pop))
            c.splat(fx.heart(k), x, y, cols[i % len(cols)], op)
            c.splat(fx.glow(int(k * 0.2)), x - k * 0.18, y - k * 0.18, (1, 1, 1), 0.35 * op, add=True)
        return c
    return frame


@design("amor-marco-corazones", "Marco de corazones", "Heart frame", "amor", 4,
        tags=AMOR + ["marco", "frame", "borde", "border"], sample="couple-02.jpg")
def _heart_frame(w, h, T, rng):
    s = w / 1080
    pts = []
    step = 120 * s
    for x in np.arange(60 * s, w - 40 * s, step):
        pts += [(x, 70 * s), (x, h - 70 * s)]
    for y in np.arange(70 * s + step, h - 70 * s, step):
        pts += [(60 * s, y), (w - 60 * s, y)]
    ph = rng.uniform(0, TAU, len(pts))
    cols = [REDS[i % len(REDS)] for i in range(len(pts))]

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        for i, (x, y) in enumerate(pts):
            beat = 0.82 + 0.18 * max(0.0, math.sin(TAU * 2 * u + ph[i] * 0.3)) ** 4
            k = int(78 * s * beat)
            c.splat(fx.heart(k), x, y, cols[i], 0.95)
            c.splat(fx.glow(int(k * 0.2)), x - k * 0.18, y - k * 0.18, (1, 1, 1), 0.3, add=True)
        return c
    return frame


design("amor-petalos-blancos", "Pétalos blancos", "White petals", "amor", 8,
       tags=["petalos", "blancos", "white", "boda", "wedding", "novia", "elegante", "flores"], sample="wedding-06.jpg")(
    _falling("petal", 55, [fx.hex_rgb(c) for c in ("#ffffff", "#fff6ee", "#f4ece6")], (40, 70), (1, 1), sway=90))
design("amor-petalos-rosa", "Pétalos rosa claro", "Blush petals", "amor", 8,
       tags=["petalos", "rosa", "blush", "boda", "quince", "romantico", "flores"], sample="quince-07.jpg")(
    _falling("petal", 55, [fx.hex_rgb(c) for c in ("#ffc2d6", "#ffb0c8", "#ffe0ea", "#ff9ec0")], (40, 70), (1, 1),
             sway=90))
