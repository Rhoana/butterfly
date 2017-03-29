precision mediump float;
uniform sampler2D u_tile;
uniform vec2 u_tile_size;
uniform vec4 u_click_id;
varying vec2 v_tile_pos;



// rgba to one 32 bit int
int unpack (ivec3 id) {
//  ivec3 id = ivec3(id.xyz*255.);
  return id.x + 256*id.y + 65536*id.z;
}

vec4 hsv2rgb(vec3 c, float a) {
  vec4 K = vec4(1., 2./3., 1./3., 3.);
  vec3 p = abs(fract(c.xxx + K.xyz) * 6. - K.www);
  vec3 done = c.z * mix(K.xxx, clamp(p - K.xxx, 0., 1.), c.y);
  return vec4(done,a);
}

vec3 spike(float id) {
    vec3 star = pow(vec3(3,7,2),vec3(-1)) + pow(vec3(10),vec3(-2,-3,-2));
    vec3 step = fract(id*star);
    step.z = mix(0.2,0.9,step.z);
    step.y = mix(0.6,1.0,step.y);
    return step;
}

vec4 colormap (ivec3 raw) {
  float id = float(unpack(raw));
  vec3 hsv = spike(id);
  return hsv2rgb(hsv,.6);
}


//
// FLOAT COMPARE FUNCTIONS
//
bool equals3(ivec3 id1, ivec3 id2) {
  return all(equal(id1,id2));
}
//
// calculate the color of sampler at an offset from position
//
ivec3 offset(vec2 pos, vec2 off) {
  // calculate the color of sampler at an offset from position
  return ivec3(texture2D(u_tile, pos + off*u_tile_size).xyz*255.);
}

vec4 mask(){
  ivec3 click_id = ivec3(u_click_id.xyz);
  ivec3 here_id = offset(v_tile_pos, vec2(0));
  if(!equals3(ivec3(0), here_id)) {
    if(equals3(here_id, click_id) && !equals3(ivec3(0), click_id)){
      return vec4(vec3(.6),.4);
    }
    // Borders if any corner not shared
    for (int n = 0; n < 4; n++){
        float side = float(n > 1);
        float even = mod(float(n),2.);
        vec2 square = vec2(even,side)*2.-1.;
        ivec3 edge = offset(v_tile_pos, square);
        if(!equals3(here_id, edge)) {
            return vec4(0.,0.,0.,1.);
        }
    }
    return colormap(here_id);
  }
  return vec4(0);
}

void main() {
  gl_FragColor = mask();
}