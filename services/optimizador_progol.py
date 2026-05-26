"""
Optimizador de Progol.

Progol México: 14 partidos, acertar 11+ para ganar el premio mayor.
Estrategias:
1. Simple:      una quiniela con el signo más probable de cada partido
2. Diversificada: N quinielas variando signos en partidos disputados
3. Cobertura:   maximiza la probabilidad de que al menos UNA quiniela acierte 11+
4. Kelly:       distribuye inversión según la probabilidad de cada quiniela
"""

import math
import itertools
import random
from typing import List, Dict


# ── Utilidades ────────────────────────────────────────────────────────────────

def _prob_acertar_k_de_n(probs_correctas: List[float], k: int) -> float:
    """
    Probabilidad de acertar exactamente k de n pronósticos
    usando programación dinámica (exacta, no aproximación).
    probs_correctas: lista de P(acierto) para cada partido
    """
    n = len(probs_correctas)
    # dp[i][j] = P(acertar exactamente j de los primeros i partidos)
    dp = [[0.0] * (n + 1) for _ in range(n + 1)]
    dp[0][0] = 1.0
    for i, p in enumerate(probs_correctas):
        for j in range(i + 1):
            if dp[i][j] == 0:
                continue
            dp[i + 1][j]     += dp[i][j] * (1 - p)   # falla
            dp[i + 1][j + 1] += dp[i][j] * p          # acierta
    return dp[n][k]


def _prob_ganar_quiniela(probs_correctas: List[float], umbral: int = 11) -> float:
    """P(acertar >= umbral partidos)."""
    n = len(probs_correctas)
    return sum(_prob_acertar_k_de_n(probs_correctas, k) for k in range(umbral, n + 1))


def _prob_correcta_para_signo(partido: dict, signo: str) -> float:
    """Retorna la probabilidad de que `signo` sea el resultado correcto."""
    mapa = {"1": partido["prob_local"], "X": partido["prob_empate"], "2": partido["prob_visitante"]}
    return mapa.get(signo, 0.0)


# ── Estrategia 1: Simple (máxima probabilidad) ─────────────────────────────

def quiniela_simple(partidos: list) -> dict:
    """Una quiniela con el signo más probable para cada partido."""
    signos = []
    probs  = []
    for p in partidos:
        candidatos = [("1", p["prob_local"]), ("X", p["prob_empate"]), ("2", p["prob_visitante"])]
        mejor = max(candidatos, key=lambda x: x[1])
        signos.append(mejor[0])
        probs.append(mejor[1])

    prob_ganar = _prob_ganar_quiniela(probs)
    return {
        "estrategia": "simple",
        "signos":     signos,
        "prob_ganar_pct": round(prob_ganar * 100, 4),
        "prob_acertar_exacta": {
            str(k): round(_prob_acertar_k_de_n(probs, k) * 100, 3)
            for k in range(8, 15)
        },
        "aciertos_esperados": round(sum(probs), 2),
    }


# ── Estrategia 2: Diversificada ────────────────────────────────────────────

def quinielas_diversificadas(partidos: list, n_quinielas: int = 10) -> list:
    """
    Genera N quinielas variando los signos en partidos disputados
    (donde la diferencia entre 1ª y 2ª opción es < 15%).
    """
    # Clasificar partidos: claros vs disputados
    claros     = []   # índices donde una prob > 55%
    disputados = []   # índices donde ninguna > 55%

    for i, p in enumerate(partidos):
        max_p = max(p["prob_local"], p["prob_empate"], p["prob_visitante"])
        if max_p > 0.55:
            claros.append(i)
        else:
            disputados.append(i)

    quinielas = []
    intentos  = 0
    vistas    = set()

    while len(quinielas) < n_quinielas and intentos < 1000:
        intentos += 1
        signos = []
        for i, p in enumerate(partidos):
            candidatos = [("1", p["prob_local"]), ("X", p["prob_empate"]), ("2", p["prob_visitante"])]
            candidatos.sort(key=lambda x: x[1], reverse=True)

            if i in disputados:
                # En partidos disputados, variar entre 1ª y 2ª opción
                pesos = [candidatos[0][1], candidatos[1][1], candidatos[2][1]]
                total = sum(pesos)
                pesos = [pw / total for pw in pesos]
                rng   = random.random()
                acum  = 0
                elegido = candidatos[0][0]
                for signo, peso in zip([c[0] for c in candidatos], pesos):
                    acum += peso
                    if rng <= acum:
                        elegido = signo
                        break
                signos.append(elegido)
            else:
                signos.append(candidatos[0][0])

        clave = tuple(signos)
        if clave in vistas:
            continue
        vistas.add(clave)

        probs = [_prob_correcta_para_signo(p, s) for p, s in zip(partidos, signos)]
        prob_ganar = _prob_ganar_quiniela(probs)

        quinielas.append({
            "quiniela_num": len(quinielas) + 1,
            "signos":       signos,
            "prob_ganar_pct": round(prob_ganar * 100, 4),
            "aciertos_esperados": round(sum(probs), 2),
        })

    return sorted(quinielas, key=lambda x: x["prob_ganar_pct"], reverse=True)


