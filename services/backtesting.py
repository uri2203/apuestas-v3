"""
Backtesting walk-forward del sistema.
Valida la precision REAL de los modelos sobre historial conocido.
Metricas: accuracy, ROI simulado, Brier Score, mejora vs aleatorio.
Además: simulación de value betting con Kelly y análisis por temporada.
"""
from models.ensemble import EnsembleModel
from models.dixon_coles import DixonColesModel
from models.elo import ELOModel


def backtest(partidos, ventana=20, kelly_frac=0.5, cuota_base=2.10):
    """
    Walk-forward backtest.
    - Entrena con los primeros 'ventana' partidos
    - Predice uno a uno los siguientes
    - Mide accuracy y ROI simulado con Kelly

    partidos: lista de {home, away, home_goals, away_goals}
    ventana:  partidos de entrenamiento inicial
    """
    if len(partidos) < ventana + 5:
        return {
            "error": f"Necesitas al menos {ventana+5} partidos. Tienes {len(partidos)}.",
            "sugerencia": "Agrega API_FOOTBALL_KEY para usar historial real de Liga MX.",
        }

    resultados  = []
    bankroll    = 1000.0
    bankroll_hist = [bankroll]

    for i in range(ventana, len(partidos)):
        train = partidos[:i]
        test  = partidos[i]

        home = test.get("home", "")
        away = test.get("away", "")
        gh   = test.get("home_goals", 0)
        ga   = test.get("away_goals", 0)

        if not home or not away:
            continue

        # Entrenar y predecir
        try:
            modelo = EnsembleModel()
            modelo.fit(train)
            pred = modelo.predict(home, away)
        except Exception:
            continue

        probs = [pred["local"], pred["empate"], pred["visitante"]]
        max_p = max(probs)
        idx   = probs.index(max_p)
        pred_str  = ["1", "X", "2"][idx]
        real_str  = "1" if gh > ga else "X" if gh == ga else "2"
        correcto  = pred_str == real_str

        # Brier Score (menor = mejor; 0.333 = aleatorio)
        real_vec = [
            1 if real_str == "1" else 0,
            1 if real_str == "X" else 0,
            1 if real_str == "2" else 0,
        ]
        brier = sum((p - r) ** 2 for p, r in zip(probs, real_vec)) / 3

        # Kelly simulado
        b    = cuota_base - 1
        q    = 1 - max_p
        kp   = (b * max_p - q) / b if b > 0 else 0
        apuesta = max(0, bankroll * kp * kelly_frac)

        if correcto and apuesta > 0:
            bankroll += apuesta * b
        elif apuesta > 0:
            bankroll -= apuesta

        bankroll = max(0, bankroll)
        bankroll_hist.append(round(bankroll, 2))

        resultados.append({
            "partido":    f"{home} vs {away}",
            "prediccion": pred_str,
            "real":       real_str,
            "correcto":   correcto,
            "confianza":  round(max_p * 100, 1),
            "brier":      round(brier, 4),
            "apuesta":    round(apuesta, 2),
            "bankroll":   round(bankroll, 2),
            "prob_local":     round(pred["local"] * 100, 1),
            "prob_empate":    round(pred["empate"] * 100, 1),
            "prob_visitante": round(pred["visitante"] * 100, 1),
        })

    if not resultados:
        return {"error": "Sin resultados — verifica los datos de entrada"}

    n         = len(resultados)
    acertados = sum(1 for r in resultados if r["correcto"])
    brier_avg = sum(r["brier"] for r in resultados) / n
    roi       = (bankroll - 1000) / 1000 * 100

    # Max drawdown
    peak = bankroll_hist[0]
    dd_max = 0
    for v in bankroll_hist:
        if v > peak:
            peak = v
        dd = (peak - v) / peak * 100
        dd_max = max(dd_max, dd)

    # Sharpe ratio anualizado de los retornos diarios
    returns = []
    for i in range(1, len(bankroll_hist)):
        if bankroll_hist[i-1] > 0:
            r = (bankroll_hist[i] - bankroll_hist[i-1]) / bankroll_hist[i-1]
            returns.append(r)
    sharpe = 0
    if len(returns) > 5:
        mean_r = sum(returns) / len(returns)
        std_r = (sum((r - mean_r) ** 2 for r in returns) / len(returns)) ** 0.5
        if std_r > 0:
            sharpe = round(mean_r / std_r * (252 ** 0.5), 2)

    # Accuracy por resultado
    por_resultado = {}
    for res in ["1", "X", "2"]:
        sub = [r for r in resultados if r["real"] == res]
        if sub:
            ok = sum(1 for r in sub if r["correcto"])
            por_resultado[res] = {
                "total": len(sub), "acertados": ok,
                "accuracy_pct": round(ok / len(sub) * 100, 1),
            }

    # Accuracy por nivel de confianza
    alta    = [r for r in resultados if r["confianza"] >= 55]
    media   = [r for r in resultados if 42 <= r["confianza"] < 55]
    baja    = [r for r in resultados if r["confianza"] < 42]

    return {
        "resumen": {
            "total_predicciones":   n,
            "acertadas":            acertados,
            "accuracy_pct":         round(acertados / n * 100, 1),
            "benchmark_aleatorio":  33.3,
            "mejora_vs_aleatorio":  round(acertados / n * 100 - 33.3, 1),
            "brier_score":          round(brier_avg, 4),
            "brier_aleatorio":      0.222,
            "roi_kelly_pct":        round(roi, 1),
            "bankroll_inicial":     1000,
            "bankroll_final":       round(bankroll, 2),
            "max_drawdown_pct":     round(dd_max, 2),
            "sharpe_ratio":         sharpe,
            "kelly_fraccion":       kelly_frac,
        },
        "accuracy_por_resultado": por_resultado,
        "accuracy_por_confianza": {
            "alta_55plus": {
                "n": len(alta),
                "accuracy_pct": round(sum(1 for r in alta if r["correcto"]) / len(alta) * 100, 1) if alta else 0,
            },
            "media_42_55": {
                "n": len(media),
                "accuracy_pct": round(sum(1 for r in media if r["correcto"]) / len(media) * 100, 1) if media else 0,
            },
            "baja_menos42": {
                "n": len(baja),
                "accuracy_pct": round(sum(1 for r in baja if r["correcto"]) / len(baja) * 100, 1) if baja else 0,
            },
        },
        "bankroll_historia": bankroll_hist,
        "ultimas_20_predicciones": resultados[-20:],
        "interpretacion": (
            "Excelente — supera significativamente al azar"
            if acertados / n > 0.50 else
            "Bueno — por encima del benchmark aleatorio"
            if acertados / n > 0.40 else
            "Regular — cerca del azar. Agregar mas datos mejora precision."
        ),
    }


