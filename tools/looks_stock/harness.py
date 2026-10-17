"""Offline preview of the looks: runs the app's own effect shaders (effects/<id>/*.frag and their
pipelines) on the sample photos with moderngl, so a whole catalogue can be reviewed in seconds.

    py tools/looks_stock/harness.py [--only id,id] [--cat cine] --sheet out.png

The Stock cards themselves are rendered by the app (build.py).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import moderngl
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import designs  # noqa: E402
from build import CARD, sample_for, card  # noqa: E402
from fx import EFFECTS, FOLDERS  # noqa: E402

VERT = """#version 330 core
in vec2 a_position; in vec2 a_texCoord; out vec2 v_texCoord;
void main() { v_texCoord = a_texCoord; gl_Position = vec4(a_position, 0.0, 1.0); }
"""


class Runner:
    def __init__(self, size=(640, 360)):
        self.ctx = moderngl.create_standalone_context(require=330)
        self.size = size
        quad = np.array([-1, -1, 0, 0, 1, -1, 1, 0, -1, 1, 0, 1, 1, 1, 1, 1], "f4")
        self.vbo = self.ctx.buffer(quad.tobytes())
        self.progs = {}
        self.specs = {}

    def spec(self, cid):
        if cid not in self.specs:
            self.specs[cid] = json.loads((EFFECTS / FOLDERS[cid] / "effect.json").read_text(encoding="utf-8"))
        return self.specs[cid]

    def prog(self, cid, frag):
        key = (cid, frag)
        if key not in self.progs:
            src = (EFFECTS / FOLDERS[cid] / frag).read_text(encoding="utf-8")
            self.progs[key] = self.ctx.program(vertex_shader=VERT, fragment_shader=src)
        return self.progs[key]

    def tex(self, size, data=None):
        t = self.ctx.texture(size, 4, data, dtype="f2" if data is None else "f1")
        t.repeat_x = t.repeat_y = False
        t.filter = (moderngl.LINEAR, moderngl.LINEAR)
        return t

    def apply(self, cid, params, src):
        spec = self.spec(cid)
        pipe = spec["pipeline"]
        bufs = {}
        for b in pipe.get("intermediateBuffers", []):
            s = (max(1, int(self.size[0] * b.get("scale", 1.0))), max(1, int(self.size[1] * b.get("scale", 1.0))))
            bufs[b["id"]] = self.tex(s)
        out = None
        for ps in pipe["passes"]:
            prog = self.prog(cid, ps["fragmentShader"])
            inputs = ps.get("inputs") or [{"type": "source_texture"}]
            size0 = self.size
            for unit, inp in enumerate(inputs):
                t = src if inp["type"] == "source_texture" else bufs[inp["id"]]
                if unit == 0 and inp["type"] == "buffer":
                    size0 = t.size
                t.use(unit)
                name = "u_currentTexture" if unit == 0 else f"u_texture{unit}"
                if name in prog:
                    prog[name].value = unit
            target = bufs[ps["output"]["id"]] if ps["output"].get("type") == "buffer" else self.tex(self.size)
            fbo = self.ctx.framebuffer(color_attachments=[target])
            fbo.use()
            self.ctx.viewport = (0, 0, *target.size)
            for k, v in (("u_resolution", size0), ("u_time", 0.6), ("u_frameIndex", 18), ("u_progress", 0.5)):
                if k in prog:
                    prog[k].value = v
            for k, v in params.items():
                if k not in prog:
                    continue
                if isinstance(v, str) and v.startswith("#"):
                    prog[k].value = tuple(int(v[i:i + 2], 16) / 255 for i in (1, 3, 5))
                elif isinstance(v, (int, float, bool)):
                    prog[k].value = float(v)
            vao = self.ctx.vertex_array(prog, [(self.vbo, "2f 2f", "a_position", "a_texCoord")])
            vao.render(moderngl.TRIANGLE_STRIP)
            vao.release()
            fbo.release()
            if ps["output"].get("type") != "buffer":
                out = target
        for b in bufs.values():
            b.release()
        return out

    def render(self, look, photo: Image.Image) -> Image.Image:
        cur = self.tex(self.size, photo.convert("RGBA").resize(self.size).tobytes())
        for e in look.effects():
            if e["catalogId"] == "color.lut":
                continue  # the factory LUTs are checked in the app
            nxt = self.apply(e["catalogId"], e["parameters"], cur)
            cur.release()
            cur = nxt
        data = cur.read()
        arr = np.frombuffer(data, np.float16).reshape(self.size[1], self.size[0], 4) if cur.dtype == "f2" else \
            np.frombuffer(data, np.uint8).reshape(self.size[1], self.size[0], 4) / 255.0
        cur.release()
        return Image.fromarray((np.clip(arr[..., :3], 0, 1) * 255 + 0.5).astype(np.uint8))


def cover_img(path: Path, size) -> Image.Image:
    im = Image.open(path).convert("RGB")
    w, h = size
    k = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    x, y = (im.width - w) // 2, int((im.height - h) * 0.35)
    return im.crop((x, y, x + w, y + h))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--cat", default="")
    ap.add_argument("--sheet", required=True)
    args = ap.parse_args()
    only = {s for s in args.only.split(",") if s}
    cats = {s for s in args.cat.split(",") if s}
    looks = [l for l in designs.LOOKS if (not only or l.id in only) and (not cats or l.category in cats)]
    r = Runner()
    cards = []
    for l in looks:
        photo = cover_img(sample_for(l), r.size)
        cards.append((l.id, card(photo, r.render(l, photo))))
    per, cols, tw, th = 30, 5, 384, 216
    for page in range(0, len(cards), per):
        chunk = cards[page:page + per]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), (22, 22, 26))
        d = ImageDraw.Draw(sheet)
        for i, (lid, c) in enumerate(chunk):
            x, y = (i % cols) * tw, (i // cols) * (th + 18)
            sheet.paste(c.resize((tw, th)), (x, y))
            d.text((x + 4, y + th + 3), lid, fill=(225, 225, 225))
        name = args.sheet if len(cards) <= per else args.sheet.replace(".png", f"_{page // per + 1}.png")
        sheet.save(name)
    print(len(cards), "looks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
