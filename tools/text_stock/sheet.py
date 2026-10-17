"""Contact sheets of the rendered cards, for review.

    py tools/text_stock/sheet.py [estilos|animaciones] [--only id,id] [--frames]

Writes <root>/<kind>-hoja-<n>.png (6 x 5 cards each, id under each card). --frames adds, for each
animation, three frames of its preview so the motion can be judged without playing it.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build import OUT  # noqa: E402

CELL = 256


def frames(preview: Path, n: int = 3) -> list[Image.Image]:
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    str(preview)], capture_output=True, text=True).stdout.strip() or 0)
        for i in range(n):
            t = dur * (i + 0.5) / n
            png = Path(tmp) / f"{i}.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(preview), "-frames:v", "1",
                            str(png)], capture_output=True)
            if png.exists():
                out.append(Image.open(png).convert("RGB").resize((CELL, CELL)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", nargs="?", default="estilos")
    ap.add_argument("--only", default="")
    ap.add_argument("--frames", action="store_true")
    a = ap.parse_args()
    only = set(filter(None, a.only.split(",")))
    folders = sorted(p for p in (OUT / a.kind).iterdir() if (p / "thumbnail.png").exists() and (not only or p.name in only))
    cols, rows = (4, 5) if a.frames else (6, 5)
    per = cols * rows
    for s in range(0, len(folders), per):
        chunk = folders[s:s + per]
        width = CELL * (4 if a.frames else 1)
        sheet = Image.new("RGB", (cols * width if not a.frames else width, rows * (CELL + 20) if not a.frames
                                  else len(chunk) * (CELL + 20)), "#808080")
        d = ImageDraw.Draw(sheet)
        for i, f in enumerate(chunk):
            x, y = ((i % cols) * width, (i // cols) * (CELL + 20)) if not a.frames else (0, i * (CELL + 20))
            sheet.paste(Image.open(f / "thumbnail.png").convert("RGB").resize((CELL, CELL)), (x, y))
            if a.frames and (f / "preview.mp4").exists():
                for j, fr in enumerate(frames(f / "preview.mp4")):
                    sheet.paste(fr, (x + CELL * (j + 1), y))
            d.text((x + 4, y + CELL + 3), f.name, fill="#ffffff")
        path = OUT / f"{a.kind}{'-frames' if a.frames else ''}-hoja-{s // per + 1}.png"
        sheet.save(path)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
