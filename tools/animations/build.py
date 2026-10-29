"""Builds Flip Studio's own animated stickers (Lottie) and renders their cards with the app.

    <venv python> tools/animations/build.py [--only id,id] [--no-render]

<out>/<id>/<id>.json      the Lottie file (what Stock downloads)
<out>/<id>/meta.json      names, category, tags, editable colours
<out>/<id>/thumbnail.png  the card (384x384), rendered by the app over a dark checker
<out>/<id>/preview.mp4    a short loop for the hover preview (360x360)

The render reuses the scene template harness (a portable build OUTSIDE the repo, headless MCP);
the registry is backed up first and restored after, keeping the account key the run may refresh.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "e2e"))

from PIL import Image  # noqa: E402

import designs  # noqa: E402
from mcp_e2e import Bridge, reply_text  # noqa: E402

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio"
APPDATA = Path(os.environ["APPDATA"]) / "Flip Studio" / "Flip Studio"
REG_KEY = r"HKCU\Software\Flip Studio"
ACCOUNT_KEY = r"HKCU\Software\Flip Studio\Flip Studio\account"


def render_project(doc_path: Path, width: int, height: int, seconds: float) -> dict:
    us = int(seconds * 1_000_000)
    tall = height > width
    cw, ch = (1080, 1920) if tall else (1080, 1080)
    box = (0, 0, cw, ch) if tall else (90, 90, 900, 900)
    return {
        "version": 14, "width": cw, "height": ch, "fps": 30, "sampleRate": 48000,
        "background": {"kind": "color", "color": "#ff1d1f27"},
        "assets": [],
        "tracks": [{"id": "t1", "type": "video", "clips": [{
            "id": "c1", "type": "vector", "path": str(doc_path), "timelineStartUs": 0, "timelineDurationUs": us,
            "srcInUs": 0, "srcOutUs": us,
            "x": {"keyframes": [{"timeUs": 0, "value": box[0]}]}, "y": {"keyframes": [{"timeUs": 0, "value": box[1]}]},
            "width": {"keyframes": [{"timeUs": 0, "value": box[2]}]}, "height": {"keyframes": [{"timeUs": 0, "value": box[3]}]},
            "vector": {"kind": "lottie", "path": str(doc_path), "width": width, "height": height, "fps": 30,
                       "durationUs": us, "fit": "contain", "loop": "loop"}}], "transitions": []}],
    }


def payload(reply) -> dict:
    for text in reply_text(reply):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            continue
    return {"error": reply.get("error") or reply}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "tienda" / "animaciones" / "paquetes")
    parser.add_argument("--exe", type=Path,
                        default=ROOT / "pruebas" / "FlipStudio-0.12.0-prueba" / "app" / "Flip Studio" / "flipstudio.exe")
    parser.add_argument("--only", default="")
    parser.add_argument("--no-render", action="store_true")
    # Another set of designs (a module next to this file with a STICKERS list), e.g. extremas.
    parser.add_argument("--designs", default="designs")
    args = parser.parse_args()
    import importlib
    source = importlib.import_module(args.designs)
    only = {s for s in args.only.split(",") if s}

    jobs = []
    for make in source.STICKERS:
        st = make()
        if only and st.id not in only:
            continue
        folder = args.out / st.id
        folder.mkdir(parents=True, exist_ok=True)
        doc = folder / f"{st.id}.json"
        doc.write_text(json.dumps(st.document(), separators=(",", ":")), encoding="utf-8")
        (folder / "meta.json").write_text(json.dumps(st.manifest(), ensure_ascii=False, indent=1), encoding="utf-8")
        seconds = st.frames / st.fps
        render = folder / "render.json"
        render.write_text(json.dumps(render_project(doc.resolve(), st.size, st.h, max(seconds, 2.0))), encoding="utf-8")
        jobs.append((st, folder, render, seconds))
        print(f"built {st.id} ({seconds:.1f} s, {len(st.layers)} layers)", flush=True)
    if args.no_render or not jobs:
        return 0

    backup = Path(tempfile.gettempdir()) / f"flip-reg-{os.getpid()}.reg"
    account = Path(tempfile.gettempdir()) / f"flip-account-{os.getpid()}.reg"
    subprocess.run(["reg", "export", REG_KEY, str(backup), "/y"], check=True, capture_output=True)
    autosave = APPDATA / "recovery" / "autosave.json"
    had_autosave = autosave.exists()
    bridge = Bridge(str(args.exe), "", str(args.out / "_mcp"), str(ROOT / "codigo" / "flip-addons" / "build" / "stage"))
    try:
        time.sleep(3)
        for st, folder, render, seconds in jobs:
            print(f"render {st.id}", flush=True)
            loaded = payload(bridge.call("load_project", {"path": str(render)}, wait=120))
            if loaded.get("error") or loaded.get("ok") is False:
                print(f"  load failed: {loaded}", flush=True)
                continue
            at = seconds * st.thumb
            shot = payload(bridge.call("capture", {"at": at, "full": True}, wait=120))
            path = shot.get("path")
            if not path or not Path(path).exists():
                print(f"  capture failed: {shot}", flush=True)
                continue
            with Image.open(path) as im:
                card = (216, 384) if st.h > st.size else (384, 384)
                im.convert("RGB").resize(card, Image.LANCZOS).save(folder / "thumbnail.png", optimize=True)
            os.remove(path)
            preview = folder / "preview.mp4"
            bridge.call("export_video", {"path": str(preview), "in": 0, "out": max(seconds, 2.0), "video": "h264",
                                         "audio": "aac", "rate": "crf", "crf": 30, "fps": 30, "height": 360}, wait=600)
            deadline = time.time() + 600
            while time.time() < deadline:
                status = payload(bridge.call("export_status", {}, wait=30))
                if not status.get("active") and not status.get("busy"):
                    break
                time.sleep(0.5)
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
