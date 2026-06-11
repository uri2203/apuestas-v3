"""
Dashboard — Landing page + módulos individuales con control de ventana.
"""
import json

# ── Estilos compartidos ──────────────────────────────────────────────────
SHARED_CSS = r"""
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#07080b;--bg2:#0d0e14;--bg3:#13151e;--bg4:#1a1d2b;--surface:rgba(255,255,255,0.03);--surface-hover:rgba(255,255,255,0.06);--border:rgba(255,255,255,0.06);--border-hover:rgba(255,255,255,0.12);--text:#e8eaf0;--text2:#8b8fa3;--text3:#535766;--accent:#6c5ce7;--accent2:#a29bfe;--green:#00cec9;--green-bg:rgba(0,206,201,0.1);--red:#ff7675;--red-bg:rgba(255,118,117,0.1);--gold:#fdcb6e;--gold-bg:rgba(253,203,110,0.1);--blue:#74b9ff;--blue-bg:rgba(116,185,255,0.1);--shadow:0 2px 12px rgba(0,0,0,.4);--radius:14px;--radius-sm:8px}
.light{--bg:#f0f2f5;--bg2:#ffffff;--bg3:#f8f9fb;--bg4:#eef0f4;--surface:rgba(0,0,0,0.02);--surface-hover:rgba(0,0,0,0.04);--border:rgba(0,0,0,0.08);--border-hover:rgba(0,0,0,0.15);--text:#1a1d2e;--text2:#5a5e72;--text3:#9a9eb0;--shadow:0 2px 12px rgba(0,0,0,.08)}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:'Inter',system-ui,-apple-system,sans-serif;font-size:13px;-webkit-font-smoothing:antialiased}
.mono{font-family:'JetBrains Mono',monospace}
a{color:var(--accent2);text-decoration:none}

/* WINDOW FRAME */
.win-frame{display:flex;flex-direction:column;height:100vh;background:var(--bg2)}
.win-titlebar{display:flex;align-items:center;padding:0 16px;height:44px;background:var(--bg3);border-bottom:1px solid var(--border);flex-shrink:0;gap:8px;-webkit-app-region:drag}
.win-titlebar .win-dots{display:flex;gap:6px;-webkit-app-region:no-drag}
.win-titlebar .win-dot{width:12px;height:12px;border-radius:50%;border:none;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:7px;color:transparent;transition:.15s}
.win-titlebar .win-dot:hover{color:rgba(0,0,0,.5)}
.win-dot.close{background:#ff5f57}.win-dot.minimize{background:#febc2e}.win-dot.maximize{background:#28c840}
.win-titlebar .win-title{font-size:12px;font-weight:600;color:var(--text2);margin-left:8px;flex:1}
.win-titlebar .win-nav{display:flex;gap:4px;-webkit-app-region:no-drag}
.win-titlebar .win-nav a{padding:4px 10px;border-radius:5px;font-size:11px;color:var(--text2);background:var(--surface);transition:.2s}
.win-titlebar .win-nav a:hover{background:var(--surface-hover);color:var(--text)}
.win-content{flex:1;overflow-y:auto;padding:20px 24px}
.win-content::-webkit-scrollbar{width:6px}
.win-content::-webkit-scrollbar-track{background:transparent}
.win-content::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}

/* LOADING */
.loading{text-align:center;padding:60px 20px;color:var(--text2)}
.spinner{width:24px;height:24px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .7s linear infinite;margin:0 auto 12px}
@keyframes spin{to{transform:rotate(360deg)}}

/* NOTIFICATIONS */
.toast{position:fixed;bottom:20px;right:20px;padding:10px 18px;border-radius:var(--radius-sm);background:var(--bg3);border:1px solid var(--border);color:var(--text);font-size:12px;z-index:9999;box-shadow:var(--shadow);animation:slideUp .3s ease;max-width:360px}
.toast.ok{border-color:var(--green)}.toast.err{border-color:var(--red)}.toast.info{border-color:var(--accent)}
@keyframes slideUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}

/* KPI CARDS */
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin-bottom:24px}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px 18px;transition:.2s}
.kpi:hover{border-color:var(--border-hover);background:var(--surface-hover)}
.kpi .label{font-size:10px;text-transform:uppercase;letter-spacing:.5px;color:var(--text3);margin-bottom:4px}
.kpi .value{font-size:22px;font-weight:700;font-family:'JetBrains Mono',monospace}
.kpi .value.green{color:var(--green)}.kpi .value.red{color:var(--red)}.kpi .value.gold{color:var(--gold)}
.kpi .sub{font-size:10px;color:var(--text2);margin-top:2px}

/* MODULE GRID */
.module-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px;max-width:860px;margin:0 auto}
.module-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px 16px;text-align:center;cursor:pointer;transition:.25s}
.module-card:hover{background:var(--surface-hover);border-color:var(--border-hover);transform:translateY(-2px);box-shadow:var(--shadow)}
.module-card .icon{font-size:28px;margin-bottom:8px;display:block}
.module-card .name{font-size:12px;font-weight:600;margin-bottom:4px}
.module-card .desc{font-size:10px;color:var(--text2);line-height:1.4}
.module-card .badge{position:absolute;top:-6px;right:-6px;min-width:20px;height:20px;padding:0 6px;border-radius:10px;background:var(--red);color:#fff;font-size:9px;font-weight:700;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(255,118,117,.4)}
.module-card{position:relative}

/* CHARTS */
.chart-container{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:12px}
.chart-container canvas{width:100%!important;max-height:280px}

/* TABLES */
table{width:100%;border-collapse:collapse;font-size:12px}
th,td{padding:8px 12px;text-align:left;border-bottom:1px solid var(--border)}
th{color:var(--text3);font-weight:600;font-size:10px;text-transform:uppercase;letter-spacing:.3px}
td{color:var(--text2)}
tr:hover td{background:var(--surface-hover)}
"""

