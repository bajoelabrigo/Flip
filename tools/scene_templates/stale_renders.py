"""Plantillas cuya muestra actual no coincide con la que se renderizó (hay que rehacer la tarjeta).

Compara las fotos que usa hoy cada plantilla (en memoria) con las del último render.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import templates  # noqa: E402

WORK = Path.home() / "Downloads" / "FlipStudio" / "tienda" / "plantillas" / "trabajo"


def current_samples(t) -> set[str]:
    return {c["_sample"] for track in t.tracks for c in track.clips if c.get("_sample")}


def rendered_samples(tid: str) -> set[str] | None:
    path = WORK / tid / "render.json"
    if not path.exists():
        return None
    doc = json.loads(path.read_text(encoding="utf-8"))
    found: set[str] = set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "path" and isinstance(v, str) and "muestras" in v:
                    found.add(Path(v).stem)
                else:
                    walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(doc)
    return found


stale: list[str] = []
missing: list[str] = []
for make in templates.TEMPLATES:
    t = make()
    now = current_samples(t)
    before = rendered_samples(t.id)
    if before is None:
        missing.append(t.id)
    elif now != before:
        stale.append(t.id)

print(f"plantillas: {len(templates.TEMPLATES)}   tarjeta desactualizada: {len(stale)}   sin render: {len(missing)}")
print("STALE=" + ",".join(sorted(stale)))
if missing:
    print("SIN_RENDER=" + ",".join(sorted(missing)))
