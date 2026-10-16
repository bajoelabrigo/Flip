#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture;
uniform vec3 shade; uniform float strength; uniform float lift;

float luma(vec3 c) { return dot(c, vec3(0.2126, 0.7152, 0.0722)); }

// The luminance-matched recolour of lipstick and eye colour: every strand and highlight keeps its
// own brightness and only hue and saturation move. Dark hair dyed a light shade would stay dark,
// so `lift` raises the luminance first, more the lighter the shade is.
void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    float L = luma(src.rgb);
    float target = luma(shade);
    float gamma = mix(1.0, 0.45, clamp(lift * target * 1.6, 0.0, 1.0));
    float L2 = pow(max(L, 0.0), gamma);
    vec3 dyed = clamp(shade * (L2 / max(target, 1e-3)), 0.0, 1.0);
    fragColor = vec4(mix(src.rgb, dyed, strength), src.a);
}
