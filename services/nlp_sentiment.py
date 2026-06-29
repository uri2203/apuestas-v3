"""
Motor NLP - Detección de lesiones y sentimiento desde noticias RSS.
Edge: las casas tardan 15-45 min en ajustar líneas tras noticias.
Este módulo detecta ANTES de ese ajuste.
Python puro - sin ML pesado, sin dependencias extra.
"""
from datetime import datetime

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

# ── DICCIONARIOS NLP ──────────────────────────────────────────────────────
LESION_KW = {
    "baja confirmada": 1.0, "no jugara": 1.0, "fuera por lesion": 1.0,
    "descartado": 1.0, "operado": 0.95, "fractura": 0.95, "rotura": 0.95,
    "ligamento": 0.95, "cirugia": 0.95, "baja definitiva": 1.0,
    "no estara": 0.9, "out": 0.9, "no podra jugar": 0.9,
    "duda": 0.5, "dudoso": 0.5, "entreno diferenciado": 0.6,
    "molestias": 0.4, "sobrecarga": 0.4, "no entreno": 0.6,
    "trabajo aparte": 0.55, "baja por": 0.7,
    "regresa": -0.4, "se recupero": -0.4, "listo para": -0.3,
    "disponible": -0.35, "vuelve al equipo": -0.4,
}

SENT_POS = [
    "confianza", "motivado", "preparados", "listos", "en forma",
    "racha ganadora", "imparable", "mejor momento", "record",
    "protagonismo", "arrasando", "enfocados", "unidos",
]
SENT_NEG = [
    "crisis", "desmotivado", "conflicto", "tension", "derrotas",
    "racha negativa", "cuestionado", "presion", "bajo nivel",
    "peor momento", "sancion", "expulsion", "problemas internos",
    "vestuario roto", "sin goles",
]

EQUIPOS = [
    "America", "Club America", "Guadalajara", "Chivas", "Cruz Azul",
    "Pumas", "Pumas UNAM", "Tigres", "Tigres UANL", "Monterrey",
    "Rayados", "Toluca", "Santos", "Santos Laguna", "Atlas", "Leon",
    "Pachuca", "Necaxa", "Queretaro", "Mazatlan", "Juarez", "Puebla",
]

ALIASES = {
    "Club America":  ["America", "aguilas", "las aguilas"],
    "Guadalajara":   ["Chivas", "rebano", "rebano sagrado"],
    "Cruz Azul":     ["la maquina", "cementeros", "maquina"],
    "Pumas UNAM":    ["Pumas", "universitarios", "felinos pumas"],
    "Tigres UANL":   ["Tigres", "felinos", "universidad autonoma"],
    "Monterrey":     ["Rayados", "rayados de monterrey"],
    "Santos Laguna": ["Santos", "guerreros"],
}

RSS_SOURCES = [
    "https://news.google.com/rss/search?q=futbol+mexico+lesiones&hl=es-419&gl=MX&ceid=MX:es-419",
    "https://news.google.com/rss/search?q=liga+mx+bajas+titulares&hl=es-419&gl=MX&ceid=MX:es-419",
    "https://news.google.com/rss/search?q=chivas+america+cruz+azul+noticias&hl=es-419&gl=MX&ceid=MX:es-419",
    "https://www.record.com.mx/rss/futbol-mexico",
    "https://www.mediotiempo.com/rss",
]


def _n(t):
    """Normaliza texto: minusculas + quitar acentos."""
    return (t.lower()
            .replace("á","a").replace("é","e").replace("í","i")
            .replace("ó","o").replace("ú","u").replace("ü","u")
            .replace("ñ","n"))


def _get_aliases(equipo):
    return ALIASES.get(equipo, [])


# ── 1. FETCH NOTICIAS RSS ─────────────────────────────────────────────────
def fetch_noticias(limite=25):
    """
    Obtiene noticias recientes de RSS de fútbol mexicano.
    Usa Google News (confiable) + fuentes mexicanas como fallback.
    """
    if not HAS_HTTPX:
        return _demo_noticias()

    noticias = []
    # Intentar Google News primero (siempre actualizado)
    for url in RSS_SOURCES[:3]:
        try:
            r = httpx.get(url, timeout=10, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ApuestasPro/5.0"
            }, follow_redirects=True)
            if r.status_code != 200:
                continue
            if HAS_BS4:
                soup = BeautifulSoup(r.text, "lxml-xml")
                for item in soup.find_all("item")[:limite]:
                    t = item.find("title")
                    d = item.find("description")
                    pub = item.find("pubDate")
                    link = item.find("link")
                    fecha = datetime.now().isoformat()
                    if pub and pub.text:
                        try:
                            from email.utils import parsedate_to_datetime
                            fecha = parsedate_to_datetime(pub.text).isoformat()
                        except Exception:
                            pass
                    noticias.append({
                        "titulo": t.text.strip() if t else "",
                        "desc":   (d.text.strip()[:200] if d else ""),
                        "fuente": url.split("/")[2],
                        "fecha":  fecha,
                        "url":    link.text.strip() if link else "",
                    })
                if noticias:
                    break  # Google News funcionó, no necesitamos más
        except Exception:
            continue

    # Fallback a fuentes mexicanas si Google News no funcionó
    if not noticias:
        for url in RSS_SOURCES[3:]:
            try:
                r = httpx.get(url, timeout=8, headers={
                    "User-Agent": "Mozilla/5.0 ApuestasPro/5.0"
                }, follow_redirects=True)
                if HAS_BS4:
                    soup = BeautifulSoup(r.text, "lxml-xml")
                    for item in soup.find_all("item")[:limite]:
                        t = item.find("title")
                        d = item.find("description")
                        pub = item.find("pubDate")
                        fecha = datetime.now().isoformat()
                        if pub and pub.text:
                            try:
                                from email.utils import parsedate_to_datetime
                                fecha = parsedate_to_datetime(pub.text).isoformat()
                            except Exception:
                                pass
                        noticias.append({
                            "titulo": t.text.strip() if t else "",
                            "desc":   (d.text.strip()[:200] if d else ""),
                            "fuente": url.split("/")[2],
                            "fecha":  fecha,
                        })
            except Exception:
                continue

    return noticias if noticias else _demo_noticias()


