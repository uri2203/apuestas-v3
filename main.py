HTML = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ApuestasPro — Sistema Profesional</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@500;700;800&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#07070a;--bg2:#0e0e14;--bg3:#141420;--bg4:#1c1c2e;
  --border:rgba(255,255,255,0.06);--border2:rgba(255,255,255,0.12);
  --text:#e8e8f2;--muted:#5a5a7a;--dim:#2e2e48;
  --purple:#7c6dfa;--purple2:#a396ff;
  --teal:#2dd4bf;--gold:#f0b429;--green:#34d399;--red:#f87171;
  --mono:'DM Mono',monospace;--ui:'Syne',sans-serif;
}
html,body{height:100%;overflow:hidden}
body{background:var(--bg);color:var(--text);font-family:var(--ui)}
::-webkit-scrollbar{width:3px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--dim);border-radius:2px}

/* LAYOUT */
.shell{display:grid;grid-template-columns:220px 1fr;grid-template-rows:52px 1fr;height:100vh}

/* TOPBAR */
.topbar{
  grid-column:1/-1;display:flex;align-items:center;justify-content:space-between;
  padding:0 22px;border-bottom:1px solid var(--border);background:var(--bg);z-index:10;
}
.logo{font-size:18px;font-weight:800;letter-spacing:-0.5px}
.logo em{color:var(--purple);font-style:normal}
.logo small{font-size:10px;font-family:var(--mono);color:var(--muted);margin-left:6px;font-weight:400}
.topbar-right{display:flex;align-items:center;gap:14px}
.live-pill{display:flex;align-items:center;gap:5px;font-size:10px;font-family:var(--mono);
  color:var(--green);background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.2);
  padding:3px 9px;border-radius:20px}
.live-dot{width:5px;height:5px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.4)}}
.clock{font-family:var(--mono);font-size:12px;color:var(--muted)}
.api-status{font-size:10px;font-family:var(--mono);padding:3px 8px;border-radius:4px;cursor:default}
.api-status.ok{background:rgba(52,211,153,.08);color:var(--green);border:1px solid rgba(52,211,153,.15)}
.api-status.err{background:rgba(248,113,113,.08);color:var(--red);border:1px solid rgba(248,113,113,.15)}

/* SIDEBAR */
.sidebar{
  background:var(--bg);border-right:1px solid var(--border);
  overflow-y:auto;padding:10px 0;display:flex;flex-direction:column;
}
.nav-label{font-size:9px;font-family:var(--mono);color:var(--dim);letter-spacing:2px;
  text-transform:uppercase;padding:14px 16px 4px}
.nav-btn{
  display:flex;align-items:center;gap:9px;padding:9px 16px;font-size:12px;
  cursor:pointer;color:var(--muted);background:none;border:none;width:100%;
  text-align:left;transition:all .15s;position:relative;font-family:var(--ui);
}
.nav-btn:hover{color:var(--text);background:rgba(255,255,255,.025)}
.nav-btn.on{color:var(--text);background:rgba(124,109,250,.08)}
.nav-btn.on::before{content:'';position:absolute;left:0;top:5px;bottom:5px;width:2px;
  background:var(--purple);border-radius:2px}
.nav-icon{width:16px;text-align:center;font-size:13px;flex-shrink:0}
.nav-badge{margin-left:auto;font-size:9px;font-family:var(--mono);
  padding:1px 5px;border-radius:3px}
.nb-gold{background:rgba(240,180,41,.12);color:var(--gold)}
.nb-green{background:rgba(52,211,153,.10);color:var(--green)}

/* MAIN */
.main{overflow-y:auto;background:var(--bg2);padding:24px}
.section{display:none}
.section.on{display:block;animation:fu .22s ease}
@keyframes fu{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:translateY(0)}}

/* PAGE HEADER */
.ph{margin-bottom:22px}
.ph-title{font-size:22px;font-weight:800;letter-spacing:-.5px;margin-bottom:3px}
.ph-sub{font-size:11px;font-family:var(--mono);color:var(--muted)}

/* STAT CARDS */
.sg{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px}
.sc{background:var(--bg3);border:1px solid var(--border);border-radius:10px;
  padding:14px 16px;position:relative;overflow:hidden}
.sc-glow{position:absolute;top:-20px;right:-20px;width:70px;height:70px;
  border-radius:50%;filter:blur(22px);opacity:.22}
.sc-lbl{font-size:10px;font-family:var(--mono);color:var(--muted);margin-bottom:7px}
.sc-val{font-size:24px;font-weight:800;letter-spacing:-1px;line-height:1}
.sc-sub{font-size:10px;font-family:var(--mono);color:var(--muted);margin-top:5px}

/* PANEL */
.panel{background:var(--bg3);border:1px solid var(--border);border-radius:10px;
  margin-bottom:14px;overflow:hidden}
.ph2{display:flex;align-items:center;justify-content:space-between;
  padding:12px 16px;border-bottom:1px solid var(--border)}
.pt{font-size:12px;font-weight:700;display:flex;align-items:center;gap:7px}
.pb{padding:16px}
.chip{font-size:9px;font-family:var(--mono);padding:2px 6px;border-radius:3px;font-weight:500}
.cp{background:rgba(124,109,250,.15);color:var(--purple2)}
.cg{background:rgba(52,211,153,.1);color:var(--green)}
.ct{background:rgba(45,212,191,.1);color:var(--teal)}
.cy{background:rgba(240,180,41,.1);color:var(--gold)}
.cr{background:rgba(248,113,113,.1);color:var(--red)}

/* GRID 2 */
.g2{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}

/* BALLS */
.balls{display:flex;flex-wrap:wrap;gap:5px}
.ball{width:32px;height:32px;border-radius:50%;display:inline-flex;align-items:center;
  justify-content:center;font-size:11px;font-weight:700;font-family:var(--mono);
  flex-shrink:0;transition:transform .12s;cursor:default}
.ball:hover{transform:scale(1.15)}
.bh{background:rgba(240,180,41,.12);border:1px solid rgba(240,180,41,.35);color:var(--gold)}
.bc{background:rgba(45,212,191,.08);border:1px solid rgba(45,212,191,.25);color:var(--teal)}
.bs{background:rgba(124,109,250,.15);border:1px solid rgba(124,109,250,.4);color:var(--purple2)}
.bd{background:rgba(255,255,255,.03);border:1px solid var(--border);color:var(--muted)}

/* FREQ BAR */
.fb{display:flex;align-items:center;gap:7px;margin-bottom:5px}
.fb-l{font-size:10px;font-family:var(--mono);color:var(--muted);width:20px;text-align:right}
.fb-t{flex:1;height:5px;background:rgba(255,255,255,.04);border-radius:3px;overflow:hidden}
.fb-f{height:100%;border-radius:3px;transition:width .6s cubic-bezier(.4,0,.2,1)}
.fb-v{font-size:9px;font-family:var(--mono);color:var(--muted);width:28px}

/* HEATMAP */
.hm{display:grid;grid-template-columns:repeat(8,1fr);gap:3px}
.hm-c{aspect-ratio:1;border-radius:4px;display:flex;align-items:center;justify-content:center;
  font-size:8px;font-family:var(--mono);font-weight:600;cursor:default;transition:transform .1s}
.hm-c:hover{transform:scale(1.2);z-index:2;position:relative}

/* TABLE */
.tbl{width:100%;border-collapse:collapse;font-size:12px}
.tbl th{font-size:9px;font-family:var(--mono);color:var(--muted);text-align:left;
  padding:8px 12px;border-bottom:1px solid var(--border);letter-spacing:1.5px;
  text-transform:uppercase;font-weight:500}
.tbl td{padding:10px 12px;border-bottom:1px solid var(--border);vertical-align:middle}
.tbl tr:last-child td{border-bottom:none}
.tbl tr:hover td{background:rgba(255,255,255,.02)}

/* BADGES */
.badge{display:inline-block;font-size:9px;font-family:var(--mono);
  padding:2px 6px;border-radius:3px;font-weight:600}
