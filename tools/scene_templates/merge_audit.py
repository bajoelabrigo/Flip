"""Junta los informes de la auditoría de fotos y, si se pide, los añade a kit.BLOCKED.

    py tools/scene_templates/merge_audit.py            # solo enseña lo encontrado
    py tools/scene_templates/merge_audit.py --apply    # lo añade a kit.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT = HERE / "work" / "audit"
sys.path.insert(0, str(HERE))
import kit  # noqa: E402

reports = sorted(AUDIT.glob("report-*.json"))
blocked: dict[str, str] = {}
unsure: dict[str, str] = {}
checked = 0

# Dudas revisadas a mano (2026-10-17): se bloquean las que enseñan una marca aunque no se lea
# (bordado con forma de logo, pestaña de marca en el vaquero, etiquetas de arnés, un wordmark
# reconocible). Las que solo son la *forma* de un objeto genérico (zapatilla tipo Converse,
# reloj tipo Apple Watch, portátil sin logo) se quedan: una silueta no es una marca.
DECIDED = {
    "christmas-01": "wordmark amarillo tipo Off-White en la camiseta",
    "h-elderly-01": "bordado rojo con forma de logo en el hombro",
    "h-grocery-04": "pestaña de marca en el bolsillo del vaquero",
    "h-pet-01": "etiquetas de marca en los arneses de los perros",
}
blocked.update(DECIDED)

for path in reports:
    data = json.loads(path.read_text(encoding="utf-8"))
    checked += int(data.get("checked") or 0)
    for entry in data.get("blocked", []):
        name = entry["name"].strip()
        if name not in kit.BLOCKED:
            blocked[name] = entry.get("brand", "")
    for entry in data.get("unsure", []):
        unsure[entry["name"].strip()] = entry.get("why", "")

print(f"informes: {len(reports)}   fotos revisadas: {checked}")
print(f"nuevas a bloquear: {len(blocked)}")
for name, why in sorted(blocked.items()):
    print(f"  {name}: {why}")
print(f"dudosas: {len(unsure)}")
for name, why in sorted(unsure.items()):
    print(f"  ? {name}: {why}")

if "--apply" in sys.argv and blocked:
    path = HERE / "kit.py"
    text = path.read_text(encoding="utf-8")
    marker = "\nMOODS = {"
    today = "2026-10-17"
    block = ("\n           # brand audit of the old sample photos (" + today + "): logos, signs, gear and film IP\n")
    names = sorted(blocked)
    line = "           "
    for i, name in enumerate(names):
        piece = f'"{name}", '
        if len(line) + len(piece) > 116:
            block += line.rstrip() + "\n"
            line = "           "
        line += piece
    block += line.rstrip().rstrip(",") + "}\n"
    # El literal de BLOCKED cierra con "}" en su última línea: se inserta justo antes del cierre.
    head, sep, tail = text.partition(marker)
    if not sep:
        raise SystemExit("no encuentro el final de BLOCKED (MOODS = {)")
    close = head.rstrip()
    if not close.endswith("}"):
        raise SystemExit("BLOCKED no cierra con } antes de MOODS")
    head = close[:-1].rstrip()
    if not head.endswith(","):
        head += ","
    path.write_text(head + "\n" + block + "\n" + sep + tail, encoding="utf-8", newline="")
    print(f"kit.py: {len(names)} fotos añadidas a BLOCKED")
