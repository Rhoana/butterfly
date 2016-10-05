//-----------------------------------
//
// DOJO.Source: makes tileSources
// -- Made & Init by DOJO.Stack
//-----------------------------------

DOJO.Source = function(src_terms){
    this.glflag = Number(src_terms.gl) || 0;
    // Change the default source terms
    this.tileSource = this.share(src_terms, this.tileSource);
}

DOJO.Source.prototype = {
    init: function(src_terms){
        var sourcer = this.share(this.tileSource,{});
        var source = this.share(src_terms, sourcer);
        var maxLevel = source.width/source.tileSize;
        source.maxLevel = Math.ceil(Math.log2(maxLevel));
        // Get the segmentation string for butterfly
        if (source.segmentation) {
            source.seg = '&segmentation=y&'+this.segmentFormats[this.glflag];
        }
        return {tileSource: source};
    },
    segmentFormats: ['segcolor=y','output=zip'],
    tileSource: {
        z: 0,
        seg: '',
        minLevel: 0,
        width: 8192,
        height: 8192,
        tileSize: 512,
        server: 'localhost:2001',
        datapath: '/Volumes/NeuroData/cylindojo/mojo',
        getTileUrl: function( level, x, y ) {
            var width = this.getTileWidth(level);
            var height = this.getTileHeight(level);
            return 'http://' + this.server + '/data/?datapath=' +
                this.datapath + '&start=' + x*width + ',' + y*height + ',' +
                this.z + '&mip=' + (this.maxLevel - level) + '&size=' +
                width + ',' + height + ',' + 1 + this.seg;
        }
    },
    share: function(from, to) {
        for (var key in from) {
           to[key] = from[key];
        }
        return to;
    }
};