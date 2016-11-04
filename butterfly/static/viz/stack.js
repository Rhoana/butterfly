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
    protoSource = new DOJO.Source(src_terms);
    this.source = this.sourcer(protoSource);
    this.maxLevel = this.source[0].tileSource.maxLevel;
}

DOJO.Stack.prototype = {
    w: null,
    vp: null,
    maxBuff: 10,
    level: 0,
    now: 0,
    index: {
      up: 1,
      down: -1
    },
    flip: {
      up: 'down',
      down: 'up'
    },
    zBuff: {
      up: 0,
      down: 0
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
    make: function(protoSource,preset,src,alpha){
        var source = protoSource.init(this.share(preset.src, src));
        return this.share({opacity: alpha, preload: !!alpha}, source);
    },
    sourcer: function(proto){
        var sources = [];
        for (var preset of this.preset){
          for (var level = 0; level < this.depth; level++){
            var alp = Number(level == this.now);
            var src = {z:level,minLevel:this.level};
            sources.push(this.make(proto,preset,src,alp));
          }
        }
        var src = {z:-1,minLevel:this.level};
        var dojosource = this.layerer('dojo');
        sources.push(this.make(proto,dojosource,src,1));
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
    findBuffer: function(zBuff,dojo){
        var buffer = []
        for (var zb = zBuff.down; zb <= zBuff.up; zb++){
          [].push.apply(buffer,this.findLayer(zb));
        }
        if (dojo){
          buffer.push(this.getDojo());
        }
        return buffer;
    },
    getDojo: function(){
        var index = this.w.getItemCount()-1;
        return this.w.getItemAt(index);
    },
    setPreload: function(image){
        image.setPreload(Boolean(this==true));
    },
    setOpacity: function(image){
        image.setOpacity(Number(this));
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
    fullyLoaded: function(zBuff){
        var fullyLoaded = function(image){
          return  image && image.getFullyLoaded() && !!image.lastDrawn.length;
        }
        return this.findBuffer(zBuff,1).every(fullyLoaded);
    },
    clamp: function(buff,action){
      var z = this.now + buff[action];
      var small = Math.abs(buff[action]) < this.maxBuff;
      var bounds = {
        up: small && z < this.depth-2,
        down: small && z > 0
      }
      return bounds[action];
    },
    updateBuff: function(zBuff,action){
        var newBuff = {
          up: zBuff.up,
          down: zBuff.down
        }
        if (action){
          var back = this.flip[action];
          var backStep = newBuff[back] + this.index[back];
          var shiftStep = newBuff[action] - this.index[action];
          if (Math.sign(shiftStep) === this.index[action]){
            newBuff[action] = shiftStep;
          }
          if (this.clamp(newBuff,back)){
            newBuff[back] = backStep;
          }
          else{
            this.findLayer(zBuff[back]).map(this.setPreload,false);
          }
        }
        log(newBuff)
        if(this.fullyLoaded(newBuff)){
          if(this.clamp(newBuff,'down')){
            newBuff.down --;
            this.findLayer(newBuff.down).map(this.setPreload,true);
          }
          if(this.clamp(newBuff,'up')){
            newBuff.up ++;
            this.findLayer(newBuff.up).map(this.setPreload,true);
          }
        }
        return newBuff;
    },
    refresher: function(e){
        e.item.addHandler('fully-loaded-change',function(e){
            var event = e.eventSource;
            var source = event.source;
            if(e.fullyLoaded){
                if(this.fullyLoaded(this.zBuff)){
                    this.zBuff = this.updateBuff(this.zBuff)
                }
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