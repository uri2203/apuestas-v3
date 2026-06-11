HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ApuestasPro — Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#07080b;--bg2:#0d0e14;--bg3:#13151e;--bg4:#1a1d2b;--surface:rgba(255,255,255,0.03);--surface-hover:rgba(255,255,255,0.06);--border:rgba(255,255,255,0.06);--border-hover:rgba(255,255,255,0.12);--text:#e8eaf0;--text2:#8b8fa3;--text3:#535766;--accent:#6c5ce7;--accent2:#a29bfe;--green:#00cec9;--green-bg:rgba(0,206,201,0.08);--red:#ff7675;--red-bg:rgba(255,118,117,0.08);--gold:#fdcb6e;--gold-bg:rgba(253,203,110,0.08);--purple:#6c5ce7;--purple-bg:rgba(108,92,231,0.1);--teal:#00cec9;--radius:12px;--radius-sm:8px;--shadow:0 1px 3px rgba(0,0,0,.3),0 4px 12px rgba(0,0,0,.2)}
.light{--bg:#f0f2f5;--bg2:#ffffff;--bg3:#f8f9fb;--bg4:#eef0f4;--surface:rgba(0,0,0,0.02);--surface-hover:rgba(0,0,0,0.04);--border:rgba(0,0,0,0.08);--border-hover:rgba(0,0,0,0.15);--text:#1a1d2e;--text2:#5a5e72;--text3:#9a9eb0;--shadow:0 1px 3px rgba(0,0,0,.06),0 4px 12px rgba(0,0,0,.04)}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:'Inter',system-ui,-apple-system,sans-serif;font-size:13px;line-height:1.5;overflow:hidden;-webkit-font-smoothing:antialiased}
pre,code,.mono{font-family:'JetBrains Mono',monospace}

/* LAYOUT */
.app{display:flex;flex-direction:column;height:100vh}
.header{display:flex;align-items:center;gap:6px;padding:0 20px;height:52px;background:var(--bg2);border-bottom:1px solid var(--border);flex-shrink:0;z-index:100;position:sticky;top:0}
.header-logo{font-size:16px;font-weight:800;letter-spacing:-.4px;margin-right:20px;display:flex;align-items:center;gap:6px}
.header-logo em{color:var(--accent);font-style:normal}
.header-logo small{font-size:8px;color:var(--text3);font-weight:500;letter-spacing:1px;text-transform:uppercase;margin-left:2px}
.header-tabs{display:flex;gap:2px;flex:1}
.header-tab{padding:6px 12px;border-radius:6px;font-size:12px;font-weight:500;color:var(--text2);background:transparent;border:none;cursor:pointer;transition:.2s;white-space:nowrap;display:flex;align-items:center;gap:5px}
.header-tab:hover{background:var(--surface-hover);color:var(--text)}
.header-tab.active{background:var(--purple-bg);color:var(--accent2);font-weight:600}
.header-actions{display:flex;align-items:center;gap:6px;margin-left:auto}
.header-btn{width:30px;height:30px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:14px;transition:.2s}
.header-btn:hover{background:var(--bg3);color:var(--text);border-color:var(--border-hover)}
.status-dot{width:6px;height:6px;border-radius:50%;display:inline-block}
.status-dot.on{background:var(--green);box-shadow:0 0 6px var(--green)}.status-dot.off{background:var(--red);box-shadow:0 0 6px var(--red)}

.content{flex:1;overflow-y:auto;padding:20px 24px}
.panel{display:none;animation:fadeUp .35s ease}.panel.active{display:block}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
.section-title{font-size:18px;font-weight:700;letter-spacing:-.3px;margin-bottom:16px;display:flex;align-items:center;gap:10px}
.section-title small{font-size:11px;color:var(--text2);font-weight:400;letter-spacing:0}

/* GRID */
.row{margin-bottom:16px}.row:last-child{margin-bottom:0}
.grid{display:grid;gap:12px}.grid-4{grid-template-columns:repeat(4,1fr)}.grid-3{grid-template-columns:repeat(3,1fr)}.grid-2{grid-template-columns:1fr 1fr}
@media(max-width:900px){.grid-4{grid-template-columns:repeat(2,1fr)}.grid-3{grid-template-columns:1fr 1fr}}
@media(max-width:600px){.grid-4,.grid-3,.grid-2{grid-template-columns:1fr}}

/* CARDS */
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;transition:.2s}
.card:hover{border-color:var(--border-hover)}
.card-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.card-title{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.8px;color:var(--text3)}
.card-value{font-size:24px;font-weight:700;letter-spacing:-.5px;line-height:1.2;font-family:'JetBrains Mono',monospace}
.card-value.up{color:var(--green)}.card-value.down{color:var(--red)}.card-value.neutral{color:var(--gold)}
.card-sub{font-size:11px;color:var(--text2);margin-top:2px}
.card-chart{height:100px;margin-top:8px;position:relative}

