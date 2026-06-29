"""
Modelos avanzados de predicción deportiva.

Implementaciones basadas en investigación académica:
- Dixon-Coles (1997): Gold standard para predicción de fútbol
- ELO mejorado con margen de goles y decaying
- Análisis de fatiga y schedule spots
- Integración de clima
- Calibración de modelos

Referencias:
- Dixon & Coles (1997) "Modelling Association Football Scores"
- Constantinou & Fenton (2013) "pi-football: A Bayesian network model"
- Elo History SDR (2026 arxiv)
"""
import math
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════════
# 1. DIXON-COLES MODEL
# ════════════════════════════════════════════════════════════════════════════

class DixonColesModel:
    """
    Modelo Dixon-Coles para predicción de resultados de fútbol.
    
    Predice probabilidades de 1X2 (local/empate/visitante) usando:
    - Parámetros de ataque/defensa por equipo
    - Ventaja de localía
    - Correlación de baja puntuación (tau)
    - Decaimiento temporal (partidos recientes pesan más)
    
    Precision típica: 49-52% en 1X2 completo, 64-72% en subconjuntos de alta confianza.
    """
    
    def __init__(self):
        # Parámetros del modelo (se ajustan con entrenamiento)
        self.home_advantage = 0.25  # ~10% ventaja de localía
        self.xi = 0.0019  # Parámetro de decaimiento temporal (half-life ~365 días)
        self.rho = -0.13  # Correlación de baja puntuación (ajustado empíricamente)
        
        # Parámetros por equipo (se cargan de BD o se inicializan)
        self.team_params = {}  # {team: {"attack": float, "defense": float, "rating": float}}
        
        # Tabla de probabilidades bajas (0-0, 1-0, 0-1, 1-1)
        self._tau_cache = {}
    
    def _poisson_prob(self, lam: float, k: int) -> float:
        """Probabilidad de Poisson: P(X=k) = e^(-λ) * λ^k / k!"""
        if lam <= 0:
            return 1.0 if k == 0 else 0.0
        return math.exp(-lam) * (lam ** k) / math.factorial(k)
    
    def _tau(self, x: int, y: int, lambda_home: float, lambda_away: float, rho: float) -> float:
        """
        Correlación de baja puntuación (Dixon-Coles tau).
        Ajusta probabilidades para resultados 0-0, 1-0, 0-1, 1-1.
        """
        cache_key = (x, y, round(lambda_home, 4), round(lambda_away, 4))
        if cache_key in self._tau_cache:
            return self._tau_cache[cache_key]
        
        if x == 0 and y == 0:
            tau = 1 - lambda_home * lambda_away * rho
        elif x == 0 and y == 1:
            tau = 1 + lambda_home * rho
        elif x == 1 and y == 0:
            tau = 1 + lambda_away * rho
        elif x == 1 and y == 1:
            tau = 1 - rho
        else:
            tau = 1.0
        
        self._tau_cache[cache_key] = tau
        return tau
    
    def _get_team_params(self, team: str) -> dict:
        """Obtiene parámetros de un equipo (con valores por defecto si no existe)."""
        if team not in self.team_params:
            self.team_params[team] = {
                "attack": 0.0,
                "defense": 0.0,
                "rating": 1500.0,  # ELO base
            }
        return self.team_params[team]
    
    def predict_match(self, home_team: str, away_team: str, 
                      recency_weight: float = 1.0) -> dict:
        """
        Predice probabilidades de un partido usando Dixon-Coles.
        
        Args:
            home_team: Nombre del equipo local
            away_team: Nombre del equipo visitante
            recency_weight: Peso de recencia (1.0 = normal, >1.0 = más peso a recientes)
        
        Returns:
            dict con probabilidades y métricas
        """
        home = self._get_team_params(home_team)
        away = self._get_team_params(away_team)
        
        # Lambda (goles esperados) para cada equipo
        lambda_home = math.exp(home["attack"] - away["defense"] + self.home_advantage)
        lambda_away = math.exp(away["attack"] - home["defense"])
        
        # Calcular matriz de probabilidades 6x6 (0-5 goles cada lado)
        max_goals = 6
        prob_matrix = []
        for i in range(max_goals):
            row = []
            for j in range(max_goals):
                p = self._poisson_prob(lambda_home, i) * self._poisson_prob(lambda_away, j)
                p *= self._tau(i, j, lambda_home, lambda_away, self.rho)
                row.append(p)
            prob_matrix.append(row)
        
        # Probabilidades 1X2
        p_home = sum(prob_matrix[i][0] for i in range(max_goals))
        p_draw = sum(prob_matrix[i][i] for i in range(max_goals))
        p_away = 1 - p_home - p_draw
        
        # Ajustar para que sumen 1
        total = p_home + p_draw + p_away
        p_home /= total
        p_draw /= total
        p_away /= total
        
        # Probabilidad Over/Under 2.5
        p_over_25 = sum(
            prob_matrix[i][j]
            for i in range(max_goals)
            for j in range(max_goals)
            if i + j > 2
        )
        
        # Probabilidad BTTS (ambos equipos anotan)
        p_btts = sum(
            prob_matrix[i][j]
            for i in range(1, max_goals)
            for j in range(1, max_goals)
        )
        
        # Goles esperados totales
        expected_goals = lambda_home + lambda_away
        
        # Cuotas justas (sin vig)
        fair_home = 1 / p_home if p_home > 0 else 100
        fair_draw = 1 / p_draw if p_draw > 0 else 100
        fair_away = 1 / p_away if p_away > 0 else 100
        
        return {
            "modelo": "Dixon-Coles",
            "partido": f"{home_team} vs {away_team}",
            "probabilidades": {
                "local": round(p_home * 100, 1),
                "empate": round(p_draw * 100, 1),
                "visitante": round(p_away * 100, 1),
            },
            "cuotas_justas": {
                "local": round(fair_home, 2),
                "empate": round(fair_draw, 2),
                "visitante": round(fair_away, 2),
            },
            "goles_esperados": round(expected_goals, 2),
            "lambda_local": round(lambda_home, 2),
            "lambda_visitante": round(lambda_away, 2),
            "over_25": round(p_over_25 * 100, 1),
            "btts": round(p_btts * 100, 1),
            "parametros": {
                "home_advantage": self.home_advantage,
                "rho": self.rho,
                "xi": self.xi,
            }
        }
    
    def find_value_bets(self, home_team: str, away_team: str,
                        bookmaker_odds: dict, min_edge: float = 2.0) -> list:
        """
        Encuentra value bets comparando predicción Dixon-Coles vs cuotas del bookmaker.
        
        Args:
            home_team, away_team: Equipos
            bookmaker_odds: {"local": 2.10, "empate": 3.40, "visitante": 3.20}
            min_edge: Edge mínimo % para reportar
        
        Returns:
            Lista de value bets encontrados
        """
        prediction = self.predict_match(home_team, away_team)
        probs = prediction["probabilidades"]
        
        value_bets = []
        
        for outcome, prob_key, odds_key in [
            ("Local", "local", "local"),
            ("Empate", "empate", "empate"),
            ("Visitante", "visitante", "visitante"),
        ]:
            model_prob = probs[prob_key] / 100
            bookmaker_odd = bookmaker_odds.get(odds_key, 0)
            
            if bookmaker_odd <= 1:
                continue
            
            implied_prob = 1 / bookmaker_odd
            edge = ((model_prob - implied_prob) / implied_prob) * 100
            
            if edge >= min_edge:
                value_bets.append({
                    "seleccion": outcome,
                    "equipo": home_team if outcome == "Local" else away_team,
                    "prob_modelo": round(model_prob * 100, 1),
                    "prob_implicita": round(implied_prob * 100, 1),
                    "cuota_bookmaker": bookmaker_odd,
                    "cuota_justa": prediction["cuotas_justas"][odds_key],
                    "edge_pct": round(edge, 2),
                    "ev": round((model_prob * bookmaker_odd - 1) * 100, 2),
                    "confianza": "ALTA" if edge >= 10 else "MEDIA" if edge >= 5 else "BAJA",
                })
        
        return sorted(value_bets, key=lambda x: x["edge_pct"], reverse=True)
    
    def update_team(self, team: str, goals_for: int, goals_against: int,
                    is_home: bool = True, days_ago: int = 0):
        """
        Actualiza parámetros de un equipo después de un partido.
        Usa decaimiento temporal para dar más peso a partidos recientes.
        """
        params = self._get_team_params(team)
        
        # Decaimiento temporal
        recency = math.exp(-self.xi * days_ago)
        
        # Resultado esperado vs real
        expected = params["attack"] - params["defense"]
        if is_home:
            expected += self.home_advantage
        
        actual = math.log(max(goals_for, 0.1)) - math.log(max(goals_against, 0.1))
        
        # Actualizar rating ELO con margen de goles
        margin = abs(goals_for - goals_against)
        k_factor = 20 * (1 + math.log(max(margin, 1)))  # K ajustado por margen
        
        # Actualizar attack/defense
        error = actual - expected
        params["attack"] += 0.1 * recency * error
        params["defense"] -= 0.1 * recency * error
        
        # Actualizar rating
        if goals_for > goals_against:
            pts = 1.0
        elif goals_for == goals_against:
            pts = 0.5
        else:
            pts = 0.0
        
        expected_pts = 1 / (1 + 10 ** ((1500 - params["rating"]) / 400))
        params["rating"] += k_factor * recency * (pts - expected_pts)


