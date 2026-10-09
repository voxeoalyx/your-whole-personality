"""Offline fixed-panel, boundary, inventory and baseline analysis. No dependencies."""
import collections
import itertools
import math
import statistics as st
import hashlib
from pathlib import Path
import qloo
from experiment2 import E, ROOT, distance, inside

OUT=E/'reports'


def ranks(values):
    """Average ranks; larger scores get larger ranks. Ties are never broken by ID."""
    order=sorted(range(len(values)),key=lambda i:values[i]); out=[0.0]*len(values)
    start=0
    while start<len(order):
        end=start+1
        while end<len(order) and values[order[end]]==values[order[start]]: end+=1
        for i in order[start:end]: out[i]=(start+1+end)/2
        start=end
    return out


def corr(x,y):
    if len(x)!=len(y) or len(x)<2: return None
    ax,ay=st.mean(x),st.mean(y)
    dx=[v-ax for v in x];dy=[v-ay for v in y]
    den=math.sqrt(sum(v*v for v in dx)*sum(v*v for v in dy))
    return max(-1,min(1,sum(a*b for a,b in zip(dx,dy))/den)) if den>0 else None


def rho(x,y): return corr(ranks(x),ranks(y))


def dissim(a,b,score=False):
    if not a or set(a)!=set(b): return None
    ids=sorted(a)
    c=corr([a[i] for i in ids],[b[i] for i in ids]) if score else rho([a[i] for i in ids],[b[i] for i in ids])
    return (1-c)/2 if c is not None else None


def med(xs):
    xs=[x for x in xs if x is not None]
    return st.median(xs) if xs else None


def csv(name,rows): qloo.write_csv(OUT/(name+'.csv'),rows)


def read_profiles():
    c=qloo.read_json(E/'candidates.json'); chosen=set(qloo.read_json(E/'panels.json')['brand_ids'])
    domains={'brands':chosen,
             'brands_independent':{b['id'] for b in c['brands'] if b['id'] in chosen and b['independent']},
             'brands_pooled':{b['id'] for b in c['brands'] if b['id'] in chosen and b['pooled']}}
    domains.update({d:{t['id'] for t in c['tags'] if t['domain']==d} for d in ['food','arts','wellness']})
    names={b['id']:b['name'] for b in c['brands']};names.update({t['id']:t['name'] for t in c['tags']})
    valid={}; coverage=[]; long=[]; requests=[]
    for folder in sorted((E/'runs').iterdir()):
        mf=folder/'manifest.json'
        if not mf.exists(): continue
        for spec in qloo.read_json(mf)['identity']['plan']['requests']:
            if spec.get('kind')!='fixed_profile': continue
            meta=folder/(spec['id']+'.meta.json')
            if not meta.exists(): continue
            m=qloo.read_json(meta)
            payload=qloo.read_json(folder/m['raw_file']) if m.get('ok') else {}
            result=payload.get('results',{})
            rows=result.get('entities',result.get('tags',[])); ids=[r.get('entity_id',r.get('tag_id',r.get('id'))) for r in rows]
            scores={i:r.get('query',{}).get('affinity') for i,r in zip(ids,rows)}
            expected=set(spec['params'].get('filter.results.entities',spec['params'].get('filter.results.tags',[])))
            unexpected=set(ids)-expected; duplicates=len(ids)!=len(set(ids))
            panel=payload.get('query',{}).get('geospatial',{}).get('panel_size',{})
            requests.append({'stage':folder.name,'request':spec['id'],'http_status':m['http_status'],
                'expected':len(expected),'returned':len(rows),'unexpected':';'.join(sorted(unexpected)),
                'duplicates':duplicates,'panel_context_undocumented':panel.get('context'),
                'panel_target_undocumented':panel.get('target'),'raw_file':str((folder/m['raw_file']).relative_to(ROOT))})
            for d,full in domains.items():
                if (d.startswith('brands'))!=(spec['dimension']=='brands'): continue
                desired=full & expected if spec.get('subset') else full
                missing=desired-set(scores)
                numeric={i:scores[i] for i in desired if i in scores and isinstance(scores[i],(float,int)) and math.isfinite(scores[i])}
                complete=not missing and len(numeric)==len(desired) and not duplicates and not unexpected and m.get('ok')
                informative=len(set(numeric.values()))>=5
                key=(folder.name,spec['area'],spec['variant'],d)
                if complete and informative: valid[key]=numeric
                coverage.append({'stage':folder.name,'area':spec['area'],'variant':spec['variant'],'domain':d,
                    'subset':bool(spec.get('subset')),'expected':len(desired),'scored':len(numeric),
                    'complete':bool(complete),'distinct_scores':len(set(numeric.values())),'informative':informative,
                    'missing':';'.join(names[i] for i in sorted(missing)),
                    'raw_file':str((folder/m['raw_file']).relative_to(ROOT))})
                if numeric:
                    ordered=sorted(numeric); rr=ranks([-numeric[i] for i in ordered])
                    for i,r in zip(ordered,rr):
                        long.append({'stage':folder.name,'area':spec['area'],'variant':spec['variant'],'domain':d,
                            'id':i,'name':names[i],'score':numeric[i],'rank_among_returned':r,
                            'complete_panel':bool(complete),'subset':bool(spec.get('subset'))})
    csv('coverage',coverage);csv('request_diagnostics',requests);csv('fixed_fingerprints',long)
    return valid,domains,names,coverage


