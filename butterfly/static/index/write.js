//-----------------------------------
//
// DOJO.Write: write data to HTML
// -- Made by DOJO.Setup
//-----------------------------------

DOJO.Write = function(setup){
  this.argue = setup.argue;
  this.share = setup.share;
  this.ask = setup.ask;
}
DOJO.Write.prototype = {
  written: {
    false: true
  },
  range: function(end){
    return Object.keys(new Uint8Array(end)).map(Number);
  },
  parent: function(el){
      return el.slice(0,el.lastIndexOf('&'));
  },
  meta: function(target){
    info = {}
    var query = target.query || 'size';
    var size = JSON.stringify(target.folder.dimensions);
    var name = target.name || target.folder['short-description'];
    info.size = size.replace(/[{"}]/g,' ').replace(/\s:/g,':');
    info.format = ' '+target.folder['data-type'];
    return [name,info[target.query]];
  },
  k: {
    lists: [{}],
    links: [{
        char: '+',
      },
      {
        field: 'dataset',
        query: 'size',
        char: '+',
        back: 1,
    }]
  },
  lists: function(target){
    var self = this.argue(target.folder);
    var labid = self.replace('=','+');
    var id = self.replace('=','-');
    return {
      input: {
        tags:[
          ['id',id],
          ['type','checkbox']
        ]
      },
      label: {
        innerHTML: 'h',
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
    return {
      a: {
        innerHTML: link+ ':',
        tags:[['href','viz.html']]
      },
      span: {
        innerHTML: info,
        tags:[]
      },
      elems: ['a','span']
    };
  },
  sections: function(fold,target){
    var ran = this.range(target.back||0);
    var el = ran.reduce(this.parent,fold.old);
    return {
      query: target.query || 'format',
      el: el.replace('=', target.char||'='),
      name: target.field? fold[target.field] : false,
      folder: fold,
    };
  },
  names: [false,'dataset'],
  queries: ['format','size'],
  build: function(target,kind){
    var parent = target.el || 'experiments';
    var el = document.createElement(kind);
    var preset = target.source[kind];
    var set = el.setAttribute;
    el.innerHTML = preset.innerHTML || '';
    preset.tags.map(set.apply.bind(set,el));
    document.getElementById(parent).appendChild(el);
  },
  write: function(target,format){
    target.field
    if (target.name in this.written){
      target.source = this[format](target);
      var build = this.build.bind(this,target);
      target.source.elems.map(build);
    }
    this.written[target.name] = true;
  },
  list: function(kind,folder){
    var fold = this.share(folder,{old: ''});
    var heading = this.sections(fold,this.k.lists[0]);
    this.write(heading,'lists');
    return folder;
  },
  link: function(kind,folder){
    var fold = this.share(folder,{old: ''});
    var channel = this.sections(fold,this.k.links[0]);
    var dataset = this.sections(fold,this.k.links[1]);
    this.write(channel,'links');
    this.write(dataset,'links');
    return folder;
  }
}