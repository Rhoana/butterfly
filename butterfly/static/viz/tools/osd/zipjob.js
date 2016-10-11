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

        var output = this.viaGL.toCanvas(raw);
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

}