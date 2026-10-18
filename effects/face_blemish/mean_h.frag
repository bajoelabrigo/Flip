#version 330 core
// Blemish Removal, pass 0: horizontal half of a wide box mean of the skin, about 6 % of the face's
// half-width across, so a pimple or a spot is smaller than the window and averages away.
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture;
uniform float u_faceValid; uniform float u_faceHasContours; uniform float u_faceHasMesh;
uniform float u_faceRx;

void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    if (u_faceValid < 0.5 || u_faceHasContours < 0.5 || u_faceHasMesh < 0.5) { fragColor = src; return; }
    vec2 step = vec2(u_faceRx * 0.012, 0.0);
    vec3 sum = src.rgb;
    for (int i = 1; i <= 4; ++i)
        sum += texture(u_currentTexture, v_texCoord + step * float(i)).rgb
             + texture(u_currentTexture, v_texCoord - step * float(i)).rgb;
    fragColor = vec4(sum / 9.0, src.a);
}
