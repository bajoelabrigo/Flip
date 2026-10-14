"""Write the new transition packages under transitions/.

Each one is a directory with transition.json and main.frag. They are all plain JSON + GLSL, so a
script keeps the boilerplate identical and the ids, orders and categories impossible to mistype.

    python tools/transitions/make_transitions.py [--repo <Flip checkout>]

Existing directories are left alone unless --force is passed.
"""

import argparse
import json
import os
import sys

# Ids, display names, categories, orders and the parameter list each shader declares.
SPECS = [
    ("slide_left", "Slide Left", "basic", 140, []),
    ("slide_right", "Slide Right", "basic", 141, []),
    ("slide_up", "Slide Up", "basic", 142, []),
    ("slide_down", "Slide Down", "basic", 143, []),
    ("spin", "Spin", "modern", 600, [
        {"identifier": "turns", "displayName": "Turns", "type": "float",
         "minValue": 0.25, "maxValue": 4.0, "defaultValue": 1.0}]),
    ("blur_dissolve", "Blur Dissolve", "modern", 610, [
        {"identifier": "blur", "displayName": "Blur Amount", "type": "float",
         "minValue": 0.0, "maxValue": 0.2, "defaultValue": 0.06}]),
    ("fold", "Fold", "modern", 620, [
        {"identifier": "angle", "displayName": "Fold Angle", "type": "float",
         "minValue": -0.6, "maxValue": 0.6, "defaultValue": 0.22}]),
    ("warp_slide", "Warp Slide", "modern", 630, [
        {"identifier": "amount", "displayName": "Warp", "type": "float",
         "minValue": 0.0, "maxValue": 1.0, "defaultValue": 0.45}]),
    ("glass_wipe", "Glass Wipe", "modern", 640, [
        {"identifier": "softness", "displayName": "Edge Softness", "type": "float",
         "minValue": 0.01, "maxValue": 0.3, "defaultValue": 0.05},
        {"identifier": "thickness", "displayName": "Glass Thickness", "type": "float",
         "minValue": 0.0, "maxValue": 0.3, "defaultValue": 0.1},
        {"identifier": "refraction", "displayName": "Refraction", "type": "float",
         "minValue": 0.0, "maxValue": 0.1, "defaultValue": 0.03}]),
    ("organic_wipe", "Organic Wipe", "modern", 650, [
        {"identifier": "roughness", "displayName": "Edge Roughness", "type": "float",
         "minValue": 0.0, "maxValue": 0.6, "defaultValue": 0.25},
        {"identifier": "scale", "displayName": "Detail", "type": "float",
         "minValue": 1.0, "maxValue": 12.0, "defaultValue": 5.0},
        {"identifier": "softness", "displayName": "Edge Softness", "type": "float",
         "minValue": 0.005, "maxValue": 0.2, "defaultValue": 0.05}]),
    ("torn_paper", "Torn Paper", "modern", 660, [
        {"identifier": "roughness", "displayName": "Tear Roughness", "type": "float",
         "minValue": 0.0, "maxValue": 1.0, "defaultValue": 0.5},
        {"identifier": "softness", "displayName": "Edge Softness", "type": "float",
         "minValue": 0.002, "maxValue": 0.08, "defaultValue": 0.01}]),
]

HEADER = """#version 330 core
in vec2 v_texCoord;
out vec4 fragColor;

uniform sampler2D u_currentTexture; // pass input 0
uniform sampler2D u_fromTexture;    // outgoing clip layer
uniform sampler2D u_toTexture;      // incoming clip layer
uniform vec2 u_resolution;
uniform float u_progress;           // 0..1 across the transition window

// Straight-alpha source-over. Clip layers are transparent outside the clip rect.
vec4 over(vec4 top, vec4 bot) {
    float oa = top.a + bot.a * (1.0 - top.a);
    if (oa <= 0.0001) return vec4(0.0);
    vec3 rgb = (top.rgb * top.a + bot.rgb * bot.a * (1.0 - top.a)) / oa;
    return vec4(rgb, oa);
}

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float valueNoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash21(i);
    float b = hash21(i + vec2(1.0, 0.0));
    float c = hash21(i + vec2(0.0, 1.0));
    float d = hash21(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

"""

