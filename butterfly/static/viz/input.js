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

    codes: {
      190: 0,
      87: 0,
      188: 1,
      83: 1,
    },
    init: function(){
        var seaGL = this.realT.seaGL;
        var toolbar = ['up','down'].map(this.button, this);
        this.osd.addViewerInputHook({ keyDown: this.keyDown.bind(this, toolbar) });
        window.onkeydown = this.osd.innerTracker.keyDownHandler;
        toolbar.map(seaGL.button, seaGL);
    },
    button: function(event) {
        return {name: event, onClick: this.event.bind(this,event)};
    },
    keyDown: function(toolbar,e){
        if (e.keyCode in this.codes) {
            var index = this.codes[e.keyCode];
            toolbar[index].onClick();
            e.stopHandlers = true;
        }
    },
    event: function(event) {
        var level = this.stack.level;
        var check = function(slice){
            if (slice && slice.lastDrawn.length) {
                return slice.lastDrawn[0].level >= level;
            }
        }
        var slices = this.stack.event(event);
        if (slices && slices.every(check)) {
            return this[event](this.stack);
        }
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
    }
}