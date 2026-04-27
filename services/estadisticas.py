"""
Motor estadístico para análisis de loterías y apuestas.
Incluye: frecuencias, rachas, probabilidades, value bets, Kelly.
"""
from collections import Counter
from typing import Optional
import math
import statistics


# ─── ANÁLISIS DE FRECUENCIAS ─────────────────────────────────────────────────

def calcular_frecuencias(resultados: list[dict], campo: str = "numeros") -> dict:
    """
    Calcula frecuencia absoluta y relativa de cada número.
    """
    todos = []
    for r in resultados:
        todos.extend(r.get(campo, []))

    contador = Counter(todos)
    total_sorteos = len(resultados)
    total_apariciones = len(todos)

    return {
        num: {
            "frecuencia_abs": cnt,
            "frecuencia_rel": round(cnt / total_sorteos, 4),
            "probabilidad_teorica": round(1 / 56, 4),  # Para Melate 6/56
            "desviacion": round((cnt / total_sorteos) - (1 / 56), 4),
        }
        for num, cnt in sorted(contador.items())
    }


def numeros_calientes(frecuencias: dict, top: int = 10) -> list[dict]:
    """Números que aparecen con mayor frecuencia (sobre la media)."""
    sorted_nums = sorted(frecuencias.items(), key=lambda x: x[1]["frecuencia_abs"], reverse=True)
    return [{"numero": n, **data} for n, data in sorted_nums[:top]]


def numeros_frios(frecuencias: dict, top: int = 10) -> list[dict]:
    """Números que aparecen con menor frecuencia (bajo la media)."""
    sorted_nums = sorted(frecuencias.items(), key=lambda x: x[1]["frecuencia_abs"])
    return [{"numero": n, **data} for n, data in sorted_nums[:top]]


def calcular_rachas(resultados: list[dict], numero: int) -> dict:
    """
    Calcula la racha actual sin aparecer de un número específico.
    """
    racha_actual = 0
    max_racha_sin = 0
    max_racha_con = 0
    racha_temp_sin = 0
    racha_temp_con = 0

    for r in reversed(resultados):
        if numero in r.get("numeros", []):
            if racha_actual == 0:
                racha_actual = racha_temp_sin
            racha_temp_con += 1
            racha_temp_sin = 0
            max_racha_con = max(max_racha_con, racha_temp_con)
        else:
            racha_temp_sin += 1
            racha_temp_con = 0
            max_racha_sin = max(max_racha_sin, racha_temp_sin)

    return {
        "numero": numero,
        "sorteos_sin_salir": racha_actual if racha_actual > 0 else racha_temp_sin,
        "maxima_racha_sin_salir": max_racha_sin,
        "maxima_racha_consecutiva": max_racha_con,
    }


# ─── PROBABILIDADES ───────────────────────────────────────────────────────────

def combinaciones(n: int, r: int) -> int:
    """Calcula C(n, r)."""
    return math.comb(n, r)


def probabilidades_melate() -> dict:
    """
    Probabilidades exactas para Melate 6/56.
    """
    total_combinaciones = combinaciones(56, 6)  # 4,096,720

    return {
        "juego": "Melate",
        "numeros_disponibles": 56,
        "numeros_por_boleto": 6,
        "total_combinaciones": total_combinaciones,
        "premios": {
            "primer_lugar_6": {
                "aciertos": 6,
                "combinaciones_ganadoras": 1,
                "probabilidad": round(1 / total_combinaciones, 10),
                "probabilidad_1_en": total_combinaciones,
                "odds_justo": round(total_combinaciones, 0),
            },
            "segundo_lugar_5": {
                "aciertos": 5,
                "combinaciones_ganadoras": combinaciones(6, 5) * combinaciones(50, 1),
                "probabilidad": round((combinaciones(6, 5) * 50) / total_combinaciones, 8),
                "probabilidad_1_en": round(total_combinaciones / (combinaciones(6, 5) * 50), 0),
            },
            "tercer_lugar_4": {
                "aciertos": 4,
                "combinaciones_ganadoras": combinaciones(6, 4) * combinaciones(50, 2),
                "probabilidad": round((combinaciones(6, 4) * combinaciones(50, 2)) / total_combinaciones, 6),
                "probabilidad_1_en": round(total_combinaciones / (combinaciones(6, 4) * combinaciones(50, 2)), 0),
            },
            "cuarto_lugar_3": {
                "aciertos": 3,
                "combinaciones_ganadoras": combinaciones(6, 3) * combinaciones(50, 3),
                "probabilidad": round((combinaciones(6, 3) * combinaciones(50, 3)) / total_combinaciones, 6),
                "probabilidad_1_en": round(total_combinaciones / (combinaciones(6, 3) * combinaciones(50, 3)), 0),
            },
        },
    }


# ─── VALUE BETS ───────────────────────────────────────────────────────────────

