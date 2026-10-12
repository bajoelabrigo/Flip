#!/usr/bin/env bash
# Remote half of the deploy: unpack the uploaded site next to the live one and swap it in
# with a single rename, so a visitor never sees a half-uploaded site.
set -euo pipefail

ROOT=/var/www/flipstudio-web
ARCHIVE=/tmp/fws.tar.gz

test -f "$ARCHIVE" || { echo "no archive at $ARCHIVE" >&2; exit 1; }

rm -rf "$ROOT.new"
mkdir -p "$ROOT.new"
tar xzf "$ARCHIVE" --no-same-owner -C "$ROOT.new"
chmod -R a+rX "$ROOT.new"

if [ -d "$ROOT" ]; then
  mv "$ROOT" "$ROOT.old"
fi
mv "$ROOT.new" "$ROOT"
rm -rf "$ROOT.old" "$ARCHIVE"

echo "swapped"
md5sum "$ROOT/addons/index.json"
ls -l "$ROOT/addons/index.json"
grep -c '"id"' "$ROOT/addons/index.json"
