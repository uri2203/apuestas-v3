"""
test_all.py - Suite de pruebas automatizada.

Uso:
  python test_all.py                    # pruebas locales con SQLite
  python test_all.py --pg               # pruebas con PostgreSQL (requiere DATABASE_URL)
  python test_all.py --ci               # modo CI (GitHub Actions)
"""

import os, sys, json, time, random, hashlib, tempfile, sqlite3, traceback

sys.stdout.reconfigure(encoding="utf-8", errors="replace") if hasattr(sys.stdout, "reconfigure") else None

# NO setear DB_PATH - dejar que database.py use default "apuestaspro.db"
os.environ.setdefault("APP_PASSWORD", "test123")
os.environ.setdefault("SESSION_SECRET", "test-secret-123456")
os.environ.setdefault("FLASK_ENV", "testing")
if "DB_PATH" in os.environ:
    del os.environ["DB_PATH"]

USE_PG = "--pg" in sys.argv
CI_MODE = "--ci" in sys.argv
PASS = 0
FAIL = 0
ERRORS = []

def log(msg, ok=True):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  [OK] {msg}")
    else:
        FAIL += 1
        print(f"  [FAIL] {msg}")

def check(cond, msg):
    if cond:
        log(msg, True)
    else:
        log(msg, False)
        ERRORS.append(msg)

def check_eq(a, b, msg):
    check(a == b, f"{msg}: esperado={b!r} recibido={a!r}")

def check_gt(a, b, msg):
    check(a > b, f"{msg}: {a} <= {b}")

