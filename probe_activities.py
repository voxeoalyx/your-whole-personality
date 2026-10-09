"""Small explicit live research probe. Public example interests only; no player data."""
import argparse
import json
import hashlib
import time
from qloo_client import Client, ROOT, items, entity
from scoring import scores, distance
from signals import normalize,informative

TERMS=['pilates','running','yoga','weightlifting','architecture']
OUT=ROOT/'.cache/activity-signals'

class ResearchClient(Client):
    def __init__(self):
        super().__init__(); self.record_dir=OUT/'raw'
        # Explicit research replay only. The app does not load disk responses.
        for file in self.record_dir.glob('*.meta.json'):
            meta=json.loads(file.read_text()); raw=file.with_name(file.name.replace('.meta.json','.json')).read_bytes()
            if hashlib.sha256(raw).hexdigest()==meta['response_sha256']:
                self.cache[meta['request_hash']]=(time.monotonic(),json.loads(raw))

def compare(client):
    catalog=json.loads((ROOT/'data/catalog.json').read_text())
    ids=sorted(e['id'] for e in catalog if e['alias'] in ['radiohead','blue_bottle'])
    panels={}; bases={}; results=[]
    for domain in ['tv_show','movie']:
        base=client.insights(ids,domain); panels[domain]=list(scores(base))
        bases[domain]=client.insights(ids,domain,panels[domain])
    selected={
        'pilates': ['urn:tag:genre:place:pilates_studio','urn:tag:category:place:pilates_studio','urn:tag:occupation:wikidata:pilates'],
        'running': ['urn:tag:genre:media:running','urn:audience:hobbies_and_interests:running'],
        'yoga': ['urn:tag:genre:music:yoga','urn:audience:hobbies_and_interests:yoga'],
        'weightlifting': ['urn:tag:genre:place:weightlifting_area','urn:tag:category:place:weightlifting_area','urn:tag:occupation:wikidata:weightlifting'],
        'architecture': ['urn:tag:genre:media:architecture','urn:audience:hobbies_and_interests:architecture']}
    for term,identifiers in selected.items():
        for ident in identifiers:
            family='audiences' if ident.startswith('urn:audience:') else 'tags'
            lookup=json.loads((OUT/(term+'_'+family+'.json')).read_text(encoding='utf-8'))['results'][family]
            match=next(x for x in lookup if x['id']==ident)  # Never synthesize a taxonomy ID.
            row={'term':term,'id':ident,'name':match['name'],'type':match['type'],'domains':{}}
            for domain,panel in panels.items():
                params={'filter.type':'urn:entity:'+domain,'signal.interests.entities':ids,
                        'signal.demographics.audiences' if family=='audiences' else 'signal.interests.tags':[ident],
                        'filter.results.entities':sorted(panel),'bias.trends':'off','feature.explainability':True,'take':len(panel)}
                raw=client.get('/v2/insights',params); rows=[entity(x) for x in items(raw)]; vals=scores(rows); base=scores(bases[domain])
                row['domains'][domain]={'scored':len(vals),'warnings':raw.get('warnings',[]),'distance':distance(base,vals,panel),
                    'max_score_change':max((abs(base[i]-vals[i]) for i in panel if i in vals),default=None),
                    'top3':[{'name':x['name'],'score':x['score']} for x in sorted(rows,key=lambda x:x.get('score') or 0,reverse=True)[:3]],
                    'base_top3':[x['name'] for x in bases[domain][:3]]}
            results.append(row); print(json.dumps(row,ensure_ascii=True),flush=True)
    save('comparison',{'baseline_entities':ids,'baseline':bases,'panels':panels,'results':results})

