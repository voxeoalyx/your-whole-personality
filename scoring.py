"""Tie-aware rank sensitivity, adapted from Experiment 3; no personality probabilities."""
import math
from statistics import mean


def ranks(values):
    order=sorted(enumerate(values),key=lambda x:x[1]); out=[0.0]*len(values); i=0
    while i<len(order):
        j=i+1
        while j<len(order) and order[j][1]==order[i][1]: j+=1
        for k,_ in order[i:j]: out[k]=(i+1+j)/2
        i=j
    return out


def distance(a,b,ids):
    if len(ids)<4 or any(i not in a or i not in b for i in ids): return None
    av,bv=ranks([a[i] for i in ids]),ranks([b[i] for i in ids])
    am,bm=mean(av),mean(bv)
    den=math.sqrt(sum((v-am)**2 for v in av)*sum((v-bm)**2 for v in bv))
    if not den: return None
    rho=sum((v-am)*(w-bm) for v,w in zip(av,bv))/den
    return (1-max(-1,min(1,rho)))/2


def scores(rows):
    return {x['id']:x['score'] for x in rows if isinstance(x.get('score'),(int,float)) and not isinstance(x['score'],bool) and math.isfinite(x['score'])}


def sensitivity(interests,full,ablations):
    rows=[]
    for entity in interests:
        row={'id':entity['id'],'name':entity['name'],'domains':{},'value':None,'halves':[None,None]}
        ds=[]; halves=[[],[]]
        for domain,base in full.items():
            reduced=ablations.get(entity['id'],{}).get(domain,[])
            ids=sorted(x['id'] for x in base)
            d=distance(scores(base),scores(reduced),ids)
            row['domains'][domain]=d; ds.append(d)
            for half in (0,1): halves[half].append(distance(scores(base),scores(reduced),ids[half::2]))
        if len(ds)==2 and all(d is not None for d in ds): row['value']=mean(ds)
        for half,values in enumerate(halves):
            if len(values)==2 and all(d is not None for d in values): row['halves'][half]=mean(values)
        rows.append(row)
    complete=len(full)==2 and all(r['value'] is not None and None not in r['halves'] for r in rows)
    ordered=sorted(rows,key=lambda r:r['value'] if r['value'] is not None else -1,reverse=True)
    winner=None
    if complete and len(ordered)>1:
        top,runner=ordered[:2]
        if top['value']>.10 and top['value']>2*runner['value'] and all(max(rows,key=lambda r:r['halves'][h])['id']==top['id'] for h in (0,1)):
            winner={'id':top['id'],'name':top['name'],'value':top['value']}
    return {'status':'complete' if complete else 'incomplete','winner':winner,'rows':ordered,
            'domains':list(full),'method':'mean((1 - tie-aware Spearman rho) / 2), two fixed panels; same winner on disjoint halves'}