/* TABLES */
.table-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:12px}
thead th{padding:8px 10px;text-align:left;font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:.6px;color:var(--text3);border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--bg2)}
tbody td{padding:7px 10px;border-bottom:1px solid var(--border);color:var(--text)}
tbody tr:hover{background:var(--surface-hover);transition:.1s}
.tag{display:inline-block;padding:1px 7px;border-radius:4px;font-size:10px;font-weight:600}
.tag-green{background:var(--green-bg);color:var(--green)}.tag-red{background:var(--red-bg);color:var(--red)}.tag-gold{background:var(--gold-bg);color:var(--gold)}.tag-purple{background:var(--purple-bg);color:var(--accent2)}

/* FORMS */
input,select{background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius-sm);padding:7px 10px;color:var(--text);font-size:12px;font-family:inherit;outline:none;transition:.2s}
input:focus,select:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--purple-bg)}
.btn{display:inline-flex;align-items:center;gap:5px;padding:7px 14px;border-radius:var(--radius-sm);font-size:11px;font-weight:600;border:none;cursor:pointer;transition:.2s;font-family:inherit;white-space:nowrap}
.btn-primary{background:var(--accent);color:#fff}.btn-primary:hover{background:var(--accent2);transform:translateY(-1px)}
.btn-ghost{background:var(--surface);border:1px solid var(--border);color:var(--text2)}.btn-ghost:hover{background:var(--bg3);color:var(--text);border-color:var(--border-hover)}
.btn-sm{padding:5px 10px;font-size:10px}
.btn-icon{width:30px;height:30px;padding:0;justify-content:center;border-radius:6px}
.flex{display:flex;align-items:center;gap:8px;flex-wrap:wrap}

/* TOAST */
.toast-container{position:fixed;top:60px;right:16px;z-index:9999;display:flex;flex-direction:column;gap:6px}
.toast{padding:10px 16px;border-radius:var(--radius-sm);font-size:12px;font-weight:500;box-shadow:var(--shadow);animation:slideIn .3s ease;max-width:340px;backdrop-filter:blur(8px)}
.toast.info{background:var(--purple-bg);border-left:3px solid var(--accent);color:var(--accent2)}
.toast.success{background:var(--green-bg);border-left:3px solid var(--green);color:var(--green)}
.toast.warn{background:var(--gold-bg);border-left:3px solid var(--gold);color:var(--gold)}
.toast.error{background:var(--red-bg);border-left:3px solid var(--red);color:var(--red)}
@keyframes slideIn{from{opacity:0;transform:translateX(24px)}to{opacity:1;transform:translateX(0)}}

/* BADGE */
.badge{display:inline-flex;align-items:center;justify-content:center;min-width:18px;height:18px;padding:0 5px;border-radius:9px;font-size:9px;font-weight:700;background:var(--red);color:#fff}

/* FEATURE BAR */
.feat-bar{display:flex;align-items:center;gap:8px;padding:3px 0;font-size:11px}
.feat-bar-track{flex:1;height:5px;background:var(--bg3);border-radius:3px;overflow:hidden}
.feat-bar-fill{height:100%;border-radius:3px;background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width .6s ease}

/* SCROLLBAR */
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--bg4);border-radius:2px}
</style>
</head>
<body>
<div class="app" id="app">
  <header class="header">
    <div class="header-logo">Apuestas<em>Pro</em> <small>v2</small></div>
    <nav class="header-tabs" id="tabs">
      <button class="header-tab active" data-tab="overview">📊 Resumen</button>
      <button class="header-tab" data-tab="simulacion">🎮 Simulación</button>
      <button class="header-tab" data-tab="portfolio">📁 Portfolio</button>
      <button class="header-tab" data-tab="bookmakers">🏷️ Casas</button>
      <button class="header-tab" data-tab="cross">🔄 Cross</button>
      <button class="header-tab" data-tab="contabilidad">💰 Contabilidad</button>
      <button class="header-tab" data-tab="journal">📓 Journal</button>
      <button class="header-tab" data-tab="mlav">🧠 ML</button>
      <button class="header-tab" data-tab="config">⚙️</button>
    </nav>
    <div class="header-actions">
      <span style="font-size:10px;color:var(--text3);font-family:'JetBrains Mono',monospace" id="clock"></span>
      <span class="status-dot on" id="statusDot"></span>
      <button class="header-btn" onclick="toggleSSE()" id="sseBtn" title="SSE">📡</button>
      <button class="header-btn" onclick="toggleTheme()" id="themeBtn">🌙</button>
    </div>
  </header>

  <main class="content" id="mainContent">

    <!-- OVERVIEW -->
    <div class="panel active" id="panel-overview">
      <div class="section-title">📊 Resumen <small>Visión general del sistema</small></div>
      <div class="grid grid-4 row" id="kpi-grid"></div>
      <div class="grid grid-2 row">
        <div class="card"><div class="card-header"><span class="card-title">Bankroll History</span></div><div class="card-chart"><canvas id="bankrollChart"></canvas></div></div>
        <div class="card"><div class="card-header"><span class="card-title">P&L por Estrategia</span></div><div class="card-chart"><canvas id="pnlChart"></canvas></div></div>
      </div>
      <div class="grid grid-3 row">
        <div class="card"><div class="card-header"><span class="card-title">⚡ Value Bets</span></div><div id="vb-list" style="font-size:12px"><span style="color:var(--text2)">Cargando...</span></div></div>
        <div class="card"><div class="card-header"><span class="card-title">🔴 Sharp Money</span></div><div id="sharp-list" style="font-size:12px"><span style="color:var(--text2)">Cargando...</span></div></div>
        <div class="card"><div class="card-header"><span class="card-title">🔄 Arbitraje</span></div><div id="arb-list" style="font-size:12px"><span style="color:var(--text2)">Cargando...</span></div></div>
      </div>
    </div>

    <!-- SIMULACION -->
    <div class="panel" id="panel-simulacion">
      <div class="section-title">🎮 Simulación en Vivo <small>Trading simulado con bankroll virtual</small></div>
      <div class="grid grid-4 row" id="sim-kpi"></div>
      <div class="grid grid-2 row">
        <div class="card"><div class="card-header"><span class="card-title">Trades Pendientes</span></div><div id="sim-pendientes" style="font-size:12px"><span style="color:var(--text2)">Cargando...</span></div></div>
        <div class="card"><div class="card-header"><span class="card-title">Profit Curve</span></div><div class="card-chart"><canvas id="simChart"></canvas></div></div>
      </div>
    </div>

    <!-- PORTFOLIO -->
    <div class="panel" id="panel-portfolio">
      <div class="section-title">📁 Portfolio Inteligente <small>Kelly correlacionado + risk management</small></div>
      <div class="grid grid-4 row" id="port-kpi"></div>
      <div class="row"><div class="card"><div class="card-header"><span class="card-title">Recomendaciones Activas</span></div><div id="port-rec" class="table-wrap"></div></div></div>
    </div>

    <!-- BOOKMAKERS -->
    <div class="panel" id="panel-bookmakers">
      <div class="section-title">🏷️ Rating de Casas <small>Ranking por overround, CLV, velocidad</small></div>
      <div class="row"><div class="card"><div id="bm-table" class="table-wrap"></div></div></div>
    </div>

    <!-- CROSS -->
    <div class="panel" id="panel-cross">
      <div class="section-title">🔄 Cross-Market <small>Inconsistencias H2H vs Asian Handicap</small></div>
      <div class="row"><div class="card"><div id="cross-list" class="table-wrap"></div></div></div>
    </div>

    <!-- CONTABILIDAD -->
    <div class="panel" id="panel-contabilidad">
      <div class="section-title">💰 Contabilidad <small>Control de depósitos, retiros y P&L real</small></div>
      <div class="flex" style="margin-bottom:12px;gap:8px">
        <input type="number" id="acct-monto" placeholder="Monto" style="width:100px">
        <select id="acct-tipo"><option value="deposito">Depósito</option><option value="retiro">Retiro</option><option value="ajuste">Ajuste</option></select>
        <input type="text" id="acct-desc" placeholder="Descripción" style="flex:1;min-width:120px">
        <input type="text" id="acct-est" placeholder="Estrategia" style="width:110px">
        <button class="btn btn-primary" onclick="addTransaction()">Registrar</button>
      </div>
      <div class="grid grid-3 row" id="acct-kpi"></div>
      <div class="grid grid-2 row">
        <div class="card"><div class="card-header"><span class="card-title">P&L por Estrategia</span></div><div id="acct-pnl" class="table-wrap"></div></div>
        <div class="card"><div class="card-header"><span class="card-title">Resumen Mensual</span></div><div id="acct-resumen" class="table-wrap"></div></div>
      </div>
    </div>

    <!-- JOURNAL -->
    <div class="panel" id="panel-journal">
      <div class="section-title">📓 Trading Journal <small>Registro automático de cada acción</small></div>
      <div class="flex" style="margin-bottom:12px;gap:8px">
        <button class="btn btn-ghost btn-sm" onclick="loadJournal()">↻ Refrescar</button>
        <button class="btn btn-ghost btn-sm" onclick="window.open('/api/journal/export-csv','_blank')">⬇ Exportar CSV</button>
        <button class="btn btn-primary btn-sm" onclick="autoJournal()">Auto-Log</button>
      </div>
      <div class="grid grid-4 row" id="journal-kpi"></div>
      <div class="row"><div class="card"><div id="journal-list" class="table-wrap"></div></div></div>
    </div>

    <!-- ML AVANZADO -->
    <div class="panel" id="panel-mlav">
      <div class="section-title">🧠 ML Avanzado <small>30+ features · MLP Neural Net · Gradient Boosting</small></div>
      <div class="flex" style="margin-bottom:12px;gap:8px">
        <button class="btn btn-ghost btn-sm" onclick="loadMLAv()">↻ Refrescar</button>
        <button class="btn btn-primary btn-sm" onclick="trainMLAv()">🧠 Entrenar Todo</button>
        <select id="mlav-liga" style="width:140px"><option value="liga_mx">Liga MX</option><option value="premier_league">Premier League</option><option value="la_liga">La Liga</option><option value="serie_a">Serie A</option><option value="bundesliga">Bundesliga</option><option value="ligue_1">Ligue 1</option><option value="mls">MLS</option></select>
        <button class="btn btn-primary btn-sm" onclick="predictProximosMLAv()">Predecir Próximos</button>
      </div>
      <div class="grid grid-4 row" id="mlav-kpi"></div>
      <div class="grid grid-2 row">
        <div class="card"><div class="card-header"><span class="card-title">Feature Importance (GBM)</span></div><div id="mlav-features" style="font-size:12px"></div></div>
        <div class="card"><div class="card-header"><span class="card-title">Rendimiento por Modelo</span></div><div id="mlav-perf" class="table-wrap"></div></div>
      </div>
      <div class="row"><div class="card"><div class="card-header"><span class="card-title">Próximas Predicciones</span></div><div id="mlav-preds" class="table-wrap" style="font-size:12px"></div></div></div>
    </div>

    <!-- CONFIG -->
    <div class="panel" id="panel-config">
      <div class="section-title">⚙️ Configuración <small>Estado del sistema</small></div>
      <div class="row"><div class="card"><pre id="sys-info" class="mono" style="font-size:11px;white-space:pre-wrap;line-height:1.7"></pre></div></div>
    </div>

  </main>
