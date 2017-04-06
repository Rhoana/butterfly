/*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
/* OpenSeadragonGL - Set Shaders in OpenSeaDragon with viaWebGL
*/
OpenSeadragonGL = function(openSD) {

    /* OpenSeaDragon API calls
    ~*~*~*~*~*~*~*~*~*~*~*~*/
    this.interface = {
        'tile-loaded': function(e) {
            // Set the imageSource as a data URL and then complete
            var output = this.viaGL.toCanvas(e.image);
            e.image.onload = e.getCompletionCallback();
            e.image.src = output.toDataURL();
        },
        'tile-drawing': function(e) {
            // Render a webGL canvas to an input canvas
            var input = e.rendered.canvas;
            e.output.canvas.width = input.width;
            e.output.canvas.height = input.height;
            e.output.drawImage(this.viaGL.toCanvas(input), 0, 0, input.width, input.height);
        },
        'canvas-click': function(e) {
            // For clicking
            var input = e.rendered.canvas;
            e.output.canvas.width = input.width;
            e.output.canvas.height = input.height;
            e.output.drawImage(this.viaGL.toCanvas(input), 0, 0, input.width, input.height);
        }
    };
    this.defaults = {
        'tile-loaded': function(callback, e) {
            callback(e);
        },
        'tile-drawing': function(callback, e) {
            callback(e);
        },
        'canvas-click': function(callback, e) {
            callback(e);
        }
    };
    this.openSD = openSD;
    this.viaGL = new ViaWebGL();
};

OpenSeadragonGL.prototype = {
    // Map to viaWebGL and OpenSeadragon
    init: function() {
        var open = this.open.bind(this);
        return new Promise(open);
    },
    open: function(done) {
        var merge = this.merger.bind(this);
        this.openSD.addHandler('open',function(e){
            merge(e).then(done);
        });
    },
    // User adds events
    addHandler: function(key,custom) {
        if (key in this.defaults){
            this[key] = this.defaults[key];
        }
        if (typeof custom == 'function') {
            this[key] = custom;
        }
    },
    // Merge with viaGL
    merger: function(e) {
        // Take GL height and width from OpenSeaDragon
        this.width = this.openSD.source.getTileWidth();
        this.height = this.openSD.source.getTileHeight();
        // Add all viaWebGL properties
        for (var key of this.and(this.viaGL)) {
            this.viaGL[key] = this[key];
        }
        var join = this.adder.bind(this);
        return this.viaGL.init().then(join);
    },
    // Add all seadragon properties
    adder: function(e) {
        for (var key of this.and(this.defaults)) {
            var that = {
              handler: this[key].bind(this),
              interface: this.interface[key].bind(this)
            }
            // Add all OpenSeadragon event handlers
            this.openSD.addHandler(key, function(e) {
                this.handler(this.interface, e);
            }.bind(that));
        }
    },
    // Joint keys
    and: function(obj) {
      return Object.keys(obj).filter(Object.hasOwnProperty,this);
    },
    // Add your own button to OSD controls
    button: function(terms) {

        var name = terms.name || 'tool';
        var prefix = terms.prefix || this.openSD.prefixUrl;
        if (!terms.hasOwnProperty('onClick')){
            terms.onClick = this.shade;
        }
        terms.onClick = terms.onClick.bind(this);
        terms.srcRest = terms.srcRest || prefix+name+'_rest.png';
        terms.srcHover = terms.srcHover || prefix+name+'_hover.png';
        terms.srcDown = terms.srcDown || prefix+name+'_pressed.png';
        terms.srcGroup = terms.srcGroup || prefix+name+'_grouphover.png';
        // Replace the current controls with the same controls plus a new button
        this.openSD.clearControls().buttons.buttons.push(new OpenSeadragon.Button(terms));
        var toolbar = new OpenSeadragon.ButtonGroup({buttons: this.openSD.buttons.buttons});
        this.openSD.addControl(toolbar.element,{anchor: OpenSeadragon.ControlAnchor.TOP_LEFT});
    },
    // Switch Shaders on or off
    shade: function() {

        this.viaGL.on++;
        this.openSD.world.resetItems();
    }
}
