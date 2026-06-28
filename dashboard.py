"""
Dashboard — Professional Clean Style.
Landing page + 12 analysis modules with empty states.
"""
import json

# ── CSS — Clean Professional Theme ──────────────────────────────────────────
SHARED_CSS = r"""
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#f8f9fc;--bg2:#ffffff;--bg3:#f1f3f7;--bg4:#e8ecf1;
  --surface:#ffffff;--surface-hover:#f4f5f9;
  --border:#e2e5ec;--border-hover:#cdd1da;
  --text:#1a1d2e;--text2:#5a5e72;--text3:#9a9eb0;
  --primary:#4f46e5;--primary-bg:rgba(79,70,229,0.06);--primary-hover:#4338ca;
  --green:#059669;--green-bg:rgba(5,150,105,0.06);
  --red:#dc2626;--red-bg:rgba(220,38,38,0.06);
  --amber:#d97706;--amber-bg:rgba(217,119,6,0.06);
  --blue:#2563eb;--blue-bg:rgba(37,99,235,0.06);
  --shadow:0 1px 3px rgba(0,0,0,0.06),0 1px 2px rgba(0,0,0,0.04);
  --shadow-md:0 4px 6px rgba(0,0,0,0.05),0 2px 4px rgba(0,0,0,0.03);
  --radius:10px;--radius-sm:6px;--radius-lg:14px
}
.dark{--bg:#0f1117;--bg2:#1a1d2e;--bg3:#232738;--bg4:#2c3044;
  --surface:#1a1d2e;--surface-hover:#232738;
  --border:#2c3044;--border-hover:#3d4259;
  --text:#e4e6ed;--text2:#8b8fa3;--text3:#535766;
  --primary:#6366f1;--primary-bg:rgba(99,102,241,0.1);--primary-hover:#818cf8;
  --green:#34d399;--green-bg:rgba(52,211,153,0.1);
  --red:#f87171;--red-bg:rgba(248,113,113,0.1);
  --amber:#fbbf24;--amber-bg:rgba(251,191,36,0.1);
  --blue:#60a5fa;--blue-bg:rgba(96,165,250,0.1);
  --shadow:0 1px 3px rgba(0,0,0,0.2);--shadow-md:0 4px 6px rgba(0,0,0,0.25)
}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:'Inter',system-ui,-apple-system,sans-serif;font-size:13px;-webkit-font-smoothing:antialiased;line-height:1.5}
a{color:var(--primary);text-decoration:none}

/* NAV */
.nav{display:flex;align-items:center;height:52px;padding:0 24px;background:var(--bg2);border-bottom:1px solid var(--border);gap:16px}
.nav .brand{font-size:15px;font-weight:700;color:var(--text);letter-spacing:-.3px}
.nav .brand span{color:var(--primary)}
.nav .links{display:flex;gap:2px;margin-left:24px}
.nav .links a{padding:6px 12px;border-radius:var(--radius-sm);font-size:12px;font-weight:500;color:var(--text2);transition:.15s}
.nav .links a:hover{color:var(--text);background:var(--surface-hover)}
.nav .right{margin-left:auto;display:flex;align-items:center;gap:12px}
.nav .dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 6px var(--green)}
.nav .dot.off{background:var(--red);box-shadow:0 0 6px var(--red)}
.nav .mode{font-size:11px;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:.5px}
.nav .btn-icon{width:32px;height:32px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--surface);color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:13px;transition:.15s}
.nav .btn-icon:hover{background:var(--surface-hover);color:var(--text);border-color:var(--border-hover)}

/* CONTENT */
.content{max-width:1200px;margin:0 auto;padding:24px}

/* KPI CARDS */
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:24px}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px 18px;transition:.15s}
.kpi:hover{border-color:var(--border-hover);box-shadow:var(--shadow)}
.kpi .label{font-size:11px;font-weight:500;color:var(--text3);margin-bottom:4px;text-transform:uppercase;letter-spacing:.3px}
.kpi .value{font-size:24px;font-weight:700;letter-spacing:-.5px;line-height:1.2}
.kpi .value.green{color:var(--green)}.kpi .value.red{color:var(--red)}.kpi .value.amber{color:var(--amber)}.kpi .value.blue{color:var(--blue)}
.kpi .sub{font-size:11px;color:var(--text3);margin-top:3px}

/* SECTION */
.section{margin-bottom:24px}
.section-header{display:flex;align-items:center;margin-bottom:12px;gap:12px}
.section-header h2{font-size:14px;font-weight:600;color:var(--text);margin:0}
.section-header .count{font-size:11px;color:var(--text3);background:var(--bg3);padding:2px 8px;border-radius:10px}
.section-header .line{flex:1;height:1px;background:var(--border)}

/* MODULE GRID */
.mod-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}
.mod{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px 16px;cursor:pointer;transition:.2s;position:relative;overflow:hidden}
.mod:hover{border-color:var(--primary);box-shadow:var(--shadow-md);transform:translateY(-1px)}
.mod::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--primary);opacity:0;transition:.2s}
.mod:hover::before{opacity:1}
.mod .icon{width:36px;height:36px;border-radius:var(--radius-sm);display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:700;margin-bottom:10px;color:var(--primary);background:var(--primary-bg)}
.mod .name{font-size:13px;font-weight:600;color:var(--text);margin-bottom:3px}
.mod .desc{font-size:11px;color:var(--text2);line-height:1.4}
.mod .tag{position:absolute;top:12px;right:12px;font-size:9px;font-weight:600;color:var(--primary);background:var(--primary-bg);padding:2px 6px;border-radius:4px;text-transform:uppercase;letter-spacing:.3px}

/* EMPTY STATE */
.empty{background:var(--surface);border:1px dashed var(--border);border-radius:var(--radius);padding:32px;text-align:center;margin-bottom:16px}
.empty .icon{font-size:32px;margin-bottom:8px;color:var(--text3)}
.empty h3{font-size:14px;font-weight:600;color:var(--text);margin-bottom:4px}
.empty p{font-size:12px;color:var(--text2);margin-bottom:12px;max-width:400px;margin-left:auto;margin-right:auto}
.empty .btn{display:inline-flex;align-items:center;gap:6px;padding:8px 20px;border-radius:var(--radius-sm);border:none;font-size:12px;font-weight:600;cursor:pointer;transition:.15s;font-family:'Inter',sans-serif}
.empty .btn-primary{background:var(--primary);color:#fff}.empty .btn-primary:hover{background:var(--primary-hover)}
.empty .btn-outline{background:transparent;border:1px solid var(--border);color:var(--text2)}.empty .btn-outline:hover{background:var(--surface-hover);border-color:var(--border-hover)}

/* TABLE */
.table-wrap{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden}
table{width:100%;border-collapse:collapse;font-size:12px}
th{padding:10px 14px;text-align:left;font-size:10px;font-weight:600;color:var(--text3);text-transform:uppercase;letter-spacing:.4px;background:var(--bg3);border-bottom:1px solid var(--border)}
td{padding:10px 14px;color:var(--text2);border-bottom:1px solid var(--border)}
tr:last-child td{border:0}
tr:hover td{background:var(--surface-hover)}
td.num{font-variant-numeric:tabular-nums;text-align:right}

/* BUTTONS */
.top-bar{display:flex;align-items:center;gap:8px;margin-bottom:14px;flex-wrap:wrap}
.btn{padding:7px 16px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--surface);color:var(--text2);font-size:12px;font-weight:500;cursor:pointer;transition:.15s;font-family:'Inter',sans-serif}
.btn:hover{background:var(--surface-hover);color:var(--text);border-color:var(--border-hover)}
.btn-primary{background:var(--primary);color:#fff;border-color:var(--primary)}.btn-primary:hover{background:var(--primary-hover)}
select,input[type=number]{padding:6px 12px;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--surface);color:var(--text);font-size:12px;font-family:'Inter',sans-serif}
select:focus,input:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px var(--primary-bg)}

/* LOADING */
.loading{text-align:center;padding:40px;color:var(--text2)}
.spinner{width:20px;height:20px;border:2px solid var(--border);border-top-color:var(--primary);border-radius:50%;animation:spin .6s linear infinite;margin:0 auto 8px}
@keyframes spin{to{transform:rotate(360deg)}}

/* TOAST */
.toast{position:fixed;bottom:16px;right:16px;padding:10px 16px;border-radius:var(--radius-sm);background:var(--bg2);border:1px solid var(--border);color:var(--text);font-size:12px;z-index:9999;box-shadow:var(--shadow-md);animation:slideUp .2s ease;max-width:320px}
.toast.ok{border-color:var(--green)}.toast.err{border-color:var(--red)}.toast.info{border-color:var(--primary)}
@keyframes slideUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

/* CHART */
.chart-box{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:12px}
.chart-box canvas{width:100%!important;max-height:240px}
"""

