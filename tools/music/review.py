"""Contact sheets to review the cuts without listening: spectrogram + level curve of every MP3.

    py tools/music/review.py [--per 24]

<ROOT>/revision/hoja-NN.png   per cut: spectrogram (top), RMS level in dB (-60..0, white) with the -14 dB line,
                              where the fade-out starts (yellow), and the numbers from informe.jsonl
<ROOT>/revision/tarjetas.png  every thumbnail, small
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import catalog  # noqa: E402
import dsp  # noqa: E402
from fetch import ROOT  # noqa: E402

PKG = ROOT / "paquetes"
OUTDIR = ROOT / "revision"
W, H = 620, 210
FONT = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
FONTB = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)


def tile(meta: dict, rep: dict) -> Image.Image:
    y = dsp.decode(PKG / meta["id"] / f"{meta['id']}.mp3")
    mono = y.mean(axis=1)
    ls, db = dsp.spectrogram(mono)
    im = Image.new("RGB", (W, H), (18, 18, 22))
    d = ImageDraw.Draw(im)
    a, b = catalog.COLORS[meta["category"]]
    d.rectangle([0, 0, 6, H], fill=a)
    # spectrogram 0..110 px
    sp = ls.T[::-1]
    sp = np.clip((sp - (sp.max() - 7)) / 7, 0, 1)
    spi = Image.fromarray((sp * 255).astype(np.uint8), "L").resize((W - 20, 90))
    im.paste(Image.merge("RGB", (spi, spi.point(lambda v: v * 0.7), spi.point(lambda v: 255 - v // 2 if v else 40))),
             (14, 30))
    # level curve
    top, hgt = 125, 80
    k = max(1, len(db) // (W - 20))
    lv = db[: len(db) // k * k].reshape(-1, k).max(axis=1)
    pts = [(14 + i * (W - 20) / len(lv), top + hgt * (-np.clip(v, -60, 0) / 60)) for i, v in enumerate(lv)]
    d.line([(14, top + hgt * 14 / 60), (W - 6, top + hgt * 14 / 60)], fill=(90, 90, 90))
    d.line([(14, top + hgt), (W - 6, top + hgt)], fill=(60, 60, 60))
    d.line(pts, fill=(240, 240, 240), width=1)
    cut = meta["cut"]
    dur = meta["durationSec"]
    fx = 14 + (cut["fadeFrom"] - cut["start"]) / dur * (W - 20)
    if cut["fadeFrom"] < cut["end"] - 0.1:
        d.line([(fx, 30), (fx, top + hgt)], fill=(255, 210, 0), width=2)
    for s in range(0, int(dur) + 1, 5):
        x = 14 + s / dur * (W - 20)
        d.line([(x, top + hgt), (x, top + hgt + 4)], fill=(120, 120, 120))
    d.text((14, 4), meta["id"], font=FONTB, fill=(255, 255, 255))
    info = (f"{dur:.1f}s  {rep.get('kind', '')} {rep.get('bars', '')}b  bpm {rep.get('bpm', '')}  "
            f"LUFS {rep.get('lufs', '')}  TP {rep.get('tp', '')}  lim {rep.get('limit', '')}  "
            f"quiet {rep.get('quiet', '')}  drop {rep.get('drop', '')}")
    d.text((14, 17), info, font=FONT, fill=(190, 190, 190))
    return im


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per", type=int, default=24)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for old in OUTDIR.glob("hoja-*.png"):
        old.unlink()
    rep = {}
    if (ROOT / "informe.jsonl").exists():
        rep = {r["id"]: r for r in map(json.loads, (ROOT / "informe.jsonl").read_text(encoding="utf-8").splitlines())}
    order = {c: i for i, c in enumerate(catalog.CATEGORIES)}
    metas = [json.loads((p / "meta.json").read_text(encoding="utf-8")) for p in PKG.iterdir() if (p / "meta.json").exists()]
    if a.only:
        want = set(a.only.split(","))
        metas = [m for m in metas if m["id"] in want]
    metas.sort(key=lambda m: (order.get(m["category"], 99), m["id"]))
    cols = 2
    for n in range(0, len(metas), a.per):
        chunk = metas[n:n + a.per]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * W, rows * H), (0, 0, 0))
        for i, m in enumerate(chunk):
            sheet.paste(tile(m, rep.get(m["id"], {})), ((i % cols) * W, (i // cols) * H))
        sheet.save(OUTDIR / f"hoja-{n // a.per + 1:02d}.png")
    # thumbnails
    th = 96
    cols = 16
    rows = (len(metas) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * th, max(1, rows) * th), (0, 0, 0))
    for i, m in enumerate(metas):
        sheet.paste(Image.open(PKG / m["id"] / "thumbnail.png").resize((th, th)), ((i % cols) * th, (i // cols) * th))
    sheet.save(OUTDIR / "tarjetas.png")
    print(len(metas), "cuts ->", OUTDIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
