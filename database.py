"""
Base de datos SQLite — capa de persistencia del sistema.

Tablas:
- predictions     : predicciones generadas por el modelo
- bets            : registro de apuestas reales (bankroll tracker)
- bankroll_history: curva del bankroll en el tiempo
- value_bets_log  : value bets detectados automáticamente
- alerts_log      : alertas enviadas (NLP, lesiones, steam)
"""

import sqlite3
import os
import logging
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "apuestaspro.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db():
    """Context manager: abre conexión, hace commit o rollback y cierra."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Crea todas las tablas si no existen."""
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS predictions (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at    TEXT    DEFAULT (datetime('now')),
            home          TEXT    NOT NULL,
            away          TEXT    NOT NULL,
            liga          TEXT    DEFAULT 'Liga MX',
            fecha_partido TEXT,
            pronostico    TEXT,          -- 1 | X | 2
            confianza_pct REAL,
            prob_local    REAL,
            prob_empate   REAL,
            prob_visitante REAL,
            xg_home       REAL,
            xg_away       REAL,
            modelo        TEXT,
            resultado_real TEXT,         -- 1 | X | 2 (se llena después)
            correcto      INTEGER,       -- 0 | 1
            verificado_at TEXT
        );

        CREATE TABLE IF NOT EXISTS bets (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at     TEXT    DEFAULT (datetime('now')),
            partido        TEXT    NOT NULL,
            liga           TEXT    DEFAULT 'Liga MX',
            mercado        TEXT    DEFAULT '1X2',   -- 1X2 | Over/Under | BTTS | Handicap
            seleccion      TEXT    NOT NULL,
            cuota          REAL    NOT NULL,
            monto          REAL    NOT NULL,
            kelly_pct      REAL,
            edge_pct       REAL,
            bankroll_antes REAL,
            resultado      TEXT    DEFAULT 'pendiente', -- pendiente | ganada | perdida | void
            ganancia_neta  REAL    DEFAULT 0,
            bankroll_despues REAL,
            notas          TEXT
        );

        CREATE TABLE IF NOT EXISTS bankroll_history (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha     TEXT    DEFAULT (datetime('now')),
            bankroll  REAL    NOT NULL,
            evento    TEXT
        );

        CREATE TABLE IF NOT EXISTS value_bets_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_at TEXT    DEFAULT (datetime('now')),
            partido     TEXT,
            liga        TEXT,
            resultado   TEXT,
            casa        TEXT,
            cuota       REAL,
            edge_pct    REAL,
            notificado  INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS alerts_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT    DEFAULT (datetime('now')),
            tipo       TEXT,   -- NLP_LESION | STEAM | VALUE_BET | NLP_MORAL
            partido    TEXT,
            detalle    TEXT,
            urgencia   TEXT,
            canal      TEXT    DEFAULT 'telegram'
        );

        CREATE INDEX IF NOT EXISTS idx_bets_resultado   ON bets(resultado);
        CREATE INDEX IF NOT EXISTS idx_pred_correcto    ON predictions(correcto);
        CREATE INDEX IF NOT EXISTS idx_vb_detected      ON value_bets_log(detected_at);
        """)
    logger.info("DB inicializada en %s", DB_PATH)


# ── Helpers de consulta ───────────────────────────────────────────────────────

def get_bankroll_actual() -> float:
    """Retorna el bankroll más reciente registrado."""
    with db() as conn:
        row = conn.execute(
            "SELECT bankroll FROM bankroll_history ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return float(row["bankroll"]) if row else 0.0


def registrar_bankroll(monto: float, evento: str = "") -> None:
    with db() as conn:
        conn.execute(
            "INSERT INTO bankroll_history (bankroll, evento) VALUES (?, ?)",
            (monto, evento),
        )


def log_value_bet(partido, liga, resultado, casa, cuota, edge_pct) -> None:
    with db() as conn:
        conn.execute(
            "INSERT INTO value_bets_log (partido, liga, resultado, casa, cuota, edge_pct) "
            "VALUES (?,?,?,?,?,?)",
            (partido, liga, resultado, casa, cuota, edge_pct),
        )


def log_alert(tipo, partido, detalle, urgencia="MEDIA", canal="telegram") -> None:
    with db() as conn:
        conn.execute(
            "INSERT INTO alerts_log (tipo, partido, detalle, urgencia, canal) VALUES (?,?,?,?,?)",
            (tipo, partido, detalle, urgencia, canal),
        )


def rows_to_list(rows) -> list:
    return [dict(r) for r in rows]
