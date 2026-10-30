#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution;
uniform float zoom; uniform float stretch; uniform float groundWidth; uniform float farWidth;
uniform float shear; uniform float bend; uniform float bulge; uniform float ground;
uniform float u_padX; uniform float u_padY;

// Squash & Stretch (0.26) as an inverse map over the layer's own box (y down), after the zoom. The
// ground edge stays put; heights scale away from it by 1 + stretch; the width goes from
// 1 + groundWidth at the ground to 1 + farWidth at the far edge, swollen by `bulge` halfway; the
// far edge leans by `shear` (straight) and `bend` (curving with the square of the height), in
// fractions of the width. That is the shape a Bezier Warp gives a rubber layer in After Effects.
void main() {
    vec2 pad = vec2(u_padX, u_padY);
    vec2 inner = max(vec2(1.0) - 2.0 * pad, vec2(1e-4));
    vec2 out_uv = (v_texCoord - pad) / inner;
    // Zoom first, about the box's centre (0 = as is, -100 = gone, 100 = twice the size).
    float z = 1.0 + zoom / 100.0;
    if (z <= 0.001) {
        fragColor = vec4(0.0);
        return;
    }
    out_uv = vec2(0.5) + (out_uv - vec2(0.5)) / z;

    float sy = max(0.05, 1.0 + stretch / 100.0);
    float gy = clamp(ground, 0.0, 100.0) / 100.0;
    float y = gy + (out_uv.y - gy) / sy;
    float far = y < gy ? max(gy, 1e-4) : max(1.0 - gy, 1e-4);
    float t = clamp(abs(y - gy) / far, 0.0, 1.0);
    float width = mix(1.0 + groundWidth / 100.0, 1.0 + farWidth / 100.0, t)
                  * (1.0 + (bulge / 100.0) * 4.0 * t * (1.0 - t));
    float lean = (shear / 100.0) * t + (bend / 100.0) * t * t;
    float x = 0.5 + (out_uv.x - 0.5 - lean) / max(1e-3, width);

    vec2 src = vec2(x, y);
    if (src.x < 0.0 || src.y < 0.0 || src.x > 1.0 || src.y > 1.0) {
        fragColor = vec4(0.0);
        return;
    }
    fragColor = texture(u_currentTexture, src * inner + pad);
}
