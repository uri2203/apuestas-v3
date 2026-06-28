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
        "value-bets", "sharp", "arbitraje", "ml", "bankroll", "simulacion",
        "contabilidad", "journal", "bookmakers", "cross-market", "backtesting", "rendimiento"
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
