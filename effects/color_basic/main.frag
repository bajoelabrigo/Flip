#version 330 core
in vec2 v_texCoord;
out vec4 fragColor;
uniform sampler2D u_currentTexture;
uniform float exposure;
uniform float brightness;
uniform float contrast;
uniform float highlights;
uniform float shadows;
uniform float saturation;
uniform float vibrance;
uniform float temperature;
uniform float tint;
uniform float whites;
uniform float blacks;
uniform float fade;
float luma(vec3 c) { return dot(c, vec3(0.2126, 0.7152, 0.0722)); }

void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    vec3 c = src.rgb;
    c *= exp2(exposure * 1.5);
    c += brightness * 0.25;
    float l = luma(c);
    // Highlights pull the top of the range, shadows lift or crush the bottom.
    float hiW = smoothstep(0.45, 1.0, l);
    float loW = 1.0 - smoothstep(0.0, 0.55, l);
    c += hiW * highlights * 0.35;
    c += loW * shadows * 0.35;
    // Whites and blacks move the ends of the range (a levels white and black point), reaching the
    // brightest and darkest tones that highlights and shadows only lean on.
    float whitePoint = 1.0 - whites * 0.25;
    float blackPoint = -blacks * 0.15;
    c = (c - blackPoint) / max(whitePoint - blackPoint, 0.05);
    c = (c - 0.5) * (1.0 + contrast * (contrast > 0.0 ? 1.0 : 0.7)) + 0.5;
    l = luma(c);
    c = mix(vec3(l), c, 1.0 + saturation);
    // Vibrance boosts the dull colours more than the strong ones.
    float sat = max(c.r, max(c.g, c.b)) - min(c.r, min(c.g, c.b));
    c = mix(vec3(luma(c)), c, 1.0 + vibrance * (1.0 - clamp(sat, 0.0, 1.0)));
    // Fade: the washed-out film look. Blacks lift, the range flattens, colour drains a little.
    c = mix(c, c * 0.82 + 0.12, fade);
    c = mix(vec3(luma(c)), c, 1.0 - 0.25 * fade);
    c += vec3(0.12, 0.03, -0.12) * temperature;
    c += vec3(0.06, -0.10, 0.06) * tint;
    fragColor = vec4(clamp(c, 0.0, 1.0), src.a);
}
