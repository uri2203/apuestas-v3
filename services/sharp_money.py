"""
Motor de detección de dinero sharp (información privilegiada legal).

Los indicadores más cercanos a "información privilegiada" que existen:
1. Reverse Line Movement (RLM)   — línea vs dinero público
2. Steam Move detector            — movimiento simultáneo en casas
3. Bet% vs Money% split           — brecha boletos vs dinero
4. Line Freeze                    — línea inmóvil bajo presión pública
5. Sharp book consensus           — Pinnacle/Bookmaker se mueven primero
6. Timing analysis                — temprano=sharp, tardío=público
7. Opening line value             — cuánto se desvió la línea de apertura

Precisión documentada: seguir RLM + Steam da 58-63% de acierto vs 50% random.
"""
from datetime import datetime, timedelta
import math

# ══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════

# Casas "sharp" — sus movimientos tienen mayor peso informativo
# Estas casas tienen límites altos y respetan dinero profesional
SHARP_BOOKS = {
    "Pinnacle":    1.0,   # la más sharp del mundo
    "Bookmaker":   0.95,
    "CRIS":        0.90,
    "BetCRIS":     0.88,
    "Circa":       0.85,
}

# Casas "square" — atraen más dinero público
SQUARE_BOOKS = {
    "DraftKings":  0.3,
    "FanDuel":     0.3,
    "BetMGM":      0.4,
    "Bet365":      0.6,
    "Codere":      0.5,
    "1xBet":       0.5,
}

# ══════════════════════════════════════════════════════════════════════════
# 1. REVERSE LINE MOVEMENT (RLM)
# ══════════════════════════════════════════════════════════════════════════

def detectar_rlm(
    linea_apertura: float,
    linea_actual: float,
    pct_apuestas_lado_a: float,   # % de boletos en el lado que abrió
    umbral_publico: float = 60.0,  # % mínimo de apuestas públicas para ser "lado público"
) -> dict:
    """
    Detecta Reverse Line Movement.
    RLM = línea se mueve CONTRA el lado que tiene más apuestas públicas.

    Ejemplo: 72% de boletos en Chivas, pero la línea mejora para América.
    Eso significa que el dinero GRANDE (sharp) está en América.

    pct_apuestas_lado_a: % de tickets apostando al lado que abrió como favorito/elegido
    """
    movimiento = linea_actual - linea_apertura
    pct_lado_b = 100 - pct_apuestas_lado_a

    # ¿El lado con más apuestas públicas recibió movimiento en su contra?
    if pct_apuestas_lado_a >= umbral_publico and movimiento < 0:
        # El lado favorito del público perdió valor → sharps en el otro lado
        is_rlm = True
        lado_sharp = "B (el menos popular)"
        fuerza = "fuerte" if pct_apuestas_lado_a >= 75 else "moderado"
    elif pct_lado_b >= umbral_publico and movimiento > 0:
        # El lado B es el público y la línea mejoró para A → sharps en A
        is_rlm = True
        lado_sharp = "A (el menos popular)"
        fuerza = "fuerte" if pct_lado_b >= 75 else "moderado"
    else:
        is_rlm = False
        lado_sharp = None
        fuerza = None

    magnitud_pct = round(abs(movimiento / linea_apertura * 100), 2) if linea_apertura else 0

    return {
        "tipo": "Reverse Line Movement (RLM)",
        "detectado": is_rlm,
        "linea_apertura": linea_apertura,
        "linea_actual": linea_actual,
        "movimiento": round(movimiento, 3),
        "movimiento_pct": magnitud_pct,
        "pct_boletos_lado_publico": max(pct_apuestas_lado_a, pct_lado_b),
        "lado_sharp": lado_sharp,
        "fuerza": fuerza,
        "señal": (
            f"RLM {fuerza}: {round(max(pct_apuestas_lado_a, pct_lado_b))}% del público en un lado, línea se mueve en contra → dinero sharp en {lado_sharp}"
            if is_rlm else
            "Sin RLM — movimiento de línea consistente con dinero público"
        ),
        "confianza_pct": (
            85 if is_rlm and fuerza == "fuerte" else
            65 if is_rlm and fuerza == "moderado" else
            0
        ),
    }


# ══════════════════════════════════════════════════════════════════════════
# 2. BET% vs MONEY% SPLIT
# ══════════════════════════════════════════════════════════════════════════

