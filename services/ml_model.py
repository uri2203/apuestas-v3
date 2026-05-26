"""
Modelo ML — Gradient Boosting Classifier (scikit-learn).

Features basadas en:
- Diferencia de ratings ELO
- Parámetros de ataque/defensa Dixon-Coles
- Forma reciente (últimos 5 partidos)
- Ventaja de local
- H2H histórico

Sin dependencias externas extra (scikit-learn ya incluye GradientBoosting).
Se entrena bajo demanda con el historial disponible.
"""

import logging
import math
from collections import defaultdict

logger = logging.getLogger(__name__)

try:
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.model_selection import cross_val_score
    import numpy as np
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logger.warning("scikit-learn no instalado — ml_model usará fallback estadístico")


# ── Feature Engineering ───────────────────────────────────────────────────────

def _extraer_features(partido: dict, historial: list, elo_ratings: dict, dc_params: dict) -> list:
    """
    Extrae vector de features numérico para un partido.
    """
    home = partido["home"]
    away = partido["away"]

    # 1. ELO
    elo_h = elo_ratings.get(home, 1500)
    elo_a = elo_ratings.get(away, 1500)
    elo_diff = elo_h - elo_a + 65  # +65 ventaja local

    # 2. Dixon-Coles
    ataque_h  = dc_params.get("ataque",  {}).get(home, 1.0)
    defensa_h = dc_params.get("defensa", {}).get(home, 1.0)
    ataque_a  = dc_params.get("ataque",  {}).get(away, 1.0)
    defensa_a = dc_params.get("defensa", {}).get(away, 1.0)
    lambda_h  = 1.35 * ataque_h * defensa_a  # lambda local estimado
    lambda_a  = ataque_a * defensa_h          # lambda visitante estimado

    # 3. Forma reciente (últimos 5 partidos)
    def _puntos_forma(equipo, n=5):
        mis = []
        for p in reversed(historial):
            if len(mis) >= n:
                break
            if p["home"] == equipo:
                gh, ga = p["home_goals"], p["away_goals"]
                mis.append(3 if gh > ga else 1 if gh == ga else 0)
            elif p["away"] == equipo:
                gh, ga = p["away_goals"], p["home_goals"]
                mis.append(3 if gh > ga else 1 if gh == ga else 0)
        return sum(mis) / (len(mis) * 3) if mis else 0.5

    forma_h = _puntos_forma(home)
    forma_a = _puntos_forma(away)

    # 4. Goles a favor/en contra (promedio últimos 5)
    def _avg_goles(equipo, gf=True, n=5):
        goles = []
        for p in reversed(historial):
            if len(goles) >= n:
                break
            if p["home"] == equipo:
                goles.append(p["home_goals"] if gf else p["away_goals"])
            elif p["away"] == equipo:
                goles.append(p["away_goals"] if gf else p["home_goals"])
        return sum(goles) / len(goles) if goles else 1.2

    gf_h = _avg_goles(home, gf=True)
    gc_h = _avg_goles(home, gf=False)
    gf_a = _avg_goles(away, gf=True)
    gc_a = _avg_goles(away, gf=False)

    # 5. H2H (últimos 5 enfrentamientos directos)
    h2h = [p for p in historial
           if (p["home"] == home and p["away"] == away) or
              (p["home"] == away and p["away"] == home)][-5:]
    if h2h:
        wins_h = sum(1 for p in h2h if
                     (p["home"] == home and p["home_goals"] > p["away_goals"]) or
                     (p["away"] == home and p["away_goals"] > p["home_goals"]))
        h2h_ratio = wins_h / len(h2h)
    else:
        h2h_ratio = 0.5

    return [
        elo_diff / 400,          # f1: diferencia ELO normalizada
        lambda_h,                # f2: goles esperados local
        lambda_a,                # f3: goles esperados visitante
        lambda_h - lambda_a,     # f4: diferencia de lambdas
        forma_h,                 # f5: forma local [0-1]
        forma_a,                 # f6: forma visitante [0-1]
        forma_h - forma_a,       # f7: diferencia de forma
        gf_h,                    # f8: goles a favor local
        gc_h,                    # f9: goles en contra local
        gf_a,                    # f10: goles a favor visitante
        gc_a,                    # f11: goles en contra visitante
        gf_h - gc_a,             # f12: ataque local vs defensa visitante
        gf_a - gc_h,             # f13: ataque visitante vs defensa local
        h2h_ratio,               # f14: dominancia H2H local
        ataque_h / max(defensa_h, 0.01),   # f15: rating ofensivo local
        ataque_a / max(defensa_a, 0.01),   # f16: rating ofensivo visitante
    ]


