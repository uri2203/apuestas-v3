"""
Ensemble model: combina Dixon-Coles, ELO y Poisson con pesos.
Produce predicción final con intervalos de confianza.
"""
from models.dixon_coles import DixonColesModel
import os
from models.elo import ELOModel
import math
import random


class EnsembleModel:
    """
    Combina tres modelos con pesos configurables:
    - Dixon-Coles: 50% (el más preciso en fútbol)
    - ELO:         30% (captura forma dinámica)
    - Poisson raw: 20% (baseline con xG de API)
    """

    def __init__(self,
                 w_dc=None,
                 w_elo=None,
                 w_poisson=None):
        import os
        # Pesos configurables vía env (optimizados empíricamente)
        self.w_dc      = w_dc      if w_dc      is not None else float(os.getenv("ENSEMBLE_W_DC", "0.50"))
        self.w_elo     = w_elo     if w_elo     is not None else float(os.getenv("ENSEMBLE_W_ELO", "0.30"))
        self.w_poisson = w_poisson if w_poisson is not None else float(os.getenv("ENSEMBLE_W_POISSON", "0.20"))
        self.dc  = DixonColesModel()
        self.elo = ELOModel()
        self.entrenado = False

    def fit(self, partidos):
        """Entrena todos los modelos con el mismo historial."""
        if not partidos:
            return self
        self.dc.fit(partidos)
        self.elo.update(partidos)
        self.entrenado = True
        return self

    def predict(self, home, away,
                xg_home=None, xg_away=None):
        """
        Predicción ensemble.
        xg_home/xg_away: expected goals de API-Football (opcional).
        Si se proporcionan, aumentan el peso del modelo Poisson.
        """
        # ── Dixon-Coles ──
        dc_pred = self.dc.predict(home, away)

        # ── ELO ──
        elo_pred = self.elo.predict_with_form(home, away)

        # ── Poisson con xG real o lambdas de DC ──
        if xg_home and xg_away:
            lam = xg_home
            mu  = xg_away
            w_p = self.w_poisson * 1.5  # más peso si tenemos xG real
        else:
            lam = dc_pred["lambda_local"]
            mu  = dc_pred["lambda_visitante"]
            w_p = self.w_poisson

        poi_pred = _poisson_predict(lam, mu)

        # ── Ensemble ponderado ──
        w_total = self.w_dc + self.w_elo + w_p
        w_dc  = self.w_dc  / w_total
        w_elo = self.w_elo / w_total
        w_poi = w_p        / w_total

        p_home = (dc_pred["local"]     * w_dc +
                  elo_pred["local"]    * w_elo +
                  poi_pred["local"]    * w_poi)
        p_draw = (dc_pred["empate"]    * w_dc +
                  elo_pred["empate"]   * w_elo +
                  poi_pred["empate"]   * w_poi)
        p_away = (dc_pred["visitante"] * w_dc +
                  elo_pred["visitante"]* w_elo +
                  poi_pred["visitante"]* w_poi)

        total = p_home + p_draw + p_away
        p_home /= total
        p_draw /= total
        p_away /= total

        return {
            "home": home,
            "away": away,
            "local":     round(p_home, 4),
            "empate":    round(p_draw, 4),
            "visitante": round(p_away, 4),
            "cuota_justa_local":     round(1 / p_home, 3) if p_home > 0 else 99,
            "cuota_justa_empate":    round(1 / p_draw, 3) if p_draw > 0 else 99,
            "cuota_justa_visitante": round(1 / p_away, 3) if p_away > 0 else 99,
            "modelo": "Ensemble (DC + ELO + Poisson)",
            "componentes": {
                "dixon_coles": {
                    "local": dc_pred["local"],
                    "empate": dc_pred["empate"],
                    "visitante": dc_pred["visitante"],
                    "peso": round(w_dc, 2),
                },
                "elo": {
                    "local": elo_pred["local"],
                    "empate": elo_pred["empate"],
                    "visitante": elo_pred["visitante"],
                    "elo_local": elo_pred.get("elo_local"),
                    "elo_visitante": elo_pred.get("elo_visitante"),
                    "peso": round(w_elo, 2),
                },
                "poisson": {
                    "local": poi_pred["local"],
                    "empate": poi_pred["empate"],
                    "visitante": poi_pred["visitante"],
                    "lambda_local": round(lam, 2),
                    "lambda_visitante": round(mu, 2),
                    "peso": round(w_poi, 2),
                    "usa_xg_real": xg_home is not None,
                },
            },
            "xg_home": xg_home or round(lam, 2),
            "xg_away": xg_away or round(mu, 2),
        }

    def ranking_dc(self):
        return self.dc.ranking()

    def ranking_elo(self):
        return self.elo.ranking()


def _poisson_predict(lam, mu, max_g=8):
    """Predicción Poisson pura para validación."""
    def pmf(k, l):
        return math.exp(-l) * (l**k) / math.factorial(k)

    h = d = a = 0.0
    for i in range(max_g + 1):
        for j in range(max_g + 1):
            p = pmf(i, lam) * pmf(j, mu)
            if i > j:   h += p
            elif i == j: d += p
            else:        a += p
    total = h + d + a or 1
    return {"local": h/total, "empate": d/total, "visitante": a/total}
