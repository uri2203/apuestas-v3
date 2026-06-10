"""
Motor avanzado v2 — Lo que usan los sistemas profesionales:
- Closing Line Value (CLV) como métrica primaria de calidad
- Simulaciones Monte Carlo (10,000 por evento)
- Detección de Sharp Money y Reverse Line Movement (RLM)
- Modelo LSTM simplificado para loterías
- Riesgo de ruina y proyección de bankroll
"""
import math
import random
import statistics
from collections import Counter
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# CLOSING LINE VALUE (CLV) — Métrica #1 de apostadores profesionales
# ══════════════════════════════════════════════════════════════════════════════

def calcular_clv(cuota_apostada: float, cuota_cierre: float) -> dict:
    """
    Calcula el Closing Line Value.
    CLV positivo = apuesta de calidad. Benchmark pro: >55% bets con CLV+.
    """
    prob_apostada = 1 / cuota_apostada
    prob_cierre = 1 / cuota_cierre

    clv_cuota = cuota_apostada - cuota_cierre
    clv_pct = (cuota_apostada / cuota_cierre - 1) * 100
    edge_prob = (prob_cierre - prob_apostada) * 100

    return {
        "cuota_apostada": cuota_apostada,
        "cuota_cierre": cuota_cierre,
        "prob_implicita_apostada_pct": round(prob_apostada * 100, 2),
        "prob_implicita_cierre_pct": round(prob_cierre * 100, 2),
        "clv_cuota": round(clv_cuota, 3),
        "clv_pct": round(clv_pct, 2),
        "edge_probabilidad_pct": round(edge_prob, 2),
        "es_positivo": clv_cuota > 0,
        "calidad": (
            "excelente (>5%)" if clv_pct > 5
            else "bueno (2-5%)" if clv_pct > 2
            else "marginal (0-2%)" if clv_pct > 0
            else "negativo — apuesta de mala calidad"
        ),
    }


