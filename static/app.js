import { summary, influenceReveal, influenceCopy, recommendationChanges, finalResult, shareCardLayout } from './logic.js';

import { identityAnswer, identityComparison, withIdentityShare, researchRecord } from './identity.js';
import { validateResearch } from './research-schema.js';
let identityState={status:'skipped',ids:[],unsupported:''}, identityShare=false, researchConsent=false, researchPreview=null, researchId=null;

const $ = s => document.querySelector(s);
const main = $('#main');
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const labels = { audience:'Hobby audiences', tag:'Tags', artist:'Music', tv_show:'TV', movie:'Movies', podcast:'Podcasts', book:'Books', brand:'Brands', videogame:'Games', person:'People' };
const typeLabel = e => e.type_label || labels[e.type];
const interestLabel = e => e.label || e.name;
const single = { artist:'ARTIST', tv_show:'TV SHOW', movie:'MOVIE', podcast:'PODCAST', book:'BOOK', brand:'BRAND', videogame:'GAME', person:'PERSON' };
let config, picks=[], phase='select', mode='live', game=null, answers={}, index=0, jobId=null, revision=0, activeRemoved=null;
let searchTimer, searchAbort, searchRevision=0, toastTimer, pollTimer;
const pending = new Set();

function toast(message) { $('#toast').textContent=message; $('#toast').classList.add('visible'); clearTimeout(toastTimer); toastTimer=setTimeout(()=>$('#toast').classList.remove('visible'),3200); }
function closingFallback() { return Boolean(game?.investigator?.closing_fallback || game?.investigator?.trace?.some(e=>e.event==='closing_fallback')); }
function roundLabel() { return mode==='demo'?'RECORDED DEMO · EXAMPLE PROFILE':game?.investigator?.fallback_reason?'FIXED QLOO · MODEL FALLBACK':closingFallback()?'QLOO + NVIDIA · FIXED CLOSING':game?.investigator?'QLOO + NVIDIA · INVESTIGATOR':'QLOO · LIVE'; }
function progress(step) { document.querySelectorAll('[data-step]').forEach(el=>el.setAttribute('aria-current',+el.dataset.step===step?'step':'false')); const m=$('#mode-label'); m.textContent=roundLabel(); m.className='mode '+(mode==='demo'?'recorded':'live'); }
function scene(html, step) { main.innerHTML=html; if((game?.investigator||game?.sensitivity)&&['guess','hijack','verdict'].includes(phase))main.insertAdjacentHTML('beforeend',tracePanel()); progress(step); window.scrollTo({top:0,behavior:'instant'}); main.focus({preventScroll:true}); wireImages(); }
function tracePanel() {
  const a=game.investigator, reveal=influenceReveal(game);
  const receipt={...a,strict_dominance:game.sensitivity,act_iii:{kind:reveal.kind,detail:reveal.detail,strict_check_failures:reveal.reasons}};
  return `<details class="investigator-trace"><summary>Inspect the investigator</summary><p>Public action summaries and returned evidence. Affinities are not probabilities. ${a?`${a.model_calls}/${a.model_call_limit} model calls; ${a.questions_remaining} questions left.`:game.source==='recorded'?'Recorded Qloo evidence; no live model calls.':'Fixed Qloo evidence; no AI investigator.'} The original strict dominance metric is preserved below.</p><pre>${escape(JSON.stringify(receipt,null,2))}</pre></details>`;
}
function wireImages() { main.querySelectorAll('img').forEach(img=>img.addEventListener('error',()=>img.remove(),{once:true})); }
function image(e) { return e.image ? `<img src="${escape(e.image)}" alt="" loading="lazy" referrerpolicy="no-referrer">` : `<span class="entity-initial" aria-hidden="true">${escape(e.name.slice(0,1))}</span>`; }
function recordedNote() { return mode==='demo'?`<div class="record-note">RECORDED DEMO · Real Qloo results from ${escape(game?.generated_at?.slice(0,10)||'a saved round')}, for this example profile. Your reactions are yours; these are not guesses from your own picks.</div>`:game?.investigator?.fallback_reason?'<div class="record-note" role="status">The AI investigator is unavailable. This round continues with fixed Qloo recommendations. Earlier AI decisions, if any, remain in the receipts.</div>':closingFallback()?'<div class="record-note" role="status">Earlier predictions were selected by the AI investigator. The final model response was unavailable; the closing line is fixed copy. The evidence and scores are unchanged.</div>':''; }
async function api(url, body, signal) {
  const timeout=new AbortController(), timer=setTimeout(()=>timeout.abort(),20000);
  const abort=()=>timeout.abort();signal?.addEventListener('abort',abort,{once:true});
  if(signal?.aborted)timeout.abort();
  try {
    const r=await fetch(url,{method:body?'POST':'GET',headers:body?{'Content-Type':'application/json'}:{},body:body?JSON.stringify(body):undefined,signal:timeout.signal});
    let data;try {data=await r.json();}catch {throw new Error('The service could not finish this request. Please try again.');}
    if(!r.ok){const err=new Error(data.error||'Something interrupted this request.');Object.assign(err,data);throw err;}
    return data;
  } catch(err) {
    if(err.name==='AbortError'&&!signal?.aborted)throw new Error('The request took too long. Please try again.');
    throw err;
  } finally {clearTimeout(timer);signal?.removeEventListener('abort',abort);}
}

