"""
Tareas programadas — funciones síncronas para BackgroundScheduler.

La versión original usaba AsyncIOScheduler y funciones async que nunca
se inicializaban. Este archivo ahora exporta funciones sync reutilizables
que el scheduler de main.py puede invocar directamente.
"""
import logging
import os

logger = logging.getLogger(__name__)


def actualizar_melate() -> None:
    """Actualiza el último resultado de Melate via scraping (sync)."""
    try:
        import httpx
        from bs4 import BeautifulSoup

        r = httpx.get(
            "https://www.pronosticos.gob.mx/resultados/melate",
            headers={"User-Agent": "Mozilla/5.0 ApuestasPro/4.2"},
            timeout=15,
            follow_redirects=True,
        )
        soup = BeautifulSoup(r.text, "html.parser")
        numeros = []
        for bola in soup.select(".resultado-bola, .numero-ganador, .ball")[:6]:
            try:
                numeros.append(int(bola.get_text(strip=True)))
            except ValueError:
                pass
        if len(numeros) == 6:
            logger.info("Melate actualizado: %s", sorted(numeros))
        else:
            logger.warning("Melate scraping: estructura HTML inesperada (%d números)", len(numeros))
    except Exception as e:
        logger.error("Error actualizando Melate: %s", e)


def actualizar_odds() -> None:
    """Actualiza odds de Liga MX via The Odds API."""
    try:
        import httpx
        from services.deportes import get_any_odds_key
        api_key = get_any_odds_key()
        if not api_key:
            return
        for deporte in ["soccer_mexico_ligamx"]:
            r = httpx.get(
                f"https://api.the-odds-api.com/v4/sports/{deporte}/odds",
                params={"apiKey": api_key, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"},
                timeout=15,
            )
            partidos = r.json()
            logger.info("Odds %s: %d partidos actualizados", deporte, len(partidos))
    except Exception as e:
        logger.error("Error actualizando odds: %s", e)


def detectar_value_bets_automatico() -> None:
    """Detecta value bets usando el modelo ensemble y los registra."""
    try:
        import httpx
        from services.deportes import get_any_odds_key
        from services.progol import predecir_partido

        api_key = get_any_odds_key()
        if not api_key:
            return

        r = httpx.get(
            "https://api.the-odds-api.com/v4/sports/soccer_mexico_ligamx/odds",
            params={"apiKey": api_key, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"},
            timeout=15,
        )
        vb_count = 0
        for m in r.json():
            ht, at = m["home_team"], m["away_team"]
            try:
                pred = predecir_partido(ht, at)
                prob_map = {ht: pred["local"], at: pred["visitante"], "Draw": pred["empate"]}
            except Exception:
                continue
            for book in m.get("bookmakers", []):
                for o in book.get("markets", [{}])[0].get("outcomes", []):
                    mp = prob_map.get(o["name"], 0)
                    if mp <= 0:
                        continue
                    edge = (mp * o["price"] - 1) * 100
                    if edge >= 5:
                        vb_count += 1
        logger.info("Value bets detectados (edge ≥5%%): %d", vb_count)
    except Exception as e:
        logger.error("Error detectando value bets: %s", e)
