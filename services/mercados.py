"""
Mercados adicionales — Over/Under, BTTS, Asian Handicap.

Usa distribución Poisson bivariante (misma base que Dixon-Coles)
para calcular probabilidades en todos los mercados disponibles.
"""

import math
from models.dixon_coles import DixonColesModel, _poisson_pmf


def _matriz_goles(lam: float, mu: float, max_g: int = 8) -> dict:
    """
    Construye matriz P(i, j) de probabilidades de marcadores.
    Incluye corrección tau de Dixon-Coles para marcadores bajos.
    """
    from models.dixon_coles import _tau
    rho = -0.13
    matriz = {}
    for i in range(max_g + 1):
        for j in range(max_g + 1):
            p = _poisson_pmf(i, lam) * _poisson_pmf(j, mu) * _tau(i, j, lam, mu, rho)
            matriz[(i, j)] = max(0.0, p)
    # Normalizar
    total = sum(matriz.values())
    if total > 0:
        matriz = {k: v / total for k, v in matriz.items()}
    return matriz


def calcular_mercados_completos(
    home: str,
    away: str,
    historial: list,
    xg_home: float = None,
    xg_away: float = None,
) -> dict:
    """
    Calcula probabilidades para todos los mercados usando el modelo DC.
    Retorna Over/Under múltiples líneas, BTTS, Handicap Asian, Marcador exacto.
    """
    dc = DixonColesModel()
    dc.fit(historial)
    dc_pred = dc.predict(home, away)

    lam = xg_home or dc_pred["lambda_local"]
    mu  = xg_away or dc_pred["lambda_visitante"]
    mat = _matriz_goles(lam, mu)

    # ── 1X2 base ──────────────────────────────────────────────────────────────
    p_local    = sum(p for (i, j), p in mat.items() if i > j)
    p_empate   = sum(p for (i, j), p in mat.items() if i == j)
    p_visitante = sum(p for (i, j), p in mat.items() if i < j)

    # ── Over / Under ──────────────────────────────────────────────────────────
    lineas_ou = [0.5, 1.5, 2.5, 3.5, 4.5]
    over_under = {}
    for linea in lineas_ou:
        p_over  = sum(p for (i, j), p in mat.items() if i + j > linea)
        p_under = 1.0 - p_over
        over_under[f"{linea}"] = {
            "over_pct":  round(p_over * 100, 2),
            "under_pct": round(p_under * 100, 2),
            "cuota_over":  round(1 / p_over, 3)  if p_over  > 0 else 99,
            "cuota_under": round(1 / p_under, 3) if p_under > 0 else 99,
        }

    # ── BTTS (Both Teams To Score) ────────────────────────────────────────────
    p_btts_si = sum(p for (i, j), p in mat.items() if i > 0 and j > 0)
    p_btts_no = 1.0 - p_btts_si

    # ── Asian Handicap ────────────────────────────────────────────────────────
    handicaps = [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5]
    asian_handicap = {}
    for h in handicaps:
        p_local_ah = sum(p for (i, j), p in mat.items() if (i + h) > j)
        p_push     = sum(p for (i, j), p in mat.items() if (i + h) == j)
        p_visit_ah = sum(p for (i, j), p in mat.items() if (i + h) < j)
        label = f"{'+' if h >= 0 else ''}{h}"
        asian_handicap[label] = {
            "p_local_pct":    round(p_local_ah * 100, 2),
            "p_push_pct":     round(p_push * 100, 2),
            "p_visitante_pct": round(p_visit_ah * 100, 2),
            "cuota_local":     round(1 / p_local_ah, 3) if p_local_ah > 0 else 99,
            "cuota_visitante": round(1 / p_visit_ah, 3) if p_visit_ah > 0 else 99,
        }

    # ── Marcadores exactos (top 10) ───────────────────────────────────────────
    top_marcadores = sorted(mat.items(), key=lambda x: x[1], reverse=True)[:10]
    marcadores_exactos = [
        {
            "marcador": f"{i}-{j}",
            "prob_pct": round(p * 100, 2),
            "cuota_justa": round(1 / p, 1) if p > 0 else 999,
            "resultado": "1" if i > j else "X" if i == j else "2",
        }
        for (i, j), p in top_marcadores
    ]

    # ── Goles del local / visitante ───────────────────────────────────────────
    p_local_anota  = sum(p for (i, j), p in mat.items() if i > 0)
    p_visita_anota = sum(p for (i, j), p in mat.items() if j > 0)

    # ── Goles esperados ───────────────────────────────────────────────────────
    goles_esp_total = sum((i + j) * p for (i, j), p in mat.items())
    goles_esp_local  = sum(i * p for (i, j), p in mat.items())
    goles_esp_visita = sum(j * p for (i, j), p in mat.items())

    return {
        "partido": f"{home} vs {away}",
        "modelo": "Dixon-Coles + Poisson bivariante",
        "lambdas": {"local": round(lam, 3), "visitante": round(mu, 3)},
        "resultado_1x2": {
            "local_pct":     round(p_local * 100, 2),
            "empate_pct":    round(p_empate * 100, 2),
            "visitante_pct": round(p_visitante * 100, 2),
        },
        "over_under":    over_under,
        "btts": {
            "si_pct":      round(p_btts_si * 100, 2),
            "no_pct":      round(p_btts_no * 100, 2),
            "cuota_si":    round(1 / p_btts_si, 3) if p_btts_si > 0 else 99,
            "cuota_no":    round(1 / p_btts_no, 3) if p_btts_no > 0 else 99,
        },
        "asian_handicap": asian_handicap,
        "marcadores_exactos": marcadores_exactos,
        "goles_esperados": {
            "total":    round(goles_esp_total, 2),
            "local":    round(goles_esp_local, 2),
            "visitante": round(goles_esp_visita, 2),
        },
        "probabilidades_adicionales": {
            "local_anota_pct":    round(p_local_anota * 100, 1),
            "visitante_anota_pct": round(p_visita_anota * 100, 1),
        },
    }


def detectar_value_bets_mercados(
    mercados: dict,
    cuotas_casa: dict,
) -> list:
    """
    Compara probabilidades del modelo vs cuotas de casa para todos los mercados.
    cuotas_casa: {"Over 2.5": 1.85, "Under 2.5": 1.95, "BTTS Si": 1.70, ...}
    """
    value_bets = []
    mapping = {
        "Over 2.5":  ("over_under", "2.5", "over_pct"),
        "Under 2.5": ("over_under", "2.5", "under_pct"),
        "Over 1.5":  ("over_under", "1.5", "over_pct"),
        "Under 1.5": ("over_under", "1.5", "under_pct"),
        "Over 3.5":  ("over_under", "3.5", "over_pct"),
        "BTTS Si":   ("btts", None, "si_pct"),
        "BTTS No":   ("btts", None, "no_pct"),
    }
    for mercado, cuota in cuotas_casa.items():
        if mercado not in mapping or cuota <= 1:
            continue
        seccion, key, campo = mapping[mercado]
        try:
            if key:
                prob_modelo = mercados[seccion][key][campo] / 100
            else:
                prob_modelo = mercados[seccion][campo] / 100
            edge = round((prob_modelo * cuota - 1) * 100, 1)
            if edge > 0:
                value_bets.append({
                    "mercado":     mercado,
                    "cuota":       cuota,
                    "prob_modelo": round(prob_modelo * 100, 1),
                    "edge_pct":    edge,
                    "es_value":    True,
                })
        except (KeyError, TypeError):
            continue

    return sorted(value_bets, key=lambda x: x["edge_pct"], reverse=True)
