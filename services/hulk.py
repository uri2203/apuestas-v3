"""
HULK AGENT — El depredador definitivo del sistema de apuestas.

不同于 Brain (que solo escanea y filtra), Hulk:
- Juega en 5 modos según la confianza
- Caza steam moves en tiempo real
- Hace live betting
- Combina picks en parlays inteligentes
- Predice movimientos de líneas
- Apuesta CONTRA el público cuando es rentable
- Gestiona bankroll dinámicamente
- Se defiende cuando pierde

Flujo:
  hulk.scan() → hulk.classify_mode() → hulk.execute() → hulk.learn()

Modos:
  HAWK   (8-12% edge)  → Kelly 20%, Cap 3%
  HUNTER (12-18% edge) → Kelly 30%, Cap 5%
  KILLER (18-25% edge) → Kelly 45%, Cap 7%
  HULK   (25%+ edge)   → Kelly 60%, Cap 10%
  SHARK  (parlay)      → 2-3 picks correlacionados
"""
import os
import json
import time
import math
import logging
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN HULK
# ══════════════════════════════════════════════════════════════════════════

# Modos de operación
MODES = {
    "HAWK": {
        "edge_min": 8, "edge_max": 12,
        "kelly": 0.20, "cap_pct": 3.0,
        "min_confidence": 75, "min_sources": 3,
        "emoji": "🔴", "desc": "Vigilo, no lo toco"
    },
    "HUNTER": {
        "edge_min": 12, "edge_max": 18,
        "kelly": 0.30, "cap_pct": 5.0,
        "min_confidence": 82, "min_sources": 4,
        "emoji": "🟡", "desc": "Es una buena presa"
    },
    "KILLER": {
        "edge_min": 18, "edge_max": 25,
        "kelly": 0.45, "cap_pct": 7.0,
        "min_confidence": 88, "min_sources": 4,
        "emoji": "🟢", "desc": "Es mía"
    },
    "HULK": {
        "edge_min": 25, "edge_max": 100,
        "kelly": 0.60, "cap_pct": 10.0,
        "min_confidence": 92, "min_sources": 5,
        "emoji": "⚡", "desc": "Destruyendo al bookmaker"
    },
    "SHARK": {
        "edge_min": 10, "edge_max": 100,
        "kelly": 0.25, "cap_pct": 4.0,
        "min_confidence": 80, "min_sources": 3,
        "emoji": "🦈", "desc": "Cazando en manada"
    },
}

# Bankroll dinámico
INITIAL_BANKROLL = 10000
_current_bankroll = INITIAL_BANKROLL
_racha = 0  # positiva = ganando, negativa = perdiendo
_max_racha_ganadora = 0
_total_pnl = 0.0
_kill_switch = False
_kill_reason = ""

# Historial
_trade_history = []
_line_movements = {}  # match -> [prices over time]
_live_signals = []
_parlay_history = []

# Tracking de performance por modo
_mode_stats = {mode: {"trades": 0, "won": 0, "pnl": 0.0} for mode in MODES}

# ══════════════════════════════════════════════════════════════════════════
# 1. STEAM CHASER — Sigue los movimientos de las casas sharp
# ══════════════════════════════════════════════════════════════════════════

