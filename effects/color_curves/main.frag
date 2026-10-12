#version 330 core
in vec2 v_texCoord;
out vec4 fragColor;
uniform sampler2D u_currentTexture;
uniform float l0;
uniform float l1;
uniform float l2;
uniform float l3;
uniform float l4;
uniform float r0;
uniform float r1;
uniform float r2;
uniform float r3;
uniform float r4;
uniform float g0;
uniform float g1;
uniform float g2;
uniform float g3;
uniform float g4;
uniform float b0;
uniform float b1;
uniform float b2;
uniform float b3;
uniform float b4;
// A smooth curve through five points at x = 0, .25, .5, .75 and 1 (Catmull-Rom, with tangents
// limited so the curve stays between its neighbours and never folds back).
float curve(float x, float p0, float p1, float p2, float p3, float p4) {
    float pts[5] = float[5](p0, p1, p2, p3, p4);
    x = clamp(x, 0.0, 1.0);
    float seg = min(floor(x * 4.0), 3.0);
    int i = int(seg);
    float t = x * 4.0 - seg;
    float y0 = pts[i];
    float y1 = pts[i + 1];
    float m0 = i > 0 ? (pts[i + 1] - pts[i - 1]) * 0.5 : (y1 - y0);
    float m1 = i < 3 ? (pts[i + 2] - pts[i]) * 0.5 : (y1 - y0);
    float lim = abs(y1 - y0) * 3.0;
    m0 = clamp(m0, -lim, lim);
    m1 = clamp(m1, -lim, lim);
    float t2 = t * t, t3 = t2 * t;
    return clamp((2.0 * t3 - 3.0 * t2 + 1.0) * y0 + (t3 - 2.0 * t2 + t) * m0
                 + (-2.0 * t3 + 3.0 * t2) * y1 + (t3 - t2) * m1, 0.0, 1.0);
}

void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    vec3 c = src.rgb;
    c = vec3(curve(c.r, l0, l1, l2, l3, l4), curve(c.g, l0, l1, l2, l3, l4), curve(c.b, l0, l1, l2, l3, l4));
    c = vec3(curve(c.r, r0, r1, r2, r3, r4), curve(c.g, g0, g1, g2, g3, g4), curve(c.b, b0, b1, b2, b3, b4));
    fragColor = vec4(c, src.a);
}
