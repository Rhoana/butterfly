// private class
function ZipJob ( viaGL, options ) {

    OpenSeadragon.extend( true, this, {
        timeout:        OpenSeadragon.DEFAULT_SETTINGS.timeout,
        jobId:          null
    }, options );

    /**
     * Image object which will contain downloaded image.
     * @member {Image} image
     * @memberof OpenSeadragon.ImageJob#
     */
    this.image = null;
    this.viaGL = viaGL;
}

ZipJob.prototype = {
    errorMsg: null,
    start: function(){
        this.image = new Image();
        this.unzip().then(this.set.bind(this));
    },

    set: function(raw) {
        var size = this.parse(this.src).size.split(",").slice(0,2).map(Number);
        var output = this.viaGL.toCanvas(raw,size);
        this.image.onload = this.finish.bind(this);
        this.image.src = output.toDataURL();
    },

    finish: function( successful ) {
        this.image.onload = this.image.onerror = this.image.onabort = null;
        if (!successful) {
            this.image = null;
        }

        if ( this.jobId ) {
            window.clearTimeout( this.jobId );
        }

        this.callback( this );
    },

    unzip: function(){

        var unzip = function(blob){
            var compressed = new Zlib.Inflate(new Uint8Array(blob));
            return compressed.decompress();
        }

        return this.get(this.src).then(unzip);
    },

    // Get a file as a promise
    get: function(where) {
        var win = function(bid){
            if (bid.status == 200) {
                return this(bid.response);
            }
            return this(where);
        };
        return new Promise(function(done){
            var bid = new XMLHttpRequest();
            bid.responseType = 'arraybuffer';
            bid.onload = win.bind(done,bid);
            bid.open('GET', where, true);
            bid.send();
        });
    },

    // Change any preset terms set in input address
    parse: function(input) {
        var output = {};
        var string = decodeURI(input);
        // read value pair as bool, string, or int
        string.split('&').map(function(pair) {
            var key = pair.split('=')[0];
            var val = pair.split('=')[1];
            switch (!val*2 + !Number(val)) {
                case 0: return output[key] = parseInt(val,10);
                case 1: return output[key] = val;
                default: return output[key] = true;
            }
        });
        return output;
    }

}