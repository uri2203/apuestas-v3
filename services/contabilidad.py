"""
Contabilidad Automática — depósitos, retiros, P&L por estrategia, reports.

Sin costo adicional: todo se calcula con datos existentes de DB.
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def registrar_transaccion(tipo, monto, categoria="general", estrategia="",
                           descripcion="", partido="", ref_id=None):
    """Registra una transacción contable y actualiza bankroll."""
    from database import db, _execute, get_bankroll_actual, registrar_bankroll

    br_actual = get_bankroll_actual()
    if tipo == "deposito":
        saldo = br_actual + monto
        registrar_bankroll(saldo, f"Depósito: {descripcion}")
    elif tipo == "retiro":
        saldo = max(0, br_actual - monto)
        registrar_bankroll(saldo, f"Retiro: {descripcion}")
    elif tipo == "bet_gain":
        saldo = br_actual + monto
        registrar_bankroll(saldo, f"Ganancia apuesta: {descripcion}")
    elif tipo == "bet_loss":
        saldo = br_actual - abs(monto)
        registrar_bankroll(saldo, f"Pérdida apuesta: {descripcion}")
    else:
        saldo = br_actual

    try:
        with db() as conn:
            _execute(conn,
                "INSERT INTO accounting_transactions "
                "(tipo, monto, saldo_resultante, categoria, estrategia, "
                "descripcion, partido, ref_id) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (tipo, monto, saldo, categoria, estrategia,
                 descripcion, partido, ref_id))
        return {"ok": True, "saldo": saldo}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def resumen_mensual(mes=None, año=None) -> dict:
    """Resumen contable del mes."""
    from database import db, _fetchall
    hoy = datetime.now()
    mes = mes or hoy.month
    año = año or hoy.year

    sql = """SELECT * FROM accounting_transactions
             WHERE strftime('%m', created_at) = ? AND strftime('%Y', created_at) = ?
             ORDER BY id ASC"""

    try:
        with db() as conn:
            rows = _fetchall(conn, sql, (f"{mes:02d}", str(año)))
    except Exception as e:
        return {"error": str(e)}

    ingresos = sum(t["monto"] for t in rows if t["monto"] > 0)
    egresos = sum(abs(t["monto"]) for t in rows if t["monto"] < 0)

    por_estrategia = {}
    for t in rows:
        est = t.get("estrategia", "general") or "general"
        if est not in por_estrategia:
            por_estrategia[est] = {"ingresos": 0, "egresos": 0, "total": 0, "n": 0}
        m = t["monto"]
        por_estrategia[est]["n"] += 1
        if m > 0:
            por_estrategia[est]["ingresos"] += m
        else:
            por_estrategia[est]["egresos"] += abs(m)
        por_estrategia[est]["total"] += m

    return {
        "mes": mes,
        "año": año,
        "ingresos": round(ingresos, 2),
        "egresos": round(egresos, 2),
        "balance": round(ingresos - egresos, 2),
        "total_transacciones": len(rows),
        "por_estrategia": {
            k: {
                "ingresos": round(v["ingresos"], 2),
                "egresos": round(v["egresos"], 2),
                "neto": round(v["total"], 2),
                "n_operaciones": v["n"],
            }
            for k, v in por_estrategia.items()
        },
    }


def pnl_por_estrategia(dias=30) -> list:
    """P&L desglosado por estrategia (value_bet, sharp, arbitraje, manual)."""
    from database import db, _fetchall, _USE_PG
    dc = "created_at::date" if _USE_PG else "date(created_at)"
    ago = "CURRENT_DATE - INTERVAL '1 day' * ?" if _USE_PG else "date('now', '-' || ? || ' days')"

    sql = f"""SELECT estrategia,
                    COUNT(*) as total,
                    SUM(CASE WHEN monto > 0 THEN 1 ELSE 0 END) as ganadas,
                    SUM(CASE WHEN monto < 0 THEN 1 ELSE 0 END) as perdidas,
                    SUM(monto) as neto
             FROM accounting_transactions
             WHERE {dc} >= {ago}
             AND tipo IN ('bet_gain', 'bet_loss')
             GROUP BY estrategia ORDER BY neto DESC"""

    try:
        with db() as conn:
            rows = _fetchall(conn, sql, (dias,))
        return rows or []
    except Exception:
        return []


def sync_bets_to_accounting() -> dict:
    """Sincroniza apuestas reales de la tabla bets a contabilidad."""
    from database import db, _fetchall, _execute

    try:
        with db() as conn:
            sin_sync = _fetchall(conn,
                "SELECT b.* FROM bets b "
                "LEFT JOIN accounting_transactions a ON a.ref_id=b.id AND a.tipo IN ('bet_gain','bet_loss') "
                "WHERE a.id IS NULL AND b.resultado != 'pendiente' AND b.ganancia_neta != 0")
    except Exception as e:
        return {"error": str(e), "sincronizados": 0}

    count = 0
    for b in sin_sync or []:
        gn = b.get("ganancia_neta", 0) or 0
        tipo = "bet_gain" if gn > 0 else "bet_loss"
        estrategia = "value_bet" if (b.get("edge_pct", 0) or 0) > 0 else "manual"
        registrar_transaccion(
            tipo=tipo, monto=gn,
            categoria="apuesta",
            estrategia=estrategia,
            descripcion=b.get("partido", ""),
            partido=b.get("partido", ""),
            ref_id=b["id"],
        )
        count += 1

    return {"sincronizados": count}