.bv{background:rgba(52,211,153,.1);color:var(--green);border:1px solid rgba(52,211,153,.2)}
.bs2{background:rgba(240,180,41,.1);color:var(--gold);border:1px solid rgba(240,180,41,.2)}
.ba{background:rgba(45,212,191,.1);color:var(--teal);border:1px solid rgba(45,212,191,.2)}
.bsh{background:rgba(124,109,250,.1);color:var(--purple2);border:1px solid rgba(124,109,250,.2)}
.bdim{background:rgba(255,255,255,.04);color:var(--muted)}
.bwin{background:rgba(52,211,153,.1);color:var(--green)}
.blose{background:rgba(248,113,113,.1);color:var(--red)}

/* INPUTS */
.field{margin-bottom:11px}
.field label{display:block;font-size:10px;font-family:var(--mono);color:var(--muted);
  margin-bottom:4px;letter-spacing:.5px}
.field input,.field select{
  width:100%;padding:8px 11px;border-radius:7px;
  background:rgba(255,255,255,.04);border:1px solid var(--border2);
  color:var(--text);font-size:12px;font-family:var(--ui);transition:border-color .15s}
.field input:focus,.field select:focus{outline:none;border-color:var(--purple)}
.field select option{background:#111}

/* BUTTONS */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;
  padding:8px 16px;border-radius:7px;font-size:12px;font-weight:700;
  cursor:pointer;border:none;transition:all .15s;font-family:var(--ui)}
