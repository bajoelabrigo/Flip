"""Efectos › Tendencias, camera motion (second half of the CATALOG.md section, from «Sacudida del terremoto» on).

Every family shares one renderer: a pose(t) (centre, zoom, turn, shift, 3D tilt, lens bulge) drawn with a real
shutter (16 poses averaged back in time), so fast moves get their own motion blur. The picture is mirrored past
the edges (Sm) and every pose keeps some zoom, so no border shows. Shockwave and swirl have their own bodies.
"""

from math import degrees

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)
# Shared by every pose family (applied in RENDER): how much closer the camera is (1 = as designed), how long the
# shutter stays open (motion blur), and where the zoom/turn is centred (0..1 of the frame).
ZOOM = Param("zoom", "Zoom", 0.5, 3.0, 1.0)
BLUR = Param("blur", "Blur", 0.0, 3.0, 1.0)
CENTER_X = Param("center_x", "Center X", 0.0, 1.0, 0.5)
CENTER_Y = Param("center_y", "Center Y", 0.0, 1.0, 0.5)
POSE_PARAMS = [INTENSITY, SPEED, ZOOM, BLUR, CENTER_X, CENTER_Y]


def deg(rad: float) -> float:
    """A Rotation default in degrees that gives back exactly the angle the card was designed with."""
    return degrees(rad)

# Pose + shutter renderer. A family body is POSE_HEAD + its pose() + RENDER.
POSE_HEAD = r"""
struct Pose { vec2 c; float k; float a; vec2 off; vec2 tilt; float bulge; };
Pose P0() { Pose q; q.c = vec2(0.5); q.k = 1.0; q.a = 0.0; q.off = vec2(0.0); q.tilt = vec2(0.0); q.bulge = 0.0;
            return q; }
int modeId() { return int(MODE + 0.5); }
"""

RENDER = r"""
vec2 poseUv(vec2 uv, Pose q) {
    vec2 p = (uv - 0.5) * vec2(aspect(), 1.0);
    p *= 1.0 + q.bulge * dot(p, p);
    if (abs(q.tilt.x) + abs(q.tilt.y) > 1e-5) {
        // The picture on a plane turned by yaw (x) and pitch (y), seen by a camera at focal F.
        float F = 1.0;
        float cy = cos(q.tilt.x), sy = sin(q.tilt.x), cp = cos(q.tilt.y), sp = sin(q.tilt.y);
        mat3 ry = mat3(cy, 0.0, -sy, 0.0, 1.0, 0.0, sy, 0.0, cy);
        mat3 rx = mat3(1.0, 0.0, 0.0, 0.0, cp, sp, 0.0, -sp, cp);
        mat3 R = ry * rx;
        vec3 n = R * vec3(0.0, 0.0, 1.0);
        vec3 d = vec3(p, F);
        vec3 o = vec3(0.0, 0.0, F);
        float h = dot(n, o) / max(dot(n, d), 1e-3);
        vec3 l = transpose(R) * (d * h - o);
        p = l.xy;
    }
    return camUv(p / vec2(aspect(), 1.0) + 0.5, q.c, q.k, q.a, q.off);
}
void main() {
    float t = u_time * speed;
    vec4 acc = vec4(0.0);
    float ws = 0.0;
    // 16 poses across the shutter, dithered per pixel so a fast move blurs instead of leaving copies.
    float dj = hash12(gl_FragCoord.xy + fract(u_time * 7.31) * 113.0);
    for (int i = 0; i < 16; ++i) {
        float f = (float(i) + dj) / 16.0;
        float w = exp(-f * TRAIL);
        Pose q = pose(t - SHUTTER * blur * speed * f);
        q.k = 1.0 + zoom * (q.k - 1.0);
        q.c += vec2(center_x, center_y) - 0.5;
        acc += Sm(poseUv(v_texCoord, q)) * w;
        ws += w;
    }
    vec4 col = acc / ws;
    col.rgb *= mix(1.0, vignette(v_texCoord, 0.25, 0.75), VIG);
    fragColor = col;
}
"""

RENDER_DEFAULTS = {"SHUTTER": 0.03, "TRAIL": 0.0, "VIG": 0.0}

