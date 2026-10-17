"""Puts the built music cuts where api.getflipstudio.com serves them (Stock › Música).

    py tools/music/publish.py

Writes into the same folder as the templates (tienda/plantillas/publicar), under musica/:
  index.json, <id>.mp3, <id>/thumbnail.png, <id>/preview.mp3, CREDITS.json, LICENCIA.txt
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
from catalog import CATEGORIES as CATEGORY_NAMES  # noqa: E402  (also the order of the categories in the filter)

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda"
SOURCE = ROOT / "musica" / "paquetes"
OUT = ROOT / "plantillas" / "publicar" / "musica"

LICENSE = """MÚSICA DE STOCK — DOMINIO PÚBLICO (CC0 1.0)

Toda la música de Stock › Música viene de autores que la dedicaron al dominio público con la licencia
Creative Commons Zero (CC0 1.0 Universal): https://creativecommons.org/publicdomain/zero/1.0/deed.es
- FreePD (freepd.com, 2008-2025): «This music is all licensed CC0 1.0 Universal Public Domain Dedication».
- HoliznaCC0 en Free Music Archive: cada pista lleva la licencia CC0 1.0 en su página.

Puedes usarla gratis en tus videos, también comerciales y monetizados, sin pedir permiso y sin dar créditos.
Flip Studio solo la eligió, la cortó a 15, 30 y 60 segundos y le igualó el volumen; no reclama ningún derecho
sobre ella. La lista de canciones, con su autor y su página, está en CREDITS.json.

Aviso: al ser de dominio público, otras personas también pueden usar estas canciones, y algún sistema
automático (como Content ID) podría marcarlas por error si alguien las registró como propias. Si te pasa,
puedes disputar el reclamo indicando que la obra es de dominio público (CC0) y enlazar su página.
"""


# Songs not tagged «Instrumental» on FMA: they may have vocals or be covers. Held back until someone listens
# to them (Jorge); take a title out of this set once it has been heard and is fine.
HOLD = {"Kitsune", "Kodama", "Jams", "Pixel Party", "Stealing Glimpses Of Your Face", "Canon Event",
        "God Rest Ye Merry Gentlemen ( Synth Wave )", "Joy To The World ( Synth Wave )",
        "The First Noel ( Synth Wave )", "We Three Kings ( Synth Wave )"}


def held(meta: dict) -> bool:
    return meta.get("song", "") in HOLD


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    cats = list(CATEGORY_NAMES)
    entries = []
    for folder in sorted(p for p in SOURCE.iterdir() if (p / "meta.json").exists()):
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        oid = meta["id"]
        if held(meta):
            print(f"hold {oid}: {meta.get('song')} (to be heard first)")
            continue
        audio = folder / f"{oid}.mp3"
        if not audio.exists() or not (folder / "thumbnail.png").exists():
            print(f"skip {oid}: missing files")
            continue
        data = audio.read_bytes()
        shutil.copy2(audio, OUT / f"{oid}.mp3")
        (OUT / oid).mkdir()
        shutil.copy2(folder / "thumbnail.png", OUT / oid / "thumbnail.png")
        shutil.copy2(folder / "preview.mp3", OUT / oid / "preview.mp3")
        cat = meta["category"]
        # within a category: shorter cuts first, then by name
        order = (cats.index(cat) if cat in cats else 99) * 1000 + {15: 0, 30: 1, 60: 2}.get(meta.get("length"), 3)
        entries.append({
            "id": oid, "names": meta["names"], "category": cat, "categoryNames": CATEGORY_NAMES.get(cat, {}),
            "order": order, "durationSec": meta["durationSec"], "slots": 0, "texts": 0,
            "tags": meta.get("tags", []), "premium": False, "width": 384, "height": 384,
            "thumb": f"{oid}/thumbnail.png", "preview": f"{oid}/preview.mp3",
            "zip": f"{oid}.mp3", "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "bpm": meta.get("bpm"),
            "credit": {"title": meta["song"], "artist": meta["artist"], "license": meta["license"],
                       "url": meta["page"]},
        })
    entries.sort(key=lambda e: (e["order"], e["id"]))
    (OUT / "index.json").write_text(json.dumps({"templates": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
    credits = ROOT / "musica" / "CREDITS.json"
    if credits.exists():
        shutil.copy2(credits, OUT / "CREDITS.json")
    (OUT / "LICENCIA.txt").write_text(LICENSE, encoding="utf-8")
    total = sum(e["bytes"] for e in entries)
    print(f"{len(entries)} music cuts, {total / 1e6:.0f} MB -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
