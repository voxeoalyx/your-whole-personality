"""Small server-only Qloo adapter: bounded memory cache, timeouts, no credential logging."""
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import time
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode,urlsplit
from urllib.request import Request,build_opener,HTTPRedirectHandler
from signals import FIELDS,parameters

ROOT=Path(__file__).resolve().parent
TYPES={'artist','tv_show','movie','podcast','book','brand','videogame','person'}


class QlooError(Exception):
    def __init__(self,message,code='service_unavailable',ids=None):
        super().__init__(message); self.code=code; self.ids=ids or []


def environment(names=None):
    values={}
    # Credentials are local to this checkout; process environment takes precedence.
    for file in [ROOT/'.env']:
        if not file.exists(): continue
        for line in file.read_text(encoding='utf-8-sig').splitlines():
            line=line.strip()
            if not line or line.startswith('#') or '=' not in line: continue
            k,v=line.removeprefix('export ').split('=',1)
            v=v.strip()
            if v.startswith(('"',"'")): v=v[1:].split(v[0],1)[0]
            else: v=re.split(r'\s+#',v,1)[0].strip()
            values[k.strip()]=v
    return {k:os.environ.get(k) or values.get(k,'') for k in (names or ['QLOO_API_KEY','QLOO_BASE_URL','QLOO_CALL_LIMIT'])}


def items(payload):
    r=payload.get('results',{})
    return r if isinstance(r,list) else r.get('entities',[]) if isinstance(r,dict) else []


def unsupported(payload):
    return list(dict.fromkeys(i for w in payload.get('warnings',[]) if isinstance(w,dict)
                              for field in FIELDS.values() for i in (w.get(field,[]) if isinstance(w.get(field,[]),list) else [w[field]])))


def entity(raw):
    prop=raw.get('properties') or {}; typ=next((t.rsplit(':',1)[-1] for t in raw.get('types',[]) if t.rsplit(':',1)[-1] in TYPES),None)
    image=(prop.get('image') or {}).get('url') if isinstance(prop.get('image'),dict) else None
    if image and not (urlsplit(image).scheme=='https' and urlsplit(image).hostname): image=None
    return {'id':raw.get('entity_id'),'name':str(raw.get('name',''))[:240],'type':typ,
            'detail':str(raw.get('disambiguation') or prop.get('release_year') or prop.get('description') or '')[:180],
            'image':image,'score':raw.get('query',{}).get('affinity')}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): return None


class Client:
    def __init__(self):
        env=environment(); self.key=env['QLOO_API_KEY']; self.base=env['QLOO_BASE_URL'] or 'https://hackathon.api.qloo.com'
        parsed=urlsplit(self.base)
        if parsed.scheme!='https' or parsed.hostname not in {'hackathon.api.qloo.com','api.qloo.com'} or parsed.path not in ('','/') or parsed.query or parsed.fragment or parsed.username or parsed.password or parsed.port not in (None,443):
            raise ValueError('QLOO_BASE_URL must be an approved HTTPS Qloo origin')
        self.base=self.base.rstrip('/'); self.cache={}; self.lock=threading.Lock(); self.calls=0; self.limit=int(env['QLOO_CALL_LIMIT'] or 180)
        self.audit=[]; self.cooldown_until=0; self.record_dir=None

    def get(self,route,params):
        if route not in {'/search','/v2/insights','/v2/tags','/v2/audiences'}: raise ValueError('Unknown endpoint')
        wire={k:','.join(map(str,v)) if isinstance(v,list) else str(v).lower() if isinstance(v,bool) else str(v) for k,v in sorted(params.items())}
        identity=json.dumps([route,wire],sort_keys=True); key=hashlib.sha256(identity.encode()).hexdigest()
        with self.lock:
            cached=self.cache.get(key)
            if cached and time.monotonic()-cached[0]<7200: return cached[1]
            if not self.key: raise QlooError('Live Qloo is not configured. A recorded round is ready below.','not_configured')
            if self.calls>=self.limit: raise QlooError('The local API budget is used up. Try a recorded round.','budget')
            if time.monotonic()<self.cooldown_until: raise QlooError('Qloo needs a short breather. Try again in a minute.','rate_limit')
            self.calls+=1
            req=Request(self.base+route+'?'+urlencode(wire),headers={'X-Api-Key':self.key,'Accept':'application/json','User-Agent':'your-whole-personality-local/0.1'})
            try:
                with build_opener(NoRedirect()).open(req,timeout=15) as response:
                    raw=response.read(8*1024*1024+1)
                if len(raw)>8*1024*1024: raise QlooError('That response was too large. Try fewer interests.')
                data=json.loads(raw)
            except HTTPError as exc:
                if exc.code==429:
                    self.cooldown_until=time.monotonic()+60
                    raise QlooError('Qloo is taking a breather. Try again in a minute.','rate_limit') from None
                if exc.code==404 and route=='/search': return {'results':[]}
                raise QlooError('Qloo could not finish that request. Try a recorded round.') from None
            except (URLError,TimeoutError,OSError,ValueError):
                raise QlooError('The connection to Qloo dropped. Your picks are still here.') from None
            if not isinstance(data,dict) or data.get('errors'): raise QlooError('Qloo could not score this request. Try a different mix.')
            if len(self.cache)>=256: self.cache.pop(next(iter(self.cache)))
            self.cache[key]=(time.monotonic(),data)
            self.audit.append({'at':time.time(),'request_hash':key,'route':route,'params':wire,'response_sha256':hashlib.sha256(raw).hexdigest()})
            if self.record_dir:
                self.record_dir.mkdir(parents=True,exist_ok=True)
                (self.record_dir/(key+'.json')).write_bytes(raw)
                (self.record_dir/(key+'.meta.json')).write_text(json.dumps(self.audit[-1],indent=2),encoding='utf-8')
            self.audit=self.audit[-256:]
            return data

    def insights(self,ids,domain,panel=None,take=20):
        params={'filter.type':'urn:entity:'+domain,**parameters(ids),'bias.trends':'off','feature.explainability':True,'take':len(panel) if panel else take}
        if panel: params['filter.results.entities']=sorted(panel)
        raw=self.get('/v2/insights',params)
        bad=unsupported(raw)
        if bad: raise QlooError('Qloo found an interest in search but cannot use it in this round. Remove the highlighted pick and try again.','unsupported',bad)
        return [entity(x) for x in items(raw)]