# ---------------------------------------------------------------------------------------------- shakes
SHAKE_POSE = r"""
Pose pose(float t) {
    Pose q = P0();
    // frequency = hits per second; the shake itself speeds up or slows down with it.
    float ratio = frequency * BEATP;
    float b = beat(t, 1.0 / max(frequency, 0.05), BEATDEC);
    float env = mix(1.0, b, BEATMIX);
    vec2 n = shake2(t, FREQ * ratio);
    if (OSC > 0.0) n = mix(n, vec2(sin(TAU * t * OSC * ratio * 0.5 + 1.1), sin(TAU * t * OSC * ratio)), 0.8);
    q.off = n * AMP * env * intensity;
    q.a = shake2(t + 7.3, FREQ * ratio * 0.8).x * radians(rotation) * env * intensity;
    q.k = ZOOM + ZPULSE * intensity * wave01(t, ZPER) + KICK * b * intensity;
    return q;
}
"""

SHAKE = Family(
    key="c2_shake", category="camara",
    params=POSE_PARAMS + [Param("rotation", "Rotation", 0.0, 20.0, deg(0.02)),
                          Param("frequency", "Frequency", 0.25, 6.0, 2.0)], photo="fx-skater-01",
    tags=["sacudir", "shake", "temblor", "camara", "camera", "vibrar"],
    defines={"MODE": 0, "FREQ": 8.0, "AMP": (0.02, 0.02), "ZOOM": 1.1, "ZPULSE": 0.0, "ZPER": 0.5,
             "BEATP": 0.5, "BEATDEC": 0.12, "BEATMIX": 0.0, "KICK": 0.0, "OSC": 0.0, **RENDER_DEFAULTS},
    body=POSE_HEAD + SHAKE_POSE + RENDER,
    variants=[
        Variant("sacudida-del-terremoto", "Sacudida del terremoto", "Earthquake shake",
                defines={"FREQ": 13.0, "AMP": (0.04, 0.035), "ZOOM": 1.16, "BEATP": 1.0,
                         "BEATDEC": 0.5, "BEATMIX": 0.35, "SHUTTER": 0.06},
                params={"rotation": deg(0.035), "frequency": 1.0},
                tags=["terremoto", "earthquake", "sismo"], thumb=0.4),
        Variant("movimiento-de-camara-en-mano", "Movimiento de cámara en mano", "Handheld camera",
                defines={"FREQ": 1.4, "AMP": (0.016, 0.012), "ZOOM": 1.08},
                params={"rotation": deg(0.014), "frequency": 2.0},
                tags=["en mano", "handheld", "natural"], thumb=1.5),
        Variant("jitter-rotacional", "Jitter rotacional", "Rotational jitter",
                defines={"FREQ": 9.0, "AMP": (0.01, 0.01), "ZOOM": 1.25, "SHUTTER": 0.07,
                         "BEATP": 0.5, "BEATDEC": 0.25, "BEATMIX": 0.4},
                params={"rotation": deg(0.16), "frequency": 2.0},
                tags=["girar", "rotation", "jitter"], thumb=0.3),
        Variant("sacudida-de-disparo", "Sacudida de disparo", "Recoil shake",
                defines={"FREQ": 20.0, "AMP": (0.03, 0.035), "ZOOM": 1.1, "BEATP": 0.5,
                         "BEATDEC": 0.1, "BEATMIX": 1.0, "KICK": 0.14, "SHUTTER": 0.03},
                params={"rotation": deg(0.03), "frequency": 2.0},
                tags=["disparo", "recoil", "golpe", "hit", "ritmo", "beat"], thumb=1.02),
        Variant("batido-suave", "Batido suave", "Soft shake",
                defines={"FREQ": 4.0, "AMP": (0.012, 0.01), "ZOOM": 1.07},
                params={"rotation": deg(0.01), "frequency": 2.0},
                tags=["suave", "soft"], thumb=1.0),
        Variant("agitar-arriba-y-abajo", "Agitar arriba y abajo", "Shake up and down",
                defines={"FREQ": 10.0, "AMP": (0.004, 0.04), "ZOOM": 1.12, "OSC": 6.0,
                         "SHUTTER": 0.05},
                params={"rotation": deg(0.0), "frequency": 2.0},
                tags=["vertical", "arriba", "abajo", "up", "down"], thumb=0.62),
        Variant("mini-batido", "Mini batido", "Mini shake",
                defines={"FREQ": 18.0, "AMP": (0.008, 0.008), "ZOOM": 1.05, "BEATP": 0.5,
                         "BEATDEC": 0.2, "BEATMIX": 0.6},
                params={"rotation": deg(0.006), "frequency": 2.0},
                tags=["mini", "pequeño", "small"], thumb=1.0),
        Variant("agitar-zoom", "Agitar zoom", "Shake zoom",
                defines={"FREQ": 12.0, "AMP": (0.022, 0.02), "ZOOM": 1.08, "ZPULSE": 0.0,
                         "BEATP": 0.5, "BEATDEC": 0.18, "BEATMIX": 0.7, "KICK": 0.18, "SHUTTER": 0.05},
                params={"rotation": deg(0.015), "frequency": 2.0},
                tags=["zoom", "pulso", "pulse"], thumb=1.03),
        Variant("movimiento-de-la-camara", "Movimiento de la cámara", "Camera movement",
                defines={"FREQ": 0.7, "AMP": (0.035, 0.025), "ZOOM": 1.13, "ZPULSE": 0.04,
                         "ZPER": 3.0},
                params={"rotation": deg(0.025), "frequency": 2.0},
                tags=["deriva", "drift", "lento", "slow"], thumb=1.5),
    ],
)

