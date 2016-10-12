log = x => console.log(x);
//-----------------------------------
//
// DOJO.Config: request data from server
// -- Made by main.js
// -- Init by main.js
//-----------------------------------

DOJO.Config = function(src_terms){
  var api = this.api.bind(this);
  var go = Promise.resolve({});
  [0,1,2,3,4].reduce(api,go);
}

DOJO.Config.prototype = {
  // Get a file as a promise
  get: function(where) {
      var win = function(bid){
          if (bid.status == 200) {
              var json = JSON.parse(bid.response);
              var target = where.split('?').pop();
              return this({out:json,at:target});
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
  api: function(pending,now){
    var kind = this.ask[now]
    var find = this.find.bind(this,kind);
    return pending.then(find).then(function(ready) {
       var next_now = {};
       log(kind);
       log(ready.at);
       log(ready.out);
       if (now) {
          next_now.old = ready.at;
       }
       next_now[kind] = ready.out[0];
       return next_now;
    }.bind(this));
  }
}