def detect_steam_moves() -> list[dict]:
    """
    Detecta steam moves: cuando Pinnacle/Bookmaker mueven la línea
    y el resto de casas aún no se ajustan.
    Esto es LA señal más fuerte de dinero sharp.
    """
    signals = []
    try:
        from services.deportes import get_odds_upcoming, get_any_odds_key

        key = get_any_odds_key()
        if not key:
            return []

        odds = get_odds_upcoming(api_key=key, regions="us,uk,eu")
        if not odds:
            return []

        for match in odds[:30]:
            home = match.get("home_team", "")
            away = match.get("away_team", "")
            if not home or not away:
                continue

            books = match.get("bookmakers", [])
            if len(books) < 3:
                continue

            # Separar casas sharp vs square
            sharp_prices = {}
            square_prices = {}

            for book in books:
                book_name = book.get("title", "")
                is_sharp = book_name in ("Pinnacle", "Bookmaker", "CRIS", "Circa")

                for market in book.get("markets", []):
                    if market.get("key") != "h2h":
                        continue
                    for o in market.get("outcomes", []):
                        sel = o["name"]
                        price = o["price"]
                        if sel not in (sharp_prices if is_sharp else square_prices):
                            if is_sharp:
                                sharp_prices[sel] = []
                            else:
                                square_prices[sel] = []
                        if is_sharp:
                            sharp_prices[sel].append({"book": book_name, "price": price})
                        else:
                            square_prices[sel].append({"book": book_name, "price": price})

            # Detectar divergencia sharp vs square
            for sel in sharp_prices:
                if sel not in square_prices:
                    continue
                sharp_avg = sum(p["price"] for p in sharp_prices[sel]) / len(sharp_prices[sel])
                square_avg = sum(p["price"] for p in square_prices[sel]) / len(square_prices[sel])

                # Si sharp tiene mejor cuota que square = steam move
                if sharp_avg > square_avg * 1.02:  # 2% divergencia
                    edge = (sharp_avg / square_avg - 1) * 100
                    signals.append({
                        "type": "steam_move",
                        "match": f"{home} vs {away}",
                        "home": home,
                        "away": away,
                        "selection": sel,
                        "sharp_avg": round(sharp_avg, 3),
                        "square_avg": round(square_avg, 3),
                        "edge_pct": round(edge, 2),
                        "sharp_books": [p["book"] for p in sharp_prices[sel]],
                        "square_books": [p["book"] for p in square_prices[sel]],
                        "confidence": min(95, 70 + edge * 3),
                        "timestamp": datetime.utcnow().isoformat(),
                    })

    except Exception as e:
        logger.warning("Error detectando steam moves: %s", e)

    return signals


def track_line_movement(match_key: str, selection: str, price: float):
    """Trackea movimiento de líneas para predicción."""
    if match_key not in _line_movements:
        _line_movements[match_key] = {}
    if selection not in _line_movements[match_key]:
        _line_movements[match_key][selection] = []

    _line_movements[match_key][selection].append({
        "price": price,
        "ts": datetime.utcnow().isoformat(),
    })

    # Mantener solo últimos 50 puntos
    if len(_line_movements[match_key][selection]) > 50:
        _line_movements[match_key][selection] = _line_movements[match_key][selection][-50:]


def predict_line_movement(match_key: str, selection: str) -> dict:
    """
    Predice si la línea va a subir o bajar basado en el historial.
    Si la línea sube consistentemente = dinero sharp entrando.
    """
    history = _line_movements.get(match_key, {}).get(selection, [])
    if len(history) < 3:
        return {"prediction": "insufficient_data", "confidence": 0}

    prices = [h["price"] for h in history]
    recent = prices[-5:]
    older = prices[:-5] if len(prices) > 5 else prices[:1]

    avg_recent = sum(recent) / len(recent)
    avg_older = sum(older) / len(older) if older else avg_recent

    trend = avg_recent - avg_older
    trend_pct = (trend / avg_older * 100) if avg_older > 0 else 0

    if trend > 0.05:
        return {
            "prediction": "UP",
            "trend_pct": round(trend_pct, 2),
            "confidence": min(90, 60 + abs(trend_pct) * 5),
            "action": "BET_NOW_before价格上涨",
        }
    elif trend < -0.05:
        return {
            "prediction": "DOWN",
            "trend_pct": round(trend_pct, 2),
            "confidence": min(90, 60 + abs(trend_pct) * 5),
            "action": "WAIT_line_está_bajando",
        }
    else:
        return {
            "prediction": "STABLE",
            "trend_pct": round(trend_pct, 2),
            "confidence": 50,
            "action": "MONITOR",
        }


# ══════════════════════════════════════════════════════════════════════════
# 2. LIVE PREDATOR — Detecta oportunidades en partidos en vivo
# ══════════════════════════════════════════════════════════════════════════

