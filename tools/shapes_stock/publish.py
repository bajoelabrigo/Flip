"""Puts the built shapes where api.getflipstudio.com serves them (Stock › Formas, «shape» delivery).

    py tools/shapes_stock/build.py
    py tools/shapes_stock/publish.py

Writes into the templates' publish folder (tienda/plantillas/publicar), under formas/:
  index.json, <id>.json (the shape file the app installs), <id>/thumbnail.png
and merges the names of the other 13 languages into publicar/i18n/<lang>.json
(items["shape:<id>"], categories["shape:<category>"]) without touching the other keys.
Then upload the whole folder with flipstudio-api/deploy/plantillas.ps1.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from i18n import OTHER_LANGS  # noqa: E402

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda"
SOURCE = ROOT / "formas" / "paquetes"
PUBLISH = ROOT / "plantillas" / "publicar"
OUT = PUBLISH / "formas"
ADDED_AT = "2026-10-16"


def main() -> int:
    previous = {}
    if (OUT / "index.json").exists():
        # Keep the date a shape first went out, so «Nuevo» in Stock stays honest on a re-publish.
        for e in json.loads((OUT / "index.json").read_text(encoding="utf-8")).get("templates", []):
            previous[e["id"]] = e.get("addedAt", ADDED_AT)
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    entries, docs = [], []
    for folder in sorted(p for p in SOURCE.iterdir() if (p / "meta.json").exists()):
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        sid = meta["id"]
        data = (folder / f"{sid}.json").read_bytes()
        doc = json.loads(data)
        (OUT / f"{sid}.json").write_bytes(data)
        (OUT / sid).mkdir()
        shutil.copy2(folder / "thumbnail.png", OUT / sid / "thumbnail.png")
        entries.append({
            "id": sid, "names": {"es": doc["names"]["es"], "en": doc["names"]["en"]}, "category": meta["category"],
            "categoryNames": {"es": doc["categoryNames"]["es"], "en": doc["categoryNames"]["en"]},
            "order": meta.get("order", 0), "durationSec": 0, "slots": 0, "texts": 0, "tags": meta.get("tags", []),
            "premium": False, "thumb": f"{sid}/thumbnail.png", "zip": f"{sid}.json",
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data), "width": meta.get("width", 512),
            "height": meta.get("height", 512), "aspect": doc["aspect"], "addedAt": previous.get(sid, ADDED_AT),
        })
        docs.append(doc)
    entries.sort(key=lambda e: (e["order"], e["id"]))
    (OUT / "index.json").write_text(json.dumps({"templates": entries}, ensure_ascii=False, indent=1), encoding="utf-8")

    (PUBLISH / "i18n").mkdir(exist_ok=True)
    for lang in OTHER_LANGS:
        path = PUBLISH / "i18n" / f"{lang}.json"
        tr = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        items = tr.setdefault("items", {})
        cats = tr.setdefault("categories", {})
        for doc in docs:
            cat_name = doc["categoryNames"][lang]
            items[f"shape:{doc['id']}"] = {"name": doc["names"][lang], "tags": [cat_name]}
            cats[f"shape:{doc['category']}"] = cat_name
        path.write_text(json.dumps(tr, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(entries)} shapes -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
