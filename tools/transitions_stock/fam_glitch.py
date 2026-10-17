"""Glitch and digital transitions."""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)

GLITCH_PUNCH = Family(
    key="glitch_punch", app_category="glitch", category="glitch", params=[INTENSITY], duration=0.8,
    tags=["glitch", "golpe", "punch", "rgb", "digital", "error"],
    defines={"ROWS": 16, "BLOCKS": 9, "BLOCKY": 0.35, "FLASH": "#ffffff", "FLASHK": 0.0, "MONO": "#000000",
             "MONOK": 0.0, "FRINGE_R": "#ff0000", "FRINGE_B": "#0000ff", "SPLIT": 1.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = peak(p, 0.2) * intensity;
    float q = floor(p * 30.0);
    float row = floor(uv.y * ROWS + hash11(q) * 3.0);
    vec2 off = vec2(0.0);
    if (hash12(vec2(row, q)) < k * 0.7) off.x += (hash12(vec2(row, q + 7.0)) - 0.5) * 0.3 * k;
    vec2 cell = floor(uv * vec2(BLOCKS * aspect(), BLOCKS));
    if (hash12(cell + q * 1.37) < k * BLOCKY) off += (hash22(cell + q) - 0.5) * 0.14 * k;
    float side = step(0.5 + (hash12(vec2(row, q + 3.0)) - 0.5) * 0.5 * k, p);
    vec2 u = uv + off;
    vec2 s = vec2(0.035 * SPLIT * k, 0.0);
    vec4 cr = mix(A(u + s), B(u + s), side);
    vec4 cg = mix(A(u), B(u), side);
    vec4 cb = mix(A(u - s), B(u - s), side);
    vec3 col = cg.rgb + (cr.rgb - cg.rgb) * FRINGE_R + (cb.rgb - cg.rgb) * FRINGE_B;
    col += (hash12(vec2(floor(uv.y * 220.0), q)) - 0.5) * 0.18 * k;
    col = mix(col, MONO * (0.25 + 1.1 * luma(col)), MONOK * k);
    col = mix(col, FLASH, FLASHK * peak(p, 0.05));
    fragColor = vec4(clamp(col, 0.0, 1.0), max(cg.a, max(cr.a, cb.a)));
}
""",
    variants=[
        Variant("glitch-golpe-rgb", "Glitch con golpe RGB", "RGB glitch punch", thumb=0.46),
        Variant("glitch-bloques", "Glitch de bloques", "Block glitch", {"ROWS": 6, "BLOCKS": 6, "BLOCKY": 0.95}, thumb=0.47),
        Variant("glitch-destello", "Glitch con destello", "Glitch flash", {"FLASHK": 0.85}, thumb=0.45),
        Variant("glitch-neon", "Glitch neón", "Neon glitch",
                {"FRINGE_R": "#ff2bd6", "FRINGE_B": "#00e5ff", "SPLIT": 1.6}, thumb=0.46),
        Variant("glitch-fosforo", "Glitch de monitor verde", "Green monitor glitch",
                {"MONO": "#35ff6a", "MONOK": 0.9, "ROWS": 30}, thumb=0.46),
    ],
)

DATAMOSH = Family(
    key="datamosh", app_category="glitch", category="glitch", params=[INTENSITY], duration=1.2,
    tags=["datamosh", "glitch", "pixeles", "arrastre", "smear"],
    defines={"DIR": (1.0, 0.0), "CELL": 18.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = bump(p) * intensity;
    float q = floor(p * 20.0);
    // Blocks drag the picture under them along DIR by an amount that grows to the cut, as a
    // broken stream reuses old motion: big cells, hard edges, a few untouched.
    vec2 cell = floor(uv * vec2(CELL * aspect(), CELL) / (1.0 + 2.0 * hash12(floor(uv * 4.0) + q)));
    float h = hash12(cell + 3.1);
    float drag = (0.25 + 0.75 * h) * k * 0.35 * step(0.18, h);
    vec2 u = uv - DIR * drag * (0.6 + 0.4 * sin(q + h * 6.0));
    float cut = linstep(0.35, 0.65, p + (h - 0.5) * 0.3);
    vec4 c = mix(A(u), B(u), step(0.5, cut));
    c.rgb += (vec3(hash12(cell + q), hash12(cell + q + 1.0), hash12(cell + q + 2.0)) - 0.5) * 0.12 * k * step(0.8, h);
    fragColor = c;
}
""",
    variants=[
        Variant("datamosh-horizontal", "Datamosh horizontal", "Horizontal datamosh"),
        Variant("datamosh-vertical", "Datamosh vertical", "Vertical datamosh", {"DIR": (0.0, 1.0), "CELL": 14.0}),
    ],
)

