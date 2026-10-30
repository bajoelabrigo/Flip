"""Animaciones Extremas, second try (0.26): the field engine.

The first set drew effects as many separate particles, each with its own outline, and Jorge turned
them down («no se ven como las de RTFX»). Studied frame by frame, a hand-drawn cartoon FX is one
mass: a field over the frame whose level sets are the tones (a red rim, a thin orange edge, the
yellow heart), with holes, and that tears into strands as it dies. So an element here is a function
that gives, at time t, two fields on a coarse grid: `d` (the mass; the red rim is d > RIM) and
`core` (the heart; orange core > EDGE, yellow core > HOT). Every second frame the fields are cut
into outlines (OpenCV contours, holes included, even-odd fill) and written as hold keys, one Lottie
layer per tone, with the rim again blurred behind as the glow.

`strip()` draws the same frames as an image, to set them side by side with a reference before any
render (see feedback: study before generating).
"""

from __future__ import annotations

import math

import cv2
import numpy as np

from lottie import Sticker, group, layer_transform, rgb, static, transform

STEP = 2
RIM, EDGE, HOT = 0.45, 0.55, 0.62


class Tex:
    """A wrapping value-noise texture, sampled anywhere (cubic)."""

    def __init__(self, seed, n=64):
        self.t = np.random.default_rng(seed).random((n, n)).astype(np.float32)
        self.n = n

    def __call__(self, u, v):
        return cv2.remap(self.t, (u % self.n).astype(np.float32), (v % self.n).astype(np.float32),
                         cv2.INTER_CUBIC, borderMode=cv2.BORDER_WRAP)

    def fbm(self, u, v, octaves=3):
        out = np.zeros_like(u, dtype=np.float32)
        a, f, tot = 1.0, 1.0, 0.0
        for o in range(octaves):
            out += a * self(u * f + o * 17.3, v * f + o * 9.1)
            tot += a
            a *= 0.5
            f *= 2.0
        return out / tot


def bump(X, Y, cx, cy, r, sx=1.0, sy=1.0, ang=0.0):
    """A puff: flat-topped with a steep edge, so puffs keep their round edges where they meet."""
    dx, dy = X - cx, Y - cy
    if ang:
        c, s = math.cos(ang), math.sin(ang)
        dx, dy = c * dx + s * dy, -s * dx + c * dy
    q = (dx / (r * sx)) ** 2 + (dy / (r * sy)) ** 2
    return np.exp(-q * q)


# ------------------------------------------------------------------ cutting into outlines
def levels(tones):
    """The heart level each tone after the rim starts at: a tone may give its own as a third item."""
    default = [EDGE, HOT] + [HOT + 0.08 * i for i in range(1, 8)]
    return [t[2] if len(t) > 2 else default[i] for i, t in enumerate(tones[1:])]


def masks(d, core, W, H, tones=None):
    up = cv2.resize(d, (W, H), interpolation=cv2.INTER_CUBIC)
    cu = cv2.resize(core, (W, H), interpolation=cv2.INTER_CUBIC)
    rim = up > RIM
    return [rim] + [rim & (cu > lv) for lv in levels(tones or TONES)]


def outlines(mask, min_area=12.0, eps=1.3):
    """The mask's outlines, holes included (even-odd fill draws them as holes), biggest first."""
    cs, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        a = abs(cv2.contourArea(c))
        if a < min_area:
            continue
        p = cv2.approxPolyDP(c, eps, True)[:, 0, :]
        if len(p) >= 3:
            out.append((a, p))
    out.sort(key=lambda x: -x[0])
    return [p for _, p in out]


def path_keys(frames, slots):
    """[(frame, [outline…])] → one animated path per slot, the same vertex count at every key."""
    paths = []
    for slot in range(slots):
        polys = [(f, outs[slot] if slot < len(outs) else None) for f, outs in frames]
        if not any(p is not None for _, p in polys):
            break
        n = max(len(p) for _, p in polys if p is not None)
        ks = []
        for f, p in polys:
            if p is None:
                v = [[-9999, -9999]] * n
            else:
                v = [[int(x), int(y)] for x, y in p]
                v += [v[-1]] * (n - len(v))
            ks.append({"t": f, "s": [{"c": True, "v": v, "i": [[0, 0]] * n, "o": [[0, 0]] * n}], "h": 1})
        paths.append({"ty": "sh", "ks": {"a": 1, "k": ks} if len(ks) > 1 else static(ks[0]["s"][0])})
    return paths