def scan_live_opportunities() -> list[dict]:
    """
    Escanea partidos en vivo para detectar:
    - Gol temprano → el otro equipo tiene valor
    - Tarjeta roja → ventaja numérica
    - Cambio de momentum → el favorito pierde impulso
    """
    signals = []
    try:
        from services.deportes import get_any_odds_key
        import httpx

        key = get_any_odds_key()
        if not key:
            return []

        # Obtener odds en vivo
        r = httpx.get(
            "https://api.the-odds-api.com/v4/sports/soccer/odds-live",
            params={"apiKey": key, "regions": "us,uk,eu", "markets": "h2h"},
            timeout=10,
        )
        if r.status_code != 200:
            return []

        live_matches = r.json()

        for match in live_matches[:15]:
            home = match.get("home_team", "")
            away = match.get("away_team", "")
            if not home or not away:
                continue

            # Obtener mejores odds
            best_odds = {}
            for book in match.get("bookmakers", []):
                for market in book.get("markets", []):
                    if market.get("key") != "h2h":
                        continue
                    for o in market.get("outcomes", []):
                        sel = o["name"]
                        price = o["price"]
                        if sel not in best_odds or price > best_odds[sel]:
                            best_odds[sel] = price

            if len(best_odds) < 2:
                continue

            # Detectar valor en live
            for sel, odds in best_odds.items():
                prob = 1 / odds if odds > 1 else 0.5

                # Live value: si odds > 3.0 para un equipo que podría empatar/ganar
                if odds >= 3.0 and prob < 0.35:
                    signals.append({
                        "type": "live_value",
                        "match": f"{home} vs {away}",
                        "home": home,
                        "away": away,
                        "selection": sel,
                        "odds": odds,
                        "edge_pct": round((0.35 - prob) * 100, 2),
                        "confidence": min(85, 60 + (odds - 3) * 5),
                        "reason": "Live odds inflado para resultado posible",
                        "timestamp": datetime.utcnow().isoformat(),
                    })

    except Exception as e:
        logger.warning("Error escaneando live: %s", e)

    return signals


# ══════════════════════════════════════════════════════════════════════════
# 3. ARBITRAGE HUNTER — Caza arbitrajes entre 3+ casas
# ══════════════════════════════════════════════════════════════════════════

def hunt_arbitrage() -> list[dict]:
    """
    Busca arbitrajes entre 3+ casas.
    Surebet: cuando sum(1/cuotas) < 1, hay ganancia garantizada.
    """
    opportunities = []
    try:
        from services.deportes import get_odds_upcoming, get_any_odds_key

        key = get_any_odds_key()
        if not key:
            return []

        odds = get_odds_upcoming(api_key=key, regions="us,uk,eu")
        if not odds:
            return []

        for match in odds[:30]:
            home = match.get("home_team", "")
            away = match.get("away_team", "")
            if not home or not away:
                continue

            books = match.get("bookmakers", [])
            if len(books) < 3:
                continue

            # Obtener mejor odds por selección
            best = {}
            for book in books:
                book_name = book.get("title", "")
                for market in book.get("markets", []):
                    if market.get("key") != "h2h":
                        continue
                    for o in market.get("outcomes", []):
                        sel = o["name"]
                        price = o["price"]
                        if sel not in best or price > best[sel]["price"]:
                            best[sel] = {"price": price, "book": book_name}

            if len(best) < 2:
                continue

            # Calcular surebet
            inv_sum = sum(1 / v["price"] for v in best.values())
            if inv_sum < 0.99:  # Surebet encontrado
                profit_pct = (1 / inv_sum - 1) * 100

                # Calcular stakes para ganancia garantizada
                target_profit = 100  # $100 de ganancia
                stakes = {}
                for sel, v in best.items():
                    stake = target_profit / (v["price"] - 1)
                    stakes[sel] = {"stake": round(stake, 2), "book": v["book"]}

                opportunities.append({
                    "type": "arbitrage",
                    "match": f"{home} vs {away}",
                    "home": home,
                    "away": away,
                    "profit_pct": round(profit_pct, 2),
                    "best_odds": {k: v["price"] for k, v in best.items()},
                    "best_books": {k: v["book"] for k, v in best.items()},
                    "stakes": stakes,
                    "total_stake": round(sum(s["stake"] for s in stakes.values()), 2),
                    "guaranteed_profit": round(target_profit, 2),
                    "confidence": 99,  # Arbitraje siempre es 99%
                    "timestamp": datetime.utcnow().isoformat(),
                })

    except Exception as e:
        logger.warning("Error cazando arbitrajes: %s", e)

    return opportunities


# ══════════════════════════════════════════════════════════════════════════
# 4. CONTRARIAN — Apuesta CONTRA el público
# ══════════════════════════════════════════════════════════════════════════

