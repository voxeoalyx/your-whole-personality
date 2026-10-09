"""Experiment 2 preparation and bounded runs; Python standard library only."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import qloo

ROOT = Path(__file__).resolve().parent
E = ROOT / 'experiment2'
R = 6371008.8


def freeze(path, obj):
    path = Path(path)
    if path.exists() and qloo.read_json(path) != obj:
        raise ValueError(f'Refusing to change frozen configuration: {path.name}')
    if not path.exists():
        qloo.save_json(path, obj)


def polygon(lat, lon, radius=1000, east=0):
    """Spherical destination formula, 32 vertices, explicit WGS84 lon/lat."""
    lon += math.degrees(east / (R * math.cos(math.radians(lat))))
    phi, lam, d = math.radians(lat), math.radians(lon), radius / R
    ring = []
    for i in range(32):
        bearing = 2 * math.pi * i / 32
        p = math.asin(math.sin(phi)*math.cos(d) + math.cos(phi)*math.sin(d)*math.cos(bearing))
        l = lam + math.atan2(math.sin(bearing)*math.sin(d)*math.cos(phi), math.cos(d)-math.sin(phi)*math.sin(p))
        ring.append([round(math.degrees(l), 8), round(math.degrees(p), 8)])
    ring.reverse()  # GeoJSON outer ring counterclockwise.
    ring.append(ring[0])
    return {'type': 'Polygon', 'coordinates': [ring]}


def centroid(ring):
    cross = [a[0]*b[1]-b[0]*a[1] for a,b in zip(ring, ring[1:])]
    s = sum(cross)
    return [sum((a[k]+b[k])*c for a,b,c in zip(ring,ring[1:],cross))/(3*s) for k in (0,1)]


def wkt(geom):
    return 'POLYGON((' + ','.join(f'{x} {y}' for x,y in geom['coordinates'][0]) + '))'


def distance(a, b):
    p1,p2 = math.radians(a['lat']), math.radians(b['lat'])
    dl = math.radians(b['lon']-a['lon'])
    return 2*R*math.asin(min(1, math.sqrt(math.sin((p2-p1)/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2)))


def inside(lon, lat, geom):
    ring = geom['coordinates'][0]
    yes = False
    for (x1,y1),(x2,y2) in zip(ring, ring[1:]):
        if (y1>lat)!=(y2>lat) and lon < (x2-x1)*(lat-y1)/(y2-y1)+x1:
            yes = not yes
    return yes


def plan(name, requests):
    freeze(E/'plans'/f'{name}.json', {'title': f'Experiment 2: {name}', 'requests': requests})


def discovery():
    plan('01-discovery', [
        {'id':'global_brands','endpoint':'/v2/insights','params':{'filter.type':'urn:entity:brand','filter.popularity.min':0.95,'take':30,'bias.trends':'off'},'kind':'discovery'},
        {'id':'theater_tags','endpoint':'/v2/tags','params':{'filter.parents.types':'urn:entity:place','filter.tag.types':'urn:tag:genre:place','filter.query':'theater','take':20},'kind':'discovery'},
        {'id':'city_district_lookup','endpoint':'/search','params':{'query':'Central Business District, Orlando, Florida','types':'urn:entity:locality','take':5},'kind':'discovery'},
    ])


def run(stage, budget):
    # Hard lifetime cap across every Experiment 2 run, including failures/repeats.
    used = sum(len(p.read_text(encoding='utf8').splitlines()) for p in (E/'runs').glob('*/requests.jsonl'))
    if used >= 90:
        raise ValueError('Experiment 2 lifetime limit of 90 attempts reached')
    cfg = qloo.read_json(E/'plans'/f'{stage}.json')
    cfg['experiment2'] = {'plan_sha256': hashlib.sha256((ROOT/'EXPERIMENT_2_PLAN.md').read_bytes()).hexdigest(),
                          'driver_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                          'frozen_config': {f: hashlib.sha256((E/f).read_bytes()).hexdigest()
                                            for f in ['geographies.json','candidates.json'] if (E/f).exists()}}
    print(f'Lifetime attempts before invocation: {used}/90', flush=True)
    return qloo.run(cfg, E/'runs'/stage, qloo.load_env(ROOT/'civilizr-research.env'),
                    min(budget,90-used), retries=0, timeout=25, delay=0.4)


def candidates():
    brands, tags = {}, {}
    for directory in ['03-discovery','04-pilot','05-culture-pilot','06-expansion','07-culture-remaining']:
        for f in sorted((ROOT/'runs'/directory).glob('*.a1.json')):
            results = qloo.read_json(f).get('results', {})
            if not isinstance(results, dict):
                continue
            for t in results.get('tags', []):
                tags.setdefault(t.get('tag_id',t.get('id')), {**t,'source':str(f.relative_to(ROOT))})
            for e in results.get('entities', []):
                for t in e.get('tags', []):
                    tags.setdefault(t.get('tag_id',t.get('id')), {**t,'source':str(f.relative_to(ROOT))})
                if f.name.endswith('_brands.a1.json'):
                    brands.setdefault(e['entity_id'], {'id':e['entity_id'],'name':e['name'],
                        'genres':[t['name'] for t in e.get('tags',[]) if t.get('type')=='urn:tag:genre:brand'],
                        'pooled':True,'independent':False,'source':str(f.relative_to(ROOT))})
    independent_file = E/'runs/01-discovery/global_brands.a1.json'
    if independent_file.exists():
        for e in qloo.read_json(independent_file).get('results',{}).get('entities',[]):
            entry = brands.setdefault(e['entity_id'], {'id':e['entity_id'],'name':e['name'],
                'genres':[t['name'] for t in e.get('tags',[]) if t.get('type')=='urn:tag:genre:brand'],
                'pooled':False,'source':str(independent_file.relative_to(ROOT))})
            entry['independent'] = True
    theater_file=E/'runs/01-discovery/theater_tags.a1.json'
    if theater_file.exists():
        for t in qloo.read_json(theater_file).get('results',{}).get('tags',[]):
            tags.setdefault(t.get('tag_id',t.get('id')), {**t,'source':str(theater_file.relative_to(ROOT))})
    regional = {'Rifle Paper Co.','Tijuana Flats','Cigar City Brewing','Cycle Brewing','Publix',
                'Sniper Gang Apparel','Disney Cruise Line','Royal Caribbean International',
                'Delta Air Lines','JetBlue Airways','Virgin Atlantic','Razor Chic','Johnny Dang & Co.'}
    audit=[]
    for b in sorted(brands.values(),key=lambda b:b['name']):
        why = ''
        if set(b['genres']) & {'Academic','Healthcare','Sports Organization','Attraction'}:
            why = 'institution/team/attraction (conservative removal including leagues)'
        elif b['name'] == 'Universal Orlando Resort':
            why = 'local tourist attraction'
        elif b['name'] in regional:
            why = 'regional origin / physical-location association; conservative confound exclusion'
        elif b['name'] == 'Magnolia':
            why = 'ambiguous entity metadata (retail and spirits)'
        audit.append({**b,'excluded':bool(why),'reason':why})
    # Exact native IDs; domain selection is frozen before any new geo affinities.
    choices = {
      'food': ['restaurant:coffee_shop','coffee_roasters','restaurant:bakery','restaurant:fine_dining',
               'restaurant:hamburger','restaurant:barbecue','restaurant:mexican','restaurant:italian',
               'restaurant:japanese','restaurant:vegan','restaurant:vegetarian','restaurant:asian_fusion'],
      'arts': ['museum','art_gallery','art_center','history_museum','science_museum','childrens_museum',
               'live_music_venue','performing_arts_theater'],
      'wellness': ['fitness_center','yoga_studio','spa','massage_spa','swimming_pool',
                   'physical_fitness_program','martial_arts_school','boxing_gym']}
    selected=[]
    for domain, suffixes in choices.items():
        for suffix in suffixes:
            tid='urn:tag:genre:place:'+suffix
            if tid not in tags:
                raise ValueError('Native taxonomy ID not verified: '+tid)
            t=tags[tid]
            selected.append({'id':tid,'name':t['name'],'domain':domain,'source':t['source']})
    freeze(E/'candidates.json', {'brands':audit,'tags':selected})
    pooled=sorted((b for b in audit if b['pooled'] and not b['excluded']),
                  key=lambda b:hashlib.sha256(('civilizr-exp2:'+b['id']).encode()).hexdigest())[:24]
    chosen=sorted({b['id'] for b in pooled} | {b['id'] for b in audit if b['independent'] and not b['excluded']})
    freeze(E/'panels.json',{'brand_ids':chosen,'rule':'all eligible independent brands plus first 24 SHA256(civilizr-exp2:ID) pooled brands; union under take=50 limit'})
    qloo.write_csv(E/'candidate_audit.csv',[{**b,'selected':b['id'] in chosen} for b in audit])
    print('Fixed candidates:',sum(not b['excluded'] for b in audit),'brands;',len(selected),'tags')


def geographies():
    original=qloo.read_json(ROOT/'localities.json')
    areas=[]
    for a in original:
        if a.get('verified') and a['slug']!='orlando':
            areas.append({'slug':a['slug'],'name':a['name'],'city':'Orlando','role':a['role'],
                **a['location'],'center_source':a['source'],
                'limitation':'Qloo locality coordinate, not independently verified geometric centroid; central-area proxy'})
    sources=qloo.read_json(E/'sources/initial_manifest.json')
    for slug,name in [('mills_50','Mills 50'),('thornton_park','Thornton Park')]:
        html=(E/'sources'/f'{slug}.html').read_text(encoding='utf8')
        m=re.search(r'"centerPoint"\s*:\s*"([\d.-]+),([\d.-]+)"',html)
        if not m:
            raise ValueError('Official anchor missing: '+slug)
        areas.append({'slug':slug,'name':name,'city':'Orlando','role':'target' if slug=='mills_50' else 'neutral',
            'lat':float(m[1]),'lon':float(m[2]),'center_source':next(s['url'] for s in sources if s['id']==slug),
            'limitation':'City-listed district address anchor, not district centroid or complete boundary'})
    a=next(a for a in original if a['slug']=='orlando')
    areas.append({'slug':'city_district','name':'City District (downtown anchor proxy)','city':'Orlando','role':'neutral',
        'lat':a['location']['lat'],'lon':a['location']['lon'],
        'center_source':a['source'],
        'limitation':'Both CBD lookups failed; use saved Qloo Orlando downtown anchor coordinate ONLY, with fixed 1 km polygon. Not the Orlando locality or City District boundary.'})
    atl=qloo.read_json(E/'sources/atlanta_neighborhoods.json')
    for f in atl['features']:
        lon,lat=centroid(f['geometry']['coordinates'][0])
        assert inside(lon,lat,f['geometry'])
        areas.append({'slug':'atl_'+f['properties']['NAME'].lower().replace(' ','_'),
            'name':f['properties']['NAME'],'city':'Atlanta','role':'cross_city','lat':lat,'lon':lon,
            'center_source':'experiment2/sources/atlanta_neighborhoods.json',
            'reference_boundary_area_km2':f['properties']['ACRES']*0.0040468564224,
            'limitation':'Area centroid of official City polygon; equal-area proxy can cross official border'})
    features=[]
    for a in areas:
        variants=[('base',1000,0)]
        if a['slug'] in ['winter_park','mills_50','pine_hills']:
            variants += [('r800',800,0),('r1200',1200,0),('east200',1000,200)]
        elif a['city']=='Atlanta':
            variants += [('east200',1000,200)]
        for variant,radius,east in variants:
            geom=polygon(a['lat'],a['lon'],radius,east)
            features.append({'type':'Feature','geometry':geom,'properties':{**a,'variant':variant,
                'radius_m':radius,'east_shift_m':east,
                'sample_lon':a['lon']+math.degrees(east/(R*math.cos(math.radians(a['lat'])))),
                'area_km2':16*radius*radius*math.sin(2*math.pi/32)/1e6,
                'area_method':'regular polygon local tangent approximation; negligible error at <=1.2 km'}})
    freeze(E/'geographies.json',{'type':'FeatureCollection','features':features})
    qloo.write_csv(E/'geographies.csv',[f['properties'] for f in features])
    names=['City District','Curry Ford West','Gateway District','Ivanhoe Village','Parramore District',
           'SoDo District','The Milk District','Thornton Park District','West Lakes District']
    selection=sorted([{'name':n,'sha256':hashlib.sha256(('civilizr-exp2:'+n).encode()).hexdigest()} for n in names],key=lambda x:x['sha256'])
    freeze(E/'neutral_selection.json',{'eligible':selection,'selected':[x['name'] for x in selection[:2]]})


def profile(f,domain,subset=False):
    a=f['properties']; c=qloo.read_json(E/'candidates.json')
    ids=qloo.read_json(E/'panels.json')['brand_ids'] if domain=='brands' else sorted(t['id'] for t in c['tags'])
    if subset:
        ids=ids[::2]
    params={'filter.type':'urn:entity:brand' if domain=='brands' else 'urn:tag',
            'signal.location':wkt(f['geometry']),'take':len(ids),'bias.trends':'off',
            'filter.results.entities' if domain=='brands' else 'filter.results.tags':ids}
    if domain=='tags':
        params['filter.parents.types']='urn:entity:place'
    return {'id':a['slug']+'_'+a['variant']+'_'+domain+('_subset' if subset else ''),
            'endpoint':'/v2/insights','params':params,'kind':'fixed_profile','area':a['slug'],
            'dimension':domain,'variant':a['variant'],'subset':subset,'city':a['city']}


def plans():
    features=qloo.read_json(E/'geographies.json')['features']
    pilot=[]; main=[]; sensitivity=[]; cross=[]; repeats=[]; subsets=[]
    for f in features:
        a=f['properties']
        for domain in ['brands','tags']:
            req=profile(f,domain)
            if a['city']=='Atlanta':
                cross.append(req)
            elif a['variant']!='base':
                sensitivity.append(req)
            elif a['slug'] in ['winter_park','pine_hills']:
                pilot.append(req); repeats.append(req); subsets.append(profile(f,domain,True))
            else:
                main.append(req)
    for n,rs in [('02-pilot',pilot),('03-main',main),('04-sensitivity',sensitivity),
                 ('05-cross-city',cross),('06-subsets',subsets),('07-repeat',repeats)]:
        plan(n,rs)


def inventory():
    features=qloo.read_json(E/'geographies.json')['features']
    coords=[p for f in features if f['properties']['city']=='Orlando' for p in f['geometry']['coordinates'][0]]
    bbox=','.join(str(round(x,7)) for x in [min(p[1] for p in coords)-.001,min(p[0] for p in coords)-.001,
                                         max(p[1] for p in coords)+.001,max(p[0] for p in coords)+.001])
    query=f'[out:json][timeout:35];(nwr[amenity]({bbox});nwr[shop]({bbox});nwr[leisure]({bbox});nwr[tourism]({bbox}););out center tags;'
    freeze(E/'inventory_request.json',{'url':'https://overpass-api.de/api/interpreter','method':'POST','query':query,
                                     'attribution':'© OpenStreetMap contributors, ODbL; https://www.openstreetmap.org/copyright'})
    out=E/'sources/osm_inventory.json'
    if out.exists():
        print('Inventory snapshot already exists; no network call'); return
    req=Request('https://overpass-api.de/api/interpreter',data=urlencode({'data':query}).encode(),
                headers={'User-Agent':'Civilizr-disposable-research/0.2'})
    at=qloo.now()
    try:
        with urlopen(req,timeout=45) as res:
            body=res.read(12*1024*1024+1)
            if len(body)>12*1024*1024: raise ValueError('Inventory response too large')
            out.write_bytes(body)
            qloo.save_json(out.with_suffix('.meta.json'),{'at':at,'status':res.status,
                'sha256':hashlib.sha256(body).hexdigest(),'request_file':'experiment2/inventory_request.json'})
            print('OSM snapshot elements:',len(json.loads(body).get('elements',[])))
    except Exception as exc:
        qloo.save_json(E/'sources/osm_inventory_failure.json',{'at':at,'error':str(exc),'request_file':'experiment2/inventory_request.json'})
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['discovery','freeze','plans','run','inventory'])
    p.add_argument('--stage');p.add_argument('--budget',type=int,default=5)
    args=p.parse_args()
    if args.command=='discovery': discovery()
    elif args.command=='freeze': candidates();geographies()
    elif args.command=='plans': plans()
    elif args.command=='inventory': inventory()
    else: return run(args.stage,args.budget)


if __name__=='__main__':
    sys.exit(main())
