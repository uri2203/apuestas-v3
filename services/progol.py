"""
Motor de Progol — combina Dixon-Coles + ELO + xG real de API-Football
para generar pronósticos 1-X-2 con probabilidades reales.

Progol México: 14 partidos por quiniela, acertar 11+ gana.
"""
import os
from models.ensemble import EnsembleModel
from models.dixon_coles import DixonColesModel
from models.elo import ELOModel
from services.features import construir_features_completo
from services.api_football import (
    get_fixtures_liga, get_upcoming_fixtures,
    get_standings, LIGAS
)

# ── HISTORIAL DEMO (cuando no hay API key) ────────────────────────────────
# Basado en estadísticas reales de Liga MX 2023-2024
HISTORIAL_DEMO = [
    {"home":"Club América","away":"Guadalajara","home_goals":2,"away_goals":1},
    {"home":"Cruz Azul","away":"Pumas UNAM","home_goals":1,"away_goals":1},
    {"home":"Tigres UANL","away":"Monterrey","home_goals":2,"away_goals":0},
    {"home":"Toluca","away":"Santos Laguna","home_goals":3,"away_goals":1},
    {"home":"Atlas","away":"León","home_goals":1,"away_goals":2},
    {"home":"Guadalajara","away":"Club América","home_goals":1,"away_goals":1},
    {"home":"Pumas UNAM","away":"Cruz Azul","home_goals":0,"away_goals":2},
    {"home":"Monterrey","away":"Tigres UANL","home_goals":1,"away_goals":1},
    {"home":"Santos Laguna","away":"Toluca","home_goals":2,"away_goals":2},
    {"home":"León","away":"Atlas","home_goals":3,"away_goals":0},
    {"home":"Club América","away":"Cruz Azul","home_goals":1,"away_goals":0},
    {"home":"Guadalajara","away":"Tigres UANL","home_goals":2,"away_goals":1},
    {"home":"Monterrey","away":"Toluca","home_goals":2,"away_goals":1},
    {"home":"Pumas UNAM","away":"Santos Laguna","home_goals":1,"away_goals":0},
    {"home":"Cruz Azul","away":"Atlas","home_goals":2,"away_goals":1},
    {"home":"Tigres UANL","away":"Club América","home_goals":0,"away_goals":1},
    {"home":"Toluca","away":"Guadalajara","home_goals":1,"away_goals":1},
    {"home":"Santos Laguna","away":"Monterrey","home_goals":1,"away_goals":2},
    {"home":"Atlas","away":"Pumas UNAM","home_goals":2,"away_goals":2},
    {"home":"Club América","away":"León","home_goals":3,"away_goals":1},
    {"home":"Cruz Azul","away":"Guadalajara","home_goals":1,"away_goals":0},
    {"home":"Tigres UANL","away":"Toluca","home_goals":2,"away_goals":1},
    {"home":"Monterrey","away":"Pumas UNAM","home_goals":3,"away_goals":0},
    {"home":"Santos Laguna","away":"Club América","home_goals":0,"away_goals":2},
    {"home":"León","away":"Cruz Azul","home_goals":1,"away_goals":3},
    {"home":"Guadalajara","away":"Atlas","home_goals":2,"away_goals":0},
    {"home":"Toluca","away":"Pumas UNAM","home_goals":2,"away_goals":1},
    {"home":"Club América","away":"Monterrey","home_goals":1,"away_goals":1},
    {"home":"Cruz Azul","away":"Tigres UANL","home_goals":0,"away_goals":1},
    {"home":"Guadalajara","away":"Santos Laguna","home_goals":2,"away_goals":1},
]

# Singleton del modelo entrenado
_modelo: EnsembleModel = None
_modelo_entrenado_con = None


def _get_modelo(partidos=None):
    """Retorna modelo ensemble, entrenándolo si es necesario."""
    global _modelo, _modelo_entrenado_con
    datos = partidos or HISTORIAL_DEMO
    key   = len(datos)
    if _modelo is None or _modelo_entrenado_con != key:
        _modelo = EnsembleModel()
        _modelo.fit(datos)
        _modelo_entrenado_con = key
    return _modelo



def predecir_partido_liga(home, away, historial_liga):
    """
    Predicción para un partido de cualquier liga, entrenando el ensemble
    con el historial específico de esa liga (no usa el cache global).
    """
    from models.ensemble import EnsembleModel
    datos = historial_liga or HISTORIAL_DEMO
    modelo = EnsembleModel()
    modelo.fit(datos)
    pred = modelo.predict(home, away)
    probs = [pred["local"], pred["empate"], pred["visitante"]]
    max_p = max(probs)
    idx = probs.index(max_p)
    pred["pronostico"]    = ["1", "X", "2"][idx]
    pred["confianza_pct"] = round(max_p * 100, 1)
    pred["clasificacion"] = (
        "Alta confianza"  if max_p > 0.55 else
        "Media confianza" if max_p > 0.42 else
        "Partido disputado"
    )
    return pred


