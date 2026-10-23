"""Efectos › Tendencias: Partículas y brillos (first part of the section: from «Nieve de flores» to «Bokeh 3D»).

Six families, every one drawn in two or three depth layers (far = small, dim and slow; near = big, soft and fast):
  pt_fall     things that fall: snow, petals, confetti, stars, light drops
  pt_field    a sky of glitter that floats and twinkles, with an optional warm light source
  pt_firefly  free wandering glows (fireflies, little lights with a motion streak)
  pt_path     glitter that flows along a curve or around a ring
  pt_burst    bursts of stars (one in the middle, or fireworks here and there)
  pt_bokeh    soft out-of-focus discs (3D drift towards the camera, or a sparkling frame)

Particles live in a grid of cells; each one is jittered inside its cell and every pixel looks at the 3x3
neighbouring cells, so nothing is cut at a cell edge and no grid shows.
"""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)
DENSITY = Param("density", "Density", 0.2, 2.0, 1.0)
# Multipliers and offsets: their defaults (1 or 0) give exactly the look each variant was designed with.
SIZE = Param("size", "Size", 0.3, 3.0, 1.0)
GLOW = Param("glow", "Glow", 0.0, 3.0, 1.0)
FLICKER = Param("flicker", "Flicker", 0.0, 2.0, 1.0)
BRIGHTNESS = Param("brightness", "Brightness", 0.0, 3.0, 1.0)
ANGLE = Param("angle", "Angle", -90.0, 90.0, 0.0)          # degrees
DIRECTION = Param("angle", "Direction", -180.0, 180.0, 0.0)  # degrees, turns the drift
SATURATION = Param("saturation", "Saturation", 0.0, 2.0, 1.0)
CENTER_X = Param("center_x", "Center X", -0.5, 0.5, 0.0)
CENTER_Y = Param("center_y", "Center Y", -0.5, 0.5, 0.0)
SPREAD = Param("spread", "Spread", 0.3, 2.5, 1.0)


def colour(default: str) -> Param:
    return Param("color", "Colour", default=default)


# Shared by every family: the colour of one particle (variations around `color`) and the particle shapes.
COMMON = r"""
// A particle's colour: hue and brightness spread around the chosen colour.
vec3 pal(float h) {
    vec3 c = hueShift(color, (h - 0.5) * HUEVAR);
    c = mix(c, vec3(1.0), WHITEMIX * step(0.72, fract(h * 13.7)));
    return c * (1.0 - BRVAR * fract(h * 7.31));
}
// Smallest radius that still reads as a soft point at this resolution, in toP units.
float minR() { return 1.1 / max(u_resolution.y, 1.0); }
float softDot(vec2 d, float r) { return exp(-dot(d, d) / (r * r) * 2.2); }
float halo(vec2 d, float r) { return exp(-length(d) / (r * 2.5)); }
// A five point star with its glow.
float star5(vec2 d, float r, float aa) { return fillSd(sdStar(d, r, 5.0, 0.48), aa); }
// An out of focus disc: flat, a little brighter at the rim.
float bokehDisc(vec2 d, float r, float aa) {
    float l = length(d);
    return smoothstep(r + aa, r - aa, l) * (0.7 + 0.3 * smoothstep(r * 0.4, r, l));
}
"""