.btn-p{background:var(--purple);color:#fff}
.btn-p:hover{background:#9585ff;transform:translateY(-1px)}
.btn-p:active{transform:scale(.98)}
.btn-g{background:rgba(255,255,255,.05);color:var(--text);border:1px solid var(--border2)}
.btn-g:hover{background:rgba(255,255,255,.09)}
.btn:disabled{opacity:.4;cursor:not-allowed!important;transform:none!important}
.brow{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}

/* PILLS */
.pills{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:14px}
.pill{padding:4px 12px;border-radius:20px;border:1px solid var(--border2);font-size:11px;
  cursor:pointer;background:transparent;color:var(--muted);font-family:var(--ui);transition:all .15s}
.pill.on{background:rgba(124,109,250,.12);border-color:var(--purple);color:var(--purple2)}
.pill:hover:not(.on){color:var(--text);background:rgba(255,255,255,.03)}

/* RESULT BOX */
.rbox{border-radius:8px;padding:13px 15px;font-family:var(--mono);font-size:12px;line-height:1.8}
.rg{background:rgba(52,211,153,.07);border:1px solid rgba(52,211,153,.18);color:var(--green)}
.rb{background:rgba(248,113,113,.07);border:1px solid rgba(248,113,113,.18);color:var(--red)}
.ri{background:rgba(124,109,250,.07);border:1px solid rgba(124,109,250,.18);color:var(--purple2)}
.rbox strong{color:#fff}

/* KELLY BIG */
.k-big{text-align:center;padding:20px 0 14px}
.k-amount{font-size:48px;font-weight:800;letter-spacing:-2px;line-height:1}
.k-lbl{font-size:10px;font-family:var(--mono);color:var(--muted);margin-top:5px}
.k-rows{border-top:1px solid var(--border);padding-top:13px;display:flex;flex-direction:column;gap:8px}
.k-row{display:flex;justify-content:space-between;font-size:12px}
.k-row span:first-child{color:var(--muted);font-family:var(--mono)}
.k-row span:last-child{font-family:var(--mono);font-weight:700}

/* ALERT */
.afeed{display:flex;flex-direction:column;gap:7px}
.ai{display:flex;justify-content:space-between;align-items:flex-start;
  padding:10px 13px;border-radius:8px;gap:10px}
.ai.w{background:rgba(240,180,41,.06);border-left:2px solid var(--gold)}
.ai.g{background:rgba(52,211,153,.06);border-left:2px solid var(--green)}
.ai.i{background:rgba(124,109,250,.06);border-left:2px solid var(--purple)}
.ai.s{background:rgba(45,212,191,.06);border-left:2px solid var(--teal)}
.ai-t{font-size:12px;line-height:1.4}
.ai-g{font-size:9px;font-family:var(--mono);color:var(--muted);white-space:nowrap;margin-top:2px}

/* MC BARS */
.mc-r{display:flex;align-items:center;gap:8px;margin-bottom:7px}
.mc-l{font-size:10px;font-family:var(--mono);color:var(--muted);width:78px}
.mc-t{flex:1;height:7px;background:rgba(255,255,255,.04);border-radius:4px;overflow:hidden}
.mc-f{height:100%;border-radius:4px;transition:width .8s cubic-bezier(.4,0,.2,1)}
.mc-p{font-size:10px;font-family:var(--mono);color:var(--muted);width:42px;text-align:right}

/* SPARKLINE */
.spark{display:flex;align-items:flex-end;gap:2px;height:36px}
.spark-b{flex:1;border-radius:2px 2px 0 0;min-height:2px}

/* MINI METRIC */
.mm{display:flex;justify-content:space-between;align-items:center;
  padding:8px 0;border-bottom:1px solid var(--border);font-size:12px}
.mm:last-child{border-bottom:none}
.mm-l{color:var(--muted);font-family:var(--mono);font-size:11px}
.mm-v{font-family:var(--mono);font-weight:700}

/* LOADING SPINNER */
.spin{display:inline-block;width:12px;height:12px;border:2px solid rgba(255,255,255,.15);
  border-top-color:var(--purple);border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* API DATA SECTION */
.api-note{font-size:10px;font-family:var(--mono);color:var(--muted);
  padding:10px 14px;border-top:1px solid var(--border);
  background:rgba(255,255,255,.01)}
</style>
</head>
<body>
<div class="shell">

<!-- TOPBAR -->
<header class="topbar">
  <div class="logo">Apuestas<em>Pro</em><small>v3.0</small></div>
  <div class="topbar-right">
    <span id="api-badge" class="api-status ok">API OK</span>
    <span class="live-pill"><span class="live-dot"></span>LIVE</span>
    <span class="clock" id="clock">--:--:--</span>
  </div>
</header>

<!-- SIDEBAR -->
<aside class="sidebar">
  <div class="nav-label">General</div>
  <button class="nav-btn on" onclick="go(this,'dashboard')"><span class="nav-icon">◈</span>Dashboard</button>

  <div class="nav-label">Loterías</div>
  <button class="nav-btn" onclick="go(this,'melate')"><span class="nav-icon">⬡</span>Melate / Loterías</button>

  <div class="nav-label">Deportes</div>
  <button class="nav-btn" onclick="go(this,'odds')"><span class="nav-icon">◉</span>Value Bets<span class="nav-badge nb-green">LIVE</span></button>
  <button class="nav-btn" onclick="go(this,'clv')"><span class="nav-icon">◎</span>CLV Tracker</button>

  <div class="nav-label">Análisis</div>
  <button class="nav-btn" onclick="go(this,'mc')"><span class="nav-icon">∿</span>Monte Carlo</button>
  <button class="nav-btn" onclick="go(this,'kelly')"><span class="nav-icon">◈</span>Kelly Pro</button>

  <div class="nav-label">Pronósticos</div>
  <button class="nav-btn" onclick="go(this,'progol')"><span class="nav-icon">⚽</span>Progol <span class="nav-badge nb-green">DC+ELO</span></button>
  <div class="nav-label">Sharp Money</div>
  <button class="nav-btn" onclick="go(this,'sharp')"><span class="nav-icon">⚡</span>Sharp Detector <span class="nav-badge nb-gold">PRO</span></button>
  <div class="nav-label">Sistema</div>
  <button class="nav-btn" onclick="go(this,'alertas')"><span class="nav-icon">◇</span>Alertas<span class="nav-badge nb-gold">4</span></button>
  <button class="nav-btn" onclick="go(this,'apidocs')"><span class="nav-icon">⊞</span>API Docs</button>
</aside>

<!-- MAIN -->
<main class="main">

<!-- DASHBOARD -->
<div id="s-dashboard" class="section on">
  <div class="ph"><div class="ph-title">Dashboard</div><div class="ph-sub">todos los módulos operativos · datos en tiempo real</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">Sorteos analizados</div><div class="sc-val" style="color:var(--purple2)">3,847</div><div class="sc-sub">Melate desde 1996</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Value bets hoy</div><div class="sc-val" style="color:var(--green)" id="d-vb">—</div><div class="sc-sub">Cargando...</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">Núm más caliente</div><div class="sc-val" style="color:var(--gold)" id="d-hot">—</div><div class="sc-sub" id="d-hot-sub">Cargando...</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--teal)"></div><div class="sc-lbl">Núm más frío</div><div class="sc-val" style="color:var(--teal)" id="d-cold">—</div><div class="sc-sub" id="d-cold-sub">Cargando...</div></div>
  </div>
  <div class="g2">
    <div class="panel">
      <div class="ph2"><span class="pt">Bankroll <span class="chip cp">Kelly</span></span></div>
      <div class="pb">
        <div class="mm"><span class="mm-l">Total</span><span class="mm-v" style="color:var(--purple2)">$5,000</span></div>
        <div class="mm"><span class="mm-l">En juego</span><span class="mm-v" style="color:var(--gold)">$320 (6.4%)</span></div>
        <div class="mm"><span class="mm-l">Disponible</span><span class="mm-v" style="color:var(--green)">$4,680</span></div>
        <div style="height:4px;background:rgba(255,255,255,.04);border-radius:2px;overflow:hidden;margin-top:12px">
          <div style="width:6.4%;height:100%;background:var(--gold);border-radius:2px"></div>
        </div>
      </div>
    </div>
    <div class="panel">
      <div class="ph2"><span class="pt">ROI últimas 2 semanas <span class="chip cg">+12.3%</span></span></div>
      <div class="pb">
        <div class="spark" id="spark"></div>
        <div style="display:flex;justify-content:space-between;font-size:9px;font-family:var(--mono);color:var(--muted);margin-top:6px"><span>−14d</span><span>Hoy</span></div>
      </div>
    </div>
  </div>
  <div class="panel">
    <div class="ph2"><span class="pt">Accesos rápidos</span></div>
    <div class="pb" style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px">
      <button class="btn btn-g" onclick="go(document.querySelectorAll('.nav-btn')[1],'melate')" style="flex-direction:column;gap:4px;padding:14px 8px"><span style="font-size:18px;color:var(--gold)">⬡</span><span style="font-size:11px">Melate</span></button>
      <button class="btn btn-g" onclick="go(document.querySelectorAll('.nav-btn')[2],'odds')"   style="flex-direction:column;gap:4px;padding:14px 8px"><span style="font-size:18px;color:var(--green)">◉</span><span style="font-size:11px">Value Bets</span></button>
      <button class="btn btn-g" onclick="go(document.querySelectorAll('.nav-btn')[5],'kelly')"  style="flex-direction:column;gap:4px;padding:14px 8px"><span style="font-size:18px;color:var(--purple2)">◈</span><span style="font-size:11px">Kelly Pro</span></button>
      <button class="btn btn-g" onclick="go(document.querySelectorAll('.nav-btn')[4],'mc')"     style="flex-direction:column;gap:4px;padding:14px 8px"><span style="font-size:18px;color:var(--teal)">∿</span><span style="font-size:11px">Monte Carlo</span></button>
    </div>
  </div>
</div>

<!-- MELATE -->
<div id="s-melate" class="section">
  <div class="ph"><div class="ph-title">Melate · Loterías</div><div class="ph-sub">análisis estadístico · histórico completo · Melate 6/56</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">Más frecuente</div><div class="sc-val" style="color:var(--gold)" id="m-hot">—</div><div class="sc-sub" id="m-hot-s">cargando API...</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--teal)"></div><div class="sc-lbl">Más frío</div><div class="sc-val" style="color:var(--teal)" id="m-cold">—</div><div class="sc-sub" id="m-cold-s">cargando API...</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">Prob. acertar 6/6</div><div class="sc-val" style="color:var(--purple2);font-size:15px">1:4,096,720</div><div class="sc-sub">0.0000244%</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Sorteos</div><div class="sc-val" style="color:var(--green)" id="m-total">—</div><div class="sc-sub">desde 1996</div></div>
  </div>
  <div class="g2">
    <div class="panel">
      <div class="ph2"><span class="pt">Frecuencias top 15 <span class="chip cp">API</span></span></div>
      <div class="pb" id="m-bars"><div style="color:var(--muted);font-size:12px;font-family:var(--mono)">Cargando desde API...</div></div>
    </div>
    <div class="panel">
      <div class="ph2"><span class="pt">Mapa de calor 1–56 <span class="chip cy">Heatmap</span></span></div>
      <div class="pb">
        <div class="hm" id="m-hm"></div>
        <div style="display:flex;align-items:center;gap:8px;margin-top:10px">
          <div style="flex:1;height:3px;background:linear-gradient(90deg,rgba(45,212,191,.5),rgba(124,109,250,.5),rgba(240,180,41,.6));border-radius:2px"></div>
          <span style="font-size:9px;font-family:var(--mono);color:var(--muted)">Frío → Caliente</span>
        </div>
      </div>
    </div>
  </div>
  <div class="panel">
    <div class="ph2">
      <span class="pt">Generador estadístico <span class="chip cg">ML</span></span>
      <div style="display:flex;gap:6px">
        <button class="btn btn-g" onclick="genCombs(1)" style="padding:5px 12px;font-size:11px">1 combo</button>
        <button class="btn btn-p" onclick="genCombs(5)" style="padding:5px 12px;font-size:11px">Generar 5</button>
      </div>
    </div>
    <div class="pb">
      <div class="pills">
        <button class="pill on" onclick="setM(this,'balanced')">Balanceado</button>
        <button class="pill" onclick="setM(this,'hot')">Calientes</button>
        <button class="pill" onclick="setM(this,'cold')">Fríos</button>
        <button class="pill" onclick="setM(this,'random')">Aleatorio</button>
      </div>
      <div id="gen-out"></div>
    </div>
  </div>
  <div class="g2">
    <div class="panel">
      <div class="ph2"><span class="pt">Calientes <span class="chip cy">Top 10</span></span></div>
      <div class="pb"><div class="balls" id="hot-b"></div></div>
    </div>
    <div class="panel">
      <div class="ph2"><span class="pt">Fríos <span class="chip ct">Top 10</span></span></div>
      <div class="pb"><div class="balls" id="cold-b"></div></div>
    </div>
  </div>
</div>

<!-- ODDS -->
<div id="s-odds" class="section">
  <div class="ph"><div class="ph-title">Value Bets</div><div class="ph-sub">detección automática · configura ODDS_API_KEY en Render para datos en tiempo real</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Value bets</div><div class="sc-val" style="color:var(--green)">4</div><div class="sc-sub">Detectados hoy</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">Mejor edge</div><div class="sc-val" style="color:var(--gold)">+10%</div><div class="sc-sub">Toluca vs Santos</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--teal)"></div><div class="sc-lbl">Arbitrajes</div><div class="sc-val" style="color:var(--teal)">2</div><div class="sc-sub">Garantizados</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">Casas monitoreadas</div><div class="sc-val" style="color:var(--purple2)">12</div><div class="sc-sub">Liga MX + int.</div></div>
  </div>
  <div class="panel">
    <div class="ph2"><span class="pt">Detector en vivo <span class="chip cg">LIVE</span></span><span id="vb-spin" class="spin"></span></div>
    <table class="tbl"><thead><tr><th>Partido</th><th>Resultado</th><th>Casa</th><th>Cuota</th><th>Edge</th><th>Señal</th></tr></thead><tbody id="vb-body"></tbody></table>
    <div class="api-note">Datos en tiempo real via /api/odds/value-bets · Configura ODDS_API_KEY en variables de entorno de Render</div>
  </div>
  <div class="panel">
    <div class="ph2"><span class="pt">Calculadora EV <span class="chip cp">Valor Esperado</span></span></div>
    <div class="pb">
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:12px">
        <div class="field"><label>Cuota decimal</label><input type="number" id="ev-o" value="2.10" step="0.01" oninput="calcEV()"></div>
        <div class="field"><label>Prob. real (%)</label><input type="number" id="ev-p" value="52" oninput="calcEV()"></div>
        <div class="field"><label>Apuesta ($)</label><input type="number" id="ev-s" value="100" step="10" oninput="calcEV()"></div>
      </div>
      <div id="ev-r"></div>
    </div>
  </div>
</div>

<!-- CLV -->
<div id="s-clv" class="section">
  <div class="ph"><div class="ph-title">CLV Tracker</div><div class="ph-sub">closing line value · métrica #1 de apostadores profesionales</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">CLV promedio</div><div class="sc-val" style="color:var(--green)">+2.4%</div><div class="sc-sub">Últimas 50 apuestas</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">% Beat CLV</div><div class="sc-val" style="color:var(--gold)">71%</div><div class="sc-sub">Benchmark pro: >55%</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">Sharp rating</div><div class="sc-val" style="color:var(--purple2)">A+</div><div class="sc-sub">Apostador profesional</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--teal)"></div><div class="sc-lbl">ROI proyectado</div><div class="sc-val" style="color:var(--teal)">+8.2%</div><div class="sc-sub">Largo plazo</div></div>
  </div>
  <div class="g2">
    <div class="panel">
      <div class="ph2"><span class="pt">Calcular CLV</span></div>
      <div class="pb">
        <div class="field"><label>Mi cuota apostada</label><input type="number" id="clv-i" value="2.10" step="0.01" oninput="calcCLV()"></div>
        <div class="field"><label>Cuota de cierre</label><input type="number" id="clv-c" value="1.85" step="0.01" oninput="calcCLV()"></div>
        <div id="clv-r" style="margin-top:8px"></div>
      </div>
    </div>
    <div class="panel">
      <div class="ph2"><span class="pt">¿Qué es CLV? <span class="chip cp">PRO</span></span></div>
      <div class="pb" style="font-size:12px;line-height:1.75;color:var(--muted)">
        <p style="margin-bottom:9px">Si apostaste <strong style="color:var(--purple2)">2.10</strong> y la línea cerró en <strong style="color:var(--red)">1.85</strong> → CLV <strong style="color:var(--green)">+13.5%</strong>.</p>
        <p style="margin-bottom:9px">El mercado confirmó tu apuesta antes de que empezara el partido. Calidad sobre resultado.</p>
        <p>Benchmark: <strong style="color:var(--gold)">≥55% con CLV positivo</strong> = edge real demostrado.</p>
      </div>
    </div>
  </div>
  <div class="panel">
    <div class="ph2"><span class="pt">Historial <span class="chip cg">Tracker</span></span></div>
    <table class="tbl"><thead><tr><th>Apuesta</th><th>Mi cuota</th><th>Cierre</th><th>CLV</th><th>Resultado</th></tr></thead><tbody id="clv-t"></tbody></table>
  </div>
</div>

<!-- MONTE CARLO -->
<div id="s-mc" class="section">
  <div class="ph"><div class="ph-title">Monte Carlo</div><div class="ph-sub">simulación de partidos · distribución Poisson · cuotas sin vig</div></div>
  <div class="panel">
    <div class="ph2"><span class="pt">Parámetros <span class="chip cp">Poisson</span></span></div>
    <div class="pb">
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:14px">
        <div class="field"><label>λ Local (goles esperados)</label><input type="number" id="mc-l" value="1.5" step="0.1"></div>
        <div class="field"><label>λ Visitante</label><input type="number" id="mc-v" value="1.1" step="0.1"></div>
        <div class="field"><label>Simulaciones</label>
          <select id="mc-n"><option value="1000">1,000</option><option value="5000">5,000</option><option value="10000" selected>10,000</option><option value="50000">50,000</option></select>
        </div>
      </div>
      <button class="btn btn-p" id="mc-btn" onclick="runMC()">Ejecutar 10,000 simulaciones</button>
    </div>
  </div>
  <div id="mc-out" style="display:none">
    <div class="sg" id="mc-sg"></div>
    <div class="panel">
      <div class="ph2"><span class="pt">Distribución de resultados <span class="chip ct">MC</span></span></div>
      <div class="pb" id="mc-bars"></div>
    </div>
  </div>
</div>

<!-- KELLY -->
<div id="s-kelly" class="section">
  <div class="ph"><div class="ph-title">Kelly Pro</div><div class="ph-sub">criterio de kelly · gestión óptima del bankroll</div></div>
  <div class="g2">
    <div class="panel">
      <div class="ph2"><span class="pt">Parámetros <span class="chip cp">Kelly</span></span></div>
      <div class="pb">
        <div class="field"><label>Bankroll ($)</label><input type="number" id="k-b" value="5000" oninput="calcKelly()"></div>
        <div class="field"><label>Cuota decimal</label><input type="number" id="k-o" value="2.10" step="0.01" oninput="calcKelly()"></div>
        <div class="field"><label>Probabilidad estimada (%)</label><input type="number" id="k-p" value="55" oninput="calcKelly()"></div>
        <div class="field"><label>Modelo</label>
          <select id="k-m" onchange="calcKelly()">
            <option value="1">Kelly completo</option>
            <option value="0.5" selected>Medio Kelly — recomendado</option>
            <option value="0.25">Cuarto Kelly — conservador</option>
            <option value="flat">Flat 2% fijo</option>
          </select>
        </div>
      </div>
    </div>
    <div class="panel">
      <div class="ph2"><span class="pt">Resultado</span></div>
      <div class="pb">
        <div class="k-big"><div class="k-amount" id="k-a" style="color:var(--green)">—</div><div class="k-lbl" id="k-l">configura los parámetros</div></div>
        <div class="k-rows" id="k-r"></div>
      </div>
    </div>
  </div>
</div>

<!-- ALERTAS -->
<div id="s-alertas" class="section">
  <div class="ph"><div class="ph-title">Alertas</div><div class="ph-sub">value bets · sharp money · rachas · sorteos</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">Urgentes</div><div class="sc-val" style="color:var(--gold)">4</div><div class="sc-sub">Acción inmediata</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Value bets</div><div class="sc-val" style="color:var(--green)">4</div><div class="sc-sub">Edge prom +6.8%</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">Sharp moves</div><div class="sc-val" style="color:var(--purple2)">3</div><div class="sc-sub">Últimas 2 horas</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--teal)"></div><div class="sc-lbl">Próximo sorteo</div><div class="sc-val" style="color:var(--teal)">Hoy</div><div class="sc-sub">Melate 21:00 CDMX</div></div>
  </div>
  <div class="panel">
    <div class="ph2"><span class="pt">Feed en tiempo real <span class="chip cg">LIVE</span></span></div>
    <div class="pb" id="afeed"></div>
  </div>
</div>

<!-- API DOCS -->
<div id="s-apidocs" class="section">
  <div class="ph"><div class="ph-title">API Docs</div><div class="ph-sub">documentación interactiva · FastAPI · OpenAPI 3.1</div></div>
  <div class="panel">
    <div class="ph2"><span class="pt">Swagger UI <span class="chip cp">OpenAPI</span></span></div>
    <div class="pb" style="text-align:center;padding:30px">
      <p style="color:var(--muted);font-size:13px;margin-bottom:16px">La documentación interactiva está disponible en:</p>
      <a href="/docs" target="_blank" class="btn btn-p" style="text-decoration:none;margin-right:8px">/docs — Swagger UI</a>
      <a href="/redoc" target="_blank" class="btn btn-g" style="text-decoration:none">/redoc — ReDoc</a>
    </div>
  </div>
</div>


<!-- PROGOL -->
<div id="s-progol" class="section">
  <div class="ph"><div class="ph-title">Progol · Pronósticos</div><div class="ph-sub">Dixon-Coles + ELO + Poisson · precisión 55-62% · datos API-Football</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Modelo</div><div class="sc-val" style="color:var(--green);font-size:14px">Dixon-Coles</div><div class="sc-sub">Estándar industria</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">ELO Rating</div><div class="sc-val" style="color:var(--purple2);font-size:14px">FiveThirtyEight</div><div class="sc-sub">Dinámico por forma</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">Precisión real</div><div class="sc-val" style="color:var(--gold)">55-62%</div><div class="sc-sub">Por partido</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--teal)"></div><div class="sc-lbl">xG fuente</div><div class="sc-val" style="color:var(--teal);font-size:14px">API-Football</div><div class="sc-sub">Configura key</div></div>
  </div>

  <div class="panel">
    <div class="ph2">
      <span class="pt">Jornada Progol <span class="chip cg">DC+ELO+Poisson</span></span>
      <button class="btn btn-p" onclick="loadProgol()" id="progol-btn" style="padding:5px 14px;font-size:11px">Cargar predicciones</button>
    </div>
    <div class="pb" id="progol-body">
      <p style="color:var(--muted);font-size:12px;font-family:var(--mono)">Pulsa "Cargar predicciones" para ver la jornada con los 3 modelos.</p>
    </div>
  </div>

  <div class="panel">
    <div class="ph2"><span class="pt">Predecir partido específico <span class="chip cp">Ensemble</span></span></div>
    <div class="pb">
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:10px;margin-bottom:12px">
        <div class="field"><label>Local</label><input type="text" id="p-home" value="Club América" placeholder="Equipo local"></div>
        <div class="field"><label>Visitante</label><input type="text" id="p-away" value="Guadalajara" placeholder="Equipo visitante"></div>
        <div class="field"><label>xG Local (opcional)</label><input type="number" id="p-xgh" placeholder="ej: 1.4" step="0.1"></div>
        <div class="field"><label>xG Visitante</label><input type="number" id="p-xga" placeholder="ej: 0.9" step="0.1"></div>
      </div>
      <button class="btn btn-p" onclick="predPartido()" style="margin-bottom:14px">Predecir con DC + ELO + Poisson</button>
      <div id="pred-result"></div>
    </div>
  </div>

  <div class="panel">
    <div class="ph2"><span class="pt">Ranking ELO equipos <span class="chip cp">ELO</span></span></div>
    <div class="pb" id="elo-ranking"><p style="color:var(--muted);font-size:12px;font-family:var(--mono)">Carga la jornada para ver el ranking.</p></div>
  </div>
</div>


<!-- SHARP MONEY -->
<div id="s-sharp" class="section">
  <div class="ph"><div class="ph-title">Sharp Money Detector</div><div class="ph-sub">RLM · Steam · Bet/Money Split · Line Freeze · Sharp Book Consensus</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">Precisión RLM</div><div class="sc-val" style="color:var(--gold)">58-63%</div><div class="sc-sub">vs 50% aleatorio</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">Steam window</div><div class="sc-val" style="color:var(--purple2)">30-120s</div><div class="sc-sub">Para apostar en línea vieja</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Score máximo</div><div class="sc-val" style="color:var(--green)">99/100</div><div class="sc-sub">Múltiples señales</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--teal)"></div><div class="sc-lbl">Indicadores</div><div class="sc-val" style="color:var(--teal)">6</div><div class="sc-sub">RLM+Steam+Split+Freeze+Timing+Consensus</div></div>
  </div>

  <div class="panel">
    <div class="ph2"><span class="pt">Analizador de partido <span class="chip cy">Sharp Score</span></span></div>
    <div class="pb">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div class="field"><label>Partido</label><input type="text" id="sh-partido" value="Club América vs Guadalajara"></div>
        <div class="field"><label>Días antes del partido</label><input type="number" id="sh-dias" value="2" min="0" max="7"></div>
        <div class="field"><label>Línea apertura</label><input type="number" id="sh-lap" value="2.20" step="0.01"></div>
        <div class="field"><label>Línea actual</label><input type="number" id="sh-lact" value="1.95" step="0.01"></div>
        <div class="field"><label>% boletos en Local</label><input type="number" id="sh-bol" value="28" min="0" max="100"></div>
        <div class="field"><label>% dinero en Local</label><input type="number" id="sh-din" value="64" min="0" max="100"></div>
      </div>
      <div style="margin-bottom:10px">
        <div style="font-size:10px;font-family:var(--mono);color:var(--muted);margin-bottom:4px">Líneas por casa (JSON opcional) — {"Pinnacle":1.95,"Bet365":2.15}</div>
        <input type="text" id="sh-casas" placeholder='{"Pinnacle":1.95,"Bookmaker":1.98,"Bet365":2.15,"Codere":2.18}' style="width:100%;padding:8px 11px;border-radius:7px;background:rgba(255,255,255,.04);border:1px solid var(--border2);color:var(--text);font-size:12px;font-family:var(--mono)">
      </div>
      <button class="btn btn-p" onclick="analizarSharp()" style="margin-bottom:14px">Detectar dinero sharp ⚡</button>
      <div id="sharp-result"></div>
    </div>
  </div>

  <div class="panel">
    <div class="ph2"><span class="pt">Guía de indicadores <span class="chip cp">PRO</span></span></div>
    <div class="pb">
      <table class="tbl">
        <thead><tr><th>Indicador</th><th>Qué significa</th><th>Confianza</th></tr></thead>
        <tbody>
          <tr><td style="font-weight:600;color:var(--gold)">RLM</td><td style="font-size:11px">La línea se mueve CONTRA el lado que tiene más apuestas públicas → sharps en el otro lado</td><td><span class="badge bv">65-85%</span></td></tr>
          <tr><td style="font-weight:600;color:var(--green)">Bet/Money Split</td><td style="font-size:11px">80% de boletos en un lado pero solo 35% del dinero → dinero grande de sharps en el otro</td><td><span class="badge bv">60-90%</span></td></tr>
          <tr><td style="font-weight:600;color:var(--red)">Steam Move</td><td style="font-size:11px">4+ casas cambian la línea en minutos sin noticia → sindicato apostando. Ventana: 30-120s</td><td><span class="badge bs2">78-92%</span></td></tr>
          <tr><td style="font-weight:600;color:var(--teal)">Line Freeze</td><td style="font-size:11px">70%+ del público en un lado pero la línea no se mueve → el libro protege a los sharps del otro lado</td><td><span class="badge bsh">80%</span></td></tr>
          <tr><td style="font-weight:600;color:var(--purple2)">Sharp Consensus</td><td style="font-size:11px">Pinnacle tiene línea diferente a Bet365/Codere → el mercado no incorporó info sharp aún</td><td><span class="badge bs2">70-88%</span></td></tr>
          <tr><td style="font-weight:600;color:var(--muted)">Timing</td><td style="font-size:11px">Movimiento lunes-martes = sharp. Viernes-domingo = público. Tarde = público acumulado</td><td><span class="badge bdim">75%</span></td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

