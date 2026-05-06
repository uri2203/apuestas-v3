from flask import Flask, jsonify, request
from dashboard import HTML
import math, random, os, json, logging
from apscheduler.schedulers.background import BackgroundScheduler
import httpx

app = Flask(__name__)

# ── DASHBOARD ──────────────────────────────────────────────────────────────
@app.route("/")
def dashboard():
    return HTML, 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": "4.1.0"})

# ── MELATE ─────────────────────────────────────────────────────────────────
FREQ = {i: random.randint(80, 220) for i in range(1, 57)}
FREQ[38]=312; FREQ[23]=290; FREQ[22]=278; FREQ[15]=265
FREQ[7]=95;   FREQ[14]=88;  FREQ[3]=91;   FREQ[51]=97

@app.route("/api/melate/frecuencias")
def melate_frecuencias():
    sf = sorted(FREQ.items(), key=lambda x: x[1], reverse=True)
    return jsonify({
        "sorteos_analizados": 3847,
        "frecuencias": {str(n): {"frecuencia_abs": f} for n,f in FREQ.items()},
        "calientes": [{"numero":n,"frecuencia_abs":f} for n,f in sf[:10]],
        "frios":     [{"numero":n,"frecuencia_abs":f} for n,f in sf[-10:]],
    })

@app.route("/api/melate/generar")
def melate_generar():
    modo = request.args.get("modo","balanced")
    cantidad = int(request.args.get("cantidad",5))
    sf = sorted(FREQ.items(), key=lambda x: x[1], reverse=True)
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
def melate_ultimo():
    return jsonify({"juego":"Melate","numeros":sorted(random.sample(range(1,57),6)),"fecha":"2025-04-25"})

@app.route("/api/melate/racha/<int:numero>")
def melate_racha(numero):
    return jsonify({"numero":numero,"sorteos_sin_salir":random.randint(1,80),"maxima_racha":84})

# ── PROGOL + DIXON-COLES + ELO ────────────────────────────────────────────
@app.route("/api/progol/jornada")
def progol_jornada():
    from services.progol import generar_jornada_progol
    api_key = os.getenv("API_FOOTBALL_KEY","")
    return jsonify(generar_jornada_progol(api_key))

@app.route("/api/progol/partido")
def progol_partido():
    from services.progol import predecir_partido
    home = request.args.get("home","Club América")
    away = request.args.get("away","Guadalajara")
    xg_h = request.args.get("xg_home", type=float)
    xg_a = request.args.get("xg_away", type=float)
    return jsonify(predecir_partido(home, away, xg_h, xg_a))

@app.route("/api/progol/partido-completo")
def progol_partido_completo():
    from services.progol import predecir_partido
    
    home      = request.args.get("home","Club América")
    away      = request.args.get("away","Guadalajara")
    arbitro   = request.args.get("arbitro")
    ciudad    = request.args.get("ciudad")
    pos_local = int(request.args.get("pos_local",9))
    pos_visit = int(request.args.get("pos_visitante",9))
    jornada   = request.args.get("jornada",type=int)
    
    # 1. Extracción de cadenas crudas
    les_local_str = request.args.get("lesiones_local","[]")
    les_visit_str = request.args.get("lesiones_visitante","[]")
    
    # 2. Parseo aislado con sanitización de comillas
    try:
        les_local = json.loads(les_local_str.replace("'", '"'))
    except Exception as e:
        logging.error(f"Fallo en parser JSON Local: {les_local_str} | Error: {e}")
        les_local = []
        
    try:
        les_visita = json.loads(les_visit_str.replace("'", '"'))
    except Exception as e:
        logging.error(f"Fallo en parser JSON Visitante: {les_visit_str} | Error: {e}")
        les_visita = []

    # 3. Inyección al modelo
    clima_key = os.getenv("OPENWEATHER_KEY","")
    return jsonify(predecir_partido(
        home, away,
        lesiones_local=les_local,
        lesiones_visitante=les_visita,
        arbitro=arbitro, ciudad=ciudad,
        pos_local=pos_local, pos_visitante=pos_visit,
        jornada=jornada, api_key_clima=clima_key,
    ))