# ------------------------------------------------------------------------------------------------- falling
FALL = Family(
    key="pt_fall", category="particulas",
    params=[INTENSITY, SPEED, DENSITY, colour("#ffffff"), SIZE, ANGLE, GLOW, SATURATION],
    photo="lighthouse", tags=["particulas", "particles", "caer", "falling"],
    defines={"SHAPE": "0", "FALL": 1.0, "WIND": 0.1, "SWAY": 0.12, "SPIN": 1.0, "SIZE": 0.07, "DENS": 0.45,
             "PAINT": 1.0, "GLOWK": 0.25, "BLUR": 0.35, "HUEVAR": 0.0, "BRVAR": 0.1, "WHITEMIX": 0.0,
             "COLUMN": 0.0, "STARS": 0.0, "FOG": 0.0, "TRAIL": 0.0},
    body=COMMON + r"""
vec3 gLight = vec3(0.0);
vec4 gPaint = vec4(0.0);

void fallLayer(vec2 p, float t, float scale, float spd, float seed, float depth) {
    vec2 q = p * scale;
    q.x -= t * WIND * spd;
    float aa = 1.5 / max(u_resolution.y, 1.0);
    for (int j = -1; j <= 1; ++j) {
        float cx = floor(q.x) + float(j);
        float colShift = t * spd + hash11(cx * 7.31 + seed) * 37.0;   // every column falls with its own offset
        float qy = q.y - colShift;
        for (int i = -1; i <= 1; ++i) {
            vec2 cell = vec2(cx, floor(qy) + float(i));
            float h = hash12(cell + seed * 3.17);
            if (h > DENS * density) continue;
            vec3 hh = hash32(cell + seed * 1.37);
            float sw = sin(t * (0.7 + hh.z) * 1.6 + hh.x * TAU) * SWAY;
            vec2 c = cell + 0.5 + (hh.xy - 0.5) * vec2(0.75, 0.8) + vec2(sw, 0.0);
            c.y += colShift;
            vec2 pc = c / scale;
            pc.x += t * WIND * spd / scale;
            vec2 d = p - pc;                                 // toP units
            float r = max(SIZE * size / scale * (0.55 + 0.45 * hh.z), minR());
            if (dot(d, d) > r * r * 30.0) continue;
            float w = 1.0;
            if (COLUMN > 0.0) w = exp(-pow(pc.x / COLUMN, 2.0)) * (0.35 + 0.65 * smoothstep(0.5, -0.3, pc.y));
            float soft = aa + BLUR * depth * r * 0.6;
            float fade = mix(0.55, 1.0, depth) * w;
            float ang = hh.y * TAU + t * SPIN * (hh.z - 0.5) * 3.0;
            vec2 dr = rot(ang) * d;
            vec3 col = saturateColor(pal(fract(hh.x * 3.1 + hh.z)), saturation);
            float a = 0.0;
            float g = 0.0;
#if SHAPE == 0
            // Soft round flake / drop of light.
            a = 1.0 - smoothstep(r * 0.3, r + soft, length(d));
            g = halo(d, r);
#elif SHAPE == 1
            // Six armed snow crystal with a soft core.
            float an = atan(dr.y, dr.x);
            float sec = mod(an + PI / 6.0, PI / 3.0) - PI / 6.0;
            float l = length(dr);
            float arm = abs(sin(sec)) * l;
            float th = r * 0.09 + soft;
            a = smoothstep(th, th * 0.3, arm) * smoothstep(r * 1.6, r * 1.2, l);
            vec2 bq = vec2(cos(sec), abs(sin(sec))) * l - vec2(r * 0.85, 0.0);
            a = max(a, smoothstep(th, th * 0.3, abs(dot(bq, vec2(0.5, -0.866)))) * step(abs(bq.x), r * 0.35)
                       * smoothstep(r * 1.6, r * 1.2, l));
            a = max(a, 1.0 - smoothstep(r * 0.15, r * 0.35 + soft, l));
            a *= 0.95;
            g = halo(d, r * 0.8) * 0.7;
#elif SHAPE == 2
            // Petal that tumbles while it falls: an ellipse with a notch, light in the middle.
            float tb = cos(t * (1.5 + 2.0 * hh.z) + hh.x * TAU);
            vec2 e = dr / vec2(r * (0.35 + 0.65 * abs(tb)), r * 0.62);
            float pd = (length(e) - 1.0) * r * 0.5;
            float notch = length((dr - vec2(r * 1.0, 0.0)) / vec2(r * 0.28, r * 0.18)) - 1.0;
            a = fillSd(pd, soft) * smoothstep(-0.2, 0.4, notch);
            col *= 0.82 + 0.25 * (1.0 - length(e)) + 0.12 * tb;
            g = 0.0;
#elif SHAPE == 3
            // Confetti: a little card that flips over (its width follows the flip, its shade too).
            float tb = cos(t * (3.0 + 4.0 * hh.z) + hh.y * TAU);
            float bd = sdBox(dr, vec2(r * max(abs(tb), 0.08), r * 0.5));
            a = fillSd(bd, soft);
            col *= 0.62 + 0.45 * (0.5 + 0.5 * tb);
#elif SHAPE == 4
            // Five point star, with a short trail above it.
            a = star5(dr, r, soft);
            g = exp(-length(d) / (r * 0.7));
            if (TRAIL > 0.0) {
                float tr = exp(-abs(d.x) / (r * 0.12)) * exp(d.y / (r * TRAIL)) * step(d.y, 0.0);
                gLight += col * tr * 0.7 * fade;
            }
#else
            // Streamer: a short wavy ribbon.
            float wv = dr.y - r * 0.3 * sin(dr.x / r * 3.5 + t * 6.0 * (hh.z - 0.5) + hh.x * 6.0);
            a = smoothstep(r * 0.16 + soft, r * 0.08, abs(wv)) * smoothstep(r * 1.4, r * 1.1, abs(dr.x));
            col *= 0.85 + 0.2 * sin(dr.x / r * 3.5);
#endif
            gPaint = over(vec4(col, sat(a * PAINT * fade)), gPaint);
            gLight += col * (g * GLOWK * glow + a * (1.0 - PAINT)) * fade;
        }
    }
}

// Far background stars that just twinkle (snowy night).
vec3 starField(vec2 p, float t) {
    vec3 s = vec3(0.0);
    vec2 q = p * 7.0;
    for (int j = -1; j <= 1; ++j)
    for (int i = -1; i <= 1; ++i) {
        vec2 cell = floor(q) + vec2(float(i), float(j));
        float h = hash12(cell + 91.0);
        if (h > 0.22) continue;
        vec3 hh = hash32(cell + 17.0);
        vec2 c = (cell + 0.5 + (hh.xy - 0.5) * 0.8) / 7.0;
        float tw = pow(0.5 + 0.5 * sin(t * (1.5 + 2.0 * hh.z) + hh.x * TAU), 3.0);
        float r = mix(0.006, 0.02, hh.z * hh.z);
        s += mix(vec3(1.0), vec3(0.8, 0.9, 1.0), hh.y) * twinkle(rot(0.3 * hh.y) * (p - c), r) * (0.25 + 0.9 * tw);
    }
    return s;
}

void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    vec3 col = src.rgb;
    if (FOG > 0.0) {
        // Winter air: a cold veil, lighter at the top.
        vec3 veil = vec3(0.82, 0.88, 0.96) * (0.75 + 0.25 * fbm(p * 2.0 + vec2(t * 0.05, 0.0)));
        col = mix(col, screen(col, veil * 0.6), FOG * intensity * (0.6 + 0.4 * smoothstep(0.5, -0.5, p.y)));
    }
    if (STARS > 0.0) col = addLight(col, starField(p, t), STARS * intensity);
    // Angle tilts the fall (the wind keeps blowing across it).
    vec2 pf = rot(radians(angle)) * p;
    fallLayer(pf, t, 10.0, FALL * 0.55, 1.0, 0.0);
    fallLayer(pf, t, 6.0, FALL * 0.85, 7.0, 0.5);
    fallLayer(pf, t, 3.2, FALL * 1.25, 13.0, 1.0);
    col = mix(col, gPaint.rgb, sat(gPaint.a * intensity));
    col = addLight(col, gLight, intensity);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("nieve-de-flores", "Nieve de flores", "Flower snow", photo="fx-woman-07", thumb=1.4,
                defines={"SHAPE": "2", "FALL": 0.7, "WIND": 0.35, "SWAY": 0.18, "SIZE": 0.2, "DENS": 0.4,
                         "HUEVAR": 0.06, "BRVAR": 0.12, "WHITEMIX": 0.35, "BLUR": 0.6},
                params={"color": "#ff6fa8"},
                tags=["flores", "petalos", "petals", "flowers", "primavera", "spring", "sakura"]),
        Variant("copos-de-nieve", "Copos de nieve", "Snowflakes", photo="lighthouse", thumb=1.6,
                defines={"SHAPE": "1", "FALL": 0.6, "WIND": 0.12, "SIZE": 0.17, "DENS": 0.3, "BRVAR": 0.05,
                         "GLOWK": 0.35},
                tags=["nieve", "snow", "copos", "snowflakes", "invierno", "winter", "navidad", "christmas"]),
        Variant("nevada-de-invierno", "Nevada de invierno", "Winter snowfall", photo="nature", thumb=1.2,
                defines={"SHAPE": "0", "FALL": 1.1, "WIND": 0.3, "SIZE": 0.09, "DENS": 0.7, "BLUR": 0.9,
                         "FOG": 0.35, "BRVAR": 0.15},
                tags=["nieve", "snow", "nevada", "snowfall", "invierno", "winter", "tormenta", "blizzard"]),
        Variant("noche-de-nieve-y-estrellas", "Noche de nieve y estrellas", "Snowy starry night", photo="citynight",
                thumb=1.5,
                defines={"SHAPE": "0", "FALL": 0.6, "WIND": 0.1, "SIZE": 0.07, "DENS": 0.45, "STARS": 1.0},
                tags=["nieve", "snow", "estrellas", "stars", "noche", "night", "invierno", "winter"]),
        Variant("confeti-volando", "Confeti volando", "Flying confetti", photo="couple", thumb=1.0,
                defines={"SHAPE": "3", "FALL": 0.9, "WIND": 0.2, "SWAY": 0.2, "SIZE": 0.2, "DENS": 0.55,
                         "HUEVAR": 1.0, "BRVAR": 0.05, "SPIN": 2.0, "BLUR": 0.5},
                params={"color": "#ff4d7a"},
                tags=["confeti", "confetti", "fiesta", "party", "celebracion", "celebration", "cumpleanos", "birthday"]),
        Variant("confeti-de-festival", "Confeti de festival", "Festival confetti", photo="concert", thumb=1.3,
                defines={"SHAPE": "5", "FALL": 0.75, "WIND": -0.15, "SWAY": 0.22, "SIZE": 0.2, "DENS": 0.5,
                         "HUEVAR": 1.0, "BRVAR": 0.0, "WHITEMIX": 0.15, "SPIN": 1.5, "BLUR": 0.4},
                params={"color": "#ffd23f"},
                tags=["confeti", "confetti", "serpentinas", "streamers", "festival", "fiesta", "party"]),
        Variant("estrellas-que-caen", "Estrellas que caen", "Falling stars", photo="fx-man-06", thumb=1.4,
                defines={"SHAPE": "4", "FALL": 0.8, "WIND": 0.05, "SWAY": 0.05, "SIZE": 0.11, "DENS": 0.28,
                         "TRAIL": 2.5, "HUEVAR": 0.06, "BRVAR": 0.1, "WHITEMIX": 0.5, "GLOWK": 0.12, "BLUR": 0.1},
                params={"color": "#ffd77a"},
                tags=["estrellas", "stars", "caer", "falling", "brillo", "sparkle", "magia", "magic"]),
        Variant("luces-navidenas", "Luces navideñas", "Christmas lights", photo="fx-citynight-02", thumb=1.2,
                defines={"SHAPE": "0", "FALL": 0.55, "WIND": 0.0, "SWAY": 0.08, "SIZE": 0.075, "DENS": 0.75,
                         "PAINT": 0.0, "GLOWK": 0.9, "COLUMN": 0.42, "HUEVAR": 0.06, "BRVAR": 0.35,
                         "WHITEMIX": 0.3, "STARS": 0.35, "BLUR": 0.6},
                params={"color": "#ffc35a"},
                tags=["navidad", "christmas", "luces", "lights", "dorado", "golden", "fiesta", "holidays"]),
    ],
)

# ------------------------------------------------------------------------------------------------- floating field
FIELD = Family(
    key="pt_field", category="particulas",
    params=[INTENSITY, SPEED, DENSITY, colour("#ffd88a"), SIZE, DIRECTION, FLICKER, GLOW, BRIGHTNESS],
    photo="dark", tags=["particulas", "particles", "brillos", "sparkles", "destellos", "glitter"],
    defines={"DRIFT": (0.0, -0.015), "WANDER": 0.15, "SIZE": 0.06, "DENS": 0.5, "TWK": 3.0, "TWP": 2.0,
             "TWD": 0.8, "STARFRAC": 0.0, "BOKFRAC": 0.0, "STAR5": 0.0, "RAYS": 2.5, "HUEVAR": 0.05,
             "BRVAR": 0.3, "WHITEMIX": 0.3, "REGION": "0", "RPOS": (0.0, 0.0), "RREACH": 0.6, "LTH": 0.6,
             "GLOWPOS": (0.0, 0.0), "GLOWR": 0.3, "GLOWK": 0.0, "GLOWCOL": "#ffb050", "STREAK": 0.0,
             "SCALE": 1.0, "SPINR": 0.0},
    body=COMMON + r"""
// How many particles live here (evaluated at each particle's centre, so they are never cut).
float regionW(vec2 c, float t) {
#if REGION == 1
    return exp(-length(c - RPOS) / RREACH);
#elif REGION == 2
    float n = fbm(c * 2.4 + vec2(t * 0.04, -t * 0.02));
    vec2 e = (c - RPOS) / vec2(RREACH * 1.6, RREACH);
    return smoothstep(0.35, 0.65, n) * exp(-dot(e, e)) * 1.3 + 0.08;
#elif REGION == 3
    return smoothstep(LTH, LTH + 0.15, luma(S(fromP(c)).rgb));
#else
    return 1.0;
#endif
}

vec3 fieldLayer(vec2 p, float t, float scale, float seed, float depth) {
    vec3 acc = vec3(0.0);
    float dm = mix(0.45, 1.0, depth);
    vec2 drift = rot(radians(angle)) * DRIFT;
    vec2 shift = drift * t * dm;
    vec2 q = (p - shift) * scale;
    float aa = 1.2 / max(u_resolution.y, 1.0);
    vec2 dirN = normalize(drift + vec2(1e-5, 0.0));
    for (int j = -1; j <= 1; ++j)
    for (int i = -1; i <= 1; ++i) {
        vec2 cell = floor(q) + vec2(float(i), float(j));
        float h = hash12(cell + seed * 3.17);
        vec3 hh = hash32(cell + seed * 1.37);
        vec2 wan = WANDER * vec2(sin(t * (0.4 + 0.5 * hh.z) + hh.x * TAU), cos(t * (0.35 + 0.5 * hh.y) + hh.z * TAU));
        vec2 c = (cell + 0.5 + (hh.xy - 0.5) * 0.85 + wan) / scale + shift;
#if REGION == 3
        // Glints sit on the brightest of a few spots of the cell (the lights of the picture).
        float best = -1.0;
        for (int k = 0; k < 4; ++k) {
            vec2 cand = (cell + 0.15 + 0.7 * hash22(cell * 1.7 + float(k) * 3.3 + seed)) / scale + shift;
            float l = luma(S(fromP(cand)).rgb);
            if (l > best) { best = l; c = cand; }
        }
        float w = smoothstep(LTH, LTH + 0.15, best);
#else
        float w = regionW(c, t);
#endif
        if (h > DENS * density * min(w, 1.5)) continue;
        vec2 d = p - c;
        float kind = fract(h * 17.31 + hh.z * 3.7);
        float big = (kind < STARFRAC) ? 1.8 : 1.0;
        float r = max(1.6 * SIZE * size / scale * (0.45 + 0.55 * hh.z * hh.z) * big * mix(0.7, 1.0, depth), minR());
        if (dot(d, d) > r * r * RAYS * RAYS * 9.0 + r * r * 40.0) continue;
        float tw = pow(0.5 + 0.5 * sin(t * TWK * (0.6 + 0.8 * hh.z) + hh.y * TAU), TWP);
        float b = mix(1.0 - min(TWD * flicker, 1.0), 1.0, tw) * mix(0.5, 1.0, depth);
        vec3 col = pal(fract(hh.x * 5.3 + hh.y));
        float v;
        if (kind < STARFRAC) {
            float ang = (hh.y - 0.5) * 0.5 + t * SPINR * (hh.z - 0.5);
            v = twinkle(rot(ang) * d, r * RAYS * mix(0.6, 1.0, min(glow, 1.0)) * max(glow, 1.0)) * 1.2 * (0.6 + 0.6 * tw);
        } else if (kind < STARFRAC + BOKFRAC) {
            v = bokehDisc(d, r * 3.0, aa + r * 0.6) * 0.32 * mix(0.7, 1.0, tw);
        } else if (STAR5 > 0.5) {
            float ang = hh.y * TAU + t * 0.5 * (hh.z - 0.5);
            v = star5(rot(ang) * d, r * 1.6 * (0.8 + 0.3 * tw), aa) * 1.1 + 0.5 * glow * halo(d, r);
        } else if (STREAK > 0.0) {
            float sd = sdSegment(d, vec2(0.0), -dirN * r * STREAK);
            v = exp(-sd * sd / (r * r) * 2.2) + 0.25 * glow * exp(-sd / (r * 2.5));
        } else {
            v = softDot(d, r) + 0.3 * glow * halo(d, r);
        }
        acc += col * v * b * 1.5;
    }
    return acc;
}

void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    vec3 light = vec3(0.0);
    light += fieldLayer(p, t, 13.0 * SCALE, 1.0, 0.0);
    light += fieldLayer(p, t, 8.0 * SCALE, 7.0, 0.5);
    light += fieldLayer(p, t, 4.5 * SCALE, 13.0, 1.0);
    if (GLOWK > 0.0) {
        float gl = exp(-length((p - GLOWPOS) * vec2(0.8, 1.0)) / GLOWR) * (0.85 + 0.15 * sin(t * 1.3));
        light += GLOWCOL * gl * GLOWK * brightness;
    }
    fragColor = vec4(addLight(src.rgb, light, intensity), src.a);
}
""",
    variants=[
        Variant("polvo-flotante", "Polvo flotante", "Floating dust", photo="woman", thumb=1.5,
                defines={"DRIFT": (0.02, -0.025), "WANDER": 0.25, "SIZE": 0.08, "DENS": 0.45, "TWK": 1.2,
                         "TWD": 0.5, "BOKFRAC": 0.25, "GLOWK": 0.12, "GLOWPOS": (0.5, -0.45), "GLOWR": 0.5,
                         "GLOWCOL": "#fff0d0", "WHITEMIX": 0.5},
                params={"color": "#fff1d6"},
                tags=["polvo", "dust", "flotar", "float", "luz", "light", "suave", "soft"]),
        Variant("puntos-brillantes", "Puntos brillantes", "Shiny dots", photo="couple", thumb=1.2,
                defines={"DRIFT": (0.0, -0.01), "WANDER": 0.1, "SIZE": 0.05, "DENS": 0.55, "TWK": 5.0, "TWP": 3.0,
                         "TWD": 0.95, "STARFRAC": 0.35, "RAYS": 2.8, "WHITEMIX": 0.7},
                params={"color": "#fff4d0"},
                tags=["puntos", "dots", "brillo", "shine", "destellos", "glitter", "magia", "magic"]),
        Variant("purpurina-dorada", "Purpurina dorada", "Golden glitter", photo="fx-face-06", thumb=1.4,
                defines={"REGION": "1", "RPOS": (-0.85, 0.05), "RREACH": 0.55, "DENS": 0.9, "SIZE": 0.055,
                         "TWK": 6.0, "TWP": 3.0, "TWD": 0.9, "STARFRAC": 0.12, "GLOWK": 0.75,
                         "GLOWPOS": (-0.95, 0.0), "GLOWR": 0.32, "GLOWCOL": "#ffcf8a", "DRIFT": (0.02, -0.01)},
                params={"color": "#ffcc66"},
                tags=["purpurina", "glitter", "dorado", "gold", "brillo", "sparkle", "lujo", "luxury"]),
        Variant("estrellas-doradas", "Estrellas doradas", "Golden stars", photo="fx-woman-02", thumb=1.0,
                defines={"DENS": 0.42, "SIZE": 0.05, "TWK": 4.0, "TWP": 2.5, "TWD": 0.85, "STARFRAC": 0.25,
                         "RAYS": 2.2, "GLOWK": 0.9, "GLOWPOS": (-0.85, -0.5), "GLOWR": 0.35, "GLOWCOL": "#ff9a2e",
                         "DRIFT": (0.01, 0.005)},
                params={"color": "#ffd27a"},
                tags=["estrellas", "stars", "dorado", "gold", "brillo", "sparkle"]),
        Variant("cielo-estrellado", "Cielo estrellado", "Starry sky", photo="citynight", thumb=1.6,
                defines={"DENS": 0.38, "SIZE": 0.045, "TWK": 2.0, "TWP": 2.0, "TWD": 0.75, "STARFRAC": 0.1,
                         "RAYS": 2.0, "DRIFT": (0.012, 0.0), "WANDER": 0.02, "HUEVAR": 0.15, "WHITEMIX": 0.8,
                         "BRVAR": 0.4},
                params={"color": "#cfe0ff"},
                tags=["estrellas", "stars", "cielo", "sky", "noche", "night"]),
        Variant("estrella-centelleante-1", "Estrella centelleante 1", "Twinkling star 1", photo="fx-citynight-04",
                thumb=1.1,
                defines={"REGION": "3", "LTH": 0.5, "DENS": 1.0, "SCALE": 1.8, "SIZE": 0.12, "TWK": 4.0,
                         "TWP": 4.0, "TWD": 1.0, "STARFRAC": 1.0, "RAYS": 3.0, "WANDER": 0.0, "DRIFT": (0.0, 0.0),
                         "WHITEMIX": 0.6},
                params={"color": "#fff2d8"},
                tags=["estrella", "star", "centelleo", "twinkle", "destello", "glint", "luces", "lights"]),
        Variant("estrella-centelleante-5", "Estrella centelleante 5", "Twinkling star 5", photo="fx-citynight-04",
                thumb=1.3,
                defines={"REGION": "3", "LTH": 0.5, "DENS": 1.0, "SCALE": 1.1, "SIZE": 0.2, "TWK": 2.0,
                         "TWP": 3.0, "TWD": 1.0, "STARFRAC": 1.0, "RAYS": 4.0, "SPINR": 1.5, "WANDER": 0.0,
                         "DRIFT": (0.0, 0.0), "WHITEMIX": 0.8},
                params={"color": "#e6eeff"},
                tags=["estrella", "star", "centelleo", "twinkle", "destello", "glint", "luces", "lights"]),
        Variant("brillo-dorado", "Brillo dorado", "Golden glow", photo="fx-cyber-02", thumb=1.4,
                defines={"REGION": "1", "RPOS": (0.0, 0.5), "RREACH": 0.45, "DENS": 0.8, "SIZE": 0.06,
                         "DRIFT": (0.0, -0.06), "WANDER": 0.2, "TWK": 3.0, "TWD": 0.7, "STARFRAC": 0.08,
                         "GLOWK": 1.0, "GLOWPOS": (0.0, 0.58), "GLOWR": 0.22, "GLOWCOL": "#ff9a3c"},
                params={"color": "#ffc25c"},
                tags=["dorado", "gold", "brillo", "glow", "calido", "warm"]),
        Variant("destellos-calidos", "Destellos cálidos", "Warm sparkles", photo="fx-hair-03", thumb=1.2,
                defines={"REGION": "1", "RPOS": (0.0, -0.45), "RREACH": 0.5, "DENS": 0.75, "SIZE": 0.055,
                         "DRIFT": (0.0, 0.03), "WANDER": 0.15, "TWK": 4.0, "TWP": 2.5, "TWD": 0.85,
                         "STARFRAC": 0.15, "GLOWK": 1.3, "GLOWPOS": (0.0, -0.62), "GLOWR": 0.32,
                         "GLOWCOL": "#ffcf8f"},
                params={"color": "#ffe0a8"},
                tags=["calido", "warm", "destellos", "sparkles", "dorado", "gold"]),
        Variant("estrellas-lejanas", "Estrellas lejanas", "Distant stars", photo="fx-citynight-04", thumb=1.5,
                defines={"DENS": 0.3, "SIZE": 0.032, "SCALE": 1.3, "TWK": 1.2, "TWP": 3.0, "TWD": 0.9,
                         "DRIFT": (-0.008, 0.0), "WANDER": 0.02, "HUEVAR": 0.1, "WHITEMIX": 0.9, "BRVAR": 0.5},
                params={"color": "#bcd4ff"},
                tags=["estrellas", "stars", "lejanas", "distant", "espacio", "space", "noche", "night"]),
        Variant("polvo-azul", "Polvo azul", "Blue dust", photo="fx-dancer-02", thumb=1.5,
                defines={"REGION": "2", "RPOS": (-0.25, -0.15), "RREACH": 0.5, "DENS": 1.3, "SIZE": 0.05,
                         "SCALE": 1.2, "DRIFT": (0.02, -0.01), "WANDER": 0.25, "TWK": 3.0, "TWD": 0.7,
                         "HUEVAR": 0.1, "WHITEMIX": 0.25, "GLOWK": 0.55, "GLOWPOS": (-0.25, -0.15), "GLOWR": 0.4,
                         "GLOWCOL": "#2a6cff"},
                params={"color": "#4aa8ff"},
                tags=["polvo", "dust", "azul", "blue", "nebulosa", "nebula", "streaming"]),
        Variant("estrellas-sueltas", "Estrellas sueltas", "Scattered stars", photo="fx-citynight-06", thumb=1.0,
                defines={"DENS": 0.2, "SIZE": 0.07, "SCALE": 0.8, "TWK": 1.5, "TWP": 2.0, "TWD": 0.8,
                         "STARFRAC": 0.2, "RAYS": 2.0, "DRIFT": (0.0, 0.0), "WANDER": 0.1, "WHITEMIX": 0.2},
                params={"color": "#ffd88a"},
                tags=["estrellas", "stars", "sueltas", "scattered", "dorado", "gold"]),
        Variant("bling-bling", "Bling bling", "Bling bling", photo="fx-face-03", thumb=1.3,
                defines={"DENS": 0.35, "SIZE": 0.06, "SCALE": 0.75, "TWK": 3.5, "TWP": 5.0, "TWD": 1.0,
                         "STARFRAC": 0.75, "RAYS": 3.2, "SPINR": 0.6, "DRIFT": (0.0, 0.0), "WANDER": 0.05,
                         "WHITEMIX": 0.9},
                params={"color": "#ffffff"},
                tags=["bling", "brillo", "shine", "destello", "glint", "joyas", "jewels"]),
        Variant("brillos-al-aire", "Brillos al aire", "Sparkles in the air", photo="fx-hair-04", thumb=1.6,
                defines={"DENS": 0.32, "SIZE": 0.05, "DRIFT": (0.01, -0.05), "WANDER": 0.3, "TWK": 2.5,
                         "TWP": 2.0, "TWD": 0.8, "STARFRAC": 0.15, "RAYS": 2.0, "HUEVAR": 0.1, "WHITEMIX": 0.6},
                params={"color": "#d8ecff"},
                tags=["brillos", "sparkles", "aire", "air", "flotar", "float"]),
        Variant("chispas-doradas", "Chispas doradas", "Golden sparks", photo="fx-skater-02", thumb=1.4,
                defines={"REGION": "1", "RPOS": (0.75, 0.45), "RREACH": 0.6, "DENS": 0.85, "SIZE": 0.045,
                         "DRIFT": (-0.05, -0.12), "WANDER": 0.2, "TWK": 9.0, "TWP": 1.5, "TWD": 0.6, "STREAK": 4.0,
                         "GLOWK": 0.8, "GLOWPOS": (0.85, 0.55), "GLOWR": 0.3, "GLOWCOL": "#ff8a2a", "HUEVAR": 0.06},
                params={"color": "#ffb347"},
                tags=["chispas", "sparks", "dorado", "gold", "fuego", "fire", "brasas", "embers"]),
        Variant("estrellas-titilantes", "Estrellas titilantes", "Twinkling stars", photo="fx-citynight-05", thumb=1.2,
                defines={"DENS": 0.3, "SIZE": 0.045, "STAR5": 1.0, "TWK": 3.0, "TWP": 2.0, "TWD": 0.9,
                         "DRIFT": (0.0, 0.0), "WANDER": 0.06, "HUEVAR": 0.08, "WHITEMIX": 0.6},
                params={"color": "#fff1b8"},
                tags=["estrellas", "stars", "titilar", "twinkle", "noche", "night"]),
        Variant("polvo-estelar", "Polvo estelar", "Stardust", photo="fx-nature-02", thumb=1.4,
                defines={"DENS": 0.28, "SIZE": 0.06, "DRIFT": (0.03, 0.0), "WANDER": 0.15, "TWK": 1.5, "TWP": 1.5,
                         "TWD": 0.6, "BOKFRAC": 0.15, "STARFRAC": 0.08, "HUEVAR": 0.12, "WHITEMIX": 0.7},
                params={"color": "#dfe8ff"},
                tags=["polvo", "dust", "estelar", "stardust", "magia", "magic"]),
        Variant("paquete-de-brillos", "Paquete de brillos", "Sparkle pack", photo="fx-cyber-05", thumb=1.3,
                defines={"DENS": 0.55, "SIZE": 0.055, "TWK": 4.0, "TWP": 3.0, "TWD": 0.9, "STARFRAC": 0.3,
                         "BOKFRAC": 0.1, "RAYS": 2.4, "DRIFT": (0.0, -0.01), "WANDER": 0.1, "HUEVAR": 0.1,
                         "WHITEMIX": 0.4, "GLOWK": 0.25, "GLOWPOS": (0.0, 0.0), "GLOWR": 0.6, "GLOWCOL": "#ffb85c"},
                params={"color": "#ffd27a"},
                tags=["brillos", "sparkles", "paquete", "pack", "dorado", "gold", "destellos"]),
    ],
)

# ------------------------------------------------------------------------------------------------- fireflies
FIREFLY = Family(
    key="pt_firefly", category="particulas",
    params=[INTENSITY, SPEED, DENSITY, colour("#d9ff6a")],
    photo="nature", tags=["luciernagas", "fireflies", "luces", "lights", "noche", "night"],
    defines={"NUMF": 0.8, "ROAM": 0.12, "WF": 0.6, "RMIN": 0.004, "RMAX": 0.012, "STREAK": 0.0, "BLINK": 0.0,
             "HUEVAR": 0.06, "BRVAR": 0.2, "WHITEMIX": 0.0, "HALO": 0.5},
    body=COMMON + r"""
