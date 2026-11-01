#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution;
uniform float completion; uniform float angle; uniform float feather;
uniform float u_padX; uniform float u_padY;

// Linear Wipe (0.29), as After Effects': a straight edge sweeps across the layer's box. The part
// already passed by the edge shows, the rest is hidden; Completion 0 = all shown. Angle 0 uncovers
// from the left edge to the right; Feather is the soft band's width in px.
void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    vec2 pad = vec2(u_padX, u_padY);
    vec2 inner = max(vec2(1.0) - 2.0 * pad, vec2(1e-4));
    vec2 boxPx = u_resolution * inner;
    vec2 q = ((v_texCoord - pad) / inner - 0.5) * boxPx;
    float a = radians(angle);
    vec2 d = vec2(cos(a), sin(a));
    float proj = dot(q, d);
    float halfExt = 0.5 * (abs(d.x) * boxPx.x + abs(d.y) * boxPx.y);
    float f = max(feather, 0.0);
    float shown = 1.0 - clamp(completion, 0.0, 100.0) / 100.0;
    // The edge runs from before the first corner (all hidden) past the last one (all shown).
    float edge = -halfExt - f + (2.0 * halfExt + 2.0 * f) * shown;
    float k = f > 0.0 ? 1.0 - smoothstep(edge - f, edge, proj) : (proj <= edge ? 1.0 : 0.0);
    if (shown >= 1.0)
        k = 1.0;
    fragColor = src * k;
}
