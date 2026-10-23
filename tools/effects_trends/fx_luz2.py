"""Efectos › Tendencias, Luz y destellos (segunda mitad): bokeh en las esquinas y en marco, focos y linterna,
bengalas azules, fugas de luz, soles con destello de lente, destellos anamórficos, flashes y estallido de rayos.
Shaders propios de Flip Studio. Todo lo que uno querría ajustar (posición, dirección, ritmo, tamaño) es un
parámetro del panel; los #define que quedan solo eligen la forma de la variante."""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)


def color(default: str) -> Param:
    return Param("color", "Colour", default=default)


def centre(x: float, y: float) -> list:
    """Center X / Center Y in frame units (0..1, a little past the edge for lights that come from outside)."""
    return [Param("center_x", "Center X", -0.2, 1.2, x), Param("center_y", "Center Y", -0.2, 1.2, y)]


# ---------------------------------------------------------------------------------------------------------------
# Bokeh near the corners or all round the frame: soft discs in three depth layers that float, breathe and twinkle.
BOKEH = Family(
    key="luz2_bokeh", category="luz",
    params=[INTENSITY, SPEED, color("#ffb86b"), Param("size", "Size", 0.4, 2.0, 1.0),
            Param("density", "Density", 0.2, 2.0, 1.0),
            Param("spread", "Spread", 0.3, 2.0, 1.0),          # how far in from the edges the discs reach
            Param("blend", "Mix", 0.0, 1.0, 0.0),                # 0 = the colour, 1 = every colour
            Param("strength", "Strength", 0.0, 3.0, 0.0),      # how much the discs shake
            Param("softness", "Softness", 0.0, 1.0, 0.4)],
    photo="dark", tags=["bokeh", "luces", "lights", "desenfoque", "blur", "brillo", "glow"],
    defines={"FRAME": "0"},
    body=r"""
// Where the discs live: 1 near the corners (FRAME 0) or along every edge (FRAME 1).
float edgeMask(vec2 p) {
    vec2 q = abs(p) / vec2(aspect() * 0.5, 0.5);
    float reach = (spread - 1.0) * 0.3;
#if FRAME
    return smoothstep(0.55, 0.92, max(q.x, q.y) + reach);
#else
    float c = length(max(q - 0.25, 0.0)) / 1.06;
    return smoothstep(0.2, 0.7, c + reach);
#endif
}
vec3 discColor(float h) {
    vec3 warm = mix(color, vec3(1.0, 0.95, 0.85), step(0.7, h) * 0.7);
    vec3 hue = hsv2rgb(vec3(fract(0.78 + h * 0.45), 0.65, 1.0));
    return mix(warm, hue, blend);
}
vec3 bokehLayer(vec2 p, float t, float scale, float seed, float soft) {
    vec2 q = p * scale;
    q.y += t * 0.12 * scale * 0.3;
    vec2 cell = floor(q), f = fract(q) - 0.5;
    vec3 h = hash32(cell + seed);
    vec2 o = (hash22(cell + seed * 3.1) - 0.5) * 0.36 + 0.08 * vec2(sin(t * 0.7 + h.x * 6.0), cos(t * 0.6 + h.y * 6.0));
    vec2 c = (cell + 0.5 + o) / scale;
    c.y -= t * 0.12 * 0.3;
    float m = edgeMask(c);
    if (h.x > 0.75 * density * m) return vec3(0.0);
    float r = (0.16 + 0.12 * h.y) * min(size, 1.2);
    float d = length(f - o);
    float disc = smoothstep(r, r * (1.0 - soft), d);
    float rim = smoothstep(r * 0.6, r, d) * disc;
    float tw = 0.55 + 0.45 * sin(t * (1.0 + 2.0 * h.z) + h.x * 30.0);
    return discColor(h.z) * (disc * 0.7 + rim * 0.4) * tw;
}
void main() {
    float t = u_time * speed;
    vec2 uv = v_texCoord + shake2(t, 6.0) * 0.006 * strength;
    vec4 src = S(v_texCoord);
    vec2 p = toP(uv);
    float sf = clamp(softness, 0.05, 0.95);
    vec3 l = bokehLayer(p, t * 0.6, 7.0, 1.0, sf * 0.6) * 0.55
           + bokehLayer(p, t * 0.8, 4.2, 7.0, sf * 0.85) * 0.8
           + bokehLayer(p, t, 2.0, 13.0, min(sf * 1.4, 0.95)) * 0.8;
    // A coloured haze where the discs gather.
    vec3 haze = discColor(0.3) * edgeMask(p) * 0.08 * (0.8 + 0.2 * sin(t * 1.3));
    vec3 col = addLight(src.rgb, l + haze, intensity);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("bokeh-en-las-esquinas", "Bokeh en las esquinas", "Corner bokeh", thumb=1.2,
                tags=["esquinas", "corners", "calido", "warm"]),
        Variant("marco-de-bokeh", "Marco de bokeh", "Bokeh frame", thumb=1.0,
                defines={"FRAME": "1"},
                params={"color": "#ff9ad5", "density": 1.4, "size": 0.8, "blend": 0.85, "strength": 1.0},
                tags=["marco", "frame", "colores", "colourful", "fiesta", "party"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# A light that picks something out of the dark: a stage spotlight from above (MODE 0) or a torch beam (MODE 1).
# Center X/Y: where the spotlight lands (MODE 0) or the middle of the torch's path (MODE 1).
BEAM = Family(
    key="luz2_beam", category="luz",
    params=[INTENSITY, SPEED, color("#ffe2b0"), Param("size", "Size", 0.4, 2.0, 1.0), *centre(0.5, 0.86),
            Param("travel", "Distance", 0.0, 2.0, 1.0),     # how far the light sways / wanders
            Param("softness", "Softness", 0.0, 1.0, 0.5),
            Param("brightness", "Brightness", 0.0, 1.0, 0.45)],  # how dark the rest of the picture goes
    photo="dark", tags=["foco", "spotlight", "escenario", "stage", "luz", "light"],
    defines={"MODE": "0"},
    body=r"""
void main() {
    float t = u_time * speed;
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    vec2 cp = toP(vec2(center_x, center_y));
    float sf = clamp(softness, 0.02, 0.98);
    float dim = mix(1.0, brightness, sat(intensity));
    vec3 col;
#if MODE == 0
    // Stage spotlight: a cone from above the frame to a pool of light on the floor, swaying, dust in the beam.
    float sway = 0.06 * travel * sin(t * 0.8);
    float floorY = cp.y;
    vec2 floorC = vec2(cp.x + sway, floorY);
    vec2 top = vec2(cp.x + sway * 0.4, -0.56);
    float depth = p.y - top.y;
    float cx = mix(top.x, floorC.x, sat(depth / max(floorY - top.y, 0.05)));
    float w = (0.02 + depth * 0.32) * size;
    float cone = smoothstep(w, w * max(1.0 - sf * 1.3, 0.0), abs(p.x - cx)) * smoothstep(floorY + 0.1, floorY - 0.05, p.y);
    float dust = 0.65 + 0.35 * fbm(vec2(p.x * 6.0, p.y * 3.0 - t * 0.4));
    float ray = 0.8 + 0.2 * sin((p.x - cx) / max(w, 0.01) * 9.0 + t * 0.5);
    vec2 pq = (p - floorC) / (vec2(0.36, 0.07) * size);
    float pool = exp(-dot(pq, pq) * 1.5);
    float lamp = exp(-length((p - top) * vec2(1.0, 2.0)) * 9.0);
    float lit = cone * 0.5 * dust * ray + pool * 0.9 + lamp;
    float flick = 0.94 + 0.06 * vnoise(vec2(t * 8.0, 1.0));
    vec3 base = src.rgb * dim;
    base *= 1.0 + (cone + pool) * 0.6 * intensity;
    col = addLight(base, color * lit * flick, intensity);
#else
    // Torch: the scene goes dark and a round beam wanders over it; a cool rim with sparkles round the edge.
    vec2 c = cp + travel * vec2(0.22 * aspect() * sin(t * 0.7), 0.16 * sin(t * 1.1 + 1.0));
    float r = 0.24 * size;
    float d = length(p - c);
    float spot = smoothstep(r, r * (1.0 - sf * 0.9), d);
    float hot = exp(-d * d / (r * r) * 3.0);
    vec3 base = src.rgb * dim;
    base = mix(base, src.rgb * (1.0 + 0.5 * hot * intensity), spot);
    float a = atan(p.y - c.y, p.x - c.x);
    float rim = exp(-abs(d - r * 0.95) / (0.025 * size));
    float sp = pow(vnoise(vec2(a * 7.0, t * 2.5)), 3.0) * 2.5;
    col = addLight(base, color * (rim * (0.35 + sp) + hot * 0.25), intensity);
#endif
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("foco-de-escenario", "Foco de escenario", "Stage spotlight", thumb=1.0, photo="concert",
                tags=["concierto", "concert", "cono", "cone"]),
        Variant("linterna", "Linterna", "Flashlight", thumb=1.5, photo="face",
                defines={"MODE": "1"},
                params={"color": "#6fb4ff", "center_x": 0.5, "center_y": 0.5, "brightness": 0.18},
                tags=["linterna", "flashlight", "torch", "oscuro", "dark", "misterio", "mystery"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Cool flares: a few soft streaks of blue light fanning out from one point, sliding and shimmering.
# Center X/Y = where they come from, Angle = where they point (degrees, 0 = right, 90 = down), Spread = the fan.
STREAKS = Family(
    key="luz2_streaks", category="luz",
    params=[INTENSITY, SPEED, color("#4f8dff"), Param("width", "Width", 0.3, 2.5, 1.0), *centre(0.5, -0.2),
            Param("angle", "Angle", -180.0, 180.0, 90.0), Param("spread", "Spread", 0.2, 3.0, 2.4),
            Param("flicker", "Flicker", 0.0, 1.0, 0.8), Param("glow", "Glow", 0.0, 2.0, 1.0)],
    photo="dark", tags=["bengala", "flare", "azul", "blue", "rayos", "streaks", "luz", "light"],
    body=r"""
void main() {
    float t = u_time * speed;
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    vec2 o = toP(vec2(center_x, center_y));
    vec2 v = p - o;
    float dist = length(v);
    float ang = radians(angle);
    vec3 l = vec3(0.0);
    for (int i = 0; i < 5; ++i) {
        float fi = float(i);
        float h = hash11(fi * 7.3 + 1.0);
        float a = ang + (fi / 4.0 - 0.5) * spread + 0.12 * sin(t * (0.4 + 0.3 * h) + fi * 2.0);
        vec2 dir = vec2(cos(a), sin(a));
        float along = dot(v, dir);
        float across = abs(v.x * dir.y - v.y * dir.x);
        float w = (0.025 + 0.06 * h + along * 0.08) * width;
        float band = exp(-across * across / (w * w)) * smoothstep(-0.05, 0.1, along) * exp(-max(along, 0.0) * (0.9 + h));
        float core = exp(-across * across / (w * w * 0.04)) * smoothstep(-0.02, 0.1, along) * exp(-max(along, 0.0) * 2.5);
        float fl = 1.0 - flicker + flicker * (0.5 + 0.5 * sin(t * (1.3 + h * 2.0) + h * 20.0));
        l += (color * band * 0.8 + mix(color, vec3(1.0), 0.6) * core * 0.35) * fl;
    }
    float g = exp(-dist * 3.2) * 0.9 * glow;
    l += mix(color, vec3(1.0), 0.4) * g * (0.85 + 0.15 * sin(t * 2.0));
    l += color * 0.08 * glow;
    fragColor = vec4(addLight(src.rgb, l, intensity), src.a);
}
""",
    variants=[
        Variant("bengalas-azules", "Bengalas azules", "Blue flares", thumb=1.0, params={"width": 1.6},
                tags=["arriba", "top"]),
        Variant("bengalas-de-color-azul-marino", "Bengalas de color azul marino", "Navy blue flares", thumb=1.4,
                params={"color": "#2f5fd0", "center_x": -0.05, "center_y": -0.05, "angle": 35.5, "spread": 0.7},
                tags=["azul marino", "navy", "diagonal"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Light leaks: big soft blobs of pink and violet light drifting across, and (Mix) a giant out-of-focus orb.
LEAK = Family(
    key="luz2_leak", category="luz",
    params=[INTENSITY, SPEED, Param("color_a", "Colour A", default="#ff3d7a"),
            Param("color_b", "Colour B", default="#7a3dff"), *centre(0.85, 0.75),
            Param("size", "Size", 0.4, 2.0, 1.0), Param("travel", "Distance", 0.0, 2.0, 1.0),
            Param("blend", "Mix", 0.0, 1.0, 0.0)],                # the giant orb, 0 = none
    photo="dark", tags=["fuga de luz", "light leak", "pelicula", "film", "calido", "warm"],
    body=r"""
float blob(vec2 p, vec2 c, vec2 r, float a) {
    vec2 q = rot(a) * (p - c) / r;
    return exp(-dot(q, q));
}
void main() {
    float t = u_time * speed * 0.6;
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    vec2 s = toP(vec2(center_x, center_y));
    float m = travel;
    vec3 l = vec3(0.0);
    l += color_a * blob(p, s + 0.18 * m * vec2(sin(t), cos(t * 0.8)), vec2(0.45, 0.18) * size, 0.6 + 0.2 * sin(t * 0.7)) * 0.9;
    l += color_b * blob(p, s + vec2(-0.3, 0.05) * size + 0.2 * m * vec2(cos(t * 0.9), sin(t * 1.2)), vec2(0.35, 0.3) * size, 0.0) * 0.7;
    l += mix(color_a, vec3(1.0, 0.8, 0.6), 0.5) * blob(p, s + vec2(0.1, -0.25) * size + 0.15 * m * vec2(sin(t * 1.3 + 2.0), 0.0),
                                                         vec2(0.18, 0.5) * size, -0.5) * 0.45;
    // A giant out-of-focus orb across from the leak: a soft disc with a brighter, slightly chromatic rim.
    vec2 oc = toP(vec2(0.98 - center_x, 0.98 - center_y)) + 0.06 * m * vec2(sin(t * 0.8), cos(t * 0.6));
    float od = length(p - oc);
    float R = (0.42 + 0.02 * sin(t * 1.4)) * size;
    float disc = smoothstep(R, R - 0.06, od);
    float rim = exp(-abs(od - R + 0.03) * 40.0);
    l += blend * (color_a * disc * 0.35 + vec3(1.0, 0.7, 0.85) * rim * 0.45 + color_b * exp(-abs(od - R) * 25.0) * 0.25);
    float breathe = 0.75 + 0.25 * sin(t * 1.7) * sin(t * 0.9 + 1.0);
    fragColor = vec4(addLight(src.rgb, l * breathe, intensity), src.a);
}
""",
    variants=[
        Variant("fuga-de-luz-3", "Fuga de luz 3", "Light leak 3", thumb=1.2, tags=["morado", "purple", "rosa", "pink"]),
        Variant("fuga-de-luz-5", "Fuga de luz 5", "Light leak 5", thumb=1.5,
                params={"color_a": "#ff2f8f", "color_b": "#c04dff", "center_x": 0.2, "center_y": 0.8, "blend": 1.0},
                tags=["orbe", "orb", "magenta"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# A sun or lamp with a lens flare: core, haze, rays, a halo ring and ghosts on the line through the centre.
SUN = Family(
    key="luz2_sun", category="luz",
    params=[INTENSITY, SPEED, color("#ffffff"), Param("size", "Size", 0.4, 2.0, 1.0), *centre(0.55, 0.32),
            Param("strength", "Strength", 0.0, 2.0, 0.35),     # the rays
            Param("amount", "Amount", 0.0, 2.0, 0.4),          # the ghosts
            Param("glow", "Glow", 0.0, 2.0, 0.6),              # the haze
            Param("travel", "Distance", 0.0, 0.2, 0.03)],    # how far the sun drifts
    photo="dark", tags=["sol", "sun", "destello", "flare", "lente", "lens", "luz", "light"],
    body=r"""
vec3 ghost(vec2 p, vec2 c, float r, vec3 tint) {
    float d = length(p - c);
    return tint * (smoothstep(r, r * 0.7, d) * 0.5 + exp(-abs(d - r * 0.9) * 60.0) * 0.4);
}
void main() {
    float t = u_time * speed;
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    vec2 s = toP(vec2(center_x, center_y)) + travel * vec2(sin(t * 0.6), cos(t * 0.45));
    vec2 v = p - s;
    float d = length(v);
    float a = atan(v.y, v.x);
    float flick = 0.92 + 0.08 * vnoise(vec2(t * 3.0, 5.0));
    float core = exp(-d / (0.035 * size)) * 1.4;
    float haze = exp(-d / (0.28 * size)) * glow + exp(-d / (0.8 * size)) * glow * 0.35;
    float rays = pow(vnoise(vec2(a * 9.0, t * 0.35)), 3.0) + 0.6 * pow(vnoise(vec2(a * 23.0 + 4.0, -t * 0.25)), 4.0);
    rays *= exp(-d / (0.3 * size)) * strength * 1.6;
    float ring = exp(-abs(d - 0.3 * size) * 30.0) * 0.12 * (0.6 + 0.4 * sin(a * 3.0 + t));
    vec3 warm = mix(color, vec3(1.0), 0.35);
    vec3 l = warm * (core + rays) * flick + color * haze + vec3(0.6, 0.8, 1.0) * ring;
    // Ghosts along the line from the sun through the centre of the frame.
    vec2 axis = -s;
    l += amount * ghost(p, s + axis * 0.7, 0.035, vec3(0.5, 0.35, 0.9) * 0.6);
    l += amount * ghost(p, s + axis * 1.25, 0.075, vec3(0.3, 0.5, 0.9) * 0.45);
    l += amount * ghost(p, s + axis * 1.55, 0.02, vec3(0.9, 0.5, 0.7) * 0.7);
    l += amount * ghost(p, s + axis * 1.9, 0.12, vec3(0.4, 0.8, 0.6) * 0.25);
    // A row of small dots (the iris reflection) between the sun and the first ghost.
    for (int i = 0; i < 4; ++i) {
        float k = 0.25 + 0.1 * float(i);
        l += amount * vec3(0.7, 0.5, 1.0) * exp(-pow(length(p - (s + axis * k)) / 0.012, 2.0)) * 0.35;
    }
    fragColor = vec4(addLight(src.rgb, l, intensity), src.a);
}
""",
    variants=[
        Variant("destello-de-lente-6", "Destello de lente 6", "Lens flare 6", thumb=1.0, tags=["centro", "centre"]),
        Variant("destello-dorado", "Destello dorado", "Golden flare", thumb=1.2,
                params={"color": "#ffc35a", "size": 1.3, "center_x": 0.92, "center_y": 0.06, "strength": 0.8,
                        "amount": 1.0, "glow": 0.75},
                tags=["dorado", "golden", "esquina", "corner"]),
        Variant("luz-del-sol-06", "Luz del sol 06", "Sunlight 06", thumb=1.5,
                params={"center_x": 0.04, "center_y": 0.04, "strength": 0.9, "amount": 1.2, "glow": 0.55},
                tags=["esquina", "corner", "blanco", "white"]),
        Variant("luz-del-sol-01", "Luz del sol 01", "Sunlight 01", thumb=1.8,
                params={"color": "#ffd27a", "size": 1.1, "center_x": 0.96, "center_y": 0.02, "strength": 0.5,
                        "amount": 1.3, "glow": 0.85, "travel": 0.05},
                tags=["dorado", "golden", "calido", "warm"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Anamorphic flares: a bright point with a long streak. Fixed and breathing (PATH 0) or a torch that sweeps across
# the frame (PATH 1). Angle turns the streak (and the sweep); Frequency = pulses (PATH 0) or sweeps per second.
ANAMORPHIC = Family(
    key="luz2_anamorphic", category="luz",
    params=[INTENSITY, SPEED, color("#5aa8ff"), Param("width", "Width", 0.3, 2.5, 1.0), *centre(0.5, 0.5),
            Param("angle", "Angle", -90.0, 90.0, 0.0), Param("size", "Size", 0.3, 2.5, 1.0),
            Param("frequency", "Frequency", 0.2, 4.0, 2.0), Param("flicker", "Flicker", 0.0, 1.0, 0.0),
            Param("glow", "Glow", 0.0, 2.0, 0.0),             # a wide soft band round the streak
            Param("amount", "Amount", 0.0, 2.0, 0.0)],        # the vertical spike of the star
    photo="dark", tags=["anamorfico", "anamorphic", "destello", "flare", "horizontal", "cine", "cinema"],
    defines={"PATH": "0", "OVAL": 0.0},
    body=r"""
void main() {
    float t = u_time * speed;
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    vec2 c = toP(vec2(center_x, center_y));
    mat2 R = rot(radians(angle));
    float k = 1.0;
#if PATH == 1
    // Sweeps from off one side to off the other (along the streak), fast in the middle, `frequency` times a second.
    float ph = phase(t * frequency, 1.0);
    c += R * vec2(mix(-0.8, 0.8, easeInOut(ph)) * aspect(), 0.0);
    k = bump(ph);
    float pulse = 1.0 - flicker * 0.4 * vnoise(vec2(t * 12.0, 2.0));
#else
    c += vec2(0.03 * sin(t * 0.7), 0.01 * sin(t * 1.1));
    float pulse = mix(1.0, 0.55 + 0.45 * beat(t, 1.0 / max(frequency, 0.01), 0.18) + 0.25 * vnoise(vec2(t * 12.0, 2.0)),
                      flicker);
#endif
    vec2 v = transpose(R) * (p - c);                 // streak space: x along the streak
    float d = length(v);
    float core = exp(-d / (0.03 * size)) * 1.5 + exp(-d / (0.12 * size)) * 0.35;
    float streak = exp(-abs(v.y) / (0.004 * width)) * exp(-abs(v.x) / (0.55 * width));
    float soft = exp(-abs(v.y) / (0.03 * width)) * exp(-abs(v.x) / (0.35 * width)) * 0.45;
    float wide = exp(-abs(v.y) / (0.18 * width)) * exp(-abs(v.x) / (0.6 * width)) * glow;
    float star = exp(-abs(v.x) / 0.004) * exp(-abs(v.y) / (0.12 * size)) * amount;
    vec2 ov = v / (vec2(0.32, 0.12) * size);
    float oval = exp(-dot(ov, ov) * 1.4) * OVAL;
    vec3 white = vec3(1.0);
    vec3 l = white * (core + star * 0.8 + oval * 0.9) + mix(color, white, 0.5) * streak * 1.2
           + color * (soft + wide * 0.7 + oval * 0.4);
    // Faint chromatic ghosts mirrored through the centre.
    l += color * 0.25 * exp(-pow(length(p + c * 0.6) / 0.05, 2.0))
       + vec3(0.9, 0.4, 0.8) * 0.15 * exp(-pow(length(p + c * 1.1) / 0.03, 2.0));
    fragColor = vec4(addLight(src.rgb, l * k * pulse, intensity), src.a);
}
""",
    variants=[
        Variant("destello-horizontal", "Destello horizontal", "Horizontal flare", thumb=1.0, photo="woman",
                params={"color": "#ff6fd2", "width": 1.8, "center_x": 0.08, "center_y": 0.45, "glow": 1.0,
                        "flicker": 1.0},
                tags=["rosa", "pink", "lateral", "side"]),
        Variant("antorcha-rapida", "Antorcha rápida", "Fast torch", thumb=1.6, defines={"PATH": "1"},
                params={"width": 2.0, "center_y": 0.55, "frequency": 0.714, "amount": 0.5, "glow": 0.5},
                tags=["rapida", "fast", "barrido", "sweep", "azul", "blue"]),
        Variant("destello-anamorfico-de-tv", "Destello anamórfico de TV", "Anamorphic TV flare", thumb=1.0,
                defines={"OVAL": 1.0},
                params={"color": "#9cc4ff", "width": 1.4, "center_y": 0.52, "flicker": 0.4},
                tags=["tv", "retro", "television"]),
        Variant("destello-de-lente-anamorfico", "Destello de lente anamórfico", "Anamorphic lens flare", thumb=1.2,
                photo="woman", params={"color": "#7fb0ff", "center_x": 0.3, "center_y": 0.42, "amount": 1.0},
                tags=["lente", "lens", "estrella", "star"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Flashes on the picture itself: camera flash bulbs, a punch-in explosion, a pulse, a shaking glow and a light hit
# from the side. MODE picks the look. Frequency = hits per second (2 = 120 BPM); Center X/Y = where the light comes
# from (or the centre of the zoom); Zoom = how far each hit punches in.
FLASH = Family(
    key="luz2_flash", category="luz",
    params=[INTENSITY, SPEED, color("#ffffff"), Param("frequency", "Frequency", 0.25, 6.0, 2.0), *centre(0.0, 0.1),
            Param("zoom", "Zoom", 0.0, 0.3, 0.0)],
    photo="woman", tags=["flash", "destello", "exposicion", "exposure", "brillo", "glow", "ritmo", "beat"],
    defines={"MODE": "0"},
    body=r"""
// Overexposure that leaves the picture untouched at f = 0 and lifts it towards white without clipping flat.
vec3 expose(vec3 c, float f) { f = max(f, 0.0); return screen(c, sat3(c * 0.85 * f + 0.12 * f)); }
void main() {
    float t = u_time * speed;
    float per = 1.0 / max(frequency, 0.01);
    vec2 uv = v_texCoord;
    vec2 cc = vec2(center_x, center_y);
    vec4 src = S(uv);
    vec2 p = toP(uv);
    vec3 col;
#if MODE == 0
    // Flash bulbs: a burst on some beats (random), each a quick double pop, light coming from Center X/Y.
    float slot = floor(t / per);
    float on = step(0.35, hash11(slot + 3.0));
    float ph = fract(t / per) * per;
    float f = on * (exp(-ph / 0.05) + 0.6 * exp(-max(ph - 0.09, 0.0) / 0.04) * step(0.09, ph)) * intensity;
    vec4 a = Sm(camUv(uv, cc, 1.0 + zoom * f, 0.0, vec2(0.0)));
    float side = exp(-length(p - toP(cc)) * 1.6);
    col = expose(a.rgb, f * (0.6 + side));
    col = addLight(col, color * (0.25 * f + side * 0.35 * f), 1.0);
    col = mix(col, vec3(1.0), sat(f * 0.35));
#elif MODE == 1
    // Explosion flash: a punch-in about Center X/Y with a zoom blur and a flash on every hit, settling back.
    float hit = exp(-phase(t, per) / 0.12);
    vec2 cu = camUv(uv, cc, 1.0 + zoom * hit * intensity, 0.0, vec2(0.0));
    vec4 s = vec4(0.0);
    for (int i = 0; i < 12; ++i) s += Sm(cc + (cu - cc) * (1.0 - 0.09 * hit * intensity * float(i) / 11.0));
    s /= 12.0;
    col = expose(s.rgb, hit * intensity);
    col = addLight(col, color * hit * 0.35, intensity);
    col += vec3(0.04, 0.0, 0.06) * hit;
#elif MODE == 2
    // Pulsing flash: the exposure breathes to white on every beat, with a small punch-in about Center X/Y.
    float b = beat(t, per, 0.16);
    vec4 a = Sm(camUv(uv, cc, 1.0 + zoom * b, 0.0, vec2(0.0)));
    float f = (0.1 + 1.4 * b) * intensity;
    col = expose(a.rgb, f);
    col = mix(col, color, sat(b * 0.2 * intensity));
    col = contrastColor(col, 1.0 + 0.15 * b);
#elif MODE == 3
    // Shaking glow: the picture jitters (zoomed in by Zoom about Center X/Y) and blooms, flickering with the shake.
    vec2 j = shake2(t, 14.0) * 0.008 * intensity;
    float k = 1.0 + max(zoom, 0.02);
    vec2 su = camUv(uv, cc, k, 0.0, j);
    vec4 a = Sm(su);
    vec3 g = brightGlow(su, 0.06, 0.45);
    float fl = 0.6 + 0.4 * beat(t, per, 0.08);
    col = expose(a.rgb, 0.5 * fl * intensity);
    col = addLight(col, (g * 2.5 + color * 0.15) * fl, intensity);
    // A slight chromatic fringe while it shakes.
    col.r = mix(col.r, expose(Sm(camUv(uv, cc, k, 0.0, j * 2.5)).rgb, 0.5 * fl * intensity).r, 0.5);
#else
    // Light hit: a beam slams in from Center X/Y on the beat, overexposing that side, with a sideways jolt.
    float ph = phase(t, per);
    float hit = exp(-ph / 0.15);
    vec2 j = vec2(0.012 * hit * intensity * sin(ph * 60.0), 0.0);
    vec4 a = Sm(camUv(uv, vec2(0.5), 1.0 + max(zoom, 0.02), 0.0, j));
    vec2 o = toP(cc);
    float beam = exp(-length((p - o) * vec2(0.55, 1.4)) * (2.0 - 0.8 * hit));
    float streak = exp(-abs(p.y - o.y) / 0.06) * exp(-abs(p.x - o.x) * 1.5);
    float f = beam * (0.3 + 0.7 * hit) * intensity;
    col = expose(a.rgb, f);
    col = addLight(col, color * (beam * (0.6 + 1.0 * hit) + streak * 0.9 * hit), intensity);
#endif
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("lampara-de-flash", "Lámpara de flash", "Flash lamp", thumb=2.02,
                tags=["camara", "camera", "fotos", "photos", "paparazzi"]),
        Variant("explosion-flash", "Explosión-flash", "Flash explosion", thumb=1.03, defines={"MODE": "1"},
                params={"frequency": 1.0, "center_x": 0.5, "center_y": 0.5, "zoom": 0.12},
                tags=["explosion", "zoom", "golpe", "punch"]),
        Variant("destello-palpitante", "Destello palpitante", "Pulsing flash", thumb=1.0, defines={"MODE": "2"},
                params={"center_x": 0.5, "center_y": 0.5, "zoom": 0.02},
                photo="fx-woman-05", tags=["pulso", "pulse", "palpitar"]),
        Variant("resplandor-vibrar", "Resplandor vibrar", "Shaking glow", thumb=1.0, defines={"MODE": "3"},
                params={"frequency": 4.0, "center_x": 0.5, "center_y": 0.5, "zoom": 0.04},
                tags=["vibrar", "shake", "vibracion", "vibration"]),
        Variant("haz-de-choque", "Haz de choque", "Shock beam", thumb=1.03, defines={"MODE": "4"},
                photo="fashion", params={"color": "#c58cff", "center_x": -0.05, "center_y": 0.4, "zoom": 0.05},
                tags=["haz", "beam", "choque", "shock", "violeta", "violet"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# A burst of golden rays fanning out from Center X/Y (up by default; Angle turns it), breathing and turning slowly,
# with drifting specks of light.
RAYS = Family(
    key="luz2_rays", category="luz",
    params=[INTENSITY, SPEED, color("#ffc04d"), Param("spread", "Spread", 0.4, 2.0, 1.0), *centre(0.5, 1.02),
            Param("angle", "Angle", -180.0, 180.0, 0.0), Param("size", "Size", 0.3, 2.0, 1.0),
            Param("density", "Density", 0.3, 2.0, 1.0)],
    photo="dark", tags=["rayos", "rays", "estallido", "burst", "dorado", "golden", "luz", "light"],
    body=r"""
float specks(vec2 p, float t, float scale, float seed) {
    vec2 q = p * scale + vec2(0.0, t * 0.4);
    vec2 cell = floor(q), f = fract(q) - 0.5;
    float h = hash12(cell + seed);
    if (h > 0.25 * density) return 0.0;
    vec2 o = (hash22(cell + seed * 2.3) - 0.5) * 0.6;
    float r = 0.08 + 0.1 * hash12(cell + seed + 4.0);
    return smoothstep(r, r * 0.3, length(f - o)) * (0.5 + 0.5 * sin(t * 3.0 + h * 40.0));
}
void main() {
    float t = u_time * speed;
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    vec2 o = toP(vec2(center_x, center_y));
    vec2 v = rot(radians(angle)) * (p - o);        // in burst space the rays go up
    float d = length(v);
    float a = atan(v.x, -v.y);                       // 0 straight up
    float fan = smoothstep(1.45 * spread, 0.9 * spread, abs(a));
    float r1 = pow(vnoise(vec2(a * 10.0 * density + t * 0.15, t * 0.4)), 2.0);
    float r2 = pow(vnoise(vec2(a * 26.0 * density - t * 0.1, 3.0 + t * 0.3)), 3.0);
    float grow = 0.75 + 0.25 * sin(t * 1.6);
    float reach = exp(-d / (0.55 * grow * size));
    float rays = (r1 * 1.2 + r2 * 0.8) * reach * fan;
    float core = exp(-d / (0.09 * size)) * 1.3 + exp(-length(v * vec2(0.6, 2.0)) / (0.25 * size)) * 0.6;
    float sp = (specks(p, t, 7.0, 1.0) * 0.6 + specks(p, t * 1.3, 4.0, 5.0)) * exp(-d / (0.6 * size)) * fan;
    vec3 hot = mix(color, vec3(1.0, 0.97, 0.9), 0.55);
    vec3 l = color * rays * 1.1 + hot * core + hot * sp * 0.6;
    fragColor = vec4(addLight(src.rgb, l, intensity), src.a);
}
""",
    variants=[
        Variant("estallido-de-rayos", "Estallido de rayos", "Ray burst", thumb=1.0,
                tags=["presencia", "presence", "divino", "divine"]),
    ],
)

FAMILIES = [BOKEH, BEAM, STREAKS, LEAK, SUN, ANAMORPHIC, FLASH, RAYS]