vec2 flyPos(vec3 h, float fi, float t) {
    vec2 base = (vec2(hash11(fi * 3.7 + 1.0), hash11(fi * 5.3 + 2.0)) - 0.5) * vec2(aspect() * 1.1, 1.1);
    vec2 w = vec2(sin(t * WF * (0.5 + h.y) + fi * 1.7) + 0.5 * sin(t * WF * 1.9 * (0.6 + h.z) + fi),
                  cos(t * WF * (0.45 + h.z) * 1.2 + fi * 2.3) + 0.5 * cos(t * WF * 2.3 * (0.5 + h.x) + fi * 0.7));
    return base + w * ROAM * (0.6 + 0.8 * h.x);
}

void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    vec3 light = vec3(0.0);
    for (int i = 0; i < 32; ++i) {
        float fi = float(i);
        vec3 h = hash32(vec2(fi * 1.37 + 0.5, fi * 0.71 + 3.1));
        if (hash11(fi * 9.1 + 4.0) > NUMF * density) continue;
        vec2 pos = flyPos(h, fi, t);
        float r = mix(RMIN, RMAX, h.y * h.y);
        float d;
        if (STREAK > 0.0) {
            vec2 prev = flyPos(h, fi, t - 0.12);
            d = sdSegment(p, pos, pos + (prev - pos) * STREAK);
        } else {
            d = length(p - pos);
        }
        if (d > r * 14.0 + 0.05) continue;
        float pulse;
        if (BLINK > 0.0) {
            // Real fireflies: dark most of the time, a slow glow now and then.
            float s = sin(t * BLINK * (0.6 + 0.8 * h.z) + h.x * TAU);
            pulse = 0.08 + smoothstep(0.2, 0.95, s);
        } else {
            pulse = 0.45 + 0.55 * (0.5 + 0.5 * sin(t * 3.0 * (0.6 + h.z) + h.y * TAU));
        }
        float depth = mix(0.55, 1.0, h.y);
        vec3 c = pal(h.z);
        float core = exp(-d * d / (r * r) * (STREAK > 0.0 ? 0.9 : 1.8));
        float glow = exp(-d / (r * 3.0)) * HALO;
        light += (c * glow + mix(c, vec3(1.0), 0.6) * core) * pulse * depth;
    }
    fragColor = vec4(addLight(src.rgb, light, intensity), src.a);
}
""",
    variants=[
        Variant("luciernagas-bailando", "Luciérnagas bailando", "Dancing fireflies", photo="fx-nature-02", thumb=1.4,
                defines={"NUMF": 1.0, "ROAM": 0.16, "WF": 0.9, "RMIN": 0.005, "RMAX": 0.013, "HALO": 0.8},
                params={"color": "#ffcf5a"},
                tags=["luciernagas", "fireflies", "bailar", "dance", "dorado", "gold"]),
        Variant("luciernaga-realista-01", "Luciérnaga realista 01", "Realistic firefly 01", photo="fx-nature-01", thumb=1.6,
                defines={"NUMF": 0.85, "ROAM": 0.1, "WF": 0.35, "RMIN": 0.005, "RMAX": 0.014, "BLINK": 1.6,
                         "HALO": 1.0},
                params={"color": "#c8ff5a"},
                tags=["luciernaga", "firefly", "realista", "realistic", "bosque", "forest", "noche", "night"]),
        Variant("lucecitas-flotantes", "Lucecitas flotantes", "Floating little lights", photo="fx-dancer-01", thumb=1.2,
                defines={"NUMF": 0.45, "ROAM": 0.2, "WF": 0.8, "RMIN": 0.012, "RMAX": 0.028, "STREAK": 1.2,
                         "HUEVAR": 1.0, "BRVAR": 0.1, "WHITEMIX": 0.2, "HALO": 0.7},
                params={"color": "#b36bff"},
                tags=["luces", "lights", "flotar", "float", "colores", "colours", "magia", "magic"]),
    ],
)

# ------------------------------------------------------------------------------------------------- along a path
PATH = Family(
    key="pt_path", category="particulas",
    params=[INTENSITY, SPEED, DENSITY, colour("#ffd27a")],
    photo="dark", tags=["particulas", "particles", "estela", "trail", "brillos", "sparkles"],
    defines={"MODE": "0", "AMP": 0.12, "FREQ": 3.0, "WAVE": 0.6, "SLOPE": -0.35, "YOFF": 0.05, "WID": 0.06,
             "WIDG": 1.5, "FLOW": 0.25, "CELL": 22.0, "DENS": 0.8, "SIZE": 0.11, "STARFRAC": 0.15, "STREAK": 0.0,
             "COMET": 0.0, "CPERIOD": 3.0, "TAIL": 0.5, "R0": 0.3, "NRING": 64.0, "HAZE": 0.12,
             "HUEVAR": 0.06, "BRVAR": 0.3, "WHITEMIX": 0.4},
    body=COMMON + r"""
