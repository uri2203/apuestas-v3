"""
Router v2 — Funciones profesionales avanzadas:
CLV, Monte Carlo, Sharp Money, Riesgo de Ruina, Pares/Tripletas.
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
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

router = APIRouter()


# ── CLV ──────────────────────────────────────────────────────────────────────

@router.get("/clv/calcular")
async def clv_calcular(cuota_apostada: float, cuota_cierre: float):
    """Calcula el Closing Line Value de una apuesta."""
    return calcular_clv(cuota_apostada, cuota_cierre)


class ApuestaCLV(BaseModel):
    cuota: float
    cuota_cierre: float
    resultado: bool
    monto: float = 100.0


@router.post("/clv/analizar-historial")
async def clv_historial(apuestas: list[ApuestaCLV]):
    """Analiza historial con métricas CLV profesionales."""
    return analizar_historial_clv([a.dict() for a in apuestas])


# ── SHARP MONEY ──────────────────────────────────────────────────────────────

@router.get("/sharp/detectar")
async def sharp_detectar(
    cuota_apertura: float,
    cuota_actual: float,
    pct_publico: float = Query(description="% de apuestas del público en este lado"),
):
    """Detecta Sharp Money y Reverse Line Movement."""
    return detectar_sharp_money(cuota_apertura, cuota_actual, pct_publico)


# ── MONTE CARLO ───────────────────────────────────────────────────────────────

@router.get("/montecarlo/melate")
async def mc_melate(
    numeros: str = Query(description="6 números separados por coma, ej: 7,14,23,38,45,50"),
    simulaciones: int = Query(default=10000, le=100000),
):
    """Monte Carlo para combinación de Melate."""
    try:
        nums = [int(x.strip()) for x in numeros.split(",") if x.strip().isdigit()]
        if len(nums) != 6 or not all(1 <= n <= 56 for n in nums):
            return {"error": "Se requieren exactamente 6 números entre 1 y 56"}
    except Exception:
        return {"error": "Formato inválido. Usa: 7,14,23,38,45,50"}

    return monte_carlo_loteria(6, 56, nums, simulaciones)


@router.get("/montecarlo/partido")
async def mc_partido(
    lambda_local: float = Query(default=1.5, description="Goles esperados local (histórico)"),
    lambda_visitante: float = Query(default=1.1, description="Goles esperados visitante"),
    simulaciones: int = Query(default=10000, le=100000),
):
    """Monte Carlo para partido de fútbol con distribución Poisson."""
    return monte_carlo_partido(lambda_local, lambda_visitante, simulaciones)


# ── RIESGO DE RUINA ───────────────────────────────────────────────────────────

@router.get("/bankroll/riesgo-ruina")
async def riesgo_ruina(
    bankroll: float = Query(default=5000),
    apuesta_pct: float = Query(default=2.0, description="% del bankroll por apuesta"),
    win_rate: float = Query(default=55.0, description="% de apuestas ganadas"),
    odds: float = Query(default=2.0),
    n_apuestas: int = Query(default=500, le=5000),
):
    """Calcula probabilidad de ruina mediante Monte Carlo."""
    return calcular_riesgo_ruina(bankroll, apuesta_pct / 100, win_rate / 100, odds, n_apuestas)


# ── PARES Y PATRONES ─────────────────────────────────────────────────────────

@router.get("/melate/pares")
async def pares_frecuentes(limite_sorteos: int = 500, top: int = 20):
    """Pares de números más frecuentes en el histórico de Melate."""
    data = await obtener_historico_melate(limite_sorteos)
    if not data:
        return {"error": "Sin datos históricos"}
    return {
        "sorteos_analizados": len(data),
        "pares": analizar_pares_frecuentes(data, top),
    }


@router.get("/melate/tripletas")
async def tripletas_frecuentes(limite_sorteos: int = 500, top: int = 10):
    """Tripletas de números más frecuentes."""
    data = await obtener_historico_melate(limite_sorteos)
    if not data:
        return {"error": "Sin datos históricos"}
    return {
        "sorteos_analizados": len(data),
        "tripletas": analizar_tripletas(data, top),
    }


@router.get("/melate/lstm")
async def generar_lstm(cantidad: int = Query(default=5, le=20)):
    """Genera combinaciones con modelo LSTM simulado."""
    data = await obtener_historico_melate(500)
    freq = calcular_frecuencias(data) if data else {}
    return {
        "metodo": "LSTM simulado",
        "combinaciones": [lstm_simulado(freq) for _ in range(cantidad)],
        "nota": "Modelo completo requiere TensorFlow entrenado con histórico completo",
    }
