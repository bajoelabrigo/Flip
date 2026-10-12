#version 330 core
in vec2 v_texCoord;
out vec4 fragColor;
uniform sampler2D u_currentTexture;
uniform float intensity;
uniform float shadowsR;
uniform float shadowsG;
uniform float shadowsB;
uniform float midtonesR;
uniform float midtonesG;
uniform float midtonesB;
uniform float highlightsR;
uniform float highlightsG;
uniform float highlightsB;
uniform float offsetR;
uniform float offsetG;
uniform float offsetB;
void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    vec3 c = src.rgb;
    vec3 lift = vec3(shadowsR, shadowsG, shadowsB) * 0.25 * intensity;
    vec3 gamma = vec3(midtonesR, midtonesG, midtonesB) * 0.5 * intensity;
    vec3 gain = vec3(highlightsR, highlightsG, highlightsB) * 0.4 * intensity;
    vec3 offs = vec3(offsetR, offsetG, offsetB) * 0.15 * intensity;
    c = c + lift * (1.0 - c);
    c = c * (1.0 + gain);
    c = pow(max(c, vec3(0.0)), 1.0 / max(vec3(0.05), 1.0 + gamma));
    c += offs;
    fragColor = vec4(clamp(c, 0.0, 1.0), src.a);
}
