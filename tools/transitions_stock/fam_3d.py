"""3D and paper transitions: page curls, cubes, flips, doors, folds and broken glass."""

from kit import Family, Param, Variant

BG = r"""
const vec4 STAGE = vec4(0.045, 0.045, 0.055, 1.0);
"""

CURL = Family(
    key="page_curl", app_category="modern", category="3d", duration=1.4,
    params=[Param("radius", "Curl Radius", 0.03, 0.3, 0.12)],
    tags=["pagina", "pasar pagina", "libro", "page curl", "papel"],
    defines={"DIR": (1.0, 0.0)},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 d = normalize(DIR);
    vec2 P = toP(uv);
    // u runs along DIR; the page's free edge is at umax and it curls back towards umin.
    vec2 half_ = vec2(0.5 * aspect(), 0.5);
    float umax = abs(d.x) * half_.x + abs(d.y) * half_.y;
    float umin = -umax;
    float u = dot(P, d);
    float R = radius;
    float c = mix(umax, umin - PI * R, easeInOut(p));
    vec4 col;
    // 1. The part of the page lying flat on its back, on top of everything.
    float u0 = 2.0 * c + PI * R - u;
    vec2 P0 = P + d * (u0 - u);
    if (u < c && u0 <= umax && insideUv(fromP(P0)) > 0.5) {
        vec4 back = A(fromP(P0));
        back.rgb = mix(back.rgb, vec3(0.96), 0.72) * (0.85 + 0.15 * sat((c - u) / R));
        fragColor = back;
        return;
    }
    // 2. Around the cylinder: its top (the back of the page) hides its bottom (the front).
    if (u >= c && u <= c + R) {
        float s = asin(sat((u - c) / R));
        float aTop = R * (PI - s);
        float aBot = R * s;
        float uTop = c + aTop, uBot = c + aBot;
        vec2 Pt = P + d * (uTop - u), Pb = P + d * (uBot - u);
        if (uTop <= umax && insideUv(fromP(Pt)) > 0.5) {
            vec4 back = A(fromP(Pt));
            back.rgb = mix(back.rgb, vec3(0.96), 0.72) * (0.7 + 0.3 * cos(s));
            fragColor = back;
            return;
        }
        if (uBot <= umax && insideUv(fromP(Pb)) > 0.5) {
            vec4 front = A(fromP(Pb));
            front.rgb *= 0.75 + 0.25 * cos(s);
            fragColor = front;
            return;
        }
    }
    // 3. The flat front of the page that has not curled yet, then the incoming picture with a shadow.
    if (u < c) {
        col = A(uv);
        col.rgb *= 1.0 - 0.25 * (1.0 - smoothstep(0.0, R, c - u)) * step(0.001, p);
        fragColor = col;
        return;
    }
    col = B(uv);
    col.rgb *= 1.0 - 0.55 * exp(-(u - c - R) / (R * 0.8));
    fragColor = col;
}
""",
    variants=[
        Variant("pasar-pagina", "Pasar página", "Page turn", thumb=0.45),
        Variant("pasar-pagina-esquina", "Pasar página desde la esquina", "Page curl from corner", {"DIR": (0.75, 0.66)}, thumb=0.45),
        Variant("pasar-pagina-arriba", "Pasar página desde arriba", "Page curl from top corner", {"DIR": (0.75, -0.66)}, thumb=0.45),
        Variant("pasar-pagina-izquierda", "Pasar página hacia la derecha", "Page turn to the right", {"DIR": (-1.0, 0.0)}, thumb=0.45),
    ],
)

TEAR = Family(
    key="paper_tear", app_category="modern", category="3d", duration=1.2,
    params=[Param("rough", "Tear Roughness", 0.0, 1.0, 0.5)],
    tags=["papel", "rasgar", "romper", "tear", "papel roto"],
    defines={"VERTICAL": 0.0},
    body=r"""
