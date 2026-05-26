"""
Endpoints REST del Bankroll Tracker.
"""

from flask import Blueprint, jsonify, request
from auth import login_required

bankroll_bp = Blueprint("bankroll", __name__, url_prefix="/api/bankroll")


@bankroll_bp.route("/registrar", methods=["POST"])
@login_required
def registrar():
    """Registra una nueva apuesta."""
    from services.bankroll import registrar_apuesta
    d = request.get_json() or {}
    required = ["partido", "seleccion", "cuota", "monto"]
    missing = [r for r in required if r not in d]
    if missing:
        return jsonify({"error": f"Campos requeridos: {missing}"}), 400

    resultado = registrar_apuesta(
        partido=d["partido"],
        seleccion=d["seleccion"],
        cuota=float(d["cuota"]),
        monto=float(d["monto"]),
        liga=d.get("liga", "Liga MX"),
        mercado=d.get("mercado", "1X2"),
        kelly_pct=d.get("kelly_pct"),
        edge_pct=d.get("edge_pct"),
        notas=d.get("notas", ""),
    )
    return jsonify(resultado)


@bankroll_bp.route("/resolver", methods=["POST"])
@login_required
def resolver():
    """Resuelve una apuesta (ganada/perdida/void)."""
    from services.bankroll import resolver_apuesta
    d = request.get_json() or {}
    bet_id    = d.get("id")
    resultado = d.get("resultado")
    if not bet_id or resultado not in ("ganada", "perdida", "void"):
        return jsonify({"error": "Requiere id y resultado (ganada|perdida|void)"}), 400
    return jsonify(resolver_apuesta(int(bet_id), resultado))


@bankroll_bp.route("/apuestas")
@login_required
def listar():
    """Lista apuestas con filtros opcionales."""
    from services.bankroll import listar_apuestas
    estado = request.args.get("estado")
    liga   = request.args.get("liga")
    limite = int(request.args.get("limite", 50))
    return jsonify(listar_apuestas(estado, liga, limite))


@bankroll_bp.route("/estadisticas")
@login_required
def estadisticas():
    """Métricas completas del bankroll."""
    from services.bankroll import estadisticas_bankroll
    return jsonify(estadisticas_bankroll())


@bankroll_bp.route("/inicializar", methods=["POST"])
@login_required
def inicializar():
    """Establece el bankroll inicial."""
    from database import registrar_bankroll, get_bankroll_actual
    d = request.get_json() or {}
    monto = float(d.get("monto", 0))
    if monto <= 0:
        return jsonify({"error": "monto debe ser mayor a 0"}), 400
    actual = get_bankroll_actual()
    if actual > 0:
        return jsonify({"error": f"Bankroll ya inicializado en ${actual}. Usa /resolver para modificarlo."}), 400
    registrar_bankroll(monto, "Bankroll inicial")
    return jsonify({"bankroll_inicial": monto, "mensaje": "Bankroll inicializado correctamente"})


@bankroll_bp.route("/curva-semanal")
@login_required
def curva_semanal():
    """Curva de bankroll agrupada por semana."""
    from services.bankroll import curva_bankroll_semanal
    return jsonify(curva_bankroll_semanal())
