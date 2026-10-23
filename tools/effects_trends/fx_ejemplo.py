"""The three first effects, written to try the whole pipeline: a particle overlay, a camera move and a frame.
They are also the model for the other fx_*.py modules (one family = one shader body, many variants)."""

from kit import Family, Param, Variant

INTENSITY = Param("intensity", "Intensity", 0.0, 1.5, 1.0)
SPEED = Param("speed", "Speed", 0.2, 3.0, 1.0)

# Falling particles in three depth layers: near ones big, blurred and fast, far ones small and slow.
SNOW = Family(
    key="ej_snow", category="particulas",
    params=[INTENSITY, SPEED, Param("density", "Density", 0.2, 2.0, 1.0), Param("size", "Size", 0.3, 2.5, 1.0),
            Param("color", "Colour", default="#ffffff"), Param("angle", "Angle", -1.0, 1.0, 0.15)],
    photo="lighthouse", tags=["nieve", "snow", "invierno", "winter", "copos"],
    defines={},
    body=r"""
float flakes(vec2 p, float t, float scale, float fall, float seed) {
    p *= scale;
    p.y -= t * fall;
    p.x += sin(p.y * 0.7 + seed) * 0.35 + t * angle * fall;
    vec2 cell = floor(p), f = fract(p) - 0.5;
    float h = hash12(cell + seed);
    if (h > 0.35 * density) return 0.0;
    vec2 o = (hash22(cell + seed * 1.7) - 0.5) * 0.6;
    float r = (0.06 + 0.1 * hash12(cell + 9.1 + seed)) * size;
    return smoothstep(r, r * 0.25, length(f - o));
}
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    float t = u_time * speed;
    float s = flakes(p, t, 7.0, 1.2, 1.0) * 0.55 + flakes(p, t, 4.5, 1.8, 7.0) * 0.8 + flakes(p, t, 2.6, 2.6, 13.0);
    vec3 col = mix(src.rgb, color, sat(s * intensity));
    fragColor = vec4(col, src.a);
}
""",
    variants=[
        Variant("nieve-realista", "Nieve realista", "Realistic snow", thumb=1.2),
    ],
)

# A handheld camera that shakes: smooth noise for the drift, a slight zoom so no border shows.
SHAKE = Family(
    key="ej_shake", category="camara",
    params=[INTENSITY, SPEED, Param("zoom", "Zoom", 1.0, 1.4, 1.08), Param("rotation", "Rotation", 0.0, 2.0, 0.6)],
    photo="skater",
    tags=["sacudir", "shake", "camara", "camera", "temblor"],
    defines={},
    body=r"""
void main() {
    float t = u_time * speed;
    vec2 n = shake2(t, 9.0) * 0.025 * intensity;
    float a = shake2(t + 5.0, 7.0).x * 0.03 * rotation * intensity;
    fragColor = cam(v_texCoord, vec2(0.5), zoom, a, n);
}
""",
    variants=[
        Variant("agite-la-camara", "Agite la cámara", "Shake the camera", thumb=0.6),
    ],
)

# A neon frame inside the edge of the picture, breathing and with light running around it.
NEON_FRAME = Family(
    key="ej_neon_frame", category="marcos",
    params=[INTENSITY, SPEED, Param("color", "Colour", default="#1e8bff"), Param("width", "Width", 0.2, 3.0, 1.0)],
    photo="dark", tags=["neon", "borde", "border", "marco", "frame", "brillo"],
    defines={"INSET": 0.03},
    body=r"""
void main() {
    vec4 src = S(v_texCoord);
    vec2 p = toP(v_texCoord);
    vec2 half_ = vec2(aspect() * 0.5, 0.5) - INSET;
    float d = sdRoundBox(p, half_, 0.03);
    float w = 0.004 * width;
    float breath = 0.8 + 0.2 * sin(u_time * speed * 3.0);
    float g = glowSd(d, w, 0.02 * width) * breath;
    // A brighter spark that runs around the frame.
    float ang = atan(p.y, p.x / aspect());
    float run = pow(0.5 + 0.5 * cos(ang - u_time * speed * 2.5), 12.0);
    vec3 light = color * g * (1.0 + 1.5 * run) + vec3(1.0) * smoothstep(w, 0.0, abs(d)) * 0.6;
    fragColor = vec4(addLight(src.rgb, light, intensity), src.a);
}
""",
    variants=[
        Variant("borde-azul-neon", "Borde azul neón", "Blue neon border", thumb=1.0),
    ],
)

FAMILIES = [SNOW, SHAKE, NEON_FRAME]
