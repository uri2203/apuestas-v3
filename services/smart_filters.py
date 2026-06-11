"""
Smart Filters Compuestos — alertas de máxima calidad que solo se disparan
cuando TODAS las señales clave coinciden simultáneamente.

Cada señal individual es ruidosa. La convergencia de múltiples señales
independientes es lo que separa una apuesta educada de una oportunidad real.

Señales consideradas:
  A. Value edge ≥ umbral (prob_modelo × cuota > 1)
  B. Sharp money score ≥ umbral (dinero profesional confirmando)
  C. Overround de la casa ≤ umbral (casa más eficiente = mejor precio)
  D. Ventana temporal ≥ umbral (+48h antes del partido = línea aún no eficiente)
  E. CLV histórico de la casa positivo (esa casa consistentemente da valor)

Score compuesto = combinación ponderada de señales activas.
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Configuración de umbrales por defecto
DEFAULT_THRESHOLDS = {
    "edge_minimo": 5.0,
    "sharp_minimo": 65,
    "overround_maximo": 5.0,
    "horas_antes_minimo": 48,
    "clv_historico_minimo": 0.0,
}

# Pesos de cada señal en el score compuesto (suma = 100)
SIGNAL_WEIGHTS = {
    "edge": 30,
    "sharp": 25,
    "overround": 20,
    "timing": 15,
    "clv_historico": 10,
}


def calcular_overround(bookmaker: dict) -> float:
    """Calcula el overround (vig) de una casa a partir de sus cuotas."""
    outcomes = bookmaker.get("markets", [{}])[0].get("outcomes", [])
    if not outcomes:
        return 99
    inv_sum = sum(1.0 / o["price"] for o in outcomes if o.get("price", 0) > 1)
    return round((inv_sum - 1) * 100, 2) if inv_sum > 0 else 99


def calcular_score_compuesto(
    edge_pct: float,
    sharp_score: float = 0,
    overround: float = 5.0,
    horas_antes: float = 48,
    clv_promedio_casa: float = 0,
    thresholds: dict = None,
) -> dict:
    """
    Calcula el score compuesto (0-100) y determina si la señal es válida.

    Retorna:
      - score: 0-100
      - aprobado: True si TODOS los filtros pasan
      - senales_activas: qué filtros pasaron
      - clasificacion: texto descriptivo
    """
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    senales = {}

    # A. Edge
    edge_ok = edge_pct >= t["edge_minimo"]
    senales["edge"] = {
        "activa": edge_ok,
        "valor": edge_pct,
        "umbral": t["edge_minimo"],
        "peso": SIGNAL_WEIGHTS["edge"] if edge_ok else 0,
    }

    # B. Sharp
    sharp_ok = sharp_score >= t["sharp_minimo"]
    senales["sharp"] = {
        "activa": sharp_ok,
        "valor": sharp_score,
        "umbral": t["sharp_minimo"],
        "peso": SIGNAL_WEIGHTS["sharp"] if sharp_ok else 0,
    }

    # C. Overround
    overround_ok = overround <= t["overround_maximo"]
    senales["overround"] = {
        "activa": overround_ok,
        "valor": overround,
        "umbral": t["overround_maximo"],
        "peso": SIGNAL_WEIGHTS["overround"] if overround_ok else 0,
    }

    # D. Timing
    timing_ok = horas_antes >= t["horas_antes_minimo"]
    senales["timing"] = {
        "activa": timing_ok,
        "valor": horas_antes,
        "umbral": t["horas_antes_minimo"],
        "peso": SIGNAL_WEIGHTS["timing"] if timing_ok else 0,
    }

    # E. CLV histórico
    clv_ok = clv_promedio_casa >= t["clv_historico_minimo"]
    senales["clv_historico"] = {
        "activa": clv_ok,
        "valor": clv_promedio_casa,
        "umbral": t["clv_historico_minimo"],
        "peso": SIGNAL_WEIGHTS["clv_historico"] if clv_ok else 0,
    }

    # Score compuesto = suma de pesos de señales activas
    score = sum(s["peso"] for s in senales.values())

    # Todas las señales deben estar activas para aprobar
    todas_activas = all(s["activa"] for s in senales.values())
    aprobado = todas_activas and score >= 80

    # Clasificación
    n_activas = sum(1 for s in senales.values() if s["activa"])
    n_total = len(senales)

    if aprobado:
        clasificacion = "OPORTUNIDAD CONFIRMADA"
    elif n_activas >= 4:
        clasificacion = "SEÑAL FUERTE — monitorear, falta 1 filtro"
    elif n_activas >= 3:
        clasificacion = "SEÑAL MODERADA — esperar confirmación"
    elif n_activas >= 2:
        clasificacion = "SEÑAL DÉBIL — corroborar con más datos"
    else:
        clasificacion = "RUIDO — filtros no aprueban"

    return {
        "score": score,
        "aprobado": aprobado,
        "clasificacion": clasificacion,
        "senales_activas": n_activas,
        "senales_totales": n_total,
        "detalle_senales": senales,
        "thresholds_usados": t,
    }


def filtrar_value_bets(value_bets: list, thresholds: dict = None) -> dict:
    """
    Filtra una lista de value bets a través de los smart filters compuestos.
    Solo retorna los que pasan TODOS los filtros.

    value_bets: lista de dicts con al menos:
      - edge_porcentaje
      - casa (nombre de bookmaker)
      - partido
      - fecha (commence_time)
    """
    from database import db, _fetchall

    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    aprobados = []
    rechazados = []
    fuente = {}

    for vb in value_bets:
        edge = vb.get("edge_porcentaje", 0) or vb.get("edge_pct", 0)
        casa = vb.get("casa", "")
        partido = vb.get("partido", "")
        fecha_str = vb.get("fecha", "")

        # Sharp score: buscar en DB si hay alerta sharp para este partido
        sharp_score = 0
        try:
            with db() as conn:
                row = _fetchone(conn,
                    "SELECT detalle FROM alerts_log WHERE partido=? AND tipo='SHARP' ORDER BY id DESC LIMIT 1",
                    (partido,))
                if row:
                    import re
                    m = re.search(r'Score\s*[:]\s*(\d+)', row.get("detalle", ""))
                    if m:
                        sharp_score = int(m.group(1))
        except Exception:
            pass

        # Overround: consultar rating de la casa
        overround = 5.0
        try:
            with db() as conn:
                row = _fetchone(conn,
                    "SELECT avg_overround FROM bookmaker_ratings WHERE bookmaker=? ORDER BY id DESC LIMIT 1",
                    (casa,))
                if row:
                    overround = row.get("avg_overround", 5.0) or 5.0
        except Exception:
            pass

        # Horas antes del partido
        horas_antes = 48
        if fecha_str:
            try:
                ct = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
                horas_antes = max(0, (ct - datetime.now().astimezone()).total_seconds() / 3600)
            except Exception:
                pass

        # CLV histórico de la casa
        clv = 0
        try:
            with db() as conn:
                row = _fetchone(conn,
                    "SELECT avg_clv FROM bookmaker_ratings WHERE bookmaker=? ORDER BY id DESC LIMIT 1",
                    (casa,))
                if row:
                    clv = row.get("avg_clv", 0) or 0
        except Exception:
            pass

        compuesto = calcular_score_compuesto(
            edge_pct=edge, sharp_score=sharp_score,
            overround=overround, horas_antes=horas_antes,
            clv_promedio_casa=clv, thresholds=t,
        )

        entry = {
            "partido": partido,
            "casa": casa,
            "edge_pct": edge,
            "sharp_score": sharp_score,
            "overround": overround,
            "horas_antes": round(horas_antes, 1),
            "clv_casa": clv,
            "score_compuesto": compuesto["score"],
            "aprobado": compuesto["aprobado"],
            "clasificacion": compuesto["clasificacion"],
            "detalle_senales": compuesto["detalle_senales"],
        }

        if compuesto["aprobado"]:
            aprobados.append(entry)
        else:
            rechazados.append(entry)

    return {
        "total_analizados": len(value_bets),
        "aprobados": len(aprobados),
        "rechazados": len(rechazados),
        "thresholds": t,
        "resultados_aprobados": aprobados,
        "resultados_rechazados": rechazados[:10],
    }


def _fetchone(conn, sql, params=None):
    """Helper interno para no depender del módulo database."""
    if params is None:
        params = ()
    if hasattr(conn, 'execute'):
        cur = conn.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        return dict(row) if row else None
    return None
