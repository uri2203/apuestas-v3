"""
Dashboard — Bloomberg Terminal Style.
Landing page + 12 módulos de análisis profesional.
"""
import json

# ── CSS Base — Bloomberg Terminal Theme ──────────────────────────────────────
SHARED_CSS = r"""
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0a0a0f;--bg2:#10111a;--bg3:#161822;--bg4:#1c1f2e;
  --surface:rgba(255,255,255,0.02);--surface-hover:rgba(255,255,255,0.04);
  --border:rgba(255,255,255,0.05);--border-hover:rgba(255,255,255,0.10);
  --text:#d4d8e8;--text2:#7a7f96;--text3:#454860;
  --gold:#f5a623;--gold-bg:rgba(245,166,35,0.08);
  --green:#00c853;--green-bg:rgba(0,200,83,0.08);
  --red:#ff1744;--red-bg:rgba(255,23,68,0.08);
  --blue:#448aff;--blue-bg:rgba(68,138,255,0.08);
  --accent:#7c6dfa;--accent-bg:rgba(124,109,250,0.08);
  --cyan:#00e5ff;
  --shadow:0 1px 8px rgba(0,0,0,.5);--radius:4px;--radius-sm:3px
}
.light{--bg:#f0f2f5;--bg2:#ffffff;--bg3:#f5f6f8;--bg4:#e8eaee;--surface:rgba(0,0,0,0.02);--surface-hover:rgba(0,0,0,0.04);--border:rgba(0,0,0,0.06);--border-hover:rgba(0,0,0,0.12);--text:#1a1d2e;--text2:#5a5e72;--text3:#9a9eb0;--shadow:0 1px 8px rgba(0,0,0,.06)}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:'IBM Plex Mono','JetBrains Mono','Fira Code',monospace;font-size:12px;-webkit-font-smoothing:antialiased;line-height:1.5}
a{color:var(--gold);text-decoration:none}
.mono{font-family:'IBM Plex Mono',monospace}

/* TERMINAL FRAME */
.term-frame{display:flex;flex-direction:column;height:100vh;background:var(--bg)}
.term-bar{display:flex;align-items:center;padding:0 14px;height:36px;background:var(--bg2);border-bottom:1px solid var(--border);flex-shrink:0;gap:10px}
.term-bar .brand{font-size:11px;font-weight:700;color:var(--gold);letter-spacing:1.5px;text-transform:uppercase}
.term-bar .sep{width:1px;height:16px;background:var(--border)}
.term-bar nav{display:flex;gap:2px}
.term-bar nav a{padding:3px 8px;border-radius:var(--radius-sm);font-size:10px;color:var(--text2);text-transform:uppercase;letter-spacing:.5px;transition:.15s}
.term-bar nav a:hover{color:var(--text);background:var(--surface-hover)}
.term-bar .status{display:flex;align-items:center;gap:6px;margin-left:auto;font-size:10px;color:var(--text3)}
.term-bar .dot{width:5px;height:5px;border-radius:50%}
.dot.on{background:var(--green);box-shadow:0 0 4px var(--green)}.dot.off{background:var(--red);box-shadow:0 0 4px var(--red)}
.term-bar .clock{font-size:10px;color:var(--text3);min-width:60px;text-align:right}
.term-bar .btn{width:24px;height:24px;border-radius:var(--radius-sm);border:1px solid var(--border);background:transparent;color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:11px;transition:.15s}
.term-bar .btn:hover{background:var(--surface-hover);color:var(--text)}
.term-content{flex:1;overflow-y:auto;padding:16px 20px}
.term-content::-webkit-scrollbar{width:4px}
.term-content::-webkit-scrollbar-track{background:transparent}
.term-content::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}

/* TICKER STRIP */
.ticker{display:flex;gap:0;padding:0 14px;background:var(--bg2);border-bottom:1px solid var(--border);overflow-x:auto;font-size:10px;white-space:nowrap;scrollbar-width:none}
.ticker::-webkit-scrollbar{display:none}
.tk{display:flex;align-items:center;gap:6px;padding:5px 10px;border-right:1px solid var(--border);flex-shrink:0}
.tk:last-child{border:0}
.tk .l{color:var(--text3);text-transform:uppercase;letter-spacing:.5px;font-size:9px}
.tk .v{font-weight:600;font-family:'IBM Plex Mono',monospace}
.tk .v.up{color:var(--green)}.tk .v.dn{color:var(--red)}.tk .v.nt{color:var(--text2)}.tk .v.gd{color:var(--gold)}

/* KPI ROW */
.kpi-row{display:grid;grid-template-columns:repeat(6,1fr);gap:1px;background:var(--border);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden;margin-bottom:16px}
.kp{background:var(--bg2);padding:12px 14px}
.kp .l{font-size:9px;text-transform:uppercase;letter-spacing:.5px;color:var(--text3);margin-bottom:2px;font-weight:500}
.kp .v{font-size:18px;font-weight:700;font-family:'IBM Plex Mono',monospace;line-height:1.2}
.kp .v.pos{color:var(--green)}.kp .v.neg{color:var(--red)}.kp .v.gd{color:var(--gold)}.kp .v.bl{color:var(--blue)}
.kp .s{font-size:9px;color:var(--text2);margin-top:2px}
@media(max-width:900px){.kpi-row{grid-template-columns:repeat(3,1fr)}}
@media(max-width:500px){.kpi-row{grid-template-columns:repeat(2,1fr)}}

/* INSTRUMENT GRID */
.sec-hdr{display:flex;align-items:center;margin:20px 0 10px;gap:10px}
.sec-hdr h2{font-size:11px;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:1px;margin:0;white-space:nowrap}
.sec-hdr .line{flex:1;height:1px;background:var(--border)}
.sec-hdr small{font-size:9px;color:var(--text3);text-transform:uppercase;letter-spacing:.5px}
.inst-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--border);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden}
@media(max-width:900px){.inst-grid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:600px){.inst-grid{grid-template-columns:repeat(2,1fr)}}
.inst{background:var(--bg2);padding:14px 12px;cursor:pointer;transition:.15s;display:flex;flex-direction:column;gap:4px;border-left:2px solid transparent}
.inst:hover{background:var(--bg3);border-left-color:var(--gold)}
.inst .name{font-size:11px;font-weight:600;color:var(--text);text-transform:uppercase;letter-spacing:.3px}
.inst .desc{font-size:10px;color:var(--text2);line-height:1.3}
.inst .tags{font-size:9px;color:var(--text3);display:flex;gap:6px;margin-top:2px;font-family:'IBM Plex Mono',monospace}
.inst .tags .t{color:var(--gold)}

/* LOADING */
.loading{text-align:center;padding:40px;color:var(--text2)}
.spinner{width:18px;height:18px;border:2px solid var(--border);border-top-color:var(--gold);border-radius:50%;animation:spin .7s linear infinite;margin:0 auto 8px}
@keyframes spin{to{transform:rotate(360deg)}}

/* TOAST */
.toast{position:fixed;bottom:16px;right:16px;padding:8px 14px;border-radius:var(--radius-sm);background:var(--bg3);border:1px solid var(--border);color:var(--text);font-size:11px;z-index:9999;box-shadow:var(--shadow);animation:slideUp .2s ease;max-width:320px}
.toast.ok{border-color:var(--green)}.toast.err{border-color:var(--red)}.toast.info{border-color:var(--gold)}
@keyframes slideUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}

/* TABLES */
table{width:100%;border-collapse:collapse;font-size:11px}
th,td{padding:6px 10px;text-align:left;border-bottom:1px solid var(--border)}
th{color:var(--text3);font-weight:600;font-size:9px;text-transform:uppercase;letter-spacing:.5px;background:var(--bg2)}
td{color:var(--text2)}
tr:hover td{background:var(--surface-hover)}
td.num{font-family:'IBM Plex Mono',monospace;text-align:right}

/* CHARTS */
.chart-box{background:var(--bg2);border:1px solid var(--border);border-radius:var(--radius);padding:12px;margin-bottom:10px}
.chart-box canvas{width:100%!important;max-height:220px}

/* SEED */
.seed-bar{display:flex;align-items:center;gap:10px;padding:10px 14px;background:var(--bg2);border:1px solid var(--gold);border-radius:var(--radius);margin:0 0 16px;font-size:11px}
.seed-bar .icon{font-size:14px;flex-shrink:0;color:var(--gold)}
.seed-btn{padding:5px 14px;border:none;border-radius:var(--radius-sm);background:var(--gold);color:#000;font-weight:600;font-size:10px;cursor:pointer;margin-left:auto;flex-shrink:0;transition:.15s;font-family:'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:.5px}
.seed-btn:hover{opacity:.85}
.seed-btn:disabled{opacity:.4;cursor:wait}
"""

