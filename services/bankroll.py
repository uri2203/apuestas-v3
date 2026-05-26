"""
Bankroll Tracker — lógica de negocio.

Registra apuestas, calcula ROI real, genera estadísticas
y la curva del bankroll en el tiempo.
"""

from datetime import datetime, timedelta
import logging
from database import db, rows_to_list, registrar_bankroll, get_bankroll_actual

logger = logging.getLogger(__name__)


# ── CRUD de apuestas ──────────────────────────────────────────────────────────

def registrar_apuesta(
    partido: str,
    seleccion: str,
    cuota: float,
    monto: float,
    liga: str = "Liga MX",
    mercado: str = "1X2",
    kelly_pct: float = None,
    edge_pct: float = None,
    notas: str = "",
) -> dict:
    """Registra una nueva apuesta como 'pendiente'."""
    bankroll_antes = get_bankroll_actual()
    with db() as conn:
        cur = conn.execute(
            """INSERT INTO bets
               (partido, liga, mercado, seleccion, cuota, monto,
                kelly_pct, edge_pct, bankroll_antes, notas)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (partido, liga, mercado, seleccion, cuota, monto,
             kelly_pct, edge_pct, bankroll_antes, notas),
        )
        bet_id = cur.lastrowid

    return {"id": bet_id, "status": "registrada", "bankroll_antes": bankroll_antes}


def resolver_apuesta(bet_id: int, resultado: str) -> dict:
    """
    Marca una apuesta como ganada, perdida o void.
    Actualiza el bankroll automáticamente.
    resultado: 'ganada' | 'perdida' | 'void'
    """
    with db() as conn:
        bet = conn.execute("SELECT * FROM bets WHERE id=?", (bet_id,)).fetchone()
        if not bet:
            return {"error": f"Apuesta {bet_id} no encontrada"}
        if bet["resultado"] != "pendiente":
            return {"error": f"Apuesta {bet_id} ya resuelta: {bet['resultado']}"}

        bankroll = bet["bankroll_antes"] or get_bankroll_actual()

        if resultado == "ganada":
            ganancia = round(bet["monto"] * (bet["cuota"] - 1), 2)
        elif resultado == "perdida":
            ganancia = -round(bet["monto"], 2)
        else:  # void
            ganancia = 0.0

        bankroll_despues = round(bankroll + ganancia, 2)

        conn.execute(
            """UPDATE bets SET resultado=?, ganancia_neta=?, bankroll_despues=?
               WHERE id=?""",
            (resultado, ganancia, bankroll_despues, bet_id),
        )

    registrar_bankroll(bankroll_despues, f"Apuesta #{bet_id} {resultado}")
    return {
        "id": bet_id,
        "resultado": resultado,
        "ganancia_neta": ganancia,
        "bankroll_despues": bankroll_despues,
    }


def listar_apuestas(
    estado: str = None,
    liga: str = None,
    limite: int = 50,
) -> list:
    query = "SELECT * FROM bets WHERE 1=1"
    params = []
    if estado:
        query += " AND resultado=?"
        params.append(estado)
    if liga:
        query += " AND liga=?"
        params.append(liga)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limite)

    with db() as conn:
        return rows_to_list(conn.execute(query, params).fetchall())


# ── Estadísticas ──────────────────────────────────────────────────────────────

def estadisticas_bankroll() -> dict:
    """Métricas completas del bankroll y rendimiento de apuestas."""
    with db() as conn:
        bets = rows_to_list(conn.execute("SELECT * FROM bets").fetchall())
        history = rows_to_list(
            conn.execute("SELECT * FROM bankroll_history ORDER BY id").fetchall()
        )

    if not bets:
        return {"error": "Sin apuestas registradas aún"}

    resueltas  = [b for b in bets if b["resultado"] in ("ganada", "perdida")]
    ganadas    = [b for b in resueltas if b["resultado"] == "ganada"]
    perdidas   = [b for b in resueltas if b["resultado"] == "perdida"]
    pendientes = [b for b in bets if b["resultado"] == "pendiente"]

    total_invertido = sum(b["monto"] for b in resueltas)
    profit_neto     = sum(b["ganancia_neta"] or 0 for b in resueltas)
    roi             = round(profit_neto / total_invertido * 100, 2) if total_invertido > 0 else 0

    win_rate = round(len(ganadas) / len(resueltas) * 100, 1) if resueltas else 0

    # CLV promedio
    clv_bets = [b for b in resueltas if b.get("edge_pct")]
    clv_avg  = round(sum(b["edge_pct"] for b in clv_bets) / len(clv_bets), 2) if clv_bets else None

    # Racha actual
    racha_actual = 0
    for b in reversed(resueltas):
        if b["resultado"] == "ganada":
            if racha_actual >= 0:
                racha_actual += 1
            else:
                break
        else:
            if racha_actual <= 0:
                racha_actual -= 1
            else:
                break

    # Mejor y peor cuota
    cuotas_ganadas = [b["cuota"] for b in ganadas]
    mejor_cuota = max(cuotas_ganadas) if cuotas_ganadas else None

    bankroll_actual = history[-1]["bankroll"] if history else 0
    bankroll_inicial = history[0]["bankroll"] if history else 0
    crecimiento = round((bankroll_actual - bankroll_inicial) / bankroll_inicial * 100, 1) if bankroll_inicial else 0

    # Por mercado
    mercados = {}
    for b in resueltas:
        m = b.get("mercado", "1X2")
        if m not in mercados:
            mercados[m] = {"total": 0, "ganadas": 0, "profit": 0}
        mercados[m]["total"] += 1
        mercados[m]["profit"] += b["ganancia_neta"] or 0
        if b["resultado"] == "ganada":
            mercados[m]["ganadas"] += 1
    for m in mercados:
        t = mercados[m]["total"]
        mercados[m]["win_rate_pct"] = round(mercados[m]["ganadas"] / t * 100, 1) if t else 0
        mercados[m]["profit"] = round(mercados[m]["profit"], 2)

    return {
        "bankroll": {
            "actual":    round(bankroll_actual, 2),
            "inicial":   round(bankroll_inicial, 2),
            "crecimiento_pct": crecimiento,
            "historia":  [{"fecha": h["fecha"], "bankroll": h["bankroll"]} for h in history[-50:]],
        },
        "apuestas": {
            "total":      len(bets),
            "resueltas":  len(resueltas),
            "ganadas":    len(ganadas),
            "perdidas":   len(perdidas),
            "pendientes": len(pendientes),
            "win_rate_pct": win_rate,
        },
        "rendimiento": {
            "total_invertido":   round(total_invertido, 2),
            "profit_neto":       round(profit_neto, 2),
            "roi_pct":           roi,
            "clv_promedio_pct":  clv_avg,
            "racha_actual":      racha_actual,
            "mejor_cuota_ganada": mejor_cuota,
        },
        "por_mercado": mercados,
        "interpretacion": (
            "Excelente — ROI sostenible a largo plazo" if roi > 8 else
            "Bueno — por encima del benchmark profesional (5%)" if roi > 5 else
            "Regular — dentro del rango esperado" if roi > 0 else
            "Negativo — revisar criterios de selección"
        ),
    }


def curva_bankroll_semanal() -> list:
    """Bankroll agrupado por semana para gráficas."""
    with db() as conn:
        rows = conn.execute("""
            SELECT strftime('%Y-W%W', fecha) as semana,
                   MAX(bankroll) as bankroll_max,
                   MIN(bankroll) as bankroll_min,
                   (SELECT bankroll FROM bankroll_history b2
                    WHERE strftime('%Y-W%W', b2.fecha) = strftime('%Y-W%W', bh.fecha)
                    ORDER BY b2.id DESC LIMIT 1) as bankroll_cierre
            FROM bankroll_history bh
            GROUP BY semana
            ORDER BY semana
        """).fetchall()
    return rows_to_list(rows)
