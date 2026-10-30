"""Puts the approved VFX where api.getflipstudio.com serves them (Stock › VFX, 0.26).

    python tools/animations/publish_vfx.py <built folder>

<built folder> is where build.py --designs rtfx2_* wrote the packages. Only the ids in APPROVED go
out: Jorge picks them on the review page (2026-10-30: 17 of the first 38). Writes into the templates'
publish folder, under vfx/: index.json, <id>.json (the Lottie file), <id>/thumbnail.png and
<id>/preview.mp4; then the vfx folder is uploaded to the VPS (the server's «vfx» type shows once the
folder has content).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

OUT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda" / "plantillas" / "publicar" / "vfx"

APPROVED = [
    # Fire
    "ex-fuego-explosion-radial", "ex-fuego-corte-derecha", "ex-fuego-golpe-arriba",
    "ex-fuego-disparo-golpe-derecha", "ex-fuego-disparo-golpe-izquierda", "ex-fuego-estela-circular",
    "ex-fuego-carga-circular",
    # Energy
    "ex-energia-golpe-anillos", "ex-energia-golpe-estrella", "ex-energia-corte-derecha",
    "ex-energia-carga-esfera", "ex-energia-explosion", "ex-energia-destello",
    # Sparks
    "ex-chispas-estallido", "ex-chispas-chorros", "ex-chispas-fuente",
    # Electricity
    "ex-electricidad-carga",
]

CATEGORY_NAMES = {
    "extremas-fuego": ("vfx-fuego", {"es": "Fuego", "en": "Fire"}),
    "extremas-energia": ("vfx-energia", {"es": "Energía", "en": "Energy"}),
    "extremas-chispas": ("vfx-chispas", {"es": "Chispas", "en": "Sparks"}),
    "extremas-electricidad": ("vfx-electricidad", {"es": "Electricidad", "en": "Electricity"}),
}


def main() -> int:
    source = Path(sys.argv[1])
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    entries = []
    for aid in APPROVED:
        folder = source / aid
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        for need in (f"{aid}.json", "thumbnail.png", "preview.mp4"):
            if not (folder / need).exists():
                raise SystemExit(f"{aid}: missing {need}")
        data = (folder / f"{aid}.json").read_bytes()
        (OUT / f"{aid}.json").write_bytes(data)
        (OUT / aid).mkdir()
        shutil.copy2(folder / "thumbnail.png", OUT / aid / "thumbnail.png")
        shutil.copy2(folder / "preview.mp4", OUT / aid / "preview.mp4")
        category, names = CATEGORY_NAMES[meta["category"]]
        entries.append({
            "id": aid, "names": meta["names"], "category": category, "categoryNames": names,
            "order": meta.get("order", 0), "durationSec": meta.get("durationSec", 0), "slots": 0, "texts": 0,
            "tags": meta.get("tags", []) + ["vfx"], "premium": False, "thumb": f"{aid}/thumbnail.png",
            "preview": f"{aid}/preview.mp4", "zip": f"{aid}.json", "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data), "colors": meta.get("colors", []),
            "loop": meta.get("loop", False), "width": meta.get("width", 512), "height": meta.get("height", 512),
        })
    entries.sort(key=lambda e: (e["order"], e["id"]))
    (OUT / "index.json").write_text(json.dumps({"templates": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(entries)} VFX -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
