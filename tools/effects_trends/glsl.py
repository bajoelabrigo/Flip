"""The GLSL every Stock trend effect starts with: the uniforms the app binds and our own helpers.

Written for Flip Studio (no code from Drift's packages). A package's main.frag is HEADER + the variant's
#defines + its parameter uniforms + the family body, which defines main().

Conventions (src/engine/GlRuntime.cpp, setPackageUniforms):
  v_texCoord.y == 0 is the top of the frame; the clip arrives as a straight-alpha canvas layer.
  u_time is the clip's own time in seconds, u_progress runs 0..1 across the clip. Effects loop on u_time
  (they work on a clip of any length); u_progress is only for things that open or close a clip.
"""

HEADER = r"""#version 330 core
in vec2 v_texCoord;
out vec4 fragColor;

uniform sampler2D u_currentTexture;
uniform vec2 u_resolution;
uniform float u_time;              // seconds since the clip started
uniform float u_progress;          // 0..1 across the clip

const float PI = 3.14159265359;
const float TAU = 6.28318530718;

float sat(float x) { return clamp(x, 0.0, 1.0); }
vec3 sat3(vec3 x) { return clamp(x, 0.0, 1.0); }
float linstep(float a, float b, float x) { return clamp((x - a) / (b - a), 0.0, 1.0); }
float easeInOut(float t) { t = sat(t); return t * t * (3.0 - 2.0 * t); }
float easeIn(float t) { t = sat(t); return t * t * t; }
float easeOut(float t) { t = 1.0 - sat(t); return 1.0 - t * t * t; }
float easeOutBack(float t) { t = sat(t) - 1.0; return 1.0 + t * t * (2.70158 * t + 1.70158); }
float bump(float t) { return sin(PI * sat(t)); }

// Loops. `period` in seconds; phase() runs 0..1 and starts again.
float phase(float t, float period) { return fract(t / period); }
// A beat that hits at the start of each period and decays (1 on the hit, ~0 before the next).
float beat(float t, float period, float decay) { return exp(-phase(t, period) * period / max(decay, 0.001)); }
// Smooth 0..1..0 once per period.
float wave01(float t, float period) { return 0.5 - 0.5 * cos(TAU * phase(t, period)); }
// Steps: a value that changes `fps` times a second (for jittery, low frame rate looks).
float stepTime(float t, float fps) { return floor(t * fps) / fps; }

float aspect() { return u_resolution.x / max(u_resolution.y, 1.0); }
// Centred coordinates with square units: x in [-aspect/2, aspect/2], y in [-0.5, 0.5], y down.
vec2 toP(vec2 uv) { return (uv - 0.5) * vec2(aspect(), 1.0); }
vec2 fromP(vec2 p) { return p / vec2(aspect(), 1.0) + 0.5; }
mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }
vec2 px() { return 1.0 / max(u_resolution, vec2(1.0)); }

float insideUv(vec2 uv) {
    vec2 s = step(vec2(0.0), uv) * step(uv, vec2(1.0));
    return s.x * s.y;
}
vec4 S(vec2 uv) { return texture(u_currentTexture, uv); }
// Transparent off the frame (pieces that move, cards, panels).
vec4 Sc(vec2 uv) { return texture(u_currentTexture, uv) * insideUv(uv); }
// Mirrored past the edges: camera moves that must never show a border.
vec4 Sm(vec2 uv) { vec2 m = 1.0 - abs(1.0 - mod(uv, 2.0)); return texture(u_currentTexture, m); }
// The picture moved like a camera: zoom k (>1 closer) about c (uv), turned by a (radians), shifted by off
// (uv units). Mirrored at the edges.
vec2 camUv(vec2 uv, vec2 c, float k, float a, vec2 off) {
    vec2 p = (uv - c) * vec2(aspect(), 1.0);
    p = rot(-a) * p / max(k, 0.001);
    return p / vec2(aspect(), 1.0) + c - off;
}
vec4 cam(vec2 uv, vec2 c, float k, float a, vec2 off) { return Sm(camUv(uv, c, k, a, off)); }

// Straight-alpha source-over.
vec4 over(vec4 top, vec4 bot) {
    float oa = top.a + bot.a * (1.0 - top.a);
    if (oa <= 0.0001) return vec4(0.0);
    return vec4((top.rgb * top.a + bot.rgb * bot.a * (1.0 - top.a)) / oa, oa);
}
float luma(vec3 c) { return dot(c, vec3(0.2126, 0.7152, 0.0722)); }
vec3 screen(vec3 a, vec3 b) { return 1.0 - (1.0 - a) * (1.0 - b); }
vec3 overlayBlend(vec3 a, vec3 b) { return mix(2.0 * a * b, 1.0 - 2.0 * (1.0 - a) * (1.0 - b), step(0.5, a)); }
vec3 softLight(vec3 a, vec3 b) { return mix(2.0 * a * b + a * a * (1.0 - 2.0 * b),
                                           sqrt(max(a, 0.0)) * (2.0 * b - 1.0) + 2.0 * a * (1.0 - b), step(0.5, b)); }
// Adds light: `col` scaled by k, as a screen so whites do not clip hard.
vec3 addLight(vec3 base, vec3 col, float k) { return screen(base, sat3(col * k)); }
vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
    float d = q.x - min(q.w, q.y);
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + 1e-10)), d / (q.x + 1e-10), q.x);
}
vec3 hsv2rgb(vec3 c) {
    vec3 p = abs(fract(c.xxx + vec3(0.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
    return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}
vec3 hueShift(vec3 c, float h) { vec3 x = rgb2hsv(c); x.x = fract(x.x + h); return hsv2rgb(x); }
vec3 saturateColor(vec3 c, float s) { return mix(vec3(luma(c)), c, s); }
vec3 contrastColor(vec3 c, float k) { return (c - 0.5) * k + 0.5; }
float vignette(vec2 uv, float r, float soft) { vec2 p = toP(uv); return 1.0 - smoothstep(r, r + soft, length(p)); }

float hash11(float p) { p = fract(p * 0.1031); p *= p + 33.33; p *= p + p; return fract(p); }
float hash12(vec2 p) { vec3 q = fract(vec3(p.xyx) * 0.1031); q += dot(q, q.yzx + 33.33); return fract((q.x + q.y) * q.z); }
vec2 hash22(vec2 p) { vec3 q = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973)); q += dot(q, q.yzx + 33.33);
                      return fract((q.xx + q.yz) * q.zy); }
vec3 hash32(vec2 p) { vec3 q = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973)); q += dot(q, q.yxz + 33.33);
                      return fract((q.xxy + q.yzz) * q.zyx); }
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
// Smooth random walk in -1..1 (camera shakes): two noise octaves at frequency f.
vec2 shake2(float t, float f) {
    return vec2(vnoise(vec2(t * f, 3.7)) + 0.5 * vnoise(vec2(t * f * 2.1, 9.1)),
                vnoise(vec2(t * f, 17.3)) + 0.5 * vnoise(vec2(t * f * 2.1, 23.9))) / 0.75 - 1.0;
}

// Signed distances in toP space (negative inside).
float sdCircle(vec2 p, float r) { return length(p) - r; }
float sdBox(vec2 p, vec2 b) { vec2 d = abs(p) - b; return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0); }
float sdRoundBox(vec2 p, vec2 b, float r) { return sdBox(p, b - r) - r; }
float sdSegment(vec2 p, vec2 a, vec2 b) { vec2 pa = p - a, ba = b - a; float h = sat(dot(pa, ba) / dot(ba, ba));
                                          return length(pa - ba * h); }
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
// A heart standing up (point down, y down). Size ~ r.
float sdHeart(vec2 p, float r) {
    p.y = -p.y;
    p /= r;
    p.x = abs(p.x);
    p.y += 0.6;
    float d;
    if (p.y + p.x > 1.0) d = sqrt(dot(p - vec2(0.25, 0.75), p - vec2(0.25, 0.75))) - 0.35355;
    else d = sqrt(min(dot(p - vec2(0.0, 1.0), p - vec2(0.0, 1.0)), dot(p - 0.5 * max(p.x + p.y, 0.0),
                                                                        p - 0.5 * max(p.x + p.y, 0.0))))
             * sign(p.x - p.y);
    return d * r;
}
float sdFlower(vec2 p, float r, float petals) { float a = atan(p.y, p.x); return length(p) - r * (0.72 + 0.28 * cos(petals * a)); }
// Soft mask from a signed distance: 1 inside, 0 outside, edge `w` wide.
float fillSd(float d, float w) { return 1.0 - smoothstep(-w, w, d); }
// A glowing line from a signed distance: core width w, halo falling off over g.
float glowSd(float d, float w, float g) { return smoothstep(w, 0.0, abs(d)) + 0.6 * exp(-abs(d) / max(g, 1e-4)); }
// A four-point twinkle (cross with a soft core) at p (toP units), size r.
float twinkle(vec2 p, float r) {
    p /= max(r, 1e-4);
    float core = exp(-dot(p, p) * 6.0);
    float rays = exp(-abs(p.x) * 28.0) * exp(-abs(p.y) * 2.2) + exp(-abs(p.y) * 28.0) * exp(-abs(p.x) * 2.2);
    return core + 0.8 * rays;
}

// Blurs that stay inside one pass.
vec4 dirBlur(vec2 uv, vec2 d) {
    vec4 s = vec4(0.0);
    for (int i = 0; i < 16; ++i) s += S(uv + d * (float(i) / 15.0 - 0.5));
    return s / 16.0;
}
vec4 zoomBlur(vec2 uv, vec2 c, float k) {
    vec4 s = vec4(0.0);
    for (int i = 0; i < 16; ++i) s += S(c + (uv - c) * (1.0 - k * float(i) / 15.0));
    return s / 16.0;
}
vec4 spinBlur(vec2 uv, vec2 c, float a) {
    vec4 s = vec4(0.0);
    vec2 p = (uv - c) * vec2(aspect(), 1.0);
    for (int i = 0; i < 16; ++i) {
        vec2 q = rot(a * (float(i) / 15.0 - 0.5)) * p;
        s += S(q / vec2(aspect(), 1.0) + c);
    }
    return s / 16.0;
}
vec4 discBlur(vec2 uv, float r) {
    vec4 s = vec4(0.0);
    for (int i = 0; i < 24; ++i) {
        float a = float(i) * 2.39996, d = sqrt((float(i) + 0.5) / 24.0) * r;
        s += S(uv + vec2(cos(a), sin(a)) * d * vec2(1.0 / aspect(), 1.0));
    }
    return s / 24.0;
}
// A cheap glow: the bright parts of a disc blur.
vec3 brightGlow(vec2 uv, float r, float threshold) {
    vec3 s = vec3(0.0);
    for (int i = 0; i < 20; ++i) {
        float a = float(i) * 2.39996, d = sqrt((float(i) + 0.5) / 20.0) * r;
        vec3 c = S(uv + vec2(cos(a), sin(a)) * d * vec2(1.0 / aspect(), 1.0)).rgb;
        s += max(c - threshold, 0.0);
    }
    return s / 20.0 / max(1.0 - threshold, 0.05);
}
// Edges (Sobel on luma), 0..1.
float edges(vec2 uv, float spread) {
    vec2 o = px() * spread;
    float tl = luma(S(uv + vec2(-o.x, -o.y)).rgb), tc = luma(S(uv + vec2(0.0, -o.y)).rgb), tr = luma(S(uv + vec2(o.x, -o.y)).rgb);
    float ml = luma(S(uv + vec2(-o.x, 0.0)).rgb), mr = luma(S(uv + vec2(o.x, 0.0)).rgb);
    float bl = luma(S(uv + vec2(-o.x, o.y)).rgb), bc = luma(S(uv + vec2(0.0, o.y)).rgb), br = luma(S(uv + vec2(o.x, o.y)).rgb);
    float gx = (tr + 2.0 * mr + br) - (tl + 2.0 * ml + bl);
    float gy = (bl + 2.0 * bc + br) - (tl + 2.0 * tc + tr);
    return sat(length(vec2(gx, gy)));
}
"""
