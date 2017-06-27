print = console.log

function openWorld(e_add){
  // Record starting time
  var t0 = performance.now();
  // Record when the loaded state changes
  function loadChange(e_load){
    // If the tiles are loaded at full resolution
    if (e_load.fullyLoaded) {
      // Record time of full load
      var t1 = performance.now();
      var load_time = Math.floor(t1 - t0).toString();
      // Get the image and the source
      var full_image = e_load.eventSource;
      var full_source = full_image.source;
      // Reload the page
      var newPage = function(){
        if (reboot.readyState == XMLHttpRequest.DONE ) {
          if (reboot.status == 200) {
            // Reload if instructed
            var command = reboot.responseText
            if (command == "continue") {
              // Reload the page
              window.location.reload(true);
            }
          }
        }
      }
      // Reconfigure the server
      var reboot = new XMLHttpRequest();
      reboot.onreadystatechange = newPage;
      // Send the time until fully loaded
      var request = "reboot?time="+load_time;
      reboot.open("GET", request, true);
      print (request)
      reboot.send();
    }
  }
  // Get the full image
  e_add.item.addHandler('fully-loaded-change', loadChange);
}

function main(){
  // Get variables from HTML
  var tile_id = "tilesource";
  var tile_el = document.getElementById(tile_id);
  // Variable getting function
  function get_var (s){
    return Number(tile_el.getAttribute(s));
  }
  // Get the number for preload flags
  var should_hide = Number(get_var('hide'))
  // Start the OpenSeadragon
  window.osd = OpenSeadragon({
    id:	tile_id,
    prefixUrl: "icons/",
    showNavigationControl: true,
    minPixelRatio: 0,
    tileSources: {
      minLevel: 0,
      preload: true,
      height: get_var('h'),
      width:  get_var('w'),
      tileSize: get_var('tile'),
      maxLevel: get_var('level'),
      opacity: !!(should_hide),
      getTileUrl: function( level, x, y ){
            // Get a random number
            var rando = String(Math.floor(Math.random()*10**14));
            // Make the request
            return "/tile/?scale=" + (this.maxLevel - level) 
            + "&y=" + y + "&x=" + x + "&r=" + rando;
      }
    }
  });
  // Get the resulting tiled image
  osd.world.addHandler('add-item', openWorld);
}
window.onload = main;