# ── Landing Page — Bloomberg Terminal ────────────────────────────────────────
LANDING_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ApuestasPro Terminal</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<style>""" + SHARED_CSS + r"""
.term-hero{display:flex;align-items:flex-start;justify-content:space-between;padding:0 0 14px;border-bottom:1px solid var(--border);margin-bottom:14px}
.term-hero h1{font-size:14px;font-weight:700;color:var(--text);margin:0 0 2px;letter-spacing:-.2px}
.term-hero h1 em{font-style:normal;color:var(--gold)}
.term-hero p{font-size:10px;color:var(--text3);margin:0;text-transform:uppercase;letter-spacing:.5px}
.term-hero .meta{text-align:right;font-size:10px;color:var(--text3)}
.term-hero .meta .val{font-size:11px;font-weight:600;color:var(--text2)}
</style>
</head>
<body>
<div class="term-frame">
  <div class="term-bar">
    <span class="brand">ApuestasPro</span>
    <div class="sep"></div>
    <nav>
      <a href="/panel/value-bets">Value</a>
      <a href="/panel/sharp">Sharp</a>
      <a href="/panel/arbitraje">Arb</a>
      <a href="/panel/ml">ML</a>
      <a href="/panel/bankroll">Bank</a>
      <a href="/panel/rendimiento">Stats</a>
    </nav>
    <div class="status">
      <span class="dot off" id="sd"></span>
      <span id="modeLabel">OFFLINE</span>
    </div>
    <div class="clock" id="clock">--:--</div>
    <button class="btn" onclick="theme()" title="Tema">&#9681;</button>
    <button class="btn" onclick="location='/logout'" title="Salir">&#8592;</button>
  </div>

  <div class="ticker" id="ticker">
    <div class="tk"><span class="l">SYS</span><span class="v nt" id="tkMode">INIT</span></div>
    <div class="tk"><span class="l">BANK</span><span class="v" id="tkBr">$0</span></div>
    <div class="tk"><span class="l">WR</span><span class="v nt" id="tkWr">0%</span></div>
    <div class="tk"><span class="l">ROI</span><span class="v nt" id="tkRoi">0%</span></div>
    <div class="tk"><span class="l">SHARPE</span><span class="v nt" id="tkSh">0.00</span></div>
    <div class="tk"><span class="l">PnL</span><span class="v nt" id="tkPnl">$0</span></div>
    <div class="tk"><span class="l">VB</span><span class="v nt" id="tkVb">0</span></div>
    <div class="tk"><span class="l">DB</span><span class="v nt" id="tkDb">--</span></div>
    <div class="tk"><span class="l">API</span><span class="v nt" id="tkApi">--</span></div>
    <div class="tk"><span class="l">LAT</span><span class="v nt" id="tkLat">--ms</span></div>
  </div>

  <div class="term-content">
    <div class="term-hero">
      <div>
        <h1>Sistema de <em>An&aacute;lisis</em> Deportivo</h1>
        <p>ML Predictivo &middot; Sharp Money &middot; Arbitraje &middot; Value Bets &middot; Bankroll &middot; Simulaci&oacute;n</p>
      </div>
      <div class="meta">
        <div>ULTIMA ACTUALIZACION</div>
        <div class="val" id="lastUpd">--</div>
        <div>v4.4 &middot; <span id="kpiMode">--</span></div>
      </div>
    </div>

    <div class="kpi-row" id="kpiGrid">
      <div class="kp"><div class="l">Bankroll</div><div class="v" id="kpiBr">$0</div><div class="s">Valor actual</div></div>
      <div class="kp"><div class="l">Win Rate</div><div class="v" id="kpiWr">0%</div><div class="s">30 dias</div></div>
      <div class="kp"><div class="l">ROI</div><div class="v" id="kpiRoi">0%</div><div class="s">Retorno total</div></div>
      <div class="kp"><div class="l">Sharpe</div><div class="v" id="kpiSh">0.00</div><div class="s">Ratio riesgo</div></div>
      <div class="kp"><div class="l">PnL Neto</div><div class="v" id="kpiPnl">$0</div><div class="s">30 dias</div></div>
      <div class="kp"><div class="l">Value Bets</div><div class="v" id="kpiVb">0</div><div class="s">Edge: <span id="kpiEdge">0%</span></div></div>
    </div>

    <div class="sec-hdr">
      <h2>Instrumentos</h2>
      <div class="line"></div>
      <small>12 modulos de analisis</small>
    </div>

    <div class="inst-grid">
      <div class="inst" onclick="location='/panel/value-bets'"><div class="name">Value Bets</div><div class="desc">Deteccion de edge positivo en cuotas</div><div class="tags"><span class="t">EDGE</span><span>Smart Filters</span><span>CLV</span></div></div>
      <div class="inst" onclick="location='/panel/sharp'"><div class="name">Sharp Money</div><div class="desc">Movimiento de lineas, steam, alertas</div><div class="tags"><span class="t">LIVE</span><span>CLV</span><span>Alertas</span></div></div>
      <div class="inst" onclick="location='/panel/arbitraje'"><div class="name">Arbitraje</div><div class="desc">Surebets multi-mercado, profit garantizado</div><div class="tags"><span class="t">H2H</span><span>AH</span><span>O/U</span></div></div>
      <div class="inst" onclick="location='/panel/ml'"><div class="name">ML Predictivo</div><div class="desc">MLP + GBM, 30+ features, ensemble</div><div class="tags"><span class="t">MLP</span><span>GBM</span><span>ENS</span></div></div>
      <div class="inst" onclick="location='/panel/bankroll'"><div class="name">Bankroll</div><div class="desc">Kelly, historial, riesgo de ruina</div><div class="tags"><span class="t">KELLY</span><span>Curva</span><span>Sharpe</span></div></div>
      <div class="inst" onclick="location='/panel/simulacion'"><div class="name">Simulacion</div><div class="desc">Trades simulados, verificacion auto</div><div class="tags"><span class="t">BT</span><span>Verify</span><span>PnL</span></div></div>
      <div class="inst" onclick="location='/panel/contabilidad'"><div class="name">Contabilidad</div><div class="desc">P&L, sync automatico, reportes</div><div class="tags"><span class="t">P&L</span><span>Sync</span><span>Reports</span></div></div>
      <div class="inst" onclick="location='/panel/journal'"><div class="name">Trading Journal</div><div class="desc">Bitacora automatica, export CSV</div><div class="tags"><span class="t">LOG</span><span>CSV</span><span>Export</span></div></div>
      <div class="inst" onclick="location='/panel/bookmakers'"><div class="name">Rating Casas</div><div class="desc">Overround, CLV, velocidad ajuste</div><div class="tags"><span class="t">RANK</span><span>CLV</span><span>Scan</span></div></div>
      <div class="inst" onclick="location='/panel/cross-market'"><div class="name">Cross Market</div><div class="desc">H2H vs AH, spreads, comparativa</div><div class="tags"><span class="t">H2H</span><span>AH</span><span>Spread</span></div></div>
      <div class="inst" onclick="location='/panel/backtesting'"><div class="name">Backtesting</div><div class="desc">Historico, estrategias, rendimiento</div><div class="tags"><span class="t">HIST</span><span>Strat</span><span>Perf</span></div></div>
      <div class="inst" onclick="location='/panel/rendimiento'"><div class="name">Rendimiento</div><div class="desc">Graficas, estadisticas avanzadas</div><div class="tags"><span class="t">CHART</span><span>Stats</span><span>Sport</span></div></div>
    </div>

    <div id="seedBanner" class="seed-bar" style="display:none">
      <div class="icon">&#9888;</div>
      <div>
        <strong>Base de datos vacia</strong> — click para poblar con datos iniciales.
        <div id="seedResult" style="font-size:10px;margin-top:3px;color:var(--text3)"></div>
      </div>
      <button class="seed-btn" onclick="seedDB()">&#9654; SEED</button>
    </div>
    <div style="height:40px"></div>
  </div>