def venue_category(t):
    if t.get('access')=='private' or t.get('disused')=='yes': return None
    a,s,l,tr=t.get('amenity'),t.get('shop'),t.get('leisure'),t.get('tourism')
    if a in ['restaurant','cafe','fast_food','bar','pub','ice_cream','nightclub','cinema','theatre','arts_centre','library']:
        return a
    if tr in ['museum','gallery']: return tr
    if l in ['fitness_centre','sports_centre','dance']: return l
    if l=='swimming_pool' and (t.get('name') or t.get('access')=='yes'): return 'swimming_pool'
    if s in ['bakery','coffee','tea','clothes','shoes','books','music','art','beauty','hairdresser','massage','supermarket','convenience','department_store']:
        return s
    if s and s not in ['no','vacant','closed']: return 'other_shop'
    return None


def inventory(features):
    f=E/'sources/osm_inventory.json'
    if not f.exists(): return {}
    data=qloo.read_json(f)
    if data.get('remark'): raise ValueError('Overpass reported incomplete/error output: '+data['remark'])
    allvenues=[]; kept=[]; duplicates=[]
    for e in sorted(data['elements'],key=lambda e:(e['type'],e['id'])):
        tags=e.get('tags',{});cat=venue_category(tags);loc=e if 'lat' in e else e.get('center',{})
        if not cat or 'lat' not in loc: continue
        v={'osm_id':e['type']+'/'+str(e['id']),'name':tags.get('name',''),'category':cat,'lat':loc['lat'],'lon':loc['lon'],
           'brand':tags.get('brand',''),'cuisine':tags.get('cuisine',''),'source_url':'https://www.openstreetmap.org/'+e['type']+'/'+str(e['id']),
           'tags_json':qloo.canonical(tags)}
        allvenues.append(v)
        match=next((k for k in kept if v['name'] and v['name'].casefold()==k['name'].casefold() and cat==k['category'] and distance(v,k)<30),None)
        if match: duplicates.append({**v,'duplicate_of':match['osm_id']})
        else: kept.append(v)
    cats=sorted({v['category'] for v in kept});counts={};summaries=[];located=[]
    for f in features:
        p=f['properties']
        if p['city']!='Orlando': continue
        raw=[v for v in allvenues if inside(v['lon'],v['lat'],f['geometry'])]
        local=[v for v in kept if inside(v['lon'],v['lat'],f['geometry'])]
        ct=collections.Counter(v['category'] for v in local)
        counts[(p['slug'],p['variant'])]={c:ct[c] for c in cats}
        summaries.append({'area':p['slug'],'variant':p['variant'],'raw_mapped_venues':len(raw),'deduplicated_venues':len(local),
            'named_venues':sum(bool(v['name']) for v in local),'sparse_under_10':len(local)<10,**{c:ct[c] for c in cats}})
        located.extend({'area':p['slug'],'variant':p['variant'],**v} for v in local)
    csv('inventory_counts',summaries);csv('inventory_venues',located);csv('inventory_duplicates',duplicates)
    qloo.save_json(OUT/'inventory_metadata.json',{'osm_base_timestamp':data.get('osm3s',{}).get('timestamp_osm_base'),
        'raw_elements':len(data['elements']),'classified':len(allvenues),'deduplicated':len(kept),
        'categories':cats,'attribution':'© OpenStreetMap contributors, ODbL; https://www.openstreetmap.org/copyright',
        'limitations':'Mapped POIs, not exhaustive current operating businesses; node locations and way/relation bounding-box centers; category mapping and dedup heuristics; no independent completeness audit.'})
    return counts


def hellinger(a,b):
    sa,sb=sum(a.values()),sum(b.values())
    if not sa or not sb: return None
    return math.sqrt(sum((math.sqrt(a.get(k,0)/sa)-math.sqrt(b.get(k,0)/sb))**2 for k in set(a)|set(b))/2)