function selectScreen(message='') {
  phase='select'; mode='live'; game=null; revision++; searchRevision++; searchAbort?.abort(); clearTimeout(searchTimer);clearTimeout(pollTimer);
  const suggestions=['radiohead','severance','taylor','blue_bottle','rogan','elden_ring','patagonia','friends'].map(alias=>config.catalog.find(e=>e.alias===alias)).filter(e=>!picks.some(p=>p.id===e.id));
  scene(`<section class="intro-grid scene"><div class="intro-copy"><p class="eyebrow"><span class="square"></span> A 3-MINUTE CRISIS OF CULTURAL IDENTITY</p><h1>YOU’RE <br>A LOT. <br><span class="stroke">PROVE IT.</span></h1><p class="tagline">You contain multitudes.<br>The algorithm disagrees.</p><p class="lede">Give us a few things you love. We’ll make some assumptions. You’ll get to hurt our feelings.</p><div class="stamp"><span aria-hidden="true">✳</span> NO ACCOUNT. NO SELF-IMPROVEMENT.</div></div><div class="selection-area"><div class="selection-top"><h2>First, your supporting evidence.</h2><div class="counter">${picks.length}<small> / 5 picks</small></div></div><div class="picks" aria-label="Selected interests">${picks.map(e=>`<div class="pick ${e.invalid?'bad':''}"><span>${escape(e.name)}${e.type==='tag'||e.type==='audience'?`<small class="pick-type">${escape(typeLabel(e))}</small>`:''}</span><button data-remove="${e.id}" aria-label="Remove ${escape(e.name)}">×</button></div>`).join('')||'<span class="empty-pick">A band?</span><span class="empty-pick">A show?</span><span class="empty-pick">Your very specific coffee?</span>'}</div><div class="search-wrap"><label class="visually-hidden" for="entity-search">Find an interest</label><div class="search-line"><span class="search-icon" aria-hidden="true">⌕</span><input id="entity-search" autocomplete="off" placeholder="A thing you’re a little too into…" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="search-results"><label class="visually-hidden" for="category">Search category</label><select id="category"><option value="">Everything</option>${Object.entries(labels).map(([k,v])=>`<option value="${k}">${v}</option>`).join('')}</select></div><div class="search-results" id="search-results" role="listbox" aria-label="Search results"></div></div><p class="search-hint">Pick 3–5. Music, shows, brands, hobbies. Your hill to die on.</p><p class="signal-hint">Tags describe categories. Hobby audiences use a group’s tastes, chosen by you.</p><div id="selection-error" class="inline-error" role="alert">${escape(message)}</div><div class="quick-label">OR BORROW SOME PERSONALITY</div><div class="suggestions">${suggestions.map(e=>`<button class="suggestion" data-add="${e.id}">${escape(e.name)} <span>＋</span></button>`).join('')}</div><button id="begin" class="button full selection-go" ${picks.length<3||picks.some(e=>e.invalid)||!config.live?'disabled':''}>${picks.length<3?`Give us ${3-picks.length} more ${picks.length===2?'interest':'interests'}`:'Let the algorithm judge'} <span aria-hidden="true">↗</span></button><p class="privacy-note">${config.live?'Picks and reactions go to Qloo / NVIDIA as explained in the fine print.':'Live Qloo is not configured. Play a recorded round below.'}<br>This is a taste test. Your actual personality remains your problem.</p></div></section><section class="seeded"><div><p class="eyebrow">A RUNNING START</p><p>Decision fatigue?<br>Try somebody else’s taste.</p></div><div><div class="presets">${config.presets.map((p,i)=>`<button class="preset" data-preset="${p.id}"><span><small class="preset-number">0${i+1} / STARTER MIX</small><strong>${escape(p.name)}</strong><small>${escape(p.line)}</small></span><span class="arrow" aria-hidden="true">↗</span></button>`).join('')}</div><div class="demo-cta"><span>Bad internet. Good taste?</span><button class="text-button" id="demo-select">Play a recorded round ↗</button></div></div></section>`,1);
  main.querySelectorAll('[data-remove]').forEach(b=>b.onclick=()=>{picks=picks.filter(e=>e.id!==b.dataset.remove);selectScreen();$('#entity-search').focus();});
  main.querySelectorAll('[data-add]').forEach(b=>b.onclick=()=>add(config.catalog.find(e=>e.id===b.dataset.add)));
  main.querySelectorAll('[data-preset]').forEach(b=>b.onclick=()=>{const p=config.presets.find(p=>p.id===b.dataset.preset);picks=p.aliases.map(a=>config.catalog.find(e=>e.alias===a));selectScreen();toast('Three excellent grounds for jumping to conclusions.');$('#begin').focus();});
  $('#begin').onclick=()=>start('live'); $('#demo-select').onclick=demoScreen;
  $('#entity-search').oninput=()=>queueSearch(); $('#category').onchange=()=>queueSearch();
  $('#entity-search').onkeydown=e=>{if(e.key==='ArrowDown'){e.preventDefault();$('#search-results button')?.focus();}if(e.key==='Escape')closeSearch();};
}

