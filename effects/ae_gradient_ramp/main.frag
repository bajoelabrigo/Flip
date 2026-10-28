#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution;
uniform float startX; uniform float startY; uniform vec3 startColor; uniform float endX; uniform float endY;
uniform vec3 endColor; uniform float radial; uniform float blend;
void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    vec2 a = vec2(startX, startY) / 100.0 * u_resolution;
    vec2 b = vec2(endX, endY) / 100.0 * u_resolution;
    vec2 p = v_texCoord * u_resolution;
    float t;
    if (radial > 0.5) t = length(p - a) / max(length(b - a), 1.0);
    else { vec2 ab = b - a; t = dot(p - a, ab) / max(dot(ab, ab), 1.0); }
    vec3 g = mix(startColor, endColor, clamp(t, 0.0, 1.0));
    fragColor = vec4(mix(g, src.rgb, clamp(blend, 0.0, 1.0)), mix(1.0, src.a, clamp(blend, 0.0, 1.0)));
}