def analizar_split(
    pct_boletos_local: float,
    pct_dinero_local: float,
    umbral_brecha: float = 15.0,
) -> dict:
    """
    Analiza la brecha entre % de boletos y % de dinero.

    Si el 80% de BOLETOS están en Local pero solo el 35% del DINERO → sharp en Visitante.
    Si el 20% de BOLETOS pero 65% del DINERO → sharp en Local.

    La brecha mínima significativa documentada es 15-20 puntos porcentuales.
    """
    brecha = pct_dinero_local - pct_boletos_local

    if abs(brecha) < umbral_brecha:
        return {
            "tipo": "Bet/Money Split",
            "detectado": False,
            "señal": f"Sin señal clara (brecha {abs(brecha):.1f}% < umbral {umbral_brecha}%)",
            "brecha": round(brecha, 1),
        }

    if brecha > 0:
        # Más dinero que boletos en Local → sharp en Local
        lado_sharp = "Local"
        descripcion = f"{pct_boletos_local:.0f}% boletos pero {pct_dinero_local:.0f}% del dinero en Local → apuestas grandes de sharps en Local"
    else:
        # Más boletos que dinero en Local → sharp en Visitante
        lado_sharp = "Visitante"
        descripcion = f"{pct_boletos_local:.0f}% boletos en Local pero solo {pct_dinero_local:.0f}% del dinero → dinero grande de sharps en Visitante"

    fuerza = "muy fuerte" if abs(brecha) >= 30 else "fuerte" if abs(brecha) >= 20 else "moderado"

    return {
        "tipo": "Bet/Money Split",
        "detectado": True,
        "pct_boletos_local": pct_boletos_local,
        "pct_dinero_local": pct_dinero_local,
        "brecha": round(brecha, 1),
        "lado_sharp": lado_sharp,
        "fuerza": fuerza,
        "descripcion": descripcion,
        "señal": descripcion,
        "confianza_pct": (
            90 if abs(brecha) >= 30 else
            75 if abs(brecha) >= 20 else
            60
        ),
    }


# ══════════════════════════════════════════════════════════════════════════
# 3. STEAM MOVE DETECTOR
# ══════════════════════════════════════════════════════════════════════════

def detectar_steam(movimientos_por_casa: list[dict], ventana_minutos: int = 10) -> dict:
    """
    Detecta Steam Move: múltiples casas cambian la misma línea simultáneamente
    sin noticia pública que lo explique.

    movimientos_por_casa: [
        {"casa": "Pinnacle", "linea_antes": 2.10, "linea_ahora": 1.85, "timestamp": "..."},
        {"casa": "Bet365",   "linea_antes": 2.15, "linea_ahora": 1.90, "timestamp": "..."},
    ]
    """
    if len(movimientos_por_casa) < 2:
        return {"tipo": "Steam Move", "detectado": False, "señal": "Insuficientes casas para detectar steam"}

    # Verificar que todas se mueven en la misma dirección
    movs = [m["linea_ahora"] - m["linea_antes"] for m in movimientos_por_casa]
    misma_dir = all(v < 0 for v in movs) or all(v > 0 for v in movs)

    if not misma_dir:
        return {"tipo": "Steam Move", "detectado": False, "señal": "Movimientos en direcciones distintas — no es steam"}

    n_casas = len(movimientos_por_casa)
    mag_promedio = sum(abs(m) for m in movs) / n_casas
    casas = [m["casa"] for m in movimientos_por_casa]

    # ¿Alguna casa sharp se movió?
    sharp_involucradas = [c for c in casas if c in SHARP_BOOKS]
    peso_sharp = sum(SHARP_BOOKS.get(c, 0) for c in sharp_involucradas)

    es_steam = n_casas >= 2 and mag_promedio >= 0.02  # 2+ casas, >2% de movimiento

    direccion = "BAJA (línea más baja → más difícil ganar en ese lado)" if movs[0] < 0 else "SUBE"
    lado_sharp = "el lado contrario a donde fue la línea" if movs[0] < 0 else "el lado favorecido"

    return {
        "tipo": "Steam Move",
        "detectado": es_steam,
        "n_casas_afectadas": n_casas,
        "casas": casas,
        "sharp_involucradas": sharp_involucradas,
        "magnitud_promedio_pct": round(mag_promedio * 100, 2),
        "direccion_linea": direccion,
        "lado_sharp": lado_sharp,
        "señal": (
            f"STEAM MOVE detectado en {n_casas} casas simultáneamente — sindicato sharp apostando. Ventana de oportunidad: 30-120 segundos"
            if es_steam else
            "Sin steam move"
        ),
        "confianza_pct": (
            92 if es_steam and sharp_involucradas else
            78 if es_steam else
            0
        ),
        "accion": "Apostar AHORA en casa que aún no actualizó la línea" if es_steam else None,
    }


# ══════════════════════════════════════════════════════════════════════════
# 4. LINE FREEZE
# ══════════════════════════════════════════════════════════════════════════

