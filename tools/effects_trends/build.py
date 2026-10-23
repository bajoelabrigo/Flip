"""Builds the effects of Efectos › Tendencias (Stock type «effect») and renders their cards with the app.

    py tools/effects_trends/build.py [--only id,id] [--mod fx_glitch] [--no-render]

<out>/<id>/package/<pkg>/effect.json, main.frag, thumbnail.png   the effect (installed folder)
<out>/<id>/<id>.driftfx      what Stock downloads; the app installs it with AddonManager::installUserPackage
<out>/<id>/thumbnail.png     768 x 432 card: a moment of the effect on its photo, rendered by the app
<out>/<id>/preview.mp4       640 x 360 hover video (the effect playing over its photo, rendered by the app)
<out>/<id>/meta.json
<out>/../catalogo-*.png      contact sheets of the cards

The app loads the packages straight from the staging folder through DRIFT_EFFECTS_DIR (searched before the
bundled and installed ones), so nothing is installed on this machine. Each card is compared with the same
frame drawn by harness.py: a big difference means the app did not compile the shader (it skips it silently).
"""

from __future__ import annotations

import argparse
import importlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / "transitions_stock"))
sys.path.append(str(HERE.parent / "scene_templates"))

import designs  # noqa: E402
import driftfx  # noqa: E402  (tools/transitions_stock)
from kit import CATEGORIES, OUT, ROOT, SAMPLES, package_id, param_defaults, photo_for, shader  # noqa: E402
from scene import Box, cover, layout  # noqa: E402

W, H = 1280, 720
WORK = OUT.parent / "trabajo"
STAGE = WORK / "effects"
EXE = ROOT.parent / "pruebas" / "FlipStudio-0.20.1-release" / "Flip Studio" / "flipstudio.exe"
MIN_APP = "0.21.0"


def manifest(fam, v, hidden=()) -> dict:
    """hidden: parameters that change nothing in this variant (harness.unused_params). They still reach the
    shader, as fixedParams, but the effect panel only shows controls that do something."""
    defaults = param_defaults(fam, v)
    params = []
    fixed = {}
    for p in fam.params:
        if p.id in hidden:
            fixed[p.id] = defaults[p.id] if p.is_color else round(float(defaults[p.id]), 4)
            continue
        if p.is_color:
            params.append({"identifier": p.id, "displayName": p.en, "type": "color", "defaultValue": defaults[p.id]})
        else:
            params.append({"identifier": p.id, "displayName": p.en, "type": "float", "minValue": p.lo,
                           "maxValue": p.hi, "defaultValue": round(float(defaults[p.id]), 4)})
    out = {
        "id": package_id(v),
        "displayName": v.en,
        "names": {"es": v.es, "en": v.en},
        "category": "trending",
        "stockCategory": fam.category,
        "stockId": v.id,
        "order": 9000 + designs.ALL.index((fam, v)),
        "parameters": params,
        "backend": "gpu",
        "pipeline": {"intermediateBuffers": [], "passes": [{
            "passIndex": 0, "fragmentShader": "main.frag",
            "inputs": [{"type": "source_texture"}], "output": {"type": "canvas"}}]},
    }
    if fixed:
        out["fixedParams"] = fixed
    if fam.requires:
        out["requires"] = fam.requires
    names = I18N.get(v.id)
    if names:
        out["names"].update(names)
    return out


def load_i18n() -> dict:
    """tools/stock_i18n/<lang>.json carry the names in the other languages, keyed flip:effect:<id>."""
    out: dict[str, dict] = {}
    folder = HERE.parent / "stock_i18n"
    for f in folder.glob("*.json"):
        lang = f.stem
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        items = data.get("items", data) if isinstance(data, dict) else {}
        for key, entry in items.items():
            if not key.startswith("flip:effect:"):
                continue
            name = entry.get("name") if isinstance(entry, dict) else entry
            if isinstance(name, str) and name:
                out.setdefault(key[len("flip:effect:"):], {})[lang] = name
    return out


I18N = load_i18n()


def write_package(fam, v, folder: Path, hidden=()) -> Path:
    pid = package_id(v)
    pkg = folder / "package" / pid
    if pkg.exists():
        shutil.rmtree(pkg)
    pkg.mkdir(parents=True)
    (pkg / "effect.json").write_text(json.dumps(manifest(fam, v, hidden), ensure_ascii=False, indent=2), encoding="utf-8")
    (pkg / "main.frag").write_text(shader(fam, v), encoding="utf-8")
    return pkg


def project(fam, v) -> dict:
    name = photo_for(fam, v)
    path = SAMPLES / f"{name}.jpg"
    with Image.open(path) as im:
        pw, ph = im.size
    aid = f"a-{name}"
    asset = {"id": aid, "kind": "image", "name": path.name, "path": str(path), "width": pw, "height": ph}
    dur = fam.preview
    clip = {"id": "c-photo", "type": "image", "assetId": aid, "path": str(path),
            "timelineStartUs": 0, "timelineDurationUs": round(dur * 1e6), "srcInUs": 0, "srcOutUs": round(dur * 1e6),
            "sourceFrame": cover(pw, ph, W, H), **layout(Box(0, 0, W, H), None),
            "effects": [{"name": "gpu", "catalogId": package_id(v), "parameters": param_defaults(fam, v)}]}
    return {"version": 14, "projectName": v.es, "width": W, "height": H, "fps": 30, "sampleRate": 48000,
            "background": {"kind": "color", "color": "#ff000000"}, "assets": [asset],
            "tracks": [{"id": "t-video", "type": "video", "name": "Video", "clips": [clip], "transitions": []}]}