def even_odd_fill(colour, sid, o=100):
    c = static(rgb(colour))
    c["sid"] = sid
    return {"ty": "fl", "c": c, "o": static(o), "r": 2}


def gaussian_blur(amount):
    return {"ty": 29, "nm": "Gaussian Blur", "np": 5, "mn": "ADBE Gaussian Blur 2", "ix": 1, "en": 1,
            "ef": [{"ty": 0, "nm": "Blurriness", "mn": "ADBE Gaussian Blur 2-0001", "ix": 1, "v": static(amount)},
                   {"ty": 7, "nm": "Blur Dimensions", "mn": "ADBE Gaussian Blur 2-0002", "ix": 2, "v": static(1)},
                   {"ty": 7, "nm": "Repeat Edge Pixels", "mn": "ADBE Gaussian Blur 2-0003", "ix": 3, "v": static(0)}]}


TONES = [("rojo", "#ff1a08"), ("naranja", "#ff6a00"), ("amarillo", "#fff3a0")]


def render(sticker: Sticker, field, tones=TONES, glow=24, slots=(48, 40, 40), halo=None):
    """Writes `field(t) -> (d, core)` into the sticker: a glow, then one layer per tone. halo, when
    given, is a list of (colour, blur, opacity) glows drawn behind instead of the single one: a wide
    soft one and a near one read as the warm haze round RTFX's effects."""
    W, H = sticker.size, sticker.h
    per_tone = [[] for _ in tones]
    for f in range(0, sticker.frames, STEP):
        d, core = field(f / sticker.fps)
        for k, m in enumerate(masks(d, core, W, H, tones)):
            per_tone[k].append((f, outlines(m)))
    ids = [sticker.slot(t[0], t[1]) for t in tones]
    rim_paths = path_keys(per_tone[0], slots[0])
    glows = halo if halo is not None else ([(tones[0][1], glow, 85)] if glow else [])
    for i, (colour, blur, opacity) in enumerate(glows):
        if not rim_paths:
            break
        sid = sticker.slot(tones[0][0] + " resplandor" + ("" if i == 0 else f" {i + 1}"), colour)
        lay = sticker.layer(group(*rim_paths, even_odd_fill(colour, sid, opacity), tr=transform()),
                            ks=layer_transform((0, 0)), name="resplandor" + ("" if i == 0 else f" {i + 1}"))
        lay["ef"] = [gaussian_blur(blur)]
    for k, t in enumerate(tones):
        sid, colour = t[0], t[1]
        paths = rim_paths if k == 0 else path_keys(per_tone[k], slots[min(k, len(slots) - 1)])
        if paths:
            sticker.layer(group(*paths, even_odd_fill(colour, ids[k]), tr=transform()), ks=layer_transform((0, 0)),
                          name=sid)
    return sticker


# ------------------------------------------------------------------ previews without the app
def picture(d, core, W, H, tones=TONES, glow=16, halo=None):
    img = np.zeros((H, W, 3), np.float32)
    ms = masks(d, core, W, H, tones)
    glows = halo if halo is not None else [(tones[0][1], glow * 2, 100)]
    for colour, blur, opacity in glows:
        r, g, b = rgb(colour)[:3]
        # AE's Blurriness is about twice the Gaussian sigma.
        h = cv2.GaussianBlur(ms[0].astype(np.float32), (0, 0), max(1.0, blur / 2)) * opacity / 100
        img += h[..., None] * np.array((b, g, r), np.float32) * (1 - img.max(axis=2, keepdims=True).clip(0, 1))
    for m, t in zip(ms, tones):
        r, g, b = rgb(t[1])[:3]
        img[m] = (b, g, r)
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def strip(field, W, H, frames, every=4, cell=190, fps=24):
    tiles = []
    for f in range(0, frames, every):
        d, core = field(f / fps)
        tiles.append(cv2.resize(picture(d, core, W, H), (cell, int(cell * H / W))))
    return np.hstack(tiles)
