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
    // Points the turn brings in from outside the picture are mirrored back in, kept 2 px off the border: the
    // border pixel of a shape or a padded layer is see-through, and clamping to it smeared dark bands across.
    vec2 lo = vec2(2.0), hi = u_resolution - 2.0;
    vec2 span = max(hi - lo, vec2(1.0));
    vec2 m = mod(q - lo, 2.0 * span);
    q = lo + min(m, 2.0 * span - m);
    fragColor = texture(u_currentTexture, q / u_resolution);
}
