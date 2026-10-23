"""Efectos › Tendencias, IA: effects that follow the face (face scan) or the person (depth analysis).

Face effects ("requires": "face") read the oval the app binds after a face scan: u_faceCenterX/Y (uv, y down),
u_faceRx/Ry (radii in frame-width units) and u_faceAngle. Without a scan (u_faceValid < 0.5) they fall back to a
guess: the beauty ones smooth skin-coloured pixels over the whole frame, the mosaics cover the usual place of a
face (upper middle), so the Stock card still shows the effect.

Person effects ("requires": "depth") use driftDepth() from the engine prelude: the person is the near part.
Without a depth map (u_hasDepth < 0.5) the person is guessed as what differs from the background read at the
left and right sides of the frame, which holds up on the plain backgrounds of their cards.
"""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)

# ---------------------------------------------------------------------------------------------------------------
# Face

FACE_LIB = r"""
uniform float u_faceValid;
uniform float u_faceCenterX;
uniform float u_faceCenterY;
uniform float u_faceRx;
uniform float u_faceRy;
uniform float u_faceAngle;

bool haveFace() { return u_faceValid > 0.5; }
// Without a scan: where a face usually is in a portrait.
vec2 faceC() { return haveFace() ? vec2(u_faceCenterX, u_faceCenterY) : vec2(0.5, 0.4); }
vec2 faceR() { return haveFace() ? max(vec2(u_faceRx, u_faceRy), vec2(1e-3)) : vec2(0.15, 0.22); }
float faceA() { return haveFace() ? u_faceAngle : 0.0; }
// uv into the face's own frame: the oval is the unit circle, x across the face, y down the face.
vec2 faceFrame(vec2 uv) {
    vec2 q = vec2(uv.x, uv.y / aspect()) - vec2(faceC().x, faceC().y / aspect());
    return (rot(faceA()) * q) / faceR();
}
// An offset in frame-width units, turned into uv.
vec2 wOff(vec2 d) { return vec2(d.x, d.y * aspect()); }
// How much a colour looks like skin (a loose box in YCbCr).
float skinLike(vec3 c) {
    float y = luma(c);
    float cb = -0.169 * c.r - 0.331 * c.g + 0.5 * c.b;
    float cr = 0.5 * c.r - 0.419 * c.g - 0.081 * c.b;
    return smoothstep(0.015, 0.05, cr) * (1.0 - smoothstep(0.2, 0.26, cr))
         * smoothstep(-0.22, -0.16, cb) * (1.0 - smoothstep(0.0, 0.05, cb)) * smoothstep(0.1, 0.22, y);
}
"""

