import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import logging

# Importación de Silos Internos
from routers import avanzado, kelly, odds, melate
from services import motor_avanzado, scheduler

# Configuración de Logs Estricta
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CorporateTech-Backend")

app = FastAPI(
    title="PRO-BET V3 API",
    description="Motor de Ingeniería para Predicciones de Alto Impacto",
    version="3.0.0"
)

# REGLA CORPORATE TECH: Habilitar CORS para comunicación con Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REGISTRO DE RUTAS (Routers)
app.include_router(avanzado.router, prefix="/api/v1/avanzado", tags=["Predicciones"])
app.include_router(kelly.router, prefix="/api/v1/kelly", tags=["Gestión de Riesgo"])
app.include_router(odds.router, prefix="/api/v1/odds", tags=["Cuotas"])
app.include_router(melate.router, prefix="/api/v1/melate", tags=["Lotería"])

@app.on_event("startup")
async def startup_event():
    """
    Inicia los servicios en segundo plano al arrancar el servidor.
    Garantiza que los datos estén frescos para el Dashboard.
    """
    logger.info("Iniciando Scheduler de Scrapers y API Football...")
    scheduler.start_background_tasks()

@app.get("/")
async def root():
    return {
        "status": "online",
        "system": "PRO-BET V3",
        "engine": "Corporate Tech Modular"
    }

# --- ENDPOINT DE AGREGACIÓN PARA DASHBOARD (TIEMPO REAL) ---

@app.get("/api/v1/dashboard/full-stream", tags=["Dashboard"])
async def get_dashboard_data():
    """
    Endpoint Maestro: Agrega datos de múltiples silos en un solo stream.
    Resuelve el problema de falta de datos en el dashboard.
    """
    try:
        # 1. Obtener predicciones base (Elo + Dixon Coles)
        predicciones = motor_avanzado.obtener_todas_las_predicciones()
        
        if not predicciones:
            logger.warning("No se encontraron predicciones en el motor.")
            return []

        # 2. El motor_avanzado ya debe devolver el objeto enriquecido.
        # Si el motor solo da datos base, aquí se asegura la integridad:
        dashboard_payload = []
        for p in predicciones:
            # Asegurar presencia de todos los campos que el Dashboard requiere
            entry = {
                "hora": p.get("hora", "N/A"),
                "liga": p.get("liga", "Unknown"),
                "local": p.get("local", "N/A"),
                "visitante": p.get("visitante", "N/A"),
                "cuota_local": p.get("cuota_local", 0.0),
                "cuota_empate": p.get("cuota_empate", 0.0),
                "cuota_visitante": p.get("cuota_visitante", 0.0),
                "prob_elo": p.get("prob_elo", 0.0),
                "prob_dixon": p.get("prob_dixon", 0.0),
                "prob_ensemble": p.get("prob_ensemble", 0.0),
                "kelly_fraction": p.get("kelly_fraction", 0.0),
                "ev": p.get("ev", 0.0)
            }
            dashboard_payload.append(entry)

        return dashboard_payload

    except Exception as e:
        logger.error(f"Error en Agregación de Dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Error interno del motor de datos")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": uvicorn.main.time.time()}

if __name__ == "__main__":
    # Configuración de puerto para despliegue en Render
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
