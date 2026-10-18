"""Comprueba en vivo el contenido de Stock tras el despliegue de la 0.15.0."""
from __future__ import annotations

import hashlib
import json
import random
import urllib.request
from pathlib import Path

LOCAL = Path.home() / "Downloads" / "FlipStudio" / "tienda" / "plantillas" / "publicar"
BASE = "https://api.getflipstudio.com/plantillas/"


def get(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


idx = json.loads(get(BASE + "index.json"))
items = idx.get("templates", idx)
yt = [e for e in items if e["id"].startswith("yt-")]
print(f"índice en vivo: {len(items)} plantillas ({len(yt)} yt-*)")
print("campo addedAt:", "sí" if items[0].get("addedAt") else "no")

random.seed(7)
sample = random.sample(yt, 3) + random.sample([e for e in items if not e["id"].startswith("yt-")], 3)
ok = 0
for e in sample:
    try:
        remote = get(BASE + e["zip"])
        local_zip = (LOCAL / e["zip"]).read_bytes()
        same = hashlib.sha256(remote).hexdigest() == hashlib.sha256(local_zip).hexdigest()
        ok += same
        print(f"  {e['id']}: zip {'idéntico' if same else 'DISTINTO'} ({len(remote)/1e6:.1f} MB)")
    except Exception as exc:  # noqa: BLE001
        print(f"  {e['id']}: error {exc}")

for e in sample[:2]:
    try:
        remote = get(BASE + e["thumb"])
        local_png = (LOCAL / e["thumb"]).read_bytes()
        print(f"  {e['id']} miniatura: {'idéntica' if remote == local_png else 'DISTINTA'}")
    except Exception as exc:  # noqa: BLE001
        print(f"  {e['id']} miniatura: error {exc}")

halloween = [e["id"] for e in items if "halloween" in e["id"] or "calabaza" in e["id"]]
print("elementos de Halloween en el índice:", halloween[:5] or "ninguno")

for pack in ("sonidos", "superposiciones", "transiciones", "animaciones", "fondos"):
    d = json.loads(get(f"{BASE}{pack}/index.json"))
    print(f"  {pack}: {len(d.get('templates', d))}")

cole = json.loads(get(BASE + "colecciones.json"))
print("kits:", len(cole.get("collections", [])))
i18n = json.loads(get(BASE + "i18n/fr.json"))
print("i18n fr: elementos", len(i18n.get("items", {})))
