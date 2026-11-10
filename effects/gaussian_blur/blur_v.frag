#version 330 core
in vec2 v_texCoord;
out vec4 fragColor;
uniform sampler2D u_currentTexture;
uniform float u_blurRadius;
uniform vec2 u_resolution;
uniform float u_unitPx;

// Pass 2: the input is already premultiplied by blur_h; un-premultiply on the way out.
// A true Gaussian (sigma = 1.64 x the amount, the strength the old 5-tap kernel had) sampled out to 3 sigma, with
// at most 33 taps a side: past that the taps spread out and linear filtering fills between them. The amount is in
// project pixels (u_unitPx), so a preview and the export blur alike.
vec4 tap(vec2 uv) { return texture(u_currentTexture, uv); }

void main() {
    float unitPx = u_unitPx > 0.0 ? u_unitPx : 1.0;
    float sigma = 1.64 * u_blurRadius * unitPx;
    if (sigma < 0.05) {
        fragColor = texture(u_currentTexture, v_texCoord);
        return;
    }
    vec2 axis = vec2(0.0, 1.0 / u_resolution.y);
    float reach = 3.0 * sigma;
    float stepPx = max(1.0, reach / 33.0);
    int taps = int(ceil(reach / stepPx));
    vec4 result = tap(v_texCoord);
    float wsum = 1.0;
    for (int i = 1; i <= 33; ++i) {
        if (i > taps)
            break;
        float d = float(i) * stepPx;
        float w = exp(-0.5 * d * d / (sigma * sigma));
        result += (tap(v_texCoord + axis * d) + tap(v_texCoord - axis * d)) * w;
        wsum += 2.0 * w;
    }
    result /= wsum;
    fragColor = vec4(result.rgb / max(result.a, 1e-4), result.a);
}
