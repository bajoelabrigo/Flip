"""Efectos › Tendencias: Dividir y copias (the picture cut into doors, quarters, strips, panels and cards) and
Abrir y cerrar (the clip opens at its start or closes at its end through a slit, an iris or a flash)."""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)

# Shared by the split families: a dim, blurred copy of the picture behind the pieces.
BG = r"""
vec3 backdrop(vec2 uv, float dim) {
    return discBlur(uv, 0.06).rgb * dim;
}
"""

# Brushed metal doors that slide open on the picture and close again (a lift).
ELEVATOR = Family(
    key="div_elevator", category="dividir", params=[INTENSITY, SPEED], photo="woman",
    tags=["ascensor", "elevator", "puertas", "doors", "abrir", "open", "metal"],
    body=r"""
vec3 metal(vec2 uv, float side) {
    float brush = vnoise(vec2(uv.x * 420.0, uv.y * 3.0)) * 0.6 + vnoise(vec2(uv.x * 1300.0, uv.y * 9.0)) * 0.4;
    float sheen = 0.5 + 0.5 * cos((uv.x * 3.0 + side * 0.7) * PI);
    vec3 c = vec3(0.50, 0.52, 0.55) * (0.78 + 0.22 * brush) + vec3(0.18) * sheen * smoothstep(0.0, 0.6, 1.0 - abs(uv.y - 0.35));
    // A faint reflection of the picture in the steel.
    c = mix(c, discBlur(vec2(1.0 - uv.x, uv.y), 0.08).rgb, 0.12);
    return c;
}
void main() {
    vec4 src = S(v_texCoord);
    vec2 uv = v_texCoord;
    float ph = phase(u_time * speed, 3.0) * 3.0;
    float open = easeInOut(linstep(0.15, 1.05, ph)) * (1.0 - easeInOut(linstep(2.2, 2.95, ph)));
    float o = 0.5 * open;
    float fw = max(px().x, 0.0008);
    float leftDoor = 1.0 - smoothstep(0.5 - o - fw, 0.5 - o + fw, uv.x);
    float rightDoor = smoothstep(0.5 + o - fw, 0.5 + o + fw, uv.x);
    vec3 col = src.rgb;
    // Shadow the doors cast on the picture near their edges.
    float sh = exp(-max(uv.x - (0.5 - o), 0.0) * 40.0) * step(0.5 - o, uv.x) + exp(-max((0.5 + o) - uv.x, 0.0) * 40.0) * step(uv.x, 0.5 + o);
    col *= 1.0 - 0.45 * sh * step(0.002, o);
    // Each door's own coordinate (it slides with the door).
    vec2 lu = vec2(uv.x + o, uv.y), ru = vec2(uv.x - o, uv.y);
    vec3 dl = metal(lu, -1.0), dr = metal(ru, 1.0);
    // Edge bevels and the seam in the middle.
    dl *= 1.0 - 0.5 * smoothstep(0.012, 0.0, 0.5 - lu.x) ;
    dl += 0.25 * smoothstep(0.006, 0.0, abs(0.5 - 0.014 - lu.x));
    dr *= 1.0 - 0.5 * smoothstep(0.012, 0.0, ru.x - 0.5);
    dr += 0.25 * smoothstep(0.006, 0.0, abs(ru.x - 0.5 - 0.014));
    // Horizontal panel lines.
    float lines = smoothstep(0.004, 0.0, abs(fract(uv.y * 3.0) - 0.5) - 0.497);
    dl *= 1.0 - 0.15 * lines; dr *= 1.0 - 0.15 * lines;
    col = mix(col, dl, leftDoor);
    col = mix(col, dr, rightDoor);
    fragColor = vec4(mix(src.rgb, col, sat(intensity)), src.a);
}
""",
    variants=[
        Variant("apertura-de-ascensor", "Apertura de ascensor", "Elevator opening", thumb=0.6, photo="fx-woman-04",
                tags=["ascensor", "elevator"]),
    ],
)

