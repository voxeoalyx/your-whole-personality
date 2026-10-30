import catalog from '../assets/catalog.json' with {type:'json'};
import {pickDomains,kind,informative,parameters} from './signals.mjs';
import {scores,sensitivity} from './scoring.mjs';
import {QlooError} from './providers.mjs';
export const SIGNAL_NOTE='Tags describe categories. Hobby audiences add the tastes of a group you chose. Removing an audience removes cohort context. Signal families have separate weighting controls; these distances measure model response, not equal shares of personal importance.';
export function initialBuild(interests){const domains=pickDomains(interests);if(domains.length!==2)throw new QlooError('This mix leaves too few categories to guess. Swap a pick.','coverage');
 return {interests,domains,full:{},ablations:{},warnings:[],generated_at:new Date().toISOString(),tasks:[...interests.filter(e=>kind(e)!=='entity').flatMap(interest=>domains.map(domain=>({type:'context',interest,domain,stage:'singleton'}))),...domains.map(domain=>({type:'discover',domain}))],game:null};}
// One Qloo operation per HTTP poll. State is JSON and saved under a D1 lease.
export async function contextStep(task,client){const {interest,domain}=task;
 if(task.stage==='reference'){const reference=catalog.find(e=>e.alias===(domain==='artist'?'blue_bottle':'radiohead')),rows=await client.insights([reference],domain);task.panel=Object.keys(scores(rows));task.stage='rescore';if(task.panel.length<10)throw contextError(task);return false;}
 const rows=await client.insights([interest],domain,task.stage==='rescore'?task.panel:null);
 if(informative(rows))return true;
 if(task.stage==='singleton'&&Object.keys(scores(rows)).length>=10){task.stage='reference';return false;}
 throw contextError(task);
}
function contextError({interest,domain}){return new QlooError('Qloo found '+interest.name+' but returned flat or insufficient '+domain.replaceAll('_',' ')+' recommendations for this '+kind(interest)+'. It cannot be used in this round; no substitute was selected.','unsupported',[interest.id]);}
export async function buildStep(b,client){if(b.game){b.game.full=b.full;b.game.ablations=b.ablations;b.game.warnings=b.warnings;}const task=b.tasks[0];if(!task)return;
 if(task.type==='context'){if(await contextStep(task,client))b.tasks.shift();return;}
 if(task.type==='discover'){const rows=await client.insights(b.interests,task.domain),panel=Object.keys(scores(rows));if(panel.length<10)throw new QlooError('Qloo has too little evidence for this mix. Swap an interest or try a recorded round.','coverage');b.tasks[0]={type:'baseline',domain:task.domain,panel};return;}
 if(task.type==='baseline'){const rows=await client.insights(b.interests,task.domain,task.panel);if(task.panel.some(i=>!(i in scores(rows))))throw new QlooError('Qloo returned an incomplete shortlist. Try another mix.','coverage');if(!informative(rows))throw new QlooError('Qloo returned a flat shortlist. Try another mix.','coverage');
 b.full[task.domain]=rows.sort((a,b)=>b.score-a.score);b.tasks.shift();
 if(Object.keys(b.full).length===2){const predictions=[];for(let rank=0;rank<3;rank++)for(const domain of b.domains)predictions.push({...b.full[domain][rank],domain,rank:rank+1});
 b.game={version:1,source:'live',generated_at:b.generated_at,interests:b.interests,domains:b.domains,predictions,full:b.full,ablations:b.ablations,sensitivity:null,warnings:b.warnings};
 b.tasks=b.interests.flatMap(interest=>b.domains.map(domain=>({type:'ablate',interest,domain})));}return;}
 if(task.type==='ablate'){b.ablations[task.interest.id]??={};try{const rows=await client.insights(b.interests.filter(e=>e.id!==task.interest.id),task.domain,b.full[task.domain].map(x=>x.id)),valid=scores(rows);b.ablations[task.interest.id][task.domain]=rows.filter(x=>x.id in valid).sort((a,b)=>b.score-a.score);}catch(e){if(!(e instanceof QlooError))throw e;b.warnings.push('Not enough evidence to compare '+task.interest.name+' in '+task.domain+'.');}
 b.tasks.shift();if(!b.tasks.length){b.game.sensitivity=sensitivity(b.interests.map(e=>({...e,name:e.label||e.name})),b.full,b.ablations);
 if(b.interests.some(e=>kind(e)!=='entity')){b.game.signal_note=SIGNAL_NOTE;b.game.sensitivity.signal_note=SIGNAL_NOTE;b.game.signal_parameters={signals:parameters(b.interests),weights:'Qloo defaults; no custom family weights'};}}}
}
