"""
Performance Tracker - Rastrea resultados reales del sistema.
ROI, win rate por tipo de señal, y métricas de calidad.
"""
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def _pg_sql(sql_pg, sql_sqlite, days, _USE_PG):
    """Retorna SQL y parámetros según el motor de BD."""
    if _USE_PG:
        return sql_pg, (days,)
    else:
        return sql_sqlite.format(days), ()


def get_performance_summary(days: int = 30) -> dict:
    """Resumen de performance de los últimos N días."""
    from database import db, _USE_PG

    try:
        sql_pg = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN resultado = 'ganada' THEN 1 ELSE 0 END) as ganadas,
                SUM(CASE WHEN resultado = 'perdida' THEN 1 ELSE 0 END) as perdidas,
                SUM(CASE WHEN resultado = 'empate' THEN 1 ELSE 0 END) as empates,
                SUM(CASE WHEN resultado = 'ganada' THEN pnl ELSE 0 END) as total_pnl_ganadas,
                SUM(CASE WHEN resultado = 'perdida' THEN pnl ELSE 0 END) as total_pnl_perdidas,
                SUM(pnl) as total_pnl,
                AVG(CASE WHEN resultado IN ('ganada','perdida') THEN
                    CASE WHEN resultado='ganada' THEN 1.0 ELSE 0.0 END
                    END) as win_rate,
                AVG(confidence_score) as avg_confidence,
                AVG(edge_pct) as avg_edge,
                AVG(kelly_pct) as avg_kelly,
                AVG(stake) as avg_stake
            FROM brain_tracks
            WHERE created_at >= NOW() - INTERVAL '1 day' * %s
        """
        sql_sqlite = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN resultado = 'ganada' THEN 1 ELSE 0 END) as ganadas,
                SUM(CASE WHEN resultado = 'perdida' THEN 1 ELSE 0 END) as perdidas,
                SUM(CASE WHEN resultado = 'empate' THEN 1 ELSE 0 END) as empates,
                SUM(CASE WHEN resultado = 'ganada' THEN pnl ELSE 0 END) as total_pnl_ganadas,
                SUM(CASE WHEN resultado = 'perdida' THEN pnl ELSE 0 END) as total_pnl_perdidas,
                SUM(pnl) as total_pnl,
                AVG(CASE WHEN resultado IN ('ganada','perdida') THEN
                    CASE WHEN resultado='ganada' THEN 1.0 ELSE 0.0 END
                    END) as win_rate,
                AVG(confidence_score) as avg_confidence,
                AVG(edge_pct) as avg_edge,
                AVG(kelly_pct) as avg_kelly,
                AVG(stake) as avg_stake
            FROM brain_tracks
            WHERE created_at >= datetime('now', '-{} days')
        """

        sql, params = _pg_sql(sql_pg, sql_sqlite, days, _USE_PG)

        with db() as conn:
            if _USE_PG:
                cur = conn.cursor()
                cur.execute(sql, params)
                row = cur.fetchone()
                cur.close()
            else:
                row = conn.execute(sql, params).fetchone()

            result = {
                "total": row[0] or 0,
                "ganadas": row[1] or 0,
                "perdidas": row[2] or 0,
                "empates": row[3] or 0,
                "pnl_ganadas": round(float(row[4] or 0), 2),
                "pnl_perdidas": round(float(row[5] or 0), 2),
                "total_pnl": round(float(row[6] or 0), 2),
                "win_rate": round(float(row[7] or 0) * 100, 1),
                "avg_confidence": round(float(row[8] or 0), 1),
                "avg_edge": round(float(row[9] or 0), 1),
                "avg_kelly": round(float(row[10] or 0), 1),
                "avg_stake": round(float(row[11] or 0), 2),
            }

            total_staked = result["total"] * result["avg_stake"]
            result["roi"] = round((result["total_pnl"] / total_staked * 100) if total_staked > 0 else 0, 2)
            result["profit_factor"] = round(
                (result["pnl_ganadas"] / abs(result["pnl_perdidas"]))
                if result["pnl_perdidas"] != 0 else 0, 2
            )
            result["calidad"] = _clasificar_calidad(result)

            return result

    except Exception as e:
        logger.error("Error get_performance_summary: %s", e)
        return {"total": 0, "ganadas": 0, "perdidas": 0, "total_pnl": 0, "win_rate": 0, "roi": 0}


