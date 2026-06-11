HTML = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ApuestasPro â€” Sistema Profesional #1</title>
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
::-webkit-scrollbar{width:3px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--dim);border-radius:2px}

/* LAYOUT */
.shell{display:grid;grid-template-columns:220px 1fr;grid-template-rows:52px 1fr;height:100vh}

/* TOPBAR */
.topbar{grid-column:1/-1;display:flex;align-items:center;justify-content:space-between;padding:0 22px;border-bottom:1px solid var(--border);background:var(--bg);z-index:10}
.logo{font-size:18px;font-weight:800;letter-spacing:-.5px}
.logo em{color:var(--purple);font-style:normal}
.logo small{font-size:10px;font-family:var(--mono);color:var(--muted);margin-left:6px;font-weight:400}
.topbar-right{display:flex;align-items:center;gap:14px}
.live-pill{display:flex;align-items:center;gap:5px;font-size:10px;font-family:var(--mono);color:var(--green);background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.2);padding:3px 9px;border-radius:20px}
.live-dot{width:5px;height:5px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.clock{font-family:var(--mono);font-size:12px;color:var(--muted)}
.api-badge{font-size:10px;font-family:var(--mono);padding:3px 8px;border-radius:4px;cursor:default}
.api-ok{background:rgba(52,211,153,.08);color:var(--green);border:1px solid rgba(52,211,153,.15)}
.api-err{background:rgba(248,113,113,.08);color:var(--red);border:1px solid rgba(248,113,113,.15)}

/* SIDEBAR */
.sidebar{background:var(--bg);border-right:1px solid var(--border);overflow-y:auto;padding:10px 0;display:flex;flex-direction:column}
.nav-label{font-size:9px;font-family:var(--mono);color:var(--dim);letter-spacing:2px;text-transform:uppercase;padding:14px 16px 4px}
.nav-btn{display:flex;align-items:center;gap:9px;padding:9px 16px;font-size:12px;cursor:pointer;color:var(--muted);background:none;border:none;width:100%;text-align:left;transition:all .15s;position:relative;font-family:var(--ui)}
.nav-btn:hover{color:var(--text);background:rgba(255,255,255,.025)}
.nav-btn.on{color:var(--text);background:rgba(124,109,250,.08)}
.nav-btn.on::before{content:'';position:absolute;left:0;top:5px;bottom:5px;width:2px;background:var(--purple);border-radius:2px}
.nav-icon{width:16px;text-align:center;font-size:13px;flex-shrink:0}
.nb{margin-left:auto;font-size:9px;font-family:var(--mono);padding:1px 5px;border-radius:3px}
.nb-green{background:rgba(52,211,153,.1);color:var(--green)}
.nb-gold{background:rgba(240,180,41,.12);color:var(--gold)}
.nb-red{background:rgba(248,113,113,.1);color:var(--red)}

/* MAIN */
.main{overflow-y:auto;background:var(--bg2);padding:24px}
.section{display:none}
.section.on{display:block;animation:fu .22s ease}
@keyframes fu{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:translateY(0)}}

/* PAGE HEADER */
.ph{margin-bottom:20px}
.ph-title{font-size:22px;font-weight:800;letter-spacing:-.5px;margin-bottom:3px}
.ph-sub{font-size:11px;font-family:var(--mono);color:var(--muted)}

/* STAT CARDS */
.sg{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:16px}
.sg3{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px}
.sg2{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:16px}
.sc{background:var(--bg3);border:1px solid var(--border);border-radius:10px;padding:14px 16px;position:relative;overflow:hidden}
.sc-glow{position:absolute;top:-20px;right:-20px;width:70px;height:70px;border-radius:50%;filter:blur(22px);opacity:.22}
.sc-lbl{font-size:10px;font-family:var(--mono);color:var(--muted);margin-bottom:7px}
.sc-val{font-size:24px;font-weight:800;letter-spacing:-1px;line-height:1}
.sc-sub{font-size:10px;font-family:var(--mono);color:var(--muted);margin-top:5px}

/* PANEL */
.panel{background:var(--bg3);border:1px solid var(--border);border-radius:10px;margin-bottom:14px;overflow:hidden}
.ph2{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--border)}
.pt{font-size:12px;font-weight:700;display:flex;align-items:center;gap:7px}
.pb{padding:16px}
.chip{font-size:9px;font-family:var(--mono);padding:2px 6px;border-radius:3px;font-weight:500}
.cp{background:rgba(124,109,250,.15);color:var(--purple2)}
.cg{background:rgba(52,211,153,.1);color:var(--green)}
.ct{background:rgba(45,212,191,.1);color:var(--teal)}
.cy{background:rgba(240,180,41,.1);color:var(--gold)}
.cr{background:rgba(248,113,113,.1);color:var(--red)}

/* GRID */
.g2{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px}
.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:14px}

/* BALLS */
.balls{display:flex;flex-wrap:wrap;gap:5px}
.ball{width:32px;height:32px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;font-family:var(--mono);flex-shrink:0;transition:transform .12s;cursor:default}
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
.hm-c{aspect-ratio:1;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:8px;font-family:var(--mono);font-weight:600;cursor:default;transition:transform .1s}
.hm-c:hover{transform:scale(1.2);z-index:2;position:relative}

/* TABLE */
.tbl{width:100%;border-collapse:collapse;font-size:12px}
.tbl th{font-size:9px;font-family:var(--mono);color:var(--muted);text-align:left;padding:8px 12px;border-bottom:1px solid var(--border);letter-spacing:1.5px;text-transform:uppercase;font-weight:500}
.tbl td{padding:10px 12px;border-bottom:1px solid var(--border);vertical-align:middle}
.tbl tr:last-child td{border-bottom:none}
.tbl tr:hover td{background:rgba(255,255,255,.02)}

/* BADGES */
.badge{display:inline-block;font-size:9px;font-family:var(--mono);padding:2px 6px;border-radius:3px;font-weight:600}
.bv{background:rgba(52,211,153,.1);color:var(--green);border:1px solid rgba(52,211,153,.2)}
.bs2{background:rgba(240,180,41,.1);color:var(--gold);border:1px solid rgba(240,180,41,.2)}
.ba{background:rgba(45,212,191,.1);color:var(--teal);border:1px solid rgba(45,212,191,.2)}
.bsh{background:rgba(124,109,250,.1);color:var(--purple2);border:1px solid rgba(124,109,250,.2)}
.bdim{background:rgba(255,255,255,.04);color:var(--muted)}
.bwin{background:rgba(52,211,153,.1);color:var(--green)}
.blose{background:rgba(248,113,113,.1);color:var(--red)}
.hot{background:rgba(248,113,113,.1);color:var(--red);border:1px solid rgba(248,113,113,.2)}

/* INPUTS */
.field{margin-bottom:11px}
.field label{display:block;font-size:10px;font-family:var(--mono);color:var(--muted);margin-bottom:4px;letter-spacing:.5px}
.field input,.field select{width:100%;padding:8px 11px;border-radius:7px;background:rgba(255,255,255,.04);border:1px solid var(--border2);color:var(--text);font-size:12px;font-family:var(--ui);transition:border-color .15s}
.field input:focus,.field select:focus{outline:none;border-color:var(--purple)}
.field select option{background:#111}

/* BUTTONS */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;padding:8px 16px;border-radius:7px;font-size:12px;font-weight:700;cursor:pointer;border:none;transition:all .15s;font-family:var(--ui)}
.btn-p{background:var(--purple);color:#fff}
.btn-p:hover{background:#9585ff;transform:translateY(-1px)}
.btn-g{background:rgba(255,255,255,.05);color:var(--text);border:1px solid var(--border2)}
.btn-g:hover{background:rgba(255,255,255,.09)}
.btn:disabled{opacity:.4;cursor:not-allowed!important;transform:none!important}

/* PILLS */
.pills{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:14px}
.pill{padding:4px 12px;border-radius:20px;border:1px solid var(--border2);font-size:11px;cursor:pointer;background:transparent;color:var(--muted);font-family:var(--ui);transition:all .15s}
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

/* KELLY MODAL */
.k-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:999;align-items:center;justify-content:center}
.k-overlay.on{display:flex}
.k-modal{background:var(--bg3);border:1px solid var(--border);border-radius:14px;width:450px;max-width:92vw;padding:24px;position:relative;max-height:90vh;overflow-y:auto}
.k-close{position:absolute;top:12px;right:14px;background:none;border:none;color:var(--muted);font-size:20px;cursor:pointer;font-family:var(--ui);line-height:1}
.k-close:hover{color:var(--text)}
.btn-kelly{background:rgba(124,109,250,.12);border:1px solid rgba(124,109,250,.25);color:var(--purple2);cursor:pointer;font-size:14px;padding:3px 8px;border-radius:5px;transition:all .15s}
.btn-kelly:hover{background:rgba(124,109,250,.25)}

/* ALERTS */
.afeed{display:flex;flex-direction:column;gap:7px}
.ai{display:flex;justify-content:space-between;align-items:flex-start;padding:10px 13px;border-radius:8px;gap:10px}
.ai.w{background:rgba(240,180,41,.06);border-left:2px solid var(--gold)}
.ai.g{background:rgba(52,211,153,.06);border-left:2px solid var(--green)}
.ai.i{background:rgba(124,109,250,.06);border-left:2px solid var(--purple)}
.ai.s{background:rgba(45,212,191,.06);border-left:2px solid var(--teal)}
.ai.r{background:rgba(248,113,113,.06);border-left:2px solid var(--red)}
.ai-t{font-size:12px;line-height:1.4}
.ai-g{font-size:9px;font-family:var(--mono);color:var(--muted);white-space:nowrap;margin-top:2px}

/* SPARKLINE */
.spark{display:flex;align-items:flex-end;gap:2px;height:36px}
.spark-b{flex:1;border-radius:2px 2px 0 0;min-height:2px}

/* MINI METRIC */
.mm{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--border);font-size:12px}
.mm:last-child{border-bottom:none}
.mm-l{color:var(--muted);font-family:var(--mono);font-size:11px}
.mm-v{font-family:var(--mono);font-weight:700}

/* PROGOL TABLE */
.prog-row{display:grid;grid-template-columns:28px 1fr auto auto auto;gap:8px;align-items:center;padding:9px 12px;border-bottom:1px solid var(--border);font-size:12px}
.prog-row:last-child{border-bottom:none}
.prog-row:hover{background:rgba(255,255,255,.02)}
.prog-num{font-family:var(--mono);color:var(--muted);font-size:10px}
.prog-match{font-weight:600}
.prog-liga{font-size:10px;color:var(--muted);font-family:var(--mono)}
.prog-probs{display:flex;gap:4px;font-family:var(--mono);font-size:11px}
.prob-box{padding:2px 6px;border-radius:4px;background:rgba(255,255,255,.04)}
.prob-box.best{background:rgba(124,109,250,.15);color:var(--purple2);font-weight:700}
.prog-pick{text-align:center}

/* SHARP SCORE */
.score-ring{width:80px;height:80px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;border:3px solid}
.score-num{font-size:22px;font-weight:800;letter-spacing:-1px}
.score-lbl{font-size:8px;font-family:var(--mono);color:var(--muted)}

/* CLV BAR */
.clv-bar{height:5px;border-radius:3px;margin-top:3px}

/* LOADING */
.loading{display:flex;gap:4px;align-items:center;padding:12px;color:var(--muted);font-family:var(--mono);font-size:12px}
.dot{width:5px;height:5px;border-radius:50%;background:var(--muted);animation:bk 1.2s infinite}
.dot:nth-child(2){animation-delay:.2s}.dot:nth-child(3){animation-delay:.4s}
@keyframes bk{0%,80%,100%{opacity:.2}40%{opacity:1}}
.spin{display:inline-block;width:10px;height:10px;border:2px solid rgba(255,255,255,.15);border-top-color:var(--purple);border-radius:50%;animation:sp .6s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="shell">

<header class="topbar">
  <div class="logo">Apuestas<em>Pro</em><small>v4.3</small></div>
  <div class="topbar-right">
    <a href="/logout" style="font-size:10px;font-family:var(--mono);color:var(--muted);text-decoration:none;padding:3px 9px;border:1px solid var(--border2);border-radius:4px;transition:all .15s" onmouseover="this.style.color='var(--text)'" onmouseout="this.style.color='var(--muted)'">Salir</a>
    <span id="api-badge" class="api-badge api-ok">API OK</span>
    <span class="live-pill"><span class="live-dot"></span>LIVE</span>
    <span class="clock" id="clock">--:--:--</span>
  </div>
</header>

<aside class="sidebar">
  <div class="nav-label">General</div>
  <button class="nav-btn on" onclick="go(this,'dashboard')"><span class="nav-icon">â—ˆ</span>Dashboard</button>

  <div class="nav-label">LoterÃ­as</div>

  <div class="nav-label">FÃºtbol</div>
  <button class="nav-btn" onclick="go(this,'progol')"><span class="nav-icon">âš½</span>Progol <span class="nb nb-green">DC+ELO</span></button>
  <button class="nav-btn" onclick="go(this,'partido')"><span class="nav-icon">ðŸ”¬</span>Partido Completo</button>

  <div class="nav-label">Apuestas</div>
  <button class="nav-btn" onclick="go(this,'odds')"><span class="nav-icon">â—‰</span>Value Bets <span class="nb nb-green">LIVE</span></button>
  <button class="nav-btn" onclick="go(this,'valuepro')"><span class="nav-icon">ðŸ’Ž</span>Value Pro <span class="nb nb-gold">â‚¬</span></button>
  <button class="nav-btn" onclick="go(this,'sharp')"><span class="nav-icon">âš¡</span>Sharp Money <span class="nb nb-gold">PRO</span></button>
  <button class="nav-btn" onclick="go(this,'clv')"><span class="nav-icon">â—Ž</span>CLV Tracker</button>
  <button class="nav-btn" onclick="go(this,'kelly')"><span class="nav-icon">â—ˆ</span>Kelly Pro</button>

  <div class="nav-label">AnÃ¡lisis</div>
  <button class="nav-btn" onclick="go(this,'mc')"><span class="nav-icon">âˆ¿</span>Monte Carlo</button>
  <button class="nav-btn" onclick="go(this,'nlp')"><span class="nav-icon">ðŸ“¡</span>NLP Â· Lesiones <span class="nb nb-red">EDGE</span></button>
  <button class="nav-btn" onclick="go(this,'backtest')"><span class="nav-icon">ðŸ“Š</span>Backtesting</button>

  <div class="nav-label">Nuevas funciones</div>
  <button class="nav-btn" onclick="go(this,'bankroll')"><span class="nav-icon">ðŸ’°</span>Bankroll Tracker <span class="nb nb-green">NEW</span></button>
  <button class="nav-btn" onclick="go(this,'mercados')"><span class="nav-icon">ðŸ“ˆ</span>Mercados Extra <span class="nb nb-green">NEW</span></button>
  <button class="nav-btn" onclick="go(this,'hedge')"><span class="nav-icon">ðŸ›¡</span>Hedge Â· Arb <span class="nb nb-gold">NEW</span></button>
  <button class="nav-btn" onclick="go(this,'progolopt')"><span class="nav-icon">ðŸŽ¯</span>Optimizador Progol <span class="nb nb-gold">NEW</span></button>
  <button class="nav-btn" onclick="go(this,'mlmodel')"><span class="nav-icon">ðŸ¤–</span>ML Model <span class="nb nb-green">NEW</span></button>
  <button class="nav-btn" onclick="go(this,'ligas')"><span class="nav-icon">ðŸŒ</span>Multi-Liga <span class="nb nb-green">NEW</span></button>

  <button class="nav-btn" onclick="go(this,'cuentas')"><span class="nav-icon">ðŸ¦</span>Cuentas & Camuflaje <span class="nb nb-red">NEW</span></button>

  <div class="nav-label">Sistema</div>
  <button class="nav-btn" onclick="go(this,'alertas')"><span class="nav-icon">â—‡</span>Alertas <span class="nb nb-gold">4</span></button>
</aside>

<main class="main">

<div id="s-dashboard" class="section on">
  <div class="ph"><div class="ph-title">Dashboard</div><div class="ph-sub" id="dash-sub">cargando datos en tiempo real...</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">Value bets activos</div><div class="sc-val" style="color:var(--green)" id="dash-vb-count">â€”</div><div class="sc-sub" id="dash-vb-edge">cargando...</div></div>
  </div>
  <div class="g2">
    <div class="panel">
      <div class="ph2"><span class="pt">Jornada Progol â€” prÃ³ximos partidos <span class="chip cp">DC+ELO</span></span></div>
      <div id="dash-progol"><div class="loading"><div class="dot"></div><div class="dot"></div><div class="dot"></div>Cargando jornada...</div></div>
    </div>
    <div class="panel">
      <div class="ph2"><span class="pt">Value Bets en vivo <span class="chip cg">LIVE</span></span></div>
      <div id="dash-vb"><div class="loading"><div class="dot"></div><div class="dot"></div><div class="dot"></div>Cargando odds...</div></div>
    </div>
  </div>
  <div class="g2">
    <div class="panel">
      <div class="ph2"><span class="pt">Alertas recientes <span class="chip cy">Feed</span></span></div>
      <div class="pb" id="dash-alertas"></div>
    </div>
    <div class="panel">
      <div class="ph2"><span class="pt">Accesos rÃ¡pidos</span></div>
      <div class="pb" style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
        <button class="btn btn-g" onclick="go(document.querySelector('[onclick*=progol]'),'progol')" style="flex-direction:column;gap:4px;padding:14px 8px"><span style="font-size:18px;color:var(--green)">âš½</span><span style="font-size:11px">Progol DC+ELO</span></button>
        <button class="btn btn-g" onclick="go(document.querySelector('[onclick*=sharp]'),'sharp')" style="flex-direction:column;gap:4px;padding:14px 8px"><span style="font-size:18px;color:var(--gold)">âš¡</span><span style="font-size:11px">Sharp Money</span></button>
        <button class="btn btn-g" onclick="go(document.querySelector('[onclick*=nlp]'),'nlp')" style="flex-direction:column;gap:4px;padding:14px 8px"><span style="font-size:18px;color:var(--red)">ðŸ“¡</span><span style="font-size:11px">NLP Lesiones</span></button>
      </div>
    </div>
  </div>
</div>


<div id="s-progol" class="section">
  <div class="ph"><div class="ph-title">Progol Â· Jornada</div><div class="ph-sub">Dixon-Coles 50% + ELO 30% + Poisson 20% Â· precisiÃ³n 55-62% Â· datos reales ESPN</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Modelo</div><div class="sc-val" style="color:var(--green);font-size:13px">Dixon-Coles</div><div class="sc-sub">EstÃ¡ndar industria</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">ELO Rating</div><div class="sc-val" style="color:var(--purple2);font-size:13px">FiveThirtyEight</div><div class="sc-sub">DinÃ¡mico por forma</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">PrecisiÃ³n real</div><div class="sc-val" style="color:var(--gold)">55-62%</div><div class="sc-sub">Por partido</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--teal)"></div><div class="sc-lbl">Fuente datos</div><div class="sc-val" style="color:var(--teal);font-size:13px">ESPN</div><div class="sc-sub">Temporada actual real</div></div>
  </div>
  <div class="panel">
    <div class="ph2">
      <span class="pt">Predicciones jornada <span class="chip cg">DC+ELO+Poisson</span></span>
      <button class="btn btn-p" onclick="loadProgol()" id="prog-btn" style="padding:5px 14px;font-size:11px">Cargar jornada</button>
    </div>
    <div id="prog-body"><div class="loading"><div class="dot"></div><div class="dot"></div><div class="dot"></div>Pulsa "Cargar jornada"</div></div>
  </div>
  <div class="g2">
    <div class="panel">
      <div class="ph2"><span class="pt">Ranking ELO <span class="chip cp">ELO</span></span></div>
      <div class="pb" id="elo-rank"><p style="color:var(--muted);font-size:12px;font-family:var(--mono)">Carga la jornada para ver el ranking.</p></div>
    </div>
    <div class="panel">
      <div class="ph2"><span class="pt">Ranking Dixon-Coles <span class="chip ct">DC</span></span></div>
      <div class="pb" id="dc-rank"><p style="color:var(--muted);font-size:12px;font-family:var(--mono)">Carga la jornada para ver el ranking.</p></div>
    </div>
  </div>
</div>

<div id="s-partido" class="section">
  <div class="ph"><div class="ph-title">Partido Completo</div><div class="ph-sub">DC + ELO + Poisson + Lesiones + H2H + Ãrbitro + Clima + Importancia</div></div>
  <div class="panel">
    <div class="ph2"><span class="pt">Configurar partido <span class="chip cp">Todos los features</span></span></div>
    <div class="pb">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div class="field"><label>Equipo local</label><input type="text" id="p-home" value="Club AmÃ©rica"></div>
        <div class="field"><label>Equipo visitante</label><input type="text" id="p-away" value="Guadalajara"></div>
        <div class="field"><label>Ãrbitro</label>
          <select id="p-arb">
            <option value="">-- Sin datos --</option>
            <option value="Fernando HernÃ¡ndez">Fernando HernÃ¡ndez (estricto)</option>
            <option value="CÃ©sar Ramos">CÃ©sar Ramos (permisivo)</option>
            <option value="Adonai Escobedo">Adonai Escobedo (muy estricto)</option>
            <option value="Diego MontaÃ±o">Diego MontaÃ±o (neutral)</option>
            <option value="Marco Antonio Ortiz">Marco Antonio Ortiz (permisivo)</option>
          </select>
        </div>
        <div class="field"><label>Ciudad del estadio</label><input type="text" id="p-ciudad" placeholder="ej: Guadalajara"></div>
        <div class="field"><label>PosiciÃ³n local en tabla</label><input type="number" id="p-pos-l" value="5" min="1" max="18"></div>
        <div class="field"><label>PosiciÃ³n visitante en tabla</label><input type="number" id="p-pos-v" value="8" min="1" max="18"></div>
        <div class="field"><label>Jornada #</label><input type="number" id="p-jornada" value="14" min="1" max="18"></div>
        <div class="field"><label>Lesiones local (JSON)</label><input type="text" id="p-les-l" placeholder="[]"></div>
        <div class="field"><label>Lesiones visitante (JSON)</label><input type="text" id="p-les-v" placeholder='[{"posicion":"Attacker","titular":true}]'></div>
      </div>
      <button class="btn btn-p" onclick="predPartidoCompleto()" style="margin-bottom:14px">Predecir con TODOS los features â†—</button>
      <div id="pred-result"></div>
    </div>
  </div>