# The picture cut into quarters that fly in from the corners, join, and fly apart again.
QUARTERS = Family(
    key="div_quarters", category="dividir", params=[INTENSITY, SPEED], photo="skater",
    tags=["cuartos", "quarters", "dividir", "split", "unir", "merge"],
    body=BG + r"""
void main() {
    vec4 src = S(v_texCoord);
    float ph = phase(u_time * speed, 2.0) * 2.0;
    float inK = 1.0 - easeOut(linstep(0.0, 0.9, ph));
    float outK = easeIn(linstep(1.7, 2.0, ph));
    float d = (inK + outK) * 0.7 * intensity;
    vec3 col = backdrop(v_texCoord, 0.25);
    float a = 0.0;
    for (int i = 0; i < 4; ++i) {
        vec2 dir = vec2(i == 0 || i == 2 ? -1.0 : 1.0, i < 2 ? -1.0 : 1.0);
        float lag = float(i) * 0.06;
        float di = d * (1.0 + lag * 4.0 * step(0.0001, d));
        vec2 uv = v_texCoord - dir * di * vec2(1.0 / aspect(), 1.0) * 0.6;
        // This quarter only: its own half on each axis, with a thin gap.
        vec2 q = (uv - 0.5) * dir;
        float g = 0.003 * step(0.0005, d);
        float inside = step(g, q.x) * step(g, q.y) * insideUv(uv);
        vec4 c = S(uv);
        col = mix(col, c.rgb, inside);
        a = max(a, inside);
    }
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("fusion-de-cuartos", "Fusión de cuartos", "Quarter merge", thumb=0.5, photo="fx-skater-02",
                tags=["cuartos", "quarters"]),
    ],
)

# The picture copied into round bubbles that pop up, float and burst, over a dim blurred copy.
BUBBLES = Family(
    key="div_bubbles", category="dividir", params=[INTENSITY, SPEED], photo="woman",
    tags=["burbujas", "bubbles", "dividir", "split", "copias", "clones"],
    body=BG + r"""
vec4 bubble(vec2 p, vec2 c, float r, float ph, float delay) {
    float k = easeOutBack(linstep(delay, delay + 0.45, ph)) * (1.0 - easeIn(linstep(2.55, 2.9, ph)));
    float rr = r * k;
    if (rr < 0.001) return vec4(0.0);
    vec2 d = (p - c) / rr;
    float l = length(d);
    float m = fillSd(l - 1.0, 2.0 / u_resolution.y / rr);
    if (m <= 0.0) return vec4(0.0);
    float z = sqrt(max(1.0 - l * l, 0.0));
    // The whole picture inside the bubble, bulging like a lens.
    vec2 q = d * 0.5 * (0.65 + 0.35 * z);
    vec3 col = Sm(fromP(q)).rgb;
    float rim = smoothstep(0.75, 1.0, l);
    col = mix(col, col * 0.75 + vec3(0.25, 0.3, 0.35), rim * 0.5);
    float hl = exp(-dot(d - vec2(-0.38, -0.42), d - vec2(-0.38, -0.42)) * 18.0);
    col = addLight(col, vec3(1.0), hl * 0.8 + rim * rim * 0.35);
    return vec4(col, m);
}
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    float ph = phase(t, 3.0) * 3.0;
    float asp = aspect();
    float s = min(asp, 1.0);
    vec3 col = mix(src.rgb, backdrop(v_texCoord, 0.45), sat(intensity));
    vec2 b = vec2(sin(t * 1.7), cos(t * 1.3)) * 0.015;
    vec4 b0 = bubble(p, vec2(0.0, 0.02) + b, 0.33 * s, ph, 0.0);
    vec4 b1 = bubble(p, vec2(-0.30 * asp, -0.22) + b.yx, 0.16 * s, ph, 0.15);
    vec4 b2 = bubble(p, vec2(0.30 * asp, 0.24) - b, 0.19 * s, ph, 0.3);
    vec4 b3 = bubble(p, vec2(0.34 * asp, -0.28) + b * 1.5, 0.10 * s, ph, 0.45);
    vec4 b4 = bubble(p, vec2(-0.33 * asp, 0.3) - b.yx, 0.09 * s, ph, 0.55);
    col = mix(col, b4.rgb, b4.a);
    col = mix(col, b3.rgb, b3.a);
    col = mix(col, b1.rgb, b1.a);
    col = mix(col, b2.rgb, b2.a);
    col = mix(col, b0.rgb, b0.a);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("division-de-burbujas", "División de burbujas", "Bubble split", thumb=1.2, photo="fx-woman-03",
                tags=["burbujas", "bubbles"]),
    ],
)

