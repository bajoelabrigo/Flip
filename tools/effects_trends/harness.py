"""Offline check of the Stock trend effects: compiles every shader with a real OpenGL 3.3 core context
(moderngl) and draws a few moments of it over its card photo, the way the app binds the uniforms.

    py tools/effects_trends/harness.py [--mod fx_glitch] [--only id,id] [--sheet out.png] [--times 0.3,1,1.7,2.4]

For designing and reviewing quickly; the cards and previews Stock shows are rendered by the app (build.py).
A "requires": "face" effect gets a face in the middle of the frame here.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

import moderngl
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from kit import PARAM_LABELS, SAMPLES, param_defaults, photo_for, shader  # noqa: E402

VERT = """#version 330 core
in vec2 a_position;
in vec2 a_texCoord;
out vec2 v_texCoord;
void main() { v_texCoord = a_texCoord; gl_Position = vec4(a_position, 0.0, 1.0); }
"""

FACE = {"u_faceValid": 1.0, "u_faceCenterX": 0.5, "u_faceCenterY": 0.4, "u_faceRx": 0.12, "u_faceRy": 0.2,
        "u_faceAngle": 0.0}


def cover(path: Path, size) -> Image.Image:
    im = Image.open(path).convert("RGBA")
    w, h = size
    k = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def hex3(s: str):
    return tuple(int(s[i:i + 2], 16) / 255 for i in (1, 3, 5))


class Renderer:
    def __init__(self, size=(320, 180)):
        self.ctx = moderngl.create_standalone_context(require=330)
        self.size = size
        quad = np.array([-1, -1, 0, 1, 1, -1, 1, 1, -1, 1, 0, 0, 1, 1, 1, 0], "f4")  # y = 0 at the top
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

    def frames(self, prog, params: dict, photo: str, times, length: float = 3.0) -> list[Image.Image]:
        vao = self.ctx.vertex_array(prog, [(self.vbo, "2f 2f", "a_position", "a_texCoord")])
        self.texture(photo).use(0)
        if "u_currentTexture" in prog:
            prog["u_currentTexture"].value = 0
        if "u_resolution" in prog:
            prog["u_resolution"].value = self.size
        for k, v in {**FACE, **params}.items():
            if k in prog:
                prog[k].value = hex3(v) if isinstance(v, str) else float(v)
        out = []
        for t in times:
            for name, value in (("u_time", t), ("u_progress", min(t / length, 1.0))):
                if name in prog:
                    prog[name].value = float(value)
            self.fbo.use()
            self.fbo.clear(0, 0, 0, 0)
            vao.render(moderngl.TRIANGLE_STRIP)
            im = Image.frombytes("RGBA", self.size, self.fbo.read(components=4)).transpose(Image.FLIP_TOP_BOTTOM)
            bg = Image.new("RGBA", self.size, (0, 0, 0, 255))
            bg.alpha_composite(im)
            out.append(bg.convert("RGB"))
        vao.release()
        return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--mod", default="", help="only the families of this fx_*.py module")
    ap.add_argument("--sheet", default="")
    ap.add_argument("--times", default="0.25,0.8,1.4,2.0,2.6")
    args = ap.parse_args()
    only = {s for s in args.only.split(",") if s}
    if args.mod:
        families = importlib.import_module(args.mod).FAMILIES
    else:
        import designs
        families = designs.FAMILIES
    times = [float(x) for x in args.times.split(",")]
    r = Renderer()
    rows = []
    failed = 0
    for fam in families:
        for p in fam.params:
            if p.en not in PARAM_LABELS:
                print(f"{fam.key}: parameter label {p.en!r} is not translated by the app (kit.PARAM_LABELS)")
                failed += 1
        for v in fam.variants:
            if only and v.id not in only:
                continue
            photo = photo_for(fam, v)
            if not (SAMPLES / f"{photo}.jpg").exists():
                print(f"{v.id}: photo {photo} missing")
                failed += 1
                continue
            try:
                prog = r.compile(shader(fam, v))
            except Exception as e:  # noqa: BLE001
                failed += 1
                print(f"{v.id}: COMPILE FAILED\n{e}")
                continue
            rows.append((v.id, r.frames(prog, param_defaults(fam, v), photo, times, fam.preview)))
            prog.release()
    print(f"{len(rows)} ok, {failed} failed")
    if args.sheet and rows:
        tw, th = r.size
        label, per = 170, 16
        for page in range(0, len(rows), per):
            chunk = rows[page:page + per]
            sheet = Image.new("RGB", (label + tw * len(times), th * len(chunk)), (24, 24, 28))
            d = ImageDraw.Draw(sheet)
            for i, (vid, frames) in enumerate(chunk):
                d.text((4, i * th + th // 2 - 6), vid, fill=(230, 230, 230))
                for j, f in enumerate(frames):
                    sheet.paste(f, (label + j * tw, i * th))
            name = args.sheet if len(rows) <= per else args.sheet.replace(".png", f"_{page // per + 1}.png")
            sheet.save(name)
            print("sheet:", name)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