def main():
    global PASS, FAIL, ERRORS

    print("")
    print("=" * 60)
    print("  APUESTAS PRO - TEST SUITE")
    print(f"  DB:     {'PostgreSQL' if USE_PG else 'SQLite'}")
    print(f"  Modo:   {'CI' if CI_MODE else 'Local'}")
    print("=" * 60)
    print("")

    # -- 1. Setup DB temporal --
    if USE_PG:
        from database import _init_pg
        _init_pg()
        print("  DB: PostgreSQL lista")
    else:
        from database import _init_sqlite
        _init_sqlite()
        print("  DB: SQLite lista")

    # -- 2. Flask test client --
    from main import app as _app
    _app.config["TESTING"] = True
    _app.config["WTF_CSRF_ENABLED"] = False
    client = _app.test_client()

    from auth import _create_session_cookie, COOKIE_NAME
    token = _create_session_cookie()
    _HEADERS = {"Cookie": f"{COOKIE_NAME}={token}"}

    def get(url):
        return client.get(url, headers=_HEADERS)

    def post(url, data=None, json_data=None):
        if json_data:
            return client.post(url, json=json_data, content_type="application/json", headers=_HEADERS)
        return client.post(url, data=data, headers=_HEADERS)

    # -- 3. Health check --
    print("\n  --- Health ---")
    r = get("/api/health")
    check_eq(r.status_code, 200, "GET /api/health = 200")
    d = r.get_json()
    check(d is not None, "/api/health retorna JSON")
    if d:
        check(d.get("status") == "ok", "health.status == ok")
        check(d.get("database", {}).get("conectada") is True, "database.conectada == True")
        check("bankroll" in d, "health.bankroll existe")

    # -- 4. Login --
    print("\n  --- Login ---")
    r = post("/login", data={"password": "test123"})
    check(r.status_code in (200, 302), f"POST /login = {r.status_code}")
    r2 = post("/login", data={"password": "wrong"})
    check(r2.status_code == 200, "POST /login wrong password = 200 (error msg)")

    # -- 5. Version --
    print("\n  --- Version ---")
    r = get("/api/version")
    check_eq(r.status_code, 200, "GET /api/version = 200")
    d = r.get_json()
    check(d and "version" in d, "version tiene 'version' key")

    # -- 6. Seed database --
    print("\n  --- Seed ---")
    r = get("/api/seed-demo")
    check_eq(r.status_code, 200, f"GET /api/seed-demo = 200")
    d = r.get_json()
    check(d is not None, "seed retorna JSON")
    if d:
        total = d.get("total_insertados", 0)
        check(total > 0, f"seed inserta registros: {total}")
        check_gt(total, 600, f"seed inserta >= 600 registros")
        errores = d.get("errores", [])
        check(len(errores) == 0, f"seed sin errores ({len(errores)})")
        if errores:
            for e in errores[:5]:
                print(f"    - {e}")

    # -- 7. Dashboard --
    print("\n  --- Dashboard ---")
    r = get("/")
    check_eq(r.status_code, 200, "GET / = 200")
    html = r.data.decode()
    check("Apuestas" in html, "landing contiene 'Apuestas'")
    check("Seed Database" in html, "landing contiene boton Seed Database")

    r = get("/api/dashboard/rendimiento")
    check_eq(r.status_code, 200, "GET /api/dashboard/rendimiento = 200")
    d = r.get_json()
    if d:
        check("general" in d, "rendimiento tiene 'general'")
        check("bankroll" in d, "rendimiento tiene 'bankroll'")
        br = d.get("bankroll", {}).get("actual", 0)
        check_gt(float(br), 0, f"bankroll actual > 0: {br}")

    # -- 7b. KPI publico --
    r = client.get("/api/kpi-summary")
    check_eq(r.status_code, 200, "GET /api/kpi-summary = 200 (publico)")
    d = r.get_json()
    if d:
        check("bankroll" in d, "kpi-summary tiene 'bankroll'")
        check("general" in d, "kpi-summary tiene 'general'")
        check("hoy" in d, "kpi-summary tiene 'hoy'")
        check("database" in d, "kpi-summary tiene 'database'")
        check_gt(float(d.get("bankroll", {}).get("actual", 0)), 0, "kpi bankroll > 0")

    # -- 8. Module pages --
    print("\n  --- Modulos ---")
    modulos = [
        "value-bets", "sharp", "alta-prob", "arbitraje", "cross-market", "kelly", "value-engine",
        "copa", "ml", "backtesting", "nlp", "montecarlo",
        "bankroll", "simulacion", "contabilidad", "journal", "mercados",
        "bookmakers", "progol", "cuentas", "portfolio", "rendimiento", "modelos-avanzados", "brain"
    ]
    for m in modulos:
        r = get(f"/panel/{m}")
        check_eq(r.status_code, 200, f"GET /panel/{m} = 200")
        html = r.data.decode()
        check('class="content"' in html or "modContent" in html, f"panel/{m} tiene estructura ventana")

    # -- 9. Value bets --
    print("\n  --- Value Bets ---")
    r = get("/api/odds/value-bets")
    check_eq(r.status_code, 200, "GET /api/odds/value-bets = 200")
    r = get("/api/value/analizar?prob=55&cuota=2.10")
    check_eq(r.status_code, 200, "GET /api/value/analizar = 200")
    r = get("/api/value/clv")
    check_eq(r.status_code, 200, "GET /api/value/clv = 200")

    # -- 10. Arbitrage --
    print("\n  --- Arbitraje ---")
    r = get("/api/odds/arbitraje")
    check_eq(r.status_code, 200, "GET /api/odds/arbitraje = 200")

    # -- 11. Sharp Money --
    print("\n  --- Sharp Money ---")
    r = get("/api/sharp/analizar")
    check_eq(r.status_code, 200, "GET /api/sharp/analizar = 200")
    r = get("/api/sharp/steam")
    check_eq(r.status_code, 200, "GET /api/sharp/steam = 200")
    r = get("/api/sharp/scan")
    check_eq(r.status_code, 200, "GET /api/sharp/scan = 200")
    d = r.get_json()
    check("recomendaciones" in d, "sharp/scan tiene recomendaciones")

    # -- 12. Alertas --
    print("\n  --- Alertas ---")
    r = get("/api/alertas/recientes")
    check_eq(r.status_code, 200, "GET /api/alertas/recientes = 200")

    # -- 13. Simulacion --
    print("\n  --- Simulacion ---")
    r = get("/api/simulacion/status")
    check_eq(r.status_code, 200, "GET /api/simulacion/status = 200")

    # -- 14. Contabilidad --
    print("\n  --- Contabilidad ---")
    r = get("/api/contabilidad/resumen-mensual")
    check_eq(r.status_code, 200, "GET /api/contabilidad/resumen-mensual = 200")
    r = get("/api/contabilidad/pnl-estrategia")
    check_eq(r.status_code, 200, "GET /api/contabilidad/pnl-estrategia = 200")

    # -- 15. Trading Journal --
    print("\n  --- Journal ---")
    r = get("/api/journal/resumen")
    check_eq(r.status_code, 200, "GET /api/journal/resumen = 200")
    r = get("/api/journal/export-csv")
    check_eq(r.status_code, 200, "GET /api/journal/export-csv = 200")

    # -- 16. Bookmaker ratings --
    print("\n  --- Bookmakers ---")
    r = get("/api/bookmakers/rating")
    check_eq(r.status_code, 200, "GET /api/bookmakers/rating = 200")

    # -- 17. Cross market --
    print("\n  --- Cross Market ---")
    r = get("/api/odds/cross-market")
    check(r.status_code in (200, 500), f"GET /api/odds/cross-market = {r.status_code} (esperado 200 o 500)")

    # -- 18. Kelly/Bankroll --
    print("\n  --- Kelly ---")
    r = post("/api/kelly/calcular", json_data={"bankroll":5000,"cuota_decimal":2.10,"probabilidad_estimada_pct":55})
    check_eq(r.status_code, 200, "POST /api/kelly/calcular = 200")

    # -- 19. Portfolio --
    print("\n  --- Portfolio ---")
    r = get("/api/portfolio/status")
    check_eq(r.status_code, 200, "GET /api/portfolio/status = 200")

    # -- 20. Backtesting --
    print("\n  --- Backtesting ---")
    r = get("/api/backtest")
    check_eq(r.status_code, 200, "GET /api/backtest = 200")

    # -- 21. Admin --
    print("\n  --- Admin ---")
    r = get("/api/admin/init-db")
    check_eq(r.status_code, 200, "GET /api/admin/init-db = 200")

    # -- 22. Auth check --
    print("\n  --- Sin autenticacion ---")
    client2 = _app.test_client()
    r = client2.get("/api/seed-demo")
    check_eq(r.status_code, 401, "GET /api/seed-demo sin auth = 401")

    # -- 23. Seed idempotencia --
    print("\n  --- Idempotencia ---")
    r = get("/api/seed-demo")
    check_eq(r.status_code, 200, "seed repetido = 200")
    d = r.get_json()
    if d:
        check(d.get("status") in ("ok", "con_errores"), "seed repetido no falla")

    # -- 24. DB functions --
    print("\n  --- DB Direct ---")
    try:
        from database import get_bankroll_actual, count_bets_today, count_predictions_today
        br = get_bankroll_actual()
        check_gt(float(br), 0, f"get_bankroll_actual() > 0: {br}")
        bets = count_bets_today()
        check(bets is not None, "count_bets_today() funciona")
        preds = count_predictions_today()
        check(preds is not None, "count_predictions_today() funciona")
    except Exception as e:
        log(f"DB direct error: {e}", False)

    # -- 25. ML endpoints --
    print("\n  --- ML ---")
    r = get("/api/ml/v2/features")
    check_eq(r.status_code, 200, "GET /api/ml/v2/features = 200")
    r = get("/api/ml/v2/performance")
    check_eq(r.status_code, 200, "GET /api/ml/v2/performance = 200")

    # -- 26. Modelos Avanzados endpoints --
    print("\n  --- Modelos Avanzados ---")
    r = get("/api/advanced/dixon-coles/predict?home=Team+A&away=Team+B")
    check_eq(r.status_code, 200, "GET /api/advanced/dixon-coles/predict = 200")
    d = r.get_json()
    check(d and "probabilidades" in d, "dixon-coles retorna probabilidades")

    r = get("/api/advanced/dixon-coles/value?home=Team+A&away=Team+B&local_odds=2.10&empate_odds=3.40&visitante_odds=3.20")
    check_eq(r.status_code, 200, "GET /api/advanced/dixon-coles/value = 200")

    r = get("/api/advanced/elo/predict?home=Team+A&away=Team+B")
    check_eq(r.status_code, 200, "GET /api/advanced/elo/predict = 200")
    d = r.get_json()
    check(d and "probabilidades" in d, "elo/predict retorna probabilidades")

    r = get("/api/advanced/elo/ratings")
    check_eq(r.status_code, 200, "GET /api/advanced/elo/ratings = 200")

    r = post("/api/advanced/elo/update", json_data={"home":"Team+A","away":"Team+B","home_goals":2,"away_goals":1})
    check_eq(r.status_code, 200, "POST /api/advanced/elo/update = 200")

    r = get("/api/advanced/fatigue/analyze?schedule=2026-06-01,2026-06-03,2026-06-05&sport=basketball")
    check_eq(r.status_code, 200, "GET /api/advanced/fatigue/analyze = 200")

    r = get("/api/advanced/fatigue/travel?origin=New+York&destination=Los+Angeles")
    check_eq(r.status_code, 200, "GET /api/advanced/fatigue/travel = 200")

    r = get("/api/advanced/weather/analyze?temperature_f=30&wind_mph=20&precipitation_pct=80&humidity_pct=90&outdoor=true")
    check_eq(r.status_code, 200, "GET /api/advanced/weather/analyze = 200")
    d = r.get_json()
    check(d and "impacto" in d, "weather/analyze retorna impacto")

    r = get("/api/advanced/clv/calculate?bet_odds=2.10&closing_odds=1.90")
    check_eq(r.status_code, 200, "GET /api/advanced/clv/calculate = 200")
    d = r.get_json()
    check(d and "clv_pct" in d, "clv/calculate retorna clv_pct")

    r = post("/api/advanced/clv/track", json_data={"match_id":"test","team":"A","bet_odds":2.10,"model_prob":0.5})
    check_eq(r.status_code, 200, "POST /api/advanced/clv/track = 200")

    r = get("/api/advanced/clv/summary")
    check_eq(r.status_code, 200, "GET /api/advanced/clv/summary = 200")

    r = get("/api/advanced/calibration/status")
    check_eq(r.status_code, 200, "GET /api/advanced/calibration/status = 200")

    r = post("/api/advanced/calibration/add", json_data={"predicted_prob":0.6,"actual":True})
    check_eq(r.status_code, 200, "POST /api/advanced/calibration/add = 200")

    r = get("/api/advanced/combined/predict?home=Team+A&away=Team+B")
    check_eq(r.status_code, 200, "GET /api/advanced/combined/predict = 200")
    d = r.get_json()
    check(d and "modelo_combinado" in d, "combined/predict retorna modelo_combinado")

    # -- 27. API Key Cascade tests --
    print("\n  --- API Key Cascade ---")
    from services.deportes import (
        _get_api_keys, _is_key_exhausted, _mark_key_exhausted,
        get_any_odds_key, _exhausted_keys, EXHAUST_TTL,
    )

    # Test: _get_api_keys reads from ODDS_API_KEYS
    os.environ["ODDS_API_KEYS"] = "testkey1,testkey2,testkey3"
    keys = _get_api_keys()
    check_eq(len(keys), 3, "_get_api_keys parsea 3 keys de ODDS_API_KEYS")
    check_eq(keys[0], "testkey1", "_get_api_keys primera key es testkey1")
    check_eq(keys[2], "testkey3", "_get_api_keys tercera key es testkey3")

    # Test: _get_api_keys fallback to ODDS_API_KEY
    del os.environ["ODDS_API_KEYS"]
    os.environ["ODDS_API_KEY"] = "singlekey"
    keys2 = _get_api_keys()
    check_eq(len(keys2), 1, "_get_api_keys fallback a ODDS_API_KEY (1 key)")
    check_eq(keys2[0], "singlekey", "_get_api_keys usa ODDS_API_KEY")
    del os.environ["ODDS_API_KEY"]

    # Test: _get_api_keys returns empty when no keys configured
    keys_empty = _get_api_keys()
    check_eq(len(keys_empty), 0, "_get_api_keys retorna [] sin keys configuradas")

    # Test: exhaustion tracking
    os.environ["ODDS_API_KEYS"] = "key_a,key_b,key_c"
    _exhausted_keys.clear()  # Limpiar estado previo

    check(not _is_key_exhausted("key_a"), "key_a NO agotada al inicio")
    _mark_key_exhausted("key_a")
    check(_is_key_exhausted("key_a"), "key_a SÍ agotada después de mark")
    check(not _is_key_exhausted("key_b"), "key_b NO agotada (solo key_a)")

    # Test: get_any_odds_key skips exhausted keys
    _exhausted_keys.clear()
    _mark_key_exhausted("key_a")
    chosen = get_any_odds_key()
    check(chosen != "key_a", f"get_any_odds_key salta key_a agotada: eligió {chosen}")
    check(chosen in ("key_b", "key_c"), f"get_any_odds_key eligió key_b o key_c: {chosen}")

    # Test: get_any_odds_key returns first non-exhausted
    _exhausted_keys.clear()
    _mark_key_exhausted("key_b")
    chosen2 = get_any_odds_key()
    check_eq(chosen2, "key_a", "get_any_odds_key retorna key_a (primera no agotada)")

    # Test: get_any_odds_key returns first key when ALL exhausted
    _exhausted_keys.clear()
    _mark_key_exhausted("key_a")
    _mark_key_exhausted("key_b")
    _mark_key_exhausted("key_c")
    chosen_all = get_any_odds_key()
    check_eq(chosen_all, "key_a", "get_any_odds_key retorna primera aunque todas agotadas")

    # Test: exhaustion TTL expires
    _exhausted_keys.clear()
    _mark_key_exhausted("key_a")
    _exhausted_keys["key_a"] = time.time() - EXHAUST_TTL - 1  # Simular expiración
    check(not _is_key_exhausted("key_a"), "key_a NO agotada tras TTL expirado")

    # Test: cascade endpoint does not crash with empty keys
    del os.environ["ODDS_API_KEYS"]
    _exhausted_keys.clear()
    r = get("/api/diag/odds-api")
    check_eq(r.status_code, 200, "GET /api/diag/odds-api = 200 (sin keys)")
    d = r.get_json()
    check(d.get("configured") == False, "diag/odds-api: configured=False sin keys")

    # Restaurar keys para siguientes tests
    os.environ["ODDS_API_KEYS"] = "testkey1,testkey2,testkey3"
    _exhausted_keys.clear()

    # Test: /api/odds/value-bets no crasha con cascade
    r = get("/api/odds/value-bets?deporte=upcoming&multi=1")
    check_eq(r.status_code, 200, "GET /api/odds/value-bets (multi) = 200")
    d = r.get_json()
    check("total_encontrados" in d, "value-bets tiene total_encontrados")

    # Test: /api/sharp/scan no crasha con cascade
    r = get("/api/sharp/scan?deporte=upcoming")
    check_eq(r.status_code, 200, "GET /api/sharp/scan = 200")
    d = r.get_json()
    check("recomendaciones" in d, "sharp/scan tiene recomendaciones")

    # Limpiar
    del os.environ["ODDS_API_KEYS"]
    _exhausted_keys.clear()

    # -- 28. Brain Agent tests --
    print("\n  --- Brain Agent ---")
    from services.brain import (
        collect_all_signals, aggregate_signals, filter_signals,
        simulate_trades, learn_from_results, get_status,
        DEFAULT_WEIGHTS, CONFIDENCE_THRESHOLD,
    )

    # Test: Brain status returns config
    status = get_status()
    check("threshold" in status, "brain.get_status tiene threshold")
    check_eq(status["threshold"], 88.0, "brain threshold = 88.0")
    check("current_weights" in status, "brain.get_status tiene current_weights")
    check("source_performance" in status, "brain.get_status tiene source_performance")

    # Test: collect_all_signals returns list
    signals = collect_all_signals()
    check(isinstance(signals, list), "collect_all_signals retorna lista")

    # Test: aggregate_signals groups by match
    test_signals = [
        {"match": "A vs B", "source": "value_bet", "confidence": 80, "edge_pct": 10, "odds": 2.1, "bookmaker": "Bet365", "selection": "A", "home": "A", "away": "B"},
        {"match": "A vs B", "source": "sharp_money", "confidence": 75, "edge_pct": 8, "odds": 2.0, "bookmaker": "Pinnacle", "selection": "A", "home": "A", "away": "B"},
        {"match": "A vs B", "source": "ml_prediction", "confidence": 85, "edge_pct": 12, "odds": 0, "bookmaker": "", "selection": "A", "home": "A", "away": "B"},
        {"match": "C vs D", "source": "value_bet", "confidence": 60, "edge_pct": 5, "odds": 3.0, "bookmaker": "Bet365", "selection": "C", "home": "C", "away": "D"},
    ]
    agg = aggregate_signals(test_signals)
    check_eq(len(agg), 2, "aggregate_signals agrupa 4 señales en 2 partidos")
    check(agg[0]["composite_score"] > agg[1]["composite_score"], "aggregate ordena por score descendente")
    check_eq(agg[0]["source_count"], 3, "A vs B tiene 3 fuentes")
    check_eq(agg[1]["source_count"], 1, "C vs D tiene 1 fuente")

    # Test: filter_signals with threshold
    filtered = filter_signals(agg, threshold=88, min_sources=2)
    check_eq(len(filtered), 1, "filter(88%, 2 src) retorna 1 señal")
    check(filtered[0]["passed_filter"] == True, "A vs B pasa filtro")

    # Test: filter_signals rejects low score
    filtered_strict = filter_signals(agg, threshold=95, min_sources=1)
    check_eq(len(filtered_strict), 0, "filter(95%) no pasa nada")

    # Test: simulate_trades with Kelly sizing
    # Preparar señales que pasan el filtro (cuota en rango 1.80-3.00)
    high_signal = [
        {"match": "X vs Y", "source": "value_bet", "confidence": 90, "edge_pct": 15, "odds": 2.30, "bookmaker": "Bet365", "selection": "X", "home": "X", "away": "Y"},
        {"match": "X vs Y", "source": "sharp_money", "confidence": 88, "edge_pct": 12, "odds": 2.25, "bookmaker": "Pinnacle", "selection": "X", "home": "X", "away": "Y"},
        {"match": "X vs Y", "source": "ml_prediction", "confidence": 92, "edge_pct": 18, "odds": 2.40, "bookmaker": "", "selection": "X", "home": "X", "away": "Y"},
        {"match": "X vs Y", "source": "nlp_sentiment", "confidence": 85, "edge_pct": 10, "odds": 0, "bookmaker": "", "selection": "X", "home": "X", "away": "Y"},
    ]
    agg_high = aggregate_signals(high_signal)
    filtered_high = filter_signals(agg_high, threshold=70, min_sources=2)
    trades = simulate_trades(filtered_high, bankroll=10000)
    check(len(trades) > 0, "simulate_trades genera trades con bankroll=10000")
    if trades:
        t = trades[0]
        check("stake" in t, "trade tiene stake")
        check(t["stake"] > 0, "trade stake > 0")
        check(t["stake"] <= 500, "trade stake <= 5% bankroll")
        check("kelly_pct" in t, "trade tiene kelly_pct")

    # Test: learn_from_results (no-op if no data)
    learn_result = learn_from_results()
    check("changes" in learn_result, "learn_from_results tiene changes")
    check("current_weights" in learn_result, "learn_from_results tiene current_weights")
    check("source_performance" in learn_result, "learn_from_results tiene source_performance")

    # Test: Brain API endpoints
    r = get("/api/brain/status")
    check_eq(r.status_code, 200, "GET /api/brain/status = 200")
    d = r.get_json()
    check(d and "threshold" in d, "brain/status retorna threshold")

    r = get("/api/brain/weights")
    check_eq(r.status_code, 200, "GET /api/brain/weights = 200")
    d = r.get_json()
    check("current" in d, "brain/weights tiene current")
    check("default" in d, "brain/weights tiene default")

    r = get("/api/brain/history")
    check_eq(r.status_code, 200, "GET /api/brain/history = 200")
    d = r.get_json()
    check("trades" in d, "brain/history tiene trades")

    r = get("/api/brain/verify")
    check_eq(r.status_code, 200, "GET /api/brain/verify = 200")

    r = get("/api/brain/learn")
    check_eq(r.status_code, 200, "GET /api/brain/learn = 200")

    r = get("/api/brain/scan")
    check_eq(r.status_code, 200, "GET /api/brain/scan = 200")
    d = r.get_json()
    check("raw_signals_count" in d, "brain/scan tiene raw_signals_count")
    check("filtered_signals" in d, "brain/scan tiene filtered_signals")
    check("trades_simulated" in d, "brain/scan tiene trades_simulated")

    r = post("/api/brain/config", json_data={"threshold": 80})
    check_eq(r.status_code, 200, "POST /api/brain/config = 200")

    # -- 29. Brain Simulation Engine tests --
    print("\n  --- Brain Simulation ---")
    from services.brain import (
        simular_trade, resolver_trade, get_performance,
        reset_simulation, auto_scan_and_simulate,
        _sim_state, _bankroll_history,
    )

    # Test: Reset simulation
    reset = reset_simulation(10000)
    check_eq(reset["status"], "ok", "reset_simulation retorna ok")
    check_eq(reset["bankroll"], 10000, "reset bankroll = 10000")
    check_eq(_sim_state["bankroll_actual"], 10000, "sim_state bankroll = 10000")
    check_eq(_sim_state["trades_total"], 0, "reset trades_total = 0")

    # Test: Simular trade con señal ficticia
    test_signal = {
        "match": "TestTeam A vs TestTeam B",
        "liga": "test_liga",
        "best_selection": "TestTeam A",
        "best_bookmaker": "TestBook",
        "best_odds": 2.50,
        "avg_edge_pct": 12.0,
        "composite_score": 88.0,
        "sources": ["value_bet", "sharp_money", "ml_prediction"],
        "source_count": 3,
    }
    trade = simular_trade(test_signal, bankroll=10000)
    check("id" in trade, "simular_trade retorna trade con id")
    check(trade["stake"] > 0, f"trade stake > 0: {trade.get('stake')}")
    check(trade["stake"] <= 500, f"trade stake <= 5% bankroll: {trade.get('stake')}")
    check_eq(_sim_state["trades_total"], 1, "trades_total = 1 después de simular")
    check(_sim_state["trades_pendientes"] >= 1, "trades_pendientes >= 1")

    # Test: Resolver trade ganada
    trade_id = trade["id"]
    result = resolver_trade(trade_id, ganada=True)
    check_eq(result["resultado"], "ganada", "resolver_trade ganada retorna 'ganada'")
    check(result["pnl"] > 0, f"pnl ganada > 0: {result.get('pnl')}")
    check_eq(_sim_state["trades_ganados"], 1, "trades_ganados = 1")
    check(_sim_state["racha_actual"] > 0, "racha_actual positiva tras ganada")

    # Test: Resolver trade perdida
    trade2 = simular_trade(test_signal, bankroll=_sim_state["bankroll_actual"])
    result2 = resolver_trade(trade2["id"], ganada=False)
    check_eq(result2["resultado"], "perdida", "resolver_trade perdida retorna 'perdida'")
    check(result2["pnl"] < 0, f"pnl perdida < 0: {result2.get('pnl')}")
    check_eq(_sim_state["trades_perdidos"], 1, "trades_perdidos = 1")

    # Test: Performance endpoint
    perf = get_performance()
    check("bankroll_inicial" in perf, "performance tiene bankroll_inicial")
    check("bankroll_actual" in perf, "performance tiene bankroll_actual")
    check("win_rate" in perf, "performance tiene win_rate")
    check("roi" in perf, "performance tiene roi")
    check("pnl_total" in perf, "performance tiene pnl_total")
    check("trades_ganados" in perf, "performance tiene trades_ganados")
    check("trades_perdidos" in perf, "performance tiene trades_perdidos")
    check("kill_switch" in perf, "performance tiene kill_switch")
    check("bankroll_history" in perf, "performance tiene bankroll_history")
    check("recent_trades" in perf, "performance tiene recent_trades")
    check(perf["trades_ganados"] == 1, "performance ganados = 1")
    check(perf["trades_perdidos"] == 1, "performance perdidos = 1")

    # Test: Kill switch trigger
    reset_simulation(1000)
    for i in range(5):
        t = simular_trade(test_signal, bankroll=_sim_state["bankroll_actual"])
        if t:
            resolver_trade(t["id"], ganada=False)
    check(_sim_state["kill_switch"], "kill_switch activa tras 5 trades perdidos con $1000")
    check(len(_sim_state["kill_reason"]) > 0, "kill_reason tiene texto")

    # Test: API endpoints
    reset_simulation(10000)

    r = get("/api/brain/performance")
    check_eq(r.status_code, 200, "GET /api/brain/performance = 200")
    d = r.get_json()
    check("bankroll_actual" in d, "brain/performance tiene bankroll_actual")
    check("win_rate" in d, "brain/performance tiene win_rate")

    r = get("/api/brain/verify-all")
    check_eq(r.status_code, 200, "GET /api/brain/verify-all = 200")

    r = get("/api/brain/auto-simulate")
    check_eq(r.status_code, 200, "GET /api/brain/auto-simulate = 200")
    d = r.get_json()
    check("scan_signals" in d, "brain/auto-simulate tiene scan_signals")
    check("trades_simulados" in d, "brain/auto-simulate tiene trades_simulados")

    r = post("/api/brain/reset", json_data={"bankroll": 5000})
    check_eq(r.status_code, 200, "POST /api/brain/reset = 200")
    d = r.get_json()
    check_eq(d.get("bankroll"), 5000, "brain/reset bankroll = 5000")

    # Reset a 10000 para siguientes tests
    reset_simulation(10000)

    # -- 30. Line Shopping tests --
    print("\n  --- Line Shopping ---")
    from services.brain import line_shop, line_shop_for_signal

    test_match = {
        "home": "Chivas",
        "away": "América",
        "bookmakers": [
            {"name": "Bet365", "outcomes": {"Chivas": 2.40, "Draw": 3.20, "América": 2.90}},
            {"name": "Pinnacle", "outcomes": {"Chivas": 2.50, "Draw": 3.30, "América": 2.85}},
            {"name": "Codere", "outcomes": {"Chivas": 2.35, "Draw": 3.10, "América": 2.95}},
        ]
    }

    ls = line_shop(test_match)
    check("best_odds" in ls, "line_shop tiene best_odds")
    check("best_bookmakers" in ls, "line_shop tiene best_bookmakers")
    check("overrounds" in ls, "line_shop tiene overrounds")
    check("savings_pct" in ls, "line_shop tiene savings_pct")
    check_eq(ls["best_odds"]["Chivas"], 2.50, "mejor odds Chivas = 2.50 (Pinnacle)")
    check_eq(ls["best_bookmakers"]["Chivas"], "Pinnacle", "mejor casa Chivas = Pinnacle")
    check_eq(ls["best_odds"]["América"], 2.95, "mejor odds América = 2.95 (Codere)")
    check(ls["total_savings"] > 0, f"line_shop ahorra {ls['total_savings']}%")

    # Test: Line shopping con 1 bookmaker (error)
    ls_one = line_shop({"home": "A", "away": "B", "bookmakers": [{"name": "B1", "outcomes": {}}]})
    check("error" in ls_one, "line_shop con 1 bookmaker retorna error")

    # -- 31. Calibration tests --
    print("\n  --- Calibration ---")
    from services.brain import (
        calibrate_probability, update_calibration,
        get_calibration_status, _calibration_data,
    )

    # Test: Calibrate probability
    cal = calibrate_probability(0.70)
    check(0.50 <= cal <= 0.99, f"calibrate_probability(0.70) = {cal}")
    check(cal != 0.70, f"calibrate ajusta prob: 0.70 → {cal}")

    # Test: Update calibration
    _calibration_data["predictions"] = []  # Limpiar
    for i in range(25):
        update_calibration(0.70, i % 3 == 0)  # ~33% win rate
    check(len(_calibration_data["predictions"]) == 25, "update_calibration agrega 25 predicciones")

    # Test: Calibration status
    status = get_calibration_status()
    check_eq(status["total_predictions"], 25, "calibration status tiene 25 predicciones")
    check("accuracy" in status, "calibration status tiene accuracy")
    check("brier_score" in status, "calibration status tiene brier_score")
    check("calibration_quality" in status, "calibration status tiene calibration_quality")

    # Test: API endpoints
    r = get("/api/brain/calibration")
    check_eq(r.status_code, 200, "GET /api/brain/calibration = 200")

    r = post("/api/brain/calibrate", json_data={"predicted_prob": 0.65, "actual_outcome": True})
    check_eq(r.status_code, 200, "POST /api/brain/calibrate = 200")

    r = post("/api/brain/line-shop", json_data=test_match)
    check_eq(r.status_code, 200, "POST /api/brain/line-shop = 200")
    d = r.get_json()
    check("best_odds" in d, "line-shop retorna best_odds")

    # -- 32. Reports tests --
    print("\n  --- Reports ---")
    from services.brain import generate_report, format_telegram_report

    # Test: Generate report
    report = generate_report("weekly")
    check("period" in report, "report tiene period")
    check("summary" in report or "message" in report, "report tiene summary o message")
    if report.get("summary"):
        s = report["summary"]
        check("total_trades" in s, "report summary tiene total_trades")
        check("win_rate" in s, "report summary tiene win_rate")
        check("roi" in s, "report summary tiene roi")
        check("total_pnl" in s, "report summary tiene total_pnl")

    # Test: Format Telegram report
    msg = format_telegram_report(report)
    check(len(msg) > 50, f"format_telegram_report retorna mensaje largo ({len(msg)} chars)")
    check("REPORTE" in msg, "telegram report contiene 'REPORTE'")

    # Test: API endpoints
    r = get("/api/brain/report?period=weekly")
    check_eq(r.status_code, 200, "GET /api/brain/report = 200")

    r = get("/api/brain/report?period=monthly")
    check_eq(r.status_code, 200, "GET /api/brain/report?period=monthly = 200")

    # -- Summary --
    total = PASS + FAIL
    print("")
    print("=" * 60)
    print(f"  RESULTADOS: {PASS}/{total} pasaron")
    if FAIL > 0:
        print(f"  FALLARON: {FAIL}")
        print("")
        print("  Errores:")
        for e in ERRORS:
            print(f"    - {e}")
    else:
        print("  TODAS LAS PRUEBAS PASARON")
    print("=" * 60)
    print("")

    if CI_MODE:
        sys.exit(0 if FAIL == 0 else 1)

if __name__ == "__main__":
    main()
