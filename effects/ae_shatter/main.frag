#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution;
uniform float progress; uniform float pieces; uniform float force; uniform float gravity; uniform float originX; uniform float originY;
float h(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
void main() {
    float t = clamp(progress, 0.0, 1.0);
    if (t <= 0.0001) { fragColor = texture(u_currentTexture, v_texCoord); return; }
    float n = floor(clamp(pieces, 3.0, 24.0));
    vec2 aspect = vec2(u_resolution.x / u_resolution.y, 1.0);
    vec2 origin = vec2(originX, originY) / 100.0;
    // Each shard (a cell of an n×n grid) flies out from the origin, falls and turns; the pixel shows
    // the shard whose moved cell covers it. Neighbouring cells are checked so shards can cross.
    vec4 outColor = vec4(0.0);
    for (int cy = 0; cy < 24; ++cy) {
        if (float(cy) >= n) break;
        for (int cx = 0; cx < 24; ++cx) {
            if (float(cx) >= n) break;
            vec2 cell = vec2(float(cx), float(cy));
            vec2 centre = (cell + 0.5) / n;
            vec2 away = (centre - origin) * aspect;
            float len = max(length(away), 0.05);
            float r = h(cell);
            vec2 move = away / len * force * t * (0.6 + r) * 0.8 / aspect + vec2(0.0, gravity * t * t * 0.9);
            float turn = (r - 0.5) * 6.0 * t;
            vec2 local = (v_texCoord - centre - move) * aspect;
            float c = cos(-turn); float s = sin(-turn);
            local = vec2(c * local.x - s * local.y, s * local.x + c * local.y) / aspect;
            vec2 srcUv = centre + local;
            vec2 inCell = srcUv * n - cell;
            if (inCell.x >= 0.0 && inCell.x < 1.0 && inCell.y >= 0.0 && inCell.y < 1.0) {
                vec4 col = texture(u_currentTexture, srcUv);
                col.a *= 1.0 - smoothstep(0.7, 1.0, t);
                if (col.a > outColor.a) outColor = col;
            }
        }
    }
    fragColor = outColor;
}
