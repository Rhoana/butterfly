window.API = {};
window.DOJO = {};
//-----------------------------------
//
// http://<host>:<port>/index.html
// New window.DOJO.Setup
// -- Called first
//-----------------------------------

window.onload = function(e){
  window.API.setup = new window.DOJO.Setup(window.API);
};

// Change any preset terms set in input address
window.API.parse = function(input) {
  var output = {};
  var string = decodeURI(input);
  // read value pair as bool, string, or int
  string.split("&").map(function(pair) {
    var key = pair.split("=")[0];
    var val = pair.split("=")[1];
    switch (!val*2 + !Number(val)) {
      case 0: return output[key] = parseInt(val,10);
      case 1: return output[key] = val;
      default: return output[key] = true;
    }
  });
  return output;
};