def detectar_value_bet(cuota_decimal: float, probabilidad_estimada: float) -> dict:
    """
    Detecta si una apuesta tiene valor positivo.
    Value bet = cuando prob_real * cuota > 1
    """
    ev = (cuota_decimal - 1) * probabilidad_estimada - (1 - probabilidad_estimada)
    edge = (probabilidad_estimada * cuota_decimal - 1) * 100
    prob_implicita = 1 / cuota_decimal

    return {
        "cuota": cuota_decimal,
        "probabilidad_estimada": round(probabilidad_estimada, 4),
        "probabilidad_implicita_casa": round(prob_implicita, 4),
        "valor_esperado_por_unidad": round(ev, 4),
        "edge_porcentaje": round(edge, 2),
        "es_value_bet": ev > 0,
        "clasificacion": (
            "value bet fuerte" if edge > 5
            else "value bet moderado" if edge > 2
            else "value bet marginal" if edge > 0
            else "sin valor"
        ),
    }


def comparar_odds_casas(odds_por_casa: dict, evento: str) -> dict:
    """
    Compara odds de un mismo evento entre múltiples casas.
    Detecta arbitrajes y la mejor cuota disponible.
    """
    resultados = {}

    # Mejor cuota por resultado
    for resultado in set(k for v in odds_por_casa.values() for k in v):
        cuotas = {
            casa: cuotas.get(resultado, 0)
            for casa, cuotas in odds_por_casa.items()
            if resultado in cuotas
        }
        if cuotas:
            mejor_casa = max(cuotas, key=cuotas.get)
            resultados[resultado] = {
                "mejor_cuota": cuotas[mejor_casa],
                "mejor_casa": mejor_casa,
                "todas_las_cuotas": cuotas,
                "variacion_max_min": round(
                    max(cuotas.values()) / min(cuotas.values()) - 1, 4
                ) if min(cuotas.values()) > 0 else 0,
            }

    # Detectar arbitraje (suma de probabilidades implícitas < 1)
    try:
        mejores = [v["mejor_cuota"] for v in resultados.values()]
        suma_prob = sum(1 / c for c in mejores if c > 0)
        hay_arb = suma_prob < 1.0
        ganancia_arb = round((1 / suma_prob - 1) * 100, 2) if hay_arb else 0
    except (ZeroDivisionError, ValueError):
        hay_arb = False
        ganancia_arb = 0

    return {
        "evento": evento,
        "resultados": resultados,
        "arbitraje": {
            "detectado": hay_arb,
            "ganancia_garantizada_pct": ganancia_arb,
        },
    }


# ─── CRITERIO DE KELLY ────────────────────────────────────────────────────────

def criterio_kelly(
    bankroll: float,
    cuota_decimal: float,
    probabilidad_estimada: float,
    fraccion: float = 0.5,
) -> dict:
    """
    Calcula el tamaño óptimo de apuesta según el Criterio de Kelly.
    fraccion=0.5 → Medio Kelly (recomendado, más conservador)
    """
    b = cuota_decimal - 1  # ganancia por unidad apostada
    p = probabilidad_estimada
    q = 1 - p

    kelly_puro = (b * p - q) / b if b > 0 else 0
    kelly_ajustado = kelly_puro * fraccion
    apuesta_sugerida = max(0, bankroll * kelly_ajustado)

    ganancia_esperada = apuesta_sugerida * b * p - apuesta_sugerida * q
    roi_esperado = (ganancia_esperada / apuesta_sugerida * 100) if apuesta_sugerida > 0 else 0

    return {
        "bankroll": bankroll,
        "cuota": cuota_decimal,
        "probabilidad": round(p, 4),
        "kelly_puro_pct": round(kelly_puro * 100, 2),
        "kelly_ajustado_pct": round(kelly_ajustado * 100, 2),
        "fraccion_usada": fraccion,
        "apuesta_sugerida": round(apuesta_sugerida, 2),
        "apuesta_maxima_recomendada": round(bankroll * 0.05, 2),  # 5% max conservador
        "ganancia_esperada": round(ganancia_esperada, 2),
        "roi_esperado_pct": round(roi_esperado, 2),
        "hay_valor": kelly_puro > 0,
        "recomendacion": (
            "Apuesta el monto sugerido" if kelly_puro > 0.02
            else "Kelly positivo marginal, considera reducir" if kelly_puro > 0
            else "Kelly negativo: NO apostar en esta cuota con esta probabilidad"
        ),
    }


# ─── GENERADOR DE COMBINACIONES ───────────────────────────────────────────────

def generar_combinacion(
    frecuencias: dict,
    modo: str = "balanceado",
    n_numeros: int = 6,
    rango_max: int = 56,
) -> list[int]:
    """
    Genera combinaciones basadas en análisis estadístico.
    modos: 'caliente', 'frio', 'balanceado', 'aleatorio'
    """
    import random

    todos = list(range(1, rango_max + 1))

    if modo == "caliente" and frecuencias:
        pool = sorted(frecuencias, key=lambda x: frecuencias[x]["frecuencia_abs"], reverse=True)[:25]
    elif modo == "frio" and frecuencias:
        pool = sorted(frecuencias, key=lambda x: frecuencias[x]["frecuencia_abs"])[:25]
    elif modo == "balanceado" and frecuencias:
        calientes = sorted(frecuencias, key=lambda x: frecuencias[x]["frecuencia_abs"], reverse=True)[:20]
        frios = sorted(frecuencias, key=lambda x: frecuencias[x]["frecuencia_abs"])[:20]
        pool = list(set(calientes + frios))
    else:
        pool = todos

    seleccion = random.sample(pool, min(n_numeros, len(pool)))
    return sorted(seleccion)
