"""Renders the sound effects of Stock › Sonidos.

    py tools/sounds/build.py [--only id,id] [--jobs 8]

<out>/<id>/<id>.wav        48 kHz stereo 16-bit (what Stock downloads)
<out>/<id>/preview.mp3     for the player in the Stock detail
<out>/<id>/thumbnail.png   384 x 384 card: the waveform on the category colour
<out>/<id>/meta.json       names, category, tags, duration
<out>/../informe.txt       duration, peak, RMS and spectral centroid of every sound, for review
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import wave
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import designs  # noqa: E402
import dsp  # noqa: E402

OUT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda" / "sonidos" / "paquetes"
CARD = 384

COLORS = {
    "transiciones": ("#2f6bff", "#7b2bff"),
    "impactos": ("#c41e00", "#3a0500"),
    "interfaz": ("#0ea5a5", "#0b4f6c"),
    "juegos": ("#ffb000", "#e0338f"),
    "magia": ("#b35cff", "#2fd8ff"),
    "comedia": ("#ff8c42", "#ffd23f"),
    "suspenso": ("#1b1f3a", "#5a1f6b"),
    "ritmo": ("#2fa84f", "#0b6c4f"),
}


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def card(x: np.ndarray, category: str, path: Path):
    a, b = COLORS[category]
    yy, xx = np.mgrid[0:CARD, 0:CARD].astype(np.float32) / CARD
    t = np.clip((xx + yy) / 2, 0, 1)[..., None]
    bg = hex_rgb(a) * (1 - t) + hex_rgb(b) * t
    im = Image.fromarray(bg.astype(np.uint8), "RGB")
    mono = np.abs(x).max(axis=1)
    bars = 48
    chunks = np.array_split(mono, bars)
    level = np.array([c.max() if len(c) else 0 for c in chunks])
    level = np.sqrt(level / (level.max() + 1e-9))
    over = Image.new("L", (CARD, CARD), 0)
    d = ImageDraw.Draw(over)
    pad, mid = 34, CARD / 2
    step = (CARD - 2 * pad) / bars
    for i, v in enumerate(level):
        h = max(v * (CARD * 0.32), 3)
        x0 = pad + i * step + step * 0.18
        d.rounded_rectangle([x0, mid - h, x0 + step * 0.64, mid + h], radius=int(step * 0.32), fill=255)
    glow = over.filter(ImageFilter.GaussianBlur(6))
    im = Image.composite(Image.new("RGB", im.size, (255, 255, 255)), im, Image.eval(glow, lambda v: v // 3))
    im = Image.composite(Image.new("RGB", im.size, (255, 255, 255)), im, over)
    im.save(path, optimize=True)


def write_wav(path: Path, x: np.ndarray):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(dsp.SR)
        w.writeframes(pcm.tobytes())


def stats(x: np.ndarray) -> dict:
    mono = x.mean(axis=1)
    spec = np.abs(np.fft.rfft(mono[: dsp.SR * 4]))
    freqs = np.fft.rfftfreq(min(len(mono), dsp.SR * 4), 1 / dsp.SR)
    centroid = float((spec * freqs).sum() / (spec.sum() + 1e-9))
    rms = float(np.sqrt((x ** 2).mean()))
    return {"dur": len(x) / dsp.SR, "peak_db": 20 * np.log10(np.abs(x).max() + 1e-9), "rms_db": 20 * np.log10(rms + 1e-9),
            "centroid": centroid}


def build(sid: str) -> str:
    s = designs.SOUNDS[sid]
    try:
        x = dsp.finish(s.make())
    except Exception as e:  # keep going
        return f"{sid}: FAILED {e!r}"
    folder = OUT / sid
    folder.mkdir(parents=True, exist_ok=True)
    wav = folder / f"{sid}.wav"
    write_wav(wav, x)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libmp3lame", "-b:a", "160k",
                    str(folder / "preview.mp3")], check=True)
    card(x, s.category, folder / "thumbnail.png")
    st = stats(x)
    meta = {"id": sid, "names": s.names, "category": s.category, "tags": s.tags, "durationSec": round(st["dur"], 3)}
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return (f"{sid}\t{s.category}\t{st['dur']:.2f}s\tpeak {st['peak_db']:.1f}\trms {st['rms_db']:.1f}\t"
            f"centroid {st['centroid']:.0f} Hz\t{wav.stat().st_size / 1e3:.0f} kB")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=8)
    args = ap.parse_args()
    ids = [i for i in args.only.split(",") if i] or list(designs.SOUNDS)
    OUT.mkdir(parents=True, exist_ok=True)
    lines = []
    with Pool(min(args.jobs, len(ids))) as pool:
        for line in pool.imap_unordered(build, ids):
            print(line, flush=True)
            lines.append(line)
    if not args.only:
        (OUT.parent / "informe.txt").write_text("\n".join(sorted(lines)), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