</div>

<script>
function clock(){var d=new Date();document.getElementById('clock').textContent=d.toLocaleTimeString('es-MX',{hour:'2-digit',minute:'2-digit',second:'2-digit'});document.getElementById('lastUpd').textContent=d.toLocaleString('es-MX')}
setInterval(clock,1e3);clock()
function theme(){document.documentElement.classList.toggle('light');localStorage.setItem('ap_theme',document.documentElement.classList.contains('light')?'light':'')}
if(localStorage.getItem('ap_theme')==='light')document.documentElement.classList.add('light')
async function seedDB(){try{
  var btn=document.querySelector('.seed-btn'),res=document.getElementById('seedResult')
  btn.disabled=true;btn.textContent='SEMBRANDO...';res.textContent='';res.style.color='var(--text3)'
  var r=await fetch('/api/seed-demo')
  if(!r.ok){var txt=await r.text();throw new Error(txt.slice(0,200))}
  var d=await r.json()
  if(d.status==='ok'||d.total_insertados>0){
    res.textContent=d.total_insertados+' registros insertados';res.style.color='var(--green)'
    btn.textContent='LISTO';setTimeout(function(){document.getElementById('seedBanner').style.display='none';loadKPI()},2e3)
  }else{
    res.textContent='ERROR: '+(d.errores||[]).slice(0,3).join(', ');res.style.color='var(--red)'
    btn.disabled=false;btn.textContent='RETRY'
  }
}catch(e){
  document.getElementById('seedResult').textContent='ERROR: '+e.message
  document.getElementById('seedResult').style.color='var(--red)'
  var btn=document.querySelector('.seed-btn');btn.disabled=false;btn.textContent='RETRY'
}}
async function loadKPI(){try{
  var t0=performance.now()
  var r=await fetch('/api/kpi-summary')
  var lat=Math.round(performance.now()-t0)
  document.getElementById('tkLat').textContent=lat+'ms'
  if(!r.ok)return
  var d=await r.json(),g=d.general||{},b=d.bankroll||{},h=d.hoy||{}
  function n(v){return parseFloat(v)||0}
  var br=n(b.actual)
  document.getElementById('kpiBr').textContent='$'+br.toLocaleString()
  document.getElementById('tkBr').textContent='$'+br.toLocaleString()
  if(br===0)document.getElementById('seedBanner').style.display='flex'
  var wr=g.win_rate||0
  document.getElementById('kpiWr').textContent=wr+'%'
  document.getElementById('kpiWr').className='v '+(wr>=50?'pos':'neg')
  document.getElementById('tkWr').textContent=wr+'%'
  var roi=g.roi_pct||0
  document.getElementById('kpiRoi').textContent=roi+'%'
  document.getElementById('kpiRoi').className='v '+(roi>=0?'pos':'neg')
  document.getElementById('tkRoi').textContent=roi+'%'
  document.getElementById('kpiSh').textContent=(g.sharpe_ratio||0).toFixed(2)
  document.getElementById('tkSh').textContent=(g.sharpe_ratio||0).toFixed(2)
  var pnl=g.ganancia_neta||0
  document.getElementById('kpiPnl').textContent='$'+n(pnl).toLocaleString()
  document.getElementById('kpiPnl').className='v '+(pnl>=0?'pos':'neg')
  document.getElementById('tkPnl').textContent='$'+n(pnl).toLocaleString()
  var vb=h.value_bets||{}
  document.getElementById('kpiVb').textContent=vb.total||0
  document.getElementById('kpiEdge').textContent=(vb.avg_edge||0).toFixed(1)+'%'
  document.getElementById('tkVb').textContent=vb.total||0
  document.getElementById('sd').className='dot on'
  document.getElementById('tkMode').textContent='LIVE'
  document.getElementById('tkMode').className='v up'
  document.getElementById('modeLabel').textContent='ONLINE'
  document.getElementById('kpiMode').textContent='REAL'
  document.getElementById('tkDb').textContent=d.database?.conectada?'OK':'ERR'
  document.getElementById('tkDb').className='v '+(d.database?.conectada?'up':'dn')
  if(d.api_tests?.odds_api?.ok){document.getElementById('tkApi').textContent='OK '+d.api_tests.odds_api.requests_restantes;document.getElementById('tkApi').className='v up'}
  else{document.getElementById('tkApi').textContent='--';document.getElementById('tkApi').className='v nt'}
}catch(e){document.getElementById('tkMode').textContent='ERR';document.getElementById('tkMode').className='v dn'}
setTimeout(loadKPI,3e4)}
loadKPI()
</script>
</body>
</html>"""

# ── Module page wrapper ───────────────────────────────────────────────────
def module_page(title: str, body_html: str, extra_js: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title} — ApuestasPro</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<style>{SHARED_CSS}
.top-bar{{display:flex;align-items:center;gap:8px;margin-bottom:14px;flex-wrap:wrap}}
.top-btn{{padding:5px 14px;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--bg2);color:var(--text2);font-size:10px;font-family:'IBM Plex Mono',monospace;cursor:pointer;transition:.15s;text-transform:uppercase;letter-spacing:.5px}}
.top-btn:hover{{background:var(--bg3);color:var(--text);border-color:var(--border-hover)}}
.top-btn.primary{{background:var(--gold);color:#000;border-color:var(--gold)}}
.top-btn.primary:hover{{opacity:.85}}
select,input[type=number]{{padding:5px 10px;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--bg2);color:var(--text);font-size:10px;font-family:'IBM Plex Mono',monospace}}
</style>
</head>
<body>
<div class="term-frame">
  <div class="term-bar">
    <span class="brand">ApuestasPro</span>
    <div class="sep"></div>
    <nav>
      <a href="/">Home</a>
      <a href="javascript:location.reload()">Reload</a>
    </nav>
    <div class="status" style="margin-left:auto">
      <span>{title}</span>
    </div>
    <button class="btn" onclick="theme()" title="Tema">&#9681;</button>
    <button class="btn" onclick="location='/'" title="Home">&#8592;</button>
  </div>
  <div class="term-content">
    <div id="modLoading" class="loading"><div class="spinner"></div><div>Loading...</div></div>
    <div id="modContent" style="display:none">{body_html}</div>
  </div>
</div>
<script>
const LS='ap_theme';if(localStorage.getItem(LS)==='light')document.documentElement.classList.add('light')
function theme(){{document.documentElement.classList.toggle('light');localStorage.setItem(LS,document.documentElement.classList.contains('light')?'light':'')}}
document.getElementById('modLoading').style.display='none'
document.getElementById('modContent').style.display='block'
function toast(msg,type){{const t=document.createElement('div');t.className='toast '+type;t.textContent=msg;document.body.appendChild(t);setTimeout(()=>t.remove(),3e3)}}
async function api(url){{const r=await fetch(url);if(!r.ok)throw new Error(await r.text());return r.json()}}
{extra_js}
</script>
</body>
</html>"""