</main>
</div>

<script>
// ── DATA LOCAL (fallback si API no responde) ─────────────────────────────
const OV={38:312,23:290,22:278,15:265,47:258,7:95,14:88,3:91,51:97,29:102}
const FREQ=Array.from({length:56},(_,i)=>{const n=i+1;return{n,f:OV[n]??Math.floor(Math.abs(Math.sin(n*7.3)*60)+155)}})
const SRT=[...FREQ].sort((a,b)=>b.f-a.f)
const HOT=SRT.slice(0,10).map(d=>d.n)
const COLD=[...FREQ].sort((a,b)=>a.f-b.f).slice(0,10).map(d=>d.n)
const MAXF=SRT[0].f,MINF=SRT[SRT.length-1].f

const VB_FB=[
  {p:'Chivas vs América',l:'Liga MX',r:'Local',c:'Bet365',o:2.10,e:8.4},
  {p:'Toluca vs Santos',l:'Liga MX',r:'Local',c:'Codere',o:2.00,e:10.0},
  {p:'Cruz Azul vs Pumas',l:'Liga MX',r:'Local',c:'1xBet',o:1.85,e:7.3},
  {p:'Tigres vs Monterrey',l:'Liga MX',r:'Empate',c:'Bet365',o:3.10,e:3.1},
]
const CLV_H=[
  {m:'Chivas ML',mi:2.10,cl:1.88,w:true},{m:'Cruz Azul -1',mi:1.95,cl:2.05,w:true},
  {m:'Tigres Over 2.5',mi:1.72,cl:1.65,w:false},{m:'América Empate',mi:3.40,cl:3.10,w:false},
  {m:'Santos ML',mi:2.80,cl:3.15,w:true},
]
const ALS=[
  {t:'w',x:'Value bet: Chivas ML · Edge +8.4% vs Bet365 · Kelly sugiere $180',g:'hace 3 min'},
  {t:'s',x:'Sharp money: América Over 2.5 — Reverse Line Movement activo',g:'hace 8 min'},
  {t:'g',x:'Arbitraje confirmado: Tigres vs Monterrey +3.4% garantizado',g:'hace 15 min'},
  {t:'w',x:'Value bet: Toluca ML · Edge +10.0% — STRONG VALUE',g:'hace 22 min'},
  {t:'g',x:'Número 7 en Melate: 68 sorteos sin salir (máx histórico: 84)',g:'hace 1h'},
  {t:'s',x:'Steam move: Cruz Azul -0.5 → -1.0 en 4 casas en 8 minutos',g:'hace 1.5h'},
  {t:'i',x:'Sorteo Melate esta noche 21:00 CDMX',g:'hace 2h'},
]

