"""Shape, grid and wipe transitions."""

from kit import Family, Param, Variant

SOFT = Param("softness", "Edge Softness", 0.0, 0.15, 0.012)

SHAPES = {
    "circle": ("(length(q) - 1.0)", 1.05),
    "heart": ("sdHeart(q, 1.0)", 1.75),
    "star": ("sdStar(q, 1.0, 5.0, 0.48)", 2.3),
    "diamond": ("sdPoly(q, 0.7071, 4.0)", 1.45),
    "hexagon": ("sdPoly(q, 0.866, 6.0)", 1.25),
    "square": ("sdRoundBox(q, vec2(1.0), 0.28)", 1.12),
    "triangle": ("sdPoly(q, 0.5, 3.0)", 2.7),
    "cross": ("sdCross(q, 1.0)", 3.0),
    "flower": ("sdFlower(q, 1.0)", 1.9),
}


def shape(name: str, **extra) -> dict:
    sd, cover = SHAPES[name]
    d = {"SHAPE_SD(q)": sd, "COVER": cover}
    d.update(extra)
    return d


IRIS = Family(
    key="shape_iris", app_category="geometric", category="formas", params=[SOFT], duration=1.0,
    tags=["forma", "iris", "abrir", "shape", "reveal"],
    defines={"ORIGIN": "vec2(0.0)", "SPIN": 0.0, "BORDER": "#ffffff", "BW": 0.0, "CLOSE": 0.0, "BG": "#000000",
             **shape("circle")},
    body=r"""
float mask(vec2 P, float r) {
    if (r <= 0.0001) return 0.0;
    vec2 q = rot(SPIN * (1.0 - r / COVER)) * P / r;
    float d = SHAPE_SD(q) * r;
    return fillSd(d, softness + 1.0 / u_resolution.y);
}
float ring(vec2 P, float r) {
    if (r <= 0.0001 || BW <= 0.0) return 0.0;
    vec2 q = rot(SPIN * (1.0 - r / COVER)) * P / r;
    float d = SHAPE_SD(q) * r;
    return 1.0 - smoothstep(BW * 0.5, BW * 0.5 + 2.0 / u_resolution.y, abs(d - BW * 0.5));
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv) - ORIGIN;
    float extent = COVER * (length(ORIGIN) > 0.01 ? 2.05 : 1.0) * (1.0 + BW * 4.0);
    vec4 col;
    if (CLOSE > 0.5) {
        // Close on the outgoing picture, then open on the incoming one.
        float r = p < 0.5 ? extent * (1.0 - easeIn(p * 2.0)) : extent * easeOut(p * 2.0 - 1.0);
        vec4 pic = p < 0.5 ? A(uv) : B(uv);
        col = mix(vec4(BG, 1.0), pic, mask(P, r));
        col.rgb = mix(col.rgb, BORDER, ring(P, r) * step(0.002, r));
    } else {
        float r = extent * easeInOut(p);
        col = mix(A(uv), B(uv), mask(P, r));
        col.rgb = mix(col.rgb, BORDER, ring(P, r) * (1.0 - step(0.995, p)));
    }
    fragColor = col;
}
""",
    variants=[
        Variant("circulo", "Círculo que se abre", "Circle reveal", tags=["circulo", "circle"]),
        Variant("circulo-esquina", "Círculo desde la esquina", "Circle from corner",
                {"ORIGIN": "vec2(-0.5 * aspect(), 0.5)"}, tags=["circulo", "esquina"]),
        Variant("corazon", "Corazón", "Heart", shape("heart"), tags=["corazon", "heart", "amor", "san valentin"]),
        Variant("estrella", "Estrella", "Star", shape("star"), tags=["estrella", "star"]),
        Variant("estrella-giro", "Estrella que gira", "Spinning star", shape("star", SPIN=3.0), tags=["estrella", "giro"]),
        Variant("rombo", "Rombo", "Diamond", shape("diamond"), tags=["rombo", "diamante", "diamond"]),
        Variant("hexagono", "Hexágono", "Hexagon", shape("hexagon", SPIN=0.6), tags=["hexagono", "hexagon"]),
        Variant("cuadrado-redondeado", "Cuadrado redondeado", "Rounded square", shape("square"), tags=["cuadrado", "square"]),
        Variant("triangulo", "Triángulo", "Triangle", shape("triangle"), tags=["triangulo", "triangle"]),
        Variant("cruz", "Cruz", "Plus sign", shape("cross", SPIN=0.8), tags=["cruz", "mas", "plus"]),
        Variant("flor", "Flor", "Flower", shape("flower", SPIN=1.2), tags=["flor", "flower", "primavera"]),
        Variant("circulo-borde", "Círculo con borde blanco", "Circle with white ring",
                shape("circle", BW=0.025), tags=["circulo", "borde"]),
        Variant("corazon-borde", "Corazón con borde rosa", "Heart with pink outline",
                shape("heart", BW=0.03, BORDER="#ff4f9a"), tags=["corazon", "amor", "rosa"]),
        Variant("estrella-borde", "Estrella dorada", "Golden star",
                shape("star", BW=0.03, BORDER="#ffc83d", SPIN=1.0), tags=["estrella", "dorado"]),
        Variant("circulo-cerrar", "Cerrar y abrir en círculo", "Iris close and open",
                shape("circle", CLOSE=1.0), tags=["iris", "cerrar", "cine", "cartoon"], thumb=0.3),
        Variant("corazon-cerrar", "Cerrar en corazón", "Heart iris",
                shape("heart", CLOSE=1.0, BG="#ffd1e3"), tags=["corazon", "amor", "cerrar"], thumb=0.3),
    ],
)

