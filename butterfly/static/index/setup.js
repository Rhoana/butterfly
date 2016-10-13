log = console.log.bind(window.console);
//-----------------------------------
//
// DOJO.Setup: request data from server
// -- Made by main.js
//-----------------------------------

DOJO.Setup = function(api){
  this.parse = api.parse;
  var go = Promise.resolve([{}]);
  var loader = this.loader.bind(this);
  var loaded = this.ask.reduce(loader,[go]);
  this.write = new DOJO.Write(this);
  Promise.all(loaded).then(function(sources){
    log(sources)
  });
}

DOJO.Setup.prototype = {
  ask: [
    'experiment',
    'sample',
    'dataset',
    'channel',
    'channel_metadata'
  ],
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
    argument = '?';
    if ('old' in hash){
        argument += hash.old + '&';
        delete hash.old;
    }
    for (var key in hash) {
      argument += key + '=';
      argument += hash[key] + '&'
    }
    return argument.slice(0,-1);
  },
  // Map a bound method
  map: function(kind,fn,arr){
    return arr.map(this[fn].bind(this,kind));
  },
  find: function(kind,hash){
    var where = this.plural(kind)+this.argue(hash);
    return this.get('/api/' + where);
  },
  mapfind: function(kind,arr){
    return Promise.all(this.map(kind,'find',arr));
  },
  draw: function(kind,result) {
    var hashes = [];
    var [out,old] = [result.out,result.old];
    var hash = 0!= old.indexOf('/api')? {old: old}:{};
    if (out instanceof Array){
      for (folder of out){
        var temp = this.share(hash,{});
        temp[kind] = folder;
        hashes.push(temp);
//        log(temp)
      }
      return hashes;
    }
    out.source = this.parse(old);
    return [out];
  },
  mapdraw: function(kind,arr){
    var cat = [].concat.apply.bind([].concat);
    return this.map(kind,'draw',arr).reduce(cat,[]);
  },
  loader: function(pending,kind){
    var find = this.mapfind.bind(this,kind);
    var draw = this.mapdraw.bind(this,kind);
    return pending.map(function(prom){
      return prom.then(find).then(draw);
    });
  }
}