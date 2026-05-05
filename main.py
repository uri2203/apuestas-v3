import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import avanzado, kelly, odds, melate
from services import scheduler, motor_avanzado

app = FastAPI(title="PRO-BET V3 - Engine")

# Configuración de CORS para el Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de Routers
app.include_router(avanzado.router, prefix="/avanzado")
app.include_router(kelly.router, prefix="/kelly")
app.include_router(odds.router, prefix="/odds")
app.include_router(melate.router, prefix="/melate")

@app.on_event("startup")
async def startup_event():
    # Inicia el motor de actualización de datos
    scheduler.start_background_tasks()

@app.get("/api/v1/dashboard/full-stream")
async def full_stream():
    # Retorna el consolidado de predicciones para el dashboard
    return motor_avanzado.obtener_todas_las_predicciones()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
