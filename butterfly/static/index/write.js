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
  copy: function(id){
    return document.getElementById(id).cloneNode(1);
  },
  grandkid: function(el){
    return el.children[1].children[1];
  },
  head: function(source){
      var self = this.copy('path');
      var parent = document.getElementById(source.old);
      var cousin = this.grandkid(parent.parentElement);
      var offspring = this.grandkid(self);
      self.removeAttribute('id');
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
      var cousin = this.grandkid(parent.parentElement);
      var ancestor = parent.parentElement.parentElement.parentElement;
      var uncle = this.grandkid(ancestor);
      var [w,h,d] = [source.dimensions.x,source.dimensions.y,source.dimensions.z];
      var path = 'viz.html?datapath='+source.path+'&width='+w+'&height='+h;
      cousin.children[0].href = path+this.channels[source.name];
      cousin.children[1].innerHTML = source['data-type'];
      uncle.children[1].innerHTML = [w,h,d].join(', ');
      uncle.children[0].href = path+'&overlay';
      ancestor.children[0].checked = false;
  },
  main: function(terms){
    var source = this.share(terms,{now:this.argue(terms)});
    source.old = source.old || this.ask[0];
    this[source.target](source);
    return terms;
  }
}