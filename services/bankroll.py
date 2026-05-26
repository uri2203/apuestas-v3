"""Bankroll Tracker — compatible con PostgreSQL y SQLite."""

from datetime import datetime
import logging
from database import db, _fetchone, _fetchall, _execute, registrar_bankroll, get_bankroll_actual

logger = logging.getLogger(__name__)


def registrar_apuesta(partido, seleccion, cuota, monto, liga="Liga MX",
                      mercado="1X2", kelly_pct=None, edge_pct=None, notas="") -> dict:
    bankroll_antes = get_bankroll_actual()
    with db() as conn:
        bid = _execute(conn,
            "INSERT INTO bets (partido, liga, mercado, seleccion, cuota, monto, "
            "kelly_pct, edge_pct, bankroll_antes, notas) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (partido, liga, mercado, seleccion, cuota, monto, kelly_pct, edge_pct, bankroll_antes, notas))
    return {"id": bid, "status": "registrada", "bankroll_antes": bankroll_antes}


def resolver_apuesta(bet_id: int, resultado: str) -> dict:
    with db() as conn:
        bet = _fetchone(conn, "SELECT * FROM bets WHERE id=?", (bet_id,))
        if not bet:
            return {"error": f"Apuesta {bet_id} no encontrada"}
        if bet["resultado"] != "pendiente":
            return {"error": f"Apuesta {bet_id} ya resuelta: {bet['resultado']}"}
        bankroll = bet["bankroll_antes"] or get_bankroll_actual()
        if resultado == "ganada":
            ganancia = round(bet["monto"] * (bet["cuota"] - 1), 2)
        elif resultado == "perdida":
            ganancia = -round(bet["monto"], 2)
        else:
            ganancia = 0.0
        bankroll_despues = round(bankroll + ganancia, 2)
        _execute(conn,
            "UPDATE bets SET resultado=?, ganancia_neta=?, bankroll_despues=? WHERE id=?",
            (resultado, ganancia, bankroll_despues, bet_id))
    registrar_bankroll(bankroll_despues, f"Apuesta #{bet_id} {resultado}")
    return {"id": bet_id, "resultado": resultado,
            "ganancia_neta": ganancia, "bankroll_despues": bankroll_despues}


def listar_apuestas(estado=None, liga=None, limite=50) -> list:
    query = "SELECT * FROM bets WHERE 1=1"
    params = []
    if estado:
        query += " AND resultado=?"; params.append(estado)
    if liga:
        query += " AND liga=?"; params.append(liga)
    query += " ORDER BY id DESC LIMIT ?"; params.append(limite)
    with db() as conn:
        return _fetchall(conn, query, tuple(params))


def estadisticas_bankroll() -> dict:
    with db() as conn:
        bets    = _fetchall(conn, "SELECT * FROM bets")
        history = _fetchall(conn, "SELECT * FROM bankroll_history ORDER BY id")
    if not bets:
        return {"error": "Sin apuestas registradas aún"}
    resueltas  = [b for b in bets if b["resultado"] in ("ganada","perdida")]
    ganadas    = [b for b in resueltas if b["resultado"] == "ganada"]
    perdidas   = [b for b in resueltas if b["resultado"] == "perdida"]
    pendientes = [b for b in bets if b["resultado"] == "pendiente"]
    total_inv  = sum(b["monto"] for b in resueltas)
    profit     = sum(b["ganancia_neta"] or 0 for b in resueltas)
    roi        = round(profit / total_inv * 100, 2) if total_inv > 0 else 0
    win_rate   = round(len(ganadas) / len(resueltas) * 100, 1) if resueltas else 0
    clv_bets   = [b for b in resueltas if b.get("edge_pct")]
    clv_avg    = round(sum(b["edge_pct"] for b in clv_bets) / len(clv_bets), 2) if clv_bets else None
    racha = 0
    for b in reversed(resueltas):
        if b["resultado"] == "ganada":
            if racha >= 0: racha += 1
            else: break
        else:
            if racha <= 0: racha -= 1
            else: break
    bankroll_actual  = history[-1]["bankroll"] if history else 0
    bankroll_inicial = history[0]["bankroll"]  if history else 0
    crecimiento = round((bankroll_actual - bankroll_inicial) / bankroll_inicial * 100, 1) if bankroll_inicial else 0
    mercados = {}
    for b in resueltas:
        m = b.get("mercado","1X2")
        if m not in mercados: mercados[m] = {"total":0,"ganadas":0,"profit":0}
        mercados[m]["total"] += 1
        mercados[m]["profit"] += b["ganancia_neta"] or 0
        if b["resultado"] == "ganada": mercados[m]["ganadas"] += 1
    for m in mercados:
        t = mercados[m]["total"]
        mercados[m]["win_rate_pct"] = round(mercados[m]["ganadas"]/t*100,1) if t else 0
        mercados[m]["profit"] = round(mercados[m]["profit"],2)
    return {
        "bankroll": {"actual": round(bankroll_actual,2), "inicial": round(bankroll_inicial,2),
                     "crecimiento_pct": crecimiento,
                     "historia": [{"fecha": str(h["fecha"]), "bankroll": h["bankroll"]} for h in history[-50:]]},
        "apuestas": {"total": len(bets), "resueltas": len(resueltas), "ganadas": len(ganadas),
                     "perdidas": len(perdidas), "pendientes": len(pendientes), "win_rate_pct": win_rate},
        "rendimiento": {"total_invertido": round(total_inv,2), "profit_neto": round(profit,2),
                        "roi_pct": roi, "clv_promedio_pct": clv_avg, "racha_actual": racha,
                        "mejor_cuota_ganada": max((b["cuota"] for b in ganadas), default=None)},
        "por_mercado": mercados,
        "interpretacion": ("Excelente — ROI sostenible" if roi>8 else "Bueno" if roi>5 else "Regular" if roi>0 else "Negativo"),
    }


def curva_bankroll_semanal() -> list:
    with db() as conn:
        return _fetchall(conn,
            "SELECT DATE_TRUNC('week', fecha::timestamp) as semana, "
            "MAX(bankroll) as max, MIN(bankroll) as min "
            "FROM bankroll_history GROUP BY semana ORDER BY semana"
            if __import__('os').getenv('DATABASE_URL') else
            "SELECT strftime('%Y-W%W', fecha) as semana, MAX(bankroll) as max, MIN(bankroll) as min "
            "FROM bankroll_history GROUP BY semana ORDER BY semana")