</div>

<div id="s-odds" class="section">
  <div class="ph"><div class="ph-title">Value Bets</div><div class="ph-sub">detecciÃ³n automÃ¡tica Â· configura ODDS_API_KEY en Render para datos en tiempo real</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Value bets activos</div><div class="sc-val" style="color:var(--green)" id="vb-count">â€”</div><div class="sc-sub" id="vb-edge">cargando...</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">Mejor edge</div><div class="sc-val" style="color:var(--gold)" id="vb-best">â€”</div><div class="sc-sub">Detectado hoy</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--teal)"></div><div class="sc-lbl">Arbitrajes</div><div class="sc-val" style="color:var(--teal)">2</div><div class="sc-sub">Garantizados</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">Casas monitoreadas</div><div class="sc-val" style="color:var(--purple2)">12</div><div class="sc-sub">Mercados multi-deporte</div></div>
  </div>
  <div class="panel">
    <div class="ph2">
      <span class="pt">Detector en vivo <span class="chip cg">LIVE</span></span>
      <div style="display:flex;gap:8px;align-items:center">
        <select id="sp-sel" style="padding:5px 8px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid var(--border2);color:var(--text);font-size:12px">
          <optgroup label="FÃºtbol" style="background:#111">
            <option value="soccer_fifa_world_cup">Copa Mundial FIFA 2026</option>
            <option value="soccer_mexico_ligamx">Liga MX</option>
            <option value="soccer_uefa_champs_league">Champions League</option>
          </optgroup>
          <optgroup label="Deportes Americanos" style="background:#111">
            <option value="americanfootball_nfl">NFL</option>
            <option value="basketball_nba">NBA</option>
            <option value="baseball_mlb">BÃ©isbol (MLB)</option>
            <option value="basketball_ncaab">NCAAB (Baloncesto Universitario)</option>
          </optgroup>
          <optgroup label="Deportes Binarios" style="background:#111">
            <option value="tennis_atp">Tenis Profesional (ATP)</option>
            <option value="tennis_wta">Tenis Femenil (WTA)</option>
          </optgroup>
          <optgroup label="Esports" style="background:#111">
            <option value="esports_csgo">CS:GO</option>
            <option value="esports_league_of_legends">League of Legends</option>
          </optgroup>
        </select>
        <button class="btn btn-p" onclick="loadVB()" style="padding:5px 12px;font-size:11px">Actualizar</button>
      </div>
    </div>
    <table class="tbl"><thead><tr><th>Partido</th><th>Resultado</th><th>Casa</th><th>Cuota</th><th>Edge</th><th>SeÃ±al</th><th></th></tr></thead><tbody id="vb-body"><tr><td colspan="7"><div class="loading"><div class="dot"></div><div class="dot"></div><div class="dot"></div>Cargando...</div></td></tr></tbody></table>
    <div style="padding:10px 16px;font-size:10px;font-family:var(--mono);color:var(--muted);border-top:1px solid var(--border)">Configura ODDS_API_KEY en Render â†’ datos reales de 12 casas Â· the-odds-api.com (500 req/mes gratis)</div>
  </div>
  <div class="panel">
    <div class="ph2"><span class="pt">Calculadora Valor Esperado <span class="chip cp">EV</span></span></div>
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

<div id="s-sharp" class="section">
  <div class="ph"><div class="ph-title">Sharp Money Detector</div><div class="ph-sub">RLM Â· Steam Move Â· Bet/Money Split Â· Line Freeze Â· Sharp Book Consensus Â· Timing</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">PrecisiÃ³n RLM</div><div class="sc-val" style="color:var(--gold)">58-63%</div><div class="sc-sub">vs 50% aleatorio</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--red)"></div><div class="sc-lbl">Steam window</div><div class="sc-val" style="color:var(--red)">30-120s</div><div class="sc-sub">Para apostar lÃ­nea vieja</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">Indicadores</div><div class="sc-val" style="color:var(--purple2)">6</div><div class="sc-sub">RLM+Steam+Split+Freeze+Timing+Consensus</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Score mÃ¡ximo</div><div class="sc-val" style="color:var(--green)">99/100</div><div class="sc-sub">MÃºltiples seÃ±ales</div></div>
  </div>
  <div class="panel">
    <div class="ph2"><span class="pt">Analizador de partido <span class="chip cy">Sharp Score</span></span></div>
    <div class="pb">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
        <div class="field"><label>Partido</label><input type="text" id="sh-partido" value="Club AmÃ©rica vs Guadalajara"></div>
        <div class="field"><label>DÃ­as antes del partido</label><input type="number" id="sh-dias" value="2" min="0" max="7"></div>
        <div class="field"><label>LÃ­nea apertura</label><input type="number" id="sh-lap" value="2.20" step="0.01"></div>
        <div class="field"><label>LÃ­nea actual</label><input type="number" id="sh-lact" value="1.95" step="0.01"></div>
        <div class="field"><label>% boletos en Local</label><input type="number" id="sh-bol" value="28" min="0" max="100"></div>
        <div class="field"><label>% dinero en Local</label><input type="number" id="sh-din" value="64" min="0" max="100"></div>
      </div>
      <div style="margin-bottom:10px">
        <div style="font-size:10px;font-family:var(--mono);color:var(--muted);margin-bottom:4px">LÃ­neas por casa JSON â€” {"Pinnacle":1.95,"Bet365":2.15}</div>
        <input type="text" id="sh-casas" placeholder='{"Pinnacle":1.95,"Bookmaker":1.98,"Bet365":2.15,"Codere":2.18}' style="width:100%;padding:8px 11px;border-radius:7px;background:rgba(255,255,255,.04);border:1px solid var(--border2);color:var(--text);font-size:12px;font-family:var(--mono)">
      </div>
      <button class="btn btn-p" onclick="analizarSharp()" style="margin-bottom:14px">Detectar dinero sharp âš¡</button>
      <div id="sharp-result"></div>
    </div>
  </div>
  <div class="panel">
    <div class="ph2"><span class="pt">GuÃ­a de indicadores <span class="chip cp">PRO</span></span></div>
    <div class="pb">
      <table class="tbl">
        <thead><tr><th>Indicador</th><th>QuÃ© significa</th><th>Confianza</th></tr></thead>
        <tbody>
          <tr><td style="font-weight:600;color:var(--gold)">RLM</td><td style="font-size:11px">LÃ­nea se mueve CONTRA el lado con mÃ¡s apuestas pÃºblicas â†’ sharps en el otro lado</td><td><span class="badge bv">65-85%</span></td></tr>
          <tr><td style="font-weight:600;color:var(--green)">Bet/Money Split</td><td style="font-size:11px">80% boletos en un lado pero 35% del dinero â†’ dinero grande de sharps en el otro</td><td><span class="badge bv">60-90%</span></td></tr>
          <tr><td style="font-weight:600;color:var(--red)">Steam Move</td><td style="font-size:11px">4+ casas cambian lÃ­nea en minutos sin noticia â†’ sindicato apostando. Ventana: 30-120s</td><td><span class="badge bs2">78-92%</span></td></tr>
          <tr><td style="font-weight:600;color:var(--teal)">Line Freeze</td><td style="font-size:11px">70%+ pÃºblico en un lado pero lÃ­nea no se mueve â†’ libro protege a sharps del otro</td><td><span class="badge bsh">80%</span></td></tr>
          <tr><td style="font-weight:600;color:var(--purple2)">Sharp Consensus</td><td style="font-size:11px">Pinnacle tiene lÃ­nea diferente a Bet365/Codere â†’ mercado no incorporÃ³ info sharp aÃºn</td><td><span class="badge bs2">70-88%</span></td></tr>
          <tr><td style="font-weight:600;color:var(--muted)">Timing</td><td style="font-size:11px">Lunes-martes = sharp. Viernes-domingo = pÃºblico. Tarde = pÃºblico acumulado</td><td><span class="badge bdim">75%</span></td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<div id="s-clv" class="section">
  <div class="ph"><div class="ph-title">CLV Tracker</div><div class="ph-sub">closing line value Â· mÃ©trica #1 de apostadores profesionales Â· benchmark sharp â‰¥55%</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">CLV promedio</div><div class="sc-val" style="color:var(--green)">+2.4%</div><div class="sc-sub">Ãšltimas 50 apuestas</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">% Beat CLV</div><div class="sc-val" style="color:var(--gold)">71%</div><div class="sc-sub">Benchmark pro: >55%</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">Sharp rating</div><div class="sc-val" style="color:var(--purple2)">A+</div><div class="sc-sub">Apostador profesional</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--teal)"></div><div class="sc-lbl">ROI proyectado</div><div class="sc-val" style="color:var(--teal)">+8.2%</div><div class="sc-sub">Largo plazo</div></div>
  </div>
  <div class="g2">
    <div class="panel">
      <div class="ph2"><span class="pt">Calculadora CLV</span></div>
      <div class="pb">
        <div class="field"><label>Mi cuota apostada</label><input type="number" id="clv-i" value="2.10" step="0.01" oninput="calcCLV()"></div>
        <div class="field"><label>Cuota de cierre</label><input type="number" id="clv-c" value="1.85" step="0.01" oninput="calcCLV()"></div>
        <div id="clv-r" style="margin-top:8px"></div>
      </div>
    </div>
    <div class="panel">
      <div class="ph2"><span class="pt">Â¿QuÃ© es CLV? <span class="chip cp">PRO</span></span></div>
      <div class="pb" style="font-size:12px;line-height:1.75;color:var(--muted)">
        <p style="margin-bottom:9px">Si apostaste <strong style="color:var(--purple2)">2.10</strong> y la lÃ­nea cerrÃ³ en <strong style="color:var(--red)">1.85</strong> â†’ CLV <strong style="color:var(--green)">+13.5%</strong>.</p>
        <p style="margin-bottom:9px">El mercado confirmÃ³ tu anÃ¡lisis antes del partido. Calidad sobre resultado.</p>
        <p>Benchmark: <strong style="color:var(--gold)">â‰¥55% con CLV+</strong> = edge real demostrado sobre el mercado.</p>
      </div>
    </div>
  </div>
  <div class="panel">
    <div class="ph2"><span class="pt">Historial CLV <span class="chip cg">Tracker</span></span></div>
    <table class="tbl">
      <thead><tr><th>Apuesta</th><th>Mi cuota</th><th>Cierre</th><th>CLV</th><th>Resultado</th></tr></thead>
      <tbody id="clv-t"></tbody>
    </table>
  </div>
</div>

<div id="s-kelly" class="section">
  <div class="ph"><div class="ph-title">Kelly Pro</div><div class="ph-sub">criterio de kelly Â· gestiÃ³n Ã³ptima del bankroll Â· riesgo de ruina</div></div>
  <div class="g2">
    <div class="panel">
      <div class="ph2"><span class="pt">ParÃ¡metros <span class="chip cp">Kelly</span></span></div>
      <div class="pb">
        <div class="field"><label>Bankroll ($)</label><input type="number" id="k-b" value="5000" oninput="calcKelly()"></div>
        <div class="field"><label>Cuota decimal</label><input type="number" id="k-o" value="2.10" step="0.01" oninput="calcKelly()"></div>
        <div class="field"><label>Probabilidad estimada (%)</label><input type="number" id="k-p" value="55" oninput="calcKelly()"></div>
        <div class="field"><label>Modelo</label>
          <select id="k-m" onchange="calcKelly()">
            <option value="1">Kelly completo</option>
            <option value="0.5" selected>Medio Kelly â€” recomendado</option>
            <option value="0.25">Cuarto Kelly â€” conservador</option>
            <option value="flat">Flat 2% fijo</option>
          </select>
        </div>
      </div>
    </div>
    <div class="panel">
      <div class="ph2"><span class="pt">Resultado</span></div>
      <div class="pb">
        <div class="k-big"><div class="k-amount" id="k-a" style="color:var(--green)">â€”</div><div class="k-lbl" id="k-l">configura los parÃ¡metros</div></div>
        <div class="k-rows" id="k-r"></div>
      </div>
    </div>
  </div>
</div>

<div id="s-mc" class="section">
  <div class="ph"><div class="ph-title">Monte Carlo</div><div class="ph-sub">simulaciÃ³n Poisson Â· cuotas justas sin vig Â· distribuciÃ³n de goles</div></div>
  <div class="panel">
    <div class="ph2"><span class="pt">Configurar simulaciÃ³n <span class="chip cp">Poisson</span></span></div>
    <div class="pb">
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:14px">
        <div class="field"><label>Î» Local (goles esperados)</label><input type="number" id="mc-l" value="1.5" step="0.1"></div>
        <div class="field"><label>Î» Visitante</label><input type="number" id="mc-v" value="1.1" step="0.1"></div>
        <div class="field"><label>Simulaciones</label>
          <select id="mc-n"><option value="1000">1,000</option><option value="5000">5,000</option><option value="10000" selected>10,000</option><option value="50000">50,000</option></select>
        </div>
      </div>
      <button class="btn btn-p" id="mc-btn" onclick="runMC()">Ejecutar simulaciÃ³n</button>
    </div>
  </div>
  <div id="mc-out" style="display:none">
    <div class="sg" id="mc-sg"></div>
    <div class="panel">
      <div class="ph2"><span class="pt">DistribuciÃ³n <span class="chip ct">MC</span></span></div>
      <div class="pb" id="mc-bars-out"></div>
    </div>
  </div>
</div>

<div id="s-nlp" class="section">
  <div class="ph"><div class="ph-title">NLP Â· Lesiones</div><div class="ph-sub">escaneo RSS en tiempo real Â· edge 15-45 min antes que las casas ajusten lÃ­neas</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--red)"></div><div class="sc-lbl">Ventana de edge</div><div class="sc-val" style="color:var(--red)">15-45m</div><div class="sc-sub">Antes del ajuste de casas</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">Fuentes RSS</div><div class="sc-val" style="color:var(--gold)">3</div><div class="sc-sub">Record, Mediotiempo, ESPN</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Keywords</div><div class="sc-val" style="color:var(--green)">22</div><div class="sc-sub">Baja, duda, descartado...</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">AnÃ¡lisis</div><div class="sc-val" style="color:var(--purple2)">NLP</div><div class="sc-sub">Sentimiento + lesiones</div></div>
  </div>
  <div class="panel">
    <div class="ph2">
      <span class="pt">Scan pre-partido <span class="chip cr">EDGE</span></span>
      <div style="display:flex;gap:8px;align-items:center">
        <input type="text" id="nlp-home" value="Club AmÃ©rica" style="width:130px;padding:5px 8px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid var(--border2);color:var(--text);font-size:12px">
        <span style="color:var(--muted);font-size:12px">vs</span>
        <input type="text" id="nlp-away" value="Guadalajara" style="width:130px;padding:5px 8px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid var(--border2);color:var(--text);font-size:12px">
        <button class="btn btn-p" onclick="scanNLP()" style="padding:5px 14px;font-size:11px">Escanear â†—</button>
      </div>
    </div>
    <div class="pb" id="nlp-result"><p style="color:var(--muted);font-size:12px;font-family:var(--mono)">Ingresa los equipos y pulsa "Escanear" para detectar lesiones y sentimiento.</p></div>
  </div>
  <div class="panel">
    <div class="ph2"><span class="pt">Feed de noticias analizadas <span class="chip cg">RSS</span></span>
      <button class="btn btn-g" onclick="loadNoticias()" style="padding:5px 12px;font-size:11px">Cargar RSS</button>
    </div>
    <div class="pb" id="noticias-list"><p style="color:var(--muted);font-size:12px;font-family:var(--mono)">Pulsa "Cargar RSS" para ver el feed analizado.</p></div>
  </div>
</div>

<div id="s-backtest" class="section">
  <div class="ph"><div class="ph-title">Backtesting</div><div class="ph-sub">validaciÃ³n walk-forward Â· accuracy real del sistema Â· ROI simulado Â· Brier Score</div></div>
  <div class="panel">
    <div class="ph2">
      <span class="pt">Ejecutar backtest <span class="chip cp">Walk-Forward</span></span>
      <div style="display:flex;gap:8px;align-items:center">
        <select id="bt-modo" style="padding:5px 8px;border-radius:6px;background:rgba(255,255,255,.04);border:1px solid var(--border2);color:var(--text);font-size:12px">
          <option value="ensemble">Ensemble (DC+ELO+Poisson)</option>
          <option value="comparar">Comparar los 3 modelos</option>
        </select>
        <button class="btn btn-p" onclick="runBacktest()" style="padding:5px 14px;font-size:11px">Ejecutar</button>
      </div>
    </div>
    <div class="pb" id="bt-result"><p style="color:var(--muted);font-size:12px;font-family:var(--mono)">Pulsa "Ejecutar" para validar la precisiÃ³n real del sistema sobre el historial.</p></div>
  </div>
</div>

<div id="s-alertas" class="section">
  <div class="ph"><div class="ph-title">Alertas</div><div class="ph-sub">value bets Â· sharp money Â· lesiones Â· rachas Â· sorteos â€” en tiempo real</div></div>
  <div class="sg">
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">Urgentes</div><div class="sc-val" style="color:var(--gold)">4</div><div class="sc-sub">AcciÃ³n inmediata</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Value bets</div><div class="sc-val" style="color:var(--green)" id="vb-count2">â€”</div><div class="sc-sub" id="vb-edge2">cargando...</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">Sharp moves</div><div class="sc-val" style="color:var(--purple2)">3</div><div class="sc-sub">Ãšltimas 2 horas</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--teal)"></div><div class="sc-lbl">Proximo evento</div><div class="sc-val" style="color:var(--teal)">Hoy</div><div class="sc-sub">Value Bets activas</div></div>
  </div>
  <div class="panel">
    <div class="ph2"><span class="pt">Feed en tiempo real <span class="chip cg">LIVE</span></span>
      <button class="btn btn-g" onclick="loadAlertas()" style="padding:5px 12px;font-size:11px">Actualizar</button>
    </div>
    <div class="pb" id="alertas-feed"></div>
  </div>
</div>


<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<!-- BANKROLL TRACKER -->
<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<div id="s-bankroll" class="section">
  <div class="ph"><div class="ph-title">ðŸ’° Bankroll Tracker</div><div class="ph-sub">Registra apuestas Â· ROI real Â· Curva de crecimiento</div></div>
  <div class="sg" id="bk-stats">
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Bankroll Actual</div><div class="sc-val" style="color:var(--green)" id="bk-actual">$â€”</div><div class="sc-sub" id="bk-crec">Cargando...</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">ROI Total</div><div class="sc-val" style="color:var(--gold)" id="bk-roi">â€”%</div><div class="sc-sub" id="bk-profit">Profit neto</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">Win Rate</div><div class="sc-val" style="color:var(--purple2)" id="bk-wr">â€”%</div><div class="sc-sub" id="bk-wl">W/L</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--teal)"></div><div class="sc-lbl">Apuestas</div><div class="sc-val" style="color:var(--teal)" id="bk-total">â€”</div><div class="sc-sub" id="bk-pend">pendientes</div></div>
  </div>

  <div class="sg2">
    <div class="panel">
      <div class="ph2"><span class="pt">ðŸ“ Registrar Apuesta</span></div>
      <div class="pb" style="display:flex;flex-direction:column;gap:10px">
        <input id="bk-partido" placeholder="Partido (ej: AmÃ©rica vs Chivas)" style="width:100%;padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
          <input id="bk-seleccion" placeholder="SelecciÃ³n (ej: Local)" style="padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
          <input id="bk-cuota" type="number" step="0.01" placeholder="Cuota (ej: 2.10)" style="padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
          <input id="bk-monto" type="number" placeholder="Monto ($)" style="padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
          <select id="bk-mercado" style="padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
            <option>1X2</option><option>Over/Under</option><option>BTTS</option><option>Handicap</option>
          </select>
        </div>
        <button class="btn" onclick="registrarApuesta()" style="width:100%;padding:10px;background:var(--purple);border:none;border-radius:8px;color:#fff;font-weight:700;cursor:pointer;font-family:var(--ui)">Registrar Apuesta</button>
        <div id="bk-msg" style="font-size:11px;font-family:var(--mono);color:var(--green);text-align:center;min-height:16px"></div>
      </div>
    </div>
    <div class="panel">
      <div class="ph2"><span class="pt">âš™ï¸ Inicializar Bankroll</span></div>
      <div class="pb" style="display:flex;flex-direction:column;gap:10px">
        <p style="font-size:11px;color:var(--muted);font-family:var(--mono)">Define tu bankroll inicial para empezar el tracking de ROI.</p>
        <input id="bk-inicial" type="number" placeholder="Bankroll inicial ($)" style="width:100%;padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <button class="btn" onclick="inicializarBankroll()" style="width:100%;padding:10px;background:var(--teal);border:none;border-radius:8px;color:#000;font-weight:700;cursor:pointer;font-family:var(--ui)">Establecer Bankroll</button>
      </div>
    </div>
  </div>

  <div class="panel">
    <div class="ph2"><span class="pt">ðŸ“‹ Apuestas Recientes</span>
      <button class="btn btn-g" onclick="loadBankroll()" style="padding:5px 12px;font-size:11px;background:var(--bg4);border:1px solid var(--border2);border-radius:6px;color:var(--text);cursor:pointer">Actualizar</button>
    </div>
    <div class="pb" id="bk-lista" style="font-family:var(--mono);font-size:11px;color:var(--muted)">Cargando...</div>
  </div>
</div>

