"""Drawing kit for the Stock overlays: a premultiplied RGBA canvas, soft sprites and loop-safe motion.

Everything is numpy. A canvas holds premultiplied colour (H, W, 3) and coverage (H, W), both 0-1
floats; `to_rgba8` turns it into the straight-alpha bytes ffmpeg encodes as VP9 with alpha.

Loops: a design that loops runs for T seconds and every moving quantity is periodic in T (integer
wraps, integer sine cycles), so the last frame flows into the first with no seam.
"""

from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

TAU = math.tau
FONTS = Path(__file__).resolve().parents[3] / "flip-addons" / "build" / "src" / "fonts"


class Canvas:
    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.rgb = np.zeros((h, w, 3), np.float32)
        self.a = np.zeros((h, w), np.float32)

    def splat(self, spr: np.ndarray, cx: float, cy: float, color, opacity: float = 1.0, add: bool = False):
        """Draws sprite `spr` (coverage, h x w) centred on (cx, cy)."""
        if opacity <= 0.002:
            return
        sh, sw = spr.shape
        x0 = int(round(cx - sw / 2))
        y0 = int(round(cy - sh / 2))
        x1, y1 = x0 + sw, y0 + sh
        cx0, cy0 = max(x0, 0), max(y0, 0)
        cx1, cy1 = min(x1, self.w), min(y1, self.h)
        if cx0 >= cx1 or cy0 >= cy1:
            return
        a = spr[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0] * opacity
        col = np.asarray(color, np.float32)
        region = self.rgb[cy0:cy1, cx0:cx1]
        cov = self.a[cy0:cy1, cx0:cx1]
        if add:
            region += a[..., None] * col
            cov[...] = 1 - (1 - cov) * (1 - a)
        else:
            region *= (1 - a)[..., None]
            region += a[..., None] * col
            cov[...] = cov * (1 - a) + a

    def layer(self, rgb: np.ndarray, a: np.ndarray):
        """Composites a full-size straight-colour layer over the canvas."""
        self.rgb *= (1 - a)[..., None]
        self.rgb += rgb * a[..., None]
        self.a = self.a * (1 - a) + a

    def merge(self, other: "Canvas", opacity: float = 1.0):
        """Composites another (premultiplied) canvas of the same size over this one."""
        oa = other.a * opacity
        self.rgb *= (1 - oa)[..., None]
        self.rgb += other.rgb * opacity
        self.a = self.a * (1 - oa) + oa

    def fill(self, color, alpha):
        """A flat colour over everything; `alpha` is a number or an (h, w) array."""
        a = np.broadcast_to(np.asarray(alpha, np.float32), (self.h, self.w)).copy()
        self.layer(np.broadcast_to(np.asarray(color, np.float32), (self.h, self.w, 3)).copy(), a)

    def image(self, img: Image.Image, x: int, y: int, color=(1, 1, 1), opacity: float = 1.0):
        """Pastes the alpha of a PIL 'L' image (text, icons) at its top-left corner."""
        arr = np.asarray(img, np.float32) / 255.0
        self.splat(arr, x + arr.shape[1] / 2, y + arr.shape[0] / 2, color, opacity)

    def to_rgba8(self) -> np.ndarray:
        a = np.clip(self.a, 0, 1)
        col = np.clip(self.rgb / np.maximum(a, 1e-4)[..., None], 0, 1)
        out = np.empty((self.h, self.w, 4), np.uint8)
        out[..., :3] = (col * 255 + 0.5).astype(np.uint8)
        out[..., 3] = (a * 255 + 0.5).astype(np.uint8)
        return out


# ---------------------------------------------------------------- sprites (coverage arrays)

def _grid(r: float, pad: float = 1.0):
    n = int(math.ceil(r * pad)) + 1
    y, x = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
    return x, y


@lru_cache(maxsize=512)
def glow(r: int) -> np.ndarray:
    """Gaussian blob whose visible radius is about r."""
    r = max(r, 1)
    x, y = _grid(r, 1.6)
    s = r / 2.2
    return np.exp(-(x * x + y * y) / (2 * s * s)).astype(np.float32)


@lru_cache(maxsize=512)
def disc(r: int, soft: float = 1.0) -> np.ndarray:
    r = max(r, 1)
    x, y = _grid(r + soft + 1)
    d = np.sqrt(x * x + y * y)
    return np.clip((r - d) / max(soft, 0.5) + 0.5, 0, 1).astype(np.float32)


@lru_cache(maxsize=256)
def bokeh(r: int) -> np.ndarray:
    """A lens bokeh disc: flat body, a brighter rim, a soft edge."""
    r = max(r, 2)
    x, y = _grid(r + 3)
    d = np.sqrt(x * x + y * y) / r
    body = np.clip((1 - d) * r / 2.5 + 0.5, 0, 1)
    rim = np.exp(-((d - 0.93) ** 2) / 0.004) * 0.35
    return np.clip(body * (0.55 + 0.1 * d) + rim * body, 0, 1).astype(np.float32)


