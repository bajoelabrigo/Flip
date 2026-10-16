"""One headless Flip Studio session for rendering Stock cards and previews (shared by looks_stock and
transitions_stock).

The app writes to HKCU\\Software\\Flip Studio even headless (recent projects, preferences): the key is
exported first and put back afterwards, a leftover autosave is removed and new project folders are
deleted (CLAUDE.md). The portable must live outside the repo, or it cannot write files.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "e2e"))

from mcp_e2e import Bridge, reply_text  # noqa: E402

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio"
APPDATA = Path(os.environ["APPDATA"]) / "Flip Studio" / "Flip Studio"
EXE = ROOT / "pruebas" / "FlipStudio-0.13.0-arreglo" / "Flip Studio" / "flipstudio.exe"
REG_KEY = r"HKCU\Software\Flip Studio"


def payload(reply) -> dict:
    for text in reply_text(reply):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            continue
    return {"error": reply.get("error") or reply}


class Session:
    def __init__(self, bridge: Bridge):
        self.bridge = bridge

    def call(self, tool: str, args: dict, wait: float = 120) -> dict:
        return payload(self.bridge.call(tool, args, wait=wait))

    def load(self, path: Path) -> bool:
        r = self.call("load_project", {"path": str(path)})
        if r.get("error") or r.get("ok") is False:
            print(f"  load failed: {r}", flush=True)
            return False
        return True

    def capture(self, at: float, target: Path) -> bool:
        r = self.call("capture", {"at": at, "full": True})
        path = r.get("path")
        if not path or not Path(path).exists():
            print(f"  capture failed: {r}", flush=True)
            return False
        shutil.move(path, target)
        return True

    def export(self, target: Path, t0: float, t1: float, height: int, crf: int = 28) -> bool:
        raw = target.with_name(target.stem + ".raw.mp4")
        self.call("export_video", {"path": str(raw), "in": t0, "out": t1, "video": "h264", "audio": "aac",
                                   "rate": "crf", "crf": crf, "fps": 30, "height": height}, wait=600)
        deadline = time.time() + 600
        while time.time() < deadline:
            s = self.call("export_status", {}, wait=30)
            if not s.get("active") and not s.get("busy"):
                break
            time.sleep(0.5)
        if not raw.exists() or raw.stat().st_size < 5_000:
            return False
        # Stock previews are silent: drop the empty audio track.
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-c:v", "copy", "-an",
                        "-movflags", "+faststart", str(target)], check=True)
        raw.unlink()
        return target.exists()


@contextmanager
def session(work: Path, exe: Path = EXE, env: dict | None = None):
    if ".claude" in str(exe) or "codigo" in str(exe):
        raise SystemExit("the app must live outside the repo, or it cannot write files")
    backup = Path(tempfile.gettempdir()) / f"flip-reg-{os.getpid()}.reg"
    subprocess.run(["reg", "export", REG_KEY, str(backup), "/y"], check=True, capture_output=True)
    autosave = APPDATA / "recovery" / "autosave.json"
    had_autosave = autosave.exists()
    projects_before = set(os.listdir(APPDATA / "projects")) if (APPDATA / "projects").exists() else set()
    saved_env = {k: os.environ.get(k) for k in (env or {})}
    os.environ.update(env or {})
    bridge = Bridge(str(exe), "", str(work / "_mcp"), str(ROOT / "codigo" / "flip-addons" / "build" / "stage"))
    try:
        time.sleep(3)
        yield Session(bridge)
    finally:
        bridge.close()
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        subprocess.run(["reg", "delete", REG_KEY, "/f"], capture_output=True)
        subprocess.run(["reg", "import", str(backup)], check=True, capture_output=True)
        backup.unlink(missing_ok=True)
        if autosave.exists() and not had_autosave:
            autosave.unlink()
        if (APPDATA / "projects").exists():
            for name in set(os.listdir(APPDATA / "projects")) - projects_before:
                shutil.rmtree(APPDATA / "projects" / name, ignore_errors=True)
