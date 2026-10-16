"""Fun transitions: lightning, hearts, stars, confetti, comic bursts, snow, sparkles."""

from kit import Family, Param, Variant

LIGHTNING = Family(
    key="lightning", app_category="cinematic", category="divertidas", duration=0.9,
    params=[Param("intensity", "Intensity", 0.0, 1.5, 1.0)],
    tags=["rayo", "relampago", "tormenta", "lightning", "electrico"],
    defines={"BOLT": "#bfe3ff"},
    body=r"""
float bolt(vec2 P, float seed, float x0) {
    // A jagged bolt from the top edge down, with one branch; distance to it in toP units.
    float y = P.y;
    float t = y + 0.5;
    float x = x0 + (fbm(vec2(t * 6.0, seed)) - 0.5) * 0.35 + (vnoise(vec2(t * 40.0, seed)) - 0.5) * 0.04;
    float d = abs(P.x - x);
    float bt = sat((t - 0.35) / 0.5);
    float bx = x + bt * 0.35 * (hash11(seed) > 0.5 ? 1.0 : -1.0) + (fbm(vec2(t * 9.0, seed + 5.0)) - 0.5) * 0.12;
    d = min(d, t > 0.35 && t < 0.85 ? abs(P.x - bx) * 1.6 : 9.0);
    return d;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float f = floor(p * 20.0);
    float strike = step(0.25, p) * (1.0 - step(0.75, p));
    float flick = 0.6 + 0.4 * hash11(f);
    float d = bolt(P, 3.0 + floor(p * 4.0), (hash11(floor(p * 4.0)) - 0.5) * 0.6 * aspect());
    float core = 1.0 - smoothstep(0.0, 0.004, d);
    float glow = exp(-d * 30.0);
    vec4 base = p < 0.5 ? A(uv) : B(uv);
    base.rgb *= 1.0 - 0.5 * bump(p) * (1.0 - strike * flick * 0.4);
    float flash = peak(p, 0.05);
    vec3 c = base.rgb + BOLT * (glow * 0.9 + core * 2.0) * strike * flick * intensity;
    c = mix(c, vec3(1.0), flash * 0.8 * intensity);
    fragColor = vec4(min(c, vec3(1.0)), base.a);
}
""",
    variants=[
        Variant("rayo", "Rayo", "Lightning strike", thumb=0.3),
        Variant("rayo-morado", "Rayo morado", "Purple lightning", {"BOLT": "#c58bff"}, thumb=0.3),
    ],
)

HEARTS = Family(
    key="hearts", app_category="geometric", category="divertidas", duration=1.2,
    params=[Param("count", "Hearts", 3.0, 14.0, 9.0)],
    tags=["corazones", "amor", "san valentin", "hearts", "romantico"],
    defines={"FILL": "#ff3d7f", "COLORED": 0.0, "RAIN": 0.0},
    body=r"""
float hearts(vec2 P, float t) {
    float best = 9.0;
    for (int i = 0; i < 14; ++i) {
        if (float(i) >= count) break;
        float fi = float(i);
        vec2 c = (hash22(vec2(fi, 3.0)) - 0.5) * vec2(aspect(), 1.0) * 1.1;
        float delay = hash11(fi + 9.0) * 0.5;
        float k = sat((t - delay) / 0.5);
        float r = easeInOut(k) * 0.6;
        if (RAIN > 0.5) {
            c.y = mix(-0.9, 0.9, sat(t * 1.4 - delay)) + c.y * 0.3;
            r = 0.16 + 0.1 * hash11(fi + 2.0) + 0.7 * smoothstep(0.35, 0.95, t);
        }
        vec2 q = rot((hash11(fi) - 0.5) * 0.6) * (P - c);
        best = min(best, r > 0.0 ? sdHeart(q / r, 1.0) * r : 9.0);
    }
    return best;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float aa = 1.5 / u_resolution.y;
    vec4 col = A(uv);
    if (COLORED > 0.5) {
        float d1 = hearts(P, sat(p * 1.3));
        col = mix(col, vec4(FILL * (0.9 + 0.2 * (1.0 - uv.y)), 1.0), 1.0 - smoothstep(-aa, aa, d1));
        float d2 = hearts(P * 1.0 + 0.07, sat(p * 1.3 - 0.3));
        col = mix(col, B(uv), 1.0 - smoothstep(-aa, aa, d2));
    } else {
        float d = hearts(P, p);
        vec4 b = B(uv);
        col = mix(col, b, 1.0 - smoothstep(-aa, aa, d));
        col.rgb = mix(col.rgb, FILL, (1.0 - smoothstep(0.0, 0.012, abs(d + 0.006))) * (1.0 - step(0.98, p)));
    }
    fragColor = mix(col, B(uv), smoothstep(0.93, 1.0, p));
}
""",
    variants=[
        Variant("corazones", "Corazones", "Hearts"),
        Variant("corazones-rosa", "Corazones rosas", "Pink hearts", {"COLORED": 1.0}),
        Variant("lluvia-corazones", "Lluvia de corazones", "Falling hearts", {"RAIN": 1.0, "FILL": "#ff6fa8"}, params={"count": 12.0}),
    ],
)