# ── MODULES ────────────────────────────────────────────────────────────────

MOD_VALUE_BETS = module_page("Value Bets", """
<div class="kpi-row">
  <div class="kp"><div class="l">Edge Avg</div><div class="v gd" id="vbAvgEdge">0%</div></div>
  <div class="kp"><div class="l">Value Bets</div><div class="v" id="vbCount">0</div></div>
  <div class="kp"><div class="l">Best Edge</div><div class="v pos" id="vbMaxEdge">0%</div></div>
</div>
<div class="top-bar">
  <select id="vbSport"><option value="upcoming">ALL</option><option value="soccer_mexico_ligamx">Liga MX</option><option value="basketball_nba">NBA</option><option value="soccer_epl">EPL</option></select>
  <input id="vbMinEdge" type="number" value="2" step="0.5" style="width:60px" placeholder="Min edge"/>
  <button class="top-btn primary" onclick="loadVB()">SCAN</button>
</div>
<table><thead><tr><th>Match</th><th>Outcome</th><th>Book</th><th>Odds</th><th>Edge</th></tr></thead><tbody id="vbBody"></tbody></table>
""", """
async function loadVB(){try{
  const s=document.getElementById('vbSport').value
  const e=document.getElementById('vbMinEdge').value
  const d=await api('/api/odds/value-bets?deporte='+s+'&edge_minimo='+e)
  const vb=d.value_bets||[]
  let h='',sumE=0,maxE=0
  vb.forEach(v=>{
    h+='<tr><td>'+v.partido+'</td><td>'+v.resultado+'</td><td>'+v.casa+'</td><td class="num">'+v.cuota+'</td><td class="num" style="color:var(--gold)">'+v.edge_porcentaje+'%</td></tr>'
    sumE+=parseFloat(v.edge_porcentaje);maxE=Math.max(maxE,parseFloat(v.edge_porcentaje))
  })
  document.getElementById('vbBody').innerHTML=h||'<tr><td colspan="5" style="text-align:center;color:var(--text3)">No value bets found</td></tr>'
  document.getElementById('vbCount').textContent=vb.length
  document.getElementById('vbAvgEdge').textContent=(vb.length?(sumE/vb.length).toFixed(1):'0')+'%'
  document.getElementById('vbMaxEdge').textContent=maxE.toFixed(1)+'%'
}catch(e){toast('Error loading value bets','err')}}
loadVB()
""")

