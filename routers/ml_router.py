"""
Endpoints de ML y multiliga.
"""

import os
from flask import Blueprint, jsonify, request
from auth import login_required

ml_bp = Blueprint("ml", __name__, url_prefix="/api/ml")
ligas_bp = Blueprint("ligas", __name__, url_prefix="/api/ligas")
predicciones_bp = Blueprint("predicciones", __name__, url_prefix="/api/predicciones")


# ── ML ────────────────────────────────────────────────────────────────────────

@ml_bp.route("/predecir")
@login_required
def ml_predecir():
    """Predicción usando el modelo Gradient Boosting ML."""
    from services.ml_model import get_ml_model
    from services.progol import HISTORIAL_DEMO
    home = request.args.get("home", "Club América")
    away = request.args.get("away", "Guadalajara")
    modelo = get_ml_model(HISTORIAL_DEMO)
    return jsonify(modelo.predict(home, away, HISTORIAL_DEMO))


@ml_bp.route("/ensemble-vs-ml")
@login_required
def ensemble_vs_ml():
    """Compara predicción del ensemble estadístico vs el modelo ML."""
    from services.ml_model import get_ml_model
    from services.progol import predecir_partido, HISTORIAL_DEMO
    home = request.args.get("home", "Club América")
    away = request.args.get("away", "Guadalajara")

    pred_ensemble = predecir_partido(home, away)
    pred_ml       = get_ml_model(HISTORIAL_DEMO).predict(home, away, HISTORIAL_DEMO)

    # Promedio ponderado si ambos están disponibles
    combinado = None
    if pred_ml.get("disponible"):
        w_ens, w_ml = 0.65, 0.35
        combinado = {
            "local":     round(pred_ensemble["local"] * w_ens + pred_ml["local"] * w_ml, 4),
            "empate":    round(pred_ensemble["empate"] * w_ens + pred_ml["empate"] * w_ml, 4),
            "visitante": round(pred_ensemble["visitante"] * w_ens + pred_ml["visitante"] * w_ml, 4),
        }
        mx = max(combinado.values())
        combinado["pronostico"] = "1" if mx == combinado["local"] else "X" if mx == combinado["empate"] else "2"
        combinado["confianza_pct"] = round(mx * 100, 1)

    return jsonify({
        "partido":   f"{home} vs {away}",
        "ensemble":  {k: pred_ensemble[k] for k in ["local", "empate", "visitante", "pronostico", "confianza_pct"]},
        "ml":        pred_ml,
        "combinado": combinado,
        "nota":      "Combinado: 65% ensemble + 35% ML (recomendado con historial > 100 partidos)",
    })


@ml_bp.route("/feature-importance")
@login_required
def feature_importance():
    """Importancia de features del modelo ML."""
    from services.ml_model import get_ml_model
    from services.progol import HISTORIAL_DEMO
    modelo = get_ml_model(HISTORIAL_DEMO)
    return jsonify({"features": modelo.feature_importance()})


@ml_bp.route("/entrenar", methods=["POST"])
@login_required
def entrenar():
    """Re-entrena el modelo ML (útil después de cargar datos reales)."""
    from services.ml_model import MLModel, get_ml_model
    from services.progol import HISTORIAL_DEMO
    import services.ml_model as ml_mod

    api_key = os.getenv("API_FOOTBALL_KEY", "")
    historial = HISTORIAL_DEMO

    if api_key:
        try:
            from services.api_football import get_fixtures_liga, LIGAS
            h = get_fixtures_liga(LIGAS["liga_mx"], 2024, api_key)
            if h:
                historial = h
        except Exception:
            pass

    nuevo = MLModel()
    nuevo.fit(historial)
    ml_mod._ml_model = nuevo

    return jsonify({
        "entrenado":     nuevo.entrenado,
        "n_partidos":    len(historial),
        "accuracy_cv":   nuevo.accuracy,
        "usa_datos_reales": api_key != "",
    })


# ── MULTI-LIGA ────────────────────────────────────────────────────────────────

LIGAS_DISPONIBLES = {
    "liga_mx":          {"nombre": "Liga MX",           "id": 262,  "pais": "México"},
    "premier_league":   {"nombre": "Premier League",    "id": 39,   "pais": "Inglaterra"},
    "la_liga":          {"nombre": "La Liga",            "id": 140,  "pais": "España"},
    "serie_a":          {"nombre": "Serie A",            "id": 135,  "pais": "Italia"},
    "bundesliga":       {"nombre": "Bundesliga",         "id": 78,   "pais": "Alemania"},
    "ligue_1":          {"nombre": "Ligue 1",            "id": 61,   "pais": "Francia"},
    "champions_league": {"nombre": "Champions League",  "id": 2,    "pais": "Europa"},
    "mls":              {"nombre": "MLS",                "id": 253,  "pais": "USA"},
}


@ligas_bp.route("/disponibles")
def ligas_disponibles():
    """Lista todas las ligas disponibles en el sistema."""
    return jsonify({"ligas": LIGAS_DISPONIBLES})


