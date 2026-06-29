"""
Router para apuestas deportivas.
Endpoints: odds, value bets, comparador, arbitrajes.
"""
from flask import Blueprint, jsonify, request
from auth import login_required
from services.deportes import get_odds_for_sport, get_any_odds_key
from services.estadisticas import detectar_value_bet, comparar_odds_casas
import os

router = Blueprint("odds", __name__)


@router.route("/odds/<deporte>", methods=["GET"])
@login_required
def obtener_odds(deporte="soccer_mexico_ligamx"):
    """
    Odds actuales de múltiples casas de apuestas.
    deportes disponibles: soccer_mexico_ligamx, basketball_nba, soccer_uefa_champs_league
    """
    casas = int(request.args.get("casas", 5))
    api_key = get_any_odds_key()
    raw = get_odds_for_sport(deporte, api_key)
    data = []
    for m in raw if isinstance(raw, list) else []:
        ht = m.get("home_team", "") or ""
        at = m.get("away_team", "") or ""
        if not ht or not at:
            continue
        odds_map = {}
        for book in m.get("bookmakers", []):
            for o in book.get("markets", [{}])[0].get("outcomes", []) if book.get("markets") else []:
                name = o.get("name", "")
                price = o.get("price", 0)
                if name and price > 1:
                    odds_map.setdefault(book.get("title", ""), {})[name] = price
        data.append({
            "id": m.get("id", ""),
            "local": ht,
            "visitante": at,
            "liga": m.get("sport_title", deporte),
            "fecha": m.get("commence_time", ""),
            "odds": odds_map,
        })
    return jsonify({"deporte": deporte, "total_partidos": len(data), "partidos": data[:20]})


@router.route("/value-bets", methods=["GET"])
@login_required
def value_bets():
    """
    Detecta automáticamente value bets con edge positivo.
    """
    deporte = request.args.get("deporte", "soccer_mexico_ligamx")
    edge_minimo = float(request.args.get("edge_minimo", 2.0))
    api_key = get_any_odds_key()
    raw = get_odds_for_sport(deporte, api_key)
    partidos = []
    for m in raw if isinstance(raw, list) else []:
        ht = m.get("home_team", "") or ""
        at = m.get("away_team", "") or ""
        if not ht or not at:
            continue
        odds_map = {}
        for book in m.get("bookmakers", []):
            for o in book.get("markets", [{}])[0].get("outcomes", []) if book.get("markets") else []:
                name = o.get("name", "")
                price = o.get("price", 0)
                if name and price > 1:
                    odds_map.setdefault(book.get("title", ""), {})[name] = price
        partidos.append({
            "id": m.get("id", ""),
            "local": ht,
            "visitante": at,
            "liga": m.get("sport_title", deporte),
            "fecha": m.get("commence_time", ""),
            "odds": odds_map,
        })

    value_bets_detectados = []

    for partido in partidos:
        for resultado, cuotas_por_casa in partido.get("odds", {}).items():
            for casa, cuota in cuotas_por_casa.items():
                if cuota <= 1:
                    continue
                todas_cuotas = [
                    c
                    for casas_data in partido["odds"].values()
                    for c in casas_data.values()
                    if c > 1
                ]
                prob_promedio = 1 / (sum(1 / c for c in todas_cuotas) / len(todas_cuotas)) if todas_cuotas else 0.5

                analisis = detectar_value_bet(cuota, prob_promedio)
                if analisis["edge_porcentaje"] >= edge_minimo:
                    value_bets_detectados.append({
                        "partido": f"{partido['local']} vs {partido['visitante']}",
                        "liga": partido.get("liga", deporte),
                        "fecha": partido.get("fecha"),
                        "resultado": resultado,
                        "casa": casa,
                        **analisis,
                    })

    value_bets_detectados.sort(key=lambda x: x["edge_porcentaje"], reverse=True)
    return jsonify({
        "deporte": deporte,
        "edge_minimo_pct": edge_minimo,
        "total_encontrados": len(value_bets_detectados),
        "value_bets": value_bets_detectados[:20],
    })


@router.route("/comparar/<partido_id>", methods=["GET"])
@login_required
def comparar_partido(partido_id, deporte="soccer_mexico_ligamx"):
    """
    Compara odds de un partido específico entre todas las casas disponibles.
    Detecta arbitrajes automáticamente.
    """
    api_key = get_any_odds_key()
    raw = get_odds_for_sport(deporte, api_key)
    partidos = []
    for m in raw if isinstance(raw, list) else []:
        ht = m.get("home_team", "") or ""
        at = m.get("away_team", "") or ""
        if not ht or not at:
            continue
        odds_map = {}
        for book in m.get("bookmakers", []):
            for o in book.get("markets", [{}])[0].get("outcomes", []) if book.get("markets") else []:
                name = o.get("name", "")
                price = o.get("price", 0)
                if name and price > 1:
                    odds_map.setdefault(book.get("title", ""), {})[name] = price
        partidos.append({
            "id": m.get("id", ""),
            "local": ht,
            "visitante": at,
            "liga": m.get("sport_title", deporte),
            "fecha": m.get("commence_time", ""),
            "odds": odds_map,
        })

    partido = next((p for p in partidos if p["id"] == partido_id), None)
    if not partido:
        return jsonify({"error": "Partido no encontrado", "id": partido_id})

    comparacion = comparar_odds_casas(
        partido["odds"],
        f"{partido['local']} vs {partido['visitante']}",
    )
    return jsonify(comparacion)


@router.route("/calcular-valor", methods=["POST"])
@login_required
def calcular_valor():
    """
    Calcula el valor esperado de una apuesta específica.
    """
    data = request.get_json()
    cuota = data["cuota"]
    probabilidad_pct = data["probabilidad_pct"]
    apuesta = data.get("apuesta", 100)
    prob = probabilidad_pct / 100
    analisis = detectar_value_bet(cuota, prob)
    analisis["valor_esperado_apuesta"] = round(analisis["valor_esperado_por_unidad"] * apuesta, 2)
    analisis["apuesta"] = apuesta
    return jsonify(analisis)