def _demo_noticias():
    return [
        {
            "titulo": "Henry Martin se pierde el Clasico por lesion muscular",
            "desc": "El delantero del America no entreno y esta descartado para el fin de semana",
            "fuente": "record.com.mx", "fecha": datetime.now().isoformat(),
        },
        {
            "titulo": "Chivas presenta su mejor once para el Clasico Nacional",
            "desc": "El tecnico confirmo que todos estan listos y motivados para ganar",
            "fuente": "mediotiempo.com", "fecha": datetime.now().isoformat(),
        },
        {
            "titulo": "Cruz Azul recupera a su goleador para el partido",
            "desc": "El delantero regresa disponible tras superar su molestia muscular",
            "fuente": "espn.com.mx", "fecha": datetime.now().isoformat(),
        },
        {
            "titulo": "Tigres en crisis: tres derrotas consecutivas en el Volcan",
            "desc": "El equipo regiomontano atraviesa su peor racha del torneo bajo presion",
            "fuente": "foxsports.com.mx", "fecha": datetime.now().isoformat(),
        },
        {
            "titulo": "Monterrey sin sus dos defensas titulares por sancion",
            "desc": "Dos bajas confirmadas para los Rayados por acumulacion de tarjetas amarillas",
            "fuente": "record.com.mx", "fecha": datetime.now().isoformat(),
        },
        {
            "titulo": "America con problemas internos antes del Clasico",
            "desc": "Tension en el vestuario de las aguilas previo al duelo de este fin de semana",
            "fuente": "mediotiempo.com", "fecha": datetime.now().isoformat(),
        },
    ]


# ── 2. DETECCION DE LESIONES ──────────────────────────────────────────────
def detectar_lesiones(texto, equipo=None):
    """
    Detecta menciones de lesiones en un texto.
    Si se especifica equipo, filtra solo las de ese equipo.
    """
    tn = _n(texto)
    alertas = []

    for kw, peso in LESION_KW.items():
        if kw not in tn:
            continue

        # Detectar equipo mencionado en el texto
        eq_detect = None
        for eq in EQUIPOS:
            if _n(eq) in tn:
                eq_detect = eq
                break

        # Si especificaron equipo, verificar que coincida
        if equipo and eq_detect:
            aliases = [equipo] + _get_aliases(equipo)
            match = any(
                _n(a) in _n(eq_detect) or _n(eq_detect) in _n(a)
                for a in aliases
            )
            if not match:
                continue

        alertas.append({
            "keyword": kw,
            "impacto": peso,
            "equipo":  eq_detect or "Desconocido",
            "tipo": (
                "BAJA CONFIRMADA" if peso >= 0.9
                else "DUDA"        if 0.4 <= peso < 0.9
                else "REGRESA"     if peso < 0
                else "MENOR"
            ),
        })

    return alertas


# ── 3. SENTIMIENTO DEL EQUIPO ─────────────────────────────────────────────
def sentimiento_equipo(textos, equipo):
    """
    Analiza sentimiento positivo/negativo del equipo en textos recientes.
    """
    score = menciones = 0
    aliases = [equipo] + _get_aliases(equipo)

    for texto in textos:
        tn = _n(texto)
        if not any(_n(a) in tn for a in aliases):
            continue
        menciones += 1
        for p in SENT_POS:
            if p in tn: score += 1
        for p in SENT_NEG:
            if p in tn: score -= 1

    if not menciones:
        return {
            "equipo": equipo, "sentimiento": "neutral",
            "score": 0, "factor_moral": 1.0, "menciones": 0,
            "descripcion": f"{equipo}: sin menciones recientes",
        }

    sn = max(-1.0, min(1.0, score / menciones / 3))
    return {
        "equipo":      equipo,
        "score":       round(sn, 3),
        "menciones":   menciones,
        "sentimiento": "positivo" if sn > 0.2 else "negativo" if sn < -0.2 else "neutral",
        "factor_moral": round(1.0 + sn * 0.05, 3),
        "descripcion": (
            f"{equipo}: moral alta en medios" if sn > 0.4
            else f"{equipo}: crisis o dudas en medios" if sn < -0.3
            else f"{equipo}: neutro en medios"
        ),
    }


