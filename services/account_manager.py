"""
Account Manager — Gestión de cuentas en casas de apuestas.

Funcionalidades:
- Registro de cuentas y límites por casa
- Detección de patrones de limitación
- Rotación óptima de apuestas entre casas
- Score de "salud" de cada cuenta
- Alertas cuando una cuenta empieza a limitarse
"""

import os
import logging
from datetime import datetime, timedelta
from database import db, _fetchone, _fetchall, _execute

logger = logging.getLogger(__name__)

# ── Tipos de casas ────────────────────────────────────────────────────────────
CASAS_CATALOGO = {
    "bet365":      {"nombre": "Bet365",       "tipo": "soft",  "tolerancia": "baja",   "margen_pct": 5.5, "limite_default": 5000},
    "codere":      {"nombre": "Codere",       "tipo": "soft",  "tolerancia": "media",  "margen_pct": 6.0, "limite_default": 3000},
    "1xbet":       {"nombre": "1xBet",        "tipo": "soft",  "tolerancia": "media",  "margen_pct": 5.0, "limite_default": 4000},
    "betano":      {"nombre": "Betano",       "tipo": "soft",  "tolerancia": "media",  "margen_pct": 6.5, "limite_default": 3000},
    "caliente":    {"nombre": "Caliente",     "tipo": "soft",  "tolerancia": "alta",   "margen_pct": 7.0, "limite_default": 2000},
    "pinnacle":    {"nombre": "Pinnacle",     "tipo": "sharp", "tolerancia": "maxima", "margen_pct": 2.5, "limite_default": 50000},
    "williamhill": {"nombre": "William Hill", "tipo": "soft",  "tolerancia": "baja",   "margen_pct": 6.0, "limite_default": 4000},
    "bwin":        {"nombre": "Bwin",         "tipo": "soft",  "tolerancia": "baja",   "margen_pct": 6.5, "limite_default": 3000},
    "betfair":     {"nombre": "Betfair Exch", "tipo": "sharp", "tolerancia": "maxima", "margen_pct": 2.0, "limite_default": 100000},
}

# ── Inicializar tablas ────────────────────────────────────────────────────────

