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
        var isTile = function(tile){
          var where = new OpenSeadragon.Point(tile.x,tile.y);
          return this.equals(where);
        }
        var click = function(callback,e){

          var allItems = stack.getItems('now').reverse();
          var point = stack.vp.viewerElementToViewportCoordinates(e.position);

          for (var layer of allItems.filter(canClick)){
            if (layer.lastDrawn.length){
              var level = layer.lastDrawn[0].level;
              var xy = layer.source.getTileAtPoint(level,point);
              var here = layer.lastDrawn.filter(isTile.bind(xy)).pop();
              if (here){
                this.viaGL.tileShape = here.bounds.getSize();
                this.viaGL.tileSpace = here.bounds.getBottomLeft();
                this.viaGL.tileSpace.y = 1 - this.viaGL.tileSpace.y;
                e.rendered = here.cacheImageRecord._renderedContext;
                callback(e);
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

        // Add a custom button
        seaGL.button({
            tooltip: 'Toggle shaders',
            prefix: this.iconPrefix,
            name: 'shade'
        });

        return seaGL.init();
    }
}