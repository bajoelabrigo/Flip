#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution;
uniform float bend; uniform float start; uniform float end; uniform float vertical;
uniform float u_padX; uniform float u_padY;

// Bend (0.26) as a joint, the way Bendio bends a layer: along its length (x, or y with `vertical`)
// the stretch from Start to End wraps onto a circular arc of `bend` degrees keeping its length;
// before Start it stays where it was, after End it carries on straight, turned by the whole angle.
// An inverse map: for each output pixel, the part drawn on top is tried first (after, arc, before).
void main() {
    vec2 pad = vec2(u_padX, u_padY);
    vec2 inner = max(vec2(1.0) - 2.0 * pad, vec2(1e-4));
    vec2 boxPx = u_resolution * inner;
    bool along = vertical > 0.5;
    vec2 size = along ? boxPx.yx : boxPx;
    vec2 q = ((v_texCoord - pad) / inner) * boxPx;
    if (along)
        q = q.yx;

    float L = size.x;
    float mid = size.y * 0.5;
    float half = size.y * 0.5;
    float s0 = clamp(min(start, end), 0.0, 100.0) / 100.0 * L;
    float s1 = clamp(max(start, end), 0.0, 100.0) / 100.0 * L;
    float theta = radians(bend);
    // A bend the other way is the same one mirrored across the axis.
    float flip = theta < 0.0 ? -1.0 : 1.0;
    float a = abs(theta);
    vec2 src = vec2(-1.0);
    if (a < 1e-4 || s1 - s0 < 1e-3) {
        src = q;
    } else {
        float qd = (q.y - mid) * flip; // offset from the axis, + on the outside of the bend
        float R = (s1 - s0) / a;
        vec2 c = vec2(s0, -R);         // the arc's centre, axis at y = 0
        vec2 qq = vec2(q.x, qd);
        // After End: straight on from the arc's end, turned by the angle.
        vec2 e = c + R * vec2(sin(a), cos(a));
        vec2 t = vec2(cos(a), -sin(a));
        vec2 n = vec2(sin(a), cos(a));
        float u = dot(qq - e, t);
        float d = dot(qq - e, n);
        if (u >= 0.0 && s1 + u <= L && abs(d) <= half) {
            src = vec2(s1 + u, d);
        } else {
            vec2 v = qq - c;
            float r = length(v);
            float ang = atan(v.x, v.y);
            if (ang < 0.0)
                ang += 6.28318530718;
            float dd = r - R;
            if (ang >= 0.0 && ang <= a && abs(dd) <= half) {
                src = vec2(s0 + ang * R, dd);
            } else if (q.x <= s0 && abs(qd) <= half) {
                src = vec2(q.x, qd);
            }
        }
        if (src.x >= 0.0)
            src.y = src.y * flip + mid;
    }
    vec2 uv = src / size;
    if (along)
        uv = uv.yx;
    if (uv.x < 0.0 || uv.y < 0.0 || uv.x > 1.0 || uv.y > 1.0) {
        fragColor = vec4(0.0);
        return;
    }
    fragColor = texture(u_currentTexture, uv * inner + pad);
}
