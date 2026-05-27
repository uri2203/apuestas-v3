"""
Camouflage Strategy — Estrategia de camuflaje para prolongar la vida de cuentas.

Genera apuestas recreativas de bajo riesgo para mezclar con las apuestas sharp,
y calcula la distribución óptima de volumen entre casas.
"""

import random
import math
from datetime import datetime
from typing import List, Dict


# ── Perfiles de apostador ─────────────────────────────────────────────────────

PERFILES = {
    "recreativo": {
        "ratio_sharp":      0.30,  # 30% apuestas con edge real
        "ratio_camuflaje":  0.70,  # 70% apuestas recreativas
        "max_pct_bankroll": 0.02,  # máx 2% por apuesta
        "descripcion":      "Cuentas duran años. ROI bajo pero sostenible.",
        "semanas_riesgo":   52,
    },
    "mixto": {
        "ratio_sharp":      0.55,
        "ratio_camuflaje":  0.45,
        "max_pct_bankroll": 0.03,
        "descripcion":      "Balance entre longevidad y ganancia. Recomendado.",
        "semanas_riesgo":   20,
    },
    "agresivo": {
        "ratio_sharp":      0.80,
        "ratio_camuflaje":  0.20,
        "max_pct_bankroll": 0.05,
        "descripcion":      "Máxima ganancia. Cuentas duran 3-6 meses.",
        "semanas_riesgo":   8,
    },
}


# ── Generador de apuestas de camuflaje ────────────────────────────────────────

# Mercados recreativos que las casas asocian con apostadores normales
MERCADOS_CAMUFLAJE = [
    {"mercado": "Acumulador 2 equipos",       "cuota_rango": (2.5, 4.0),   "peso": 3},
    {"mercado": "Tarjetas totales Over",       "cuota_rango": (1.70, 2.10), "peso": 2},
    {"mercado": "Córners Over/Under",          "cuota_rango": (1.75, 2.05), "peso": 2},
    {"mercado": "Minuto primer gol",           "cuota_rango": (1.90, 3.00), "peso": 1},
    {"mercado": "Marcador Exacto 1-0 o 0-1",  "cuota_rango": (4.00, 7.00), "peso": 1},
    {"mercado": "Ambos equipos Over 0.5",      "cuota_rango": (1.40, 1.80), "peso": 2},
    {"mercado": "Equipo local Over 1.5 goles", "cuota_rango": (1.80, 2.40), "peso": 2},
    {"mercado": "Half time / Full time",       "cuota_rango": (2.50, 5.00), "peso": 1},
]

# Ligas "recreativas" para apostar (no las que usa el modelo)
LIGAS_CAMUFLAJE = [
    "Serie B Italia", "Liga Portugal", "Eredivisie Holanda",
    "Segunda División España", "Championship Inglaterra",
    "Liga MX Expansión", "USL Championship",
]


def generar_apuestas_camuflaje(
    perfil: str,
    bankroll: float,
    n_apuestas: int = 3,
    casas: List[str] = None,
) -> List[Dict]:
    """
    Genera sugerencias de apuestas de camuflaje para mezclar con apuestas sharp.

    perfil: 'recreativo' | 'mixto' | 'agresivo'
    bankroll: bankroll total
    n_apuestas: cuántas apuestas de camuflaje generar
    casas: lista de casas donde distribuirlas
    """
    config = PERFILES.get(perfil, PERFILES["mixto"])
    max_monto = bankroll * 0.01  # nunca más del 1% por apuesta de camuflaje

    # Seleccionar mercados ponderados por peso
    pool = []
    for m in MERCADOS_CAMUFLAJE:
        pool.extend([m] * m["peso"])

    resultado = []
    casas_disponibles = casas or ["bet365", "codere", "1xbet"]

    for i in range(n_apuestas):
        mercado = random.choice(pool)
        cuota = round(random.uniform(*mercado["cuota_rango"]), 2)
        monto = round(random.uniform(max_monto * 0.3, max_monto), 0)
        liga  = random.choice(LIGAS_CAMUFLAJE)
        casa  = casas_disponibles[i % len(casas_disponibles)]

        resultado.append({
            "tipo":        "camuflaje",
            "mercado":     mercado["mercado"],
            "liga":        liga,
            "cuota":       cuota,
            "monto":       monto,
            "casa":        casa,
            "proposito":   "Mantener perfil recreativo",
            "prioridad":   "BAJA — solo para camuflaje",
            "ev_esperado": round((1 / cuota - 0.5) * monto, 2),  # EV negativo esperado
        })

    return resultado


