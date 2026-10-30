import {scores} from './scoring.mjs';
export const FIELDS={entity:'signal.interests.entities',tag:'signal.interests.tags',audience:'signal.demographics.audiences'};
export const DOMAINS=['tv_show','movie','brand','videogame','artist','podcast','book'];
export const TYPES=['artist','tv_show','movie','podcast','book','brand','videogame','person'];
export const HOBBIES='urn:audience:hobbies_and_interests';
export const TAG_TYPES=['urn:tag:genre:media','urn:tag:genre:music','urn:tag:genre:brand','urn:tag:genre:place','urn:tag:category:place','urn:tag:keyword:qloo','urn:tag:subgenre:qloo'];
const NAMES={tv_show:'TV',movie:'Movies',podcast:'Podcasts',podcaster:'Podcasts',book:'Books',author:'Books',artist:'Music',album:'Music',brand:'Brands',place:'Places',videogame:'Games'};
export const kind=e=>['tag','audience'].includes(e?.type)?e.type:'entity';
export function parameters(interests){const grouped={};for(const e of interests){const field=FIELDS[kind(e)];(grouped[field]??=[]).push(typeof e==='string'?e:e.id);}return Object.fromEntries(Object.entries(grouped).map(([k,v])=>[k,[...new Set(v)].sort()]));}
export function pickDomains(interests){const used=new Set(interests.flatMap(e=>kind(e)==='entity'?[e.type]:kind(e)==='tag'?e.parent_types||[]:[]));return DOMAINS.filter(d=>!used.has(d)).slice(0,2);}
export const informative=(rows,minimum=10)=>{const vs=Object.values(scores(rows));return vs.length>=minimum&&new Set(vs).size>1;};
export function normalize(raw,family){const {id:ident='',type:taxonomy='',name=''}=raw;
  if(typeof ident!=='string'||!/^urn:[a-zA-Z0-9_:.-]+$/.test(ident)||typeof name!=='string')return null;
  const parents=[...new Set((raw.parents||[]).filter(x=>x.type?.startsWith('urn:entity:')).map(x=>x.type.slice(11)))].sort();let label,detail;
  if(family==='audience'){if(taxonomy!==HOBBIES||!ident.startsWith(HOBBIES+':'))return null;
    label='hobby audience';detail='Uses the tastes of this hobby group. You choose the group; we do not infer membership.';
  }else if(family==='tag'){if(!TAG_TYPES.includes(taxonomy)||!ident.startsWith(taxonomy+':'))return null;
    let source=[...new Set(parents.map(p=>NAMES[p]||p.replaceAll('_',' ')))].join(' / ')||'Cultural';
    if(taxonomy==='urn:tag:genre:place'&&ident.split(':').length>5)source={restaurant:'Restaurants',hotel:'Hotels'}[ident.split(':')[4]]||source;
    label=source+' '+taxonomy.split(':')[2]+' tag';detail='Interest in this '+source.toLowerCase()+' category, not proof that you do the activity.';
  }else return null;
  return {id:ident,name:name.slice(0,160),type:family,taxonomy,parent_types:parents,type_label:label,label:name.slice(0,160)+' ('+label+')',detail,image:null};
}
export function contextTasks(interest,domain){return {interest,domain,stage:'singleton',panel:null};}