# ---------------------------------------------------------------------------------------------- zooms & pans
MOVE_POSE = r"""
Pose pose(float t) {
    Pose q = P0();
    float I = intensity;
    float ph = phase(t, PER);
    int m = modeId();
    // direction: 0 right, 1 down, 2 left, 3 up (slides, scrolls, throws, pans, jumps, trails).
    int di = int(mod(floor(direction + 0.5), 4.0));
    vec2 v = di == 0 ? vec2(1.0, 0.0) : di == 1 ? vec2(0.0, 1.0) : di == 2 ? vec2(-1.0, 0.0) : vec2(0.0, -1.0);
    vec2 side = vec2(-v.y, v.x);
    float e = 0.0;           // how far into its move the camera is, for the extra Rotation
    if (m == 1) {            // sliding zoom: closer while sliding sideways, and back
        float s = easeInOut(wave01(t, PER));
        q.k = 1.08 + 0.3 * s * I;
        q.off = 0.06 * s * I * v;
        e = s;
    } else if (m == 2) {     // smooth zoom towards one side
        float s = wave01(t, PER);
        q.k = 1.06 + 0.3 * s * I;
        e = s;
    } else if (m == 3) {     // zoom bounce: a snap in, then a damped spring back
        float z = ph < 0.1 ? easeOut(ph / 0.1) : exp(-(ph - 0.1) * 5.0) * cos((ph - 0.1) * TAU * 2.2);
        q.k = 1.1 + 0.32 * I * max(z, -0.25);
        e = z;
    } else if (m == 4) {     // fast zoom: rushes in, eases back
        float z = ph < 0.22 ? easeIn(ph / 0.22) : 1.0 - easeInOut((ph - 0.22) / 0.78);
        q.k = 1.08 + 0.55 * z * I;
        e = z;
    } else if (m == 5) {     // scroll, then zoom in
        float pan = 1.0 - easeOut(linstep(0.0, 0.35, ph)) + easeInOut(linstep(0.8, 1.0, ph));
        float zz = easeInOut(linstep(0.35, 0.7, ph)) * (1.0 - easeInOut(linstep(0.8, 1.0, ph)));
        q.k = 1.15 + 0.3 * zz * I;
        q.off = 0.06 * pan * I * v;
        e = zz;
    } else if (m == 6) {     // throw: flung up out of frame and back in (two mirrored heights = the same picture)
        float u = linstep(0.15, 0.5, ph);
        q.off = 0.03 * bump(u) * I * side + 2.0 * easeInOut(u) * v;
        e = bump(u);
        q.k = 1.1 + 0.15 * bump(u) * I;
    } else if (m == 7) {     // whip pan sideways
        float u = linstep(0.25, 0.55, ph);
        q.off = 2.0 * easeInOut(u) * v;
        q.k = 1.08 + 0.08 * bump(u) * I;
        e = bump(u);
    } else if (m == 8) {     // jump: up and down, a little bump on landing
        float h = 4.0 * ph * (1.0 - ph);
        float land = beat(t, PER, 0.12);
        q.k = 1.15 + 0.2 * h * I + 0.05 * land * I;
        q.off = (0.1 * h - 0.015 * land) * I * v;
        e = h;
    } else if (m == 9) {     // parallax pulling out: the edges travel faster than the middle
        float s = easeInOut(wave01(t, PER));
        q.k = 1.12 + 0.25 * (1.0 - s) * I;
        q.bulge = -0.12 * (1.0 - s) * I;
        e = 1.0 - s;
    } else {                 // motion trail: a sway that leaves echoes behind
        q.k = 1.12;
        q.off = (0.05 * sin(TAU * ph) * v + 0.015 * sin(2.0 * TAU * ph) * side) * I;
        e = sin(TAU * ph);
    }
    q.a += radians(rotation) * e * I;
    return q;
}
"""

