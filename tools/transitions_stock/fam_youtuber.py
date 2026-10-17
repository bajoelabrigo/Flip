"""YouTuber transitions: the quick, punchy cuts of creator edits (0.4-0.6 s).

Own versions, each one clearly different from the other families: whips that roll the camera, zooms that
jump in steps, a card that flies away, channels that slide apart, a shockwave, a bass thump, a story swipe,
a freeze-frame photo, a blink, a pixel snap, a split screen, a strobe, a jelly pop and a video wall.

A transition carries no audio, so every variant says in its `note` which sound fits (Stock shows it as the
description) and has the sound among its tags.
"""

from kit import Family, Param, Variant

BLUR = Param("blur", "Motion Blur", 0.0, 1.5, 1.0)
AMOUNT = Param("amount", "Intensity", 0.0, 1.5, 1.0)

MIRROR = r"""
vec2 mirrorUv(vec2 u) { return 1.0 - abs(1.0 - mod(u, 2.0)); }
"""


def note(es: str, en: str) -> dict:
    return {"es": es, "en": en}


WHOOSH = note("Combina con un whoosh.", "Pairs with a whoosh.")

WHIP_ROLL = Family(
    key="yt_whip_roll", app_category="cinematic", category="youtuber", duration=0.45, params=[BLUR],
    tags=["youtuber", "whoosh"],
    defines={"DIR": (1.0, 0.0), "ROLL": 0.2, "PUSH": 0.14},
    body=MIRROR + r"""
// A handheld whip: the camera speeds into the cut while it rolls and pushes in, the picture smears
// along the move and the incoming clip lands the same way (mirrored at the frame edges, never black).
vec2 camera(vec2 uv, vec2 off, float ang, float zoom) {
    return fromP(rot(ang) * toP(uv) / zoom) + off;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    bool second = p >= 0.5;
    float t = second ? (1.0 - p) * 2.0 : p * 2.0;  // 0 at both ends, 1 at the cut
    float e = easeIn(t);
    float sgn = second ? -1.0 : 1.0;
    vec2 off = DIR * e * 0.55 * sgn;
    float ang = ROLL * e * sgn;
    float zoom = 1.0 + PUSH * e;
    vec2 base = camera(uv, off, ang, zoom);
    vec2 spread = DIR * blur * 0.32 * e;
    vec4 col = vec4(0.0);
    for (int i = 0; i < 20; ++i) {
        vec2 q = mirrorUv(base + spread * (float(i) / 19.0 - 0.5));
        col += second ? B(q) : A(q);
    }
    fragColor = col / 20.0;
}
""",
    variants=[
        Variant("latigazo-giro-derecha", "Latigazo con giro a la derecha", "Whip roll right",
                tags=["latigazo", "giro", "whip", "roll"], thumb=0.44, note=WHOOSH),
        Variant("latigazo-giro-izquierda", "Latigazo con giro a la izquierda", "Whip roll left",
                {"DIR": (-1.0, 0.0), "ROLL": -0.2}, tags=["latigazo", "giro", "whip", "roll"], thumb=0.44,
                note=WHOOSH),
        Variant("paneo-diagonal-arriba", "Paneo diagonal hacia arriba", "Diagonal whip up",
                {"DIR": (0.75, -0.75), "ROLL": 0.08}, tags=["paneo", "diagonal", "whip pan"], thumb=0.44,
                note=WHOOSH),
        Variant("paneo-diagonal-abajo", "Paneo diagonal hacia abajo", "Diagonal whip down",
                {"DIR": (-0.75, 0.75), "ROLL": -0.08}, tags=["paneo", "diagonal", "whip pan"], thumb=0.44,
                note=WHOOSH),
    ],
)

