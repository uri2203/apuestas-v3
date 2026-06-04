"""
TheSportsDB — fuente GRATUITA de datos actuales de Liga MX.

A diferencia de API-Football (plan free limitado a 2022-2024),
TheSportsDB da acceso a la temporada actual sin costo.

Key gratuita de prueba: "3" (o "123"). Para más requests, key gratis
registrándose en thesportsdb.com.

Liga MX ID en TheSportsDB: 4350
"""

import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

SPORTSDB_KEY = os.getenv("SPORTSDB_KEY", "3").strip()
BASE = f"https://www.thesportsdb.com/api/v1/json/{SPORTSDB_KEY}"

# IDs de ligas en TheSportsDB
LIGAS_SDB = {
    "liga_mx":          "4350",   # Mexican Liga MX
    "premier_league":   "4328",
    "la_liga":          "4335",
    "serie_a":          "4332",
    "bundesliga":       "4331",
    "ligue_1":          "4334",
    "champions_league": "4480",
    "mls":              "4346",
}

_cache = {}
_cache_ts = {}
CACHE_TTL = 1800  # 30 min


def _cached_get(url: str, params: dict = None, ttl: int = CACHE_TTL):
    if not HAS_HTTPX:
        return {}
    key = url + str(params or {})
    now = datetime.now().timestamp()
    if key in _cache and now - _cache_ts.get(key, 0) < ttl:
        return _cache[key]
    try:
        r = httpx.get(url, params=params or {}, timeout=12,
                      headers={"User-Agent": "ApuestasPro/4.3"})
        data = r.json()
        _cache[key] = data
        _cache_ts[key] = now
        return data
    except Exception as e:
        logger.warning("SportsDB error %s: %s", url, e)
        return {}


def get_past_events(liga_key: str = "liga_mx", max_events: int = 30) -> list:
    """
    Últimos resultados de la liga (con marcadores reales) para entrenar el modelo.
    eventspastleague devuelve los últimos ~15 partidos jugados.
    """
    liga_id = LIGAS_SDB.get(liga_key, "4350")
    data = _cached_get(f"{BASE}/eventspastleague.php", {"id": liga_id})
    events = data.get("events") or []
    partidos = []
    for e in events:
        hs = e.get("intHomeScore")
        as_ = e.get("intAwayScore")
        if hs in (None, "") or as_ in (None, ""):
            continue
        try:
            partidos.append({
                "home":       e.get("strHomeTeam", ""),
                "away":       e.get("strAwayTeam", ""),
                "home_goals": int(hs),
                "away_goals": int(as_),
                "fecha":      e.get("dateEvent", ""),
            })
        except (ValueError, TypeError):
            continue
    return partidos[:max_events]


def get_next_events(liga_key: str = "liga_mx") -> list:
    """Próximos partidos programados de la liga."""
    liga_id = LIGAS_SDB.get(liga_key, "4350")
    data = _cached_get(f"{BASE}/eventsnextleague.php", {"id": liga_id})
    events = data.get("events") or []
    return [
        {
            "home":  e.get("strHomeTeam", ""),
            "away":  e.get("strAwayTeam", ""),
            "fecha": e.get("dateEvent", ""),
            "hora":  e.get("strTime", ""),
            "liga":  e.get("strLeague", "Liga MX"),
            "jornada": e.get("intRound", ""),
        }
        for e in events
        if e.get("strHomeTeam") and e.get("strAwayTeam")
    ]


def get_season_events(liga_key: str = "liga_mx", season: str = None) -> list:
    """
    Todos los partidos de una temporada (con marcadores).
    season formato: "2025-2026". Si None, usa la temporada actual.
    Da MÁS datos de entrenamiento que get_past_events.
    """
    liga_id = LIGAS_SDB.get(liga_key, "4350")
    if not season:
        now = datetime.now()
        # Liga MX: temporada cruza el año (Apertura/Clausura)
        y = now.year
        season = f"{y}-{y+1}" if now.month >= 7 else f"{y-1}-{y}"

    data = _cached_get(f"{BASE}/eventsseason.php", {"id": liga_id, "s": season})
    events = data.get("events") or []
    partidos = []
    for e in events:
        hs = e.get("intHomeScore")
        as_ = e.get("intAwayScore")
        if hs in (None, "") or as_ in (None, ""):
            continue
        try:
            partidos.append({
                "home":       e.get("strHomeTeam", ""),
                "away":       e.get("strAwayTeam", ""),
                "home_goals": int(hs),
                "away_goals": int(as_),
                "fecha":      e.get("dateEvent", ""),
            })
        except (ValueError, TypeError):
            continue
    return partidos


