"""Captures a built template at full size (1920×1080) at the given clip times and puts each next to the reference
frame of 50962342.mp4 it copies, cropped to the lower third, to compare edges by pixels.

    py llt4_frames.py <template id> <ref start s (abs time of u=0)> <out dir> <u> [u ...]

Writes <out>/<id>-<u>.png (ours, full), <out>/<id>-<u>-ref.png and <out>/<id>-pares.png (reference over ours).
Restores the registry like build.py (it reuses its render session code)."""

from __future__ import annotations

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

from PIL import Image, ImageDraw  # noqa: E402

import build  # noqa: E402
import renderlock  # noqa: E402
from mcp_e2e import Bridge  # noqa: E402

VIDEO = Path(os.environ["USERPROFILE"]) / "Downloads" / "EDITAR PARA STOCK" / "LOWERTHIRDS" / "50962342.mp4"
EXE = Path("E:/FlipStudio/pruebas/FlipStudio-0.30.2-stock/Flip Studio/flipstudio.exe")
CROP = (0, 640, 1280, 1080)


def ref_frame(at: float, target: Path) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.4f}", "-i", str(VIDEO), "-frames:v", "1",
                    str(target)], check=True)


def main() -> int:
    tid, start, out = sys.argv[1], float(sys.argv[2]), Path(sys.argv[3])
    times = [float(v) for v in sys.argv[4:]]
    out.mkdir(parents=True, exist_ok=True)
    render = build.DEFAULTS["work"] / tid / "render.json"
    backup = Path(tempfile.gettempdir()) / f"flip-reg-{os.getpid()}.reg"
    subprocess.run(["reg", "export", build.REG_KEY, str(backup), "/y"], check=True, capture_output=True)
    autosave = build.APPDATA / "recovery" / "autosave.json"
    had_autosave = autosave.exists()
    projects_before = set(os.listdir(build.APPDATA / "projects")) if (build.APPDATA / "projects").exists() else set()
    shots = []
    with renderlock.exclusive("rendering"):
        bridge = Bridge(str(EXE), "", str(build.DEFAULTS["work"] / "_mcp"),
                        str(build.ROOT / "codigo" / "flip-addons" / "build" / "stage"))
        try:
            time.sleep(3)
            build.payload(bridge.call("load_project", {"path": str(render)}, wait=120))
            for u in times:
                shot = build.payload(bridge.call("capture", {"at": u, "full": True}, wait=120)).get("path")
                mine = out / f"{tid}-{u:.3f}.png"
                shutil.move(shot, mine)
                ref = out / f"{tid}-{u:.3f}-ref.png"
                ref_frame(start + u, ref)
                shots.append((u, mine, ref))
        finally:
            bridge.close()
            subprocess.run(["reg", "delete", build.REG_KEY, "/f"], capture_output=True)
            subprocess.run(["reg", "import", str(backup)], check=True, capture_output=True)
            backup.unlink(missing_ok=True)
            if autosave.exists() and not had_autosave:
                autosave.unlink()
            if (build.APPDATA / "projects").exists():
                for name in set(os.listdir(build.APPDATA / "projects")) - projects_before:
                    shutil.rmtree(build.APPDATA / "projects" / name, ignore_errors=True)
    w, h = (CROP[2] - CROP[0]) // 2, (CROP[3] - CROP[1]) // 2
    sheet = Image.new("RGB", (w * 2, h * len(shots)), "black")
    d = ImageDraw.Draw(sheet)
    for k, (u, mine, ref) in enumerate(shots):
        for col, path in enumerate((ref, mine)):
            with Image.open(path) as im:
                sheet.paste(im.convert("RGB").crop(CROP).resize((w, h)), (col * w, k * h))
        d.text((4, k * h + 4), f"{u:.3f}", fill="yellow")
    sheet.save(out / f"{tid}-pares.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
