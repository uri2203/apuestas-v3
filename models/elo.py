"""
Sistema ELO para fútbol — estilo FiveThirtyEight.
Referencia: https://fivethirtyeight.com/methodology/how-our-club-soccer-predictions-work/

Características:
- K-factor adaptativo según importancia del partido
- Ajuste por margen de victoria (mov_multiplier)
- Ajuste por ventaja de local (+100 ELO por default)
- Decay al inicio de temporada (regresión a la media)
- Conversión ELO → probabilidad win/draw/lose
"""
import math
from collections import defaultdict


# ELO inicial para equipos nuevos
ELO_BASE = 1500
# Ventaja de local en puntos ELO
HOME_ADV = 65
# K-factor base
K_BASE = 20


def _expected(elo_a, elo_b):
    """Probabilidad esperada de victoria para equipo A."""
    return 1.0 / (1.0 + 10 ** ((elo_b - elo_a) / 400.0))


def _mov_multiplier(goles_a, goles_b, elo_diff):
    """
    Multiplicador por margen de victoria.
    Partidos ganados por más goles actualizan ELO más agresivamente.
    Fórmula FiveThirtyEight.
    """
    margen = abs(goles_a - goles_b)
    if margen == 0:
        return 1.0
    mult = math.log(margen + 1) * (2.2 / (elo_diff * 0.001 + 2.2))
    return max(0.5, min(mult, 3.0))


class ELOModel:
    """
    Modelo ELO dinámico para equipos de fútbol.
    
    Uso:
        elo = ELOModel()
        elo.update(partidos)  # lista de {home, away, home_goals, away_goals}
        probs = elo.predict("Chivas", "América")
        rating = elo.rating("Chivas")
    """

    def __init__(self, k=K_BASE, home_adv=HOME_ADV):
        self.k        = k
        self.home_adv = home_adv
        self.ratings  = defaultdict(lambda: ELO_BASE)
        self.history  = defaultdict(list)  # historial de ratings por equipo
        self.partidos_procesados = 0

    # ── ACTUALIZACIÓN ──────────────────────────────────────────────────────
    def update(self, partidos):
        """Procesa lista de partidos y actualiza ratings ELO."""
        for p in partidos:
            home   = p["home"]
            away   = p["away"]
            gh     = p["home_goals"]
            ga     = p["away_goals"]

            elo_h  = self.ratings[home] + self.home_adv
            elo_a  = self.ratings[away]

            exp_h  = _expected(elo_h, elo_a)
            exp_a  = 1.0 - exp_h

            # Resultado real: 1=victoria, 0.5=empate, 0=derrota
            if gh > ga:
                s_h, s_a = 1.0, 0.0
            elif gh == ga:
                s_h, s_a = 0.5, 0.5
            else:
                s_h, s_a = 0.0, 1.0

            elo_diff = abs(self.ratings[home] - self.ratings[away])
            mov = _mov_multiplier(gh, ga, elo_diff)

            delta_h = self.k * mov * (s_h - exp_h)
            delta_a = self.k * mov * (s_a - exp_a)

            self.ratings[home] = round(self.ratings[home] + delta_h, 1)
            self.ratings[away] = round(self.ratings[away] + delta_a, 1)

            self.history[home].append(self.ratings[home])
            self.history[away].append(self.ratings[away])
            self.partidos_procesados += 1

        return self

    def season_decay(self, factor=0.33):
        """
        Regresión a la media al inicio de temporada.
        Reduce diferencias extremas. FiveThirtyEight usa factor ~0.33.
        """
        for equipo in self.ratings:
            self.ratings[equipo] = round(
                self.ratings[equipo] * (1 - factor) + ELO_BASE * factor, 1
            )
        return self

    # ── PREDICCIÓN ─────────────────────────────────────────────────────────
    def predict(self, home, away):
        """
        Convierte diferencia ELO a probabilidades.
        Usa distribución logística calibrada para fútbol
        (más empates que otros deportes).
        """
        elo_h = self.ratings[home] + self.home_adv
        elo_a = self.ratings[away]
        diff  = elo_h - elo_a

        # Prob. de no-derrota para local (win + draw)
        p_win_or_draw = _expected(elo_h, elo_a)

        # Prob. de no-derrota para visitante
        p_away_or_draw = _expected(elo_a, elo_h)

        # Prob. de victoria local
        p_home = max(0.05, p_win_or_draw - 0.1)

        # Prob. de victoria visitante  
        p_away = max(0.05, p_away_or_draw - 0.1)

        # Prob. de empate (residuo)
        p_draw = max(0.05, 1.0 - p_home - p_away)

        # Renormalizar
        total = p_home + p_draw + p_away
        p_home /= total
        p_draw /= total
        p_away /= total

        return {
            "local":     round(p_home, 4),
            "empate":    round(p_draw, 4),
            "visitante": round(p_away, 4),
            "elo_local":     round(self.ratings[home], 0),
            "elo_visitante": round(self.ratings[away], 0),
            "elo_diff":      round(diff, 0),
            "cuota_justa_local":     round(1 / p_home, 3),
            "cuota_justa_empate":    round(1 / p_draw, 3),
            "cuota_justa_visitante": round(1 / p_away, 3),
            "modelo": "ELO",
        }

    def rating(self, equipo):
        """Rating ELO actual de un equipo."""
        return round(self.ratings.get(equipo, ELO_BASE), 1)

    def ranking(self):
        """Ranking completo de equipos por ELO."""
        return sorted(
            [{"equipo": e, "elo": round(r, 0)} for e, r in self.ratings.items()],
            key=lambda x: x["elo"],
            reverse=True,
        )

    def forma_reciente(self, equipo, n=5):
        """Últimos n ratings del equipo (tendencia)."""
        hist = self.history.get(equipo, [])
        return hist[-n:] if len(hist) >= n else hist

    # ── PREDICCIÓN COMBINADA ───────────────────────────────────────────────
    def predict_with_form(self, home, away, form_weight=0.2):
        """
        Predicción ELO ajustada por forma reciente.
        form_weight: cuánto pesa la forma vs ELO base.
        """
        base = self.predict(home, away)

        # Calcular tendencia reciente
        hist_h = self.forma_reciente(home)
        hist_a = self.forma_reciente(away)

        if len(hist_h) >= 3 and len(hist_a) >= 3:
            trend_h = hist_h[-1] - hist_h[-3]   # delta últimos 3 partidos
            trend_a = hist_a[-1] - hist_a[-3]
            adj = (trend_h - trend_a) / 400.0 * form_weight
            p_home = max(0.05, min(0.9, base["local"] + adj))
            p_away = max(0.05, min(0.9, base["visitante"] - adj))
            p_draw = max(0.05, 1.0 - p_home - p_away)
            total  = p_home + p_draw + p_away
            base.update({
                "local":     round(p_home / total, 4),
                "empate":    round(p_draw / total, 4),
                "visitante": round(p_away / total, 4),
                "ajuste_forma": round(adj, 4),
                "modelo": "ELO + Forma",
            })

        return base
