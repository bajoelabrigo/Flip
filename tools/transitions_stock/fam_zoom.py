"""Zoom, punch and motion transitions."""

from kit import Family, Param, Variant

BLUR = Param("blur", "Motion Blur", 0.0, 1.5, 1.0)

MIRROR = r"""
vec2 mirrorUv(vec2 u) { return 1.0 - abs(1.0 - mod(u, 2.0)); }
"""

ZOOM_IN = Family(
    key="zoom_punch", app_category="cinematic", category="zoom", duration=0.7,
    params=[Param("zoom", "Zoom", 1.2, 5.0, 2.6), BLUR],
    tags=["zoom", "golpe", "punch", "impacto", "rapido", "reels"],
    defines={"FLASH": "#ffffff", "FLASHK": 0.0, "SHAKE": 0.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 c = vec2(0.5);
    vec2 sh = SHAKE * (hash22(vec2(floor(p * 30.0), 3.0)) - 0.5) * 0.05 * bump(p);
    vec4 col;
    if (p < 0.5) {
        float t = easeIn(p * 2.0);
        vec2 u = c + (uv - c) * mix(1.0, 1.0 / zoom, t) + sh;
        col = zoomBlurA(u, c, blur * t * 0.4);
    } else {
        float t = easeOut((p - 0.5) * 2.0);
        vec2 u = c + (uv - c) * mix(1.0 / zoom, 1.0, t) + sh;
        col = zoomBlurB(u, c, blur * (1.0 - t) * 0.4);
    }
    col.rgb = mix(col.rgb, FLASH, FLASHK * peak(p, 0.07));
    fragColor = col;
}
""",
    variants=[
        Variant("zoom-golpe", "Zoom con golpe", "Zoom punch", thumb=0.42),
        Variant("zoom-golpe-suave", "Zoom suave", "Soft zoom", params={"zoom": 1.6, "blur": 0.6}, thumb=0.42),
        Variant("zoom-golpe-fuerte", "Zoom con golpe fuerte", "Hard zoom punch", params={"zoom": 4.5, "blur": 1.4}, thumb=0.44),
        Variant("zoom-golpe-destello", "Zoom con destello", "Zoom flash", {"FLASHK": 0.9}, thumb=0.47),
        Variant("zoom-golpe-temblor", "Zoom con temblor", "Shaky zoom punch", {"SHAKE": 1.0}, params={"zoom": 3.2}, thumb=0.42),
    ],
)

ZOOM_OUT = Family(
    key="zoom_out", app_category="cinematic", category="zoom", duration=0.8,
    params=[Param("zoom", "Zoom", 1.2, 5.0, 2.5), BLUR],
    tags=["zoom", "alejar", "zoom out", "espejo", "golpe"],
    defines={"SPIN": 0.0},
    body=MIRROR + r"""
vec4 mirA(vec2 u, vec2 c, float k) {
    vec4 s = vec4(0.0);
    for (int i = 0; i < 16; ++i) s += A(mirrorUv(c + (u - c) * (1.0 + k * float(i) / 15.0)));
    return s / 16.0;
}
vec4 mirB(vec2 u, vec2 c, float k) {
    vec4 s = vec4(0.0);
    for (int i = 0; i < 16; ++i) s += B(mirrorUv(c + (u - c) * (1.0 + k * float(i) / 15.0)));
    return s / 16.0;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 c = vec2(0.5);
    float ang = SPIN * (p - 0.5) * 1.2;
    vec2 q = fromP(rot(ang * bump(p)) * toP(uv));
    if (p < 0.5) {
        float t = easeIn(p * 2.0);
        fragColor = mirA(c + (q - c) * mix(1.0, zoom, t), c, blur * t * 0.35);
    } else {
        float t = easeOut((p - 0.5) * 2.0);
        fragColor = mirB(c + (q - c) * mix(zoom, 1.0, t), c, blur * (1.0 - t) * 0.35);
    }
}
""",
    variants=[
        Variant("zoom-alejar", "Zoom hacia atrás", "Zoom out", thumb=0.4),
        Variant("zoom-alejar-giro", "Zoom atrás con giro", "Zoom out spin", {"SPIN": 1.0}, thumb=0.4),
    ],
)

ZOOM_SPIN = Family(
    key="zoom_spin", app_category="cinematic", category="zoom", duration=0.9,
    params=[BLUR],
    tags=["giro", "spin", "zoom", "rotar", "remolino"],
    defines={"TURNS": 0.5, "DIRS": 1.0},
    body=MIRROR + r"""
vec4 spinSample(vec2 uv, float ang, float s, bool useB) {
    vec2 q = fromP(rot(ang) * toP(uv) * s);
    q = mirrorUv(q);
    return useB ? B(q) : A(q);
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float e = easeInOut(p);
    float ang = DIRS * TURNS * TAU * (e - (p < 0.5 ? 0.0 : 1.0));
    float s = 1.0 - 0.45 * bump(p);
    float speed = DIRS * TURNS * TAU * 6.0 * p * (1.0 - p) * 0.06 * blur;
    vec4 col = vec4(0.0);
    for (int i = 0; i < 12; ++i) {
        float o = (float(i) / 11.0 - 0.5) * speed;
        col += spinSample(uv, ang + o, s, p >= 0.5);
    }
    fragColor = col / 12.0;
}
""",
    variants=[
        Variant("giro-horario", "Giro con zoom", "Spin zoom", thumb=0.4),
        Variant("giro-antihorario", "Giro con zoom a la izquierda", "Spin zoom left", {"DIRS": -1.0}, thumb=0.4),
        Variant("giro-doble", "Doble giro", "Double spin", {"TURNS": 1.0}, thumb=0.4),
    ],
)

SHAKE = Family(
    key="shake_cut", app_category="cinematic", category="zoom", duration=0.6,
    params=[Param("amount", "Shake", 0.0, 2.0, 1.0)],
    tags=["temblor", "sacudida", "shake", "camara", "golpe", "impacto"],
    defines={"FREQ": 18.0, "AMP": 0.05},
    body=MIRROR + r"""
vec2 jolt(float t) {
    float f = t * FREQ;
    float i = floor(f);
    vec2 a = hash22(vec2(i, 1.0)) - 0.5, b = hash22(vec2(i + 1.0, 1.0)) - 0.5;
    return mix(a, b, easeInOut(fract(f)));
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = bump(p) * amount;
    vec2 o = jolt(p) * AMP * k;
    vec2 v = (jolt(p + 0.02) - jolt(p - 0.02)) * AMP * k * 0.8;
    float zoom = 1.0 - 0.08 * k;
    vec4 col = vec4(0.0);
    float m = smoothstep(0.42, 0.58, p);
    for (int i = 0; i < 10; ++i) {
        vec2 q = mirrorUv(vec2(0.5) + (uv - 0.5) * zoom + o + v * (float(i) / 9.0 - 0.5));
        col += mix(A(q), B(q), m);
    }
    fragColor = col / 10.0;
}
""",
    variants=[
        Variant("sacudida-suave", "Sacudida suave", "Soft shake", params={"amount": 0.7}),
        Variant("sacudida-fuerte", "Sacudida fuerte", "Hard shake", {"FREQ": 26.0, "AMP": 0.09}, params={"amount": 1.2}),
    ],
)

WHIP = Family(
    key="whip_pan", app_category="cinematic", category="movimiento", duration=0.6, params=[BLUR],
    tags=["paneo", "whip", "barrido rapido", "movimiento", "desenfoque"],
    defines={"DIR": (1.0, 0.0)},
    body=r"""
vec4 strip(vec2 q) {
    // The two pictures side by side along DIR: the outgoing one, then the incoming one after it.
    if (insideUv(q) > 0.5) return A(q);
    return B(q - DIR);
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float o = easeInOut(p);
    vec2 q = uv + DIR * o;
    float spread = 0.45 * blur * bump(p);
    vec4 col = vec4(0.0);
    for (int i = 0; i < 20; ++i) col += strip(q + DIR * spread * (float(i) / 19.0 - 0.5));
    fragColor = col / 20.0;
}
""",
    variants=[
        Variant("paneo-derecha", "Paneo rápido a la derecha", "Whip pan right"),
        Variant("paneo-izquierda", "Paneo rápido a la izquierda", "Whip pan left", {"DIR": (-1.0, 0.0)}),
        Variant("paneo-arriba", "Paneo rápido hacia arriba", "Whip pan up", {"DIR": (0.0, -1.0)}),
        Variant("paneo-abajo", "Paneo rápido hacia abajo", "Whip pan down", {"DIR": (0.0, 1.0)}),
    ],
)

TUNNEL = Family(
    key="light_tunnel", app_category="cinematic", category="zoom", duration=1.0,
    params=[Param("intensity", "Streaks", 0.0, 2.0, 1.0)],
    tags=["tunel", "hiperespacio", "velocidad", "warp", "zoom", "rayos"],
    defines={"RAINBOW": 0.0, "TINTC": "#ffffff"},
    body=r"""
vec3 hue(float h) { return clamp(abs(fract(h + vec3(0.0, 0.333, 0.667)) * 6.0 - 3.0) - 1.0, 0.0, 1.0); }
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = bump(p);
    vec2 c = vec2(0.5);
    vec4 col;
    if (p < 0.5) {
        float t = easeIn(p * 2.0);
        col = zoomBlurA(c + (uv - c) * mix(1.0, 0.35, t), c, 0.7 * t);
    } else {
        float t = easeOut((p - 0.5) * 2.0);
        col = zoomBlurB(c + (uv - c) * mix(0.35, 1.0, t), c, 0.7 * (1.0 - t));
    }
    vec2 d = toP(uv);
    float a = atan(d.y, d.x);
    float r = length(d);
    float rays = pow(hash11(floor(a * 60.0 / TAU * 3.0) + 5.0), 6.0);
    float lane = smoothstep(0.08, 0.5, r) * rays;
    vec3 rc = mix(TINTC, hue(a / TAU + p), RAINBOW);
    col.rgb += rc * lane * k * k * intensity * 2.0;
    col.rgb = mix(col.rgb, vec3(1.0), peak(p, 0.05) * 0.7 * intensity);
    fragColor = vec4(min(col.rgb, 1.0), col.a);
}
""",
    variants=[
        Variant("tunel-luz", "Túnel de luz", "Light tunnel", thumb=0.42),
        Variant("tunel-arcoiris", "Túnel arcoíris", "Rainbow tunnel", {"RAINBOW": 1.0}, thumb=0.42),
    ],
)

STRETCH = Family(
    key="stretch_snap", app_category="modern", category="zoom", duration=0.7, params=[BLUR],
    tags=["estirar", "stretch", "elastico", "golpe", "snap"],
    defines={"AXIS": (1.0, 0.0)},
    body=r"""