def init_account_tables() -> None:
    """Crea tablas de gestión de cuentas."""
    USE_PG = bool(os.getenv("DATABASE_URL", ""))
    with db() as conn:
        if USE_PG:
            conn.cursor().execute("""
            CREATE TABLE IF NOT EXISTS bookmaker_accounts (
                id            SERIAL PRIMARY KEY,
                created_at    TIMESTAMP DEFAULT NOW(),
                casa_key      TEXT NOT NULL UNIQUE,
                nombre        TEXT NOT NULL,
                tipo          TEXT DEFAULT 'soft',
                activa        INTEGER DEFAULT 1,
                limite_actual REAL DEFAULT 0,
                limite_inicial REAL DEFAULT 0,
                balance       REAL DEFAULT 0,
                notas         TEXT,
                ultima_apuesta TEXT,
                health_score  INTEGER DEFAULT 100
            );
            CREATE TABLE IF NOT EXISTS account_bets (
                id          SERIAL PRIMARY KEY,
                created_at  TIMESTAMP DEFAULT NOW(),
                casa_key    TEXT NOT NULL,
                partido     TEXT,
                mercado     TEXT,
                seleccion   TEXT,
                cuota       REAL,
                monto       REAL,
                tipo_apuesta TEXT DEFAULT 'sharp',
                resultado   TEXT DEFAULT 'pendiente',
                ganancia    REAL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS limit_history (
                id         SERIAL PRIMARY KEY,
                fecha      TIMESTAMP DEFAULT NOW(),
                casa_key   TEXT NOT NULL,
                limite_ant REAL,
                limite_nuevo REAL,
                razon      TEXT
            );
            """)
        else:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS bookmaker_accounts (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at     TEXT DEFAULT (datetime('now')),
                casa_key       TEXT NOT NULL UNIQUE,
                nombre         TEXT NOT NULL,
                tipo           TEXT DEFAULT 'soft',
                activa         INTEGER DEFAULT 1,
                limite_actual  REAL DEFAULT 0,
                limite_inicial REAL DEFAULT 0,
                balance        REAL DEFAULT 0,
                notas          TEXT,
                ultima_apuesta TEXT,
                health_score   INTEGER DEFAULT 100
            )""")
            conn.execute("""
            CREATE TABLE IF NOT EXISTS account_bets (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at   TEXT DEFAULT (datetime('now')),
                casa_key     TEXT NOT NULL,
                partido      TEXT,
                mercado      TEXT,
                seleccion    TEXT,
                cuota        REAL,
                monto        REAL,
                tipo_apuesta TEXT DEFAULT 'sharp',
                resultado    TEXT DEFAULT 'pendiente',
                ganancia     REAL DEFAULT 0
            )""")
            conn.execute("""
            CREATE TABLE IF NOT EXISTS limit_history (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha        TEXT DEFAULT (datetime('now')),
                casa_key     TEXT NOT NULL,
                limite_ant   REAL,
                limite_nuevo REAL,
                razon        TEXT
            )""")


# ── CRUD de cuentas ───────────────────────────────────────────────────────────

def registrar_cuenta(casa_key: str, limite_inicial: float, balance: float = 0, notas: str = "") -> dict:
    """Registra una nueva cuenta de casa de apuestas."""
    info = CASAS_CATALOGO.get(casa_key.lower(), {})
    nombre = info.get("nombre", casa_key)
    tipo   = info.get("tipo", "soft")

    with db() as conn:
        try:
            _execute(conn,
                "INSERT INTO bookmaker_accounts (casa_key, nombre, tipo, limite_actual, limite_inicial, balance, notas) "
                "VALUES (?,?,?,?,?,?,?)",
                (casa_key.lower(), nombre, tipo, limite_inicial, limite_inicial, balance, notas))
            return {"ok": True, "casa": nombre, "limite": limite_inicial}
        except Exception as e:
            return {"error": f"Cuenta ya existe o error: {e}"}


def actualizar_limite(casa_key: str, nuevo_limite: float, razon: str = "") -> dict:
    """Registra un cambio de límite — señal clave de limitación."""
    with db() as conn:
        cuenta = _fetchone(conn, "SELECT * FROM bookmaker_accounts WHERE casa_key=?", (casa_key.lower(),))
        if not cuenta:
            return {"error": "Cuenta no encontrada"}

        limite_ant = cuenta["limite_actual"]
        reduccion_pct = round((1 - nuevo_limite / limite_ant) * 100, 1) if limite_ant > 0 else 0

        # Actualizar health score
        if reduccion_pct > 80:
            health_delta = -50  # Limitación severa
        elif reduccion_pct > 50:
            health_delta = -30
        elif reduccion_pct > 20:
            health_delta = -15
        else:
            health_delta = -5

        nuevo_health = max(0, min(100, (cuenta["health_score"] or 100) + health_delta))

        _execute(conn,
            "UPDATE bookmaker_accounts SET limite_actual=?, health_score=? WHERE casa_key=?",
            (nuevo_limite, nuevo_health, casa_key.lower()))

        _execute(conn,
            "INSERT INTO limit_history (casa_key, limite_ant, limite_nuevo, razon) VALUES (?,?,?,?)",
            (casa_key.lower(), limite_ant, nuevo_limite, razon))

    nivel = "CRÍTICA" if reduccion_pct > 50 else "MODERADA" if reduccion_pct > 20 else "LEVE"
    return {
        "casa":         cuenta["nombre"],
        "limite_antes": limite_ant,
        "limite_nuevo": nuevo_limite,
        "reduccion_pct": reduccion_pct,
        "nivel":        nivel,
        "health_score": nuevo_health,
        "alerta":       reduccion_pct > 20,
        "recomendacion": _recomendacion_limitacion(reduccion_pct, cuenta["tipo"]),
    }


def _recomendacion_limitacion(reduccion_pct: float, tipo: str) -> str:
    if reduccion_pct > 80:
        return "Cuenta prácticamente cerrada. Enfocar volumen a otras casas. Usar esta solo para línea de referencia."
    elif reduccion_pct > 50:
        return "Limitación severa. Reducir frecuencia de apuestas al 30%. Aumentar apuestas de camuflaje."
    elif reduccion_pct > 20:
        return "Inicio de limitación. Activar protocolo de camuflaje esta semana. Mezclar 2 recreativas por cada sharp."
    else:
        return "Límite ajustado levemente. Monitorear próximas 2 semanas."


def registrar_apuesta_en_cuenta(casa_key: str, partido: str, mercado: str,
                                 seleccion: str, cuota: float, monto: float,
                                 tipo: str = "sharp") -> dict:
    """Registra una apuesta en la cuenta específica de la casa."""
    with db() as conn:
        cuenta = _fetchone(conn, "SELECT * FROM bookmaker_accounts WHERE casa_key=?", (casa_key.lower(),))
        if not cuenta:
            return {"error": "Cuenta no encontrada"}

        _execute(conn,
            "INSERT INTO account_bets (casa_key, partido, mercado, seleccion, cuota, monto, tipo_apuesta) "
            "VALUES (?,?,?,?,?,?,?)",
            (casa_key.lower(), partido, mercado, seleccion, cuota, monto, tipo))

        _execute(conn,
            "UPDATE bookmaker_accounts SET ultima_apuesta=? WHERE casa_key=?",
            (datetime.now().isoformat(), casa_key.lower()))

    return {"ok": True, "registrada_en": cuenta["nombre"], "monto": monto, "tipo": tipo}


def listar_cuentas() -> list:
    """Lista todas las cuentas con su estado de salud."""
    with db() as conn:
        cuentas = _fetchall(conn, "SELECT * FROM bookmaker_accounts ORDER BY health_score DESC")

    resultado = []
    for c in cuentas:
        info = CASAS_CATALOGO.get(c["casa_key"], {})
        limite_ini = c["limite_inicial"] or 1
        pct_restante = round(c["limite_actual"] / limite_ini * 100, 1) if limite_ini > 0 else 100
        score = c["health_score"] or 100
        resultado.append({
            **c,
            "pct_limite_restante": pct_restante,
            "estado": "verde" if score >= 70 else "amarillo" if score >= 40 else "rojo",
            "margen_casa_pct": info.get("margen_pct", 6.0),
            "tolerancia": info.get("tolerancia", "media"),
        })
    return resultado


# ── Health Score ──────────────────────────────────────────────────────────────

def calcular_health_score(casa_key: str) -> dict:
    """
    Calcula el score de salud de una cuenta basado en:
    - Reducción de límites histórica
    - Ratio sharp/recreativo de apuestas
    - Win rate en esa casa
    - Tiempo desde última apuesta
    """
    with db() as conn:
        cuenta = _fetchone(conn, "SELECT * FROM bookmaker_accounts WHERE casa_key=?", (casa_key.lower(),))
        if not cuenta:
            return {"error": "Cuenta no encontrada"}

        bets = _fetchall(conn,
            "SELECT * FROM account_bets WHERE casa_key=? ORDER BY created_at DESC LIMIT 50",
            (casa_key.lower(),))

        limites = _fetchall(conn,
            "SELECT * FROM limit_history WHERE casa_key=? ORDER BY fecha DESC LIMIT 10",
            (casa_key.lower(),))

    score = 100
    factores = []

    # Factor 1: Reducción de límites
    if limites:
        total_reduccion = sum(
            max(0, (h["limite_ant"] or 0) - (h["limite_nuevo"] or 0))
            for h in limites
        )
        limite_ini = cuenta["limite_inicial"] or 1
        pct_reduccion = total_reduccion / limite_ini * 100
        if pct_reduccion > 70:
            score -= 40
            factores.append(f"Límite reducido {pct_reduccion:.0f}% históricamente (-40)")
        elif pct_reduccion > 40:
            score -= 20
            factores.append(f"Límite reducido {pct_reduccion:.0f}% históricamente (-20)")

    # Factor 2: Ratio sharp/recreativo
    if bets:
        sharps = sum(1 for b in bets if b["tipo_apuesta"] == "sharp")
        ratio = sharps / len(bets)
        if ratio > 0.9:
            score -= 25
            factores.append(f"90%+ apuestas sharp — perfil muy agresivo (-25)")
        elif ratio > 0.7:
            score -= 10
            factores.append(f"70%+ apuestas sharp (-10)")
        else:
            factores.append(f"Ratio sharp/recreativo OK ({ratio:.0%} sharps)")

    # Factor 3: Win rate
    resueltas = [b for b in bets if b["resultado"] in ("ganada", "perdida")]
    if len(resueltas) >= 5:
        ganadas = sum(1 for b in resueltas if b["resultado"] == "ganada")
        wr = ganadas / len(resueltas)
        if wr > 0.60:
            score -= 20
            factores.append(f"Win rate {wr:.0%} — muy alto, foco de atención (-20)")
        elif wr > 0.55:
            score -= 10
            factores.append(f"Win rate {wr:.0%} — moderadamente alto (-10)")

    score = max(0, min(100, score))

    return {
        "casa":        cuenta["nombre"],
        "health_score": score,
        "estado":      "verde" if score >= 70 else "amarillo" if score >= 40 else "rojo",
        "limite_actual": cuenta["limite_actual"],
        "pct_limite": round((cuenta["limite_actual"] or 0) / max(cuenta["limite_inicial"] or 1, 1) * 100, 1),
        "factores":   factores,
        "recomendacion": (
            "Cuenta saludable — operar normalmente" if score >= 70 else
            "Activar protocolo de camuflaje — reducir frecuencia sharp" if score >= 40 else
            "Cuenta en riesgo — solo apuestas recreativas por 2 semanas"
        ),
    }
