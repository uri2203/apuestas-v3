"""
Router para Criterio de Kelly y gestión de bankroll.
"""
from fastapi import APIRouter, Body
from services.estadisticas import criterio_kelly
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class KellyInput(BaseModel):
    bankroll: float
    cuota_decimal: float
    probabilidad_estimada_pct: float
    fraccion: Optional[float] = 0.5


class ApuestaHistorial(BaseModel):
    partido: str
    cuota: float
    probabilidad_pct: float
    apuesta: float
    resultado: bool  # True = ganó


@router.post("/calcular")
async def calcular_kelly(data: KellyInput):
    """
    Calcula el tamaño óptimo de apuesta con el Criterio de Kelly.
    fraccion: 1.0=Kelly completo, 0.5=Medio Kelly, 0.25=Cuarto Kelly
    """
    return criterio_kelly(
        bankroll=data.bankroll,
        cuota_decimal=data.cuota_decimal,
        probabilidad_estimada=data.probabilidad_estimada_pct / 100,
        fraccion=data.fraccion,
    )


@router.post("/analizar-historial")
async def analizar_historial(apuestas: list[ApuestaHistorial]):
    """
    Analiza el historial de apuestas y calcula métricas de rendimiento.
    """
    if not apuestas:
        return {"error": "Sin apuestas para analizar"}

    ganadas = [a for a in apuestas if a.resultado]
    perdidas = [a for a in apuestas if not a.resultado]

    total_apostado = sum(a.apuesta for a in apuestas)
    ganancias = sum(a.apuesta * (a.cuota - 1) for a in ganadas)
    perdidas_total = sum(a.apuesta for a in perdidas)
    profit = ganancias - perdidas_total

    tasa_acierto = len(ganadas) / len(apuestas) if apuestas else 0
    roi = (profit / total_apostado * 100) if total_apostado > 0 else 0

    cuotas_avg = sum(a.cuota for a in apuestas) / len(apuestas)

    # Racha actual
    racha = 0
    for a in reversed(apuestas):
        if a.resultado:
            if racha >= 0:
                racha += 1
            else:
                break
        else:
            if racha <= 0:
                racha -= 1
            else:
                break

    return {
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
            "Negativo — revisar estrategia"
        ),
    }


@router.get("/guia-bankroll")
async def guia_bankroll():
    """Guía de gestión de bankroll y juego responsable."""
    return {
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
    }