STEP_ZOOM = Family(
    key="yt_step_zoom", app_category="cinematic", category="youtuber", duration=0.6,
    params=[Param("zoom", "Zoom", 1.2, 3.0, 1.9), BLUR],
    tags=["youtuber", "zoom", "golpe", "hit"],
    defines={"STEPS": 3.0, "OUT": 0.0},
    body=r"""
// Jump-cut zoom: the picture jumps closer in hard steps (each one with a small punch and a lift of
// light); the other clip glides the rest of the way. OUT plays it backwards (glide in, jump out).
float level(float f, float n, out float fr) {
    float k = min(floor(f * n), n - 1.0);
    fr = f * n - k;
    return k;
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 c = vec2(0.5);
    bool onJumps = OUT > 0.5 ? p >= 0.45 : p < 0.55;
    float jumps = OUT > 0.5 ? sat((1.0 - p) / 0.55) : sat(p / 0.55);
    vec4 col;
    if (onJumps) {
        // IN: levels 1, z^(1/S) ... z^((S-1)/S), then the cut. OUT: from z down to 1 in S jumps.
        float n = OUT > 0.5 ? STEPS + 1.0 : STEPS;
        float fr;
        float k = level(jumps, n, fr);
        // Time runs forwards through the steps in both directions, so the punch lands on each jump.
        float since = OUT > 0.5 ? 1.0 - fr : fr;
        float s = pow(zoom, k / STEPS);
        float hit = (OUT > 0.5 ? step(k, STEPS - 0.5) : step(0.5, k)) * exp(-since * 7.0);
        hit *= sat((1.0 - p) * 12.0) * sat(p * 12.0);
        s *= 1.0 + 0.07 * hit;
        vec2 q = c + (uv - c) / s;
        col = OUT > 0.5 ? B(q) : A(q);
        col.rgb = col.rgb * (1.0 + 0.25 * hit) + 0.06 * hit;
    } else {
        float t = OUT > 0.5 ? easeIn(p / 0.45) : easeOut((p - 0.55) / 0.45);
        float s = OUT > 0.5 ? mix(1.0, zoom, t) : mix(zoom, 1.0, t);
        float k = OUT > 0.5 ? t : 1.0 - t;
        vec2 q = c + (uv - c) / s;
        col = OUT > 0.5 ? zoomBlurA(q, c, blur * 0.3 * k) : zoomBlurB(q, c, blur * 0.3 * k);
        float flash = OUT > 0.5 ? exp(-(0.45 - p) * 40.0) : exp(-(p - 0.55) * 40.0);
        col.rgb += 0.3 * flash;
    }
    fragColor = vec4(min(col.rgb, vec3(1.0)), col.a);
}
""",
    variants=[
        Variant("zoom-saltos", "Zoom en saltos", "Step zoom in", tags=["saltos", "jump cut", "step zoom"],
                thumb=0.4, note=note("Combina con un golpe (hit) en cada salto.", "Pairs with a hit on every jump.")),
        Variant("zoom-saltos-atras", "Zoom en saltos hacia atrás", "Step zoom out", {"OUT": 1.0},
                tags=["saltos", "jump cut", "step zoom", "alejar"], thumb=0.62,
                note=note("Combina con un golpe (hit) en cada salto.", "Pairs with a hit on every jump.")),
    ],
)

CARD_REVEAL = Family(
    key="yt_card_reveal", app_category="modern", category="youtuber", duration=0.6, params=[BLUR],
    tags=["youtuber", "revelar", "reveal", "whoosh"],
    defines={"FLY": (0.0, -1.0), "SPIN": 0.12},
    body=r"""
// The outgoing clip pulls back into a rounded card with a white rim and a soft shadow, then flies off;
// the incoming clip behind it comes into focus.
vec4 card(vec2 P, float shrink, float fly, out float shadow) {
    float sc = mix(1.0, 0.52, shrink);
    float ang = -0.05 * shrink + SPIN * fly;
    vec2 off = FLY * vec2(aspect(), 1.0) * 1.25 * fly;
    vec2 ext = vec2(aspect() * 0.5, 0.5);
    vec2 q = rot(ang) * (P - off) / sc;
    float rr = 0.06 * shrink;
    float rim = 0.022 * shrink;
    float aa = max(1.5 / u_resolution.y / sc * sat(shrink * 30.0), 1e-5);
    float d = sdRoundBox(q, ext, rr);
    float inside = 1.0 - smoothstep(-aa, aa, d);
    float framed = 1.0 - smoothstep(-aa, aa, d - rim);
    vec2 qs = rot(ang) * (P - off - vec2(0.015, 0.035)) / sc;
    shadow = (1.0 - smoothstep(-0.02, 0.16, sdRoundBox(qs, ext, rr) * sc)) * shrink;
    vec4 a = A(fromP(q));
    vec3 c = mix(vec3(0.97), a.rgb, inside);
    return vec4(c, framed);
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float shrink = easeOut(linstep(0.0, 0.38, p));
    float fly = easeIn(linstep(0.34, 1.0, p));
    float vel = 3.0 * pow(linstep(0.34, 1.0, p), 2.0);
    float reveal = easeOut(linstep(0.15, 1.0, p));
    vec4 bg = discBlurB(uv, 0.03 * (1.0 - reveal));
    bg.rgb *= mix(0.5, 1.0, reveal);
    vec4 acc = vec4(0.0);
    float sh = 0.0;
    for (int i = 0; i < 8; ++i) {
        float f = max(fly - vel * 0.06 * blur * float(i) / 7.0, 0.0);
        float s;
        acc += card(P, shrink, f, s);
        sh += s;
    }
    acc /= 8.0;
    sh /= 8.0;
    bg.rgb *= 1.0 - 0.5 * sh;
    // acc.rgb is an average of colours weighted by coverage only where covered; un-premultiply gently.
    vec3 cardRgb = acc.a > 0.001 ? acc.rgb : vec3(0.0);
    fragColor = vec4(mix(bg.rgb, cardRgb, acc.a), 1.0);
}
""",
    variants=[
        Variant("alejar-revelar", "Alejar y revelar", "Zoom-out reveal", tags=["alejar", "tarjeta", "card"],
                thumb=0.5, note=WHOOSH),
        Variant("alejar-revelar-lado", "Alejar y lanzar a un lado", "Zoom-out toss", {"FLY": (1.0, 0.15), "SPIN": 0.45},
                tags=["alejar", "lanzar", "card", "toss"], thumb=0.6, note=WHOOSH),
    ],
)

