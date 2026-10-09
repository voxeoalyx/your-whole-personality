"""Controlled comparison; scripted reactions are NOT human preference ground truth.

python compare_investigators.py --live-model --modes A B C --scenarios positive negative
Reads saved real-Qloo panels by default; never calls Qloo. All modes share candidates.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from investigator import Investigator, accuracy
from model_client import ModelClient
from qloo_client import ROOT

SCENARIOS = {'positive': ['yes']*5, 'negative': ['no']*5, 'unfamiliar': ['unknown']*5,
             'contradiction': ['yes','no','yes','no','unknown']}
MODES = {'A':'llm_only','B':'fixed_qloo','C':'agentic_qloo'}


def run(game, model, mode, reactions, prefix=0):
    engine=Investigator(deepcopy(game),model,mode=MODES[mode])
    start=time.monotonic()
    for n,response in enumerate(reactions):
        if n<prefix:
            # Force identical observed items for an isolated counterfactual branching check.
            p=deepcopy(game['predictions'][n]);engine.predictions.append(p)
            engine.trace.append({'event':'controlled_prefix','result':{'presented':p['id']}})
        else:engine.advance()
        if engine.finished:break
        engine.answer(engine.predictions[-1]['id'],response,n)
    engine.advance()
    result=engine.snapshot()
    result['evaluation']={'mode':mode,'controlled_feedback':True,'forced_prefix':prefix,
                          'seconds':round(time.monotonic()-start,2),
                          'accuracy':accuracy(engine.predictions,engine.answers),
                          'valid_live_agent_run':mode=='B' or not engine.fallback_reason}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live-model',action='store_true')
    parser.add_argument('--modes',nargs='+',choices=list(MODES),default=['A','B','C'])
    parser.add_argument('--scenarios',nargs='+',choices=list(SCENARIOS),default=list(SCENARIOS))
    parser.add_argument('--profile',choices=['overthinker','comfort','sidequest'],default='overthinker')
    parser.add_argument('--forced-prefix',type=int,choices=[0,2],default=0)
    parser.add_argument('--output',default='test-results/investigator-comparison.json')
    args=parser.parse_args()
    if not args.live_model and any(m!='B' for m in args.modes):parser.error('A and C need --live-model; no simulated agent results.')
    model=ModelClient()
    if args.live_model and not model.key:parser.error('NVIDIA_API_KEY is missing; no live results claimed.')
    game=json.loads((ROOT/'data/demos.json').read_text(encoding='utf-8'))[args.profile]
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    report={'at':datetime.now(timezone.utc).isoformat(),'profile':args.profile,'model':model.model,
            'candidate_source':'frozen real Qloo panels shared across all modes; A sees names/types only',
            'limitation':'A has no live Qloo access or scores, but candidate selection is Qloo-derived. Scripted feedback cannot measure relevance or superiority.',
            'runs':[]}
    for mode in args.modes:
        for scenario in args.scenarios:
            result=run(game,model,mode,SCENARIOS[scenario],args.forced_prefix)
            result['evaluation']['scenario']=scenario
            report['runs'].append(result)
            output.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
            print(json.dumps({'mode':mode,'scenario':scenario,**result['evaluation'],
                              'predictions':[p['name'] for p in result['game']['predictions']],
                              'fallback':result['game']['investigator']['fallback_reason']}),flush=True)
    print('Saved '+str(output),flush=True)


if __name__=='__main__':main()
