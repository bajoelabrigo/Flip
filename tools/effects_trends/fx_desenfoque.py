"""Efectos › Tendencias, Desenfoque: blurs with a sharp area, directional and motion blurs, focus pulls, a square
blur, a blurred-background frame, blurs that close a clip, and sharpening (fix blur, sharp luma, auto enhance).

Every blur here is a single pass of at most 24 taps, mirrored at the edges (no dark rim), with Gaussian weights so
the outer taps do not leave ghosts."""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)
BLUR = Param("blur", "Blur", 0.0, 2.0, 1.0)
SIZE = Param("size", "Size", 0.3, 2.0, 1.0)

# Shared blur helpers (prepended to each body).
BLURS = r"""
// Disc blur of radius r (height units), 24 golden-angle taps, Gaussian weights, mirrored at the edges. A turn
// per pixel trades the tap pattern for a fine grain that the eye reads as softness.
vec3 softBlur(vec2 uv, float r) {
    if (r < 0.0005) return Sm(uv).rgb;
    vec3 s = vec3(0.0);
    float wsum = 0.0;
    float j = hash12(floor(uv * u_resolution) + 7.3) * TAU;
    for (int i = 0; i < 24; ++i) {
        float f = sqrt((float(i) + 0.5) / 24.0);
        float a = float(i) * 2.39996 + j;
        float w = exp(-2.2 * f * f);
        s += Sm(uv + vec2(cos(a), sin(a)) * f * r * vec2(1.0 / aspect(), 1.0)).rgb * w;
        wsum += w;
    }
    return s / wsum;
}
// Line blur along d (uv units, full length), 24 taps, Gaussian, jittered along the line.
vec3 lineBlur(vec2 uv, vec2 d) {
    vec3 s = vec3(0.0);
    float wsum = 0.0;
    float j = hash12(floor(uv * u_resolution) + 3.1) - 0.5;
    for (int i = 0; i < 24; ++i) {
        float f = (float(i) + 0.5 + j) / 24.0 - 0.5;
        float w = exp(-6.0 * f * f);
        s += Sm(uv + d * f).rgb * w;
        wsum += w;
    }
    return s / wsum;
}
"""

