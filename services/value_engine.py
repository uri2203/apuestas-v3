"""
Value Betting Engine — el núcleo de rentabilidad real.

El acierto de predicción NO genera dinero. El VALUE sí:
apostar solo cuando prob_modelo × cuota > 1 (edge positivo),
con el monto óptimo de Kelly, y midiendo CLV para validar.

Este módulo integra:
- Detección de value con margen del modelo vs cuota de la casa
- Kelly fraccionado para el stake óptimo
- Comparación contra Pinnacle (precio justo del mercado)
- Clasificación por confianza y tamaño del edge
"""

import logging

logger = logging.getLogger(__name__)


def quitar_margen_casa(cuotas: dict) -> dict:
    """
    Quita el margen (vig/overround) de las cuotas de una casa para
    obtener la probabilidad 'justa' que la casa realmente estima.

    cuotas: {"1": 2.10, "X": 3.40, "2": 3.80}
    Retorna probabilidades sin margen que suman 1.0
    """
    if not cuotas:
        return {}
    inv = {k: 1.0 / v for k, v in cuotas.items() if v and v > 1}
    total = sum(inv.values())
    if total <= 0:
        return {}
    return {k: round(v / total, 4) for k, v in inv.items()}


def overround(cuotas: dict) -> float:
    """Margen de la casa en %. Mientras más bajo, mejor para el apostador."""
    inv = sum(1.0 / v for v in cuotas.values() if v and v > 1)
    return round((inv - 1) * 100, 2)


def kelly_fraccionado(prob: float, cuota: float, fraccion: float = 0.25,
                      bankroll: float = 0) -> dict:
    """
    Kelly Criterion fraccionado (conservador).
    fraccion 0.25 = cuarto de Kelly (recomendado para recreativo).
    """
    b = cuota - 1
    q = 1 - prob
    kelly_full = (b * prob - q) / b if b > 0 else 0
    kelly_full = max(0, kelly_full)  # nunca negativo
    kelly_aplicado = kelly_full * fraccion

    resultado = {
        "kelly_completo_pct":  round(kelly_full * 100, 2),
        "kelly_aplicado_pct":  round(kelly_aplicado * 100, 2),
        "fraccion_usada":      fraccion,
    }
    if bankroll > 0:
        resultado["stake_sugerido"] = round(bankroll * kelly_aplicado, 2)
    return resultado


def analizar_value(prob_modelo: float, cuota_casa: float,
                   cuota_pinnacle: float = None,
                   bankroll: float = 0, fraccion_kelly: float = 0.25) -> dict:
    """
    Análisis completo de value de una apuesta.

    El edge se mide de dos formas:
    1. Modelo: prob_modelo × cuota - 1
    2. Mercado (si hay Pinnacle): cuota_casa vs precio justo de Pinnacle
    """
    prob_implicita = 1 / cuota_casa if cuota_casa > 1 else 1
    edge_modelo = (prob_modelo * cuota_casa - 1) * 100
    ev_unidad   = (cuota_casa - 1) * prob_modelo - (1 - prob_modelo)

    resultado = {
        "cuota_casa":            cuota_casa,
        "prob_modelo_pct":       round(prob_modelo * 100, 1),
        "prob_implicita_pct":    round(prob_implicita * 100, 1),
        "edge_modelo_pct":       round(edge_modelo, 2),
        "ev_por_unidad":         round(ev_unidad, 4),
        "es_value":              edge_modelo > 0,
    }

    # Validación con Pinnacle (el "precio justo" del mercado)
    if cuota_pinnacle and cuota_pinnacle > 1:
        prob_justa_pinnacle = 1 / cuota_pinnacle
        # Edge real de mercado: cuánto mejor paga la casa vs el precio justo
        edge_mercado = (cuota_casa / cuota_pinnacle - 1) * 100
        resultado["cuota_pinnacle"]       = cuota_pinnacle
        resultado["prob_justa_pinnacle_pct"] = round(prob_justa_pinnacle * 100, 1)
        resultado["edge_mercado_pct"]     = round(edge_mercado, 2)
        # El value MÁS confiable: ambos edges positivos
        resultado["value_confirmado"]     = edge_modelo > 0 and edge_mercado > 0
        resultado["confianza"] = (
            "ALTA — modelo y mercado coinciden" if edge_modelo > 2 and edge_mercado > 1 else
            "MEDIA — solo un indicador positivo" if edge_modelo > 0 or edge_mercado > 0 else
            "BAJA — sin value real"
        )
    else:
        resultado["confianza"] = (
            "MEDIA — solo modelo (sin Pinnacle de referencia)" if edge_modelo > 3 else
            "BAJA — edge pequeño sin confirmar"
        )

    # Kelly para el stake
    if edge_modelo > 0:
        resultado["kelly"] = kelly_fraccionado(prob_modelo, cuota_casa, fraccion_kelly, bankroll)

    # Clasificación final
    resultado["clasificacion"] = (
        "🔥 VALUE FUERTE" if edge_modelo > 7 else
        "✅ VALUE BUENO"  if edge_modelo > 4 else
        "👍 VALUE MODERADO" if edge_modelo > 2 else
        "⚠️ VALUE MARGINAL" if edge_modelo > 0 else
        "❌ SIN VALUE"
    )

    # Recomendación accionable
    if edge_modelo > 4:
        resultado["recomendacion"] = "Apostar el stake de Kelly. Edge sólido."
    elif edge_modelo > 2:
        resultado["recomendacion"] = "Apostar con cautela. Considera medio stake de Kelly."
    elif edge_modelo > 0:
        resultado["recomendacion"] = "Edge marginal. Solo si confías mucho en el modelo."
    else:
        resultado["recomendacion"] = "NO apostar. La casa tiene ventaja."

    return resultado


def clv(cuota_apostada: float, cuota_cierre: float) -> dict:
    """
    Closing Line Value — la métrica REINA de la rentabilidad a largo plazo.

    Si consistentemente apuestas a cuotas mejores que la de cierre,
    serás rentable a largo plazo aunque pierdas apuestas individuales.
    """
    if cuota_cierre <= 1:
        return {"error": "Cuota de cierre inválida"}
    clv_pct = (cuota_apostada / cuota_cierre - 1) * 100
    return {
        "cuota_apostada":  cuota_apostada,
        "cuota_cierre":    cuota_cierre,
        "clv_pct":         round(clv_pct, 2),
        "positivo":        clv_pct > 0,
        "interpretacion": (
            "Excelente — apostaste mucho mejor que el cierre" if clv_pct > 3 else
            "Bueno — batiste el cierre" if clv_pct > 0 else
            "Negativo — el mercado se movió en tu contra"
        ),
        "nota": "CLV positivo consistente = rentabilidad garantizada a largo plazo",
    }


def filtrar_value_bets(value_bets: list, edge_minimo: float = 2.0,
                       solo_confirmados: bool = False) -> list:
    """
    Filtra y ordena value bets por calidad.
    solo_confirmados: si True, solo los validados con Pinnacle.
    """
    filtrados = []
    for vb in value_bets:
        edge = vb.get("edge_modelo_pct", vb.get("edge_porcentaje", 0))
        if edge < edge_minimo:
            continue
        if solo_confirmados and not vb.get("value_confirmado", False):
            continue
        filtrados.append(vb)
    return sorted(filtrados, key=lambda x: x.get("edge_modelo_pct", x.get("edge_porcentaje", 0)),
                  reverse=True)
