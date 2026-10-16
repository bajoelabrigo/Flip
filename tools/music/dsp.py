"""Audio analysis for the music cuts: decoding, beats and bars, sections, loudness (BS.1770) and a peak limiter.

Only numpy/scipy: onset strength from a log-band spectral flux, tempo from its autocorrelation, beats by
dynamic programming (Ellis 2007), downbeats by the phase of the bar that carries the most bass/novelty.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d

SR = 44100          # output and analysis rate
HOP = 512           # analysis hop (11.6 ms)
NFFT = 2048
FPS = SR / HOP


def decode(path: Path, sr: int = SR) -> np.ndarray:
    """Any file ffmpeg reads -> float32 stereo (n, 2) at `sr`."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


# ---------------------------------------------------------------- spectrum and onsets

def _bands(n_bands: int = 48, fmin: float = 30, fmax: float = 16000) -> np.ndarray:
    freqs = np.fft.rfftfreq(NFFT, 1 / SR)
    edges = np.geomspace(fmin, fmax, n_bands + 2)
    fb = np.zeros((n_bands, len(freqs)), np.float32)
    for i in range(n_bands):
        lo, c, hi = edges[i], edges[i + 1], edges[i + 2]
        up = (freqs - lo) / (c - lo)
        down = (hi - freqs) / (hi - c)
        fb[i] = np.clip(np.minimum(up, down), 0, None)
    fb /= fb.sum(axis=1, keepdims=True) + 1e-9
    return fb


FB = _bands()
BAND_HZ = np.geomspace(30, 16000, 50)[1:-1]


