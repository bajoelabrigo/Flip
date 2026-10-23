"""Efectos › Tendencias, «Retro y película»: old film (dust, hairs, scratches, gate weave, flicker, tones), VHS and
CRT (chroma bleed, tracking, static, curved screens, horror monitors, a camcorder viewfinder with its own pixel
font), film burn, film strips and slides, and cinema bars. Our own shaders."""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)
GRAIN = Param("grain", "Grain", 0.0, 2.0, 1.0)

TAGS = ["retro", "vintage", "pelicula", "film"]

# ---------------------------------------------------------------------------------------------------------------
# Old film: one body, the look comes from the defines.
#   TONE: 0 colour as is, 1 black and white, 2 sepia, 3 faded 70s, 4 faded colour film.
# ---------------------------------------------------------------------------------------------------------------
FILM_LIB = r"""
float grainN(vec2 uv, float f) {
    vec2 g = floor(uv * u_resolution / 1.5);
    return hash12(g + vec2(f * 17.13, f * 7.31)) + hash12(g * 1.37 + vec2(f * 3.1, 11.0)) - 1.0;
}
vec3 filmTone(vec3 c, float mode) {
    float l = luma(c);
    if (mode < 0.5) return c;
    if (mode < 1.5) return vec3(sat(contrastColor(vec3(l), 1.18).x));
    if (mode < 2.5) {
        vec3 s = vec3(l) * vec3(1.10, 0.93, 0.70) + vec3(0.04, 0.02, 0.0);
        return sat3(contrastColor(s, 1.06));
    }
    if (mode < 3.5) {
        vec3 d = saturateColor(c, 0.62);
        d = d * vec3(1.08, 0.98, 0.80) + vec3(0.03, 0.03, 0.0);
        return sat3(mix(vec3(0.09, 0.08, 0.05), vec3(0.98, 0.92, 0.80), d));
    }
    vec3 d = saturateColor(c, 0.78);
    d = mix(d * vec3(0.93, 1.0, 1.04), d * vec3(1.07, 1.0, 0.88), smoothstep(0.2, 0.8, l));
    return sat3(mix(vec3(0.06, 0.06, 0.07), vec3(0.97, 0.95, 0.89), d));
}
// Dust for frame f: (light specks, dark specks), irregular soft blobs scattered at random inside their cells.
vec2 specks(vec2 p, float f, float scale, float prob, float seed) {
    p *= scale;
    vec2 cell = floor(p), q = fract(p) - 0.5;
    float h = hash12(cell + vec2(f * 13.17, seed));
    if (h > prob) return vec2(0.0);
    vec3 r = hash32(cell + vec2(seed, f * 7.7));
    vec2 d = q - (r.xy - 0.5) * 0.7;
    float sz = 0.035 + 0.14 * r.z * r.z;
    float n = vnoise(d / sz * 1.8 + r.xy * 40.0);
    float m = smoothstep(1.0, 0.5, length(d * vec2(1.0, 0.6 + r.y)) / sz + (n - 0.5) * 0.9);
    return hash11(r.z * 91.0 + seed) < 0.6 ? vec2(m, 0.0) : vec2(0.0, m);
}
// Hairs: thin curly lines, a few per frame.
float hairs(vec2 p, float f, float scale, float prob, float seed) {
    p *= scale;
    vec2 cell = floor(p), q = fract(p) - 0.5;
    if (hash12(cell + vec2(f * 5.31, seed + 2.0)) > prob) return 0.0;
    vec3 r = hash32(cell + vec2(f * 3.3, seed + 8.0));
    q = rot(r.x * TAU) * (q - (r.yz - 0.5) * 0.3);
    float len = 0.22 + 0.22 * r.z;
    float y = (r.y - 0.5) * 3.0 * q.x * q.x + 0.06 * sin(q.x * 14.0 + r.x * 6.0);
    float w = max(0.0016, 1.0 / u_resolution.y) * scale;
    return smoothstep(w * 1.5, w * 0.2, abs(q.y - y)) * smoothstep(len, len * 0.6, abs(q.x));
}
// Vertical scratches that live a while and wander: (light, dark).
vec2 scratches(vec2 uv, float t, float f, float count, float seed) {
    vec2 s = vec2(0.0);
    for (int i = 0; i < 4; ++i) {
        float fi = float(i);
        float life = floor(t * (0.7 + 0.35 * fi) + fi * 0.37);
        float x = 0.06 + 0.88 * hash11(life * 3.7 + fi * 11.0 + seed);
        x += 0.012 * sin(t * (1.3 + fi) + fi) + (hash11(f * 1.9 + fi) - 0.5) * 0.0025;
        float on = step(fi + 0.5, count) * step(0.2, hash11(life * 5.1 + fi + seed));
        float w = max(0.0008, 1.0 / u_resolution.x) * (0.7 + 1.1 * hash11(life + fi * 2.0));
        float dx = (uv.x - x) / w;
        float along = smoothstep(0.2, 0.65, vnoise(vec2(uv.y * 4.0 + fi * 7.0, life * 3.0 + t * 0.5)));
        float k = on * along * exp(-dx * dx) * (0.65 + 0.35 * hash11(f + fi * 3.0));
        if (hash11(life * 9.3 + fi) < 0.65) s.x += k; else s.y += k;
    }
    return clamp(s, 0.0, 1.0);
}
float filmVig(vec2 uv, float amt) {
    vec2 q = abs(uv - 0.5) * 2.0;
    float d = pow(pow(q.x, 4.0) + pow(q.y, 4.0), 0.25) * 0.55 + length(q) * 0.45;
    return 1.0 - amt * smoothstep(0.42, 1.3, d);
}
"""

