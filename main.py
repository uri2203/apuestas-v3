"""
ApuestasPro v4.3 — Servidor principal.
"""

import math, os, json, logging, time, queue
from flask import Flask, jsonify, request, Response, stream_with_context
from apscheduler.schedulers.background import BackgroundScheduler

from dashboard import HTML
from auth import auth_bp, login_required
from telegram_bot import telegram_bp, register_webhook, alerta_value_bets, alerta_nlp
from database import init_db
from routers.bankroll_router import bankroll_bp
from routers.mercados_router import mercados_bp
from routers.ml_router import ml_bp, ligas_bp, predicciones_bp
from routers.progol_optimizer_router import progol_opt_bp
from routers.accounts_router import accounts_bp

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# ── Blueprints ─────────────────────────────────────────────────────────────────
for bp in [auth_bp, telegram_bp, bankroll_bp, mercados_bp, ml_bp, ligas_bp, predicciones_bp, progol_opt_bp, accounts_bp]:
    app.register_blueprint(bp)

# ── Base de datos ──────────────────────────────────────────────────────────────
init_db()
from services.account_manager import init_account_tables
try:
    init_account_tables()
except Exception as e:
    logging.warning("account_tables init: %s", e)

# ── SSE — cola de eventos en tiempo real ──────────────────────────────────────
_sse_clients: list[queue.Queue] = []

def _broadcast(evento: dict):
    """Envía un evento a todos los clientes SSE conectados."""
    import json as _json
    data = f"data: {_json.dumps(evento)}\n\n"
    dead = []
    for q in _sse_clients:
        try:
            q.put_nowait(data)
        except Exception:
            dead.append(q)
    for q in dead:
        _sse_clients.remove(q)

