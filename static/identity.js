import { influenceReveal, predictability } from './logic.js';

export const EXPERIMENT = 'identity-reality-check-v1';
export function identityAnswer(game, status = 'skipped', ids = [], unsupported = '') {
  if (!['selected','none','declined','skipped'].includes(status)) throw Error('Choose an identity response.');
  if (!Array.isArray(ids) || ids.some(id => !game.interests.some(e => e.id === id))) throw Error('Unknown interest.');
  const text = String(unsupported).normalize('NFC').replace(/[\u0000-\u001f\u007f-\u009f\u202a-\u202e\u2066-\u2069]/g, '').trim();
  if (text.length > 80) throw Error('Keep your interest to 80 characters.');
  if (status === 'selected' && !ids.length && !text) throw Error('Choose an interest, or tell us what is missing.');
  return { status, ids:status === 'selected' ? [...new Set(ids)] : [], unsupported:status === 'selected' ? text : '' };
}

export function identityComparison(game, answer) {
  const r = influenceReveal(game);
  const selected = game.interests.filter(e => answer.ids.includes(e.id)).map(e => e.label || e.name);
  if (answer.unsupported) selected.push(`${answer.unsupported} (self-report only; not Qloo-scored)`);
  const self = answer.status === 'none' ? 'None of these' : selected.join(' / ');
  const base = { kind:null, model:'No defensible overall leader', self, model_ids:[], overlap_ids:[] };
  if (['skipped','declined'].includes(answer.status)) return {...base, text:answer.status === 'declined' ? 'Your identity has declined to comment. The original verdict stands.' : '', title:'NO ANSWER REQUIRED'};
  if (['pending','insufficient'].includes(r.kind) || r.detail === 'partial') return {...base,kind:'insufficient',title:'THE ALGORITHM HAS NO JURISDICTION.',text:`You say: ${self}. Our removal comparisons cannot support an overall comparison. The algorithm will have to live with not knowing.`};
  const shared = r.kind === 'distributed';
  const modelIds = shared ? [...new Set([...r.domains.flatMap(d => d.leaders.map(e => e.id)), ...r.halfLeaders.flatMap(rows => rows.map(e => e.id))])] : [r.strict.winner?.id || r.leader.id];
  const model = shared ? (r.detail === 'unchanged' ? 'No ranking movement on these panels' : game.interests.filter(e => modelIds.includes(e.id)).map(e => e.label || e.name).join(' / ') + ' (shared or category-dependent)') : `${game.interests.find(e => e.id === modelIds[0])?.name} (${r.kind === 'dominant' ? 'strict panel dominance' : 'largest measured; no clear dominance'})`;
  const overlap = answer.ids.filter(id => modelIds.includes(id));
  let kind = shared || selected.length > 1 ? 'shared' : overlap.length ? 'agreement' : 'disagreement';
  const titles = { shared:'COALITION GOVERNMENT.', agreement:'A RARE MOMENT OF AGREEMENT.', disagreement:'A JURISDICTIONAL DISPUTE.' };
  const joke = kind === 'shared' ? 'The algorithm requested a main character. It got a committee.' : kind === 'agreement' ? 'The algorithm guessed a piece of your identity. It is already ordering a name badge.' : 'The algorithm has confused its seating chart with your autobiography.';
  return {kind,model,self,model_ids:modelIds,overlap_ids:overlap,title:titles[kind],text:`Our rankings: ${model}. You say: ${self}. ${joke}`};
}

export function withIdentityShare(verdict, game, answer, consent = false) {
  const result = {...verdict};
  delete result.identity;
  if (consent === true && !['skipped','declined'].includes(answer.status)) result.identity = identityComparison(game, answer);
  return result;
}

// Strict allowlist: never export a whole game, request, model response or trace.
export function researchRecord(game, answers, answer, consent = false, meta = {}) {
  if (consent !== true) return null;
  const r = influenceReveal(game), comparison = identityComparison(game,answer);
  const number = value => typeof value === 'number' && Number.isFinite(value) ? value : null;
  const record = {
    schema_version:1, experiment_version:EXPERIMENT, consent_version:'local-export-v1',
    record_id:meta.id || crypto.randomUUID(), consent:{granted:true, timestamp:meta.timestamp || new Date().toISOString(), scope:'reviewed_local_export'},
    source:game.source === 'recorded' ? 'recorded' : 'live', evidence_generated_at:game.generated_at || null,
    model:{provider:game.investigator?.provider || null, name:game.investigator?.model || null, fallback:Boolean(game.investigator?.fallback_reason || game.investigator?.closing_fallback || game.investigator?.trace?.some(e=>e.event==='closing_fallback')), closing_fallback:Boolean(game.investigator?.closing_fallback || game.investigator?.trace?.some(e=>e.event==='closing_fallback')), qloo_version:'v2/insights', scoring_version:'fixed-panel-loo-v1', influence_version:'act-iii-v1'},
    interests:game.interests.map(e => ({id:e.id,type:e.type || 'unknown',taxonomy:e.taxonomy || null,supported:true})),
    predictions:game.predictions.map((p,sequence) => ({id:p.id,domain:p.domain,sequence,response:({yes:'liked',no:'disliked',unknown:'unfamiliar'})[answers[p.id]] || null, in_original_inputs:game.interests.some(e => e.id === p.id)})),
    influence:{classification:r.kind, detail:r.detail || null, strict_status:game.sensitivity?.status || 'missing', strict_winner_id:game.sensitivity?.winner?.id || null,
      measurements:(game.sensitivity?.rows || []).map(row => ({id:row.id,value:number(row.value),domains:Object.fromEntries(game.domains.map(d => [d,number(row.domains?.[d])])),halves:[0,1].map(h => number(row.halves?.[h]))}))},
    identity:{...answer, unsupported:answer.unsupported ? {text:answer.unsupported,supported:false} : null},
    comparison:{classification:comparison.kind,model_ids:comparison.model_ids,overlap_ids:comparison.overlap_ids},
    denominators:predictability(game.predictions,answers)
  };
  return record;
}
