HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ApuestasPro v2 — Dashboard Profesional</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#0a0a10;--bg2:#12121c;--bg3:#1a1a28;--bg4:#222236;--card:rgba(255,255,255,0.03);--border:rgba(255,255,255,0.06);--text:#e8e8f2;--muted:#5a5a7a;--purple:#7c6dfa;--teal:#2dd4bf;--gold:#f0b429;--green:#34d399;--red:#f87171;--mono:'DM Mono',monospace;--ui:'Inter',system-ui,sans-serif;--radius:10px}
.light{--bg:#f4f4f9;--bg2:#ffffff;--bg3:#eeeeee;--bg4:#dddddd;--card:rgba(0,0,0,0.02);--border:rgba(0,0,0,0.08);--text:#1a1a2e;--muted:#666680}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:var(--ui);overflow:hidden}
.shell{display:grid;grid-template-columns:200px 1fr;grid-template-rows:48px 1fr 32px;height:100vh}
.topbar{grid-column:1/-1;display:flex;align-items:center;justify-content:space-between;padding:0 16px;border-bottom:1px solid var(--border);background:var(--bg2);z-index:10}
.logo{font-size:16px;font-weight:800;letter-spacing:-.3px}
.logo em{color:var(--purple);font-style:normal}
.logo small{font-size:9px;font-family:var(--mono);color:var(--muted);margin-left:6px;font-weight:400}
.top-controls{display:flex;gap:8px;align-items:center}
.toggle-btn,.theme-btn{background:var(--bg3);border:1px solid var(--border);color:var(--muted);padding:4px 10px;border-radius:6px;cursor:pointer;font-size:11px;font-family:var(--mono);transition:.2s}
.toggle-btn:hover,.theme-btn:hover{background:var(--bg4);color:var(--text)}
.sidebar{background:var(--bg2);border-right:1px solid var(--border);padding:8px;display:flex;flex-direction:column;gap:4px;overflow-y:auto}
.sidebar button{background:transparent;border:none;color:var(--muted);padding:8px 12px;border-radius:6px;cursor:pointer;font-size:12px;text-align:left;transition:.2s;font-family:var(--ui);display:flex;align-items:center;gap:6px}
.sidebar button:hover{background:var(--bg3);color:var(--text)}
.sidebar button.active{background:var(--purple);color:#fff;font-weight:600}
.main{overflow-y:auto;padding:16px;background:var(--bg)}
.statusbar{grid-column:1/-1;border-top:1px solid var(--border);background:var(--bg2);display:flex;align-items:center;justify-content:space-between;padding:0 12px;font-size:10px;font-family:var(--mono);color:var(--muted)}
.statusbar .dot{width:6px;height:6px;border-radius:50%;display:inline-block;margin-right:4px}
.dot.green{background:var(--green)}.dot.red{background:var(--red)}.dot.yellow{background:var(--gold)}
.panel{display:none;animation:fadeIn .3s}.panel.active{display:block}
@keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:12px}
.grid-4{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:14px;backdrop-filter:blur(4px);cursor:grab;transition:.2s;position:relative}
.card:active{cursor:grabbing}
.card h3{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px;font-weight:600}
.card .val{font-size:22px;font-weight:700;font-family:var(--mono)}.card .val.up{color:var(--green)}.card .val.down{color:var(--red)}.card .val.neutral{color:var(--gold)}
.card .sub{font-size:10px;color:var(--muted);margin-top:2px}
.card .chart-wrap{height:120px;margin-top:8px}
.card table{width:100%;font-size:11px;font-family:var(--mono);border-collapse:collapse}
.card table td{padding:4px 6px;border-bottom:1px solid var(--border)}
.card table th{text-align:left;padding:4px 6px;color:var(--muted);font-size:9px;text-transform:uppercase;letter-spacing:.5px;border-bottom:1px solid var(--border)}
.card table tr:hover{background:var(--bg3)}
input,select{background:var(--bg3);border:1px solid var(--border);color:var(--text);padding:6px 10px;border-radius:6px;font-size:12px;font-family:var(--mono);width:100%}
button.action{background:var(--purple);border:none;color:#fff;padding:6px 14px;border-radius:6px;cursor:pointer;font-size:11px;font-weight:600;transition:.2s;font-family:var(--ui)}
button.action:hover{opacity:.85}
button.action.sm{padding:4px 10px;font-size:10px}
.refresh-btn{background:var(--bg3);border:1px solid var(--border);color:var(--muted);width:28px;height:28px;border-radius:6px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:14px;transition:.2s}
.refresh-btn:hover{background:var(--bg4);color:var(--text)}
.flex{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.toast{position:fixed;top:56px;right:16px;background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);padding:10px 16px;font-size:12px;font-family:var(--mono);z-index:999;animation:slideIn .3s;max-width:320px;box-shadow:0 8px 24px rgba(0,0,0,.4)}
.toast.info{border-left:3px solid var(--purple)}.toast.success{border-left:3px solid var(--green)}.toast.warn{border-left:3px solid var(--gold)}.toast.error{border-left:3px solid var(--red)}
@keyframes slideIn{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:translateX(0)}}
@media(max-width:768px){.shell{grid-template-columns:1fr}.sidebar{display:none}.grid-2,.grid-3{grid-template-columns:1fr}}
.notif-badge{position:absolute;top:-4px;right:-4px;background:var(--red);color:#fff;font-size:8px;padding:1px 4px;border-radius:8px;font-weight:700}
.controles{margin-bottom:12px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
</style>
</head>
<body onload="init()">

<div class="shell">
  <div class="topbar">
    <div class="logo">Apuestas<em>Pro</em> <small>v2</small></div>
    <div class="top-controls">
      <button class="toggle-btn" onclick="toggleSSE()" id="sseBtn">SSE: ON</button>
      <button class="theme-btn" onclick="toggleTheme()" id="themeBtn">🌙</button>
    </div>
  </div>
  <div class="sidebar" id="sidebar">
    <button class="active" data-tab="overview">📊 Resumen</button>
    <button data-tab="simulacion">🎮 Simulación</button>
    <button data-tab="portfolio">📁 Portfolio</button>
    <button data-tab="bookmakers">🏷️ Casas</button>
    <button data-tab="cross">🔄 Cross-Market</button>
    <button data-tab="contabilidad">💰 Contabilidad</button>
    <button data-tab="journal">📓 Journal</button>
    <button data-tab="mlav">🧠 ML Avanzado</button>
    <button data-tab="config" style="margin-top:auto;color:var(--muted)">⚙️</button>
  </div>
  <div class="main" id="main">
    <!-- OVERVIEW -->
    <div class="panel active" id="panel-overview">
      <div class="flex" style="margin-bottom:12px"><h2 style="font-size:16px;font-weight:700">Resumen del Sistema</h2><button class="refresh-btn" onclick="loadOverview()">↻</button></div>
      <div class="grid-4" id="kpi-grid"></div>
      <div class="grid-2">
        <div class="card"><h3>Bankroll History</h3><div class="chart-wrap"><canvas id="bankrollChart"></canvas></div></div>
        <div class="card"><h3>P&L por Estrategia</h3><div class="chart-wrap"><canvas id="pnlChart"></canvas></div></div>
      </div>
      <div class="grid-3">
        <div class="card" id="widget-value-bets"><h3>⚡ Value Bets Recientes</h3><div id="vb-list"><small style="color:var(--muted)">Cargando...</small></div></div>
        <div class="card" id="widget-sharp"><h3>🔴 Sharp Money</h3><div id="sharp-list"><small style="color:var(--muted)">Cargando...</small></div></div>
        <div class="card" id="widget-arbitraje"><h3>🔄 Arbitraje</h3><div id="arb-list"><small style="color:var(--muted)">Cargando...</small></div></div>
      </div>
    </div>
    <!-- SIMULACION -->
    <div class="panel" id="panel-simulacion">
      <div class="flex" style="margin-bottom:12px"><h2 style="font-size:16px;font-weight:700">Simulación en Vivo</h2><button class="refresh-btn" onclick="loadSimulacion()">↻</button></div>
      <div class="grid-4" id="sim-kpi"></div>
      <div class="grid-2">
        <div class="card"><h3>Trades Pendientes</h3><div id="sim-pendientes"><small>Cargando...</small></div></div>
        <div class="card"><h3>Profit Curve</h3><div class="chart-wrap"><canvas id="simChart"></canvas></div></div>
      </div>
    </div>
    <!-- PORTFOLIO -->
    <div class="panel" id="panel-portfolio">
      <div class="flex" style="margin-bottom:12px"><h2 style="font-size:16px;font-weight:700">Portfolio Inteligente</h2><button class="refresh-btn" onclick="loadPortfolio()">↻</button></div>
      <div class="grid-4" id="port-kpi"></div>
      <div class="card"><h3>Recomendaciones Activas</h3><div id="port-rec"></div></div>
    </div>
    <!-- BOOKMAKERS -->
    <div class="panel" id="panel-bookmakers">
      <div class="flex" style="margin-bottom:12px"><h2 style="font-size:16px;font-weight:700">Rating de Casas</h2><button class="refresh-btn" onclick="loadBookmakers()">↻</button></div>
      <div class="card"><div id="bm-table"></div></div>
    </div>
    <!-- CROSS-MARKET -->
    <div class="panel" id="panel-cross">
      <div class="flex" style="margin-bottom:12px"><h2 style="font-size:16px;font-weight:700">Cross-Market Opportunities</h2><button class="refresh-btn" onclick="loadCrossMarket()">↻</button></div>
      <div class="card"><div id="cross-list"></div></div>
    </div>
    <!-- CONTABILIDAD -->
    <div class="panel" id="panel-contabilidad">
      <div class="flex" style="margin-bottom:12px"><h2 style="font-size:16px;font-weight:700">Contabilidad</h2><button class="refresh-btn" onclick="loadContabilidad()">↻</button></div>
      <div class="controles">
        <input type="number" id="acct-monto" placeholder="Monto" style="width:100px">
        <select id="acct-tipo"><option value="deposito">Depósito</option><option value="retiro">Retiro</option><option value="ajuste">Ajuste</option></select>
        <input type="text" id="acct-desc" placeholder="Descripción" style="flex:1">
        <input type="text" id="acct-est" placeholder="Estrategia">
        <button class="action" onclick="addTransaction()">Registrar</button>
      </div>
      <div class="grid-3" id="acct-kpi"></div>
      <div class="grid-2">
        <div class="card"><h3>P&L por Estrategia</h3><div id="acct-pnl"></div></div>
        <div class="card"><h3>Resumen Mensual</h3><div id="acct-resumen"></div></div>
      </div>
    </div>
    <!-- JOURNAL -->
    <div class="panel" id="panel-journal">
      <div class="flex" style="margin-bottom:12px"><h2 style="font-size:16px;font-weight:700">Trading Journal</h2>
        <button class="refresh-btn" onclick="loadJournal()">↻</button>
        <button class="action sm" onclick="window.open('/api/journal/export-csv','_blank')">⬇ CSV</button>
        <button class="action sm" onclick="autoJournal()">Auto-Log</button>
      </div>
      <div class="grid-4" id="journal-kpi"></div>
      <div class="card"><div id="journal-list"></div></div>
    </div>
    <!-- ML AVANZADO -->
    <div class="panel" id="panel-mlav">
      <div class="flex" style="margin-bottom:12px"><h2 style="font-size:16px;font-weight:700">ML Avanzado — 30+ Features</h2>
        <button class="refresh-btn" onclick="loadMLAv()">↻</button>
        <button class="action sm" onclick="trainMLAv()">🧠 Entrenar Todo</button>
      </div>
      <div class="grid-4" id="mlav-kpi"></div>
      <div class="grid-2">
        <div class="card"><h3>🏆 Feature Importance (GBM)</h3><div id="mlav-features"></div></div>
        <div class="card"><h3>📈 Rendimiento por Modelo</h3><div id="mlav-perf"></div></div>
      </div>
      <div class="card"><h3>🎯 Próximas Predicciones</h3>
        <div class="controles">
          <select id="mlav-liga"><option value="liga_mx">Liga MX</option><option value="premier_league">Premier</option><option value="la_liga">La Liga</option><option value="serie_a">Serie A</option><option value="bundesliga">Bundesliga</option><option value="ligue_1">Ligue 1</option><option value="mls">MLS</option></select>
          <button class="action sm" onclick="predictProximosMLAv()">Predecir</button>
        </div>
        <div id="mlav-preds"><small>Cargando...</small></div>
      </div>
    </div>
    <!-- CONFIG -->
    <div class="panel" id="panel-config">
      <h2 style="font-size:16px;font-weight:700;margin-bottom:12px">Configuración</h2>
      <div class="card"><h3>Estado del Sistema</h3><pre id="sys-info" style="font-family:var(--mono);font-size:11px;white-space:pre-wrap"></pre></div>
    </div>
  </div>
  <div class="statusbar">
    <span><span class="dot green" id="statusDot"></span><span id="statusText">Conectado</span></span>
    <span id="clock"></span>
  </div>
</div>
<div id="toast-area"></div>

<script>
// ── STATE ──
let sse=null, sseOn=true, charts={}, theme='dark', audioCtx=null;

function init(){
  clock(); setInterval(clock,1000);
  document.querySelectorAll('.sidebar button[data-tab]').forEach(b=>b.onclick=e=>switchTab(e.target.dataset.tab));
  loadOverview();
  connectSSE();
}
function clock(){document.getElementById('clock').textContent=new Date().toLocaleTimeString('es-MX')}

// ── TABS ──
function switchTab(name){
  document.querySelectorAll('.sidebar button').forEach(b=>b.classList.remove('active'));
  document.querySelector(`.sidebar button[data-tab="${name}"]`).classList.add('active');
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  const el=document.getElementById('panel-'+name);
  if(el)el.classList.add('active');
  // load on switch
  if(name==='simulacion')loadSimulacion();
  else if(name==='portfolio')loadPortfolio();
  else if(name==='bookmakers')loadBookmakers();
  else if(name==='cross')loadCrossMarket();
  else if(name==='contabilidad')loadContabilidad();
  else if(name==='journal')loadJournal();
  else   if(name==='config')loadConfig();
  if(name==='mlav')loadMLAv();
}

// ── THEME ──
function toggleTheme(){
  theme=theme==='dark'?'light':'dark';
  document.documentElement.classList.toggle('light',theme==='light');
  document.getElementById('themeBtn').textContent=theme==='dark'?'🌙':'☀️';
}

// ── SSE ──
function connectSSE(){
  if(!sseOn)return;
  sse=new EventSource('/api/eventos');
  sse.onmessage=e=>{
    try{
      const d=JSON.parse(e.data);
      handleSSE(d);
    }catch(_){}
  };
  sse.onerror=()=>{
    document.getElementById('statusDot').className='dot red';
    document.getElementById('statusText').textContent='Reconectando...';
    setTimeout(connectSSE,3000);
  };
  sse.onopen=()=>{
    document.getElementById('statusDot').className='dot green';
    document.getElementById('statusText').textContent='Conectado';
  };
}
function toggleSSE(){
  sseOn=!sseOn;
  document.getElementById('sseBtn').textContent=sseOn?'SSE: ON':'SSE: OFF';
  if(sseOn)connectSSE();
  else if(sse){sse.close();sse=null}
}
function handleSSE(d){
  if(d.tipo==='value_bet')showToast(`Value bet: ${d.edge_pct}% edge`,d.edge_pct>10?'success':'info');
  else if(d.tipo==='sharp')showToast(`🔴 Sharp: ${d.score} score`,d.score>8?'warn':'info');
  else if(d.tipo==='alarma'){showToast(`🚨 ${d.msg}`,'error');playAlert()}
}

// ── TOAST ──
function showToast(msg,type='info'){
  const el=document.createElement('div');
  el.className='toast '+type;
  el.textContent=msg;
  document.getElementById('toast-area').appendChild(el);
  setTimeout(()=>el.remove(),4000);
}

// ── SOUND ──
function playAlert(){
  try{
    if(!audioCtx)audioCtx=new (window.AudioContext||window.webkitAudioContext)();
    const o=audioCtx.createOscillator(),g=audioCtx.createGain();
    o.connect(g);g.connect(audioCtx.destination);
    o.frequency.value=880;o.type='sine';
    g.gain.value=0.3;
    o.start();o.stop(audioCtx.currentTime+0.15);
  }catch(_){}
}

// ── NOTIFICATION ──
function sendNotification(title,body){
  if(!("Notification"in window))return;
  if(Notification.permission==='granted')new Notification(title,{body});
  else if(Notification.permission!=='denied')Notification.requestPermission();
}

// ── FETCH HELPERS ──
async function api(url){const r=await fetch(url);return r.json()}

// ── OVERVIEW ──
async function loadOverview(){
  try{
    const [h,rend,arb,sharp,cross]=await Promise.all([
      api('/api/health'),api('/api/dashboard/rendimiento?days=30'),
      api('/api/odds/arbitraje'),api('/api/odds/sharp?deporte=all'),
      api('/api/odds/cross-market')]);
    renderKPI(h,rend);renderBankrollChart(rend);renderPnLChart(rend);
    renderVBList();renderSharpList(sharp);renderArbList(arb);
  }catch(e){showToast('Error loading overview','error')}
}
function renderKPI(h,rend){
  const kpis=[
    {l:'Bankroll',v:`$${((rend.bankroll_actual||0)).toFixed(2)}`,c:(rend.bankroll_actual||0)>=0?'up':'down',s:`Sharpe: ${(rend.sharpe_ratio||0).toFixed(2)}`},
    {l:'Rendimiento',v:`${((rend.return_pct||0)).toFixed(1)}%`,c:(rend.return_pct||0)>=0?'up':'down',s:`${rend.total_apuestas||0} apuestas`},
    {l:'Win Rate',v:`${((rend.win_rate||0)*100).toFixed(1)}%`,c:'neutral',s:`${rend.ganadas||0}G / ${rend.perdidas||0}P`},
    {l:'Versión',v:h.version||'4.3.0',c:'neutral',s:`${h.sse_clients||0} clientes SSE`},
  ];
  document.getElementById('kpi-grid').innerHTML=kpis.map(k=>`<div class="card"><h3>${k.l}</h3><div class="val ${k.c}">${k.v}</div><div class="sub">${k.s||''}</div></div>`).join('');
}
function renderBankrollChart(rend){
  const hist=rend.bankroll_history||[];
  const labels=hist.map((_,i)=>i), data=hist;
  destroyChart('bankrollChart');
  charts.bankrollChart=new Chart(document.getElementById('bankrollChart'),{type:'line',data:{labels,datasets:[{label:'Bankroll',data,borderColor:'#7c6dfa',fill:false,tension:.3,pointRadius:1}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{display:false},y:{ticks:{font:{size:9}}}}}});
}
function renderPnLChart(rend){
  destroyChart('pnlChart');
  const ests=rend.pnl_por_estrategia||{};
  const labels=Object.keys(ests), data=labels.map(l=>ests[l]?.neto||0);
  charts.pnlChart=new Chart(document.getElementById('pnlChart'),{type:'bar',data:{labels,datasets:[{label:'Neto',data,backgroundColor:data.map(v=>v>=0?'#34d399':'#f87171')}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{ticks:{font:{size:9}}}}}});
}
async function renderVBList(){
  try{
    const vb=await api('/api/odds/value-bets?min_edge=2&limit=8');
    const list=vb.value_bets||[];
    document.getElementById('vb-list').innerHTML=list.length?list.map(v=>`<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--border);font-size:11px"><span>${v.partido||'?'}</span><span style="color:var(--green)">+${(v.edge_pct||0).toFixed(1)}%</span></div>`).join(''):'<small style="color:var(--muted)">Sin value bets ahora</small>';
  }catch(_){document.getElementById('vb-list').innerHTML='<small style="color:var(--red)">Error</small>'}
}
async function renderSharpList(sharp){
  const list=sharp.alertas||[];
  document.getElementById('sharp-list').innerHTML=list.length?list.slice(0,5).map(s=>`<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--border);font-size:11px"><span>${s.partido||s.detalle||'?'}</span><span style="color:var(--red)">${s.score||s.urgencia||''}</span></div>`).join(''):'<small style="color:var(--muted)">Sin sharp ahora</small>';
}
async function renderArbList(arb){
  const list=arb.arbitrajes||[];
  document.getElementById('arb-list').innerHTML=list.length?list.slice(0,5).map(a=>`<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--border);font-size:11px"><span>${a.partido||(a.resultados||[]).join(' vs ')}</span><span style="color:var(--teal)">${(a.profit_pct||0).toFixed(2)}%</span></div>`).join(''):'<small style="color:var(--muted)">Sin arbitraje ahora</small>';
}

// ── SIMULACION ──
async function loadSimulacion(){
  try{
    const s=await api('/api/simulacion/status');
    const kpis=[
      {l:'Bankroll Sim',v:`$${(s.bankroll_actual||0).toFixed(2)}`,c:'up',s:`Inicial: $${(s.bankroll_inicial||10000).toFixed(0)}`},
      {l:'Trades Totales',v:s.total_trades||0,c:'neutral',s:`${s.ganados||0}G / ${s.perdidos||0}P`},
      {l:'ROI',v:`${((s.roi||0)).toFixed(1)}%`,c:(s.roi||0)>=0?'up':'down',s:`${s.win_rate_pct||0}% WR`},
      {l:'Profit Neto',v:`$${(s.profit_neto||0).toFixed(2)}`,c:(s.profit_neto||0)>=0?'up':'down',s:'Acumulado'},
    ];
    document.getElementById('sim-kpi').innerHTML=kpis.map(k=>`<div class="card"><h3>${k.l}</h3><div class="val ${k.c}">${k.v}</div><div class="sub">${k.s||''}</div></div>`).join('');
    const pend=s.trades_pendientes||[];
    document.getElementById('sim-pendientes').innerHTML=pend.length?`<table><tr><th>Partido</th><th>Cuota</th><th>Edge</th><th>Stake</th></tr>${pend.slice(0,10).map(t=>`<tr><td>${t.partido||''}</td><td>${(t.cuota||0).toFixed(2)}</td><td style="color:var(--green)">${(t.edge_pct||0).toFixed(1)}%</td><td>$${(t.stake_simulado||0).toFixed(2)}</td></tr>`).join('')}</table>`:'<small>Sin trades pendientes</small>';
    const hist=s.bankroll_history||[];
    if(hist.length>1){
      destroyChart('simChart');
      charts.simChart=new Chart(document.getElementById('simChart'),{type:'line',data:{labels:hist.map((_,i)=>i),datasets:[{label:'Sim Bankroll',data:hist,borderColor:'#2dd4bf',fill:false,tension:.3,pointRadius:1}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{display:false},y:{ticks:{font:{size:9}}}}}});
    }
  }catch(e){showToast('Error simulación','error')}
}

// ── PORTFOLIO ──
async function loadPortfolio(){
  try{
    const p=await api('/api/portfolio/recomendar?dias=30');
    const kpis=[
      {l:'Bankroll',v:`$${(p.bankroll_actual||0).toFixed(2)}`,c:'up',s:`Stake: ${((p.max_stake_pct||0)*100).toFixed(1)}%`},
      {l:'Apuestas Activas',v:p.apuestas_activas||0,c:'neutral',s:`Exposición: $${(p.exposicion_total||0).toFixed(2)}`},
      {l:'Kelly Recomendado',v:`${((p.kelly_recomendado||0)*100).toFixed(1)}%`,c:'neutral',s:'Fracción'},
      {l:'Score Sharpe',v:(p.sharpe_ratio||0).toFixed(2),c:(p.sharpe_ratio||0)>=1?'up':'neutral',s:'Últimos 30d'},
    ];
    document.getElementById('port-kpi').innerHTML=kpis.map(k=>`<div class="card"><h3>${k.l}</h3><div class="val ${k.c}">${k.v}</div><div class="sub">${k.s||''}</div></div>`).join('');
    const recs=p.recomendaciones||[];
    document.getElementById('port-rec').innerHTML=recs.length?`<table><tr><th>Partido</th><th>Mercado</th><th>Selección</th><th>Cuota</th><th>Edge</th><th>Kelly</th><th>Stake</th></tr>${recs.slice(0,15).map(r=>`<tr><td>${r.partido||''}</td><td>${r.mercado||'H2H'}</td><td>${r.seleccion||''}</td><td>${(r.cuota||0).toFixed(2)}</td><td style="color:var(--green)">${(r.edge_pct||0).toFixed(1)}%</td><td>${((r.kelly_pct||0)).toFixed(1)}%</td><td>$${(r.stake||0).toFixed(2)}</td></tr>`).join('')}</table>`:'<small>Sin recomendaciones activas</small>';
  }catch(e){showToast('Error portfolio','error')}
}

// ── BOOKMAKERS ──
async function loadBookmakers(){
  try{
    const bm=await api('/api/bookmakers/rating');
    const rows=bm.ranking||[];
    document.getElementById('bm-table').innerHTML=rows.length?`<table><tr><th>#</th><th>Casa</th><th>Overround</th><th>Cuota Prom</th><th>CLV</th><th>Score</th></tr>${rows.map((r,i)=>`<tr><td>${i+1}</td><td><strong>${r.bookmaker||''}</strong></td><td style="color:${(r.avg_overround||5)<5?'var(--green)':'var(--gold)'}">${(r.avg_overround||0).toFixed(2)}%</td><td>${(r.avg_cuota||0).toFixed(3)}</td><td>${(r.avg_clv||0).toFixed(2)}</td><td style="font-weight:700;color:${i<3?'var(--green)':'var(--muted)'}">${(r.score||0).toFixed(1)}</td></tr>`).join('')}</table>`:'<small>Sin datos de bookmakers</small>';
  }catch(e){showToast('Error bookmakers','error')}
}

// ── CROSS-MARKET ──
async function loadCrossMarket(){
  try{
    const cm=await api('/api/odds/cross-market');
    const opps=cm.opportunities||[];
    document.getElementById('cross-list').innerHTML=opps.length?`<table><tr><th>Partido</th><th>Mercados</th><th>Diferencia</th><th>Potencial</th></tr>${opps.slice(0,20).map(o=>`<tr><td>${o.partido||''}</td><td>${(o.mercados||[]).join(' vs ')}</td><td style="color:${(o.diferencia||0)>5?'var(--green)':'var(--gold)'}">${(o.diferencia||0).toFixed(2)}%</td><td>${o.accion||'N/A'}</td></tr>`).join('')}</table>`:'<small>Sin oportunidades cross-market</small>';
  }catch(e){showToast('Error cross-market','error')}
}

// ── CONTABILIDAD ──
async function loadContabilidad(){
  try{
    const [resumen,pnl,sync]=await Promise.all([
      api('/api/contabilidad/resumen-mensual'),
      api('/api/contabilidad/pnl-estrategia?dias=30'),
      api('/api/contabilidad/sync')]);
    document.getElementById('acct-kpi').innerHTML=[
      {l:'Balance Mes',v:`$${(resumen.balance||0).toFixed(2)}`,c:(resumen.balance||0)>=0?'up':'down',s:`${resumen.total_transacciones||0} transacciones`},
      {l:'Ingresos',v:`$${(resumen.ingresos||0).toFixed(2)}`,c:'up',s:''},
      {l:'Egresos',v:`$${(resumen.egresos||0).toFixed(2)}`,c:'down',s:''},
    ].map(k=>`<div class="card"><h3>${k.l}</h3><div class="val ${k.c}">${k.v}</div><div class="sub">${k.s||''}</div></div>`).join('');
    const ests=resumen.por_estrategia||{};
    document.getElementById('acct-pnl').innerHTML=Object.keys(ests).length?`<table><tr><th>Estrategia</th><th>Ingresos</th><th>Egresos</th><th>Neto</th><th>Ops</th></tr>${Object.entries(ests).map(([k,v])=>`<tr><td>${k}</td><td style="color:var(--green)">$${(v.ingresos||0).toFixed(2)}</td><td style="color:var(--red)">$${(v.egresos||0).toFixed(2)}</td><td style="font-weight:700;color:${(v.neto||0)>=0?'var(--green)':'var(--red)'}">$${(v.neto||0).toFixed(2)}</td><td>${v.n_operaciones||0}</td></tr>`).join('')}</table>`:'<small>Sin datos</small>';
    const pnlData=pnl||[];
    document.getElementById('acct-resumen').innerHTML=pnlData.length?`<table><tr><th>Estrategia</th><th>Ganadas</th><th>Perdidas</th><th>Neto</th></tr>${pnlData.slice(0,10).map(r=>`<tr><td>${r.estrategia||'N/A'}</td><td style="color:var(--green)">${r.ganadas||0}</td><td style="color:var(--red)">${r.perdidas||0}</td><td style="font-weight:700;color:${(r.neto||0)>=0?'var(--green)':'var(--red)'}">$${(r.neto||0).toFixed(2)}</td></tr>`).join('')}</table>`:'<small>Sin P&L</small>';
  }catch(e){showToast('Error contabilidad','error')}
}
async function addTransaction(){
  const monto=parseFloat(document.getElementById('acct-monto').value);
  const tipo=document.getElementById('acct-tipo').value;
  const desc=document.getElementById('acct-desc').value;
  const est=document.getElementById('acct-est').value;
  if(!monto||monto===0){showToast('Ingresa un monto válido','warn');return}
  try{
    const r=await fetch('/api/contabilidad/transaccion',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tipo,monto,descripcion:desc,estrategia:est})});
    const j=await r.json();
    if(j.ok){showToast('Transacción registrada','success');loadContabilidad();document.getElementById('acct-monto').value=''}
    else showToast('Error: '+j.error,'error');
  }catch(e){showToast('Error de red','error')}
}

