"""Second batch of overlays: more light, film and retro, glitch, camera UI."""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

import fx
from fx import TAU, Canvas
from designs import GOLD, PARTY, _bokeh, _leak, design, ramp, wrap

MONO = "VT323-Regular.ttf"


# ================================================================ Luces

for _id, es, en, rp, kw, tags, sample in (
    ("luz-fuga-dorada", "Fuga de luz dorada", "Golden light leak",
     ramp("#9a3d00", "#e07b00", "#ffb820", "#ffe48a", "#fffbe8"), {}, ["dorado", "golden hour", "atardecer"], "beach-04.jpg"),
    ("luz-fuga-roja", "Fuga de luz roja", "Red light leak",
     ramp("#5a0010", "#c8102e", "#ff3b2f", "#ff9a6a", "#ffeedd"), {}, ["rojo", "red", "dramatico"], "fashion-02.jpg"),
    ("luz-fuga-turquesa", "Fuga de luz turquesa y naranja", "Teal and orange leak",
     ramp("#004a5a", "#0ea5a5", "#ff8a3d", "#ffc27a", "#fff5e6"), {"bands": 6}, ["turquesa", "teal", "cine"], "city-01.jpg"),
    ("luz-fuga-violeta", "Fuga de luz violeta", "Purple light leak",
     ramp("#2d0a6b", "#6a1fd6", "#b35cff", "#e6b8ff", "#fbf3ff"), {}, ["violeta", "purple", "sueño"], "concert-02.jpg"),
    ("luz-fuga-verde", "Fuga de luz vintage verde", "Vintage green leak",
     ramp("#1f3d00", "#5f8f00", "#c8e04a", "#f2f7b0", "#fffff0"), {}, ["verde", "vintage", "retro"], "nature-06.jpg"),
    ("luz-fuga-esquina", "Luz en las esquinas", "Corner glow",
     ramp("#9a2a00", "#ff6a1a", "#ffb04a", "#ffe6b0", "#fffaf0"), {"mode": "corner"}, ["esquina", "corner", "calido"], "family-03.jpg"),
    ("luz-fuga-esquina-rosa", "Luz rosa en las esquinas", "Pink corner glow",
     ramp("#6b0f8f", "#e0338f", "#ff7fb3", "#ffc6dd", "#fff3f8"), {"mode": "corner"}, ["esquina", "rosa", "pink"], "makeup-02.jpg"),
):
    design(_id, es, en, "luces", 6, res=(270, 480), tags=["luz", "light leak", "fuga de luz", "pelicula"] + tags,
           sample=sample)(_leak(rp, **kw))

for _id, es, en, rp, sample in (
    ("luz-barrido-calido", "Barrido de luz cálida", "Warm light sweep",
     ramp("#9a2a00", "#ff6a1a", "#ffb04a", "#ffe6b0", "#fffaf0"), "friends-06.jpg"),
    ("luz-barrido-rosa", "Barrido de luz rosa", "Pink light sweep",
     ramp("#6b0f8f", "#e0338f", "#ff7fb3", "#ffc6dd", "#fff3f8"), "portrait-02.jpg"),
):
    design(_id, es, en, "luces", 2.5, loop=False, res=(270, 480), thumb_at=0.45,
           tags=["barrido", "sweep", "transicion", "transition", "luz", "light leak"], sample=sample)(
        _leak(rp, bands=5, sweep=True))

design("luz-flash-transicion", "Destello de transición", "Flash transition", "luces", 1.6, loop=False, res=(270, 480),
       thumb_at=0.2, tags=["flash", "destello", "transicion", "transition", "blanco", "luz"], sample="friends-02.jpg")(
    _leak(ramp("#ff7a1a", "#ffb04a", "#ffe6b0", "#fffaf0", "#ffffff"), bands=6, mode="flash"))


def _flare(core, streak_col, ghosts, path="sweep"):
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        yy = np.arange(h, dtype=np.float32)[:, None]
        xx = np.arange(w, dtype=np.float32)[None, :]
        warm = fx.hex_rgb(core)
        sc = fx.hex_rgb(streak_col)

        def frame(t):
            u = t / T
            if path == "sweep":
                env = fx.envelope(t, 0.5, T - 0.8, 0.8)
                px, py = w * (-0.15 + 1.3 * u), h * (0.28 + 0.05 * math.sin(u * 3))
            else:   # a sun that drifts in a small loop and breathes
                env = 0.85 + 0.15 * math.sin(TAU * 2 * u)
                px, py = w * (0.78 + 0.06 * math.sin(TAU * u)), h * (0.16 + 0.03 * math.sin(TAU * u + 1))
            c = Canvas(w, h)
            wash = np.exp(-((xx - px) ** 2 + (yy - py) ** 2) / (2 * (0.5 * w) ** 2)) * 0.4
            c.fill(warm, wash * env)
            streak = np.exp(-((yy - py) ** 2) / (2 * (5 * s + 1) ** 2)) * np.exp(-((xx - px) ** 2) / (2 * (0.55 * w) ** 2))
            c.fill(sc, np.clip(streak, 0, 1) * 0.85 * env)
            c.splat(fx.glow(int(170 * s)), px, py, warm, 0.8 * env, add=True)
            c.splat(fx.glow(int(55 * s)), px, py, (1, 1, 1), env, add=True)
            c.splat(fx.sparkle(int(280 * s)), px, py, (1, 1, 1), 0.9 * env, add=True)
            cx, cy = w / 2, h / 2
            for k, r, col, op in ghosts:
                gx, gy = px + (cx - px) * (1 + k), py + (cy - py) * (1 + k)
                spr = fx.ring(int(-r * s), max(4 * s, 2)) if r < 0 else fx.bokeh(int(r * s * 2))
                c.splat(spr, gx, gy, fx.hex_rgb(col), op * env, add=True)
            return c
        return frame
    return make


GH_BLUE = [(-0.4, 50, "#5fb0ff", 0.2), (0.3, -60, "#7fd0ff", 0.25), (0.8, 90, "#3d7bff", 0.14), (1.3, 40, "#bfe4ff", 0.2),
           (1.7, -110, "#5fb0ff", 0.12)]
GH_WARM = [(-0.45, 60, "#ffd27a", 0.18), (0.35, 40, "#ffb38a", 0.16), (0.7, -90, "#ffcf9a", 0.16), (1.25, 70, "#ff9a5a", 0.14),
           (1.6, 28, "#ffffff", 0.2)]