STARS = Family(
    key="stars", app_category="geometric", category="divertidas", duration=1.2,
    params=[Param("count", "Stars", 3.0, 14.0, 10.0)],
    tags=["estrellas", "brillo", "stars", "magia", "fiesta"],
    defines={"FILL": "#ffd23d", "COLORED": 0.0},
    body=r"""
float stars(vec2 P, float t) {
    float best = 9.0;
    for (int i = 0; i < 14; ++i) {
        if (float(i) >= count) break;
        float fi = float(i);
        vec2 c = (hash22(vec2(fi, 8.0)) - 0.5) * vec2(aspect(), 1.0) * 1.1;
        float delay = hash11(fi + 4.0) * 0.5;
        float k = sat((t - delay) / 0.5);
        float r = easeInOut(k) * 1.0;
        vec2 q = rot(k * 2.0 + fi) * (P - c);
        best = min(best, r > 0.0 ? sdStar(q / r, 1.0, 5.0, 0.5) * r : 9.0);
    }
    return best;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float aa = 1.5 / u_resolution.y;
    vec4 col = A(uv);
    if (COLORED > 0.5) {
        float d1 = stars(P, sat(p * 1.3));
        vec3 gold = FILL * (0.85 + 0.3 * sat(-d1 * 8.0));
        col = mix(col, vec4(gold, 1.0), 1.0 - smoothstep(-aa, aa, d1));
        col = mix(col, B(uv), 1.0 - smoothstep(-aa, aa, stars(P + 0.05, sat(p * 1.3 - 0.3))));
    } else {
        float d = stars(P, p);
        col = mix(col, B(uv), 1.0 - smoothstep(-aa, aa, d));
        col.rgb = mix(col.rgb, FILL, (1.0 - smoothstep(0.0, 0.01, abs(d + 0.005))) * (1.0 - step(0.98, p)));
    }
    fragColor = mix(col, B(uv), smoothstep(0.93, 1.0, p));
}
""",
    variants=[
        Variant("estrellas", "Estrellas", "Stars"),
        Variant("estrellas-doradas", "Estrellas doradas", "Golden stars", {"COLORED": 1.0}),
    ],
)