RGB_SLIDE = Family(
    key="yt_rgb_slide", app_category="glitch", category="youtuber", duration=0.45,
    params=[Param("spread", "Channel Split", 0.0, 1.5, 1.0), BLUR],
    tags=["youtuber", "rgb", "glitch"],
    defines={"DIR": (1.0, 0.0)},
    body=r"""
// The red, green and blue layers of the picture slide out one after the other (red leads, blue trails),
// so the move tears into colour fringes and settles back into one clean picture.
vec4 strip(vec2 q) {
    if (insideUv(q) > 0.5) return A(q);
    return B(q - DIR);
}
float slide(float p, float lag) {
    return easeInOut(sat((p - lag) / (1.0 - 0.14 * spread)));
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float lags[3] = float[3](0.0, 0.07 * spread, 0.14 * spread);
    vec3 col = vec3(0.0);
    for (int ch = 0; ch < 3; ++ch) {
        float o = slide(p, lags[ch]);
        float v = (slide(p + 0.02, lags[ch]) - slide(p - 0.02, lags[ch])) / 0.04;
        float len = v * 0.04 * blur * bump(p);
        float acc = 0.0;
        for (int i = 0; i < 10; ++i) acc += strip(uv + DIR * (o + len * (float(i) / 9.0 - 0.5)))[ch];
        col[ch] = acc / 10.0;
    }
    float k = bump(p);
    float line = hash12(vec2(floor(uv.y * u_resolution.y / 3.0), floor(p * 24.0)));
    col += (line - 0.5) * 0.1 * k;
    fragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
}
""",
    variants=[
        Variant("deslizamiento-rgb", "Deslizamiento RGB", "RGB slide", tags=["rgb", "deslizar", "slide", "zap"],
                thumb=0.45, note=note("Combina con un zap o un whoosh digital.", "Pairs with a zap or a digital whoosh.")),
    ],
)

SHOCKWAVE = Family(
    key="yt_shockwave", app_category="cinematic", category="youtuber", duration=0.5, params=[AMOUNT],
    tags=["youtuber", "impacto", "impact", "boom"],
    defines={"FLASHC": "#ffffff"},
    body=r"""
// Impact: the picture leans in, a white hit swaps the clips and a shockwave ring bends the new one as it
// rushes out from the centre.
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float r = (p - 0.5) * 2.0;
    float strength = linstep(0.5, 0.53, p) * (1.0 - linstep(0.6, 1.0, p)) * amount;
    float d = length(P) - r;
    float ring = exp(-pow(d / 0.07, 2.0)) * strength;
    vec2 n = P / max(length(P), 1e-4);
    float z = p < 0.5 ? 1.0 + 0.15 * easeIn(p * 2.0) : 1.0 + 0.12 * (1.0 - easeOut((p - 0.5) * 2.0));
    vec2 Q = (P - n * ring * 0.07) / z;
    vec2 ca = n * ring * 0.012;
    vec2 q = fromP(Q);
    vec3 col;
    if (p < 0.5) col = vec3(A(fromP(Q + ca)).r, A(q).g, A(fromP(Q - ca)).b);
    else col = vec3(B(fromP(Q + ca)).r, B(q).g, B(fromP(Q - ca)).b);
    col += FLASHC * ring * 0.35;
    col = mix(col, FLASHC, peak(p, 0.045) * 0.95 * min(amount, 1.0));
    fragColor = vec4(min(col, vec3(1.0)), 1.0);
}
""",
    variants=[
        Variant("impacto-onda", "Impacto con onda expansiva", "Shockwave impact",
                tags=["onda expansiva", "shockwave", "golpe", "flash"], thumb=0.62,
                note=note("Combina con un boom o un golpe grave.", "Pairs with a boom or a deep hit.")),
    ],
)