# ── Landing Page ─────────────────────────────────────────────────────────
LANDING_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ApuestasPro</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<style>""" + SHARED_CSS + r"""
.hero{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:24px;padding-bottom:20px;border-bottom:1px solid var(--border)}
.hero h1{font-size:22px;font-weight:700;margin:0 0 4px;letter-spacing:-.3px}
.hero h1 span{color:var(--primary)}
.hero p{font-size:13px;color:var(--text2);margin:0}
.hero .meta{text-align:right}
.hero .meta .label{font-size:10px;color:var(--text3);text-transform:uppercase;letter-spacing:.5px}
.hero .meta .val{font-size:13px;font-weight:600;color:var(--text)}
.hero .meta .ver{font-size:11px;color:var(--text3)}
</style>
</head>
<body>
<div class="nav">
  <div class="brand">Apuestas<span>Pro</span></div>
  <div class="links">
    <a href="/panel/value-bets">Value Bets</a>
    <a href="/panel/sharp">Sharp Money</a>
    <a href="/panel/arbitraje">Arbitraje</a>
    <a href="/panel/ml">ML Predictivo</a>
    <a href="/panel/bankroll">Bankroll</a>
    <a href="/panel/rendimiento">Rendimiento</a>
  </div>
  <div class="right">
    <span class="dot off" id="sd"></span>
    <span class="mode" id="modeLabel">OFFLINE</span>
    <button class="btn-icon" onclick="location='/logout'" title="Salir">&#8592;</button>
  </div>
