"""
ApuestasPro v4.3 — Servidor principal.
"""

import math, os, json, logging, time, queue, threading, traceback, httpx
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, Response, stream_with_context
from apscheduler.schedulers.background import BackgroundScheduler

from dashboard import HTML
from auth import auth_bp, login_required
from telegram_bot import telegram_bp, register_webhook, alerta_value_bets, alerta_nlp, telegram_send
from database import init_db
from services.deportes import get_active_league_keys, get_odds_for_sport, get_odds_upcoming
from routers.bankroll_router import bankroll_bp
from routers.mercados_router import mercados_bp
from routers.ml_router import ml_bp, ligas_bp, predicciones_bp
from routers.progol_optimizer_router import progol_opt_bp
from routers.accounts_router import accounts_bp
from routers.avanzado import router as avanzado_bp
from routers.kelly import router as kelly_bp
from routers.odds import router as odds_bp

if not logging.getLogger().hasHandlers():
    logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.errorhandler(Exception)
def _unhandled_error(e):
    import traceback
    tb = traceback.format_exc()
    logging.exception("Unhandled exception: %s", e)
    return jsonify({"error": str(e), "traceback": tb}), 500

# ── Blueprints ─────────────────────────────────────────────────────────────────
for bp in [auth_bp, telegram_bp, bankroll_bp, mercados_bp, ml_bp, ligas_bp, predicciones_bp, progol_opt_bp, accounts_bp]:
    app.register_blueprint(bp)
app.register_blueprint(avanzado_bp, url_prefix="/api")
app.register_blueprint(kelly_bp, url_prefix="/api")
app.register_blueprint(odds_bp, url_prefix="/api")

# ── Base de datos ──────────────────────────────────────────────────────────────
init_db()
from services.account_manager import init_account_tables
try:
    init_account_tables()
except Exception as e:
    logging.warning("account_tables init: %s", e)

# ── SSE — cola de eventos en tiempo real ──────────────────────────────────────
_sse_clients: list[queue.Queue] = []
_sse_lock = threading.Lock()

def _broadcast(evento: dict):
    """Envía un evento a todos los clientes SSE conectados."""
    data = f"data: {json.dumps(evento)}\n\n"
    dead = []
    with _sse_lock:
        for q in list(_sse_clients):
            try:
                q.put_nowait(data)
            except Exception:
                dead.append(q)
    for q in dead:
        with _sse_lock:
            _sse_clients.remove(q)