MOD_SHARP = module_page("Sharp Money", """
<div class="kpi-row">
  <div class="kp"><div class="l">Alerts</div><div class="v" id="sharpCount">0</div><div class="s">Last 24h</div></div>
  <div class="kp"><div class="l">CLV Avg</div><div class="v gd" id="sharpClv">0</div></div>
</div>
<table><thead><tr><th>Match</th><th>Signal</th><th>From</th><th>To</th><th>Urgency</th></tr></thead><tbody id="sharpBody"></tbody></table>
""", """
async function loadSharp(){try{
  const d=await api('/api/odds/arbitraje?min_profit=0.1')
  const a=d.arbitrajes||[]
  document.getElementById('sharpCount').textContent=a.length
  let h=''
  a.forEach(v=>{
    h+='<tr><td>'+v.partido+'</td><td>'+v.profit+'%</td><td>'+v.n_bookmakers+'</td><td>'+v.profit_pct+'%</td><td>MED</td></tr>'
  })
  document.getElementById('sharpBody').innerHTML=h||'<tr><td colspan="5" style="text-align:center;color:var(--text3)">No signals</td></tr>'
}catch(e){toast('Error','err')}}
loadSharp()
""")

MOD_ARBITRAJE = module_page("Arbitraje", """
<div class="kpi-row">
  <div class="kp"><div class="l">Arbs Found</div><div class="v gd" id="arbCount">0</div></div>
  <div class="kp"><div class="l">Max Profit</div><div class="v pos" id="arbMaxProfit">0%</div></div>
</div>
<div class="top-bar">
  <input id="arbMinProfit" type="number" value="0.5" step="0.1" style="width:60px"/>
  <button class="top-btn primary" onclick="loadArb()">SCAN</button>
</div>
<table><thead><tr><th>Match</th><th>Profit</th><th>Outcomes</th></tr></thead><tbody id="arbBody"></tbody></table>
""", """
async function loadArb(){try{
  const m=document.getElementById('arbMinProfit').value
  const d=await api('/api/odds/arbitraje?min_profit='+m)
  const a=d.arbitrajes||[]
  document.getElementById('arbCount').textContent=a.length
  let maxP=0,h=''
  a.forEach(v=>{
    maxP=Math.max(maxP,parseFloat(v.profit_pct||0))
    h+='<tr><td>'+v.partido+'</td><td class="num" style="color:var(--green)">'+v.profit_pct+'%</td><td>'+v.n_resultados+'</td></tr>'
  })
  document.getElementById('arbMaxProfit').textContent=maxP.toFixed(2)+'%'
  document.getElementById('arbBody').innerHTML=h||'<tr><td colspan="3" style="text-align:center;color:var(--text3)">No arbitrage found</td></tr>'
}catch(e){toast('Error','err')}}
loadArb()
""")