vec4 smp(vec2 uv, float s, bool useB, float spread) {
    vec4 col = vec4(0.0);
    for (int i = 0; i < 12; ++i) {
        vec2 d = uv - 0.5;
        vec2 q = 0.5 + d / mix(vec2(1.0), vec2(s), AXIS) + AXIS * spread * (float(i) / 11.0 - 0.5);
        col += useB ? B(q) : A(q);
    }
    return col / 12.0;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    if (p < 0.5) {
        float t = easeIn(p * 2.0);
        fragColor = smp(uv, 1.0 + 5.0 * t, false, 0.3 * t * blur);
    } else {
        float t = (p - 0.5) * 2.0;
        float s = mix(6.0, 1.0, easeOutBack(t));
        fragColor = smp(uv, max(s, 0.6), true, 0.3 * (1.0 - t) * blur);
    }
}
""",
    variants=[
        Variant("estirar-horizontal", "Estirón horizontal", "Horizontal stretch", thumb=0.4),
        Variant("estirar-vertical", "Estirón vertical", "Vertical stretch", {"AXIS": (0.0, 1.0)}, thumb=0.4),
    ],
)

BOUNCE = Family(
    key="bounce_push", app_category="basic", category="movimiento", duration=0.9, params=[BLUR],
    tags=["empujar", "rebote", "push", "deslizar", "slide", "elastico"],
    defines={"DIR": (-1.0, 0.0)},
    body=r"""
