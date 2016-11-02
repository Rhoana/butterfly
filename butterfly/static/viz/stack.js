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
    channels = channels.split('').concat('dojo');
    this.preset = channels.map(this.layerer);
    this.nLayers = this.preset.length;
    // Prepare the sources
    this.protoSource = new DOJO.Source(src_terms);
    this.source = this.make(this.now, new Array(this.nLayers));
    this.index = this.indexer(this.preset);
    this.total = this.source.length;
}

DOJO.Stack.prototype = {
    now: 0,
    level: 0,
    zBuff: 0,
    maxBuff: 100,
    loadBuff: {up:3,down:-3},
    layerer: function(char,i){
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
    make: function(zLevel, indices) {
        return this.preset.map(this.sourcer.bind(this,zLevel,indices));
    },
    share: DOJO.Source.prototype.share.bind(null),
    sourcer: function(zLevel, indices, layer, i){
        var levelDiff = zLevel - this.now;
        var src = {z:zLevel,minLevel:this.level};
        var set = {opacity: Number(levelDiff <= this.loadBuff.up && levelDiff >= this.loadBuff.down)};
        var source = this.protoSource.init(this.share(layer.src, src));
        return this.share(this.share(set, {index:indices[i]}), source);
    },
    indexer: function(zBuff){
        var nL = this.nLayers;
        var preset = this.preset;
        var buffer = function(zbo){
          return preset.map(function(p,i){
              return Math.max(zbo,0)*nL+i;
          });
        }
        return {
          'start': buffer(0),
          'up': buffer(zBuff),
          'down': buffer(zBuff-1),
          'end': buffer(2*zBuff-1),
          'now': buffer(2*zBuff)
        }
    },
    init: function(osd){
        var w = osd.world;
        var nL = this.nLayers;
        this.getItems = function(event,loaded){
            var indices = this.index[event];
            if (loaded){
              indices = indices.map(function(ind){
                var offset = loaded[event]
                if (event == 'up'){
                  return ind + Math.max(offset-2,-1)*nL;
                }
                return ind + offset*nL;
              });
            }
            return indices.map(w.getItemAt, w);
        }
        this.setOpacity = function(event,loaded){
            var tiles = this.getItems(event,loaded);
//            log('loaded ' + event + ' ' + loaded[event] )
            tiles.map(function(t){
              t.setOpacity(1);
            });
        }
        this.check = function(event){
            if (this.total == w.getItemCount()) {
              return this.getItems(event);
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
        this.log = function(){
            for(var c = 0; c < w.getItemCount(); c++){
               log(w.getItemAt(c).source.z);
            }
            log(' ');
        }
        this.vp = osd.viewport;
        this.w = w;
        return this;
    },
    updater: function(){
        if (this.zBuff < this.maxBuff){
            this.zBuff += 1;
            this.total += 2*this.nLayers;
            this.index = this.indexer(this.zBuff);
//            if (this.zBuff > this.loadBuff.up){
//                this.setOpacity('up',this.loadBuff)
//                this.loadBuff.up ++;
//            }
//            if (-this.zBuff < this.loadBuff.down){
//                this.setOpacity('down',this.loadBuff)
//                this.loadBuff.down --;
//            }

            this.gain(-this.zBuff, this.index.start);
            this.gain(this.zBuff, this.index.end);
        }
    },
    refresher: function(e){
        e.item.addHandler('fully-loaded-change',function(e){
            var event = e.eventSource;
            var source = event.source;
            if(e.fullyLoaded){
                if(!this.w.needsDraw()){
                    var levelDiff = source.z - this.now;
                    if (levelDiff == this.loadBuff.up){
                        for (var reps = levelDiff; reps < this.maxBuff; reps++){
                          this.updater();
                          log(this.zBuff)
                        }
                    }
                    this.updater();
                    log(this.w)
                    log(this.w.getItemCount())
                }
                source.minLevel = 0;
                event.draw();
                return;
            }
        }.bind(this));
    },
    zoomer: function(e){
        var z = Math.max(e.zoom,1);
        var maxLevel = this.source[0].tileSource.maxLevel;
        this.level = Math.min(Math.ceil(Math.log(z)/Math.LN2), maxLevel);
    }
};