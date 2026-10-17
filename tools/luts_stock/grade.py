"""Colour grading kit for the Stock LUTs: every operation works on (..., 3) float RGB in 0-1 (display-referred).

A look is a list of (operation, params) applied in order; `apply_look` runs it on any array, so the same
function grades the sample photo for the card and samples the 33-point cube for the .cube file.
"""

from __future__ import annotations

import numpy as np

W = np.array([0.2126, 0.7152, 0.0722], np.float32)


def luma(x):
    return x @ W


def clip(x):
    return np.clip(x, 0.0, 1.0)


def smooth(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- operations

def exposure(x, stops=0.0):
    return x * (2.0 ** stops)


def contrast(x, amount=0.0, pivot=0.45):
    """S-curve around the pivot that never clips: amount -1..1."""
    if amount >= 0:
        s = x * x * (3 - 2 * x)
        return x + (s - x) * amount * 1.4
    return pivot + (x - pivot) * (1 + amount * 0.6)


def lift_gamma_gain(x, lift=(0, 0, 0), gamma=(1, 1, 1), gain=(1, 1, 1)):
    lift, gamma, gain = (np.asarray(v, np.float32) for v in (lift, gamma, gain))
    y = x * gain + lift * (1 - x)
    return np.power(clip(y), 1.0 / gamma)


def white_balance(x, temp=0.0, tint=0.0):
    """temp > 0 warmer (more red, less blue), tint > 0 more magenta. About -1..1."""
    m = np.array([1 + 0.12 * temp + 0.03 * tint, 1 - 0.06 * tint, 1 - 0.14 * temp + 0.03 * tint], np.float32)
    return x * m


def saturation(x, amount=1.0):
    l = luma(x)[..., None]
    return l + (x - l) * amount


def vibrance(x, amount=0.0):
    """More colour where there is little; protects already saturated (and skin) colours."""
    mx, mn = x.max(-1, keepdims=True), x.min(-1, keepdims=True)
    sat = mx - mn
    k = 1 + amount * (1 - sat) ** 2
    l = luma(x)[..., None]
    return l + (x - l) * k


def fade(x, amount=0.0, tone=(0, 0, 0)):
    """Lifts the blacks (and lowers the whites a touch) toward `tone`, like faded print."""
    tone = np.asarray(tone, np.float32)
    return x * (1 - amount) + amount * (0.5 * x + tone * 0.5 + 0.08) * (1 - x * 0.6)


def split_tone(x, shadows=(0, 0, 0), highlights=(0, 0, 0), balance=0.0, amount=1.0):
    """Push shadows and highlights toward colours (offsets around 0, e.g. (0.05, 0, -0.04))."""
    l = luma(x)[..., None]
    sh = (1 - smooth(0.0, 0.55 + 0.2 * balance, l)) * np.asarray(shadows, np.float32)
    hi = smooth(0.35 + 0.2 * balance, 1.0, l) * np.asarray(highlights, np.float32)
    return x + (sh + hi) * amount


def hue_shift(x, hue_from=0.08, width=0.08, shift=0.0, sat=1.0, light=0.0):
    """Shift / saturate / lighten one hue range (hue 0-1: 0 red, .08 orange, .17 yellow, .33 green, .5 cyan,
    .66 blue, .83 magenta)."""
    mx, mn = x.max(-1), x.min(-1)
    d = mx - mn + 1e-6
    r, g, b = x[..., 0], x[..., 1], x[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) / 6.0
    dist = np.abs(((h - hue_from) + 0.5) % 1.0 - 0.5)
    wgt = (1 - smooth(width * 0.5, width, dist)) * smooth(0.02, 0.15, d)
    hs = (h + shift * wgt) % 1.0
    s = d / (mx + 1e-6)
    s2 = np.clip(s * (1 + (sat - 1) * wgt), 0, 1)
    v = np.clip(mx + light * wgt, 0, 1)
    # back to RGB (HSV)
    i = np.floor(hs * 6).astype(int) % 6
    f = hs * 6 - np.floor(hs * 6)
    p, q, t = v * (1 - s2), v * (1 - s2 * f), v * (1 - s2 * (1 - f))
    out = np.stack([np.choose(i, [v, q, p, p, t, v]), np.choose(i, [t, v, v, q, p, p]), np.choose(i, [p, p, t, v, v, q])], -1)
    return out


def mono(x, mix=(0.3, 0.59, 0.11), tone=(0, 0, 0)):
    """Black and white from a channel mix (a coloured filter), optionally toned."""
    v = np.clip(x @ np.asarray(mix, np.float32), 0, 1)[..., None]
    return v + np.asarray(tone, np.float32) * (1 - np.abs(2 * v - 1))


def channel_mix(x, matrix):
    return x @ np.asarray(matrix, np.float32).T


def curve(x, points, channel=None):
    """A smooth tone curve through (in, out) points; channel 0/1/2 or None for all."""
    pts = np.asarray(points, np.float32)
    xs, ys = pts[:, 0], pts[:, 1]
    fine = np.linspace(0, 1, 1024)
    ycurve = np.interp(fine, xs, ys)
    # light smoothing so the segments do not show as kinks
    k = np.ones(31) / 31
    ycurve = np.convolve(np.pad(ycurve, 15, mode="edge"), k, mode="valid")
    if channel is None:
        return np.interp(x, fine, ycurve)
    y = x.copy()
    y[..., channel] = np.interp(x[..., channel], fine, ycurve)
    return y


def highlight_roll(x, start=0.8):
    """Soft shoulder: highlights roll off instead of clipping."""
    over = np.clip(x - start, 0, None)
    return np.where(x > start, start + (1 - start) * (1 - np.exp(-over / (1 - start) * 1.4)) / (1 - np.exp(-1.4)), x)


OPS = dict(exposure=exposure, contrast=contrast, lgg=lift_gamma_gain, wb=white_balance, sat=saturation, vib=vibrance,
           fade=fade, split=split_tone, hue=hue_shift, mono=mono, mix=channel_mix, curve=curve, roll=highlight_roll)


def apply_look(x, steps, strength=1.0):
    y = x.astype(np.float32)
    for op, params in steps:
        y = OPS[op](y, **params)
    y = clip(y)
    return clip(x + (y - x) * strength) if strength != 1.0 else y


def cube(steps, size=33):
    g = np.linspace(0, 1, size, dtype=np.float32)
    b, gg, r = np.meshgrid(g, g, g, indexing="ij")   # .cube order: red changes fastest
    rgb = np.stack([r, gg, b], -1).reshape(-1, 3)
    return apply_look(rgb, steps)


def write_cube(path, title, steps, size=33):
    data = cube(steps, size)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f'TITLE "{title}"\n# Flip Studio Stock look (tools/luts_stock)\n')
        f.write(f"LUT_3D_SIZE {size}\nDOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n")
        np.savetxt(f, data, fmt="%.5f")
