"""
Verificador automático de predicciones.

Compara las predicciones guardadas en la DB contra los resultados
reales obtenidos de API-Football. Actualiza accuracy en tiempo real.
"""

import os
import logging
from datetime import datetime, timedelta
from database import db, rows_to_list

logger = logging.getLogger(__name__)


def guardar_prediccion(
    home: str, away: str, pronostico: str, confianza_pct: float,
    prob_local: float, prob_empate: float, prob_visitante: float,
    liga: str = "Liga MX", fecha_partido: str = None,
    xg_home: float = None, xg_away: float = None, modelo: str = "Ensemble",
) -> int:
    """Guarda una predicción en la DB. Retorna el ID."""
    with db() as conn:
        cur = conn.execute(
            """INSERT INTO predictions
               (home, away, liga, fecha_partido, pronostico, confianza_pct,
                prob_local, prob_empate, prob_visitante, xg_home, xg_away, modelo)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (home, away, liga, fecha_partido, pronostico, confianza_pct,
             prob_local, prob_empate, prob_visitante, xg_home, xg_away, modelo),
        )
        return cur.lastrowid


def verificar_prediccion(pred_id: int, resultado_real: str) -> dict:
    """
    Marca una predicción como verificada.
    resultado_real: '1' | 'X' | '2'
    """
    with db() as conn:
        pred = conn.execute("SELECT * FROM predictions WHERE id=?", (pred_id,)).fetchone()
        if not pred:
            return {"error": f"Predicción {pred_id} no encontrada"}

        correcto = 1 if pred["pronostico"] == resultado_real else 0
        conn.execute(
            """UPDATE predictions SET resultado_real=?, correcto=?, verificado_at=?
               WHERE id=?""",
            (resultado_real, correcto, datetime.now().isoformat(), pred_id),
        )
    return {
        "id":             pred_id,
        "pronostico":     pred["pronostico"],
        "resultado_real": resultado_real,
        "correcto":       bool(correcto),
    }


def verificar_automatico(api_key: str = "") -> dict:
    """
    Busca predicciones pendientes con fecha de partido pasada y las verifica
    contra la API de API-Football.
    """
    if not api_key:
        return {"verificadas": 0, "mensaje": "Sin API_FOOTBALL_KEY — verificación manual"}

    try:
        import httpx
        # Predicciones sin verificar con fecha pasada
        ayer = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        with db() as conn:
            pendientes = rows_to_list(conn.execute(
                """SELECT * FROM predictions
                   WHERE correcto IS NULL AND fecha_partido IS NOT NULL
                   AND fecha_partido <= ?
                   ORDER BY fecha_partido DESC LIMIT 20""",
                (ayer,),
            ).fetchall())

        if not pendientes:
            return {"verificadas": 0, "mensaje": "Sin predicciones pendientes para verificar"}

        verificadas = 0
        for pred in pendientes:
            # Buscar resultado real en la API
            try:
                fecha = pred["fecha_partido"][:10] if pred["fecha_partido"] else None
                if not fecha:
                    continue

                headers = {"x-apisports-key": api_key}
                r = httpx.get(
                    "https://v3.football.api-sports.io/fixtures",
                    params={
                        "date": fecha,
                        "league": 262,  # Liga MX
                        "status": "FT",
                    },
                    headers=headers, timeout=12,
                )
                fixtures = r.json().get("response", [])

                for f in fixtures:
                    ht = f.get("teams", {}).get("home", {}).get("name", "")
                    at = f.get("teams", {}).get("away", {}).get("name", "")
                    # Coincidencia aproximada de nombres
                    if not (_nombre_similar(ht, pred["home"]) and _nombre_similar(at, pred["away"])):
                        continue

                    gh = f.get("goals", {}).get("home", 0) or 0
                    ga = f.get("goals", {}).get("away", 0) or 0
                    real = "1" if gh > ga else "X" if gh == ga else "2"
                    verificar_prediccion(pred["id"], real)
                    verificadas += 1
                    break

            except Exception as e:
                logger.warning("Error verificando pred %d: %s", pred["id"], e)

        return {"verificadas": verificadas, "total_pendientes": len(pendientes)}

    except Exception as e:
        logger.error("verificar_automatico error: %s", e)
        return {"error": str(e)}


def _nombre_similar(a: str, b: str) -> bool:
    """Comparación laxa de nombres de equipos."""
    a, b = a.lower().strip(), b.lower().strip()
    return a == b or a in b or b in a or (len(a) > 4 and a[:4] in b)


def estadisticas_predicciones() -> dict:
    """Accuracy real del modelo basado en predicciones verificadas."""
    with db() as conn:
        todas = rows_to_list(conn.execute("SELECT * FROM predictions").fetchall())

    verificadas = [p for p in todas if p["correcto"] is not None]
    pendientes  = [p for p in todas if p["correcto"] is None]

    if not verificadas:
        return {
            "total":       len(todas),
            "verificadas": 0,
            "pendientes":  len(pendientes),
            "mensaje":     "Sin predicciones verificadas aún",
        }

    acertadas = [p for p in verificadas if p["correcto"] == 1]
    accuracy  = round(len(acertadas) / len(verificadas) * 100, 1)

    # Por resultado real
    por_resultado = {}
    for res in ["1", "X", "2"]:
        sub = [p for p in verificadas if p["resultado_real"] == res]
        ok  = [p for p in sub if p["correcto"] == 1]
        por_resultado[res] = {
            "total":        len(sub),
            "acertadas":    len(ok),
            "accuracy_pct": round(len(ok) / len(sub) * 100, 1) if sub else 0,
        }

    # Por confianza
    alta  = [p for p in verificadas if (p["confianza_pct"] or 0) >= 55]
    media = [p for p in verificadas if 42 <= (p["confianza_pct"] or 0) < 55]
    baja  = [p for p in verificadas if (p["confianza_pct"] or 0) < 42]

    def _acc(grupo):
        if not grupo:
            return 0
        return round(sum(1 for p in grupo if p["correcto"] == 1) / len(grupo) * 100, 1)

    # Tendencia (últimas 20)
    ultimas = sorted(verificadas, key=lambda x: x.get("created_at", ""), reverse=True)[:20]
    tendencia_acc = _acc(ultimas)

    return {
        "total":       len(todas),
        "verificadas": len(verificadas),
        "pendientes":  len(pendientes),
        "acertadas":   len(acertadas),
        "accuracy_pct": accuracy,
        "benchmark_aleatorio": 33.3,
        "mejora_vs_aleatorio": round(accuracy - 33.3, 1),
        "por_resultado": por_resultado,
        "por_confianza": {
            "alta_55plus": {"n": len(alta), "accuracy_pct": _acc(alta)},
            "media_42_55": {"n": len(media), "accuracy_pct": _acc(media)},
            "baja_menos42": {"n": len(baja), "accuracy_pct": _acc(baja)},
        },
        "tendencia_ultimas_20_pct": tendencia_acc,
        "interpretacion": (
            "Excelente — supera el benchmark profesional (55%)" if accuracy > 55 else
            "Bueno — por encima del aleatorio"                   if accuracy > 40 else
            "Regular — cerca del azar"
        ),
    }