<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<!-- MERCADOS EXTRA -->
<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<div id="s-mercados" class="section">
  <div class="ph"><div class="ph-title">ðŸ“ˆ Mercados Extra</div><div class="ph-sub">Over/Under Â· BTTS Â· Asian Handicap Â· Marcadores exactos</div></div>
  <div class="panel">
    <div class="ph2"><span class="pt">ðŸ” Analizar Partido</span></div>
    <div class="pb" style="display:flex;gap:10px;align-items:flex-end">
      <input id="m-home" placeholder="Local (ej: Club AmÃ©rica)" value="Club AmÃ©rica" style="flex:1;padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
      <input id="m-away" placeholder="Visitante (ej: Guadalajara)" value="Guadalajara" style="flex:1;padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
      <button onclick="loadMercados()" style="padding:9px 18px;background:var(--purple);border:none;border-radius:8px;color:#fff;font-weight:700;cursor:pointer;font-family:var(--ui);white-space:nowrap">Calcular</button>
    </div>
  </div>
  <div id="m-resultado" style="display:none">
    <div class="sg3">
      <div class="panel"><div class="ph2"><span class="pt">Over/Under</span></div><div class="pb" id="m-ou" style="font-family:var(--mono);font-size:11px"></div></div>
      <div class="panel"><div class="ph2"><span class="pt">BTTS Â· Ambos Anotan</span></div><div class="pb" id="m-btts"></div></div>
      <div class="panel"><div class="ph2"><span class="pt">Marcadores Exactos</span></div><div class="pb" id="m-scores" style="font-family:var(--mono);font-size:11px"></div></div>
    </div>
    <div class="panel"><div class="ph2"><span class="pt">Asian Handicap</span></div><div class="pb" id="m-ah" style="font-family:var(--mono);font-size:11px;display:grid;grid-template-columns:repeat(3,1fr);gap:6px"></div></div>
  </div>
</div>

<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<!-- HEDGE & ARBITRAJE -->
<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<div id="s-hedge" class="section">
  <div class="ph"><div class="ph-title">ðŸ›¡ Hedge Â· Arbitraje Â· Dutching</div><div class="ph-sub">Asegura ganancias Â· Detecta arbitrajes Â· Distribuye stake</div></div>
  <div class="sg3">
    <div class="panel">
      <div class="ph2"><span class="pt">Hedge Garantizado</span></div>
      <div class="pb" style="display:flex;flex-direction:column;gap:8px">
        <input id="h-stake" type="number" placeholder="Stake original ($)" value="100" style="width:100%;padding:8px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <input id="h-corig" type="number" step="0.01" placeholder="Cuota original" value="2.50" style="width:100%;padding:8px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <input id="h-chedge" type="number" step="0.01" placeholder="Cuota hedge" value="2.10" style="width:100%;padding:8px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <button onclick="calcHedge()" style="padding:9px;background:var(--purple);border:none;border-radius:8px;color:#fff;font-weight:700;cursor:pointer;font-family:var(--ui)">Calcular Hedge</button>
        <div id="h-res" style="font-family:var(--mono);font-size:11px;line-height:1.8;color:var(--muted)"></div>
      </div>
    </div>
    <div class="panel">
      <div class="ph2"><span class="pt">Detector de Arbitraje</span></div>
      <div class="pb" style="display:flex;flex-direction:column;gap:8px">
        <p style="font-size:10px;font-family:var(--mono);color:var(--muted)">Cuotas del mismo partido en distintas casas:</p>
        <input id="arb-1" type="number" step="0.01" placeholder='Cuota "1" (Local)' value="2.10" style="width:100%;padding:8px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <input id="arb-x" type="number" step="0.01" placeholder='Cuota "X" (Empate)' value="3.40" style="width:100%;padding:8px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <input id="arb-2" type="number" step="0.01" placeholder='Cuota "2" (Visitante)' value="3.80" style="width:100%;padding:8px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <input id="arb-bank" type="number" placeholder="Bankroll ($)" value="1000" style="width:100%;padding:8px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <button onclick="calcArbitraje()" style="padding:9px;background:var(--green);border:none;border-radius:8px;color:#000;font-weight:700;cursor:pointer;font-family:var(--ui)">Detectar Arbitraje</button>
        <div id="arb-res" style="font-family:var(--mono);font-size:11px;line-height:1.8;color:var(--muted)"></div>
      </div>
    </div>
    <div class="panel">
      <div class="ph2"><span class="pt">Resultado del AnÃ¡lisis</span></div>
      <div class="pb" id="hedge-detail" style="font-family:var(--mono);font-size:11px;color:var(--muted);line-height:1.8">Ingresa los datos y calcula.</div>
    </div>
  </div>
</div>

<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<!-- OPTIMIZADOR PROGOL -->
<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<div id="s-progolopt" class="section">
  <div class="ph"><div class="ph-title">ðŸŽ¯ Optimizador de Progol</div><div class="ph-sub">Quiniela simple Â· Diversificada Â· MÃ¡xima cobertura</div></div>
  <div class="panel">
    <div class="ph2"><span class="pt">Estrategia</span>
      <div style="display:flex;gap:8px">
        <button onclick="loadProgolOpt('simple')" style="padding:5px 14px;background:var(--purple);border:none;border-radius:6px;color:#fff;font-size:11px;cursor:pointer;font-family:var(--ui)">Simple</button>
        <button onclick="loadProgolOpt('diversificada')" style="padding:5px 14px;background:var(--bg4);border:1px solid var(--border2);border-radius:6px;color:var(--text);font-size:11px;cursor:pointer;font-family:var(--ui)">Diversificada</button>
        <button onclick="loadProgolOpt('cobertura')" style="padding:5px 14px;background:var(--gold);border:none;border-radius:6px;color:#000;font-size:11px;cursor:pointer;font-family:var(--ui)">MÃ¡x Cobertura</button>
      </div>
    </div>
    <div class="pb" id="progolopt-res" style="font-family:var(--mono);font-size:12px;color:var(--muted)">Selecciona una estrategia...</div>
  </div>
  <div class="panel" id="progolopt-analisis" style="display:none">
    <div class="ph2"><span class="pt">AnÃ¡lisis de Jornada</span></div>
    <div class="pb" id="progolopt-jornada" style="font-family:var(--mono);font-size:11px"></div>
  </div>
</div>

<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<!-- ML MODEL -->
<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<div id="s-mlmodel" class="section">
  <div class="ph"><div class="ph-title">ðŸ¤– Modelo ML</div><div class="ph-sub">Gradient Boosting Â· 16 features Â· Comparativa vs Ensemble estadÃ­stico</div></div>
  <div class="panel">
    <div class="ph2"><span class="pt">PredicciÃ³n ML vs Ensemble</span></div>
    <div class="pb" style="display:flex;gap:10px;align-items:flex-end">
      <input id="ml-home" placeholder="Local" value="Club AmÃ©rica" style="flex:1;padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
      <input id="ml-away" placeholder="Visitante" value="Guadalajara" style="flex:1;padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
      <button onclick="loadML()" style="padding:9px 18px;background:var(--purple);border:none;border-radius:8px;color:#fff;font-weight:700;cursor:pointer;font-family:var(--ui)">Predecir</button>
    </div>
  </div>
  <div id="ml-resultado" style="display:none">
    <div class="sg3">
      <div class="panel"><div class="ph2"><span class="pt">Ensemble (DC+ELO+Poisson)</span></div><div class="pb" id="ml-ens" style="font-family:var(--mono);font-size:12px;line-height:2"></div></div>
      <div class="panel"><div class="ph2"><span class="pt">ML (Gradient Boosting)</span></div><div class="pb" id="ml-gb" style="font-family:var(--mono);font-size:12px;line-height:2"></div></div>
      <div class="panel"><div class="ph2"><span class="pt">Combinado (65%+35%)</span></div><div class="pb" id="ml-comb" style="font-family:var(--mono);font-size:12px;line-height:2"></div></div>
    </div>
    <div class="panel"><div class="ph2"><span class="pt">Feature Importance</span></div><div class="pb" id="ml-feat" style="font-family:var(--mono);font-size:11px;display:grid;grid-template-columns:repeat(2,1fr);gap:4px"></div></div>
  </div>
</div>

<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<!-- MULTI-LIGA -->
<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<div id="s-ligas" class="section">
  <div class="ph"><div class="ph-title">ðŸŒ Multi-Liga</div><div class="ph-sub">Premier Â· La Liga Â· Serie A Â· Bundesliga Â· Champions Â· MLS Â· Liga MX</div></div>
  <div class="panel">
    <div class="ph2"><span class="pt">Seleccionar Liga</span></div>
    <div class="pb" style="display:flex;gap:8px;flex-wrap:wrap">
      <button onclick="loadLiga('liga_mx')" class="liga-btn" style="padding:7px 14px;background:var(--purple);border:none;border-radius:7px;color:#fff;font-size:12px;cursor:pointer;font-family:var(--ui)">ðŸ‡²ðŸ‡½ Liga MX</button>
      <button onclick="loadLiga('premier_league')" class="liga-btn" style="padding:7px 14px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-size:12px;cursor:pointer;font-family:var(--ui)">ðŸ´ó §ó ¢ó ¥ó ®ó §ó ¿ Premier</button>
      <button onclick="loadLiga('la_liga')" class="liga-btn" style="padding:7px 14px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-size:12px;cursor:pointer;font-family:var(--ui)">ðŸ‡ªðŸ‡¸ La Liga</button>
      <button onclick="loadLiga('serie_a')" class="liga-btn" style="padding:7px 14px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-size:12px;cursor:pointer;font-family:var(--ui)">ðŸ‡®ðŸ‡¹ Serie A</button>
      <button onclick="loadLiga('bundesliga')" class="liga-btn" style="padding:7px 14px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-size:12px;cursor:pointer;font-family:var(--ui)">ðŸ‡©ðŸ‡ª Bundesliga</button>
      <button onclick="loadLiga('champions_league')" class="liga-btn" style="padding:7px 14px;background:var(--gold);border:none;border-radius:7px;color:#000;font-size:12px;cursor:pointer;font-family:var(--ui)">â­ Champions</button>
      <button onclick="loadLiga('mls')" class="liga-btn" style="padding:7px 14px;background:var(--green);border:none;border-radius:7px;color:#000;font-size:12px;cursor:pointer;font-family:var(--ui)">ðŸ‡ºðŸ‡¸ MLS (activa)</button>
      <button onclick="loadLiga('ligue_1')" class="liga-btn" style="padding:7px 14px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-size:12px;cursor:pointer;font-family:var(--ui)">ðŸ‡«ðŸ‡· Ligue 1</button>
    </div>
  </div>
  <div class="panel" id="ligas-panel" style="display:none">
    <div class="ph2"><span class="pt" id="ligas-title">Predicciones</span>
      <span class="chip cp" id="ligas-badge"></span>
    </div>
    <div class="pb" id="ligas-res" style="font-family:var(--mono);font-size:11px"></div>
  </div>
</div>


<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<!-- CUENTAS & CAMUFLAJE -->
<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<div id="s-cuentas" class="section">
  <div class="ph">
    <div class="ph-title">ðŸ¦ Cuentas & Estrategia de Camuflaje</div>
    <div class="ph-sub">Gestiona tus cuentas Â· Monitorea health Â· Genera plan de camuflaje</div>
  </div>

  <!-- Stats de cuentas -->
  <div class="sg" id="cuentas-stats">
    <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Cuentas Activas</div><div class="sc-val" style="color:var(--green)" id="ct-activas">â€”</div><div class="sc-sub">casas registradas</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">Health Promedio</div><div class="sc-val" style="color:var(--gold)" id="ct-health">â€”</div><div class="sc-sub">score de salud</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--red)"></div><div class="sc-lbl">En Riesgo</div><div class="sc-val" style="color:var(--red)" id="ct-riesgo">â€”</div><div class="sc-sub">cuentas limitadas</div></div>
    <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">Perfil Activo</div><div class="sc-val" style="color:var(--purple2)" id="ct-perfil">Recreativo</div><div class="sc-sub">camuflaje</div></div>
  </div>

  <div class="sg2">
    <!-- Registrar cuenta -->
    <div class="panel">
      <div class="ph2"><span class="pt">âž• Registrar Cuenta</span></div>
      <div class="pb" style="display:flex;flex-direction:column;gap:10px">
        <select id="ct-casa" style="padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
          <option value="caliente">ðŸ‡²ðŸ‡½ Caliente.mx</option>
          <option value="codere">Codere</option>
          <option value="1xbet">1xBet</option>
          <option value="bet365">Bet365</option>
          <option value="betano">Betano</option>
          <option value="pinnacle">Pinnacle (sharp)</option>
          <option value="williamhill">William Hill</option>
          <option value="bwin">Bwin</option>
        </select>
        <input id="ct-limite" type="number" placeholder="LÃ­mite mÃ¡ximo por apuesta ($)" style="padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <input id="ct-balance" type="number" placeholder="Balance inicial ($)" style="padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <input id="ct-notas" placeholder="Notas (opcional)" style="padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <button onclick="registrarCuenta()" style="padding:10px;background:var(--purple);border:none;border-radius:8px;color:#fff;font-weight:700;cursor:pointer;font-family:var(--ui)">Registrar Casa</button>
        <div id="ct-msg" style="font-size:11px;font-family:var(--mono);color:var(--green);text-align:center;min-height:16px"></div>
      </div>
    </div>

    <!-- Reportar limitaciÃ³n -->
    <div class="panel">
      <div class="ph2"><span class="pt">âš ï¸ Reportar LimitaciÃ³n</span></div>
      <div class="pb" style="display:flex;flex-direction:column;gap:10px">
        <p style="font-size:11px;color:var(--muted);font-family:var(--mono)">Si una casa redujo tu lÃ­mite mÃ¡ximo por apuesta, regÃ­stralo aquÃ­ para que el sistema ajuste tu estrategia.</p>
        <select id="ct-casa-lim" style="padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
          <option value="">Selecciona la casa...</option>
        </select>
        <input id="ct-nuevo-lim" type="number" placeholder="Nuevo lÃ­mite mÃ¡ximo ($)" style="padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <input id="ct-razon" placeholder="RazÃ³n (ej: limitaron a $200)" style="padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        <button onclick="reportarLimitacion()" style="padding:10px;background:rgba(248,113,113,.2);border:1px solid var(--red);border-radius:8px;color:var(--red);font-weight:700;cursor:pointer;font-family:var(--ui)">Reportar LimitaciÃ³n</button>
        <div id="ct-lim-msg" style="font-size:11px;font-family:var(--mono);min-height:16px"></div>
      </div>
    </div>
  </div>

  <!-- Estado de cuentas -->
  <div class="panel">
    <div class="ph2">
      <span class="pt">ðŸ“Š Estado de Cuentas</span>
      <button onclick="loadCuentas()" style="padding:5px 12px;font-size:11px;background:var(--bg4);border:1px solid var(--border2);border-radius:6px;color:var(--text);cursor:pointer">Actualizar</button>
    </div>
    <div class="pb" id="ct-lista" style="font-family:var(--mono);font-size:11px;color:var(--muted)">Sin cuentas registradas. Agrega tu primera casa arriba.</div>
  </div>

  <!-- Plan de camuflaje -->
  <div class="panel">
    <div class="ph2"><span class="pt">ðŸŽ­ Plan de Camuflaje Semanal</span></div>
    <div class="pb">
      <div style="display:flex;gap:10px;margin-bottom:12px;align-items:flex-end">
        <div>
          <div style="font-size:10px;color:var(--muted);font-family:var(--mono);margin-bottom:4px">PERFIL</div>
          <select id="ct-perfil-sel" style="padding:8px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
            <option value="recreativo">Recreativo â€” cuentas duran aÃ±os</option>
            <option value="mixto" selected>Mixto â€” balance recomendado</option>
            <option value="agresivo">Agresivo â€” mÃ¡xima ganancia</option>
          </select>
        </div>
        <div>
          <div style="font-size:10px;color:var(--muted);font-family:var(--mono);margin-bottom:4px">BANKROLL ($)</div>
          <input id="ct-bank" type="number" value="2000" style="padding:8px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px;width:110px">
        </div>
        <button onclick="loadCamuflaje()" style="padding:9px 18px;background:var(--teal);border:none;border-radius:8px;color:#000;font-weight:700;cursor:pointer;font-family:var(--ui)">Generar Plan</button>
      </div>
      <div id="ct-camuflaje" style="font-family:var(--mono);font-size:11px;color:var(--muted)">Selecciona un perfil y genera el plan.</div>
    </div>
  </div>

  <!-- AnÃ¡lisis de comportamiento -->
  <div class="panel">
    <div class="ph2">
      <span class="pt">ðŸ” AnÃ¡lisis de tu Perfil de Riesgo</span>
      <button onclick="loadAnalisisCuenta()" style="padding:5px 12px;font-size:11px;background:var(--bg4);border:1px solid var(--border2);border-radius:6px;color:var(--text);cursor:pointer">Analizar</button>
    </div>
    <div class="pb" id="ct-analisis" style="font-family:var(--mono);font-size:11px;color:var(--muted)">Haz clic en "Analizar" para ver tu perfil de riesgo actual.</div>
  </div>

  <!-- RotaciÃ³n Ã³ptima -->
  <div class="panel">
    <div class="ph2"><span class="pt">ðŸ”„ RotaciÃ³n Ã“ptima por Apuesta</span></div>
    <div class="pb" style="display:flex;gap:10px;align-items:flex-end;margin-bottom:12px">
      <input id="ct-monto-rot" type="number" value="500" placeholder="Monto total ($)" style="padding:8px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px;width:140px">
      <button onclick="loadRotacion()" style="padding:9px 18px;background:var(--purple);border:none;border-radius:8px;color:#fff;font-weight:700;cursor:pointer;font-family:var(--ui)">Calcular RotaciÃ³n</button>
    </div>
    <div id="ct-rotacion" style="font-family:var(--mono);font-size:11px;color:var(--muted)">Ingresa el monto y calcula cÃ³mo distribuirlo entre tus casas.</div>
  </div>
</div>


<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<!-- VALUE PRO -->
<!-- â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• -->
<div id="s-valuepro" class="section">
  <div class="ph">
    <div class="ph-title">ðŸ’Ž Value Betting Pro</div>
    <div class="ph-sub">Donde estÃ¡ el dinero real Â· Edge + Kelly + CLV Â· El mÃ©todo de los profesionales</div>
  </div>

  <div class="panel" style="background:rgba(124,109,250,.05);border:1px solid rgba(124,109,250,.2)">
    <div class="pb" style="font-family:var(--mono);font-size:12px;color:var(--muted);line-height:1.7">
      <span style="color:var(--purple2);font-weight:700">El secreto de los apostadores rentables:</span> no aciertan mÃ¡s del 55% de sus apuestas.
      Ganan porque apuestan <span style="color:var(--green)">solo cuando hay value</span> (la casa paga de mÃ¡s) y usan
      <span style="color:var(--gold)">Kelly</span> para el monto Ã³ptimo. No persiguen aciertos, persiguen <span style="color:var(--green)">edge positivo</span>.
    </div>
  </div>

  <!-- Calculadora de Value -->
  <div class="sg2">
    <div class="panel">
      <div class="ph2"><span class="pt">ðŸ” Calculadora de Value</span></div>
      <div class="pb" style="display:flex;flex-direction:column;gap:10px">
        <div>
          <div style="font-size:10px;color:var(--muted);font-family:var(--mono);margin-bottom:4px">PROBABILIDAD REAL (tu estimaciÃ³n o la del modelo) %</div>
          <input id="vp-prob" type="number" step="0.1" placeholder="ej: 55" value="55" style="width:100%;padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        </div>
        <div>
          <div style="font-size:10px;color:var(--muted);font-family:var(--mono);margin-bottom:4px">CUOTA QUE PAGA LA CASA</div>
          <input id="vp-cuota" type="number" step="0.01" placeholder="ej: 2.10" value="2.10" style="width:100%;padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        </div>
        <div>
          <div style="font-size:10px;color:var(--muted);font-family:var(--mono);margin-bottom:4px">CUOTA PINNACLE (opcional â€” valida el value)</div>
          <input id="vp-pinnacle" type="number" step="0.01" placeholder="ej: 1.95 (dejar vacÃ­o si no tienes)" style="width:100%;padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
          <div>
            <div style="font-size:10px;color:var(--muted);font-family:var(--mono);margin-bottom:4px">BANKROLL $</div>
            <input id="vp-bank" type="number" placeholder="2000" value="2000" style="width:100%;padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
          </div>
          <div>
            <div style="font-size:10px;color:var(--muted);font-family:var(--mono);margin-bottom:4px">FRACCIÃ“N KELLY</div>
            <select id="vp-frac" style="width:100%;padding:9px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px">
              <option value="0.25" selected>1/4 Kelly (seguro)</option>
              <option value="0.5">1/2 Kelly (moderado)</option>
              <option value="1">Kelly completo (agresivo)</option>
            </select>
          </div>
        </div>
        <button onclick="calcValuePro()" style="padding:11px;background:var(--purple);border:none;border-radius:8px;color:#fff;font-weight:700;cursor:pointer;font-family:var(--ui)">Analizar Value</button>
      </div>
    </div>

    <div class="panel">
      <div class="ph2"><span class="pt">ðŸ“Š Resultado del AnÃ¡lisis</span></div>
      <div class="pb" id="vp-resultado" style="font-family:var(--mono);font-size:12px;color:var(--muted)">
        Ingresa los datos y analiza. Te dirÃ© si hay value real y cuÃ¡nto apostar.
      </div>
    </div>
  </div>

  <!-- CLV Calculator -->
  <div class="panel">
    <div class="ph2"><span class="pt">ðŸ“ˆ Closing Line Value (CLV) â€” la mÃ©trica reina</span></div>
    <div class="pb">
      <p style="font-size:11px;font-family:var(--mono);color:var(--muted);margin-bottom:12px;line-height:1.6">
        El CLV mide si apostaste a mejor cuota que la de cierre. <span style="color:var(--green)">CLV positivo consistente = rentabilidad garantizada</span> a largo plazo, aunque pierdas apuestas individuales.
      </p>
      <div style="display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap">
        <div>
          <div style="font-size:10px;color:var(--muted);font-family:var(--mono);margin-bottom:4px">CUOTA QUE APOSTASTE</div>
          <input id="clv-apostada" type="number" step="0.01" value="2.10" style="padding:8px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px;width:130px">
        </div>
        <div>
          <div style="font-size:10px;color:var(--muted);font-family:var(--mono);margin-bottom:4px">CUOTA DE CIERRE</div>
          <input id="clv-cierre" type="number" step="0.01" value="1.90" style="padding:8px 12px;background:var(--bg4);border:1px solid var(--border2);border-radius:7px;color:var(--text);font-family:var(--ui);font-size:12px;width:130px">
        </div>
        <button onclick="calcCLVpro()" style="padding:9px 18px;background:var(--teal);border:none;border-radius:8px;color:#000;font-weight:700;cursor:pointer;font-family:var(--ui)">Calcular CLV</button>
      </div>
      <div id="clv-pro-res" style="margin-top:12px;font-family:var(--mono);font-size:12px;color:var(--muted)"></div>
    </div>
  </div>

  <!-- GuÃ­a rÃ¡pida -->
  <div class="panel">
    <div class="ph2"><span class="pt">ðŸ“– CÃ³mo ganar dinero (resumen)</span></div>
    <div class="pb" style="font-family:var(--mono);font-size:11px;color:var(--muted);line-height:1.8">
      <div style="padding:6px 0;border-bottom:1px solid var(--border)"><span style="color:var(--green)">1.</span> Apuesta SOLO cuando el edge es positivo (modelo dice mÃ¡s probable que la casa)</div>
      <div style="padding:6px 0;border-bottom:1px solid var(--border)"><span style="color:var(--green)">2.</span> Usa el stake de Kelly â€” ni mÃ¡s ni menos</div>
      <div style="padding:6px 0;border-bottom:1px solid var(--border)"><span style="color:var(--green)">3.</span> Compara con Pinnacle: si tu casa paga mÃ¡s, el value es real</div>
      <div style="padding:6px 0;border-bottom:1px solid var(--border)"><span style="color:var(--green)">4.</span> Registra el CLV de cada apuesta â€” es tu termÃ³metro de rentabilidad</div>
      <div style="padding:6px 0"><span style="color:var(--gold)">5.</span> Acepta perder apuestas individuales. El edge se paga a largo plazo.</div>
    </div>
  </div>
