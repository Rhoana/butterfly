//-----------------------------------
//
// DOJO.Write: write data to HTML
// -- Made by DOJO.Setup
//-----------------------------------

DOJO.Write = function(setup){
  this.share = setup.share;
}
DOJO.Write.prototype = {
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
    var self = this.copy('proto',0);
    var offspring = this.grandkid(self,[1,1]);
    var id = this.totalIds++;
    var factsheet = [
      ['id', 'in'+id],
      ['for', 'in'+id],
      ['id', source.self]
    ];
    factsheet.forEach(function(tag,tagi){
      var temp = self.children[tagi];
      temp.setAttribute.apply(temp,tag);
    });
    self.children[0].checked = true;
    parent.appendChild(self);
    offspring.children[0].innerHTML = source.name;
    cousin.children[1].innerHTML = source.length;
  },
  body: function(source,parent,cousin){
    var grandparent = this.grandparent(cousin);
    var ancestor = this.grandparent(grandparent);
    var uncle = this.grandkid(ancestor,[1,1]);
    var size = source.dimensions;
    var dtype = source['data-type'];
    var withGL = Number(dtype!='uint8');
    var [w,h,d] = [size.x,size.y,size.z];
    var channel = withGL + source.channel;
    var path = 'viz.html?depth='+d+'&width='+w+'&height='+h;
    var old = source.old.replace(/&channel=(\w+)/,'&channel='+channel);;
    cousin.children[0].href = path + '&' + old;
    if (uncle.children[0].href) {
      uncle.children[0].href += ',' + channel;
    }
    else {
      uncle.children[0].href = path;
    }
    cousin.children[1].innerHTML = dtype;
    uncle.children[1].innerHTML = [w,h,d].join(', ');
    grandparent.children[0].checked = false;
    ancestor.children[0].checked = false;
    var factsheet = [
      ['description', source['short-description'] || source['name']],
      ['datasource', source.datasource || 'unknown'],
      ['path', source.path || 'unknown']
    ]
    factsheet.forEach(function(items){
      var temp = this.copy('proto',2);
      var info = this.grandkid(temp,[0,0]);
      info.children[0].innerHTML = items[0];
      info.children[1].innerHTML = items[1];
      parent.appendChild(temp);
    },this);
  },
  main: function(terms){
    var source = this.share(terms,{self:terms.self.join(',')});
    var parent = document.getElementById(terms.parent.join(',') || '0');
    var cousin = this.grandkid(parent.parentElement,[1,1]);
    this[source.target](source,parent,cousin);
    return terms;
  }
}
