"""Turns the built packages into what api.getflipstudio.com serves for Stock › Templates.

    python tools/scene_templates/publish.py [--packages DIR] [--out DIR]

<out>/index.json            the catalog flipstudio-api reads (TEMPLATES_DIR)
<out>/<id>.zip              the package (the folder, at the zip root as <id>/...)
<out>/<id>/thumbnail.png    the card, and preview.mp4 for the hover/preview

Upload <out> as a whole to TEMPLATES_DIR on the server (swap the directory, as deploy.sh does for
the sites: replacing index.json alone has been seen to come back, see CLAUDE.md).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import zipfile
from pathlib import Path

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda" / "plantillas"

CATEGORY_NAMES = {
    "reels": {"es": "Reels de fotos", "en": "Photo reels"},
    "intro": {"es": "Intros y títulos", "en": "Intros and titles"},
    "text": {"es": "Texto", "en": "Text"},
    "collage": {"es": "Collages", "en": "Collages"},
    "beforeafter": {"es": "Antes y después", "en": "Before and after"},
    "product": {"es": "Productos", "en": "Products"},
    "celebration": {"es": "Celebraciones", "en": "Celebrations"},
    "countdown": {"es": "Cuentas regresivas", "en": "Countdowns"},
    "outro": {"es": "Cierres", "en": "Endings"},
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packages", type=Path, default=ROOT / "paquetes")
    parser.add_argument("--out", type=Path, default=ROOT / "publicar")
    args = parser.parse_args()
    # The animations (tools/animations/publish.py) share the folder: keep them.
    if args.out.exists():
        for child in args.out.iterdir():
            if child.name == "animaciones":
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    args.out.mkdir(parents=True, exist_ok=True)
    entries = []
    for pkg in sorted(p for p in args.packages.iterdir() if (p / "template.json").exists()):
        manifest = json.loads((pkg / "template.json").read_text(encoding="utf-8"))
        tid = manifest["id"]
        zip_path = args.out / f"{tid}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for file in sorted(pkg.rglob("*")):
                if file.is_file():
                    # Stored, not deflated: pictures, music and video are already compressed.
                    kind = zipfile.ZIP_STORED if file.suffix.lower() in {".png", ".mp4", ".m4a", ".jpg"} else zipfile.ZIP_DEFLATED
                    z.write(file, f"{tid}/{file.relative_to(pkg).as_posix()}", compress_type=kind)
        data = zip_path.read_bytes()
        (args.out / tid).mkdir()
        shutil.copy2(pkg / "thumbnail.png", args.out / tid / "thumbnail.png")
        if (pkg / "preview.mp4").exists():
            shutil.copy2(pkg / "preview.mp4", args.out / tid / "preview.mp4")
        entries.append({
            "id": tid,
            "names": manifest.get("names") or {"es": manifest["displayName"], "en": manifest["displayName"]},
            "category": manifest.get("category", ""),
            "categoryNames": CATEGORY_NAMES.get(manifest.get("category", ""), {}),
            "order": manifest.get("order", 0),
            "durationSec": manifest.get("durationSec", 0),
            "slots": manifest.get("slots", 0),
            "texts": manifest.get("texts", 0),
            "tags": manifest.get("tags", []),
            "premium": bool(manifest.get("premium", False)),
            "thumb": f"{tid}/thumbnail.png",
            "preview": f"{tid}/preview.mp4" if (pkg / "preview.mp4").exists() else None,
            "zip": f"{tid}.zip",
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
        })
        print(f"{tid}: {len(data) / 1e6:.1f} MB", flush=True)
    entries.sort(key=lambda e: (e["order"], e["id"]))
    (args.out / "index.json").write_text(json.dumps({"templates": entries}, ensure_ascii=False, indent=1),
                                         encoding="utf-8")
    print(f"{len(entries)} templates -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