# Vertical strips that slide in from above and below in turn, hold, and slide out.
STRIPS = Family(
    key="div_strips", category="dividir", params=[INTENSITY, SPEED], photo="skater",
    tags=["tiras", "strips", "cortes", "cuts", "dividir", "split"],
    defines={"N": 6.0},
    body=BG + r"""
void main() {
    vec4 src = S(v_texCoord);
    float i = floor(v_texCoord.x * N);
    float dir = mod(i, 2.0) < 0.5 ? -1.0 : 1.0;
    float ph = phase(u_time * speed, 2.0) * 2.0 - i * 0.05;
    float inK = 1.0 - easeOut(linstep(0.0, 0.55, ph));
    float outK = easeIn(linstep(1.45, 1.75, ph));
    float off = dir * (inK - outK) * 1.05 * intensity;
    vec2 uv = vec2(v_texCoord.x, v_texCoord.y + off);
    float m = insideUv(uv);
    // A thin dark seam between strips while they move.
    float fx = fract(v_texCoord.x * N);
    float seam = smoothstep(0.012, 0.0, min(fx, 1.0 - fx)) * step(0.001, abs(off));
    vec3 col = mix(backdrop(v_texCoord, 0.2), S(uv).rgb, m);
    col *= 1.0 - 0.7 * seam;
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("cortes-en-tiras", "Cortes en tiras", "Strip cuts", thumb=0.35, photo="fx-skater-04",
                tags=["tiras", "strips"]),
    ],
)

# A comic page: three slanted panels with white gutters, each a different framing of the picture that drifts.
COMIC = Family(
    key="div_comic", category="dividir", params=[INTENSITY, SPEED], photo="man",
    tags=["comic", "cómic", "paneles", "panels", "viñetas", "dividir", "split"],
    body=r"""
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float asp = aspect();
    float t = u_time * speed;
    float ph = phase(t, 3.0) * 3.0;
    // The gutters slide into place at the start of each loop.
    float k = easeOutBack(linstep(0.0, 0.5, ph));
    float x0 = mix(-asp * 0.5 - 0.1, 0.06 * asp, k) - 0.16 * p.y;
    float dA = (p.x - x0) / 1.0127;
    float y0 = mix(0.6, 0.02, easeOutBack(linstep(0.15, 0.65, ph))) + 0.14 * p.x;
    float dB = (p.y - y0) / 1.0098;
    vec3 col;
    if (dA < 0.0) {
        col = cam(v_texCoord, vec2(0.45, 0.5), 1.08 + 0.04 * sin(t * 0.8), 0.0, vec2(0.02 * sin(t * 0.6), 0.0)).rgb;
    } else if (dB < 0.0) {
        col = cam(v_texCoord, vec2(0.62, 0.32), 1.9 + 0.1 * sin(t * 0.9), 0.0, vec2(0.13 - 0.02 * sin(t * 0.7), 0.12)).rgb;
    } else {
        col = cam(v_texCoord, vec2(0.5, 0.6), 1.45, 0.0, vec2(-0.06 + 0.03 * sin(t * 0.5), -0.08)).rgb;
    }
    // A touch of ink: more contrast and a halftone on the shadows.
    col = sat3(contrastColor(col, 1.15));
    vec2 hp = rot(0.785) * p * u_resolution.y / 5.0;
    float dots = smoothstep(0.35, 0.25, length(fract(hp) - 0.5) - (0.5 - luma(col)) * 0.5);
    col *= 1.0 - 0.18 * dots * smoothstep(0.45, 0.15, luma(col));
    // Gutters, outlines and the page border.
    float gw = 0.012;
    float g = min(abs(dA), dA > 0.0 ? abs(dB) : 1.0);
    float pw = 1.0 / u_resolution.y;
    float border = sdBox(p, vec2(asp * 0.5, 0.5) - 0.022);
    float white = max(1.0 - smoothstep(gw - pw, gw + pw, g), smoothstep(-pw, pw, border));
    float ink = max(smoothstep(gw + 2.5 * pw, gw + pw, g) * (1.0 - white), smoothstep(-3.0 * pw, -pw, border) * (1.0 - white));
    col = mix(col, vec3(0.06), ink);
    col = mix(col, vec3(0.97, 0.96, 0.93), white);
    fragColor = vec4(mix(src.rgb, col, sat(intensity)), src.a);
}
""",
    variants=[
        Variant("pista-multiple-de-comics", "Pista múltiple de cómics", "Multi-panel comic", thumb=1.4,
                photo="fx-man-04", tags=["comic", "panels"]),
    ],
)

# The picture as a card in 3D over a dim blurred copy of itself: tilted in perspective, or turning.
CARD3D = Family(
    key="div_card3d", category="dividir", params=[INTENSITY, SPEED, Param("size", "Size", 0.4, 1.0, 0.78)],
    photo="man", tags=["3d", "tarjeta", "card", "perspectiva", "perspective", "inclinar", "tilt"],
    defines={"MODE": 0.0},
    body=BG + r"""