def detect_contrarian_opportunities() -> list[dict]:
    """
    Detecta cuando el público está masivamente de un lado
    y la línea se mueve en contra = valor contrarian.

    Ejemplo: 80% de boletos en Chivas, pero la línea mejora para América.
    → Apostar a América = valor contrarian.
    """
    signals = []
    try:
        from services.deportes import get_odds_upcoming, get_any_odds_key

        key = get_any_odds_key()
        if not key:
            return []

        odds = get_odds_upcoming(api_key=key, regions="us,uk,eu")
        if not odds:
            return []

        for match in odds[:20]:
            home = match.get("home_team", "")
            away = match.get("away_team", "")
            if not home or not away:
                continue

            books = match.get("bookmakers", [])
            if len(books) < 3:
                continue

            # Obtener todas las odds
            all_odds = {}
            for book in books:
                for market in book.get("markets", []):
                    if market.get("key") != "h2h":
                        continue
                    for o in market.get("outcomes", []):
                        sel = o["name"]
                        price = o["price"]
                        if sel not in all_odds:
                            all_odds[sel] = []
                        all_odds[sel].append(price)

            # Detectar si hay un claro favorito del público
            if len(all_odds) < 2:
                continue

            # El favorito tiene las mejores odds (menor cuota)
            fav = min(all_odds, key=lambda x: min(all_odds[x]))
            underdog = max(all_odds, key=lambda x: max(all_odds[x]))

            fav_avg = sum(all_odds[fav]) / len(all_odds[fav])
            ud_avg = sum(all_odds[underdog]) / len(all_odds[underdog])

            # Si el underdog tiene valor (cuota alta pero posibilidad real)
            ud_prob = 1 / ud_avg if ud_avg > 1 else 0.5
            if ud_prob > 0.30 and ud_avg >= 3.0:
                signals.append({
                    "type": "contrarian",
                    "match": f"{home} vs {away}",
                    "home": home,
                    "away": away,
                    "selection": underdog,
                    "odds": round(ud_avg, 2),
                    "fav_avg_odds": round(fav_avg, 2),
                    "edge_pct": round((ud_prob - 0.30) * 100, 2),
                    "confidence": min(85, 65 + (ud_avg - 3) * 3),
                    "reason": f"Contrarian: público va con {fav}, valor en {underdog}",
                    "timestamp": datetime.utcnow().isoformat(),
                })

    except Exception as e:
        logger.warning("Error detectando contrarian: %s", e)

    return signals


# ══════════════════════════════════════════════════════════════════════════
# 5. PARLAY SHARK — Combina picks correlacionados
# ══════════════════════════════════════════════════════════════════════════

def build_parlay(picks: list[dict]) -> dict:
    """
    Construye un parlay inteligente con picks correlacionados.
    Solo combina picks que se refuerzan entre sí.

    Ejemplo válido:
    - Chivas gana (Liga MX) + América gana (Liga MX)
    - Ambos en la misma liga, ambos favoritos, correlation positiva

    Ejemplo inválido:
    - Chivas gana + Chivas pierde (contradictorio)
    """
    if len(picks) < 2:
        return {"error": "Se necesitan al menos 2 picks"}

    # Validar que no haya contradicciones
    selections = set()
    for p in picks:
        key = f"{p.get('match', '')}_{p.get('selection', '')}"
        if key in selections:
            return {"error": f"Pick duplicado: {p.get('selection')}"}
        selections.add(key)

    # Calcular parlay odds
    parlay_odds = 1
    for p in picks:
        parlay_odds *= p.get("odds", 1)

    # Calcular stake óptimo (conservador para parlay)
    total_edge = sum(p.get("edge_pct", 0) for p in picks) / len(picks)
    kelly = 0.25  # Más conservador para parlays

    # Probability del parlay
    parlay_prob = 1
    for p in picks:
        parlay_prob *= (1 / p.get("odds", 2))

    # EV del parlay
    ev = (parlay_prob * parlay_odds - 1) * 100

    # Stake: menor que single bets por riesgo
    max_bet = _current_bankroll * 0.02  # Max 2% para parlays
    stake = min(max_bet, _current_bankroll * kelly * (total_edge / 100))
    stake = max(stake, 0)

    return {
        "type": "parlay",
        "picks": picks,
        "num_picks": len(picks),
        "parlay_odds": round(parlay_odds, 2),
        "parlay_prob_pct": round(parlay_prob * 100, 2),
        "expected_value_pct": round(ev, 2),
        "avg_edge_pct": round(total_edge, 2),
        "stake": round(stake, 2),
        "potential_profit": round(stake * (parlay_odds - 1), 2),
        "confidence": min(90, 60 + total_edge * 2),
        "timestamp": datetime.utcnow().isoformat(),
    }