@lru_cache(maxsize=256)
def sparkle(r: int) -> np.ndarray:
    """Four-point star: two thin streaks and a hot centre."""
    r = max(r, 2)
    x, y = _grid(r)
    ax, ay = np.abs(x), np.abs(y)
    w = max(r / 14, 0.7)
    streak = np.exp(-(ay ** 2) / (2 * w * w)) * np.clip(1 - ax / r, 0, 1) ** 2
    streak = np.maximum(streak, np.exp(-(ax ** 2) / (2 * w * w)) * np.clip(1 - ay / r, 0, 1) ** 2)
    core = np.exp(-(x * x + y * y) / (2 * (r / 7) ** 2))
    return np.clip(streak + core, 0, 1).astype(np.float32)


@lru_cache(maxsize=256)
def ring(r: int, width: float = 2.0) -> np.ndarray:
    x, y = _grid(r + width + 2)
    d = np.sqrt(x * x + y * y)
    return np.clip(width / 2 - np.abs(d - r) + 0.5, 0, 1).astype(np.float32)


def _poly_sprite(points, size: int, ss: int = 4) -> np.ndarray:
    """Antialiased polygon from points in [-1, 1] coordinates, drawn into a size x size box."""
    big = size * ss
    im = Image.new("L", (big, big), 0)
    pts = [((px * 0.5 + 0.5) * (big - 1), (py * 0.5 + 0.5) * (big - 1)) for px, py in points]
    ImageDraw.Draw(im).polygon(pts, fill=255)
    im = im.resize((size, size), Image.LANCZOS)
    return np.asarray(im, np.float32) / 255.0


def _rotate(points, angle: float, sx: float = 1.0, sy: float = 1.0):
    c, s = math.cos(angle), math.sin(angle)
    return [((px * sx) * c - (py * sy) * s, (px * sx) * s + (py * sy) * c) for px, py in points]


ANGLES = 36


def _q(angle: float) -> int:
    return int(round((angle % TAU) / TAU * ANGLES)) % ANGLES


def _qs(v: float) -> int:
    return int(round(np.clip(abs(v), 0, 1) * 8))


@lru_cache(maxsize=4096)
def rect(size: int, aspect: float, qa: int, qsq: int) -> np.ndarray:
    """Confetti: a rectangle rotated by qa/ANGLES of a turn and squashed (3-D flip) by qsq/8."""
    hw, hh = 0.9, 0.9 * aspect
    sq = max(qsq / 8, 0.12)
    pts = [(-hw * sq, -hh), (hw * sq, -hh), (hw * sq, hh), (-hw * sq, hh)]
    return _poly_sprite(_rotate(pts, qa / ANGLES * TAU), size)


def confetti(size: int, aspect: float, angle: float, flip: float) -> np.ndarray:
    return rect(size, round(aspect, 1), _q(angle), _qs(flip))


@lru_cache(maxsize=1024)
def heart(size: int, qa: int = 0) -> np.ndarray:
    pts = []
    for i in range(64):
        t = i / 64 * TAU
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((x / 17.5, (y + 2.5) / 17.5))
    return _poly_sprite(_rotate(pts, qa / ANGLES * TAU), size)


@lru_cache(maxsize=1024)
def petal(size: int, qa: int, qsq: int) -> np.ndarray:
    """Rose / cherry petal: a teardrop with a small notch at the wide end."""
    pts = []
    for i in range(48):
        t = i / 48 * TAU
        x = math.sin(t) * (0.55 + 0.25 * math.cos(t))
        y = -math.cos(t) * 0.9
        if y < -0.78:
            y += 0.12 * (1 - abs(x) / 0.3) if abs(x) < 0.3 else 0
        pts.append((x, y))
    return _poly_sprite(_rotate(pts, qa / ANGLES * TAU, sx=max(qsq / 8, 0.15)), size)


@lru_cache(maxsize=1024)
def leaf(size: int, qa: int, qsq: int) -> np.ndarray:
    """A pointed leaf (vesica) with a short stem."""
    pts = []
    for i in range(40):
        t = i / 40 * TAU
        pts.append((math.sin(t) * 0.42 * abs(math.sin(t)) ** 0.3, -math.cos(t) * 0.85))
    pts += [(0.04, 0.85), (0.04, 0.98), (-0.04, 0.98), (-0.04, 0.85)]
    return _poly_sprite(_rotate(pts, qa / ANGLES * TAU, sx=max(qsq / 8, 0.15)), size)


@lru_cache(maxsize=256)
def star5(size: int, qa: int = 0) -> np.ndarray:
    pts = []
    for i in range(10):
        r = 1.0 if i % 2 == 0 else 0.42
        t = i / 10 * TAU
        pts.append((math.sin(t) * r * 0.95, -math.cos(t) * r * 0.95 + 0.05))
    return _poly_sprite(_rotate(pts, qa / ANGLES * TAU), size)


