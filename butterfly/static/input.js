//-----------------------------------
//
// DOJO.Input - Let people control slices
// gets OpenSeadragon
// gets DOJO.Stack
// new DOJO.RealTime
//     DOJO.RealTime.init
// -- Called by main.js
// -- Init by self
//-----------------------------------

DOJO.Input = function(scope) {

    this.osd = scope.openSD;
    this.stack = scope.stack;
    this.realT = new DOJO.RealTime(this.osd);
    this.realT.init().then(this.init.bind(this));
}

DOJO.Input.prototype = {

    init: function(){
        var seaGL = this.realT.seaGL;
        var toolbar = ['up','down'].map(this.button, this);
        var keychain = this.key.bind(toolbar.reduce(this.chain,{}));
        this.osd.addViewerInputHook({ keyDown: keychain });
        toolbar.map(seaGL.button, seaGL);
    },
    key: function(e){
        e.shift = !e.shift;
        var keychain = this;
        if (e.shift && e.keyCode in keychain) {
            e.preventDefaultAction = true;
            keychain[e.keyCode]();
        }
    },
    event: function(event) {
        var slices = this.stack.event(event);
        if (slices.every(this.check.bind(this))) {
            if (this.stack.total == this.stack.w.getItemCount()) {
                return this[event](this.stack);
            }
        }
    },
    button: function(name) {
        var obj = {name:name};
        obj.onClick = this.event.bind(this,name);
        return obj;
    },
    chain: function(o,b,i){
        var key = [38,40][i];
        o[key] = b.onClick;
        return o;
    },
    up: function(stack){
        stack.now ++;
        stack.show(stack.index.up);
        stack.lose(stack.index.start);
        stack.gain(stack.zBuff, stack.index.end);
    },
    down: function(stack){
        stack.now --;
        stack.show(stack.index.down);
        stack.lose(stack.index.end);
        stack.gain(-stack.zBuff, stack.index.start);
    },
    check: function(slice){
        var level = this.stack.level;
        if (slice && slice.lastDrawn.length) {
            return slice.lastDrawn[0].level >= level;
        }
    }
}