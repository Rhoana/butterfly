precision highp float;
uniform sampler2D u_tile;
uniform vec2 u_tile_size;
varying vec2 v_tile_pos;

//
// calculate the color of sampler at an offset from position
//
vec4 offset(vec2 off) {
  // calculate the color of sampler at an offset from position
  return texture2D(u_tile, v_tile_pos + off*u_tile_size);
}

void main() {
  gl_FragColor = vec4(offset(vec2(0)).xyz,1.);
}