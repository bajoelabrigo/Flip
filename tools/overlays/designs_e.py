"""Fifth batch: weather and nature."""

from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import fx
from fx import TAU, Canvas
from designs import _falling, design, wrap

CLIMA = ["clima", "weather", "naturaleza", "nature"]


def _rain_f(n, laps, length, op, angle=10, lightning=False):
    def make(w, h, T, rng):
        s = w / 1080
        x0, y0 = rng.uniform(-0.2, 1.1, n) * w, rng.uniform(0, h, n)
        lp = rng.integers(laps[0], laps[1] + 1, n)
        ln = rng.uniform(length[0], length[1], n) * s
        o = rng.uniform(op[0], op[1], n)
        ang = math.radians(angle)
        flashes = [T * 0.3, T * 0.32, T * 0.78] if lightning else []

        def frame(t):
            u = t / T
            c = Canvas(w, h)
            for f in flashes:
                d = t - f
                if 0 <= d < 0.25:
                    c.fill((0.92, 0.95, 1.0), 0.75 * (1 - d / 0.25) ** 2)
            for i in range(n):
                m = ln[i]
                y = wrap(y0[i] + lp[i] * (h + 2 * m) * u, -m, h + m)
                x = x0[i] - math.tan(ang) * (y - y0[i])
                c.splat(fx.streak_at(ln[i], 2.6 * s, -ang), x, y, (0.85, 0.9, 1.0), o[i])
            return c
        return frame
    return make


design("clima-lluvia-ligera", "Llovizna", "Drizzle", "clima", 4,
       tags=CLIMA + ["llovizna", "lluvia", "drizzle", "rain", "calma", "nostalgia"], sample="fashion-01.jpg")(
    _rain_f(180, (3, 5), (50, 110), (0.25, 0.5), angle=6))
design("clima-tormenta", "Tormenta", "Thunderstorm", "clima", 4,
       tags=CLIMA + ["tormenta", "storm", "rayos", "relampago", "lluvia", "dramatico", "terror"], sample="cusco-04.jpg")(
    _rain_f(520, (5, 8), (70, 170), (0.25, 0.55), angle=14, lightning=True))


def _bolt_points(rng, x0, y0, x1, y1, depth):
    pts = [(x0, y0), (x1, y1)]
    for _ in range(depth):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            L = math.dist(a, b)
            mx += rng.normal(0, L * 0.18)
            out += [(mx, my), b]
        pts = out
    return pts


@design("clima-relampago", "Relámpago", "Lightning strike", "clima", 1.5, loop=False, res=(540, 960), thumb_at=0.08,
        tags=CLIMA + ["relampago", "rayo", "lightning", "tormenta", "impacto", "poder", "transicion"], sample="man-05.jpg")
def _strike(w, h, T, rng):
    s = w / 1080
    main = _bolt_points(rng, w * 0.62, -10, w * 0.38, h * 0.85, 6)
    branches = []
    for k in (12, 22, 34):
        bx, by = main[k]
        branches.append(_bolt_points(rng, bx, by, bx + rng.uniform(-0.3, 0.3) * w, by + rng.uniform(0.15, 0.3) * h, 4))
    im = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(im)
    d.line(main, fill=255, width=max(int(7 * s), 2), joint="curve")
    for b in branches:
        d.line(b, fill=200, width=max(int(3 * s), 1), joint="curve")
    core = np.asarray(im, np.float32) / 255
    glow = np.asarray(im.filter(ImageFilter.GaussianBlur(18 * s)), np.float32) / 255

    def frame(t):
        k = 1.0 if t < 0.12 else (0.6 if 0.18 < t < 0.26 else max(0.0, 1 - (t - 0.26) / 0.6) * 0.5)
        c = Canvas(w, h)
        c.fill((0.85, 0.9, 1.0), (0.55 if t < 0.1 else 0.0) + 0.0)
        c.fill(fx.hex_rgb("#9fc4ff"), np.clip(glow * 2.5, 0, 1) * k)
        c.fill((1, 1, 1), core * k)
        return c
    return frame


@design("clima-gotas-cristal", "Gotas en el cristal", "Raindrops on glass", "clima", 6,
        tags=CLIMA + ["gotas", "cristal", "ventana", "window", "lluvia", "melancolia", "triste"], sample="diwali-01.jpg")
