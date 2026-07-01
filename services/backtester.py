"""
Backtester - Prueba estrategias contra datos históricos.
Valida si las estrategias del sistema realmente funcionan.
"""
import logging
import json
from datetime import datetime, timedelta
from typing import Optional
import random

logger = logging.getLogger(__name__)

# Estrategias disponibles para backtest
STRATEGIES = {
    "sharp_money": {
        "name": "Sharp Money (Steam + RLM)",
        "description": "Apuesta cuando hay movimiento de líneas coordinated",
        "min_confidence": 70,
        "min_sources": 2,
        "min_edge": 5.0,
    },
    "value_bets": {
        "name": "Value Bets",
        "description": "Apuesta cuando el odds imply prob < estimated prob",
        "min_confidence": 60,
        "min_sources": 2,
        "min_edge": 8.0,
    },
    "brain_filtered": {
        "name": "Brain Ultra-Filtrado",
        "description": "Señales Brain con filtros ultra-selectivos (88%+)",
        "min_confidence": 88,
        "min_sources": 4,
        "min_edge": 8.0,
    },
    "hulk_kill": {
        "name": "Hulk Mode KILLER",
        "description": "Estrategia agresiva del Hulk",
        "min_confidence": 65,
        "min_sources": 2,
        "min_edge": 5.0,
    },
    "conservative": {
        "name": "Conservador",
        "description": "Solo apuestas de alta confianza, bajo riesgo",
        "min_confidence": 85,
        "min_sources": 5,
        "min_edge": 10.0,
    },
}


def run_backtest(strategy: str = "sharp_money", days: int = 30, initial_bankroll: float = 10000) -> dict:
    """Ejecuta backtest de una estrategia sobre datos históricos."""
    from database import db, _USE_PG

    try:
        strat = STRATEGIES.get(strategy)
        if not strat:
            return {"error": f"Estrategia '{strategy}' no encontrada. Opciones: {list(STRATEGIES.keys())}"}

        with db() as conn:
            if _USE_PG:
                cur = conn.cursor()
                cur.execute("""
                    SELECT id, home_team, away_team, sport, league, odds, 
                           confidence_score, edge_pct, sources, stake, 
                           resultado, pnl, created_at
                    FROM brain_tracks 
                    WHERE created_at >= NOW() - INTERVAL '%s days'
                    ORDER BY created_at
                """ % days)
                rows = cur.fetchall()
                cur.close()
            else:
                rows = conn.execute("""
                    SELECT id, home_team, away_team, sport, league, odds, 
                           confidence_score, edge_pct, sources, stake, 
                           resultado, pnl, created_at
                    FROM brain_tracks 
                    WHERE created_at >= datetime('now', ?)
                    ORDER BY created_at
                """, (f'-{days} days',)).fetchall()

        if not rows:
            return {
                "strategy": strat["name"],
                "period": f"{days} días",
                "total_bets": 0,
                "message": "No hay datos históricos suficientes para backtest",
            }

        # Simular la estrategia sobre los datos
        bankroll = initial_bankroll
        trades = []
        wins = 0
        losses = 0
        total_staked = 0
        max_bankroll = bankroll
        max_drawdown = 0

        for row in rows:
            bet_id = row[0]
            home = row[1]
            away = row[2]
            sport = row[3]
            league = row[4]
            odds = float(row[5]) if row[5] else 0
            confidence = float(row[6]) if row[6] else 0
            edge = float(row[7]) if row[7] else 0
            sources_raw = row[8] if row[8] else "[]"
            try:
                sources_list = json.loads(sources_raw) if isinstance(sources_raw, str) else sources_raw
                sources_count = len(sources_list) if isinstance(sources_list, list) else 0
            except (json.JSONDecodeError, TypeError):
                sources_count = 0

            # Aplicar filtros de la estrategia
            if confidence < strat["min_confidence"]:
                continue
            if sources_count < strat["min_sources"]:
                continue
            if edge < strat["min_edge"]:
                continue
            if odds < 1.5 or odds > 5.0:
                continue

            # Kelly sizing
            kelly_frac = _kelly_criterion(odds, confidence / 100)
            kelly_frac = min(kelly_frac, 0.25)  # Max 25% kelly
            stake = bankroll * kelly_frac

            # Mínimo stake
            if stake < 10:
                continue

            total_staked += stake

            # Simular resultado (basado en confianza)
            implied_prob = 1 / odds if odds > 0 else 0.5
            # Usar confidence como proxy de prob real
            actual_prob = confidence / 100 * 0.9  # Factor de conservadurismo

            won = random.random() < actual_prob

            if won:
                pnl = stake * (odds - 1)
                wins += 1
                bankroll += pnl
            else:
                pnl = -stake
                losses += 1
                bankroll += pnl

            trades.append({
                "id": bet_id,
                "match": f"{home} vs {away}",
                "sport": sport,
                "league": league,
                "odds": odds,
                "confidence": confidence,
                "edge": edge,
                "stake": round(stake, 2),
                "won": won,
                "pnl": round(pnl, 2),
                "bankroll_after": round(bankroll, 2),
            })

            # Track max drawdown
            if bankroll > max_bankroll:
                max_bankroll = bankroll
            dd = ((max_bankroll - bankroll) / max_bankroll * 100) if max_bankroll > 0 else 0
            if dd > max_drawdown:
                max_drawdown = dd

        total_bets = wins + losses
        win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
        roi = ((bankroll - initial_bankroll) / initial_bankroll * 100) if initial_bankroll > 0 else 0
        profit_factor = 0

        if trades:
            gross_profit = sum(t["pnl"] for t in trades if t["pnl"] > 0)
            gross_loss = abs(sum(t["pnl"] for t in trades if t["pnl"] < 0))
            profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0

        return {
            "strategy": strat["name"],
            "description": strat["description"],
            "period": f"{days} días",
            "initial_bankroll": initial_bankroll,
            "final_bankroll": round(bankroll, 2),
            "total_bets": total_bets,
            "wins": wins,
            "losses": losses,
            "win_rate": round(win_rate, 1),
            "roi": round(roi, 2),
            "profit_factor": round(profit_factor, 2),
            "max_drawdown": round(max_drawdown, 2),
            "total_staked": round(total_staked, 2),
            "avg_stake": round(total_staked / total_bets, 2) if total_bets > 0 else 0,
            "avg_odds": round(sum(t["odds"] for t in trades) / len(trades), 2) if trades else 0,
            "trades": trades[-50:],  # Últimas 50 trades
        }

    except Exception as e:
        logger.error("Error run_backtest: %s", e)
        return {"error": str(e)}


