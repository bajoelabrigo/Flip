"""Puts the built effects where api.getflipstudio.com will serve them (Stock › Efectos and Efectos › Tendencias).

    py tools/effects_trends/publish.py

Writes tienda/plantillas/publicar/efectos/:
  index.json, <id>.driftfx (or <id>.json for the voices), <id>/thumbnail.png, <id>/preview.mp4
in the format of publicar/transiciones/index.json, with "delivery": "effect" (the 0.21.0 installs the .driftfx with
AddonManager::installUserPackage) or "effect-preset" for the voices. Not deployed from here.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.append(str(HERE.parent / "transitions_stock"))

import designs  # noqa: E402
import driftfx  # noqa: E402
import voices  # noqa: E402
from kit import CATEGORIES, OUT, ROOT  # noqa: E402

DEST = ROOT / "plantillas" / "publicar" / "efectos"
MIN_APP = "0.21.0"


def main() -> int:
    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    cats = list(CATEGORIES)
    entries = []
    jobs = [(f.category, v.id) for f, v in designs.ALL] + [("audio", v[0]) for v in voices.VOICES]
    for n, (category, vid) in enumerate(jobs):
        folder = OUT / vid
        voice = category == "audio"
        pkg = folder / (f"{vid}.json" if voice else f"{vid}.driftfx")
        files = [pkg, folder / "thumbnail.png", folder / "meta.json"] + ([] if voice else [folder / "preview.mp4"])
        missing = [f.name for f in files if not f.exists()]
        if missing:
            print(f"skip {vid}: missing {', '.join(missing)}")
            continue
        if not voice:
            driftfx.check(pkg)
        meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
        data = pkg.read_bytes()
        shutil.copy2(pkg, DEST / pkg.name)
        (DEST / vid).mkdir()
        shutil.copy2(folder / "thumbnail.png", DEST / vid / "thumbnail.png")
        entry = {
            "id": vid, "names": meta["names"], "category": category, "categoryNames": CATEGORIES[category],
            "order": cats.index(category) * 1000 + n, "durationSec": meta["durationSec"], "slots": 0, "texts": 0,
            "tags": meta["tags"], "premium": False, "width": 768, "height": 432,
            "thumb": f"{vid}/thumbnail.png", "thumbWide": f"{vid}/thumbnail.png",
            "zip": pkg.name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "delivery": "effect-preset" if voice else "effect", "minAppVersion": MIN_APP,
            **({"description": meta["description"]} if "description" in meta else {}),
        }
        if not voice:
            shutil.copy2(folder / "preview.mp4", DEST / vid / "preview.mp4")
            entry.update({"preview": f"{vid}/preview.mp4", "previewWide": f"{vid}/preview.mp4", "package": meta["package"]})
            if meta.get("requires"):
                entry["requires"] = meta["requires"]
        entries.append(entry)
    entries.sort(key=lambda e: (e["order"], e["id"]))
    (DEST / "index.json").write_text(json.dumps({"templates": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(entries)} effects, {sum(e['bytes'] for e in entries) / 1e6:.1f} MB of packages -> {DEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