def get_historial_entrenamiento(liga_key: str = "liga_mx") -> list:
    """
    Mejor historial disponible para entrenar:
    1. Temporada actual completa (eventsseason)
    2. Si está vacía, temporada anterior
    3. Combina con últimos resultados (eventspastleague)
    """
    now = datetime.now()
    y = now.year
    season_actual   = f"{y}-{y+1}" if now.month >= 7 else f"{y-1}-{y}"
    season_anterior = f"{y-1}-{y}" if now.month >= 7 else f"{y-2}-{y-1}"

    partidos = get_season_events(liga_key, season_actual)

    # Si la temporada actual tiene pocos partidos, agregar la anterior
    if len(partidos) < 30:
        prev = get_season_events(liga_key, season_anterior)
        # Combinar sin duplicar
        vistos = {(p["home"], p["away"], p["fecha"]) for p in partidos}
        for p in prev:
            if (p["home"], p["away"], p["fecha"]) not in vistos:
                partidos.append(p)

    # Si aún hay pocos, agregar últimos resultados
    if len(partidos) < 20:
        past = get_past_events(liga_key, 30)
        vistos = {(p["home"], p["away"], p["fecha"]) for p in partidos}
        for p in past:
            if (p["home"], p["away"], p["fecha"]) not in vistos:
                partidos.append(p)

    # Ordenar por fecha
    partidos.sort(key=lambda x: x.get("fecha", ""))
    return partidos


def diagnostico(liga_key: str = "liga_mx") -> dict:
    """Diagnóstico de la conexión con TheSportsDB para una liga."""
    now = datetime.now()
    y = now.year
    season = f"{y}-{y+1}" if now.month >= 7 else f"{y-1}-{y}"

    result = {
        "liga":          liga_key,
        "key_usada":     SPORTSDB_KEY,
        "liga_id":       LIGAS_SDB.get(liga_key, "?"),
        "season_actual": season,
    }

    try:
        past = get_past_events(liga_key, 30)
        result["past_events"] = len(past)
        result["past_ejemplo"] = past[:3]
    except Exception as e:
        result["past_error"] = str(e)[:150]

    try:
        nxt = get_next_events(liga_key)
        result["next_events"] = len(nxt)
        result["next_ejemplo"] = nxt[:3]
    except Exception as e:
        result["next_error"] = str(e)[:150]

    try:
        season_ev = get_season_events(liga_key, season)
        result["season_events"] = len(season_ev)
    except Exception as e:
        result["season_error"] = str(e)[:150]

    try:
        hist = get_historial_entrenamiento(liga_key)
        result["historial_entrenamiento"] = len(hist)
    except Exception as e:
        result["historial_error"] = str(e)[:150]

    # Liga activa detectada
    try:
        result["liga_activa_detectada"] = liga_activa_actual()["nombre"]
    except Exception:
        pass

    return result


def liga_activa_actual() -> dict:
    """
    Detecta automáticamente qué liga tiene partidos próximos.
    Prioriza Liga MX; si está en receso, busca otras ligas activas.
    Retorna {liga_key, nombre, next_events, en_receso}.
    """
    # Orden de preferencia: Liga MX primero, luego las que juegan todo el año / verano
    prioridad = [
        ("liga_mx",          "Liga MX"),
        ("mls",              "MLS"),              # juega abr-oct (verano)
        ("premier_league",   "Premier League"),  # ago-may
        ("la_liga",          "La Liga"),
        ("serie_a",          "Serie A"),
        ("champions_league", "Champions League"),
        ("bundesliga",       "Bundesliga"),
        ("ligue_1",          "Ligue 1"),
    ]
    for liga_key, nombre in prioridad:
        try:
            nxt = get_next_events(liga_key)
            if nxt:
                return {
                    "liga_key":    liga_key,
                    "nombre":      nombre,
                    "next_events": len(nxt),
                    "partidos":    nxt,
                    "en_receso":   False,
                }
        except Exception:
            continue
    # Ninguna liga con partidos próximos
    return {"liga_key": "liga_mx", "nombre": "Liga MX", "next_events": 0,
            "partidos": [], "en_receso": True}


def historial_por_liga(liga_key: str = "liga_mx") -> list:
    """Historial de entrenamiento para una liga específica."""
    return get_historial_entrenamiento(liga_key)