MOD_ML = module_page("ML Predictivo", """
<div class="kpi-row">
  <div class="kp"><div class="l">Models</div><div class="v">MLP + GBM</div></div>
  <div class="kp"><div class="l">Features</div><div class="v" id="mlFeat">0</div></div>
  <div class="kp"><div class="l">Confidence</div><div class="v gd" id="mlConf">--</div></div>
</div>
<div class="top-bar">
  <select id="mlLiga"><option value="liga_mx">Liga MX</option><option value="mls">MLS</option><option value="premier_league">EPL</option><option value="la_liga">La Liga</option><option value="serie_a">Serie A</option><option value="bundesliga">Bundesliga</option><option value="ligue_1">Ligue 1</option></select>
  <button class="top-btn primary" onclick="trainML()">TRAIN</button>
  <button class="top-btn" onclick="loadML()">REFRESH</button>
</div>
<div id="mlStatus" style="font-size:10px;color:var(--text2);margin-bottom:8px"></div>
<table><thead><tr><th>Feature</th><th>Importance</th></tr></thead><tbody id="mlBody"></tbody></table>
""", """
async function loadML(){try{
  const l=document.getElementById('mlLiga').value
  const d=await api('/api/ml/v2/features?liga='+l)
  const f=d.features||[]
  document.getElementById('mlFeat').textContent=f.length
  document.getElementById('mlConf').textContent=f.length?'OK':'EMPTY'
  let h=''
  f.slice(0,15).forEach(v=>{
    h+='<tr><td>'+v.feature_name+'</td><td><div style="background:var(--bg4);border-radius:2px;overflow:hidden;width:100px;display:inline-block"><div style="width:'+(v.importance*100)+'%;height:4px;background:var(--gold);border-radius:2px"></div></div> '+(v.importance*100).toFixed(1)+'%</td></tr>'
  })
  document.getElementById('mlBody').innerHTML=h||'<tr><td colspan="2" style="text-align:center;color:var(--text3)">Train models first</td></tr>'
}catch(e){toast('Error','err')}}
async function trainML(){try{
  document.getElementById('mlStatus').textContent='Training...'
  await api('/api/ml/v2/train')
  document.getElementById('mlStatus').textContent='Training started (background)'
  setTimeout(loadML,5e3)
}catch(e){toast('Error','err')}}
loadML()
""")

MOD_BANKROLL = module_page("Bankroll", """
<div class="kpi-row">
  <div class="kp"><div class="l">Current</div><div class="v" id="brActual">$0</div></div>
  <div class="kp"><div class="l">Total Bets</div><div class="v gd" id="brTotal">0</div></div>
  <div class="kp"><div class="l">Win Rate</div><div class="v pos" id="brWinRate">0%</div></div>
  <div class="kp"><div class="l">Net PnL</div><div class="v" id="brGanancia">$0</div></div>
</div>
<div class="chart-box"><canvas id="brChart"></canvas></div>
<table><thead><tr><th>Date</th><th>Event</th><th>Bankroll</th></tr></thead><tbody id="brBody"></tbody></table>
""", """
let brChart=null
async function loadBR(){try{
  const d=await api('/api/dashboard/rendimiento')
  const g=d.general||{},b=d.bankroll||{},h=b.history||[]
  document.getElementById('brActual').textContent='$'+(b.actual||0).toLocaleString()
  document.getElementById('brTotal').textContent=g.total_apuestas||0
  document.getElementById('brWinRate').textContent=(g.win_rate||0)+'%'
  document.getElementById('brGanancia').textContent='$'+(g.ganancia_neta||0).toLocaleString()
  let hh=''
  h.slice().reverse().slice(-20).forEach(v=>{
    hh+='<tr><td>'+(v.fecha||'').slice(0,10)+'</td><td>'+v.evento+'</td><td class="num">$'+v.bankroll+'</td></tr>'
  })
  document.getElementById('brBody').innerHTML=hh||'<tr><td colspan="3" style="text-align:center;color:var(--text3)">No history</td></tr>'
  if(brChart)brChart.destroy()
  brChart=new Chart(document.getElementById('brChart'),{type:'line',data:{labels:h.map(v=>(v.fecha||'').slice(5,10)),datasets:[{label:'Bankroll',data:h.map(v=>v.bankroll),borderColor:'#f5a623',backgroundColor:'rgba(245,166,35,0.05)',fill:true,tension:.3,pointRadius:1,borderWidth:1.5}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:{color:'rgba(255,255,255,0.03)'},ticks:{color:'var(--text3)',font:{size:9,family:'IBM Plex Mono'}}},y:{grid:{color:'rgba(255,255,255,0.03)'},ticks:{color:'var(--text3)',font:{size:9,family:'IBM Plex Mono'}}}}}})
}catch(e){toast('Error','err')}}
loadBR()
""")

MOD_SIMULACION = module_page("Simulacion", """
<div class="kpi-row">
  <div class="kp"><div class="l">Total Trades</div><div class="v" id="simTotal">0</div></div>
  <div class="kp"><div class="l">Won</div><div class="v pos" id="simGanadas">0</div></div>
  <div class="kp"><div class="l">Lost</div><div class="v neg" id="simPerdidas">0</div></div>
  <div class="kp"><div class="l">PnL</div><div class="v gd" id="simPnl">$0</div></div>
</div>
<table><thead><tr><th>Match</th><th>Pick</th><th>Odds</th><th>Edge</th><th>Result</th><th>PnL</th></tr></thead><tbody id="simBody"></tbody></table>
""", """
async function loadSim(){try{
  const d=await api('/api/simulacion/status')
  document.getElementById('simTotal').textContent=d.total||0
  document.getElementById('simGanadas').textContent=d.ganadas||0
  document.getElementById('simPerdidas').textContent=d.perdidas||0
  document.getElementById('simPnl').textContent='$'+(d.pnl_total||0).toLocaleString()
  const t=d.trades||[]
  let h=''
  t.forEach(v=>{
    const cls=v.resultado_simulado==='ganada'?'pos':v.resultado_simulado==='perdida'?'neg':'gd'
    h+='<tr><td>'+v.partido+'</td><td>'+v.seleccion+'</td><td class="num">'+v.cuota+'</td><td class="num">'+(v.edge_pct||0)+'%</td><td class="'+cls+'">'+v.resultado_simulado+'</td><td class="num">$'+(v.pnl_real||0)+'</td></tr>'
  })
  document.getElementById('simBody').innerHTML=h||'<tr><td colspan="6" style="text-align:center;color:var(--text3)">No trades</td></tr>'
}catch(e){toast('Error','err')}}
loadSim()
""")