function closeSearch() { if($('#search-results'))$('#search-results').innerHTML='';$('#entity-search')?.setAttribute('aria-expanded','false');searchAbort?.abort();searchRevision++; }
function queueSearch() {
  clearTimeout(searchTimer);searchAbort?.abort();const request=++searchRevision;const q=$('#entity-search').value.trim(),type=$('#category').value;
  if(q.length<2){closeSearch();return;}
  $('#search-results').innerHTML='<div class="search-message" role="status">Looking for your exact brand of taste…</div>';$('#entity-search').setAttribute('aria-expanded','true');
  searchTimer=setTimeout(async()=>{searchAbort=new AbortController();try{const data=await api(`/api/search?q=${encodeURIComponent(q)}&type=${encodeURIComponent(type)}`,null,searchAbort.signal);if(request!==searchRevision||phase!=='select')return;
    const found=data.results.filter(e=>!picks.some(p=>p.id===e.id));const notices=(data.notices||[]).map(n=>`<div class="search-message" role="status">${escape(n)}</div>`).join('');$('#search-results').innerHTML=notices+(found.length?found.map((e,i)=>`<button class="result" role="option" aria-selected="false" data-result="${i}">${image(e)}<span class="result-copy"><strong>${escape(e.name)}</strong><small>${escape(typeLabel(e))}${e.verified===false?' · INPUT UNAVAILABLE':''}</small>${e.detail?`<small class="result-detail">${escape(e.detail)}</small>`:''}</span><span class="plus" aria-hidden="true">＋</span></button>`).join(''):'<div class="search-message">No matching interest in this category. Try another term or category.</div>');
    const options=main.querySelectorAll('[data-result]');options.forEach((b,i)=>{b.onclick=()=>add(found[i]);b.onkeydown=e=>{if(e.key==='ArrowDown'){e.preventDefault();options[i+1]?.focus();}if(e.key==='ArrowUp'){e.preventDefault();(options[i-1]||$('#entity-search')).focus();}if(e.key==='Escape'){closeSearch();$('#entity-search').focus();}};});wireImages();
  }catch(err){if(err.name==='AbortError'||request!==searchRevision||phase!=='select')return;$('#search-results').innerHTML=`<div class="search-message" role="alert">${escape(err.message)}<br>Starter mixes and recorded rounds are still below.</div>`;}},320);
}

async function add(e) {
  if(picks.length>=5){toast('Five interests. Leave a little mystery.');return;}if(picks.some(p=>p.id===e.id)||pending.has(e.id))return;
  const rev=revision;pending.add(e.id);toast('Checking that Qloo can actually use '+e.name+'…');
  try {const check=await api('/api/validate',{id:e.id});if(rev!==revision||phase!=='select')return;if(!check.valid){$('#selection-error').textContent=check.message;closeSearch();return;}if(picks.length<5&&!picks.some(p=>p.id===e.id)){picks.push({...check.entity,verified:true});selectScreen();$('#entity-search').focus();toast(`${e.name}. Noted. Judged a little.`);}}
  catch(err){if(phase==='select')$('#selection-error').textContent=err.message;}
  finally{pending.delete(e.id);}
}

function demoScreen() { phase='demo';mode='demo';revision++;scene(`<section class="error-stage scene"><p class="eyebrow">BAD INTERNET IS NOT A PERSONALITY TRAIT</p><h1>TAKE A<br>TEST DRIVE.</h1><p class="lede">Real Qloo responses. A borrowed profile. Pick a recorded round and give the algorithm your honest review.</p><p class="small muted">These guesses belong to the example mix, not to you. No live API calls.</p><div class="demo-options">${config.presets.filter(p=>config.demos.includes(p.id)).map(p=>`<button class="button light" data-demo="${p.id}">${escape(p.name)} <span>↗</span></button>`).join('')||'<p>No recorded rounds are installed yet.</p>'}</div><button id="back-select" class="text-button">Back to my own interests</button></section>`,1);main.querySelectorAll('[data-demo]').forEach(b=>b.onclick=()=>start('demo',b.dataset.demo));$('#back-select').onclick=()=>selectScreen(); }

async function start(source,demoId) {
  identityState={status:'skipped',ids:[],unsupported:''};identityShare=false;researchConsent=false;researchPreview=null;
  researchId=null;mode=source;phase='loading';game=null;answers={};index=0;activeRemoved=null;clearTimeout(pollTimer);const rev=++revision;
  scene(`<section class="loading-page scene"><p class="eyebrow">ASSEMBLING SOME ENTIRELY UNNECESSARY OPINIONS</p><span class="orbit" aria-hidden="true">✳</span><h1>DON’T WORRY.<br>WE’LL ASSUME<br>THE REST.</h1><div class="load-track" role="progressbar" aria-label="Preparing your round" aria-valuemin="0" aria-valuemax="100" aria-valuenow="5"><div style="width:5%"></div></div><p id="loading-status" role="status">Calling the cultural witness stand.</p><p class="small muted">A live round can take 15–45 seconds to start. You can start<br>guessing while we check which interest moves the rankings.</p><button class="text-button" id="cancel-round">Back to my picks</button><p class="small muted">Leaving this screen does not cancel requests already running.</p></section>`,2);
  $('#cancel-round').onclick=()=>selectScreen();
  try {const job=await api('/api/game',source==='demo'?{mode:'demo',demo_id:demoId}:{mode:'live',investigate:true,ids:picks.map(e=>e.id)});if(rev!==revision)return;jobId=job.id;poll(rev);}
  catch(err){if(rev===revision)errorScreen(err);}
}

