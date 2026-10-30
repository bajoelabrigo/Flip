#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution; uniform float u_time; uniform float u_unitPx;
uniform float amount; uniform float size; uniform float complexity; uniform float evolution;
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
    vec2 px = v_texCoord * u_resolution / unitPx();
    float t = u_time * evolution;
    vec2 d = vec2(fbm(px / size, complexity, t), fbm(px / size + vec2(31.7, 11.3), complexity, t)) - 0.5;
    vec2 uv = v_texCoord + d * 2.0 * amount * unitPx() / u_resolution;
    fragColor = texture(u_currentTexture, uv);
}