def linear_fit(xs,ys):
    """Small OLS with training-only scaling; tiny diagonal jitter for numerical rank."""
    p=len(xs[0]);means=[st.mean(x[k] for x in xs) for k in range(p)]
    scales=[st.pstdev(x[k] for x in xs) or 1 for k in range(p)]
    z=[[1]+[(x[k]-means[k])/scales[k] for k in range(p)] for x in xs]
    mat=[[sum(r[i]*r[j] for r in z)+(1e-10 if i==j and i>0 else 0) for j in range(p+1)]
         +[sum(r[i]*y for r,y in zip(z,ys))] for i in range(p+1)]
    for i in range(p+1):
        pivot=max(range(i,p+1),key=lambda j:abs(mat[j][i]));mat[i],mat[pivot]=mat[pivot],mat[i]
        if abs(mat[i][i])<1e-12: return None
        divisor=mat[i][i];mat[i]=[v/divisor for v in mat[i]]
        for j in range(p+1):
            if j!=i:
                factor=mat[j][i];mat[j]=[a-factor*b for a,b in zip(mat[j],mat[i])]
    beta=[row[-1] for row in mat]
    return lambda x: beta[0]+sum(beta[k+1]*(x[k]-means[k])/scales[k] for k in range(p))


def baselines(pairs,domain):
    rows=[r for r in pairs if r['domain']==domain]; result=[];predictions=[]
    for label,cols in [('geography',['log_distance']),('inventory',['inventory_distance','inventory_count_difference']),
                       ('both',['log_distance','inventory_distance','inventory_count_difference'])]:
        use=[r for r in rows if all(r[c] is not None for c in cols)]
        areas=sorted({r['a'] for r in use}|{r['b'] for r in use});err=[];null=[]
        for area in areas:
            train=[r for r in use if area not in [r['a'],r['b']]]; test=[r for r in use if area in [r['a'],r['b']]]
            if len(train)<len(cols)+3: continue
            fn=linear_fit([[r[c] for c in cols] for r in train],[r['qloo_distance'] for r in train])
            if fn is None: continue
            avg=st.mean(r['qloo_distance'] for r in train)
            for r in test:
                pred=fn([r[c] for c in cols]);err.append((r['qloo_distance']-pred)**2);null.append((r['qloo_distance']-avg)**2)
                predictions.append({'domain':domain,'model':label,'held_out':area,'a':r['a'],'b':r['b'],
                    'actual':r['qloo_distance'],'predicted':pred,'residual':r['qloo_distance']-pred})
        result.append({'domain':domain,'model':label,'pairs':len(use),'areas':len(areas),
            'held_out_endpoint_predictions':len(err),'rmse':math.sqrt(st.mean(err)) if err else None,
            'training_mean_rmse':math.sqrt(st.mean(null)) if null else None,
            'held_out_r2_vs_training_mean':1-sum(err)/sum(null) if null and sum(null)>0 else None})
    return result,predictions


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    valid,domains,names,coverage=read_profiles()
    features=qloo.read_json(E/'geographies.json')['features']
    features += [qloo.read_json(p) for p in sorted((E/'sources').glob('*_east200.geojson'))]
    geo={f['properties']['slug']:f['properties'] for f in features if f['properties']['variant']=='base'}
    inv=inventory(features)
    base={(a,d):v for (stage,a,variant,d),v in valid.items() if stage in ['02-pilot','03-main','05-cross-city'] and variant=='base'}
    pairs=[];robust=[];domain_summary=[];baseline=[];cv=[];panelchecks=[];repeats=[];cross=[]
    orlando=sorted(a for a,p in geo.items() if p['city']=='Orlando')
    for d in domains:
        usable=[a for a in orlando if (a,d) in base]
        for a,b in itertools.combinations(usable,2):
            km=distance(geo[a],geo[b])/1000; ca,cb=inv.get((a,'base'),{}),inv.get((b,'base'),{})
            pairs.append({'domain':d,'a':a,'b':b,'distance_km':km,'proxy_circles_overlap':km<2,
                'log_distance':math.log1p(km),'qloo_distance':dissim(base[a,d],base[b,d]),
                'score_distance':dissim(base[a,d],base[b,d],True),'inventory_distance':hellinger(ca,cb),
                'inventory_count_difference':abs(math.log1p(sum(ca.values()))-math.log1p(sum(cb.values()))) if ca and cb else None,
                'inventory_sparse':min(sum(ca.values()),sum(cb.values()))<10})
        dp=[r for r in pairs if r['domain']==d]
        for (stage,a,var,dom),v in valid.items():
            if dom!=d or var=='base' or a not in orlando or (a,d) not in base: continue
            others=[r['qloo_distance'] for r in dp if a in [r['a'],r['b']]]
            change=dissim(base[a,d],v)
            robust.append({'stage':stage,'domain':d,'area':a,'variant':var,'within_distance':change,
                'exact_scores_equal':base[a,d]==v,
                'median_between_for_area':med(others),'nearest_between_for_area':min(others) if others else None,
                'exceeds_nearest_between':change>min(others) if others else None})
        # Gate uses the prespecified three-neighborhood perturbation set only.
        prespec=[r for r in robust if r['domain']==d and r['stage']=='04-sensitivity']
        all_within=[r['within_distance'] for r in prespec]
        mb=med(r['qloo_distance'] for r in dp);mw=med(all_within)
        sensitive_complete=len(prespec)==9
        adequately_covered=len(domains[d])>=8 and len(usable)>=8 and sensitive_complete
        rd={'domain':d,'candidates':len(domains[d]),'complete_orlando':len(usable),
            'valid_perturbations_of_9':len(prespec),'adequate_coverage':adequately_covered,
            'median_between':mb,'median_within':mw,'max_within':max(all_within) if all_within else None,
            'within_between_ratio':mw/mb if mb else None,
            'robust_screen':bool(adequately_covered and mb>=.05 and mw<=mb/3),
            'geo_distance_rho':rho([r['distance_km'] for r in dp],[r['qloo_distance'] for r in dp]) if dp else None,
            'rank_score_agreement':rho([r['qloo_distance'] for r in dp],[r['score_distance'] for r in dp]) if dp else None}
        bp=[r for r in dp if r['inventory_distance'] is not None]
        rd['inventory_distance_rho']=rho([r['inventory_distance'] for r in bp],[r['qloo_distance'] for r in bp]) if bp else None
        domain_summary.append(rd)
        for scope,eligible in [('all_available',pairs),('inventory_ge10',[r for r in pairs if not r['inventory_sparse']])]:
            bs,ps=baselines(eligible,d)
            baseline += [{**r,'scope':scope} for r in bs]
            cv += [{**r,'scope':scope} for r in ps]
        matrix=[]
        for a in usable:
            matrix.append({'area':a,**{b:1-2*dissim(base[a,d],base[b,d]) for b in usable}})
        csv(d+'_spearman_matrix',matrix)
        # Deterministic halves assess candidate dependence without imputation.
        for offset in [0,1]:
            ids=set(sorted(domains[d])[offset::2]); common=[]
            for r in dp:
                av={i:v for i,v in base[r['a'],d].items() if i in ids};bv={i:v for i,v in base[r['b'],d].items() if i in ids}
                ds=dissim(av,bv)
                if ds is not None: common.append((r['qloo_distance'],ds))
            panelchecks.append({'domain':d,'check':f'alternating_half_{offset}','candidates':len(ids),'pairs':len(common),
                'distance_order_rho':rho([r[0] for r in common],[r[1] for r in common]) if common else None})
    for (stage,a,var,d),v in valid.items():
        original=base.get((a,d))
        if stage=='07-repeat':
            repeats.append({'area':a,'domain':d,'valid_complete_comparison':bool(original),
                            'rho':1-2*dissim(original,v) if original else None,
                            'exact_numeric_equal':original==v if original else None})
        if stage=='06-subsets' and original:
            subset={i:original[i] for i in v}
            panelchecks.append({'domain':d,'check':'reissued_subset_'+a,'candidates':len(v),'pairs':None,
                                'distance_order_rho':None,'within_profile_rho':1-2*dissim(subset,v)})
    for d in domains:
        for a in orlando:
            if (a,d) not in base: continue
            matches=[]
            for b in sorted(g for g,p in geo.items() if p['city']=='Atlanta'):
                if (b,d) not in base: continue
                shift=valid.get(('05-cross-city',b,'east200',d));av=base[a,d];bv=base[b,d]
                matches.append((dissim(av,bv),b,shift))
            matches.sort(key=lambda m:(m[0],m[1]))
            if not matches: continue
            best=matches[0]; shifted=sorted((dissim(base[a,d],s),b) for _,b,s in matches if s)
            # Generic Orlando profile is the mean of within-profile ranks, leave query area out.
            others=[v for (g,dom),v in base.items() if dom==d and g in orlando and g!=a]
            ids=sorted(domains[d]);rank_vectors=[ranks([v[i] for i in ids]) for v in others]
            generic={i:st.mean(r[k] for r in rank_vectors) for k,i in enumerate(ids)} if rank_vectors else {}
            generic_matches=sorted((dissim(generic,base[b,d]),b) for _,b,_ in matches) if generic else []
            half_best=[]
            for off in [0,1]:
                sub=set(ids[off::2]); scored=[]
                for _,b,_ in matches:
                    ds=dissim({i:v for i,v in base[a,d].items() if i in sub},{i:v for i,v in base[b,d].items() if i in sub})
                    if ds is not None: scored.append((ds,b))
                half_best.append(min(scored)[1] if scored else None)
            source_shift=valid.get(('04-sensitivity',a,'east200',d),valid.get(('08-additional-shifts',a,'east200',d)))
            source_matches=sorted((dissim(source_shift,base[b,d]),b) for _,b,_ in matches) if source_shift else []
            cross.append({'domain':d,'orlando':a,'best_atlanta':best[1],'rho':1-2*best[0],
                'available_atlanta':len(matches),'runner_up':matches[1][1] if len(matches)>1 else None,
                'distance_margin':matches[1][0]-best[0] if len(matches)>1 else None,
                'best_after_atlanta_shift':shifted[0][1] if shifted else None,
                'best_after_orlando_shift':source_matches[0][1] if source_matches else None,
                'generic_orlando_best':generic_matches[0][1] if generic_matches else None,
                'half0_best':half_best[0],'half1_best':half_best[1],
                'shared_top_quartile':';'.join(names[i] for i in ids if i in sorted(base[a,d],key=base[a,d].get,reverse=True)[:max(2,len(ids)//4)] and i in sorted(base[best[1],d],key=base[best[1],d].get,reverse=True)[:max(2,len(ids)//4)])})
    csv('pairwise_baselines',pairs);csv('geographic_sensitivity',robust);csv('domain_summary',domain_summary)
    csv('baseline_cross_validation',baseline);csv('baseline_predictions',cv);csv('candidate_sensitivity',panelchecks)
    csv('repeat_checks',repeats);csv('cross_city_matches',cross)
    exact_repeats=[]
    repeat_dir=E/'runs/07-repeat'
    if (repeat_dir/'manifest.json').exists():
        for spec in qloo.read_json(repeat_dir/'manifest.json')['identity']['plan']['requests']:
            original=E/'runs/02-pilot'/(spec['id']+'.a1.json')
            repeated=repeat_dir/(spec['id']+'.a1.json')
            if original.exists() and repeated.exists():
                before,after=qloo.read_json(original),qloo.read_json(repeated)
                rr=before.get('results',{})
                returned=rr.get('entities',rr.get('tags',[]))
                wanted=spec['params'].get('filter.results.entities',spec['params'].get('filter.results.tags',[]))
                exact_repeats.append({'request':spec['id'],'results_exact_equal':before.get('results')==after.get('results'),
                                      'includes_missing_candidates':len(returned)!=len(wanted),
                                      'note':'Exact equality does not imply complete scoring or historical stability'})
    csv('repeat_request_equality',exact_repeats)
    residuals=[]
    grouped=collections.defaultdict(list)
    for r in cv:
        if r['model']=='both' and r['scope']=='inventory_ge10': grouped[(r['domain'],r['a'],r['b'])].append(r)
    for (d,a,b),rs in grouped.items():
        residuals.append({'domain':d,'a':a,'b':b,'actual':rs[0]['actual'],
            'mean_endpoint_heldout_prediction':st.mean(r['predicted'] for r in rs),
            'mean_residual':st.mean(r['residual'] for r in rs),
            'warning':'Unexplained Qloo variation, not externally validated culture'})
    csv('baseline_residual_contrasts',sorted(residuals,key=lambda r:abs(r['mean_residual']),reverse=True))
    # Brands pooled versus independent, on the same complete locations only.
    pmap={(r['domain'],r['a'],r['b']):r['qloo_distance'] for r in pairs}
    common=[(pmap['brands_pooled',a,b],pmap['brands_independent',a,b]) for a,b in itertools.combinations(orlando,2)
            if ('brands_pooled',a,b) in pmap and ('brands_independent',a,b) in pmap]
    qloo.save_json(OUT/'summary.json',{'domains':domain_summary,'brand_panel_comparison_pairs':len(common),
        'pooled_independent_pair_distance_rho':rho([x for x,y in common],[y for x,y in common]) if common else None,
        'network_attempts':sum(len(p.read_text(encoding='utf8').splitlines()) for p in (E/'runs').glob('*/requests.jsonl')),
        'analysis_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'at':qloo.now()})
    print(qloo.canonical(domain_summary))


if __name__=='__main__': main()