async function poll(rev) {
  if(rev!==revision)return;
  try {const job=await api('/api/game/'+jobId);if(rev!==revision)return;if(job.status==='error'){errorScreen(Object.assign(new Error(job.error),{code:job.code,unsupported:job.unsupported}));return;}
    if(job.game){const hadSensitivity=Boolean(game?.sensitivity);game=job.game;if(mode==='demo')picks=game.interests;
      if(game.investigator){answers=job.answers||{};index=Object.keys(answers).length;
        if(game.investigator.finished&&['loading','thinking','guess'].includes(phase))hijackScreen();
        else if(job.status==='waiting'&&['loading','thinking'].includes(phase))guessScreen();
        else if(phase==='hijack'&&!hadSensitivity&&game.sensitivity)hijackScreen();
      }else if(phase==='loading'){phase='guess';guessScreen();}else if(phase==='hijack'&&job.status==='ready')hijackScreen();}
    if($('#loading-status'))$('#loading-status').textContent=job.message||'Preparing the evidence.';
    if($('.load-track')){$('.load-track').setAttribute('aria-valuenow',job.progress);$('.load-track div').style.width=job.progress+'%';}
    if(game?.investigator?(job.status==='working'||!game.sensitivity):job.status!=='ready')pollTimer=setTimeout(()=>poll(rev),900);
  } catch(err) {if(rev===revision)errorScreen(err,()=>poll(rev));}
}

async function investigateAnswer(p,response) {
  const rev=revision, sequence=index, fixed=Boolean(game?.investigator?.fallback_reason);phase='thinking';clearTimeout(pollTimer);
  scene(`${recordedNote()}<section class="loading-page scene"><p class="eyebrow">YOUR ANSWER HAS ENTERED THE RECORD</p><span class="orbit" aria-hidden="true">✳</span><h1>${fixed?'NEXT ON<br>THE FIXED LIST.':'RECONSIDERING<br>MY ASSUMPTIONS.'}</h1><p role="status">${fixed?'Reaction recorded. Continuing the fixed Qloo shortlist.':response==='no'?'That theory took a hit. Testing another direction.':response==='unknown'?'Unfamiliar is not a rejection. Finding another test.':'Noted. Let’s see whether that pattern holds.'}</p><p class="small muted">${fixed?'AI selection is unavailable. Your answers still count toward the result.':'The next guess uses your answers. Usually a few seconds.'}</p></section>`,2);
  try {await api('/api/answer',{id:jobId,prediction_id:p.id,response,sequence});if(rev===revision)poll(rev);}
  catch(err){if(rev===revision)errorScreen(err,()=>investigateAnswer(p,response));}
}

function errorScreen(err,retry=null) {phase='error';if(err.unsupported)picks=picks.map(e=>({...e,invalid:err.unsupported.includes(e.id)}));scene(`<section class="error-stage scene"><p class="eyebrow">THE ALGORITHM HAS ENCOUNTERED HUMILITY</p><h1>A SMALL<br>IDENTITY CRISIS.</h1><p class="lede" role="alert">${escape(err.message)}</p><div class="center-actions">${retry?'<button class="button" id="resume-round">Retry this round ↗</button>':''}<button class="button" id="error-retry">Back to my picks <span>↗</span></button><button class="button light" id="error-demo">Try a recorded round <span>↗</span></button></div></section>`,2);$('#error-retry').onclick=()=>selectScreen(err.code==='unsupported'?'Remove the highlighted interest. No substitutions were made.':'');$('#error-demo').onclick=demoScreen;if(retry)$('#resume-round').onclick=()=>{phase='loading';$('#resume-round').disabled=true;retry();};}

function guessScreen() {
  phase='guess';const p=game.predictions[index];const prompts={tv_show:'We think this belongs in your queue.',movie:'We have a theory about your watchlist.',brand:'We suspect this brand is your kind of thing.',videogame:'We think this is your kind of problem.',artist:'We think your headphones would approve.',podcast:'We suspect this could derail your commute.',book:'We have a theory about your nightstand.'};
  scene(`${recordedNote()}<section class="guess-layout scene"><div class="guess-copy"><p class="eyebrow">ACT II / THE ALGORITHM HAS OPINIONS</p><h1>FEELING <br>SEEN? <br><span class="stroke">OR SUED?</span></h1><p class="lede">${game.investigator?escape(game.investigator.observation):'Six guesses. Be honest.<br>You cannot hurt its feelings.<br>We checked.'}</p><div class="guess-counter">GUESS ${index+1} OF ${game.investigator?.question_limit||game.predictions.length}<div class="dots" aria-hidden="true">${Array.from({length:game.investigator?.question_limit||game.predictions.length},(_,i)=>`<span class="dot ${i<index?'done':i===index?'active':''}"></span>`).join('')}</div></div><div class="crumb-interests">THE EVIDENCE YOU GAVE US<br>${game.interests.map(e=>escape(interestLabel(e))).join(' · ')}</div></div><div><article class="prediction"><div class="prediction-top"><span>${escape(single[p.domain])} / AN EDUCATED GUESS</span><span>0${index+1}</span></div><div class="prediction-image">${p.image?`<img src="${escape(p.image)}" alt="${escape(p.name)} artwork" referrerpolicy="no-referrer">`:`<span class="fallback-title" aria-hidden="true">?</span>`}</div><div class="prediction-body"><p class="eyebrow">${escape(prompts[p.domain])}</p><h2>${escape(p.name)}</h2><p>${escape(p.detail?.length<100?p.detail:'Recommended by Qloo from this mix.')}</p></div></article><div class="responses" aria-label="Your reaction to ${escape(p.name)}"><button class="response" data-answer="yes">✳ &nbsp; Nailed it</button><button class="response no" data-answer="no">× &nbsp; Absolutely not</button><button class="response unknown" data-answer="unknown">Haven’t tried it &nbsp; ↗</button></div><p class="reply-note muted">New to you? That’s discovery, not a wrong answer.</p>${index>0&&!game.investigator?'<button id="previous-guess" class="text-button">← Change my last answer</button>':''}</div></section>`,2);
  if(game.investigator)main.querySelector('.guess-copy .lede').classList.add('agent-observation');
  main.querySelectorAll('[data-answer]').forEach(b=>b.onclick=()=>{if(game.investigator){investigateAnswer(p,b.dataset.answer);return;}answers[p.id]=b.dataset.answer;index++;if(index<game.predictions.length)guessScreen();else hijackScreen();});
  if($('#previous-guess'))$('#previous-guess').onclick=()=>{index--;guessScreen();};
}

