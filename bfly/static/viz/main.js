var SCOPE = {};
var DOJO = {};
//-----------------------------------
//
// http://<host>:<port>/viz.html?server=<...>&datapath=<...>
// New DOJO.Stack
//     DOJO.Stack.init
// New OpenSeadragon
// New DOJO.Input
// -- Called first
//-----------------------------------
window.onload = function(e){

  OpenSeadragon.ImageLoader = ZipLoader;
  // preset tile source
  SCOPE.stack  = new DOJO.Stack(SCOPE.parse());
  // Open a seadragon with two layers
  SCOPE.openSD = OpenSeadragon({
    tileSources: SCOPE.stack.source,
    crossOriginPolicy: "Anonymous",
    prefixUrl: "../images/icons/",
    minZoomImageRatio: .2,
    maxZoomPixelRatio: 8,
    showZoomControl: 0,
    showHomeControl: 0,
    id: "viaWebGL"
  });
  SCOPE.openSD.world.addHandler("add-item", SCOPE.stack.refresher.bind(SCOPE.stack));
  SCOPE.openSD.addHandler("zoom",SCOPE.stack.zoomer.bind(SCOPE.stack));
  // Link everything to WebGL
  SCOPE.stack.init(SCOPE.openSD);
  SCOPE.link = new DOJO.Input(SCOPE);
};

// Change any preset terms set in input address
SCOPE.parse = function(maker) {
  var output = {};
  var input = document.location.search;
  var string = decodeURI(input).slice(1);
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