SLIDE_BODY = """
// Both layers slide the same way across the frame. Whatever leaves the canvas is simply not
// drawn, so the project background fills the gap behind them -- which is what a slide should do.
vec4 sampleShifted(sampler2D tex, vec2 uv, vec2 shift) {{
    vec2 src = uv + shift;
    if (src.x < 0.0 || src.x > 1.0 || src.y < 0.0 || src.y > 1.0)
        return vec4(0.0);
    return texture(tex, src);
}}

void main() {{
    vec2 dir = vec2({dx}, {dy});
    vec2 shift = dir * u_progress;
    vec4 outgoing = sampleShifted(u_fromTexture, v_texCoord, shift);
    vec4 incoming = sampleShifted(u_toTexture, v_texCoord, shift - dir);
    fragColor = over(incoming, outgoing);
}}
"""

BODIES = {
    # dir_x, dir_y: +1 right / +1 down in screen terms, converted below.
    "slide_left": SLIDE_BODY.format(dx="1.0", dy="0.0"),
    "slide_right": SLIDE_BODY.format(dx="-1.0", dy="0.0"),
    "slide_up": SLIDE_BODY.format(dx="0.0", dy="1.0"),
    "slide_down": SLIDE_BODY.format(dx="0.0", dy="-1.0"),

    "spin": """
uniform float turns;

void main() {
    vec2 uv = v_texCoord;
    // Both layers rotate about the centre and the incoming one scales up out of the outgoing
    // one, so the frame never splits into two halves that do not agree on a centre.
    float eased = u_progress * u_progress * (3.0 - 2.0 * u_progress);
    float angle = eased * 6.2831853 * turns;
    float ca = cos(angle);
    float sa = sin(angle);
    // Aspect-corrected space, so a spin about the centre stays circular on a wide canvas.
    vec2 p = uv - 0.5;
    p.x *= u_resolution.x / max(u_resolution.y, 1.0);
    vec2 rotated = vec2(p.x * ca - p.y * sa, p.x * sa + p.y * ca);
    rotated.x /= u_resolution.x / max(u_resolution.y, 1.0);
    vec2 fromUv = rotated + 0.5;

    float zoom = mix(1.0, 0.45, eased);
    vec2 toUv = (rotated * zoom) + 0.5;

    vec4 outgoing = vec4(0.0);
    if (fromUv.x >= 0.0 && fromUv.x <= 1.0 && fromUv.y >= 0.0 && fromUv.y <= 1.0)
        outgoing = texture(u_fromTexture, fromUv);
    vec4 incoming = vec4(0.0);
    if (toUv.x >= 0.0 && toUv.x <= 1.0 && toUv.y >= 0.0 && toUv.y <= 1.0)
        incoming = texture(u_toTexture, toUv);

    // The outgoing layer fades as the incoming one takes over; a straight mix of two rotated
    // layers would show both at half opacity through the middle of the turn.
    outgoing *= 1.0 - eased;
    incoming *= eased;
    // Incoming on top: at full progress it has to be the only thing left.
    fragColor = over(incoming, outgoing);
}
""",

    "blur_dissolve": """
uniform float blur;

// Box blur in texture space. Sample count is fixed: the shader has to be a pure function of
// (from, to, progress, params), and a data-dependent loop would not compile portably anyway.
vec4 blurTexture(sampler2D tex, vec2 uv, float radius) {
    if (radius <= 0.0001)
        return texture(tex, uv);
    vec4 sum = vec4(0.0);
    const int TAPS = 12;
    float stepSize = 1.0 / float(TAPS);
    for (int i = 0; i < TAPS; ++i) {
        float a = float(i) * stepSize * 6.2831853;
        vec2 offset = vec2(cos(a), sin(a)) * radius;
        sum += texture(tex, uv + offset);
    }
    return sum / float(TAPS);
}

void main() {
    // Blur rises and falls across the window, so both ends are pin-sharp and only the middle is
    // soft -- that is what makes it read as a dissolve rather than a fade through fog.
    float amount = sin(u_progress * 3.14159265) * blur;
    vec4 outgoing = blurTexture(u_fromTexture, v_texCoord, amount);
    vec4 incoming = blurTexture(u_toTexture, v_texCoord, amount);
    float m = smoothstep(0.0, 1.0, u_progress);
    fragColor = over(mix(outgoing, incoming, m), vec4(0.0));
}
""",

    "fold": """
uniform float angle;

void main() {
    // A hard vertical fold travelling left to right: the outgoing half lifts away and the
    // incoming one is revealed underneath, with a highlight riding the crease.
    float edge = mix(-0.1, 1.1, u_progress);
    vec2 uv = v_texCoord;
    vec4 outgoing = texture(u_fromTexture, uv);
    vec4 incoming = texture(u_toTexture, uv);

    // Inside the folded-back band the outgoing layer is mirrored and darkened, like paper seen
    // from behind.
    float band = 0.12;
    float d = edge - uv.x;
    if (d > 0.0 && d < band) {
        float t = d / band;
        vec2 back = vec2(edge - d, uv.y);
        vec4 behind = texture(u_fromTexture, back);
        outgoing = mix(outgoing, behind * 0.75, 1.0 - t);
    } else if (uv.x > edge) {
        outgoing = vec4(0.0);
    }

    float crease = 1.0 - smoothstep(0.0, band * angle / 0.22, abs(d));
    incoming = mix(incoming, vec4(1.0, 1.0, 1.0, incoming.a), crease * 0.35);
    fragColor = over(incoming, outgoing);
}
""",

    "warp_slide": """
uniform float amount;

void main() {
    // The frame slides one way while a vertical wave bends the seam, so the cut reads as motion
    // rather than as a line crossing the shot.
    float eased = u_progress * u_progress * (3.0 - 2.0 * u_progress);
    vec2 uv = v_texCoord;
    float wave = sin(uv.y * 8.0 + eased * 6.2831853) * 0.04 * amount;

    vec2 shift = vec2(eased, 0.0);
    vec2 fromUv = vec2(uv.x + shift.x + wave, uv.y);
    vec2 toUv = vec2(uv.x + shift.x - 1.0 + wave, uv.y);

    vec4 outgoing = vec4(0.0);
    if (fromUv.x >= 0.0 && fromUv.x <= 1.0)
        outgoing = texture(u_fromTexture, fromUv);
    vec4 incoming = vec4(0.0);
    if (toUv.x >= 0.0 && toUv.x <= 1.0)
        incoming = texture(u_toTexture, toUv);
    fragColor = over(incoming, outgoing);
}
""",

    "glass_wipe": """
uniform float softness;
uniform float thickness;
uniform float refraction;

void main() {
    vec2 uv = v_texCoord;
    float edge = mix(-softness, 1.0 + softness, u_progress);
    float d = uv.x - edge;
    float ad = abs(d);

    // A band straddling the seam refracts what is under it, so the wipe looks like a pane of
    // glass dragging across the frame instead of a painted line.
    vec2 bent = uv;
    if (ad < thickness) {
        float t = 1.0 - ad / thickness;
        bent.x -= refraction * t;
        bent.y += refraction * t * sin(uv.y * 12.0);
    }

    vec4 outgoing = texture(u_fromTexture, bent);
    vec4 incoming = texture(u_toTexture, bent);
    float m = smoothstep(edge - softness, edge + softness, uv.x);
    vec4 mixed = mix(outgoing, incoming, m);

    // Bright rim on the leading edge, and a darker one trailing it: the two together read as
    // thickness. Kept additive on rgb only so alpha (the clip rect) is untouched.
    float rim = 1.0 - smoothstep(0.0, thickness, ad);
    float side = smoothstep(-thickness, 0.0, d);
    mixed.rgb += vec3(rim * (0.35 * (1.0 - side) + 0.12 * side));
    fragColor = mixed;
}
""",

    "organic_wipe": """
uniform float roughness;
uniform float scale;
uniform float softness;

void main() {
    vec2 uv = v_texCoord;
    // Noise, not a straight line: a fractal offset on the seam is what makes a wipe feel like a
    // reveal rather than a wipe.
    float n = (valueNoise(uv * scale) - 0.5);
    float n2 = (valueNoise(uv * scale * 2.7 + 11.0) - 0.5) * 0.5;
    float edge = mix(-roughness, 1.0 + roughness, u_progress) + (n + n2) * roughness;
    float m = 1.0 - smoothstep(edge - softness, edge + softness, uv.x);
    fragColor = mix(texture(u_fromTexture, uv), texture(u_toTexture, uv), m);
}
""",

    "torn_paper": """
uniform float roughness;
uniform float softness;

void main() {
    vec2 uv = v_texCoord;
    // High-frequency noise on a mostly vertical seam. The threshold is kept tight so the edge
    // reads as a tear; a wide band would just look like a soft wipe.
    float n = valueNoise(vec2(uv.y * 34.0, 3.0)) * 0.6
            + valueNoise(vec2(uv.y * 91.0, 17.0)) * 0.4;
    float jitter = (n - 0.5) * roughness * 0.22;
    float edge = mix(-0.05, 1.05, u_progress) + jitter;
    float m = 1.0 - smoothstep(edge - softness, edge + softness, uv.x);

    vec4 outgoing = texture(u_fromTexture, uv);
    vec4 incoming = texture(u_toTexture, uv);
    // A thin bright lip on the torn edge, as if the paper's fibre caught the light.
    float lip = 1.0 - smoothstep(0.0, 0.012 + softness, abs(uv.x - edge));
    vec4 mixed = mix(outgoing, incoming, m);
    mixed.rgb += vec3(lip * 0.5);
    fragColor = mixed;
}
""",
}


