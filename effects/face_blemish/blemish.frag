#version 330 core
// Blemish Removal, pass 2: on the skin of the tracked face (the oval minus eyes, brows and lips,
// the same mask Face Retouch smooths), a pixel noticeably darker or redder than the skin around it
// (the wide mean of passes 0-1) is a spot, a pimple or the shadow of a fine wrinkle, and is pulled
// to that surrounding skin. The pull eases in with how far it stands out, so pores and fine
// texture, which barely differ from the mean, stay; larger features never reach the mean's scale.
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; // source
uniform sampler2D u_texture1;       // spot_mean
uniform vec2 u_resolution;
uniform float u_faceValid; uniform float u_faceHasContours; uniform float u_faceHasMesh;
uniform vec2 u_faceOval[36];
uniform vec2 u_faceLipOuter[20];
uniform vec2 u_faceEyeLeft[16];
uniform vec2 u_faceEyeRight[16];
uniform vec2 u_faceBrowLeft[10];
uniform vec2 u_faceBrowRight[10];
uniform float u_faceRx;
uniform float spots; uniform float wrinkles;

vec2 toLocal(vec2 uv, float aspect) { return vec2(uv.x, uv.y * aspect); }

#define SD_POLY(NAME, ARR, N)                                                                      \
    float NAME(vec2 p) {                                                                           \
        vec2 d0 = p - ARR[0];                                                                      \
        float d = dot(d0, d0);                                                                     \
        float s = 1.0;                                                                             \
        for (int i = 0, j = N - 1; i < N; j = i, i++) {                                            \
            vec2 e = ARR[j] - ARR[i];                                                              \
            vec2 w = p - ARR[i];                                                                   \
            vec2 b = w - e * clamp(dot(w, e) / dot(e, e), 0.0, 1.0);                               \
            d = min(d, dot(b, b));                                                                 \
            bvec3 c = bvec3(p.y >= ARR[i].y, p.y < ARR[j].y, e.x * w.y > e.y * w.x);               \
            if (all(c) || all(not(c))) s = -s;                                                     \
        }                                                                                          \
        return s * sqrt(d);                                                                        \
    }

SD_POLY(sdOval, u_faceOval, 36)
SD_POLY(sdLips, u_faceLipOuter, 20)
SD_POLY(sdEyeL, u_faceEyeLeft, 16)
SD_POLY(sdEyeR, u_faceEyeRight, 16)
SD_POLY(sdBrowL, u_faceBrowLeft, 10)
SD_POLY(sdBrowR, u_faceBrowRight, 10)

float luma(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }

void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    if (u_faceValid < 0.5 || u_faceHasContours < 0.5 || u_faceHasMesh < 0.5
        || (spots <= 0.0 && wrinkles <= 0.0)) { fragColor = src; return; }

    float aspect = u_resolution.y / u_resolution.x;
    vec2 p = toLocal(v_texCoord, aspect);
    float fw = max(0.05 * u_faceRx, 1e-5);
    float face = 1.0 - smoothstep(-fw, fw * 0.4, sdOval(p));
    if (face <= 0.0) { fragColor = src; return; }
    float featureD = min(min(sdLips(p), min(sdEyeL(p), sdEyeR(p))), min(sdBrowL(p), sdBrowR(p)));
    float guard = max(u_faceRx * 0.06, 1e-5);
    float skin = face * smoothstep(-guard * 0.2, guard, featureD);
    if (skin <= 0.0) { fragColor = src; return; }

    vec3 mean = texture(u_texture1, v_texCoord).rgb;
    float dark = luma(mean) - luma(src.rgb);              // > 0: darker than the skin around
    float red = (src.r - mean.r) - 0.5 * ((src.g - mean.g) + (src.b - mean.b)); // > 0: redder

    // Spots and pimples stand out by 4 % or more; wrinkle shadows are fainter and only darker.
    float spot = smoothstep(0.035, 0.11, max(dark, red * 1.3)) * spots;
    float line = smoothstep(0.012, 0.05, dark) * wrinkles * 0.75;
    float k = clamp(max(spot, line) * skin, 0.0, 1.0);

    // Toward the surrounding skin, keeping a trace of the pixel's own fine detail.
    vec3 healed = mean + (src.rgb - mean) * 0.15;
    fragColor = vec4(mix(src.rgb, healed, k), src.a);
}
