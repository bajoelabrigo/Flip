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
