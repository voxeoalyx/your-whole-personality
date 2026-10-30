import catalog from '../assets/catalog.json' with {type:'json'};
import demos from '../assets/demos.json' with {type:'json'};
import contract from './contract.json' with {type:'json'};
import {Store} from './store.mjs';
import {Qloo,Model,Evidence,QlooError,items,entity,boundedJSON} from './providers.mjs';
import {HOBBIES,TAG_TYPES,TYPES,kind,pickDomains,normalize} from './signals.mjs';
import {scores} from './scoring.mjs';
import {initialBuild,buildStep,contextStep} from './game.mjs';
import {createInvestigator,advance,answer,snapshot} from './investigator.mjs';
const TTL=1800000;
export const SECURITY_HEADERS={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','Cross-Origin-Resource-Policy':'same-origin','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' https: data: blob:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"};
const response=(data,status=200)=>Response.json(data,{status,headers:{...SECURITY_HEADERS,...(status===429?{'Retry-After':String(data.retry_after||5)}:{})}});
const busy=()=>response({error:'The investigator is busy. Please retry shortly.',retry_after:5},429);
const limited=()=>response({error:'Too many requests. Please wait and try again.',retry_after:60},429);
async function findInterest(store,id){return catalog.find(e=>e.id===id)||await store.get('entity:'+id);}
async function search(q,typ,client,store){const found=[],notices=[],routes=[];
 if(!typ||typ==='audience')routes.push(['/v2/audiences',{'filter.query':q,'filter.parents.types':HOBBIES,take:12},'audience']);
 if(!typ||typ==='tag')routes.push(['/v2/tags',{'filter.query':q,'filter.tag.types':[...TAG_TYPES].sort(),take:12},'tag']);
 if(!typ||TYPES.includes(typ))routes.push(['/search',{query:q,take:8,...(typ?{types:'urn:entity:'+typ}:{})},'entity']);
 // Searches run concurrently, bounded to the three fixed provider routes.
 await Promise.all(routes.map(async([route,params,family])=>{try{const raw=await client.get(route,params),rows=family==='entity'?items(raw):raw.results?.[family==='tag'?'tags':'audiences']||[];
 for(const rawRow of rows.slice(0,12)){const e=family==='entity'?entity(rawRow):normalize(rawRow,family);if(!e?.id||!e.type||family==='entity'&&!/^[A-Fa-f0-9-]{36}$/.test(e.id))continue;e.verified=(await store.get('valid:'+e.id))?.valid??catalog.find(x=>x.id===e.id)?.verified??null;e.support_message=(await store.get('valid:'+e.id))?.message||'';await store.put('entity:'+e.id,'entity',e,7200000);found.push(e);}}
 catch(e){if(!(e instanceof QlooError))throw e;notices.push(family[0].toUpperCase()+family.slice(1)+' search unavailable: '+e.message);}}));
 const unique=[...new Map(found.map(e=>[e.id,e])).values()];unique.sort((a,b)=>Number(a.name.toLowerCase()!==q.toLowerCase())-Number(b.name.toLowerCase()!==q.toLowerCase())+0||({audience:0,tag:1}[a.type]??2)-({audience:0,tag:1}[b.type]??2));
 if(['pilates','weightlifting','weight lifting'].includes(q.toLowerCase())&&['','tag','audience'].includes(typ))notices.unshift('No usable exact '+q+' hobby signal was found in our hackathon tests. The related place tags returned flat recommendations; a title containing the word is a different interest. Fitness and Health & Fitness are broader content tags you can search for, not equivalents. Nothing is substituted.');return {results:unique,notices};}
function publicJob(state,model){if(state.error)return {status:'error',error:state.error,code:state.code,unsupported:state.unsupported||[]};
 const game=state.build?.game||state.game;
 if(state.investigate&&!state.engine)return {status:'working',progress:game?35:12,message:'Preparing the investigator from Qloo evidence.'};
 if(state.engine){const result=snapshot(state.engine,game,model,state.receipts||[]);return {...result,progress:game.sensitivity?100:50,message:'Checking which interest moves the rankings.'};}
 return {status:game?.sensitivity?'ready':'working',...(game?{game}:{}),progress:state.build?.game?40:12,message:'Finding a few things you did not tell us.'};}
async function step(state,env,store,transport){const qloo=new Qloo(env,store,transport),evidence=new Evidence(qloo,state),model=new Model(env,store,transport);
 const engine=state.engine,game=state.build?.game;
 if(game&&state.investigate&&!engine){state.engine=createInvestigator(game);await advance(state.engine,game,model,evidence);return;}
 if(engine&&!engine.finished&&(engine.pendingQuery||engine.predictions.length===Object.keys(engine.answers).length)){await advance(engine,game,model,evidence);return;}
 if(state.build?.tasks.length)await buildStep(state.build,evidence);
 else if(engine&&!engine.finished)await advance(engine,game,model,evidence);
}
export async function handleAPI(request,env,{transport=fetch}={}){
 const url=new URL(request.url),path=url.pathname,origin=request.headers.get('Origin');
 if(origin&&origin!==url.origin||request.headers.get('Sec-Fetch-Site')==='cross-site')return response({error:'Same-origin requests only.'},403);
 if(!env.DB)return response({error:'The service is not configured yet.'},503);
 const store=new Store(env.DB);let leaseKey=null,owner=null;
 try{
 let visitor;
 try{await store.cleanup();visitor=await store.visitor(request);}
 catch(error){console.error('quota_initialization_failed '+error.stack);return response({error:'The service could not initialize request limits. Please try again.'},503);}
 if(request.method==='GET'&&path==='/api/config')return response({live:Boolean(env.QLOO_API_KEY),investigator:Boolean(env.NVIDIA_API_KEY),catalog,presets:contract.presets,demos:Object.keys(demos),privacy:'Search terms go to Qloo while typing. Live picks/evidence go to Qloo and NVIDIA; reactions go to this server and NVIDIA. Temporary rounds expire after 30 minutes. No game account database or analytics. This private preview requires ChatGPT sign-in; hosting logs and provider retention are separate.'});
 const route=path==='/api/search'?'search':path==='/api/validate'?'validate':path==='/api/game'?'game_request':path==='/api/answer'?'answer':/^\/api\/game\/[a-f0-9]{32}$/.test(path)?'poll':null;
 if(!route)return response({error:'Not found.'},404);
 if(!await store.rate(visitor,route,route==='search'?3:0))return limited();
 if(request.method==='GET'&&route==='poll'){
 const id=path.split('/').at(-1),key='job:'+id;let state=await store.get(key);if(!state)return response({error:'This round expired. Start another.'},404);
 if(state.game?.source==='recorded'||state.error||state.build?.game?.sensitivity&&(!state.investigate||state.engine?.finished))return response(publicJob(state,env.NVIDIA_MODEL||'nvidia/nemotron-3.5-lightning-30b-a3b'));
 owner=await store.lease(key);if(!owner)return response(publicJob(state,env.NVIDIA_MODEL||'nvidia/nemotron-3.5-lightning-30b-a3b'));leaseKey=key;
 state=await store.get(key);if(!state)return response({error:'This round expired. Start another.'},404);
 try{await step(state,env,store,transport);}catch(e){state.error=e instanceof QlooError?e.message:'The investigation was interrupted. Start a fresh round.';state.code=e.code||'internal';state.unsupported=e.ids||[];}
 await store.saveJob(id,state,owner);return response(publicJob(state,env.NVIDIA_MODEL||'nvidia/nemotron-3.5-lightning-30b-a3b'));
 }
 if(request.method==='GET'&&route==='search'){
 const q=(url.searchParams.get('q')||'').trim(),typ=url.searchParams.get('type')||'';if([...q].length<2||[...q].length>100||typ&&!TYPES.concat(['tag','audience']).includes(typ))return response({error:'Use 2–100 characters and a supported category.'},400);
 leaseKey='search:'+crypto.randomUUID();owner=await store.lease(leaseKey);if(!owner)return busy();return response(await search(q,typ,new Qloo(env,store,transport),store));}
 if(request.method!=='POST'||!['validate','game_request','answer'].includes(route))return response({error:'Not found.'},404);
 let data;try{data=await boundedJSON(request,8192);if(!data||Array.isArray(data)||typeof data!=='object')throw new Error();}catch{return response({error:'Invalid request.'},400);}
 if(route==='validate'){
 if(typeof data.id!=='string')return response({error:'Search for that exact interest again.'},400);const e=await findInterest(store,data.id);if(!e)return response({error:'Search for that exact interest again.'},400);
 const saved=await store.get('valid:'+e.id);if(saved||typeof e.verified==='boolean')return response(saved?{...saved,entity:e}:{valid:e.verified,entity:e,message:e.verified?'Ready.':'Qloo cannot use this exact record as an interest. Choose another result; we will not swap it for you.'});
 leaseKey='validate:'+e.id;owner=await store.lease(leaseKey);if(!owner)return busy();let validation=await store.get('validation:'+e.id);
 if(!validation){if(!await store.consume('cost:'+visitor,8,120,900000))return limited();validation={tasks:pickDomains([e]).map(domain=>({interest:e,domain,stage:'singleton'}))};}
 let result;const qloo=new Qloo(env,store,transport);
 try{if(kind(e)==='entity')result={valid:Object.keys(scores(await qloo.insights([e],e.type==='brand'?'tv_show':'brand',null,2))).length>0};else{if(await contextStep(validation.tasks[0],qloo))validation.tasks.shift();if(validation.tasks.length){await store.put('validation:'+e.id,'validation',validation,7200000);return response({pending:true,entity:e});}result={valid:true};}}
 catch(e){if(!(e instanceof QlooError)||e.code!=='unsupported')throw e;result={valid:false,message:e.message};}
 result.message??=result.valid?'Ready.':'Qloo cannot use this exact record as an interest. Choose another result; we will not swap it for you.';await store.put('valid:'+e.id,'validation',result,7200000);return response({...result,entity:e});
 }
 if(route==='game_request'){
 if(!['live','demo'].includes(data.mode))return response({error:'Choose live or recorded mode.'},400);
 const id=crypto.randomUUID().replaceAll('-','');let state,kindName;
 if(data.mode==='demo'){if(typeof data.demo_id!=='string'||!Object.hasOwn(demos,data.demo_id))return response({error:'That recorded round is unavailable.'},400);state={game:{...structuredClone(demos[data.demo_id]),source:'recorded'}};kindName='demo';}
 else {const ids=data.ids;if(!Array.isArray(ids)||ids.length<3||ids.length>5||ids.some(i=>typeof i!=='string')||new Set(ids).size!==ids.length)return response({error:'Pick 3–5 different interests.'},400);
 const interests=await Promise.all(ids.map(i=>findInterest(store,i)));for(let i=0;i<ids.length;i++)if(!interests[i]||!((await store.get('valid:'+ids[i]))?.valid??interests[i].verified))return response({error:'Every pick needs to be checked first.'},400);
 if(!env.QLOO_API_KEY)throw new QlooError('No live key is configured. Choose a recorded round.','not_configured');if(!await store.rate(visitor,'game',42))return limited();if(!await store.newRound(visitor)){const reset=(Math.floor(Date.now()/86400000)+1)*86400000;return response({error:'Your daily allowance of 10 new live rounds is used up. It resets at '+new Date(reset).toISOString().slice(0,10)+' 00:00 UTC. Existing rounds and recorded examples remain available.',code:'daily_round_limit',retry_after:Math.max(1,Math.ceil((reset-Date.now())/1000))},429);}state={build:initialBuild(interests),investigate:data.investigate===true,receipts:[]};kindName='live';}
 if(kindName==='demo'){await store.demo('job:'+id,state,TTL);return response({id},202);}
 if(!await store.insert('job:'+id,kindName,state,TTL,24))return response({error:'Round capacity is full. Please return later.','retry_after':60},429);return response({id},202);
 }
 if(route==='answer'){
 if(typeof data.id!=='string'||! /^[a-f0-9]{32}$/.test(data.id))return response({error:'Invalid round.'},400);
 leaseKey='job:'+data.id;owner=await store.lease(leaseKey);if(!owner)return busy();const state=await store.get(leaseKey);if(!state?.engine)return response({error:'This investigation expired. Start another.'},404);
 const changed=answer(state.engine,data.prediction_id,data.response,data.sequence);await store.saveJob(data.id,state,owner);return response({accepted:true,duplicate:!changed},202);
 }
 return response({error:'Not found.'},404);
 }catch(e){if(e instanceof TypeError)return response({error:'Invalid request.'},400);if(e instanceof QlooError)return response({error:e.message,code:e.code,unsupported:e.ids},503);return response({error:'The service could not finish this request. Please try again.'},500);}
 finally{if(owner&&leaseKey)await store.release(leaseKey,owner);}
}
