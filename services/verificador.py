"""Verificador automático de predicciones — compatible con PostgreSQL y SQLite."""

import os, logging
from datetime import datetime, timedelta
from database import db, _fetchone, _fetchall, _execute

logger = logging.getLogger(__name__)


def guardar_prediccion(home, away, pronostico, confianza_pct,
                       prob_local, prob_empate, prob_visitante,
                       liga="Liga MX", fecha_partido=None,
                       xg_home=None, xg_away=None, modelo="Ensemble") -> int:
    with db() as conn:
        return _execute(conn,
            "INSERT INTO predictions (home,away,liga,fecha_partido,pronostico,confianza_pct,"
            "prob_local,prob_empate,prob_visitante,xg_home,xg_away,modelo) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (home,away,liga,fecha_partido,pronostico,confianza_pct,
             prob_local,prob_empate,prob_visitante,xg_home,xg_away,modelo))


def verificar_prediccion(pred_id: int, resultado_real: str) -> dict:
    with db() as conn:
        pred = _fetchone(conn, "SELECT * FROM predictions WHERE id=?", (pred_id,))
        if not pred:
            return {"error": f"Predicción {pred_id} no encontrada"}
        correcto = 1 if pred["pronostico"] == resultado_real else 0
        _execute(conn,
            "UPDATE predictions SET resultado_real=?, correcto=?, verificado_at=? WHERE id=?",
            (resultado_real, correcto, datetime.now().isoformat(), pred_id))
    return {"id": pred_id, "pronostico": pred["pronostico"],
            "resultado_real": resultado_real, "correcto": bool(correcto)}


def verificar_automatico(api_key: str = "") -> dict:
    if not api_key:
        return {"verificadas": 0, "mensaje": "Sin API_FOOTBALL_KEY"}
    try:
        import httpx
        ayer = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        with db() as conn:
            pendientes = _fetchall(conn,
                "SELECT * FROM predictions WHERE correcto IS NULL "
                "AND fecha_partido IS NOT NULL AND fecha_partido <= ? "
                "ORDER BY fecha_partido DESC LIMIT 20", (ayer,))
        if not pendientes:
            return {"verificadas": 0, "mensaje": "Sin predicciones pendientes"}
        verificadas = 0
        for pred in pendientes:
            try:
                fecha = (pred["fecha_partido"] or "")[:10]
                if not fecha: continue
                api_host = os.getenv("SPORTS_API_HOST", "v3.football.api-sports.io")
                r = httpx.get("https://v3.football.api-sports.io/fixtures",
                    params={"date": fecha, "league": 262, "status": "FT"},
                    headers={"x-apisports-key": api_key, "x-rapidapi-key": api_key,
                             "x-rapidapi-host": api_host}, timeout=12)
                for f in r.json().get("response", []):
                    ht = f.get("teams",{}).get("home",{}).get("name","")
                    at = f.get("teams",{}).get("away",{}).get("name","")
                    if not (_sim(ht, pred["home"]) and _sim(at, pred["away"])): continue
                    gh = f.get("goals",{}).get("home",0) or 0
                    ga = f.get("goals",{}).get("away",0) or 0
                    verificar_prediccion(pred["id"], "1" if gh>ga else "X" if gh==ga else "2")
                    verificadas += 1; break
            except Exception as e:
                logger.warning("Error verificando pred %d: %s", pred["id"], e)
        return {"verificadas": verificadas, "total_pendientes": len(pendientes)}
    except Exception as e:
        return {"error": str(e)}


def _sim(a, b):
    a,b = a.lower().strip(), b.lower().strip()
    return a==b or a in b or b in a or (len(a)>4 and a[:4] in b)


def estadisticas_predicciones() -> dict:
    with db() as conn:
        todas = _fetchall(conn, "SELECT * FROM predictions")
    verificadas = [p for p in todas if p["correcto"] is not None]
    pendientes  = [p for p in todas if p["correcto"] is None]
    if not verificadas:
        return {"total": len(todas), "verificadas": 0, "pendientes": len(pendientes),
                "mensaje": "Sin predicciones verificadas aún"}
    acertadas = [p for p in verificadas if p["correcto"] == 1]
    accuracy  = round(len(acertadas)/len(verificadas)*100, 1)
    por_resultado = {}
    for res in ["1","X","2"]:
        sub = [p for p in verificadas if p["resultado_real"]==res]
        ok  = [p for p in sub if p["correcto"]==1]
        por_resultado[res] = {"total": len(sub), "acertadas": len(ok),
                               "accuracy_pct": round(len(ok)/len(sub)*100,1) if sub else 0}
    def _acc(g): return round(sum(1 for p in g if p["correcto"]==1)/len(g)*100,1) if g else 0
    alta  = [p for p in verificadas if (p["confianza_pct"] or 0)>=55]
    media = [p for p in verificadas if 42<=(p["confianza_pct"] or 0)<55]
    baja  = [p for p in verificadas if (p["confianza_pct"] or 0)<42]
    return {
        "total": len(todas), "verificadas": len(verificadas),
        "pendientes": len(pendientes), "acertadas": len(acertadas),
        "accuracy_pct": accuracy, "benchmark_aleatorio": 33.3,
        "mejora_vs_aleatorio": round(accuracy-33.3, 1),
        "por_resultado": por_resultado,
        "por_confianza": {
            "alta_55plus":  {"n": len(alta),  "accuracy_pct": _acc(alta)},
            "media_42_55":  {"n": len(media), "accuracy_pct": _acc(media)},
            "baja_menos42": {"n": len(baja),  "accuracy_pct": _acc(baja)},
        },
        "interpretacion": ("Excelente" if accuracy>55 else "Bueno" if accuracy>40 else "Regular"),
    }
