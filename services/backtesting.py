"""
Backtesting walk-forward del sistema.
Valida la precision REAL de los modelos sobre historial conocido.
Metricas: accuracy, ROI simulado, Brier Score, mejora vs aleatorio.
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