SLICES = Family(
    key="slice_tear", app_category="glitch", category="glitch", params=[INTENSITY], duration=0.9,
    tags=["cortes", "franjas", "slice", "glitch", "rasgado"],
    defines={"BANDS": 26.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = bump(p) * intensity;
    float band = floor(uv.y * BANDS);
    float h = hash11(band * 1.7 + 0.3);
    float dir = mod(band, 2.0) < 1.0 ? 1.0 : -1.0;
    // Each band slides out sideways at its own moment; the incoming picture slides in behind it.
    float t = sat((p - h * 0.35) / 0.65);
    float e = easeInOut(t);
    float shiftA = dir * e;
    float shiftB = dir * (e - 1.0);
    vec4 a = Ac(vec2(uv.x - shiftA, uv.y));
    vec4 b = Bc(vec2(uv.x - shiftB, uv.y));
    vec4 c = over(a, b);
    c.rgb += vec3(0.25, 0.0, 0.35) * k * step(0.93, hash12(vec2(band, floor(p * 24.0))));
    fragColor = c;
}
""",
    variants=[
        Variant("franjas-finas", "Franjas que se deslizan", "Sliding slices"),
        Variant("franjas-gruesas", "Franjas gruesas", "Thick slices", {"BANDS": 8.0}),
    ],
)

CHROMA_SWEEP = Family(
    key="chroma_sweep", app_category="glitch", category="glitch", params=[INTENSITY], duration=1.0,
    tags=["cromatico", "rgb", "barrido", "chromatic", "aberracion"],
    defines={"DIR": (1.0, 0.0)},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    // Red, green and blue wipe across one after another, each with a soft edge and a push.
    float along = dot(uv - 0.5, normalize(DIR)) + 0.5;
    vec3 col = vec3(0.0);
    float alpha = 0.0;
    for (int i = 0; i < 3; ++i) {
        float lag = float(i) * 0.12 * intensity;
        float edge = mix(-0.25, 1.25, sat((p - lag) / (1.0 - 0.24 * intensity)));
        float m = smoothstep(edge - 0.12, edge + 0.12, along);
        vec2 push = DIR * 0.05 * bump(p) * intensity;
        vec4 a = A(uv - push), b = B(uv + push);
        vec4 c = mix(b, a, m);
        col[i] = c[i];
        alpha = max(alpha, c.a);
    }
    fragColor = vec4(col, alpha);
}
""",
    variants=[
        Variant("cromatico-lateral", "Barrido cromático", "Chromatic sweep"),
        Variant("cromatico-vertical", "Barrido cromático vertical", "Vertical chromatic sweep", {"DIR": (0.0, 1.0)}),
    ],
)

