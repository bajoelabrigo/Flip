"""Render a transition's shader outside the app, as a contact sheet across its progress.

    py tools/transitions/preview.py transitions/fold from.png to.png out.png [steps]

It compiles main.frag with the uniforms the compositor sets (u_fromTexture, u_toTexture,
u_progress, u_resolution, plus each parameter's defaultValue from transition.json), so a shader
that does not compile, or runs backwards, shows up here without a full build. Texture row 0 is
the image's top row, as in the app. Needs moderngl and Pillow.
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


def render_frames(folder, a, b, steps):
    """The transition in `folder` from image a to image b, at `steps` evenly spaced progresses."""
    folder = Path(folder)
    meta = json.loads((folder / "transition.json").read_text(encoding="utf-8"))
    frag = (folder / "main.frag").read_text(encoding="utf-8")
    a = a.convert("RGBA")
    b = b.convert("RGBA").resize(a.size)
    w, h = a.size
    ctx = moderngl.create_standalone_context()
    prog = ctx.program(vertex_shader=VERT, fragment_shader=frag)
    quad = ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype="f4"))
    vao = ctx.vertex_array(prog, [(quad, "2f", "a_pos")])
    tex_a = ctx.texture((w, h), 4, a.tobytes())
    tex_b = ctx.texture((w, h), 4, b.tobytes())
    fbo = ctx.simple_framebuffer((w, h), components=4)

    def setu(name, value):
        if name in prog:
            prog[name].value = value

    setu("u_resolution", (float(w), float(h)))
    for p in meta.get("parameters", []):
        setu(p["identifier"], float(p["defaultValue"]))
    tex_a.use(0)
    tex_b.use(1)
    setu("u_fromTexture", 0)
    setu("u_toTexture", 1)
    setu("u_currentTexture", 0)

    frames = []
    for i in range(steps):
        setu("u_progress", i / (steps - 1))
        fbo.use()
        fbo.clear(0, 0, 0, 1)
        vao.render(moderngl.TRIANGLE_STRIP)
        frames.append(Image.frombytes("RGBA", (w, h), fbo.read(components=4))
                      .transpose(Image.FLIP_TOP_BOTTOM))
    ctx.release()
    return frames


def main():
    folder, src, dst, out = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]
    steps = int(sys.argv[5]) if len(sys.argv) > 5 else 7
    frames = render_frames(folder, Image.open(src), Image.open(dst), steps)
    w, h = frames[0].size
    sheet = Image.new("RGB", (w * steps, h))
    for i, img in enumerate(frames):
        sheet.paste(img.convert("RGB"), (i * w, 0))
    sheet.save(out)
    print(f"{folder.name}: {steps} frames -> {out}")


if __name__ == "__main__":
    main()