mat3 rotX(float a) { float c = cos(a), s = sin(a); return mat3(1.0, 0.0, 0.0, 0.0, c, s, 0.0, -s, c); }
mat3 rotY(float a) { float c = cos(a), s = sin(a); return mat3(c, 0.0, -s, 0.0, 1.0, 0.0, s, 0.0, c); }
mat3 rotZ(float a) { float c = cos(a), s = sin(a); return mat3(c, s, 0.0, -s, c, 0.0, 0.0, 0.0, 1.0); }
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    float k = sat(intensity);
    float yaw, pitch, roll;
    if (MODE < 0.5) {   // tilted in perspective, swaying a little
        yaw = (0.55 + 0.12 * sin(t * 1.2)) * k;
        pitch = (-0.28 + 0.08 * sin(t * 0.9 + 1.0)) * k;
        roll = (0.06 + 0.03 * sin(t * 0.7)) * k;
    } else {            // a card turning back and forth
        yaw = 0.75 * sin(t * 1.6) * k;
        pitch = 0.22 * sin(t * 1.1 + 0.5) * k;
        roll = 0.05 * sin(t * 0.8) * k;
    }
    mat3 R = rotY(yaw) * rotX(pitch) * rotZ(roll);
    float F = 1.6;
    vec3 c = vec3(0.0, 0.0, F);
    vec3 n = R * vec3(0.0, 0.0, 1.0);
    vec3 r = vec3(p, F);
    float th = dot(c, n) / dot(r, n);
    vec3 l = transpose(R) * (r * th - c);
    vec2 q = l.xy / size;
    vec2 halfSize = vec2(aspect() * 0.5, 0.5);
    float d = sdBox(q, halfSize);
    float pw = 1.5 / u_resolution.y / size;
    float m = (1.0 - smoothstep(-pw, pw, d)) * step(0.0, th);
    vec3 col = backdrop(v_texCoord, 0.3);
    // Soft shadow under the card.
    float sd = sdBox(p - vec2(0.03, 0.04), halfSize * size * 0.95);
    col *= 1.0 - 0.6 * (1.0 - smoothstep(-0.02, 0.08, sd));
    vec3 card = S(fromP(q)).rgb;
    // Light falls off with the turn, and a thin white edge.
    float shade = 0.82 + 0.18 * abs(n.z);
    card *= shade;
    card = addLight(card, vec3(1.0), 0.25 * exp(-abs(dot(normalize(l.xy + 1e-4), vec2(0.7, -0.7)) - 1.0) * 6.0) * smoothstep(-0.2, 0.0, d));
    card = mix(card, vec3(0.95), smoothstep(-pw * 3.5, -pw * 1.5, d));
    col = mix(col, card, m);
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("inclinar-en-perspectiva", "Inclinar en perspectiva", "Perspective tilt", thumb=1.0,
                defines={"MODE": 0.0}, photo="fx-man-01", tags=["perspectiva", "perspective", "esquinas", "corner pin"]),
        Variant("tarjeta-3d", "Tarjeta 3D", "3D card", thumb=0.7, defines={"MODE": 1.0}, photo="fx-man-05",
                tags=["3d", "tarjeta", "card", "girar", "turn"]),
    ],
)

