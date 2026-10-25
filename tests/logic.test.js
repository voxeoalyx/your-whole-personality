import test from 'node:test';
import assert from 'node:assert/strict';
import { predictability, verdict, summary, influenceReveal, influenceCopy, recommendationChanges, finalResult, influenceSummary, shareCardLayout, wrapLines } from '../static/logic.js';
import { profiles, analyze } from '../tools/analyze_influence.mjs';
const predictions = Array.from({length:6},(_,i)=>({id:String(i)}));
const full={status:'complete',winner:null};
test('unfamiliar guesses are excluded, never counted as errors',()=>{
  assert.deepEqual(predictability(predictions,{'0':'yes','1':'no','2':'unknown'}),{yes:1,no:1,unknown:1,known:2,total:6,answered:3,rate:.5});
});
test('zero denominator yields no accuracy, not zero accuracy',()=>assert.equal(predictability(predictions,{}).rate,null));
test('fewer than three familiar responses is insufficient, even with a model winner',()=>{
  const v=verdict(predictions,{'0':'yes','1':'yes'}, {status:'complete',winner:{name:'Radiohead'}});
  assert.equal(v.id,'evidence');assert.equal(v.stats.rate,1);
});
test('high confirmation, low confirmation and mixed reactions have distinct supported verdicts',()=>{
  assert.equal(verdict(predictions,{'0':'yes','1':'yes','2':'yes','3':'no'},full).id,'legible');
  assert.equal(verdict(predictions,{'0':'no','1':'no','2':'no','3':'yes'},full).id,'inconvenience');
  assert.equal(verdict(predictions,{'0':'yes','1':'no','2':'yes','3':'no'},full).id,'multitudes');
});
test('only complete sensitivity can name an influential interest',()=>{
  const answers={'0':'yes','1':'yes','2':'no'};
  assert.equal(verdict(predictions,answers,{status:'incomplete',winner:{name:'Fake'}}).winner,null);
  assert.equal(verdict(predictions,answers,{status:'complete',winner:{name:'Radiohead'}}).id,'hijack');
});
test('recorded share text explicitly identifies an example profile',()=>{
  assert.match(summary(verdict(predictions,{},full),'recorded'),/not predictions from my own interests/);
  assert.doesNotMatch(summary(verdict(predictions,{},full),'recorded'),/https?:/);
});
test('all verdict branches require the appropriate evidence',()=>{
  for(let yes=0;yes<=6;yes++)for(let no=0;no<=6-yes;no++){
    const a={};for(let i=0;i<yes;i++)a[i]='yes';for(let i=yes;i<yes+no;i++)a[i]='no';for(let i=yes+no;i<6;i++)a[i]='unknown';
    const v=verdict(predictions,a,full);assert.equal(v.stats.known,yes+no);
    if(yes+no<3)assert.equal(v.id,'evidence');
    if(v.id==='legible')assert.ok(v.stats.rate>=.75&&v.stats.known>=3);
    if(v.id==='inconvenience')assert.ok(v.stats.rate<=.25&&v.stats.known>=3);
  }
});

