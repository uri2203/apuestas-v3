"""
Integración con API-Football (api-football.com)
Plan gratuito: 100 requests/día
"""
import os
from datetime import datetime, timedelta

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

API_BASE   = "https://v3.football.api-sports.io"
RAPID_BASE = "https://api-football-v1.p.rapidapi.com/v3"

# Plan FREE de API-Football solo permite temporadas 2022-2024
API_FOOTBALL_MAX_SEASON = int(os.getenv("API_FOOTBALL_MAX_SEASON", "2024"))

def current_season() -> int:
    """
    Retorna la temporada a consultar.
    Limitada a API_FOOTBALL_MAX_SEASON (2024 en plan free).
    """
    from datetime import datetime
    now = datetime.now()
    real_season = now.year if now.month >= 7 else now.year - 1
    # Plan free no accede a temporadas > 2024
    return min(real_season, API_FOOTBALL_MAX_SEASON)

LIGAS = {
    "liga_mx":          262,
    "champions_league": 2,
    "premier_league":   39,
    "la_liga":          140,
    "serie_a":          135,
    "bundesliga":       78,
    "ligue_1":          61,
    "mls":              253,
}

_cache    = {}
_cache_ts = {}
CACHE_TTL = 3600


def _headers(api_key):
    if not api_key:
        return {}
    if len(api_key) > 40:
        return {"x-rapidapi-key": api_key, "x-rapidapi-host": "api-football-v1.p.rapidapi.com"}
    return {"x-apisports-key": api_key}


def _cached_get(url, params, api_key, ttl=CACHE_TTL):
    if not HAS_HTTPX:
        return {"response": []}
    key = url + str(sorted(params.items()))
    now = datetime.now().timestamp()
    if key in _cache and now - _cache_ts.get(key, 0) < ttl:
        return _cache[key]
    try:
        base = RAPID_BASE if (api_key and len(api_key) > 40) else API_BASE
        import httpx
        r = httpx.get(base + url, params=params, headers=_headers(api_key), timeout=12)
        data = r.json()
        _cache[key]    = data
        _cache_ts[key] = now
        return data
    except Exception as e:
        return {"errors": str(e), "response": []}


def get_fixtures_liga(liga_id, season=None, api_key=""):
    if season is None: season = current_season()
    data = _cached_get("/fixtures", {"league": liga_id, "season": season, "status": "FT"}, api_key)
    partidos = []
    for f in data.get("response", []):
        teams = f.get("teams", {})
        goals = f.get("goals", {})
        gh, ga = goals.get("home"), goals.get("away")
        if gh is None or ga is None:
            continue
        partidos.append({
            "fixture_id": f.get("fixture", {}).get("id"),
            "fecha":      f.get("fixture", {}).get("date", ""),
            "home":       teams.get("home", {}).get("name", ""),
            "away":       teams.get("away", {}).get("name", ""),
            "home_goals": int(gh),
            "away_goals": int(ga),
        })
    return partidos


def get_upcoming_fixtures(liga_id=262, days=7, api_key=""):
    today = datetime.now()

    def _fetch(d):
        end = today + timedelta(days=d)
        data = _cached_get("/fixtures", {
            "league": liga_id, "season": current_season(),
            "from":   today.strftime("%Y-%m-%d"),
            "to":     end.strftime("%Y-%m-%d"),
            "status": "NS",
        }, api_key)
        return [
            {
                "fixture_id": f.get("fixture", {}).get("id"),
                "fecha":      f.get("fixture", {}).get("date", ""),
                "home":       f.get("teams", {}).get("home", {}).get("name", ""),
                "away":       f.get("teams", {}).get("away", {}).get("name", ""),
            }
            for f in data.get("response", [])
        ]

    # Buscar en ventana pedida; si no hay, ampliar a 30 días
    partidos = _fetch(days)
    if not partidos:
        partidos = _fetch(30)
    return partidos


def get_standings(liga_id=262, season=None, api_key=""):
    if season is None: season = current_season()
    data = _cached_get("/standings", {"league": liga_id, "season": season}, api_key)
    standings = []
    for group in data.get("response", []):
        for league in group.get("league", {}).get("standings", []):
            for team in league:
                standings.append({
                    "posicion": team.get("rank"),
                    "equipo":   team.get("team", {}).get("name", ""),
                    "pts":      team.get("points"),
                    "pj":       team.get("all", {}).get("played"),
                    "gf":       team.get("all", {}).get("goals", {}).get("for"),
                    "gc":       team.get("all", {}).get("goals", {}).get("against"),
                    "forma":    team.get("form", "")[-5:],
                })
    return standings


def get_progol_jornada(api_key=""):
    upcoming = get_upcoming_fixtures(262, days=7, api_key=api_key)
    return [{"liga": "Liga MX", "liga_id": 262, **p} for p in upcoming[:14]]
