"""Downloads the source songs of Stock › Música and records where each one came from.

    py tools/music/fetch.py [--freepd] [--fma] [--max-mb 25]

Only two sources, both public domain (CC0 1.0), which allows redistributing the files as a catalogue:

- FreePD (freepd.com, closed in 2025). "This music is all licensed CC0 1.0 Universal Public Domain
  Dedication" and "Can I include this music in a piece of software? YES!" — checked on the archived site
  https://web.archive.org/web/20241231185827/https://freepd.com/ and in the README of the mirror the
  files come from (https://a.ocv.me/pub/stuff/music/freepd/, 316 songs, the same list as FreePD's own
  /music/ index).
- HoliznaCC0 on the Free Music Archive. Every track page is read and kept only if its licence link is
  https://creativecommons.org/publicdomain/zero/1.0/ (FMA shows the licence per track).

Writes <ROOT>/fuente/freepd/<folder>__<file>.mp3, <ROOT>/fuente/fma/<track id>.mp3 and
<ROOT>/fuente/sources-freepd.json / sources-fma.json (one entry per song: page URL, file URL, artist, licence, date checked).
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "tienda" / "musica"
SRC = ROOT / "fuente"
UA = {"User-Agent": "Mozilla/5.0 (FlipStudio music catalogue; contact via getflipstudio.com)"}
CC0 = "https://creativecommons.org/publicdomain/zero/1.0/"
FREEPD_MIRROR = "https://a.ocv.me/pub/stuff/music/freepd/"
FREEPD_PROOF = "https://web.archive.org/web/20241231185827/https://freepd.com/"
FREEPD_FOLDERS = ["chill", "classical", "comedy", "country", "electronic", "epic", "fantasy", "horror", "jazz",
                  "misc", "rock", "romantic", "scoring", "unsorted", "upbeat", "world"]
FMA_ARTISTS = ["holiznacc0"]
# Albums left out on purpose: covers of known songs, or albums named after other works.
FMA_SKIP_ALBUMS = {"house-of-the-rising-sun", "interstellar-pop-songs", "bio", "contact", "followers", "discography"}
# Our older copies of the FreePD songs (flip-addons, "musica.libre").
ADDONS_MP3 = Path(os.environ["USERPROFILE"]) / "Downloads" / "FlipStudio" / "codigo" / "flip-addons" / "work" / "musica" / "mp3"


def get(url: str, tries: int = 4) -> bytes:
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read()
        except Exception:
            if i == tries - 1:
                raise
            time.sleep(2 + 3 * i)
    raise RuntimeError


def today() -> str:
    return dt.date.today().isoformat()


def load_sources() -> dict:
    """All the songs downloaded so far (sources-freepd.json + sources-fma.json)."""
    out = {}
    for p in sorted(SRC.glob("sources-*.json")):
        out.update({s["key"]: s for s in json.loads(p.read_text(encoding="utf-8"))})
    return out


def save_sources(src: dict, prefixes=("freepd", "fma")):
    for prefix in prefixes:
        rows = sorted((s for s in src.values() if s["key"].startswith(prefix + "/")), key=lambda s: s["key"])
        if rows:
            (SRC / f"sources-{prefix}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1),
                                                         encoding="utf-8")


def fetch_freepd(src: dict, max_mb: float):
    out = SRC / "freepd"
    out.mkdir(parents=True, exist_ok=True)
    for folder in FREEPD_FOLDERS:
        listing = json.loads(get(f"{FREEPD_MIRROR}{folder}/?ls"))
        for f in listing["files"]:
            name = urllib.parse.unquote(f["href"])
            if not name.lower().endswith(".mp3"):
                continue
            key = f"freepd/{folder}__{name}"
            tags = f.get("tags", {})
            if f["sz"] > max_mb * 1e6:
                continue
            dest = SRC / key
            if not dest.exists():
                old = ADDONS_MP3 / f"{folder}__{name}"
                if old.exists() and old.stat().st_size == f["sz"]:
                    dest.write_bytes(old.read_bytes())
                else:
                    dest.write_bytes(get(f"{FREEPD_MIRROR}{folder}/{f['href']}"))
                print("freepd", name, flush=True)
            src[key] = {
                "key": key, "source": "FreePD", "title": name[:-4], "artist": tags.get("artist") or "FreePD",
                "folder": folder, "page": "https://freepd.com/", "file": f"{FREEPD_MIRROR}{folder}/{f['href']}",
                "license": "CC0 1.0", "licenseUrl": CC0, "licenseProof": FREEPD_PROOF, "checked": today(),
                "bpmHint": tags.get(".bpm"), "durationSec": tags.get(".dur"),
            }
        save_sources(src, ["freepd"])


TRACK_INFO = re.compile(r"data-track-info='([^']+)'")
LICENSE = re.compile(r'rel="license"[^>]*href="([^"]+)"')
GENRE = re.compile(r'href="https://freemusicarchive.org/genre/([^/"]+)/?"')


def fetch_fma(src: dict, max_mb: float):
    out = SRC / "fma"
    out.mkdir(parents=True, exist_ok=True)
    for artist in FMA_ARTISTS:
        disc = get(f"https://freemusicarchive.org/music/{artist}/discography").decode("utf-8", "replace")
        albums = sorted(set(re.findall(rf'href="https://freemusicarchive.org/music/{artist}/([^/"]+)/?"', disc)))
        for album in albums:
            if album in FMA_SKIP_ALBUMS:
                continue
            page = get(f"https://freemusicarchive.org/music/{artist}/{album}/").decode("utf-8", "replace")
            for raw in TRACK_INFO.findall(page):
                info = json.loads(html.unescape(raw))
                key = f"fma/{info['id']}.mp3"
                if key in src and "genres" in src[key]:
                    continue
                track = get(info["url"]).decode("utf-8", "replace")
                genres = sorted(set(GENRE.findall(track)))
                if key in src:  # older entry: only the genres were missing
                    src[key]["genres"] = genres
                    continue
                lic = LICENSE.findall(track)
                if not lic or lic[0].rstrip("/") + "/" != CC0:
                    print("skip (licence)", info["title"], lic[:1], flush=True)
                    continue
                dest = SRC / key
                if not dest.exists():
                    data = get(info["fileUrl"])
                    if len(data) > max_mb * 1e6:
                        continue
                    dest.write_bytes(data)
                src[key] = {
                    "key": key, "source": "Free Music Archive", "title": info["title"], "artist": info["artistName"],
                    "album": info.get("albumTitle"), "albumSlug": album, "genres": genres, "page": info["url"], "file": info["fileUrl"],
                    "license": "CC0 1.0", "licenseUrl": CC0, "licenseProof": info["url"], "checked": today(),
                }
                print("fma", album, "/", info["title"], flush=True)
                time.sleep(0.4)
            save_sources(src, ["fma"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--freepd", action="store_true")
    ap.add_argument("--fma", action="store_true")
    ap.add_argument("--max-mb", type=float, default=25)
    a = ap.parse_args()
    SRC.mkdir(parents=True, exist_ok=True)
    src = load_sources()
    if a.freepd or not a.fma:
        fetch_freepd(src, a.max_mb)
    if a.fma or not a.freepd:
        fetch_fma(src, a.max_mb)
    print(len(src), "songs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