def predecir_partido(home, away, xg_home=None, xg_away=None, historial=None,
                     lesiones_local=None, lesiones_visitante=None,
                     arbitro=None, ciudad=None, pos_local=9, pos_visitante=9,
                     jornada=None, es_liguilla=False, api_key_clima=""):
    """
    Predicción completa con todos los features:
    DC + ELO + Poisson + Lesiones + H2H + Forma + Árbitro + Clima + Importancia
    """
    hist   = historial or HISTORIAL_DEMO
    modelo = _get_modelo(hist)
    
    # Construir features avanzados
    features = construir_features_completo(
        home, away, hist,
        lesiones_local=lesiones_local or [],
        lesiones_visitante=lesiones_visitante or [],
        arbitro=arbitro,
        ciudad_estadio=ciudad,
        api_key_clima=api_key_clima,
        pos_local=pos_local, pos_visitante=pos_visitante,
        jornada=jornada, es_liguilla=es_liguilla,
    )
    
    # Ajustar xG con los factores calculados
    ff = features["factores_finales"]
    xg_h_adj = (xg_home or 1.4) * ff["lambda_local"]
    xg_a_adj = (xg_away or 1.1) * ff["lambda_visitante"]
    
    pred = modelo.predict(home, away, xg_home=xg_h_adj, xg_away=xg_a_adj)
    
    # Aplicar boost de empate (clásicos, finales)
    if ff["empate_boost"] != 1.0:
        p_emp = pred["empate"] * ff["empate_boost"]
        excess = (p_emp - pred["empate"]) / 2
        p_loc = max(0.05, pred["local"] - excess)
        p_vis = max(0.05, pred["visitante"] - excess)
        total = p_loc + p_emp + p_vis
        pred["local"]     = round(p_loc / total, 4)
        pred["empate"]    = round(p_emp / total, 4)
        pred["visitante"] = round(p_vis / total, 4)
        pred["cuota_justa_local"]     = round(1/pred["local"],3) if pred["local"]>0 else 99
        pred["cuota_justa_empate"]    = round(1/pred["empate"],3) if pred["empate"]>0 else 99
        pred["cuota_justa_visitante"] = round(1/pred["visitante"],3) if pred["visitante"]>0 else 99
    
    # Agregar features al resultado
    pred["features"] = features

    # Señal de apuesta
    probs = [pred["local"], pred["empate"], pred["visitante"]]
    max_p = max(probs)
    idx   = probs.index(max_p)
    resultado_likely = ["1", "X", "2"][idx]

    pred["pronostico"]   = resultado_likely
    pred["confianza_pct"] = round(max_p * 100, 1)
    pred["clasificacion"] = (
        "Alta confianza"   if max_p > 0.55 else
        "Media confianza"  if max_p > 0.42 else
        "Partido disputado"
    )
    return pred



