/**
 * @class ImageLoader
 * @memberof OpenSeadragon
 * @classdesc Handles downloading of a set of images using asynchronous queue pattern.
 * You generally won't have to interact with the ImageLoader directly.
 * @param {Object} options - Options for this ImageLoader.
 * @param {Number} [options.jobLimit] - The number of concurrent image requests. See imageLoaderLimit in {@link OpenSeadragon.Options} for details.
 */
function ZipLoader( options ) {
    this.viaGL = new ViaWebGL();
    this.viaGL.vShader = '../shaders/vertex/square.glsl';
    this.viaGL.fShader = '../shaders/fragment/ids.glsl';
    this.viaGL.init();
    OpenSeadragon.extend( true, this, {
        jobLimit:       OpenSeadragon.DEFAULT_SETTINGS.imageLoaderLimit,
        jobQueue:       [],
        jobsInProgress: 0
    }, options );

};

/** @lends OpenSeadragon.ImageLoader.prototype */
ZipLoader.prototype = {

    /**
     * Add an unloaded image to the loader queue.
     * @method
     * @param {String} src - URL of image to download.
     * @param {String} crossOriginPolicy - CORS policy to use for downloads
     * @param {Function} callback - Called once image has been downloaded.
     */
    addJob: function( options ) {
        var _this = this,
            complete = function( job ) {
                completeJob( _this, job, options.callback );
            },
            jobOptions = {
                src: options.src,
                crossOriginPolicy: options.crossOriginPolicy,
                callback: complete,
                abort: options.abort
            };
        // Cool Hack from 2016-09-26
        if (options.src.indexOf('&format=zip') >= 0) {
            var newJob = new ZipJob( this.viaGL, jobOptions );
        }
        else {
            var newJob = new ImageJob( jobOptions );
        }

        if ( !this.jobLimit || this.jobsInProgress < this.jobLimit ) {
            newJob.start();
            this.jobsInProgress++;
        }
        else {
            this.jobQueue.push( newJob );
        }
    },

    /**
     * Clear any unstarted image loading jobs from the queue.
     * @method
     */
    clear: function() {
        for( var i = 0; i < this.jobQueue.length; i++ ) {
            var job = this.jobQueue[i];
            if ( typeof job.abort === "function" ) {
                job.abort();
            }
        }

        this.jobQueue = [];
    }
};

/**
 * Cleans up ImageJob once completed.
 * @method
 * @private
 * @param loader - ImageLoader used to start job.
 * @param job - The ImageJob that has completed.
 * @param callback - Called once cleanup is finished.
 */
function completeJob( loader, job, callback ) {
    var nextJob;

    loader.jobsInProgress--;

    if ( (!loader.jobLimit || loader.jobsInProgress < loader.jobLimit) && loader.jobQueue.length > 0) {
        nextJob = loader.jobQueue.shift();
        nextJob.start();
        loader.jobsInProgress++;
    }

    callback( job.image, job.errorMsg );
};