design("luz-destello-azul", "Destello anamórfico azul", "Blue anamorphic flare", "luces", 3, loop=False, res=(540, 960),
       thumb_at=0.45, tags=["destello", "flare", "anamorfico", "azul", "cine", "ciencia ficcion"], sample="city-04.jpg")(
    _flare("#9fd0ff", "#4f9bff", GH_BLUE))
design("luz-sol", "Sol con destellos", "Sun flare", "luces", 8, res=(540, 960),
       tags=["sol", "sun", "destello", "flare", "verano", "summer", "playa"], sample="beach-01.jpg")(
    _flare("#ffd9a0", "#ffe2b0", GH_WARM, path="drift"))


@design("luz-prisma", "Prisma arcoíris", "Rainbow prism", "luces", 6, res=(270, 480),
        tags=["prisma", "prism", "arcoiris", "rainbow", "refraccion", "cristal", "aesthetic"], sample="portrait-04.jpg")
def _prism(w, h, T, rng):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ang = math.radians(64)
    along = xx * math.cos(ang) + yy * math.sin(ang)
    span = w * math.cos(ang) + h * math.sin(ang)
    hue = np.linspace(0, 0.83, 256)
    lut = np.array([fx.hsv(v, 0.75, 1.0) for v in hue], np.float32)

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        for k, (off, width, op) in enumerate(((0.0, 0.22, 0.55), (0.5, 0.12, 0.35))):
            pos = span * (0.25 + 0.5 * (0.5 + 0.5 * math.sin(TAU * u + off * TAU)))
            d = (along - pos) / (span * width)
            inside = np.clip(1 - np.abs(d), 0, 1)
            idx = np.clip(((d + 1) / 2) * 255, 0, 255).astype(int)
            col = lut[idx]
            a = inside ** 1.5 * op * (0.8 + 0.2 * math.sin(TAU * 2 * u + k))
            c.layer(col, a.astype(np.float32))
        return c
    return frame


@design("luz-neon-barrido", "Barrido de neón", "Neon sweep", "luces", 1.4, loop=False, res=(540, 960), thumb_at=0.5,
        tags=["neon", "barrido", "sweep", "transicion", "transition", "luz", "moderno"], sample="concert-04.jpg")
def _neon_sweep(w, h, T, rng):
    s = min(w, h) / 1080
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ang = math.radians(-58)
    along = xx * math.cos(ang) + yy * math.sin(ang)
    lo, hi = along.min(), along.max()
    cols = [fx.hex_rgb("#ff2fb3"), fx.hex_rgb("#2fd8ff")]

    def frame(t):
        u = t / T
        pos = lo - 200 * s + (hi - lo + 400 * s) * (u * u * (3 - 2 * u))
        c = Canvas(w, h)
        for k, col in enumerate(cols):
            d = along - (pos - k * 90 * s)
            c.fill(col, np.exp(-(d ** 2) / (2 * (45 * s) ** 2)) * 0.75)
        d = along - pos
        c.fill((1, 1, 1), np.exp(-(d ** 2) / (2 * (10 * s) ** 2)))
        return c
    return frame


@design("luz-escaner", "Línea de escáner", "Scanner line", "luces", 3, res=(540, 960),
        tags=["escaner", "scanner", "laser", "tecnologia", "tech", "futurista", "linea"], sample="office-02.jpg")
def _scanner(w, h, T, rng):
    s = min(w, h) / 1080
    yy = np.arange(h, dtype=np.float32)[:, None] * np.ones((1, w), np.float32)
    col = fx.hex_rgb("#39f5ff")

    def frame(t):
        u = t / T
        y = h * (0.5 - 0.48 * math.cos(TAU * u))
        c = Canvas(w, h)
        trail_dir = 1 if math.sin(TAU * u) > 0 else -1
        d = (yy - y) * -trail_dir
        trail = np.where(d > 0, np.exp(-d / (120 * s)), 0) * 0.35
        c.fill(col, trail)
        c.fill(col, np.exp(-((yy - y) ** 2) / (2 * (14 * s) ** 2)) * 0.8)
        c.fill((1, 1, 1), np.exp(-((yy - y) ** 2) / (2 * (3 * s) ** 2)))
        return c
    return frame


def _shaped_bokeh(shape, palette, n, rmin, rmax, opacity, fall=False):
    """Bokeh whose discs are hearts or stars (a lens with a shaped aperture)."""
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        x0, y0 = rng.uniform(0, w, n), rng.uniform(0, h, n)
        ph = rng.uniform(0, TAU, n)
        tw = rng.integers(1, 4, n)
        rad = rng.uniform(rmin, rmax, n) * s
        cols = [palette[i] for i in rng.integers(0, len(palette), n)]
        sprites = {}
        m = rmax * s * 1.3

        def spr(r):
            k = int(r)
            if k not in sprites:
                base = fx.heart(k * 2) if shape == "heart" else fx.star5(k * 2) if shape == "star" else fx.disc(k)
                sprites[k] = np.clip(fx.blur_sprite(base, max(k / 18, 1)) * 0.85, 0, 1)
            return sprites[k]

        def frame(t):
            u = t / T
            c = Canvas(w, h)
            for i in np.argsort(rad)[::-1]:
                dy = (h + 2 * m) * u * (1 if fall else -1)
                y = wrap(y0[i] + dy, -m, h + m)
                x = x0[i] + 25 * s * math.sin(TAU * u + ph[i])
                op = opacity * (0.55 + 0.45 * math.sin(TAU * tw[i] * u + ph[i]))
                c.splat(spr(rad[i]), x, y, cols[i], op, add=True)
            return c
        return frame
    return make


design("luz-bokeh-blanco", "Bokeh blanco", "White bokeh", "luces", 8, res=(540, 960),
       tags=["bokeh", "blanco", "white", "luces", "desenfoque", "boda", "elegante"], sample="couple-06.jpg")(
    _bokeh([(1, 1, 1), (1, 0.97, 0.9), (0.9, 0.95, 1)], 40, 25, 90, 0.5))
design("luz-bokeh-azul", "Bokeh azul nocturno", "Blue night bokeh", "luces", 8, res=(540, 960),
       tags=["bokeh", "azul", "noche", "night", "ciudad", "city", "luces"], sample="city-02.jpg")(
    _bokeh([fx.hex_rgb(c) for c in ("#3d7bff", "#5fb0ff", "#8a6bff", "#2fd8ff")], 42, 25, 90, 0.55))