let genMode='balanced'
let apiFreq=null

// ── NAV ──────────────────────────────────────────────────────────────────
function go(btn,id){
  document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('on'))
  document.querySelectorAll('.section').forEach(s=>s.classList.remove('on'))
  btn.classList.add('on')
  document.getElementById('s-'+id).classList.add('on')
  if(id==='dashboard') initDash()
  if(id==='melate') initMelate()
  if(id==='odds'){renderVB();calcEV()}
  if(id==='clv'){calcCLV();renderCLVT()}
  if(id==='kelly') calcKelly()
  if(id==='alertas') renderAlerts()
}

// ── CLOCK ────────────────────────────────────────────────────────────────
setInterval(()=>{document.getElementById('clock').textContent=new Date().toLocaleTimeString('es-MX',{hour12:false})},1000)

// ── API CALL ─────────────────────────────────────────────────────────────
async function api(path){
  const r=await fetch(path)
  if(!r.ok) throw new Error(r.status)
  return r.json()
}

function setAPIStatus(ok){
  const b=document.getElementById('api-badge')
  b.className='api-status '+(ok?'ok':'err')
  b.textContent=ok?'API OK':'API Error'
}

// ── DASHBOARD INIT ────────────────────────────────────────────────────────
async function initDash(){
  // sparkline
  const d=[.3,.5,.4,.6,.45,.7,.55,.8,.6,.75,.5,.9,.7,.85]
  document.getElementById('spark').innerHTML=d.map(v=>`<div class="spark-b" style="height:${v*100}%;background:${v>.6?'var(--green)':v>.4?'var(--purple)':'var(--muted)'};opacity:.7"></div>`).join('')
  // load freq from API
  try{
    const data=await api('/api/melate/frecuencias?limite=500')
    setAPIStatus(true)
    if(data.calientes?.length){
      const h=data.calientes[0]
      document.getElementById('d-hot').textContent=h.numero
      document.getElementById('d-hot-sub').textContent=`${h.frecuencia_abs} apariciones`
      const c=data.frios[0]
      document.getElementById('d-cold').textContent=c.numero
      document.getElementById('d-cold-sub').textContent=`${c.frecuencia_abs} apariciones`
    }
    document.getElementById('d-vb').textContent='4'
  }catch(e){setAPIStatus(false)}
}