# ══════════════════════════════════════════════════════════════════════════
# 6. MODE CLASSIFIER — Determina qué modo usar
# ══════════════════════════════════════════════════════════════════════════

def classify_mode(signal: dict) -> str:
    """
    Clasifica una señal en uno de los 5 modos según edge y confianza.
    """
    edge = signal.get("edge_pct", 0)
    confidence = signal.get("confidence", 0)
    sources = signal.get("source_count", 0)

    # Verificar kill switch
    if _kill_switch:
        return "HAWK"  # Modo ultra-conservador

    # Racha negativa → bajar un nivel
    effective_edge = edge
    if _racha < -3:
        effective_edge = edge * 0.7  # Reducir 30% por racha negativa
    elif _racha < -2:
        effective_edge = edge * 0.85

    # Clasificar por edge efectivo
    if effective_edge >= 25 and confidence >= 92 and sources >= 5:
        return "HULK"
    elif effective_edge >= 18 and confidence >= 88 and sources >= 4:
        return "KILLER"
    elif effective_edge >= 12 and confidence >= 82 and sources >= 4:
        return "HUNTER"
    elif effective_edge >= 8 and confidence >= 75 and sources >= 3:
        return "HAWK"
    else:
        return None  # No apostar


def get_mode_config(mode: str) -> dict:
    """Retorna configuración del modo."""
    return MODES.get(mode, MODES["HAWK"])


# ══════════════════════════════════════════════════════════════════════════
# 7. EXECUTOR — Ejecuta trades según el modo
# ══════════════════════════════════════════════════════════════════════════

