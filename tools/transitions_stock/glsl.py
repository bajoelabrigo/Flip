"""The GLSL every Stock transition starts with: the uniforms the app binds and our own helpers.

Written for Flip Studio (no code from Drift's packages or from gl-transitions). A package's main.frag is
HEADER + the variant's #defines + its parameter uniforms + the family body, which defines main().

Conventions (docs/gpu-transitions.md):
  v_texCoord.y == 0 is the top of the frame; both clips arrive as straight-alpha canvas layers.
  A transition is a pure function of (from, to, u_progress, parameters): no u_time anywhere.
"""

HEADER = r"""#version 330 core
in vec2 v_texCoord;
out vec4 fragColor;

uniform sampler2D u_fromTexture;   // outgoing clip (source 0)
uniform sampler2D u_toTexture;     // incoming clip (source 1)
uniform vec2 u_resolution;
uniform float u_progress;          // 0..1 across the transition window

const float PI = 3.14159265359;
const float TAU = 6.28318530718;

float sat(float x) { return clamp(x, 0.0, 1.0); }
float linstep(float a, float b, float x) { return clamp((x - a) / (b - a), 0.0, 1.0); }
float easeInOut(float t) { t = sat(t); return t * t * (3.0 - 2.0 * t); }
float easeIn(float t) { t = sat(t); return t * t * t; }
float easeOut(float t) { t = 1.0 - sat(t); return 1.0 - t * t * t; }
float easeOutBack(float t) { t = sat(t) - 1.0; return 1.0 + t * t * (2.70158 * t + 1.70158); }
// 0 at both ends, 1 in the middle: how strong an effect that peaks at the cut is.
float bump(float t) { return sin(PI * sat(t)); }
float peak(float t, float w) { return exp(-pow((t - 0.5) / w, 2.0)); }

float aspect() { return u_resolution.x / max(u_resolution.y, 1.0); }
// Centred coordinates with square units: x in [-aspect/2, aspect/2], y in [-0.5, 0.5], y down.
vec2 toP(vec2 uv) { return (uv - 0.5) * vec2(aspect(), 1.0); }
vec2 fromP(vec2 p) { return p / vec2(aspect(), 1.0) + 0.5; }
mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

// Straight-alpha source-over.
vec4 over(vec4 top, vec4 bot) {
    float oa = top.a + bot.a * (1.0 - top.a);
    if (oa <= 0.0001) return vec4(0.0);
    return vec4((top.rgb * top.a + bot.rgb * bot.a * (1.0 - top.a)) / oa, oa);
}
float insideUv(vec2 uv) {
    vec2 s = step(vec2(0.0), uv) * step(uv, vec2(1.0));
    return s.x * s.y;
}
vec4 A(vec2 uv) { return texture(u_fromTexture, uv); }
vec4 B(vec2 uv) { return texture(u_toTexture, uv); }
// The same, but transparent off the frame (for slides, cubes and pieces that move).
vec4 Ac(vec2 uv) { return texture(u_fromTexture, uv) * insideUv(uv); }
vec4 Bc(vec2 uv) { return texture(u_toTexture, uv) * insideUv(uv); }
vec4 mixc(vec4 a, vec4 b, float t) { return mix(a, b, sat(t)); }
vec4 tint(vec4 c, vec3 col, float k) { return vec4(mix(c.rgb, col, sat(k)), c.a); }
vec4 lighten(vec4 c, vec3 col, float k) { return vec4(c.rgb + col * k, c.a); }
float luma(vec3 c) { return dot(c, vec3(0.2126, 0.7152, 0.0722)); }

float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
float hash12(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
vec2 hash22(vec2 p) { vec3 q = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973)); q += dot(q, q.yzx + 33.33);
                      return fract((q.xx + q.yz) * q.zy); }
float vnoise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash12(i), hash12(i + vec2(1.0, 0.0)), f.x),
               mix(hash12(i + vec2(0.0, 1.0)), hash12(i + vec2(1.0, 1.0)), f.x), f.y);
}
float fbm(vec2 p) {
    float v = 0.0, a = 0.5;
    for (int i = 0; i < 5; ++i) { v += a * vnoise(p); p = p * 2.03 + vec2(17.1, 9.7); a *= 0.5; }
    return v;
}

// Signed distances in toP space (negative inside).
float sdCircle(vec2 p, float r) { return length(p) - r; }
float sdBox(vec2 p, vec2 b) { vec2 d = abs(p) - b; return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0); }
float sdRoundBox(vec2 p, vec2 b, float r) { return sdBox(p, b - r) - r; }
// Regular n-gon with apothem r, a vertex pointing up.
float sdPoly(vec2 p, float r, float n) {
    float seg = TAU / n;
    float a = mod(atan(p.x, -p.y), seg) - seg * 0.5;
    return length(p) * cos(a) - r;
}
// n-pointed star: outer radius r, inner radius r * m.
float sdStar(vec2 p, float r, float n, float m) {
    float an = PI / n;
    float a = mod(atan(p.x, -p.y), 2.0 * an) - an;
    vec2 q = length(p) * vec2(cos(a), abs(sin(a)));
    vec2 t = vec2(r, 0.0), v = vec2(r * m * cos(an), r * m * sin(an));
    vec2 pa = q - t, ba = v - t;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    float d = length(pa - ba * h);
    return (ba.x * pa.y - ba.y * pa.x) > 0.0 ? -d : d;
}
// A heart: a square stood on its corner with two circles on its upper sides. Size ~ r.
float sdHeart(vec2 p, float r) {
    p.y -= r * 0.18;
    float s = r * 0.62;
    vec2 q = rot(PI * 0.25) * p;
    float sq = sdBox(q, vec2(s));
    float k = s * 0.7071;
    float c1 = length(p - vec2(-k, -k)) - s;
    float c2 = length(p - vec2(k, -k)) - s;
    return min(sq, min(c1, c2));
}
float sdCross(vec2 p, float r) {
    return min(sdBox(p, vec2(r, r * 0.34)), sdBox(p, vec2(r * 0.34, r)));
}
float sdFlower(vec2 p, float r) {
    float a = atan(p.y, p.x);
    return length(p) - r * (0.78 + 0.22 * cos(6.0 * a));
}
float sdMoon(vec2 p, float r) {
    return max(length(p) - r, -(length(p - vec2(r * 0.42, -r * 0.18)) - r * 0.8));
}
// Soft mask from a signed distance: 1 inside, 0 outside, edge `w` wide.
float fillSd(float d, float w) { return 1.0 - smoothstep(-w, w, d); }

// Blurs that stay inside one pass: taps along a direction or towards a centre.
vec4 dirBlurA(vec2 uv, vec2 d) {
    vec4 s = vec4(0.0);
    for (int i = 0; i < 16; ++i) s += A(uv + d * (float(i) / 15.0 - 0.5));
    return s / 16.0;
}
vec4 dirBlurB(vec2 uv, vec2 d) {
    vec4 s = vec4(0.0);
    for (int i = 0; i < 16; ++i) s += B(uv + d * (float(i) / 15.0 - 0.5));
    return s / 16.0;
}
vec4 zoomBlurA(vec2 uv, vec2 c, float k) {
    vec4 s = vec4(0.0);
    for (int i = 0; i < 16; ++i) s += A(c + (uv - c) * (1.0 - k * float(i) / 15.0));
    return s / 16.0;
}
vec4 zoomBlurB(vec2 uv, vec2 c, float k) {
    vec4 s = vec4(0.0);
    for (int i = 0; i < 16; ++i) s += B(c + (uv - c) * (1.0 - k * float(i) / 15.0));
    return s / 16.0;
}
vec4 discBlurA(vec2 uv, float r) {
    vec4 s = vec4(0.0);
    for (int i = 0; i < 24; ++i) {
        float a = float(i) * 2.39996, d = sqrt((float(i) + 0.5) / 24.0) * r;
        s += A(uv + vec2(cos(a), sin(a)) * d * vec2(1.0 / aspect(), 1.0));
    }
    return s / 24.0;
}
vec4 discBlurB(vec2 uv, float r) {
    vec4 s = vec4(0.0);
    for (int i = 0; i < 24; ++i) {
        float a = float(i) * 2.39996, d = sqrt((float(i) + 0.5) / 24.0) * r;
        s += B(uv + vec2(cos(a), sin(a)) * d * vec2(1.0 / aspect(), 1.0));
    }
    return s / 24.0;
}
"""
