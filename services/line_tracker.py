"""
Line Movement Tracker - Sharp Money REAL.

Funciona con The Odds API que ya tenemos:
1. Guarda snapshots de odds cada 15 min
2. Detecta movimientos significativos (line movement)
3. Detecta steam moves (cambio rapido en multiples casas)
4. Detecta Reverse Line Movement (RLM)
5. Produce senales SHARP MONEY reales

NO es comparador de cuotas - es tracking de movimiento real.
"""
import json
import math
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

STEAM_THRESHOLD_PTS = 0.05
STEAM_MIN_BOOKS = 3
RLM_MOVE_THRESHOLD = 0.03

SHARP_BOOKS = {"pinnacle", "bookmaker", "cris", "circa", "betcris"}
SQUARE_BOOKS = {"draftkings", "fanduel", "betmgm", "bet365", "codere", "1xbet"}


def snapshot_odds(api_key=None):
    from services.deportes import get_odds_upcoming
    from database import db, _q, _USE_PG

    if not api_key:
        from services.deportes import get_any_odds_key
        api_key = get_any_odds_key()
    if not api_key:
        return {"saved": 0, "matches": 0, "errors": 1}

    raw = get_odds_upcoming(api_key, regions="us,uk,eu", markets="h2h")
    if not raw:
        return {"saved": 0, "matches": 0, "errors": 1}

    saved = 0
    errors = 0
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with db() as conn:
            for match in (raw if isinstance(raw, list) else []):
                try:
                    ht = match.get("home_team", "")
                    at = match.get("away_team", "")
                    sport = match.get("sport_key", "")
                    league = match.get("sport_title", "")
                    commence = match.get("commence_time", "")
                    bookmakers = match.get("bookmakers", [])

                    if not ht or not at or not bookmakers:
                        continue

                    for book in bookmakers:
                        casa = book.get("title", "").lower()
                        markets = book.get("markets", [])
                        if not markets:
                            continue
                        h2h = markets[0]
                        outcomes = h2h.get("outcomes", [])

                        for o in outcomes:
                            nombre = o.get("name", "")
                            precio = o.get("price", 0)
                            if not nombre or precio <= 1:
                                continue

                            ph = "%s" if _USE_PG else "?"
                            sql = _q(
                                "INSERT INTO odds_snapshots"
                                "(timestamp, home_team, away_team, sport_key, liga,"
                                " commence_time, bookmaker, selection, odds)"
                                f" VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph})"
                            )
                            conn.execute(sql, (
                                now, ht, at, sport, league,
                                commence, casa, nombre, precio
                            ))
                            saved += 1
                except Exception as e:
                    errors += 1
                    logger.debug("Error snapshot match: %s", e)
    except Exception as e:
        logger.error("Error en snapshot_odds: %s", e)
        return {"saved": 0, "matches": 0, "errors": 1}

    return {"saved": saved, "matches": len(raw if isinstance(raw, list) else []), "errors": errors}


def get_line_movements(hours_back=24, min_change_pct=3.0):
    from database import db, _fetchall, _USE_PG

    cutoff = (datetime.utcnow() - timedelta(hours=hours_back)).strftime("%Y-%m-%d %H:%M:%S")
    ph = "%s" if _USE_PG else "?"

    try:
        with db() as conn:
            sql = _q(
                "SELECT home_team, away_team, sport_key, liga, bookmaker, selection,"
                " odds, timestamp FROM odds_snapshots"
                f" WHERE timestamp > {ph}"
                " ORDER BY home_team, away_team, bookmaker, selection, timestamp"
            )
            rows = _fetchall(conn, sql, (cutoff,))
    except Exception as e:
        logger.error("Error get_line_movements: %s", e)
        return []

    if not rows:
        return []

    groups = {}
    for r in rows:
        key = (r["home_team"], r["away_team"], r["bookmaker"], r["selection"])
        if key not in groups:
            groups[key] = []
        groups[key].append(r)

    movements = []
    for key, snapshots in groups.items():
        if len(snapshots) < 2:
            continue
        first = snapshots[0]
        last = snapshots[-1]
        old_odds = first["odds"]
        new_odds = last["odds"]
        if old_odds <= 0:
            continue
        change_pct = ((new_odds - old_odds) / old_odds) * 100
        if abs(change_pct) >= min_change_pct:
            movements.append({
                "partido": f"{key[0]} vs {key[1]}",
                "home_team": key[0], "away_team": key[1],
                "sport": last.get("sport_key", ""),
                "liga": last.get("liga", ""),
                "casa": key[2], "seleccion": key[3],
                "odds_inicial": round(old_odds, 2),
                "odds_actual": round(new_odds, 2),
                "cambio_pct": round(change_pct, 2),
                "direccion": "SUBIO" if change_pct > 0 else "BAJO",
                "timestamp": last["timestamp"],
            })

    movements.sort(key=lambda x: abs(x["cambio_pct"]), reverse=True)
    return movements