def backtest_por_modelo(partidos, ventana=20):
    """
    Compara precision de DC solo vs ELO solo vs Ensemble.
    """
    if len(partidos) < ventana + 5:
        return {"error": "Datos insuficientes"}

    modelos = {
        "Dixon-Coles": DixonColesModel(),
        "ELO":         ELOModel(),
        "Ensemble":    EnsembleModel(),
    }

    stats = {k: {"correcto": 0, "total": 0} for k in modelos}

    for i in range(ventana, len(partidos)):
        train = partidos[:i]
        test  = partidos[i]
        home, away = test.get("home",""), test.get("away","")
        gh, ga = test.get("home_goals",0), test.get("away_goals",0)
        real = "1" if gh > ga else "X" if gh == ga else "2"
        if not home or not away: continue

        # Dixon-Coles
        try:
            dc = DixonColesModel(); dc.fit(train)
            p  = dc.predict(home, away)
            probs = [p["local"], p["empate"], p["visitante"]]
            pred = ["1","X","2"][probs.index(max(probs))]
            stats["Dixon-Coles"]["total"] += 1
            if pred == real: stats["Dixon-Coles"]["correcto"] += 1
        except Exception: pass

        # ELO
        try:
            elo = ELOModel(); elo.update(train)
            p   = elo.predict(home, away)
            probs = [p["local"], p["empate"], p["visitante"]]
            pred = ["1","X","2"][probs.index(max(probs))]
            stats["ELO"]["total"] += 1
            if pred == real: stats["ELO"]["correcto"] += 1
        except Exception: pass

        # Ensemble
        try:
            ens = EnsembleModel(); ens.fit(train)
            p   = ens.predict(home, away)
            probs = [p["local"], p["empate"], p["visitante"]]
            pred = ["1","X","2"][probs.index(max(probs))]
            stats["Ensemble"]["total"] += 1
            if pred == real: stats["Ensemble"]["correcto"] += 1
        except Exception: pass

    return {
        k: {
            "accuracy_pct": round(v["correcto"] / v["total"] * 100, 1) if v["total"] else 0,
            "acertados": v["correcto"],
            "total": v["total"],
        }
        for k, v in stats.items()
    }


# ── FULL BACKTESTING CON VALUE BETTING ───────────────────────────────────────