vec2 mirrorUv(vec2 u) { return 1.0 - abs(1.0 - mod(u, 2.0)); }
float ease(float t) {
    t = sat(t);
    return easeOutBack(pow(t, 1.8));
}
vec4 scene(vec2 uv, float e) {
    vec4 a = Ac(uv - DIR * e);
    vec4 b = B(uv - DIR * (e - 1.0));
    float inB = insideUv(uv - DIR * (e - 1.0));
    return mix(a, b, max(inB, 1.0 - a.a));
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float e = ease(p);
    float v = abs(ease(p + 0.01) - ease(p - 0.01)) / 0.02;
    vec4 col = vec4(0.0);
    for (int i = 0; i < 10; ++i) col += scene(uv + DIR * v * 0.03 * blur * (float(i) / 9.0 - 0.5), e);
    fragColor = col / 10.0;
}
""",
    variants=[
        Variant("empuje-rebote-izquierda", "Empujar con rebote a la izquierda", "Bounce push left", thumb=0.3),
        Variant("empuje-rebote-derecha", "Empujar con rebote a la derecha", "Bounce push right", {"DIR": (1.0, 0.0)}, thumb=0.3),
        Variant("empuje-rebote-arriba", "Empujar con rebote hacia arriba", "Bounce push up", {"DIR": (0.0, -1.0)}, thumb=0.3),
        Variant("empuje-rebote-abajo", "Empujar con rebote hacia abajo", "Bounce push down", {"DIR": (0.0, 1.0)}, thumb=0.3),
    ],
)

CARD_TOSS = Family(
    key="card_toss", app_category="modern", category="movimiento", duration=1.0,
    params=[Param("tilt", "Tilt", 0.0, 1.5, 1.0)],
    tags=["tarjeta", "lanzar", "girar", "deslizar", "card", "foto"],
    defines={"SIDE": 1.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float e = easeOut(p);
    vec2 P = toP(uv);
    // The incoming picture is thrown in like a photo on a table: from below one side, turning.
    vec2 off = vec2(SIDE * aspect() * 1.1, 0.35) * (1.0 - e);
    float ang = SIDE * 0.5 * tilt * (1.0 - e);
    float sc = mix(0.8, 1.0, e);
    vec2 q = rot(ang) * (P - off) / sc;
    vec2 qb = fromP(q);
    vec4 b = Bc(qb);
    // A soft shadow under the card.
    vec2 sq = rot(ang) * (P - off - vec2(0.02, 0.03)) / sc;
    float sh = 1.0 - smoothstep(-0.02, 0.08, sdBox(sq, vec2(aspect() * 0.5, 0.5)));
    vec4 a = A(uv);
    a.rgb *= 1.0 - 0.45 * e;
    a.rgb *= 1.0 - 0.3 * sh * (1.0 - b.a);
    fragColor = over(b, a);
}
""",
    variants=[
        Variant("tarjeta-derecha", "Foto lanzada desde la derecha", "Card toss from right", thumb=0.45),
        Variant("tarjeta-izquierda", "Foto lanzada desde la izquierda", "Card toss from left", {"SIDE": -1.0}, thumb=0.45),
    ],
)

