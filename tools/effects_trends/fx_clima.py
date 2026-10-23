"""Efectos › Tendencias, Partículas y brillos (segunda mitad): mariposas que brillan, niebla y humo, lluvia.

Three families: glowing butterflies drawn procedurally (two wing lobes that flap), fog/smoke made of drifting
warped fbm, and rain as streaks in three depth layers (with lightning for the storm)."""

import math

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)

# ---------------------------------------------------------------------------------------------------------------
# Butterflies. MODE 0: a few big ones flying across the frame. MODE 1: a burst from the middle that repeats.
BUTTERFLIES = Family(
    key="clima_butterflies", category="particulas",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#eaf6ff"), Param("glowcol", "Colour B", default="#7fd4ff"),
            Param("size", "Size", 0.4, 2.0, 1.0), Param("density", "Density", 0.2, 2.0, 1.0),
            Param("glow", "Glow", 0.0, 2.0, 1.0)],
    photo="woman", tags=["mariposa", "mariposas", "butterfly", "butterflies", "brillo", "glow", "magia", "magic"],
    defines={"MODE": "0"},
    body=r"""
float sdEll(vec2 p, vec2 r) { return (length(p / r) - 1.0) * min(r.x, r.y); }

// One butterfly in its own units (about 1 across), y down, head up. flap 1 = wings open, ~0.1 = edge on.
// Returns x = body and wings, y = rim, z = halo.
vec3 butterfly(vec2 q, float flap) {
    float fl = max(flap, 0.12);
    vec2 w = vec2(abs(q.x) / fl, q.y);
    // Upper wing leans up and out, lower wing smaller and down; blended into one shape.
    float d1 = sdEll(rot(0.65) * (w - vec2(0.40, -0.16)), vec2(0.40, 0.29));
    float d2 = sdEll(rot(-0.7) * (w - vec2(0.27, 0.22)), vec2(0.25, 0.18));
    float k = 0.08, hh = sat(0.5 + 0.5 * (d2 - d1) / k);
    float d = mix(d2, d1, hh) - k * hh * (1.0 - hh);
    d *= mix(0.55, 1.0, fl);
    float wing = fillSd(d, 0.025);
    // Translucent near the body, bright toward the tips and along the edge.
    float grad = 0.35 + 0.65 * smoothstep(0.05, 0.75, length(w));
    float edge = smoothstep(0.07, 0.0, -d) * wing;
    float spot = fillSd(length(w - vec2(0.52, -0.28)) - 0.07, 0.03);
    float body = fillSd(sdSegment(q, vec2(0.0, -0.26), vec2(0.0, 0.34)) - 0.04, 0.02);
    float ant = smoothstep(0.02, 0.0, min(sdSegment(q, vec2(0.0, -0.26), vec2(-0.13, -0.55)),
                                        sdSegment(q, vec2(0.0, -0.26), vec2(0.13, -0.55))));
    float shape = max(wing * grad * (1.0 - 0.45 * spot), max(body, ant * 0.8));
    float halo = exp(-max(d, 0.0) / 0.16) * 0.8;
    return vec3(shape, edge, halo);
}

vec3 drawOne(vec2 p, vec2 pos, float sz, float ang, float flap, float a) {
    vec2 q = rot(ang) * (p - pos) / max(sz, 1e-4);
    if (dot(q, q) > 9.0) return vec3(0.0);
    return butterfly(q, flap) * a;
}

void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    float A = aspect();
    vec3 acc = vec3(0.0);   // shape, rim, halo
    vec3 sparks = vec3(0.0);
#if MODE == 0
    for (int i = 0; i < 12; ++i) {
        if (float(i) >= 6.0 * density) break;
        float fi = float(i);
        float h1 = hash11(fi * 7.31 + 1.0), h2 = hash11(fi * 3.17 + 5.0), h3 = hash11(fi * 11.7 + 2.0);
        float dir = (i % 2 == 0) ? 1.0 : -1.0;
        float span = A + 0.7;
        float v = 0.05 + 0.05 * h2;
        float x = (fract(h1 + t * v / span) * span - span * 0.5) * dir;
        float y = (h3 - 0.5) * 0.75 + 0.07 * sin(t * 1.3 + fi * 2.1);
        float depth = 0.55 + 0.45 * fract(h1 * 5.3 + h2);
        float sz = (0.055 + 0.07 * depth) * size;
        float flap = 0.15 + 0.85 * abs(cos(t * (5.0 + 3.0 * h2) + fi));
        float ang = 0.35 * dir + 0.25 * sin(t * 1.3 + fi * 2.1 + 1.0);
        vec3 b = drawOne(p, vec2(x, y), sz, ang, flap, depth);
        acc = max(acc, b);
        // Glitter falling from each one.
        for (int k = 0; k < 3; ++k) {
            float fk = float(k);
            float age = fract(t * 0.8 + fk / 3.0 + h1);
            vec2 sp = vec2(x - dir * age * 0.12, y + age * 0.12 + 0.05 * (hash11(fi + fk * 3.1) - 0.5));
            sparks += glowcol * twinkle(p - sp, 0.012 * size * depth) * (1.0 - age) * depth;
        }
    }
#else
    vec2 c = vec2(0.0, 0.05);
    float P = 2.4;
    for (int i = 0; i < 28; ++i) {
        if (float(i) >= 14.0 * density) break;
        float fi = float(i);
        float h1 = hash11(fi * 7.31 + 1.0), h2 = hash11(fi * 3.17 + 5.0), h3 = hash11(fi * 11.7 + 2.0);
        float age = fract(t / P + h1);
        float ang = fi / 14.0 * TAU + h2 * 0.45 + floor(t / P + h1) * 1.3;
        float r = easeOut(age) * (0.28 + 0.38 * h3) * (0.8 + 0.2 * A);
        vec2 pos = c + vec2(cos(ang) * A * 0.75, sin(ang)) * r + vec2(0.0, -0.12 * age * age);
        float sz = mix(0.012, 0.045 + 0.04 * h2, easeOut(age * 1.4)) * size;
        float a = smoothstep(0.0, 0.08, age) * (1.0 - smoothstep(0.6, 1.0, age));
        float flap = 0.15 + 0.85 * abs(cos(t * (7.0 + 3.0 * h2) + fi * 1.7));
        vec3 b = drawOne(p, pos, sz, 0.6 * cos(ang) + 0.2 * sin(t * 2.0 + fi), flap, a);
        acc = max(acc, b);
        sparks += glowcol * twinkle(p - mix(c, pos, 0.6), 0.01 * size) * a * (1.0 - age) * 1.5;
    }
    // The burst itself: a soft flash in the middle at the start of each wave.
    float wave = beat(t, P / 3.0, 0.25);
    sparks += glowcol * exp(-length(p - c) / 0.12) * wave * 0.25;
#endif
    vec3 light = color * acc.x * 0.95 + mix(glowcol, vec3(1.0), 0.5) * acc.y * 0.5 + glowcol * acc.z * 0.5 * glow + sparks * glow;
    fragColor = vec4(addLight(src.rgb, light, intensity), src.a);
}
""",
    variants=[
        Variant("mariposa-brillante", "Mariposa brillante", "Glowing butterfly", photo="fashion", thumb=1.4,
                tags=["blanco", "white"]),
        Variant("explosion-de-mariposas", "Explosión de mariposas", "Butterfly burst",
                defines={"MODE": "1"}, params={"color": "#ffd1ea", "glowcol": "#ff7ac8"}, photo="woman", thumb=1.2,
                tags=["explosion", "burst", "rosa", "pink"]),
    ],
)


