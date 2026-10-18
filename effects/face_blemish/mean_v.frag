#version 330 core
// Blemish Removal, pass 1: vertical half of the box mean. See mean_h.frag.
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture; // spot_h
uniform vec2 u_resolution;
uniform float u_faceValid; uniform float u_faceHasContours; uniform float u_faceHasMesh;
uniform float u_faceRx;

void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    if (u_faceValid < 0.5 || u_faceHasContours < 0.5 || u_faceHasMesh < 0.5) { fragColor = src; return; }
    float aspect = u_resolution.x / u_resolution.y;
    vec2 step = vec2(0.0, u_faceRx * 0.012 * aspect);
    vec3 sum = src.rgb;
    for (int i = 1; i <= 4; ++i)
        sum += texture(u_currentTexture, v_texCoord + step * float(i)).rgb
             + texture(u_currentTexture, v_texCoord - step * float(i)).rgb;
    fragColor = vec4(sum / 9.0, src.a);
}
