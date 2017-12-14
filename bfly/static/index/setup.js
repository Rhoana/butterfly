//log = console.log.bind(window.console);
//-----------------------------------
//
// window.DOJO.Setup: request data from server
// -- Made by main.js
//-----------------------------------

window.DOJO.Setup = function(api){
  this.parse = api.parse;
  this.write = new window.DOJO.Write(this);
  var allData = this.start([]);
  allData.then(function(all){
//    log(all)
  });
};

window.DOJO.Setup.prototype = {
  ask: [
    "experiment","sample",
    "dataset","channel",
    "channel_metadata"
  ],
  start: function(old){
    return this.loader(["root"],{old:old},0);
  },
  // Copy an object
  share: function(from, to) {
    for (var key in from) {
      if (from.hasOwnProperty(key)) {
        to[key] = from[key];
      }
    }
    return to;
  },
  // Get a file as a promise
  get: function(where) {
    var win = function(bid){
      if (bid.status === 200) {
        var json = JSON.parse(bid.response);
        var target = where.split("?").pop();
        var old = target.split('&').filter(function(x){
            return (x !== '');
        });
        return this({out:json, old:old});
      }
      //console.log("error loading");
    };
    return new Promise(function(done){
      var bid = new XMLHttpRequest();
      bid.onload = win.bind(done,bid);
      bid.open("GET", where, true);
      bid.send();
    });
  },
  plural: function(str){
    return (str + "s").replace(/datas$/,"data");
  },
  hash: function(hash){
    var now = hash.old.slice();
    if(hash.kind && hash.name){
      now.push(hash.kind+"="+hash.name);
    }
    return now.join('&');
  },
  build: function(hash,sources){
    hash.kind = this.ask[hash.depth];
    var terms = sources.reduce(this.share,hash);
    return this.write.main(terms);
  },
  draw: function(parent, depth, result) {
    var constant = {
      old: result.old,
      depth: depth
    };
    var target = {
      self: parent.concat(0),
      parent: parent,
      target: "body"
    };
    var loader = this.loader.bind(this);
    var build = this.build.bind(this,constant);
    if (result.out instanceof Array){
      var promises = result.out.map(function(name,i){
        target.target = "head";
        target.self = parent.concat(i);
        var sources = [target,{name:name,length:result.out.length}];
        return loader(target.self, build(sources), depth+1);
      });
      return Promise.all(promises);
    }
    old_terms = this.parse(result.old.join('&'))
    var sources = [target,old_terms,result.out];
    return build(sources);
  },
  find: function(hash,depth){
    var where = this.plural(this.ask[depth])+"?";
    return this.get("/api/" + where + this.hash(hash));
  },
  loader: function(parent,folder,depth){
    var draw = this.draw.bind(this, parent, depth);
    return this.find(folder, depth).then(draw);
  }
};
