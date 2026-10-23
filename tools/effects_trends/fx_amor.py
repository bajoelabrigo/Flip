"""Efectos › Tendencias › Amor: hearts, pink glows, a heart made of sparkles, neon hearts, heart bokeh, a pink frame
and a love collage of photo frames. Our own shaders (Flip Studio); the cards follow the CATALOG.md section fx_amor."""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)
DENSITY = Param("density", "Density", 0.2, 2.0, 1.0)
SIZE = Param("size", "Size", 0.4, 2.0, 1.0)
CX = Param("centerx", "Center X", 0.0, 1.0, 0.5)
CY = Param("centery", "Center Y", 0.0, 1.0, 0.53)
FREQ = Param("frequency", "Frequency", 0.3, 3.0, 1.0)
GLOW = Param("glow", "Glow", 0.0, 2.0, 1.0)
SPREAD = Param("spread", "Spread", 0.0, 1.0, 0.3)


def colour(default: str) -> Param:
    return Param("color", "Colour", default=default)


# Shared GLSL: one layer of hearts scattered in cells (each one moved inside its cell, turned and sized at random).
# Returns (fill, distance / radius, twinkle, hash) so each family draws them its own way.
HEART_LAYER = r"""
vec4 heartLayer(vec2 p, float scale, vec2 drift, float seed, float dens, float r0, float soft) {
    vec2 g = p * scale + drift;
    vec2 cell = floor(g), f = fract(g) - 0.5;
    float h = hash12(cell + seed);
    if (h > dens) return vec4(0.0, 9.0, 0.0, 0.0);
    vec2 o = (hash22(cell + seed * 1.7) - 0.5) * 0.42;
    float r = r0 * (0.65 + 0.35 * hash12(cell + seed + 3.1));
    float a = (hash12(cell + seed + 5.3) - 0.5) * 0.7 + sin(u_time * 1.3 + h * 40.0) * 0.12;
    vec2 q = rot(a) * (f - o);
    float d = sdHeart(q, r) / r;
    float tw = 0.65 + 0.35 * sin(u_time * 3.1 + h * 57.0);
    return vec4(fillSd(d, soft), d, tw, hash12(cell + seed + 8.8));
}
"""

