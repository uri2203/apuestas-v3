"""
Dashboard v5 — Full Feature Rebuild.
Landing page + 20+ analysis modules with ALL system capabilities.
"""
import json

# ── CSS — Professional Theme ──────────────────────────────────────────────
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
  --purple:#7c3aed;--purple-bg:rgba(124,58,237,0.06);
  --teal:#0d9488;--teal-bg:rgba(13,148,136,0.06);
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
  --purple:#a78bfa;--purple-bg:rgba(167,139,250,0.1);
  --teal:#2dd4bf;--teal-bg:rgba(45,212,191,0.1);
  --shadow:0 1px 3px rgba(0,0,0,0.2);--shadow-md:0 4px 6px rgba(0,0,0,0.25)
}
html,body{height:100%;background:var(--bg);color:var(--text);font-family:'Inter',system-ui,-apple-system,sans-serif;font-size:13px;-webkit-font-smoothing:antialiased;line-height:1.5}
a{color:var(--primary);text-decoration:none}
.nav{display:flex;align-items:center;height:52px;padding:0 24px;background:var(--bg2);border-bottom:1px solid var(--border);gap:16px}
.nav .brand{font-size:15px;font-weight:700;color:var(--text);letter-spacing:-.3px}
.nav .brand span{color:var(--primary)}
.nav .links{display:flex;gap:2px;margin-left:24px;flex-wrap:wrap}
.nav .links a{padding:6px 12px;border-radius:var(--radius-sm);font-size:11px;font-weight:500;color:var(--text2);transition:.15s;white-space:nowrap}
.nav .links a:hover,.nav .links a.active{color:var(--text);background:var(--surface-hover)}
.nav .right{margin-left:auto;display:flex;align-items:center;gap:12px}
.nav .dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 6px var(--green)}
.nav .dot.off{background:var(--red);box-shadow:0 0 6px var(--red)}
.nav .mode{font-size:11px;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:.5px}
.nav .btn-icon{width:32px;height:32px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--surface);color:var(--text2);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:13px;transition:.15s}
.nav .btn-icon:hover{background:var(--surface-hover);color:var(--text);border-color:var(--border-hover)}
.content{max-width:1200px;margin:0 auto;padding:24px}
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:24px}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px 18px;transition:.15s}
.kpi:hover{border-color:var(--border-hover);box-shadow:var(--shadow)}
.kpi .label{font-size:10px;font-weight:600;color:var(--text3);margin-bottom:4px;text-transform:uppercase;letter-spacing:.3px}
.kpi .value{font-size:22px;font-weight:700;letter-spacing:-.5px;line-height:1.2}
.kpi .value.green{color:var(--green)}.kpi .value.red{color:var(--red)}.kpi .value.amber{color:var(--amber)}.kpi .value.blue{color:var(--blue)}.kpi .value.purple{color:var(--purple)}.kpi .value.teal{color:var(--teal)}
.kpi .sub{font-size:11px;color:var(--text3);margin-top:3px}
.section{margin-bottom:24px}
.section-header{display:flex;align-items:center;margin-bottom:12px;gap:12px}
.section-header h2{font-size:14px;font-weight:600;color:var(--text);margin:0}
.section-header .count{font-size:11px;color:var(--text3);background:var(--bg3);padding:2px 8px;border-radius:10px}
.section-header .line{flex:1;height:1px;background:var(--border)}
.mod-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}
.mod{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px 16px;cursor:pointer;transition:.2s;position:relative;overflow:hidden}
.mod:hover{border-color:var(--primary);box-shadow:var(--shadow-md);transform:translateY(-1px)}
.mod::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--primary);opacity:0;transition:.2s}
.mod:hover::before{opacity:1}
.mod .icon{width:36px;height:36px;border-radius:var(--radius-sm);display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:700;margin-bottom:10px;color:var(--primary);background:var(--primary-bg)}
.mod .name{font-size:13px;font-weight:600;color:var(--text);margin-bottom:3px}
.mod .desc{font-size:11px;color:var(--text2);line-height:1.4}
.mod .tag{position:absolute;top:12px;right:12px;font-size:9px;font-weight:600;color:var(--primary);background:var(--primary-bg);padding:2px 6px;border-radius:4px;text-transform:uppercase;letter-spacing:.3px}
.empty{background:var(--surface);border:1px dashed var(--border);border-radius:var(--radius);padding:32px;text-align:center;margin-bottom:16px}
.empty .icon{font-size:32px;margin-bottom:8px;color:var(--text3)}
.empty h3{font-size:14px;font-weight:600;color:var(--text);margin-bottom:4px}
.empty p{font-size:12px;color:var(--text2);margin-bottom:12px;max-width:400px;margin-left:auto;margin-right:auto}
.empty .btn{display:inline-flex;align-items:center;gap:6px;padding:8px 20px;border-radius:var(--radius-sm);border:none;font-size:12px;font-weight:600;cursor:pointer;transition:.15s;font-family:'Inter',sans-serif}
.btn{padding:7px 16px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--surface);color:var(--text2);font-size:12px;font-weight:500;cursor:pointer;transition:.15s;font-family:'Inter',sans-serif}
.btn:hover{background:var(--surface-hover);color:var(--text);border-color:var(--border-hover)}
.btn-primary{background:var(--primary);color:#fff;border-color:var(--primary)}.btn-primary:hover{background:var(--primary-hover)}
.btn-sm{padding:5px 10px;font-size:11px}
.btn-green{background:var(--green);color:#fff;border-color:var(--green)}
.btn-red{background:var(--red);color:#fff;border-color:var(--red)}
.btn-amber{background:var(--amber);color:#fff;border-color:var(--amber)}
.btn-outline{background:transparent;border:1px solid var(--border);color:var(--text2)}.btn-outline:hover{background:var(--surface-hover);border-color:var(--border-hover)}
.top-bar{display:flex;align-items:center;gap:8px;margin-bottom:14px;flex-wrap:wrap}
select,input[type=number],input[type=text]{padding:6px 12px;border:1px solid var(--border);border-radius:var(--radius-sm);background:var(--surface);color:var(--text);font-size:12px;font-family:'Inter',sans-serif}
select:focus,input:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px var(--primary-bg)}
.table-wrap{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);overflow:hidden}
table{width:100%;border-collapse:collapse;font-size:12px}
th{padding:10px 14px;text-align:left;font-size:10px;font-weight:600;color:var(--text3);text-transform:uppercase;letter-spacing:.4px;background:var(--bg3);border-bottom:1px solid var(--border)}
td{padding:10px 14px;color:var(--text2);border-bottom:1px solid var(--border)}
tr:last-child td{border:0}
tr:hover td{background:var(--surface-hover)}
td.num{font-variant-numeric:tabular-nums;text-align:right}
.loading{text-align:center;padding:40px;color:var(--text2)}
.spinner{width:20px;height:20px;border:2px solid var(--border);border-top-color:var(--primary);border-radius:50%;animation:spin .6s linear infinite;margin:0 auto 8px}
@keyframes spin{to{transform:rotate(360deg)}}
.toast{position:fixed;bottom:16px;right:16px;padding:10px 16px;border-radius:var(--radius-sm);background:var(--bg2);border:1px solid var(--border);color:var(--text);font-size:12px;z-index:9999;box-shadow:var(--shadow-md);animation:slideUp .2s ease;max-width:320px}
.toast.ok{border-color:var(--green)}.toast.err{border-color:var(--red)}.toast.info{border-color:var(--primary)}
@keyframes slideUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.chart-box{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:12px}
.chart-box canvas{width:100%!important;max-height:240px}
.edge-hot{color:var(--green);font-weight:700}
.edge-warm{color:var(--amber);font-weight:600}
.edge-cold{color:var(--text3);font-weight:400}
.edge-mega{color:#10b981;font-weight:800;text-shadow:0 0 4px rgba(16,185,129,0.3)}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:600}
.badge-green{background:var(--green-bg);color:var(--green)}
.badge-red{background:var(--red-bg);color:var(--red)}
.badge-amber{background:var(--amber-bg);color:var(--amber)}
.badge-blue{background:var(--blue-bg);color:var(--blue)}
.badge-purple{background:var(--purple-bg);color:var(--purple)}
.badge-teal{background:var(--teal-bg);color:var(--teal)}
.tabs{display:flex;gap:2px;margin-bottom:14px;border-bottom:1px solid var(--border);padding-bottom:0}
.tab{padding:8px 16px;font-size:12px;font-weight:500;color:var(--text3);cursor:pointer;border-bottom:2px solid transparent;transition:.15s}
.tab:hover{color:var(--text2)}
.tab.active{color:var(--primary);border-bottom-color:var(--primary);font-weight:600}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:16px;margin-bottom:12px}
.card h3{font-size:13px;font-weight:600;margin-bottom:8px}
.card p{font-size:12px;color:var(--text2)}
.flex-row{display:flex;gap:12px;flex-wrap:wrap}
.flex-col{flex:1;min-width:200px}
.news-item{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:12px 16px;margin-bottom:8px;transition:.15s}
.news-item:hover{border-color:var(--border-hover)}
.news-item .title{font-size:13px;font-weight:600;margin-bottom:4px}
.news-item .meta{font-size:11px;color:var(--text3)}
.news-item .alert{font-size:11px;color:var(--red);font-weight:500;margin-top:4px}
.progress-bar{background:var(--bg4);border-radius:3px;overflow:hidden;height:6px;width:100%}
.progress-bar .fill{height:100%;border-radius:3px;transition:width .3s}
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
.cat-label{font-size:10px;font-weight:700;color:var(--primary);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;padding:4px 0;border-bottom:1px solid var(--primary-bg)}
</style>
</head>
<body>
<div class="nav">
  <div class="brand">Apuestas<span>Pro</span></div>
  <div class="links">
    <a href="/" class="active">Home</a>
    <a href="/panel/value-bets">Value</a>
    <a href="/panel/alta-prob">Alta Prob</a>
    <a href="/panel/sharp">Sharp</a>
    <a href="/panel/copa">Copa</a>
    <a href="/panel/bankroll">Bankroll</a>
    <a href="/panel/rendimiento">Stats</a>
  </div>
  <div class="right">
    <span class="dot off" id="sd"></span>
    <span class="mode" id="modeLabel">OFFLINE</span>
    <button class="btn-icon" onclick="theme()" title="Theme">&#9790;</button>
    <button class="btn-icon" onclick="location='/logout'" title="Salir">&#8592;</button>
  </div>
</div>

<div class="content">
  <div class="hero">
    <div>
      <h1>Sistema de <span>Analisis</span> Deportivo</h1>
      <p>ML Predictivo &middot; Sharp Money &middot; Arbitraje &middot; Value Bets &middot; Kelly &middot; Monte Carlo &middot; NLP</p>
    </div>
    <div class="meta">
      <div class="label">Ultima actualizacion</div>
      <div class="val" id="lastUpd">--</div>
      <div class="ver">v5.0</div>
    </div>
  </div>

  <div class="kpi-grid" id="kpiGrid">
    <div class="kpi"><div class="label">Bankroll</div><div class="value" id="kpiBr">$0</div><div class="sub">Valor actual</div></div>
    <div class="kpi"><div class="label">Win Rate</div><div class="value" id="kpiWr">0%</div><div class="sub">Ultimos 30d</div></div>
    <div class="kpi"><div class="label">ROI</div><div class="value" id="kpiRoi">0%</div><div class="sub">Retorno total</div></div>
    <div class="kpi"><div class="label">Sharpe</div><div class="value" id="kpiSh">0.00</div><div class="sub">Riesgo ajustado</div></div>
    <div class="kpi"><div class="label">PnL Neto</div><div class="value" id="kpiPnl">$0</div><div class="sub">30 dias</div></div>
    <div class="kpi"><div class="label">Value Bets Hoy</div><div class="value amber" id="kpiVb">0</div><div class="sub">Edge: <span id="kpiEdge">0%</span></div></div>
    <div class="kpi"><div class="label">Bets Hoy</div><div class="value blue" id="kpiBets">0</div><div class="sub">Registradas</div></div>
    <div class="kpi"><div class="label">Predicciones</div><div class="value purple" id="kpiPreds">0</div><div class="sub">Hoy</div></div>
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
      <h2>VALUE &amp; EDGE</h2>
      <span class="count">8 modulos</span>
      <div class="line"></div>
    </div>
    <div class="mod-grid">
      <div class="mod" onclick="location='/panel/value-bets'"><span class="tag">EDGE</span><div class="icon" style="color:var(--green)">&#9650;</div><div class="name">Value Bets</div><div class="desc">Deteccion de edge con colores por nivel</div></div>
      <div class="mod" onclick="location='/panel/sharp'"><span class="tag">LIVE</span><div class="icon" style="color:var(--red)">$</div><div class="name">Sharp Money</div><div class="desc">Movimiento de lineas y steam moves</div></div>
      <div class="mod" onclick="location='/panel/arbitraje'"><span class="tag">ARB</span><div class="icon" style="color:var(--amber)">&#8734;</div><div class="name">Arbitraje</div><div class="desc">Surebets multi-casa garantizadas</div></div>
      <div class="mod" onclick="location='/panel/cross-market'"><span class="tag">X</span><div class="icon" style="color:var(--blue)">&#8644;</div><div class="name">Cross Market</div><div class="desc">H2H vs AH comparativa</div></div>
      <div class="mod" onclick="location='/panel/kelly'"><span class="tag">CALC</span><div class="icon" style="color:var(--teal)">K</div><div class="name">Kelly Calculator</div><div class="desc">Fraccion optimal de bankroll</div></div>
      <div class="mod" onclick="location='/panel/alta-prob'"><span class="tag" style="background:var(--green-bg);color:var(--green)">PRO</span><div class="icon" style="color:var(--green)">&#9733;</div><div class="name">Alta Probabilidad</div><div class="desc">Tenis, MMA, NBA, NFL, Caballos, Esports - 2 resultados</div></div>
      <div class="mod" onclick="location='/panel/value-engine'"><span class="tag">PRO</span><div class="icon" style="color:var(--purple)">V</div><div class="name">Value Engine</div><div class="desc">Analisis profesional CLV + EV</div></div>
      <div class="mod" onclick="location='/panel/copa'"><span class="tag">WC</span><div class="icon" style="color:var(--green)">&#9917;</div><div class="name">Copa del Mundo</div><div class="desc">2026: value bets, standings, sharp</div></div>
    </div>
  </div>

  <div class="section">
    <div class="section-header">
      <h2>ANALISIS &amp; MODELOS</h2>
      <span class="count">6 modulos</span>
      <div class="line"></div>
    </div>
    <div class="mod-grid">
      <div class="mod" onclick="location='/panel/brain'"><span class="tag">BRAIN</span><div class="icon" style="color:var(--amber)">&#9878;</div><div class="name">Agente Brain</div><div class="desc">Cerebro autónomo: escanea, filtra, simula, aprende</div></div>
      <div class="mod" onclick="location='/panel/hulk'"><span class="tag">HULK</span><div class="icon" style="color:var(--red)">&#9876;</div><div class="name">Agente HULK</div><div class="desc">El depredador: steam, live, arbitraje, contrarian, parlay</div></div>
      <div class="mod" onclick="location='/panel/modelos-avanzados'"><span class="tag">ADV</span><div class="icon" style="color:var(--green)">&#9878;</div><div class="name">Modelos Avanzados</div><div class="desc">Dixon-Coles, ELO, Fatiga, Clima, CLV</div></div>
      <div class="mod" onclick="location='/panel/ml'"><span class="tag">ML</span><div class="icon" style="color:var(--purple)">&#9734;</div><div class="name">ML Predictivo</div><div class="desc">MLP + GBM ensemble + feature importance</div></div>
      <div class="mod" onclick="location='/panel/backtesting'"><span class="tag">BT</span><div class="icon" style="color:var(--blue)">&#8634;</div><div class="name">Backtesting</div><div class="desc">Historico y validacion de modelos</div></div>
      <div class="mod" onclick="location='/panel/nlp'"><span class="tag">NLP</span><div class="icon" style="color:var(--teal)">&#9998;</div><div class="name">Noticias &amp; Lesiones</div><div class="desc">Sentimiento y lesiones NLP</div></div>
      <div class="mod" onclick="location='/panel/montecarlo'"><span class="tag">SIM</span><div class="icon" style="color:var(--amber)">&#119891;</div><div class="name">Monte Carlo</div><div class="desc">Simulacion probabilistica de partidos</div></div>
    </div>
  </div>

  <div class="section">
    <div class="section-header">
      <h2>OPERACIONES</h2>
      <span class="count">5 modulos</span>
      <div class="line"></div>
    </div>
    <div class="mod-grid">
      <div class="mod" onclick="location='/panel/bankroll'"><span class="tag">KELLY</span><div class="icon" style="color:var(--green)">$</div><div class="name">Bankroll</div><div class="desc">Gestion, historial y riesgo de ruina</div></div>
      <div class="mod" onclick="location='/panel/simulacion'"><span class="tag">SIM</span><div class="icon" style="color:var(--amber)">&#8644;</div><div class="name">Simulacion</div><div class="desc">Trades simulados automaticos</div></div>
      <div class="mod" onclick="location='/panel/contabilidad'"><span class="tag">P&amp;L</span><div class="icon" style="color:var(--blue)">&#9776;</div><div class="name">Contabilidad</div><div class="desc">P&amp;L por estrategia y reportes</div></div>
      <div class="mod" onclick="location='/panel/journal'"><span class="tag">LOG</span><div class="icon" style="color:var(--text2)">&#9998;</div><div class="name">Trading Journal</div><div class="desc">Bitacora y export CSV</div></div>
      <div class="mod" onclick="location='/panel/mercados'"><span class="tag">MULTI</span><div class="icon" style="color:var(--purple)">&#8644;</div><div class="name">Mercados Multi</div><div class="desc">Hedge, Dutching, Value multi-mercado</div></div>
    </div>
  </div>

  <div class="section">
    <div class="section-header">
      <h2>INFRAESTRUCTURA</h2>
      <span class="count">5 modulos</span>
      <div class="line"></div>
    </div>
    <div class="mod-grid">
      <div class="mod" onclick="location='/panel/bookmakers'"><span class="tag">RANK</span><div class="icon" style="color:var(--amber)">&#9733;</div><div class="name">Rating Casas</div><div class="desc">Overround, CLV y ranking</div></div>
      <div class="mod" onclick="location='/panel/progol'"><span class="tag">QUI</span><div class="icon" style="color:var(--green)">&#9917;</div><div class="name">Progol Optimizer</div><div class="desc">Quiniela optimizada y diversificada</div></div>
      <div class="mod" onclick="location='/panel/cuentas'"><span class="tag">ACC</span><div class="icon" style="color:var(--blue)">&#9783;</div><div class="name">Cuentas</div><div class="desc">Multi-cuenta y camuflaje</div></div>
      <div class="mod" onclick="location='/panel/portfolio'"><span class="tag">PORT</span><div class="icon" style="color:var(--teal)">&#9670;</div><div class="name">Portfolio</div><div class="desc">Distribucion y rotacion de apuestas</div></div>
      <div class="mod" onclick="location='/panel/rendimiento'"><span class="tag">STATS</span><div class="icon" style="color:var(--primary)">&#9632;</div><div class="name">Rendimiento</div><div class="desc">Graficas, Sharpe, por deporte</div></div>
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
  document.getElementById('kpiBets').textContent=h.apuestas||0
  document.getElementById('kpiPreds').textContent=h.predicciones||0
  document.getElementById('sd').className='dot'
  document.getElementById('modeLabel').textContent='ONLINE'
}catch(e){
  document.getElementById('sd').className='dot off'
  document.getElementById('modeLabel').textContent='ERROR'
}
setTimeout(loadKPI,3e4)}
loadKPI()
</script>
</body>
</html>"""

# ── Module page wrapper ───────────────────────────────────────────────────
def module_page(title, body_html, extra_js=""):
    nav_links = [
        ("Home","/"),("Value Bets","/panel/value-bets"),("Sharp","/panel/sharp"),
        ("Arbitraje","/panel/arbitraje"),("Kelly","/panel/kelly"),
        ("Bankroll","/panel/bankroll"),("Cuentas","/panel/cuentas"),
        ("Progol","/panel/progol"),("Rendimiento","/panel/rendimiento"),
    ]
    links_html = "".join(f'<a href="{u}"{" class=active" if title.lower() in t.lower() or (title=="Home" and u=="/") else ""}>{t}</a>' for t,u in nav_links)
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
  <div class="links">{links_html}</div>
  <div class="right">
    <span style="font-size:12px;font-weight:600;color:var(--text2)">{title}</span>
    <button class="btn-icon" onclick="theme()" title="Theme">&#9790;</button>
    <button class="btn-icon" onclick="location='/'" title="Home">&#8592;</button>
  </div>
</div>
<div class="content">
  <div id="modLoading" class="loading"><div class="spinner"></div><div>Loading...</div></div>
  <div id="modContent" style="display:none">{body_html}</div>
</div>
<script>
if(localStorage.getItem('ap_theme')==='dark')document.documentElement.classList.add('dark')
else if(!localStorage.getItem('ap_theme'))document.documentElement.classList.add('dark')
document.getElementById('modLoading').style.display='none'
document.getElementById('modContent').style.display='block'
function theme(){{document.documentElement.classList.toggle('dark');localStorage.setItem('ap_theme',document.documentElement.classList.contains('dark')?'dark':'light')}}
function toast(msg,type){{const t=document.createElement('div');t.className='toast '+type;t.textContent=msg;document.body.appendChild(t);setTimeout(()=>t.remove(),3e3)}}
async function api(url){{const r=await fetch(url);if(!r.ok)throw new Error(await r.text());return r.json()}}
function edgeClass(e){{e=parseFloat(e)||0;if(e>=10)return 'edge-mega';if(e>=5)return 'edge-hot';if(e>=2)return 'edge-warm';return 'edge-cold'}}
function edgeBadge(e){{e=parseFloat(e)||0;if(e>=10)return '<span class="badge badge-green">MEGA '+e.toFixed(1)+'%</span>';if(e>=5)return '<span class="badge badge-green">HIGH '+e.toFixed(1)+'%</span>';if(e>=2)return '<span class="badge badge-amber">MID '+e.toFixed(1)+'%</span>';return '<span class="badge badge-red">LOW '+e.toFixed(1)+'%</span>'}}
{extra_js}
</script>
</body>
</html>"""

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

