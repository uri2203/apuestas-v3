"""Endpoints de gestión de cuentas y estrategia de camuflaje."""

import json
from flask import Blueprint, jsonify, request
from auth import login_required

accounts_bp = Blueprint("accounts", __name__, url_prefix="/api/cuentas")


@accounts_bp.route("/registrar", methods=["POST"])
@login_required
def registrar():
    from services.account_manager import registrar_cuenta
    d = request.get_json() or {}
    return jsonify(registrar_cuenta(
        d.get("casa_key", ""),
        float(d.get("limite_inicial", 1000)),
        float(d.get("balance", 0)),
        d.get("notas", ""),
    ))


@accounts_bp.route("/listar")
@login_required
def listar():
    from services.account_manager import listar_cuentas
    return jsonify(listar_cuentas())


@accounts_bp.route("/health/<casa_key>")
@login_required
def health(casa_key):
    from services.account_manager import calcular_health_score
    return jsonify(calcular_health_score(casa_key))


@accounts_bp.route("/limite", methods=["POST"])
@login_required
def actualizar_limite():
    from services.account_manager import actualizar_limite
    d = request.get_json() or {}
    return jsonify(actualizar_limite(
        d.get("casa_key", ""),
        float(d.get("nuevo_limite", 0)),
        d.get("razon", ""),
    ))


@accounts_bp.route("/apuesta", methods=["POST"])
@login_required
def registrar_apuesta():
    from services.account_manager import registrar_apuesta_en_cuenta
    d = request.get_json() or {}
    return jsonify(registrar_apuesta_en_cuenta(
        d.get("casa_key", ""),
        d.get("partido", ""),
        d.get("mercado", "1X2"),
        d.get("seleccion", ""),
        float(d.get("cuota", 2.0)),
        float(d.get("monto", 100)),
        d.get("tipo", "sharp"),
    ))


@accounts_bp.route("/catalogo")
def catalogo():
    from services.account_manager import CASAS_CATALOGO
    return jsonify(CASAS_CATALOGO)


@accounts_bp.route("/camuflaje/plan")
@login_required
def plan_camuflaje():
    from services.camouflage import plan_semanal_camuflaje
    from services.account_manager import listar_cuentas
    perfil   = request.args.get("perfil", "mixto")
    bankroll = float(request.args.get("bankroll", 5000))
    cuentas  = listar_cuentas()
    casas_activas = [c["casa_key"] for c in cuentas if c.get("activa")]
    return jsonify(plan_semanal_camuflaje(perfil, bankroll, [], casas_activas))


@accounts_bp.route("/camuflaje/generar")
@login_required
def generar_camuflaje():
    from services.camouflage import generar_apuestas_camuflaje
    from services.account_manager import listar_cuentas
    perfil    = request.args.get("perfil", "mixto")
    bankroll  = float(request.args.get("bankroll", 5000))
    n         = int(request.args.get("n", 3))
    cuentas   = listar_cuentas()
    casas     = [c["casa_key"] for c in cuentas if c.get("activa")] or ["bet365", "codere"]
    return jsonify(generar_apuestas_camuflaje(perfil, bankroll, n, casas))


@accounts_bp.route("/camuflaje/analizar")
@login_required
def analizar_comportamiento():
    from services.camouflage import analizar_comportamiento
    from database import db, _fetchall
    with db() as conn:
        bets = _fetchall(conn, "SELECT * FROM account_bets ORDER BY created_at DESC LIMIT 50")
    return jsonify(analizar_comportamiento(bets))


@accounts_bp.route("/perfiles")
def perfiles():
    from services.camouflage import PERFILES
    return jsonify(PERFILES)


@accounts_bp.route("/rotacion")
@login_required
def rotacion_optima():
    """Sugiere cómo distribuir una apuesta entre las casas activas."""
    from services.account_manager import listar_cuentas
    monto_total = float(request.args.get("monto", 1000))
    cuentas = [c for c in listar_cuentas() if c.get("activa")]
    if not cuentas:
        return jsonify({"error": "Sin cuentas activas registradas"})

    total_health = sum(c["health_score"] or 100 for c in cuentas) or 1
    distribucion = []
    for c in cuentas:
        h     = c["health_score"] or 100
        pct   = h / total_health
        monto = round(monto_total * pct, 2)
        lim   = c["limite_actual"] or 0
        monto = min(monto, lim * 0.15)  # nunca más del 15% del límite en una apuesta
        distribucion.append({
            "casa":         c["nombre"],
            "casa_key":     c["casa_key"],
            "health_score": h,
            "estado":       c["estado"],
            "monto":        round(monto, 2),
            "pct_del_total": round(pct * 100, 1),
            "limite_actual": lim,
        })

    return jsonify({
        "monto_total":   monto_total,
        "distribucion":  distribucion,
        "total_a_apostar": round(sum(d["monto"] for d in distribucion), 2),
        "nota": "Distribución proporcional al health score de cada cuenta",
    })
