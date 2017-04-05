window.SCOPE = {}
window.DOJO = {}
//-----------------------------------
//
// http://<host>:<port>/viz.html?server=<...>&datapath=<...>
// New window.DOJO.Stack
//     window.DOJO.Stack.init
// New OpenSeadragon
// New window.DOJO.Input
// -- Called first
//-----------------------------------
window.onload = function(e){

  OpenSeadragon.ImageLoader = ZipLoader;
  // preset tile source
  window.SCOPE.stack  = new window.DOJO.Stack(window.SCOPE.parse());
  // Open a seadragon with two layers
  window.SCOPE.openSD = OpenSeadragon({
    tileSources: window.SCOPE.stack.source,
    crossOriginPolicy: "Anonymous",
    prefixUrl: "../images/icons/",
    minZoomImageRatio: .2,
    maxZoomPixelRatio: 8,
    showZoomControl: 0,
    showHomeControl: 0,
    id: "viaWebGL"
  });
  window.SCOPE.openSD.world.addHandler("add-item", window.SCOPE.stack.refresher.bind(window.SCOPE.stack));
  window.SCOPE.openSD.addHandler("zoom",window.SCOPE.stack.zoomer.bind(window.SCOPE.stack));
  // Link everything to WebGL
  window.SCOPE.stack.init(window.SCOPE.openSD);
  window.SCOPE.link = new window.DOJO.Input(window.SCOPE);
};

// Change any preset terms set in input address
window.SCOPE.parse = function(maker) {
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
