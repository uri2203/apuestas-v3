"""
Autenticación — Blueprint Flask.

Mejoras vs versión original:
- Sesiones firmadas con itsdangerous (sobreviven reinicios siempre que
  SESSION_SECRET sea constante en las env vars)
- Rate limiting simple en memoria (5 intentos / 15 min por IP)
- Sin almacenamiento server-side de tokens
- CSRF básico via SameSite=Strict en cookie
"""

import os
import time
import hashlib
import secrets
from collections import defaultdict
from functools import wraps

from flask import (
    Blueprint, request, redirect, url_for,
    make_response, jsonify, current_app,
)
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

auth_bp = Blueprint("auth", __name__)

# ── Configuración ─────────────────────────────────────────────────────────────
APP_PASSWORD    = os.getenv("APP_PASSWORD", "")
SESSION_SECRET  = os.getenv("SESSION_SECRET", secrets.token_hex(32))
SESSION_DAYS    = int(os.getenv("SESSION_DAYS", "7"))
COOKIE_NAME     = "ap_session"

_serializer = URLSafeTimedSerializer(SESSION_SECRET, salt="apuestaspro-auth")

# ── Rate limiter en memoria ───────────────────────────────────────────────────
# {ip: [(timestamp, ...], ...}
_attempts: dict[str, list[float]] = defaultdict(list)
_WINDOW   = 15 * 60   # 15 minutos
_MAX_TRIES = 5


def _rate_ok(ip: str) -> bool:
    """Devuelve True si el IP puede intentar login. Limpia entradas viejas."""
    now = time.time()
    _attempts[ip] = [t for t in _attempts[ip] if now - t < _WINDOW]
    if len(_attempts[ip]) >= _MAX_TRIES:
        return False
    _attempts[ip].append(now)
    return True


def _remaining_wait(ip: str) -> int:
    """Segundos hasta que el bloqueo se levante."""
    if not _attempts[ip]:
        return 0
    oldest = min(_attempts[ip])
    return max(0, int(_WINDOW - (time.time() - oldest)))


# ── Helpers de sesión ─────────────────────────────────────────────────────────
def _create_session_cookie() -> str:
    """Genera token firmado con expiración embebida."""
    return _serializer.dumps({"user": "admin"})


def _verify_session(token: str) -> bool:
    """Verifica firma y expiración. False en cualquier error."""
    if not token:
        return False
    try:
        _serializer.loads(token, max_age=SESSION_DAYS * 86400)
        return True
    except (BadSignature, SignatureExpired):
        return False


def valid_session() -> bool:
    """Comprueba la cookie de sesión del request actual."""
    return _verify_session(request.cookies.get(COOKIE_NAME, ""))


# ── Decorador ────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not valid_session():
            if request.path.startswith("/api/"):
                return jsonify({"error": "No autorizado"}), 401
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


# ── Hash de contraseña ────────────────────────────────────────────────────────
def _hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# ── Rutas ────────────────────────────────────────────────────────────────────
_LOGIN_HTML = """<!DOCTYPE html>
<html lang="es"><head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>ApuestasPro — Acceso</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono&display=swap" rel="stylesheet"/>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{min-height:100vh;display:flex;align-items:center;justify-content:center;
  background:radial-gradient(ellipse at 60% 20%,rgba(124,109,250,.15) 0%,#07070a 60%);
  font-family:'Syne',sans-serif;color:#e8e8f2}}
.card{{background:#0e0e14;border:1px solid rgba(255,255,255,.08);border-radius:16px;
  padding:48px 40px;width:360px;text-align:center;box-shadow:0 24px 64px rgba(0,0,0,.6)}}
.logo{{font-size:32px;font-weight:800;margin-bottom:6px}}
.logo em{{color:#7c6dfa;font-style:normal}}
.sub{{font-size:11px;font-family:'DM Mono',monospace;color:#5a5a7a;margin-bottom:36px}}
.field{{margin-bottom:16px;text-align:left}}
.field label{{font-size:10px;font-family:'DM Mono',monospace;color:#5a5a7a;
  display:block;margin-bottom:5px;letter-spacing:.5px}}
.field input{{width:100%;padding:11px 14px;border-radius:8px;
  background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);
  color:#e8e8f2;font-size:14px;font-family:'Syne',sans-serif;
  transition:border-color .15s;outline:none}}
.field input:focus{{border-color:#7c6dfa}}
.btn{{width:100%;padding:12px;border-radius:8px;background:#7c6dfa;color:#fff;
  font-size:14px;font-weight:700;font-family:'Syne',sans-serif;
  border:none;cursor:pointer;transition:all .15s;margin-top:8px}}
.btn:hover{{background:#9585ff;transform:translateY(-1px)}}
.error{{background:rgba(248,113,113,.1);border:1px solid rgba(248,113,113,.25);
  color:#f87171;border-radius:7px;padding:10px 14px;font-size:12px;
  font-family:'DM Mono',monospace;margin-bottom:16px}}
.warn{{background:rgba(251,191,36,.1);border:1px solid rgba(251,191,36,.25);
  color:#fbbf24;border-radius:7px;padding:10px 14px;font-size:12px;
  font-family:'DM Mono',monospace;margin-bottom:16px}}
.badge{{margin-top:28px;font-size:10px;font-family:'DM Mono',monospace;color:#2e2e48}}
</style></head><body>
<div class="card">
  <div class="logo">Apuestas<em>Pro</em></div>
  <div class="sub">v4.2 · Sistema Profesional</div>
  {alert}
  <form method="POST" action="/login">
    <div class="field">
      <label>CONTRASEÑA DE ACCESO</label>
      <input type="password" name="password" placeholder="••••••••••••"
             autofocus autocomplete="current-password"/>
    </div>
    <button class="btn" type="submit">Entrar al sistema →</button>
  </form>
  <div class="badge">Dixon-Coles · ELO · Sharp Money · NLP · CLV · Kelly</div>
</div>
</body></html>"""


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Verificar que APP_PASSWORD esté configurada
    if not APP_PASSWORD:
        warn = '<div class="warn">⚠ Configura APP_PASSWORD en las variables de entorno.</div>'
        return _LOGIN_HTML.format(alert=warn), 200, {"Content-Type": "text/html; charset=utf-8"}

    error = ""
    if request.method == "POST":
        ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()

        if not _rate_ok(ip):
            wait = _remaining_wait(ip)
            error = f"Demasiados intentos. Espera {wait // 60}m {wait % 60}s."
        else:
            pw = request.form.get("password", "")
            if APP_PASSWORD and _hash_pw(pw) == _hash_pw(APP_PASSWORD):
                token = _create_session_cookie()
                resp = make_response(redirect("/"))
                resp.set_cookie(
                    COOKIE_NAME, token,
                    max_age=SESSION_DAYS * 86400,
                    httponly=True,
                    samesite="Strict",
                    secure=request.is_secure,
                )
                return resp
            error = "Contraseña incorrecta."

    alert = f'<div class="error">{error}</div>' if error else ""
    return _LOGIN_HTML.format(alert=alert), 200, {"Content-Type": "text/html; charset=utf-8"}


@auth_bp.route("/logout")
def logout():
    resp = make_response(redirect("/login"))
    resp.delete_cookie(COOKIE_NAME)
    return resp
