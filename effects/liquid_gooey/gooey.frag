#version 330 core
// Liquid, pass 2: the blur down, then a soft threshold on the alpha, so drops that touch melt
// into one (the gooey trick), coloured with their own unpremultiplied colour and lit on the rim
// facing up-left, the way a glossy liquid catches the light.
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution;
uniform float goo; uniform float threshold; uniform float shine;

vec4 blurDown(vec2 uv, float radius) {
    if (radius < 0.5)
        return texture(u_currentTexture, uv);
    float sigma = radius / 2.0;
    vec4 sum = vec4(0.0);
    float weights = 0.0;
    const int kTaps = 12;
    for (int i = -kTaps; i <= kTaps; ++i) {
        float y = float(i) * radius / float(kTaps);
        float w = exp(-0.5 * y * y / (sigma * sigma));
        sum += w * texture(u_currentTexture, uv + vec2(0.0, y / u_resolution.y));
        weights += w;
    }
    return sum / weights;
}

void main() {
    float radius = max(goo, 0.0) * u_resolution.y / 1080.0;
    vec4 c = blurDown(v_texCoord, radius);
    float t = clamp(threshold, 0.05, 0.95);
    float soft = 0.06;
    float a = smoothstep(t - soft, t + soft, c.a);
    if (a <= 0.0) {
        fragColor = vec4(0.0);
        return;
    }
    vec3 colour = c.rgb / max(c.a, 1e-4);
    // The rim's slope from the blurred alpha around: its normal, lit from the top left.
    vec2 px = max(vec2(1.5), vec2(radius * 0.35)) / u_resolution;
    float ax = blurDown(v_texCoord + vec2(px.x, 0.0), radius).a - blurDown(v_texCoord - vec2(px.x, 0.0), radius).a;
    float ay = blurDown(v_texCoord + vec2(0.0, px.y), radius).a - blurDown(v_texCoord - vec2(0.0, px.y), radius).a;
    vec3 n = normalize(vec3(-ax, -ay, 0.35));
    vec3 l = normalize(vec3(-0.5, -0.6, 0.6));
    float diffuse = clamp(dot(n, l), 0.0, 1.0);
    float spec = pow(clamp(dot(reflect(-l, n), vec3(0.0, 0.0, 1.0)), 0.0, 1.0), 18.0);
    colour = colour * mix(1.0, 0.75 + 0.45 * diffuse, clamp(shine, 0.0, 1.0)) + vec3(spec * shine * 0.9);
    fragColor = vec4(clamp(colour, 0.0, 1.0) * a, a);
}