# ── Estrategia 3: Máxima Cobertura ────────────────────────────────────────

def optimizar_cobertura(
    partidos: list,
    n_quinielas: int = 5,
    umbral: int = 11,
) -> dict:
    """
    Encuentra el conjunto de N quinielas que maximiza la probabilidad
    de que AL MENOS UNA acierte >= umbral partidos.
    Usa hill-climbing estocástico (exacto sería NP-hard con 14 partidos).
    """
    def prob_al_menos_una(conjunto_quinielas: list) -> float:
        """P(al menos una quiniela gana) = 1 - P(ninguna gana)."""
        p_ninguna = 1.0
        for q in conjunto_quinielas:
            probs_q = [_prob_correcta_para_signo(p, s)
                       for p, s in zip(partidos, q)]
            p_no_gana = 1.0 - _prob_ganar_quiniela(probs_q, umbral)
            p_ninguna *= p_no_gana
        return 1.0 - p_ninguna

    # Empezar con quinielas diversificadas como semilla
    pool = quinielas_diversificadas(partidos, max(n_quinielas * 5, 50))
    pool_signos = [q["signos"] for q in pool]

    # Seleccionar greedily las N mejores maximizando cobertura marginal
    seleccionadas = []
    disponibles   = list(range(len(pool_signos)))

    for _ in range(min(n_quinielas, len(pool_signos))):
        mejor_idx  = None
        mejor_prob = -1
        for idx in disponibles:
            candidatas = [pool_signos[i] for i in [j for j in range(len(pool_signos)) if pool_signos[j] in seleccionadas + [pool_signos[idx]]]]
            p = prob_al_menos_una(seleccionadas + [pool_signos[idx]])
            if p > mejor_prob:
                mejor_prob = p
                mejor_idx  = idx
        if mejor_idx is not None:
            seleccionadas.append(pool_signos[mejor_idx])
            disponibles.remove(mejor_idx)

    prob_total = prob_al_menos_una(seleccionadas)

    resultado_quinielas = []
    for i, signos in enumerate(seleccionadas):
        probs = [_prob_correcta_para_signo(p, s) for p, s in zip(partidos, signos)]
        resultado_quinielas.append({
            "quiniela_num":  i + 1,
            "signos":        signos,
            "aciertos_esp":  round(sum(probs), 2),
            "prob_gana_pct": round(_prob_ganar_quiniela(probs, umbral) * 100, 4),
        })

    return {
        "estrategia":            "maxima_cobertura",
        "n_quinielas":           len(seleccionadas),
        "umbral_aciertos":       umbral,
        "prob_al_menos_una_pct": round(prob_total * 100, 4),
        "quinielas":             resultado_quinielas,
        "costo_total_mxn":       len(seleccionadas) * 15,  # ~$15 por quiniela
        "roi_esperado_nota":     "El pozo de Progol varía; consultar monto actual",
    }


# ── Análisis de la jornada ────────────────────────────────────────────────────

def analizar_jornada_progol(partidos: list) -> dict:
    """
    Análisis completo de la jornada: clasificación de partidos,
    quiniela óptima y distribución de signos esperados.
    """
    if not partidos:
        return {"error": "Sin partidos"}

    # Clasificar cada partido
    clasificados = []
    for p in partidos:
        max_p = max(p["prob_local"], p["prob_empate"], p["prob_visitante"])
        signos_ord = sorted(
            [("1", p["prob_local"]), ("X", p["prob_empate"]), ("2", p["prob_visitante"])],
            key=lambda x: x[1], reverse=True
        )
        clasificados.append({
            **p,
            "tipo": (
                "fijo"      if max_p > 0.60 else
                "claro"     if max_p > 0.50 else
                "disputado" if max_p > 0.38 else
                "loteria"
            ),
            "signo_1": signos_ord[0][0],
            "signo_2": signos_ord[1][0],
            "signo_3": signos_ord[2][0],
            "margen_1_2": round((signos_ord[0][1] - signos_ord[1][1]) * 100, 1),
        })

    # Distribución de tipos
    tipos = {"fijo": 0, "claro": 0, "disputado": 0, "loteria": 0}
    for c in clasificados:
        tipos[c["tipo"]] += 1

    return {
        "total_partidos": len(clasificados),
        "distribucion_tipos": tipos,
        "partidos": clasificados,
        "quiniela_simple": quiniela_simple(partidos),
        "recomendacion": (
            f"Con {tipos['fijo']} fijos y {tipos['claro']} claros, "
            f"enfoca variación en {tipos['disputado']} disputados y {tipos['loteria']} de lotería."
        ),
    }