CONFETTI = Family(
    key="confetti", app_category="liquid", category="divertidas", duration=1.4,
    params=[Param("density", "Density", 0.3, 1.0, 0.8)],
    tags=["confeti", "fiesta", "celebracion", "cumpleaños", "confetti"],
    body=r"""
vec3 pal(float h) {
    vec3 c = vec3(1.0, 0.25, 0.4);
    if (h > 0.2) c = vec3(1.0, 0.82, 0.15);
    if (h > 0.4) c = vec3(0.2, 0.8, 1.0);
    if (h > 0.6) c = vec3(0.45, 0.95, 0.4);
    if (h > 0.8) c = vec3(0.7, 0.4, 1.0);
    return c;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec4 col = mix(A(uv), B(uv), smoothstep(0.45, 0.55, p));
    // Three layers of tumbling paper bits falling through the frame, thickest at the cut.
    for (int layer = 0; layer < 3; ++layer) {
        float fl = float(layer);
        float sc = 9.0 + fl * 6.0;
        vec2 g = toP(uv) * sc;
        g.y -= (p * 2.4 - 1.2) * sc * (0.9 + fl * 0.2);
        vec2 id = floor(g);
        vec2 f = fract(g) - 0.5;
        float h = hash12(id + fl * 17.0);
        float on = step(h, density * (0.25 + 0.75 * bump(p)));
        vec2 o = (hash22(id + 3.0 + fl) - 0.5) * 0.5;
        float a = hash11(h * 91.0) * TAU + p * 12.0 * (h - 0.5);
        vec2 q = rot(a) * (f - o);
        q.x *= 1.0 / max(abs(cos(p * 20.0 * h + h * 7.0)), 0.25);
        float d = sdBox(q, vec2(0.18, 0.09));
        float m = (1.0 - smoothstep(0.0, 0.03, d)) * on;
        col.rgb = mix(col.rgb, pal(hash11(h * 37.0)) * (0.8 + 0.2 * cos(a)), m);
    }
    fragColor = col;
}
""",
    variants=[Variant("confeti", "Confeti", "Confetti", thumb=0.45)],
)

COMIC = Family(
    key="comic_burst", app_category="cinematic", category="divertidas", duration=0.9,
    params=[Param("spikes", "Spikes", 6.0, 24.0, 14.0)],
    tags=["comic", "historieta", "pop art", "explosion", "boom"],
    defines={"BURST": "#ffe14d", "RIM": "#ff3b30"},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float a = atan(P.y, P.x);
    float r = length(P);
    // A spiky burst grows over the outgoing picture with speed lines, then opens on the incoming one.
    float grow = easeInOut(sat(p / 0.45)) * 1.4;
    float spikeR = (0.75 + 0.25 * abs(fract(a / TAU * spikes) - 0.5) * 2.0) * grow;
    float hole = easeIn(sat((p - 0.33) / 0.55)) * 1.8;
    vec4 col = A(uv);
    float lines = step(0.85, hash11(floor(a / TAU * 90.0))) * smoothstep(0.15, 0.5, r) * bump(p);
    col.rgb = mix(col.rgb, vec3(1.0), lines * 0.8);
    float inBurst = 1.0 - smoothstep(spikeR - 0.004, spikeR + 0.004, r);
    vec2 cell = fract(uv * u_resolution / 9.0) - 0.5;
    float dots = 1.0 - smoothstep(0.18, 0.24, length(cell));
    vec3 bc = mix(BURST, BURST * 0.8 + RIM * 0.2, dots * smoothstep(0.0, 0.8, r / max(spikeR, 0.01)));
    float rim = (1.0 - smoothstep(0.0, 0.03, abs(r - spikeR * 0.88))) * inBurst;
    bc = mix(bc, RIM, rim);
    col.rgb = mix(col.rgb, bc, inBurst);
    float holeR = hole * (0.75 + 0.25 * abs(fract(a / TAU * spikes + 0.5) - 0.5) * 2.0);
    col = mix(col, B(uv), 1.0 - smoothstep(holeR - 0.004, holeR + 0.004, r));
    fragColor = col;
}
""",
    variants=[
        Variant("explosion-comic", "Explosión de cómic", "Comic burst", thumb=0.45),
        Variant("explosion-comic-azul", "Explosión de cómic azul", "Blue comic burst", {"BURST": "#4dd2ff", "RIM": "#1b2bff"}, thumb=0.45),
    ],
)

SNOW = Family(
    key="snow", app_category="liquid", category="divertidas", duration=1.6,
    params=[Param("density", "Density", 0.3, 1.0, 0.85)],
    tags=["nieve", "navidad", "invierno", "copos", "snow"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec4 col = mix(A(uv), B(uv), smoothstep(0.42, 0.58, p));
    float k = bump(p);
    col.rgb = mix(col.rgb, vec3(0.93, 0.96, 1.0), k * 0.45);
    for (int layer = 0; layer < 4; ++layer) {
        float fl = float(layer);
        float sc = 6.0 + fl * 5.0;
        vec2 g = toP(uv) * sc;
        g.y -= p * sc * (0.6 + fl * 0.3);
        g.x += sin(g.y * 0.7 + fl) * 0.3;
        vec2 id = floor(g);
        vec2 f = fract(g) - 0.5 - (hash22(id + fl * 9.0) - 0.5) * 0.6;
        float on = step(hash12(id + fl * 3.0), density * (0.35 + 0.65 * k));
        float rr = 0.08 + 0.12 * hash12(id + 5.0);
        float flake = (1.0 - smoothstep(rr * 0.4, rr, length(f))) * on;
        col.rgb = mix(col.rgb, vec3(1.0), flake * (0.6 + 0.4 * fl / 3.0));
    }
    fragColor = col;
}
""",
    variants=[Variant("nieve", "Nevada", "Snowfall", thumb=0.45)],
)