design("luz-bokeh-rosa", "Bokeh rosa", "Pink bokeh", "luces", 8, res=(540, 960),
       tags=["bokeh", "rosa", "pink", "romantico", "quince", "luces"], sample="quince-02.jpg")(
    _bokeh([fx.hex_rgb(c) for c in ("#ff6fa8", "#ffb0d0", "#ff9ec7", "#e07bff")], 40, 25, 90, 0.55))
design("luz-bokeh-corazones", "Bokeh de corazones", "Heart bokeh", "luces", 8, res=(540, 960),
       tags=["bokeh", "corazones", "hearts", "amor", "love", "san valentin", "romantico"], sample="couple-03.jpg")(
    _shaped_bokeh("heart", [fx.hex_rgb(c) for c in ("#ff4d7d", "#ff8fb3", "#ffc2d6", "#ffd27a")], 30, 30, 85, 0.9))
design("luz-bokeh-estrellas", "Bokeh de estrellas", "Star bokeh", "luces", 8, res=(540, 960),
       tags=["bokeh", "estrellas", "stars", "magia", "navidad", "fiesta"], sample="christmas-05.jpg")(
    _shaped_bokeh("star", GOLD + [(1, 1, 1)], 30, 30, 80, 0.9))
design("luz-bokeh-cayendo", "Bokeh que cae", "Falling bokeh", "luces", 8, res=(540, 960),
       tags=["bokeh", "cayendo", "falling", "luces", "navidad", "elegante"], sample="christmas-01.jpg")(
    _shaped_bokeh("disc", GOLD + [(1, 1, 1)], 40, 20, 70, 0.7, fall=True))
design("luz-luces-navidad", "Luces de Navidad", "Christmas lights", "luces", 8, res=(540, 960),
       tags=["navidad", "christmas", "luces", "lights", "bokeh", "fiestas", "diciembre"], sample="christmas-03.jpg")(
    _bokeh([fx.hex_rgb(c) for c in ("#ff3b3b", "#2fd06b", "#ffd23f", "#ffffff", "#3d9bff")], 60, 15, 60, 0.6))
design("luz-luces-ciudad", "Luces de ciudad", "City lights", "luces", 8, res=(540, 960),
       tags=["ciudad", "city", "luces", "noche", "night", "urbano", "bokeh"], sample="city-03.jpg")(
    _bokeh([fx.hex_rgb(c) for c in ("#ffb04a", "#ff6a3d", "#ffe08a", "#5fb0ff", "#ff4d6d")], 90, 10, 40, 0.65))


# ================================================================ Película y retro

def _grain_layer(c: Canvas, rnd, amount, warm=False):
    n = rnd.standard_normal((c.h, c.w)).astype(np.float32)
    light = (1, 0.96, 0.88) if warm else (1, 1, 1)
    c.fill(light, np.clip(np.clip(n, 0, None) * amount, 0, 0.5))
    c.fill((0, 0, 0), np.clip(np.clip(-n, 0, None) * amount * 1.15, 0, 0.5))


def _grain(amount, warm=False):
    def make(w, h, T, rng):
        frames = int(T * 30)

        def frame(t):
            i = (int(round(t * 30)) % frames) // 2   # grain changes every other frame: half the weight
            c = Canvas(w, h)
            _grain_layer(c, np.random.default_rng(7000 + i), amount, warm)
            return c
        return frame
    return make


design("pel-grano-fino", "Grano fino", "Fine grain", "pelicula", 1, res=(540, 960), crf=44,
       tags=["grano", "grain", "fino", "fine", "cine", "pelicula", "textura"], sample="portrait-06.jpg")(_grain(0.07))
design("pel-grano-16mm", "Grano de 16 mm", "16 mm grain", "pelicula", 1, res=(360, 640), crf=44,
       tags=["grano", "grain", "16mm", "pelicula", "film", "vintage", "analogico"], sample="family-04.jpg")(
    _grain(0.13, warm=True))
design("pel-grano-fuerte", "Grano fuerte", "Heavy grain", "pelicula", 1, res=(540, 960), crf=44,
       tags=["grano", "grain", "fuerte", "heavy", "ruido", "noise", "grunge"], sample="man-02.jpg")(_grain(0.2))