@app.route("/api/progol/ranking")
def progol_ranking():
    from services.progol import ranking_equipos
    api_key = os.getenv("API_FOOTBALL_KEY","")
    return jsonify(ranking_equipos(api_key))

# ── ODDS ───────────────────────────────────────────────────────────────────
VB=[
    {"partido":"Chivas vs América","liga":"Liga MX","resultado":"Local","casa":"Bet365","cuota":2.10,"edge_porcentaje":8.4,"es_value_bet":True},
    {"partido":"Toluca vs Santos","liga":"Liga MX","resultado":"Local","casa":"Codere","cuota":2.00,"edge_porcentaje":10.0,"es_value_bet":True},
    {"partido":"Cruz Azul vs Pumas","liga":"Liga MX","resultado":"Local","casa":"1xBet","cuota":1.85,"edge_porcentaje":7.3,"es_value_bet":True},
    {"partido":"Tigres vs Monterrey","liga":"Liga MX","resultado":"Empate","casa":"Bet365","cuota":3.10,"edge_porcentaje":3.1,"es_value_bet":True},
]

@app.route("/api/odds/value-bets")
def value_bets():
    edge_min = float(request.args.get("edge_minimo",2))
    api_key  = os.getenv("ODDS_API_KEY","")
    results  = VB
    if api_key:
        try:
            r = httpx.get(
                f"https://api.the-odds-api.com/v4/sports/{request.args.get('deporte','soccer_mexico_ligamx')}/odds",
                params={"apiKey":api_key,"regions":"eu","markets":"h2h","oddsFormat":"decimal"},timeout=10)
            real = []
            for m in r.json():
                for book in m.get("bookmakers",[]):
                    for o in book.get("markets",[{}])[0].get("outcomes",[]):
                        edge=round((1/o["price"]*o["price"]-1)*100*1.05,1)
                        if edge>=edge_min:
                            real.append({"partido":f"{m['home_team']} vs {m['away_team']}","liga":m["sport_title"],"resultado":o["name"],"casa":book["title"],"cuota":o["price"],"edge_porcentaje":edge,"es_value_bet":True})
            if real: results = real
        except: pass
    filtered=[v for v in results if v["edge_porcentaje"]>=edge_min]
    return jsonify({"total_encontrados":len(filtered),"value_bets":filtered})

# ── KELLY ──────────────────────────────────────────────────────────────────
@app.route("/api/kelly/calcular", methods=["POST"])
def kelly_calcular():
    d=request.get_json()
    bank=float(d.get("bankroll",5000)); odds=float(d.get("cuota_decimal",2.10))
    prob=float(d.get("probabilidad_estimada_pct",55))/100; frac=float(d.get("fraccion",0.5))
    b=odds-1; q=1-prob
    kp=(b*prob-q)/b if b>0 else 0
    ka=kp*frac; bet=max(0,bank*ka)
    return jsonify({"kelly_puro_pct":round(kp*100,2),"kelly_ajustado_pct":round(ka*100,2),
        "apuesta_sugerida":round(bet,2),"hay_valor":kp>0,
        "roi_esperado_pct":round((b*prob-q)*100,2),
        "recomendacion":"Apostar" if kp>0 else "NO apostar"})

# ── CLV ────────────────────────────────────────────────────────────────────
@app.route("/api/pro/clv/calcular")
def clv_calcular():
    mi=float(request.args.get("cuota_apostada",2.10))
    cl=float(request.args.get("cuota_cierre",1.85))
    pct=round((mi/cl-1)*100,2)
    return jsonify({"clv_pct":pct,"es_positivo":pct>0,
        "prob_implicita_apostada_pct":round(1/mi*100,2),
        "prob_implicita_cierre_pct":round(1/cl*100,2),
        "calidad":"positivo" if pct>0 else "negativo"})

