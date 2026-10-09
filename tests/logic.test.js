import test from 'node:test';
import assert from 'node:assert/strict';
import { predictability, verdict, summary } from '../static/logic.js';
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