def backtest_value_betting(
    partidos: list,
    ventana: int = 30,
    edge_minimo: float = 3.0,
    kelly_frac: float = 0.25,
    cuota_minima: float = 1.5,
    cuota_maxima: float = 5.0,
) -> dict:
    """
    Simulación completa de value betting.
    En cada paso: predice, calcula edge, aplica Kelly si hay valor.

    Retorna métricas detalladas de rendimiento.
    """
    if len(partidos) < ventana + 10:
        return {"error": f"Datos insuficientes: {len(partidos)} (min {ventana + 10})"}

    bankroll = 1000.0
    bankroll_hist = [bankroll]
    trades = []
    max_dd = 0
    peak = bankroll

    for i in range(ventana, len(partidos)):
        train = partidos[:i]
        test = partidos[i]

        home = test.get("home", "")
        away = test.get("away", "")
        gh = test.get("home_goals", 0)
        ga = test.get("away_goals", 0)
        if not home or not away:
            continue

        try:
            modelo = EnsembleModel()
            modelo.fit(train)
            pred = modelo.predict(home, away)
        except Exception:
            continue

        probs = {
            "1": pred.get("local", 0),
            "X": pred.get("empate", 0),
            "2": pred.get("visitante", 0),
        }
        real = "1" if gh > ga else "X" if gh == ga else "2"

        mejor_resultado = max(probs, key=probs.get)
        prob_modelo = probs[mejor_resultado]

        # Simular cuota de mercado (inversa de prob promedio)
        cuota_mercado = 1.0 / max(prob_modelo, 0.01)
        cuota_mercado = max(cuota_minima, min(cuota_maxima, cuota_mercado))

        # Añadir vig (4% de overround)
        cuota_apostada = cuota_mercado * 0.96

        # Edge
        edge = (prob_modelo * cuota_apostada - 1) * 100

        apuesta = 0
        resultado_trade = "skip"
        pnl = 0

        if edge >= edge_minimo and cuota_minima <= cuota_apostada <= cuota_maxima:
            b_odds = cuota_apostada - 1
            kelly = (b_odds * prob_modelo - (1 - prob_modelo)) / b_odds if b_odds > 0 else 0
            kelly = max(0, kelly)
            apuesta = min(bankroll * kelly * kelly_frac, bankroll * 0.05)

            if apuesta > 0:
                ganada = mejor_resultado == real
                if ganada:
                    pnl = apuesta * b_odds
                    bankroll += pnl
                else:
                    pnl = -apuesta
                    bankroll -= apuesta
                resultado_trade = "ganada" if ganada else "perdida"

        bankroll = max(0, bankroll)
        bankroll_hist.append(round(bankroll, 2))

        # Track drawdown
        if bankroll > peak:
            peak = bankroll
        dd = (peak - bankroll) / peak * 100
        max_dd = max(max_dd, dd)

        trades.append({
            "partido": f"{home} vs {away}",
            "prediccion": mejor_resultado,
            "real": real,
            "prob_modelo": round(prob_modelo * 100, 1),
            "cuota_simulada": round(cuota_apostada, 2),
            "edge_pct": round(edge, 2),
            "resultado": resultado_trade,
            "apuesta": round(apuesta, 2),
            "pnl": round(pnl, 2),
            "bankroll": round(bankroll, 2),
        })

    if not trades:
        return {"error": "Sin trades generados"}

    # Métricas
    total_trades = len([t for t in trades if t["resultado"] != "skip"])
    ganadas = len([t for t in trades if t["resultado"] == "ganada"])
    perdidas = len([t for t in trades if t["resultado"] == "perdida"])

    roi_total = ((bankroll - 1000) / 1000) * 100

    # Sharpe de los retornos
    returns = []
    for i in range(1, len(bankroll_hist)):
        if bankroll_hist[i-1] > 0:
            r = (bankroll_hist[i] - bankroll_hist[i-1]) / bankroll_hist[i-1]
            returns.append(r)
    sharpe = 0
    if len(returns) > 5:
        mean_r = sum(returns) / len(returns)
        std_r = (sum((r - mean_r) ** 2 for r in returns) / len(returns)) ** 0.5
        if std_r > 0:
            sharpe = round(mean_r / std_r * (252 ** 0.5), 2)

    # Profit factor
    gross_profit = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    gross_loss = abs(sum(t["pnl"] for t in trades if t["pnl"] < 0))
    profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else 0

    return {
        "config": {
            "ventana_entrenamiento": ventana,
            "edge_minimo_pct": edge_minimo,
            "kelly_fraccion": kelly_frac,
            "cuota_rango": [cuota_minima, cuota_maxima],
        },
        "resumen": {
            "total_partidos_analizados": len(trades),
            "total_apuestas": total_trades,
            "ganadas": ganadas,
            "perdidas": perdidas,
            "win_rate_pct": round(ganadas / total_trades * 100, 1) if total_trades else 0,
            "bankroll_inicial": 1000,
            "bankroll_final": round(bankroll, 2),
            "roi_total_pct": round(roi_total, 2),
            "profit_factor": profit_factor,
            "max_drawdown_pct": round(max_dd, 2),
            "sharpe_ratio": sharpe,
        },
        "trades_ejemplo": trades[-20:],
        "bankroll_historia": bankroll_hist,
    }
