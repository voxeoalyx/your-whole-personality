"""Dependency-free web prototype; loopback by default. Run: python server.py"""
import argparse
import os
import ipaddress
from protection import VISITORS,LimitReached
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import mimetypes
import re
import threading
import time
import uuid
from urllib.parse import urlsplit,parse_qs
from game import CATALOG,PRESETS,build
from qloo_client import Client,QlooError,ROOT,TYPES,entity,items
from scoring import scores
from signals import normalize,HOBBIES,TAG_TYPES,kind,pick_domains,validate_context
from investigator import Investigator,EvidenceClient
from model_client import ModelClient

CLIENT=Client(); REGISTRY={e['id']:e for e in CATALOG}; VALID={e['id']:e['verified'] for e in CATALOG}
DISCOVERED={}; SEED_IDS=set(REGISTRY)
CHECK_MESSAGES={}
JOBS={}; LOCK=threading.Lock(); WORKERS=ThreadPoolExecutor(max_workers=2)
INVESTIGATORS={}; MODEL=ModelClient()
DEMO_FILE=ROOT/'data/demos.json'
DEMOS=json.loads(DEMO_FILE.read_text(encoding='utf-8')) if DEMO_FILE.exists() else {}
STATIC={'/':'index.html','/app.js':'app.js','/logic.js':'logic.js','/style.css':'style.css','/favicon.svg':'favicon.svg'}


def search_interests(q,typ):
    found=[]; notices=[]
    routes=[]
    if not typ or typ=='audience':routes.append(('/v2/audiences',{'filter.query':q,'filter.parents.types':HOBBIES,'take':12},'audience'))
    if not typ or typ=='tag':routes.append(('/v2/tags',{'filter.query':q,'filter.tag.types':sorted(TAG_TYPES),'take':12},'tag'))
    if not typ or typ in TYPES:
        routes.append(('/search',{'query':q,'take':8,**({'types':'urn:entity:'+typ} if typ else {})},'entity'))
    for route,params,family in routes:
        try:raw=CLIENT.get(route,params)
        except QlooError as exc:
            notices.append(family.title()+' search unavailable: '+str(exc));continue
        rows=items(raw) if family=='entity' else raw.get('results',{}).get('tags' if family=='tag' else 'audiences',[])
        for x in rows:
            e=entity(x) if family=='entity' else normalize(x,family)
            if not e or not e['type'] or not e['id']:continue
            if family=='entity' and not re.fullmatch(r'[A-Fa-f0-9-]{36}',e['id']):continue
            e['verified']=VALID.get(e['id']); e['support_message']=CHECK_MESSAGES.get(e['id'],'')
            REGISTRY[e['id']]=e;found.append(e)
            if e['id'] not in SEED_IDS:DISCOVERED[e['id']]=time.monotonic()
    found=list({e['id']:e for e in found}.values())
    # An exact hobby match precedes incidental titles, without merging distinct meanings.
    found.sort(key=lambda e:(e['name'].casefold()!=q.casefold(),{'audience':0,'tag':1}.get(e['type'],2)))
    if len(REGISTRY)>1500:
        keep={e['id']:e for e in CATALOG};keep.update({e['id']:e for e in found});REGISTRY.clear();REGISTRY.update(keep)
    if q.casefold() in {'pilates','weightlifting','weight lifting'} and typ in {'','tag','audience'}:
        notices.insert(0,'No usable exact '+q+' hobby signal was found in our hackathon tests. The related place tags returned flat recommendations; a title containing the word is a different interest. Fitness and Health & Fitness are broader content tags you can search for, not equivalents. Nothing is substituted.')
    return {'results':found,'notices':notices}


def work(token,interests):
    def update(**kw):
        with LOCK: JOBS[token].update(deepcopy(kw))
    try:
        result=build(CLIENT,interests,update)
        update(status='ready',game=result)
    except QlooError as exc: update(status='error',error=str(exc),code=exc.code,unsupported=exc.ids)
    except Exception: update(status='error',error='The algorithm tripped over its own assumptions. Try again.',code='internal')


