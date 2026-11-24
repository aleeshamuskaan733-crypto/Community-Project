const fmt=(n,d=0)=>Number(n).toLocaleString('en-IN',{maximumFractionDigits:d,minimumFractionDigits:d});
const rs=n=>'₹'+fmt(n,0);
async function post(url,form){
  const body=new URLSearchParams(new FormData(form));
  // unchecked checkboxes are absent from FormData; that is what we want
  const r=await fetch(url,{method:'POST',body});return r.json();
}
function bars(el,labels,a,b,la,lb){
  const W=640,H=220,p=30,max=Math.max(1,...a,...b),bw=(W-2*p)/labels.length;
  let s=`<svg viewBox="0 0 ${W} ${H}" width="100%" role="img" aria-label="${la} vs ${lb} by month">`;
  labels.forEach((l,i)=>{
    const x=p+i*bw,ha=(H-2*p)*a[i]/max,hb=(H-2*p)*b[i]/max;
    s+=`<rect x="${x+3}" y="${H-p-ha}" width="${bw/2-4}" height="${ha}" fill="#94a3a0"><title>${la} ${l}: ${fmt(a[i])}</title></rect>`;
    s+=`<rect x="${x+bw/2}" y="${H-p-hb}" width="${bw/2-4}" height="${hb}" fill="#f2a50c"><title>${lb} ${l}: ${fmt(b[i])}</title></rect>`;
    s+=`<text x="${x+bw/2}" y="${H-10}" text-anchor="middle">${l}</text>`;
  });
  s+=`<text x="${p}" y="14">■ ${la}  </text><text x="${p+170}" y="14" style="fill:#f2a50c">■ ${lb}</text></svg>`;
  el.innerHTML=s;
}
function stat(v,l){return `<div class="card"><div class="stat">${v}</div><div class="lbl">${l}</div></div>`}

const calc=document.getElementById('calc');
if(calc){
  const out=document.getElementById('out');
  const run=async e=>{
    if(e)e.preventDefault();
    const d=await post('/api/estimate',calc), cb=d.current_bill;
    document.getElementById('billbox').innerHTML=
      `<div class="tablewrap"><table><tr><td>Fixed charge</td><td>${rs(cb.gross.fixed)}</td></tr>
      <tr><td>Energy charges</td><td>${rs(cb.gross.energy)}</td></tr>
      <tr><td>FPPCA + P&amp;G surcharge</td><td>${rs(cb.gross.fppca+cb.gross.pg)}</td></tr>
      <tr><td>Tax</td><td>${rs(cb.gross.tax)}</td></tr>
      <tr><td><b>Sub total 1</b></td><td><b>${rs(cb.gross.total)}</b></td></tr>
      <tr><td>Gruha Jyothi subsidy (${cb.subsidy.units||0} units + fixed)</td><td>− ${rs(cb.subsidy.total)}</td></tr>
      <tr><td><b>Bill amount (payable)</b></td><td><b>${rs(cb.payable)}</b></td></tr></table></div>`;
    out.innerHTML='<div class="grid">'+
      stat(fmt(d.annual_generation)+' kWh','Solar generation / year')+
      stat(rs(d.annual_saving),'Estimated bill saving / year')+
      stat(d.payback_years===null?'—':fmt(d.payback_years,1)+' yrs','Simple payback on '+rs(d.net_cost)+' net cost')+
      stat(fmt(d.co2_kg/1000,2)+' t','CO₂ avoided / year (≈ '+fmt(d.trees)+' trees)')+'</div>'+
      `<p class="note">Suggested size to offset ~100 % of your use: <b>${d.suggested_kw} kW</b>. System cost ${rs(d.system_cost)}, subsidy ${rs(d.subsidy)}. 25-year net gain ≈ ${rs(d.gain_25y)}.</p>`;
    if(calc.gruha_jyothi.checked&&d.annual_saving<3000)
      out.innerHTML+='<div class="warn">Your Gruha Jyothi subsidy already covers most of your bill, so solar saves little in rupees. The value is mainly CO₂ reduction, protection if your use grows, and income from surplus credit.</div>';
    bars(document.getElementById('chart'),d.rows.map(r=>r.month),d.rows.map(r=>r.bill_before),d.rows.map(r=>r.bill_after),'Bill now (₹)','Bill with solar (₹)');
    document.getElementById('rows').innerHTML=d.rows.map(r=>`<tr><td>${r.month}</td><td>${fmt(r.generation)}</td><td>${fmt(r.net_units)}</td><td>${rs(r.bill_before)}</td><td>${rs(r.bill_after)}</td></tr>`).join('');
  };
  calc.addEventListener('submit',run);calc.addEventListener('change',()=>run());run();
}
const com=document.getElementById('com');
if(com){
  const run=async e=>{
    if(e)e.preventDefault();
    const d=await post('/api/community',com);
    document.getElementById('cout').innerHTML='<div class="grid">'+
      stat(fmt(d.adopters),'Households with rooftop solar')+
      stat(fmt(d.installed_kw,0)+' kW','Total installed capacity')+
      stat(fmt(d.total_kwh/1000,1)+' MWh','Clean energy / year ('+fmt(d.share_pct,0)+' % of demand)')+
      stat('₹'+fmt(d.money_saved/100000,1)+' lakh','Community bill savings / year')+
      stat(fmt(d.co2_tonnes,0)+' t','CO₂ avoided / year (≈ '+fmt(d.trees)+' trees)')+
      stat('₹'+fmt(d.investment/100000,1)+' lakh','Gross investment (before subsidy)')+'</div>';
  };
  com.addEventListener('submit',run);com.addEventListener('change',()=>run());run();
}