@app.route("/api/eventos")
@login_required
def sse_eventos():
    """Server-Sent Events: el dashboard recibe alertas en tiempo real."""
    q = queue.Queue()
    with _sse_lock:
        _sse_clients.append(q)

    def stream():
        try:
            yield "data: {\"tipo\": \"conectado\", \"msg\": \"Stream activo\"}\n\n"
            while True:
                try:
                    msg = q.get(timeout=30)
                    yield msg
                except queue.Empty:
                    yield ": heartbeat\n\n"
        except GeneratorExit:
            with _sse_lock:
                _sse_clients.remove(q)

    return Response(
        stream_with_context(stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

# ── Dashboard ──────────────────────────────────────────────────────────────────
@app.route("/")
@login_required
def dashboard():
    return HTML, 200, {"Content-Type": "text/html; charset=utf-8"}

@app.route("/health")
@app.route("/api/health")
def health():
    """Diagnóstico completo del sistema — público, nunca falla."""
    estado = {
        "status":  "ok",
        "version": "4.3.0",
        "sse_clients": len(_sse_clients),
    }

    # Test de conexión a la base de datos
    db_ok = False
    db_error = None
    db_tipo = "PostgreSQL/Supabase" if os.getenv("DATABASE_URL") else "SQLite"
    try:
        from database import get_bankroll_actual
        bankroll = get_bankroll_actual()
        db_ok = True
        estado["bankroll"] = bankroll
    except Exception as e:
        db_error = str(e)[:200]

    # Parsear la URL para diagnóstico (sin exponer password)
    url_info = {}
    raw_url = os.getenv("DATABASE_URL", "")
    if raw_url:
        try:
            from urllib.parse import urlparse
            stripped = raw_url.strip()
            url_info["tenia_espacios"] = (raw_url != stripped)
            url_info["longitud"] = len(stripped)
            p = urlparse(stripped)
            url_info["usuario"] = p.username
            url_info["host"]    = p.hostname
            url_info["puerto"]  = p.port
            url_info["dbname"]  = p.path.lstrip("/")
            url_info["password_longitud"] = len(p.password) if p.password else 0
            url_info["scheme"]  = p.scheme
        except Exception as e:
            url_info["parse_error"] = str(e)[:100]

    estado["database"] = {
        "tipo":      db_tipo,
        "conectada": db_ok,
        "error":     db_error,
        "url_configurada": bool(os.getenv("DATABASE_URL")),
        "url_info":  url_info,
    }

    # Estado de las API keys (solo booleanos, sin exponer las keys)
    estado["api_keys"] = {
        "api_football": bool(os.getenv("API_FOOTBALL_KEY")),
        "odds_api":     bool(os.getenv("ODDS_API_KEY")),
        "openweather":  bool(os.getenv("OPENWEATHER_KEY")),
        "telegram":     bool(os.getenv("TELEGRAM_TOKEN")),
        "app_password": bool(os.getenv("APP_PASSWORD")),
        "session_secret": bool(os.getenv("SESSION_SECRET")),
    }

    # Test rápido de API-Football (1 request ligera)
    estado["api_tests"] = {}
    if os.getenv("API_FOOTBALL_KEY"):
        try:
            from services.api_football import _headers, API_BASE, RAPID_BASE, current_season
            key = os.getenv("API_FOOTBALL_KEY")
            base = RAPID_BASE if len(key) > 40 else API_BASE
            r = httpx.get(base + "/status", headers=_headers(key), timeout=8)
            d = r.json()
            resp = d.get("response", {})
            estado["api_tests"]["api_football"] = {
                "ok": r.status_code == 200,
                "cuenta": resp.get("account", {}).get("plan", "?") if isinstance(resp, dict) else "?",
                "requests_dia": resp.get("requests", {}).get("current", "?") if isinstance(resp, dict) else "?",
                "limite_dia": resp.get("requests", {}).get("limit_day", "?") if isinstance(resp, dict) else "?",
            }
        except Exception as e:
            estado["api_tests"]["api_football"] = {"ok": False, "error": str(e)[:150]}

    if os.getenv("ODDS_API_KEY"):
        try:
            r = httpx.get("https://api.the-odds-api.com/v4/sports/",
                          params={"apiKey": os.getenv("ODDS_API_KEY")}, timeout=8)
            remaining = r.headers.get("x-requests-remaining", "?")
            used = r.headers.get("x-requests-used", "?")
            estado["api_tests"]["odds_api"] = {
                "ok": r.status_code == 200,
                "status_code": r.status_code,
                "requests_restantes": remaining,
                "requests_usados": used,
            }
        except Exception as e:
            estado["api_tests"]["odds_api"] = {"ok": False, "error": str(e)[:150]}

    # Resumen
    estado["modo"] = "REAL" if (db_ok and os.getenv("API_FOOTBALL_KEY")) else "PARCIAL" if db_ok else "ERROR_DB"

    return jsonify(estado)

@app.route("/api/version")
def version():
    """Endpoint público para verificar qué commit está desplegado."""
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL, timeout=5).decode().strip()
    except Exception:
        commit = "unknown"
    return jsonify({"version": "4.3.4", "commit": commit, "mensaje": "Solo datos reales + boton Kelly sin emojis"})

# ── PROGOL ─────────────────────────────────────────────────────────────────────
@app.route("/api/progol/jornada")
@login_required
def progol_jornada():
    from services.progol import generar_jornada_progol
    return jsonify(generar_jornada_progol(os.getenv("API_FOOTBALL_KEY","")))

@app.route("/api/progol/partido")
@login_required
def progol_partido():
    from services.progol import predecir_partido
    home=request.args.get("home","Club América"); away=request.args.get("away","Guadalajara")
    return jsonify(predecir_partido(home,away,request.args.get("xg_home",type=float),request.args.get("xg_away",type=float)))

@app.route("/api/progol/partido-completo")
@login_required
def progol_partido_completo():
    from services.progol import predecir_partido
    home=request.args.get("home","Club América"); away=request.args.get("away","Guadalajara")
    try: les_local=json.loads(request.args.get("lesiones_local","[]").replace("'",'"'))
    except: les_local=[]
    try: les_visita=json.loads(request.args.get("lesiones_visitante","[]").replace("'",'"'))
    except: les_visita=[]
    return jsonify(predecir_partido(
        home,away,
        lesiones_local=les_local,lesiones_visitante=les_visita,
        arbitro=request.args.get("arbitro"),ciudad=request.args.get("ciudad"),
        pos_local=int(request.args.get("pos_local",9)),pos_visitante=int(request.args.get("pos_visitante",9)),
        jornada=request.args.get("jornada",type=int),
        api_key_clima=os.getenv("OPENWEATHER_KEY",""),
    ))

@app.route("/api/progol/ranking")
@login_required
def progol_ranking():
    from services.progol import ranking_equipos
    return jsonify(ranking_equipos(os.getenv("API_FOOTBALL_KEY","")))

# ── ODDS / VALUE BETS ──────────────────────────────────────────────────────────

def get_bankroll_seguro():
    """Bankroll actual sin crashear si la DB falla."""
    try:
        from database import get_bankroll_actual
        return get_bankroll_actual()
    except Exception:
        return 0

def _edge_simple(prob_real, cuota):
    """Edge = (cuota * prob - 1) * 100."""
    try:
        return round((cuota * prob_real - 1) * 100, 1)
    except Exception:
        return 0.0

def _prob_implicita(cuota):
    """1 / cuota, con piso 0.01."""
    try:
        return max(0.01, 1.0 / cuota)
    except Exception:
        return 0.01

_vb_cache = {}  # {key: (timestamp, response)}

@app.route("/api/odds/sports")
@login_required
def odds_sports():
    """Lista todos los deportes activos disponibles en Odds API."""
    from services.deportes import get_sports_list
    sports = get_sports_list()
    result = []
    for s in sports:
        result.append({
            "key": s.get("key"),
            "title": s.get("title"),
            "group": s.get("group"),
            "description": s.get("description"),
            "has_outrights": s.get("has_outrights"),
        })
    return jsonify({"total": len(result), "sports": result})


@app.route("/api/odds/value-bets")
@login_required
def value_bets():
    try:
        edge_min = float(request.args.get("edge_minimo", 2))
        multi    = request.args.get("multi", "0") == "1"
        api_key  = os.getenv("ODDS_API_KEY", "")
        deporte  = request.args.get("deporte", "soccer_mexico_ligamx")

        now = time.time()

        if not api_key:
            return jsonify({
                "total_encontrados": 0, "value_bets": [],
                "es_demo": False, "total_partidos_analizados": 0,
                "aviso": "ODDS_API_KEY no configurada",
            })

        # ── 1. Obtener datos ──
        # Usar upcoming (1 call) para multi-scan, o deporte específico
        partidos = []
        deportes_escaneados = 0
        total_escaneados = 0

        if multi:
            # upcoming cubre todos los deportes en 1 call
            raw_data = get_odds_upcoming(api_key, regions="us,uk,eu")
            if raw_data:
                # Agrupar temporalmente por sport_key para el cache_key
                active = {}
                for m in raw_data:
                    sk = m.get("sport_key", "unknown")
                    if sk not in active:
                        active[sk] = True
                deportes_escaneados = len(active)
            else:
                raw_data = []
            raw_batches = [raw_data]
        else:
            deportes_a_escanear = [deporte]
            deportes_escaneados = 1
            try:
                raw_batches = [get_odds_for_sport(deporte, api_key, regions="us,uk,eu")]
            except Exception:
                raw_batches = [[]]

        cache_key = f"vb_{'multi' if multi else deporte}|{edge_min}"
        cached = _vb_cache.get(cache_key)
        if cached and now - cached[0] < 60:
            return jsonify(cached[1])

        for raw in raw_batches:
            if not raw:
                continue
            for m in raw if isinstance(raw, list) else []:
                ht = m.get("home_team","") or ""
                at = m.get("away_team","") or ""
                if not ht or not at:
                    continue
                total_escaneados += 1
                consensus_sum = {}
                consensus_count = {}
                best_per_outcome = {}
                for book in m.get("bookmakers", []):
                    casa = book.get("title","")
                    for o in book.get("markets", [{}])[0].get("outcomes", []):
                        name = o.get("name","")
                        price = o.get("price", 0)
                        if not name or price <= 1:
                            continue
                        consensus_sum[name] = consensus_sum.get(name, 0) + 1.0 / price
                        consensus_count[name] = consensus_count.get(name, 0) + 1
                        prev = best_per_outcome.get(name)
                        if not prev or price > prev["cuota"]:
                            best_per_outcome[name] = {"cuota": min(price, 50.0), "casa": casa}
                if consensus_sum and best_per_outcome:
                    raw_probs = {}
                    for outcome, inv_sum in consensus_sum.items():
                        raw_probs[outcome] = inv_sum / consensus_count[outcome]
                    total_prob = sum(raw_probs.values())
                    consensus = {k: (v / total_prob) if total_prob > 0 else 0.01 for k, v in raw_probs.items()}
                    partidos.append({
                        "home": ht, "away": at,
                        "best": best_per_outcome,
                        "consensus": consensus,
                        "liga": m.get("sport_title", skey),
                    })

        # ── 3. Calcular edge: mejor cuota vs consenso ──
        real = []
        for m in partidos:
            ht, at = m["home"], m["away"]
            best = m["best"]
            consensus = m["consensus"]
            for resultado, info in best.items():
                prob = consensus.get(resultado, 0.01)
                edge = _edge_simple(prob, info["cuota"])
                if edge >= edge_min:
                    real.append({
                        "partido":          f"{ht} vs {at}",
                        "liga":             m.get("liga", deporte),
                        "fecha":            "",
                        "resultado":        resultado,
                        "casa":             info["casa"],
                        "cuota":            info["cuota"],
                        "edge_porcentaje":  edge,
                        "edge_modelo_pct":  edge,
                        "prob_modelo_pct":  round(prob * 100, 1),
                        "es_value_bet":     True,
                        "clasificacion":    "FUERTE" if edge > 7 else "BUENO" if edge > 4 else "MODERADO" if edge > 2 else "MARGINAL",
                    })

        seen = {}
        for vb in sorted(real, key=lambda x: x["edge_porcentaje"], reverse=True):
            key = f"{vb['partido']}|{vb['resultado']}"
            if key not in seen:
                seen[key] = vb
        filtered = list(seen.values())

        response = {
            "total_encontrados": len(filtered),
            "value_bets":        filtered[:50],
            "es_demo":           False,
            "total_partidos_analizados": len(partidos),
            "deportes_escaneados": deportes_escaneados,
            "multideporte": multi,
            "aviso": None if filtered else f"Sin value bets con edge >= {edge_min}%",
        }
        _vb_cache[cache_key] = (now, response)
        return jsonify(response)

    except Exception as e:
        tb = traceback.format_exc()
        logging.exception("value_bets fatal\n%s", tb)
        return jsonify({"total_encontrados": 0, "value_bets": [], "es_demo": False,
                        "error": str(e), "traceback": tb})

# ── ARBITRAJE / SUREBETS ──────────────────────────────────────────────────────
@app.route("/api/odds/arbitraje")
@login_required
def odds_arbitraje():
    """Escáner de arbitraje/surebets. Detecta cuando sum(1/mejores cuotas) < 1.
    Sin costo adicional de API — usa los mismos datos que value-bets."""
    try:
        min_profit = float(request.args.get("min_profit", 0.5))
        multi = request.args.get("multi", "1") == "1"
        api_key = os.getenv("ODDS_API_KEY", "")
        deporte = request.args.get("deporte", "upcoming")

        if not api_key:
            return jsonify({"total_encontrados": 0, "arbitrajes": [],
                            "aviso": "ODDS_API_KEY no configurada"})

        cache_key = f"arb_{deporte}|{min_profit}"
        now = time.time()
        cached = _vb_cache.get(cache_key)
        if cached and now - cached[0] < 60:
            return jsonify(cached[1])

        # Usar upcoming (1 call) para multi-scan, o deporte específico
        if multi or deporte == "upcoming":
            raw = get_odds_upcoming(api_key, regions="us,uk,eu")
        else:
            raw = get_odds_for_sport(deporte, api_key, regions="us,uk,eu")

        if not raw:
            raw = []

        arbitrajes = []
        for m in raw if isinstance(raw, list) else []:
            ht = m.get("home_team", "") or ""
            at = m.get("away_team", "") or ""
            if not ht or not at:
                continue

            best_per_outcome = {}
            bookmaker_count = 0
            for book in m.get("bookmakers", []):
                casa = book.get("title", "")
                for o in book.get("markets", [{}])[0].get("outcomes", []):
                    name = o.get("name", "")
                    price = o.get("price", 0)
                    if not name or price <= 1:
                        continue
                    prev = best_per_outcome.get(name)
                    if not prev or price > prev["cuota"]:
                        best_per_outcome[name] = {"cuota": min(price, 50.0), "casa": casa}
                bookmaker_count += 1

            if len(best_per_outcome) < 2:
                continue

            # Calcular arbitraje: L = sum(1/mejor_cuota)
            L = sum(1.0 / v["cuota"] for v in best_per_outcome.values())
            if L >= 1:
                continue

            profit = round((1.0 / L - 1.0) * 100, 2)
            if profit < min_profit:
                continue

            # Distribución de stakes para ganancia garantizada (ejemplo con $100)
            stake_total = 100.0
            stakes = {}
            for outcome, info in best_per_outcome.items():
                stake = round(stake_total * (1.0 / info["cuota"]) / L, 2)
                retorno = round(stake * info["cuota"], 2)
                stakes[outcome] = {
                    "cuota": info["cuota"],
                    "casa": info["casa"],
                    "stake": stake,
                    "retorno": retorno,
                    "ganancia_neta": round(retorno - stake, 2),
                }

            arbitrajes.append({
                "partido":               f"{ht} vs {at}",
                "liga":                  m.get("sport_title", deporte),
                "fecha":                 m.get("commence_time", ""),
                "profit_pct":            profit,
                "n_resultados":          len(best_per_outcome),
                "n_bookmakers":          bookmaker_count,
                "inversion_ejemplo":     stake_total,
                "retorno_garantizado":   round(stake_total * (1.0 / L), 2),
                "ganancia_ejemplo":      round(stake_total * (1.0 / L) - stake_total, 2),
                "resultados":            {outcome: {"cuota": v["cuota"], "casa": v["casa"]}
                                          for outcome, v in best_per_outcome.items()},
                "stakes_ejemplo":        stakes,
            })

        arbitrajes.sort(key=lambda x: x["profit_pct"], reverse=True)

        # Loggear los mejores
        for a in arbitrajes[:5]:
            try:
                from database import log_arbitrage
                log_arbitrage(a["partido"], a["liga"], a["profit_pct"],
                              json.dumps(a["resultados"]), json.dumps(a["stakes_ejemplo"]))
            except Exception:
                pass

        response = {
            "total_encontrados": len(arbitrajes),
            "arbitrajes":        arbitrajes[:30],
            "min_profit_pct":    min_profit,
            "deporte_usado":     "upcoming" if (multi or deporte == "upcoming") else deporte,
        }
        _vb_cache[cache_key] = (now, response)
        return jsonify(response)

    except Exception as e:
        tb = traceback.format_exc()
        logging.exception("arbitraje fatal\n%s", tb)
        return jsonify({"total_encontrados": 0, "arbitrajes": [],
                        "error": str(e), "traceback": tb})


# ── ASIAN HANDICAP ────────────────────────────────────────────────────────────
@app.route("/api/odds/mercados")
@login_required
def odds_mercados():
    """Obtiene odds con mercados adicionales (h2h, asian_handicap, spreads, totals).
    Params: deporte, mercados (separados por coma), regions."""
    try:
        api_key = os.getenv("ODDS_API_KEY", "")
        deporte = request.args.get("deporte", "upcoming")
        mercados = request.args.get("mercados", "h2h,asian_handicap")
        regions = request.args.get("regions", "us,uk,eu")

        if not api_key:
            return jsonify({"error": "ODDS_API_KEY no configurada"})

        # Usar upcoming para multi-sport
        if deporte == "upcoming":
            raw = get_odds_upcoming(api_key, regions=regions, markets=mercados)
        else:
            raw = get_odds_for_sport(deporte, api_key, regions=regions, markets=mercados)

        if not raw:
            raw = []

        result = []
        for m in raw if isinstance(raw, list) else []:
            ht = m.get("home_team", "") or ""
            at = m.get("away_team", "") or ""
            if not ht or not at:
                continue

            mercados_data = {}
            for book in m.get("bookmakers", []):
                casa = book.get("title", "")
                for market in book.get("markets", []):
                    market_key = market.get("key", "")
                    if market_key not in mercados_data:
                        mercados_data[market_key] = {}
                    for outcome in market.get("outcomes", []):
                        name = outcome.get("name", "")
                        price = outcome.get("price", 0)
                        point = outcome.get("point")
                        if not name or price <= 1:
                            continue
                        key = f"{name}|{point}" if point else name
                        prev = mercados_data[market_key].get(key, {})
                        if not prev or price > prev.get("cuota", 0):
                            mercados_data[market_key][key] = {
                                "cuota": min(price, 50.0),
                                "casa": casa,
                                "name": name,
                                "point": point,
                            }

            if mercados_data:
                result.append({
                    "partido": f"{ht} vs {at}",
                    "liga": m.get("sport_title", deporte),
                    "fecha": m.get("commence_time", ""),
                    "mercados": {
                        mk: list(outcomes.values())
                        for mk, outcomes in mercados_data.items()
                    },
                    "n_bookmakers": len(m.get("bookmakers", [])),
                })

        return jsonify({
            "deporte": deporte,
            "mercados_solicitados": mercados,
            "total_partidos": len(result),
            "partidos": result[:20],
        })

    except Exception as e:
        return jsonify({"error": str(e)[:300]})


# ── EVENTOS EN VIVO ───────────────────────────────────────────────────────────
@app.route("/api/odds/live")
@login_required
def odds_live():
    """Lista partidos que están en vivo (commence_time < now)."""
    try:
        api_key = os.getenv("ODDS_API_KEY", "")
        if not api_key:
            return jsonify({"error": "ODDS_API_KEY no configurada"})

        raw = get_odds_upcoming(api_key, regions="us,uk,eu")
        if not raw:
            raw = []

        now_dt = datetime.utcnow()
        live = []
        for m in raw if isinstance(raw, list) else []:
            ct = m.get("commence_time", "")
            if not ct:
                continue
            try:
                ct_dt = datetime.fromisoformat(ct.replace("Z", "+00:00"))
            except Exception:
                continue
            is_live = ct_dt <= now_dt
            diff_min = round((now_dt - ct_dt).total_seconds() / 60) if is_live else 0
            live.append({
                "partido": f"{m.get('home_team','')} vs {m.get('away_team','')}",
                "liga": m.get("sport_title", ""),
                "commence_time": ct,
                "en_vivo": is_live,
                "minutos_desde_inicio": diff_min if is_live else 0,
                "n_bookmakers": len(m.get("bookmakers", [])),
            })

        en_vivo = [e for e in live if e["en_vivo"]]
        proximos = [e for e in live if not e["en_vivo"]][:20]

        return jsonify({
            "total": len(live),
            "en_vivo": en_vivo,
            "proximos": proximos,
        })

    except Exception as e:
        return jsonify({"error": str(e)[:300]})


@app.route("/api/odds/bookmakers")
@login_required
def odds_bookmakers():
    """Devuelve cuotas de todas las casas para la línea del equipo LOCAL."""
    try:
        api_key = os.getenv("ODDS_API_KEY", "")
        deporte = request.args.get("deporte", "soccer_mexico_ligamx")
        home    = request.args.get("home", "").strip()
        away    = request.args.get("away", "").strip()
        if not api_key:
            return jsonify({"error": "ODDS_API_KEY no configurada"})
        if not home or not away:
            return jsonify({"error": "Faltan home/away"})

        r = httpx.get(f"https://api.the-odds-api.com/v4/sports/{deporte}/odds",
                      params={"apiKey": api_key, "regions": "us", "markets": "h2h", "oddsFormat": "decimal"},
                      timeout=5)
        data = r.json()
        if isinstance(data, dict) and data.get("message"):
            return jsonify({"error": data["message"]})
        if not isinstance(data, list):
            return jsonify({"error": "Formato inesperado"})

        match = None
        for m in data:
            ht = (m.get("home_team","") or "").strip().lower()
            at = (m.get("away_team","") or "").strip().lower()
            if ht == home.lower() and at == away.lower():
                match = m
                break

        if not match:
            return jsonify({"error": f"No se encontro {home} vs {away} en {deporte}"})

        # Extraer cuota del LOCAL (home_team) de cada casa
        bookmakers = {}
        for book in match.get("bookmakers", []):
            casa = book.get("title", "")
            for o in book.get("markets", [{}])[0].get("outcomes", []):
                if o.get("name","").lower() == match["home_team"].lower():
                    bookmakers[casa] = o["price"]
                    break

        return jsonify({
            "partido": f"{match['home_team']} vs {match['away_team']}",
            "liga": match.get("sport_title", deporte),
            "bookmakers": bookmakers,
        })

    except Exception as e:
        return jsonify({"error": str(e)[:200]})
# ── KELLY ──────────────────────────────────────────────────────────────────────
@app.route("/api/kelly/calcular",methods=["POST"])
@login_required
def kelly_calcular():
    d=request.get_json(); bank=float(d.get("bankroll",5000)); odds=float(d.get("cuota_decimal",2.10))
    prob=float(d.get("probabilidad_estimada_pct",55))/100; frac=float(d.get("fraccion",0.5))
    b=odds-1; q=1-prob; kp=(b*prob-q)/b if b>0 else 0; ka=kp*frac; bet=max(0,bank*ka)
    return jsonify({"kelly_puro_pct":round(kp*100,2),"kelly_ajustado_pct":round(ka*100,2),
        "apuesta_sugerida":round(bet,2),"hay_valor":kp>0,
        "roi_esperado_pct":round((b*prob-q)*100,2),"recomendacion":"Apostar" if kp>0 else "NO apostar"})

# ── CLV ────────────────────────────────────────────────────────────────────────
@app.route("/api/pro/clv/calcular")
@login_required
def clv_calcular():
    mi=float(request.args.get("cuota_apostada",2.10)); cl=float(request.args.get("cuota_cierre",1.85))
    pct=round((mi/cl-1)*100,2)
    return jsonify({"clv_pct":pct,"es_positivo":pct>0,
        "prob_implicita_apostada_pct":round(1/mi*100,2),
        "prob_implicita_cierre_pct":round(1/cl*100,2),
        "calidad":"positivo" if pct>0 else "negativo"})

# ── MONTE CARLO ────────────────────────────────────────────────────────────────
@app.route("/api/pro/montecarlo/partido")
@login_required
def montecarlo():
    import random
    lL=float(request.args.get("lambda_local",1.5)); lV=float(request.args.get("lambda_visitante",1.1))
    N=min(int(request.args.get("simulaciones",10000)),50000)
    def poisson(l):
        k,p,q=0,math.exp(-l),1.0
        while q>p: k+=1; q*=random.random()
        return k-1
    h=d=a=0; gols=[]
    for _ in range(N):
        gl,gv=poisson(lL),poisson(lV); gols.append(gl+gv)
        if gl>gv: h+=1
        elif gl==gv: d+=1
        else: a+=1
    pL,pD,pV=h/N*100,d/N*100,a/N*100; avg=sum(gols)/N
    return jsonify({"simulaciones":N,
        "probabilidades":{"local_pct":round(pL,1),"empate_pct":round(pD,1),"visitante_pct":round(pV,1)},
        "cuotas_justas_sin_vig":{"local":round(100/pL,2) if pL>0 else 99,"empate":round(100/pD,2) if pD>0 else 99,"visitante":round(100/pV,2) if pV>0 else 99},
        "mercados_adicionales":{"avg_goles_totales":round(avg,2),
            "prob_over_2_5_pct":round(sum(1 for g in gols if g>2.5)/N*100,1),
            "prob_over_1_5_pct":round(sum(1 for g in gols if g>1.5)/N*100,1)}})

# ── SHARP MONEY ────────────────────────────────────────────────────────────────
@app.route("/api/sharp/analizar")
@login_required
def sharp_analizar():
    from services.sharp_money import analizar_partido_sharp
    partido=request.args.get("partido","Local vs Visitante")
    try: casas=json.loads(request.args.get("lineas_casas","{}"))
    except: casas={}
    resultado=analizar_partido_sharp(
        partido,float(request.args.get("linea_apertura",2.10)),
        float(request.args.get("linea_actual",1.95)),
        float(request.args.get("pct_boletos_local",30)),
        float(request.args.get("pct_dinero_local",60)),
        lineas_por_casa=casas or None,dias_antes=int(request.args.get("dias_antes",2)))
    _broadcast({"tipo":"sharp_move","data":resultado})
    return jsonify(resultado)

@app.route("/api/sharp/steam")
@login_required
def sharp_steam():
    from services.sharp_money import detectar_steam
    try: movs=json.loads(request.args.get("movimientos","[]"))
    except: movs=[]
    if not movs:
        movs=[{"casa":"Pinnacle","linea_antes":2.10,"linea_ahora":1.85},
              {"casa":"Bet365","linea_antes":2.15,"linea_ahora":1.90},
              {"casa":"Codere","linea_antes":2.18,"linea_ahora":1.92}]
    resultado=detectar_steam(movs)
    if resultado.get("detectado"): _broadcast({"tipo":"steam_move","data":resultado})
    return jsonify(resultado)

# ── NLP ─────────────────────────────────────────────────────────────────────────
@app.route("/api/nlp/scan")
@login_required
def nlp_scan():
    from services.nlp_sentiment import scan_completo
    home=request.args.get("home","Club América"); away=request.args.get("away","Guadalajara")
    resultado=scan_completo(home,away)
    if resultado.get("tiene_edge"):
        _broadcast({"tipo":"nlp_alerta","partido":f"{home} vs {away}","edges":resultado.get("alertas_edge",[])})
    return jsonify(resultado)

@app.route("/api/nlp/noticias")
@login_required
def nlp_noticias():
    from services.nlp_sentiment import fetch_noticias,detectar_lesiones
    noticias=fetch_noticias(20)
    for n in noticias: n["alertas"]=detectar_lesiones(n["titulo"]+" "+n["desc"])
    return jsonify({"noticias":noticias,"total":len(noticias)})

# ── BACKTESTING ────────────────────────────────────────────────────────────────
@app.route("/api/backtest")
@login_required
def backtest_run():
    from services.backtesting import backtest, backtest_por_modelo
    from services.api_football import get_fixtures_liga, LIGAS
    from services.progol import HISTORIAL_DEMO
    ventana = int(request.args.get("ventana", 20))
    modo    = request.args.get("modo", "ensemble")
    api_key = os.getenv("API_FOOTBALL_KEY", "")
    # Usar datos reales si hay key, sino historial demo con aviso
    historial = HISTORIAL_DEMO
    es_demo   = True
    if api_key:
        try:
            real = get_fixtures_liga(LIGAS["liga_mx"], None, api_key)
            if real and len(real) >= 10:
                historial = real
                es_demo   = False
        except Exception:
            pass
    resultado = backtest_por_modelo(historial, ventana) if modo == "comparar" else backtest(historial, ventana)
    resultado["es_demo"]    = es_demo
    resultado["n_partidos"] = len(historial)
    if es_demo:
        resultado["aviso"] = "Backtesting con historial demo (30 partidos). Configura API_FOOTBALL_KEY para datos reales."
    return jsonify(resultado)


@app.route("/api/alertas/recientes")
@login_required
def alertas_recientes():
    """Alertas reales desde la base de datos + estado de las APIs."""
    from database import db, _fetchall
    
    alertas = []
    
    # Leer alertas reales de la DB
    try:
        with db() as conn:
            rows = _fetchall(conn,
                "SELECT * FROM alerts_log ORDER BY id DESC LIMIT 20")
        for r in rows:
            tipo_map = {"NLP_LESION":"r","STEAM":"s","VALUE_BET":"g","NLP_MORAL":"i"}
            alertas.append({
                "t": tipo_map.get(r.get("tipo",""),"i"),
                "x": r.get("detalle",""),
                "g": r.get("created_at",""),
                "urgencia": r.get("urgencia",""),
                "real": True,
            })
    except Exception:
        pass

    # Leer últimos value bets detectados
    try:
        with db() as conn:
            vbs = _fetchall(conn,
                "SELECT * FROM value_bets_log ORDER BY id DESC LIMIT 5")
        for v in vbs:
            alertas.append({
                "t": "g",
                "x": f"Value bet: {v.get('partido','')} · {v.get('resultado','')} @{v.get('cuota','')} · Edge +{v.get('edge_pct','')}% ({v.get('casa','')})",
                "g": str(v.get("detected_at","")),
                "real": True,
            })
    except Exception:
        pass

    # Estado de las APIs
    api_status = {
        "api_football": bool(os.getenv("API_FOOTBALL_KEY","")),
        "odds_api":     bool(os.getenv("ODDS_API_KEY","")),
        "openweather":  bool(os.getenv("OPENWEATHER_KEY","")),
        "telegram":     bool(os.getenv("TELEGRAM_TOKEN","")),
        "db":           bool(os.getenv("DATABASE_URL","")),
        "modo":         "REAL" if os.getenv("API_FOOTBALL_KEY","") else "DEMO",
    }

    # Si no hay alertas reales, indicar que el sistema está en modo demo
    if not alertas:
        alertas = [{
            "t": "i",
            "x": "Sistema en modo DEMO — configura API_FOOTBALL_KEY y ODDS_API_KEY para datos reales",
            "g": "ahora",
            "real": False,
        }]

    return jsonify({
        "alertas": sorted(alertas, key=lambda x: x.get("g",""), reverse=True)[:15],
        "api_status": api_status,
        "total": len(alertas),
    })



@app.route("/api/admin/init-db")
def admin_init_db():
    """Crea/repara todas las tablas. Útil tras configurar la DB."""
    resultado = {"tablas_creadas": [], "errores": []}
    try:
        from database import init_db
        init_db()
        resultado["tablas_creadas"].append("core (predictions, bets, bankroll_history, value_bets_log, alerts_log)")
    except Exception as e:
        resultado["errores"].append(f"core: {str(e)[:150]}")

    try:
        from services.account_manager import init_account_tables
        init_account_tables()
        resultado["tablas_creadas"].append("cuentas (bookmaker_accounts, account_bets, limit_history)")
    except Exception as e:
        resultado["errores"].append(f"cuentas: {str(e)[:150]}")

    # Verificar que funcionan
    try:
        from database import get_bankroll_actual
        bk = get_bankroll_actual()
        resultado["verificacion"] = {"ok": True, "bankroll": bk}
    except Exception as e:
        resultado["verificacion"] = {"ok": False, "error": str(e)[:150]}

    resultado["status"] = "ok" if not resultado["errores"] else "con_errores"
    return jsonify(resultado)


@app.route("/api/seed-demo")
@login_required
def seed_demo():
    """Pobla la base con datos iniciales realistas."""
    import logging, traceback
    logger = logging.getLogger(__name__)
    try:
        from database import seed_demo_data
        result = seed_demo_data()
        result["mensaje"] = f"OK — {result.get('total_insertados',0)} registros insertados"
        logger.info("Seed endpoint: %d registros, %d errores",
                    result.get("total_insertados", 0), len(result.get("errores", [])))
        if result.get("errores"):
            result["mensaje"] += f" ({len(result['errores'])} errores, ver consola)"
        return jsonify(result)
    except Exception as e:
        tb = traceback.format_exc()
        logger.error("Seed endpoint error: %s\n%s", e, tb)
        return jsonify({"status": "error", "error": str(e), "traceback": tb}), 500


@app.route("/api/admin/diag-football")
def diag_football():
    """Diagnostica qué devuelve API-Football exactamente."""
    api_key = os.getenv("API_FOOTBALL_KEY", "")
    if not api_key:
        return jsonify({"error": "Sin API_FOOTBALL_KEY"})

    from services.api_football import (
        get_fixtures_liga, get_upcoming_fixtures, current_season,
        _cached_get, LIGAS, _headers, API_BASE, RAPID_BASE
    )

    result = {
        "season_calculada": current_season(),
        "liga_mx_id": LIGAS["liga_mx"],
        "tipo_key": "rapidapi" if len(api_key) > 40 else "api-sports",
    }

    # Test 1: fixtures terminados (historial)
    try:
        hist = get_fixtures_liga(LIGAS["liga_mx"], None, api_key)
        result["historial_partidos"] = len(hist)
        result["historial_ejemplo"] = hist[:2] if hist else []
    except Exception as e:
        result["historial_error"] = str(e)[:150]

    # Test 2: próximos partidos (7 días)
    try:
        up = get_upcoming_fixtures(LIGAS["liga_mx"], 7, api_key)
        result["proximos_7d"] = len(up)
        result["proximos_ejemplo"] = up[:3] if up else []
    except Exception as e:
        result["proximos_error"] = str(e)[:150]

    # Test 3: llamada cruda a la API para ver respuesta completa
    try:
        base = RAPID_BASE if len(api_key) > 40 else API_BASE
        hoy = datetime.now()
        r = httpx.get(base + "/fixtures", params={
            "league": LIGAS["liga_mx"],
            "season": current_season(),
            "from": hoy.strftime("%Y-%m-%d"),
            "to": (hoy + timedelta(days=30)).strftime("%Y-%m-%d"),
        }, headers=_headers(api_key), timeout=12)
        raw = r.json()
        result["raw_api"] = {
            "status_code": r.status_code,
            "results": raw.get("results"),
            "errors": raw.get("errors"),
            "paging": raw.get("paging"),
            "primer_fixture": raw.get("response", [{}])[0] if raw.get("response") else None,
        }
    except Exception as e:
        result["raw_error"] = str(e)[:200]

    return jsonify(result)



@app.route("/api/admin/diag-sportsdb")
def diag_sportsdb():
    """Diagnostica TheSportsDB — fuente gratuita de datos actuales."""
    try:
        from services import sportsdb
        liga = request.args.get("liga", "liga_mx")
        return jsonify(sportsdb.diagnostico(liga))
    except Exception as e:
        return jsonify({"error": str(e)})



@app.route("/api/admin/diag-espn")
def diag_espn():
    """Diagnostica ESPN — fuente gratuita completa de datos actuales."""
    try:
        from services import espn_scraper
        liga = request.args.get("liga", "liga_mx")
        return jsonify(espn_scraper.diagnostico(liga))
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()[:300]})



