print = console.log

function openWorld(e_add){
  // Record when the loaded state changes
  function loadChange(e_load){
    // If the tiles are loaded at full resolution
    if (e_load.fullyLoaded) {
      // Get the image and the source
      full_image = e_load.eventSource;
      full_source = full_image.source;
      // Increase the minimum zoom level
      print([full_source.minLevel, full_source.maxLevel])
      full_source.minLevel += 1;
      // Send the data and reload the page if at highest resolution
      if (full_source.minLevel == full_source.maxLevel){
        // Reload the page
        var newPage = function(){
          if (reboot.readyState == XMLHttpRequest.DONE ) {
            if (reboot.status == 200) {
              print(reboot.responseText)
              // Reload the page
              window.location.reload(true);
            }
          }
        }
        // Reconfigure the server
        var reboot = new XMLHttpRequest();
        reboot.onreadystatechange = newPage;
        reboot.open("GET", "reboot", true);
        reboot.send();
      }
    }
    // Send the data and reload the page
    else {
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
  // Start the OpenSeadragon
  window.osd = OpenSeadragon({
    id:	tile_id,
    prefixUrl: "icons/",
    showNavigationControl: true,
    minPixelRatio: 0,
    tileSources: {
      minLevel: 0,
      height: get_var('h'),
      width:  get_var('w'),
      tileSize: get_var('tile'),
      maxLevel: get_var('level'),
      getTileUrl: function( level, x, y ){
            return "/tile/?scale=" + (this.maxLevel - level) 
            + "&y=" + y + "&x=" + x;
      }
    }
  });
  // Get the resulting tiled image
  osd.world.addHandler('add-item', openWorld);
}
window.onload = main;
