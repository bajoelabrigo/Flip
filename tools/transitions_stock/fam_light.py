"""Light, flash and film transitions."""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)

FLASH = Family(
    key="light_flash", app_category="cinematic", category="luz", params=[INTENSITY], duration=0.8,
    tags=["destello", "flash", "luz", "brillo", "blanco"],
    defines={"COL": "#ffffff", "PRISM": 0.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = peak(p, 0.22) * intensity;
    // Overexpose and bloom towards the flash colour, swap pictures at the brightest moment.
    vec4 base = p < 0.5 ? A(uv) : B(uv);
    vec4 soft = p < 0.5 ? discBlurA(uv, 0.04 * k) : discBlurB(uv, 0.04 * k);
    vec3 c = mix(base.rgb, soft.rgb, sat(k));
    c = c * (1.0 + 2.5 * k) + COL * k * 0.6;
    if (PRISM > 0.5) {
        vec2 d = (uv - 0.5) * 0.03 * k;
        vec3 split = vec3((p < 0.5 ? A(uv + d) : B(uv + d)).r, c.g / (1.0 + 2.5 * k), (p < 0.5 ? A(uv - d) : B(uv - d)).b);
        c = mix(c, split * (1.0 + 2.5 * k) + vec3(0.2, 0.1, 0.3) * k, 0.6);
    }
    c = mix(c, COL, smoothstep(0.55, 1.0, k));
    fragColor = vec4(min(c, vec3(1.0)), max(base.a, sat(k)));
}
""",
    variants=[
        Variant("destello-blanco", "Destello blanco", "White flash", thumb=0.42),
        Variant("destello-dorado", "Destello dorado", "Golden flash", {"COL": "#ffc56b"}, thumb=0.42),
        Variant("destello-azul", "Destello frío", "Cool flash", {"COL": "#8fd3ff"}, thumb=0.42),
        Variant("destello-rosa", "Destello rosa", "Pink flash", {"COL": "#ff9fd0"}, thumb=0.42),
        Variant("destello-prisma", "Destello de prisma", "Prism flash", {"PRISM": 1.0, "COL": "#fff0ff"}, thumb=0.4),
    ],
)

LEAK = Family(
    key="light_leak", app_category="cinematic", category="luz", params=[INTENSITY], duration=1.4,
    tags=["fuga de luz", "light leak", "pelicula", "calido", "vintage"],
    defines={"C1": "#ff7a18", "C2": "#ffd36b", "C3": "#ff2f5c"},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    // Warm blobs of light drift across the frame; the cut hides under the brightest one.
    float sweep = mix(-1.4, 1.4, p);
    float n = fbm(P * 1.6 + vec2(p * 1.5, 0.0));
    float blob = exp(-pow((P.x * 0.8 - P.y * 0.5 - sweep) / 0.55, 2.0));
    float glow = blob * (0.55 + 0.9 * n);
    vec3 lc = mix(C1, C2, sat(n * 1.4 - 0.2));
    lc = mix(lc, C3, sat((P.y + 0.5) * 0.8 - n * 0.4));
    float k = glow * intensity * (0.4 + 0.6 * bump(p));
    float m = smoothstep(0.4, 0.6, p);
    vec4 base = mix(A(uv), B(uv), m);
    vec3 c = 1.0 - (1.0 - base.rgb) * (1.0 - lc * k * 1.4);
    c += lc * pow(k, 3.0) * 0.6;
    fragColor = vec4(min(c, vec3(1.0)), base.a);
}
""",
    variants=[
        Variant("fuga-calida", "Fuga de luz cálida", "Warm light leak"),
        Variant("fuga-rosa", "Fuga de luz rosa", "Pink light leak", {"C1": "#ff4f9a", "C2": "#ffb3d9", "C3": "#9a4dff"}),
        Variant("fuga-arcoiris", "Fuga de luz arcoíris", "Rainbow light leak", {"C1": "#ff3b3b", "C2": "#ffe14d", "C3": "#3bb8ff"}),
        Variant("fuga-dorada", "Fuga de luz dorada", "Golden light leak", {"C1": "#ffb000", "C2": "#fff1b8", "C3": "#ff7a00"}),
        Variant("fuga-turquesa", "Fuga de luz turquesa", "Teal light leak", {"C1": "#18e0c8", "C2": "#c8fff2", "C3": "#2b6bff"}),
    ],
)

