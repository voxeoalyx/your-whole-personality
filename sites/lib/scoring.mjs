// Direct port of scoring.py: retain tie handling, missing values and strict thresholds.
const mean=xs=>xs.reduce((a,b)=>a+b,0)/xs.length;
export function ranks(values) {
  const order=values.map((v,i)=>[i,v]).sort((a,b)=>a[1]-b[1]), out=values.map(()=>0);
  for(let i=0;i<order.length;){let j=i+1;while(j<order.length&&order[j][1]===order[i][1])j++;
    for(let k=i;k<j;k++)out[order[k][0]]=(i+1+j)/2;i=j;}
  return out;
}
export function scores(rows){return Object.fromEntries(rows.filter(x=>typeof x.score==='number'&&Number.isFinite(x.score)).map(x=>[x.id,x.score]));}
export function distance(a,b,ids){
  if(ids.length<4||ids.some(i=>!(i in a)||!(i in b)))return null;
  const av=ranks(ids.map(i=>a[i])),bv=ranks(ids.map(i=>b[i])),am=mean(av),bm=mean(bv);
  const den=Math.sqrt(av.reduce((s,v)=>s+(v-am)**2,0)*bv.reduce((s,v)=>s+(v-bm)**2,0));
  if(!den)return null;
  const rho=av.reduce((s,v,i)=>s+(v-am)*(bv[i]-bm),0)/den;
  return (1-Math.max(-1,Math.min(1,rho)))/2;
}
export function sensitivity(interests,full,ablations){
  const rows=interests.map(e=>{const row={id:e.id,name:e.name,domains:{},value:null,halves:[null,null]}, ds=[],halves=[[],[]];
    for(const [domain,base] of Object.entries(full)){const reduced=ablations[e.id]?.[domain]||[],ids=base.map(x=>x.id).sort();
      const d=distance(scores(base),scores(reduced),ids);row.domains[domain]=d;ds.push(d);
      for(let h=0;h<2;h++)halves[h].push(distance(scores(base),scores(reduced),ids.filter((_,i)=>i%2===h)));}
    if(ds.length===2&&ds.every(d=>d!==null))row.value=mean(ds);
    halves.forEach((values,h)=>{if(values.length===2&&values.every(d=>d!==null))row.halves[h]=mean(values);});return row;});
  const complete=Object.keys(full).length===2&&rows.every(r=>r.value!==null&&r.halves.every(x=>x!==null));
  const ordered=[...rows].sort((a,b)=>(b.value??-1)-(a.value??-1));let winner=null;
  if(complete&&ordered.length>1){const [top,runner]=ordered;
    if(top.value>.10&&top.value>2*runner.value&&[0,1].every(h=>rows.reduce((a,b)=>b.halves[h]>a.halves[h]?b:a).id===top.id))winner={id:top.id,name:top.name,value:top.value};}
  return {status:complete?'complete':'incomplete',winner,rows:ordered,domains:Object.keys(full),method:'mean((1 - tie-aware Spearman rho) / 2), two fixed panels; same winner on disjoint halves'};
}