// Curve: centre line y(x), how wide the glitter spreads there, and how strong (a comet head can sweep it).
float curveY(float x, float t) { return AMP * sin(x * FREQ + t * WAVE) + SLOPE * x + YOFF; }
float spread(float x) { return WID * (1.0 + WIDG * sat(x / aspect() + 0.5)); }
float cometW(float x, float t) {
    if (COMET <= 0.0) return 1.0;
    float head = mix(-aspect() * 0.5 - 0.1, aspect() * 0.5 + 0.35, phase(t, CPERIOD));
    return smoothstep(head + 0.02, head - 0.04, x) * exp(-(head - x) / TAIL);
}

vec3 sparkle(vec2 d, float r, float kind, float tw, vec3 col, vec2 dir) {
    if (kind < STARFRAC) return col * twinkle(rot(0.4) * d, r * 2.4) * (0.5 + 0.8 * tw);
    if (STREAK > 0.0) {
        float sd = sdSegment(d, vec2(0.0), -dir * r * STREAK);
        return col * (exp(-sd * sd / (r * r) * 2.0) + 0.2 * exp(-sd / (r * 2.5))) * (0.5 + 0.5 * tw);
    }
    return col * (softDot(d, r) + 0.3 * halo(d, r)) * (0.4 + 0.6 * tw);
}