SLATS = Family(
    key="slat_flip", app_category="geometric", category="barridos", duration=1.2,
    params=[Param("stagger", "Stagger", 0.0, 1.0, 0.6)],
    tags=["persiana", "lamas", "girar", "blinds", "3d"],
    defines={"N": 10.0, "VERTICAL": 0.0, "DIAG": 0.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float axis = VERTICAL > 0.5 ? uv.x : uv.y;
    float other = VERTICAL > 0.5 ? uv.y : uv.x;
    float i = floor(axis * N);
    float f = fract(axis * N);
    float order = i / max(N - 1.0, 1.0);
    if (DIAG > 0.5) order = mix(order, other, 0.6);
    float t = easeInOut(sat((p - order * stagger) / (1.0 - stagger)));
    float c = cos(t * PI);
    float g = 0.5 + (f - 0.5) / max(abs(c), 0.001);
    vec4 col = vec4(0.0, 0.0, 0.0, 1.0);
    if (g >= 0.0 && g <= 1.0) {
        float a2 = (i + g) / N;
        vec2 s = VERTICAL > 0.5 ? vec2(a2, uv.y) : vec2(uv.x, a2);
        col = c > 0.0 ? A(s) : B(s);
        col.rgb *= 0.55 + 0.45 * abs(c);
        col.rgb += vec3(0.25) * pow(1.0 - abs(c), 6.0) * (1.0 - abs(g - 0.5) * 2.0);
    }
    fragColor = col;
}
""",
    variants=[
        Variant("persiana-giratoria", "Persiana giratoria", "Rotating blinds", thumb=0.45),
        Variant("persiana-vertical", "Persiana vertical", "Vertical rotating blinds", {"VERTICAL": 1.0, "N": 12.0}, thumb=0.45),
        Variant("persiana-diagonal", "Persiana en diagonal", "Diagonal rotating blinds", {"DIAG": 1.0, "N": 14.0}, thumb=0.45),
    ],
)

TILES = Family(
    key="grid_tiles", app_category="geometric", category="formas", duration=1.2,
    params=[Param("cells", "Cells", 2.0, 20.0, 6.0)],
    tags=["cuadros", "mosaico", "rejilla", "grid", "tiles"],
    defines={"ORDER": 0.0, "FLIP": 0.0, "ROUND": 0.12},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 n = vec2(floor(cells * aspect() + 0.5), cells);
    vec2 g = uv * n;
    vec2 id = floor(g);
    vec2 l = fract(g) - 0.5;
    float o;
    if (ORDER < 0.5) o = hash12(id + 4.0);
    else if (ORDER < 1.5) o = (id.x + id.y) / (n.x + n.y - 2.0);
    else o = length((id + 0.5) / n - 0.5) / 0.7071;
    float t = sat((p - o * 0.6) / 0.4);
    if (FLIP > 0.5) {
        float c = cos(easeInOut(t) * PI);
        float gx = l.x / max(abs(c), 0.001);
        vec4 col = B(uv);
        col.rgb *= 0.25;
        if (abs(gx) <= 0.5) {
            vec2 s = (id + vec2(gx + 0.5, l.y + 0.5)) / n;
            col = c > 0.0 ? A(s) : B(s);
            col.rgb *= 0.6 + 0.4 * abs(c);
        }
        fragColor = col;
        return;
    }
    float s = easeOutBack(t) * 0.5;
    float d = sdRoundBox(l, vec2(max(s, 0.0001)), ROUND * s * 2.0);
    float m = fillSd(d, 0.02) * step(0.0001, t);
    if (t >= 1.0) m = 1.0;
    fragColor = mix(A(uv), B(uv), m);
}
""",
    variants=[
        Variant("cuadros-al-azar", "Cuadros al azar", "Random tiles"),
        Variant("cuadros-diagonal", "Cuadros en diagonal", "Diagonal tiles", {"ORDER": 1.0}),
        Variant("cuadros-centro", "Cuadros desde el centro", "Tiles from the centre", {"ORDER": 2.0}, params={"cells": 8.0}),
        Variant("cuadros-volteo", "Cuadros que se voltean", "Flipping tiles", {"ORDER": 1.0, "FLIP": 1.0}, params={"cells": 4.0}),
    ],
)