OLD_FILM = Family(
    key="retro_oldfilm", category="retro",
    params=[INTENSITY, SPEED, GRAIN, Param("amount", "Amount", 0.0, 3.0, 1.0), Param("flicker", "Flicker", 0.0, 3.0, 1.0),
            Param("saturation", "Saturation", 0.0, 1.5, 1.0), Param("contrast", "Contrast", 0.5, 1.6, 1.0)], photo="walk",
    tags=TAGS + ["polvo", "dust", "rayas", "scratches", "antiguo", "old"],
    defines={"TONE": 0, "FPS": 18.0, "WEAVE": 0.5, "JUMP": 0.0, "FLICK": 0.5, "GRAINK": 1.0, "DUST": 0.5,
             "HAIR": 0.3, "SCRATCH": 1.0, "MUD": 0.0, "PROJ": 0.0, "VIG": 0.4, "LEAK": 0.0},
    body=FILM_LIB + r"""
void main() {
    vec4 src = S(v_texCoord);
    float k = intensity;
    float t = u_time * speed;
    float f = floor(t * FPS);
    // Gate weave and, now and then, a frame that jumps.
    vec2 w = (shake2(t, 1.3) * 0.0025 + (hash22(vec2(f, 3.1)) - 0.5) * 0.0016) * WEAVE * k;
    w.y += JUMP * k * step(0.94, hash11(f * 0.71 + 2.0)) * 0.012;
    vec2 uv = camUv(v_texCoord, vec2(0.5), 1.0 + 0.025 * (WEAVE + JUMP), 0.0, w);
    vec3 c = Sm(uv).rgb;
    vec3 toned = filmTone(c, TONE);
    toned = saturateColor(toned, saturation);
    toned = sat3(contrastColor(toned, contrast));
    c = mix(c, toned, sat(k));
    // Warm light leak breathing at one edge (70s).
    if (LEAK > 0.0) {
        vec2 p0 = toP(v_texCoord);
        float lk = exp(-length(p0 - vec2(aspect() * 0.55, -0.35 + 0.15 * sin(t * 0.7))) * 2.6);
        c = addLight(c, vec3(1.0, 0.45, 0.15) * lk * (0.6 + 0.4 * sin(t * 1.3)), LEAK * k);
    }
    c *= 1.0 + ((hash11(f * 1.37 + 0.5) - 0.5) * 0.16 + 0.025 * sin(t * 47.0)) * FLICK * flicker * k;
    c += grainN(v_texCoord, f) * 0.055 * grain * GRAINK * k;
    vec2 p = toP(v_texCoord);
    vec2 sp = specks(p, f, 10.0, 0.05 * DUST * amount, 1.0) + specks(p, f, 4.5, 0.025 * DUST * amount, 7.0);
    float hr = hairs(p, f, 2.6, 0.10 * HAIR * amount, 3.0);
    vec2 sc = scratches(v_texCoord, t, f, SCRATCH * amount, 5.0);
    float mud = 0.0;
    if (MUD > 0.0) { vec2 m = specks(p, floor(t * 2.5), 6.0, 0.10 * MUD * amount, 21.0); mud = sat(m.x + m.y); }
    float dk = sat(k);
    c = mix(c, vec3(0.94, 0.93, 0.88), sat(sp.x * 0.85 + sc.x * 0.6) * dk);
    c = mix(c, vec3(0.04, 0.035, 0.03), sat(sp.y * 0.85 + hr * 0.8 + sc.y * 0.65) * dk);
    c = mix(c, vec3(0.16, 0.11, 0.07), mud * 0.85 * dk);
    // The projector line: one long line that stays and wanders slowly.
    if (PROJ > 0.0) {
        float x = 0.32 + 0.05 * sin(t * 0.45) + 0.003 * (hash11(f) - 0.5);
        float dx = (v_texCoord.x - x) / max(0.0012, 1.2 / u_resolution.x);
        float x2 = 0.71 + 0.03 * sin(t * 0.31 + 2.0);
        float dx2 = (v_texCoord.x - x2) / max(0.0008, 1.0 / u_resolution.x);
        c = mix(c, vec3(0.05), exp(-dx * dx) * 0.75 * PROJ * sat(amount) * dk);
        c = mix(c, vec3(0.9), exp(-dx2 * dx2) * 0.45 * PROJ * sat(amount) * dk * step(0.3, vnoise(vec2(v_texCoord.y * 3.0, t))));
    }
    c *= mix(1.0, filmVig(v_texCoord, VIG), sat(k));
    fragColor = vec4(sat3(c), src.a);
}
""",
    variants=[
        Variant("anos-70", "Años 70", "The 70s", photo="woman", thumb=1.2,
                defines={"TONE": 3, "DUST": 0.5, "HAIR": 0.4, "SCRATCH": 1, "PROJ": 0.8, "FLICK": 0.5,
                         "VIG": 0.45, "LEAK": 0.5, "GRAINK": 1.3},
                tags=["70s", "setentas", "seventies"]),
        Variant("pelicula-vieja", "Película vieja", "Old film", photo="walk", thumb=1.0,
                defines={"TONE": 4, "DUST": 1.0, "HAIR": 1.0, "SCRATCH": 3, "VIG": 0.5, "FLICK": 0.6}),
        Variant("pelicula-muda-2", "Película muda 2", "Silent film 2", photo="walk", thumb=0.8,
                defines={"TONE": 1, "DUST": 0.8, "HAIR": 0.6, "SCRATCH": 2, "VIG": 0.9, "FLICK": 1.0,
                         "WEAVE": 1.0, "GRAINK": 1.3},
                tags=["muda", "silent", "blanco y negro", "black and white"]),
        Variant("pelicula-muda", "Película muda", "Silent film", photo="woman", thumb=1.4,
                defines={"TONE": 1, "DUST": 0.6, "HAIR": 0.4, "SCRATCH": 2, "VIG": 1.35, "FLICK": 1.4,
                         "WEAVE": 1.2, "JUMP": 1.0, "FPS": 16.0, "GRAINK": 1.4},
                tags=["muda", "silent", "blanco y negro", "black and white", "chaplin"]),
        Variant("pelicula-de-grano", "Película de grano", "Grainy film", photo="woman", thumb=1.0,
                defines={"GRAINK": 2.6, "DUST": 0.15, "HAIR": 0.0, "SCRATCH": 0, "VIG": 0.3, "FLICK": 0.3,
                         "WEAVE": 0.2},
                tags=["grano", "grain"]),
        Variant("ruido-retro", "Ruido retro", "Retro noise", photo="lighthouse", thumb=1.0,
                defines={"TONE": 4, "GRAINK": 1.8, "PROJ": 1.0, "DUST": 0.4, "HAIR": 0.2, "SCRATCH": 1,
                         "VIG": 0.35},
                tags=["ruido", "noise"]),
        Variant("ligeras-salpicaduras-de-barro", "Ligeras salpicaduras de barro", "Light mud splashes",
                photo="lighthouse", thumb=1.0,
                defines={"MUD": 1.8, "DUST": 0.2, "HAIR": 0.1, "SCRATCH": 0, "FLICK": 0.2, "VIG": 0.2,
                         "GRAINK": 0.6},
                tags=["barro", "mud", "manchas", "stains"]),
        Variant("pelicula-sucia", "Película sucia", "Dirty film", photo="lighthouse", thumb=1.0,
                defines={"DUST": 1.8, "HAIR": 0.8, "SCRATCH": 1, "VIG": 0.3, "GRAINK": 1.0},
                tags=["sucia", "dirty", "polvo", "dust"]),
        Variant("pelicula-extremadamente-sucia", "Película extremadamente sucia", "Extremely dirty film",
                photo="walk", thumb=1.0,
                defines={"TONE": 4, "DUST": 3.8, "HAIR": 2.2, "SCRATCH": 4, "MUD": 0.5, "VIG": 0.6,
                         "FLICK": 0.8, "WEAVE": 0.8, "GRAINK": 1.5},
                tags=["sucia", "dirty", "polvo", "dust"]),
        Variant("cine-retro", "Cine retro", "Retro cinema", photo="car", thumb=1.0,
                defines={"TONE": 4, "DUST": 0.7, "HAIR": 0.5, "SCRATCH": 2, "VIG": 0.45, "FLICK": 0.5},
                tags=["cine", "cinema"]),
        Variant("ruido-de-pelicula", "Ruido de película", "Film noise", photo="lighthouse", thumb=1.0,
                defines={"TONE": 4, "GRAINK": 2.2, "DUST": 1.0, "HAIR": 0.3, "SCRATCH": 2, "FLICK": 0.9,
                         "VIG": 0.4},
                tags=["ruido", "noise", "grano", "grain"]),
        Variant("pelicula-antigua-1", "Película antigua 1", "Vintage film 1", photo="car", thumb=1.0,
                defines={"TONE": 1, "DUST": 0.5, "HAIR": 0.3, "SCRATCH": 1, "VIG": 0.4, "FLICK": 0.5,
                         "GRAINK": 1.3},
                tags=["blanco y negro", "black and white"]),
        Variant("pelicula-antigua-2", "Película antigua 2", "Vintage film 2", photo="car", thumb=1.0,
                defines={"TONE": 2, "DUST": 0.8, "HAIR": 0.5, "SCRATCH": 2, "VIG": 0.75, "FLICK": 0.6,
                         "GRAINK": 1.2},
                tags=["sepia"]),
        Variant("pelicula-muy-antigua", "Película muy antigua", "Very old film", photo="car", thumb=1.4,
                defines={"TONE": 1, "DUST": 2.6, "HAIR": 1.6, "SCRATCH": 4, "VIG": 0.9, "FLICK": 1.6,
                         "WEAVE": 1.6, "JUMP": 1.0, "FPS": 14.0, "GRAINK": 1.8},
                tags=["blanco y negro", "black and white", "1920"]),
        Variant("rayas-de-proyector", "Rayas de proyector", "Projector lines", photo="woman", thumb=1.0,
                defines={"PROJ": 1.5, "SCRATCH": 2, "DUST": 0.4, "HAIR": 0.2, "VIG": 0.6, "FLICK": 0.6,
                         "TONE": 4},
                tags=["proyector", "projector", "rayas", "lines"]),
        Variant("vineta-de-pelicula", "Viñeta de película", "Film vignette", photo="woman", thumb=1.0,
                defines={"VIG": 1.25, "TONE": 4, "DUST": 0.3, "HAIR": 0.1, "SCRATCH": 0, "FLICK": 0.7,
                         "GRAINK": 1.1},
                tags=["viñeta", "vignette"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Tape and tube: VHS (chroma bleed, tracking band, static), CRT (curved screen, scanlines, rolling picture),
# horror monitors (bezel with a coloured rim) and a camcorder viewfinder with PLAY ▶, SP and a running timecode.
# ---------------------------------------------------------------------------------------------------------------

# A 3×5 pixel font for the viewfinder (rows top to bottom, bit 14 = top left).
_GLYPHS = {
    "0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111",
    "4": "101101111001001", "5": "111100111001111", "6": "111100111101111", "7": "111001001001001",
    "8": "111101111101111", "9": "111101111001111", "P": "110101110100100", "L": "100100100100111",
    "A": "010101111101101", "Y": "101101010010010", "S": "011100010001110", ":": "000010000010000",
    " ": "000000000000000", "R": "110101110101101", "E": "111100110100111", "C": "011100100100011",
}
_ORDER = list("0123456789PLAYS: REC")
_GLYPH_ARR = "const int GLYPHS[%d] = int[%d](%s);" % (
    len(_ORDER), len(_ORDER), ", ".join(str(int(_GLYPHS[c], 2)) for c in _ORDER))
G = {c: i for i, c in enumerate(_ORDER)}


def _codes(s: str) -> str:
    s = s.ljust(8)[:8]
    return "int[8](" + ", ".join(str(G[c]) for c in s) + ")"


TAPE = Family(
    key="retro_tape", category="retro",
    params=[INTENSITY, SPEED, Param("amount", "Amount", 0.0, 2.5, 1.0), GRAIN,
            Param("color", "Colour", default="#ffffff"), Param("colorA", "Colour A", default="#000000"),
            Param("colorB", "Colour B", default="#000000")],
    photo="woman",
    tags=TAGS + ["vhs", "tv", "crt", "estatica", "static"],
    defines={"BLEED": 0.6, "TRACK": 0.0, "JIT": 0.5, "STATIC": 0.05, "FLOOR": 0.0, "SCAN": 0.4, "CURVE": 0.0,
             "ROLL": 0.0, "DESAT": 0.1, "VIG": 0.4, "SOFT": 0.0, "DIM": 0.0,
             "FRAME": 0.0, "INSET": 0.0, "RADIUS": 0.0, "RIM": 0.0, "OSD": 0.0, "LINES": 240.0},
    body=_GLYPH_ARR + r"""
float glyphPix(int code, vec2 q) {
    if (q.x < 0.0 || q.x >= 3.0 || q.y < 0.0 || q.y >= 5.0) return 0.0;
    ivec2 i = ivec2(floor(q));
    return float((GLYPHS[code] >> (14 - (i.y * 3 + i.x))) & 1);
}
// A line of up to 8 characters, top left at o, one font pixel = ps (toP units).
float textAt(vec2 p, vec2 o, float ps, int codes[8], int n) {
    vec2 q = (p - o) / ps;
    int idx = int(floor(q.x / 4.0));
    if (idx < 0 || idx >= n) return 0.0;
    return glyphPix(codes[idx], vec2(q.x - float(idx) * 4.0, q.y));
}
vec3 vhsSample(vec2 q, float bleed, float soft) {
    vec2 o = vec2(px().x, 0.0);
    vec3 sharp = (Sm(q).rgb * 2.0 + Sm(q - o * (1.0 + soft * 2.0)).rgb + Sm(q + o * (1.0 + soft * 2.0)).rgb) / 4.0;
    vec3 chroma = vec3(0.0);
    for (int i = 0; i < 8; ++i) chroma += Sm(q - vec2(0.0025 * bleed * (float(i) + 1.5), 0.0)).rgb;
    chroma /= 8.0;
    float y = dot(sharp, vec3(0.299, 0.587, 0.114));
    float ci = dot(chroma, vec3(0.596, -0.274, -0.322)) * (1.0 + 0.3 * bleed);
    float cq = dot(chroma, vec3(0.211, -0.523, 0.312)) * (1.0 + 0.3 * bleed);
    return vec3(y + 0.956 * ci + 0.621 * cq, y - 0.272 * ci - 0.647 * cq, y - 1.106 * ci + 1.703 * cq);
}
#define TINT color
#define FRAME_COL colorA
#define RIM_COL colorB
void main() {
    vec4 src = S(v_texCoord);
    float k = intensity;
    float t = u_time * speed;
    float f = floor(t * 30.0);
    float dist = amount;
    vec2 p = toP(v_texCoord);
    // The screen: inset in the frame, the picture scaled to fill it, then bent like a tube.
    vec2 hs = vec2(aspect() * 0.5, 0.5) - INSET;
    vec2 puv = fromP(p / hs * vec2(aspect() * 0.5, 0.5));
    vec2 cq = puv * 2.0 - 1.0;
    cq *= 1.0 + CURVE * vec2(0.06 * cq.y * cq.y, 0.09 * cq.x * cq.x);
    vec2 q = cq * 0.5 + 0.5;
    vec2 sp = (q - 0.5) * vec2(aspect(), 1.0);
    float sd = sdRoundBox(sp, vec2(aspect() * 0.5, 0.5), max(RADIUS, 0.0001));
    float screen = 1.0 - smoothstep(-1.5 * px().y, 0.0, sd);
    if (INSET <= 0.0 && CURVE <= 0.0) screen = 1.0;

    // Vertical hold: every few seconds the picture rolls once.
    float rollOff = 0.0, seam = 0.0;
    if (ROLL > 0.0) {
        float rp = phase(t, 3.2);
        float r = easeInOut(linstep(0.05, 0.35, rp));
        rollOff = r * ROLL * k;
        float y = fract(q.y + rollOff);
        seam = (r > 0.0 && r < 1.0) ? smoothstep(0.05, 0.0, y) + smoothstep(0.97, 1.0, y) : 0.0;
        q.y = y;
    }
    float line = floor(q.y * LINES);
    float by = fract(t * 0.21) * 1.5 - 0.25;
    float band = exp(-pow((q.y - by) / 0.04, 2.0)) * TRACK * dist * k;
    float band2 = exp(-pow((q.y - 0.94 - 0.015 * sin(t * 3.0)) / 0.02, 2.0)) * TRACK * dist * k * 0.6;
    float jit = (hash12(vec2(line, f)) - 0.5) * (0.0025 * JIT * dist * k + 0.05 * (band + band2));
    jit += (vnoise(vec2(q.y * 8.0, t * 4.0)) - 0.5) * 0.004 * JIT * dist * k;
    q.x += jit;

    vec3 c = vhsSample(q, BLEED * dist * k, SOFT);
    c = mix(c, vec3(luma(c)), sat(DESAT * k));
    c *= mix(vec3(1.0), TINT, sat(k));
    c *= 1.0 - DIM * k;

    float n = hash12(floor(v_texCoord * u_resolution / 1.4) + vec2(f * 13.1, f * 7.7));
    float sn = STATIC * grain * k * (0.8 + 0.4 * hash11(f * 0.37));
    c = mix(c, vec3(n), sat(sn));
    // Tracking: white streaks and torn lines inside the band.
    float streak = step(0.8, hash12(vec2(floor(q.y * LINES * 0.5), f + 3.0))) * hash12(vec2(floor(q.x * 40.0), line + f));
    c = mix(c, vec3(0.92), sat((band + band2) * (0.25 + 0.75 * streak) * 0.9));
    // Static gathered at the bottom of the picture.
    if (FLOOR > 0.0) {
        float edge = 0.5 + 0.08 * (vnoise(vec2(q.x * 5.0, t * 1.5)) - 0.5) * 2.0;
        float m = smoothstep(edge, edge + 0.3, q.y) * FLOOR * k * min(grain, 1.5);
        float ln = hash12(vec2(floor(q.y * LINES * 0.7), f)) * 0.6 + 0.4;
        float g = hash12(floor(vec2(q.x * u_resolution.x / 2.0, q.y * LINES * 0.7)) + f * 3.1) * ln;
        c = mix(c * (1.0 - 0.35 * FLOOR * k), vec3(g * 0.85), sat(m));
    }
    c *= 1.0 - seam * 0.9;
    c *= 1.0 - SCAN * k * 0.28 * (0.5 + 0.5 * cos(q.y * LINES * TAU));
    c *= 1.0 - 0.04 * k * sin(t * 60.0 + q.y * 3.0);
    c *= mix(1.0, vignette(q, 0.35, 0.55), VIG * sat(k));
    // Inner glow of the rim (horror monitors).
    c = addLight(c, RIM_COL * exp(max(sd, -1.0) / 0.035) * screen, RIM * k);
    c = sat3(c);

    // The frame around the screen.
    vec3 fr = FRAME_COL * (0.75 + 0.5 * (1.0 - v_texCoord.y));
    fr += 0.08 * exp(-max(sd, 0.0) / 0.01) * step(0.0, sd) * FRAME;
    fr = addLight(fr, RIM_COL * exp(-max(sd, 0.0) / 0.02), RIM * 0.6 * k);
    vec3 outc = mix(fr, c, screen);

    // Camcorder viewfinder: PLAY ▶ and SP on the left, a running timecode on the right.
    if (OSD > 0.0) {
        float ps = 0.0105;
        vec2 tl = vec2(-hs.x + 0.07, -hs.y + 0.065);
        vec2 bl = vec2(-hs.x + 0.07, hs.y - 0.065 - ps * 5.0);
        int s = int(floor(u_time));
        int hh = s / 3600, mm = (s / 60) - (s / 3600) * 60, ss = s - (s / 60) * 60;
        int tc[8] = int[8](hh / 10, hh - (hh / 10) * 10, 15, mm / 10, mm - (mm / 10) * 10, 15, ss / 10,
                           ss - (ss / 10) * 10);
        vec2 br = vec2(hs.x - 0.07 - ps * 31.0, bl.y);
        float txt = 0.0, sh = 0.0;
        vec2 so = vec2(ps * 0.5, ps * 0.5);
        txt += textAt(p, tl, ps, """ + _codes("PLAY") + r""", 4);
        sh += textAt(p - so, tl, ps, """ + _codes("PLAY") + r""", 4);
        txt += textAt(p, bl, ps, """ + _codes("SP") + r""", 2);
        sh += textAt(p - so, bl, ps, """ + _codes("SP") + r""", 2);
        txt += textAt(p, br, ps, tc, 8);
        sh += textAt(p - so, br, ps, tc, 8);
        // ▶ after PLAY.
        vec2 tri = p - (tl + vec2(ps * 18.5, ps * 2.5));
        float dTri = max(-tri.x - ps * 1.6, abs(tri.y) * 1.25 + tri.x * 0.75 - ps * 1.2);
        txt += fillSd(dTri, px().y * 0.7);
        sh += fillSd(max(-(tri.x - so.x) - ps * 1.6, abs(tri.y - so.y) * 1.25 + (tri.x - so.x) * 0.75 - ps * 1.2),
                     px().y * 0.7);
        float a = OSD * sat(k);
        outc = mix(outc, vec3(0.0), sat(sh) * 0.5 * a);
        outc = mix(outc, vec3(0.96), sat(txt) * a);
    }
    float keep = (FRAME > 0.0 || CURVE > 0.0) ? 1.0 : src.a;
    fragColor = vec4(outc, keep);
}
""",
    variants=[
        Variant("tv-antigua-4x", "TV antigua 4x", "Old TV 4x", photo="skater", thumb=0.3,
                params={"color": "#dfeaff", "colorA": "#141414"},
                defines={"CURVE": 1.0, "INSET": 0.02, "RADIUS": 0.05, "FRAME": 1, "SCAN": 0.7, "STATIC": 0.16, "ROLL": 1.0, "BLEED": 1.0, "DESAT": 0.35,
                         "VIG": 0.7, "LINES": 200.0},
                tags=["televisor", "television", "crt"]),
        Variant("video-antiguo", "Vídeo antiguo", "Old video", photo="woman", thumb=1.0,
                params={"color": "#fff3e6"},
                defines={"BLEED": 0.9, "SCAN": 0.5, "VIG": 0.75, "DESAT": 0.3, "STATIC": 0.07, "SOFT": 1.0,
                         "DIM": 0.08, "JIT": 0.6},
                tags=["video", "casero", "home video"]),
        Variant("vhs-estatico-1", "VHS estático 1", "VHS static 1", photo="car", thumb=0.5,
                defines={"BLEED": 1.3, "TRACK": 1.0, "STATIC": 0.14, "SCAN": 0.45, "JIT": 1.0, "VIG": 0.3,
                         "DESAT": 0.1},
                tags=["vhs", "cinta", "tape", "tracking"]),
        Variant("estatica-en-el-suelo", "Estática en el suelo", "Static on the floor", photo="lighthouse",
                thumb=1.0,
                defines={"FLOOR": 1.0, "STATIC": 0.08, "BLEED": 0.6, "SCAN": 0.5, "DIM": 0.15, "DESAT": 0.4,
                         "VIG": 0.6},
                tags=["halloween", "estatica", "static", "terror", "horror"]),
        Variant("marco-de-terror", "Marco de terror", "Horror frame", photo="woman", thumb=1.0,
                params={"color": "#c9dccb", "colorA": "#0b0c0b", "colorB": "#9fb8a0"},
                defines={"FRAME": 1, "INSET": 0.07, "RADIUS": 0.07, "CURVE": 0.5, "RIM": 0.35, "SCAN": 0.8, "STATIC": 0.22, "DESAT": 0.75,
                         "VIG": 0.7, "JIT": 0.8, "BLEED": 0.6},
                tags=["terror", "horror", "monitor", "camara de seguridad", "cctv"]),
        Variant("monitor-de-terror", "Monitor de terror", "Horror monitor", photo="woman", thumb=1.0,
                params={"color": "#d6d0d0", "colorA": "#050505", "colorB": "#ff2a3c"},
                defines={"FRAME": 1, "INSET": 0.05, "RADIUS": 0.09, "CURVE": 0.8, "RIM": 0.55, "SCAN": 0.9, "STATIC": 0.18, "DESAT": 0.85,
                         "VIG": 0.8, "JIT": 1.0, "ROLL": 0.0, "TRACK": 0.5, "LINES": 180.0},
                tags=["terror", "horror", "monitor", "crt"]),
        Variant("videocamara-retro", "Videocámara retro", "Retro camcorder", photo="woman", thumb=1.4,
                params={"colorA": "#000000"},
                defines={"FRAME": 1, "INSET": 0.035, "RADIUS": 0.06, "OSD": 1.0,
                         "BLEED": 0.8, "SCAN": 0.3, "STATIC": 0.05, "VIG": 0.6, "JIT": 0.5, "DESAT": 0.1},
                tags=["videocamara", "camcorder", "play", "rec", "vhs"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Film burn: a hole burns through the frame (orange edge, white-hot core), flashes white and starts again.
# ---------------------------------------------------------------------------------------------------------------
BURN = Family(
    key="retro_burn", category="retro",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#ff6b14"), Param("size", "Size", 0.5, 2.0, 1.0)], photo="woman",
    tags=TAGS + ["quemar", "burn", "quemado", "fuga de luz", "light leak"],
    defines={"PERIOD": 2.6},
    body=r"""
void main() {
    vec4 src = S(v_texCoord);
    float k = intensity;
    float t = u_time * speed;
    float cyc = floor(t / PERIOD);
    float ph = fract(t / PERIOD);
    vec2 p = toP(v_texCoord) / size;
    vec2 c0 = (hash22(vec2(cyc, 4.0)) - 0.5) * vec2(aspect() * 0.7, 0.6);
    float b = easeIn(linstep(0.02, 0.9, ph)) * 0.95;
    vec2 wp = p + 0.12 * vec2(fbm(p * 3.0 + cyc), fbm(p * 3.0 + cyc + 5.2));
    float v = fbm(wp * 3.6 + vec2(cyc * 7.3, cyc * 3.1) + vec2(0.0, -t * 0.2)) + 0.45 - length(wp - c0) * 1.05;
    float e = v - (1.0 - b);
    vec3 photo = src.rgb;
    // Before the hole: the frame warms up and a leak of colour crosses it.
    float warm = sat(b * 1.2) * exp(-max(-e, 0.0) * 2.5);
    vec3 leak = mix(vec3(0.15, 0.9, 0.35), vec3(1.0, 0.35, 0.05), smoothstep(-0.6, 0.0, e));
    vec3 col = addLight(photo * mix(vec3(1.0), vec3(1.05, 0.85, 0.65), warm * 0.6), leak * warm, 0.8 * k);
    float rim = exp(-abs(e) * 14.0);
    col = addLight(col, color * vec3(1.0, 0.65, 0.55) * rim, 1.2 * k);
    col = mix(col, vec3(0.08, 0.03, 0.01), smoothstep(0.0, 0.02, e) * smoothstep(0.09, 0.03, e) * 0.6 * sat(k));
    vec3 hot = mix(color * 1.05, mix(color, vec3(1.0, 0.9, 0.6), 0.6), smoothstep(0.05, 0.22, e));
    hot = mix(hot, vec3(1.0, 0.98, 0.92), smoothstep(0.2, 0.45, e));
    hot *= 0.85 + 0.3 * fbm(p * 9.0 + t * 0.8);
    col = mix(col, hot, smoothstep(0.04, 0.12, e) * sat(k));
    // White at the end of the cycle and fading back to the picture at its start.
    float white = max(smoothstep(0.9, 1.0, ph), 1.0 - smoothstep(0.0, 0.05, ph));
    col = mix(col, vec3(1.0, 0.97, 0.9), white * sat(k));
    fragColor = vec4(mix(photo, sat3(col), sat(k)), src.a);
}
""",
    variants=[
        Variant("borrar-pelicula", "Borrar película", "Film burn", photo="woman", thumb=1.6,
                tags=["borrar", "erase"]),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Film strips and slides. MODE: 0 strips rolling past, 1 stacked frames (old lenses), 2 slide swaying,
# 3 slide changes (in from the right, out to the left).
# ---------------------------------------------------------------------------------------------------------------
STRIP = Family(
    key="retro_strip", category="retro",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#1c1c1e"), Param("size", "Size", 0.5, 1.6, 1.0)],
    photo="lighthouse",
    tags=TAGS + ["tira", "strip", "diapositiva", "slide", "fotogramas", "frames"],
    defines={"MODE": 0, "BW": 0.0},
    body=FILM_LIB + r"""
// The photo inside a frame at centre c, half height h (photo aspect), turned by a. Returns colour, alpha.
vec4 framed(vec2 p, vec2 c, float h, float a, float border, vec3 mount) {
    vec2 l = rot(-a) * (p - c);
    vec2 hi = vec2(aspect() * 0.5, 0.5) * h * 2.0;
    float dImg = sdBox(l, hi);
    float dOut = sdRoundBox(l, hi + border, border * 0.35);
    float aa = px().y * 1.2;
    vec3 img = Sm(fromP(l / (h * 2.0))).rgb;
    float bev = exp(-abs(dOut) / (border * 0.25 + 1e-4));
    vec3 m = mount * (0.85 + 0.3 * (0.5 - l.y / (hi.y * 2.0))) + 0.08 * bev;
    vec3 col = mix(m, img, fillSd(dImg, aa));
    return vec4(col, fillSd(dOut, aa));
}
vec3 shadowed(vec3 bg, vec2 p, vec2 c, float h, float a, float border) {
    vec2 l = rot(-a) * (p - c - vec2(0.012, 0.02));
    vec2 hi = vec2(aspect() * 0.5, 0.5) * h * 2.0 + border;
    return bg * (1.0 - 0.55 * fillSd(sdRoundBox(l, hi, border), 0.05));
}
void main() {
    vec4 src = S(v_texCoord);
    float k = intensity;
    float t = u_time * speed;
    vec2 p = toP(v_texCoord);
    vec3 col;
    if (MODE < 0.5) {
        // Three strips of film rolling past, alternate directions, with sprocket holes.
        vec2 q = rot(-0.06) * p * 1.08;
        float rows = 3.0 / size;
        float r = floor((q.y + 0.5) * rows);
        float ly = fract((q.y + 0.5) * rows) - 0.5;            // -0.5..0.5 inside a strip
        float dir = mod(r, 2.0) < 0.5 ? 1.0 : -1.0;
        float fh = 0.70;                                         // frame height, strip units
        float fw = fh * aspect() + 0.1;                          // frame width with its gap
        float x = q.x * rows + dir * t * 0.6 + r * 0.37;
        float fi = floor(x / fw);
        float lx = x - fi * fw - fw * 0.5;
        vec2 img = vec2(lx / (fh * aspect()), ly / fh) + 0.5;
        float inImg = fillSd(sdBox(vec2(lx, ly), vec2(fh * aspect() * 0.5, fh * 0.5)), 0.01);
        vec3 base = color;
        float hx = fract(x / 0.16) - 0.5;
        float hole = fillSd(sdRoundBox(vec2(hx * 0.16, abs(ly) - 0.425), vec2(0.035, 0.035), 0.012), 0.008);
        vec3 pic = filmTone(Sm(img).rgb, 4.0);
        pic *= 0.9 + 0.1 * hash11(fi + r * 13.0);
        col = mix(base, pic, inImg);
        col = mix(col, vec3(0.92, 0.9, 0.84), hole);
        col += grainN(v_texCoord, floor(t * 18.0)) * 0.04;
    } else if (MODE < 1.5) {
        // Old lenses: copies of the frame stacked in depth, sliding forward one after another.
        col = color * 0.5 + 0.02;
        float kk = fract(t * 0.45);
        for (int i = 0; i < 5; ++i) {
            float s = float(i) + kk;                             // 0 = far back, 4 = front
            vec2 c = vec2(-0.30 * aspect() + 0.15 * aspect() * s * 0.85, -0.16 + 0.07 * s);
            float h = (0.25 + 0.022 * s) * size;
            float fade = smoothstep(0.0, 0.6, s) * (1.0 - smoothstep(4.2, 5.0, s));
            vec4 fr = framed(p, c, h, 0.0, 0.03, color);
            fr.rgb = mix(fr.rgb, color, 1.0 - fillSd(sdBox(rot(0.0) * (p - c), vec2(aspect() * 0.5, 0.5) * h * 2.0), px().y));
            fr.rgb = filmTone(fr.rgb, 1.0) * (0.55 + 0.45 * s / 4.0);
            col = mix(col, fr.rgb, fr.a * fade);
            // A thin light edge so the black frames read against each other.
            float d = sdRoundBox(p - c, vec2(aspect() * 0.5, 0.5) * h * 2.0 + 0.03, 0.01);
            col += vec3(0.5) * exp(-abs(d) * u_resolution.y * 0.9) * fade * 0.35;
        }
        col += grainN(v_texCoord, floor(t * 18.0)) * 0.05;
        col *= filmVig(v_texCoord, 0.5);
    } else {
        // Slides: the photo in a mount over a blurred, darker copy of itself.
        vec3 bg = (discBlur(v_texCoord, 0.022).rgb + discBlur(v_texCoord + vec2(0.006, 0.004), 0.03).rgb) * 0.21;
        bg *= vignette(v_texCoord, 0.3, 0.6) * 0.6 + 0.4;
        vec2 c = vec2(0.0);
        float a, h;
        if (MODE < 2.5) {
            a = -0.07 + 0.06 * sin(t * 1.2);
            h = (0.33 + 0.012 * sin(t * 0.9 + 1.0)) * size;
            c = vec2(0.02 * sin(t * 0.8), 0.01 * cos(t * 1.1));
        } else {
            float ph = phase(t, 2.2);
            float in_ = easeOut(linstep(0.0, 0.28, ph));
            float out_ = easeIn(linstep(0.78, 1.0, ph));
            c = vec2(aspect() * 1.1 * (1.0 - in_) - aspect() * 1.1 * out_, 0.0);
            a = 0.08 * (1.0 - in_) - 0.1 * out_ + 0.03;
            h = 0.32 * size;
        }
        bg = shadowed(bg, p, c, h, a, 0.04);
        vec4 fr = framed(p, c, h, a, 0.04, color);
        col = mix(bg, fr.rgb, fr.a);
    }
    if (BW > 0.0) col = mix(col, vec3(luma(col)), BW);
    fragColor = vec4(mix(src.rgb, sat3(col), sat(k)), 1.0);
}
""",
    variants=[
        Variant("laminacion-de-pelicula", "Laminación de película", "Film roll", photo="lighthouse", thumb=1.0,
                defines={"MODE": 0}, params={"color": "#120e0b"}, tags=["rollo", "roll"]),
        Variant("lentes-de-camara-viejas", "Lentes de cámara viejas", "Old camera lenses", photo="car", thumb=1.0,
                defines={"MODE": 1}, params={"color": "#000000"}, tags=["lentes", "lens", "blanco y negro", "black and white"]),
        Variant("diapositivas-de-la-pelicula-1", "Diapositivas de la película 1", "Film slides 1", photo="woman",
                thumb=1.0, defines={"MODE": 2}, params={"color": "#1c1c1e"}),
        Variant("diapositivas-de-la-pelicula-2", "Diapositivas de la película 2", "Film slides 2", photo="woman",
                thumb=1.0, defines={"MODE": 3}, params={"color": "#ece8de"}),
    ],
)

# ---------------------------------------------------------------------------------------------------------------
# Cinema bars: black bars slide in and the picture takes a light film grade.
# ---------------------------------------------------------------------------------------------------------------
BARS = Family(
    key="retro_bars", category="retro", params=[INTENSITY, SPEED, Param("size", "Size", 0.3, 2.0, 1.0)],
    photo="lighthouse", tags=TAGS + ["barras", "bars", "cine", "cinema", "letterbox", "cinematografico"],
    defines={"BAR": 0.12},
    body=r"""
void main() {
    vec4 src = S(v_texCoord);
    float k = intensity;
    float e = easeOut(linstep(0.0, 0.9, u_time * speed));
    float h = BAR * size * e;
    float y = v_texCoord.y;
    float aa = 1.0 / max(u_resolution.y, 1.0);
    float bar = 1.0 - smoothstep(h - aa, h + aa, y) + smoothstep(1.0 - h - aa, 1.0 - h + aa, y);
    vec3 c = src.rgb;
    vec3 g = contrastColor(c, 1.08);
    g = mix(g * vec3(0.95, 1.0, 1.05), g * vec3(1.06, 1.0, 0.92), smoothstep(0.25, 0.75, luma(c)));
    c = mix(c, sat3(g), sat(k) * e);
    c = mix(c, vec3(0.0), sat(bar) * sat(k));
    fragColor = vec4(c, max(src.a, sat(bar) * sat(k)));
}
""",
    variants=[
        Variant("barras-de-cine", "Barras de cine", "Cinema bars", photo="lighthouse", thumb=1.4,
                tags=["titulo", "title"]),
    ],
)

FAMILIES = [OLD_FILM, TAPE, BURN, STRIP, BARS]