PANELS = Family(
    key="split_panels", app_category="geometric", category="movimiento", duration=1.0,
    params=[Param("stagger", "Stagger", 0.0, 1.0, 0.5)],
    tags=["paneles", "columnas", "deslizar", "split", "persiana"],
    defines={"N": 3.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float i = floor(uv.x * N);
    float dir = mod(i, 2.0) < 1.0 ? -1.0 : 1.0;
    float lag = (i / max(N - 1.0, 1.0)) * stagger * 0.5;
    float t = easeInOut(sat((p - lag) / (1.0 - stagger * 0.5)));
    // Each column of the incoming picture slides in vertically, alternating up and down; the
    // outgoing column is pushed out the other side.
    vec4 a = Ac(vec2(uv.x, uv.y - dir * t));
    vec4 b = Bc(vec2(uv.x, uv.y - dir * (t - 1.0)));
    float edge = abs(fract(uv.x * N) - 0.5) > 0.49 ? 0.0 : 1.0;
    fragColor = over(b, a);
}
""",
    variants=[
        Variant("paneles-3", "Tres paneles", "Three panels"),
        Variant("paneles-5", "Cinco paneles", "Five panels", {"N": 5.0}),
        Variant("paneles-8", "Ocho columnas", "Eight columns", {"N": 8.0}, params={"stagger": 0.8}),
    ],
)

FAMILIES = [ZOOM_IN, ZOOM_OUT, ZOOM_SPIN, SHAKE, WHIP, TUNNEL, STRETCH, BOUNCE, CARD_TOSS, PANELS]