@app.route("/api/admin/optimizar-pesos")
def optimizar_pesos_endpoint():
    """Encuentra los mejores pesos del ensemble probando contra datos reales."""
    try:
        from services import espn_scraper
        from services.optimizador_pesos import optimizar
        liga = request.args.get("liga", "liga_mx")
        partidos = espn_scraper.get_historial_entrenamiento(liga)
        if len(partidos) < 30:
            # Probar con MLS que tiene más datos
            partidos = espn_scraper.get_historial_entrenamiento("mls")
            liga = "mls"
        resultado = optimizar(partidos)
        resultado["liga_evaluada"] = liga
        return jsonify(resultado)
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()[:300]})



@app.route("/api/value/analizar")
@login_required
def value_analizar():
    """Análisis profesional de value de una apuesta específica."""
    from services.value_engine import analizar_value
    prob   = float(request.args.get("prob", 0)) / 100  # viene en %
    cuota_str = request.args.get('cuota', '')
    if not cuota_str:
        return jsonify({"error": "Falta parametro cuota"}), 400
    cuota = float(cuota_str)
    pinn   = request.args.get("pinnacle")
    bk     = float(request.args.get("bankroll", 0)) or get_bankroll_seguro()
    frac   = float(request.args.get("fraccion", 0.25))
    pinn_v = float(pinn) if pinn else None
    return jsonify(analizar_value(prob, cuota, pinn_v, bk, frac))