BASS = Family(
    key="yt_bass_pulse", app_category="cinematic", category="youtuber", duration=0.6, params=[AMOUNT],
    tags=["youtuber", "bajo", "bass", "ritmo"],
    body=r"""
// Three thumps like a bass drop: the frame kicks outwards with a colour split and a dark vignette on
// each one; the clips swap on the strongest, in the middle.
float beat(float p, float t0) { return p < t0 ? 0.0 : exp(-(p - t0) * 12.0); }
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = beat(p, 0.18) * 0.6 + beat(p, 0.5) + beat(p, 0.78) * 0.45;
    k *= sat((1.0 - p) * 8.0) * amount;
    float s = 1.0 + 0.14 * k;
    vec2 q = 0.5 + (uv - 0.5) / s;
    vec2 off = (uv - 0.5) * 0.035 * k;
    vec3 col = p < 0.5 ? vec3(A(q + off).r, A(q).g, A(q - off).b) : vec3(B(q + off).r, B(q).g, B(q - off).b);
    col *= 1.0 - 0.55 * k * smoothstep(0.25, 0.85, length(toP(uv)));
    col += 0.07 * k;
    fragColor = vec4(min(col, vec3(1.0)), 1.0);
}
""",
    variants=[
        Variant("pulso-bajo", "Pulso de bajo", "Bass pulse", tags=["pulso", "pulse", "drop", "808"], thumb=0.52,
                note=note("Combina con un drop de bajo o un 808.", "Pairs with a bass drop or an 808.")),
    ],
)

SWING = Family(
    key="yt_corner_swing", app_category="modern", category="youtuber", duration=0.5, params=[BLUR],
    tags=["youtuber", "giro", "swing", "whoosh"],
    defines={"PIV": (0.0, 1.0), "SIGN": 1.0},
    body=r"""
// The outgoing clip swings away around its bottom corner like a door kicked open, with a blur along the
// turn and a shadow on the incoming clip, which settles from slightly zoomed out.
vec4 swung(vec2 P, vec2 piv, float ang) {
    vec2 q = rot(-ang) * (P - piv) + piv;
    return Ac(fromP(q));
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    vec2 piv = toP(PIV);
    float e = p * p;
    float ang = SIGN * 1.85 * e;
    float vel = SIGN * 1.85 * 2.0 * p;
    vec4 a = vec4(0.0);
    for (int i = 0; i < 12; ++i) a += swung(P, piv, ang - vel * 0.05 * blur * float(i) / 11.0);
    a /= 12.0;
    vec2 qs = rot(-ang) * (P - piv - vec2(0.03, 0.02)) + piv;
    float sh = (1.0 - smoothstep(-0.02, 0.14, sdBox(qs, vec2(aspect() * 0.5, 0.5)))) * sat(p * 10.0) * sat((1.0 - p) * 5.0);
    float s = mix(0.9, 1.0, easeOut(p));
    vec4 b = B(0.5 + (uv - 0.5) * s);
    b.rgb *= mix(0.55, 1.0, easeOut(p)) * (1.0 - 0.45 * sh);
    fragColor = vec4(a.rgb + b.rgb * (1.0 - a.a), 1.0);
}
""",
    variants=[
        Variant("giro-esquina", "Giro desde la esquina", "Corner swing", tags=["esquina", "corner", "puerta"],
                thumb=0.55, note=WHOOSH),
    ],
)

SMEAR = Family(
    key="yt_smear", app_category="modern", category="youtuber", duration=0.45, params=[BLUR],
    tags=["youtuber", "estela", "smear", "whoosh"],
    defines={"DIR": (-1.0, 0.0)},
    body=r"""
// A smear frame: each row of the picture leaves at its own moment and drags a streak behind it, so the
// edge between the clips is ragged like paint pulled by a brush, then everything snaps into place.
vec4 world(vec2 q) {
    if (insideUv(q) > 0.5) return A(q);
    return B(q - DIR);
}
float travel(float p, float lag) { return easeInOut(sat((p - lag) / 0.72)); }
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float across = dot(uv, abs(DIR.yx));
    float n = vnoise(vec2(across * 9.0, 3.1)) * 0.7 + hash11(floor(across * u_resolution.y / 3.0)) * 0.3;
    float lag = 0.28 * n;
    float o = travel(p, lag);
    float v = (travel(p + 0.02, lag) - travel(p - 0.02, lag)) / 0.04;
    float len = v * 0.09 * blur * bump(p);
    vec4 col = vec4(0.0);
    for (int i = 0; i < 16; ++i) col += world(uv + DIR * (o - len * float(i) / 15.0));
    fragColor = col / 16.0;
}
""",
    variants=[
        Variant("estela-derecha", "Barrido con estela", "Smear swipe", tags=["estela", "smear", "barrido", "swipe"],
                thumb=0.5, note=note("Combina con un whoosh rápido.", "Pairs with a fast whoosh.")),
    ],
)

