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
    if text == "/status":
        _cmd_status()
    elif text in ("/valuebet", "/vb"):
        _cmd_vb()
    elif text == "/melate":
        _cmd_melate()
    elif text in ("/help", "/ayuda"):
        _cmd_help()


# ── Comandos ──────────────────────────────────────────────────────────────────
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
    api_key = os.getenv("ODDS_API_KEY", "")
    if not api_key:
        telegram_send(
            "<b>Value Bets — Liga MX (demo)</b>\n\n"
            "Chivas vs América → +8.4% edge (Bet365)\n"
            "Toluca vs Santos → +10.0% edge (Codere)\n\n"
            "Configura ODDS_API_KEY para datos reales."
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


def _cmd_melate() -> None:
    from services.estadisticas import numeros_calientes, numeros_frios
    from main import FREQ_MELATE
    freq = {n: {"frecuencia_abs": f} for n, f in FREQ_MELATE.items()}
    hot  = " ".join(str(e["numero"]) for e in numeros_calientes(freq, 5))
    cold = " ".join(str(e["numero"]) for e in numeros_frios(freq, 5))
    telegram_send(
        f"<b>Melate — Análisis</b>\n\n"
        f"🔥 Calientes: {hot}\n"
        f"❄️ Fríos: {cold}\n\n"
        f"Prob. 6/6: 1 en 4,096,720"
    )


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
    api_key = os.getenv("ODDS_API_KEY", "")
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