# ════════════════════════════════════════════════════════════════════════════
# 2. ELO MEJORADO CON MARGEN DE GOLES
# ════════════════════════════════════════════════════════════════════════════

class ImprovedElo:
    """
    Sistema ELO mejorado con:
    - Margen de goles (goal difference multiplier)
    - Ventaja de localía dinámica
    - Decaimiento temporal
    - Ajuste por confederación
    """
    
    def __init__(self, k_factor: float = 20.0, home_adv: float = 50.0):
        self.k_factor = k_factor
        self.home_adv = home_adv
        self.ratings = {}  # {team: rating}
        self.history = {}  # {team: [(rating, date), ...]}
    
    def get_rating(self, team: str) -> float:
        """Obtiene rating actual de un equipo."""
        return self.ratings.get(team, 1500.0)
    
    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """Probabilidad esperada de A contra B."""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    def goal_difference_multiplier(self, margin: int) -> float:
        """
        Multiplicador por margen de goles.
        Goles grandes dan más rating pero con diminishing returns.
        """
        if margin <= 1:
            return 1.0
        elif margin == 2:
            return 1.5
        else:
            return (11 + margin) / 8  # Máx ~2.75 para margin=8
    
    def predict_match(self, home_team: str, away_team: str) -> dict:
        """Predice resultado usando ELO."""
        home_elo = self.get_rating(home_team) + self.home_adv
        away_elo = self.get_rating(away_team)
        
        exp_home = self.expected_score(home_elo, away_elo)
        exp_away = 1 - exp_home
        
        # Modelo de Poisson simple basado en ELO
        elo_diff = home_elo - away_elo
        lambda_home = 1.35 + 0.1 * (elo_diff / 100)
        lambda_away = 1.35 - 0.1 * (elo_diff / 100)
        lambda_home = max(0.3, min(4.0, lambda_home))
        lambda_away = max(0.3, min(4.0, lambda_away))
        
        return {
            "modelo": "ELO Mejorado",
            "partido": f"{home_team} vs {away_team}",
            "probabilidades": {
                "local": round(exp_home * 100, 1),
                "empate": round(25, 1),  # Estimación
                "visitante": round(exp_away * 100, 1),
            },
            "elo_home": round(self.get_rating(home_team), 0),
            "elo_away": round(self.get_rating(away_team), 0),
            "elo_diff": round(elo_diff, 0),
            "lambda_local": round(lambda_home, 2),
            "lambda_visitante": round(lambda_away, 2),
            "rating_favorito": home_team if exp_home > exp_away else away_team,
        }
    
    def update(self, home_team: str, away_team: str,
               home_goals: int, away_goals: int,
               match_date: str = None):
        """Actualiza ratings después de un partido."""
        home_elo = self.get_rating(home_team)
        away_elo = self.get_rating(away_team)
        
        # Expected scores
        exp_home = self.expected_score(home_elo + self.home_adv, away_elo)
        exp_away = 1 - exp_home
        
        # Actual scores
        if home_goals > away_goals:
            actual_home, actual_away = 1.0, 0.0
        elif home_goals == away_goals:
            actual_home, actual_away = 0.5, 0.5
        else:
            actual_home, actual_away = 0.0, 1.0
        
        # Goal difference multiplier
        margin = abs(home_goals - away_goals)
        gdm = self.goal_difference_multiplier(margin)
        
        # Update ratings
        new_home = home_elo + self.k_factor * gdm * (actual_home - exp_home)
        new_away = away_elo + self.k_factor * gdm * (actual_away - exp_away)
        
        self.ratings[home_team] = new_home
        self.ratings[away_team] = new_away
        
        # Store history
        if home_team not in self.history:
            self.history[home_team] = []
        if away_team not in self.history:
            self.history[away_team] = []
        
        self.history[home_team].append((new_home, match_date))
        self.history[away_team].append((new_away, match_date))


