//-----------------------------------
//
// DOJO.Stack: Stack some tileSources
// New DOJO.Source
//     DOJO.Source.init
// -- Made by main.js
// -- Init by main.js
//-----------------------------------
log = console.log.bind(window.console);

DOJO.Stack = function(src_terms){

    // Setup
    var channels = src_terms.channel || ['i'];
    this.preset = channels.split('').map(this.layerer);
    this.nLayers = this.preset.length;
    this.depth = src_terms.depth;
    // Prepare the sources
    var protoSource = new DOJO.Source(src_terms);
    this.source = this.sourcer(protoSource);
    this.maxLevel = this.source[0].tileSource.maxLevel;
}

DOJO.Stack.prototype = {
    w: null,
    vp: null,
    level: 0,
    now: 0,
    index: {
      up: 1,
      down: -1
    },
    layerer: function(char){
        var layers = {
            i: {gl:0, mod:''},
            s: {gl:0, mod:'&segmentation=y&segcolor=y'},
            g: {gl:1, target: true, mod:'&segmentation=y'},
            y: {gl:1, target: true, mod:'&synapse=y'},
            dojo: {gl:0, dojo:true}
        };
        var src = layers[char] || layers.i;
        return {src:src, set:{}}
    },
    share: DOJO.Source.prototype.share.bind(null),
    make: function(protoSource,preset,src,set){
        var source = protoSource.init(this.share(preset.src, src));
        return this.share(set, source);
    },
    sourcer: function(proto){
        var sources = [];
        for (var preset of this.preset){
          for (var level = 0; level < this.depth; level++){
            var diff = Math.abs(level-this.now);
            var src = {z:level,minLevel:this.level};
            var set = {opacity: Number(diff <= 2)};
            sources.push(this.make(proto,preset,src,set));
          }
        }
        var set = {opacity: 1};
        var src = {z:-1,minLevel:this.level};
        var dojosource = this.layerer('dojo');
        sources.push(this.make(proto,dojosource,src,set));
        return sources;
    },
    init: function(osd){
        this.vp = osd.viewport;
        this.w = osd.world;
        return this;
    },
    findIndex: function(z){
        var found = []
        for (var layi in this.preset){
            found.push(layi*this.depth + this.now + z);
        }
        return found;
    },
    findLayer: function(z){
        return this.findIndex(z).map(this.w.getItemAt,this.w);
    },
    setOpacity: function(image){
      image.setOpacity(this);
    },
    showLayer: function(z){
        this.findLayer(z).map(this.setOpacity,1);
    },
    hideLayer: function(z){
        this.findLayer(z).map(this.setOpacity,0);
    },
    check: function(event){
        return this.findLayer(this.index[event]);
    },
    getDojo: function(){
        var index = this.w.getItemCount()-1;
        return this.w.getItemAt(index);
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
    zoomer: function(e){
        var z = Math.max(e.zoom,1);
        var level = Math.ceil(Math.log(z)/Math.LN2);
        this.level = Math.min(level, this.maxLevel);
    }
};