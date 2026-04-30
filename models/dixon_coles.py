"""
Modelo Dixon-Coles para predicción de fútbol.
Referencia: Dixon & Coles (1997) "Modelling Association Football Scores
and Inefficiencies in the Football Betting Market"

Calcula:
- Fuerza ofensiva (ataque) de cada equipo
- Fuerza defensiva de cada equipo  
- Ventaja de local
- Probabilidades P(local gana), P(empate), P(visitante gana)
- Factor de corrección tau para marcadores bajos (0-0, 1-0, 0-1, 1-1)
"""
import math
from collections import defaultdict


def _tau(x, y, lam, mu, rho):
    """Factor de corrección Dixon-Coles para marcadores bajos."""
    if x == 0 and y == 0:
        return 1 - lam * mu * rho
    elif x == 0 and y == 1:
        return 1 + lam * rho
    elif x == 1 and y == 0:
        return 1 + mu * rho
    elif x == 1 and y == 1:
        return 1 - rho
    return 1.0


def _poisson_pmf(k, lam):
    """P(X=k) para distribución Poisson con media lam."""
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


class DixonColesModel:
    """
    Modelo Dixon-Coles entrenado sobre historial de partidos.
    
    Uso:
        model = DixonColesModel()
        model.fit(partidos)  # lista de {home, away, home_goals, away_goals}
        probs = model.predict("Chivas", "América")
    """

    def __init__(self, rho=-0.13):
        # rho: parámetro de correlación DC, típicamente entre -0.1 y -0.2
        self.rho = rho
        self.ataque   = defaultdict(lambda: 1.0)
        self.defensa  = defaultdict(lambda: 1.0)
        self.home_adv = 1.35  # ventaja de local promedio Liga MX
        self.avg_goals = 1.4  # goles esperados promedio
        self.equipos  = set()
        self.entrenado = False

    # ── ENTRENAMIENTO ──────────────────────────────────────────────────────
    def fit(self, partidos, iteraciones=50, decay=0.0065):
        """
        Estima parámetros por máxima verosimilitud iterativa.
        decay: factor de olvido temporal (partidos recientes pesan más)
        """
        if not partidos:
            return self

        self.equipos = set()
        for p in partidos:
            self.equipos.add(p["home"])
            self.equipos.add(p["away"])

        # Inicializar parámetros
        for eq in self.equipos:
            self.ataque[eq]  = 1.0
            self.defensa[eq] = 1.0

        n = len(partidos)

        for _ in range(iteraciones):
            # Actualizar ataque
            for equipo in self.equipos:
                numerador = sum(
                    p.get("weight", 1.0) * p["home_goals"]
                    for p in partidos if p["home"] == equipo
                ) + sum(
                    p.get("weight", 1.0) * p["away_goals"]
                    for p in partidos if p["away"] == equipo
                )
                denominador = sum(
                    p.get("weight", 1.0) * self.home_adv * self.defensa[p["away"]]
                    for p in partidos if p["home"] == equipo
                ) + sum(
                    p.get("weight", 1.0) * self.defensa[p["home"]]
                    for p in partidos if p["away"] == equipo
                )
                if denominador > 0:
                    self.ataque[equipo] = numerador / denominador

            # Normalizar ataque
            mean_atk = sum(self.ataque[e] for e in self.equipos) / len(self.equipos)
            if mean_atk > 0:
                for e in self.equipos:
                    self.ataque[e] /= mean_atk

            # Actualizar defensa
            for equipo in self.equipos:
                numerador = sum(
                    p.get("weight", 1.0) * p["away_goals"]
                    for p in partidos if p["home"] == equipo
                ) + sum(
                    p.get("weight", 1.0) * p["home_goals"]
                    for p in partidos if p["away"] == equipo
                )
                denominador = sum(
                    p.get("weight", 1.0) * self.ataque[p["away"]]
                    for p in partidos if p["home"] == equipo
                ) + sum(
                    p.get("weight", 1.0) * self.home_adv * self.ataque[p["home"]]
                    for p in partidos if p["away"] == equipo
                )
                if denominador > 0:
                    self.defensa[equipo] = numerador / denominador

            # Normalizar defensa
            mean_def = sum(self.defensa[e] for e in self.equipos) / len(self.equipos)
            if mean_def > 0:
                for e in self.equipos:
                    self.defensa[e] /= mean_def

        self.entrenado = True
        return self

    # ── PREDICCIÓN ─────────────────────────────────────────────────────────
    def predict(self, home, away, max_goles=8):
        """
        Retorna probabilidades P(local), P(empate), P(visitante)
        y lambda esperados usando corrección Dixon-Coles.
        """
        # Lambda esperados
        lam = self.home_adv * self.ataque.get(home, 1.0) * self.defensa.get(away, 1.0) * self.avg_goals
        mu  = self.ataque.get(away, 1.0) * self.defensa.get(home, 1.0) * self.avg_goals

        lam = max(0.1, min(lam, 6.0))
        mu  = max(0.1, min(mu,  6.0))

        # Matriz de probabilidades con corrección tau
        p_home = p_draw = p_away = 0.0
        score_probs = {}

        for i in range(max_goles + 1):
            for j in range(max_goles + 1):
                p = (_poisson_pmf(i, lam) * _poisson_pmf(j, mu) *
                     _tau(i, j, lam, mu, self.rho))
                score_probs[(i, j)] = p
                if i > j:
                    p_home += p
                elif i == j:
                    p_draw += p
                else:
                    p_away += p

        total = p_home + p_draw + p_away
        if total == 0:
            return {"local": 1/3, "empate": 1/3, "visitante": 1/3,
                    "lambda_local": lam, "lambda_visitante": mu}

        return {
            "local":      round(p_home / total, 4),
            "empate":     round(p_draw / total, 4),
            "visitante":  round(p_away / total, 4),
            "lambda_local":     round(lam, 3),
            "lambda_visitante": round(mu,  3),
            "cuota_justa_local":     round(total / p_home, 3) if p_home > 0 else 99,
            "cuota_justa_empate":    round(total / p_draw, 3) if p_draw > 0 else 99,
            "cuota_justa_visitante": round(total / p_away, 3) if p_away > 0 else 99,
            "goles_esperados_local":     round(lam, 2),
            "goles_esperados_visitante": round(mu,  2),
            "modelo": "Dixon-Coles",
        }

    def strength(self, equipo):
        """Retorna ataque y defensa normalizados de un equipo."""
        return {
            "equipo":  equipo,
            "ataque":  round(self.ataque.get(equipo, 1.0), 3),
            "defensa": round(self.defensa.get(equipo, 1.0), 3),
            "rating":  round(self.ataque.get(equipo, 1.0) / self.defensa.get(equipo, 1.0), 3),
        }

    def ranking(self):
        """Ranking de equipos por rating ofensivo/defensivo."""
        equipos = list(self.equipos)
        return sorted(
            [self.strength(e) for e in equipos],
            key=lambda x: x["rating"],
            reverse=True,
        )