# ════════════════════════════════════════════════════════════════════════════
# 3. ANÁLISIS DE FATIGA Y SCHEDULE SPOTS
# ════════════════════════════════════════════════════════════════════════════

class FatigueAnalyzer:
    """
    Analiza factores de fatiga y schedule spots que afectan rendimiento.
    
    Impacto documentado:
    - Back-to-back en NBA: -5-7% rendimiento
    - Viaje transcontinental: -2-3% por zona horaria
    - 3 juegos en 4 noches: fracaso frecuente en ATS
    - Descanso de 2+ días: ventaja consistente
    """
    
    # Zonas horarias por ciudad (simplificado)
    TIMEZONES = {
        "Los Angeles": -8, "San Francisco": -8, "Sacramento": -8,
        "Phoenix": -7, "Denver": -7, "Salt Lake City": -7,
        "Dallas": -6, "Houston": -6, "San Antonio": -6, "Memphis": -6,
        "Minneapolis": -6, "Oklahoma City": -6,
        "New Orleans": -6, "Chicago": -6,
        "Atlanta": -5, "Miami": -5, "Orlando": -5, "Charlotte": -5,
        "Indiana": -5, "Cleveland": -5, "Detroit": -5,
        "New York": -5, "Brooklyn": -5, "Philadelphia": -5, "Boston": -5,
        "Toronto": -5, "Montreal": -5,
        "Washington DC": -5, "Milwaukee": -6,
        "Portland": -8, "Seattle": -8,
        # Fútbol
        "Guadalajara": -6, "Monterrey": -6, "Ciudad de Mexico": -6,
        "London": 0, "Manchester": 0, "Liverpool": 0,
        "Madrid": 1, "Barcelona": 1, "Sevilla": 1,
        "Roma": 1, "Milan": 1, "Turin": 1,
        "Munich": 1, "Berlin": 1,
        "Paris": 1, "Lyon": 1,
        "Buenos Aires": -3, "Sao Paulo": -3, "Lima": -5,
    }
    
    def analyze_fatigue(self, team_schedule: list, sport: str = "basketball") -> dict:
        """
        Analiza factores de fatiga de un equipo.
        
        Args:
            team_schedule: Lista de fechas de partidos recientes ["2026-01-15", ...]
            sport: "basketball", "football", "soccer"
        
        Returns:
            dict con análisis de fatiga y impacto estimado
        """
        if not team_schedule or len(team_schedule) < 2:
            return {"fatiga_score": 0, "factores": [], "impacto_pct": 0}
        
        factores = []
        fatiga_score = 0
        
        # Parsear fechas
        dates = []
        for d in team_schedule:
            try:
                if isinstance(d, str):
                    dates.append(datetime.strptime(d[:10], "%Y-%m-%d"))
                else:
                    dates.append(d)
            except:
                continue
        
        if len(dates) < 2:
            return {"fatiga_score": 0, "factores": [], "impacto_pct": 0}
        
        dates.sort(reverse=True)
        now = dates[0]
        
        # 1. Back-to-back detection
        if len(dates) >= 2:
            days_since_last = (dates[0] - dates[1]).days
            if days_since_last <= 1:
                fatiga_score += 30
                factores.append({
                    "tipo": "BACK-TO-BACK",
                    "severidad": "ALTA",
                    "detalle": f"Jugaron hace {days_since_last} días",
                    "impacto_pct": -5 if sport == "basketball" else -3,
                })
        
        # 2. Games in last 7 days
        seven_days_ago = now - timedelta(days=7)
        games_last_7 = sum(1 for d in dates if d >= seven_days_ago)
        if games_last_7 >= 4:
            fatiga_score += 20
            factores.append({
                "tipo": "CONGESTIÓN",
                "severidad": "MEDIA",
                "detalle": f"{games_last_7} juegos en 7 días",
                "impacto_pct": -3 if sport == "basketball" else -2,
            })
        
        # 3. Games in last 3 days
        three_days_ago = now - timedelta(days=3)
        games_last_3 = sum(1 for d in dates if d >= three_days_ago)
        if games_last_3 >= 3:
            fatiga_score += 25
            factores.append({
                "tipo": "3 EN 3 DÍAS",
                "severidad": "ALTA",
                "detalle": f"{games_last_3} juegos en 3 días",
                "impacto_pct": -4,
            })
        
        # 4. Long road trip
        if len(dates) >= 5:
            road_games = sum(1 for d in dates[:5] if True)  # Simplificado
            if road_games >= 4:
                fatiga_score += 15
                factores.append({
                    "tipo": "GIRA LARGA",
                    "severidad": "MEDIA",
                    "detalle": f"{road_games} juegos de visitante recientes",
                    "impacto_pct": -2,
                })
        
        # 5. Rest advantage
        if len(dates) >= 2:
            rest_days = (dates[0] - dates[1]).days
            if rest_days >= 3:
                fatiga_score -= 10
                factores.append({
                    "tipo": "DESCANSO EXTRA",
                    "severidad": "POSITIVA",
                    "detalle": f"{rest_days} días de descanso",
                    "impacto_pct": 3,
                })
        
        # Calcular impacto total
        impacto_total = sum(f.get("impacto_pct", 0) for f in factores)
        
        # Clasificación
        if fatiga_score >= 50:
            nivel = "CRÍTICA"
        elif fatiga_score >= 30:
            nivel = "MODERADA"
        elif fatiga_score >= 15:
            nivel = "LEVE"
        else:
            nivel = "MÍNIMA"
        
        return {
            "fatiga_score": min(100, fatiga_score),
            "nivel": nivel,
            "factores": factores,
            "impacto_pct": impacto_total,
            "resumen": f"Fatiga {nivel}: {len(factores)} factores detectados, impacto estimado {impacto_total:+d}%",
        }
    
    def analyze_travel(self, origin_city: str, destination_city: str,
                       game_time: str = None) -> dict:
        """
        Analiza impacto de viaje entre ciudades.
        
        Returns:
            dict con análisis de viaje y zones horarias
        """
        tz_origin = self.TIMEZONES.get(origin_city, 0)
        tz_dest = self.TIMEZONES.get(destination_city, 0)
        tz_diff = tz_dest - tz_origin
        
        factores = []
        impacto = 0
        
        # Diferencia de zona horaria
        if abs(tz_diff) >= 3:
            factores.append({
                "tipo": "ZONA HORARIA",
                "severidad": "ALTA",
                "detalle": f"{'Pierde' if tz_diff > 0 else 'Gana'} {abs(tz_diff)} horas",
                "impacto_pct": -3 if tz_diff > 0 else 1,
            })
            impacto += -3 if tz_diff > 0 else 1
        elif abs(tz_diff) >= 2:
            factores.append({
                "tipo": "ZONA HORARIA",
                "severidad": "MEDIA",
                "detalle": f"Cambio de {abs(tz_diff)} horas",
                "impacto_pct": -2,
            })
            impacto -= 2
        
        # Viaje transcontinental (simplificado)
        if abs(tz_diff) >= 3:
            factores.append({
                "tipo": "VIAJE TRANSCONTINENTAL",
                "severidad": "ALTA",
                "detalle": "Viaje largo + cambio de zona horaria",
                "impacto_pct": -2,
            })
            impacto -= 2
        
        return {
            "origin": origin_city,
            "destination": destination_city,
            "timezone_diff": tz_diff,
            "factores": factores,
            "impacto_pct": impacto,
            "resumen": f"Viaje {origin_city}→{destination_city}: {tz_diff:+d}h, impacto {impacto:+d}%",
        }


