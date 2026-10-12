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

// Both layers slide the same way across the frame. Whatever leaves the canvas is simply not
// drawn, so the project background fills the gap behind them -- which is what a slide should do.
vec4 sampleShifted(sampler2D tex, vec2 uv, vec2 shift) {
    vec2 src = uv + shift;
    if (src.x < 0.0 || src.x > 1.0 || src.y < 0.0 || src.y > 1.0)
        return vec4(0.0);
    return texture(tex, src);
}

void main() {
    // +x moves right; y is flipped because texture rows run top-down.
    vec2 dir = vec2(1.0, 0.0);
    vec2 shift = dir * u_progress;
    vec4 outgoing = sampleShifted(u_fromTexture, v_texCoord, shift);
    vec4 incoming = sampleShifted(u_toTexture, v_texCoord, shift - dir);
    fragColor = over(incoming, outgoing);
}