</div>
<div class="toast-container" id="toastArea"></div>

<script>
// ── STATE ──
let sse=null, sseOn=true, charts={}, theme='dark', audioCtx=null;

function init(){
  setInterval(clock,1000);clock();
  document.querySelectorAll('.header-tab').forEach(b=>b.onclick=e=>switchTab(e.target.dataset.tab));
  connectSSE();loadOverview();
}
function clock(){document.getElementById('clock').textContent=new Date().toLocaleTimeString('es-MX',{hour:'2-digit',minute:'2-digit',second:'2-digit'})}

// ── TABS ──
function switchTab(name){
  document.querySelectorAll('.header-tab').forEach(b=>b.classList.toggle('active',b.dataset.tab===name));
  document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('active',p.id==='panel-'+name));
  if(name==='simulacion')loadSimulacion();else if(name==='portfolio')loadPortfolio();
  else if(name==='bookmakers')loadBookmakers();else if(name==='cross')loadCrossMarket();
  else if(name==='contabilidad')loadContabilidad();else if(name==='journal')loadJournal();
  else if(name==='mlav')loadMLAv();else if(name==='config')loadConfig();
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
  sse.onmessage=e=>{try{handleSSE(JSON.parse(e.data))}catch(_){}};
  sse.onerror=()=>{document.getElementById('statusDot').className='status-dot off';setTimeout(connectSSE,3000)};
  sse.onopen=()=>{document.getElementById('statusDot').className='status-dot on'};
}
function toggleSSE(){
  sseOn=!sseOn;
  document.getElementById('sseBtn').style.opacity=sseOn?'1':'0.4';
  if(sseOn)connectSSE();else if(sse){sse.close();sse=null}
}
function handleSSE(d){
  if(d.tipo==='value_bet')showToast(`Value bet: ${d.edge_pct}% edge`,'success');
  else if(d.tipo==='sharp')showToast(`🔴 Sharp: ${d.score} score`,'warn');
  else if(d.tipo==='alarma'){showToast(`🚨 ${d.msg}`,'error');playAlert()}
}