# ════════════════════════════════════════════════════════════════════════════
# MODULE: VALUE BETS — with edge color coding
# ════════════════════════════════════════════════════════════════════════════
MOD_VALUE_BETS = module_page("Value Bets", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Edge Promedio</div><div class="value amber" id="vbAvgEdge">0%</div></div>
  <div class="kpi"><div class="label">Value Bets</div><div class="value" id="vbCount">0</div></div>
  <div class="kpi"><div class="label">Mejor Edge</div><div class="value green" id="vbMaxEdge">0%</div></div>
  <div class="kpi"><div class="label">Deportes</div><div class="value blue" id="vbSports">0</div></div>
  <div class="kpi"><div class="label">Partidos</div><div class="value" id="vbMatches">0</div></div>
</div>
<div class="top-bar">
  <select id="vbSport"><option value="upcoming">Todos los deportes</option><optgroup label="ALTA PREDECIBILIDAD"><option value="soccer_fifa_world_cup">Copa del Mundo 2026</option><option value="tennis_atp_world_tour">Tenis ATP</option><option value="tennis_wta">Tenis WTA</option><option value="mma_mixed_martial_arts">MMA/UFC</option><option value="boxing_boxing">Boxing</option></optgroup><optgroup label="ALTO VOLUMEN"><option value="basketball_nba">NBA</option><option value="basketball_wnba">WNBA</option><option value="americanfootball_nfl">NFL</option><option value="icehockey_nhl">NHL</option><option value="baseball_mlb">MLB</option></optgroup><optgroup label="CARRERAS"><option value="horse_racing">Carreras de Caballos</option></optgroup><optgroup label="CRICKET & RUGBY"><option value="cricket_ipl">Cricket IPL</option><option value="cricket_big_bash">Cricket Big Bash</option><option value="rugby_league_nrl">Rugby NRL</option></optgroup><optgroup label="ESPORTS"><option value="esports_lol_lck">LoL LCK</option><option value="esports_lol_lec">LoL LEC</option><option value="esports_csgo_esl">CS2 ESL</option><option value="esports_dota2_dpc">Dota 2 DPC</option></optgroup><optgroup label="MOTORSPORT"><option value="motorsport_f1_race_winner">F1 Ganador Carrera</option></optgroup><optgroup label="FUTBOL"><option value="soccer_mexico_ligamx">Liga MX</option><option value="soccer_epl">Premier League</option><option value="soccer_spain_la_liga">La Liga</option><option value="soccer_germany_bundesliga">Bundesliga</option><option value="soccer_italy_serie_a">Serie A</option><option value="soccer_uefa_champions_league">Champions League</option></optgroup></select>
  <input id="vbMinEdge" type="number" value="2" step="0.5" style="width:70px" placeholder="Edge min"/>
  <select id="vbConf" onchange="filterVBConf()">
    <option value="all">Todas las confianzas</option>
    <option value="ALTA">Solo ALTA (75+)</option>
    <option value="MEDIA">Solo MEDIA (55-74)</option>
    <option value="BAJA">BAJA / MUY BAJA (&lt;55)</option>
  </select>
  <button class="btn btn-primary" onclick="loadVB()">Buscar Value Bets</button>
  <button class="btn" onclick="loadVB()">Actualizar</button>
  <span id="vbStatus" style="font-size:11px;color:var(--text3)"></span>
</div>
<div id="vbCards"></div>
<div class="table-wrap"><table><thead><tr><th>Conf</th><th>Edge</th><th>Partido</th><th>Apostar</th><th>Casa</th><th>Cuota</th><th>Kelly %</th><th>Monto</th></tr></thead><tbody id="vbBody"></tbody></table></div>
""", """
function sportIcon(d){if(d==='combat')return'🥊';if(d==='tennis')return'🎾';if(d==='team')return'🏈';if(d==='racing')return'🏇';if(d==='soccer')return'⚽';return'🏆'}
function confBadge(score,label){
  if(score>=75)return'<span class="badge badge-green">'+label+' ('+score+')</span>'
  if(score>=55)return'<span class="badge badge-amber">'+label+' ('+score+')</span>'
  return'<span class="badge badge-red">'+label+' ('+score+')</span>'
}
let vbAllData=[]
function filterVBConf(){
  const f=document.getElementById('vbConf').value
  const rows=document.querySelectorAll('#vbBody tr[data-conf]')
  let h='',sumE=0,maxE=0,count=0
  rows.forEach(r=>{
    const conf=r.getAttribute('data-conf')
    const show=f==='all'||conf===f||(f==='BAJA'&&(conf==='BAJA'||conf==='MUY BAJA'))
    r.style.display=show?'':'none'
    if(show){
      const e=parseFloat(r.dataset.edge)||0
      const m=parseFloat(r.dataset.monto)||0
      sumE+=e;maxE=Math.max(maxE,e);count++
      h+=r.outerHTML
    }
  })
  if(f!=='all'){
    document.getElementById('vbBody').innerHTML=h||'<tr><td colspan="8" style="text-align:center;color:var(--text3);padding:20px">Sin signals con confianza '+f+'</td></tr>'
    document.getElementById('vbCount').textContent=count
    document.getElementById('vbAvgEdge').textContent=(count?(sumE/count).toFixed(1):'0')+'%'
    document.getElementById('vbMaxEdge').textContent=maxE.toFixed(1)+'%'
  }
}
async function loadVB(){try{
  document.getElementById('vbStatus').textContent='Escaneando...'
  const s=document.getElementById('vbSport').value
  const e=document.getElementById('vbMinEdge').value
  const d=await api('/api/odds/value-bets?deporte='+s+'&edge_minimo='+e+'&multi='+(s==='upcoming'?'1':'0'))
  const vb=d.value_bets||[]
  vbAllData=vb
  let h='',sumE=0,maxE=0
  const bySport={}
  vb.forEach(v=>{const k=v.deporte||'other';if(!bySport[k])bySport[k]=[];bySport[k].push(v)})
  let cardsHtml=''
  Object.entries(bySport).forEach(([sport,items])=>{
    const icon=sportIcon(sport)
    const best=items[0]
    cardsHtml+='<div class="card" style="border-left:4px solid var(--green);margin-bottom:10px;padding:12px">'
    cardsHtml+='<div style="display:flex;justify-content:space-between;align-items:center">'
    cardsHtml+='<div><strong>'+icon+' '+sport.toUpperCase()+'</strong> — '+items.length+' value bets</div>'
    cardsHtml+='<div style="font-size:12px;color:var(--text3)">Mejor edge: <strong style="color:var(--green)">'+best.edge_porcentaje+'%</strong> en '+best.partido+'</div>'
    cardsHtml+='</div></div>'
  })
  document.getElementById('vbCards').innerHTML=cardsHtml
  vb.forEach(v=>{
    const edge=parseFloat(v.edge_porcentaje)||0
    const icon=sportIcon(v.deporte)
    const conf=v.confianza_score||0
    const confL=v.confianza||'-'
    const kelly=v.kelly||{}
    const kellyPct=kelly.kelly_ajustado_pct||0
    const monto=kelly.monto_sugerido||0
    const score=v.confianza_score||0
    h+='<tr data-conf="'+confL+'" data-edge="'+edge+'" data-monto="'+monto+'">'
    h+='<td>'+confBadge(score,confL)+'</td>'
    h+='<td>'+edgeBadge(edge)+'</td>'
    h+='<td>'+v.partido+'</td>'
    h+='<td><strong>'+v.resultado+'</strong></td>'
    h+='<td><span class="badge badge-blue">'+v.casa+'</span></td>'
    h+='<td class="num">'+v.cuota+'</td>'
    h+='<td class="num" style="color:'+(kellyPct>0?'var(--green)':'var(--red)')+'">'+kellyPct+'%</td>'
    h+='<td class="num" style="font-weight:700;color:'+(monto>0?'var(--green)':'var(--red)')+'">$'+monto+'</td>'
    h+='</tr>'
    sumE+=edge;maxE=Math.max(maxE,edge)
  })
  const err=d.api_error||(!vb.length?d.aviso:'')
  document.getElementById('vbBody').innerHTML=h||'<tr><td colspan="8" style="text-align:center;color:var(--text3);padding:20px">'+(err||'Sin value bets encontrados')+'</td></tr>'
  document.getElementById('vbCount').textContent=vb.length
  document.getElementById('vbAvgEdge').textContent=(vb.length?(sumE/vb.length).toFixed(1):'0')+'%'
  document.getElementById('vbMaxEdge').textContent=maxE.toFixed(1)+'%'
  document.getElementById('vbSports').textContent=d.deportes_escaneados||0
  document.getElementById('vbMatches').textContent=d.total_partidos_analizados||0
  document.getElementById('vbStatus').textContent=vb.length+' value bets | '+d.total_partidos_analizados+' partidos'
  if(d.api_error)toast(d.api_error,'err')
}catch(e){toast('Error al cargar value bets','err')}}
loadVB()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: SHARP MONEY
# ════════════════════════════════════════════════════════════════════════════
MOD_SHARP = module_page("Sharp Money", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Partidos Escaneados</div><div class="value" id="sharpCount">0</div></div>
  <div class="kpi"><div class="label">Con Señal</div><div class="value green" id="sharpSignal">0</div></div>
  <div class="kpi"><div class="label">Mejor Edge</div><div class="value amber" id="sharpBestEdge">0%</div></div>
  <div class="kpi"><div class="label">Total Sugerido</div><div class="value green" id="sharpTotal$">$0</div></div>
</div>
<div class="top-bar">
  <select id="sharpSport"><option value="upcoming">Todos</option><option value="soccer_fifa_world_cup">Copa del Mundo</option><option value="tennis_atp_world_tour">Tenis ATP</option><option value="tennis_wta">Tenis WTA</option><option value="mma_mixed_martial_arts">MMA/UFC</option><option value="basketball_nba">NBA</option><option value="horse_racing">Caballos</option><option value="cricket_ipl">Cricket IPL</option><option value="esports_lol_lck">LoL LCK</option><option value="motorsport_f1_race_winner">F1</option></select>
  <select id="sharpConf" onchange="filterSharpConf()">
    <option value="all">Todas las confianzas</option>
    <option value="ALTA">Solo ALTA (75+)</option>
    <option value="MEDIA">Solo MEDIA (55-74)</option>
    <option value="BAJA">BAJA / MUY BAJA (&lt;55)</option>
  </select>
  <button class="btn btn-primary" onclick="loadSharp()">Escanear Partidos</button>
  <button class="btn" onclick="loadSharp()">Actualizar</button>
  <span id="sharpStatus" style="font-size:11px;color:var(--text3)"></span>
</div>
<div id="sharpCards"></div>
""", """
function sharpBadge(conf){if(conf==='ALTA')return '<span class="badge badge-green">ALTA</span>';if(conf==='MEDIA')return '<span class="badge badge-amber">MEDIA</span>';return '<span class="badge badge-red">'+conf+'</span>'}
function signalBadge(t){if(t==='VALUE BET')return '<span class="badge badge-green">VALUE BET</span>';if(t==='VALUE MENOR')return '<span class="badge badge-amber">VALUE</span>';if(t==='STEAM')return '<span class="badge badge-purple">STEAM</span>';return '<span class="badge badge-red">SIN SEÑAL</span>'}
let sharpAllCards=[]
function filterSharpConf(){
  const f=document.getElementById('sharpConf').value
  let totalM=0,count=0,html=''
  sharpAllCards.forEach(c=>{
    const conf=c.conf
    const show=f==='all'||conf===f||(f==='BAJA'&&(conf==='BAJA'||conf==='MUY BAJA'))
    if(show){html+=c.html;totalM+=c.monto;count++}
  })
  document.getElementById('sharpCards').innerHTML=html||'<div class="empty"><div class="icon">$</div><h3>Sin signals con confianza '+f+'</h3></div>'
  document.getElementById('sharpSignal').textContent=count
  document.getElementById('sharpTotal$').textContent='$'+totalM.toFixed(0)
}
async function loadSharp(){try{
  document.getElementById('sharpStatus').textContent='Escaneando...'
  const s=document.getElementById('sharpSport').value
  const d=await api('/api/sharp/scan?deporte='+s)
  const recs=d.recomendaciones||[]
  document.getElementById('sharpCount').textContent=d.total_partidos||0
  document.getElementById('sharpSignal').textContent=d.con_señal||0
  let bestE=0,totalMonto=0,html=''
  sharpAllCards=[]
  recs.forEach(v=>{
    const edge=parseFloat(v.edge)||0
    if(edge>bestE)bestE=edge
    const conf=v.confianza||'-'
    const confS=v.confianza_score||0
    const sel=v.seleccion||''
    const casa=v.casa_recomendada||''
    const cuota=v.cuota||0
    const accion=v.accion||''
    const sig=v.tipo_senal||'SIN SEÑAL'
    const liga=v.liga||''
    const fecha=v.fecha||''
    const nCasas=v.n_casas||0
    const prob=v.probabilidad_implicita||0
    const k=v.kelly||{}
    const monto=k.monto_sugerido||0
    if(monto>0)totalMonto+=monto
    const color=edge>=5?'border-left:4px solid var(--green)':edge>=2?'border-left:4px solid var(--amber)':'border-left:4px solid var(--border)'
    let cardHtml=''
    cardHtml+='<div class="card" style="'+color+'margin-bottom:12px;padding:16px">'
    cardHtml+='<div style="display:flex;justify-content:space-between;align-items:start;flex-wrap:wrap;gap:8px">'
    cardHtml+='<div>'
    cardHtml+='<div style="font-size:15px;font-weight:700;margin-bottom:4px">'+v.partido+'</div>'
    cardHtml+='<div style="font-size:11px;color:var(--text3)">'+liga+' | '+nCasas+' casas | '+fecha+'</div>'
    cardHtml+='</div>'
    cardHtml+='<div>'+signalBadge(sig)+' '+sharpBadge(conf)+'</div>'
    cardHtml+='</div>'
    if(sig==='VALUE BET'||sig==='VALUE MENOR'){
      const kellyPct=k.kelly_ajustado_pct||0
      cardHtml+='<div style="margin-top:12px;padding:12px;background:var(--green-bg);border-radius:var(--radius-sm)">'
      cardHtml+='<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">'
      cardHtml+='<div style="font-size:14px;font-weight:700;color:var(--green)">&#9650; APOSTAR: '+sel+'</div>'
      cardHtml+='<div>'+(confS>=75?'<span class="badge badge-green">CONFIANZA '+conf+' ('+confS+')</span>':confS>=55?'<span class="badge badge-amber">CONFIANZA '+conf+' ('+confS+')</span>':'<span class="badge badge-red">CONFIANZA '+conf+' ('+confS+')</span>')+'</div>'
      cardHtml+='</div>'
      cardHtml+='<div style="display:flex;gap:16px;flex-wrap:wrap;font-size:12px;margin-top:6px">'
      cardHtml+='<div><strong>Casa:</strong> '+casa+'</div>'
      cardHtml+='<div><strong>Cuota:</strong> '+cuota+'</div>'
      cardHtml+='<div><strong>Edge:</strong> <span style="color:var(--green);font-weight:700">'+edge.toFixed(1)+'%</span></div>'
      cardHtml+='<div><strong>Kelly:</strong> '+kellyPct+'%</div>'
      cardHtml+='<div style="font-weight:700;color:var(--green)">MONTO: $'+monto+'</div>'
      cardHtml+='</div>'
      cardHtml+='<div><strong>Ejemplo:</strong> '+accion+'</div>'
      cardHtml+='</div></div>'
      if(v.casas&&v.casas.length>0){
        cardHtml+='<div style="margin-top:8px;font-size:11px;color:var(--text3)"><strong>Odds comparadas:</strong> '
        v.casas.slice(0,6).forEach(c=>{
          const odds=c.odds||{}
          const oH=odds[sel]||'-'
          cardHtml+='<span class="badge badge-blue" style="margin:2px">'+c.casa+': '+oH+'</span> '
        })
        cardHtml+='</div>'
      }
    }else if(sig==='STEAM'){
      cardHtml+='<div style="margin-top:8px;font-size:12px;color:var(--purple)">Steam detectado — '+((v.nota||'').slice(0,100))+'</div>'
    }else{
      cardHtml+='<div style="margin-top:8px;font-size:12px;color:var(--text3)">Sin señal clara en este partido</div>'
    }
    cardHtml+='</div>'
    html+=cardHtml
    sharpAllCards.push({conf:conf,monto:monto,html:cardHtml})
  })
  document.getElementById('sharpCards').innerHTML=html||'<div class="empty"><div class="icon">$</div><h3>Sin partidos disponibles</h3><p>Escanea para encontrar value bets con análisis sharp</p></div>'
  document.getElementById('sharpStatus').textContent=(d.con_señal||0)+' señales de '+(d.total_partidos||0)+' partidos'
  document.getElementById('sharpTotal$').textContent='$'+totalMonto.toFixed(0)
}catch(e){toast('Error scan: '+e.message,'err')}}
loadSharp()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: ARBITRAJE
# ════════════════════════════════════════════════════════════════════════════
MOD_ARBITRAJE = module_page("Arbitraje", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Arbitrajes</div><div class="value amber" id="arbCount">0</div></div>
  <div class="kpi"><div class="label">Max Profit</div><div class="value green" id="arbMaxProfit">0%</div></div>
  <div class="kpi"><div class="label">Profit Promedio</div><div class="value" id="arbAvgProfit">0%</div></div>
</div>
<div class="top-bar">
  <input id="arbMinProfit" type="number" value="0.5" step="0.1" style="width:70px"/>
  <button class="btn btn-primary" onclick="loadArb()">Escanear</button>
  <span id="arbStatus" style="font-size:11px;color:var(--text3)"></span>
</div>
<div class="table-wrap"><table><thead><tr><th>Partido</th><th>Liga</th><th>Profit</th><th>Resultados</th><th>Inversion</th><th>Ganancia</th></tr></thead><tbody id="arbBody"></tbody></table></div>
""", """
async function loadArb(){try{
  document.getElementById('arbStatus').textContent='Escaneando...'
  const m=document.getElementById('arbMinProfit').value
  const d=await api('/api/odds/arbitraje?min_profit='+m)
  const a=d.arbitrajes||[]
  document.getElementById('arbCount').textContent=a.length
  let maxP=0,sumP=0,h=''
  a.forEach(v=>{
    const p=parseFloat(v.profit_pct||0)
    maxP=Math.max(maxP,p);sumP+=p
    h+='<tr><td>'+v.partido+'</td><td><span class="badge badge-blue">'+(v.liga||'-')+'</span></td><td class="num" style="color:var(--green);font-weight:600">'+v.profit_pct+'%</td><td>'+v.n_resultados+'</td><td class="num">$'+(v.inversion_ejemplo||'-')+'</td><td class="num green">$'+(v.ganancia_ejemplo||'-')+'</td></tr>'
  })
  document.getElementById('arbMaxProfit').textContent=maxP.toFixed(2)+'%'
  document.getElementById('arbAvgProfit').textContent=(a.length?(sumP/a.length).toFixed(2):'0')+'%'
  const err=d.api_error||(!a.length?d.aviso:'')
  document.getElementById('arbBody').innerHTML=h||'<tr><td colspan="6" style="text-align:center;color:var(--text3);padding:20px">'+(err||'Sin arbitrajes encontrados')+'</td></tr>'
  document.getElementById('arbStatus').textContent=a.length+' arbitrajes'
  if(d.api_error)toast(d.api_error,'err')
}catch(e){toast('Error','err')}}
loadArb()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: CROSS MARKET
# ════════════════════════════════════════════════════════════════════════════
MOD_CROSS = module_page("Cross Market", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Alertas</div><div class="value amber" id="cmCount">0</div></div>
  <div class="kpi"><div class="label">Mercados</div><div class="value blue">H2H vs AH</div></div>
  <div class="kpi"><div class="label">Diferencia Max</div><div class="value green" id="cmMaxDiff">0%</div></div>
</div>
<div class="top-bar"><button class="btn btn-primary" onclick="loadCM()">Analizar Cross-Market</button></div>
<div class="table-wrap"><table><thead><tr><th>Partido</th><th>H2H Mejor</th><th>AH Mejor</th><th>Diferencia</th><th>Mercados</th></tr></thead><tbody id="cmBody"></tbody></table></div>
""", """
async function loadCM(){try{
  const d=await api('/api/odds/cross-market')
  const a=d.alertas||[]
  document.getElementById('cmCount').textContent=d.total_alertas||a.length
  let maxD=0,h=''
  a.slice(0,30).forEach(v=>{
    const diff=parseFloat(v.diferencia_pct||0)
    maxD=Math.max(maxD,diff)
    h+='<tr><td>'+(v.partido||'N/A')+'</td><td class="num">'+(v.cuota_h2h_mejor||'-')+'</td><td class="num">'+(v.cuota_ah_mejor||'-')+'</td><td class="num" style="color:var(--green);font-weight:600">'+diff.toFixed(1)+'%</td><td>'+(v.mercados_analizados||2)+'</td></tr>'
  })
  document.getElementById('cmMaxDiff').textContent=maxD.toFixed(1)+'%'
  document.getElementById('cmBody').innerHTML=h||'<tr><td colspan="5" style="text-align:center;color:var(--text3);padding:20px">Sin datos cross-market</td></tr>'
}catch(e){toast('Error','err')}}
loadCM()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: KELLY CRITERION
# ════════════════════════════════════════════════════════════════════════════
MOD_KELLY = module_page("Kelly Calculator", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Kelly Puro</div><div class="value" id="kellyPuro">0%</div></div>
  <div class="kpi"><div class="label">Kelly Ajustado</div><div class="value amber" id="kellyAjustado">0%</div></div>
  <div class="kpi"><div class="label">Apuesta Sugerida</div><div class="value green" id="kellySugerida">$0</div></div>
  <div class="kpi"><div class="label">ROI Esperado</div><div class="value blue" id="kellyRoi">0%</div></div>
</div>
<div class="card">
  <h3>Calcular Kelly</h3>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">
    <input id="kellyProb" type="number" step="0.01" placeholder="Probabilidad (0.55)" style="width:140px"/>
    <input id="kellyCuota" type="number" step="0.1" placeholder="Cuota decimal (2.0)" style="width:140px"/>
    <input id="kellyBankroll" type="number" step="1" placeholder="Bankroll ($10000)" style="width:140px"/>
    <select id="kellyFrac"><option value="0.25">1/4 Kelly</option><option value="0.5" selected>1/2 Kelly</option><option value="0.75">3/4 Kelly</option><option value="1">Full Kelly</option></select>
    <button class="btn btn-primary" onclick="calcKelly()">Calcular</button>
  </div>
  <div id="kellyResult" style="margin-top:12px;font-size:12px;color:var(--text2)"></div>
</div>
<div class="card" style="margin-top:12px">
  <h3>Guia Kelly</h3>
  <p>El criterio Kelly optimiza el crecimiento del bankroll. Usa fraccion parcial (1/4 o 1/2) para reducir varianza.</p>
</div>
""", """
async function calcKelly(){try{
  const prob=parseFloat(document.getElementById('kellyProb').value)
  const cuota=parseFloat(document.getElementById('kellyCuota').value)
  const bankroll=parseFloat(document.getElementById('kellyBankroll').value)||10000
  const frac=parseFloat(document.getElementById('kellyFrac').value)
  if(!prob||!cuota)return toast('Ingresa probabilidad y cuota','err')
  const d=await fetch('/api/kelly/calcular',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({probabilidad:prob,cuota:cuota,bankroll:bankroll,fraccion:frac})})
  const r=await d.json()
  document.getElementById('kellyPuro').textContent=(r.kelly_puro_pct||0).toFixed(2)+'%'
  document.getElementById('kellyAjustado').textContent=(r.kelly_ajustado_pct||0).toFixed(2)+'%'
  document.getElementById('k KellySugerida').textContent='$'+(r.apuesta_sugerida||0).toLocaleString()
  document.getElementById('kellyRoi').textContent=(r.roi_esperado_pct||0).toFixed(2)+'%'
  document.getElementById('kellyResult').innerHTML='<strong>Recomendacion:</strong> '+(r.recomendacion||'-')+' | <strong>Hay valor:</strong> '+(r.hay_valor?'SI':'NO')
}catch(e){toast('Error calculando Kelly','err')}}
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: VALUE ENGINE
# ════════════════════════════════════════════════════════════════════════════
MOD_VALUE_ENGINE = module_page("Value Engine", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">CLV</div><div class="value" id="veClv">--</div></div>
  <div class="kpi"><div class="label">EV</div><div class="value amber" id="veEv">--</div></div>
</div>
<div class="card">
  <h3>Analisis de Valor Profesional</h3>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">
    <input id="veProb" type="number" step="0.01" placeholder="Prob real (0.55)" style="width:130px"/>
    <input id="veCuotaApostada" type="number" step="0.1" placeholder="Cuota apostada" style="width:130px"/>
    <input id="veCuotaCierre" type="number" step="0.1" placeholder="Cuota cierre" style="width:130px"/>
    <button class="btn btn-primary" onclick="analyzeValue()">Analizar</button>
  </div>
  <div id="veResult" style="margin-top:12px"></div>
</div>
""", """
async function analyzeValue(){try{
  const prob=parseFloat(document.getElementById('veProb').value)
  const ca=parseFloat(document.getElementById('veCuotaApostada').value)
  const cc=parseFloat(document.getElementById('veCuotaCierre').value)
  if(!prob||!ca)return toast('Ingresa datos','err')
  let html=''
  if(cc){
    const clv=await api('/api/pro/clv/calcular?cuota_apostada='+ca+'&cuota_cierre='+cc+'&prob_apostada='+prob)
    html+='<div class="card"><h3>CLV (Closing Line Value)</h3><p>CLV: <strong>'+(clv.clv_pct||0).toFixed(2)+'%</strong> | Positivo: '+(clv.es_positivo?'SI':'NO')+' | Calidad: '+(clv.calidad||'-')+'</p></div>'
  }
  const ev=await api('/api/pro/montecarlo/partido?goles_esperados=2.5')
  html+='<div class="card"><h3>Monte Carlo</h3><p>Local: '+(ev.probabilidades?.local_pct||0).toFixed(1)+'% | Empate: '+(ev.probabilidades?.empate_pct||0).toFixed(1)+'% | Visitante: '+(ev.probabilidades?.visitante_pct||0).toFixed(1)+'%</p><p>Over 2.5: '+(ev.mercados_adicionales?.prob_over_2_5_pct||0).toFixed(1)+'% | Simulaciones: '+(ev.simulaciones||0)+'</p></div>'
  document.getElementById('veResult').innerHTML=html
}catch(e){toast('Error: '+e.message,'err')}}
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: COPA DEL MUNDO
# ════════════════════════════════════════════════════════════════════════════
MOD_COPA = module_page("Copa del Mundo 2026", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Partidos</div><div class="value" id="copaCount">0</div></div>
  <div class="kpi"><div class="label">Con Value</div><div class="value green" id="copaValue">0</div></div>
  <div class="kpi"><div class="label">Mejor Edge</div><div class="value amber" id="copaEdge">0%</div></div>
  <div class="kpi"><div class="label">Fase</div><div class="value blue" id="copaFase">Grupos</div></div>
</div>
<div class="top-bar">
  <button class="btn btn-primary" onclick="loadCopa()">Escanear Copa del Mundo</button>
  <button class="btn" onclick="loadCopaStandings()">Ver Posiciones</button>
  <button class="btn" onclick="loadCopaSharp()">Sharp Money WC</button>
  <span id="copaStatus" style="font-size:11px;color:var(--text3)"></span>
</div>
<div id="copaContent"></div>
""", """
async function loadCopa(){try{
  document.getElementById('copaStatus').textContent='Escaneando partidos del Mundial...'
  const d=await api('/api/odds/value-bets?deporte=soccer_fifa_world_cup&edge_minimo=1&multi=0')
  const vb=d.value_bets||[]
  document.getElementById('copaCount').textContent=d.total_partidos_analizados||0
  document.getElementById('copaValue').textContent=vb.length
  let maxE=0
  vb.forEach(v=>{const e=parseFloat(v.edge_porcentaje)||0;if(e>maxE)maxE=e})
  document.getElementById('copaEdge').textContent=maxE.toFixed(1)+'%'
  let h=''
  if(vb.length){
    h+='<div class="table-wrap"><table><thead><tr><th>Edge</th><th>Partido</th><th>Resultado</th><th>Casa</th><th>Cuota</th><th>Prob</th></tr></thead><tbody>'
    vb.forEach(v=>{
      const edge=parseFloat(v.edge_porcentaje)||0
      h+='<tr><td>'+edgeBadge(edge)+'</td><td><strong>'+v.partido+'</strong></td><td>'+v.resultado+'</td><td><span class="badge badge-blue">'+v.casa+'</span></td><td class="num">'+v.cuota+'</td><td class="num">'+(v.prob_modelo_pct?(v.prob_modelo_pct*100).toFixed(1)+'%':'-')+'</td></tr>'
    })
    h+='</tbody></table></div>'
  }else{
    h='<div class="card"><h3>Sin value bets en Copa del Mundo</h3><p>Puede que no haya partidos disponibles o que el edge sea menor al umbral.</p></div>'
  }
  document.getElementById('copaContent').innerHTML=h
  document.getElementById('copaStatus').textContent=vb.length+' value bets encontrados'
  if(d.api_error)toast(d.api_error,'err')
}catch(e){toast('Error Copa: '+e.message,'err')}}
async function loadCopaStandings(){try{
  const d=await api('/api/ligas/standings?liga=soccer_fifa_world_cup')
  let h='<div class="card"><h3>Posiciones Copa del Mundo</h3>'
  if(d.tabla&&d.tabla.length){
    h+='<div class="table-wrap"><table><thead><tr><th>#</th><th>Equipo</th><th>PJ</th><th>PG</th><th>PE</th><th>PP</th><th>Dif</th><th>Pts</th></tr></thead><tbody>'
    d.tabla.forEach((v,i)=>{
      h+='<tr><td>'+(i+1)+'</td><td><strong>'+v.equipo+'</strong></td><td class="num">'+v.pj+'</td><td class="num green">'+v.pg+'</td><td class="num amber">'+v.pe+'</td><td class="num red">'+v.pp+'</td><td class="num">'+v.dif+'</td><td class="num" style="font-weight:700">'+v.pts+'</td></tr>'
    })
    h+='</tbody></table></div>'
  }else{
    h+='<p>Sin posiciones disponibles</p>'
  }
  h+='</div>'
  document.getElementById('copaContent').innerHTML=h
}catch(e){toast('Error standings: '+e.message,'err')}}
async function loadCopaSharp(){try{
  document.getElementById('copaStatus').textContent='Escaneando sharp money en Mundial...'
  const d=await api('/api/sharp/scan?deporte=soccer_fifa_world_cup')
  const recs=d.recomendaciones||[]
  document.getElementById('copaCount').textContent=d.total_partidos||0
  document.getElementById('copaValue').textContent(d.con_señal||0)
  let bestE=0,html=''
  recs.forEach(v=>{
    const edge=parseFloat(v.edge)||0
    if(edge>bestE)bestE=edge
    const sig=v.tipo_senal||'SIN SEÑAL'
    const sel=v.seleccion||''
    const casa=v.casa_recomendada||''
    const cuota=v.cuota||0
    const accion=v.accion||''
    const conf=v.confianza||'-'
    const color=edge>=5?'border-left:4px solid var(--green)':edge>=2?'border-left:4px solid var(--amber)':'border-left:4px solid var(--border)'
    html+='<div class="card" style="'+color+'margin-bottom:8px;padding:12px">'
    html+='<div style="font-size:14px;font-weight:700;margin-bottom:4px">'+v.partido+'</div>'
    if(sig==='VALUE BET'||sig==='VALUE MENOR'){
      html+='<div style="padding:8px;background:var(--green-bg);border-radius:var(--radius-sm);font-size:12px">'
      html+='<strong style="color:var(--green)">&#9650; APOSTAR: '+sel+'</strong> en '+casa+' | Cuota: '+cuota+' | Edge: '+edge.toFixed(1)+'% | '+accion
      html+='</div>'
    }else{
      html+='<div style="font-size:11px;color:var(--text3)">Sin señal clara</div>'
    }
    html+='</div>'
  })
  document.getElementById('copaEdge').textContent=bestE.toFixed(1)+'%'
  document.getElementById('copaContent').innerHTML=html||'<div class="card"><p>Sin partidos disponibles</p></div>'
}catch(e){toast('Error: '+e.message,'err')}}
loadCopa()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: ALTA PROBABILIDAD
# ════════════════════════════════════════════════════════════════════════════
MOD_ALTA_PROB = module_page("Alta Probabilidad", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Deportes</div><div class="value green" id="apCount">0</div></div>
  <div class="kpi"><div class="label">Con Value</div><div class="value amber" id="apValue">0</div></div>
  <div class="kpi"><div class="label">Mejor Edge</div><div class="value" id="apBestEdge">0%</div></div>
</div>
<div class="card" style="margin-bottom:16px">
  <h3>Por que estos deportes son mas predecibles?</h3>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-top:8px;font-size:12px">
    <div style="padding:8px;background:var(--green-bg);border-radius:var(--radius-sm)"><strong style="color:var(--green)">Tenis ATP/WTA</strong><br/>2 resultados (sin empate). Modelo 1v1 con ELO, superficie, H2H. Acierto 65-75%.</div>
    <div style="padding:8px;background:var(--green-bg);border-radius:var(--radius-sm)"><strong style="color:var(--green)">MMA/Boxing</strong><br/>2 resultados. Analisis fisico, estilo, recencia. Menos datos pero mas claro.</div>
    <div style="padding:8px;background:var(--blue-bg);border-radius:var(--radius-sm)"><strong style="color:var(--blue)">NBA</strong><br/>Alto scoring = menos variance. Favoritos ganan 65%+. Back-to-backs predecibles.</div>
    <div style="padding:8px;background:var(--blue-bg);border-radius:var(--radius-sm)"><strong style="color:var(--blue)">NFL</strong><br/>Spreads claros en desajustes. Bye weeks, lesiones, home field importan.</div>
    <div style="padding:8px;background:var(--amber-bg);border-radius:var(--radius-sm)"><strong style="color:var(--amber)">Caballos</strong><br/>Mercado eficiente pero hay valor en challengers. Jockey + track + forma.</div>
    <div style="padding:8px;background:var(--purple-bg);border-radius:var(--radius-sm)"><strong style="color:var(--purple)">Esports</strong><br/>Mercado nuevo = inefficiencias. Datos objetivos (KDA, GPM, draft).</div>
  </div>
</div>
<div class="top-bar">
  <select id="apSport"><option value="all">Todos los deportes alta prob.</option><option value="tennis_atp_world_tour">Tenis ATP</option><option value="tennis_wta">Tenis WTA</option><option value="mma_mixed_martial_arts">MMA/UFC</option><option value="boxing_boxing">Boxing</option><option value="basketball_nba">NBA</option><option value="americanfootball_nfl">NFL</option><option value="horse_racing">Caballos</option><option value="cricket_ipl">Cricket IPL</option><option value="esports_lol_lck">LoL LCK</option><option value="motorsport_f1_race_winner">F1</option></select>
  <button class="btn btn-primary" onclick="loadAP()">Escanear Value Bets</button>
  <button class="btn" onclick="loadAPSharp()">Sharp Money</button>
  <span id="apStatus" style="font-size:11px;color:var(--text3)"></span>
</div>
<div id="apContent"></div>
""", """
async function loadAP(){try{
  document.getElementById('apStatus').textContent='Escaneando deportes de alta probabilidad...'
  const s=document.getElementById('apSport').value
  const urls=s==='all'?['tennis_atp_world_tour','tennis_wta','mma_mixed_martial_arts','boxing_boxing','basketball_nba','americanfootball_nfl','horse_racing','cricket_ipl','esports_lol_lck','motorsport_f1_race_winner']:[s]
  let totalMatches=0,totalVb=0,bestEdge=0,html=''
  for(const sport of urls){
    try{
      const d=await api('/api/odds/value-bets?deporte='+sport+'&edge_minimo=1&multi=0')
      const vb=d.value_bets||[]
      const matches=d.total_partidos_analizados||0
      totalMatches+=matches
      totalVb+=vb.length
      if(vb.length){
        const sportName=sport.replace('soccer_','').replace('_world_tour','').replace('_mixed_martial_arts','MMA').replace('_boxing','Boxing').replace('_nba','NBA').replace('_nfl','NFL').replace('horse_racing','Caballos').replace('cricket_ipl','IPL').replace('esports_lol_lck','LoL LCK').replace('motorsport_f1_race_winner','F1')
        html+='<div style="margin-bottom:12px"><div style="font-size:12px;font-weight:600;color:var(--text2);margin-bottom:4px">'+sportName+' ('+vb.length+' value bets)</div>'
        html+='<div class="table-wrap"><table><thead><tr><th>Edge</th><th>Partido</th><th>Resultado</th><th>Casa</th><th>Cuota</th></tr></thead><tbody>'
        vb.slice(0,5).forEach(v=>{
          const edge=parseFloat(v.edge_porcentaje)||0
          if(edge>bestEdge)bestEdge=edge
          html+='<tr><td>'+edgeBadge(edge)+'</td><td><strong>'+v.partido+'</strong></td><td>'+v.resultado+'</td><td><span class="badge badge-blue">'+v.casa+'</span></td><td class="num">'+v.cuota+'</td></tr>'
        })
        html+='</tbody></table></div></div>'
      }
    }catch(e){}
  }
  document.getElementById('apCount').textContent=urls.length
  document.getElementById('apValue').textContent=totalVb
  document.getElementById('apBestEdge').textContent=bestEdge.toFixed(1)+'%'
  document.getElementById('apContent').innerHTML=html||'<div class="card"><p>Sin value bets encontrados en estos deportes</p></div>'
  document.getElementById('apStatus').textContent=totalVb+' value bets de '+totalMatches+' partidos'
}catch(e){toast('Error: '+e.message,'err')}}
async function loadAPSharp(){try{
  document.getElementById('apStatus').textContent='Escaneando sharp money...'
  const d=await api('/api/sharp/scan?deporte=upcoming')
  const recs=(d.recomendaciones||[]).filter(r=>['tennis_atp_world_tour','tennis_wta','mma_mixed_martial_arts','boxing_boxing','basketball_nba','americanfootball_nfl','horse_racing','cricket_ipl','esports_lol_lck','motorsport_f1_race_winner'].some(s=>(r.liga||'').includes(s)||r.partido.toLowerCase().includes(s)))
  let html=''
  recs.slice(0,10).forEach(v=>{
    const edge=parseFloat(v.edge)||0
    const sig=v.tipo_senal||'SIN SEÑAL'
    const color=edge>=5?'border-left:4px solid var(--green)':edge>=2?'border-left:4px solid var(--amber)':'border-left:4px solid var(--border)'
    html+='<div class="card" style="'+color+'margin-bottom:8px;padding:12px">'
    html+='<div style="font-size:13px;font-weight:600">'+v.partido+'</div>'
    if(sig==='VALUE BET'||sig==='VALUE MENOR'){
      html+='<div style="font-size:12px;color:var(--green);font-weight:600;margin-top:4px">APOSTAR: '+v.seleccion+' en '+v.casa_recomendada+' | Cuota: '+v.cuota+' | Edge: '+edge.toFixed(1)+'%</div>'
    }
    html+='</div>'
  })
  document.getElementById('apContent').innerHTML=html||'<div class="card"><p>Sin señales sharp en deportes alta probabilidad</p></div>'
}catch(e){toast('Error: '+e.message,'err')}}
loadAP()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: ML PREDICTIVO
# ════════════════════════════════════════════════════════════════════════════
MOD_ML = module_page("ML Predictivo", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Modelos</div><div class="value">MLP + GBM</div></div>
  <div class="kpi"><div class="label">Features</div><div class="value" id="mlFeat">0</div></div>
  <div class="kpi"><div class="label">Estado</div><div class="value" id="mlConf">--</div></div>
  <div class="kpi"><div class="label">Entrenamiento</div><div class="value" id="mlStatus">--</div></div>
</div>
<div class="top-bar">
  <select id="mlLiga"><option value="liga_mx">Liga MX</option><option value="mls">MLS</option><option value="premier_league">Premier League</option><option value="la_liga">La Liga</option><option value="serie_a">Serie A</option><option value="bundesliga">Bundesliga</option><option value="ligue_1">Ligue 1</option></select>
  <button class="btn btn-primary" onclick="trainML()">Entrenar</button>
  <button class="btn" onclick="loadML()">Actualizar</button>
  <button class="btn" onclick="loadPerf()">Performance</button>
</div>
<div id="mlTrainStatus" style="font-size:12px;color:var(--text2);margin-bottom:8px"></div>
<div class="tabs"><div class="tab active" onclick="showTab('features',this)">Features</div><div class="tab" onclick="showTab('perf',this)">Performance</div></div>
<div id="tab-features"><div class="table-wrap"><table><thead><tr><th>Feature</th><th>Importancia</th><th>Barra</th></tr></thead><tbody id="mlBody"></tbody></table></div></div>
<div id="tab-perf" style="display:none"><div class="table-wrap"><table><thead><tr><th>Metrica</th><th>Valor</th></tr></thead><tbody id="mlPerfBody"></tbody></table></div></div>
""", """
function showTab(id,el){document.querySelectorAll('.tabs .tab').forEach(t=>t.classList.remove('active'));el.classList.add('active');document.querySelectorAll('[id^=tab-]').forEach(t=>t.style.display='none');document.getElementById('tab-'+id).style.display='block'}
async function loadML(){try{
  const l=document.getElementById('mlLiga').value
  const d=await api('/api/ml/v2/features?liga='+l)
  const f=d.features||[]
  document.getElementById('mlFeat').textContent=f.length
  document.getElementById('mlConf').textContent=f.length?'Entrenado':'Sin datos'
  document.getElementById('mlConf').className='value '+(f.length?'green':'red')
  let h=''
  f.slice(0,20).forEach(v=>{
    const pct=((v.importance||0)*100)
    h+='<tr><td>'+v.feature_name+'</td><td class="num">'+pct.toFixed(1)+'%</td><td><div class="progress-bar" style="width:150px"><div class="fill" style="width:'+pct+'%;background:var(--primary)"></div></div></td></tr>'
  })
  document.getElementById('mlBody').innerHTML=h||'<tr><td colspan="3" style="text-align:center;color:var(--text3);padding:20px">Entrena modelos primero</td></tr>'
}catch(e){toast('Error','err')}}
async function trainML(){try{
  document.getElementById('mlTrainStatus').textContent='Entrenando modelos...'
  await api('/api/ml/v2/train')
  document.getElementById('mlTrainStatus').textContent='Entrenamiento completado'
  loadML()
}catch(e){toast('Error','err')}}
async function loadPerf(){try{
  const d=await api('/api/ml/v2/performance')
  let h=''
  Object.entries(d).forEach(([k,v])=>{h+='<tr><td>'+k+'</td><td>'+v+'</td></tr>'})
  document.getElementById('mlPerfBody').innerHTML=h||'<tr><td colspan="2">Sin datos</td></tr>'
}catch(e){toast('Error','err')}}
loadML()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: BACKTESTING
# ════════════════════════════════════════════════════════════════════════════
MOD_BACKTESTING = module_page("Backtesting", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Partidos</div><div class="value" id="btTotal">0</div></div>
  <div class="kpi"><div class="label">Accuracy</div><div class="value amber" id="btAcc">0%</div></div>
  <div class="kpi"><div class="label">Correctos</div><div class="value green" id="btCorrect">0</div></div>
  <div class="kpi"><div class="label">Incorrectos</div><div class="value red" id="btWrong">0</div></div>
</div>
<div class="top-bar"><button class="btn btn-primary" onclick="loadBT()">Ejecutar Backtest</button></div>
<div class="table-wrap"><table><thead><tr><th>Local</th><th>Visitante</th><th>Prediccion</th><th>Confianza</th><th>Resultado</th></tr></thead><tbody id="btBody"></tbody></table></div>
""", """
async function loadBT(){try{
  const d=await api('/api/backtest')
  const res=d.resumen||{}
  document.getElementById('btTotal').textContent=d.n_partidos||0
  document.getElementById('btAcc').textContent=(res.accuracy_pct||0).toFixed(1)+'%'
  document.getElementById('btCorrect').textContent=res.correctos||0
  document.getElementById('btWrong').textContent=res.incorrectos||0
  const preds=d.ultimas_20_predicciones||[]
  let h2=''
  if(d.aviso)h2+='<tr><td colspan="5" style="color:var(--amber)">'+d.aviso+'</td></tr>'
  preds.slice(0,20).forEach(v=>{
    const parts=(v.partido||'').split(' vs ')
    const cls=v.correcto===1?'green':v.correcto===0?'red':''
    h2+='<tr><td>'+parts[0]+'</td><td>'+parts[1]+'</td><td><span class="badge badge-blue">'+(v.prediccion||'-')+'</span></td><td>'+(v.confianza||'-')+'%</td><td class="'+cls+'">'+(v.correcto===1?'CORRECTO':v.correcto===0?'INCORRECTO':'-')+'</td></tr>'
  })
  document.getElementById('btBody').innerHTML=h2||'<tr><td colspan="5" style="text-align:center;color:var(--text3);padding:20px">Ejecuta un backtest</td></tr>'
}catch(e){toast('Error','err')}}
loadBT()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: NLP / NOTICIAS
# ════════════════════════════════════════════════════════════════════════════
MOD_NLP = module_page("Noticias & Lesiones", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Noticias</div><div class="value blue" id="nlpCount">0</div></div>
  <div class="kpi"><div class="label">Alertas Edge</div><div class="value amber" id="nlpAlerts">0</div></div>
  <div class="kpi"><div class="label">Fuente</div><div class="value teal" id="nlpSource">—</div></div>
</div>
<div class="top-bar">
  <button class="btn btn-primary" onclick="loadNLP()">Escanear Noticias</button>
  <button class="btn" onclick="loadScan()">NLP Completo</button>
  <span id="nlpStatus" style="font-size:11px;color:var(--text3)"></span>
</div>
<div id="nlpResults"></div>
""", """
async function loadNLP(){try{
  document.getElementById('nlpStatus').textContent='Escaneando noticias...'
  const d=await api('/api/nlp/noticias')
  const ns=d.noticias||[]
  document.getElementById('nlpCount').textContent=ns.length
  const fuentes=d.fuentes||(ns.length?ns.map(n=>n.fuentes||'?').filter((v,i,a)=>a.indexOf(v)===i):[])
  document.getElementById('nlpSource').textContent=(Array.isArray(fuentes)?fuentes.join(', '):(fuentes||'?'))
  let h=''
  ns.forEach(n=>{
    let alertHtml=''
    if(n.alertas&&n.alertas.length)alertHtml='<div class="alert">&#9888; '+n.alertas.join(', ')+'</div>'
    const fecha=n.fecha?new Date(n.fecha):null
    const fechaStr=fecha?fecha.toLocaleDateString('es-MX',{day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'}):''
    h+='<div class="news-item"><div class="title">'+n.titulo+'</div><div class="meta">'+(n.desc||'').slice(0,120)+'</div><div style="font-size:10px;color:var(--text3);margin-top:2px">'+fechaStr+' — '+(n.fuente||'')+'</div>'+alertHtml+'</div>'
  })
  document.getElementById('nlpResults').innerHTML=h||'<div class="empty"><p>Sin noticias recientes</p></div>'
  document.getElementById('nlpStatus').textContent=ns.length+' noticias'
}catch(e){toast('Error NLP: '+e.message,'err')}}
async function loadScan(){try{
  const d=await api('/api/nlp/scan')
  const msg=d.es_demo?'Datos DEMO — configura APIs para datos reales':(d.tiene_edge?'Alertas edge detectadas!':'Sin alertas de edge')
  toast(msg,'info')
}catch(e){toast('Error scan: '+e.message,'err')}}
loadNLP()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: MONTE CARLO
# ════════════════════════════════════════════════════════════════════════════
MOD_MONTECARLO = module_page("Monte Carlo", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Local</div><div class="value" id="mcLocal">0%</div></div>
  <div class="kpi"><div class="label">Empate</div><div class="value amber" id="mcEmpate">0%</div></div>
  <div class="kpi"><div class="label">Visitante</div><div class="value" id="mcVisit">0%</div></div>
  <div class="kpi"><div class="label">Over 2.5</div><div class="value green" id="mcOver">0%</div></div>
</div>
<div class="card">
  <h3>Simulacion Monte Carlo</h3>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">
    <input id="mcGoles" type="number" step="0.1" value="2.5" placeholder="Goles esperados" style="width:140px"/>
    <button class="btn btn-primary" onclick="loadMC()">Simular</button>
  </div>
</div>
<div class="chart-box"><canvas id="mcChart"></canvas></div>
<div class="table-wrap"><table><thead><tr><th>Mercado</th><th>Probabilidad</th><th>Cuota Justa</th></tr></thead><tbody id="mcBody"></tbody></table></div>
""", """
let mcChart=null
async function loadMC(){try{
  const g=document.getElementById('mcGoles').value||2.5
  const d=await api('/api/pro/montecarlo/partido?goles_esperados='+g)
  const p=d.probabilidades||{}
  const c=d.cuotas_justas_sin_vig||{}
  const m=d.mercados_adicionales||{}
  document.getElementById('mcLocal').textContent=(p.local_pct||0).toFixed(1)+'%'
  document.getElementById('mcEmpate').textContent=(p.empate_pct||0).toFixed(1)+'%'
  document.getElementById('mcVisit').textContent=(p.visitante_pct||0).toFixed(1)+'%'
  document.getElementById('mcOver').textContent=(m.prob_over_2_5_pct||0).toFixed(1)+'%'
  let h=''
  h+='<tr><td>Local</td><td>'+(p.local_pct||0).toFixed(1)+'%</td><td>'+(c.local||0).toFixed(2)+'</td></tr>'
  h+='<tr><td>Empate</td><td>'+(p.empate_pct||0).toFixed(1)+'%</td><td>'+(c.empate||0).toFixed(2)+'</td></tr>'
  h+='<tr><td>Visitante</td><td>'+(p.visitante_pct||0).toFixed(1)+'%</td><td>'+(c.visitante||0).toFixed(2)+'</td></tr>'
  h+='<tr><td>Over 2.5</td><td>'+(m.prob_over_2_5_pct||0).toFixed(1)+'%</td><td>-</td></tr>'
  h+='<tr><td>Over 1.5</td><td>'+(m.prob_over_1_5_pct||0).toFixed(1)+'%</td><td>-</td></tr>'
  document.getElementById('mcBody').innerHTML=h
  if(mcChart)mcChart.destroy()
  mcChart=new Chart(document.getElementById('mcChart'),{type:'doughnut',data:{labels:['Local','Empate','Visitante'],datasets:[{data:[p.local_pct||0,p.empate_pct||0,p.visitante_pct||0],backgroundColor:['#4f46e5','#d97706','#059669'],borderWidth:0}]},options:{responsive:true,plugins:{legend:{position:'bottom',labels:{color:'var(--text2)',font:{size:11}}}}}})
}catch(e){toast('Error','err')}}
loadMC()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: BANKROLL
# ════════════════════════════════════════════════════════════════════════════
MOD_BANKROLL = module_page("Bankroll", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Bankroll Actual</div><div class="value" id="brActual">$0</div></div>
  <div class="kpi"><div class="label">Apuestas</div><div class="value amber" id="brTotal">0</div></div>
  <div class="kpi"><div class="label">Win Rate</div><div class="value green" id="brWinRate">0%</div></div>
  <div class="kpi"><div class="label">Ganancia Neta</div><div class="value" id="brGanancia">$0</div></div>
  <div class="kpi"><div class="label">Riesgo Ruina</div><div class="value red" id="brRuin">--</div></div>
</div>
<div class="tabs"><div class="tab active" onclick="showBrTab('chart',this)">Grafica</div><div class="tab" onclick="showBrTab('history',this)">Historial</div><div class="tab" onclick="showBrTab('risk',this)">Riesgo</div></div>
<div id="brtab-chart"><div class="chart-box"><canvas id="brChart"></canvas></div></div>
<div id="brtab-history" style="display:none"><div class="table-wrap"><table><thead><tr><th>Fecha</th><th>Evento</th><th>Bankroll</th></tr></thead><tbody id="brBody"></tbody></table></div></div>
<div id="brtab-risk" style="display:none"><div class="card"><div id="brRiskInfo">Cargando...</div></div></div>
""", """
function showBrTab(id,el){document.querySelectorAll('.tabs .tab').forEach(t=>t.classList.remove('active'));el.classList.add('active');document.querySelectorAll('[id^=brtab-]').forEach(t=>t.style.display='none');document.getElementById('brtab-'+id).style.display='block'}
let brChart=null
async function loadBR(){try{
  const d=await api('/api/dashboard/rendimiento')
  const g=d.general||{},b=d.bankroll||{},h=b.history||[]
  document.getElementById('brActual').textContent='$'+(b.actual||0).toLocaleString()
  document.getElementById('brTotal').textContent=g.total_apuestas||0
  document.getElementById('brWinRate').textContent=(g.win_rate||0)+'%'
  document.getElementById('brGanancia').textContent='$'+(g.ganancia_neta||0).toLocaleString()
  let hh=''
  h.slice().reverse().slice(-30).forEach(v=>{
    hh+='<tr><td>'+(v.fecha||'').slice(0,10)+'</td><td>'+v.evento+'</td><td class="num">$'+v.bankroll+'</td></tr>'
  })
  document.getElementById('brBody').innerHTML=hh||'<tr><td colspan="3">Sin historial</td></tr>'
  if(brChart)brChart.destroy()
  brChart=new Chart(document.getElementById('brChart'),{type:'line',data:{labels:h.map(v=>(v.fecha||'').slice(5,10)),datasets:[{label:'Bankroll',data:h.map(v=>v.bankroll),borderColor:'#4f46e5',backgroundColor:'rgba(79,70,229,0.05)',fill:true,tension:.4,pointRadius:1,borderWidth:2}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:{color:'rgba(0,0,0,0.04)'},ticks:{color:'var(--text3)',font:{size:10}}},y:{grid:{color:'rgba(0,0,0,0.04)'},ticks:{color:'var(--text3)',font:{size:10}}}}}})
  try{const ru=await api('/api/bankroll/riesgo-ruina');document.getElementById('brRuin').textContent=(ru.probabilidad_ruina||0).toFixed(2)+'%';document.getElementById('brRiskInfo').innerHTML='<p>Riesgo de ruina: <strong>'+(ru.probabilidad_ruina||0).toFixed(2)+'%</strong></p><p>Recomendacion: '+(ru.recomendacion||'-')+'</p>'}catch(e){}
}catch(e){toast('Error','err')}}
loadBR()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: SIMULACION
# ════════════════════════════════════════════════════════════════════════════
MOD_SIMULACION = module_page("Simulacion", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Trades</div><div class="value" id="simTotal">0</div></div>
  <div class="kpi"><div class="label">Ganadas</div><div class="value green" id="simGanadas">0</div></div>
  <div class="kpi"><div class="label">Perdidas</div><div class="value red" id="simPerdidas">0</div></div>
  <div class="kpi"><div class="label">PnL</div><div class="value amber" id="simPnl">$0</div></div>
</div>
<div class="top-bar"><button class="btn" onclick="verifySim()">Verificar Pendientes</button></div>
<div class="table-wrap"><table><thead><tr><th>Partido</th><th>Seleccion</th><th>Cuota</th><th>Stake</th><th>Resultado</th><th>PnL</th></tr></thead><tbody id="simBody"></tbody></table></div>
""", """
async function loadSim(){try{
  const d=await api('/api/simulacion/status')
  document.getElementById('simTotal').textContent=d.total_trades||d.total||0
  document.getElementById('simGanadas').textContent=d.ganadas||0
  document.getElementById('simPerdidas').textContent=d.perdidas||0
  document.getElementById('simPnl').textContent='$'+(d.pnl_total||0).toLocaleString()
  const t=d.ultimos_trades||d.trades||[]
  let h=''
  t.forEach(v=>{
    const cls=v.resultado==='ganada'?'green':v.resultado==='perdida'?'red':'amber'
    h+='<tr><td>'+v.partido+'</td><td>'+v.seleccion+'</td><td class="num">'+v.cuota+'</td><td class="num">$'+(v.stake_simulado||v.stake||0)+'</td><td class="'+cls+'">'+(v.resultado||'pendiente')+'</td><td class="num '+(v.pnl>=0?'green':'red')+'">$'+(v.pnl||0)+'</td></tr>'
  })
  document.getElementById('simBody').innerHTML=h||'<tr><td colspan="6">Sin trades simulados</td></tr>'
}catch(e){toast('Error','err')}}
async function verifySim(){try{await api('/api/simulacion/verificar');toast('Verificado','info');loadSim()}catch(e){toast('Error','err')}}
loadSim()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: CONTABILIDAD
# ════════════════════════════════════════════════════════════════════════════
MOD_CONTABILIDAD = module_page("Contabilidad", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Transacciones</div><div class="value" id="conCount">0</div></div>
  <div class="kpi"><div class="label">Ganadas</div><div class="value green" id="conGanadas">0</div></div>
  <div class="kpi"><div class="label">Perdidas</div><div class="value red" id="conPerdidas">0</div></div>
  <div class="kpi"><div class="label">Neto</div><div class="value amber" id="conNeto">$0</div></div>
</div>
<div class="top-bar"><button class="btn" onclick="syncCont()">Sync Bets</button></div>
<div class="chart-box"><canvas id="conChart"></canvas></div>
<div class="table-wrap"><table><thead><tr><th>Estrategia</th><th>Total</th><th>Ganadas</th><th>Perdidas</th><th>Neto</th></tr></thead><tbody id="conBody"></tbody></table></div>
""", """
let conChart=null
async function loadCon(){try{
  const d=await api('/api/contabilidad/pnl-estrategia')
  const arr=Array.isArray(d)?d:(d.pnl||d.data||[])
  document.getElementById('conCount').textContent=arr.reduce((s,v)=>s+(v.total||0),0)
  let g=0,p=0,n=0,h=''
  arr.forEach(v=>{
    g+=v.ganadas||0;p+=v.perdidas||0;n+=v.neto||0
    h+='<tr><td>'+(v.estrategia||'general')+'</td><td>'+(v.total||0)+'</td><td class="green">'+(v.ganadas||0)+'</td><td class="red">'+(v.perdidas||0)+'</td><td class="'+((v.neto||0)>=0?'green':'red')+'">$'+(v.neto||0)+'</td></tr>'
  })
  document.getElementById('conGanadas').textContent=g
  document.getElementById('conPerdidas').textContent=p
  document.getElementById('conNeto').textContent='$'+n.toLocaleString()
  document.getElementById('conBody').innerHTML=h||'<tr><td colspan="5">Sin datos contables</td></tr>'
  if(conChart)conChart.destroy()
  conChart=new Chart(document.getElementById('conChart'),{type:'bar',data:{labels:arr.map(v=>v.estrategia||'general'),datasets:[{label:'Ganado',data:arr.map(v=>v.ganadas||0),backgroundColor:'rgba(5,150,105,0.7)',borderRadius:4},{label:'Perdido',data:arr.map(v=>v.perdidas||0),backgroundColor:'rgba(220,38,38,0.7)',borderRadius:4}]},options:{responsive:true,plugins:{legend:{position:'bottom',labels:{color:'var(--text2)',font:{size:10}}}},scales:{x:{grid:{display:false}},y:{grid:{color:'rgba(0,0,0,0.04)'}}}}})
}catch(e){toast('Error','err')}}
async function syncCont(){try{await api('/api/contabilidad/sync');toast('Sync completado','info');loadCon()}catch(e){toast('Error','err')}}
loadCon()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: JOURNAL
# ════════════════════════════════════════════════════════════════════════════
MOD_JOURNAL = module_page("Trading Journal", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Acciones (7d)</div><div class="value" id="jrTotal">0</div></div>
  <div class="kpi"><div class="label">Tipos</div><div class="value" id="jrTipos">0</div></div>
</div>
<div class="top-bar">
  <button class="btn" onclick="exportCSV()">Exportar CSV</button>
  <button class="btn" onclick="autoLog()">Auto-Log</button>
  <button class="btn" onclick="loadJR()">Actualizar</button>
</div>
<div class="table-wrap"><table><thead><tr><th>Fecha</th><th>Accion</th><th>Partido</th><th>Detalle</th><th>PnL</th></tr></thead><tbody id="jrBody"></tbody></table></div>
""", """
async function loadJR(){try{
  const d=await api('/api/journal/resumen')
  const t=d.por_tipo||{},u=d.ultimas_acciones||[]
  document.getElementById('jrTotal').textContent=d.total_acciones||0
  document.getElementById('jrTipos').textContent=Object.keys(t).length
  let h=''
  u.forEach(v=>{
    h+='<tr><td>'+(v.fecha||'').slice(0,10)+'</td><td><span class="badge badge-blue">'+v.tipo+'</span></td><td>'+(v.partido||'-')+'</td><td>'+v.estrategia+' '+(v.resultado||'')+'</td><td class="num '+(v.pnl>=0?'green':'red')+'">$'+(v.pnl||0)+'</td></tr>'
  })
  document.getElementById('jrBody').innerHTML=h||'<tr><td colspan="5">Sin actividad registrada</td></tr>'
}catch(e){toast('Error','err')}}
function exportCSV(){window.open('/api/journal/export-csv','_blank')}
async function autoLog(){try{await api('/api/journal/auto-log');toast('Auto-log completado','info');loadJR()}catch(e){toast('Error','err')}}
loadJR()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: MERCADOS MULTI
# ════════════════════════════════════════════════════════════════════════════
MOD_MERCADOS = module_page("Mercados Multi", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Value Bets</div><div class="value amber" id="mrcVb">0</div></div>
  <div class="kpi"><div class="label">Cuotas</div><div class="value" id="mrcCuotas">0</div></div>
</div>
<div class="card">
  <h3>Analisis Multi-Mercado</h3>
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px">
    <input id="mrcPartido" type="text" placeholder="Ej: Chivas vs America" style="width:220px"/>
    <button class="btn btn-primary" onclick="loadMrc()">Analizar</button>
  </div>
</div>
<div class="tabs"><div class="tab active" onclick="showMrcTab('vb',this)">Value Bets</div><div class="tab" onclick="showMrcTab('arb',this)">Arbitraje</div></div>
<div id="mrctab-vb"><div class="table-wrap"><table><thead><tr><th>Mercado</th><th>Seleccion</th><th>Cuota</th><th>Edge</th><th>EV</th></tr></thead><tbody id="mrcVbBody"></tbody></table></div></div>
<div id="mrctab-arb" style="display:none"><div class="table-wrap"><table><thead><tr><th>Mercado</th><th>Seleccion</th><th>Cuota</th><th>Stake</th></tr></thead><tbody id="mrcArbBody"></tbody></table></div></div>
""", """
function showMrcTab(id,el){document.querySelectorAll('.tabs .tab').forEach(t=>t.classList.remove('active'));el.classList.add('active');document.querySelectorAll('[id^=mrctab-]').forEach(t=>t.style.display='none');document.getElementById('mrctab-'+id).style.display='block'}
async function loadMrc(){try{
  const p=document.getElementById('mrcPartido').value
  if(!p)return toast('Ingresa un partido','err')
  const vb=await api('/api/mercados/value-bets-mercados?partido='+encodeURIComponent(p))
  document.getElementById('mrcVb').textContent=(vb.value_bets||[]).length
  document.getElementById('mrcCuotas').textContent=vb.cuotas_analizadas||0
  let h=''
  (vb.value_bets||[]).forEach(v=>{
    h+='<tr><td>'+(v.mercado||'-')+'</td><td>'+v.seleccion+'</td><td class="num">'+v.cuota+'</td><td class="num" style="color:var(--green)">'+(v.edge||0).toFixed(1)+'%</td><td class="num">'+(v.ev||0).toFixed(2)+'</td></tr>'
  })
  document.getElementById('mrcVbBody').innerHTML=h||'<tr><td colspan="5">Sin value bets para este partido</td></tr>'
  try{
    const ar=await api('/api/mercados/arbitraje?partido='+encodeURIComponent(p))
    let ha=''
    (ar.arbitrajes||[]).forEach(v=>{
      ha+='<tr><td>'+(v.mercado||'-')+'</td><td>'+v.seleccion+'</td><td class="num">'+v.cuota+'</td><td class="num">$'+(v.stake||0)+'</td></tr>'
    })
    document.getElementById('mrcArbBody').innerHTML=ha||'<tr><td colspan="4">Sin arbitraje</td></tr>'
  }catch(e){}
}catch(e){toast('Error','err')}}
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: RATING CASAS
# ════════════════════════════════════════════════════════════════════════════
MOD_BOOKMAKERS = module_page("Rating Casas", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Casas</div><div class="value" id="bmCount">0</div></div>
  <div class="kpi"><div class="label">Mejor Overround</div><div class="value green" id="bmBestOver">0</div></div>
</div>
<div class="top-bar">
  <button class="btn btn-primary" onclick="scanBM()">Escanear Casas</button>
  <span id="bmStatus" style="font-size:12px;color:var(--text2)"></span>
</div>
<div class="table-wrap"><table><thead><tr><th>#</th><th>Casa</th><th>Overround</th><th>CLV</th><th>Apariciones</th></tr></thead><tbody id="bmBody"></tbody></table></div>
""", """
async function loadBM(){try{
  const d=await api('/api/bookmakers/rating')
  const r=(d.ratings||[]).sort((a,b)=>(a.avg_overround||99)-(b.avg_overround||99))
  document.getElementById('bmCount').textContent=r.length
  document.getElementById('bmBestOver').textContent=r.length?(Math.min(...r.map(v=>v.avg_overround||99))).toFixed(2)+'%':'0'
  let h=''
  r.forEach((v,i)=>{
    h+='<tr><td>'+(i+1)+'</td><td><strong>'+v.bookmaker+'</strong></td><td class="num">'+(v.avg_overround||0).toFixed(2)+'%</td><td class="num">'+(v.avg_clv||0).toFixed(4)+'</td><td class="num">'+v.apariciones+'</td></tr>'
  })
  document.getElementById('bmBody').innerHTML=h||'<tr><td colspan="5">Escanear casas primero</td></tr>'
}catch(e){toast('Error','err')}}
async function scanBM(){try{document.getElementById('bmStatus').textContent='Escaneando...';await api('/api/bookmakers/scan');document.getElementById('bmStatus').textContent='Listo';loadBM()}catch(e){toast('Error','err')}}
loadBM()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: PROGOL OPTIMIZER
# ════════════════════════════════════════════════════════════════════════════
MOD_PROGOL = module_page("Progol Optimizer", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Jornada</div><div class="value" id="pgJornada">--</div></div>
  <div class="kpi"><div class="label">Partidos</div><div class="value blue" id="pgCount">0</div></div>
  <div class="kpi"><div class="label">Quinielas</div><div class="value amber" id="pgQuin">0</div></div>
</div>
<div class="top-bar">
  <button class="btn btn-primary" onclick="loadProgol()">Cargar Jornada</button>
  <button class="btn" onclick="loadOptQ()">Quiniela Simple</button>
  <button class="btn" onclick="loadOptD()">Diversificada</button>
  <button class="btn" onclick="loadOptC()">Max Cobertura</button>
</div>
<div class="table-wrap"><table><thead><tr><th>#</th><th>Local</th><th>Visitante</th><th>ELO L</th><th>ELO V</th><th>Pronostico</th></tr></thead><tbody id="pgBody"></tbody></table></div>
<div id="pgOptResult" style="margin-top:12px"></div>
""", """
async function loadProgol(){try{
  const d=await api('/api/progol/jornada')
  const p=d.partidos||d||[]
  document.getElementById('pgJornada').textContent=d.jornada||'Actual'
  document.getElementById('pgCount').textContent=(Array.isArray(p)?p:[]).length
  let h=''
  ;(Array.isArray(p)?p:[]).forEach((v,i)=>{
    h+='<tr><td>'+(i+1)+'</td><td>'+v.local+'</td><td>'+v.visitante+'</td><td class="num">'+(v.elo_local||'-')+'</td><td class="num">'+(v.elo_visitante||'-')+'</td><td><span class="badge badge-blue">'+(v.pronostico||'-')+'</span></td></tr>'
  })
  document.getElementById('pgBody').innerHTML=h||'<tr><td colspan="6">Sin datos de jornada</td></tr>'
}catch(e){toast('Error','err')}}
async function loadOptQ(){try{const d=await api('/api/progol/optimizar/quiniela-simple');document.getElementById('pgOptResult').innerHTML='<div class="card"><h3>Quiniela Simple</h3><pre style="font-size:12px;white-space:pre-wrap">'+JSON.stringify(d,null,2)+'</pre></div>'}catch(e){toast('Error','err')}}
async function loadOptD(){try{const d=await api('/api/progol/optimizar/diversificada');const q=d.quinielas||[];document.getElementById('pgQuin').textContent=q.length;let h='<div class="card"><h3>Quinielas Diversificadas ('+q.length+')</h3>';q.forEach((v,i)=>{h+='<p><strong>#'+(i+1)+'</strong>: '+JSON.stringify(v)+'</p>'});h+='</div>';document.getElementById('pgOptResult').innerHTML=h}catch(e){toast('Error','err')}}
async function loadOptC(){try{const d=await api('/api/progol/optimizar/maxima-cobertura');document.getElementById('pgOptResult').innerHTML='<div class="card"><h3>Maxima Cobertura</h3><pre style="font-size:12px;white-space:pre-wrap">'+JSON.stringify(d,null,2)+'</pre></div>'}catch(e){toast('Error','err')}}
loadProgol()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: CUENTAS
# ════════════════════════════════════════════════════════════════════════════
MOD_CUENTAS = module_page("Cuentas", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Cuentas</div><div class="value" id="cuCount">0</div></div>
  <div class="kpi"><div class="label">Salud Promedio</div><div class="value green" id="cuHealth">--</div></div>
</div>
<div class="top-bar">
  <button class="btn btn-primary" onclick="loadCuentas()">Listar Cuentas</button>
  <button class="btn" onclick="loadRotacion()">Rotacion</button>
  <button class="btn" onclick="loadCamuflaje()">Camuflaje</button>
</div>
<div id="cuContent"></div>
""", """
async function loadCuentas(){try{
  const d=await api('/api/cuentas/listar')
  const c=d.cuentas||[]
  document.getElementById('cuCount').textContent=c.length
  let h='<div class="table-wrap"><table><thead><tr><th>Casa</th><th>Estado</th><th>Limite</th><th>Apuestas</th><th>Health</th></tr></thead><tbody>'
  c.forEach(v=>{
    const hc=v.health_score>=80?'green':v.health_score>=50?'amber':'red'
    h+='<tr><td><strong>'+v.casa+'</strong></td><td><span class="badge badge-'+(v.estado==='activa'?'green':'red')+'">'+v.estado+'</span></td><td class="num">$'+(v.limite_diario||0)+'</td><td class="num">'+(v.apuestas_hoy||0)+'</td><td class="'+hc+'">'+(v.health_score||'-')+'/100</td></tr>'
  })
  h+='</tbody></table></div>'
  document.getElementById('cuContent').innerHTML=h||'<div class="empty"><p>Sin cuentas registradas</p></div>'
}catch(e){toast('Error','err')}}
async function loadRotacion(){try{
  const d=await api('/api/cuentas/rotacion?monto=1000')
  let h='<div class="card"><h3>Distribucion recomendada</h3><p>Total: $'+(d.monto_total||0)+'</p><div class="table-wrap"><table><thead><tr><th>Casa</th><th>Health</th><th>Monto</th><th>%</th></tr></thead><tbody>'
  ;(d.distribucion||[]).forEach(v=>{
    h+='<tr><td>'+v.casa+'</td><td>'+(v.health_score||0)+'</td><td class="num">$'+(v.monto||0)+'</td><td class="num">'+(v.pct_del_total||0)+'%</td></tr>'
  })
  h+='</tbody></table></div></div>'
  document.getElementById('cuContent').innerHTML=h
}catch(e){toast('Error','err')}}
async function loadCamuflaje(){try{
  const d=await api('/api/cuentas/camuflaje/plan')
  document.getElementById('cuContent').innerHTML='<div class="card"><h3>Plan de Camuflaje</h3><pre style="font-size:12px;white-space:pre-wrap">'+JSON.stringify(d,null,2)+'</pre></div>'
}catch(e){toast('Error','err')}}
loadCuentas()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: PORTFOLIO
# ════════════════════════════════════════════════════════════════════════════
MOD_PORTFOLIO = module_page("Portfolio", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Posiciones</div><div class="value" id="pfPos">0</div></div>
  <div class="kpi"><div class="label">Exposure</div><div class="value amber" id="pfExp">$0</div></div>
  <div class="kpi"><div class="label">PnL Abierto</div><div class="value green" id="pfPnl">$0</div></div>
</div>
<div class="top-bar">
  <button class="btn btn-primary" onclick="loadPF()">Estado Portfolio</button>
  <button class="btn" onclick="recomendar()">Recomendar Apuesta</button>
</div>
<div id="pfContent"></div>
""", """
async function loadPF(){try{
  const d=await api('/api/portfolio/status')
  document.getElementById('pfPos').textContent=d.posiciones_abiertas||0
  document.getElementById('pfExp').textContent='$'+(d.exposure_total||0).toLocaleString()
  document.getElementById('pfPnl').textContent='$'+(d.pnl_abierto||0).toLocaleString()
  document.getElementById('pfContent').innerHTML='<div class="card"><pre style="font-size:12px;white-space:pre-wrap">'+JSON.stringify(d,null,2)+'</pre></div>'
}catch(e){toast('Error','err')}}
async function recomendar(){try{
  const d=await api('/api/portfolio/recomendar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({})})
  toast('Recomendacion: $'+(d.monto_sugerido||0)+' en '+(d.apuesta||'-'),'info')
}catch(e){toast('Error','err')}}
loadPF()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: RENDIMIENTO
# ════════════════════════════════════════════════════════════════════════════
MOD_RENDIMIENTO = module_page("Rendimiento", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Total Apuestas</div><div class="value" id="rpTotal">0</div></div>
  <div class="kpi"><div class="label">Win Rate</div><div class="value amber" id="rpWinRate">0%</div></div>
  <div class="kpi"><div class="label">Sharpe</div><div class="value" id="rpSharpe">0</div></div>
  <div class="kpi"><div class="label">ROI</div><div class="value green" id="rpRoi">0%</div></div>
  <div class="kpi"><div class="label">Predicciones</div><div class="value purple" id="rpPreds">0</div></div>
  <div class="kpi"><div class="label">Accuracy</div><div class="value teal" id="rpAcc">0%</div></div>
</div>
<div class="chart-box"><canvas id="rpChart"></canvas></div>
<div class="table-wrap"><table><thead><tr><th>Deporte</th><th>Total</th><th>Ganadas</th><th>Perdidas</th><th>Neto</th></tr></thead><tbody id="rpBody"></tbody></table></div>
""", """
let rpChart=null
async function loadRP(){try{
  const d=await api('/api/dashboard/rendimiento')
  const g=d.general||{},p=d.por_deporte||[],b=d.bankroll||{},h=b.history||[],pred=d.predicciones||{}
  document.getElementById('rpTotal').textContent=g.total_apuestas||0
  document.getElementById('rpWinRate').textContent=(g.win_rate||0)+'%'
  document.getElementById('rpSharpe').textContent=(g.sharpe_ratio||0).toFixed(2)
  document.getElementById('rpRoi').textContent=(g.roi_pct||0)+'%'
  document.getElementById('rpPreds').textContent=pred.total||0
  document.getElementById('rpAcc').textContent=(pred.accuracy||0)+'%'
  let ht=''
  p.forEach(v=>{
    const net=v.ganancia_neta||0
    ht+='<tr><td>'+v.liga+'</td><td class="num">'+v.total+'</td><td class="num green">'+v.ganadas+'</td><td class="num red">'+v.perdidas+'</td><td class="num '+(net>=0?'green':'red')+'">$'+net+'</td></tr>'
  })
  document.getElementById('rpBody').innerHTML=ht||'<tr><td colspan="5">Sin datos</td></tr>'
  if(rpChart)rpChart.destroy()
  rpChart=new Chart(document.getElementById('rpChart'),{type:'bar',data:{labels:p.map(v=>v.liga||'?'),datasets:[{label:'Ganancia',data:p.map(v=>v.ganancia_neta||0),backgroundColor:p.map(v=>(v.ganancia_neta||0)>=0?'rgba(5,150,105,0.7)':'rgba(220,38,38,0.7)'),borderRadius:6,barThickness:24}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:{display:false},ticks:{color:'var(--text3)',font:{size:10}}},y:{grid:{color:'rgba(0,0,0,0.04)'},ticks:{color:'var(--text3)',font:{size:10}}}}}})
}catch(e){toast('Error','err')}}
loadRP()
""")

# ════════════════════════════════════════════════════════════════════════════
# MODULE: MODELOS AVANZADOS
# ════════════════════════════════════════════════════════════════════════════
MOD_BRAIN = module_page("Agente Brain", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Bankroll</div><div class="value amber" id="brBankroll">—</div></div>
  <div class="kpi"><div class="label">P&L Total</div><div class="value green" id="brPnl">—</div></div>
  <div class="kpi"><div class="label">Win Rate</div><div class="value purple" id="brWinRate">—</div></div>
  <div class="kpi"><div class="label">ROI</div><div class="value teal" id="brRoi">—</div></div>
</div>

<div class="kpi-grid" style="margin-top:8px">
  <div class="kpi"><div class="label">Trades</div><div class="value" id="brTotal">—</div></div>
  <div class="kpi"><div class="label">Ganados</div><div class="value green" id="brWon">—</div></div>
  <div class="kpi"><div class="label">Perdidos</div><div class="value red" id="brLost">—</div></div>
  <div class="kpi"><div class="label">Racha</div><div class="value amber" id="brStreak">—</div></div>
</div>

<div id="brKillSwitch" style="display:none;margin:8px 0;padding:10px;background:rgba(239,68,68,.15);border:1px solid var(--red);border-radius:8px;color:var(--red);font-weight:600"></div>

<h3 style="margin:14px 0 6px;color:var(--text1)">Acciones</h3>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
  <button class="btn primary" onclick="brainAutoSim()">Ejecutar Scan + Simular</button>
  <button class="btn" onclick="brainVerifyAll()">Verificar Pendientes</button>
  <button class="btn" onclick="brainReset()">Reset ($10,000)</button>
</div>

<h3 style="margin:14px 0 6px;color:var(--text1)">Gráfica de Bankroll</h3>
<canvas id="brChart" width="700" height="200" style="width:100%;margin-bottom:12px;background:var(--card);border-radius:8px"></canvas>

<h3 style="margin:14px 0 6px;color:var(--text1)">Trades Recientes</h3>
<div id="brTrades" style="margin-bottom:12px;color:var(--text2)">Cargando...</div>

<h3 style="margin:14px 0 6px;color:var(--text1)">Performance por Fuente</h3>
<div id="brSources" style="margin-bottom:12px;color:var(--text2)">Cargando...</div>

<h3 style="margin:14px 0 6px;color:var(--text1)">Pesos del Brain</h3>
<div id="brWeights" style="margin-bottom:12px;color:var(--text2)">Cargando...</div>

<script>
async function brainAutoSim() {
  const el = document.getElementById('brTrades');
  el.innerHTML = '<span style="color:var(--amber)">Escaneando y simulando...</span>';
  try {
    const r = await fetch('/api/brain/auto-simulate');
    const d = await r.json();
    el.innerHTML = '<b>Scan:</b> '+d.scan_signals+' raw → '+d.scan_filtered+' filtradas | <b>Simulados:</b> '+d.trades_simulados+' | <b>Verificados:</b> '+d.trades_verificados+' (W:'+d.trades_won+' L:'+d.trades_lost+') | <b>P&L:</b> $'+d.pnl.toFixed(2);
    brainLoadPerf();
    brainLoadTrades();
  } catch(e) { el.innerHTML = '<span style="color:var(--red)">Error: '+e.message+'</span>'; }
}

async function brainVerifyAll() {
  try {
    const r = await fetch('/api/brain/verify-all');
    const d = await r.json();
    alert('Verificados: '+d.verified+' | Ganados: '+d.won+' | Perdidos: '+d.lost+' | P&L: $'+d.pnl.toFixed(2));
    brainLoadPerf();
    brainLoadTrades();
  } catch(e) { alert('Error: '+e.message); }
}

async function brainReset() {
  if (!confirm('¿Resetear simulación a $10,000? Se borrarán todos los trades.')) return;
  try {
    await fetch('/api/brain/reset', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({bankroll:10000})});
    brainLoadPerf();
    brainLoadTrades();
  } catch(e) { alert('Error: '+e.message); }
}

async function brainLoadPerf() {
  try {
    const r = await fetch('/api/brain/performance');
    const d = await r.json();
    document.getElementById('brBankroll').textContent = '$'+d.bankroll_actual.toLocaleString();
    const pnlColor = d.pnl_total >= 0 ? 'var(--green)' : 'var(--red)';
    document.getElementById('brPnl').textContent = '$'+d.pnl_total.toFixed(2);
    document.getElementById('brPnl').style.color = pnlColor;
    document.getElementById('brWinRate').textContent = d.win_rate+'%';
    const roiColor = d.roi >= 0 ? 'var(--green)' : 'var(--red)';
    document.getElementById('brRoi').textContent = d.roi+'%';
    document.getElementById('brRoi').style.color = roiColor;
    document.getElementById('brTotal').textContent = d.trades_total;
    document.getElementById('brWon').textContent = d.trades_ganados;
    document.getElementById('brLost').textContent = d.trades_perdidos;
    document.getElementById('brStreak').textContent = (d.racha_actual>0?'+':'')+d.racha_actual;

    // Kill switch
    const ks = document.getElementById('brKillSwitch');
    if (d.kill_switch) {
      ks.style.display = 'block';
      ks.innerHTML = '⚠️ KILL SWITCH ACTIVO: '+d.kill_reason;
    } else {
      ks.style.display = 'none';
    }

    // Sources
    let srcHtml = '<table style="width:100%;font-size:12px"><tr><th>Fuente</th><th>Accuracy</th><th>Trades</th><th>P&L</th></tr>';
    for (const [src, perf] of Object.entries(d.source_stats || {})) {
      srcHtml += '<tr><td>'+src+'</td><td>'+perf.accuracy+'%</td><td>'+perf.total+'</td><td>$'+perf.pnl.toFixed(2)+'</td></tr>';
    }
    srcHtml += '</table>';
    document.getElementById('brSources').innerHTML = srcHtml;

    // Chart
    drawBrainChart(d.bankroll_history || []);
  } catch(e) { console.error(e); }
}

async function brainLoadTrades() {
  try {
    const r = await fetch('/api/brain/history?limit=30');
    const d = await r.json();
    const trades = d.trades || [];
    if (trades.length === 0) { document.getElementById('brTrades').innerHTML = 'Sin trades aún. Ejecuta un scan primero.'; return; }
    let html = '<table style="width:100%;font-size:12px"><tr><th>#</th><th>Partido</th><th>Selección</th><th>Cuota</th><th>Edge</th><th>Score</th><th>Stake</th><th>P&L</th><th>Estado</th><th>Acción</th></tr>';
    trades.forEach(t => {
      const color = t.resultado === 'ganada' ? 'var(--green)' : t.resultado === 'perdida' ? 'var(--red)' : 'var(--amber)';
      const btns = t.resultado === 'pendiente' ?
        '<button class="btn" style="font-size:10px;padding:2px 6px" onclick="resolveTrade('+t.id+',true)">✅</button> <button class="btn" style="font-size:10px;padding:2px 6px" onclick="resolveTrade('+t.id+',false)">❌</button>' : '';
      html += '<tr><td>'+t.id+'</td><td>'+t.partido+'</td><td>'+t.seleccion+'</td><td>'+t.cuota+'</td><td>'+t.edge_pct+'%</td><td>'+t.confidence_score+'</td><td>$'+t.stake_simulado+'</td><td style="color:'+(t.pnl>0?'var(--green)':t.pnl<0?'var(--red)':'var(--text2)')+'">$'+(t.pnl||0).toFixed(2)+'</td><td style="color:'+color+'">'+t.resultado+'</td><td>'+btns+'</td></tr>';
    });
    html += '</table>';
    document.getElementById('brTrades').innerHTML = html;
  } catch(e) { document.getElementById('brTrades').innerHTML = 'Error cargando trades'; }
}

async function resolveTrade(id, ganada) {
  try {
    await fetch('/api/brain/resolve', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({trade_id:id, ganada:ganada})});
    brainLoadPerf();
    brainLoadTrades();
  } catch(e) { alert('Error: '+e.message); }
}

async function brainWeights() {
  try {
    const r = await fetch('/api/brain/weights');
    const d = await r.json();
    let html = '<table style="width:100%;font-size:12px"><tr><th>Fuente</th><th>Peso</th></tr>';
    for (const [src, w] of Object.entries(d.current || {})) {
      html += '<tr><td>'+src+'</td><td>'+w+'</td></tr>';
    }
    html += '</table>';
    document.getElementById('brWeights').innerHTML = html;
  } catch(e) { document.getElementById('brWeights').innerHTML = 'Error'; }
}

function drawBrainChart(history) {
  const canvas = document.getElementById('brChart');
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0,0,W,H);
  if (!history || history.length < 2) { ctx.fillStyle='var(--text2)'; ctx.fillText('Sin datos aún', W/2-30, H/2); return; }
  const vals = history.map(h => h.bankroll || 0);
  const min = Math.min(...vals) * 0.98;
  const max = Math.max(...vals) * 1.02;
  const step = W / (vals.length - 1);
  // Grid
  ctx.strokeStyle = 'rgba(255,255,255,0.05)';
  ctx.lineWidth = 1;
  for (let i = 0; i < 5; i++) { const y = H*0.1 + (H*0.8)*(i/4); ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke(); }
  // Line
  ctx.beginPath();
  ctx.strokeStyle = vals[vals.length-1] >= vals[0] ? '#22c55e' : '#ef4444';
  ctx.lineWidth = 2;
  vals.forEach((v,i) => { const x = i*step; const y = H - ((v-min)/(max-min))*H*0.8 - H*0.1; i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y); });
  ctx.stroke();
  // Labels
  ctx.fillStyle = 'rgba(255,255,255,0.5)';
  ctx.font = '11px monospace';
  ctx.fillText('$'+vals[0].toLocaleString(), 4, H-8);
  ctx.fillText('$'+vals[vals.length-1].toLocaleString(), W-60, H-8);
  ctx.fillText('Min: $'+Math.min(...vals).toLocaleString(), 4, 14);
  ctx.fillText('Max: $'+Math.max(...vals).toLocaleString(), W-70, 14);
}

brainLoadPerf();
brainLoadTrades();
brainWeights();
</script>
""", "brain")

MOD_HULK = module_page("Agente HULK", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Bankroll</div><div class="value amber" id="hkBankroll">—</div></div>
  <div class="kpi"><div class="label">P&L</div><div class="value green" id="hkPnl">—</div></div>
  <div class="kpi"><div class="label">Win Rate</div><div class="value purple" id="hkWinRate">—</div></div>
  <div class="kpi"><div class="label">Racha</div><div class="value teal" id="hkStreak">—</div></div>
</div>

<div id="hkKillSwitch" style="display:none;margin:8px 0;padding:10px;background:rgba(239,68,68,.15);border:1px solid var(--red);border-radius:8px;color:var(--red);font-weight:600"></div>

<h3 style="margin:14px 0 6px;color:var(--text1)">Modos de Operación</h3>
<div id="hkModes" style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px"></div>

<h3 style="margin:14px 0 6px;color:var(--text1)">Acciones</h3>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
  <button class="btn primary" onclick="hulkScan()">Ejecutar Scan Hulk</button>
  <button class="btn" onclick="hulkScanSteam()">Steam Moves</button>
  <button class="btn" onclick="hulkScanLive()">Live Betting</button>
  <button class="btn" onclick="hulkScanArb()">Arbitraje</button>
  <button class="btn" onclick="hulkReset()">Reset ($10,000)</button>
</div>
<div id="hkScanResult" style="margin-bottom:12px"></div>

<h3 style="margin:14px 0 6px;color:var(--text1)">Trades Recientes</h3>
<div id="hkTrades" style="margin-bottom:12px;color:var(--text2)">Cargando...</div>

<h3 style="margin:14px 0 6px;color:var(--text1)">Performance por Modo</h3>
<div id="hkModeStats" style="margin-bottom:12px;color:var(--text2)">Cargando...</div>

<script>
const HK_MODES_COLORS = {HAWK:'var(--red)',HUNTER:'var(--amber)',KILLER:'var(--green)',HULK:'var(--purple)',SHARK:'var(--teal)'};

async function hulkScan() {
  const el = document.getElementById('hkScanResult');
  el.innerHTML = '<span style="color:var(--amber)">HULK escaneando...</span>';
  try {
    const r = await fetch('/api/hulk/scan');
    const d = await r.json();
    let html = '<div style="margin-top:8px">';
    html += '<b>Steam:</b> '+d.steam_moves+' | <b>Live:</b> '+d.live_opportunities+' | <b>Arb:</b> '+d.arbitrage+' | <b>Contrarian:</b> '+d.contrarian+'<br>';
    html += '<b>Ejecutados:</b> '+d.trades_executed+' | <b>Modos:</b> '+(d.modes_used||[]).join(', ');
    if (d.executed && d.executed.length > 0) {
      html += '<table style="width:100%;margin-top:8px;font-size:12px"><tr><th>Modo</th><th>Partido</th><th>Selección</th><th>Cuota</th><th>Edge</th><th>Stake</th></tr>';
      d.executed.forEach(t => {
        html += '<tr><td style="color:'+(HK_MODES_COLORS[t.mode]||'var(--text2)')+'">'+(t.mode_emoji||'')+' '+t.mode+'</td><td>'+t.match+'</td><td>'+t.selection+'</td><td>'+t.odds+'</td><td>'+t.edge_pct+'%</td><td>$'+t.stake+'</td></tr>';
      });
      html += '</table>';
    }
    html += '</div>';
    el.innerHTML = html;
    hulkLoadPerf();
    hulkLoadTrades();
  } catch(e) { el.innerHTML = '<span style="color:var(--red)">Error: '+e.message+'</span>'; }
}

async function hulkScanSteam() {
  const el = document.getElementById('hkScanResult');
  el.innerHTML = '<span style="color:var(--amber)">Buscando steam moves...</span>';
  try {
    const r = await fetch('/api/hulk/steam');
    const d = await r.json();
    const moves = d.steam_moves || [];
    if (moves.length === 0) { el.innerHTML = 'Sin steam moves detectados'; return; }
    let html = '<b>Steam Moves Detectados:</b><br>';
    moves.forEach(m => {
      html += '<div style="margin:4px 0;padding:6px;background:var(--card);border-radius:6px">';
      html += '<b>'+m.match+'</b> → '+m.selection+'<br>';
      html += 'Sharp: '+m.sharp_avg+' vs Square: '+m.square_avg+' | Edge: '+m.edge_pct+'%<br>';
      html += '<span style="color:var(--text2)">Casas sharp: '+m.sharp_books.join(', ')+'</span>';
      html += '</div>';
    });
    el.innerHTML = html;
  } catch(e) { el.innerHTML = '<span style="color:var(--red)">Error: '+e.message+'</span>'; }
}

async function hulkScanLive() {
  const el = document.getElementById('hkScanResult');
  el.innerHTML = '<span style="color:var(--amber)">Escaneando live betting...</span>';
  try {
    const r = await fetch('/api/hulk/live');
    const d = await r.json();
    const live = d.live_opportunities || [];
    if (live.length === 0) { el.innerHTML = 'Sin oportunidades live'; return; }
    let html = '<b>Oportunidades Live:</b><br>';
    live.forEach(l => {
      html += '<div style="margin:4px 0;padding:6px;background:var(--card);border-radius:6px">';
      html += '<b>'+l.match+'</b> → '+l.selection+' @ '+l.odds+'<br>';
      html += 'Edge: '+l.edge_pct+'% | '+l.reason;
      html += '</div>';
    });
    el.innerHTML = html;
  } catch(e) { el.innerHTML = '<span style="color:var(--red)">Error: '+e.message+'</span>'; }
}

async function hulkScanArb() {
  const el = document.getElementById('hkScanResult');
  el.innerHTML = '<span style="color:var(--amber)">Cazando arbitrajes...</span>';
  try {
    const r = await fetch('/api/hulk/arbitrage');
    const d = await r.json();
    const arbs = d.arbitrage || [];
    if (arbs.length === 0) { el.innerHTML = 'Sin arbitrajes detectados'; return; }
    let html = '<b>Arbitrajes Encontrados:</b><br>';
    arbs.forEach(a => {
      html += '<div style="margin:4px 0;padding:6px;background:rgba(34,197,94,.1);border:1px solid var(--green);border-radius:6px">';
      html += '<b>'+a.match+'</b> → PROFIT: '+a.profit_pct+'%<br>';
      for (const [sel, book] of Object.entries(a.best_books)) {
        html += sel+': '+a.best_odds[sel]+' @ '+book+'<br>';
      }
      html += '</div>';
    });
    el.innerHTML = html;
  } catch(e) { el.innerHTML = '<span style="color:var(--red)">Error: '+e.message+'</span>'; }
}

async function hulkReset() {
  if (!confirm('¿Resetear Hulk a $10,000?')) return;
  await fetch('/api/hulk/reset', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({bankroll:10000})});
  hulkLoadPerf();
  hulkLoadTrades();
}

async function hulkLoadPerf() {
  try {
    const r = await fetch('/api/hulk/status');
    const d = await r.json();
    document.getElementById('hkBankroll').textContent = '$'+d.bankroll_actual.toLocaleString();
    document.getElementById('hkPnl').textContent = '$'+d.total_pnl.toFixed(2);
    document.getElementById('hkPnl').style.color = d.total_pnl >= 0 ? 'var(--green)' : 'var(--red)';
    document.getElementById('hkWinRate').textContent = d.win_rate+'%';
    document.getElementById('hkStreak').textContent = (d.racha_actual>0?'+':'')+d.racha_actual;
    const ks = document.getElementById('hkKillSwitch');
    if (d.kill_switch) { ks.style.display='block'; ks.innerHTML='⚠️ KILL SWITCH: '+d.kill_reason; }
    else { ks.style.display='none'; }
    // Modes
    let modesHtml = '';
    for (const [mode, cfg] of Object.entries(d.modes_config || {})) {
      const stats = (d.by_mode||{})[mode] || {};
      const trades = stats.trades || 0;
      const pnl = stats.pnl || 0;
      modesHtml += '<div style="padding:8px 12px;background:var(--card);border-radius:8px;border-left:3px solid '+(HK_MODES_COLORS[mode]||'var(--text2)')+'">';
      modesHtml += '<b>'+cfg.emoji+' '+mode+'</b> ('+cfg.desc+')<br>';
      modesHtml += '<span style="font-size:11px">Edge: '+cfg.edge_min+'-'+cfg.edge_max+'% | Kelly: '+(cfg.kelly*100)+'% | Cap: '+cfg.cap_pct+'%</span><br>';
      modesHtml += '<span style="font-size:11px">Trades: '+trades+' | P&L: $'+pnl.toFixed(2)+'</span>';
      modesHtml += '</div>';
    }
    document.getElementById('hkModes').innerHTML = modesHtml;
    // Mode stats
    let statsHtml = '<table style="width:100%;font-size:12px"><tr><th>Modo</th><th>Trades</th><th>Wins</th><th>Win Rate</th><th>P&L</th></tr>';
    for (const [mode, stats] of Object.entries(d.by_mode || {})) {
      statsHtml += '<tr><td style="color:'+(HK_MODES_COLORS[mode]||'var(--text2)')+'">'+mode+'</td><td>'+stats.trades+'</td><td>'+stats.won+'</td><td>'+stats.win_rate+'%</td><td>$'+stats.pnl.toFixed(2)+'</td></tr>';
    }
    statsHtml += '</table>';
    document.getElementById('hkModeStats').innerHTML = statsHtml;
  } catch(e) { console.error(e); }
}

async function hulkLoadTrades() {
  try {
    const r = await fetch('/api/hulk/history?limit=20');
    const d = await r.json();
    const trades = d.trades || [];
    if (trades.length === 0) { document.getElementById('hkTrades').innerHTML = 'Sin trades aún'; return; }
    let html = '<table style="width:100%;font-size:12px"><tr><th>#</th><th>Modo</th><th>Partido</th><th>Selección</th><th>Cuota</th><th>Edge</th><th>Stake</th><th>P&L</th><th>Estado</th></tr>';
    trades.forEach(t => {
      const color = t.resultado === 'ganada' ? 'var(--green)' : t.resultado === 'perdida' ? 'var(--red)' : 'var(--amber)';
      html += '<tr><td>'+t.id+'</td><td style="color:'+(HK_MODES_COLORS[t.mode]||'var(--text2)')+'">'+t.mode+'</td><td>'+t.match+'</td><td>'+t.selection+'</td><td>'+t.odds+'</td><td>'+t.edge_pct+'%</td><td>$'+t.stake+'</td><td style="color:'+(t.pnl>0?'var(--green)':t.pnl<0?'var(--red)':'var(--text2)')+'">$'+(t.pnl||0).toFixed(2)+'</td><td style="color:'+color+'">'+t.resultado+'</td></tr>';
    });
    html += '</table>';
    document.getElementById('hkTrades').innerHTML = html;
  } catch(e) { document.getElementById('hkTrades').innerHTML = 'Error'; }
}

hulkLoadPerf();
hulkLoadTrades();
</script>
""", "hulk")

MOD_MODELOS_AVANZADOS = module_page("Modelos Avanzados", """
<div class="kpi-grid">
  <div class="kpi"><div class="label">Dixon-Coles</div><div class="value green" id="maDC">—</div></div>
  <div class="kpi"><div class="label">ELO Promedio</div><div class="value amber" id="maELO">—</div></div>
  <div class="kpi"><div class="label">CLV Promedio</div><div class="value purple" id="maCLV">—</div></div>
  <div class="kpi"><div class="label">Calibracion</div><div class="value teal" id="maCal">—</div></div>
</div>

<h3 style="margin:12px 0 6px;color:var(--text1)">Predicción Dixon-Coles + ELO</h3>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
  <input id="maHome" placeholder="Equipo Local" style="flex:1;min-width:140px;padding:6px 10px;border-radius:8px;border:1px solid var(--border);background:var(--card);color:var(--text1)">
  <input id="maAway" placeholder="Equipo Visitante" style="flex:1;min-width:140px;padding:6px 10px;border-radius:8px;border:1px solid var(--border);background:var(--card);color:var(--text1)">
  <button class="btn primary" onclick="maPredict()">Predecir</button>
</div>
<div id="maPredResult" style="margin-bottom:12px"></div>

<h3 style="margin:12px 0 6px;color:var(--text1)">Análisis de Fatiga</h3>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
  <input id="maFatSchedule" placeholder="Fechas (separadas por coma: 2026-06-01,2026-06-03,...)" style="flex:2;min-width:200px;padding:6px 10px;border-radius:8px;border:1px solid var(--border);background:var(--card);color:var(--text1)">
  <select id="maFatSport" style="padding:6px 10px;border-radius:8px;border:1px solid var(--border);background:var(--card);color:var(--text1)">
    <option value="basketball">Basketball</option>
    <option value="football">Football</option>
    <option value="soccer">Soccer</option>
  </select>
  <button class="btn primary" onclick="maFatigue()">Analizar</button>
</div>
<div id="maFatResult" style="margin-bottom:12px"></div>

<h3 style="margin:12px 0 6px;color:var(--text1)">Análisis de Clima</h3>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
  <input id="maTempF" type="number" placeholder="Temp °F" value="72" style="width:80px;padding:6px 10px;border-radius:8px;border:1px solid var(--border);background:var(--card);color:var(--text1)">
  <input id="maWind" type="number" placeholder="Viento mph" value="5" style="width:80px;padding:6px 10px;border-radius:8px;border:1px solid var(--border);background:var(--card);color:var(--text1)">
  <input id="maPrecip" type="number" placeholder="Lluvia %" value="0" style="width:80px;padding:6px 10px;border-radius:8px;border:1px solid var(--border);background:var(--card);color:var(--text1)">
  <input id="maHumid" type="number" placeholder="Humedad %" value="50" style="width:80px;padding:6px 10px;border-radius:8px;border:1px solid var(--border);background:var(--card);color:var(--text1)">
  <button class="btn primary" onclick="maWeather()">Analizar</button>
</div>
<div id="maWeatherResult" style="margin-bottom:12px"></div>

<h3 style="margin:12px 0 6px;color:var(--text1)">Calcular CLV</h3>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px">
  <input id="maBetOdds" type="number" step="0.01" placeholder="Cuota apostada" value="2.10" style="width:100px;padding:6px 10px;border-radius:8px;border:1px solid var(--border);background:var(--card);color:var(--text1)">
  <input id="maCloseOdds" type="number" step="0.01" placeholder="Cuota cierre" value="1.90" style="width:100px;padding:6px 10px;border-radius:8px;border:1px solid var(--border);background:var(--card);color:var(--text1)">
  <button class="btn primary" onclick="maCLV()">Calcular</button>
</div>
<div id="maCLVResult"></div>
""", """
async function maPredict(){
  const h=document.getElementById('maHome').value||'Club América'
  const a=document.getElementById('maAway').value||'Guadalajara'
  try{
    const d=await api('/api/advanced/combined/predict?home='+encodeURIComponent(h)+'&away='+encodeURIComponent(a))
    const dc=d.dixon_coles||{},elo=d.elo||{},comb=d.modelo_combinado||{}
    let html='<div class="kpi-grid" style="margin-top:8px">'
    html+='<div class="kpi"><div class="label">Dixon-Coles Local</div><div class="value green">'+(dc.local||0)+'%</div></div>'
    html+='<div class="kpi"><div class="label">ELO Local</div><div class="value amber">'+(elo.local||0)+'%</div></div>'
    html+='<div class="kpi"><div class="label">Combinado Local</div><div class="value green">'+(comb.local||0)+'%</div></div>'
    html+='<div class="kpi"><div class="label">Combinado Empate</div><div class="value purple">'+(comb.empate||0)+'%</div></div>'
    html+='<div class="kpi"><div class="label">Combinado Visitante</div><div class="value red">'+(comb.visitante||0)+'%</div></div>'
    html+='<div class="kpi"><div class="label">Goles Esperados</div><div class="value">'+d.goles_esperados+'</div></div>'
    html+='<div class="kpi"><div class="label">Over 2.5</div><div class="value teal">'+d.over_25+'%</div></div>'
    html+='<div class="kpi"><div class="label">BTTS</div><div class="value purple">'+d.btts+'%</div></div>'
    html+='</div>'
    document.getElementById('maPredResult').innerHTML=html
    document.getElementById('maDC').textContent=(dc.local||0)+'%'
    document.getElementById('maELO').textContent=(elo.elo_home||1500)
  }catch(e){document.getElementById('maPredResult').innerHTML='<span class="red">Error: '+e.message+'</span>'}
}
async function maFatigue(){
  const s=document.getElementById('maFatSchedule').value
  const sp=document.getElementById('maFatSport').value
  try{
    const d=await api('/api/advanced/fatigue/analyze?schedule='+encodeURIComponent(s)+'&sport='+sp)
    let html='<div class="kpi-grid" style="margin-top:8px">'
    html+='<div class="kpi"><div class="label">Fatiga Score</div><div class="value '+(d.fatiga_score>=50?'red':d.fatiga_score>=30?'amber':'green')+'">'+d.fatiga_score+'/100</div></div>'
    html+='<div class="kpi"><div class="label">Nivel</div><div class="value">'+d.nivel+'</div></div>'
    html+='<div class="kpi"><div class="label">Impacto</div><div class="value '+(d.impacto_pct<0?'red':'green')+'">'+d.impacto_pct+'%</div></div>'
    html+='</div>'
    if(d.factores&&d.factores.length){
      html+='<div class="table-wrap"><table><thead><tr><th>Tipo</th><th>Severidad</th><th>Detalle</th><th>Impacto</th></tr></thead><tbody>'
      d.factores.forEach(f=>{html+='<tr><td>'+f.tipo+'</td><td class="'+(f.severidad==='ALTA'?'red':f.severidad==='MEDIA'?'amber':'')+'">'+f.severidad+'</td><td>'+f.detalle+'</td><td class="'+(f.impacto_pct<0?'red':'green')+'">'+f.impacto_pct+'%</td></tr>'})
      html+='</tbody></table></div>'
    }
    document.getElementById('maFatResult').innerHTML=html
  }catch(e){document.getElementById('maFatResult').innerHTML='<span class="red">Error: '+e.message+'</span>'}
}
async function maWeather(){
  const t=document.getElementById('maTempF').value,w=document.getElementById('maWind').value,p=document.getElementById('maPrecip').value,h=document.getElementById('maHumid').value
  try{
    const d=await api('/api/advanced/weather/analyze?temperature_f='+t+'&wind_mph='+w+'&precipitation_pct='+p+'&humidity_pct='+h+'&outdoor=true')
    let html='<div class="kpi-grid" style="margin-top:8px">'
    html+='<div class="kpi"><div class="label">Impacto</div><div class="value '+(d.impacto_total_pct<=-5?'red':d.impacto_total_pct<=-2?'amber':'green')+'">'+d.impacto+'</div></div>'
    html+='<div class="kpi"><div class="label">Total Impacto</div><div class="value '+(d.impacto_total_pct<0?'red':'green')+'">'+d.impacto_total_pct+'%</div></div>'
    html+='</div>'
    if(d.factores&&d.factores.length){
      html+='<div class="table-wrap"><table><thead><tr><th>Tipo</th><th>Severidad</th><th>Mercado</th><th>Impacto</th></tr></thead><tbody>'
      d.factores.forEach(f=>{html+='<tr><td>'+f.tipo+'</td><td class="'+(f.severidad==='ALTA'?'red':'amber')+'">'+f.severidad+'</td><td>'+(f.mercado_afectado||'-')+'</td><td class="red">'+f.impacto_pct+'%</td></tr>'})
      html+='</tbody></table></div>'
    }
    document.getElementById('maWeatherResult').innerHTML=html
  }catch(e){document.getElementById('maWeatherResult').innerHTML='<span class="red">Error: '+e.message+'</span>'}
}
async function maCLV(){
  const b=document.getElementById('maBetOdds').value,c=document.getElementById('maCloseOdds').value
  try{
    const d=await api('/api/advanced/clv/calculate?bet_odds='+b+'&closing_odds='+c)
    let html='<div class="kpi-grid" style="margin-top:8px">'
    html+='<div class="kpi"><div class="label">CLV</div><div class="value '+(d.es_positivo?'green':'red')+'">'+d.clv_pct+'%</div></div>'
    html+='<div class="kpi"><div class="label">Nivel</div><div class="value">'+d.nivel+'</div></div>'
    html+='<div class="kpi"><div class="label">Prob Apostada</div><div class="value">'+d.bet_implied_prob+'%</div></div>'
    html+='<div class="kpi"><div class="label">Prob Cierre</div><div class="value">'+d.closing_implied_prob+'%</div></div>'
    html+='</div>'
    html+='<div style="margin-top:6px;color:var(--text2)">'+d.recomendacion+'</div>'
    document.getElementById('maCLVResult').innerHTML=html
    document.getElementById('maCLV').textContent=d.clv_pct+'%'
    document.getElementById('maCal').textContent=d.nivel
  }catch(e){document.getElementById('maCLVResult').innerHTML='<span class="red">Error: '+e.message+'</span>'}
}
// Cargar ratings ELO al inicio
(async()=>{try{
  const d=await api('/api/advanced/elo/ratings')
  if(d.total_equipos>0)document.getElementById('maELO').textContent=d.total_equipos+' equipos'
}catch(e){}})()
""")

# ── Module map ──────────────────────────────────────────────────────────────
MODULES = {
    "value-bets":    ("Value Bets",          MOD_VALUE_BETS),
    "sharp":         ("Sharp Money",         MOD_SHARP),
    "alta-prob":     ("Alta Probabilidad",   MOD_ALTA_PROB),
    "arbitraje":     ("Arbitraje",           MOD_ARBITRAJE),
    "cross-market":  ("Cross Market",        MOD_CROSS),
    "kelly":         ("Kelly Calculator",    MOD_KELLY),
    "value-engine":  ("Value Engine",        MOD_VALUE_ENGINE),
    "copa":          ("Copa del Mundo 2026", MOD_COPA),
    "ml":            ("ML Predictivo",       MOD_ML),
    "backtesting":   ("Backtesting",         MOD_BACKTESTING),
    "nlp":           ("Noticias & Lesiones", MOD_NLP),
    "montecarlo":    ("Monte Carlo",         MOD_MONTECARLO),
    "bankroll":      ("Bankroll",            MOD_BANKROLL),
    "simulacion":    ("Simulacion",          MOD_SIMULACION),
    "contabilidad":  ("Contabilidad",        MOD_CONTABILIDAD),
    "journal":       ("Trading Journal",     MOD_JOURNAL),
    "mercados":      ("Mercados Multi",      MOD_MERCADOS),
    "bookmakers":    ("Rating Casas",        MOD_BOOKMAKERS),
    "progol":        ("Progol Optimizer",    MOD_PROGOL),
    "cuentas":       ("Cuentas",             MOD_CUENTAS),
    "portfolio":     ("Portfolio",           MOD_PORTFOLIO),
    "rendimiento":   ("Rendimiento",         MOD_RENDIMIENTO),
    "modelos-avanzados": ("Modelos Avanzados", MOD_MODELOS_AVANZADOS),
    "brain":         ("Agente Brain",        MOD_BRAIN),
    "hulk":          ("Agente HULK",         MOD_HULK),
}

# ── Main export ──────────────────────────────────────────────────────────
HTML = LANDING_HTML
