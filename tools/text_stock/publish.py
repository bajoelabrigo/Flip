"""Puts the built text styles and text animations where api.getflipstudio.com serves them.

    py tools/text_stock/publish.py

Writes into the same folder as the templates (tienda/plantillas/publicar):
  estilos-texto/   index.json, <id>.json (the style file), <id>/thumbnail.png, <id>/preview.mp4
  textos-animados/ index.json, <id>.json (the preset file), <id>/thumbnail.png, <id>/preview.mp4
then upload the whole folder with flipstudio-api/deploy/plantillas.ps1.

In the app (0.14.0): a text style installs with AppController::importUserTextPreset(<file url>)
(Mis estilos), a text animation with AppController::importTextAnimationPreset(<file url>, "").
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build import ANIM_CATEGORIES, ANIMS, OUT, PREVIEW, STYLE_CATEGORIES, STYLES, THUMB  # noqa: E402
from kit import ROOT  # noqa: E402

PUBLISH = ROOT / "tienda" / "plantillas" / "publicar"


def publish(kind: str, items, categories: dict, target: str, delivery: str) -> None:
    out = PUBLISH / target
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    cats = list(categories)
    entries = []
    for n, item in enumerate(items):
        folder = OUT / kind / item.id
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        if not (folder / "thumbnail.png").exists():
            print(f"skip {item.id}: no thumbnail")
            continue
        data = (folder / f"{item.id}.json").read_bytes()
        (out / f"{item.id}.json").write_bytes(data)
        (out / item.id).mkdir()
        shutil.copy2(folder / "thumbnail.png", out / item.id / "thumbnail.png")
        has_preview = (folder / "preview.mp4").exists()
        if has_preview:
            shutil.copy2(folder / "preview.mp4", out / item.id / "preview.mp4")
        cat = meta["category"]
        entry = {
            "id": item.id, "names": meta["names"], "category": cat, "categoryNames": categories.get(cat, {}),
            "order": (cats.index(cat) if cat in cats else 99) * 1000 + n,
            "durationSec": meta["durationSec"], "slots": 0, "texts": 1, "tags": meta.get("tags", []),
            "premium": False, "width": THUMB, "height": THUMB, "thumb": f"{item.id}/thumbnail.png",
            "preview": f"{item.id}/preview.mp4" if has_preview else None,
            "zip": f"{item.id}.json", "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "delivery": delivery, "sample": meta.get("sample", ""),
        }
        if kind == "estilos":
            entry["subtitle"] = meta.get("subtitle", False)
            entry["font"] = meta.get("font")
        else:
            entry["textSlots"] = meta["slots"]  # in / out / loop: which gallery the preset belongs to
        entries.append(entry)
    entries.sort(key=lambda e: (e["order"], e["id"]))
    (out / "index.json").write_text(json.dumps({"templates": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(e["bytes"] for e in entries)
    print(f"{len(entries)} {target} ({total / 1e3:.0f} kB of files) -> {out}")


def main() -> int:
    publish("estilos", STYLES, STYLE_CATEGORIES, "estilos-texto", "text-style")
    publish("animaciones", ANIMS, ANIM_CATEGORIES, "textos-animados", "text-animation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
