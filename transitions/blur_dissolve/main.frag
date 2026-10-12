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