void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    vec3 light = vec3(0.0);
    float hazeAcc = 0.0;
    for (int L = 0; L < 2; ++L) {
        float fl = float(L);
        float cs = CELL * (fl < 0.5 ? 1.0 : 0.6);
        float depth = fl;
#if MODE == 1
        // Ring: angle around the centre and distance from the circle.
        float ang = atan(p.y, p.x);
        float rr = length(p);
        float rot_ = t * FLOW * (fl < 0.5 ? 0.7 : 1.0);
        vec2 q = vec2((ang / TAU + 0.5) * NRING * (fl < 0.5 ? 1.0 : 0.6) - rot_ * NRING / TAU,
                      (rr - R0) * cs);
        float n = NRING * (fl < 0.5 ? 1.0 : 0.6);
        float vv = rr - R0;
        hazeAcc += smoothstep(-0.02, 0.02, vv) * exp(-vv / 0.12) * 0.5;
#else
        float yc = curveY(p.x, t);
        vec2 q = vec2((p.x - t * FLOW * mix(0.7, 1.0, depth)) * cs, (p.y - yc) * cs);
        float sp = spread(p.x);
        hazeAcc += exp(-pow((p.y - yc) / (sp * 1.4), 2.0)) * cometW(p.x, t) * 0.5;
#endif
        for (int j = -1; j <= 1; ++j)
        for (int i = -1; i <= 1; ++i) {
            vec2 cell = floor(q) + vec2(float(i), float(j));
#if MODE == 1
            vec2 key = vec2(mod(cell.x, n), cell.y);
#else
            vec2 key = cell;
#endif
            float h = hash12(key + fl * 31.7);
            vec3 hh = hash32(key + fl * 11.3 + 5.0);
            vec2 cq = cell + 0.5 + (hh.xy - 0.5) * 0.85;
            vec2 c;
            float w;
            vec2 dir;
#if MODE == 1
            float a = (cq.x + rot_ * NRING / TAU) / n * TAU - PI;
            float rad = R0 + cq.y / cs;
            c = rad * vec2(cos(a), sin(a));
            float v = rad - R0;
            w = smoothstep(-0.02, 0.02, v) * (0.3 + 0.9 * exp(-v / 0.09));
            dir = vec2(-sin(a), cos(a));
#else
            float x = cq.x / cs + t * FLOW * mix(0.7, 1.0, depth);
            float ofs = cq.y / cs;
            c = vec2(x, curveY(x, t) + ofs);
            float s2 = spread(x);
            w = exp(-pow(ofs / s2, 2.0)) * cometW(x, t);
            dir = normalize(vec2(1.0, SLOPE + AMP * FREQ * cos(x * FREQ + t * WAVE)));
#endif
            if (h > DENS * density * w) continue;
            vec2 d = p - c;
            float r = max(1.5 * SIZE / cs * (0.4 + 0.6 * hh.z * hh.z) * mix(0.75, 1.3, depth), minR());
            if (dot(d, d) > r * r * 60.0) continue;
            float tw = 0.5 + 0.5 * sin(t * 6.0 * (0.5 + hh.z) + hh.x * TAU);
            float kind = fract(h * 13.7 + hh.y * 5.1);
            light += sparkle(d, r, kind, tw, pal(fract(hh.x * 3.3 + hh.z)), dir) * mix(0.55, 1.0, depth);
        }
    }
    light += color * hazeAcc * HAZE;
    vec3 base = src.rgb;
