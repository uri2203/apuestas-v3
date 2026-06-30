"""
Agente Brain — Cerebro autónomo que:
1. RECOLECTA señales de todos los módulos del sistema
2. AGREGA en un score compuesto ponderado
3. FILTRA por umbral de confianza (85%)
4. AUTO-SIMULA trades con Kelly sizing
5. APRENDE de resultados para mejorar pesos

Flujo:
  brain.scan() → brain.aggregate() → brain.filter() → brain.simulate()
  brain.verify() → brain.learn() → brain.update_weights()

Cada paso es independiente y testeable.
"""
import os
import json
import math
import time
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════

CONFIDENCE_THRESHOLD = 85.0  # Umbral mínimo para activar señal
MIN_SIGNAL_SOURCES = 3       # Mínimo de fuentes que deben confirmar
MAX_BET_PCT_BANKROLL = 5.0   # Máximo 5% del bankroll por apuesta
KELLY_FRACTION = 0.25        # Quarter Kelly (conservador)
SCAN_INTERVAL_HOURS = 2      # Cada cuántas horas escanea

# Pesos por defecto de cada fuente de señal (suma = 100)
DEFAULT_WEIGHTS = {
    "value_bet": 25,      # Edge del modelo vs cuota
    "sharp_money": 20,    # Dinero profesional confirmando
    "ml_prediction": 20,  # Predicción ML v2
    "nlp_sentiment": 10,  # Noticias/lesiones
    "cross_market": 10,   # Inconsistencia entre mercados
    "monte_carlo": 10,    # Simulaciones Poisson
    "clv": 5,             # Closing Line Value
}

# Pesos dinámicos (se actualizan con el aprendizaje)
_dynamic_weights = dict(DEFAULT_WEIGHTS)

# Historial de performance por fuente (acumulado)
_source_performance = {
    src: {"correct": 0, "total": 0, "profit": 0.0}
    for src in DEFAULT_WEIGHTS
}

# Último escaneo
_last_scan = None
_last_signals = []


# ══════════════════════════════════════════════════════════════════════════
# 1. RECOLECTOR — Recopila señales de todos los módulos
# ══════════════════════════════════════════════════════════════════════════

def _collect_value_bets() -> list[dict]:
    """Recolecta value bets con edge significativo."""
    signals = []
    try:
        from services.value_engine import analizar_value
        from services.deportes import get_odds_upcoming, get_any_odds_key

        key = get_any_odds_key()
        if not key:
            return []

        odds = get_odds_upcoming(api_key=key)
        if not odds:
            return []

        for match in odds[:30]:  # Limitar a 30 partidos
            home = match.get("home_team", "")
            away = match.get("away_team", "")
            if not home or not away:
                continue

            for book in match.get("bookmakers", []):
                book_name = book.get("title", "")
                for market in book.get("markets", []):
                    if market.get("key") != "h2h":
                        continue
                    outcomes = {o["name"]: o["price"] for o in market.get("outcomes", [])}
                    if len(outcomes) < 2:
                        continue

                    # Analizar cada outcome
                    for sel, odds_val in outcomes.items():
                        # Probabilidad implícita como proxy del modelo
                        prob = 1.0 / odds_val if odds_val > 1 else 0.5
                        analysis = analizar_value(prob, odds_val)
                        edge = analysis.get("edge_modelo_pct", 0)

                        if edge >= 5.0:  # Mínimo 5% edge
                            signals.append({
                                "source": "value_bet",
                                "match": f"{home} vs {away}",
                                "selection": sel,
                                "odds": odds_val,
                                "bookmaker": book_name,
                                "edge_pct": round(edge, 2),
                                "confidence": min(95, max(50, 60 + edge * 2)),
                                "home": home,
                                "away": away,
                                "timestamp": datetime.utcnow().isoformat(),
                            })
    except Exception as e:
        logger.warning("Error recolectando value bets: %s", e)
    return signals