def meta(fam, v) -> dict:
    extra = {"description": v.note} if v.note else {}
    return {**extra, "id": v.id, "package": package_id(v), "names": {"es": v.es, "en": v.en}, "category": fam.category,
            "categoryNames": CATEGORIES[fam.category], "family": fam.key, "photo": photo_for(fam, v),
            "requires": fam.requires, "durationSec": fam.preview,
            "tags": sorted(set(fam.tags + v.tags + ["efecto", "effect", "tendencia", "trending"])),
            "width": 768, "height": 432}


def package_meta(v) -> dict:
    return {"id": package_id(v), "name": v.en, "version": "1.0.0", "author": "Flip Studio",
            "description": v.es, "details": v.note.get("es", ""), "license": "Flip Studio Stock",
            "minAppVersion": MIN_APP, "generator": "flip-stock"}


def diff(a: Image.Image, b: Image.Image) -> float:
    x = np.asarray(a.convert("RGB").resize((160, 90)), np.float32)
    y = np.asarray(b.convert("RGB").resize((160, 90)), np.float32)
    return float(np.abs(x - y).mean())


def contact_sheets() -> None:
    cards = [(OUT / v.id, v.es) for _, v in designs.ALL if (OUT / v.id / "thumbnail.png").exists()]
    per, cols, tw, th = 48, 6, 320, 180
    for page in range(0, len(cards), per):
        chunk = cards[page:page + per]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (22, 22, 26))
        d = ImageDraw.Draw(sheet)
        for i, (c, label) in enumerate(chunk):
            x, y = (i % cols) * tw, (i // cols) * (th + 18)
            sheet.paste(Image.open(c / "thumbnail.png").convert("RGB").resize((tw, th)), (x, y))
            d.text((x + 4, y + th + 3), f"{c.name} · {label}", fill=(225, 225, 225))
        sheet.save(OUT.parent / f"catalogo-{page // per + 1}.png")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--mod", default="")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--no-preview", action="store_true", help="only the cards (faster, for reviewing)")
    args = ap.parse_args()
    only = {s for s in args.only.split(",") if s}
    keys = {f.key for f in importlib.import_module(args.mod).FAMILIES} if args.mod else set()
    jobs = [(f, v) for f, v in designs.ALL if (not only or v.id in only) and (not keys or f.key in keys)]
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)
    (WORK / "projects").mkdir(parents=True, exist_ok=True)
    from harness import Renderer as _Probe, unused_params
    probe = _Probe((192, 108))
    for fam, v in jobs:
        folder = OUT / v.id
        folder.mkdir(parents=True, exist_ok=True)
        hidden = set(v.hide) | set(unused_params(probe, fam, v))
        pkg = write_package(fam, v, folder, hidden)
        shutil.copytree(pkg, STAGE / pkg.name)
        (WORK / "projects" / f"{v.id}.json").write_text(json.dumps(project(fam, v), ensure_ascii=False), encoding="utf-8")
        (folder / "meta.json").write_text(json.dumps(meta(fam, v), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(jobs)} packages staged in {STAGE}", flush=True)

    if not args.no_render:
        import appsession  # tools/transitions_stock
        import renderlock  # tools/scene_templates
        from harness import Renderer, engine_source
        renderer = Renderer((256, 144))
        suspicious = []
        with renderlock.exclusive("efectos"), appsession.session(WORK, exe=EXE, env={"DRIFT_EFFECTS_DIR": str(STAGE)}) as app:
            for fam, v in jobs:
                folder = OUT / v.id
                if not app.load(WORK / "projects" / f"{v.id}.json"):
                    continue
                frame = WORK / f"{v.id}.png"
                if app.capture(min(v.thumb, fam.preview - 0.05), frame):
                    with Image.open(frame) as im:
                        card = im.convert("RGB").resize((768, 432), Image.LANCZOS)
                    card.save(folder / "thumbnail.png", optimize=True)
                    card.resize((320, 180), Image.LANCZOS).save(folder / "package" / package_id(v) / "thumbnail.png")
                    frame.unlink()
                    prog = renderer.compile(engine_source(fam, v))
                    ref = renderer.frames(prog, param_defaults(fam, v), photo_for(fam, v),
                                          [min(v.thumb, fam.preview - 0.05)], fam.preview)[0]
                    prog.release()
                    score = diff(card, ref)
                    if score > 22:
                        suspicious.append((v.id, round(score, 1)))
                if not args.no_preview and not app.export(folder / "preview.mp4", 0.0, fam.preview, 360):
                    print(f"  {v.id}: export failed", flush=True)
                print(f"rendered {v.id}", flush=True)
        if suspicious:
            print("cards that differ from the offline render (shader not compiled in the app?):", suspicious)

    for fam, v in jobs:
        folder = OUT / v.id
        target = folder / f"{v.id}.driftfx"
        driftfx.write(folder / "package" / package_id(v), "effects", package_meta(v), target)
        driftfx.check(target)
    contact_sheets()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