#if MODE == 1
    base *= 1.0 - 0.35 * intensity * smoothstep(R0 - 0.02, R0 + 0.12, length(p));
#endif
    fragColor = vec4(addLight(base, light, intensity), src.a);
}
""",
    variants=[
        Variant("luz-de-las-estrellas", "Luz de las estrellas", "Starlight", photo="fx-citynight-03", thumb=1.5,
                defines={"AMP": 0.1, "FREQ": 3.5, "WAVE": 0.8, "SLOPE": -0.3, "YOFF": 0.05, "WID": 0.045,
                         "WIDG": 2.2, "FLOW": 0.18, "CELL": 34.0, "DENS": 0.95, "SIZE": 0.14, "HUEVAR": 0.0,
                         "WHITEMIX": 0.6, "HAZE": 0.2},
                params={"color": "#d6e6ff"},
                tags=["estrellas", "stars", "luz", "light", "estela", "trail", "galaxia", "galaxy"]),
        Variant("particulas-doradas", "Partículas doradas", "Golden particles", photo="fx-hair-01", thumb=1.6,
                defines={"AMP": 0.06, "FREQ": 4.0, "WAVE": 0.5, "SLOPE": -0.45, "YOFF": 0.08, "WID": 0.1,
                         "WIDG": -0.6, "FLOW": 0.1, "CELL": 32.0, "DENS": 1.0, "SIZE": 0.17, "COMET": 1.0,
                         "CPERIOD": 3.0, "TAIL": 0.7, "STARFRAC": 0.12, "HAZE": 0.35},
                params={"color": "#ffbe55"},
                tags=["particulas", "particles", "dorado", "gold", "cometa", "comet", "magia", "magic"]),
        Variant("particulas-en-movimiento", "Partículas en movimiento", "Particles in motion", photo="skater",
                thumb=1.3,
                defines={"AMP": 0.08, "FREQ": 2.5, "WAVE": 1.5, "SLOPE": 0.0, "YOFF": 0.05, "WID": 0.1, "WIDG": 0.6,
                         "FLOW": 0.6, "CELL": 26.0, "DENS": 0.75, "STREAK": 1.2, "SIZE": 0.13, "STARFRAC": 0.25, "HAZE": 0.2,
                         "HUEVAR": 0.12, "WHITEMIX": 0.6},
                params={"color": "#ffe3a0"},
                tags=["particulas", "particles", "movimiento", "motion", "velocidad", "speed", "estela", "trail"]),
        Variant("anillo-de-brillos", "Anillo de brillos", "Glitter ring", photo="fx-woman-08", thumb=1.2,
                defines={"MODE": "1", "R0": 0.36, "NRING": 90.0, "CELL": 26.0, "FLOW": 0.35, "DENS": 0.8,
                         "SIZE": 0.16, "STARFRAC": 0.12, "HAZE": 0.35, "WHITEMIX": 0.35},
                params={"color": "#ffcf6e"},
                tags=["anillo", "ring", "brillos", "glitter", "circulo", "circle", "dorado", "gold", "bling"]),
    ],
)

# ------------------------------------------------------------------------------------------------- bursts
BURST = Family(
    key="pt_burst", category="particulas",
    params=[INTENSITY, SPEED, colour("#fff0c0")],
    photo="dark", tags=["estallido", "burst", "estrellas", "stars", "fuegos artificiales", "fireworks"],
    defines={"MODE": "0", "PERIOD": 1.6, "RAD": 0.32, "GRAV": 0.08, "PSIZE": 0.016, "HUEVAR": 0.1, "BRVAR": 0.2,
             "WHITEMIX": 0.5, "FLASH": 0.6},
    body=COMMON + r"""
