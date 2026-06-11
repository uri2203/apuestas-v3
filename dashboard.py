HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ApuestasPro — Sistema Profesional</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#07080b;--bg2:#0d0e14;--bg3:#13151e;--bg4:#1a1d2b;--surface:rgba(255,255,255,0.03);--surface-hover:rgba(255,255,255,0.06);--border:rgba(255,255,255,0.06);--border-hover:rgba(255,255,255,0.12);--text:#e8eaf0;--text2:#8b8fa3;--text3:#535766;--accent:#6c5ce7;--accent2:#a29bfe;--green:#00cec9;--green-bg:rgba(0,206,201,0.1);--red:#ff7675;--red-bg:rgba(255,118,117,0.1);--gold:#fdcb6e;--gold-bg:rgba(253,203,110,0.1);--purple-bg:rgba(108,92,231,0.12);--shadow:0 2px 8px rgba(0,0,0,.3),0 8px 32px rgba(0,0,0,.2);--radius:12px;--radius-sm:8px}
.light{--bg:#f0f2f5;--bg2:#ffffff;--bg3:#f8f9fb;--bg4:#eef0f4;--surface:rgba(0,0,0,0.02);--surface-hover:rgba(0,0,0,0.04);--border:rgba(0,0,0,0.08);--border-hover:rgba(0,0,0,0.15);--text:#1a1d2e;--text2:#5a5e72;--text3:#9a9eb0;--shadow:0 2px 8px rgba(0,0,0,.08),0 8px 32px rgba(0,0,0,.05)}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:'Inter',system-ui,sans-serif;font-size:13px;overflow:hidden;-webkit-font-smoothing:antialiased}
.mono{font-family:'JetBrains Mono',monospace}

/* TOP BAR */
.topbar{display:flex;align-items:center;padding:0 20px;height:50px;background:var(--bg2);border-bottom:1px solid var(--border);gap:12px;flex-shrink:0;z-index:100}
.logo{font-size:15px;font-weight:800;letter-spacing:-.3px;display:flex;align-items:center;gap:5px;margin-right:8px}
.logo em{color:var(--accent);font-style:normal}
.logo small{font-size:8px;color:var(--text3);font-weight:500;text-transform:uppercase;letter-spacing:1px}
.topbar-right{margin-left:auto;display:flex;align-items:center;gap:8px}
.top-btn{width:30px;height:30px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:13px;transition:.2s}
.top-btn:hover{background:var(--bg3);color:var(--text);border-color:var(--border-hover)}
.theme-btn{width:30px;height:30px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:14px;transition:.2s}
.theme-btn:hover{background:var(--bg3);color:var(--text)}
.clock{font-size:11px;color:var(--text3);font-family:'JetBrains Mono',monospace}
.status-dot{width:6px;height:6px;border-radius:50%;display:inline-block}
.status-dot.on{background:var(--green);box-shadow:0 0 6px var(--green)}
.status-dot.off{background:var(--red);box-shadow:0 0 6px var(--red)}

/* MAIN LAYOUT */
.main{flex:1;overflow-y:auto;padding:20px 24px}
.page{display:none}.page.active{display:block;animation:fade .35s ease}
@keyframes fade{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}

/* HERO */
.hero{text-align:center;padding:40px 20px 30px;max-width:700px;margin:0 auto}
.hero h1{font-size:32px;font-weight:800;letter-spacing:-1px;margin-bottom:6px}
.hero h1 em{color:var(--accent);font-style:normal}
.hero p{color:var(--text2);font-size:14px;line-height:1.6}

/* ACTION GRID */
.action-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;max-width:860px;margin:0 auto 20px}
.action-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px 12px;text-align:center;cursor:pointer;transition:.25s;position:relative;overflow:hidden}
.action-card:hover{background:var(--surface-hover);border-color:var(--border-hover);transform:translateY(-2px);box-shadow:var(--shadow)}
.action-card .icon{font-size:26px;margin-bottom:6px;display:block}
.action-card .name{font-size:12px;font-weight:600;margin-bottom:3px}
.action-card .desc{font-size:10px;color:var(--text2);line-height:1.4}
.action-card .badge-count{position:absolute;top:-4px;right:-4px;min-width:18px;height:18px;padding:0 5px;border-radius:9px;background:var(--red);color:#fff;font-size:9px;font-weight:700;display:flex;align-items:center;justify-content:center}

/* KPI ROW */
.kpi-row{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px;max-width:860px;margin:0 auto 16px}
.kpi-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:14px}
.kpi-card .lbl{font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:.6px;font-weight:600;margin-bottom:4px}
.kpi-card .val{font-size:20px;font-weight:700;font-family:'JetBrains Mono',monospace;letter-spacing:-.3px}
.kpi-card .val.up{color:var(--green)}.kpi-card .val.down{color:var(--red)}.kpi-card .val.neutral{color:var(--gold)}
.kpi-card .sub{font-size:10px;color:var(--text2);margin-top:2px}

