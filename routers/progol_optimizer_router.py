"""Endpoints del Optimizador de Progol."""

from flask import Blueprint, jsonify, request
from auth import login_required

progol_opt_bp = Blueprint("progol_opt", __name__, url_prefix="/api/progol/optimizar")


@progol_opt_bp.route("/analizar")
@login_required
def analizar():
    """Análisis completo de la jornada con clasificación de partidos."""
    from services.optimizador_progol import analizar_jornada_progol
    from services.progol import generar_jornada_progol
    import os
    api_key = os.getenv("API_FOOTBALL_KEY", "")
    jornada = generar_jornada_progol(api_key)
    partidos = jornada.get("partidos", [])
    if not partidos:
        return jsonify({"error": "Sin partidos disponibles"}), 400
    return jsonify(analizar_jornada_progol(partidos))


@progol_opt_bp.route("/quiniela-simple")
@login_required
def quiniela_simple():
    """Una quiniela con el signo más probable de cada partido."""
    from services.optimizador_progol import quiniela_simple as _qs
    from services.progol import generar_jornada_progol
    import os
    jornada  = generar_jornada_progol(os.getenv("API_FOOTBALL_KEY", ""))
    partidos = jornada.get("partidos", [])
    return jsonify(_qs(partidos))


@progol_opt_bp.route("/diversificada")
@login_required
def diversificada():
    """N quinielas diversificadas variando signos en partidos disputados."""
    from services.optimizador_progol import quinielas_diversificadas
    from services.progol import generar_jornada_progol
    import os
    n        = int(request.args.get("n", 10))
    jornada  = generar_jornada_progol(os.getenv("API_FOOTBALL_KEY", ""))
    partidos = jornada.get("partidos", [])
    return jsonify({"quinielas": quinielas_diversificadas(partidos, n)})


@progol_opt_bp.route("/maxima-cobertura")
@login_required
def maxima_cobertura():
    """Conjunto de N quinielas que maximiza la probabilidad de acertar 11+."""
    from services.optimizador_progol import optimizar_cobertura
    from services.progol import generar_jornada_progol
    import os
    n        = int(request.args.get("n", 5))
    umbral   = int(request.args.get("umbral", 11))
    jornada  = generar_jornada_progol(os.getenv("API_FOOTBALL_KEY", ""))
    partidos = jornada.get("partidos", [])
    return jsonify(optimizar_cobertura(partidos, n, umbral))
