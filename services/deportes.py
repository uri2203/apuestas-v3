"""
Escáner multi-deporte — descubre todos los deportes activos en Odds API
y proporciona utilidades para trabajar con múltiples ligas simultáneamente.
"""
import os
import logging
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

ODDS_API_BASE = "https://api.the-odds-api.com/v4/sports"

# Deportes con mayor ROI potencial (ordenados por rentabilidad documentada)
SPORTS_BY_ROI = [
    "americanfootball_nfl",
    "americanfootball_ncaaf",
    "basketball_nba",
    "basketball_ncaab",
    "icehockey_nhl",
    "baseball_mlb",
    "soccer_usa_mls",
    "soccer_mexico_ligamx",
    "soccer_england_premierleague",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "soccer_uefa_champions_league",
    "tennis_atp_world_tour",
    "mma_mixed_martial_arts",
    "boxing_boxing",
]

_cached_sports = None
_cached_sports_ts = 0


def get_sports_list(api_key: str = None, force_refresh: bool = False) -> list[dict]:
    """Obtiene lista de todos los deportes disponibles en Odds API."""
    global _cached_sports, _cached_sports_ts
    now = datetime.now().timestamp()
    if not force_refresh and _cached_sports and now - _cached_sports_ts < 3600:
        return _cached_sports

    api_key = api_key or os.getenv("ODDS_API_KEY", "")
    if not api_key:
        return []

    try:
        r = httpx.get(
            f"{ODDS_API_BASE}?apiKey={api_key}",
            timeout=10,
        )
        data = r.json()
        if isinstance(data, list):
            active = [s for s in data if s.get("active", False)]
            _cached_sports = active
            _cached_sports_ts = now
            return active
        return []
    except Exception as e:
        logger.error("Error fetching sports list: %s", e)
        return []


def get_active_league_keys(api_key: str = None) -> list[str]:
    """Devuelve solo los keys de deportes activos, priorizando los de alta rentabilidad."""
    sports = get_sports_list(api_key)
    if not sports:
        return []

    active_keys = {s["key"] for s in sports}
    # Primero los de alta rentabilidad que están activos
    ordered = [k for k in SPORTS_BY_ROI if k in active_keys]
    # Luego el resto de activos
    rest = sorted([s["key"] for s in sports if s["key"] not in ordered])
    return ordered + rest


def get_odds_upcoming(
    api_key: str = None,
    regions: str = "us,uk,eu",
    markets: str = "h2h",
) -> list[dict]:
    """Obtiene odds de TODOS los deportes activos en un solo call (upcoming).
    Costo: len(regions) × len(markets) — mucho más barato que llamar por deporte.
    Retorna cualquier partido en vivo + los próximos 8 por deporte."""
    api_key = api_key or os.getenv("ODDS_API_KEY", "")
    if not api_key:
        return []
    try:
        r = httpx.get(
            f"{ODDS_API_BASE}/upcoming/odds",
            params={
                "apiKey": api_key,
                "regions": regions,
                "markets": markets,
                "oddsFormat": "decimal",
            },
            timeout=10,
        )
        data = r.json()
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        logger.warning("Error fetching upcoming odds: %s", e)
        return []


def get_odds_for_sport(
    sport_key: str,
    api_key: str = None,
    regions: str = "us,uk,eu",
    markets: str = "h2h",
) -> list[dict]:
    """Obtiene odds de un deporte específico. Retorna lista vacía si error."""
    api_key = api_key or os.getenv("ODDS_API_KEY", "")
    if not api_key:
        return []
    try:
        r = httpx.get(
            f"{ODDS_API_BASE}/{sport_key}/odds",
            params={
                "apiKey": api_key,
                "regions": regions,
                "markets": markets,
                "oddsFormat": "decimal",
            },
            timeout=10,
        )
        data = r.json()
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        logger.warning("Error fetching odds for %s: %s", sport_key, e)
        return []