# ---------------------------------------------------------------------------------------------------------------
# A blur that leaves one area sharp: round (vignette), a band (tilt / depth) or the top edge (shadow). The sharp
# area breathes or drifts slowly; the blurred part can also go darker.
FOCUS_MASK = Family(
    key="blur_focus_mask", category="desenfoque", params=[INTENSITY, SPEED, BLUR, SIZE],
    photo="woman", tags=["desenfoque", "blur", "enfoque", "focus", "difuminar"],
    defines={"SHAPE": 0, "RADIUS": 0.17, "SOFT": 0.2, "ELLX": 1.25, "BLUR_R": 0.05, "DARK": 0.12,
             "BREATHE": 0.22, "PERIOD": 4.0, "ANGLE": 0.0, "DRIFT": 0.0},
    body=BLURS + r"""
float focusMask(vec2 uv, float t) {
    vec2 p = toP(uv);
    float wv = sin(t * TAU / PERIOD);
    if (SHAPE < 0.5) {                       // round sharp area in the middle
        float r = RADIUS * size * (1.0 + BREATHE * wv);
        return smoothstep(r, r + SOFT * size, length(p / vec2(ELLX, 1.0)));
    } else if (SHAPE < 1.5) {                // a sharp band through the middle (tilt shift)
        vec2 n = vec2(cos(ANGLE), sin(ANGLE));
        float d = abs(dot(p, n) - DRIFT * wv);
        float r = RADIUS * size * (1.0 + BREATHE * wv);
        return smoothstep(r, r + SOFT * size, d);
    }
    // the top edge: a shadow that comes down a little and goes back
    float h = RADIUS * size * (1.0 + BREATHE * wv);
    return 1.0 - smoothstep(0.0, h, uv.y);
}
void main() {
    vec4 src = S(v_texCoord);
    float t = u_time * speed;
    float m = focusMask(v_texCoord, t);
    vec3 col = softBlur(v_texCoord, BLUR_R * blur * intensity * m);
    col *=1.0 - DARK * pow(m, 1.3) * min(intensity, 1.2);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("desenfoque-de-vineta", "Desenfoque de viñeta", "Vignette blur", thumb=1.0,
                tags=["viñeta", "vignette"]),
        Variant("radio-de-la-vineta", "Radio de la viñeta", "Vignette radius", thumb=2.2,
                defines={"RADIUS": 0.24, "SOFT": 0.16, "BREATHE": 0.45, "PERIOD": 3.0, "DARK": 0.55},
                tags=["viñeta", "vignette", "radio", "radius"], photo="woman"),
        Variant("objetivo-de-camara", "Objetivo de cámara", "Camera lens", thumb=1.0,
                defines={"RADIUS": 0.22, "SOFT": 0.22, "ELLX": 1.0, "DARK": 0.62, "BREATHE": 0.12, "PERIOD": 2.5,
                         "BLUR_R": 0.045},
                tags=["lente", "lens", "oscuro", "dark", "objetivo"], photo="citynight"),
        Variant("desenfoque-oblicuo", "Desenfoque oblicuo", "Oblique blur", thumb=1.0,
                defines={"SHAPE": 1, "ANGLE": 0.3, "RADIUS": 0.09, "SOFT": 0.14, "BREATHE": 0.1, "DRIFT": 0.08,
                         "PERIOD": 5.0, "BLUR_R": 0.055},
                tags=["oblicuo", "tilt", "inclinado", "diagonal"], photo="woman"),
        Variant("desenfoque-de-profundidad", "Desenfoque de profundidad", "Depth blur", thumb=1.0,
                defines={"SHAPE": 1, "ANGLE": 1.5708, "RADIUS": 0.07, "SOFT": 0.22, "BREATHE": 0.2,
                         "DRIFT": 0.05, "PERIOD": 5.0, "BLUR_R": 0.04},
                tags=["profundidad", "depth", "tilt shift", "miniatura", "miniature"], photo="walk"),
        Variant("sombra-a", "Sombra A", "Shadow A", thumb=0.8,
                defines={"SHAPE": 2, "RADIUS": 0.35, "BREATHE": 0.25, "PERIOD": 3.0, "DARK": 0.92,
                         "BLUR_R": 0.02},
                tags=["sombra", "shadow", "borde", "edge"], photo="skater"),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# The picture smaller and sharp in the middle, over a blurred, darker copy of itself that drifts slowly.
BG_BLUR = Family(
    key="blur_background", category="desenfoque", params=[INTENSITY, SPEED, BLUR, SIZE],
    photo="woman", tags=["fondo", "background", "desenfoque", "blur", "marco"],
    defines={"SCALE": 0.66},
    body=BLURS + r"""
void main() {
    vec4 src = S(v_texCoord);
    float t = u_time * speed;
    float k = sat(intensity);
    // Background: zoomed, drifting, blurred, a little darker.
    vec2 buv = camUv(v_texCoord, vec2(0.5), 1.15 + 0.03 * sin(t * 0.9), 0.0, 0.015 * vec2(sin(t * 0.6), cos(t * 0.5)));
    vec3 bg = softBlur(buv, 0.05 * blur) * (1.0 - 0.25 * k);
    // Foreground card.
    float sc = mix(1.0, SCALE * size, k) * (1.0 + 0.015 * sin(t * 1.3));
    sc = min(sc, 1.0);
    vec2 fuv = (v_texCoord - 0.5) / sc + 0.5;
    vec4 fg = Sc(fuv);
    vec2 p = toP(v_texCoord);
    vec2 half_ = vec2(aspect() * 0.5, 0.5) * sc;
    float sh = 1.0 - smoothstep(0.0, 0.05, sdBox(p - vec2(0.0, 0.012), half_));
    bg *= 1.0 - 0.45 * sh * k;
    float edge = fillSd(sdBox(p, half_), 0.0015);
    vec3 col = mix(bg, fg.rgb, edge);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("desenfoque-de-fondo-basico", "Desenfoque de fondo básico", "Basic background blur", thumb=1.0,
                tags=["vertical", "horizontal", "relleno", "fill"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# A blurred, slightly cool picture with two square focus windows that roam and lock on: sharp inside, with
# white corner brackets.
FOCUS_BOXES = Family(
    key="blur_focus_boxes", category="desenfoque", params=[INTENSITY, SPEED, BLUR, SIZE, Param("color", "Colour", default="#ffffff")],
    photo="skater", tags=["enfoque", "focus", "analitico", "analytic", "cuadros", "squares", "detector"],
    body=BLURS + r"""
float bracket(vec2 p, vec2 c, float h) {
    vec2 q = abs(p - c);
    float frame = abs(sdBox(p - c, vec2(h)));
    float corner = step(h * 0.55, max(q.x, q.y)) * step(h * 0.6, min(q.x, q.y));
    return smoothstep(0.004, 0.0015, frame) * corner;
}
vec2 roam(float t, float seed) {
    // hops between random spots, easing into each one and resting there
    float i = floor(t), f = easeInOut(linstep(0.0, 0.45, fract(t)));
    vec2 a = hash22(vec2(i, seed)) - 0.5, b = hash22(vec2(i + 1.0, seed)) - 0.5;
    return mix(a, b, f) * vec2(aspect() * 0.62, 0.55);
}
void main() {
    vec4 src = S(v_texCoord);
    float t = u_time * speed * 0.8;
    float k = sat(intensity);
    vec2 p = toP(v_texCoord);
    vec3 bl = softBlur(v_texCoord, 0.045 * blur * intensity);
    bl = mix(bl, bl * vec3(0.8, 1.02, 1.05), 0.6 * k) * (1.0 - 0.2 * k);
    float inside = 0.0, lines = 0.0;
    for (int n = 0; n < 2; ++n) {
        float seed = float(n) * 13.7 + 1.0;
        vec2 c = roam(t + float(n) * 0.5, seed);
        float lock = easeOut(linstep(0.45, 0.6, fract(t + float(n) * 0.5)));
        float h = 0.13 * size * (1.25 - 0.25 * lock);
        inside = max(inside, fillSd(sdBox(p - c, vec2(h)), 0.003));
        lines = max(lines, bracket(p, c, h) * (0.6 + 0.4 * lock));
        lines = max(lines, smoothstep(0.003, 0.0, abs(sdBox(p - c, vec2(h)))) * 0.25);
    }
    vec3 col = mix(bl, src.rgb, inside);
    col = mix(col, color, lines * k);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("enfoque-analitico", "Enfoque analítico", "Analytic focus", thumb=1.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Directional blurs: a fixed angle that swells and settles, a hand-held camera blurred along its own motion, and
# a long sideways smear.
DIRECTIONAL = Family(
    key="blur_directional", category="desenfoque", params=[INTENSITY, SPEED, BLUR, Param("angle", "Angle", -180.0, 180.0, 0.0)],
    photo="skater", tags=["desenfoque", "blur", "movimiento", "motion", "direccion", "direction"],
    defines={"MODE": 0, "AMT": 0.11, "BASE": 0.15, "PERIOD": 2.0},
    body=BLURS + r"""
void main() {
    vec4 src = S(v_texCoord);
    float t = u_time * speed;
    float a = radians(angle);
    vec2 dir = vec2(cos(a), sin(a));
    vec2 uv = v_texCoord;
    vec2 d;
    if (MODE < 0.5) {
        // swells and settles once per period
        float amt = AMT * (BASE + (1.0 - BASE) * wave01(t, PERIOD));
        d = dir * amt;
    } else if (MODE < 1.5) {
        // hand-held: the camera wanders, blur follows its velocity
        vec2 o = shake2(t, 1.6) * 0.035;
        vec2 o2 = shake2(t + 0.05, 1.6) * 0.035;
        vec2 vel = (o2 - o) / 0.05;
        uv = camUv(uv, vec2(0.5), 1.1, shake2(t + 9.0, 1.2).x * 0.02 * intensity, o * intensity);
        d = vel * AMT + dir * AMT * BASE;
    } else {
        // a long smear that drifts sideways and back
        float w = wave01(t, PERIOD);
        uv = camUv(uv, vec2(0.5), 1.08, 0.0, vec2((w - 0.5) * 0.04 * intensity, 0.0));
        d = dir * AMT * (0.55 + 0.45 * w);
    }
    d *= blur * intensity / vec2(aspect(), 1.0);
    vec3 col = lineBlur(uv, d);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("desenfoque-de-direccion", "Desenfoque de dirección", "Directional blur", thumb=1.0,
                params={"angle": 30.0}, tags=["angulo", "angle"]),
        Variant("desenfoque-de-movimiento", "Desenfoque de movimiento", "Motion blur", thumb=1.4,
                defines={"MODE": 1, "AMT": 0.16, "BASE": 0.3}, tags=["camara", "camera", "mano", "handheld"]),
        Variant("dibujo-desenfoque", "Dibujo desenfoque", "Smear blur", thumb=1.0,
                defines={"MODE": 2, "AMT": 0.16, "PERIOD": 3.0}, tags=["barrido", "smear", "lateral", "sideways"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# A square box blur: 16 taps on a grid that turns into soft square blocks, its size breathing.
SQUARE = Family(
    key="blur_square", category="desenfoque", params=[INTENSITY, SPEED, BLUR],
    photo="woman", tags=["desenfoque", "blur", "cuadrado", "square", "caja", "box"],
    body=r"""
void main() {
    vec4 src = S(v_texCoord);
    float t = u_time * speed;
    float w = 0.03 * blur * intensity * (0.7 + 0.3 * sin(t * TAU / 3.0));   // box size, height units
    vec2 box = vec2(w / aspect(), w);
    // snap the box to a grid half its size: soft square blocks instead of a plain blur
    vec2 cell = box * 0.5;
    vec2 base = (floor(v_texCoord / max(cell, vec2(1e-5))) + 0.5) * cell;
    vec2 c = mix(v_texCoord, base, 0.55 * sat(intensity));
    vec3 s = vec3(0.0);
    for (int y = 0; y < 4; ++y)
        for (int x = 0; x < 4; ++x)
            s += Sm(c + (vec2(float(x), float(y)) / 3.0 - 0.5) * box).rgb;
    fragColor = vec4(s / 16.0, src.a);
}
""",
    variants=[
        Variant("desenfoque-cuadrado", "Desenfoque cuadrado", "Square blur", thumb=1.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Focus over time: a lens that racks out and snaps back (looping), and blurs that close the clip.
FOCUS_PULL = Family(
    key="blur_focus_pull", category="desenfoque", params=[INTENSITY, SPEED, BLUR],
    photo="skater", tags=["desenfoque", "blur", "enfoque", "focus"],
    defines={"MODE": 0, "R": 0.04, "PERIOD": 2.0},
    body=BLURS + r"""
void main() {
    vec4 src = S(v_texCoord);
    float t = u_time * speed;
    float amt;
    vec2 uv = v_texCoord;
    float fade = 0.0;
    if (MODE < 0.5) {
        // out of focus, snaps sharp with a small push in, holds, drifts out again
        float f = phase(t, PERIOD);
        float snap = easeOut(linstep(0.0, 0.18, f));
        float out_ = easeIn(linstep(0.6, 1.0, f));
        amt = max(1.0 - snap, out_);
        float push = 1.0 + 0.07 * intensity * (easeOutBack(linstep(0.0, 0.3, f)) * (1.0 - out_));
        uv = camUv(uv, vec2(0.5), push, 0.0, vec2(0.0));
    } else if (MODE < 1.5) {
        // sharp, then blurs out over the last part of the clip
        amt = easeInOut(linstep(0.55, 1.0, u_progress));
        fade = 0.15 * amt;
    } else {
        // blurs away across the clip until the picture is a soft wash
        amt = easeInOut(linstep(0.05, 0.9, u_progress));
        fade = 0.3 * amt;
    }
    float r = R * blur * intensity * amt;
    vec3 col = softBlur(uv, r);
    if (MODE > 1.5) col = mix(col, softBlur(uv, r * 2.2), sat(amt * 1.4 - 0.4));
    col = mix(col, vec3(luma(col)) * 0.6 + col * 0.4 + 0.08, fade * sat(intensity));
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("amplificar-enfoque", "Amplificar enfoque", "Focus boost", thumb=0.15,
                defines={"R": 0.035}, tags=["zoom", "golpe", "punch"]),
        Variant("final-borroso", "Final borroso", "Blurry ending", thumb=2.8,
                defines={"MODE": 1, "R": 0.06}, tags=["final", "ending", "cierre", "outro"]),
        Variant("desenfocar-para-borrar", "Desenfocar para borrar", "Blur to erase", thumb=2.2,
                defines={"MODE": 2, "R": 0.07}, tags=["borrar", "erase", "salida", "exit"], photo="woman"),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Sharpening: unsharp mask on colour or only on brightness, and an automatic enhance (levels, contrast,
# vibrance, a little sharpening).
SHARPEN = Family(
    key="blur_sharpen", category="desenfoque", params=[INTENSITY, Param("amount", "Amount", 0.0, 2.0, 1.0)],
    photo="face", tags=["nitidez", "sharpen", "enfocar", "detalle", "detail"],
    defines={"MODE": 0, "SHARP": 1.4, "RADIUS_PX": 1.6},
    body=r"""
vec3 ringBlur(vec2 uv, float rpx) {
    vec2 o = px() * rpx;
    vec3 s = S(uv).rgb * 0.25;
    for (int i = 0; i < 8; ++i) {
        float a = float(i) * TAU / 8.0;
        s += S(uv + vec2(cos(a), sin(a)) * o).rgb * (0.75 / 8.0);
    }
    return s;
}
void main() {
    vec4 src = S(v_texCoord);
    float k = intensity;
    float rpx = RADIUS_PX * max(u_resolution.y / 1080.0, 0.5);
    vec3 b = ringBlur(v_texCoord, rpx);
    vec3 det = src.rgb - b;
    vec3 col;
    if (MODE < 0.5) {
        // fix blur: strong unsharp mask with a little local contrast
        vec3 b2 = ringBlur(v_texCoord, rpx * 3.0);
        col = src.rgb + det * SHARP * amount * k + (src.rgb - b2) * 0.35 * amount * k;
    } else if (MODE < 1.5) {
        // sharp luma: only the brightness gets the detail (no colour fringes), a touch more contrast
        float d = luma(det);
        col = src.rgb + d * SHARP * amount * k;
        col = contrastColor(col, 1.0 + 0.08 * k);
    } else {
        // auto enhance: stretch levels, S-curve, vibrance, light sharpening
        vec3 c = src.rgb + det * 0.7 * amount * k;
        vec3 lv = (c - 0.03) / 0.94;
        c = mix(c, lv, k);
        vec3 sc = c * c * (3.0 - 2.0 * c);
        c = mix(c, sc, 0.35 * k);
        float mx = max(c.r, max(c.g, c.b)), mn = min(c.r, min(c.g, c.b));
        float satv = mx - mn;
        c = saturateColor(c, 1.0 + 0.45 * k * (1.0 - satv));
        c *= 1.0 + 0.04 * k;
        col = c;
    }
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[
        Variant("quitar-desenfoque", "Quitar desenfoque", "Remove blur", thumb=1.0,
                tags=["quitar desenfoque", "unblur", "nitido", "sharp"]),
        Variant("luma-nitido", "Luma nítido", "Sharp luma", thumb=1.0,
                defines={"MODE": 1, "SHARP": 1.6}, tags=["luma", "brillo", "brightness"], photo="man"),
        Variant("mejoramiento-automatico", "Mejoramiento automático", "Auto enhance", thumb=1.0,
                defines={"MODE": 2}, tags=["auto", "mejorar", "enhance", "color", "contraste", "contrast"],
                photo="beach"),
    ],
)

FAMILIES = [FOCUS_MASK, BG_BLUR, FOCUS_BOXES, DIRECTIONAL, SQUARE, FOCUS_PULL, SHARPEN]