// ── JOURNAL ──
async function loadJournal(){
  try{
    const j=await api('/api/journal/resumen?dias=7');
    document.getElementById('journal-kpi').innerHTML=[
      {l:'Total Acciones',v:j.total_acciones||0,c:'neutral',s:`Últimos ${j.dias||7}d`},
      {l:'Value Bets',v:(j.por_tipo||{}).value_bet_detected||0,c:'up',s:''},
      {l:'Apuestas Real',v:(j.por_tipo||{}).apuesta_real||0,c:'neutral',s:''},
      {l:'Sharp Alerts',v:(j.por_tipo||{}).sharp_alert||0,c:'warn',s:''},
    ].map(k=>`<div class="card"><h3>${k.l}</h3><div class="val ${k.c}">${k.v}</div><div class="sub">${k.s||''}</div></div>`).join('');
    const ult=j.ultimas_acciones||[];
    document.getElementById('journal-list').innerHTML=ult.length?`<table><tr><th>Fecha</th><th>Tipo</th><th>Partido</th><th>Estrategia</th><th>Resultado</th><th>P&L</th></tr>${ult.map(r=>`<tr><td style="font-size:10px;color:var(--muted)">${(r.fecha||'').slice(0,19)}</td><td>${r.tipo||''}</td><td>${r.partido||''}</td><td>${r.estrategia||''}</td><td style="color:${r.resultado==='ganada'?'var(--green)':r.resultado==='perdida'?'var(--red)':'var(--gold)'}">${r.resultado||''}</td><td style="font-weight:700;color:${(r.pnl||0)>=0?'var(--green)':'var(--red)'}">$${(r.pnl||0).toFixed(2)}</td></tr>`).join('')}</table>`:'<small>Sin actividad reciente</small>';
  }catch(e){showToast('Error journal','error')}
}
async function autoJournal(){
  try{
    const r=await api('/api/journal/auto-log');
    showToast(`${r.registrados||0} entries registradas`,'success');
    loadJournal();
  }catch(e){showToast('Error auto-log','error')}
}

