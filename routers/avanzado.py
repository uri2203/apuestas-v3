"""
Router v2 – Funciones profesionales avanzadas:
CLV, Monte Carlo, Sharp Money, Riesgo de Ruina, Pares/Tripletas.
"""
from flask import Blueprint, jsonify, request
from services.motor_avanzado import (
    calcular_clv,
    analizar_historial_clv,
    detectar_sharp_money,
    monte_carlo_loteria,
    monte_carlo_partido,
    calcular_riesgo_ruina,
    analizar_pares_frecuentes,
    analizar_tripletas,
    lstm_simulado,
)
from services.scraper import obtener_historico_melate
from services.estadisticas import calcular_frecuencias

router = Blueprint("avanzado", __name__)


# ┄┄ CLV ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

@router.route("/clv/calcular", methods=["GET"])
def clv_calcular():
    """Calcula el Closing Line Value de una apuesta."""
    cuota_apostada = float(request.args.get("cuota_apostada"))
    cuota_cierre = float(request.args.get("cuota_cierre"))
    return jsonify(calcular_clv(cuota_apostada, cuota_cierre))


@router.route("/clv/analizar-historial", methods=["POST"])
def clv_historial():
    """Analiza historial con métricas CLV profesionales."""
    apuestas = request.get_json()
    return jsonify(analizar_historial_clv([a for a in apuestas]))


# ┄┄ SHARP MONEY ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

@router.route("/sharp/detectar", methods=["GET"])
def sharp_detectar():
    """Detecta Sharp Money y Reverse Line Movement."""
    cuota_apertura = float(request.args.get("cuota_apertura"))
    cuota_actual = float(request.args.get("cuota_actual"))
    pct_publico = float(request.args.get("pct_publico"))
    return jsonify(detectar_sharp_money(cuota_apertura, cuota_actual, pct_publico))


# ┄┄ MONTE CARLO ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

@router.route("/montecarlo/melate", methods=["GET"])
def mc_melate():
    """Monte Carlo para combinación de Melate."""
    numeros = request.args.get("numeros", "7,14,23,38,45,50")
    simulaciones = int(request.args.get("simulaciones", 10000))
    try:
        nums = [int(x.strip()) for x in numeros.split(",") if x.strip().isdigit()]
        if len(nums) != 6 or not all(1 <= n <= 56 for n in nums):
            return jsonify({"error": "Se requieren exactamente 6 números entre 1 y 56"})
    except Exception:
        return jsonify({"error": "Formato inválido. Usa: 7,14,23,38,45,50"})

    return jsonify(monte_carlo_loteria(6, 56, nums, simulaciones))


@router.route("/montecarlo/partido", methods=["GET"])
def mc_partido():
    """Monte Carlo para partido de fútbol con distribución Poisson."""
    lambda_local = float(request.args.get("lambda_local", 1.5))
    lambda_visitante = float(request.args.get("lambda_visitante", 1.1))
    simulaciones = int(request.args.get("simulaciones", 10000))
    return jsonify(monte_carlo_partido(lambda_local, lambda_visitante, simulaciones))


# ┄┄ RIESGO DE RUINA ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

@router.route("/bankroll/riesgo-ruina", methods=["GET"])
def riesgo_ruina():
    """Calcula probabilidad de ruina mediante Monte Carlo."""
    bankroll = float(request.args.get("bankroll", 5000))
    apuesta_pct = float(request.args.get("apuesta_pct", 2.0))
    win_rate = float(request.args.get("win_rate", 55.0))
    odds = float(request.args.get("odds", 2.0))
    n_apuestas = int(request.args.get("n_apuestas", 500))
    return jsonify(calcular_riesgo_ruina(bankroll, apuesta_pct / 100, win_rate / 100, odds, n_apuestas))


# ┄┄ PARES Y PATRONES ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄

@router.route("/melate/pares", methods=["GET"])
def pares_frecuentes():
    """Pares de números más frecuentes en el histórico de Melate."""
    limite_sorteos = int(request.args.get("limite_sorteos", 500))
    top = int(request.args.get("top", 20))
    data = obtener_historico_melate(limite_sorteos)
    if not data:
        return jsonify({"error": "Sin datos históricos"})
    return jsonify({
        "sorteos_analizados": len(data),
        "pares": analizar_pares_frecuentes(data, top),
    })


@router.route("/melate/tripletas", methods=["GET"])
def tripletas_frecuentes():
    """Tripletas de números más frecuentes."""
    limite_sorteos = int(request.args.get("limite_sorteos", 500))
    top = int(request.args.get("top", 10))
    data = obtener_historico_melate(limite_sorteos)
    if not data:
        return jsonify({"error": "Sin datos históricos"})
    return jsonify({
        "sorteos_analizados": len(data),
        "tripletas": analizar_tripletas(data, top),
    })


@router.route("/melate/lstm", methods=["GET"])
def generar_lstm():
    """Genera combinaciones con modelo LSTM simulado."""
    cantidad = int(request.args.get("cantidad", 5))
    data = obtener_historico_melate(500)
    freq = calcular_frecuencias(data) if data else {}
    return jsonify({
        "metodo": "LSTM simulado",
        "combinaciones": [lstm_simulado(freq) for _ in range(cantidad)],
        "nota": "Modelo completo requiere TensorFlow entrenado con histórico completo",
    })
