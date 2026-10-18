"""Compara `publicar` con lo que hay hoy en el servidor y deja la lista de archivos a subir.

- Cambiado o nuevo: su zip/prev/thumb/.cube/.json difieren en sha256 o el elemento es nuevo.
- Quitado: elementos del servidor que ya no están (Halloween), para borrarlos en la copia.
"""
from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

LOCAL = Path.home() / "Downloads" / "FlipStudio" / "tienda" / "plantillas" / "publicar"
BASE = "https://api.getflipstudio.com/plantillas/"
PACKS = {
    "templates": ".", "animaciones": "animaciones", "superposiciones": "superposiciones",
    "fondos": "fondos", "sonidos": "sonidos", "musica": "musica", "luts": "luts",
    "looks": "looks", "estilos-texto": "estilos-texto", "textos-animados": "textos-animados",
    "transiciones": "transiciones", "formas": "formas",
}


def fetch(url: str):
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"  ! {url}: {exc}")
        return None


def entries(doc):
    if not doc:
        return []
    return doc.get("templates", []) if isinstance(doc, dict) else doc


upload: list[str] = []
removed: list[str] = []
changed = 0

for name, folder in PACKS.items():
    local_index = LOCAL / folder / "index.json"
    if not local_index.exists():
        continue
    local = {e["id"]: e for e in entries(json.loads(local_index.read_text(encoding="utf-8")))}
    rel = "" if folder == "." else folder + "/"
    remote_doc = fetch(f"{BASE}{rel}index.json")
    remote = {e["id"]: e for e in entries(remote_doc)}
    for tid, e in local.items():
        before = remote.get(tid)
        if before is None or before.get("sha256") != e.get("sha256"):
            changed += 1
            upload.append(rel + e["zip"])
            for key in ("thumb", "preview", "thumbWide", "previewWide", "thumbSquare", "previewSquare"):
                if e.get(key):
                    upload.append(rel + e[key])
    for tid in remote:
        if tid not in local:
            e = remote[tid]
            removed.append(rel + e["zip"])
            for key in ("thumb", "preview", "thumbWide", "previewWide", "thumbSquare", "previewSquare"):
                if e.get(key):
                    removed.append(rel + e[key])
            removed.append(f"{rel}{tid}")
    upload.append(rel + "index.json")

upload += ["i18n/" + p.name for p in (LOCAL / "i18n").glob("*.json")]
if (LOCAL / "colecciones.json").exists():
    upload.append("colecciones.json")

files = sorted(set(upload))
missing = [f for f in files if not (LOCAL / f).exists()]
files = [f for f in files if (LOCAL / f).exists()]
total = sum((LOCAL / f).stat().st_size for f in files)
print(f"archivos a subir: {len(files)}  ({total / 1e6:.0f} MB)")
print(f"elementos cambiados o nuevos: {changed}")
print(f"archivos a borrar en el servidor: {len(set(removed))} ({len(removed)} rutas)")
if missing:
    print("no están en disco:", missing[:5])

out = Path(sys.argv[1] if len(sys.argv) > 1 else "upload-list.txt")
out.write_text("\n".join(files) + "\n", encoding="utf-8", newline="")
Path("remove-list.txt").write_text("\n".join(sorted(set(removed))) + "\n", encoding="utf-8", newline="")
print("listas:", out, "y remove-list.txt")