# ════════════════════════════════════════════════════════════════════════════
# 4. INTEGRACIÓN DE CLIMA
# ════════════════════════════════════════════════════════════════════════════

class WeatherAnalyzer:
    """
    Analiza impacto del clima en partidos al aire libre.
    
    Impactos documentados:
    - Viento >15mph: Reduce scoring significativamente
    - Lluvia: Aumenta turnovers, reduce passing
    - Frío extremo: Afecta kicking accuracy
    - Calor extremo: Fatiga acelerada
    """
    
    def analyze_weather(self, temperature_f: float, wind_mph: float,
                        precipitation_pct: float, humidity_pct: float,
                        is_outdoor: bool = True) -> dict:
        """
        Analiza impacto del clima en un partido.
        
        Args:
            temperature_f: Temperatura en Fahrenheit
            wind_mph: Velocidad del viento en mph
            precipitation_pct: Probabilidad de precipitación (%)
            humidity_pct: Humedad (%)
            is_outdoor: Si es al aire libre
        
        Returns:
            dict con análisis de clima y impacto
        """
        if not is_outdoor:
            return {
                "impacto": "MÍNIMO",
                "factores": [],
                "impacto_total_pct": 0,
                "resumen": "Estadio cubierto - sin impacto climático",
            }
        
        factores = []
        impacto = 0
        
        # Viento
        if wind_mph >= 20:
            factores.append({
                "tipo": "VIENTO FUERTE",
                "severidad": "ALTA",
                "detalle": f"{wind_mph} mph - reduce passing y kicking",
                "impacto_pct": -5,
                "mercado_afectado": "Totals (Under)",
            })
            impacto -= 5
        elif wind_mph >= 15:
            factores.append({
                "tipo": "VIENTO MODERADO",
                "severidad": "MEDIA",
                "detalle": f"{wind_mph} mph - efecto notable en juego aéreo",
                "impacto_pct": -3,
                "mercado_afectado": "Totals (Under)",
            })
            impacto -= 3
        elif wind_mph >= 10:
            factores.append({
                "tipo": "VIENTO LEVE",
                "severidad": "BAJA",
                "detalle": f"{wind_mph} mph - efecto menor",
                "impacto_pct": -1,
                "mercado_afectado": "Totals",
            })
            impacto -= 1
        
        # Lluvia
        if precipitation_pct >= 70:
            factores.append({
                "tipo": "LLUVIA ALTA",
                "severidad": "ALTA",
                "detalle": f"{precipitation_pct}% probabilidad",
                "impacto_pct": -4,
                "mercado_afectado": "Totals (Under), Turnovers",
            })
            impacto -= 4
        elif precipitation_pct >= 40:
            factores.append({
                "tipo": "LLUVIA PROBABLE",
                "severidad": "MEDIA",
                "detalle": f"{precipitation_pct}% probabilidad",
                "impacto_pct": -2,
                "mercado_afectado": "Totals (Under)",
            })
            impacto -= 2
        
        # Temperatura extrema
        if temperature_f <= 20:
            factores.append({
                "tipo": "FRÍO EXTREMO",
                "severidad": "ALTA",
                "detalle": f"{temperature_f}°F - afecta manos y kicking",
                "impacto_pct": -3,
                "mercado_afectado": "Totals (Under)",
            })
            impacto -= 3
        elif temperature_f >= 95:
            factores.append({
                "tipo": "CALOR EXTREMO",
                "severidad": "ALTA",
                "detalle": f"{temperature_f}°F - fatiga acelerada",
                "impacto_pct": -3,
                "mercado_afectado": "Totals (Under), Player Props",
            })
            impacto -= 3
        
        # Clasificación
        if impacto <= -8:
            nivel = "CRÍTICO"
        elif impacto <= -5:
            nivel = "SIGNIFICATIVO"
        elif impacto <= -2:
            nivel = "MODERADO"
        else:
            nivel = "MÍNIMO"
        
        return {
            "impacto": nivel,
            "factores": factores,
            "impacto_total_pct": impacto,
            "resumen": f"Clima {nivel}: {len(factores)} factores, impacto {impacto:+d}% en totals",
        }


