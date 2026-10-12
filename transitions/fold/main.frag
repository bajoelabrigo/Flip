#version 330 core
in vec2 v_texCoord;
out vec4 fragColor;

uniform sampler2D u_currentTexture; // pass input 0
uniform sampler2D u_fromTexture;    // outgoing clip layer
uniform sampler2D u_toTexture;      // incoming clip layer
uniform vec2 u_resolution;
uniform float u_progress;           // 0..1 across the transition window

// Straight-alpha source-over. Clip layers are transparent outside the clip rect.
vec4 over(vec4 top, vec4 bot) {
    float oa = top.a + bot.a * (1.0 - top.a);
    if (oa <= 0.0001) return vec4(0.0);
    vec3 rgb = (top.rgb * top.a + bot.rgb * bot.a * (1.0 - top.a)) / oa;
    return vec4(rgb, oa);
}

float hash21(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float valueNoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float a = hash21(i);
    float b = hash21(i + vec2(1.0, 0.0));
    float c = hash21(i + vec2(0.0, 1.0));
    float d = hash21(i + vec2(1.0, 1.0));
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

uniform float angle;

void main() {
    // A crease travelling left to right, tilted by `angle`. Ahead of it the outgoing clip still
    // lies flat; behind it the incoming one is uncovered, and a narrow flap of the outgoing clip
    // -- mirrored and shaded, like paper seen from behind -- lies folded over just behind the
    // crease. The sweep runs from fully outgoing to fully incoming, flap and tilt included.
    vec2 uv = v_texCoord;
    float band = 0.12;
    float tilt = angle * (uv.y - 0.5);
    float reach = abs(angle) * 0.5 + 0.01;
    float edge = mix(-reach, 1.0 + band + reach, u_progress) + tilt;
    float d = edge - uv.x;              // > 0: the crease has already passed this pixel

    vec4 incoming = texture(u_toTexture, uv);
    vec4 lying = d < 0.0 ? texture(u_fromTexture, uv) : vec4(0.0);

    vec4 flap = vec4(0.0);
    if (d >= 0.0 && d < band) {
        vec2 back = vec2(edge + d, uv.y);
        if (back.x <= 1.0) {
            flap = texture(u_fromTexture, back);
            float t = d / band;
            flap.rgb *= mix(0.9, 0.6, t);
        }
    }

    // A soft highlight on the uncovered side of the crease, and a shadow cast by the flap.
    float glow = 1.0 - smoothstep(0.0, band * 0.6, abs(d - band));
    incoming.rgb = mix(incoming.rgb, vec3(1.0), glow * 0.25 * float(d > band));
    float shadow = 1.0 - smoothstep(band, band * 1.6, d);
    incoming.rgb *= 1.0 - 0.35 * shadow * float(d >= band);

    fragColor = over(flap, over(lying, incoming));
}
