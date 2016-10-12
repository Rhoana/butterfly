log = console.log.bind(window.console);
//-----------------------------------
//
// DOJO.Config: request data from server
// -- Made by main.js
// -- Init by main.js
//-----------------------------------

DOJO.Config = function(src_terms){
  var api = this.api.bind(this);
  var go = Promise.resolve([{}]);
  a = [0,1,2,3,4].reduce(api,[go]);
}

DOJO.Config.prototype = {
  // Get a file as a promise
  get: function(where) {
      log(where)
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
  ask: [
    'experiment',
    'sample',
    'dataset',
    'channel',
    'channel_metadata'
  ],
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
  find: function(kind,hash){
    return this.get('/api/'+this.plural(kind)+this.argue(hash));
  },
  finds: function(kind,hashes){
        log('')
    log(hashes)
    return Promise.all(hashes.map(this.find.bind(this,kind)));
  },
  draw: function(kind,result) {
    if (result.out instanceof Array){
      var hashes = []
      for (folder of result.out){
        var hash = {};
        hash[kind] = folder;
        if(result.old.indexOf('/')){
          hash.old = result.old;
        }
        hashes.push(hash);
      }
      return hashes;
    }
    return result.out;
  },
  draws: function(kind,result) {
    hashes = result.map(this.draw.bind(this,kind)).reduce(function(all,one){
      return all.concat(one);
    },[]);
    log(hashes)
    return hashes;
  },
  api: function(pending,now){
    return pending.map(function(prom,id){
      var kind = this.ask[now]
      var finds = this.finds.bind(this,kind);
      var draws = this.draws.bind(this,kind);
      return prom.then(finds).then(draws);
    },this);
  }
}