#version 330 core
in vec2 v_texCoord;
out vec4 fragColor;
uniform sampler2D u_currentTexture;
uniform float redHue;
uniform float redSat;
uniform float redLum;
uniform float orangeHue;
uniform float orangeSat;
uniform float orangeLum;
uniform float yellowHue;
uniform float yellowSat;
uniform float yellowLum;
uniform float greenHue;
uniform float greenSat;
uniform float greenLum;
uniform float aquaHue;
uniform float aquaSat;
uniform float aquaLum;
uniform float blueHue;
uniform float blueSat;
uniform float blueLum;
uniform float purpleHue;
uniform float purpleSat;
uniform float purpleLum;
uniform float magentaHue;
uniform float magentaSat;
uniform float magentaLum;
vec3 rgb2hsl(vec3 c) {
    float hi = max(c.r, max(c.g, c.b));
    float lo = min(c.r, min(c.g, c.b));
    float l = (hi + lo) * 0.5;
    float d = hi - lo;
    if (d < 1e-5) return vec3(0.0, 0.0, l);
    float s = l > 0.5 ? d / (2.0 - hi - lo) : d / (hi + lo);
    float h;
    if (hi == c.r) h = (c.g - c.b) / d + (c.g < c.b ? 6.0 : 0.0);
    else if (hi == c.g) h = (c.b - c.r) / d + 2.0;
    else h = (c.r - c.g) / d + 4.0;
    return vec3(h * 60.0, s, l);
}
float hue2rgb(float p, float q, float t) {
    t = fract(t);
    if (t < 1.0 / 6.0) return p + (q - p) * 6.0 * t;
    if (t < 0.5) return q;
    if (t < 2.0 / 3.0) return p + (q - p) * (2.0 / 3.0 - t) * 6.0;
    return p;
}
vec3 hsl2rgb(vec3 hsl) {
    if (hsl.y < 1e-5) return vec3(hsl.z);
    float q = hsl.z < 0.5 ? hsl.z * (1.0 + hsl.y) : hsl.z + hsl.y - hsl.z * hsl.y;
    float p = 2.0 * hsl.z - q;
    float h = hsl.x / 360.0;
    return vec3(hue2rgb(p, q, h + 1.0 / 3.0), hue2rgb(p, q, h), hue2rgb(p, q, h - 1.0 / 3.0));
}
// Adds one band's (hue, saturation, lightness) shift, weighted by how close the pixel's hue is.
void band(float h, float centre, vec3 amount, inout vec3 shift, inout float w) {
    float d = abs(mod(h - centre + 180.0, 360.0) - 180.0);
    float k = 1.0 - smoothstep(0.0, 40.0, d);
    shift += amount * k;
    w += k;
}

void main() {
    vec4 src = texture(u_currentTexture, v_texCoord);
    vec3 hsl = rgb2hsl(src.rgb);
    vec3 shift = vec3(0.0);
    float w = 0.0;
    float h = hsl.x;
    band(h, 0.0, vec3(redHue, redSat, redLum), shift, w);
    band(h, 30.0, vec3(orangeHue, orangeSat, orangeLum), shift, w);
    band(h, 60.0, vec3(yellowHue, yellowSat, yellowLum), shift, w);
    band(h, 120.0, vec3(greenHue, greenSat, greenLum), shift, w);
    band(h, 180.0, vec3(aquaHue, aquaSat, aquaLum), shift, w);
    band(h, 225.0, vec3(blueHue, blueSat, blueLum), shift, w);
    band(h, 270.0, vec3(purpleHue, purpleSat, purpleLum), shift, w);
    band(h, 315.0, vec3(magentaHue, magentaSat, magentaLum), shift, w);
    shift /= max(w, 1.0);
    // Greys have no hue: the less colour a pixel has, the less any band touches it.
    float colourful = smoothstep(0.02, 0.25, hsl.y);
    hsl.x = mod(hsl.x + shift.x * 30.0 * colourful, 360.0);
    hsl.y = clamp(hsl.y * (1.0 + shift.y * colourful), 0.0, 1.0);
    hsl.z = clamp(hsl.z + shift.z * 0.25 * colourful * (1.0 - abs(hsl.z * 2.0 - 1.0)), 0.0, 1.0);
    fragColor = vec4(hsl2rgb(hsl), src.a);
}
