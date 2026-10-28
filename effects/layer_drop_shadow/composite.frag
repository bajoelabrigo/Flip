#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform sampler2D u_texture1;
uniform vec3 color; uniform float opacity;
void main() {
    vec4 src = texture(u_texture1, v_texCoord);
    float sa = texture(u_currentTexture, v_texCoord).a * clamp(opacity, 0.0, 1.0);
    // The layer over its shadow (straight alpha).
    float a = src.a + sa * (1.0 - src.a);
    vec3 rgb = a > 1e-5 ? (src.rgb * src.a + color * sa * (1.0 - src.a)) / a : vec3(0.0);
    fragColor = vec4(rgb, a);
}
