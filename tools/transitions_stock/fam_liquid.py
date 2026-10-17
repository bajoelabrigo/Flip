"""Ink, paint, smoke, water and fire transitions."""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)

INK = Family(
    key="ink_drop", app_category="liquid", category="liquido", duration=1.5,
    params=[Param("detail", "Edge Detail", 0.0, 1.0, 0.5)],
    tags=["tinta", "gota", "mancha", "ink", "acuarela"],
    defines={"INK": "#0a0a0d", "INKED": 1.0, "DROPS": 1.0},
    body=r"""
float field(vec2 P) {
    float best = 9.0;
    for (int i = 0; i < 6; ++i) {
        if (float(i) >= DROPS) break;
        vec2 c = DROPS < 1.5 ? vec2(0.0) : (hash22(vec2(float(i), 11.0)) - 0.5) * vec2(aspect(), 1.0) * 0.85;
        float delay = DROPS < 1.5 ? 0.0 : hash11(float(i) + 4.0) * 0.35;
        best = min(best, length(P - c) + delay);
    }
    return best;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float n = fbm(P * 5.0 + 2.0) * 0.28 + fbm(P * 18.0) * 0.08 * detail;
    float d = field(P) + n - 0.18;
    float reach = (DROPS < 1.5 ? 1.35 : 1.5);
    float t1 = easeOut(p * 1.25) * reach;
    float t2 = easeInOut(sat(p * 1.35 - 0.3)) * (reach + 0.1);
    vec4 col = A(uv);
    if (INKED > 0.5) {
        float m1 = 1.0 - smoothstep(t1 - 0.02, t1, d);
        // Wet edge: the ink is darker where it is still spreading.
        vec3 ink = INK * (0.8 + 0.3 * fbm(P * 9.0)) + (1.0 - smoothstep(0.0, 0.05, t1 - d)) * 0.08;
        col = mix(col, vec4(ink, 1.0), m1);
        float m2 = 1.0 - smoothstep(t2 - 0.03, t2, d + 0.05);
        col = mix(col, B(uv), m2);
    } else {
        float m = 1.0 - smoothstep(t1 - 0.015, t1, d);
        vec4 b = B(uv);
        b.rgb *= 1.0 - 0.35 * (1.0 - smoothstep(0.0, 0.06, t1 - d)) * m;
        col = mix(col, b, m);
    }
    fragColor = mix(col, B(uv), smoothstep(0.96, 1.0, p));
}
""",
    variants=[
        Variant("tinta-negra", "Gota de tinta negra", "Black ink drop"),
        Variant("tinta-blanca", "Manchas de tinta blanca", "White ink blots", {"INK": "#f4f1ea", "DROPS": 5.0}),
        Variant("tinta-azul", "Manchas de tinta azul", "Blue ink blots", {"INK": "#1438a8", "DROPS": 4.0}),
        Variant("tinta-roja", "Gota de tinta roja", "Red ink drop", {"INK": "#b3121e"}),
        Variant("tinta-revelar", "Mancha que revela", "Ink reveal", {"INKED": 0.0, "DROPS": 3.0}),
    ],
)

