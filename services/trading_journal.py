"""
Trading Journal Automático — cada acción del sistema se guarda con
snapshot del mercado. Exportable a CSV.

Acciones registradas:
  - value_bet_detected
  - arbitrage_detected
  - sharp_alert
  - cross_market_alert
  - apuesta_real
  - trade_simulado
  - prediccion_ml
"""
import logging
import csv
import io
from datetime import datetime

logger = logging.getLogger(__name__)


def log_entry(tipo_accion, partido="", liga="", mercado="", seleccion="",
              cuota=0, monto=0, edge_pct=0, score_sharp=0, overround=0,
              casa="", estrategia="", resultado="", pnl=0, snapshot=None):
    """Registra una entrada en el trading journal."""
    from database import db, _execute
    import json

    snap_str = json.dumps(snapshot) if snapshot else ""

    try:
        with db() as conn:
            _execute(conn,
                "INSERT INTO trading_journal "
                "(tipo_accion, partido, liga, mercado, seleccion, "
                "cuota, monto, edge_pct, score_sharp, overround, "
                "casa, estrategia, resultado, pnl, snapshot) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (tipo_accion, partido, liga, mercado, seleccion,
                 cuota, monto, edge_pct, score_sharp, overround,
                 casa, estrategia, resultado, pnl, snap_str))
    except Exception as e:
        logger.error("Journal log error: %s", e)


def auto_log_from_recent() -> dict:
    """Auto-registra acciones recientes del sistema en el journal."""
    from database import db, _fetchall

    registrados = 0

    # Value bets recientes no registrados
    try:
        with db() as conn:
            vbs = _fetchall(conn,
                "SELECT v.* FROM value_bets_log v "
                "LEFT JOIN trading_journal j ON j.ref_id=v.id AND j.tipo_accion='value_bet_detected' "
                "WHERE j.id IS NULL ORDER BY v.id DESC LIMIT 20")
        for vb in vbs or []:
            log_entry(
                "value_bet_detected",
                partido=vb.get("partido", ""),
                liga=vb.get("liga", ""),
                seleccion=vb.get("resultado", ""),
                cuota=vb.get("cuota", 0) or 0,
                edge_pct=vb.get("edge_pct", 0) or 0,
                casa=vb.get("casa", ""),
                estrategia="value_bet",
                snapshot={"fuente": "odds_api", "edge": vb.get("edge_pct", 0)},
            )
            registrados += 1
    except Exception:
        pass

    # Alertas sharp recientes
    try:
        with db() as conn:
            sharps = _fetchall(conn,
                "SELECT a.* FROM alerts_log a "
                "LEFT JOIN trading_journal j ON j.tipo_accion='sharp_alert' AND j.partido=a.partido "
                "WHERE j.id IS NULL AND a.tipo='SHARP' ORDER BY a.id DESC LIMIT 10")
        for s in sharps or []:
            log_entry(
                "sharp_alert",
                partido=s.get("partido", ""),
                liga=s.get("liga", ""),
                estrategia="sharp",
                snapshot={"alerta": s.get("detalle", "")},
            )
            registrados += 1
    except Exception:
        pass

    # Apuestas reales recientes no registradas
    try:
        with db() as conn:
            bets = _fetchall(conn,
                "SELECT b.* FROM bets b "
                "LEFT JOIN trading_journal j ON j.ref_id=b.id AND j.tipo_accion='apuesta_real' "
                "WHERE j.id IS NULL ORDER BY b.id DESC LIMIT 20")
        for b in bets or []:
            log_entry(
                "apuesta_real",
                partido=b.get("partido", ""),
                liga=b.get("liga", ""),
                seleccion=b.get("seleccion", ""),
                cuota=b.get("cuota", 0) or 0,
                monto=b.get("monto", 0) or 0,
                edge_pct=b.get("edge_pct", 0) or 0,
                resultado=b.get("resultado", "pendiente"),
                pnl=b.get("ganancia_neta", 0) or 0,
                estrategia="value_bet",
                snapshot={"kelly_pct": b.get("kelly_pct", 0)},
            )
            registrados += 1
    except Exception:
        pass

    return {"registrados": registrados}


def export_csv(dias=7) -> str:
    """Exporta el journal a CSV."""
    from database import db, _fetchall, _USE_PG
    dc = "created_at::date" if _USE_PG else "date(created_at)"
    ago = "CURRENT_DATE - INTERVAL '1 day' * ?" if _USE_PG else "date('now', '-' || ? || ' days')"

    try:
        with db() as conn:
            rows = _fetchall(conn,
                f"SELECT * FROM trading_journal "
                f"WHERE {dc} >= {ago} "
                f"ORDER BY id DESC", (dias,))
    except Exception as e:
        return f"Error: {e}"

    if not rows:
        return "Sin entradas en el período"

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "fecha", "tipo_accion", "partido", "liga", "mercado",
                     "seleccion", "cuota", "monto", "edge_pct", "score_sharp",
                     "overround", "casa", "estrategia", "resultado", "pnl"])

    for r in rows:
        writer.writerow([
            r.get("id", ""),
            r.get("created_at", ""),
            r.get("tipo_accion", ""),
            r.get("partido", ""),
            r.get("liga", ""),
            r.get("mercado", ""),
            r.get("seleccion", ""),
            r.get("cuota", 0),
            r.get("monto", 0),
            r.get("edge_pct", 0),
            r.get("score_sharp", 0),
            r.get("overround", 0),
            r.get("casa", ""),
            r.get("estrategia", ""),
            r.get("resultado", ""),
            r.get("pnl", 0),
        ])

    return output.getvalue()


def resumen_journal(dias=7) -> dict:
    """Resumen de actividad del journal."""
    from database import db, _fetchall, _USE_PG
    dc = "created_at::date" if _USE_PG else "date(created_at)"
    ago_p = "CURRENT_DATE - INTERVAL '1 day' * ?" if _USE_PG else "date('now', '-' || ? || ' days')"
    ago_1 = "CURRENT_DATE - INTERVAL '1 day'" if _USE_PG else "date('now', '-' || 1 || ' days')"

    try:
        with db() as conn:
            total = _fetchall(conn,
                f"SELECT tipo_accion, COUNT(*) as n FROM trading_journal "
                f"WHERE {dc} >= {ago_p} "
                f"GROUP BY tipo_accion ORDER BY n DESC", (dias,))

            recientes = _fetchall(conn,
                f"SELECT * FROM trading_journal "
                f"WHERE {dc} >= {ago_1} "
                f"ORDER BY id DESC LIMIT 10")
    except Exception as e:
        return {"error": str(e)}

    return {
        "dias": dias,
        "total_acciones": sum(r.get("n", 0) for r in (total or [])),
        "por_tipo": {r.get("tipo_accion", "?"): r.get("n", 0) for r in (total or [])},
        "ultimas_acciones": [
            {
                "tipo": r.get("tipo_accion", ""),
                "partido": r.get("partido", ""),
                "estrategia": r.get("estrategia", ""),
                "resultado": r.get("resultado", ""),
                "pnl": r.get("pnl", 0),
                "fecha": r.get("created_at", ""),
            }
            for r in (recientes or [])
        ],
    }