MOVE = Family(
    key="c2_move", category="camara",
    params=POSE_PARAMS + [Param("rotation", "Rotation", -45.0, 45.0, 0.0),
                          Param("direction", "Direction", 0.0, 3.0, 0.0)], photo="fx-skater-01",
    tags=["zoom", "camara", "camera", "movimiento", "motion"],
    defines={"MODE": 1, "PER": 2.0, **RENDER_DEFAULTS},
    body=POSE_HEAD + MOVE_POSE + RENDER,
    variants=[
        Variant("zoom-deslizante", "Zoom deslizante", "Sliding zoom", defines={"MODE": 1, "PER": 2.0},
                photo="fx-skater-03", tags=["deslizar", "slide"], thumb=1.0),
        Variant("zoom-suave-hacia-la-derecha", "Zoom suave hacia la derecha", "Smooth zoom right",
                defines={"MODE": 2, "PER": 2.0}, params={"center_x": 0.72}, tags=["suave", "smooth", "derecha", "right"],
                thumb=1.0),
        Variant("zoom-suave-hacia-la-izquierda", "Zoom suave hacia la izquierda", "Smooth zoom left",
                defines={"MODE": 2, "PER": 2.0}, params={"center_x": 0.28}, tags=["suave", "smooth", "izquierda", "left"],
                photo="fx-skater-03", thumb=1.0),
        Variant("rebote-de-zoom", "Rebote de zoom", "Zoom bounce",
                defines={"MODE": 3, "PER": 1.0, "SHUTTER": 0.05}, tags=["rebote", "bounce"], thumb=1.08),
        Variant("zoom-rapido", "Zoom rápido", "Fast zoom",
                defines={"MODE": 4, "PER": 1.2, "SHUTTER": 0.09}, tags=["rapido", "fast", "punch"], thumb=0.25),
        Variant("desplazar-y-ampliar", "Desplazar y ampliar", "Scroll and zoom",
                defines={"MODE": 5, "PER": 2.0, "SHUTTER": 0.06}, params={"direction": 3.0}, tags=["desplazar", "scroll", "ampliar"],
                thumb=0.15),
        Variant("lanzar", "Lanzar", "Throw",
                defines={"MODE": 6, "PER": 1.5, "SHUTTER": 0.1},
                params={"direction": 3.0, "rotation": deg(0.12)}, tags=["lanzar", "throw", "whip"], thumb=0.5),
        Variant("toma-panoramica-rapida", "Toma panorámica rápida", "Fast pan",
                defines={"MODE": 7, "PER": 1.5, "SHUTTER": 0.1}, tags=["panoramica", "pan", "whip", "barrido"],
                thumb=0.6),
        Variant("saltar", "Saltar", "Jump",
                defines={"MODE": 8, "PER": 0.75, "SHUTTER": 0.05}, params={"direction": 3.0}, tags=["saltar", "jump", "rebote"], thumb=0.3),
        Variant("paralaje-suave-alejar", "Paralaje suave alejar", "Smooth parallax zoom out",
                defines={"MODE": 9, "PER": 3.0}, photo="fx-skater-03",
                tags=["paralaje", "parallax", "alejar", "zoom out"], thumb=1.0),
        Variant("estela-de-movimiento", "Estela de movimiento", "Motion trail",
                defines={"MODE": 10, "PER": 1.2, "SHUTTER": 0.3, "TRAIL": 2.5},
                tags=["estela", "trail", "eco", "echo"], thumb=0.3),
    ],
)

# ---------------------------------------------------------------------------------------------- 3D moves
TILT_POSE = r"""
Pose pose(float t) {
    Pose q = P0();
    float I = intensity;
    float ph = phase(t, PER);
    if (modeId() == 1) {     // the camera swings round to the right, and back
        float s = easeInOut(wave01(t, PER));
        q.tilt = radians(rotation) * s * I * vec2(-1.0, 0.04 / 0.45);
        q.k = 1.15 + 0.3 * s * I;
        q.off = vec2(-0.03 * s * I, 0.0);
    } else {                 // the picture leans round a circle, to the left
        float a = -TAU * ph;
        q.tilt = radians(rotation) * I * vec2(cos(a), sin(a));
        q.k = 1.42;
        q.a = 0.03 * sin(a) * I;
    }
    return q;
}
"""

