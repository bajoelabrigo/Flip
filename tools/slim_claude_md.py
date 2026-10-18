"""Mueve a docs/historia.md los bloques viejos de CLAUDE.md y deja un puntero."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(r"C:\Users\bajoe\Downloads\FlipStudio\codigo\Flip")
claude = ROOT / "CLAUDE.md"
history = ROOT / "docs" / "historia.md"

text = claude.read_text(encoding="utf-8")

moved = [
    ("## Lo que avanzamos el 2026-10-12", "## Mañana (2026-10-13): usuarios, instalaciones y Pexels"),
    ("## Mañana (2026-10-13): usuarios, instalaciones y Pexels",
     "## El panel de video salió en inglés: qué se sabe (2026-10-12)"),
    ("### 0.9.7 en curso (2026-10-13)",
     "### 0.9.8 PUBLICADA (2026-10-13, noche): capas de ajuste profesionales y LUT"),
    ("### 0.9.8 PUBLICADA (2026-10-13, noche): capas de ajuste profesionales y LUT",
     "### 0.9.9 PUBLICADA (2026-10-14): capas de ajuste como en Photoshop"),
]

chunks: list[str] = []
for start, end in moved:
    i, j = text.find(start), text.find(end)
    if i == -1 or j == -1 or j <= i:
        print("no encontrado:", start)
        continue
    chunks.append(text[i:j].rstrip() + "\n")
    text = text[:i] + text[j:]

pointer = (
    "## Historia (movida a `docs/historia.md`)\n\n"
    "Lo cerrado de las 0.9.x, el plan de cuentas/instalaciones/Pexels del 2026-10-13 y la investigación del panel\n"
    "en inglés están en `docs/historia.md`; aquí quedan solo el estado, las trampas vigentes y la rutina.\n\n"
)
anchor = "## Rutina de publicación (lo que funcionó en la 0.9.2)"
text = text.replace(anchor, pointer + anchor, 1) if anchor in text else text + "\n" + pointer

claude.write_text(text, encoding="utf-8", newline="")

header = (
    "# Historia de Flip Studio\n\n"
    "Bloques que salieron de `CLAUDE.md` por espacio (2026-10-17). Se conservan tal cual: sirven\n"
    "para entender por qué el código está como está, no como instrucciones del día a día.\n"
)
if history.exists():
    old = history.read_text(encoding="utf-8")
    if not old.startswith("# Historia de Flip Studio"):
        history.write_text(header + "\n" + old, encoding="utf-8", newline="")
else:
    history.write_text(header, encoding="utf-8", newline="")

with history.open("a", encoding="utf-8", newline="") as f:
    for chunk in chunks:
        f.write("\n---\n\n" + chunk + "\n")

print("CLAUDE.md bytes:", len(text.encode("utf-8")))
print("historia.md bytes:", history.stat().st_size)
