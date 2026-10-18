#!/bin/bash
# Aplica el delta de contenido de la 0.15.0 sobre la carpeta viva, sin tocar los archivos que no
# cambiaron: se clona por enlaces duros, se sobrescribe con --unlink-first (para no escribir a
# través del enlace y romper la carpeta viva) y se borran los elementos que salieron (Halloween).
set -euo pipefail

LIVE=/var/www/flipstudio-templates
NEW=/var/www/flipstudio-templates.new
OLD=/var/www/flipstudio-templates.old

echo "== 1. clon por enlaces duros"
rm -rf "$NEW"
cp -al "$LIVE" "$NEW"

echo "== 2. descomprimir el delta encima (unlink-first)"
mkdir -p /tmp/plantillas015-delta
tar -xf /tmp/plantillas015-delta.tar -C /tmp/plantillas015-delta
tar -xf /tmp/plantillas015-delta.tar -C "$NEW" --unlink-first

echo "== 3. borrar lo que ya no está"
if [ -s /tmp/remove-list.txt ]; then
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    case "$f" in
      /*|*..*) echo "ruta rara, se ignora: $f"; continue ;;
    esac
    rm -rf "${NEW:?}/$f"
  done < /tmp/remove-list.txt
fi

echo "== 4. cambiar la carpeta entera"
rm -rf "$OLD"
mv "$LIVE" "$OLD"
mv "$NEW" "$LIVE"

echo "== 5. resumen"
du -sh "$LIVE"
ls "$LIVE" | head -20
echo "índice:"; python3 - <<'PY'
import json
p = "/var/www/flipstudio-templates/index.json"
d = json.load(open(p, encoding="utf-8"))
items = d.get("templates", d)
print(len(items), "plantillas;", sum(1 for e in items if e["id"].startswith("yt-")), "yt-*")
PY
rm -rf "$OLD"
echo "listo"
