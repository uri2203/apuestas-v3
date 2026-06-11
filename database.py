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
        "CREATE INDEX IF NOT EXISTS idx_bets_resultado ON bets(resultado)",
        "CREATE INDEX IF NOT EXISTS idx_pred_correcto  ON predictions(correcto)",
    ]
    for stmt in statements:
        cur.execute(stmt)
    cur.close()
    conn.close()


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
    sql = """SELECT
               COUNT(*) as total,
               SUM(CASE WHEN resultado='ganada' THEN 1 ELSE 0 END) as ganadas,
               SUM(CASE WHEN resultado='perdida' THEN 1 ELSE 0 END) as perdidas,
               SUM(CASE WHEN resultado='pendiente' THEN 1 ELSE 0 END) as pendientes,
               COALESCE(SUM(ganancia_neta), 0) as ganancia_neta
             FROM bets WHERE date(created_at) = date('now')"""
    with db() as conn:
        r = _fetchone(conn, sql)
    if not r:
        return {"total": 0, "ganadas": 0, "perdidas": 0, "pendientes": 0, "ganancia_neta": 0}
    return {k: (v or 0) for k, v in r.items()}


def count_predictions_today() -> dict:
    """Cuenta predicciones de hoy."""
    sql = """SELECT
               COUNT(*) as total,
               SUM(CASE WHEN correcto=1 THEN 1 ELSE 0 END) as correctos,
               SUM(CASE WHEN correcto=0 THEN 1 ELSE 0 END) as incorrectos,
               SUM(CASE WHEN correcto IS NULL THEN 1 ELSE 0 END) as pendientes
             FROM predictions WHERE date(created_at) = date('now')"""
    with db() as conn:
        r = _fetchone(conn, sql)
    if not r:
        return {"total": 0, "correctos": 0, "incorrectos": 0, "pendientes": 0}
    return {k: (v or 0) for k, v in r.items()}


def count_value_bets_today() -> dict:
    """Cuenta value bets detectados hoy."""
    sql = """SELECT
               COUNT(*) as total,
               COALESCE(AVG(edge_pct), 0) as avg_edge
             FROM value_bets_log WHERE date(detected_at) = date('now')"""
    with db() as conn:
        r = _fetchone(conn, sql)
    if not r:
        return {"total": 0, "avg_edge": 0}
    return {k: (v or 0) for k, v in r.items()}


def count_alerts_today() -> dict:
    """Cuenta alertas de hoy por urgencia."""
    sql = """SELECT
               SUM(CASE WHEN urgencia='ALTA' THEN 1 ELSE 0 END) as altas,
               SUM(CASE WHEN urgencia='MEDIA' THEN 1 ELSE 0 END) as medias,
               SUM(CASE WHEN urgencia='BAJA' THEN 1 ELSE 0 END) as bajas,
               COUNT(*) as total
             FROM alerts_log WHERE date(created_at) = date('now')"""
    with db() as conn:
        r = _fetchone(conn, sql)
    if not r:
        return {"altas": 0, "medias": 0, "bajas": 0, "total": 0}
    return {k: (v or 0) for k, v in r.items()}


# ── Consultas de rendimiento ─────────────────────────────────────────────────

def get_bankroll_history(days: int = 30) -> list[dict]:
    """Historial de bankroll para gráficas."""
    sql = """SELECT fecha, bankroll FROM bankroll_history
             WHERE fecha >= date('now', '-' || ? || ' days')
             ORDER BY fecha ASC"""
    with db() as conn:
        rows = _fetchall(conn, sql, (days,))
    return rows or []


def get_bets_stats(days: int = 30) -> dict:
    """Estadísticas generales de apuestas en los últimos N días."""
    sql = """SELECT
               COUNT(*) as total,
               SUM(CASE WHEN resultado='ganada' THEN 1 ELSE 0 END) as ganadas,
               SUM(CASE WHEN resultado='perdida' THEN 1 ELSE 0 END) as perdidas,
               SUM(CASE WHEN resultado='pendiente' THEN 1 ELSE 0 END) as pendientes,
               COALESCE(SUM(ganancia_neta), 0) as ganancia_neta,
               COALESCE(AVG(edge_pct), 0) as avg_edge,
               COALESCE(AVG(kelly_pct), 0) as avg_kelly
             FROM bets WHERE date(created_at) >= date('now', '-' || ? || ' days')"""
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
    sql = """SELECT
               liga,
               COUNT(*) as total,
               SUM(CASE WHEN resultado='ganada' THEN 1 ELSE 0 END) as ganadas,
               SUM(CASE WHEN resultado='perdida' THEN 1 ELSE 0 END) as perdidas,
               COALESCE(SUM(ganancia_neta), 0) as ganancia_neta
             FROM bets WHERE date(created_at) >= date('now', '-' || ? || ' days')
             GROUP BY liga ORDER BY ganancia_neta DESC"""
    with db() as conn:
        rows = _fetchall(conn, sql, (days,))
    return rows or []


def get_prediction_stats(days: int = 30) -> dict:
    """Estadísticas de predicciones."""
    sql = """SELECT
               COUNT(*) as total,
               SUM(CASE WHEN correcto=1 THEN 1 ELSE 0 END) as correctos,
               SUM(CASE WHEN correcto=0 THEN 1 ELSE 0 END) as incorrectos
             FROM predictions WHERE date(created_at) >= date('now', '-' || ? || ' days')"""
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
    sql = """SELECT date(created_at) as dia, SUM(ganancia_neta) as ganancia_diaria
             FROM bets WHERE date(created_at) >= date('now', '-' || ? || ' days')
             AND resultado != 'pendiente'
             GROUP BY date(created_at) ORDER BY dia"""
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