def _glass(w, h, T, rng):
    s = w / 1080
    n = 170
    xs, ys = rng.uniform(0, w, n), rng.uniform(0, h, n)
    r = rng.gamma(2.0, 9.0, n) * s + 5 * s
    sliders = 6
    sx = rng.uniform(0.05, 0.95, sliders) * w
    sph = rng.uniform(0, 1, sliders)

    @lru_cache(maxsize=128)
    def drop(rad):
        rad = max(rad, 2)
        y, x = np.mgrid[-rad - 2:rad + 3, -rad - 2:rad + 3].astype(np.float32)
        d = np.sqrt(x * x + (y * 1.1) ** 2) / rad
        body = np.clip((1 - d) * rad / 1.2, 0, 1)
        rim = np.clip(1 - np.abs(d - 0.85) * 6, 0, 1) * body
        hi = np.exp(-(((x + rad * 0.35) ** 2 + (y + rad * 0.4) ** 2) / (2 * (rad * 0.18) ** 2)))
        return (body * 0.3 + rim * 0.5).astype(np.float32), (hi * body).astype(np.float32)

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        c.fill((0.75, 0.8, 0.88), 0.08)
        for i in range(n):
            body, hi = drop(int(r[i]))
            c.splat(body, xs[i], ys[i], (0.1, 0.12, 0.16), 1)
            c.splat(hi, xs[i], ys[i], (1, 1, 1), 0.9)
        for k in range(sliders):
            p = (u + sph[k]) % 1.0
            y = -40 * s + (h + 80 * s) * p ** 1.4
            body, hi = drop(int(14 * s))
            trail = np.zeros((h, w), np.float32)
            x0 = int(sx[k])
            y_top = max(int(y - 260 * s), 0)
            if int(y) > y_top:
                trail[y_top:int(y), max(x0 - int(3 * s), 0):x0 + int(3 * s)] = 0.12
            c.fill((0.1, 0.12, 0.16), trail)
            c.splat(body, sx[k], y, (0.1, 0.12, 0.16), 1)
            c.splat(hi, sx[k], y, (1, 1, 1), 0.9)
        return c
    return frame


@lru_cache(maxsize=512)
def _flake(size, qa):
    n = size * 4
    im = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(im)
    c = n / 2
    lw = max(int(n * 0.045), 2)
    for k in range(6):
        a = k / 6 * TAU + qa / fx.ANGLES * TAU
        ex, ey = c + math.cos(a) * n * 0.46, c + math.sin(a) * n * 0.46
        d.line([(c, c), (ex, ey)], fill=255, width=lw)
        for f in (0.45, 0.7):
            bx, by = c + math.cos(a) * n * 0.46 * f, c + math.sin(a) * n * 0.46 * f
            for side in (-1, 1):
                b = a + side * 0.7
                L = n * 0.14 * (1.2 - f)
                d.line([(bx, by), (bx + math.cos(b) * L, by + math.sin(b) * L)], fill=255, width=lw)
    return np.asarray(im.resize((size, size), Image.LANCZOS), np.float32) / 255


@design("clima-copos", "Copos de nieve", "Snowflakes", "clima", 8,
        tags=CLIMA + ["copos", "snowflakes", "nieve", "invierno", "navidad", "frio"], sample="christmas-05.jpg")
def _flakes(w, h, T, rng):
    s = w / 1080
    n = 40
    x0, y0 = rng.uniform(0, w, n), rng.uniform(0, h, n)
    sz = rng.uniform(40, 120, n) * s
    ph = rng.uniform(0, TAU, n)
    spin = rng.choice([-1, 1], n)
    m = 130 * s

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        for i in np.argsort(sz):
            y = wrap(y0[i] + (h + 2 * m) * u, -m, h + m)
            x = x0[i] + 50 * s * math.sin(TAU * u + ph[i])
            spr = _flake(int(sz[i]), fx._q(ph[i] + spin[i] * TAU * u / 3))
            c.splat(fx.glow(int(sz[i] * 0.4)), x, y, (0.85, 0.93, 1), 0.25, add=True)
            c.splat(spr, x, y, (1, 1, 1), 0.92)
        return c
    return frame


