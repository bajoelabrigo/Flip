#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; uniform vec2 u_resolution; uniform float u_time; uniform float u_unitPx;
uniform float birthRate; uniform float lifespan; uniform float emitterX; uniform float emitterY; uniform float velocity;
uniform float gravity; uniform float particleSize; uniform vec3 color; uniform float spread; uniform float direction;
float unitPx() { return u_unitPx > 0.0 ? u_unitPx : 1.0; }

float h1(float n) { return fract(sin(n * 127.1) * 43758.5453); }
void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    vec2 p = v_texCoord * u_resolution / unitPx();
    vec2 emitter = vec2(emitterX, emitterY) / 100.0 * u_resolution / unitPx();
    float rate = max(birthRate, 0.1);
    float life = max(lifespan, 0.05);
    int count = int(min(rate * life, 240.0));
    float firstBorn = floor((u_time - life) * rate);
    float a = 0.0;
    for (int i = 0; i < 240; ++i) {
        if (i >= count) break;
        float id = firstBorn + float(i) + 1.0;
        float born = id / rate;
        float age = u_time - born;
        if (age < 0.0 || age > life || born < 0.0) continue;
        float ang = radians(-direction + (h1(id) - 0.5) * spread);
        float sp = velocity * (0.6 + 0.8 * h1(id + 7.0));
        vec2 v = vec2(cos(ang), sin(ang)) * sp;
        vec2 pos = emitter + v * age + vec2(0.0, 0.5 * gravity * age * age);
        float r = particleSize * (0.6 + 0.8 * h1(id + 3.0));
        float fadeOut = 1.0 - age / life;
        a = max(a, smoothstep(r, r * 0.4, length(p - pos)) * fadeOut);
    }
    float outA = src.a + a * (1.0 - src.a);
    vec3 rgb = outA > 1e-5 ? (src.rgb * src.a * (1.0 - a) + color * a) / outA : vec3(0.0);
    fragColor = vec4(rgb, outA);
}