// ── TOAST ──
function showToast(msg,type='info'){
  const el=document.createElement('div');el.className='toast '+type;el.textContent=msg;
  document.getElementById('toastArea').appendChild(el);
  setTimeout(()=>el.remove(),4000);
}
function playAlert(){
  try{if(!audioCtx)audioCtx=new(window.AudioContext||window.webkitAudioContext)();
  const o=audioCtx.createOscillator(),g=audioCtx.createGain();
  o.connect(g);g.connect(audioCtx.destination);o.frequency.value=880;o.type='sine';
  g.gain.value=0.3;o.start();o.stop(audioCtx.currentTime+0.15)}catch(_){}}

// ── API ──
async function api(url){const r=await fetch(url);return r.json()}
function destroyChart(id){if(charts[id]){charts[id].destroy();delete charts[id]}}

// ── OVERVIEW ──
async function loadOverview(){
  try{
    const[h,rend,arb,sharp]=await Promise.all([
      api('/api/health'),api('/api/dashboard/rendimiento?days=30'),
      api('/api/odds/arbitraje'),api('/api/odds/sharp?deporte=all')]);
    document.getElementById('kpi-grid').innerHTML=[
      {l:'Bankroll',v:`$${((rend.bankroll_actual||0)).toFixed(2)}`,c:(rend.bankroll_actual||0)>=0?'up':'down',s:`Sharpe: ${(rend.sharpe_ratio||0).toFixed(2)}`},
      {l:'Rendimiento',v:`${((rend.return_pct||0)).toFixed(1)}%`,c:(rend.return_pct||0)>=0?'up':'down',s:`${rend.total_apuestas||0} apuestas`},
      {l:'Win Rate',v:`${((rend.win_rate||0)*100).toFixed(1)}%`,c:'neutral',s:`${rend.ganadas||0}G / ${rend.perdidas||0}P`},
      {l:'Versión',v:h.version,c:'neutral',s:`${h.sse_clients||0} clientes SSE`},
    ].map(k=>`<div class="card"><div class="card-title">${k.l}</div><div class="card-value ${k.c}">${k.v}</div><div class="card-sub">${k.s}</div></div>`).join('');
    const hist=rend.bankroll_history||[];
    if(hist.length){
      destroyChart('bankrollChart');
      charts.bankrollChart=new Chart(document.getElementById('bankrollChart'),{type:'line',data:{labels:hist.map((_,i)=>i),datasets:[{label:'Bankroll',data:hist,borderColor:'#6c5ce7',backgroundColor:'rgba(108,92,231,0.1)',fill:true,tension:.3,pointRadius:0,borderWidth:2}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{display:false,grid:{display:false}},y:{grid:{color:'rgba(255,255,255,0.03)'},ticks:{font:{size:9}}}}}});
    }
    const ests=rend.pnl_por_estrategia||{};
    const elabels=Object.keys(ests), edata=elabels.map(l=>ests[l]?.neto||0);
    destroyChart('pnlChart');
    charts.pnlChart=new Chart(document.getElementById('pnlChart'),{type:'bar',data:{labels:elabels,datasets:[{label:'Neto',data:edata,backgroundColor:edata.map(v=>v>=0?'rgba(0,206,201,0.7)':'rgba(255,118,117,0.7)'),borderRadius:4,borderSkipped:false}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{grid:{display:false},ticks:{font:{size:9}}},y:{grid:{color:'rgba(255,255,255,0.03)'},ticks:{font:{size:9}}}}}});
    const vb=await api('/api/odds/value-bets?min_edge=2&limit=8');
    document.getElementById('vb-list').innerHTML=(vb.value_bets||[]).length?(vb.value_bets||[]).slice(0,5).map(v=>`<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border)"><span>${v.partido||'?'}</span><span class="tag tag-green">+${(v.edge_pct||0).toFixed(1)}%</span></div>`).join(''):'<span style="color:var(--text2)">Sin value bets ahora</span>';
    document.getElementById('sharp-list').innerHTML=(sharp.alertas||[]).length?(sharp.alertas||[]).slice(0,5).map(s=>`<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border)"><span>${s.partido||s.detalle||'?'}</span><span class="tag tag-red">${s.score||s.urgencia||''}</span></div>`).join(''):'<span style="color:var(--text2)">Sin sharp ahora</span>';
    document.getElementById('arb-list').innerHTML=(arb.arbitrajes||[]).length?(arb.arbitrajes||[]).slice(0,5).map(a=>`<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border)"><span>${a.partido||(a.resultados||[]).join(' vs ')}</span><span class="tag tag-purple">${(a.profit_pct||0).toFixed(2)}%</span></div>`).join(''):'<span style="color:var(--text2)">Sin arbitraje ahora</span>';
  }catch(e){showToast('Error overview','error')}
}

