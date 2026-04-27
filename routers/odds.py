"""
Router para apuestas deportivas.
Endpoints: odds, value bets, comparador, arbitrajes.
"""
from fastapi import APIRouter, Query
from services.scraper import obtener_odds_deportivos
from services.estadisticas import detectar_value_bet, comparar_odds_casas
import os

router = APIRouter()


@router.get("/odds/{deporte}")
async def obtener_odds(
    deporte: str = "soccer_mexico_ligamx",
    casas: int = Query(default=5, le=10),
):
    """
    Odds actuales de múltiples casas de apuestas.
    deportes disponibles: soccer_mexico_ligamx, basketball_nba, soccer_uefa_champs_league
    """
    api_key = os.getenv("ODDS_API_KEY", "")
    data = await obtener_odds_deportivos(deporte, api_key)
    return {"deporte": deporte, "total_partidos": len(data), "partidos": data[:20]}


@router.get("/value-bets")
async def value_bets(
    deporte: str = Query(default="soccer_mexico_ligamx"),
    edge_minimo: float = Query(default=2.0, description="Edge mínimo en % para considerar value bet"),
):
    """
    Detecta automáticamente value bets con edge positivo.
    """
    api_key = os.getenv("ODDS_API_KEY", "")
    partidos = await obtener_odds_deportivos(deporte, api_key)

    value_bets_detectados = []

    for partido in partidos:
        for resultado, cuotas_por_casa in partido.get("odds", {}).items():
            for casa, cuota in cuotas_por_casa.items():
                if cuota <= 1:
                    continue
                # Estimación de probabilidad real usando promedio de todas las casas
                todas_cuotas = [
                    c
                    for casas_data in partido["odds"].values()
                    for c in casas_data.values()
                    if c > 1
                ]
                prob_promedio = 1 / (sum(1 / c for c in todas_cuotas) / len(todas_cuotas)) if todas_cuotas else 0.5

                analisis = detectar_value_bet(cuota, prob_promedio)
                if analisis["edge_porcentaje"] >= edge_minimo:
                    value_bets_detectados.append({
                        "partido": f"{partido['local']} vs {partido['visitante']}",
                        "liga": partido.get("liga", deporte),
                        "fecha": partido.get("fecha"),
                        "resultado": resultado,
                        "casa": casa,
                        **analisis,
                    })

    value_bets_detectados.sort(key=lambda x: x["edge_porcentaje"], reverse=True)
    return {
        "deporte": deporte,
        "edge_minimo_pct": edge_minimo,
        "total_encontrados": len(value_bets_detectados),
        "value_bets": value_bets_detectados[:20],
    }


@router.get("/comparar/{partido_id}")
async def comparar_partido(partido_id: str, deporte: str = "soccer_mexico_ligamx"):
    """
    Compara odds de un partido específico entre todas las casas disponibles.
    Detecta arbitrajes automáticamente.
    """
    api_key = os.getenv("ODDS_API_KEY", "")
    partidos = await obtener_odds_deportivos(deporte, api_key)

    partido = next((p for p in partidos if p["id"] == partido_id), None)
    if not partido:
        return {"error": "Partido no encontrado", "id": partido_id}

    comparacion = comparar_odds_casas(
        partido["odds"],
        f"{partido['local']} vs {partido['visitante']}",
    )
    return comparacion


@router.post("/calcular-valor")
async def calcular_valor(cuota: float, probabilidad_pct: float, apuesta: float = 100):
    """
    Calcula el valor esperado de una apuesta específica.
    """
    prob = probabilidad_pct / 100
    analisis = detectar_value_bet(cuota, prob)
    analisis["valor_esperado_apuesta"] = round(analisis["valor_esperado_por_unidad"] * apuesta, 2)
    analisis["apuesta"] = apuesta
    return analisis
