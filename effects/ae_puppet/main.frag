#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution;
uniform float pins; uniform float stiffness;
uniform vec2 pin1; uniform vec2 move1;
uniform vec2 pin2; uniform vec2 move2;
uniform vec2 pin3; uniform vec2 move3;
uniform vec2 pin4; uniform vec2 move4;
uniform vec2 pin5; uniform vec2 move5;
uniform vec2 pin6; uniform vec2 move6;
uniform vec2 pin7; uniform vec2 move7;
uniform vec2 pin8; uniform vec2 move8;

// After Effects' Puppet pins as an inverse map: a pixel is read from where it was before the pins
// moved, by the pins' moves weighted by how near their new places are (inverse distance, sharper
// with stiffness). A pin that stays put holds the picture around it.
void main() {
    int n = int(clamp(pins, 0.0, 8.0) + 0.5);
    if (n == 0) {
        fragColor = texture(u_currentTexture, v_texCoord);
        return;
    }
    vec2 P[8];
    vec2 M[8];
    P[0] = pin1; M[0] = move1;
    P[1] = pin2; M[1] = move2;
    P[2] = pin3; M[2] = move3;
    P[3] = pin4; M[3] = move4;
    P[4] = pin5; M[4] = move5;
    P[5] = pin6; M[5] = move6;
    P[6] = pin7; M[6] = move7;
    P[7] = pin8; M[7] = move8;
    vec2 aspect = vec2(u_resolution.x / max(u_resolution.y, 1.0), 1.0);
    vec2 uv = v_texCoord;
    vec2 sum = vec2(0.0);
    float weights = 0.0;
    float power = 1.0 + clamp(stiffness, 0.0, 3.0);
    for (int i = 0; i < 8; ++i) {
        if (i >= n)
            break;
        vec2 at = (P[i] + M[i]) / 100.0;
        vec2 delta = (uv - at) * aspect;
        float w = 1.0 / pow(dot(delta, delta) + 1e-5, power);
        sum += w * M[i] / 100.0;
        weights += w;
    }
    vec2 src = uv - sum / max(weights, 1e-9);
    if (src.x < 0.0 || src.y < 0.0 || src.x > 1.0 || src.y > 1.0) {
        fragColor = vec4(0.0);
        return;
    }
    fragColor = texture(u_currentTexture, src);
}
