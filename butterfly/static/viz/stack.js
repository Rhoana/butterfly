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
    this.z = src_terms.z || this.z;
    // Prepare the sources
    protoSource = new DOJO.Source(src_terms);
    this.source = this.sourcer(protoSource);
    this.maxLevel = this.source[0].tileSource.maxLevel;
}

DOJO.Stack.prototype = {
    w: null,
    vp: null,
    maxBuff: 3,
    level: 0,
    z: 0,
    flip: {
      up: 'down',
      down: 'up'
    },
    zBuff: {
      up: 0,
      down: 0
    },
    sign: {
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
    make: function(protoSource,preset,src,alpha){
        var source = protoSource.init(this.share(preset.src, src));
        return this.share({opacity: alpha, preload: !!alpha}, source);
    },
    sourcer: function(proto){
        var sources = [];
        for (var preset of this.preset){
          for (var level = 0; level < this.depth; level++){
            var alp = Number(level == this.z);
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
    findIndex: function(zb){
        var found = []
        for (var layi in this.preset){
            found.push(layi*this.depth + this.z + zb);
        }
        return found;
    },
    findLayer: function(zb){
        return this.findIndex(zb).map(this.w.getItemAt,this.w);
    },
    findBuffer: function(zBuff,dojo){
        var buffer = []
        for (var zb = -zBuff.down; zb <= zBuff.up; zb++){
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
    fullyLoaded: function(zBuff){
        var fullyLoaded = function(image){
          return  image && image.getFullyLoaded();
        }
        return this.findBuffer(zBuff,1).every(fullyLoaded);
    },
    preload: function(buffer,sign,value){
        this.findLayer(this.sign[sign]*buffer).map(this.setPreload,value);
    },
    range: function(buffer,sign){
        var z = this.z + buffer*this.sign[sign];
        return z < this.depth && z >= 0;
    },
    clamp: function(buffer,sign){
        var small = 0 <= buffer && buffer <= this.maxBuff;
        return small && this.range(buffer,sign);
    },
    updateBuff: function(zBuff,action){
        var newBuff = {
          up: zBuff.up,
          down: zBuff.down
        }
        if (action){
          var back = this.flip[action];
          var backStep = newBuff[back]+1;
          var actStep = newBuff[action]-1;
          if(this.clamp(backStep, back)) {
            newBuff[back] = backStep;
          }
          else if (this.range(backStep, back)){
            this.preload(backStep, back, false);
          }
          if (this.clamp(actStep, action)){
            newBuff[action] = actStep;
          }
        }
        if(this.fullyLoaded(newBuff)){
          for (var arrow of ['down', 'up']){
            var nextStep = newBuff[arrow]+1;
            if(this.clamp(nextStep, arrow)){
                this.preload(nextStep, arrow, true);
                newBuff[arrow] = nextStep;
            }
          }
        }
        return newBuff;
    },
    log: function(newBuff){
      log('z:' + this.z);
      log('buffer: [' + newBuff.down + ':' + newBuff.up+']');
      for (var zb = -newBuff.down; zb <= newBuff.up; zb++){
        var tab = '   ';
        var star = zb===0? '*' : ' ';
        var image = this.findLayer(zb).pop();
        if (image) {
          var zeta = image.source.z;
          var alpha = image.getOpacity();
          var preload = image.getPreload();
        }
        log(star+tab+'layer '+ zeta || 'null' );
        log(tab+tab+'opacity:'+alpha || 'null');
        log(tab+tab+'preload:'+preload || 'null');
        log(tab+tab+'index: ['+this.findIndex(zb)+']');
      };
      log(' ');
    },
    refresher: function(e){
        e.item.addHandler('fully-loaded-change',function(e){
            var image = e.eventSource;
            var source = image.source;
            if(e.fullyLoaded){
                this.zBuff = this.updateBuff(this.zBuff);
                source.minLevel = 0;
                image.draw();
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
