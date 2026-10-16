"""The overlays of Stock › Superposiciones. Each design is a function (w, h, T, rng) -> frame(t) -> Canvas.

`res` is the size the design draws at; build.py scales it to 1080 x 1920 when encoding (soft fields
such as light leaks and fog draw small, sharp particles draw full size). Sizes inside a design are
written for a 1080-wide frame and multiplied by `s`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageDraw

import fx
from fx import TAU, Canvas


@dataclass
class Design:
    id: str
    names: dict
    category: str
    seconds: float
    make: object
    loop: bool = True
    res: tuple = (1080, 1920)
    tags: list = field(default_factory=list)
    sample: str = "portrait-01.jpg"
    thumb_at: float = 0.5   # fraction of the duration used for the card


DESIGNS: dict[str, Design] = {}


def design(id, es, en, category, seconds, *, loop=True, res=(1080, 1920), tags=(), sample="portrait-01.jpg",
           thumb_at=0.5):
    def deco(fn):
        DESIGNS[id] = Design(id, {"es": es, "en": en}, category, seconds, fn, loop, res, list(tags), sample, thumb_at)
        return fn
    return deco


def wrap(v, lo, hi):
    return lo + (v - lo) % (hi - lo)


GOLD = [fx.hex_rgb(c) for c in ("#ffd27a", "#ffb84d", "#fff1c2", "#ffc060", "#ffe08a")]
PARTY = [fx.hex_rgb(c) for c in ("#ff4d6d", "#ffd23f", "#3ec1ff", "#7bf06a", "#b26bff", "#ff8c42", "#ffffff",
                                  "#ff6fd8")]


# ================================================================ Luces

def _leak(ramp, strength=1.0, bands=5, sweep=False, mode="edge"):
    """Film light leak: hot, almost white cores on an edge that fall off through the ramp colours
    (core -> fringe) to clean picture. `ramp` goes from the fringe colour to the core colour.
    mode: "edge" (left/right borders), "corner" (top corners, rounder), "flash" (one-shot: blooms over
    the frame and clears, a transition), or sweep=True (one pass from left to right)."""
    if sweep:
        mode = "sweep"
    def make(w, h, T, rng):
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        side = rng.choice([-1, 1], bands)
        fy = rng.integers(1, 3, bands)
        ph = rng.uniform(0, TAU, (bands, 3))
        sx = rng.uniform(0.09, 0.2, bands) * w       # narrow across
        sy = rng.uniform(0.18, 0.42, bands) * h      # tall: leaks are vertical bands
        wt = rng.uniform(0.55, 0.95, bands)
        pal = np.array(ramp, np.float32)

        def frame(t):
            u = t / T
            I = np.zeros((h, w), np.float32)
            for i in range(bands):
                if mode == "sweep":   # one pass across the frame
                    cx = w * (-0.4 + 1.8 * fx.ease_out(u) + 0.15 * i / bands)
                elif mode == "corner":
                    cx = w * (0.0 if side[i] < 0 else 1.0) - side[i] * w * 0.06 * math.sin(TAU * u + ph[i, 0])
                elif mode == "flash":
                    cx = w * (0.5 + 0.35 * side[i] * (0.4 + 0.6 * i / bands))
                else:
                    edge = 0.0 if side[i] < 0 else 1.0
                    cx = w * (edge - side[i] * (0.03 + 0.07 * math.sin(TAU * u + ph[i, 0])))
                cy = h * (0.5 + 0.4 * math.sin(TAU * fy[i] * u + ph[i, 1]))
                if mode == "corner":
                    cy = h * (0.04 + 0.1 * (0.5 + 0.5 * math.sin(TAU * fy[i] * u + ph[i, 1])))
                pulse = 0.75 + 0.25 * math.sin(TAU * 2 * u + ph[i, 2])
                gx, gy = (sx[i] * 1.8, sy[i] * 0.7) if mode == "corner" else (sx[i] * (2.2 if mode == "flash" else 1), sy[i])
                I += wt[i] * pulse * np.exp(-((xx - cx) ** 2) / (2 * gx ** 2) - ((yy - cy) ** 2) / (2 * gy ** 2))
            I *= strength
            if mode == "flash":
                I *= 2.6 * math.sin(math.pi * min(u, 1.0)) ** 1.5
            if mode == "sweep":
                I *= math.sin(math.pi * min(u * 1.05, 1.0)) ** 0.7 * 1.3
            v = np.clip(I, 0, 1.6) / 1.6
            idx = v * (len(pal) - 1)
            lo = np.floor(idx).astype(int)
            hi = np.minimum(lo + 1, len(pal) - 1)
            f = (idx - lo)[..., None]
            col = pal[lo] * (1 - f) + pal[hi] * f
            a = fx.smooth(0.03, 1.3, I) ** 0.8 * 0.88
            c = Canvas(w, h)
            c.layer(col.astype(np.float32), a.astype(np.float32))
            return c
        return frame
    return make


def ramp(*hexes):
    return [fx.hex_rgb(x) for x in hexes]


design("luz-fuga-calida", "Fuga de luz cálida", "Warm light leak", "luces", 6, res=(270, 480),
       tags=["luz", "light leak", "calido", "naranja", "pelicula", "vintage", "warm"], sample="couple-02.jpg")(
    _leak(ramp("#b3200a", "#ff5a14", "#ff9a2e", "#ffd27a", "#fff4dc")))
design("luz-fuga-rosa", "Fuga de luz rosa", "Pink light leak", "luces", 6, res=(270, 480),
       tags=["luz", "light leak", "rosa", "pink", "romantico", "sueño"], sample="portrait-03.jpg")(
    _leak(ramp("#7a1fd6", "#e0338f", "#ff6fa8", "#ffb6d2", "#fff0f6")))
design("luz-fuga-fria", "Fuga de luz fría", "Cool light leak", "luces", 6, res=(270, 480),
       tags=["luz", "light leak", "azul", "frio", "blue", "noche"], sample="city-02.jpg")(
    _leak(ramp("#2a1fb8", "#2f6bff", "#2fc6ff", "#9cf2ff", "#f0fdff")))
design("luz-arcoiris", "Luz arcoíris", "Rainbow light", "luces", 6, res=(270, 480),
       tags=["luz", "arcoiris", "rainbow", "prisma", "colores"], sample="friends-03.jpg")(
    _leak(ramp("#7b2bff", "#2f8bff", "#2fe0a0", "#ffe04a", "#ff7a3a", "#fff6e0"), bands=6))


@design("luz-destello", "Destello de lente", "Lens flare", "luces", 3, loop=False, res=(540, 960),
        tags=["destello", "flare", "lente", "lens", "sol", "transicion", "brillo"], sample="beach-02.jpg", thumb_at=0.45)
def _flare(w, h, T, rng):
    s = w / 1080
    warm = fx.hex_rgb("#ffd9a0")
    ghosts = [(-0.45, 60, "#7bd3ff", 0.18), (0.35, 40, "#b8ff9a", 0.16), (0.7, 110, "#ff9ad5", 0.12),
              (1.25, 70, "#ffd27a", 0.16), (1.6, 28, "#ffffff", 0.2)]
    yy = np.arange(h, dtype=np.float32)[:, None]
    xx = np.arange(w, dtype=np.float32)[None, :]

    def frame(t):
        u = t / T
        env = fx.envelope(t, 0.5, 2.2, 0.8)
        px = w * (-0.15 + 1.3 * u)
        py = h * (0.28 + 0.05 * math.sin(u * 3))
        c = Canvas(w, h)
        # wash, anamorphic streak, hot spot
        wash = np.exp(-((xx - px) ** 2 + (yy - py) ** 2) / (2 * (0.55 * w) ** 2)) * 0.45
        c.layer(np.broadcast_to(np.asarray(warm, np.float32), (h, w, 3)).copy(), (wash * env).astype(np.float32))
        streak = np.exp(-((yy - py) ** 2) / (2 * (5 * s + 1) ** 2)) * np.exp(-((xx - px) ** 2) / (2 * (0.5 * w) ** 2))
        c.layer(np.broadcast_to(np.asarray(fx.hex_rgb("#bfe4ff"), np.float32), (h, w, 3)).copy(),
                (np.clip(streak, 0, 1) * 0.8 * env).astype(np.float32))
        c.splat(fx.glow(int(160 * s)), px, py, warm, 0.8 * env, add=True)
        c.splat(fx.glow(int(50 * s)), px, py, (1, 1, 1), 1.0 * env, add=True)
        c.splat(fx.sparkle(int(260 * s)), px, py, (1, 1, 1), 0.9 * env, add=True)
        cx, cy = w / 2, h / 2
        for k, r, col, op in ghosts:
            gx, gy = px + (cx - px) * (1 + k), py + (cy - py) * (1 + k)
            c.splat(fx.bokeh(int(r * s * 2)), gx, gy, fx.hex_rgb(col), op * env, add=True)
        return c
    return frame


@design("luz-rayos", "Rayos de sol", "Sun rays", "luces", 8, res=(270, 480),
        tags=["rayos", "sol", "sun", "rays", "luz", "dios", "atardecer"], sample="nature-02.jpg")
def _rays(w, h, T, rng):
    ox, oy = -0.15 * w, -0.1 * h
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ang = np.arctan2(yy - oy, xx - ox)
    dist = np.sqrt((xx - ox) ** 2 + (yy - oy) ** 2) / h
    col = np.broadcast_to(np.asarray(fx.hex_rgb("#fff0c8"), np.float32), (h, w, 3)).copy()

    def frame(t):
        u = t / T
        r = (0.5 + 0.5 * np.sin(ang * 23 + TAU * u)) * (0.5 + 0.5 * np.sin(ang * 37 - TAU * 2 * u + 1.3))
        r = r ** 2.2 * (0.6 + 0.4 * np.sin(ang * 7 + TAU * u))
        fall = np.clip(1.15 - dist, 0, 1) ** 1.6
        a = np.clip(r * fall * 0.85 + fall * 0.12, 0, 1)
        c = Canvas(w, h)
        c.layer(col, a.astype(np.float32))
        return c
    return frame


def _bokeh(palette, n, rmin, rmax, opacity):
    def make(w, h, T, rng):
        s = w / 1080
        x0 = rng.uniform(0, w, n)
        y0 = rng.uniform(0, h, n)
        laps = rng.integers(0, 2, n) * 0 + 1
        sway = rng.uniform(10, 50, n) * s
        ph = rng.uniform(0, TAU, n)
        tw = rng.integers(1, 4, n)
        rad = rng.uniform(rmin, rmax, n) * s
        cols = [palette[i % len(palette)] for i in rng.integers(0, len(palette), n)]
        m = rmax * s * 1.2

        def frame(t):
            u = t / T
            c = Canvas(w, h)
            for i in np.argsort(rad)[::-1]:
                y = wrap(y0[i] - laps[i] * (h + 2 * m) * u, -m, h + m)
                x = x0[i] + sway[i] * math.sin(TAU * u + ph[i])
                op = opacity * (0.55 + 0.45 * math.sin(TAU * tw[i] * u + ph[i]))
                c.splat(fx.bokeh(int(rad[i])), x, y, cols[i], op, add=True)
            return c
        return frame
    return make


design("luz-bokeh-dorado", "Bokeh dorado", "Golden bokeh", "luces", 8, res=(540, 960),
       tags=["bokeh", "dorado", "gold", "luces", "desenfoque", "navidad", "elegante"], sample="couple-05.jpg")(
    _bokeh(GOLD, 38, 25, 95, 0.55))
design("luz-bokeh-color", "Bokeh de colores", "Colourful bokeh", "luces", 8, res=(540, 960),
       tags=["bokeh", "colores", "fiesta", "luces", "noche", "party"], sample="concert-01.jpg")(
    _bokeh(PARTY[:6], 42, 25, 90, 0.5))


@design("luz-luciernagas", "Luciérnagas", "Fireflies", "luces", 8, res=(540, 960),
        tags=["luciernagas", "fireflies", "magia", "noche", "bosque", "brillo"], sample="nature-04.jpg")
def _fireflies(w, h, T, rng):
    s = w / 1080
    n = 55
    cx, cy = rng.uniform(0, w, n), rng.uniform(h * 0.15, h, n)
    ax, ay = rng.uniform(30, 110, n) * s, rng.uniform(30, 110, n) * s
    fxs, fys = rng.integers(1, 3, n), rng.integers(1, 3, n)
    ph = rng.uniform(0, TAU, (n, 3))
    blink = rng.integers(1, 4, n)
    col = fx.hex_rgb("#e4ff8a")

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        for i in range(n):
            x = cx[i] + ax[i] * math.sin(TAU * fxs[i] * u + ph[i, 0])
            y = cy[i] + ay[i] * math.sin(TAU * fys[i] * u + ph[i, 1])
            b = max(0.0, math.sin(TAU * blink[i] * u + ph[i, 2])) ** 2
            c.splat(fx.glow(int(42 * s)), x, y, col, 0.45 * b, add=True)
            c.splat(fx.glow(int(9 * s)), x, y, (1, 1, 0.85), 0.95 * b, add=True)
        return c
    return frame


# ================================================================ Película y retro

@design("pel-polvo-rayas", "Polvo y rayas de película", "Film dust and scratches", "pelicula", 4, res=(1080, 1920),
        tags=["pelicula", "film", "polvo", "rayas", "dust", "scratches", "vintage", "antiguo", "retro"],
        sample="family-02.jpg")
def _dust(w, h, T, rng):
    fps = 30
    frames = int(T * fps)
    lines = [(rng.uniform(0.05, 0.95) * w, rng.uniform(0, frames), rng.uniform(8, 40)) for _ in range(6)]

    def frame(t):
        i = int(round(t * fps)) % frames
        r = np.random.default_rng(1000 + i)
        im = Image.new("L", (w, h), 0)
        dark = Image.new("L", (w, h), 0)
        d, dd = ImageDraw.Draw(im), ImageDraw.Draw(dark)
        for _ in range(r.integers(6, 16)):
            target = d if r.random() < 0.45 else dd
            x, y = r.uniform(0, w), r.uniform(0, h)
            for _ in range(r.integers(1, 4)):
                rr = r.uniform(1.5, 6)
                ox, oy = r.normal(0, 4, 2)
                target.ellipse([x + ox - rr, y + oy - rr, x + ox + rr, y + oy + rr], fill=int(r.uniform(140, 255)))
        if r.random() < 0.35:   # a hair
            target = d if r.random() < 0.5 else dd
            x, y = r.uniform(0, w), r.uniform(0, h)
            pts = [(x, y)]
            ang = r.uniform(0, TAU)
            for _ in range(14):
                ang += r.normal(0, 0.35)
                x += math.cos(ang) * 9
                y += math.sin(ang) * 9
                pts.append((x, y))
            target.line(pts, fill=200, width=2)
        for lx, start, life in lines:
            age = (i - start) % frames
            if age < life:
                x = lx + r.normal(0, 1.5)
                d.line([(x, 0), (x + r.normal(0, 3), h)], fill=int(r.uniform(60, 150)), width=int(r.integers(1, 3)))
        c = Canvas(w, h)
        c.image(dark, 0, 0, (0.05, 0.04, 0.03), 0.8)
        c.image(im, 0, 0, (1, 0.98, 0.93), 0.75)
        return c
    return frame


@design("pel-grano", "Grano de película", "Film grain", "pelicula", 2, res=(540, 960),
        tags=["grano", "grain", "pelicula", "film", "ruido", "noise", "cine", "analogico"], sample="portrait-05.jpg")
def _grain(w, h, T, rng):
    fps = 30
    frames = int(T * fps)

    def frame(t):
        i = int(round(t * fps)) % frames
        n = np.random.default_rng(5000 + i).standard_normal((h, w)).astype(np.float32)
        c = Canvas(w, h)
        light = np.clip(n, 0, None) * 0.11
        dark = np.clip(-n, 0, None) * 0.13
        c.layer(np.ones((h, w, 3), np.float32), np.clip(light, 0, 0.5))
        c.layer(np.zeros((h, w, 3), np.float32), np.clip(dark, 0, 0.5))
        return c
    return frame


@design("pel-quemado", "Quemado de película", "Film burn", "pelicula", 3.5, loop=False, res=(270, 480),
        tags=["quemado", "film burn", "pelicula", "transicion", "fuego", "flash", "vintage"], sample="friends-05.jpg",
        thumb_at=0.24)
def _burn(w, h, T, rng):
    tile = fx.tile_noise(512, 77, falloff=1.6)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    grad = (xx / w) * 0.55 + (1 - yy / h) * 0.25   # comes in from the right and the top
    ramp = np.array([fx.hex_rgb(c) for c in ("#3a0500", "#c41e00", "#ff6a00", "#ffb000", "#fff2c0", "#ffffff")],
                    np.float32)

    def frame(t):
        u = t / T
        n = fx.sample_tile(tile, w, h, 40 + 60 * u, 90, 0.9)
        level = 1.4 * math.sin(math.pi * min(u * 1.1, 1.0)) ** 1.3
        heat = np.clip(level - (1 - grad) - n * 0.6 + 0.35, 0, 1)
        idx = heat * (len(ramp) - 1)
        lo = np.floor(idx).astype(int)
        hi = np.minimum(lo + 1, len(ramp) - 1)
        f = (idx - lo)[..., None]
        col = ramp[lo] * (1 - f) + ramp[hi] * f
        a = np.clip(heat * 1.6, 0, 1)
        c = Canvas(w, h)
        c.layer(col, a.astype(np.float32))
        return c
    return frame


def _vhs_text(w, h, t, s, c):
    white = (0.96, 0.97, 1.0)
    shadow = (0, 0, 0)
    play = fx.text_image("PLAY", "VT323-Regular.ttf", int(84 * s))
    sp = fx.text_image("SP", "VT323-Regular.ttf", int(84 * s))
    secs = int(t)
    tc = fx.text_image(f"0:00:{secs:02d}", "VT323-Regular.ttf", int(84 * s))
    tri = Image.new("L", (int(54 * s), int(60 * s)), 0)
    ImageDraw.Draw(tri).polygon([(0, 0), (int(54 * s), int(30 * s)), (0, int(60 * s))], fill=255)
    for img, x, y in ((play, 80 * s, 110 * s), (tri, 80 * s + play.width + 24 * s, 122 * s),
                      (sp, w - 80 * s - sp.width, 110 * s), (tc, 80 * s, h - 200 * s)):
        c.image(img, int(x + 4 * s), int(y + 4 * s), shadow, 0.45)
        c.image(img, int(x), int(y), white, 0.92)


@design("pel-vhs", "VHS", "VHS", "pelicula", 6, res=(1080, 1920),
        tags=["vhs", "retro", "90s", "cinta", "tape", "glitch", "play", "noventas"], sample="friends-08.jpg")
def _vhs(w, h, T, rng):
    s = w / 1080
    scan = np.zeros((h, w), np.float32)
    scan[::4] = 0.14
    scan[1::4] = 0.07
    fps = 30
    frames = int(T * fps)

    def frame(t):
        u = t / T
        i = int(round(t * fps)) % frames
        r = np.random.default_rng(9000 + i)
        c = Canvas(w, h)
        c.layer(np.zeros((h, w, 3), np.float32), scan)
        tint = np.broadcast_to(np.asarray(fx.hex_rgb("#5a6bff"), np.float32), (h, w, 3)).copy()
        c.layer(tint, np.full((h, w), 0.05, np.float32))
        # tracking band rolling down once per loop
        band_y = int(wrap(h * u * 1.0, 0, h))
        band_h = int(70 * s)
        y0, y1 = max(band_y - band_h, 0), band_y
        if y1 > y0:
            noise = r.uniform(0, 1, (y1 - y0, w)).astype(np.float32)
            a = np.zeros((h, w), np.float32)
            a[y0:y1] = (noise > 0.55) * 0.55 * np.linspace(0.2, 1, y1 - y0)[:, None]
            c.layer(np.ones((h, w, 3), np.float32), a)
        for _ in range(r.integers(0, 3)):   # stray white lines
            y = int(r.uniform(0, h))
            a = np.zeros((h, w), np.float32)
            x0 = int(r.uniform(0, w * 0.7))
            a[y:y + 2, x0:x0 + int(r.uniform(80, 500) * s)] = 0.6
            c.layer(np.ones((h, w, 3), np.float32), a)
        _vhs_text(w, h, t, s, c)
        return c
    return frame


@design("cam-rec", "Cámara grabando (REC)", "Camera recording (REC)", "camara", 10, res=(1080, 1920),
        tags=["rec", "camara", "grabando", "camera", "recording", "visor", "vlog", "marco"], sample="creator-01.jpg")
def _rec(w, h, T, rng):
    s = w / 1080
    m, L, th = int(70 * s), int(130 * s), max(int(7 * s), 2)
    frame_img = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(frame_img)
    for (x, y, dx, dy) in ((m, m, 1, 1), (w - m, m, -1, 1), (m, h - m, 1, -1), (w - m, h - m, -1, -1)):
        d.line([(x, y), (x + dx * L, y)], fill=255, width=th)
        d.line([(x, y), (x, y + dy * L)], fill=255, width=th)
    cx, cy, k = w // 2, h // 2, int(34 * s)
    d.line([(cx - k, cy), (cx + k, cy)], fill=255, width=max(th // 2, 2))
    d.line([(cx, cy - k), (cx, cy + k)], fill=255, width=max(th // 2, 2))
    # battery
    bx, by, bw, bh = w - m - int(140 * s), h - m - int(110 * s), int(110 * s), int(50 * s)
    d.rectangle([bx, by, bx + bw, by + bh], outline=255, width=max(th // 2, 2))
    d.rectangle([bx + bw, by + bh // 3, bx + bw + int(10 * s), by + 2 * bh // 3], fill=255)
    for j in range(3):
        x = bx + int(10 * s) + j * int(32 * s)
        d.rectangle([x, by + int(10 * s), x + int(24 * s), by + bh - int(10 * s)], fill=255)
    hd = fx.text_image("4K  60", "VT323-Regular.ttf", int(70 * s))
    frame_img.paste(255, (m + int(30 * s), h - m - int(110 * s)), hd)
    rec = fx.text_image("REC", "VT323-Regular.ttf", int(90 * s))
    dot = fx.disc(int(22 * s))

    def frame(t):
        c = Canvas(w, h)
        c.image(frame_img, int(3 * s), int(3 * s), (0, 0, 0), 0.4)
        c.image(frame_img, 0, 0, (1, 1, 1), 0.92)
        on = (t % 1.0) < 0.6
        x0, y0 = m + int(40 * s), m + int(40 * s)
        if on:
            c.splat(dot, x0 + 22 * s, y0 + 45 * s, fx.hex_rgb("#ff2b2b"), 1.0)
        c.image(rec, int(x0 + 62 * s), int(y0), (1, 1, 1), 0.95)
        f = int(t * 30) % 30
        tc = fx.text_image(f"00:00:{int(t):02d}:{f:02d}", "VT323-Regular.ttf", int(80 * s))
        c.image(tc, int(w - m - 40 * s - tc.width + 3 * s), int(y0 + 3 * s), (0, 0, 0), 0.4)
        c.image(tc, int(w - m - 40 * s - tc.width), int(y0), (1, 1, 1), 0.95)
        return c
    return frame


# ================================================================ Partículas

def _rising(n, palette, size, speed_laps, life_frac, glow_r, streak_len, add=True, sway=40):
    """Particles born at the bottom that rise and fade: sparks, embers."""
    def make(w, h, T, rng):
        s = w / 1080
        x0 = rng.uniform(0.05, 0.95, n) * w
        ph = rng.uniform(0, 1, n)
        laps = rng.integers(speed_laps[0], speed_laps[1] + 1, n)
        rise = rng.uniform(0.45, 1.0, n) * h
        drift = rng.normal(0, 60, n) * s
        sw = rng.uniform(0, sway, n) * s
        flick = rng.integers(3, 9, n)
        cols = [palette[i] for i in rng.integers(0, len(palette), n)]
        sz = rng.uniform(0.6, 1.3, n)

        def frame(t):
            u = t / T
            c = Canvas(w, h)
            for i in range(n):
                age = (u * laps[i] + ph[i]) % 1.0
                x = x0[i] + drift[i] * age + sw[i] * math.sin(TAU * (age * 2 + ph[i]))
                y = h + 20 * s - rise[i] * fx.ease_out(age * 1.15) * 1.0
                fade = (1 - age) ** 1.4 * min(age * 8, 1)
                fl = 0.7 + 0.3 * math.sin(TAU * flick[i] * u + ph[i] * 9)
                if streak_len:
                    vx = drift[i] + sw[i] * TAU * 2 * math.cos(TAU * (age * 2 + ph[i]))
                    ang = math.atan2(-vx, rise[i])   # pointing along the motion
                    c.splat(fx.streak_at(streak_len * s * sz[i] * (1 - age * 0.6), 4 * s * sz[i], ang + math.pi),
                            x, y, cols[i], fade * fl, add=add)
                c.splat(fx.glow(int(glow_r * s * sz[i])), x, y, cols[i], 0.5 * fade * fl, add=add)
                c.splat(fx.glow(int(size * s * sz[i])), x, y, (1, 0.95, 0.8), fade * fl, add=add)
            return c
        return frame
    return make


design("part-chispas", "Chispas", "Sparks", "particulas", 6, res=(540, 960),
       tags=["chispas", "sparks", "fuego", "bengala", "energia", "fire"], sample="gym-02.jpg")(
    _rising(90, [fx.hex_rgb(c) for c in ("#ffb347", "#ff7a1a", "#ffd27a")], 5, (2, 3), 1, 22, 70, sway=30))
design("part-brasas", "Brasas", "Embers", "particulas", 8, res=(540, 960),
       tags=["brasas", "embers", "fuego", "fogata", "calido", "fire", "campfire"], sample="man-03.jpg")(
    _rising(70, [fx.hex_rgb(c) for c in ("#ff5a1a", "#ff8c2a", "#ffb000")], 6, (1, 2), 1, 30, 0, sway=60))


def _falling(kind, n, palette, size, laps_range, sway=60, opacity=1.0, spin=(1, 3)):
    def make(w, h, T, rng):
        s = w / 1080
        x0, y0 = rng.uniform(0, w, n), rng.uniform(0, h, n)
        laps = rng.integers(laps_range[0], laps_range[1] + 1, n)
        sw = rng.uniform(10, sway, n) * s
        swk = rng.integers(1, 3, n)
        ph = rng.uniform(0, TAU, (n, 3))
        rot = rng.integers(spin[0], spin[1] + 1, n) * rng.choice([-1, 1], n)
        flip = rng.integers(1, 4, n)
        sz = rng.uniform(size[0], size[1], n) * s
        cols = [palette[i] for i in rng.integers(0, len(palette), n)]
        aspect = rng.uniform(0.35, 0.7, n)
        m = size[1] * s * 1.5

        def frame(t):
            u = t / T
            c = Canvas(w, h)
            for i in range(n):
                y = wrap(y0[i] + laps[i] * (h + 2 * m) * u, -m, h + m)
                x = x0[i] + sw[i] * math.sin(TAU * swk[i] * u + ph[i, 0])
                a = ph[i, 1] + TAU * rot[i] * u
                f = math.cos(TAU * flip[i] * u + ph[i, 2])
                shade = 0.72 + 0.28 * abs(f)
                col = tuple(v * shade for v in cols[i])
                size_px = max(int(sz[i]), 4)
                if kind == "confetti":
                    spr = fx.confetti(size_px, aspect[i], a, f)
                elif kind == "petal":
                    spr = fx.petal(size_px, fx._q(a), fx._qs(f))
                elif kind == "leaf":
                    spr = fx.leaf(size_px, fx._q(a), fx._qs(f))
                elif kind == "heart":
                    spr = fx.heart(size_px, fx._q(0.35 * math.sin(a)))
                elif kind == "star":
                    spr = fx.star5(size_px, fx._q(a))
                else:
                    spr = fx.disc(max(size_px // 2, 1))
                c.splat(spr, x, y, col, opacity)
            return c
        return frame
    return make


design("cel-confeti", "Lluvia de confeti", "Confetti rain", "celebracion", 6,
       tags=["confeti", "confetti", "fiesta", "cumpleaños", "celebracion", "party", "birthday", "boda"],
       sample="birthday-03.jpg")(
    _falling("confetti", 150, PARTY, (16, 32), (1, 2), spin=(1, 3)))
design("cel-confeti-dorado", "Confeti dorado", "Gold confetti", "celebracion", 6,
       tags=["confeti", "dorado", "gold", "año nuevo", "new year", "elegante", "celebracion"], sample="newyear-02.jpg")(
    _falling("confetti", 140, GOLD + [(0.92, 0.92, 0.95)], (16, 30), (1, 2), spin=(1, 3)))
design("cel-estrellas", "Lluvia de estrellas", "Falling stars", "celebracion", 6,
       tags=["estrellas", "stars", "fiesta", "infantil", "celebracion", "magia"], sample="friends-01.jpg")(
    _falling("star", 60, [fx.hex_rgb("#ffd23f"), fx.hex_rgb("#fff1c2"), fx.hex_rgb("#ff9ad5")], (26, 52), (1, 1)))


design("amor-petalos", "Pétalos de rosa", "Rose petals", "amor", 8,
       tags=["petalos", "rosa", "rose", "petals", "boda", "wedding", "amor", "romantico", "flores"],
       sample="couple-04.jpg")(
    _falling("petal", 55, [fx.hex_rgb(c) for c in ("#c8102e", "#e0254a", "#a0001e", "#ff4d6d")], (40, 70), (1, 1),
             sway=90, spin=(1, 2)))


# ================================================================ Clima y naturaleza

def _snow(layers, wind=0.0):
    def make(w, h, T, rng):
        s = w / 1080
        parts = []
        for n, rmin, rmax, laps, op in layers:
            parts.append(dict(
                x=rng.uniform(0, w, n), y=rng.uniform(0, h, n), r=rng.uniform(rmin, rmax, n) * s,
                laps=np.full(n, laps), ph=rng.uniform(0, TAU, n), sw=rng.uniform(10, 40, n) * s, op=op))

        def frame(t):
            u = t / T
            c = Canvas(w, h)
            for L in parts:
                for i in range(len(L["x"])):
                    m = L["r"][i] * 3
                    y = wrap(L["y"][i] + L["laps"][i] * (h + 2 * m) * u, -m, h + m)
                    x = wrap(L["x"][i] + wind * L["laps"][i] * w * u + L["sw"][i] * math.sin(TAU * 2 * u + L["ph"][i]),
                             -m, w + m)
                    c.splat(fx.glow(max(int(L["r"][i]), 1)), x, y, (1, 1, 1), L["op"])
            return c
        return frame
    return make


design("clima-nieve", "Nieve suave", "Gentle snow", "clima", 8, res=(540, 960),
       tags=["nieve", "snow", "invierno", "winter", "navidad", "christmas", "frio"], sample="christmas-02.jpg")(
    _snow([(200, 5, 9, 1, 0.8), (90, 11, 18, 1, 0.95), (14, 28, 46, 2, 0.55)]))
design("clima-nevada", "Nevada", "Snowstorm", "clima", 6, res=(540, 960),
       tags=["nieve", "nevada", "tormenta", "snowstorm", "invierno", "winter", "navidad"], sample="christmas-04.jpg")(
    _snow([(420, 5, 9, 2, 0.8), (170, 10, 17, 3, 0.95), (22, 26, 44, 4, 0.5)], wind=0.5))


@design("clima-lluvia", "Lluvia", "Rain", "clima", 4,
        tags=["lluvia", "rain", "tormenta", "triste", "melancolia", "storm", "gotas"], sample="friends-10.jpg")
def _rain(w, h, T, rng):
    s = w / 1080
    n = 420
    x0, y0 = rng.uniform(-0.2, 1.1, n) * w, rng.uniform(0, h, n)
    laps = rng.integers(4, 8, n)
    ln = rng.uniform(50, 150, n) * s
    op = rng.uniform(0.18, 0.5, n)
    ang = math.radians(10)
    col = (0.85, 0.9, 1.0)

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        for i in range(n):
            m = ln[i]
            y = wrap(y0[i] + laps[i] * (h + 2 * m) * u, -m, h + m)
            x = x0[i] - math.tan(ang) * (y - y0[i])
            c.splat(fx.streak_at(ln[i], 2.6 * s, -ang), x, y, col, op[i])
        return c
    return frame


def _fog(rising: bool):
    def make(w, h, T, rng):
        t1 = fx.tile_noise(512, 11, falloff=2.0)
        t2 = fx.tile_noise(512, 23, falloff=2.2)
        yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
        col = np.broadcast_to(np.asarray((0.93, 0.94, 0.96), np.float32), (h, w, 3)).copy()

        def field(tt):
            if rising:
                a = fx.sample_tile(t1, w, h, 30, 60 * tt, 1.0)
                b = fx.sample_tile(t2, w, h, 200 + 10 * tt, 35 * tt, 0.7)
                grad = fx.smooth(0.1, 1.0, yy) * 0.9 + 0.05
            else:
                a = fx.sample_tile(t1, w, h, 25 * tt, 40, 1.0)
                b = fx.sample_tile(t2, w, h, -15 * tt + 200, 90, 0.7)
                grad = fx.smooth(0.25, 0.95, yy) * 0.8 + 0.1
            v = (a * 0.6 + b * 0.4)
            return np.clip((v - 0.3) * 2.6, 0, 1) * grad

        def frame(t):
            wgt = t / T
            f = field(t) * (1 - wgt) + field(t - T) * wgt
            c = Canvas(w, h)
            c.layer(col, (f * (0.8 if rising else 0.7)).astype(np.float32))
            return c
        return frame
    return make


design("clima-niebla", "Niebla", "Fog", "clima", 10, res=(270, 480),
       tags=["niebla", "fog", "bruma", "mist", "misterio", "terror", "halloween"], sample="nature-03.jpg")(_fog(False))
design("clima-humo", "Humo", "Smoke", "clima", 10, res=(270, 480),
       tags=["humo", "smoke", "vapor", "misterio", "dramatico", "concierto"], sample="concert-03.jpg")(_fog(True))
design("clima-hojas", "Hojas de otoño", "Autumn leaves", "clima", 8,
       tags=["hojas", "otoño", "autumn", "fall", "leaves", "naturaleza", "acción de gracias"], sample="nature-01.jpg")(
    _falling("leaf", 34, [fx.hex_rgb(c) for c in ("#d9480f", "#f08c00", "#e8590c", "#a61e4d", "#c2a000")], (55, 95),
             (1, 1), sway=120, spin=(1, 2)))
design("clima-sakura", "Flores de cerezo", "Cherry blossoms", "clima", 8,
       tags=["sakura", "cerezo", "cherry blossom", "primavera", "spring", "flores", "petalos", "japon"],
       sample="portrait-07.jpg")(
    _falling("petal", 80, [fx.hex_rgb(c) for c in ("#ffc2d6", "#ffd6e5", "#ffb0c8", "#fff0f5")], (22, 42), (1, 1),
             sway=100, spin=(1, 2)))


import designs_b  # noqa: E402,F401  (more families register themselves on import)
import designs_c  # noqa: E402,F401
import designs_d  # noqa: E402,F401
import designs_e  # noqa: E402,F401
