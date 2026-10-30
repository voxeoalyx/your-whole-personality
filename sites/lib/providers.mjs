import {FIELDS,parameters,TYPES} from './signals.mjs';
import {scores} from './scoring.mjs';
export class QlooError extends Error {constructor(message,code='service_unavailable',ids=[]){super(message);this.code=code;this.ids=ids;}}
export class ModelError extends Error {constructor(code){super('Investigator unavailable');this.code=code;}}
export async function boundedJSON(response,max,signal){
  if(!response.body)throw new Error('Empty response');const reader=response.body.getReader();let total=0;const chunks=[];
  try {for(;;){signal?.throwIfAborted();const {done,value}=await reader.read();if(done)break;total+=value.byteLength;if(total>max)throw new Error('Response too large');chunks.push(value);}}
  finally{await reader.cancel().catch(()=>{});}
  const bytes=new Uint8Array(total);let pos=0;for(const v of chunks){bytes.set(v,pos);pos+=v.length;}
  return JSON.parse(new TextDecoder().decode(bytes));
}
export const items=raw=>Array.isArray(raw.results)?raw.results:raw.results?.entities||[];
export function entity(raw){const prop=raw.properties||{};let image=prop.image?.url||null;try{if(new URL(image).protocol!=='https:')image=null;}catch{image=null;}
 return {id:raw.entity_id,name:String(raw.name||'').slice(0,240),type:(raw.types||[]).map(t=>t.split(':').at(-1)).find(t=>TYPES.includes(t))||null,detail:String(raw.disambiguation||prop.release_year||prop.description||'').slice(0,180),image,score:raw.query?.affinity??null};}
