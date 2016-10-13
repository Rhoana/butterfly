//-----------------------------------
//
// DOJO.Write: write data to HTML
// -- Made by DOJO.Setup
//-----------------------------------

DOJO.Write = function(setup){
  this.argue = setup.argue;
  this.share = setup.share;
  this.ask = setup.ask;
//  [0,1,2,3,4,5,6,7,8,9,10,11,12].map(this.experiment,this);
}
DOJO.Write.prototype = {
  basic: function(fold,kind,self){
    var label = kind+' '+fold[kind];
    var id = self.replace('=','-');
    return {
      input: {
        innerHTML: '',
        tags:[
          ['id',id],
          ['type','checkbox']
        ]
      },
      label: {
        innerHTML: label,
        tags: [
          ['for',id]
        ]
      },
      section: {
        innerHTML: '',
        tags: [['id',self]]
      }
    };
  },
  keys: ['input','label','section'],
  build: function(parent,basic,kind){
    parent = parent || 'experiments';
    var el = document.createElement(kind);
    var preset = basic[kind];
    var set = el.setAttribute;
    el.innerHTML = preset.innerHTML;
    preset.tags.map(set.apply.bind(set,el));
    document.getElementById(parent).appendChild(el);
  },
  dom: function(kind,folder){
    var fold = this.share(folder,{old: ''});
    var [parent,self] = [fold.old,this.argue(fold)];
    var basic = this.basic(fold,kind,self);
    var build = this.build.bind(this,parent,basic);
    this.keys.map(build)
    log(parent)
    log(self)
    log('')
//    var build = this.build.bind(this,parent,basic);
  }
}