# ── Landing page ─────────────────────────────────────────────────────────
LANDING_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ApuestasPro — Sistema Profesional</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet"/>
<style>
""" + SHARED_CSS + r"""
.landing{max-width:960px;margin:0 auto;padding:0 20px}
.hero{text-align:center;padding:50px 20px 30px}
.hero h1{font-size:34px;font-weight:800;letter-spacing:-1px;margin-bottom:8px}
.hero h1 em{color:var(--accent);font-style:normal}
.hero p{color:var(--text2);font-size:14px;max-width:520px;margin:0 auto;line-height:1.6}
.hero .version{font-size:10px;color:var(--text3);font-family:'JetBrains Mono',monospace;margin-top:10px}
.hero .version span{color:var(--accent)}
.section-title{font-size:15px;font-weight:700;margin:24px 0 14px;display:flex;align-items:center;gap:8px}
.section-title small{font-size:11px;font-weight:400;color:var(--text3)}
.topbar{display:flex;align-items:center;padding:0 20px;height:48px;background:var(--bg2);border-bottom:1px solid var(--border);gap:10px}
.logo{font-size:15px;font-weight:800;letter-spacing:-.3px;display:flex;align-items:center;gap:5px}
.logo em{color:var(--accent);font-style:normal}
.logo small{font-size:7px;color:var(--text3);font-weight:500;text-transform:uppercase;letter-spacing:1px}
.spacer{flex:1}
.topbar .clock{font-size:11px;color:var(--text3);font-family:'JetBrains Mono',monospace}
.top-btn{width:30px;height:30px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:13px;transition:.2s}
.top-btn:hover{background:var(--bg3);color:var(--text);border-color:var(--border-hover)}
.status-dot{width:6px;height:6px;border-radius:50%;display:inline-block}
.status-dot.on{background:var(--green);box-shadow:0 0 6px var(--green)}
.status-dot.off{background:var(--red);box-shadow:0 0 6px var(--red)}
</style>
</head>
<body>
<div class="topbar">
  <div class="logo">Apuestas<em>Pro</em> <small>v4.3</small></div>
  <div class="spacer"></div>
  <span id="statusDot" class="status-dot off"></span>
  <span class="clock" id="clock">--:--</span>
  <button class="top-btn" onclick="toggleTheme()" title="Tema">&#9681;</button>
  <button class="top-btn" onclick="location.href='/logout'" title="Salir">&#8592;</button>