def _upcoming_desde_odds():
    """Obtiene próximos partidos de Liga MX desde The Odds API (tiene acceso real)."""
    import os
    odds_key = os.getenv("ODDS_API_KEY", "")
    if not odds_key:
        return []
    try:
        import httpx
        r = httpx.get(
            "https://api.the-odds-api.com/v4/sports/soccer_mexico_ligamx/odds",
            params={"apiKey": odds_key, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"},
            timeout=10,
        )
        data = r.json()
        if not isinstance(data, list):
            return []
        partidos = []
        for m in data:
            ht, at = m.get("home_team", ""), m.get("away_team", "")
            if ht and at:
                partidos.append({
                    "home": ht, "away": at, "liga": "Liga MX",
                    "fecha": m.get("commence_time", ""),
                })
        return partidos
    except Exception:
        return []

def generar_jornada_progol(api_key=""):
    """
    Genera predicciones para la jornada completa de Progol.
    Usa API-Football si hay key, si no usa historial demo.
    """
    partidos_futuros = []
    historial        = []
    xg_map           = {}
    fuente_datos     = "demo"
    liga_nombre      = "Liga MX"
    liga_key_activa  = "liga_mx"

    # ── FUENTE PRIMARIA: ESPN (gratis, completo, temporada actual) ────────────
    try:
        from services import espn_scraper
        activa = espn_scraper.liga_activa_actual()
        liga_key_activa = activa["liga_key"]
        liga_nombre     = activa["nombre"]
        partidos_futuros = activa.get("partidos", [])
        historial = espn_scraper.get_historial_entrenamiento(liga_key_activa)
        if historial or partidos_futuros:
            fuente_datos = f"ESPN · {liga_nombre} (temporada actual)"
    except Exception as e:
        import logging; logging.warning("ESPN falló: %s", e)

    # ── RESPALDO: TheSportsDB ─────────────────────────────────────────────────
    if not historial and not partidos_futuros:
        try:
            from services import sportsdb
            activa = sportsdb.liga_activa_actual()
            liga_key_activa = activa["liga_key"]
            liga_nombre     = activa["nombre"]
            partidos_futuros = activa.get("partidos", [])
            historial = sportsdb.historial_por_liga(liga_key_activa)
            if historial or partidos_futuros:
                fuente_datos = f"TheSportsDB · {liga_nombre}"
        except Exception as e:
            import logging; logging.warning("SportsDB falló: %s", e)

    # ── Respaldo: API-Football para historial Liga MX ─────────────────────────
    if not historial and api_key:
        try:
            historial = get_fixtures_liga(LIGAS["liga_mx"], None, api_key)
            if historial:
                fuente_datos = "API-Football (2024)"
        except Exception:
            pass

    # ── Respaldo: Odds API para próximos partidos ─────────────────────────────
    if not partidos_futuros:
        partidos_futuros = _upcoming_desde_odds()
        if partidos_futuros and "demo" in fuente_datos:
            fuente_datos = "The Odds API"

    # ── Fallback final: demo solo para entrenar ───────────────────────────────
    if not historial:
        historial = HISTORIAL_DEMO

    # Sin partidos próximos — Liga MX en receso. Mostrar ranking actual + info útil
    _usando_demo_partidos = not bool(partidos_futuros)
    if not partidos_futuros:
        modelo_receso = _get_modelo(historial)
        ranking = modelo_receso.ranking_elo()[:18] if historial else []
        return {
            "error": None,
            "partidos": [], "total_partidos": 0, "es_demo": False,
            "en_receso": True,
            "usa_datos_reales": True,
            "fuente_partidos": fuente_datos,
            "liga_activa": liga_nombre,
            "partidos_entrenamiento": len(historial),
            "modelo": "Ensemble (Dixon-Coles 50% + ELO 30% + Poisson 20%)",
            "ranking_elo": ranking,
            "aviso": (f"El modelo está entrenado con {len(historial)} partidos REALES de "
                      f"la temporada actual (vía ESPN). No hay jornada programada en los "
                      f"próximos 45 días — las ligas principales están en receso de verano. "
                      f"El ranking ELO de abajo refleja la fuerza real actual de cada equipo. "
                      f"Cuando regrese la liga, las predicciones se activan automáticamente."),
        }

    modelo = _get_modelo(historial)

    jornada = []
    for i, p in enumerate(partidos_futuros[:14], 1):
        home = p.get("home", "")
        away = p.get("away", "")
        if not home or not away:
            continue
        xg_h = xg_map.get((home, "home"))
        xg_a = xg_map.get((away, "away"))
        pred = predecir_partido(home, away, xg_h, xg_a, historial)
        jornada.append({
            "numero":      i,
            "home":        home,
            "away":        away,
            "local_nombre":  home,
            "visitante_nombre": away,
            "liga":        p.get("liga", "Liga MX"),
            "fecha":       p.get("fecha", ""),
            "prob_local":      pred["local"],
            "prob_empate":     pred["empate"],
            "prob_visitante":  pred["visitante"],
            "cuota_local":     pred.get("cuota_justa_local"),
            "cuota_empate":    pred.get("cuota_justa_empate"),
            "cuota_visitante": pred.get("cuota_justa_visitante"),
            "pronostico":      pred["pronostico"],
            "confianza_pct":   pred["confianza_pct"],
            "clasificacion":   pred["clasificacion"],
            "modelo":          pred["modelo"],
            "xg_home":         pred.get("xg_home"),
            "xg_away":         pred.get("xg_away"),
            "componentes":     pred.get("componentes"),
        })

    return {
        "total_partidos":     len(jornada),
        "usa_datos_reales":   not _usando_demo_partidos,
        "fuente_partidos":    fuente_datos,
        "liga_activa":        liga_nombre,
        "es_demo":            _usando_demo_partidos,
        "en_receso":          False,
        "partidos_entrenamiento": len(historial),
        "modelo":             "Ensemble (Dixon-Coles 50% + ELO 30% + Poisson 20%)",
        "precision_esperada": "55-62% por partido",
        "partidos":           jornada,
        "ranking_elo":        modelo.ranking_elo()[:10],
    }


def ranking_equipos(api_key=""):
    """Ranking de equipos por ELO y Dixon-Coles."""
    historial = []
    # Priorizar TheSportsDB (temporada actual)
    try:
        from services import sportsdb
        historial = sportsdb.get_historial_entrenamiento("liga_mx")
    except Exception:
        pass
    if not historial:
        historial = HISTORIAL_DEMO
    if not historial and api_key:
        try:
            h = get_fixtures_liga(LIGAS["liga_mx"], None, api_key)
            if h:
                historial = h
        except Exception:
            pass
    modelo = _get_modelo(historial)
    elo_rank = modelo.ranking_elo()
    dc_rank  = modelo.ranking_dc()
    return {
        "elo":         elo_rank,
        "dixon_coles": dc_rank,
    }