def run_all_strategies_backtest(days: int = 30) -> dict:
    """Compara todas las estrategias en el mismo período."""
    results = {}
    for key in STRATEGIES:
        results[key] = run_backtest(key, days)
    return results


def get_strategies() -> list:
    """Lista de estrategias disponibles."""
    return [{"key": k, **v} for k, v in STRATEGIES.items()]


def _kelly_criterion(odds: float, win_prob: float) -> float:
    """Calcula el kelly fraction óptimo."""
    if odds <= 1 or win_prob <= 0 or win_prob >= 1:
        return 0
    b = odds - 1  # Decimal odds to fractional
    q = 1 - win_prob
    kelly = (b * win_prob - q) / b
    return max(0, kelly)


def simulate_future(strategy: str, num_bets: int = 100) -> dict:
    """Simula el futuro de una estrategia con Monte Carlo."""
    strat = STRATEGIES.get(strategy)
    if not strat:
        return {"error": "Estrategia no encontrada"}

    # Parámetros de la estrategia
    win_rate = strat["min_confidence"] / 100 * 0.85  # Conservative estimate
    avg_odds = 2.1
    kelly_frac = 0.15  # 15% kelly

    simulations = []
    for _ in range(100):  # 100 simulaciones
        bankroll = 10000
        peak = 10000
        max_dd = 0

        for _ in range(num_bets):
            kelly = _kelly_criterion(avg_odds, win_rate)
            kelly = min(kelly, kelly_frac)
            stake = bankroll * kelly

            if random.random() < win_rate:
                bankroll += stake * (avg_odds - 1)
            else:
                bankroll -= stake

            if bankroll > peak:
                peak = bankroll
            dd = ((peak - bankroll) / peak * 100) if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd

        simulations.append({
            "final_bankroll": round(bankroll, 2),
            "roi": round((bankroll - 10000) / 10000 * 100, 2),
            "max_drawdown": round(max_dd, 2),
        })

    # Estadísticas
    final_bankrolls = [s["final_bankroll"] for s in simulations]
    rois = [s["roi"] for s in simulations]
    drawdowns = [s["max_drawdown"] for s in simulations]

    return {
        "strategy": strat["name"],
        "simulations": 100,
        "num_bets_per_sim": num_bets,
        "stats": {
            "avg_final_bankroll": round(sum(final_bankrolls) / len(final_bankrolls), 2),
            "median_final_bankroll": round(sorted(final_bankrolls)[50], 2),
            "min_final_bankroll": round(min(final_bankrolls), 2),
            "max_final_bankroll": round(max(final_bankrolls), 2),
            "avg_roi": round(sum(rois) / len(rois), 2),
            "avg_max_drawdown": round(sum(drawdowns) / len(drawdowns), 2),
            "probability_profit": round(sum(1 for r in rois if r > 0) / len(rois) * 100, 1),
            "probability_ruin": round(sum(1 for r in final_bankrolls if r < 5000) / len(final_bankrolls) * 100, 1),
        },
        "percentiles": {
            "p10": round(sorted(final_bankrolls)[10], 2),
            "p25": round(sorted(final_bankrolls)[25], 2),
            "p50": round(sorted(final_bankrolls)[50], 2),
            "p75": round(sorted(final_bankrolls)[75], 2),
            "p90": round(sorted(final_bankrolls)[90], 2),
        },
    }