function hijackScreen() {
  phase='hijack';const s=game.sensitivity;
  if(!s){scene(`${recordedNote()}<section class="loading-page"><p class="eyebrow">YOUR ANSWERS ARE IN</p><h1>WHO’S PULLING<br>THE STRINGS?</h1><span class="orbit" aria-hidden="true">✳</span><p role="status">Finishing the leave-one-out checks. Your reactions are recorded for this round.</p><p class="small muted">We would rather say “not enough evidence” than invent a winner.</p></section>`,3);return;}
  const reveal=influenceReveal(game), copy=influenceCopy(reveal,labels);
  activeRemoved=activeRemoved||reveal.focus;
  const domainReceipts=reveal.domains.map(d=>`<div class="domain-finding"><span class="micro">${escape(labels[d.domain]||d.domain)}</span><p>${d.measured.length<2?'Not enough comparable removals.':d.leaders.length?`${d.leaders.map(r=>`<strong>${escape(r.name)}</strong>`).join(' / ')} · largest measured change${d.missing.length?' among available comparisons':''}.`:'No ranking movement among the measured removals.'}</p>${d.missing.length?`<p class="small muted">Unavailable: ${d.missing.map(r=>escape(r.name)).join(', ')}.</p>`:''}</div>`).join('');
  scene(`${recordedNote()}<section class="scene" data-influence-outcome="${reveal.kind}"><div class="hijack-header"><p class="eyebrow">ACT III / THE PERSONALITY HIJACK</p><h1>${escape(copy.title)}</h1><p class="lede">${escape(copy.text)}</p><p class="small muted">Changes to Qloo’s fixed shortlists, not shares of your personality or proof of what you’ll like.</p>${game.signal_note?`<p class="signal-hint">${escape(game.signal_note)}</p>`:''}</div>
    <div class="domain-findings">${domainReceipts}</div>
    <div class="hijack-grid"><div><p class="eyebrow">TAKE ONE AWAY. WATCH WHAT MOVES.</p><div class="influence-list">${s.rows.map(row=>`<div class="influence ${row.id===activeRemoved?'current':''}"><div class="influence-row"><strong>${escape(row.name)}</strong><button data-without="${escape(row.id)}" aria-label="Compare without ${escape(row.name)}" aria-pressed="${row.id===activeRemoved}">Try without ↗</button></div><div class="bar" aria-hidden="true"><span style="width:${row.value==null?0:Math.max(0,Math.min(100,row.value*100))}%"></span></div><div class="micro">${row.value==null?'OVERALL DISTANCE UNAVAILABLE':`${row.value.toFixed(3)} AVERAGE RANK DISTANCE`}</div><div class="small muted">${game.domains.map(d=>`${escape(labels[d]||d)}: ${row.domains[d]==null?'unavailable':row.domains[d].toFixed(3)}`).join(' · ')}</div></div>`).join('')}</div>
    <details class="method"><summary>What did you actually measure?</summary><p>Each selected interest was removed from the same mix. The candidate titles stayed fixed within each category. Distance is (1 − tie-aware rank correlation) / 2, averaged equally across the two categories. Zero means the same order; one means reversed. Distances are not percentages of influence and do not add up to a whole.</p><p>The strict dominance rule is unchanged: a complete average above 0.10, more than twice the runner-up, and the same winner in both disjoint half-panel checks. These are consistency checks, not statistical confidence intervals.</p><p>Act III also names the largest measured change without declaring dominance. Different category leaders, tied averages, or changing half-panel leaders get a shared reveal. Partial evidence is scoped to available comparisons; missing values are never zero-filled. Shortlists were selected for the starting mix, so results are conditional on these panels.</p><p>Original strict result: <strong>${s.status!=='complete'?'incomplete':s.winner?escape(s.winner.name):'no dominant interest'}</strong>. Full distances and half-panel values are in the investigator trace.</p></details></div>
    <div><div id="comparison" class="comparison" aria-live="polite"></div><div class="hijack-actions"><button class="button" id="verdict-button">Deliver my verdict <span>↗</span></button><button class="text-button" id="remix">Make a swap ↗</button></div><p class="small muted spaced">The preview uses the same shortlist. Making a new mix starts a new round and resets your answers.</p></div></div></section>`,3);
  renderComparison();main.querySelectorAll('[data-without]').forEach(b=>b.onclick=()=>{activeRemoved=b.dataset.without;renderComparison();main.querySelectorAll('.influence').forEach(el=>{const button=el.querySelector('button'),active=button.dataset.without===activeRemoved;el.classList.toggle('current',active);button.setAttribute('aria-pressed',active);});});
  $('#verdict-button').onclick=verdictScreen;$('#remix').onclick=()=>{selectScreen();toast('Swap a pick, then play a fresh round.');};
}