CHECKER = Family(
    key="checker", app_category="geometric", category="formas", duration=1.0,
    params=[Param("cells", "Cells", 2.0, 20.0, 8.0)],
    tags=["ajedrez", "damero", "checker", "cuadros"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 n = vec2(floor(cells * aspect() + 0.5), cells);
    vec2 id = floor(uv * n);
    vec2 l = fract(uv * n) - 0.5;
    float odd = mod(id.x + id.y, 2.0);
    float t = odd < 0.5 ? sat(p * 2.0) : sat(p * 2.0 - 1.0);
    t = easeInOut(t);
    float m = fillSd(sdBox(l, vec2(t * 0.5 + 0.001)), 0.01);
    if (t >= 1.0) m = 1.0;
    fragColor = mix(A(uv), B(uv), m);
}
""",
    variants=[
        Variant("ajedrez", "Tablero de ajedrez", "Checkerboard"),
        Variant("ajedrez-grande", "Tablero grande", "Large checkerboard", params={"cells": 3.0}),
    ],
)

STRIPES = Family(
    key="stripes_slide", app_category="geometric", category="barridos", duration=1.0,
    params=[Param("stripes", "Stripes", 2.0, 24.0, 7.0)],
    tags=["franjas", "rayas", "deslizar", "stripes"],
    defines={"ANG": 0.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 Q = rot(ANG) * toP(uv);
    float i = floor(Q.y * stripes + stripes * 2.0);
    float dir = mod(i, 2.0) < 1.0 ? 1.0 : -1.0;
    float lag = hash11(i + 2.0) * 0.25;
    float e = easeOut(sat((p - lag) / 0.75));
    float off = dir * (1.0 - e) * 2.2;
    vec2 src = fromP(rot(-ANG) * (Q - vec2(off, 0.0)));
    vec4 b = Bc(src);
    vec4 a = A(uv);
    a.rgb *= 1.0 - 0.25 * e;
    fragColor = over(b, a);
}
""",
    variants=[
        Variant("rayas-horizontales", "Rayas que se cruzan", "Crossing stripes"),
        Variant("rayas-verticales", "Rayas verticales", "Vertical stripes", {"ANG": 1.5708}, params={"stripes": 5.0}),
        Variant("rayas-diagonales", "Rayas en diagonal", "Diagonal stripes", {"ANG": 0.6}, params={"stripes": 9.0}),
    ],
)

