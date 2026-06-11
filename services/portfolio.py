"""
Portfolio Inteligente — Kelly correlacionado + gestión multi-apuesta.

Problema: si apuestas a 3 equipos diferentes del mismo partido o
a múltiples partidos correlacionados, el riesgo real es mayor al estimado.

Este módulo:
  1. Lee apuestas activas de la DB
  2. Detecta correlaciones (misma liga, mismo día, equipos relacionados)
  3. Reduce stakes según correlación
  4. Ajusta al bankroll disponible
  5. Retorna recomendación de stake ajustado
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Penalización por tipo de correlación
CORRELATION_PENALTIES = {
    "mismo_partido": 0.0,        # misma selección en mismo partido → 100% overlap
    "misma_liga": 0.3,           # diferente partido, misma liga
    "mismo_dia": 0.15,           # mismo día calendario
    "mismo_deporte": 0.2,        # mismo deporte (ej. NFL spreads)
    "independiente": 0.0,        # sin correlación
}

MAX_STAKE_PCT = 0.05  # 5% max del bankroll por apuesta individual


def clasificar_correlacion(bet_a: dict, bet_b: dict) -> str:
    """Clasifica el nivel de correlación entre dos apuestas."""
    if bet_a.get("partido") == bet_b.get("partido"):
        return "mismo_partido"
    if bet_a.get("liga") and bet_b.get("liga") and bet_a["liga"] == bet_b["liga"]:
        return "misma_liga"
    if bet_a.get("deporte") and bet_b.get("deporte") and bet_a["deporte"] == bet_b["deporte"]:
        return "mismo_deporte"
    return "independiente"


def calcular_penalizacion(bets_activas: list[dict], nueva_apuesta: dict) -> float:
    """Calcula penalización compuesta por correlación vs portfolio existente."""
    if not bets_activas:
        return 0.0
    penalidad_max = 0.0
    for existing in bets_activas:
        corr = clasificar_correlacion(existing, nueva_apuesta)
        penalty = CORRELATION_PENALTIES.get(corr, 0.0)
        penalidad_max = max(penalidad_max, penalty)
    return penalidad_max


def kelly_correlacionado(
    prob: float, cuota: float,
    bankroll: float,
    bets_activas: list[dict] = None,
    fraccion_base: float = 0.25,
) -> dict:
    """
    Kelly ajustado por correlación con el portfolio existente.
    """
    if prob <= 0 or prob >= 1 or cuota <= 1:
        return {"stake": 0, "kelly_pct": 0, "recomendacion": "NO apostar"}

    b = cuota - 1
    q = 1 - prob
    kelly_full = (b * prob - q) / b if b > 0 else 0
    kelly_full = max(0, kelly_full)

    # Penalización por correlación
    penalizacion = calcular_penalizacion(bets_activas or [], {"partido": "?", "liga": "?"})
    fraccion_ajustada = fraccion_base * (1.0 - penalizacion)

    kelly_ajustado = kelly_full * fraccion_ajustada
    stake = min(bankroll * kelly_ajustado, bankroll * MAX_STAKE_PCT)
    kelly_pct = (stake / bankroll * 100) if bankroll > 0 else 0

    return {
        "stake": round(stake, 2),
        "kelly_pct": round(kelly_pct, 2),
        "kelly_full_pct": round(kelly_full * 100, 2),
        "fraccion_usada": fraccion_ajustada,
        "penalizacion_correlacion": penalizacion,
        "bankroll_disponible": round(bankroll, 2),
        "recomendacion": (
            f"Apostar ${stake:.2f} ({kelly_pct:.1f}% del bankroll)"
            if stake > 0 else "NO apostar"
        ),
    }


def get_portfolio_status() -> dict:
    """Estado actual del portfolio de apuestas activas."""
    from database import db, _fetchall

    try:
        with db() as conn:
            activas = _fetchall(conn,
                "SELECT * FROM bets WHERE resultado='pendiente' ORDER BY id DESC")
    except Exception as e:
        return {"error": str(e), "activas": [], "total_expuesto": 0}

    total_expuesto = sum(b.get("monto", 0) or 0 for b in activas)
    ganancia_potencial = sum(
        (b.get("monto", 0) or 0) * ((b.get("cuota", 1) or 1) - 1)
        for b in activas if b.get("cuota", 1) > 1
    )

    # Agrupar por liga para ver concentración
    por_liga = {}
    for b in activas:
        liga = b.get("liga", "desconocida")
        if liga not in por_liga:
            por_liga[liga] = {"total": 0, "monto": 0, "apuestas": []}
        por_liga[liga]["total"] += 1
        por_liga[liga]["monto"] += b.get("monto", 0) or 0
        por_liga[liga]["apuestas"].append({
            "partido": b.get("partido", ""),
            "seleccion": b.get("seleccion", ""),
            "cuota": b.get("cuota", 0),
            "monto": b.get("monto", 0),
        })

    return {
        "activas": activas,
        "total_apuestas": len(activas),
        "total_expuesto": round(total_expuesto, 2),
        "ganancia_potencial_max": round(ganancia_potencial, 2),
        "por_liga": por_liga,
    }


def recomendar_nueva_apuesta(
    partido: str, liga: str, seleccion: str,
    cuota: float, prob_modelo: float,
    bankroll: float = None,
    fraccion_kelly: float = 0.25,
) -> dict:
    """
    Recomendación completa para una nueva apuesta considerando el portfolio.
    """
    from database import db, _fetchall

    if bankroll is None:
        try:
            from database import get_bankroll_actual
            bankroll = get_bankroll_actual()
        except Exception:
            bankroll = 5000

    if bankroll <= 0:
        return {"error": "Bankroll insuficiente", "stake": 0}

    # Obtener apuestas activas
    try:
        with db() as conn:
            activas = _fetchall(conn,
                "SELECT * FROM bets WHERE resultado='pendiente'")
    except Exception:
        activas = []

    nueva = {
        "partido": partido,
        "liga": liga,
        "seleccion": seleccion,
        "cuota": cuota,
        "monto": 0,
    }

    kelly_res = kelly_correlacionado(
        prob_modelo, cuota, bankroll,
        bets_activas=activas,
        fraccion_base=fraccion_kelly,
    )

    # Calcular valor esperado
    edge = (prob_modelo * cuota - 1) * 100
    ev = (cuota - 1) * prob_modelo - (1 - prob_modelo)

    return {
        "partido": partido,
        "liga": liga,
        "seleccion": seleccion,
        "cuota": cuota,
        "prob_modelo_pct": round(prob_modelo * 100, 1),
        "edge_pct": round(edge, 2),
        "ev_por_unidad": round(ev, 4),
        "es_value": edge > 0,
        **kelly_res,
        "portfolio_actual": {
            "activas": len(activas),
            "expuesto_total": round(sum(b.get("monto", 0) or 0 for b in activas), 2),
        },
    }