LUMA_LEAK = Family(
    key="yt_luma_leak", app_category="cinematic", category="youtuber", duration=0.6, params=[AMOUNT],
    tags=["youtuber", "fundido", "luz", "light leak"],
    defines={"C1": "#ff7a2e", "C2": "#ffd36b"},
    body=r"""
// The new clip shows first through the brightest parts of the old one, the dissolving edge glows warm
// and a light leak sweeps across the frame.
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec4 a = A(uv);
    vec4 b = B(uv);
    float key = 1.0 - luma(a.rgb);
    float w = 0.3;
    float m = smoothstep(0.0, 1.0, sat((p * (1.0 + w) - key) / w));
    vec3 col = mix(a.rgb, b.rgb, m);
    float k = bump(p) * amount;
    vec3 lc = mix(C1, C2, sat(uv.y * 1.2 - 0.1));
    col += lc * bump(m) * 0.45 * k;
    vec2 P = toP(uv);
    float sweep = mix(-1.3, 1.3, p);
    float blob = exp(-pow((P.x * 0.9 + P.y * 0.4 - sweep) / 0.45, 2.0)) * (0.6 + 0.6 * fbm(P * 2.0 + p));
    col = 1.0 - (1.0 - col) * (1.0 - lc * blob * 0.85 * k);
    fragColor = vec4(min(col, vec3(1.0)), 1.0);
}
""",
    variants=[
        Variant("fundido-brillo-luz", "Fundido de brillo con luz", "Luma fade with light leak",
                tags=["brillo", "luma", "fade", "calido"], thumb=0.5,
                note=note("Combina con un riser suave o un brillo (shimmer).", "Pairs with a soft riser or a shimmer.")),
    ],
)

STORY = Family(
    key="yt_story_swipe", app_category="modern", category="youtuber", duration=0.45, params=[BLUR],
    tags=["youtuber", "deslizar", "swipe", "movil"],
    defines={"DIR": (1.0, 0.0)},
    body=r"""
// Like swiping stories on a phone: the new clip slides over as a card with rounded corners and a shadow,
// while the old one sinks back, shrinks a little and dims.
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    vec2 ext = vec2(aspect() * 0.5, 0.5);
    vec2 span = DIR * vec2(aspect(), 1.0);
    float e = easeOut(p);
    float v = 3.0 * (1.0 - p) * (1.0 - p);
    float live = sat(p * 40.0);
    // The old clip.
    float sa = 1.0 - 0.08 * e;
    vec2 qa = (P + span * 0.22 * e) / sa;
    float ra = 0.05 * e;
    float aaA = max(1.5 / u_resolution.y * sat(e * 30.0), 1e-5);
    float inA = 1.0 - smoothstep(-aaA, aaA, sdRoundBox(qa, ext, ra));
    vec3 col = mix(vec3(0.03), A(fromP(qa)).rgb * (1.0 - 0.5 * e), inA);
    // The new clip, with a short blur along the swipe.
    vec2 off = span * (1.0 - e) * 1.06;
    float rb = 0.05 * (1.0 - e);
    float aaB = max(1.5 / u_resolution.y * sat((1.0 - e) * 30.0), 1e-5);
    float dB = sdRoundBox(P - off, ext, rb);
    float inB = 1.0 - smoothstep(-aaB, aaB, dB);
    col *= 1.0 - 0.5 * (1.0 - smoothstep(0.0, 0.12, dB)) * live * (1.0 - inB);
    vec4 b = vec4(0.0);
    vec2 bl = DIR * v * 0.02 * blur;
    for (int i = 0; i < 8; ++i) b += B(fromP(P - off) + bl * (float(i) / 7.0 - 0.5));
    b /= 8.0;
    fragColor = vec4(mix(col, b.rgb, inB), 1.0);
}
""",
    variants=[
        Variant("deslizar-historia", "Deslizar historia", "Story swipe", tags=["historia", "story", "movil", "phone"],
                thumb=0.4, note=note("Combina con un swipe o un clic suave.", "Pairs with a swipe or a soft click.")),
        Variant("deslizar-arriba", "Deslizar hacia arriba", "Swipe up", {"DIR": (0.0, 1.0)},
                tags=["feed", "arriba", "swipe up", "phone"], thumb=0.4,
                note=note("Combina con un swipe o un clic suave.", "Pairs with a swipe or a soft click.")),
    ],
)

