"""Efectos › Tendencias, Luz y destellos (first half of the catalog section, up to «Fuga de luz 1»).

Light leaks, lens flares (ghosts, streaks, halo), sun rays and spotlights, bokeh, glows and flashes, disco
lights. Every light is added with a screen blend so whites never clip hard, and moves on u_time.
Everything a person would want to move is a parameter: where the light comes from (Center X/Y), where it
points (Angle, in degrees), how big it is (Size), how many (Density), how wide (Spread).
"""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)


def colour(default: str) -> Param:
    return Param("color", "Colour", default=default)


def center(x: float, y: float) -> list:
    """Where the light comes from, in frame units (a little past the edges is allowed: a sun off frame)."""
    return [Param("centerX", "Center X", -0.2, 1.2, x), Param("centerY", "Center Y", -0.2, 1.2, y)]


def angle(default: float = 0.0, lo: float = -180.0, hi: float = 180.0) -> Param:
    return Param("angle", "Angle", lo, hi, default)


SIZE = Param("size", "Size", 0.3, 2.0, 1.0)


# ---------------------------------------------------------------------------------------------------------------
# Light leaks: three coloured blobs that drift near the edges, warped by noise, with optional streaks. BURN turns
# the same field into a film burn (a hot colour ramp that eats into the picture). Angle turns the whole leak
# (where it comes in from and the direction of its streaks) about the centre.
LEAK = Family(
    key="luz_leak", category="luz", params=[INTENSITY, SPEED, colour("#ff6a1a"), angle(), SIZE],
    photo="woman",
    tags=["fuga de luz", "light leak", "luz", "light", "pelicula", "film", "calido", "warm"],
    defines={"COL_B": "#e01a0c", "COL_C": "#ffc040", "P1": (0.0, 0.3), "P2": (1.0, 0.7), "P3": (0.05, 0.95),
             "R1": 0.35, "R2": 0.35, "R3": 0.25, "WARP": 0.5, "STREAK": 0.0, "STREAK_ANG": 0.6, "BURN": 0.0,
             "GAIN": 1.0, "WASH": 0.0},
    body=r"""
mat2 turn() { return rot(radians(angle)); }
vec2 at(vec2 uv) { return turn() * ((uv - 0.5) * vec2(aspect(), 1.0)); }
vec3 field(vec2 p, float t) {
    vec2 w = vec2(fbm(p * 1.4 + vec2(t * 0.11, -t * 0.07)), fbm(p * 1.4 + vec2(-t * 0.09, t * 0.13) + 5.2)) - 0.5;
    vec2 q = p + w * WARP;
    vec2 c1 = at(P1) + 0.13 * vec2(sin(t * 0.70), cos(t * 0.53));
    vec2 c2 = at(P2) + 0.13 * vec2(cos(t * 0.61 + 1.0), sin(t * 0.47 + 2.0));
    vec2 c3 = at(P3) + 0.10 * vec2(sin(t * 0.43 + 4.0), cos(t * 0.71 + 3.0));
    float r1 = R1 * size, r2 = R2 * size, r3 = R3 * size;
    vec3 acc = color * exp(-dot(q - c1, q - c1) / (r1 * r1));
    acc += COL_B * exp(-dot(q - c2, q - c2) / (r2 * r2));
    acc += COL_C * exp(-dot(q - c3, q - c3) / (r3 * r3));
    return acc;
}
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    vec3 L = field(p, t);
    if (STREAK > 0.0) {
        float sa = STREAK_ANG - radians(angle);
        vec2 dir = vec2(cos(sa), sin(sa));
        vec2 per = vec2(-dir.y, dir.x);
        float s = fbm(vec2(dot(p, per) * 7.0 / size - t * 0.35, dot(p, dir) * 0.8 + t * 0.05));
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
# Center X/Y = the source, Size = everything's scale, Angle turns the streak and the beam.
FLARE = Family(
    key="luz_flare", category="luz",
    params=[INTENSITY, SPEED, colour("#ffd9a0"), *center(0.3, 0.15), SIZE, angle()],
    photo="dark", tags=["destello", "flare", "lente", "lens", "sol", "sun"],
    defines={"DRIFT": 0.06, "CORE": 0.05, "RAYS": 0.6, "RAYS_FALL": 4.0, "HALO_R": 0.0,
             "HALO": 0.0, "STREAK": 0.0, "STREAK_COL": "#7ab8ff", "STREAK_L": 0.5, "STREAK_W": 0.012,
             "GHOSTS": 0.6, "GHOST_R": 0.06, "GHOST_COL": "#9fd0ff", "BEAM": 0.0, "BEAM_COL": "#5a8cff",
             "BEAM_W": 0.06, "BEAM_L": 0.9, "BEAM_ANG": 99.0, "HAZE": 0.0, "EDGE": 0.0, "EDGE_COL": "#8a3cff"},
    body=r"""
float ringAt(float r, float R, float w) { float x = (r - R) / w; return exp(-x * x); }
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    float k = size;
    vec2 s = (vec2(centerX, centerY) + DRIFT * vec2(sin(t * 0.55), 0.6 * cos(t * 0.42)) - 0.5) * vec2(aspect(), 1.0);
    vec2 d = p - s;
    float r = length(d);
    float a = atan(d.y, d.x);
    float flick = 0.93 + 0.07 * vnoise(vec2(t * 6.0, 1.3));
    float core = CORE * k;
    vec3 L = vec3(0.0);
    // Core and glow.
    L += color * (exp(-r * r / (core * core)) * 1.3 + 0.45 * exp(-r / (core * 3.0)));
    L += vec3(1.0) * exp(-r * r / (core * core * 0.12));
    // Starburst (integer frequencies: no seam at the back of the angle).
    float st = pow(abs(cos(a * 7.0 + t * 0.15)), 40.0) + 0.7 * pow(abs(cos(a * 11.0 - t * 0.11 + 1.0)), 60.0)
             + 0.4 * pow(abs(cos(a * 17.0 + t * 0.07 + 2.0)), 80.0);
    L += mix(color, vec3(1.0), 0.4) * st * exp(-r * RAYS_FALL / k) * RAYS;
    // Chromatic halo ring.
    if (HALO > 0.0) {
        float R = HALO_R * k, w = R * 0.07;
        vec3 ring = vec3(ringAt(r, R * 1.04, w), ringAt(r, R, w), ringAt(r, R * 0.96, w));
        L += ring * HALO * (0.75 + 0.25 * sin(a * 3.0 + t));
    }
    // Anamorphic streak, turned by Angle.
    vec2 dr = rot(-radians(angle)) * d;
    if (STREAK > 0.0) {
        float sl = STREAK_L * k;
        float sx = exp(-abs(dr.y) / STREAK_W) * exp(-abs(dr.x) / sl);
        sx += 0.35 * exp(-abs(dr.y) / (STREAK_W * 5.0)) * exp(-abs(dr.x) / (sl * 0.6));
        L += STREAK_COL * sx * STREAK * (0.85 + 0.15 * sin(t * 2.0));
    }
    // Ghosts on the line through the source and the centre of the frame.
    if (GHOSTS > 0.0) {
        for (int i = 0; i < 6; ++i) {
            float fi = float(i);
            float gk = 0.55 - fi * 0.38 + 0.08 * sin(fi * 3.1);
            vec2 g = s * gk;
            float gr = GHOST_R * k * (0.45 + 1.1 * hash11(fi * 7.3 + 1.0));
            float gd = length(p - g);
            float disk = smoothstep(gr, gr * 0.75, gd);
            float rim = exp(-pow((gd - gr * 0.92) / (gr * 0.12), 2.0));
            vec3 gc = mix(GHOST_COL, hsv2rgb(vec3(hash11(fi * 3.7 + 2.0), 0.55, 1.0)), 0.5);
            L += gc * (disk * 0.22 + rim * 0.25) * GHOSTS;
        }
    }
    // Beam from the source (towards the centre when BEAM_ANG is unset), turned by Angle.
    if (BEAM > 0.0) {
        vec2 bd = BEAM_ANG > 50.0 ? normalize(-s + 1e-4) : vec2(cos(BEAM_ANG), sin(BEAM_ANG));
        bd = rot(radians(angle)) * bd;
        float along = dot(d, bd);
        float perp = abs(dot(d, vec2(-bd.y, bd.x)));
        float wid = BEAM_W * k * (0.4 + abs(along) * 1.2);
        float b = exp(-perp * perp / (wid * wid)) * exp(-max(along, 0.0) / (BEAM_L * k)) * smoothstep(-0.05, 0.05, along);
        b *= 0.75 + 0.25 * sin(along * 9.0 - t * 2.0);
        L += BEAM_COL * b * BEAM;
    }
    if (HAZE > 0.0) L += mix(color, vec3(0.85, 0.9, 1.0), 0.5) * exp(-r * 1.6 / k) * HAZE;
    if (EDGE > 0.0) {
        float ex = v_texCoord.x;
        float e = exp(-ex / (0.07 * k)) * (0.55 + 0.6 * fbm(vec2(v_texCoord.y * 5.0, t * 0.6)));
        e += 0.5 * exp(-ex / (0.22 * k)) * (0.5 + 0.5 * sin(v_texCoord.y * 6.0 + t * 1.5));
        L += EDGE_COL * e * EDGE * (0.8 + 0.2 * sin(t * 3.0));
    }
    vec3 col = addLight(src.rgb, L * flick, intensity);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("luz-del-sol-05", "Luz del sol 05", "Sunlight 05", photo="dark",
                params={"centerX": 0.32, "centerY": 0.18},
                defines={"GHOSTS": 1.0, "GHOST_R": 0.07, "RAYS": 0.5, "HAZE": 0.25, "HALO": 0.25, "HALO_R": 0.16},
                tags=["luz del sol", "sunlight"], thumb=1.0),
        Variant("explosion-prismatica", "Explosión prismática", "Prismatic burst", photo="dark",
                params={"color": "#d8e4ff", "centerX": 0.48, "centerY": 0.4},
                defines={"DRIFT": 0.04, "CORE": 0.035, "STREAK": 1.2, "STREAK_L": 0.7,
                         "STREAK_COL": "#6a9cff", "GHOSTS": 0.5, "GHOST_COL": "#b07aff", "EDGE": 1.1,
                         "RAYS": 0.4, "HALO": 0.35, "HALO_R": 0.09},
                tags=["prisma", "prism", "morado", "purple", "anamorfico", "anamorphic"], thumb=1.2),
        Variant("destello-de-la-lente-5", "Destello de la lente 5", "Lens flare 5", photo="fx-beach-03",
                params={"color": "#fff1dc", "centerX": 0.1, "centerY": 0.12},
                defines={"DRIFT": 0.08, "CORE": 0.1, "RAYS": 0.08, "RAYS_FALL": 3.0,
                         "HAZE": 0.8, "HALO": 0.45, "HALO_R": 0.42, "GHOSTS": 0.5, "GHOST_R": 0.11},
                tags=["suave", "soft", "brumoso", "hazy"], thumb=1.5),
        Variant("destello-de-la-lente-3", "Destello de la lente 3", "Lens flare 3", photo="dark",
                params={"color": "#ffc6d6", "centerX": 0.88, "centerY": 0.95},
                defines={"DRIFT": 0.05, "CORE": 0.07, "RAYS": 0.3, "BEAM": 1.0,
                         "BEAM_COL": "#ff8fb4", "BEAM_W": 0.08, "BEAM_L": 1.2, "BEAM_ANG": -2.3,
                         "GHOSTS": 0.35, "HAZE": 0.2},
                tags=["rosa", "pink", "diagonal"], thumb=1.4),
        Variant("destello-de-lente-azul", "Destello de lente azul", "Blue lens flare", photo="dark",
                params={"color": "#e4efff", "centerX": 0.1, "centerY": 0.1},
                defines={"CORE": 0.06, "RAYS": 0.7, "BEAM": 0.9, "BEAM_COL": "#4a7cff",
                         "BEAM_W": 0.05, "BEAM_L": 1.1, "GHOSTS": 0.8, "GHOST_COL": "#7a8cff", "HAZE": 0.2},
                tags=["azul", "blue"], thumb=1.0),
        Variant("sol-en-la-esquina", "Sol en la esquina", "Sun in the corner", photo="dark",
                params={"centerX": 0.04, "centerY": 0.04},
                defines={"DRIFT": 0.03, "CORE": 0.09, "RAYS": 1.0, "RAYS_FALL": 2.5,
                         "HALO": 0.5, "HALO_R": 0.3, "GHOSTS": 0.6, "GHOST_R": 0.08, "HAZE": 0.35},
                tags=["esquina", "corner", "rayos", "rays"], thumb=1.2),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Rays from a point: god rays, beams, spotlights (with the rest darkened) and a pool on the floor.
# Center X/Y = where they come from, Angle = where they point (degrees, 90 = down), Spread = how wide the cone,
# Density = how many separate rays.
RAYS_HELPERS = r"""
float rayPattern(float a, float t, float sharp, float dens) {
    float n = 0.5 * sin(a * floor(13.0 * dens) + t * 0.6 + 1.5 * sin(a * 5.0 - t * 0.25))
            + 0.3 * sin(a * floor(29.0 * dens) - t * 0.9 + 2.0) + 0.2 * sin(a * floor(47.0 * dens) + t * 1.3 + 4.0);
    return pow(sat(0.5 + 0.5 * n), sharp);
}
float angDiff(float a, float b) { return atan(sin(a - b), cos(a - b)); }
float dust(vec2 p, float t) {
    vec2 q = p * 9.0 + vec2(t * 0.15, -t * 0.25);
    vec2 c = floor(q), f = fract(q) - 0.5;
    vec2 o = (hash22(c) - 0.5) * 0.7;
    float tw = 0.5 + 0.5 * sin(t * 2.0 + hash12(c) * 30.0);
    return smoothstep(0.08, 0.0, length(f - o)) * step(0.6, hash12(c + 4.1)) * tw;
}
"""

RAYS = Family(
    key="luz_rays", category="luz",
    params=[INTENSITY, SPEED, colour("#ffc35a"), *center(0.5, -0.1), angle(90.0),
            Param("spread", "Spread", 0.3, 2.5, 1.0), Param("density", "Density", 0.4, 2.0, 1.0)],
    photo="woman", tags=["rayos", "rays", "haz", "beam", "luz", "light"],
    defines={"CONE": 1.0, "SWAY": 0.08, "FALL": 1.2, "FILL": 0.4, "RAYAMT": 0.9, "SHARP": 3.0, "DARK": 0.0,
             "POOL": 0.0, "POOL_Y": 0.85, "DUST": 0.3},
    body=RAYS_HELPERS + r"""
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    vec3 base = src.rgb;
    vec2 o = (vec2(centerX, centerY) - 0.5) * vec2(aspect(), 1.0);
    vec2 d = p - o;
    float r = length(d);
    float a = atan(d.y, d.x);
    float dir = radians(angle) + SWAY * sin(t * 0.7);
    float cw = min(CONE * spread, 3.1);
    float cone = smoothstep(cw, cw * 0.35, abs(angDiff(a, dir)));
    float fall = exp(-r * FALL);
    float rays = rayPattern(a, t, SHARP, density);
    vec3 L = color * cone * (FILL + RAYAMT * rays) * fall;
    L += vec3(1.0) * dust(p, t) * cone * fall * DUST;
    if (DARK > 0.0) base *= mix(1.0 - DARK * sat(intensity), 1.0, sat(cone * (0.35 + exp(-r * 0.8))));
    if (POOL > 0.0) {
        // The pool lands where the cone meets the floor line below the source.
        vec2 dd = vec2(cos(dir), sin(dir));
        float reach = (POOL_Y - 0.5 - o.y) / max(dd.y, 0.2);
        vec2 pc = o + dd * reach;
        vec2 e = (p - pc) * vec2(1.0, 4.0) / spread;
        float el = length(e);
        L += color * POOL * (0.8 * exp(-el * el / 0.03) + 0.9 * exp(-pow((el - 0.2) / 0.02, 2.0)));
    }
    vec3 col = addLight(base, L, intensity);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("rayo-dorado", "Rayo dorado", "Golden rays", photo="dark",
                defines={"CONE": 1.1, "FALL": 1.4, "FILL": 0.35}, tags=["dorado", "golden", "dios", "god rays"],
                thumb=1.2),
        Variant("rayo-de-luz", "Rayo de luz", "Light beam", photo="dark",
                params={"color": "#ffe2b0", "centerX": 0.98, "centerY": -0.05, "angle": 140.0},
                defines={"CONE": 0.32, "SWAY": 0.05, "FALL": 1.0, "FILL": 0.5, "RAYAMT": 0.7},
                tags=["diagonal", "haz", "beam"], thumb=1.4),
        Variant("luz-del-sol-03", "Luz del sol 03", "Sunlight 03", photo="dark",
                params={"centerY": -0.05},
                defines={"CONE": 0.42, "SWAY": 0.06, "FALL": 1.0, "FILL": 0.5, "POOL": 0.6, "POOL_Y": 0.8},
                tags=["foco", "spotlight", "escenario", "stage"], thumb=1.0),
        Variant("foco-final", "Foco final", "Spotlight finish", photo="lighthouse",
                params={"color": "#ffffff", "centerY": -0.12},
                defines={"CONE": 0.3, "SWAY": 0.05, "FALL": 0.6, "FILL": 0.55, "RAYAMT": 0.3, "DARK": 0.8,
                         "DUST": 0.15},
                tags=["foco", "spotlight", "final", "ending"], thumb=1.2),
    ],
)

# Rainbow neon rays round the subject. With the clip's depth map (AI) the nearest thing, the person, covers the
# rays so they come from behind; without it the rays fade near the centre so the face stays clean.
NEON_RAYS = Family(
    key="luz_neon_rays", category="luz", requires="depth",
    params=[INTENSITY, SPEED, *center(0.5, 0.42), SIZE, Param("density", "Density", 0.4, 2.0, 1.0),
            Param("saturation", "Saturation", 0.0, 1.0, 0.75)],
    photo="fashion", tags=["rayos", "rays", "neon", "arcoiris", "rainbow", "detras", "behind"],
    defines={"SHARP": 6.0},
    body=RAYS_HELPERS + r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec2 o = (vec2(centerX, centerY) - 0.5) * vec2(aspect(), 1.0);
    vec2 d = p - o;
    float r = length(d);
    float a = atan(d.y, d.x);
    float rays = rayPattern(a + t * 0.05, t, SHARP, density);
    vec3 c = hsv2rgb(vec3(fract(a / TAU + t * 0.08), saturation, 1.0));
    float k = (0.05 + 1.3 * rays) * exp(-r * 0.9 / size);
    float front = 0.0;
    if (u_hasDepth > 0.5) {
        // Near = the person: depth well above the background's. Rays go behind it, with a thin back-light rim.
        float z = driftDepth(uv);
        front = smoothstep(0.45, 0.62, z);
        float zr = driftDepth(uv + normalize(d + 1e-4) * 0.012 * vec2(1.0 / aspect(), 1.0));
        float rim = sat(front - smoothstep(0.45, 0.62, zr)) * 2.0;
        k = k * (1.0 - front) + rim * 0.6 * (0.6 + rays);
    } else {
        k *= smoothstep(0.08, 0.42, r) * 0.85 + 0.15;
    }
    vec3 col = addLight(src.rgb, c * k, intensity);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("fiebre-del-neon", "Fiebre del neón", "Neon fever", tags=["fiesta", "party"], thumb=1.0,
                note={"es": "Con el análisis de profundidad (IA) los rayos salen detrás de la persona.",
                      "en": "With the depth analysis (AI) the rays come from behind the person."}),
    ],
)

# Stage: six coloured beams sweeping up from the floor. Spread = how wide each beam, Angle = how far they swing.
STAGE = Family(
    key="luz_stage", category="luz",
    params=[INTENSITY, SPEED, Param("color", "Colour A", default="#ff2fc0"), Param("colorB", "Colour B",
            default="#2a6dff"), Param("spread", "Spread", 0.3, 2.5, 1.0), angle(29.0, 0.0, 80.0),
            Param("density", "Density", 2.0, 8.0, 6.0)],
    photo="dark", tags=["escenario", "stage", "concierto", "concert", "fiesta", "party", "rayos", "beams"],
    body=r"""
float angDiff(float a, float b) { return atan(sin(a - b), cos(a - b)); }
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    vec3 L = vec3(0.0);
    float n = floor(density + 0.5);
    for (int i = 0; i < 8; ++i) {
        float fi = float(i);
        if (fi >= n) break;
        vec2 o = (vec2((fi + 0.5) / n, 1.03) - 0.5) * vec2(aspect(), 1.0);
        float ang = -1.5708 + radians(angle) * sin(t * 0.9 + fi * 1.7) * (mod(fi, 2.0) < 0.5 ? 1.0 : -1.0);
        vec2 d = p - o;
        float r = length(d);
        float da = abs(angDiff(atan(d.y, d.x), ang));
        vec3 c = mod(fi, 2.0) < 0.5 ? color : colorB;
        float beam = smoothstep(0.14 * spread, 0.0, da) * exp(-r * 1.1)
                   + 1.6 * smoothstep(0.03 * spread, 0.0, da) * exp(-r * 2.2);
        L += c * (beam * 0.8 + 1.8 * exp(-r * r / 0.002));
    }
    vec3 col = addLight(src.rgb * mix(1.0, 0.85, sat(intensity)), L, intensity);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("luces-de-escenario", "Luces de escenario", "Stage lights", thumb=1.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Bokeh: soft discs with a brighter rim in three depth layers, drifting and twinkling. Palettes: the colour
# parameter, rainbow, warm gold, grey bubbles, city lights. Spread = how much of the frame they cover (from the
# edges in), Blur = how much the picture behind goes out of focus, Angle = where they drift.
BOKEH = Family(
    key="luz_bokeh", category="luz",
    params=[INTENSITY, SPEED, colour("#ffd27a"), Param("size", "Size", 0.5, 1.5, 1.0),
            Param("density", "Density", 0.2, 2.0, 1.0), Param("spread", "Spread", 0.1, 1.0, 1.0),
            Param("blur", "Blur", 0.0, 0.06, 0.0), angle(-30.0)],
    photo="citynight", tags=["bokeh", "luces", "lights", "desenfoque", "blur", "circulos", "circles"],
    defines={"PAL": 0.0, "RIM": 0.5, "SOFT": 0.25, "DRIFT": 0.058, "FALL": 0.0, "TOPGLOW": 0.0, "GAIN": 1.0,
             "SCALE": 1.0, "FILLK": 0.55},
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
    float da = radians(angle);
    q -= vec2(cos(da), sin(da)) * DRIFT * t * sc;
    q += vec2(sin(t * 0.35 + seed), cos(t * 0.27 + seed * 1.3)) * 0.25;
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
    if (blur > 0.0005) base = mix(base, discBlur(uv, blur).rgb * 0.85, 0.9);
    float k = 4.0 * SCALE / size;
    vec3 L = layer(p, t, k * 1.9, 11.0, 0.45) + layer(p, t * 1.2, k * 1.2, 23.0, 0.7)
           + layer(p, t * 1.45, k * 0.75, 37.0, 1.0);
    // 0 in the middle, 1 at the edges; Spread 1 covers everything, less keeps them to a frame.
    float e = max(abs(uv.y - 0.5) * 2.0, abs(uv.x - 0.5) * 2.0 * 0.92);
    float lo = 1.0 - spread * 1.45;
    float m = smoothstep(lo, lo + 0.45, e);
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
                params={"blur": 0.01}, defines={"PAL": 1.0}, tags=["colores", "colours", "arcoiris"], thumb=1.0),
        Variant("desenfoque-de-bokeh-5", "Desenfoque de bokeh 5", "Bokeh blur 5", photo="citynight",
                params={"blur": 0.035}, defines={"PAL": 4.0, "SCALE": 0.7, "SOFT": 0.45, "GAIN": 1.1},
                tags=["desenfoque", "blur", "fondo", "background"], thumb=1.2),
        Variant("bokeh-urbano", "Bokeh urbano", "Urban bokeh", photo="citynight",
                params={"density": 0.6, "blur": 0.012, "angle": 180.0},
                defines={"PAL": 4.0, "SCALE": 0.85, "SOFT": 0.35, "RIM": 0.7, "FILLK": 0.4, "DRIFT": 0.08},
                tags=["ciudad", "city", "noche", "night"], thumb=1.4),
        Variant("burbujas-de-luz", "Burbujas de luz", "Light bubbles", photo="dark",
                params={"density": 0.9, "angle": -90.0},
                defines={"PAL": 3.0, "RIM": 0.55, "FILLK": 0.18, "SOFT": 0.12, "DRIFT": 0.06, "GAIN": 0.8},
                tags=["burbujas", "bubbles", "vlog"], thumb=1.4),
        Variant("bokeh-5", "Bokeh 5", "Bokeh 5", photo="fx-woman-08", params={"density": 1.5, "spread": 0.35},
                defines={"PAL": 2.0, "SCALE": 0.9, "GAIN": 1.2},
                tags=["dorado", "golden", "marco", "frame"], thumb=1.0),
        Variant("lluvia-de-luz", "Lluvia de luz", "Light rain", photo="dark", params={"size": 0.6},
                defines={"PAL": 2.0, "FALL": 1.0, "TOPGLOW": 0.9, "SOFT": 0.5, "RIM": 0.2, "GAIN": 1.3,
                         "DRIFT": 0.0},
                tags=["lluvia", "rain", "dorado", "golden", "streaming"], thumb=1.2),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Glows and flashes on the picture itself, one family each so every slider does something.

# Aura bloom: the bright parts bleed a coloured glow that breathes. Size = glow radius, Brightness = what counts
# as bright (lower glows more of the picture).
AURA = Family(
    key="luz_aura", category="luz",
    params=[INTENSITY, SPEED, colour("#7ab4ff"), SIZE, Param("threshold", "Brightness", 0.2, 0.95, 0.6)],
    photo="fx-woman-05", tags=["brillo", "glow", "aura", "bloom", "suave", "soft"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float t = u_time * speed;
    vec3 col = src.rgb;
    float br = 0.7 + 0.3 * sin(t * 1.6);
    vec3 g = brightGlow(uv, 0.08 * size, threshold);
    vec3 soft = discBlur(uv, 0.02 * size).rgb;
    col = mix(col, max(col, soft), 0.45 * sat(intensity));
    col = addLight(col, (g * 1.3 * mix(vec3(1.0), color, 0.5) + color * 0.12 * luma(soft)) * br, intensity);
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[Variant("floracion-de-aura", "Floración de aura", "Aura bloom", thumb=1.0)],
)

# Golden plasma crawling on the frame. Width = how thick, Detail = how fine the flames.
PLASMA = Family(
    key="luz_plasma", category="luz",
    params=[INTENSITY, SPEED, colour("#ffb820"), Param("width", "Width", 0.3, 3.0, 1.0),
            Param("detail", "Detail", 0.5, 2.0, 1.0)],
    photo="fx-woman-05", tags=["plasma", "amarillo", "yellow", "marco", "frame", "electrico", "electric"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec3 col = src.rgb;
    float d = -sdBox(p, vec2(aspect() * 0.5, 0.5));
    float n = fbm(p * 5.0 * detail + vec2(t * 1.3, -t * 0.9));
    float n2 = fbm(p * 11.0 * detail - vec2(t * 2.1, t * 1.7));
    float flame = exp(-max(d - n * 0.07 * width, 0.0) / ((0.018 + 0.02 * n2) * width));
    float arcs = pow(1.0 - abs(vnoise(p * 16.0 * detail + vec2(t * 3.0, -t * 2.0)) * 2.0 - 1.0), 10.0)
               * exp(-d / (0.05 * width));
    float fl = 0.85 + 0.15 * vnoise(vec2(t * 12.0, 3.0));
    vec3 L = color * (flame * 1.1 + arcs * 0.9) * vec3(1.0, 0.85, 0.6)
           + vec3(1.0, 0.95, 0.75) * smoothstep(0.8, 1.0, flame) * 0.3;
    col = mix(col, color * (0.8 + 0.4 * n2), sat(flame * 0.75 * intensity));
    col = addLight(col, L * fl, intensity);
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[Variant("amarillo-plasma", "Amarillo plasma", "Plasma yellow", thumb=1.2)],
)

# Star-light burst: a pulsing glow from the edges and sparkles inside it. Width = how far in, Density = sparkles.
STARBURST = Family(
    key="luz_starburst", category="luz",
    params=[INTENSITY, SPEED, colour("#ffd640"), Param("width", "Width", 0.3, 3.0, 1.0),
            Param("density", "Density", 0.2, 2.0, 1.0)],
    photo="dark", tags=["estrellas", "stars", "brillos", "sparkle", "amarillo", "yellow"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    float d = -sdBox(p, vec2(aspect() * 0.5, 0.5));
    float pulse = 0.75 + 0.25 * sin(t * 2.2);
    float n = fbm(p * 3.0 + vec2(t * 0.4, t * 0.3));
    float g = exp(-d / ((0.08 + 0.05 * pulse) * width)) * (0.6 + 0.8 * n);
    vec2 q = p * 22.0 + vec2(0.0, -t * 0.6);
    vec2 c = floor(q), f = fract(q) - 0.5;
    vec2 o = (hash22(c) - 0.5) * 0.6;
    float tw = 0.5 + 0.5 * sin(t * 5.0 + hash12(c) * 40.0);
    float sp = smoothstep(0.12, 0.0, length(f - o)) * step(1.0 - 0.55 * density, hash12(c + 2.0)) * tw;
    sp *= smoothstep(0.32 * width, 0.0, d) + 0.25;
    vec3 L = color * g * 1.3 + vec3(1.0, 0.95, 0.7) * sp * 1.4 + vec3(1.0, 0.98, 0.85) * smoothstep(0.5, 1.2, g);
    fragColor = vec4(sat3(addLight(src.rgb, L, intensity)), src.a);
}
""",
    variants=[Variant("explosion-de-luz-estelar", "Explosión de luz estelar", "Star-light burst", thumb=1.0)],
)

# Exposure flash: a hit that burns the picture to white and settles. Frequency = flashes per second,
# Brightness = how much the picture is lifted between flashes.
FLASH = Family(
    key="luz_flash", category="luz",
    params=[INTENSITY, SPEED, colour("#ffffff"), Param("frequency", "Frequency", 0.25, 4.0, 1.0),
            Param("brightness", "Brightness", 0.0, 1.0, 0.35)],
    photo="fx-skater-01", tags=["flash", "exposicion", "exposure", "blanco", "white", "destello"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float t = u_time * speed;
    float b = beat(t, 1.0 / frequency, 0.28 / max(frequency, 1.0));
    vec3 g = brightGlow(uv, 0.05, 0.35);
    float e = 1.0 + (brightness + 2.6 * b) * intensity;
    vec3 col = 1.0 - exp(-src.rgb * e * 1.1);
    col = addLight(col, (g + color * 0.15) * (0.4 + b), intensity);
    col = mix(col, color, 0.35 * b * sat(intensity));
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[Variant("exposicion-de-destello", "Exposición de destello", "Flash exposure", thumb=0.1)],
)

# Vibrating flash: the frame shakes on the beat (120 BPM), a ghost copy and a white bloom. Strength = how hard
# it shakes, Frequency = hits per second.
VIBRATE = Family(
    key="luz_vibrate", category="luz",
    params=[INTENSITY, SPEED, colour("#ffffff"), Param("strength", "Strength", 0.0, 2.0, 1.0),
            Param("frequency", "Frequency", 0.5, 4.0, 2.0)],
    photo="fx-skater-01", tags=["flash", "vibracion", "shake", "ritmo", "beat", "destello"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float t = u_time * speed;
    float b = beat(t, 1.0 / frequency, 0.3 / frequency);
    vec2 sh = shake2(t, 18.0) * 0.02 * b * strength;
    vec3 a = Sm(camUv(uv, vec2(0.5), 1.06 + 0.04 * b * strength, 0.0, sh)).rgb;
    vec3 gh = Sm(camUv(uv, vec2(0.5), 1.12 + 0.06 * b * strength, 0.0, -sh * 1.5)).rgb;
    vec3 col = mix(a, screen(a, gh), 0.45 * b);
    col = 1.0 - exp(-col * (1.2 + 1.6 * b * intensity));
    col = mix(col, color, 0.25 * b * sat(intensity));
    fragColor = vec4(sat3(col), S(uv).a);
}
""",
    variants=[Variant("destello-de-vibracion", "Destello de vibración", "Vibration flash", thumb=0.05)],
)

# Grainy beam: coloured grain, a bright halo round the middle that a sweep of light crosses, dark edges.
# Grain = how much grain, Size = the halo, Center X/Y = where the halo sits.
GRAIN_BEAM = Family(
    key="luz_grain_beam", category="luz",
    params=[INTENSITY, SPEED, colour("#cfe4ff"), Param("grain", "Grain", 0.0, 2.0, 1.0), SIZE,
            *center(0.5, 0.5)],
    photo="fx-skater-04", tags=["grano", "grain", "ruido", "noise", "haz", "beam"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec3 col = src.rgb;
    float ft = stepTime(t, 24.0);
    vec3 gr = hash32(uv * u_resolution + ft * 91.0) - 0.5;
    vec2 c = (vec2(centerX, centerY) - 0.5) * vec2(aspect(), 1.0);
    float r = length(p - c - vec2(0.05 * sin(t * 0.8), 0.0));
    float halo = exp(-r * r / (0.14 * size * size)) * (0.85 + 0.15 * vnoise(vec2(t * 10.0, 1.0)));
    float sweep = exp(-pow((p.x + p.y * 0.4 - (fract(t * 0.25) * 2.4 - 1.2)) / 0.18, 2.0));
    col = addLight(col, color * (halo * 0.55 + sweep * 0.35), intensity);
    col += (gr + 0.15 * (gr.x + gr.y + gr.z)) * (0.26 + 0.2 * halo) * grain * sat(intensity);
    col *= mix(1.0, vignette(uv, 0.45 * size, 0.55), 0.6 * sat(intensity));
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[Variant("haz-granulado", "Haz granulado", "Grainy beam", thumb=1.0)],
)

# ---------------------------------------------------------------------------------------------------------------
# Disco: mirror-ball spots turning across the picture, LED columns and a wash with soft scanlines.
# Center X/Y = the mirror ball, Size = the spots, Density = how many are lit.
DISCO = Family(
    key="luz_disco", category="luz",
    params=[INTENSITY, SPEED, colour("#ff5fa8"), *center(0.5, -0.1), SIZE,
            Param("density", "Density", 0.2, 2.0, 1.0)],
    photo="fx-woman-04", tags=["discoteca", "disco", "fiesta", "party", "luces", "lights"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec3 col = mix(src.rgb, src.rgb * mix(vec3(1.0), color * 1.4, 0.5), 0.45 * sat(intensity));
    // Mirror-ball spots turning about the ball.
    vec2 ball = (vec2(centerX, centerY) - 0.5) * vec2(aspect(), 1.0);
    vec2 q = rot(t * 0.35) * (p - ball) * 5.0 / size;
    q.x += t * 0.4;
    vec2 c = floor(q), f = fract(q) - 0.5;
    vec2 o = (hash22(c) - 0.5) * 0.5;
    float on = step(1.0 - 0.55 * density, hash12(c + floor(t * 2.0) * 0.37));
    float spot = smoothstep(0.24, 0.06, length(f - o)) * on;
    vec3 sc = hsv2rgb(vec3(fract(hash12(c + 5.0) * 0.35 + 0.8), 0.6, 1.0));
    // LED columns that change a few times a second.
    float colx = floor(uv.x * 18.0);
    float led = hash12(vec2(colx, floor(t * 6.0)));
    float ledMask = smoothstep(0.65, 0.95, led) * (0.6 + 0.4 * smoothstep(0.0, 0.3, fract(uv.y * 9.0 + colx)));
    // A wash that sweeps across.
    float sweep = 0.5 + 0.5 * sin(p.x * 3.0 - t * 1.8);
    float scan = 0.92 + 0.08 * sin(uv.y * u_resolution.y * 1.2);
    vec3 L = sc * spot * 0.9 + color * ledMask * 0.35 + color * sweep * 0.22;
    col = addLight(col, L, intensity) * mix(1.0, scan, sat(intensity));
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[
        Variant("luz-de-discoteca", "Luz de discoteca", "Disco light", tags=["rosa", "pink"], thumb=1.0),
    ],
)

FAMILIES = [LEAK, FLARE, RAYS, NEON_RAYS, STAGE, BOKEH, AURA, PLASMA, STARBURST, FLASH, VIBRATE, GRAIN_BEAM, DISCO]