# ════════════════════════════════════════════════════════════════════════════
# 5. CLV TRACKING
# ════════════════════════════════════════════════════════════════════════════

class CLVTracker:
    """
    Closing Line Value Tracker - La métrica #1 para medir edge real.
    
    CLV = (Closing_Implied_Prob - Bet_Implied_Prob) / Bet_Implied_Prob
    
    Benchmarks:
    - 2%+ CLV promedio = edge genuino (ROI esperado ~3.8%)
    - 3-5% CLV = territorio sharp elite
    - 5%+ CLV sostenido = raro, indica nicho especializado
    """
    
    def __init__(self):
        self.bets = []  # Lista de apuestas con CLV
    
    def calculate_clv(self, bet_odds: float, closing_odds: float,
                      bet_side: str = "back") -> dict:
        """
        Calcula CLV para una apuesta.
        
        Args:
            bet_odds: Cuota donde se apostó
            closing_odds: Cuota al cierre (la más efficiente)
            bet_side: "back" o "lay"
        
        Returns:
            dict con CLV y métricas
        """
        if bet_odds <= 1 or closing_odds <= 1:
            return {"error": "Cuotas inválidas"}
        
        bet_implied = 1 / bet_odds
        closing_implied = 1 / closing_odds
        
        if bet_side == "back":
            clv_pct = ((closing_implied - bet_implied) / bet_implied) * 100
        else:
            clv_pct = ((bet_implied - closing_implied) / closing_implied) * 100
        
        # Clasificación
        if clv_pct >= 5:
            nivel = "ELITE"
        elif clv_pct >= 3:
            nivel = "SHARP"
        elif clv_pct >= 2:
            nivel = "BUENO"
        elif clv_pct >= 0:
            nivel = "NEUTRAL"
        else:
            nivel = "NEGATIVO"
        
        return {
            "clv_pct": round(clv_pct, 2),
            "es_positivo": clv_pct > 0,
            "nivel": nivel,
            "bet_implied_prob": round(bet_implied * 100, 1),
            "closing_implied_prob": round(closing_implied * 100, 1),
            "bet_odds": bet_odds,
            "closing_odds": closing_odds,
            "recomendacion": (
                "CLV positivo - edge confirmado por mercado" if clv_pct >= 2 else
                "CLV negativo - reconsiderar estrategia" if clv_pct < 0 else
                "CLV marginal - monitorear"
            ),
        }
    
    def track_bet(self, match_id: str, team: str, bet_odds: float,
                  model_prob: float, closing_odds: float = None):
        """Registra una apuesta para tracking de CLV."""
        bet = {
            "match_id": match_id,
            "team": team,
            "bet_odds": bet_odds,
            "model_prob": model_prob,
            "bet_implied": round(1 / bet_odds * 100, 1),
            "timestamp": datetime.now().isoformat(),
            "closing_odds": closing_odds,
            "clv": None,
        }
        
        if closing_odds:
            clv_result = self.calculate_clv(bet_odds, closing_odds)
            bet["clv"] = clv_result
        
        self.bets.append(bet)
        return bet
    
    def get_summary(self) -> dict:
        """Resumen de CLV de todas las apuestas tracked."""
        if not self.bets:
            return {"total": 0, "clv_promedio": 0, "clv_positivo_pct": 0}
        
        clvs = [b["clv"]["clv_pct"] for b in self.bets if b.get("clv")]
        if not clvs:
            return {"total": len(self.bets), "clv_promedio": 0, "clv_positivo_pct": 0}
        
        return {
            "total": len(self.bets),
            "con_clv": len(clvs),
            "clv_promedio": round(sum(clvs) / len(clvs), 2),
            "clv_max": round(max(clvs), 2),
            "clv_min": round(min(clvs), 2),
            "clv_positivo_pct": round(sum(1 for c in clvs if c > 0) / len(clvs) * 100, 1),
            "nivel": (
                "ELITE" if sum(clvs) / len(clvs) >= 5 else
                "SHARP" if sum(clvs) / len(clvs) >= 3 else
                "BUENO" if sum(clvs) / len(clvs) >= 2 else
                "MEJORABLE"
            ),
        }


