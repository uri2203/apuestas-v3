"""
Bot de Telegram — Blueprint Flask.

Mejoras vs versión original:
- Validación HMAC-SHA256 del webhook (previene peticiones falsas)
- Registro automático del webhook al inicializar
- Comandos separados del código de auth y scheduling
"""

import os
import hmac
import hashlib
import logging

import httpx
from flask import Blueprint, request, jsonify, current_app

logger = logging.getLogger(__name__)

telegram_bp = Blueprint("telegram", __name__)

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


# ── Helpers ───────────────────────────────────────────────────────────────────
def telegram_send(msg: str) -> bool:
    """Envía mensaje HTML a Telegram. Silencioso si no está configurado."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"},
            timeout=8,
        )
        return True
    except Exception as e:
        logger.warning("Telegram send error: %s", e)
        return False


def _verify_telegram_signature(body: bytes, secret_token: str) -> bool:
    """
    Valida la firma HMAC-SHA256 del webhook de Telegram.
    Telegram envía el header X-Telegram-Bot-Api-Secret-Token.
    Si no está configurado el secret_token, se omite la validación.
    """
    webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    if not webhook_secret:
        # Sin secret configurado, aceptar pero loguear advertencia
        logger.warning("TELEGRAM_WEBHOOK_SECRET no configurado — webhook sin validación HMAC")
        return True
    incoming = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
    return hmac.compare_digest(incoming, webhook_secret)


def register_webhook(app_url: str) -> None:
    """Registra el webhook en Telegram con secret token si está disponible."""
    if not TELEGRAM_TOKEN or not app_url:
        return
    webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
    payload = {"url": f"{app_url}/telegram/webhook"}
    if webhook_secret:
        payload["secret_token"] = webhook_secret
    try:
        r = httpx.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
            json=payload,
            timeout=10,
        )
        logger.info("Telegram webhook registrado: %s → %s", app_url, r.json())
    except Exception as e:
        logger.error("Telegram webhook error: %s", e)


# ── Webhook ───────────────────────────────────────────────────────────────────
@telegram_bp.route("/telegram/webhook", methods=["POST"])
def webhook():
    # 1. Validar firma
    if not _verify_telegram_signature(request.get_data(), TELEGRAM_TOKEN):
        logger.warning("Telegram webhook — firma inválida desde %s", request.remote_addr)
        return jsonify({"ok": False, "error": "invalid signature"}), 403

    data = request.get_json(silent=True) or {}
    msg  = data.get("message", {})
    text = msg.get("text", "").strip().lower()
    chat = str(msg.get("chat", {}).get("id", ""))

    # 2. Solo responder al chat autorizado
    if chat != TELEGRAM_CHAT_ID:
        return jsonify({"ok": True})

    # 3. Despachar comandos
    _dispatch(text)
    return jsonify({"ok": True})


def _dispatch(text: str) -> None:
    """Despacha comandos del bot."""
    parts = text.split()
    cmd = parts[0]
    args = parts[1:] if len(parts) > 1 else []

    if cmd == "/status":
        _cmd_status()
    elif cmd in ("/valuebet", "/vb", "/value"):
        _cmd_vb()
    elif cmd in ("/bankroll", "/br"):
        _cmd_bankroll()
    elif cmd in ("/apostar", "/bet"):
        _cmd_apostar(args)
    elif cmd == "/alertas":
        _cmd_alertas()
    elif cmd in ("/arbitraje", "/arb"):
        _cmd_arbitraje()
    elif cmd in ("/sharp", "/sharpmoney"):
        _cmd_sharp()
    elif cmd in ("/predicciones", "/preds"):
        _cmd_predicciones()
    elif cmd in ("/portfolio", "/port"):
        _cmd_portfolio()
    elif cmd in ("/brain", "/cerebro"):
        _cmd_brain(args)
    elif cmd in ("/brain-status", "/bs"):
        _cmd_brain_status()
    elif cmd in ("/brain-scan", "/bscan"):
        _cmd_brain_scan()
    elif cmd in ("/hulk", "/h"):
        _cmd_hulk(args)
    elif cmd in ("/hulk-status", "/hs"):
        _cmd_hulk_status()
    elif cmd in ("/hulk-scan", "/hscan"):
        _cmd_hulk_scan()
    elif cmd in ("/help", "/ayuda"):
        _cmd_help()


# ── Comandos ──────────────────────────────────────────────────────────────────
def _cmd_help() -> None:
    telegram_send(
        "<b>ApuestasPro Bot — Comandos</b>\n\n"
        "/status — Pronósticos de la jornada actual\n"
        "/vb — Value bets activos (edge > 5%)\n"
        "/bankroll — Estado del bankroll\n"
        "/apostar <partido> <seleccion> <cuota> <monto> — Registrar apuesta\n"
        "/alertas — Últimas alertas del sistema\n"
        "/arbitraje — Oportunidades de arbitraje\n"
        "/sharp — Señales de sharp money\n"
        "/predicciones — Predicciones ML del día\n"
        "/portfolio — Estado del portfolio activo\n"
        "/brain scan — Escaneo completo del Brain\n"
        "/brain-status — Performance del Brain (ROI, wins, P&L)\n"
        "/ayuda — Esta ayuda"
    )


def _cmd_bankroll() -> None:
    from database import get_bankroll_actual, get_bets_stats
    try:
        br = get_bankroll_actual()
        stats = get_bets_stats(30)
        lines = ["<b>💰 Bankroll</b>", ""]
        lines.append(f"Actual: <b>${br:,.2f}</b>")
        lines.append("")
        lines.append("📊 Últimos 30 días:")
        lines.append(f"  Apuestas: {stats.get('total', 0)}")
        lines.append(f"  Ganadas: {stats.get('ganadas', 0)}")
        lines.append(f"  Perdidas: {stats.get('perdidas', 0)}")
        gn = stats.get('ganancia_neta', 0) or 0
        sign = "+" if gn >= 0 else ""
        lines.append(f"  Ganancia neta: {sign}${gn:,.2f}")
        win_rate = stats.get('win_rate', 0)
        lines.append(f"  Win rate: {win_rate}%")
        telegram_send("\n".join(lines))
    except Exception as e:
        telegram_send(f"Error: {e}")


def _cmd_apostar(args: list) -> None:
    """Registrar apuesta: /apostar 'America vs Chivas' 'America' 2.10 100"""
    if len(args) < 4:
        telegram_send("Uso: /apostar \"partido\" \"seleccion\" cuota monto\n"
                      "Ej: /apostar \"America vs Chivas\" \"America\" 2.10 100")
        return
    partido = args[0]
    seleccion = args[1]
    try:
        cuota = float(args[2])
        monto = float(args[3])
    except ValueError:
        telegram_send("Cuota y monto deben ser números")
        return
    from database import db, _execute, get_bankroll_actual
    try:
        br = get_bankroll_actual()
        with db() as conn:
            _execute(conn,
                "INSERT INTO bets (partido, seleccion, cuota, monto, "
                "bankroll_antes, resultado) VALUES (?,?,?,?,?,?)",
                (partido, seleccion, cuota, monto, br, "pendiente"))
        msg = (
            f"<b>✅ Apuesta registrada</b>\n\n"
            f"Partido: {partido}\n"
            f"Selección: {seleccion}\n"
            f"Cuota: {cuota}\n"
            f"Monto: ${monto:.2f}\n"
            f"Retorno potencial: ${monto * cuota:.2f}"
        )
        telegram_send(msg)
    except Exception as e:
        telegram_send(f"Error registrando apuesta: {e}")


def _cmd_alertas() -> None:
    from database import db, _fetchall
    try:
        with db() as conn:
            rows = _fetchall(conn,
                "SELECT * FROM alerts_log ORDER BY id DESC LIMIT 5")
        if not rows:
            telegram_send("No hay alertas recientes")
            return
        lines = ["<b>🚨 Últimas Alertas</b>", ""]
        for r in rows:
            tipo = r.get("tipo", "?")
            detalle = (r.get("detalle", "") or "")[:80]
            urgencia = r.get("urgencia", "")
            emoji = {"ALTA": "🔴", "MEDIA": "🟡", "BAJA": "🟢"}.get(urgencia, "⚪")
            lines.append(f"{emoji} [{tipo}] {detalle}")
        telegram_send("\n".join(lines))
    except Exception as e:
        telegram_send(f"Error: {e}")


def _cmd_arbitraje() -> None:
    from services.deportes import get_any_odds_key
    api_key = get_any_odds_key()
    if not api_key:
        telegram_send("No hay API keys configuradas. Agrega ODDS_API_KEYS=key1,key2")
        return
    try:
        from services.deportes import get_odds_upcoming
        raw = get_odds_upcoming(api_key, regions="us,uk,eu")
        arbitrajes = []
        for m in raw if isinstance(raw, list) else []:
            ht = m.get("home_team", "") or ""
            at = m.get("away_team", "") or ""
            if not ht or not at:
                continue
            best = {}
            for book in m.get("bookmakers", []):
                for o in book.get("markets", [{}])[0].get("outcomes", []):
                    name = o.get("name", "")
                    price = o.get("price", 0)
                    if not name or price <= 1:
                        continue
                    prev = best.get(name)
                    if not prev or price > prev["cuota"]:
                        best[name] = {"cuota": price, "casa": book.get("title", "")}
            if len(best) < 2:
                continue
            L = sum(1.0 / v["cuota"] for v in best.values())
            if L >= 1:
                continue
            profit = round((1.0 / L - 1.0) * 100, 2)
            if profit >= 0.5:
                arbitrajes.append(f"💰 {ht} vs {at} | Profit: {profit}%")
        if arbitrajes:
            msg = "<b>💰 Arbitrajes Detectados</b>\n\n" + "\n".join(arbitrajes[:5])
        else:
            msg = "No hay arbitrajes > 0.5% en este momento"
        telegram_send(msg)
    except Exception as e:
        telegram_send(f"Error: {e}")


def _cmd_sharp() -> None:
    from services.deportes import get_any_odds_key
    api_key = get_any_odds_key()
    if not api_key:
        telegram_send("No hay API keys configuradas. Agrega ODDS_API_KEYS=key1,key2")
        return
    try:
        from services.sharp_money import analizar_partido_sharp
        from services.deportes import get_odds_upcoming
        raw = get_odds_upcoming(api_key, regions="us,uk,eu")
        alertas = []
        for m in raw[:12] if isinstance(raw, list) else []:
            ht = m.get("home_team", "") or ""
            at = m.get("away_team", "") or ""
            if not ht or not at:
                continue
            lineas = {}
            for book in m.get("bookmakers", []):
                casa = book.get("title", "")
                for o in book.get("markets", [{}])[0].get("outcomes", []):
                    if o.get("name", "").lower() == ht.lower():
                        lineas[casa] = o["price"]
                        break
            if len(lineas) < 2:
                continue
            vals = list(lineas.values())
            res = analizar_partido_sharp(f"{ht} vs {at}", max(vals),
                                         sum(vals) / len(vals), 50, 50,
                                         lineas_por_casa=lineas, dias_antes=2)
            score = res.get("score_sharp", {}).get("score", 0)
            if score >= 65:
                clasif = res.get("score_sharp", {}).get("clasificacion", "")
                alertas.append(f"⚡ {ht} vs {at} — Score {score}/100 — {clasif}")
        if alertas:
            msg = "<b>⚡ Sharp Money</b>\n\n" + "\n".join(alertas[:5])
        else:
            msg = "Sin señales sharp significativas"
        telegram_send(msg)
    except Exception as e:
        telegram_send(f"Error: {e}")


def _cmd_predicciones() -> None:
    from database import db, _fetchall, _USE_PG
    dc = "created_at::date" if _USE_PG else "date(created_at)"
    td = "CURRENT_DATE" if _USE_PG else "date('now')"
    try:
        with db() as conn:
            rows = _fetchall(conn,
                f"SELECT * FROM predictions WHERE {dc} = {td} "
                f"AND resultado_real IS NULL ORDER BY confianza_pct DESC LIMIT 5")
        if not rows:
            telegram_send("No hay predicciones para hoy")
            return
        lines = ["<b>🔮 Predicciones ML — Hoy</b>", ""]
        for r in rows:
            home = r.get("home", "")
            away = r.get("away", "")
            pick = r.get("pronostico", "?")
            conf = r.get("confianza_pct", 0)
            emoji = "⭐" if conf > 55 else "◇"
            lines.append(f"{emoji} {home} vs {away} → <b>[{pick}]</b> {conf}%")
        telegram_send("\n".join(lines))
    except Exception as e:
        telegram_send(f"Error: {e}")


def _cmd_portfolio() -> None:
    from services.portfolio import get_portfolio_status
    try:
        port = get_portfolio_status()
        if "error" in port:
            telegram_send(f"Error: {port['error']}")
            return
        lines = ["<b>📊 Portfolio Activo</b>", ""]
        lines.append(f"Apuestas activas: {port['total_apuestas']}")
        lines.append(f"Total expuesto: <b>${port['total_expuesto']:,.2f}</b>")
        lines.append(f"Ganancia potencial: <b>+${port['ganancia_potencial_max']:,.2f}</b>")
        lines.append("")
        for liga, info in port.get("por_liga", {}).items():
            lines.append(f"  {liga}: {info['total']} apuestas (${info['monto']:,.0f})")
        telegram_send("\n".join(lines))
    except Exception as e:
        telegram_send(f"Error: {e}")


def _cmd_brain(args: list) -> None:
    """Comandos del Brain: /brain scan, /brain status"""
    sub = args[0].lower() if args else "status"
    if sub == "scan":
        _cmd_brain_scan()
    elif sub == "status":
        _cmd_brain_status()
    else:
        telegram_send("Uso: /brain scan | /brain status")


def _cmd_brain_status() -> None:
    """Muestra performance del Brain."""
    try:
        from services.brain import get_performance
        p = get_performance()
        pnl_emoji = "🟢" if p["pnl_total"] >= 0 else "🔴"
        streak = f"+{p['racha_actual']}" if p["racha_actual"] > 0 else str(p["racha_actual"])
        lines = [
            "<b>🧠 AGENTE BRAIN — Performance</b>",
            "━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            f"💰 Bankroll: <b>${p['bankroll_actual']:,.2f}</b>",
            f"{pnl_emoji} P&L: <b>${p['pnl_total']:+,.2f}</b> ({p['roi']:+.1f}%)",
            f"📊 Win Rate: <b>{p['win_rate']}%</b>",
            f"🎯 Trades: {p['trades_ganados']}W / {p['trades_perdidos']}L ({p['trades_total']} total)",
            f"📈 Racha: <b>{streak}</b>",
            f"📉 Max Drawdown: {p['max_drawdown_pct']:.1f}%",
        ]
        if p["kill_switch"]:
            lines.append("")
            lines.append(f"⚠️ <b>KILL SWITCH:</b> {p['kill_reason']}")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━")
        telegram_send("\n".join(lines))
    except Exception as e:
        telegram_send(f"Error Brain: {e}")


def _cmd_brain_scan() -> None:
    """Ejecuta scan completo del Brain y envía señales."""
    try:
        from services.brain import scan, simulate_trades
        result = scan(threshold=80)
        raw = result.get("raw_signals_count", 0)
        filtered = result.get("filtered_signals", 0)
        trades = result.get("trades", [])
        lines = [
            "<b>🧠 BRAIN SCAN</b>",
            "━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📡 Raw: {raw} → Filtradas: {filtered}",
            "",
        ]
        if not trades:
            lines.append("Sin señales que superen el umbral.")
        else:
            for i, t in enumerate(trades[:5], 1):
                score = t.get("confidence_score", 0)
                emoji = "🟢" if score >= 90 else "🟡" if score >= 85 else "🔵"
                lines.append(f"{emoji} <b>#{i} — {t['match']}</b>")
                lines.append(f"   ✅ {t['best_selection']} @ {t['best_odds']}")
                lines.append(f"   📊 Score: {score} | Edge: {t['avg_edge_pct']}%")
                lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("⚙️ Kelly: 20% | Umbral: 88% | Cuota: 1.80-3.00")
        telegram_send("\n".join(lines))
    except Exception as e:
        telegram_send(f"Error Brain scan: {e}")


def _cmd_hulk(args: list) -> None:
    """Comandos del Hulk: /hulk scan, /hulk status"""
    sub = args[0].lower() if args else "status"
    if sub == "scan":
        _cmd_hulk_scan()
    elif sub == "status":
        _cmd_hulk_status()
    elif sub == "steam":
        _cmd_hulk_steam()
    elif sub == "live":
        _cmd_hulk_live()
    elif sub == "arb":
        _cmd_hulk_arb()
    else:
        telegram_send("Uso: /hulk scan | /hulk status | /hulk steam | /hulk live | /hulk arb")


def _cmd_hulk_status() -> None:
    """Muestra performance del Hulk."""
    try:
        from services.hulk import get_performance
        p = get_performance()
        pnl_emoji = "🟢" if p["total_pnl"] >= 0 else "🔴"
        streak = f"+{p['racha_actual']}" if p["racha_actual"] > 0 else str(p["racha_actual"])
        lines = [
            "<b>🦖 HULK AGENT — Performance</b>",
            "━━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            f"💰 Bankroll: <b>${p['bankroll_actual']:,.2f}</b>",
            f"{pnl_emoji} P&L: <b>${p['total_pnl']:+,.2f}</b> ({p['roi']:+.1f}%)",
            f"🎯 Win Rate: <b>{p['win_rate']}%</b>",
            f"📊 Trades: {p['total_won']}W / {p['total_lost']}L ({p['total_trades']} total)",
            f"📈 Racha: <b>{streak}</b>",
        ]
        if p["kill_switch"]:
            lines.append("")
            lines.append(f"⚠️ <b>KILL SWITCH:</b> {p['kill_reason']}")
        lines.append("")
        lines.append("<b>Modos:</b>")
        for mode, stats in p.get("by_mode", {}).items():
            if stats["trades"] > 0:
                emoji = {"HAWK":"🔴","HUNTER":"🟡","KILLER":"🟢","HULK":"⚡","SHARK":"🦈"}.get(mode, "")
                lines.append(f"  {emoji} {mode}: {stats['trades']} trades | {stats['win_rate']}% WR | ${stats['pnl']:+.2f}")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━")
        telegram_send("\n".join(lines))
    except Exception as e:
        telegram_send(f"Error Hulk: {e}")


def _cmd_hulk_scan() -> None:
    """Ejecuta scan completo del Hulk."""
    try:
        from services.hulk import scan
        result = scan()
        lines = [
            "<b>🦖 HULK SCAN</b>",
            "━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"⚡ Steam: {result.get('steam_moves', 0)}",
            f"🔴 Live: {result.get('live_opportunities', 0)}",
            f"💰 Arbitraje: {result.get('arbitrage', 0)}",
            f"🔄 Contrarian: {result.get('contrarian', 0)}",
            "",
            f"<b>Trades ejecutados:</b> {result.get('trades_executed', 0)}",
            f"<b>Modos usados:</b> {', '.join(result.get('modes_used', []))}",
            f"<b>Bankroll:</b> ${result.get('bankroll', 0):,.2f}",
            "",
        ]
        for t in result.get("executed", [])[:5]:
            lines.append(f"{t.get('mode_emoji','')} <b>{t['mode']}</b> — {t['match']}")
            lines.append(f"   ✅ {t['selection']} @ {t['odds']} | Edge: {t['edge_pct']}% | Stake: ${t['stake']}")
        if not result.get("executed"):
            lines.append("Sin trades ejecutados en este scan.")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━")
        telegram_send("\n".join(lines))
    except Exception as e:
        telegram_send(f"Error Hulk scan: {e}")


def _cmd_hulk_steam() -> None:
    """Detecta steam moves."""
    try:
        from services.hulk import detect_steam_moves
        moves = detect_steam_moves()
        lines = ["<b>⚡ STEAM MOVES</b>", "━━━━━━━━━━━━━━━━━━━━━━━━━"]
        if not moves:
            lines.append("Sin steam moves detectados.")
        else:
            for m in moves[:5]:
                lines.append(f"<b>{m['match']}</b> → {m['selection']}")
                lines.append(f"   Sharp: {m['sharp_avg']} vs Square: {m['square_avg']}")
                lines.append(f"   Edge: {m['edge_pct']}% | Casas: {', '.join(m['sharp_books'])}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━")
        telegram_send("\n".join(lines))
    except Exception as e:
        telegram_send(f"Error: {e}")


def _cmd_hulk_live() -> None:
    """Escanea live betting."""
    try:
        from services.hulk import scan_live_opportunities
        live = scan_live_opportunities()
        lines = ["<b>🔴 LIVE BETTING</b>", "━━━━━━━━━━━━━━━━━━━━━━━━━"]
        if not live:
            lines.append("Sin oportunidades live.")
        else:
            for l in live[:5]:
                lines.append(f"<b>{l['match']}</b> → {l['selection']} @ {l['odds']}")
                lines.append(f"   Edge: {l['edge_pct']}% | {l['reason']}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━")
        telegram_send("\n".join(lines))
    except Exception as e:
        telegram_send(f"Error: {e}")


def _cmd_hulk_arb() -> None:
    """Caza arbitrajes."""
    try:
        from services.hulk import hunt_arbitrage
        arbs = hunt_arbitrage()
        lines = ["<b>💰 ARBITRAJE</b>", "━━━━━━━━━━━━━━━━━━━━━━━━━"]
        if not arbs:
            lines.append("Sin arbitrajes detectados.")
        else:
            for a in arbs[:3]:
                lines.append(f"<b>{a['match']}</b> → PROFIT: {a['profit_pct']}%")
                for sel, book in a.get("best_books", {}).items():
                    lines.append(f"   {sel}: {a['best_odds'][sel]} @ {book}")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━")
        telegram_send("\n".join(lines))
    except Exception as e:
        telegram_send(f"Error: {e}")


def _cmd_status() -> None:
    from services.progol import generar_jornada_progol
    api_key = os.getenv("API_FOOTBALL_KEY", "")
    try:
        j = generar_jornada_progol(api_key)
        lines = ["<b>ApuestasPro — Estado del sistema</b>", ""]
        for p in (j.get("partidos") or [])[:5]:
            conf = p.get("confianza_pct", 0)
            pick = p.get("pronostico", "?")
            home = p.get("local_nombre") or p.get("home", "")
            away = p.get("visitante_nombre") or p.get("away", "")
            star = "⭐" if conf > 55 else "◇"
            lines.append(f"{star} {home} vs {away} → <b>[{pick}]</b> {conf}%")
        telegram_send("\n".join(lines))
    except Exception as e:
        telegram_send(f"Error al cargar jornada: {e}")


def _cmd_vb() -> None:
    from services.progol import generar_jornada_progol, predecir_partido
    from services.deportes import get_any_odds_key
    api_key = get_any_odds_key()
    if not api_key:
        telegram_send(
            "<b>Value Bets — Liga MX (demo)</b>\n\n"
            "Chivas vs América → +8.4% edge (Bet365)\n"
            "Toluca vs Santos → +10.0% edge (Codere)\n\n"
            "Configura ODDS_API_KEYS=key1,key2 para datos reales."
        )
        return
    try:
        r = httpx.get(
            "https://api.the-odds-api.com/v4/sports/soccer_mexico_ligamx/odds",
            params={"apiKey": api_key, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"},
            timeout=10,
        )
        lines = ["<b>🔥 Value Bets — Liga MX</b>", ""]
        found = 0
        for m in r.json():
            ht, at = m["home_team"], m["away_team"]
            try:
                pred = predecir_partido(ht, at)
                model_probs = {ht: pred["local"], "Draw": pred["empate"], at: pred["visitante"]}
            except Exception:
                model_probs = {}
            for book in m.get("bookmakers", []):
                for o in book.get("markets", [{}])[0].get("outcomes", []):
                    mp = model_probs.get(o["name"], model_probs.get("Draw", 0))
                    if mp <= 0:
                        continue
                    edge = round((mp * o["price"] - 1) * 100, 1)
                    if edge >= 7:
                        lines.append(f"⚡ {ht} vs {at} | {o['name']} @ {o['price']} | Edge +{edge}% ({book['title']})")
                        found += 1
        if found == 0:
            lines.append("Sin value bets > 7% en este momento.")
        telegram_send("\n".join(lines[:8]))
    except Exception as e:
        telegram_send(f"Error obteniendo value bets: {e}")



def _cmd_help() -> None:
    telegram_send(
        "<b>ApuestasPro Bot — Comandos</b>\n\n"
        "/status — Pronósticos de la jornada actual\n"
        "/vb — Value bets activos\n"
        "/melate — Números calientes y fríos\n"
        "/ayuda — Esta ayuda"
    )


# ── Alertas automáticas (llamadas por el scheduler) ───────────────────────────
def alerta_value_bets() -> None:
    """Detecta value bets y los envía a Telegram (llamar desde scheduler)."""
    from services.deportes import get_any_odds_key
    api_key = get_any_odds_key()
    if not api_key or not TELEGRAM_TOKEN:
        return
    try:
        from services.progol import predecir_partido
        r = httpx.get(
            "https://api.the-odds-api.com/v4/sports/soccer_mexico_ligamx/odds",
            params={"apiKey": api_key, "regions": "eu", "markets": "h2h", "oddsFormat": "decimal"},
            timeout=10,
        )
        fuertes = []
        for m in r.json():
            ht, at = m["home_team"], m["away_team"]
            try:
                pred = predecir_partido(ht, at)
                model_probs = {ht: pred["local"], "Draw": pred["empate"], at: pred["visitante"]}
            except Exception:
                model_probs = {}
            for book in m.get("bookmakers", []):
                for o in book.get("markets", [{}])[0].get("outcomes", []):
                    mp = model_probs.get(o["name"], 0)
                    if mp <= 0:
                        continue
                    edge = round((mp * o["price"] - 1) * 100, 1)
                    if edge >= 7:
                        fuertes.append(
                            f"⚡ {ht} vs {at} | {o['name']} @ {o['price']} "
                            f"| Edge +{edge}% ({book['title']})"
                        )
        if fuertes:
            msg = "<b>🔥 STRONG VALUE BETS DETECTADOS</b>\n\n" + "\n".join(fuertes[:5])
            telegram_send(msg)
    except Exception as e:
        logger.error("alerta_value_bets: %s", e)


def alerta_nlp() -> None:
    """Escanea NLP y alerta si hay lesiones críticas (llamar desde scheduler)."""
    if not TELEGRAM_TOKEN:
        return
    try:
        from services.nlp_sentiment import scan_completo
        from services.progol import generar_jornada_progol
        api_key = os.getenv("API_FOOTBALL_KEY", "")
        j = generar_jornada_progol(api_key)
        for p in (j.get("partidos") or [])[:4]:
            home = p.get("local_nombre") or p.get("home", "")
            away = p.get("visitante_nombre") or p.get("away", "")
            if not home or not away:
                continue
            scan = scan_completo(home, away)
            for e in scan.get("alertas_edge", []):
                if e.get("urgencia") == "ALTA":
                    msg = (
                        f"🚨 <b>LESIÓN CRÍTICA DETECTADA — EDGE ACTIVO</b>\n\n"
                        f"Partido: {home} vs {away}\n"
                        f"Alerta: {e['detalle']}\n"
                        f"→ {e['accion']}\n"
                        f"Ventana: {e.get('ventana_min', '?')} minutos"
                    )
                    telegram_send(msg)
    except Exception as e:
        logger.error("alerta_nlp: %s", e)