def spectrogram(mono: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(log band energies (frames, bands), RMS per frame in dBFS)."""
    pad = np.pad(mono.astype(np.float32), (NFFT // 2, NFFT // 2))
    view = np.lib.stride_tricks.sliding_window_view(pad, NFFT)[::HOP]
    n = len(view)
    win = np.hanning(NFFT).astype(np.float32)
    out = np.empty((n, FB.shape[0]), np.float32)
    db = np.empty(n, np.float64)
    for a in range(0, n, 1024):
        frames = np.asarray(view[a:a + 1024])
        db[a:a + 1024] = 10 * np.log10((frames.astype(np.float64) ** 2).mean(axis=1) + 1e-12)
        mag = np.abs(np.fft.rfft(frames * win, axis=1)).astype(np.float32)
        out[a:a + 1024] = (mag ** 2) @ FB.T
    return np.log10(out + 1e-10), db


def onset_strength(logspec: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(all-band flux, bass flux) normalised to unit std, one value per frame."""
    d = np.diff(logspec, axis=0, prepend=logspec[:1])
    d = np.maximum(d, 0)
    full = d.mean(axis=1)
    bass = d[:, BAND_HZ < 160].mean(axis=1)
    out = []
    for o in (full, bass):
        o = o - uniform_filter1d(o, int(FPS * 0.5))
        o = np.maximum(o, 0)
        out.append(o / (o.std() + 1e-9))
    return out[0], out[1]


# ---------------------------------------------------------------- tempo and beats

def pulse_clarity(onset: np.ndarray, bpm: float) -> float:
    """Autocorrelation of the onset curve at the beat period (0 = no pulse, ~0.3+ = clear beat)."""
    o = onset - onset.mean()
    n = len(o)
    ac = signal.fftconvolve(o, o[::-1], mode="full")[n - 1:]
    ac /= ac[0] + 1e-9
    lag = FPS * 60 / bpm
    w = np.arange(int(lag * 0.95), int(lag * 1.05) + 2)
    return float(ac[w[w < len(ac)]].max())


def tempo(onset: np.ndarray, hint: float | None = None) -> float:
    o = onset - onset.mean()
    n = len(o)
    ac = signal.fftconvolve(o, o[::-1], mode="full")[n - 1:]
    ac /= ac[0] + 1e-9
    bpms = np.linspace(55, 210, 1600)
    lags = FPS * 60 / bpms
    val = np.interp(lags, np.arange(len(ac)), ac)
    # harmonics reinforce the true period
    val = val + 0.5 * np.interp(lags * 2, np.arange(len(ac)), ac) + 0.25 * np.interp(lags / 2, np.arange(len(ac)), ac)
    prior = np.exp(-0.5 * (np.log2(bpms / 115) / 0.9) ** 2)
    est = float(bpms[np.argmax(val * prior)])
    if hint and hint > 0:
        for k in (1, 2, 0.5, 1.5, 2 / 3):
            h = hint * k
            if abs(h / est - 1) < 0.04:
                return h
    return est


def beat_track(onset: np.ndarray, bpm: float, tightness: float = 100) -> np.ndarray:
    """Beat frames by dynamic programming."""
    period = FPS * 60 / bpm
    loc = np.convolve(onset, np.exp(-0.5 * (np.arange(-period, period + 1) * 32 / period) ** 2), "same")
    loc = loc / (loc.std() + 1e-9)
    n = len(loc)
    score = np.zeros(n)
    back = np.full(n, -1)
    lo, hi = int(round(period / 2)), int(round(2 * period))
    offs = np.arange(lo, hi + 1)
    pen = -tightness * np.log(offs / period) ** 2
    for t in range(n):
        cand = t - offs
        ok = cand >= 0
        if not ok.any():
            score[t] = loc[t]
            continue
        s = score[cand[ok]] + pen[ok]
        j = int(np.argmax(s))
        if s[j] > 0:
            score[t] = loc[t] + s[j]
            back[t] = cand[ok][j]
        else:
            score[t] = loc[t]
    # end: best score among the last period, among local maxima
    tail = np.arange(max(0, n - int(period * 2)), n)
    t = int(tail[np.argmax(score[tail])])
    beats = []
    while t >= 0:
        beats.append(t)
        t = back[t]
    return np.array(beats[::-1])


@dataclass
class Analysis:
    dur: float
    bpm: float
    beats: np.ndarray        # seconds
    downbeats: np.ndarray    # seconds (bar starts)
    meter: int
    pulse: float             # pulse clarity
    accent: np.ndarray       # per downbeat: onset strength at it
    bar_rms_db: np.ndarray   # per bar (between downbeats)
    novelty: np.ndarray      # per downbeat: how different the music is after it than before it
    start: float             # first audible sample
    end: float               # last audible sample
    frame_db: np.ndarray     # RMS per analysis frame, dBFS
    logspec: np.ndarray


def analyse(x: np.ndarray, hint_bpm: float | None = None, meter: int | None = None) -> Analysis:
    mono = x.mean(axis=1)
    logspec, frame_db = spectrogram(mono)
    full, bass = onset_strength(logspec)
    nfr = len(full)
    loud = frame_db > frame_db.max() - 45
    start = float(np.argmax(loud) * HOP / SR)
    end = float((nfr - np.argmax(loud[::-1])) * HOP / SR)
    bpm = tempo(full, hint_bpm)
    while bpm > 185:
        bpm /= 2
    while bpm < 60:
        bpm *= 2
    bfr = beat_track(full, bpm)
    bfr = bfr[(bfr * HOP / SR >= start - 0.05) & (bfr * HOP / SR <= end)]
    beats = bfr * HOP / SR
    # beat-synchronous features for meter and downbeat phase
    def at(v, frames, w=2):
        return np.array([v[max(0, f - w):f + w + 1].max() for f in frames])
    accent = at(bass, bfr) + 0.5 * at(full, bfr)
    chroma = np.array([logspec[a:b].mean(axis=0) if b > a else logspec[a] for a, b in zip(bfr[:-1], bfr[1:])])
    change = np.r_[0, np.linalg.norm(np.diff(chroma, axis=0), axis=1), 0][:len(bfr)]
    change = (change - change.mean()) / (change.std() + 1e-9)
    if meter is None:
        meter = 4
    best, phase = -1e9, 0
    for p in range(meter):
        sel = np.arange(p, len(bfr), meter)
        s = accent[sel].mean() + 0.6 * change[sel].mean() if len(sel) else -1e9
        if s > best:
            best, phase = s, p
    down = beats[phase::meter]
    down_acc = accent[phase::meter]
    # per bar loudness and novelty between the 4 bars before and after each downbeat
    dfr = (down * FPS).astype(int)
    bars = [(a, b) for a, b in zip(dfr[:-1], dfr[1:])]
    bar_rms = np.array([10 * np.log10(np.mean(10 ** (frame_db[a:b] / 10)) + 1e-12) for a, b in bars]) if bars else np.zeros(0)
    feats = np.array([np.r_[logspec[a:b].mean(axis=0), bar_rms[i] / 10] for i, (a, b) in enumerate(bars)]) if bars else np.zeros((0, 1))
    nov = np.zeros(len(down))
    for k in range(len(down)):
        a, b = feats[max(0, k - 4):k], feats[k:k + 4]
        if len(a) and len(b):
            nov[k] = np.linalg.norm(a.mean(axis=0) - b.mean(axis=0))
    if nov.std() > 0:
        nov = (nov - nov.mean()) / nov.std()
    return Analysis(dur=len(x) / SR, bpm=bpm, beats=beats, downbeats=down, meter=meter, pulse=pulse_clarity(full, bpm),
                    accent=down_acc, bar_rms_db=bar_rms,
                    novelty=nov, start=start, end=end, frame_db=frame_db, logspec=logspec)


# ---------------------------------------------------------------- loudness (ITU-R BS.1770-4)

def _kweight(sr: int):
    # high shelf (+4 dB above ~1.5 kHz) and RLB high pass, as in pyloudnorm
    G, Q, fc = 3.99984385397, 0.7071752369554193, 1681.9744509555319
    A = 10 ** (G / 40)
    w0 = 2 * np.pi * fc / sr
    alpha = np.sin(w0) / (2 * Q)
    b0 = A * ((A + 1) + (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha)
    b1 = -2 * A * ((A - 1) + (A + 1) * np.cos(w0))
    b2 = A * ((A + 1) + (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha)
    a0 = (A + 1) - (A - 1) * np.cos(w0) + 2 * np.sqrt(A) * alpha
    a1 = 2 * ((A - 1) - (A + 1) * np.cos(w0))
    a2 = (A + 1) - (A - 1) * np.cos(w0) - 2 * np.sqrt(A) * alpha
    shelf = (np.array([b0, b1, b2]) / a0, np.array([1, a1 / a0, a2 / a0]))
    Q, fc = 0.5003270373253953, 38.13547087613982
    w0 = 2 * np.pi * fc / sr
    alpha = np.sin(w0) / (2 * Q)
    b = np.array([(1 + np.cos(w0)) / 2, -(1 + np.cos(w0)), (1 + np.cos(w0)) / 2])
    a = np.array([1 + alpha, -2 * np.cos(w0), 1 - alpha])
    hp = (b / a[0], a / a[0])
    return shelf, hp


def lufs(x: np.ndarray, sr: int = SR) -> float:
    (b1, a1), (b2, a2) = _kweight(sr)
    y = signal.lfilter(b2, a2, signal.lfilter(b1, a1, x, axis=0), axis=0)
    blk, step = int(0.4 * sr), int(0.1 * sr)
    if len(y) < blk:
        return -70.0
    sq = np.cumsum(np.r_[np.zeros((1, y.shape[1])), y.astype(np.float64) ** 2], axis=0)
    starts = np.arange(0, len(y) - blk + 1, step)
    z = (sq[starts + blk] - sq[starts]) / blk
    lk = -0.691 + 10 * np.log10(z.sum(axis=1) + 1e-12)
    keep = lk > -70
    if not keep.any():
        return -70.0
    rel = -0.691 + 10 * np.log10(z[keep].sum(axis=1).mean() + 1e-12) - 10
    keep &= lk > rel
    return float(-0.691 + 10 * np.log10(z[keep].sum(axis=1).mean() + 1e-12))


def true_peak_db(x: np.ndarray) -> float:
    up = signal.resample_poly(x, 4, 1, axis=0)
    return float(20 * np.log10(np.abs(up).max() + 1e-12))


def limit(x: np.ndarray, ceiling_db: float = -1.5, sr: int = SR) -> tuple[np.ndarray, float]:
    """Look-ahead peak limiter (5 ms look-ahead, 120 ms release). Returns (y, max gain reduction dB)."""
    thr = 10 ** (ceiling_db / 20)
    peak = np.abs(signal.resample_poly(x, 2, 1, axis=0)).max(axis=1)[::2][:len(x)]
    g = np.minimum(1.0, thr / (peak + 1e-12))
    if g.min() >= 1.0:
        return x, 0.0
    la = int(0.005 * sr)
    g = minimum_filter1d(g, 2 * la + 1)
    # release at 1 ms resolution
    step = int(sr / 1000)
    gc = g[: len(g) // step * step].reshape(-1, step).min(axis=1)
    rel = np.exp(-1 / 120)
    out = np.empty_like(gc)
    cur = 1.0
    for i, v in enumerate(gc):
        cur = v if v < cur else v + (cur - v) * rel
        out[i] = cur
    gs = np.repeat(out, step)
    gs = np.r_[gs, np.full(len(g) - len(gs), gs[-1] if len(gs) else 1.0)]
    gs = np.minimum(gs, g)
    gs = uniform_filter1d(gs, la)  # smooth corners; look-ahead keeps it under the peaks
    gs = np.minimum(gs, minimum_filter1d(g, la))
    return (x * gs[:, None]).astype(np.float32), float(-20 * np.log10(gs.min()))