def _collect_sharp_money() -> list[dict]:
    """Recolecta señales de sharp money."""
    signals = []
    try:
        from services.deportes import get_odds_upcoming, get_any_odds_key

        key = get_any_odds_key()
        if not key:
            return []

        odds = get_odds_upcoming(api_key=key)
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

            # Detectar movimiento de líneas
            h2h_prices = {}
            for book in books:
                for market in book.get("markets", []):
                    if market.get("key") != "h2h":
                        continue
                    for o in market.get("outcomes", []):
                        name = o["name"]
                        price = o["price"]
                        if name not in h2h_prices:
                            h2h_prices[name] = []
                        h2h_prices[name].append({"book": book.get("title", ""), "price": price})

            # Calcular variación de precios
            for sel, prices in h2h_prices.items():
                if len(prices) < 2:
                    continue
                price_list = [p["price"] for p in prices]
                avg_price = sum(price_list) / len(price_list)
                variance = max(price_list) - min(price_list)

                # High variance = potential sharp action
                if variance > 0.3:
                    sharp_score = min(95, 50 + variance * 30)
                    signals.append({
                        "source": "sharp_money",
                        "match": f"{home} vs {away}",
                        "selection": sel,
                        "odds": avg_price,
                        "bookmaker": prices[0]["book"],
                        "edge_pct": round(variance * 5, 2),
                        "confidence": round(sharp_score, 2),
                        "home": home,
                        "away": away,
                        "variance": round(variance, 3),
                        "timestamp": datetime.utcnow().isoformat(),
                    })
    except Exception as e:
        logger.warning("Error recolectando sharp money: %s", e)
    return signals


def _collect_ml_predictions() -> list[dict]:
    """Recolecta predicciones del modelo ML."""
    signals = []
    try:
        from services.ml_predictor import auto_train
        result = auto_train("liga_mx")
        if result.get("error"):
            return []

        for pred in result.get("predicciones", []):
            conf = pred.get("confianza_pct", 0)
            if conf >= 55:
                signals.append({
                    "source": "ml_prediction",
                    "match": f"{pred.get('home', '')} vs {pred.get('away', '')}",
                    "selection": pred.get("pronostico", ""),
                    "odds": 0,  # Se llenará al cruzar con odds
                    "bookmaker": "",
                    "edge_pct": round(conf - 50, 2),  # Edge = conf - 50
                    "confidence": min(95, conf),
                    "home": pred.get("home", ""),
                    "away": pred.get("away", ""),
                    "probs": pred.get("probs", {}),
                    "timestamp": datetime.utcnow().isoformat(),
                })
    except Exception as e:
        logger.warning("Error recolectando ML predictions: %s", e)
    return signals


def _collect_nlp_signals() -> list[dict]:
    """Recolecta señales de NLP/sentimiento."""
    signals = []
    try:
        from services.nlp_sentiment import scan_all_news
        news = scan_all_news()
        if not news:
            return []

        for article in news[:15]:
            teams = article.get("equipos_detectados", [])
            injury_score = article.get("score_lesion", 0)
            sentiment = article.get("sentimiento", 0)

            if abs(injury_score) > 0.3 or abs(sentiment) > 0.3:
                signals.append({
                    "source": "nlp_sentiment",
                    "match": " vs ".join(teams) if len(teams) >= 2 else teams[0] if teams else "",
                    "selection": "NLP_ALERT",
                    "odds": 0,
                    "bookmaker": "",
                    "edge_pct": round(abs(injury_score + sentiment) * 10, 2),
                    "confidence": min(90, 50 + abs(injury_score) * 30 + abs(sentiment) * 20),
                    "home": teams[0] if teams else "",
                    "away": teams[1] if len(teams) > 1 else "",
                    "headline": article.get("titulo", "")[:100],
                    "timestamp": datetime.utcnow().isoformat(),
                })
    except Exception as e:
        logger.warning("Error recolectando NLP: %s", e)
    return signals


def _collect_cross_market() -> list[dict]:
    """Recolecta inconsistencias cross-market."""
    signals = []
    try:
        from services.cross_market import detectar_inconsistencias
        result = detectar_inconsistencias()
        alerts = result.get("alertas", [])
        for alert in alerts[:10]:
            signals.append({
                "source": "cross_market",
                "match": alert.get("partido", ""),
                "selection": alert.get("mercado", ""),
                "odds": 0,
                "bookmaker": "",
                "edge_pct": round(alert.get("diferencia_pct", 0), 2),
                "confidence": min(85, 50 + alert.get("diferencia_pct", 0) * 3),
                "home": "",
                "away": "",
                "detail": alert.get("detalle", ""),
                "timestamp": datetime.utcnow().isoformat(),
            })
    except Exception as e:
        logger.warning("Error recolectando cross-market: %s", e)
    return signals


