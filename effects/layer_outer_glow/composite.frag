#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform sampler2D u_texture1;
uniform vec3 color; uniform float opacity; uniform float spread;
void main() {
    vec4 src = texture(u_texture1, v_texCoord);
    float g = texture(u_currentTexture, v_texCoord).a;
    // Spread pushes the soft edge out towards a solid one.
    g = clamp(g / max(1.0 - clamp(spread, 0.0, 0.95), 0.05), 0.0, 1.0) * clamp(opacity, 0.0, 1.0);
    float a = src.a + g * (1.0 - src.a);
    vec3 rgb = a > 1e-5 ? (src.rgb * src.a + color * g * (1.0 - src.a)) / a : vec3(0.0);
    fragColor = vec4(rgb, a);
}
