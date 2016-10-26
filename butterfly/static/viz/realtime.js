//-----------------------------------
//
// DOJO.RealTime - WebGL Annimation
// gets OpenSeadragon
// new openSeadragonGL
//     openSeadragonGL.init
// -- Made by DOJO.Input
// -- Init by DOJO.Input
//-----------------------------------


DOJO.RealTime = function(scope) {
    this.stack = scope.stack;
    this.seaGL = new openSeadragonGL(scope.openSD);
    this.seaGL.vShader = './shaders/vertex/rect.glsl';
    this.seaGL.fShader = './shaders/fragment/rect.glsl';
}

DOJO.RealTime.prototype = {
    init: function(){
        var seaGL = this.seaGL;
        var stack = this.stack;
        var fun = function(){ };
        var canClick = fun.call.bind(function(){
          return this.source && this.source.gl;
        });
        var isDojo = fun.call.bind(function(){
          return this.source && this.source.dojo;
        });
        var isTile = function(tile){
          var here = this.bounds.getTopLeft();
          var where = tile.bounds.getTopLeft();
          return this.level == tile.level && here.equals(where);
        }
        // Image to Tile
        var image2tile = function(point,space,shape) {
            var d = point.minus(space);
            return [d.x/shape.x, d.y/shape.y];
        }
        var click = function(callback,e){

          var allItems = stack.getItems('now').reverse();
          var point = stack.vp.viewerElementToViewportCoordinates(e.position);
          var layer = allItems.filter(canClick)[0];
          var dojo = allItems.filter(isDojo)[0];
          if(!dojo || !layer){
            return;
          }
          for (var toTile of dojo.lastDrawn){
            var fromTile = layer.lastDrawn.filter(isTile.bind(toTile))[0];
            if (fromTile){
              e.rendered = fromTile.cacheImageRecord.getRenderedContext();
              e.output = toTile.cacheImageRecord.getRenderedContext();
              var tileShape = fromTile.bounds.getSize();
              var tileSpace = fromTile.bounds.getTopLeft();
              this.viaGL.clickSpot = image2tile(point,tileSpace,tileShape);
              this.viaGL.clickSpot[1] = 1 - this.viaGL.clickSpot[1];
              callback(e);
            }
          }
          this.openSD.forceRedraw();
        }

        // Load for glsl
        var GLloaded = function(program) {
          this.clicker = this.gl.getUniformLocation(program, 'u_click_pos');
        }

        // Draw for glsl
        var GLdrawing = function() {
          this.gl.uniform2f(this.clicker, this.clickSpot[0], this.clickSpot[1]);
        }

        seaGL.addHandler('gl-loaded',GLloaded);
        seaGL.addHandler('gl-drawing',GLdrawing);
        seaGL.addHandler('canvas-click',click);

        return seaGL.init();
    }
}