CLOCK = Family(
    key="clock_wipe", app_category="geometric", category="barridos", params=[SOFT], duration=1.0,
    tags=["reloj", "radial", "clock", "aguja", "barrido"],
    defines={"HANDS": 1.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float a = atan(P.x, -P.y) / TAU + 0.5;
    a = fract(a + 0.5);
    float f = fract(a * HANDS);
    float t = easeInOut(p) * (1.0 + 0.04) - 0.02;
    float w = softness * 2.0 + 0.004;
    float m = 1.0 - smoothstep(t - w, t + w, f);
    if (p >= 0.999) m = 1.0;
    fragColor = mix(A(uv), B(uv), m);
}
""",
    variants=[
        Variant("reloj", "Reloj", "Clock wipe"),
        Variant("reloj-doble", "Reloj doble", "Double clock wipe", {"HANDS": 2.0}),
        Variant("reloj-cuatro", "Abanico de cuatro", "Four-way fan", {"HANDS": 4.0}),
    ],
)

SPIRAL = Family(
    key="spiral_wipe", app_category="geometric", category="barridos", params=[SOFT], duration=1.2,
    tags=["espiral", "spiral", "remolino", "caracol"],
    defines={"ARMS": 1.0, "TURNS": 3.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float r = length(P) / (0.5 * length(vec2(aspect(), 1.0)));
    float a = fract(atan(P.x, -P.y) / TAU + 1.0);
    float aa = fract(a * ARMS);
    float o = (floor(r * TURNS - aa) + aa + 1.0) / (TURNS + 1.0);
    float t = easeInOut(p) * 1.06 - 0.03;
    float m = 1.0 - smoothstep(t - softness - 0.01, t + softness + 0.01, o);
    fragColor = mix(A(uv), B(uv), m);
}
""",
    variants=[
        Variant("espiral", "Espiral", "Spiral"),
        Variant("espiral-triple", "Espiral de tres brazos", "Three-arm spiral", {"ARMS": 3.0, "TURNS": 2.0}),
    ],
)