class MLModel:
    """
    Gradient Boosting Classifier para predicción 1X2.
    Wrapper que incluye entrenamiento, predicción y evaluación.
    """

    def __init__(self):
        self.clf       = None
        self.le        = None
        self.entrenado = False
        self.accuracy  = None
        self._elo      = {}
        self._dc_atk   = defaultdict(lambda: 1.0)
        self._dc_def   = defaultdict(lambda: 1.0)

    def _actualizar_parametros(self, historial: list):
        """Pre-computa ELO y DC params del historial."""
        from models.elo import ELOModel
        from models.dixon_coles import DixonColesModel

        elo = ELOModel()
        elo.update(historial)
        self._elo = dict(elo.ratings)

        dc = DixonColesModel()
        dc.fit(historial)
        self._dc_atk = dc.ataque
        self._dc_def = dc.defensa

    def fit(self, historial: list) -> "MLModel":
        if not HAS_SKLEARN:
            logger.warning("scikit-learn no disponible — ML model desactivado")
            return self

        if len(historial) < 20:
            logger.warning("Historial insuficiente para ML (%d partidos)", len(historial))
            return self

        self._actualizar_parametros(historial)

        X, y = [], []
        dc_params = {"ataque": self._dc_atk, "defensa": self._dc_def}

        for p in historial:
            if "home_goals" not in p:
                continue
            feats = _extraer_features(p, historial, self._elo, dc_params)
            gh, ga = p["home_goals"], p["away_goals"]
            resultado = "1" if gh > ga else "X" if gh == ga else "2"
            X.append(feats)
            y.append(resultado)

        if len(X) < 15:
            return self

        import numpy as np
        X_np = np.array(X)
        self.le = LabelEncoder()
        y_enc   = self.le.fit_transform(y)

        self.clf = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            min_samples_leaf=3,
            random_state=42,
        )

        # Cross-validation para estimar accuracy real
        if len(X) >= 30:
            scores = cross_val_score(self.clf, X_np, y_enc, cv=min(5, len(X)//5), scoring="accuracy")
            self.accuracy = round(float(scores.mean()) * 100, 1)
        else:
            self.accuracy = None

        self.clf.fit(X_np, y_enc)
        self.entrenado = True
        logger.info("MLModel entrenado con %d partidos. Accuracy CV: %s%%", len(X), self.accuracy)
        return self

    def predict(self, home: str, away: str, historial: list) -> dict:
        if not HAS_SKLEARN or not self.entrenado:
            return {"error": "Modelo ML no disponible", "disponible": False}

        import numpy as np
        dc_params = {"ataque": self._dc_atk, "defensa": self._dc_def}
        partido_dummy = {"home": home, "away": away}
        feats = _extraer_features(partido_dummy, historial, self._elo, dc_params)

        probs = self.clf.predict_proba([feats])[0]
        clases = self.le.classes_

        prob_map = {str(c): round(float(p), 4) for c, p in zip(clases, probs)}
        p_local    = prob_map.get("1", 0.0)
        p_empate   = prob_map.get("X", 0.0)
        p_visitante= prob_map.get("2", 0.0)

        max_p  = max(p_local, p_empate, p_visitante)
        pronostico = "1" if max_p == p_local else "X" if max_p == p_empate else "2"

        importancia = None
        if hasattr(self.clf, "feature_importances_"):
            nombres = [
                "elo_diff", "lambda_local", "lambda_visitante", "diff_lambdas",
                "forma_local", "forma_visitante", "diff_forma",
                "gf_local", "gc_local", "gf_visitante", "gc_visitante",
                "atk_local_vs_def_vis", "atk_vis_vs_def_local", "h2h",
                "rating_ofensivo_local", "rating_ofensivo_visitante",
            ]
            importancia = {n: round(float(v), 4)
                           for n, v in zip(nombres, self.clf.feature_importances_)}

        return {
            "disponible":       True,
            "modelo":           "GradientBoosting ML",
            "local":            p_local,
            "empate":           p_empate,
            "visitante":        p_visitante,
            "pronostico":       pronostico,
            "confianza_pct":    round(max_p * 100, 1),
            "accuracy_cv_pct":  self.accuracy,
            "importancia_features": importancia,
        }

    def feature_importance(self) -> list:
        if not self.entrenado or not HAS_SKLEARN:
            return []
        nombres = [
            "elo_diff", "lambda_local", "lambda_visitante", "diff_lambdas",
            "forma_local", "forma_visitante", "diff_forma",
            "gf_local", "gc_local", "gf_visitante", "gc_visitante",
            "atk_local_vs_def_vis", "atk_vis_vs_def_local", "h2h",
            "rating_ofensivo_local", "rating_ofensivo_visitante",
        ]
        return sorted(
            [{"feature": n, "importancia": round(float(v), 4)}
             for n, v in zip(nombres, self.clf.feature_importances_)],
            key=lambda x: x["importancia"], reverse=True,
        )


# Singleton
_ml_model: MLModel = None


def get_ml_model(historial: list = None) -> MLModel:
    global _ml_model
    if _ml_model is None or (historial and not _ml_model.entrenado):
        _ml_model = MLModel()
        from services.progol import HISTORIAL_DEMO
        _ml_model.fit(historial or HISTORIAL_DEMO)
    return _ml_model