# ---------------------------------------------------------------------------------------------------------------
# Looks over the picture: a pink dreamy glow with a heart halo, heart ripples, a heartbeat, a romcom grade.
LOOK = Family(
    key="amor_look", category="amor", params=[INTENSITY, SPEED, colour("#ff7fb0"), CX, CY, SIZE, FREQ, GLOW], photo="woman",
    tags=["amor", "love", "corazon", "heart", "rosa", "pink", "romantico", "romantic"],
    defines={"MODE": "0"},
    body=HEART_LAYER + r"""
void main() {
    vec2 uv = v_texCoord;
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec4 src = S(uv);
    vec3 col = src.rgb;
    vec2 C = toP(vec2(centerx, centery));
#if MODE == 0
    // Claridad de amor: soft pink bloom, a hazy tint and a big glowing heart halo that breathes.
    vec3 bloom = brightGlow(uv, 0.05, 0.4);
    col = addLight(col, bloom * color, 0.6 * intensity * glow);
    col = mix(col, softLight(col, mix(vec3(0.5), color, 0.8)), 0.45 * intensity);
    col = mix(col, screen(col, color * 0.2), 0.45 * intensity);
    float br = 1.0 + 0.05 * sin(t * 2.2 * frequency);
    vec2 hc = C + vec2(0.0, sin(t * 0.9) * 0.015);
    float d1 = sdHeart(rot(-0.18) * (p - hc), 0.27 * size * br);
    float d2 = sdHeart(rot(0.2) * (p - vec2(0.3 * aspect(), -0.2 + sin(t * 1.1 + 1.0) * 0.02)), 0.09 * br);
    vec3 halo = color * (glowSd(d1, 0.006, 0.035 * glow) + 0.5 * fillSd(d1, 0.05) * 0.35)
              + vec3(1.0, 0.92, 0.95) * smoothstep(0.006, 0.0, abs(d1)) * 0.6
              + color * glowSd(d2, 0.004, 0.02) * 0.8;
    col = addLight(col, halo, 0.85 * intensity);
#elif MODE == 1
    // Ondas de amor: heart-shaped ripples run out from the middle, bending the picture and leaving a pink crest.
    vec2 off = vec2(0.0);
    vec3 crest = vec3(0.0);
    for (int i = 0; i < 3; ++i) {
        float k = fract(t * 0.45 * frequency + float(i) / 3.0);
        float d = sdHeart(p - C, (0.05 + k * 1.1) * size);
        float ring = exp(-abs(d) / 0.025) * (1.0 - k) * smoothstep(0.0, 0.15, k);
        float wave = sin(d * 70.0) * ring;
        off += normalize(p + 1e-4) * wave * 0.02;
        crest += color * ring * 1.1 * glow + vec3(1.0) * exp(-abs(d) / 0.006) * (1.0 - k) * 0.35;
    }
    col = S(uv + off * intensity * vec2(1.0 / aspect(), 1.0)).rgb;
    col = mix(col, softLight(col, mix(vec3(0.5), color, 0.5)), 0.3 * intensity);
    col = addLight(col, crest, intensity);
#elif MODE == 2
    // Pulso de corazón: a double heartbeat (lub-dub) pushes the camera and lights a deep red heart vignette.
    float per = 1.0 / max(frequency, 0.05);
    float b = beat(t, per, 0.11) + 0.75 * beat(t - 0.24, per, 0.11);
    vec2 cuv = camUv(uv, vec2(centerx, centery), 1.04 + 0.05 * b * intensity, 0.0, vec2(0.0));
    col = Sm(cuv).rgb;
    float d = sdHeart(p - C, (0.5 + 0.05 * b) * size);
    float outside = smoothstep(-0.12, 0.22, d);
    vec3 dark = color * 0.12 + col * color * 0.25;
    col = mix(col, dark, outside * sat(0.85 * intensity));
    col = mix(col, col * mix(vec3(1.0), color, 0.35), 0.5 * intensity);
    col = addLight(col, color * exp(-abs(d) / (0.05 * max(glow, 0.05))) * (0.25 + 0.75 * b), 0.8 * intensity);
#else
    // Romcom elevada: a lilac and pink dreamy grade, a glowing violet edge, hearts and sparkles floating up.
    col = mix(col, softLight(col, vec3(0.62, 0.45, 0.72)), 0.55 * intensity);
    col = addLight(col, brightGlow(uv, 0.04, 0.6) * vec3(1.0, 0.7, 0.95), 0.4 * intensity * glow);
    float edge = 1.0 - vignette(uv, 0.32, 0.45);
    col = addLight(col, vec3(0.5, 0.2, 0.95) * edge * edge * (0.85 + 0.15 * sin(t * 2.0 * frequency)), 0.6 * intensity * glow);
    vec3 acc = vec3(0.0);
    for (int i = 0; i < 2; ++i) {
        float sc = (4.0 + float(i) * 3.0) / max(size, 0.2);
        vec4 h = heartLayer(p, sc, vec2(sin(t * 0.4 + float(i)) * 0.4, t * (0.9 - 0.3 * float(i))), 11.0 + float(i) * 7.0, 0.3, 0.2, 0.1);
        vec3 hc = mix(color, vec3(1.0, 0.85, 0.3), step(0.7, h.w));
        acc += hc * (h.x * 0.9 + 0.5 * exp(-max(h.y, 0.0) * 6.0)) * h.z * edge * 1.4;
        vec2 g = p * (10.0 + float(i) * 6.0) + vec2(0.0, t * 1.2);
        vec2 c = floor(g);
        vec2 o = (hash22(c + 3.0 + float(i)) - 0.5) * 0.6;
        float on = step(hash12(c + 9.0 + float(i)), 0.25);
        acc += vec3(1.0, 0.9, 1.0) * twinkle(fract(g) - 0.5 - o, 0.09) * on * (0.5 + 0.5 * sin(u_time * 5.0 + hash12(c) * 30.0)) * edge;
    }
    col = addLight(col, acc, intensity);
#endif
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[
        Variant("claridad-de-amor", "Claridad de amor", "Love clarity", defines={"MODE": "0"},
                params={"centerx": 0.24, "centery": 0.52},
                tags=["brillo", "glow", "suave", "soft"], thumb=1.0),
        Variant("ondas-de-amor", "Ondas de amor", "Love waves", defines={"MODE": "1"},
                params={"color": "#ff6fa8", "centery": 0.52},
                tags=["ondas", "waves", "ripple"], thumb=1.0),
        Variant("pulso-de-corazon", "Pulso de corazón", "Heartbeat pulse", defines={"MODE": "2"},
                params={"color": "#e0103a"}, photo="couple", tags=["latido", "heartbeat", "pulso", "pulse", "rojo", "red"],
                thumb=1.05),
        Variant("romcom-elevada", "Romcom elevada", "Elevated romcom", defines={"MODE": "3"},
                params={"color": "#ff6fd0"}, tags=["romcom", "lila", "lilac", "sueño", "dreamy"], thumb=1.4),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Hearts drifting over the picture in three depth layers: soft pink bokeh, neon outlines, gold outlines, solid
# glossy hearts, or bokeh hearts gathered at the edges.
HEARTS = Family(
    key="amor_hearts", category="amor", params=[INTENSITY, SPEED, colour("#ff5fa0"), DENSITY, SIZE, SPREAD], photo="couple",
    tags=["corazones", "hearts", "amor", "love", "san valentin", "valentine"],
    defines={"STYLE": "0", "DIR": 0.5, "DARK": 0.0},
    body=HEART_LAYER + r"""
void main() {
    vec2 uv = v_texCoord;
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec4 src = S(uv);
    vec3 col = src.rgb * (1.0 - DARK * sat(intensity));
#if STYLE == 3
    float edge = smoothstep(0.18, 0.5, length(p * vec2(0.75, 1.0)) + 0.12 * fbm(p * 3.0 + t * 0.1));
#else
    float edge = 1.0;
#endif
    vec3 acc = vec3(0.0);
    for (int i = 0; i < 3; ++i) {
        float fi = float(i);
        float sc = (2.4 + fi * 1.9) / max(size, 0.2);
        float depth = 1.0 - fi * 0.25;
        vec2 drift = vec2(sin(t * 0.35 + fi * 2.0) * spread, -DIR * t * (1.0 - 0.25 * fi));
#if STYLE == 0
        vec4 h = heartLayer(p, sc, drift, 5.0 + fi * 13.0, 0.4 * density, 0.24, 0.35 - 0.1 * fi);
        // Soft out-of-focus hearts with a slightly brighter rim, like bokeh.
        float rim = exp(-abs(h.y) * 5.0) * 0.4;
        vec3 hc = mix(color, vec3(1.0, 0.75, 0.9), 0.25 * h.w);
        acc += hc * (h.x * 0.55 + rim) * depth * (0.7 + 0.3 * h.z);
#elif STYLE == 1
        vec4 h = heartLayer(p, sc * 0.7, drift, 21.0 + fi * 9.0, 0.25 * density, 0.2 + 0.03 * sin(t * 3.0 + fi), 0.05);
        float line = smoothstep(0.09, 0.0, abs(h.y)) + 0.55 * exp(-abs(h.y) * 9.0);
        acc += (color * line + vec3(1.0, 0.9, 0.95) * smoothstep(0.035, 0.0, abs(h.y)) * 0.8) * depth * h.z;
#elif STYLE == 2
        vec4 h = heartLayer(p, sc * 0.75, drift, 31.0 + fi * 5.0, 0.25 * density, 0.22, 0.05);
        float line = smoothstep(0.1, 0.0, abs(h.y)) + 0.6 * exp(-abs(h.y) * 8.0) + 0.15 * h.x;
        acc += color * line * depth * h.z;
        // Sparkles scattered between the hearts.
        vec2 g = p * (9.0 + fi * 5.0) + drift * 1.3;
        vec2 c = floor(g);
        vec2 o = (hash22(c + 4.0 + fi) - 0.5) * 0.6;
        float on = step(hash12(c + 2.0 + fi * 3.0), 0.22 * density);
        acc += mix(color, vec3(1.0), 0.6) * twinkle(fract(g) - 0.5 - o, 0.08) * on
             * (0.5 + 0.5 * sin(u_time * 4.0 + hash12(c) * 40.0)) * depth;
#elif STYLE == 3
        vec4 h = heartLayer(p, sc * 0.8, drift, 41.0 + fi * 7.0, 0.6 * density, 0.26, 0.3 - 0.08 * fi);
        vec3 hc = mix(color, vec3(1.0, 0.85, 0.45), h.w * 0.6);
        acc += hc * (h.x * 1.1 + exp(-abs(h.y) * 5.0) * 0.5) * depth * h.z * edge;
#else
        // Glossy solid hearts, drawn over the picture (near ones last).
        float k = 2.0 - fi;
        vec4 h = heartLayer(p, (2.6 + k * 1.9) / max(size, 0.2), vec2(sin(t * 0.35 + k * 2.0) * spread, -DIR * t * (1.0 - 0.25 * k)),
                            51.0 + k * 11.0, 0.3 * density, 0.22, 0.06);
        float shade = 0.75 + 0.25 * sat(-h.y * 2.0);
        vec3 hc = color * shade * mix(0.8, 1.15, h.w);
        hc = mix(hc, vec3(1.0), 0.6 * exp(-abs(h.y + 0.55) * 9.0) * 0.5);
        float a = h.x * (1.0 - 0.25 * k) * sat(intensity);
        col = mix(col, hc, a);
        acc += color * exp(-max(h.y, 0.0) * 8.0) * 0.25 * (1.0 - h.x);
        // Small round dots in between.
        vec2 g = p * (12.0 + k * 4.0) + vec2(0.0, -DIR * t * 1.2);
        vec2 c = floor(g);
        vec2 o = (hash22(c + 6.0 + k) - 0.5) * 0.6;
        float on = step(hash12(c + 1.0 + k), 0.3 * density);
        acc += color * smoothstep(0.1, 0.04, length(fract(g) - 0.5 - o)) * on * 0.8;
#endif
    }
    col = addLight(col, acc, intensity);
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[
        Variant("corazones-bokeh", "Corazones bokeh", "Bokeh hearts", defines={"STYLE": "3", "DIR": 0.25},
                params={"color": "#ff9a2e"}, tags=["bokeh", "dorado", "golden", "naranja", "orange"], thumb=1.2),
        Variant("corazones-de-neon", "Corazones de neón", "Neon hearts", defines={"STYLE": "1", "DIR": 0.3, "DARK": 0.3},
                params={"color": "#ff3d9a"}, tags=["neon", "neón", "brillo", "glow"], thumb=1.3),
        Variant("corazones-dorados", "Corazones dorados", "Golden hearts", defines={"STYLE": "2", "DIR": 0.25, "DARK": 0.3},
                params={"color": "#ffc861"}, tags=["dorado", "golden", "brillos", "sparkles"], thumb=1.0),
        Variant("lluvia-de-corazones-rosas", "Lluvia de corazones rosas", "Pink heart rain",
                defines={"STYLE": "0", "DIR": -0.6, "DARK": 0.1}, params={"color": "#ff5fae", "density": 1.4},
                tags=["lluvia", "rain", "rosa", "pink", "bokeh"], thumb=1.0),
        Variant("fondo-del-corazon-del-amor", "Fondo del corazón del amor", "Love heart background",
                defines={"STYLE": "4", "DIR": 0.35}, params={"color": "#ff4f8f"}, photo="woman",
                tags=["fondo", "background", "rosa", "pink"], thumb=1.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# A heart drawn with sparkles: still and twinkling, bursting out like a firework, or swirled until it forms.
SPARKLE_HEART = Family(
    key="amor_sparkle_heart", category="amor", params=[INTENSITY, SPEED, colour("#ffd9a8"), DENSITY, SIZE, CX, CY, GLOW],
    photo="couple", tags=["corazon", "heart", "brillos", "sparkles", "purpurina", "glitter", "amor", "love"],
    defines={"MODE": "0", "DARK": 0.35, "HUEMIX": 0.0},
    body=r"""
// Sparkles in cells; a cell lights when its particle (not the pixel) lies near the heart outline.
vec3 glitter(vec2 q, float scale, float seed, float R, float band, float fillAmt, float tt) {
    vec2 g = q * scale;
    vec2 cell = floor(g);
    vec2 o = (hash22(cell + seed) - 0.5) * 0.7;
    vec2 c = (cell + 0.5 + o) / scale;
    float d = sdHeart(c, R);
    float w = exp(-abs(d) / band) + fillAmt * fillSd(d, 0.02) + 0.04;
    float h = hash12(cell + seed + 2.7);
    if (h > w * 0.9 * density) return vec3(0.0);
    float r = 0.12 + 0.14 * hash12(cell + seed + 5.1);
    float tw = 0.35 + 0.65 * pow(0.5 + 0.5 * sin(tt * (3.0 + 4.0 * h) + h * 60.0), 2.0);
    vec3 tint = mix(color, hsv2rgb(vec3(hash12(cell + seed + 9.3), 0.55, 1.0)), HUEMIX);
    return tint * twinkle(fract(g) - 0.5 - o, r) * tw;
}
void main() {
    vec2 uv = v_texCoord;
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec4 src = S(uv);
    float R = 0.3 * size;
    vec2 q = p - toP(vec2(centerx, centery));
    float amp = 1.0, fillAmt = 0.08;
#if MODE == 1
    // Corazón de luces: the sparkles fly out from the middle into a heart, hang, fall a little and fade; loops.
    float k = phase(t, 2.6);
    float grow = 0.12 + 0.88 * easeOut(k / 0.35);
    q = q / grow;
    q.y -= k * k * 0.06;
    amp = (1.0 - linstep(0.62, 1.0, k)) * (0.6 + 0.4 * (1.0 - linstep(0.0, 0.5, k)));
    fillAmt = 0.25;
#elif MODE == 2
    // Remolino de corazones: the glitter is swirled around the middle and untwists into a heart.
    float sw = sin(t * 0.9) * 2.4;
    q = rot(sw * (0.6 - length(q)) * 2.0 + t * 0.4) * q;
    amp = 1.0;
#endif
    vec3 acc = glitter(q, 55.0, 1.0, R, 0.012, fillAmt, u_time) * 0.8
             + glitter(q, 32.0, 7.0, R, 0.018, fillAmt, u_time)
             + glitter(q, 18.0, 13.0, R, 0.028, fillAmt * 0.5, u_time) * 1.2;
    float d = sdHeart(q, R);
    vec3 halo = color * (exp(-abs(d) / 0.04) * 0.45 + exp(-abs(d) / 0.008) * 0.35) * glow;
    float dark = DARK * sat(intensity) * (0.6 + 0.4 * amp);
    vec3 col = src.rgb * (1.0 - dark);
    col = addLight(col, (acc * 2.6 + halo) * amp, intensity);
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[
        Variant("corazon-de-brillos", "Corazón de brillos", "Sparkle heart", defines={"MODE": "0"},
                tags=["romantico", "romantic"], thumb=1.0),
        Variant("corazon-de-luces", "Corazón de luces", "Heart of lights", defines={"MODE": "1"},
                params={"color": "#f2f4ff"}, tags=["fuegos artificiales", "fireworks", "estallido", "burst", "valentin"],
                thumb=0.9),
        Variant("remolino-de-corazones", "Remolino de corazones", "Heart swirl",
                defines={"MODE": "2", "HUEMIX": 0.6}, params={"color": "#ffd6ec"},
                tags=["remolino", "swirl", "giro", "spin"], thumb=1.8),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# A pink glowing frame with little hearts floating up along its sides.
FRAME = Family(
    key="amor_frame", category="amor", params=[INTENSITY, SPEED, colour("#ff8cc0"), Param("width", "Width", 0.2, 3.0, 1.0), DENSITY, SIZE, GLOW],
    photo="couple", tags=["marco", "frame", "borde", "border", "rosa", "pink", "corazones", "hearts", "amor", "love"],
    defines={"INSET": 0.035},
    body=HEART_LAYER + r"""
void main() {
    vec2 uv = v_texCoord;
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec4 src = S(uv);
    vec2 hb = vec2(aspect() * 0.5, 0.5) - INSET;
    float d = sdRoundBox(p, hb, 0.04);
    float breath = 0.85 + 0.15 * sin(t * 2.4);
    // Soft pink light coming in from the edges, then a glowing line.
    float inner = exp(min(-d, 0.5) * -14.0 / width);
    float outer = smoothstep(0.0, 0.03, d);
    vec3 light = color * (glowSd(d, 0.0035 * width, 0.02 * width) * breath + 0.55 * inner) * glow;
    light += vec3(1.0, 0.92, 0.96) * smoothstep(0.003 * width, 0.0, abs(d)) * 0.6;
    vec3 col = mix(src.rgb, mix(src.rgb, color, 0.55), outer * 0.85 * sat(intensity));
    // Hearts rising along the frame.
    vec3 acc = vec3(0.0);
    for (int i = 0; i < 2; ++i) {
        float fi = float(i);
        vec4 h = heartLayer(p, (7.0 + fi * 4.0) / max(size, 0.2), vec2(sin(t * 0.5 + fi) * 0.2, t * (0.6 - 0.15 * fi)), 3.0 + fi * 17.0, 0.45 * density, 0.22, 0.12);
        float near = exp(max(-d, 0.0) * -6.0);
        acc += mix(color, vec3(1.0, 0.8, 0.9), 0.3 * h.w) * (h.x * 0.9 + 0.4 * exp(-max(h.y, 0.0) * 6.0)) * h.z * near * (1.0 - 0.3 * fi);
    }
    col = addLight(col, light + acc, intensity);
    fragColor = vec4(sat3(col), src.a);
}
""",
    variants=[
        Variant("marco-rosa-de-amor", "Marco rosa de amor", "Pink love frame", tags=["san valentin", "valentine"],
                thumb=1.0),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Love collage: the picture blurred behind, three instant photo frames of it swaying, small red hearts stuck on.
COLLAGE = Family(
    key="amor_collage", category="amor", params=[INTENSITY, SPEED, colour("#ff8db5"), Param("blur", "Blur", 0.0, 2.0, 1.0),
            Param("brightness", "Brightness", 0.2, 1.2, 0.72), Param("rotation", "Rotation", 0.0, 3.0, 1.0), SIZE],
    photo="couple",
    tags=["collage", "fotos", "photos", "polaroid", "marcos", "frames", "amor", "love", "recuerdos", "memories"],
    body=HEART_LAYER + r"""
// One instant photo: centre c, photo half height h, turn a; shows the picture cropped about crop with zoom z.
vec4 polaroid(vec2 p, vec2 c, float h, float a, vec2 crop, float z, inout float shadow) {
    vec2 q = rot(-a) * (p - c);
    vec2 inner = vec2(h * aspect(), h);
    float bd = h * 0.08;
    vec2 outerHalf = inner + vec2(bd, bd);
    vec2 qo = q - vec2(0.0, bd * 1.6);               // thicker white border at the bottom
    float dOut = sdRoundBox(qo, outerHalf + vec2(0.0, bd * 1.6), 0.006);
    float dIn = sdBox(q, inner);
    shadow = max(shadow, fillSd(sdRoundBox(qo - vec2(0.012, 0.02), outerHalf + vec2(0.0, bd * 1.6), 0.02), 0.03) * 0.55);
    float aOut = fillSd(dOut, 0.0025);
    vec2 puv = crop + q / (2.0 * h) * vec2(1.0 / aspect(), 1.0) / z;
    vec3 photo = S(clamp(puv, 0.001, 0.999)).rgb;
    vec3 paper = vec3(0.97, 0.95, 0.93);
    vec3 c3 = mix(paper, photo, fillSd(dIn, 0.0015));
    return vec4(c3, aOut);
}
void main() {
    vec2 uv = v_texCoord;
    vec2 p = toP(uv);
    float t = u_time * speed;
    vec4 src = S(uv);
    float k = sat(intensity);
    vec3 bg = discBlur(uv, 0.06 * blur).rgb;
    bg = mix(bg, softLight(bg, mix(vec3(0.5), color, 0.7)), 0.6) * brightness;
    vec3 col = bg;
    float sh = 0.0;
    float sz = size;
    vec4 a = polaroid(p, vec2(-0.32 * aspect(), 0.06 + 0.01 * sin(t * 1.1)), 0.14 * sz, -0.16 + 0.03 * rotation * sin(t * 0.9), vec2(0.38, 0.45), 1.5, sh);
    vec4 b = polaroid(p, vec2(0.32 * aspect(), 0.03 + 0.01 * sin(t * 1.3 + 2.0)), 0.14 * sz, 0.14 + 0.03 * rotation * sin(t * 0.8 + 1.0), vec2(0.62, 0.42), 1.6, sh);
    float sh2 = 0.0;
    vec4 m = polaroid(p, vec2(0.0, -0.04 + 0.008 * sin(t * 1.0 + 4.0)), 0.23 * sz, 0.03 * rotation * sin(t * 0.7), vec2(0.5), 1.0, sh2);
    col *= 1.0 - sh;
    col = mix(col, a.rgb, a.a);
    col = mix(col, b.rgb, b.a);
    col *= 1.0 - sh2 * (1.0 - m.a);
    col = mix(col, m.rgb, m.a);
    // Two red hearts stuck on the corners of the middle photo, beating softly.
    float bt = 1.0 + 0.08 * beat(t, 1.0, 0.15);
    float d1 = sdHeart(rot(0.3) * ((p - vec2((0.23 * aspect() + 0.02) * sz, -0.25 * sz))), 0.055 * sz * bt);
    float d2 = sdHeart(rot(-0.35) * ((p - vec2((-0.23 * aspect() - 0.01) * sz, 0.18 * sz))), 0.04 * sz * bt);
    vec3 red = vec3(0.92, 0.12, 0.3);
    col = mix(col, red * (0.85 + 0.3 * sat(-d1 * 20.0)), fillSd(d1, 0.003));
    col = mix(col, red * (0.85 + 0.3 * sat(-d2 * 20.0)), fillSd(d2, 0.003));
    // A few soft hearts floating in the background, behind nothing important.
    vec4 hh = heartLayer(p, 5.0, vec2(0.0, t * 0.4), 9.0, 0.25, 0.2, 0.2);
    float free = (1.0 - a.a) * (1.0 - b.a) * (1.0 - m.a);
    col = addLight(col, color * hh.x * 0.5 * hh.z * free, 1.0);
    fragColor = vec4(mix(src.rgb, sat3(col), k), src.a);
}
""",
    variants=[
        Variant("collage-de-amor", "Collage de amor", "Love collage", thumb=1.0),
    ],
)

FAMILIES = [LOOK, HEARTS, SPARKLE_HEART, FRAME, COLLAGE]