def _dir(drift: float, rise: float) -> float:
    """The Direction (degrees) of a fog that moves -drift in x and +rise in y (toP, y down)."""
    return round(math.degrees(math.atan2(rise, -drift)), 4)


# ---------------------------------------------------------------------------------------------------------------
# Fog, mist and smoke: two layers of domain-warped fbm drifting at different speeds. LOW keeps it near the floor;
# TOXIC tints the picture with it; DREAMY adds a soft bloom of the bright parts.
FOG = Family(
    key="clima_fog", category="particulas",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#d8dde6"), Param("density", "Density", 0.2, 2.0, 1.0),
            Param("size", "Size", 0.3, 3.0, 1.0), Param("direction", "Direction", -180.0, 180.0, 180.0),
            Param("opacity", "Opacity", 0.0, 1.0, 0.55), Param("glow", "Glow", 0.0, 1.0, 0.0)],
    photo="dark", tags=["niebla", "fog", "bruma", "mist", "humo", "smoke"],
    defines={"SCALE": 2.2, "DRIFT": 0.09, "RISE": 0.0, "LOW": 0.0, "LOW_TOP": 0.35, "TOXIC": 0.0,
             "PULSE": 0.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec2 q = p * SCALE / max(size, 0.05);
    // Drift: DRIFT/RISE set how fast, `direction` (degrees, 180 = to the left) where to.
    float ang = radians(direction);
    vec2 mv = vec2(cos(ang), sin(ang)) * length(vec2(DRIFT, RISE));
    vec2 warp = vec2(fbm(q * 0.7 + vec2(t * 0.04, 1.7)), fbm(q * 0.7 + vec2(5.2, 1.3) - vec2(0.0, t * 0.035)));
    float f1 = fbm(q + 1.6 * warp + mv * t);
    float f2 = fbm(q * 1.9 + 0.9 * warp + mv * t * vec2(1.8, 1.6) + 3.1);
    float n = f1 * 0.65 + f2 * 0.35;
    float lo = 0.68 - 0.16 * density;
    float fog = smoothstep(lo - 0.2, lo + 0.22, n);
    // A thin veil everywhere so the gaps are not empty.
    fog = max(fog, 0.14 * density * smoothstep(0.25, 0.6, n));
    float hm = smoothstep(LOW_TOP, 1.0, uv.y + 0.12 * (f2 - 0.5));
    fog *= mix(1.0, hm * 1.25, LOW);
    fog *= 1.0 + PULSE * 0.25 * sin(t * 1.7);
    vec3 base = src.rgb;
    if (glow > 0.0) base = mix(base, screen(base, brightGlow(uv, 0.035, 0.5) * 0.9), glow * sat(intensity));
    if (TOXIC > 0.0) {
        vec3 g = vec3(luma(base)) * vec3(0.72, 1.05, 0.55) + color * 0.05;
        base = mix(base, g, 0.3 * TOXIC * sat(intensity));
    }
    vec3 fogc = color * (0.8 + 0.35 * f2);
    float a = sat(fog * opacity * intensity);
    vec3 col = mix(base, screen(base, fogc), a);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("esmog-toxico", "Esmog tóxico", "Toxic smog", photo="woman", thumb=1.3,
                defines={"TOXIC": 1.0, "SCALE": 1.8, "DRIFT": 0.08, "RISE": 0.03, "PULSE": 1.0},
                params={"color": "#9dff5c", "density": 1.0, "opacity": 0.6, "direction": _dir(0.08, 0.03)}, tags=["toxico", "toxic", "verde", "green", "esmog", "smog"]),
        Variant("niebla-de-ensueno-1", "Niebla de ensueño 1", "Dreamy fog 1", thumb=1.5,
                defines={"DRIFT": 0.09}, params={"glow": 0.5}, tags=["ensueño", "dreamy"]),
        Variant("niebla-de-ensueno-2", "Niebla de ensueño 2", "Dreamy fog 2", thumb=1.5,
                defines={"DRIFT": 0.015, "RISE": 0.06, "SCALE": 2.8},
                params={"density": 0.8, "glow": 0.4, "direction": _dir(0.015, 0.06)}, tags=["ensueño", "dreamy", "vertical"]),
        Variant("niebla-de-ensueno-3", "Niebla de ensueño 3", "Dreamy fog 3", photo="nature", thumb=1.5,
                defines={"DRIFT": 0.04, "SCALE": 1.6},
                params={"color": "#e4ecff", "density": 1.3, "glow": 0.9, "opacity": 0.6}, tags=["ensueño", "dreamy", "suave", "soft"]),
        Variant("niebla-de-ensueno-4", "Niebla de ensueño 4", "Dreamy fog 4", thumb=1.5,
                defines={"DRIFT": 0.12, "SCALE": 3.4},
                params={"density": 0.7, "glow": 0.3, "opacity": 0.5}, tags=["ensueño", "dreamy", "jirones", "wisps"]),
        Variant("humo-bajo", "Humo bajo", "Low smoke", thumb=1.5,
                defines={"LOW": 1.0, "LOW_TOP": 0.35, "DRIFT": 0.07, "RISE": 0.02, "SCALE": 2.6},
                params={"color": "#cfd3da", "density": 1.3, "opacity": 0.8, "direction": _dir(0.07, 0.02)}, tags=["halloween", "suelo", "ground", "terror"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Rain: streaks in three depth layers (far thin and slow, near wide, soft and fast), the picture darkened and
# cooled, a mist near the ground. STORM adds lightning flashes.
RAIN = Family(
    key="clima_rain", category="particulas",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#cfe0f0"), Param("density", "Density", 0.2, 2.0, 1.0),
            Param("angle", "Angle", -0.6, 0.6, 0.0), Param("size", "Size", 0.3, 2.5, 1.0),
            Param("brightness", "Brightness", 0.3, 1.3, 0.85), Param("contrast", "Contrast", 0.6, 1.6, 1.0),
            Param("flicker", "Flicker", 0.0, 1.5, 0.0)],
    photo="dark", tags=["lluvia", "rain", "llover", "raining", "clima", "weather"],
    defines={"STREAK": 0.35, "COOL": 0.3, "MIST": 0.15},
    body=r"""
float rainLayer(vec2 p, float t, float scale, float fall, float len, float width, float seed) {
    p *= scale;
    p.y -= t * fall;
    float col = floor(p.x);
    vec2 g = vec2(p.x, p.y / 3.0 + hash11(col * 1.37 + seed) * 7.0);
    vec2 cell = floor(g), f = fract(g);
    vec3 h = hash32(cell + seed);
    if (h.x > 0.55 * density) return 0.0;
    float ox = 0.15 + 0.7 * h.y;
    float L = len * (0.6 + 0.4 * h.z);
    float oy = (1.0 - L) * fract(h.z * 7.13 + h.y);
    float w = max(width, scale * 1.4 / max(u_resolution.y, 1.0));
    float dx = abs(f.x - ox);
    float dy = f.y - oy;
    float line = smoothstep(w, 0.0, dx);
    float along = smoothstep(0.0, L, dy) * (1.0 - smoothstep(L * 0.92, L, dy)) * step(0.0, dy);
    return line * along * (0.6 + 0.4 * h.y);
}
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec2 r = rot(angle) * p;
    float far_ = rainLayer(r, t, 34.0, 26.0, STREAK * size * 0.8, 0.05, 3.0);
    float mid = rainLayer(r, t, 18.0, 17.0, STREAK * size, 0.06, 11.0);
    float near = rainLayer(r, t, 9.0, 10.5, STREAK * size * 1.2, 0.08, 23.0);
    float rain = far_ * 0.45 + mid * 0.7 + near * 0.9;

    vec3 base = src.rgb;
    float k = sat(intensity);
    base = mix(base, contrastColor(base, contrast), k);
    base *= mix(1.0, brightness, k);
    base = mix(base, vec3(luma(base)) * vec3(0.85, 0.95, 1.12), COOL * k);
    // Mist near the ground and a faint haze from the rain.
    float mist = smoothstep(0.45, 1.0, uv.y) * (0.6 + 0.4 * fbm(p * 3.0 + vec2(t * 0.1, 0.0)));
    base = mix(base, screen(base, vec3(0.55, 0.62, 0.7)), MIST * mist * k);
    float flash = 0.0;
    if (flicker > 0.0) {
        float tf = fract(u_time / 3.6);
        flash = exp(-abs(tf - 0.38) * 45.0) + 0.7 * exp(-abs(tf - 0.45) * 30.0) + 0.4 * exp(-abs(tf - 0.53) * 35.0);
        flash *= flicker;
        base = screen(base, vec3(0.7, 0.78, 0.95) * flash * 0.55 * k);
    }
    vec3 col = addLight(base, color * (1.0 + flash), rain * intensity);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("lloviendo-1", "Lloviendo 1", "Raining 1", thumb=1.0, tags=["llovizna", "drizzle"]),
        Variant("lloviendo-2", "Lloviendo 2", "Raining 2", thumb=1.0,
                defines={"STREAK": 0.55, "MIST": 0.05}, params={"density": 0.6, "angle": 0.08, "brightness": 0.9}),
        Variant("lluvia-de-cine", "Lluvia de cine", "Cinematic rain", photo="citynight", thumb=1.0,
                defines={"STREAK": 0.45, "COOL": 0.55, "MIST": 0.3},
                params={"density": 1.4, "angle": 0.12, "brightness": 0.8, "contrast": 1.12}, tags=["cine", "cinematic", "pelicula", "movie"]),
        Variant("tormenta-de-lluvia", "Tormenta de lluvia", "Rainstorm", thumb=1.0,
                defines={"STREAK": 0.5, "COOL": 0.5, "MIST": 0.35},
                params={"density": 1.8, "angle": 0.3, "speed": 1.3, "brightness": 0.7, "flicker": 1.0},
                tags=["tormenta", "storm", "rayo", "lightning", "trueno", "thunder"]),
    ],
)

FAMILIES = [BUTTERFLIES, FOG, RAIN]