</div>

</main>
</div>

<script>
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// CORE
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
const API = ''  // mismo servidor

async function api(path) {
  const r = await fetch(API + path)
  const body = await r.json().catch(() => null)
  if (!r.ok) throw new Error(body?.error || r.status)
  return body
}

function setAPIStatus(ok) {
  const b = document.getElementById('api-badge')
  b.className = 'api-badge ' + (ok ? 'api-ok' : 'api-err')
  b.textContent = ok ? 'API OK' : 'API Error'
}

// Clock
setInterval(() => {
  document.getElementById('clock').textContent = new Date().toLocaleTimeString('es-MX',{hour12:false})
}, 1000)

// NAV
function go(btn, id) {
  // Quitar clase activa de todos los botones y secciones
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('on'))
  document.querySelectorAll('.section').forEach(s => s.classList.remove('on'))
  // Activar botÃ³n clickeado
  if(btn) btn.classList.add('on')
  // Mostrar secciÃ³n correspondiente
  const sec = document.getElementById('s-' + id)
  if(sec) {
    sec.classList.add('on')
  } else {
    console.warn('SecciÃ³n no encontrada: s-' + id)
  }
  // Ejecutar acciÃ³n de carga segÃºn secciÃ³n
  if(id==='dashboard') initDashboard()
  else if(id==='odds') { loadVB(); calcEV() }
  else if(id==='clv') { calcCLV(); renderCLVT() }
  else if(id==='kelly') calcKelly()
  else if(id==='alertas') loadAlertas()
  else if(id==='bankroll') loadBankroll()
  else if(id==='progol') loadProgol()
  else if(id==='nlp') { loadNoticias(); loadAlertas('nlp-alertas') }
  else if(id==='valuepro') calcValuePro()
  else if(id==='mercados') loadMercados()
  else if(id==='hedge') calcHedge()
  else if(id==='progolopt') loadProgolOpt()
  else if(id==='mlmodel') loadML()
  else if(id==='ligas') loadLiga()
  else if(id==='cuentas') loadCuentas()
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// DATOS LOCALES (fallback)
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// DASHBOARD
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// BANKROLL TRACKER
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function loadBankroll() {
  try {
    const d = await api('/api/bankroll/estadisticas')
    if (d.error) { document.getElementById('bk-lista').innerHTML = '<span style="color:var(--muted)">'+d.error+'</span>'; return }
    const b = d.bankroll || {}
    const a = d.apuestas || {}
    const r = d.rendimiento || {}
    document.getElementById('bk-actual').textContent = '$'+(b.actual||0).toLocaleString('es-MX',{minimumFractionDigits:2})
    document.getElementById('bk-crec').textContent = (b.crecimiento_pct>=0?'+':'')+b.crecimiento_pct+'% vs inicial'
    document.getElementById('bk-roi').textContent = (r.roi_pct>=0?'+':'')+r.roi_pct+'%'
    document.getElementById('bk-profit').textContent = 'Profit: $'+(r.profit_neto||0).toLocaleString('es-MX',{minimumFractionDigits:2})
    document.getElementById('bk-wr').textContent = (a.win_rate_pct||0)+'%'
    document.getElementById('bk-wl').textContent = (a.ganadas||0)+'W / '+(a.perdidas||0)+'L'
    document.getElementById('bk-total').textContent = a.total||0
    document.getElementById('bk-pend').textContent = (a.pendientes||0)+' pendientes'
    const lista = await api('/api/bankroll/apuestas?limite=10')
    if (!lista.length) { document.getElementById('bk-lista').innerHTML = '<span style="color:var(--muted)">Sin apuestas registradas</span>'; return }
    document.getElementById('bk-lista').innerHTML = lista.map(b => {
      const color = b.resultado==='ganada'?'var(--green)':b.resultado==='perdida'?'var(--red)':'var(--gold)'
      const gn = (b.ganancia_neta||0)>=0?'+'+b.ganancia_neta:b.ganancia_neta
      return `<div style="display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--border)">
        <span><span style="color:var(--text)">${b.partido}</span> <span style="color:var(--muted)">${b.seleccion} @${b.cuota}</span></span>
        <span><span style="color:${color}">${b.resultado}</span> <span style="color:${color}">${b.resultado!=='pendiente'?'$'+gn:''}</span></span>
      </div>`
    }).join('')
  } catch(e) { document.getElementById('bk-lista').innerHTML = '<span style="color:var(--red)">Error: '+e+'</span>' }
}

