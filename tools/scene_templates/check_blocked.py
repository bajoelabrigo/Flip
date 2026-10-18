"""Lista las plantillas cuyos clips usan fotos bloqueadas (kit.BLOCKED o la lista propia del módulo)."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import kit  # noqa: E402
import templates  # noqa: E402


def module_blocked() -> dict[str, set[str]]:
    """El BLOCKED propio de cada módulo de plantillas (varios lotes lo tienen)."""
    out: dict[str, set[str]] = {}
    for name, mod in list(sys.modules.items()):
        if name.startswith("templates") and isinstance(getattr(mod, "BLOCKED", None), set):
            out[name] = set(mod.BLOCKED)
    return out


offenders: dict[str, set[str]] = {}
errors: list[str] = []
for make in templates.TEMPLATES:
    try:
        t = make()
    except BaseException as exc:  # noqa: BLE001
        errors.append(f"{make.__module__}.{make.__name__}: {exc}")
        continue
    blocked = set(kit.BLOCKED) | module_blocked().get(make.__module__, set())
    bad = {c["_sample"] for track in t.tracks for c in track.clips if c.get("_sample") in blocked}
    if bad:
        offenders[t.id] = bad

print(f"plantillas distintas: {len(templates.TEMPLATES)}")
print(f"con foto bloqueada: {len(offenders)}")
for tid, samples in sorted(offenders.items()):
    print(f"{tid}\t{','.join(sorted(samples))}")
for e in errors:
    print(f"!! {e}")