def _smoke(ramp_hexes, base="bottom", strength=0.95, speed=1.0):
    def make(w, h, T, rng):
        t1 = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.0)
        t2 = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.3)
        hue = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.6)
        yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        pal = np.array([fx.hex_rgb(c) for c in ramp_hexes], np.float32)
        grad = fx.smooth(-0.25, 0.85, yy) if base == "bottom" else fx.smooth(0.3, 0.95, yy)

        def field(tt):
            a = fx.sample_tile(t1, w, h, 30 + 8 * tt, 60 * tt * speed, 1.0)
            b = fx.sample_tile(t2, w, h, 200 - 12 * tt, 35 * tt * speed, 0.7)
            return np.clip(((a * 0.6 + b * 0.4) - 0.3) * 2.6, 0, 1) * grad

        def frame(t):
            wgt = t / T
            f = field(t) * (1 - wgt) + field(t - T) * wgt
            hv = fx.sample_tile(hue, w, h, 10 * t, 20 * t, 0.6)
            idx = np.clip(hv, 0, 0.999) * (len(pal) - 1)
            lo = np.floor(idx).astype(int)
            fr = (idx - lo)[..., None]
            col = pal[lo] * (1 - fr) + pal[np.minimum(lo + 1, len(pal) - 1)] * fr
            c = Canvas(w, h)
            c.layer(col.astype(np.float32), (f * strength).astype(np.float32))
            return c
        return frame
    return make


SMOKE = CLIMA + ["humo", "smoke", "bomba de humo", "color"]
design("clima-humo-rosa", "Humo rosa", "Pink smoke", "clima", 8, res=(270, 480),
       tags=SMOKE + ["rosa", "pink", "revelacion", "gender reveal", "niña", "bebe"], sample="pregnant-03.jpg")(
    _smoke(("#ff6fb5", "#ff9ec7", "#ffc2d6")))
design("clima-humo-azul", "Humo azul", "Blue smoke", "clima", 8, res=(270, 480),
       tags=SMOKE + ["azul", "blue", "revelacion", "gender reveal", "niño", "bebe"], sample="pregnant-01.jpg")(
    _smoke(("#3d7bff", "#5fb0ff", "#9fd8ff")))
design("clima-humo-colores", "Humo de colores", "Colour smoke", "clima", 8, res=(270, 480),
       tags=SMOKE + ["colores", "holi", "festival", "arcoiris", "fiesta"], sample="friends-11.jpg")(
    _smoke(("#ff3d6e", "#ffb800", "#2fd06b", "#3d7bff", "#b26bff")))
design("clima-niebla-baja", "Niebla baja", "Low fog", "clima", 10, res=(270, 480),
       tags=CLIMA + ["niebla", "fog", "suelo", "misterio", "escenario", "baile", "sueño"], sample="dance-01.jpg")(
    _smoke(("#e8ecf2", "#ffffff", "#d8dde6"), base="low", strength=0.8, speed=0.3))
design("clima-polvo-viento", "Polvo en el viento", "Blowing dust", "clima", 6, res=(270, 480),
       tags=CLIMA + ["polvo", "arena", "desierto", "viento", "wind", "sand", "western"], sample="man-04.jpg")(
    _smoke(("#d8b080", "#f0d4a8", "#b08a5a"), base="bottom", strength=0.9, speed=0.25))

design("clima-hojas-verdes", "Hojas verdes", "Green leaves", "clima", 8,
       tags=CLIMA + ["hojas", "verdes", "leaves", "primavera", "verano", "bosque", "eco"], sample="garden-01.jpg")(
    _falling("leaf", 34, [fx.hex_rgb(c) for c in ("#3fa34d", "#6cc04a", "#2f7a3a", "#9fd36b")], (50, 90), (1, 1),
             sway=120, spin=(1, 2)))
design("clima-petalos-flores", "Pétalos de colores", "Colourful petals", "clima", 8,
       tags=CLIMA + ["petalos", "flores", "flowers", "primavera", "colores", "dia de la madre"], sample="flowers-02.jpg")(
    _falling("petal", 60, [fx.hex_rgb(c) for c in ("#ff6fa8", "#ffd23f", "#ffffff", "#ff8c42", "#c86bff")], (30, 55),
             (1, 1), sway=100, spin=(1, 2)))