@ligas_bp.route("/proximos-partidos")
@login_required
def proximos_partidos():
    """Próximos partidos de cualquier liga."""
    liga_key = request.args.get("liga", "liga_mx")
    dias     = int(request.args.get("dias", 7))
    api_key  = os.getenv("API_FOOTBALL_KEY", "")

    liga_info = LIGAS_DISPONIBLES.get(liga_key)
    if not liga_info:
        return jsonify({"error": f"Liga '{liga_key}' no encontrada. Disponibles: {list(LIGAS_DISPONIBLES.keys())}"}), 400

    if not api_key:
        return jsonify({"error": "API_FOOTBALL_KEY requerida para datos reales", "liga": liga_info})

    try:
        from services.api_football import get_upcoming_fixtures
        partidos = get_upcoming_fixtures(liga_info["id"], dias, api_key)
        return jsonify({
            "liga":     liga_info,
            "partidos": partidos,
            "total":    len(partidos),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ligas_bp.route("/predicciones-liga")
@login_required
def predicciones_liga():
    """Predicciones para los próximos partidos de una liga (datos reales TheSportsDB)."""
    from services.progol import predecir_partido_liga
    liga_key = request.args.get("liga", "liga_mx")

    liga_info = LIGAS_DISPONIBLES.get(liga_key)
    if not liga_info:
        return jsonify({"error": "Liga no encontrada"}), 400

    # Obtener partidos y entrenar con datos reales (ESPN primero, SportsDB respaldo)
    partidos_futuros = []
    historial = []
    try:
        from services import espn_scraper
        partidos_futuros = espn_scraper.get_proximos(liga_key, 14)
        historial = espn_scraper.get_historial_entrenamiento(liga_key)
    except Exception:
        pass
    if not historial and not partidos_futuros:
        try:
            from services import sportsdb
            partidos_futuros = sportsdb.get_next_events(liga_key)
            historial = sportsdb.historial_por_liga(liga_key)
        except Exception as e:
            return jsonify({"error": f"Error obteniendo datos: {e}", "liga": liga_info})

    if not partidos_futuros:
        # Mostrar ranking de la liga si no hay partidos
        ranking = []
        if historial:
            try:
                from models.elo import ELOModel
                elo = ELOModel(); elo.update(historial)
                ranking = [{"equipo": k, "elo": round(v)} for k, v in
                           sorted(elo.ratings.items(), key=lambda x: -x[1])[:18]]
            except Exception:
                pass
        return jsonify({
            "liga": liga_info, "predicciones": [], "total": 0,
            "en_receso": True, "ranking_elo": ranking,
            "partidos_entrenamiento": len(historial),
            "aviso": f"{liga_info['nombre']} sin partidos próximos. Ranking actualizado con {len(historial)} partidos reales.",
        })

    # Entrenar modelo con el historial de esta liga
    predicciones = []
    for p in partidos_futuros[:12]:
        home, away = p.get("home", ""), p.get("away", "")
        if not home or not away:
            continue
        try:
            pred = predecir_partido_liga(home, away, historial)
            predicciones.append({
                "home": home, "away": away, "fecha": p.get("fecha", ""),
                "pronostico":     pred["pronostico"],
                "confianza_pct":  pred["confianza_pct"],
                "prob_local":     pred["local"],
                "prob_empate":    pred["empate"],
                "prob_visitante": pred["visitante"],
            })
        except Exception:
            continue

    return jsonify({
        "liga":         liga_info,
        "predicciones": predicciones,
        "total":        len(predicciones),
        "partidos_entrenamiento": len(historial),
        "usa_datos_reales": True,
        "fuente": "ESPN (temporada actual)",
        "modelo": "Ensemble (Dixon-Coles + ELO + Poisson)",
    })


@ligas_bp.route("/standings")
@login_required
def standings():
    """Tabla de posiciones de una liga (ESPN, temporada actual)."""
    liga_key = request.args.get("liga", "liga_mx")
    liga_info = LIGAS_DISPONIBLES.get(liga_key)
    if not liga_info:
        return jsonify({"error": "Liga no encontrada"}), 400
    try:
        from services import espn_scraper
        tabla = espn_scraper.get_standings(liga_key)
        return jsonify({"liga": liga_info, "tabla": tabla, "fuente": "ESPN"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── PREDICCIONES (tracking) ────────────────────────────────────────────────────

@predicciones_bp.route("/guardar", methods=["POST"])
@login_required
def guardar():
    """Guarda una predicción para tracking posterior."""
    from services.verificador import guardar_prediccion
    d = request.get_json() or {}
    pred_id = guardar_prediccion(
        home=d.get("home", ""),
        away=d.get("away", ""),
        pronostico=d.get("pronostico", ""),
        confianza_pct=d.get("confianza_pct", 0),
        prob_local=d.get("prob_local", 0),
        prob_empate=d.get("prob_empate", 0),
        prob_visitante=d.get("prob_visitante", 0),
        liga=d.get("liga", "Liga MX"),
        fecha_partido=d.get("fecha_partido"),
        modelo=d.get("modelo", "Ensemble"),
    )
    return jsonify({"id": pred_id, "guardada": True})


@predicciones_bp.route("/verificar", methods=["POST"])
@login_required
def verificar():
    """Verifica manualmente el resultado de una predicción."""
    from services.verificador import verificar_prediccion
    d = request.get_json() or {}
    return jsonify(verificar_prediccion(int(d.get("id", 0)), d.get("resultado_real", "")))


@predicciones_bp.route("/verificar-auto")
@login_required
def verificar_auto():
    """Verifica automáticamente predicciones pasadas contra la API."""
    from services.verificador import verificar_automatico
    api_key = os.getenv("API_FOOTBALL_KEY", "")
    return jsonify(verificar_automatico(api_key))


@predicciones_bp.route("/estadisticas")
@login_required
def estadisticas():
    """Accuracy real del modelo basado en predicciones verificadas."""
    from services.verificador import estadisticas_predicciones
    return jsonify(estadisticas_predicciones())