@app.route("/api/eventos")
@login_required
def sse_eventos():
    """Server-Sent Events: el dashboard recibe alertas en tiempo real."""
    q = queue.Queue()
    _sse_clients.append(q)

    def stream():
        try:
            yield "data: {\"tipo\": \"conectado\", \"msg\": \"Stream activo\"}\n\n"
            while True:
                try:
                    msg = q.get(timeout=30)
                    yield msg
                except queue.Empty:
                    yield ": heartbeat\n\n"
        except GeneratorExit:
            _sse_clients.remove(q)

    return Response(
        stream_with_context(stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

# ── Dashboard ──────────────────────────────────────────────────────────────────
@app.route("/")
@login_required
def dashboard():
    return HTML, 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/health")
def health():
    from database import get_bankroll_actual
    return jsonify({
        "status":  "ok",
        "version": "4.3.0",
        "db":      "ok",
        "sse_clients": len(_sse_clients),
        "bankroll": get_bankroll_actual(),
    })

# ── MELATE ─────────────────────────────────────────────────────────────────────
FREQ_MELATE = {
    1:179,2:168,3:152,4:185,5:171,6:193,7:142,8:188,9:175,10:164,
    11:182,12:177,13:169,14:148,15:205,16:183,17:176,18:191,19:162,20:178,
    21:186,22:218,23:231,24:174,25:181,26:167,27:189,28:172,29:165,30:187,
    31:173,32:196,33:158,34:184,35:170,36:179,37:163,38:247,39:155,40:190,
    41:177,42:185,43:168,44:174,45:199,46:161,47:183,48:169,49:176,50:158,
    51:144,52:172,53:180,54:165,55:187,56:171,
}

@app.route("/api/melate/frecuencias")
@login_required
def melate_frecuencias():
    sf = sorted(FREQ_MELATE.items(), key=lambda x: x[1], reverse=True)
    return jsonify({
        "sorteos_analizados": 3847,
        "frecuencias": {str(n): {"frecuencia_abs": f} for n, f in FREQ_MELATE.items()},
        "calientes": [{"numero": n, "frecuencia_abs": f} for n, f in sf[:10]],
        "frios":     [{"numero": n, "frecuencia_abs": f} for n, f in sf[-10:]],
    })

@app.route("/api/melate/generar")
@login_required
def melate_generar():
    import random
    modo = request.args.get("modo","balanced")
    cantidad = int(request.args.get("cantidad",5))
    sf = sorted(FREQ_MELATE.items(), key=lambda x: x[1], reverse=True)
    hot=[n for n,_ in sf[:20]]; cold=[n for n,_ in sf[-20:]]
    pool = hot if modo=="hot" else cold if modo=="cold" else list(range(1,57))
    return jsonify({"combinaciones":[
        {"combinacion":i+1,"numeros":sorted(random.sample(pool,min(6,len(pool)))),"modo":modo}
        for i in range(cantidad)
    ]})

@app.route("/api/melate/probabilidades")
def melate_probabilidades():
    t = math.comb(56,6)
    return jsonify({"total_combinaciones":t,"prob_1_en":t})

@app.route("/api/melate/ultimo-resultado")
@login_required
def melate_ultimo():
    import random
    return jsonify({"juego":"Melate","numeros":sorted(random.sample(range(1,57),6)),"fecha":"2025-04-25"})

@app.route("/api/melate/racha/<int:numero>")
@login_required
def melate_racha(numero):
    import random
    return jsonify({"numero":numero,"sorteos_sin_salir":random.randint(1,80),"maxima_racha":84})

# ── PROGOL ─────────────────────────────────────────────────────────────────────
@app.route("/api/progol/jornada")
@login_required
def progol_jornada():
    from services.progol import generar_jornada_progol
    return jsonify(generar_jornada_progol(os.getenv("API_FOOTBALL_KEY","")))

@app.route("/api/progol/partido")
@login_required
def progol_partido():
    from services.progol import predecir_partido
    home=request.args.get("home","Club América"); away=request.args.get("away","Guadalajara")
    return jsonify(predecir_partido(home,away,request.args.get("xg_home",type=float),request.args.get("xg_away",type=float)))

@app.route("/api/progol/partido-completo")
@login_required
def progol_partido_completo():
    from services.progol import predecir_partido
    home=request.args.get("home","Club América"); away=request.args.get("away","Guadalajara")
    try: les_local=json.loads(request.args.get("lesiones_local","[]").replace("'",'"'))
    except: les_local=[]
    try: les_visita=json.loads(request.args.get("lesiones_visitante","[]").replace("'",'"'))
    except: les_visita=[]
    return jsonify(predecir_partido(
        home,away,
        lesiones_local=les_local,lesiones_visitante=les_visita,
        arbitro=request.args.get("arbitro"),ciudad=request.args.get("ciudad"),
        pos_local=int(request.args.get("pos_local",9)),pos_visitante=int(request.args.get("pos_visitante",9)),
        jornada=request.args.get("jornada",type=int),
        api_key_clima=os.getenv("OPENWEATHER_KEY",""),
    ))

@app.route("/api/progol/ranking")
@login_required
def progol_ranking():
    from services.progol import ranking_equipos
    return jsonify(ranking_equipos(os.getenv("API_FOOTBALL_KEY","")))

# ── ODDS / VALUE BETS ──────────────────────────────────────────────────────────
_pred_cache = {}

def _edge_con_modelo(ht, at, outcome, price):
    """Calcula edge real: (prob_modelo * cuota - 1) * 100. Cachea predicciones."""
    try:
        key = f"{ht}|{at}"
        if key not in _pred_cache:
            from services.progol import predecir_partido
            _pred_cache[key] = predecir_partido(ht, at)
        pred = _pred_cache[key]
        prob_map = {ht: pred["local"], at: pred["visitante"], "Draw": pred["empate"]}
        mp = prob_map.get(outcome, 0)
        if not mp:
            for k, v in prob_map.items():
                if k.lower() in outcome.lower() or outcome.lower() in k.lower():
                    mp = v; break
        return round((mp * price - 1) * 100, 1) if mp > 0 else 0.0
    except Exception:
        return 0.0

@app.route("/api/odds/value-bets")
@login_required
def value_bets():
    import httpx
    edge_min = float(request.args.get("edge_minimo", 2))
    api_key  = os.getenv("ODDS_API_KEY", "")
    _pred_cache.clear()  # limpiar cache de predicciones

    # Sin API key — error claro, sin datos demo
    if not api_key:
        return jsonify({
            "total_encontrados": 0,
            "value_bets": [],
            "es_demo": True,
            "error": "ODDS_API_KEY no configurada",
            "aviso": "Configura ODDS_API_KEY en Render → Environment para obtener value bets reales",
        })

    try:
        deporte = request.args.get("deporte", "soccer_mexico_ligamx")
        r = httpx.get(
            f"https://api.the-odds-api.com/v4/sports/{deporte}/odds",
            params={"apiKey": api_key, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"},
            timeout=10,
        )
        data = r.json()

        # Error de API (cuota expirada, plan agotado, etc.)
        if isinstance(data, dict) and data.get("message"):
            return jsonify({
                "total_encontrados": 0,
                "value_bets": [],
                "es_demo": False,
                "error": f"Odds API: {data['message']}",
                "aviso": f"Error de la API: {data['message']}",
            })

        real = []
        # Cache de predicciones por partido (evita recalcular el modelo por cada cuota)
        pred_cache = {}
        for m in data if isinstance(data, list) else []:
            ht, at = m.get("home_team",""), m.get("away_team","")
            if not ht or not at: continue
            for book in m.get("bookmakers", []):
                for o in book.get("markets", [{}])[0].get("outcomes", []):
                    if not o.get("price") or o["price"] <= 1: continue
                    edge = _edge_con_modelo(ht, at, o["name"], o["price"])
                    if edge >= edge_min:
                        real.append({
                            "partido":          f"{ht} vs {at}",
                            "liga":             m.get("sport_title", "Liga MX"),
                            "fecha":            m.get("commence_time", ""),
                            "resultado":        o["name"],
                            "casa":             book["title"],
                            "cuota":            o["price"],
                            "edge_porcentaje":  edge,
                            "es_value_bet":     True,
                        })

        # Guardar todos los value bets en UNA sola conexión (evita saturar el pool)
        if real:
            try:
                from database import db, _execute
                with db() as conn:
                    for vb in real[:30]:
                        _execute(conn,
                            "INSERT INTO value_bets_log (partido, liga, resultado, casa, cuota, edge_pct) "
                            "VALUES (?,?,?,?,?,?)",
                            (vb["partido"], vb["liga"], vb["resultado"], vb["casa"], vb["cuota"], vb["edge_porcentaje"]))
            except Exception as e:
                logging.warning("No se pudo guardar value bets en DB: %s", e)

        # Deduplicar: mejor cuota por partido+resultado
        seen = {}
        for vb in sorted(real, key=lambda x: x["edge_porcentaje"], reverse=True):
            key = f"{vb['partido']}|{vb['resultado']}"
            if key not in seen:
                seen[key] = vb
        filtered = list(seen.values())

        return jsonify({
            "total_encontrados": len(filtered),
            "value_bets":        filtered,
            "es_demo":           False,
            "total_partidos_analizados": len(data) if isinstance(data, list) else 0,
            "aviso": None if filtered else f"Sin value bets con edge >= {edge_min}% en este momento",
        })

    except httpx.TimeoutException:
        return jsonify({"total_encontrados": 0, "value_bets": [], "es_demo": False,
                        "error": "Timeout al conectar con Odds API", "aviso": "La API tardó demasiado. Intenta de nuevo."})
    except Exception as e:
        logging.error("Odds API error: %s", e)
        return jsonify({"total_encontrados": 0, "value_bets": [], "es_demo": False,
                        "error": str(e), "aviso": f"Error: {e}"})

# ── KELLY ──────────────────────────────────────────────────────────────────────
@app.route("/api/kelly/calcular",methods=["POST"])
@login_required
def kelly_calcular():
    d=request.get_json(); bank=float(d.get("bankroll",5000)); odds=float(d.get("cuota_decimal",2.10))
    prob=float(d.get("probabilidad_estimada_pct",55))/100; frac=float(d.get("fraccion",0.5))
    b=odds-1; q=1-prob; kp=(b*prob-q)/b if b>0 else 0; ka=kp*frac; bet=max(0,bank*ka)
    return jsonify({"kelly_puro_pct":round(kp*100,2),"kelly_ajustado_pct":round(ka*100,2),
        "apuesta_sugerida":round(bet,2),"hay_valor":kp>0,
        "roi_esperado_pct":round((b*prob-q)*100,2),"recomendacion":"Apostar" if kp>0 else "NO apostar"})

# ── CLV ────────────────────────────────────────────────────────────────────────
@app.route("/api/pro/clv/calcular")
@login_required
def clv_calcular():
    mi=float(request.args.get("cuota_apostada",2.10)); cl=float(request.args.get("cuota_cierre",1.85))
    pct=round((mi/cl-1)*100,2)
    return jsonify({"clv_pct":pct,"es_positivo":pct>0,
        "prob_implicita_apostada_pct":round(1/mi*100,2),
        "prob_implicita_cierre_pct":round(1/cl*100,2),
        "calidad":"positivo" if pct>0 else "negativo"})

# ── MONTE CARLO ────────────────────────────────────────────────────────────────
@app.route("/api/pro/montecarlo/partido")
@login_required
def montecarlo():
    import random
    lL=float(request.args.get("lambda_local",1.5)); lV=float(request.args.get("lambda_visitante",1.1))
    N=min(int(request.args.get("simulaciones",10000)),50000)
    def poisson(l):
        k,p,q=0,math.exp(-l),1.0
        while q>p: k+=1; q*=random.random()
        return k-1
    h=d=a=0; gols=[]
    for _ in range(N):
        gl,gv=poisson(lL),poisson(lV); gols.append(gl+gv)
        if gl>gv: h+=1
        elif gl==gv: d+=1
        else: a+=1
    pL,pD,pV=h/N*100,d/N*100,a/N*100; avg=sum(gols)/N
    return jsonify({"simulaciones":N,
        "probabilidades":{"local_pct":round(pL,1),"empate_pct":round(pD,1),"visitante_pct":round(pV,1)},
        "cuotas_justas_sin_vig":{"local":round(100/pL,2) if pL>0 else 99,"empate":round(100/pD,2) if pD>0 else 99,"visitante":round(100/pV,2) if pV>0 else 99},
        "mercados_adicionales":{"avg_goles_totales":round(avg,2),
            "prob_over_2_5_pct":round(sum(1 for g in gols if g>2.5)/N*100,1),
            "prob_over_1_5_pct":round(sum(1 for g in gols if g>1.5)/N*100,1)}})

# ── SHARP MONEY ────────────────────────────────────────────────────────────────
@app.route("/api/sharp/analizar")
@login_required
def sharp_analizar():
    from services.sharp_money import analizar_partido_sharp
    partido=request.args.get("partido","Local vs Visitante")
    try: casas=json.loads(request.args.get("lineas_casas","{}"))
    except: casas={}
    resultado=analizar_partido_sharp(
        partido,float(request.args.get("linea_apertura",2.10)),
        float(request.args.get("linea_actual",1.95)),
        float(request.args.get("pct_boletos_local",30)),
        float(request.args.get("pct_dinero_local",60)),
        lineas_por_casa=casas or None,dias_antes=int(request.args.get("dias_antes",2)))
    _broadcast({"tipo":"sharp_move","data":resultado})
    return jsonify(resultado)

@app.route("/api/sharp/steam")
@login_required
def sharp_steam():
    from services.sharp_money import detectar_steam
    try: movs=json.loads(request.args.get("movimientos","[]"))
    except: movs=[]
    if not movs:
        movs=[{"casa":"Pinnacle","linea_antes":2.10,"linea_ahora":1.85},
              {"casa":"Bet365","linea_antes":2.15,"linea_ahora":1.90},
              {"casa":"Codere","linea_antes":2.18,"linea_ahora":1.92}]
    resultado=detectar_steam(movs)
    if resultado.get("detectado"): _broadcast({"tipo":"steam_move","data":resultado})
    return jsonify(resultado)

# ── NLP ─────────────────────────────────────────────────────────────────────────
@app.route("/api/nlp/scan")
@login_required
def nlp_scan():
    from services.nlp_sentiment import scan_completo
    home=request.args.get("home","Club América"); away=request.args.get("away","Guadalajara")
    resultado=scan_completo(home,away)
    if resultado.get("tiene_edge"):
        _broadcast({"tipo":"nlp_alerta","partido":f"{home} vs {away}","edges":resultado.get("alertas_edge",[])})
    return jsonify(resultado)

@app.route("/api/nlp/noticias")
@login_required
def nlp_noticias():
    from services.nlp_sentiment import fetch_noticias,detectar_lesiones
    noticias=fetch_noticias(20)
    for n in noticias: n["alertas"]=detectar_lesiones(n["titulo"]+" "+n["desc"])
    return jsonify({"noticias":noticias,"total":len(noticias)})

# ── BACKTESTING ────────────────────────────────────────────────────────────────
@app.route("/api/backtest")
@login_required
def backtest_run():
    from services.backtesting import backtest, backtest_por_modelo
    from services.api_football import get_fixtures_liga, LIGAS
    from services.progol import HISTORIAL_DEMO
    ventana = int(request.args.get("ventana", 20))
    modo    = request.args.get("modo", "ensemble")
    api_key = os.getenv("API_FOOTBALL_KEY", "")
    # Usar datos reales si hay key, sino historial demo con aviso
    historial = HISTORIAL_DEMO
    es_demo   = True
    if api_key:
        try:
            real = get_fixtures_liga(LIGAS["liga_mx"], None, api_key)
            if real and len(real) >= 10:
                historial = real
                es_demo   = False
        except Exception:
            pass
    resultado = backtest_por_modelo(historial, ventana) if modo == "comparar" else backtest(historial, ventana)
    resultado["es_demo"]    = es_demo
    resultado["n_partidos"] = len(historial)
    if es_demo:
        resultado["aviso"] = "Backtesting con historial demo (30 partidos). Configura API_FOOTBALL_KEY para datos reales."
    return jsonify(resultado)


@app.route("/api/alertas/recientes")
@login_required
def alertas_recientes():
    """Alertas reales desde la base de datos + estado de las APIs."""
    from database import db, _fetchall
    
    alertas = []
    
    # Leer alertas reales de la DB
    try:
        with db() as conn:
            rows = _fetchall(conn,
                "SELECT * FROM alerts_log ORDER BY id DESC LIMIT 20")
        for r in rows:
            tipo_map = {"NLP_LESION":"r","STEAM":"s","VALUE_BET":"g","NLP_MORAL":"i"}
            alertas.append({
                "t": tipo_map.get(r.get("tipo",""),"i"),
                "x": r.get("detalle",""),
                "g": r.get("created_at",""),
                "urgencia": r.get("urgencia",""),
                "real": True,
            })
    except Exception:
        pass

    # Leer últimos value bets detectados
    try:
        with db() as conn:
            vbs = _fetchall(conn,
                "SELECT * FROM value_bets_log ORDER BY id DESC LIMIT 5")
        for v in vbs:
            alertas.append({
                "t": "g",
                "x": f"Value bet: {v.get('partido','')} · {v.get('resultado','')} @{v.get('cuota','')} · Edge +{v.get('edge_pct','')}% ({v.get('casa','')})",
                "g": str(v.get("detected_at","")),
                "real": True,
            })
    except Exception:
        pass

    # Estado de las APIs
    api_status = {
        "api_football": bool(os.getenv("API_FOOTBALL_KEY","")),
        "odds_api":     bool(os.getenv("ODDS_API_KEY","")),
        "openweather":  bool(os.getenv("OPENWEATHER_KEY","")),
        "telegram":     bool(os.getenv("TELEGRAM_TOKEN","")),
        "db":           bool(os.getenv("DATABASE_URL","")),
        "modo":         "REAL" if os.getenv("API_FOOTBALL_KEY","") else "DEMO",
    }

    # Si no hay alertas reales, indicar que el sistema está en modo demo
    if not alertas:
        alertas = [{
            "t": "i",
            "x": "Sistema en modo DEMO — configura API_FOOTBALL_KEY y ODDS_API_KEY para datos reales",
            "g": "ahora",
            "real": False,
        }]

    return jsonify({
        "alertas": sorted(alertas, key=lambda x: x.get("g",""), reverse=True)[:15],
        "api_status": api_status,
        "total": len(alertas),
    })


# ── SCHEDULER ──────────────────────────────────────────────────────────────────
def _alerta_vb_con_broadcast():
    alerta_value_bets()
    _broadcast({"tipo":"scheduler_tick","job":"value_bets","ts":time.time()})

def _alerta_nlp_con_broadcast():
    alerta_nlp()
    _broadcast({"tipo":"scheduler_tick","job":"nlp","ts":time.time()})

def _verificacion_auto():
    from services.verificador import verificar_automatico
    api_key=os.getenv("API_FOOTBALL_KEY","")
    if api_key:
        r=verificar_automatico(api_key)
        logging.info("Verificación auto: %s",r)

def _resumen_diario():
    from services.email_alerts import enviar_resumen_diario_completo
    enviar_resumen_diario_completo()

scheduler=BackgroundScheduler()
scheduler.add_job(_alerta_vb_con_broadcast,   "interval", hours=3,  id="vb_alert")
scheduler.add_job(_alerta_nlp_con_broadcast,  "interval", hours=4,  id="nlp_alert")
scheduler.add_job(_verificacion_auto,         "interval", hours=6,  id="verify_preds")
scheduler.add_job(_resumen_diario,            "cron",     hour=8,   id="daily_email")
scheduler.add_job(lambda: logging.info("ApuestasPro v4.3 tick"), "interval", hours=1, id="tick")
scheduler.start()

register_webhook(os.getenv("RENDER_EXTERNAL_URL",""))

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",8000)))