/* MODAL */
.modal-overlay{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,.6);backdrop-filter:blur(4px);z-index:1000;display:none;align-items:center;justify-content:center;padding:20px;animation:fadeIn .2s ease}
.modal-overlay.open{display:flex}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.modal{background:var(--bg2);border:1px solid var(--border);border-radius:14px;width:100%;max-width:960px;max-height:85vh;display:flex;flex-direction:column;box-shadow:var(--shadow);animation:scaleIn .25s ease}
.modal.full{max-width:98vw;max-height:92vh}
@keyframes scaleIn{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:scale(1)}}
.modal-header{display:flex;align-items:center;padding:14px 18px;border-bottom:1px solid var(--border);gap:10px;flex-shrink:0}
.modal-header .title{font-size:15px;font-weight:700;flex:1}
.modal-header .sub{font-size:11px;color:var(--text2);font-weight:400}
.modal-close{width:28px;height:28px;border-radius:6px;border:none;background:var(--surface);color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:16px;transition:.2s}
.modal-close:hover{background:var(--red-bg);color:var(--red)}
.modal-body{overflow-y:auto;padding:18px;flex:1}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:12px}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px}
@media(max-width:768px){.grid-4,.grid-3,.grid-2{grid-template-columns:1fr}.hero h1{font-size:24px}}

/* CARD INSIDE MODAL */
.c{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:14px}
.c-title{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:.6px;color:var(--text3);margin-bottom:8px}
.c-val{font-size:20px;font-weight:700;font-family:'JetBrains Mono',monospace}
.c-val.up{color:var(--green)}.c-val.down{color:var(--red)}.c-val.neutral{color:var(--gold)}
.c-sub{font-size:10px;color:var(--text2);margin-top:2px}
.c-chart{height:90px;margin-top:6px}
.c-table{overflow-x:auto}

/* TABLE STYLES */
table{width:100%;border-collapse:collapse;font-size:12px}
thead th{padding:6px 8px;text-align:left;font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;color:var(--text3);border-bottom:1px solid var(--border);position:sticky;top:0;background:var(--bg2)}
tbody td{padding:6px 8px;border-bottom:1px solid var(--border)}
tbody tr:hover{background:var(--surface-hover)}

/* TAGS */
.tag{display:inline-block;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:600}
.tg{background:var(--green-bg);color:var(--green)}.tr{background:var(--red-bg);color:var(--red)}
.ty{background:var(--gold-bg);color:var(--gold)}.tp{background:var(--purple-bg);color:var(--accent2)}

/* CONTROLS */
.controls{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:10px}
input,select{background:var(--bg3);border:1px solid var(--border);border-radius:6px;padding:6px 10px;color:var(--text);font-size:12px;font-family:inherit;outline:none}
input:focus,select:focus{border-color:var(--accent);box-shadow:0 0 0 2px var(--purple-bg)}
.btn{display:inline-flex;align-items:center;gap:4px;padding:6px 12px;border-radius:6px;font-size:11px;font-weight:600;border:none;cursor:pointer;transition:.2s;font-family:inherit}
.bp{background:var(--accent);color:#fff}.bp:hover{background:var(--accent2);transform:translateY(-1px)}
.bg{background:var(--surface);border:1px solid var(--border);color:var(--text2)}.bg:hover{background:var(--bg3);color:var(--text)}
.bs{padding:4px 9px;font-size:10px}
.bi{width:28px;height:28px;padding:0;justify-content:center;border-radius:6px}
.flex{display:flex;gap:6px;align-items:center;flex-wrap:wrap}

/* TOAST */
.toast-area{position:fixed;top:56px;right:16px;z-index:9999;display:flex;flex-direction:column;gap:6px}
.toast{padding:9px 14px;border-radius:var(--radius-sm);font-size:12px;font-weight:500;box-shadow:var(--shadow);animation:slide .3s ease;max-width:320px;pointer-events:none}
.toast.i{background:var(--purple-bg);border-left:3px solid var(--accent);color:var(--accent2)}
.toast.s{background:var(--green-bg);border-left:3px solid var(--green);color:var(--green)}
.toast.w{background:var(--gold-bg);border-left:3px solid var(--gold);color:var(--gold)}
.toast.e{background:var(--red-bg);border-left:3px solid var(--red);color:var(--red)}
@keyframes slide{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:translateX(0)}}

/* FEATURE BAR */
.fb{display:flex;align-items:center;gap:8px;padding:3px 0;font-size:11px}
.fb-track{flex:1;height:5px;background:var(--bg3);border-radius:3px;overflow:hidden}
.fb-fill{height:100%;border-radius:3px;background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width .6s ease}

/* SCROLLBAR */
::-webkit-scrollbar{width:4px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--bg4);border-radius:2px}

/* RESPONSIVE */
@media(max-width:640px){.hero h1{font-size:20px}.action-grid{grid-template-columns:repeat(2,1fr)}.main{padding:12px}.modal{padding:0;max-height:100vh;border-radius:0;max-width:100vw}}
</style>
</head>
<body style="display:flex;flex-direction:column;height:100vh">

<!-- TOPBAR -->
<div class="topbar">
  <div class="logo">Apuestas<em>Pro</em> <small>v4.3</small></div>
  <span class="status-dot on" id="statusDot"></span>
  <div class="topbar-right">
    <span class="clock" id="clock"></span>
    <button class="top-btn" onclick="location.reload()" title="Refrescar">↻</button>
    <button class="top-btn" onclick="toggleSSE()" id="sseBtn" title="Conexión">📡</button>
    <button class="theme-btn" onclick="toggleTheme()" id="themeBtn">🌙</button>
  </div>
