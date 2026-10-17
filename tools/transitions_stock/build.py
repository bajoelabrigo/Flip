"""Builds the transitions of Stock › Transiciones and renders their cards with the app.

    py tools/transitions_stock/build.py [--only id,id] [--mod fam_glitch] [--no-render]

<out>/<id>/package/<pkg>/transition.json, main.frag, preview_strip.png   the transition (installed folder)
<out>/<id>/<id>.driftfx      what Stock downloads; the app installs it with AddonManager::installUserPackage
<out>/<id>/thumbnail.png     768 x 432 card: a moment of the transition, rendered by the app
<out>/<id>/preview.mp4       640 x 360, 2 s: photo A, the transition, photo B (rendered by the app)
<out>/<id>/meta.json
<out>/../catalogo-*.png      contact sheets of the cards

The app loads the packages straight from the staging folder through DRIFT_TRANSITIONS_DIR (searched
before the bundled and installed ones), so nothing is installed on this machine. Each card is also
compared with the same frame drawn by harness.py: a big difference means the app did not compile the
shader and fell back to a crossfade.
"""

from __future__ import annotations

import argparse
import importlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / "scene_templates"))

import designs  # noqa: E402
import driftfx  # noqa: E402
from kit import CATEGORIES, OUT, PAIRS, SAMPLES, package_id, param_defaults, shader  # noqa: E402
from scene import Box, cover, layout  # noqa: E402

W, H = 1280, 720
WORK = OUT.parent / "trabajo"
STAGE = WORK / "transitions"
PREVIEW_LEN = 2.0
STRIP_FRAMES = 12


def window(fam) -> tuple[float, float]:
    d = min(fam.duration, 1.6)
    return 1.0 - d / 2, 1.0 + d / 2


def write_package(fam, v, folder: Path) -> Path:
    pid = package_id(v)
    pkg = folder / "package" / pid
    if pkg.exists():
        shutil.rmtree(pkg)
    pkg.mkdir(parents=True)
    defaults = param_defaults(fam, v)
    params = [{"identifier": p.id, "displayName": p.en, "type": "float", "minValue": p.lo, "maxValue": p.hi,
               "defaultValue": round(float(defaults[p.id]), 4)} for p in fam.params]
    manifest = {
        "id": pid,
        "displayName": v.en,
        "names": {"es": v.es, "en": v.en},
        "category": fam.app_category,
        "order": 5000 + designs.ALL.index((fam, v)),
        "audioCurve": fam.audio,
        "parameters": params,
        "pipeline": {"intermediateBuffers": [], "passes": [{
            "passIndex": 0, "fragmentShader": "main.frag",
            "inputs": [{"type": "source_texture", "index": 0}, {"type": "source_texture", "index": 1}],
            "output": {"type": "canvas"}}]},
    }
    (pkg / "transition.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (pkg / "main.frag").write_text(shader(fam, v), encoding="utf-8")
    return pkg


def photo_clip(name: str, t0: float, dur: float) -> tuple[dict, dict]:
    path = SAMPLES / f"{name}.jpg"
    with Image.open(path) as im:
        pw, ph = im.size
    aid = f"a-{name}"
    asset = {"id": aid, "kind": "image", "name": path.name, "path": str(path), "width": pw, "height": ph}
    clip = {"id": f"c-{name}-{t0:g}", "type": "image", "assetId": aid, "path": str(path),
            "timelineStartUs": round(t0 * 1e6), "timelineDurationUs": round(dur * 1e6), "srcInUs": 0,
            "srcOutUs": round(dur * 1e6), "sourceFrame": cover(pw, ph, W, H), **layout(Box(0, 0, W, H), None)}
    return asset, clip


def project(fam, v, pair) -> dict:
    a_asset, a = photo_clip(pair[0], 0.0, 1.0)
    b_asset, b = photo_clip(pair[1], 1.0, 1.0)
    t0, t1 = window(fam)
    track = {"id": "t-video", "type": "video", "name": "Video", "clips": [a, b], "transitions": [{
        "id": "x1", "kind": package_id(v), "fromClipId": a["id"], "toClipId": b["id"],
        "durationUs": round((t1 - t0) * 1e6), "parameters": param_defaults(fam, v)}]}
    return {"version": 14, "projectName": v.es, "width": W, "height": H, "fps": 30, "sampleRate": 48000,
            "background": {"kind": "color", "color": "#ff000000"}, "assets": [a_asset, b_asset], "tracks": [track]}


def pair_for(fam) -> tuple[str, str]:
    return PAIRS[designs.FAMILIES.index(fam) % len(PAIRS)]


def strip(preview: Path, fam, target: Path) -> None:
    """12 square frames across the transition, from the app's own preview video."""
    t0, t1 = window(fam)
    cells = []
    for i in range(STRIP_FRAMES):
        t = t0 + (t1 - t0) * i / (STRIP_FRAMES - 1)
        t = min(max(t, 0.0), PREVIEW_LEN - 0.04)
        out = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(preview), "-frames:v", "1",
                              "-vf", "crop=ih:ih,scale=128:128", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True, check=True).stdout
        cells.append(Image.frombytes("RGB", (128, 128), out[:128 * 128 * 3]))
    sheet = Image.new("RGB", (128 * STRIP_FRAMES, 128))
    for i, c in enumerate(cells):
        sheet.paste(c, (i * 128, 0))
    sheet.save(target, optimize=True)