SPARKLE = Family(
    key="sparkle", app_category="cinematic", category="divertidas", duration=1.2,
    params=[Param("intensity", "Intensity", 0.0, 1.5, 1.0)],
    tags=["brillos", "destellos", "magia", "glitter", "sparkle"],
    defines={"GLINT": "#fff2c4"},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec4 col = mix(A(uv), B(uv), smoothstep(0.3, 0.7, p));
    float k = bump(p) * intensity;
    vec2 n = vec2(aspect(), 1.0) * 14.0;
    vec2 g = uv * n;
    vec2 id = floor(g);
    vec2 f = fract(g) - 0.5 - (hash22(id) - 0.5) * 0.5;
    float h = hash12(id + 2.0);
    float tw = sat(1.0 - abs(fract(p * 3.0 + h) - 0.5) * 6.0);
    float on = step(0.78, h) * tw;
    float cross_ = exp(-abs(f.x) * 60.0) * exp(-abs(f.y) * 6.0) + exp(-abs(f.y) * 60.0) * exp(-abs(f.x) * 6.0);
    float dot_ = exp(-length(f) * 18.0);
    col.rgb += GLINT * (cross_ * 0.9 + dot_) * on * k * 1.4;
    col.rgb += GLINT * 0.12 * k;
    fragColor = vec4(min(col.rgb, vec3(1.0)), col.a);
}
""",
    variants=[
        Variant("brillos", "Brillos mágicos", "Magic sparkles"),
        Variant("brillos-rosa", "Brillos rosas", "Pink sparkles", {"GLINT": "#ffc2e6"}),
    ],
)

RAINBOW = Family(
    key="rainbow_wipe", app_category="basic", category="divertidas", duration=1.1,
    params=[Param("band", "Band Width", 0.1, 0.8, 0.4)],
    tags=["arcoiris", "colores", "rainbow", "barrido", "orgullo"],
    body=r"""
vec3 hue(float h) { return clamp(abs(fract(h + vec3(0.0, 0.333, 0.667)) * 6.0 - 3.0) - 1.0, 0.0, 1.0); }
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float s = uv.x * 0.8 + (1.0 - uv.y) * 0.2;
    float e = mix(-0.02, 1.0 + band + 0.02, easeInOut(p));
    float inside = (s - (e - band)) / band;   // 0..1 across the band
    vec4 col = s > e ? A(uv) : B(uv);
    if (inside >= 0.0 && inside <= 1.0) {
        vec3 rb = hue(inside * 0.8);
        col = vec4(mix(col.rgb, rb, 0.85), 1.0);
    }
    fragColor = col;
}
""",
    variants=[Variant("arcoiris", "Barrido arcoíris", "Rainbow wipe")],
)

POP_CIRCLES = Family(
    key="pop_circles", app_category="geometric", category="divertidas", duration=1.1,
    params=[Param("count", "Circles", 3.0, 14.0, 10.0)],
    tags=["circulos", "burbujas", "pop", "colores", "lunares"],
    body=r"""
