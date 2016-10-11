//-----------------------------------
//
// DOJO.RealTime - WebGL Annimation
// gets OpenSeadragon
// new openSeadragonGL
//     openSeadragonGL.init
// -- Made by DOJO.Input
// -- Init by DOJO.Input
//-----------------------------------


DOJO.RealTime = function(osd) {
    this.seaGL = new openSeadragonGL(osd);
    this.seaGL.vShader = './shaders/vertex/square.glsl';
    this.seaGL.fShader = './shaders/fragment/outline.glsl';
}

DOJO.RealTime.prototype = {
    init: function(){
        return this.seaGL.init();
    }
}