def detectar_line_freeze(
    pct_apuestas_lado_publico: float,
    movimiento_linea: float,
    umbral_publico: float = 70.0,
) -> dict:
    """
    Line Freeze: el libro NO mueve la línea aunque el 70%+ del público
    está en un lado. Señal de que los sharps están en el otro lado
    y el libro no quiere darles mejor línea.
    """
    es_freeze = (
        pct_apuestas_lado_publico >= umbral_publico and
        abs(movimiento_linea) < 0.03   # línea casi inmóvil
    )

    return {
        "tipo": "Line Freeze",
        "detectado": es_freeze,
        "pct_publico": pct_apuestas_lado_publico,
        "movimiento_linea": movimiento_linea,
        "señal": (
            f"LINE FREEZE: {pct_apuestas_lado_publico:.0f}% del público en un lado pero la línea no se mueve → el libro sabe que los sharps están del otro lado y no quiere exponer mejor precio"
            if es_freeze else
            "Sin line freeze"
        ),
        "confianza_pct": 80 if es_freeze else 0,
        "lado_sharp": "contrario al público" if es_freeze else None,
    }


# ══════════════════════════════════════════════════════════════════════════
# 5. TIMING ANALYSIS
# ══════════════════════════════════════════════════════════════════════════

def analizar_timing(
    hora_movimiento: str,   # "lunes 09:00", "miércoles 14:00", etc.
    dias_antes_partido: int,
    magnitud_pct: float,
) -> dict:
    """
    Timing del movimiento:
    - Temprano en la semana + límites altos = SHARP
    - Tarde (horas antes del partido) = PÚBLICO o ajuste de libro
    - Lunes/Martes en fútbol = sharp profesional
    - Viernes-Domingo = mezcla de público
    """
    es_temprano = dias_antes_partido >= 3
    es_sharp_timing = es_temprano and magnitud_pct >= 2.0

    return {
        "tipo": "Timing Analysis",
        "dias_antes_partido": dias_antes_partido,
        "es_movimiento_temprano": es_temprano,
        "magnitud_pct": magnitud_pct,
        "interpretacion": (
            "SHARP: movimiento temprano y significativo — acción de profesionales que toman ventaja de línea abierta"
            if es_sharp_timing else
            "PÚBLICO: movimiento tarde — dinero recreativo acumulado cerca del partido"
            if not es_temprano else
            "Movimiento temprano pero pequeño — ajuste de libro, monitorear"
        ),
        "confianza_pct": 75 if es_sharp_timing else 30,
    }


# ══════════════════════════════════════════════════════════════════════════
# 6. CONSENSUS SHARP BOOKS
# ══════════════════════════════════════════════════════════════════════════

def analizar_consensus_sharp(lineas_por_casa: dict) -> dict:
    """
    Compara las líneas de casas sharp vs square.
    Si Pinnacle tiene línea significativamente diferente a las casas square,
    el mercado aún no ha incorporado la información que tienen los sharps.

    lineas_por_casa: {"Pinnacle": 1.85, "Bet365": 2.10, "Codere": 2.15, ...}
    """
    sharp_lines  = {k: v for k, v in lineas_por_casa.items() if k in SHARP_BOOKS}
    square_lines = {k: v for k, v in lineas_por_casa.items() if k in SQUARE_BOOKS}

    if not sharp_lines or not square_lines:
        return {"tipo": "Sharp Book Consensus", "detectado": False, "señal": "Insuficientes casas para comparar"}

    avg_sharp  = sum(sharp_lines.values())  / len(sharp_lines)
    avg_square = sum(square_lines.values()) / len(square_lines)
    diferencia_pct = (avg_sharp - avg_square) / avg_square * 100

    # Si Pinnacle es más BAJO → sharps piensan que ese lado tiene MENOS valor del que el mercado cree
    # Si Pinnacle es más ALTO → sharps ven más valor → oportunidad

    oportunidad = abs(diferencia_pct) >= 3.0

    return {
        "tipo": "Sharp Book Consensus",
        "detectado": oportunidad,
        "linea_sharp_avg": round(avg_sharp, 3),
        "linea_square_avg": round(avg_square, 3),
        "diferencia_pct": round(diferencia_pct, 2),
        "sharp_books_usados": list(sharp_lines.keys()),
        "señal": (
            f"DISCREPANCIA SHARP vs SQUARE: Pinnacle/{list(sharp_lines.keys())[0]} en {avg_sharp:.2f} vs casas square en {avg_square:.2f} ({diferencia_pct:+.1f}%). El mercado no ha incorporado la info de los sharps aún."
            if oportunidad else
            f"Mercado eficiente — casas sharp y square alineadas (diferencia {diferencia_pct:+.1f}%)"
        ),
        "confianza_pct": (
            88 if oportunidad and abs(diferencia_pct) >= 5 else
            70 if oportunidad else
            0
        ),
        "accion": (
            "Apostar en casa square antes de que ajuste su línea al nivel de Pinnacle"
            if oportunidad and diferencia_pct > 0 else
            "El lado sharp tiene menos valor aparente — evitar o buscar otra oportunidad"
            if oportunidad else None
        ),
    }