</div>
<div class="landing">
  <div class="hero">
    <h1>Sistema Profesional de <em>Apuestas</em></h1>
    <p>Machine Learning, Sharp Money, Arbitraje, Value Bets y gesti&oacute;n de bankroll en un solo lugar.</p>
    <div class="version">v4.3 &middot; <span id="kpiMode">REAL</span> &middot; <span id="kpiDb">DB conectada</span></div>
  </div>

  <div id="kpiGrid" class="kpi-grid">
    <div class="kpi"><div class="label">Bankroll</div><div class="value" id="kpiBankroll">$0</div><div class="sub" id="kpiBrChange">---</div></div>
    <div class="kpi"><div class="label">Win Rate</div><div class="value gold" id="kpiWinRate">0%</div><div class="sub">&Uacute;ltimos 30 d&iacute;as</div></div>
    <div class="kpi"><div class="label">ROI</div><div class="value" id="kpiRoi">0%</div><div class="sub">Retorno sobre inversi&oacute;n</div></div>
    <div class="kpi"><div class="label">Sharpe Ratio</div><div class="value" id="kpiSharpe">0</div><div class="sub">Ajustado por riesgo</div></div>
    <div class="kpi"><div class="label">Ganancia Neta</div><div class="value green" id="kpiGanancia">$0</div><div class="sub">&Uacute;ltimos 30 d&iacute;as</div></div>
    <div class="kpi"><div class="label">Value Bets Hoy</div><div class="value" id="kpiVb">0</div><div class="sub">Edge promedio: <span id="kpiVbEdge">0%</span></div></div>
  </div>

  <div class="section-title">M&oacute;dulos <small>— Acceso r&aacute;pido</small></div>
  <div class="module-grid" id="moduleGrid">
    <div class="module-card" onclick="go('/panel/value-bets')"><span class="icon">&#9889;</span><div class="name">Value Bets</div><div class="desc">Edge, cuotas justas, filtros inteligentes</div></div>
    <div class="module-card" onclick="go('/panel/sharp')"><span class="icon">&#128200;</span><div class="name">Sharp Money</div><div class="desc">Movimiento de l&iacute;neas, CLV, steam</div></div>
    <div class="module-card" onclick="go('/panel/arbitraje')"><span class="icon">&#9878;</span><div class="name">Arbitraje</div><div class="desc">Surebets en vivo, profit garantizado</div></div>
    <div class="module-card" onclick="go('/panel/ml')"><span class="icon">&#129302;</span><div class="name">ML Predictivo</div><div class="desc">MLP + GBM, 30+ features, confianza</div></div>
    <div class="module-card" onclick="go('/panel/bankroll')"><span class="icon">&#128176;</span><div class="name">Bankroll</div><div class="desc">Kelly, historial, riesgo de ruina</div></div>
    <div class="module-card" onclick="go('/panel/simulacion')"><span class="icon">&#128202;</span><div class="name">Simulaci&oacute;n</div><div class="desc">Trades simulados, verificaci&oacute;n autom&aacute;tica</div></div>
    <div class="module-card" onclick="go('/panel/contabilidad')"><span class="icon">&#128221;</span><div class="name">Contabilidad</div><div class="desc">P&L, sync autom&aacute;tico, reportes</div></div>
    <div class="module-card" onclick="go('/panel/journal')"><span class="icon">&#128214;</span><div class="name">Trading Journal</div><div class="desc">Bit&aacute;cora autom&aacute;tica, export CSV</div></div>
    <div class="module-card" onclick="go('/panel/bookmakers')"><span class="icon">&#127954;</span><div class="name">Rating Casas</div><div class="desc">Overround, CLV, velocidad ajuste</div></div>
    <div class="module-card" onclick="go('/panel/cross-market')"><span class="icon">&#8644;</span><div class="name">Cross Market</div><div class="desc">H2H vs AH, spreads, totals</div></div>
    <div class="module-card" onclick="go('/panel/backtesting')"><span class="icon">&#128270;</span><div class="name">Backtesting</div><div class="desc">Hist&oacute;rico, estrategias, rendimiento</div></div>
    <div class="module-card" onclick="go('/panel/rendimiento')"><span class="icon">&#128200;</span><div class="name">Rendimiento</div><div class="desc">Gr&aacute;ficas, estad&iacute;sticas avanzadas</div></div>
  </div>
  <div style="height:40px"></div>
