"""
ESPN Scraper — fuente GRATUITA y completa de datos reales de fútbol.

Usa la API pública JSON de ESPN (site.api.espn.com), que es estable,
gratuita y sin límite práctico. Cubre Liga MX y las principales ligas
con resultados históricos y próximos partidos de la temporada ACTUAL.

No requiere API key.
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# Códigos de liga en ESPN
LIGAS_ESPN = {
    "liga_mx":          "mex.1",
    "premier_league":   "eng.1",
    "la_liga":          "esp.1",
    "serie_a":          "ita.1",
    "bundesliga":       "ger.1",
    "ligue_1":          "fra.1",
    "champions_league": "uefa.champions",
    "mls":              "usa.1",
}

BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"

_cache = {}
_cache_ts = {}
CACHE_TTL = 1800  # 30 min


def _get(url: str, params: dict = None, ttl: int = CACHE_TTL):
    if not HAS_HTTPX:
        return {}
    key = url + str(params or {})
    now = datetime.now().timestamp()
    if key in _cache and now - _cache_ts.get(key, 0) < ttl:
        return _cache[key]
    try:
        r = httpx.get(url, params=params or {}, timeout=15,
                      headers={"User-Agent": "Mozilla/5.0 (ApuestasPro/4.3)"})
        data = r.json()
        _cache[key] = data
        _cache_ts[key] = now
        return data
    except Exception as e:
        logger.warning("ESPN error %s: %s", url, e)
        return {}


def _parse_event(ev: dict) -> dict:
    """Extrae datos de un evento de ESPN."""
    try:
        comp = ev.get("competitions", [{}])[0]
        competitors = comp.get("competitors", [])
        home = away = None
        home_score = away_score = None
        for c in competitors:
            team_name = c.get("team", {}).get("displayName", "") or c.get("team", {}).get("name", "")
            score = c.get("score")
            if c.get("homeAway") == "home":
                home = team_name
                home_score = score
            else:
                away = team_name
                away_score = score

        status = ev.get("status", {}).get("type", {}).get("state", "")  # pre, in, post
        completado = status == "post"

        result = {
            "home":  home,
            "away":  away,
            "fecha": ev.get("date", "")[:10],
            "estado": status,
        }
        if completado and home_score is not None and away_score is not None:
            try:
                result["home_goals"] = int(home_score)
                result["away_goals"] = int(away_score)
            except (ValueError, TypeError):
                pass
        return result
    except Exception:
        return {}


def get_resultados(liga_key: str = "liga_mx", dias_atras: int = 120) -> list:
    """
    Resultados de partidos terminados en los últimos N días.
    Para entrenar el modelo con datos reales de la temporada actual.
    """
    liga = LIGAS_ESPN.get(liga_key, "mex.1")
    hoy = datetime.now()
    inicio = hoy - timedelta(days=dias_atras)

    # ESPN acepta rango de fechas YYYYMMDD-YYYYMMDD
    dates = f"{inicio.strftime('%Y%m%d')}-{hoy.strftime('%Y%m%d')}"
    data = _get(f"{BASE}/{liga}/scoreboard", {"dates": dates, "limit": 500})

    partidos = []
    for ev in data.get("events", []):
        p = _parse_event(ev)
        if p.get("home") and p.get("away") and "home_goals" in p:
            partidos.append({
                "home":       p["home"],
                "away":       p["away"],
                "home_goals": p["home_goals"],
                "away_goals": p["away_goals"],
                "fecha":      p["fecha"],
            })
    return partidos


def get_proximos(liga_key: str = "liga_mx", dias_adelante: int = 14) -> list:
    """Próximos partidos programados (no jugados aún)."""
    liga = LIGAS_ESPN.get(liga_key, "mex.1")
    hoy = datetime.now()
    fin = hoy + timedelta(days=dias_adelante)

    dates = f"{hoy.strftime('%Y%m%d')}-{fin.strftime('%Y%m%d')}"
    data = _get(f"{BASE}/{liga}/scoreboard", {"dates": dates, "limit": 200})

    partidos = []
    for ev in data.get("events", []):
        p = _parse_event(ev)
        if p.get("home") and p.get("away") and p.get("estado") in ("pre", ""):
            partidos.append({
                "home":  p["home"],
                "away":  p["away"],
                "fecha": p["fecha"],
                "liga":  liga_key,
            })
    return partidos


def get_historial_entrenamiento(liga_key: str = "liga_mx") -> list:
    """
    Mejor historial disponible para entrenar el modelo.
    Trae hasta ~180 días de resultados reales (temporada actual + parte anterior).
    """
    partidos = get_resultados(liga_key, dias_atras=180)
    # Si hay pocos, ampliar a un año
    if len(partidos) < 30:
        partidos = get_resultados(liga_key, dias_atras=365)
    partidos.sort(key=lambda x: x.get("fecha", ""))
    return partidos


def get_standings(liga_key: str = "liga_mx") -> list:
    """Tabla de posiciones actual."""
    liga = LIGAS_ESPN.get(liga_key, "mex.1")
    data = _get(f"{BASE}/{liga}/standings")
    tabla = []
    try:
        groups = data.get("children", []) or [data]
        for g in groups:
            standings = g.get("standings", {}).get("entries", [])
            for e in standings:
                stats = {s.get("name"): s.get("value") for s in e.get("stats", [])}
                tabla.append({
                    "equipo":   e.get("team", {}).get("displayName", ""),
                    "posicion": stats.get("rank"),
                    "puntos":   stats.get("points"),
                    "jugados":  stats.get("gamesPlayed"),
                    "ganados":  stats.get("wins"),
                    "empates":  stats.get("ties"),
                    "perdidos": stats.get("losses"),
                })
    except Exception as e:
        logger.warning("ESPN standings parse: %s", e)
    return tabla


def liga_activa_actual() -> dict:
    """Detecta qué liga tiene partidos próximos. Busca hasta 45 días."""
    prioridad = [
        ("liga_mx", "Liga MX"), ("mls", "MLS"),
        ("premier_league", "Premier League"), ("la_liga", "La Liga"),
        ("serie_a", "Serie A"), ("champions_league", "Champions League"),
        ("bundesliga", "Bundesliga"), ("ligue_1", "Ligue 1"),
    ]
    # Primera pasada: 14 días (partidos inminentes)
    for dias in (14, 45):
        for liga_key, nombre in prioridad:
            try:
                nxt = get_proximos(liga_key, dias)
                if nxt:
                    return {"liga_key": liga_key, "nombre": nombre,
                            "next_events": len(nxt), "partidos": nxt,
                            "en_receso": False, "ventana_dias": dias}
            except Exception:
                continue
    return {"liga_key": "liga_mx", "nombre": "Liga MX",
            "next_events": 0, "partidos": [], "en_receso": True}


def diagnostico(liga_key: str = "liga_mx") -> dict:
    """Diagnóstico de la conexión con ESPN."""
    result = {
        "fuente":  "ESPN API pública",
        "liga":    liga_key,
        "liga_espn_code": LIGAS_ESPN.get(liga_key, "?"),
    }
    try:
        res = get_resultados(liga_key, 120)
        result["resultados_120d"] = len(res)
        result["resultado_ejemplo"] = res[-3:] if res else []
    except Exception as e:
        result["resultados_error"] = str(e)[:150]

    try:
        prox = get_proximos(liga_key, 14)
        result["proximos_14d"] = len(prox)
        result["proximo_ejemplo"] = prox[:3]
    except Exception as e:
        result["proximos_error"] = str(e)[:150]

    try:
        hist = get_historial_entrenamiento(liga_key)
        result["historial_entrenamiento"] = len(hist)
    except Exception as e:
        result["historial_error"] = str(e)[:150]

    try:
        result["liga_activa_detectada"] = liga_activa_actual()["nombre"]
    except Exception:
        pass

    return result