@lru_cache(maxsize=256)
def bubble(r: int) -> np.ndarray:
    x, y = _grid(r + 3)
    d = np.sqrt(x * x + y * y) / r
    edge = np.clip((1 - d) * r / 1.5 + 0.5, 0, 1)
    shell = edge * (0.08 + 0.75 * np.clip(d, 0, 1) ** 6)
    hx, hy = x / r + 0.38, y / r + 0.38
    hi = np.exp(-(hx * hx + hy * hy) / 0.012) * 0.9
    return np.clip(shell + hi * edge, 0, 1).astype(np.float32)


@lru_cache(maxsize=512)
def streak(length: int, width: float, qa: int) -> np.ndarray:
    """A line that fades from its head (centre-bottom) to its tail: rain, sparks, shooting stars."""
    n = length + 4
    y, x = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
    a = qa / ANGLES * TAU
    c, s = math.cos(a), math.sin(a)
    u = x * s + y * c          # along the streak (head at +length/2)
    v = x * c - y * s          # across
    along = np.clip((u + length / 2) / length, 0, 1)
    inside = (u > -length / 2) & (u < length / 2)
    cover = np.exp(-(v * v) / (2 * (width / 2) ** 2)) * along ** 1.5 * inside
    return cover.astype(np.float32)


def streak_at(length: float, width: float, angle: float) -> np.ndarray:
    return streak(max(int(length), 2), round(width, 1), _q(angle))


# ---------------------------------------------------------------- fields

def tile_noise(n: int, seed: int, falloff: float = 1.8, lo: int = 2) -> np.ndarray:
    """Seamlessly tiling fractal noise (n x n, 0-1), made by shaping white noise in frequency."""
    rng = np.random.default_rng(seed)
    white = rng.standard_normal((n, n))
    f = np.fft.fftfreq(n) * n
    fx, fy = np.meshgrid(f, f)
    k = np.sqrt(fx * fx + fy * fy)
    amp = np.where(k < lo, 0, 1 / np.maximum(k, 1) ** falloff)
    out = np.real(np.fft.ifft2(np.fft.fft2(white) * amp))
    out -= out.min()
    return (out / out.max()).astype(np.float32)


def sample_tile(tile: np.ndarray, w: int, h: int, ox: float, oy: float, scale: float = 1.0) -> np.ndarray:
    """A w x h window into a tiling field, offset by (ox, oy) tile pixels, zoomed by `scale`."""
    n = tile.shape[0]
    xs = (np.arange(w) * scale + ox) % n
    ys = (np.arange(h) * scale + oy) % n
    x0 = np.floor(xs).astype(int) % n   # a float modulo can land exactly on n
    y0 = np.floor(ys).astype(int) % n
    fx = (xs - x0)[None, :]
    fy = (ys - y0)[:, None]
    x1 = (x0 + 1) % n
    y1 = (y0 + 1) % n
    a = tile[y0][:, x0]
    b = tile[y0][:, x1]
    c = tile[y1][:, x0]
    d = tile[y1][:, x1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def smooth(e0: float, e1: float, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def ease_out(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def envelope(t: float, attack: float, hold_end: float, release: float) -> float:
    """0 -> 1 over `attack`, 1 until `hold_end`, then down to 0 over `release`."""
    if t < attack:
        return t / attack if attack > 0 else 1.0
    if t < hold_end:
        return 1.0
    return max(0.0, 1 - (t - hold_end) / release) if release > 0 else 0.0


@lru_cache(maxsize=64)
def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = next(FONTS.rglob(name))
    return ImageFont.truetype(str(path), size)


def text_image(text: str, font_name: str, size: int) -> Image.Image:
    f = font(font_name, size)
    box = f.getbbox(text)
    im = Image.new("L", (box[2] - box[0] + 4, box[3] - box[1] + 4), 0)
    ImageDraw.Draw(im).text((2 - box[0], 2 - box[1]), text, font=f, fill=255)
    return im


def hex_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def vignette(w: int, h: int, inner: float = 0.55, outer: float = 1.05, round_: float = 1.0) -> np.ndarray:
    """Coverage that is 0 in the middle and rises towards the corners."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = (xx / w - 0.5) * 2, (yy / h - 0.5) * 2
    d = (np.abs(nx) ** (2 * round_) + np.abs(ny) ** (2 * round_)) ** (1 / (2 * round_))
    return smooth(inner, outer, d).astype(np.float32)


def hsv(hh: float, s: float = 1.0, v: float = 1.0):
    import colorsys
    return colorsys.hsv_to_rgb(hh % 1.0, s, v)


def blur_sprite(spr: np.ndarray, radius: float) -> np.ndarray:
    from PIL import ImageFilter
    pad = int(radius * 3) + 1
    im = Image.fromarray((np.pad(spr, pad) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(radius))
    return np.asarray(im, np.float32) / 255.0


def draw_layer(w: int, h: int):
    """A blank 'L' image and its drawer, for UI lines, text and icons."""
    im = Image.new("L", (w, h), 0)
    return im, ImageDraw.Draw(im)
