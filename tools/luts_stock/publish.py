"""Puts the built LUTs where api.getflipstudio.com will serve them (Stock › LUTs).

    py tools/luts_stock/publish.py

Writes tienda/plantillas/publicar/luts/:
  index.json, <id>.cube (what the app installs with AppController::importLut), <id>/thumbnail.png
in the format of publicar/sonidos/index.json, plus "delivery": "lut". The card is the sample photo
with the look applied on the right, so it doubles as the preview image. Not deployed from here.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import looks  # noqa: E402
from build import OUT, ROOT  # noqa: E402

DEST = ROOT / "plantillas" / "publicar" / "luts"


def main() -> int:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    cats = list(looks.CATEGORIES)
    entries = []
    for n, look in enumerate(looks.LOOKS):
        lid, _es, _en, category = look[0], look[1], look[2], look[3]
        folder = OUT / lid
        cube = folder / f"{lid}.cube"
        if not (cube.exists() and (folder / "thumbnail.png").exists() and (folder / "meta.json").exists()):
            print(f"skip {lid}: missing files")
            continue
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        data = cube.read_bytes()
        shutil.copy2(cube, DEST / cube.name)
        (DEST / lid).mkdir()
        shutil.copy2(folder / "thumbnail.png", DEST / lid / "thumbnail.png")
        entries.append({
            "id": lid, "names": meta["names"], "category": category,
            "categoryNames": looks.CATEGORIES[category], "order": cats.index(category) * 1000 + n,
            "durationSec": 0, "slots": 0, "texts": 0, "tags": meta["tags"], "premium": False,
            "width": meta.get("width", 768), "height": meta.get("height", 432),
            "thumb": f"{lid}/thumbnail.png", "preview": f"{lid}/thumbnail.png",
            "zip": cube.name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "delivery": "lut", "minAppVersion": "0.14.0",
        })
    entries.sort(key=lambda e: (e["order"], e["id"]))
    (DEST / "index.json").write_text(json.dumps({"templates": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(entries)} LUTs, {sum(e['bytes'] for e in entries) / 1e6:.1f} MB -> {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
