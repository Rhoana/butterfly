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
          var where = new OpenSeadragon.Point(tile.x,tile.y);
          return this.equals(where);
        }
        var click = function(callback,e){

          var allItems = stack.getItems('now').reverse();
          var point = stack.vp.viewerElementToViewportCoordinates(e.position);
          var dojo = allItems.filter(isDojo)[0];
          if(!dojo){
            return;
          }
          for (var layer of allItems.filter(canClick)){
            var last = layer.lastDrawn[0];
            if (last){
              var xy = layer.source.getTileAtPoint(last.level,point);
              var fromTile = layer.lastDrawn.filter(isTile.bind(xy))[0];
              var toTile = dojo.lastDrawn.filter(isTile.bind(xy))[0];
              if (fromTile && toTile){
                this.viaGL.tileShape = fromTile.bounds.getSize();
                this.viaGL.tileSpace = fromTile.bounds.getBottomLeft();
                this.viaGL.tileSpace.y = 1 - this.viaGL.tileSpace.y;
                e.rendered = fromTile.cacheImageRecord._renderedContext;
                e.output = toTile.cacheImageRecord._renderedContext;
                callback(e);
                break;
              }
            }
          }
        }

        // Load for glsl
        var GLloaded = function(program) {
          this.wherer = this.gl.getUniformLocation(program, 'u_tile_where');
          this.shaper = this.gl.getUniformLocation(program, 'u_tile_shape');
        }

        // Draw for glsl
        var GLdrawing = function() {
          this.gl.uniform2f(this.wherer, this.tileSpace.x, this.tileSpace.y);
          this.gl.uniform2f(this.shaper, this.tileShape.x, this.tileShape.y);
        }

        seaGL.addHandler('gl-loaded',GLloaded);
        seaGL.addHandler('gl-drawing',GLdrawing);
        seaGL.addHandler('canvas-click',click);

        return seaGL.init();
    }
}