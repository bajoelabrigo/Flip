#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution; uniform float u_unitPx;
uniform float size;
float unitPx() { return u_unitPx > 0.0 ? u_unitPx : 1.0; }

void main() {
    float radius = max(0.0, size) * unitPx();
    vec2 shift = vec2(0.0);
    vec2 dir = vec2(0.0, 1.0) / u_resolution;
    // A Gaussian over up to 65 taps, spread to cover any radius.
    float stepPx = max(1.0, radius / 32.0);
    float sigma = max(radius * 0.5, 0.001);
    float sum = 0.0;
    float wsum = 0.0;
    for (int k = -32; k <= 32; ++k) {
        float d = float(k) * stepPx;
        if (abs(d) > radius + 0.5 && k != 0) continue;
        float w = radius < 0.5 ? 1.0 : exp(-0.5 * (d * d) / (sigma * sigma));
        sum += texture(u_currentTexture, v_texCoord - shift + dir * d).a * w;
        wsum += w;
    }
    fragColor = vec4(0.0, 0.0, 0.0, sum / max(wsum, 1e-5));
}