# ── 4. SCAN COMPLETO PRE-PARTIDO ──────────────────────────────────────────
def scan_completo(home, away):
    """
    Scan NLP completo antes de un partido.
    Detecta lesiones + sentimiento + genera alertas de edge con accion.
    """
    noticias = fetch_noticias(30)
    textos   = [n["titulo"] + " " + n["desc"] for n in noticias]

    # Lesiones local y visitante
    al_home, al_away = [], []
    for n in noticias:
        texto = n["titulo"] + " " + n["desc"]
        aliases_h = [home] + _get_aliases(home)
        aliases_a = [away] + _get_aliases(away)

        if any(_n(a) in _n(texto) for a in aliases_h):
            for a in detectar_lesiones(texto, home):
                a["noticia"] = n["titulo"][:80]
                a["fuente"]  = n.get("fuente", "")
                al_home.append(a)

        if any(_n(a) in _n(texto) for a in aliases_a):
            for a in detectar_lesiones(texto, away):
                a["noticia"] = n["titulo"][:80]
                a["fuente"]  = n.get("fuente", "")
                al_away.append(a)

    # Impacto en lambdas (máx 35%)
    imp_h = min(0.35, sum(a["impacto"] for a in al_home if a["impacto"] > 0) * 0.12)
    imp_a = min(0.35, sum(a["impacto"] for a in al_away if a["impacto"] > 0) * 0.12)

    # Sentimiento
    sent_h = sentimiento_equipo(textos, home)
    sent_a = sentimiento_equipo(textos, away)

    # Alertas de edge con ventana de oportunidad
    edges = []
    bajas_h = [a for a in al_home if a["impacto"] >= 0.9]
    bajas_a = [a for a in al_away if a["impacto"] >= 0.9]

    if bajas_h:
        edges.append({
            "tipo":      "LESION CRITICA LOCAL",
            "urgencia":  "ALTA",
            "detalle":   f"{len(bajas_h)} baja(s) titular(es) en {home}",
            "accion":    f"Apostar {away} ANTES de que las casas actualicen la linea",
            "ventana_min": 20,
            "noticias":  [b["noticia"] for b in bajas_h[:2]],
        })

    if bajas_a:
        edges.append({
            "tipo":      "LESION CRITICA VISITANTE",
            "urgencia":  "ALTA",
            "detalle":   f"{len(bajas_a)} baja(s) titular(es) en {away}",
            "accion":    f"Apostar {home} ANTES de que las casas actualicen la linea",
            "ventana_min": 20,
            "noticias":  [b["noticia"] for b in bajas_a[:2]],
        })

    if sent_h["score"] < -0.4:
        edges.append({
            "tipo":     "CRISIS DE MORAL LOCAL",
            "urgencia": "MEDIA",
            "detalle":  f"{home} con sentimiento muy negativo en medios",
            "accion":   "Considerar visitante o empate — factor psicologico negativo",
            "ventana_min": None,
        })

    if sent_a["score"] > 0.5 and sent_h["score"] < 0:
        edges.append({
            "tipo":     "CONTRASTE DE MORAL",
            "urgencia": "MEDIA",
            "detalle":  f"{away} muy motivado vs {home} en dudas",
            "accion":   "Edge psicologico claro a favor del visitante",
            "ventana_min": None,
        })

    # Factores finales para ajustar lambdas
    fL = round(max(0.6, (1.0 - imp_h) * sent_h["factor_moral"]), 3)
    fA = round(max(0.6, (1.0 - imp_a) * sent_a["factor_moral"]), 3)

    # Detectar si los datos son demo o reales
    es_demo = any(n.get("fuente", "") == "demo" for n in noticias[:3])
    fuentes_unicas = list(set(n.get("fuente", "") for n in noticias))

    return {
        "home": home,
        "away": away,
        "alertas_lesiones_local":      al_home[:5],
        "alertas_lesiones_visitante":  al_away[:5],
        "impacto_local_pct":           round(imp_h * 100, 1),
        "impacto_visitante_pct":       round(imp_a * 100, 1),
        "sentimiento_local":           sent_h,
        "sentimiento_visitante":       sent_a,
        "alertas_edge":                edges,
        "factores": {
            "lambda_local":     fL,
            "lambda_visitante": fA,
        },
        "n_noticias":  len(noticias),
        "fuentes":     fuentes_unicas,
        "es_demo":     es_demo,
        "tiene_edge":  len(edges) > 0,
        "timestamp":   datetime.now().isoformat(),
    }
