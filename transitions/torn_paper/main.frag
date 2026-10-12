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
