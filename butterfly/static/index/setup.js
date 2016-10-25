log = console.log.bind(window.console);
//-----------------------------------
//
// DOJO.Setup: request data from server
// -- Made by main.js
//-----------------------------------

DOJO.Setup = function(api){
  this.parse = api.parse;
  this.write = new DOJO.Write(this);
  this.loaded = this.start('');

  this.loaded.then(function(h){
//      log(h)
  });
}

DOJO.Setup.prototype = {
  ask: [
    'experiment','sample',
    'dataset','channel',
    'channel_metadata'
  ],
  start: function(old){
    var temp = Promise.resolve([{old:old,out:['']}]);
    return this.ask.reduce(this.loader.bind(this),temp);
  },
  // Copy an object
  share: function(from, to) {
    for (var key in from) {
      to[key] = from[key];
    }
    return to;
  },
  // Get a file as a promise
  get: function(where) {
    var win = function(bid){
      if (bid.status == 200) {
        var json = JSON.parse(bid.response);
        var target = where.split('?').pop();
        return this({out:json,old:target});
      }
      console.log('error loading')
    };
    return new Promise(function(done){
      var bid = new XMLHttpRequest();
      bid.onload = win.bind(done,bid);
      bid.open('GET', where, true);
      bid.send();
    });
  },
  plural: function(str){
    return (str + 's').replace(/datas$/,'data');
  },
  hash: function(hash){
    var now = hash.old+'&';
    now = now.replace(/^&/,'');
    if(hash.kind && hash.name){
      now += hash.kind+'='+hash.name;
    }
    return now;
  },
  build: function(hash,sources){
    var terms = sources.reduce(this.share,hash);
    return this.write.main(terms);
  },
  draw: function(kind,result,i) {
    var [out,old] = [result.out,result.old];
    var hash = {old: old, kind:kind};
    if (out instanceof Array){
      return out.map(function(name){
        var sources = [{target:'head',name:name}];
        sources.push({length:result.out.length});
        return this.build(hash,sources);
      },this);
    }
    var sources = [{target:'body'},this.parse(old),out];
    return this.build(hash,sources);
  },
  find: function(kind,hash,i){
    var where = this.plural(kind)+'?'+this.hash(hash);
    return this.get('/api/' + where);
  },
  map: function(arr,kind,fn){
    return arr.map(this[fn].bind(this,kind));
  },
  loader: function(pending,kind,depth){
    map = this.map.bind(this);
    var find = function(arr){
      return Promise.all(map(arr,kind,'find'));
    };
    var draw = function(arr){
      var cat = [].concat.apply.bind([].concat);
      return map(arr,kind,'draw').reduce(cat,[]);
    };
    return pending.then(find).then(draw);
  }
}