"""
Scraper de resultados de loterías mexicanas y odds deportivos.
Fuentes: Pronósticos (lotería oficial), APIs públicas de odds.
"""
import httpx
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

BASE_PRONOSTICOS = "https://www.pronosticos.gob.mx"
ODDS_API_BASE = "https://api.the-odds-api.com/v4"  # API gratuita con key


async def obtener_ultimo_melate() -> Optional[dict]:
    """
    Obtiene el último resultado de Melate desde Pronósticos.
    Retorna dict con números ganadores o None si falla.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{BASE_PRONOSTICOS}/resultados/melate",
                headers={"User-Agent": "Mozilla/5.0 ApuestasPro/1.0"},
            )
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            # Parsear números del resultado más reciente
            # La estructura real depende del HTML de Pronósticos
            numeros = []
            bolas = soup.select(".resultado-bola, .numero-ganador, .ball")
            for bola in bolas[:6]:
                try:
                    numeros.append(int(bola.get_text(strip=True)))
                except ValueError:
                    pass

            if len(numeros) == 6:
                return {
                    "juego": "Melate",
                    "fecha": datetime.now().isoformat(),
                    "numeros": sorted(numeros),
                    "fuente": BASE_PRONOSTICOS,
                }
    except Exception as e:
        logger.warning(f"Error scraping Melate: {e}")

    # Fallback: intentar con datos del CSV histórico de Pronósticos
    return await obtener_melate_csv()


async def obtener_melate_csv() -> Optional[dict]:
    """
    Descarga el CSV histórico oficial de resultados de Melate.
    Pronósticos publica CSVs descargables con todo el historial.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(
                f"{BASE_PRONOSTICOS}/resultados/melate/historico.csv",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            if r.status_code == 200:
                lines = r.text.strip().split("\n")
                if len(lines) > 1:
                    last = lines[-1].split(",")
                    return {
                        "juego": "Melate",
                        "concurso": last[0] if last else "N/A",
                        "fecha": last[1] if len(last) > 1 else datetime.now().isoformat(),
                        "numeros": [int(x) for x in last[2:8] if x.strip().isdigit()],
                    }
    except Exception as e:
        logger.warning(f"Error CSV Melate: {e}")
    return None


async def obtener_historico_melate(limite: int = 500) -> list[dict]:
    """
    Descarga historial completo de Melate.
    Parsea el CSV oficial de Pronósticos.
    """
    resultados = []
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.get(
                f"{BASE_PRONOSTICOS}/resultados/melate/historico.csv",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            lines = r.text.strip().split("\n")[1:]  # Skip header
            for line in lines[-limite:]:
                cols = line.split(",")
                if len(cols) >= 8:
                    try:
                        resultados.append({
                            "concurso": cols[0].strip(),
                            "fecha": cols[1].strip(),
                            "numeros": [int(cols[i].strip()) for i in range(2, 8)],
                            "adicional": int(cols[8].strip()) if len(cols) > 8 else None,
                        })
                    except (ValueError, IndexError):
                        continue
    except Exception as e:
        logger.error(f"Error descargando histórico: {e}")

    return resultados


async def obtener_odds_deportivos(deporte: str = "soccer_mexico_ligamx", api_key: str = "") -> list[dict]:
    """
    Obtiene odds de múltiples casas de apuestas via The Odds API.
    API gratuita: 500 requests/mes. https://the-odds-api.com
    """
    if not api_key:
        return _odds_demo()

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{ODDS_API_BASE}/sports/{deporte}/odds",
                params={
                    "apiKey": api_key,
                    "regions": "eu,us",
                    "markets": "h2h",
                    "oddsFormat": "decimal",
                },
            )
            data = r.json()
            return [
                {
                    "id": m["id"],
                    "deporte": m["sport_title"],
                    "liga": m["sport_key"],
                    "fecha": m["commence_time"],
                    "local": m["home_team"],
                    "visitante": m["away_team"],
                    "odds": {
                        book["title"]: {
                            outcome["name"]: outcome["price"]
                            for outcome in book["outcomes"]
                        }
                        for book in m.get("bookmakers", [])
                    },
                }
                for m in data
            ]
    except Exception as e:
        logger.error(f"Error obteniendo odds: {e}")
        return _odds_demo()


def _odds_demo() -> list[dict]:
    """Datos de ejemplo cuando no hay API key configurada."""
    return [
        {
            "id": "demo1",
            "deporte": "Fútbol",
            "liga": "Liga MX",
            "fecha": datetime.now().isoformat(),
            "local": "Club América",
            "visitante": "Guadalajara",
            "odds": {
                "Bet365": {"Club América": 2.10, "Draw": 3.20, "Guadalajara": 3.50},
                "Codere": {"Club América": 2.05, "Draw": 3.30, "Guadalajara": 3.60},
                "1xBet": {"Club América": 2.15, "Draw": 3.15, "Guadalajara": 3.45},
            },
        }
    ]
