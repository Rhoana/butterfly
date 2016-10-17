//-----------------------------------
//
// DOJO.Write: write data to HTML
// -- Made by DOJO.Setup
//-----------------------------------

DOJO.Write = function(setup){
  this.ask = setup.ask;
  this.argue = setup.argue;
  this.share = setup.share;
}
DOJO.Write.prototype = {
  totalIds: 0,
  channels: {
    'img':'',
    'ids':'&id'
  },
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
  head: function(source){
      var parent = document.getElementById(source.old);
      var grandparent = parent.parentElement;
      var cousin = this.grandkid(grandparent,[1,1]);

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
      parent.appendChild(self);
      offspring.children[0].innerHTML = source.name;
      cousin.children[1].innerHTML = source.length;
  },
  body: function(source){
      var parent = document.getElementById(source.old);
      var grandparent = parent.parentElement;
      var cousin = this.grandkid(grandparent,[1,1]);

      var ancestor = this.grandparent(grandparent);
      var uncle = this.grandkid(ancestor,[1,1]);
      var [w,h,d] = [source.dimensions.x,source.dimensions.y,source.dimensions.z];
      var path = 'viz.html?datapath='+source.path+'&width='+w+'&height='+h;
      cousin.children[0].href = path+this.channels[source.name];
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
    var source = this.share(terms,{now:this.argue(terms)});
    source.old = source.old || this.ask[0];
    this[source.target](source);
    return terms;
  }
}