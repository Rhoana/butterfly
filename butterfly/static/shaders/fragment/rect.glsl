precision mediump float;
uniform sampler2D u_tile;
uniform vec2 u_tile_size;
uniform vec4 u_click_id;
varying vec2 v_tile_pos;

//
// FLOAT COMPARE FUNCTIONS
//
bool equals3(ivec3 id1, ivec3 id2) {
  return all(equal(id1,id2));
}
//
// calculate the color of sampler at an offset from position
//
vec4 offset(vec2 pos, vec2 off) {
  // calculate the color of sampler at an offset from position
  return texture2D(u_tile, pos + off*u_tile_size);
}

vec4 mask(){
  ivec4 click_id = ivec4(u_click_id);
  ivec4 here_id = ivec4(offset(v_tile_pos, vec2(0))*255.);
  if(!equals3(ivec3(0), here_id.xyz) && !equals3(ivec3(0), click_id.xyz)) {
    if(equals3(here_id.xyz, click_id.xyz)){
      return vec4(1);
    }
  }
  return vec4(0);
}

void main() {
  gl_FragColor = mask();
}