vec3 burst(vec2 p, vec2 c, float ph, float seed, float R, vec3 tint, float t) {
    vec3 acc = vec3(0.0);
    if (length(p - c) > R * 1.5 + 0.08) return acc;
    float ex = 1.0 - pow(1.0 - ph, 3.0);
    float fade = pow(1.0 - ph, 1.4) * smoothstep(0.0, 0.1, ph) * mix(0.04, 1.0, smoothstep(0.15, 0.5, ex));
    for (int i = 0; i < 20; ++i) {
        float fi = float(i);
        vec3 h = hash32(vec2(fi * 1.31 + seed, seed * 0.77 + 2.0));
        float ang = (fi + h.x * 0.7) / 20.0 * TAU;
        vec2 dir = vec2(cos(ang), sin(ang));
        float sp = mix(0.5, 1.0, h.y);
        vec2 pos = c + dir * R * sp * ex + vec2(0.0, GRAV * ph * ph);
        vec2 d = p - pos;
        float r = PSIZE * mix(0.6, 1.2, h.z) * (1.0 - 0.4 * ph);
        float fl = 0.65 + 0.35 * sin(t * 25.0 + h.z * TAU);
        vec3 col = mix(tint, pal(h.x), 0.5);
        // The trail behind the spark, shorter as it slows down.
        float tr = sdSegment(p, pos, pos - dir * R * sp * 0.35 * (1.0 - ph));
        acc += col * exp(-tr * tr / (r * r * 0.25)) * 0.7 * fade;
        float st = star5(rot(h.y * TAU + t * 2.0) * d, r * 1.6, 1.2 / max(u_resolution.y, 1.0));
        acc += mix(col, vec3(1.0), 0.5) * (st + 0.6 * halo(d, r * 0.6)) * fade * fl;
    }
    // A flash in the middle when it goes off.
    acc += tint * exp(-length(p - c) / (R * 0.08)) * FLASH * exp(-ph * 14.0);
    return acc;
}

void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    vec3 light = vec3(0.0);
#if MODE == 0
    // One burst in the middle, again and again (two of them overlap so it never stops).
    for (int k = 0; k < 2; ++k) {
        float off = float(k) * 0.5;
        float n = floor(t / PERIOD + off);
        float ph = fract(t / PERIOD + off);
        vec2 c = (hash22(vec2(n, float(k))) - 0.5) * vec2(0.12, 0.08);
        light += burst(p, c, ph, n * 7.0 + float(k) * 3.0, RAD, color, t);
    }
