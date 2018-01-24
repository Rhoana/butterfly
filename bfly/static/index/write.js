//-----------------------------------
//
// window.DOJO.Write: write data to HTML
// -- Made by window.DOJO.Setup
//-----------------------------------

window.DOJO.Write = function(setup){
  this.share = setup.share;
  this.parse = setup.parse;
};
window.DOJO.Write.prototype = {
  totalIds: 0,
  copy: function(id,i){
    return document.getElementById(id).children[i].cloneNode(1);
  },
  grandparent: function(el){
    return el.parentElement.parentElement;
  },
  grandkid: function(el,A){
    return A.reduce(function(el,i){
      return el.children[i];
    },el);
  },
  head: function(source,parent,cousin){
    var self = this.copy("proto",0);
    var offspring = this.grandkid(self,[1,1]);
    var id = this.totalIds++;
    var factsheet = [
      ["id", "in"+id],
      ["for", "in"+id],
      ["id", source.self]
    ];
    factsheet.forEach(function(tag,tagi){
      var temp = self.children[tagi];
      temp.setAttribute.apply(temp,tag);
    });
    self.children[0].checked = true;
    parent.appendChild(self);
    offspring.children[0].innerText = source.name;
    cousin.children[1].innerText = source.length;
  },
  ng_host: function() {
    // NEUROGLANCER HOSTNAME 
    var query = this.parse(location.search.substring(1));
    if (typeof query.host === 'number') {
      return location.hostname +':'+ query.host;
    }
    else if (typeof query.host === 'string') {
      return query.host; 
    }
    return location.host;
  },
  ng_channel: function(source){
    var channel = source.channel;
    var ng_type = 'segmentation';
    if (source['data-type'].match(/float|uint8/)) {
      ng_type = 'image';
    }
    var host = this.ng_host();
    if (host.slice(0,4) != 'http') {
      host = location.protocol+'//'+host;
    }
    // By current butterfly convention
    var old_values = source.old.map(function(x) {
      return x.split('=').pop();
    });
    var token = old_values.slice(0, -1).join('::');
//  var path = 'ndstore://'+host+'/'+token+'/'+channel;
    var path = 'precomputed://'+host+'/pre/'+token+'/'+channel;
    return {
      key: channel,
      value: {
        type: ng_type,
        source: path,
      }
    }
  },
  ng_path: function(old_path, next){
    var new_spec = {
      layers: {},
      layout: 'xy',
    };
    if (old_path) {
      var old_hash = old_path.split('ng/#!').pop();
      new_spec = JSON.parse(old_hash);
    }
    new_spec.layers[next.key] = next.value;
    return 'ng/#!'+JSON.stringify(new_spec);
  },
  body: function(source,parent,cousin){
    var grandparent = this.grandparent(cousin);
    var ancestor = this.grandparent(grandparent);
    var uncle = this.grandkid(ancestor, [1, 1]);
    var size = source.dimensions;

    // Get all details for current channel
    var [w,h,d] = [size.x, size.y, size.z];
    var new_item = this.ng_channel(source);
    // Get current and group elements
    var current = cousin.children
    var group = uncle.children

    // Add link and data to the newest channel
    var current_url = this.ng_path('', new_item);
    current[0].setAttribute("href", current_url);
    current[1].innerText = source['data-type'];

    // Add newest channel to containing group
    var group_url = this.ng_path(group[0].href, new_item);
    group[0].setAttribute("href", group_url);
    group[1].innerText = [w,h,d].join(", ");

    // Close all containing checkboxes
    grandparent.children[0].checked = false;
    ancestor.children[0].checked = false;
    // Give the flavor-text for each itex
    var factsheet = [
      ["description", source["short-description"] || source["name"]],
      ["datasource", source["source-type"] || "unknown"],
      ["path", source.path || "unknown"]
    ];
    factsheet.forEach(function(items){
      var temp = this.copy("proto",2);
      var info = this.grandkid(temp,[0,0]);
      info.children[0].innerText = items[0];
      info.children[1].innerText = items[1];
      parent.appendChild(temp);
    }, this);
  },
  main: function(terms){
    var source = this.share(terms,{self:terms.self.join(",")});
    var parent = document.getElementById(terms.parent.join(",") || "0");
    var cousin = this.grandkid(parent.parentElement,[1,1]);
    this[source.target](source,parent,cousin);
    return terms;
  }
};
