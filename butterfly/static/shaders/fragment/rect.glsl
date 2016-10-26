precision mediump float;
uniform sampler2D u_tile;
uniform vec2 u_tile_size;
uniform vec2 u_click_pos;
varying vec2 v_tile_pos;

//
// FLOAT COMPARE FUNCTIONS
//
bool equals4(vec4 id1, vec4 id2) {
  return all(equal(id1,id2));
}

bool equals3(vec3 id1, vec3 id2) {
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
  vec4 here_id = offset(v_tile_pos, vec2(0));
  vec4 click_id = offset(u_click_pos, vec2(0));
  if(!equals3(vec3(0), here_id.xyz) && !equals3(vec3(0), click_id.xyz)) {
    if(equals4(here_id, click_id)){
      return vec4(1);
    }
  }
  return vec4(0);
}

void main() {
  gl_FragColor = mask();
}