FREEZE = Family(
    key="yt_freeze_frame", app_category="modern", category="youtuber", duration=0.65, params=[BLUR],
    tags=["youtuber", "congelar", "freeze", "foto"],
    body=r"""
// Freeze frame: a camera flash, the old clip becomes a printed photo with a white border that tilts and
// is tossed off the frame, uncovering the new clip, which comes into focus.
float pose(float p) { return easeOutBack(linstep(0.1, 0.32, p)); }
vec4 photo(vec2 P, float f, float fly, out float shadow) {
    float sc = mix(1.0, 0.7, f);
    float ang = -0.07 * f + 0.4 * fly;
    vec2 off = vec2(aspect() * 1.3, 0.3) * fly;
    vec2 ext = vec2(aspect() * 0.5, 0.5);
    vec2 q = rot(ang) * (P - off) / sc;
    float aa = max(1.5 / u_resolution.y / sc * sat(f * 30.0), 1e-5);
    float din = sdBox(q, ext);
    float rim = 0.05 * sat(f);
    float pic = 1.0 - smoothstep(-aa, aa, din);
    float paper = 1.0 - smoothstep(-aa, aa, din - rim);
    vec2 qs = rot(ang) * (P - off - vec2(0.02, 0.04)) / sc;
    shadow = (1.0 - smoothstep(-0.02, 0.09, (sdBox(qs, ext) - rim) * sc)) * sat(f);
    vec3 a = A(fromP(q)).rgb;
    a = mix(a, vec3(luma(a)) * vec3(1.05, 1.0, 0.92), 0.25 * sat(f));
    return vec4(mix(vec3(0.97, 0.96, 0.93), a, pic), paper);
}
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float f = pose(p);
    float flyT = linstep(0.5, 1.0, p);
    float fly = easeIn(flyT);
    float vel = 3.0 * flyT * flyT;
    float reveal = easeOut(linstep(0.3, 1.0, p));
    vec4 bg = discBlurB(uv, 0.03 * (1.0 - reveal));
    bg.rgb *= mix(0.45, 1.0, reveal);
    vec4 acc = vec4(0.0);
    float sh = 0.0;
    for (int i = 0; i < 8; ++i) {
        float s;
        acc += photo(P, f, max(fly - vel * 0.05 * blur * float(i) / 7.0, 0.0), s);
        sh += s;
    }
    acc /= 8.0;
    bg.rgb *= 1.0 - 0.45 * sh / 8.0;
    vec3 col = mix(bg.rgb, acc.rgb, acc.a);
    col = mix(col, vec3(1.0), exp(-pow((p - 0.1) / 0.035, 2.0)) * 0.9);
    fragColor = vec4(col, 1.0);
}
""",
    variants=[
        Variant("foto-congelada", "Foto congelada", "Freeze frame", tags=["foto", "photo", "camara", "camera"],
                thumb=0.42, note=note("Combina con el obturador de una cámara.", "Pairs with a camera shutter.")),
    ],
)

BLINK = Family(
    key="yt_blink", app_category="cinematic", category="youtuber", duration=0.45, params=[BLUR],
    tags=["youtuber", "parpadeo", "blink", "ojo"],
    body=r"""
// A blink: curved eyelids close over the old clip as it goes soft, and open on the new one.
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    float amt = p < 0.5 ? easeIn(linstep(0.0, 0.44, p)) : 1.0 - easeOut(linstep(0.56, 1.0, p));
    float x = P.x / (aspect() * 0.5);
    float yT = mix(-0.72, 0.06, amt) + 0.16 * (1.0 - x * x);
    float yB = -mix(-0.72, 0.06, amt) - 0.16 * (1.0 - x * x);
    float w = 0.014;
    float lid = max(1.0 - smoothstep(yT - w, yT + w, P.y), smoothstep(yB - w, yB + w, P.y));
    float r = 0.025 * amt * blur;
    vec4 c = p < 0.5 ? discBlurA(uv, r) : discBlurB(uv, r);
    c.rgb *= 1.0 - 0.35 * amt;
    // The lid is dark with a soft shade near its edge.
    float edge = min(abs(P.y - yT), abs(P.y - yB));
    vec3 lc = vec3(0.02) + vec3(0.07, 0.04, 0.04) * exp(-edge * 30.0);
    fragColor = vec4(mix(c.rgb, lc, lid), 1.0);
}
""",
    variants=[
        Variant("parpadeo", "Parpadeo", "Blink", tags=["ojo", "eye", "cerrar"], thumb=0.38,
                note=note("Combina con un clic o un swish corto.", "Pairs with a click or a short swish.")),
    ],
)

