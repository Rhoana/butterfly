//-----------------------------------
//
// DOJO.Write: write data to HTML
// -- Made by DOJO.Setup
//-----------------------------------

DOJO.Write = function(setup){
  this.argue = setup.argue;
  this.share = setup.share;
  this.html = new DOMParser();
  this.max = setup.ask.length;
  this.ask = setup.ask;
}
DOJO.Write.prototype = {
  range: function(end){
    return Object.keys(new Uint8Array(end)).map(Number);
  },
  parent: function(el){
      return el.slice(0,el.lastIndexOf('&'));
  },
  unstring: function(target){
      return target.el.split('&').pop().split(target.char);
  },
  meta: function(target){
    info = {}
    var query = target.query || 'size';
    var size = JSON.stringify(target.dimensions);
    var field = target['short-description'];
    if(target.field){
      field = target[target.field]
    }
    info.size = size.replace(/[{"}]/g,' ').replace(/\s:/g,':');
    info.format = ' '+target['data-type'];
    return [field,info[target.query]];
  },
  targets: {
    head: [{
        template:'lists'
    },
    {
        maxdraw: 1,
        template:'lengths',
        char: '+'
    }],
    body: [{
        template:'links',
        char: '+'
      },
      {
        maxdraw: 1,
        template:'links',
        field: 'dataset',
        query: 'size',
        char: '+',
        back: 1
    }]
  },
  lists: function(target){
    var self = this.argue(target);
    var labid = self.replace(/=/g,'+');
    var id = self.replace(/=/g,'-');
    return {
      input: {
        tags:[
          ['id',id],
          ['type','checkbox']
        ]
      },
      label: {
        tags: [
          ['for',id],
          ['id',labid]
        ]
      },
      section: {
        tags: [['id',self]]
      },
      elems: ['input','label','section']
    };
  },
  links: function(target){
    var [link,info] = this.meta(target);
    var path = 'viz.html?datapath='+target.path;
    return {
      a: {
        innerHTML: link+ ':',
        tags:[['href',path]]
      },
      svg: {
        innerHTML: '<path d="M 0,4 L 3,7 L 6,4"/>'
      },
      span: {
        innerHTML: info
      },
      elems: ['svg','a','span']
    };
  },
  lengths: function(target){
    var index = this.ask.indexOf(target.kind);
    var parentName = this.unstring(target).pop();
    if(index==0 || this.max<index+3) {
      return {elems:[]};
    }
    return {
      svg: {
        innerHTML: '<path d="M 0,4 L 3,7 L 6,4"/>'
      },
      b: {
        innerHTML: parentName +': '
      },
      span: {
        innerHTML: ' ('+target.length +') '
      },
      elems: ['svg','b','span']
    };
  },
  build: function(target,elem){
    if (target.parent && target.source){
      var el = document.createElement(elem);
      if (elem == 'svg'){
          el = document.getElementById('icon').cloneNode(1);
      }
      var preset = target.source[elem];
      if(preset){
        var set = el.setAttribute;
        el.innerHTML = preset.innerHTML || '';
        (preset.tags||[]).map(set.apply.bind(set,el));
        target.parent.appendChild(el);
      }
    }
  },
  template: function(target){
    if(!target.maxdraw || target.maxdraw > target.num){
        target.source = this[target.template](target);
        var build = this.build.bind(this,target);
        target.source.elems.map(build,this);
    }
  },
  write: function(target){
    var parent = target.el || this.ask[0];
    target.parent = document.getElementById(parent);
    this.template(target);
  },
  sections: function(source,target){
    var ran = this.range(target.back||0);
    var el = ran.reduce(this.parent,source.old);
    return this.share(source,{
      query: target.query || 'format',
      el: el.replace(/=/g, target.char||'='),
      field: target.field || false,
      template: target.template,
      maxdraw: target.maxdraw,
      char: target.char || '='
    });
  },
  main: function(terms){
    var source = this.share(terms,{old: ''});
    var section = this.sections.bind(this,source);
    this.targets[terms.target].map(section).map(this.write,this);
    return terms;
  }
}