def _collect_monte_carlo() -> list[dict]:
    """Recolecta señales de Monte Carlo."""
    signals = []
    try:
        from services.deportes import get_odds_upcoming, get_any_odds_key
        from services.motor_avanzado import simulacion_monte_carlo_poisson

        key = get_any_odds_key()
        if not key:
            return []

        odds = get_odds_upcoming(api_key=key)
        if not odds:
            return []

        for match in odds[:10]:
            home = match.get("home_team", "")
            away = match.get("away_team", "")
            if not home or not away:
                continue

            books = match.get("bookmakers", [])
            if not books:
                continue

            # Get average odds
            h2h_prices = {"1": [], "X": [], "2": []}
            for book in books:
                for market in book.get("markets", []):
                    if market.get("key") != "h2h":
                        continue
                    for o in market.get("outcomes", []):
                        if o["name"] == home:
                            h2h_prices["1"].append(o["price"])
                        elif o["name"] == "Draw":
                            h2h_prices["X"].append(o["price"])
                        elif o["name"] == away:
                            h2h_prices["2"].append(o["price"])

            avg_odds = {}
            for k, v in h2h_prices.items():
                if v:
                    avg_odds[k] = sum(v) / len(v)

            if len(avg_odds) < 2:
                continue

            # Simular con Poisson (parámetros estimados)
            prob_home = 1 / avg_odds.get("1", 3) if avg_odds.get("1") else 0.33
            prob_draw = 1 / avg_odds.get("X", 3) if avg_odds.get("X") else 0.33
            prob_away = 1 / avg_odds.get("2", 3) if avg_odds.get("2") else 0.33

            # Normalizar
            total = prob_home + prob_draw + prob_away
            if total > 0:
                prob_home /= total
                prob_draw /= total
                prob_away /= total

            # Detectar edge si modelo difiere del mercado
            for sel, prob in [("1", prob_home), ("X", prob_draw), ("2", prob_away)]:
                market_prob = 1 / avg_odds.get(sel, 3) if avg_odds.get(sel) else 0.33
                edge = (prob - market_prob) * 100
                if edge > 5:
                    signals.append({
                        "source": "monte_carlo",
                        "match": f"{home} vs {away}",
                        "selection": sel,
                        "odds": avg_odds.get(sel, 0),
                        "bookmaker": "PROMEDIO",
                        "edge_pct": round(edge, 2),
                        "confidence": min(85, 50 + edge * 2),
                        "home": home,
                        "away": away,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
    except Exception as e:
        logger.warning("Error recolectando Monte Carlo: %s", e)
    return signals


def collect_all_signals() -> list[dict]:
    """Recolecta TODAS las señales de TODOS los módulos."""
    all_signals = []
    collectors = [
        _collect_value_bets,
        _collect_sharp_money,
        _collect_ml_predictions,
        _collect_nlp_signals,
        _collect_cross_market,
        _collect_monte_carlo,
    ]
    for collector in collectors:
        try:
            signals = collector()
            all_signals.extend(signals)
        except Exception as e:
            logger.warning("Error en collector %s: %s", collector.__name__, e)
    return all_signals


# ══════════════════════════════════════════════════════════════════════════
# 2. AGREGADOR — Combina señales del mismo partido en un score compuesto
# ══════════════════════════════════════════════════════════════════════════

def aggregate_signals(signals: list[dict]) -> list[dict]:
    """
    Agrupa señales por partido y calcula un score compuesto.
    Cada fuente contribuye al score total según su peso.
    """
    # Agrupar por partido
    matches = {}
    for s in signals:
        key = s.get("match", "").strip()
        if not key:
            continue
        if key not in matches:
            matches[key] = []
        matches[key].append(s)

    results = []
    for match_key, match_signals in matches.items():
        # Calcular score compuesto
        total_score = 0
        total_weight = 0
        sources_used = []
        edges = []
        best_odds = 0
        best_selection = ""
        best_bookmaker = ""

        for s in match_signals:
            src = s.get("source", "")
            weight = _dynamic_weights.get(src, 10)
            conf = s.get("confidence", 50)
            edge = s.get("edge_pct", 0)

            # Score de esta fuente = confianza × peso
            source_score = (conf / 100) * weight
            total_score += source_score
            total_weight += weight
            sources_used.append(src)
            edges.append(edge)

            if s.get("odds", 0) > best_odds:
                best_odds = s["odds"]
                best_selection = s.get("selection", "")
                best_bookmaker = s.get("bookmaker", "")

        # Score final normalizado a 0-100
        if total_weight > 0:
            composite_score = (total_score / total_weight) * 100
        else:
            composite_score = 0

        # Bonus por convergencia de fuentes
        unique_sources = len(set(sources_used))
        if unique_sources >= 3:
            convergence_bonus = min(10, (unique_sources - 2) * 3)
            composite_score = min(100, composite_score + convergence_bonus)

        # Promedio de edges
        avg_edge = sum(edges) / len(edges) if edges else 0

        results.append({
            "match": match_key,
            "home": match_signals[0].get("home", ""),
            "away": match_signals[0].get("away", ""),
            "composite_score": round(composite_score, 2),
            "avg_edge_pct": round(avg_edge, 2),
            "max_edge_pct": round(max(edges) if edges else 0, 2),
            "sources": list(set(sources_used)),
            "source_count": unique_sources,
            "best_odds": best_odds,
            "best_selection": best_selection,
            "best_bookmaker": best_bookmaker,
            "signals_detail": match_signals,
            "timestamp": datetime.utcnow().isoformat(),
        })

    # Ordenar por score descendente
    results.sort(key=lambda x: x["composite_score"], reverse=True)
    return results


# ══════════════════════════════════════════════════════════════════════════
# 3. FILTRO — Solo pasa señales con score >= umbral
# ══════════════════════════════════════════════════════════════════════════

def filter_signals(aggregated: list[dict],
                   threshold: float = CONFIDENCE_THRESHOLD,
                   min_sources: int = MIN_SIGNAL_SOURCES) -> list[dict]:
    """
    Filtra señales por:
    1. Score compuesto >= umbral
    2. Al menos N fuentes distintas confirmando
    """
    filtered = []
    for signal in aggregated:
        score = signal.get("composite_score", 0)
        sources = signal.get("source_count", 0)

        if score >= threshold and sources >= min_sources:
            signal["passed_filter"] = True
            signal["filter_reason"] = f"Score {score:.1f} >= {threshold} con {sources} fuentes"
            filtered.append(signal)
        else:
            signal["passed_filter"] = False
            reasons = []
            if score < threshold:
                reasons.append(f"score {score:.1f} < {threshold}")
            if sources < min_sources:
                reasons.append(f"fuentes {sources} < {min_sources}")
            signal["filter_reason"] = " / ".join(reasons)

    return filtered


# ══════════════════════════════════════════════════════════════════════════
# 4. AUTO-SIMULADOR — Registra trades simulados con Kelly sizing
# ══════════════════════════════════════════════════════════════════════════

def simulate_trades(filtered_signals: list[dict],
                    bankroll: float = 0) -> list[dict]:
    """
    Para cada señal filtrada:
    1. Calcula stake óptimo con Kelly
    2. Registra en simulated_trades
    3. Retorna lista de trades ejecutados
    """
    if bankroll <= 0:
        try:
            from database import get_bankroll_actual
            bankroll = float(get_bankroll_actual())
        except Exception:
            bankroll = 10000  # Default

    trades = []
    for signal in filtered_signals:
        try:
            odds = signal.get("best_odds", 0)
            if odds <= 1:
                continue

            # Estimar probabilidad del modelo
            edge = signal.get("avg_edge_pct", 0) / 100
            prob_modelo = (1 / odds) + edge  # Prob justa del modelo
            prob_modelo = max(0.01, min(0.99, prob_modelo))

            # Kelly fraccionado
            from services.value_engine import kelly_fraccionado
            kelly = kelly_fraccionado(prob_modelo, odds, KELLY_FRACTION, bankroll)
            stake = kelly.get("stake_sugerido", 0)

            # Cap maximum bet
            max_bet = bankroll * (MAX_BET_PCT_BANKROLL / 100)
            stake = min(stake, max_bet)

            if stake < 1:  # Mínimo $1
                continue

            trade = {
                "match": signal.get("match", ""),
                "liga": "",
                "selection": signal.get("best_selection", ""),
                "bookmaker": signal.get("best_bookmaker", ""),
                "odds": odds,
                "edge_pct": signal.get("avg_edge_pct", 0),
                "confidence_score": signal.get("composite_score", 0),
                "stake": round(stake, 2),
                "kelly_pct": kelly.get("kelly_aplicado_pct", 0),
                "prob_modelo": round(prob_modelo * 100, 2),
                "bankroll": round(bankroll, 2),
                "sources": signal.get("sources", []),
                "source_count": signal.get("source_count", 0),
                "status": "pending",
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Registrar en DB
            _save_simulated_trade(trade)
            trades.append(trade)

        except Exception as e:
            logger.warning("Error simulando trade: %s", e)

    return trades


def _save_simulated_trade(trade: dict):
    """Guarda trade simulado en la DB."""
    try:
        from database import db
        with db() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO simulated_trades
                (partido, liga, seleccion, casa, cuota, edge_pct,
                 stake_simulado, bankroll_al_momento, resultado_simulado, pnl_real)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pendiente', 0)
            """, (
                trade["match"],
                trade.get("liga", ""),
                trade["selection"],
                trade["bookmaker"],
                trade["odds"],
                trade["edge_pct"],
                trade["stake"],
                trade["bankroll"],
            ))
    except Exception as e:
        logger.warning("Error guardando trade simulado: %s", e)


# ══════════════════════════════════════════════════════════════════════════
# 5. VERIFICADOR — Compara trades pendientes con resultados reales
# ══════════════════════════════════════════════════════════════════════════

def verify_pending_trades() -> dict:
    """
    Verifica trades pendientes contra resultados reales.
    Actualiza P&L y retorna estadísticas.
    """
    stats = {"verified": 0, "won": 0, "lost": 0, "pending": 0, "pnl": 0.0}

    try:
        from database import db, _row_to_dict, PH
        with db() as conn:
            cur = conn.cursor()
            cur.execute(f"""
                SELECT id, partido, seleccion, cuota, edge_pct, stake_simulado,
                       confidence_score
                FROM simulated_trades
                WHERE resultado_simulado = 'pendiente'
                ORDER BY id DESC
                LIMIT 50
            """)
            pending = [_row_to_dict(r) for r in cur.fetchall()]

            for trade in pending:
                # Intentar verificar contra predictions o resultados reales
                result = _check_match_result(trade["partido"], trade["seleccion"])

                if result is not None:
                    # Calcular P&L
                    if result:
                        pnl = trade["stake_simulado"] * (trade["cuota"] - 1)
                        stats["won"] += 1
                    else:
                        pnl = -trade["stake_simulado"]
                        stats["lost"] += 1

                    stats["pnl"] += pnl
                    stats["verified"] += 1

                    # Actualizar en DB
                    cur.execute(f"""
                        UPDATE simulated_trades
                        SET resultado_simulado = ?, pnl_real = ?
                        WHERE id = ?
                    """, ("ganada" if result else "perdida", round(pnl, 2), trade["id"]))

                    # Actualizar performance por fuente
                    _update_source_performance(trade, result)
                else:
                    stats["pending"] += 1

    except Exception as e:
        logger.warning("Error verificando trades: %s", e)

    return stats


def _check_match_result(match_str: str, selection: str) -> Optional[bool]:
    """Verifica si un partido ya tiene resultado."""
    try:
        from database import db, _row_to_dict
        with db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT pronostico, resultado_real, correcto
                FROM predictions
                WHERE home || ' vs ' || away = ?
                AND resultado_real IS NOT NULL
                ORDER BY id DESC LIMIT 1
            """, (match_str,))
            row = cur.fetchone()
            if row:
                r = _row_to_dict(row)
                return r.get("correcto") == 1
    except Exception:
        pass
    return None


def _update_source_performance(trade: dict, won: bool):
    """Actualiza el historial de performance por fuente."""
    try:
        sources = trade.get("sources", [])
        if isinstance(sources, str):
            sources = json.loads(sources) if sources.startswith("[") else [sources]

        for src in sources:
            if src in _source_performance:
                _source_performance[src]["total"] += 1
                if won:
                    _source_performance[src]["correct"] += 1
                    _source_performance[src]["profit"] += trade["stake_simulado"] * (trade["cuota"] - 1)
                else:
                    _source_performance[src]["profit"] -= trade["stake_simulado"]
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════
# 6. APRENDIZAJE — Ajusta pesos dinámicamente según performance
# ══════════════════════════════════════════════════════════════════════════

def learn_from_results() -> dict:
    """
    Analiza performance histórica y ajusta pesos.
    Fuentes con mejor accuracy → más peso
    Fuentes con peor accuracy → menos peso
    """
    global _dynamic_weights

    changes = []
    for src, perf in _source_performance.items():
        if perf["total"] < 5:  # Mínimo 5 muestras para aprender
            continue

        accuracy = perf["correct"] / perf["total"] * 100
        roi = perf["profit"] / max(1, perf["total"]) * 100

        old_weight = _dynamic_weights.get(src, 10)
        new_weight = old_weight

        # Ajustar peso según accuracy
        if accuracy >= 65:
            # Buena performance → aumentar peso (máximo +30%)
            new_weight = min(old_weight * 1.3, old_weight + 10)
        elif accuracy <= 45:
            # Mala performance → reducir peso (mínimo -30%)
            new_weight = max(old_weight * 0.7, old_weight - 10)
        elif accuracy >= 55:
            # Performance aceptable → ajuste leve
            new_weight = old_weight * 1.1

        new_weight = max(5, min(40, new_weight))  # Clamp entre 5 y 40
        new_weight = round(new_weight, 1)

        if new_weight != old_weight:
            changes.append({
                "source": src,
                "old_weight": old_weight,
                "new_weight": new_weight,
                "accuracy": round(accuracy, 1),
                "roi": round(roi, 2),
                "samples": perf["total"],
            })
            _dynamic_weights[src] = new_weight

    # Normalizar pesos para que sumen 100
    total = sum(_dynamic_weights.values())
    if total > 0:
        for src in _dynamic_weights:
            _dynamic_weights[src] = round(_dynamic_weights[src] / total * 100, 1)

    return {
        "changes": changes,
        "current_weights": dict(_dynamic_weights),
        "source_performance": {
            src: {
                "accuracy": round(perf["correct"] / max(1, perf["total"]) * 100, 1),
                "total": perf["total"],
                "profit": round(perf["profit"], 2),
            }
            for src, perf in _source_performance.items()
            if perf["total"] > 0
        },
    }


# ══════════════════════════════════════════════════════════════════════════
# 7. SCAN PRINCIPAL — Orquesta todo el flujo
# ══════════════════════════════════════════════════════════════════════════

def scan(threshold: float = CONFIDENCE_THRESHOLD) -> dict:
    """
    Flujo completo:
    1. Recolección → 2. Agregación → 3. Filtrado → 4. Simulación
    """
    global _last_scan, _last_signals

    start = time.time()

    # 1. Recolección
    raw_signals = collect_all_signals()

    # 2. Agregación
    aggregated = aggregate_signals(raw_signals)

    # 3. Filtrado
    filtered = filter_signals(aggregated, threshold=threshold)

    # 4. Simulación
    trades = simulate_trades(filtered)

    elapsed = round(time.time() - start, 2)

    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "elapsed_seconds": elapsed,
        "raw_signals_count": len(raw_signals),
        "aggregated_matches": len(aggregated),
        "filtered_signals": len(filtered),
        "trades_simulated": len(trades),
        "threshold": threshold,
        "weights": dict(_dynamic_weights),
        "signals": filtered,
        "trades": trades,
    }

    _last_scan = result
    _last_signals = filtered

    return result


def get_status() -> dict:
    """Estado actual del agente Brain."""
    return {
        "status": "active",
        "threshold": CONFIDENCE_THRESHOLD,
        "min_sources": MIN_SIGNAL_SOURCES,
        "kelly_fraction": KELLY_FRACTION,
        "max_bet_pct": MAX_BET_PCT_BANKROLL,
        "current_weights": dict(_dynamic_weights),
        "source_performance": {
            src: {
                "accuracy": round(perf["correct"] / max(1, perf["total"]) * 100, 1),
                "total": perf["total"],
                "profit": round(perf["profit"], 2),
            }
            for src, perf in _source_performance.items()
        },
        "last_scan": _last_scan.get("timestamp") if _last_scan else None,
        "last_signals_count": len(_last_signals),
    }


def get_history(limit: int = 50) -> list[dict]:
    """Historial de trades simulados."""
    try:
        from database import db, _row_to_dict
        with db() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT * FROM simulated_trades
                ORDER BY id DESC LIMIT ?
            """, (limit,))
            return [_row_to_dict(r) for r in cur.fetchall()]
    except Exception:
        return []
