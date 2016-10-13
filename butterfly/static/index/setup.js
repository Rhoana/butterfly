log = console.log.bind(window.console);
//-----------------------------------
//
// DOJO.Setup: request data from server
// -- Made by main.js
//-----------------------------------

DOJO.Setup = function(api){
  this.parse = api.parse;
  this.write = new DOJO.Write(this);
  this.loaded = this.ask.reduce(this.loader.bind(this),this.start(''));
  Promise.all(this.loaded).then(function(sources){
    log(sources.pop());
  });
}

DOJO.Setup.prototype = {
  ask: [
    'experiment','sample',
    'dataset','channel',
    'channel_metadata'
  ],
  start: function(old){
    return [Promise.resolve([{old:old}])];
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
    if (str.substr(-4) != 'data'){
      str += 's';
    }
    return str;
  },
  argue: function(hash){
    var argument = hash.old? hash.old+'&': '';
    delete hash.old;
    for (var key in hash) {
      argument += key + '=';
      argument += hash[key]+'&';
    }
    return argument.slice(0,-1);
  },
  find: function(kind,hash){
    var where = this.plural(kind)+'?'+this.argue(hash);
    return this.get('/api/' + where);
  },
  draw: function(kind,result) {
    var hashes = [];
    var [out,old] = [result.out,result.old];
    var hash = (kind !== this.ask[0])? {old: old}: {};
    var list = this.write.list.bind(this.write,kind);
    var link = this.write.link.bind(this.write,kind);
    if (out instanceof Array){
      for (folder of out){
        var temp = this.share(hash,{});
        temp[kind] = folder;
        hashes.push(list(temp));
      }
      return hashes;
    }
    out = this.share(out,this.parse(old));
    out.old = old;
    return [link(out)];
  },
  map: function(arr,kind,fn){
    return arr.map(this[fn].bind(this,kind));
  },
  loader: function(pending,kind){
    map = this.map.bind(this);
    var find = function(arr){
      return Promise.all(map(arr,kind,'find'));
    };
    var draw = function(arr){
      var cat = [].concat.apply.bind([].concat);
      return map(arr,kind,'draw').reduce(cat,[]);
    };
    return pending.map(function(prom){
      return prom.then(find).then(draw);
    });
  }
}