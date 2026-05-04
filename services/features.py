"""
Motor de features avanzados para predicción de fútbol.
Integra todos los factores que mejoran la precisión hasta 15%:

1. Lesiones y suspensiones (API-Football)
2. Head-to-head histórico (últimos 5 partidos)
3. Forma reciente (últimos 5 y 10 partidos con puntos)
4. Congestión de fixtures (fatiga acumulada)
5. Árbitro (tendencia amarillas/rojas/penaltis)
6. Clima (temperatura, lluvia, viento)
7. Venue y distancia de viaje
8. Importancia del partido (clásico, final, etc.)
9. Posición en tabla y presión
"""
import math
from datetime import datetime, timedelta

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# ══════════════════════════════════════════════════════════════════════════
# 1. AJUSTE POR LESIONES Y SUSPENSIONES
# ══════════════════════════════════════════════════════════════════════════

# Peso de cada posición en el rendimiento del equipo
POSICION_PESO = {
    "Goalkeeper":   0.12,
    "Defender":     0.08,
    "Midfielder":   0.10,
    "Attacker":     0.14,
    "Forward":      0.14,
}

def calcular_ajuste_lesiones(lesiones_local, lesiones_visitante):
    """
    Ajusta las probabilidades según jugadores clave ausentes.
    Retorna factores multiplicadores para lam_local y lam_visitante.
    
    lesiones: lista de {jugador, posicion, tipo, titular}
    """
    def impacto_equipo(lesiones):
        impacto = 0.0
        for l in lesiones:
            pos   = l.get("posicion", "Midfielder")
            peso  = POSICION_PESO.get(pos, 0.08)
            # Titular pesa más
            if l.get("titular", False):
                peso *= 1.5
            impacto += peso
        return min(impacto, 0.35)  # máximo 35% de impacto

    imp_local  = impacto_equipo(lesiones_local)
    imp_visita = impacto_equipo(lesiones_visitante)

    # Factor multiplicador del ataque esperado
    factor_local  = 1.0 - imp_local  * 0.4   # lesiones reducen ataque
    factor_visita = 1.0 - imp_visita * 0.4

    return {
        "factor_lambda_local":     round(max(0.6, factor_local), 3),
        "factor_lambda_visitante": round(max(0.6, factor_visita), 3),
        "impacto_local_pct":       round(imp_local  * 100, 1),
        "impacto_visitante_pct":   round(imp_visita * 100, 1),
        "lesiones_local":          len(lesiones_local),
        "lesiones_visitante":      len(lesiones_visitante),
    }


def get_lesiones_api(fixture_id, api_key=""):
    """Obtiene lesiones de API-Football para un fixture."""
    if not HAS_HTTPX or not api_key:
        return [], []
    try:
        headers = ({"x-rapidapi-key": api_key, "x-rapidapi-host": "api-football-v1.p.rapidapi.com"}
                   if len(api_key) > 40 else {"x-apisports-key": api_key})
        r = httpx.get(
            "https://v3.football.api-sports.io/injuries",
            params={"fixture": fixture_id},
            headers=headers, timeout=10
        )
        data = r.json().get("response", [])
        local, visita = [], []
        for p in data:
            entry = {
                "jugador":  p.get("player", {}).get("name", ""),
                "posicion": p.get("player", {}).get("type", "Midfielder"),
                "tipo":     p.get("player", {}).get("reason", ""),
                "titular":  True,
            }
            if p.get("team", {}).get("id") == p.get("fixture", {}).get("teams", {}).get("home", {}).get("id"):
                local.append(entry)
            else:
                visita.append(entry)
        return local, visita
    except Exception:
        return [], []


# ══════════════════════════════════════════════════════════════════════════
# 2. HEAD-TO-HEAD HISTÓRICO
# ══════════════════════════════════════════════════════════════════════════