BAND = Family(
    key="color_band_wipe", app_category="basic", category="barridos", duration=0.9,
    params=[Param("band", "Band Width", 0.0, 0.5, 0.18)],
    tags=["barrido", "franja", "color", "wipe", "diagonal"],
    defines={"DIR": (0.8, 0.6), "COL1": "#ffd400", "COL2": "#ffd400", "DOUBLE": 0.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 d = normalize(DIR);
    vec2 P = toP(uv);
    float ext = 0.5 * (abs(d.x) * aspect() + abs(d.y));
    float s = dot(P, d) / ext * 0.5 + 0.5;
    float bw = band * (DOUBLE > 0.5 ? 2.0 : 1.0);
    float e = mix(-0.02, 1.0 + bw + 0.02, easeInOut(p));
    float aa = 1.5 / u_resolution.y;
    vec4 col = A(uv);
    float inBand = smoothstep(e - bw - aa, e - bw + aa, s) * (1.0 - smoothstep(e - aa, e + aa, s));
    float inB = 1.0 - smoothstep(e - bw - aa, e - bw + aa, s);
    vec3 bc = COL1;
    if (DOUBLE > 0.5 && s < e - bw * 0.5) bc = COL2;
    col = mix(col, vec4(bc, 1.0), inBand);
    vec4 b = B(uv);
    b.rgb *= 1.0 - 0.3 * (1.0 - smoothstep(0.0, 0.08, e - bw - s));
    col = mix(col, b, inB);
    fragColor = col;
}
""",
    variants=[
        Variant("franja-amarilla", "Barrido con franja amarilla", "Yellow band wipe"),
        Variant("franja-blanca", "Barrido con franja blanca", "White band wipe", {"COL1": "#ffffff", "COL2": "#ffffff", "DIR": (1.0, 0.0)}),
        Variant("franja-rosa", "Barrido con franja rosa", "Pink band wipe", {"COL1": "#ff3d8b", "COL2": "#ff3d8b", "DIR": (-0.8, 0.6)}),
        Variant("franja-negra", "Barrido con franja negra", "Black band wipe", {"COL1": "#0b0b0f", "COL2": "#0b0b0f", "DIR": (0.0, 1.0)}),
        Variant("franja-doble", "Barrido de dos colores", "Two-colour band wipe",
                {"COL1": "#00c2ff", "COL2": "#ff5a1f", "DOUBLE": 1.0, "DIR": (0.7, -0.7)}),
    ],
)

DOORS = Family(
    key="split_doors", app_category="basic", category="movimiento", duration=1.0,
    params=[Param("gap", "Distance", 0.2, 1.5, 1.0)],
    tags=["puertas", "abrir", "dividir", "split", "doors"],
    defines={"N1": (1.0, 0.0), "N2": (0.0, 0.0), "CLOSE": 0.0},
    body=r"""
vec4 halves(vec4 bgc, vec2 P, float e, bool closeMode) {
    vec2 n1 = length(N1) > 0.0 ? normalize(N1) : vec2(0.0);
    vec2 n2 = length(N2) > 0.0 ? normalize(N2) : vec2(0.0);
    float travel = gap * 0.5 * (aspect() + 1.0);
    // Which half the moved pixel came from: its side of each split line after undoing the move.
    for (int k = 0; k < 4; ++k) {
        float s1 = (k & 1) == 0 ? 1.0 : -1.0;
        float s2 = (k & 2) == 0 ? 1.0 : -1.0;
        if (length(n2) == 0.0 && k > 1) break;
        vec2 shift = (s1 * n1 + s2 * n2) * e * travel;
        vec2 q = P - shift;
        bool ok = dot(q, n1) * s1 >= 0.0 && (length(n2) == 0.0 || dot(q, n2) * s2 >= 0.0);
        if (ok) {
            vec2 uv = fromP(q);
            if (insideUv(uv) > 0.5) {
                vec4 c = closeMode ? B(uv) : A(uv);
                float edge = min(abs(dot(q, n1)), length(n2) > 0.0 ? abs(dot(q, n2)) : 9.0);
                c.rgb *= 1.0 - 0.35 * (1.0 - smoothstep(0.0, 0.04, edge)) * step(0.001, e);
                return c;
            }
        }
    }
    return bgc;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    if (CLOSE > 0.5) {
        float e = 1.0 - easeOut(p);
        vec4 a = A(uv);
        a.rgb *= 1.0 - 0.5 * p;
        fragColor = halves(a, P, e, true);
    } else {
        float e = easeInOut(p);
        vec4 b = B(fromP(P * mix(0.9, 1.0, e)));
        b.rgb *= mix(0.5, 1.0, e);
        fragColor = halves(b, P, e, false);
    }
}
""",
    variants=[
        Variant("puertas-abrir", "Puertas que se abren", "Opening doors"),
        Variant("puertas-vertical", "Abrir hacia arriba y abajo", "Vertical doors", {"N1": (0.0, 1.0)}),
        Variant("puertas-diagonal", "Corte diagonal", "Diagonal split", {"N1": (0.6, 0.8)}),
        Variant("puertas-cuatro", "Cuatro esquinas", "Four corners", {"N1": (1.0, 0.0), "N2": (0.0, 1.0)}),
        Variant("puertas-cerrar", "Puertas que se cierran", "Closing doors", {"CLOSE": 1.0}, thumb=0.4),
    ],
)

CURTAIN = Family(
    key="curtain", app_category="cinematic", category="barridos", duration=1.6,
    params=[Param("folds", "Folds", 3.0, 20.0, 7.0)],
    tags=["telon", "cortina", "teatro", "curtain", "escenario"],
    defines={"CLOTH": "#9b0f1c"},
    body=r"""
vec4 drape(vec2 uv, float cover) {
    // Two drapes meet in the middle; each is gathered towards its outer edge as it opens.
    float x = uv.x < 0.5 ? uv.x : 1.0 - uv.x;
    float w = 0.5 * cover;
    float sway = 0.012 * sin(uv.y * 9.0 + cover * 4.0) * cover;
    float edge = w + sway;
    if (x > edge) return vec4(0.0);
    float u = x / max(edge, 0.001);
    float ph = u * folds * TAU * (0.7 + 0.3 * cover) + 0.6 * sin(uv.y * 3.0 + u * 5.0);
    float fold = 0.5 + 0.5 * cos(ph);
    vec3 c = CLOTH * (0.5 + 0.6 * pow(fold, 1.4)) + vec3(0.12) * pow(fold, 12.0);
    c *= 1.0 - 0.45 * smoothstep(0.85, 1.0, u);
    c *= 0.85 + 0.15 * (1.0 - uv.y);
    float aa = 1.0 / u_resolution.x;
    return vec4(c, 1.0 - smoothstep(edge - aa * 2.0, edge, x));
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float cover = p < 0.5 ? easeInOut(p * 2.2) : 1.0 - easeInOut((p - 0.5) * 2.2 - 0.1);
    vec4 pic = p < 0.5 ? A(uv) : B(uv);
    fragColor = over(drape(uv, cover), pic);
}
""",
    variants=[
        Variant("telon-rojo", "Telón de teatro", "Theatre curtain", thumb=0.42),
        Variant("telon-negro", "Telón negro", "Black curtain", {"CLOTH": "#2a2a33"}, thumb=0.42),
        Variant("telon-azul", "Telón azul", "Blue curtain", {"CLOTH": "#1d3fa8"}, thumb=0.42),
    ],
)

RINGS = Family(
    key="rings", app_category="geometric", category="formas", duration=1.2,
    params=[Param("rings", "Rings", 2.0, 20.0, 7.0)],
    tags=["anillos", "circulos", "ondas", "rings"],
    defines={"ORIGIN": "vec2(0.0)"},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv) - ORIGIN;
    float rmax = length(vec2(0.5 * aspect(), 0.5)) * (length(ORIGIN) > 0.01 ? 2.0 : 1.0);
    float o = length(P) / rmax;
    float k = floor(o * rings);
    float f = fract(o * rings);
    float t = sat((p * 1.5 - k / rings * 0.5));
    float dir = mod(k, 2.0) < 1.0 ? f : 1.0 - f;
    float m = step(dir, easeInOut(t));
    fragColor = mix(A(uv), B(uv), m);
}
""",
    variants=[
        Variant("anillos", "Anillos", "Rings"),
        Variant("anillos-esquina", "Anillos desde la esquina", "Rings from corner",
                {"ORIGIN": "vec2(0.5 * aspect(), -0.5)"}, params={"rings": 10.0}),
    ],
)