@app.route("/api/value/clv")
@login_required
def value_clv():
    """Calcula Closing Line Value."""
    from services.value_engine import clv
    apostada = float(request.args.get("apostada", 2.0))
    cierre   = float(request.args.get("cierre", 1.9))
    return jsonify(clv(apostada, cierre))


# ── DASHBOARD RENDIMIENTO ─────────────────────────────────────────────────────
@app.route("/api/dashboard/rendimiento")
@login_required
def dashboard_rendimiento():
    """Datos completos de rendimiento para la sección de performance."""
    from database import (
        get_bankroll_actual, get_bankroll_history,
        get_bets_stats, get_bets_by_sport,
        get_prediction_stats, get_sharpe_ratio,
        count_bets_today, count_predictions_today, count_value_bets_today,
    )
    days = int(request.args.get("days", 30))
    br = get_bankroll_actual()
    history = get_bankroll_history(days)
    bets = get_bets_stats(days)
    by_sport = get_bets_by_sport(days)
    preds = get_prediction_stats(days)
    sharpe = get_sharpe_ratio(days)
    today_bets = count_bets_today()
    today_preds = count_predictions_today()
    today_vb = count_value_bets_today()

    win_rate = (bets["ganadas"] / bets["total"] * 100) if bets["total"] > 0 else 0
    net = bets["ganancia_neta"]
    roi = round((net / max(br, 1)) * 100, 2) if br > 0 else 0

    return jsonify({
        "bankroll": {
            "actual": round(br, 2),
            "history": history,
        },
        "general": {
            "total_apuestas": bets["total"],
            "ganadas": bets["ganadas"],
            "perdidas": bets["perdidas"],
            "pendientes": bets["pendientes"],
            "win_rate": round(win_rate, 1),
            "ganancia_neta": round(net, 2),
            "roi_pct": roi,
            "avg_edge_pct": round(bets.get("avg_edge", 0), 2),
            "sharpe_ratio": sharpe,
        },
        "hoy": {
            "apuestas": today_bets,
            "predicciones": today_preds,
            "value_bets": today_vb,
        },
        "predicciones": preds,
        "por_deporte": by_sport,
    })