</div>
<script>
const LS='theme',D=document;
function toggleTheme(){D.body.classList.toggle('light');localStorage.setItem(LS,D.body.classList.contains('light')?'light':'')}
if(localStorage.getItem(LS)==='light')D.body.classList.add('light')
function go(p){location.href=p}
function clock(){const d=new Date();document.getElementById('clock').textContent=d.toLocaleTimeString('es-MX',{hour:'2-digit',minute:'2-digit'})}
setInterval(clock,1e4);clock()
async function loadKPI(){try{
  const r=await fetch('/api/dashboard/rendimiento')
  if(!r.ok)return
  const d=await r.json()
  const g=d.general||{},b=d.bankroll||{},h=d.hoy||{}
  document.getElementById('kpiBankroll').textContent='$'+(b.actual||0).toLocaleString()
  document.getElementById('kpiWinRate').textContent=(g.win_rate||0)+'%'
  document.getElementById('kpiRoi').textContent=(g.roi_pct||0)+'%'
  document.getElementById('kpiSharpe').textContent=(g.sharpe_ratio||0).toFixed(2)
  document.getElementById('kpiGanancia').textContent='$'+(g.ganancia_neta||0).toLocaleString()
  const vb=h.value_bets||{}
  document.getElementById('kpiVb').textContent=vb.total||0
  document.getElementById('kpiVbEdge').textContent=(vb.avg_edge||0).toFixed(1)+'%'
  const status=document.getElementById('statusDot')
  status.className='status-dot on'
}catch(e){}
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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet"/>
<style>{SHARED_CSS}</style>
</head>
<body>
<div class="win-frame">
  <div class="win-titlebar">
    <div class="win-dots">
      <div class="win-dot close" onclick="closeWin()" title="Cerrar">&#10005;</div>
      <div class="win-dot minimize" onclick="minWin()" title="Minimizar">&#9472;</div>
      <div class="win-dot maximize" onclick="maxWin()" title="Maximizar">&#9678;</div>
    </div>
    <div class="win-title">{title}</div>
    <div class="win-nav">
      <a href="/">Inicio</a>
      <a href="javascript:location.reload()">Recargar</a>
    </div>
  </div>
  <div class="win-content">
    <div id="moduleLoading" class="loading"><div class="spinner"></div><div>Cargando...</div></div>
    <div id="moduleContent" style="display:none">{body_html}</div>
  </div>
</div>
<script>
const LS='theme';
if(localStorage.getItem(LS)==='light')document.body.classList.add('light')
function closeWin(){{window.location.href='/'}}
function minWin(){{window.open('','_self','');window.close()}}
function maxWin(){{if(!document.fullscreenElement)document.documentElement.requestFullscreen();else document.exitFullscreen()}}
document.getElementById('moduleLoading').style.display='none'
document.getElementById('moduleContent').style.display='block'
function toast(msg,type){{const t=document.createElement('div');t.className='toast '+type;t.textContent=msg;document.body.appendChild(t);setTimeout(()=>t.remove(),3000)}}
async function api(url){{const r=await fetch(url);if(!r.ok)throw new Error(await r.text());return r.json()}}
{extra_js}
</script>
</body>
</html>"""

# ── Módulos ──────────────────────────────────────────────────────────────

MOD_VALUE_BETS = module_page("Value Bets", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Edge Promedio</div><div class="value gold" id="vbAvgEdge">0%</div></div>
  <div class="kpi"><div class="label">Value Bets Hoy</div><div class="value" id="vbCount">0</div></div>
  <div class="kpi"><div class="label">Mejor Edge</div><div class="value green" id="vbMaxEdge">0%</div></div>
</div>
<div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap">
  <select id="vbSport" style="padding:6px 12px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--text);font-size:12px">
    <option value="upcoming">Todos los deportes</option>
    <option value="soccer_mexico_ligamx">Liga MX</option>
    <option value="basketball_nba">NBA</option>
    <option value="soccer_epl">Premier League</option>
  </select>
  <input id="vbMinEdge" type="number" value="2" step="0.5" style="width:70px;padding:6px 10px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--text);font-size:12px" placeholder="Edge min"/> 
  <button class="top-btn" onclick="loadVB()" style="width:auto;padding:6px 16px">Buscar</button>
</div>
<table id="vbTable"><thead><tr><th>Partido</th><th>Resultado</th><th>Casa</th><th>Cuota</th><th>Edge</th></tr></thead><tbody id="vbBody"></tbody></table>
""", """
async function loadVB(){try{
  const s=document.getElementById('vbSport').value
  const e=document.getElementById('vbMinEdge').value
  const d=await api('/api/odds/value-bets?deporte='+s+'&edge_minimo='+e)
  const vb=d.value_bets||[]
  let h=''
  let sumEdge=0
  let maxEdge=0
  vb.forEach(v=>{
    h+='<tr><td>'+v.partido+'</td><td>'+v.resultado+'</td><td>'+v.casa+'</td><td>'+v.cuota+'</td><td class="gold">'+v.edge_porcentaje+'%</td></tr>'
    sumEdge+=parseFloat(v.edge_porcentaje)
    maxEdge=Math.max(maxEdge,parseFloat(v.edge_porcentaje))
  })
  document.getElementById('vbBody').innerHTML=h||'<tr><td colspan="5" style="text-align:center;color:var(--text3)">Sin value bets</td></tr>'
  document.getElementById('vbCount').textContent=vb.length
  document.getElementById('vbAvgEdge').textContent=(vb.length?(sumEdge/vb.length).toFixed(1):'0')+'%'
  document.getElementById('vbMaxEdge').textContent=maxEdge.toFixed(1)+'%'
}catch(e){toast('Error al cargar value bets','err')}}
loadVB()
""")