TRIANGLES = Family(
    key="triangles", app_category="geometric", category="formas", duration=1.2,
    params=[Param("size", "Size", 2.0, 20.0, 5.0)],
    tags=["triangulos", "triangles", "geometrico", "mosaico"],
    defines={"CENTER": 0.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 g = toP(uv) * size;
    vec2 q = vec2(g.x - g.y * 0.57735, g.y * 1.1547);
    vec2 cell = floor(q);
    vec2 f = fract(q);
    bool upper = f.x + f.y > 1.0;
    if (upper) f = 1.0 - f;
    float bmin = min(min(f.x, f.y), 1.0 - f.x - f.y);
    vec2 centre = cell + (upper ? vec2(2.0 / 3.0) : vec2(1.0 / 3.0));
    vec2 cg = vec2(centre.x + centre.y * 0.5, centre.y * 0.866) / size;
    float o = CENTER > 0.5 ? length(cg) / 1.0 : (cg.x / aspect() + 0.5) * 0.8 + hash12(cell + (upper ? 0.5 : 0.0)) * 0.2;
    float t = easeOutBack(sat((p - o * 0.6) / 0.4));
    float m = step((1.0 - t) / 3.0, bmin);
    if (p >= 0.999) m = 1.0;
    vec4 b = B(uv);
    b.rgb *= 0.9 + 0.1 * float(upper);
    fragColor = mix(A(uv), b, m);
}
""",
    variants=[
        Variant("triangulos", "Triángulos", "Triangles"),
        Variant("triangulos-centro", "Triángulos desde el centro", "Triangles from centre", {"CENTER": 1.0}, params={"size": 7.0}),
    ],
)

DOTS = Family(
    key="halftone_dots", app_category="geometric", category="formas", duration=1.1,
    params=[Param("cells", "Dots", 4.0, 40.0, 14.0)],
    tags=["puntos", "lunares", "halftone", "dots", "pop"],
    defines={"CENTER": 0.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 n = vec2(cells * aspect(), cells);
    vec2 id = floor(uv * n);
    vec2 l = (fract(uv * n) - 0.5);
    vec2 c = (id + 0.5) / n;
    float o = CENTER > 0.5 ? length(toP(c)) / 1.02 : (c.x + c.y) * 0.5;
    float t = sat(p * 1.7 - o * 0.7);
    float r = easeInOut(t) * 0.75;
    float m = 1.0 - smoothstep(r - 0.04, r + 0.04, length(l));
    if (t >= 1.0) m = 1.0;
    fragColor = mix(A(uv), B(uv), m);
}
""",
    variants=[
        Variant("puntos", "Puntos en diagonal", "Diagonal dots"),
        Variant("puntos-centro", "Puntos desde el centro", "Dots from centre", {"CENTER": 1.0}, params={"cells": 18.0}),
    ],
)