SPLASH = Family(
    key="paint_splash", app_category="liquid", category="liquido", duration=1.0,
    params=[Param("spikes", "Splatter", 0.0, 1.0, 0.6)],
    tags=["salpicadura", "pintura", "splash", "mancha", "splat"],
    defines={"ORIGIN": "vec2(0.0)", "RIM": "#ff3b6b", "MULTI": 0.0},
    body=r"""
float splat(vec2 P, vec2 c, float r, float seed) {
    vec2 d = P - c;
    float a = atan(d.y, d.x);
    float wob = (fbm(vec2(a * 2.0, seed)) - 0.5) * 0.5;
    float spk = pow(abs(sin(a * 7.0 + seed * 3.0)), 18.0) * spikes * 0.45 + pow(abs(sin(a * 13.0 + seed)), 30.0) * spikes * 0.3;
    float body = length(d) - r * (1.0 + wob + spk);
    // Droplets flung out around the splat.
    float drops = 9.0;
    for (int i = 0; i < 9; ++i) {
        float aa = hash11(float(i) + seed * 7.0) * TAU;
        float rr = r * (1.3 + hash11(float(i) * 3.0 + seed) * 0.8);
        vec2 q = c + vec2(cos(aa), sin(aa)) * rr;
        drops = min(drops, length(P - q) - r * 0.07 * (0.5 + hash11(float(i) + 2.0 + seed)));
    }
    return min(body, drops);
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float t = easeOut(p);
    float d;
    if (MULTI > 0.5) {
        d = 9.0;
        for (int i = 0; i < 3; ++i) {
            vec2 c = (hash22(vec2(float(i), 2.0)) - 0.5) * vec2(aspect(), 1.0) * 0.8;
            float tt = easeOut(sat((p - float(i) * 0.15) / 0.7));
            d = min(d, splat(P, c, tt * 0.75, float(i) + 1.0));
        }
    } else {
        float reach = length(ORIGIN) > 0.01 ? 1.6 : 0.95;
        d = splat(P, ORIGIN, t * reach, 1.0);
    }
    float aa = 1.5 / u_resolution.y;
    float m = 1.0 - smoothstep(-aa, aa, d);
    float rim = (1.0 - smoothstep(0.0, 0.03, abs(d + 0.015))) * (1.0 - step(0.98, p));
    vec4 col = mix(A(uv), B(uv), m);
    col.rgb = mix(col.rgb, RIM, rim * 0.9);
    if (p >= 0.995) col = B(uv);
    fragColor = col;
}
""",
    variants=[
        Variant("salpicadura", "Salpicadura de pintura", "Paint splash"),
        Variant("salpicadura-esquina", "Salpicadura desde la esquina", "Corner splash",
                {"ORIGIN": "vec2(0.5 * aspect(), 0.5)", "RIM": "#18c8ff"}),
        Variant("salpicaduras", "Salpicaduras", "Paint splatters", {"MULTI": 1.0, "RIM": "#ffd400"}),
    ],
)

SMOKE = Family(
    key="smoke", app_category="liquid", category="liquido", params=[INTENSITY], duration=1.6,
    tags=["humo", "niebla", "smoke", "bruma", "misterio"],
    defines={"SMOKE": "#151518"},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    // Smoke rises and thickens over the outgoing picture, then thins out over the incoming one.
    vec2 flow = vec2(0.0, p * 1.2);
    float n = fbm(P * 2.5 + flow + fbm(P * 1.5 - flow) * 1.5);
    float density = sat(bump(p) * 1.6 * intensity - (1.0 - n) * 0.9 + (uv.y - 0.5) * 0.4);
    vec4 base = mix(A(uv), B(uv), smoothstep(0.4, 0.6, p));
    vec3 s = SMOKE * (0.7 + 0.6 * n);
    fragColor = vec4(mix(base.rgb, s, density), base.a);
}
""",
    variants=[
        Variant("humo-oscuro", "Humo oscuro", "Dark smoke"),
        Variant("humo-blanco", "Niebla blanca", "White mist", {"SMOKE": "#eeeef2"}),
    ],
)

RIPPLE = Family(
    key="water_ripple", app_category="liquid", category="liquido", params=[INTENSITY], duration=1.4,
    tags=["agua", "ondas", "ripple", "gota", "lago"],
    defines={"RAIN": 0.0},
    body=r"""