def publish_investigation(token,engine):
    snapshot=engine.snapshot()
    with LOCK:
        if token in JOBS:JOBS[token].update(snapshot)


def investigation_work(token,interests):
    evidence=EvidenceClient(CLIENT)
    engine=None
    def update(**kw):
        nonlocal engine
        partial=kw.pop('game',None)
        with LOCK:JOBS[token].update(kw)
        if partial and engine is None:
            engine=Investigator(partial,MODEL,evidence)
            with LOCK:INVESTIGATORS[token]=engine
            engine.advance()
            publish_investigation(token,engine)
        elif partial and partial.get('sensitivity'):
            engine.set_influence(partial)
            publish_investigation(token,engine)
    try:
        result=build(evidence,interests,update)
        engine.set_influence(result)
        publish_investigation(token,engine)
    except QlooError as exc:
        with LOCK:JOBS[token].update(status='error',error=str(exc),code=exc.code,unsupported=exc.ids)
    except Exception:
        with LOCK:JOBS[token].update(status='error',error='The investigation was interrupted. Start a fresh round.',code='internal')


def next_investigation(token,engine):
    try:
        engine.advance()
        publish_investigation(token,engine)
    except Exception:
        with LOCK:JOBS[token].update(status='error',error='The investigation was interrupted. Start a fresh round.',code='internal')


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def live_limit(self, category, maximum, seconds):
        address = self.client_address[0]
        # Only enable behind Render: its edge appends the connecting IP.
        # Never trust the first X-Forwarded-For value supplied by a client.
        if os.environ.get("TRUST_PROXY") == "render":
            address = self.headers.get("X-Forwarded-For", address).split(",")[-1].strip()
            try: ipaddress.ip_address(address)
            except ValueError:
                self.send({"error":"Invalid proxy address."},400)
                return False
        try:
            VISITORS.take(address, category, maximum, seconds)
            return True
        except LimitReached as exc:
            self.send({"error":str(exc),"code":"rate_limit"},429)
            return False

    def log_message(self,*args): pass  # No query strings or user interests in access logs.

    def send(self,data,status=200,kind='application/json; charset=utf-8'):
        raw=json.dumps(data,ensure_ascii=False,allow_nan=False).encode() if kind.startswith('application/json') else data
        self.send_response(status); self.send_header('Content-Type',kind); self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer'); self.send_header('Cross-Origin-Resource-Policy','same-origin')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' https: data: blob:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        try:
            self.end_headers(); self.wfile.write(raw)
        except (BrokenPipeError,ConnectionResetError,ConnectionAbortedError): pass

    def origin_ok(self):
        # Local prototype: prevent cross-origin pages driving the paid API.
        host=self.headers.get('Host','')
        origins={f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'}
        if getattr(self.server,'public_origin',None):origins.add(self.server.public_origin)
        if host not in {urlsplit(o).netloc for o in origins}: return False
        origin=self.headers.get('Origin')
        return (not origin or origin in origins) and self.headers.get('Sec-Fetch-Site') not in {'cross-site'}

    def do_GET(self):
        if self.path=='/healthz': return self.send({'status':'ok'})
        if not self.origin_ok(): return self.send({'error':'Origin not allowed.'},403)
        url=urlsplit(self.path); query=parse_qs(url.query)
        try:
            if url.path in STATIC:
                file=ROOT/'static'/STATIC[url.path]
                kind=mimetypes.guess_type(str(file))[0] or 'application/octet-stream'
                return self.send(file.read_bytes(),kind=kind+'; charset=utf-8' if kind.startswith('text') or kind=='application/javascript' else kind)
            if url.path=='/api/config':
                return self.send({'live':bool(CLIENT.key),'investigator':bool(MODEL.key),'catalog':CATALOG,'presets':PRESETS,'demos':list(DEMOS),'privacy':'Live picks and recommendations go to Qloo and NVIDIA. Reactions go to the investigator on this server and NVIDIA. Rounds expire after 30 minutes. No account or analytics.'})
            if url.path=='/api/search':
                if not self.live_limit('search',20,60): return
                q=query.get('q',[''])[0].strip(); typ=query.get('type',[''])[0]
                if not 2<=len(q)<=100 or typ and typ not in TYPES|{'tag','audience'}: return self.send({'error':'Use 2–100 characters and a supported category.'},400)
                return self.send(search_interests(q,typ))
            if url.path.startswith('/api/game/'):
                token=url.path.rsplit('/',1)[-1]
                if token.startswith('recorded-') and token[9:] in DEMOS:
                    game=deepcopy(DEMOS[token[9:]]);game['source']='recorded'
                    return self.send({'status':'ready','game':game,'progress':100})
                with LOCK: job=deepcopy(JOBS.get(token))
                if not job: return self.send({'error':'This round expired. Start another.'},404)
                return self.send(job)
            return self.send({'error':'Not found.'},404)
        except QlooError as exc: return self.send({'error':str(exc),'code':exc.code,'unsupported':exc.ids},503)
        except Exception: return self.send({'error':'Something interrupted the request. Try again.'},500)

    def do_POST(self):
        if not self.origin_ok(): return self.send({'error':'Local requests only.'},403)
        if self.headers.get('Transfer-Encoding') or len(self.headers.get_all('Content-Length', [])) != 1:
            return self.send({'error':'A single Content-Length is required.'},400)
        if self.headers.get_content_type() != 'application/json':
            return self.send({'error':'Use application/json.'},415)
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=8192: return self.send({'error':'Invalid request size.'},400)
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict): raise ValueError()
            if self.path=='/api/validate':
                if not self.live_limit('validate',30,60): return
                ident=data.get('id'); e=REGISTRY.get(ident)
                if not e: return self.send({'error':'Search for that exact interest again.'},400)
                if ident not in VALID:
                    try:
                        if kind(e)=='entity':VALID[ident]=bool(scores(CLIENT.insights([e],'brand' if e['type']!='brand' else 'tv_show',take=2)))
                        else:
                            domains=pick_domains([e]); validate_context(CLIENT,e,domains); VALID[ident]=len(domains)==2
                    except QlooError as exc:
                        if exc.code=='unsupported': VALID[ident]=False; CHECK_MESSAGES[ident]=str(exc)
                        else: raise
                return self.send({'valid':VALID[ident],'entity':e,'message':CHECK_MESSAGES.get(ident,'Qloo cannot use this exact record as an interest. Choose another result; we will not swap it for you.') if not VALID[ident] else 'Ready.'})
            if self.path=='/api/answer':
                token=data.get('id')
                if not isinstance(token,str):return self.send({'error':'Invalid round.'},400)
                with LOCK:engine=INVESTIGATORS.get(token)
                if not engine:return self.send({'error':'This investigation expired. Start another.'},404)
                if not self.live_limit('answer',30,60): return
                with LOCK:
                    if JOBS[token]['status']!='working' and sum(j['status']=='working' for j in JOBS.values())>=2:
                        return self.send({'error':'Live rounds are busy. Try again shortly or play a recorded round.'},429)
                    changed=engine.answer(data.get('prediction_id'),data.get('response'),data.get('sequence'))
                    if changed: JOBS[token]['status']='working'
                if changed:
                    with LOCK:JOBS[token]['status']='working'
                    WORKERS.submit(next_investigation,token,engine)
                return self.send({'accepted':True,'duplicate':not changed},202)
            if self.path=='/api/game':
                mode=data.get('mode')
                if mode not in {'live','demo'}: return self.send({'error':'Choose live or recorded mode.'},400)
                with LOCK:
                    expired=[k for k,v in JOBS.items() if time.monotonic()-v['created']>1800 and v['status']!='working']
                    for k in expired: del JOBS[k]; INVESTIGATORS.pop(k,None)
                    if mode=='live' and (len(JOBS)>=24 or sum(x['status']=='working' for x in JOBS.values())>=2): return self.send({'error':'A couple of rounds are running. Try again shortly.'},429)
                if mode=='demo':
                    demo=DEMOS.get(data.get('demo_id'))
                    if not demo: return self.send({'error':'That recorded round is unavailable.'},400)
                    # Stateless recorded rounds remain available when live capacity is full.
                    return self.send({'id':'recorded-'+data['demo_id']},202)
                else:
                    ids=data.get('ids')
                    if not isinstance(ids,list) or not 3<=len(ids)<=5 or any(not isinstance(i,str) for i in ids) or len(set(ids))!=len(ids): return self.send({'error':'Pick 3–5 different interests.'},400)
                    if any(i not in REGISTRY or VALID.get(i)!=True for i in ids): return self.send({'error':'Every pick needs to be checked first.'},400)
                    if not CLIENT.key: raise QlooError('No live key is configured. Choose a recorded round.','not_configured')
                    if not self.live_limit('round',3,3600): return
                    token=uuid.uuid4().hex
                    with LOCK:
                        if sum(x['status']=='working' for x in JOBS.values())>=2 or len(JOBS)>=24:
                            return self.send({'error':'Live rounds are busy. Play a recorded round.'},429)
                        JOBS[token]={'created':time.monotonic(),'status':'working','message':'Calling the cultural witness stand.','progress':5}
                    WORKERS.submit(investigation_work if data.get('investigate') is True else work,token,[deepcopy(REGISTRY[i]) for i in ids])
                return self.send({'id':token},202)
            return self.send({'error':'Not found.'},404)
        except (ValueError,TypeError): return self.send({'error':'Invalid request.'},400)
        except QlooError as exc: return self.send({'error':str(exc),'code':exc.code},503)
        except Exception: return self.send({'error':'The request could not be completed.'},500)


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 32

    def __init__(self, *args, **kwargs):
        self.slots = threading.BoundedSemaphore(32)
        super().__init__(*args, **kwargs)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            self.shutdown_request(request)
            return
        try: super().process_request(request, client_address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try: super().process_request_thread(request, client_address)
        finally: self.slots.release()

    def service_actions(self):
        now=time.monotonic()
        with LOCK:
            for token in [k for k,v in JOBS.items() if now-v['created']>1800 and v['status']!='working']:
                JOBS.pop(token,None); INVESTIGATORS.pop(token,None)
            for ident in [i for i,t in DISCOVERED.items() if now-t>7200]:
                DISCOVERED.pop(ident,None); REGISTRY.pop(ident,None); VALID.pop(ident,None); CHECK_MESSAGES.pop(ident,None)
        if CLIENT.lock.acquire(blocking=False):
            try:
                for k in [k for k,v in CLIENT.cache.items() if now-v[0]>7200]: CLIENT.cache.pop(k,None)
                CLIENT.audit[:]=[r for r in CLIENT.audit if time.time()-r.get('at',0)<=7200]
            finally: CLIENT.lock.release()


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--host',default='127.0.0.1');parser.add_argument('--public-origin')
    args=parser.parse_args()
    if args.public_origin and (urlsplit(args.public_origin).scheme!='https' or not urlsplit(args.public_origin).hostname or urlsplit(args.public_origin).username or urlsplit(args.public_origin).password or urlsplit(args.public_origin).path or urlsplit(args.public_origin).query or urlsplit(args.public_origin).fragment):
        parser.error('--public-origin must be an HTTPS origin without a path')
    if args.host!='127.0.0.1' and not args.public_origin:parser.error('An external bind requires --public-origin and an HTTPS reverse proxy')
    server=LocalServer((args.host,args.port),Handler);server.public_origin=args.public_origin
    print(f'Your Whole Personality: http://127.0.0.1:{args.port} (Ctrl+C to stop)',flush=True)
    server.serve_forever()