def coverage(client):
    # Singleton signals expose flat/zero components hidden by ordinary entities.
    prior=json.loads((OUT/'comparison.json').read_text(encoding='utf-8')); results=[]
    for item in prior['results']:
        if item['id'].startswith('urn:audience:'):continue
        row={'id':item['id'],'domains':{}}
        for domain in ['tv_show','movie','brand','videogame']:
            raw=client.get('/v2/insights',{'filter.type':'urn:entity:'+domain,'signal.interests.tags':[item['id']],
                'bias.trends':'off','feature.explainability':True,'take':20})
            vals=scores([entity(x) for x in items(raw)])
            row['domains'][domain]={'scored':len(vals),'distinct_scores':len(set(vals.values())),
                'score_range':[min(vals.values()),max(vals.values())] if vals else [],'warnings':raw.get('warnings',[]),
                'top3':[(x['name'],x.get('query',{}).get('affinity')) for x in items(raw)[:3]]}
        results.append(row);print(json.dumps(row),flush=True)
    save('coverage',results)
    for term in ['fitness','weight','strength','bodybuilding']:
        raw=client.get('/v2/audiences',{'filter.query':term,'take':50})
        save(term+'_audiences',raw)
        print(json.dumps({'term':term,'audiences':raw.get('results',{}).get('audiences',[])}),flush=True)

def mechanics(client):
    from game import build,CATALOG
    entities=[e for e in CATALOG if e['alias'] in ['radiohead','blue_bottle']]
    choices=[]
    for term,family,ident in [('running','audience','urn:audience:hobbies_and_interests:running'),
                            ('yoga','audience','urn:audience:hobbies_and_interests:yoga'),
                            ('architecture','audience','urn:audience:hobbies_and_interests:architecture'),
                            ('architecture','tag','urn:tag:genre:media:architecture'),
                            ('yoga','tag','urn:tag:genre:music:yoga')]:
        plural='audiences' if family=='audience' else 'tags'
        raw=json.loads((OUT/(term+'_'+plural+'.json')).read_text(encoding='utf-8'))['results'][plural]
        choices.append(normalize(next(x for x in raw if x['id']==ident),family))
    mixes=[[x] for x in choices]+[[choices[3],choices[0],choices[1]]]
    results=[]
    for extra in mixes:
        game=build(client,entities+extra); save('game_'+str(len(results)+1),game)
        row={'inputs':[e.get('label',e['name']) for e in game['interests']],
             'predictions':[(p['name'],p['domain'],p['score']) for p in game['predictions']],
             'sensitivity':game['sensitivity']}
        results.append(row);print(json.dumps(row),flush=True)
    save('mechanics',results)

def broader(client):
    prior=json.loads((OUT/'comparison.json').read_text(encoding='utf-8')); results=[]
    for term,ident in [('fitness','urn:tag:genre:media:fitness'),('fitness','urn:tag:genre:media:health_fitness'),
                      ('exercise','urn:tag:genre:media:exercise')]:
        lookup=client.get('/v2/tags',{'filter.query':term,'take':50});save(term+'_tags',lookup)
        raw=lookup['results']['tags']
        e=normalize(next(x for x in raw if x['id']==ident),'tag'); row={'id':ident,'label':e['label'],'domains':{}}
        for domain,panel in prior['panels'].items():
            solo=client.insights([e],domain)
            mixed=client.insights(prior['baseline_entities']+[e],domain,panel)
            row['domains'][domain]={'singleton_informative':informative(solo),'distance':distance(scores(prior['baseline'][domain]),scores(mixed),panel),
                'top3':[(x['name'],x['score']) for x in mixed[:3]]}
        results.append(row);print(json.dumps(row),flush=True)
    save('broader',results)

def save(name,data):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/(name+'.json')).write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')

def run():
    parser=argparse.ArgumentParser(); parser.add_argument('--live',action='store_true'); parser.add_argument('--phase',choices=['lookup','compare','coverage','mechanics','broader'],default='lookup'); args=parser.parse_args()
    if not args.live: parser.error('Use --live to make bounded Qloo calls')
    client=ResearchClient()
    if args.phase=='lookup':
        for term in TERMS:
            for family in ['tags','audiences']:
                data=client.get('/v2/'+family,{'filter.query':term,'take':50})
                save(term+'_'+family,data)
                print(json.dumps({'term':term,'family':family,'matches':[{'id':x['id'],'name':x['name']} for x in data.get('results',{}).get(family,[])]},ensure_ascii=True),flush=True)
    elif args.phase=='compare':compare(client)
    elif args.phase=='coverage':coverage(client)
    elif args.phase=='mechanics':mechanics(client)
    else:broader(client)
    print('Calls: '+str(client.calls),flush=True)

if __name__=='__main__':run()
