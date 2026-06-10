"""
Hedging (cobertura) y Arbitraje.

- Hedging garantizado:  asegurar ganancia tras apuesta ganadora en vivo
- Hedging parcial:      reducir exposición sin garantizar todo
- Arbitraje clásico:    apostar todos los resultados con ganancia garantizada
- Dutching:             distribuir stake en múltiples selecciones para igual ganancia
"""


# ── HEDGING ───────────────────────────────────────────────────────────────────

def calcular_hedge_garantizado(
    stake_original: float,
    cuota_original: float,
    cuota_hedge: float,
) -> dict:
    """
    Calcula el stake de hedge para garantizar ganancia sin importar el resultado.

    Situación típica: apostaste $X a cuota Y antes del partido.
    Ahora la cuota del resultado contrario es Z (en vivo o en otra casa).
    ¿Cuánto apostar en el hedge para asegurar ganancia?

    Fórmula: stake_hedge = (stake_original × cuota_original) / cuota_hedge
    """
    ganancia_potencial = stake_original * cuota_original  # retorno total si gana apuesta original
    stake_hedge        = ganancia_potencial / cuota_hedge

    # Si gana la original
    ganancia_si_original = ganancia_potencial - stake_original - stake_hedge
    # Si gana el hedge
    ganancia_si_hedge    = stake_hedge * cuota_hedge - stake_hedge - stake_original

    ganancia_garantizada = min(ganancia_si_original, ganancia_si_hedge)
    roi_garantizado      = ganancia_garantizada / (stake_original + stake_hedge) * 100

    return {
        "tipo":                  "hedge_garantizado",
        "stake_original":        round(stake_original, 2),
        "cuota_original":        cuota_original,
        "stake_hedge":           round(stake_hedge, 2),
        "cuota_hedge":           cuota_hedge,
        "total_invertido":       round(stake_original + stake_hedge, 2),
        "ganancia_si_original_gana": round(ganancia_si_original, 2),
        "ganancia_si_hedge_gana":    round(ganancia_si_hedge, 2),
        "ganancia_garantizada":  round(ganancia_garantizada, 2),
        "roi_garantizado_pct":   round(roi_garantizado, 2),
        "conviene": ganancia_garantizada > 0,
        "recomendacion": (
            f"Apostar ${round(stake_hedge, 2)} al resultado contrario asegura "
            f"${round(ganancia_garantizada, 2)} de ganancia garantizada ({round(roi_garantizado, 1)}% ROI)"
            if ganancia_garantizada > 0 else
            "Este hedge no asegura ganancia — considera hedge parcial"
        ),
    }


def calcular_hedge_parcial(
    stake_original: float,
    cuota_original: float,
    cuota_hedge: float,
    pct_cobertura: float = 50.0,
) -> dict:
    """
    Hedge parcial: cubre solo un % de la exposición.
    Útil para reducir riesgo sin sacrificar toda la ganancia potencial.
    pct_cobertura: 0-100, qué % del riesgo cubrir
    """
    ganancia_potencial  = stake_original * cuota_original
    stake_hedge_total   = ganancia_potencial / cuota_hedge           # hedge completo
    stake_hedge_parcial = stake_hedge_total * (pct_cobertura / 100)  # hedge parcial

    # Escenarios
    esc_original_gana = ganancia_potencial - stake_original - stake_hedge_parcial
    esc_hedge_gana    = stake_hedge_parcial * cuota_hedge - stake_hedge_parcial - stake_original

    return {
        "tipo":              "hedge_parcial",
        "pct_cobertura":     pct_cobertura,
        "stake_original":    round(stake_original, 2),
        "stake_hedge":       round(stake_hedge_parcial, 2),
        "total_invertido":   round(stake_original + stake_hedge_parcial, 2),
        "escenarios": {
            "apuesta_original_gana": round(esc_original_gana, 2),
            "hedge_gana":            round(esc_hedge_gana, 2),
        },
        "vs_sin_hedge": {
            "si_gana_original":  round(ganancia_potencial - stake_original, 2),
            "si_pierde_original": round(-stake_original, 2),
        },
    }