BURN = Family(
    key="film_burn", app_category="cinematic", category="luz", params=[INTENSITY], duration=1.4,
    tags=["quemado", "pelicula", "fuego", "burn", "celuloide"],
    defines={"SPOTS": 0.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float n = fbm(P * 4.0 + 7.0);
    float field;
    if (SPOTS > 0.5) {
        float best = 9.0;
        for (int i = 0; i < 5; ++i) {
            vec2 c = (hash22(vec2(float(i), 4.0)) - 0.5) * vec2(aspect(), 1.0) * 0.8;
            best = min(best, length(P - c) - hash11(float(i) + 2.0) * 0.15);
        }
        field = best / 0.9;
    } else {
        field = length(P) / 1.02;
    }
    field += (n - 0.5) * 0.35;
    float t = mix(-0.25, 1.15, easeInOut(p));
    float d = field - t;
    // Behind the front: the incoming picture. On the front: white hot, then orange, then charred.
    vec4 col = A(uv);
    float hot = 1.0 - smoothstep(0.0, 0.05, abs(d));
    float orange = 1.0 - smoothstep(0.0, 0.12, abs(d - 0.04));
    float char_ = smoothstep(0.03, 0.1, d) * (1.0 - smoothstep(0.1, 0.2, d));
    col.rgb *= 1.0 - 0.85 * char_;
    col.rgb = mix(col.rgb, vec3(1.0, 0.45, 0.08), orange * 0.9 * intensity);
    col.rgb = mix(col.rgb, vec3(1.0, 0.92, 0.7), hot * intensity);
    vec4 b = B(uv);
    b.rgb += vec3(1.0, 0.5, 0.1) * (1.0 - smoothstep(-0.12, 0.0, d)) * smoothstep(-0.3, -0.05, d) * 0.4 * intensity;
    fragColor = d < 0.0 ? over(vec4(vec3(1.0, 0.8, 0.5), hot * intensity), b) : col;
}
""",
    variants=[
        Variant("pelicula-quemada", "Película que se quema", "Film burn"),
        Variant("pelicula-quemada-puntos", "Quemaduras de película", "Film burn spots", {"SPOTS": 1.0}),
    ],
)

STREAK = Family(
    key="lens_streak", app_category="cinematic", category="luz", params=[INTENSITY], duration=1.0,
    tags=["destello de lente", "anamorfico", "flare", "luz", "cine"],
    defines={"COL": "#6fb7ff"},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float x0 = mix(-0.9, 0.9, p) * aspect();
    vec2 src = vec2(x0, -0.1);
    float k = bump(p) * intensity;
    // A long horizontal streak, a hot core and a few ghosts mirrored through the centre.
    float streak = exp(-abs(P.y - src.y) * 90.0) * exp(-abs(P.x - src.x) * 0.9);
    float core = exp(-length(P - src) * 9.0);
    float ghosts = 0.0;
    for (int i = 1; i < 4; ++i) {
        vec2 g = -src * (0.35 * float(i));
        ghosts += (1.0 - smoothstep(0.02, 0.05 + 0.02 * float(i), length(P - g))) * 0.25 / float(i);
    }
    float m = smoothstep(0.42, 0.58, p);
    vec4 base = mix(A(uv), B(uv), m);
    vec3 c = base.rgb + COL * (streak * 1.6 + ghosts) * k + vec3(1.0) * core * k * 1.2;
    c = mix(c, vec3(1.0), peak(p, 0.06) * 0.6 * intensity);
    fragColor = vec4(min(c, vec3(1.0)), base.a);
}
""",
    variants=[
        Variant("destello-lente-azul", "Destello de lente azul", "Blue lens streak"),
        Variant("destello-lente-dorado", "Destello de lente dorado", "Golden lens streak", {"COL": "#ffb347"}),
    ],
)

FILM_ROLL = Family(
    key="film_roll", app_category="cinematic", category="luz", duration=0.9,
    params=[Param("blur", "Motion Blur", 0.0, 1.5, 1.0)],
    tags=["rollo", "pelicula", "cinta", "fotograma", "proyector", "film"],
    defines={"DIRY": 1.0},
    body=r"""
vec4 frameAt(vec2 uv, float y) {
    // A strip of film: the outgoing frame, a black bar, the incoming frame; sprockets down both sides.
    float gap = 0.12;
    vec4 c = vec4(0.04, 0.04, 0.045, 1.0);
    if (y >= 0.0 && y <= 1.0) c = A(vec2(uv.x, y));
    float l2 = DIRY > 0.0 ? y - 1.0 - gap : y + 1.0 + gap;
    if (l2 >= 0.0 && l2 <= 1.0) c = B(vec2(uv.x, l2));
    float side = step(uv.x, 0.045) + step(0.955, uv.x);
    float holes = step(abs(fract(y * 7.0) - 0.5), 0.22) * step(abs(fract(uv.x / 0.045) - 0.5), 0.3);
    vec3 rail = mix(vec3(0.04), vec3(0.85), holes);
    c.rgb = mix(c.rgb, rail, side * sat(bump(u_progress) * 3.0));
    return c;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float e = easeInOut(p) * 1.12;
    float y = uv.y + DIRY * e;
    float sp = blur * 0.12 * bump(p);
    vec4 col = vec4(0.0);
    for (int i = 0; i < 12; ++i) col += frameAt(uv, y + sp * (float(i) / 11.0 - 0.5));
    col /= 12.0;
    col.rgb *= 1.0 - 0.15 * bump(p) * (hash11(floor(p * 24.0)) );
    fragColor = col;
}
""",
    variants=[
        Variant("rollo-pelicula", "Rollo de película", "Film roll", thumb=0.45),
        Variant("rollo-pelicula-abajo", "Rollo de película hacia abajo", "Film roll down", {"DIRY": -1.0}, thumb=0.45),
    ],
)

