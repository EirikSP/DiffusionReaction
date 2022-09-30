#version 430

in vec2 vert_tex;

uniform sampler2D Texture;

out vec4 fragColor;



void main(){
    vec4 conc = texture(Texture, vert_tex);
    float diff = (texture(Texture, vert_tex).x - texture(Texture, vert_tex).y + 1)/2;
    fragColor = vec4(vec3(diff), texture(Texture, vert_tex).w);
    //fragColor = texture(Texture, vert_tex);
    fragColor = vec4(conc.x, 0.0, conc.y, conc.w);
}