float tearLine(float x) {
    return 0.5 + (fbm(vec2(x * 5.0, 3.0)) - 0.5) * 0.18 * (0.4 + rough) + (vnoise(vec2(x * 60.0, 1.0)) - 0.5) * 0.02 * rough;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 q = VERTICAL > 0.5 ? uv.yx : uv;
    float e = easeIn(p);
    float off = e * 0.75;
    float ang = e * 0.25;
    vec4 col;
    // Top piece: up and turned a little; bottom piece: down and turned the other way.
    vec2 c1 = vec2(0.0, 0.0);
    vec2 t1 = c1 + rot(-ang) * (q - c1) + vec2(0.0, off);
    vec2 c2 = vec2(1.0, 1.0);
    vec2 t2 = c2 + rot(-ang) * (q - c2) - vec2(0.0, off);
    float fiber = 0.012 + 0.01 * rough;
    vec4 back = (VERTICAL > 0.5) ? B(fromP(toP(uv) * mix(0.92, 1.0, e))) : B(fromP(toP(uv) * mix(0.92, 1.0, e)));
    back.rgb *= mix(0.6, 1.0, e);
    col = back;
    float l1 = tearLine(t1.x);
    if (insideUv(t1) > 0.5 && t1.y < l1) {
        vec2 s = VERTICAL > 0.5 ? t1.yx : t1;
        col = A(s);
        float edge = smoothstep(l1 - fiber, l1 - fiber * 0.3, t1.y);
        col.rgb = mix(col.rgb, vec3(0.97, 0.96, 0.93), edge);
    }
    float l2 = tearLine(t2.x);
    if (insideUv(t2) > 0.5 && t2.y > l2) {
        vec2 s = VERTICAL > 0.5 ? t2.yx : t2;
        col = A(s);
        float edge = 1.0 - smoothstep(l2 + fiber * 0.3, l2 + fiber, t2.y);
        col.rgb = mix(col.rgb, vec3(0.97, 0.96, 0.93), edge);
    }
    fragColor = col;
}
""",
    variants=[
        Variant("papel-rasgado", "Papel que se rasga", "Paper rip", thumb=0.45),
        Variant("papel-rasgado-vertical", "Papel rasgado vertical", "Vertical paper rip", {"VERTICAL": 1.0}, thumb=0.45),
    ],
)

CUBE = Family(
    key="cube", app_category="modern", category="3d", duration=1.1,
    params=[Param("zoom", "Pull Back", 0.0, 1.0, 0.4)],
    tags=["cubo", "3d", "girar", "cube", "rotar"],
    defines={"VERT": 0.0, "SIGN": 1.0},
    body=BG + r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float a = aspect();
    // A box whose front shows the outgoing picture and whose side shows the incoming one,
    // turned a quarter round. Depth equals the side that turns, so both faces keep their shape.
    float depth = VERT > 0.5 ? 1.0 : a;
    vec3 hs = vec3(a * 0.5, 0.5, depth * 0.5);
    float f = 2.2;
    float cam = depth * 0.5 + f;
    float th = easeInOut(p) * PI * 0.5 * SIGN;
    float push = zoom * bump(p) * 0.9;
    vec3 ro = vec3(0.0, 0.0, -cam - push);
    vec3 rd = normalize(vec3(P, f));
    // Into box space.
    mat2 r = rot(th);
    if (VERT > 0.5) { ro.yz = r * ro.yz; rd.yz = r * rd.yz; }
    else { ro.xz = r * ro.xz; rd.xz = r * rd.xz; }
    vec3 inv = 1.0 / rd;
    vec3 t0 = (-hs - ro) * inv, t1 = (hs - ro) * inv;
    vec3 tmin = min(t0, t1), tmax = max(t0, t1);
    float tn = max(max(tmin.x, tmin.y), tmin.z);
    float tf = min(min(tmax.x, tmax.y), tmax.z);
    if (tn > tf || tf < 0.0) { fragColor = STAGE; return; }
    vec3 h = ro + rd * tn;
    vec3 nrm = abs(h / hs);
    vec4 col = STAGE;
    float shade = 1.0;
    if (nrm.z >= nrm.x && nrm.z >= nrm.y) {
        if (h.z < 0.0) col = A(vec2(h.x / a + 0.5, h.y + 0.5));
        shade = abs(cos(th));
    } else if (VERT < 0.5) {
        col = B(vec2(sign(h.x) * h.z / a + 0.5, h.y + 0.5));
        shade = abs(sin(th));
    } else {
        col = B(vec2(h.x / a + 0.5, sign(h.y) * h.z + 0.5));
        shade = abs(sin(th));
    }
    col.rgb *= 0.35 + 0.65 * shade;
    fragColor = col;
}
""",
    variants=[
        Variant("cubo-derecha", "Cubo hacia la derecha", "Cube right", thumb=0.5),
        Variant("cubo-izquierda", "Cubo hacia la izquierda", "Cube left", {"SIGN": -1.0}, thumb=0.5),
        Variant("cubo-abajo", "Cubo hacia abajo", "Cube down", {"VERT": 1.0}, thumb=0.5),
        Variant("cubo-arriba", "Cubo hacia arriba", "Cube up", {"VERT": 1.0, "SIGN": -1.0}, thumb=0.5),
    ],
)

