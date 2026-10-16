"""The animated backgrounds of Stock › Fondos: 45 motifs in four palettes plus seasonal sets.

A motif is make(w, h, T, rng, pal) -> frame(t) -> (h, w, 3) float RGB in 0-1 (opaque). Every motion is
periodic in T, so the loop is seamless. `res` is the drawing size; build.py scales to 1080 x 1920.
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "overlays"))
import fx  # noqa: E402
from fx import TAU  # noqa: E402

def H(h):
    return np.array(fx.hex_rgb(h), np.float32)



@dataclass
class Background:
    id: str
    names: dict
    category: str
    seconds: float
    make: object
    pal: dict
    res: tuple = (540, 960)
    tags: list = field(default_factory=list)


BACKGROUNDS: dict[str, Background] = {}

CATEGORIES = {
    "degradados": {"es": "Degradados y líquidos", "en": "Gradients and liquids"},
    "geometricos": {"es": "Geométricos", "en": "Geometric"},
    "ambiente": {"es": "Luces y ambiente", "en": "Lights and atmosphere"},
    "texturas": {"es": "Texturas", "en": "Textures"},
    "fechas": {"es": "Fechas especiales", "en": "Special days"},
}

# Each palette: background a/b, accents c/d, light e.
PALETTES = {
    "vibrante": {"es": "vibrante", "en": "vibrant", "a": H("#2b0a5e"), "b": H("#ff2f8e"), "c": H("#7b2bff"), "d": H("#2fd8ff"),
                 "e": H("#fff1fb")},
    "calido": {"es": "cálido", "en": "warm", "a": H("#5a1206"), "b": H("#ff8a3d"), "c": H("#ff4e50"), "d": H("#ffd23f"),
               "e": H("#fff6e6")},
    "frio": {"es": "frío", "en": "cool", "a": H("#032b43"), "b": H("#0ea5a5"), "c": H("#3d7bff"), "d": H("#9cf2e0"),
             "e": H("#effcff")},
    "oscuro": {"es": "oscuro", "en": "dark", "a": H("#07060f"), "b": H("#1b1f3a"), "c": H("#5a1f9e"), "d": H("#c9a8ff"),
               "e": H("#e8e6ff")},
}


def register(id, es, en, category, make, *, seconds=8, res=(540, 960), tags=(), palettes=PALETTES):
    for key, pal in palettes.items():
        bid = f"{id}-{key}" if len(palettes) > 1 else id
        BACKGROUNDS[bid] = Background(
            bid, {"es": f"{es} ({pal['es']})" if len(palettes) > 1 else es,
                  "en": f"{en} ({pal['en']})" if len(palettes) > 1 else en},
            category, seconds, make, pal, res, list(tags) + ["fondo", "background", pal["es"], pal["en"]])


def grid(w, h):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    return xx / w, yy / h


def mix(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return np.asarray(a, np.float32) * (1 - t) + np.asarray(b, np.float32) * t


def ramp(stops, v):
    """Colour ramp through `stops` (list of rgb) at v in 0-1 (array)."""
    pal = np.array(stops, np.float32)
    idx = np.clip(v, 0, 0.9999) * (len(pal) - 1)
    lo = np.floor(idx).astype(int)
    f = (idx - lo)[..., None]
    return pal[lo] * (1 - f) + pal[np.minimum(lo + 1, len(pal) - 1)] * f


def vgrad(w, h, top, bottom):
    _, y = grid(w, h)
    return mix(top, bottom, y)


def loop_noise(tile, w, h, t, T, speed=(30, 20), scale=1.0):
    """A tiling field that drifts and loops: crossfade between t and t - T."""
    wgt = t / T
    a = fx.sample_tile(tile, w, h, speed[0] * t, speed[1] * t, scale)
    b = fx.sample_tile(tile, w, h, speed[0] * (t - T), speed[1] * (t - T), scale)
    return a * (1 - wgt) + b * wgt


def from_canvas(base, c):
    """Composite an fx.Canvas (premultiplied) over an opaque RGB base."""
    return base * (1 - c.a[..., None]) + c.rgb


def draw_rgb(w, h, draw_fn, ss=2):
    im = Image.new("L", (w * ss, h * ss), 0)
    draw_fn(ImageDraw.Draw(im), ss)
    return np.asarray(im.resize((w, h), Image.LANCZOS), np.float32) / 255.0


# ================================================================ Degradados y líquidos

def m_gradient(w, h, T, rng, p):
    x, y = grid(w, h)
    blobs = [(p["b"], 0.0), (p["c"], 2.1), (p["d"], 4.2)]

    def frame(t):
        u = t / T
        out = np.broadcast_to(p["a"], (h, w, 3)).astype(np.float32).copy()
        for col, ph in blobs:
            cx = 0.5 + 0.35 * math.sin(TAU * u + ph)
            cy = 0.5 + 0.35 * math.cos(TAU * u * 1 + ph * 1.3)
            g = np.exp(-((x - cx) ** 2 + ((y - cy) * 0.56) ** 2) / 0.09)
            out = mix(out, col, g * 0.85)
        return out
    return frame


def m_mesh(w, h, T, rng, p):
    x, y = grid(w, h)
    pts = rng.uniform(0, 1, (6, 2))
    cols = [p["a"], p["b"], p["c"], p["d"], p["b"], p["c"]]
    ph = rng.uniform(0, TAU, 6)

    def frame(t):
        u = t / T
        wsum = np.zeros((h, w), np.float32)
        acc = np.zeros((h, w, 3), np.float32)
        for k in range(6):
            cx = pts[k, 0] + 0.15 * math.sin(TAU * u + ph[k])
            cy = pts[k, 1] + 0.15 * math.cos(TAU * u + ph[k])
            wk = 1 / (((x - cx) ** 2 + ((y - cy) * 0.6) ** 2) + 0.02) ** 1.6
            wsum += wk
            acc += wk[..., None] * np.asarray(cols[k], np.float32)
        return acc / wsum[..., None]
    return frame


def m_aurora(w, h, T, rng, p):
    x, y = grid(w, h)

    def frame(t):
        u = t / T
        out = vgrad(w, h, p["a"] * 0.6, p["a"])
        for k, (col, amp, off) in enumerate(((p["d"], 0.06, 0.3), (p["b"], 0.05, 0.42), (p["c"], 0.07, 0.55))):
            cy = off + amp * np.sin(TAU * (x * (1.5 + k * 0.4)) + TAU * u + k) + 0.03 * np.sin(TAU * (3 * x - u))
            band = np.exp(-((y - cy) ** 2) / 0.004) * (0.6 + 0.4 * np.sin(TAU * (x * 4 + u + k)) ** 2)
            curtain = np.exp(-np.clip(cy - y, 0, None) / 0.08) * (y < cy)
            out = out + np.asarray(col, np.float32) * (band * 0.7 + curtain[..., None][..., 0] * 0.25)[..., None]
        return np.clip(out, 0, 1)
    return frame


def m_diagonal(w, h, T, rng, p):
    x, y = grid(w, h)

    def frame(t):
        a = TAU * t / T
        v = (x * math.cos(a) + y * 1.78 * math.sin(a)) / 2.2 + 0.5
        v = (v + t / T) % 1.0
        return ramp([p["a"], p["c"], p["b"], p["d"], p["a"]], v)
    return frame


def m_waves(w, h, T, rng, p):
    x, y = grid(w, h)
    cols = [p["c"], p["b"], p["d"], p["e"]]

    def frame(t):
        u = t / T
        out = vgrad(w, h, p["a"], p["c"] * 0.6)
        for k in range(4):
            base = 0.45 + k * 0.13
            yy = base + 0.04 * np.sin(TAU * (x * (1 + k * 0.3)) + TAU * u * (1 if k % 2 else -1) + k)
            out = np.where((y > yy)[..., None], mix(out, cols[k], 0.75), out)
        return out
    return frame


def m_liquid(w, h, T, rng, p):
    tile = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.2)
    tile2 = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.0)

    def frame(t):
        n1 = loop_noise(tile, w, h, t, T, (12, 8), 0.35)
        n2 = loop_noise(tile2, w, h, t, T, (-8, 10), 0.3)
        v = np.sin(n1 * TAU + n2 * 2.5) * 0.5 + 0.5
        v = v * v * (3 - 2 * v)
        return ramp([p["a"], p["c"], p["b"], p["d"]], v * 0.95)
    return frame


def m_lava(w, h, T, rng, p):
    x, y = grid(w, h)
    n = 9
    cx, cy = rng.uniform(0.15, 0.85, n), rng.uniform(0, 1.2, n)
    r = rng.uniform(0.06, 0.11, n)
    ph = rng.uniform(0, TAU, n)

    def frame(t):
        u = t / T
        field_ = np.zeros((h, w), np.float32)
        for k in range(n):
            bx = cx[k] + 0.08 * math.sin(TAU * u + ph[k])
            by = (cy[k] + u * 1.2 * (1 if k % 2 else -1)) % 1.2 - 0.1
            field_ += r[k] ** 2 / (((x - bx) ** 2 + ((y - by) * 1.78) ** 2) + 1e-4)
        inside = fx.smooth(0.75, 0.95, field_)
        bg = vgrad(w, h, p["a"], p["c"] * 0.7)
        blob = ramp([p["b"], p["d"]], np.clip(y, 0, 1))
        return mix(bg, blob, inside)
    return frame


def m_smoke(w, h, T, rng, p):
    tile = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.1)

    def frame(t):
        n = loop_noise(tile, w, h, t, T, (6, -14), 0.6)
        base = vgrad(w, h, p["a"], p["c"] * 0.5)
        return mix(base, ramp([p["c"], p["b"], p["d"]], n), fx.smooth(0.35, 0.85, n) * 0.8)
    return frame


def m_clouds(w, h, T, rng, p):
    tile = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.4)

    def frame(t):
        n = loop_noise(tile, w, h, t, T, (16, 0), 0.5)
        sky = vgrad(w, h, p["c"], p["d"])
        return mix(sky, p["e"], fx.smooth(0.45, 0.8, n) * 0.85)
    return frame


def m_sunset(w, h, T, rng, p):
    x, y = grid(w, h)
    tile = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.4)

    def frame(t):
        u = t / T
        horizon = 0.64
        sky = ramp([p["a"], p["c"], p["b"], p["d"]], np.clip(y / horizon, 0, 1))
        d = np.sqrt((x - 0.5) ** 2 + ((y - horizon + 0.07) * 1.78) ** 2)
        sun = fx.smooth(0.15, 0.13, d) + np.exp(-d * 9) * 0.5
        sky = mix(sky, p["e"], np.clip(sun, 0, 1) * (y < horizon))
        n = loop_noise(tile, w, h, t, T, (10, 0), 0.7)
        sky = mix(sky, p["b"] * 0.7 + p["e"] * 0.3, fx.smooth(0.55, 0.8, n) * fx.smooth(horizon - 0.1, 0.1, y) * 0.55)
        # the sea: darker, with the sun's reflection shimmering on it
        depth = np.clip((y - horizon) / (1 - horizon), 0, 1)
        sea = mix(p["c"] * 0.8 + p["d"] * 0.2, p["a"], depth)
        shimmer = (np.sin((y * 220) + TAU * u * 2 + np.sin(x * 40) * 2) > 0.3) * np.exp(-((x - 0.5) / (0.06 + 0.25 * depth)) ** 2)
        sea = mix(sea, p["e"], shimmer * (1 - depth * 0.7) * 0.7)
        return np.where((y >= horizon)[..., None], sea, sky)
    return frame


for args in (("degradado-movil", "Degradado en movimiento", "Moving gradient", m_gradient, ["degradado", "gradient", "suave"]),
             ("degradado-malla", "Degradado de malla", "Mesh gradient", m_mesh, ["malla", "mesh", "moderno", "apple"]),
             ("aurora", "Aurora", "Aurora", m_aurora, ["aurora", "boreal", "cielo", "noche"]),
             ("degradado-diagonal", "Degradado diagonal", "Diagonal gradient", m_diagonal, ["diagonal", "degradado", "arcoiris"]),
             ("ondas-suaves", "Ondas suaves", "Soft waves", m_waves, ["ondas", "waves", "mar", "suave"]),
             ("liquido", "Líquido", "Liquid", m_liquid, ["liquido", "fluido", "marmol", "psicodelico"]),
             ("lampara-lava", "Lámpara de lava", "Lava lamp", m_lava, ["lava", "burbujas", "retro", "70s", "blob"]),
             ("humo-color", "Humo de color", "Colour smoke", m_smoke, ["humo", "smoke", "misterio"]),
             ("nubes", "Nubes", "Clouds", m_clouds, ["nubes", "cielo", "clouds", "sueño"]),
             ("atardecer", "Atardecer", "Sunset", m_sunset, ["atardecer", "sunset", "sol", "verano"])):
    i, es, en, fn, tg = args
    register(i, es, en, "degradados", fn, res=(270, 480), tags=tg)


# ================================================================ Geométricos

def m_retro_grid(w, h, T, rng, p):
    x, y = grid(w, h)
    horizon = 0.58

    def frame(t):
        u = t / T
        sky = ramp([p["a"], p["c"], p["b"]], np.clip(y / horizon, 0, 1))
        # a striped sun sitting on the horizon (distances in pixels: y counts 1.78 times x)
        d = np.sqrt((x - 0.5) ** 2 + ((y - horizon + 0.02) * 1.78) ** 2)
        cut = (np.sin((y * 90 - u * TAU)) > 0.55) & (y > horizon - 0.16)
        sun = (fx.smooth(0.3, 0.295, d) * ~cut) * (y < horizon)
        sky = mix(sky, ramp([p["d"], p["b"]], np.clip((y - horizon + 0.3) / 0.3, 0, 1)), sun)
        sky = mix(sky, p["b"], np.exp(-np.abs(y - horizon) * 40) * 0.6)
        # perspective floor: line width measured in screen pixels so it stays crisp
        z = 1 / np.maximum(y - horizon, 1e-3)
        xw = (x - 0.5) * z * 3
        dist_x = np.abs(xw - np.round(xw)) / np.maximum(3 * z / w, 1e-6)
        zw = z * 0.35 + u * 4
        dist_z = np.abs(zw - np.round(zw)) / np.maximum(0.35 * z * z / h, 1e-6)
        line = np.clip(1.6 - np.minimum(dist_x, dist_z), 0, 1) * fx.smooth(horizon, horizon + 0.05, y)
        floor = mix(p["a"] * 0.7, p["c"] * 0.5, np.clip((y - horizon) * 2, 0, 1))
        floor = mix(floor, p["d"], line)
        return np.where((y > horizon)[..., None], floor, sky)
    return frame


def m_stripes(w, h, T, rng, p):
    x, y = grid(w, h)

    def frame(t):
        v = ((x + y * 1.78) * 6 - t / T * 2) % 1.0
        a = fx.smooth(0.45, 0.5, v) - fx.smooth(0.95, 1.0, v)
        return mix(p["a"], p["b"], a * 0.9)
    return frame


def m_dots(w, h, T, rng, p):
    x, y = grid(w, h)
    n = 18

    def frame(t):
        u = t / T
        gx, gy = (x * n) % 1.0 - 0.5, (y * n * 1.78) % 1.0 - 0.5
        cx, cy = np.floor(x * n), np.floor(y * n * 1.78)
        r = 0.18 + 0.17 * np.sin(TAU * u + (cx + cy) * 0.35)
        dot = fx.smooth(r + 0.04, r, np.sqrt(gx ** 2 + gy ** 2))
        bg = vgrad(w, h, p["a"], p["c"] * 0.7)
        return mix(bg, ramp([p["b"], p["d"]], y), dot)
    return frame


def m_rings(w, h, T, rng, p):
    x, y = grid(w, h)
    d = np.sqrt((x - 0.5) ** 2 + ((y - 0.5) * 1.78) ** 2)

    def frame(t):
        v = (d * 5 - t / T * 2) % 1.0
        return ramp([p["a"], p["c"], p["b"], p["d"], p["a"]], v)
    return frame


def m_sunburst(w, h, T, rng, p):
    x, y = grid(w, h)
    ang = np.arctan2((y - 0.5) * 1.78, x - 0.5)
    d = np.sqrt((x - 0.5) ** 2 + ((y - 0.5) * 1.78) ** 2)

    def frame(t):
        rays = (np.sin(ang * 16 + TAU * t / T) > 0).astype(np.float32)
        out = mix(p["b"], p["c"], rays * 0.8)
        return mix(out, p["a"], fx.smooth(0.3, 1.3, d))
    return frame


def m_checker(w, h, T, rng, p):
    x, y = grid(w, h)

    def frame(t):
        u = t / T
        n = 8
        cx = np.floor(x * n + u * 2)
        cy = np.floor(y * n * 1.78 + u * 2)
        c = ((cx + cy) % 2).astype(np.float32)
        return mix(p["a"], p["c"], c * 0.9)
    return frame


def m_hex(w, h, T, rng, p):
    x, y = grid(w, h)
    s = 14

    def frame(t):
        u = t / T
        qx = x * s
        qy = y * s * 1.78
        # hex grid via two offset lattices
        a = np.stack([qx, qy], -1)
        r = np.array([1.0, 1.732])
        hr = r * 0.5
        ga = np.mod(a, r) - hr
        gb = np.mod(a - hr, r) - hr
        g = np.where((np.sum(ga ** 2, -1) < np.sum(gb ** 2, -1))[..., None], ga, gb)
        dist = np.max(np.stack([np.abs(g[..., 0]) * 0.866 + np.abs(g[..., 1]) * 0.5, np.abs(g[..., 1])], -1), -1)
        cell = a - g
        pulse = 0.5 + 0.5 * np.sin(TAU * u + cell[..., 0] * 0.4 + cell[..., 1] * 0.3)
        edge = fx.smooth(0.40, 0.43, dist)
        fillc = ramp([p["a"], p["c"], p["b"]], pulse * 0.9)
        return mix(fillc, p["d"], edge)
    return frame


def m_lowpoly(w, h, T, rng, p):
    cols, rows = 6, 10
    base = np.stack(np.meshgrid(np.linspace(0, 1, cols + 1), np.linspace(0, 1, rows + 1)), -1)
    jit = rng.uniform(-0.35, 0.35, base.shape) / np.array([cols, rows])
    jit[0, :, 1] = jit[-1, :, 1] = 0   # the frame's edges stay put: no gaps at the borders
    jit[:, 0, 0] = jit[:, -1, 0] = 0
    ph = rng.uniform(0, TAU, base.shape[:2])

    def frame(t):
        u = t / T
        pts = base + jit * np.stack([np.sin(TAU * u + ph), np.cos(TAU * u + ph)], -1)
        im = Image.new("RGB", (w, h))
        d = ImageDraw.Draw(im)
        for j in range(rows):
            for i in range(cols):
                quad = [pts[j, i], pts[j, i + 1], pts[j + 1, i + 1], pts[j + 1, i]]
                for tri in ((quad[0], quad[1], quad[2]), (quad[0], quad[2], quad[3])):
                    cx = sum(q[0] for q in tri) / 3
                    cy = sum(q[1] for q in tri) / 3
                    v = np.clip(cy * 0.8 + 0.2 * math.sin(TAU * u + cx * 5), 0, 1)
                    col = ramp([p["a"], p["c"], p["b"], p["d"]], np.array(v))
                    d.polygon([(q[0] * w, q[1] * h) for q in tri], fill=tuple(int(c * 255) for c in col))
        return np.asarray(im, np.float32) / 255.0
    return frame


def m_floating_shapes(w, h, T, rng, p):
    n = 26
    xs, ys = rng.uniform(0, 1, n), rng.uniform(0, 1, n)
    kinds = rng.integers(0, 4, n)
    sz = rng.uniform(0.04, 0.09, n)
    ph = rng.uniform(0, TAU, n)
    cols = [p["b"], p["c"], p["d"], p["e"]]

    def frame(t):
        u = t / T
        base = vgrad(w, h, p["a"], p["a"] * 0.7 + p["c"] * 0.3)
        im = Image.new("RGB", (w * 2, h * 2), tuple(int(c * 255) for c in p["a"]))
        imd = ImageDraw.Draw(im)
        out = base
        layer = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for k in range(n):
            cx = xs[k] * w * 2
            cy = ((ys[k] - u * 1.1) % 1.1 - 0.05) * h * 2
            r = sz[k] * w * 2
            a = ph[k] + TAU * u * (1 if k % 2 else -1)
            col = tuple(int(c * 255) for c in cols[k % 4]) + (230,)
            if kinds[k] == 0:
                d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=int(r * 0.25))
            elif kinds[k] == 1:
                d.polygon([(cx + r * math.cos(a + j * TAU / 3), cy + r * math.sin(a + j * TAU / 3)) for j in range(3)], fill=col)
            elif kinds[k] == 2:
                d.line([(cx - r, cy), (cx - r / 2, cy - r / 2), (cx, cy), (cx + r / 2, cy - r / 2), (cx + r, cy)], fill=col,
                       width=int(r * 0.2), joint="curve")
            else:
                d.polygon([(cx + r * math.cos(a + j * TAU / 4), cy + r * math.sin(a + j * TAU / 4)) for j in range(4)], fill=col)
        im = im.convert("RGBA")
        im.alpha_composite(layer)
        out = np.asarray(im.convert("RGB").resize((w, h), Image.LANCZOS), np.float32) / 255.0
        return mix(out, base, 0.35)
    return frame


def m_tunnel(w, h, T, rng, p):
    x, y = grid(w, h)
    dx, dy = x - 0.5, (y - 0.5) * 1.78
    d = np.sqrt(dx ** 2 + dy ** 2) + 1e-3
    ang = np.arctan2(dy, dx)

    def frame(t):
        u = t / T
        z = 0.3 / d + u * 2
        v = (z % 1.0)
        seg = (np.sin(ang * 8 + z * 2) > 0).astype(np.float32)
        col = ramp([p["c"], p["b"], p["d"]], v)
        col = mix(col, p["a"], seg * 0.4)
        return mix(col, p["a"], fx.smooth(0.25, 0.0, d))
    return frame


def m_spiral(w, h, T, rng, p):
    x, y = grid(w, h)
    dx, dy = x - 0.5, (y - 0.5) * 1.78
    d = np.sqrt(dx ** 2 + dy ** 2)
    ang = np.arctan2(dy, dx)

    def frame(t):
        v = ((ang / TAU) * 3 + d * 6 - t / T * 3) % 1.0
        return ramp([p["a"], p["c"], p["b"], p["d"], p["a"]], v)
    return frame


def m_memphis(w, h, T, rng, p):
    return m_floating_shapes(w, h, T, rng, {**p, "a": p["e"] * 0.15 + p["d"] * 0.85, "e": p["a"]})


def m_hills(w, h, T, rng, p):
    x, y = grid(w, h)

    def frame(t):
        u = t / T
        out = ramp([p["d"], p["e"]], np.clip(1 - y * 1.6, 0, 1))
        for k, col in enumerate((p["c"], p["b"], p["a"])):
            base = 0.62 + k * 0.12
            yy = base + 0.05 * np.sin(TAU * (x * (0.8 + k * 0.5) + u * (k + 1) * 0.5 * (1 if k % 2 else -1)) + k * 2)
            out = np.where((y > yy)[..., None], np.broadcast_to(col, out.shape), out)
        return out
    return frame


def m_circuit(w, h, T, rng, p):
    lines = []
    for _ in range(46):
        x0, y0 = rng.uniform(0, 1), rng.uniform(0, 1)
        pts = [(x0, y0)]
        for _ in range(rng.integers(2, 5)):
            if rng.random() < 0.5:
                x0 += rng.choice([-1, 1]) * rng.uniform(0.05, 0.25)
            else:
                y0 += rng.choice([-1, 1]) * rng.uniform(0.03, 0.15)
            pts.append((x0, y0))
        lines.append(pts)
    base_img = draw_rgb(w, h, lambda d, ss: [d.line([(px * w * ss, py * h * ss) for px, py in pts], fill=110, width=2 * ss)
                                              for pts in lines])
    nodes = draw_rgb(w, h, lambda d, ss: [d.ellipse([pts[-1][0] * w * ss - 5 * ss, pts[-1][1] * h * ss - 5 * ss,
                                                      pts[-1][0] * w * ss + 5 * ss, pts[-1][1] * h * ss + 5 * ss], fill=255)
                                           for pts in lines])
    x, y = grid(w, h)

    def frame(t):
        u = t / T
        pulse = 0.5 + 0.5 * np.sin(TAU * (x * 2 + y * 3 - u * 2))
        out = vgrad(w, h, p["a"], p["a"] * 0.6 + p["c"] * 0.2)
        out = mix(out, p["d"], base_img * (0.35 + 0.65 * pulse))
        return mix(out, p["e"], nodes * (0.5 + 0.5 * pulse))
    return frame


def m_equalizer(w, h, T, rng, p):
    bars = 18
    ph = rng.uniform(0, TAU, bars)
    k = rng.integers(1, 4, bars)
    x, y = grid(w, h)

    def frame(t):
        u = t / T
        out = vgrad(w, h, p["a"], p["a"] * 0.5 + p["c"] * 0.3)
        b = np.floor(x * bars).astype(int).clip(0, bars - 1)
        level = 0.25 + 0.2 * np.sin(TAU * k[b] * u + ph[b]) + 0.12 * np.sin(TAU * 2 * k[b] * u + ph[b] * 2)
        inside = ((x * bars) % 1.0 > 0.18) & ((x * bars) % 1.0 < 0.82) & (np.abs(y - 0.5) < level)
        col = ramp([p["d"], p["b"], p["c"]], np.abs(y - 0.5) * 2)
        return np.where(inside[..., None], col, out)
    return frame


for args in (("cuadricula-retro", "Cuadrícula retro", "Retro grid", m_retro_grid, ["retro", "synthwave", "80s", "grid", "vaporwave"], (540, 960)),
             ("rayas", "Rayas en movimiento", "Moving stripes", m_stripes, ["rayas", "stripes", "lineas", "dinamico"], (540, 960)),
             ("puntos", "Puntos que laten", "Pulsing dots", m_dots, ["puntos", "dots", "semitono", "pop"], (540, 960)),
             ("circulos", "Círculos concéntricos", "Concentric rings", m_rings, ["circulos", "anillos", "hipnotico"], (270, 480)),
             ("rayos-sol", "Rayos que giran", "Spinning sunburst", m_sunburst, ["rayos", "sunburst", "promo", "infantil", "oferta"], (540, 960)),
             ("ajedrez", "Cuadros en movimiento", "Moving checkers", m_checker, ["cuadros", "ajedrez", "checker", "retro"], (540, 960)),
             ("hexagonos", "Hexágonos", "Hexagons", m_hex, ["hexagonos", "panal", "tecnologia", "gaming"], (540, 960)),
             ("low-poly", "Polígonos", "Low poly", m_lowpoly, ["poligonos", "low poly", "cristal", "moderno"], (540, 960)),
             ("formas-flotantes", "Formas flotantes", "Floating shapes", m_floating_shapes, ["formas", "geometrico", "divertido"], (540, 960)),
             ("tunel", "Túnel", "Tunnel", m_tunnel, ["tunel", "tunnel", "viaje", "zoom", "psicodelico"], (270, 480)),
             ("espiral", "Espiral", "Spiral", m_spiral, ["espiral", "hipnotico", "remolino"], (270, 480)),
             ("memphis", "Estilo Memphis", "Memphis style", m_memphis, ["memphis", "80s", "pop", "formas"], (540, 960)),
             ("colinas", "Colinas", "Rolling hills", m_hills, ["colinas", "paisaje", "plano", "flat"], (270, 480)),
             ("circuito", "Circuito", "Circuit board", m_circuit, ["circuito", "tecnologia", "tech", "digital", "datos"], (540, 960)),
             ("ecualizador", "Ecualizador", "Equalizer", m_equalizer, ["ecualizador", "musica", "podcast", "audio", "dj"], (540, 960))):
    i, es, en, fn, tg, rs = args
    register(i, es, en, "geometricos", fn, res=rs, tags=tg)


# ================================================================ Luces y ambiente

def m_stars(w, h, T, rng, p):
    tile = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.3)
    n = 220
    xs, ys = rng.uniform(0, w, n), rng.uniform(0, h, n)
    r = rng.gamma(1.4, 1.2, n) + 0.6
    ph = rng.uniform(0, TAU, n)
    k = rng.integers(1, 4, n)

    def frame(t):
        u = t / T
        neb = loop_noise(tile, w, h, t, T, (4, 2), 0.6)
        out = mix(p["a"], ramp([p["c"], p["b"]], neb), fx.smooth(0.4, 0.9, neb) * 0.55)
        c = fx.Canvas(w, h)
        for i in range(n):
            b = 0.5 + 0.5 * math.sin(TAU * k[i] * u + ph[i])
            c.splat(fx.glow(max(int(r[i] * 2), 1)), xs[i], ys[i], (1, 1, 1), 0.4 + 0.6 * b, add=True)
        return np.clip(from_canvas(out, c), 0, 1)
    return frame


def m_bokeh_bg(w, h, T, rng, p):
    n = 40
    xs, ys = rng.uniform(0, w, n), rng.uniform(0, h, n)
    r = rng.uniform(20, 70, n) * w / 540
    ph = rng.uniform(0, TAU, n)
    cols = [p["b"], p["c"], p["d"], p["e"]]

    def frame(t):
        u = t / T
        out = vgrad(w, h, p["a"], p["a"] * 0.6 + p["c"] * 0.3)
        c = fx.Canvas(w, h)
        for i in range(n):
            y = (ys[i] - u * (h + 160)) % (h + 160) - 80
            c.splat(fx.bokeh(int(r[i])), xs[i] + 20 * math.sin(TAU * u + ph[i]), y, cols[i % 4],
                    0.35 + 0.25 * math.sin(TAU * u * 2 + ph[i]), add=True)
        return np.clip(from_canvas(out, c), 0, 1)
    return frame


def m_particles(w, h, T, rng, p):
    n = 180
    xs, ys = rng.uniform(0, w, n), rng.uniform(0, h, n)
    r = rng.uniform(1.5, 4.5, n)
    ph = rng.uniform(0, TAU, n)

    def frame(t):
        u = t / T
        out = m_gradient_cache(w, h, p)(t * 0 + u * T, T)
        c = fx.Canvas(w, h)
        for i in range(n):
            y = (ys[i] - u * h) % h
            c.splat(fx.glow(int(r[i] * 2.5)), xs[i] + 15 * math.sin(TAU * u + ph[i]), y, p["e"],
                    0.4 + 0.4 * math.sin(TAU * 3 * u + ph[i]), add=True)
        return np.clip(from_canvas(out, c), 0, 1)
    return frame


def m_gradient_cache(w, h, p):
    x, y = grid(w, h)

    def at(t, T):
        u = t / T
        out = vgrad(w, h, p["a"], p["c"] * 0.8)
        g = np.exp(-((x - 0.5 - 0.3 * math.sin(TAU * u)) ** 2 + ((y - 0.4) * 0.56) ** 2) / 0.1)
        return mix(out, p["b"], g * 0.6)
    return at


def m_neon_lines(w, h, T, rng, p):
    x, y = grid(w, h)

    def frame(t):
        u = t / T
        out = np.broadcast_to(p["a"] * 0.6, (h, w, 3)).astype(np.float32).copy()
        for k, col in enumerate((p["b"], p["d"], p["c"])):
            yy = 0.3 + k * 0.2 + 0.08 * np.sin(TAU * (x * 1.2 + u + k * 0.3))
            d = np.abs(y - yy)
            out = out + np.asarray(col, np.float32) * (np.exp(-d / 0.02) * 0.6 + np.exp(-(d / 0.003) ** 2))[..., None]
        return np.clip(out, 0, 1)
    return frame


def m_stage(w, h, T, rng, p):
    x, y = grid(w, h)
    beams = [(0.15, p["b"], 0.0), (0.5, p["d"], 2.0), (0.85, p["c"], 4.0)]
    tile = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.0)

    def frame(t):
        u = t / T
        haze = loop_noise(tile, w, h, t, T, (8, -6), 0.6)
        out = np.broadcast_to(p["a"], (h, w, 3)).astype(np.float32).copy() * (0.7 + 0.3 * haze[..., None])
        for bx, col, ph in beams:
            ang = 0.35 * math.sin(TAU * u + ph)
            dxl = (x - bx) - (y - 0.0) * math.tan(ang)
            beam = np.exp(-(dxl / (0.03 + 0.12 * y)) ** 2) * (0.4 + 0.6 * haze)
            out = out + np.asarray(col, np.float32) * beam[..., None] * 0.7
        return np.clip(out, 0, 1)
    return frame


def m_city_lights(w, h, T, rng, p):
    n = 120
    xs, ys = rng.uniform(0, w, n), rng.uniform(h * 0.3, h, n)
    r = rng.uniform(8, 30, n) * w / 540
    ph = rng.uniform(0, TAU, n)
    cols = [H("#ffb04a"), H("#ffe08a"), p["b"], p["d"]]

    def frame(t):
        u = t / T
        out = vgrad(w, h, p["a"] * 0.5, p["a"])
        c = fx.Canvas(w, h)
        for i in range(n):
            x = (xs[i] + u * (w + 60) * (1 if i % 3 else -1)) % (w + 60) - 30
            c.splat(fx.bokeh(int(r[i])), x, ys[i], cols[i % 4], 0.3 + 0.2 * math.sin(TAU * 2 * u + ph[i]), add=True)
        return np.clip(from_canvas(out, c), 0, 1)
    return frame


def m_snow_bg(w, h, T, rng, p):
    n = 220
    xs, ys = rng.uniform(0, w, n), rng.uniform(0, h, n)
    r = rng.uniform(1.5, 6, n)
    ph = rng.uniform(0, TAU, n)

    def frame(t):
        u = t / T
        out = vgrad(w, h, p["a"], p["c"] * 0.7)
        c = fx.Canvas(w, h)
        for i in range(n):
            y = (ys[i] + u * (h + 20) * (1 + (r[i] > 4))) % (h + 20) - 10
            c.splat(fx.glow(int(r[i] * 1.8)), xs[i] + 12 * math.sin(TAU * u * 2 + ph[i]), y, (1, 1, 1), 0.85)
        return np.clip(from_canvas(out, c), 0, 1)
    return frame


def m_rays_bg(w, h, T, rng, p):
    x, y = grid(w, h)
    ang = np.arctan2(y + 0.1, x - 0.2)

    def frame(t):
        u = t / T
        out = vgrad(w, h, p["b"], p["a"])
        r = (0.5 + 0.5 * np.sin(ang * 22 + TAU * u)) * (0.5 + 0.5 * np.sin(ang * 35 - TAU * 2 * u))
        return mix(out, p["e"], r ** 2 * fx.smooth(1.4, 0.0, np.sqrt((x - 0.2) ** 2 + (y + 0.1) ** 2)) * 0.6)
    return frame


def m_galaxy(w, h, T, rng, p):
    x, y = grid(w, h)
    dx, dy = x - 0.5, (y - 0.5) * 1.78
    d = np.sqrt(dx ** 2 + dy ** 2)
    ang = np.arctan2(dy, dx)
    tile = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=1.8)

    def frame(t):
        u = t / T
        arm = 0.5 + 0.5 * np.sin(ang * 2 - d * 14 + TAU * u)
        n = loop_noise(tile, w, h, t, T, (3, 3), 0.8)
        v = arm * np.exp(-d * 2.5) * (0.6 + 0.4 * n)
        out = mix(p["a"], ramp([p["c"], p["b"], p["e"]], np.clip(v * 1.5, 0, 1)), np.clip(v * 1.8, 0, 1))
        return mix(out, p["e"], np.exp(-(d / 0.04) ** 2))
    return frame


def m_fireflies_bg(w, h, T, rng, p):
    n = 60
    cx, cy = rng.uniform(0, w, n), rng.uniform(0, h, n)
    ax = rng.uniform(15, 50, n)
    ph = rng.uniform(0, TAU, (n, 3))
    k = rng.integers(1, 3, n)

    def frame(t):
        u = t / T
        out = vgrad(w, h, p["a"] * 0.7, p["a"] * 0.5 + p["c"] * 0.3)
        c = fx.Canvas(w, h)
        for i in range(n):
            x = cx[i] + ax[i] * math.sin(TAU * k[i] * u + ph[i, 0])
            y = cy[i] + ax[i] * math.cos(TAU * u + ph[i, 1])
            b = max(0.0, math.sin(TAU * k[i] * u + ph[i, 2])) ** 2
            c.splat(fx.glow(26), x, y, p["d"], 0.6 * b, add=True)
            c.splat(fx.glow(7), x, y, p["e"], b, add=True)
        return np.clip(from_canvas(out, c), 0, 1)
    return frame


for args in (("cielo-estrellado", "Cielo estrellado", "Starry sky", m_stars, ["estrellas", "noche", "espacio", "cielo"]),
             ("bokeh", "Bokeh", "Bokeh", m_bokeh_bg, ["bokeh", "luces", "desenfoque", "elegante"]),
             ("particulas", "Partículas", "Particles", m_particles, ["particulas", "polvo", "suave", "calma"]),
             ("neon", "Líneas de neón", "Neon lines", m_neon_lines, ["neon", "lineas", "noche", "cyber"]),
             ("escenario", "Luces de escenario", "Stage lights", m_stage, ["escenario", "concierto", "show", "luces"]),
             ("luces-ciudad", "Luces de ciudad", "City lights", m_city_lights, ["ciudad", "noche", "bokeh", "urbano"]),
             ("nieve", "Nieve", "Snowfall", m_snow_bg, ["nieve", "invierno", "navidad", "frio"]),
             ("rayos-luz", "Rayos de luz", "Light rays", m_rays_bg, ["rayos", "luz", "cielo", "esperanza"]),
             ("galaxia", "Galaxia", "Galaxy", m_galaxy, ["galaxia", "espacio", "universo", "cosmos"]),
             ("luciernagas", "Luciérnagas", "Fireflies", m_fireflies_bg, ["luciernagas", "noche", "magia", "bosque"])):
    i, es, en, fn, tg = args
    register(i, es, en, "ambiente", fn, res=(540, 960), tags=tg)


def m_soundwave(w, h, T, rng, p):
    x, y = grid(w, h)

    def frame(t):
        u = t / T
        out = vgrad(w, h, p["a"], p["a"] * 0.6 + p["c"] * 0.3)
        for k, col in enumerate((p["c"], p["b"], p["d"])):
            env = 0.6 + 0.4 * np.sin(TAU * (x * 1.5 + u + k * 0.3))
            yy = 0.5 + 0.08 * env * np.sin(TAU * (x * (6 + k * 2) - u * (2 + k)))
            out = out + np.asarray(col, np.float32) * np.exp(-((y - yy) / 0.004) ** 2)[..., None] * 0.9
        return np.clip(out, 0, 1)
    return frame


def m_bubbles_bg(w, h, T, rng, p):
    n = 30
    xs, ys = rng.uniform(0, w, n), rng.uniform(0, h, n)
    r = rng.uniform(10, 45, n) * w / 540
    ph = rng.uniform(0, TAU, n)

    def frame(t):
        u = t / T
        out = vgrad(w, h, p["c"], p["a"])
        c = fx.Canvas(w, h)
        for i in range(n):
            y = (ys[i] - u * (h + 100)) % (h + 100) - 50
            c.splat(fx.bubble(int(r[i])), xs[i] + 15 * math.sin(TAU * 2 * u + ph[i]), y, p["e"], 0.8)
        return np.clip(from_canvas(out, c), 0, 1)
    return frame


def m_confetti_bg(w, h, T, rng, p):
    n = 60
    xs, ys = rng.uniform(0, w, n), rng.uniform(0, h, n)
    sz = rng.uniform(8, 16, n) * w / 540
    ph = rng.uniform(0, TAU, (n, 2))
    cols = [p["b"], p["c"], p["d"], p["e"]]

    def frame(t):
        u = t / T
        out = vgrad(w, h, p["a"], p["a"] * 0.6 + p["b"] * 0.3)
        c = fx.Canvas(w, h)
        for i in range(n):
            y = (ys[i] + u * (h + 40)) % (h + 40) - 20
            a = ph[i, 0] + TAU * u * 2
            c.splat(fx.confetti(int(sz[i] * 2), 0.5, a, math.cos(ph[i, 1] + TAU * 3 * u)), xs[i] + 20 * math.sin(TAU * u + ph[i, 1]),
                    y, cols[i % 4], 0.85)
        return np.clip(from_canvas(out, c), 0, 1)
    return frame


def m_light_rain_bg(w, h, T, rng, p):
    n = 50
    xs, ys = rng.uniform(0, w, n), rng.uniform(0, h, n)
    ln = rng.uniform(60, 160, n) * w / 540
    laps = rng.integers(1, 3, n)
    cols = [p["b"], p["c"], p["d"]]

    def frame(t):
        u = t / T
        out = vgrad(w, h, p["a"] * 0.6, p["a"])
        c = fx.Canvas(w, h)
        for i in range(n):
            y = (ys[i] + laps[i] * u * (h + 2 * ln[i])) % (h + 2 * ln[i]) - ln[i]
            c.splat(fx.streak_at(ln[i], 4, 0), xs[i], y, cols[i % 3], 0.8, add=True)
        return np.clip(from_canvas(out, c), 0, 1)
    return frame


def m_prism_bg(w, h, T, rng, p):
    x, y = grid(w, h)
    lut = np.array([fx.hsv(v, 0.55, 1.0) for v in np.linspace(0, 0.85, 256)], np.float32)

    def frame(t):
        u = t / T
        base = vgrad(w, h, p["e"], p["d"] * 0.6 + p["e"] * 0.4)
        out = base
        for k in range(3):
            pos = 0.2 + 0.6 * (0.5 + 0.5 * math.sin(TAU * u + k * 2.1))
            d = (x * 0.6 + y * 0.8 - pos) / (0.08 + 0.04 * k)
            band = np.clip(1 - np.abs(d), 0, 1) ** 1.5
            col = lut[np.clip((d + 1) / 2 * 255, 0, 255).astype(int)]
            out = mix(out, col, band * 0.55)
        return out
    return frame


for args in (("ondas-sonido", "Ondas de sonido", "Sound waves", m_soundwave, ["ondas", "sonido", "podcast", "musica", "audio"]),
             ("burbujas", "Burbujas", "Bubbles", m_bubbles_bg, ["burbujas", "agua", "infantil", "suave"]),
             ("confeti", "Confeti suave", "Soft confetti", m_confetti_bg, ["confeti", "fiesta", "celebracion", "cumpleaños"]),
             ("lluvia-luces", "Lluvia de luces", "Light rain", m_light_rain_bg, ["luces", "lluvia de luces", "noche", "fiesta"]),
             ("prisma", "Prisma", "Prism", m_prism_bg, ["prisma", "arcoiris", "cristal", "aesthetic"])):
    i, es, en, fn, tg = args
    register(i, es, en, "ambiente", fn, res=(540, 960), tags=tg)


# ================================================================ Texturas

def m_paper(w, h, T, rng, p):
    fib = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=1.0)
    blot = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.4)

    def frame(t):
        i = int(t * 6) % 3
        f = fx.sample_tile(fib, w, h, i * 41, i * 17, 0.7)
        b = loop_noise(blot, w, h, t, T, (2, 1), 0.5)
        base = mix(p["e"] * 0.92 + p["d"] * 0.08, p["d"], b * 0.25)
        return np.clip(base - (f[..., None] - 0.5) * 0.08, 0, 1)
    return frame


def m_chalk(w, h, T, rng, p):
    n1 = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=1.2)
    smudge = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.4)

    def frame(t):
        i = int(t * 6) % 3
        g = fx.sample_tile(n1, w, h, i * 23, i * 31, 0.8)
        s = loop_noise(smudge, w, h, t, T, (2, 2), 0.5)
        board = p["a"] * 0.25 + H("#2c4a3a") * 0.75
        x, y = grid(w, h)
        board = mix(board, board * 0.7, fx.vignette(w, h, 0.3, 1.3))
        return np.clip(mix(board, p["e"], fx.smooth(0.5, 0.9, s) * 0.22) + (g[..., None] - 0.5) * 0.1, 0, 1)
    return frame


def m_marble(w, h, T, rng, p):
    tile = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.7)
    x, y = grid(w, h)

    def frame(t):
        n = loop_noise(tile, w, h, t, T, (3, 5), 0.35)
        veins = np.abs(np.sin((x * 1.2 + y * 2.0 + n * 3.0) * math.pi))
        fine = np.abs(np.sin((x * 2.5 - y * 1.5 + n * 5.0) * math.pi))
        base = mix(p["e"], p["d"] * 0.35 + p["e"] * 0.65, n)
        out = mix(p["c"] * 0.6 + p["e"] * 0.4, base, fx.smooth(0.0, 0.12, veins))
        return mix(p["c"] * 0.4 + p["e"] * 0.6, out, fx.smooth(0.0, 0.05, fine) * 0.6 + 0.4)
    return frame


def m_watercolor(w, h, T, rng, p):
    tile = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.0)
    edge = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=1.4)

    def frame(t):
        n = loop_noise(tile, w, h, t, T, (5, 4), 0.5)
        e = fx.sample_tile(edge, w, h, 0, 0, 1.0)
        v = n + (e - 0.5) * 0.15
        col = ramp([p["b"], p["c"], p["d"]], np.clip(v, 0, 1))
        paper = p["e"]
        a = fx.smooth(0.3, 0.55, v) * 0.6 + (fx.smooth(0.5, 0.53, v) - fx.smooth(0.53, 0.58, v)) * 0.15
        return mix(paper, col, np.clip(a, 0, 1))
    return frame


def m_ink(w, h, T, rng, p):
    tile = fx.tile_noise(512, int(rng.integers(1, 9999)), falloff=2.2)
    x, y = grid(w, h)

    def frame(t):
        n = loop_noise(tile, w, h, t, T, (0, -10), 0.5)
        warp = loop_noise(tile, w, h, t, T, (6, 4), 0.25)
        dens = fx.smooth(0.4, 0.8, n * 0.7 + warp * 0.5)
        tone = np.clip(warp * 1.2 - 0.1, 0, 1)
        return mix(p["e"], ramp([p["c"], p["b"], p["a"]], tone), dens * 0.92)
    return frame


for args in (("papel", "Papel", "Paper", m_paper, ["papel", "paper", "textura", "collage", "vintage"]),
             ("pizarra", "Pizarra", "Chalkboard", m_chalk, ["pizarra", "escuela", "clase", "educacion"]),
             ("marmol", "Mármol", "Marble", m_marble, ["marmol", "marble", "elegante", "lujo"]),
             ("acuarela", "Acuarela", "Watercolour", m_watercolor, ["acuarela", "pintura", "arte", "suave"]),
             ("tinta", "Tinta en agua", "Ink in water", m_ink, ["tinta", "agua", "arte", "fluido"])):
    i, es, en, fn, tg = args
    register(i, es, en, "texturas", fn, res=(540, 960), tags=tg)


# ================================================================ Fechas especiales (2 versions each)

def seasonal(bg_a, bg_b, particle, colours, extra=None):
    def make(w, h, T, rng, p):
        n = 70
        xs, ys = rng.uniform(0, w, n), rng.uniform(0, h, n)
        sz = rng.uniform(10, 24, n) * w / 540
        ph = rng.uniform(0, TAU, (n, 2))
        cols = [H(c) for c in colours]
        rise = particle in ("heart", "balloon_dot")

        def frame(t):
            u = t / T
            out = vgrad(w, h, H(bg_a), H(bg_b))
            if extra:
                out = extra(out, w, h, u)
            c = fx.Canvas(w, h)
            for i in range(n):
                m = 40
                y = (ys[i] + (-1 if rise else 1) * u * (h + 2 * m)) % (h + 2 * m) - m
                x = xs[i] + 20 * math.sin(TAU * u + ph[i, 0])
                k = int(sz[i])
                a = ph[i, 1] + TAU * u
                if particle == "heart":
                    spr = fx.heart(k * 2)
                elif particle == "star":
                    spr = fx.star5(k * 2, fx._q(a))
                elif particle == "snow":
                    spr = fx.glow(k // 2 + 1)
                elif particle == "leaf":
                    spr = fx.leaf(k * 3, fx._q(a), fx._qs(math.cos(a * 2)))
                elif particle == "petal":
                    spr = fx.petal(k * 2, fx._q(a), fx._qs(math.cos(a * 2)))
                else:
                    spr = fx.confetti(k * 2, 0.5, a, math.cos(a * 3))
                c.splat(spr, x, y, cols[i % len(cols)], 0.9)
            return np.clip(from_canvas(out, c), 0, 1)
        return frame
    return make


def moon_lantern(out, w, h, u):
    x, y = grid(w, h)
    moon = (np.sqrt((x - 0.72) ** 2 + ((y - 0.16) * 1.78) ** 2) < 0.14) & ~(np.sqrt((x - 0.78) ** 2 + ((y - 0.145) * 1.78) ** 2) < 0.125)
    return mix(out, H("#ffe39a"), moon.astype(np.float32))


def bunting(out, w, h, u):
    flags = draw_rgb(w, h, lambda d, ss: [d.polygon([((k * 0.1 + 0.02) * w * ss, (0.06 + 0.02 * math.sin(k + TAU * u)) * h * ss),
                                                     ((k * 0.1 + 0.1) * w * ss, (0.06 + 0.02 * math.sin(k + 1 + TAU * u)) * h * ss),
                                                     ((k * 0.1 + 0.06) * w * ss, (0.12 + 0.02 * math.sin(k + 0.5 + TAU * u)) * h * ss)],
                                                    fill=255) for k in range(10)])
    return mix(out, H("#ffd23f"), flags)


SEASONAL = [
    ("navidad", "Navidad", "Christmas", "#0b3d2e", "#7a0d1a", "snow", ["#ffffff", "#ffe39a"], None,
     ["navidad", "christmas", "diciembre", "fiestas"], "#0b3d2e", "#c8102e"),
    ("anio-nuevo", "Año Nuevo", "New Year", "#0b0b2a", "#3a2a00", "star", ["#ffd27a", "#ffffff", "#ffb84d"], None,
     ["año nuevo", "new year", "brindis", "fiesta"], "#1a1a1a", "#5a4300"),
    ("san-valentin", "San Valentín", "Valentine's Day", "#ff9ec0", "#c8102e", "heart", ["#ffffff", "#ff4d7d", "#ffd6e5"], None,
     ["san valentin", "amor", "corazones", "febrero"], "#ffd6e5", "#ff4d7d"),
    ("halloween", "Halloween", "Halloween", "#1a0b2e", "#ff6a00", "leaf", ["#ff8c00", "#5a1f9e", "#1a1a1a"], None,
     ["halloween", "terror", "octubre", "calabaza"], "#0d0d0d", "#5a1f9e"),
    ("cumpleanos", "Cumpleaños", "Birthday", "#3d7bff", "#b26bff", "confetti", ["#ff4d6d", "#ffd23f", "#3ec1ff", "#7bf06a"], bunting,
     ["cumpleaños", "birthday", "fiesta", "celebracion"], "#ff8fb3", "#ffd23f"),
    ("graduacion", "Graduación", "Graduation", "#0b1f4a", "#1b2f6a", "star", ["#ffd27a", "#ffffff"], None,
     ["graduacion", "graduation", "logro", "promocion"], "#2a0a0a", "#5a1010"),
    ("primavera", "Primavera", "Spring", "#d8f5c8", "#7fcf8a", "petal", ["#ff9ec7", "#ffffff", "#ffd23f"], None,
     ["primavera", "spring", "flores", "dia de la madre"], "#fff0f5", "#ffb0c8"),
    ("otono", "Otoño", "Autumn", "#ffd9a0", "#b3420a", "leaf", ["#d9480f", "#f08c00", "#a61e4d"], None,
     ["otoño", "autumn", "hojas", "accion de gracias"], "#5a2a0a", "#c2a000"),
    ("ramadan", "Ramadán y Eid", "Ramadan and Eid", "#0b1f3a", "#1f4a5a", "star", ["#ffe39a", "#ffffff"], moon_lantern,
     ["ramadan", "eid", "luna", "noche"], "#1a0b3a", "#3a1f6a"),
    ("diwali", "Diwali", "Diwali", "#3a0a2a", "#ff8a3d", "snow", ["#ffd27a", "#ffb04a", "#ff6a3d"], None,
     ["diwali", "luces", "festival", "velas"], "#2a0a4a", "#ffb000"),
]

for sid, es, en, a, b, part, cols, extra, tg, a2, b2 in SEASONAL:
    make1 = seasonal(a, b, part, cols, extra)
    make2 = seasonal(a2, b2, part, cols[::-1], extra)
    BACKGROUNDS[sid] = Background(sid, {"es": es, "en": en}, "fechas", 8, make1, PALETTES["vibrante"], (540, 960),
                                  tg + ["fondo", "background"])
    BACKGROUNDS[sid + "-2"] = Background(sid + "-2", {"es": f"{es} 2", "en": f"{en} 2"}, "fechas", 8, make2, PALETTES["vibrante"],
                                         (540, 960), tg + ["fondo", "background"])
