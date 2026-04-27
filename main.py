"""
ApuestasPro v3 — UN SOLO SERVICIO
FastAPI sirve el dashboard HTML + la API en el mismo puerto.
Deploy: render.yaml → 1 web service → listo.
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from routers import melate, odds, kelly, avanzado
from services.scheduler import iniciar_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    s = iniciar_scheduler()
    s.start()
    yield
    s.shutdown()

app = FastAPI(title="ApuestasPro API", version="3.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── API ROUTERS ────────────────────────────────────────────────────────────
app.include_router(melate.router,   prefix="/api/melate",   tags=["Melate"])
app.include_router(odds.router,     prefix="/api/odds",     tags=["Odds"])
app.include_router(kelly.router,    prefix="/api/kelly",    tags=["Kelly"])
app.include_router(avanzado.router, prefix="/api/pro",      tags=["Pro"])

# ── DASHBOARD (raíz) ──────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def dashboard():
    from dashboard import HTML
    return HTMLResponse(content=HTML)

@app.get("/health")
async def health():
    return {"status": "ok", "version": "3.0.0"}