MOD_SHARP = module_page("Sharp Money", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Alertas Sharp</div><div class="value" id="sharpCount">0</div><div class="sub">&Uacute;ltimas 24h</div></div>
  <div class="kpi"><div class="label">CLV Promedio</div><div class="value gold" id="sharpClv">0</div></div>
</div>
<table id="sharpTable"><thead><tr><th>Partido</th><th>Movimiento</th><th>De</th><th>A</th><th>Urgencia</th></tr></thead><tbody id="sharpBody"></tbody></table>
""", """
async function loadSharp(){try{
  const d=await api('/api/odds/arbitraje?min_profit=0.1')
  const a=d.arbitrajes||[]
  document.getElementById('sharpCount').textContent=a.length
  let h=''
  a.forEach(v=>{
    const outcomes=Object.entries(v.stakes||{}).map(([k,o])=>k+': '+o.casa+' $'+o.cuota).join(' | ')
    h+='<tr><td>'+v.partido+'</td><td>'+v.tipo+'</td><td>'+outcomes+'</td><td>'+v.profit+'%</td><td>MEDIA</td></tr>'
  })
  document.getElementById('sharpBody').innerHTML=h||'<tr><td colspan="5" style="text-align:center;color:var(--text3)">Sin datos</td></tr>'
}catch(e){toast('Error','err')}}
loadSharp()
""")

MOD_ARBITRAJE = module_page("Arbitraje", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Arbitrajes</div><div class="value gold" id="arbCount">0</div></div>
  <div class="kpi"><div class="label">Max Profit</div><div class="value green" id="arbMaxProfit">0%</div></div>
</div>
<div style="margin-bottom:12px">
  <input id="arbMinProfit" type="number" value="0.5" step="0.1" style="width:80px;padding:6px 10px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--text);font-size:12px"/> 
  <button class="top-btn" onclick="loadArb()" style="width:auto;padding:6px 16px">Escaneary</button>
</div>
<table><thead><tr><th>Partido</th><th>Profit</th><th>Resultados</th></tr></thead><tbody id="arbBody"></tbody></table>
""", """
async function loadArb(){try{
  const m=document.getElementById('arbMinProfit').value
  const d=await api('/api/odds/arbitraje?min_profit='+m)
  const a=d.arbitrajes||[]
  document.getElementById('arbCount').textContent=a.length
  let maxP=0,h=''
  a.forEach(v=>{
    maxP=Math.max(maxP,parseFloat(v.profit||0))
    const r=Object.entries(v.stakes||{}).map(([k,o])=>k).join(', ')
    h+='<tr><td>'+v.partido+'</td><td class="green">'+v.profit+'%</td><td>'+r+'</td></tr>'
  })
  document.getElementById('arbMaxProfit').textContent=maxP.toFixed(2)+'%'
  document.getElementById('arbBody').innerHTML=h||'<tr><td colspan="3" style="text-align:center;color:var(--text3)">Sin arbitrajes</td></tr>'
}catch(e){toast('Error','err')}}
loadArb()
""")

