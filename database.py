"""
Base de datos — PostgreSQL (Supabase) en producción, SQLite en desarrollo.

Detecta automáticamente según DATABASE_URL:
- Si existe DATABASE_URL → PostgreSQL (Supabase)
- Si no → SQLite local (desarrollo)
"""

import os
import logging
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
_USE_PG = bool(DATABASE_URL)


# ── Conexión ──────────────────────────────────────────────────────────────────

def get_connection():
    if _USE_PG:
        import psycopg2
        import psycopg2.extras
        url = DATABASE_URL
        if "sslmode" not in url:
            url += "?sslmode=require" if "?" not in url else "&sslmode=require"
        conn = psycopg2.connect(url)
        conn.autocommit = False
        return conn
    else:
        import sqlite3
        conn = sqlite3.connect(
            os.getenv("DB_PATH", "apuestaspro.db"),
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=10000")
        return conn


@contextmanager
def db():
    """Context manager: abre, commit o rollback, cierra."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _row_to_dict(row) -> dict:
    """Convierte una fila (psycopg2 o sqlite3) a dict."""
    if row is None:
        return None
    if hasattr(row, "_asdict"):          # psycopg2 RealDictRow
        return dict(row)
    if hasattr(row, "keys"):             # sqlite3.Row
        return dict(row)
    return dict(row)


def rows_to_list(rows) -> list:
    return [_row_to_dict(r) for r in rows] if rows else []


# ── Placeholder portátil ──────────────────────────────────────────────────────
# SQLite usa ? y PostgreSQL usa %s
PH = "%s" if _USE_PG else "?"


def _q(sql: str) -> str:
    """Reemplaza ? por %s si estamos en PostgreSQL."""
    return sql.replace("?", "%s") if _USE_PG else sql


# ── SQL Date helpers portátiles (SQLite vs PostgreSQL) ───────────────────────

def SQL_TODAY() -> str:
    """Retorna SQL para 'hoy' (sin fecha ni hora)."""
    return "CURRENT_DATE" if _USE_PG else "date('now')"

def SQL_DAYS_AGO(n: str = "?") -> str:
    """Retorna SQL para 'N días atrás'. n es el placeholder o literal."""
    if _USE_PG:
        return f"CURRENT_DATE - INTERVAL '1 day' * {n}"
    return f"date('now', '-' || {n} || ' days')"

def SQL_DATE(col: str) -> str:
    """Extrae la fecha (sin hora) de una columna timestamp."""
    return f"{col}::date" if _USE_PG else f"date({col})"


# ── Crear tablas ──────────────────────────────────────────────────────────────

def init_db() -> None:
    """Crea todas las tablas si no existen. No fatal si DB no disponible."""
    try:
        if _USE_PG:
            _init_pg()
        else:
            _init_sqlite()
        logger.info("DB inicializada (%s)", "PostgreSQL/Supabase" if _USE_PG else "SQLite")
    except Exception as e:
        logger.error("DB no disponible: %s — sistema funciona sin persistencia", e)


def _init_pg() -> None:
    import psycopg2
    import psycopg2.extras
    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    conn.autocommit = True
    cur = conn.cursor()

    statements = [
        """CREATE TABLE IF NOT EXISTS predictions (
            id             SERIAL PRIMARY KEY,
            created_at     TIMESTAMP DEFAULT NOW(),
            home           TEXT NOT NULL,
            away           TEXT NOT NULL,
            liga           TEXT DEFAULT 'Liga MX',
            fecha_partido  TEXT,
            pronostico     TEXT,
            confianza_pct  REAL,
            prob_local     REAL,
            prob_empate    REAL,
            prob_visitante REAL,
            xg_home        REAL,
            xg_away        REAL,
            modelo         TEXT,
            resultado_real TEXT,
            correcto       INTEGER,
            verificado_at  TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS bets (
            id               SERIAL PRIMARY KEY,
            created_at       TIMESTAMP DEFAULT NOW(),
            partido          TEXT NOT NULL,
            liga             TEXT DEFAULT 'Liga MX',
            mercado          TEXT DEFAULT '1X2',
            seleccion        TEXT NOT NULL,
            cuota            REAL NOT NULL,
            monto            REAL NOT NULL,
            kelly_pct        REAL,
            edge_pct         REAL,
            bankroll_antes   REAL,
            resultado        TEXT DEFAULT 'pendiente',
            ganancia_neta    REAL DEFAULT 0,
            bankroll_despues REAL,
            notas            TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS bankroll_history (
            id        SERIAL PRIMARY KEY,
            fecha     TIMESTAMP DEFAULT NOW(),
            bankroll  REAL NOT NULL,
            evento    TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS arbitrage_log (
            id          SERIAL PRIMARY KEY,
            detected_at TIMESTAMP DEFAULT NOW(),
            partido     TEXT,
            liga        TEXT,
            profit_pct  REAL,
            resultados  TEXT,
            stakes      TEXT,
            notificado  INTEGER DEFAULT 0
        )""",
        """CREATE TABLE IF NOT EXISTS value_bets_log (
            id          SERIAL PRIMARY KEY,
            detected_at TIMESTAMP DEFAULT NOW(),
            partido     TEXT,
            liga        TEXT,
            resultado   TEXT,
            casa        TEXT,
            cuota       REAL,
            edge_pct    REAL,
            notificado  INTEGER DEFAULT 0
        )""",
        """CREATE TABLE IF NOT EXISTS alerts_log (
            id         SERIAL PRIMARY KEY,
            created_at TIMESTAMP DEFAULT NOW(),
            tipo       TEXT,
            partido    TEXT,
            detalle    TEXT,
            urgencia   TEXT,
            canal      TEXT DEFAULT 'telegram'
        )""",
        """CREATE TABLE IF NOT EXISTS backtest_results (
            id            SERIAL PRIMARY KEY,
            created_at    TIMESTAMP DEFAULT NOW(),
            tipo          TEXT,
            config        TEXT,
            resumen       TEXT,
            bankroll_hist TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS simulated_trades (
            id                   SERIAL PRIMARY KEY,
            created_at           TIMESTAMP DEFAULT NOW(),
            partido              TEXT,
            liga                 TEXT,
            seleccion            TEXT,
            casa                 TEXT,
            cuota                REAL,
            edge_pct             REAL,
            stake_simulado       REAL,
            bankroll_al_momento  REAL,
            resultado_simulado   TEXT DEFAULT 'pendiente',
            pnl_real             REAL DEFAULT 0,
            resultado_real_partido TEXT,
            fecha_partido        TEXT,
            verificado_at        TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS bookmaker_ratings (
            id              SERIAL PRIMARY KEY,
            bookmaker       TEXT,
            avg_overround   REAL DEFAULT 5.0,
            avg_cuota       REAL DEFAULT 0,
            apariciones     INTEGER DEFAULT 0,
            avg_clv         REAL DEFAULT 0,
            velocidad_ajuste INTEGER DEFAULT 0,
            fecha_rating    TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS accounting_transactions (
            id          SERIAL PRIMARY KEY,
            created_at  TIMESTAMP DEFAULT NOW(),
            tipo        TEXT NOT NULL,
            monto       REAL NOT NULL,
            saldo_resultante REAL DEFAULT 0,
            categoria   TEXT,
            estrategia  TEXT,
            descripcion TEXT,
            partido     TEXT,
            ref_id      INTEGER
        )""",
        """CREATE TABLE IF NOT EXISTS trading_journal (
            id          SERIAL PRIMARY KEY,
            created_at  TIMESTAMP DEFAULT NOW(),
            tipo_accion TEXT NOT NULL,
            partido     TEXT,
            liga        TEXT,
            mercado     TEXT,
            seleccion   TEXT,
            cuota       REAL,
            monto       REAL,
            edge_pct    REAL,
            score_sharp INTEGER DEFAULT 0,
            overround   REAL DEFAULT 0,
            casa        TEXT,
            estrategia  TEXT,
            resultado   TEXT,
            pnl         REAL DEFAULT 0,
            snapshot    TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS model_performance (
            id              SERIAL PRIMARY KEY,
            created_at      TIMESTAMP DEFAULT NOW(),
            liga            TEXT,
            modelo          TEXT,
            accuracy        REAL,
            log_loss        REAL,
            n_muestras      INTEGER,
            n_features      INTEGER,
            pesos           TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS feature_importance (
            id              SERIAL PRIMARY KEY,
            liga            TEXT,
            feature_name    TEXT,
            importance      REAL,
            updated_at      TIMESTAMP DEFAULT NOW(),
            UNIQUE(liga, feature_name)
        )""",
        """CREATE TABLE IF NOT EXISTS ml_predictions_v2 (
            id              SERIAL PRIMARY KEY,
            created_at      TIMESTAMP DEFAULT NOW(),
            liga            TEXT,
            home            TEXT,
            away            TEXT,
            pronostico      TEXT,
            confianza_pct   REAL,
            prob_local      REAL,
            prob_empate     REAL,
            prob_visitante  REAL,
            cuota_justa_local   REAL,
            cuota_justa_empate  REAL,
            cuota_justa_visitante REAL,
            modelo          TEXT DEFAULT 'advanced_ensemble',
            fecha_partido   TEXT,
            resultado_real  TEXT,
            correcto        INTEGER,
            verificado_at   TEXT
        )""",
        "CREATE INDEX IF NOT EXISTS idx_bets_resultado ON bets(resultado)",
        "CREATE INDEX IF NOT EXISTS idx_pred_correcto  ON predictions(correcto)",
    ]
    for stmt in statements:
        cur.execute(stmt)
    cur.close()
    conn.close()


# ── Seed data ─────────────────────────────────────────────────────────────────
def seed_demo_data() -> dict:
    """Pobla la base con datos iniciales realistas.
    Usa una sola conexion con autocommit=True (PG) o commit lote (SQLite)."""
    from datetime import datetime, timedelta
    import random, json

    results = {"insertados": {}, "errores": []}
    today = datetime.utcnow()
    PH = "%s" if _USE_PG else "?"

    def _get_conn():
        if _USE_PG:
            import psycopg2
            url = DATABASE_URL
            if "sslmode" not in url:
                url += "?sslmode=require" if "?" not in url else "&sslmode=require"
            conn = psycopg2.connect(url)
            conn.autocommit = True
            return conn
        else:
            import sqlite3
            conn = sqlite3.connect(os.getenv("DB_PATH", "apuestaspro.db"))
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.execute("PRAGMA synchronous=OFF")
            return conn

    conn = _get_conn()
    cur = conn.cursor()

    def _exec(sql, params=None):
        nonlocal cur
        try:
            sql_final = sql if not _USE_PG else sql.replace("?", "%s")
            cur.execute(sql_final, params or ())
        except Exception as e:
            results["errores"].append(f"{sql[:50]}: {str(e)[:150]}")
            logger.warning("Seed exec: %s", e)

    def _insert(table, columns, rows):
        if not rows:
            return
        cols = ", ".join(columns)
        ph = ", ".join([PH] * len(columns))
        sql = f"INSERT INTO {table} ({cols}) VALUES ({ph})"
        for r in rows:
            _exec(sql, r)

    # - bankroll_history
    br_rows = []
    br = 10000.0
    for i in range(90):
        d = today - timedelta(days=89 - i)
        cambio = random.uniform(-300, 400)
        br = max(1000, br + cambio)
        br_rows.append((
            d.strftime("%Y-%m-%d %H:%M:%S"),
            round(br, 2),
            f"Inicialización {i+1}",
        ))
    _insert("bankroll_history", ("fecha", "bankroll", "evento"), br_rows)

    # - bets
    equipos = [
        ("América", "Chivas"), ("Cruz Azul", "Pumas"), ("Tigres", "Monterrey"),
        ("Barcelona", "Real Madrid"), ("Man City", "Liverpool"), ("Bayern", "Dortmund"),
        ("PSG", "Marseille"), ("Juventus", "Milan"), ("Inter", "Roma"),
        ("Lakers", "Celtics"), ("Warriors", "Nuggets"), ("Bucks", "76ers"),
    ]
    resultados = ["ganada", "perdida", "pendiente"]
    bet_rows = []
    for i in range(120):
        d = today - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))
        eq = random.choice(equipos)
        cuota = round(random.uniform(1.5, 4.5), 2)
        edge = round(random.uniform(-5, 15), 1)
        sel = random.choice(["Local", "Visitante", "Empate"])
        monto = round(random.uniform(200, 2000), 0)
        res = random.choice(resultados[:2] if i < 100 else resultados)
        pnl = round(monto * (cuota - 1), 2) if res == "ganada" else round(-monto, 2) if res == "perdida" else 0
        bet_rows.append((
            d.strftime("%Y-%m-%d %H:%M:%S"),
            f"{eq[0]} vs {eq[1]}",
            random.choice(["Liga MX", "Premier League", "La Liga", "NBA", "Bundesliga"]),
            "1X2", sel, cuota, monto,
            round(random.uniform(0.5, 5), 1), edge,
            round(random.uniform(8000, 12000), 2), res, pnl,
            round(random.uniform(8000, 12000), 2), "",
        ))
    _insert("bets", (
        "created_at", "partido", "liga", "mercado", "seleccion", "cuota", "monto",
        "kelly_pct", "edge_pct", "bankroll_antes", "resultado", "ganancia_neta",
        "bankroll_despues", "notas",
    ), bet_rows)

    # - predictions
    pred_rows = []
    for i in range(80):
        d = today - timedelta(days=random.randint(0, 60), hours=random.randint(0, 23))
        eq = random.choice(equipos)
        conf = round(random.uniform(55, 92), 1)
        probs = [round(random.uniform(0.2, 0.6), 3) for _ in range(3)]
        s = sum(probs)
        probs = [round(p / s, 3) for p in probs]
        correcto = random.choice([0, 1, None])
        pred_rows.append((
            d.strftime("%Y-%m-%d %H:%M:%S"),
            eq[0], eq[1],
            random.choice(["Liga MX", "Premier", "La Liga"]),
            (today - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            random.choice(["Local", "Visitante", "Empate"]), conf,
            probs[0], probs[1], probs[2],
            round(random.uniform(0.5, 3), 2),
            round(random.uniform(0.3, 2.5), 2),
            "ensemble_v1",
            random.choice(["Local", "Visitante", "Empate", None]),
            correcto,
            (today - timedelta(days=random.randint(0, 5))).strftime("%Y-%m-%d") if correcto is not None else None,
        ))
    _insert("predictions", (
        "created_at", "home", "away", "liga", "fecha_partido", "pronostico",
        "confianza_pct", "prob_local", "prob_empate", "prob_visitante",
        "xg_home", "xg_away", "modelo", "resultado_real", "correcto", "verificado_at",
    ), pred_rows)

    # - value_bets_log
    vb_rows = []
    for i in range(40):
        d = today - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))
        eq = random.choice(equipos)
        vb_rows.append((
            d.strftime("%Y-%m-%d %H:%M:%S"),
            f"{eq[0]} vs {eq[1]}",
            random.choice(["Liga MX", "Premier", "La Liga"]),
            random.choice(["Local", "Visitante", "Empate"]),
            random.choice(["Bet365", "DraftKings", "FanDuel", "BetMGM"]),
            round(random.uniform(2.0, 6.0), 2),
            round(random.uniform(3, 25), 1),
            0,
        ))
    _insert("value_bets_log", (
        "detected_at", "partido", "liga", "resultado", "casa", "cuota", "edge_pct", "notificado",
    ), vb_rows)

    # - simulated_trades
    sim_rows = []
    for i in range(50):
        d = today - timedelta(days=random.randint(0, 45), hours=random.randint(0, 23))
        eq = random.choice(equipos)
        cuota = round(random.uniform(1.8, 5.0), 2)
        edge = round(random.uniform(1, 20), 1)
        stake = round(random.uniform(100, 1000), 0)
        br_at = round(random.uniform(9000, 11000), 2)
        res = random.choice(["ganada", "perdida", "pendiente"])
        pnl = round(stake * (cuota - 1), 2) if res == "ganada" else round(-stake, 2) if res == "perdida" else 0
        sim_rows.append((
            d.strftime("%Y-%m-%d %H:%M:%S"),
            f"{eq[0]} vs {eq[1]}",
            random.choice(["Liga MX", "NBA", "Premier"]),
            random.choice(["Local", "Visitante"]),
            random.choice(["Bet365", "DraftKings"]),
            cuota, edge, stake, br_at, res, pnl,
            random.choice(["Local", "Visitante"]),
            (today - timedelta(days=random.randint(0, 15))).strftime("%Y-%m-%d"),
            (today - timedelta(days=random.randint(0, 3))).strftime("%Y-%m-%d") if res != "pendiente" else None,
        ))
    _insert("simulated_trades", (
        "created_at", "partido", "liga", "seleccion", "casa", "cuota", "edge_pct",
        "stake_simulado", "bankroll_al_momento", "resultado_simulado", "pnl_real",
        "resultado_real_partido", "fecha_partido", "verificado_at",
    ), sim_rows)

    # - accounting_transactions
    acct_rows = []
    saldo = 10000.0
    for i in range(60):
        d = today - timedelta(days=59 - i, hours=random.randint(0, 12))
        es_ingreso = random.random() > 0.45
        monto = round(random.uniform(100, 2000), 2) if es_ingreso else round(random.uniform(100, 1500), 2)
        saldo = saldo + monto if es_ingreso else saldo - monto
        acct_rows.append((
            d.strftime("%Y-%m-%d %H:%M:%S"),
            "ingreso" if es_ingreso else "egreso", monto, round(saldo, 2),
            random.choice(["apuesta", "retiro", "deposito", "comision"]),
            random.choice(["Value Bets", "Sharp Money", "ML Predictivo", "Arbitraje"]),
            f"Inicialización {i+1}", "", None,
        ))
    _insert("accounting_transactions", (
        "created_at", "tipo", "monto", "saldo_resultante", "categoria", "estrategia",
        "descripcion", "partido", "ref_id",
    ), acct_rows)

    # - trading_journal
    jr_rows = []
    for i in range(80):
        d = today - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
        eq = random.choice(equipos)
        cuota = round(random.uniform(1.5, 5.0), 2)
        edge = round(random.uniform(-3, 18), 1)
        res = random.choice(["ganada", "perdida", "abierta"])
        pnl = round(random.uniform(-500, 1500), 2)
        jr_rows.append((
            d.strftime("%Y-%m-%d %H:%M:%S"),
            random.choice(["apuesta", "value_bet", "sharp_alerta", "simulacion"]),
            f"{eq[0]} vs {eq[1]}",
            random.choice(["Liga MX", "Premier", "NBA"]),
            "1X2", random.choice(["Local", "Visitante", "Empate"]),
            cuota, round(random.uniform(200, 1500), 0), edge,
            random.randint(0, 10), round(random.uniform(2, 8), 2),
            random.choice(["Bet365", "DraftKings"]),
            random.choice(["Value", "Sharp", "ML", "Manual"]),
            res, pnl, "{}",
        ))
    _insert("trading_journal", (
        "created_at", "tipo_accion", "partido", "liga", "mercado", "seleccion",
        "cuota", "monto", "edge_pct", "score_sharp", "overround", "casa",
        "estrategia", "resultado", "pnl", "snapshot",
    ), jr_rows)

    # - bookmaker_ratings
    bm_rows = [
        ("Bet365", round(random.uniform(2.5, 5.0), 2), round(random.uniform(1.8, 2.2), 2),
         random.randint(50, 200), round(random.uniform(0.002, 0.015), 4),
         random.randint(1, 10), today.strftime("%Y-%m-%d")),
        ("DraftKings", round(random.uniform(3.0, 5.5), 2), round(random.uniform(1.7, 2.1), 2),
         random.randint(40, 180), round(random.uniform(0.003, 0.018), 4),
         random.randint(1, 8), today.strftime("%Y-%m-%d")),
        ("FanDuel", round(random.uniform(2.8, 5.2), 2), round(random.uniform(1.75, 2.15), 2),
         random.randint(30, 150), round(random.uniform(0.002, 0.016), 4),
         random.randint(1, 9), today.strftime("%Y-%m-%d")),
        ("BetMGM", round(random.uniform(3.2, 5.8), 2), round(random.uniform(1.7, 2.1), 2),
         random.randint(25, 120), round(random.uniform(0.004, 0.020), 4),
         random.randint(1, 7), today.strftime("%Y-%m-%d")),
        ("Caesars", round(random.uniform(3.5, 6.0), 2), round(random.uniform(1.65, 2.05), 2),
         random.randint(20, 100), round(random.uniform(0.005, 0.022), 4),
         random.randint(1, 6), today.strftime("%Y-%m-%d")),
    ]
    _insert("bookmaker_ratings", (
        "bookmaker", "avg_overround", "avg_cuota", "apariciones", "avg_clv",
        "velocidad_ajuste", "fecha_rating",
    ), bm_rows)

    # - alerts_log
    alert_rows = []
    for i in range(20):
        d = today - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
        eq = random.choice(equipos)
        alert_rows.append((
            d.strftime("%Y-%m-%d %H:%M:%S"),
            random.choice(["value_bet", "sharp_move", "steam", "arbitraje", "ml_alerta"]),
            f"{eq[0]} vs {eq[1]}",
            f"Edge detectado: {round(random.uniform(2, 20), 1)}%",
            random.choice(["alta", "media", "baja"]), "telegram",
        ))
    _insert("alerts_log", (
        "created_at", "tipo", "partido", "detalle", "urgencia", "canal",
    ), alert_rows)

    # - backtest_results
    bt_rows = [
        (today.strftime("%Y-%m-%d %H:%M:%S"), "full",
         '{"estrategia":"value","edge_min":2}',
         '{"total":120,"ganadas":65,"perdidas":55,"roi":8.5,"sharpe":1.2}',
         json.dumps([10000, 10200, 10100, 10500, 10800])),
        (today.strftime("%Y-%m-%d %H:%M:%S"), "modelo",
         '{"modelo":"mlp","liga":"Liga MX"}',
         '{"total":45,"ganadas":28,"perdidas":17,"roi":12.3,"sharpe":1.8}',
         json.dumps([10000, 10150, 10300, 10200, 10600])),
        (today.strftime("%Y-%m-%d %H:%M:%S"), "simulacion",
         '{"tipo":"montecarlo","n":10000}',
         '{"total":10000,"ganadas":5234,"perdidas":4766,"roi":6.7,"sharpe":0.95}',
         json.dumps([10000, 10050, 10100, 9950, 10200])),
    ]
    _insert("backtest_results", (
        "created_at", "tipo", "config", "resumen", "bankroll_hist",
    ), bt_rows)

    # - feature_importance
    feat_rows = []
    ligas = ["Liga MX", "Premier League", "La Liga", "NBA"]
    features = [
        "xg_diff", "ppg_home", "ppg_away", "form_5_home", "form_5_away",
        "gf_avg_home", "ga_avg_away", "h2h_wr", "b2b", "rest_days_diff",
        "market_volume", "line_movement", "sharp_score", "public_pct",
        "kelly_pct", "edge_pct", "clv", "overround", "injury_index",
        "weather_factor", "ref_factor", "travel_dist", "altura", "presion_alta",
    ]
    for liga in ligas:
        remaining = 1.0
        f_list = features.copy()
        random.shuffle(f_list)
        for f in f_list[:12]:
            imp = round(random.uniform(0.02, min(0.25, remaining)), 3)
            remaining -= imp
            feat_rows.append((liga, f, imp))
        if remaining > 0:
            feat_rows.append((liga, "other", round(remaining, 3)))
    _insert("feature_importance", ("liga", "feature_name", "importance"), feat_rows)

    # - model_performance
    perf_rows = []
    for liga in ligas:
        for modelo in ["mlp", "gbm", "advanced_ensemble"]:
            perf_rows.append((
                today.strftime("%Y-%m-%d %H:%M:%S"), liga, modelo,
                round(random.uniform(0.55, 0.82), 3),
                round(random.uniform(0.35, 0.65), 3),
                random.randint(50, 300), random.randint(10, 30), "{}",
            ))
    _insert("model_performance", (
        "created_at", "liga", "modelo", "accuracy", "log_loss",
        "n_muestras", "n_features", "pesos",
    ), perf_rows)

    # - ml_predictions_v2
    mlp_rows = []
    for i in range(30):
        d = today - timedelta(days=random.randint(0, 20), hours=random.randint(0, 23))
        eq = random.choice(equipos)
        conf = round(random.uniform(55, 95), 1)
        probs = [round(random.uniform(0.2, 0.6), 3) for _ in range(3)]
        s = sum(probs)
        probs = [round(p / s, 3) for p in probs]
        correcto = random.choice([0, 1, None])
        mlp_rows.append((
            d.strftime("%Y-%m-%d %H:%M:%S"),
            random.choice(["Liga MX", "Premier League", "La Liga"]),
            eq[0], eq[1],
            random.choice(["Local", "Visitante", "Empate"]), conf,
            probs[0], probs[1], probs[2],
            round(1 / max(probs[0], 0.01), 2),
            round(1 / max(probs[1], 0.01), 2),
            round(1 / max(probs[2], 0.01), 2),
            "advanced_ensemble",
            (today - timedelta(days=random.randint(0, 10))).strftime("%Y-%m-%d"),
            random.choice(["Local", "Visitante", "Empate", None]),
            correcto,
            (today - timedelta(days=random.randint(0, 3))).strftime("%Y-%m-%d") if correcto is not None else None,
        ))
    _insert("ml_predictions_v2", (
        "created_at", "liga", "home", "away", "pronostico", "confianza_pct",
        "prob_local", "prob_empate", "prob_visitante",
        "cuota_justa_local", "cuota_justa_empate", "cuota_justa_visitante",
        "modelo", "fecha_partido", "resultado_real", "correcto", "verificado_at",
    ), mlp_rows)

    # Summary - usar misma conexion
    counts = {}
    tables = [
        "bankroll_history", "bets", "predictions", "value_bets_log",
        "simulated_trades", "accounting_transactions", "trading_journal",
        "bookmaker_ratings", "alerts_log", "backtest_results",
        "feature_importance", "model_performance", "ml_predictions_v2",
    ]
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) as n FROM {t}")
            row = cur.fetchone()
            counts[t] = row[0] if row else 0
        except Exception as e:
            counts[t] = 0
            logger.warning("Seed count %s: %s", t, e)

    if not _USE_PG:
        conn.commit()
    cur.close()
    conn.close()

    results["insertados"] = counts
    results["total_insertados"] = sum(counts.values())
    results["status"] = "ok" if not results["errores"] else "con_errores"
    logger.info("Seed completo: %d registros, %d errores",
                results["total_insertados"], len(results["errores"]))
    return results


def _init_sqlite() -> None:
    import sqlite3
    db_path = os.getenv("DB_PATH", "apuestaspro.db")
    conn = sqlite3.connect(db_path)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS predictions (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at     TEXT DEFAULT (datetime('now')),
        home           TEXT NOT NULL, away TEXT NOT NULL,
        liga           TEXT DEFAULT 'Liga MX', fecha_partido TEXT,
        pronostico     TEXT, confianza_pct REAL,
        prob_local REAL, prob_empate REAL, prob_visitante REAL,
        xg_home REAL, xg_away REAL, modelo TEXT,
        resultado_real TEXT, correcto INTEGER, verificado_at TEXT
    );
    CREATE TABLE IF NOT EXISTS bets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (datetime('now')),
        partido TEXT NOT NULL, liga TEXT DEFAULT 'Liga MX',
        mercado TEXT DEFAULT '1X2', seleccion TEXT NOT NULL,
        cuota REAL NOT NULL, monto REAL NOT NULL,
        kelly_pct REAL, edge_pct REAL, bankroll_antes REAL,
        resultado TEXT DEFAULT 'pendiente',
        ganancia_neta REAL DEFAULT 0, bankroll_despues REAL, notas TEXT
    );
    CREATE TABLE IF NOT EXISTS bankroll_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT DEFAULT (datetime('now')),
        bankroll REAL NOT NULL, evento TEXT
    );
    CREATE TABLE IF NOT EXISTS arbitrage_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        detected_at TEXT DEFAULT (datetime('now')),
        partido TEXT, liga TEXT,
        profit_pct REAL, resultados TEXT, stakes TEXT,
        notificado INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS value_bets_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        detected_at TEXT DEFAULT (datetime('now')),
        partido TEXT, liga TEXT, resultado TEXT,
        casa TEXT, cuota REAL, edge_pct REAL, notificado INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS alerts_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (datetime('now')),
        tipo TEXT, partido TEXT, detalle TEXT, urgencia TEXT,
        canal TEXT DEFAULT 'telegram'
    );
    CREATE TABLE IF NOT EXISTS backtest_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (datetime('now')),
        tipo TEXT, config TEXT, resumen TEXT, bankroll_hist TEXT
    );
    CREATE TABLE IF NOT EXISTS simulated_trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (datetime('now')),
        partido TEXT, liga TEXT, seleccion TEXT,
        casa TEXT, cuota REAL, edge_pct REAL,
        stake_simulado REAL, bankroll_al_momento REAL,
        resultado_simulado TEXT DEFAULT 'pendiente',
        pnl_real REAL DEFAULT 0,
        resultado_real_partido TEXT,
        fecha_partido TEXT, verificado_at TEXT
    );
    CREATE TABLE IF NOT EXISTS bookmaker_ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bookmaker TEXT,
        avg_overround REAL DEFAULT 5.0,
        avg_cuota REAL DEFAULT 0,
        apariciones INTEGER DEFAULT 0,
        avg_clv REAL DEFAULT 0,
        velocidad_ajuste INTEGER DEFAULT 0,
        fecha_rating TEXT
    );
    CREATE TABLE IF NOT EXISTS accounting_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (datetime('now')),
        tipo TEXT NOT NULL, monto REAL NOT NULL,
        saldo_resultante REAL DEFAULT 0,
        categoria TEXT, estrategia TEXT,
        descripcion TEXT, partido TEXT, ref_id INTEGER
    );
    CREATE TABLE IF NOT EXISTS trading_journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (datetime('now')),
        tipo_accion TEXT NOT NULL, partido TEXT,
        liga TEXT, mercado TEXT, seleccion TEXT,
        cuota REAL, monto REAL, edge_pct REAL,
        score_sharp INTEGER DEFAULT 0,
        overround REAL DEFAULT 0, casa TEXT,
        estrategia TEXT, resultado TEXT,
        pnl REAL DEFAULT 0, snapshot TEXT
    );
    CREATE TABLE IF NOT EXISTS model_performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (datetime('now')),
        liga TEXT, modelo TEXT,
        accuracy REAL, log_loss REAL,
        n_muestras INTEGER, n_features INTEGER,
        pesos TEXT
    );
    CREATE TABLE IF NOT EXISTS feature_importance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        liga TEXT, feature_name TEXT,
        importance REAL,
        updated_at TEXT DEFAULT (datetime('now')),
        UNIQUE(liga, feature_name)
    );
    CREATE TABLE IF NOT EXISTS ml_predictions_v2 (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT DEFAULT (datetime('now')),
        liga TEXT, home TEXT, away TEXT,
        pronostico TEXT, confianza_pct REAL,
        prob_local REAL, prob_empate REAL, prob_visitante REAL,
        cuota_justa_local REAL, cuota_justa_empate REAL, cuota_justa_visitante REAL,
        modelo TEXT DEFAULT 'advanced_ensemble',
        fecha_partido TEXT, resultado_real TEXT,
        correcto INTEGER, verificado_at TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_bets_resultado ON bets(resultado);
    CREATE INDEX IF NOT EXISTS idx_pred_correcto  ON predictions(correcto);
    """)
    conn.commit()
    conn.close()


# ── Helpers de consulta ───────────────────────────────────────────────────────

def _fetchone(conn, sql: str, params: tuple = ()):
    if _USE_PG:
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cur = conn.cursor()
    cur.execute(_q(sql), params)
    row = cur.fetchone()
    cur.close()
    return _row_to_dict(row) if row else None


def _fetchall(conn, sql: str, params: tuple = ()):
    if _USE_PG:
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        cur = conn.cursor()
    cur.execute(_q(sql), params)
    rows = cur.fetchall()
    cur.close()
    return rows_to_list(rows)


def _execute(conn, sql: str, params: tuple = ()):
    is_insert = "INSERT" in sql.upper()
    if _USE_PG:
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if is_insert and "RETURNING" not in sql.upper():
            sql = _q(sql) + " RETURNING id"
        else:
            sql = _q(sql)
    else:
        cur = conn.cursor()
        sql = _q(sql)
    cur.execute(sql, params)
    last_id = None
    if is_insert:
        try:
            if _USE_PG:
                row = cur.fetchone()
                last_id = row["id"] if row else None
            else:
                last_id = cur.lastrowid
        except Exception:
            last_id = None
    cur.close()
    return last_id


# ── Funciones de acceso directo ───────────────────────────────────────────────

def get_bankroll_actual() -> float:
    with db() as conn:
        row = _fetchone(conn,
            "SELECT bankroll FROM bankroll_history ORDER BY id DESC LIMIT 1")
        return float(row["bankroll"]) if row else 0.0


def registrar_bankroll(monto: float, evento: str = "") -> None:
    with db() as conn:
        _execute(conn,
            "INSERT INTO bankroll_history (bankroll, evento) VALUES (?, ?)",
            (monto, evento))


def log_value_bet(partido, liga, resultado, casa, cuota, edge_pct) -> None:
    with db() as conn:
        _execute(conn,
            "INSERT INTO value_bets_log "
            "(partido, liga, resultado, casa, cuota, edge_pct) VALUES (?,?,?,?,?,?)",
            (partido, liga, resultado, casa, cuota, edge_pct))


def log_alert(tipo, partido, detalle, urgencia="MEDIA", canal="telegram") -> None:
    with db() as conn:
        _execute(conn,
            "INSERT INTO alerts_log (tipo, partido, detalle, urgencia, canal) "
            "VALUES (?,?,?,?,?)",
            (tipo, partido, detalle, urgencia, canal))


def log_arbitrage(partido, liga, profit_pct, resultados_json, stakes_json) -> None:
    with db() as conn:
        _execute(conn,
            "INSERT INTO arbitrage_log (partido, liga, profit_pct, resultados, stakes) "
            "VALUES (?,?,?,?,?)",
            (partido, liga, profit_pct, resultados_json, stakes_json))


# ── Consultas para resumen diario ─────────────────────────────────────────────

def count_bets_today() -> dict:
    """Cuenta apuestas de hoy: total, ganadas, perdidas, pendientes, ganancia neta."""
    dc = "created_at::date" if _USE_PG else "date(created_at)"
    td = "CURRENT_DATE" if _USE_PG else "date('now')"
    sql = f"""SELECT
               COUNT(*) as total,
               SUM(CASE WHEN resultado='ganada' THEN 1 ELSE 0 END) as ganadas,
               SUM(CASE WHEN resultado='perdida' THEN 1 ELSE 0 END) as perdidas,
               SUM(CASE WHEN resultado='pendiente' THEN 1 ELSE 0 END) as pendientes,
               COALESCE(SUM(ganancia_neta), 0) as ganancia_neta
             FROM bets WHERE {dc} = {td}"""
    with db() as conn:
        r = _fetchone(conn, sql)
    if not r:
        return {"total": 0, "ganadas": 0, "perdidas": 0, "pendientes": 0, "ganancia_neta": 0}
    return {k: (v or 0) for k, v in r.items()}


def count_predictions_today() -> dict:
    """Cuenta predicciones de hoy."""
    dc = "created_at::date" if _USE_PG else "date(created_at)"
    td = "CURRENT_DATE" if _USE_PG else "date('now')"
    sql = f"""SELECT
               COUNT(*) as total,
               SUM(CASE WHEN correcto=1 THEN 1 ELSE 0 END) as correctos,
               SUM(CASE WHEN correcto=0 THEN 1 ELSE 0 END) as incorrectos,
               SUM(CASE WHEN correcto IS NULL THEN 1 ELSE 0 END) as pendientes
             FROM predictions WHERE {dc} = {td}"""
    with db() as conn:
        r = _fetchone(conn, sql)
    if not r:
        return {"total": 0, "correctos": 0, "incorrectos": 0, "pendientes": 0}
    return {k: (v or 0) for k, v in r.items()}


def count_value_bets_today() -> dict:
    """Cuenta value bets detectados hoy."""
    dc = "detected_at::date" if _USE_PG else "date(detected_at)"
    td = "CURRENT_DATE" if _USE_PG else "date('now')"
    sql = f"""SELECT
               COUNT(*) as total,
               COALESCE(AVG(edge_pct), 0) as avg_edge
             FROM value_bets_log WHERE {dc} = {td}"""
    with db() as conn:
        r = _fetchone(conn, sql)
    if not r:
        return {"total": 0, "avg_edge": 0}
    return {k: (v or 0) for k, v in r.items()}


def count_alerts_today() -> dict:
    """Cuenta alertas de hoy por urgencia."""
    dc = "created_at::date" if _USE_PG else "date(created_at)"
    td = "CURRENT_DATE" if _USE_PG else "date('now')"
    sql = f"""SELECT
               SUM(CASE WHEN urgencia='ALTA' THEN 1 ELSE 0 END) as altas,
               SUM(CASE WHEN urgencia='MEDIA' THEN 1 ELSE 0 END) as medias,
               SUM(CASE WHEN urgencia='BAJA' THEN 1 ELSE 0 END) as bajas,
               COUNT(*) as total
             FROM alerts_log WHERE {dc} = {td}"""
    with db() as conn:
        r = _fetchone(conn, sql)
    if not r:
        return {"altas": 0, "medias": 0, "bajas": 0, "total": 0}
    return {k: (v or 0) for k, v in r.items()}


# ── Consultas de rendimiento ─────────────────────────────────────────────────

def get_bankroll_history(days: int = 30) -> list[dict]:
    """Historial de bankroll para gráficas."""
    ago = "CURRENT_DATE - INTERVAL '1 day' * ?" if _USE_PG else "date('now', '-' || ? || ' days')"
    sql = f"""SELECT fecha, bankroll FROM bankroll_history
             WHERE fecha >= {ago}
             ORDER BY fecha ASC"""
    with db() as conn:
        rows = _fetchall(conn, sql, (days,))
    return rows or []


def get_bets_stats(days: int = 30) -> dict:
    """Estadísticas generales de apuestas en los últimos N días."""
    dc = "created_at::date" if _USE_PG else "date(created_at)"
    ago = "CURRENT_DATE - INTERVAL '1 day' * ?" if _USE_PG else "date('now', '-' || ? || ' days')"
    sql = f"""SELECT
               COUNT(*) as total,
               SUM(CASE WHEN resultado='ganada' THEN 1 ELSE 0 END) as ganadas,
               SUM(CASE WHEN resultado='perdida' THEN 1 ELSE 0 END) as perdidas,
               SUM(CASE WHEN resultado='pendiente' THEN 1 ELSE 0 END) as pendientes,
               COALESCE(SUM(ganancia_neta), 0) as ganancia_neta,
               COALESCE(AVG(edge_pct), 0) as avg_edge,
               COALESCE(AVG(kelly_pct), 0) as avg_kelly
             FROM bets WHERE {dc} >= {ago}"""
    with db() as conn:
        r = _fetchone(conn, sql, (days,))
    if not r:
        return {"total": 0, "ganadas": 0, "perdidas": 0, "pendientes": 0,
                "ganancia_neta": 0, "avg_edge": 0, "avg_kelly": 0, "win_rate": 0, "roi": 0}
    total = r.get("total", 0) or 0
    ganadas = r.get("ganadas", 0) or 0
    ganancia = r.get("ganancia_neta", 0) or 0
    win_rate = (ganadas / total * 100) if total > 0 else 0
    roi = (ganancia / max(abs(ganancia), 1) * 100) if False else 0  # placeholder real
    return {k: (v or 0) for k, v in r.items()} | {
        "win_rate": round(win_rate, 1),
    }


def get_bets_by_sport(days: int = 30) -> list[dict]:
    """Apuestas agrupadas por liga/deporte."""
    dc = "created_at::date" if _USE_PG else "date(created_at)"
    ago = "CURRENT_DATE - INTERVAL '1 day' * ?" if _USE_PG else "date('now', '-' || ? || ' days')"
    sql = f"""SELECT
               liga,
               COUNT(*) as total,
               SUM(CASE WHEN resultado='ganada' THEN 1 ELSE 0 END) as ganadas,
               SUM(CASE WHEN resultado='perdida' THEN 1 ELSE 0 END) as perdidas,
               COALESCE(SUM(ganancia_neta), 0) as ganancia_neta
             FROM bets WHERE {dc} >= {ago}
             GROUP BY liga ORDER BY ganancia_neta DESC"""
    with db() as conn:
        rows = _fetchall(conn, sql, (days,))
    return rows or []


def get_prediction_stats(days: int = 30) -> dict:
    """Estadísticas de predicciones."""
    dc = "created_at::date" if _USE_PG else "date(created_at)"
    ago = "CURRENT_DATE - INTERVAL '1 day' * ?" if _USE_PG else "date('now', '-' || ? || ' days')"
    sql = f"""SELECT
               COUNT(*) as total,
               SUM(CASE WHEN correcto=1 THEN 1 ELSE 0 END) as correctos,
               SUM(CASE WHEN correcto=0 THEN 1 ELSE 0 END) as incorrectos
             FROM predictions WHERE {dc} >= {ago}"""
    with db() as conn:
        r = _fetchone(conn, sql, (days,))
    if not r:
        return {"total": 0, "correctos": 0, "incorrectos": 0, "accuracy": 0}
    total = r.get("total", 0) or 0
    correctos = r.get("correctos", 0) or 0
    accuracy = (correctos / total * 100) if total > 0 else 0
    return {k: (v or 0) for k, v in r.items()} | {"accuracy": round(accuracy, 1)}


def get_sharpe_ratio(days: int = 30) -> float:
    """Calcula Sharpe ratio de las ganancias diarias."""
    dc = "created_at::date" if _USE_PG else "date(created_at)"
    ago = "CURRENT_DATE - INTERVAL '1 day' * ?" if _USE_PG else "date('now', '-' || ? || ' days')"
    sql = f"""SELECT {dc} as dia, SUM(ganancia_neta) as ganancia_diaria
             FROM bets WHERE {dc} >= {ago}
             AND resultado != 'pendiente'
             GROUP BY {dc} ORDER BY dia"""
    with db() as conn:
        rows = _fetchall(conn, sql, (days,))
    returns = [r.get("ganancia_diaria", 0) or 0 for r in (rows or [])]
    if len(returns) < 5:
        return 0
    mean_r = sum(returns) / len(returns)
    std_r = (sum((r - mean_r) ** 2 for r in returns) / len(returns)) ** 0.5
    if std_r == 0:
        return 0
    return round(mean_r / std_r * (252 ** 0.5), 2)  # anualizado
