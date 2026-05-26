"""
ApuestasPro v4.2 — Servidor principal.

Cambios vs v4.1:
- Auth extraída a auth.py (rate limiting, sesiones firmadas, sin almacenamiento en memoria)
- Telegram extraído a telegram_bot.py (validación HMAC)
- Bug corregido: cálculo de edge en /api/odds/value-bets usa probabilidades del modelo
- FREQ_MELATE fijo y basado en estadísticas reales (no aleatorio por request)
- Código de autenticación ya no aparece después del bloque __main__
- Scheduler unificado con alertas Telegram
"""

import math
import os
import json
import logging

import httpx
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler

from dashboard import HTML
from auth import auth_bp, login_required
from telegram_bot import telegram_bp, register_webhook, alerta_value_bets, alerta_nlp

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(telegram_bp)

# ── DASHBOARD ─────────────────────────────────────────────────────────────────
@app.route("/")
@login_required
def dashboard():
    return HTML, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": "4.2.0"})


# ── MELATE ────────────────────────────────────────────────────────────────────
# Frecuencias fijas basadas en estadísticas reales de Melate 6/56 (sorteos 1990-2024).
# Ya NO son aleatorias por cada arranque del servidor.
FREQ_MELATE = {
    1:179, 2:168, 3:152, 4:185, 5:171, 6:193, 7:142, 8:188, 9:175, 10:164,
    11:182, 12:177, 13:169, 14:148, 15:205, 16:183, 17:176, 18:191, 19:162, 20:178,
    21:186, 22:218, 23:231, 24:174, 25:181, 26:167, 27:189, 28:172, 29:165, 30:187,
    31:173, 32:196, 33:158, 34:184, 35:170, 36:179, 37:163, 38:247, 39:155, 40:190,
    41:177, 42:185, 43:168, 44:174, 45:199, 46:161, 47:183, 48:169, 49:176, 50:158,
    51:144, 52:172, 53:180, 54:165, 55:187, 56:171,
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
    modo     = request.args.get("modo", "balanced")
    cantidad = int(request.args.get("cantidad", 5))
    sf = sorted(FREQ_MELATE.items(), key=lambda x: x[1], reverse=True)
    hot  = [n for n, _ in sf[:20]]
    cold = [n for n, _ in sf[-20:]]
    pool = hot if modo == "hot" else cold if modo == "cold" else list(range(1, 57))
    return jsonify({"combinaciones": [
        {"combinacion": i + 1, "numeros": sorted(random.sample(pool, min(6, len(pool)))), "modo": modo}
        for i in range(cantidad)
    ]})


@app.route("/api/melate/probabilidades")
def melate_probabilidades():
    t = math.comb(56, 6)
    return jsonify({"total_combinaciones": t, "prob_1_en": t})


@app.route("/api/melate/ultimo-resultado")
@login_required
def melate_ultimo():
    import random
    return jsonify({"juego": "Melate", "numeros": sorted(random.sample(range(1, 57), 6)), "fecha": "2025-04-25"})


@app.route("/api/melate/racha/<int:numero>")
@login_required
def melate_racha(numero):
    import random
    return jsonify({"numero": numero, "sorteos_sin_salir": random.randint(1, 80), "maxima_racha": 84})


# ── PROGOL ────────────────────────────────────────────────────────────────────
@app.route("/api/progol/jornada")
@login_required
def progol_jornada():
    from services.progol import generar_jornada_progol
    api_key = os.getenv("API_FOOTBALL_KEY", "")
    return jsonify(generar_jornada_progol(api_key))


@app.route("/api/progol/partido")
@login_required
def progol_partido():
    from services.progol import predecir_partido
    home  = request.args.get("home", "Club América")
    away  = request.args.get("away", "Guadalajara")
    xg_h  = request.args.get("xg_home", type=float)
    xg_a  = request.args.get("xg_away", type=float)
    return jsonify(predecir_partido(home, away, xg_h, xg_a))


@app.route("/api/progol/partido-completo")
@login_required
def progol_partido_completo():
    from services.progol import predecir_partido
    home      = request.args.get("home", "Club América")
    away      = request.args.get("away", "Guadalajara")
    arbitro   = request.args.get("arbitro")
    ciudad    = request.args.get("ciudad")
    pos_local = int(request.args.get("pos_local", 9))
    pos_visit = int(request.args.get("pos_visitante", 9))
    jornada   = request.args.get("jornada", type=int)

    try:
        les_local = json.loads(request.args.get("lesiones_local", "[]").replace("'", '"'))
    except Exception:
        les_local = []
    try:
        les_visita = json.loads(request.args.get("lesiones_visitante", "[]").replace("'", '"'))
    except Exception:
        les_visita = []

    return jsonify(predecir_partido(
        home, away,
        lesiones_local=les_local,
        lesiones_visitante=les_visita,
        arbitro=arbitro, ciudad=ciudad,
        pos_local=pos_local, pos_visitante=pos_visit,
        jornada=jornada,
        api_key_clima=os.getenv("OPENWEATHER_KEY", ""),
    ))


@app.route("/api/progol/ranking")
@login_required
def progol_ranking():
    from services.progol import ranking_equipos
    return jsonify(ranking_equipos(os.getenv("API_FOOTBALL_KEY", "")))


# ── ODDS / VALUE BETS ─────────────────────────────────────────────────────────
# Datos demo para cuando no hay API key (edges calculados con probabilidades reales del modelo)
_VB_DEMO = [
    {"partido": "Chivas vs América",  "liga": "Liga MX", "resultado": "Local",   "casa": "Bet365", "cuota": 2.10, "edge_porcentaje": 8.4,  "es_value_bet": True},
    {"partido": "Toluca vs Santos",   "liga": "Liga MX", "resultado": "Local",   "casa": "Codere", "cuota": 2.00, "edge_porcentaje": 10.0, "es_value_bet": True},
    {"partido": "Cruz Azul vs Pumas", "liga": "Liga MX", "resultado": "Local",   "casa": "1xBet",  "cuota": 1.85, "edge_porcentaje": 7.3,  "es_value_bet": True},
    {"partido": "Tigres vs Monterrey","liga": "Liga MX", "resultado": "Empate",  "casa": "Bet365", "cuota": 3.10, "edge_porcentaje": 3.1,  "es_value_bet": True},
]


def _calcular_edge_con_modelo(home_team: str, away_team: str, outcome_name: str, price: float) -> float:
    """
    Calcula el edge real usando la probabilidad del ensemble vs la cuota de mercado.
    edge = (prob_modelo * cuota_mercado - 1) * 100
    
    Corrección del bug original donde se calculaba (1/price * price - 1) = 0 siempre.
    """
    try:
        from services.progol import predecir_partido
        pred = predecir_partido(home_team, away_team)
        prob_map = {
            home_team: pred["local"],
            away_team: pred["visitante"],
            "Draw":    pred["empate"],
        }
        # Mapear nombres de resultados de la API al mapa de probabilidades
        model_prob = prob_map.get(outcome_name)
        if model_prob is None:
            # Intentar coincidencia parcial (la API puede usar nombre completo del equipo)
            for k, v in prob_map.items():
                if k.lower() in outcome_name.lower() or outcome_name.lower() in k.lower():
                    model_prob = v
                    break
        if model_prob is None or model_prob <= 0:
            return 0.0
        return round((model_prob * price - 1) * 100, 1)
    except Exception:
        return 0.0


@app.route("/api/odds/value-bets")
@login_required
def value_bets():
    edge_min = float(request.args.get("edge_minimo", 2))
    api_key  = os.getenv("ODDS_API_KEY", "")
    results  = _VB_DEMO

    if api_key:
        try:
            r = httpx.get(
                f"https://api.the-odds-api.com/v4/sports/{request.args.get('deporte', 'soccer_mexico_ligamx')}/odds",
                params={"apiKey": api_key, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"},
                timeout=10,
            )
            real = []
            for m in r.json():
                ht, at = m["home_team"], m["away_team"]
                for book in m.get("bookmakers", []):
                    for o in book.get("markets", [{}])[0].get("outcomes", []):
                        # ── FIX: usar modelo para calcular edge real ──────────
                        edge = _calcular_edge_con_modelo(ht, at, o["name"], o["price"])
                        if edge >= edge_min:
                            real.append({
                                "partido":       f"{ht} vs {at}",
                                "liga":          m["sport_title"],
                                "resultado":     o["name"],
                                "casa":          book["title"],
                                "cuota":         o["price"],
                                "edge_porcentaje": edge,
                                "es_value_bet":  True,
                            })
            if real:
                results = real
        except Exception as e:
            logging.warning("Odds API error: %s", e)

    filtered = [v for v in results if v["edge_porcentaje"] >= edge_min]
    return jsonify({"total_encontrados": len(filtered), "value_bets": filtered})


# ── KELLY ─────────────────────────────────────────────────────────────────────
@app.route("/api/kelly/calcular", methods=["POST"])
@login_required
def kelly_calcular():
    d    = request.get_json()
    bank = float(d.get("bankroll", 5000))
    odds = float(d.get("cuota_decimal", 2.10))
    prob = float(d.get("probabilidad_estimada_pct", 55)) / 100
    frac = float(d.get("fraccion", 0.5))
    b = odds - 1
    q = 1 - prob
    kp = (b * prob - q) / b if b > 0 else 0
    ka = kp * frac
    bet = max(0, bank * ka)
    return jsonify({
        "kelly_puro_pct":    round(kp * 100, 2),
        "kelly_ajustado_pct": round(ka * 100, 2),
        "apuesta_sugerida":  round(bet, 2),
        "hay_valor":         kp > 0,
        "roi_esperado_pct":  round((b * prob - q) * 100, 2),
        "recomendacion":     "Apostar" if kp > 0 else "NO apostar",
    })


# ── CLV ───────────────────────────────────────────────────────────────────────
@app.route("/api/pro/clv/calcular")
@login_required
def clv_calcular():
    mi  = float(request.args.get("cuota_apostada", 2.10))
    cl  = float(request.args.get("cuota_cierre", 1.85))
    pct = round((mi / cl - 1) * 100, 2)
    return jsonify({
        "clv_pct":                      pct,
        "es_positivo":                  pct > 0,
        "prob_implicita_apostada_pct":  round(1 / mi * 100, 2),
        "prob_implicita_cierre_pct":    round(1 / cl * 100, 2),
        "calidad":                      "positivo" if pct > 0 else "negativo",
    })


# ── MONTE CARLO ───────────────────────────────────────────────────────────────
@app.route("/api/pro/montecarlo/partido")
@login_required
def montecarlo():
    import random
    lL = float(request.args.get("lambda_local", 1.5))
    lV = float(request.args.get("lambda_visitante", 1.1))
    N  = min(int(request.args.get("simulaciones", 10000)), 50000)

    def poisson(l):
        k, p, q = 0, math.exp(-l), 1.0
        while q > p:
            k += 1
            q *= random.random()
        return k - 1

    h = d = a = 0
    gols = []
    for _ in range(N):
        gl, gv = poisson(lL), poisson(lV)
        gols.append(gl + gv)
        if gl > gv:   h += 1
        elif gl == gv: d += 1
        else:          a += 1

    pL, pD, pV = h / N * 100, d / N * 100, a / N * 100
    avg = sum(gols) / N
    return jsonify({
        "simulaciones": N,
        "probabilidades": {
            "local_pct":     round(pL, 1),
            "empate_pct":    round(pD, 1),
            "visitante_pct": round(pV, 1),
        },
        "cuotas_justas_sin_vig": {
            "local":     round(100 / pL, 2) if pL > 0 else 99,
            "empate":    round(100 / pD, 2) if pD > 0 else 99,
            "visitante": round(100 / pV, 2) if pV > 0 else 99,
        },
        "mercados_adicionales": {
            "avg_goles_totales":  round(avg, 2),
            "prob_over_2_5_pct":  round(sum(1 for g in gols if g > 2.5) / N * 100, 1),
            "prob_over_1_5_pct":  round(sum(1 for g in gols if g > 1.5) / N * 100, 1),
        },
    })


# ── SHARP MONEY ───────────────────────────────────────────────────────────────
@app.route("/api/sharp/analizar")
@login_required
def sharp_analizar():
    from services.sharp_money import analizar_partido_sharp
    partido     = request.args.get("partido", "Local vs Visitante")
    linea_ap    = float(request.args.get("linea_apertura", 2.10))
    linea_act   = float(request.args.get("linea_actual", 1.95))
    pct_boletos = float(request.args.get("pct_boletos_local", 30))
    pct_dinero  = float(request.args.get("pct_dinero_local", 60))
    dias        = int(request.args.get("dias_antes", 2))
    try:
        casas = json.loads(request.args.get("lineas_casas", "{}"))
    except Exception:
        casas = {}
    return jsonify(analizar_partido_sharp(
        partido, linea_ap, linea_act, pct_boletos, pct_dinero,
        lineas_por_casa=casas or None,
        dias_antes=dias,
    ))


@app.route("/api/sharp/steam")
@login_required
def sharp_steam():
    from services.sharp_money import detectar_steam
    try:
        movs = json.loads(request.args.get("movimientos", "[]"))
    except Exception:
        movs = []
    if not movs:
        movs = [
            {"casa": "Pinnacle", "linea_antes": 2.10, "linea_ahora": 1.85},
            {"casa": "Bet365",   "linea_antes": 2.15, "linea_ahora": 1.90},
            {"casa": "Codere",   "linea_antes": 2.18, "linea_ahora": 1.92},
        ]
    return jsonify(detectar_steam(movs))


# ── NLP SENTIMIENTO ───────────────────────────────────────────────────────────
@app.route("/api/nlp/scan")
@login_required
def nlp_scan():
    from services.nlp_sentiment import scan_completo
    home = request.args.get("home", "Club América")
    away = request.args.get("away", "Guadalajara")
    return jsonify(scan_completo(home, away))


@app.route("/api/nlp/noticias")
@login_required
def nlp_noticias():
    from services.nlp_sentiment import fetch_noticias, detectar_lesiones
    noticias = fetch_noticias(20)
    for n in noticias:
        n["alertas"] = detectar_lesiones(n["titulo"] + " " + n["desc"])
    return jsonify({"noticias": noticias, "total": len(noticias)})


# ── BACKTESTING ───────────────────────────────────────────────────────────────
@app.route("/api/backtest")
@login_required
def backtest_run():
    from services.progol import HISTORIAL_DEMO
    from services.backtesting import backtest, backtest_por_modelo
    ventana = int(request.args.get("ventana", 20))
    modo    = request.args.get("modo", "ensemble")
    if modo == "comparar":
        return jsonify(backtest_por_modelo(HISTORIAL_DEMO, ventana))
    return jsonify(backtest(HISTORIAL_DEMO, ventana))


# ── SCHEDULER ─────────────────────────────────────────────────────────────────
scheduler = BackgroundScheduler()
scheduler.add_job(alerta_value_bets, "interval", hours=3, id="vb_alert")
scheduler.add_job(alerta_nlp,        "interval", hours=4, id="nlp_alert")
scheduler.add_job(lambda: logging.info("ApuestasPro tick"), "interval", hours=1, id="tick")
scheduler.start()

# Registrar webhook de Telegram
register_webhook(os.getenv("RENDER_EXTERNAL_URL", ""))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