def get_performance_by_source(days: int = 30) -> list:
    """Performance desglosada por fuente de señal."""
    from database import db, _USE_PG

    try:
        sql_pg = """
            SELECT
                COALESCE(sources, 'unknown') as source,
                COUNT(*) as total,
                SUM(CASE WHEN resultado = 'ganada' THEN 1 ELSE 0 END) as ganadas,
                SUM(pnl) as total_pnl,
                AVG(confidence_score) as avg_conf
            FROM brain_tracks
            WHERE created_at >= NOW() - INTERVAL '1 day' * %s
            GROUP BY sources
            ORDER BY total_pnl DESC
        """
        sql_sqlite = """
            SELECT
                COALESCE(sources, 'unknown') as source,
                COUNT(*) as total,
                SUM(CASE WHEN resultado = 'ganada' THEN 1 ELSE 0 END) as ganadas,
                SUM(pnl) as total_pnl,
                AVG(confidence_score) as avg_conf
            FROM brain_tracks
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY sources
            ORDER BY total_pnl DESC
        """

        sql, params = _pg_sql(sql_pg, sql_sqlite, days, _USE_PG)

        with db() as conn:
            if _USE_PG:
                cur = conn.cursor()
                cur.execute(sql, params)
                rows = cur.fetchall()
                cur.close()
            else:
                rows = conn.execute(sql, params).fetchall()

            results = []
            for row in rows:
                total = row[1] or 0
                ganadas = row[2] or 0
                results.append({
                    "source": row[0] or "unknown",
                    "total": total,
                    "ganadas": ganadas,
                    "win_rate": round((ganadas / total * 100) if total > 0 else 0, 1),
                    "total_pnl": round(float(row[3] or 0), 2),
                    "avg_confidence": round(float(row[4] or 0), 1),
                })
            return results

    except Exception as e:
        logger.error("Error get_performance_by_source: %s", e)
        return []


def get_clv_summary(days: int = 30) -> dict:
    """Closing Line Value - mide si las apuestas vencen a la línea de cierre."""
    from database import db, _USE_PG

    try:
        sql_pg = """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN odds > 0 AND resultado = 'ganada' THEN 1 ELSE 0 END)::float /
                    NULLIF(SUM(CASE WHEN odds > 0 AND resultado IN ('ganada','perdida') THEN 1 ELSE 0 END), 0) as implied_vs_actual
            FROM brain_tracks
            WHERE created_at >= NOW() - INTERVAL '1 day' * %s
        """
        sql_sqlite = """
            SELECT
                COUNT(*) as total,
                CAST(SUM(CASE WHEN odds > 0 AND resultado = 'ganada' THEN 1 ELSE 0 END) AS REAL) /
                    NULLIF(SUM(CASE WHEN odds > 0 AND resultado IN ('ganada','perdida') THEN 1 ELSE 0 END), 0) as implied_vs_actual
            FROM brain_tracks
            WHERE created_at >= datetime('now', '-{} days')
        """

        sql, params = _pg_sql(sql_pg, sql_sqlite, days, _USE_PG)

        with db() as conn:
            if _USE_PG:
                cur = conn.cursor()
                cur.execute(sql, params)
                row = cur.fetchone()
                cur.close()
            else:
                row = conn.execute(sql, params).fetchone()

            total = row[0] or 0
            return {
                "total_apuestas": total,
                "implied_prob_vs_real": round(float(row[1] or 0) * 100, 1),
                "status": "DATA" if total > 0 else "NO_DATA",
                "note": "CLV real requiere closing odds (odds al cierre del partido)",
            }

    except Exception as e:
        logger.error("Error get_clv_summary: %s", e)
        return {"total_apuestas": 0, "implied_prob_vs_real": 0, "status": "NO_DATA"}