FLIP = Family(
    key="flip_card", app_category="modern", category="3d", duration=1.0,
    params=[Param("zoom", "Pull Back", 0.0, 1.0, 0.5)],
    tags=["voltear", "tarjeta", "girar", "flip", "3d"],
    defines={"VERT": 0.0},
    body=BG + r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float a = aspect();
    float f = 2.2;
    float th = easeInOut(p) * PI;
    vec3 ro = vec3(0.0, 0.0, -f - zoom * bump(p));
    vec3 rd = normalize(vec3(P, f));
    mat2 r = rot(th);
    if (VERT > 0.5) { ro.yz = r * ro.yz; rd.yz = r * rd.yz; }
    else { ro.xz = r * ro.xz; rd.xz = r * rd.xz; }
    if (abs(rd.z) < 1e-5) { fragColor = STAGE; return; }
    float t = -ro.z / rd.z;
    vec3 h = ro + rd * t;
    vec2 q = vec2(h.x / a + 0.5, h.y + 0.5);
    if (t < 0.0 || insideUv(q) < 0.5) { fragColor = STAGE; return; }
    bool front = ro.z < 0.0;
    vec4 col;
    if (front) col = A(q);
    else col = VERT > 0.5 ? B(vec2(q.x, 1.0 - q.y)) : B(vec2(1.0 - q.x, q.y));
    col.rgb *= 0.45 + 0.55 * abs(cos(th));
    fragColor = col;
}
""",
    variants=[
        Variant("voltear", "Voltear", "Flip", thumb=0.35),
        Variant("voltear-vertical", "Voltear vertical", "Vertical flip", {"VERT": 1.0}, thumb=0.35),
    ],
)

DOORS3D = Family(
    key="doors_3d", app_category="modern", category="3d", duration=1.3,
    params=[Param("angle", "Swing", 0.5, 1.0, 0.95)],
    tags=["puertas", "3d", "abrir", "ventana", "doors"],
    defines={"CLOSE": 0.0},
    body=BG + r"""
// A door hinged at x = side * h, swung towards the camera by th. Solves the projection for the
// point of the door under this pixel; returns its colour, or alpha 0 when the door is not there.
vec4 leaf(vec2 S, float side, float th, bool useB, float f, out float depth) {
    float h = aspect() * 0.5;
    depth = 9.0;
    float den = f * cos(th) - side * S.x * sin(th);
    if (den <= 1e-4) return vec4(0.0);
    float w = f * (h - side * S.x) / den;
    if (w < 0.0 || w > h) return vec4(0.0);
    float z = -w * sin(th);
    float y = S.y * (f + z) / f;
    if (abs(y) > 0.5) return vec4(0.0);
    float x = side * (h - w);
    vec2 q = vec2(x / aspect() + 0.5, y + 0.5);
    vec4 c = useB ? B(q) : A(q);
    c.rgb *= 0.55 + 0.45 * cos(th);
    depth = z;
    return c;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 S = toP(uv);
    float f = 2.0;
    float e = CLOSE > 0.5 ? 1.0 - easeInOut(p) : easeInOut(p);
    float th = e * angle * PI * 0.5;
    bool doorB = CLOSE > 0.5;
    float dl, dr;
    vec4 l = leaf(S, -1.0, th, doorB, f, dl);
    vec4 r = leaf(S, 1.0, th, doorB, f, dr);
    vec4 back = doorB ? A(uv) : B(fromP(S * mix(0.85, 1.0, e)));
    back.rgb *= doorB ? mix(1.0, 0.45, 1.0 - e) : mix(0.45, 1.0, e);
    vec4 col = back;
    if (l.a > 0.0 && (r.a <= 0.0 || dl < dr)) col = over(l, col);
    else if (r.a > 0.0) col = over(r, col);
    fragColor = col;
}
""",
    variants=[
        Variant("puertas-3d", "Puertas 3D", "3D doors", thumb=0.5),
        Variant("puertas-3d-cerrar", "Puertas 3D que se cierran", "Closing 3D doors", {"CLOSE": 1.0}, thumb=0.5),
    ],
)

ACCORDION = Family(
    key="accordion", app_category="modern", category="3d", duration=1.2,
    params=[Param("depth", "Depth", 0.0, 0.4, 0.15)],
    tags=["acordeon", "origami", "pliegue", "doblar", "fold", "papel"],
    defines={"N": 4.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float th = easeInOut(p) * 1.53;
    float w = cos(th) / N;
    float W = w * N;
    vec4 b = B(fromP(toP(uv) * mix(0.9, 1.0, p)));
    b.rgb *= mix(0.55, 1.0, p);
    if (uv.x > W || W < 0.002) { fragColor = b; return; }
    float i = floor(uv.x / w);
    float f = fract(uv.x / w);
    bool even = mod(i, 2.0) < 1.0;
    // Alternate panels lean away and towards the light; the far crease is smaller.
    float far = even ? f : 1.0 - f;
    float sy = 1.0 - depth * sin(th) * far;
    float y = 0.5 + (uv.y - 0.5) / sy;
    if (y < 0.0 || y > 1.0) { fragColor = b; return; }
    vec4 col = A(vec2((i + f) / N, y));
    col.rgb *= even ? 1.0 - 0.15 * sin(th) : 1.0 - 0.6 * sin(th);
    fragColor = col;
}
""",
    variants=[
        Variant("acordeon", "Acordeón", "Accordion fold", thumb=0.5),
        Variant("origami", "Origami", "Origami fold", {"N": 7.0}, params={"depth": 0.22}, thumb=0.5),
    ],
)