# ── MONTE CARLO ────────────────────────────────────────────────────────────
@app.route("/api/pro/montecarlo/partido")
def montecarlo():
    lL=float(request.args.get("lambda_local",1.5))
    lV=float(request.args.get("lambda_visitante",1.1))
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
    pL,pD,pV=h/N*100,d/N*100,a/N*100
    avg=sum(gols)/N
    return jsonify({
        "simulaciones":N,
        "probabilidades":{"local_pct":round(pL,1),"empate_pct":round(pD,1),"visitante_pct":round(pV,1)},
        "cuotas_justas_sin_vig":{"local":round(100/pL,2) if pL>0 else 99,"empate":round(100/pD,2) if pD>0 else 99,"visitante":round(100/pV,2) if pV>0 else 99},
        "mercados_adicionales":{"avg_goles_totales":round(avg,2),"prob_over_2_5_pct":round(sum(1 for g in gols if g>2.5)/N*100,1),"prob_over_1_5_pct":round(sum(1 for g in gols if g>1.5)/N*100,1)},
    })

# ── SHARP MONEY ────────────────────────────────────────────────────────────
@app.route("/api/sharp/analizar")
def sharp_analizar():
    from services.sharp_money import analizar_partido_sharp
    partido     = request.args.get("partido","Local vs Visitante")
    linea_ap    = float(request.args.get("linea_apertura",2.10))
    linea_act   = float(request.args.get("linea_actual",1.95))
    pct_boletos = float(request.args.get("pct_boletos_local",30))
    pct_dinero  = float(request.args.get("pct_dinero_local",60))
    dias        = int(request.args.get("dias_antes",2))
    casas_raw   = request.args.get("lineas_casas","{}")
    try:
        casas = json.loads(casas_raw)
    except Exception:
        casas = {}
    return jsonify(analizar_partido_sharp(
        partido, linea_ap, linea_act, pct_boletos, pct_dinero,
        lineas_por_casa=casas if casas else None,
        dias_antes=dias,
    ))

@app.route("/api/sharp/steam")
def sharp_steam():
    from services.sharp_money import detectar_steam
    movs_raw = request.args.get("movimientos","[]")
    try:
        movs = json.loads(movs_raw)
    except Exception:
        movs = []
    if not movs:
        movs = [
            {"casa":"Pinnacle","linea_antes":2.10,"linea_ahora":1.85},
            {"casa":"Bet365","linea_antes":2.15,"linea_ahora":1.90},
            {"casa":"Codere","linea_antes":2.18,"linea_ahora":1.92},
        ]
    return jsonify(detectar_steam(movs))

# ── NLP SENTIMIENTO ────────────────────────────────────────────────────────
@app.route("/api/nlp/scan")
def nlp_scan():
    from services.nlp_sentiment import scan_completo
    home = request.args.get("home","Club América")
    away = request.args.get("away","Guadalajara")
    return jsonify(scan_completo(home, away))

@app.route("/api/nlp/noticias")
def nlp_noticias():
    from services.nlp_sentiment import fetch_noticias, detectar_lesiones
    noticias = fetch_noticias(20)
    for n in noticias:
        n["alertas"] = detectar_lesiones(n["titulo"]+" "+n["desc"])
    return jsonify({"noticias":noticias,"total":len(noticias)})

# ── BACKTESTING ────────────────────────────────────────────────────────────
@app.route("/api/backtest")
def backtest_run():
    from services.progol import HISTORIAL_DEMO
    from services.backtesting import backtest, backtest_por_modelo
    ventana = int(request.args.get("ventana",20))
    modo    = request.args.get("modo","ensemble")
    if modo == "comparar":
        return jsonify(backtest_por_modelo(HISTORIAL_DEMO, ventana))
    return jsonify(backtest(HISTORIAL_DEMO, ventana))

# ── SCHEDULER ──────────────────────────────────────────────────────────────
scheduler = BackgroundScheduler()
scheduler.add_job(lambda: print("ApuestasPro tick"), "interval", hours=1)
scheduler.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT",8000)))