function renderComparison() {
  const interest=game.interests.find(e=>e.id===activeRemoved), reduced=game.ablations[activeRemoved]||{};
  const rankMove=x=>`<strong>${escape(x.name)}</strong> (${escape(x.before.rank)} → ${escape(x.after.rank)})`;
  const titles=rows=>`<ul>${rows.map(p=>`<li><span class="rank-label">${escape(p.rank)}</span> ${escape(p.name)}</li>`).join('')}</ul>`;
  $('#comparison').innerHTML=`<p class="eyebrow">A SMALL ACT OF CULTURAL SABOTAGE</p><h3>Without ${escape(interestLabel(interest))}.</h3><p class="small">Same candidates. One input removed. Ranks are within each fixed shortlist; ties share a rank range.</p>${game.domains.map(d=>{
    const change=recommendationChanges(game.full[d],reduced[d]);
    if(!change.available)return `<div class="compare-domain"><p class="micro">${escape(labels[d]||d)}</p><p>Missing, too-short or flat scores. No supported ranking comparison for this removal.</p></div>`;
    let evidence;
    if(change.entrants.length||change.exits.length) evidence=[change.entrants.length?`Into the top three: ${change.entrants.map(rankMove).join(', ')}.`:'',change.exits.length?`Out of the top three: ${change.exits.map(rankMove).join(', ')}.`:''].filter(Boolean).join(' ');
    else if(change.moves.length)evidence=`${change.moves.slice(0,2).map(rankMove).join('; ')}. The top-three membership stays the same.`;
    else evidence=change.changed?'Only tied rank groups changed; no unambiguous move to spotlight.':'The entire shortlist keeps the same rank order. No recommendation swap to claim.';
    return `<div class="compare-domain"><p class="micro">${escape(labels[d]||d)}</p><p class="change-evidence">${evidence}</p><details class="comparison-lists"><summary>See both top threes</summary><div class="comparison-head"><span>THE ORIGINAL MIX</span><span>ONE INTEREST LESS</span></div><div class="compare-titles">${titles(change.before)}${titles(change.after)}</div></details></div>`;
  }).join('')}`;
}

function verdictScreen() {
  phase='verdict';const v=finalResult(game,answers,labels);const accuracy=v.stats.known?Math.round(v.stats.rate*100)+'%':'—';
  scene(`${recordedNote()}<section class="verdict-layout scene"><article class="share-card" aria-label="Your share card"><div class="card-head"><span class="micro">YOUR WHOLE PERSONALITY<br>${escape(roundLabel())}</span><span class="mark" aria-hidden="true">✳</span></div><h1>${escape(v.title)}</h1><p class="roast">${escape(v.roast)}</p><div class="card-stats card-stats-summary"><div class="card-stat"><span class="micro">PREDICTABILITY</span><b>${accuracy}</b><small>${v.stats.yes}/${v.stats.known} familiar guesses confirmed<br>${v.stats.unknown} not tried · ${v.stats.total} shown</small></div></div><section class="card-influence" aria-label="Your ranking influences"><p class="micro">${escape(v.influence.label)}</p>${v.influence.entries.map(e=>`<p class="influence-credit"><span>${escape(e.label)}</span><strong>${escape(e.names)}</strong></p>`).join('')}<p class="influence-qualification">${escape(v.influence.qualification)}</p><p class="card-footnote">Ranking changes on these fixed shortlists, not shares of personality.</p></section><p class="card-invite">YOUR FRIENDS ARE NEXT. <span>↗</span></p><p class="card-footnote">A tiny taste test, not a personality diagnosis. Powered by Qloo.</p></article><div class="verdict-copy"><p class="eyebrow">ACT IV / YOU MAY APPEAL THIS DECISION</p><h2>Well.<br><em>That got specific.</em></h2><p class="explanation">${escape(v.why)}</p><p class="eyebrow">THE INFLUENCE FINDING</p><p class="explanation final-influence">${escape(v.influence.explanation)}</p>${game.investigator?`<p class="investigator-closing">${closingFallback()?'<strong>Fixed closing:</strong> ':''}${escape(game.investigator.observation)}</p>`:''}<button class="button" id="save-card">Save the evidence <span>↓</span></button><button class="button light" id="copy-card">Copy the verdict <span>↗</span></button><p class="privacy-note">Save a PNG or copy the words. No public result link.<br>${mode==='demo'?'The card is labeled as an example-profile round.':'Only share the interests and answers you’re comfortable sharing.'}</p><div id="copy-fallback"></div><div class="round-nav"><button class="text-button" id="play-again">Another personality? ↗</button><button class="text-button" id="back-hijack">Review the hijack</button></div><details class="receipt"><summary>The receipts: your ${game.predictions.length} reactions</summary>${game.predictions.map(p=>`<div class="receipt-item"><span>${escape(p.name)}</span><span>${answers[p.id]==='yes'?'✓ Nailed it':answers[p.id]==='no'?'× Absolutely not':'↗ Not tried'}</span></div>`).join('')}<p class="privacy-note">${v.stats.unknown} unfamiliar guesses were excluded from accuracy. ${game.investigator?'Live reactions were sent to the investigator and NVIDIA.':'Recorded-round reactions stay in this tab.'}</p><button class="text-button export-session" id="export-session">Download my session data ↓</button></details></div></section>`,4);
  main.insertAdjacentHTML('beforeend','<div id="identity-panel"></div>');identityPanel();updateIdentityCard();
  $('#save-card').onclick=()=>exportCard(withIdentityShare(v,game,identityState,identityShare));$('#copy-card').onclick=()=>copyVerdict(withIdentityShare(v,game,identityState,identityShare));$('#play-again').onclick=()=>selectScreen();$('#back-hijack').onclick=hijackScreen;
  $('#export-session').onclick=()=>{const sessionJSON=JSON.stringify({version:2,investigator:game.investigator,source:game.source,generated_at:game.generated_at,interests:game.interests.map(({id,name,type,taxonomy,type_label,parent_types})=>({id,name,type,taxonomy,type_label,parent_types})),signal_parameters:game.signal_parameters,signal_note:game.signal_note,predictions:game.predictions.map(p=>({id:p.id,name:p.name,domain:p.domain,rank:p.rank,reaction:answers[p.id]})),predictability:v.stats,sensitivity:game.sensitivity,influence_reveal:influenceReveal(game),influence_summary:v.influence},null,2);download(new Blob([sessionJSON],{type:'application/json'}),'my-whole-personality-session.json');
    if(!$('#session-json'))$('#export-session').insertAdjacentHTML('afterend','<label for="session-json" class="privacy-note">Download requested. If blocked, copy this JSON:</label><textarea id="session-json" class="share-fallback" readonly></textarea>');
    $('#session-json').value=sessionJSON;toast('Session ready. A copyable backup is below.');};
}


