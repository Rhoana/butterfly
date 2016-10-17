//-----------------------------------
//
// DOJO.Write: write data to HTML
// -- Made by DOJO.Setup
//-----------------------------------

DOJO.Write = function(setup){
  this.ask = setup.ask;
  this.hash = setup.hash;
  this.share = setup.share;
}
DOJO.Write.prototype = {
  totalIds: 0,
  copy: function(id,i){
    return document.getElementById(id).children[i].cloneNode(1);
  },
  chan: new RegExp('(seg|id).*', 'i'),
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
      var path = [
        ['id', 'in'+id],
        ['for', 'in'+id],
        ['id', source.now]
      ];
      path.forEach(function(tag,tagi){
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
      var [w,h,d] = [size.x,size.y,size.z];
      var matchID = Number(this.chan.test(source.name));
      var path = 'viz.html?datapath='+source.path+'&width='+w+'&height='+h;
      cousin.children[0].href = path+ (['','&id'][matchID]);
      cousin.children[1].innerHTML = source['data-type'];
      uncle.children[1].innerHTML = [w,h,d].join(', ');
      uncle.children[0].href = path+'&overlay';
      grandparent.children[0].checked = false;
      ancestor.children[0].checked = false;
      var path = [
        ['name', source['short-description']],
        ['path', source.path]
      ]
      path.forEach(function(items){
        var temp = this.copy('proto',2);
        var info = this.grandkid(temp,[0,0]);
        info.children[0].innerHTML = items[0];
        info.children[1].innerHTML = items[1];
        parent.appendChild(temp);
      },this);
  },
  main: function(terms){
    var source = this.share(terms,{now:this.hash(terms)});
    var parent = document.getElementById(source.old || this.ask[0]);
    var cousin = this.grandkid(parent.parentElement,[1,1]);
    this[source.target](source,parent,cousin);
    return terms;
  }
}