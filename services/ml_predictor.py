"""
ML Predictivo Automático — entrena modelos con datos ESPN gratis
y genera predicciones con confidence score.

Flujo:
  1. Fetch historial ESPN (resultados reales)
  2. Entrenar EnsembleModel (Dixon-Coles + ELO)
  3. Fetch próximos partidos ESPN
  4. Predecir cada uno
  5. Guardar en DB + retornar
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from models.ensemble import EnsembleModel
    HAS_MODELS = True
except ImportError:
    HAS_MODELS = False


def auto_train(liga_key: str = "liga_mx") -> dict:
    """Entrena el modelo con historial ESPN y predice próximos partidos."""
    from services.espn_scraper import get_historial_entrenamiento, get_proximos

    historial = get_historial_entrenamiento(liga_key)
    if len(historial) < 20:
        return {"error": f"Historial insuficiente: {len(historial)} partidos (min 20)",
                "liga": liga_key}

    if not HAS_MODELS:
        return {"error": "Modelos no disponibles (falta numpy/scipy?)"}

    modelo = EnsembleModel()
    try:
        modelo.fit(historial)
    except Exception as e:
        logger.error("Error entrenando modelo: %s", e)
        return {"error": f"Error entrenando: {e}"}

    proximos = get_proximos(liga_key, 14)
    if not proximos:
        return {"error": "No hay próximos partidos", "liga": liga_key,
                "historial_usado": len(historial)}

    predicciones = []
    for p in proximos:
        home = p.get("home", "")
        away = p.get("away", "")
        if not home or not away:
            continue
        try:
            pred = modelo.predict(home, away)
        except Exception as e:
            logger.warning("Error prediciendo %s vs %s: %s", home, away, e)
            continue

        probs = [
            ("1", pred.get("local", 0)),
            ("X", pred.get("empate", 0)),
            ("2", pred.get("visitante", 0)),
        ]
        probs.sort(key=lambda x: x[1], reverse=True)
        pick, conf = probs[0]

        # Solo guardar si confianza > 35% (umbral mínimo)
        if conf < 0.35:
            continue

        predicciones.append({
            "home": home,
            "away": away,
            "liga": liga_key,
            "fecha": p.get("fecha", ""),
            "pronostico": pick,
            "confianza_pct": round(conf * 100, 1),
            "prob_local": round(pred.get("local", 0) * 100, 1),
            "prob_empate": round(pred.get("empate", 0) * 100, 1),
            "prob_visitante": round(pred.get("visitante", 0) * 100, 1),
            "modelo": "ensemble",
        })

    # Guardar en DB
    from database import db, _execute, _fetchall
    try:
        with db() as conn:
            for p in predicciones:
                _execute(conn,
                    "INSERT INTO predictions "
                    "(home, away, liga, fecha_partido, pronostico, confianza_pct, "
                    "prob_local, prob_empate, prob_visitante, modelo) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (p["home"], p["away"], p["liga"], p["fecha"],
                     p["pronostico"], p["confianza_pct"],
                     p["prob_local"], p["prob_empate"], p["prob_visitante"],
                     p["modelo"]))
        logger.info("ML Predictor: %d predicciones guardadas para %s",
                    len(predicciones), liga_key)
    except Exception as e:
        logger.error("Error guardando predicciones: %s", e)

    return {
        "liga": liga_key,
        "historial_usado": len(historial),
        "total_predicciones": len(predicciones),
        "predicciones": predicciones,
    }


def auto_train_all() -> dict:
    """Entrena para TODAS las ligas disponibles y acumula resultados."""
    ligas = ["liga_mx", "mls", "premier_league", "la_liga",
             "serie_a", "bundesliga", "ligue_1"]
    total_preds = 0
    errores = []
    for liga in ligas:
        try:
            res = auto_train(liga)
            if "error" not in res:
                total_preds += res.get("total_predicciones", 0)
            else:
                errores.append(f"{liga}: {res['error']}")
        except Exception as e:
            errores.append(f"{liga}: {e}")
    return {
        "total_predicciones": total_preds,
        "ligas_procesadas": len(ligas) - len(errores),
        "errores": errores,
    }


def verificar_resultados() -> dict:
    """Verifica predicciones anteriores contra resultados reales ESPN."""
    from services.espn_scraper import get_resultados
    from database import db, _fetchall, _execute

    # Predicciones sin verificar
    try:
        with db() as conn:
            pendientes = _fetchall(conn,
                "SELECT * FROM predictions WHERE resultado_real IS NULL "
                "AND fecha_partido != '' AND fecha_partido IS NOT NULL "
                "ORDER BY id DESC LIMIT 100")
    except Exception as e:
        return {"error": f"DB error: {e}"}

    if not pendientes:
        return {"verificados": 0, "mensaje": "Sin predicciones pendientes"}

    # Obtener resultados reales para cada liga involucrada
    ligas_unicas = set(p.get("liga", "liga_mx") for p in pendientes)
    resultados_por_liga = {}
    for liga in ligas_unicas:
        try:
            resultados_por_liga[liga] = get_resultados(liga, 30)
        except Exception:
            resultados_por_liga[liga] = []

    verificados = 0
    for p in pendientes:
        fecha = p.get("fecha_partido", "")
        home = p.get("home", "")
        away = p.get("away", "")
        if not home or not away:
            continue
        for r in resultados_por_liga.get(p.get("liga", ""), []):
            if (r.get("home", "") == home and r.get("away", "") == away
                    and r.get("fecha", "")[:10] == fecha[:10]):
                gh = r.get("home_goals")
                ga = r.get("away_goals")
                if gh is None or ga is None:
                    continue
                real = "1" if gh > ga else "X" if gh == ga else "2"
                correcto = 1 if p.get("pronostico", "") == real else 0
                try:
                    with db() as conn:
                        _execute(conn,
                            "UPDATE predictions SET resultado_real=?, correcto=?, "
                            "verificado_at=? WHERE id=?",
                            (real, correcto, datetime.now().isoformat(), p["id"]))
                    verificados += 1
                except Exception:
                    pass
                break

    return {"verificados": verificados, "total_pendientes": len(pendientes)}