STATIC = Family(
    key="static_noise", app_category="glitch", category="glitch", params=[INTENSITY], duration=0.9,
    tags=["estatica", "ruido", "tv", "static", "noise", "señal"],
    defines={"COLORED": 0.0, "LINES": 1.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = peak(p, 0.18) * intensity;
    float q = floor(p * 40.0);
    vec2 px = floor(uv * u_resolution / 2.0);
    float n = hash12(px + q * 13.7);
    vec3 noise = mix(vec3(n), vec3(n, hash12(px + q * 7.1 + 2.0), hash12(px + q * 3.3 + 5.0)), COLORED);
    float roll = fract(uv.y * 3.0 - p * 6.0);
    noise *= 0.75 + 0.25 * smoothstep(0.0, 0.1, roll) * LINES;
    vec2 jit = vec2((hash12(vec2(floor(uv.y * 60.0), q)) - 0.5) * 0.04 * k, 0.0);
    vec4 c = p < 0.5 ? A(uv + jit) : B(uv + jit);
    c.rgb = mix(c.rgb, noise, sat(k * 1.15));
    fragColor = vec4(c.rgb, max(c.a, k));
}
""",
    variants=[
        Variant("estatica-tv", "Estática de TV", "TV static"),
        Variant("estatica-color", "Estática de color", "Colour static", {"COLORED": 1.0}),
    ],
)

PIXEL_SORT = Family(
    key="pixel_sort", app_category="glitch", category="glitch", params=[INTENSITY], duration=1.3,
    tags=["pixel sort", "chorreado", "glitch", "estiramiento", "melt"],
    defines={"DIR": (0.0, 1.0)},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 d = normalize(DIR);
    vec2 perp = vec2(-d.y, d.x);
    // Bright columns smear along DIR the way a sorted image streaks: each column starts where its
    // picture is brightest and runs out with progress.
    float col = floor(dot(uv, perp) * u_resolution.x / 3.0);
    float h = hash11(col * 0.37 + 1.0);
    float along = dot(uv, d);
    float k = bump(p) * intensity;
    float len = k * (0.25 + 0.75 * h) * 0.9;
    float t = fract(along * 0.0 + h);
    vec2 src = uv - d * len * smoothstep(0.0, 1.0, along + h * 0.4 - 0.2);
    vec4 a = A(src), b = B(src);
    float thr = luma(mix(a.rgb, b.rgb, 0.5));
    vec2 s2 = mix(uv, src, step(0.45 - 0.25 * h, thr));
    float cut = smoothstep(0.42, 0.58, p);
    fragColor = mix(A(s2), B(s2), cut);
}
""",
    variants=[
        Variant("pixeles-chorreados", "Píxeles que chorrean", "Pixel drip"),
        Variant("pixeles-arrastrados", "Píxeles arrastrados", "Pixel drag", {"DIR": (1.0, 0.0)}),
    ],
)

TRACKING = Family(
    key="vhs_tracking", app_category="glitch", category="glitch", params=[INTENSITY], duration=1.0,
    tags=["vhs", "tracking", "cinta", "retro", "rebobinar", "rewind"],
    defines={"DIRY": -1.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = bump(p) * intensity;
    // The picture rolls vertically as a tape that loses sync, with a tracking band and wobble.
    float roll = DIRY * easeInOut(p);
    vec2 u = vec2(uv.x, uv.y + roll);
    float frameIdx = floor(u.y);
    u.y = fract(u.y);
    float wob = sin(uv.y * 40.0 + p * 30.0) * 0.006 * k + (hash12(vec2(floor(uv.y * 90.0), floor(p * 25.0))) - 0.5) * 0.02 * k;
    u.x += wob;
    bool useB = (DIRY < 0.0) ? (frameIdx < 0.0) : (frameIdx >= 1.0);
    vec4 c = useB ? B(u) : A(u);
    float band = smoothstep(0.0, 0.03, u.y) * smoothstep(0.0, 0.03, 1.0 - u.y);
    c.rgb *= mix(1.0, band, sat(k * 2.0));
    float tb = exp(-pow((fract(uv.y - p * 2.0) - 0.5) / 0.04, 2.0)) * k;
    c.rgb = mix(c.rgb, vec3(hash12(floor(uv * u_resolution / 2.0) + floor(p * 40.0))), tb * 0.8);
    c.r = mix(c.r, (useB ? B(u + vec2(0.006 * k, 0.0)) : A(u + vec2(0.006 * k, 0.0))).r, 0.7);
    fragColor = c;
}
""",
    variants=[
        Variant("vhs-rebobinar", "VHS rebobinar", "VHS rewind", thumb=0.4),
        Variant("vhs-avanzar", "VHS avance rápido", "VHS fast forward", {"DIRY": 1.0}, thumb=0.4),
    ],
)

FAMILIES = [GLITCH_PUNCH, DATAMOSH, SLICES, CHROMA_SWEEP, STATIC, PIXEL_SORT, TRACKING]