# ══════════════════════════════════════════════════════════════════════════
# 7. SCORE SHARP COMPUESTO
# ══════════════════════════════════════════════════════════════════════════

def score_sharp_total(indicadores: list[dict]) -> dict:
    """
    Combina todos los indicadores en un score de 0-100.
    Score > 70 = señal sharp fuerte.
    Score > 85 = apostar con mayor confianza.
    """
    señales_detectadas = [i for i in indicadores if i.get("detectado")]
    n_total = len(indicadores)
    n_detectadas = len(señales_detectadas)

    if n_detectadas == 0:
        return {
            "score": 0,
            "clasificacion": "Sin señal sharp",
            "recomendacion": "No hay evidencia de dinero profesional",
            "señales_activas": [],
        }

    # Score ponderado por confianza de cada indicador
    scores = [i.get("confianza_pct", 50) for i in señales_detectadas]
    score_base = sum(scores) / len(scores)

    # Bonus por múltiples señales confirmando lo mismo
    bonus_convergencia = min(n_detectadas * 5, 20)

    score_final = min(100, round(score_base + bonus_convergencia))

    return {
        "score": score_final,
        "clasificacion": (
            "Señal sharp MUY FUERTE — apostar" if score_final >= 85 else
            "Señal sharp fuerte — considerar fuertemente" if score_final >= 70 else
            "Señal sharp moderada — monitorear" if score_final >= 55 else
            "Señal débil — precaución"
        ),
        "n_señales_detectadas": n_detectadas,
        "n_señales_totales": n_total,
        "señales_activas": [
            {"tipo": i["tipo"], "confianza": i.get("confianza_pct"), "señal": i.get("señal", "")[:100]}
            for i in señales_detectadas
        ],
        "recomendacion": (
            "Apostar siguiendo el dinero sharp identificado" if score_final >= 70 else
            "Monitorear — esperar más señales de confirmación"
        ),
    }


# ══════════════════════════════════════════════════════════════════════════
# 8. ANÁLISIS COMPLETO DE UN PARTIDO
# ══════════════════════════════════════════════════════════════════════════

def analizar_partido_sharp(
    partido: str,
    linea_apertura: float,
    linea_actual: float,
    pct_boletos_local: float,
    pct_dinero_local: float,
    lineas_por_casa: dict = None,
    movimientos_simultan: list = None,
    dias_antes: int = 2,
) -> dict:
    """
    Análisis sharp completo de un partido.
    Combina todos los indicadores y produce score final.
    """
    indicadores = []

    # 1. RLM
    rlm = detectar_rlm(linea_apertura, linea_actual, pct_boletos_local)
    indicadores.append(rlm)

    # 2. Split
    split = analizar_split(pct_boletos_local, pct_dinero_local)
    indicadores.append(split)

    # 3. Line Freeze
    mov_relativo = abs((linea_actual - linea_apertura) / linea_apertura) if linea_apertura else 0
    freeze = detectar_line_freeze(pct_boletos_local, mov_relativo)
    indicadores.append(freeze)

    # 4. Steam (si hay datos)
    if movimientos_simultan:
        steam = detectar_steam(movimientos_simultan)
        indicadores.append(steam)

    # 5. Consensus sharp books (si hay datos)
    if lineas_por_casa and len(lineas_por_casa) >= 2:
        consensus = analizar_consensus_sharp(lineas_por_casa)
        indicadores.append(consensus)

    # 6. Timing
    mag_mov = abs((linea_actual - linea_apertura) / linea_apertura * 100) if linea_apertura else 0
    timing = analizar_timing("auto", dias_antes, mag_mov)
    indicadores.append(timing)

    # Score final
    score = score_sharp_total(indicadores)

    return {
        "partido": partido,
        "timestamp": datetime.now().isoformat(),
        "linea_apertura": linea_apertura,
        "linea_actual": linea_actual,
        "pct_boletos_local": pct_boletos_local,
        "pct_dinero_local": pct_dinero_local,
        "score_sharp": score,
        "indicadores": indicadores,
        "resumen": (
            f"Score Sharp: {score['score']}/100 — {score['clasificacion']}. "
            f"{score['n_señales_detectadas']} de {score['n_señales_totales']} señales activas."
        ),
    }
