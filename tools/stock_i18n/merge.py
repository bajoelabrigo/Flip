"""Fold translated batches (work/done/<lang>-*.json) into tools/stock_i18n/<lang>.json.

    py tools/stock_i18n/merge.py            # every language with done batches
    py tools/stock_i18n/merge.py --lang fr

Only well-formed entries for keys that exist in the indexes are taken; tags are lower-cased,
trimmed and de-duplicated. Processed batches move to work/merged/.
"""
from __future__ import annotations

import argparse
import json

from common import LANGS, WORK, load_sources, load_translations, save_json, translation_path, valid_item


def clean_tags(tags: list[str]) -> list[str]:
    out: list[str] = []
    for t in tags:
        t = " ".join(t.strip().lower().split())
        if t and t not in out:
            out.append(t)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", action="append")
    args = ap.parse_args()

    items, categories = load_sources()
    own_keys = {i["key"] for i in items if not i["base"]}
    for lang in args.lang or LANGS:
        files = sorted((WORK / "done").glob(f"{lang}-*.json"))
        if not files:
            continue
        tr = load_translations(lang)
        added = skipped = 0
        for f in files:
            data = json.loads(f.read_text(encoding="utf-8"))
            for key, entry in data.get("items", {}).items():
                if key in own_keys and valid_item(entry):
                    tr["items"][key] = {"name": entry["name"].strip(), "tags": clean_tags(entry["tags"])}
                    added += 1
                else:
                    skipped += 1
                    print(f"  {f.name}: skipped {key!r}")
            for key, name in data.get("categories", {}).items():
                if key in categories and isinstance(name, str) and name.strip():
                    tr["categories"][key] = name.strip()
            dest = WORK / "merged" / f.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            f.replace(dest)
        save_json(translation_path(lang), tr)
        print(f"{lang}: merged {added} items from {len(files)} batch(es), skipped {skipped}")


if __name__ == "__main__":
    main()
