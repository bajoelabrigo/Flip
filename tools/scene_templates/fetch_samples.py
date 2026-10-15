"""Downloads the sample photos the scene template thumbnails and previews are rendered with.

The photos come from Pexels, whose licence allows using them in "a template you sell". They are only
ever composited into thumbnails and previews (a modified, creative use): they are never shipped inside
a template package, whose slots go out empty. Nothing here is committed: the photos land outside the
repo, with CREDITS.json beside them.

    python tools/scene_templates/fetch_samples.py --keys <secretos>/api-claves.txt --out <dir>
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# theme -> (query, how many, orientation)
THEMES: dict[str, tuple[str, int, str]] = {
    "friends": ("latino friends laughing", 12, "portrait"),
    "travel": ("peru travel", 10, "portrait"),
    "cusco": ("cusco", 4, "portrait"),
    "birthday": ("birthday party latina", 8, "portrait"),
    "quince": ("quinceanera dress", 8, "portrait"),
    "mother": ("mother daughter hispanic", 8, "portrait"),
    "graduation": ("graduation cap gown", 6, "portrait"),
    "couple": ("couple romantic latin", 8, "portrait"),
    "food": ("ceviche", 3, "portrait"),
    "cooking": ("cooking ingredients top view", 6, "portrait"),
    "gym": ("fitness workout gym", 6, "portrait"),
    "interior": ("living room interior bright", 8, "portrait"),
    "kitchen-old": ("old kitchen", 2, "portrait"),
    "product": ("sneaker product plain background", 4, "portrait"),
    "fashion": ("streetwear model", 6, "portrait"),
    "portrait": ("latina woman portrait", 8, "portrait"),
    "man": ("latino man portrait smiling", 6, "portrait"),
    "city": ("lima peru city", 4, "portrait"),
    "nature": ("mountains sunrise", 6, "portrait"),
    "beach": ("beach sunset friends", 6, "portrait"),
    "cafe": ("small business coffee shop owner", 4, "portrait"),
    "creator": ("content creator smiling", 4, "portrait"),
    "family": ("hispanic family", 6, "portrait"),
    "baby": ("baby smiling", 3, "portrait"),
    # Trend batch (2026-10-15)
    "halloween": ("halloween costume party", 6, "portrait"),
    "muertos": ("dia de los muertos catrina makeup", 4, "portrait"),
    "christmas": ("christmas family latino", 6, "portrait"),
    "xmaslights": ("christmas lights bokeh", 3, "portrait"),
    "newyear": ("new year party fireworks friends", 5, "portrait"),
    "shopping": ("woman shopping bags", 4, "portrait"),
    "wedding": ("wedding couple latino", 6, "portrait"),
    "pregnant": ("pregnant woman belly", 3, "portrait"),
    "pet": ("dog portrait happy", 5, "portrait"),
    "restaurant": ("restaurant dish plating", 5, "portrait"),
    "coffee": ("latte art coffee cup", 4, "portrait"),
    "salon": ("hair salon stylist", 4, "portrait"),
    "nails": ("manicure nails pink", 3, "portrait"),
    "barber": ("barber haircut", 4, "portrait"),
    "concert": ("concert crowd lights", 4, "portrait"),
    "sport": ("soccer player football", 4, "portrait"),
    "car": ("sports car night", 3, "portrait"),
    "skate": ("skateboard trick", 3, "portrait"),
    "study": ("student studying desk", 3, "portrait"),
    "office": ("small business team office", 4, "portrait"),
    "podcast": ("podcast microphone host", 3, "portrait"),
    "outfit": ("outfit of the day mirror", 4, "portrait"),
    "makeup": ("makeup tutorial woman", 3, "portrait"),
    "selfie": ("latina selfie smile", 4, "portrait"),
}


def read_key(path: Path, name: str) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip().upper().startswith(name):
            rest = line.strip()[len(name):]
            return rest.lstrip(" 	:=").strip()
    raise SystemExit(f"{name} not found in {path}")


def get(url: str, key: str) -> bytes:
    request = urllib.request.Request(url, headers={"Authorization": key, "User-Agent": "FlipStudio-templates/1.0"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=60) as reply:
                return reply.read()
        except Exception as error:  # noqa: BLE001 - retried, then raised
            if attempt == 3:
                raise
            print(f"  retry ({error})", flush=True)
            time.sleep(2 + attempt * 3)
    return b""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keys", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    key = read_key(args.keys, "PEXELS_API_KEY")
    args.out.mkdir(parents=True, exist_ok=True)
    credits_path = args.out / "CREDITS.json"
    credits = json.loads(credits_path.read_text(encoding="utf-8")) if credits_path.exists() else {}

    for theme, (query, count, orientation) in THEMES.items():
        existing = sorted(args.out.glob(f"{theme}-*.jpg"))
        if len(existing) >= count:
            continue
        params = urllib.parse.urlencode({"query": query, "per_page": count * 2, "orientation": orientation})
        data = json.loads(get(f"https://api.pexels.com/v1/search?{params}", key))
        taken = 0
        for photo in data.get("photos", []):
            if taken >= count:
                break
            name = f"{theme}-{taken + 1:02d}.jpg"
            target = args.out / name
            if not target.exists():
                target.write_bytes(get(photo["src"]["large2x"], key))
            credits[name] = {
                "pexelsId": photo["id"],
                "url": photo["url"],
                "photographer": photo["photographer"],
                "photographerUrl": photo["photographer_url"],
                "alt": photo.get("alt", ""),
            }
            taken += 1
        print(f"{theme}: {taken}", flush=True)
        credits_path.write_text(json.dumps(credits, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
