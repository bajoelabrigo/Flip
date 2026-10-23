"""Efectos › Tendencias, Movimiento de cámara (primera mitad del catálogo, de «Carrusel feliz» a «Acercamiento de
paralaje»). Two families:

  * RIG: one virtual camera (zoom punches, bounces, pendulum, 3D yaw/pitch with fake perspective, whip spins and
    pans, shakes, parallax push). The motion blur comes from the camera itself: the frame is sampled along the path
    between the camera now and a moment earlier, so any fast move smears the way a real shutter would. Flashes, tint,
    colour split and glow ride on the same beat.
  * CARD: the picture as a card over a blurred copy of itself (flash cuts at new angles, a stacked rotation with
    lagging copies, a tilted card that swings open to full frame).
"""

import math

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)

TAGS = ["camara", "camera", "movimiento", "motion", "zoom"]

RIG = Family(
    key="cam_rig", category="camara", photo="skater", tags=TAGS,
    params=[INTENSITY, SPEED,
            Param("zoom", "Zoom", 0.0, 3.0, 1.0),               # how far the punches / pushes come in
            Param("rotation", "Rotation", 0.0, 3.0, 1.0),       # how far the swings and 3D turns go
            Param("blur", "Blur", 0.0, 5.0, 1.0),               # motion blur (shutter)
            Param("centerX", "Center X", 0.0, 1.0, 0.5),        # where the zoom aims
            Param("centerY", "Center Y", 0.0, 1.0, 0.5),
            Param("frequency", "Frequency", 0.25, 4.0, 1.0),    # beats (or swings) per second
            Param("color", "Colour", default="#ffffff")],       # tint and flash
    defines={
        "PERIOD": 1.0, "PMODE": 0.0, "ATT": 0.05, "DECAY": 0.25, "WPER": 2.0,
        "ZBASE": 1.08, "ZPUNCH": 0.0, "ZWAVE": 0.0, "ZWHIP": 0.0,
        "ROTA": 0.0, "ROTP": 0.0, "ROTWHIP": 0.0, "WHIPT": 0.3, "COVER": 0.9, "PIV": (0.5, 0.5),
        "YAWA": 0.0, "YAWW": 0.0, "PITA": 0.0, "PITPH": 0.0,
        "SWAY": (0.0, 0.0), "JUMP": 0.0, "SHAKE": 0.0, "SHP": 0.0, "SHF": 8.0, "SHAXIS": (1.0, 1.0),
        "PANW": 0.0, "WRAP": 0.0, "PARALLAX": 0.0,
        "BLUR": 1.0, "RGB": 0.0, "FLASH": 0.0, "TINT": "#ffffff", "TINTA": 0.0,
        "CONTR": 0.0, "EXPO": 0.0, "GLOW": 0.0, "VIG": 0.0,
    },
    body=r"""
// The settings people edit (uniforms) behind the names the shader uses.
#define PERIOD (1.0 / max(frequency, 0.05))
#define WPER (WMUL * PERIOD)
#define SHF (SHFM * frequency)
#define BLUR blur
#define TINT color

// One hit: rises over ATT seconds and decays with DECAY. x = seconds since the hit.
float hit(float x) {
    if (x < 0.0) return 0.0;
    return linstep(0.0, max(ATT, 1e-3), x) * exp(-max(x - ATT, 0.0) / DECAY);
}
float pulseAt(float t) {
    float x = phase(t, PERIOD) * PERIOD;
    if (PMODE > 1.5) return wave01(t, PERIOD);
    if (PMODE > 0.5) return min(hit(x) + 0.75 * hit(x - 0.24), 1.0);   // heartbeat: lub-dub
    return hit(x);
}

vec2 rigUv(vec2 uv, float t) {
    float pl = pulseAt(t) * intensity;
    float n = floor(t / PERIOD), ph = phase(t, PERIOD);
    float wv = wave01(t, WPER);
    float sn = sin(TAU * t / WPER);
    float wp = linstep(0.0, WHIPT, ph);
    float whip = n + easeInOut(wp);
    float bsgn = mod(n, 2.0) < 0.5 ? 1.0 : -1.0;

    float a = (ROTA * intensity * sn + ROTP * pl * bsgn) * rotation + ROTWHIP * whip;
    float yaw = YAWA * rotation * intensity * (YAWW > 0.5 ? wv : sn);
    float pitch = PITA * rotation * intensity * sin(TAU * t / WPER + PITPH);
    vec2 off = SWAY * intensity * vec2(sn, sin(TAU * t / WPER * 2.0 + 0.7))
             + vec2(0.0, JUMP * pl)
             + (SHAKE * intensity + SHP * pl) * shake2(t, SHF) * SHAXIS
             + vec2(-PANW * whip, 0.0);
    float k = ZBASE * (1.0 + zoom * (ZPUNCH * pl + ZWAVE * intensity * wv + ZWHIP * intensity * bump(wp)));
    // Turned pictures need a closer camera so the corners stay filled.
    float aw = min(abs(atan(sin(a), cos(a))), 1.0);
    float asp = max(aspect(), 1.0 / aspect());
    k *= mix(1.0, cos(aw) + asp * sin(aw), COVER);
    // A turned plane leaves its far side short of the frame: come closer as it turns.
    k *= 1.0 + 0.5 * abs(sin(yaw)) + 0.5 * abs(sin(pitch));

    vec2 pc = toP(vec2(centerX, centerY));
    vec2 p = toP(uv) - pc;
    // Fake 3D: the picture is a plane turned about the vertical (yaw) and horizontal (pitch) axes.
    const float D = 1.6;
    if (abs(yaw) > 1e-4) {
        float u = p.x * D / (D * cos(yaw) - p.x * sin(yaw));
        p.y *= (u * sin(yaw) + D) / D;
        p.x = u;
    }
    if (abs(pitch) > 1e-4) {
        float v = p.y * D / (D * cos(pitch) - p.y * sin(pitch));
        p.x *= (v * sin(pitch) + D) / D;
        p.y = v;
    }
    // Parallax push: the middle comes closer faster than the edges.
    p /= 1.0 + PARALLAX * zoom * intensity * wv * (1.0 - smoothstep(0.0, 0.85, length(p)));
    p /= max(k, 1e-3);
    vec2 pv = (toP(PIV) - pc) / max(k, 1e-3);
    p = rot(-a) * (p - pv) + pv;
    return fromP(p + pc) - off;
}
vec4 smp(vec2 uv) { return WRAP > 0.5 ? S(fract(uv)) : Sm(uv); }

void main() {
    float t = u_time * speed;
    vec2 uvA = rigUv(v_texCoord, t);
    vec2 uvB = rigUv(v_texCoord, t - 0.03 * BLUR * speed);
    // Very fast moves (whips): keep the smear to a believable length, and dither the samples so no copies show.
    vec2 dm = (uvB - uvA) * vec2(aspect(), 1.0);
    float L = length(dm);
    if (L > 0.14) uvB = uvA + (uvB - uvA) * (0.14 / L);
    float jit = hash12(gl_FragCoord.xy) - 0.5;
    float pl = pulseAt(t) * intensity;
    vec4 col = vec4(0.0);
    if (RGB > 0.0) {
        vec2 sp = (uvA - uvB) * 0.6 * RGB + (v_texCoord - 0.5) * 0.012 * RGB * pl;
        for (int i = 0; i < 8; ++i) {
            vec2 q = mix(uvA, uvB, (float(i) + 0.5 + jit) / 8.0);
            vec4 g = smp(q);
            col += vec4(smp(q + sp).r, g.g, smp(q - sp).b, g.a);
        }
        col /= 8.0;
    } else {
        for (int i = 0; i < 16; ++i) col += smp(mix(uvA, uvB, (float(i) + 0.5 + jit) / 16.0));
        col /= 16.0;
    }
    vec3 c = col.rgb;
    if (GLOW > 0.0) c = addLight(c, brightGlow(uvA, 0.035, 0.55), GLOW * intensity);
    c = mix(c, contrastColor(c, 1.0 + CONTR), sat(pl));
    c *= 1.0 + EXPO * pl;
    c = mix(c, screen(c, TINT * 0.85), sat(TINTA * pl));
    // Without a beat tint or flash, the colour grades the picture (white leaves it as it is).
    if (TINTA <= 0.0 && FLASH <= 0.0) c *= mix(vec3(1.0), TINT, 0.5);
    c = mix(c, TINT, sat(FLASH * pl * pl));
    if (VIG > 0.0) c *= mix(1.0, vignette(v_texCoord, 0.35, 0.5), VIG);
    fragColor = vec4(sat3(c), col.a);
}
""",
    variants=[
        Variant("carrusel-feliz", "Carrusel feliz", "Happy carousel", photo="fx-skater-01", thumb=0.6,
                defines={"YAWA": 0.42, "WPER": 2.0, "SWAY": (0.035, 0.0), "ROTA": 0.025, "ZBASE": 1.2,
                         "BLUR": 1.5},
                tags=["carrusel", "carousel", "3d", "balanceo", "swing"]),
        Variant("salto-violeta-2", "Salto violeta 2", "Violet jump 2", photo="woman", thumb=1.03,
                defines={"PERIOD": 0.5, "ZPUNCH": 0.16, "JUMP": -0.035, "DECAY": 0.18, "TINT": "#9b4dff",
                         "TINTA": 0.95, "BLUR": 1.6},
                tags=["salto", "jump", "violeta", "violet", "ritmo", "beat"]),
        Variant("extremo", "Extremo", "Extreme", photo="fx-skater-06", thumb=1.05,
                defines={"PERIOD": 0.5, "ZPUNCH": 0.24, "SHP": 0.035, "SHF": 14.0, "ROTP": 0.06, "BLUR": 2.2,
                         "CONTR": 0.25, "DECAY": 0.2},
                tags=["extremo", "extreme", "golpe", "punch", "ritmo", "beat"]),
        Variant("templado", "Templado", "Tempered", photo="fx-skater-01", thumb=1.05,
                defines={"ZPUNCH": 0.06, "DECAY": 0.4, "SWAY": (0.01, 0.008), "ROTA": 0.012, "BLUR": 1.0},
                tags=["suave", "soft", "sutil", "subtle"]),
        Variant("voltear-zoom", "Voltear zoom", "Flip zoom", thumb=1.62,
                defines={"PERIOD": 1.5, "ROTWHIP": 2 * math.pi, "WHIPT": 0.35, "ZWHIP": 0.35, "COVER": 0.35,
                         "ZBASE": 1.15, "BLUR": 1.8},
                tags=["voltear", "flip", "giro", "spin", "zoom"]),
        Variant("pendulo", "Péndulo", "Pendulum", thumb=0.4,
                defines={"ROTA": 0.14, "WPER": 1.6, "PIV": (0.5, 0.0), "ZBASE": 1.12, "COVER": 1.0, "BLUR": 1.6},
                tags=["pendulo", "pendulum", "balanceo", "swing", "rotacion"]),
        Variant("movimiento-de-camara-oscilante", "Movimiento de cámara oscilante", "Oscillating camera motion",
                thumb=0.2,
                defines={"SWAY": (0.04, 0.0), "WPER": 0.8, "ROTA": 0.03, "ZBASE": 1.12, "BLUR": 2.5},
                tags=["oscilante", "oscillating", "balanceo", "sway"]),
        Variant("latido-del-corazon", "Latido del corazón", "Heartbeat", thumb=1.03,
                defines={"PMODE": 1.0, "ZPUNCH": 0.12, "DECAY": 0.14, "BLUR": 2.2, "EXPO": 0.3, "GLOW": 0.25},
                tags=["latido", "heartbeat", "pulso", "pulse", "corazon"]),
        Variant("batido-de-latidos-del-corazon", "Batido de latidos del corazón", "Heartbeat shake", thumb=1.03,
                defines={"PMODE": 1.0, "ZPUNCH": 0.1, "DECAY": 0.16, "SHP": 0.03, "SHF": 16.0, "ROTP": 0.04,
                         "BLUR": 2.2},
                tags=["latido", "heartbeat", "sacudir", "shake", "corazon"]),
        Variant("camara-rabiosa", "Cámara rabiosa", "Rabid camera", thumb=1.02,
                defines={"PERIOD": 0.5, "SHAKE": 0.025, "SHF": 18.0, "SHP": 0.04, "ZPUNCH": 0.08, "ROTP": 0.05,
                         "DECAY": 0.15, "BLUR": 3.0, "RGB": 1.0},
                tags=["rabiosa", "rabid", "sacudir", "shake", "caos", "chaos"]),
        Variant("efecto-zoom", "Efecto zoom", "Zoom effect", photo="fx-skater-06", thumb=1.04,
                defines={"ZPUNCH": 0.32, "ATT": 0.02, "DECAY": 0.22, "BLUR": 3.0},
                tags=["zoom", "golpe", "punch", "desenfoque", "blur"]),
        Variant("movimiento-de-camara-3d", "Movimiento de cámara 3D", "3D camera motion", thumb=0.5,
                defines={"YAWA": 0.7, "PITA": 0.2, "PITPH": 1.2, "WPER": 2.0, "SWAY": (0.03, 0.0), "ZBASE": 1.25,
                         "BLUR": 2.2},
                tags=["3d", "perspectiva", "perspective", "giro", "turn"]),
        Variant("movimiento-unidireccional", "Movimiento unidireccional", "One-way motion", thumb=1.12,
                defines={"PANW": 1.0, "WRAP": 1.0, "WHIPT": 0.32, "ZBASE": 1.0, "BLUR": 2.2},
                tags=["barrido", "whip pan", "paneo", "pan", "direccion"]),
        Variant("cuadro-congelado-de-accion", "Cuadro congelado de acción", "Action freeze frame", thumb=1.08,
                defines={"ZPUNCH": 0.1, "ATT": 0.01, "DECAY": 0.45, "FLASH": 0.55, "CONTR": 0.45, "EXPO": 0.25,
                         "BLUR": 1.5},
                tags=["congelado", "freeze", "accion", "action", "flash"]),
        Variant("lente-de-zoom-con-flash", "Lente de zoom con flash", "Flash zoom lens", photo="fx-skater-01", thumb=1.04,
                defines={"ZPUNCH": 0.3, "ATT": 0.02, "DECAY": 0.25, "FLASH": 0.7, "BLUR": 3.0},
                tags=["zoom", "flash", "destello", "lente", "lens"]),
        Variant("movimiento-de-camara-sedoso", "Movimiento de cámara sedoso", "Silky camera motion",
                photo="woman", thumb=0.4,
                defines={"SWAY": (0.05, 0.02), "WPER": 1.6, "ZWAVE": 0.08, "ROTA": 0.02, "ZBASE": 1.12,
                         "BLUR": 4.0, "GLOW": 0.55},
                tags=["sedoso", "silky", "suave", "smooth", "brillo"]),
        Variant("movimiento-de-camara-local", "Movimiento de cámara local", "Local camera motion", photo="woman",
                thumb=1.04,
                defines={"ZPUNCH": 0.15, "DECAY": 0.3, "SHAKE": 0.008, "BLUR": 2.2, "RGB": 1.5},
                tags=["local", "aberracion", "aberration", "zoom", "rgb"]),
        Variant("camara-3d-izquierda", "Cámara 3D izquierda", "3D camera left", photo="man", thumb=1.0,
                defines={"YAWA": -0.65, "YAWW": 1.0, "WPER": 2.0, "ZBASE": 1.2, "BLUR": 1.8},
                tags=["3d", "izquierda", "left", "perspectiva", "perspective"]),
        Variant("giro-de-rotacion", "Giro de rotación", "Rotation spin", photo="cyber", thumb=1.2,
                defines={"PERIOD": 1.2, "ROTWHIP": 2 * math.pi, "WHIPT": 0.35, "COVER": 0.3, "ZBASE": 1.2, "BLUR": 3.0},
                tags=["giro", "spin", "rotacion", "rotation"]),
        Variant("agitar-a-izquierda-y-derecha", "Agitar a izquierda y derecha", "Shake left and right",
                photo="figure", thumb=0.7,
                defines={"SHAKE": 0.035, "SHAXIS": (1.0, 0.0), "SHF": 10.0, "BLUR": 2.0},
                tags=["sacudir", "shake", "lados", "sideways"]),
        Variant("batido-de-pulso-03", "Batido de pulso 03", "Pulse shake 03", photo="woman", thumb=1.03,
                defines={"PERIOD": 0.5, "ZPUNCH": 0.1, "DECAY": 0.18, "SHP": 0.02, "SHF": 14.0, "TINT": "#ff6fae",
                         "TINTA": 0.35, "RGB": 0.6, "BLUR": 1.8},
                tags=["pulso", "pulse", "sacudir", "shake", "ritmo", "beat"]),
        Variant("mini-zoom", "Mini zoom", "Mini zoom", photo="fx-skater-01", thumb=1.02,
                defines={"PERIOD": 0.5, "ZPUNCH": 0.05, "DECAY": 0.15, "BLUR": 1.5},
                tags=["zoom", "mini", "ritmo", "beat"]),
        Variant("acercamiento-de-paralaje", "Acercamiento de paralaje", "Parallax zoom in", photo="fx-skater-06", thumb=1.4,
                defines={"PARALLAX": 0.22, "ZWAVE": 0.12, "WPER": 3.0, "ZBASE": 1.06, "BLUR": 0.6},
                tags=["paralaje", "parallax", "acercar", "zoom in", "profundidad", "depth"]),
    ],
)

