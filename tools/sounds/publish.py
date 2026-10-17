"""Puts the rendered sound effects where api.getflipstudio.com serves them (Stock › Sonidos).

    py tools/sounds/publish.py

Writes into the same folder as the templates (tienda/plantillas/publicar), under sonidos/:
  index.json, <id>.wav, <id>/thumbnail.png, <id>/preview.mp3
then upload the whole folder with flipstudio-api/deploy/plantillas.ps1.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from designs import CATEGORIES as CATEGORY_NAMES  # noqa: E402  (also the order of the categories in the filter)

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda"
SOURCE = ROOT / "sonidos" / "paquetes"
OUT = ROOT / "plantillas" / "publicar" / "sonidos"



def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    cats = list(CATEGORY_NAMES)
    entries = []
    for folder in sorted(p for p in SOURCE.iterdir() if (p / "meta.json").exists()):
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        oid = meta["id"]
        video = folder / f"{oid}.wav"
        if not video.exists() or not (folder / "thumbnail.png").exists():
            print(f"skip {oid}: missing files")
            continue
        data = video.read_bytes()
        shutil.copy2(video, OUT / f"{oid}.wav")
        (OUT / oid).mkdir()
        shutil.copy2(folder / "thumbnail.png", OUT / oid / "thumbnail.png")
        shutil.copy2(folder / "preview.mp3", OUT / oid / "preview.mp3")
        cat = meta["category"]
        entries.append({
            "id": oid, "names": meta["names"], "category": cat, "categoryNames": CATEGORY_NAMES.get(cat, {}),
            "order": cats.index(cat) * 1000 if cat in cats else 99_000,
            "durationSec": meta["durationSec"], "slots": 0, "texts": 0,
            "tags": meta.get("tags", []), "premium": False, "width": 384, "height": 384,
            "thumb": f"{oid}/thumbnail.png", "preview": f"{oid}/preview.mp3",
            "zip": f"{oid}.wav", "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
        })
    entries.sort(key=lambda e: (e["order"], e["id"]))
    (OUT / "index.json").write_text(json.dumps({"templates": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(e["bytes"] for e in entries)
    print(f"{len(entries)} sounds, {total / 1e6:.0f} MB -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
