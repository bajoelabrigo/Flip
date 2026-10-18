"""Puts the rendered overlays where api.getflipstudio.com serves them (Stock › Superposiciones).

    py tools/overlays/publish.py

Writes into the same folder as the templates (tienda/plantillas/publicar), under superposiciones/:
  index.json, <id>.webm, <id>/thumbnail.png, <id>/preview.mp4
then upload the whole folder with flipstudio-api/deploy/plantillas.ps1.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda"
SOURCE = ROOT / "superposiciones" / "paquetes"
OUT = ROOT / "plantillas" / "publicar" / "superposiciones"

# Order of the categories in the app's filter.
CATEGORY_NAMES = {
    "luces": {"es": "Luces y destellos", "en": "Light leaks and flares"},
    "particulas": {"es": "Partículas y brillos", "en": "Particles and sparkles"},
    "celebracion": {"es": "Celebración", "en": "Celebration"},
    "amor": {"es": "Amor", "en": "Love"},
    "garabatos": {"es": "Garabatos", "en": "Doodles"},
    "clima": {"es": "Clima y naturaleza", "en": "Weather and nature"},
    "pelicula": {"es": "Película y retro", "en": "Film and retro"},
    "glitch": {"es": "Glitch", "en": "Glitch"},
    "camara": {"es": "Cámara y pantalla", "en": "Camera and screen"},
    "marcos": {"es": "Marcos y texturas", "en": "Frames and textures"},
    "youtuber": {"es": "Youtuber", "en": "YouTuber"},
    "camara-cara": {"es": "Marcos para la cámara", "en": "Face-cam frames"},
}


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    cats = list(CATEGORY_NAMES)
    entries = []
    for folder in sorted(p for p in SOURCE.iterdir() if (p / "meta.json").exists()):
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        oid = meta["id"]
        video = folder / f"{oid}.webm"
        if not video.exists() or not (folder / "thumbnail.png").exists():
            print(f"skip {oid}: missing files")
            continue
        data = video.read_bytes()
        shutil.copy2(video, OUT / f"{oid}.webm")
        (OUT / oid).mkdir()
        shutil.copy2(folder / "thumbnail.png", OUT / oid / "thumbnail.png")
        shutil.copy2(folder / "preview.mp4", OUT / oid / "preview.mp4")
        cat = meta["category"]
        entries.append({
            "id": oid, "names": meta["names"], "category": cat, "categoryNames": CATEGORY_NAMES.get(cat, {}),
            "order": cats.index(cat) * 1000 if cat in cats else 99_000,
            "durationSec": meta["durationSec"], "loop": meta.get("loop", True), "slots": 0, "texts": 0,
            "tags": meta.get("tags", []), "premium": False, "width": meta["width"], "height": meta["height"],
            "thumb": f"{oid}/thumbnail.png", "preview": f"{oid}/preview.mp4",
            "zip": f"{oid}.webm", "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
        })
    entries.sort(key=lambda e: (e["order"], e["id"]))
    (OUT / "index.json").write_text(json.dumps({"templates": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(e["bytes"] for e in entries)
    print(f"{len(entries)} overlays, {total / 1e6:.0f} MB -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
