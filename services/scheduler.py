import threading
import time
import schedule
from services import api_football, scraper

def update_data_job():
    """
    Ejecuta la actualización masiva de silos de datos.
    Sincroniza el scraper web y la API de cuotas.
    """
    print("[SCHEDULER] Iniciando ciclo de actualización de datos...")
    try:
        # Refrescar caché de API Football
        api_football.refresh_cache()
        # Ejecutar recolección de datos mediante scraping
        scraper.run_web_scraper()
        print("[SCHEDULER] Ciclo completado exitosamente.")
    except Exception as e:
        print(f"[SCHEDULER] ERROR durante la ejecución: {str(e)}")

def start_background_tasks():
    """
    Inicia el motor de tareas programadas en un hilo persistente.
    Configurado para ejecutarse cada 5 minutos.
    """
    # Programar la tarea cada 5 minutos
    schedule.every(5).minutes.do(update_data_job)
    
    def run_loop():
        # Ejecución inicial al arrancar el sistema
        update_data_job()
        while True:
            schedule.run_pending()
            time.sleep(1)

    # Iniciar como hilo demonio para que cierre con la aplicación principal
    daemon_thread = threading.Thread(target=run_loop, daemon=True)
    daemon_thread.start()
    print("[SYSTEM] Tareas en segundo plano activadas.")
