#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution; uniform float u_time; uniform float u_unitPx;
uniform float scale; uniform float complexity; uniform float contrast; uniform float brightness; uniform float evolution;
uniform float offsetX; uniform float offsetY; uniform float invert; uniform float blend;
float unitPx() { return u_unitPx > 0.0 ? u_unitPx : 1.0; }

float hash21(vec2 p) { p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
float vnoise(vec2 p) {
    vec2 i = floor(p); vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash21(i), hash21(i + vec2(1.0, 0.0)), u.x), mix(hash21(i + vec2(0.0, 1.0)), hash21(i + vec2(1.0, 1.0)), u.x), u.y);
}
float fbm(vec2 p, float octaves, float t) {
    float v = 0.0; float a = 0.5; vec2 shift = vec2(t * 0.37, -t * 0.23);
    for (int i = 0; i < 10; ++i) {
        if (float(i) >= octaves) break;
        v += a * vnoise(p + shift);
        p = p * 2.03 + vec2(17.1, 9.2);
        shift *= 1.7;
        a *= 0.5;
    }
    return v;
}

void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    vec2 px = v_texCoord * u_resolution / unitPx() + vec2(offsetX, offsetY);
    float n = fbm(px / max(scale, 1.0), complexity, u_time * evolution);
    n = clamp((n - 0.5) * contrast + 0.5 + brightness, 0.0, 1.0);
    if (invert > 0.5) n = 1.0 - n;
    fragColor = vec4(mix(vec3(n), src.rgb, clamp(blend, 0.0, 1.0)), mix(1.0, src.a, clamp(blend, 0.0, 1.0)));
}
