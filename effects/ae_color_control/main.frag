#version 330 core
in vec2 v_texCoord; out vec4 fragColor;
uniform sampler2D u_currentTexture;
// An Expression Control holds a value for expressions to read: the picture goes through untouched.
void main() { fragColor = texture(u_currentTexture, v_texCoord); }
