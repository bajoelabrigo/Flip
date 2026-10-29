#version 330 core
// Liquid, pass 1: a Gaussian blur across, on the premultiplied picture.
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution;
uniform float goo;

void main() {
    float radius = max(goo, 0.0) * u_resolution.y / 1080.0;
    if (radius < 0.5) {
        fragColor = texture(u_currentTexture, v_texCoord);
        return;
    }
    float sigma = radius / 2.0;
    vec4 sum = vec4(0.0);
    float weights = 0.0;
    const int kTaps = 12;
    for (int i = -kTaps; i <= kTaps; ++i) {
        float x = float(i) * radius / float(kTaps);
        float w = exp(-0.5 * x * x / (sigma * sigma));
        sum += w * texture(u_currentTexture, v_texCoord + vec2(x / u_resolution.x, 0.0));
        weights += w;
    }
    fragColor = sum / weights;
}
