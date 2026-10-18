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

import renderlock
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
    # Horizontal templates (16:9) and the second reel batch (2026-10-16): people from everywhere.
    "h-travel": ("travel landscape road trip", 8, "landscape"),
    "h-city": ("city skyline evening", 6, "landscape"),
    "h-nature": ("forest mountains lake", 6, "landscape"),
    "h-beach": ("tropical beach aerial", 5, "landscape"),
    "h-food": ("food table dinner top view", 6, "landscape"),
    "h-cooking": ("chef cooking kitchen", 5, "landscape"),
    "h-office": ("business meeting diverse team", 6, "landscape"),
    "h-podcast": ("two people podcast studio microphones", 4, "landscape"),
    "h-gaming": ("gaming setup rgb lights desk", 5, "landscape"),
    "h-sport": ("athlete running stadium", 5, "landscape"),
    "h-soccer": ("soccer match field", 4, "landscape"),
    "h-wedding": ("wedding ceremony couple", 6, "landscape"),
    "h-birthday": ("birthday party cake friends", 5, "landscape"),
    "h-graduation": ("graduates throwing caps", 4, "landscape"),
    "h-family": ("happy family park", 6, "landscape"),
    "h-couple": ("couple sunset", 5, "landscape"),
    "h-kids": ("children playing colorful", 5, "landscape"),
    "h-house": ("modern house exterior", 5, "landscape"),
    "h-interior": ("bright living room", 5, "landscape"),
    "h-classroom": ("teacher classroom students", 4, "landscape"),
    "h-desk": ("laptop desk workspace", 5, "landscape"),
    "h-concert": ("concert stage lights crowd", 4, "landscape"),
    "h-fitness": ("gym workout", 5, "landscape"),
    "h-tech": ("technology circuit abstract", 4, "landscape"),
    "h-portrait": ("smiling woman portrait outdoors", 6, "landscape"),
    "h-man": ("smiling man portrait", 5, "landscape"),
    "h-pet": ("dog playing park", 4, "landscape"),
    "h-christmas": ("christmas tree family living room", 5, "landscape"),
    "h-newyear": ("new year fireworks city", 4, "landscape"),
    "h-halloween": ("halloween pumpkins", 4, "landscape"),
    "h-cafe": ("cozy cafe interior", 5, "landscape"),
    "h-shop": ("small shop owner store", 5, "landscape"),
    "h-grocery": ("grocery store fresh produce", 4, "landscape"),
    "h-tools": ("hardware store tools", 3, "landscape"),
    "h-community": ("community gathering people", 4, "landscape"),
    "h-truck": ("moving boxes truck", 3, "landscape"),
    "h-baby": ("newborn baby", 4, "landscape"),
    "h-mother": ("mother and child hug", 4, "landscape"),
    "h-father": ("father and son", 4, "landscape"),
    "h-easter": ("easter eggs spring", 3, "landscape"),
    "h-lunar": ("red lanterns lunar new year", 3, "landscape"),
    "h-ramadan": ("ramadan lanterns", 3, "landscape"),
    "h-diwali": ("diwali diya lamps", 3, "landscape"),
    "h-thanksgiving": ("thanksgiving dinner table", 3, "landscape"),
    "h-autumn": ("autumn leaves park", 3, "landscape"),
    "h-winter": ("snowy winter landscape", 3, "landscape"),
    "h-spring": ("spring flowers field", 3, "landscape"),
    "h-summer": ("summer pool friends", 3, "landscape"),
    "h-school": ("school supplies notebook", 3, "landscape"),
    "h-earth": ("green earth nature hands plant", 3, "landscape"),
    "h-salon": ("spa beauty salon", 3, "landscape"),
    "h-memorial": ("candles memorial", 2, "landscape"),
    "h-elderly": ("grandparents smiling", 3, "landscape"),
    "h-studio": ("photo studio portfolio", 3, "landscape"),
    "h-product": ("product photography minimal", 4, "landscape"),
    "easter": ("easter family spring", 3, "portrait"),
    "lunar": ("lunar new year red lanterns", 3, "portrait"),
    "ramadan": ("ramadan iftar family", 3, "portrait"),
    "diwali": ("diwali lights woman", 3, "portrait"),
    "holi": ("holi colors festival", 3, "portrait"),
    "thanksgiving": ("thanksgiving family dinner", 3, "portrait"),
    "autumn": ("autumn cozy sweater", 4, "portrait"),
    "winter": ("winter snow friends", 4, "portrait"),
    "spring": ("spring flowers woman", 3, "portrait"),
    "summer": ("summer friends pool", 4, "portrait"),
    "school": ("back to school kids", 3, "portrait"),
    "kids": ("kids playing outdoors", 4, "portrait"),
    "elderly": ("grandparents grandchild", 4, "portrait"),
    "father": ("father daughter", 4, "portrait"),
    "night": ("city night neon street", 4, "portrait"),
    "sunset": ("sunset silhouette", 4, "portrait"),
    "dance": ("dancer studio", 3, "portrait"),
    "bakery": ("bakery fresh bread", 3, "portrait"),
    "icecream": ("ice cream cone", 3, "portrait"),
    "flowers": ("florist bouquet", 3, "portrait"),
    "spa": ("spa massage stones", 3, "portrait"),
    "mechanic": ("car mechanic garage", 3, "portrait"),
    "vet": ("veterinarian dog", 3, "portrait"),
    "laundry": ("laundry folded clothes", 2, "portrait"),
    "handmade": ("handmade crafts artisan", 3, "portrait"),
    "music": ("guitar musician", 3, "portrait"),
    "reading": ("woman reading book cozy", 3, "portrait"),
    "hike": ("hiking mountain trail", 3, "portrait"),
    "home": ("house for sale exterior", 3, "portrait"),
    "garden": ("garden plants", 3, "portrait"),
    "puppy": ("puppy cute", 3, "portrait"),
    "cake": ("birthday cake candles", 3, "portrait"),
    "proposal": ("marriage proposal ring", 3, "portrait"),
    "box": ("package box delivery", 3, "portrait"),
    "skincare": ("skincare product bottle", 3, "portrait"),
    "community": ("community volunteers", 3, "portrait"),
    "church": ("church interior light", 2, "portrait"),
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
    # A batch's own themes, as {"theme": ["query", count, "portrait"|"landscape"]}: only those are fetched.
    parser.add_argument("--themes", type=Path)
    args = parser.parse_args()
    themes = THEMES
    if args.themes:
        themes = {k: tuple(v) for k, v in json.loads(args.themes.read_text(encoding="utf-8")).items()}
    with renderlock.exclusive("downloading samples"):
        return fetch(args, themes)


def fetch(args, themes) -> int:
    key = read_key(args.keys, "PEXELS_API_KEY")
    args.out.mkdir(parents=True, exist_ok=True)
    credits_path = args.out / "CREDITS.json"
    credits = json.loads(credits_path.read_text(encoding="utf-8")) if credits_path.exists() else {}

    for theme, (query, count, orientation) in themes.items():
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
