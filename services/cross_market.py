"""
Alertas Cross-Mercado — detecta inconsistencias entre mercados
que revelan edges invisibles en un solo mercado.

Ejemplo:
  - H2H: Team A @ 2.10 → prob implícita 47.6%
  - Asian Handicap: Team A -0.75 @ 1.85 → prob implícita 54.1%
  - Diferencia de 6.5 puntos → el mercado AH sabe algo que H2H no refleja

Mercados analizados:
  - h2h (1X2)
  - asian_handicap (líneas con punto)
  - spreads (alternativa americana)
  - totals (over/under)

Sin costo adicional: todos estos mercados vienen en la misma respuesta de Odds API.
"""
import os
import logging
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


def prob_implicita(cuota: float) -> float:
    """Probabilidad implícita de una cuota decimal."""
    return 1.0 / cuota if cuota > 1 else 0


def detectar_inconsistencias(api_key: str = None) -> dict:
    """
    Escanea partidos activos con múltiples mercados y detecta
    diferencias significativas entre probabilidades implícitas.
    """
    from services.deportes import get_odds_upcoming

    api_key = api_key or os.getenv("ODDS_API_KEY", "")
    if not api_key:
        return {"error": "ODDS_API_KEY no configurada"}

    # Pedir h2h + asian_handicap + spreads en un solo call
    raw = get_odds_upcoming(api_key, regions="us,uk,eu", markets="h2h,asian_handicap,spreads,totals")
    if not raw:
        raw = []

    alertas = []
    for m in raw if isinstance(raw, list) else []:
        ht = m.get("home_team", "") or ""
        at = m.get("away_team", "") or ""
        if not ht or not at:
            continue

        # Extraer mejor cuota por mercado y resultado
        mercados = {}  # market_key -> { outcome_name: best_price }
        for book in m.get("bookmakers", []):
            for market in book.get("markets", []):
                mk = market.get("key", "")
                if mk not in mercados:
                    mercados[mk] = {}
                for o in market.get("outcomes", []):
                    name = o.get("name", "")
                    price = o.get("price", 0)
                    point = o.get("point")
                    key = f"{name}|{point}" if point is not None else name
                    if not name or price <= 1:
                        continue
                    prev = mercados[mk].get(key, {}).get("cuota", 0)
                    if price > prev:
                        mercados[mk][key] = {
                            "cuota": min(price, 50.0),
                            "casa": book.get("title", ""),
                            "name": name,
                            "point": point,
                        }

        # Comparar H2H vs Asian Handicap para el mismo equipo
        h2h = mercados.get("h2h", {})
        ah = mercados.get("asian_handicap", {})

        if h2h and ah:
            for h2h_key, h2h_info in h2h.items():
                prob_h2h = prob_implicita(h2h_info["cuota"])
                h2h_name = h2h_info.get("name", "")

                # Buscar en AH la misma selección
                for ah_key, ah_info in ah.items():
                    ah_name = ah_info.get("name", "")
                    if ah_name.lower() != h2h_name.lower():
                        continue

                    prob_ah = prob_implicita(ah_info["cuota"])
                    diff = abs(prob_ah - prob_h2h) * 100
                    point = ah_info.get("point")

                    if diff >= 5.0:  # Diferencia significativa
                        direccion = "AH ve MAS valor" if prob_ah > prob_h2h else "AH ve MENOS valor"
                        profit_est = round(diff * 0.5, 2)  # estimado

                        alertas.append({
                            "partido": f"{ht} vs {at}",
                            "liga": m.get("sport_title", ""),
                            "seleccion": h2h_name,
                            "point_ah": point,
                            "prob_h2h_pct": round(prob_h2h * 100, 1),
                            "prob_ah_pct": round(prob_ah * 100, 1),
                            "diferencia_pct": round(diff, 1),
                            "direccion": direccion,
                            "cuota_h2h_mejor": h2h_info["cuota"],
                            "cuota_ah_mejor": ah_info["cuota"],
                            "casa_h2h": h2h_info.get("casa", ""),
                            "casa_ah": ah_info.get("casa", ""),
                            "profit_estimado_pct": profit_est,
                        })

    # Ordenar por diferencia (mayor primero)
    alertas.sort(key=lambda x: x["diferencia_pct"], reverse=True)

    return {
        "total_alertas": len(alertas),
        "mercados_analizados": list(mercados.keys()) if mercados else ["h2h", "asian_handicap", "spreads", "totals"],
        "alertas": alertas[:20],
    }


def get_opportunities(api_key: str = None, min_diff: float = 4.0) -> dict:
    """
    Similar a detectar_inconsistencias pero con filtro mínimo configurable.
    Útil para el dashboard.
    """
    from database import db, _execute, _fetchall

    result = detectar_inconsistencias(api_key)
    filtradas = [a for a in result.get("alertas", []) if a.get("diferencia_pct", 0) >= min_diff]

    # Loggear las mejores oportunidades
    for a in filtradas[:3]:
        try:
            detalle = (
                f"{a['seleccion']}: H2H={a['prob_h2h_pct']}% vs AH={a['prob_ah_pct']}% "
                f"(dif {a['diferencia_pct']}%)"
            )
            with db() as conn:
                _execute(conn,
                    "INSERT INTO alerts_log (tipo, partido, detalle, urgencia, canal) "
                    "VALUES (?,?,?,?,?)",
                    ("CROSS_MARKET", a["partido"], detalle, "MEDIA", "telegram"))
        except Exception:
            pass

    return {
        "total_alertas": len(filtradas),
        "min_diferencia_pct": min_diff,
        "alertas": filtradas[:20],
    }