// ── SIMULACION ──
async function loadSimulacion(){try{const s=await api('/api/simulacion/status');
  document.getElementById('sim-kpi').innerHTML=[
    {l:'Bankroll Sim',v:`$${(s.bankroll_actual||0).toFixed(2)}`,c:'up',s:`Inicial: $${(s.bankroll_inicial||10000).toFixed(0)}`},
    {l:'Trades',v:s.total_trades||0,c:'neutral',s:`${s.ganados||0}G / ${s.perdidos||0}P`},
    {l:'ROI',v:`${((s.roi||0)).toFixed(1)}%`,c:(s.roi||0)>=0?'up':'down',s:`${s.win_rate_pct||0}% WR`},
    {l:'Profit Neto',v:`$${(s.profit_neto||0).toFixed(2)}`,c:(s.profit_neto||0)>=0?'up':'down',s:'Acumulado'},
  ].map(k=>`<div class="card"><div class="card-title">${k.l}</div><div class="card-value ${k.c}">${k.v}</div><div class="card-sub">${k.s}</div></div>`).join('');
  const pend=s.trades_pendientes||[];
  document.getElementById('sim-pendientes').innerHTML=pend.length?`<table><thead><tr><th>Partido</th><th>Cuota</th><th>Edge</th><th>Stake</th></tr></thead><tbody>${pend.slice(0,8).map(t=>`<tr><td>${t.partido||''}</td><td>${(t.cuota||0).toFixed(2)}</td><td><span class="tag tag-green">${(t.edge_pct||0).toFixed(1)}%</span></td><td>$${(t.stake_simulado||0).toFixed(2)}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin trades pendientes</span>';
  const hist=s.bankroll_history||[];
  if(hist.length>1){destroyChart('simChart');
  charts.simChart=new Chart(document.getElementById('simChart'),{type:'line',data:{labels:hist.map((_,i)=>i),datasets:[{label:'Sim Bankroll',data:hist,borderColor:'#00cec9',backgroundColor:'rgba(0,206,201,0.1)',fill:true,tension:.3,pointRadius:0,borderWidth:2}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{display:false,grid:{display:false}},y:{grid:{color:'rgba(255,255,255,0.03)'},ticks:{font:{size:9}}}}}})}
}catch(e){showToast('Error simulación','error')}}

