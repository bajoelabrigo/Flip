"""Analyses every downloaded song once (beats, bars, sections, loudness) and writes a table to choose from.

    py tools/music/survey.py [--jobs 12]

<ROOT>/analisis/<slug>-m<meter>.npz   cached analysis, reused by build.py
<ROOT>/analisis/survey.tsv            one line per song: duration, bpm, pulse clarity, loudness, brightness...
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import dsp  # noqa: E402
from fetch import ROOT, SRC, load_sources  # noqa: E402

CACHE = ROOT / "analisis"


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "x"


def cache_path(key: str, meter: int) -> Path:
    return CACHE / f"{slug(key)}-m{meter}.npz"


def analysis(key: str, meter: int = 4, hint: float | None = None) -> dsp.Analysis:
    p = cache_path(key, meter)
    if p.exists():
        z = np.load(p)
        return dsp.Analysis(dur=float(z["dur"]), bpm=float(z["bpm"]), beats=z["beats"], downbeats=z["downbeats"],
                            meter=int(z["meter"]), pulse=float(z["pulse"]), accent=z["accent"],
                            bar_rms_db=z["bar_rms_db"], novelty=z["novelty"], start=float(z["start"]),
                            end=float(z["end"]), frame_db=z["frame_db"], logspec=None)
    x = dsp.decode(SRC / key)
    a = dsp.analyse(x, hint, meter)
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(p, dur=a.dur, bpm=a.bpm, beats=a.beats, downbeats=a.downbeats, meter=a.meter, pulse=a.pulse,
                        accent=a.accent, bar_rms_db=a.bar_rms_db, novelty=a.novelty, start=a.start, end=a.end,
                        frame_db=a.frame_db.astype(np.float32))
    feats = {"lufs": dsp.lufs(x)}
    ls = a.logspec
    w = 10 ** ls
    feats["centroid"] = float(np.exp((np.log(dsp.BAND_HZ)[None, :] * w).sum(1) / (w.sum(1) + 1e-12)).mean())
    feats["bass"] = float((w[:, dsp.BAND_HZ < 160].sum(1) / (w.sum(1) + 1e-12)).mean())
    p.with_suffix(".json").write_text(json.dumps(feats), encoding="utf-8")
    return a


def row(s: dict) -> str:
    try:
        a = analysis(s["key"], 4, s.get("bpmHint"))
    except Exception as e:  # keep going
        return f"{s['key']}\tFAILED {e!r}"
    f = json.loads(cache_path(s["key"], 4).with_suffix(".json").read_text())
    bars = a.bar_rms_db
    dr = float(np.percentile(bars, 90) - np.percentile(bars, 10)) if len(bars) > 3 else 0
    return "\t".join([s["key"], s.get("albumSlug") or s.get("folder", ""), s["title"], f"{a.dur:.0f}", f"{a.bpm:.0f}",
                      f"{a.pulse:.2f}", f"{f['lufs']:.1f}", f"{f['centroid']:.0f}", f"{f['bass']:.2f}", f"{dr:.1f}",
                      ",".join(s.get("genres", []))])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=12)
    a = ap.parse_args()
    songs = list(load_sources().values())
    with Pool(a.jobs) as pool:
        lines = sorted(pool.imap_unordered(row, songs, chunksize=2))
    head = "key\talbum\ttitle\tdur\tbpm\tpulse\tlufs\tcentroid\tbass\tdyn\tgenres"
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / "survey.tsv").write_text(head + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    print(len(lines), "songs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
