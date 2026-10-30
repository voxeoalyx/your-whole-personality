const str = {type:'string'}, bool = {type:'boolean'}, num = {type:'number'};
const nullable = s => ({anyOf:[s,{type:'null'}]});
const choice = values => ({enum:values});
const array = items => ({type:'array',items});
const object = properties => ({type:'object',properties,required:Object.keys(properties),additionalProperties:false});
const ids = array(str), nullableNumber = nullable(num);
export const researchSchema = {
  $schema:'https://json-schema.org/draft/2020-12/schema',
  title:'Your Whole Personality voluntary research export v1',
  ...object({
    schema_version:{const:1},experiment_version:{const:'identity-reality-check-v1'},consent_version:{const:'local-export-v1'},
    record_id:{type:'string',pattern:'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'},
    consent:object({granted:{const:true},timestamp:{type:'string',pattern:'^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}Z$'},scope:{const:'reviewed_local_export'}}),
    source:choice(['live','recorded']),evidence_generated_at:nullable(str),
    model:object({provider:nullable(str),name:nullable(str),fallback:bool,closing_fallback:bool,qloo_version:{const:'v2/insights'},scoring_version:{const:'fixed-panel-loo-v1'},influence_version:{const:'act-iii-v1'}}),
    interests:array(object({id:str,type:str,taxonomy:nullable(str),supported:{const:true}})),
    predictions:array(object({id:str,domain:str,sequence:{type:'integer',minimum:0},response:choice(['liked','disliked','unfamiliar',null]),in_original_inputs:bool})),
    influence:object({classification:choice(['dominant','largest','distributed','insufficient','pending']),detail:nullable(str),strict_status:str,strict_winner_id:nullable(str),measurements:array(object({id:str,value:nullableNumber,domains:{type:'object',additionalProperties:nullableNumber},halves:{...array(nullableNumber),minItems:2,maxItems:2}}))}),
    identity:object({status:choice(['selected','none','declined','skipped']),ids,unsupported:nullable(object({text:{type:'string',minLength:1,maxLength:80},supported:{const:false}}))}),
    comparison:object({classification:choice(['agreement','disagreement','shared','insufficient',null]),model_ids:ids,overlap_ids:ids}),
    denominators:object({yes:num,no:num,unknown:num,known:num,total:num,answered:num,rate:nullableNumber})
  })
};
// Small validator for precisely the schema keywords above; no evaluation of data as code.
// Optional in v1 so previously downloaded records remain valid.
researchSchema.properties.model.required=researchSchema.properties.model.required.filter(k=>k!=='closing_fallback');

export function validateResearch(record) {
  function valid(s,v) {
    if (s.anyOf) return s.anyOf.some(x=>valid(x,v));
    if ('const' in s && v!==s.const) return false;
    if (s.enum && !s.enum.includes(v)) return false;
    if (s.type==='null') return v===null;
    if (s.type==='array') return Array.isArray(v) && v.length >= (s.minItems||0) && v.length <= (s.maxItems||Infinity) && v.every(x=>valid(s.items,x));
    if (s.type==='object') return v!==null && typeof v==='object' && !Array.isArray(v) && (s.required||[]).every(k=>Object.hasOwn(v,k)) && Object.keys(v).every(k=>s.properties?.[k] ? valid(s.properties[k],v[k]) : s.additionalProperties===false ? false : valid(s.additionalProperties||{},v[k]));
    if (s.type==='string') return typeof v==='string' && v.length >= (s.minLength||0) && v.length <= (s.maxLength||Infinity) && (!s.pattern || new RegExp(s.pattern).test(v));
    if (s.type==='boolean') return typeof v==='boolean';
    if (['number','integer'].includes(s.type)) return typeof v==='number' && Number.isFinite(v) && (s.type!=='integer'||Number.isInteger(v)) && v >= (s.minimum??-Infinity);
    return true;
  }
  if (!valid(researchSchema,record)) return false;
  const {identity:i,comparison:c,denominators:d,predictions:p}=record;
  const ids=new Set(record.interests.map(e=>e.id));
  if (i.ids.some(id=>!ids.has(id)) || new Set(i.ids).size!==i.ids.length) return false;
  if (i.status==='selected' ? !i.ids.length&&!i.unsupported : i.ids.length||i.unsupported!==null) return false;
  if (['skipped','declined'].includes(i.status) ? c.classification!==null : c.classification===null) return false;
  if ([...c.model_ids,...c.overlap_ids].some(id=>!ids.has(id)) || c.overlap_ids.some(id=>!i.ids.includes(id)||!c.model_ids.includes(id))) return false;
  const yes=p.filter(x=>x.response==='liked').length,no=p.filter(x=>x.response==='disliked').length,unknown=p.filter(x=>x.response==='unfamiliar').length;
  return d.yes===yes && d.no===no && d.unknown===unknown && d.known===yes+no && d.answered===yes+no+unknown && d.total===p.length && d.rate===(yes+no?yes/(yes+no):null);
}