// ── PORTFOLIO ──
async function loadPortfolio(){try{const p=await api('/api/portfolio/recomendar?dias=30');
  document.getElementById('port-kpi').innerHTML=[
    {l:'Bankroll',v:`$${(p.bankroll_actual||0).toFixed(2)}`,c:'up',s:`Stake: ${((p.max_stake_pct||0)*100).toFixed(1)}%`},
    {l:'Apuestas Activas',v:p.apuestas_activas||0,c:'neutral',s:`Exp: $${(p.exposicion_total||0).toFixed(2)}`},
    {l:'Kelly Recomendado',v:`${((p.kelly_recomendado||0)*100).toFixed(1)}%`,c:'neutral',s:'Fracción'},
    {l:'Sharpe',v:(p.sharpe_ratio||0).toFixed(2),c:(p.sharpe_ratio||0)>=1?'up':'neutral',s:'30d'},
  ].map(k=>`<div class="card"><div class="card-title">${k.l}</div><div class="card-value ${k.c}">${k.v}</div><div class="card-sub">${k.s}</div></div>`).join('');
  const recs=p.recomendaciones||[];
  document.getElementById('port-rec').innerHTML=recs.length?`<table><thead><tr><th>Partido</th><th>Mercado</th><th>Selección</th><th>Cuota</th><th>Edge</th><th>Kelly</th><th>Stake</th></tr></thead><tbody>${recs.slice(0,12).map(r=>`<tr><td>${r.partido||''}</td><td>${r.mercado||'H2H'}</td><td>${r.seleccion||''}</td><td>${(r.cuota||0).toFixed(2)}</td><td><span class="tag tag-green">${(r.edge_pct||0).toFixed(1)}%</span></td><td>${((r.kelly_pct||0)).toFixed(1)}%</td><td><strong>$${(r.stake||0).toFixed(2)}</strong></td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin recomendaciones activas</span>';
}catch(e){showToast('Error portfolio','error')}}

// ── BOOKMAKERS ──
async function loadBookmakers(){try{const bm=await api('/api/bookmakers/rating');const rows=bm.ranking||[];
  document.getElementById('bm-table').innerHTML=rows.length?`<table><thead><tr><th>#</th><th>Casa</th><th>Overround</th><th>Cuota Prom</th><th>CLV</th><th>Score</th></tr></thead><tbody>${rows.map((r,i)=>`<tr><td>${i+1}</td><td><strong>${r.bookmaker||''}</strong></td><td><span class="tag ${(r.avg_overround||5)<5?'tag-green':'tag-gold'}">${(r.avg_overround||0).toFixed(2)}%</span></td><td>${(r.avg_cuota||0).toFixed(3)}</td><td>${(r.avg_clv||0).toFixed(2)}</td><td style="font-weight:700;color:${i<3?'var(--green)':'var(--text2)'}">${(r.score||0).toFixed(1)}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin datos de bookmakers</span>';
}catch(e){showToast('Error bookmakers','error')}}

// ── CROSS ──
async function loadCrossMarket(){try{const cm=await api('/api/odds/cross-market');const opps=cm.opportunities||[];
  document.getElementById('cross-list').innerHTML=opps.length?`<table><thead><tr><th>Partido</th><th>Mercados</th><th>Diferencia</th><th>Acción</th></tr></thead><tbody>${opps.slice(0,15).map(o=>`<tr><td>${o.partido||''}</td><td>${(o.mercados||[]).join(' vs ')}</td><td><span class="tag ${(o.diferencia||0)>5?'tag-green':'tag-gold'}">${(o.diferencia||0).toFixed(2)}%</span></td><td>${o.accion||'—'}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin oportunidades cross-market</span>';
}catch(e){showToast('Error cross-market','error')}}

