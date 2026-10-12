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
