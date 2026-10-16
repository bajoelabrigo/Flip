"""Puts the built animations where api.getflipstudio.com serves them (Stock › Animaciones).

    python tools/animations/publish.py

Writes into the same folder as the templates (tienda/plantillas/publicar), under animaciones/:
  index.json, <id>.json (the Lottie file), <id>/thumbnail.png, <id>/preview.mp4
then upload the whole folder with flipstudio-api/deploy/plantillas.ps1.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda"
SOURCE = ROOT / "animaciones" / "paquetes"
OUT = ROOT / "plantillas" / "publicar" / "animaciones"

CATEGORY_NAMES = {
    "celebracion": {"es": "Celebración", "en": "Celebration"},
    "resaltar": {"es": "Resaltar", "en": "Highlights"},
    "flechas": {"es": "Flechas", "en": "Arrows"},
    "formas": {"es": "Formas", "en": "Shapes"},
    "redes": {"es": "Redes sociales", "en": "Social"},
    "emociones": {"es": "Emociones", "en": "Emotions"},
    "negocios": {"es": "Negocios", "en": "Business"},
    "llamadas": {"es": "Llamadas y marcos", "en": "Callouts and frames"},
    "clima": {"es": "Clima", "en": "Weather"},
    "transiciones": {"es": "Transiciones", "en": "Transitions"},
    "fechas": {"es": "Fechas especiales", "en": "Special days"},
    "comida": {"es": "Comida y bebida", "en": "Food and drink"},
    "deportes": {"es": "Deportes", "en": "Sports"},
    "iconos": {"es": "Iconos", "en": "Icons"},
}


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    entries = []
    for folder in sorted(p for p in SOURCE.iterdir() if (p / "meta.json").exists()):
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        aid = meta["id"]
        doc = folder / f"{aid}.json"
        if not (folder / "thumbnail.png").exists():
            print(f"skip {aid}: no thumbnail")
            continue
        data = doc.read_bytes()
        (OUT / f"{aid}.json").write_bytes(data)
        (OUT / aid).mkdir()
        shutil.copy2(folder / "thumbnail.png", OUT / aid / "thumbnail.png")
        if (folder / "preview.mp4").exists():
            shutil.copy2(folder / "preview.mp4", OUT / aid / "preview.mp4")
        entries.append({
            "id": aid, "names": meta["names"], "category": meta["category"],
            "categoryNames": CATEGORY_NAMES.get(meta["category"], {}), "order": meta.get("order", 0),
            "durationSec": meta.get("durationSec", 0), "slots": 0, "texts": 0, "tags": meta.get("tags", []),
            "premium": False, "thumb": f"{aid}/thumbnail.png",
            "preview": f"{aid}/preview.mp4" if (folder / "preview.mp4").exists() else None,
            "zip": f"{aid}.json", "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "colors": meta.get("colors", []),
        })
    entries.sort(key=lambda e: (e["order"], e["id"]))
    (OUT / "index.json").write_text(json.dumps({"templates": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(entries)} animations -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