MOD_ML = module_page("ML Predictivo", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Modelos</div><div class="value">MLP + GBM</div></div>
  <div class="kpi"><div class="label">Features</div><div class="value" id="mlFeat">0</div></div>
  <div class="kpi"><div class="label">Confianza Base</div><div class="value gold" id="mlConf">--</div></div>
</div>
<div style="display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap">
  <select id="mlLiga" style="padding:6px 12px;border-radius:6px;border:1px solid var(--border);background:var(--surface);color:var(--text);font-size:12px">
    <option value="liga_mx">Liga MX</option><option value="mls">MLS</option><option value="premier_league">Premier League</option>
    <option value="la_liga">La Liga</option><option value="serie_a">Serie A</option><option value="bundesliga">Bundesliga</option><option value="ligue_1">Ligue 1</option>
  </select>
  <button class="top-btn" onclick="trainML()" style="width:auto;padding:6px 16px">Entrenary</button>
  <button class="top-btn" onclick="loadML()" style="width:auto;padding:6px 16px">Actualizar</button>
</div>
<div id="mlStatus" style="margin-bottom:12px;font-size:12px;color:var(--text2)"></div>
<table><thead><tr><th>Feature</th><th>Importancia</th></tr></thead><tbody id="mlBody"></tbody></table>
""", """
async function loadML(){try{
  const l=document.getElementById('mlLiga').value
  const d=await api('/api/ml/v2/features?liga='+l)
  const f=d.features||[]
  document.getElementById('mlFeat').textContent=f.length
  document.getElementById('mlConf').textContent=f.length?'Con datos':'Sin datos'
  let h=''
  f.slice(0,15).forEach(v=>{
    h+='<tr><td>'+v.feature_name+'</td><td><div style="background:var(--bg4);border-radius:4px;overflow:hidden;width:120px"><div style="width:'+(v.importance*100)+'%;height:6px;background:var(--accent);border-radius:4px"></div></div> '+(v.importance*100).toFixed(1)+'%</td></tr>'
  })
  document.getElementById('mlBody').innerHTML=h||'<tr><td colspan="2" style="text-align:center;color:var(--text3)">Entrena modelos primero</td></tr>'
}catch(e){toast('Error','err')}}
async function trainML(){try{
  document.getElementById('mlStatus').textContent='Entrenando...'
  await api('/api/ml/v2/train')
  document.getElementById('mlStatus').textContent='Entrenamiento iniciado (fondo)'
  setTimeout(loadML,5e3)
}catch(e){toast('Error','err')}}
loadML()
""")

MOD_BANKROLL = module_page("Bankroll", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Bankroll Actual</div><div class="value" id="brActual">$0</div></div>
  <div class="kpi"><div class="label">Apuestas</div><div class="value gold" id="brTotal">0</div></div>
  <div class="kpi"><div class="label">Win Rate</div><div class="value green" id="brWinRate">0%</div></div>
  <div class="kpi"><div class="label">Ganancia Neta</div><div class="value" id="brGanancia">$0</div></div>
</div>
<div class="chart-container"><canvas id="brChart"></canvas></div>
<table><thead><tr><th>Fecha</th><th>Evento</th><th>Bankroll</th></tr></thead><tbody id="brBody"></tbody></table>
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
    hh+='<tr><td>'+(v.fecha||'').slice(0,10)+'</td><td>'+v.evento+'</td><td>$'+v.bankroll+'</td></tr>'
  })
  document.getElementById('brBody').innerHTML=hh||'<tr><td colspan="3" style="text-align:center;color:var(--text3)">Sin historial</td></tr>'
  if(brChart)brChart.destroy()
  brChart=new Chart(document.getElementById('brChart'),{type:'line',data:{labels:h.map(v=>(v.fecha||'').slice(5,10)),datasets:[{label:'Bankroll',data:h.map(v=>v.bankroll),borderColor:'#6c5ce7',backgroundColor:'rgba(108,92,231,.1)',fill:true,tension:.3,pointRadius:2}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:{color:'var(--border)'},ticks:{color:'var(--text3)'}},y:{grid:{color:'var(--border)'},ticks:{color:'var(--text3)'}}}}})
}catch(e){toast('Error','err')}}
loadBR()
""")

MOD_SIMULACION = module_page("Simulación", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Trades Simulados</div><div class="value" id="simTotal">0</div></div>
  <div class="kpi"><div class="label">Ganadas</div><div class="value green" id="simGanadas">0</div></div>
  <div class="kpi"><div class="label">Perdidas</div><div class="value red" id="simPerdidas">0</div></div>
  <div class="kpi"><div class="label">PnL Total</div><div class="value gold" id="simPnl">$0</div></div>
</div>
<table><thead><tr><th>Partido</th><th>Selección</th><th>Cuota</th><th>Edge</th><th>Resultado</th><th>PnL</th></tr></thead><tbody id="simBody"></tbody></table>
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
    const cls=v.resultado_simulado==='ganada'?'green':v.resultado_simulado==='perdida'?'red':'gold'
    h+='<tr><td>'+v.partido+'</td><td>'+v.seleccion+'</td><td>'+v.cuota+'</td><td>'+(v.edge_pct||0)+'%</td><td class="'+cls+'">'+v.resultado_simulado+'</td><td>$'+(v.pnl_real||0)+'</td></tr>'
  })
  document.getElementById('simBody').innerHTML=h||'<tr><td colspan="6" style="text-align:center;color:var(--text3)">Sin trades</td></tr>'
}catch(e){toast('Error','err')}}
loadSim()
""")

MOD_CONTABILIDAD = module_page("Contabilidad", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Transacciones</div><div class="value" id="conCount">0</div></div>
  <div class="kpi"><div class="label">Ganadas</div><div class="value green" id="conGanadas">0</div></div>
  <div class="kpi"><div class="label">Perdidas</div><div class="value red" id="conPerdidas">0</div></div>
  <div class="kpi"><div class="label">Neto</div><div class="value gold" id="conNeto">$0</div></div>
</div>
<div class="chart-container"><canvas id="conChart"></canvas></div>
<table><thead><tr><th>Estrategia</th><th>Total</th><th>Ganadas</th><th>Perdidas</th><th>Neto</th></tr></thead><tbody id="conBody"></tbody></table>
""", """
async function loadCon(){try{
  const d=await api('/api/contabilidad/pnl-estrategia')
  document.getElementById('conCount').textContent=d.reduce((s,v)=>s+(v.total||0),0)
  let g=0,p=0,n=0,h=''
  d.forEach(v=>{
    g+=v.ganadas||0;p+=v.perdidas||0;n+=v.neto||0
    h+='<tr><td>'+v.estrategia+'</td><td>'+v.total+'</td><td class="green">'+v.ganadas+'</td><td class="red">'+v.perdidas+'</td><td class="'+(v.neto>=0?'green':'red')+'">$'+(v.neto||0)+'</td></tr>'
  })
  document.getElementById('conGanadas').textContent=g
  document.getElementById('conPerdidas').textContent=p
  document.getElementById('conNeto').textContent='$'+n
  document.getElementById('conBody').innerHTML=h||'<tr><td colspan="5" style="text-align:center;color:var(--text3)">Sin datos</td></tr>'
}catch(e){toast('Error','err')}}
loadCon()
""")

