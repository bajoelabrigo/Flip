"""Writes the built-in text animations of Text › Animation and renders review sheets of them.

    py tools/text_animations/build.py                    check, write presets/text-animations/<id>.json
    py tools/text_animations/build.py --sheet [--only a,b|prefix*] [--exe path]
                                                         also render frames of each one into
                                                         Downloads/FlipStudio/pruebas/animaciones-texto/

The designs live in the in_*.py / out_*.py modules (lists named PRESETS of tkit.T). The Spanish names
go to es.json for drift_es.ts. Rendering uses a portable build OUTSIDE the repo through headless MCP
(tools/e2e/mcp_e2e.py), with the registry backed up and restored around the run; the presets reach
it through DRIFT_TEXT_ANIMATIONS (relative to the exe: the variable splits on ':').
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "tools" / "e2e"))

from tkit import CHIPS, T, argb  # noqa: E402

PRESETS_DIR = REPO / "presets" / "text-animations"
ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio"
SHEETS = ROOT / "pruebas" / "animaciones-texto"
APPDATA = Path(os.environ["APPDATA"]) / "Flip Studio" / "Flip Studio"
REG_KEY = r"HKCU\Software\Flip Studio"
ACCOUNT_KEY = r"HKCU\Software\Flip Studio\Flip Studio\account"
MANIFEST = HERE / "generated.json"   # ids this tool wrote, so a rename removes the old file

MODULES = sorted(p.stem for p in HERE.glob("in_*.py")) + sorted(p.stem for p in HERE.glob("out_*.py"))
W, H = 960, 540
FRAMES = 6
US = 1_000_000


def load(modules: list[str] | None = None) -> list[T]:
    out: list[T] = []
    for name in modules or MODULES:
        mod = importlib.import_module(name)
        for t in mod.PRESETS:
            out.append(t)
    for i, t in enumerate(out):
        t.order = i
    return out


def check(presets: list[T]) -> list[str]:
    problems = []
    generated = set(json.loads(MANIFEST.read_text(encoding="utf-8"))) if MANIFEST.exists() else set()
    hand_made = {p.stem for p in PRESETS_DIR.glob("*.json")} - generated
    seen, es_for = set(), {}
    for t in presets:
        if t.id in hand_made:
            problems.append(f"{t.id}: clashes with a hand-made preset")
        if t.id in seen:
            problems.append(f"{t.id}: duplicate id")
        seen.add(t.id)
        if t.cat not in CHIPS:
            problems.append(f"{t.id}: unknown chip {t.cat}")
        if not set(t.slots) <= {"in", "out", "loop"} or not t.slots:
            problems.append(f"{t.id}: bad slots {t.slots}")
        if es_for.get(t.en, t.es) != t.es:
            problems.append(f"{t.id}: '{t.en}' is already '{es_for[t.en]}' in Spanish, not '{t.es}'")
        es_for[t.en] = t.es
        text = json.dumps(t.document())
        declared = set(t.param_defaults()) | {"duration", "stagger", "unit", "order", "ease"}
        for r in set(re.findall(r'"\{(\w+)\}"', text)) | set(re.findall(r'"\$": "(\w+)"', text)):
            if r not in declared:
                problems.append(f"{t.id}: references undeclared param {r}")
    for slot in ("in", "out"):
        names = [t.en for t in presets if slot in t.slots]
        for n in {x for x in names if names.count(x) > 1}:
            problems.append(f"'{n}' is used twice in the {slot} gallery")
    return problems


def write(presets: list[T]) -> None:
    old = set(json.loads(MANIFEST.read_text(encoding="utf-8"))) if MANIFEST.exists() else set()
    for gone in old - {t.id for t in presets}:
        (PRESETS_DIR / f"{gone}.json").unlink(missing_ok=True)
    for t in presets:
        (PRESETS_DIR / f"{t.id}.json").write_text(json.dumps(t.document(), ensure_ascii=False, indent=1) + "\n",
                                                 encoding="utf-8", newline="\n")
    MANIFEST.write_text(json.dumps(sorted(t.id for t in presets), indent=0) + "\n", encoding="utf-8", newline="\n")
    es = {t.en: t.es for t in presets}
    (HERE / "es.json").write_text(json.dumps(es, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                                  encoding="utf-8", newline="\n")


# --- review sheets --------------------------------------------------------------------------------

def kf(v: float) -> dict:
    return {"keyframes": [{"timeUs": 0, "value": float(v)}]}


def look() -> dict:
    return {"fontFamily": "Montserrat", "pixelSize": 150, "fontWeight": 900, "italic": False,
            "layers": [{"id": "shadow", "kind": "shadow", "enabled": True, "opacity": 0.6, "offsetX": 0, "offsetY": 7,
                        "blur": 20, "paint": {"kind": "solid", "color": argb("#000000")}},
                       {"id": "stroke", "kind": "stroke", "enabled": True, "opacity": 1, "width": 7,
                        "strokeAlign": "outside", "paint": {"kind": "solid", "color": argb("#16181f")}},
                       {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1,
                        "paint": {"kind": "solid", "color": argb("#ffffff")}}],
            "align": "center", "valign": "middle", "wordWrap": True, "lineHeight": 1.15, "animation": {}}


def reveal_seconds(t: T) -> float:
    d = t.param_defaults()
    n = {"word": 1, "line": 1, "block": 1}.get(d.get("unit", "block"), len(t.sample.replace(" ", "")))
    slots = (n - 1) / 2 if d.get("order") == "centerOut" else (n - 1)
    lead = float(d.get("lead", 0.0)) if t.caret else 0.0
    return lead + float(d.get("duration", 0.4)) + float(d.get("stagger", 0.06)) * slots


def project(t: T, slot: str) -> tuple[dict, list[float]]:
    style = look()
    style["animation"][slot] = {"preset": t.id}
    reveal = reveal_seconds(t)
    tail = 1.0  # particles and glyph carets outlive the motion
    if slot == "in":
        seconds = reveal + tail + 0.5
        times = [reveal * f for f in (0.08, 0.3, 0.55, 0.8)] + [reveal + 0.15, reveal + tail * 0.6]
    else:
        seconds = reveal + 1.5
        start = seconds - reveal
        times = [start - 0.2] + [start + reveal * f for f in (0.2, 0.45, 0.7, 0.9)] + [seconds - 0.02]
    us = int(round(seconds * US))
    clip = {"srcInUs": 0, "srcOutUs": us, "timelineStartUs": 0, "timelineDurationUs": us}
    bg = {"kind": "rectangle", "cornerRadius": 0, "layers": [
        {"id": "fill", "kind": "fill", "enabled": True, "opacity": 1, "paint": {"kind": "solid", "color": argb("#20232c")}}]}
    doc = {"version": 14, "projectName": "anim-sheet", "width": W, "height": H, "fps": 30, "sampleRate": 48000,
           "background": {"kind": "color", "color": argb("#20232c")}, "assets": [],
           "tracks": [
               {"id": "t2", "type": "text", "name": "Texto", "transitions": [], "clips": [
                   {"id": "c2", "type": "text", **clip, "textContent": t.sample, "textStyle": style,
                    "transformX": kf(60), "transformY": kf(60), "transformW": kf(W - 120), "transformH": kf(H - 120)}]},
               {"id": "t1", "type": "shape", "name": "Fondo", "transitions": [], "clips": [
                   {"id": "c1", "type": "shape", **clip, "shapeStyle": bg,
                    "transformX": kf(0), "transformY": kf(0), "transformW": kf(W), "transformH": kf(H)}]}]}
    return doc, [round(max(0.0, min(seconds - 0.01, x)), 3) for x in times]


def payload(reply) -> dict:
    from mcp_e2e import reply_text
    for text in reply_text(reply):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            continue
    return {"error": reply.get("error") or reply}


def sheets(presets: list[T], exe: Path) -> None:
    from mcp_e2e import Bridge
    from PIL import Image, ImageDraw

    SHEETS.mkdir(parents=True, exist_ok=True)
    work = SHEETS / "_work"
    work.mkdir(exist_ok=True)
    staged = work / "presets"
    if staged.exists():
        shutil.rmtree(staged)
    staged.mkdir()
    for t in load():
        (staged / f"{t.id}.json").write_text(json.dumps(t.document(), ensure_ascii=False), encoding="utf-8")
    os.environ["DRIFT_TEXT_ANIMATIONS"] = os.path.relpath(staged, exe.parent)
    os.environ["FLIP_NO_STATS"] = "1"

    backup = Path(tempfile.gettempdir()) / f"flip-reg-{os.getpid()}.reg"
    account = Path(tempfile.gettempdir()) / f"flip-account-{os.getpid()}.reg"
    subprocess.run(["reg", "export", REG_KEY, str(backup), "/y"], check=True, capture_output=True)
    autosave = APPDATA / "recovery" / "autosave.json"
    had_autosave = autosave.exists()
    projects_before = set((APPDATA / "projects").glob("*")) if (APPDATA / "projects").exists() else set()
    bridge = Bridge(str(exe), "", str(work / "_mcp"), str(ROOT / "codigo" / "flip-addons" / "build" / "stage"))
    cw, ch = 240, 135
    rows = []
    try:
        time.sleep(3)
        for n, t in enumerate(presets, 1):
            for slot in t.slots:
                if slot == "loop":
                    continue
                doc, times = project(t, slot)
                path = work / f"{t.id}-{slot}.json"
                path.write_text(json.dumps(doc), encoding="utf-8")
                print(f"[{n}/{len(presets)}] {t.id} ({slot})", flush=True)
                loaded = payload(bridge.call("load_project", {"path": str(path)}, wait=120))
                if loaded.get("error") or loaded.get("ok") is False:
                    print(f"  load failed: {loaded}", flush=True)
                    continue
                cells = []
                for at in times:
                    shot = payload(bridge.call("capture", {"at": at, "full": True}, wait=120))
                    p = shot.get("path")
                    if not p or not Path(p).exists():
                        print(f"  capture failed at {at}: {shot}", flush=True)
                        cells.append(Image.new("RGB", (cw, ch), "#ff00ff"))
                        continue
                    with Image.open(p) as im:
                        cells.append(im.convert("RGB").resize((cw, ch), Image.LANCZOS))
                    os.remove(p)
                rows.append((f"{t.id} [{slot}] {t.en} / {t.es}", cells))
    finally:
        bridge.close()
        subprocess.run(["reg", "export", ACCOUNT_KEY, str(account), "/y"], capture_output=True)
        subprocess.run(["reg", "delete", REG_KEY, "/f"], capture_output=True)
        subprocess.run(["reg", "import", str(backup)], check=True, capture_output=True)
        if account.exists():
            subprocess.run(["reg", "import", str(account)], capture_output=True)
            account.unlink()
        backup.unlink(missing_ok=True)
        if autosave.exists() and not had_autosave:
            autosave.unlink()
        if (APPDATA / "projects").exists():
            for extra in set((APPDATA / "projects").glob("*")) - projects_before:
                shutil.rmtree(extra, ignore_errors=True) if extra.is_dir() else extra.unlink(missing_ok=True)

    per = 12
    for s in range(0, len(rows), per):
        chunk = rows[s:s + per]
        sheet = Image.new("RGB", (FRAMES * cw, len(chunk) * (ch + 18)), "#101114")
        d = ImageDraw.Draw(sheet)
        for i, (label, cells) in enumerate(chunk):
            y = i * (ch + 18)
            d.text((4, y + 3), label, fill="#ffffff")
            for j, c in enumerate(cells):
                sheet.paste(c, (j * cw, y + 18))
        out = SHEETS / f"hoja-{s // per + 1:02d}.png"
        sheet.save(out)
        print(out)


def selected(presets: list[T], only: str) -> list[T]:
    if not only:
        return presets
    keep = []
    pats = only.split(",")
    for t in presets:
        if any((t.id.startswith(p[:-1]) if p.endswith("*") else t.id == p) for p in pats):
            keep.append(t)
    return keep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--check", metavar="MODULE", help="only check one design module (writes nothing)")
    ap.add_argument("--only", default="")
    ap.add_argument("--exe", type=Path, default=ROOT / "pruebas" / "FlipStudio-animaciones" / "Flip Studio" / "flipstudio.exe")
    a = ap.parse_args()
    if a.check:
        presets = load([a.check])
        problems = check(presets)
        for p in problems:
            print("CHECK:", p)
        for t in presets:
            json.dumps(t.document())
        ins = sum(1 for t in presets if "in" in t.slots)
        outs = sum(1 for t in presets if "out" in t.slots)
        print(f"{a.check}: {len(presets)} presets ({ins} in, {outs} out), {len(problems)} problems")
        return 1 if problems else 0
    presets = load()
    problems = check(presets)
    for p in problems:
        print("CHECK:", p)
    if problems:
        return 1
    write(presets)
    ins = sum(1 for t in presets if "in" in t.slots)
    outs = sum(1 for t in presets if "out" in t.slots)
    print(f"{len(presets)} presets ({ins} in, {outs} out) -> {PRESETS_DIR}")
    if a.sheet:
        sheets(selected(presets, a.only), a.exe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