vec3 pal(float h) {
    vec3 c = vec3(1.0, 0.36, 0.5);
    if (h > 0.25) c = vec3(1.0, 0.8, 0.2);
    if (h > 0.5) c = vec3(0.25, 0.75, 1.0);
    if (h > 0.75) c = vec3(0.55, 0.9, 0.45);
    return c;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    vec4 col = A(uv);
    // Coloured circles pop up one after another; the incoming picture fills the last ones.
    for (int i = 0; i < 14; ++i) {
        if (float(i) >= count) break;
        float fi = float(i);
        vec2 c = (hash22(vec2(fi, 21.0)) - 0.5) * vec2(aspect(), 1.0) * 1.2;
        float delay = fi / count * 0.55;
        float k = sat((p - delay) / 0.45);
        float r = easeOutBack(k) * 0.75;
        float d = length(P - c) - r;
        float m = 1.0 - smoothstep(-0.003, 0.003, d);
        bool last = fi >= count - 3.0;
        col = mix(col, last ? B(uv) : vec4(pal(hash11(fi * 3.7)), 1.0), m);
    }
    fragColor = mix(col, B(uv), smoothstep(0.9, 1.0, p));
}
""",
    variants=[Variant("circulos-pop", "Círculos pop", "Pop circles")],
)

TV_OFF = Family(
    key="tv_off", app_category="glitch", category="divertidas", duration=1.0,
    params=[Param("glow", "Glow", 0.0, 1.5, 1.0)],
    tags=["tv", "apagar", "television", "retro", "crt"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    // The outgoing picture collapses into a bright line and a dot like an old TV switching off;
    // the incoming one switches on the same way, in reverse.
    float t = p < 0.5 ? p * 2.0 : (1.0 - p) * 2.0;
    float sy = 1.0 - easeIn(sat(t / 0.6));
    float sx = 1.0 - easeIn(sat((t - 0.55) / 0.45));
    sy = max(sy, 0.004);
    sx = max(sx, 0.002);
    vec2 q = vec2(P.x / sx, P.y / sy);
    vec2 src = fromP(q);
    vec4 pic = p < 0.5 ? Ac(src) : Bc(src);
    float bright = (1.0 - sy) * 2.0 * glow;
    pic.rgb = pic.rgb * (1.0 + bright) + vec3(bright * 0.3);
    vec4 bg = vec4(0.02, 0.02, 0.025, 1.0);
    float dot_ = exp(-length(P) * 40.0) * (1.0 - sx) * glow * step(0.5, 1.0 - sx + 0.5);
    vec4 col = over(pic, bg);
    col.rgb += vec3(0.9, 0.95, 1.0) * dot_ * 2.0;
    fragColor = vec4(min(col.rgb, vec3(1.0)), 1.0);
}
""",
    variants=[Variant("tv-apagar", "Apagar la tele", "TV switch-off", thumb=0.4)],
)

LEADER = Family(
    key="film_leader", app_category="cinematic", category="divertidas", duration=1.4,
    params=[Param("sweep", "Sweeps", 1.0, 4.0, 2.0)],
    tags=["cuenta regresiva", "cine", "pelicula", "leader", "countdown", "retro"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    // An old film leader: crosshair and circles over a grey frame, a sweeping hand, then the cut.
    float k = bump(p);
    float lead = smoothstep(0.1, 0.25, p) * (1.0 - smoothstep(0.75, 0.9, p));
    vec4 base = p < 0.5 ? A(uv) : B(uv);
    float l = luma(base.rgb);
    vec3 film = vec3(0.55 + 0.25 * l) * vec3(1.0, 0.97, 0.9);
    float a = fract(atan(P.x, -P.y) / TAU + 1.0);
    float hand = fract(p * sweep * 1.0);
    vec3 c = film;
    c *= a < hand ? 0.72 : 1.0;
    float r = length(P);
    float rings = (1.0 - smoothstep(0.0, 0.006, abs(r - 0.33))) + (1.0 - smoothstep(0.0, 0.006, abs(r - 0.4)));
    float cross_ = (1.0 - smoothstep(0.0, 0.004, abs(P.x))) + (1.0 - smoothstep(0.0, 0.004, abs(P.y)));
    c = mix(c, vec3(0.08), sat(rings + cross_) * 0.85);
    float f = floor(p * 24.0);
    c *= 0.9 + 0.2 * hash11(f);
    fragColor = vec4(mix(base.rgb, c, lead), base.a);
}
""",
    variants=[Variant("cuenta-cine", "Cuenta de cine", "Film leader", thumb=0.4)],
)

FAMILIES = [LIGHTNING, HEARTS, STARS, CONFETTI, COMIC, SNOW, SPARKLE, RAINBOW, POP_CIRCLES, TV_OFF, LEADER]
