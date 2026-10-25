/* Operating data, projections and sensitivity results are read from Eclipse Ditto. */
'use strict';
const SVG='http://www.w3.org/2000/svg';
const $=id=>document.getElementById(id);
const colors={ready:'#83b8ce',planned:'#8292a7',waiting_acid:'#ef9971',acidifying:'#bc9ee8',ramping:'#e2c76d',producing:'#69d6b0',depleted:'#78889a'};
const fmt=(n,d=1)=>Number(n).toLocaleString('en-GB',{maximumFractionDigits:d,minimumFractionDigits:d});
const clean=s=>String(s).replaceAll('_',' ');
let data=null,selected='mpp-b1',busy=false,timer=null,queued=null;
function node(tag,attrs={},text){const n=document.createElementNS(SVG,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(text!==undefined)n.textContent=text;return n;}
function add(parent,tag,attrs,text){const n=node(tag,attrs,text);parent.appendChild(n);return n;}
function state(name){return data.twins[data.namespace+':'+name].state;}
function label(parent,x,y,text,size=13,color='#dce6f2',extra={}){return add(parent,'text',{x,y,fill:color,'font-size':size,'font-family':'system-ui',...extra},text);}
function clickable(g,name){g.setAttribute('role','button');g.setAttribute('tabindex','0');g.setAttribute('aria-label','Inspect '+name);g.classList.add('twin');g.addEventListener('click',()=>inspect(name));g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();inspect(name);}});}
function inspect(name){
  selected=name;const s=state(name);$('detail-title').textContent=s.label||name;const dl=$('detail');dl.replaceChildren();
  const fields={state:'Lifecycle',acid_requirement_t:'Assumed commissioning dose (t)',planned_acid_day:'Planned acidification day',acid_start_day:'Simulated acid start',baseline_commission_day:'Baseline production start',projected_commission_day:'Projected production start',commission_delay_days:'Commissioning delay (days)',potential_kg_u_day:'Potential extraction (kg U/day)',extraction_kg_u_day:'Actual simulated extraction (kg U/day)',ix_factor:'Area IX flow factor',drying_factor:'Shared drying/WIP flow factor',remaining_uranium_kg:'U retained in model group (kg)',acid_inventory_t:'Commissioning acid stock (t)',acid_received_t:'Delivered acid (t)',acid_used_t:'Reserved acid (t)',ix_output_kg_u_day:'IX recovered U (kg/day)',ix_capacity_kg_u_day:'IX limit (kg U/day)',solution_m3_day:'Solution equivalent (m³/day)',ix_utilization:'IX utilization',pending_kg_u:'Recovered U in WIP (kg)',wip_limit_kg_u:'Assumed end-of-day WIP target (kg)',drying_kg_u_day:'Drying (kg U/day)',drying_capacity_kg_u_day:'Drying limit (kg U/day)',product_kg_u:'Cumulative dried U (kg)'};
  Object.entries(fields).forEach(([key,title])=>{if(key in s){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=title;dd.textContent=s[key]===null?'Not started':typeof s[key]==='number'?fmt(s[key],key.endsWith('_factor')?3:1):clean(s[key]);dl.append(dt,dd);}});
  document.querySelectorAll('.twin').forEach(g=>g.classList.toggle('selected',g.getAttribute('aria-label')==='Inspect '+name));
}
function pipe(svg,d,active,labelText,x,y){
  add(svg,'path',{d,fill:'none',stroke:'#243d4a','stroke-width':7});
  add(svg,'path',{d,fill:'none',stroke:active?'#70c6d4':'#53616d','stroke-width':2.2,'marker-end':'url(#flow-arrow)',class:active?'flowing':''});
  if(labelText)label(svg,x,y,labelText,12,'#8cd8df');
}
function drawMap(){
  const svg=$('map');svg.replaceChildren();const defs=add(svg,'defs');
  const marker=add(defs,'marker',{id:'flow-arrow',viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:6,markerHeight:6,orient:'auto'});add(marker,'path',{d:'M0 0 L10 5 L0 10 z',fill:'#70c6d4'});
  const pattern=add(defs,'pattern',{id:'ground-grid',width:24,height:24,patternUnits:'userSpaceOnUse'});add(pattern,'circle',{cx:1,cy:1,r:.65,fill:'#294039'});add(svg,'rect',{width:1200,height:675,fill:'url(#ground-grid)'});
  // Process connectivity is meaningful; all field footprints and positions are synthetic.
  pipe(svg,'M 563 202 H 602 V 329 H 955 V 450',state('sat1').ix_output_kg_u_day>0,'Satellite recovered-U transfer (aggregate)',660,368);
  pipe(svg,'M 1163 202 H 1184 V 349 H 1015 V 450',state('sat2').ix_output_kg_u_day>0);
  pipe(svg,'M 563 532 H 875',state('mpp').ix_output_kg_u_day>0,'MPP recovered U',657,518);
  ['sat1','sat2','mpp'].forEach(aid=>{
    const a=state(aid),tank=state('acid-'+aid),ax=a.map_x,ay=a.map_y;
    add(svg,'path',{d:`M${ax+8} ${ay+12} L${ax+520} ${ay} L${ax+550} ${ay+37} L${ax+541} ${ay+247} L${ax+24} ${ay+257} L${ax} ${ay+215} Z`,fill:'#15282a',stroke:'#405d50','stroke-width':1.2});
    label(svg,ax+18,ay+32,a.label+' production area',17,'#e3eee2');
    const tg=add(svg,'g');clickable(tg,'acid-'+aid);add(tg,'rect',{x:ax+130,y:ay+47,width:228,height:34,rx:5,fill:'#382d4c',stroke:'#9579b4'});label(tg,ax+142,ay+69,`${fmt(tank.acid_inventory_t,0)} t commissioning acid`,12,'#e5cef7');
    [0,1,2].forEach(i=>{
      const id=`${aid}-b${i}`,b=state(id),x=b.x,y=b.y,affected=b.commission_delay_days>0;
      if(i)add(svg,'path',{d:`M${ax+244} ${ay+81} V${ay+91} H${x+52} V${y+4}`,fill:'none',stroke:'#b69bd2','stroke-dasharray':'4 4','stroke-width':1.3});
      pipe(svg,`M${x+52} ${y+92} V${ay+231} H${ax+489} V${ay+204}`,b.extraction_kg_u_day>0);
      const g=add(svg,'g');clickable(g,id);
      add(g,'polygon',{points:`${x},${y+9} ${x+94},${y} ${x+108},${y+70} ${x+98},${y+96} ${x+5},${y+86}`,fill:colors[b.state],stroke:affected?'#ffc27a':colors[b.state],'fill-opacity':.13,'stroke-width':affected?3:1.4});
      label(g,x+11,y+27,id.toUpperCase(),12,'#e7edf5',{'font-weight':650});
      // A well-pattern symbol, not individual measured or separately modelled wells.
      [0,1,2,3].forEach(j=>add(g,'circle',{cx:x+18+j*21,cy:y+43,r:2.5,fill:'none',stroke:colors[b.state],'stroke-width':1.3}));
      label(g,x+11,y+65,clean(b.state),11.5,colors[b.state]);
      label(g,x+11,y+83,i?`start D${b.projected_commission_day} · base ${b.baseline_commission_day}`:`${fmt(b.extraction_kg_u_day/1000,2)} t U/day`,9.7);
    });
    const ix=add(svg,'g');clickable(ix,aid);add(ix,'rect',{x:ax+445,y:ay+130,width:88,height:74,rx:5,fill:'#18323e',stroke:'#70c6d4'});label(ix,ax+456,ay+152,'IX plant',13);label(ix,ax+456,ay+175,fmt(a.ix_output_kg_u_day/1000,2)+' t U/d',11);label(ix,ax+456,ay+193,fmt(a.ix_utilization*100,0)+'% of limit',10,'#a2bac8');
    label(svg,ax+22,ay+285,`Actual solution equivalent: ${fmt(a.solution_m3_day/24,0)} m³/h`,12,'#9bbabc');
  });
  const p=state('packaging'),g=add(svg,'g');clickable(g,'packaging');
  add(g,'rect',{x:875,y:450,width:286,height:155,rx:7,fill:'#203343',stroke:'#70c6d4','stroke-width':2});
  label(g,893,478,'MPP drying & packaging',19);label(g,893,508,`${fmt(p.drying_kg_u_day/1000,2)} t U/day · ${fmt(p.drying_kg_u_day/p.drying_capacity_kg_u_day*100,0)}%`,16);
  label(g,893,535,`WIP ${fmt(p.pending_kg_u/1000,2)} / ${fmt(p.wip_limit_kg_u/1000,2)} t U`,13);
  add(g,'rect',{x:893,y:548,width:246,height:7,fill:'#102131',rx:3});add(g,'rect',{x:893,y:548,width:246*Math.min(1,p.wip_limit_kg_u?p.pending_kg_u/p.wip_limit_kg_u:0),height:7,fill:'#e2c76d',rx:3});
  label(g,893,579,`Shared flow factor ${fmt(p.drying_factor,3)}`,12,'#e2c76d');
  label(svg,660,388,'FLOW PACING',11,'#e2c76d',{'letter-spacing':1.8});label(svg,660,410,'Drying + WIP headroom limit extraction.',12);label(svg,660,430,'Excess potential U remains underground.',12,'#a2b3c8');
}
function chart(id,base,scenario,day,ceiling){
  const svg=$(id);svg.replaceChildren();const left=54,top=18,width=550,height=174,max=Math.max(1,...base,...scenario,ceiling||0)*1.1;
  [0,.5,1].forEach(v=>{const y=top+height*(1-v);add(svg,'line',{x1:left,x2:left+width,y1:y,y2:y,stroke:'#2b3a4e'});label(svg,2,y+4,fmt(max*v,max<20?1:0),10,'#a2b3c8');});
  [0,30,60,90].forEach(d=>label(svg,left+d/90*width-7,218,'D'+d,10,'#a2b3c8'));
  const line=values=>values.map((v,i)=>`${i?'L':'M'}${left+i/90*width},${top+height-v/max*height}`).join(' ');
  add(svg,'path',{d:line(base),stroke:'#70c6d4','stroke-width':2,fill:'none'});add(svg,'path',{d:line(scenario),stroke:'#eeb363','stroke-width':2.5,fill:'none'});
  if(ceiling!==undefined){const y=top+height-ceiling/max*height;add(svg,'line',{x1:left,x2:left+width,y1:y,y2:y,stroke:'#bc9ee8','stroke-dasharray':'5 3'});label(svg,left+5,y-5,'Assumed WIP target',10,'#bc9ee8');}
  add(svg,'line',{x1:left+day/90*width,x2:left+day/90*width,y1:top,y2:top+height,stroke:'#c4cfdf','stroke-dasharray':'4 4'});
}
function renderSensitivity(sweep,assumptions){
  const body=$('sensitivity-grid');body.replaceChildren();
  const head=document.createElement('tr');['Dose multiplier / acidification days',...sweep.acidification_days.map(d=>d+' days')].forEach(t=>{const th=document.createElement('th');th.textContent=t;head.appendChild(th);});body.appendChild(head);
  sweep.dose_multipliers.forEach(dose=>{const tr=document.createElement('tr'),th=document.createElement('th');th.textContent=fmt(dose,2)+'× assumed dose';tr.appendChild(th);sweep.acidification_days.forEach(days=>{const r=sweep.rows.find(x=>x.dose_multiplier===dose&&x.acidification_days===days&&x.wip_target_days===assumptions.wip_target_days),td=document.createElement('td');td.textContent=`${fmt(r.product_delta_kg_u/1000,2)} t U · ${r.delayed_groups} late groups`;if(dose===1&&days===assumptions.acidification_days)td.className='central-case';tr.appendChild(td);});body.appendChild(tr);});
  $('sensitivity-summary').textContent=`Across all ${sweep.case_count} cases: ${sweep.min_delayed_groups}–${sweep.max_delayed_groups} new groups start late; day-90 product difference spans ${fmt(sweep.min_product_delta_kg_u/1000,2)} to ${fmt(sweep.max_product_delta_kg_u/1000,2)} t U.`;
  $('sensitivity-verdict').textContent=sweep.min_delayed_groups>0&&sweep.max_product_delta_kg_u>=-.001?'Commissioning risk persists; a product shortfall is not robust across these assumptions.':sweep.max_delayed_groups===0?'Baseline: every assumption case is compared with its own no-delay run.':'The direction and magnitude below apply only to this illustrative grid.';
}
function render(next){
  if(data&&data.revision===next.revision&&!document.body.classList.contains('stale'))return;
  data=next;document.body.classList.remove('stale');$('error').hidden=true;
  const s=state('site'),scenario=state('scenario'),p=JSON.parse(scenario.projection),sweep=JSON.parse(scenario.sensitivity),blocks=Object.values(data.twins).filter(t=>t.attributes.kind==='block_group').map(t=>t.state),waiting=blocks.filter(b=>b.state==='waiting_acid').length;
  $('connection').textContent='● Live platform snapshot · 18 twins';$('day').value=s.day;$('delay').value=s.delay_days;
  $('metric-day').textContent=`Day ${s.day} / 90`;$('metric-product').textContent=fmt(s.product_kg_u/1000,2)+' t U';$('metric-delta').textContent=fmt(s.product_delta_kg_u/1000,2)+' t U';
  $('schedule').textContent=`First arrivals: D3 → D${3+s.delay_days}. Second arrivals stay D60. Applied delay: ${s.delay_days} days. All figures are simulated.`;
  $('narrative').textContent=s.day===0?'Initial condition: no time has elapsed. Existing groups are ready; cumulative production is zero. Show baseline day 30 to see operating flows.':waiting?`${waiting} new groups are waiting for commissioning acid. Existing groups continue under the protected sustaining-acid assumption.`:s.drying_factor<.999?`The drying/WIP pacing rule limits upstream flow to ${fmt(s.drying_factor*100,1)}% after area IX limits. Withheld potential extraction remains underground.`:'Follow the simulated delivery → commissioning → processing chain below.';
  const values=[['Arrival',`D${3+s.delay_days}`,`baseline D3 · +${s.delay_days} days`],['Commissioning acid',fmt(s.acid_inventory_t,0)+' t',waiting+' groups waiting'],['Solution equivalent',fmt(s.solution_m3_day/24,0)+' m³/h','at assumed 100 mg U/L'],['IX recovery',fmt(s.recovered_kg_u_day/1000,2)+' t U/day','98% plant factor'],['Drying WIP',fmt(s.pending_kg_u/1000,2)+' t U',`target ≤ ${fmt(s.wip_limit_kg_u/1000,2)} t U`],['Dried product',fmt(s.drying_kg_u_day/1000,2)+' t U/day',`limit ${fmt(s.drying_capacity_kg_u_day/1000,2)} t U/day`]];
  const chain=$('causal-chain');chain.replaceChildren();values.forEach(([title,value,note])=>{const box=document.createElement('div'),small=document.createElement('small'),strong=document.createElement('strong'),p=document.createElement('span');small.textContent=title;strong.textContent=value;p.textContent=note;box.append(small,strong,p);chain.appendChild(box);});
  $('projection-summary').textContent=`Day-90 difference: ${fmt(p.final_product_delta_kg_u/1000,2)} t U. Equal delivered acid at horizon: ${p.delivered_t_equal_at_horizon?'yes':'no'}.`;
  $('balance').textContent=`U account: ${fmt(s.extracted_kg_u/1000,2)} t extracted = ${fmt(s.product_kg_u/1000,2)} t product + ${fmt(s.pending_kg_u/1000,2)} t WIP + ${fmt(s.unrecovered_kg_u/1000,2)} t unrecovered.`;
  $('flow-limit').textContent=`Potential extraction today: ${fmt(s.potential_extraction_kg_u_day/1000,2)} t U. Capacity-withheld potential: ${fmt(s.withheld_kg_u_day/1000,2)} t U. This is not destroyed uranium or permanent lost production.`;
  drawMap();chart('production-chart',p.baseline_product_kg_u.map(v=>v/1000),p.scenario_product_kg_u.map(v=>v/1000),s.day);chart('acid-chart',p.baseline_acid_t,p.scenario_acid_t,s.day);chart('wip-chart',p.baseline_wip_kg_u.map(v=>v/1000),p.scenario_wip_kg_u.map(v=>v/1000),s.day,s.wip_limit_kg_u/1000);renderSensitivity(sweep,scenario.assumptions);
  const body=$('block-table');body.replaceChildren();blocks.filter(b=>b.planned_acid_day!==null).forEach(b=>{const tr=document.createElement('tr');[b.label,clean(b.state),fmt(b.acid_requirement_t,0)+' t','D'+b.baseline_commission_day,'D'+b.projected_commission_day,b.commission_delay_days+' days'].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.appendChild(td);});body.appendChild(tr);});
  inspect(selected);$('provenance').textContent=`${data.source} · ${data.transport} · ${data.namespace} · revision ${data.revision}`;if(s.day>=90)stopPlay();
}
function stopPlay(){if(timer){clearInterval(timer);timer=null;}$('play').textContent='Play days';}
async function request(command){
  if(busy){if(command)queued=command;return;}busy=true;
  if(command)document.querySelectorAll('[data-control]').forEach(b=>b.disabled=true);
  if(timer)$('play').disabled=false;
  try{const response=await fetch(command?'/api/control':'/api/state',command?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(command)}:{cache:'no-store'});const body=await response.json();if(!response.ok)throw new Error(body.error||'Platform request failed');render(body);}
  catch(e){stopPlay();queued=null;document.body.classList.add('stale');$('connection').textContent='Platform unavailable · displayed values are stale';$('error').hidden=false;$('error').textContent=e.message;}
  finally{busy=false;document.querySelectorAll('[data-control]').forEach(b=>b.disabled=false);if(queued){const next=queued;queued=null;request(next);}}
}
$('baseline').onclick=()=>{stopPlay();request({action:'configure',day:30,delay_days:0});};
$('example-delay').onclick=()=>{stopPlay();request({action:'configure',day:30,delay_days:28});};
$('apply').onclick=()=>{stopPlay();request({action:'configure',delay_days:Number($('delay').value)});};
$('seek').onclick=()=>{stopPlay();request({action:'configure',day:Number($('day').value)});};
$('advance').onclick=()=>request({action:'advance',days:7});
$('reset').onclick=()=>{stopPlay();request({action:'reset'});};
$('play').onclick=()=>{if(timer){stopPlay();return;}$('play').textContent='Pause';timer=setInterval(()=>{if(!busy)request({action:'advance',days:1});},1500);};
request();setInterval(()=>{if(!busy&&!timer)request();},8000);