def manifest(spec):
    tid, name, category, order, params = spec
    return {
        "id": tid,
        "displayName": name,
        "category": category,
        "order": order,
        "parameters": params,
        "pipeline": {
            "intermediateBuffers": [],
            "passes": [
                {
                    "passIndex": 0,
                    "fragmentShader": "main.frag",
                    "inputs": [
                        {"type": "source_texture", "index": 0},
                        {"type": "source_texture", "index": 1},
                    ],
                    "output": {"type": "canvas"},
                }
            ],
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=r"C:\Users\bajoe\Downloads\FlipStudio\codigo\Flip")
    ap.add_argument("--force", action="store_true")
    opts = ap.parse_args()

    root = os.path.join(opts.repo, "transitions")
    if not os.path.isdir(root):
        print(f"no transitions directory at {root}", file=sys.stderr)
        return 1

    written = 0
    for spec in SPECS:
        tid = spec[0]
        d = os.path.join(root, tid)
        if os.path.isdir(d) and not opts.force:
            print(f"skip {tid} (exists)")
            continue
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "transition.json"), "w", encoding="utf-8") as fh:
            json.dump(manifest(spec), fh, indent=2)
            fh.write("\n")
        with open(os.path.join(d, "main.frag"), "w", encoding="utf-8") as fh:
            fh.write(HEADER + BODIES[tid].lstrip("\n"))
        print(f"wrote {tid}")
        written += 1

    print(f"{written} written, {len(SPECS)} in the set")
    return 0


if __name__ == "__main__":
    sys.exit(main())