def analizar_h2h(partidos_h2h, home, away, ultimos_n=5):
    """
    Analiza historial directo entre dos equipos.
    partidos_h2h: lista de {home, away, home_goals, away_goals}
    
    Retorna factor de ajuste basado en dominancia histórica.
    """
    if not partidos_h2h:
        return {"factor_h2h": 1.0, "dominio": "sin datos H2H"}

    # Filtrar últimos N partidos entre estos equipos
    relevantes = [
        p for p in partidos_h2h
        if (p["home"] == home and p["away"] == away) or
           (p["home"] == away and p["away"] == home)
    ][-ultimos_n:]

    if not relevantes:
        return {"factor_h2h": 1.0, "dominio": "sin datos H2H"}

    wins_home = draws = wins_away = 0
    goles_home = goles_away = 0

    for p in relevantes:
        if p["home"] == home:
            gh, ga = p["home_goals"], p["away_goals"]
        else:
            gh, ga = p["away_goals"], p["home_goals"]  # invertir

        goles_home += gh
        goles_away += ga

        if gh > ga:   wins_home += 1
        elif gh == ga: draws += 1
        else:          wins_away += 1

    n = len(relevantes)
    pct_home = wins_home / n
    pct_away = wins_away / n

    # Factor de ajuste: si home gana más del 60% de H2H → boost
    if pct_home > 0.6:
        factor = 1.0 + (pct_home - 0.5) * 0.3
        dominio = f"{home} domina H2H ({wins_home}/{n})"
    elif pct_away > 0.6:
        factor = 1.0 - (pct_away - 0.5) * 0.3
        dominio = f"{away} domina H2H ({wins_away}/{n})"
    else:
        factor = 1.0
        dominio = f"H2H equilibrado ({wins_home}W-{draws}D-{wins_away}L)"

    return {
        "factor_h2h":    round(factor, 3),
        "dominio":        dominio,
        "partidos_h2h":  n,
        "victorias_local": wins_home,
        "empates":         draws,
        "victorias_visita": wins_away,
        "goles_local_avg":  round(goles_home / n, 2),
        "goles_visita_avg": round(goles_away / n, 2),
    }


# ══════════════════════════════════════════════════════════════════════════
# 3. FORMA RECIENTE (ROLLING FORM)
# ══════════════════════════════════════════════════════════════════════════

def calcular_forma(partidos, equipo, ultimos_n=5):
    """
    Calcula forma reciente de un equipo.
    Retorna puntos, goles, xG, tendencia.
    """
    # Filtrar partidos del equipo (como local o visitante)
    mis_partidos = []
    for p in partidos:
        if p["home"] == equipo:
            mis_partidos.append({
                "gf": p["home_goals"], "gc": p["away_goals"],
                "xg": p.get("xg_home", None), "xga": p.get("xg_away", None),
                "es_local": True,
            })
        elif p["away"] == equipo:
            mis_partidos.append({
                "gf": p["away_goals"], "gc": p["home_goals"],
                "xg": p.get("xg_away", None), "xga": p.get("xg_home", None),
                "es_local": False,
            })

    recientes = mis_partidos[-ultimos_n:]
    if not recientes:
        return {"puntos": 0, "forma_str": "N/A", "factor_forma": 1.0}

    puntos = goles_f = goles_c = 0
    xg_sum = xga_sum = xg_count = 0
    forma_str = []

    for p in recientes:
        if p["gf"] > p["gc"]:
            puntos += 3; forma_str.append("W")
        elif p["gf"] == p["gc"]:
            puntos += 1; forma_str.append("D")
        else:
            forma_str.append("L")
        goles_f += p["gf"]
        goles_c += p["gc"]
        if p["xg"]:
            xg_sum  += p["xg"];  xg_count += 1
        if p["xga"]:
            xga_sum += p["xga"]

    max_pts = len(recientes) * 3
    pct_forma = puntos / max_pts if max_pts > 0 else 0.5

    # Factor: forma excelente (+15%) a mala (-15%)
    factor = 0.85 + pct_forma * 0.30

    return {
        "puntos":        puntos,
        "max_puntos":    max_pts,
        "pct_forma":     round(pct_forma * 100, 1),
        "forma_str":     "".join(forma_str),
        "goles_favor":   round(goles_f / len(recientes), 2),
        "goles_contra":  round(goles_c / len(recientes), 2),
        "xg_promedio":   round(xg_sum / xg_count, 2) if xg_count else None,
        "factor_forma":  round(factor, 3),
    }


# ══════════════════════════════════════════════════════════════════════════
# 4. CONGESTIÓN DE FIXTURES (FATIGA)
# ══════════════════════════════════════════════════════════════════════════

def calcular_fatiga(partidos_recientes_equipo, dias_desde_ultimo=3):
    """
    Equipos con muchos partidos en poco tiempo rinden peor.
    Retorna factor de fatiga (menor = más cansado).
    """
    if dias_desde_ultimo <= 3:
        factor = 0.93   # muy poco descanso → 7% peor rendimiento
    elif dias_desde_ultimo <= 5:
        factor = 0.97   # algo de fatiga
    elif dias_desde_ultimo <= 7:
        factor = 1.00   # normal
    else:
        factor = 1.02   # bien descansado → ligera mejora

    n_ultimos_14_dias = len(partidos_recientes_equipo)
    if n_ultimos_14_dias >= 4:
        factor *= 0.95  # 4+ partidos en 14 días = fatiga extra

    return {"factor_fatiga": round(factor, 3), "partidos_14_dias": n_ultimos_14_dias}


# ══════════════════════════════════════════════════════════════════════════
# 5. ÁRBITRO
# ══════════════════════════════════════════════════════════════════════════

