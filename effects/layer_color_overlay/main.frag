#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec3 color; uniform float opacity;
void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    fragColor = vec4(mix(src.rgb, color, clamp(opacity, 0.0, 1.0)), src.a);
}