function identityPanel() {
  const result=identityComparison(game,identityState);
  $('#identity-panel').innerHTML=`<section class="identity-check" aria-labelledby="identity-heading"><p class="eyebrow">OPTIONAL / THE IDENTITY REALITY CHECK</p><h2 id="identity-heading">ONE LAST QUESTION.</h2><p>We checked which interests move our predictions. But which actually feel like part of who you are?</p>${mode==='demo'?'<p class="signal-hint">This is a borrowed example profile. Your answer is yours, but its influence findings are not a test of your own mix.</p>':''}<form id="identity-form"><fieldset><legend>Choose as many as fit. Your original verdict is already yours.</legend>${game.interests.map((e,i)=>`<label class="identity-option"><input type="checkbox" name="identity-interest" value="${escape(e.id)}" ${identityState.ids.includes(e.id)?'checked':''}><span>${escape(interestLabel(e))}<small>${escape(typeLabel(e)||e.type)}</small></span></label>`).join('')}<label class="identity-option"><input type="checkbox" id="identity-other" ${identityState.unsupported?'checked':''}><span>My actual whole personality isn’t on your list.</span></label><label class="identity-free" ${identityState.unsupported?'':'hidden'}>What is missing? <input id="identity-text" maxlength="80" autocomplete="off" value="${escape(identityState.unsupported)}" placeholder="An interest, not personal details"><small>Up to 80 characters. Avoid names of private people, contact details, health details or other sensitive information. This stays in your tab unless you export or share it. We will not score it or substitute something else in Qloo.</small></label></fieldset><div class="identity-actions"><button class="button" type="submit">Overrule the algorithm ↗</button><button type="button" class="button light" id="identity-none">None of these</button><button type="button" class="text-button" id="identity-decline">Prefer not to answer</button><button type="button" class="text-button" id="identity-clear">Clear my answer</button></div><p id="identity-error" role="alert"></p></form><div id="identity-result" role="status">${identityState.status!=='skipped'?`<h3>${escape(result.title)}</h3><p>${escape(result.text)}</p>`:''}</div><p class="small muted">Qloo ranking changes measure cultural influence on this model. Your answer is self-reported identity attachment. Whether attachment transfers through partnerships is an untested hypothesis.</p>${!['skipped','declined'].includes(identityState.status)?`<label class="identity-option"><input type="checkbox" id="identity-share" ${identityShare?'checked':''}><span>Include this identity answer in my copied verdict and PNG.</span></label>`:''}</section><details class="research-export"><summary>Help investigate the gap? Optional research export</summary><p>No research record is sent to us. You can create a file, inspect it, and decide whether to share it separately. The file contains a random record ID, typed interest IDs, prediction IDs/categories and reactions, influence measurements, identity answer (including any free text), comparison, model versions and consent time. No account, contact details, API keys or private model reasoning.</p><p>If you choose to share it with a researcher, it could inform research and future commercial products. This app has no research inbox or persistent research database. The preview lasts in this tab until cleared, a new round, or reload. A downloaded copy remains on your device until you delete it. There is no server research copy to delete; a separately shared copy is governed by its recipient’s retention and deletion agreement. Interest combinations can be identifying: this is pseudonymous, not guaranteed anonymous.</p><label class="identity-option"><input type="checkbox" id="research-consent" ${researchConsent?'checked':''}><span>I choose to prepare this record for review and possible research sharing, including possible future commercial research. Nothing is uploaded.</span></label><button class="button light" id="research-review" ${researchConsent?'':'disabled'}>Review research JSON</button><button class="text-button" id="research-clear">Decline / clear research preview</button><div id="research-preview"></div></details>`;
  const finish=(status,ids=[],text='')=>{try{identityState=identityAnswer(game,status,ids,text);identityShare=false;researchConsent=false;researchPreview=null;identityPanel();updateIdentityCard();$('#identity-result').scrollIntoView({block:'nearest'});}catch(err){$('#identity-error').textContent=err.message;}};
  $('#identity-other').onchange=e=>{$('.identity-free').hidden=!e.target.checked;if(!e.target.checked)$('#identity-text').value='';};
  $('#identity-form').onsubmit=e=>{e.preventDefault();finish('selected',[...main.querySelectorAll('[name="identity-interest"]:checked')].map(e=>e.value),$('#identity-other').checked?$('#identity-text').value:'');};
  $('#identity-none').onclick=()=>finish('none');$('#identity-decline').onclick=()=>finish('declined');$('#identity-clear').onclick=()=>finish('skipped');
  if($('#identity-share'))$('#identity-share').onchange=e=>{identityShare=e.target.checked;updateIdentityCard();};
  $('#research-consent').onchange=e=>{researchConsent=e.target.checked;researchPreview=null;$('#research-preview').innerHTML='';$('#research-review').disabled=!researchConsent;};
  $('#research-clear').onclick=()=>{researchConsent=false;researchPreview=null;identityPanel();};
  $('#research-review').onclick=()=>{
    researchId=researchId||crypto.randomUUID();
    researchPreview=researchRecord(game,answers,identityState,researchConsent,{id:researchId});
    if(!validateResearch(researchPreview)){researchPreview=null;toast('Research export could not be validated. Your game is unaffected.');return;}
    $('#research-preview').innerHTML='<label for="research-json">Review the exact file before downloading. No automatic sharing.</label><textarea id="research-json" class="share-fallback" readonly></textarea><button class="button" id="research-download">Download reviewed research JSON ↓</button>';
    $('#research-json').value=JSON.stringify(researchPreview,null,2);
    $('#research-download').onclick=()=>{if(researchConsent&&researchPreview&&validateResearch(researchPreview))download(new Blob([JSON.stringify(researchPreview,null,2)],{type:'application/json'}),'whole-personality-research-v1.json');};
  };
}
function updateIdentityCard() {
  $('#copy-fallback').innerHTML='';
  $('#export-dialog')?.remove();
  let section=$('#card-identity');
  if(!section){section=document.createElement('section');section.id='card-identity';section.className='card-influence';$('.card-invite').before(section);}
  const r=identityComparison(game,identityState);
  section.hidden=!identityShare;
  section.innerHTML=identityShare?`<p class="micro">${escape(r.title)}</p><p>OUR RANKINGS: ${escape(r.model)}</p><p>I SAY: ${escape(r.self)}</p><small>Self-report, not a psychological measurement.</small>`:'';
}

