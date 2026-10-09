"""Explicit developer-only recording of three public research fixtures, never player feedback."""
import argparse
import hashlib
import json
from game import CATALOG,PRESETS,build
from qloo_client import Client,ROOT

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--live',action='store_true'); args=p.parse_args()
    if not args.live: p.error('Use --live to authorize recording these fixed Qloo examples (about 30 calls).')
    c=Client(); c.record_dir=ROOT/'.cache/verification'; out=ROOT/'data/demos.json'; demos={}
    if out.exists(): demos=json.loads(out.read_text(encoding='utf-8'))
    for preset in PRESETS:
        if preset['id'] in demos:
            print(preset['id']+': reusing existing recording',flush=True); continue
        interests=[next(e for e in CATALOG if e['alias']==alias) for alias in preset['aliases']]
        print('Recording '+preset['id'],flush=True)
        result=build(c,interests,lambda **kw: print(kw['message'],flush=True) if 'message' in kw else None)
        result['source']='recorded'; result['fixture']=preset['id']; result['provenance']={'kind':'Qloo live fixture recorded for this prototype','request_hashes':[r['request_hash'] for r in c.audit]}
        demos[preset['id']]=result
        out.write_text(json.dumps(demos,ensure_ascii=False,indent=2),encoding='utf-8')
        print(preset['id']+': '+result['sensitivity']['status'],flush=True)
    print(json.dumps({'new_calls':c.calls,'fixtures':list(demos),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}),flush=True)
