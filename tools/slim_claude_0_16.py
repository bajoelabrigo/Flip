"""Pasa a docs/historia.md las secciones 0.16.0 y 0.15.0 de CLAUDE.md (ya cerradas) por espacio."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(r"C:\Users\bajoe\Downloads\FlipStudio\codigo\Flip")
claude = ROOT / "CLAUDE.md"
history = ROOT / "docs" / "historia.md"

text = claude.read_text(encoding="utf-8")
moved = [
    ("### 0.16.0 PUBLICADA (2026-10-18)", "### 0.15.0 PUBLICADA (2026-10-18)"),
    ("### 0.15.0 PUBLICADA (2026-10-18)", "### 0.14.0 PUBLICADA (2026-10-17)"),
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
    "Las versiones 0.16.0 y 0.15.0 (menú como Filmora/CapCut y Stock para creadores) están contadas enteras en\n"
    "`docs/historia.md`, con sus trampas; lo de arriba es lo vigente.\n"
)
anchor = "### 0.14.0 PUBLICADA (2026-10-17)"
if anchor in text and chunks:
    text = text.replace(anchor, pointer + "\n" + anchor, 1)

claude.write_text(text, encoding="utf-8", newline="")

with history.open("a", encoding="utf-8", newline="") as f:
    for chunk in chunks:
        f.write("\n---\n\n" + chunk + "\n")

print("CLAUDE.md:", len(text.encode("utf-8")), "bytes")
print("historia.md:", history.stat().st_size, "bytes")