async function copyVerdict(v) {
  const text=summary(v,game.source)+(game.investigator?'\n'+roundLabel():'');
  $('#copy-fallback').innerHTML='<label for="manual-copy" class="small">Your verdict. Copy manually if the clipboard is unavailable:</label><textarea id="manual-copy" class="share-fallback" readonly></textarea>';
  $('#manual-copy').value=text;$('#manual-copy').select();
  try {await Promise.race([navigator.clipboard.writeText(text),new Promise((_,reject)=>setTimeout(()=>reject(new Error('Clipboard timeout')),2500))]);toast('Copied. Go bother someone you love.');}
  catch {toast('Select and copy the text below the buttons.');}
}

function download(blob,name) {const url=URL.createObjectURL(blob);const link=document.createElement('a');link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),3000);}
async function exportCard(v) {
  const button=$('#save-card');button.disabled=true;
  try {await document.fonts.ready;const canvas=document.createElement('canvas'), c=canvas.getContext('2d');
    const layout=shareCardLayout(v,roundLabel(),(text,font)=>{c.font=font;return c.measureText(text).width;});
    canvas.width=layout.width;canvas.height=layout.height;
    c.fillStyle='#dbfa45';c.fillRect(0,0,canvas.width,canvas.height);c.fillStyle='#191b18';c.strokeStyle='#191b18';c.lineWidth=2;c.strokeRect(30,30,canvas.width-60,canvas.height-60);c.textBaseline='top';
    for(const block of layout.blocks){c.font=block.font;block.lines.forEach((line,i)=>c.fillText(line,block.x,block.y+i*block.lineHeight));}
    for(const y of layout.rules)c.fillRect(70,y,940,2);
    const dataUrl=canvas.toDataURL('image/png');
    let dialog=document.querySelector('#export-dialog');if(!dialog){dialog=document.createElement('dialog');dialog.id='export-dialog';dialog.className='export-preview';document.body.append(dialog);}
    dialog.innerHTML='<button class="close-dialog" aria-label="Close image preview">×</button><p class="eyebrow">EXHIBIT A / READY FOR THE GROUP CHAT</p><a class="button full" id="download-png" download="your-whole-personality.png">Download PNG <span>↓</span></a><p class="privacy-note">If this browser blocks downloads, press and hold or right-click the image to save it.</p><img id="exported-card" alt="Your generated share card, with verdict and both measurements">';
    dialog.querySelector('img').src=dataUrl;dialog.querySelector('img').alt=summary(v,game.source);dialog.querySelector('a').href=dataUrl;dialog.querySelector('button').onclick=()=>dialog.close();dialog.showModal();
  }catch {toast('Image export failed. You can still copy the verdict.');}finally{button.disabled=false;}
}

$('#about-button').onclick=$('#privacy-button').onclick=()=>$('#about').showModal();document.querySelectorAll('.close-dialog').forEach(b=>b.onclick=()=>$('#about').close());
document.addEventListener('click',e=>{if(!e.target.closest('.search-wrap')&&phase==='select')closeSearch();});
try {config=await api('/api/config');selectScreen();} catch(err){main.innerHTML=`<section class="error-stage"><h1>THE SERVER<br>IS TAKING FIVE.</h1><p>${escape(err.message)}</p><a class="button" href="/">Try again ↗</a></section>`;}
