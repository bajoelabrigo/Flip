"""Efectos › Tendencias, Glitch: RGB splits, digital blocks, VCR tape, flickers, time echoes and beat hits.

Glitches come in bursts (burstEnv): a hit that flickers for a fraction of a period, then calm until the next.
What Filmora ties to the audio runs at a steady 120 BPM (one beat every 0.5 s).
"""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)

# Shared by every family: the burst envelope and a stepped random value.
COMMON = r"""
// Bursts: the first BURST of every BPERIOD seconds glitches (flickering at ~14 fps), the rest is calm.
float burstEnv(float t) {
    float k = floor(t / BPERIOD);
    float ph = fract(t / BPERIOD);
    float amp = 0.7 + 0.3 * hash11(k * 3.17 + 1.3);
    float on = 1.0 - smoothstep(BURST - 0.05, BURST, ph);
    float flick = mix(0.4, 1.0, step(0.3, hash11(floor(t * 14.0) * 1.73 + 5.1)));
    return on * flick * amp;
}
// A random value in -1..1 that changes fps times a second.
float jit(float t, float fps, float seed) { return hash11(floor(t * fps) * 7.31 + seed) * 2.0 - 1.0; }
"""


def body(src: str) -> str:
    return COMMON + src


# ---------------------------------------------------------------------------------------------------------------
# RGB split, chromatic aberration, edge ghosts, soul, punch and stretch: the picture with its channels apart.
SPLIT = Family(
    key="gl_split", category="glitch", params=[INTENSITY, SPEED], photo="woman",
    tags=["glitch", "rgb", "falla", "aberracion", "aberration", "split"],
    defines={"BPERIOD": 1.0, "BURST": 0.45, "SPLIT": 0.012, "DIR": (1.0, 0.0), "RADIAL": 0.0, "BASE": 0.15,
             "SHAKE": 0.0, "ZOOM": 1.0, "PUNCH": 0.0, "ROT": 0.0, "STRETCH": (0.0, 0.0), "EDGEONLY": 0.0,
             "EDGEA": "#ff2a6a", "EDGEB": "#20e8ff", "EDGEGAIN": 0.6, "SOUL": 0.0, "FLASH": 0.0, "BLUR": 0.0},
    body=body(r"""
void main() {
    float t = u_time * speed;
    float e = burstEnv(t) * intensity;
    float ec = max(e, BASE * intensity * (0.75 + 0.25 * sin(t * 3.0)));
    vec2 j = vec2(jit(t, 15.0, 1.0), jit(t, 15.0, 2.0));
    vec2 ctr = vec2(center_x, center_y);
    vec2 uv = camUv(v_texCoord, ctr, ZOOM + PUNCH * e, ROT * j.x * e, j * SHAKE * e);
    uv = 0.5 + (uv - 0.5) / (vec2(1.0) + STRETCH * e * (0.6 + 0.4 * abs(j.y)));
    vec2 o = RADIAL > 0.5 ? (uv - ctr) * vec2(aspect(), 1.0) * SPLIT * 3.0 * ec
                          : DIR * SPLIT * ec * (0.7 + 0.3 * j.x);
    vec4 c = Sm(uv);
    vec3 col;
    if (BLUR > 0.0) {
        vec2 d = DIR * BLUR * e;
        col = vec3(dirBlur(uv + o, d).r, dirBlur(uv, d).g, dirBlur(uv - o, d).b);
    } else {
        col = vec3(Sm(uv + o).r, c.g, Sm(uv - o).b);
    }
    if (EDGEONLY > 0.5) {
        // Colour outlines that shake away from the picture.
        col = c.rgb;
        vec3 glow = vec3(0.0);
        for (int i = 1; i <= 3; ++i) {
            float fi = float(i);
            vec2 d = o * fi * 1.8;
            glow += EDGEA * edges(uv + d, 1.5) / fi;
            glow += EDGEB * edges(uv - d, 1.5) / fi;
        }
        col = addLight(col, glow, EDGEGAIN * sat(ec * 1.5));
    }
    if (SOUL > 0.0) {
        // A copy that leaves the body on every beat (120 BPM) and fades out.
        float sp = phase(t, 0.5);
        vec2 su = ctr + (uv - ctr) / (1.0 + SOUL * easeOut(sp));
        vec3 g = Sm(su + vec2(o.x, 0.0)).rgb;
        col = mix(col, screen(col, g * vec3(0.85, 0.95, 1.1)), (1.0 - sp) * 0.65 * sat(intensity));
    }
    if (FLASH > 0.0) col = addLight(col, vec3(0.95, 0.97, 1.0), FLASH * e);
    fragColor = vec4(sat3(col), c.a);
}
"""),
    variants=[
        Variant("aberracion-cromatica", "Aberración cromática", "Chromatic aberration", photo="woman", thumb=0.3,
                defines={"RADIAL": 1.0, "BASE": 0.6, "SPLIT": 0.04, "BURST": 0.35},
                tags=["cromatica", "chromatic", "lente", "lens"]),
        Variant("division-rgb", "División RGB", "RGB split", photo="lighthouse", thumb=0.3,
                defines={"SPLIT": 0.055, "BASE": 0.3, "SHAKE": 0.006, "ZOOM": 1.06}, tags=["division", "dividir"]),
        Variant("agitar-rgb", "Agitar RGB", "RGB shake", photo="skater", thumb=0.3,
                defines={"SPLIT": 0.025, "SHAKE": 0.03, "ZOOM": 1.1, "ROT": 0.04, "BASE": 0.1},
                tags=["agitar", "shake", "temblor"]),
        Variant("vibracion-de-borde-rgb", "Vibración de borde RGB", "RGB edge vibration", photo="figure", thumb=0.3,
                defines={"EDGEONLY": 1.0, "SPLIT": 0.014, "BASE": 0.35, "EDGEGAIN": 0.7, "SHAKE": 0.008, "ZOOM": 1.05},
                tags=["borde", "edge", "contorno", "outline", "vibracion"]),
        Variant("temblor-de-contorno", "Temblor de contorno", "Outline tremble", photo="woman", thumb=1.6,
                defines={"EDGEONLY": 1.0, "SPLIT": 0.008, "BASE": 0.4, "DIR": (0.7, 0.7), "SHAKE": 0.012,
                         "ZOOM": 1.06, "EDGEA": "#ffffff", "EDGEB": "#ffd0f0", "EDGEGAIN": 0.3, "BPERIOD": 0.5, "BURST": 0.6},
                tags=["contorno", "outline", "temblor", "tremble"]),
        Variant("nerviosismo-del-alma", "Nerviosismo del alma", "Soul jitter", photo="woman", thumb=0.25,
                defines={"SOUL": 0.35, "SPLIT": 0.012, "SHAKE": 0.01, "ZOOM": 1.06, "BASE": 0.2},
                tags=["alma", "soul", "fantasma", "ghost", "nervios"]),
        Variant("nerviosismo-cinematografico", "Nerviosismo cinematográfico", "Cinematic jitter", photo="man",
                thumb=0.2, params={"intensity": 1.3}, defines={"SPLIT": 0.018, "SHAKE": 0.012, "ZOOM": 1.08, "ROT": 0.02, "BASE": 0.2,
                                    "BPERIOD": 0.5, "BURST": 0.5},
                tags=["cine", "cinematic", "nervios", "jitter"]),
        Variant("choque-de-corte", "Choque de corte", "Cut impact", photo="woman", thumb=1.6,
                defines={"PUNCH": 0.18, "ZOOM": 1.04, "SPLIT": 0.03, "SHAKE": 0.02, "BASE": 0.0, "BPERIOD": 0.5,
                         "BURST": 0.3, "BLUR": 0.02, "DIR": (0.0, 1.0)},
                tags=["choque", "impact", "corte", "cut", "zoom"]),
        Variant("colision", "Colisión", "Collision", photo="skater", thumb=0.15,
                defines={"FLASH": 0.45, "BLUR": 0.07, "SPLIT": 0.025, "SHAKE": 0.02, "ZOOM": 1.08, "PUNCH": 0.08,
                         "BASE": 0.0, "BURST": 0.4},
                tags=["colision", "collision", "destello", "flash", "choque"]),
        Variant("estiramiento-vibracion", "Estiramiento vibración", "Stretch vibration", photo="skater", thumb=1.55,
                defines={"STRETCH": (0.0, 0.4), "SPLIT": 0.012, "SHAKE": 0.012, "ZOOM": 1.05, "BASE": 0.1,
                         "BPERIOD": 0.5, "BURST": 0.55},
                tags=["estirar", "stretch", "vibracion", "vibration"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Digital breakage: slices that slide, blocks that jump, macroblocks, colour blocks, pixel drag, a scan band.
BLOCKS = Family(
    key="gl_blocks", category="glitch", params=[INTENSITY, SPEED], photo="fashion",
    tags=["glitch", "falla", "digital", "bloques", "blocks", "error"],
    defines={"BPERIOD": 1.0, "BURST": 0.45, "FPS": 12.0, "ROWS": 22.0, "SLICES": 1.0, "SLIDE": 0.2,
             "BLOCKS": 0.0, "BLOCKSIZE": (10.0, 8.0), "PIXEL": 0.0, "RGBAMT": 0.012, "WAVE": 0.0, "POSTER": 0.0,
             "COLORBLOCKS": 0.0, "ROWCOL": 0.0, "COLA": "#18ff6a", "COLB": "#ff2bd6", "INVERT": 0.0, "SMEAR": 0.0,
             "SCAN": 0.0, "TINT": "#ffffff", "SCANL": 0.15},
    body=body(r"""
void main() {
    float t = u_time * speed;
    float e = burstEnv(t) * intensity;
    float tt = floor(t * FPS);
    vec2 uv = v_texCoord;
    float scanBand = 0.0;
    if (SCAN > 0.0) {
        // A band that sweeps down the picture and breaks what it crosses.
        float y0 = fract(t * SCAN) * 1.5 - 0.25;
        scanBand = smoothstep(0.14, 0.0, abs(uv.y - y0));
        e = max(e * 0.35, scanBand * intensity);
    }
    // Slices of random height that slide sideways.
    float row = floor(uv.y * ROWS + hash11(tt) * 4.0);
    float hr = hash12(vec2(row, tt));
    float sliceOn = step(1.0 - SLICES * sat(e) * 0.45, hr);
    uv.x += (hash12(vec2(row, tt + 9.0)) - 0.5) * SLIDE * sliceOn * e;
    uv.x += sin(uv.y * 26.0 + t * 11.0) * WAVE * e + sin(uv.y * 7.0 - t * 5.0) * WAVE * 0.6 * e;
    // Blocks that jump (the grid changes size between hits).
    vec2 grid = BLOCKSIZE / max(size, 0.05) * vec2(aspect() / 1.7778, 1.0) * (1.0 + floor(hash11(tt * 1.9) * 2.0));
    vec2 cell = floor(v_texCoord * grid);
    float blockOn = BLOCKS > 0.0 ? step(1.0 - BLOCKS * sat(e) * 0.3, hash12(cell + tt * 7.31)) : 0.0;
    uv += (hash22(cell + tt * 3.7) - 0.5) * vec2(0.22, 0.08) * blockOn * e;
    if (PIXEL > 0.0) {
        vec2 g = grid * PIXEL;
        uv = mix(uv, (floor(uv * g) + 0.5) / g, max(blockOn, sliceOn * ROWCOL));
    }
    if (SMEAR > 0.0) {
        // Pixel drag: a row keeps repeating the pixel where it froze.
        float sr = floor(v_texCoord.y * 70.0 + hash11(floor(t * 3.0)) * 5.0);
        float x0 = 0.15 + 0.7 * hash12(vec2(sr, floor(t * FPS * 0.5)));
        float on = step(1.0 - SMEAR * sat(e) * 0.5, hash12(vec2(sr * 1.3, floor(t * 4.0))));
        uv.x = mix(uv.x, min(uv.x, x0), on);
    }
    vec2 o = vec2(RGBAMT * (0.25 + 1.5 * e), 0.0);
    vec4 c = Sm(uv);
    vec3 col = vec3(Sm(uv + o).r, c.g, Sm(uv - o).b);
    if (POSTER > 0.0) {
        vec3 pc = floor(col * 3.99) / 3.0;
        pc = saturateColor(hueShift(pc, floor(t * 6.0) * 0.137), 1.7);
        col = mix(col, pc, POSTER * sat(0.35 + e));
    }
    float mask = max(blockOn, sliceOn * ROWCOL) * sat(e * 1.5);
    float pick = hash12(cell + floor(uv.y * ROWS) + tt * 1.3);
    if (COLORBLOCKS > 0.0) {
        vec3 bc = mix(COLA, COLB, step(0.5, hash12(cell + 1.7 + tt))) * (0.35 + 0.9 * luma(c.rgb));
        col = mix(col, bc, COLORBLOCKS * step(0.35, pick) * mask);
    }
    if (INVERT > 0.0) col = mix(col, 1.0 - col, INVERT * step(0.55, pick) * max(mask, sliceOn * sat(e)));
    col = mix(col, col * TINT * 1.25, sliceOn * sat(e));
    col *= 1.0 - SCANL * sat(e + scanBand) * (0.5 + 0.5 * sin(v_texCoord.y * u_resolution.y * 1.6));
    fragColor = vec4(sat3(col), S(v_texCoord).a);
}
"""),
    variants=[
        Variant("glitch-fuerte", "Glitch fuerte", "Heavy glitch", photo="cyber", thumb=0.3,
                defines={"SLIDE": 0.3, "BLOCKS": 1.0, "RGBAMT": 0.02, "INVERT": 0.4, "BURST": 0.55},
                tags=["fuerte", "heavy", "intenso"]),
        Variant("efecto-de-falla-20", "Efecto de falla 20", "Glitch effect 20", photo="woman", thumb=1.4,
                defines={"SLIDE": 0.18, "ROWS": 34.0, "RGBAMT": 0.016}),
        Variant("efecto-de-falla-7", "Efecto de falla 7", "Glitch effect 7", photo="citynight", thumb=0.3,
                defines={"WAVE": 0.035, "POSTER": 1.0, "SLIDE": 0.12, "RGBAMT": 0.01, "BURST": 0.6},
                tags=["onda", "wave", "psicodelico"]),
        Variant("glitch-de-mpeg", "Glitch de MPEG", "MPEG glitch", photo="citynight", thumb=0.3,
                defines={"BLOCKS": 1.2, "PIXEL": 0.25, "COLORBLOCKS": 1.0, "ROWCOL": 1.0, "COLA": "#1cff5a",
                         "COLB": "#0b3d1a", "SLIDE": 0.1, "BLOCKSIZE": (16.0, 12.0)},
                tags=["mpeg", "compresion", "compression", "macrobloques", "datamosh"]),
        Variant("bloque-de-falla-2", "Bloque de falla 2", "Glitch block 2", photo="fashion", thumb=0.3,
                defines={"BLOCKS": 1.6, "SLICES": 0.4, "BLOCKSIZE": (6.0, 5.0), "RGBAMT": 0.018},
                tags=["bloque", "block"]),
        Variant("efecto-de-falla-17", "Efecto de falla 17", "Glitch effect 17", photo="dancer", thumb=0.3,
                defines={"INVERT": 1.0, "BLOCKS": 0.6, "SLIDE": 0.15, "ROWCOL": 0.5}, tags=["invertir", "invert"]),
        Variant("error-cibernetico-01", "Error cibernético 01", "Cyber error 01", photo="skater", thumb=0.3,
                defines={"COLORBLOCKS": 0.8, "ROWCOL": 1.0, "COLA": "#2040ff", "COLB": "#ff30c8", "BLOCKS": 0.8,
                         "TINT": "#7fb0ff", "SLIDE": 0.22, "RGBAMT": 0.02},
                tags=["cibernetico", "cyber", "neon"]),
        Variant("fallo-vintage-01", "Fallo vintage 01", "Vintage glitch 01", photo="fashion", thumb=0.3,
                defines={"SMEAR": 0.8, "BLOCKS": 0.6, "SLIDE": 0.12, "RGBAMT": 0.02, "SCANL": 0.3},
                tags=["vintage", "retro"]),
        Variant("fallo-psicodelico", "Fallo psicodélico", "Psychedelic glitch", photo="fashion", thumb=0.3,
                defines={"POSTER": 1.0, "RGBAMT": 0.03, "SLIDE": 0.1, "BURST": 0.6},
                tags=["psicodelico", "psychedelic", "colores", "colors"]),
        Variant("congelacion-de-fallas", "Congelación de fallas", "Glitch freeze", photo="fashion", thumb=0.3,
                defines={"SMEAR": 1.5, "SLICES": 0.6, "RGBAMT": 0.014, "FPS": 8.0, "BURST": 0.6},
                tags=["congelar", "freeze", "arrastre", "drag"]),
        Variant("escaneo-de-fallas", "Escaneo de fallas", "Glitch scan", photo="cyber", thumb=1.0,
                defines={"SCAN": 0.45, "ROWS": 60.0, "SLIDE": 0.12, "WAVE": 0.02, "RGBAMT": 0.02, "SLICES": 1.6},
                tags=["escaneo", "scan", "barrido"]),
        Variant("fallo-con-filtro", "Fallo con filtro", "Filtered glitch", photo="man", thumb=0.3,
                defines={"TINT": "#40e0ff", "SLIDE": 0.14, "ROWS": 14.0, "RGBAMT": 0.014, "BLOCKS": 0.5},
                tags=["filtro", "filter", "color"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Analogue tape: wobbling lines, a tracking band that rolls down, colour bleeding sideways, snow and streaks.
VCR = Family(
    key="gl_vcr", category="glitch", params=[INTENSITY, SPEED], photo="woman",
    tags=["vcr", "vhs", "cinta", "tape", "analogico", "analog", "glitch"],
    defines={"BPERIOD": 1.0, "BURST": 0.4, "BASE": 0.4, "WOBBLE": 0.006, "BLEED": 0.012, "NOISE": 0.5,
             "STRIPES": 0.0, "TEAR": 0.03, "SATV": 0.85},
    body=body(r"""
void main() {
    float t = u_time * speed;
    float e = burstEnv(t) * intensity;
    float base = BASE * intensity;
    vec2 uv = v_texCoord;
    // Tracking band rolling down, and a tear (vertical jump) during a hit.
    float y0 = fract(t * 0.27) * 1.3 - 0.15;
    float tb = exp(-pow((uv.y - y0) / 0.045, 2.0));
    uv.y += TEAR * e * jit(t, 9.0, 4.0);
    float lineN = vnoise(vec2(uv.y * 180.0, t * 40.0)) - 0.5;
    uv.x += lineN * 0.006 * (base + 1.5 * e);
    uv.x += tb * (0.012 + 0.04 * e) * (vnoise(vec2(uv.y * 70.0, t * 25.0)) - 0.35) * intensity;
    uv.x += sin(uv.y * 9.0 + t * 4.0) * WOBBLE * (base * 0.4 + e);
    vec4 c = Sm(uv);
    // Colour smeared sideways over a sharp luma.
    vec3 ch = dirBlur(uv + vec2(BLEED * 0.5 * (1.0 + e), 0.0), vec2(BLEED * (1.0 + 2.0 * e), 0.0)).rgb;
    vec3 col = vec3(luma(c.rgb)) + (ch - vec3(luma(ch)));
    col = mix(c.rgb, col, sat(intensity));
    vec2 o = vec2(0.004 + 0.012 * e, 0.0);
    col.r = mix(col.r, Sm(uv + o).r, 0.5);
    col.b = mix(col.b, Sm(uv - o).b, 0.5);
    // Snow and white streaks, mostly in the band and the hits.
    vec2 cell = floor(v_texCoord * u_resolution / 2.0);
    float n = hash12(cell + floor(t * 24.0) * 13.1);
    col = mix(col, vec3(n), NOISE * (tb * 0.45 + e * 0.2 + 0.04) * intensity);
    float ln = floor(v_texCoord.y * u_resolution.y / 2.0);
    float streak = step(0.975 - 0.03 * e, hash12(vec2(ln, floor(t * 24.0)))) *
                   smoothstep(0.3, 0.9, hash12(vec2(floor(v_texCoord.x * 18.0 + ln), floor(t * 24.0))));
    col = addLight(col, vec3(1.0), streak * 0.7 * sat(tb + e) * intensity);
    if (STRIPES > 0.0) {
        float s = sin((v_texCoord.x * aspect() + v_texCoord.y * 1.3) * 120.0 - t * 30.0);
        col = mix(col, col * (0.7 + 0.3 * s) + 0.06 * s, STRIPES * (0.35 + 0.65 * e));
    }
    col = saturateColor(col, mix(1.0, SATV, sat(intensity)));
    col *= 0.93 + 0.07 * sin(v_texCoord.y * u_resolution.y * 1.57);
    col *= mix(1.0, vignette(v_texCoord, 0.45, 0.6), 0.35 * sat(intensity));
    fragColor = vec4(sat3(col), c.a);
}
"""),
    variants=[
        Variant("distorsion-vcr", "Distorsión VCR", "VCR distortion", photo="woman", thumb=0.3,
                tags=["distorsion", "distortion"]),
        Variant("cinta-de-video", "Cinta de video", "Video tape", photo="fashion", thumb=0.3,
                defines={"STRIPES": 0.6, "WOBBLE": 0.01, "BASE": 0.5}, tags=["video", "rayas", "stripes"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Flickers: strobe, invert, brightness jitter, difference ghosts, colour tints and haunt copies.
FLICKER = Family(
    key="gl_flicker", category="glitch", params=[INTENSITY, SPEED], photo="woman",
    tags=["parpadeo", "flicker", "glitch", "destello"],
    defines={"MODE": 1.0, "BPERIOD": 1.0, "BURST": 0.5, "TINTA": "#ff3c9a", "TINTB": "#26e0ff"},
    body=body(r"""
bool mode(float m) { return abs(MODE - m) < 0.5; }
void main() {
    float t = u_time * speed;
    float e = burstEnv(t) * intensity;
    vec2 j = vec2(jit(t, 14.0, 1.0), jit(t, 14.0, 2.0));
    vec2 uv = v_texCoord;
    vec4 c = Sm(uv);
    vec3 col = c.rgb;
    if (mode(1.0)) {
        // Strobe locked to the beat: a hard flash, the frame snaps closer, a dark frame after.
        float ph = phase(t, 0.5);
        float b = floor(t / 0.5);
        float snap = step(0.5, hash11(b * 2.3)) * 0.12;
        uv = camUv(v_texCoord, vec2(0.5), 1.0 + snap * intensity, 0.0, vec2(0.0));
        float fl = pow(1.0 - smoothstep(0.0, 0.26, ph), 2.0);
        vec2 o = vec2(0.012 * fl * intensity, 0.0);
        col = vec3(Sm(uv + o).r, Sm(uv).g, Sm(uv - o).b);
        // The flash fades over ~130 ms; a dark frame follows.
        col = mix(col, vec3(1.0), fl * 0.85 * sat(intensity));
        col *= 1.0 - step(0.28, ph) * step(ph, 0.36) * 0.75 * sat(intensity);
    } else if (mode(2.0)) {
        // Inverted frames in the hits, with the channels apart.
        float inv = step(0.45, hash11(floor(t * 12.0) * 3.1)) * step(0.01, e);
        vec2 o = vec2(0.02 * e, 0.0) * amount;
        uv = camUv(v_texCoord, vec2(0.5), 1.04, 0.0, j * 0.008 * e);
        col = vec3(Sm(uv + o).r, Sm(uv).g, Sm(uv - o).b);
        col = mix(col, 1.0 - col, inv * sat(intensity));
    } else if (mode(3.0)) {
        // Brightness jitter: exposure jumps frame to frame and the picture twitches.
        uv = camUv(v_texCoord, vec2(0.5), 1.05, j.y * 0.015 * e * amount, j * 0.012 * e * amount);
        vec2 o = vec2(0.01 * e, 0.0) * amount;
        col = vec3(Sm(uv + o).r, Sm(uv).g, Sm(uv - o).b);
        float ex = jit(t, 18.0, 7.0);
        col = ex > 0.0 ? addLight(col, col, ex * 0.9 * e) : col * (1.0 + ex * 0.6 * e);
    } else if (mode(4.0)) {
        // Difference ghost: a shifted copy subtracted from the frame (negative double image).
        // Double image with the channels apart; some frames turn magenta/green (two channels inverted).
        vec2 o = vec2(0.03 + 0.02 * j.x, 0.01 * j.y) * e * amount;
        vec3 d = vec3(Sm(uv + o).r, col.g, Sm(uv - o * 1.5).b);
        float inv = step(0.5, hash11(floor(t * 12.0) * 2.9)) * step(0.01, e);
        col = mix(d, vec3(1.0 - d.r, d.g, 1.0 - d.b), inv * 0.85 * sat(intensity));
    } else if (mode(5.0)) {
        // Colour flicker: the frame takes a colour wash frame by frame in the hits.
        float k = hash11(floor(t * 10.0) * 1.7);
        vec3 tint = k < 0.33 ? TINTA : (k < 0.66 ? TINTB : vec3(1.0, 0.85, 0.2));
        vec3 washed = mix(col, screen(col * tint, tint * 0.35), sat(0.7 * amount));
        col = mix(col, washed, sat(e * 1.2));
        col = addLight(col, tint, 0.12 * e);
    } else {
        // Haunt: two tinted copies drift off in the hits, the frame flickers a little darker.
        vec2 o = vec2(0.06 + 0.04 * j.x, 0.01 * j.y) * e * amount;
        vec3 g1 = Sm(uv + o).rgb, g2 = Sm(uv - o * 1.4).rgb;
        col *= 1.0 - 0.25 * e * step(0.0, j.y);
        col = mix(col, screen(col * 0.8, g1 * TINTB), 0.6 * sat(e * 1.5));
        col = mix(col, screen(col, g2 * TINTA * 0.8), 0.45 * sat(e * 1.5));
    }
    fragColor = vec4(sat3(col), c.a);
}
"""),
    variants=[
        Variant("estroboscopio-bloqueado", "Estroboscopio bloqueado", "Locked strobe", photo="woman", thumb=0.55,
                defines={"MODE": 1.0}, tags=["estroboscopio", "strobe", "flash", "ritmo", "beat"]),
        Variant("invertir-alterado", "Invertir alterado", "Glitched invert", photo="man", thumb=0.3,
                defines={"MODE": 2.0}, tags=["invertir", "invert", "negativo", "negative"]),
        Variant("jitter-de-parpadeo-01", "Jitter de parpadeo 01", "Flicker jitter 01", photo="dancer", thumb=0.3,
                defines={"MODE": 3.0, "BPERIOD": 0.5, "BURST": 0.6}, tags=["jitter", "brillo", "brightness"]),
        Variant("falla-de-parpadeo", "Falla de parpadeo", "Flicker glitch", photo="skater", thumb=2.4,
                defines={"MODE": 4.0}, tags=["falla", "doble", "double", "negativo"]),
        Variant("parpadeo-de-color", "Parpadeo de color", "Colour flicker", photo="woman", thumb=2.2,
                defines={"MODE": 5.0, "BURST": 0.6}, tags=["color", "colour", "tinte", "tint"]),
        Variant("fantasma-glitch", "Fantasma glitch", "Glitch haunt", photo="woman", thumb=1.5,
                defines={"MODE": 6.0, "BURST": 0.6}, tags=["fantasma", "ghost", "haunt", "terror"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Time: low frame rate, afterimage trails of a moving camera.
TIME = Family(
    key="gl_time", category="glitch", params=[INTENSITY, SPEED], photo="skater",
    tags=["glitch", "fps", "eco", "echo", "tiempo", "time"],
    defines={"MODE": 1.0, "FPSL": 8.0, "BPERIOD": 1.0, "BURST": 0.5},
    body=body(r"""
// The camera path both modes follow: a lively handheld drift.
vec2 camPath(float t) { return shake2(t, 1.6) * vec2(0.05, 0.03) * distance; }
float camTurn(float t) { return shake2(t + 4.0, 1.2).x * 0.03 * distance; }
void main() {
    float t = u_time * speed;
    vec4 src = S(v_texCoord);
    vec3 col;
    if (MODE < 1.5) {
        // Low frame rate: the moving picture only updates FPSL times a second, with a dropped frame now and then.
        float ts = stepTime(t, FPSL);
        float drop = step(0.8, hash11(floor(t * FPSL) * 2.7)) * 0.3;
        float k = sat(intensity);
        col = cam(v_texCoord, vec2(0.5), 1.1, camTurn(ts) * k, camPath(ts - drop / FPSL) * k * 1.4).rgb;
    } else {
        // Afterimage: the trail of where the picture just was, fading.
        float k = sat(intensity);
        col = cam(v_texCoord, vec2(0.5), 1.1, camTurn(t) * k * 1.5, camPath(t) * k * 1.8).rgb;
        vec3 acc = col;
        for (int i = 1; i <= 5; ++i) {
            float fi = float(i);
            float tp = t - fi * 0.8 / FPSL;
            vec3 g = cam(v_texCoord, vec2(0.5), 1.1, camTurn(tp) * k * 1.5, camPath(tp) * k * 1.8).rgb;
            float w = (1.0 - fi / 6.0) * 0.75 * sat(intensity);
            acc = mix(acc, max(acc, g * vec3(0.9, 0.95, 1.05)), w);
        }
        col = mix(col, acc, 0.85);
    }
    fragColor = vec4(sat3(col), src.a);
}
"""),
    variants=[
        Variant("estilo-de-fps-bajo", "Estilo de FPS bajo", "Low FPS style", photo="skater", thumb=1.25,
                defines={"MODE": 1.0}, tags=["fps", "entrecortado", "choppy", "stutter"]),
        Variant("imagen-remanente", "Imagen remanente", "Afterimage", photo="dancer", thumb=0.65,
                params={"distance": 1.6}, defines={"MODE": 2.0}, tags=["remanente", "afterimage", "estela", "trail", "eco"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# On the beat (120 BPM, where Filmora follows the audio): colour jumps, blur pulses, exposure hits.
BEAT = Family(
    key="gl_beat", category="glitch", params=[INTENSITY, SPEED], photo="fashion",
    tags=["ritmo", "beat", "musica", "music", "audio", "120 bpm"],
    defines={"MODE": 1.0, "DECAY": 0.12, "BPERIOD": 1.0, "BURST": 0.5},
    body=body(r"""
void main() {
    float t = u_time * speed;
    float b = floor(t / 0.5);
    float hit = beat(t, 0.5, DECAY) * intensity;
    vec2 ctr = vec2(center_x, center_y);
    vec4 c = S(v_texCoord);
    vec3 col = c.rgb;
    if (MODE < 1.5) {
        // Colour change: the hue jumps on every beat, the copies jump apart on the hit.
        float h = floor(hash11(b * 1.31) * 6.0) / 6.0 + 0.08;
        vec2 o = vec2(0.035, 0.0) * hit * amount;
        vec2 uv = camUv(v_texCoord, ctr, 1.0 + 0.05 * hit, 0.0, vec2(0.0));
        vec3 base = vec3(Sm(uv + o).r, Sm(uv).g, Sm(uv - o).b);
        vec3 shifted = saturateColor(hueShift(base, h), 1.25);
        col = mix(base, shifted, sat(intensity));
        col = screen(col, Sm(uv + o * 2.0).rgb * vec3(1.0, 0.2, 0.3) * 0.4 * sat(hit));
    } else if (MODE < 2.5) {
        // Blur pulse: a zoom blur and a small push on every beat.
        vec2 uv = camUv(v_texCoord, ctr, 1.0 + 0.06 * hit * amount, 0.0, vec2(0.0));
        col = mix(Sm(uv).rgb, zoomBlur(uv, ctr, 0.12 * hit * amount).rgb, sat(hit * 2.0));
    } else {
        // Exposure: the frame blows out on every beat and settles.
        col = addLight(col, col * 1.2 + 0.2, 1.1 * hit * amount);
        col = mix(col, contrastColor(col, 1.0 + 0.2 * hit), 0.5);
    }
    fragColor = vec4(sat3(col), c.a);
}
"""),
    variants=[
        Variant("cambio-de-color-al-ritmo", "Cambio de color al ritmo", "Colour change on the beat",
                photo="fashion", thumb=1.0, defines={"MODE": 1.0, "DECAY": 0.15}, tags=["color", "colour", "tono", "hue"]),
        Variant("pulso-al-ritmo", "Pulso al ritmo", "Pulse on the beat", photo="woman", thumb=1.0,
                defines={"MODE": 2.0, "DECAY": 0.14}, tags=["pulso", "pulse", "desenfoque", "blur"]),
        Variant("exposicion-al-ritmo", "Exposición al ritmo", "Exposure on the beat", photo="dancer", thumb=1.0,
                defines={"MODE": 3.0, "DECAY": 0.12}, tags=["exposicion", "exposure", "destello", "flash"]),
    ],
)


# ---------------------------------------------------------------------------------------------------------------
# Everything one would want to tune is a parameter of the effect panel. The designs above set #defines; promote()
# turns a define into a uniform (an alias #define keeps the body as it is) and moves every variant's value into its
# parameter defaults, so each card keeps exactly its look.
def promote(family, name, param, to_param=lambda v: v, alias=None):
    family.params.append(param)
    param.default = to_param(family.defines.pop(name)) if name in family.defines else param.default
    for v in family.variants:
        if name in v.defines:
            v.params[param.id] = to_param(v.defines.pop(name))
    family.body = f"#define {name} ({alias or param.id})\n" + family.body


def add(family, param):
    family.params.append(param)


def per_second(v):
    return round(1.0 / v, 4)


FREQ = dict(to_param=per_second, alias="1.0 / max(frequency, 0.01)")

promote(SPLIT, "SPLIT", Param("amount", "Amount", 0.0, 0.12, 0.012))
promote(SPLIT, "BPERIOD", Param("frequency", "Frequency", 0.25, 4.0, 1.0), **FREQ)
promote(SPLIT, "SHAKE", Param("strength", "Strength", 0.0, 0.08, 0.0))
promote(SPLIT, "PUNCH", Param("zoom", "Zoom", 0.0, 0.4, 0.0))
promote(SPLIT, "EDGEA", Param("color_a", "Colour A", default="#ff2a6a"))
promote(SPLIT, "EDGEB", Param("color_b", "Colour B", default="#20e8ff"))
promote(SPLIT, "FLASH", Param("brightness", "Brightness", 0.0, 1.5, 0.0))
promote(SPLIT, "BLUR", Param("blur", "Blur", 0.0, 0.15, 0.0))
add(SPLIT, Param("center_x", "Center X", 0.0, 1.0, 0.5))
add(SPLIT, Param("center_y", "Center Y", 0.0, 1.0, 0.5))

promote(BLOCKS, "RGBAMT", Param("amount", "Amount", 0.0, 0.08, 0.012))
promote(BLOCKS, "BPERIOD", Param("frequency", "Frequency", 0.25, 4.0, 1.0), **FREQ)
promote(BLOCKS, "SLICES", Param("density", "Density", 0.0, 2.0, 1.0))
promote(BLOCKS, "SLIDE", Param("distance", "Distance", 0.0, 0.5, 0.2))
add(BLOCKS, Param("size", "Size", 0.4, 2.5, 1.0))
promote(BLOCKS, "COLA", Param("color_a", "Colour A", default="#18ff6a"))
promote(BLOCKS, "COLB", Param("color_b", "Colour B", default="#ff2bd6"))
promote(BLOCKS, "TINT", Param("color", "Colour", default="#ffffff"))
promote(BLOCKS, "FPS", Param("flicker", "Flicker", 2.0, 30.0, 12.0))

promote(VCR, "BLEED", Param("amount", "Amount", 0.0, 0.05, 0.012))
promote(VCR, "BPERIOD", Param("frequency", "Frequency", 0.25, 4.0, 1.0), **FREQ)
promote(VCR, "NOISE", Param("grain", "Grain", 0.0, 1.5, 0.5))
promote(VCR, "SATV", Param("saturation", "Saturation", 0.0, 1.5, 0.85))
promote(VCR, "STRIPES", Param("detail", "Detail", 0.0, 1.0, 0.0))

promote(FLICKER, "BPERIOD", Param("frequency", "Frequency", 0.25, 4.0, 1.0), **FREQ)
add(FLICKER, Param("amount", "Amount", 0.0, 3.0, 1.0))
promote(FLICKER, "TINTA", Param("color_a", "Colour A", default="#ff3c9a"))
promote(FLICKER, "TINTB", Param("color_b", "Colour B", default="#26e0ff"))

promote(TIME, "FPSL", Param("frequency", "Frequency", 2.0, 24.0, 8.0))
add(TIME, Param("distance", "Distance", 0.0, 3.0, 1.0))

promote(BEAT, "DECAY", Param("softness", "Softness", 0.03, 0.45, 0.12))
add(BEAT, Param("amount", "Amount", 0.0, 2.5, 1.0))
add(BEAT, Param("center_x", "Center X", 0.0, 1.0, 0.5))
add(BEAT, Param("center_y", "Center Y", 0.0, 1.0, 0.5))

FAMILIES = [SPLIT, BLOCKS, VCR, FLICKER, TIME, BEAT]