# ── ML PREDICTOR ──────────────────────────────────────────────────────────────
@app.route("/api/ml/auto-train")
@login_required
def ml_auto_train():
    """Entrena modelo con datos ESPN y predice próximos partidos."""
    from services.ml_predictor import auto_train_all
    return jsonify(auto_train_all())


@app.route("/api/ml/auto-train/<liga>")
@login_required
def ml_auto_train_liga(liga):
    """Entrena para una liga específica."""
    from services.ml_predictor import auto_train
    return jsonify(auto_train(liga))


@app.route("/api/ml/verify")
@login_required
def ml_verify():
    """Verifica predicciones previas vs resultados reales ESPN."""
    from services.ml_predictor import verificar_resultados
    return jsonify(verificar_resultados())


# ── ML AVANZADO (Tier 6) ──────────────────────────────────────────────────────
_training_status = {"running": False, "liga": None, "result": None, "error": None, "started_at": None}

@app.route("/api/ml/v2/train")
@login_required
def ml_v2_train():
    """Inicia entrenamiento de modelos avanzados (fondo async)."""
    if _training_status["running"]:
        return jsonify({"status": "already_running", **{k: v for k, v in _training_status.items() if k != "result"}})
    _training_status.update({"running": True, "liga": "all", "result": None, "error": None, "started_at": time.time()})
    def _work():
        try:
            from services.ml_avanzado import auto_train_all_avanzado
            res = auto_train_all_avanzado()
            _training_status["result"] = res
            _training_status["error"] = None
        except Exception as e:
            _training_status["error"] = str(e)
            _training_status["result"] = None
            logging.exception("ML train bg error: %s", e)
        finally:
            _training_status["running"] = False
    threading.Thread(target=_work, daemon=True).start()
    return jsonify({"status": "started", "liga": "all"})


