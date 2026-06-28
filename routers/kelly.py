"""
Router para Criterio de Kelly y gestión de bankroll.
"""
from flask import Blueprint, jsonify, request
from auth import login_required
from services.estadisticas import criterio_kelly

router = Blueprint("kelly", __name__)


@router.route("/calcular", methods=["POST"])
@login_required
def calcular_kelly():
    """
    Calcula el tamaño óptimo de apuesta con el Criterio de Kelly.
    fraccion: 1.0=Kelly completo, 0.5=Medio Kelly, 0.25=Cuarto Kelly
    """
    data = request.get_json()
    return jsonify(criterio_kelly(
        bankroll=data.get("bankroll", 5000),
        cuota_decimal=data.get("cuota_decimal", 2.0),
        probabilidad_estimada=data.get("probabilidad_estimada_pct", 55) / 100,
        fraccion=data.get("fraccion", 0.5),
    ))


@router.route("/analizar-historial", methods=["POST"])
@login_required
def analizar_historial():
    """
    Analiza el historial de apuestas y calcula métricas de rendimiento.
    """
    apuestas = request.get_json()
    if not apuestas:
        return jsonify({"error": "Sin apuestas para analizar"})

    ganadas = [a for a in apuestas if a["resultado"]]
    perdidas = [a for a in apuestas if not a["resultado"]]

    total_apostado = sum(a["apuesta"] for a in apuestas)
    ganancias = sum(a["apuesta"] * (a["cuota"] - 1) for a in ganadas)
    perdidas_total = sum(a["apuesta"] for a in perdidas)
    profit = ganancias - perdidas_total

    tasa_acierto = len(ganadas) / len(apuestas) if apuestas else 0
    roi = (profit / total_apostado * 100) if total_apostado > 0 else 0

    cuotas_avg = sum(a["cuota"] for a in apuestas) / len(apuestas)

    racha = 0
    for a in reversed(apuestas):
        if a["resultado"]:
            if racha >= 0:
                racha += 1
            else:
                break
        else:
            if racha <= 0:
                racha -= 1
            else:
                break

    return jsonify({
        "total_apuestas": len(apuestas),
        "ganadas": len(ganadas),
        "perdidas": len(perdidas),
        "tasa_acierto_pct": round(tasa_acierto * 100, 1),
        "total_apostado": round(total_apostado, 2),
        "profit_neto": round(profit, 2),
        "roi_pct": round(roi, 2),
        "cuota_promedio": round(cuotas_avg, 2),
        "racha_actual": racha,
        "clasificacion_roi": (
            "Excelente" if roi > 10 else
            "Bueno" if roi > 5 else
            "Regular" if roi > 0 else
            "Negativo – revisar estrategia"
        ),
    })


@router.route("/guia-bankroll", methods=["GET"])
@login_required
def guia_bankroll():
    """Guía de gestión de bankroll y juego responsable."""
    return jsonify({
        "principios": [
            "Nunca apostar más del 5% del bankroll en una sola apuesta",
            "Usar Medio Kelly (0.5) o menos para reducir varianza",
            "Registrar todas las apuestas para calcular ROI real",
            "Establecer límite de pérdida diaria (ej. 10% del bankroll)",
            "Solo apostar en mercados donde tienes edge demostrable",
        ],
        "fracciones_kelly": {
            "kelly_completo": "Matemáticamente óptimo pero alta varianza. Solo para expertos.",
            "medio_kelly": "Recomendado. Reduce riesgo de ruina un 50%.",
            "cuarto_kelly": "Muy conservador. Bueno para principiantes.",
        },
        "juego_responsable": {
            "establece_limites": "Define cuánto puedes perder sin afectar tu vida.",
            "no_perseguir_perdidas": "Nunca aumentes apuestas para recuperar pérdidas.",
            "ayuda": "CONADIC México: 800 290 0024 (gratuito, 24/7)",
        },
    })