</div>

<!-- MAIN -->
<div class="main" id="main">

  <!-- LANDING PAGE -->
  <div class="page active" id="page-landing">
    <div class="hero">
      <h1><em>Apuestas</em>Pro</h1>
      <p>Sistema profesional de análisis de apuestas deportivas — detección de value bets, sharp money, arbitraje, ML predictivo y gestión de portfolio.</p>
    </div>
    <div class="kpi-row" id="landing-kpis"></div>
    <div class="action-grid" id="action-grid"></div>
  </div>

</div>

<!-- TOASTS -->
<div class="toast-area" id="toastArea"></div>

<script>
// ── STATE ──
let sse=null, sseOn=true, charts={}, theme='dark';

function init(){
  setInterval(clock,1000);clock();
  loadLanding();
  connectSSE();
}
function clock(){document.getElementById('clock').textContent=new Date().toLocaleTimeString('es-MX',{hour:'2-digit',minute:'2-digit',second:'2-digit'})}

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
  sse.onmessage=e=>{try{const d=JSON.parse(e.data);if(d.tipo==='value_bet')toast(`Value bet: ${d.edge_pct}% edge`,'s');else if(d.tipo==='sharp')toast(`🔴 Sharp ${d.score}`,'w');else if(d.tipo==='alarma'){toast(`🚨 ${d.msg}`,'e');playAlert()}}catch(_){}};
  sse.onerror=()=>{document.getElementById('statusDot').className='status-dot off';setTimeout(connectSSE,3000)};
  sse.onopen=()=>{document.getElementById('statusDot').className='status-dot on'};
}
function toggleSSE(){
  sseOn=!sseOn;
  document.getElementById('sseBtn').style.opacity=sseOn?'1':'0.35';
  if(sseOn)connectSSE();else if(sse){sse.close();sse=null}
}

// ── TOAST ──
function toast(msg,t='i'){const el=document.createElement('div');el.className='toast '+t;el.textContent=msg;document.getElementById('toastArea').appendChild(el);setTimeout(()=>el.remove(),4000)}
function playAlert(){try{if(!audioCtx)audioCtx=new(window.AudioContext||window.webkitAudioContext)();const o=audioCtx.createOscillator(),g=audioCtx.createGain();o.connect(g);g.connect(audioCtx.destination);o.frequency.value=880;o.type='sine';g.gain.value=0.3;o.start();o.stop(audioCtx.currentTime+0.15)}catch(_){}}

// ── API ──
async function api(u){const r=await fetch(u);return r.json()}
function destroyChart(id){if(charts[id]){charts[id].destroy();delete charts[id]}}

// ── LANDING ──
async function loadLanding(){
  try{
    const[h,rend]=await Promise.all([api('/api/health'),api('/api/dashboard/rendimiento?days=30')]);
    document.getElementById('landing-kpis').innerHTML=[
      {l:'Bankroll',v:`$${((rend.bankroll_actual||0)).toFixed(2)}`,c:(rend.bankroll_actual||0)>=0?'up':'down',s:`Sharpe: ${(rend.sharpe_ratio||0).toFixed(2)}`},
      {l:'Rendimiento',v:`${((rend.return_pct||0)).toFixed(1)}%`,c:(rend.return_pct||0)>=0?'up':'down',s:`${rend.total_apuestas||0} apuestas`},
      {l:'Win Rate',v:`${((rend.win_rate||0)*100).toFixed(1)}%`,c:'neutral',s:`${rend.ganadas||0}G / ${rend.perdidas||0}P`},
      {l:'Conexión',v:'🟢 Activo',c:'up',s:`SSE: ${h.sse_clients||0}`},
    ].map(k=>`<div class="kpi-card"><div class="lbl">${k.l}</div><div class="val ${k.c}">${k.v}</div><div class="sub">${k.s}</div></div>`).join('');
  }catch(e){}

  const modules=[
    {id:'valuebets',icon:'⚡',name:'Value Bets',desc:'Edge >2% con cuotas reales',color:'var(--green)'},
    {id:'sharp',icon:'🔴',name:'Sharp Money',desc:'RLM, Steam, Split, Freeze',color:'var(--red)'},
    {id:'arbitraje',icon:'🔄',name:'Arbitraje',desc:'Surebets en vivo',color:'var(--accent)'},
    {id:'simulacion',icon:'🎮',name:'Simulación',desc:'Trading virtual',color:'var(--green)'},
    {id:'portfolio',icon:'📁',name:'Portfolio',desc:'Kelly correlacionado',color:'var(--gold)'},
    {id:'bookmakers',icon:'🏷️',name:'Bookmakers',desc:'Rating de casas',color:'var(--accent2)'},
    {id:'cross',icon:'🔗',name:'Cross-Market',desc:'H2H vs AH',color:'var(--gold)'},
    {id:'mlav',icon:'🧠',name:'ML Avanzado',desc:'30+ features',color:'var(--accent)'},
    {id:'contabilidad',icon:'💰',name:'Contabilidad',desc:'P&L real',color:'var(--green)'},
    {id:'journal',icon:'📓',name:'Trading Journal',desc:'Registro automático',color:'var(--gold)'},
    {id:'backtest',icon:'📊',name:'Backtesting',desc:'Histórico value betting',color:'var(--accent2)'},
    {id:'config',icon:'⚙️',name:'Sistema',desc:'Estado y diagnóstico',color:'var(--text2)'},
  ];
  document.getElementById('action-grid').innerHTML=modules.map(m=>`<div class="action-card" onclick="openModule('${m.id}')"><span class="icon">${m.icon}</span><div class="name">${m.name}</div><div class="desc">${m.desc}</div></div>`).join('');
}