</div>

<div class="content">
  <div class="hero">
    <div>
      <h1>Sistema de <span>Analisis</span> Deportivo</h1>
      <p>ML Predictivo &middot; Sharp Money &middot; Arbitraje &middot; Value Bets &middot; Bankroll &middot; Simulacion</p>
    </div>
    <div class="meta">
      <div class="label">Ultima actualizacion</div>
      <div class="val" id="lastUpd">--</div>
      <div class="ver">v4.4</div>
    </div>
  </div>

  <div class="kpi-grid" id="kpiGrid">
    <div class="kpi"><div class="label">Bankroll</div><div class="value" id="kpiBr">$0</div><div class="sub">Valor actual</div></div>
    <div class="kpi"><div class="label">Win Rate</div><div class="value" id="kpiWr">0%</div><div class="sub">Ultimos 30 dias</div></div>
    <div class="kpi"><div class="label">ROI</div><div class="value" id="kpiRoi">0%</div><div class="sub">Retorno total</div></div>
    <div class="kpi"><div class="label">Sharpe Ratio</div><div class="value" id="kpiSh">0.00</div><div class="sub">Riesgo ajustado</div></div>
    <div class="kpi"><div class="label">PnL Neto</div><div class="value" id="kpiPnl">$0</div><div class="sub">30 dias</div></div>
    <div class="kpi"><div class="label">Value Bets</div><div class="value" id="kpiVb">0</div><div class="sub">Edge: <span id="kpiEdge">0%</span></div></div>
  </div>

  <div id="seedBanner" class="empty" style="display:none">
    <div class="icon">&#9888;</div>
    <h3>Base de datos vacia</h3>
    <p>Pobla la base con datos iniciales para comenzar a usar el sistema.</p>
    <button class="btn btn-primary" onclick="seedDB()" id="seedBtn">Seed Database</button>
    <div id="seedResult" style="font-size:11px;margin-top:8px;color:var(--text2)"></div>
  </div>

  <div class="section">
    <div class="section-header">
      <h2>Modulos de Analisis</h2>
      <span class="count">12</span>
      <div class="line"></div>
    </div>
    <div class="mod-grid">
      <div class="mod" onclick="location='/panel/value-bets'"><span class="tag">EDGE</span><div class="icon">V</div><div class="name">Value Bets</div><div class="desc">Deteccion de edge positivo en cuotas</div></div>
      <div class="mod" onclick="location='/panel/sharp'"><span class="tag">LIVE</span><div class="icon">S</div><div class="name">Sharp Money</div><div class="desc">Movimiento de lineas y alertas</div></div>
      <div class="mod" onclick="location='/panel/arbitraje'"><span class="tag">ARB</span><div class="icon">A</div><div class="name">Arbitraje</div><div class="desc">Surebets multi-mercado</div></div>
      <div class="mod" onclick="location='/panel/ml'"><span class="tag">ML</span><div class="icon">M</div><div class="name">ML Predictivo</div><div class="desc">MLP + GBM ensemble</div></div>
      <div class="mod" onclick="location='/panel/bankroll'"><span class="tag">KELLY</span><div class="icon">B</div><div class="name">Bankroll</div><div class="desc">Kelly, historial, riesgo</div></div>
      <div class="mod" onclick="location='/panel/simulacion'"><span class="tag">SIM</span><div class="icon">~</div><div class="name">Simulacion</div><div class="desc">Trades simulados</div></div>
      <div class="mod" onclick="location='/panel/contabilidad'"><span class="tag">P&L</span><div class="icon">C</div><div class="name">Contabilidad</div><div class="desc">P&L y reportes</div></div>
      <div class="mod" onclick="location='/panel/journal'"><span class="tag">LOG</span><div class="icon">J</div><div class="name">Trading Journal</div><div class="desc">Bitacora y export CSV</div></div>
      <div class="mod" onclick="location='/panel/bookmakers'"><span class="tag">RANK</span><div class="icon">R</div><div class="name">Rating Casas</div><div class="desc">Overround y CLV</div></div>
      <div class="mod" onclick="location='/panel/cross-market'"><span class="tag">X</span><div class="icon">X</div><div class="name">Cross Market</div><div class="desc">H2H vs AH comparativa</div></div>
      <div class="mod" onclick="location='/panel/backtesting'"><span class="tag">BT</span><div class="icon">T</div><div class="name">Backtesting</div><div class="desc">Historico y estrategias</div></div>
      <div class="mod" onclick="location='/panel/rendimiento'"><span class="tag">STATS</span><div class="icon">G</div><div class="name">Rendimiento</div><div class="desc">Graficas y estadisticas</div></div>
    </div>
  </div>
  <div style="height:40px"></div>
