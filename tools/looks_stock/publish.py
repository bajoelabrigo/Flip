"""Puts the built looks where api.getflipstudio.com will serve them (Stock › Looks).

    py tools/looks_stock/publish.py

Writes tienda/plantillas/publicar/looks/:
  index.json, <id>.json (the effect-stack preset), <id>/thumbnail.png
in the format of publicar/sonidos/index.json, plus "delivery": "effect-preset". The 0.14.0 imports the
.json with AppController::importUserEffectPreset (it lands in «Mis efectos»). Not deployed from here.
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
from build import OUT, ROOT  # noqa: E402

DEST = ROOT / "plantillas" / "publicar" / "looks"


def main() -> int:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    cats = list(designs.CATEGORIES)
    entries = []
    for n, look in enumerate(designs.LOOKS):
        folder = OUT / look.id
        preset = folder / f"{look.id}.json"
        if not (preset.exists() and (folder / "thumbnail.png").exists()):
            print(f"skip {look.id}: missing files")
            continue
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        payload = json.loads(preset.read_text(encoding="utf-8"))
        assert payload.get("drift") == "effectStack" and payload["effects"], look.id
        data = preset.read_bytes()
        shutil.copy2(preset, DEST / preset.name)
        (DEST / look.id).mkdir()
        shutil.copy2(folder / "thumbnail.png", DEST / look.id / "thumbnail.png")
        entries.append({
            "id": look.id, "names": meta["names"], "category": look.category,
            "categoryNames": designs.CATEGORIES[look.category], "order": cats.index(look.category) * 1000 + n,
            "durationSec": 0, "slots": 0, "texts": 0, "tags": meta["tags"], "premium": False,
            "width": 768, "height": 432, "thumb": f"{look.id}/thumbnail.png", "preview": f"{look.id}/thumbnail.png",
            "zip": preset.name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "delivery": "effect-preset", "effects": meta["effects"], "minAppVersion": "0.14.0",
        })
    entries.sort(key=lambda e: (e["order"], e["id"]))
    (DEST / "index.json").write_text(json.dumps({"templates": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(entries)} looks -> {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
