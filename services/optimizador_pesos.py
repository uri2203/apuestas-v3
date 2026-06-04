"""
Optimizador de Pesos del Ensemble.

Prueba todas las combinaciones de pesos (Dixon-Coles, ELO, Poisson)
contra los partidos reales y selecciona la que MÁS acierta.

Esto es backtesting walk-forward: entrena con datos pasados, predice
el siguiente partido, compara con el resultado real, y mide accuracy.
"""

import logging
from models.ensemble import EnsembleModel

logger = logging.getLogger(__name__)


def _resultado_real(home_goals, away_goals):
    if home_goals > away_goals: return "1"
    if home_goals == away_goals: return "X"
    return "2"


def evaluar_pesos(partidos, w_dc, w_elo, w_poisson, ventana_min=20):
    """
    Walk-forward: para cada partido (a partir de ventana_min),
    entrena con los anteriores y predice. Retorna accuracy.
    """
    if len(partidos) < ventana_min + 5:
        return None

    aciertos = 0
    total = 0

    # Evaluar en bloques para eficiencia (no reentrenar por cada partido)
    paso = max(1, len(partidos) // 15)  # ~15 evaluaciones máx (evita timeout)

    for i in range(ventana_min, len(partidos), paso):
        train = partidos[:i]
        test  = partidos[i]

        modelo = EnsembleModel(w_dc=w_dc, w_elo=w_elo, w_poisson=w_poisson)
        modelo.fit(train)

        try:
            pred = modelo.predict(test["home"], test["away"])
            probs = {"1": pred["local"], "X": pred["empate"], "2": pred["visitante"]}
            pronostico = max(probs, key=probs.get)
            real = _resultado_real(test["home_goals"], test["away_goals"])
            if pronostico == real:
                aciertos += 1
            total += 1
        except Exception:
            continue

    return round(aciertos / total * 100, 1) if total > 0 else None


def optimizar(partidos, ventana_min=20):
    """
    Prueba combinaciones de pesos y retorna la mejor según accuracy real.
    """
    if len(partidos) < ventana_min + 10:
        return {
            "error": f"Se necesitan al menos {ventana_min + 10} partidos. Hay {len(partidos)}.",
            "pesos_recomendados": {"dc": 0.50, "elo": 0.30, "poisson": 0.20},
        }
    # Limitar a últimos 100 partidos para velocidad (evita timeout Render)
    if len(partidos) > 100:
        partidos = partidos[-100:]

    # Combinaciones a probar (suman 1.0)
    combinaciones = [
        (0.50, 0.30, 0.20),  # balance estándar (baseline)
        (0.60, 0.25, 0.15),  # DC reforzado
        (0.70, 0.20, 0.10),  # DC dominante
        (0.45, 0.35, 0.20),  # más forma reciente
    ]

    resultados = []
    for w_dc, w_elo, w_poi in combinaciones:
        acc = evaluar_pesos(partidos, w_dc, w_elo, w_poi, ventana_min)
        if acc is not None:
            resultados.append({
                "pesos": {"dc": w_dc, "elo": w_elo, "poisson": w_poi},
                "accuracy_pct": acc,
                "etiqueta": f"DC {int(w_dc*100)}% · ELO {int(w_elo*100)}% · Poisson {int(w_poi*100)}%",
            })

    if not resultados:
        return {"error": "No se pudo evaluar", "pesos_recomendados": {"dc": 0.50, "elo": 0.30, "poisson": 0.20}}

    # Ordenar por accuracy
    resultados.sort(key=lambda x: x["accuracy_pct"], reverse=True)
    mejor = resultados[0]

    return {
        "mejor_combinacion":  mejor,
        "todas_las_pruebas":  resultados,
        "pesos_recomendados": mejor["pesos"],
        "accuracy_mejor":     mejor["accuracy_pct"],
        "accuracy_baseline":  next((r["accuracy_pct"] for r in resultados
                                    if r["pesos"]["dc"] == 0.50), None),
        "partidos_evaluados": len(partidos),
        "mejora_vs_baseline": None,
    }