# Skin smoothing that keeps edges (each tap weighted by how alike its colour is), brighter eyes, a soft glow.
BEAUTY = Family(
    key="ia_beauty", category="ia", requires="face", photo="face",
    params=[INTENSITY, SPEED, Param("amount", "Amount", 0.0, 1.0, 0.85),
            Param("brightness", "Brightness", 0.0, 1.5, 0.5), Param("glow", "Glow", 0.0, 1.5, 1.0),
            Param("color", "Colour", default="#ffe6d6")],
    tags=["belleza", "beauty", "piel", "skin", "retoque", "retouch", "rostro", "face", "ia", "ai"],
    defines={"SIGMA": 28.0, "RADIUS": 0.075, "GLOW_K": 0.35, "SWEEP": 0.0, "LIFT": 0.04},
    body=FACE_LIB + r"""
vec3 smoothSkin(vec2 uv, float r, vec3 c0) {
    vec3 acc = c0;
    float wsum = 1.0;
    for (int i = 0; i < 20; ++i) {
        float a = float(i) * 2.39996, d = sqrt((float(i) + 0.5) / 20.0) * r;
        vec3 c = S(uv + wOff(vec2(cos(a), sin(a)) * d)).rgb;
        vec3 dc = c - c0;
        float w = exp(-dot(dc, dc) * SIGMA);
        acc += c * w;
        wsum += w;
    }
    return acc / wsum;
}
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float t = u_time * speed;
    vec2 e = faceFrame(uv);
    float fr = length(e);
    float skin = skinLike(src.rgb);
    float m, r;
    if (haveFace()) {
        float inFace = 1.0 - smoothstep(0.85, 1.2, fr);
        m = inFace * mix(0.55, 1.0, skin) + (1.0 - inFace) * skin * 0.35;   // a little on the neck too
        r = faceR().x * RADIUS;
    } else {
        m = skin * 0.8;
        r = 0.012;
    }
    vec3 col = src.rgb;
    vec3 sm = smoothSkin(uv, r, src.rgb);
    float k = sat(m * amount * intensity);
    col = mix(col, sm, k);
    // Skin a touch lighter and warmer.
    col = mix(col, softLight(col, color * 0.6 + 0.25) + LIFT, k * 0.6);
    // Eyes: a little more contrast and light, where the eyes sit inside the oval.
    if (haveFace()) {
        vec2 ex = vec2(abs(e.x) - 0.38, e.y + 0.22) / vec2(0.2, 0.11);
        float eyes = exp(-dot(ex, ex) * 1.5) * brightness * intensity;
        col = mix(col, sat3(contrastColor(col, 1.25) * 1.1), sat(eyes));
    }
    // A soft glow over the bright parts, breathing slowly.
    float breath = 0.8 + 0.2 * sin(t * TAU / 3.0);
    vec3 g = brightGlow(uv, 0.035, 0.55);
    col = addLight(col, g * color, GLOW_K * glow * breath * intensity);
    // A light that sweeps across the face now and then.
    if (SWEEP > 0.0) {
        float ph = phase(t, 2.8);
        vec2 p = toP(uv);
        float x = (p.x + p.y * 0.6) - mix(-1.4, 1.4, easeInOut(linstep(0.0, 0.55, ph)));
        float band = exp(-x * x * 40.0) * (haveFace() ? 1.0 - smoothstep(0.9, 1.4, fr) : 0.6);
        col = addLight(col, color * band, 0.35 * SWEEP * intensity);
        // and a few soft sparkles in the light
        vec2 q = p * 9.0 + vec2(0.0, -t * 0.4);
        vec2 cell = floor(q), f = fract(q) - 0.5;
        float h = hash12(cell);
        vec2 o = (hash22(cell + 3.1) - 0.5) * 0.6;
        float tw = 0.5 + 0.5 * sin(t * 4.0 + h * TAU);
        float sp = step(0.86, h) * twinkle(f - o, 0.18) * tw;
        col = addLight(col, vec3(1.0, 0.95, 0.9) * sp, 0.5 * SWEEP * glow * intensity);
    }
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[
        Variant("belleza", "Belleza", "Beauty", photo="fx-woman-08", thumb=1.0,
                tags=["suavizar", "smooth", "natural"]),
        Variant("embellecer-con-ia", "Embellecer con IA", "AI beautify", photo="fx-woman-05", thumb=0.9,
                defines={"SIGMA": 22.0, "RADIUS": 0.1, "GLOW_K": 0.55, "SWEEP": 1.0, "LIFT": 0.06},
                params={"amount": 1.0, "brightness": 0.8},
                tags=["embellecer", "beautify", "brillo", "glow"]),
    ],
)

# Pixelates or blurs only inside the face oval, following it.
MOSAIC = Family(
    key="ia_mosaic", category="ia", requires="face", photo="face",
    params=[INTENSITY, Param("size", "Size", 0.3, 3.0, 1.0), Param("softness", "Softness", 0.0, 1.0, 0.35),
            Param("spread", "Spread", 0.8, 2.0, 1.3)],
    tags=["mosaico", "mosaic", "censura", "censor", "ocultar", "hide", "rostro", "face", "privacidad", "privacy",
          "ia", "ai"],
    defines={"MODE": 0},
    body=FACE_LIB + r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float fr = length(faceFrame(uv)) / spread;
    float fw = 0.04 + 0.3 * softness;
    float m = (1.0 - smoothstep(1.0 - fw, 1.0 + fw * 0.5, fr)) * sat(intensity);
    if (m <= 0.001) { fragColor = src; return; }
    vec3 col;
    vec2 c = faceC();
    if (MODE < 0.5) {
        // Square blocks on a grid anchored to the face: the mosaic moves with it.
        float b = max(faceR().x * 0.2 * size, 0.004);
        vec2 q = vec2(uv.x - c.x, (uv.y - c.y) / aspect());
        vec2 cell = floor(q / b);
        vec3 acc = vec3(0.0);
        for (int j = 0; j < 2; ++j)
            for (int i = 0; i < 2; ++i) {
                vec2 s = (cell + vec2(0.25 + 0.5 * float(i), 0.25 + 0.5 * float(j))) * b;
                acc += S(c + vec2(s.x, s.y * aspect())).rgb;
            }
        col = acc * 0.25;
        // the faint seam between blocks of a classic mosaic
        vec2 f = fract(q / b);
        float seam = smoothstep(0.0, 0.06, f.x) * smoothstep(0.0, 0.06, f.y);
        col *= mix(0.92, 1.0, seam);
    } else {
        // A wide blur, sampled twice as wide on the outer ring so the oval reads as frosted.
        float r = faceR().y * 0.3 * size;
        vec3 a = discBlur(uv, r).rgb;
        vec3 b2 = discBlur(uv + vec2(0.37, 0.61) * px(), r * 0.6).rgb;
        col = mix(a, b2, 0.35);
    }
    fragColor = vec4(mix(src.rgb, col, m), src.a);
}
""",
    variants=[
        Variant("mosaico-clasico-de-ia", "Mosaico clásico de IA", "AI classic mosaic", photo="fx-woman-08", thumb=1.0,
                tags=["pixelar", "pixelate", "pixeles", "pixels"]),
        Variant("mosaico-de-desenfoque-de-ia", "Mosaico de desenfoque de IA", "AI blur mosaic", photo="fx-woman-07", thumb=1.0,
                defines={"MODE": 1}, tags=["desenfoque", "blur", "difuminar"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Person (depth)

# driftDepth() and u_hasDepth come from the engine's depth prelude (put after #version by the app).
PERSON_LIB = r"""
// The background at this height, read from the left and right sides of the frame (a clean plate guess).
vec3 plate(vec2 uv) {
    vec3 l = vec3(0.0), r = vec3(0.0);
    for (int i = 0; i < 3; ++i) {
        float y = clamp(uv.y + (float(i) - 1.0) * 0.05, 0.0, 1.0);
        l += S(vec2(0.02, y)).rgb;
        r += S(vec2(0.98, y)).rgb;
    }
    return mix(l, r, smoothstep(0.15, 0.85, uv.x)) / 3.0;
}
// 0..1: how much of the person is at uv. pl = plate() near uv (used only without a depth map).
float figureAt(vec2 uv, vec3 pl) {
    if (u_hasDepth > 0.5)
        return smoothstep(CUT - 0.08, CUT + 0.08, driftDepth(uv)) * insideUv(uv);
    // averaged over three taps down the frame: thin lines across the background (a wall seam, a horizon)
    // count less as the person
    vec2 o = vec2(0.0, 3.0 * px().y);
    float d = (2.0 * length(S(uv).rgb - pl) + length(S(uv - o).rgb - pl) + length(S(uv + o).rgb - pl)) * 0.25;
    float m = smoothstep(0.11, 0.23, d);
    m *= 1.0 - smoothstep(0.36, 0.47, abs(uv.x - 0.5));
    return m * insideUv(uv);
}
// The same, softened a little (fewer specks in the guess).
float figureSoft(vec2 uv, vec3 pl) {
    vec2 o = px() * 2.5;
    return (figureAt(uv, pl) * 2.0 + figureAt(uv + vec2(o.x, 0.0), pl) + figureAt(uv - vec2(o.x, 0.0), pl)
            + figureAt(uv + vec2(0.0, o.y), pl) + figureAt(uv - vec2(0.0, o.y), pl)) / 6.0;
}
// The person's halo: the mask spread over radius r (height units).
float figureHalo(vec2 uv, vec3 pl, float r) {
    float s = 0.0;
    for (int i = 0; i < 16; ++i) {
        float a = float(i) * 2.39996, d = sqrt((float(i) + 0.5) / 16.0) * r;
        s += figureAt(uv + vec2(cos(a) / aspect(), sin(a)) * d, pl);
    }
    return s / 16.0;
}
"""


# The person turned into a glowing white silhouette over a coloured, dimmed background.
FIGURE_GLOW = Family(
    key="ia_figure_glow", category="ia", requires="depth", photo="figure",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#3d6bff"), Param("glow", "Glow", 0.0, 1.5, 1.0),
            Param("spread", "Spread", 0.3, 2.5, 1.0)],
    tags=["resplandor", "glow", "silueta", "silhouette", "persona", "person", "figura", "figure", "ia", "ai"],
    defines={"CUT": 0.55},
    body=PERSON_LIB + r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float t = u_time * speed;
    vec3 pl = plate(uv);
    float m = figureSoft(uv, pl);
    float halo = figureHalo(uv, pl, 0.07 * spread);
    float pulse = 0.75 + 0.25 * sin(t * TAU * 0.6);
    // Background: the photo dimmed and washed in the colour, lighter towards the top.
    vec3 bg = mix(src.rgb * 0.35, color * mix(1.0, 0.55, uv.y), 0.7);
    // The figure: almost white, a trace of its own shading left inside.
    vec3 fig = mix(vec3(1.0), vec3(0.85, 0.9, 1.0) * (0.75 + 0.25 * luma(src.rgb)), 0.3);
    vec3 col = mix(bg, fig, m);
    col = addLight(col, mix(color, vec3(1.0), 0.45) * halo * (1.0 - m * 0.5), 1.3 * glow * pulse);
    float k = sat(intensity);
    fragColor = vec4(mix(src.rgb, sat3(col), k), src.a);
}
""",
    variants=[
        Variant("resplandor-de-la-figura", "Resplandor de la figura", "Figure glow", photo="fx-figure-01", thumb=1.0,
                tags=["blanco", "white", "neon"]),
    ],
)

# Copies of the person slide out to both sides, behind it, with a glowing outline.
CLONE = Family(
    key="ia_clone", category="ia", requires="depth", photo="figure",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#ffc46b"),
            Param("dist", "Distance", 0.3, 2.0, 1.0), Param("glow", "Glow", 0.0, 2.0, 1.0),
            Param("opacity", "Opacity", 0.1, 1.0, 0.92)],
    tags=["clon", "clone", "copias", "copies", "brillo", "glow", "persona", "person", "ia", "ai"],
    defines={"CUT": 0.55},
    body=PERSON_LIB + r"""
float rimAt(vec2 uv, vec3 pl, float m) {
    float s = 0.0;
    for (int i = 0; i < 8; ++i) {
        float a = float(i) * TAU / 8.0;
        s += figureAt(uv + vec2(cos(a) / aspect(), sin(a)) * 0.012, pl);
    }
    s /= 8.0;
    return smoothstep(0.2, 0.6, s) * (1.0 - smoothstep(0.3, 0.75, m));
}
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float t = u_time * speed;
    float ph = phase(t, 2.6);
    // out (0 .. 0.3), hold, back in (0.8 .. 1)
    float out_ = easeOutBack(linstep(0.0, 0.3, ph)) * (1.0 - easeInOut(linstep(0.8, 1.0, ph)));
    float pulse = 0.7 + 0.3 * sin(t * TAU * 1.2);
    vec3 pl = plate(uv);
    float m0 = figureSoft(uv, pl);
    vec3 col = src.rgb;
    for (int k = 0; k < 2; ++k) {
        float sx = k == 0 ? -1.0 : 1.0;
        vec2 uk = uv + vec2(sx * 0.2 * dist * out_, 0.0);
        vec3 pk = plate(uk);
        float mk = figureAt(uk, pk) * (1.0 - m0);
        vec3 ck = S(uk).rgb;
        ck = mix(ck, ck * color * 1.3, 0.35);                     // the copies take the colour a little
        col = mix(col, ck, mk * opacity * smoothstep(0.02, 0.15, out_));
        float rim = rimAt(uk, pk, figureAt(uk, pk)) * (1.0 - m0) * smoothstep(0.02, 0.15, out_);
        col = addLight(col, color * rim, 0.9 * pulse * glow);
    }
    // the person itself glows at the edge too
    col = addLight(col, color * rimAt(uv, pl, m0), 0.8 * pulse * glow);
    fragColor = vec4(mix(src.rgb, sat3(col), sat(intensity)), src.a);
}
""",
    variants=[
        Variant("clon-humano-brillando", "Clon humano brillando", "Glowing human clone", photo="fx-figure-05", thumb=1.0,
                tags=["duplicar", "duplicate", "trio"]),
    ],
)

# The person dissolves from the bottom into glowing particles that float up, then forms again.
DISSOLVE = Family(
    key="ia_dissolve", category="ia", requires="depth", photo="figure",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#3dffb0"),
            Param("density", "Density", 0.2, 2.0, 1.0), Param("glow", "Glow", 0.0, 2.0, 1.0),
            Param("size", "Size", 0.3, 2.0, 1.0)],
    tags=["disolver", "dissolve", "particulas", "particles", "luz", "light", "persona", "person", "ia", "ai"],
    defines={"CUT": 0.55},
    body=PERSON_LIB + r"""
float sparks(vec2 uv, float t, float scale, float rise, float seed, float level) {
    vec2 p = toP(uv) * scale;
    p.y += t * rise;
    vec2 cell = floor(p), f = fract(p) - 0.5;
    float h = hash12(cell + seed);
    if (h > 0.45 * density) return 0.0;
    vec2 o = (hash22(cell + seed * 1.3) - 0.5) * 0.7;
    float tw = 0.6 + 0.4 * sin(t * 6.0 + h * 40.0);
    // where this spark came from: lower down, where the body has already gone
    float back = (0.03 + 0.12 * hash12(cell + 5.7)) ;
    vec2 from_ = uv + vec2(sin(h * 30.0 + t) * 0.01, back);
    float body = figureAt(from_, plate(from_));
    float gone = step(level, from_.y + (fbm(from_ * vec2(aspect(), 1.0) * 6.0) - 0.5) * 0.25);
    float r = (0.14 + 0.14 * hash12(cell + 2.2)) * size;
    return smoothstep(r, r * 0.2, length(f - o)) * tw * body * gone;
}
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float t = u_time * speed;
    float ph = phase(t, 3.2);
    float level = 1.08 - 0.62 * easeInOut(linstep(0.0, 0.6, ph)) * (1.0 - easeInOut(linstep(0.78, 1.0, ph)));
    vec3 pl = plate(uv);
    float m = figureSoft(uv, pl);
    float n = fbm(uv * vec2(aspect(), 1.0) * 6.0);
    float y = uv.y + (n - 0.5) * 0.25;
    float gone = smoothstep(level - 0.01, level + 0.01, y);
    float edge = exp(-abs(y - level) * 45.0) * 1.3;
    // Background a little darker so the light shows; where the body has gone, the side colours fill in.
    vec3 bg = mix(src.rgb, pl, m) * 0.5;
    vec3 col = mix(src.rgb * mix(0.5, 1.0, m * (1.0 - gone)), bg, m * gone);
    col = addLight(col, color * edge * m * (1.0 - gone * 0.5), 1.6 * glow);
    float s = sparks(uv, t, 34.0, 0.9, 1.0, level) * 0.7 + sparks(uv, t, 20.0, 1.4, 7.0, level);
    col = addLight(col, mix(color, vec3(1.0), 0.35) * s, 1.4 * glow);
    fragColor = vec4(mix(src.rgb, sat3(col), sat(intensity)), src.a);
}
""",
    variants=[
        Variant("luz-que-se-disuelve", "Luz que se disuelve", "Dissolving light", photo="fx-figure-01", thumb=1.6,
                tags=["verde", "green", "desaparecer", "disappear"]),
    ],
)

# The person comes in from the side with a trail of fading copies; afterwards the trail echoes on each beat.
APPEAR = Family(
    key="ia_appear", category="ia", requires="depth", photo="woman",
    params=[INTENSITY, SPEED, Param("dist", "Distance", 0.3, 2.0, 1.0), Param("blur", "Blur", 0.0, 2.0, 1.0),
            Param("opacity", "Opacity", 0.0, 1.0, 0.55)],
    tags=["aparicion", "appear", "entrada", "intro", "estela", "trail", "persona", "person", "ia", "ai"],
    defines={"CUT": 0.55, "IN_TIME": 1.1},
    body=PERSON_LIB + r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float t = u_time * speed;
    float rev = easeOut(linstep(0.0, IN_TIME, t));
    float echo = t > IN_TIME ? beat(t - IN_TIME, 2.0, 0.35) * 0.55 : 0.0;
    float off = (1.0 - rev) * 0.38 * dist;
    float trail = max(1.0 - rev, echo);
    vec3 pl = plate(uv);
    float m0 = figureSoft(uv, pl);
    // The place of the person, filled with the background while it is not there yet.
    vec3 col = mix(src.rgb, pl, m0 * (1.0 - rev * rev));
    // The trail, farthest copy first.
    for (int k = 4; k >= 1; --k) {
        float fk = float(k);
        vec2 uk = uv + vec2(off + fk * 0.045 * dist * trail, 0.0);
        float mk = figureAt(uk, plate(uk));
        vec3 ck = mix(S(uk).rgb, vec3(luma(S(uk).rgb)) * vec3(0.9, 1.0, 1.1), 0.4);
        col = mix(col, ck, mk * opacity * (1.0 - fk * 0.2) * sat(trail * 1.6));
    }
    // The person: slides in and fades up, with a little motion blur while it moves.
    vec2 u0 = uv + vec2(off, 0.0);
    float mm = figureAt(u0, plate(u0));
    vec3 c0 = mix(S(u0).rgb, dirBlur(u0, vec2(0.06 * blur * (1.0 - rev), 0.0)).rgb, 1.0 - rev);
    col = mix(col, c0, mm * sat(rev * 1.4));
    fragColor = vec4(mix(src.rgb, sat3(col), sat(intensity)), src.a);
}
""",
    variants=[
        Variant("aparicion-humana-1", "Aparición humana 1", "Human appear 1", photo="fx-woman-04", thumb=0.55,
                tags=["fantasma", "ghost", "eco", "echo"]),
    ],
)

FAMILIES = [BEAUTY, MOSAIC, FIGURE_GLOW, CLONE, DISSOLVE, APPEAR]