</div>

<script>
function clock(){document.getElementById('lastUpd').textContent=new Date().toLocaleString('es-MX')}
clock();setInterval(clock,3e4)
function theme(){document.documentElement.classList.toggle('dark');localStorage.setItem('ap_theme',document.documentElement.classList.contains('dark')?'dark':'light')}
if(localStorage.getItem('ap_theme')==='dark')document.documentElement.classList.add('dark')
else if(!localStorage.getItem('ap_theme'))document.documentElement.classList.add('dark')
async function seedDB(){try{
  var btn=document.getElementById('seedBtn'),res=document.getElementById('seedResult')
  btn.disabled=true;btn.textContent='Sembrando...';res.textContent=''
  var r=await fetch('/api/seed-demo')
  if(!r.ok)throw new Error(await r.text())
  var d=await r.json()
  if(d.status==='ok'||d.total_insertados>0){
    res.textContent=d.total_insertados+' registros insertados';res.style.color='var(--green)'
    btn.textContent='Listo';setTimeout(function(){document.getElementById('seedBanner').style.display='none';loadKPI()},2e3)
  }else{
    res.textContent='Error: '+(d.errores||[]).slice(0,3).join(', ');res.style.color='var(--red)'
    btn.disabled=false;btn.textContent='Reintentar'
  }
}catch(e){
  document.getElementById('seedResult').textContent='Error: '+e.message
  document.getElementById('seedResult').style.color='var(--red)'
  document.getElementById('seedBtn').disabled=false;document.getElementById('seedBtn').textContent='Reintentar'
}}
async function loadKPI(){try{
  var r=await fetch('/api/kpi-summary')
  if(!r.ok)return
  var d=await r.json(),g=d.general||{},b=d.bankroll||{},h=d.hoy||{}
  function n(v){return parseFloat(v)||0}
  var br=n(b.actual)
  document.getElementById('kpiBr').textContent='$'+br.toLocaleString()
  if(br===0)document.getElementById('seedBanner').style.display='block'
  var wr=g.win_rate||0
  document.getElementById('kpiWr').textContent=wr+'%'
  document.getElementById('kpiWr').className='value '+(wr>=50?'green':'red')
  var roi=g.roi_pct||0
  document.getElementById('kpiRoi').textContent=roi+'%'
  document.getElementById('kpiRoi').className='value '+(roi>=0?'green':'red')
  document.getElementById('kpiSh').textContent=(g.sharpe_ratio||0).toFixed(2)
  var pnl=g.ganancia_neta||0
  document.getElementById('kpiPnl').textContent='$'+n(pnl).toLocaleString()
  document.getElementById('kpiPnl').className='value '+(pnl>=0?'green':'red')
  var vb=h.value_bets||{}
  document.getElementById('kpiVb').textContent=vb.total||0
  document.getElementById('kpiEdge').textContent=(vb.avg_edge||0).toFixed(1)+'%'
  document.getElementById('sd').className='dot'
  document.getElementById('modeLabel').textContent='ONLINE'
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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
<style>{SHARED_CSS}</style>
</head>
<body>
<div class="nav">
  <div class="brand" style="cursor:pointer" onclick="location='/'">Apuestas<span>Pro</span></div>
  <div class="links">
    <a href="/">Home</a>
    <a href="javascript:location.reload()">Reload</a>
  </div>
  <div class="right">
    <span style="font-size:12px;font-weight:600;color:var(--text2)">{title}</span>
    <button class="btn-icon" onclick="location='/'" title="Home">&#8592;</button>
  </div>
</div>
<div class="content">
  <div id="modLoading" class="loading"><div class="spinner"></div><div>Loading...</div></div>
  <div id="modContent" style="display:none">{body_html}</div>
</div>
<script>
if(!localStorage.getItem('ap_theme'))document.documentElement.classList.add('dark')
else if(localStorage.getItem('ap_theme')==='dark')document.documentElement.classList.add('dark')
document.getElementById('modLoading').style.display='none'
document.getElementById('modContent').style.display='block'
function toast(msg,type){{const t=document.createElement('div');t.className='toast '+type;t.textContent=msg;document.body.appendChild(t);setTimeout(()=>t.remove(),3e3)}}
async function api(url){{const r=await fetch(url);if(!r.ok)throw new Error(await r.text());return r.json()}}
{extra_js}
</script>
</body>
</html>"""

# ── Empty state helper ───────────────────────────────────────────────────
def _empty_state(icon, title, desc, btn_text="Seed Database", btn_action="seedModule()"):
    return f"""<div class="empty">
  <div class="icon">{icon}</div>
  <h3>{title}</h3>
  <p>{desc}</p>
  <button class="btn btn-primary" onclick="{btn_action}">{btn_text}</button>
  <div id="moduleSeedResult" style="font-size:11px;margin-top:8px;color:var(--text2)"></div>
</div>
<script>
async function seedModule(){{try{{var btn=document.querySelector('.empty .btn'),res=document.getElementById('moduleSeedResult');btn.disabled=true;btn.textContent='Working...';res.textContent='';var r=await fetch('/api/seed-demo');if(!r.ok)throw new Error(await r.text());var d=await r.json();if(d.status==='ok'||d.total_insertados>0){{res.textContent=d.total_insertados+' records inserted';res.style.color='var(--green)';btn.textContent='Done';setTimeout(()=>location.reload(),1500)}}else{{res.textContent='Error';res.style.color='var(--red)';btn.disabled=false;btn.textContent='Retry'}}}}catch(e){{document.getElementById('moduleSeedResult').textContent='Error: '+e.message;document.getElementById('moduleSeedResult').style.color='var(--red)';document.querySelector('.empty .btn').disabled=false;document.querySelector('.empty .btn').textContent='Retry'}}}}
</script>"""

# ── MODULES ────────────────────────────────────────────────────────────────

MOD_VALUE_BETS = module_page("Value Bets", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Edge Promedio</div><div class="value amber" id="vbAvgEdge">0%</div></div>
  <div class="kpi"><div class="label">Value Bets</div><div class="value" id="vbCount">0</div></div>
  <div class="kpi"><div class="label">Mejor Edge</div><div class="value green" id="vbMaxEdge">0%</div></div>
</div>
<div class="top-bar">
  <select id="vbSport"><option value="upcoming">Todos</option><option value="soccer_mexico_ligamx">Liga MX</option><option value="basketball_nba">NBA</option><option value="soccer_epl">Premier League</option></select>
  <input id="vbMinEdge" type="number" value="2" step="0.5" style="width:70px" placeholder="Edge min"/>
  <button class="btn btn-primary" onclick="loadVB()">Buscar</button>
</div>
<div class="table-wrap"><table><thead><tr><th>Partido</th><th>Resultado</th><th>Casa</th><th>Cuota</th><th>Edge</th></tr></thead><tbody id="vbBody"></tbody></table></div>
""", """
async function loadVB(){try{
  const s=document.getElementById('vbSport').value
  const e=document.getElementById('vbMinEdge').value
  const d=await api('/api/odds/value-bets?deporte='+s+'&edge_minimo='+e)
  const vb=d.value_bets||[]
  let h='',sumE=0,maxE=0
  vb.forEach(v=>{
    h+='<tr><td>'+v.partido+'</td><td>'+v.resultado+'</td><td>'+v.casa+'</td><td class="num">'+v.cuota+'</td><td class="num" style="color:var(--amber);font-weight:600">'+v.edge_porcentaje+'%</td></tr>'
    sumE+=parseFloat(v.edge_porcentaje);maxE=Math.max(maxE,parseFloat(v.edge_porcentaje))
  })
  document.getElementById('vbBody').innerHTML=h||'<tr><td colspan="5" style="text-align:center;color:var(--text3);padding:20px">Sin value bets. Configura ODDS_API_KEY para datos reales.</td></tr>'
  document.getElementById('vbCount').textContent=vb.length
  document.getElementById('vbAvgEdge').textContent=(vb.length?(sumE/vb.length).toFixed(1):'0')+'%'
  document.getElementById('vbMaxEdge').textContent=maxE.toFixed(1)+'%'
}catch(e){toast('Error al cargar value bets','err')}}
loadVB()
""")

MOD_SHARP = module_page("Sharp Money", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Alertas Sharp</div><div class="value" id="sharpCount">0</div><div class="sub">Ultimas 24h</div></div>
  <div class="kpi"><div class="label">CLV Promedio</div><div class="value amber" id="sharpClv">0</div></div>
</div>
<div class="table-wrap"><table><thead><tr><th>Partido</th><th>Movimiento</th><th>De</th><th>A</th><th>Urgencia</th></tr></thead><tbody id="sharpBody"></tbody></table></div>
""", """
async function loadSharp(){try{
  const d=await api('/api/odds/arbitraje?min_profit=0.1')
  const a=d.arbitrajes||[]
  document.getElementById('sharpCount').textContent=a.length
  let h=''
  a.forEach(v=>{
    h+='<tr><td>'+v.partido+'</td><td>'+v.profit_pct+'%</td><td>'+v.n_bookmakers+'</td><td>'+v.profit_pct+'%</td><td>MEDIA</td></tr>'
  })
  document.getElementById('sharpBody').innerHTML=h||'<tr><td colspan="5" style="text-align:center;color:var(--text3);padding:20px">Sin senales sharp. Configura ODDS_API_KEY.</td></tr>'
}catch(e){toast('Error','err')}}
loadSharp()
""")

MOD_ARBITRAJE = module_page("Arbitraje", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Arbitrajes</div><div class="value amber" id="arbCount">0</div></div>
  <div class="kpi"><div class="label">Max Profit</div><div class="value green" id="arbMaxProfit">0%</div></div>
</div>
<div class="top-bar">
  <input id="arbMinProfit" type="number" value="0.5" step="0.1" style="width:70px"/>
  <button class="btn btn-primary" onclick="loadArb()">Escanear</button>
</div>
<div class="table-wrap"><table><thead><tr><th>Partido</th><th>Profit</th><th>Resultados</th></tr></thead><tbody id="arbBody"></tbody></table></div>
""", """
async function loadArb(){try{
  const m=document.getElementById('arbMinProfit').value
  const d=await api('/api/odds/arbitraje?min_profit='+m)
  const a=d.arbitrajes||[]
  document.getElementById('arbCount').textContent=a.length
  let maxP=0,h=''
  a.forEach(v=>{
    maxP=Math.max(maxP,parseFloat(v.profit_pct||0))
    h+='<tr><td>'+v.partido+'</td><td class="num" style="color:var(--green);font-weight:600">'+v.profit_pct+'%</td><td>'+v.n_resultados+'</td></tr>'
  })
  document.getElementById('arbMaxProfit').textContent=maxP.toFixed(2)+'%'
  document.getElementById('arbBody').innerHTML=h||'<tr><td colspan="3" style="text-align:center;color:var(--text3);padding:20px">Sin arbitrajes. Configura ODDS_API_KEY.</td></tr>'
}catch(e){toast('Error','err')}}
loadArb()
""")

MOD_ML = module_page("ML Predictivo", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Modelos</div><div class="value">MLP + GBM</div></div>
  <div class="kpi"><div class="label">Features</div><div class="value" id="mlFeat">0</div></div>
  <div class="kpi"><div class="label">Estado</div><div class="value" id="mlConf">--</div></div>
</div>
<div class="top-bar">
  <select id="mlLiga"><option value="liga_mx">Liga MX</option><option value="mls">MLS</option><option value="premier_league">Premier League</option><option value="la_liga">La Liga</option><option value="serie_a">Serie A</option><option value="bundesliga">Bundesliga</option><option value="ligue_1">Ligue 1</option></select>
  <button class="btn btn-primary" onclick="trainML()">Entrenar</button>
  <button class="btn" onclick="loadML()">Actualizar</button>
</div>
<div id="mlStatus" style="font-size:12px;color:var(--text2);margin-bottom:8px"></div>
<div class="table-wrap"><table><thead><tr><th>Feature</th><th>Importancia</th></tr></thead><tbody id="mlBody"></tbody></table></div>
""", """
async function loadML(){try{
  const l=document.getElementById('mlLiga').value
  const d=await api('/api/ml/v2/features?liga='+l)
  const f=d.features||[]
  document.getElementById('mlFeat').textContent=f.length
  document.getElementById('mlConf').textContent=f.length?'OK':'Sin datos'
  document.getElementById('mlConf').className='value '+(f.length?'green':'red')
  let h=''
  f.slice(0,15).forEach(v=>{
    h+='<tr><td>'+v.feature_name+'</td><td><div style="background:var(--bg4);border-radius:3px;overflow:hidden;width:120px;display:inline-block"><div style="width:'+(v.importance*100)+'%;height:5px;background:var(--primary);border-radius:3px"></div></div> '+(v.importance*100).toFixed(1)+'%</td></tr>'
  })
  document.getElementById('mlBody').innerHTML=h||'<tr><td colspan="2" style="text-align:center;color:var(--text3);padding:20px">Entrena modelos primero</td></tr>'
}catch(e){toast('Error','err')}}
async function trainML(){try{
  document.getElementById('mlStatus').textContent='Entrenando...'
  await api('/api/ml/v2/train')
  document.getElementById('mlStatus').textContent='Entrenamiento iniciado'
  setTimeout(loadML,5e3)
}catch(e){toast('Error','err')}}
loadML()
""")

MOD_BANKROLL = module_page("Bankroll", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Bankroll Actual</div><div class="value" id="brActual">$0</div></div>
  <div class="kpi"><div class="label">Apuestas</div><div class="value amber" id="brTotal">0</div></div>
  <div class="kpi"><div class="label">Win Rate</div><div class="value green" id="brWinRate">0%</div></div>
  <div class="kpi"><div class="label">Ganancia Neta</div><div class="value" id="brGanancia">$0</div></div>
</div>
<div class="chart-box"><canvas id="brChart"></canvas></div>
<div class="table-wrap"><table><thead><tr><th>Fecha</th><th>Evento</th><th>Bankroll</th></tr></thead><tbody id="brBody"></tbody></table></div>
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
  document.getElementById('brBody').innerHTML=hh||'<tr><td colspan="3" style="text-align:center;color:var(--text3);padding:20px">Sin historial. Haz seed de la base de datos.</td></tr>'
  if(brChart)brChart.destroy()
  brChart=new Chart(document.getElementById('brChart'),{type:'line',data:{labels:h.map(v=>(v.fecha||'').slice(5,10)),datasets:[{label:'Bankroll',data:h.map(v=>v.bankroll),borderColor:'#4f46e5',backgroundColor:'rgba(79,70,229,0.05)',fill:true,tension:.4,pointRadius:1,borderWidth:2}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:{color:'rgba(0,0,0,0.04)'},ticks:{color:'var(--text3)',font:{size:10}}},y:{grid:{color:'rgba(0,0,0,0.04)'},ticks:{color:'var(--text3)',font:{size:10}}}}}})
}catch(e){toast('Error','err')}}
loadBR()
""")

MOD_SIMULACION = module_page("Simulacion", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Trades Simulados</div><div class="value" id="simTotal">0</div></div>
  <div class="kpi"><div class="label">Ganadas</div><div class="value green" id="simGanadas">0</div></div>
  <div class="kpi"><div class="label">Perdidas</div><div class="value red" id="simPerdidas">0</div></div>
  <div class="kpi"><div class="label">PnL Total</div><div class="value amber" id="simPnl">$0</div></div>
</div>
<div class="table-wrap"><table><thead><tr><th>Partido</th><th>Seleccion</th><th>Cuota</th><th>Edge</th><th>Resultado</th><th>PnL</th></tr></thead><tbody id="simBody"></tbody></table></div>
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
    const cls=v.resultado_simulado==='ganada'?'green':v.resultado_simulado==='perdida'?'red':'amber'
    h+='<tr><td>'+v.partido+'</td><td>'+v.seleccion+'</td><td class="num">'+v.cuota+'</td><td class="num">'+(v.edge_pct||0)+'%</td><td class="'+cls+'">'+v.resultado_simulado+'</td><td class="num">$'+(v.pnl_real||0)+'</td></tr>'
  })
  document.getElementById('simBody').innerHTML=h||'<tr><td colspan="6" style="text-align:center;color:var(--text3);padding:20px">Sin trades simulados</td></tr>'
}catch(e){toast('Error','err')}}
loadSim()
""")

MOD_CONTABILIDAD = module_page("Contabilidad", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Transacciones</div><div class="value" id="conCount">0</div></div>
  <div class="kpi"><div class="label">Ganadas</div><div class="value green" id="conGanadas">0</div></div>
  <div class="kpi"><div class="label">Perdidas</div><div class="value red" id="conPerdidas">0</div></div>
  <div class="kpi"><div class="label">Neto</div><div class="value amber" id="conNeto">$0</div></div>
</div>
<div class="chart-box"><canvas id="conChart"></canvas></div>
<div class="table-wrap"><table><thead><tr><th>Estrategia</th><th>Total</th><th>Ganadas</th><th>Perdidas</th><th>Neto</th></tr></thead><tbody id="conBody"></tbody></table></div>
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
  document.getElementById('conNeto').textContent='$'+n.toLocaleString()
  document.getElementById('conBody').innerHTML=h||'<tr><td colspan="5" style="text-align:center;color:var(--text3);padding:20px">Sin datos contables</td></tr>'
}catch(e){toast('Error','err')}}
loadCon()
""")

