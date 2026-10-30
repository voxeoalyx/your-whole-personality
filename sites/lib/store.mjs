// All mutable state lives in D1; a new Worker isolate can resume any round.
export class Store {
  constructor(db,clock=()=>Date.now()){if(!db)throw new Error('DB binding is required');this.db=db;this.clock=clock;}
  async get(key){const row=await this.db.prepare('SELECT value FROM records WHERE key=? AND expires>?').bind(key,this.clock()).first();return row?JSON.parse(row.value):null;}
  async put(key,kind,value,ttl){await this.db.prepare('INSERT INTO records(key,kind,value,expires) VALUES(?,?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,expires=excluded.expires,version=records.version+1').bind(key,kind,JSON.stringify(value),this.clock()+ttl).run();
    const cap=({cache:256,entity:1500,validation:1500})[kind];if(cap)await this.db.prepare("DELETE FROM records WHERE kind=? AND key NOT IN (SELECT key FROM records WHERE kind=? ORDER BY expires DESC LIMIT ?)").bind(kind,kind,cap).run();}
  async insert(key,kind,value,ttl,cap){const result=await this.db.prepare('INSERT INTO records(key,kind,value,expires) SELECT ?,?,?,? WHERE (SELECT count(*) FROM records WHERE kind=? AND expires>?)<?').bind(key,kind,JSON.stringify(value),this.clock()+ttl,kind,this.clock(),cap).run();return result.meta.changes===1;}
  async demo(key,value,ttl){const now=this.clock();await this.db.batch([
    this.db.prepare("DELETE FROM records WHERE key=(SELECT key FROM records WHERE kind='demo' AND expires>? ORDER BY expires LIMIT 1) AND (SELECT count(*) FROM records WHERE kind='demo' AND expires>?)>=24").bind(now,now),
    this.db.prepare("INSERT INTO records(key,kind,value,expires) VALUES(?,'demo',?,?)").bind(key,JSON.stringify(value),now+ttl)
  ]);}
  async consume(key,amount,limit,window){const now=this.clock();return Boolean(await this.db.prepare('INSERT INTO counters(key,value,expires) SELECT ?,?,? WHERE ?<=? ON CONFLICT(key) DO UPDATE SET value=CASE WHEN counters.expires<=? THEN excluded.value ELSE counters.value+excluded.value END, expires=CASE WHEN counters.expires<=? THEN excluded.expires ELSE counters.expires END WHERE counters.expires<=? OR counters.value+excluded.value<=? RETURNING value').bind(key,amount,now+window,amount,limit,now,now,now,limit).first());}
  async lease(key){const owner=crypto.randomUUID(),now=this.clock();await this.db.prepare('DELETE FROM leases WHERE expires<=?').bind(now).run();
    const r=await this.db.prepare('INSERT OR IGNORE INTO leases(key,owner,expires) SELECT ?,?,? WHERE (SELECT count(*) FROM leases)<2').bind(key,owner,now+30000).run();return r.meta.changes===1?owner:null;}
  async release(key,owner){await this.db.prepare('DELETE FROM leases WHERE key=? AND owner=?').bind(key,owner).run();}
  async saveJob(id,state,owner){const r=await this.db.prepare('UPDATE records SET value=?,version=version+1 WHERE key=? AND expires>? AND EXISTS(SELECT 1 FROM leases WHERE key=? AND owner=? AND expires>?)').bind(JSON.stringify(state),'job:'+id,this.clock(),'job:'+id,owner,this.clock()).run();if(r.meta.changes!==1)throw new Error('Round lease expired');}
  async cleanup(){const now=this.clock();await this.db.batch([
    this.db.prepare('DELETE FROM records WHERE expires<=?').bind(now),this.db.prepare('DELETE FROM counters WHERE expires<=?').bind(now),this.db.prepare('DELETE FROM leases WHERE expires<=?').bind(now)
  ]);}
  async visitor(request){const now=this.clock(),saltKey='salt:'+new Date(now).toISOString().slice(0,10);let salt=await this.get(saltKey);if(!salt){await this.db.prepare("INSERT OR IGNORE INTO records(key,kind,value,expires) VALUES(?,'control',?,?)").bind(saltKey,JSON.stringify(crypto.randomUUID()),(Math.floor(now/86400000)+1)*86400000).run();salt=await this.get(saltKey);}
    const identity=request.headers.get('oai-authenticated-user-id');
    const address=identity?'site:'+identity:request.cf?request.headers.get('CF-Connecting-IP')||'shared':'local';
    const key=await crypto.subtle.importKey('raw',new TextEncoder().encode(salt),{name:'HMAC',hash:'SHA-256'},false,['sign']);
    return [...new Uint8Array(await crypto.subtle.sign('HMAC',key,new TextEncoder().encode(address)))].map(n=>n.toString(16).padStart(2,'0')).join('');}
  async rate(visitor,route,cost=0){const limit={search:30,validate:30,game:6,game_request:30,answer:30,poll:120}[route];
    if(!await this.consume('rate:global',1,240,60000)||!await this.consume('rate:'+visitor+':'+route,1,limit,60000))return false;
    if(cost&&!await this.consume('cost:'+visitor,cost,120,900000))return false;return true;}
  async newRound(visitor){const day=new Date(this.clock()).toISOString().slice(0,10);return this.consume('new-rounds:'+day+':'+visitor,1,10,86400000);}
}