def detect_steam_moves(hours_back=6, min_books=None):
    from database import db, _fetchall, _USE_PG

    if min_books is None:
        min_books = STEAM_MIN_BOOKS

    cutoff = (datetime.utcnow() - timedelta(hours=hours_back)).strftime("%Y-%m-%d %H:%M:%S")
    ph = "%s" if _USE_PG else "?"

    try:
        with db() as conn:
            sql = _q(
                "SELECT home_team, away_team, sport_key, liga, bookmaker, selection,"
                " odds, timestamp FROM odds_snapshots"
                f" WHERE timestamp > {ph}"
                " ORDER BY home_team, away_team, selection, bookmaker, timestamp"
            )
            rows = _fetchall(conn, sql, (cutoff,))
    except Exception as e:
        logger.error("Error detect_steam_moves: %s", e)
        return []

    if not rows:
        return []

    groups = {}
    for r in rows:
        key = (r["home_team"], r["away_team"], r["seleccion"])
        if key not in groups:
            groups[key] = {}
        casa = r["bookmaker"]
        if casa not in groups[key]:
            groups[key][casa] = []
        groups[key][casa].append(r)

    steam_moves = []
    for key, casas in groups.items():
        if len(casas) < min_books:
            continue

        cambios = []
        for casa, snapshots in casas.items():
            if len(snapshots) < 2:
                continue
            first = snapshots[0]
            last = snapshots[-1]
            old_odds = first["odds"]
            new_odds = last["odds"]
            if old_odds <= 0:
                continue
            change_pct = ((new_odds - old_odds) / old_odds) * 100
            cambios.append({
                "casa": casa, "old": old_odds, "new": new_odds,
                "change_pct": change_pct,
                "is_sharp": casa.lower() in SHARP_BOOKS,
            })

        if len(cambios) < min_books:
            continue

        subieron = [c for c in cambios if c["change_pct"] > STEAM_THRESHOLD_PTS * 100]
        bajaron = [c for c in cambios if c["change_pct"] < -STEAM_THRESHOLD_PTS * 100]
        majority = max(len(subieron), len(bajaron))

        if majority >= min_books:
            direction = "BAJANDO" if len(bajaron) > len(subieron) else "SUBIENDO"
            sharps = [c["casa"] for c in cambios if c["is_sharp"]]
            avg_change = sum(abs(c["change_pct"]) for c in cambios) / len(cambios)
            conf = _steam_confidence(cambios)

            steam_moves.append({
                "partido": f"{key[0]} vs {key[1]}",
                "home_team": key[0], "away_team": key[1],
                "seleccion": key[2], "direccion": direction,
                "n_casas": len(cambios), "cambios": cambios,
                "cambio_promedio_pct": round(avg_change, 2),
                "sharp_books": sharps, "confianza": conf,
            })

    steam_moves.sort(key=lambda x: x["confianza"], reverse=True)
    return steam_moves


def _steam_confidence(cambios):
    score = 0
    score += min(len(cambios) * 5, 25)
    n_sharps = sum(1 for c in cambios if c["is_sharp"])
    score += min(n_sharps * 10, 30)
    avg_change = sum(abs(c["change_pct"]) for c in cambios) / len(cambios)
    if avg_change > 10:
        score += 25
    elif avg_change > 5:
        score += 15
    elif avg_change > 3:
        score += 10
    changes = [abs(c["change_pct"]) for c in cambios]
    if changes:
        avg = sum(changes) / len(changes)
        std = (sum((x - avg) ** 2 for x in changes) / len(changes)) ** 0.5
        if std < 2:
            score += 20
        elif std < 5:
            score += 10
    return min(score, 100)


def detect_rlm(hours_back=24):
    from database import db, _fetchall, _USE_PG

    cutoff = (datetime.utcnow() - timedelta(hours=hours_back)).strftime("%Y-%m-%d %H:%M:%S")
    ph = "%s" if _USE_PG else "?"

    try:
        with db() as conn:
            sql = _q(
                "SELECT home_team, away_team, sport_key, liga, bookmaker, selection,"
                " odds, timestamp FROM odds_snapshots"
                f" WHERE timestamp > {ph}"
                " ORDER BY home_team, away_team, selection, bookmaker, timestamp"
            )
            rows = _fetchall(conn, sql, (cutoff,))
    except Exception as e:
        logger.error("Error detect_rlm: %s", e)
        return []

    if not rows:
        return []

    matches = {}
    for r in rows:
        key = (r["home_team"], r["away_team"])
        if key not in matches:
            matches[key] = []
        matches[key].append(r)

    rlm_signals = []
    for key, snapshots in matches.items():
        if len(snapshots) < 4:
            continue

        by_selection = {}
        for r in snapshots:
            sel = r["seleccion"]
            casa = r["bookmaker"]
            if sel not in by_selection:
                by_selection[sel] = {}
            if casa not in by_selection[sel]:
                by_selection[sel][casa] = []
            by_selection[sel][casa].append(r)

        for sel, casas in by_selection.items():
            all_firsts = []
            all_lasts = []
            for casa, snaps in casas.items():
                if len(snaps) >= 2:
                    all_firsts.append(snaps[0]["odds"])
                    all_lasts.append(snaps[-1]["odds"])

            if not all_firsts:
                continue

            avg_first = sum(all_firsts) / len(all_firsts)
            avg_last = sum(all_lasts) / len(all_lasts)
            if avg_first <= 0:
                continue

            line_change_pct = ((avg_last - avg_first) / avg_first) * 100

            if abs(line_change_pct) >= RLM_MOVE_THRESHOLD * 100:
                opposite = _opposite_selection(sel, key)
                rlm_signals.append({
                    "partido": f"{key[0]} vs {key[1]}",
                    "home_team": key[0], "away_team": key[1],
                    "liga": snapshots[0].get("liga", ""),
                    "seleccion_publico": sel,
                    "seleccion_sharp": opposite,
                    "line_change_pct": round(line_change_pct, 2),
                    "tipo": "ODDS_SUBIERON" if line_change_pct > 0 else "ODDS_BAJARON",
                    "interpretacion": (
                        f"El publico apuesta a {sel}, pero la linea se movio en su contra. "
                        f"Dinero sharp probablemente en {opposite}."
                    ),
                    "confianza": _rlm_confidence(line_change_pct),
                })

    rlm_signals.sort(key=lambda x: x["confianza"], reverse=True)
    return rlm_signals