PIXEL = Family(
    key="yt_pixel_snap", app_category="glitch", category="youtuber", duration=0.4,
    params=[Param("cells", "Biggest Pixels", 4.0, 40.0, 10.0)],
    tags=["youtuber", "pixel", "8 bits", "retro"],
    body=r"""
// The whole picture snaps into bigger and bigger pixels in a few hard steps, the clips swap cell by cell
// at the blockiest moment and the new one snaps back to sharp.
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float k = floor(pow(bump(p), 2.5) * 6.0 + 0.5) / 6.0;
    if (k <= 0.0) {
        fragColor = p < 0.5 ? A(uv) : B(uv);
        return;
    }
    float n = mix(u_resolution.y / 3.0, cells, pow(k, 0.5));
    vec2 nn = vec2(floor(n * aspect() + 0.5), floor(n + 0.5));
    vec2 id = floor(uv * nn);
    vec2 g = (id + 0.5) / nn;
    float thr = 0.5 + (hash12(id + 7.0) - 0.5) * 0.14;
    vec4 col = mix(A(g), B(g), step(thr, p));
    float lv = 6.0;
    col.rgb = mix(col.rgb, floor(col.rgb * lv + 0.5) / lv, k);
    fragColor = col;
}
""",
    variants=[
        Variant("pixelado-rapido", "Pixelado rápido", "Pixel snap", tags=["pixelado", "pixelate", "blip"], thumb=0.5,
                note=note("Combina con un blip de 8 bits.", "Pairs with an 8-bit blip.")),
    ],
)

SPLIT = Family(
    key="yt_split_screen", app_category="geometric", category="youtuber", duration=0.6,
    params=[Param("line", "Divider", 0.0, 3.0, 1.0)],
    tags=["youtuber", "pantalla dividida", "split screen", "whoosh"],
    body=r"""
// Split screen: the new clip slides in to share the frame half and half with a white divider, holds a
// beat, then takes the whole frame and pushes the old clip out.
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float xb = 1.0 - 0.5 * easeInOut(linstep(0.0, 0.4, p)) - 0.5 * easeInOut(linstep(0.6, 1.0, p));
    vec3 col;
    if (uv.x < xb) col = A(vec2(0.5 + uv.x - xb * 0.5, uv.y)).rgb;
    else col = B(vec2(0.5 + uv.x - (xb + 1.0) * 0.5, uv.y)).rgb;
    float px = 1.0 / u_resolution.x;
    float lw = 0.004 * line;
    float ln = (1.0 - smoothstep(lw, lw + px, abs(uv.x - xb))) * sat(min(xb, 1.0 - xb) * 40.0);
    col = mix(col, vec3(1.0), ln);
    fragColor = vec4(col, 1.0);
}
""",
    variants=[
        Variant("pantalla-dividida", "Pantalla dividida", "Split screen", tags=["dividir", "split", "mitad"],
                thumb=0.5, note=note("Combina con un whoosh doble.", "Pairs with a double whoosh.")),
    ],
)

STROBE = Family(
    key="yt_strobe", app_category="glitch", category="youtuber", duration=0.5, params=[AMOUNT],
    tags=["youtuber", "estrobo", "strobe", "beat"],
    body=r"""
// Strobe cut: the two clips flicker back and forth on hard frames, with white flashes and small camera
// jolts, and more and more of the frames belong to the new clip.
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float idx = floor(p * 22.0);
    float pb = smoothstep(0.2, 0.8, p);
    bool useB = hash11(idx * 1.7 + 3.0) < pb;
    float on = step(0.15, p) * step(p, 0.85) * amount;
    float flash = step(hash11(idx + 11.0), 0.28) * on;
    float z = 1.0 + 0.06 * hash11(idx + 5.0) * on;
    vec2 q = 0.5 + (uv - 0.5) / z + (hash22(vec2(idx, 2.0)) - 0.5) * 0.02 * on;
    vec4 c = useB ? B(q) : A(q);
    c.rgb = mix(c.rgb, (c.rgb - 0.5) * 1.3 + 0.5, min(on, 1.0));
    c.rgb = mix(c.rgb, vec3(1.0), min(flash, 1.0) * 0.75);
    fragColor = vec4(clamp(c.rgb, 0.0, 1.0), c.a);
}
""",
    variants=[
        Variant("corte-estrobo", "Corte estroboscópico", "Strobe cut", tags=["parpadeo", "flicker", "redoble"],
                thumb=0.5, note=note("Combina con un beat rápido o un redoble.", "Pairs with a fast beat or a drum roll.")),
    ],
)