TILT = Family(
    key="c2_tilt", category="camara",
    params=POSE_PARAMS + [Param("rotation", "Rotation", 0.0, 50.0, deg(0.45))], photo="fx-man-01",
    tags=["3d", "perspectiva", "perspective", "camara", "camera"],
    defines={"MODE": 1, "PER": 2.0, **RENDER_DEFAULTS},
    body=POSE_HEAD + TILT_POSE + RENDER,
    variants=[
        Variant("camara-3d-derecha", "Cámara 3D derecha", "3D camera right",
                defines={"MODE": 1, "PER": 2.5}, tags=["derecha", "right"], thumb=1.25),
        Variant("movimiento-3d-circular-izquierda", "Movimiento 3D circular izquierda", "3D circular move left",
                defines={"MODE": 2, "PER": 2.0}, params={"rotation": deg(0.34)}, tags=["circular", "izquierda", "left"], thumb=0.6),
    ],
)

# ---------------------------------------------------------------------------------------------- turns
SPIN_POSE = r"""
Pose pose(float t) {
    Pose q = P0();
    float I = intensity;
    float ph = phase(t, PER);
    int m = modeId();
    float ang = radians(rotation);
    // Whole turns (spin bounce, 360) take Rotation in turns of 360 degrees, so the loop always lands upright.
    float turns = sign(rotation + 1e-4) * max(1.0, floor(abs(rotation) / 360.0 + 0.5));
    if (m == 1) {            // spin bounce: a whole turn that overshoots and settles
        float u = linstep(0.0, 0.6, ph);
        q.a = TAU * turns * easeOutBack(u);
        q.k = 1.12 + 0.4 * bump(u) * I;
    } else if (m == 2) {     // rotational bounce: a kick that swings and settles
        q.a = ang * I * exp(-ph * 4.5) * sin(ph * TAU * 2.2);
        q.k = 1.18 + 0.08 * I * exp(-ph * 6.0);
    } else if (m == 3) {     // 360: a full turn, pulled out a little while it spins
        float u = linstep(0.1, 0.75, ph);
        q.a = TAU * turns * easeInOut(u);
        q.k = 1.12 + 0.5 * bump(u) * I;
    } else if (m == 4) {     // circling: the frame orbits, through a slightly round lens
        float a = TAU * ph;
        q.off = 0.035 * I * vec2(cos(a), sin(a));
        q.a = ang * sin(a) * I;
        q.k = 1.12;
        q.bulge = 0.18 * I;
    } else {                 // wiper: swings from the bottom, holding at each end
        q.a = ang * I * clamp(1.5 * sin(TAU * ph), -1.0, 1.0);
        q.k = 1.4;
    }
    return q;
}
"""

SPIN = Family(
    key="c2_spin", category="camara",
    params=POSE_PARAMS + [Param("rotation", "Rotation", -720.0, 720.0, 360.0)], photo="fx-skater-01",
    tags=["girar", "spin", "rotar", "rotate", "camara", "camera"],
    defines={"MODE": 1, "PER": 1.5, **RENDER_DEFAULTS},
    body=POSE_HEAD + SPIN_POSE + RENDER,
    variants=[
        Variant("rebote-de-giro", "Rebote de giro", "Spin bounce",
                defines={"MODE": 1, "PER": 1.5, "SHUTTER": 0.08}, tags=["rebote", "bounce"], thumb=0.3),
        Variant("rebote-rotacional", "Rebote rotacional", "Rotational bounce",
                defines={"MODE": 2, "PER": 1.0, "SHUTTER": 0.06}, params={"rotation": deg(0.3)}, tags=["rebote", "bounce", "inclinar"],
                thumb=0.12),
        Variant("movimiento-de-camara-360-1", "Movimiento de cámara 360° 1", "360° camera move 1",
                defines={"MODE": 3, "PER": 2.0, "SHUTTER": 0.1}, params={"rotation": -360.0}, tags=["360", "vuelta", "turn"], thumb=0.85),
        Variant("girar-en-circulos", "Girar en círculos", "Spin in circles",
                defines={"MODE": 4, "PER": 1.0, "SHUTTER": 0.05, "VIG": 0.6},
                params={"rotation": deg(0.035)}, tags=["circulos", "circles", "orbita"],
                thumb=0.4),
        Variant("limpiaparabrisas", "Limpiaparabrisas", "Wiper",
                defines={"MODE": 5, "PER": 1.2, "SHUTTER": 0.06},
                params={"rotation": deg(0.18), "center_y": 0.55}, tags=["limpiaparabrisas", "wiper", "pendulo"],
                thumb=0.3),
    ],
)

