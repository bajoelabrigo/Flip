#version 330 core
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
    // Incoming behind the seam (left of it), outgoing ahead, the way wipe_left reads.
    float m = 1.0 - smoothstep(edge - softness, edge + softness, uv.x);
    vec4 mixed = mix(outgoing, incoming, m);

    // Bright rim on the leading edge, and a darker one trailing it: the two together read as
    // thickness. Kept additive on rgb only so alpha (the clip rect) is untouched.
    float rim = 1.0 - smoothstep(0.0, thickness, ad);
    float side = smoothstep(-thickness, 0.0, d);
    mixed.rgb += vec3(rim * (0.35 * (1.0 - side) + 0.12 * side));
    fragColor = mixed;
}
