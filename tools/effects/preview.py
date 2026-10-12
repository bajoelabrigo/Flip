"""Run an effect package's main.frag outside the app, on a picture, with chosen parameters.

    py tools/effects/preview.py effects/color_hsl in.png out.png [key=value ...]

Compiles the shader with the uniforms the compositor sets (u_currentTexture plus each parameter,
defaulting to the manifest's defaultValue), so a shader that does not compile, or does the wrong
thing, shows up without a full build. Single-pass float-parameter effects only. Needs moderngl.
"""
import json
import sys
from pathlib import Path

import moderngl
import numpy as np
from PIL import Image

VERT = """#version 330 core
in vec2 a_pos;
out vec2 v_texCoord;
void main() {
    v_texCoord = vec2(a_pos.x * 0.5 + 0.5, 0.5 - a_pos.y * 0.5);
    gl_Position = vec4(a_pos, 0.0, 1.0);
}
"""


def render(folder, image, overrides=None):
    folder = Path(folder)
    meta = json.loads((folder / "effect.json").read_text(encoding="utf-8"))
    frag = (folder / "main.frag").read_text(encoding="utf-8")
    img = image.convert("RGBA")
    w, h = img.size
    ctx = moderngl.create_standalone_context()
    prog = ctx.program(vertex_shader=VERT, fragment_shader=frag)
    quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype="f4"))
    vao = ctx.vertex_array(prog, [(quad, "2f", "a_pos")])
    tex = ctx.texture((w, h), 4, img.tobytes())
    tex.use(0)
    if "u_currentTexture" in prog:
        prog["u_currentTexture"].value = 0
    values = {p["identifier"]: float(p["defaultValue"]) for p in meta.get("parameters", [])}
    values.update(overrides or {})
    for k, v in values.items():
        if k in prog:
            prog[k].value = float(v)
    fbo = ctx.simple_framebuffer((w, h), components=4)
    fbo.use()
    vao.render(moderngl.TRIANGLE_STRIP)
    out = Image.frombytes("RGBA", (w, h), fbo.read(components=4)).transpose(Image.FLIP_TOP_BOTTOM)
    ctx.release()
    return out


if __name__ == "__main__":
    folder, src, dst = sys.argv[1:4]
    overrides = {k: float(v) for k, v in (a.split("=") for a in sys.argv[4:])}
    render(folder, Image.open(src), overrides).save(dst)
    print("wrote", dst)