PROJECTOR = Family(
    key="projector", app_category="cinematic", category="luz", params=[INTENSITY], duration=1.2,
    tags=["proyector", "parpadeo", "cine antiguo", "vintage", "flicker", "retro"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float f = floor(p * 18.0);
    float k = bump(p) * intensity;
    // The gate jumps and the lamp flickers; whole frames of either picture alternate before settling.
    vec2 jump = vec2(0.0, (hash11(f) - 0.5) * 0.05 * k);
    float pick = step(hash11(f + 3.0), smoothstep(0.15, 0.85, p));
    vec2 u = uv + jump;
    vec4 c = mix(A(u), B(u), pick);
    float l = luma(c.rgb);
    c.rgb = mix(c.rgb, vec3(l) * vec3(1.05, 0.95, 0.8), 0.6 * k);
    c.rgb *= 1.0 + (hash11(f + 7.0) - 0.5) * 0.8 * k;
    float scratch = step(0.997, hash12(vec2(floor(uv.x * 300.0), f))) * k;
    float dust = step(0.9985, hash12(floor(uv * u_resolution / 3.0) + f)) * k;
    c.rgb = mix(c.rgb, vec3(0.95), scratch * 0.7 + dust);
    vec2 v = uv * 2.0 - 1.0;
    c.rgb *= 1.0 - 0.45 * k * dot(v, v) * 0.5;
    fragColor = c;
}
""",
    variants=[Variant("proyector-antiguo", "Proyector antiguo", "Old projector")],
)

BOKEH = Family(
    key="bokeh_blur", app_category="cinematic", category="luz", params=[INTENSITY], duration=1.2,
    tags=["desenfoque", "bokeh", "suave", "blur", "foco"],
    defines={"SPARK": 1.0, "TINT": "#ffe2b0"},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = bump(p) * intensity;
    // Rack focus out of the outgoing picture and into the incoming one, with discs of light.
    vec4 a = discBlurA(uv, 0.06 * k);
    vec4 b = discBlurB(uv, 0.06 * k);
    vec4 c = mix(a, b, smoothstep(0.3, 0.7, p));
    vec2 n = vec2(aspect(), 1.0) * 9.0;
    vec2 g = uv * n;
    vec2 id = floor(g);
    vec2 o = hash22(id) - 0.5;
    float r = 0.18 + 0.25 * hash12(id + 2.0);
    float disc = 1.0 - smoothstep(r - 0.04, r, length(fract(g) - 0.5 - o * 0.3));
    float on = step(0.72, hash12(id + 5.0));
    c.rgb += TINT * disc * on * SPARK * k * 0.45;
    fragColor = vec4(min(c.rgb, vec3(1.0)), c.a);
}
""",
    variants=[
        Variant("desenfoque-bokeh", "Desenfoque con bokeh", "Bokeh blur"),
        Variant("desenfoque-suave", "Desenfoque suave", "Soft blur", {"SPARK": 0.0}),
    ],
)