vec2 wave(vec2 P, vec2 c, float t, float amp) {
    vec2 d = P - c;
    float r = length(d);
    float front = t * 1.3;
    float w = sin((r - front) * 40.0) * exp(-abs(r - front) * 8.0) * amp;
    return r > 0.0001 ? d / r * w : vec2(0.0);
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float k = bump(p) * intensity;
    vec2 off = vec2(0.0);
    if (RAIN > 0.5) {
        for (int i = 0; i < 6; ++i) {
            vec2 c = (hash22(vec2(float(i), 6.0)) - 0.5) * vec2(aspect(), 1.0);
            float t = sat(p * 1.5 - hash11(float(i)) * 0.5);
            off += wave(P, c, t, 0.012);
        }
    } else {
        off = wave(P, vec2(0.0), p, 0.03);
    }
    off *= k;
    vec2 q = fromP(P + off);
    vec4 col = mix(A(q), B(q), smoothstep(0.3, 0.7, p));
    col.rgb += vec3(length(off) * 6.0);
    fragColor = vec4(min(col.rgb, vec3(1.0)), col.a);
}
""",
    variants=[
        Variant("ondas-agua", "Ondas de agua", "Water ripple"),
        Variant("lluvia-ondas", "Lluvia sobre el agua", "Rain ripples", {"RAIN": 1.0}),
    ],
)

WAVE = Family(
    key="liquid_wave", app_category="liquid", category="liquido", duration=1.1,
    params=[Param("height", "Wave Height", 0.0, 0.2, 0.06)],
    tags=["ola", "liquido", "wave", "agua", "barrido"],
    defines={"VERTICAL": 1.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float along = VERTICAL > 0.5 ? 1.0 - uv.y : uv.x;
    float across = VERTICAL > 0.5 ? uv.x : uv.y;
    float e = mix(-height * 2.0, 1.0 + height * 2.0, easeInOut(p));
    float edge = e + sin(across * 9.0 + p * 10.0) * height + sin(across * 23.0 - p * 7.0) * height * 0.35;
    float d = along - edge;
    // Under the liquid line the incoming picture shows through a little refraction, with foam on top.
    vec2 refr = (VERTICAL > 0.5 ? vec2(0.0, 1.0) : vec2(1.0, 0.0)) * sin(across * 30.0 + along * 20.0) * 0.006;
    vec4 b = B(uv + refr * (1.0 - smoothstep(-0.3, 0.0, d)) * 0.0 + refr * smoothstep(-0.25, 0.0, d));
    float foam = 1.0 - smoothstep(0.0, 0.015, abs(d + 0.006));
    b.rgb = mix(b.rgb, vec3(1.0), foam * 0.85);
    b.rgb *= 1.0 - 0.25 * smoothstep(-0.1, 0.0, d);
    float aa = 1.5 / u_resolution.y;
    fragColor = mix(b, A(uv), smoothstep(-aa, aa, d));
}
""",
    variants=[
        Variant("ola-sube", "Ola que sube", "Rising wave"),
        Variant("ola-lateral", "Ola lateral", "Sideways wave", {"VERTICAL": 0.0}),
    ],
)

MELT = Family(
    key="melt_drip", app_category="liquid", category="liquido", duration=1.3,
    params=[Param("drips", "Drips", 4.0, 60.0, 22.0)],
    tags=["derretir", "goteo", "chorreado", "melt", "drip"],
    defines={"UP": 0.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float y = UP > 0.5 ? 1.0 - uv.y : uv.y;
    float col_ = uv.x * drips;
    float i = floor(col_);
    float f = fract(col_);
    float sp = hash11(i + 1.0);
    // Rounded drip heads: each column runs at its own speed.
    float speed = 0.6 + 0.8 * sp;
    float t = easeIn(p) * speed * 1.5 + p * 0.25 + smoothstep(0.9, 1.0, p);
    float edge = t + sqrt(max(1.0 - pow((f - 0.5) * 2.0, 2.0), 0.0)) * 0.035 - 0.035;
    float aa = 1.5 / u_resolution.y;
    float m = 1.0 - smoothstep(edge - aa, edge + aa, y);
    // The outgoing picture is dragged along with the drips.
    float ys = y - min(t, 1.2) * 0.25 * (0.5 + 0.5 * sp);
    vec4 a = A(vec2(uv.x, UP > 0.5 ? 1.0 - ys : ys));
    vec4 b = B(uv);
    b.rgb *= 0.8 + 0.2 * smoothstep(0.0, 0.08, edge - y);
    fragColor = mix(a, b, m);
}
""",
    variants=[
        Variant("derretir", "Derretir hacia abajo", "Melt down"),
        Variant("derretir-arriba", "Derretir hacia arriba", "Melt up", {"UP": 1.0}),
    ],
)

SWIRL = Family(
    key="swirl", app_category="liquid", category="liquido", duration=1.2,
    params=[Param("strength", "Swirl", 0.0, 12.0, 5.0)],
    tags=["remolino", "giro", "swirl", "vortice", "espiral"],
    defines={"SPIN": 1.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float r = length(P);
    float k = bump(p);
    float ang = SPIN * strength * k * smoothstep(0.75, 0.0, r);
    vec2 q = fromP(rot(ang) * P * (1.0 - 0.2 * k));
    vec4 col = mix(A(q), B(q), smoothstep(0.35, 0.65, p));
    fragColor = col;
}
""",
    variants=[
        Variant("remolino", "Remolino", "Swirl"),
        Variant("remolino-izquierda", "Remolino a la izquierda", "Swirl left", {"SPIN": -1.0}),
        Variant("remolino-fuerte", "Vórtice", "Vortex", params={"strength": 11.0}),
    ],
)

