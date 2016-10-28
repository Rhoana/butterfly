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
    init: function(input){
        var seaGL = this.seaGL;
        var stack = this.stack;
        var fun = function(){ };
        var found = input.findings;
        var rgb2id = function(rgb){
          return rgb[0] + 256*rgb[1] + 65536*rgb[2];
        }
        var isTarget = fun.call.bind(function(){
          return this.source && this.source.gl;
        });
        var isDojo = fun.call.bind(function(){
          return this.source && this.source.dojo;
        });
        var nearTile = function(tile){
          var where = new OpenSeadragon.Point(tile.x,tile.y);
          return this.level == tile.level && this.xy.equals(where);
        }
        var isTile = function(tile){
          var here = this.bounds.getTopLeft();
          var where = tile.bounds.getTopLeft();
          return this.level == tile.level && here.equals(where);
        }
        var contextualize = function(tile){
          return tile.cacheImageRecord.getRenderedContext();
        }
        var pointColor = function(point,tile) {
            var shape = tile.bounds.getSize();
            var space = tile.bounds.getTopLeft();
            var inImg = contextualize(tile);
            var inCanv = inImg.canvas;
            var d = point.minus(space);
            var tmp = [d.x/shape.x, d.y/shape.y];
            var xy = [inCanv.width*tmp[0], inCanv.height*tmp[1]].map(Math.ceil);
            return inImg.getImageData(xy[0], xy[1], 1, 1).data;
        }
        var click = function(callback,e){
          var point = stack.vp.viewerElementToViewportCoordinates(e.position);
          var allItems = stack.getItems('now').reverse();
          var targets = allItems.filter(isTarget)[0];
          var dojo = allItems.filter(isDojo)[0];
          if(dojo && targets && targets.lastDrawn.length){
            var here = {level: targets.lastDrawn[0].level};
            here.xy = dojo.source.getTileAtPoint(here.level,point);
            var hereTile = targets.lastDrawn.filter(nearTile.bind(here))[0];
            if(hereTile){
              this.viaGL.clickID = pointColor(point,hereTile);
              found[1].childNodes[1].innerHTML = rgb2id(this.viaGL.clickID);
              this.openSD.forceRedraw();
            }
          }
        }
        var draw = function(callback,e){
          var dojo = e.tiledImage.source.dojo;
          var ind = stack.w.getIndexOfItem(e.tiledImage);
          var allItems = stack.getItems('now').reverse();
          var targets = allItems.filter(isTarget)[0];
          if(0 <= stack.index['now'].indexOf(ind) && dojo && targets && targets.lastDrawn.length){
            var fromTile = targets.lastDrawn.filter(isTile.bind(e.tile))[0];
            if(fromTile){
              e.output = contextualize(e.tile);
              e.rendered = contextualize(fromTile);
              callback(e);
            }
          }
        }
        // Load for glsl
        var GLloaded = function(program) {
          this.clicker = this.gl.getUniformLocation(program, 'u_click_id');
        }
        // Draw for glsl
        var GLdrawing = function() {
          var clickID = this.clickID || [-1,-1,-1,-1];
          this.gl.uniform4f(this.clicker, clickID[0], clickID[1], clickID[2], clickID[3]);
        }
        seaGL.addHandler('gl-loaded',GLloaded);
        seaGL.addHandler('gl-drawing',GLdrawing);
        seaGL.addHandler('canvas-click',click);
        seaGL.addHandler('tile-drawing',draw);
        return seaGL.init();
    }
}