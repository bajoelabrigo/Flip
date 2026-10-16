"""Write <PUBLICAR>/i18n/<lang>.json from tools/stock_i18n/<lang>.json, deriving the variants.

    py tools/stock_i18n/build.py             # validate and write every language
    py tools/stock_i18n/build.py --check     # only report what is missing, write nothing
    py tools/stock_i18n/build.py --strict    # exit 1 if anything is missing

Variants ("<id>-h") get "<base name> (<suffix word>)" and the base's tags. Missing items are left
out (the server falls back to English) and reported per language.
"""
from __future__ import annotations

import argparse
import json
import sys

from common import LANGS, PUBLICAR, VARIANTS, load_sources, load_translations, save_json, valid_item, variant_name


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()

    items, categories = load_sources()
    print(f"{len(items)} items, {len(categories)} categories in {PUBLICAR}")
    total_missing = 0
    for lang in LANGS:
        tr = load_translations(lang)
        out: dict = {"items": {}, "categories": {}}
        missing: list[str] = []
        for i in items:
            if i["base"]:
                base = tr["items"].get(i["base"])
                if valid_item(base):
                    out["items"][i["key"]] = {"name": variant_name(base["name"], VARIANTS[i["suffix"]][lang], lang),
                                              "tags": list(base["tags"])}
                else:
                    missing.append(i["base"])
                continue
            entry = tr["items"].get(i["key"])
            if valid_item(entry):
                out["items"][i["key"]] = {"name": entry["name"], "tags": entry["tags"]}
            else:
                missing.append(i["key"])
        missing_cats = []
        for key in categories:
            name = tr["categories"].get(key)
            if isinstance(name, str) and name.strip():
                out["categories"][key] = name
            else:
                missing_cats.append(key)
        stale = sorted(set(tr["items"]) - {i["key"] for i in items})
        missing = sorted(set(missing))
        total_missing += len(missing) + len(missing_cats)
        print(f"{lang}: {len(out['items'])} items, {len(out['categories'])} categories; "
              f"missing {len(missing)} items, {len(missing_cats)} categories"
              + (f"; {len(stale)} no longer in Stock" if stale else ""))
        for k in (missing + missing_cats)[:5]:
            print(f"    missing {k}")
        if not args.check:
            path = PUBLICAR / "i18n" / f"{lang}.json"
            save_json(path, out)
            json.loads(path.read_text(encoding="utf-8"))  # round-trip: valid UTF-8 JSON
    if args.strict and total_missing:
        sys.exit(1)


if __name__ == "__main__":
    main()
