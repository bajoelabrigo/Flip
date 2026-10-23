"""Efectos › Tendencias: Marcos y bordes (category "marcos").

Instant-photo frames and photobook pages (the picture inside a paper card that sways), light running along the
border, echo frames, fire, edge lines, grunge scribbles, manga speed lines, music bars and rings, a grey grid.
"""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)

# Signed distance to a rectangle's outline and the position along it (0..1, clockwise from the top-left corner).
PERIM = r"""
float perim(vec2 p, vec2 h) {
    float L = 4.0 * (h.x + h.y);
    float dx = h.x - abs(p.x), dy = h.y - abs(p.y);
    float s;
    if (dy < dx) {
        float x = clamp(p.x, -h.x, h.x);
        s = p.y < 0.0 ? x + h.x : 2.0 * h.x + 2.0 * h.y + (h.x - x);
    } else {
        float y = clamp(p.y, -h.y, h.y);
        s = p.x > 0.0 ? 2.0 * h.x + (y + h.y) : 4.0 * h.x + 2.0 * h.y + (h.y - y);
    }
    return s / L;
}
"""

# ---------------------------------------------------------------------------------------------------------------
# The picture inside a paper card (instant photo, photobook page, sticky notes): blurred or paper background,
# soft shadow, optional tape and torn edge, cards behind, a camera flash that develops the photo.
CARD = Family(
    key="marcos_card", category="marcos",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#f6f4ef"), Param("size", "Size", 0.3, 1.0, 0.84),
            Param("width", "Width", 0.0, 3.0, 1.0), Param("angle", "Angle", -30.0, 30.0, 0.0),
            Param("rotation", "Rotation", 0.0, 10.0, 2.0), Param("blur", "Blur", 0.0, 3.0, 1.0),
            Param("brightness", "Brightness", 0.0, 1.0, 0.42)],
    photo="woman", tags=["marco", "frame", "polaroid", "foto instantanea", "instant photo", "papel", "paper"],
    defines={"FA": 0.5625, "SIDE": 0.06, "BOTTOM": 0.0, "TAPE": 0.0, "TORN": 0.0, "BG": 0.0,
             "BACK": 0.0, "FLASH": 0.0, "NOTES": 0.0, "PULSE": 0.0, "ROUND": 0.0},
    body=PERIM + r"""
vec2 cardHalf(float size) {
    float fa = FA > 0.0 ? FA : aspect();
    vec2 lim = vec2(aspect() * 0.5, 0.5) * size;
    float h = lim.y, w = h * fa;
    if (w > lim.x) { w = lim.x; h = w / fa; }
    return vec2(w, h);
}

// The card in its own space q (unrotated). rgb + coverage.
vec4 card(vec2 q, vec2 hs, float seed, float zoom, vec2 shift, float develop) {
    float m = 2.0 * min(hs.x, hs.y);
    float b = SIDE * width * m, eb = BOTTOM * width * m;
    float aa = 1.2 / u_resolution.y;
    float bottom = hs.y;
    if (TORN > 0.5) bottom -= 0.006 + (vnoise(vec2(q.x * 70.0, seed)) - 0.5) * 0.014
                             + (vnoise(vec2(q.x * 260.0, seed + 4.0)) - 0.5) * 0.006;
    float d = max(max(abs(q.x) - hs.x, -q.y - hs.y), q.y - bottom);
    if (ROUND > 0.0) d = max(d, sdRoundBox(q, hs, ROUND * m));
    float cover = 1.0 - smoothstep(-aa, aa, d);
    vec2 ic = vec2(0.0, -eb * 0.5);
    vec2 ih = hs - vec2(b, b + eb * 0.5);
    float dIn = sdBox(q - ic, ih);
    if (ROUND > 0.0) dIn = sdRoundBox(q - ic, ih, ROUND * m * 0.6);
    float win = 1.0 - smoothstep(-aa, aa, dIn);
    float ia = ih.x / ih.y;
    vec2 reg = ia >= aspect() ? vec2(1.0, aspect() / ia) : vec2(ia / aspect(), 1.0);
    vec2 uv = 0.5 + shift + (q - ic) / (2.0 * ih) * reg / zoom;
    vec3 pic = S(clamp(uv, 0.001, 0.999)).rgb;
    pic = mix(vec3(0.86, 0.85, 0.80), pic, develop);
    pic *= 0.82 + 0.18 * smoothstep(0.0, 0.012, -dIn);          // a soft inner shadow at the window
    vec3 pap = color * (0.95 + 0.05 * vnoise(q * 420.0 + seed));
    pap *= 1.0 - 0.06 * smoothstep(0.0, 0.03, -d) * 0.0 - 0.05 * (q.y / hs.y);
    return vec4(mix(pap, pic, win), cover);
}

float cardShadow(vec2 q, vec2 hs) {
    float d = sdBox(q - vec2(0.012, 0.02), hs);
    return 0.55 * exp(-max(d, 0.0) / 0.025) * smoothstep(0.06, -0.02, d);
}

vec4 tape(vec2 q, vec2 c, float a, vec2 hs) {
    vec2 r = rot(-a) * (q - c);
    float ends = (vnoise(vec2(r.y * 180.0, c.x * 9.0)) - 0.5) * 0.008;
    float d = max(abs(r.x) - hs.x - ends, abs(r.y) - hs.y);
    float m = 1.0 - smoothstep(-0.0015, 0.0015, d);
    vec3 col = vec3(0.86, 0.85, 0.80) * (0.93 + 0.07 * vnoise(r * 300.0));
    return vec4(col, m * 0.78);
}

vec4 note(vec2 p, vec2 c, float a, float r, vec3 tint, float t) {
    vec2 q = rot(-a) * (p - c);
    float d = sdBox(q, vec2(r));
    float m = 1.0 - smoothstep(-0.0015, 0.0015, d);
    float lift = 0.5 + 0.5 * sin(t * 2.3 + c.x * 7.0);
    float curl = smoothstep(-r, r, q.y) * (0.75 + 0.2 * lift);   // the free edge bends toward the light
    vec3 col = tint * (1.02 - 0.18 * curl * curl);
    col *= 1.0 - 0.25 * smoothstep(-r, -r * 0.7, q.y) * 0.0;
    col = mix(col * 0.82, col, smoothstep(-r, -r + 0.03, q.y));    // the glued strip
    return vec4(col, m);
}

void main() {
    vec2 uv = v_texCoord;
    vec2 p = toP(uv);
    float t = u_time * speed;
    float k = intensity;

    vec3 bg;
    if (BG < 0.5) bg = discBlur(uv, 0.06 * blur).rgb * brightness;
    else if (BG < 1.5) bg = vec3(0.86, 0.86, 0.84) * (0.9 + 0.1 * vnoise(p * 6.0)) * (0.92 + 0.08 * vnoise(p * 300.0));
    else bg = discBlur(uv, 0.01 * blur).rgb * brightness;
    bg *= mix(1.0, vignette(uv, 0.35, 0.5), 0.5);

    float sc = mix(0.9, 1.0, easeOutBack(u_time / 0.5));
    if (PULSE > 0.5) sc *= 1.0 - 0.08 * beat(u_time, 0.5, 0.22) * k - 0.02 * wave01(t, 4.0);
    vec2 hs = cardHalf(size) * sc;
    float ang = radians(angle) + radians(rotation) * k * sin(t * 1.25);
    vec2 off = vec2(0.010 * sin(t * 0.9), 0.008 * sin(t * 1.1 + 1.0)) * k;
    vec3 col = bg;

    // Cards behind (photobook pages): their own crop of the picture, turned the other way.
    for (int i = 0; i < 2; ++i) {
        if (float(i) >= BACK) break;
        float fi = float(i);
        float a2 = (i == 0 ? -0.16 : 0.13) + 0.03 * sin(t * 0.8 + fi * 2.0) * k;
        vec2 c2 = vec2(i == 0 ? -0.22 : 0.24, i == 0 ? -0.04 : 0.06) * vec2(aspect(), 1.0) * 0.55
                  + vec2(0.012 * sin(t * 0.7 + fi), 0.0) * k;
        vec2 h2 = hs * 0.82;
        vec2 q2 = rot(-a2) * (p - c2);
        col *= 1.0 - cardShadow(q2, h2) * 0.8;
        vec4 c = card(q2, h2, 3.0 + fi, 1.1, vec2(i == 0 ? -0.12 : 0.12, 0.03), 1.0);
        col = mix(col, c.rgb * 0.9, c.a);
    }

    float develop = 1.0;
    if (FLASH > 0.5) develop = easeInOut((phase(u_time, 3.0) - 0.05) / 0.9);
    vec2 q = rot(-ang) * (p - off);
    col *= 1.0 - cardShadow(q, hs);
    float zoom = 1.0 + 0.04 * wave01(t, 6.0);
    vec4 c = card(q, hs, 1.0, zoom, vec2(0.0), develop);
    col = mix(col, c.rgb, c.a);

    if (TAPE > 0.5) {
        float m = 2.0 * min(hs.x, hs.y);
        vec4 tp = tape(q, vec2(0.0, -hs.y + 0.004), -0.05, vec2(0.16, 0.045) * m);
        col = mix(col, tp.rgb, tp.a);
    }
    if (NOTES > 0.5) {
        float r = 0.07;
        vec4 n1 = note(p, vec2(-hs.x + 0.01, -hs.y + 0.03) + off, -0.25, r, vec3(1.0, 0.86, 0.32), t);
        vec4 n2 = note(p, vec2(hs.x - 0.02, hs.y - 0.06) + off, 0.18, r * 0.9, vec3(1.0, 0.55, 0.68), t + 1.7);
        vec4 n3 = note(p, vec2(hs.x - 0.01, -hs.y + 0.05) + off, 0.3, r * 0.8, vec3(0.5, 0.86, 0.95), t + 3.1);
        col *= 1.0 - 0.35 * (1.0 - smoothstep(0.0, 0.03, sdBox(rot(0.25) * (p - vec2(-hs.x + 0.02, -hs.y + 0.045) - off), vec2(r))));
        col = mix(col, n1.rgb, n1.a);
        col = mix(col, n2.rgb, n2.a);
        col = mix(col, n3.rgb, n3.a);
    }
    if (FLASH > 0.5) col = mix(col, vec3(1.0), 0.85 * beat(u_time, 3.0, 0.12) * sat(k));
    fragColor = vec4(col, 1.0);
}
""",
    variants=[
        Variant("marco-instantaneo-stories-03-9-16", "Marco instantáneo stories 03 9-16", "Instant frame stories 03 9:16",
                defines={"FA": 0.5625, "SIDE": 0.05, "BOTTOM": 0.07, "TAPE": 1.0, "TORN": 1.0},
                tags=["9:16", "vertical", "cinta", "tape", "papel rasgado", "torn paper"], thumb=1.2),
        Variant("marco-instantaneo-memories-02-1-1", "Marco instantáneo memories 02 1-1", "Instant frame memories 02 1:1",
                defines={"FA": 1.0, "SIDE": 0.06, "BOTTOM": 0.16}, params={"size": 0.8},
                tags=["1:1", "cuadrado", "square"], thumb=1.0),
        Variant("marco-instantaneo-02-9-16", "Marco instantáneo 02 9-16", "Instant frame 02 9:16",
                defines={"FA": 0.5625, "SIDE": 0.045, "BOTTOM": 0.04, "ROUND": 0.02},
                tags=["9:16", "vertical"], photo="fx-woman-05", thumb=1.6),
        Variant("marco-instantaneo-memories-03-1-1", "Marco instantáneo memories 03 1-1", "Instant frame memories 03 1:1",
                defines={"FA": 1.0, "SIDE": 0.06, "BOTTOM": 0.1, "TAPE": 1.0, "TORN": 1.0}, params={"size": 0.8, "angle": -1.7},
                tags=["1:1", "cuadrado", "square", "cinta", "tape", "papel rasgado", "torn paper"], photo="couple", thumb=1.4),
        Variant("marco-instantaneo-03-16-9", "Marco instantáneo 03 16-9", "Instant frame 03 16:9",
                defines={"FA": 1.6, "SIDE": 0.05, "BOTTOM": 0.06, "TAPE": 1.0, "TORN": 1.0}, params={"size": 0.78},
                tags=["16:9", "horizontal", "cinta", "tape", "papel rasgado", "torn paper"], photo="beach", thumb=1.0),
        Variant("marco-instantaneo-02-16-9", "Marco instantáneo 02 16-9", "Instant frame 02 16:9",
                defines={"FA": 1.6, "SIDE": 0.035, "BOTTOM": 0.0, "ROUND": 0.025}, params={"size": 0.8},
                tags=["16:9", "horizontal"], photo="walk", thumb=1.8),
        Variant("camara-instantanea", "Cámara instantánea", "Instant camera",
                defines={"FA": 0.82, "SIDE": 0.06, "BOTTOM": 0.2, "BG": 2.0, "FLASH": 1.0}, params={"size": 0.72, "angle": 2.3, "brightness": 0.6, "blur": 0.0},
                tags=["flash", "revelar", "develop", "camara", "camera"], photo="nature", thumb=1.6),
        Variant("paralelo-photobook", "Paralelo Photobook", "Parallel photobook",
                defines={"FA": 1.45, "SIDE": 0.035, "BG": 1.0}, params={"size": 0.72, "angle": -4.0, "rotation": 2.9},
                tags=["album", "photobook", "fotolibro", "pagina", "page"], photo="man", thumb=1.2),
        Variant("diapositivas-de-fotolibros", "Diapositivas de fotolibros", "Photobook slides",
                defines={"FA": 1.4, "SIDE": 0.04, "BG": 0.0, "BACK": 2.0}, params={"size": 0.66, "angle": -2.9, "brightness": 0.7},
                tags=["album", "photobook", "fotolibro", "diapositivas", "slides"], photo="woman", thumb=1.0),
        Variant("notas-fijadas", "Notas fijadas", "Pinned notes",
                defines={"FA": 0.0, "SIDE": 0.03, "BG": 1.0, "NOTES": 1.0}, params={"size": 0.8, "angle": 1.1, "rotation": 1.1},
                tags=["notas", "notes", "post-it", "papel", "paper"], photo="fx-woman-03", thumb=1.0),
        Variant("escala-de-borde", "Escala de borde", "Border scale",
                defines={"FA": 0.0, "SIDE": 0.012, "BG": 0.0, "PULSE": 1.0}, params={"size": 0.9, "rotation": 0.0, "brightness": 0.75},
                tags=["escala", "scale", "ritmo", "beat", "pulso", "pulse"], photo="fashion", thumb=1.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Light running along the border: heads with long tails, two colours spread over the frame.
BEAM = Family(
    key="marcos_beam", category="marcos",
    params=[INTENSITY, SPEED, Param("color_a", "Colour A", default="#ff2a2a"),
            Param("color_b", "Colour B", default="#2f7bff"), Param("width", "Width", 0.3, 3.0, 1.0),
            Param("density", "Density", 1.0, 4.0, 2.0), Param("spread", "Spread", 0.03, 0.5, 0.2),
            Param("glow", "Glow", 0.0, 3.0, 1.0)],
    photo="dark", tags=["haz", "beam", "luz", "light", "borde", "border", "neon"],
    defines={"INSET": 0.012, "BASE": 0.18, "DIR": (0.7, -0.7), "GRAIN": 0.0,
             "SPD": 0.22, "FLICK": 0.0},
    body=PERIM + r"""
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    vec2 h = vec2(aspect() * 0.5, 0.5) - INSET;
    float d = sdRoundBox(p, h, 0.012);
    float s = perim(p, h);
    float t = u_time * speed * SPD;
    float energy = BASE;
    float head = 0.0;
    for (int i = 0; i < 4; ++i) {
        float heads = floor(density + 0.5);
        if (float(i) >= heads) break;
        float hd = fract(t + float(i) / heads);
        float behind = fract(hd - s);
        energy += exp(-behind / spread);
        head += exp(-behind / 0.006) * step(behind, 0.5);
    }
    if (GRAIN > 0.0) energy *= mix(1.0, 0.35 + 1.3 * vnoise(vec2(s * 260.0, u_time * 6.0)), GRAIN);
    if (FLICK > 0.0) energy *= 1.0 + FLICK * (vnoise(vec2(u_time * 9.0, s * 20.0)) - 0.5);
    vec2 dir = normalize(DIR);
    float m = sat(0.5 + 0.75 * dot(p / vec2(aspect() * 0.5, 0.5), dir));
    vec3 c = mix(color_a, color_b, smoothstep(0.15, 0.85, m));
    float w = 0.005 * width;
    float core = smoothstep(w, 0.0, abs(d));
    float halo = glow * exp(-abs(d) / (0.035 * width)) * (d < 0.0 ? 1.0 : 0.4);
    vec3 light = c * (core * 1.8 + halo * 1.4) * energy + vec3(1.0) * core * (0.35 * energy * energy + head);
    light += c * halo * head * 1.5;
    fragColor = vec4(addLight(src.rgb * (1.0 - 0.15 * intensity * halo), light, intensity), src.a);
}
""",
    variants=[
        Variant("flujo-de-haz-2", "Flujo de haz 2", "Beam flow 2",
                params={"color_a": "#ff3b30", "color_b": "#2f8bff"}, defines={"DIR": (0.6, -0.8)}, thumb=0.8),
        Variant("flujo-de-haz-3", "Flujo de haz 3", "Beam flow 3",
                params={"color_a": "#ffd21a", "color_b": "#ff2420", "density": 3.0, "spread": 0.09},
                defines={"DIR": (1.0, 0.0), "GRAIN": 0.8}, thumb=1.4),
        Variant("flujo-de-haz-4", "Flujo de haz 4", "Beam flow 4",
                params={"color_a": "#36c6ff", "color_b": "#ff3349", "width": 0.6, "spread": 0.12},
                defines={"DIR": (1.0, 0.0), "BASE": 0.05, "SPD": 0.3}, thumb=1.0),
        Variant("flujo-de-haz-6", "Flujo de haz 6", "Beam flow 6",
                params={"color_a": "#ff6a00", "color_b": "#ffc22e", "width": 1.3, "density": 3.0},
                defines={"DIR": (0.0, 1.0), "BASE": 0.45, "GRAIN": 0.5, "FLICK": 0.5}, thumb=1.2),
        Variant("flujo-de-haz-7", "Flujo de haz 7", "Beam flow 7",
                params={"color_a": "#2a5bff", "color_b": "#ff2a3d"}, defines={"DIR": (0.7, -0.7), "BASE": 0.3},
                thumb=2.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Echo frames: the picture in a front frame and outlines repeating behind it in perspective, flowing back.
ECHO = Family(
    key="marcos_echo", category="marcos",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#ffffff"), Param("density", "Density", 1.0, 6.0, 6.0),
            Param("distance", "Distance", 0.0, 1.0, 0.42), Param("size", "Size", 0.3, 0.9, 0.52),
            Param("blur", "Blur", 0.0, 3.0, 1.0), Param("brightness", "Brightness", 0.0, 1.0, 0.28)],
    photo="man", tags=["eco", "echo", "marcos", "frames", "perspectiva", "perspective"],
    body=r"""
float trap(vec2 q, vec2 h, float skew) {
    q.y /= max(1.0 + skew * q.x / h.x, 0.2);
    return sdBox(q, h);
}
void main() {
    vec2 uv = v_texCoord;
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec3 col = discBlur(uv, 0.05 * blur).rgb * brightness;
    vec2 h = vec2(aspect() * 0.5, 0.5) * size;
    float swing = sin(t * 1.1) * 0.25;
    float aa = 1.5 / u_resolution.y;
    float line = 0.0;
    for (int i = 0; i < 6; ++i) {
        float n = floor(density + 0.5);
        if (float(i) >= n) break;
        float f = (float(i) + fract(t * 0.6)) / n;        // 0 = at the front, 1 = far behind
        vec2 c = vec2(distance * f * aspect() * 0.5 * (1.0 + swing), -0.02 * f);
        float sc = 1.0 - 0.45 * f;
        float skew = -0.35 * f + swing * 0.3;
        float d = trap((p - c) / sc, h, skew) * sc;
        float fade = (1.0 - f) * smoothstep(0.0, 0.15, f);
        line = max(line, smoothstep(0.0028 + aa, 0.0, abs(d)) * fade);
    }
    col = mix(col, color, sat(line * intensity));
    // The front frame holds the picture.
    vec2 c0 = vec2(-0.06 * aspect() * 0.5, 0.0);
    float skew0 = 0.12 * sin(t * 1.1);
    vec2 q = p - c0;
    q.y /= 1.0 + skew0 * q.x / h.x;
    float d0 = sdBox(q, h);
    float win = 1.0 - smoothstep(-aa, aa, d0);
    vec2 puv = 0.5 + q / (2.0 * h) / 1.02;
    col *= 1.0 - 0.5 * exp(-max(d0, 0.0) / 0.02);
    col = mix(col, S(clamp(puv, 0.001, 0.999)).rgb, win);
    col = mix(col, color, smoothstep(0.004 + aa, 0.0, abs(d0)) * sat(intensity));
    fragColor = vec4(col, 1.0);
}
""",
    variants=[Variant("marco-de-eco-31", "Marco de eco 31", "Echo frame 31", thumb=1.0)],
)

# ---------------------------------------------------------------------------------------------------------------
# Fire burning along the edges of the picture.
FIRE = Family(
    key="marcos_fire", category="marcos",
    params=[INTENSITY, SPEED, Param("color_a", "Colour A", default="#bf1400"),
            Param("color_b", "Colour B", default="#ffd959"), Param("width", "Width", 0.3, 2.5, 1.0),
            Param("frequency", "Frequency", 2.0, 14.0, 7.0), Param("amount", "Amount", 0.0, 1.5, 0.0)],
    photo="dark", tags=["fuego", "fire", "llamas", "flames", "borde", "border", "marco", "frame"],
    defines={"TH": 0.05, "CHUNK": 0.6},
    body=r"""
vec3 fireRamp(float x) {
    x = sat(x);
    vec3 c = mix(vec3(0.0), color_a, linstep(0.0, 0.35, x));
    c = mix(c, mix(color_a, color_b, 0.45) * 1.15, linstep(0.3, 0.65, x));
    c = mix(c, color_b, linstep(0.6, 0.9, x));
    return mix(c, vec3(1.0, 0.98, 0.85), linstep(0.9, 1.0, x));
}
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    float e = min(min(uv.x, 1.0 - uv.x) * aspect(), min(uv.y, 1.0 - uv.y));   // distance to the nearest edge
    vec2 out_ = normalize(p + 1e-4);
    vec2 q = p * frequency - out_ * t * 1.6 + vec2(0.0, t * 0.7);
    float n = fbm(q + fbm(q * 0.7 + t * 0.3) * 1.5);
    float th = TH * width;
    float heat = (th - e) / th + (n - 0.5) * 2.0 * CHUNK;
    float flame = sat(heat) * 0.88;
    vec3 fire = fireRamp(flame) * smoothstep(0.0, 0.25, heat);
    float smoke = amount * smoothstep(th * 2.6, 0.0, e) * (0.6 + 0.4 * n);
    vec3 base = src.rgb * (1.0 - smoke * 0.85 * intensity);
    base *= 1.0 - 0.5 * smoothstep(th * 2.0, 0.0, e) * intensity;
    float glowK = exp(-e / (th * 1.5)) * 0.35;
    vec3 col = addLight(base, fire + mix(color_a, color_b, 0.3) * glowK * (0.8 + 0.2 * sin(t * 13.0)), intensity);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("marco-de-fuego", "Marco de fuego", "Fire frame", thumb=1.0),
        Variant("marco-de-llamas", "Marco de llamas", "Flame frame",
                defines={"TH": 0.085, "CHUNK": 0.8}, params={"frequency": 4.5, "amount": 1.0},
                tags=["barbacoa", "barbecue", "fiesta", "party"], thumb=1.5),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# A line around the picture: a clean border, an inset line drawn on, a hand-drawn marker frame.
LINE = Family(
    key="marcos_line", category="marcos",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#ffffff"), Param("width", "Width", 0.3, 3.0, 1.0),
            Param("distance", "Distance", 0.0, 0.2, 0.006), Param("softness", "Softness", 0.0, 0.1, 0.02),
            Param("glow", "Glow", 0.0, 3.0, 1.0), Param("amount", "Amount", 0.0, 0.1, 0.0)],
    photo="dark", tags=["borde", "border", "linea", "line", "marco", "frame"],
    defines={"LW": 0.004, "DRAW": 0.0, "MARKER": 0.0, "SHINE": 1.0},
    body=PERIM + r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec2 h = vec2(aspect() * 0.5, 0.5) - distance;
    float aa = 1.2 / u_resolution.y;
    float a = 0.0;
    if (MARKER > 0.5) {
        float st = stepTime(t, 8.0);
        float strokes = 0.0;
        for (int i = 0; i < 2; ++i) {
            float fi = float(i);
            vec2 q = p + (vec2(vnoise(p * 3.0 + st * 3.1 + fi * 7.0), vnoise(p * 3.0 + st * 2.3 + 5.0 + fi * 3.0)) - 0.5) * amount
                       + (hash22(vec2(st, fi)) - 0.5) * 0.006;
            float d = sdRoundBox(q, h - vec2(0.012 * fi), softness);
            float w = LW * width * (0.8 + 0.4 * vnoise(vec2(perim(q, h) * 40.0, fi)));
            strokes = max(strokes, smoothstep(w + aa, w - aa, abs(d)) * (fi < 0.5 ? 1.0 : 0.7));
        }
        float fib = 0.75 + 0.25 * vnoise(vec2(dot(p, vec2(1.0, 1.0)) * 300.0, 1.0));   // the felt tip texture
        a = strokes * fib;
        vec3 col = mix(src.rgb, src.rgb * color * 1.15 + color * 0.25, sat(a * intensity) * 0.9);
        fragColor = vec4(col, src.a);
        return;
    }
    float d = sdRoundBox(p, h, softness);
    float w = LW * width;
    float line = smoothstep(w + aa, w - aa, abs(d));
    if (DRAW > 0.5) {
        float ph = phase(t, 4.0);
        float grow = easeInOut(ph / 0.35), shrink = easeInOut((ph - 0.8) / 0.2);
        float s = perim(p, h);
        float s2 = fract(s - 0.0);
        line *= step(s2, grow) * step(shrink, s2);
    }
    float s = perim(p, h);
    float shine = SHINE * glow * pow(0.5 + 0.5 * cos(TAU * (s - t * 0.25)), 24.0);
    float halo = exp(-abs(d) / 0.012) * 0.25 * glow * line;
    vec3 col = mix(src.rgb, color, sat(line * intensity));
    col = addLight(col, color * (shine * smoothstep(0.03, 0.0, abs(d)) + halo), intensity);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("borde", "Borde", "Border", defines={"LW": 0.006}, params={"distance": 0.012, "softness": 0.03}, thumb=1.0),
        Variant("linea-fronteriza-01", "Línea fronteriza 01", "Border line 01",
                defines={"LW": 0.0035, "DRAW": 1.0, "SHINE": 0.6}, params={"distance": 0.045, "softness": 0.0}, thumb=2.0),
        Variant("marco-marcador", "Marco marcador", "Marker frame",
                params={"color": "#ffe14a", "width": 1.6, "distance": 0.04, "softness": 0.01, "amount": 0.04},
                defines={"LW": 0.006, "MARKER": 1.0},
                tags=["marcador", "marker", "dibujo", "doodle", "a mano", "hand drawn"], photo="woman", thumb=1.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Glow on the outlines of the picture (the person lights up at the edges), at 120 BPM.
EDGE_GLOW = Family(
    key="marcos_edge_glow", category="marcos",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#e8d6ff")],
    photo="fashion", tags=["resplandor", "glow", "contorno", "outline", "bordes", "edges"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float e = edges(uv, 1.5);
    float ring = 0.0;
    for (int i = 0; i < 8; ++i) {
        float a = float(i) * TAU / 8.0;
        ring += edges(uv + vec2(cos(a), sin(a)) * px() * 4.0, 1.5);
    }
    ring /= 8.0;
    float b = beat(u_time * speed, 0.5, 0.2);
    float k = intensity * (0.35 + 0.5 * b);
    vec3 glow = color * (smoothstep(0.3, 0.9, e) * 0.9 + smoothstep(0.2, 0.7, ring) * 0.6);
    vec3 col = addLight(src.rgb * (1.0 - 0.12 * intensity), glow, k);
    fragColor = vec4(col, src.a);
}
""",
    variants=[Variant("resplandor-de-borde-04", "Resplandor de borde 04", "Edge glow 04", thumb=1.0)],
)

# ---------------------------------------------------------------------------------------------------------------
# White chalky scribbles (and grunge blotches) that boil at 8 frames a second.
GRUNGE = Family(
    key="marcos_grunge", category="marcos",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#ffffff"), Param("scale", "Scale", 1.0, 6.0, 2.6),
            Param("density", "Density", 0.0, 2.0, 1.0), Param("width", "Width", 0.3, 3.0, 1.0),
            Param("amount", "Amount", 0.0, 1.0, 0.0)],
    photo="dark", tags=["grunge", "garabatos", "scribbles", "tiza", "chalk", "dibujo", "doodle"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    float st = stepTime(t, 8.0);
    float cycle = floor(t / 2.0);                       // the scribbles change their shape every two seconds
    vec2 j = (hash22(vec2(st, 3.0)) - 0.5) * 0.006;
    vec2 q = (p + j) * scale + hash22(vec2(cycle, 1.0)) * 20.0;
    float f = fbm(q);
    float w = (0.012 + 0.008 * vnoise(q * 3.0)) * width;
    float lines = smoothstep(w, w * 0.4, abs(f - 0.5)) + smoothstep(w, w * 0.4, abs(f - 0.62)) * 0.8;
    float region = smoothstep(0.52 - 0.2 * (density - 1.0), 0.66 - 0.2 * (density - 1.0), vnoise(p * 2.2 + hash22(vec2(cycle, 7.0)) * 10.0));
    float dry = smoothstep(0.1, 0.5, vnoise((p + j) * 260.0) * 0.6 + vnoise((p + j) * 70.0) * 0.6);
    float a = sat(lines) * region * dry;
    float show = smoothstep(0.0, 0.15, fract(t / 2.0));
    a *= show;
    if (amount > 0.0) {
        float g = fbm(p * 4.0 + vec2(cycle * 3.1, 0.0));
        float sp = step(0.93, hash12(floor((p + j) * 180.0)));
        float bl = smoothstep(0.58, 0.66, g) * (0.5 + 0.5 * vnoise(p * 120.0)) + sp * smoothstep(0.5, 0.6, g) * 0.8;
        float edge = smoothstep(0.25, 0.5, max(abs(p.x) / aspect() * 2.0, abs(p.y) * 2.0));
        a = max(a, bl * mix(0.35, 1.0, edge) * amount);
    }
    vec3 col = mix(src.rgb, color, sat(a * intensity) * 0.92);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("garabatos-grunge", "Garabatos grunge", "Grunge scribbles", thumb=1.0),
        Variant("grunge-blanco", "Grunge blanco", "White grunge", params={"amount": 1.0, "scale": 2.2}, thumb=1.3),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Manga speed lines rushing in from the edges, redrawn 12 times a second.
SPEED_LINES = Family(
    key="marcos_speed", category="marcos",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#ffffff"), Param("density", "Density", 0.4, 2.0, 1.0),
            Param("size", "Size", 0.2, 1.5, 1.0), Param("width", "Width", 0.3, 3.0, 1.0)],
    photo="dark", tags=["manga", "anime", "velocidad", "speed", "lineas", "lines", "comic"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float st = stepTime(u_time * speed, 12.0);
    vec2 e = p / vec2(aspect() * 0.5, 0.5);
    float r = length(e);
    float ang = atan(p.y, p.x) / TAU + 0.5;
    float n = floor(140.0 * density);
    float cell = floor(ang * n);
    float f = fract(ang * n);
    float a = 0.0;
    for (int k = -1; k <= 1; ++k) {
        float c = cell + float(k);
        vec3 h = hash32(vec2(mod(c, n), st));
        float ff = f - float(k);
        float inner = (0.72 + 0.4 * h.y) * size;                       // where the line starts (from the centre)
        float w = (0.15 + 0.5 * h.z) * sat((r - inner) / 0.6) * 2.2 * width;
        float on = step(0.45, h.x);
        a += on * smoothstep(w, w * 0.3, abs(ff - 0.5 - (h.x - 0.5) * 0.6)) * smoothstep(inner, inner + 0.12, r);
    }
    a = sat(a);
    vec3 base = src.rgb * (1.0 - 0.35 * intensity * smoothstep(0.5, 1.3, r));
    fragColor = vec4(mix(base, color, a * sat(intensity)), src.a);
}
""",
    variants=[Variant("lineas-de-velocidad", "Líneas de velocidad", "Speed lines",
                      tags=["shake it up", "concentracion", "focus"], thumb=1.0)],
)

# ---------------------------------------------------------------------------------------------------------------
# Music visualizers at a steady 120 BPM: bars, a thin spectrum, a glowing ring.
MUSIC = Family(
    key="marcos_music", category="marcos",
    params=[INTENSITY, SPEED, Param("color_a", "Colour A", default="#ff3fd8"),
            Param("color_b", "Colour B", default="#2f6bff"), Param("frequency", "Frequency", 0.2, 3.0, 1.0),
            Param("size", "Size", 0.3, 2.0, 1.0), Param("width", "Width", 0.3, 2.0, 1.0),
            Param("density", "Density", 0.3, 2.0, 1.0)],
    photo="dark", tags=["musica", "music", "audio", "ritmo", "beat", "espectro", "spectrum"],
    defines={"MODE": 0.0},
    body=r"""
float level(float i, float t) {
    float b = beat(t, 0.5, 0.18);
    return (0.25 + 0.75 * vnoise(vec2(i * 0.9, t * 5.0 * frequency))) * (0.55 + 0.45 * b);
}
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    float aa = 1.5 / u_resolution.y;
    vec3 light = vec3(0.0);
    float dim = 0.0;
    if (MODE < 0.5) {
        // Bars mirrored up and down, taller in the middle, colour across.
        float W = aspect() * 0.36 * width, N = floor(44.0 * density);
        float x = (p.x + W) / (2.0 * W);
        float i = floor(x * N);
        float fx = fract(x * N);
        float env = pow(sin(PI * sat((i + 0.5) / N)), 1.5);
        float hgt = (0.04 + 0.3 * env * level(abs(i - N * 0.5) + 3.0 * step(N * 0.5, i), t)) * size; // level(abs(i - N * 0.5) + 3.0 * step(N * 0.5, i), t);
        float inBar = step(0.0, x) * step(x, 1.0) * smoothstep(0.5, 0.36, abs(fx - 0.5));
        float d = abs(p.y) - hgt;
        float bar = inBar * (1.0 - smoothstep(-aa, aa, d));
        vec3 c = mix(color_a, color_b, sat(x));
        light = c * (bar * 1.3 + inBar * exp(-max(d, 0.0) / 0.03) * 0.5) + vec3(1.0) * bar * 0.15;
        dim = 0.25 * smoothstep(0.35, 0.0, abs(p.y));
    } else if (MODE < 1.5) {
        // A thin spectrum across the whole width.
        float N = floor(150.0 * density);
        float x = uv.x;
        float i = floor(x * N);
        float fx = fract(x * N);
        float spike = pow(vnoise(vec2(i * 0.35, floor(t * 2.0 * frequency))), 3.0);
        float hgt = (0.01 + 0.05 * level(i, t) + 0.17 * spike * beat(t, 0.5, 0.25)) * size;
        float d = abs(p.y) - hgt;
        float inBar = smoothstep(0.5, 0.3, abs(fx - 0.5));
        float bar = inBar * (1.0 - smoothstep(-aa, aa, d));
        light = color_a * bar * 1.1 + color_a * inBar * exp(-max(d, 0.0) / 0.015) * 0.2;
    } else {
        // A ring that bulges on the beat, with bumps around it.
        float R = 0.2 * size;
        float ang = atan(p.y, p.x);
        float b = beat(t, 0.5, 0.2);
        float bumps = pow(0.5 + 0.5 * cos(ang * floor(9.0 * density + 0.5) + t * 1.5 * frequency), 6.0) * 0.03 * (0.4 + 0.6 * b);
        float wob = (vnoise(vec2(ang * 3.0 + 10.0, t * 3.0)) - 0.5) * 0.02;
        float r = R * (1.0 + 0.1 * b) + bumps + wob;
        float d = length(p) - r;
        float core = smoothstep(0.006 * width + aa, 0.0, abs(d));
        float halo = exp(-abs(d) / (0.03 * width)) * (0.6 + 0.6 * b);
        float dots = 0.0;
        for (int k = 0; k < 9; ++k) {
            float a2 = float(k) * TAU / 9.0 - t * 0.5 * frequency;
            vec2 c = vec2(cos(a2), sin(a2)) * (r + 0.035 + 0.02 * b);
            dots += exp(-dot(p - c, p - c) / 0.00012);
        }
        light = color_a * (core * 1.4 + halo * 0.9 + dots) + vec3(1.0) * core * 0.6;
        dim = 0.3 * smoothstep(0.45, 0.0, length(p));
    }
    vec3 col = addLight(src.rgb * (1.0 - dim * intensity), light, intensity);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("barras-de-musica", "Barras de música", "Music bars", defines={"MODE": 0.0},
                tags=["barras", "bars", "ecualizador", "equalizer"], thumb=1.0),
        Variant("espectro-de-audio-03", "Espectro de audio 03", "Audio spectrum 03", defines={"MODE": 1.0},
                params={"color_a": "#ffffff"}, tags=["onda", "waveform"], thumb=1.0),
        Variant("anillo-de-musica", "Anillo de música", "Music ring", defines={"MODE": 2.0},
                params={"color_a": "#ffe25a"}, tags=["anillo", "ring", "circulo", "circle", "resplandor", "glow"],
                thumb=1.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# A grey halftone grid on both sides, the picture clear in a band in the middle.
GRID = Family(
    key="marcos_grid", category="marcos",
    params=[INTENSITY, SPEED, Param("width", "Width", 0.3, 2.0, 1.0), Param("size", "Size", 0.5, 2.0, 1.0),
            Param("color", "Colour", default="#9e9e9e"), Param("softness", "Softness", 0.0, 1.0, 0.0)],
    photo="hair", tags=["rejilla", "grid", "puntos", "dots", "semitono", "halftone", "gris", "grey"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    float cs = 0.022 * size;
    vec2 g = p + vec2(0.0, t * 0.02);
    vec2 cell = floor(g / cs);
    vec2 f = fract(g / cs) - 0.5;
    vec2 cuv = fromP((cell + 0.5) * cs - vec2(0.0, t * 0.02));
    float l = luma(S(clamp(cuv, 0.0, 1.0)).rgb);
    float r = 0.12 + 0.36 * sqrt(l);
    float dotm = smoothstep(r + 0.08, r - 0.08, length(f));
    vec3 grey = mix(vec3(0.16), color * 0.62 / 0.62, dotm);
    float bw = aspect() * 0.18 * width * (1.0 + 0.04 * sin(t * 1.4));
    float band = smoothstep(bw, bw - 0.01 - 0.15 * softness, abs(p.x));
    float shade = exp(-max(abs(p.x) - bw, 0.0) / 0.02) * (1.0 - band) * 0.5;
    vec3 side = mix(grey * (1.0 - shade), src.rgb, 0.08);
    vec3 col = mix(src.rgb, mix(side, src.rgb, band), sat(intensity));
    fragColor = vec4(col, src.a);
}
""",
    variants=[Variant("rejilla-gris", "Rejilla gris", "Grey grid", thumb=1.0)],
)

FAMILIES = [CARD, BEAM, ECHO, FIRE, LINE, EDGE_GLOW, GRUNGE, SPEED_LINES, MUSIC, GRID]