MOD_JOURNAL = module_page("Trading Journal", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Acciones (7d)</div><div class="value" id="jrTotal">0</div></div>
  <div class="kpi"><div class="label">Tipos</div><div class="value" id="jrTipos">0</div></div>
</div>
<div style="margin-bottom:12px">
  <button class="top-btn" onclick="exportCSV()" style="width:auto;padding:6px 16px">Exportar CSV</button>
  <button class="top-btn" onclick="loadJR()" style="width:auto;padding:6px 16px">Actualizar</button>
</div>
<table><thead><tr><th>Fecha</th><th>Acción</th><th>Partido</th><th>Detalle</th></tr></thead><tbody id="jrBody"></tbody></table>
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
  document.getElementById('jrBody').innerHTML=h||'<tr><td colspan="4" style="text-align:center;color:var(--text3)">Sin actividad</td></tr>'
}catch(e){toast('Error','err')}}
function exportCSV(){window.open('/api/journal/export-csv','_blank')}
loadJR()
""")

MOD_BOOKMAKERS = module_page("Rating Casas", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Casas Evaluadas</div><div class="value" id="bmCount">0</div></div>
  <div class="kpi"><div class="label">Mejor Overround</div><div class="value green" id="bmBestOver">0</div></div>
</div>
<button class="top-btn" onclick="scanBM()" style="width:auto;padding:6px 16px;margin-bottom:12px">Escanear Casas</button>
<div id="bmStatus" style="font-size:12px;color:var(--text2);margin-bottom:8px"></div>
<table><thead><tr><th>Casa</th><th>Overround</th><th>CLV</th><th>Apariciones</th></tr></thead><tbody id="bmBody"></tbody></table>
""", """
async function loadBM(){try{
  const d=await api('/api/bookmakers/rating')
  const r=d.ratings||[]
  document.getElementById('bmCount').textContent=r.length
  document.getElementById('bmBestOver').textContent=r.length?Math.min(...r.map(v=>v.avg_overround||99)).toFixed(2)+'%':'0'
  let h=''
  r.sort((a,b)=>(a.avg_overround||99)-(b.avg_overround||99)).forEach(v=>{
    h+='<tr><td>'+v.bookmaker+'</td><td>'+(v.avg_overround||0).toFixed(2)+'%</td><td>'+(v.avg_clv||0).toFixed(4)+'</td><td>'+v.apariciones+'</td></tr>'
  })
  document.getElementById('bmBody').innerHTML=h||'<tr><td colspan="4" style="text-align:center;color:var(--text3)">Escanea casas primero</td></tr>'
}catch(e){toast('Error','err')}}
async function scanBM(){try{
  document.getElementById('bmStatus').textContent='Escaneando...'
  await api('/api/bookmakers/scan')
  document.getElementById('bmStatus').textContent='Escaneo completado'
  loadBM()
}catch(e){document.getElementById('bmStatus').textContent='Error';toast('Error','err')}}
loadBM()
""")