# Diagonal (bevel) cuts: three bands that slide along the diagonal, or one slanted window that flickers.
BEVEL = Family(
    key="div_bevel", category="dividir", params=[INTENSITY, SPEED], photo="skater",
    tags=["bisel", "bevel", "diagonal", "corte", "cut", "dividir", "split"],
    defines={"MODE": 0.0},
    body=BG + r"""
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float asp = aspect();
    float t = u_time * speed;
    float k = sat(intensity);
    vec2 n = normalize(vec2(1.0, 0.62));
    vec2 tg = vec2(-n.y, n.x);
    float s = dot(p, n);
    vec3 col;
    if (MODE < 0.5) {
        // Three bands; the outer two slide in along the cut from opposite ends, hold, and slide out.
        float ph = phase(t, 2.0) * 2.0;
        float off = ((1.0 - easeOut(linstep(0.0, 0.6, ph))) + easeIn(linstep(1.6, 2.0, ph))) * 1.1 * k;
        float W = 0.16;
        float band = s < -W ? -1.0 : (s > W ? 1.0 : 0.0);
        vec2 sh = tg * off * band;
        vec2 uv = fromP(p - sh);
        float m = insideUv(uv);
        col = mix(backdrop(v_texCoord, 0.18), S(uv).rgb, m);
        if (band == 0.0) col = addLight(col, vec3(1.0), 0.06);
        float pw = 1.0 / u_resolution.y;
        float seam = smoothstep(2.0 * pw, 0.0, min(abs(s + W), abs(s - W)));
        col = mix(col, vec3(0.05), seam * step(0.002, off));
        col = addLight(col, vec3(1.0), 0.7 * seam * step(0.002, off) * 0.0);
    } else {
        // A slanted window of the bright picture over a dark blurred copy; edges flicker to the beat.
        float bi = floor(t / 0.5);
        float b = beat(t, 0.5, 0.18);
        vec2 jit = (hash22(vec2(bi, 3.1)) - 0.5) * vec2(0.18, 0.08) * k;
        vec2 w = p - jit;
        float skew = w.x - 0.55 * w.y;
        float d = max(abs(skew) - 0.33 * asp * 0.62, abs(w.y) - 0.3);
        float pw = 1.5 / u_resolution.y;
        float m = 1.0 - smoothstep(-pw, pw, d);
        vec3 inner = cam(v_texCoord, vec2(0.5) + jit * vec2(1.0 / asp, 1.0), 1.06, 0.0, vec2(0.0)).rgb;
        inner = addLight(inner, vec3(1.0), 0.04 + 0.25 * b * k);
        col = mix(backdrop(v_texCoord, 0.35), inner, m);
        float flick = 0.55 + 0.45 * step(0.4, hash11(floor(t * 14.0)));
        float e = glowSd(d, 2.0 * pw, 0.018) * flick * (0.6 + 0.8 * b);
        col = addLight(col, vec3(0.92, 0.97, 1.0), e * k);
        // A glint running along the window.
        float gl = exp(-abs(skew - mix(-0.6, 0.6, phase(t, 1.0)) * asp * 0.5) * 30.0) * m;
        col = addLight(col, vec3(1.0), gl * 0.35 * k);
    }
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("corte-en-bisel", "Corte en bisel", "Bevel cut", thumb=0.3, defines={"MODE": 0.0},
                photo="fx-skater-01", tags=["bisel", "bevel"]),
        Variant("corte-biselado-parpadeante", "Corte biselado parpadeante", "Flickering bevel cut", thumb=1.0,
                defines={"MODE": 1.0}, photo="fx-woman-06", tags=["parpadeo", "flicker"]),
    ],
)

# Flash split cuts: on each beat (120 BPM) a vertical slice of the picture is shifted, smeared and blown out.
FLASHSPLIT = Family(
    key="div_flashsplit", category="dividir", params=[INTENSITY, SPEED], photo="woman",
    tags=["flash", "destello", "dividir", "split", "corte", "cut", "ritmo", "beat"],
    defines={"MODE": 0.0},
    body=r"""
void main() {
    vec4 src = S(v_texCoord);
    vec2 uv = v_texCoord;
    float t = u_time * speed;
    float k = sat(intensity);
    float bi = floor(t / 0.5);
    float b = beat(t, 0.5, 0.22);
    float lp = phase(t, 0.5);
    vec3 col = src.rgb;
    if (MODE < 0.5) {
        // A smeared, blown-out band that sweeps across the frame on each beat; the rest dims.
        float cx = mix(0.2, 0.8, hash11(bi * 1.7 + 0.3)) + (lp - 0.5) * 0.12;
        float w = mix(0.07, 0.14, hash11(bi + 5.0));
        float m = smoothstep(w, w * 0.4, abs(uv.x - cx));
        vec3 smear = dirBlur(uv + vec2(0.04 * (hash11(bi) - 0.5), 0.0), vec2(0.0, 0.18)).rgb;
        smear = addLight(smear, vec3(1.0), 0.55 + 0.35 * b);
        col *= 1.0 - 0.35 * k;
        col = mix(col, smear, m * k);
        // A thinner echo band.
        float cx2 = fract(cx + 0.37);
        float m2 = smoothstep(w * 0.4, w * 0.1, abs(uv.x - cx2)) * b;
        col = addLight(col, S(uv + vec2(0.03, 0.0)).rgb, m2 * 0.8 * k);
    } else {
        // The frame cut in two at a seam; the right side jumps down, a white flash lights the seam.
        float sx = mix(0.35, 0.65, hash11(bi * 2.3 + 1.0));
        float side = step(sx, uv.x);
        float jump = (hash11(bi + 9.0) - 0.5) * 0.45 * k * (0.4 + 0.6 * b);
        vec2 suv = uv + vec2(0.0, jump * side);
        col = Sm(suv).rgb;
        float seam = exp(-abs(uv.x - sx) * 22.0);
        vec3 smear = dirBlur(uv, vec2(0.0, 0.25)).rgb;
        col = mix(col, addLight(smear, vec3(1.0), 0.9), seam * (0.5 + 0.5 * b) * k);
        col = addLight(col, vec3(1.0), b * b * 0.35 * k);
        col *= 1.0 - 0.25 * k * (1.0 - side) * (1.0 - b);
    }
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("dividir-flash-cut-2", "Dividir flash cut 2", "Split flash cut 2", thumb=1.05, defines={"MODE": 0.0},
                photo="fx-fashion-02", tags=["flash cut"]),
        Variant("corte-de-destello-dividido-1", "Corte de destello dividido 1", "Split flash cut 1", thumb=1.05,
                defines={"MODE": 1.0}, photo="fx-woman-02", tags=["destello", "flash"]),
    ],
)