async function registrarApuesta() {
  const partido = document.getElementById('bk-partido').value
  const seleccion = document.getElementById('bk-seleccion').value
  const cuota = parseFloat(document.getElementById('bk-cuota').value)
  const monto = parseFloat(document.getElementById('bk-monto').value)
  const mercado = document.getElementById('bk-mercado').value
  if (!partido||!seleccion||!cuota||!monto) { document.getElementById('bk-msg').textContent='Completa todos los campos'; return }
  try {
    const r = await fetch('/api/bankroll/registrar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({partido,seleccion,cuota,monto,mercado})})
    const d = await r.json()
    document.getElementById('bk-msg').textContent = d.error ? 'âŒ '+d.error : 'âœ… Apuesta #'+d.id+' registrada'
    document.getElementById('bk-msg').style.color = d.error?'var(--red)':'var(--green)'
    if (!d.error) loadBankroll()
  } catch(e) { document.getElementById('bk-msg').textContent='âŒ '+e }
}

async function inicializarBankroll() {
  const monto = parseFloat(document.getElementById('bk-inicial').value)
  if (!monto||monto<=0) return
  try {
    const r = await fetch('/api/bankroll/inicializar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({monto})})
    const d = await r.json()
    alert(d.error || 'âœ… Bankroll de $'+monto+' establecido')
    loadBankroll()
  } catch(e) { alert('Error: '+e) }
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// MERCADOS EXTRA
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function loadMercados() {
  const home = document.getElementById('m-home').value
  const away = document.getElementById('m-away').value
  try {
    const d = await api('/api/mercados/partido?home='+encodeURIComponent(home)+'&away='+encodeURIComponent(away))
    document.getElementById('m-resultado').style.display='block'
    // Over/Under
    const ou = d.over_under||{}
    document.getElementById('m-ou').innerHTML = Object.entries(ou).map(([l,v])=>
      `<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--border)">
        <span style="color:var(--text)">O/U ${l}</span>
        <span><span style="color:var(--green)">Over ${v.over_pct}%</span> Â· <span style="color:var(--red)">Under ${v.under_pct}%</span></span>
      </div>`).join('')
    // BTTS
    const btts = d.btts||{}
    document.getElementById('m-btts').innerHTML = `
      <div style="text-align:center;padding:10px 0">
        <div style="font-size:28px;font-weight:800;color:var(--green)">${btts.si_pct}%</div>
        <div style="font-size:11px;color:var(--muted);font-family:var(--mono)">Ambos anotan</div>
        <div style="margin-top:8px;font-size:11px;font-family:var(--mono)">Cuota Si: <span style="color:var(--text)">${btts.cuota_si}</span></div>
        <div style="font-size:11px;font-family:var(--mono)">No anotan: <span style="color:var(--text)">${btts.no_pct}% @ ${btts.cuota_no}</span></div>
        <div style="font-size:11px;font-family:var(--mono);color:var(--muted);margin-top:4px">Goles esp: ${(d.goles_esperados||{}).total||'â€”'}</div>
      </div>`
    // Marcadores exactos
    const ms = d.marcadores_exactos||[]
    document.getElementById('m-scores').innerHTML = ms.map(m=>
      `<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid var(--border)">
        <span style="color:var(--text)">${m.marcador}</span>
        <span><span style="color:var(--gold)">${m.prob_pct}%</span> <span style="color:var(--muted)">@${m.cuota_justa}</span></span>
      </div>`).join('')
    // Asian Handicap
    const ah = d.asian_handicap||{}
    document.getElementById('m-ah').innerHTML = Object.entries(ah).slice(0,9).map(([h,v])=>
      `<div style="background:var(--bg4);border:1px solid var(--border);border-radius:6px;padding:6px 8px">
        <div style="color:var(--muted);font-size:10px">AH ${h}</div>
        <div style="color:var(--green);font-size:11px">L: ${v.p_local_pct}%</div>
        <div style="color:var(--red);font-size:11px">V: ${v.p_visitante_pct}%</div>
      </div>`).join('')
  } catch(e) { document.getElementById('m-resultado').style.display='none'; alert('Error: '+e) }
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// HEDGE & ARBITRAJE
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function calcHedge() {
  const stake = document.getElementById('h-stake').value
  const corig = document.getElementById('h-corig').value
  const chedge = document.getElementById('h-chedge').value
  try {
    const d = await api(`/api/mercados/hedge/garantizado?stake=${stake}&cuota_original=${corig}&cuota_hedge=${chedge}`)
    const color = d.conviene?'var(--green)':'var(--red)'
    document.getElementById('h-res').innerHTML = `
      <div style="color:${color};font-size:13px;font-weight:700;margin-bottom:6px">${d.conviene?'âœ… Hedge recomendado':'âš ï¸ No asegura ganancia'}</div>
      Apostar hedge: <span style="color:var(--text)">$${d.stake_hedge}</span><br>
      Si original gana: <span style="color:var(--green)">+$${d.ganancia_si_original_gana}</span><br>
      Si hedge gana: <span style="color:var(--green)">+$${d.ganancia_si_hedge_gana}</span><br>
      Ganancia garantizada: <span style="color:${color};font-weight:700">$${d.ganancia_garantizada} (${d.roi_garantizado_pct}%)</span>`
    document.getElementById('hedge-detail').innerHTML = d.recomendacion
  } catch(e) { document.getElementById('h-res').innerHTML='<span style="color:var(--red)">Error: '+e+'</span>' }
}

async function calcArbitraje() {
  const c1 = document.getElementById('arb-1').value
  const cx = document.getElementById('arb-x').value
  const c2 = document.getElementById('arb-2').value
  const bank = document.getElementById('arb-bank').value
  const cuotas = {'1':parseFloat(c1),'X':parseFloat(cx),'2':parseFloat(c2)}
  try {
    const d = await api(`/api/mercados/arbitraje?bankroll=${bank}&cuotas=${encodeURIComponent(JSON.stringify(cuotas))}`)
    const color = d.hay_arbitraje?'var(--green)':'var(--red)'
    if (d.hay_arbitraje) {
      const stakes = d.stakes_optimos||{}
      document.getElementById('arb-res').innerHTML = `
        <div style="color:var(--green);font-size:13px;font-weight:700;margin-bottom:6px">âœ… ARBITRAJE DETECTADO +${d.margen_arb_pct}%</div>
        ${Object.entries(stakes).map(([k,v])=>`Apostar [${k}]: <span style="color:var(--text)">$${v}</span>`).join('<br>')}<br>
        Ganancia garantizada: <span style="color:var(--green);font-weight:700">$${d.ganancia_garantizada}</span>`
      document.getElementById('hedge-detail').innerHTML = `<span style="color:var(--green)">Arbitraje real â€” ${d.urgencia}</span>`
    } else {
      document.getElementById('arb-res').innerHTML = `<span style="color:var(--red)">Sin arbitraje â€” overround casa: ${d.overround_casa_pct}%</span>`
    }
  } catch(e) { document.getElementById('arb-res').innerHTML='<span style="color:var(--red)">Error: '+e+'</span>' }
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// OPTIMIZADOR PROGOL
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function loadProgolOpt(estrategia) {
  const el = document.getElementById('progolopt-res')
  el.innerHTML = 'Calculando...'
  try {
    let d, html = ''
    if (estrategia==='simple') {
      d = await api('/api/progol/optimizar/quiniela-simple')
      html = `<div style="margin-bottom:12px"><span style="color:var(--muted);font-size:10px">QUINIELA Ã“PTIMA</span>
        <div style="display:flex;flex-wrap:wrap;gap:5px;margin-top:8px">${(d.signos||[]).map((s,i)=>
          `<div style="background:${s==='1'?'rgba(52,211,153,.15)':s==='X'?'rgba(124,109,250,.15)':'rgba(248,113,113,.15)'};border:1px solid ${s==='1'?'var(--green)':s==='X'?'var(--purple)':'var(--red)'};border-radius:5px;padding:5px 10px;font-family:var(--mono);font-size:12px">
            <span style="color:var(--muted)">${i+1}.</span> <span style="font-weight:700">${s}</span>
          </div>`).join('')}
        </div>
        <div style="margin-top:10px;font-size:11px;font-family:var(--mono);color:var(--muted)">
          Prob. ganar: <span style="color:var(--gold)">${d.prob_ganar_pct}%</span> Â· Aciertos esperados: <span style="color:var(--text)">${d.aciertos_esperados}/14</span>
        </div></div>`
    } else if (estrategia==='diversificada') {
      d = await api('/api/progol/optimizar/diversificada?n=5')
      html = (d.quinielas||[]).map(q=>`
        <div style="margin-bottom:10px;padding:10px;background:var(--bg4);border-radius:7px">
          <div style="display:flex;justify-content:space-between;margin-bottom:6px">
            <span style="color:var(--muted);font-size:10px;font-family:var(--mono)">Quiniela ${q.quiniela_num}</span>
            <span style="color:var(--gold);font-size:10px;font-family:var(--mono)">P(ganar): ${q.prob_ganar_pct}%</span>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:3px">${(q.signos||[]).map((s,i)=>
            `<span style="background:${s==='1'?'rgba(52,211,153,.15)':s==='X'?'rgba(124,109,250,.15)':'rgba(248,113,113,.15)'};padding:2px 7px;border-radius:3px;font-family:var(--mono);font-size:11px">${s}</span>`).join('')}</div>
        </div>`).join('')
    } else {
      d = await api('/api/progol/optimizar/maxima-cobertura?n=3')
      html = `<div style="margin-bottom:10px;padding:10px;background:rgba(240,180,41,.05);border:1px solid rgba(240,180,41,.2);border-radius:7px">
        <div style="color:var(--gold);font-size:12px;font-weight:700">P(al menos 1 quiniela gana 11+): ${d.prob_al_menos_una_pct}%</div>
        <div style="color:var(--muted);font-size:10px;font-family:var(--mono)">Costo total: $${d.costo_total_mxn}</div>
      </div>` + (d.quinielas||[]).map(q=>`
        <div style="margin-bottom:8px;padding:8px;background:var(--bg4);border-radius:6px">
          <div style="display:flex;justify-content:space-between;margin-bottom:5px">
            <span style="color:var(--muted);font-size:10px">Q${q.quiniela_num}</span>
            <span style="color:var(--gold);font-size:10px;font-family:var(--mono)">${q.prob_gana_pct}% Â· ${q.aciertos_esp} esp.</span>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:3px">${(q.signos||[]).map(s=>
            `<span style="background:${s==='1'?'rgba(52,211,153,.15)':s==='X'?'rgba(124,109,250,.15)':'rgba(248,113,113,.15)'};padding:2px 7px;border-radius:3px;font-family:var(--mono);font-size:11px">${s}</span>`).join('')}</div>
        </div>`).join('')
    }
    el.innerHTML = html || 'Sin resultados'
    document.getElementById('progolopt-analisis').style.display='none'
  } catch(e) { el.innerHTML='<span style="color:var(--red)">Error: '+e+'</span>' }
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// ML MODEL
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function loadML() {
  const home = document.getElementById('ml-home').value
  const away = document.getElementById('ml-away').value
  try {
    const d = await api('/api/ml/ensemble-vs-ml?home='+encodeURIComponent(home)+'&away='+encodeURIComponent(away))
    document.getElementById('ml-resultado').style.display='block'
    const fmt = (o, label) => o ? `
      <div>Local: <span style="color:var(--green)">${((o.local||0)*100).toFixed(1)}%</span></div>
      <div>Empate: <span style="color:var(--gold)">${((o.empate||0)*100).toFixed(1)}%</span></div>
      <div>Visitante: <span style="color:var(--red)">${((o.visitante||0)*100).toFixed(1)}%</span></div>
      <div style="margin-top:6px;color:var(--purple2);font-weight:700">[${o.pronostico||'?'}] ${o.confianza_pct||0}%</div>` : '<span style="color:var(--muted)">No disponible</span>'
    document.getElementById('ml-ens').innerHTML = fmt(d.ensemble)
    document.getElementById('ml-gb').innerHTML = d.ml&&d.ml.disponible ? fmt(d.ml) : '<span style="color:var(--muted)">Necesita mÃ¡s datos histÃ³ricos</span>'
    document.getElementById('ml-comb').innerHTML = d.combinado ? fmt(d.combinado) : '<span style="color:var(--muted)">â€”</span>'
    // Feature importance
    const fi = await api('/api/ml/feature-importance')
    document.getElementById('ml-feat').innerHTML = (fi.features||[]).slice(0,8).map(f=>
      `<div style="display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid var(--border)">
        <span style="color:var(--muted)">${f.feature}</span>
        <span style="color:var(--text)">${(f.importancia*100).toFixed(1)}%</span>
      </div>`).join('')
  } catch(e) { document.getElementById('ml-resultado').style.display='none'; alert('Error: '+e) }
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// MULTI-LIGA
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function loadLiga(ligaKey) {
  document.getElementById('ligas-panel').style.display='block'
  document.getElementById('ligas-res').innerHTML='Cargando datos reales...'
  document.querySelectorAll('.liga-btn').forEach(b=>b.style.opacity='0.6')
  try {
    const d = await api('/api/ligas/predicciones-liga?liga='+ligaKey)
    document.getElementById('ligas-title').textContent = (d.liga||{}).nombre||ligaKey
    const preds = d.predicciones || []

    // Con partidos â†’ mostrar predicciones
    if (preds.length) {
      document.getElementById('ligas-badge').textContent = preds.length+' partidos'
      const fuente = d.usa_datos_reales ? `<div style="font-size:10px;font-family:var(--mono);color:var(--green);margin-bottom:8px">&#10003; ${d.fuente} Â· ${d.partidos_entrenamiento} partidos de entrenamiento</div>` : ''
      document.getElementById('ligas-res').innerHTML = fuente + preds.map(p=>`
        <div style="display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid var(--border)">
          <span style="color:var(--text)">${p.home} <span style="color:var(--muted)">vs</span> ${p.away}</span>
          <div style="display:flex;gap:8px;align-items:center">
            <span style="color:var(--muted);font-size:10px">${((p.prob_local||0)*100).toFixed(0)}%&middot;${((p.prob_empate||0)*100).toFixed(0)}%&middot;${((p.prob_visitante||0)*100).toFixed(0)}%</span>
            <span style="background:${p.confianza_pct>55?'rgba(52,211,153,.15)':'rgba(124,109,250,.1)'};color:${p.confianza_pct>55?'var(--green)':'var(--purple2)'};padding:3px 10px;border-radius:4px;font-family:var(--mono);font-size:11px;font-weight:700">[${p.pronostico}] ${p.confianza_pct}%</span>
          </div>
        </div>`).join('')
      return
    }

    // Sin partidos â†’ mostrar ranking ELO si existe
    document.getElementById('ligas-badge').textContent = 'receso'
    const rank = d.ranking_elo || []
    let html = `<div style="font-size:11px;font-family:var(--mono);color:var(--gold);margin-bottom:10px;line-height:1.5">${d.aviso || 'Sin partidos prÃ³ximos'}</div>`
    if (rank.length) {
      html += '<div style="font-size:10px;font-family:var(--mono);color:var(--purple2);margin-bottom:6px;font-weight:700">RANKING ELO ACTUAL</div>'
      html += rank.map((e,i)=>`<div style="display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px solid var(--border);font-family:var(--mono);font-size:11px"><span style="color:var(--text)">${i+1}. ${e.equipo}</span><span style="color:var(--purple2);font-weight:700">${e.elo}</span></div>`).join('')
    }
    document.getElementById('ligas-res').innerHTML = html
  } catch(e) { document.getElementById('ligas-res').innerHTML='<span style="color:var(--red)">'+e+'</span>' }
}


// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// SSE â€” Alertas en tiempo real
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// CUENTAS & CAMUFLAJE
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function loadCuentas() {
  try {
    const resp = await api('/api/cuentas/listar')
    const cuentas = Array.isArray(resp) ? resp : (resp.cuentas || [])
    const activas = cuentas.filter(c => c.activa)
    document.getElementById('ct-activas').textContent = activas.length
    const avgHealth = activas.length ? Math.round(activas.reduce((s,c)=>s+(c.health_score||100),0)/activas.length) : 100
    document.getElementById('ct-health').textContent = avgHealth + '/100'
    const enRiesgo = activas.filter(c => (c.health_score||100) < 40).length
    document.getElementById('ct-riesgo').textContent = enRiesgo

    // Llenar selector de casas para reportar limitaciÃ³n
    const sel = document.getElementById('ct-casa-lim')
    sel.innerHTML = '<option value="">Selecciona la casa...</option>' +
      activas.map(c => `<option value="${c.casa_key}">${c.nombre}</option>`).join('')

    if (!activas.length) {
      document.getElementById('ct-lista').innerHTML = '<span style="color:var(--muted)">Sin cuentas registradas. Agrega tu primera casa arriba.</span>'
      return
    }

    document.getElementById('ct-lista').innerHTML = `
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px">
        ${activas.map(c => {
          const color = c.estado==='verde'?'var(--green)':c.estado==='amarillo'?'var(--gold)':'var(--red)'
          const icon  = c.estado==='verde'?'ðŸŸ¢':c.estado==='amarillo'?'ðŸŸ¡':'ðŸ”´'
          return `<div style="background:var(--bg4);border:1px solid ${color}33;border-radius:8px;padding:12px">
            <div style="display:flex;justify-content:space-between;margin-bottom:8px">
              <span style="color:var(--text);font-weight:700">${icon} ${c.nombre}</span>
              <span style="color:${color};font-size:10px">${c.health_score||100}/100</span>
            </div>
            <div style="color:var(--muted);font-size:10px">Tipo: ${c.tipo} Â· ${c.tolerancia||''}</div>
            <div style="color:var(--muted);font-size:10px">LÃ­mite: $${c.limite_actual||0} (${c.pct_limite_restante||100}%)</div>
            <div style="margin-top:6px;background:var(--bg3);border-radius:3px;height:4px">
              <div style="background:${color};width:${c.health_score||100}%;height:4px;border-radius:3px"></div>
            </div>
          </div>`
        }).join('')}
      </div>`
  } catch(e) {
    document.getElementById('ct-lista').innerHTML = '<span style="color:var(--red)">Error: '+e+'</span>'
  }
}

async function registrarCuenta() {
  const casa_key = document.getElementById('ct-casa').value
  const limite   = parseFloat(document.getElementById('ct-limite').value)
  const balance  = parseFloat(document.getElementById('ct-balance').value||0)
  const notas    = document.getElementById('ct-notas').value
  if (!limite) { document.getElementById('ct-msg').textContent='Ingresa el lÃ­mite mÃ¡ximo'; return }
  try {
    const r = await fetch('/api/cuentas/registrar',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({casa_key,limite_inicial:limite,balance,notas})})
    const d = await r.json()
    const msg = document.getElementById('ct-msg')
    msg.textContent = d.error ? 'âŒ '+d.error : 'âœ… '+d.casa+' registrada con lÃ­mite $'+d.limite
    msg.style.color = d.error?'var(--red)':'var(--green)'
    if (!d.error) loadCuentas()
  } catch(e) { document.getElementById('ct-msg').textContent='âŒ '+e }
}

async function reportarLimitacion() {
  const casa_key    = document.getElementById('ct-casa-lim').value
  const nuevo_limite = parseFloat(document.getElementById('ct-nuevo-lim').value)
  const razon       = document.getElementById('ct-razon').value
  if (!casa_key || !nuevo_limite) { document.getElementById('ct-lim-msg').textContent='Completa los campos'; return }
  try {
    const r = await fetch('/api/cuentas/limite',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({casa_key,nuevo_limite,razon})})
    const d = await r.json()
    const msg = document.getElementById('ct-lim-msg')
    if (d.error) { msg.style.color='var(--red)'; msg.textContent='âŒ '+d.error; return }
    const color = d.nivel==='CRÃTICA'?'var(--red)':d.nivel==='MODERADA'?'var(--gold)':'var(--muted)'
    msg.style.color = color
    msg.textContent = `${d.nivel}: -${d.reduccion_pct}% en ${d.casa}. Health: ${d.health_score}/100`
    document.getElementById('ct-analisis').innerHTML =
      `<div style="color:${color};margin-bottom:6px">âš ï¸ ${d.recomendacion}</div>`
    loadCuentas()
  } catch(e) { document.getElementById('ct-lim-msg').textContent='âŒ '+e }
}

async function loadCamuflaje() {
  const perfil  = document.getElementById('ct-perfil-sel').value
  const bankroll = document.getElementById('ct-bank').value
  document.getElementById('ct-perfil').textContent = perfil.charAt(0).toUpperCase()+perfil.slice(1)
  try {
    const d = await api(`/api/cuentas/camuflaje/plan?perfil=${perfil}&bankroll=${bankroll}`)
    const r = d.resumen || {}
    const camuflajes = d.apuestas_camuflaje || []
    document.getElementById('ct-camuflaje').innerHTML = `
      <div style="background:rgba(124,109,250,.08);border:1px solid rgba(124,109,250,.2);border-radius:8px;padding:12px;margin-bottom:12px">
        <div style="color:var(--purple2);font-weight:700;margin-bottom:6px">Plan Semana ${d.semana||''}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;font-size:11px">
          <div>Sharp: <span style="color:var(--green)">${r.apuestas_sharp||0}</span></div>
          <div>Camuflaje: <span style="color:var(--gold)">${r.apuestas_camuflaje||0}</span></div>
          <div>Ratio: <span style="color:var(--text)">${r.ratio_real||''}</span></div>
        </div>
        <div style="color:var(--muted);font-size:10px;margin-top:6px">${d.advertencia||''}</div>
        <div style="color:var(--muted);font-size:10px">Vida estimada de cuentas: ~${d.semanas_vida_estimada||0} semanas</div>
      </div>
      <div style="color:var(--text);margin-bottom:6px;font-weight:700">ðŸŽ­ Apuestas de Camuflaje Sugeridas:</div>
      ${camuflajes.map(c=>`
        <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border)">
          <div>
            <span style="color:var(--gold)">â—‡</span>
            <span style="color:var(--text)">${c.mercado}</span>
            <span style="color:var(--muted)"> Â· ${c.liga}</span>
          </div>
          <div>
            <span style="color:var(--muted)">@${c.cuota}</span>
            <span style="color:var(--text)"> $${c.monto}</span>
            <span style="color:var(--muted)"> en ${c.casa}</span>
          </div>
        </div>`).join('')}`
  } catch(e) { document.getElementById('ct-camuflaje').innerHTML='<span style="color:var(--red)">'+e+'</span>' }
}

async function loadAnalisisCuenta() {
  try {
    const d = await api('/api/cuentas/camuflaje/analizar')
    const color = d.riesgo==='ALTO'?'var(--red)':d.riesgo==='MEDIO'?'var(--gold)':'var(--green)'
    const alertas = d.alertas || []
    const recs    = d.recomendaciones || []
    document.getElementById('ct-analisis').innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
        <div style="font-size:24px;font-weight:800;color:${color}">${d.score_riesgo||0}/100</div>
        <div>
          <div style="color:${color};font-weight:700">Riesgo ${d.riesgo||'BAJO'}</div>
          <div style="color:var(--muted);font-size:10px">Score de exposiciÃ³n a limitaciones</div>
        </div>
      </div>
      ${alertas.length ? alertas.map(a=>`
        <div style="background:rgba(248,113,113,.05);border-left:3px solid var(--red);padding:6px 10px;margin-bottom:5px;border-radius:0 5px 5px 0">
          <div style="color:var(--red);font-size:10px">${a.urgencia}</div>
          <div style="color:var(--text);font-size:11px">${a.detalle}</div>
        </div>`).join('') : '<div style="color:var(--green)">âœ“ Sin alertas de comportamiento</div>'}
      ${recs.length ? '<div style="margin-top:8px;color:var(--muted)">'+recs.map(r=>'â†’ '+r).join('<br>')+'</div>' : ''}`
  } catch(e) { document.getElementById('ct-analisis').innerHTML='<span style="color:var(--red)">'+e+'</span>' }
}

async function loadRotacion() {
  const monto = document.getElementById('ct-monto-rot').value
  try {
    const d = await api(`/api/cuentas/rotacion?monto=${monto}`)
    if (d.error) { document.getElementById('ct-rotacion').innerHTML='<span style="color:var(--muted)">'+d.error+'</span>'; return }
    document.getElementById('ct-rotacion').innerHTML = `
      <div style="color:var(--muted);font-size:10px;margin-bottom:8px">Total a apostar: <span style="color:var(--text)">$${d.total_a_apostar}</span> de $${d.monto_total}</div>
      ${(d.distribucion||[]).map(c=>{
        const color = c.estado==='verde'?'var(--green)':c.estado==='amarillo'?'var(--gold)':'var(--red)'
        return `<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--border)">
          <div>
            <span style="color:var(--text);font-weight:700">${c.casa}</span>
            <span style="color:var(--muted)"> Â· Health ${c.health_score}/100</span>
          </div>
          <div>
            <span style="color:${color};font-weight:700">$${c.monto}</span>
            <span style="color:var(--muted)"> (${c.pct_del_total}%)</span>
          </div>
        </div>`}).join('')}`
  } catch(e) { document.getElementById('ct-rotacion').innerHTML='<span style="color:var(--red)">'+e+'</span>' }
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// VALUE PRO
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function calcValuePro() {
  const prob = document.getElementById('vp-prob').value
  const cuota = document.getElementById('vp-cuota').value
  const pinn = document.getElementById('vp-pinnacle').value
  const bank = document.getElementById('vp-bank').value
  const frac = document.getElementById('vp-frac').value
  let url = `/api/value/analizar?prob=${prob}&cuota=${cuota}&bankroll=${bank}&fraccion=${frac}`
  if (pinn) url += `&pinnacle=${pinn}`
  try {
    const d = await api(url)
    const edgeColor = d.edge_modelo_pct > 4 ? 'var(--green)' : d.edge_modelo_pct > 0 ? 'var(--gold)' : 'var(--red)'
    let html = `
      <div style="text-align:center;padding:12px 0;border-bottom:1px solid var(--border);margin-bottom:12px">
        <div style="font-size:32px;font-weight:800;color:${edgeColor}">${d.edge_modelo_pct > 0 ? '+' : ''}${d.edge_modelo_pct}%</div>
        <div style="font-size:11px;color:var(--muted)">EDGE Â· ${d.clasificacion}</div>
      </div>
      <div style="line-height:2">
        <div>Prob. modelo: <span style="color:var(--text)">${d.prob_modelo_pct}%</span></div>
        <div>Prob. implÃ­cita casa: <span style="color:var(--text)">${d.prob_implicita_pct}%</span></div>
        <div>Valor esperado/unidad: <span style="color:${d.ev_por_unidad>0?'var(--green)':'var(--red)'}">${d.ev_por_unidad}</span></div>`
    if (d.edge_mercado_pct !== undefined) {
      html += `<div style="margin-top:6px;padding-top:6px;border-top:1px solid var(--border)">
        Edge vs Pinnacle: <span style="color:${d.edge_mercado_pct>0?'var(--green)':'var(--red)'}">${d.edge_mercado_pct}%</span></div>
        <div>Confianza: <span style="color:var(--purple2)">${d.confianza}</span></div>`
    }
    if (d.kelly) {
      html += `<div style="margin-top:10px;padding:10px;background:rgba(240,180,41,.08);border-radius:7px">
        <div style="color:var(--gold);font-weight:700;margin-bottom:4px">ðŸ’° STAKE KELLY</div>
        <div>Apostar: <span style="color:var(--gold);font-size:16px;font-weight:700">$${d.kelly.stake_sugerido || 0}</span></div>
        <div style="font-size:10px;color:var(--muted)">${d.kelly.kelly_aplicado_pct}% del bankroll (${d.kelly.fraccion_usada} Kelly)</div>
      </div>`
    }
    html += `<div style="margin-top:10px;padding:8px;background:var(--bg4);border-radius:6px;color:${edgeColor}">${d.recomendacion}</div></div>`
    document.getElementById('vp-resultado').innerHTML = html
  } catch(e) { document.getElementById('vp-resultado').innerHTML = '<span style="color:var(--red)">Error: '+e+'</span>' }
}

async function calcCLVpro() {
  const ap = document.getElementById('clv-apostada').value
  const ci = document.getElementById('clv-cierre').value
  try {
    const d = await api(`/api/value/clv?apostada=${ap}&cierre=${ci}`)
    const color = d.positivo ? 'var(--green)' : 'var(--red)'
    document.getElementById('clv-pro-res').innerHTML = `
      <div style="display:flex;align-items:center;gap:14px">
        <div style="font-size:28px;font-weight:800;color:${color}">${d.clv_pct>0?'+':''}${d.clv_pct}%</div>
        <div>
          <div style="color:${color};font-weight:700">${d.interpretacion}</div>
          <div style="font-size:10px;color:var(--muted)">${d.nota}</div>
        </div>
      </div>`
  } catch(e) { document.getElementById('clv-pro-res').innerHTML = '<span style="color:var(--red)">Error: '+e+'</span>' }
}

function conectarSSE() {
  const evtSource = new EventSource('/api/eventos')
  evtSource.onmessage = function(e) {
    try {
      const data = JSON.parse(e.data)
      if (data.tipo === 'conectado') {
        document.querySelector('.live-pill').style.opacity = '1'
        return
      }
      if (data.tipo === 'nlp_alerta' || data.tipo === 'steam_move' || data.tipo === 'value_bet') {
        mostrarToast(data)
      }
    } catch(err) {}
  }
  evtSource.onerror = function() {
    document.querySelector('.live-pill').style.opacity = '0.3'
    setTimeout(conectarSSE, 5000) // reconectar en 5s
  }
}

function mostrarToast(data) {
  const toast = document.createElement('div')
  const color = data.tipo==='nlp_alerta'?'var(--red)':data.tipo==='steam_move'?'var(--gold)':'var(--green)'
  const icon  = data.tipo==='nlp_alerta'?'ðŸš¨':data.tipo==='steam_move'?'âš¡':'ðŸ’°'
  toast.style.cssText = `position:fixed;bottom:20px;right:20px;background:var(--bg3);border:1px solid ${color};
    border-radius:10px;padding:12px 16px;z-index:9999;font-family:var(--mono);font-size:11px;
    max-width:280px;box-shadow:0 4px 20px rgba(0,0,0,.5);animation:fu .3s ease`
  toast.innerHTML = `<div style="color:${color};font-weight:700;margin-bottom:4px">${icon} ${data.tipo.replace('_',' ').toUpperCase()}</div>
    <div style="color:var(--muted)">${data.partido||data.job||''}</div>`
  document.body.appendChild(toast)
  setTimeout(() => toast.remove(), 6000)
}


// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// CUENTAS & CAMUFLAJE
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function loadCuentas() {
  try {
    const resp = await api('/api/cuentas/listar')
    const cuentas = Array.isArray(resp) ? resp : (resp.cuentas || [])
    const activas = cuentas.filter(c => c.activa)
    document.getElementById('ct-activas').textContent = activas.length
    const avgHealth = activas.length ? Math.round(activas.reduce((s,c)=>s+(c.health_score||100),0)/activas.length) : 100
    document.getElementById('ct-health').textContent = avgHealth + '/100'
    const enRiesgo = activas.filter(c => (c.health_score||100) < 40).length
    document.getElementById('ct-riesgo').textContent = enRiesgo

    // Llenar selector de casas para reportar limitaciÃ³n
    const sel = document.getElementById('ct-casa-lim')
    sel.innerHTML = '<option value="">Selecciona la casa...</option>' +
      activas.map(c => `<option value="${c.casa_key}">${c.nombre}</option>`).join('')

    if (!activas.length) {
      document.getElementById('ct-lista').innerHTML = '<span style="color:var(--muted)">Sin cuentas registradas. Agrega tu primera casa arriba.</span>'
      return
    }

    document.getElementById('ct-lista').innerHTML = `
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px">
        ${activas.map(c => {
          const color = c.estado==='verde'?'var(--green)':c.estado==='amarillo'?'var(--gold)':'var(--red)'
          const icon  = c.estado==='verde'?'ðŸŸ¢':c.estado==='amarillo'?'ðŸŸ¡':'ðŸ”´'
          return `<div style="background:var(--bg4);border:1px solid ${color}33;border-radius:8px;padding:12px">
            <div style="display:flex;justify-content:space-between;margin-bottom:8px">
              <span style="color:var(--text);font-weight:700">${icon} ${c.nombre}</span>
              <span style="color:${color};font-size:10px">${c.health_score||100}/100</span>
            </div>
            <div style="color:var(--muted);font-size:10px">Tipo: ${c.tipo} Â· ${c.tolerancia||''}</div>
            <div style="color:var(--muted);font-size:10px">LÃ­mite: $${c.limite_actual||0} (${c.pct_limite_restante||100}%)</div>
            <div style="margin-top:6px;background:var(--bg3);border-radius:3px;height:4px">
              <div style="background:${color};width:${c.health_score||100}%;height:4px;border-radius:3px"></div>
            </div>
          </div>`
        }).join('')}
      </div>`
  } catch(e) {
    document.getElementById('ct-lista').innerHTML = '<span style="color:var(--red)">Error: '+e+'</span>'
  }
}

async function registrarCuenta() {
  const casa_key = document.getElementById('ct-casa').value
  const limite   = parseFloat(document.getElementById('ct-limite').value)
  const balance  = parseFloat(document.getElementById('ct-balance').value||0)
  const notas    = document.getElementById('ct-notas').value
  if (!limite) { document.getElementById('ct-msg').textContent='Ingresa el lÃ­mite mÃ¡ximo'; return }
  try {
    const r = await fetch('/api/cuentas/registrar',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({casa_key,limite_inicial:limite,balance,notas})})
    const d = await r.json()
    const msg = document.getElementById('ct-msg')
    msg.textContent = d.error ? 'âŒ '+d.error : 'âœ… '+d.casa+' registrada con lÃ­mite $'+d.limite
    msg.style.color = d.error?'var(--red)':'var(--green)'
    if (!d.error) loadCuentas()
  } catch(e) { document.getElementById('ct-msg').textContent='âŒ '+e }
}

async function reportarLimitacion() {
  const casa_key    = document.getElementById('ct-casa-lim').value
  const nuevo_limite = parseFloat(document.getElementById('ct-nuevo-lim').value)
  const razon       = document.getElementById('ct-razon').value
  if (!casa_key || !nuevo_limite) { document.getElementById('ct-lim-msg').textContent='Completa los campos'; return }
  try {
    const r = await fetch('/api/cuentas/limite',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({casa_key,nuevo_limite,razon})})
    const d = await r.json()
    const msg = document.getElementById('ct-lim-msg')
    if (d.error) { msg.style.color='var(--red)'; msg.textContent='âŒ '+d.error; return }
    const color = d.nivel==='CRÃTICA'?'var(--red)':d.nivel==='MODERADA'?'var(--gold)':'var(--muted)'
    msg.style.color = color
    msg.textContent = `${d.nivel}: -${d.reduccion_pct}% en ${d.casa}. Health: ${d.health_score}/100`
    document.getElementById('ct-analisis').innerHTML =
      `<div style="color:${color};margin-bottom:6px">âš ï¸ ${d.recomendacion}</div>`
    loadCuentas()
  } catch(e) { document.getElementById('ct-lim-msg').textContent='âŒ '+e }
}

async function loadCamuflaje() {
  const perfil  = document.getElementById('ct-perfil-sel').value
  const bankroll = document.getElementById('ct-bank').value
  document.getElementById('ct-perfil').textContent = perfil.charAt(0).toUpperCase()+perfil.slice(1)
  try {
    const d = await api(`/api/cuentas/camuflaje/plan?perfil=${perfil}&bankroll=${bankroll}`)
    const r = d.resumen || {}
    const camuflajes = d.apuestas_camuflaje || []
    document.getElementById('ct-camuflaje').innerHTML = `
      <div style="background:rgba(124,109,250,.08);border:1px solid rgba(124,109,250,.2);border-radius:8px;padding:12px;margin-bottom:12px">
        <div style="color:var(--purple2);font-weight:700;margin-bottom:6px">Plan Semana ${d.semana||''}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;font-size:11px">
          <div>Sharp: <span style="color:var(--green)">${r.apuestas_sharp||0}</span></div>
          <div>Camuflaje: <span style="color:var(--gold)">${r.apuestas_camuflaje||0}</span></div>
          <div>Ratio: <span style="color:var(--text)">${r.ratio_real||''}</span></div>
        </div>
        <div style="color:var(--muted);font-size:10px;margin-top:6px">${d.advertencia||''}</div>
        <div style="color:var(--muted);font-size:10px">Vida estimada de cuentas: ~${d.semanas_vida_estimada||0} semanas</div>
      </div>
      <div style="color:var(--text);margin-bottom:6px;font-weight:700">ðŸŽ­ Apuestas de Camuflaje Sugeridas:</div>
      ${camuflajes.map(c=>`
        <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border)">
          <div>
            <span style="color:var(--gold)">â—‡</span>
            <span style="color:var(--text)">${c.mercado}</span>
            <span style="color:var(--muted)"> Â· ${c.liga}</span>
          </div>
          <div>
            <span style="color:var(--muted)">@${c.cuota}</span>
            <span style="color:var(--text)"> $${c.monto}</span>
            <span style="color:var(--muted)"> en ${c.casa}</span>
          </div>
        </div>`).join('')}`
  } catch(e) { document.getElementById('ct-camuflaje').innerHTML='<span style="color:var(--red)">'+e+'</span>' }
}

async function loadAnalisisCuenta() {
  try {
    const d = await api('/api/cuentas/camuflaje/analizar')
    const color = d.riesgo==='ALTO'?'var(--red)':d.riesgo==='MEDIO'?'var(--gold)':'var(--green)'
    const alertas = d.alertas || []
    const recs    = d.recomendaciones || []
    document.getElementById('ct-analisis').innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
        <div style="font-size:24px;font-weight:800;color:${color}">${d.score_riesgo||0}/100</div>
        <div>
          <div style="color:${color};font-weight:700">Riesgo ${d.riesgo||'BAJO'}</div>
          <div style="color:var(--muted);font-size:10px">Score de exposiciÃ³n a limitaciones</div>
        </div>
      </div>
      ${alertas.length ? alertas.map(a=>`
        <div style="background:rgba(248,113,113,.05);border-left:3px solid var(--red);padding:6px 10px;margin-bottom:5px;border-radius:0 5px 5px 0">
          <div style="color:var(--red);font-size:10px">${a.urgencia}</div>
          <div style="color:var(--text);font-size:11px">${a.detalle}</div>
        </div>`).join('') : '<div style="color:var(--green)">âœ“ Sin alertas de comportamiento</div>'}
      ${recs.length ? '<div style="margin-top:8px;color:var(--muted)">'+recs.map(r=>'â†’ '+r).join('<br>')+'</div>' : ''}`
  } catch(e) { document.getElementById('ct-analisis').innerHTML='<span style="color:var(--red)">'+e+'</span>' }
}

async function loadRotacion() {
  const monto = document.getElementById('ct-monto-rot').value
  try {
    const d = await api(`/api/cuentas/rotacion?monto=${monto}`)
    if (d.error) { document.getElementById('ct-rotacion').innerHTML='<span style="color:var(--muted)">'+d.error+'</span>'; return }
    document.getElementById('ct-rotacion').innerHTML = `
      <div style="color:var(--muted);font-size:10px;margin-bottom:8px">Total a apostar: <span style="color:var(--text)">$${d.total_a_apostar}</span> de $${d.monto_total}</div>
      ${(d.distribucion||[]).map(c=>{
        const color = c.estado==='verde'?'var(--green)':c.estado==='amarillo'?'var(--gold)':'var(--red)'
        return `<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--border)">
          <div>
            <span style="color:var(--text);font-weight:700">${c.casa}</span>
            <span style="color:var(--muted)"> Â· Health ${c.health_score}/100</span>
          </div>
          <div>
            <span style="color:${color};font-weight:700">$${c.monto}</span>
            <span style="color:var(--muted)"> (${c.pct_del_total}%)</span>
          </div>
        </div>`}).join('')}`
  } catch(e) { document.getElementById('ct-rotacion').innerHTML='<span style="color:var(--red)">'+e+'</span>' }
}


// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// VALUE PRO
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function calcValuePro() {
  const prob = document.getElementById('vp-prob').value
  const cuota = document.getElementById('vp-cuota').value
  const pinn = document.getElementById('vp-pinnacle').value
  const bank = document.getElementById('vp-bank').value
  const frac = document.getElementById('vp-frac').value
  let url = `/api/value/analizar?prob=${prob}&cuota=${cuota}&bankroll=${bank}&fraccion=${frac}`
  if (pinn) url += `&pinnacle=${pinn}`
  try {
    const d = await api(url)
    const edgeColor = d.edge_modelo_pct > 4 ? 'var(--green)' : d.edge_modelo_pct > 0 ? 'var(--gold)' : 'var(--red)'
    let html = `
      <div style="text-align:center;padding:12px 0;border-bottom:1px solid var(--border);margin-bottom:12px">
        <div style="font-size:32px;font-weight:800;color:${edgeColor}">${d.edge_modelo_pct > 0 ? '+' : ''}${d.edge_modelo_pct}%</div>
        <div style="font-size:11px;color:var(--muted)">EDGE Â· ${d.clasificacion}</div>
      </div>
      <div style="line-height:2">
        <div>Prob. modelo: <span style="color:var(--text)">${d.prob_modelo_pct}%</span></div>
        <div>Prob. implÃ­cita casa: <span style="color:var(--text)">${d.prob_implicita_pct}%</span></div>
        <div>Valor esperado/unidad: <span style="color:${d.ev_por_unidad>0?'var(--green)':'var(--red)'}">${d.ev_por_unidad}</span></div>`
    if (d.edge_mercado_pct !== undefined) {
      html += `<div style="margin-top:6px;padding-top:6px;border-top:1px solid var(--border)">
        Edge vs Pinnacle: <span style="color:${d.edge_mercado_pct>0?'var(--green)':'var(--red)'}">${d.edge_mercado_pct}%</span></div>
        <div>Confianza: <span style="color:var(--purple2)">${d.confianza}</span></div>`
    }
    if (d.kelly) {
      html += `<div style="margin-top:10px;padding:10px;background:rgba(240,180,41,.08);border-radius:7px">
        <div style="color:var(--gold);font-weight:700;margin-bottom:4px">ðŸ’° STAKE KELLY</div>
        <div>Apostar: <span style="color:var(--gold);font-size:16px;font-weight:700">$${d.kelly.stake_sugerido || 0}</span></div>
        <div style="font-size:10px;color:var(--muted)">${d.kelly.kelly_aplicado_pct}% del bankroll (${d.kelly.fraccion_usada} Kelly)</div>
      </div>`
    }
    html += `<div style="margin-top:10px;padding:8px;background:var(--bg4);border-radius:6px;color:${edgeColor}">${d.recomendacion}</div></div>`
    document.getElementById('vp-resultado').innerHTML = html
  } catch(e) { document.getElementById('vp-resultado').innerHTML = '<span style="color:var(--red)">Error: '+e+'</span>' }
}

async function calcCLVpro() {
  const ap = document.getElementById('clv-apostada').value
  const ci = document.getElementById('clv-cierre').value
  try {
    const d = await api(`/api/value/clv?apostada=${ap}&cierre=${ci}`)
    const color = d.positivo ? 'var(--green)' : 'var(--red)'
    document.getElementById('clv-pro-res').innerHTML = `
      <div style="display:flex;align-items:center;gap:14px">
        <div style="font-size:28px;font-weight:800;color:${color}">${d.clv_pct>0?'+':''}${d.clv_pct}%</div>
        <div>
          <div style="color:${color};font-weight:700">${d.interpretacion}</div>
          <div style="font-size:10px;color:var(--muted)">${d.nota}</div>
        </div>
      </div>`
  } catch(e) { document.getElementById('clv-pro-res').innerHTML = '<span style="color:var(--red)">Error: '+e+'</span>' }
}

conectarSSE()
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// VALUE PRO
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function calcValuePro() {
  const prob = document.getElementById('vp-prob').value
  const cuota = document.getElementById('vp-cuota').value
  const pinn = document.getElementById('vp-pinnacle').value
  const bank = document.getElementById('vp-bank').value
  const frac = document.getElementById('vp-frac').value
  let url = `/api/value/analizar?prob=${prob}&cuota=${cuota}&bankroll=${bank}&fraccion=${frac}`
  if (pinn) url += `&pinnacle=${pinn}`
  try {
    const d = await api(url)
    const edgeColor = d.edge_modelo_pct > 4 ? 'var(--green)' : d.edge_modelo_pct > 0 ? 'var(--gold)' : 'var(--red)'
    let html = `
      <div style="text-align:center;padding:12px 0;border-bottom:1px solid var(--border);margin-bottom:12px">
        <div style="font-size:32px;font-weight:800;color:${edgeColor}">${d.edge_modelo_pct > 0 ? '+' : ''}${d.edge_modelo_pct}%</div>
        <div style="font-size:11px;color:var(--muted)">EDGE Â· ${d.clasificacion}</div>
      </div>
      <div style="line-height:2">
        <div>Prob. modelo: <span style="color:var(--text)">${d.prob_modelo_pct}%</span></div>
        <div>Prob. implÃ­cita casa: <span style="color:var(--text)">${d.prob_implicita_pct}%</span></div>
        <div>Valor esperado/unidad: <span style="color:${d.ev_por_unidad>0?'var(--green)':'var(--red)'}">${d.ev_por_unidad}</span></div>`
    if (d.edge_mercado_pct !== undefined) {
      html += `<div style="margin-top:6px;padding-top:6px;border-top:1px solid var(--border)">
        Edge vs Pinnacle: <span style="color:${d.edge_mercado_pct>0?'var(--green)':'var(--red)'}">${d.edge_mercado_pct}%</span></div>
        <div>Confianza: <span style="color:var(--purple2)">${d.confianza}</span></div>`
    }
    if (d.kelly) {
      html += `<div style="margin-top:10px;padding:10px;background:rgba(240,180,41,.08);border-radius:7px">
        <div style="color:var(--gold);font-weight:700;margin-bottom:4px">ðŸ’° STAKE KELLY</div>
        <div>Apostar: <span style="color:var(--gold);font-size:16px;font-weight:700">$${d.kelly.stake_sugerido || 0}</span></div>
        <div style="font-size:10px;color:var(--muted)">${d.kelly.kelly_aplicado_pct}% del bankroll (${d.kelly.fraccion_usada} Kelly)</div>
      </div>`
    }
    html += `<div style="margin-top:10px;padding:8px;background:var(--bg4);border-radius:6px;color:${edgeColor}">${d.recomendacion}</div></div>`
    document.getElementById('vp-resultado').innerHTML = html
  } catch(e) { document.getElementById('vp-resultado').innerHTML = '<span style="color:var(--red)">Error: '+e+'</span>' }
}

async function calcCLVpro() {
  const ap = document.getElementById('clv-apostada').value
  const ci = document.getElementById('clv-cierre').value
  try {
    const d = await api(`/api/value/clv?apostada=${ap}&cierre=${ci}`)
    const color = d.positivo ? 'var(--green)' : 'var(--red)'
    document.getElementById('clv-pro-res').innerHTML = `
      <div style="display:flex;align-items:center;gap:14px">
        <div style="font-size:28px;font-weight:800;color:${color}">${d.clv_pct>0?'+':''}${d.clv_pct}%</div>
        <div>
          <div style="color:${color};font-weight:700">${d.interpretacion}</div>
          <div style="font-size:10px;color:var(--muted)">${d.nota}</div>
        </div>
      </div>`
  } catch(e) { document.getElementById('clv-pro-res').innerHTML = '<span style="color:var(--red)">Error: '+e+'</span>' }
}

async function initDashboard() {
  document.getElementById('dash-sub').textContent = 'cargando datos en tiempo real...'

  // Progol mini
  try {
    const j = await api('/api/progol/jornada')
    if (j.error || !j.partidos || !j.partidos.length) {
      document.getElementById('dash-progol').innerHTML = `<p style="color:var(--gold);padding:12px;font-size:11px;font-family:var(--mono)">${j.aviso || j.error || 'Sin partidos en los proximos 7 dias'}</p>`
    } else {
      const rows = j.partidos.slice(0,5).map(p => `
        <div class="prog-row">
          <span class="prog-num">${p.numero}</span>
          <div><div class="prog-match">${p.local_nombre||p.home}</div><div class="prog-liga">vs ${p.visitante_nombre||p.away}</div></div>
          <div class="prog-probs">
            <span class="prob-box${p.pronostico==='1'?' best':''}">1 ${((p.prob_local||0)*100).toFixed(0)}%</span>
            <span class="prob-box${p.pronostico==='X'?' best':''}">X ${((p.prob_empate||0)*100).toFixed(0)}%</span>
            <span class="prob-box${p.pronostico==='2'?' best':''}">2 ${((p.prob_visitante||0)*100).toFixed(0)}%</span>
          </div>
          <span class="prog-pick"><span class="badge ${p.confianza_pct>55?'bv':p.confianza_pct>42?'bs2':'bdim'}">[${p.pronostico}] ${p.confianza_pct}%</span></span>
        </div>`).join('')
      document.getElementById('dash-progol').innerHTML = rows
    }
  } catch(e) {
    document.getElementById('dash-progol').innerHTML = '<p style="color:var(--red);padding:12px;font-size:11px;font-family:var(--mono)">Error al cargar jornada: ' + e + '</p>'
  }

  // Value bets mini + tarjeta superior
  try {
    const v = await api('/api/odds/value-bets?edge_minimo=2')
    const vbs = v.value_bets || []
    // Actualizar tarjeta superior con datos reales
    const cnt = document.getElementById('dash-vb-count')
    const edg = document.getElementById('dash-vb-edge')
    if (cnt) cnt.textContent = vbs.length
    if (edg) {
      if (v.error || v.es_demo) edg.textContent = 'sin API'
      else if (!vbs.length) edg.textContent = 'sin edge ahora'
      else edg.textContent = `Edge prom +${(vbs.reduce((s,x)=>s+x.edge_porcentaje,0)/vbs.length).toFixed(1)}%`
    }
    // Lista mini
    if (v.error || v.es_demo) {
      document.getElementById('dash-vb').innerHTML = `<p style="color:var(--gold);padding:12px;font-size:11px;font-family:var(--mono)">${v.aviso || v.error}</p>`
    } else if (!vbs.length) {
      document.getElementById('dash-vb').innerHTML = '<p style="color:var(--muted);padding:12px;font-size:11px;font-family:var(--mono)">Sin value bets con edge &gt;= 2% en este momento</p>'
    } else {
      const rows = vbs.slice(0,4).map(d => `
        <div class="mm">
          <div><div class="mm-l" style="font-size:11px;color:var(--text)">${d.partido}</div>
          <div style="font-size:10px;color:var(--muted)">${d.resultado} &middot; ${d.casa}</div></div>
          <span class="badge ${d.edge_porcentaje>7?'bs2':'bv'}">+${d.edge_porcentaje}%</span>
        </div>`).join('')
      document.getElementById('dash-vb').innerHTML = `<div class="pb">${rows}</div>`
    }
  } catch(e) {
    const cnt = document.getElementById('dash-vb-count')
    if (cnt) cnt.textContent = '0'
    document.getElementById('dash-vb').innerHTML = '<p style="color:var(--red);padding:12px;font-size:11px;font-family:var(--mono)">Error: ' + e + '</p>'
  }

  loadAlertas('dash-alertas')
  document.getElementById('dash-sub').textContent = 'todos los mÃ³dulos activos Â· ' + new Date().toLocaleTimeString('es-MX',{hour12:false})
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// PROGOL
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function loadProgol() {
  const btn = document.getElementById('prog-btn')
  btn.textContent = 'Cargando...'; btn.disabled = true
  document.getElementById('prog-body').innerHTML = '<div class="loading"><div class="dot"></div><div class="dot"></div><div class="dot"></div>Ejecutando Dixon-Coles + ELO + Poisson...</div>'

  try {
    const d = await api('/api/progol/jornada')
    setAPIStatus(true)

    // En receso â€” mostrar aviso + ranking ELO actualizado
    if (d.en_receso || !d.partidos || !d.partidos.length) {
      const rankHtml = (d.ranking_elo || []).length
        ? '<div style="padding:12px 14px"><div style="font-size:11px;font-family:var(--mono);color:var(--purple2);margin-bottom:8px;font-weight:700">RANKING ELO ACTUAL (temporada real)</div>' +
          d.ranking_elo.map((e,i) => `<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--border);font-family:var(--mono);font-size:11px">
            <span style="color:var(--text)">${i+1}. ${e.equipo}</span>
            <span style="color:var(--purple2);font-weight:700">${e.elo}</span></div>`).join('') + '</div>'
        : ''
      document.getElementById('prog-body').innerHTML =
        `<div style="padding:16px;font-family:var(--mono);font-size:11px;color:var(--gold);line-height:1.6;border-bottom:1px solid var(--border)">${d.aviso || d.error || 'Sin partidos'}</div>` + rankHtml
      const btn2 = document.getElementById('prog-btn')
      if (btn2) { btn2.textContent = 'Actualizar'; btn2.disabled = false }
      // Llenar ranking lateral tambiÃ©n
      if (d.ranking_elo?.length) {
        const er = document.getElementById('elo-rank')
        if (er) er.innerHTML = d.ranking_elo.slice(0,8).map((e,i)=>`<div class="mm"><span class="mm-l">${i+1}. ${e.equipo}</span><span class="mm-v" style="color:var(--purple2)">${e.elo}</span></div>`).join('')
      }
      return
    }

    const fuente = d.usa_datos_reales
      ? '<span style="color:var(--green)">&#10003; Datos reales (' + (d.fuente_partidos || 'API') + ')</span>'
      : '<span style="color:var(--gold)">&#9888; Historial demo</span>'
    document.getElementById('prog-body').innerHTML = `
      <div style="font-size:10px;font-family:var(--mono);color:var(--muted);padding:10px 14px;border-bottom:1px solid var(--border)">
        ${d.modelo} Â· PrecisiÃ³n esperada: ${d.precision_esperada} Â· ${fuente}
      </div>
      ${(d.partidos||[]).map(p=>`
        <div class="prog-row" style="grid-template-columns:28px 1fr auto auto auto">
          <span class="prog-num">${p.numero}</span>
          <div>
            <div class="prog-match">${p.local_nombre||p.home||''}</div>
            <div class="prog-liga">${p.liga||'Liga MX'} Â· vs ${p.visitante_nombre||p.away||''}</div>
          </div>
          <div class="prog-probs">
            <span class="prob-box${p.pronostico==='1'?' best':''}">1&nbsp;${((p.prob_local||0)*100).toFixed(1)}%</span>
            <span class="prob-box${p.pronostico==='X'?' best':''}">X&nbsp;${((p.prob_empate||0)*100).toFixed(1)}%</span>
            <span class="prob-box${p.pronostico==='2'?' best':''}">2&nbsp;${((p.prob_visitante||0)*100).toFixed(1)}%</span>
          </div>
          <span><span class="badge ${p.confianza_pct>55?'bv':p.confianza_pct>42?'bs2':'bdim'}">[${p.pronostico}]</span></span>
          <span style="font-family:var(--mono);font-size:11px;color:var(--muted)">${p.confianza_pct}%</span>
        </div>`).join('')}`

    // Ranking ELO
    if(d.ranking_elo?.length) {
      document.getElementById('elo-rank').innerHTML = d.ranking_elo.slice(0,8).map((e,i)=>`
        <div class="mm"><span class="mm-l">${i+1}. ${e.equipo}</span><span class="mm-v" style="color:var(--purple2)">${e.elo}</span></div>`).join('')
      // El ranking Dixon-Coles deriva de la fuerza ofensiva/defensiva; mostramos el ELO como referencia unificada
      const dcEl = document.getElementById('dc-rank')
      if (dcEl) dcEl.innerHTML = '<p style="color:var(--muted);font-size:11px;font-family:var(--mono);line-height:1.5">El ranking Dixon-Coles se integra dentro del Ensemble junto con ELO. El ranking ELO de la izquierda refleja la fuerza combinada de cada equipo.</p>'
    }

  } catch(e) {
    document.getElementById('prog-body').innerHTML = `<div class="pb"><div class="rbox rb"><strong>Error</strong><br>${e.message}</div></div>`
  }

  btn.textContent = 'Actualizar'; btn.disabled = false
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// PARTIDO COMPLETO
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function predPartidoCompleto() {
  const home    = document.getElementById('p-home').value.trim()
  const away    = document.getElementById('p-away').value.trim()
  const arb     = document.getElementById('p-arb').value
  const ciudad  = document.getElementById('p-ciudad').value.trim()
  const posL    = document.getElementById('p-pos-l').value
  const posV    = document.getElementById('p-pos-v').value
  const jornada = document.getElementById('p-jornada').value
  
  // PARCHE DE EXTRACCIÃ“N: Forzar lectura de ambos campos de lesiones
  const lesL_el = document.getElementById('p-les-l')
  const lesV_el = document.getElementById('p-les-v')
  
  let valL = lesL_el.value.trim() !== '' ? lesL_el.value.trim() : lesL_el.placeholder
  let valV = lesV_el.value.trim() !== '' ? lesV_el.value.trim() : lesV_el.placeholder
  
  if (valL === '[]') valL = ''
  if (valV === '[]') valV = ''
  
  const el      = document.getElementById('pred-result')

  el.innerHTML = '<div class="loading"><div class="dot"></div><div class="dot"></div><div class="dot"></div>Calculando DC + ELO + Lesiones + H2H + Ãrbitro + Clima...</div>'
  try {
    let url = `/api/progol/partido-completo?home=${encodeURIComponent(home)}&away=${encodeURIComponent(away)}`
    if(arb)    url += `&arbitro=${encodeURIComponent(arb)}`
    if(ciudad) url += `&ciudad=${encodeURIComponent(ciudad)}`
    url += `&pos_local=${posL}&pos_visitante=${posV}&jornada=${jornada}`
    
    // InyecciÃ³n obligatoria de las variables independientes en la URL
    url += `&lesiones_local=${encodeURIComponent(valL || '[]')}`
    url += `&lesiones_visitante=${encodeURIComponent(valV || '[]')}`
    
    const d = await api(url)
    const f = d.features || {}
    const ff = f.factores_finales || {}

    el.innerHTML = `
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:14px">
        ${[['Local (1)',d.local,'var(--green)',d.cuota_justa_local],
           ['Empate (X)',d.empate,'var(--gold)',d.cuota_justa_empate],
           ['Visitante (2)',d.visitante,'var(--teal)',d.cuota_justa_visitante]].map(([l,v,c,q])=>`
          <div class="sc"><div class="sc-glow" style="background:${c}"></div>
            <div class="sc-lbl">${l}</div>
            <div class="sc-val" style="color:${c}">${((v||0)*100).toFixed(1)}%</div>
            <div class="sc-sub">Cuota justa: ${q||'â€”'}</div>
          </div>`).join('')}
      </div>
      <div class="rbox ri" style="font-size:12px;line-height:2">
        <strong>PronÃ³stico: [${d.pronostico}] ${d.confianza_pct}% â€” ${d.clasificacion}</strong><br>
        Modelo: ${d.modelo||'Ensemble DC+ELO+Poisson'}<br>
        ${f.lesiones?`Lesiones local: ${f.lesiones.lesiones_local} (${f.lesiones.impacto_local_pct}% impacto) Â· Visitante: ${f.lesiones.lesiones_visitante} (${f.lesiones.impacto_visitante_pct}%)<br>`:''}
        ${f.h2h?`H2H: ${f.h2h.dominio}<br>`:''}
        ${f.forma_local?`Forma local: ${f.forma_local.forma_str} Â· Visita: ${f.forma_visitante?.forma_str||'â€”'}<br>`:''}
        ${f.arbitro?.arbitro?`Ãrbitro: ${f.arbitro.arbitro} â€” ${f.arbitro.estilo}<br>`:''}
        ${f.importancia?`Partido: ${f.importancia.nivel}${f.importancia.es_clasico?' ðŸ”¥ CLÃSICO':''}<br>`:''}
        ${ff.lambda_local?`Î» ajustados: Local=${ff.lambda_local} Â· Visita=${ff.lambda_visitante} Â· EmpateÃ—${ff.empate_boost}`:''}
      </div>`
  } catch(e) {
    el.innerHTML = `<div class="rbox rb"><strong>Error</strong><br>${e.message}</div>`
  }
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// VALUE BETS
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function loadVB() {
  const dep = document.getElementById('sp-sel')?.value || 'soccer_mexico_ligamx'
  document.getElementById('vb-body').innerHTML = '<tr><td colspan="7"><div class="loading"><div class="dot"></div><div class="dot"></div><div class="dot"></div>Cargando...</div></td></tr>'
  try {
    const d = await api(`/api/odds/value-bets?edge_minimo=2&deporte=${dep}`)
    setAPIStatus(true)

    // Error de API â€” mostrar mensaje real
    if (d.error || d.es_demo) {
      const tb = d.traceback ? `<details style="margin-top:8px;font-size:10px;color:var(--red)"><summary>Ver traceback</summary><pre style="white-space:pre-wrap;font-size:9px;max-height:200px;overflow:auto;background:var(--bg2);padding:8px;border-radius:4px;margin:4px 0 0;text-align:left">${d.traceback}</pre></details>` : ''
      document.getElementById('vb-body').innerHTML = `<tr><td colspan="7" style="padding:16px;font-family:var(--mono);font-size:11px;color:var(--gold)">${d.aviso || d.error}${tb}</td></tr>`
      document.getElementById('vb-count').textContent = '0'
      document.getElementById('vb-edge').textContent  = 'sin datos'
      document.getElementById('vb-best').textContent  = 'â€”'
      return
    }

    const vbs = d.value_bets || []
    const edgeTxt = vbs.length ? `Edge prom +${(vbs.reduce((s,v)=>s+v.edge_porcentaje,0)/vbs.length).toFixed(1)}%` : 'sin edge'
    document.getElementById('vb-count').textContent = vbs.length
    document.getElementById('vb-edge').textContent  = edgeTxt
    const c2 = document.getElementById('vb-count2'); if (c2) c2.textContent = vbs.length
    const e2 = document.getElementById('vb-edge2'); if (e2) e2.textContent = edgeTxt
    document.getElementById('vb-best').textContent  = vbs.length ? `+${Math.max(...vbs.map(v=>v.edge_porcentaje))}%` : 'â€”'

    if (!vbs.length) {
      const msg = d.aviso || `Sin value bets con edge >= 2% en ${dep.replace('soccer_mexico_','').replace('ligamx','Liga MX')}`
      document.getElementById('vb-body').innerHTML = `<tr><td colspan="7" style="padding:16px;font-family:var(--mono);font-size:11px;color:var(--muted)">${msg}</td></tr>`
      return
    }

    document.getElementById('vb-body').innerHTML = vbs.map(vb => `
      <tr>
        <td>
          <div style="font-weight:700;font-size:12px">${vb.partido}</div>
          <div style="font-size:9px;font-family:var(--mono);color:var(--muted)">${vb.liga}${vb.fecha ? ' Â· ' + new Date(vb.fecha).toLocaleDateString('es-MX') : ''}</div>
        </td>
        <td style="font-family:var(--mono);font-size:11px">${vb.resultado}</td>
        <td style="font-family:var(--mono);font-size:10px;color:var(--muted)">${vb.casa}</td>
        <td style="font-family:var(--mono);font-weight:700;font-size:14px">${vb.cuota}</td>
        <td><span class="badge ${vb.edge_porcentaje>7?'bs2':'bv'}">+${vb.edge_porcentaje}%</span></td>
        <td><span class="badge ${vb.edge_porcentaje>7?'hot':'bv'}">${vb.edge_porcentaje>7?'STRONG VALUE':'VALUE BET'}</span></td>
        <td><button class="btn btn-kelly" onclick="openKelly('${vb.partido.replace(/'/g,"\\'")}','${vb.resultado}','${vb.cuota}','${vb.edge_porcentaje}','${vb.casa}')">ðŸ’Ž</button></td>
      </tr>`).join('')

  } catch(e) {
    document.getElementById('vb-body').innerHTML = `<tr><td colspan="7" style="padding:12px;font-size:11px;font-family:var(--mono);color:var(--red)">Error: ${e}</td></tr>`
  }
}

function calcEV() {
  const o=parseFloat(document.getElementById('ev-o')?.value)||2.10
  const p=parseFloat(document.getElementById('ev-p')?.value)/100||0.52
  const s=parseFloat(document.getElementById('ev-s')?.value)||100
  const ev=((o-1)*p-(1-p))*s, edge=((p*o-1)*100).toFixed(1)
  const el=document.getElementById('ev-r'); if(!el) return
  el.innerHTML=`<div class="rbox ${ev>0?'rg':'rb'}"><strong>${ev>0?'VALUE BET â€” apostar':'Sin valor â€” no apostar'}</strong><br>EV: <strong>$${ev.toFixed(2)}</strong> Â· Edge: <strong>${edge}%</strong></div>`
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// SHARP MONEY
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function analizarSharp() {
  const partido=document.getElementById('sh-partido').value.trim()
  const lap=document.getElementById('sh-lap').value
  const lact=document.getElementById('sh-lact').value
  const bol=document.getElementById('sh-bol').value
  const din=document.getElementById('sh-din').value
  const dias=document.getElementById('sh-dias').value
  const casasStr=document.getElementById('sh-casas').value.trim()
  const el=document.getElementById('sharp-result')
  el.innerHTML='<div class="loading"><div class="dot"></div><div class="dot"></div><div class="dot"></div>Analizando indicadores sharp...</div>'
  try {
    let url=`/api/sharp/analizar?partido=${encodeURIComponent(partido)}&linea_apertura=${lap}&linea_actual=${lact}&pct_boletos_local=${bol}&pct_dinero_local=${din}&dias_antes=${dias}`
    if(casasStr) url+=`&lineas_casas=${encodeURIComponent(casasStr)}`
    const d=await api(url)
    const sc=d.score_sharp
    const col=sc.score>=85?'var(--green)':sc.score>=70?'var(--gold)':sc.score>=55?'var(--teal)':'var(--red)'
    el.innerHTML=`
      <div style="display:grid;grid-template-columns:110px 1fr;gap:16px;margin-bottom:14px;align-items:center">
        <div style="text-align:center">
          <div style="font-size:52px;font-weight:800;color:${col};letter-spacing:-2px;line-height:1">${sc.score}</div>
          <div style="font-size:9px;font-family:var(--mono);color:var(--muted)">/ 100 SHARP SCORE</div>
        </div>
        <div>
          <div style="font-size:14px;font-weight:700;color:${col};margin-bottom:4px">${sc.clasificacion}</div>
          <div style="font-size:12px;color:var(--muted);margin-bottom:6px">${sc.recomendacion}</div>
          <div style="font-size:10px;font-family:var(--mono);color:var(--muted)">${sc.n_seÃ±ales_detectadas}/${sc.n_seÃ±ales_totales} seÃ±ales activas</div>
        </div>
      </div>
      ${sc.seÃ±ales_activas.map(s=>`
        <div style="padding:9px 12px;background:rgba(255,255,255,.02);border-radius:7px;border-left:2px solid ${s.confianza>=80?'var(--green)':s.confianza>=65?'var(--gold)':'var(--muted)'};margin-bottom:6px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:3px">
            <span style="font-size:11px;font-weight:600">${s.tipo}</span>
            <span class="badge ${s.confianza>=80?'bv':s.confianza>=65?'bs2':'bdim'}">${s.confianza}%</span>
          </div>
          <div style="font-size:11px;font-family:var(--mono);color:var(--muted)">${s.seÃ±al}</div>
        </div>`).join('')}`
  } catch(e) {
    el.innerHTML=`<div class="rbox rb"><strong>Error</strong><br>${e.message}</div>`
  }
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// CLV
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
function calcCLV() {
  const mi=parseFloat(document.getElementById('clv-i')?.value)||2.10
  const cl=parseFloat(document.getElementById('clv-c')?.value)||1.85
  const pos=mi>cl, pct=((mi/cl-1)*100).toFixed(1)
  const el=document.getElementById('clv-r'); if(!el) return
  el.innerHTML=`<div class="rbox ${pos?'rg':'rb'}"><strong>CLV ${pos?'Positivo âœ“':'Negativo âœ—'}</strong><br>CLV: <strong>${pos?'+':''}${pct}%</strong> Â· Prob. apostada: ${(1/mi*100).toFixed(2)}% â†’ Cierre: ${(1/cl*100).toFixed(2)}%<br>${pos?'El mercado confirmÃ³ tu anÃ¡lisis.':'El mercado se moviÃ³ en tu contra.'}</div>`
}

const CLV_HIST=[
  {m:'Chivas ML',mi:2.10,cl:1.88,w:true},{m:'Cruz Azul -1',mi:1.95,cl:2.05,w:true},
  {m:'Tigres Over 2.5',mi:1.72,cl:1.65,w:false},{m:'AmÃ©rica Empate',mi:3.40,cl:3.10,w:false},
  {m:'Santos ML',mi:2.80,cl:3.15,w:true},
]
function renderCLVT() {
  const el=document.getElementById('clv-t'); if(!el) return
  el.innerHTML=CLV_HIST.map(b=>{
    const pos=b.mi>b.cl,pct=+((b.mi/b.cl-1)*100).toFixed(1)
    return`<tr><td style="font-weight:600">${b.m}</td><td style="font-family:var(--mono)">${b.mi}</td><td style="font-family:var(--mono)">${b.cl}</td>
      <td><span class="badge ${pos?'bv':'bdim'}">${pos?'+':''}${pct}%</span></td>
      <td><span class="badge ${b.w?'bwin':'blose'}">${b.w?'GanÃ³':'PerdiÃ³'}</span></td></tr>`
  }).join('')
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// KELLY
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
function calcKelly() {
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
    l.textContent='Kelly negativo â€” sin valor matemÃ¡tico'
    r.innerHTML='<div style="padding:9px;background:rgba(248,113,113,.07);border-radius:7px;font-size:11px;font-family:var(--mono);color:var(--red)">La cuota no tiene valor con esta probabilidad.</div>'
    return
  }
  a.style.color='var(--green)';a.textContent=`$${ap.toFixed(0)}`
  l.textContent='apuesta Ã³ptima sugerida'
  r.innerHTML=[
    ['Kelly puro',`${(kp*100).toFixed(2)}%`],
    ['Kelly ajustado',`${(ka*100).toFixed(2)}%`],
    ['% del bankroll',`${(ka*100).toFixed(1)}%`],
    ['ROI esperado',`+${((b*prob-q)*100).toFixed(1)}%`],
    ['MÃ¡x. 5% recomendado',`$${(bank*0.05).toFixed(0)}`],
  ].map(([l,v])=>`<div class="k-row"><span>${l}</span><span>${v}</span></div>`).join('')
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// MONTE CARLO
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
function runMC() {
  const lL=parseFloat(document.getElementById('mc-l').value)||1.5
  const lV=parseFloat(document.getElementById('mc-v').value)||1.1
  const N=parseInt(document.getElementById('mc-n').value)||10000
  const btn=document.getElementById('mc-btn')
  btn.textContent=`Simulando ${N.toLocaleString()}â€¦`; btn.disabled=true
  setTimeout(()=>{
    function poisson(l){let k=0,p=Math.exp(-l),q=1;while(q>p){k++;q*=Math.random()};return k-1}
    let h=0,d=0,a=0,gs=[]
    for(let i=0;i<N;i++){const gl=poisson(lL),gv=poisson(lV);gs.push(gl+gv);if(gl>gv)h++;else if(gl===gv)d++;else a++}
    const pL=h/N*100,pD=d/N*100,pV=a/N*100
    const avg=(gs.reduce((s,v)=>s+v,0)/N).toFixed(2)
    const o25=(gs.filter(g=>g>2.5).length/N*100).toFixed(1)
    const o15=(gs.filter(g=>g>1.5).length/N*100).toFixed(1)
    document.getElementById('mc-sg').innerHTML=[
      ['Local',pL.toFixed(1)+'%',(100/pL).toFixed(2),'var(--purple)'],
      ['Empate',pD.toFixed(1)+'%',(100/pD).toFixed(2),'var(--gold)'],
      ['Visitante',pV.toFixed(1)+'%',(100/pV).toFixed(2),'var(--teal)'],
      ['Over 2.5',o25+'%',`Î» avg:${avg}g`,'var(--green)'],
    ].map(([l,v,s,c])=>`<div class="sc"><div class="sc-glow" style="background:${c}"></div><div class="sc-lbl">${l}</div><div class="sc-val" style="color:${c}">${v}</div><div class="sc-sub">${s}</div></div>`).join('')
    const mx=Math.max(pL,pD,pV)
    document.getElementById('mc-bars-out').innerHTML=`
      <div style="margin-bottom:10px;font-size:10px;font-family:var(--mono);color:var(--muted)">${N.toLocaleString()} simulaciones Â· Î»L=${lL} Î»V=${lV} Â· Over 1.5: ${o15}%</div>
      ${[['Local',pL,'var(--purple)'],['Empate',pD,'var(--gold)'],['Visitante',pV,'var(--teal)']].map(([l,p,c])=>`
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:7px">
          <span style="font-size:10px;font-family:var(--mono);color:var(--muted);width:60px">${l}</span>
          <div style="flex:1;height:7px;background:rgba(255,255,255,.04);border-radius:4px;overflow:hidden"><div style="width:${Math.round(p/mx*100)}%;height:100%;border-radius:4px;background:${c};transition:width .8s"></div></div>
          <span style="font-size:10px;font-family:var(--mono);color:var(--muted);width:40px;text-align:right">${p.toFixed(1)}%</span>
        </div>`).join('')}
      <div style="margin-top:10px;padding:9px 11px;background:rgba(255,255,255,.02);border-radius:7px;font-size:10px;font-family:var(--mono);color:var(--muted)">Cuotas justas sin vig: Local ${(100/pL).toFixed(2)} Â· Empate ${(100/pD).toFixed(2)} Â· Visitante ${(100/pV).toFixed(2)}</div>`
    document.getElementById('mc-out').style.display='block'
    btn.textContent=`Re-ejecutar ${N.toLocaleString()}`; btn.disabled=false
  },50)
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// NLP
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function scanNLP() {
  const home=document.getElementById('nlp-home').value.trim()
  const away=document.getElementById('nlp-away').value.trim()
  const el=document.getElementById('nlp-result')
  el.innerHTML='<div class="loading"><div class="dot"></div><div class="dot"></div><div class="dot"></div>Escaneando noticias RSS...</div>'
  try {
    const d=await api(`/api/nlp/scan?home=${encodeURIComponent(home)}&away=${encodeURIComponent(away)}`)
    const sL=d.sentimiento_local||{},sA=d.sentimiento_visitante||{}
    const edges=d.alertas_edge||[]
    el.innerHTML=`
      <div class="sg" style="margin-bottom:14px">
        <div class="sc"><div class="sc-glow" style="background:${d.impacto_local_pct>15?'var(--red)':'var(--green)'}"></div>
          <div class="sc-lbl">Lesiones ${home.split(' ')[0]}</div>
          <div class="sc-val" style="color:${d.impacto_local_pct>15?'var(--red)':'var(--green)'}">${d.impacto_local_pct}%</div>
          <div class="sc-sub">${d.alertas_lesiones_local?.length||0} alertas detectadas</div></div>
        <div class="sc"><div class="sc-glow" style="background:${d.impacto_visitante_pct>15?'var(--red)':'var(--green)'}"></div>
          <div class="sc-lbl">Lesiones ${away.split(' ')[0]}</div>
          <div class="sc-val" style="color:${d.impacto_visitante_pct>15?'var(--red)':'var(--green)'}">${d.impacto_visitante_pct}%</div>
          <div class="sc-sub">${d.alertas_lesiones_visitante?.length||0} alertas detectadas</div></div>
        <div class="sc"><div class="sc-glow" style="background:${sL.sentimiento==='positivo'?'var(--green)':sL.sentimiento==='negativo'?'var(--red)':'var(--muted)'}"></div>
          <div class="sc-lbl">Moral ${home.split(' ')[0]}</div>
          <div class="sc-val" style="font-size:14px;color:${sL.sentimiento==='positivo'?'var(--green)':sL.sentimiento==='negativo'?'var(--red)':'var(--muted)'}">${sL.sentimiento||'neutral'}</div>
          <div class="sc-sub">Score: ${sL.score||0}</div></div>
        <div class="sc"><div class="sc-glow" style="background:${sA.sentimiento==='positivo'?'var(--green)':sA.sentimiento==='negativo'?'var(--red)':'var(--muted)'}"></div>
          <div class="sc-lbl">Moral ${away.split(' ')[0]}</div>
          <div class="sc-val" style="font-size:14px;color:${sA.sentimiento==='positivo'?'var(--green)':sA.sentimiento==='negativo'?'var(--red)':'var(--muted)'}">${sA.sentimiento||'neutral'}</div>
          <div class="sc-sub">Score: ${sA.score||0}</div></div>
      </div>
      ${edges.length?`
        <div style="margin-bottom:10px">
          <div style="font-size:11px;font-weight:700;color:var(--gold);margin-bottom:8px">âš¡ ALERTAS DE EDGE DETECTADAS</div>
          ${edges.map(e=>`
            <div style="padding:10px 13px;border-radius:8px;margin-bottom:7px;border-left:3px solid ${e.urgencia==='ALTA'?'var(--red)':'var(--gold)'};background:${e.urgencia==='ALTA'?'rgba(248,113,113,.07)':'rgba(240,180,41,.06)'}">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
                <span style="font-size:11px;font-weight:700;color:${e.urgencia==='ALTA'?'var(--red)':'var(--gold)'}">${e.tipo}</span>
                <span class="badge ${e.urgencia==='ALTA'?'hot':'bs2'}">${e.urgencia}${e.ventana_min?' Â· '+e.ventana_min+'min':''}</span>
              </div>
              <div style="font-size:12px;color:var(--text);margin-bottom:3px">${e.detalle}</div>
              <div style="font-size:11px;font-family:var(--mono);color:var(--teal)">â†’ ${e.accion}</div>
              ${e.noticias?.length?`<div style="font-size:10px;color:var(--muted);margin-top:3px">${e.noticias[0]}</div>`:''}
            </div>`).join('')}
        </div>`:
        '<div style="font-size:12px;color:var(--muted);margin-bottom:10px">Sin alertas de edge â€” no se detectaron lesiones crÃ­ticas.</div>'}
      <div style="font-size:10px;font-family:var(--mono);color:var(--muted)">${d.n_noticias} noticias analizadas Â· ${d.timestamp?.split('T')[0]||''}</div>`
  } catch(e) {
    el.innerHTML=`<div class="rbox rb"><strong>Error</strong><br>${e.message}</div>`
  }
}

async function loadNoticias() {
  const el=document.getElementById('noticias-list')
  el.innerHTML='<div class="loading"><div class="dot"></div><div class="dot"></div><div class="dot"></div>Cargando RSS...</div>'
  try {
    const d=await api('/api/nlp/noticias')
    el.innerHTML=d.noticias.map(n=>`
      <div style="padding:9px 0;border-bottom:1px solid var(--border)">
        <div style="font-size:12px;font-weight:600;margin-bottom:3px">${n.titulo}</div>
        <div style="display:flex;justify-content:space-between;align-items:center">
          <span style="font-size:10px;font-family:var(--mono);color:var(--muted)">${n.fuente}</span>
          <div style="display:flex;gap:4px">${(n.alertas||[]).map(a=>`<span class="badge ${a.tipo==='BAJA CONFIRMADA'?'hot':a.tipo==='DUDA'?'bs2':'bv'}">${a.tipo}</span>`).join('')}</div>
        </div>
      </div>`).join('')
  } catch(e) {
    el.innerHTML=`<div class="rbox rb">Error: ${e.message}</div>`
  }
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// BACKTEST
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function runBacktest() {
  const modo=document.getElementById('bt-modo').value
  const el=document.getElementById('bt-result')
  el.innerHTML='<div class="loading"><div class="dot"></div><div class="dot"></div><div class="dot"></div>Ejecutando backtest walk-forward...</div>'
  try {
    const d=await api(`/api/backtest?modo=${modo}&ventana=20`)
    if(modo==='comparar'){
      el.innerHTML=`<table class="tbl">
        <thead><tr><th>Modelo</th><th>Accuracy</th><th>Acertados</th><th>Total</th><th>vs Aleatorio</th></tr></thead>
        <tbody>${Object.entries(d).map(([m,v])=>`
          <tr>
            <td style="font-weight:600">${m}</td>
            <td><span class="badge ${v.accuracy_pct>45?'bv':v.accuracy_pct>38?'bs2':'bdim'}">${v.accuracy_pct}%</span></td>
            <td style="font-family:var(--mono)">${v.acertados}</td>
            <td style="font-family:var(--mono)">${v.total}</td>
            <td style="font-family:var(--mono);color:${v.accuracy_pct>33.3?'var(--green)':'var(--red)'}">${v.accuracy_pct>33.3?'+':''}${(v.accuracy_pct-33.3).toFixed(1)}%</td>
          </tr>`).join('')}
        </tbody></table>`
    } else {
      const r=d.resumen||{},c=d.accuracy_por_confianza||{}
      el.innerHTML=`
        <div class="sg" style="margin-bottom:14px">
          <div class="sc"><div class="sc-glow" style="background:var(--green)"></div><div class="sc-lbl">Accuracy total</div><div class="sc-val" style="color:var(--green)">${r.accuracy_pct}%</div><div class="sc-sub">Benchmark: 33.3%</div></div>
          <div class="sc"><div class="sc-glow" style="background:var(--gold)"></div><div class="sc-lbl">Mejora vs azar</div><div class="sc-val" style="color:var(--gold)">+${r.mejora_vs_aleatorio}%</div><div class="sc-sub">${r.acertadas}/${r.total_predicciones}</div></div>
          <div class="sc"><div class="sc-glow" style="background:var(--purple)"></div><div class="sc-lbl">Brier Score</div><div class="sc-val" style="color:var(--purple2)">${r.brier_score}</div><div class="sc-sub">Azar: 0.222</div></div>
          <div class="sc"><div class="sc-glow" style="background:var(--teal)"></div><div class="sc-lbl">ROI Kelly</div><div class="sc-val" style="color:${r.roi_kelly_pct>=0?'var(--teal)':'var(--red)'}">${r.roi_kelly_pct>0?'+':''}${r.roi_kelly_pct}%</div><div class="sc-sub">$${r.bankroll_inicial}â†’$${r.bankroll_final}</div></div>
        </div>
        <div class="panel" style="margin-bottom:10px">
          <div class="ph2"><span class="pt">Accuracy por confianza</span></div>
          <div class="pb">${[['Alta >55%',c.alta_55plus],['Media 42-55%',c.media_42_55],['Baja <42%',c.baja_menos42]].map(([l,v])=>v?`
            <div class="mm"><span class="mm-l">${l} Â· ${v.n} partidos</span><span class="mm-v" style="color:${v.accuracy_pct>40?'var(--green)':'var(--muted)'}">${v.accuracy_pct}%</span></div>`:''
          ).join('')}</div>
        </div>
        <div style="font-size:11px;padding:10px;background:rgba(255,255,255,.02);border-radius:7px;font-family:var(--mono);color:var(--muted)">${d.interpretacion}</div>`
    }
  } catch(e) {
    el.innerHTML=`<div class="rbox rb"><strong>Error</strong><br>${e.message}</div>`
  }
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// ALERTAS
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
const ALERTS_DATA=[
  {t:'r',x:'Value bet: Chivas ML Â· Edge +8.4% vs Bet365 Â· Kelly sugiere $180',g:'hace 3 min'},
  {t:'s',x:'Sharp money: AmÃ©rica Over 2.5 â€” Reverse Line Movement activo (72% pÃºblico, lÃ­nea baja)',g:'hace 8 min'},
  {t:'g',x:'Arbitraje confirmado: Tigres vs Monterrey +3.4% garantizado en 2 casas',g:'hace 15 min'},
  {t:'w',x:'Value bet: Toluca ML Â· Edge +10.0% â€” STRONG VALUE, apostar antes de que corrija',g:'hace 22 min'},
  {t:'g',x:'NLP: Henry MartÃ­n descartado para el ClÃ¡sico â€” lesiÃ³n muscular confirmada',g:'hace 35 min'},
  {t:'s',x:'Steam move: Cruz Azul -0.5 â†’ -1.0 en 4 casas en 8 minutos â€” sindicato sharp',g:'hace 1.5h'},
]

async function loadAlertas(target='alertas-feed') {
  const el = document.getElementById(target)
  if (!el) return
  try {
    const d = await api('/api/alertas/recientes')
    const alertas = d.alertas || []
    const status = d.api_status || {}
    const modoColor = status.modo === 'REAL' ? 'var(--green)' : 'var(--gold)'
    let html = `<div style="padding:6px 10px;margin-bottom:8px;background:var(--bg4);border-radius:6px;font-family:var(--mono);font-size:10px;display:flex;gap:10px;flex-wrap:wrap">
      <span style="color:${modoColor};font-weight:700">${status.modo || 'DEMO'}</span>
      <span style="color:${status.api_football ? 'var(--green)' : 'var(--red)'}">Football API ${status.api_football ? '&#10003;' : '&#10007;'}</span>
      <span style="color:${status.odds_api ? 'var(--green)' : 'var(--red)'}">Odds API ${status.odds_api ? '&#10003;' : '&#10007;'}</span>
      <span style="color:${status.db ? 'var(--green)' : 'var(--red)'}">DB ${status.db ? '&#10003;' : '&#10007;'}</span>
    </div>`
    if (alertas.length) {
      html += '<div class="afeed">' + alertas.map(a => {
        const pre = a.real ? '' : '[DEMO] '
        const op = a.real ? '' : 'opacity:0.55;'
        return `<div class="ai ${a.t}" style="${op}"><span class="ai-t">${pre}${a.x}</span><span class="ai-g">${a.g}</span></div>`
      }).join('') + '</div>'
    } else {
      html += '<div style="color:var(--muted);padding:16px;text-align:center;font-family:var(--mono);font-size:11px">Sin alertas aun. El sistema las genera automaticamente.</div>'
    }
    el.innerHTML = html
  } catch(e) {
    el.innerHTML = '<div class="afeed">' + ALERTS_DATA.map(a =>
      `<div class="ai ${a.t}"><span class="ai-t">[DEMO] ${a.x}</span><span class="ai-g">${a.g}</span></div>`
    ).join('') + '</div>'
  }
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// INIT
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// CUENTAS & CAMUFLAJE
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function loadCuentas() {
  try {
    const resp = await api('/api/cuentas/listar')
    const cuentas = Array.isArray(resp) ? resp : (resp.cuentas || [])
    const activas = cuentas.filter(c => c.activa)
    document.getElementById('ct-activas').textContent = activas.length
    const avgHealth = activas.length ? Math.round(activas.reduce((s,c)=>s+(c.health_score||100),0)/activas.length) : 100
    document.getElementById('ct-health').textContent = avgHealth + '/100'
    const enRiesgo = activas.filter(c => (c.health_score||100) < 40).length
    document.getElementById('ct-riesgo').textContent = enRiesgo

    // Llenar selector de casas para reportar limitaciÃ³n
    const sel = document.getElementById('ct-casa-lim')
    sel.innerHTML = '<option value="">Selecciona la casa...</option>' +
      activas.map(c => `<option value="${c.casa_key}">${c.nombre}</option>`).join('')

    if (!activas.length) {
      document.getElementById('ct-lista').innerHTML = '<span style="color:var(--muted)">Sin cuentas registradas. Agrega tu primera casa arriba.</span>'
      return
    }

    document.getElementById('ct-lista').innerHTML = `
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px">
        ${activas.map(c => {
          const color = c.estado==='verde'?'var(--green)':c.estado==='amarillo'?'var(--gold)':'var(--red)'
          const icon  = c.estado==='verde'?'ðŸŸ¢':c.estado==='amarillo'?'ðŸŸ¡':'ðŸ”´'
          return `<div style="background:var(--bg4);border:1px solid ${color}33;border-radius:8px;padding:12px">
            <div style="display:flex;justify-content:space-between;margin-bottom:8px">
              <span style="color:var(--text);font-weight:700">${icon} ${c.nombre}</span>
              <span style="color:${color};font-size:10px">${c.health_score||100}/100</span>
            </div>
            <div style="color:var(--muted);font-size:10px">Tipo: ${c.tipo} Â· ${c.tolerancia||''}</div>
            <div style="color:var(--muted);font-size:10px">LÃ­mite: $${c.limite_actual||0} (${c.pct_limite_restante||100}%)</div>
            <div style="margin-top:6px;background:var(--bg3);border-radius:3px;height:4px">
              <div style="background:${color};width:${c.health_score||100}%;height:4px;border-radius:3px"></div>
            </div>
          </div>`
        }).join('')}
      </div>`
  } catch(e) {
    document.getElementById('ct-lista').innerHTML = '<span style="color:var(--red)">Error: '+e+'</span>'
  }
}

async function registrarCuenta() {
  const casa_key = document.getElementById('ct-casa').value
  const limite   = parseFloat(document.getElementById('ct-limite').value)
  const balance  = parseFloat(document.getElementById('ct-balance').value||0)
  const notas    = document.getElementById('ct-notas').value
  if (!limite) { document.getElementById('ct-msg').textContent='Ingresa el lÃ­mite mÃ¡ximo'; return }
  try {
    const r = await fetch('/api/cuentas/registrar',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({casa_key,limite_inicial:limite,balance,notas})})
    const d = await r.json()
    const msg = document.getElementById('ct-msg')
    msg.textContent = d.error ? 'âŒ '+d.error : 'âœ… '+d.casa+' registrada con lÃ­mite $'+d.limite
    msg.style.color = d.error?'var(--red)':'var(--green)'
    if (!d.error) loadCuentas()
  } catch(e) { document.getElementById('ct-msg').textContent='âŒ '+e }
}

async function reportarLimitacion() {
  const casa_key    = document.getElementById('ct-casa-lim').value
  const nuevo_limite = parseFloat(document.getElementById('ct-nuevo-lim').value)
  const razon       = document.getElementById('ct-razon').value
  if (!casa_key || !nuevo_limite) { document.getElementById('ct-lim-msg').textContent='Completa los campos'; return }
  try {
    const r = await fetch('/api/cuentas/limite',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({casa_key,nuevo_limite,razon})})
    const d = await r.json()
    const msg = document.getElementById('ct-lim-msg')
    if (d.error) { msg.style.color='var(--red)'; msg.textContent='âŒ '+d.error; return }
    const color = d.nivel==='CRÃTICA'?'var(--red)':d.nivel==='MODERADA'?'var(--gold)':'var(--muted)'
    msg.style.color = color
    msg.textContent = `${d.nivel}: -${d.reduccion_pct}% en ${d.casa}. Health: ${d.health_score}/100`
    document.getElementById('ct-analisis').innerHTML =
      `<div style="color:${color};margin-bottom:6px">âš ï¸ ${d.recomendacion}</div>`
    loadCuentas()
  } catch(e) { document.getElementById('ct-lim-msg').textContent='âŒ '+e }
}

async function loadCamuflaje() {
  const perfil  = document.getElementById('ct-perfil-sel').value
  const bankroll = document.getElementById('ct-bank').value
  document.getElementById('ct-perfil').textContent = perfil.charAt(0).toUpperCase()+perfil.slice(1)
  try {
    const d = await api(`/api/cuentas/camuflaje/plan?perfil=${perfil}&bankroll=${bankroll}`)
    const r = d.resumen || {}
    const camuflajes = d.apuestas_camuflaje || []
    document.getElementById('ct-camuflaje').innerHTML = `
      <div style="background:rgba(124,109,250,.08);border:1px solid rgba(124,109,250,.2);border-radius:8px;padding:12px;margin-bottom:12px">
        <div style="color:var(--purple2);font-weight:700;margin-bottom:6px">Plan Semana ${d.semana||''}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;font-size:11px">
          <div>Sharp: <span style="color:var(--green)">${r.apuestas_sharp||0}</span></div>
          <div>Camuflaje: <span style="color:var(--gold)">${r.apuestas_camuflaje||0}</span></div>
          <div>Ratio: <span style="color:var(--text)">${r.ratio_real||''}</span></div>
        </div>
        <div style="color:var(--muted);font-size:10px;margin-top:6px">${d.advertencia||''}</div>
        <div style="color:var(--muted);font-size:10px">Vida estimada de cuentas: ~${d.semanas_vida_estimada||0} semanas</div>
      </div>
      <div style="color:var(--text);margin-bottom:6px;font-weight:700">ðŸŽ­ Apuestas de Camuflaje Sugeridas:</div>
      ${camuflajes.map(c=>`
        <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border)">
          <div>
            <span style="color:var(--gold)">â—‡</span>
            <span style="color:var(--text)">${c.mercado}</span>
            <span style="color:var(--muted)"> Â· ${c.liga}</span>
          </div>
          <div>
            <span style="color:var(--muted)">@${c.cuota}</span>
            <span style="color:var(--text)"> $${c.monto}</span>
            <span style="color:var(--muted)"> en ${c.casa}</span>
          </div>
        </div>`).join('')}`
  } catch(e) { document.getElementById('ct-camuflaje').innerHTML='<span style="color:var(--red)">'+e+'</span>' }
}

async function loadAnalisisCuenta() {
  try {
    const d = await api('/api/cuentas/camuflaje/analizar')
    const color = d.riesgo==='ALTO'?'var(--red)':d.riesgo==='MEDIO'?'var(--gold)':'var(--green)'
    const alertas = d.alertas || []
    const recs    = d.recomendaciones || []
    document.getElementById('ct-analisis').innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
        <div style="font-size:24px;font-weight:800;color:${color}">${d.score_riesgo||0}/100</div>
        <div>
          <div style="color:${color};font-weight:700">Riesgo ${d.riesgo||'BAJO'}</div>
          <div style="color:var(--muted);font-size:10px">Score de exposiciÃ³n a limitaciones</div>
        </div>
      </div>
      ${alertas.length ? alertas.map(a=>`
        <div style="background:rgba(248,113,113,.05);border-left:3px solid var(--red);padding:6px 10px;margin-bottom:5px;border-radius:0 5px 5px 0">
          <div style="color:var(--red);font-size:10px">${a.urgencia}</div>
          <div style="color:var(--text);font-size:11px">${a.detalle}</div>
        </div>`).join('') : '<div style="color:var(--green)">âœ“ Sin alertas de comportamiento</div>'}
      ${recs.length ? '<div style="margin-top:8px;color:var(--muted)">'+recs.map(r=>'â†’ '+r).join('<br>')+'</div>' : ''}`
  } catch(e) { document.getElementById('ct-analisis').innerHTML='<span style="color:var(--red)">'+e+'</span>' }
}

async function loadRotacion() {
  const monto = document.getElementById('ct-monto-rot').value
  try {
    const d = await api(`/api/cuentas/rotacion?monto=${monto}`)
    if (d.error) { document.getElementById('ct-rotacion').innerHTML='<span style="color:var(--muted)">'+d.error+'</span>'; return }
    document.getElementById('ct-rotacion').innerHTML = `
      <div style="color:var(--muted);font-size:10px;margin-bottom:8px">Total a apostar: <span style="color:var(--text)">$${d.total_a_apostar}</span> de $${d.monto_total}</div>
      ${(d.distribucion||[]).map(c=>{
        const color = c.estado==='verde'?'var(--green)':c.estado==='amarillo'?'var(--gold)':'var(--red)'
        return `<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--border)">
          <div>
            <span style="color:var(--text);font-weight:700">${c.casa}</span>
            <span style="color:var(--muted)"> Â· Health ${c.health_score}/100</span>
          </div>
          <div>
            <span style="color:${color};font-weight:700">$${c.monto}</span>
            <span style="color:var(--muted)"> (${c.pct_del_total}%)</span>
          </div>
        </div>`}).join('')}`
  } catch(e) { document.getElementById('ct-rotacion').innerHTML='<span style="color:var(--red)">'+e+'</span>' }
}


// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// VALUE PRO
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
async function calcValuePro() {
  const prob = document.getElementById('vp-prob').value
  const cuota = document.getElementById('vp-cuota').value
  const pinn = document.getElementById('vp-pinnacle').value
  const bank = document.getElementById('vp-bank').value
  const frac = document.getElementById('vp-frac').value
  let url = `/api/value/analizar?prob=${prob}&cuota=${cuota}&bankroll=${bank}&fraccion=${frac}`
  if (pinn) url += `&pinnacle=${pinn}`
  try {
    const d = await api(url)
    const edgeColor = d.edge_modelo_pct > 4 ? 'var(--green)' : d.edge_modelo_pct > 0 ? 'var(--gold)' : 'var(--red)'
    let html = `
      <div style="text-align:center;padding:12px 0;border-bottom:1px solid var(--border);margin-bottom:12px">
        <div style="font-size:32px;font-weight:800;color:${edgeColor}">${d.edge_modelo_pct > 0 ? '+' : ''}${d.edge_modelo_pct}%</div>
        <div style="font-size:11px;color:var(--muted)">EDGE Â· ${d.clasificacion}</div>
      </div>
      <div style="line-height:2">
        <div>Prob. modelo: <span style="color:var(--text)">${d.prob_modelo_pct}%</span></div>
        <div>Prob. implÃ­cita casa: <span style="color:var(--text)">${d.prob_implicita_pct}%</span></div>
        <div>Valor esperado/unidad: <span style="color:${d.ev_por_unidad>0?'var(--green)':'var(--red)'}">${d.ev_por_unidad}</span></div>`
    if (d.edge_mercado_pct !== undefined) {
      html += `<div style="margin-top:6px;padding-top:6px;border-top:1px solid var(--border)">
        Edge vs Pinnacle: <span style="color:${d.edge_mercado_pct>0?'var(--green)':'var(--red)'}">${d.edge_mercado_pct}%</span></div>
        <div>Confianza: <span style="color:var(--purple2)">${d.confianza}</span></div>`
    }
    if (d.kelly) {
      html += `<div style="margin-top:10px;padding:10px;background:rgba(240,180,41,.08);border-radius:7px">
        <div style="color:var(--gold);font-weight:700;margin-bottom:4px">ðŸ’° STAKE KELLY</div>
        <div>Apostar: <span style="color:var(--gold);font-size:16px;font-weight:700">$${d.kelly.stake_sugerido || 0}</span></div>
        <div style="font-size:10px;color:var(--muted)">${d.kelly.kelly_aplicado_pct}% del bankroll (${d.kelly.fraccion_usada} Kelly)</div>
      </div>`
    }
    html += `<div style="margin-top:10px;padding:8px;background:var(--bg4);border-radius:6px;color:${edgeColor}">${d.recomendacion}</div></div>`
    document.getElementById('vp-resultado').innerHTML = html
  } catch(e) { document.getElementById('vp-resultado').innerHTML = '<span style="color:var(--red)">Error: '+e+'</span>' }
}

async function calcCLVpro() {
  const ap = document.getElementById('clv-apostada').value
  const ci = document.getElementById('clv-cierre').value
  try {
    const d = await api(`/api/value/clv?apostada=${ap}&cierre=${ci}`)
    const color = d.positivo ? 'var(--green)' : 'var(--red)'
    document.getElementById('clv-pro-res').innerHTML = `
      <div style="display:flex;align-items:center;gap:14px">
        <div style="font-size:28px;font-weight:800;color:${color}">${d.clv_pct>0?'+':''}${d.clv_pct}%</div>
        <div>
          <div style="color:${color};font-weight:700">${d.interpretacion}</div>
          <div style="font-size:10px;color:var(--muted)">${d.nota}</div>
        </div>
      </div>`
  } catch(e) { document.getElementById('clv-pro-res').innerHTML = '<span style="color:var(--red)">Error: '+e+'</span>' }
}

conectarSSE()
initDashboard()
calcCLV()
renderCLVT()
calcKelly()
calcEV()
loadAlertas()
}

// KELLY POPUP
function openKelly(partido, resultado, cuota, edge_pct, casa) {
  document.getElementById('km-partido').textContent = partido
  document.getElementById('km-resultado').textContent = resultado + ' @ ' + casa
  document.getElementById('km-cuota').value = cuota
  document.getElementById('km-edge').textContent = '+' + edge_pct + '%'
  document.getElementById('km-overlay').classList.add('on')
  calcKellyPopup()
}
function closeKelly() {
  document.getElementById('km-overlay').classList.remove('on')
}
function calcKellyPopup() {
  const bank = parseFloat(document.getElementById('km-bank').value) || 5000
  const odds = parseFloat(document.getElementById('km-cuota').value) || 2.0
  const prob = parseFloat(document.getElementById('km-prob').value) / 100 || 0.5
  const frac = parseFloat(document.getElementById('km-frac').value) || 0.25
  const b = odds - 1, q = 1 - prob
  const kp = b > 0 ? (b * prob - q) / b : 0
  const ka = kp * frac
  const stake = Math.max(0, bank * ka)
  const el = document.getElementById('km-result')
  if (kp <= 0) {
    el.innerHTML = '<div style="padding:12px;background:rgba(248,113,113,.07);border-radius:7px;color:var(--red);font-size:11px;font-family:var(--mono)">Sin valor matemÃ¡tico â€” Kelly negativo</div>'
    return
  }
  el.innerHTML = `<div class="k-big"><div class="k-amount" style="color:var(--green)">$${stake.toFixed(0)}</div><div class="k-lbl">apuesta sugerida (${(ka*100).toFixed(1)}% del bankroll)</div></div><div class="k-rows">
    <div class="k-row"><span>Kelly puro</span><span>${(kp*100).toFixed(2)}%</span></div>
    <div class="k-row"><span>Kelly ajustado</span><span>${(ka*100).toFixed(2)}%</span></div>
    <div class="k-row"><span>FracciÃ³n</span><span>${frac}x</span></div>
    <div class="k-row"><span>ROI esperado</span><span style="color:var(--green)">+${((b*prob-q)*100).toFixed(1)}%</span></div>
    <div class="k-row"><span>LÃ­mite 5% bankroll</span><span>$${(bank*0.05).toFixed(0)}</span></div>
  </div>`
}
</script>
<div class="k-overlay" id="km-overlay" onclick="if(event.target===this)closeKelly()">
  <div class="k-modal">
    <button class="k-close" onclick="closeKelly()">&times;</button>
    <div style="font-size:16px;font-weight:800;margin-bottom:2px" id="km-partido"></div>
    <div style="font-size:11px;font-family:var(--mono);color:var(--muted);margin-bottom:16px" id="km-resultado"></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px">
      <div class="field"><label>Cuota</label><input type="number" id="km-cuota" step="0.01" oninput="calcKellyPopup()"></div>
      <div class="field"><label>Prob. real (%)</label><input type="number" id="km-prob" value="55" oninput="calcKellyPopup()"></div>
      <div class="field"><label>Bankroll ($)</label><input type="number" id="km-bank" value="5000" oninput="calcKellyPopup()"></div>
      <div class="field"><label>FracciÃ³n Kelly</label><select id="km-frac" onchange="calcKellyPopup()">
        <option value="0.25" selected>1/4 (seguro)</option>
        <option value="0.5">1/2 (moderado)</option>
        <option value="1">Completo (agresivo)</option>
      </select></div>
    </div>
    <div style="margin-bottom:8px;font-size:10px;font-family:var(--mono);color:var(--muted)">Edge: <span style="color:var(--green)" id="km-edge"></span></div>
    <div id="km-result"></div>
  </div>
</div>
</body>
</html>
"""