RAYS = Family(
    key="sun_rays", app_category="cinematic", category="luz", params=[INTENSITY], duration=1.2,
    tags=["rayos", "sol", "luz", "god rays", "celestial"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 src = vec2(0.5, 0.35);
    float k = bump(p) * intensity;
    // Light shafts from a bright point: march towards it and gather the brightness of each picture.
    float m = smoothstep(0.4, 0.6, p);
    vec3 acc = vec3(0.0);
    for (int i = 0; i < 24; ++i) {
        vec2 q = mix(uv, src, float(i) / 24.0 * 0.8);
        vec3 s = mix(A(q).rgb, B(q).rgb, m);
        acc += max(s - 0.45, 0.0) * (1.0 - float(i) / 24.0);
    }
    acc /= 12.0;
    vec4 base = mix(A(uv), B(uv), m);
    float a = atan(uv.y - src.y, (uv.x - src.x) * aspect());
    float shafts = 0.6 + 0.4 * sin(a * 18.0 + fbm(vec2(a * 3.0, 1.0)) * 4.0);
    vec3 c = base.rgb + (acc * 2.0 + vec3(1.0, 0.92, 0.75) * 0.25 * shafts * exp(-length(toP(uv) - toP(src)) * 2.0)) * k;
    c = mix(c, vec3(1.0, 0.97, 0.9), peak(p, 0.07) * 0.65 * intensity);
    fragColor = vec4(min(c, vec3(1.0)), base.a);
}
""",
    variants=[Variant("rayos-de-sol", "Rayos de sol", "Sun rays")],
)

NEGATIVE = Family(
    key="negative_flash", app_category="glitch", category="luz", params=[INTENSITY], duration=0.6,
    tags=["negativo", "invertir", "flash", "golpe", "invert"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = peak(p, 0.16) * intensity;
    vec2 c = vec2(0.5);
    vec4 base = p < 0.5 ? A(c + (uv - c) * (1.0 - 0.06 * k)) : B(c + (uv - c) * (1.0 - 0.06 * k));
    vec3 inv = 1.0 - base.rgb;
    float f = floor(p * 24.0);
    float on = step(0.3, k) * (mod(f, 2.0) < 1.0 ? 1.0 : 0.6);
    fragColor = vec4(mix(base.rgb, inv, on * sat(k * 1.3)), base.a);
}
""",
    variants=[Variant("negativo", "Flash en negativo", "Negative flash")],
)

POP = Family(
    key="duotone_pop", app_category="cinematic", category="luz", params=[INTENSITY], duration=0.8,
    tags=["duotono", "pop", "color", "flash", "duotone"],
    defines={"DARK": "#2b00ff", "LIGHT": "#ff3db4"},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = peak(p, 0.2) * intensity;
    vec4 base = p < 0.5 ? A(uv) : B(uv);
    float l = smoothstep(0.1, 0.8, luma(base.rgb));
    vec3 duo = mix(DARK, LIGHT, l);
    float step2 = floor(p * 16.0);
    vec2 sh = vec2((hash11(step2) - 0.5) * 0.02 * k, 0.0);
    vec4 b2 = p < 0.5 ? A(uv + sh) : B(uv + sh);
    duo = mix(duo, mix(LIGHT, DARK, smoothstep(0.1, 0.8, luma(b2.rgb))), 0.25 * k);
    fragColor = vec4(mix(base.rgb, duo, sat(k * 1.4)), base.a);
}
""",
    variants=[
        Variant("duotono-rosa", "Golpe duotono rosa", "Pink duotone pop"),
        Variant("duotono-limon", "Golpe duotono lima", "Lime duotone pop", {"DARK": "#0b3d2e", "LIGHT": "#d8ff3d"}),
    ],
)

OLD_FILM = Family(
    key="old_film", app_category="cinematic", category="luz", params=[INTENSITY], duration=1.4,
    tags=["pelicula antigua", "sepia", "rayas", "vintage", "retro", "fundido"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = bump(p) * intensity;
    float f = floor(p * 24.0);
    vec4 c = mix(A(uv), B(uv), smoothstep(0.25, 0.75, p));
    vec3 sep = vec3(luma(c.rgb)) * vec3(1.08, 0.92, 0.72);
    c.rgb = mix(c.rgb, sep, k * 0.85);
    float lines = 0.0;
    for (int i = 0; i < 3; ++i) {
        float x = hash11(f * 3.0 + float(i));
        lines += (1.0 - smoothstep(0.0, 0.0025, abs(uv.x - x))) * step(0.4, hash11(f + float(i) * 7.0));
    }
    float blot = smoothstep(0.75, 0.8, fbm(uv * 12.0 + f * 3.1)) * 0.6;
    c.rgb = mix(c.rgb, vec3(0.1, 0.08, 0.05), (lines * 0.6 + blot * 0.5) * k);
    c.rgb *= 1.0 + (hash11(f + 1.0) - 0.5) * 0.25 * k;
    fragColor = c;
}
""",
    variants=[Variant("pelicula-antigua", "Película antigua", "Old film dissolve")],
)

FAMILIES = [FLASH, LEAK, BURN, STREAK, FILM_ROLL, PROJECTOR, BOKEH, RAYS, NEGATIVE, POP, OLD_FILM]
