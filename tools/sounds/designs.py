"""The 200 sound effects of Stock › Sonidos. Each is a function () -> signal; build.py finishes and encodes it."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

import dsp as d
from dsp import SR, TAU


@dataclass
class Sound:
    id: str
    names: dict
    category: str
    make: object
    tags: list = field(default_factory=list)


SOUNDS: dict[str, Sound] = {}

CATEGORIES = {
    "transiciones": {"es": "Transiciones", "en": "Transitions"},
    "impactos": {"es": "Impactos", "en": "Impacts"},
    "interfaz": {"es": "Botones y avisos", "en": "UI and alerts"},
    "juegos": {"es": "Monedas y juegos", "en": "Coins and games"},
    "magia": {"es": "Magia y brillos", "en": "Magic and sparkle"},
    "comedia": {"es": "Comedia", "en": "Comedy"},
    "suspenso": {"es": "Suspenso y drama", "en": "Suspense and drama"},
    "ritmo": {"es": "Ritmo y música", "en": "Beats and music"},
}


def sound(id, es, en, category, fn, tags=()):
    SOUNDS[id] = Sound(id, {"es": es, "en": en}, category, fn, list(tags))


def R(name):
    return d.rng_for(name)


# ================================================================ building blocks

def whoosh(sec=0.7, lo=300, hi=3000, q=1.4, color="pink", peak=0.6, pan_from=0.0, pan_to=0.0, seed="w",
           metal=0.0, verb=0.15):
    n = d.samples(sec)
    x = d.noise(sec, color, R(seed))
    u = np.linspace(0, 1, n)
    f = lo * (hi / lo) ** np.where(u < peak, u / peak, 1 - (u - peak) / (1 - peak) * 0.6)
    y = d.sweep_filter(x, f, q) * d.swell(n, peak, 2.2)
    y = d.lowpass(y, min(max(lo, hi) * 1.8, 16000), order=4)   # the band's skirts let hiss through
    if metal:
        comb = np.zeros_like(y)
        for k, g in ((int(SR / 900), 0.6), (int(SR / 1370), 0.45)):
            comb[k:] += y[:-k] * g
        y = y + comb * metal
    st = d.pan(d.stereo(y, 0.25), np.linspace(pan_from, pan_to, n))
    return d.reverb(st, verb, 0.8) if verb else st


def riser_noise(sec=2.0, lo=200, hi=9000, seed="r"):
    n = d.samples(sec)
    u = np.linspace(0, 1, n)
    x = d.noise(sec, "pink", R(seed))
    f = lo * (hi / lo) ** (u ** 1.4)
    y = d.sweep_filter(x, f, 2.5) * u ** 2.2
    y = d.sweep_filter(y, f * 2.2, 0.8, kind="low")
    return d.reverb(d.stereo(y, 0.4), 0.3, 1.5)


def riser_synth(sec=2.0, f0=110, f1=880, wobble=0.0, seed="rs"):
    n = d.samples(sec)
    u = np.linspace(0, 1, n)
    f = d.glide(f0, f1, sec)
    if wobble:
        f = f * (1 + wobble * np.sin(TAU * (2 + 10 * u) * u * sec))
    saw = d.osc(f, sec, "saw") + 0.5 * d.osc(f * 1.007, sec, "saw") + 0.5 * d.osc(f * 0.993, sec, "saw")
    y = d.sweep_filter(saw, 300 + 7000 * u ** 2, 1.5, kind="low") * u ** 1.8
    return d.reverb(d.stereo(y * 0.5, 0.5), 0.25, 1.4)


def downlifter(sec=2.0, seed="dl", synth=False):
    n = d.samples(sec)
    u = np.linspace(0, 1, n)
    if synth:
        x = d.osc(d.glide(660, 50, sec), sec, "saw")
        y = d.lowpass(x, 3000) * (1 - u) ** 1.5
    else:
        x = d.noise(sec, "pink", R(seed))
        f = 6000 * (60 / 6000) ** u
        y = d.sweep_filter(x, f, 2.0) * (1 - u) ** 1.2 * np.minimum(u * 20, 1)
        y = d.sweep_filter(y, f * 2.2, 0.8, kind="low")
    return d.reverb(d.stereo(y, 0.4), 0.3, 1.6)


def reverse_cymbal(sec=1.5, seed="rc"):
    c = cymbal(sec, seed)
    return c[::-1] * np.linspace(0.2, 1, len(c))[:, None]


def cymbal(sec=1.8, seed="cy"):
    n = d.samples(sec)
    x = d.noise(sec, "white", R(seed))
    metal = d.fm(np.full(n, 431.0), 1.48, 6 * d.perc(n, 0.001, sec), sec)
    y = d.highpass(x * 0.8 + metal * 0.3, 3500) * d.perc(n, 0.001, sec, 0.9)
    return d.reverb(d.stereo(y, 0.6), 0.25, 1.4, bright=9000)


def tape_stop(sec=0.8, base=220):
    n = d.samples(sec)
    u = np.linspace(0, 1, n)
    f = base * (1 - u) ** 1.6 + 8
    tone = d.osc(f, sec, "saw") * 0.6 + d.osc(f * 2.01, sec, "tri") * 0.4
    y = d.lowpass(tone, 2500) * (1 - u ** 3)
    return d.stereo(y, 0.2)


def glitch(sec=0.5, seed="g", stutter=False, crush=True):
    r = R(seed)
    n = d.samples(sec)
    out = np.zeros(n)
    i = 0
    while i < n:
        L = int(r.uniform(0.012, 0.06) * SR)
        kind = r.integers(0, 4)
        t = np.arange(L) / SR
        if kind == 0:
            seg = np.sin(TAU * r.uniform(200, 3000) * t)
        elif kind == 1:
            seg = r.standard_normal(L) * 0.7
        elif kind == 2:
            seg = d.bitcrush(np.sin(TAU * r.uniform(60, 400) * t), 3, 8) if L > 16 else np.zeros(L)
        else:
            seg = np.zeros(L)
        if stutter and i > 0 and r.random() < 0.5:
            seg = out[max(i - L, 0):i][:L]
            seg = np.pad(seg, (0, L - len(seg)))
        out[i:i + L] = seg[:max(min(L, n - i), 0)]
        i += L
    if crush:
        out = d.bitcrush(out, 5, 3)
    return d.pan(out * 0.8, np.sin(np.linspace(0, 9, n)) * 0.6)


def shutter(seed="sh"):
    r = R(seed)
    def click(f, dur):
        n = d.samples(dur)
        return d.bandpass(r.standard_normal(n), f * 0.6, f * 1.6) * d.perc(n, 0.0005, dur)
    x = d.place([(click(2500, 0.03), 0, 1.0), (d.lowpass(click(900, 0.06), 2000), 0.012, 0.8),
                 (click(3500, 0.02), 0.09, 0.7), (d.lowpass(click(1200, 0.05), 2500), 0.1, 0.6)])
    return d.reverb(x, 0.08, 0.3)


def thump(f0=120, f1=45, sec=0.6, click=0.6, drive_amt=1.5, seed="t"):
    n = d.samples(sec)
    body = d.osc(d.glide(f0, f1, sec), sec) * d.perc(n, 0.001, sec)
    nz = d.lowpass(d.noise(0.03, "white", R(seed)), 4000) * d.perc(d.samples(0.03), 0.0005, 0.03)
    y = body.copy()
    y[:len(nz)] += nz * click
    return d.drive(y, drive_amt)


def boom(sec=2.5, f0=90, f1=32, verb=0.35, distance=0.0, seed="b"):
    n = d.samples(sec)
    sub = d.osc(d.glide(f0, f1, sec * 0.6), sec * 0.6)
    sub = np.pad(sub, (0, n - len(sub))) * d.perc(n, 0.002, sec)
    rumble = d.lowpass(d.noise(sec, "brown", R(seed)), 180) * d.perc(n, 0.005, sec * 0.9) * 0.8
    crack = d.bandpass(d.noise(0.12, "white", R(seed + "c")), 400, 5000) * d.perc(d.samples(0.12), 0.001, 0.12)
    y = sub + rumble
    y[:len(crack)] += crack * (0.5 * (1 - distance))
    y = d.drive(y, 2.2)
    if distance:
        y = d.lowpass(y, 1200 - 800 * distance)
    return d.reverb(d.stereo(y, 0.2), verb + 0.3 * distance, 2.2, bright=3000)


def bass_drop(sec=1.6, f0=140, f1=28, dist=1.5):
    n = d.samples(sec)
    f = d.glide(f0, f1, sec, "exp")
    y = d.osc(f, sec) + 0.25 * d.osc(f * 2, sec, "tri")
    y = d.drive(y * d.adsr(n, 0.005, 0.1, 0.9, sec * 0.4), dist)
    return d.stereo(d.lowpass(y, 2000), 0.1)


def punch(seed="p", heavy=False):
    a = thump(160 if heavy else 220, 55, 0.35, 1.0, 2.5 if heavy else 1.8, seed)
    snap = d.bandpass(d.noise(0.05, "white", R(seed + "s")), 1500, 6000) * d.perc(d.samples(0.05), 0.0005, 0.05)
    return d.reverb(d.place([(a, 0, 1.0), (snap, 0, 0.6)]), 0.12, 0.5)


def braam(sec=2.6, root=55, seed="br"):
    n = d.samples(sec)
    u = np.linspace(0, 1, n)
    x = np.zeros(n)
    for ratio, g in ((1, 1), (1.5, 0.7), (2, 0.6), (2.0 * 1.012, 0.5), (0.5, 0.8)):
        x += g * d.osc(root * ratio * (1 + 0.003 * np.sin(TAU * 4.5 * u * sec)), sec, "saw")
    y = d.sweep_filter(x, 200 + 1600 * np.exp(-u * 3) * np.minimum(u * 30, 1), 1.1, kind="low")
    y = d.drive(y * d.adsr(n, 0.03, 0.3, 0.7, 0.8), 2.5)
    return d.reverb(d.stereo(y, 0.5), 0.3, 2.5, bright=4000)


def metal_hit(freq=320, sec=1.6, index=8, seed="m"):
    n = d.samples(sec)
    e = d.perc(n, 0.001, sec)
    y = d.fm(np.full(n, freq), 1.41, index * e, sec) * e + d.fm(np.full(n, freq * 2.76), 1.13, 4 * e, sec) * e * 0.4
    y[:d.samples(0.02)] += d.bandpass(d.noise(0.02, "white", R(seed)), 2000, 9000) * 0.6
    return d.reverb(d.stereo(y, 0.3), 0.25, 1.6, bright=8000)


def taiko(freq=70, seed="tk", verb=0.4):
    n = d.samples(1.4)
    body = d.osc(d.glide(freq * 1.6, freq, 0.1), 0.1)
    body = np.concatenate([body, d.osc(np.full(n - len(body), freq), d.seconds(n - len(body)), phase=0.0)]) \
        * d.perc(n, 0.002, 1.2)
    skin = d.bandpass(d.noise(0.08, "white", R(seed)), 300, 2500) * d.perc(d.samples(0.08), 0.001, 0.08)
    body[:len(skin)] += skin * 0.5
    return d.reverb(d.stereo(d.drive(body, 1.6), 0.2), verb, 2.0, bright=3500)


def explosion(sec=3.0, seed="ex"):
    r = R(seed)
    n = d.samples(sec)
    y = boom(sec, 70, 25, 0.3, 0, seed)[:n, 0]
    crackle = np.zeros(n)
    for _ in range(140):
        i = int(r.uniform(0, 0.6) ** 2 * n)
        L = int(r.uniform(0.002, 0.01) * SR)
        crackle[i:i + L] += r.standard_normal(min(L, n - i)) * r.uniform(0.2, 1)
    crackle = d.highpass(crackle, 800) * d.perc(n, 0.001, sec)
    return d.reverb(d.stereo(d.drive(y + crackle * 0.5, 2.0), 0.6), 0.3, 2.4, bright=3000)


def pop(f=600, sec=0.12, bend=2.5, soft=False):
    n = d.samples(sec)
    y = d.osc(d.glide(f * bend, f, sec * 0.4, "ease").tolist() + [f] * (n - d.samples(sec * 0.4)), sec)
    y = y * d.perc(n, 0.0008 if not soft else 0.004, sec)
    return d.reverb(d.stereo(y, 0.1), 0.08, 0.3)


def click(f=4000, sec=0.015, seed="c", body=0.0):
    n = d.samples(sec)
    y = d.bandpass(d.noise(sec, "white", R(seed)), f * 0.5, min(f * 2, 20000)) * d.perc(n, 0.0002, sec)
    if body:
        y += d.osc(f / 8, sec) * d.perc(n, 0.0002, sec) * body
    return y


def typing(sec=1.6, rate=9.0, seed="ty", mech=False):
    r = R(seed)
    parts = []
    t = 0.05
    while t < sec:
        f = r.uniform(2500, 5000) if not mech else r.uniform(1200, 2500)
        k = click(f, 0.02 if not mech else 0.035, seed + str(t), body=0.8 if mech else 0.2)
        parts.append((d.stereo(k, 0.1), t, r.uniform(0.5, 1.0)))
        if mech:
            parts.append((click(f * 1.6, 0.012, seed + "u" + str(t)), t + 0.045, 0.4))
        t += r.exponential(1 / rate) + 0.03
        if r.random() < 0.08:   # space bar
            parts.append((click(900, 0.05, seed + "sp" + str(t), 1.0), t, 0.9))
            t += 0.12
    return d.reverb(d.place(parts), 0.06, 0.25)


def tone_note(f, sec, shape="sine", decay=None, attack=0.003):
    n = d.samples(sec)
    return d.osc(f, sec, shape) * d.perc(n, attack, decay or sec)


def bell(f, sec=1.2, bright=1.0):
    partials = [(1, 1), (2.0, 0.6 * bright), (2.76, 0.4 * bright), (5.4, 0.25 * bright), (8.93, 0.12 * bright)]
    decays = [3, 4.5, 6, 9, 13]
    return additive(f, sec, partials, decays)


def additive(f, sec, partials, decays):
    y = d.additive(f, sec, partials, decays)
    n = len(y)
    a = d.samples(0.002)
    y[:a] *= np.linspace(0, 1, a)
    return y


def chime_seq(notes, step=0.08, sec=1.0, bright=1.0, verb=0.3):
    parts = [(d.pan(bell(d.midi(m), sec, bright), (i % 3 - 1) * 0.4), i * step, 0.8) for i, m in enumerate(notes)]
    return d.reverb(d.place(parts), verb, 1.6)


def chip(notes, step=0.08, shape="square", dur=None, gap=0.0):
    seq = d.sequence([(d.midi(m), dur or step) for m in notes], lambda f, t: tone_note(f, t, shape, t * 0.9), gap)
    return d.stereo(seq * 0.6, 0.05)


def sparkle_cloud(sec=1.2, density=40, lo=4000, hi=11000, seed="sp", rise=False):
    r = R(seed)
    parts = []
    for k in range(int(density * sec)):
        t = r.uniform(0, sec * 0.85)
        f = r.uniform(lo, hi) * ((1 + t / sec) if rise else 1)
        g = bell(min(f, 15000) / 2.0, 0.35, 0.6)
        parts.append((d.pan(g, r.uniform(-0.8, 0.8)), t, r.uniform(0.15, 0.5) * (1 - t / sec * 0.6)))
    shimmer = d.highpass(d.noise(sec, "white", R(seed + "n")), 7000) * d.swell(d.samples(sec), 0.3) * 0.08
    parts.append((d.stereo(shimmer, 0.8), 0, 1))
    return d.reverb(d.place(parts), 0.35, 1.8, bright=12000)


def harp(notes, step=0.035, up=True):
    seq = notes if up else notes[::-1]
    parts = []
    for i, m in enumerate(seq):
        f = d.midi(m)
        n = d.samples(1.4)
        s = d.osc(f, 1.4, "tri") * 0.6 + d.osc(f * 2, 1.4) * 0.3
        parts.append((d.pan(s * d.perc(n, 0.002, 1.2), (i / len(seq) - 0.5)), i * step, 0.5))
    return d.reverb(d.place(parts), 0.35, 2.0)


def pad(chord, sec=3.0, bright=2500, breathy=0.2, seed="pd"):
    n = d.samples(sec)
    y = np.zeros(n)
    for m in chord:
        f = d.midi(m)
        for det in (-0.004, 0.0, 0.005):
            y += d.osc(f * (1 + det), sec, "saw") * 0.2
    y = d.lowpass(y, bright)
    y += d.bandpass(d.noise(sec, "pink", R(seed)), 800, 4000) * breathy
    y *= d.adsr(n, sec * 0.3, 0.2, 0.9, sec * 0.4)
    return d.reverb(d.stereo(y, 0.7), 0.45, 3.0, bright=6000)


# ================================================================ Transiciones (40)

T = "transiciones"
WH = ["whoosh", "swoosh", "transicion", "transition", "movimiento"]
sound("whoosh-corto", "Whoosh corto", "Short whoosh", T, lambda: whoosh(0.35, 500, 5000, seed="a"), WH + ["rapido"])
sound("whoosh", "Whoosh", "Whoosh", T, lambda: whoosh(0.7, seed="b"), WH)
sound("whoosh-largo", "Whoosh largo", "Long whoosh", T, lambda: whoosh(1.4, 200, 2500, peak=0.7, seed="c"), WH + ["lento"])
sound("whoosh-grave", "Whoosh grave", "Deep whoosh", T, lambda: whoosh(0.9, 120, 900, 1.2, "pink", seed="d", verb=0.2),
      WH + ["grave", "profundo"])
sound("whoosh-aire", "Whoosh de aire", "Airy whoosh", T, lambda: whoosh(0.8, 1500, 9000, 0.9, "pink", seed="e"),
      WH + ["aire", "suave"])
sound("whoosh-metalico", "Whoosh metálico", "Metallic whoosh", T, lambda: whoosh(0.7, 400, 4000, 2.0, seed="f", metal=0.8),
      WH + ["metal", "ciencia ficcion"])
sound("whoosh-doble", "Whoosh doble", "Double whoosh", T,
      lambda: d.place([(whoosh(0.4, 600, 5000, seed="g1"), 0, 1), (whoosh(0.45, 400, 4000, seed="g2"), 0.22, 0.9)]),
      WH + ["doble"])
sound("whoosh-reverso", "Whoosh en reversa", "Reverse whoosh", T, lambda: whoosh(0.8, 300, 6000, peak=0.95, seed="h"),
      WH + ["reversa", "reverse", "entrada"])
sound("swoosh-titulo", "Swoosh de título", "Title swoosh", T,
      lambda: d.place([(whoosh(0.5, 800, 8000, 1.6, seed="i"), 0, 1), (sparkle_cloud(0.6, 30, seed="i2"), 0.25, 0.5)]),
      WH + ["titulo", "texto", "title", "intro"])
sound("whoosh-izquierda-derecha", "Whoosh de izquierda a derecha", "Left-to-right whoosh", T,
      lambda: whoosh(0.7, 300, 4000, pan_from=-0.9, pan_to=0.9, seed="j"), WH + ["paneo", "estereo"])
sound("whoosh-derecha-izquierda", "Whoosh de derecha a izquierda", "Right-to-left whoosh", T,
      lambda: whoosh(0.7, 300, 4000, pan_from=0.9, pan_to=-0.9, seed="k"), WH + ["paneo", "estereo"])
sound("whoosh-espada", "Espada cortando el aire", "Sword swish", T, lambda: whoosh(0.3, 2500, 9000, 4.0, seed="l", verb=0.1),
      WH + ["espada", "sword", "corte", "accion"])
sound("whoosh-fuego", "Whoosh de fuego", "Fire whoosh", T,
      lambda: d.place([(whoosh(1.0, 150, 1500, 1.0, "brown", seed="m"), 0, 1),
                       (d.stereo(d.highpass(d.noise(1.0, "white", R("m2")), 3000) * d.swell(d.samples(1.0), 0.5)
                                 * (R("m3").random(d.samples(1.0)) > 0.985), 0.6), 0, 0.6)]), WH + ["fuego", "fire", "llama"])
sound("rafaga-viento", "Ráfaga de viento", "Wind gust", T, lambda: whoosh(1.6, 150, 1200, 3.0, "pink", peak=0.5, seed="n"),
      WH + ["viento", "wind", "rafaga"])
sound("whoosh-tela", "Tela que se agita", "Cloth flap", T,
      lambda: d.stereo(d.bandpass(d.noise(0.5, "pink", R("o")), 200, 2500)
                       * d.swell(d.samples(0.5), 0.4) * (0.6 + 0.4 * np.sign(np.sin(TAU * 22 * d.t_axis(0.5)))), 0.3),
      WH + ["tela", "ropa", "outfit", "cambio de ropa"])
sound("deslizar-arriba", "Deslizar hacia arriba", "Swipe up", T, lambda: whoosh(0.22, 1000, 7000, 2.0, peak=0.8, seed="p"),
      ["deslizar", "swipe", "arriba", "interfaz", "rapido"])
sound("deslizar-abajo", "Deslizar hacia abajo", "Swipe down", T,
      lambda: whoosh(0.22, 7000, 1000, 2.0, peak=0.3, seed="q"), ["deslizar", "swipe", "abajo", "interfaz"])
RS = ["riser", "subida", "tension", "build up", "anticipacion", "transicion"]
sound("riser-2s", "Subida (riser) 2 s", "Riser 2 s", T, lambda: riser_noise(2.0, seed="r1"), RS)
sound("riser-4s", "Subida (riser) 4 s", "Riser 4 s", T, lambda: riser_noise(4.0, seed="r2"), RS + ["largo"])
sound("riser-sinte-2s", "Subida sintetizada 2 s", "Synth riser 2 s", T, lambda: riser_synth(2.0, seed="r3"), RS + ["sinte"])
sound("riser-sinte-4s", "Subida sintetizada 4 s", "Synth riser 4 s", T,
      lambda: d.place([(riser_synth(4.0, 80, 1200), 0, 0.8), (riser_noise(4.0, seed="r4"), 0, 0.5)]), RS + ["epico"])
sound("riser-tension", "Subida de tensión", "Tension riser", T, lambda: riser_synth(3.0, 220, 660, 0.04), RS + ["suspenso"])
sound("riser-brillante", "Subida brillante", "Bright uplifter", T,
      lambda: d.place([(riser_noise(2.5, 800, 14000, "r5"), 0, 0.7), (sparkle_cloud(2.5, 25, seed="r6", rise=True), 0, 0.6)]),
      RS + ["brillo", "positivo"])
sound("riser-rapido", "Subida rápida", "Quick riser", T, lambda: riser_noise(0.9, 400, 10000, "r7"), RS + ["corto"])
DL = ["caida", "bajada", "downlifter", "transicion", "final"]
sound("caida-ruido", "Caída de ruido", "Noise downlifter", T, lambda: downlifter(2.0, "d1"), DL)
sound("caida-larga", "Caída larga", "Long downlifter", T, lambda: downlifter(3.5, "d2"), DL + ["largo"])
sound("caida-sinte", "Caída sintetizada", "Synth fall", T, lambda: downlifter(1.6, "d3", True), DL + ["sinte"])
sound("platillo-reverso", "Platillo en reversa", "Reverse cymbal", T, lambda: reverse_cymbal(1.5, "rc1"),
      ["platillo", "reverse cymbal", "reversa", "transicion", "entrada"])
sound("platillo-reverso-largo", "Platillo en reversa largo", "Long reverse cymbal", T, lambda: reverse_cymbal(3.0, "rc2"),
      ["platillo", "reverse cymbal", "reversa", "largo"])
sound("cinta-frenada", "Cinta que se frena", "Tape stop", T, lambda: tape_stop(0.8), ["tape stop", "frenar", "parar", "corte", "dj"])
sound("cinta-frenada-lenta", "Cinta que se frena lenta", "Slow tape stop", T, lambda: tape_stop(1.8, 160),
      ["tape stop", "frenar", "lento", "final"])
GL = ["glitch", "digital", "error", "falla", "transicion"]
sound("glitch-corto", "Glitch corto", "Short glitch", T, lambda: glitch(0.35, "g1"), GL)
sound("glitch-digital", "Glitch digital", "Digital glitch", T, lambda: glitch(0.8, "g2"), GL + ["computadora"])
sound("glitch-estatica", "Estática", "Static burst", T,
      lambda: d.stereo(d.bandpass(d.noise(0.6, "white", R("g3")), 500, 9000) * d.adsr(d.samples(0.6), 0.005, 0.05, 0.8, 0.1)
                       * (R("g4").random(d.samples(0.6)) > 0.3), 0.5), GL + ["estatica", "tv", "radio"])
sound("glitch-tartamudeo", "Tartamudeo digital", "Stutter glitch", T, lambda: glitch(0.7, "g5", stutter=True),
      GL + ["stutter", "repeticion"])
sound("zoom-entrada", "Zoom hacia adentro", "Zoom in", T,
      lambda: d.place([(whoosh(0.5, 300, 6000, 1.5, peak=0.9, seed="z1"), 0, 1),
                       (d.stereo(tone_note(d.glide(200, 900, 0.5), 0.5, "sine", 0.5) * np.linspace(0.2, 1, d.samples(0.5)) * 0.3, 0.2), 0, 1)]),
      ["zoom", "acercar", "zoom in", "transicion"])
sound("zoom-salida", "Zoom hacia afuera", "Zoom out", T,
      lambda: d.place([(whoosh(0.5, 6000, 300, 1.5, peak=0.15, seed="z2"), 0, 1),
                       (d.stereo(tone_note(d.glide(900, 200, 0.5), 0.5, "sine", 0.5) * 0.3, 0.2), 0, 1)]),
      ["zoom", "alejar", "zoom out", "transicion"])
sound("rampa-velocidad", "Rampa de velocidad", "Speed ramp", T,
      lambda: d.place([(riser_noise(0.8, 300, 9000, "sr1"), 0, 0.8), (whoosh(0.4, 500, 6000, seed="sr2"), 0.7, 1),
                       (punch("sr3"), 0.9, 0.7)]), ["speed ramp", "velocidad", "rampa", "transicion", "edit"])
sound("transicion-foto", "Transición con foto", "Photo transition", T,
      lambda: d.place([(whoosh(0.4, 600, 6000, seed="tf"), 0, 0.8), (shutter("tf2"), 0.3, 1)]),
      ["foto", "camara", "transicion", "flash"])
sound("pasar-pagina", "Pasar página", "Page turn", T,
      lambda: d.reverb(d.stereo(d.bandpass(d.noise(0.45, "pink", R("pp")), 800, 7000) * d.swell(d.samples(0.45), 0.65)
                                * (0.7 + 0.3 * R("pp2").random(d.samples(0.45))), 0.3), 0.1, 0.4),
      ["pagina", "page turn", "libro", "papel", "transicion"])


# ================================================================ Impactos (30)

I = "impactos"
BM = ["boom", "impacto", "impact", "golpe", "epico", "cine"]
sound("boom-cine", "Boom de cine", "Cinematic boom", I, lambda: boom(2.6, seed="b1"), BM + ["trailer"])
sound("boom-profundo", "Boom profundo", "Deep boom", I, lambda: boom(3.2, 70, 24, 0.3, seed="b2"), BM + ["grave", "sub"])
sound("boom-lejano", "Boom lejano", "Distant boom", I, lambda: boom(3.0, 80, 30, distance=0.7, seed="b3"), BM + ["lejos"])
BD = ["bass drop", "caida de bajo", "drop", "grave", "impacto", "edit"]
sound("bass-drop", "Caída de bajo", "Bass drop", I, lambda: bass_drop(1.6), BD)
sound("bass-drop-corto", "Caída de bajo corta", "Short bass drop", I, lambda: bass_drop(0.7, 180, 40, 1.8), BD + ["corto"])
sound("bass-drop-distorsion", "Caída de bajo distorsionada", "Distorted bass drop", I, lambda: bass_drop(1.8, 160, 26, 4.0),
      BD + ["distorsion", "trap"])
sound("sub-drop", "Sub drop", "Sub drop", I,
      lambda: d.stereo(d.osc(d.glide(70, 22, 2.2), 2.2) * d.perc(d.samples(2.2), 0.004, 2.2), 0.0), BD + ["sub"])
sound("golpe", "Golpe", "Punch", I, lambda: punch("pu1"), ["golpe", "puñetazo", "punch", "pelea", "accion"])
sound("golpe-fuerte", "Golpe fuerte", "Heavy punch", I, lambda: punch("pu2", heavy=True), ["golpe", "fuerte", "punch", "pelea"])
sound("bofetada", "Bofetada", "Slap", I,
      lambda: d.reverb(d.stereo(d.bandpass(d.noise(0.08, "white", R("sl")), 900, 7000) * d.perc(d.samples(0.08), 0.0003, 0.08)
                                + thump(300, 120, 0.08, 0, 1.2, "sl2")[:d.samples(0.08)] * 0.4, 0.1), 0.15, 0.4),
      ["bofetada", "slap", "cachetada", "humor", "drama"])
sound("braam", "Braam", "Braam", I, lambda: braam(), ["braam", "trailer", "epico", "cine", "drama", "inception"])
sound("braam-grave", "Braam grave", "Deep braam", I, lambda: braam(3.4, 41, "br2"), ["braam", "trailer", "grave", "oscuro"])
sound("golpe-metal", "Golpe metálico", "Metal hit", I, lambda: metal_hit(), ["metal", "golpe", "hierro", "impacto"])
sound("golpe-metal-agudo", "Golpe metálico agudo", "Bright metal hit", I, lambda: metal_hit(780, 1.2, 6, "m2"),
      ["metal", "agudo", "campana", "impacto"])
TR = ["trailer", "impacto", "cine", "epico", "hit", "drama"]
sound("impacto-trailer", "Impacto de tráiler", "Trailer hit", I,
      lambda: d.place([(boom(2.5, seed="th1"), 0, 1), (metal_hit(220, 2.0, 10, "th2"), 0, 0.5), (taiko(60, "th3"), 0, 0.7)]), TR)
sound("impacto-trailer-oscuro", "Impacto oscuro", "Dark trailer hit", I,
      lambda: d.place([(boom(3.0, 60, 22, seed="th4"), 0, 1), (braam(2.4, 36, "th5"), 0, 0.6)]), TR + ["oscuro", "terror"])
sound("impacto-trailer-brillante", "Impacto brillante", "Bright trailer hit", I,
      lambda: d.place([(boom(2.2, seed="th6"), 0, 0.9), (cymbal(2.0, "th7"), 0, 0.5), (metal_hit(520, 1.8, 7, "th8"), 0, 0.5)]),
      TR + ["brillante", "platillo"])
WG = ["whoosh", "golpe", "transicion", "impacto", "edit"]
sound("whoosh-golpe", "Whoosh y golpe", "Whoosh hit", I,
      lambda: d.place([(whoosh(0.5, 300, 5000, peak=0.9, seed="wg1"), 0, 0.9), (punch("wg2", True), 0.45, 1)]), WG)
sound("whoosh-boom", "Whoosh y boom", "Whoosh boom", I,
      lambda: d.place([(whoosh(0.7, 200, 4000, peak=0.92, seed="wg3"), 0, 0.9), (boom(2.4, seed="wg4"), 0.62, 1)]), WG + ["boom"])
sound("riser-golpe", "Subida y golpe", "Riser hit", I,
      lambda: d.place([(riser_noise(1.5, seed="wg5"), 0, 0.8), (boom(2.4, seed="wg6"), 1.45, 1)]), WG + ["riser", "drop"])
sound("tambor-taiko", "Tambor taiko", "Taiko drum", I, lambda: taiko(), ["tambor", "taiko", "drum", "epico", "impacto"])
sound("tambor-taiko-doble", "Doble taiko", "Double taiko", I,
      lambda: d.place([(taiko(75, "tk2"), 0, 0.8), (taiko(62, "tk3"), 0.28, 1)]), ["tambor", "taiko", "doble", "epico"])
sound("portazo", "Portazo", "Door slam", I,
      lambda: d.place([(d.reverb(d.stereo(thump(150, 70, 0.4, 1.0, 2.0, "ds"), 0.2), 0.3, 0.9), 0, 1),
                       (d.stereo(d.bandpass(d.noise(0.25, "white", R("ds2")), 2000, 6000) * d.perc(d.samples(0.25), 0.002, 0.25)
                                 * (np.sin(TAU * 60 * d.t_axis(0.25)) > 0.5), 0.3), 0.02, 0.3)]),
      ["puerta", "portazo", "door", "golpe", "enojo"])
sound("caida-objeto", "Objeto que cae", "Object drop", I,
      lambda: d.reverb(d.stereo(thump(260, 90, 0.3, 1.0, 1.5, "co"), 0.2), 0.2, 0.6), ["caida", "drop", "objeto", "golpe seco"])
sound("explosion", "Explosión", "Explosion", I, lambda: explosion(3.0, "ex1"), ["explosion", "bomba", "boom", "accion"])
sound("explosion-lejana", "Explosión lejana", "Distant explosion", I,
      lambda: d.stereo(d.lowpass(d.to_stereo(explosion(3.5, "ex2"))[:, 0], 900), 0.3), ["explosion", "lejos", "guerra"])
sound("trueno", "Trueno", "Thunder", I,
      lambda: d.place([(d.stereo(d.highpass(d.noise(0.15, "white", R("tn")), 1500) * d.perc(d.samples(0.15), 0.001, 0.15), 0.5), 0, 0.7),
                       (d.reverb(d.stereo(d.lowpass(d.noise(4.0, "brown", R("tn2")), 300) * d.swell(d.samples(4.0), 0.15, 1.2), 0.6),
                                 0.4, 3.0), 0.05, 1.2)]), ["trueno", "thunder", "tormenta", "rayo", "lluvia"])
sound("latigazo", "Latigazo", "Whip crack", I,
      lambda: d.place([(whoosh(0.25, 1500, 8000, 3, peak=0.95, seed="lt", verb=0), 0, 0.7),
                       (d.reverb(d.stereo(d.highpass(d.noise(0.02, "white", R("lt2")), 2000) * d.perc(d.samples(0.02), 0.0002, 0.02), 0.2),
                                 0.2, 0.8), 0.24, 1.2)]), ["latigo", "whip", "crack", "rapido"])
sound("golpe-glitch", "Golpe glitch", "Glitch hit", I,
      lambda: d.place([(punch("gh", True), 0, 1), (glitch(0.3, "gh2"), 0.02, 0.6)]), ["glitch", "golpe", "digital", "impacto"])
sound("impacto-reverso", "Impacto en reversa", "Reverse hit", I, lambda: d.to_stereo(boom(1.6, seed="rv"))[::-1],
      ["reversa", "reverse", "entrada", "suspenso"])


# ================================================================ Botones y avisos (35)

U = "interfaz"
PO = ["pop", "texto", "aparecer", "boton", "burbuja"]
sound("pop", "Pop", "Pop", U, lambda: pop(650), PO)
sound("pop-agudo", "Pop agudo", "High pop", U, lambda: pop(1100, 0.09), PO + ["agudo"])
sound("pop-grave", "Pop grave", "Low pop", U, lambda: pop(320, 0.16, 2.0), PO + ["grave"])
sound("pop-doble", "Pop doble", "Double pop", U, lambda: d.place([(pop(700), 0, 1), (pop(950), 0.09, 0.9)]), PO + ["doble"])
sound("pop-suave", "Pop suave", "Soft pop", U, lambda: pop(520, 0.2, 1.6, soft=True), PO + ["suave"])
sound("clic", "Clic", "Click", U, lambda: d.stereo(click(3500, 0.012, "c1", 0.3), 0.05), ["clic", "click", "boton"])
sound("clic-raton", "Clic de ratón", "Mouse click", U,
      lambda: d.place([(click(2800, 0.01, "c2", 0.5), 0, 1), (click(3800, 0.008, "c3", 0.3), 0.07, 0.6)]),
      ["clic", "raton", "mouse", "computadora", "tutorial"])
sound("clic-boligrafo", "Clic de bolígrafo", "Pen click", U,
      lambda: d.place([(click(5000, 0.008, "c4"), 0, 1), (click(4200, 0.01, "c5", 0.2), 0.05, 0.8)]), ["clic", "boligrafo", "pen"])
sound("toque", "Toque", "Tap", U, lambda: d.stereo(click(1800, 0.03, "c6", 1.2), 0.05), ["toque", "tap", "pantalla", "celular"])
sound("toque-doble", "Doble toque", "Double tap", U,
      lambda: d.place([(click(1800, 0.03, "c7", 1.2), 0, 1), (click(2000, 0.03, "c8", 1.2), 0.12, 0.9)]), ["toque", "doble", "like"])
sound("teclado", "Teclado", "Keyboard typing", U, lambda: typing(1.6), ["teclado", "typing", "escribir", "computadora", "texto"])
sound("teclado-rapido", "Teclado rápido", "Fast typing", U, lambda: typing(1.6, 16, "ty2"), ["teclado", "rapido", "hacker"])
sound("teclado-mecanico", "Teclado mecánico", "Mechanical keyboard", U, lambda: typing(1.8, 8, "ty3", True),
      ["teclado", "mecanico", "gaming", "asmr"])
NT = ["notificacion", "notification", "aviso", "alerta", "celular", "mensaje"]
sound("notificacion-campanita", "Campanita de aviso", "Bell notification", U, lambda: chime_seq([88, 95], 0.1, 0.8), NT)
sound("notificacion-dos-tonos", "Aviso de dos tonos", "Two-tone alert", U,
      lambda: d.reverb(d.place([(tone_note(d.midi(84), 0.12, "sine", 0.3), 0, 0.8), (tone_note(d.midi(91), 0.25, "sine", 0.4), 0.11, 0.8)]),
                       0.15, 0.6), NT)
sound("notificacion-mensaje", "Mensaje nuevo", "New message", U,
      lambda: d.reverb(d.place([(pop(900, 0.08), 0, 0.7), (tone_note(d.midi(86), 0.2, "tri", 0.25), 0.05, 0.7)]), 0.12, 0.5),
      NT + ["chat", "whatsapp"])
sound("notificacion-suave", "Aviso suave", "Soft alert", U, lambda: chime_seq([79, 84, 88], 0.09, 1.0, 0.6), NT + ["suave"])
sound("notificacion-cristal", "Aviso de cristal", "Glass alert", U,
      lambda: d.reverb(d.stereo(additive(1760, 1.2, [(1, 1), (2.32, 0.5), (4.25, 0.3)], [4, 6, 9]), 0.3), 0.35, 1.2),
      NT + ["cristal", "glass"])
sound("me-gusta", "Me gusta", "Like", U, lambda: d.place([(pop(800), 0, 0.8), (chime_seq([84, 88, 91], 0.05, 0.6), 0.04, 0.8)]),
      ["like", "me gusta", "corazon", "redes", "heart"])
sound("seguir", "Nuevo seguidor", "New follower", U, lambda: chime_seq([76, 83, 88, 95], 0.07, 0.8),
      ["seguir", "follow", "seguidor", "suscribirse", "redes"])
sound("correcto", "Correcto", "Correct", U, lambda: chime_seq([84, 91], 0.09, 0.7), ["correcto", "check", "bien", "success"])
sound("logro", "Logro", "Achievement", U, lambda: chime_seq([72, 76, 79, 84, 88], 0.06, 1.2), ["logro", "achievement", "exito"])
sound("completado", "Completado", "Completed", U,
      lambda: d.place([(pop(700), 0, 0.6), (chime_seq([79, 86, 91], 0.08, 1.0), 0.03, 0.9)]), ["completado", "listo", "done"])
sound("error-zumbido", "Error", "Error buzz", U,
      lambda: d.stereo(d.lowpass(d.osc(140, 0.35, "square") + d.osc(147, 0.35, "square"), 2500) * d.adsr(d.samples(0.35), 0.005, 0.05, 0.8, 0.05) * 0.4, 0.1),
      ["error", "incorrecto", "mal", "wrong", "buzz"])
sound("error-negativo", "Negativo", "Negative tone", U,
      lambda: d.reverb(d.place([(tone_note(d.midi(67), 0.18, "tri", 0.3), 0, 0.8), (tone_note(d.midi(60), 0.35, "tri", 0.5), 0.16, 0.8)]),
                       0.15, 0.6), ["error", "negativo", "no", "fallo"])
sound("mensaje-enviado", "Mensaje enviado", "Message sent", U,
      lambda: d.place([(whoosh(0.25, 1500, 8000, 2.0, peak=0.8, seed="ms", verb=0.05), 0, 0.7), (pop(1200, 0.06), 0.18, 0.4)]),
      ["enviado", "sent", "mensaje", "chat"])
sound("mensaje-recibido", "Mensaje recibido", "Message received", U,
      lambda: d.place([(pop(600, 0.1), 0, 0.8), (pop(900, 0.1), 0.08, 0.7)]), ["recibido", "received", "mensaje", "chat"])
sound("interruptor-encender", "Interruptor encendido", "Switch on", U,
      lambda: d.place([(click(2500, 0.012, "sw1", 0.8), 0, 1), (tone_note(d.midi(88), 0.08, "sine", 0.1), 0.01, 0.3)]),
      ["interruptor", "switch", "encender", "on", "luz"])
sound("interruptor-apagar", "Interruptor apagado", "Switch off", U,
      lambda: d.place([(click(2000, 0.012, "sw2", 0.8), 0, 1), (tone_note(d.midi(81), 0.08, "sine", 0.1), 0.01, 0.3)]),
      ["interruptor", "switch", "apagar", "off"])
sound("bloquear", "Bloquear", "Lock", U,
      lambda: d.place([(click(1600, 0.02, "lk1", 1.0), 0, 1), (click(3000, 0.01, "lk2", 0.4), 0.06, 0.7)]),
      ["bloquear", "lock", "candado", "celular"])
sound("desbloquear", "Desbloquear", "Unlock", U,
      lambda: d.place([(click(3000, 0.01, "lk3", 0.4), 0, 0.7), (click(1800, 0.02, "lk4", 1.0), 0.05, 1),
                       (tone_note(d.midi(91), 0.15, "sine", 0.2), 0.08, 0.25)]), ["desbloquear", "unlock", "celular"])
sound("deslizar-interfaz", "Deslizar en pantalla", "UI swipe", U, lambda: whoosh(0.18, 2000, 9000, 1.5, peak=0.6, seed="us", verb=0),
      ["deslizar", "swipe", "pantalla", "celular", "app"])
sound("maquina-escribir", "Máquina de escribir", "Typewriter", U,
      lambda: d.place([(typing(1.4, 7, "tw", True), 0, 1), (d.reverb(d.stereo(bell(d.midi(96), 0.9), 0.2), 0.2, 0.8), 1.45, 0.5)]),
      ["maquina de escribir", "typewriter", "retro", "texto", "escribir"])
sound("camara-foto", "Cámara de fotos", "Camera shutter", U, lambda: shutter(), ["camara", "foto", "shutter", "click", "selfie"])
sound("captura-pantalla", "Captura de pantalla", "Screenshot", U,
      lambda: d.place([(shutter("ss"), 0, 0.7), (whoosh(0.2, 3000, 9000, 1.2, seed="ss2", verb=0), 0.05, 0.3)]),
      ["captura", "screenshot", "pantalla", "celular"])


# ================================================================ Monedas y juegos (20)

G = "juegos"
CO = ["moneda", "coin", "juego", "game", "dinero", "8 bits"]
sound("moneda", "Moneda", "Coin", G, lambda: chip([83, 88], 0.07, "square", gap=0.0), CO)
sound("moneda-doble", "Dos monedas", "Double coin", G, lambda: d.place([(chip([83, 88], 0.06), 0, 1), (chip([86, 91], 0.06), 0.14, 0.9)]), CO)
sound("lluvia-monedas", "Lluvia de monedas", "Coin shower", G,
      lambda: d.place([(d.pan(chip([80 + (k * 5) % 12, 88 + (k * 3) % 7], 0.05), (k % 5 - 2) / 3), k * 0.07, 0.6) for k in range(16)]),
      CO + ["lluvia", "premio"])
sound("subir-nivel", "Subir de nivel", "Level up", G, lambda: chip([72, 76, 79, 84, 88, 91, 96], 0.06, "pulse25"),
      ["nivel", "level up", "juego", "logro", "8 bits"])
sound("poder", "Poder especial", "Power up", G,
      lambda: chip([60 + k for k in range(0, 25, 2)], 0.03, "square"), ["poder", "power up", "juego", "energia"])
sound("salto", "Salto", "Jump", G, lambda: d.stereo(tone_note(d.glide(300, 900, 0.18), 0.18, "square", 0.18) * 0.5, 0.05),
      ["salto", "jump", "juego", "brincar"])
sound("game-over", "Fin del juego", "Game over", G, lambda: chip([67, 66, 65, 64, 52], 0.18, "square"),
      ["game over", "fin", "perder", "juego", "fallo"])
sound("vida-extra", "Vida extra", "Extra life", G, lambda: chip([76, 79, 88, 84, 86, 91], 0.07, "pulse25"),
      ["vida extra", "1up", "juego", "bonus"])
sound("gema", "Gema", "Gem", G, lambda: d.place([(chip([91, 96, 100], 0.04, "tri"), 0, 1), (sparkle_cloud(0.5, 30, seed="gem"), 0.05, 0.4)]),
      ["gema", "diamante", "gem", "juego", "brillo"])
sound("bonus", "Bonus", "Bonus", G, lambda: chip([72, 79, 84, 79, 84, 88, 91], 0.05, "square"), ["bonus", "extra", "juego", "premio"])
sound("inicio-juego", "Inicio del juego", "Game start", G, lambda: chip([60, 64, 67, 72, 67, 72, 76], 0.09, "pulse25"),
      ["inicio", "start", "juego", "empezar"])
sound("laser", "Láser", "Laser", G, lambda: d.stereo(tone_note(d.glide(2500, 200, 0.25), 0.25, "square", 0.25) * 0.4, 0.2),
      ["laser", "disparo", "pew", "ciencia ficcion", "juego"])
sound("laser-doble", "Láser doble", "Double laser", G,
      lambda: d.place([(d.stereo(tone_note(d.glide(3000, 300, 0.18), 0.18, "square", 0.18) * 0.4, 0.2), t, 1) for t in (0, 0.14)]),
      ["laser", "disparo", "doble", "juego"])
sound("explosion-8bits", "Explosión de 8 bits", "8-bit explosion", G,
      lambda: d.stereo(d.bitcrush(d.lowpass(d.noise(0.7, "white", R("e8")), 3000) * d.perc(d.samples(0.7), 0.001, 0.7), 4, 12), 0.1),
      ["explosion", "8 bits", "retro", "juego"])
sound("menu-seleccion", "Seleccionar en el menú", "Menu select", G, lambda: chip([84, 91], 0.04, "pulse25"),
      ["menu", "seleccionar", "select", "juego", "boton"])
sound("contador-puntos", "Contador de puntos", "Score counter", G,
      lambda: d.place([(chip([96], 0.025, "square"), k * 0.045, 0.5) for k in range(20)]), ["puntos", "score", "contador", "juego"])
sound("dano", "Daño", "Hurt", G, lambda: d.stereo(d.bitcrush(tone_note(d.glide(500, 120, 0.25), 0.25, "square", 0.25), 4, 6) * 0.5, 0.05),
      ["daño", "hurt", "golpe", "juego"])
sound("victoria-8bits", "Victoria de 8 bits", "8-bit victory", G,
      lambda: chip([67, 67, 67, 72, 72, 76, 72, 79], 0.11, "pulse25"), ["victoria", "ganar", "win", "juego", "fanfarria"])
sound("caja-registradora", "Caja registradora", "Cash register", G,
      lambda: d.place([(click(2500, 0.02, "cr1", 1.0), 0, 0.8), (click(1800, 0.03, "cr2", 1.0), 0.08, 0.7),
                       (d.reverb(d.stereo(bell(d.midi(93), 1.4), 0.2), 0.25, 1.0), 0.15, 0.9)]),
      ["caja registradora", "cash", "venta", "dinero", "ka-ching", "negocio"])
sound("premio-mayor", "Premio mayor", "Jackpot", G,
      lambda: d.place([(chip([72, 76, 79, 84] * 3, 0.06, "square"), 0, 0.7), (chime_seq([84, 88, 91, 96, 100], 0.08, 1.2), 0.5, 0.8),
                       ] + [(d.pan(chip([88 + k % 5], 0.04), (k % 7 - 3) / 4), 0.5 + k * 0.05, 0.4) for k in range(20)]),
      ["premio", "jackpot", "ganar", "casino", "sorteo"])


# ================================================================ Magia y brillos (20)

M = "magia"
SP = ["brillo", "sparkle", "magia", "glitter", "destello"]
sound("brillo-escena", "Brillo de cambio de escena", "Scene sparkle", M, lambda: sparkle_cloud(1.2, seed="s1"),
      SP + ["transicion", "escena"])
sound("brillo-largo", "Brillo largo", "Long sparkle", M, lambda: sparkle_cloud(2.5, 35, seed="s2"), SP + ["largo"])
sound("brillo-oscuro", "Brillo misterioso", "Dark shimmer", M, lambda: sparkle_cloud(1.8, 25, 2000, 6000, "s3"),
      SP + ["misterio", "oscuro"])
sound("campanitas", "Campanitas", "Wind chimes", M,
      lambda: chime_seq([88, 91, 95, 98, 100, 103, 98, 95], 0.11, 1.4, 0.8, 0.4), ["campanitas", "chimes", "viento", "suave"])
sound("campanitas-rapidas", "Campanitas rápidas", "Quick chimes", M, lambda: chime_seq([95, 98, 100, 103, 107], 0.04, 1.0),
      ["campanitas", "chimes", "rapido", "brillo"])
sound("varita-magica", "Varita mágica", "Magic wand", M,
      lambda: d.place([(sparkle_cloud(1.0, 50, seed="v1", rise=True), 0, 1), (harp([72, 76, 79, 84, 88, 91], 0.04), 0, 0.5)]),
      ["varita", "magic wand", "hada", "magia", "hechizo"])
sound("varita-subida", "Varita que sube", "Rising wand", M,
      lambda: d.place([(riser_noise(1.0, 2000, 14000, "v2"), 0, 0.4), (sparkle_cloud(1.0, 40, seed="v3", rise=True), 0, 1)]),
      ["varita", "subida", "magia", "aparecer"])
sound("polvo-hada", "Polvo de hada", "Fairy dust", M, lambda: sparkle_cloud(1.5, 60, 6000, 13000, "fd"), ["hada", "fairy", "polvo", "magia"])
sound("arpa-subida", "Arpa que sube", "Harp glissando up", M, lambda: harp([60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84, 86, 88]),
      ["arpa", "harp", "glissando", "sueño", "recuerdo"])
sound("arpa-bajada", "Arpa que baja", "Harp glissando down", M,
      lambda: harp([60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84, 86, 88], up=False), ["arpa", "harp", "bajada", "flashback"])
sound("destello-ding", "Destello", "Sparkle ding", M,
      lambda: d.place([(d.reverb(d.stereo(bell(d.midi(100), 1.0), 0.3), 0.3, 1.2), 0, 1), (sparkle_cloud(0.6, 30, seed="dd"), 0, 0.4)]),
      ["destello", "ding", "brillo", "limpio", "nuevo"])
sound("aparicion", "Aparición", "Poof reveal", M,
      lambda: d.place([(whoosh(0.4, 400, 5000, 1.0, "pink", peak=0.3, seed="ap"), 0, 0.9), (sparkle_cloud(0.8, 40, seed="ap2"), 0.1, 0.7)]),
      ["aparicion", "poof", "aparecer", "revelacion", "reveal"])
sound("desaparicion", "Desaparición", "Vanish", M,
      lambda: d.place([(sparkle_cloud(0.6, 40, seed="dp"), 0, 0.7), (whoosh(0.5, 5000, 300, 1.0, "pink", peak=0.2, seed="dp2"), 0.15, 0.9)]),
      ["desaparecer", "vanish", "magia", "puf"])
sound("angelical", "Angelical", "Angelic", M, lambda: pad([72, 76, 79, 84], 3.5, 3000, 0.25), ["angel", "angelical", "cielo", "paz", "milagro"])
sound("coro-celestial", "Coro celestial", "Heavenly choir", M,
      lambda: d.place([(pad([60, 67, 72, 76], 4.0, 2200, 0.4, "cc"), 0, 1), (sparkle_cloud(3.0, 12, seed="cc2"), 0.5, 0.4)]),
      ["coro", "celestial", "choir", "angeles", "revelacion"])
sound("cristal", "Copa de cristal", "Glass ting", M,
      lambda: d.reverb(d.stereo(additive(2093, 2.0, [(1, 1), (2.32, 0.4), (4.25, 0.25), (6.63, 0.1)], [2, 3.5, 6, 9]), 0.3), 0.3, 1.5),
      ["cristal", "copa", "brindis", "glass", "ting"])
sound("hechizo", "Hechizo", "Spell", M,
      lambda: d.reverb(d.stereo(d.fm(d.glide(300, 900, 1.2), 2.01, 3 + 2 * np.sin(TAU * 6 * d.t_axis(1.2)), 1.2)
                                * d.swell(d.samples(1.2), 0.6) * 0.5, 0.6), 0.4, 1.8), ["hechizo", "spell", "magia", "fantasia"])
sound("teletransporte", "Teletransporte", "Teleport", M,
      lambda: d.place([(d.stereo(d.fm(d.glide(200, 2400, 0.7), 1.5, 6 * d.perc(d.samples(0.7), 0.01, 0.7), 0.7) * 0.4, 0.4), 0, 1),
                       (sparkle_cloud(0.7, 30, seed="tp"), 0.3, 0.5)]), ["teletransporte", "teleport", "ciencia ficcion", "desaparecer"])
sound("burbujas-magicas", "Burbujas mágicas", "Magic bubbles", M,
      lambda: d.place([(d.pan(pop(400 + 120 * k, 0.12, 2.0), (k % 5 - 2) / 3), k * 0.08, 0.6) for k in range(10)]
                      + [(sparkle_cloud(1.0, 20, seed="bm"), 0.1, 0.4)]), ["burbujas", "bubbles", "magia", "infantil"])
sound("aura", "Aura brillante", "Shimmer aura", M,
      lambda: d.place([(pad([84, 88, 91, 96], 3.0, 6000, 0.1, "au"), 0, 0.6), (sparkle_cloud(3.0, 18, seed="au2"), 0, 0.6)]),
      ["aura", "shimmer", "brillo", "fondo", "suave"])


# ================================================================ Comedia (20)

C = "comedia"


def boing(f=180, sec=0.7, depth=0.35, rate=11):
    t = d.t_axis(sec)
    f_curve = f * (1 + depth * np.sin(TAU * rate * t) * np.exp(-t * 5)) * (1 + 0.6 * np.exp(-t * 12))
    return d.stereo(d.osc(f_curve, sec, "tri") * d.perc(d.samples(sec), 0.002, sec) * 0.8, 0.1)


sound("boing", "Boing", "Boing", C, lambda: boing(), ["boing", "resorte", "rebote", "humor", "caricatura"])
sound("boing-agudo", "Boing agudo", "High boing", C, lambda: boing(420, 0.5, 0.3, 14), ["boing", "agudo", "humor"])
sound("boing-grave", "Boing grave", "Low boing", C, lambda: boing(90, 0.9, 0.4, 8), ["boing", "grave", "humor"])
sound("silbato-subida", "Silbato de subida", "Slide whistle up", C,
      lambda: d.stereo(d.osc(d.glide(500, 1800, 0.7, "ease") * (1 + 0.01 * np.sin(TAU * 6 * d.t_axis(0.7))), 0.7)
                       * d.adsr(d.samples(0.7), 0.03, 0.1, 0.9, 0.1) * 0.6, 0.1), ["silbato", "slide whistle", "subida", "humor"])
sound("silbato-bajada", "Silbato de bajada", "Slide whistle down", C,
      lambda: d.stereo(d.osc(d.glide(1800, 400, 0.8, "ease") * (1 + 0.01 * np.sin(TAU * 6 * d.t_axis(0.8))), 0.8)
                       * d.adsr(d.samples(0.8), 0.03, 0.1, 0.9, 0.1) * 0.6, 0.1), ["silbato", "bajada", "caida", "humor"])


def trombone_note(m, sec, bend=0.0):
    t = d.t_axis(sec)
    f = d.midi(m) * (1 + bend * t / sec) * (1 + 0.012 * np.sin(TAU * 5.5 * t) * (t > sec * 0.4))
    y = d.osc(f, sec, "saw")
    y = d.sweep_filter(y, 500 + 1400 * d.adsr(len(t), 0.06, 0.2, 0.6, 0.15), 1.6, kind="low")
    return y * d.adsr(len(t), 0.04, 0.1, 0.85, 0.12)


sound("trombon-triste", "Trombón triste", "Sad trombone", C,
      lambda: d.reverb(d.stereo(np.concatenate([trombone_note(58, 0.45), trombone_note(57, 0.45), trombone_note(56, 0.45),
                                                trombone_note(55, 1.3, -0.03)]) * 0.5, 0.2), 0.2, 1.2),
      ["trombon", "triste", "sad", "fallo", "fail", "humor"])
sound("ba-dum-tss", "Ba dum tss", "Rimshot", C,
      lambda: d.place([(snare("bd1"), 0, 0.7), (snare("bd2"), 0.14, 0.7), (kick(), 0.3, 0.8), (cymbal(1.2, "bd3"), 0.3, 0.7)]),
      ["ba dum tss", "rimshot", "chiste", "broma", "humor"])
sound("disco-rayado", "Disco rayado", "Record scratch", C,
      lambda: d.stereo(d.bandpass(d.noise(0.45, "white", R("rs")), 600, 4000)
                       * np.abs(np.sin(TAU * d.glide(9, 3, 0.45) * d.t_axis(0.45))) * d.perc(d.samples(0.45), 0.002, 0.45), 0.1),
      ["disco rayado", "record scratch", "pausa", "que", "humor"])
sound("disco-rayado-frenada", "Frenada de disco", "Record stop", C,
      lambda: d.place([(d.stereo(d.bandpass(d.noise(0.25, "white", R("rs2")), 800, 5000) * d.perc(d.samples(0.25), 0.002, 0.25), 0.1), 0, 0.8),
                       (tape_stop(0.6, 300), 0.05, 0.7)]), ["disco", "frenada", "stop", "pausa", "silencio incomodo"])
sound("bocina-payaso", "Bocina de payaso", "Clown horn", C,
      lambda: d.place([(d.stereo(d.lowpass(d.osc(370, 0.22, "square") + 0.5 * d.osc(372, 0.22, "saw"), 3000)
                                 * d.adsr(d.samples(0.22), 0.01, 0.05, 0.8, 0.05) * 0.5, 0.1), t, 1) for t in (0, 0.28)]),
      ["bocina", "payaso", "honk", "horn", "humor", "circo"])
sound("chillido-juguete", "Juguete que chilla", "Toy squeak", C,
      lambda: d.stereo(d.osc(d.glide(1200, 1800, 0.18, "ease") + 40 * np.sin(TAU * 30 * d.t_axis(0.18)), 0.18)
                       * d.adsr(d.samples(0.18), 0.01, 0.05, 0.7, 0.05) * 0.5, 0.05), ["chillido", "squeak", "juguete", "mascota"])
sound("chillido-doble", "Doble chillido", "Double squeak", C,
      lambda: d.place([(SOUNDS["chillido-juguete"].make(), 0, 1), (SOUNDS["chillido-juguete"].make(), 0.22, 0.9)]),
      ["chillido", "squeak", "doble", "juguete"])
sound("tambaleo", "Tambaleo", "Wobble", C,
      lambda: d.stereo(d.osc(220 * (1 + 0.25 * np.sin(TAU * 7 * d.t_axis(1.0))), 1.0, "tri") * d.adsr(d.samples(1.0), 0.02, 0.1, 0.8, 0.2) * 0.5, 0.2),
      ["tambaleo", "wobble", "mareo", "humor", "borracho"])
sound("carrera-caricatura", "Carrera de caricatura", "Cartoon run", C,
      lambda: d.place([(d.pan(tom(260 + 40 * (k % 2)), (k % 2) * 0.4 - 0.2), k * 0.055, 0.6) for k in range(16)]),
      ["correr", "carrera", "run", "caricatura", "huir", "humor"])
sound("cremallera", "Cremallera", "Zipper", C,
      lambda: d.stereo(d.bandpass(d.noise(0.5, "white", R("zp")), 1500, 8000) * (np.sin(TAU * d.glide(40, 90, 0.5) * d.t_axis(0.5)) > 0.3)
                       * d.adsr(d.samples(0.5), 0.02, 0.05, 0.9, 0.05) * 0.7, 0.2), ["cremallera", "zipper", "cierre", "ropa"])
sound("resorte", "Resorte", "Spring", C, lambda: boing(600, 0.6, 0.15, 22), ["resorte", "spring", "rebote", "humor"])
sound("bonk", "Bonk", "Bonk", C,
      lambda: d.reverb(d.stereo(additive(900, 0.4, [(1, 1), (2.7, 0.5), (5.1, 0.2)], [18, 26, 40]), 0.1), 0.15, 0.4),
      ["bonk", "golpe", "cabeza", "madera", "humor"])
sound("sarten", "Golpe de sartén", "Frying pan", C, lambda: metal_hit(440, 1.4, 3, "fp"), ["sarten", "pan", "golpe", "humor", "cocina"])
sound("grillos", "Grillos (silencio incómodo)", "Crickets", C,
      lambda: d.place([(d.pan(cricket(k), (k % 3 - 1) * 0.5), k * 0.55 + (k % 2) * 0.17, 0.5) for k in range(6)]),
      ["grillos", "crickets", "silencio incomodo", "awkward", "nadie", "humor"])


def cricket(k):
    t = d.t_axis(0.3)
    gate = (np.sin(TAU * 32 * t) > 0) * (t < 0.24)
    return d.osc(4300 + 60 * k, 0.3) * gate * 0.4


def tom(f=180):
    n = d.samples(0.25)
    return d.osc(d.glide(f * 1.5, f, 0.05).tolist() + [f] * (n - d.samples(0.05)), 0.25) * d.perc(n, 0.001, 0.25)


# ================================================================ Suspenso y drama (15)

S = "suspenso"


def heartbeat(bpm=70, beats=4):
    gap = 60 / bpm
    parts = []
    for k in range(beats):
        parts += [(thump(70, 40, 0.18, 0.1, 1.2, "hb" + str(k)), k * gap, 1.0), (thump(60, 38, 0.2, 0.1, 1.2, "hc" + str(k)), k * gap + 0.22, 0.75)]
    return d.reverb(d.place(parts), 0.1, 0.6)


sound("latido", "Latido", "Heartbeat", S, lambda: heartbeat(), ["latido", "heartbeat", "corazon", "tension", "suspenso"])
sound("latido-rapido", "Latido acelerado", "Fast heartbeat", S, lambda: heartbeat(130, 7), ["latido", "rapido", "miedo", "nervios"])


def drone(root=41, sec=5.0, metal=0.0, rising=False, seed="dr"):
    n = d.samples(sec)
    u = np.linspace(0, 1, n)
    y = np.zeros(n)
    bend = 1 + (0.06 * u ** 2 if rising else 0)
    for ratio, g in ((1, 1), (1.5, 0.4), (2.02, 0.3), (2.97, 0.15)):
        y += g * d.osc(d.midi(root) * ratio * bend, sec, "saw")
    y = d.sweep_filter(y, 900 + 2500 * u, 0.9, kind="low") if rising else d.lowpass(y, 900)
    y += d.bandpass(d.noise(sec, "pink", R(seed)), 200, 1200) * 0.3
    if metal:
        y += metal * d.fm(np.full(n, d.midi(root + 36)), 1.41, 3, sec) * 0.2
    y *= d.adsr(n, sec * 0.25, 0.2, 0.9, sec * 0.25)
    return d.reverb(d.stereo(y * 0.4, 0.7), 0.4, 3.0, bright=3000)


sound("dron-oscuro", "Dron oscuro", "Dark drone", S, lambda: drone(), ["dron", "drone", "oscuro", "suspenso", "terror", "fondo"])
sound("dron-metalico", "Dron metálico", "Metallic drone", S, lambda: drone(36, 5.0, 1.0, seed="dr2"), ["dron", "metal", "industrial", "misterio"])
sound("tension-subiendo", "Tensión que sube", "Rising tension", S, lambda: drone(43, 5.0, 0.4, True, "dr3"),
      ["tension", "suspenso", "subida", "miedo"])


def tick_tock(rate=1.0, count=6):
    parts = []
    for k in range(count):
        parts.append((d.stereo(additive(2600 if k % 2 == 0 else 2100, 0.05, [(1, 1), (2.3, 0.4)], [80, 120]) * 0.8, 0.05),
                      k / rate * 0.5, 1))
    return d.reverb(d.place(parts), 0.12, 0.5)


sound("reloj", "Reloj", "Ticking clock", S, lambda: tick_tock(), ["reloj", "tic tac", "clock", "tiempo", "espera"])
sound("reloj-rapido", "Reloj acelerado", "Fast clock", S, lambda: tick_tock(2.5, 12), ["reloj", "rapido", "apuro", "cuenta regresiva"])
sound("sirena", "Sirena", "Siren", S,
      lambda: d.reverb(d.stereo(d.osc(700 + 350 * np.sin(TAU * 0.9 * d.t_axis(3.0)), 3.0, "tri") * d.adsr(d.samples(3.0), 0.1, 0.1, 0.9, 0.3) * 0.4, 0.2),
                       0.3, 1.5), ["sirena", "alarma", "policia", "emergencia", "siren"])
sound("despertador", "Despertador", "Alarm clock", S,
      lambda: d.place([(d.stereo(d.osc(2000, 0.08, "square") * 0.3 * d.adsr(d.samples(0.08), 0.002, 0.01, 0.9, 0.01), 0.05), k * 0.12 + (k // 4) * 0.25, 1)
                       for k in range(12)]), ["despertador", "alarma", "alarm", "mañana", "despertar"])
sound("golpe-dramatico", "Golpe dramático", "Dramatic sting", S,
      lambda: d.place([(dramatic_note(48, 0.3), 0, 1), (dramatic_note(49, 0.3), 0.35, 1), (dramatic_note(46, 1.8), 0.75, 1.1)]),
      ["dramatico", "dun dun dun", "sorpresa", "drama", "revelacion"])
sound("golpe-dramatico-corto", "Acento dramático", "Short dramatic sting", S,
      lambda: d.place([(dramatic_note(45, 1.6), 0, 1), (boom(2.0, seed="gd"), 0, 0.5)]), ["dramatico", "acento", "drama", "shock"])


def dramatic_note(m, sec):
    n = d.samples(sec)
    y = np.zeros(n)
    for o, g in ((0, 1), (12, 0.6), (19, 0.3), (-12, 0.7)):
        y += g * d.osc(d.midi(m + o), sec, "saw")
    y = d.lowpass(y, 1800) * d.adsr(n, 0.01, 0.15, 0.6, min(0.3, sec * 0.4))
    return d.reverb(d.stereo(d.drive(y * 0.4, 1.5), 0.5), 0.3, 1.8)


sound("susto-terror", "Susto", "Jump scare", S,
      lambda: d.place([(d.reverb(d.stereo(sum(d.osc(d.midi(m) * (1 + 0.01 * np.sin(TAU * 7 * d.t_axis(1.5))), 1.5, "saw")
                                              for m in (72, 73, 78, 79)) * d.perc(d.samples(1.5), 0.005, 1.5) * 0.25, 0.6), 0.35, 2.0), 0, 1),
                       (boom(1.5, seed="st"), 0, 0.6)]), ["susto", "terror", "jump scare", "miedo"])
sound("revelacion", "Revelación", "Reveal sting", S,
      lambda: d.place([(riser_synth(1.2, 220, 660), 0, 0.6), (chime_seq([72, 79, 84, 88], 0.05, 1.6), 1.15, 0.9), (boom(2.0, seed="rv2"), 1.15, 0.5)]),
      ["revelacion", "reveal", "sorpresa", "antes y despues", "resultado"])
sound("campana-iglesia", "Campana de iglesia", "Church bell", S,
      lambda: d.place([(d.reverb(d.stereo(additive(220, 4.0, [(0.5, 0.6), (1, 1), (1.19, 0.6), (1.5, 0.4), (2, 0.5), (2.5, 0.25), (3, 0.2)],
                                                  [0.6, 0.8, 1.0, 1.2, 1.5, 2.2, 3]), 0.2), 0.4, 3.0), t, 1) for t in (0, 1.6)]),
      ["campana", "iglesia", "church bell", "boda", "solemne"])
sound("viento-misterio", "Viento misterioso", "Eerie wind", S,
      lambda: d.reverb(d.stereo(d.sweep_filter(d.noise(5.0, "pink", R("vm")), 400 + 300 * np.sin(TAU * 0.3 * d.t_axis(5.0)) ** 2 + 200, 6.0)
                                * d.adsr(d.samples(5.0), 1.0, 0.2, 0.9, 1.0), 0.6), 0.4, 2.5), ["viento", "misterio", "terror", "noche", "fantasma"])


# ================================================================ Ritmo y música (20)

B = "ritmo"


def kick():
    return thump(140, 45, 0.45, 0.8, 1.6, "kk")


def snare(seed="sn"):
    n = d.samples(0.25)
    body = d.osc(d.glide(330, 180, 0.04).tolist() + [180] * (n - d.samples(0.04)), 0.25) * d.perc(n, 0.001, 0.12)
    nz = d.bandpass(d.noise(0.25, "white", R(seed)), 1500, 9000) * d.perc(n, 0.001, 0.22)
    return body * 0.6 + nz * 0.8


def clap(seed="cl"):
    r = R(seed)
    parts = []
    for k in range(4):
        n = d.samples(0.2 if k == 3 else 0.012)
        parts.append((d.bandpass(r.standard_normal(n), 900, 5000) * d.perc(n, 0.0005, n / SR), k * 0.01, 1))
    return d.reverb(d.place(parts), 0.2, 0.7)


def drumroll(sec=2.0, crash=False):
    r = R("roll")
    parts = []
    t = 0.0
    while t < sec:
        g = 0.3 + 0.7 * (t / sec) ** 1.5
        parts.append((d.pan(snare("dr" + str(int(t * 1000))) * g, r.uniform(-0.2, 0.2)), t, 0.6))
        t += 0.045 + r.uniform(-0.004, 0.004)
    if crash:
        parts += [(cymbal(2.0, "drc"), sec, 0.9), (kick(), sec, 0.8)]
    return d.reverb(d.place(parts), 0.2, 1.2)


sound("redoble", "Redoble", "Drumroll", B, lambda: drumroll(2.0), ["redoble", "drumroll", "tambor", "suspenso", "anuncio"])
sound("redoble-platillo", "Redoble con platillo", "Drumroll with crash", B, lambda: drumroll(2.2, True),
      ["redoble", "platillo", "anuncio", "revelacion", "ganador"])
sound("platillo", "Platillo", "Crash cymbal", B, lambda: cymbal(2.2, "cr"), ["platillo", "crash", "cymbal", "acento"])
sound("platillo-corto", "Platillo corto", "Short cymbal", B, lambda: cymbal(0.7, "cr2"), ["platillo", "corto", "acento"])
sound("gong", "Gong", "Gong", B,
      lambda: d.reverb(d.stereo(d.fm(np.full(d.samples(5.0), 110.0), 1.41, 4 * d.perc(d.samples(5.0), 0.01, 3.0), 5.0) * d.perc(d.samples(5.0), 0.01, 5.0)
                                + additive(110, 5.0, [(1, 0.6), (1.83, 0.4), (2.71, 0.3), (3.6, 0.2)], [0.8, 1.1, 1.5, 2]), 0.4), 0.35, 3.0),
      ["gong", "oriental", "inicio", "solemne", "meditacion"])
sound("bombo", "Bombo", "Kick drum", B, lambda: d.stereo(kick(), 0.0), ["bombo", "kick", "tambor", "beat"])
sound("caja", "Caja", "Snare drum", B, lambda: d.reverb(d.stereo(snare(), 0.2), 0.2, 0.8), ["caja", "snare", "tambor", "beat"])
sound("palmas", "Palmas", "Clap", B, lambda: clap(), ["palmas", "clap", "aplauso", "beat"])
sound("chasquido", "Chasquido de dedos", "Finger snap", B,
      lambda: d.reverb(d.stereo(d.bandpass(d.noise(0.04, "white", R("snp")), 1800, 7000) * d.perc(d.samples(0.04), 0.0003, 0.04)
                                + d.osc(1100, 0.04) * d.perc(d.samples(0.04), 0.0003, 0.02) * 0.3, 0.1), 0.2, 0.6),
      ["chasquido", "snap", "dedos", "magia", "cambio"])
sound("corneta-aire", "Corneta de aire", "Air horn", B,
      lambda: d.place([(air_horn(0.25), 0, 1), (air_horn(0.25), 0.3, 1), (air_horn(0.9), 0.6, 1)]),
      ["corneta", "air horn", "fiesta", "dj", "hype", "celebracion"])


def air_horn(sec):
    n = d.samples(sec)
    y = sum(d.osc(f * (1 + 0.002 * np.sin(TAU * 5 * d.t_axis(sec))), sec, "saw") for f in (466, 554, 698, 932))
    y = d.peak_eq(d.lowpass(y, 5000), 1800, 8, 1.2)
    return d.stereo(d.drive(y * 0.25 * d.adsr(n, 0.02, 0.05, 0.9, 0.05), 2.0), 0.3)


def scratch(sec=0.6, seed="sc"):
    t = d.t_axis(sec)
    speed = np.sin(TAU * 3.2 * t / sec * 2)
    src = d.noise(sec, "pink", R(seed))
    tone = d.osc(300 + 900 * np.abs(speed), sec, "saw") * 0.4
    y = d.bandpass(src * 0.5 + tone, 300, 4000) * np.abs(speed) ** 0.7
    return d.stereo(y * d.adsr(len(t), 0.005, 0.05, 0.9, 0.05), 0.1)


sound("scratch-dj", "Scratch de DJ", "DJ scratch", B, lambda: scratch(), ["scratch", "dj", "hip hop", "vinilo", "transicion"])
sound("scratch-doble", "Doble scratch", "Double scratch", B, lambda: d.place([(scratch(0.35, "sc2"), 0, 1), (scratch(0.35, "sc3"), 0.38, 1)]),
      ["scratch", "dj", "doble", "hip hop"])
sound("vinilo", "Crepitar de vinilo", "Vinyl crackle", B,
      lambda: d.stereo(d.lowpass(d.noise(4.0, "white", R("vn")) * (R("vn2").random(d.samples(4.0)) > 0.9985) * 4 + d.noise(4.0, "pink", R("vn3")) * 0.03, 6000), 0.4),
      ["vinilo", "vinyl", "crackle", "retro", "lofi", "nostalgia"])


def brass(notes, step=0.16, sec_last=0.9):
    parts = []
    t = 0
    for i, m in enumerate(notes):
        sec = sec_last if i == len(notes) - 1 else step * 0.95
        n = d.samples(sec)
        y = sum(d.osc(d.midi(m + o) * (1 + det), sec, "saw") * g for o, g in ((0, 1), (12, 0.3)) for det in (-0.003, 0.003))
        y = d.sweep_filter(y, 600 + 2500 * d.adsr(n, 0.05, 0.1, 0.7, 0.1), 1.3, kind="low") * d.adsr(n, 0.02, 0.05, 0.85, 0.08)
        parts.append((d.stereo(y * 0.3, 0.3), t, 1))
        t += step
    return d.reverb(d.place(parts), 0.3, 1.6)


sound("fanfarria", "Fanfarria", "Fanfare", B, lambda: brass([67, 72, 76, 79], 0.15, 1.1), ["fanfarria", "fanfare", "trompeta", "anuncio", "ganador"])
sound("fanfarria-victoria", "Fanfarria de victoria", "Victory fanfare", B,
      lambda: d.place([(brass([67, 67, 67, 72, 76, 79, 84], 0.13, 1.4), 0, 1), (cymbal(2.0, "fv"), 0.78, 0.4)]),
      ["victoria", "fanfarria", "ganador", "premio", "campeon"])
sound("campanas-boda", "Campanas de boda", "Wedding bells", B,
      lambda: chime_seq([76, 72, 74, 67, 67, 74, 76, 72], 0.32, 2.0, 0.8, 0.45), ["boda", "campanas", "wedding", "novios", "matrimonio"])
sound("drop-fill", "Remate de batería", "Drum fill", B,
      lambda: d.place([(tom(220), 0, 0.7), (tom(200), 0.1, 0.7), (tom(170), 0.2, 0.7), (tom(140), 0.3, 0.8), (snare("df"), 0.4, 0.8),
                       (kick(), 0.5, 1), (cymbal(1.6, "df2"), 0.5, 0.7)]), ["fill", "bateria", "drums", "drop", "transicion"])
sound("cuenta-palillos", "Cuenta con palillos", "Stick count-in", B,
      lambda: d.place([(d.stereo(additive(2400, 0.08, [(1, 1), (2.8, 0.4)], [60, 90]), 0.05), k * 0.5, 1) for k in range(4)]),
      ["cuenta", "1 2 3 4", "palillos", "sticks", "inicio", "count in"])
sound("maraca", "Maraca", "Shaker", B,
      lambda: d.place([(d.stereo(d.highpass(d.noise(0.09, "white", R("mk" + str(k))), 5000) * d.swell(d.samples(0.09), 0.3) * 0.6, 0.2), k * 0.25, 1 if k % 2 else 0.6)
                       for k in range(8)]), ["maraca", "shaker", "ritmo", "latino", "percusion"])


sound("caida-caricatura", "Caída de caricatura", "Cartoon fall", C,
      lambda: d.place([(SOUNDS["silbato-bajada"].make(), 0, 0.8), (SOUNDS["bonk"].make(), 0.85, 0.9), (thump(200, 60, 0.4, 0.8, 1.5, "cf"), 0.85, 0.8)]),
      ["caida", "fall", "caricatura", "golpe", "humor", "fail"])


def applause(sec=3.0, density=55, seed="ap"):
    r = R(seed)
    parts = []
    for k in range(int(density * sec)):
        t = r.uniform(0, sec)
        g = min(t / 0.4, 1) * min((sec - t) / 0.8, 1)
        parts.append((d.pan(clap(seed + str(k)), r.uniform(-0.9, 0.9)), t, 0.25 * g))
    return d.place(parts)


sound("aplausos", "Aplausos", "Applause", B, lambda: applause(), ["aplausos", "applause", "publico", "bravo", "felicitaciones"])