def plan_semanal_camuflaje(
    perfil: str,
    bankroll: float,
    apuestas_sharp_semana: List[Dict],
    cuentas_activas: List[str],
) -> Dict:
    """
    Genera el plan completo de la semana:
    - Cuántas apuestas sharp hacer y en qué casas
    - Cuántas apuestas de camuflaje hacer y en qué casas
    - Distribución de volumen por casa
    """
    config = PERFILES.get(perfil, PERFILES["mixto"])
    n_sharps = len(apuestas_sharp_semana)

    # Calcular cuántas apuestas de camuflaje se necesitan
    if config["ratio_sharp"] > 0:
        n_camuflaje = max(1, round(n_sharps * config["ratio_camuflaje"] / config["ratio_sharp"]))
    else:
        n_camuflaje = n_sharps * 3

    # Distribuir volumen sharp entre casas (más volumen a las más saludables)
    distribucion = {}
    if cuentas_activas:
        vol_por_casa = 1.0 / len(cuentas_activas)
        for casa in cuentas_activas:
            distribucion[casa] = round(vol_por_casa * 100, 1)

    # Generar camuflaje
    camuflaje = generar_apuestas_camuflaje(perfil, bankroll, n_camuflaje, cuentas_activas)

    # Cronograma sugerido
    cronograma = _generar_cronograma(apuestas_sharp_semana, camuflaje)

    return {
        "perfil":           perfil,
        "config":           config,
        "semana":           datetime.now().strftime("%Y-W%W"),
        "resumen": {
            "apuestas_sharp":      n_sharps,
            "apuestas_camuflaje":  n_camuflaje,
            "ratio_real":          f"{round(n_sharps/(n_sharps+n_camuflaje)*100)}% sharp",
            "monto_sharp_total":   sum(a.get("monto", 0) for a in apuestas_sharp_semana),
            "monto_camuflaje_total": sum(a.get("monto", 0) for a in camuflaje),
        },
        "distribucion_por_casa": distribucion,
        "apuestas_camuflaje":    camuflaje,
        "cronograma":            cronograma,
        "advertencia":           config["descripcion"],
        "semanas_vida_estimada": config["semanas_riesgo"],
    }


def _generar_cronograma(sharps: List[Dict], camuflaje: List[Dict]) -> List[Dict]:
    """Intercala apuestas sharp y camuflaje a lo largo de la semana."""
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    todas = [(a, "sharp") for a in sharps] + [(a, "camuf") for a in camuflaje]
    random.shuffle(todas)

    cronograma = []
    for i, (apuesta, tipo) in enumerate(todas):
        dia = dias[i % 7]
        hora = f"{random.randint(10, 20):02d}:{random.choice(['00','15','30','45'])}"
        cronograma.append({
            "dia":     dia,
            "hora":    hora,
            "tipo":    tipo,
            "mercado": apuesta.get("mercado", ""),
            "monto":   apuesta.get("monto", 0),
            "casa":    apuesta.get("casa", ""),
        })

    return sorted(cronograma, key=lambda x: (dias.index(x["dia"]), x["hora"]))


# ── Detector de comportamiento riesgoso ───────────────────────────────────────