MOD_CONTABILIDAD = module_page("Contabilidad", """
<div class="kpi-row">
  <div class="kp"><div class="l">Transactions</div><div class="v" id="conCount">0</div></div>
  <div class="kp"><div class="l">Won</div><div class="v pos" id="conGanadas">0</div></div>
  <div class="kp"><div class="l">Lost</div><div class="v neg" id="conPerdidas">0</div></div>
  <div class="kp"><div class="l">Net</div><div class="v gd" id="conNeto">$0</div></div>
</div>
<div class="chart-box"><canvas id="conChart"></canvas></div>
<table><thead><tr><th>Strategy</th><th>Total</th><th>Won</th><th>Lost</th><th>Net</th></tr></thead><tbody id="conBody"></tbody></table>
""", """
async function loadCon(){try{
  const d=await api('/api/contabilidad/pnl-estrategia')
  document.getElementById('conCount').textContent=d.reduce((s,v)=>s+(v.total||0),0)
  let g=0,p=0,n=0,h=''
  d.forEach(v=>{
    g+=v.ganadas||0;p+=v.perdidas||0;n+=v.neto||0
    h+='<tr><td>'+v.estrategia+'</td><td>'+v.total+'</td><td class="pos">'+v.ganadas+'</td><td class="neg">'+v.perdidas+'</td><td class="'+(v.neto>=0?'pos':'neg')+'">$'+(v.neto||0)+'</td></tr>'
  })
  document.getElementById('conGanadas').textContent=g
  document.getElementById('conPerdidas').textContent=p
  document.getElementById('conNeto').textContent='$'+n.toLocaleString()
  document.getElementById('conBody').innerHTML=h||'<tr><td colspan="5" style="text-align:center;color:var(--text3)">No data</td></tr>'
}catch(e){toast('Error','err')}}
loadCon()
""")

MOD_JOURNAL = module_page("Trading Journal", """
<div class="kpi-row">
  <div class="kp"><div class="l">Actions (7d)</div><div class="v" id="jrTotal">0</div></div>
  <div class="kp"><div class="l">Types</div><div class="v" id="jrTipos">0</div></div>
</div>
<div class="top-bar">
  <button class="top-btn" onclick="exportCSV()">EXPORT CSV</button>
  <button class="top-btn" onclick="loadJR()">REFRESH</button>
</div>
<table><thead><tr><th>Date</th><th>Action</th><th>Match</th><th>Detail</th></tr></thead><tbody id="jrBody"></tbody></table>
""", """
async function loadJR(){try{
  const d=await api('/api/journal/resumen')
  const t=d.por_tipo||{},u=d.ultimas_acciones||[]
  document.getElementById('jrTotal').textContent=d.total_acciones||0
  document.getElementById('jrTipos').textContent=Object.keys(t).length
  let h=''
  u.forEach(v=>{
    h+='<tr><td>'+(v.created_at||'').slice(0,10)+'</td><td>'+v.tipo_accion+'</td><td>'+(v.partido||'-')+'</td><td>'+v.seleccion+' $'+(v.monto||0)+'</td></tr>'
  })
  document.getElementById('jrBody').innerHTML=h||'<tr><td colspan="4" style="text-align:center;color:var(--text3)">No activity</td></tr>'
}catch(e){toast('Error','err')}}
function exportCSV(){window.open('/api/journal/export-csv','_blank')}
loadJR()
""")

MOD_BOOKMAKERS = module_page("Rating Casas", """
<div class="kpi-row">
  <div class="kp"><div class="l">Bookmakers</div><div class="v" id="bmCount">0</div></div>
  <div class="kp"><div class="l">Best Overround</div><div class="v pos" id="bmBestOver">0</div></div>
</div>
<div class="top-bar">
  <button class="top-btn primary" onclick="scanBM()">SCAN BOOKS</button>
  <div id="bmStatus" style="font-size:10px;color:var(--text2)"></div>
</div>
<table><thead><tr><th>Book</th><th>Overround</th><th>CLV</th><th>Appearances</th></tr></thead><tbody id="bmBody"></tbody></table>
""", """
async function loadBM(){try{
  const d=await api('/api/bookmakers/rating')
  const r=d.ratings||[]
  document.getElementById('bmCount').textContent=r.length
  document.getElementById('bmBestOver').textContent=r.length?Math.min(...r.map(v=>v.avg_overround||99)).toFixed(2)+'%':'0'
  let h=''
  r.sort((a,b)=>(a.avg_overround||99)-(b.avg_overround||99)).forEach(v=>{
    h+='<tr><td>'+v.bookmaker+'</td><td class="num">'+(v.avg_overround||0).toFixed(2)+'%</td><td class="num">'+(v.avg_clv||0).toFixed(4)+'</td><td class="num">'+v.apariciones+'</td></tr>'
  })
  document.getElementById('bmBody').innerHTML=h||'<tr><td colspan="4" style="text-align:center;color:var(--text3)">Scan books first</td></tr>'
}catch(e){toast('Error','err')}}
async function scanBM(){try{
  document.getElementById('bmStatus').textContent='Scanning...'
  await api('/api/bookmakers/scan')
  document.getElementById('bmStatus').textContent='Done'
  loadBM()
}catch(e){document.getElementById('bmStatus').textContent='Error';toast('Error','err')}}
loadBM()
""")

