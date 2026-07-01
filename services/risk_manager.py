"""
Risk Manager - Control de riesgo para el sistema de apuestas.
Stop loss, max exposición, límites diarios, diversificación automática.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# Configuración de riesgo
MAX_EXPOSURE_POR_PARTIDO = 5       # % del bankroll máximo por partido
MAX_EXPOSURE_POR_DEPORTE = 20      # % del bankroll máximo por deporte
MAX_APUESTAS_DIARIAS = 15          # máximo de apuestas por día
STOP_LOSS_DIARIO = -500            # stop loss diario en $
STOP_LOSS_SEMANAL = -2000          # stop loss semanal en $
MAX_DRAWDOWN_PCT = 15              # drawdown máximo antes de pausar
MAX_KELLY_FRACTION = 0.25          # máximo 25% del kelly óptimo
MIN_BANKROLL_RESERVE = 2000        # reserva mínima del bankroll


def get_risk_status() -> dict:
    """Estado actual del sistema de riesgo."""
    from database import db, _USE_PG

    try:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())

        with db() as conn:
            if _USE_PG:
                cur = conn.cursor()

                # Bankroll actual
                cur.execute("SELECT bankroll FROM brain_bankroll ORDER BY id DESC LIMIT 1")
                row = cur.fetchone()
                bankroll = float(row[0]) if row and row[0] else 10000

                # Apuestas hoy
                cur.execute("""
                    SELECT COUNT(*), COALESCE(SUM(stake), 0), COALESCE(SUM(pnl), 0)
                    FROM brain_tracks WHERE created_at >= %s
                """, (today_start,))
                today = cur.fetchone()
                today_count = today[0] or 0
                today_staked = float(today[1] or 0)
                today_pnl = float(today[2] or 0)

                # Apuestas esta semana
                cur.execute("""
                    SELECT COUNT(*), COALESCE(SUM(stake), 0), COALESCE(SUM(pnl), 0)
                    FROM brain_tracks WHERE created_at >= %s
                """, (week_start,))
                week = cur.fetchone()
                week_count = week[0] or 0
                week_staked = float(week[1] or 0)
                week_pnl = float(week[2] or 0)

                # Exposición por deporte
                cur.execute("""
                    SELECT sport, SUM(stake) as total_staked
                    FROM brain_tracks 
                    WHERE created_at >= %s AND resultado IS NULL
                    GROUP BY sport
                """, (today_start,))
                sport_exposure = {r[0]: float(r[1]) for r in cur.fetchall()}

                # Exposición por partido
                cur.execute("""
                    SELECT home_team || ' vs ' || away_team as match, stake
                    FROM brain_tracks 
                    WHERE created_at >= %s AND resultado IS NULL
                """, (today_start,))
                match_exposure = {r[0]: float(r[1]) for r in cur.fetchall()}

                # Drawdown actual
                cur.execute("SELECT MAX.bankroll FROM (SELECT bankroll FROM brain_bankroll ORDER BY id) LIMIT 1")
                cur.execute("SELECT bankroll FROM brain_bankroll ORDER BY id DESC LIMIT 1")
                max_bankroll_row = cur.fetchone()
                max_bankroll = float(max_bankroll_row[0]) if max_bankroll_row else bankroll
                drawdown_pct = ((max_bankroll - bankroll) / max_bankroll * 100) if max_bankroll > 0 else 0

                cur.close()

            else:
                row = conn.execute("SELECT bankroll FROM brain_bankroll ORDER BY id DESC LIMIT 1").fetchone()
                bankroll = float(row[0]) if row and row[0] else 10000

                today = conn.execute("""
                    SELECT COUNT(*), COALESCE(SUM(stake), 0), COALESCE(SUM(pnl), 0)
                    FROM brain_tracks WHERE created_at >= ?
                """, (today_start.isoformat(),)).fetchone()
                today_count = today[0] or 0
                today_staked = float(today[1] or 0)
                today_pnl = float(today[2] or 0)

                week = conn.execute("""
                    SELECT COUNT(*), COALESCE(SUM(stake), 0), COALESCE(SUM(pnl), 0)
                    FROM brain_tracks WHERE created_at >= ?
                """, (week_start.isoformat(),)).fetchone()
                week_count = week[0] or 0
                week_staked = float(week[1] or 0)
                week_pnl = float(week[2] or 0)

                sport_rows = conn.execute("""
                    SELECT sport, SUM(stake) as total_staked
                    FROM brain_tracks 
                    WHERE created_at >= ? AND resultado IS NULL
                    GROUP BY sport
                """, (today_start.isoformat(),)).fetchall()
                sport_exposure = {r[0]: float(r[1]) for r in sport_rows}

                match_rows = conn.execute("""
                    SELECT home_team || ' vs ' || away_team as match, stake
                    FROM brain_tracks 
                    WHERE created_at >= ? AND resultado IS NULL
                """, (today_start.isoformat(),)).fetchall()
                match_exposure = {r[0]: float(r[1]) for r in match_rows}

                max_bankroll_row = conn.execute("SELECT bankroll FROM brain_bankroll ORDER BY id DESC LIMIT 1").fetchone()
                max_bankroll = float(max_bankroll_row[0]) if max_bankroll_row else bankroll
                drawdown_pct = ((max_bankroll - bankroll) / max_bankroll * 100) if max_bankroll > 0 else 0

            # Alertas
            alerts = []
            if today_count >= MAX_APUESTAS_DIARIAS:
                alerts.append(f"⚠️ Límite diario alcanzado ({today_count}/{MAX_APUESTAS_DIARIAS})")
            if today_pnl <= STOP_LOSS_DIARIO:
                alerts.append(f"🛑 STOP LOSS DIARIO: ${today_pnl:.2f}")
            if week_pnl <= STOP_LOSS_SEMANAL:
                alerts.append(f"🛑 STOP LOSS SEMANAL: ${week_pnl:.2f}")
            if drawdown_pct >= MAX_DRAWDOWN_PCT:
                alerts.append(f"🛑 DRAWDOWN MÁXIMO: {drawdown_pct:.1f}%")
            if bankroll < MIN_BANKROLL_RESERVE:
                alerts.append(f"⚠️ Bankroll bajo reserva: ${bankroll:.2f}")

            # Verificar si el sistema debe pausarse
            paused = (
                today_pnl <= STOP_LOSS_DIARIO or
                week_pnl <= STOP_LOSS_SEMANAL or
                drawdown_pct >= MAX_DRAWDOWN_PCT
            )

            return {
                "bankroll": round(bankroll, 2),
                "today": {
                    "count": today_count,
                    "staked": round(today_staked, 2),
                    "pnl": round(today_pnl, 2),
                    "limit": MAX_APUESTAS_DIARIAS,
                    "remaining": max(0, MAX_APUESTAS_DIARIAS - today_count),
                },
                "week": {
                    "count": week_count,
                    "staked": round(week_staked, 2),
                    "pnl": round(week_pnl, 2),
                },
                "exposure": {
                    "by_sport": sport_exposure,
                    "by_match": match_exposure,
                },
                "risk_metrics": {
                    "drawdown_pct": round(drawdown_pct, 2),
                    "max_drawdown_pct": MAX_DRAWDOWN_PCT,
                    "stop_loss_diario": STOP_LOSS_DIARIO,
                    "stop_loss_semanal": STOP_LOSS_SEMANAL,
                    "max_exposure_por_partido": MAX_EXPOSURE_POR_PARTIDO,
                    "max_exposure_por_deporte": MAX_EXPOSURE_POR_DEPORTE,
                },
                "alerts": alerts,
                "paused": paused,
                "status": "PAUSADO" if paused else "ACTIVO",
            }

    except Exception as e:
        logger.error("Error get_risk_status: %s", e)
        return {
            "bankroll": 10000,
            "today": {"count": 0, "staked": 0, "pnl": 0, "limit": MAX_APUESTAS_DIARIAS, "remaining": MAX_APUESTAS_DIARIAS},
            "week": {"count": 0, "staked": 0, "pnl": 0},
            "exposure": {"by_sport": {}, "by_match": {}},
            "risk_metrics": {},
            "alerts": [],
            "paused": False,
            "status": "ERROR",
        }


def check_can_bet(sport: str, match: str, stake: float) -> dict:
    """Verifica si se puede hacer una apuesta según las reglas de riesgo."""
    from database import db, _USE_PG

    try:
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        with db() as conn:
            if _USE_PG:
                cur = conn.cursor()
                cur.execute("SELECT bankroll FROM brain_bankroll ORDER BY id DESC LIMIT 1")
                row = cur.fetchone()
                bankroll = float(row[0]) if row and row[0] else 10000

                cur.execute("SELECT COUNT(*) FROM brain_tracks WHERE created_at >= %s", (today_start,))
                today_count = cur.fetchone()[0] or 0

                cur.execute("SELECT COALESCE(SUM(stake), 0) FROM brain_tracks WHERE created_at >= %s AND sport = %s", (today_start, sport))
                sport_staked = float(cur.fetchone()[0] or 0)

                cur.execute("SELECT COALESCE(SUM(stake), 0) FROM brain_tracks WHERE created_at >= %s AND home_team || ' vs ' || away_team = %s", (today_start, match))
                match_staked = float(cur.fetchone()[0] or 0)

                cur.execute("SELECT COALESCE(SUM(pnl), 0) FROM brain_tracks WHERE created_at >= %s", (today_start,))
                today_pnl = float(cur.fetchone()[0] or 0)

                cur.execute("SELECT COALESCE(SUM(pnl), 0) FROM brain_tracks WHERE created_at >= %s", (today_start - timedelta(days=today_start.weekday()),))
                week_pnl = float(cur.fetchone()[0] or 0)

                cur.close()
            else:
                row = conn.execute("SELECT bankroll FROM brain_bankroll ORDER BY id DESC LIMIT 1").fetchone()
                bankroll = float(row[0]) if row and row[0] else 10000
                today_count = conn.execute("SELECT COUNT(*) FROM brain_tracks WHERE created_at >= ?", (today_start.isoformat(),)).fetchone()[0] or 0
                sport_staked = float(conn.execute("SELECT COALESCE(SUM(stake), 0) FROM brain_tracks WHERE created_at >= ? AND sport = ?", (today_start.isoformat(), sport)).fetchone()[0] or 0)
                match_staked = float(conn.execute("SELECT COALESCE(SUM(stake), 0) FROM brain_tracks WHERE created_at >= ? AND home_team || ' vs ' || away_team = ?", (today_start.isoformat(), match)).fetchone()[0] or 0)
                today_pnl = float(conn.execute("SELECT COALESCE(SUM(pnl), 0) FROM brain_tracks WHERE created_at >= ?", (today_start.isoformat(),)).fetchone()[0] or 0)
                week_pnl = float(conn.execute("SELECT COALESCE(SUM(pnl), 0) FROM brain_tracks WHERE created_at >= ?", ((today_start - timedelta(days=today_start.weekday())).isoformat(),)).fetchone()[0] or 0)

        # Verificaciones
        reasons = []
        allowed = True

        # 1. Stop loss diario
        if today_pnl <= STOP_LOSS_DIARIO:
            allowed = False
            reasons.append(f"Stop loss diario alcanzado: ${today_pnl:.2f}")

        # 2. Stop loss semanal
        if week_pnl <= STOP_LOSS_SEMANAL:
            allowed = False
            reasons.append(f"Stop loss semanal alcanzado: ${week_pnl:.2f}")

        # 3. Límite de apuestas diarias
        if today_count >= MAX_APUESTAS_DIARIAS:
            allowed = False
            reasons.append(f"Límite diario: {today_count}/{MAX_APUESTAS_DIARIAS}")

        # 4. Exposición por partido
        match_pct = ((match_staked + stake) / bankroll * 100) if bankroll > 0 else 100
        if match_pct > MAX_EXPOSURE_POR_PARTIDO:
            allowed = False
            reasons.append(f"Exposición por partido: {match_pct:.1f}% > {MAX_EXPOSURE_POR_PARTIDO}%")

        # 5. Exposición por deporte
        sport_pct = ((sport_staked + stake) / bankroll * 100) if bankroll > 0 else 100
        if sport_pct > MAX_EXPOSURE_POR_DEPORTE:
            allowed = False
            reasons.append(f"Exposición por deporte: {sport_pct:.1f}% > {MAX_EXPOSURE_POR_DEPORTE}%")

        # 6. Reserva mínima
        if (bankroll - stake) < MIN_BANKROLL_RESERVE:
            allowed = False
            reasons.append(f"Bankroll bajo reserva: ${bankroll - stake:.2f} < ${MIN_BANKROLL_RESERVE}")

        # 7. Kelly máximo
        kelly_pct = (stake / bankroll * 100) if bankroll > 0 else 100
        if kelly_pct > MAX_KELLY_FRACTION * 100:
            reasons.append(f"Stake alto: {kelly_pct:.1f}% del bankroll (max {MAX_KELLY_FRACTION*100}%)")
            stake = bankroll * MAX_KELLY_FRACTION

        return {
            "allowed": allowed,
            "reasons": reasons,
            "recommended_stake": round(stake, 2),
            "bankroll": round(bankroll, 2),
        }

    except Exception as e:
        logger.error("Error check_can_bet: %s", e)
        return {"allowed": False, "reasons": [str(e)], "recommended_stake": 0, "bankroll": 10000}


def get_daily_limits() -> dict:
    """Límites diarios configurados."""
    return {
        "max_apuestas_diarias": MAX_APUESTAS_DIARIAS,
        "stop_loss_diario": STOP_LOSS_DIARIO,
        "stop_loss_semanal": STOP_LOSS_SEMANAL,
        "max_exposure_por_partido": MAX_EXPOSURE_POR_PARTIDO,
        "max_exposure_por_deporte": MAX_EXPOSURE_POR_DEPORTE,
        "max_drawdown_pct": MAX_DRAWDOWN_PCT,
        "max_kelly_fraction": MAX_KELLY_FRACTION,
        "min_bankroll_reserve": MIN_BANKROLL_RESERVE,
    }


def update_risk_config(config: dict) -> dict:
    """Actualiza configuración de riesgo (solo en memoria, no persistente)."""
    global MAX_EXPOSURE_POR_PARTIDO, MAX_EXPOSURE_POR_DEPORTE, MAX_APUESTAS_DIARIAS
    global STOP_LOSS_DIARIO, STOP_LOSS_SEMANAL, MAX_DRAWDOWN_PCT, MAX_KELLY_FRACTION, MIN_BANKROLL_RESERVE

    if "max_exposure_por_partido" in config:
        MAX_EXPOSURE_POR_PARTIDO = float(config["max_exposure_por_partido"])
    if "max_exposure_por_deporte" in config:
        MAX_EXPOSURE_POR_DEPORTE = float(config["max_exposure_por_deporte"])
    if "max_apuestas_diarias" in config:
        MAX_APUESTAS_DIARIAS = int(config["max_apuestas_diarias"])
    if "stop_loss_diario" in config:
        STOP_LOSS_DIARIO = float(config["stop_loss_diario"])
    if "stop_loss_semanal" in config:
        STOP_LOSS_SEMANAL = float(config["stop_loss_semanal"])
    if "max_drawdown_pct" in config:
        MAX_DRAWDOWN_PCT = float(config["max_drawdown_pct"])
    if "max_kelly_fraction" in config:
        MAX_KELLY_FRACTION = float(config["max_kelly_fraction"])
    if "min_bankroll_reserve" in config:
        MIN_BANKROLL_RESERVE = float(config["min_bankroll_reserve"])

    return get_daily_limits()