#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution;
uniform float u_bodyValid;
uniform float u_bodyNoseX; uniform float u_bodyNoseY;
uniform float u_bodyShoulderLX; uniform float u_bodyShoulderLY;
uniform float u_bodyShoulderRX; uniform float u_bodyShoulderRY;
uniform float u_bodyHipLX; uniform float u_bodyHipLY;
uniform float u_bodyHipRX; uniform float u_bodyHipRY;
uniform float slim; uniform float waist; uniform float legs; uniform float shoulders; uniform float head;

// Width-normalized space (uv with y scaled by the aspect), so a radius means the same along both
// axes, like the face warps.
vec2 toLocal(vec2 uv, float aspect) { return vec2(uv.x, uv.y * aspect); }
vec2 fromLocal(vec2 q, float aspect) { return vec2(q.x, q.y / aspect); }

// Every warp below is written as an inverse map: given where a pixel lands, where it is read
// from. Each squeezes or stretches across the body's own axis (`across`), inside an ellipse in
// the body's frame, easing to nothing at its edge so the background bends smoothly instead of
// tearing.
vec2 squeeze(vec2 p, vec2 centre, vec2 up, vec2 across, vec2 radii, float amount) {
    vec2 d = p - centre;
    vec2 local = vec2(dot(d, across), dot(d, up));
    float t = length(local / max(radii, vec2(1e-5)));
    if (t >= 1.0) return p;
    float falloff = (1.0 - t * t) * (1.0 - t * t);
    // amount > 0 narrows: the pixel is read from further out.
    local.x *= 1.0 + amount * falloff;
    return centre + across * local.x + up * local.y;
}

void main() {
    if (u_bodyValid < 0.5) { fragColor = texture(u_currentTexture, v_texCoord); return; }
    float aspect = u_resolution.y / u_resolution.x;
    vec2 p = toLocal(v_texCoord, aspect);

    vec2 shL = toLocal(vec2(u_bodyShoulderLX, u_bodyShoulderLY), aspect);
    vec2 shR = toLocal(vec2(u_bodyShoulderRX, u_bodyShoulderRY), aspect);
    vec2 hipL = toLocal(vec2(u_bodyHipLX, u_bodyHipLY), aspect);
    vec2 hipR = toLocal(vec2(u_bodyHipRX, u_bodyHipRY), aspect);
    vec2 nose = toLocal(vec2(u_bodyNoseX, u_bodyNoseY), aspect);
    vec2 shC = 0.5 * (shL + shR);
    vec2 hipC = 0.5 * (hipL + hipR);
    float bodyW = max(length(shL - shR), 0.02);
    float torso = max(length(shC - hipC), 0.03);
    vec2 up = normalize(shC - hipC);          // towards the head, in image space y grows down
    vec2 across = vec2(-up.y, up.x);

    // Head: scaled about a point a little above the nose.
    if (abs(head) > 1e-3) {
        vec2 hc = nose + up * bodyW * 0.12;
        float r = bodyW * 0.62;
        vec2 d = p - hc;
        float t = length(d) / r;
        if (t < 1.0) {
            float falloff = (1.0 - t * t) * (1.0 - t * t);
            p = hc + d / mix(1.0, 1.0 + head * 0.3, falloff);
        }
    }
    // Shoulders: wider (positive) or narrower about the shoulder line.
    p = squeeze(p, shC, up, across, vec2(bodyW * 1.1, torso * 0.35), -shoulders * 0.22);
    // Waist: a third of the way from the hips to the shoulders.
    p = squeeze(p, mix(hipC, shC, 0.32), up, across, vec2(bodyW * 0.95, torso * 0.42), waist * 0.3);
    // Whole body: a tall ellipse from above the head to below the knees.
    p = squeeze(p, mix(hipC, shC, 0.1), up, across, vec2(bodyW * 1.5, torso * 2.6), slim * 0.18);

    vec2 uv = fromLocal(p, aspect);
    // Longer legs: everything below the hips is stretched near the hips and squeezed at the
    // bottom of the frame, which stays put, so nothing slides off the edge.
    float hy = 0.5 * (u_bodyHipLY + u_bodyHipRY);
    if (legs > 1e-3 && hy < 0.98 && uv.y > hy) {
        float t = (uv.y - hy) / (1.0 - hy);
        float a = legs * 0.4;
        uv.y = hy + (1.0 - hy) * (t - a * t * (1.0 - t));
    }
    fragColor = texture(u_currentTexture, clamp(uv, 0.0, 1.0));
}
