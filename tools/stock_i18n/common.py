"""Shared bits of the Stock translation tools (see README.md)."""
from __future__ import annotations

import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE / "work"  # scratch: todo/ and done/ batches (git-ignored)

# The published Stock folder (the server reads <PUBLICAR>/i18n/<lang>.json).
PUBLICAR = Path(os.environ.get(
    "FLIP_STOCK_PUBLICAR",
    Path.home() / "Downloads" / "FlipStudio" / "tienda" / "plantillas" / "publicar"))

# type -> folder inside PUBLICAR (same as PACKS in flipstudio-api/src/market.ts).
FOLDERS = {
    "template": ".",
    "animation": "animaciones",
    "overlay": "superposiciones",
    "background": "fondos",
    "sound": "sonidos",
    "music": "musica",
}

# The server's languages minus es/en, which live in the indexes themselves.
LANGS = ["ar", "bn", "fr", "it", "ja", "ko", "pl", "pt", "ru", "si", "tl", "vi", "zh"]

# Id suffixes that mark a variant of another id. Their names are derived:
# "<translated base name> (<suffix word>)", tags copied from the base. Never translated by hand.
VARIANTS = {
    "-h": {
        "ar": "أفقي", "bn": "আনুভূমিক", "fr": "horizontal", "it": "orizzontale", "ja": "横",
        "ko": "가로", "pl": "poziomo", "pt": "horizontal", "ru": "горизонтально", "si": "තිරස්",
        "tl": "pahalang", "vi": "ngang", "zh": "横屏",
    },
}


def variant_of(item_id: str, ids: set[str]) -> tuple[str, str] | None:
    """(base id, suffix) when item_id is a variant of an existing id."""
    for suffix in VARIANTS:
        if item_id.endswith(suffix) and item_id[: -len(suffix)] in ids:
            return item_id[: -len(suffix)], suffix
    return None


def load_sources() -> tuple[list[dict], dict[str, dict]]:
    """All Stock items and categories from the published indexes.

    Returns (items, categories): items are dicts with key/type/id/en/es/category/tags/base/suffix;
    categories maps "<type>:<category>" -> {"en", "es"}.
    """
    items: list[dict] = []
    categories: dict[str, dict] = {}
    for type_, folder in FOLDERS.items():
        index = PUBLICAR / folder / "index.json"
        if not index.exists():
            continue
        entries = json.loads(index.read_text(encoding="utf-8")).get("templates", [])
        ids = {e["id"] for e in entries}
        for e in entries:
            var = variant_of(e["id"], ids)
            names = e.get("names", {})
            cat = e.get("category", "")
            items.append({
                "key": f"{type_}:{e['id']}",
                "type": type_,
                "id": e["id"],
                "en": names.get("en", ""),
                "es": names.get("es", ""),
                "category": cat,
                "tags": e.get("tags", []),
                "base": f"{type_}:{var[0]}" if var else None,
                "suffix": var[1] if var else None,
            })
            cn = e.get("categoryNames", {})
            categories.setdefault(f"{type_}:{cat}", {"en": cn.get("en", cat), "es": cn.get("es", cat)})
    return items, categories


def translation_path(lang: str) -> Path:
    return HERE / f"{lang}.json"


def load_translations(lang: str) -> dict:
    p = translation_path(lang)
    if not p.exists():
        return {"items": {}, "categories": {}}
    raw = json.loads(p.read_text(encoding="utf-8"))
    return {"items": raw.get("items", {}), "categories": raw.get("categories", {})}


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def valid_item(tr: object) -> bool:
    return (isinstance(tr, dict) and isinstance(tr.get("name"), str) and tr["name"].strip() != ""
            and isinstance(tr.get("tags"), list) and len(tr["tags"]) > 0
            and all(isinstance(t, str) and t.strip() for t in tr["tags"]))