def matriz_hedging(
    stake_original: float,
    cuota_original: float,
    cuota_hedge: float,
) -> list:
    """
    Tabla de coberturas del 0% al 100% para visualización.
    """
    ganancia_potencial = stake_original * cuota_original
    stake_hedge_total  = ganancia_potencial / cuota_hedge

    tabla = []
    for pct in range(0, 105, 10):
        sh = stake_hedge_total * (pct / 100)
        esc_orig  = ganancia_potencial - stake_original - sh
        esc_hedge = sh * cuota_hedge - sh - stake_original
        tabla.append({
            "cobertura_pct":    pct,
            "stake_hedge":      round(sh, 2),
            "si_original_gana": round(esc_orig, 2),
            "si_hedge_gana":    round(esc_hedge, 2),
            "peor_caso":        round(min(esc_orig, esc_hedge), 2),
        })
    return tabla


# ── ARBITRAJE ─────────────────────────────────────────────────────────────────

def detectar_arbitraje(cuotas: dict, bankroll: float = 1000.0) -> dict:
    if cuota_hedge <= 1 or cuota_back <= 1: return {"error": "Las cuotas deben ser mayores a 1"}
    """
    Detecta y calcula arbitraje en un mercado 1X2 o 2-way.

    cuotas: {"1": 2.10, "X": 3.20, "2": 3.80} o {"Over": 1.85, "Under": 2.05}
    Arbitraje si sum(1/cuota) < 1
    """
    suma_imp = sum(1 / c for c in cuotas.values() if c > 0)
    hay_arb  = suma_imp < 1.0
    margen   = round((1 - suma_imp) * 100, 3)

    if not hay_arb:
        overround = round((suma_imp - 1) * 100, 2)
        return {
            "hay_arbitraje": False,
            "suma_probabilidades": round(suma_imp, 4),
            "overround_casa_pct":  overround,
            "mensaje": f"Sin arbitraje. La casa tiene un margen del {overround}%.",
        }

    # Calcular stakes para garantizar la misma ganancia en todos los resultados
    ganancia_garantizada = bankroll * margen / 100
    stakes = {}
    for resultado, cuota in cuotas.items():
        stakes[resultado] = round(bankroll / (cuota * suma_imp), 2)

    return {
        "hay_arbitraje":        True,
        "suma_probabilidades":  round(suma_imp, 4),
        "margen_arb_pct":       margen,
        "bankroll_total":       round(bankroll, 2),
        "stakes_optimos":       stakes,
        "ganancia_garantizada": round(ganancia_garantizada, 2),
        "roi_pct":              round(margen, 3),
        "cuotas_analizadas":    cuotas,
        "urgencia":             "ALTA — las cuotas de arbitraje duran segundos",
        "instrucciones":        [
            f"Apostar ${v} al resultado '{k}'" for k, v in stakes.items()
        ],
    }


# ── DUTCHING ──────────────────────────────────────────────────────────────────

def calcular_dutching(selecciones: list, bankroll: float = 1000.0) -> dict:
    """
    Dutching: distribuir el bankroll en múltiples selecciones para obtener
    la misma ganancia neta sin importar cuál gane.

    selecciones: [{"nombre": "Chivas", "cuota": 2.10}, {"nombre": "Empate", "cuota": 3.20}]
    """
    suma_imp = sum(1 / s["cuota"] for s in selecciones if s["cuota"] > 0)

    if suma_imp >= 1.0:
        return {
            "viable": False,
            "mensaje": f"Dutching no viable — suma de probabilidades implícitas = {round(suma_imp, 3)} ≥ 1.0",
        }

    ganancia_neta = bankroll * (1 / suma_imp - 1)
    resultado = []
    for s in selecciones:
        stake = round(bankroll / (s["cuota"] * suma_imp), 2)
        resultado.append({
            "seleccion": s["nombre"],
            "cuota":     s["cuota"],
            "stake":     stake,
            "retorno_si_gana": round(stake * s["cuota"], 2),
        })

    return {
        "viable":             True,
        "bankroll_total":     round(bankroll, 2),
        "selecciones":        resultado,
        "ganancia_neta_si_cualquiera_gana": round(ganancia_neta, 2),
        "roi_pct":            round(ganancia_neta / bankroll * 100, 2),
        "suma_probabilidades": round(suma_imp, 4),
    }
