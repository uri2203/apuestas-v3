"""
Router v2 – Funciones profesionales avanzadas:
CLV, Monte Carlo, Sharp Money, Riesgo de Ruina.
"""
from flask import Blueprint, jsonify, request
from auth import login_required
from services.motor_avanzado import (
    calcular_clv,
    analizar_historial_clv,
    detectar_sharp_money,
    monte_carlo_partido,
    calcular_riesgo_ruina,
)

router = Blueprint("avanzado", __name__)

# ┄┄ CLV ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

@router.route("/clv/calcular", methods=["GET"])
@login_required
def clv_calcular():
    """Calcula el Closing Line Value de una apuesta."""
    cuota_apostada = float(request.args.get("cuota_apostada"))
    cuota_cierre = float(request.args.get("cuota_cierre"))
    return jsonify(calcular_clv(cuota_apostada, cuota_cierre))

@router.route("/clv/analizar-historial", methods=["POST"])
@login_required
def clv_historial():
    """Analiza historial con métricas CLV profesionales."""
    apuestas = request.get_json()
    return jsonify(analizar_historial_clv([a for a in apuestas]))

# ┄┄ SHARP MONEY ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

@router.route("/sharp/detectar", methods=["GET"])
@login_required
def sharp_detectar():
    """Detecta Sharp Money y Reverse Line Movement."""
    cuota_apertura = float(request.args.get("cuota_apertura"))
    cuota_actual = float(request.args.get("cuota_actual"))
    pct_publico = float(request.args.get("pct_publico"))
    return jsonify(detectar_sharp_money(cuota_apertura, cuota_actual, pct_publico))

# ┄┄ MONTE CARLO ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

@router.route("/montecarlo/partido", methods=["GET"])
@login_required
def mc_partido():
    """Monte Carlo para partido de fútbol con distribución Poisson."""
    lambda_local = float(request.args.get("lambda_local", 1.5))
    lambda_visitante = float(request.args.get("lambda_visitante", 1.1))
    simulaciones = int(request.args.get("simulaciones", 10000))
    return jsonify(monte_carlo_partido(lambda_local, lambda_visitante, simulaciones))

# ┄┄ RIESGO DE RUINA ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

@router.route("/bankroll/riesgo-ruina", methods=["GET"])
@login_required
def riesgo_ruina():
    """Calcula probabilidad de ruina mediante Monte Carlo."""
    bankroll = float(request.args.get("bankroll", 5000))
    apuesta_pct = float(request.args.get("apuesta_pct", 2.0))
    win_rate = float(request.args.get("win_rate", 55.0))
    odds = float(request.args.get("odds", 2.0))
    n_apuestas = int(request.args.get("n_apuestas", 500))
    return jsonify(calcular_riesgo_ruina(bankroll, apuesta_pct / 100, win_rate / 100, odds, n_apuestas))

# ┄┄ PARES Y PATRONES ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

