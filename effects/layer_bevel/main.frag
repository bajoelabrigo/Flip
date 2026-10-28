#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution; uniform float u_unitPx;
uniform float size; uniform float depth; uniform float angle; uniform vec3 highlight; uniform vec3 shadow;
uniform float opacity;
float unitPx() { return u_unitPx > 0.0 ? u_unitPx : 1.0; }

float softAlpha(vec2 uv, float r) {
    float sum = 0.0;
    for (int k = 0; k < 16; ++k) {
        float ang = 6.2831853 * float(k) / 16.0;
        sum += texture(u_currentTexture, uv + vec2(cos(ang), sin(ang)) * r / u_resolution).a;
    }
    return (sum / 16.0 + texture(u_currentTexture, uv).a) * 0.5;
}
void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    if (src.a <= 0.001) { fragColor = src; return; }
    float r = max(1.0, size * unitPx());
    vec2 e = vec2(r * 0.5) / u_resolution;
    float dx = softAlpha(v_texCoord + vec2(e.x, 0.0), r) - softAlpha(v_texCoord - vec2(e.x, 0.0), r);
    float dy = softAlpha(v_texCoord + vec2(0.0, e.y), r) - softAlpha(v_texCoord - vec2(0.0, e.y), r);
    vec3 n = normalize(vec3(-dx * depth * 4.0, dy * depth * 4.0, 1.0));
    vec3 l = normalize(vec3(cos(radians(angle)), sin(radians(angle)), 0.6));
    float shade = dot(n, l) - l.z;
    vec3 tint = shade > 0.0 ? highlight : shadow;
    float amt = clamp(abs(shade) * 2.0, 0.0, 1.0) * clamp(opacity, 0.0, 1.0);
    fragColor = vec4(mix(src.rgb, tint, amt), src.a);
}
