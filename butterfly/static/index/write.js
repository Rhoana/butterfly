//-----------------------------------
//
// DOJO.Write: write data to HTML
// -- Made by DOJO.Setup
//-----------------------------------

DOJO.Write = function(setup){
  this.argue = setup.argue;
  this.ask = setup.ask;
//  [0,1,2,3,4,5,6,7,8,9,10,11,12].map(this.experiment,this);
}
DOJO.Write.prototype = {
  basic: function(kind,folder){
    var name = folder[kind];
    var id = kind+'='+name;
    var label = kind+' '+name;
    return {
      input: {
        innerHTML: '',
        tags:[
          ['id',name],
          ['type','checkbox']
        ]
      },
      label: {
        innerHTML: label,
        tags: [
          ['for',name]
        ]
      },
      section: {
        innerHTML: 'Content for '+label,
        tags: [['id',id]]
      }
    };
  },
  keys: ['input','label','section'],
  build: function(parent,basic,kind){
    var el = document.createElement(kind);
    var preset = basic[kind];
    var set = el.setAttribute;
    el.innerHTML = preset.innerHTML;
    preset.tags.map(set.apply.bind(set,el));
    document.getElementById(parent).appendChild(el);
  },
  dom: function(kind,folder){
    if (folder.old !== ''){
//        log(folder.old)
    }
    else{
//      log('hi')
      var basic = this.basic(kind,folder);
      var build = this.build.bind(this,'experiments',basic);
      this.keys.map(build);
    }
//    var build = this.build.bind(this,'experiments',id);
  }
}