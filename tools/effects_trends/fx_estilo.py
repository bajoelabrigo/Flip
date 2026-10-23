"""Efectos › Tendencias, Estilizar: comic and cartoon looks, censor mosaics, colour grades, psychedelic warps,
a skull ghost, falling cheese, a computer-screen search and the neon scans (a bright band sweeping across with
glowing edges)."""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)

# Shared GLSL helpers (each family is its own shader, so they are pasted where needed).
COMMON = r"""
// Pixel spreads scale with the frame so lines keep their look at 1080p and at a 320 px preview.
float rs() { return max(u_resolution.y / 360.0, 1.0); }
float smin(float a, float b, float k) { float h = sat(0.5 + 0.5 * (b - a) / k); return mix(b, a, h) - k * h * (1.0 - h); }
// A light smoothing that keeps edges (flat colour areas for cartoons).
vec3 flatColor(vec2 uv) {
    vec3 c = S(uv).rgb, acc = c;
    float w = 1.0;
    for (int i = 0; i < 8; ++i) {
        float a = float(i) * 0.785398;
        vec3 s = S(uv + vec2(cos(a), sin(a)) * px() * 2.0 * rs()).rgb;
        float k = exp(-dot(s - c, s - c) * 30.0);
        acc += s * k;
        w += k;
    }
    return acc / w;
}
vec3 posterize(vec3 c, float levels, float satb) {
    vec3 h = rgb2hsv(c);
    float v = h.z * levels;
    h.z = (floor(v) + smoothstep(0.3, 0.7, fract(v))) / levels;
    h.y = sat(h.y * satb);
    return hsv2rgb(h);
}
// Halftone dots on a 45 degree grid: 1 on a dot. `amount` 0..1 = how much of the cell the dot covers.
float halftone(vec2 uv, float amount, vec2 drift) {
    float cell = u_resolution.y / 95.0;
    vec2 p = rot(0.785398) * (uv * u_resolution + drift * u_resolution.y) / cell;
    vec2 f = fract(p) - 0.5;
    float r = sqrt(sat(amount)) * 0.62;
    return smoothstep(r + 0.09, r - 0.09, length(f));
}
"""

