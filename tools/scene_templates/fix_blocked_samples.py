"""Cambia fotos bloqueadas por alternativas libres en los módulos de plantillas.

"Bloqueada" = está en kit.BLOCKED o en la lista propia del módulo (varios lotes de la 0.15.0 traen
la suya). El reemplazo se elige entre las fotos libres para TODOS los módulos, del mismo tema y que
no aparezcan ya en la misma línea. Se repite hasta que no quede ninguna.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import kit  # noqa: E402

SAMPLES = Path.home() / "Downloads" / "FlipStudio" / "tienda" / "plantillas" / "muestras"
HAVE = sorted(p.stem for p in SAMPLES.glob("*.jpg"))


def module_blocked() -> set[str]:
    import importlib

    out: set[str] = set()
    for path in sorted(HERE.glob("templates*.py")):
        if path.stem in ("templates", ):
            importlib.import_module(path.stem)
        else:
            importlib.import_module(path.stem)
    for name, mod in list(sys.modules.items()):
        if name.startswith("templates") and isinstance(getattr(mod, "BLOCKED", None), set):
            out |= set(mod.BLOCKED)
    return out


U = set(kit.BLOCKED) | module_blocked()
FREE = [h for h in HAVE if h not in U]
print(f"bloqueadas (union): {len(U)}   libres: {len(FREE)}")

PREF = ["friends", "y4c-friends", "family", "party", "portrait", "man", "woman", "couple",
        "birthday", "concert", "cafe", "coffee", "food", "restaurant", "box", "travel", "beach",
        "nature", "city", "night", "pet", "fashion", "gamer", "race", "street", "outfit", "cozy",
        "study", "tech", "phone", "cam", "gadget", "unbox", "work", "desk", "office", "music"]


def theme_of(stem: str) -> str:
    m = re.match(r"^(y\d[a-z]?-)?([a-z]+(?:-[a-z]+)?)-", stem)
    return m.group(2) if m else stem.split("-")[0]


def pool_for(stem: str) -> list[str]:
    theme = theme_of(stem)
    same = [h for h in FREE if theme_of(h) == theme]
    loose = [h for h in FREE if theme.split("-")[0] in h and h not in same]
    family = [h for h in FREE if theme_of(h) in PREF and h not in same and h not in loose]
    rest = [h for h in FREE if h not in same and h not in loose and h not in family]
    return same + loose + family + rest


changed_total = 0
for _round in range(12):
    changed = 0
    for path in sorted(HERE.glob("templates*.py")):
        text = path.read_text(encoding="utf-8")
        out = []
        for line in text.splitlines(keepends=True):
            if '"' not in line:
                out.append(line)
                continue
            names = re.findall(r'"([a-z0-9][a-z0-9-]*)"', line)
            bad = [n for n in names if n in U]
            if not bad:
                out.append(line)
                continue
            new_line = line
            for old in bad:
                free_here = [c for c in pool_for(old) if f'"{c}"' not in new_line]
                if not free_here:
                    continue
                new_line = new_line.replace(f'"{old}"', f'"{free_here[0]}"', 1)
                changed += 1
            out.append(new_line)
        result = "".join(out)
        if result != text:
            path.write_text(result, encoding="utf-8", newline="")
    changed_total += changed
    print(f"vuelta {_round + 1}: {changed} cambios")
    if not changed:
        break
print(f"total: {changed_total}")
