"""Mapa foto de muestra -> plantillas que la usan, a partir de <trabajo>/<id>/render.json.

Sirve para la auditoría de marcas: qué fotos viejas siguen sin bloquear y qué plantillas habría
que volver a renderizar si se bloquean.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path.home() / "Downloads" / "FlipStudio" / "tienda" / "plantillas"
WORK = ROOT / "trabajo"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit  # noqa: E402

blocked = set(kit.BLOCKED)
used: dict[str, set[str]] = defaultdict(set)


def photos_in(doc) -> set[str]:
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


for render in WORK.glob("*/render.json"):
    tid = render.parent.name
    if tid.startswith("_"):
        continue
    try:
        doc = json.loads(render.read_text(encoding="utf-8"))
    except ValueError:
        continue
    for p in photos_in(doc):
        used[p].add(tid)

old = sorted(p for p in used if not re.match(r"^y\d", p))
open_old = [p for p in old if p not in blocked]
new = sorted(p for p in used if re.match(r"^y\d", p))

print(f"plantillas con render.json: {len({t for s in used.values() for t in s})}")
print(f"fotos distintas: {len(used)}   viejas: {len(old)} (sin bloquear: {len(open_old)})   nuevas y*: {len(new)}")
print(f"nuevas y* ya bloqueadas: {len([p for p in new if p in blocked])}")
print(f"plantillas que usan alguna foto ya bloqueada: {len({t for p in used if p in blocked for t in used[p]})}")
print()
for p in open_old:
    print(f"{p}\t{len(used[p])}\t{','.join(sorted(used[p]))}")