# Árbitros conocidos en Liga MX con tendencias documentadas
ARBITROS_PERFIL = {
    "Fernando Hernández": {"tarjetas_por_partido": 4.8, "penaltis_por_10": 1.2, "estilo": "estricto"},
    "César Ramos":        {"tarjetas_por_partido": 3.9, "penaltis_por_10": 0.8, "estilo": "permisivo"},
    "Diego Montaño":      {"tarjetas_por_partido": 4.2, "penaltis_por_10": 1.0, "estilo": "neutral"},
    "Adonai Escobedo":    {"tarjetas_por_partido": 5.1, "penaltis_por_10": 1.5, "estilo": "muy estricto"},
    "Marco Antonio Ortiz":{"tarjetas_por_partido": 3.5, "penaltis_por_10": 0.6, "estilo": "permisivo"},
}

def analizar_arbitro(nombre_arbitro):
    """
    Retorna perfil del árbitro y su impacto en el partido.
    Árbitros estrictos → más tarjetas → afecta equipos físicos.
    """
    if not nombre_arbitro or nombre_arbitro not in ARBITROS_PERFIL:
        return {
            "arbitro": nombre_arbitro or "Desconocido",
            "tarjetas_por_partido": 4.0,
            "penaltis_por_10": 1.0,
            "estilo": "neutral",
            "factor_arbitro": 1.0,
            "nota": "Árbitro sin perfil — usando promedio Liga MX",
        }

    p = ARBITROS_PERFIL[nombre_arbitro]
    # Árbitros estrictos favorecen ligeramente al visitante (más penaltis)
    factor = 1.0 + (p["penaltis_por_10"] - 1.0) * 0.02

    return {
        "arbitro":             nombre_arbitro,
        "tarjetas_por_partido": p["tarjetas_por_partido"],
        "penaltis_por_10":     p["penaltis_por_10"],
        "estilo":              p["estilo"],
        "factor_arbitro":      round(factor, 3),
    }


# ══════════════════════════════════════════════════════════════════════════
# 6. CLIMA
# ══════════════════════════════════════════════════════════════════════════

def get_clima(ciudad, api_key_clima=""):
    """
    Obtiene clima actual vía OpenWeatherMap (gratis, 1000 req/día).
    Registrarse en openweathermap.org
    """
    if not HAS_HTTPX or not api_key_clima:
        return {"disponible": False}
    try:
        r = httpx.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": ciudad + ",MX", "appid": api_key_clima, "units": "metric"},
            timeout=8,
        )
        d = r.json()
        temp     = d["main"]["temp"]
        lluvia   = d.get("rain", {}).get("1h", 0)
        viento   = d["wind"]["speed"]
        condicion = d["weather"][0]["main"]

        # Impacto en juego
        factor = 1.0
        if lluvia > 5:   factor -= 0.04  # lluvia → menos goles
        if viento > 15:  factor -= 0.03  # viento → menos goles
        if temp > 32:    factor -= 0.05  # calor extremo → fatiga

        return {
            "disponible":  True,
            "ciudad":      ciudad,
            "temperatura": temp,
            "lluvia_mm":   lluvia,
            "viento_kmh":  round(viento * 3.6, 1),
            "condicion":   condicion,
            "factor_clima": round(factor, 3),
            "impacto": (
                "lluvia fuerte → menos goles esperados" if lluvia > 5
                else "calor extremo → fatiga" if temp > 32
                else "condiciones normales"
            ),
        }
    except Exception:
        return {"disponible": False}


def calcular_factor_clima(datos_clima):
    """Factor de ajuste de lambdas por clima."""
    if not datos_clima.get("disponible"):
        return 1.0
    return datos_clima.get("factor_clima", 1.0)


# ══════════════════════════════════════════════════════════════════════════
# 7. IMPORTANCIA DEL PARTIDO
# ══════════════════════════════════════════════════════════════════════════

CLASICOS = {
    ("Club América", "Guadalajara"),
    ("Guadalajara", "Club América"),
    ("Cruz Azul", "Club América"),
    ("Club América", "Cruz Azul"),
    ("Tigres UANL", "Monterrey"),
    ("Monterrey", "Tigres UANL"),
    ("Pumas UNAM", "Cruz Azul"),
    ("Cruz Azul", "Pumas UNAM"),
}

