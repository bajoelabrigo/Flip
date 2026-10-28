#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution; uniform float u_time; uniform float u_unitPx;
uniform float centerX; uniform float centerY; uniform float frequency; uniform float speed; uniform float width;
uniform vec3 color; uniform float fade;
float unitPx() { return u_unitPx > 0.0 ? u_unitPx : 1.0; }

void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    vec2 c = vec2(centerX, centerY) / 100.0 * u_resolution;
    float d = length(v_texCoord * u_resolution - c) / unitPx();
    float spacing = speed / max(frequency, 0.01);
    float phase = d - u_time * speed;
    float k = mod(phase, spacing);
    float dd = min(k, spacing - k);
    float ring = 1.0 - smoothstep(0.0, max(width, 0.5), dd);
    float born = step(phase, 0.0);
    float a = clamp(ring, 0.0, 1.0) * born * clamp(1.0 - d / fade, 0.0, 1.0);
    float outA = src.a + a * (1.0 - src.a);
    vec3 rgb = outA > 1e-5 ? (src.rgb * src.a + color * a * (1.0 - src.a)) / outA : vec3(0.0);
    fragColor = vec4(mix(rgb, color, a * src.a), outA);
}
