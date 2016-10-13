//-----------------------------------
//
// DOJO.Write: write data to HTML
// -- Made by DOJO.Setup
//-----------------------------------

DOJO.Write = function(setup){
  this.setup = setup;
  [0,1,2,3,4,5,6,7,8,9,10,11,12].map(this.experiment,this);
}
DOJO.Write.prototype = {
  keys: ['input','label','section'],
  basic: function(id){
    return {
      input: {
        innerHTML: '',
        tags:[
          ['id','experiment'+id],
          ['type','checkbox']
        ]
      },
      label: {
        innerHTML: 'Experiment '+id,
        tags: [
          ['for','experiment'+id]
        ]
      },
      section: {
        innerHTML: 'Content for Experiment '+id,
        tags: []
      }
    };
  },
  build: function(parent,id,kind){
    var el = document.createElement(kind);
    var preset = this.basic(id)[kind];
    var set = el.setAttribute;
    el.innerHTML = preset.innerHTML;
    preset.tags.map(set.apply.bind(set,el));
    document.getElementById(parent).appendChild(el);
  },
  experiment: function(id){
    var build = this.build.bind(this,'api',id);
    this.keys.map(build);
  }
}