"""Write preview_strip.png for transitions that lack one, without building tools/transitionthumbs.

    py tools/transitions/make_strips.py [id ...]

The base pictures are lifted from crossfade's own strip (its first cell is the outgoing image,
its last the incoming one), so new strips match the existing ones. Output follows
transitionthumbs: 12 square 128px cells, quantised to a 128-colour palette. With no ids, every
transition folder without a strip gets one. Rendering goes through preview.py's shader runner.
"""
import sys
from pathlib import Path

from PIL import Image

from preview import render_frames

ROOT = Path(__file__).resolve().parents[2] / "transitions"
SIZE, FRAMES, COLORS = 128, 12, 128


def main():
    ref = Image.open(ROOT / "crossfade" / "preview_strip.png").convert("RGBA")
    a = ref.crop((0, 0, SIZE, SIZE))
    b = ref.crop((ref.width - SIZE, 0, ref.width, SIZE))
    ids = sys.argv[1:] or [p.name for p in sorted(ROOT.iterdir())
                           if p.is_dir() and not (p / "preview_strip.png").exists()]
    for tid in ids:
        cells = render_frames(ROOT / tid, a, b, FRAMES)
        strip = Image.new("RGB", (SIZE * FRAMES, SIZE))
        for i, cell in enumerate(cells):
            strip.paste(cell.convert("RGB"), (i * SIZE, 0))
        strip.quantize(colors=COLORS, method=Image.Quantize.MEDIANCUT).save(
            ROOT / tid / "preview_strip.png", optimize=True)
        print("wrote", tid)


if __name__ == "__main__":
    main()