BARS = Family(
    key="bars_drop", app_category="basic", category="barridos", duration=1.0,
    params=[Param("bars", "Bars", 2.0, 30.0, 8.0)],
    tags=["barras", "caida", "bars", "cortina"],
    defines={"UP": 0.0, "COLORED": 0.0, "BARCOL": "#ff4d6d"},
    body=r"""
float cover(float x, float y, float p, float delay) {
    float i = floor(x * bars);
    float o = hash11(i * 3.1 + 1.0) * 0.3 + i / bars * 0.2;
    float t = easeOut(sat((p - o - delay) / 0.5));
    float yy = UP > 0.5 ? 1.0 - y : y;
    return step(yy, t * 1.001);
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec4 col = A(uv);
    if (COLORED > 0.5) {
        col = mix(col, vec4(BARCOL, 1.0), cover(uv.x, uv.y, p * 1.25, 0.0));
        col = mix(col, B(uv), cover(uv.x, uv.y, p * 1.25, 0.25));
    } else {
        col = mix(col, B(uv), cover(uv.x, uv.y, p, 0.0));
    }
    fragColor = col;
}
""",
    variants=[
        Variant("barras-caen", "Barras que caen", "Falling bars"),
        Variant("barras-suben", "Barras que suben", "Rising bars", {"UP": 1.0}, params={"bars": 12.0}),
        Variant("barras-color", "Barras de color", "Colour bars", {"COLORED": 1.0}, params={"bars": 6.0}),
    ],
)

DIAMONDS = Family(
    key="diamonds", app_category="geometric", category="formas", duration=1.1,
    params=[Param("cells", "Cells", 2.0, 20.0, 6.0)],
    tags=["rombos", "diamantes", "diamonds", "geometrico"],
    defines={"CENTER": 0.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 n = vec2(cells * aspect(), cells);
    vec2 id = floor(uv * n);
    vec2 l = fract(uv * n) - 0.5;
    vec2 c = (id + 0.5) / n;
    float o = CENTER > 0.5 ? length(toP(c)) / 1.02 : c.x;
    float t = easeInOut(sat(p * 1.6 - o * 0.6));
    float d = abs(l.x) + abs(l.y) - t;
    float m = fillSd(d, 0.02);
    if (t >= 1.0) m = 1.0;
    fragColor = mix(A(uv), B(uv), m);
}
""",
    variants=[
        Variant("rombos", "Rombos", "Diamonds"),
        Variant("rombos-centro", "Rombos desde el centro", "Diamonds from centre", {"CENTER": 1.0}, params={"cells": 9.0}),
    ],
)

ZIGZAG = Family(
    key="zigzag", app_category="basic", category="barridos", params=[SOFT], duration=0.9,
    tags=["zigzag", "dientes", "barrido", "sierra"],
    defines={"VERTICAL": 0.0, "TEETH": 9.0, "AMP": 0.06},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float along = VERTICAL > 0.5 ? uv.y : uv.x;
    float across = VERTICAL > 0.5 ? uv.x : uv.y;
    float tri = abs(fract(across * TEETH) - 0.5) * 2.0;
    float e = mix(-AMP, 1.0 + AMP, easeInOut(p));
    float edge = e + (tri - 0.5) * AMP * 2.0;
    float m = 1.0 - smoothstep(edge - softness - 0.002, edge + softness + 0.002, along);
    fragColor = mix(A(uv), B(uv), m);
}
""",
    variants=[
        Variant("zigzag", "Zigzag", "Zigzag wipe"),
        Variant("zigzag-vertical", "Zigzag vertical", "Vertical zigzag", {"VERTICAL": 1.0, "TEETH": 14.0, "AMP": 0.08}),
    ],
)