FIRE = Family(
    key="fire", app_category="liquid", category="liquido", params=[INTENSITY], duration=1.4,
    tags=["fuego", "llamas", "fire", "quemar", "calor"],
    defines={"RING": 0.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float s = RING > 0.5 ? 1.0 - length(P) / 1.02 : 1.0 - uv.y;
    float n = fbm(vec2(P.x * 4.0, P.y * 2.0 + p * 4.0));
    float t = mix(-0.3, 1.25, easeInOut(p));
    float d = s + (n - 0.5) * 0.35 - t;   // < 0: burnt through to the incoming picture
    // Flames rise from the front into the outgoing picture.
    float flame = sat(1.0 - (d + 0.0) / (0.18 + 0.12 * fbm(vec2(P.x * 8.0, p * 6.0)))) * step(0.0, d);
    vec3 fc = mix(vec3(1.0, 0.25, 0.02), vec3(1.0, 0.85, 0.3), flame * flame);
    vec4 a = A(uv);
    a.rgb = mix(a.rgb, a.rgb * 0.35, sat(1.0 - d * 5.0) * step(0.0, d));
    vec3 c = a.rgb + fc * flame * flame * 1.4 * intensity;
    vec4 b = B(uv);
    b.rgb += vec3(1.0, 0.45, 0.1) * (1.0 - smoothstep(-0.12, 0.0, d)) * 0.5 * intensity;
    fragColor = d < 0.0 ? vec4(min(b.rgb, vec3(1.0)), b.a) : vec4(min(c, vec3(1.0)), a.a);
}
""",
    variants=[
        Variant("fuego", "Fuego que sube", "Rising fire"),
        Variant("fuego-anillo", "Anillo de fuego", "Ring of fire", {"RING": 1.0}),
    ],
)

HAZE = Family(
    key="heat_haze", app_category="liquid", category="liquido", params=[INTENSITY], duration=1.3,
    tags=["calor", "espejismo", "ondulacion", "haze", "sueño"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = bump(p) * intensity;
    vec2 n = vec2(fbm(uv * vec2(6.0, 14.0) + vec2(0.0, p * 3.0)), fbm(uv * vec2(6.0, 14.0) + vec2(5.0, p * 3.0))) - 0.5;
    vec2 q = uv + n * 0.06 * k;
    vec4 col = mix(A(q), B(q), smoothstep(0.3, 0.7, p));
    col.rgb = mix(col.rgb, col.rgb * vec3(1.05, 1.0, 0.95) + 0.05, k * 0.5);
    fragColor = col;
}
""",
    variants=[Variant("espejismo", "Espejismo", "Heat haze")],
)

MORPH = Family(
    key="displace_morph", app_category="liquid", category="liquido", duration=1.2,
    params=[Param("strength", "Strength", 0.0, 0.5, 0.15)],
    tags=["morph", "desplazar", "liquido", "fusion", "mezcla"],
    defines={"BYCOLOR": 1.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    // Each picture pushes its pixels along its own colours; one melts into the other.
    vec2 da, db;
    if (BYCOLOR > 0.5) {
        vec3 ca = A(uv).rgb, cb = B(uv).rgb;
        da = vec2(ca.r - ca.b, ca.g - 0.5);
        db = vec2(cb.r - cb.b, cb.g - 0.5);
    } else {
        da = vec2(fbm(uv * 4.0), fbm(uv * 4.0 + 3.0)) - 0.5;
        db = vec2(fbm(uv * 4.0 + 7.0), fbm(uv * 4.0 + 9.0)) - 0.5;
    }
    vec4 a = A(uv + da * strength * p);
    vec4 b = B(uv - db * strength * (1.0 - p));
    fragColor = mix(a, b, easeInOut(p));
}
""",
    variants=[
        Variant("fusion-color", "Fusión por color", "Colour morph"),
        Variant("fusion-liquida", "Fusión líquida", "Liquid morph", {"BYCOLOR": 0.0}, params={"strength": 0.3}),
    ],
)

FAMILIES = [INK, SPLASH, SMOKE, RIPPLE, WAVE, MELT, SWIRL, FIRE, HAZE, MORPH]