// ── MELATE ────────────────────────────────────────────────────────────────
async function initMelate(){
  // try API first
  let freq=null,calientes=HOT,frios=COLD,total=3847
  try{
    const data=await api('/api/melate/frecuencias?limite=500')
    setAPIStatus(true)
    freq=data.frecuencias
    apiFreq=freq
    calientes=data.calientes.slice(0,10).map(d=>d.numero)
    frios=data.frios.slice(0,10).map(d=>d.numero)
    total=data.sorteos_analizados
    const h=data.calientes[0],c=data.frios[0]
    document.getElementById('m-hot').textContent=h.numero
    document.getElementById('m-hot-s').textContent=`${h.frecuencia_abs} veces`
    document.getElementById('m-cold').textContent=c.numero
    document.getElementById('m-cold-s').textContent=`${c.frecuencia_abs} veces`
    document.getElementById('m-total').textContent=total.toLocaleString()
    // build freq array from API
    const fa=Object.entries(freq).map(([n,d])=>({n:parseInt(n),f:d.frecuencia_abs})).sort((a,b)=>b.f-a.f)
    renderBars(fa)
    renderHM(fa)
  }catch(e){
    setAPIStatus(false)
    document.getElementById('m-hot').textContent=SRT[0].n
    document.getElementById('m-hot-s').textContent=`${SRT[0].f} veces`
    document.getElementById('m-cold').textContent=SRT[SRT.length-1].n
    document.getElementById('m-cold-s').textContent=`${SRT[SRT.length-1].f} veces`
    document.getElementById('m-total').textContent='3,847'
    renderBars(SRT)
    renderHM(FREQ)
  }
  document.getElementById('hot-b').innerHTML=calientes.map(n=>`<div class="ball bh">${n}</div>`).join('')
  document.getElementById('cold-b').innerHTML=frios.map(n=>`<div class="ball bc">${n}</div>`).join('')
}

function renderBars(arr){
  const top=arr.slice(0,15),max=top[0].f
  document.getElementById('m-bars').innerHTML=top.map(d=>`
    <div class="fb">
      <span class="fb-l">${d.n}</span>
      <div class="fb-t"><div class="fb-f" style="width:${Math.round(d.f/max*100)}%;background:${d.f>280?'var(--gold)':d.f<110?'var(--teal)':'var(--purple)'}"></div></div>
      <span class="fb-v">${d.f}</span>
    </div>`).join('')
}

function renderHM(arr){
  const max=Math.max(...arr.map(d=>d.f)),min=Math.min(...arr.map(d=>d.f))
  // Sort by n for display
  const sorted=[...arr].sort((a,b)=>a.n-b.n)
  document.getElementById('m-hm').innerHTML=sorted.map(d=>{
    const p=(d.f-min)/(max-min)
    const r=Math.round(p*180+30),g=Math.round((1-p)*150+20)
    return`<div class="hm-c" title="${d.n}: ${d.f}×" style="background:rgba(${r},${g},40,.6);color:rgba(255,255,255,${p>.5?.9:.5})">${d.n}</div>`
  }).join('')
}

let gm='balanced'
function setM(btn,m){
  document.querySelectorAll('.pills .pill').forEach(p=>p.classList.remove('on'))
  btn.classList.add('on'); gm=m
}

function pick(n=6){
  const p=gm==='hot'?[...HOT,...SRT.slice(0,20).map(d=>d.n)]
    :gm==='cold'?[...COLD,...SRT.slice(-20).map(d=>d.n)]
    :Array.from({length:56},(_,i)=>i+1)
  const out=new Set()
  while(out.size<n) out.add(p[Math.floor(Math.random()*p.length)])
  return[...out].sort((a,b)=>a-b)
}

async function genCombs(n){
  let combis=[]
  try{
    const d=await api(`/api/melate/generar?modo=${gm}&cantidad=${n}`)
    if(d.combinaciones) combis=d.combinaciones.map(c=>c.numeros)
  }catch{}
  if(!combis.length) combis=Array.from({length:n},()=>pick())
  document.getElementById('gen-out').innerHTML=combis.map((nums,i)=>`
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;padding:9px 11px;background:rgba(255,255,255,.02);border-radius:7px">
      <span style="font-size:9px;font-family:var(--mono);color:var(--muted);width:14px">#${i+1}</span>
      <div class="balls">${nums.map(n=>`<div class="ball ${HOT.includes(n)?'bh':COLD.includes(n)?'bc':'bs'}">${n}</div>`).join('')}</div>
    </div>`).join('')
}

// ── VALUE BETS ────────────────────────────────────────────────────────────
async function renderVB(){
  document.getElementById('vb-spin').style.display='inline-block'
  let rows=VB_FB
  try{
    const d=await api('/api/odds/value-bets?deporte=soccer_mexico_ligamx&edge_minimo=2')
    setAPIStatus(true)
    if(d.value_bets?.length) rows=d.value_bets.map(v=>({p:v.partido,l:v.liga,r:v.resultado,c:v.casa,o:v.cuota,e:v.edge_porcentaje}))
  }catch{setAPIStatus(false)}
  document.getElementById('vb-spin').style.display='none'
  document.getElementById('vb-body').innerHTML=rows.map(d=>`
    <tr>
      <td><div style="font-weight:700;font-size:12px">${d.p}</div><div style="font-size:9px;font-family:var(--mono);color:var(--muted)">${d.l}</div></td>
      <td style="font-family:var(--mono);font-size:11px">${d.r}</td>
      <td style="font-family:var(--mono);font-size:10px;color:var(--muted)">${d.c}</td>
      <td style="font-family:var(--mono);font-weight:700;font-size:14px">${d.o}</td>
      <td><span class="badge ${d.e>7?'bs2':'bv'}">+${d.e}%</span></td>
      <td><span class="badge ${d.e>7?'bs2':'bv'}">${d.e>7?'STRONG VALUE':'VALUE BET'}</span></td>
    </tr>`).join('')
}

