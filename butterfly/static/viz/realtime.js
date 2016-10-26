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
        var isTile = function(level,tile){
          var where = new OpenSeadragon.Point(tile.x,tile.y);
          return tile.level == level && this.equals(where);
        }
        // Image to Tile
        var image2tile = function(point,space,shape) {
            var d = point.minus(space);
            log(d)
            log(shape)
            log(' ')
            return [d.x/shape.x, d.y/shape.y];
        }
        var click = function(callback,e){

          var allItems = stack.getItems('now').reverse();
          var point = stack.vp.viewerElementToViewportCoordinates(e.position);
          var dojo = allItems.filter(isDojo)[0];
          if(!dojo){
            return;
          }
          var last = dojo.lastDrawn[0];
          for (var layer of allItems.filter(canClick)){
            if (last){
              var level = last.level;
              var xy = dojo.source.getTileAtPoint(level,point);
              var toTile = dojo.lastDrawn.filter(isTile.bind(xy,level))[0];
              var fromTile = layer.lastDrawn.filter(isTile.bind(xy,level))[0];
              if (fromTile && toTile){

                e.rendered = fromTile.cacheImageRecord._renderedContext;
                e.output = toTile.cacheImageRecord._renderedContext;

                var tileShape = fromTile.bounds.getSize();
                var tileSpace = fromTile.bounds.getTopLeft();
                this.viaGL.clickSpot = image2tile(point,tileSpace,tileShape);
                this.viaGL.clickSpot[1] = 1 - this.viaGL.clickSpot[1];
                callback(e);
                break;
              }
            }
          }
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