@app.route("/api/ml/v2/train/<liga>")
@login_required
def ml_v2_train_liga(liga):
    """Inicia entrenamiento para una liga específica (fondo async)."""
    if _training_status["running"]:
        return jsonify({"status": "already_running", **{k: v for k, v in _training_status.items() if k != "result"}})
    _training_status.update({"running": True, "liga": liga, "result": None, "error": None, "started_at": time.time()})
    def _work():
        try:
            from services.ml_avanzado import AdvancedEnsemble
            ae = AdvancedEnsemble()
            res = ae.train(liga)
            _training_status["result"] = res
            _training_status["error"] = None
        except Exception as e:
            _training_status["error"] = str(e)
            _training_status["result"] = None
            logging.exception("ML train liga bg error: %s", e)
        finally:
            _training_status["running"] = False
    threading.Thread(target=_work, daemon=True).start()
    return jsonify({"status": "started", "liga": liga})


@app.route("/api/ml/v2/train-status")
@login_required
def ml_v2_train_status():
    """Estado del entrenamiento en curso."""
    return jsonify({k: v for k, v in _training_status.items()})


@app.route("/api/ml/v2/predict")
@login_required
def ml_v2_predict():
    """Predice un partido con el modelo avanzado."""
    from services.ml_avanzado import predict_single_avanzado
    home = request.args.get("home", "")
    away = request.args.get("away", "")
    liga = request.args.get("liga", "liga_mx")
    if not home or not away:
        return jsonify({"error": "home y away requeridos"}), 400
    return jsonify(predict_single_avanzado(home, away, liga))


@app.route("/api/ml/v2/predict-proximos")
@login_required
def ml_v2_proximos():
    """Predice próximos partidos de una liga."""
    from services.ml_avanzado import AdvancedEnsemble
    liga = request.args.get("liga", "liga_mx")
    dias = int(request.args.get("dias", 7))
    ae = AdvancedEnsemble()
    return jsonify(ae.predict_proximos(liga, dias))


@app.route("/api/ml/v2/features")
@login_required
def ml_v2_features():
    """Importancia de features para una liga."""
    from services.ml_avanzado import get_feature_importance
    liga = request.args.get("liga", "liga_mx")
    return jsonify({"features": get_feature_importance(liga)})


@app.route("/api/ml/v2/performance")
@login_required
def ml_v2_performance():
    """Rendimiento histórico de modelos."""
    from services.ml_avanzado import get_model_performance
    liga = request.args.get("liga", "liga_mx")
    return jsonify(get_model_performance(liga))


# ── PORTFOLIO ─────────────────────────────────────────────────────────────────
@app.route("/api/portfolio/status")
@login_required
def portfolio_status():
    """Estado actual del portfolio de apuestas activas."""
    from services.portfolio import get_portfolio_status
    return jsonify(get_portfolio_status())


@app.route("/api/portfolio/recomendar", methods=["POST"])
@login_required
def portfolio_recomendar():
    """Recomienda stake ajustado por correlación para una nueva apuesta."""
    from services.portfolio import recomendar_nueva_apuesta
    data = request.get_json() or {}
    partido = data.get("partido", "")
    liga = data.get("liga", "")
    seleccion = data.get("seleccion", "")
    cuota = float(data.get("cuota", 0))
    prob = float(data.get("probabilidad", 0)) / 100
    fraccion = float(data.get("fraccion_kelly", 0.25))
    bankroll = data.get("bankroll")
    if bankroll is not None:
        bankroll = float(bankroll)
    return jsonify(recomendar_nueva_apuesta(
        partido, liga, seleccion, cuota, prob, bankroll, fraccion))


# ── FULL BACKTESTING ──────────────────────────────────────────────────────────
@app.route("/api/backtest/full")
@login_required
def backtest_full():
    """Full value betting backtest contra datos históricos ESPN."""
    from services.backtesting import backtest_value_betting
    from services.espn_scraper import get_historial_entrenamiento
    liga = request.args.get("liga", "liga_mx")
    edge_min = float(request.args.get("edge_minimo", 3.0))
    kelly_frac = float(request.args.get("kelly_fraccion", 0.25))

    partidos = get_historial_entrenamiento(liga)
    if len(partidos) < 40:
        return jsonify({"error": f"Historial insuficiente: {len(partidos)} partidos (min 40)"})

    resultado = backtest_value_betting(
        partidos, ventana=30, edge_minimo=edge_min,
        kelly_frac=kelly_frac,
    )
    resultado["liga"] = liga

    # Guardar en DB
    try:
        from database import db, _execute
        import json
        with db() as conn:
            _execute(conn,
                "INSERT INTO backtest_results (tipo, config, resumen, bankroll_hist) "
                "VALUES (?,?,?,?)",
                ("value_betting",
                 json.dumps(resultado.get("config", {})),
                 json.dumps(resultado.get("resumen", {})),
                 json.dumps(resultado.get("bankroll_historia", []))))
    except Exception:
        pass

    return jsonify(resultado)


# ── SMART FILTERS COMPUESTOS ──────────────────────────────────────────────────
@app.route("/api/alertas/smart")
@login_required
def alertas_smart():
    """Evalúa value bets recientes con filtros compuestos multi-señal."""
    from services.smart_filters import filtrar_value_bets
    from database import db, _fetchall
    try:
        with db() as conn:
            rows = _fetchall(conn,
                "SELECT * FROM value_bets_log ORDER BY id DESC LIMIT 50")
    except Exception as e:
        return jsonify({"error": str(e)})

    thresholds = {}
    for k in ("edge_minimo", "sharp_minimo", "overround_maximo",
              "horas_antes_minimo", "clv_historico_minimo"):
        v = request.args.get(k)
        if v is not None:
            thresholds[k] = float(v)

    return jsonify(filtrar_value_bets(rows, thresholds))


# ── SIMULACIÓN EN VIVO ───────────────────────────────────────────────────────
@app.route("/api/simulacion/status")
@login_required
def simulacion_status():
    """Resumen de trades simulados."""
    from services.simulador import resumen_simulacion
    dias = int(request.args.get("dias", 1))
    return jsonify(resumen_simulacion(dias))


