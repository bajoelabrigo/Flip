#version 330 core
// Film grain: per-frame noise, strongest in the mid-tones as on film, sized in output pixels so a
// preview and the export at the same size grain alike. Alpha is untouched.
in vec2 v_texCoord;
out vec4 fragColor;
uniform sampler2D u_currentTexture;
uniform vec2 u_resolution;
uniform float u_time;
uniform float amount;
uniform float grainSize;
uniform float colourGrain;

float hash(vec3 p) {
    p = fract(p * vec3(443.897, 441.423, 437.195));
    p += dot(p, p.yxz + 19.19);
    return fract((p.x + p.y) * p.z);
}

void main() {
    vec4 c = texture(u_currentTexture, v_texCoord);
    vec2 cell = floor(v_texCoord * u_resolution / max(grainSize, 1.0));
    float frame = floor(u_time * 24.0);
    float l = dot(c.rgb, vec3(0.2126, 0.7152, 0.0722));
    float midtones = 1.0 - pow(abs(l * 2.0 - 1.0), 2.0);
    float strength = amount * 0.22 * (0.35 + 0.65 * midtones);
    vec3 n = vec3(hash(vec3(cell, frame)));
    if (colourGrain > 0.5)
        n = vec3(n.x, hash(vec3(cell, frame + 17.0)), hash(vec3(cell, frame + 31.0)));
    fragColor = vec4(clamp(c.rgb + (n - 0.5) * strength, 0.0, 1.0), c.a);
}