def analizar_historial_clv(apuestas: list[dict]) -> dict:
    """
    Analiza el historial completo de apuestas con métricas CLV.
    apuestas: [{cuota, cuota_cierre, resultado, monto}, ...]
    """
    if not apuestas:
        return {"error": "Sin datos"}

    clvs = []
    profit = 0
    invertido = 0
    clv_positivos = 0

    for a in apuestas:
        clv = calcular_clv(a["cuota"], a["cuota_cierre"])
        clvs.append(clv["clv_pct"])
        if clv["es_positivo"]:
            clv_positivos += 1

        monto = a.get("monto", 100)
        invertido += monto
        if a.get("resultado", False):
            profit += monto * (a["cuota"] - 1)
        else:
            profit -= monto

    pct_clv_positivo = clv_positivos / len(apuestas) * 100
    roi = profit / invertido * 100 if invertido > 0 else 0

    return {
        "total_apuestas": len(apuestas),
        "pct_clv_positivo": round(pct_clv_positivo, 1),
        "benchmark_profesional_pct": 55.0,
        "es_apostador_sharp": pct_clv_positivo >= 55,
        "clv_promedio_pct": round(statistics.mean(clvs), 2),
        "roi_real_pct": round(roi, 2),
        "invertido_total": round(invertido, 2),
        "profit_neto": round(profit, 2),
        "interpretacion": (
            "Apostador sharp — Edge consistente sobre el mercado" if pct_clv_positivo >= 65
            else "Por encima del benchmark profesional" if pct_clv_positivo >= 55
            else "Cerca del benchmark — mejora el timing" if pct_clv_positivo >= 45
            else "Por debajo del benchmark — revisar estrategia de selección"
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
# SHARP MONEY Y MOVIMIENTO DE LÍNEA
# ══════════════════════════════════════════════════════════════════════════════

def detectar_sharp_money(
    cuota_apertura: float,
    cuota_actual: float,
    pct_apuestas_publicas: float,
    umbral_movimiento: float = 0.05,
) -> dict:
    """
    Detecta movimiento de dinero sharp.
    Reverse Line Movement (RLM): línea se mueve CONTRA el dinero público.
    """
    movimiento = cuota_apertura - cuota_actual
    movimiento_pct = (movimiento / cuota_apertura) * 100
    pct_apostado_sharp = 100 - pct_apuestas_publicas

    # RLM: >60% apuestas al lado A pero la línea SE MUEVE CONTRA A
    is_rlm = (pct_apuestas_publicas > 60 and movimiento > 0) or (
        pct_apuestas_publicas < 40 and movimiento < 0
    )

    # Steam move: movimiento brusco en poco tiempo (>5%)
    is_steam = abs(movimiento_pct) > 5

    tipo = "sin_sharp"
    if is_rlm:
        tipo = "reverse_line_movement"
    elif is_steam:
        tipo = "steam_move"
    elif abs(movimiento_pct) > 2:
        tipo = "movimiento_sharp_moderado"

    return {
        "cuota_apertura": cuota_apertura,
        "cuota_actual": cuota_actual,
        "movimiento_puntos": round(movimiento, 3),
        "movimiento_pct": round(movimiento_pct, 2),
        "pct_apuestas_publicas": pct_apuestas_publicas,
        "tipo": tipo,
        "is_reverse_line_movement": is_rlm,
        "is_steam_move": is_steam,
        "senal_sharp": is_rlm or is_steam,
        "accion_recomendada": (
            "Seguir el sharp money — bet inmediato" if is_rlm
            else "Steam move — actuar rápido antes que se corrija" if is_steam
            else "Monitorear movimiento" if abs(movimiento_pct) > 2
            else "Sin señal sharp relevante"
        ),
    }


def detectar_rlm_multiple(mercados: list[dict]) -> list[dict]:
    """
    Analiza múltiples mercados y devuelve solo los con señal sharp.
    """
    resultados = []
    for m in mercados:
        analisis = detectar_sharp_money(
            m["cuota_apertura"],
            m["cuota_actual"],
            m["pct_publico"],
        )
        if analisis["senal_sharp"]:
            resultados.append({"mercado": m.get("nombre", "?"), **analisis})

    return sorted(resultados, key=lambda x: abs(x["movimiento_pct"]), reverse=True)


# ══════════════════════════════════════════════════════════════════════════════
# MONTE CARLO
# ══════════════════════════════════════════════════════════════════════════════

def monte_carlo_loteria(
    n_numeros: int,
    rango_max: int,
    combinacion_objetivo: list[int],
    n_simulaciones: int = 10000,
) -> dict:
    """
    Simula n_simulaciones sorteos y analiza resultados vs combinación objetivo.
    """
    distribucion = Counter()
    aciertos_por_sim = []

    for _ in range(n_simulaciones):
        drawn = set(random.sample(range(1, rango_max + 1), n_numeros))
        aciertos = len(set(combinacion_objetivo) & drawn)
        distribucion[aciertos] += 1
        aciertos_por_sim.append(aciertos)

    media = statistics.mean(aciertos_por_sim)
    desv = statistics.stdev(aciertos_por_sim) if len(aciertos_por_sim) > 1 else 0

    return {
        "simulaciones": n_simulaciones,
        "combinacion_analizada": sorted(combinacion_objetivo),
        "distribucion": dict(sorted(distribucion.items())),
        "media_aciertos": round(media, 3),
        "desviacion_std": round(desv, 3),
        "probabilidades_simuladas": {
            k: round(v / n_simulaciones, 6)
            for k, v in sorted(distribucion.items())
        },
        "percentil_95": round(media + 1.96 * desv, 2),
    }


def monte_carlo_partido(
    lambda_local: float = 1.5,
    lambda_visitante: float = 1.1,
    n_simulaciones: int = 10000,
) -> dict:
    """
    Simula partido de fútbol usando distribución Poisson para goles.
    lambda = tasa de goles esperados.
    Genera probabilidades sin sesgo de casa de apuestas (sin vig).
    """
    victorias_local = 0
    empates = 0
    victorias_visitante = 0
    goles_totales = []
    spreads = []

    for _ in range(n_simulaciones):
        # Poisson: -ln(U) para simular
        goles_l = 0
        p = math.exp(-lambda_local)
        q = 1.0
        while q > p:
            goles_l += 1
            q *= random.random()
        goles_l -= 1

        goles_v = 0
        p = math.exp(-lambda_visitante)
        q = 1.0
        while q > p:
            goles_v += 1
            q *= random.random()
        goles_v -= 1

        total = goles_l + goles_v
        goles_totales.append(total)
        spreads.append(goles_l - goles_v)

        if goles_l > goles_v:
            victorias_local += 1
        elif goles_l == goles_v:
            empates += 1
        else:
            victorias_visitante += 1

    n = n_simulaciones
    prob_l = victorias_local / n
    prob_d = empates / n
    prob_v = victorias_visitante / n

    # Cuotas justas (sin vig)
    cuota_l = round(1 / prob_l, 3) if prob_l > 0 else 99.0
    cuota_d = round(1 / prob_d, 3) if prob_d > 0 else 99.0
    cuota_v = round(1 / prob_v, 3) if prob_v > 0 else 99.0

    avg_goles = statistics.mean(goles_totales)
    prob_over25 = sum(1 for g in goles_totales if g > 2.5) / n

    return {
        "simulaciones": n_simulaciones,
        "lambda_local": lambda_local,
        "lambda_visitante": lambda_visitante,
        "probabilidades": {
            "local_pct": round(prob_l * 100, 1),
            "empate_pct": round(prob_d * 100, 1),
            "visitante_pct": round(prob_v * 100, 1),
        },
        "cuotas_justas_sin_vig": {
            "local": cuota_l,
            "empate": cuota_d,
            "visitante": cuota_v,
        },
        "mercados_adicionales": {
            "avg_goles_totales": round(avg_goles, 2),
            "prob_over_2_5_pct": round(prob_over25 * 100, 1),
            "prob_over_1_5_pct": round(sum(1 for g in goles_totales if g > 1.5) / n * 100, 1),
            "prob_ambos_anotan_pct": round(
                sum(1 for sg, ga in zip(goles_totales, spreads) if sg > 0 and abs(ga) < sg) / max(n, 1) * 100, 1
            ) if goles_totales else 0,
        },
        "notas": "Cuotas justas generadas por simulación Poisson — compara vs casas para detectar value",
    }


# ══════════════════════════════════════════════════════════════════════════════
# RIESGO DE RUINA Y PROYECCIÓN DE BANKROLL
# ══════════════════════════════════════════════════════════════════════════════

def calcular_riesgo_ruina(
    bankroll: float,
    apuesta_pct: float,
    win_rate: float,
    odds: float,
    n_apuestas: int = 1000,
) -> dict:
    """
    Calcula probabilidad de ruina mediante simulación Monte Carlo.
    Más preciso que la fórmula cerrada cuando hay varianza alta.
    """
    ruinas = 0
    trajectories = []
    SIM = 200  # Paths simulados para estimar distribución

    for _ in range(SIM):
        bk = bankroll
        path = [bk]
        broke = False
        for _ in range(n_apuestas):
            if bk <= 0:
                broke = True
                break
            bet = bk * apuesta_pct
            if random.random() < win_rate:
                bk += bet * (odds - 1)
            else:
                bk -= bet
            path.append(round(bk, 2))
        if broke or bk <= bankroll * 0.05:
            ruinas += 1
        trajectories.append(path[-1])

    prob_ruina = ruinas / SIM
    median_final = sorted(trajectories)[SIM // 2]
    roi_proyectado = (median_final - bankroll) / bankroll * 100

    return {
        "bankroll_inicial": bankroll,
        "apuesta_pct": round(apuesta_pct * 100, 1),
        "win_rate_pct": round(win_rate * 100, 1),
        "odds": odds,
        "n_apuestas": n_apuestas,
        "prob_ruina_pct": round(prob_ruina * 100, 1),
        "bankroll_mediano_final": round(median_final, 2),
        "roi_proyectado_pct": round(roi_proyectado, 1),
        "evaluacion": (
            "Riesgo muy alto — reduce el tamaño de apuesta" if prob_ruina > 0.30
            else "Riesgo moderado-alto" if prob_ruina > 0.15
            else "Riesgo aceptable" if prob_ruina > 0.05
            else "Riesgo bajo — estrategia conservadora"
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
# ANÁLISIS DE PARES Y PATRONES (LOTERÍAS)
# ══════════════════════════════════════════════════════════════════════════════

def analizar_pares_frecuentes(resultados: list[dict], top: int = 20) -> list[dict]:
    """
    Encuentra los pares de números que aparecen juntos con mayor frecuencia.
    """
    pares = Counter()
    for r in resultados:
        nums = sorted(r.get("numeros", []))
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                pares[(nums[i], nums[j])] += 1

    return [
        {"par": list(par), "frecuencia": cnt, "descripcion": f"{par[0]}-{par[1]}"}
        for par, cnt in pares.most_common(top)
    ]


def analizar_tripletas(resultados: list[dict], top: int = 10) -> list[dict]:
    """Tripletas de números más frecuentes en el histórico."""
    tripletas = Counter()
    for r in resultados:
        nums = sorted(r.get("numeros", []))
        for i in range(len(nums)):
            for j in range(i + 1, len(nums)):
                for k in range(j + 1, len(nums)):
                    tripletas[(nums[i], nums[j], nums[k])] += 1

    return [
        {"tripleta": list(t), "frecuencia": cnt}
        for t, cnt in tripletas.most_common(top)
    ]


def lstm_simulado(frecuencias: dict, n_numeros: int = 6) -> dict:
    """
    LSTM simulado: genera combinación pesando frecuencias con varianza controlada.
    En producción reemplazar con modelo TensorFlow/PyTorch entrenado.
    """
    # Pesos = frecuencia normalizada con ruido gaussiano controlado
    numeros = list(frecuencias.keys())
    pesos = [
        max(0.01, frecuencias[n]["frecuencia_abs"] + random.gauss(0, 5))
        for n in numeros
    ]
    total_peso = sum(pesos)
    probs = [p / total_peso for p in pesos]

    # Selección sin reemplazo por ruleta ponderada
    seleccion = []
    disponibles = list(zip(numeros, probs))
    while len(seleccion) < n_numeros:
        r = random.random()
        acum = 0
        for num, prob in disponibles:
            acum += prob
            if r <= acum:
                seleccion.append(num)
                disponibles = [(n, p) for n, p in disponibles if n != num]
                total = sum(p for _, p in disponibles)
                if total > 0:
                    disponibles = [(n, p / total) for n, p in disponibles]
                break

    return {
        "metodo": "LSTM simulado (basado en frecuencias ponderadas)",
        "numeros": sorted(seleccion),
        "nota": "Para LSTM real entrenar con TensorFlow sobre histórico completo",
        "produccion_recomendada": "tensorflow >= 2.16 con capas LSTM bidireccionales",
    }
