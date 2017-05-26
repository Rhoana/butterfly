//-----------------------------------
//
// window.DOJO.Input - Let people control slices
// gets OpenSeadragon
// gets window.DOJO.Stack
// new window.DOJO.RealTime
//     window.DOJO.RealTime.init
// -- Called by main.js
// -- Init by self
//-----------------------------------

window.DOJO.Input = function(scope) {

  var proto = document.getElementById("proto");
  var corner = scope.openSD.element.childNodes[0].childNodes[3];
  var list = proto.getElementsByTagName("UL")[0].cloneNode(true);
  this.findings = list.getElementsByTagName("LI");
  corner.appendChild(list);
  list.id = "findings";

  this.osd = scope.openSD;
  this.stack = scope.stack;
  this.realT = new window.DOJO.RealTime(scope);
  this.realT.init(this).then(this.init.bind(this));
  this.findings[0].childNodes[0].innerText = this.stack.z;
  this.findings[0].childNodes[1].innerText = "/"+(this.stack.depth-1);
};

window.DOJO.Input.prototype = {

  codes: {
    190: 1,
    87: 1,
    188: 2,
    83: 2,
  },
  init: function(){
    var seaGL = this.realT.seaGL;
    var toolbar = ["home","up","down"].map(this.button, this);
    this.osd.addViewerInputHook({ keyDown: this.keyDown.bind(this, toolbar) });
    this.osd.addViewerInputHook({ clickHandler: function(e){e.quick=false;} });
    window.onkeydown = this.osd.innerTracker.keyDownHandler;
    toolbar.map(seaGL.button, seaGL);
  },
  button: function(event) {
    return {name: event, onClick: this.event.bind(this,event)};
  },
  keyDown: function(toolbar,e){
    if (e.eventSource && e.keyCode in this.codes) {
      var index = this.codes[e.keyCode];
      toolbar[index].onClick();
      e.stopHandlers = true;
    }
  },
  event: function(event) {
    if (event === "home"){
      window.location.replace("index.html");
      return;
    }
    if (!this.stack.clamp(1,event)){
      return;
    }
    var check = function(slice){
      return slice && slice.lastDrawn.length;
    };
    var sign = this.stack.sign[event];
    var slices = this.stack.findLayer(sign);
    if (slices && slices.every(check)) {
      return this[event](this.stack);
    }
  },
  up: function(stack){
    stack.showLayer(1);
    stack.hideLayer(0);
    stack.z ++;
    stack.zBuff = stack.updateBuff(stack.zBuff,"up");
    this.findings[0].childNodes[0].innerText = stack.z;
  },
  down: function(stack){
    stack.showLayer(-1);
    stack.hideLayer(0);
    stack.z --;
    stack.zBuff = stack.updateBuff(stack.zBuff,"down");
    this.findings[0].childNodes[0].innerText = stack.z;
  }
};