CARD = Family(
    key="cam_card", category="camara", photo="man", tags=TAGS,
    params=[INTENSITY, SPEED,
            Param("size", "Size", 0.4, 1.3, 1.0),               # card size
            Param("rotation", "Rotation", 0.0, 3.0, 1.0),       # how far the card turns
            Param("frequency", "Frequency", 0.25, 4.0, 2.0),    # cuts / steps per second
            Param("blur", "Blur", 0.0, 0.15, 0.06)],            # background blur
    defines={"MODE": 0.0, "CUT": 0.5, "TILT": 0.22, "BGK": 0.4, "BGLIFT": 0.0},
    body=r"""
#define CUT (1.0 / max(frequency, 0.05))
#define TILT (TILT0 * rotation)

// The picture as a card: zoom k about the middle, turned by a, shifted by off. Soft, anti-aliased edges.
vec4 card(vec2 uv, float k, float a, vec2 off) {
    vec2 q = camUv(uv, vec2(0.5), k, a, off);
    vec4 c = S(clamp(q, 0.0, 1.0));
    vec2 e = min(q, 1.0 - q) * u_resolution * k;
    return vec4(c.rgb, c.a * sat(min(e.x, e.y) + 0.5));
}
float stackAngle(float t) {
    float n = floor(t / CUT), ph = phase(t, CUT);
    float a0 = sin((n - 1.0) * PI / 3.0), a1 = sin(n * PI / 3.0);
    return TILT * 1.6 * mix(a0, a1, easeOutBack(linstep(0.0, 0.45, ph)));
}
void main() {
    float t = u_time * speed;
    vec2 uv = v_texCoord;
    vec3 bg = discBlur(fromP(toP(uv) / 1.15), blur).rgb;
    bg = mix(bg * BGK, screen(bg, vec3(0.35)), BGLIFT);
    vec4 res = vec4(bg, 1.0);
    float flash = 0.0;
    if (MODE < 0.5) {
        // Flash cuts: every CUT seconds a new angle, size and place, with a white flash on the cut.
        float n = floor(t / CUT), ph = phase(t, CUT);
        float a = (hash11(n * 1.37 + 3.0) - 0.5) * 2.0 * TILT * intensity + 0.05 * ph;
        float k = (0.76 + 0.12 * hash11(n * 2.11 + 7.0) + 0.04 * ph) * size;
        vec2 off = (hash22(vec2(n, 4.0)) - 0.5) * 0.08 * intensity;
        vec4 c = card(uv, k, a, off);
        c.rgb = mix(c.rgb, screen(c.rgb, vec3(0.1, 0.25, 0.3)), 0.5);
        res = over(c, res);
        flash = exp(-ph * CUT / 0.07) * intensity;
    } else if (MODE < 1.5) {
        // Stacked rotation: the card turns in steps and two copies lag behind it.
        for (int i = 2; i >= 0; --i) {
            float lag = float(i) * 0.12;
            float a = (stackAngle(t - lag) - 0.09 * float(i)) * intensity;
            vec4 c = card(uv, (0.8 - 0.02 * float(i)) * size, a, vec2(0.0));
            c.rgb *= 1.0 - 0.3 * float(i);
            c.a *= i == 0 ? 1.0 : 0.55 / float(i);
            res = over(c, res);
        }
    } else {
        // Tilted card that swings open to full frame, holds, and closes.
        float ph = phase(t, CUT);
        float s = ph < 0.3 ? easeOutBack(ph / 0.3) : (ph < 0.75 ? 1.0 : 1.0 - easeInOut((ph - 0.75) / 0.25));
        float a = mix(-TILT * intensity, 0.0, s);
        float k = mix(0.78 * size, 1.04, s);
        res = over(card(uv, k, a, vec2(0.0)), res);
    }
    res.rgb = mix(res.rgb, vec3(1.0), sat(flash) * 0.8);
    fragColor = vec4(res.rgb, S(uv).a);
}
""",
    variants=[
        Variant("rotacion-apilada", "Rotación apilada", "Stacked rotation", photo="fx-figure-03", thumb=1.1,
                defines={"MODE": 1.0, "CUT": 0.5, "TILT": 0.22},
                tags=["rotacion", "rotation", "apilada", "stacked", "copias", "copies"]),
        Variant("inclinar-abierto", "Inclinar abierto", "Tilt open", photo="lighthouse", thumb=0.25,
                defines={"MODE": 2.0, "CUT": 2.0, "TILT": 0.2, "BGK": 0.9, "BGLIFT": 0.6},
                tags=["inclinar", "tilt", "abrir", "open", "tarjeta", "card"]),
        Variant("corte-de-flash-giratorio", "Corte de flash giratorio", "Spinning flash cut", thumb=1.2,
                defines={"MODE": 0.0, "CUT": 0.5, "TILT": 0.25, "BGK": 0.3},
                tags=["flash", "corte", "cut", "giro", "spin"]),
    ],
)


def _expose(family, keys):
    """The editable settings were #defines: move each variant's value into its parameter defaults, so the cards
    keep exactly the look they were designed with."""
    base = dict(family.defines)
    for k in keys:
        family.defines.pop(k, None)
    for v in family.variants:
        d = {**base, **v.defines}
        for k in keys:
            v.defines.pop(k, None)
        if family is RIG:
            f = 1.0 / d["PERIOD"]
            v.params.update({"blur": d["BLUR"], "frequency": f, "color": d["TINT"]})
            v.defines.update({"WMUL": d["WPER"] / d["PERIOD"], "SHFM": d["SHF"] / f})
        else:
            v.params.update({"frequency": 1.0 / d["CUT"]})
            v.defines["TILT0"] = d["TILT"]


_expose(RIG, ["PERIOD", "WPER", "SHF", "BLUR", "TINT"])
_expose(CARD, ["CUT", "TILT"])

FAMILIES = [RIG, CARD]
