"""
Router para Melate y loterías mexicanas.
Endpoints: resultados, frecuencias, probabilidades, generador.
"""
from fastapi import APIRouter, Query, HTTPException
from services.scraper import obtener_ultimo_melate, obtener_historico_melate
from services.estadisticas import (
    calcular_frecuencias,
    numeros_calientes,
    numeros_frios,
    calcular_rachas,
    probabilidades_melate,
    generar_combinacion,
)
import asyncio

router = APIRouter()

# Cache simple en memoria (en producción usar Redis)
_cache = {}


@router.get("/ultimo-resultado")
async def ultimo_resultado():
    """Obtiene el resultado más reciente de Melate."""
    resultado = await obtener_ultimo_melate()
    if not resultado:
        raise HTTPException(status_code=503, detail="No se pudo obtener el resultado. Reintenta.")
    return resultado


@router.get("/historico")
async def historico(limite: int = Query(default=500, le=5000)):
    """Historial de resultados de Melate."""
    if "historico" not in _cache:
        _cache["historico"] = await obtener_historico_melate(limite)
    return {
        "total": len(_cache["historico"]),
        "resultados": _cache["historico"][-limite:],
    }


@router.get("/frecuencias")
async def frecuencias(limite: int = Query(default=500, le=5000)):
    """Frecuencia de aparición de cada número."""
    data = await obtener_historico_melate(limite)
    if not data:
        raise HTTPException(status_code=503, detail="Sin datos históricos disponibles.")
    freq = calcular_frecuencias(data)
    return {
        "sorteos_analizados": len(data),
        "frecuencias": freq,
        "calientes": numeros_calientes(freq, top=10),
        "frios": numeros_frios(freq, top=10),
    }


@router.get("/racha/{numero}")
async def racha_numero(numero: int):
    """Analiza la racha de un número específico."""
    if not 1 <= numero <= 56:
        raise HTTPException(status_code=400, detail="Número debe estar entre 1 y 56")
    data = await obtener_historico_melate(500)
    return calcular_rachas(data, numero)


@router.get("/probabilidades")
async def probabilidades():
    """Probabilidades exactas de cada premio en Melate."""
    return probabilidades_melate()


@router.get("/generar")
async def generar(
    modo: str = Query(default="balanceado", enum=["caliente", "frio", "balanceado", "aleatorio"]),
    cantidad: int = Query(default=1, le=20),
):
    """Genera combinaciones basadas en análisis estadístico."""
    data = await obtener_historico_melate(500)
    freq = calcular_frecuencias(data) if data else {}

    combinaciones = [
        {
            "combinacion": idx + 1,
            "numeros": generar_combinacion(freq, modo=modo),
            "modo": modo,
        }
        for idx in range(cantidad)
    ]
    return {
        "modo": modo,
        "cantidad": cantidad,
        "combinaciones": combinaciones,
        "nota": "Generadas con análisis estadístico. La lotería es aleatoria — juega responsablemente.",
    }


@router.get("/estadisticas-generales")
async def estadisticas_generales():
    """Resumen estadístico completo de Melate."""
    data = await obtener_historico_melate(500)
    if not data:
        raise HTTPException(status_code=503, detail="Sin datos")

    freq = calcular_frecuencias(data)
    calientes = numeros_calientes(freq, 5)
    frios = numeros_frios(freq, 5)

    # Par/impar, altos/bajos
    numeros_todos = [n for r in data for n in r.get("numeros", [])]
    pares = sum(1 for n in numeros_todos if n % 2 == 0)
    impares = len(numeros_todos) - pares
    altos = sum(1 for n in numeros_todos if n > 28)
    bajos = len(numeros_todos) - altos

    return {
        "sorteos_analizados": len(data),
        "top_5_calientes": calientes,
        "top_5_frios": frios,
        "distribucion": {
            "pct_pares": round(pares / len(numeros_todos) * 100, 1),
            "pct_impares": round(impares / len(numeros_todos) * 100, 1),
            "pct_altos_29_56": round(altos / len(numeros_todos) * 100, 1),
            "pct_bajos_1_28": round(bajos / len(numeros_todos) * 100, 1),
        },
        "probabilidades": probabilidades_melate(),
    }
