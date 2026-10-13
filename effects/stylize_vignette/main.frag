#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture;
// Defaults (0.55, 0, 1) draw exactly the old fixed vignette, so older projects look the same.
uniform float amount;
uniform float size;     // how far in from the corners the darkening starts
uniform float softness; // 1: a gentle falloff; 0: a hard edge
void main() {
    vec4 c = texture(u_currentTexture, v_texCoord);
    vec2 p = v_texCoord * 2.0 - 1.0;
    float d = max(dot(p, p) - size, 0.0);
    // The darkening reaches its full 2 x amount over this distance from where it starts.
    float width = mix(0.05, 2.0, clamp(softness, 0.0, 1.0));
    float vig = clamp(1.0 - clamp(d / width, 0.0, 1.0) * 2.0 * amount, 0.0, 1.0);
    fragColor = vec4(c.rgb * vig, c.a);
}