// ── MODAL SYSTEM ──
function openModule(id){
  const existing=document.getElementById('modal-'+id);
  if(existing){existing.classList.add('open');return}
  const modal=document.createElement('div');modal.className='modal-overlay';modal.id='modal-'+id;
  modal.onclick=e=>{if(e.target===modal)modal.remove()};
  modal.innerHTML=`<div class="modal full"><div class="modal-header"><div class="title">Cargando...</div><span class="sub"></span><button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button></div><div class="modal-body"><div style="text-align:center;padding:40px;color:var(--text2)">Cargando módulo...</div></div></div>`;
  document.body.appendChild(modal);
  setTimeout(()=>modal.classList.add('open'),10);
  loadModule(id,modal);
}

function loadModule(id,modal){
  const fns={
    valuebets:loadValueBets,sharp:loadSharp,arbitraje:loadArbitraje,
    simulacion:loadSimulacion,portfolio:loadPortfolio,bookmakers:loadBookmakers,
    cross:loadCrossMarket,mlav:loadMLAv,contabilidad:loadContabilidad,
    journal:loadJournal,backtest:loadBacktest,config:loadConfig,
  };
  if(fns[id])fns[id](modal);
}

function setModalContent(modal,title,sub,body){
  const h=modal.querySelector('.modal-header');
  h.innerHTML=`<div class="title">${title}</div><span class="sub">${sub||''}</span><button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button>`;
  modal.querySelector('.modal-body').innerHTML=body;
}

// ── MODULES ──