function influenceGame(values = [.3, .2, .1]) {
  const interests = ['A', 'B', 'C'].map(name => ({id:name, name}));
  return { interests, domains:['movie', 'brand'], sensitivity:{ status:'complete', winner:null,
    rows:interests.map((e,i) => ({...e, value:values[i], domains:{movie:values[i], brand:values[i]}, halves:[values[i], values[i]]})) } };
}
const labels = {movie:'Movies', brand:'Brands'};
test('strict dominance alone produces a dominant reveal and does not mutate scoring',()=>{
  const g=influenceGame([.7,.2,.1]); g.sensitivity.winner={id:'A',name:'A',value:.7};
  const original=JSON.stringify(g), reveal=influenceReveal(g);
  assert.equal(reveal.kind,'dominant');assert.equal(reveal.strict,g.sensitivity);
  assert.match(influenceCopy(reveal,labels).text,/strict dominance test/);
  assert.equal(JSON.stringify(g),original);
});
test('largest measured influence is named without inventing a strict winner',()=>{
  const g=influenceGame(), r=influenceReveal(g);
  assert.equal(r.kind,'largest');assert.equal(r.leader.name,'A');assert.equal(g.sensitivity.winner,null);
  assert.deepEqual(r.reasons,['below_double_runner_up']);
  assert.match(influenceCopy(r,labels).text,/without clear dominance/);
});
test('small, even near-tied, nonzero leads are descriptive and explicitly qualified',()=>{
  const r=influenceReveal(influenceGame([.00001,.000009,.000008]));
  assert.equal(r.kind,'largest');assert.ok(r.reasons.includes('below_magnitude'));
  assert.match(influenceCopy(r,labels).text,/change is small/);
});
test('different domain leaders get their own credits and retain the overall leader',()=>{
  const g=influenceGame();g.sensitivity.rows[1].domains.brand=.6;
  const r=influenceReveal(g);
  assert.equal(r.kind,'distributed');assert.equal(r.detail,'domain_specific');
  assert.deepEqual(r.domains.map(d=>d.leaders[0].name),['A','B']);
  assert.match(influenceCopy(r,labels).text,/A moves Movies most; B moves Brands most/);
  assert.match(influenceCopy(r,labels).text,/largest average/);
});
test('half-panel instability is named even when the same interest leads both domains',()=>{
  const g=influenceGame();g.sensitivity.rows[1].halves=[.4,.1];
  const r=influenceReveal(g);assert.equal(r.detail,'unstable');
  assert.match(influenceCopy(r,labels).text,/First half: B. Second half: A/);
});
test('tied averages and half-panel ties never manufacture a single leader',()=>{
  const r=influenceReveal(influenceGame([.3,.3,.1]));
  assert.equal(r.kind,'distributed');assert.equal(r.detail,'tied');assert.equal(r.leader,null);
  assert.match(influenceCopy(r,labels).text,/A \/ B tie/);
  const g=influenceGame();g.sensitivity.rows[1].halves=[.3,.2];
  assert.equal(influenceReveal(g).detail,'unstable');
});
test('complete zero movement is a result, not missing evidence',()=>{
  const r=influenceReveal(influenceGame([0,0,0]));
  assert.equal(r.kind,'distributed');assert.equal(r.detail,'unchanged');
  assert.match(influenceCopy(r,labels).text,/A \/ B \/ C/);
});
test('one usable category is retained without making an overall comparison',()=>{
  const g=influenceGame();g.sensitivity.status='incomplete';
  g.sensitivity.rows.forEach(r=>{r.value=null;r.domains.brand=null;r.halves=[null,null];});
  const r=influenceReveal(g);assert.equal(r.kind,'distributed');assert.equal(r.detail,'partial');
  assert.equal(r.leader,null);assert.equal(r.domains[0].leaders[0].id,'A');
  assert.match(influenceCopy(r,labels).text,/Movies: A/);
});
test('partial per-interest coverage is scoped to measured competitors, never zero-filled',()=>{
  const g=influenceGame();g.sensitivity.status='incomplete';
  const missing=g.sensitivity.rows[0];missing.value=null;missing.domains={movie:null,brand:null};missing.halves=[null,null];
  const r=influenceReveal(g);assert.equal(r.detail,'partial');assert.equal(r.leader,null);
  assert.deepEqual(r.domains[0].missing.map(x=>x.id),['A']);
  assert.match(influenceCopy(r,labels).text,/B moves the ranking most among the measured interests/);
});
test('missing halves do not discard valid full-panel comparisons',()=>{
  const g=influenceGame();g.sensitivity.status='incomplete';g.sensitivity.rows[0].halves=[null,null];
  const r=influenceReveal(g);assert.equal(r.kind,'largest');
  assert.match(influenceCopy(r,labels).text,/stability is unverified/);
});
test('insufficient means no two interests can be compared within any category',()=>{
  const g=influenceGame();g.sensitivity.status='incomplete';
  g.sensitivity.rows.forEach((r,i)=>{r.value=null;r.halves=[null,null];r.domains={movie:i===0?.3:null,brand:i===1?.2:null};});
  const r=influenceReveal(g);assert.equal(r.kind,'insufficient');
  assert.match(influenceCopy(r,labels).text,/A \/ B \/ C/);
});
test('typed labels are preserved and an unfinished ablation remains pending',()=>{
  const g=influenceGame();g.interests[0].label='A (hobby audience)';
  assert.match(influenceCopy(influenceReveal(g),labels).text,/A \(hobby audience\)/);
  g.sensitivity=null;assert.equal(influenceReveal(g).kind,'pending');
});
const panel = scores => scores.map((score,i)=>({id:String(i),name:`Title ${i}`,score}));
test('receipts show entrants, exits and within-panel positions from unsorted data',()=>{
  const c=recommendationChanges(panel([4,3,2,1]),panel([1,2,3,4]));
  assert.equal(c.entrants[0].name,'Title 3');assert.equal(c.entrants[0].before.rank,'#4');assert.equal(c.entrants[0].after.rank,'#1');
  assert.equal(c.exits[0].name,'Title 0');assert.equal(c.exits[0].after.rank,'#4');
});
test('same top three can still reveal changes further down the fixed panel',()=>{
  const c=recommendationChanges(panel([6,5,4,3,2,1]),panel([6,5,4,1,2,3]));
  assert.equal(c.entrants.length,0);assert.equal(c.exits.length,0);assert.equal(c.moves.length,2);
});
test('score changes with unchanged order never create recommendation swaps',()=>{
  const c=recommendationChanges(panel([4,3,2,1]),panel([.8,.6,.4,.2]));
  assert.equal(c.changed,false);assert.equal(c.moves.length,0);
});
test('tied third places are all included and arbitrary tie ordering is ignored',()=>{
  const base=panel([5,4,3,3,1]);
  const c=recommendationChanges(base,[...base].reverse());
  assert.equal(c.before.length,4);assert.equal(c.before[2].rank,'tied #3–4');
  assert.equal(c.changed,false);assert.equal(c.entrants.length,0);
});
test('missing, flat, duplicate, nonfinite and too-small panels cannot supply examples',()=>{
  const base=panel([4,3,2,1]);
  for(const reduced of [[],base.slice(1),panel([1,1,1,1]),panel([4,3,NaN,1]),panel([4,3,Infinity,1]),[...base.slice(0,3),base[0]]])assert.equal(recommendationChanges(base,reduced).available,false);
  assert.equal(recommendationChanges(base.slice(0,3),base.slice(0,3)).available,false);
});
test('recommendation receipts exclude unexpected items outside the fixed panel',()=>{
  const base=panel([4,3,2,1]);
  const c=recommendationChanges(base,[...base,{id:'extra',name:'Unrequested',score:100}]);
  assert.equal(c.changed,false);assert.ok(!c.after.some(x=>x.id==='extra'));
});
test('nine archived profiles have reproducible before/after verdicts, with no changed strict scores',()=>{
  const report=analyze();
  assert.deepEqual(report.before,{no_single_culprit:8,dominant:1});
  assert.deepEqual(report.after,{distributed:5,largest:3,dominant:1});
  assert.deepEqual(report.details,{domain_specific:4,unstable:1,qualified:3,strict:1});
  for(const {game} of profiles){
    const original=JSON.stringify(game), oldVerdict=verdict(game.predictions,{},game.sensitivity);
    const r=influenceReveal(game);assert.notEqual(r.kind,'insufficient');
    assert.ok(r.domains.every(d=>!d.missing.length));
    assert.equal(JSON.stringify(game),original);
    assert.deepEqual(verdict(game.predictions,{},game.sensitivity),oldVerdict);
  }
});
test('archived overthinker examples name the actual games and exact changed ranks',()=>{
  const g=profiles[0].game, interest=g.interests.find(e=>e.name==='Severance');
  const c=recommendationChanges(g.full.videogame,g.ablations[interest.id].videogame);
  assert.ok(c.entrants.some(x=>x.name==='Kenshi'&&x.after.rank==='#1'));
  assert.ok(c.exits.some(x=>x.name==='Control'&&x.before.rank==='#1'));
});

