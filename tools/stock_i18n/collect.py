"""List what is still untranslated, per language, in batches for the translator.

    py tools/stock_i18n/collect.py              # all languages, batches of 150
    py tools/stock_i18n/collect.py --lang fr --size 100

Writes work/todo/<lang>-<NN>.json: {"lang", "items": [{key, en, es, category, tags}], "categories": {key: {en, es}}}.
Variants ("-h") are skipped: build.py derives them from their base item.
The translator answers each batch with work/done/<lang>-<NN>.json in the published shape
({"items": {key: {"name", "tags"}}, "categories": {key: name}}) and merge.py folds it in.
"""
from __future__ import annotations

import argparse

from common import LANGS, WORK, load_sources, load_translations, save_json, valid_item


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", action="append", help="only these languages (repeatable)")
    ap.add_argument("--size", type=int, default=150, help="items per batch")
    args = ap.parse_args()

    items, categories = load_sources()
    own = [i for i in items if not i["base"]]
    print(f"{len(items)} items ({len(items) - len(own)} derived variants), {len(categories)} categories")

    todo_dir = WORK / "todo"
    for lang in args.lang or LANGS:
        for old in todo_dir.glob(f"{lang}-*.json"):
            old.unlink()
        tr = load_translations(lang)
        missing = [i for i in own if not valid_item(tr["items"].get(i["key"]))]
        missing_cats = {k: v for k, v in categories.items() if not tr["categories"].get(k)}
        batches = [missing[n:n + args.size] for n in range(0, len(missing), args.size)]
        if not batches and missing_cats:
            batches = [[]]
        for n, batch in enumerate(batches, 1):
            save_json(todo_dir / f"{lang}-{n:02d}.json", {
                "lang": lang,
                "items": [{k: i[k] for k in ("key", "en", "es", "category", "tags")} for i in batch],
                "categories": missing_cats if n == 1 else {},
            })
        print(f"{lang}: {len(missing)} items and {len(missing_cats)} categories missing -> {len(batches)} batch(es)")


if __name__ == "__main__":
    main()
