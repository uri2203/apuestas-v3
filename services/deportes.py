"""
Escáner multi-deporte — descubre todos los deportes activos en Odds API
y proporciona utilidades para trabajar con múltiples ligas simultáneamente.

Soporta CASCADEO de API keys: si una key se agota, usa la siguiente automáticamente.
Configura: ODDS_API_KEYS=key1,key2,key3 (separadas por coma)
"""
import os
import logging
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

ODDS_API_BASE = "https://api.the-odds-api.com/v4/sports"

# Deportes con mayor ROI potencial (ordenados por rentabilidad documentada)
SPORTS_BY_ROI = [
    "soccer_fifa_world_cup",
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

# ── API Key Cascade ──────────────────────────────────────────────────────────

def get_any_odds_key() -> str:
    """Retorna cualquier API key válida (de ODDS_API_KEYS o ODDS_API_KEY).
    Para usar donde solo se necesita un string para pasar a funciones externas."""
    for key in _get_api_keys():
        if not _is_key_exhausted(key):
            return key
    # Retornar la primera aunque esté agotada (para checks de "está configurada?")
    keys = _get_api_keys()
    return keys[0] if keys else ""


def _get_api_keys() -> list[str]:
    """Retorna lista de API keys configuradas, en orden de preferencia.
    Soporta: ODDS_API_KEYS=key1,key2,key3 o ODDS_API_KEY=key1"""
    keys = []
    # Primero: lista separada por comas (nuevo formato)
    multi = os.getenv("ODDS_API_KEYS", "")
    if multi:
        keys = [k.strip() for k in multi.split(",") if k.strip()]
    # Fallback: key individual
    if not keys:
        single = os.getenv("ODDS_API_KEY", "")
        if single:
            keys = [single]
    return keys


# Cache de keys agotadas: {key: timestamp_cuando_fallo}
_exhausted_keys: dict[str, float] = {}
EXHAUST_TTL = 300  # 5 minutos antes de reintentar una key agotada


def _is_key_exhausted(key: str) -> bool:
    """Verifica si una key fue marcada como agotada recientemente."""
    ts = _exhausted_keys.get(key)
    if ts and (datetime.now().timestamp() - ts) < EXHAUST_TTL:
        return True
    return False


def _mark_key_exhausted(key: str):
    """Marca una key como agotada."""
    _exhausted_keys[key] = datetime.now().timestamp()
    logger.warning("API Key agotada, marcada para reintento en %ds: ...%s", EXHAUST_TTL, key[-6:])


def _get_working_key() -> str | None:
    """Retorna la primera key que no esté agotada, o None si todas lo están."""
    for key in _get_api_keys():
        if not _is_key_exhausted(key):
            return key
    return None


def get_odds_upcoming(
    api_key: str = None,
    regions: str = "us,uk,eu",
    markets: str = "h2h",
) -> list[dict]:
    """Obtiene odds de TODOS los deportes activos en un solo call (upcoming).
    Costo: len(regions) × len(markets) — mucho más barato que llamar por deporte.
    Soporta cascadeo de keys: si una falla, usa la siguiente."""
    keys_to_try = []
    if api_key:
        keys_to_try = [api_key]
    else:
        keys_to_try = [k for k in _get_api_keys() if not _is_key_exhausted(k)]

    if not keys_to_try:
        logger.warning("Sin API keys disponibles para upcoming odds")
        return []

    for key in keys_to_try:
        try:
            r = httpx.get(
                f"{ODDS_API_BASE}/upcoming/odds",
                params={
                    "apiKey": key,
                    "regions": regions,
                    "markets": markets,
                    "oddsFormat": "decimal",
                },
                timeout=10,
            )
            # Verificar si la key tiene cuota agotada
            remaining = int(r.headers.get("x-requests-remaining", "999"))
            if remaining <= 0 or r.status_code == 429:
                _mark_key_exhausted(key)
                logger.info("Key ...%s agotada (%s remaining), probando siguiente", key[-6:], remaining)
                continue

            data = r.json()
            if isinstance(data, list):
                return data
            # Si la respuesta no es lista, es un error
            logger.warning("Odds API respondió no-lista con key ...%s: %s", key[-6:], str(data)[:100])
            continue
        except Exception as e:
            logger.warning("Error con key ...%s en upcoming: %s", key[-6:], e)
            continue

    logger.warning("Todas las API keys fallaron para upcoming odds")
    return []


def get_odds_for_sport(
    sport_key: str,
    api_key: str = None,
    regions: str = "us,uk,eu",
    markets: str = "h2h",
) -> list[dict]:
    """Obtiene odds de un deporte específico. Soporta cascadeo de keys."""
    keys_to_try = []
    if api_key:
        keys_to_try = [api_key]
    else:
        keys_to_try = [k for k in _get_api_keys() if not _is_key_exhausted(k)]

    if not keys_to_try:
        logger.warning("Sin API keys disponibles para %s", sport_key)
        return []

    for key in keys_to_try:
        try:
            r = httpx.get(
                f"{ODDS_API_BASE}/{sport_key}/odds",
                params={
                    "apiKey": key,
                    "regions": regions,
                    "markets": markets,
                    "oddsFormat": "decimal",
                },
                timeout=10,
            )
            remaining = int(r.headers.get("x-requests-remaining", "999"))
            if remaining <= 0 or r.status_code == 429:
                _mark_key_exhausted(key)
                logger.info("Key ...%s agotada (%s remaining), probando siguiente", key[-6:], remaining)
                continue

            data = r.json()
            if isinstance(data, list):
                return data
            continue
        except Exception as e:
            logger.warning("Error con key ...%s en %s: %s", key[-6:], sport_key, e)
            continue

    logger.warning("Todas las API keys fallaron para %s", sport_key)
    return []


def get_sports_list(api_key: str = None, force_refresh: bool = False) -> list[dict]:
    """Obtiene lista de todos los deportes disponibles en Odds API."""
    global _cached_sports, _cached_sports_ts
    now = datetime.now().timestamp()
    if not force_refresh and _cached_sports and now - _cached_sports_ts < 3600:
        return _cached_sports

    keys_to_try = []
    if api_key:
        keys_to_try = [api_key]
    else:
        keys_to_try = [k for k in _get_api_keys() if not _is_key_exhausted(k)]

    if not keys_to_try:
        return []

    for key in keys_to_try:
        try:
            r = httpx.get(
                f"{ODDS_API_BASE}?apiKey={key}",
                timeout=10,
            )
            remaining = int(r.headers.get("x-requests-remaining", "999"))
            if remaining <= 0 or r.status_code == 429:
                _mark_key_exhausted(key)
                continue

            data = r.json()
            if isinstance(data, list):
                active = [s for s in data if s.get("active", False)]
                _cached_sports = active
                _cached_sports_ts = now
                return active
            continue
        except Exception as e:
            logger.warning("Error con key ...%s en sports list: %s", key[-6:], e)
            continue

    return []


def get_active_league_keys(api_key: str = None) -> list[str]:
    """Devuelve solo los keys de deportes activos, priorizando los de alta rentabilidad."""
    sports = get_sports_list(api_key)
    if not sports:
        return []

    active_keys = {s["key"] for s in sports}
    ordered = [k for k in SPORTS_BY_ROI if k in active_keys]
    rest = sorted([s["key"] for s in sports if s["key"] not in ordered])
    return ordered + rest


def get_key_status() -> list[dict]:
    """Estado de todas las keys configuradas — útil para diagnóstico."""
    result = []
    for key in _get_api_keys():
        info = {
            "key_suffix": "..."+key[-6:] if len(key) > 6 else "***",
            "exhausted": _is_key_exhausted(key),
        }
        try:
            r = httpx.get(
                f"{ODDS_API_BASE}?apiKey={key}",
                timeout=8,
            )
            info["ok"] = r.status_code == 200
            info["remaining"] = r.headers.get("x-requests-remaining", "?")
            info["used"] = r.headers.get("x-requests-used", "?")
            info["status_code"] = r.status_code
        except Exception as e:
            info["ok"] = False
            info["error"] = str(e)[:100]
        result.append(info)
    return result
