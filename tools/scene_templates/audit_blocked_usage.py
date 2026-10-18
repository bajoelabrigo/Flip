"""Plantillas construidas que hoy usan una foto de kit.BLOCKED (build.py se negaría a rehacerlas)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path.home() / "Downloads" / "FlipStudio" / "tienda" / "plantillas"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kit  # noqa: E402


def photos(doc) -> set[str]:
    out: set[str] = set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "path" and isinstance(v, str) and "muestras" in v:
                    out.add(Path(v).stem)
                else:
                    walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(doc)
    return out


bad: dict[str, list[str]] = {}
for render in ROOT.glob("trabajo/*/render.json"):
    tid = render.parent.name
    if tid.startswith("_"):
        continue
    try:
        doc = json.loads(render.read_text(encoding="utf-8"))
    except ValueError:
        continue
    hit = sorted(p for p in photos(doc) if p in kit.BLOCKED)
    if hit:
        bad[tid] = hit

print(f"{len(bad)} plantillas construidas usan una foto bloqueada")
for tid, samples in sorted(bad.items()):
    print(f"{tid}\t{','.join(samples)}")
