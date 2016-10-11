// private class
function ImageJob ( options ) {

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
}

ImageJob.prototype = {
    errorMsg: null,
    start: function(){
        var _this = this;

        this.image = new Image();

        if ( this.crossOriginPolicy !== false ) {
            this.image.crossOrigin = this.crossOriginPolicy;
        }

        this.image.onload = function(){
            _this.finish( true );
        };
        this.image.onabort = this.image.onerror = function(){
            _this.errorMsg = "Image load aborted";
            _this.finish( false );
        };

        this.jobId = window.setTimeout( function(){
            _this.errorMsg = "Image load exceeded timeout";
            _this.finish( false );
        }, this.timeout);

        this.image.src = this.src;
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
    }

}