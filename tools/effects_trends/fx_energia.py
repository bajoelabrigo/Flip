"""Efectos › Tendencias, «Energía y elementos»: rayos, fuego, brasas, ondas de choque, vórtices, fuegos
artificiales, humo, estelas, huellas y la carga en oscuro. Shaders propios (Flip Studio).

Defines are floats (kit.define_value), so modes are chosen with `if (MODE < 0.5)` and friends; the compiler folds
them away."""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)


def color(default: str) -> Param:
    return Param("color", "Colour", default=default)


SIZE = Param("size", "Size", 0.3, 2.0, 1.0)
DENSITY = Param("density", "Density", 0.2, 2.0, 1.0)
WIDTH = Param("width", "Width", 0.3, 3.0, 1.0)
CENTER = [Param("center_x", "Center X", 0.0, 1.0, 0.5), Param("center_y", "Center Y", 0.0, 1.0, 0.5)]

# Every body starts with @OCC@: for the plain families an occlude() that changes nothing, and for the «behind the
# person» ones (requires "depth": the engine puts its depth prelude, driftDepth and u_hasDepth, before the shader)
# an occlude() that puts the near part of the clip (the person) back in front of the effect. Without a depth map it
# changes nothing either: the effect covers everything, as in the plain family.
OCC_NONE = "vec3 occlude(vec3 col, vec3 front, vec2 uv) { return col; }\n"
OCC_DEPTH = r"""
vec3 occlude(vec3 col, vec3 front, vec2 uv) {
    if (u_hasDepth < 0.5) return col;
    return mix(col, front, smoothstep(0.55, 0.7, driftDepth(uv)));
}
"""


def _plain(family: Family) -> Family:
    family.body = family.body.replace("@OCC@", OCC_NONE)
    return family


def _behind(family: Family, key: str, ids: list) -> Family:
    """Moves the variants `ids` of `family` (still with @OCC@) to a new family drawn behind the person."""
    moved = [v for v in family.variants if v.id in ids]
    assert len(moved) == len(ids), ids
    family.variants = [v for v in family.variants if v.id not in ids]
    return Family(key=key, category=family.category, body=family.body.replace("@OCC@", OCC_DEPTH),
                  params=list(family.params), variants=moved, defines=dict(family.defines),
                  tags=family.tags + ["persona", "person", "detras", "behind"], photo=family.photo,
                  requires="depth", preview=family.preview)