// VALUE BETS
async function loadValueBets(modal){
  setModalContent(modal,'⚡ Value Bets','Apuestas con valor esperado positivo','<div id="vb-content">Cargando...</div>');
  try{const vb=await api('/api/odds/value-bets?min_edge=2&limit=30');const list=vb.value_bets||[];
  document.getElementById('vb-content').innerHTML=list.length?`<table><thead><tr><th>Partido</th><th>Liga</th><th>Cuota</th><th>Edge</th><th>Casa</th></tr></thead><tbody>${list.map(v=>`<tr><td>${v.partido||'?'}</td><td>${v.liga||''}</td><td>${(v.cuota||0).toFixed(2)}</td><td><span class="tag tg">+${(v.edge_pct||0).toFixed(1)}%</span></td><td>${v.casa||''}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin value bets ahora</span>'}catch(e){document.getElementById('vb-content').innerHTML='<span style="color:var(--red)">Error cargando</span>'}
}

// SHARP
async function loadSharp(modal){
  setModalContent(modal,'🔴 Sharp Money','Detección de sharp money en 6 deportes','<div id="sharp-content">Cargando...</div>');
  try{const sh=await api('/api/odds/sharp?deporte=all');const list=sh.alertas||[];
  document.getElementById('sharp-content').innerHTML=list.length?`<table><thead><tr><th>Partido</th><th>Liga</th><th>Score</th><th>Tipo</th></tr></thead><tbody>${list.slice(0,30).map(s=>`<tr><td>${s.partido||s.detalle||'?'}</td><td>${s.liga||''}</td><td><span class="tag ${(s.score||0)>7?'tr':'ty'}">${s.score||s.urgencia||''}</span></td><td>${s.tipo||'?'}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin alertas sharp ahora</span>'}catch(e){document.getElementById('sharp-content').innerHTML='<span style="color:var(--red)">Error</span>'}
}

// ARBITRAJE
async function loadArbitraje(modal){
  setModalContent(modal,'🔄 Arbitraje / Surebets','Oportunidades de arbitraje en vivo','<div id="arb-content">Cargando...</div>');
  try{const ar=await api('/api/odds/arbitraje');const list=ar.arbitrajes||[];
  document.getElementById('arb-content').innerHTML=list.length?`<table><thead><tr><th>Partido</th><th>Profit</th><th>Resultados</th><th>Bookmakers</th></tr></thead><tbody>${list.slice(0,25).map(a=>`<tr><td>${a.partido||(a.resultados||[]).join(' vs ')}</td><td><span class="tag tg">${(a.profit_pct||0).toFixed(2)}%</span></td><td>${(a.resultados||[]).join(', ')}</td><td>${a.n_bookmakers||0}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin arbitraje ahora</span>'}catch(e){document.getElementById('arb-content').innerHTML='<span style="color:var(--red)">Error</span>'}
}

// SIMULACION
async function loadSimulacion(modal){
  setModalContent(modal,'🎮 Simulación en Vivo','Trading simulado con bankroll virtual','<div id="sim-content">Cargando...</div>');
  try{const s=await api('/api/simulacion/status');
  let html=`<div class="grid-4">${[
    {l:'Bankroll Sim',v:`$${(s.bankroll_actual||0).toFixed(2)}`,c:'up',s:`Inicial: $${(s.bankroll_inicial||10000).toFixed(0)}`},
    {l:'Trades',v:s.total_trades||0,c:'neutral',s:`${s.ganados||0}G / ${s.perdidos||0}P`},
    {l:'ROI',v:`${((s.roi||0)).toFixed(1)}%`,c:(s.roi||0)>=0?'up':'down',s:`${s.win_rate_pct||0}% WR`},
    {l:'Profit Neto',v:`$${(s.profit_neto||0).toFixed(2)}`,c:(s.profit_neto||0)>=0?'up':'down',s:'Acumulado'},
  ].map(k=>`<div class="c"><div class="c-title">${k.l}</div><div class="c-val ${k.c}">${k.v}</div><div class="c-sub">${k.s}</div></div>`).join('')}</div>`;
  const pend=s.trades_pendientes||[];
  html+=`<div class="c"><div class="c-title">Trades Pendientes</div>${pend.length?`<table><thead><tr><th>Partido</th><th>Cuota</th><th>Edge</th><th>Stake</th></tr></thead><tbody>${pend.slice(0,12).map(t=>`<tr><td>${t.partido||''}</td><td>${(t.cuota||0).toFixed(2)}</td><td><span class="tag tg">${(t.edge_pct||0).toFixed(1)}%</span></td><td>$${(t.stake_simulado||0).toFixed(2)}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin trades pendientes</span>'}</div>`;
  document.getElementById('sim-content').innerHTML=html}catch(e){document.getElementById('sim-content').innerHTML='<span style="color:var(--red)">Error</span>'}
}

// PORTFOLIO
async function loadPortfolio(modal){
  setModalContent(modal,'📁 Portfolio Inteligente','Gestión de bankroll con Kelly correlacionado','<div id="port-content">Cargando...</div>');
  try{const p=await api('/api/portfolio/recomendar?dias=30');
  let html=`<div class="grid-4">${[
    {l:'Bankroll',v:`$${(p.bankroll_actual||0).toFixed(2)}`,c:'up',s:`Stake: ${((p.max_stake_pct||0)*100).toFixed(1)}%`},
    {l:'Apuestas Activas',v:p.apuestas_activas||0,c:'neutral',s:`Exp: $${(p.exposicion_total||0).toFixed(2)}`},
    {l:'Kelly Recom.',v:`${((p.kelly_recomendado||0)*100).toFixed(1)}%`,c:'neutral',s:'Fracción'},
    {l:'Sharpe',v:(p.sharpe_ratio||0).toFixed(2),c:(p.sharpe_ratio||0)>=1?'up':'neutral',s:'30d'},
  ].map(k=>`<div class="c"><div class="c-title">${k.l}</div><div class="c-val ${k.c}">${k.v}</div><div class="c-sub">${k.s}</div></div>`).join('')}</div>`;
  const recs=p.recomendaciones||[];
  html+=`<div class="c"><div class="c-title">Recomendaciones Activas</div>${recs.length?`<table><thead><tr><th>Partido</th><th>Selección</th><th>Cuota</th><th>Edge</th><th>Kelly</th><th>Stake</th></tr></thead><tbody>${recs.slice(0,15).map(r=>`<tr><td>${r.partido||''}</td><td>${r.seleccion||''}</td><td>${(r.cuota||0).toFixed(2)}</td><td><span class="tag tg">${(r.edge_pct||0).toFixed(1)}%</span></td><td>${((r.kelly_pct||0)).toFixed(1)}%</td><td><strong>$${(r.stake||0).toFixed(2)}</strong></td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin recomendaciones activas</span>'}</div>`;
  document.getElementById('port-content').innerHTML=html}catch(e){document.getElementById('port-content').innerHTML='<span style="color:var(--red)">Error</span>'}
}

// BOOKMAKERS
async function loadBookmakers(modal){
  setModalContent(modal,'🏷️ Rating de Casas','Ranking por overround, CLV y velocidad','<div id="bm-content">Cargando...</div>');
  try{const bm=await api('/api/bookmakers/rating');const rows=bm.ranking||[];
  document.getElementById('bm-content').innerHTML=rows.length?`<table><thead><tr><th>#</th><th>Casa</th><th>Overround</th><th>Cuota Prom</th><th>CLV</th><th>Score</th></tr></thead><tbody>${rows.map((r,i)=>`<tr><td>${i+1}</td><td><strong>${r.bookmaker||''}</strong></td><td><span class="tag ${(r.avg_overround||5)<5?'tg':'ty'}">${(r.avg_overround||0).toFixed(2)}%</span></td><td>${(r.avg_cuota||0).toFixed(3)}</td><td>${(r.avg_clv||0).toFixed(2)}</td><td style="font-weight:700;color:${i<3?'var(--green)':'var(--text2)'}">${(r.score||0).toFixed(1)}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin datos</span>'}catch(e){document.getElementById('bm-content').innerHTML='<span style="color:var(--red)">Error</span>'}
}

// CROSS-MARKET
async function loadCrossMarket(modal){
  setModalContent(modal,'🔗 Cross-Market','Inconsistencias H2H vs Asian Handicap','<div id="cross-content">Cargando...</div>');
  try{const cm=await api('/api/odds/cross-market');const opps=cm.opportunities||[];
  document.getElementById('cross-content').innerHTML=opps.length?`<table><thead><tr><th>Partido</th><th>Mercados</th><th>Diferencia</th><th>Acción</th></tr></thead><tbody>${opps.slice(0,20).map(o=>`<tr><td>${o.partido||''}</td><td>${(o.mercados||[]).join(' vs ')}</td><td><span class="tag ${(o.diferencia||0)>5?'tg':'ty'}">${(o.diferencia||0).toFixed(2)}%</span></td><td>${o.accion||'—'}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin oportunidades</span>'}catch(e){document.getElementById('cross-content').innerHTML='<span style="color:var(--red)">Error</span>'}
}

// ML AVANZADO
async function loadMLAv(modal){
  setModalContent(modal,'🧠 ML Avanzado','30+ features · MLP Neural Net · Gradient Boosting','<div id="mlav-content">Cargando...</div><div class="flex" style="margin-top:10px"><select id="mlav-liga"><option value="liga_mx">Liga MX</option><option value="premier_league">Premier</option><option value="la_liga">La Liga</option><option value="serie_a">Serie A</option><option value="bundesliga">Bundesliga</option><option value="ligue_1">Ligue 1</option><option value="mls">MLS</option></select><button class="btn bp bs" onclick="trainMLAv()">Entrenar</button><button class="btn bg bs" onclick="predictProximosMLAv()">Predecir Próximos</button></div><div id="mlav-preds" style="margin-top:10px"></div>');
  try{const[feat,perf]=await Promise.all([api('/api/ml/v2/features?liga=liga_mx'),api('/api/ml/v2/performance?liga=liga_mx')]);const items=feat.features||[],rend=perf.rendimiento||[],last=rend[rend.length-1]||{},maxImp=Math.max(...items.map(i=>i.importance||0),0.01),top=items.slice(0,3);
  let html=`<div class="grid-4">${[
    {l:'Features',v:items.length||0,c:'neutral',s:'20+ ingeniería'},{l:'Top Feature',v:top[0]?.feature_name||'N/A',c:'neutral',s:`${top[0]?((top[0].importance||0)*100).toFixed(1):''}%`},
    {l:'Acc. MLP',v:last.accuracy?`${(last.accuracy*100).toFixed(1)}%`:'N/A',c:'neutral',s:'Neural Net'},{l:'Log Loss GBM',v:last.log_loss?last.log_loss.toFixed(4):'N/A',c:'neutral',s:'Gradient Boosting'},
  ].map(k=>`<div class="c"><div class="c-title">${k.l}</div><div class="c-val ${k.c}">${k.v}</div><div class="c-sub">${k.s}</div></div>`).join('')}</div>`;
  html+=`<div class="grid-2"><div class="c"><div class="c-title">Feature Importance</div>${items.length?items.map((f,i)=>`<div class="fb"><span style="width:14px;color:var(--text3)">${i+1}</span><div class="fb-track"><div class="fb-fill" style="width:${(f.importance||0)/maxImp*100}%"></div></div><span style="width:130px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${f.feature_name||''}</span><span style="width:38px;text-align:right;color:var(--text2)">${((f.importance||0)*100).toFixed(1)}%</span></div>`).join(''):'<span style="color:var(--text2)">Entrena primero</span>'}</div>`;
  html+=`<div class="c"><div class="c-title">Rendimiento</div>${rend.length?`<table><thead><tr><th>Fecha</th><th>Modelo</th><th>Acc</th><th>LL</th><th>N</th></tr></thead><tbody>${rend.slice(-8).reverse().map(r=>`<tr><td style="font-size:10px;color:var(--text3)">${(r.created_at||'').slice(0,10)}</td><td>${r.modelo||''}</td><td><span class="tag tg">${r.accuracy?((r.accuracy)*100).toFixed(1)+'%':'-'}</span></td><td>${r.log_loss?r.log_loss.toFixed(4):'-'}</td><td>${r.n_muestras||''}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin datos</span>'}</div></div>`;
  document.getElementById('mlav-content').innerHTML=html}catch(e){document.getElementById('mlav-content').innerHTML='<span style="color:var(--red)">Error</span>'}
}
async function trainMLAv(){toast('Entrenando modelos...','i');try{const r=await api('/api/ml/v2/train');toast(`Entrenado: ${r.ligas_entrenadas||0} ligas`,'s')}catch(e){toast('Error','e')}}
async function predictProximosMLAv(){const liga=document.getElementById('mlav-liga').value;toast(`Prediciendo ${liga}...`,'i');
  try{const r=await api(`/api/ml/v2/predict-proximos?liga=${liga}&dias=7`);const preds=r.predicciones||[];
  document.getElementById('mlav-preds').innerHTML=preds.length?`<div class="c"><div class="c-title">Predicciones ${liga}</div><table><thead><tr><th>Partido</th><th>1</th><th>X</th><th>2</th><th>Pick</th><th>Conf</th></tr></thead><tbody>${preds.map(p=>{const pick=p.pronostico||'';return `<tr><td><strong>${p.home||''}</strong> vs <strong>${p.away||''}</strong></td><td>${((p.prob_local||0)*100).toFixed(0)}%</td><td>${((p.prob_empate||0)*100).toFixed(0)}%</td><td>${((p.prob_visitante||0)*100).toFixed(0)}%</td><td><span class="tag ${pick==='1'?'tg':pick==='2'?'tr':'ty'}">${pick}</span></td><td><strong>${p.confianza_pct||0}%</strong></td></tr>`}).join('')}</tbody></table></div>`:'<span style="color:var(--text2)">Sin próximos</span>'}catch(e){toast('Error','e')}}

// CONTABILIDAD
async function loadContabilidad(modal){
  setModalContent(modal,'💰 Contabilidad','Control de depósitos, retiros y P&L real','<div id="acct-content">Cargando...</div><div class="flex" style="margin-top:10px"><input type="number" id="acct-monto" placeholder="Monto" style="width:90px"><select id="acct-tipo"><option value="deposito">Depósito</option><option value="retiro">Retiro</option><option value="ajuste">Ajuste</option></select><input type="text" id="acct-desc" placeholder="Descripción" style="flex:1;min-width:100px"><input type="text" id="acct-est" placeholder="Estrategia" style="width:100px"><button class="btn bp bs" onclick="addTransaction()">Registrar</button></div>');
  try{const[resumen,pnl]=await Promise.all([api('/api/contabilidad/resumen-mensual'),api('/api/contabilidad/pnl-estrategia?dias=30')]);
  let html=`<div class="grid-4">${[
    {l:'Balance Mes',v:`$${(resumen.balance||0).toFixed(2)}`,c:(resumen.balance||0)>=0?'up':'down',s:`${resumen.total_transacciones||0} transacciones`},
    {l:'Ingresos',v:`$${(resumen.ingresos||0).toFixed(2)}`,c:'up',s:''},{l:'Egresos',v:`$${(resumen.egresos||0).toFixed(2)}`,c:'down',s:''},
  ].map(k=>`<div class="c"><div class="c-title">${k.l}</div><div class="c-val ${k.c}">${k.v}</div><div class="c-sub">${k.s}</div></div>`).join('')}</div>`;
  const ests=resumen.por_estrategia||{};
  html+=`<div class="grid-2"><div class="c"><div class="c-title">P&L por Estrategia</div>${Object.keys(ests).length?`<table><thead><tr><th>Estrategia</th><th>Ingresos</th><th>Egresos</th><th>Neto</th><th>Ops</th></tr></thead><tbody>${Object.entries(ests).map(([k,v])=>`<tr><td><strong>${k}</strong></td><td style="color:var(--green)">$${(v.ingresos||0).toFixed(2)}</td><td style="color:var(--red)">$${(v.egresos||0).toFixed(2)}</td><td style="font-weight:700;color:${(v.neto||0)>=0?'var(--green)':'var(--red)'}">$${(v.neto||0).toFixed(2)}</td><td>${v.n_operaciones||0}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin datos</span>'}</div>`;
  html+=`<div class="c"><div class="c-title">P&L Mensual</div>${(pnl||[]).length?`<table><thead><tr><th>Estrategia</th><th>G</th><th>P</th><th>Neto</th></tr></thead><tbody>${(pnl||[]).slice(0,10).map(r=>`<tr><td>${r.estrategia||'N/A'}</td><td><span class="tag tg">${r.ganadas||0}</span></td><td><span class="tag tr">${r.perdidas||0}</span></td><td style="font-weight:700;color:${(r.neto||0)>=0?'var(--green)':'var(--red)'}">$${(r.neto||0).toFixed(2)}</td></tr>`).join('')}</tbody></table>`:'<span style="color:var(--text2)">Sin P&L</span>'}</div></div>`;
  document.getElementById('acct-content').innerHTML=html}catch(e){document.getElementById('acct-content').innerHTML='<span style="color:var(--red)">Error</span>'}
}
async function addTransaction(){const m=parseFloat(document.getElementById('acct-monto').value),t=document.getElementById('acct-tipo').value,d=document.getElementById('acct-desc').value,e=document.getElementById('acct-est').value;if(!m){toast('Ingresa monto','w');return}
  try{const r=await fetch('/api/contabilidad/transaccion',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tipo:t,monto:m,descripcion:d,estrategia:e})});const j=await r.json();
  if(j.ok){toast('Registrada','s');document.getElementById('acct-monto').value='';loadContabilidad(document.getElementById('modal-contabilidad'))}else toast('Error: '+j.error,'e')}catch(e){toast('Error red','e')}}

// JOURNAL
async function loadJournal(modal){
  const bod=`<div id="j-content">Cargando...</div><div class="flex" style="margin-top:10px"><button class="btn bg bs" onclick="(()=>{const m=document.getElementById('modal-journal');if(m){const b=m.querySelector('.modal-body');b.innerHTML='<div id=\\'j-content\\'>Cargando...</div>';loadJournal(m)}})()">↻ Refrescar</button><button class="btn bg bs" onclick="window.open('/api/journal/export-csv','_blank')">⬇ CSV</button><button class="btn bp bs" onclick="autoJournal()">Auto-Log</button></div>`;
  setModalContent(modal,'📓 Trading Journal','Registro automático de cada acción',bod);
  try{const j=await api('/api/journal/resumen?dias=7');
  let html=`<div class="grid-4">${[
    {l:'Total',v:j.total_acciones||0,c:'neutral',s:`${j.dias||7}d`},{l:'Value Bets',v:(j.por_tipo||{}).value_bet_detected||0,c:'up',s:''},
    {l:'Apuestas Real',v:(j.por_tipo||{}).apuesta_real||0,c:'neutral',s:''},{l:'Sharp Alerts',v:(j.por_tipo||{}).sharp_alert||0,c:'warn',s:''},
  ].map(k=>`<div class="c"><div class="c-title">${k.l}</div><div class="c-val ${k.c}">${k.v}</div><div class="c-sub">${k.s}</div></div>`).join('')}</div>`;
  const ult=j.ultimas_acciones||[];
  html+=ult.length?`<div class="c"><table><thead><tr><th>Fecha</th><th>Tipo</th><th>Partido</th><th>Estrategia</th><th>Resultado</th><th>P&L</th></tr></thead><tbody>${ult.map(r=>`<tr><td style="font-size:10px;color:var(--text3)">${(r.fecha||'').slice(0,19)}</td><td>${r.tipo||''}</td><td>${r.partido||''}</td><td>${r.estrategia||''}</td><td><span class="tag ${r.resultado==='ganada'?'tg':r.resultado==='perdida'?'tr':'ty'}">${r.resultado||'—'}</span></td><td style="font-weight:700;color:${(r.pnl||0)>=0?'var(--green)':'var(--red)'}">$${(r.pnl||0).toFixed(2)}</td></tr>`).join('')}</tbody></table></div>`:'<span style="color:var(--text2)">Sin actividad reciente</span>';
  document.getElementById('j-content').innerHTML=html}catch(e){document.getElementById('j-content').innerHTML='<span style="color:var(--red)">Error</span>'}
}
async function autoJournal(){try{const r=await api('/api/journal/auto-log');toast(`${r.registrados||0} registradas`,'s');const m=document.getElementById('modal-journal');if(m){m.querySelector('.modal-body').innerHTML='<div id=\'j-content\'>Cargando...</div>';loadJournal(m)}}catch(e){toast('Error','e')}}

// BACKTEST
async function loadBacktest(modal){
  setModalContent(modal,'📊 Backtesting','Simulación histórica de value betting','<div id="bt-content">Cargando...</div>');
  try{const bt=await api('/api/backtest/full');
  let html=`<div class="grid-4">${[
    {l:'ROI Total',v:`${(bt.roi_total||0).toFixed(1)}%`,c:(bt.roi_total||0)>=0?'up':'down',s:`${bt.total_apuestas||0} apuestas`},
    {l:'Win Rate',v:`${(bt.win_rate||0).toFixed(1)}%`,c:'neutral',s:`${bt.ganadas||0}G / ${bt.perdidas||0}P`},
    {l:'Profit Neto',v:`$${(bt.profit_neto||0).toFixed(2)}`,c:(bt.profit_neto||0)>=0?'up':'down',s:`Bankroll final: $${(bt.bankroll_final||0).toFixed(2)}`},
    {l:'Sharpe',v:(bt.sharpe_ratio||0).toFixed(2),c:(bt.sharpe_ratio||0)>=1?'up':'neutral',s:`Kelly frac: ${((bt.kelly_frac||0)*100).toFixed(0)}%`},
  ].map(k=>`<div class="c"><div class="c-title">${k.l}</div><div class="c-val ${k.c}">${k.v}</div><div class="c-sub">${k.s}</div></div>`).join('')}</div>`;
  const hist=bt.bankroll_history||[];
  html+=`<div class="c"><div class="c-title">Bankroll History</div><div class="c-chart"><canvas id="btChart"></canvas></div></div>`;
  document.getElementById('bt-content').innerHTML=html;
  if(hist.length>1){destroyChart('btChart');
    charts.btChart=new Chart(document.getElementById('btChart'),{type:'line',data:{labels:hist.map((_,i)=>i),datasets:[{label:'Bankroll',data:hist,borderColor:'#6c5ce7',backgroundColor:'rgba(108,92,231,0.1)',fill:true,tension:.3,pointRadius:0,borderWidth:2}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{display:false,grid:{display:false}},y:{grid:{color:'rgba(255,255,255,0.03)'},ticks:{font:{size:9}}}}}})};
  }catch(e){document.getElementById('bt-content').innerHTML='<span style="color:var(--red)">Error</span>'}
}

// CONFIG
async function loadConfig(modal){
  setModalContent(modal,'⚙️ Sistema','Estado y diagnóstico completo','<div id="cfg-content" class="mono" style="font-size:11px;white-space:pre-wrap;line-height:1.7">Cargando...</div>');
  try{const h=await api('/api/health');document.getElementById('cfg-content').textContent=JSON.stringify(h,null,2)}catch(e){document.getElementById('cfg-content').textContent='Error'}
}

// ── INIT ──
let audioCtx=null;
if("Notification"in window&&Notification.permission==='default')Notification.requestPermission();
init();
</script>
</body>
</html>"""