test('final result retains every original verdict field and the same Act III finding across all archived profiles',()=>{
  for(const {game} of profiles){
    const original=JSON.stringify(game), answers=Object.fromEntries(game.predictions.map((p,i)=>[p.id,i%2?'no':'yes']));
    const {influence,...result}=finalResult(game,answers,labels);
    assert.deepEqual(result,verdict(game.predictions,answers,game.sensitivity));
    assert.equal(influence.explanation,influenceCopy(influenceReveal(game),labels).text);
    assert.equal(JSON.stringify(game),original);
  }
});
test('copied domain-specific result names the category leaders without promoting them to a strict winner',()=>{
  const g=profiles[0].game, result=finalResult(g,{}, {movie:'Movies',videogame:'Games'});
  assert.equal(result.winner,null);assert.equal(result.id,'evidence');
  const text=summary(result,'recorded');
  assert.match(text,/Movies: Blue Bottle Coffee/);assert.match(text,/Games: Severance/);
  assert.match(text,/Largest average: Severance/);assert.match(text,/No clear overall dominance/);
  assert.match(text,/not predictions from my own interests/);
  assert.doesNotMatch(text,/No clear single influence|No clear winner/);
});
test('dominant and qualified-largest cards carry different claims',()=>{
  const dominant=influenceSummary(influenceReveal(profiles.find(p=>p.id==='activity_5').game),labels);
  const largest=influenceSummary(influenceReveal(profiles.find(p=>p.id==='activity_1').game),labels);
  assert.equal(dominant.label,'DOMINANT ON THESE PANELS');assert.equal(dominant.entries[0].names,'Radiohead');
  assert.equal(largest.label,'LARGEST WITHOUT CLEAR DOMINANCE');assert.equal(largest.entries[0].names,'Radiohead');
  assert.match(largest.qualification,/strict dominance test was not met/);
  assert.ok(largest.entries.some(e=>e.names==='Blue Bottle Coffee'));
});
test('unstable and tied summaries credit competing interests and explain the distinction',()=>{
  const g=profiles.find(p=>p.id==='comfort').game, card=influenceSummary(influenceReveal(g),labels);
  assert.equal(card.label,'SHARED INFLUENCE');
  assert.deepEqual(card.entries.map(e=>e.names),['Friends','Starbucks','Friends']);
  assert.match(card.qualification,/half-panel/);
  const tied=influenceSummary(influenceReveal(influenceGame([.3,.3,.1])),labels);
  assert.equal(tied.entries[0].names,'A / B');assert.match(tied.qualification,/tie on the full panels/);
});
test('partial influence summaries retain typed labels, measured scope and unavailable interests',()=>{
  const g=influenceGame();g.interests[0].label='A (hobby audience)';g.sensitivity.status='incomplete';
  g.sensitivity.rows[2].value=null;g.sensitivity.rows[2].domains.movie=null;
  g.sensitivity.rows.forEach(r=>{r.value=null;r.domains.brand=null;r.halves=[null,null];});
  const card=influenceSummary(influenceReveal(g),labels);
  assert.equal(card.label,'PARTIAL INFLUENCE EVIDENCE');
  assert.deepEqual(card.entries[0],{label:'Movies · largest among measured',names:'A (hobby audience)'});
  assert.ok(card.entries.some(e=>e.label==='Movies · unavailable'&&e.names==='C'));
  assert.match(card.qualification,/No overall ranking or dominance claim/);
});
test('missing influence and valid zero movement remain distinct on share cards',()=>{
  const g=influenceGame();g.sensitivity.rows.forEach(r=>{r.value=null;r.domains={movie:null,brand:null};r.halves=[null,null];});
  g.sensitivity.status='incomplete';
  const missing=influenceSummary(influenceReveal(g),labels);
  assert.equal(missing.label,'INSUFFICIENT INFLUENCE EVIDENCE');assert.equal(missing.entries[0].names,'A / B / C');
  const unchanged=influenceSummary(influenceReveal(influenceGame([0,0,0])),labels);
  assert.equal(unchanged.label,'THE MIX HOLDS ITS GROUND');assert.equal(unchanged.entries[0].names,'A / B / C');
  assert.match(unchanged.qualification,/rank order unchanged/);
});
test('small movement and missing stability checks survive the compact card summary',()=>{
  const g=influenceGame([.03,.02,.01]);g.sensitivity.status='incomplete';g.sensitivity.rows[0].halves=[null,null];
  const card=influenceSummary(influenceReveal(g),labels);
  assert.match(card.qualification,/change is small/);assert.match(card.qualification,/stability is unverified/);
});
const measureText=(text,font)=>[...text].length*Number(font.match(/(\d+)px/)[1])*.6;
test('PNG layout includes every influence name, qualifier and source label with no overlapping text blocks',()=>{
  for(const {game} of profiles){
    const v=finalResult(game,{},labels), source='RECORDED DEMO · EXAMPLE PROFILE';
    const layout=shareCardLayout(v,source,measureText), text=layout.blocks.flatMap(b=>b.lines).join(' ').replace(/\s+/g,' ');
    assert.equal(layout.width,1080);assert.ok(layout.height>=1350);assert.match(text,/RECORDED DEMO · EXAMPLE PROFILE/);
    for(const entry of v.influence.entries)assert.ok(text.includes(`${entry.label}: ${entry.names}`));
    assert.ok(text.includes(v.influence.qualification));
    for(let i=0;i<layout.blocks.length;i++){
      const block=layout.blocks[i], bottom=block.y+block.lineHeight*block.lines.length;
      assert.ok(bottom<layout.height-30);
      assert.ok(block.lines.every(line=>measureText(line,block.font)<=940));
      if(i)assert.ok(block.y>=layout.blocks[i-1].y+layout.blocks[i-1].lineHeight*layout.blocks[i-1].lines.length);
    }
  }
});
test('long interest labels wrap without dropping characters or clipping qualifiers from the PNG',()=>{
  const g=profiles[0].game, v=finalResult(g,{},labels);
  v.influence.entries=Array.from({length:5},(_,i)=>({label:`Domain ${i}`,names:`${'長い題名🎵'.repeat(25)} (hobby audience)`}));
  const layout=shareCardLayout(v,'RECORDED DEMO · EXAMPLE PROFILE',measureText);
  assert.ok(layout.height>1350);
  const compact=layout.blocks.flatMap(b=>b.lines).join('').replace(/\s/g,'');
  for(const entry of v.influence.entries)assert.ok(compact.includes(entry.names.replace(/\s/g,'')));
  assert.ok(compact.includes(v.influence.qualification.replace(/\s/g,'')));
  const word='🎵'.repeat(20), lines=wrapLines(word,30,s=>[...s].length*10);
  assert.equal(lines.join(''),word);assert.ok(lines.every(s=>[...s].length<=3));
});