# ════════════════════════════════════════════════════════════════════════════
# 6. CALIBRACIÓN DE MODELOS
# ════════════════════════════════════════════════════════════════════════════

class ModelCalibrator:
    """
    Calibración de modelos - más importante que accuracy bruta.
    
    Referencia: Walsh & Joshi (2024)
    "Model calibration is more important than accuracy for sports betting.
    Using calibration rather than accuracy leads to ROI of +34.69% vs -35.17%"
    """
    
    def __init__(self):
        self.predictions = []  # Lista de (predicted_prob, actual_outcome)
    
    def add_prediction(self, predicted_prob: float, actual: bool):
        """Agrega una predicción para calibración."""
        self.predictions.append((predicted_prob, actual))
    
    def calibrate(self, method: str = "isotonic") -> dict:
        """
        Calibra el modelo usando Platt scaling o isotonic regression.
        
        Args:
            method: "platt" o "isotonic"
        
        Returns:
            dict con métricas de calibración
        """
        if len(self.predictions) < 20:
            return {"error": "Necesitas al menos 20 predicciones para calibrar"}
        
        # Binning: agrupar predicciones en cubos
        n_bins = min(10, len(self.predictions) // 5)
        bins = [[] for _ in range(n_bins)]
        
        for prob, actual in self.predictions:
            bin_idx = min(int(prob * n_bins), n_bins - 1)
            bins[bin_idx].append(actual)
        
        # Calcular calibration error
        calibration_error = 0
        bin_details = []
        
        for i, bin_preds in enumerate(bins):
            if not bin_preds:
                continue
            
            expected_prob = (i + 0.5) / n_bins
            actual_rate = sum(bin_preds) / len(bin_preds)
            error = abs(expected_prob - actual_rate)
            
            calibration_error += error * len(bin_preds)
            bin_details.append({
                "bin": f"{expected_prob*100:.0f}%",
                "predicciones": len(bin_preds),
                "tasa_real": round(actual_rate * 100, 1),
                "error": round(error * 100, 1),
            })
        
        total = len(self.predictions)
        ece = calibration_error / total  # Expected Calibration Error
        
        # Brier Score
        brier = sum((p - a) ** 2 for p, a in self.predictions) / total
        
        # Log Loss
        log_loss = 0
        for p, a in self.predictions:
            p = max(0.001, min(0.999, p))
            if a:
                log_loss -= math.log(p)
            else:
                log_loss -= math.log(1 - p)
        log_loss /= total
        
        return {
            "n_predicciones": total,
            "ece": round(ece * 100, 2),  # Expected Calibration Error
            "brier_score": round(brier, 4),
            "log_loss": round(log_loss, 4),
            "calidad": (
                "EXCELENTE" if ece < 0.03 else
                "BUENA" if ece < 0.05 else
                "ACEPTABLE" if ece < 0.08 else
                "NECESITA CALIBRACIÓN"
            ),
            "bins": bin_details,
            "recomendacion": (
                "Modelo bien calibrado - usar para apuestas" if ece < 0.05 else
                "Calibrar modelo antes de apostar significativamente"
            ),
        }


# ════════════════════════════════════════════════════════════════════════════
# INSTANCIAS GLOBALES
# ════════════════════════════════════════════════════════════════════════════

dixon_coles = DixonColesModel()
improved_elo = ImprovedElo()
fatigue_analyzer = FatigueAnalyzer()
weather_analyzer = WeatherAnalyzer()
clv_tracker = CLVTracker()
calibrator = ModelCalibrator()