MOD_JOURNAL = module_page("Trading Journal", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Acciones (7d)</div><div class="value" id="jrTotal">0</div></div>
  <div class="kpi"><div class="label">Tipos</div><div class="value" id="jrTipos">0</div></div>
</div>
<div class="top-bar">
  <button class="btn" onclick="exportCSV()">Exportar CSV</button>
  <button class="btn" onclick="loadJR()">Actualizar</button>
</div>
<div class="table-wrap"><table><thead><tr><th>Fecha</th><th>Accion</th><th>Partido</th><th>Detalle</th></tr></thead><tbody id="jrBody"></tbody></table></div>
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
  document.getElementById('jrBody').innerHTML=h||'<tr><td colspan="4" style="text-align:center;color:var(--text3);padding:20px">Sin actividad registrada</td></tr>'
}catch(e){toast('Error','err')}}
function exportCSV(){window.open('/api/journal/export-csv','_blank')}
loadJR()
""")

MOD_BOOKMAKERS = module_page("Rating Casas", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Casas Evaluadas</div><div class="value" id="bmCount">0</div></div>
  <div class="kpi"><div class="label">Mejor Overround</div><div class="value green" id="bmBestOver">0</div></div>
</div>
<div class="top-bar">
  <button class="btn btn-primary" onclick="scanBM()">Escanear Casas</button>
  <span id="bmStatus" style="font-size:12px;color:var(--text2)"></span>
</div>
<div class="table-wrap"><table><thead><tr><th>Casa</th><th>Overround</th><th>CLV</th><th>Apariciones</th></tr></thead><tbody id="bmBody"></tbody></table></div>
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
  document.getElementById('bmBody').innerHTML=h||'<tr><td colspan="4" style="text-align:center;color:var(--text3);padding:20px">Escanear casas primero</td></tr>'
}catch(e){toast('Error','err')}}
async function scanBM(){try{
  document.getElementById('bmStatus').textContent='Escaneando...'
  await api('/api/bookmakers/scan')
  document.getElementById('bmStatus').textContent='Listo'
  loadBM()
}catch(e){document.getElementById('bmStatus').textContent='Error';toast('Error','err')}}
loadBM()
""")

