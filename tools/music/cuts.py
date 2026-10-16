"""Where to cut a song so a 15/30/60 s version sounds finished.

A cut starts on a downbeat (or at the very start of the song) and either
- ends with the song's own ending (when it fits the length), or
- plays a whole number of bars (even, ideally 4 or 8), lets the next downbeat hit and fades out over a tail.
Candidates are scored on how representative the window is (loudness against the song's loud parts), whether it
starts and ends on section changes, how clean the phrase is and how close it lands to the target length.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import dsp


@dataclass
class Cut:
    start: float        # seconds in the song
    end: float          # seconds in the song
    fade_in: float      # seconds
    fade_from: float    # seconds in the song where the fade-out starts (== end: no fade)
    kind: str           # "intro+fade", "fade", "ending", "intro+ending"
    bars: int
    score: float

    @property
    def length(self) -> float:
        return self.end - self.start


def _window_db(a: dsp.Analysis, t0: float, t1: float) -> tuple[float, float]:
    f0, f1 = int(t0 * dsp.FPS), max(int(t0 * dsp.FPS) + 1, int(t1 * dsp.FPS))
    seg = a.frame_db[f0:f1]
    p = 10 ** (seg / 10)
    mean = 10 * np.log10(p.mean() + 1e-12)
    # quietest second inside the window
    k = int(dsp.FPS)
    if len(p) > k:
        sm = np.convolve(p, np.ones(k) / k, "valid")
        low = 10 * np.log10(sm.min() + 1e-12)
    else:
        low = mean
    return float(mean), float(low)


def song_reference_db(a: dsp.Analysis) -> float:
    """Loudness of the song's loud parts (75th percentile of 1 s windows)."""
    p = 10 ** (a.frame_db / 10)
    k = int(dsp.FPS)
    sm = np.convolve(p, np.ones(k) / k, "valid") if len(p) > k else p
    sm = sm[sm > 1e-9]
    return float(10 * np.log10(np.percentile(sm, 75) + 1e-12))


def ending_decays(a: dsp.Analysis) -> bool:
    """True when the song ends by itself (it rings out or fades) instead of stopping dead in a loop."""
    f1 = int(a.end * dsp.FPS)
    last = a.frame_db[max(0, f1 - int(0.6 * dsp.FPS)):f1]
    before = a.frame_db[max(0, f1 - int(6 * dsp.FPS)):max(1, f1 - int(3 * dsp.FPS))]
    if len(last) == 0 or len(before) == 0:
        return False
    drop = 10 * np.log10((10 ** (before / 10)).mean()) - 10 * np.log10((10 ** (last / 10)).mean())
    return drop > 9


def choose(a: dsp.Analysis, L: float, *, avoid: list[tuple[float, float]] = (), prefer_intro: float | None = None,
           tail_range=(1.6, 4.2), min_start: float | None = None) -> Cut:
    D = a.downbeats
    if len(D) < 4:
        raise ValueError("no bars found")
    ref = song_reference_db(a)
    bar = float(np.median(np.diff(D)))
    nov = a.novelty
    acc = (a.accent - a.accent.mean()) / (a.accent.std() + 1e-9)
    intro_bonus = {15: 0.0, 30: 0.5, 60: 1.0}.get(int(L), 0.5) if prefer_intro is None else prefer_intro
    rhythmic = a.pulse > 0.12
    natural = ending_decays(a)
    cands: list[Cut] = []

    def score_window(t0, t1, s_idx, e_idx, kind, bars, total):
        mean, low = _window_db(a, t0, t1)
        rel = mean - ref
        sc = 1.2 * min(rel + 2.5, 0)            # quieter than the song's loud parts
        if L <= 30:
            sc += 0.5 * min(low - (ref - 14), 0) / 4   # deep breakdowns inside a short cut
        sc += 0.45 * (nov[s_idx] if s_idx is not None and s_idx < len(nov) else 0)
        sc += 0.45 * (nov[e_idx] if e_idx is not None and e_idx < len(nov) else 0)
        if s_idx is not None and s_idx < len(acc):
            sc += 0.25 * acc[s_idx]
        if bars:
            sc += 0.6 * (bars % 4 == 0) + 0.3 * (bars % 8 == 0) - 0.6 * (bars % 2 == 1)
        sc -= 0.9 * abs(total - L)
        for o0, o1 in avoid:                  # another cut of the same song already uses this part
            ov = max(0.0, min(t1, o1) - max(t0, o0))
            sc -= 0.6 * ov / L
        return sc

    for s in range(len(D)):
        if min_start is not None and D[s] < min_start - 0.05:
            continue
        is_intro = s == 0 or D[s] - a.start < bar * 0.75
        t0 = max(0.0, a.start - 0.04) if is_intro else max(0.0, D[s] - 0.03)
        # 1) whole bars + the next downbeat + a fade
        for B in range(2, len(D) - s):
            t_hit = D[s + B]
            content = t_hit - t0
            if content > L - tail_range[0] + 0.01:
                break
            tail = float(np.clip(L - content, *tail_range))
            total = content + tail
            if total > L + 0.05 or total < L - 2.5 or t_hit + tail > a.end + 0.5:
                continue
            sc = score_window(t0, t_hit + tail, s, s + B, "fade", B, total)
            if is_intro:
                sc += intro_bonus
            cands.append(Cut(t0, t_hit + tail, 0.0 if is_intro else 0.012, t_hit + (0.18 if rhythmic else 0.0),
                             "intro+fade" if is_intro else "fade", B, sc))
        # 2) the song's own ending
        if natural:
            total = a.end + 0.25 - t0
            if L - 2.5 <= total <= L + 0.05:
                sc = score_window(t0, a.end, s, None, "ending", 0, total) + 1.1 + (intro_bonus if is_intro else 0)
                cands.append(Cut(t0, min(a.dur, a.end + 0.25), 0.0 if is_intro else 0.012, min(a.dur, a.end + 0.25),
                                 "intro+ending" if is_intro else "ending", 0, sc))
    if not cands:
        # very short or beatless song: from the start with a fade
        t0 = max(0.0, a.start - 0.04)
        t1 = min(a.end, t0 + L)
        return Cut(t0, t1, 0.0, max(t0, t1 - 3.0), "intro+fade", 0, -99)
    if not rhythmic:
        # no clear beat: give the fades more room
        for c in cands:
            if c.kind.endswith("fade"):
                c.fade_from = max(c.start, c.end - max(3.0, c.end - c.fade_from))
                if c.fade_in:
                    c.fade_in = 0.35
    return max(cands, key=lambda c: c.score)


def render(x: np.ndarray, c: Cut) -> np.ndarray:
    sr = dsp.SR
    i0, i1 = int(round(c.start * sr)), int(round(c.end * sr))
    y = x[i0:i1].astype(np.float32).copy()
    n = len(y)
    if c.fade_in > 0:
        k = min(n, int(c.fade_in * sr))
        y[:k] *= (np.sin(np.linspace(0, np.pi / 2, k)) ** 2)[:, None].astype(np.float32)
    f0 = int(round((c.fade_from - c.start) * sr))
    if 0 <= f0 < n - 1:
        k = n - f0
        u = np.linspace(0, 1, k)
        # smooth start, then close to an exponential decay that reaches about -60 dB at the end
        g = (0.5 * (1 + np.cos(np.pi * u))) ** 1.6
        y[f0:] *= g[:, None].astype(np.float32)
    else:
        k = min(n, int(0.05 * sr))  # natural ending: just make sure the last samples land on zero
        y[n - k:] *= np.linspace(1, 0, k)[:, None]
    return y