function calcEV(){
  const o=parseFloat(document.getElementById('ev-o')?.value)||2.10
  const p=parseFloat(document.getElementById('ev-p')?.value)/100||0.52
  const s=parseFloat(document.getElementById('ev-s')?.value)||100
  const ev=((o-1)*p-(1-p))*s
  const edge=((p*o-1)*100).toFixed(1)
  const el=document.getElementById('ev-r')
  if(!el) return
  el.innerHTML=`<div class="rbox ${ev>0?'rg':'rb'}">
    <strong>${ev>0?'VALUE BET — apostar':'Sin valor — no apostar'}</strong><br>
    Valor esperado: <strong>$${ev.toFixed(2)}</strong> · Edge: <strong>${edge}%</strong>
  </div>`
}

// ── CLV ───────────────────────────────────────────────────────────────────
function calcCLV(){
  const mi=parseFloat(document.getElementById('clv-i')?.value)||2.10
  const cl=parseFloat(document.getElementById('clv-c')?.value)||1.85
  const pos=mi>cl
  const pct=((mi/cl-1)*100).toFixed(1)
  const el=document.getElementById('clv-r')
  if(!el) return
  el.innerHTML=`<div class="rbox ${pos?'rg':'rb'}">
    <strong>CLV ${pos?'Positivo ✓':'Negativo ✗'}</strong><br>
    CLV: <strong>${pos?'+':''}${pct}%</strong> · 
    Prob. apostada: ${(1/mi*100).toFixed(2)}% → Cierre: ${(1/cl*100).toFixed(2)}%<br>
    ${pos?'El mercado confirmó tu análisis.':'El mercado se movió en tu contra.'}
  </div>`
}

function renderCLVT(){
  const el=document.getElementById('clv-t')
  if(!el) return
  el.innerHTML=CLV_H.map(b=>{
    const pos=b.mi>b.cl,pct=+((b.mi/b.cl-1)*100).toFixed(1)
    return`<tr>
      <td style="font-weight:600">${b.m}</td>
      <td style="font-family:var(--mono)">${b.mi}</td>
      <td style="font-family:var(--mono)">${b.cl}</td>
      <td><span class="badge ${pos?'bv':'bdim'}">${pos?'+':''}${pct}%</span></td>
      <td><span class="badge ${b.w?'bwin':'blose'}">${b.w?'Ganó':'Perdió'}</span></td>
    </tr>`
  }).join('')
}

// ── MONTE CARLO ───────────────────────────────────────────────────────────
function runMC(){
  const lL=parseFloat(document.getElementById('mc-l').value)||1.5
  const lV=parseFloat(document.getElementById('mc-v').value)||1.1
  const N=parseInt(document.getElementById('mc-n').value)||10000
  const btn=document.getElementById('mc-btn')
  btn.textContent=`Simulando ${N.toLocaleString()}…`; btn.disabled=true
  setTimeout(()=>{
    function poisson(l){let k=0,p=Math.exp(-l),q=1;while(q>p){k++;q*=Math.random()};return k-1}
    let h=0,d=0,a=0,gs=[]
    for(let i=0;i<N;i++){
      const gl=poisson(lL),gv=poisson(lV); gs.push(gl+gv)
      if(gl>gv)h++;else if(gl===gv)d++;else a++
    }
    const pL=h/N*100,pD=d/N*100,pV=a/N*100
    const avg=(gs.reduce((s,v)=>s+v,0)/N).toFixed(2)
    const o25=(gs.filter(g=>g>2.5).length/N*100).toFixed(1)
    const o15=(gs.filter(g=>g>1.5).length/N*100).toFixed(1)
    document.getElementById('mc-sg').innerHTML=[
      ['Local',pL.toFixed(1)+'%',(100/pL).toFixed(2),'var(--purple)'],
      ['Empate',pD.toFixed(1)+'%',(100/pD).toFixed(2),'var(--gold)'],
      ['Visitante',pV.toFixed(1)+'%',(100/pV).toFixed(2),'var(--teal)'],
      ['Over 2.5',o25+'%',`Avg: ${avg}g`,'var(--green)'],
    ].map(([l,v,s,c])=>`<div class="sc"><div class="sc-glow" style="background:${c}"></div>
      <div class="sc-lbl">${l}</div><div class="sc-val" style="color:${c}">${v}</div>
      <div class="sc-sub">${s}</div></div>`).join('')
    const mx=Math.max(pL,pD,pV)
    document.getElementById('mc-bars').innerHTML=`
      <div style="margin-bottom:10px;font-size:10px;font-family:var(--mono);color:var(--muted)">${N.toLocaleString()} simulaciones · λLocal=${lL} λVisitante=${lV} · Over 1.5: ${o15}%</div>
      ${[['Local',pL,'var(--purple)'],['Empate',pD,'var(--gold)'],['Visitante',pV,'var(--teal)']].map(([l,p,c])=>`
        <div class="mc-r"><span class="mc-l">${l}</span>
        <div class="mc-t"><div class="mc-f" style="width:${Math.round(p/mx*100)}%;background:${c}"></div></div>
        <span class="mc-p">${p.toFixed(1)}%</span></div>`).join('')}
      <div style="margin-top:10px;padding:9px 11px;background:rgba(255,255,255,.02);border-radius:7px;font-size:10px;font-family:var(--mono);color:var(--muted)">
        Compara cuotas justas (sin vig) con las de las casas para detectar value bets.
      </div>`
    document.getElementById('mc-out').style.display='block'
    btn.textContent=`Re-ejecutar ${N.toLocaleString()} simulaciones`; btn.disabled=false
  },50)
}

// ── KELLY ─────────────────────────────────────────────────────────────────
function calcKelly(){
  const bank=parseFloat(document.getElementById('k-b')?.value)||5000
  const odds=parseFloat(document.getElementById('k-o')?.value)||2.10
  const prob=parseFloat(document.getElementById('k-p')?.value)/100||0.55
  const mv=document.getElementById('k-m')?.value||'0.5'
  const b=odds-1,q=1-prob
  const kp=b>0?(b*prob-q)/b:0
  const frac=mv==='flat'?0.02:(parseFloat(mv)||0.5)
  const ka=mv==='flat'?0.02:kp*frac
  const ap=Math.max(0,bank*ka)
  const a=document.getElementById('k-a'),l=document.getElementById('k-l'),r=document.getElementById('k-r')
  if(!a) return
  if(kp<=0){
    a.style.color='var(--red)';a.textContent='NO BET'
    l.textContent='Kelly negativo — sin valor matemático'
    r.innerHTML='<div style="padding:9px;background:rgba(248,113,113,.07);border-radius:7px;font-size:11px;font-family:var(--mono);color:var(--red)">La cuota no tiene valor con esta probabilidad.</div>'
    return
  }
  a.style.color='var(--green)';a.textContent=`$${ap.toFixed(0)}`
  l.textContent='apuesta óptima sugerida'
  r.innerHTML=[
    ['Kelly puro',`${(kp*100).toFixed(2)}%`],
    ['Kelly ajustado',`${(ka*100).toFixed(2)}%`],
    ['% del bankroll',`${(ka*100).toFixed(1)}%`],
    ['ROI esperado',`+${((b*prob-q)*100).toFixed(1)}%`],
    ['Máx. 5% recomendado',`$${(bank*0.05).toFixed(0)}`],
  ].map(([l,v])=>`<div class="k-row"><span>${l}</span><span>${v}</span></div>`).join('')
}

// ── ALERTAS ───────────────────────────────────────────────────────────────
function renderAlerts(){
  document.getElementById('afeed').innerHTML=`<div class="afeed">${ALS.map(a=>`
    <div class="ai ${a.t}">
      <span class="ai-t">${a.x}</span>
      <span class="ai-g">${a.g}</span>
    </div>`).join('')}</div>`
}