// ── CONFIG ──
async function loadConfig(){
  try{
    const h=await api('/api/health');
    document.getElementById('sys-info').textContent=JSON.stringify(h,null,2);
  }catch(e){document.getElementById('sys-info').textContent='Error loading system info'}
}

// ── CHART HELPERS ──
function destroyChart(id){
  if(charts[id]){charts[id].destroy();delete charts[id]}
}

// ── ML AVANZADO ──
async function loadMLAv(){
  try{
    const [feat,perf]=await Promise.all([
      api('/api/ml/v2/features?liga=liga_mx'),
      api('/api/ml/v2/performance?liga=liga_mx')]);
    renderMLAvKPI(feat,perf);renderMLAvFeatures(feat);renderMLAvPerf(perf);
  }catch(e){showToast('Error ML Avanzado','error')}
}
function renderMLAvKPI(feat,perf){
  const top=(feat.features||[]).slice(0,3);
  const rend=(perf.rendimiento||[]);
  const last=rend[rend.length-1]||{};
  document.getElementById('mlav-kpi').innerHTML=[
    {l:'Features',v:(feat.features||[]).length||0,c:'neutral',s:'20+ ingeniería'},
    {l:'Top Feature',v:top[0]?.feature_name||'N/A',c:'neutral',s:`${top[0]?((top[0].importance||0)*100).toFixed(1):''}%`},
    {l:'Accuracy MLP',v:last.accuracy?`${(last.accuracy*100).toFixed(1)}%`:'N/A',c:'neutral',s:'Neural Net'},
    {l:'Log Loss GBM',v:last.log_loss?last.log_loss.toFixed(4):'N/A',c:'neutral',s:'Gradient Boosting'},
  ].map(k=>`<div class="card"><h3>${k.l}</h3><div class="val ${k.c}">${k.v}</div><div class="sub">${k.s||''}</div></div>`).join('');
}
function renderMLAvFeatures(feat){
  const items=feat.features||[];
  const maxImp=Math.max(...items.map(i=>i.importance||0),0.01);
  document.getElementById('mlav-features').innerHTML=items.length?
    items.map((f,i)=>`<div style="display:flex;align-items:center;gap:8px;padding:3px 0;font-size:11px"><span style="width:14px;color:var(--muted)">${i+1}</span><div style="flex:1;height:6px;background:var(--bg3);border-radius:3px"><div style="width:${(f.importance||0)/maxImp*100}%;height:6px;background:var(--purple);border-radius:3px"></div></div><span style="width:120px;white-space:nowrap;overflow:hidden">${f.feature_name||''}</span><span style="width:50px;text-align:right;color:var(--muted)">${((f.importance||0)*100).toFixed(1)}%</span></div>`).join('')
    :'<small style="color:var(--muted)">Entrena modelos primero</small>';
}
function renderMLAvPerf(perf){
  const rend=perf.rendimiento||[];
  document.getElementById('mlav-perf').innerHTML=rend.length?`<table><tr><th>Fecha</th><th>Modelo</th><th>Accuracy</th><th>Log Loss</th><th>Muestras</th></tr>${rend.slice(-10).reverse().map(r=>`<tr><td style="font-size:10px;color:var(--muted)">${(r.created_at||'').slice(0,10)}</td><td>${r.modelo||''}</td><td style="color:var(--green)">${r.accuracy?((r.accuracy)*100).toFixed(1)+'%':'-'}</td><td style="color:var(--gold)">${r.log_loss?r.log_loss.toFixed(4):'-'}</td><td>${r.n_muestras||''}</td></tr>`).join('')}</table>`:'<small>Sin datos de rendimiento</small>';
}
async function trainMLAv(){
  showToast('Entrenando modelos avanzados...','info');
  try{
    const r=await api('/api/ml/v2/train');
    showToast(`Entrenamiento completado: ${r.ligas_entrenadas||0} ligas`,'success');
    loadMLAv();
  }catch(e){showToast('Error entrenamiento','error')}
}
async function predictProximosMLAv(){
  const liga=document.getElementById('mlav-liga').value;
  showToast(`Prediciendo ${liga}...`,'info');
  try{
    const r=await api(`/api/ml/v2/predict-proximos?liga=${liga}&dias=7`);
    const preds=r.predicciones||[];
    document.getElementById('mlav-preds').innerHTML=preds.length?
      `<table><tr><th>Partido</th><th>1</th><th>X</th><th>2</th><th>Pronóstico</th><th>Conf</th></tr>${
        preds.map(p=>{
          const pick=p.pronostico||'';
          return `<tr><td>${p.home||''} vs ${p.away||''}</td>
            <td>${((p.prob_local||0)*100).toFixed(0)}%</td>
            <td>${((p.prob_empate||0)*100).toFixed(0)}%</td>
            <td>${((p.prob_visitante||0)*100).toFixed(0)}%</td>
            <td style="font-weight:700;color:${pick==='1'?'var(--green)':pick==='2'?'var(--red)':'var(--gold)'}">${pick}</td>
            <td style="color:var(--purple)">${p.confianza_pct||0}%</td></tr>`}).join('')}</table>`
      :'<small>Sin próximos partidos</small>';
    showToast(`${preds.length} predicciones generadas`,'success');
  }catch(e){showToast('Error predicción','error')}
}

// ── NOTIFICATION PERMISSION ──
if("Notification"in window&&Notification.permission==='default')Notification.requestPermission();

// ── AUTO-REFRESH ──
setInterval(()=>{const a=document.querySelector('.panel.active');if(a&&a.id==='panel-overview')loadOverview()},30000);
</script>
</body>
</html>"""