SHATTER = Family(
    key="glass_shatter", app_category="modern", category="3d", duration=1.4,
    params=[Param("pieces", "Pieces", 3.0, 12.0, 6.0)],
    tags=["cristal", "vidrio", "romper", "shatter", "pedazos"],
    defines={"FALL": 0.0},
    body=r"""
vec2 seed(vec2 id) { return id + 0.15 + 0.7 * hash22(id); }
// Which cell of the jittered grid a point of the original picture belongs to.
vec2 cellOf(vec2 g) {
    vec2 b = floor(g);
    vec2 best = b;
    float bd = 9.0;
    for (int y = -1; y <= 1; ++y)
        for (int x = -1; x <= 1; ++x) {
            vec2 id = b + vec2(float(x), float(y));
            float d = length(g - seed(id));
            if (d < bd) { bd = d; best = id; }
        }
    return best;
}
float edgeDist(vec2 g) {
    vec2 b = floor(g);
    float d1 = 9.0, d2 = 9.0;
    for (int y = -1; y <= 1; ++y)
        for (int x = -1; x <= 1; ++x) {
            float d = length(g - seed(b + vec2(float(x), float(y))));
            if (d < d1) { d2 = d1; d1 = d; } else if (d < d2) d2 = d;
        }
    return d2 - d1;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 n = vec2(pieces * aspect(), pieces);
    float crack = sat(p / 0.2);
    float t = sat((p - 0.18) / 0.82);
    vec4 b = B(uv);
    b.rgb *= mix(0.6, 1.0, t);
    vec4 col = b;
    vec2 gp = uv * n;
    // Try the pieces that could have moved over this pixel.
    for (int y = -3; y <= 2; ++y)
        for (int x = -2; x <= 2; ++x) {
            vec2 id = floor(gp) + vec2(float(x), float(y));
            vec2 c = seed(id) / n;   // piece centre in uv
            float h = hash12(id + 7.0);
            float delay = FALL > 0.5 ? (1.0 - c.y) * 0.4 + h * 0.15 : length(c - 0.5) * 0.3 + h * 0.1;
            float k = sat((t - delay) / (1.0 - delay * 0.8));
            vec2 move = FALL > 0.5 ? vec2((h - 0.5) * 0.15 * k, 1.4 * k * k)
                                   : (c - 0.5) * (0.9 * k) + vec2(0.0, 0.6 * k * k);
            float spin = (h - 0.5) * 3.0 * k;
            float sc = FALL > 0.5 ? 1.0 : 1.0 + 0.5 * k;
            vec2 local = (uv - c - move) * vec2(aspect(), 1.0);
            local = rot(-spin) * local / sc;
            vec2 src = c + local / vec2(aspect(), 1.0);
            if (insideUv(src) < 0.5) continue;
            vec2 cell = cellOf(src * n);
            if (cell != id) continue;
            vec4 a = A(src);
            float e = edgeDist(src * n);
            a.rgb += vec3(0.5) * (1.0 - smoothstep(0.0, 0.08, e)) * crack * (1.0 - k);
            a.rgb *= 1.0 - 0.25 * k + 0.25 * sin(spin + h * 6.0) * k;
            col = vec4(a.rgb, a.a * (1.0 - smoothstep(0.75, 1.0, k)));
            col = over(col, b);
        }
    fragColor = col;
}
""",
    variants=[
        Variant("cristal-roto", "Cristal roto", "Shattered glass", thumb=0.45),
        Variant("cristal-cae", "Cristal que cae", "Falling glass", {"FALL": 1.0}, thumb=0.45),
    ],
)

