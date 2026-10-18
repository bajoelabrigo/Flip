"""Redraws the built-in cards on varied photos (0.18, Jorge: «fotos variadas para que no quede todo igual»):
the effects listed in thumb_bases.json "rerender", every effect template and every transition strip.

    py tools/effects/vary_thumbs.py --tools <dir with effectthumbs.exe, templatethumbs.exe, transitionthumbs.exe>
        [--photos <drift-addons>/assets/thumbs] [--only effects|templates|transitions]

The tools come from a Windows build (the `windows-thumb-tools` artifact of build.yml) and need the app's
DLLs beside them: copy them into an unpacked portable's folder. They write into effects/, effect-templates/
and transitions/ of this repo. Afterwards run tools/effects/before_bases.py for the hover's "before" photos.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DEFAULT_PHOTOS = ROOT.parent / "flip-addons" / "work" / "drift-addons" / "assets" / "thumbs"


def run(cmd):
    print(">", " ".join(str(c) for c in cmd), flush=True)
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr, file=sys.stderr)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tools", required=True, type=Path)
    ap.add_argument("--photos", type=Path, default=DEFAULT_PHOTOS)
    ap.add_argument("--only", choices=["effects", "templates", "transitions"])
    opts = ap.parse_args()
    rules = json.loads((HERE / "thumb_bases.json").read_text(encoding="utf-8"))
    failed = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for p in opts.photos.glob("*.jpg"):
            shutil.copy(p, tmp / p.name)
        # effectthumbs resolves the photos relative to the JSON.
        shutil.copy(HERE / "thumb_bases.json", tmp / "bases.json")

        if opts.only in (None, "effects"):
            for eid in rules["rerender"]:
                if not run([opts.tools / "effectthumbs.exe", "--effects", ROOT / "effects", "--bases",
                            tmp / "bases.json", "--only", eid]):
                    failed.append(eid)

        if opts.only in (None, "templates"):
            for tid, photo in rules["templates"].items():
                if not run([opts.tools / "templatethumbs.exe", "--effects", ROOT / "effects", "--templates",
                            ROOT / "effect-templates", "--base", tmp / photo, "--only", tid, "--force"]):
                    failed.append(tid)

        if opts.only in (None, "transitions"):
            pairs = rules["transitionPairs"]
            for i, folder in enumerate(sorted(p for p in (ROOT / "transitions").iterdir() if p.is_dir())):
                meta = json.loads((folder / "transition.json").read_text(encoding="utf-8"))
                a, b = pairs[i % len(pairs)]
                if not run([opts.tools / "transitionthumbs.exe", "--transitions", ROOT / "transitions",
                            "--base-a", tmp / a, "--base-b", tmp / b, "--only", meta["id"]]):
                    failed.append(meta["id"])

    print("failed:", failed or "none")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
