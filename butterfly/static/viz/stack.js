//-----------------------------------
//
// DOJO.Stack: Stack some tileSources
// New DOJO.Source
//     DOJO.Source.init
// -- Made by main.js
// -- Init by main.js
//-----------------------------------

DOJO.Stack = function(src_terms){

    // Setup
    var zBuff = this.zBuff;
    var first = this.now-zBuff;

    this.idflag = Number(src_terms.id || 0);
    this.glflag = Number(src_terms.gl || 0);
    this.seg = src_terms.overlay? 1: this.idflag;
    this.nLayers = 1+Number(src_terms.overlay || 0);
    this.layers[1].set.opacity = [.5,1][this.glflag || this.idflag];
    this.preset = this.range(this.nLayers).map(this.layerer, this);

    var keys = this.range(2*zBuff+1);
    var addFirst = this.add.bind(first);
    var join = this.join.bind(this,this.nLayers);

    // Prepare the sources
    keys.push(keys.splice(zBuff, 1)[0]);
    this.protoSource = new DOJO.Source(src_terms);
    this.source = keys.map(addFirst).reduce(join,[]);
    this.index = this.indexer(zBuff,this.nLayers);
    this.total = this.nLayers*keys.length;
}

DOJO.Stack.prototype = {
    now: 0,
    zBuff: 1,
    preset: [],
    layers: [
        {
            set: {},
            src: {}
        },
        {
            set: {},
            src: {segmentation: true}
        }
    ],
    init: function(osd){
        var w = osd.world;
        this.event = function(event){
            if (this.total == w.getItemCount()) {
              return this.index[event].map(w.getItemAt, w);
            }
        }
        this.lose = function(lost){
            lost.map(w.getItemAt,w).map(w.removeItem,w);
        }
        this.gain = function(offset, index){
            this.make(offset+this.now, index).map(osd.addTiledImage,osd);
        }
        this.show = function(shown){
            shown.map(w.getItemAt,w).map(function(shownItem){
                w.setItemIndex(shownItem, w.getItemCount()-1);
            });
            this.index.end.map(w.getItemAt,w).map(function(lastItem,i){
                w.setItemIndex(lastItem, shown[i]);
            });
        }
        this.w = w;
        return this;
    },
    share: DOJO.Source.prototype.share.bind(null),
    sourcer: function(zLevel, indices, layer, i){
        var src = {z:zLevel,minLevel:this.level,glflag:this.glflag};
        var source = this.protoSource.init(this.share(layer.src, src));
        return this.share(this.share(layer.set, {index:indices[i]}), source);
    },
    indexer: function(zBuff, nLayers){
        var arrows = this.arrows.bind(this);
        var index = [0, zBuff, zBuff-1, 2*zBuff-1];
        var timesLayers = this.times.bind(nLayers);
        var addRange = this.addRange.bind(this, nLayers);
        index = [].slice.call(new Uint8ClampedArray(index));
        return index.map(timesLayers).map(addRange).reduce(arrows,{});
    },
    make: function(zLevel, indices) {
        return this.preset.map(this.sourcer.bind(this,zLevel,indices));
    },
    join: function(nLayers, out, zLevel) {
        return out.concat(this.make(zLevel,new Array(nLayers)));
    },
    arrows: function(out,index,i) {
        out[['start','up','down','end'][i]] = index;
        return out;
    },
    range: function(end){
        return Object.keys(new Uint8Array(end)).map(Number);
    },
    addRange: function(layers,one) {
        return this.range(layers).map(this.add,one);
    },
    add: function(that) {
        return this + that;
    },
    times: function(that) {
        return this * that;
    },
    layerer:  function(ind){
        var kind = Number(ind == this.nLayers-this.seg);
        return this.share(this.layers[kind],{});
    },
    refresher: function(e){
        e.item.addHandler('fully-loaded-change',function(e){
            var event = e.eventSource;
            var source = event.source;
            if(e.fullyLoaded){
                source.minLevel = 0;
                event.draw();
                return;
            }
        }.bind(this));
    },
    porter: function(e){

    },
    zoomer: function(e){
        var z = Math.max(e.zoom,1);
        var maxLevel = this.source[0].tileSource.maxLevel;
        this.level = Math.min(Math.ceil(Math.log(z)/Math.LN2), maxLevel);
    },
    level: 0
};