# ---------------------------------------------------------------------------------------------- swirl
SWIRL = Family(
    key="c2_swirl", category="camara",
    params=[INTENSITY, SPEED, Param("amount", "Amount", 0.0, 3.0, 1.0), Param("size", "Size", 0.2, 1.5, 0.75),
            BLUR, CENTER_X, CENTER_Y], photo="cyber",
    tags=["remolino", "swirl", "torcer", "twist", "distorsion"],
    defines={"PER": 2.0},
    body=r"""
void main() {
    float t = u_time * speed;
    float amt = 2.6 * amount * intensity * sin(TAU * phase(t, PER));
    vec2 c = vec2(center_x, center_y);
    vec2 p = (v_texCoord - c) * vec2(aspect(), 1.0) / 1.06;
    float r = length(p);
    float fall = 1.0 - smoothstep(0.0, size, r);
    fall *= fall;
    vec4 acc = vec4(0.0);
    for (int i = 0; i < 10; ++i) {
        float a = amt * fall * (1.0 - 0.025 * blur * float(i));
        acc += Sm((rot(a) * p) / vec2(aspect(), 1.0) + c);
    }
    fragColor = acc / 10.0;
}
""",
    variants=[
        Variant("remolino-distorsionado", "Remolino distorsionado", "Distorted swirl", thumb=0.5),
    ],
)

# ---------------------------------------------------------------------------------------------- shockwave
SHOCK = Family(
    key="c2_shock", category="camara",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#cfe8ff"),
            Param("frequency", "Frequency", 0.25, 4.0, 1.0), Param("size", "Size", 0.2, 2.0, 0.95),
            Param("width", "Width", 0.3, 3.0, 1.0), Param("amount", "Amount", 0.0, 3.0, 1.0),
            Param("glow", "Glow", 0.0, 3.0, 1.0), CENTER_X, Param("center_y", "Center Y", 0.0, 1.0, 0.52)],
    photo="fx-skater-01",
    tags=["onda", "shockwave", "choque", "anillo", "ring", "impacto"],
    defines={"FLAT": 2.2},
    body=r"""
void main() {
    float t = u_time * speed;
    float per = 1.0 / max(frequency, 0.05);
    float ph = phase(t, per);
    float b = beat(t, per, 0.12);
    // A small jolt on each hit.
    vec2 uv = camUv(v_texCoord, vec2(0.5), 1.05 + 0.03 * b * intensity, 0.0, shake2(t, 18.0) * 0.008 * b * intensity);
    vec2 p = (uv - vec2(center_x, center_y)) * vec2(aspect(), 1.0);
    vec2 q = p * vec2(1.0, FLAT);
    float r0 = easeOut(ph) * size;
    float d = length(q) - r0;
    float w = (0.035 + 0.05 * ph) * width;
    float fade = 1.0 - easeIn(ph);
    float prof = exp(-d * d / (w * w)) * fade * intensity;
    vec2 dir = normalize(q + 1e-5) / vec2(1.0, FLAT);
    vec2 shift = dir * 0.045 * amount * prof * sign(-d) / vec2(aspect(), 1.0);
    vec4 col;
    col.r = Sm(uv + shift * 1.15).r;
    col.g = Sm(uv + shift).g;
    col.b = Sm(uv + shift * 0.85).b;
    col.a = Sm(uv).a;
    float rim = exp(-d * d / (w * w * 0.12)) * fade * intensity;
    col.rgb = addLight(col.rgb, color, (0.55 * prof + 0.5 * rim) * glow);
    fragColor = col;
}
""",
    variants=[
        Variant("onda-de-choque-3", "Onda de choque 3", "Shockwave 3", thumb=0.35),
    ],
)

FAMILIES = [SHAKE, MOVE, TILT, SPIN, SWIRL, SHOCK]
