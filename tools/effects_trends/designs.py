"""Every Stock trend effect, from the fx_*.py modules (one per theme, written in parallel)."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

MODULES = sorted(p.stem for p in HERE.glob("fx_*.py"))

FAMILIES = []
for _name in MODULES:
    FAMILIES += importlib.import_module(_name).FAMILIES

ALL = [(f, v) for f in FAMILIES for v in f.variants]

_seen: dict[str, str] = {}
for _f, _v in ALL:
    if _v.id in _seen:
        raise SystemExit(f"duplicate effect id {_v.id} ({_seen[_v.id]} and {_f.key})")
    _seen[_v.id] = _f.key
