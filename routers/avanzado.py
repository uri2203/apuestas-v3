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

def _safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def _safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

# ┄┄ CLV ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

@router.route("/clv/calcular", methods=["GET"])
@login_required
def clv_calcular():
    """Calcula el Closing Line Value de una apuesta."""
    try:
        cuota_apostada = _safe_float(request.args.get("cuota_apostada"), 2.0)
        cuota_cierre = _safe_float(request.args.get("cuota_cierre"), 1.9)
        return jsonify(calcular_clv(cuota_apostada, cuota_cierre))
    except Exception as e:
        return jsonify({"error": str(e)[:200]})

@router.route("/clv/analizar-historial", methods=["POST"])
@login_required
def clv_historial():
    """Analiza historial con métricas CLV profesionales."""
    try:
        apuestas = request.get_json(silent=True) or []
        return jsonify(analizar_historial_clv([a for a in apuestas]) if isinstance(apuestas, list) else {"error": "Formato inválido"})
    except Exception as e:
        return jsonify({"error": str(e)[:200]})

# ┄┄ SHARP MONEY ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

@router.route("/sharp/detectar", methods=["GET"])
@login_required
def sharp_detectar():
    """Detecta Sharp Money y Reverse Line Movement."""
    try:
        cuota_apertura = _safe_float(request.args.get("cuota_apertura"), 2.0)
        cuota_actual = _safe_float(request.args.get("cuota_actual"), 1.9)
        pct_publico = _safe_float(request.args.get("pct_publico"), 50)
        return jsonify(detectar_sharp_money(cuota_apertura, cuota_actual, pct_publico))
    except Exception as e:
        return jsonify({"error": str(e)[:200]})

# ┄┄ MONTE CARLO ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

@router.route("/montecarlo/partido", methods=["GET"])
@login_required
def mc_partido():
    """Monte Carlo para partido de fútbol con distribución Poisson."""
    try:
        lambda_local = _safe_float(request.args.get("lambda_local"), 1.5)
        lambda_visitante = _safe_float(request.args.get("lambda_visitante"), 1.1)
        simulaciones = _safe_int(request.args.get("simulaciones"), 10000)
        return jsonify(monte_carlo_partido(lambda_local, lambda_visitante, simulaciones))
    except Exception as e:
        return jsonify({"error": str(e)[:200]})

# ┄┄ RIESGO DE RUINA ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

@router.route("/bankroll/riesgo-ruina", methods=["GET"])
@login_required
def riesgo_ruina():
    """Calcula probabilidad de ruina mediante Monte Carlo."""
    try:
        bankroll = _safe_float(request.args.get("bankroll"), 5000)
        apuesta_pct = _safe_float(request.args.get("apuesta_pct"), 2.0)
        win_rate = _safe_float(request.args.get("win_rate"), 55.0)
        odds = _safe_float(request.args.get("odds"), 2.0)
        n_apuestas = _safe_int(request.args.get("n_apuestas"), 500)
        return jsonify(calcular_riesgo_ruina(bankroll, apuesta_pct / 100, win_rate / 100, odds, n_apuestas))
    except Exception as e:
        return jsonify({"error": str(e)[:200]})

# ┄┄ PARES Y PATRONES ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

