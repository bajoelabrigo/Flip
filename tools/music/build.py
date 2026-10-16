"""Cuts, levels and packages the songs of Stock › Música.

    py tools/music/build.py [--only id,id] [--jobs 12]

For every item of catalog.ITEMS (a song + a length of 15, 30 or 60 s):
<out>/<id>/<id>.mp3        44.1 kHz stereo MP3 192 kb/s, about -14 LUFS, peaks under -1 dBTP (what Stock downloads)
<out>/<id>/preview.mp3     the same cut at 128 kb/s for the player in the Stock detail
<out>/<id>/thumbnail.png   384 x 384 card: the waveform on the mood colour, with the length
<out>/<id>/meta.json       names, category, tags, duration, bpm, source and licence
<out>/../informe.tsv       per cut: where it was cut, loudness, true peak, longest quiet stretch, how the end decays
<out>/../CREDITS.json      every song used: title, artist, page, file URL, licence
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import wave
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import catalog  # noqa: E402
import cuts  # noqa: E402
import dsp  # noqa: E402
from fetch import ROOT, SRC, load_sources  # noqa: E402
from survey import analysis  # noqa: E402

OUT = ROOT / "paquetes"
CARD = 384
TARGET_LUFS = -14.0
CEILING_DB = -1.5        # sample peak after the limiter (2x oversampled); the MP3 then stays under -1 dBTP
MAX_LIMIT_DB = 4.0       # never squash more than this to reach the target
FONT = "C:/Windows/Fonts/segoeuib.ttf"


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def card(y: np.ndarray, category: str, seconds: float, path: Path):
    a, b = catalog.COLORS[category]
    yy, xx = np.mgrid[0:CARD, 0:CARD].astype(np.float32) / CARD
    t = np.clip((xx * 0.6 + yy * 0.4), 0, 1)[..., None]
    bg = hex_rgb(a) * (1 - t) + hex_rgb(b) * t
    im = Image.fromarray(bg.astype(np.uint8), "RGB")
    mono = np.abs(y).max(axis=1)
    bars = 40
    chunks = np.array_split(mono, bars)
    level = np.array([np.sqrt((c.astype(np.float64) ** 2).mean()) if len(c) else 0 for c in chunks])
    ldb = 20 * np.log10(level + 1e-9)
    level = np.clip((ldb - (ldb.max() - 18)) / 18, 0, 1) ** 1.3
    over = Image.new("L", (CARD, CARD), 0)
    d = ImageDraw.Draw(over)
    pad, mid = 36, CARD * 0.47
    step = (CARD - 2 * pad) / bars
    for i, v in enumerate(level):
        h = max(v * (CARD * 0.26), 3)
        x0 = pad + i * step + step * 0.2
        d.rounded_rectangle([x0, mid - h, x0 + step * 0.6, mid + h], radius=int(step * 0.3), fill=255)
    glow = over.filter(ImageFilter.GaussianBlur(7))
    white = Image.new("RGB", im.size, (255, 255, 255))
    im = Image.composite(white, im, Image.eval(glow, lambda v: v // 3))
    im = Image.composite(white, im, over)
    # length pill, bottom left
    d = ImageDraw.Draw(im, "RGBA")
    f = ImageFont.truetype(FONT, 30)
    label = f"{int(round(seconds))} s"
    w = d.textlength(label, font=f)
    d.rounded_rectangle([24, CARD - 70, 24 + w + 32, CARD - 24], radius=23, fill=(0, 0, 0, 105))
    d.text((40, CARD - 47), label, font=f, fill=(255, 255, 255, 255), anchor="lm")
    # note glyph, bottom right
    nx, ny = CARD - 52, CARD - 47
    d.ellipse([nx - 13, ny + 2, nx + 3, ny + 15], fill=(255, 255, 255, 235))
    d.rectangle([nx, ny - 26, nx + 3, ny + 9], fill=(255, 255, 255, 235))
    d.polygon([(nx + 3, ny - 26), (nx + 17, ny - 18), (nx + 17, ny - 11), (nx + 3, ny - 18)], fill=(255, 255, 255, 235))
    im.save(path, optimize=True)


def write_wav(path: Path, y: np.ndarray):
    pcm = (np.clip(y, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(dsp.SR)
        w.writeframes(pcm.tobytes())


def level(y: np.ndarray) -> tuple[np.ndarray, float, float]:
    """Gain to TARGET_LUFS and limit the peaks; backs off the gain if the limiter would work too hard."""
    l0 = dsp.lufs(y)
    gain = TARGET_LUFS - l0
    for _ in range(6):
        z, gr = dsp.limit(y * 10 ** (gain / 20), CEILING_DB)
        if gr <= MAX_LIMIT_DB:
            break
        gain -= gr - MAX_LIMIT_DB + 0.3
    return z, gain, gr


def quiet_stretch(y: np.ndarray, until: int) -> float:
    """Longest run (s) under -45 dBFS before sample `until` (the fade-out is not counted)."""
    k = dsp.SR // 20
    seg = y[:until]
    n = len(seg) // k
    if n == 0:
        return 0.0
    rms = 10 * np.log10((seg[:n * k].astype(np.float64) ** 2).reshape(n, k, 2).mean(axis=(1, 2)) + 1e-12)
    best = run = 0
    for v in rms:
        run = run + 1 if v < -45 else 0
        best = max(best, run)
    return best * k / dsp.SR


def tail_drop(y: np.ndarray) -> float:
    """dB between the body of the cut and its last 0.3 s: how much the end decays."""
    k = int(0.3 * dsp.SR)
    body = 10 * np.log10((y[: -2 * k].astype(np.float64) ** 2).mean() + 1e-12)
    last = 10 * np.log10((y[-k:].astype(np.float64) ** 2).mean() + 1e-12)
    return body - last


def build(item: catalog.Item, x: np.ndarray, avoid: list) -> tuple[dict, tuple[float, float]]:
    src = SOURCES[item.key]
    a = analysis(item.key, item.meter, src.get("bpmHint"))
    c = cuts.choose(a, item.length, avoid=avoid, prefer_intro=item.prefer_intro, min_start=item.start)
    y = cuts.render(x, c)
    y, gain, gr = level(y)
    folder = OUT / item.id
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "cut.wav"
        write_wav(wav, y)
        for name, rate in ((f"{item.id}.mp3", "192k"), ("preview.mp3", "128k")):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-c:a", "libmp3lame", "-b:a", rate,
                            "-map_metadata", "-1", "-id3v2_version", "0", "-write_xing", "1", str(folder / name)],
                           check=True)
    z = dsp.decode(folder / f"{item.id}.mp3")
    final_lufs, tp = dsp.lufs(z), dsp.true_peak_db(z)
    seconds = len(y) / dsp.SR
    card(y, item.category, seconds, folder / "thumbnail.png")
    fade_at = int((c.fade_from - c.start) * dsp.SR)
    meta = {
        "id": item.id, "names": item.names, "category": item.category,
        "tags": item.tags + [w for w in catalog.tempo_tags(a.bpm) if w not in item.tags],
        "durationSec": round(seconds, 3), "bpm": round(a.bpm), "length": item.length,
        "song": src["title"], "artist": src["artist"], "source": src["source"], "page": src["page"],
        "license": src["license"], "licenseUrl": src["licenseUrl"],
        "cut": {"start": round(c.start, 3), "end": round(c.end, 3), "fadeFrom": round(c.fade_from, 3),
                "kind": c.kind, "bars": c.bars},
    }
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"id": item.id, "category": item.category, "song": src["title"], "length": item.length,
            "dur": round(seconds, 2), "kind": c.kind, "bars": c.bars, "start": round(c.start, 2),
            "bpm": round(a.bpm), "pulse": round(a.pulse, 2), "gain": round(gain, 1), "limit": round(gr, 1),
            "lufs": round(final_lufs, 1), "tp": round(tp, 1), "quiet": round(quiet_stretch(y, max(fade_at, 1)), 2),
            "drop": round(tail_drop(y), 1), "score": round(c.score, 2)}, (c.start, c.end)


def build_song(items: list) -> list[dict]:
    """All the cuts of one song, in catalogue order; later cuts avoid the parts the earlier ones used."""
    out, avoid = [], []
    try:
        x = dsp.decode(SRC / items[0].key)
    except Exception as e:
        return [{"id": i.id, "error": repr(e)} for i in items]
    for item in items:
        try:
            r, window = build(item, x, avoid)
            avoid.append(window)
            out.append(r)
        except Exception as e:  # keep going; the report shows it
            out.append({"id": item.id, "error": repr(e)})
    return out


SOURCES = load_sources()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=12)
    args = ap.parse_args()
    only = {i for i in args.only.split(",") if i}
    items = [i for i in catalog.ITEMS if not only or i.id in only]
    groups: dict[str, list] = {}
    for i in items:
        groups.setdefault(i.key, []).append(i)
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with Pool(max(1, min(args.jobs, len(groups)))) as pool:
        for rs in pool.imap_unordered(build_song, list(groups.values())):
            for r in rs:
                print(json.dumps(r, ensure_ascii=False), flush=True)
                rows.append(r)
    report = ROOT / "informe.jsonl"
    old = {}
    if only and report.exists():
        old = {r["id"]: r for r in map(json.loads, report.read_text(encoding="utf-8").splitlines() if report.exists() else [])}
    old.update({r["id"]: r for r in rows})
    keep = {i.id for i in catalog.ITEMS}
    lines = [json.dumps(old[k], ensure_ascii=False) for k in sorted(old) if k in keep]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    used = sorted({i.key for i in catalog.ITEMS})
    credits = [{k: SOURCES[u].get(k) for k in ("title", "artist", "album", "source", "page", "file", "license",
                                                "licenseUrl", "licenseProof", "checked")} for u in used]
    (ROOT / "CREDITS.json").write_text(json.dumps(credits, ensure_ascii=False, indent=1), encoding="utf-8")
    bad = [r for r in rows if "error" in r]
    print(f"{len(rows) - len(bad)} built, {len(bad)} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