POP = Family(
    key="yt_jelly_pop", app_category="modern", category="youtuber", duration=0.5,
    params=[Param("wobble", "Wobble", 0.0, 1.5, 1.0)],
    tags=["youtuber", "pop", "elastico", "jelly"],
    body=r"""
// Jelly pop: the new clip pops out of the centre as a rounded card that overshoots, squashes and
// stretches like jelly and settles to fill the frame; the old clip dims behind it.
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    vec2 P = toP(uv);
    vec2 ext = vec2(aspect() * 0.5, 0.5);
    float t = p;
    float s = 1.0 - (1.0 - t) * exp(-5.0 * t) * cos(10.0 * t);
    float w = (1.0 - t) * exp(-4.0 * t) * sin(12.0 * t) * 0.35 * wobble;
    vec2 sc = max(vec2(s * (1.0 + w), s * (1.0 - w)), vec2(1e-4));
    vec2 q = P / sc;
    float rr = 0.07 * (1.0 - t);
    float aa = max(1.5 / u_resolution.y / sc.y * sat((1.0 - t) * 30.0), 1e-5);
    float d = sdRoundBox(q, ext, rr);
    float inside = (1.0 - smoothstep(-aa, aa, d)) * sat(t * 200.0);
    float sh = (1.0 - smoothstep(0.0, 0.1, d * sc.y)) * sat(t * 10.0) * (1.0 - inside);
    vec3 a = A(0.5 + (uv - 0.5) * (1.0 - 0.05 * t)).rgb * (1.0 - 0.5 * t) * (1.0 - 0.5 * sh);
    fragColor = vec4(mix(a, B(fromP(q)).rgb, inside), 1.0);
}
""",
    variants=[
        Variant("entrada-pop", "Entrada pop", "Jelly pop", tags=["pop", "rebote", "bounce", "boing"], thumb=0.3,
                note=note("Combina con un pop o un boing.", "Pairs with a pop or a boing.")),
    ],
)

WALL = Family(
    key="yt_video_wall", app_category="geometric", category="youtuber", duration=0.65,
    params=[Param("gap", "Gap", 0.0, 2.0, 1.0)],
    tags=["youtuber", "pantallas", "grid", "mosaico"],
    body=r"""
// Video wall: the camera pulls back to a wall of nine screens of the old clip, the screens pop over to
// the new clip one by one and the camera pushes into the middle screen.
void main() {
    vec2 uv = v_texCoord;
    float p = u_progress;
    float zin = easeInOut(linstep(0.0, 0.32, p));
    float zout = easeInOut(linstep(0.68, 1.0, p));
    float z = 1.0 + 2.0 * (zin - zout);
    vec2 G = (uv - 0.5) * z + 0.5;
    vec2 id = floor(G);
    vec2 l = G - id;
    float g = 0.03 * gap * (z - 1.0) * 0.5;
    float sw = (id.x == 0.0 && id.y == 0.0) ? 0.5 : 0.34 + 0.32 * hash12(id + 4.0);
    // A quick pop as each screen switches: it ducks a little and lights up.
    float pop = 1.0 - sat(abs(p - sw) / 0.045);
    l = 0.5 + (l - 0.5) / (1.0 - 0.18 * pop);
    bool inTile = l.x >= g && l.x <= 1.0 - g && l.y >= g && l.y <= 1.0 - g;
    vec3 col = vec3(0.05);
    if (inTile) col = (p >= sw ? B(l).rgb : A(l).rgb) + 0.45 * pop;
    fragColor = vec4(min(col, vec3(1.0)), 1.0);
}
""",
    variants=[
        Variant("muro-pantallas", "Muro de pantallas", "Video wall", tags=["muro", "wall", "nueve", "clic"],
                thumb=0.5, note=note("Combina con un whoosh y unos clics.", "Pairs with a whoosh and a few clicks.")),
    ],
)

FAMILIES = [WHIP_ROLL, STEP_ZOOM, CARD_REVEAL, RGB_SLIDE, SHOCKWAVE, BASS, SWING, SMEAR, LUMA_LEAK, STORY, FREEZE,
            BLINK, PIXEL, SPLIT, STROBE, POP, WALL]
