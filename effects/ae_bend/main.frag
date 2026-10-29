#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution;
uniform float bend; uniform float vertical; uniform float pivot;
uniform float u_padX; uniform float u_padY;

// Bend (0.26) as an inverse map: the layer's middle line wraps onto a circular arc of `bend`
// degrees, keeping its length; the point at `pivot` along it stays where it was. Positive bends the
// ends up (an arch), negative down. Along the height, the same with the axes swapped.
void main() {
    vec2 pad = vec2(u_padX, u_padY);
    vec2 inner = max(vec2(1.0) - 2.0 * pad, vec2(1e-4));
    vec2 boxPx = u_resolution * inner;
    // The box in px, y down; swapped when bending along the height.
    bool along = vertical > 0.5;
    vec2 size = along ? boxPx.yx : boxPx;
    vec2 p = ((v_texCoord - pad) / inner) * boxPx;
    if (along)
        p = p.yx;
    float theta = radians(clamp(bend, -360.0, 360.0));
    vec2 src = p;
    if (abs(theta) > 1e-4) {
        float L = size.x;
        float R = L / abs(theta);
        float px = clamp(pivot, 0.0, 100.0) / 100.0 * L;
        float mid = size.y * 0.5;
        // Arching up puts the centre below the middle line; down, above (mirrored).
        float s = theta > 0.0 ? 1.0 : -1.0;
        vec2 c = vec2(px, mid + s * R);
        vec2 d = p - c;
        float phi = atan(d.x, -s * d.y);
        float r = length(d);
        src = vec2(px + phi * R, mid - s * (r - R));
    }
    if (along)
        src = src.yx;
    vec2 uv = src / boxPx;
    if (uv.x < 0.0 || uv.y < 0.0 || uv.x > 1.0 || uv.y > 1.0) {
        fragColor = vec4(0.0);
        return;
    }
    fragColor = texture(u_currentTexture, uv * inner + pad);
}