def meta(fam, v) -> dict:
    return {"id": v.id, "package": package_id(v), "names": {"es": v.es, "en": v.en}, "category": fam.category,
            "categoryNames": CATEGORIES[fam.category], "family": fam.key, "durationSec": round(window(fam)[1] - window(fam)[0], 3),
            "tags": sorted(set(fam.tags + v.tags + ["transicion", "transition"])), "width": 768, "height": 432}


def package_meta(v) -> dict:
    return {"id": package_id(v), "name": v.en, "version": "1.0.0", "author": "Flip Studio",
            "description": v.es, "details": "", "license": "Flip Studio Stock", "minAppVersion": "0.13.0",
            "generator": "flip-stock"}


def reference(fam, v, renderer, at: float) -> Image.Image:
    prog = renderer.compile(shader(fam, v))
    frame = renderer.frames(prog, param_defaults(fam, v), pair_for(fam), [at])[0]
    prog.release()
    return frame


def diff(a: Image.Image, b: Image.Image) -> float:
    x = np.asarray(a.convert("RGB").resize((160, 90)), np.float32)
    y = np.asarray(b.convert("RGB").resize((160, 90)), np.float32)
    return float(np.abs(x - y).mean())


def contact_sheets() -> None:
    cards = [OUT / v.id for _, v in designs.ALL if (OUT / v.id / "thumbnail.png").exists()]
    per, cols, tw, th = 48, 6, 320, 180
    for page in range(0, len(cards), per):
        chunk = cards[page:page + per]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (22, 22, 26))
        d = ImageDraw.Draw(sheet)
        for i, c in enumerate(chunk):
            x, y = (i % cols) * tw, (i // cols) * (th + 18)
            sheet.paste(Image.open(c / "thumbnail.png").convert("RGB").resize((tw, th)), (x, y))
            d.text((x + 4, y + th + 3), c.name, fill=(225, 225, 225))
        sheet.save(OUT.parent / f"catalogo-{page // per + 1}.png")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--mod", default="")
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()
    only = {s for s in args.only.split(",") if s}
    keys = {f.key for f in importlib.import_module(args.mod).FAMILIES} if args.mod else set()
    jobs = [(f, v) for f, v in designs.ALL if (not only or v.id in only) and (not keys or f.key in keys)]
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    for fam, v in jobs:
        folder = OUT / v.id
        folder.mkdir(parents=True, exist_ok=True)
        pkg = write_package(fam, v, folder)
        shutil.copytree(pkg, STAGE / pkg.name)
        (WORK / "projects").mkdir(parents=True, exist_ok=True)
        (WORK / "projects" / f"{v.id}.json").write_text(json.dumps(project(fam, v, pair_for(fam)), ensure_ascii=False),
                                                       encoding="utf-8")
        (folder / "meta.json").write_text(json.dumps(meta(fam, v), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(jobs)} packages staged in {STAGE}", flush=True)

    if not args.no_render:
        import appsession
        from harness import Renderer
        renderer = Renderer((256, 144))
        suspicious = []
        with appsession.session(WORK, env={"DRIFT_TRANSITIONS_DIR": str(STAGE)}) as app:
            for fam, v in jobs:
                folder = OUT / v.id
                if not app.load(WORK / "projects" / f"{v.id}.json"):
                    continue
                t0, t1 = window(fam)
                frame = WORK / f"{v.id}.png"
                if app.capture(t0 + (t1 - t0) * v.thumb, frame):
                    with Image.open(frame) as im:
                        card = im.convert("RGB").resize((768, 432), Image.LANCZOS)
                    card.save(folder / "thumbnail.png", optimize=True)
                    frame.unlink()
                    score = diff(card, reference(fam, v, renderer, v.thumb))
                    if score > 22:
                        suspicious.append((v.id, round(score, 1)))
                if app.export(folder / "preview.mp4", 0.0, PREVIEW_LEN, 360):
                    strip(folder / "preview.mp4", fam, folder / "package" / package_id(v) / "preview_strip.png")
                else:
                    print(f"  {v.id}: export failed", flush=True)
                print(f"rendered {v.id}", flush=True)
        if suspicious:
            print("cards that differ from the offline render (shader not compiled in the app?):", suspicious)

    for fam, v in jobs:
        folder = OUT / v.id
        target = folder / f"{v.id}.driftfx"
        driftfx.write(folder / "package" / package_id(v), "transitions", package_meta(v), target)
        driftfx.check(target)
    contact_sheets()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
