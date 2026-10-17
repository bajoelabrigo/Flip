"""Puts the built transitions where api.getflipstudio.com will serve them (Stock › Transiciones).

    py tools/transitions_stock/publish.py

Writes tienda/plantillas/publicar/transiciones/:
  index.json, <id>.driftfx, <id>/thumbnail.png, <id>/preview.mp4
in the format of publicar/sonidos/index.json, plus "delivery": "transition" and the package id. The 0.14.0
installs the .driftfx with AddonManager::inspectUserPackage + installUserPackage. Not deployed from here.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import designs  # noqa: E402
import driftfx  # noqa: E402
from kit import CATEGORIES, OUT, ROOT  # noqa: E402

DEST = ROOT / "plantillas" / "publicar" / "transiciones"


def main() -> int:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    cats = list(CATEGORIES)
    entries = []
    for n, (fam, v) in enumerate(designs.ALL):
        folder = OUT / v.id
        pkg = folder / f"{v.id}.driftfx"
        files = [pkg, folder / "thumbnail.png", folder / "preview.mp4", folder / "meta.json"]
        if not all(f.exists() for f in files):
            print(f"skip {v.id}: missing files")
            continue
        driftfx.check(pkg)
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        data = pkg.read_bytes()
        shutil.copy2(pkg, DEST / pkg.name)
        (DEST / v.id).mkdir()
        shutil.copy2(folder / "thumbnail.png", DEST / v.id / "thumbnail.png")
        shutil.copy2(folder / "preview.mp4", DEST / v.id / "preview.mp4")
        entries.append({
            "id": v.id, "names": meta["names"], "category": fam.category, "categoryNames": CATEGORIES[fam.category],
            "order": cats.index(fam.category) * 1000 + n, "durationSec": meta["durationSec"], "slots": 0, "texts": 0,
            "tags": meta["tags"], "premium": False, "width": 768, "height": 432,
            "thumb": f"{v.id}/thumbnail.png", "preview": f"{v.id}/preview.mp4",
            "zip": pkg.name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "delivery": "transition", "package": meta["package"], "minAppVersion": "0.14.0",
        })
    entries.sort(key=lambda e: (e["order"], e["id"]))
    (DEST / "index.json").write_text(json.dumps({"templates": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(entries)} transitions, {sum(e['bytes'] for e in entries) / 1e3:.0f} kB of packages -> {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