@app.route("/api/simulacion/verificar")
@login_required
def simulacion_verificar():
    """Verifica trades simulados pendientes vs resultados reales ESPN."""
    from services.simulador import verificar_trades_pendientes
    return jsonify(verificar_trades_pendientes())


@app.route("/api/simulacion/registrar", methods=["POST"])
@login_required
def simulacion_registrar():
    """Registra manualmente un trade simulado."""
    from services.simulador import registrar_trade_simulado
    data = request.get_json() or {}
    return jsonify(registrar_trade_simulado(
        data.get("partido", ""), data.get("liga", ""),
        data.get("seleccion", ""), data.get("casa", ""),
        float(data.get("cuota", 0)), float(data.get("edge_pct", 0)),
        data.get("fecha_partido", ""),
    ))


# ── RATING DE BOOKMAKERS ─────────────────────────────────────────────────────
@app.route("/api/bookmakers/scan")
@login_required
def bookmakers_scan():
    """Escanea partidos activos y actualiza ratings de bookmakers."""
    from services.bookmaker_ratings import actualizar_ratings
    return jsonify(actualizar_ratings())


@app.route("/api/bookmakers/rating")
@login_required
def bookmakers_rating():
    """Ranking de bookmakers por calidad (overround, CLV, frecuencia)."""
    from services.bookmaker_ratings import get_ranking
    return jsonify(get_ranking())


# ── CROSS-MARKET ─────────────────────────────────────────────────────────────
@app.route("/api/odds/cross-market")
@login_required
def odds_cross_market():
    """Detecta inconsistencias entre mercados (H2H vs Asian Handicap vs spreads)."""
    from services.cross_market import get_opportunities
    min_diff = float(request.args.get("min_diferencia", 4.0))
    return jsonify(get_opportunities(None, min_diff))


# ── CONTABILIDAD ──────────────────────────────────────────────────────────────
@app.route("/api/contabilidad/transaccion", methods=["POST"])
@login_required
def contabilidad_transaccion():
    """Registra una transacción manual (depósito/retiro/ajuste)."""
    from services.contabilidad import registrar_transaccion
    data = request.get_json(force=True, silent=True) or {}
    r = registrar_transaccion(
        tipo=data.get("tipo", "ajuste"),
        monto=float(data.get("monto", 0)),
        categoria=data.get("categoria", "general"),
        estrategia=data.get("estrategia", ""),
        descripcion=data.get("descripcion", ""),
        partido=data.get("partido", ""),
    )
    return jsonify(r)


@app.route("/api/contabilidad/resumen-mensual")
@login_required
def contabilidad_resumen():
    from services.contabilidad import resumen_mensual
    mes = request.args.get("mes")
    año = request.args.get("año")
    return jsonify(resumen_mensual(
        int(mes) if mes else None,
        int(año) if año else None,
    ))


@app.route("/api/contabilidad/pnl-estrategia")
@login_required
def contabilidad_pnl():
    from services.contabilidad import pnl_por_estrategia
    dias = int(request.args.get("dias", 30))
    return jsonify(pnl_por_estrategia(dias))


@app.route("/api/contabilidad/sync")
@login_required
def contabilidad_sync():
    """Sincroniza apuestas reales de tabla bets → contabilidad."""
    from services.contabilidad import sync_bets_to_accounting
    return jsonify(sync_bets_to_accounting())


# ── TRADING JOURNAL ──────────────────────────────────────────────────────────
@app.route("/api/journal/log", methods=["POST"])
@login_required
def journal_log():
    from services.trading_journal import log_entry
    data = request.get_json(force=True, silent=True) or {}
    r = log_entry(
        tipo_accion=data.get("tipo_accion", "manual"),
        partido=data.get("partido", ""),
        liga=data.get("liga", ""),
        mercado=data.get("mercado", ""),
        seleccion=data.get("seleccion", ""),
        cuota=float(data.get("cuota", 0)),
        monto=float(data.get("monto", 0)),
        edge_pct=float(data.get("edge_pct", 0)),
        score_sharp=int(data.get("score_sharp", 0)),
        overround=float(data.get("overround", 0)),
        casa=data.get("casa", ""),
        estrategia=data.get("estrategia", ""),
        resultado=data.get("resultado", ""),
        pnl=float(data.get("pnl", 0)),
    )
    return jsonify({"ok": True})


@app.route("/api/journal/auto-log")
@login_required
def journal_auto():
    from services.trading_journal import auto_log_from_recent
    return jsonify(auto_log_from_recent())


@app.route("/api/journal/resumen")
@login_required
def journal_resumen():
    from services.trading_journal import resumen_journal
    dias = int(request.args.get("dias", 7))
    return jsonify(resumen_journal(dias))