TILT = Family(
    key="tilt_slide", app_category="modern", category="3d", duration=1.1,
    params=[Param("tilt", "Tilt", 0.0, 1.2, 0.7)],
    tags=["perspectiva", "inclinar", "deslizar", "3d", "tilt"],
    defines={"SIDE": 0.0},
    body=r"""
const vec4 STAGE = vec4(0.045, 0.045, 0.055, 1.0);
vec4 plane(vec2 P, float th, vec2 shift, bool useB) {
    // A picture on a plane tipped back by th about its centre line, moved by shift.
    float f = 2.0;
    vec3 rd = normalize(vec3(P, f));
    vec3 ro = vec3(-shift, -f);
    mat2 r = rot(th);
    if (SIDE > 0.5) { ro.xz = r * ro.xz; rd.xz = r * rd.xz; }
    else { ro.yz = r * ro.yz; rd.yz = r * rd.yz; }
    if (abs(rd.z) < 1e-5) return vec4(0.0);
    float t = -ro.z / rd.z;
    if (t < 0.0) return vec4(0.0);
    vec3 h = ro + rd * t;
    vec2 q = vec2(h.x / aspect() + 0.5, h.y + 0.5);
    vec4 c = useB ? Bc(q) : Ac(q);
    c.rgb *= 0.6 + 0.4 * cos(th);
    return c;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float e = easeInOut(p);
    vec2 dir = SIDE > 0.5 ? vec2(-aspect() * 1.3, 0.0) : vec2(0.0, -1.3);
    vec4 a = plane(P, tilt * sin(e * PI * 0.5), dir * e, false);
    vec4 b = plane(P, -tilt * cos(e * PI * 0.5), -dir * (1.0 - e), true);
    fragColor = over(b, over(a, STAGE));
}
""",
    variants=[
        Variant("perspectiva-arriba", "Deslizar en perspectiva", "Perspective slide"),
        Variant("perspectiva-lateral", "Deslizar en perspectiva lateral", "Sideways perspective slide", {"SIDE": 1.0}),
    ],
)

LENS = Family(
    key="lens_warp", app_category="modern", category="3d", duration=0.9,
    params=[Param("strength", "Strength", 0.0, 1.5, 1.0)],
    tags=["lente", "ojo de pez", "burbuja", "fisheye", "deformar"],
    defines={"SIGN": 1.0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float r = length(P);
    float k = bump(p) * strength * SIGN;
    // Bulge (SIGN 1) or pinch (SIGN -1) the picture towards a sphere, swap at the peak.
    float m = 1.0 - k * 0.9 * (1.0 - smoothstep(0.0, 0.9, r));
    vec2 q = fromP(P * m);
    vec4 col = mix(A(q), B(q), smoothstep(0.42, 0.58, p));
    col.rgb *= 1.0 - 0.25 * abs(k) * smoothstep(0.3, 1.0, r);
    fragColor = col;
}
""",
    variants=[
        Variant("lupa", "Lupa", "Bulge"),
        Variant("pellizco", "Pellizco", "Pinch", {"SIGN": -1.0}),
    ],
)

MIRRORS = Family(
    key="mirror_tiles", app_category="geometric", category="3d", duration=1.1,
    params=[Param("tiles", "Tiles", 2.0, 6.0, 3.0)],
    tags=["espejo", "mosaico", "caleidoscopio", "repetir", "mirror"],
    body=r"""
vec2 mirrorUv(vec2 u) { return 1.0 - abs(1.0 - mod(u, 2.0)); }
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    // The picture shrinks into a wall of mirrored copies, the incoming one grows out of it.
    float k = bump(p);
    float s = 1.0 + (tiles - 1.0) * easeInOut(k);
    vec2 q = mirrorUv(0.5 + (uv - 0.5) * s);
    vec4 col = p < 0.5 ? A(q) : B(q);
    vec2 cell = fract((uv - 0.5) * s + 0.5);
    float gap = (1.0 - smoothstep(0.0, 0.02 * s, min(min(cell.x, 1.0 - cell.x), min(cell.y, 1.0 - cell.y)))) * k;
    col.rgb *= 1.0 - 0.6 * gap;
    fragColor = col;
}
""",
    variants=[Variant("espejos", "Mosaico de espejos", "Mirror tiles")],
)

FAMILIES = [CURL, TEAR, CUBE, FLIP, DOORS3D, ACCORDION, SHATTER, TILT, LENS, MIRRORS]