// ── CONTABILIDAD ──
async function loadContabilidad(){try{const[resumen,pnl]=await Promise.all([api('/api/contabilidad/resumen-mensual'),api('/api/contabilidad/pnl-estrategia?dias=30')]);
  document.getElementById('acct-kpi').innerHTML=[
    {l:'Balance Mes',v:`$${(resumen.balance||0).toFixed(2)}`,c:(resumen.balance||0)>=0?'up':'down',s:`${resumen.total_transacciones||0} transacciones`},
    {l:'Ingresos',v:`$${(resumen.ingresos||0).toFixed(2)}`,c:'up',s:''},{l:'Egresos',v:`$${(resumen.egresos||0).toFixed(2)}`,c:'down',s:''},
  ].map(k=>`<div class="card"><div class="card-title">${k.l}</div><div class="card-value ${k.c}">${k.v}</div><div class="card-sub">${k.s}</div></div>`).join('');
  const ests=resumen.por_estrategia||{};
  document.getElementById('acct-pnl').innerHTML=Object.keys(ests).length?`<table><thead><tr><th>Estrategia</th><th>Ingresos</th><th>Egresos</th><th>Neto</th><th>Ops</th></tr></thead><tbody>${Object.entries(ests).map(([k,v])=>`<tr><td><strong>${k}</strong></td><td style="color:var(--green)">$${(v.ingresos||0).toFixed(2)}</td><td style="color:var(--red)">$${(v.egresos||0).toFixed(2)}</td><td style="font-weight:700;color:${(v.neto||0)>=0?'var(--green)':'var(--red)'}">$${(v.neto||0).toFixed(2)}</td><td>${v.n_operaciones||0}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin datos</span>';
  document.getElementById('acct-resumen').innerHTML=(pnl||[]).length?`<table><thead><tr><th>Estrategia</th><th>Ganadas</th><th>Perdidas</th><th>Neto</th></tr></thead><tbody>${(pnl||[]).slice(0,8).map(r=>`<tr><td>${r.estrategia||'N/A'}</td><td><span class="tag tag-green">${r.ganadas||0}</span></td><td><span class="tag tag-red">${r.perdidas||0}</span></td><td style="font-weight:700;color:${(r.neto||0)>=0?'var(--green)':'var(--red)'}">$${(r.neto||0).toFixed(2)}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin P&L</span>';
}catch(e){showToast('Error contabilidad','error')}}
async function addTransaction(){
  const m=parseFloat(document.getElementById('acct-monto').value),t=document.getElementById('acct-tipo').value,d=document.getElementById('acct-desc').value,e=document.getElementById('acct-est').value;
  if(!m||m===0){showToast('Ingresa un monto válido','warn');return}
  try{const r=await fetch('/api/contabilidad/transaccion',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tipo:t,monto:m,descripcion:d,estrategia:e})});const j=await r.json();
  if(j.ok){showToast('Transacción registrada','success');loadContabilidad();document.getElementById('acct-monto').value=''}else showToast('Error: '+j.error,'error');
}catch(e){showToast('Error de red','error')}}

// ── JOURNAL ──
async function loadJournal(){try{const j=await api('/api/journal/resumen?dias=7');
  document.getElementById('journal-kpi').innerHTML=[
    {l:'Total Acciones',v:j.total_acciones||0,c:'neutral',s:`${j.dias||7}d`},{l:'Value Bets',v:(j.por_tipo||{}).value_bet_detected||0,c:'up',s:''},
    {l:'Apuestas Real',v:(j.por_tipo||{}).apuesta_real||0,c:'neutral',s:''},{l:'Sharp Alerts',v:(j.por_tipo||{}).sharp_alert||0,c:'warn',s:''},
  ].map(k=>`<div class="card"><div class="card-title">${k.l}</div><div class="card-value ${k.c}">${k.v}</div><div class="card-sub">${k.s}</div></div>`).join('');
  const ult=j.ultimas_acciones||[];
  document.getElementById('journal-list').innerHTML=ult.length?`<table><thead><tr><th>Fecha</th><th>Tipo</th><th>Partido</th><th>Estrategia</th><th>Resultado</th><th>P&L</th></tr></thead><tbody>${ult.map(r=>`<tr><td style="font-size:11px;color:var(--text3)">${(r.fecha||'').slice(0,19)}</td><td>${r.tipo||''}</td><td>${r.partido||''}</td><td>${r.estrategia||''}</td><td><span class="tag ${r.resultado==='ganada'?'tag-green':r.resultado==='perdida'?'tag-red':'tag-gold'}">${r.resultado||'—'}</span></td><td style="font-weight:700;color:${(r.pnl||0)>=0?'var(--green)':'var(--red)'}">$${(r.pnl||0).toFixed(2)}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin actividad reciente</span>';
}catch(e){showToast('Error journal','error')}}
async function autoJournal(){try{const r=await api('/api/journal/auto-log');showToast(`${r.registrados||0} entries registradas`,'success');loadJournal()}catch(e){showToast('Error auto-log','error')}}

