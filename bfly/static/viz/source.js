//-----------------------------------
//
// window.DOJO.Source: makes tileSources
// -- Made & Init by window.DOJO.Stack
//-----------------------------------

window.DOJO.Source = function(src_terms){
  // Change the default source terms
  this.tileSource = this.share(src_terms, this.tileSource);
};

window.DOJO.Source.prototype = {
  init: function(src_terms){
    var sourcer = this.share(this.tileSource,{});
    var source = this.share(src_terms, sourcer);
    var maxLevel = source.width/source.tileSize;
    source.maxLevel = Math.floor(Math.log2(maxLevel));
    if (source.target){
      source.datapath += "&format=zip";
    }
    return {tileSource: source};
  },
  tileSource: {
    z: 0,
    mod: "",
    server: "",
    datapath: "",
    minLevel: 0,
    width: 8192,
    height: 8192,
    tileSize: 512,
    getTileUrl: function( level, x, y ) {

      if (this.dojo) {
        return "/images/pix.png?"+[level,x,y].join("-");
      }
      var blevel = this.maxLevel - level;
      var t_width = this.getTileWidth(level);
      var t_height = this.getTileHeight(level);
      var bounds = this.getTileBounds(level, x, y).getSize();
      var shape = bounds.times(this.getLevelScale(level)*this.width);
      var [width, height] = [Math.round(shape.x), Math.round(shape.y)];
      var start = ["", "x="+x*t_width, "y="+y*t_height, "z="+this.z].join("&");
      var size = ["", "width="+width, "height="+height].join("&");
      var resolution = "&resolution=" + blevel;

      return this.server + this.datapath + start + size + resolution;
    }
  },
  share: function(from, to) {
    for (var key in from) {
      to[key] = from[key];
    }
    return to;
  }
}
