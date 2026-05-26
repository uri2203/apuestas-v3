"""
Endpoints de mercados adicionales: Over/Under, BTTS, Handicap, Hedging, Arbitraje.
"""

import json
from flask import Blueprint, jsonify, request
from auth import login_required

mercados_bp = Blueprint("mercados", __name__, url_prefix="/api/mercados")


@mercados_bp.route("/partido")
@login_required
def mercados_partido():
    """Todos los mercados disponibles para un partido."""
    from services.mercados import calcular_mercados_completos
    from services.progol import HISTORIAL_DEMO
    home   = request.args.get("home", "Club América")
    away   = request.args.get("away", "Guadalajara")
    xg_h   = request.args.get("xg_home", type=float)
    xg_a   = request.args.get("xg_away", type=float)
    return jsonify(calcular_mercados_completos(home, away, HISTORIAL_DEMO, xg_h, xg_a))


@mercados_bp.route("/value-bets-mercados")
@login_required
def value_bets_mercados():
    """Value bets en mercados alternativos comparando modelo vs cuotas de casa."""
    from services.mercados import calcular_mercados_completos, detectar_value_bets_mercados
    from services.progol import HISTORIAL_DEMO
    home = request.args.get("home", "Club América")
    away = request.args.get("away", "Guadalajara")

    try:
        cuotas = json.loads(request.args.get("cuotas", "{}"))
    except Exception:
        cuotas = {}

    if not cuotas:
        cuotas = {"Over 2.5": 1.85, "Under 2.5": 2.00, "BTTS Si": 1.75}

    mercados = calcular_mercados_completos(home, away, HISTORIAL_DEMO)
    vbs = detectar_value_bets_mercados(mercados, cuotas)
    return jsonify({"partido": f"{home} vs {away}", "value_bets": vbs, "cuotas_analizadas": cuotas})


@mercados_bp.route("/hedge/garantizado")
@login_required
def hedge_garantizado():
    """Calcula hedge para garantizar ganancia."""
    from services.hedging import calcular_hedge_garantizado
    stake  = float(request.args.get("stake", 100))
    cuota  = float(request.args.get("cuota_original", 2.50))
    cuota_h = float(request.args.get("cuota_hedge", 2.10))
    return jsonify(calcular_hedge_garantizado(stake, cuota, cuota_h))


@mercados_bp.route("/hedge/parcial")
@login_required
def hedge_parcial():
    """Hedge parcial por porcentaje de cobertura."""
    from services.hedging import calcular_hedge_parcial, matriz_hedging
    stake   = float(request.args.get("stake", 100))
    cuota   = float(request.args.get("cuota_original", 2.50))
    cuota_h = float(request.args.get("cuota_hedge", 2.10))
    pct     = float(request.args.get("pct_cobertura", 50))
    return jsonify({
        **calcular_hedge_parcial(stake, cuota, cuota_h, pct),
        "matriz": matriz_hedging(stake, cuota, cuota_h),
    })


@mercados_bp.route("/arbitraje")
@login_required
def arbitraje():
    """Detecta y calcula arbitraje en un mercado."""
    from services.hedging import detectar_arbitraje
    bankroll = float(request.args.get("bankroll", 1000))
    try:
        cuotas = json.loads(request.args.get("cuotas", '{"1":2.10,"X":3.20,"2":3.80}'))
    except Exception:
        cuotas = {"1": 2.10, "X": 3.20, "2": 3.80}
    return jsonify(detectar_arbitraje(cuotas, bankroll))


@mercados_bp.route("/dutching")
@login_required
def dutching():
    """Calcula distribución Dutching entre múltiples selecciones."""
    from services.hedging import calcular_dutching
    bankroll = float(request.args.get("bankroll", 1000))
    try:
        sels = json.loads(request.args.get("selecciones",
               '[{"nombre":"Chivas","cuota":2.10},{"nombre":"Empate","cuota":3.20}]'))
    except Exception:
        sels = [{"nombre": "Local", "cuota": 2.10}, {"nombre": "Empate", "cuota": 3.20}]
    return jsonify(calcular_dutching(sels, bankroll))
