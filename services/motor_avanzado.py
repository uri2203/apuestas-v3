import pandas as pd
import numpy as np
from services import api_football, estadisticas

def calcular_kelly(prob, cuota):
    """
    Cálculo estricto de la Fracción de Kelly.
    Aplica un divisor de gestión de riesgo (Fractional Kelly) al 10%.
    """
    if cuota <= 1: 
        return 0.0
    b = cuota - 1
    p = prob
    q = 1 - p
    # Fórmula: f* = (bp - q) / b
    f_star = (b * p - q) / b
    return max(0, f_star * 0.1)

def obtener_todas_las_predicciones():
    """
    Silo Maestro de Agregación. 
    Consolida datos de API, modelos estadísticos y gestión de bankroll.
    """
    try:
        # Recuperar partidos desde el silo de API Football
        partidos = api_football.get_upcoming_matches()
        if not partidos:
            return []

        resultados = []
        for p in partidos:
            # Extracción de probabilidades desde modelos independientes
            prob_elo = estadisticas.get_elo_prob(p['local'], p['visitante'])
            prob_dixon = estadisticas.get_dixon_prob(p['local'], p['visitante'])
            
            # Ensamble de modelos (Media ponderada para estabilidad)
            prob_final = (prob_elo + prob_dixon) / 2
            
            # Cálculo de Valor Esperado (EV)
            cuota = p.get('cuota_local', 0.0)
            if cuota > 0:
                ev = (prob_final * cuota) - 1
            else:
                ev = 0.0
            
            # Construcción del objeto final para el Dashboard
            entry = {
                "hora": p.get("hora", "00:00"),
                "liga": p.get("liga", "N/A"),
                "local": p.get("local", "Desconocido"),
                "visitante": p.get("visitante", "Desconocido"),
                "cuota_local": cuota,
                "cuota_empate": p.get("cuota_empate", 0.0),
                "cuota_visitante": p.get("cuota_visitante", 0.0),
                "prob_elo": float(prob_elo),
                "prob_dixon": float(prob_dixon),
                "prob_ensemble": float(prob_final),
                "kelly_fraction": float(calcular_kelly(prob_final, cuota)),
                "ev": float(ev)
            }
            resultados.append(entry)
            
        return resultados
    except Exception as e:
        print(f"CRITICAL ERROR - MOTOR AVANZADO: {str(e)}")
        return []
