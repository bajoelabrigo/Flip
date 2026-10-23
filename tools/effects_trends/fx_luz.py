"""Efectos › Tendencias, Luz y destellos (first half of the catalog section, up to «Fuga de luz 1»).

Light leaks, lens flares (ghosts, streaks, halo), sun rays and spotlights, bokeh, glows and flashes, disco
lights. Every light is added with a screen blend so whites never clip hard, and moves on u_time.
"""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)


def colour(default: str) -> Param:
    return Param("color", "Colour", default=default)


# ---------------------------------------------------------------------------------------------------------------
# Light leaks: three coloured blobs that drift near the edges, warped by noise, with optional streaks. BURN turns
# the same field into a film burn (a hot colour ramp that eats into the picture).
LEAK = Family(
    key="luz_leak", category="luz", params=[INTENSITY, SPEED, colour("#ff6a1a")], photo="woman",
    tags=["fuga de luz", "light leak", "luz", "light", "pelicula", "film", "calido", "warm"],
    defines={"COL_B": "#e01a0c", "COL_C": "#ffc040", "P1": (0.0, 0.3), "P2": (1.0, 0.7), "P3": (0.05, 0.95),
             "R1": 0.35, "R2": 0.35, "R3": 0.25, "WARP": 0.5, "STREAK": 0.0, "STREAK_ANG": 0.6, "BURN": 0.0,
             "GAIN": 1.0, "WASH": 0.0},
    body=r"""
vec2 at(vec2 uv) { return (uv - 0.5) * vec2(aspect(), 1.0); }
vec3 field(vec2 p, float t) {
    vec2 w = vec2(fbm(p * 1.4 + vec2(t * 0.11, -t * 0.07)), fbm(p * 1.4 + vec2(-t * 0.09, t * 0.13) + 5.2)) - 0.5;
    vec2 q = p + w * WARP;
    vec2 c1 = at(P1) + 0.13 * vec2(sin(t * 0.70), cos(t * 0.53));
    vec2 c2 = at(P2) + 0.13 * vec2(cos(t * 0.61 + 1.0), sin(t * 0.47 + 2.0));
    vec2 c3 = at(P3) + 0.10 * vec2(sin(t * 0.43 + 4.0), cos(t * 0.71 + 3.0));
    vec3 acc = color * exp(-dot(q - c1, q - c1) / (R1 * R1));
    acc += COL_B * exp(-dot(q - c2, q - c2) / (R2 * R2));
    acc += COL_C * exp(-dot(q - c3, q - c3) / (R3 * R3));
    return acc;
}
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    vec3 L = field(p, t);
    if (STREAK > 0.0) {
        vec2 dir = vec2(cos(STREAK_ANG), sin(STREAK_ANG));
        vec2 per = vec2(-dir.y, dir.x);
        float s = fbm(vec2(dot(p, per) * 7.0 - t * 0.35, dot(p, dir) * 0.8 + t * 0.05));
        float band = pow(smoothstep(0.35, 0.8, s), 2.0) * (0.4 + 0.6 * fbm(p * 1.2 - t * 0.1));
        L += mix(color, COL_C, 0.5 + 0.5 * sin(dot(p, per) * 4.0 + t)) * band * STREAK;
    }
    float breath = 0.78 + 0.22 * sin(t * 1.3) + 0.08 * (vnoise(vec2(t * 7.0, 2.0)) - 0.5);
    vec3 col;
    if (BURN > 0.5) {
        float heat = dot(L, vec3(0.55, 0.4, 0.05)) * 1.7 + (fbm(p * 2.2 + vec2(t * 0.35, -t * 0.2)) - 0.5) * 0.7;
        heat *= breath;
        vec3 ramp = mix(color * 0.7, COL_B, smoothstep(0.25, 0.55, heat));
        ramp = mix(ramp, COL_C, smoothstep(0.5, 0.8, heat));
        ramp = mix(ramp, vec3(1.0, 0.97, 0.9), smoothstep(0.8, 1.05, heat));
        float amt = smoothstep(0.12, 0.7, heat) * intensity;
        col = mix(src.rgb, screen(src.rgb, ramp), sat(amt));
        col = mix(col, ramp, sat(smoothstep(0.75, 1.1, heat) * intensity * 0.7));
        col = mix(col, col * vec3(1.08, 0.95, 0.82), 0.5 * sat(intensity));
    } else {
        col = addLight(src.rgb, L * GAIN * breath, intensity);
    }
    if (WASH > 0.0) col = mix(col, screen(col, color * 0.35), WASH * sat(intensity));
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[
        Variant("efecto-de-fuga-de-luz-02", "Efecto de fuga de luz 02", "Light leak effect 02", photo="fx-woman-02",
                defines={"P1": (-0.05, 0.25), "P2": (1.02, 0.55), "P3": (0.1, 1.0), "R1": 0.42, "R2": 0.4,
                         "R3": 0.3, "STREAK": 0.6, "STREAK_ANG": 1.2, "GAIN": 1.1},
                tags=["naranja", "orange"], thumb=1.0),
        Variant("fuga-de-luz-4", "Fuga de luz 4", "Light leak 4", photo="dark", params={"color": "#e8202a"},
                defines={"COL_B": "#1fd36a", "COL_C": "#2a6dff", "P1": (0.25, 0.4), "P2": (0.75, 0.45),
                         "P3": (0.5, 0.95), "R1": 0.28, "R2": 0.3, "R3": 0.3, "GAIN": 0.85},
                tags=["rgb", "colores", "colours"], thumb=1.5),
        Variant("fuga-de-luz-6", "Fuga de luz 6", "Light leak 6", photo="fx-hair-01", params={"color": "#ff7a20"},
                defines={"COL_B": "#c8186a", "COL_C": "#7a3cff", "P1": (0.2, 0.15), "P2": (0.9, 0.85),
                         "P3": (0.95, 0.15), "R1": 0.4, "R2": 0.4, "R3": 0.3, "STREAK": 0.9, "STREAK_ANG": 0.9,
                         "GAIN": 1.0, "WASH": 0.25},
                tags=["morado", "purple", "rayas", "streaks"], thumb=1.4),
        Variant("fuga-de-luz-1", "Fuga de luz 1", "Light leak 1", photo="dark", params={"color": "#2a7dff"},
                defines={"COL_B": "#1a3a8a", "COL_C": "#46c8ff", "P1": (0.6, 0.85), "P2": (0.3, 1.05),
                         "P3": (0.8, 0.6), "R1": 0.3, "R2": 0.35, "R3": 0.18, "GAIN": 0.75},
                tags=["azul", "blue", "suave", "soft"], thumb=1.2),
        Variant("quemadura-de-pelicula", "Quemadura de película", "Film burn", photo="fx-walk-04",
                params={"color": "#8a1a06"},
                defines={"BURN": 1.0, "COL_B": "#ff6a10", "COL_C": "#ffc24a", "P1": (1.0, 0.2),
                         "P2": (0.85, 0.9), "P3": (0.0, 0.0), "R1": 0.55, "R2": 0.45, "R3": 0.3, "WARP": 0.8},
                tags=["quemadura", "burn", "naranja", "orange", "vintage"], thumb=1.6),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Lens flares: a bright source with a starburst, a chromatic halo ring, an anamorphic streak, ghosts along the
# axis through the centre, an optional beam, a haze and a coloured edge glow (prismatic). The source drifts.
FLARE = Family(
    key="luz_flare", category="luz", params=[INTENSITY, SPEED, colour("#ffd9a0")], photo="dark",
    tags=["destello", "flare", "lente", "lens", "sol", "sun"],
    defines={"SRC": (0.3, 0.15), "DRIFT": 0.06, "CORE": 0.05, "RAYS": 0.6, "RAYS_FALL": 4.0, "HALO_R": 0.0,
             "HALO": 0.0, "STREAK": 0.0, "STREAK_COL": "#7ab8ff", "STREAK_L": 0.5, "STREAK_W": 0.012,
             "GHOSTS": 0.6, "GHOST_R": 0.06, "GHOST_COL": "#9fd0ff", "BEAM": 0.0, "BEAM_COL": "#5a8cff",
             "BEAM_W": 0.06, "BEAM_L": 0.9, "BEAM_ANG": 99.0, "HAZE": 0.0, "EDGE": 0.0, "EDGE_COL": "#8a3cff"},
    body=r"""
float ringAt(float r, float R, float w) { float x = (r - R) / w; return exp(-x * x); }
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    vec2 s = (SRC + DRIFT * vec2(sin(t * 0.55), 0.6 * cos(t * 0.42)) - 0.5) * vec2(aspect(), 1.0);
    vec2 d = p - s;
    float r = length(d);
    float a = atan(d.y, d.x);
    float flick = 0.93 + 0.07 * vnoise(vec2(t * 6.0, 1.3));
    vec3 L = vec3(0.0);
    // Core and glow.
    L += color * (exp(-r * r / (CORE * CORE)) * 1.3 + 0.45 * exp(-r / (CORE * 3.0)));
    L += vec3(1.0) * exp(-r * r / (CORE * CORE * 0.12));
    // Starburst (integer frequencies: no seam at the back of the angle).
    float st = pow(abs(cos(a * 7.0 + t * 0.15)), 40.0) + 0.7 * pow(abs(cos(a * 11.0 - t * 0.11 + 1.0)), 60.0)
             + 0.4 * pow(abs(cos(a * 17.0 + t * 0.07 + 2.0)), 80.0);
    L += mix(color, vec3(1.0), 0.4) * st * exp(-r * RAYS_FALL) * RAYS;
    // Chromatic halo ring.
    if (HALO > 0.0) {
        float w = HALO_R * 0.07;
        vec3 ring = vec3(ringAt(r, HALO_R * 1.04, w), ringAt(r, HALO_R, w), ringAt(r, HALO_R * 0.96, w));
        L += ring * HALO * (0.75 + 0.25 * sin(a * 3.0 + t));
    }
    // Anamorphic streak.
    if (STREAK > 0.0) {
        float sx = exp(-abs(d.y) / STREAK_W) * exp(-abs(d.x) / STREAK_L);
        sx += 0.35 * exp(-abs(d.y) / (STREAK_W * 5.0)) * exp(-abs(d.x) / (STREAK_L * 0.6));
        L += STREAK_COL * sx * STREAK * (0.85 + 0.15 * sin(t * 2.0));
    }
    // Ghosts on the line through the source and the centre of the frame.
    if (GHOSTS > 0.0) {
        for (int i = 0; i < 6; ++i) {
            float fi = float(i);
            float k = 0.55 - fi * 0.38 + 0.08 * sin(fi * 3.1);
            vec2 g = s * k;
            float gr = GHOST_R * (0.45 + 1.1 * hash11(fi * 7.3 + 1.0));
            float gd = length(p - g);
            float disk = smoothstep(gr, gr * 0.75, gd);
            float rim = exp(-pow((gd - gr * 0.92) / (gr * 0.12), 2.0));
            vec3 gc = mix(GHOST_COL, hsv2rgb(vec3(hash11(fi * 3.7 + 2.0), 0.55, 1.0)), 0.5);
            L += gc * (disk * 0.22 + rim * 0.25) * GHOSTS;
        }
    }
    // Beam from the source (towards the centre when BEAM_ANG is unset).
    if (BEAM > 0.0) {
        vec2 bd = BEAM_ANG > 50.0 ? normalize(-s + 1e-4) : vec2(cos(BEAM_ANG), sin(BEAM_ANG));
        float along = dot(d, bd);
        float perp = abs(dot(d, vec2(-bd.y, bd.x)));
        float wid = BEAM_W * (0.4 + abs(along) * 1.2);
        float b = exp(-perp * perp / (wid * wid)) * exp(-max(along, 0.0) / BEAM_L) * smoothstep(-0.05, 0.05, along);
        b *= 0.75 + 0.25 * sin(along * 9.0 - t * 2.0);
        L += BEAM_COL * b * BEAM;
    }
    if (HAZE > 0.0) L += mix(color, vec3(0.85, 0.9, 1.0), 0.5) * exp(-r * 1.6) * HAZE;
    if (EDGE > 0.0) {
        float ex = v_texCoord.x;
        float e = exp(-ex / 0.07) * (0.55 + 0.6 * fbm(vec2(v_texCoord.y * 5.0, t * 0.6)));
        e += 0.5 * exp(-ex / 0.22) * (0.5 + 0.5 * sin(v_texCoord.y * 6.0 + t * 1.5));
        L += EDGE_COL * e * EDGE * (0.8 + 0.2 * sin(t * 3.0));
    }
    vec3 col = addLight(src.rgb, L * flick, intensity);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("luz-del-sol-05", "Luz del sol 05", "Sunlight 05", photo="dark",
                defines={"SRC": (0.32, 0.18), "GHOSTS": 1.0, "GHOST_R": 0.07, "RAYS": 0.5, "HAZE": 0.25,
                         "HALO": 0.25, "HALO_R": 0.16},
                tags=["luz del sol", "sunlight"], thumb=1.0),
        Variant("explosion-prismatica", "Explosión prismática", "Prismatic burst", photo="dark",
                params={"color": "#d8e4ff"},
                defines={"SRC": (0.48, 0.4), "DRIFT": 0.04, "CORE": 0.035, "STREAK": 1.2, "STREAK_L": 0.7,
                         "STREAK_COL": "#6a9cff", "GHOSTS": 0.5, "GHOST_COL": "#b07aff", "EDGE": 1.1,
                         "RAYS": 0.4, "HALO": 0.35, "HALO_R": 0.09},
                tags=["prisma", "prism", "morado", "purple", "anamorfico", "anamorphic"], thumb=1.2),
        Variant("destello-de-la-lente-5", "Destello de la lente 5", "Lens flare 5", photo="fx-beach-03",
                params={"color": "#fff1dc"},
                defines={"SRC": (0.1, 0.12), "DRIFT": 0.08, "CORE": 0.1, "RAYS": 0.08, "RAYS_FALL": 3.0,
                         "HAZE": 0.8, "HALO": 0.45, "HALO_R": 0.42, "GHOSTS": 0.5, "GHOST_R": 0.11},
                tags=["suave", "soft", "brumoso", "hazy"], thumb=1.5),
        Variant("destello-de-la-lente-3", "Destello de la lente 3", "Lens flare 3", photo="dark",
                params={"color": "#ffc6d6"},
                defines={"SRC": (0.88, 0.95), "DRIFT": 0.05, "CORE": 0.07, "RAYS": 0.3, "BEAM": 1.0,
                         "BEAM_COL": "#ff8fb4", "BEAM_W": 0.08, "BEAM_L": 1.2, "BEAM_ANG": -2.3,
                         "GHOSTS": 0.35, "HAZE": 0.2},
                tags=["rosa", "pink", "diagonal"], thumb=1.4),
        Variant("destello-de-lente-azul", "Destello de lente azul", "Blue lens flare", photo="dark",
                params={"color": "#e4efff"},
                defines={"SRC": (0.1, 0.1), "CORE": 0.06, "RAYS": 0.7, "BEAM": 0.9, "BEAM_COL": "#4a7cff",
                         "BEAM_W": 0.05, "BEAM_L": 1.1, "GHOSTS": 0.8, "GHOST_COL": "#7a8cff", "HAZE": 0.2},
                tags=["azul", "blue"], thumb=1.0),
        Variant("sol-en-la-esquina", "Sol en la esquina", "Sun in the corner", photo="dark",
                defines={"SRC": (0.04, 0.04), "DRIFT": 0.03, "CORE": 0.09, "RAYS": 1.0, "RAYS_FALL": 2.5,
                         "HALO": 0.5, "HALO_R": 0.3, "GHOSTS": 0.6, "GHOST_R": 0.08, "HAZE": 0.35},
                tags=["esquina", "corner", "rayos", "rays"], thumb=1.2),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Rays from a point: god rays, beams, spotlights (with the rest darkened) and a pool on the floor, rainbow neon
# rays round the subject, and STAGE: six coloured beams sweeping up from the floor.
RAYS = Family(
    key="luz_rays", category="luz", params=[INTENSITY, SPEED, colour("#ffc35a")], photo="woman",
    tags=["rayos", "rays", "haz", "beam", "luz", "light"],
    defines={"ORIGIN": (0.5, -0.1), "DIR": 1.5708, "CONE": 1.0, "SWAY": 0.08, "FALL": 1.2, "FILL": 0.4,
             "RAYAMT": 0.9, "SHARP": 3.0, "RAINBOW": 0.0, "PROTECT": 0.0, "DARK": 0.0, "POOL": 0.0,
             "POOL_AT": (0.5, 0.85), "STAGE": 0.0, "STAGE_B": "#2a6dff", "DUST": 0.3},
    body=r"""
float rayPattern(float a, float t) {
    float n = 0.5 * sin(a * 13.0 + t * 0.6 + 1.5 * sin(a * 5.0 - t * 0.25))
            + 0.3 * sin(a * 29.0 - t * 0.9 + 2.0) + 0.2 * sin(a * 47.0 + t * 1.3 + 4.0);
    return pow(sat(0.5 + 0.5 * n), SHARP);
}
float angDiff(float a, float b) { return atan(sin(a - b), cos(a - b)); }
float dust(vec2 p, float t) {
    vec2 q = p * 9.0 + vec2(t * 0.15, -t * 0.25);
    vec2 c = floor(q), f = fract(q) - 0.5;
    vec2 o = (hash22(c) - 0.5) * 0.7;
    float tw = 0.5 + 0.5 * sin(t * 2.0 + hash12(c) * 30.0);
    return smoothstep(0.08, 0.0, length(f - o)) * step(0.6, hash12(c + 4.1)) * tw;
}
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    vec3 L = vec3(0.0);
    vec3 base = src.rgb;
    if (STAGE > 0.5) {
        for (int i = 0; i < 6; ++i) {
            float fi = float(i);
            vec2 o = (vec2((fi + 0.5) / 6.0, 1.03) - 0.5) * vec2(aspect(), 1.0);
            float ang = -1.5708 + 0.5 * sin(t * 0.9 + fi * 1.7) * (mod(fi, 2.0) < 0.5 ? 1.0 : -1.0);
            vec2 d = p - o;
            float r = length(d);
            float da = abs(angDiff(atan(d.y, d.x), ang));
            vec3 c = mod(fi, 2.0) < 0.5 ? color : STAGE_B;
            float beam = smoothstep(0.14, 0.0, da) * exp(-r * 1.1) + 1.6 * smoothstep(0.03, 0.0, da) * exp(-r * 2.2);
            L += c * (beam * 0.8 + 1.8 * exp(-r * r / 0.002));
        }
        base *= 0.85;
    } else {
        vec2 o = (ORIGIN - 0.5) * vec2(aspect(), 1.0);
        vec2 d = p - o;
        float r = length(d);
        float a = atan(d.y, d.x);
        float dir = DIR + SWAY * sin(t * 0.7);
        float cone = CONE > 3.0 ? 1.0 : smoothstep(CONE, CONE * 0.35, abs(angDiff(a, dir)));
        float fall = exp(-r * FALL);
        float rays = rayPattern(a, t);
        vec3 c = color;
        if (RAINBOW > 0.5) c = hsv2rgb(vec3(fract(a / TAU + t * 0.08), 0.75, 1.0));
        float k = cone * (FILL + RAYAMT * rays) * fall;
        if (PROTECT > 0.0) k *= mix(1.0, smoothstep(0.08, 0.42, r), PROTECT);
        L += c * k;
        L += vec3(1.0) * dust(p, t) * cone * fall * DUST;
        if (DARK > 0.0) base *= mix(1.0 - DARK * sat(intensity), 1.0, sat(cone * (0.35 + exp(-r * 0.8))));
        if (POOL > 0.0) {
            vec2 pc = (POOL_AT + vec2(0.06 * sin(t * 0.7), 0.0) - 0.5) * vec2(aspect(), 1.0);
            vec2 e = (p - pc) * vec2(1.0, 4.0);
            float el = length(e);
            L += color * POOL * (0.8 * exp(-el * el / 0.03) + 0.9 * exp(-pow((el - 0.2) / 0.02, 2.0)));
        }
    }
    vec3 col = addLight(base, L, intensity);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("rayo-dorado", "Rayo dorado", "Golden rays", photo="dark",
                defines={"CONE": 1.1, "FALL": 1.4, "FILL": 0.35}, tags=["dorado", "golden", "dios", "god rays"],
                thumb=1.2),
        Variant("rayo-de-luz", "Rayo de luz", "Light beam", photo="dark", params={"color": "#ffe2b0"},
                defines={"ORIGIN": (0.98, -0.05), "DIR": 2.45, "CONE": 0.32, "SWAY": 0.05, "FALL": 1.0,
                         "FILL": 0.5, "RAYAMT": 0.7},
                tags=["diagonal", "haz", "beam"], thumb=1.4),
        Variant("luz-del-sol-03", "Luz del sol 03", "Sunlight 03", photo="dark",
                defines={"ORIGIN": (0.5, -0.05), "CONE": 0.42, "SWAY": 0.06, "FALL": 1.0, "FILL": 0.5,
                         "POOL": 0.6, "POOL_AT": (0.5, 0.8)},
                tags=["foco", "spotlight", "escenario", "stage"], thumb=1.0),
        Variant("foco-final", "Foco final", "Spotlight finish", photo="lighthouse", params={"color": "#ffffff"},
                defines={"ORIGIN": (0.5, -0.12), "CONE": 0.3, "SWAY": 0.05, "FALL": 0.6, "FILL": 0.55,
                         "RAYAMT": 0.3, "DARK": 0.8, "DUST": 0.15},
                tags=["foco", "spotlight", "final", "ending"], thumb=1.2),
        Variant("fiebre-del-neon", "Fiebre del neón", "Neon fever", photo="fashion",
                defines={"ORIGIN": (0.5, 0.42), "CONE": 4.0, "SWAY": 0.0, "FALL": 0.9, "FILL": 0.05,
                         "RAYAMT": 1.3, "SHARP": 6.0, "RAINBOW": 1.0, "PROTECT": 0.85, "DUST": 0.0},
                tags=["neon", "arcoiris", "rainbow", "rayos"], thumb=1.0),
        Variant("luces-de-escenario", "Luces de escenario", "Stage lights", photo="dark",
                params={"color": "#ff2fc0"}, defines={"STAGE": 1.0},
                tags=["escenario", "stage", "concierto", "concert", "fiesta", "party"], thumb=1.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Bokeh: soft discs with a brighter rim in three depth layers, drifting and twinkling. Palettes: the colour
# parameter, rainbow, warm gold, grey bubbles. FRAME keeps them on the edges, DEFOCUS blurs the picture behind,
# FALL makes them rain and TOPGLOW adds a golden haze at the top.
BOKEH = Family(
    key="luz_bokeh", category="luz",
    params=[INTENSITY, SPEED, colour("#ffd27a"), Param("size", "Size", 0.5, 1.5, 1.0),
            Param("density", "Density", 0.2, 2.0, 1.0)],
    photo="citynight", tags=["bokeh", "luces", "lights", "desenfoque", "blur", "circulos", "circles"],
    defines={"PAL": 0.0, "RIM": 0.5, "SOFT": 0.25, "DRIFT": (0.05, -0.03), "FALL": 0.0, "FRAME": 0.0,
             "DEFOCUS": 0.0, "TOPGLOW": 0.0, "GAIN": 1.0, "SCALE": 1.0, "FILLK": 0.55},
    body=r"""
vec3 palette(float h) {
    if (PAL < 0.5) return color * (0.75 + 0.5 * h);
    if (PAL < 1.5) return hsv2rgb(vec3(h, 0.6, 1.0));
    if (PAL < 2.5) return mix(vec3(1.0, 0.72, 0.32), vec3(1.0, 0.93, 0.75), h);
    if (PAL < 3.5) return vec3(0.75 + 0.2 * h);
    // city: white, warm, red and blue lights
    return h < 0.4 ? vec3(1.0, 0.9, 0.75) : (h < 0.65 ? vec3(1.0, 0.3, 0.25) : (h < 0.85 ? vec3(0.4, 0.6, 1.0)
                                                                                    : vec3(1.0, 0.75, 0.3)));
}
vec3 layer(vec2 p, float t, float sc, float seed, float bright) {
    vec2 q = p * sc;
    q += DRIFT * t * sc + vec2(sin(t * 0.35 + seed), cos(t * 0.27 + seed * 1.3)) * 0.25;
    q.y -= FALL * t * sc * 0.35;
    vec2 cell = floor(q), f = fract(q) - 0.5;
    float h = hash12(cell + seed);
    if (h > 0.42 * density) return vec3(0.0);
    float rad = min(mix(0.2, 0.42, hash12(cell + seed + 3.1)), 0.45);
    vec2 o = (hash22(cell + seed * 1.3) - 0.5) * (1.0 - 2.0 * rad);
    float d = length(f - o);
    float disk = smoothstep(rad, rad * (1.0 - SOFT), d);
    float rim = smoothstep(rad * 0.55, rad * 0.95, d) * disk;
    float tw = 0.55 + 0.45 * sin(t * (0.8 + 1.8 * h) + h * 40.0);
    return palette(hash12(cell + seed + 7.7)) * (disk * FILLK + rim * RIM) * tw * bright;
}
void main() {
    vec4 src = S(v_texCoord);
    vec2 uv = v_texCoord;
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec3 base = src.rgb;
    if (DEFOCUS > 0.0) base = mix(base, discBlur(uv, DEFOCUS).rgb * 0.85, 0.9);
    float k = 4.0 * SCALE / size;
    vec3 L = layer(p, t, k * 1.9, 11.0, 0.45) + layer(p, t * 1.2, k * 1.2, 23.0, 0.7)
           + layer(p, t * 1.45, k * 0.75, 37.0, 1.0);
    float m = 1.0;
    if (FRAME > 0.0) {
        float e = max(abs(uv.y - 0.5) * 2.0, abs(uv.x - 0.5) * 2.0 * 0.92);
        m = mix(1.0, smoothstep(0.5, 0.95, e), FRAME);
    }
    if (TOPGLOW > 0.0) {
        m *= mix(1.0, smoothstep(0.85, 0.05, uv.y), 0.85);
        float g = exp(-uv.y * 3.5) * (0.55 + 0.7 * fbm(vec2(p.x * 3.0 - t * 0.2, t * 0.15)));
        L += color * g * TOPGLOW * (0.85 + 0.15 * sin(t * 1.5));
    }
    vec3 col = addLight(base, L * m * GAIN, intensity);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("bokeh-de-colores", "Bokeh de colores", "Colourful bokeh", photo="citynight",
                defines={"PAL": 1.0, "DEFOCUS": 0.01}, tags=["colores", "colours", "arcoiris"], thumb=1.0),
        Variant("desenfoque-de-bokeh-5", "Desenfoque de bokeh 5", "Bokeh blur 5", photo="citynight",
                defines={"PAL": 4.0, "DEFOCUS": 0.035, "SCALE": 0.7, "SOFT": 0.45, "GAIN": 1.1},
                tags=["desenfoque", "blur", "fondo", "background"], thumb=1.2),
        Variant("bokeh-urbano", "Bokeh urbano", "Urban bokeh", photo="citynight",
                params={"density": 0.6},
                defines={"PAL": 4.0, "DEFOCUS": 0.012, "SCALE": 0.85, "SOFT": 0.35, "RIM": 0.7, "FILLK": 0.4,
                         "DRIFT": (0.08, 0.0)},
                tags=["ciudad", "city", "noche", "night"], thumb=1.4),
        Variant("burbujas-de-luz", "Burbujas de luz", "Light bubbles", photo="dark",
                params={"density": 0.9},
                defines={"PAL": 3.0, "RIM": 0.55, "FILLK": 0.18, "SOFT": 0.12, "DRIFT": (0.0, -0.06),
                         "GAIN": 0.8},
                tags=["burbujas", "bubbles", "vlog"], thumb=1.4),
        Variant("bokeh-5", "Bokeh 5", "Bokeh 5", photo="fx-woman-08", params={"density": 1.5},
                defines={"PAL": 2.0, "FRAME": 1.0, "SCALE": 0.9, "GAIN": 1.2},
                tags=["dorado", "golden", "marco", "frame"], thumb=1.0),
        Variant("lluvia-de-luz", "Lluvia de luz", "Light rain", photo="dark", params={"size": 0.6},
                defines={"PAL": 2.0, "FALL": 1.0, "TOPGLOW": 0.9, "SOFT": 0.5, "RIM": 0.2, "GAIN": 1.3,
                         "DRIFT": (0.0, 0.0)},
                tags=["lluvia", "rain", "dorado", "golden", "streaming"], thumb=1.2),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Glows and flashes on the picture itself. MODE 0 aura bloom, 1 golden plasma frame, 2 star-light burst from the
# edges, 3 exposure flash, 4 vibrating flash, 5 grainy beam.
GLOW = Family(
    key="luz_glow", category="luz", params=[INTENSITY, SPEED, colour("#7ab4ff")], photo="woman",
    tags=["brillo", "glow", "resplandor", "luz", "light"],
    defines={"MODE": 0.0},
    body=r"""
float inner(vec2 p) { return -sdBox(p, vec2(aspect() * 0.5, 0.5)); }   // distance in from the frame edge
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec3 col = src.rgb;
    if (MODE < 0.5) {
        // Aura bloom: the bright parts bleed a coloured glow that breathes.
        float br = 0.7 + 0.3 * sin(t * 1.6);
        vec3 g = brightGlow(uv, 0.08, 0.6);
        vec3 soft = discBlur(uv, 0.02).rgb;
        col = mix(col, max(col, soft), 0.45 * sat(intensity));
        col = addLight(col, (g * 1.3 * mix(vec3(1.0), color, 0.5) + color * 0.12 * luma(soft)) * br, intensity);
    } else if (MODE < 1.5) {
        // Golden plasma crawling on the frame.
        float d = inner(p);
        float n = fbm(p * 5.0 + vec2(t * 1.3, -t * 0.9));
        float n2 = fbm(p * 11.0 - vec2(t * 2.1, t * 1.7));
        float flame = exp(-max(d - n * 0.07, 0.0) / (0.018 + 0.02 * n2));
        float arcs = pow(1.0 - abs(vnoise(p * 16.0 + vec2(t * 3.0, -t * 2.0)) * 2.0 - 1.0), 10.0)
                   * exp(-d / 0.05);
        float fl = 0.85 + 0.15 * vnoise(vec2(t * 12.0, 3.0));
        vec3 L = color * (flame * 1.1 + arcs * 0.9) * vec3(1.0, 0.85, 0.6) + vec3(1.0, 0.95, 0.75) * smoothstep(0.8, 1.0, flame) * 0.3;
        col = mix(col, color * (0.8 + 0.4 * n2), sat(flame * 0.75 * intensity));
        col = addLight(col, L * fl, intensity);
    } else if (MODE < 2.5) {
        // Star-light burst: a pulsing glow from the edges and sparkles inside it.
        float d = inner(p);
        float pulse = 0.75 + 0.25 * sin(t * 2.2);
        float n = fbm(p * 3.0 + vec2(t * 0.4, t * 0.3));
        float g = exp(-d / (0.08 + 0.05 * pulse)) * (0.6 + 0.8 * n);
        vec2 q = p * 22.0 + vec2(0.0, -t * 0.6);
        vec2 c = floor(q), f = fract(q) - 0.5;
        vec2 o = (hash22(c) - 0.5) * 0.6;
        float tw = 0.5 + 0.5 * sin(t * 5.0 + hash12(c) * 40.0);
        float sp = smoothstep(0.12, 0.0, length(f - o)) * step(0.45, hash12(c + 2.0)) * tw;
        sp *= smoothstep(0.32, 0.0, d) + 0.25;
        vec3 L = color * g * 1.3 + vec3(1.0, 0.95, 0.7) * sp * 1.4 + vec3(1.0, 0.98, 0.85) * smoothstep(0.5, 1.2, g);
        col = addLight(col, L, intensity);
    } else if (MODE < 3.5) {
        // Exposure flash: a hit every second that burns the picture to white and settles.
        float b = beat(t, 1.0, 0.28);
        vec3 g = brightGlow(uv, 0.05, 0.35);
        float e = 1.0 + (0.35 + 2.6 * b) * intensity;
        col = 1.0 - exp(-col * e * 1.1);
        col = addLight(col, (g + color * 0.15) * (0.4 + b), intensity);
        col = mix(col, vec3(1.0), 0.35 * b * sat(intensity));
    } else if (MODE < 4.5) {
        // Vibrating flash: the frame shakes on the beat, a ghost copy and a white bloom.
        float b = beat(t, 0.5, 0.15);
        vec2 sh = shake2(t, 18.0) * 0.02 * b * intensity;
        vec2 cu = camUv(uv, vec2(0.5), 1.06 + 0.04 * b, 0.0, sh);
        vec3 a = Sm(cu).rgb;
        vec3 gh = Sm(camUv(uv, vec2(0.5), 1.12 + 0.06 * b, 0.0, -sh * 1.5)).rgb;
        col = mix(a, screen(a, gh), 0.45 * b);
        col = 1.0 - exp(-col * (1.2 + 1.6 * b * intensity));
        col = mix(col, vec3(1.0), 0.25 * b * sat(intensity));
    } else {
        // Grainy beam: coloured grain, a bright halo round the middle and dark edges, flickering.
        float ft = stepTime(t, 24.0);
        vec3 gr = hash32(uv * u_resolution + ft * 91.0) - 0.5;
        float r = length(p - vec2(0.05 * sin(t * 0.8), 0.0));
        float halo = exp(-r * r / 0.14) * (0.85 + 0.15 * vnoise(vec2(t * 10.0, 1.0)));
        float sweep = exp(-pow((p.x + p.y * 0.4 - (fract(t * 0.25) * 2.4 - 1.2)) / 0.18, 2.0));
        col = addLight(col, color * (halo * 0.55 + sweep * 0.35), intensity);
        col += (gr + 0.15 * (gr.x + gr.y + gr.z)) * (0.26 + 0.2 * halo) * intensity;
        col *= mix(1.0, vignette(uv, 0.45, 0.55), 0.6 * sat(intensity));
    }
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[
        Variant("floracion-de-aura", "Floración de aura", "Aura bloom", photo="fx-woman-05",
                defines={"MODE": 0.0}, tags=["aura", "bloom", "suave", "soft"], thumb=1.0),
        Variant("amarillo-plasma", "Amarillo plasma", "Plasma yellow", photo="fx-woman-05", params={"color": "#ffb820"},
                defines={"MODE": 1.0}, tags=["plasma", "amarillo", "yellow", "marco", "frame", "electrico"],
                thumb=1.2),
        Variant("explosion-de-luz-estelar", "Explosión de luz estelar", "Star-light burst", photo="dark",
                params={"color": "#ffd640"}, defines={"MODE": 2.0},
                tags=["estrellas", "stars", "brillos", "sparkle", "amarillo"], thumb=1.0),
        Variant("exposicion-de-destello", "Exposición de destello", "Flash exposure", photo="fx-skater-01",
                params={"color": "#ffffff"}, defines={"MODE": 3.0},
                tags=["flash", "exposicion", "exposure", "blanco", "white"], thumb=0.1),
        Variant("destello-de-vibracion", "Destello de vibración", "Vibration flash", photo="fx-skater-01",
                params={"color": "#ffffff"}, defines={"MODE": 4.0},
                tags=["flash", "vibracion", "shake", "ritmo", "beat"], thumb=0.05),
        Variant("haz-granulado", "Haz granulado", "Grainy beam", photo="fx-skater-04", params={"color": "#cfe4ff"},
                defines={"MODE": 5.0}, tags=["grano", "grain", "ruido", "noise", "haz", "beam"], thumb=1.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Disco: mirror-ball spots turning across the picture, LED columns and a pink wash with soft scanlines.
DISCO = Family(
    key="luz_disco", category="luz", params=[INTENSITY, SPEED, colour("#ff5fa8")], photo="woman",
    tags=["discoteca", "disco", "fiesta", "party", "luces", "lights"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec3 col = mix(src.rgb, src.rgb * mix(vec3(1.0), color * 1.4, 0.5), 0.45 * sat(intensity));
    // Mirror-ball spots.
    vec2 q = rot(t * 0.35) * (p - vec2(0.0, -0.6)) * 5.0;
    q.x += t * 0.4;
    vec2 c = floor(q), f = fract(q) - 0.5;
    vec2 o = (hash22(c) - 0.5) * 0.5;
    float on = step(0.45, hash12(c + floor(t * 2.0) * 0.37));
    float spot = smoothstep(0.24, 0.06, length(f - o)) * on;
    vec3 sc = hsv2rgb(vec3(fract(hash12(c + 5.0) * 0.35 + 0.8), 0.6, 1.0));
    // LED columns that change a few times a second.
    float colx = floor(uv.x * 18.0);
    float led = hash12(vec2(colx, floor(t * 6.0))) ;
    float ledMask = smoothstep(0.65, 0.95, led) * (0.6 + 0.4 * smoothstep(0.0, 0.3, fract(uv.y * 9.0 + colx)));
    // A pink wash that sweeps across.
    float sweep = 0.5 + 0.5 * sin(p.x * 3.0 - t * 1.8);
    float scan = 0.92 + 0.08 * sin(uv.y * u_resolution.y * 1.2);
    vec3 L = sc * spot * 0.9 + color * ledMask * 0.35 + color * sweep * 0.22;
    col = addLight(col, L, intensity) * mix(1.0, scan, sat(intensity));
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[
        Variant("luz-de-discoteca", "Luz de discoteca", "Disco light", photo="fx-woman-04",
                tags=["rosa", "pink"], thumb=1.0),
    ],
)

FAMILIES = [LEAK, FLARE, RAYS, BOKEH, GLOW, DISCO]