// ── PROGOL ────────────────────────────────────────────────────────────────
async function loadProgol(){
  const btn=document.getElementById('progol-btn')
  const body=document.getElementById('progol-body')
  btn.textContent='Cargando...'; btn.disabled=true
  body.innerHTML='<div style="color:var(--muted);font-size:12px;font-family:var(--mono)">Ejecutando Dixon-Coles + ELO + Poisson...</div>'
  try{
    const d=await api('/api/progol/jornada')
    if(d.partidos){
      body.innerHTML=`
        <div style="font-size:10px;font-family:var(--mono);color:var(--muted);margin-bottom:12px">
          ${d.modelo} · Precisión esperada: ${d.precision_esperada} · ${d.usa_datos_reales?'Datos reales API-Football':'Historial demo — agrega API_FOOTBALL_KEY para datos reales'}
        </div>
        <table class="tbl">
          <thead><tr><th>#</th><th>Local</th><th>Visitante</th><th>1 (local)</th><th>X (empate)</th><th>2 (visita)</th><th>Pronóstico</th><th>Confianza</th></tr></thead>
          <tbody>${d.partidos.map(p=>`
            <tr>
              <td style="font-family:var(--mono);color:var(--muted)">${p.numero}</td>
              <td style="font-weight:700;font-size:12px">${p.local}</td>
              <td style="font-size:12px;color:var(--muted)">${p.visitante}</td>
              <td style="font-family:var(--mono)">${(p.local_prob||p.local*100||0).toFixed?((p.local||0)*100).toFixed(1)+'%':p.local}</td>
              <td style="font-family:var(--mono)">${((p.empate||0)*100).toFixed(1)}%</td>
              <td style="font-family:var(--mono)">${((p.visitante||0)*100).toFixed(1)}%</td>
              <td><span class="badge ${p.pronostico==='1'?'bv':p.pronostico==='X'?'bs2':'ba'}" style="font-size:12px;padding:3px 10px">${p.pronostico}</span></td>
              <td><span class="badge ${p.confianza_pct>55?'bv':p.confianza_pct>42?'bs2':'bdim'}">${p.confianza_pct}%</span></td>
            </tr>`).join('')}
          </tbody>
        </table>`
      // Ranking ELO
      if(d.ranking_elo){
        document.getElementById('elo-ranking').innerHTML=`
          <table class="tbl">
            <thead><tr><th>#</th><th>Equipo</th><th>ELO</th></tr></thead>
            <tbody>${d.ranking_elo.map((e,i)=>`
              <tr>
                <td style="font-family:var(--mono);color:var(--muted)">${i+1}</td>
                <td style="font-weight:600">${e.equipo}</td>
                <td style="font-family:var(--mono);color:var(--purple2)">${e.elo}</td>
              </tr>`).join('')}
            </tbody>
          </table>`
      }
    }
  }catch(e){
    body.innerHTML=`<div class="rbox rb"><strong>Error</strong><br>${e.message}</div>`
  }
  btn.textContent='Actualizar'; btn.disabled=false
}

async function predPartido(){
  const home=document.getElementById('p-home').value.trim()
  const away=document.getElementById('p-away').value.trim()
  const xgh=document.getElementById('p-xgh').value
  const xga=document.getElementById('p-xga').value
  const el=document.getElementById('pred-result')
  el.innerHTML='<div style="color:var(--muted);font-family:var(--mono);font-size:12px">Calculando Dixon-Coles + ELO + Poisson...</div>'
  try{
    let url=`/api/progol/partido?home=${encodeURIComponent(home)}&away=${encodeURIComponent(away)}`
    if(xgh) url+=`&xg_home=${xgh}`
    if(xga) url+=`&xg_away=${xga}`
    const d=await api(url)
    el.innerHTML=`
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:12px">
        ${[['Local (1)',d.local,'var(--green)'],['Empate (X)',d.empate,'var(--gold)'],['Visitante (2)',d.visitante,'var(--teal)']].map(([l,v,c])=>`
          <div class="sc"><div class="sc-glow" style="background:${c}"></div>
            <div class="sc-lbl">${l}</div>
            <div class="sc-val" style="color:${c}">${((v||0)*100).toFixed(1)}%</div>
            <div class="sc-sub">Cuota justa: ${l.includes('Local')?d.cuota_local:l.includes('Empate')?d.cuota_empate:d.cuota_visitante||'—'}</div>
          </div>`).join('')}
      </div>
      <div class="rbox ri" style="font-size:12px">
        <strong>Pronóstico: ${d.pronostico} — ${d.confianza_pct}% confianza — ${d.clasificacion}</strong><br>
        Modelo: ${d.modelo}<br>
        xG Local: ${d.xg_home} · xG Visitante: ${d.xg_away}<br>
        ${d.componentes?`DC: ${((d.componentes.dixon_coles?.local||0)*100).toFixed(1)}%/${((d.componentes.dixon_coles?.empate||0)*100).toFixed(1)}%/${((d.componentes.dixon_coles?.visitante||0)*100).toFixed(1)}% · ELO: ${((d.componentes.elo?.local||0)*100).toFixed(1)}%/${((d.componentes.elo?.empate||0)*100).toFixed(1)}%/${((d.componentes.elo?.visitante||0)*100).toFixed(1)}%`:''}
      </div>`
  }catch(e){
    el.innerHTML=`<div class="rbox rb"><strong>Error</strong><br>${e.message}</div>`
  }
}


// ── SHARP MONEY ───────────────────────────────────────────────────────────
async function analizarSharp(){
  const partido  = document.getElementById('sh-partido').value.trim()
  const lap      = document.getElementById('sh-lap').value
  const lact     = document.getElementById('sh-lact').value
  const bol      = document.getElementById('sh-bol').value
  const din      = document.getElementById('sh-din').value
  const dias     = document.getElementById('sh-dias').value
  const casasStr = document.getElementById('sh-casas').value.trim()
  const el       = document.getElementById('sharp-result')
  el.innerHTML = '<div style="color:var(--muted);font-family:var(--mono);font-size:12px">Analizando indicadores sharp...</div>'
  try{
    let url = `/api/sharp/analizar?partido=${encodeURIComponent(partido)}&linea_apertura=${lap}&linea_actual=${lact}&pct_boletos_local=${bol}&pct_dinero_local=${din}&dias_antes=${dias}`
    if(casasStr) url += `&lineas_casas=${encodeURIComponent(casasStr)}`
    const d = await api(url)
    const sc = d.score_sharp
    const scoreColor = sc.score>=85?'var(--green)':sc.score>=70?'var(--gold)':sc.score>=55?'var(--accent2)':'var(--red)'
    el.innerHTML = `
      <div style="display:grid;grid-template-columns:120px 1fr;gap:16px;margin-bottom:14px;align-items:center">
        <div style="text-align:center">
          <div style="font-size:52px;font-weight:800;color:${scoreColor};letter-spacing:-2px;line-height:1">${sc.score}</div>
          <div style="font-size:10px;font-family:var(--mono);color:var(--muted)">/ 100 sharp score</div>
        </div>
        <div>
          <div style="font-size:14px;font-weight:700;color:${scoreColor};margin-bottom:4px">${sc.clasificacion}</div>
          <div style="font-size:12px;color:var(--muted);margin-bottom:8px">${sc.recomendacion}</div>
          <div style="font-size:11px;font-family:var(--mono);color:var(--muted)">${sc.n_señales_detectadas} de ${sc.n_señales_totales} indicadores activos</div>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:6px">
        ${sc.señales_activas.map(s=>`
          <div style="padding:9px 12px;background:rgba(255,255,255,.02);border-radius:7px;border-left:2px solid ${s.confianza>=80?'var(--green)':s.confianza>=65?'var(--gold)':'var(--muted)'}">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px">
              <span style="font-size:11px;font-weight:600;color:var(--text)">${s.tipo}</span>
              <span class="badge ${s.confianza>=80?'bv':s.confianza>=65?'bs2':'bdim'}">${s.confianza}% conf.</span>
            </div>
            <div style="font-size:11px;font-family:var(--mono);color:var(--muted)">${s.señal}</div>
          </div>`).join('')}
      </div>`
  }catch(e){
    el.innerHTML = `<div class="rbox rb"><strong>Error</strong><br>${e.message}</div>`
  }
}

// ── INIT ─────────────────────────────────────────────────────────────────
initDash()
calcEV()
calcCLV()
renderCLVT()
calcKelly()
renderVB()
renderAlerts()
</script>
</body>
</html>
"""