MOD_CROSS = module_page("Cross Market", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Oportunidades</div><div class="value amber" id="cmCount">0</div></div>
  <div class="kpi"><div class="label">Mercados</div><div class="value">H2H vs AH</div></div>
</div>
<div class="top-bar"><button class="btn btn-primary" onclick="loadCM()">Analizar</button></div>
<div class="table-wrap"><table><thead><tr><th>Partido</th><th>H2H</th><th>AH</th><th>Diferencia</th></tr></thead><tbody id="cmBody"></tbody></table></div>
""", """
async function loadCM(){try{
  const d=await api('/api/odds/arbitraje?min_profit=0.1')
  const a=d.arbitrajes||[]
  document.getElementById('cmCount').textContent=a.length
  let h=''
  a.slice(0,20).forEach(v=>{
    h+='<tr><td>'+v.partido+'</td><td>H2H</td><td class="num">'+v.profit_pct+'%</td><td class="num" style="color:var(--green)">'+v.profit_pct+'%</td></tr>'
  })
  document.getElementById('cmBody').innerHTML=h||'<tr><td colspan="4" style="text-align:center;color:var(--text3);padding:20px">Sin datos cross-market</td></tr>'
}catch(e){toast('Error','err')}}
loadCM()
""")

MOD_BACKTESTING = module_page("Backtesting", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Resultados</div><div class="value" id="btTotal">0</div></div>
  <div class="kpi"><div class="label">Accuracy</div><div class="value amber" id="btAcc">0%</div></div>
</div>
<div class="top-bar"><button class="btn btn-primary" onclick="loadBT()">Actualizar</button></div>
<div class="table-wrap"><table><thead><tr><th>Config</th><th>Tipo</th><th>Resumen</th></tr></thead><tbody id="btBody"></tbody></table></div>
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
  <div class="kpi"><div class="label">Win Rate</div><div class="value amber" id="rpWinRate">0%</div></div>
  <div class="kpi"><div class="label">Sharpe</div><div class="value" id="rpSharpe">0</div></div>
  <div class="kpi"><div class="label">ROI</div><div class="value green" id="rpRoi">0%</div></div>
</div>
<div class="chart-box"><canvas id="rpChart"></canvas></div>
<div class="table-wrap"><table><thead><tr><th>Deporte</th><th>Total</th><th>Ganadas</th><th>Perdidas</th><th>Neto</th></tr></thead><tbody id="rpBody"></tbody></table></div>
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
    ht+='<tr><td>'+v.liga+'</td><td class="num">'+v.total+'</td><td class="num green">'+v.ganadas+'</td><td class="num red">'+v.perdidas+'</td><td class="num '+(net>=0?'green':'red')+'">$'+net+'</td></tr>'
  })
  document.getElementById('rpBody').innerHTML=ht||'<tr><td colspan="5" style="text-align:center;color:var(--text3);padding:20px">Sin datos de rendimiento</td></tr>'
  if(rpChart)rpChart.destroy()
  rpChart=new Chart(document.getElementById('rpChart'),{type:'bar',data:{labels:p.map(v=>v.liga||'?'),datasets:[{label:'Ganancia',data:p.map(v=>v.ganancia_neta||0),backgroundColor:p.map(v=>(v.ganancia_neta||0)>=0?'rgba(5,150,105,0.7)':'rgba(220,38,38,0.7)'),borderRadius:6,barThickness:24}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:{display:false},ticks:{color:'var(--text3)',font:{size:10}}},y:{grid:{color:'rgba(0,0,0,0.04)'},ticks:{color:'var(--text3)',font:{size:10}}}}}})
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