def _opposite_selection(sel, teams):
    home, away = teams
    if sel == home:
        return away
    elif sel == away:
        return home
    return "Draw/Empate"


def _rlm_confidence(change_pct):
    abs_change = abs(change_pct)
    if abs_change > 10:
        return 85
    elif abs_change > 7:
        return 70
    elif abs_change > 5:
        return 55
    elif abs_change > 3:
        return 40
    return 25


def get_sharp_signals(hours_back=24):
    steam = detect_steam_moves(hours_back=6)
    rlm = detect_rlm(hours_back=hours_back)
    movements = get_line_movements(hours_back=hours_back, min_change_pct=3.0)

    sharp_recs = []

    for s in steam:
        if s["confianza"] >= 50:
            rec = {
                "partido": s["partido"],
                "tipo": "STEAM_MOVE",
                "seleccion": s["seleccion"],
                "direccion": s["direccion"],
                "n_casas": s["n_casas"],
                "sharp_books": s["sharp_books"],
                "cambio_promedio": s["cambio_promedio_pct"],
                "confianza": s["confianza"],
                "accion": f"STEAM: {s['seleccion']} {s['direccion']} en {s['n_casas']} casas",
            }
            sharp_recs.append(rec)

    for r in rlm:
        if r["confianza"] >= 40:
            rec = {
                "partido": r["partido"],
                "tipo": "RLM",
                "seleccion": r["seleccion_sharp"],
                "seleccion_publico": r["seleccion_publico"],
                "line_change": r["line_change_pct"],
                "interpretacion": r["interpretacion"],
                "confianza": r["confianza"],
                "accion": f"RLM: Apostar a {r['seleccion_sharp']} (publico en {r['seleccion_publico']})",
            }
            sharp_recs.append(rec)

    sharp_recs.sort(key=lambda x: x["confianza"], reverse=True)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "hours_back": hours_back,
        "steam_moves": len(steam),
        "rlm_signals": len(rlm),
        "line_movements": len(movements),
        "sharp_recommendations": sharp_recs,
        "total_signals": len(sharp_recs),
    }


def get_tracker_stats():
    from database import db, _fetchall, _row_to_dict, _USE_PG

    ph = "%s" if _USE_PG else "?"
    try:
        with db() as conn:
            sql = _q(f"SELECT COUNT(*) as total, MIN(timestamp) as oldest, MAX(timestamp) as newest FROM odds_snapshots")
            stats = _row_to_dict(conn.execute(sql).fetchone()) if not _USE_PG else None
            if _USE_PG:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) as total, MIN(timestamp) as oldest, MAX(timestamp) as newest FROM odds_snapshots")
                row = cur.fetchone()
                stats = {"total": row[0], "oldest": str(row[1]) if row[1] else None, "newest": str(row[2]) if row[2] else None}
                cur.close()

            sql2 = _q(f"SELECT COUNT(DISTINCT home_team || away_team) as matches FROM odds_snapshots WHERE timestamp > {ph}")
            cutoff = (datetime.utcnow() - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
            if _USE_PG:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(DISTINCT home_team || away_team) as matches FROM odds_snapshots WHERE timestamp > %s", (cutoff,))
                row2 = cur.fetchone()
                matches_24h = row2[0] if row2 else 0
                cur.close()
            else:
                matches_24h_row = conn.execute(sql2, (cutoff,)).fetchone()
                matches_24h = matches_24h_row[0] if matches_24h_row else 0

            return {
                "total_snapshots": stats["total"] if stats else 0,
                "oldest": stats["oldest"] if stats else None,
                "newest": stats["newest"] if stats else None,
                "matches_tracked_24h": matches_24h,
            }
    except Exception as e:
        logger.error("Error get_tracker_stats: %s", e)
        return {"total_snapshots": 0, "matches_tracked_24h": 0}