def analizar_comportamiento(historial_bets: List[Dict]) -> Dict:
    """
    Analiza el historial de apuestas y detecta patrones que alertan a las casas.
    """
    if not historial_bets:
        return {"riesgo": "BAJO", "score_riesgo": 0, "alertas": []}

    alertas = []
    score_riesgo = 0

    # 1. Ratio sharp muy alto
    sharps = [b for b in historial_bets if b.get("tipo_apuesta") == "sharp"]
    ratio_sharp = len(sharps) / len(historial_bets)
    if ratio_sharp > 0.8:
        score_riesgo += 35
        alertas.append({
            "tipo": "ratio_sharp_alto",
            "detalle": f"{ratio_sharp:.0%} de apuestas son sharp — reducir a menos del 60%",
            "urgencia": "ALTA",
        })

    # 2. Apuestas siempre al mejor precio
    cuotas = [b.get("cuota", 2.0) for b in historial_bets]
    cuota_promedio = sum(cuotas) / len(cuotas)
    if cuota_promedio > 2.5:
        score_riesgo += 15
        alertas.append({
            "tipo": "cuotas_altas_consistentes",
            "detalle": f"Cuota promedio {cuota_promedio:.2f} — muy alto para perfil normal",
            "urgencia": "MEDIA",
        })

    # 3. Siempre el mismo mercado
    mercados = [b.get("mercado", "1X2") for b in historial_bets]
    mercado_principal = max(set(mercados), key=mercados.count)
    pct_mercado = mercados.count(mercado_principal) / len(mercados)
    if pct_mercado > 0.7:
        score_riesgo += 20
        alertas.append({
            "tipo": "mercado_unico",
            "detalle": f"{pct_mercado:.0%} de apuestas en {mercado_principal} — diversificar mercados",
            "urgencia": "MEDIA",
        })

    # 4. Apuestas siempre cerca del partido (< 2 horas antes)
    # (sin timestamps reales usamos heurística)
    if len(historial_bets) > 10:
        score_riesgo += 10
        alertas.append({
            "tipo": "patron_timing",
            "detalle": "Variar horario de apuestas — no siempre apostar en la misma ventana",
            "urgencia": "BAJA",
        })

    nivel = "ALTO" if score_riesgo > 50 else "MEDIO" if score_riesgo > 25 else "BAJO"

    return {
        "riesgo":       nivel,
        "score_riesgo": min(100, score_riesgo),
        "alertas":      alertas,
        "recomendaciones": _recomendaciones_comportamiento(alertas),
    }


def _recomendaciones_comportamiento(alertas: List[Dict]) -> List[str]:
    recs = []
    tipos = [a["tipo"] for a in alertas]

    if "ratio_sharp_alto" in tipos:
        recs.append("Agregar 2-3 apuestas recreativas por cada apuesta sharp esta semana")
    if "mercado_unico" in tipos:
        recs.append("Apostar en Over/Under, tarjetas o córners en al menos 1 partido por semana")
    if "cuotas_altas_consistentes" in tipos:
        recs.append("Incluir algunas apuestas a cuotas bajas (1.3-1.6) en favoritos claros")
    if "patron_timing" in tipos:
        recs.append("Variar los horarios: algunas apuestas el día antes, otras 3 horas antes")

    if not recs:
        recs.append("Perfil saludable — mantener el comportamiento actual")

    return recs


# ── Estrategia Pinnacle como referencia ──────────────────────────────────────

def filtrar_por_pinnacle(value_bets: List[Dict], margen_minimo_pct: float = 3.0) -> List[Dict]:
    """
    Filtra value bets: solo recomienda apostar en soft books cuando
    la cuota supera la de Pinnacle en X%.

    Esto tiene doble beneficio:
    1. Garantiza que hay valor real (no solo variación aleatoria)
    2. Protege de apostar "demasiado inteligente" en soft books

    En la práctica necesitas tener cuenta en Pinnacle para comparar.
    """
    recomendados = []
    for vb in value_bets:
        cuota_soft   = vb.get("cuota", 0)
        cuota_pinnacle = vb.get("cuota_pinnacle")  # Si está disponible

        if cuota_pinnacle and cuota_pinnacle > 0:
            ventaja = (cuota_soft / cuota_pinnacle - 1) * 100
            if ventaja >= margen_minimo_pct:
                recomendados.append({
                    **vb,
                    "ventaja_vs_pinnacle_pct": round(ventaja, 2),
                    "recomendado": True,
                    "razon": f"Cuota {cuota_soft} vs Pinnacle {cuota_pinnacle} (+{ventaja:.1f}%)",
                })
        else:
            # Sin cuota de Pinnacle, usar el edge del modelo
            if vb.get("edge_porcentaje", 0) >= margen_minimo_pct + 3:
                recomendados.append({
                    **vb,
                    "ventaja_vs_pinnacle_pct": None,
                    "recomendado": True,
                    "razon": f"Edge modelo +{vb.get('edge_porcentaje', 0)}% (sin cuota Pinnacle)",
                })

    return sorted(recomendados, key=lambda x: x.get("edge_porcentaje", 0), reverse=True)
