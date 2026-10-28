#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution; uniform float u_unitPx;
uniform vec3 color; uniform float size; uniform float position; uniform float opacity;
float unitPx() { return u_unitPx > 0.0 ? u_unitPx : 1.0; }

void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    float r = max(0.0, size) * unitPx();
    if (r < 0.5) { fragColor = src; return; }
    // Grown (max) and shrunk (min) alpha over a disc of the stroke's radius.
    float grow = src.a;
    float shrink = src.a;
    for (int ring = 1; ring <= 4; ++ring) {
        float rr = r * float(ring) / 4.0;
        for (int k = 0; k < 24; ++k) {
            float ang = 6.2831853 * float(k) / 24.0;
            float aa = texture(u_currentTexture, v_texCoord + vec2(cos(ang), sin(ang)) * rr / u_resolution).a;
            grow = max(grow, aa);
            shrink = min(shrink, aa);
        }
    }
    float outside = clamp(grow - src.a, 0.0, 1.0);
    float inside = clamp(src.a - shrink, 0.0, 1.0);
    float pos = clamp(position, 0.0, 2.0);
    float s = pos < 0.5 ? outside : (pos < 1.5 ? max(outside, inside) * 0.5 + 0.5 * outside : inside);
    s *= clamp(opacity, 0.0, 1.0);
    if (pos >= 0.5) {
        // Inside (or centred) the stroke paints over the layer.
        vec3 rgb = mix(src.rgb, color, s);
        float a = max(src.a, s);
        fragColor = vec4(rgb, a);
        return;
    }
    float a = src.a + s * (1.0 - src.a);
    vec3 rgb = a > 1e-5 ? (src.rgb * src.a + color * s * (1.0 - src.a)) / a : vec3(0.0);
    fragColor = vec4(rgb, a);
}
