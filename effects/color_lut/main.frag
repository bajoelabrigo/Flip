#version 330 core
// A .cube LUT (see drift::CubeLut). The engine uploads the table to u_texture1: a 3D table as
// size slices of size x size side by side (blue picks the slice, red runs along x, green along y),
// a 1D table as one row. The picture is read as the LUT expects it, in the clip's own (display,
// gamma-encoded) values; the input is mapped through DOMAIN_MIN..DOMAIN_MAX and clamped.
// Intensity mixes the result with the untouched colour in that same space; alpha is not touched.
in vec2 v_texCoord;
out vec4 fragColor;
uniform sampler2D u_currentTexture;
uniform sampler2D u_texture1;
uniform float intensity;
uniform float u_lutReady;
uniform float u_lutSize;
uniform float u_lut3d;
uniform vec3 u_lutDomainMin;
uniform vec3 u_lutDomainMax;

vec3 lut3d(vec3 p) {
    float n = u_lutSize;
    // Texel centres: the hardware filters red and green inside a slice without bleeding into the
    // next slice; blue is mixed by hand between the two nearest slices.
    float b = p.b * (n - 1.0);
    float b0 = floor(b);
    float b1 = min(b0 + 1.0, n - 1.0);
    float t = b - b0;
    float x = p.r * (n - 1.0) + 0.5;
    float y = (p.g * (n - 1.0) + 0.5) / n;
    vec3 c0 = texture(u_texture1, vec2((b0 * n + x) / (n * n), y)).rgb;
    vec3 c1 = texture(u_texture1, vec2((b1 * n + x) / (n * n), y)).rgb;
    return mix(c0, c1, t);
}

vec3 lut1d(vec3 p) {
    float n = u_lutSize;
    vec3 u = (p * (n - 1.0) + 0.5) / n;
    return vec3(texture(u_texture1, vec2(u.r, 0.5)).r,
                texture(u_texture1, vec2(u.g, 0.5)).g,
                texture(u_texture1, vec2(u.b, 0.5)).b);
}

void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    if (u_lutReady < 0.5 || u_lutSize < 2.0) {
        fragColor = src;
        return;
    }
    vec3 p = clamp((src.rgb - u_lutDomainMin) / max(u_lutDomainMax - u_lutDomainMin, vec3(1e-6)), 0.0, 1.0);
    vec3 graded = u_lut3d > 0.5 ? lut3d(p) : lut1d(p);
    fragColor = vec4(clamp(mix(src.rgb, graded, clamp(intensity, 0.0, 1.0)), 0.0, 1.0), src.a);
}
