"""
Alertas por email — SMTP con Gmail u otro proveedor.

Variables de entorno requeridas:
  EMAIL_FROM       = tu-email@gmail.com
  EMAIL_PASSWORD   = contraseña de aplicación (no tu contraseña normal)
  EMAIL_TO         = destinatario (puede ser igual a FROM)
  EMAIL_SMTP_HOST  = smtp.gmail.com (default)
  EMAIL_SMTP_PORT  = 587 (default, TLS)

Para Gmail: activar "Contraseñas de aplicación" en
https://myaccount.google.com/apppasswords
"""

import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

logger = logging.getLogger(__name__)

EMAIL_FROM      = os.getenv("EMAIL_FROM", "")
EMAIL_PASSWORD  = os.getenv("EMAIL_PASSWORD", "")
EMAIL_TO        = os.getenv("EMAIL_TO", EMAIL_FROM)
SMTP_HOST       = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT       = int(os.getenv("EMAIL_SMTP_PORT", "587"))


def _email_configurado() -> bool:
    return bool(EMAIL_FROM and EMAIL_PASSWORD and EMAIL_TO)


def enviar_email(asunto: str, html: str, texto: str = "") -> bool:
    """Envía email HTML. Retorna True si fue exitoso."""
    if not _email_configurado():
        logger.debug("Email no configurado — skipping")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = asunto
        msg["From"]    = EMAIL_FROM
        msg["To"]      = EMAIL_TO

        if texto:
            msg.attach(MIMEText(texto, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

        logger.info("Email enviado: %s", asunto)
        return True
    except Exception as e:
        logger.error("Error enviando email: %s", e)
        return False


# ── Templates ────────────────────────────────────────────────────────────────

_BASE_HTML = """
<!DOCTYPE html><html lang="es"><head>
<meta charset="UTF-8"/>
<style>
  body{{font-family:Arial,sans-serif;background:#f5f5f5;padding:20px;color:#333}}
  .card{{background:#fff;border-radius:8px;padding:24px;max-width:600px;margin:0 auto;
         box-shadow:0 2px 8px rgba(0,0,0,.08)}}
  .header{{background:#7c6dfa;color:#fff;padding:16px 24px;border-radius:8px 8px 0 0;margin:-24px -24px 20px}}
  h1{{margin:0;font-size:20px}}
  .badge{{display:inline-block;padding:3px 10px;border-radius:12px;font-size:12px;font-weight:bold}}
  .badge-red{{background:#fee2e2;color:#b91c1c}}
  .badge-green{{background:#dcfce7;color:#166534}}
  .badge-yellow{{background:#fef9c3;color:#854d0e}}
  .badge-blue{{background:#dbeafe;color:#1e40af}}
  table{{width:100%;border-collapse:collapse;margin:12px 0}}
  td,th{{padding:8px 12px;text-align:left;border-bottom:1px solid #eee;font-size:14px}}
  th{{color:#666;font-weight:normal}}
  .footer{{color:#999;font-size:12px;margin-top:20px;text-align:center}}
  .big-num{{font-size:28px;font-weight:bold;color:#7c6dfa}}
</style></head><body>
<div class="card">
  <div class="header"><h1>🎯 ApuestasPro — {titulo}</h1></div>
  {contenido}
  <div class="footer">ApuestasPro v4.2 · {fecha} · Este email se generó automáticamente</div>
</div></body></html>
"""


def email_resumen_diario(stats: dict, value_bets: list, predicciones: list) -> bool:
    """Resumen diario con estadísticas del bankroll, VBs y predicciones del día."""
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Bankroll section
    br = stats.get("bankroll", {})
    ap = stats.get("apuestas", {})
    rend = stats.get("rendimiento", {})

    roi_color = "green" if rend.get("roi_pct", 0) > 0 else "red"

    vb_rows = ""
    for vb in value_bets[:5]:
        vb_rows += f"""<tr>
            <td>{vb.get('partido','')}</td>
            <td>{vb.get('resultado','')}</td>
            <td>{vb.get('cuota','')}</td>
            <td><span class="badge badge-green">+{vb.get('edge_pct',0)}%</span></td>
        </tr>"""

    pred_rows = ""
    for p in predicciones[:5]:
        color = "blue" if p.get("confianza_pct", 0) > 55 else "yellow"
        pred_rows += f"""<tr>
            <td>{p.get('home','')} vs {p.get('away','')}</td>
            <td><strong>[{p.get('pronostico','')}]</strong></td>
            <td><span class="badge badge-{color}">{p.get('confianza_pct',0)}%</span></td>
        </tr>"""

    contenido = f"""
    <table>
      <tr><th>Bankroll actual</th><td><span class="big-num">${br.get('actual', 0):,.2f}</span></td></tr>
      <tr><th>ROI total</th><td><span class="badge badge-{roi_color}">{rend.get('roi_pct', 0)}%</span></td></tr>
      <tr><th>Win rate</th><td>{ap.get('win_rate_pct', 0)}%</td></tr>
      <tr><th>Apuestas resueltas</th><td>{ap.get('resueltas', 0)} ({ap.get('ganadas', 0)}W / {ap.get('perdidas', 0)}L)</td></tr>
      <tr><th>Profit neto</th><td>${rend.get('profit_neto', 0):,.2f}</td></tr>
    </table>

    <h3 style="margin:20px 0 8px">🔥 Value Bets detectados</h3>
    {'<table><tr><th>Partido</th><th>Selección</th><th>Cuota</th><th>Edge</th></tr>' + vb_rows + '</table>' if vb_rows else '<p style="color:#999">Sin value bets activos en este momento.</p>'}

    <h3 style="margin:20px 0 8px">📊 Predicciones del día</h3>
    {'<table><tr><th>Partido</th><th>Pronóstico</th><th>Confianza</th></tr>' + pred_rows + '</table>' if pred_rows else '<p style="color:#999">Sin predicciones generadas hoy.</p>'}
    """

    html = _BASE_HTML.format(titulo="Resumen Diario", contenido=contenido, fecha=fecha)
    return enviar_email(f"ApuestasPro — Resumen {datetime.now().strftime('%d/%m/%Y')}", html)


def email_alerta_value_bet(partido: str, resultado: str, cuota: float, edge: float, casa: str) -> bool:
    """Alerta inmediata cuando se detecta un value bet fuerte (>8%)."""
    if edge < 8:
        return False
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    contenido = f"""
    <div style="text-align:center;padding:20px 0">
        <div class="big-num">+{edge}% Edge</div>
        <p style="font-size:18px;margin:8px 0">{partido}</p>
        <p><span class="badge badge-green">{resultado} @ {cuota}</span> en {casa}</p>
    </div>
    <p style="color:#666;font-size:14px">
        El modelo detectó una probabilidad significativamente mayor a la implícita en la cuota.
        La ventana de oportunidad puede cerrar en minutos.
    </p>
    """
    html = _BASE_HTML.format(titulo="🚨 Value Bet Detectado", contenido=contenido, fecha=fecha)
    return enviar_email(f"⚡ Value Bet: {partido} — Edge +{edge}%", html)


def email_alerta_lesion(home: str, away: str, detalle: str, accion: str) -> bool:
    """Alerta cuando NLP detecta baja crítica de jugador titular."""
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    contenido = f"""
    <div style="background:#fee2e2;border-radius:8px;padding:16px;margin-bottom:16px">
        <strong style="color:#b91c1c">🚨 BAJA CONFIRMADA</strong><br/>
        <span style="font-size:16px">{home} vs {away}</span>
    </div>
    <table>
      <tr><th>Detalle</th><td>{detalle}</td></tr>
      <tr><th>Acción recomendada</th><td><strong>{accion}</strong></td></tr>
      <tr><th>Ventana</th><td>~20 minutos antes que las casas ajusten líneas</td></tr>
    </table>
    """
    html = _BASE_HTML.format(titulo="🚨 Lesión Crítica Detectada", contenido=contenido, fecha=fecha)
    return enviar_email(f"🚨 Lesión: {home} vs {away} — Actuar ahora", html)


def enviar_resumen_diario_completo() -> None:
    """Llama desde el scheduler para enviar el resumen diario."""
    if not _email_configurado():
        return
    try:
        from services.bankroll import estadisticas_bankroll
        from services.progol import generar_jornada_progol
        import os

        stats = estadisticas_bankroll()
        jornada = generar_jornada_progol(os.getenv("API_FOOTBALL_KEY", ""))
        predicciones = jornada.get("partidos", [])[:5]

        # Últimos VBs del log
        from database import db, rows_to_list
        with db() as conn:
            vbs = rows_to_list(conn.execute(
                "SELECT * FROM value_bets_log ORDER BY id DESC LIMIT 5"
            ).fetchall())

        email_resumen_diario(stats, vbs, predicciones)
    except Exception as e:
        logger.error("Error enviando resumen diario: %s", e)