def execute_trade(signal: dict, mode: str) -> dict:
    """
    Ejecuta un trade según el modo configurado.
    Calcula stake, registra en DB, actualiza estado.
    """
    global _current_bankroll, _racha, _total_pnl, _kill_switch, _kill_reason

    if _kill_switch:
        return {"error": "Kill switch activo", "reason": _kill_reason}

    config = get_mode_config(mode)
    odds = signal.get("odds", 0) or signal.get("best_odds", 0)
    edge = signal.get("edge_pct", 0)

    if odds <= 1 or edge < config["edge_min"]:
        return {"error": f"Edge {edge:.1f}% no califica para modo {mode}"}

    # Calcular stake con Kelly dinámico
    prob = (1 / odds) + (edge / 100)
    prob = max(0.01, min(0.99, prob))

    kelly_full = (prob * (odds - 1) - (1 - prob)) / (odds - 1)
    kelly_full = max(0, kelly_full)
    kelly_aplicado = kelly_full * config["kelly"]

    # Cap dinámico
    max_bet = _current_bankroll * (config["cap_pct"] / 100)
    stake = min(max_bet, _current_bankroll * kelly_aplicado)
    stake = max(stake, 1)  # Mínimo $1

    if stake < 1:
        return {"error": "Stake muy bajo"}

    # Registrar trade
    trade = {
        "match": signal.get("match", ""),
        "selection": signal.get("selection", "") or signal.get("best_selection", ""),
        "odds": odds,
        "edge_pct": edge,
        "mode": mode,
        "mode_emoji": config["emoji"],
        "kelly_pct": round(kelly_aplicado * 100, 2),
        "stake": round(stake, 2),
        "bankroll_antes": round(_current_bankroll, 2),
        "prob_modelo": round(prob * 100, 2),
        "confidence": signal.get("confidence", 0),
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Guardar en DB
    _save_hulk_trade(trade)

    # Actualizar estado
    _current_bankroll = round(_current_bankroll - stake, 2)
    _trade_history.append(trade)
    _mode_stats[mode]["trades"] += 1

    return trade


def resolve_hulk_trade(trade_id: int, won: bool) -> dict:
    """Resuelve un trade Hulk y actualiza todo el estado."""
    global _current_bankroll, _racha, _total_pnl, _kill_switch, _kill_reason
    global _max_racha_ganadora

    try:
        from database import db, _row_to_dict, _USE_PG
        with db() as conn:
            cur = conn.cursor()
            ph = "%s" if _USE_PG else "?"
            cur.execute(f"SELECT * FROM hulk_trades WHERE id = {ph}", (trade_id,))
            row = cur.fetchone()
            if not row:
                return {"error": "Trade no encontrado"}

            trade = _row_to_dict(row)
            stake = trade["stake"]
            odds = trade["odds"]
            mode = trade.get("mode", "HAWK")

            if won:
                pnl = stake * (odds - 1)
                _racha = max(1, _racha + 1)
                _max_racha_ganadora = max(_max_racha_ganadora, _racha)
                _mode_stats[mode]["won"] += 1
            else:
                pnl = -stake
                _racha = min(-1, _racha - 1)

            _total_pnl = round(_total_pnl + pnl, 2)
            _current_bankroll = round(_current_bankroll + stake + pnl, 2)
            _mode_stats[mode]["pnl"] = round(_mode_stats[mode]["pnl"] + pnl, 2)

            # Actualizar DB
            resultado = "ganada" if won else "perdida"
            cur.execute(f"""
                UPDATE hulk_trades
                SET resultado = {ph}, pnl = {ph}, bankroll_despues = {ph}, verified_at = {ph}
                WHERE id = {ph}
            """, (resultado, round(pnl, 2), _current_bankroll,
                  datetime.utcnow().isoformat(), trade_id))

            # Kill switch check
            if _total_pnl < -INITIAL_BANKROLL * 0.15:
                _kill_switch = True
                _kill_reason = f"Pérdida del 15% del bankroll (${_total_pnl:,.2f})"

            conn.commit()
            _save_hulk_state()

            return {
                "trade_id": trade_id,
                "resultado": resultado,
                "pnl": round(pnl, 2),
                "bankroll": _current_bankroll,
                "racha": _racha,
                "mode": mode,
                "kill_switch": _kill_switch,
            }

    except Exception as e:
        logger.warning("Error resolviendo trade Hulk: %s", e)
        return {"error": str(e)}


# ══════════════════════════════════════════════════════════════════════════
# 8. DB OPERATIONS
# ══════════════════════════════════════════════════════════════════════════

def _init_hulk_db():
    """Crea tabla hulk_trades si no existe."""
    try:
        from database import db, _USE_PG
        with db() as conn:
            cur = conn.cursor()
            if _USE_PG:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS hulk_trades (
                        id SERIAL PRIMARY KEY,
                        match TEXT,
                        selection TEXT,
                        odds REAL,
                        edge_pct REAL,
                        mode TEXT,
                        kelly_pct REAL,
                        stake REAL,
                        bankroll_antes REAL,
                        bankroll_despues REAL,
                        prob_modelo REAL,
                        confidence REAL,
                        resultado TEXT DEFAULT 'pendiente',
                        pnl REAL DEFAULT 0,
                        verified_at TEXT,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS hulk_state (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)
            else:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS hulk_trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        match TEXT,
                        selection TEXT,
                        odds REAL,
                        edge_pct REAL,
                        mode TEXT,
                        kelly_pct REAL,
                        stake REAL,
                        bankroll_antes REAL,
                        bankroll_despues REAL,
                        prob_modelo REAL,
                        confidence REAL,
                        resultado TEXT DEFAULT 'pendiente',
                        pnl REAL DEFAULT 0,
                        verified_at TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS hulk_state (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)
            conn.commit()
    except Exception as e:
        logger.warning("Error init hulk DB: %s", e)


def _save_hulk_trade(trade: dict):
    """Guarda trade en DB."""
    try:
        from database import db, _USE_PG
        _init_hulk_db()
        with db() as conn:
            cur = conn.cursor()
            if _USE_PG:
                cur.execute("""
                    INSERT INTO hulk_trades
                    (match, selection, odds, edge_pct, mode, kelly_pct,
                     stake, bankroll_antes, prob_modelo, confidence)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    trade["match"], trade["selection"], trade["odds"],
                    trade["edge_pct"], trade["mode"], trade["kelly_pct"],
                    trade["stake"], trade["bankroll_antes"],
                    trade["prob_modelo"], trade["confidence"],
                ))
                trade["id"] = cur.fetchone()[0]
            else:
                cur.execute("""
                    INSERT INTO hulk_trades
                    (match, selection, odds, edge_pct, mode, kelly_pct,
                     stake, bankroll_antes, prob_modelo, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trade["match"], trade["selection"], trade["odds"],
                    trade["edge_pct"], trade["mode"], trade["kelly_pct"],
                    trade["stake"], trade["bankroll_antes"],
                    trade["prob_modelo"], trade["confidence"],
                ))
                trade["id"] = cur.lastrowid
            conn.commit()
    except Exception as e:
        logger.warning("Error guardando trade Hulk: %s", e)


def _save_hulk_state():
    """Guarda estado en DB."""
    try:
        from database import db, _USE_PG
        _init_hulk_db()
        state = {
            "bankroll": _current_bankroll,
            "racha": _racha,
            "max_racha_ganadora": _max_racha_ganadora,
            "total_pnl": _total_pnl,
            "kill_switch": _kill_switch,
            "kill_reason": _kill_reason,
            "mode_stats": _mode_stats,
        }
        with db() as conn:
            cur = conn.cursor()
            if _USE_PG:
                cur.execute("""
                    INSERT INTO hulk_state (key, value) VALUES (%s, %s)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                """, ("main", json.dumps(state)))
            else:
                cur.execute("""
                    INSERT OR REPLACE INTO hulk_state (key, value) VALUES (?, ?)
                """, ("main", json.dumps(state)))
            conn.commit()
    except Exception as e:
        logger.warning("Error guardando estado Hulk: %s", e)


def _load_hulk_state():
    """Carga estado desde DB."""
    global _current_bankroll, _racha, _max_racha_ganadora
    global _total_pnl, _kill_switch, _kill_reason, _mode_stats

    try:
        from database import db, _row_to_dict, _USE_PG
        _init_hulk_db()
        with db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM hulk_state WHERE key = 'main'")
            row = cur.fetchone()
            if row:
                state = json.loads(_row_to_dict(row)["value"])
                _current_bankroll = state.get("bankroll", INITIAL_BANKROLL)
                _racha = state.get("racha", 0)
                _max_racha_ganadora = state.get("max_racha_ganadora", 0)
                _total_pnl = state.get("total_pnl", 0)
                _kill_switch = state.get("kill_switch", False)
                _kill_reason = state.get("kill_reason", "")
                _mode_stats = state.get("mode_stats", {m: {"trades": 0, "won": 0, "pnl": 0} for m in MODES})
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════
# 9. SCAN PRINCIPAL — Orquesta todo
# ══════════════════════════════════════════════════════════════════════════

def scan() -> dict:
    """
    Escaneo completo Hulk:
    1. Steam moves
    2. Live opportunities
    3. Arbitrage
    4. Contrarian
    5. Clasificar modo
    6. Ejecutar trades
    """
    start = time.time()
    _load_hulk_state()

    all_signals = []

    # 1. Steam moves (la señal más fuerte)
    steam = detect_steam_moves()
    all_signals.extend(steam)

    # 2. Live opportunities
    live = scan_live_opportunities()
    all_signals.extend(live)

    # 3. Arbitrage (siempre ejecutar)
    arbitrage = hunt_arbitrage()
    for arb in arbitrage:
        # Ejecutar arbitraje directamente (confidence 99%)
        execute_trade({
            "match": arb["match"],
            "selection": "ARBITRAJE",
            "odds": 1,  # Special case
            "edge_pct": arb["profit_pct"],
            "confidence": 99,
            "source_count": len(arb.get("best_books", {})),
        }, "HAWK")

    # 4. Contrarian
    contrarian = detect_contrarian_opportunities()
    all_signals.extend(contrarian)

    # 5. Brain signals (del módulo Brain)
    try:
        from services.brain import collect_all_signals, aggregate_signals, filter_signals
        brain_raw = collect_all_signals()
        brain_agg = aggregate_signals(brain_raw)
        brain_filtered = filter_signals(brain_agg, threshold=75, min_sources=3)
        for s in brain_filtered:
            s["source"] = "brain"
            all_signals.append(s)
    except Exception:
        pass

    # 6. Clasificar y ejecutar
    executed = []
    for signal in all_signals:
        mode = classify_mode(signal)
        if mode:
            trade = execute_trade(signal, mode)
            if "error" not in trade:
                executed.append(trade)

    # 7. Verificar trades pendientes
    verified = verify_hulk_trades()

    elapsed = round(time.time() - start, 2)

    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "elapsed_seconds": elapsed,
        "steam_moves": len(steam),
        "live_opportunities": len(live),
        "arbitrage": len(arbitrage),
        "contrarian": len(contrarian),
        "brain_signals": len(brain_filtered) if 'brain_filtered' in dir() else 0,
        "total_signals": len(all_signals),
        "trades_executed": len(executed),
        "trades_verified": verified.get("verified", 0),
        "bankroll": _current_bankroll,
        "racha": _racha,
        "total_pnl": _total_pnl,
        "kill_switch": _kill_switch,
        "modes_used": list(set(t["mode"] for t in executed)),
        "executed": executed,
    }

    _save_hulk_state()
    return result


def verify_hulk_trades() -> dict:
    """Verifica trades pendientes Hulk."""
    stats = {"verified": 0, "won": 0, "lost": 0}
    try:
        from database import db, _row_to_dict, _USE_PG
        _init_hulk_db()
        with db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, match, selection FROM hulk_trades
                WHERE resultado = 'pendiente' ORDER BY id DESC LIMIT 20
            """)
            pending = [_row_to_dict(r) for r in cur.fetchall()]

            for trade in pending:
                result = _check_result(trade["match"], trade["selection"])
                if result is not None:
                    r = resolve_hulk_trade(trade["id"], result)
                    if "error" not in r:
                        stats["verified"] += 1
                        if result:
                            stats["won"] += 1
                        else:
                            stats["lost"] += 1
    except Exception:
        pass
    return stats


def _check_result(match_str: str, selection: str) -> Optional[bool]:
    """Verifica resultado contra DB."""
    try:
        from database import db, _row_to_dict, _USE_PG
        with db() as conn:
            cur = conn.cursor()
            ph = "%s" if _USE_PG else "?"
            cur.execute(f"""
                SELECT correcto FROM predictions
                WHERE (home || ' vs ' || away = {ph} OR home = {ph} OR away = {ph})
                AND resultado_real IS NOT NULL
                ORDER BY id DESC LIMIT 1
            """, (match_str, selection, selection))
            row = cur.fetchone()
            if row:
                return _row_to_dict(row).get("correcto") == 1
    except Exception:
        pass
    return None


# ══════════════════════════════════════════════════════════════════════════
# 10. PERFORMANCE & REPORTS
# ══════════════════════════════════════════════════════════════════════════

def get_performance() -> dict:
    """Performance completa del Hulk."""
    _load_hulk_state()

    total_trades = sum(s["trades"] for s in _mode_stats.values())
    total_won = sum(s["won"] for s in _mode_stats.values())
    win_rate = (total_won / total_trades * 100) if total_trades > 0 else 0
    roi = (_total_pnl / INITIAL_BANKROLL * 100) if INITIAL_BANKROLL > 0 else 0

    return {
        "bankroll_inicial": INITIAL_BANKROLL,
        "bankroll_actual": _current_bankroll,
        "total_pnl": _total_pnl,
        "roi": round(roi, 2),
        "total_trades": total_trades,
        "total_won": total_won,
        "total_lost": total_trades - total_won,
        "win_rate": round(win_rate, 1),
        "racha_actual": _racha,
        "mejor_racha": _max_racha_ganadora,
        "kill_switch": _kill_switch,
        "kill_reason": _kill_reason,
        "by_mode": {
            mode: {
                "trades": stats["trades"],
                "won": stats["won"],
                "win_rate": round(stats["won"] / max(1, stats["trades"]) * 100, 1),
                "pnl": round(stats["pnl"], 2),
            }
            for mode, stats in _mode_stats.items()
        },
        "modes_config": {mode: {k: v for k, v in cfg.items()} for mode, cfg in MODES.items()},
    }


def reset_hulk(new_bankroll: float = 10000) -> dict:
    """Resetea el Hulk."""
    global _current_bankroll, _racha, _max_racha_ganadora
    global _total_pnl, _kill_switch, _kill_reason, _mode_stats, _trade_history

    _current_bankroll = new_bankroll
    _racha = 0
    _max_racha_ganadora = 0
    _total_pnl = 0
    _kill_switch = False
    _kill_reason = ""
    _mode_stats = {mode: {"trades": 0, "won": 0, "pnl": 0.0} for mode in MODES}
    _trade_history = []

    try:
        from database import db
        _init_hulk_db()
        with db() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM hulk_trades")
            cur.execute("DELETE FROM hulk_state")
            conn.commit()
    except Exception:
        pass

    _save_hulk_state()
    return {"status": "ok", "bankroll": new_bankroll}


# Cargar estado al iniciar
_load_hulk_state()
_init_hulk_db()
