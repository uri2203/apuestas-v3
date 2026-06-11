"""
Modo Simulación en Vivo — cada value bet detectado se registra como
trade simulado con stake sugerido (Kelly). Dashboard muestra
"hoy habrías ganado/perdido $X" en tiempo real.

Flujo:
  1. Leer value_bets_log sin simular
  2. Asignar stake Kelly sobre bankroll actual
  3. Marcar como trade simulado
  4. Cuando el partido termina (vía ESPN), verificar resultado
  5. Calcular P&L simulado acumulado
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def registrar_trade_simulado(
    partido: str, liga: str, seleccion: str,
    casa: str, cuota: float, edge_pct: float,
    fecha_partido: str = "",
) -> dict:
    """
    Registra un trade simulado en la DB.
    Calcula stake usando Kelly completo sobre bankroll actual.
    """
    from database import db, _execute, get_bankroll_actual

    bankroll = get_bankroll_actual()
    if bankroll <= 0:
        bankroll = 10000  # bankroll por defecto para simulación

    prob = 1.0 / cuota
    b = cuota - 1
    q = 1 - prob
    kelly = (b * prob - q) / b if b > 0 else 0
    kelly = max(0, min(kelly, 0.05))  # cap al 5%
    stake = round(bankroll * kelly, 2)

    if stake < 1:
        return {"simulado": False, "razon": "Stake muy bajo (< $1)"}

    try:
        with db() as conn:
            _execute(conn,
                "INSERT INTO simulated_trades "
                "(partido, liga, seleccion, casa, cuota, edge_pct, "
                "stake_simulado, bankroll_al_momento, resultado_simulado, fecha_partido) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (partido, liga, seleccion, casa, cuota, edge_pct,
                 stake, bankroll, "pendiente", fecha_partido))
        return {
            "simulado": True,
            "partido": partido,
            "seleccion": seleccion,
            "cuota": cuota,
            "stake": stake,
            "bankroll": bankroll,
            "retorno_potencial": round(stake * cuota, 2),
        }
    except Exception as e:
        logger.error("Error registrando trade simulado: %s", e)
        return {"simulado": False, "error": str(e)}


def verificar_trades_pendientes() -> dict:
    """
    Verifica trades simulados pendientes contra resultados reales ESPN.
    """
    from database import db, _fetchall, _execute
    from services.espn_scraper import get_resultados

    try:
        with db() as conn:
            pendientes = _fetchall(conn,
                "SELECT * FROM simulated_trades WHERE resultado_simulado='pendiente' "
                "ORDER BY id DESC LIMIT 200")
    except Exception as e:
        return {"error": str(e), "verificados": 0}

    if not pendientes:
        return {"verificados": 0, "mensaje": "Sin trades pendientes"}

    # Agrupar por liga para fetch eficiente
    ligas = set(p.get("liga", "liga_mx") for p in pendientes)
    resultados_por_liga = {}
    for liga in ligas:
        try:
            resultados_por_liga[liga] = get_resultados(liga, 14)
        except Exception:
            resultados_por_liga[liga] = []

    ganancia_total = 0
    verificados = 0
    for t in pendientes:
        partido = t.get("partido", "")
        seleccion = t.get("seleccion", "")
        cuota = t.get("cuota", 0) or 1
        stake = t.get("stake_simulado", 0) or 0
        fecha = t.get("fecha_partido", "")[:10]
        liga = t.get("liga", "liga_mx")

        # Parsear partido para buscar en ESPN
        home_away = partido.split(" vs ")
        if len(home_away) != 2:
            continue
        home, away = home_away[0].strip(), home_away[1].strip()

        for r in resultados_por_liga.get(liga, []):
            if (r.get("home", "") == home and r.get("away", "") == away
                    and r.get("fecha", "")[:10] == fecha):
                gh = r.get("home_goals")
                ga = r.get("away_goals")
                if gh is None or ga is None:
                    continue
                real = "1" if gh > ga else "X" if gh == ga else "2"
                ganada = seleccion.lower() == real.lower()
                pnl = round(stake * (cuota - 1), 2) if ganada else round(-stake, 2)
                resultado_str = "ganada" if ganada else "perdida"

                try:
                    with db() as conn:
                        _execute(conn,
                            "UPDATE simulated_trades SET resultado_simulado=?, pnl_real=?, "
                            "resultado_real_partido=?, verificado_at=? WHERE id=?",
                            (resultado_str, pnl, real, datetime.now().isoformat(), t["id"]))
                except Exception:
                    pass

                ganancia_total += pnl
                verificados += 1
                break

    return {
        "verificados": verificados,
        "total_pendientes": len(pendientes),
        "ganancia_neta_simulada": round(ganancia_total, 2),
    }


def resumen_simulacion(dias: int = 1) -> dict:
    """
    Resumen de rendimiento de la simulación.
    """
    from database import db, _fetchall, _USE_PG
    dc = "created_at::date" if _USE_PG else "date(created_at)"
    ago = "CURRENT_DATE - INTERVAL '1 day' * ?" if _USE_PG else "date('now', '-' || ? || ' days')"

    try:
        with db() as conn:
            # Trades del período
            trades = _fetchall(conn,
                f"SELECT * FROM simulated_trades "
                f"WHERE {dc} >= {ago} "
                f"ORDER BY id DESC", (dias,))

            stats = _fetchone(conn,
                f"SELECT "
                f"COUNT(*) as total, "
                f"SUM(CASE WHEN resultado_simulado='ganada' THEN 1 ELSE 0 END) as ganadas, "
                f"SUM(CASE WHEN resultado_simulado='perdida' THEN 1 ELSE 0 END) as perdidas, "
                f"SUM(CASE WHEN resultado_simulado='pendiente' THEN 1 ELSE 0 END) as pendientes, "
                f"COALESCE(SUM(pnl_real), 0) as pnl_total "
                f"FROM simulated_trades "
                f"WHERE {dc} >= {ago}",
                (dias,))
    except Exception as e:
        return {"error": str(e)}

    if not stats or stats.get("total", 0) == 0:
        return {"total": 0, "mensaje": "Sin trades simulados en el período"}

    total = stats.get("total", 0) or 0
    ganadas = stats.get("ganadas", 0) or 0
    perdidas = stats.get("perdidas", 0) or 0
    pendientes = stats.get("pendientes", 0) or 0
    pnl = stats.get("pnl_total", 0) or 0

    resueltas = ganadas + perdidas
    win_rate = round(ganadas / resueltas * 100, 1) if resueltas > 0 else 0

    # Últimos 5 trades
    ultimos = [
        {
            "partido": t.get("partido", ""),
            "seleccion": t.get("seleccion", ""),
            "cuota": t.get("cuota", 0),
            "stake": t.get("stake_simulado", 0),
            "resultado": t.get("resultado_simulado", ""),
            "pnl": t.get("pnl_real", 0),
        }
        for t in (trades or [])[:5]
    ]

    return {
        "dias": dias,
        "total_trades": total,
        "ganadas": ganadas,
        "perdidas": perdidas,
        "pendientes": pendientes,
        "win_rate_pct": win_rate,
        "pnl_total": round(pnl, 2),
        "ultimos_trades": ultimos,
    }


def _fetchone(conn, sql, params=None):
    if params is None:
        params = ()
    cur = conn.execute(sql, params)
    row = cur.fetchone()
    cur.close()
    return dict(row) if row else None