def _old_film(sepia, flicker, vig, scratches, dust_amount, grain_amount, gate=False):
    """Old projected film: dust, hairs, scratches, grain, flicker, vignette and an optional gate weave."""
    def make(w, h, T, rng):
        frames = int(T * 30)
        vg = fx.vignette(w, h, 0.45, 1.25) * vig
        lines = [(rng.uniform(0.05, 0.95) * w, rng.uniform(0, frames), rng.uniform(10, 50)) for _ in range(scratches)]
        sep = fx.hex_rgb("#704214")

        def frame(t):
            i = int(round(t * 30)) % frames
            r = np.random.default_rng(3000 + i)
            c = Canvas(w, h)
            if sepia:
                c.fill(sep, sepia)
            c.fill((0, 0, 0), vg)
            c.fill((0, 0, 0) if r.random() < 0.6 else (1, 0.96, 0.85), r.uniform(0, flicker))
            im, d = fx.draw_layer(w, h)
            dk, dd = fx.draw_layer(w, h)
            sc = w / 1080
            for _ in range(int(r.integers(4, 12) * dust_amount)):
                tgt = d if r.random() < 0.4 else dd
                x, y = r.uniform(0, w), r.uniform(0, h)
                for _ in range(r.integers(1, 4)):
                    rr = r.uniform(1.5, 6) * sc
                    ox, oy = r.normal(0, 4 * sc, 2)
                    tgt.ellipse([x + ox - rr, y + oy - rr, x + ox + rr, y + oy + rr], fill=int(r.uniform(140, 255)))
            if r.random() < 0.3 * dust_amount:
                tgt = d if r.random() < 0.5 else dd
                x, y = r.uniform(0, w), r.uniform(0, h)
                pts, ang = [(x, y)], r.uniform(0, TAU)
                for _ in range(16):
                    ang += r.normal(0, 0.35)
                    x += math.cos(ang) * 9 * sc
                    y += math.sin(ang) * 9 * sc
                    pts.append((x, y))
                tgt.line(pts, fill=210, width=max(int(2 * sc), 1))
            for lx, start, life in lines:
                if (i - start) % frames < life:
                    x = lx + r.normal(0, 1.5)
                    (dd if r.random() < 0.3 else d).line([(x, 0), (x + r.normal(0, 3), h)], fill=int(r.uniform(70, 160)),
                                                        width=max(int(r.integers(1, 3) * sc), 1))
            c.image(dk, 0, 0, (0.05, 0.04, 0.03), 0.85)
            c.image(im, 0, 0, (1, 0.98, 0.92), 0.8)
            if grain_amount:
                _grain_layer(c, np.random.default_rng(3500 + i // 2), grain_amount * 0.7, warm=True)
            if gate:
                c = _shift(c, int(r.normal(0, 2.0 * sc)))
            return c
        return frame
    return make


def _shift(c: Canvas, dy: int) -> Canvas:
    if dy:
        c.rgb = np.roll(c.rgb, dy, axis=0)
        c.a = np.roll(c.a, dy, axis=0)
    return c


design("pel-polvo-suave", "Polvo suave", "Light dust", "pelicula", 4, res=(1080, 1920),
       tags=["polvo", "dust", "suave", "pelicula", "film", "textura"], sample="couple-08.jpg")(
    _old_film(0, 0.0, 0, 2, 0.5, 0))
design("pel-8mm", "Película de 8 mm", "8 mm film", "pelicula", 4, res=(540, 960), crf=42,
       tags=["8mm", "super 8", "pelicula", "film", "vintage", "recuerdos", "familia", "home video"], sample="family-01.jpg")(
    _old_film(0.12, 0.06, 0.55, 3, 1.0, 0.12, gate=True))
design("pel-cine-mudo", "Cine mudo", "Silent movie", "pelicula", 4, res=(540, 960), crf=42,
       tags=["cine mudo", "silent film", "antiguo", "old", "sepia", "1920", "blanco y negro", "vintage"],
       sample="man-05.jpg")(
    _old_film(0.32, 0.12, 0.85, 6, 1.6, 0.16, gate=True))


def _burn(rp, direction="right", seconds=3.5):
    def make(w, h, T, rng):
        tile = fx.tile_noise(512, int(rng.integers(1, 10_000)), falloff=1.6)
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        if direction == "right":
            grad = (xx / w) * 0.55 + (1 - yy / h) * 0.25
        elif direction == "left":
            grad = (1 - xx / w) * 0.55 + (yy / h) * 0.25
        elif direction == "center":
            grad = 0.8 - np.sqrt(((xx / w) - 0.5) ** 2 + ((yy / h) - 0.45) ** 2) * 1.3
        else:   # edges: burns in from all sides
            grad = np.sqrt(((xx / w) - 0.5) ** 2 + ((yy / h) - 0.5) ** 2) * 1.3
        pal = np.array(rp, np.float32)

        def frame(t):
            u = t / T
            n = fx.sample_tile(tile, w, h, 40 + 60 * u, 90, 0.9)
            level = 1.4 * math.sin(math.pi * min(u * 1.1, 1.0)) ** 1.3
            heat = np.clip(level - (1 - grad) - n * 0.6 + 0.35, 0, 1)
            idx = heat * (len(pal) - 1)
            lo = np.floor(idx).astype(int)
            hi = np.minimum(lo + 1, len(pal) - 1)
            f = (idx - lo)[..., None]
            col = pal[lo] * (1 - f) + pal[hi] * f
            c = Canvas(w, h)
            c.layer(col, np.clip(heat * 1.6, 0, 1).astype(np.float32))
            return c
        return frame
    return make


BURN_RED = ramp("#2a0000", "#8f0010", "#e0102a", "#ff5a3d", "#ffc8a0", "#ffffff")
BURN_BLUE = ramp("#00062a", "#0a2a8f", "#1f6bff", "#3fd0ff", "#c8f4ff", "#ffffff")
BURN_ORANGE = ramp("#3a0500", "#c41e00", "#ff6a00", "#ffb000", "#fff2c0", "#ffffff")
BURN_PINK = ramp("#2a0020", "#8f0a5a", "#e0338f", "#ff8fc0", "#ffe0f0", "#ffffff")
for _id, es, en, rp, dirn, sample in (
    ("pel-quemado-rojo", "Quemado rojo", "Red film burn", BURN_RED, "left", "fashion-04.jpg"),
    ("pel-quemado-azul", "Quemado azul", "Blue film burn", BURN_BLUE, "right", "city-01.jpg"),
    ("pel-quemado-centro", "Quemado desde el centro", "Centre film burn", BURN_ORANGE, "center", "friends-07.jpg"),
    ("pel-quemado-bordes", "Quemado en los bordes", "Edge film burn", BURN_ORANGE, "edges", "couple-02.jpg"),
    ("pel-quemado-rosa", "Quemado rosa", "Pink film burn", BURN_PINK, "right", "quince-04.jpg"),
):
    design(_id, es, en, "pelicula", 3.5, loop=False, res=(270, 480), thumb_at=0.24, sample=sample,
           tags=["quemado", "film burn", "pelicula", "transicion", "transition", "vintage"])(_burn(rp, dirn))


@design("pel-flash-blanco", "Flash de película", "Film flash", "pelicula", 1.2, loop=False, res=(270, 480), thumb_at=0.3,
        tags=["flash", "blanco", "white", "transicion", "transition", "pelicula", "parpadeo"], sample="friends-09.jpg")
def _film_flash(w, h, T, rng):
    vg = fx.vignette(w, h, 0.2, 1.3)

    def frame(t):
        u = t / T
        a = max(0.0, math.sin(math.pi * u)) ** 0.6
        a *= 0.7 + 0.3 * (1 if int(t * 30) % 3 else 0.4)   # a couple of uneven frames
        c = Canvas(w, h)
        c.fill((1, 0.97, 0.9), np.clip(a * (1 - 0.35 * vg), 0, 1))
        return c
    return frame


def _film_border(kind):
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        frames = int(T * 30)
        im, d = fx.draw_layer(w, h)
        holes, hd = fx.draw_layer(w, h)
        if kind == "super8":
            m = int(54 * s)
            d.rectangle([0, 0, w, h], fill=255)
            d.rounded_rectangle([m + int(70 * s), m, w - m, h - m], radius=int(60 * s), fill=0)
            hx = int(22 * s)
            hd.rounded_rectangle([hx, h // 2 - int(70 * s), hx + int(70 * s), h // 2 + int(70 * s)], radius=int(16 * s),
                                 fill=255)
            pitch = None
        else:   # 35 mm strip: borders with perforations on both sides, scrolling
            bw = int(110 * s)
            d.rectangle([0, 0, bw, h], fill=255)
            d.rectangle([w - bw, 0, w, h], fill=255)
            pitch = int(96 * s)
            for y in range(-pitch, h + 2 * pitch, pitch):
                for x in (int(30 * s), w - bw + int(30 * s)):
                    hd.rounded_rectangle([x, y, x + int(50 * s), y + int(62 * s)], radius=int(10 * s), fill=255)
        num = fx.text_image("24    25", MONO, int(44 * s))

        def frame(t):
            i = int(round(t * 30)) % frames
            r = np.random.default_rng(4000 + i)
            c = Canvas(w, h)
            dark = Canvas(w, h)
            dark.image(im, 0, 0, (0.03, 0.025, 0.02), 1.0)
            dark.image(holes, 0, 0, (1, 0.96, 0.88), 0.95)
            if kind != "super8":
                dark.image(num.rotate(90, expand=True), int(w - 104 * s), int(h * 0.3), (1, 0.75, 0.3), 0.8)
            if pitch:
                dark = _shift(dark, int((t * 30 * 6 * s) % pitch))
            else:
                dark = _shift(dark, int(r.normal(0, 2.5 * s)))
            c.merge(dark)
            return c
        return frame
    return make


design("pel-marco-super8", "Marco de Super 8", "Super 8 frame", "pelicula", 3, res=(1080, 1920),
       tags=["super 8", "8mm", "marco", "frame", "pelicula", "film", "vintage", "borde"], sample="family-05.jpg")(
    _film_border("super8"))
design("pel-tira-35mm", "Tira de película 35 mm", "35 mm film strip", "pelicula", 4, res=(1080, 1920),
       tags=["35mm", "tira", "film strip", "pelicula", "marco", "frame", "cine", "perforaciones"], sample="travel-01.jpg")(
    _film_border("35mm"))


def _vhs(label, mode="play"):
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        scan = np.zeros((h, w), np.float32)
        scan[::4] = 0.14
        scan[1::4] = 0.07
        frames = int(T * 30)
        big = fx.text_image(label, MONO, int(84 * s))
        sp = fx.text_image("SP", MONO, int(84 * s))

        def frame(t):
            u = t / T
            i = int(round(t * 30)) % frames
            r = np.random.default_rng(9100 + i)
            c = Canvas(w, h)
            c.fill((0, 0, 0), scan)
            c.fill(fx.hex_rgb("#5a6bff"), 0.05)
            nbands = {"play": 1, "pause": 1, "rew": 3, "rec": 1}[mode]
            for b in range(nbands):
                if mode == "pause":
                    band_y = int(h * 0.86 + r.normal(0, 4 * s))
                    band_h = int(36 * s)
                else:
                    speed = 3 if mode == "rew" else 1
                    band_y = int(wrap(h * (u * speed + b / nbands), 0, h))
                    band_h = int((140 if mode == "rew" else 70) * s)
                y0, y1 = max(band_y - band_h, 0), min(band_y, h)
                if y1 > y0:
                    a = np.zeros((h, w), np.float32)
                    hb, wb = (y1 - y0 + 3) // 4, (w + 3) // 4   # 4 px blocks: tape noise, and it compresses
                    blocks = np.kron(r.uniform(0, 1, (hb, wb)), np.ones((4, 4)))[:y1 - y0, :w]
                    a[y0:y1] = (blocks > (0.7 if mode == "rew" else 0.5)) * 0.6 * np.linspace(0.2, 1, y1 - y0)[:, None]
                    c.fill((1, 1, 1), a)
            for _ in range(r.integers(0, 4 if mode == "rew" else 3)):
                y = int(r.uniform(0, h))
                a = np.zeros((h, w), np.float32)
                x0 = int(r.uniform(0, w * 0.7))
                a[y:y + 2, x0:x0 + int(r.uniform(80, 500) * s)] = 0.6
                c.fill((1, 1, 1), a)
            blink = mode != "pause" or (t % 1.0) < 0.6
            items = [(big, 80 * s, 110 * s, blink), (sp, w - 80 * s - sp.width, 110 * s, True)]
            if mode != "pause":
                tc = fx.text_image(f"0:{int(t) // 60:02d}:{int(t) % 60:02d}", MONO, int(84 * s))
                items.append((tc, 80 * s, h - 200 * s, True))
            for img, x, y, on in items:
                if on:
                    c.image(img, int(x + 4 * s), int(y + 4 * s), (0, 0, 0), 0.45)
                    c.image(img, int(x), int(y), (0.96, 0.97, 1.0), 0.92)
            if mode == "rec":
                if (t % 1.0) < 0.6:
                    c.splat(fx.disc(int(20 * s)), 80 * s + big.width + 46 * s, 152 * s, fx.hex_rgb("#ff2b2b"), 1.0)
            return c
        return frame
    return make


design("pel-vhs-rec", "VHS grabando", "VHS recording", "pelicula", 6,
       tags=["vhs", "rec", "grabando", "retro", "90s", "cinta", "camcorder"], sample="friends-10.jpg")(_vhs("REC", "rec"))
design("pel-vhs-pausa", "VHS en pausa", "VHS pause", "pelicula", 4,
       tags=["vhs", "pausa", "pause", "retro", "90s", "cinta", "tape"], sample="friends-11.jpg")(_vhs("PAUSE", "pause"))
design("pel-vhs-rebobinar", "VHS rebobinando", "VHS rewind", "pelicula", 3,
       tags=["vhs", "rebobinar", "rewind", "retro", "90s", "transicion", "flashback", "recuerdo"],
       sample="friends-12.jpg")(_vhs("<< REW", "rew"))


@design("pel-crt", "Televisor antiguo (CRT)", "Old TV (CRT)", "pelicula", 4,
        tags=["crt", "tv", "televisor", "retro", "scanlines", "lineas", "80s", "90s"], sample="podcast-01.jpg")
def _crt(w, h, T, rng):
    s = min(w, h) / 1080
    scan = np.zeros((h, w), np.float32)
    scan[::3] = 0.2
    corners = fx.vignette(w, h, 0.9, 1.02, round_=3.5)
    vg = fx.vignette(w, h, 0.5, 1.3) * 0.5
    yy = np.arange(h, dtype=np.float32)[:, None] * np.ones((1, w), np.float32)

    def frame(t):
        u = t / T
        c = Canvas(w, h)
        c.fill((0, 0, 0), scan)
        bar = h * u
        c.fill((1, 1, 1), np.exp(-((yy - bar) ** 2) / (2 * (90 * s) ** 2)) * 0.07)
        c.fill((0, 0, 0), vg)
        c.fill((0.02, 0.02, 0.02), corners)
        return c
    return frame


# ================================================================ Glitch

GL = [fx.hex_rgb(c) for c in ("#ff2a6d", "#05d9e8", "#ffffff", "#d1f7ff", "#ff00ff", "#00ff9f")]


def _glitch(kind, bursty=True):
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        frames = int(T * 30)
        bursts = sorted(list(rng.uniform(0, T, 3)) + [T * 0.5])   # one at the middle: the card shows it

        def strength(t):
            if not bursty:
                return 1.0
            return max(max(0.0, 1 - abs(t - b) / 0.18) for b in bursts)

        def frame(t):
            i = int(round(t * 30)) % frames
            r = np.random.default_rng(6000 + i)
            k = strength(t)
            c = Canvas(w, h)
            if k <= 0.01:
                return c
            if kind in ("rgb", "transition"):
                for _ in range(int(r.integers(3, 9) * (2 if kind == "transition" else 1))):
                    y = int(r.uniform(0, h))
                    bh = int(r.uniform(6, 90) * s)
                    x0 = int(r.uniform(-0.2, 0.8) * w)
                    bw = int(r.uniform(0.2, 1.0) * w)
                    a = np.zeros((h, w), np.float32)
                    a[y:y + bh, max(x0, 0):max(min(x0 + bw, w), 0)] = r.uniform(0.25, 0.7) * k
                    c.fill(GL[int(r.integers(0, len(GL)))], a)
            if kind in ("blocks", "transition"):
                n = int(r.integers(10, 40) * (2 if kind == "transition" else 1))
                for _ in range(n):
                    bs = int(r.choice([8, 16, 24, 40, 64]) * s)
                    x, y = int(r.uniform(0, w)), int(r.uniform(0, h))
                    a = np.zeros((h, w), np.float32)
                    a[y:y + bs, x:x + int(bs * r.uniform(1, 6))] = r.uniform(0.5, 1.0) * k
                    c.fill(GL[int(r.integers(0, len(GL)))], a)
            if kind in ("static", "transition"):
                lo = (h // 4, w // 4)
                n = (r.uniform(0, 1, lo) ** 1.5).astype(np.float32)
                big = np.kron(n, np.ones((4, 4), np.float32))[:h, :w]
                amt = 0.5 if kind == "static" else 0.9 * math.sin(math.pi * min(t / T, 1))
                c.fill((1, 1, 1), big * amt * (k if kind != "static" else 1))
            return c
        return frame
    return make


design("glitch-rgb", "Glitch RGB", "RGB glitch", "glitch", 4,
       tags=["glitch", "rgb", "error", "digital", "cyber", "tecnologia", "falla"], sample="man-04.jpg")(_glitch("rgb"))
design("glitch-bloques", "Glitch de bloques", "Block glitch", "glitch", 4,
       tags=["glitch", "bloques", "blocks", "pixeles", "digital", "datamosh", "error"], sample="gym-05.jpg")(_glitch("blocks"))
design("glitch-estatica", "Estática de TV", "TV static", "glitch", 2, res=(1080, 1920),
       tags=["estatica", "static", "tv", "ruido", "noise", "señal", "retro"], sample="podcast-02.jpg")(
    _glitch("static", bursty=False))


design("glitch-transicion", "Transición glitch", "Glitch transition", "glitch", 0.8, loop=False, thumb_at=0.5,
       tags=["glitch", "transicion", "transition", "error", "digital", "corte"], sample="concert-01.jpg")(
    _glitch("transition", bursty=False))


@design("glitch-codigo", "Lluvia de código", "Code rain", "glitch", 6, res=(540, 960),
        tags=["codigo", "code", "binario", "binary", "matrix", "hacker", "tecnologia", "datos"], sample="office-03.jpg")
def _code_rain(w, h, T, rng):
    s = min(w, h) / 1080
    size = int(52 * s)
    glyphs = [fx.text_image(ch, MONO, size) for ch in "0101101<>/$#{}=+*"]
    cols = int(w / (size * 0.62))
    head = rng.uniform(0, 1, cols)
    laps = rng.integers(1, 3, cols)
    length = rng.integers(8, 22, cols)
    green = fx.hex_rgb("#39ff7a")
    step = size * 0.95
    rows = int(h / step) + 2

    def frame(t):
        u = t / T
        i = int(round(t * 30))
        c = Canvas(w, h)
        for col in range(cols):
            hy = wrap((head[col] + laps[col] * u) * (rows + length[col]), 0, rows + length[col])
            for k in range(length[col]):
                row = int(hy) - k
                if row < 0 or row >= rows:
                    continue
                g = glyphs[(col * 7 + row * 3 + (i // 4 if k == 0 else 0)) % len(glyphs)]
                op = (1 - k / length[col]) ** 1.2
                colr = (0.85, 1, 0.9) if k == 0 else green
                if k == 0:
                    c.splat(fx.glow(int(size * 0.7)), col * size * 0.62 + g.width / 2, row * step + g.height / 2, green,
                            0.35, add=True)
                c.image(g, int(col * size * 0.62), int(row * step), colr, op)
        return c
    return frame


# ================================================================ Cámara y pantalla

def _shadowed(c, img, x, y, color=(1, 1, 1), s=1.0, op=0.95):
    c.image(img, int(x + 3 * s), int(y + 3 * s), (0, 0, 0), 0.4 * op)
    c.image(img, int(x), int(y), color, op)


@design("cam-rec-minimal", "REC minimalista", "Minimal REC", "camara", 4,
        tags=["rec", "grabando", "minimal", "camara", "vlog", "recording"], sample="creator-02.jpg")
def _rec_min(w, h, T, rng):
    s = min(w, h) / 1080
    rec = fx.text_image("REC", MONO, int(66 * s))
    dot = fx.disc(int(16 * s))

    def frame(t):
        c = Canvas(w, h)
        if (t % 1.0) < 0.6:
            c.splat(dot, 96 * s, 132 * s, fx.hex_rgb("#ff2b2b"), 1)
        _shadowed(c, rec, 124 * s, 104 * s, s=s)
        return c
    return frame


@design("cam-en-vivo", "En vivo (LIVE)", "Live badge", "camara", 6,
        tags=["live", "en vivo", "directo", "transmision", "stream", "redes", "camara"], sample="creator-03.jpg")
def _live(w, h, T, rng):
    s = min(w, h) / 1080
    pill, d = fx.draw_layer(int(190 * s), int(76 * s))
    d.rounded_rectangle([0, 0, pill.width - 1, pill.height - 1], radius=int(14 * s), fill=255)
    txt = fx.text_image("LIVE", MONO, int(64 * s))
    eye_pill, d2 = fx.draw_layer(int(230 * s), int(76 * s))
    d2.rounded_rectangle([0, 0, eye_pill.width - 1, eye_pill.height - 1], radius=int(14 * s), fill=255)

    def frame(t):
        c = Canvas(w, h)
        x, y = 70 * s, 100 * s
        pulse = 0.85 + 0.15 * math.sin(TAU * t)
        c.image(pill, int(x), int(y), fx.hex_rgb("#ff1f4b"), 0.95 * pulse + 0.05)
        c.image(txt, int(x + (pill.width - txt.width) / 2), int(y + (pill.height - txt.height) / 2), (1, 1, 1), 1)
        ex = x + pill.width + 16 * s
        c.image(eye_pill, int(ex), int(y), (0, 0, 0), 0.45)
        viewers = 1200 + int(t / T * 340)
        vt = fx.text_image(f"{viewers / 1000:.1f}K", MONO, int(58 * s))
        tx = ex + (eye_pill.width - vt.width) / 2 + 18 * s
        c.splat(fx.disc(int(10 * s)), tx - 30 * s, y + eye_pill.height / 2, (1, 1, 1), 1)
        c.image(vt, int(tx), int(y + (eye_pill.height - vt.height) / 2), (1, 1, 1), 1)
        return c
    return frame


def _cam_ui(tint=None, label="", clock=False, grid=False, low_battery=False, noise=0.0, scan=0.0):
    def make(w, h, T, rng):
        s = min(w, h) / 1080
        m, L, th = int(70 * s), int(120 * s), max(int(6 * s), 2)
        ui, d = fx.draw_layer(w, h)
        for (x, y, dx, dy) in ((m, m, 1, 1), (w - m, m, -1, 1), (m, h - m, 1, -1), (w - m, h - m, -1, -1)):
            d.line([(x, y), (x + dx * L, y)], fill=255, width=th)
            d.line([(x, y), (x, y + dy * L)], fill=255, width=th)
        if grid:
            for k in (1, 2):
                d.line([(w * k // 3, m + L), (w * k // 3, h - m - L)], fill=150, width=max(th // 3, 1))
                d.line([(m + L, h * k // 3), (w - m - L, h * k // 3)], fill=150, width=max(th // 3, 1))
            fs = int(110 * s)
            d.rectangle([w // 2 - fs, h // 2 - fs, w // 2 + fs, h // 2 + fs], outline=255, width=max(th // 2, 2))
            info = fx.text_image("ISO 400   f/2.8   1/120", MONO, int(54 * s))
            ui.paste(255, (w // 2 - info.width // 2, h - m - int(80 * s)), info)
        else:
            k = int(30 * s)
            d.line([(w // 2 - k, h // 2), (w // 2 + k, h // 2)], fill=255, width=max(th // 2, 2))
            d.line([(w // 2, h // 2 - k), (w // 2, h // 2 + k)], fill=255, width=max(th // 2, 2))
        bx, by, bw, bh = w - m - int(140 * s), h - m - int(100 * s), int(100 * s), int(46 * s)
        d.rectangle([bx, by, bx + bw, by + bh], outline=255, width=max(th // 2, 2))
        d.rectangle([bx + bw, by + bh // 3, bx + bw + int(9 * s), by + 2 * bh // 3], fill=255)
        bars = 1 if low_battery else 3
        if not low_battery:
            for j in range(bars):
                x = bx + int(9 * s) + j * int(29 * s)
                d.rectangle([x, by + int(9 * s), x + int(22 * s), by + bh - int(9 * s)], fill=255)
        if label:
            lab = fx.text_image(label, MONO, int(66 * s))
            ui.paste(255, (m + int(30 * s), h - m - int(100 * s)), lab)
        rec = fx.text_image("REC", MONO, int(84 * s))
        dot = fx.disc(int(20 * s))
        frames = int(T * 30)

        def frame(t):
            c = Canvas(w, h)
            i = int(round(t * 30)) % frames
            if tint:
                c.fill(fx.hex_rgb(tint[0]), tint[1])
            if scan:
                a = np.zeros((h, w), np.float32)
                a[::3] = scan
                c.fill((0, 0, 0), a)
            if noise:
                _grain_layer(c, np.random.default_rng(8000 + i), noise)
            c.image(ui, int(3 * s), int(3 * s), (0, 0, 0), 0.35)
            c.image(ui, 0, 0, (1, 1, 1), 0.92)
            x0, y0 = m + int(40 * s), m + int(40 * s)
            if (t % 1.0) < 0.6:
                c.splat(dot, x0 + 20 * s, y0 + 42 * s, fx.hex_rgb("#ff2b2b"), 1.0)
            _shadowed(c, rec, x0 + 56 * s, y0, s=s)
            if low_battery and (t % 0.8) < 0.45:
                a = np.zeros((h, w), np.float32)
                a[by + int(9 * s):by + bh - int(9 * s), bx + int(9 * s):bx + int(31 * s)] = 1
                c.fill(fx.hex_rgb("#ff2b2b"), a)
            if clock:
                sec = 41 * 60 + 7 + int(t)
                txt = f"2026-10-16  23:{sec // 60 % 60:02d}:{sec % 60:02d}"
            else:
                txt = f"00:00:{int(t):02d}:{int(t * 30) % 30:02d}"
            tc = fx.text_image(txt, MONO, int(70 * s))
            _shadowed(c, tc, w - m - 40 * s - tc.width, y0 + 6 * s, s=s)
            return c
        return frame
    return make


design("cam-vision-nocturna", "Visión nocturna", "Night vision", "camara", 6, res=(1080, 1920),
       tags=["vision nocturna", "night vision", "verde", "camara", "noche", "misterio", "terror"], sample="halloween-02.jpg")(
    _cam_ui(tint=("#1aff5a", 0.32), label="NIGHT", scan=0.14))
design("cam-seguridad", "Cámara de seguridad", "Security camera", "camara", 8, res=(1080, 1920),
       tags=["seguridad", "cctv", "security", "camara", "vigilancia", "broma", "prank"], sample="office-04.jpg")(
    _cam_ui(tint=("#8090a0", 0.18), label="CAM 01", clock=True, scan=0.12))
design("cam-visor", "Visor de cámara", "Camera viewfinder", "camara", 6, res=(1080, 1920),
       tags=["visor", "viewfinder", "cuadricula", "grid", "camara", "foto", "fotografo"], sample="portrait-08.jpg")(
    _cam_ui(grid=True))
design("cam-bateria-baja", "Batería baja", "Low battery", "camara", 6, res=(1080, 1920),
       tags=["bateria", "battery", "baja", "low", "camara", "vlog", "humor"], sample="creator-04.jpg")(
    _cam_ui(low_battery=True, label="4K  60"))


@design("cam-enfoque", "Enfoque", "Focus lock", "camara", 1.8, loop=False, thumb_at=0.9,
        tags=["enfoque", "focus", "camara", "foto", "autofocus", "cuadro"], sample="pet-01.jpg")
def _focus(w, h, T, rng):
    s = min(w, h) / 1080
    th = max(int(6 * s), 2)

    def frame(t):
        u = t / T
        k = fx.ease_out(min(u / 0.45, 1))
        half = (420 - 220 * k) * s
        locked = u > 0.55
        col = fx.hex_rgb("#7CFF6B") if locked else (1, 1, 1)
        L = int(70 * s)
        im, d = fx.draw_layer(w, h)
        cx, cy = w / 2, h / 2
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            x, y = cx + sx * half, cy + sy * half
            d.line([(x, y), (x - sx * L, y)], fill=255, width=th)
            d.line([(x, y), (x, y - sy * L)], fill=255, width=th)
        c = Canvas(w, h)
        op = 1.0 if not locked or (t * 8) % 2 < 1.4 else 0.6
        c.image(im, 2, 2, (0, 0, 0), 0.35)
        c.image(im, 0, 0, col, op)
        return c
    return frame


@design("cam-flash", "Flash de foto", "Camera flash", "camara", 0.7, loop=False, res=(270, 480), thumb_at=0.55,
        tags=["flash", "foto", "camara", "photo", "transicion", "blanco", "paparazzi"], sample="fashion-01.jpg")
def _photo_flash(w, h, T, rng):
    def frame(t):
        a = 1.0 if t < 0.05 else max(0.0, 1 - (t - 0.05) / (T - 0.05)) ** 1.8
        c = Canvas(w, h)
        c.fill((1, 1, 1), a)
        return c
    return frame


@design("cam-obturador", "Obturador", "Camera shutter", "camara", 0.9, loop=False, thumb_at=0.12,
        tags=["obturador", "shutter", "camara", "foto", "transicion", "iris", "click"], sample="travel-02.jpg")
def _shutter(w, h, T, rng):
    blades = 7
    R = math.hypot(w, h) / 2 + 40

    def frame(t):
        u = t / T
        close = math.sin(math.pi * min(u, 1)) ** 0.8   # 0 open -> 1 shut -> 0 open
        hole = R * (1 - close) * 1.02
        cx, cy = w / 2, h / 2
        im = Image.new("L", (w * 2, h * 2), 0)
        d = ImageDraw.Draw(im)
        for b in range(blades):
            a0 = b / blades * TAU + close * 0.9
            a1 = a0 + TAU / blades
            p = []
            for a in (a0, a1):
                p.append((cx * 2 + math.cos(a) * hole * 2, cy * 2 + math.sin(a) * hole * 2))
            p += [(cx * 2 + math.cos(a1 + 0.6) * R * 3, cy * 2 + math.sin(a1 + 0.6) * R * 3),
                  (cx * 2 + math.cos(a0 + 0.6) * R * 3, cy * 2 + math.sin(a0 + 0.6) * R * 3)]
            d.polygon(p, fill=255)
            d.line(p[:2], fill=120, width=4)
        im = im.resize((w, h), Image.LANCZOS)
        c = Canvas(w, h)
        if close > 0.01:
            c.image(im, 0, 0, (0.08, 0.08, 0.09), 1)
        return c
    return frame


@design("cam-cuenta-regresiva", "Cuenta regresiva de cine", "Film leader countdown", "camara", 3, loop=False,
        thumb_at=0.2, tags=["cuenta regresiva", "countdown", "cine", "film leader", "3 2 1", "intro", "retro"],
        sample="concert-02.jpg")
def _leader(w, h, T, rng):
    s = min(w, h) / 1080
    R = 380 * s

    def frame(t):
        num = 3 - int(t)
        frac = t % 1.0
        c = Canvas(w, h)
        c.fill((0.55, 0.53, 0.5), 0.88)
        im, d = fx.draw_layer(w, h)
        cx, cy = w // 2, h // 2
        d.pieslice([cx - R * 2, cy - R * 2, cx + R * 2, cy + R * 2], -90, -90 + 360 * frac, fill=110)
        d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=255, width=int(10 * s))
        d.ellipse([cx - R * 0.82, cy - R * 0.82, cx + R * 0.82, cy + R * 0.82], outline=255, width=int(6 * s))
        d.line([(0, cy), (w, cy)], fill=255, width=int(5 * s))
        d.line([(cx, 0), (cx, h)], fill=255, width=int(5 * s))
        c.image(im, 0, 0, (0.08, 0.08, 0.08), 0.85)
        if num >= 1:
            n = fx.text_image(str(num), "Anton-Regular.ttf", int(460 * s))
            c.image(n, cx - n.width // 2, cy - n.height // 2, (0.05, 0.05, 0.05), 0.95)
        return c
    return frame


@design("cam-grabando-pantalla", "Grabando pantalla", "Screen recording", "camara", 6,
        tags=["grabar pantalla", "screen recording", "tutorial", "pantalla", "rec", "celular"], sample="office-01.jpg")
def _screen_rec(w, h, T, rng):
    s = min(w, h) / 1080
    border, d = fx.draw_layer(w, h)
    d.rounded_rectangle([6, 6, w - 7, h - 7], radius=int(60 * s), outline=255, width=int(10 * s))
    pill, d2 = fx.draw_layer(int(260 * s), int(70 * s))
    d2.rounded_rectangle([0, 0, pill.width - 1, pill.height - 1], radius=int(35 * s), fill=255)

    def frame(t):
        c = Canvas(w, h)
        pulse = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(TAU * t))
        c.image(border, 0, 0, fx.hex_rgb("#ff2b2b"), pulse)
        x, y = (w - pill.width) // 2, int(60 * s)
        c.image(pill, x, y, fx.hex_rgb("#ff2b2b"), 0.95)
        c.splat(fx.disc(int(12 * s)), x + 40 * s, y + pill.height / 2, (1, 1, 1), 1)
        tc = fx.text_image(f"{int(t) // 60:02d}:{int(t) % 60:02d}", MONO, int(56 * s))
        c.image(tc, int(x + 70 * s), int(y + (pill.height - tc.height) / 2), (1, 1, 1), 1)
        return c
    return frame