# ---------------------------------------------------------------------------------------------------------------
# Cartoons: flat colour + ink lines that "boil" (redrawn 8 times a second, like a hand-drawn cartoon).
# MODE 0 colour comic (saturated, halftone shadows, punch on the beat), 1 cartoon, 2 black and white ink,
# 3 a pencil sketch that colour floods up from the bottom and drains again.
CARTOON = Family(
    key="est_cartoon", category="estilo",
    params=[INTENSITY, SPEED, Param("detail", "Detail", 2.0, 12.0, 5.0), Param("saturation", "Saturation", 0.0, 2.5, 1.5),
            Param("edge_width", "Edge Width", 0.3, 3.0, 1.0), Param("color", "Colour", default="#000000")],
    photo="woman",
    tags=["comic", "cómic", "dibujo", "cartoon", "caricatura", "ilustracion", "illustration"],
    defines={"MODE": 0, "EDGE_LO": 0.24, "EDGE_HI": 0.55},
    body=COMMON + r"""
void main() {
    float t = u_time * speed;
    float k = 1.0;
    if (MODE < 0.5) k = 1.0 + 0.03 * beat(u_time, 0.5, 0.12) * sat(intensity);
    vec2 cuv = camUv(v_texCoord, vec2(0.5), k, 0.0, vec2(0.0));
    vec4 src = Sm(cuv);
    float bt = stepTime(t, 8.0);
    vec2 suv = cuv + (hash22(vec2(bt, 1.7)) - 0.5) * px() * 1.4 * rs();
    vec3 fl = flatColor(suv);
    float e = edges(suv, 1.3 * rs() * edge_width);
    float ink = smoothstep(EDGE_LO, EDGE_HI, e) * min(intensity, 1.2);
    vec3 col;
    if (MODE < 0.5) {
        col = contrastColor(posterize(fl, detail, saturation), 1.12);
        float amt = sat((0.42 - luma(col)) * 2.2);
        col = mix(col, col * 0.4, halftone(cuv, amt, vec2(t * 0.01, 0.0)) * step(0.02, amt));
        col = mix(col, color, ink * 0.92);
    } else if (MODE < 1.5) {
        col = posterize(pow(fl, vec3(0.8)), detail, saturation);
        col = mix(col, sat3(col * 1.08 + 0.03), 0.6);
        col = mix(col, color, ink * 0.85);
    } else if (MODE < 2.5) {
        float l = luma(fl);
        float thr = 0.3 + 0.024 * detail + 0.025 * (hash11(bt * 3.1) - 0.5);
        float b = smoothstep(thr - 0.035, thr + 0.035, l);
        // Hatching in the middle tones.
        float hatchZone = (1.0 - smoothstep(thr + 0.05, thr + 0.2, l)) * b;
        vec2 hp = rot(0.6) * (cuv * u_resolution) / (2.6 * rs());
        float hatch = smoothstep(0.35, 0.15, abs(fract(hp.x + 0.15 * hash11(floor(hp.y * 0.08) + bt)) - 0.5));
        b *= 1.0 - hatch * hatchZone * 0.85;
        b *= 1.0 - ink;
        float grain = (hash12(cuv * u_resolution + bt) - 0.5) * 0.04;
        col = mix(color, vec3(0.97, 0.955, 0.93), sat(b)) + grain;
    } else {
        // Pencil sketch on paper.
        float l = luma(fl);
        vec2 hp = rot(0.7) * (cuv * u_resolution) / (2.4 * rs());
        float hatch = smoothstep(0.3, 0.1, abs(fract(hp.x) - 0.5)) * (1.0 - smoothstep(0.25, 0.6, l));
        vec3 paper = vec3(0.97, 0.965, 0.95) - 0.03 * fbm(cuv * 9.0);
        vec3 sketch = mix(paper, color, ink * 0.8) * (1.0 - hatch * 0.35);
        vec3 paint = mix(posterize(fl, detail, saturation), color, ink * 0.6);
        float cyc = phase(t, 3.0);
        float fill = easeInOut(linstep(0.05, 0.55, cyc)) * (1.0 - easeInOut(linstep(0.78, 1.0, cyc)));
        float lvl = 1.06 - 1.18 * fill;
        float wv = 0.022 * sin(cuv.x * 17.0 + t * 5.0) + 0.04 * (fbm(vec2(cuv.x * 5.0, t * 0.7)) - 0.5);
        float fy = lvl + wv;
        float m = smoothstep(fy - 0.012, fy + 0.012, cuv.y);
        col = mix(sketch, paint, m);
        col = addLight(col, vec3(0.85, 0.95, 1.0), exp(-abs(cuv.y - fy) * 90.0) * 0.6 * step(0.01, fill));
    }
    fragColor = vec4(mix(src.rgb, sat3(col), sat(intensity)), src.a);
}
""",
    variants=[
        Variant("comic-en-color", "Cómic en color", "Colour comic", photo="fx-woman-08", thumb=1.0,
                params={"detail": 5.0, "saturation": 1.5},
                tags=["color", "colour", "pop art"]),
        Variant("filtro-de-dibujos-animados-01", "Filtro de dibujos animados 01", "Cartoon filter 01",
                defines={"MODE": 1, "EDGE_LO": 0.26, "EDGE_HI": 0.6}, params={"detail": 7.0, "saturation": 1.2}, photo="fx-woman-05", thumb=1.0),
        Variant("filtro-de-dibujos-animados-05", "Filtro de dibujos animados 05", "Cartoon filter 05",
                defines={"MODE": 2, "EDGE_LO": 0.2, "EDGE_HI": 0.45}, params={"detail": 5.0, "color": "#12110f"},
                photo="fx-woman-08", thumb=1.0,
                tags=["blanco y negro", "black and white", "tinta", "ink"]),
        Variant("inundacion-dibujo", "Inundación dibujo", "Drawing flood",
                defines={"MODE": 3, "EDGE_LO": 0.12, "EDGE_HI": 0.38}, params={"detail": 6.0, "saturation": 1.3},
                photo="fx-man-01", thumb=1.4, tags=["boceto", "sketch", "lapiz", "pencil"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# A comic page: three panels with the photo at three crops, halftone shading and ink, popping in one by one.
COMIC_PAGE = Family(
    key="est_comic_page", category="estilo",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#2aa6b4"), Param("detail", "Detail", 2.0, 12.0, 5.0),
            Param("saturation", "Saturation", 0.0, 2.5, 1.45), Param("edge_width", "Edge Width", 0.3, 3.0, 1.0),
            Param("zoom", "Zoom", 0.5, 2.0, 1.0)],
    photo="man",
    tags=["comic", "cómic", "viñetas", "panels", "historieta", "halftone"],
    defines={"FOCUS": (0.45, 0.32)},
    body=COMMON + r"""
vec3 comicShade(vec2 uv, float bt) {
    vec2 suv = uv + (hash22(vec2(bt, 4.1)) - 0.5) * px() * rs();
    vec3 col = contrastColor(posterize(flatColor(suv), detail, saturation), 1.1);
    float amt = sat((0.45 - luma(col)) * 2.0);
    col = mix(col, col * 0.45, halftone(uv, amt, vec2(0.0)) * step(0.02, amt));
    float ink = smoothstep(0.24, 0.55, edges(suv, 1.3 * rs() * edge_width));
    return col * (1.0 - ink * 0.9);
}
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float t = u_time * speed;
    float bt = stepTime(t, 8.0);
    // Page: halftone dots in the page colour.
    vec3 page = mix(color * 1.15, color * 0.7, halftone(uv, 0.35, vec2(t * 0.02, 0.0)));
    vec3 col = page;
    float g = 0.012;  // gutter (uv of the height)
    vec2 gx = vec2(g / aspect(), g);
    vec4 rects[3];
    rects[0] = vec4(gx.x * 2.0, gx.y * 2.0, 0.5 - gx.x, 1.0 - gx.y * 2.0);
    rects[1] = vec4(0.5 + gx.x, gx.y * 2.0, 1.0 - gx.x * 2.0, 0.5 - gx.y);
    rects[2] = vec4(0.5 + gx.x, 0.5 + gx.y, 1.0 - gx.x * 2.0, 1.0 - gx.y * 2.0);
    vec3 zooms = vec3(1.0, 1.5, 2.2);
    for (int i = 0; i < 3; ++i) {
        vec4 r = rects[i];
        vec2 c = 0.5 * (r.xy + r.zw), h = 0.5 * (r.zw - r.xy);
        float fi = float(i);
        float s = easeOutBack(linstep(0.1 + fi * 0.3, 0.45 + fi * 0.3, u_time * speed));
        if (s <= 0.001) continue;
        vec2 q = (uv - c) / (h * s);
        // Drop shadow first.
        vec2 qs = (uv - c - vec2(0.006, 0.01)) / (h * s);
        float sh = (1.0 - smoothstep(0.98, 1.06, max(abs(qs.x), abs(qs.y))));
        col = mix(col, col * 0.45, sh * 0.6);
        float inside = step(max(abs(q.x), abs(q.y)), 1.0);
        if (inside < 0.5) continue;
        float z = max(zooms[i] * zoom, 1.0) * (1.0 + 0.05 * sin(t * 0.6 + fi * 2.0));
        vec2 focus = (i == 0) ? vec2(0.5, 0.5) : FOCUS + vec2(0.02 * fi, 0.0);
        vec2 puv = focus + q * h / z + vec2(0.01 * sin(t * 0.4 + fi), 0.0);
        puv = 1.0 - abs(1.0 - mod(puv, 2.0));
        vec3 pc = comicShade(puv, bt + fi);
        // Black frame line.
        vec2 border = (1.0 - abs(q)) * h * s * vec2(aspect(), 1.0);
        float line = 1.0 - smoothstep(0.0035, 0.0055, min(border.x, border.y));
        col = mix(pc, vec3(0.05), line);
    }
    fragColor = vec4(mix(src.rgb, col, sat(intensity)), src.a);
}
""",
    variants=[
        Variant("estilo-de-comic-3", "Estilo de cómic 3", "Comic style 3", photo="fx-man-01", thumb=2.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Censor mosaics over a region (face area by default; move it with Center X/Y). MODE 0 pixel blocks,
# 1 painted smear, 2 scribbles. The region follows a little, like a hand-tracked censor.
MOSAIC = Family(
    key="est_mosaic", category="estilo",
    params=[INTENSITY, SPEED, Param("size", "Size", 0.3, 2.5, 1.0), Param("amount", "Amount", 0.3, 2.5, 1.0),
            Param("center_x", "Center X", 0.0, 1.0, 0.5), Param("center_y", "Center Y", 0.0, 1.0, 0.4),
            Param("softness", "Softness", 0.0, 1.0, 0.0)],
    photo="woman", tags=["mosaico", "mosaic", "censura", "censor", "pixel", "ocultar", "hide"],
    defines={"MODE": 0, "REG": (0.13, 0.17), "ROUND": 0.0, "BLOCK": 0.028},
    body=COMMON + r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float t = u_time * speed;
    vec2 pc = toP(vec2(center_x, center_y)) + shake2(t * 0.35, 1.0) * 0.008;
    vec2 p = toP(uv);
    vec2 d = p - pc;
    vec2 hs = REG * size;
    float region;
    if (MODE < 0.5) {
        region = fillSd(sdRoundBox(d, hs, ROUND * hs.y), 0.002 + 0.05 * softness);
    } else {
        // An irregular blob for the painted kinds.
        float a = atan(d.y, d.x);
        float wob = 0.08 * (vnoise(vec2(a * 2.0, stepTime(t, 6.0) * 1.3)) - 0.5);
        float rr = length(d / hs);
        region = 1.0 - smoothstep(0.9 + wob - 0.5 * softness, 1.05 + wob, rr);
    }
    vec3 col = src.rgb;
    if (MODE < 0.5) {
        float cell = BLOCK * amount;
        vec2 off = (hash22(vec2(stepTime(t, 4.0), 2.0)) - 0.5) * cell * 0.25;
        vec2 q = (floor((d + off) / cell) + 0.5) * cell + pc - off;
        col = vec3(0.0);
        col += S(fromP(q + cell * vec2(-0.25, -0.25))).rgb;
        col += S(fromP(q + cell * vec2(0.25, -0.25))).rgb;
        col += S(fromP(q + cell * vec2(-0.25, 0.25))).rgb;
        col += S(fromP(q + cell * vec2(0.25, 0.25))).rgb;
        col *= 0.25;
    } else if (MODE < 1.5) {
        // Painted: smear along a flowing direction, with brush-stroke ridges.
        float bt = stepTime(t, 6.0);
        float ang = fbm(p * 3.0 + vec2(bt * 0.4, 1.0)) * TAU * 1.5;
        vec2 dir = vec2(cos(ang), sin(ang)) * 0.13 * amount;
        vec3 acc = vec3(0.0);
        for (int i = 0; i < 12; ++i) acc += S(fromP(p + dir * (float(i) / 11.0 - 0.5))).rgb;
        col = acc / 12.0;
        vec2 sp = rot(-ang) * p;
        float ridge = sin(sp.y * 260.0 * amount / max(amount * amount, 0.3) + vnoise(sp * 30.0) * 4.0);
        col *= 0.92 + 0.08 * ridge;
        col = saturateColor(col, 1.15);
    } else {
        // Scribbles: a short smear plus dark pen strokes boiling 8 times a second.
        float bt = stepTime(t, 8.0);
        vec2 jit = (vec2(vnoise(p * 40.0 + bt * 3.0), vnoise(p * 40.0 + 7.0 + bt * 3.0)) - 0.5) * 0.05 * amount;
        col = (S(fromP(p + jit)).rgb + S(fromP(p - jit * 0.6)).rgb) * 0.5;
        float strokes = 0.0;
        for (int i = 0; i < 4; ++i) {
            float fi = float(i);
            float a = hash11(fi * 3.7 + bt) * PI;
            vec2 sp = rot(a) * (p - pc);
            float n = vnoise(sp * vec2(8.0, 3.0) + fi * 11.0 + bt) * 0.6;
            float l = abs(fract(sp.y * (28.0 + 9.0 * fi) / amount + n * 1.6 + sin(sp.x * 25.0 + fi) * 0.25) - 0.5);
            strokes = max(strokes, smoothstep(0.16, 0.04, l) * smoothstep(0.5, 0.6, vnoise(sp * 5.0 + fi * 5.0 + bt * 2.0)));
        }
        col = mix(col, col * 0.25, strokes * 0.75);
    }
    fragColor = vec4(mix(src.rgb, col, region * sat(intensity)), src.a);
}
""",
    variants=[
        Variant("mosaico", "Mosaico", "Mosaic", photo="fx-woman-08",
                params={"center_x": 0.5, "center_y": 0.42}, defines={"REG": (0.12, 0.3), "BLOCK": 0.024},
                thumb=1.0),
        Variant("mosaico-clasico", "Mosaico clásico", "Classic mosaic", photo="fx-man-04",
                params={"center_x": 0.62, "center_y": 0.36}, defines={"REG": (0.12, 0.15), "ROUND": 0.1,
                                                                     "BLOCK": 0.045}, thumb=1.0),
        Variant("pintar-mosaico", "Pintar mosaico", "Paint mosaic", photo="fx-woman-05",
                params={"center_x": 0.5, "center_y": 0.33}, defines={"MODE": 1, "REG": (0.13, 0.19)},
                thumb=1.0, tags=["pintura", "paint", "oleo"]),
        Variant("mosaico-de-garabatos", "Mosaico de garabatos", "Scribble mosaic", photo="fx-woman-08",
                params={"center_x": 0.5, "center_y": 0.38}, defines={"MODE": 2, "REG": (0.13, 0.2)},
                thumb=1.0, tags=["garabatos", "scribble"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Local colour: one hue kept (Colour), the rest grey; the kept colour pops on the beat.
LOCAL = Family(
    key="est_local_color", category="estilo",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#1494c8"), Param("spread", "Spread", 0.2, 3.0, 1.0),
            Param("saturation", "Saturation", 0.0, 2.5, 1.25), Param("contrast", "Contrast", 0.5, 2.0, 1.12)],
    photo="woman", tags=["color", "colour", "filtro", "filter"],
    defines={"TOL": 0.075},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float t = u_time * speed;
    vec4 src = S(uv);
    vec4 c = cam(uv, vec2(0.5), 1.02 + 0.03 * wave01(t, 6.0), 0.0, vec2(0.0));
    vec3 h = rgb2hsv(c.rgb);
    float target = rgb2hsv(color).x;
    float dh = abs(h.x - target);
    dh = min(dh, 1.0 - dh);
    float tol = TOL * spread;
    float keep = smoothstep(tol + 0.05, tol - 0.01, dh) * smoothstep(0.12, 0.28, h.y) * smoothstep(0.05, 0.15, h.z);
    float pulse = beat(u_time, 0.5, 0.15);
    vec3 grey = vec3(contrastColor(vec3(luma(c.rgb)), contrast).r);
    vec3 kept = saturateColor(c.rgb, saturation + 0.25 * pulse);
    vec3 col = mix(grey, kept, keep);
    fragColor = vec4(mix(src.rgb, sat3(col), sat(intensity)), src.a);
}
""",
    variants=[
        Variant("color-local", "Color local", "Local colour", photo="fx-woman-04", thumb=1.0,
                tags=["un color", "one colour", "color selectivo", "selective colour", "blanco y negro"]),
    ],
)

# Red horror: a monochrome in Colour, flicker, jolts of the camera and grain.
HORROR = Family(
    key="est_horror", category="estilo",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#b80805"), Param("flicker", "Flicker", 0.0, 2.0, 1.0),
            Param("grain", "Grain", 0.0, 2.0, 1.0), Param("contrast", "Contrast", 0.5, 2.0, 1.3)],
    photo="man", tags=["terror", "horror", "miedo", "scary", "filtro", "filter"],
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    float t = u_time * speed;
    vec4 src = S(uv);
    float jolt = step(0.8, hash11(floor(t * 5.0) + 1.3)) * min(flicker, 1.5);
    vec2 sh = shake2(t, 18.0) * 0.012 * jolt;
    vec4 c = cam(uv, vec2(0.5), 1.06 + 0.02 * jolt, sh.x * 0.3, sh);
    float l = contrastColor(vec3(luma(c.rgb)), contrast).r;
    vec3 col = mix(vec3(0.02, 0.0, 0.0), color, smoothstep(0.0, 0.55, l));
    col = mix(col, mix(color, vec3(1.0, 0.92, 0.88), 0.58), smoothstep(0.55, 1.0, l));
    float flick = 1.0 - flicker * (0.38 * step(0.82, hash11(floor(t * 12.0) + 7.0)) + 0.08 * sin(t * 31.0) * sin(t * 7.0));
    col *= flick;
    col *= 0.35 + 0.65 * vignette(uv, 0.28, 0.55);
    col += (hash12(uv * u_resolution + floor(t * 24.0)) - 0.5) * 0.07 * grain;
    fragColor = vec4(mix(src.rgb, sat3(col), sat(intensity)), src.a);
}
""",
    variants=[
        Variant("terror-rojo", "Terror rojo", "Red horror", photo="fx-man-04", thumb=1.3, tags=["rojo", "red"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Psychedelic. MODE 0 liquid wave (marbled warp, colours flowing around the subject), 1 swirl.
PSY = Family(
    key="est_psy", category="estilo",
    params=[INTENSITY, SPEED, Param("frequency", "Frequency", 0.3, 3.0, 1.0), Param("amount", "Amount", 0.0, 2.0, 1.0),
            Param("hue", "Hue", 0.0, 1.0, 0.0), Param("saturation", "Saturation", 0.0, 2.5, 1.2)],
    photo="dancer",
    tags=["psicodelico", "psychedelic", "trippy", "onda", "wave", "color"],
    defines={"MODE": 0},
    body=r"""
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float t = u_time * speed;
    vec2 p = toP(uv);
    vec3 col;
    if (MODE < 0.5) {
        vec2 q = p * 2.4 * frequency;
        vec2 w = vec2(fbm(q + vec2(t * 0.35, 0.0)), fbm(q + vec2(5.2, -t * 0.3)));
        float far = 0.35 + 0.65 * smoothstep(0.08, 0.42, length(p * vec2(1.3, 0.8)));
        vec2 off = (w - 0.5) * 0.16 * far * intensity * amount;
        vec4 c = Sm(uv + off / vec2(aspect(), 1.0));
        float l = luma(c.rgb);
        float band = fbm(q * 1.2 + w * 2.5 + vec2(t * 0.12, 0.0));
        float stripes = 0.5 + 0.5 * sin(band * 26.0 - t * 1.5);
        vec3 pal = 0.5 + 0.5 * cos(TAU * (band * 1.4 + t * 0.08 + hue + vec3(0.55, 0.68, 0.85)));
        vec3 liquid = pal * (0.45 + 0.9 * l) * (0.8 + 0.3 * stripes);
        col = mix(c.rgb, liquid, 0.25 + 0.5 * far);
    } else {
        float r = length(p);
        float ang = (1.0 + 0.6 * sin(t * 0.9)) * pow(1.0 - smoothstep(0.0, 0.8, r), 2.0) * smoothstep(0.03, 0.25, r) * intensity * amount;
        vec2 sp = rot(ang) * p / 1.08;
        vec4 c = Sm(fromP(sp));
        float a = atan(sp.y, sp.x);
        float blobs = sin(a * 3.0 + r * 9.0 * frequency - t * 2.0) * 0.5 + 0.5;
        vec3 pal = hueShift(mix(vec3(0.95, 0.15, 0.85), vec3(0.2, 0.95, 0.45), blobs), hue);
        vec3 hs = hueShift(c.rgb, r * 0.7 * frequency - t * 0.2 + hue);
        col = mix(c.rgb, hs, 0.55);
        col = mix(col, overlayBlend(col, pal), 0.55 * smoothstep(0.08, 0.5, r));
    }
    col = saturateColor(col, saturation);
    fragColor = vec4(mix(src.rgb, sat3(col), sat(intensity)), src.a);
}
""",
    variants=[
        Variant("onda-psicodelica", "Onda psicodélica", "Psychedelic wave", photo="fx-woman-03", thumb=1.2),
        Variant("giro-psicodelico", "Giro psicodélico", "Psychedelic swirl", defines={"MODE": 1},
                params={"saturation": 1.25},
                photo="fx-dancer-06", thumb=1.0, tags=["giro", "swirl", "espiral"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# A skull ghost that lunges out of the face, twice a second, over a cold, darker picture.
SKULL = Family(
    key="est_skull", category="estilo",
    params=[INTENSITY, SPEED, Param("size", "Size", 0.4, 2.0, 1.0), Param("center_x", "Center X", 0.0, 1.0, 0.5),
            Param("center_y", "Center Y", 0.0, 1.0, 0.4), Param("color", "Colour", default="#cfe6ff"),
            Param("opacity", "Opacity", 0.0, 1.5, 1.0), Param("flicker", "Flicker", 0.0, 2.0, 1.0)],
    photo="woman", tags=["calavera", "skull", "fantasma", "ghost", "terror", "halloween", "espiritu"],
    body=COMMON + r"""
// Skull in its own units (about 2 tall, y down). x: body distance, y: holes (eyes, nose), z: teeth lines.
vec3 skull(vec2 q) {
    float cran = sdCircle(q - vec2(0.0, -0.22), 0.82);
    float cheek = sdRoundBox(q - vec2(0.0, 0.32), vec2(0.6, 0.3), 0.22);
    float jaw = sdRoundBox(q - vec2(0.0, 0.76), vec2(0.38, 0.2), 0.14);
    float body = smin(smin(cran, cheek, 0.18), jaw, 0.12);
    vec2 e = vec2(abs(q.x) - 0.32, q.y - 0.08);
    float eyes = length(e * vec2(1.0, 1.15)) - 0.22;
    vec2 n = q - vec2(0.0, 0.42);
    float nose = max(abs(n.x) * 1.7 + n.y * 0.6 - 0.1, -n.y - 0.12);
    float holes = min(eyes, nose);
    float inJaw = step(0.6, q.y) * step(q.y, 0.9) * step(abs(q.x), 0.3);
    float teeth = inJaw * (smoothstep(0.06, 0.0, abs(fract(q.x * 6.0) - 0.5) - 0.42) + smoothstep(0.03, 0.0, abs(q.y - 0.75)));
    return vec3(body, holes, teeth);
}
// Light and darkness of one ghost (x: added light, y: how much it darkens under the sockets).
vec2 ghost(vec2 p, vec2 c, float sc) {
    vec2 q = (p - c) / sc;
    vec3 s = skull(q);
    float w = 0.04;
    float fill = fillSd(s.x, w);
    float rim = exp(-abs(s.x) / 0.08);
    float holes = fillSd(s.y, w) * fill;
    float light = fill * (0.45 + 0.25 * (1.0 - smoothstep(-0.8, 0.2, s.x))) + rim * 0.5;
    light *= (1.0 - holes) * (1.0 - s.z * 0.6);
    return vec2(light, holes);
}
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float t = u_time * speed;
    vec2 c = toP(vec2(center_x, center_y));
    float sz = 0.15 * size;
    vec2 p = toP(uv);
    float flick = 1.0 - 0.25 * flicker * (1.0 - step(0.3, hash11(floor(t * 14.0))));
    // The picture: colder and darker, with a shiver when a ghost leaves.
    float cyc = phase(t, 1.0);
    float hit = exp(-cyc * 6.0);
    vec4 b = cam(uv, vec2(0.5), 1.04, 0.0, shake2(t, 20.0) * 0.004 * hit);
    vec3 base = mix(b.rgb, vec3(luma(b.rgb)) * vec3(0.8, 0.92, 1.05), 0.5) * (0.78 - 0.1 * hit);
    vec3 col = base;
    // A faint skull over the face, and two ghosts that fly out of it, one after the other.
    vec2 g0 = ghost(p, c, sz);
    col = mix(col, col * 0.35, g0.y * 0.6);
    col = addLight(col, color, g0.x * 0.35 * flick * opacity);
    for (int i = 0; i < 2; ++i) {
        float ph = fract(cyc + float(i) * 0.5);
        float sc = sz * (1.0 + 1.1 * easeOut(ph));
        vec2 gc = c + vec2(0.04 * sin(t * 3.0 + float(i) * 2.0), -0.12 * easeOut(ph));
        float a = (1.0 - ph) * smoothstep(0.0, 0.05, ph) * opacity;
        vec2 g = ghost(p, gc, sc);
        col = mix(col, col * 0.5, g.y * a * 0.5);
        col = addLight(col, color, g.x * a * 0.7 * flick);
    }
    fragColor = vec4(mix(src.rgb, sat3(col), sat(intensity)), src.a);
}
""",
    variants=[
        Variant("fantasma-calavera", "Fantasma calavera", "Skull ghost", photo="fx-woman-08",
                params={"center_x": 0.5, "center_y": 0.36}, thumb=1.1),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Pieces of holey cheese tumbling down around the picture, in three depth layers.
CHEESE = Family(
    key="est_cheese", category="estilo",
    params=[INTENSITY, SPEED, Param("density", "Density", 0.2, 2.0, 1.0), Param("color", "Colour", default="#f6c53c"),
            Param("size", "Size", 0.4, 2.0, 1.0)],
    photo="woman", tags=["queso", "cheese", "divertido", "fun", "comida", "food"],
    body=r"""
float sdTri(vec2 p, vec2 p0, vec2 p1, vec2 p2) {
    vec2 e0 = p1 - p0, e1 = p2 - p1, e2 = p0 - p2;
    vec2 v0 = p - p0, v1 = p - p1, v2 = p - p2;
    vec2 pq0 = v0 - e0 * sat(dot(v0, e0) / dot(e0, e0));
    vec2 pq1 = v1 - e1 * sat(dot(v1, e1) / dot(e1, e1));
    vec2 pq2 = v2 - e2 * sat(dot(v2, e2) / dot(e2, e2));
    float s = sign(e0.x * e2.y - e0.y * e2.x);
    vec2 d = min(min(vec2(dot(pq0, pq0), s * (v0.x * e0.y - v0.y * e0.x)),
                     vec2(dot(pq1, pq1), s * (v1.x * e1.y - v1.y * e1.x))),
                 vec2(dot(pq2, pq2), s * (v2.x * e2.y - v2.y * e2.x)));
    return -sqrt(d.x) * sign(d.y);
}
// One piece in a layer: returns colour (rgb) and coverage (a).
vec4 pieces(vec2 p, float t, float scale, float fall, float seed, float soft) {
    p *= scale / size;
    p.y -= t * fall / size;
    vec2 cell = floor(p), f = fract(p) - 0.5;
    float h = hash12(cell + seed);
    if (h > 0.22 * density) return vec4(0.0);
    vec2 o = (hash22(cell + seed * 1.7) - 0.5) * 0.3;
    float sway = sin(t * 1.3 + h * 20.0) * 0.06;
    vec2 q = rot(t * (hash12(cell + 4.0) - 0.5) * 2.5 + h * 6.0) * (f - o - vec2(sway, 0.0));
    float sz = 0.22 + 0.08 * hash12(cell + 9.1);
    q /= sz;
    float kind = hash12(cell + 3.3);
    float d = kind < 0.5 ? sdTri(q, vec2(-1.0, 0.55), vec2(1.0, 0.55), vec2(-0.1, -0.75)) - 0.08
                         : sdRoundBox(q, vec2(0.75, 0.6), 0.15);
    float e = soft / sz / size;
    float cover = fillSd(d, e);
    if (cover <= 0.0) return vec4(0.0);
    vec3 col = color * (0.85 + 0.25 * (-q.y * 0.5 + 0.5));
    // Holes: darker, with an inner shadow on one side.
    float holes = 0.0, shade = 0.0;
    for (int i = 0; i < 3; ++i) {
        vec2 hc = (hash22(cell + float(i) * 7.3 + seed) - 0.5) * vec2(1.0, 0.7);
        float hr = 0.14 + 0.12 * hash12(cell + float(i) * 2.1);
        float hd = length(q - hc) - hr;
        float m = fillSd(hd, e);
        holes = max(holes, m);
        shade = max(shade, m * smoothstep(-hr, hr, (q - hc).y));
    }
    col = mix(col, color * vec3(0.78, 0.6, 0.3), holes);
    col *= 1.0 - shade * 0.35;
    col *= 1.0 - 0.3 * smoothstep(-0.12, 0.0, d);          // darker rind at the edge
    return vec4(col, cover);
}
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec3 col = src.rgb;
    // Far, middle, near: smaller and slower far away, bigger and softer close.
    vec4 l0 = pieces(p, t, 6.5, 0.8, 1.0, 0.03);
    vec4 l1 = pieces(p + vec2(0.3, 0.0), t, 4.2, 1.1, 7.0, 0.025);
    vec4 l2 = pieces(p + vec2(0.7, 0.0), t, 2.4, 1.5, 13.0, 0.05);
    vec4 sh = pieces(p + vec2(0.7, 0.0) - vec2(0.012, 0.02), t, 2.4, 1.5, 13.0, 0.08);
    col = mix(col, mix(l0.rgb, col, 0.35), l0.a * sat(intensity));
    col = mix(col, l1.rgb, l1.a * sat(intensity));
    col = mix(col, col * 0.55, sh.a * 0.5 * sat(intensity) * (1.0 - l2.a));
    col = mix(col, l2.rgb, l2.a * sat(intensity));
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("trozos-de-queso", "Trozos de queso", "Cheese pieces", photo="fx-woman-07", thumb=1.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# A computer screen searching the picture: CRT curve and scanlines, a search bar typing, a magnifier box that
# jumps between spots and locks on, a loading bar.
SEARCH = Family(
    key="est_search", category="estilo",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#39d6ff"), Param("zoom", "Zoom", 1.0, 3.0, 1.7),
            Param("size", "Size", 0.5, 2.0, 1.0)],
    photo="man", tags=["busqueda", "search", "pantalla", "screen", "computadora", "computer", "escaner"],
    body=COMMON + r"""
vec2 target(float i) { return vec2(0.3, 0.28) + hash22(vec2(i, 3.7)) * vec2(0.4, 0.4); }
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    float t = u_time * speed;
    // Screen curve.
    vec2 d = uv - 0.5;
    vec2 cuv = 0.5 + d * (0.94 + 0.12 * dot(d, d));
    float scr = fillSd(sdRoundBox(toP(cuv), vec2(aspect() * 0.5, 0.5) - 0.01, 0.04), 0.004);
    vec3 col = S(cuv).rgb;
    col = mix(col, col * vec3(0.85, 1.05, 1.1), 0.35);
    // The magnifier: moves between spots, then locks on.
    float seg = floor(t / 1.1), f = fract(t / 1.1);
    vec2 pos = mix(target(seg), target(seg + 1.0), easeInOut(linstep(0.0, 0.45, f)));
    float lock = linstep(0.45, 0.55, f);
    vec2 pp = toP(cuv) - toP(pos);
    vec2 bs = vec2(0.13, 0.13) * size * (1.0 - 0.12 * lock * (1.0 - linstep(0.55, 0.7, f)));
    float box = sdRoundBox(pp, bs, 0.01);
    float inside = fillSd(box, 0.003);
    vec3 zoomed = S(pos + (cuv - pos) / zoom).rgb * 1.12;
    col = mix(col * 0.72, zoomed, inside);
    // Corner brackets and a crosshair.
    vec2 ap = abs(pp);
    float corner = step(bs.x - 0.04, ap.x) * step(bs.y - 0.04, ap.y);
    float frameLine = smoothstep(0.004, 0.0015, abs(box)) * corner;
    float cross_ = (smoothstep(0.003, 0.001, abs(pp.x)) * step(ap.y, 0.025) + smoothstep(0.003, 0.001, abs(pp.y)) * step(ap.x, 0.025));
    float blink = 0.6 + 0.4 * step(0.5, fract(t * 4.0));
    col = addLight(col, color, frameLine * 1.2 + cross_ * 0.8 * blink + exp(-abs(box) / 0.01) * 0.25 * lock);
    // Search bar at the top: magnifier icon, typing dots and a cursor.
    vec2 sp = toP(cuv) - vec2(0.0, -0.36);
    float bar = sdRoundBox(sp, vec2(0.36, 0.045), 0.045);
    col = mix(col, vec3(0.05, 0.08, 0.1), fillSd(bar, 0.003) * 0.75);
    col = addLight(col, color, smoothstep(0.003, 0.001, abs(bar)) * 0.9);
    vec2 ip = sp - vec2(-0.31, 0.0);
    float icon = smoothstep(0.004, 0.0015, abs(length(ip + vec2(0.004, 0.004)) - 0.014))
               + smoothstep(0.004, 0.0015, sdSegment(ip, vec2(0.006, 0.006), vec2(0.02, 0.02)));
    float typed = floor(fract(t / 2.2) * 14.0);
    float dx = sp.x + 0.25;
    float slot = floor(dx / 0.04);
    float dots = step(0.0, dx) * step(slot, typed - 1.0) * smoothstep(0.012, 0.008, length(vec2(fract(dx / 0.04) * 0.04 - 0.02, sp.y)));
    float cursor = step(abs(dx - typed * 0.04 + 0.006), 0.003) * step(abs(sp.y), 0.025) * step(0.5, fract(t * 2.5));
    col = addLight(col, vec3(1.0), (icon + dots + cursor) * 0.9);
    // Loading bar at the bottom.
    vec2 lp = toP(cuv) - vec2(0.0, 0.4);
    float track = sdRoundBox(lp, vec2(0.3, 0.008), 0.008);
    float prog = fract(t / 2.2);
    float fillBar = fillSd(track, 0.002) * step(lp.x + 0.3, prog * 0.6);
    col = mix(col, vec3(0.1), fillSd(track, 0.002) * 0.6);
    col = addLight(col, color, fillBar * 1.2);
    // Scanlines, grain and the dark bezel.
    col *= 0.86 + 0.14 * sin(cuv.y * u_resolution.y * TAU / (3.0 * rs()));
    col += (hash12(uv * u_resolution + floor(t * 30.0)) - 0.5) * 0.04;
    col *= 0.6 + 0.4 * vignette(uv, 0.35, 0.5);
    col = mix(vec3(0.02, 0.025, 0.03), col, scr);
    fragColor = vec4(mix(src.rgb, sat3(col), sat(intensity)), src.a);
}
""",
    variants=[
        Variant("busqueda-de-respuesta", "Búsqueda de respuesta", "Answer search", photo="fx-man-01", thumb=0.9),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Neon scans: a bright band sweeps across; the edges it touches light up in two neon colours, and a fading rim
# stays behind it. Flags add a grid, halftone dots, an RGB split, a ring (shockwave) or electric veins.
# Two families share the body: est_scan lights every edge of the picture; est_scan_person ("requires": "depth")
# lights only the outline of the person (the near part of the depth map) and falls back to every edge without it.
SCAN_PARAMS = [INTENSITY, SPEED, Param("color_a", "Colour A", default="#16b8ff"),
               Param("color_b", "Colour B", default="#ff2fb4"), Param("width", "Width", 0.3, 3.0, 1.0),
               Param("angle", "Angle", -180.0, 180.0, 0.0), Param("glow_amt", "Glow", 0.0, 3.0, 1.0),
               Param("brightness", "Brightness", 0.0, 1.0, 0.55)]
SCAN_DEFINES = {"PERIOD": 2.0, "RIM": 0.6, "ALWAYS": 0.0, "BANDFILL": 0.25, "CORE": 0.6,
                "GRID": 0.0, "DOTS": 0.0, "RGBSPLIT": 0.0, "RING": 0.0, "ELECTRIC": 0.0, "PINGPONG": 0.0,
                "SPECTRAL": 0.0, "TINT": 0.3}

SCAN_BODY = COMMON + r"""
//@OUTLINE
void main() {
    vec2 uv = v_texCoord;
    vec4 src = S(uv);
    vec2 p = toP(uv);
    float t = u_time * speed;
    float a = aspect();
    // Where the band is: s runs 0..1 across the frame along the scan direction (or out from the centre).
    float s;
    if (RING > 0.5) s = length(p) / (0.5 * sqrt(a * a + 1.0));
    else {
        float ang = radians(angle);
        vec2 dir = vec2(cos(ang), sin(ang));
        float ext = 0.5 * (abs(dir.x) * a + abs(dir.y));
        s = dot(p, dir) / ext * 0.5 + 0.5;
    }
    float front = PINGPONG > 0.5 ? 0.5 + 0.62 * sin(t * TAU / PERIOD) : -0.2 + 1.4 * phase(t, PERIOD);
    float bw = 0.07 * width;
    float dist = s - front;
    float band = exp(-dist * dist / (bw * bw));
    float core = exp(-dist * dist / (bw * bw * 0.03));
    float behind = PINGPONG > 0.5 ? 1.0 - smoothstep(-0.02, 0.02, dist) : step(dist, 0.0) * exp(dist / 0.45);
    // Base: the picture darker and tinted; an RGB split inside the band.
    vec3 base = src.rgb;
    if (RGBSPLIT > 0.5) {
        vec2 o = vec2(0.012, 0.0) * (band + 0.3 * behind);
        base = vec3(S(uv + o).r, src.g, S(uv - o).b);
    }
    base *= brightness * backdrop(uv);
    base = mix(base, base * mix(color_a, vec3(1.0), 0.4) * 1.3, TINT);
    // Outlines, thin and wide, make the neon.
    float r = rs();
    float e1 = outline(uv, 1.0 * r), e2 = outline(uv, 3.0 * r);
    float edge = sat(e1 * 1.8 + e2 * 0.8) * glow_amt;
    float g = SPECTRAL > 0.5 ? uv.x + 0.25 * sin(t * 0.8 + uv.y * 3.0) : 0.5 + dist / (bw * 3.0);
    vec3 neon = mix(color_a, color_b, sat(g));
    float lit = ELECTRIC > 0.5 ? ALWAYS : band * 2.4 + behind * RIM + ALWAYS;
    vec3 glow = neon * edge * lit;
    glow += neon * band * BANDFILL + vec3(1.0) * core * CORE;
    if (GRID > 0.5) {
        vec2 gp = p * 9.0;
        vec2 gl = smoothstep(0.05, 0.0, abs(fract(gp) - 0.5) - 0.44);
        glow += neon * max(gl.x, gl.y) * 0.3 * (band + behind * 0.35);
    }
    if (DOTS > 0.5) {
        float l = luma(src.rgb);
        float ht = halftone(uv, l * 0.9, vec2(0.0));
        glow += neon * ht * (0.55 * (band + behind) + 0.25) * smoothstep(0.08, 0.3, l);
    }
    if (ELECTRIC > 0.5) {
        float bt = stepTime(t, 15.0);
        float v = 1.0 - abs(fbm(p * 7.0 + vec2(bt * 0.9, -bt * 0.6)) * 2.0 - 1.0);
        float veins = smoothstep(0.93, 0.985, v) * sat(e2 * 1.6) * smoothstep(0.15, 0.4, luma(src.rgb) + 0.2);
        float fl = 0.7 + 0.3 * hash11(bt * 7.0);
        glow += (mix(color_a, vec3(1.0), 0.4) * veins * 1.4 + neon * e1 * 0.6) * fl * glow_amt;
    }
    // Scanlines inside the light.
    glow *= 0.78 + 0.22 * sin(uv.y * u_resolution.y * TAU / (3.0 * r));
    vec3 col = addLight(mix(src.rgb, base, sat(intensity)), glow, intensity);
    fragColor = vec4(col, src.a);
}
"""

OUTLINE_EDGES = r"""
float outline(vec2 uv, float spread) { return edges(uv, spread); }
float backdrop(vec2 uv) { return 1.0; }
"""

# The person = the near part of the depth map. Its outline is where that mask changes within a few pixels; the
# person's own inner lines (face, clothes) glow a little too. Without a depth map: every edge, as est_scan.
OUTLINE_PERSON = r"""
float personAt(vec2 uv) { return smoothstep(CUT - 0.08, CUT + 0.08, driftDepth(uv)); }
float outline(vec2 uv, float spread) {
    if (u_hasDepth < 0.5) return edges(uv, spread);
    vec2 o = px() * spread * 2.0;
    float c = personAt(uv);
    float l = personAt(uv - vec2(o.x, 0.0)), rr = personAt(uv + vec2(o.x, 0.0));
    float u = personAt(uv - vec2(0.0, o.y)), d = personAt(uv + vec2(0.0, o.y));
    float hi = max(max(max(l, rr), max(u, d)), c), lo = min(min(min(l, rr), min(u, d)), c);
    float rim = sat((hi - lo) * 2.0);
    return max(rim, edges(uv, spread) * c * INNER);
}
// The background goes a little darker than the person, so the lit outline reads.
float backdrop(vec2 uv) { return u_hasDepth > 0.5 ? mix(1.0 - BG_DIM, 1.0, personAt(uv)) : 1.0; }
"""

SCAN_TAGS = ["escaneo", "scan", "neon", "ciencia ficcion", "sci-fi", "cyber", "brillo", "glow"]

SCAN = Family(
    key="est_scan", category="estilo", params=SCAN_PARAMS, photo="cyber", tags=SCAN_TAGS,
    defines=dict(SCAN_DEFINES), body=SCAN_BODY.replace("//@OUTLINE", OUTLINE_EDGES),
    variants=[
        Variant("escaneo-de-ondas-de-choque", "Escaneo de ondas de choque", "Shockwave scan", photo="fx-woman-05",
                defines={"RING": 1, "DOTS": 1, "PERIOD": 1.5, "RIM": 0.5},
                params={"color_a": "#2a9bff", "color_b": "#ff3fc8", "brightness": 0.45}, thumb=0.8,
                tags=["onda de choque", "shockwave", "halftone"]),
        Variant("escaneo-de-rayos", "Escaneo de rayos", "Ray scan", photo="fx-cyber-01",
                defines={"TINT": 0.0, "RIM": 0.3, "BANDFILL": 0.3, "CORE": 0.5, "PERIOD": 1.6},
                params={"color_a": "#c8d6ff", "color_b": "#8fa8ff", "width": 1.0, "angle": 34.4, "brightness": 0.65},
                thumb=0.8, tags=["rayo", "ray", "luz", "light"]),
    ],
)

SCAN_PERSON = Family(
    key="est_scan_person", category="estilo", params=SCAN_PARAMS, photo="cyber", requires="depth",
    tags=SCAN_TAGS + ["persona", "person", "contorno", "outline", "silueta", "silhouette"],
    defines={**SCAN_DEFINES, "CUT": 0.55, "INNER": 0.35, "BG_DIM": 0.3},
    body=SCAN_BODY.replace("//@OUTLINE", OUTLINE_PERSON),
    variants=[
        Variant("escaneo-electrooptico", "Escaneo electroóptico", "Electro-optic scan", photo="fx-dancer-02",
                defines={"TINT": 0.35, "RIM": 0.9, "BANDFILL": 0.15},
                params={"color_a": "#2fd2ff", "color_b": "#3b6bff", "angle": 90.0, "brightness": 0.8}, thumb=1.0),
        Variant("escaneo-de-ciencia-ficcion-01", "Escaneo de ciencia ficción 01", "Sci-fi scan 01",
                photo="fx-woman-05", defines={"RIM": 0.8}, params={"angle": 0.0, "brightness": 0.45}, thumb=1.1),
        Variant("escaneo-de-ciencia-ficcion-02", "Escaneo de ciencia ficción 02", "Sci-fi scan 02",
                photo="fx-cyber-05", defines={"GRID": 1, "RIM": 0.7},
                params={"color_a": "#20e0ff", "color_b": "#ff3a9a", "angle": 90.0, "brightness": 0.5}, thumb=1.1),
        Variant("exploracion-espectral", "Exploración espectral", "Spectral exploration", photo="fx-cyber-03",
                defines={"SPECTRAL": 1, "ALWAYS": 0.7, "RIM": 0.6, "PERIOD": 2.5},
                params={"color_a": "#2a7bff", "color_b": "#ff2fa8", "angle": 0.0, "brightness": 0.45}, thumb=1.2),
        Variant("escaneo-de-rayos-04", "Escaneo de rayos 04", "Ray scan 04", photo="fx-cyber-03",
                defines={"RIM": 0.7, "BANDFILL": 0.45, "CORE": 1.0, "PERIOD": 1.8},
                params={"color_a": "#ff3fb0", "color_b": "#3a7dff", "width": 1.2, "angle": 43.0, "brightness": 0.5},
                thumb=0.9, tags=["rayo", "ray"]),
        Variant("escaneo-de-rayos-ciberneticos-01", "Escaneo de rayos cibernéticos 01", "Cyber ray scan 01",
                photo="fx-woman-05", defines={"PINGPONG": 1, "PERIOD": 3.0, "RIM": 1.0, "BANDFILL": 0.35, "CORE": 1.1},
                params={"color_a": "#ff2fa8", "color_b": "#2fb8ff", "brightness": 0.4}, thumb=0.6, tags=["cyberpunk"]),
        Variant("escaneo-de-rayos-ciberneticos-02", "Escaneo de rayos cibernéticos 02", "Cyber ray scan 02",
                photo="fx-cyber-05", defines={"PINGPONG": 1, "PERIOD": 2.6, "RGBSPLIT": 1, "RIM": 0.9, "BANDFILL": 0.3,
                                              "CORE": 1.0},
                params={"color_a": "#ff3366", "color_b": "#22e5ff", "brightness": 0.55}, thumb=0.6,
                tags=["cyberpunk", "rgb"]),
        Variant("venas-electricas", "Venas eléctricas", "Electric veins", photo="fx-dancer-02",
                defines={"ELECTRIC": 1, "PERIOD": 2.0, "RIM": 0.0, "BANDFILL": 0.0, "CORE": 0.0, "TINT": 0.2},
                params={"color_a": "#5fd8ff", "color_b": "#a25bff", "width": 0.7, "brightness": 0.7}, thumb=1.0,
                tags=["electricidad", "electricity", "rayos", "lightning", "venas", "veins"]),
    ],
)

FAMILIES = [CARTOON, COMIC_PAGE, MOSAIC, LOCAL, HORROR, PSY, SKULL, CHEESE, SEARCH, SCAN, SCAN_PERSON]