// ── ML AVANZADO ──
async function loadMLAv(){try{const[feat,perf]=await Promise.all([api('/api/ml/v2/features?liga=liga_mx'),api('/api/ml/v2/performance?liga=liga_mx')]);const items=feat.features||[],rend=perf.rendimiento||[],last=rend[rend.length-1]||{},maxImp=Math.max(...items.map(i=>i.importance||0),0.01),top=items.slice(0,3);
  document.getElementById('mlav-kpi').innerHTML=[
    {l:'Features',v:items.length||0,c:'neutral',s:'20+ ingeniería'},{l:'Top Feature',v:top[0]?.feature_name||'N/A',c:'neutral',s:`${top[0]?((top[0].importance||0)*100).toFixed(1):''}%`},
    {l:'Accuracy MLP',v:last.accuracy?`${(last.accuracy*100).toFixed(1)}%`:'N/A',c:'neutral',s:'Neural Net'},{l:'Log Loss GBM',v:last.log_loss?last.log_loss.toFixed(4):'N/A',c:'neutral',s:'Gradient Boosting'},
  ].map(k=>`<div class="card"><div class="card-title">${k.l}</div><div class="card-value ${k.c}">${k.v}</div><div class="card-sub">${k.s}</div></div>`).join('');
  document.getElementById('mlav-features').innerHTML=items.length?items.map((f,i)=>`<div class="feat-bar"><span style="width:16px;color:var(--text3);font-size:10px">${i+1}</span><div class="feat-bar-track"><div class="feat-bar-fill" style="width:${(f.importance||0)/maxImp*100}%"></div></div><span style="width:130px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${f.feature_name||''}</span><span style="width:40px;text-align:right;color:var(--text2);font-family:'JetBrains Mono',monospace">${((f.importance||0)*100).toFixed(1)}%</span></div>`).join(''):'<span style="color:var(--text2)">Entrena modelos primero</span>';
  document.getElementById('mlav-perf').innerHTML=rend.length?`<table><thead><tr><th>Fecha</th><th>Modelo</th><th>Accuracy</th><th>Log Loss</th><th>Muestras</th></tr></thead><tbody>${rend.slice(-10).reverse().map(r=>`<tr><td style="font-size:11px;color:var(--text3)">${(r.created_at||'').slice(0,10)}</td><td>${r.modelo||''}</td><td><span class="tag tag-green">${r.accuracy?((r.accuracy)*100).toFixed(1)+'%':'-'}</span></td><td>${r.log_loss?r.log_loss.toFixed(4):'-'}</td><td>${r.n_muestras||''}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin datos de rendimiento</span>';
}catch(e){showToast('Error ML Avanzado','error')}}
async function trainMLAv(){showToast('Entrenando modelos avanzados...','info');try{const r=await api('/api/ml/v2/train');showToast(`Entrenado: ${r.ligas_entrenadas||0} ligas`,'success');loadMLAv()}catch(e){showToast('Error entrenamiento','error')}}
async function predictProximosMLAv(){const liga=document.getElementById('mlav-liga').value;showToast(`Prediciendo ${liga}...`,'info');
  try{const r=await api(`/api/ml/v2/predict-proximos?liga=${liga}&dias=7`);const preds=r.predicciones||[];
  document.getElementById('mlav-preds').innerHTML=preds.length?`<table><thead><tr><th>Partido</th><th>1</th><th>X</th><th>2</th><th>Pronóstico</th><th>Confianza</th></tr></thead><tbody>${preds.map(p=>{const pick=p.pronostico||'';return `<tr><td><strong>${p.home||''}</strong> vs <strong>${p.away||''}</strong></td><td>${((p.prob_local||0)*100).toFixed(0)}%</td><td>${((p.prob_empate||0)*100).toFixed(0)}%</td><td>${((p.prob_visitante||0)*100).toFixed(0)}%</td><td><span class="tag ${pick==='1'?'tag-green':pick==='2'?'tag-red':'tag-gold'}">${pick}</span></td><td><strong>${p.confianza_pct||0}%</strong></td></tr>`}).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin próximos partidos</span>';
  showToast(`${preds.length} predicciones`,'success')}catch(e){showToast('Error predicción','error')}}

// ── CONFIG ──
async function loadConfig(){try{const h=await api('/api/health');document.getElementById('sys-info').textContent=JSON.stringify(h,null,2)}catch(e){document.getElementById('sys-info').textContent='Error loading system info'}}

// ── NOTIFICATION PERMISSION ──
if("Notification"in window&&Notification.permission==='default')Notification.requestPermission();

// ── INIT ──
init();
</script>
</body>
</html>"""