const digest=async text=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))].map(n=>n.toString(16).padStart(2,'0')).join('');
export class Qloo {
 constructor(env,store,transport=fetch){this.env=env;this.store=store;this.transport=(...args)=>transport(...args);const base=env.QLOO_BASE_URL||'https://hackathon.api.qloo.com';const u=new URL(base);
 if(u.protocol!=='https:'||!['hackathon.api.qloo.com','api.qloo.com'].includes(u.hostname)||!['','/'].includes(u.pathname)||u.search||u.hash||u.username||u.password||u.port)throw new QlooError('Invalid provider configuration.');this.base=u.origin;}
 async get(route,params){if(!['/search','/v2/insights','/v2/tags','/v2/audiences'].includes(route))throw new QlooError('Invalid endpoint');
 const wire=Object.fromEntries(Object.keys(params).sort().map(k=>[k,Array.isArray(params[k])?params[k].join(','):String(params[k])])),hash=await digest(JSON.stringify([route,wire])),key='qloo:'+hash;
 const cached=await this.store.get(key);if(cached)return cached;
 if(!this.env.QLOO_API_KEY)throw new QlooError('Live Qloo is not configured. Choose a recorded round.','not_configured');
 if(await this.store.get('qloo-cooldown'))throw new QlooError('Qloo needs a short breather.','rate_limit');
 const limit=Number(this.env.QLOO_CALL_LIMIT??500);if(!Number.isInteger(limit)||limit<0||!await this.store.consume('provider:qloo:'+new Date().toISOString().slice(0,10),1,limit,86400000))throw new QlooError('The API budget is used up. Try a recorded round.','budget');
 const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),15000);try{
 const r=await this.transport(this.base+route+'?'+new URLSearchParams(wire),{headers:{'X-Api-Key':this.env.QLOO_API_KEY,Accept:'application/json'},redirect:'manual',signal:ctrl.signal});
 if(r.status===429){await r.body?.cancel();await this.store.put('qloo-cooldown','control',true,60000);throw new QlooError('Qloo needs a short breather.','rate_limit');}
 if(r.status===404&&route==='/search'){await r.body?.cancel();return {results:[]};}
 if(!r.ok){await r.body?.cancel();throw new QlooError('Qloo could not finish that request.');}
 const raw=await boundedJSON(r,route==='/v2/insights'?8*1024*1024:1024*1024,ctrl.signal);if(!raw||Array.isArray(raw)||typeof raw!=='object'||raw.errors)throw new QlooError('Qloo could not score this request.');
 if(new TextEncoder().encode(JSON.stringify(raw)).byteLength<1000000)await this.store.put(key,'cache',raw,7200000);return raw;
 }catch(e){if(e instanceof QlooError)throw e;throw new QlooError('The connection to Qloo dropped. Your picks are still here.');}finally{clearTimeout(timer);}}
 async insights(interests,domain,panel=null,take=20){const params={'filter.type':'urn:entity:'+domain,...parameters(interests),'bias.trends':'off','feature.explainability':true,take:panel?.length||take};if(panel)params['filter.results.entities']=[...panel].sort();
 const raw=await this.get('/v2/insights',params),bad=[...new Set((raw.warnings||[]).flatMap(w=>Object.values(FIELDS).flatMap(k=>Array.isArray(w[k])?w[k]:w[k]?[w[k]]:[])))];
 if(bad.length)throw new QlooError('Qloo cannot use an interest in this round. Remove the highlighted pick.','unsupported',bad);return items(raw).slice(0,panel?.length||take).map(entity);}
}
export class Evidence {
 constructor(client,state){this.client=client;this.state=state;state.receipts??=[];}
 async insights(interests,domain,panel=null,take=20){const receipts=this.state.receipts;if(receipts.length>=32)throw new QlooError('This round reached its Qloo request budget.','budget');
 const receipt={id:'q'+(receipts.length+1),endpoint:'/v2/insights',parameters:{'filter.type':'urn:entity:'+domain,...parameters(interests),take:panel?.length||take,'bias.trends':'off','feature.explainability':true}};if(panel)receipt.parameters['filter.results.entities']=[...panel].sort();receipts.push(receipt);
 try{const rows=await this.client.insights(interests,domain,panel,take);receipt.result={count:rows.length,scored:Object.keys(scores(rows)).length,entities:rows.map(r=>({id:r.id,name:r.name,score:r.score}))};return rows;}catch(e){receipt.error=e.code||'service_unavailable';throw e;}}
}
export class Model {
 constructor(env,store,transport=fetch){this.env=env;this.store=store;this.transport=(...args)=>transport(...args);this.model=env.NVIDIA_MODEL||'nvidia/nemotron-3.5-lightning-30b-a3b';}
 async decide(instructions,state,schema){if(!this.env.NVIDIA_API_KEY)throw new ModelError('not_configured');
 const limit=Math.max(0,Math.min(1000,Number(this.env.NVIDIA_CALL_LIMIT||150)));if(!Number.isInteger(limit)||!await this.store.consume('provider:nvidia:'+new Date().toISOString().slice(0,10),1,limit,86400000))throw new ModelError('process_budget');
 const payload={model:this.model,messages:[{role:'system',content:instructions},{role:'user',content:JSON.stringify(state)}],tools:[{type:'function',function:{name:'investigate',description:'Choose the next bounded investigative action.',parameters:schema}}],tool_choice:{type:'function',function:{name:'investigate'}},temperature:.2,max_tokens:850,stream:false,chat_template_kwargs:this.model.startsWith('moonshotai/')?{thinking:false}:{enable_thinking:false}};
 const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),15000),start=Date.now();try{const r=await this.transport('https://integrate.api.nvidia.com/v1/chat/completions',{method:'POST',body:JSON.stringify(payload),headers:{Authorization:'Bearer '+this.env.NVIDIA_API_KEY,'Content-Type':'application/json'},redirect:'manual',signal:ctrl.signal});
 if(!r.ok){await r.body?.cancel();throw new ModelError(({401:'authentication',402:'quota',403:'access',429:'rate_limit'})[r.status]||'http_'+r.status);}
 const data=await boundedJSON(r,262144,ctrl.signal),choice=data.choices?.[0],calls=choice?.message?.tool_calls;
 if(!['tool_calls','stop'].includes(choice?.finish_reason)||!Array.isArray(calls)||calls.length!==1||calls[0].function?.name!=='investigate')throw new ModelError('invalid_tool_response');
 const action=JSON.parse(calls[0].function.arguments);if(!action||typeof action!=='object'||Array.isArray(action))throw new ModelError('invalid_action');
 return [action,{provider:'NVIDIA',model:this.model,seconds:(Date.now()-start)/1000,usage:Object.fromEntries(['prompt_tokens','completion_tokens','total_tokens'].filter(k=>Number.isFinite(data.usage?.[k])).map(k=>[k,data.usage[k]]))}];
 }catch(e){if(e instanceof ModelError)throw e;throw new ModelError(ctrl.signal.aborted?'timeout_or_network':'malformed_response');}finally{clearTimeout(timer);}}
}