@app.route("/api/journal/export-csv")
@login_required
def journal_csv():
    from services.trading_journal import export_csv
    dias = int(request.args.get("dias", 7))
    csv_data = export_csv(dias)
    return Response(csv_data, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=journal.csv"})


# ── MÓDULOS (páginas individuales) ──────────────────────────────────────────
@app.route("/panel/<module_name>")
@login_required
def modulo_page(module_name):
    from dashboard import MODULES
    entry = MODULES.get(module_name)
    if not entry:
        return "Módulo no encontrado", 404
    return entry[1], 200, {"Content-Type": "text/html; charset=utf-8"}


# ── SCHEDULER ──────────────────────────────────────────────────────────────────
def _alerta_vb_con_broadcast():
    alerta_value_bets()
    _broadcast({"tipo":"scheduler_tick","job":"value_bets","ts":time.time()})

def _alerta_nlp_con_broadcast():
    alerta_nlp()
    _broadcast({"tipo":"scheduler_tick","job":"nlp","ts":time.time()})

def _verificacion_auto():
    from services.verificador import verificar_automatico
    api_key=os.getenv("API_FOOTBALL_KEY","")
    if api_key:
        r=verificar_automatico(api_key)
        logging.info("Verificación auto: %s",r)

def _heartbeat():
    """Heartbeat del scheduler — corre cada 6h y reporta salud de todos los jobs."""
    jobs_info = []
    for job in scheduler.get_jobs():
        next_run = str(job.next_run_time) if job.next_run_time else "N/A"
        jobs_info.append(f"  [{job.id}] next: {next_run}")
    msg = "Scheduler heartbeat OK\n" + "\n".join(jobs_info)
    logging.info("Heartbeat:\n%s", msg)
    _broadcast({"tipo":"heartbeat","ts":time.time(),"jobs":[j.id for j in scheduler.get_jobs()]})

def _alerta_sharp_auto():
    """Escanea todos los deportes activos y envía alerta Telegram si detecta sharp money fuerte."""
    api_key = os.getenv("ODDS_API_KEY", "")
    if not api_key:
        return
    from services.sharp_money import analizar_partido_sharp, score_sharp_total
    deportes = get_active_league_keys(api_key)
    alertas = []
    for skey in deportes[:6]:  # max 6 deportes para no exceder API calls
        matches = get_odds_for_sport(skey, api_key, regions="us,uk,eu")
        if not matches:
            continue
        for m in matches[:8]:  # max 8 partidos por deporte
            ht = m.get("home_team","") or ""
            at = m.get("away_team","") or ""
            if not ht or not at:
                continue
            try:
                lineas_por_casa = {}
                for book in m.get("bookmakers", []):
                    casa = book.get("title","")
                    for o in book.get("markets", [{}])[0].get("outcomes", []):
                        if o.get("name","").lower() == ht.lower():
                            lineas_por_casa[casa] = o["price"]
                            break
                if len(lineas_por_casa) < 2:
                    continue
                cuotas = list(lineas_por_casa.values())
                linea_actual = sum(cuotas) / len(cuotas)
                linea_apert = max(cuotas)  # simulación de apertura
                # Score simple sin datos de público (usamos split 50/50 por defecto)
                res = analizar_partido_sharp(
                    f"{ht} vs {at}",
                    linea_apert, linea_actual,
                    50, 50,
                    lineas_por_casa=lineas_por_casa,
                    dias_antes=2,
                )
                score = res.get("score_sharp", {}).get("score", 0)
                if score >= 70:
                    clasif = res.get("score_sharp", {}).get("clasificacion", "")
                    alertas.append(
                        f"⚡ {ht} vs {at} ({m.get('sport_title', skey)})\n"
                        f"   Score: {score}/100 — {clasif}\n"
                        f"   Señales: {res.get('score_sharp', {}).get('n_señales_detectadas', 0)}/{res.get('score_sharp', {}).get('n_señales_totales', 0)}"
                    )
            except Exception:
                continue
    if alertas:
        msg = "<b>🔍 ALERTA SHARP MONEY — DETECCIÓN AUTOMÁTICA</b>\n\n" + "\n\n".join(alertas[:5])
        telegram_send(msg)
        logging.info("Alerta sharp automática enviada — %d detecciones", len(alertas))
    _broadcast({"tipo":"sharp_auto","n_alertas":len(alertas),"ts":time.time()})

def _resumen_diario():
    """Resumen diario real con datos de DB + envío por Telegram."""
    from database import (
        get_bankroll_actual,
        count_bets_today,
        count_predictions_today,
        count_value_bets_today,
        count_alerts_today,
    )
    from telegram_bot import telegram_send

    br = get_bankroll_actual()
    bets = count_bets_today()
    preds = count_predictions_today()
    vbs = count_value_bets_today()
    alerts = count_alerts_today()

    lines = ["<b>📊 ApuestasPro — Resumen Diario</b>", ""]
    lines.append(f"<b>💰 Bankroll:</b> ${br:,.2f}")
    lines.append("")
    lines.append("<b>📝 Apuestas Hoy:</b>")
    lines.append(f"  • Totales: {bets['total']}")
    lines.append(f"  • Ganadas: {bets['ganadas']}")
    lines.append(f"  • Perdidas: {bets['perdidas']}")
    lines.append(f"  • Pendientes: {bets['pendientes']}")
    gn = bets['ganancia_neta']
    sign = "+" if gn >= 0 else ""
    lines.append(f"  • Ganancia neta: {sign}${gn:,.2f}")
    lines.append("")
    lines.append("<b>🔮 Pronósticos Hoy:</b>")
    lines.append(f"  • Totales: {preds['total']}")
    lines.append(f"  • Correctos: {preds['correctos']}")
    lines.append(f"  • Incorrectos: {preds['incorrectos']}")
    lines.append(f"  • Pendientes: {preds['pendientes']}")
    pct = (preds['correctos'] / preds['total'] * 100) if preds['total'] > 0 else 0
    lines.append(f"  • Acierto: {pct:.1f}%")
    lines.append("")
    lines.append("<b>⚡ Value Bets Detectados:</b>")
    lines.append(f"  • Total: {vbs['total']}")
    lines.append(f"  • Edge promedio: +{vbs['avg_edge']:.1f}%")
    lines.append("")
    lines.append("<b>🚨 Alertas:</b>")
    lines.append(f"  • Altas: {alerts['altas']}")
    lines.append(f"  • Medias: {alerts['medias']}")
    lines.append(f"  • Bajas: {alerts['bajas']}")

    telegram_send("\n".join(lines))
    logging.info("Resumen diario enviado por Telegram — Bankroll: $%.2f", br)

def _ml_auto_train():
    """Auto-entrena modelos ML con datos ESPN y guarda predicciones."""
    try:
        from services.ml_predictor import auto_train_all
        res = auto_train_all()
        logging.info("ML auto-train: %d predicciones generadas", res.get("total_predicciones", 0))
        if res.get("total_predicciones", 0) > 0:
            telegram_send(f"<b>🤖 ML Predictor</b>\n\n{res['total_predicciones']} predicciones generadas automáticamente para {res['ligas_procesadas']} ligas.")
    except Exception as e:
        logging.error("ML auto-train error: %s", e)


def _ml_auto_verify():
    """Verifica predicciones previas vs resultados reales ESPN."""
    try:
        from services.ml_predictor import verificar_resultados
        res = verificar_resultados()
        if res.get("verificados", 0) > 0:
            logging.info("ML auto-verify: %d predicciones verificadas", res["verificados"])
    except Exception as e:
        logging.error("ML auto-verify error: %s", e)


def _ml_avanzado_auto_train():
    """Auto-entrena modelos ML avanzados (Tier 6)."""
    try:
        from services.ml_avanzado import auto_train_all_avanzado
        _training_status.update({"running": True, "liga": "all (auto)", "result": None, "error": None, "started_at": time.time()})
        res = auto_train_all_avanzado()
        _training_status["result"] = res
        n = res.get("ligas_entrenadas", 0)
        if n > 0:
            logging.info("ML Avanzado auto-train: %d ligas, %d features",
                         n, res.get("feature_count", 23))
            _broadcast({"tipo":"ml_v2_train","ts":time.time(),**res})
    except Exception as e:
        _training_status["error"] = str(e)
        logging.error("ML Avanzado auto-train error: %s", e)
    finally:
        _training_status["running"] = False


def _bookmaker_auto_scan():
    """Actualiza ratings de bookmakers automáticamente."""
    try:
        from services.bookmaker_ratings import actualizar_ratings
        res = actualizar_ratings()
        n = res.get("bookmakers_actualizados", 0)
        if n > 0:
            logging.info("Bookmaker scan: %d bookmakers actualizados", n)
    except Exception as e:
        logging.error("Bookmaker scan error: %s", e)


def _simulacion_auto_log():
    """Auto-registra trades simulados de value bets recientes no simulados."""
    try:
        from database import db, _fetchall
        from services.simulador import registrar_trade_simulado
        with db() as conn:
            sin_simular = _fetchall(conn,
                "SELECT v.* FROM value_bets_log v "
                "LEFT JOIN simulated_trades s ON v.partido=s.partido AND v.casa=s.casa "
                "WHERE s.id IS NULL AND v.edge_pct >= 5 "
                "ORDER BY v.id DESC LIMIT 20")
        registrados = 0
        for vb in sin_simular or []:
            res = registrar_trade_simulado(
                vb.get("partido", ""), vb.get("liga", ""),
                vb.get("resultado", ""), vb.get("casa", ""),
                vb.get("cuota", 0) or 0, vb.get("edge_pct", 0) or 0,
            )
            if res.get("simulado"):
                registrados += 1
        if registrados > 0:
            logging.info("Simulación auto: %d trades registrados", registrados)
    except Exception as e:
        logging.error("Simulación auto error: %s", e)


def _accounting_sync():
    """Sincroniza apuestas → contabilidad cada 6h."""
    try:
        from services.contabilidad import sync_bets_to_accounting
        r = sync_bets_to_accounting()
        if r.get("sincronizados", 0) > 0:
            logging.info("Accounting sync: %d bets sincronizados", r["sincronizados"])
            _broadcast({"tipo":"contabilidad_sync","ts":time.time(),**r})
    except Exception as e:
        logging.error("Accounting sync error: %s", e)


def _journal_auto_log():
    """Auto-registra acciones recientes en el journal cada 4h."""
    try:
        from services.trading_journal import auto_log_from_recent
        r = auto_log_from_recent()
        if r.get("registrados", 0) > 0:
            logging.info("Journal auto: %d entries registradas", r["registrados"])
    except Exception as e:
        logging.error("Journal auto error: %s", e)


scheduler=BackgroundScheduler()
scheduler.add_job(_alerta_vb_con_broadcast,   "interval", hours=3,  id="vb_alert")
scheduler.add_job(_alerta_nlp_con_broadcast,  "interval", hours=4,  id="nlp_alert")
scheduler.add_job(_verificacion_auto,         "interval", hours=6,  id="verify_preds")
scheduler.add_job(_alerta_sharp_auto,         "interval", hours=2,  id="sharp_auto")
scheduler.add_job(_heartbeat,                 "interval", hours=6,  id="heartbeat")
scheduler.add_job(_resumen_diario,            "cron",     hour=8,   id="daily_summary")
scheduler.add_job(_ml_auto_train,             "interval", hours=12, id="ml_train")
scheduler.add_job(_ml_avanzado_auto_train,    "interval", hours=24, id="ml_v2_train")
scheduler.add_job(_ml_auto_verify,            "interval", hours=6,  id="ml_verify")
scheduler.add_job(_bookmaker_auto_scan,       "interval", hours=6,  id="bookmaker_scan")
scheduler.add_job(_simulacion_auto_log,       "interval", hours=3,  id="simulacion_log")
scheduler.add_job(_accounting_sync,           "interval", hours=6,  id="accounting_sync")
scheduler.add_job(_journal_auto_log,          "interval", hours=4,  id="journal_auto")
scheduler.start()

register_webhook(os.getenv("RENDER_EXTERNAL_URL",""))

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.getenv("PORT",8000)))