MOD_CROSS = module_page("Cross Market", """
<div class="kpi-row">
  <div class="kp"><div class="l">Opportunities</div><div class="v gd" id="cmCount">0</div></div>
  <div class="kp"><div class="l">Markets</div><div class="v">H2H vs AH</div></div>
</div>
<div class="top-bar"><button class="top-btn primary" onclick="loadCM()">ANALYZE</button></div>
<table><thead><tr><th>Match</th><th>H2H</th><th>AH</th><th>Diff</th></tr></thead><tbody id="cmBody"></tbody></table>
""", """
async function loadCM(){try{
  const d=await api('/api/odds/arbitraje?min_profit=0.1')
  const a=d.arbitrajes||[]
  document.getElementById('cmCount').textContent=a.length
  let h=''
  a.slice(0,20).forEach(v=>{
    h+='<tr><td>'+v.partido+'</td><td>H2H</td><td class="num">'+v.profit_pct+'%</td><td class="num pos">'+v.profit_pct+'%</td></tr>'
  })
  document.getElementById('cmBody').innerHTML=h||'<tr><td colspan="4" style="text-align:center;color:var(--text3)">No data</td></tr>'
}catch(e){toast('Error','err')}}
loadCM()
""")

MOD_BACKTESTING = module_page("Backtesting", """
<div class="kpi-row">
  <div class="kp"><div class="l">Results</div><div class="v" id="btTotal">0</div></div>
  <div class="kp"><div class="l">Accuracy</div><div class="v gd" id="btAcc">0%</div></div>
</div>
<div class="top-bar"><button class="top-btn primary" onclick="loadBT()">REFRESH</button></div>
<table><thead><tr><th>Config</th><th>Type</th><th>Summary</th></tr></thead><tbody id="btBody"></tbody></table>
""", """
async function loadBT(){try{
  const d=await api('/api/dashboard/rendimiento')
  const g=d.general||{}
  document.getElementById('btTotal').textContent=g.total_apuestas||0
  document.getElementById('btAcc').textContent=(g.win_rate||0)+'%'
}catch(e){toast('Error','err')}}
loadBT()
""")

MOD_RENDIMIENTO = module_page("Rendimiento", """
<div class="kpi-row">
  <div class="kp"><div class="l">Total Bets</div><div class="v" id="rpTotal">0</div></div>
  <div class="kp"><div class="l">Win Rate</div><div class="v gd" id="rpWinRate">0%</div></div>
  <div class="kp"><div class="l">Sharpe</div><div class="v" id="rpSharpe">0</div></div>
  <div class="kp"><div class="l">ROI</div><div class="v pos" id="rpRoi">0%</div></div>
</div>
<div class="chart-box"><canvas id="rpChart"></canvas></div>
<table><thead><tr><th>Sport</th><th>Total</th><th>Won</th><th>Lost</th><th>Net</th></tr></thead><tbody id="rpBody"></tbody></table>
""", """
let rpChart=null
async function loadRP(){try{
  const d=await api('/api/dashboard/rendimiento')
  const g=d.general||{},p=d.por_deporte||[],b=d.bankroll||{},h=b.history||[]
  document.getElementById('rpTotal').textContent=g.total_apuestas||0
  document.getElementById('rpWinRate').textContent=(g.win_rate||0)+'%'
  document.getElementById('rpSharpe').textContent=(g.sharpe_ratio||0).toFixed(2)
  document.getElementById('rpRoi').textContent=(g.roi_pct||0)+'%'
  let ht=''
  p.forEach(v=>{
    const net=v.ganancia_neta||0
    ht+='<tr><td>'+v.liga+'</td><td class="num">'+v.total+'</td><td class="num pos">'+v.ganadas+'</td><td class="num neg">'+v.perdidas+'</td><td class="num '+(net>=0?'pos':'neg')+'">$'+net+'</td></tr>'
  })
  document.getElementById('rpBody').innerHTML=ht||'<tr><td colspan="5" style="text-align:center;color:var(--text3)">No data</td></tr>'
  if(rpChart)rpChart.destroy()
  rpChart=new Chart(document.getElementById('rpChart'),{type:'bar',data:{labels:p.map(v=>v.liga||'?'),datasets:[{label:'PnL',data:p.map(v=>v.ganancia_neta||0),backgroundColor:p.map(v=>(v.ganancia_neta||0)>=0?'rgba(0,200,83,0.6)':'rgba(255,23,68,0.6)'),borderRadius:2,barThickness:20}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:{display:false},ticks:{color:'var(--text3)',font:{size:9,family:'IBM Plex Mono'}}},y:{grid:{color:'rgba(255,255,255,0.03)'},ticks:{color:'var(--text3)',font:{size:9,family:'IBM Plex Mono'}}}}}})
}catch(e){toast('Error','err')}}
loadRP()
""")

# ── Module map ──────────────────────────────────────────────────────────────
MODULES = {
    "value-bets":    ("Value Bets",      MOD_VALUE_BETS),
    "sharp":         ("Sharp Money",     MOD_SHARP),
    "arbitraje":     ("Arbitraje",       MOD_ARBITRAJE),
    "ml":            ("ML Predictivo",   MOD_ML),
    "bankroll":      ("Bankroll",        MOD_BANKROLL),
    "simulacion":    ("Simulacion",      MOD_SIMULACION),
    "contabilidad":  ("Contabilidad",    MOD_CONTABILIDAD),
    "journal":       ("Trading Journal", MOD_JOURNAL),
    "bookmakers":    ("Rating Casas",    MOD_BOOKMAKERS),
    "cross-market":  ("Cross Market",    MOD_CROSS),
    "backtesting":   ("Backtesting",     MOD_BACKTESTING),
    "rendimiento":   ("Rendimiento",     MOD_RENDIMIENTO),
}

# ── Main export ──────────────────────────────────────────────────────────
HTML = LANDING_HTML
