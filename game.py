"""Build held-out guesses, then ablate each input against identical candidate panels."""
from datetime import datetime,timezone
import json
from qloo_client import ROOT,QlooError
from scoring import scores,sensitivity
from signals import kind,pick_domains,validate_context,informative

CATALOG=json.loads((ROOT/'data/catalog.json').read_text(encoding='utf-8'))
PRESETS=[{'id':'overthinker','name':'The overthinker','line':'Good coffee. Complicated television.','aliases':['radiohead','blue_bottle','severance']},
         {'id':'comfort','name':'The comfort zone','line':'The hits are hits for a reason.','aliases':['taylor','starbucks','friends']},
         {'id':'sidequest','name':'The side quest','line':'Heavy guitars. Questionable sleep schedule.','aliases':['metallica','nike','elden_ring']}]


def build(client,interests,update=lambda **kw:None):
    domains=pick_domains(interests)
    if len(domains)!=2:raise QlooError('This mix leaves too few categories to guess. Swap a pick.','coverage')
    for interest in interests:
        if kind(interest)!='entity':validate_context(client,interest,domains)
    full={}; warnings=[]; ablations={}; start=datetime.now(timezone.utc).isoformat()
    for d in domains:
        update(message='Finding a few things you did not tell us.',progress=12+len(full)*12)
        discovery=client.insights(interests,d)
        panel=list(scores(discovery))
        if len(panel)<10: raise QlooError('Qloo has too little evidence for this mix. Swap an interest or try a recorded round.','coverage')
        baseline=client.insights(interests,d,panel)
        if not set(panel)<=scores(baseline).keys(): raise QlooError('Qloo returned an incomplete shortlist. Try another mix.','coverage')
        if not informative(baseline): raise QlooError('Qloo returned a flat shortlist. Try another mix.','coverage')
        full[d]=sorted(baseline,key=lambda x:x['score'],reverse=True)
    # Six untouched categories' guesses, before responses and before any remix.
    predictions=[]
    for rank in range(3):
        for d in domains:
            row=dict(full[d][rank]); row['domain']=d; row['rank']=rank+1; predictions.append(row)
    game={'version':1,'source':'live','generated_at':start,'interests':interests,'domains':domains,'predictions':predictions,
          'full':full,'ablations':ablations,'sensitivity':None,'warnings':warnings}
    update(game=game,message='The guesses are ready. Checking who moves the rankings.',progress=35)
    for n,interest in enumerate(interests):
        smaller=[i for i in interests if i['id']!=interest['id']]; ablations[interest['id']]={}
        for domain in domains:
            try:
                rows=client.insights(smaller,domain,[x['id'] for x in full[domain]])
                valid=scores(rows)
                ablations[interest['id']][domain]=sorted([x for x in rows if x['id'] in valid],key=lambda x:x['score'],reverse=True)
            except QlooError:
                warnings.append('Not enough evidence to compare '+interest['name']+' in '+domain+'.')
        update(message='Checking the mix without '+interest['name']+'.',progress=35+int((n+1)/len(interests)*60))
    game['sensitivity']=sensitivity([{**e,'name':e.get('label',e['name'])} for e in interests],full,ablations)
    if any(kind(e)!='entity' for e in interests):
        game['signal_note']='Tags describe categories. Hobby audiences add the tastes of a group you chose. Removing an audience removes cohort context. Signal families have separate weighting controls; these distances measure model response, not equal shares of personal importance.'
        game['sensitivity']['signal_note']=game['signal_note']
        game['signal_parameters']=parameters_for_receipt(interests)
    update(game=game,progress=100,message='The algorithm would like a word.')
    return game


def parameters_for_receipt(interests):
    from signals import parameters
    return {'signals':parameters(interests),'weights':'Qloo defaults; no custom family weights'}