@lru_cache(maxsize=256)
def _seed(size, qa):
    n = size * 4
    im = Image.new("L", (n, n), 0)
    d = ImageDraw.Draw(im)
    c = n / 2
    for k in range(18):
        a = k / 18 * TAU + qa / fx.ANGLES * TAU
        d.line([(c, c), (c + math.cos(a) * n * 0.42, c + math.sin(a) * n * 0.42)], fill=210, width=max(n // 90, 1))
        d.ellipse([c + math.cos(a) * n * 0.42 - n * 0.02, c + math.sin(a) * n * 0.42 - n * 0.02,
                   c + math.cos(a) * n * 0.42 + n * 0.02, c + math.sin(a) * n * 0.42 + n * 0.02], fill=255)
    d.line([(c, c), (c + n * 0.05, c + n * 0.45)], fill=255, width=max(n // 60, 1))
    return np.asarray(im.resize((size, size), Image.LANCZOS), np.float32) / 255


@design("clima-dientes-de-leon", "Dientes de león", "Dandelion seeds", "clima", 10,
        tags=CLIMA + ["dientes de leon", "dandelion", "deseo", "wish", "calma", "primavera", "suave"], sample="garden-03.jpg")
def _dandelion(w, h, T, rng):
    s = w / 1080
    n = 26
    x0, y0 = rng.uniform(0, w, n), rng.uniform(0, h, n)
    sz = rng.uniform(50, 110, n) * s
    ph = rng.uniform(0, TAU, (n, 2))
    m = 120 * s

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        for i in range(n):
            x = wrap(x0[i] + (w + 2 * m) * u, -m, w + m)
            y = y0[i] - 60 * s * math.sin(TAU * u + ph[i, 0]) + 30 * s * math.sin(TAU * 3 * u + ph[i, 1])
            c.splat(_seed(int(sz[i]), fx._q(0.3 * math.sin(TAU * u + ph[i, 1]))), x, y, (1, 1, 1), 0.9)
        return c
    return frame


@design("clima-noche-estrellada", "Noche estrellada", "Starry night", "clima", 8, res=(1080, 1920),
        tags=CLIMA + ["estrellas", "noche", "night sky", "cielo", "magia", "luna", "dormir"], sample="church-02.jpg")
def _starry(w, h, T, rng):
    s = w / 1080
    n = 260
    xs, ys = rng.uniform(0, w, n), rng.beta(1.2, 3.0, n) * h * 0.8
    r = rng.gamma(1.6, 2.2, n) * s + 1.5 * s
    ph = rng.uniform(0, TAU, n)
    k = rng.integers(1, 4, n)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None] * np.ones((1, w), np.float32)
    sky = fx.smooth(0.65, 0.0, yy) * 0.55

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        c.fill(fx.hex_rgb("#0b1440"), sky)
        for i in range(n):
            b = 0.55 + 0.45 * math.sin(TAU * k[i] * u + ph[i])
            c.splat(fx.glow(max(int(r[i] * 2), 2)), xs[i], ys[i], (0.85, 0.9, 1), 0.4 * b, add=True)
            c.splat(fx.disc(max(int(r[i] * 0.6), 1)), xs[i], ys[i], (1, 1, 1), b)
            if r[i] > 7 * s and b > 0.85:
                c.splat(fx.sparkle(int(r[i] * 6)), xs[i], ys[i], (1, 1, 1), (b - 0.85) * 6, add=True)
        return c
    return frame


@design("clima-arcoiris", "Arcoíris", "Rainbow", "clima", 5, res=(540, 960),
        tags=CLIMA + ["arcoiris", "rainbow", "lluvia", "esperanza", "orgullo", "colores", "cielo"], sample="nature-02.jpg")
def _rainbow(w, h, T, rng):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w * 0.5, h * 0.62
    R = w * 0.95
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    band = (d - R * 0.8) / (R * 0.2)
    inside = np.clip(1 - np.abs(band - 0.5) * 2, 0, 1) ** 0.6
    hue = np.clip(band, 0, 1) * 0.78
    lut = np.array([fx.hsv(0.78 - v, 0.8, 1.0) for v in np.linspace(0, 0.78, 256)], np.float32)
    col = lut[np.clip(hue / 0.78 * 255, 0, 255).astype(int)]
    angle = np.arctan2(cy - yy, xx - cx)   # 0 at right, pi at left

    def frame(t):
        u = t / T
        sweep = math.pi * fx.ease_out(min(u / 0.5, 1))   # draws from left to right
        shown = fx.smooth(math.pi - sweep - 0.15, math.pi - sweep + 0.15, angle)
        a = inside * shown * (yy < cy) * 0.5 * (0.9 + 0.1 * math.sin(TAU * u))
        c = Canvas(w, h)
        c.layer(col, a.astype(np.float32))
        return c
    return frame