#else
    // Fireworks: three bursts here and there, each with its own colour.
    for (int k = 0; k < 3; ++k) {
        float off = float(k) / 3.0;
        float n = floor(t / PERIOD + off);
        float ph = fract(t / PERIOD + off);
        vec2 hc = hash22(vec2(n * 1.7, float(k) * 5.1));
        vec2 c = (hc - 0.5) * vec2(aspect() * 0.75, 0.55) - vec2(0.0, 0.05);
        vec3 tint = hueShift(color, hash11(n * 3.1 + float(k)) * HUEVAR * 4.0);
        light += burst(p, c, ph, n * 5.0 + float(k) * 11.0, RAD * mix(0.7, 1.1, hc.y), tint, t);
    }
#endif
    fragColor = vec4(addLight(src.rgb, light, intensity), src.a);
}
""",
    variants=[
        Variant("estallido-de-estrellas", "Estallido de estrellas", "Star burst", photo="fx-citynight-06", thumb=0.5,
                defines={"MODE": "0", "PERIOD": 1.6, "RAD": 0.42, "GRAV": 0.06, "PSIZE": 0.02, "WHITEMIX": 0.6},
                params={"color": "#ffe9b0"},
                tags=["estallido", "burst", "estrellas", "stars", "explosion", "brillo", "sparkle"]),
        Variant("fuegos-de-estrellas", "Fuegos de estrellas", "Star fireworks", photo="fx-citynight-01", thumb=0.9,
                defines={"MODE": "1", "PERIOD": 1.8, "RAD": 0.26, "GRAV": 0.1, "PSIZE": 0.018, "HUEVAR": 0.25,
                         "WHITEMIX": 0.3, "FLASH": 0.25},
                params={"color": "#ff9ad5"},
                tags=["fuegos artificiales", "fireworks", "estrellas", "stars", "fiesta", "party", "celebracion"]),
    ],
)

# ------------------------------------------------------------------------------------------------- bokeh
BOKEH = Family(
    key="pt_bokeh", category="particulas",
    params=[INTENSITY, SPEED, DENSITY, colour("#e8eef8")],
    photo="dark", tags=["bokeh", "desenfoque", "luces", "lights", "circulos", "circles"],
    defines={"MODE": "0", "ZS": 0.12, "DENS": 0.5, "BSIZE": 0.33, "HUEVAR": 0.05, "BRVAR": 0.35, "WHITEMIX": 0.2,
             "EDGE": 0.22, "SPARK": 0.0},
    body=COMMON + r"""
vec3 bokehLayer(vec2 q, float seed, float aa, float bright, float t, float edgeMode) {
    vec3 acc = vec3(0.0);
    for (int j = -1; j <= 1; ++j)
    for (int i = -1; i <= 1; ++i) {
        vec2 cell = floor(q) + vec2(float(i), float(j));
        float h = hash12(cell + seed);
        vec3 hh = hash32(cell + seed * 1.9);
        vec2 c = cell + 0.5 + (hh.xy - 0.5) * 0.9
                 + 0.12 * vec2(sin(t * 0.5 + hh.z * TAU), cos(t * 0.4 + hh.x * TAU));
        float w = 1.0;
        if (edgeMode > 0.5) w = 0.0;   // set by the caller through the frame mask below
        if (h > DENS * density) continue;
        float r = BSIZE * (0.5 + 0.5 * hh.z);
        float pulse = 0.75 + 0.25 * sin(t * (0.8 + hh.y) + hh.x * TAU);
        acc += pal(fract(hh.x * 4.1 + hh.y)) * bokehDisc(q - c, r, aa + r * 0.12) * bright * pulse;
    }
    return acc;
}

void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    vec3 light = vec3(0.0);
#if MODE == 0
    // Three layers that come towards the camera, growing and fading in and out.
    for (int k = 0; k < 3; ++k) {
        float z = fract(t * ZS + float(k) / 3.0);
        float zoom = mix(0.55, 2.4, z * z);
        float sc = 3.2 / zoom;
        vec2 q = p * sc + vec2(float(k) * 17.3, 0.0);
        float aa = 2.0 * sc / max(u_resolution.y, 1.0);
        float bright = bump(z) * 0.55;
        light += bokehLayer(q, 3.0 + float(k) * 7.0 + floor(t * ZS + float(k) / 3.0) * 13.0, aa, bright, t, 0.0);
    }
#else
    // A frame of bokeh with glints on the edges of the picture.
    float e = min(aspect() * 0.5 - abs(p.x), 0.5 - abs(p.y));
    float fw = smoothstep(EDGE, 0.0, e);
    for (int k = 0; k < 2; ++k) {
        float sc = k == 0 ? 7.0 : 4.0;
        vec2 q = p * sc + vec2(t * 0.15 * (1.0 + float(k)), float(k) * 9.1);
        float aa = 2.0 * sc / max(u_resolution.y, 1.0);
        light += bokehLayer(q, 5.0 + float(k) * 11.0, aa, 0.9, t, 0.0) * fw;
    }
    // Glints that come and go on the frame.
    vec2 q = p * 10.0;
    for (int j = -1; j <= 1; ++j)
    for (int i = -1; i <= 1; ++i) {
        vec2 cell = floor(q) + vec2(float(i), float(j));
        vec3 hh = hash32(cell + 41.0);
        vec2 c = (cell + 0.5 + (hh.xy - 0.5) * 0.8) / 10.0;
        float ce = min(aspect() * 0.5 - abs(c.x), 0.5 - abs(c.y));
        if (hash12(cell + 7.0) > SPARK * smoothstep(EDGE * 1.2, 0.0, ce)) continue;
        float tw = pow(0.5 + 0.5 * sin(t * 4.0 * (0.6 + hh.z) + hh.y * TAU), 3.0);
        light += mix(color, vec3(1.0), 0.6) * twinkle(p - c, 0.025 * (0.5 + hh.z)) * tw;
    }
    light += color * fw * fw * 0.3;
#endif
    fragColor = vec4(addLight(src.rgb, light, intensity), src.a);
}
""",
    variants=[
        Variant("bokeh-3d", "Bokeh 3D", "3D bokeh", photo="fx-cyber-03", thumb=1.5,
                defines={"MODE": "0", "ZS": 0.15, "DENS": 0.45, "BSIZE": 0.3, "HUEVAR": 0.04, "WHITEMIX": 0.4},
                params={"color": "#e2e8f2"},
                tags=["bokeh", "3d", "desenfoque", "blur", "luces", "lights", "profundidad", "depth"]),
        Variant("chispa", "Chispa", "Spark", photo="fx-dancer-03", thumb=1.2,
                defines={"MODE": "1", "DENS": 0.8, "BSIZE": 0.34, "HUEVAR": 0.35, "BRVAR": 0.25, "WHITEMIX": 0.2,
                         "EDGE": 0.24, "SPARK": 1.0},
                params={"color": "#ffc46b"},
                tags=["chispa", "spark", "bokeh", "marco", "frame", "dorado", "gold", "brillo"]),
    ],
)

FAMILIES = [FALL, FIELD, FIREFLY, PATH, BURST, BOKEH]
