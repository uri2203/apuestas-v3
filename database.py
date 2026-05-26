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

DATABASE_URL = os.getenv("DATABASE_URL", "")
_USE_PG = bool(DATABASE_URL)


# ── Conexión ──────────────────────────────────────────────────────────────────

def get_connection():
    if _USE_PG:
        import psycopg2
        import psycopg2.extras
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
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
    """Crea todas las tablas si no existen."""
    if _USE_PG:
        _init_pg()
    else:
        _init_sqlite()
    logger.info("DB inicializada (%s)", "PostgreSQL/Supabase" if _USE_PG else "SQLite")


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
    if _USE_PG:
        import psycopg2.extras
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        if _USE_PG and "INSERT" in sql.upper() and "RETURNING" not in sql.upper():
            sql = _q(sql) + " RETURNING id"
        else:
            sql = _q(sql)
    else:
        cur = conn.cursor()
        sql = _q(sql)
    cur.execute(sql, params)
    last_id = None
    if "INSERT" in sql.upper():
        if _USE_PG:
            row = cur.fetchone()
            last_id = row["id"] if row else None
        else:
            last_id = cur.lastrowid
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
