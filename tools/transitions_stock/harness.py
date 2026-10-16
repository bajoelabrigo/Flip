"""Offline check of the Stock transitions: compiles every shader with a real OpenGL 3.3 core context
(moderngl) and draws a few frames between two sample photos, the way the app binds them.

    py tools/transitions_stock/harness.py [--only id,id] [--family key] [--sheet out.png]

This is for designing and reviewing quickly; the cards and previews Stock shows are rendered by the
app itself (build.py).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import moderngl
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import designs  # noqa: E402
from kit import PAIRS, SAMPLES, param_defaults, shader  # noqa: E402

VERT = """#version 330 core
in vec2 a_position;
in vec2 a_texCoord;
out vec2 v_texCoord;
void main() { v_texCoord = a_texCoord; gl_Position = vec4(a_position, 0.0, 1.0); }
"""


def cover(path: Path, size) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    w, h = size
    k = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


class Renderer:
    def __init__(self, size=(480, 270)):
        self.ctx = moderngl.create_standalone_context(require=330)
        self.size = size
        quad = np.array([-1, -1, 0, 0, 1, -1, 1, 0, -1, 1, 0, 1, 1, 1, 1, 1], "f4")
        self.vbo = self.ctx.buffer(quad.tobytes())
        self.fbo = self.ctx.simple_framebuffer(size, components=4)
        self.tex = {}

    def texture(self, name: str):
        if name not in self.tex:
            im = cover(SAMPLES / f"{name}.jpg", self.size)
            t = self.ctx.texture(self.size, 4, im.tobytes())
            t.repeat_x = t.repeat_y = False
            t.filter = (moderngl.LINEAR, moderngl.LINEAR)
            self.tex[name] = t
        return self.tex[name]

    def compile(self, src: str):
        return self.ctx.program(vertex_shader=VERT, fragment_shader=src)

    def frames(self, prog, params: dict, pair, progresses) -> list[Image.Image]:
        vao = self.ctx.vertex_array(prog, [(self.vbo, "2f 2f", "a_position", "a_texCoord")])
        a, b = (self.texture(n) for n in pair)
        a.use(0)
        b.use(1)
        for name, unit in (("u_fromTexture", 0), ("u_toTexture", 1)):
            if name in prog:
                prog[name].value = unit
        if "u_resolution" in prog:
            prog["u_resolution"].value = self.size
        for k, v in params.items():
            if k in prog:
                prog[k].value = float(v)
        out = []
        for p in progresses:
            if "u_progress" in prog:
                prog["u_progress"].value = float(p)
            self.fbo.use()
            self.fbo.clear(0, 0, 0, 0)
            vao.render(moderngl.TRIANGLE_STRIP)
            data = self.fbo.read(components=4)
            im = Image.frombytes("RGBA", self.size, data)
            bg = Image.new("RGBA", self.size, (0, 0, 0, 255))
            bg.alpha_composite(im)
            out.append(bg.convert("RGB"))
        vao.release()
        return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--family", default="")
    ap.add_argument("--mod", default="", help="only the families of this fam_*.py module")
    ap.add_argument("--sheet", default="")
    ap.add_argument("--frames", default="0.08,0.25,0.4,0.5,0.6,0.75,0.92")
    args = ap.parse_args()
    only = {s for s in args.only.split(",") if s}
    fams = {s for s in args.family.split(",") if s}
    if args.mod:
        import importlib
        fams |= {f.key for f in importlib.import_module(args.mod).FAMILIES}
    progresses = [float(x) for x in args.frames.split(",")]
    r = Renderer((256, 144))
    rows = []
    failed = 0
    for fi, fam in enumerate(designs.FAMILIES):
        if fams and fam.key not in fams:
            continue
        for v in fam.variants:
            if only and v.id not in only:
                continue
            try:
                prog = r.compile(shader(fam, v))
            except Exception as e:  # noqa: BLE001
                failed += 1
                print(f"{v.id}: COMPILE FAILED\n{e}")
                continue
            pair = PAIRS[fi % len(PAIRS)]
            rows.append((v.id, r.frames(prog, param_defaults(fam, v), pair, progresses)))
            prog.release()
    print(f"{len(rows)} ok, {failed} failed")
    if args.sheet and rows:
        tw, th = r.size
        label = 150
        per = 18
        for page in range(0, len(rows), per):
            chunk = rows[page:page + per]
            sheet = Image.new("RGB", (label + tw * len(progresses), th * len(chunk)), (24, 24, 28))
            d = ImageDraw.Draw(sheet)
            for i, (vid, frames) in enumerate(chunk):
                d.text((4, i * th + th // 2 - 6), vid, fill=(230, 230, 230))
                for j, f in enumerate(frames):
                    sheet.paste(f, (label + j * tw, i * th))
            name = args.sheet if len(rows) <= per else args.sheet.replace(".png", f"_{page // per + 1}.png")
            sheet.save(name)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