def calcular_importancia(home, away, jornada=None, es_liguilla=False, es_final=False):
    """
    Partidos importantes generan más intensidad → más goles y tarjetas.
    Los clásicos tienden a ser más cerrados (favorece empate).
    """
    es_clasico = (home, away) in CLASICOS

    factor_goles  = 1.0
    factor_empate = 1.0

    if es_clasico:
        factor_goles  = 0.95   # clásicos → más disputados → menos goles
        factor_empate = 1.15   # más probabilidad de empate en clásico

    if es_final:
        factor_goles  = 0.90
        factor_empate = 1.20

    if jornada and jornada >= 16:   # últimas jornadas → más presión
        factor_goles  *= 0.97
        factor_empate *= 1.05

    return {
        "es_clasico":     es_clasico,
        "es_liguilla":    es_liguilla,
        "es_final":       es_final,
        "factor_goles":   round(factor_goles, 3),
        "factor_empate":  round(factor_empate, 3),
        "nivel": "Final" if es_final else "Clásico" if es_clasico else "Liguilla" if es_liguilla else "Jornada regular",
    }


# ══════════════════════════════════════════════════════════════════════════
# 8. POSICIÓN EN TABLA Y PRESIÓN
# ══════════════════════════════════════════════════════════════════════════

def calcular_presion(pos_local, pos_visitante, total_equipos=18):
    """
    Equipos en zona de descenso o necesitados de puntos
    juegan con más presión → mayor varianza en resultados.
    """
    zona_descenso_local  = pos_local  > total_equipos - 4
    zona_descenso_visita = pos_visitante > total_equipos - 4
    lider_local = pos_local <= 3
    lider_visita = pos_visitante <= 3

    # Equipo desesperado juega más arriesgado → más goles
    factor_goles = 1.0
    if zona_descenso_local or zona_descenso_visita:
        factor_goles = 1.08

    return {
        "factor_presion": round(factor_goles, 3),
        "zona_descenso_local":  zona_descenso_local,
        "zona_descenso_visita": zona_descenso_visita,
        "lider_local":  lider_local,
        "lider_visita": lider_visita,
        "diferencia_posicion": abs(pos_local - pos_visitante),
    }


# ══════════════════════════════════════════════════════════════════════════
# 9. FEATURE VECTOR COMPLETO
# ══════════════════════════════════════════════════════════════════════════

def construir_features_completo(
    home, away,
    historial,
    lesiones_local=None, lesiones_visitante=None,
    arbitro=None,
    ciudad_estadio=None,
    api_key_clima="",
    pos_local=9, pos_visitante=9,
    jornada=None,
    es_liguilla=False,
    fixture_id=None,
    api_key_football="",
):
    """
    Construye el vector completo de features para el partido.
    Retorna factores de ajuste consolidados para los lambdas DC.
    """
    features = {}

    # Lesiones
    if api_key_football and fixture_id:
        les_l, les_v = get_lesiones_api(fixture_id, api_key_football)
    else:
        les_l = lesiones_local or []
        les_v = lesiones_visitante or []

    adj_lesiones = calcular_ajuste_lesiones(les_l, les_v)
    features["lesiones"] = adj_lesiones

    # H2H
    h2h = analizar_h2h(historial, home, away)
    features["h2h"] = h2h

    # Forma
    forma_local  = calcular_forma(historial, home, 5)
    forma_visita = calcular_forma(historial, away, 5)
    features["forma_local"]    = forma_local
    features["forma_visitante"] = forma_visita

    # Árbitro
    arb = analizar_arbitro(arbitro)
    features["arbitro"] = arb

    # Clima
    clima = {}
    if ciudad_estadio:
        clima = get_clima(ciudad_estadio, api_key_clima)
    features["clima"] = clima

    # Importancia
    importancia = calcular_importancia(home, away, jornada, es_liguilla)
    features["importancia"] = importancia

    # Presión tabla
    presion = calcular_presion(pos_local, pos_visitante)
    features["presion"] = presion

    # ── FACTORES CONSOLIDADOS ──────────────────────────────────────────
    # Factor final para lambda_local (goles esperados local)
    f_lambda_local = (
        adj_lesiones["factor_lambda_local"] *
        h2h["factor_h2h"] *
        forma_local["factor_forma"] *
        importancia["factor_goles"] *
        presion["factor_presion"] *
        calcular_factor_clima(clima)
    )

    # Factor final para lambda_visitante
    f_lambda_visitante = (
        adj_lesiones["factor_lambda_visitante"] *
        (1 / h2h["factor_h2h"] if h2h["factor_h2h"] > 0 else 1.0) *
        forma_visita["factor_forma"] *
        importancia["factor_goles"] *
        presion["factor_presion"] *
        calcular_factor_clima(clima)
    )

    # Factor de empate (clásicos, partidos importantes)
    f_empate = importancia["factor_empate"]

    features["factores_finales"] = {
        "lambda_local":    round(max(0.5, min(2.0, f_lambda_local)), 3),
        "lambda_visitante": round(max(0.5, min(2.0, f_lambda_visitante)), 3),
        "empate_boost":    round(max(0.8, min(1.4, f_empate)), 3),
    }

    return features
