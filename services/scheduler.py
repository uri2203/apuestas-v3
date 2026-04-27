"""
Tareas programadas: scraping automático de resultados y odds.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)


def iniciar_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()

    # Actualizar resultados de Melate (lunes, miércoles y viernes a las 22:00 hora CDMX)
    scheduler.add_job(
        actualizar_melate,
        CronTrigger(day_of_week="mon,wed,fri", hour=22, minute=30, timezone="America/Mexico_City"),
        id="melate_actualizar",
        name="Actualizar resultados Melate",
        replace_existing=True,
    )

    # Actualizar odds deportivos cada hora
    scheduler.add_job(
        actualizar_odds,
        "interval",
        hours=1,
        id="odds_actualizar",
        name="Actualizar odds deportivos",
        replace_existing=True,
    )

    # Detectar value bets cada 15 minutos
    scheduler.add_job(
        detectar_value_bets_automatico,
        "interval",
        minutes=15,
        id="value_bets",
        name="Detección automática de value bets",
        replace_existing=True,
    )

    logger.info("Scheduler inicializado con 3 tareas programadas")
    return scheduler


async def actualizar_melate():
    """Actualiza los resultados más recientes de Melate."""
    try:
        from services.scraper import obtener_ultimo_melate
        resultado = await obtener_ultimo_melate()
        if resultado:
            logger.info(f"Melate actualizado: {resultado['numeros']}")
        else:
            logger.warning("No se pudo actualizar Melate")
    except Exception as e:
        logger.error(f"Error actualizando Melate: {e}")


async def actualizar_odds():
    """Actualiza odds de los principales mercados deportivos."""
    try:
        from services.scraper import obtener_odds_deportivos
        import os
        api_key = os.getenv("ODDS_API_KEY", "")
        for deporte in ["soccer_mexico_ligamx", "basketball_nba"]:
            odds = await obtener_odds_deportivos(deporte, api_key)
            logger.info(f"Odds {deporte}: {len(odds)} partidos actualizados")
    except Exception as e:
        logger.error(f"Error actualizando odds: {e}")


async def detectar_value_bets_automatico():
    """Detecta value bets automáticamente y los registra."""
    try:
        from services.scraper import obtener_odds_deportivos
        from services.estadisticas import detectar_value_bet
        import os
        api_key = os.getenv("ODDS_API_KEY", "")
        partidos = await obtener_odds_deportivos("soccer_mexico_ligamx", api_key)
        vb_count = 0
        for partido in partidos:
            for resultado, cuotas_casa in partido.get("odds", {}).items():
                for casa, cuota in cuotas_casa.items():
                    if cuota > 1:
                        analisis = detectar_value_bet(cuota, 1 / cuota * 1.05)
                        if analisis["es_value_bet"]:
                            vb_count += 1
        logger.info(f"Value bets detectados: {vb_count}")
    except Exception as e:
        logger.error(f"Error detectando value bets: {e}")