def get_performance_by_confidence(days: int = 30) -> list:
    """Win rate por nivel de confianza."""
    from database import db, _USE_PG

    try:
        sql_pg = """
            SELECT
                CASE
                    WHEN confidence_score >= 80 THEN 'ALTA (80+)'
                    WHEN confidence_score >= 60 THEN 'MEDIA (60-79)'
                    WHEN confidence_score >= 40 THEN 'BAJA (40-59)'
                    ELSE 'MUY_BAJA (<40)'
                END as nivel,
                COUNT(*) as total,
                SUM(CASE WHEN resultado = 'ganada' THEN 1 ELSE 0 END) as ganadas,
                SUM(pnl) as total_pnl
            FROM brain_tracks
            WHERE created_at >= NOW() - INTERVAL '1 day' * %s
            GROUP BY nivel
            ORDER BY nivel
        """
        sql_sqlite = """
            SELECT
                CASE
                    WHEN confidence_score >= 80 THEN 'ALTA (80+)'
                    WHEN confidence_score >= 60 THEN 'MEDIA (60-79)'
                    WHEN confidence_score >= 40 THEN 'BAJA (40-59)'
                    ELSE 'MUY_BAJA (<40)'
                END as nivel,
                COUNT(*) as total,
                SUM(CASE WHEN resultado = 'ganada' THEN 1 ELSE 0 END) as ganadas,
                SUM(pnl) as total_pnl
            FROM brain_tracks
            WHERE created_at >= datetime('now', '-{} days')
            GROUP BY nivel
            ORDER BY nivel
        """

        sql, params = _pg_sql(sql_pg, sql_sqlite, days, _USE_PG)

        with db() as conn:
            if _USE_PG:
                cur = conn.cursor()
                cur.execute(sql, params)
                rows = cur.fetchall()
                cur.close()
            else:
                rows = conn.execute(sql, params).fetchall()

            results = []
            for row in rows:
                total = row[1] or 0
                ganadas = row[2] or 0
                results.append({
                    "nivel": row[0],
                    "total": total,
                    "ganadas": ganadas,
                    "win_rate": round((ganadas / total * 100) if total > 0 else 0, 1),
                    "total_pnl": round(float(row[3] or 0), 2),
                })
            return results

    except Exception as e:
        logger.error("Error get_performance_by_confidence: %s", e)
        return []


def get_streak_analysis(days: int = 30) -> dict:
    """Análisis de rachas."""
    from database import db, _USE_PG

    try:
        sql_pg = """
            SELECT resultado FROM brain_tracks
            WHERE created_at >= NOW() - INTERVAL '1 day' * %s
            AND resultado IN ('ganada', 'perdida')
            ORDER BY created_at
        """
        sql_sqlite = """
            SELECT resultado FROM brain_tracks
            WHERE created_at >= datetime('now', '-{} days')
            AND resultado IN ('ganada', 'perdida')
            ORDER BY created_at
        """

        sql, params = _pg_sql(sql_pg, sql_sqlite, days, _USE_PG)

        with db() as conn:
            if _USE_PG:
                cur = conn.cursor()
                cur.execute(sql, params)
                rows = [r[0] for r in cur.fetchall()]
                cur.close()
            else:
                rows = [r[0] for r in conn.execute(sql, params).fetchall()]

            if not rows:
                return {"max_win_streak": 0, "max_lose_streak": 0, "current_streak": 0, "current_type": "none"}

            max_win = 0
            max_lose = 0
            current = 1
            current_type = rows[0]

            for i in range(1, len(rows)):
                if rows[i] == rows[i-1]:
                    current += 1
                else:
                    if rows[i-1] == 'ganada':
                        max_win = max(max_win, current)
                    else:
                        max_lose = max(max_lose, current)
                    current = 1
                    current_type = rows[i]

            if rows[-1] == 'ganada':
                max_win = max(max_win, current)
            else:
                max_lose = max(max_lose, current)

            return {
                "max_win_streak": max_win,
                "max_lose_streak": max_lose,
                "current_streak": current,
                "current_type": current_type,
            }

    except Exception as e:
        logger.error("Error get_streak_analysis: %s", e)
        return {"max_win_streak": 0, "max_lose_streak": 0, "current_streak": 0, "current_type": "none"}


def _clasificar_calidad(result: dict) -> str:
    """Clasifica la calidad del sistema basado en métricas."""
    wr = result.get("win_rate", 0)
    roi = result.get("roi", 0)
    pf = result.get("profit_factor", 0)
    total = result.get("total", 0)

    if total < 10:
        return "INSUFICIENTE"
    if wr >= 55 and roi > 5 and pf > 1.2:
        return "EXCELENTE"
    if wr >= 50 and roi > 0 and pf > 1.0:
        return "BUENA"
    if wr >= 45 and roi > -5:
        return "REGULAR"
    return "MALA"
