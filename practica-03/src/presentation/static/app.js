'use strict';
const $ = id => document.getElementById(id);
let data = null, clock = 0, eventIndex = 0, playing = true, lastFrame = 0, lastDraw = 0;
const names = {arrival:'Llegada',service_start:'Comienza servicio',departure:'Salida',end:'Fin de simulación'};
const fmt = (n, digits=3) => n == null || !Number.isFinite(n) ? '—' : Number(n).toFixed(digits);
const percent = n => fmt(n * 100, 1) + '%';

function config(){return {arrival_rate:Number($('lambda').value),service_rate:Number($('mu').value),duration:Number($('duration').value),seed:Number($('seed').value)}}
async function loadSimulation(){
  $('alert').textContent=''; $('run').disabled=true;
  try {
    const response=await fetch('/api/simulate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(config())});
    const result=await response.json(); if(!response.ok) throw Error(result.error || 'Error inesperado');
    data=result; clock=0; eventIndex=0; playing=true; lastFrame=0;
    $('timeline').max=data.config.duration;$('timeline').value=0;$('durationText').textContent='/ '+data.config.duration;
    $('play').textContent='❚❚ Pausar'; $('conveyor').classList.remove('paused');
    draw(true);
  }catch(error){$('alert').textContent=error.message}
  finally{$('run').disabled=false}
}
function snapshot(){
  if(!data)return null;
  while(eventIndex<data.events.length && data.events[eventIndex].t<=clock+0.00000001)eventIndex++;
  return data.events[Math.max(0,eventIndex-1)] || {t:0,queue:0,system:0,busy:0,arrived:0,completed:0,mean_wait:0,mean_system:0,avg_queue:0,avg_system:0,utilization:0};
}
function liveStats(s){
  // Integración exacta por tramos constantes desde el último evento hasta el reloj de animación.
  const dt=Math.max(0,clock-s.t),t=Math.max(clock,0.00000001);
  const q=(s.avg_queue*s.t+dt*s.queue)/t;
  const l=(s.avg_system*s.t+dt*s.system)/t;
  const u=(s.utilization*s.t+dt*s.busy)/t;
  return {Lq:q,L:l,rho:u,Wq:s.mean_wait,W:s.mean_system};
}
function draw(force=false){
  if(!data)return;
  const s=snapshot(), live=liveStats(s);
  $('clock').textContent=fmt(clock,1);$('timeline').value=clock;
  $('arrived').textContent=s.arrived;$('completed').textContent=s.completed;
  $('queue').textContent=s.queue;$('util').textContent=percent(live.rho);
  $('queueCount').textContent=s.queue;$('processing').textContent=s.busy?'SÍ':'NO';$('finished').textContent=s.completed;
  $('workState').textContent=s.busy?'● EN SERVICIO':'○ SERVIDOR LIBRE';
  $('status').textContent=clock>=data.config.duration?'● FINALIZADO':playing?'● EJECUTANDO':'● PAUSADO';
  $('status').style.color=clock>=data.config.duration?'#ffc368':'#58dab0';
  $('stationBody').parentElement.classList.toggle('active',Boolean(s.busy));
  const start=[...data.events.slice(0,eventIndex)].reverse().find(e=>e.type==='service_start' && !data.events.slice(data.events.indexOf(e)+1,eventIndex).some(d=>d.type==='departure' && d.id===e.id));
  $('stationJob').textContent=s.busy&&start?'PKG-'+String(start.id).padStart(3,'0'):'LIBRE';
  const queued=[];
  // Orden FIFO reconstruido desde el registro; se limita la representación a 9 cajas.
  for(let k=0;k<eventIndex;k++){const e=data.events[k];if(e.type==='arrival')queued.push(e.id);if(e.type==='service_start'){const idx=queued.indexOf(e.id);if(idx>=0)queued.splice(idx,1)}}
  const container=$('queuePacks');container.replaceChildren();
  queued.slice(0,9).forEach((id,i)=>{const box=document.createElement('div');box.className='package';box.style.left=`${Math.max(0,61-(Math.min(queued.length,9)-i)*7.4)}%`;const small=document.createElement('small');small.textContent='#'+id;box.append(small);container.append(box)});
  if(queued.length>9){const extra=document.createElement('div');extra.className='package';extra.style.left='1%';extra.textContent='+'+(queued.length-9);container.append(extra)}
  const pairs=[['ρ · utilización','rho','rho'],['L · número medio en sistema','L','L'],['Lq · longitud media de cola','Lq','Lq'],['W · permanencia media','W','W'],['Wq · espera media','Wq','Wq']];
  $('metrics').innerHTML=pairs.map(([label,theoretical,key])=>{const a=data.theory[theoretical],b=live[key];return `<tr><td>${label}</td><td>${fmt(a)}</td><td>${fmt(b)}</td><td>${a==null?'—':fmt(b-a)}</td></tr>`}).join('');
  const recent=data.events.slice(Math.max(0,eventIndex-8),eventIndex).reverse();
  $('log').innerHTML=recent.map(e=>`<div class="logline"><b>${fmt(e.t,2)}</b> ${names[e.type]} ${e.id!=null?'· Paquete #'+e.id:''}${e.type==='service_start'?' · espera '+fmt(e.wait,2):''}</div>`).join('');
  const now=performance.now();if(force || now-lastDraw>90){drawChart($('queueChart'),'queue','#42d3d8',clock);drawChart($('waitChart'),'mean_wait','#ffc368',clock,'Espera promedio');lastDraw=now}
}
function drawChart(canvas,field,color,until,title){
 const rect=canvas.getBoundingClientRect(),dpr=window.devicePixelRatio||1;
 const w=Math.max(180,rect.width),h=210;canvas.width=w*dpr;canvas.height=h*dpr;
 const ctx=canvas.getContext('2d');ctx.scale(dpr,dpr);ctx.clearRect(0,0,w,h);
 let events=data.events.filter(e=>e.t<=until),series=events.map(e=>({x:e.t,y:e[field]}));
 let last=series.at(-1);series.push({x:until,y:last?last.y:0});
 let max=Math.max(1,...series.map(p=>p.y));max*=1.15;
 const left=35,right=w-10,top=20,bottom=h-27,width=right-left,height=bottom-top;
 ctx.font='11px ui-sans-serif,system-ui';ctx.textAlign='right';ctx.strokeStyle='#27384c';ctx.fillStyle='#8c9eb2';ctx.lineWidth=1;
 for(let i=0;i<=4;i++){const y=bottom-(i/4)*height;ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(right,y);ctx.stroke();ctx.fillText(fmt(max*i/4,1),left-8,y+4)}
 ctx.textAlign='center';for(let i=0;i<=4;i++){let x=left+i*width/4;ctx.fillText(fmt(until*i/4,0),x,bottom+17)}
 ctx.beginPath();ctx.lineWidth=2;ctx.strokeStyle=color;
 series.forEach((p,i)=>{let x=left+width*(until?p.x/until:0),y=bottom-height*p.y/max;if(!i)ctx.moveTo(x,y);else if(field==='queue'){let prev=series[i-1];ctx.lineTo(x,bottom-height*prev.y/max);ctx.lineTo(x,y)}else ctx.lineTo(x,y)});ctx.stroke();
 let grad=ctx.createLinearGradient(0,top,0,bottom);grad.addColorStop(0,color+'33');grad.addColorStop(1,color+'02');
 ctx.lineTo(right,bottom);ctx.lineTo(left,bottom);ctx.closePath();ctx.fillStyle=grad;ctx.fill();
}
function frame(now){
 if(!lastFrame)lastFrame=now;const delta=Math.min((now-lastFrame)/1000,.1);lastFrame=now;
 if(data && playing && clock<data.config.duration){clock=Math.min(data.config.duration,clock+delta*Number($('speed').value));if(clock===data.config.duration){playing=false;$('play').textContent='▶ Reproducir';$('conveyor').classList.add('paused')}draw()}
 requestAnimationFrame(frame);
}
// Nueva semilla en cada pulsación de "Generar simulación": así la realización de
// llegadas Poisson (rng.expovariate(λ)) cambia y nunca repite la última ejecución.
let lastSeed = Number($('seed').value);
function newSeed(){
  let s = lastSeed;
  const buf = new Uint32Array(1);
  while(s === lastSeed){(window.crypto || self.crypto).getRandomValues(buf);s = buf[0]}
  lastSeed = s;
  $('seed').value = s;
  return s;
}
$('run').addEventListener('click',()=>{newSeed();loadSimulation()});
$('scenario').addEventListener('change',e=>{if(e.target.value!=='custom'){$('lambda').value=e.target.value;$('mu').value=3;loadSimulation()}});
for(const id of ['lambda','mu'])$(id).addEventListener('input',()=>{$('scenario').value='custom'});
$('play').addEventListener('click',()=>{if(!data)return;if(clock>=data.config.duration){clock=0;eventIndex=0}playing=!playing;$('play').textContent=playing?'❚❚ Pausar':'▶ Reproducir';$('conveyor').classList.toggle('paused',!playing);draw(true)});
$('restart').addEventListener('click',()=>{clock=0;eventIndex=0;playing=true;$('play').textContent='❚❚ Pausar';$('conveyor').classList.remove('paused');draw(true)});
$('timeline').addEventListener('input',e=>{clock=Number(e.target.value);eventIndex=0;draw(true)});
$('export').addEventListener('click',()=>{if(!data)return;const cols=['id','arrival','start','departure','wait','service','system'];let rows=[cols.join(';'),...data.jobs.map(j=>cols.map(k=>Number.isFinite(j[k])?String(j[k]).replace('.',','):j[k]).join(';'))];let blob=new Blob(['\ufeff'+rows.join('\n')],{type:'text/csv;charset=utf-8'});let url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='simulacion_mm1_paquetes.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)});
$('compare').addEventListener('click',async()=>{const b=$('compare');b.disabled=true;$('comparisonResults').textContent='Calculando los tres escenarios…';try{const response=await fetch('/api/scenarios'),r=await response.json();if(!response.ok)throw Error('Error en comparación');$('comparisonResults').innerHTML=`<table><thead><tr><th>Escenario</th><th>λ</th><th>μ</th><th>ρ teórico</th><th>Lq teórico</th><th>Lq simulado</th><th>Wq teórico</th><th>Wq simulado</th></tr></thead><tbody>${r.map(s=>`<tr><td>${s.scenario}</td><td>${fmt(s.arrival_rate,1)}</td><td>${fmt(s.service_rate,1)}</td><td>${percent(s.theory.rho)}</td><td>${fmt(s.theory.Lq)}</td><td>${fmt(s.simulated.avg_queue)}</td><td>${fmt(s.theory.Wq)}</td><td>${fmt(s.simulated.mean_wait)}</td></tr>`).join('')}</tbody></table><p class="footnote">Los valores simulados varían con la duración y la semilla. El escenario próximo a saturación requiere horizontes mayores para converger.</p>`}catch(err){$('comparisonResults').textContent=err.message}finally{b.disabled=false}});
window.addEventListener('resize',()=>draw(true));
requestAnimationFrame(frame);loadSimulation();
