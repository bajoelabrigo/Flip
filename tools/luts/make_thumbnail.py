"""effects/color_lut/thumbnail.png: the retouch reference photo (CC0) through the factory
Teal & Orange LUT, applied with the same trilinear lookup the app uses.

    py tools/luts/make_thumbnail.py
"""
import os

from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


def read_cube(path):
    size, rows = 0, []
    for line in open(path, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if not line:
            continue
        if line.startswith("LUT_3D_SIZE"):
            size = int(line.split()[1])
        elif line[0].isdigit() or line[0] in "-.":
            rows.append(tuple(float(v) for v in line.split()))
    return size, rows


def lookup(size, rows, r, g, b):
    n = size - 1
    f = [min(max(c, 0.0), 1.0) * n for c in (r, g, b)]
    i0 = [min(int(c), n - 1) for c in f]
    t = [c - i for c, i in zip(f, i0)]
    out = [0.0, 0.0, 0.0]
    for corner in range(8):
        d = (corner & 1, (corner >> 1) & 1, (corner >> 2) & 1)
        w = 1.0
        for k in range(3):
            w *= t[k] if d[k] else 1.0 - t[k]
        ri, gi, bi = i0[0] + d[0], i0[1] + d[1], i0[2] + d[2]
        row = rows[(bi * size + gi) * size + ri]
        for k in range(3):
            out[k] += w * row[k]
    return out


def main():
    size, rows = read_cube(os.path.join(ROOT, "effects", "color_lut", "luts", "teal_orange.cube"))
    photo = Image.open(os.path.join(ROOT, "resources", "retouch", "original.jpg")).convert("RGB")
    side = min(photo.size)
    photo = photo.crop(((photo.width - side) // 2, (photo.height - side) // 2,
                        (photo.width + side) // 2, (photo.height + side) // 2)).resize((256, 256), Image.LANCZOS)
    px = photo.load()
    for y in range(256):
        for x in range(256):
            r, g, b = (c / 255.0 for c in px[x, y])
            o = lookup(size, rows, r, g, b)
            px[x, y] = tuple(int(round(min(max(c, 0.0), 1.0) * 255)) for c in o)
    out = os.path.join(ROOT, "effects", "color_lut", "thumbnail.png")
    photo.convert("RGBA").save(out)
    print("wrote", os.path.abspath(out))


if __name__ == "__main__":
    main()
