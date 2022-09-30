#version 430

uniform sampler2D Texture;

out vec3 outVert;
 

uniform float f = 0.05;
uniform float k = 0.062;
float dA = 1.0;
float dB = 0.50;
float dt = 1.0/1.0;


vec4 tex(int x, int y){
    ivec2 tSize = textureSize(Texture, 0).xy;
    return texelFetch(Texture, ivec2((x + tSize.x) % tSize.x, (y + tSize.y) % tSize.y), 0);
}

vec2 averageHood(int x, int y){
    vec2 cell = vec2(tex(x,y).r, tex(x,y).g);
    vec2 hood = vec2(0.0, 0.0);

    hood += 0.2*vec2(tex(x + 1,y + 0).r, tex(x + 1,y + 0).g);
    hood += 0.05*vec2(tex(x + 1,y + 1).r, tex(x + 1,y + 1).g);
    hood += 0.2*vec2(tex(x + 0,y + 1).r, tex(x + 0,y + 1).g);
    hood += 0.2*vec2(tex(x - 1,y + 0).r, tex(x - 1,y + 0).g);
    hood += 0.2*vec2(tex(x + 0,y - 1).r, tex(x + 0,y - 1).g);
    hood += 0.05*vec2(tex(x - 1,y - 1).r, tex(x - 1,y - 1).g);
    hood += 0.05*vec2(tex(x + 1,y - 1).r, tex(x + 1,y - 1).g);
    hood += 0.05*vec2(tex(x - 1,y + 1).r, tex(x - 1,y + 1).g);
    hood -= cell;

    return hood;
}

vec2 nextState(int x, int y){
    float F = f;
    float K = k;
    float A = tex(x,y).r;
    float B = tex(x,y).g;
    float nextA = A + (dA*averageHood(x, y).x - 1*A*B*B + f*(1-A))*dt;
    float nextB = B + (dB*averageHood(x, y).y + 1*A*B*B - B*(k+f))*dt; 

    return vec2(nextA, nextB);

}

void main(){

    int width = textureSize(Texture, 0).x;
    int height = textureSize(Texture, 0).y;
    ivec2 in_text = ivec2(gl_VertexID % width, gl_VertexID / width);

    vec2 nextS = nextState(in_text.x,in_text.y);

    float x = in_text.x;
    float y = in_text.y;
    
    outVert = vec3(nextS, 0.0);
    
}

// Dots, size fluctuating
//float f = 0.025;
//float k = 0.060;