MOD_CROSS = module_page("Cross Market", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Oportunidades</div><div class="value gold" id="cmCount">0</div></div>
  <div class="kpi"><div class="label">Mercados</div><div class="value">H2H vs AH</div></div>
</div>
<button class="top-btn" onclick="loadCM()" style="width:auto;padding:6px 16px;margin-bottom:12px">Analizar</button>
<table><thead><tr><th>Partido</th><th>H2H</th><th>AH</th><th>Diferencia</th></tr></thead><tbody id="cmBody"></tbody></table>
""", """
async function loadCM(){try{
  const d=await api('/api/odds/arbitraje?min_profit=0.1')
  const a=d.arbitrajes||[]
  document.getElementById('cmCount').textContent=a.length
  let h=''
  a.slice(0,20).forEach(v=>{
    h+='<tr><td>'+v.partido+'</td><td>'+(v.tipo||'H2H')+'</td><td>'+v.profit+'%</td><td class="green">'+v.profit+'%</td></tr>'
  })
  document.getElementById('cmBody').innerHTML=h||'<tr><td colspan="4" style="text-align:center;color:var(--text3)">Sin datos</td></tr>'
}catch(e){toast('Error','err')}}
loadCM()
""")

MOD_BACKTESTING = module_page("Backtesting", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Resultados</div><div class="value" id="btTotal">0</div></div>
  <div class="kpi"><div class="label">Accuracy</div><div class="value gold" id="btAcc">0%</div></div>
</div>
<button class="top-btn" onclick="loadBT()" style="width:auto;padding:6px 16px;margin-bottom:12px">Actualizar</button>
<table><thead><tr><th>Config</th><th>Tipo</th><th>Resumen</th></tr></thead><tbody id="btBody"></tbody></table>
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
<div class="kpi-grid">
  <div class="kpi"><div class="label">Total Apuestas</div><div class="value" id="rpTotal">0</div></div>
  <div class="kpi"><div class="label">Win Rate</div><div class="value gold" id="rpWinRate">0%</div></div>
  <div class="kpi"><div class="label">Sharpe</div><div class="value" id="rpSharpe">0</div></div>
  <div class="kpi"><div class="label">ROI</div><div class="value green" id="rpRoi">0%</div></div>
</div>
<div class="chart-container"><canvas id="rpChart"></canvas></div>
<table><thead><tr><th>Deporte</th><th>Total</th><th>Ganadas</th><th>Perdidas</th><th>Neto</th></tr></thead><tbody id="rpBody"></tbody></table>
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
    ht+='<tr><td>'+v.liga+'</td><td>'+v.total+'</td><td class="green">'+v.ganadas+'</td><td class="red">'+v.perdidas+'</td><td class="'+(net>=0?'green':'red')+'">$'+net+'</td></tr>'
  })
  document.getElementById('rpBody').innerHTML=ht||'<tr><td colspan="5" style="text-align:center;color:var(--text3)">Sin datos</td></tr>'
  if(rpChart)rpChart.destroy()
  rpChart=new Chart(document.getElementById('rpChart'),{type:'bar',data:{labels:p.map(v=>v.liga||'?'),datasets:[{label:'Ganancia',data:p.map(v=>v.ganancia_neta||0),backgroundColor:p.map(v=>(v.ganancia_neta||0)>=0?'rgba(0,206,201,.7)':'rgba(255,118,117,.7)'),borderRadius:4}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:{display:false},ticks:{color:'var(--text3)'}},y:{grid:{color:'var(--border)'},ticks:{color:'var(--text3)'}}}}})
}catch(e){toast('Error','err')}}
loadRP()
""")

# ── Mapa de módulos ──────────────────────────────────────────────────────
MODULES = {
    "value-bets":    ("Value Bets",      MOD_VALUE_BETS),
    "sharp":         ("Sharp Money",     MOD_SHARP),
    "arbitraje":     ("Arbitraje",       MOD_ARBITRAJE),
    "ml":            ("ML Predictivo",   MOD_ML),
    "bankroll":      ("Bankroll",        MOD_BANKROLL),
    "simulacion":    ("Simulación",      MOD_SIMULACION),
    "contabilidad":  ("Contabilidad",    MOD_CONTABILIDAD),
    "journal":       ("Trading Journal", MOD_JOURNAL),
    "bookmakers":    ("Rating Casas",    MOD_BOOKMAKERS),
    "cross-market":  ("Cross Market",    MOD_CROSS),
    "backtesting":   ("Backtesting",     MOD_BACKTESTING),
    "rendimiento":   ("Rendimiento",     MOD_RENDIMIENTO),
}

# ── Main export ──────────────────────────────────────────────────────────
# Por compatibilidad, HTML es la landing page
HTML = LANDING_HTML
