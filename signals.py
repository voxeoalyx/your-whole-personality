"""Typed input signals. A hobby audience is explicit cohort context, never inferred identity."""
import re

FIELDS={'entity':'signal.interests.entities','tag':'signal.interests.tags','audience':'signal.demographics.audiences'}
DOMAINS=['tv_show','movie','brand','videogame','artist','podcast','book']
HOBBIES='urn:audience:hobbies_and_interests'
TAG_TYPES={'urn:tag:genre:media','urn:tag:genre:music','urn:tag:genre:brand','urn:tag:genre:place',
           'urn:tag:category:place','urn:tag:keyword:qloo','urn:tag:subgenre:qloo'}
NAMES={'tv_show':'TV','movie':'Movies','podcast':'Podcasts','podcaster':'Podcasts','book':'Books','author':'Books',
       'artist':'Music','album':'Music','brand':'Brands','place':'Places','videogame':'Games'}

def kind(interest):
    return interest.get('type') if isinstance(interest,dict) and interest.get('type') in {'tag','audience'} else 'entity'

def parameters(interests):
    grouped={field:[] for field in FIELDS.values()}
    for interest in interests:
        grouped[FIELDS[kind(interest)]].append(interest['id'] if isinstance(interest,dict) else interest)
    return {k:sorted(set(v)) for k,v in grouped.items() if v}

def pick_domains(interests):
    used=set()
    for e in interests:
        if kind(e)=='entity':used.add(e['type'])
        elif kind(e)=='tag':used.update(e.get('parent_types',[]))
    # A cohort has no entity output domain; tags exclude their documented parent domains.
    return [d for d in DOMAINS if d not in used][:2]

def normalize(raw,family):
    ident=raw.get('id',''); taxonomy=raw.get('type',''); name=raw.get('name','')
    if not isinstance(ident,str) or not re.fullmatch(r'urn:[a-zA-Z0-9_:.-]+',ident) or not isinstance(name,str):return None
    parents=sorted({x.get('type','').removeprefix('urn:entity:') for x in raw.get('parents',[]) if x.get('type','').startswith('urn:entity:')})
    if family=='audience':
        if taxonomy!=HOBBIES or not ident.startswith(HOBBIES+':'):return None
        label='hobby audience'; detail='Uses the tastes of this hobby group. You choose the group; we do not infer membership.'
    elif family=='tag':
        if taxonomy not in TAG_TYPES or not ident.startswith(taxonomy+':'):return None
        source=' / '.join(dict.fromkeys(NAMES.get(p,p.replace('_',' ')) for p in parents)) or 'Cultural'
        if taxonomy=='urn:tag:genre:place' and len(ident.split(':'))>5:
            source={'restaurant':'Restaurants','hotel':'Hotels'}.get(ident.split(':')[4],source)
        label=source+' '+taxonomy.split(':')[2]+' tag'
        detail='Interest in this '+source.lower()+' category, not proof that you do the activity.'
    else:return None
    return {'id':ident,'name':name[:160],'type':family,'taxonomy':taxonomy,'parent_types':parents,
            'type_label':label,'label':name[:160]+' ('+label+')','detail':detail,'image':None}

def informative(rows,minimum=10):
    from scoring import scores
    values=scores(rows)
    return len(values)>=minimum and len(set(values.values()))>1

def validate_context(client,interest,domains):
    """A successful mixed request can hide a flat tag behind entity scores."""
    from qloo_client import QlooError
    from scoring import scores
    for domain in domains:
        rows=client.insights([interest],domain,take=20)
        if not informative(rows) and len(scores(rows))>=10:
            # A tied top-20 can hide useful variation elsewhere. Check a different fixed panel.
            from game import CATALOG
            reference=next(e for e in CATALOG if e['alias']==('blue_bottle' if domain=='artist' else 'radiohead'))
            panel=list(scores(client.insights([reference],domain,take=20)))
            rows=client.insights([interest],domain,panel) if len(panel)>=10 else []
        if not informative(rows):
            raise QlooError('Qloo found '+interest['name']+' but returned flat or insufficient '+domain.replace('_',' ')+
                            ' recommendations for this '+kind(interest)+'. It cannot be used in this round; no substitute was selected.',
                            'unsupported',[interest['id']])
