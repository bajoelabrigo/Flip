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
    // A hard vertical fold travelling left to right: the outgoing half lifts away and the
    // incoming one is revealed underneath, with a highlight riding the crease.
    float edge = mix(-0.1, 1.1, u_progress);
    vec2 uv = v_texCoord;
    vec4 outgoing = texture(u_fromTexture, uv);
    vec4 incoming = texture(u_toTexture, uv);

    // Inside the folded-back band the outgoing layer is mirrored and darkened, like paper seen
    // from behind.
    float band = 0.12;
    float d = edge - uv.x;
    if (d > 0.0 && d < band) {
        float t = d / band;
        vec2 back = vec2(edge - d, uv.y);
        vec4 behind = texture(u_fromTexture, back);
        outgoing = mix(outgoing, behind * 0.75, 1.0 - t);
    } else if (uv.x > edge) {
        outgoing = vec4(0.0);
    }

    float crease = 1.0 - smoothstep(0.0, band * angle / 0.22, abs(d));
    incoming = mix(incoming, vec4(1.0, 1.0, 1.0, incoming.a), crease * 0.35);
    fragColor = over(incoming, outgoing);
}