# ---------------------------------------------------------------------------------------------------------------
# Lightning: jagged bolts (a 1D noise offset along a segment) with a branch, white core and coloured halo. Each bolt
# strikes, flickers and fades on its own clock, and is drawn somewhere new on the next strike.
#   MODE 0 scattered across the frame, 1 radiating around the subject, 2 one big bolt top to bottom,
#   3 radiating and twisted into a vortex.
LIGHTNING = Family(
    key="en_lightning", category="energia",
    params=[INTENSITY, SPEED, color("#5aa0ff"), SIZE, DENSITY, WIDTH] + CENTER,
    photo="dark", tags=["rayos", "lightning", "electricidad", "electric", "relampago", "tormenta", "storm", "energia",
                        "energy"],
    defines={"MODE": 0, "NB": 5, "LEN": 0.7, "AMP": 0.07, "RATE": 1.6, "DARKEN": 0.35, "FLASH": 0.25,
             "CGLOW": 0.0, "TINT": 0.0, "THICK": 1.0, "R0": 0.2},
    body=r"""@OCC@
float n1(float x, float s) { float i = floor(x), f = fract(x); f = f * f * (3.0 - 2.0 * f);
                             return mix(hash11(i + s * 13.7), hash11(i + 1.0 + s * 13.7), f) * 2.0 - 1.0; }
// Jagged offset along the bolt: big wander plus fine kinks.
float jag(float x, float s) {
    return 0.55 * n1(x * 4.0, s) + 0.28 * n1(x * 9.0, s + 1.0) + 0.14 * n1(x * 21.0, s + 2.0) + 0.07 * n1(x * 47.0, s + 3.0);
}
// Distance to a bolt from a to b; t returns the position along it (0..1).
float boltD(vec2 p, vec2 a, vec2 b, float s, float amp, out float t) {
    vec2 ab = b - a; float L = max(length(ab), 1e-4); vec2 dir = ab / L, n = vec2(-dir.y, dir.x);
    vec2 q = p - a;
    t = dot(q, dir) / L;
    float tc = sat(t);
    float off = jag(tc * L, s) * amp * (0.25 + 0.75 * sin(PI * tc));
    return length(vec2((t - tc) * L, dot(q, n) - off));
}
vec2 boltPoint(vec2 a, vec2 b, float s, float amp, float t) {
    vec2 ab = b - a; float L = max(length(ab), 1e-4); vec2 dir = ab / L, n = vec2(-dir.y, dir.x);
    return a + ab * t + n * jag(t * L, s) * amp * (0.25 + 0.75 * sin(PI * t));
}
float boltLight(float d, float t, float w) {
    float taper = mix(1.0, 0.4, sat(t)) * w;
    float wc = max(0.0035, px().y * 0.7) * taper;
    return exp(-d / wc) + 0.7 * exp(-d / (0.018 * taper)) + 0.3 * exp(-d / (0.07 * taper));
}
void main() {
    vec4 src = S(v_texCoord);
    float A = aspect();
    // Bolts that surround a point follow Center X/Y; scattered ones fill the frame.
    vec2 cc = MODE > 0.5 ? (vec2(center_x, center_y) - 0.5) * vec2(A, 1.0) : vec2(0.0);
    vec2 p = toP(v_texCoord) - cc;
    float t = u_time * speed;
    float nb = clamp(floor(NB * density + 0.5), 1.0, 8.0);
    float len = LEN * size, r0 = R0 * size;
    vec2 q = p;
    if (MODE > 2.5) {               // vortex: twist the space around the centre, turning slowly
        float r = length(p);
        q = rot(r * 4.0 - t * 1.2) * p;
    }
    float core = 0.0, halo = 0.0, flash = 0.0;
    for (int i = 0; i < 8; ++i) {
        if (float(i) >= nb) break;
        float fi = float(i);
        float hb = hash11(fi * 7.31 + 1.0);
        float clk = t * RATE * (0.8 + 0.5 * hb) + hb * 5.0;
        float strike = floor(clk), life = fract(clk);
        float on = step(0.15, hash12(vec2(strike, fi + 3.0)));
        // A strike flickers a few times and fades.
        float vis = on * exp(-life * 4.0) * (0.55 + 0.45 * step(0.45, fract(life * 9.0 + hb)));
        if (vis < 0.01) continue;
        float sd = strike * 3.1 + fi * 11.7;
        vec3 rr = hash32(vec2(sd, fi * 1.9 + 0.3));
        vec2 a, b;
        if (MODE < 0.5) {
            a = (rr.xy - 0.5) * vec2(A, 1.0) * 0.95;
            float ang = rr.z * TAU;
            b = a + vec2(cos(ang), sin(ang)) * len * (0.6 + 0.4 * hash11(sd));
        } else if (MODE < 1.5 || MODE > 2.5) {
            float ang = (fi + rr.x * 0.8) / nb * TAU + rr.y;
            vec2 dir = vec2(cos(ang), sin(ang));
            a = dir * r0 * vec2(0.8, 1.15);
            b = dir * (r0 + len * (0.6 + 0.4 * rr.z)) * vec2(1.3, 1.0);
        } else {
            a = vec2((rr.x - 0.5) * A * 0.5, -0.6);
            b = vec2((rr.y - 0.5) * A * 0.6, 0.6);
        }
        float amp = AMP * length(b - a);
        float tt;
        float d = boltD(q, a, b, sd, amp, tt);
        float l = boltLight(d, tt, THICK * width);
        // One branch leaving the bolt part way along.
        float t0 = 0.25 + 0.4 * hash11(sd + 4.0);
        vec2 a2 = boltPoint(a, b, sd, amp, t0);
        vec2 dir2 = rot((hash11(sd + 5.0) > 0.5 ? 0.6 : -0.6)) * normalize(b - a);
        vec2 b2 = a2 + dir2 * length(b - a) * (0.3 + 0.25 * hash11(sd + 6.0));
        float t2;
        float d2 = boltD(q, a2, b2, sd + 9.0, amp * 0.8, t2);
        l += 0.7 * boltLight(d2, 0.4 + 0.6 * t2, THICK * width * 0.7);
        core += vis * l;
        flash += vis;
    }
    vec3 base = src.rgb * (1.0 - DARKEN * sat(intensity));
    base = mix(base, base * (color * 0.6 + 0.4) * 1.2, TINT);
    // Glow around the subject (energy bursts behind a person).
    if (CGLOW > 0.0) {
        float r = length(p * vec2(0.8, 1.0));
        float pulse = 0.7 + 0.3 * sin(t * 6.0) * hash11(floor(t * 8.0));
        float ring = exp(-abs(r - r0 * 1.1) / (0.06 * size)) * (0.6 + 0.4 * fbm(vec2(atan(p.y, p.x) * 3.0, t * 2.0)));
        base = addLight(base, color, CGLOW * ring * pulse * intensity * 0.9);
    }
    vec3 light = color * (1.1 * core + 0.12 * FLASH * flash);
    vec3 col = addLight(base, light, intensity);
    col = mix(col, vec3(1.0), sat(core - 0.7) * 0.85 * sat(intensity));
    fragColor = vec4(occlude(col, src.rgb, v_texCoord), src.a);
}
""",
    variants=[
        Variant("rayos-01", "Rayos 01", "Lightning 01", photo="dark", thumb=1.7,
                defines={"NB": 5, "LEN": 0.65}),
        Variant("relampagos", "Relámpagos", "Dazzling lightning", photo="dark", thumb=2.25,
                defines={"NB": 3, "LEN": 1.0, "AMP": 0.09, "THICK": 1.4, "RATE": 1.2, "FLASH": 0.4},
                params={"color": "#dfe8ff"}),
        Variant("fondo-de-relampago", "Fondo de relámpago", "Lightning background", photo="fx-cyber-02", thumb=2.3,
                defines={"MODE": 1, "NB": 6, "LEN": 0.45, "R0": 0.22, "CGLOW": 0.6, "DARKEN": 0.25},
                params={"color": "#3d8bff"}),
        Variant("descarga-electrica", "Descarga eléctrica", "Electric discharge", photo="cyber", thumb=2.85,
                defines={"MODE": 1, "NB": 8, "LEN": 0.4, "R0": 0.18, "AMP": 0.12, "RATE": 2.6, "THICK": 1.4,
                         "DARKEN": 0.3, "FLASH": 0.4}, params={"color": "#8ab8ff"}),
        Variant("vortice-de-relampagos", "Vórtice de relámpagos", "Lightning vortex", photo="cyber", thumb=1.3,
                defines={"MODE": 3, "NB": 6, "LEN": 0.55, "R0": 0.16, "RATE": 2.0, "CGLOW": 0.4, "DARKEN": 0.2},
                params={"color": "#9a6dff"}),
        Variant("explosion-de-energia", "Explosión de energía", "Energy explosion", photo="dancer", thumb=2.5,
                defines={"MODE": 1, "NB": 6, "LEN": 0.5, "R0": 0.24, "CGLOW": 1.2, "RATE": 2.2, "FLASH": 0.4,
                         "DARKEN": 0.2}, params={"color": "#c08cff"}),
        Variant("luz-electrica", "Luz eléctrica", "Electric light", photo="figure", thumb=1.2,
                defines={"NB": 6, "LEN": 0.85, "FLASH": 0.9, "DARKEN": 0.45, "TINT": 0.8, "THICK": 2.0},
                params={"color": "#b9a8ff"}),
        Variant("cupula-del-trueno", "Cúpula del trueno", "Thunder dome", photo="figure", thumb=2.7,
                defines={"MODE": 2, "NB": 1, "AMP": 0.12, "THICK": 2.6, "RATE": 1.0, "FLASH": 0.6, "TINT": 0.9,
                         "DARKEN": 0.45}, params={"color": "#7ab8ff"}),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Fire: rising, domain-warped noise shaped by a mask (where the flames are born) and coloured on a heat ramp.
#   MODE 0 on the ground, 1 all around the frame, 2 a ring (ellipse RX × RY at CY, turning), 3 a band scanning up,
#   4 the whole frame (billowing explosion).
FIRE = Family(
    key="en_fire", category="energia",
    params=[INTENSITY, SPEED, Param("color_a", "Colour A", default="#ffd860"),
            Param("color_b", "Colour B", default="#ff4a0a"), Param("height", "Height", 0.3, 2.5, 1.0), SIZE] + CENTER,
    photo="dark", tags=["fuego", "fire", "llamas", "flames", "incendio", "calor", "heat"],
    defines={"MODE": 0, "HGT": 0.35, "FREQ": 3.0, "CY": 0.0, "RX": 0.33, "RY": 0.33, "DARKEN": 0.3,
             "RISE": 1.6, "HEATK": 1.25},
    body=r"""@OCC@
// Heat 0..1 to colour: the edge colour (B) fading in, the core colour (A) in the hot part, white at the very top.
vec3 heatRamp(float h) {
    h = sat(h);
    vec3 c = color_b * sat(h * 2.0);
    c = mix(c, color_a, smoothstep(0.45, 0.8, h));
    return sat3(mix(c, vec3(1.0), smoothstep(0.8, 1.0, h) * 0.8));
}
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    float A = aspect();
    float hgt = HGT * height;
    vec2 cc = (vec2(center_x, center_y) - 0.5) * vec2(A, 1.0);   // ring and explosion centre
    float m;
    vec2 fp = p;
    if (MODE < 0.5) {
        m = linstep(0.5 - hgt, 0.52, p.y);
        m *= m;
    } else if (MODE < 1.5) {
        float e = min(A * 0.5 - abs(p.x), 0.5 - abs(p.y));
        float bottom = linstep(0.5 - hgt * 1.4, 0.5, p.y);
        m = max(1.0 - linstep(0.0, hgt, e), bottom * bottom);
        m = pow(m, 1.6);
    } else if (MODE < 2.5) {
        vec2 c = p - cc - vec2(0.0, CY);
        vec2 rad = vec2(RX, RY) * size;
        float ang = atan(c.y / rad.y, c.x / rad.x);
        float r = length(c / rad);
        float d = abs(r - 1.0) * min(rad.x, rad.y);
        m = 1.0 - linstep(0.0, hgt, d);
        m = m * m;
        // Flames lick round the ring.
        fp = vec2(ang * 0.25 - t * 0.35, r * 0.3) * 2.5 + p * 0.6;
    } else if (MODE < 3.5) {
        float yf = 0.75 - fract(t * 0.35) * 1.6;
        m = linstep(yf - 0.02, yf + hgt * 0.35, p.y) * (1.0 - linstep(yf + hgt * 0.3, yf + hgt, p.y));
        m = pow(m, 0.8);
    } else {
        float b = beat(t, 2.0, 0.6);
        m = 0.45 + 0.3 * b - 0.2 * linstep(0.1 * size, 0.8 * size, length(p - cc)) + 0.1 * sin(t * 1.3);
    }
    vec2 qn = vec2(fp.x * FREQ, fp.y * FREQ * 0.8 + t * RISE);
    vec2 warp = vec2(fbm(qn * 0.7 + vec2(0.0, t * 0.4)), fbm(qn * 0.7 + vec2(5.2, 1.3 + t * 0.4))) - 0.5;
    float n = fbm(qn + warp * 1.4);
    float fine = vnoise(qn * 3.0 + vec2(0.0, t * RISE * 2.0));
    float heat = m * HEATK + (n - 0.5) * 1.6 + (fine - 0.5) * 0.25 - 0.35;
    heat = sat(heat) * smoothstep(0.0, 0.15, m);
    vec3 fire = heatRamp(heat);
    // Smoke-dark under the flames, warm glow around them.
    vec3 base = src.rgb * (1.0 - DARKEN * sat(m) * sat(intensity));
    base = addLight(base, color_b, 0.35 * m * intensity);
    vec3 col = mix(base, fire, sat(heat * 1.8) * sat(intensity) * 0.85);
    col = addLight(col, fire, intensity * 0.6);
    fragColor = vec4(occlude(col, src.rgb, v_texCoord), src.a);
}
""",
    variants=[
        Variant("fuego-en-el-suelo", "Fuego en el suelo", "Burning ground", photo="dark", thumb=1.0,
                defines={"MODE": 0, "HGT": 0.3}),
        Variant("fuego-escaneando-hacia-arriba", "Fuego escaneando hacia arriba", "Fire scanning up", photo="dark",
                thumb=1.4, defines={"MODE": 3, "HGT": 0.45, "FREQ": 3.5}),
        Variant("fondo-de-explosion", "Fondo de explosión", "Explosion background", photo="dancer", thumb=1.2,
                defines={"MODE": 1, "HGT": 0.3, "FREQ": 2.5, "DARKEN": 0.2, "HEATK": 0.95}),
        Variant("explosion-fuego", "Explosión fuego", "Fire explosion", photo="dark", thumb=0.3,
                defines={"MODE": 4, "FREQ": 1.8, "RISE": 1.2, "DARKEN": 0.6}),
        Variant("anillo-de-fuego", "Anillo de fuego", "Ring of fire", photo="dark", thumb=1.0,
                defines={"MODE": 2, "HGT": 0.12, "RX": 0.42, "RY": 0.36, "FREQ": 3.0}),
        Variant("envolvente-de-fuego-azul", "Envolvente de fuego azul", "Blue fire wrap", photo="dancer", thumb=1.0,
                defines={"MODE": 2, "HGT": 0.09, "RX": 0.3, "RY": 0.08, "CY": 0.12, "FREQ": 3.5,
                         "DARKEN": 0.05}, params={"color_a": "#a8e8ff", "color_b": "#2a6aff"}),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Embers and sparks: three depth layers of glowing specks that rise (drift along DIR), wobble, flicker and fade.
EMBERS = Family(
    key="en_embers", category="energia", params=[INTENSITY, SPEED, color("#ff7a1a"), DENSITY, SIZE],
    photo="dark", tags=["brasas", "embers", "chispas", "sparks", "ceniza", "ash", "fuego", "fire"],
    defines={"DIR": (0.0, -1.0), "STREAK": 1.0, "BGLOW": 0.0, "SIZE": 1.0, "FALL": 0.35},
    body=r"""@OCC@
float layer(vec2 p, float t, float scale, float seed, out float hue) {
    vec2 d = normalize(DIR);
    vec2 side = vec2(-d.y, d.x);
    // Rotate into the drift frame: x across, y against the motion.
    vec2 q = vec2(dot(p, side), -dot(p, d)) * scale;
    float colI = floor(q.x);
    q.y += t * FALL * scale * (0.7 + 0.6 * hash11(colI + seed));
    q.x += 0.25 * sin(q.y * 0.9 + seed + colI);
    vec2 cell = floor(q), f = fract(q) - 0.5;
    float h = hash12(cell + seed);
    hue = hash12(cell + seed + 4.0);
    if (h > 0.45 * density) return 0.0;
    vec2 o = (hash22(cell + seed * 1.7) - 0.5) * 0.7;
    float r = (0.04 + 0.07 * hash12(cell + 9.1 + seed)) * SIZE * size;
    vec2 v = f - o;
    v.y /= STREAK;                  // stretched along the motion
    float g = exp(-dot(v, v) / (r * r)) + 0.25 * exp(-dot(v, v) / (r * r * 9.0));
    float fl = 0.55 + 0.45 * sin(t * (4.0 + 8.0 * h) + h * 40.0);
    return g * fl;
}
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    float h1, h2, h3;
    float a = layer(p, t, 16.0, 1.0, h1);
    float b = layer(p, t, 9.0, 7.0, h2);
    float c = layer(p, t, 4.5, 13.0, h3);
    vec3 c1 = mix(color, vec3(1.0, 0.85, 0.4), h1 * 0.6);
    vec3 c2 = mix(color, vec3(1.0, 0.8, 0.35), h2 * 0.6);
    vec3 c3 = mix(color, vec3(1.0, 0.75, 0.3), h3 * 0.6);
    vec3 light = c1 * a * 0.6 + c2 * b * 0.9 + c3 * c * 0.8;
    light += vec3(1.0, 0.95, 0.8) * sat(a + b + c - 1.2) * 0.5;
    vec3 base = src.rgb;
    if (BGLOW > 0.0) {
        float g = linstep(0.0, 0.55, p.y) * (0.8 + 0.2 * fbm(vec2(p.x * 3.0, t)));
        base = addLight(base * (1.0 - 0.25 * BGLOW), color * vec3(1.0, 0.6, 0.4), BGLOW * g * g * intensity);
    }
    fragColor = vec4(occlude(addLight(base, light, intensity * 1.2), src.rgb, v_texCoord), src.a);
}
""",
    variants=[
        Variant("ceniza-de-fuego-de-batalla", "Ceniza de fuego de batalla", "Battle fire ash", photo="dark",
                thumb=1.2, defines={"DIR": (0.35, -1.0), "STREAK": 1.0, "SIZE": 0.7, "FALL": 0.25},
                params={"density": 0.8}),
        Variant("brasas", "Brasas", "Embers", photo="dark", thumb=1.0,
                defines={"STREAK": 1.6, "BGLOW": 0.35, "FALL": 0.3}, params={"color": "#ff4a12"}),
        Variant("particulas-de-llamas-voladoras", "Partículas de llamas voladoras", "Flying flame particles",
                photo="dark", thumb=1.4, defines={"DIR": (0.5, -1.0), "STREAK": 3.0, "SIZE": 0.9, "FALL": 0.7,
                                                   "BGLOW": 0.2}, params={"density": 0.9}),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Warps: the picture bent by energy. MODE 0 shockwave rings that refract outward from the centre, 1 vortex rings
# that twist everything around the subject, 2 a spiral tunnel of light.
WARP = Family(
    key="en_warp", category="energia", params=[INTENSITY, SPEED, color("#2fe0ff"), SIZE] + CENTER,
    photo="cyber", tags=["vortice", "vortex", "onda", "wave", "energia", "energy", "remolino", "swirl"],
    defines={"MODE": 0, "PERIOD": 1.0, "R0": 0.18},
    body=r"""@OCC@
void main() {
    vec2 uv = v_texCoord;
    vec2 cc = (vec2(center_x, center_y) - 0.5) * vec2(aspect(), 1.0);
    vec2 p = toP(uv) - cc;
    float t = u_time * speed;
    float r = length(p) / size, a = atan(p.y, p.x);
    float r0 = R0;
    vec3 col;
    if (MODE < 0.5) {
        // Two rings in flight, each growing over PERIOD and fading as it leaves.
        float disp = 0.0, glow = 0.0;
        for (int i = 0; i < 2; ++i) {
            float ph = fract(t / PERIOD + float(i) * 0.5);
            float R = 0.05 + ph * 0.75;
            float x = (r - R) / 0.09;
            float w = (1.0 - ph);
            disp += -x * exp(-x * x) * 0.11 * w;
            glow += exp(-x * x * 1.5) * w;
        }
        float ripple = fbm(vec2(a * 3.0, r * 8.0 - t * 3.0));
        vec2 dir = p / max(r, 1e-4);
        vec2 off = dir * (disp + (ripple - 0.5) * 0.02) * intensity;
        vec2 o = off / vec2(aspect(), 1.0);
        col = vec3(Sm(uv + o * 1.15).r, Sm(uv + o).g, Sm(uv + o * 0.85).b);
        // Teal energy tint, darker hole in the middle.
        col = mix(col, col * (0.3 + 1.1 * color), 0.65 * sat(intensity));
        col *= 1.0 - 0.55 * exp(-r * r / 0.012) * sat(intensity);
        col = addLight(col, color, glow * (0.5 + 0.8 * ripple) * 1.2 * intensity);
    } else if (MODE < 1.5) {
        // Twist that grows outside the subject, breathing.
        float k = linstep(r0, r0 + 0.5, r);
        k = k * k;
        float tw = k * (0.7 + 0.35 * sin(t * 1.5)) * intensity;
        vec2 q = rot(tw) * p;
        vec2 suv = fromP(q + cc);
        col = Sm(suv).rgb;
        col = mix(col, spinBlur(suv, fromP(cc), 0.25 * k * intensity).rgb, k);
        // Rings of light turning round the subject.
        float rings = 0.0;
        for (int i = 0; i < 3; ++i) {
            float fi = float(i);
            float rr = r0 + 0.06 + fi * 0.09 + 0.02 * sin(t * 2.0 + fi);
            float wob = 0.012 * sin(a * (3.0 + fi) + t * (2.0 + fi));
            rings += exp(-abs(r - rr - wob) / 0.012) * (0.5 + 0.5 * sin(a * 2.0 - t * 3.0 + fi * 2.0));
        }
        col = mix(col, col * (0.6 + 0.5 * color), 0.35 * k);
        col = addLight(col, color, rings * 0.7 * intensity);
    } else {
        // A spiral tunnel of light around a hole that shows the picture sucked in.
        float lr = log(max(r, 1e-3));
        float sp = sin(a * 3.0 + lr * 5.0 - t * 5.0);
        float sp2 = sin(a * 5.0 - lr * 3.0 - t * 3.0 + 1.0);
        float band = smoothstep(0.0, 0.8, sp) * 0.85 + smoothstep(0.5, 1.0, sp2) * 0.35;
        float n = fbm(vec2(a * 2.0 + t, lr * 3.0 - t * 2.0));
        vec3 tun = mix(color * 0.12, color * 1.1, band) * (0.55 + 0.7 * n);
        tun = mix(tun, vec3(1.0, 0.95, 0.75), sat(band * n * 1.3 - 0.6));
        vec2 q = rot(0.4 * sin(t) + 0.15 / (r + 0.15)) * p * 0.95;
        vec3 pic = Sm(fromP(q + cc)).rgb;
        float hole = 1.0 - smoothstep(r0 * 0.6, r0 * 1.6, r);
        float alpha = sat(intensity) * 0.85 * (1.0 - hole);
        col = mix(pic, tun, alpha);
        col = addLight(col, color, exp(-abs(r - r0 * 1.2) / 0.03) * 0.6 * intensity);
    }
    fragColor = vec4(occlude(col, S(uv).rgb, uv), S(uv).a);
}
""",
    variants=[
        Variant("energia-de-onda-de-choque", "Energía de onda de choque", "Shockwave energy", photo="cyber",
                thumb=0.6, defines={"MODE": 0, "PERIOD": 1.2}),
        Variant("anillos-de-vortice", "Anillos de vórtice", "Vortex rings", photo="cyber", thumb=1.2,
                defines={"MODE": 1, "R0": 0.26}, params={"color": "#8a7dff"}),
        Variant("vortice-amarillo", "Vórtice amarillo", "Yellow vortex", photo="dancer", thumb=1.0,
                defines={"MODE": 2, "R0": 0.12}, params={"color": "#ffb413"}),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Spider-web zoom: a glowing web (jittered spokes, polygon rings spaced in log radius) that we fly into for ever.
WEB = Family(
    key="en_web", category="energia",
    params=[INTENSITY, SPEED, color("#ff3a4a"), WIDTH, Param("center_x", "Center X", 0.0, 1.0, 0.517),
            Param("center_y", "Center Y", 0.0, 1.0, 0.48)],
    photo="dark", tags=["telarana", "spider web", "zoom", "red", "web"],
    defines={"SPOKES": 11.0},
    body=r"""@OCC@
void main() {
    vec2 uv = v_texCoord;
    vec2 p = toP(uv);
    float t = u_time * speed;
    float zoomPh = fract(t * 0.5);
    // The picture pushes in a little on every loop of the web.
    vec4 src = zoomBlur(uv, vec2(center_x, center_y), 0.04 * intensity * (1.0 - zoomPh));
    vec2 c = p - (vec2(center_x, center_y) - 0.5) * vec2(aspect(), 1.0);
    float r = length(c), a = atan(c.y, c.x) + PI;
    float seg = TAU / SPOKES;
    float k = floor(a / seg);
    // Jittered spoke angles at both sides of this sector.
    float a0 = (k + 0.5 * (hash11(k) - 0.5)) * seg;
    float a1 = (k + 1.0 + 0.5 * (hash11(mod(k + 1.0, SPOKES)) - 0.5)) * seg;
    if (a < a0) { a1 = a0; a0 = (k - 1.0 + 0.5 * (hash11(mod(k - 1.0 + SPOKES, SPOKES)) - 0.5)) * seg; }
    else if (a > a1) { a0 = a1; float k2 = k + 2.0; a1 = (k2 + 0.5 * (hash11(mod(k2, SPOKES)) - 0.5)) * seg; }
    float dSpoke = min(abs(sin(a - a0)), abs(sin(a - a1))) * r;
    // Rings: straight chords between the spokes, at radii spaced in log space and flowing outward.
    float mid = 0.5 * (a0 + a1), halfA = 0.5 * (a1 - a0);
    float rp = r * cos(a - mid) / cos(halfA);
    float stp = 0.32;
    float lr = (log(max(rp, 1e-3)) - t * 0.5 * stp * 2.0) / stp;
    float fr = fract(lr) - 0.5;
    float sag = 0.08 * sin(PI * sat((a - a0) / max(a1 - a0, 1e-3)));
    float dRing = abs(fr + sag) * stp * rp;
    float w = (0.0015 + 0.0015 * r) * width;
    float line = exp(-dSpoke / w) + exp(-dRing / w);
    float halo = exp(-min(dSpoke, dRing) / (w * 6.0));
    float fadeC = linstep(0.01, 0.06, r);
    float web = (line + 0.4 * halo) * fadeC;
    vec3 base = src.rgb * (1.0 - 0.45 * sat(intensity));
    vec3 lc = mix(color, vec3(1.0), 0.45 * hash11(floor(lr) + k));
    vec3 col = addLight(base, lc, web * intensity * (0.8 + 0.2 * sin(t * 7.0)));
    fragColor = vec4(occlude(col, src.rgb, uv), src.a);
}
""",
    variants=[
        Variant("zoom-de-telarana", "Zoom de telaraña", "Spider-web zoom", photo="dark", thumb=1.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Fireworks: rockets rise with a fading trail and burst into a ring of streaking sparks that droop and fade.
FIREWORKS = Family(
    key="en_fireworks", category="energia",
    params=[INTENSITY, SPEED, color("#ff4fa0"), Param("color_mix", "Mix", 0.0, 1.0, 0.0), SIZE, DENSITY],
    photo="dark", tags=["fuegos artificiales", "fireworks", "fiesta", "party", "festival", "celebracion"],
    defines={"PERIOD": 2.2},
    body=r"""@OCC@
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    float A = aspect();
    vec3 light = vec3(0.0);
    float nr = clamp(floor(7.0 * density + 0.5), 1.0, 10.0);
    for (int i = 0; i < 10; ++i) {
        if (float(i) >= nr) break;
        float fi = float(i);
        float clk = t / PERIOD + hash11(fi * 3.7);
        float n = floor(clk), ph = fract(clk);
        vec3 rr = hash32(vec2(n * 1.3 + fi, fi * 7.1));
        // Random colours; Mix pulls them toward Colour.
        vec3 hue = mix(hsv2rgb(vec3(rr.z, 0.75, 1.0)), color, color_mix);
        vec2 top = vec2((rr.x - 0.5) * A * 0.85, -0.35 + rr.y * 0.3);
        vec2 start = vec2(top.x + (rr.y - 0.5) * 0.15, 0.6);
        float launch = 0.35;
        if (ph < launch) {
            float k = easeOut(ph / launch);
            vec2 head = mix(start, top, k);
            vec2 tail = mix(start, top, max(k - 0.25, 0.0));
            float d = sdSegment(p, tail, head);
            float along = sat(dot(p - tail, head - tail) / max(dot(head - tail, head - tail), 1e-5));
            light += hue * (exp(-d / 0.0045) * along + 0.4 * exp(-d / 0.015) * along);
            light += vec3(1.0, 0.9, 0.7) * exp(-length(p - head) / 0.006);
        } else {
            float b = (ph - launch) / (1.0 - launch);
            float R = 0.45 * size * (0.7 + 0.5 * rr.y) * easeOut(b * 1.3);
            vec2 q = p - top - vec2(0.0, 0.12 * b * b);      // gravity
            float N = 18.0;
            float ang = atan(q.y, q.x);
            float j = floor(ang / TAU * N + 0.5);
            float sa = j / N * TAU;
            vec2 dir = vec2(cos(sa), sin(sa));
            float Rj = R * (0.85 + 0.3 * hash11(j + n * 5.0 + fi));
            float d = sdSegment(q, dir * Rj * 0.55, dir * Rj);
            float fade = (1.0 - b) * (1.0 - b);
            float spark = exp(-d / 0.0055) + 0.4 * exp(-d / 0.02);
            float tw = 0.6 + 0.4 * step(0.4, hash12(vec2(j, floor(t * 14.0) + fi)));
            light += mix(hue, vec3(1.0), 0.3) * spark * fade * tw * 1.2;
            light += hue * exp(-length(q) / 0.12) * 0.25 * exp(-b * 6.0);
        }
    }
    vec3 col = addLight(src.rgb * (1.0 - 0.15 * sat(intensity)), light, intensity);
    fragColor = vec4(occlude(col, src.rgb, v_texCoord), src.a);
}
""",
    variants=[
        Variant("fuegos-artificiales", "Fuegos artificiales", "Fireworks", photo="dark", thumb=0.95),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Smoke lines: thin wisps (contours of a slowly warped noise) curling up over the picture.
SMOKE = Family(
    key="en_smoke", category="energia", params=[INTENSITY, SPEED, color("#ffffff"), SIZE, DENSITY],
    photo="woman", tags=["humo", "smoke", "lineas", "lines", "niebla", "mist"],
    body=r"""@OCC@
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed * 0.35;
    vec2 q = p * 2.2 / size + vec2(0.0, t * 1.2);
    vec2 w = vec2(vnoise(q * 0.8 + vec2(t * 0.6, 0.0)) + 0.5 * vnoise(q * 1.7 + 4.0),
                  vnoise(q * 0.8 + vec2(3.1, 7.7) - vec2(0.0, t * 0.5)) + 0.5 * vnoise(q * 1.7 + 9.0)) / 1.5 - 0.5;
    float v = fbm(q + w * 2.2);
    float lines = 0.0;
    float v2 = vnoise(q * 1.3 + w * 1.5) * 0.6 + vnoise(q * 2.6 + w) * 0.4;
    float c1 = abs(fract(v2 * 3.0) - 0.5);
    lines += exp(-c1 / 0.05) * 0.6 + exp(-c1 / 0.15) * 0.25;
    float th = 0.36 - 0.15 * (density - 1.0);   // more density, more of the frame in smoke
    float patch_ = smoothstep(th, th + 0.33, fbm(p * 1.4 / size + vec2(-t * 0.4, t * 0.8)));
    float haze = fbm(q * 0.7 + w) * patch_;
    float s = lines * patch_ * 1.1 + haze * 0.22;
    vec3 col = addLight(src.rgb, color, s * intensity);
    fragColor = vec4(occlude(col, src.rgb, v_texCoord), src.a);
}
""",
    variants=[
        Variant("lineas-de-humo", "Líneas de humo", "Smoke lines", photo="woman", thumb=2.9),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# A ribbon of light that sweeps round the frame, bright at the head and fading along its tail, shedding sparkles.
TRAIL = Family(
    key="en_trail", category="energia", params=[INTENSITY, SPEED, color("#ff5fc0"), WIDTH, SIZE],
    photo="woman", tags=["estela", "trail", "rosa", "pink", "luz", "light", "brillo"],
    body=r"""@OCC@
vec2 path(float s) {
    return vec2(0.38 * aspect() * sin(s * 1.1) * 0.9, 0.32 * sin(s * 1.9 + 0.6) + 0.04 * sin(s * 5.0)) * size;
}
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed * 1.4;
    float glow = 0.0, core = 0.0;
    vec2 prev = path(t);
    for (int i = 1; i < 18; ++i) {
        float s = t - float(i) * 0.09;
        vec2 cur = path(s);
        float d = sdSegment(p, prev, cur);
        float age = float(i) / 17.0;
        float w = mix(0.02, 0.004, age) * width;
        float k = (1.0 - age);
        core = max(core, exp(-d / (w * 0.35)) * k);
        glow += exp(-d / (w * 2.5)) * k * 0.25;
        prev = cur;
    }
    // Sparkles left behind the head.
    vec2 g = p * 26.0;
    vec2 cell = floor(g);
    vec2 o = hash22(cell) - 0.5;
    float life = fract(hash12(cell + 3.0) + t * 0.7);
    float sp = twinkle((fract(g) - 0.5 - o * 0.6) / 26.0, 0.01) * step(hash12(cell + 9.0), 0.25) * (1.0 - life);
    sp *= smoothstep(0.25, 0.0, sdSegment(p, path(t), path(t - 0.6))) ;
    vec3 head = vec3(1.0) * exp(-length(p - path(t)) / 0.012);
    vec3 light = color * (glow + core * 0.6) + vec3(1.0, 0.9, 0.97) * (core * 0.6 + sp) + head;
    fragColor = vec4(occlude(addLight(src.rgb, light, intensity), src.rgb, v_texCoord), src.a);
}
""",
    variants=[
        Variant("estela-rosa", "Estela rosa", "Pink trail", photo="woman", thumb=1.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Glowing footprints that appear one after another across the floor, then fade.
FOOT = Family(
    key="en_foot", category="energia", params=[INTENSITY, SPEED, color("#ffd27a"), SIZE],
    photo="figure", tags=["huellas", "footprints", "pasos", "steps", "rastro", "trail", "brillo", "glow"],
    defines={"PERIOD": 3.0},
    body=r"""@OCC@
float footSd(vec2 q, float side) {
    q.x *= side;
    float sole = length((q - vec2(0.0, -0.01)) / vec2(0.0105, 0.021)) - 1.0;
    float heel = length((q - vec2(0.002, 0.024)) / vec2(0.0075, 0.0105)) - 1.0;
    float d = min(sole, heel) * 0.009;
    for (int k = 0; k < 4; ++k) {
        float fk = float(k);
        vec2 c = vec2(-0.0085 + fk * 0.0062, -0.041 + abs(fk - 0.8) * 0.0035);
        d = min(d, length(q - c) - (0.0034 - fk * 0.0004));
    }
    return d;
}
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    float A = aspect();
    float ph = fract(t / PERIOD);
    float light = 0.0;
    vec2 a = vec2(-A * 0.3, 0.46), b = vec2(A * 0.3, 0.06);
    vec2 dir = normalize(b - a), nrm = vec2(-dir.y, dir.x);
    float ang = atan(dir.y, dir.x) + PI * 0.5;
    for (int i = 0; i < 10; ++i) {
        float fi = float(i);
        float k = fi / 9.0;
        float sc = mix(4.2, 2.2, k) * size;   // perspective: nearer prints are bigger
        vec2 c = mix(a, b, k) + nrm * (mod(fi, 2.0) < 0.5 ? 0.035 : -0.035) * sc;
        float born = fi * 0.075;
        float age = ph - born;
        if (age < 0.0) continue;
        float vis = exp(-age * 2.6) * 0.7 + 0.3 * exp(-age * 0.6);
        vis *= 1.0 - linstep(0.85, 1.0, ph);
        vis *= 1.0 + 1.5 * exp(-age * 40.0);
        vec2 q = rot(ang) * (p - c) / sc;
        q.y *= 1.1;
        float d = footSd(q, mod(fi, 2.0) < 0.5 ? 1.0 : -1.0) * sc;
        light += vis * (smoothstep(0.0015, -0.0015, d) * 0.95 + 0.3 * exp(-max(d, 0.0) / 0.008));
    }
    vec3 col = addLight(src.rgb * (1.0 - 0.15 * sat(intensity)), color, light * intensity * 1.4);
    fragColor = vec4(occlude(col, src.rgb, v_texCoord), src.a);
}
""",
    variants=[
        Variant("rastro-de-huellas", "Rastro de huellas", "Glowing footprints", photo="figure", thumb=0.9),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Charging in the dark: the picture goes dark, a ring of light charges up in the centre, flashes and reveals it.
CHARGE = Family(
    key="en_charge", category="energia", params=[INTENSITY, SPEED, color("#7fe8ff"), SIZE] + CENTER,
    photo="cyber", tags=["carga", "charge", "oscuro", "dark", "loading", "brillo", "glow", "revelar", "reveal"],
    defines={"PERIOD": 3.0},
    body=r"""@OCC@
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = (toP(v_texCoord) - (vec2(center_x, center_y) - 0.5) * vec2(aspect(), 1.0)) / size;
    float t = u_time * speed;
    float ph = fract(t / PERIOD);
    float charge = linstep(0.0, 0.42, ph);
    float fl = ph > 0.42 ? exp(-(ph - 0.42) * 14.0) : 0.0;
    float reveal = linstep(0.42, 0.46, ph) * (1.0 - linstep(0.85, 1.0, ph));
    float dark = mix(0.14, 1.0, reveal);
    vec3 base = src.rgb * dark;
    // The ring fills round clockwise from the top, with a bright head.
    float r = length(p), a = fract(atan(p.x, -p.y) / TAU);
    float R = 0.11;
    float ring = exp(-abs(r - R) / 0.006) + 0.4 * exp(-abs(r - R) / 0.03);
    float filled = step(a, charge);
    float head = exp(-length(p - R * vec2(sin(charge * TAU), -cos(charge * TAU))) / 0.012);
    float showRing = 1.0 - linstep(0.48, 0.68, ph);
    float l = (ring * (0.15 + 0.85 * filled) + head * 1.2) * showRing;
    l += exp(-r / 0.05) * 0.35 * charge * showRing * (0.7 + 0.3 * sin(t * 20.0));
    // Sparks pulled in toward the ring while charging.
    float sp = 0.0;
    for (int i = 0; i < 8; ++i) {
        float fi = float(i);
        float k = fract(ph * 3.0 + hash11(fi));
        float an = hash11(fi * 3.3) * TAU;
        vec2 pos = vec2(cos(an), sin(an)) * mix(0.45, R, easeIn(k));
        sp += exp(-length(p - pos) / 0.004) * k;
    }
    l += sp * showRing * 0.8;
    // The flash spreads from the centre.
    float wave = exp(-abs(r - (ph - 0.42) * 2.5) / 0.05) * fl;
    vec3 col = addLight(base, color, l * intensity);
    col = addLight(col, mix(color, vec3(1.0), 0.6), (fl * 0.8 + wave) * intensity);
    fragColor = vec4(occlude(col, src.rgb, v_texCoord), src.a);
}
""",
    variants=[
        Variant("carga-en-oscuro", "Carga en oscuro", "Charging in the dark", photo="cyber", thumb=1.6),
    ],
)

# Filmora draws these behind the person: same shaders, but the near part of a depth map stays in front.
LIGHTNING_BEHIND = _behind(LIGHTNING, "en_lightning_behind", ["fondo-de-relampago", "explosion-de-energia"])
FIRE_BEHIND = _behind(FIRE, "en_fire_behind", ["fondo-de-explosion", "envolvente-de-fuego-azul"])
WARP_BEHIND = _behind(WARP, "en_warp_behind", ["anillos-de-vortice"])

FAMILIES = [_plain(f) for f in (LIGHTNING, FIRE, EMBERS, WARP, WEB, FIREWORKS, SMOKE, TRAIL, FOOT, CHARGE)]
FAMILIES += [LIGHTNING_BEHIND, FIRE_BEHIND, WARP_BEHIND]