# Crop: the picture framed in a narrower window with black bars, slowly pushing in.
CROP = Family(
    key="div_crop", category="dividir", params=[INTENSITY, SPEED], photo="lighthouse",
    tags=["recorte", "crop", "barras", "bars", "encuadre", "framing"],
    body=r"""
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    float k = sat(intensity);
    float hw = aspect() * 0.5 * mix(1.0, 0.58 + 0.04 * sin(t * 0.9), k);
    float pw = 1.0 / u_resolution.y;
    float m = 1.0 - smoothstep(hw - pw, hw + pw, abs(p.x));
    vec3 inner = cam(v_texCoord, vec2(0.5), 1.0 + 0.1 * k * (0.5 + 0.5 * sin(t * 0.6)), 0.0, vec2(0.0)).rgb;
    fragColor = vec4(mix(vec3(0.0), inner, m), src.a);
}
""",
    variants=[
        Variant("recorte", "Recorte", "Crop", thumb=1.0, photo="fx-lighthouse-02", tags=["recorte", "crop"]),
    ],
)

# Open and close: the clip opens through a slit or an iris at its start, or closes at its end. Duration of the
# clip = u_time / u_progress; the move takes TRANS seconds (shorter on very short clips).
OPENCLOSE = Family(
    key="abr_openclose", category="abrir", params=[INTENSITY, SPEED], photo="lighthouse",
    tags=["abrir", "open", "cerrar", "close", "transicion", "transition"],
    defines={"SHAPE": 0.0, "CLOSE": 0.0, "FLASH": 0.0, "BLUR": 0.0, "TRANS": 1.0},
    body=r"""
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float asp = aspect();
    float D = u_progress > 1e-4 ? u_time / u_progress : 1e6;
    float dur = min(TRANS / speed, D * 0.45);
    float k;   // 1 = fully open
    if (CLOSE < 0.5) k = easeOut(u_time / dur);
    else k = 1.0 - easeInOut((u_time - (D - dur)) / dur);
    float pw = 1.5 / u_resolution.y;
    float d;   // signed distance to the opening (negative inside)
    if (SHAPE < 0.5) d = abs(p.x) - asp * 0.5 * k;
    else if (SHAPE < 1.5) d = abs(p.y) - 0.5 * k;
    else d = length(p) - length(vec2(asp * 0.5, 0.5)) * k * 1.02;
    float soft = SHAPE > 1.5 ? 0.012 : pw;
    float m = 1.0 - smoothstep(-soft, soft, d);
    float closed = 1.0 - k;
    vec3 col = src.rgb;
    if (BLUR > 0.5) {
        float r = 0.05 * closed * sat(intensity);
        if (SHAPE < 1.5) col = mix(col, dirBlur(v_texCoord, vec2(r * 2.0, 0.0)).rgb, smoothstep(0.0, 0.2, closed));
        else col = mix(col, discBlur(v_texCoord, r).rgb, smoothstep(0.0, 0.2, closed));
        col *= 1.0 - 0.25 * closed * (1.0 - FLASH);
    }
    if (FLASH > 0.5) {
        float f = sat(intensity) * smoothstep(0.0, 0.6, closed);
        col = addLight(col, vec3(1.0, 0.98, 0.94), 0.75 * f);
        // A glow along the edge of the opening.
        col = addLight(col, vec3(1.0), glowSd(d, pw, 0.02) * f * m);
    }
    col = mix(vec3(0.0), col, m);
    if (FLASH > 0.5) col = addLight(col, vec3(1.0, 0.97, 0.9), exp(-max(d, 0.0) * 40.0) * (1.0 - m) * 0.6 * sat(intensity) * smoothstep(0.0, 0.3, closed) * step(0.001, k));
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("abierto-vertical", "Abierto vertical", "Vertical open", thumb=0.5,
                defines={"SHAPE": 0.0, "CLOSE": 0.0}, photo="fx-lighthouse-02", tags=["abrir", "open", "vertical"]),
        Variant("cierre-horizontal", "Cierre horizontal", "Horizontal close", thumb=2.35,
                defines={"SHAPE": 1.0, "CLOSE": 1.0}, photo="fx-lighthouse-03", tags=["cerrar", "close", "horizontal"]),
        Variant("cierre-redondo", "Cierre redondo", "Round close", thumb=2.45,
                defines={"SHAPE": 2.0, "CLOSE": 1.0}, photo="fx-lighthouse-02", tags=["cerrar", "close", "iris", "circulo"]),
        Variant("ronda-abierta", "Ronda abierta", "Round open", thumb=0.35,
                defines={"SHAPE": 2.0, "CLOSE": 0.0}, photo="fx-lighthouse-04", tags=["abrir", "open", "iris", "circulo"]),
        Variant("cerrar-flash", "Cerrar flash", "Flash close", thumb=2.5,
                defines={"SHAPE": 1.0, "CLOSE": 1.0, "FLASH": 1.0, "BLUR": 1.0},
                photo="fx-lighthouse-03", tags=["flash", "cerrar", "close"]),
        Variant("flash-abierto", "Flash abierto", "Flash open", thumb=0.4,
                defines={"SHAPE": 1.0, "CLOSE": 0.0, "FLASH": 1.0, "BLUR": 1.0},
                photo="fx-lighthouse-02", tags=["flash", "abrir", "open"]),
        Variant("ocultar", "Ocultar", "Hide", thumb=2.5,
                defines={"SHAPE": 1.0, "CLOSE": 1.0, "BLUR": 1.0, "TRANS": 1.3},
                photo="fx-lighthouse-04", tags=["ocultar", "hide", "desenfoque", "blur"]),
    ],
)

FAMILIES = [ELEVATOR, QUARTERS, BUBBLES, STRIPS, COMIC, CARD3D, BEVEL, FLASHSPLIT, CROP, OPENCLOSE]