BRUSH = Family(
    key="brush_strokes", app_category="liquid", category="barridos", duration=1.2,
    params=[Param("strokes", "Strokes", 2.0, 10.0, 4.0)],
    tags=["pincel", "pintura", "brocha", "brush", "pintado a mano"],
    defines={"PAINT": 0.0, "PAINTC": "#f2e8d5"},
    body=r"""
float stroke(vec2 uv, float p, float delay) {
    float y = uv.y * strokes;
    float i = floor(y);
    float f = fract(y);
    float dir = mod(i, 2.0) < 1.0 ? 1.0 : -1.0;
    float x = dir > 0.0 ? uv.x : 1.0 - uv.x;
    float t = easeInOut(sat((p - delay - i / strokes * 0.45) / 0.55));
    float rough = (fbm(vec2(uv.x * 6.0, i * 3.7)) - 0.5) * 0.22;
    float bristle = (fbm(vec2(uv.x * 2.0 + i, f * 30.0)) - 0.5) * 0.08;
    float head = t * 1.25 - 0.1 + (fbm(vec2(f * 5.0, i)) - 0.5) * 0.12;
    float body = step(abs(f - 0.5), 0.62 + rough);
    return step(x + bristle, head) * body;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec4 col = A(uv);
    if (PAINT > 0.5) {
        float s1 = stroke(uv, p * 1.2, 0.0);
        vec3 pc = PAINTC * (0.9 + 0.1 * fbm(uv * vec2(40.0, 4.0)));
        col = mix(col, vec4(pc, 1.0), s1);
        col = mix(col, B(uv), stroke(uv, p * 1.2, 0.25));
    } else {
        col = mix(col, B(uv), stroke(uv, p, 0.0));
    }
    fragColor = col;
}
""",
    variants=[
        Variant("pinceladas", "Pinceladas", "Brush strokes"),
        Variant("pinceladas-pintura", "Pintura y pinceladas", "Paint strokes", {"PAINT": 1.0}, params={"strokes": 5.0}),
    ],
)

CLOUD = Family(
    key="cloud_wipe", app_category="liquid", category="barridos", params=[SOFT], duration=1.2,
    tags=["nube", "humo", "suave", "noise", "organico"],
    defines={"DIR": (1.0, 0.0), "CENTER": 0.0, "SCALE": 3.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float s = CENTER > 0.5 ? 1.0 - length(P) / 1.02 : dot(uv - 0.5, normalize(DIR)) * -1.0 + 0.5;
    float n = fbm(P * SCALE + 3.0);
    float v = s * 0.65 + n * 0.35;
    float t = mix(-0.05, 1.05, easeInOut(p));
    float m = smoothstep(1.0 - t - softness - 0.03, 1.0 - t + softness + 0.03, v);
    fragColor = mix(A(uv), B(uv), m);
}
""",
    variants=[
        Variant("nube-barrido", "Barrido de nubes", "Cloud wipe", params={"softness": 0.03}),
        Variant("nube-centro", "Nubes desde el centro", "Clouds from centre", {"CENTER": 1.0}, params={"softness": 0.02}),
        Variant("degradado-suave", "Barrido suave", "Soft gradient wipe", {"SCALE": 0.6, "DIR": (0.7, 0.7)},
                params={"softness": 0.15}),
    ],
)

MOSAIC = Family(
    key="mosaic_flash", app_category="glitch", category="formas", duration=1.0,
    params=[Param("cells", "Cells", 3.0, 40.0, 12.0)],
    tags=["mosaico", "pixeles", "cuadros", "aparecer", "pixel"],
    defines={"CENTER": 0.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 n = vec2(floor(cells * aspect() + 0.5), cells);
    vec2 id = floor(uv * n);
    vec2 c = (id + 0.5) / n;
    float o = CENTER > 0.5 ? length(toP(c)) / 1.02 * 0.8 + hash12(id) * 0.2 : hash12(id + 9.0);
    float t = sat((p - o * 0.75) / 0.25);
    vec4 col = mix(A(uv), B(uv), step(0.5, t));
    // Each square lights up the moment it turns over.
    col.rgb += vec3(0.45) * bump(t);
    fragColor = vec4(min(col.rgb, 1.0), col.a);
}
""",
    variants=[
        Variant("mosaico", "Mosaico al azar", "Random mosaic"),
        Variant("mosaico-centro", "Mosaico desde el centro", "Mosaic from centre", {"CENTER": 1.0}, params={"cells": 16.0}),
    ],
)

FAMILIES = [IRIS, SLATS, TILES, CHECKER, STRIPES, CLOCK, SPIRAL, BAND, DOORS, CURTAIN, RINGS, TRIANGLES, DOTS, BARS,
            DIAMONDS, ZIGZAG, BRUSH, CLOUD, MOSAIC]
