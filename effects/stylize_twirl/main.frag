#version 330 core
// After Effects' Twirl (2026-11-08, for the spiral backgrounds of the YouTube packs): the picture turns round a
// centre by `angle` degrees at the centre, easing to no turn at `radius` (a fraction of the half diagonal).
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution;
uniform float angle; uniform float radius; uniform float centerX; uniform float centerY;
void main() {
    vec2 c = vec2(centerX, centerY) * u_resolution;
    vec2 p = v_texCoord * u_resolution - c;
    float r = max(radius * length(0.5 * u_resolution), 1.0);
    float d = length(p);
    float t = clamp(1.0 - d / r, 0.0, 1.0);
    float a = radians(angle) * t * t;
    float s = sin(a), co = cos(a);
    vec2 q = vec2(co * p.x - s * p.y, s * p.x + co * p.y) + c;
    fragColor = texture(u_currentTexture, clamp(q / u_resolution, 0.0, 1.0));
}
