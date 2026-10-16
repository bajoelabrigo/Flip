"""Sound kit for the Stock sound effects: oscillators, noise, filters, envelopes, reverb and stereo.

Everything is synthesized here (numpy + scipy), so every sound is ours. Signals are float64 mono
arrays at SR; `stereo()` widens a mono sound into (n, 2) and `finish()` normalises it.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import signal

SR = 48000
TAU = 2 * math.pi


def rng_for(name: str) -> np.random.Generator:
    return np.random.default_rng(sum(map(ord, name)) * 104729)


RNG = np.random.default_rng(1)


def seconds(n: int) -> float:
    return n / SR


def t_axis(sec: float) -> np.ndarray:
    return np.arange(int(SR * sec)) / SR


def samples(sec: float) -> int:
    return int(SR * sec)


# ---------------------------------------------------------------- sources

def noise(sec: float, color: str = "white", rng=None) -> np.ndarray:
    r = rng or RNG
    n = samples(sec)
    x = r.standard_normal(n)
    if color == "pink":
        b, a = [0.049922035, -0.095993537, 0.050612699, -0.004408786], [1, -2.494956002, 2.017265875, -0.522189400]
        x = signal.lfilter(b, a, x) * 3
    elif color == "brown":
        x = np.cumsum(x)
        x = signal.lfilter([1, -1], [1, -0.995], x) * 0.05
    return x / (np.max(np.abs(x)) + 1e-9)


def osc(freq, sec: float, shape: str = "sine", phase: float = 0.0) -> np.ndarray:
    """freq may be a number or a per-sample array (glides)."""
    n = samples(sec)
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,))
    ph = np.cumsum(f) / SR * TAU + phase
    if shape == "sine":
        return np.sin(ph)
    if shape == "tri":
        return 2 / math.pi * np.arcsin(np.sin(ph))
    if shape == "square":
        return np.tanh(np.sin(ph) * 8)
    if shape == "pulse25":
        return np.where((ph / TAU) % 1.0 < 0.25, 1.0, -1.0)
    if shape == "saw":
        # band-limited-ish saw: sum of harmonics under Nyquist
        out = np.zeros(n)
        fmax = float(np.max(f)) or 1
        for k in range(1, int(SR / 2 / fmax)):
            if k > 40:
                break
            out += np.sin(ph * k) / k
        return out * 0.6
    raise ValueError(shape)


def glide(f0: float, f1: float, sec: float, curve: str = "exp") -> np.ndarray:
    u = np.linspace(0, 1, samples(sec))
    if curve == "exp":
        return f0 * (f1 / f0) ** u
    if curve == "ease":
        return f0 + (f1 - f0) * (1 - (1 - u) ** 3)
    return f0 + (f1 - f0) * u


def fm(carrier, mod_ratio: float, index, sec: float) -> np.ndarray:
    """Two-operator FM: bells, metal, electric tones. index may be an envelope array."""
    n = samples(sec)
    fc = np.broadcast_to(np.asarray(carrier, dtype=float), (n,))
    ix = np.broadcast_to(np.asarray(index, dtype=float), (n,))
    mod = np.sin(np.cumsum(fc * mod_ratio) / SR * TAU)
    return np.sin(np.cumsum(fc) / SR * TAU + ix * mod)


def additive(freq: float, sec: float, partials, decays) -> np.ndarray:
    """Inharmonic partials (ratio, amp) each with its own decay rate: bells, chimes, glass."""
    t = t_axis(sec)
    out = np.zeros_like(t)
    for (ratio, amp), d in zip(partials, decays):
        out += amp * np.sin(TAU * freq * ratio * t) * np.exp(-t * d)
    return out


# ---------------------------------------------------------------- envelopes

def adsr(n: int, a: float, d: float, s: float, r: float, hold: float | None = None) -> np.ndarray:
    a_n, d_n, r_n = samples(a), samples(d), samples(r)
    h_n = max(n - a_n - d_n - r_n, 0) if hold is None else samples(hold)
    e = np.concatenate([np.linspace(0, 1, max(a_n, 1)), np.linspace(1, s, max(d_n, 1)), np.full(h_n, s),
                        np.linspace(s, 0, max(r_n, 1))])
    return np.pad(e, (0, max(n - len(e), 0)))[:n]


def perc(n: int, attack: float = 0.002, decay: float = 0.3, curve: float = 1.0) -> np.ndarray:
    """Fast attack, exponential decay (decay = time to about -60 dB)."""
    t = np.arange(n) / SR
    a = samples(attack)
    e = np.exp(-t / max(decay / 6.9, 1e-4)) ** curve
    if a > 0:
        e[:a] *= np.linspace(0, 1, a)
    return e


def swell(n: int, peak: float = 0.75, power: float = 2.0) -> np.ndarray:
    """Rises to its peak at `peak` (fraction) and falls away: whooshes."""
    u = np.linspace(0, 1, n)
    up = (u / peak) ** power
    down = np.clip((1 - u) / (1 - peak), 0, 1) ** 1.5
    return np.where(u < peak, up, down)


# ---------------------------------------------------------------- filters

def _sos(kind: str, f, q: float = 0.707, order: int = 2):
    nyq = SR / 2
    if kind in ("low", "high"):
        return signal.butter(order, min(f / nyq, 0.999), btype=kind, output="sos")
    lo, hi = f
    return signal.butter(order, [max(lo / nyq, 1e-4), min(hi / nyq, 0.999)], btype="band", output="sos")


def lowpass(x, f, order=2):
    return signal.sosfilt(_sos("low", f, order=order), x)


def highpass(x, f, order=2):
    return signal.sosfilt(_sos("high", f, order=order), x)


def bandpass(x, lo, hi, order=2):
    return signal.sosfilt(_sos("band", (lo, hi), order=order), x)


def sweep_filter(x: np.ndarray, f_curve: np.ndarray, q: float = 1.2, kind: str = "band") -> np.ndarray:
    """A resonant state-variable filter whose cutoff follows f_curve (per sample): whooshes, wah, risers."""
    n = len(x)
    f_curve = np.broadcast_to(np.asarray(f_curve, dtype=float), (n,))
    out = np.empty(n)
    low = band = 0.0
    damp = 1 / q
    for i in range(n):
        f = 2 * math.sin(math.pi * min(f_curve[i], SR / 6) / SR)
        high = x[i] - low - damp * band
        band += f * high
        low += f * band
        out[i] = band if kind == "band" else low if kind == "low" else high
    return out


def peak_eq(x, f, gain_db, q=1.0):
    a = 10 ** (gain_db / 40)
    w = TAU * f / SR
    al = math.sin(w) / (2 * q)
    b = [1 + al * a, -2 * math.cos(w), 1 - al * a]
    aa = [1 + al / a, -2 * math.cos(w), 1 - al / a]
    return signal.lfilter(b, aa, x)


# ---------------------------------------------------------------- dynamics and colour

def drive(x, amount: float = 2.0):
    return np.tanh(x * amount) / math.tanh(amount)


def bitcrush(x, bits: int = 6, hold: int = 4):
    y = np.repeat(x[::hold], hold)[:len(x)]
    q = 2 ** (bits - 1)
    return np.round(y * q) / q


def compress(x, threshold: float = 0.5, ratio: float = 4.0, release: float = 0.08):
    env = np.abs(x)
    coef = math.exp(-1 / (SR * release))
    sm = signal.lfilter([1 - coef], [1, -coef], env)
    gain = np.where(sm > threshold, (threshold + (sm - threshold) / ratio) / np.maximum(sm, 1e-9), 1.0)
    return x * gain


# ---------------------------------------------------------------- space

def reverb_ir(decay: float = 1.2, predelay: float = 0.01, bright: float = 6000, stereo: bool = True, seed: int = 7):
    r = np.random.default_rng(seed)
    n = samples(decay * 1.2 + predelay)
    t = np.arange(n) / SR
    chans = []
    for c in range(2 if stereo else 1):
        x = r.standard_normal(n) * np.exp(-t / (decay / 6.9))
        x[:samples(predelay)] = 0
        x = lowpass(x, bright)
        chans.append(x / np.sqrt(np.sum(x ** 2)))
    return np.stack(chans, axis=1)


def reverb(x: np.ndarray, mix: float = 0.25, decay: float = 1.2, bright: float = 6000, predelay: float = 0.012):
    """Convolution reverb with a synthetic tail. x mono or stereo; returns stereo, longer by the tail."""
    ir = reverb_ir(decay, predelay, bright)
    st = to_stereo(x)
    tail = samples(decay * 1.2 + predelay)
    out = np.zeros((len(st) + tail, 2))
    out[:len(st)] += st * (1 - mix * 0.5)
    for c in range(2):
        wet = signal.fftconvolve(st[:, c], ir[:, c])[:len(out)]
        out[:len(wet), c] += wet * mix
    return out


def delay(x: np.ndarray, time: float = 0.18, feedback: float = 0.35, mix: float = 0.3, repeats: int = 5, pingpong=True):
    st = to_stereo(x)
    d = samples(time)
    out = np.zeros((len(st) + d * repeats, 2))
    out[:len(st)] += st
    g = mix
    for k in range(1, repeats + 1):
        seg = st * g
        if pingpong:
            seg = seg[:, ::-1] if k % 2 else seg
        out[d * k:d * k + len(st)] += seg
        g *= feedback
    return out


def to_stereo(x: np.ndarray) -> np.ndarray:
    return np.stack([x, x], axis=1) if x.ndim == 1 else x


def stereo(x: np.ndarray, width: float = 0.3, seed: int = 3) -> np.ndarray:
    """Widen a mono sound: a few short decorrelating all-pass delays per side."""
    if x.ndim == 2:
        return x
    r = np.random.default_rng(seed)
    side = np.zeros_like(x)
    for _ in range(4):
        d = int(r.uniform(0.0004, 0.004) * SR)
        g = r.uniform(-0.5, 0.5)
        side[d:] += x[:-d] * g
    return np.stack([x + side * width, x - side * width], axis=1)


def pan(x: np.ndarray, p) -> np.ndarray:
    """p in [-1, 1] (number or per-sample array), equal power."""
    st = to_stereo(x)
    p = np.broadcast_to(np.asarray(p, dtype=float), (len(st),))
    a = (p + 1) * math.pi / 4
    return np.stack([st[:, 0] * np.cos(a), st[:, 1] * np.sin(a)], axis=1) * math.sqrt(2)


# ---------------------------------------------------------------- assembly

def place(parts, total: float | None = None) -> np.ndarray:
    """Mix (signal, start_seconds, gain) into one stereo buffer."""
    end = max(samples(s) + len(x) for x, s, _ in parts)
    n = max(end, samples(total) if total else 0)
    out = np.zeros((n, 2))
    for x, s, g in parts:
        st = to_stereo(x)
        i = samples(s)
        out[i:i + len(st)] += st * g
    return out


def fade(x: np.ndarray, fin: float = 0.002, fout: float = 0.02) -> np.ndarray:
    x = x.copy()
    a, b = samples(fin), samples(fout)
    if a:
        x[:a] *= np.linspace(0, 1, a)[:, None] if x.ndim == 2 else np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)[:, None] if x.ndim == 2 else np.linspace(1, 0, b)
    return x


def trim_silence(x: np.ndarray, floor_db: float = -60) -> np.ndarray:
    st = to_stereo(x)
    level = np.max(np.abs(st), axis=1)
    thr = 10 ** (floor_db / 20) * max(level.max(), 1e-9)
    idx = np.nonzero(level > thr)[0]
    if not len(idx):
        return st
    return st[:min(idx[-1] + samples(0.02), len(st))]


def finish(x: np.ndarray, peak_db: float = -1.0, lufs_like: float | None = None) -> np.ndarray:
    """Stereo, DC removed, trailing silence trimmed, faded, normalised to a peak."""
    st = to_stereo(np.asarray(x, dtype=float))
    st = st - st.mean(axis=0)
    st = highpass(st.T, 25).T if len(st) > 64 else st
    st = trim_silence(st)
    st = fade(st, 0.001, min(0.03, len(st) / SR / 4))
    peak = np.max(np.abs(st)) + 1e-9
    return st / peak * 10 ** (peak_db / 20)


def sequence(notes, wave_fn, gap: float = 0.0):
    """notes: (freq, dur) list -> concatenated mono signal, each note from wave_fn(freq, dur)."""
    return np.concatenate([np.concatenate([wave_fn(f, d), np.zeros(samples(gap))]) for f, d in notes])


def midi(n: float) -> float:
    return 440.0 * 2 ** ((n - 69) / 12)
