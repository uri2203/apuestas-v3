"""
ML Avanzado — Feature Engineering (30+ features), MLP Neural Net,
Gradient Boosting, Advanced Ensemble con calibración.

Sin costo adicional: features desde ESPN (resultados + standings).
"""
import logging, os, pickle, json, math
from datetime import datetime

logger = logging.getLogger(__name__)

import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "saved")
os.makedirs(MODEL_DIR, exist_ok=True)

LIGAS = ["liga_mx","mls","premier_league","la_liga","serie_a","bundesliga","ligue_1"]

# ── FEATURE ENGINEER ─────────────────────────────────────────────────────────────

class FeatureEngineer:
    """Construye 30+ features por partido desde datos ESPN."""

    def build_features(self, liga_key="liga_mx"):
        """Construye dataset X, y para entrenamiento."""
        from services.espn_scraper import get_historial_entrenamiento, get_standings

        historial = get_historial_entrenamiento(liga_key)
        if len(historial) < 30:
            return np.array([]), np.array([]), []

        # Calcular estadísticas por equipo (ventanas móviles)
        team_stats = self._compute_team_stats(historial)

        # Tabla de posiciones
        standings = get_standings(liga_key)
        standings_map = {s["equipo"]: s for s in standings if s.get("equipo")}

        X, y, match_info = [], [], []
        for i, m in enumerate(historial):
            home, away = m.get("home",""), m.get("away","")
            if not home or not away:
                continue
            gh, ga = m.get("home_goals"), m.get("away_goals")
            if gh is None or ga is None:
                continue

            # Features de cada equipo hasta este partido
            hist_h = historial[:i]
            hist_a = historial[:i]

            feat_h = self._team_features(home, hist_h, standings_map)
            feat_a = self._team_features(away, hist_a, standings_map)
            if feat_h is None or feat_a is None:
                continue

            features = feat_h + feat_a + self._match_features(home, away)
            X.append(features)
            # target: 0=visitante, 1=empate, 2=local
            if gh > ga:
                y.append(2)
            elif gh == ga:
                y.append(1)
            else:
                y.append(0)
            match_info.append({"home":home,"away":away,"fecha":m.get("fecha","")})

        return np.array(X), np.array(y), match_info

    def _compute_team_stats(self, historial):
        """Precomputa todas las estadísticas por equipo a lo largo del tiempo."""
        stats = {}
        for m in historial:
            home, away = m.get("home",""), m.get("away","")
            gh, ga = m.get("home_goals",0), m.get("away_goals",0)
            for team, gf, gc, is_home in [(home,gh,ga,True),(away,ga,gh,False)]:
                if team not in stats:
                    stats[team] = {"goles_favor":[],"goles_contra":[],"resultados":[],"local":[]}
                stats[team]["goles_favor"].append(gf)
                stats[team]["goles_contra"].append(gc)
                stats[team]["resultados"].append(1 if gf>gc else 0.5 if gf==gc else 0)
                stats[team]["local"].append(1 if is_home else 0)
        return stats

    def _team_features(self, team, historial_previo, standings_map):
        """30+ features para un equipo."""
        from services.espn_scraper import get_historial_entrenamiento

        relevant = [m for m in historial_previo
                    if m.get("home")==team or m.get("away")==team]
        n = len(relevant)
        if n == 0:
            return None

        last5 = relevant[-5:] if len(relevant)>=5 else relevant
        last10 = relevant[-10:] if len(relevant)>=10 else relevant

        # Form features
        pts5 = sum(3 if m.get("home")==team and (m.get("home_goals",0) or 0)>(m.get("away_goals",0) or 0)
                      or m.get("away")==team and (m.get("away_goals",0) or 0)>(m.get("home_goals",0) or 0)
                   else 1 if (m.get("home_goals",0) or 0)==(m.get("away_goals",0) or 0)
                   else 0 for m in last5)
        pts10 = sum(3 if m.get("home")==team and (m.get("home_goals",0) or 0)>(m.get("away_goals",0) or 0)
                       or m.get("away")==team and (m.get("away_goals",0) or 0)>(m.get("home_goals",0) or 0)
                    else 1 if (m.get("home_goals",0) or 0)==(m.get("away_goals",0) or 0)
                    else 0 for m in last10)

        gf5 = sum(m.get("home_goals",0) or 0 if m.get("home")==team
                  else m.get("away_goals",0) or 0 for m in last5)
        gc5 = sum(m.get("away_goals",0) or 0 if m.get("home")==team
                  else m.get("home_goals",0) or 0 for m in last5)
        gf10 = sum(m.get("home_goals",0) or 0 if m.get("home")==team
                   else m.get("away_goals",0) or 0 for m in last10)
        gc10 = sum(m.get("away_goals",0) or 0 if m.get("home")==team
                   else m.get("home_goals",0) or 0 for m in last10)

        wins5 = sum(1 for m in last5 if (m.get("home")==team and (m.get("home_goals",0) or 0)>(m.get("away_goals",0) or 0))
                                         or (m.get("away")==team and (m.get("away_goals",0) or 0)>(m.get("home_goals",0) or 0)))
        clean5 = sum(1 for m in last5 if (m.get("home")==team and (m.get("away_goals",0) or 0)==0)
                                         or (m.get("away")==team and (m.get("home_goals",0) or 0)==0))
        home_pct = sum(1 for m in last10 if m.get("home")==team) / max(len(last10),1)

        # Averages
        ppg5 = pts5 / max(len(last5),1)
        ppg10 = pts10 / max(len(last10),1)
        gf_p5 = gf5 / max(len(last5),1)
        gc_p5 = gc5 / max(len(last5),1)
        win_rate5 = wins5 / max(len(last5),1)

        # Season features (from standings)
        st = standings_map.get(team, {})
        pos = st.get("posicion", 10) or 10
        pts_st = st.get("puntos", 0) or 0
        jugados = st.get("jugados", 1) or 1
        ppg_season = pts_st / max(jugados, 1)
        gd = (st.get("ganados", 0) or 0) * 2 + (st.get("empates", 0) or 0)  # simplified gd proxy

        # Trend (last 3 vs previous 3)
        if len(relevant) >= 6:
            prev3 = relevant[-6:-3]
            pts_prev3 = sum(3 if m.get("home")==team and (m.get("home_goals",0) or 0)>(m.get("away_goals",0) or 0)
                               or m.get("away")==team and (m.get("away_goals",0) or 0)>(m.get("home_goals",0) or 0)
                            else 1 if (m.get("home_goals",0) or 0)==(m.get("away_goals",0) or 0)
                            else 0 for m in prev3) / 3
            trend = ppg5 - pts_prev3
        else:
            trend = 0

        # Attack/defense strength vs league avg
        all_gf = [m.get("home_goals",0) or 0 for m in historial_previo] + \
                 [m.get("away_goals",0) or 0 for m in historial_previo]
        all_gc = [m.get("away_goals",0) or 0 for m in historial_previo] + \
                 [m.get("home_goals",0) or 0 for m in historial_previo]
        league_avg_gf = np.mean(all_gf) if all_gf else 1
        league_avg_gc = np.mean(all_gc) if all_gc else 1
        atk_strength = gf_p5 / max(league_avg_gf, 0.1)
        def_strength = gc_p5 / max(league_avg_gc, 0.1)

        features = [
            ppg5, ppg10, gf_p5, gc_p5, win_rate5, clean5/5,
            ppg_season, pos/20, pts_st/50, gd/30,
            atk_strength, def_strength, home_pct, trend,
            n/50, gf10/10, gc10/10,  # raw totals
            ppg5 - ppg_season,  # form vs season
            gf_p5 - gc_p5,  # goal diff per game
            (gf_p5 * atk_strength) / max(def_strength, 0.01),  # power index
        ]
        return features

    def _match_features(self, home, away):
        """Features del matchup (H2H implícito solo con datos disponibles)."""
        return [0.5, 0.5]  # placeholder for future H2H features

    @property
    def feature_names(self):
        return [
            "ppg5","ppg10","gf_p5","gc_p5","win_rate5","clean_sheet_pct",
            "ppg_season","posicion_norm","pts_norm","gd_norm",
            "attack_strength","defense_strength","home_pct","trend",
            "n_partidos","gf10","gc10",
            "form_vs_season","gd_pg","power_index",
        ] + ["h2h_placeholder1","h2h_placeholder2"]


# ── MODELOS ──────────────────────────────────────────────────────────────────────

def _save_model(model, scaler, name, liga):
    path = os.path.join(MODEL_DIR, f"{liga}_{name}.pkl")
    with open(path, "wb") as f:
        pickle.dump({"model":model,"scaler":scaler}, f)
    return path

def _load_model(name, liga):
    path = os.path.join(MODEL_DIR, f"{liga}_{name}.pkl")
    if not os.path.exists(path):
        return None, None
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data["model"], data["scaler"]


class MLPModel:
    """MLP Neural Net Classifier con early stopping y calibración."""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.name = "mlp"

    def train(self, X, y, liga):
        if X.shape[0] < 50:
            return False
        mask = np.isfinite(X).all(axis=1)
        X, y = X[mask], y[mask]
        if X.shape[0] < 50:
            return False

        X_scaled = self.scaler.fit_transform(X)
        clf = MLPClassifier(
            hidden_layer_sizes=(64,32), activation="relu",
            solver="adam", max_iter=500, early_stopping=True,
            validation_fraction=0.15, n_iter_no_change=10,
            random_state=42, verbose=False,
        )
        try:
            clf.fit(X_scaled, y)
            # Calibrate
            cal = CalibratedClassifierCV(clf, cv=3, method="sigmoid")
            cal.fit(X_scaled, y)
            self.model = cal
            _save_model(cal, self.scaler, self.name, liga)
            logger.info("MLP entrenado para %s: %d muestras, %d features",
                        liga, X.shape[0], X.shape[1])
            return True
        except Exception as e:
            logger.error("MLP train error %s: %s", liga, e)
            return False

    def predict_proba(self, X):
        if self.model is None:
            return None
        try:
            X_s = self.scaler.transform(X)
            return self.model.predict_proba(X_s)
        except Exception:
            return None

    def load(self, liga):
        m, s = _load_model(self.name, liga)
        if m:
            self.model = m
            self.scaler = s
            return True
        return False

    @property
    def clases(self):
        return [[0],[1],[2]]


class GBModel:
    """Gradient Boosting Classifier con calibración."""

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.name = "gbm"

    def train(self, X, y, liga):
        if X.shape[0] < 50:
            return False
        mask = np.isfinite(X).all(axis=1)
        X, y = X[mask], y[mask]
        if X.shape[0] < 50:
            return False

        X_scaled = self.scaler.fit_transform(X)
        clf = GradientBoostingClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.05,
            subsample=0.8, random_state=42, verbose=False,
        )
        try:
            clf.fit(X_scaled, y)
            cal = CalibratedClassifierCV(clf, cv=3, method="sigmoid")
            cal.fit(X_scaled, y)
            self.model = cal
            _save_model(cal, self.scaler, self.name, liga)
            logger.info("GBM entrenado para %s: %d muestras", liga, X.shape[0])
            return True
        except Exception as e:
            logger.error("GBM train error %s: %s", liga, e)
            return False

    def predict_proba(self, X):
        if self.model is None:
            return None
        try:
            X_s = self.scaler.transform(X)
            return self.model.predict_proba(X_s)
        except Exception:
            return None

    def load(self, liga):
        m, s = _load_model(self.name, liga)
        if m:
            self.model = m
            self.scaler = s
            return True
        return False


class AdvancedEnsemble:
    """Combina MLP + GBM con pesos dinámicos según rendimiento histórico."""

    def __init__(self):
        self.mlp = MLPModel()
        self.gbm = GBModel()
        self.fe = FeatureEngineer()
        self.name = "advanced_ensemble"

    def train(self, liga="liga_mx"):
        """Entrena ambos modelos y evalua performance."""
        X, y, match_info = self.fe.build_features(liga)
        if X.shape[0] < 50:
            return {"error":f"Dataset insuficiente: {X.shape[0]} muestras (min 50)"}

        self.mlp.train(X, y, liga)
        self.gbm.train(X, y, liga)

        # Evaluación
        from sklearn.metrics import accuracy_score, log_loss, brier_score_loss
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)

        results = {}
        for name, mod in [("mlp",self.mlp), ("gbm",self.gbm)]:
            mod.train(X_train, y_train, f"{liga}_{name}_eval")
            proba = mod.predict_proba(X_test)
            if proba is not None:
                preds = np.argmax(proba, axis=1)
                results[name] = {
                    "accuracy": round(accuracy_score(y_test, preds), 4),
                    "log_loss": round(log_loss(y_test, proba), 4),
                    "n_test": len(y_test),
                }

        # Guardar ensemble meta-info
        _save_model(
            {"pesos": self._calcular_pesos(results), "results": results},
            StandardScaler(), self.name, liga,
        )
        self._guardar_rendimiento(liga, X_test, y_test)

        return {
            "liga": liga,
            "n_muestras": X.shape[0],
            "n_features": X.shape[1],
            "resultados": results,
            "feature_names": self.fe.feature_names,
            "status": "ok",
        }

    def _calcular_pesos(self, results):
        """Pesos inversamente proporcionales al log_loss."""
        pesos = {}
        total_ll = sum(r.get("log_loss", 1) for r in results.values())
        for name, r in results.items():
            ll = r.get("log_loss", 1)
            pesos[name] = round((total_ll - ll) / max(total_ll, 0.01), 2)
        # Normalizar
        total = sum(pesos.values()) or 1
        return {k: round(v/total, 3) for k, v in pesos.items()}

    def _guardar_rendimiento(self, liga, X_test, y_test):
        """Guarda métricas de rendimiento en DB."""
        from database import db, _execute
        # Feature importance from GBM
        if self.gbm.model and hasattr(self.gbm.model, "calibrated_classifiers_"):
            cc = self.gbm.model.calibrated_classifiers_[0]
            gbm_inner = getattr(cc, "base_estimator", None) or getattr(cc, "estimator", None)
            if hasattr(gbm_inner, "feature_importances_"):
                imp = gbm_inner.feature_importances_.tolist()
                names = self.fe.feature_names[:len(imp)]
                try:
                    with db() as conn:
                        for n, v in zip(names, imp):
                            _execute(conn,
                                "INSERT OR REPLACE INTO feature_importance "
                                "(liga, feature_name, importance, updated_at) "
                                "VALUES (?,?,?,datetime('now'))",
                                (liga, n, round(v, 6)))
                except Exception as e:
                    logger.warning("Feature importance save: %s", e)

    def predict(self, home, away, liga="liga_mx"):
        """Predice un partido usando el ensemble avanzado."""
        from services.espn_scraper import get_historial_entrenamiento

        historial = get_historial_entrenamiento(liga)
        if len(historial) < 30:
            return {"error": "Historial insuficiente para features"}

        stats = self.fe._compute_team_stats(historial)
        from services.espn_scraper import get_standings
        standings = get_standings(liga)
        standings_map = {s["equipo"]: s for s in standings if s.get("equipo")}

        feat_h = self.fe._team_features(home, historial, standings_map)
        feat_a = self.fe._team_features(away, historial, standings_map)
        if feat_h is None or feat_a is None:
            return {"error": f"Sin datos para {home} o {away}"}

        X = np.array([feat_h + feat_a + self.fe._match_features(home, away)])

        # Cargar modelos si no están en memoria
        if self.mlp.model is None:
            self.mlp.load(liga)
        if self.gbm.model is None:
            self.gbm.load(liga)

        probas = {}
        for name, mod in [("mlp",self.mlp), ("gbm",self.gbm)]:
            p = mod.predict_proba(X)
            if p is not None:
                probas[name] = p[0].tolist()

        if not probas:
            return {"error": "Ningún modelo pudo predecir"}

        # Cargar pesos del ensemble
        meta, _ = _load_model(self.name, liga)
        pesos = meta.get("pesos", {"mlp":0.5,"gbm":0.5}) if meta else {"mlp":0.5,"gbm":0.5}

        # Ensemble ponderado
        final = np.zeros(3)
        for name, p in probas.items():
            w = pesos.get(name, 0.5)
            final += np.array(p) * w
        final /= sum(pesos.values()) or 1
        final = final / final.sum()

        # Interpretar: [visitante, empate, local]
        labels = ["2","X","1"]
        results = {l: round(float(final[i]), 4) for i, l in enumerate(labels)}
        pick = max(results, key=results.get)
        conf = results[pick]

        return {
            "home": home, "away": away,
            "liga": liga,
            "prob_local": float(results["1"]),
            "prob_empate": float(results["X"]),
            "prob_visitante": float(results["2"]),
            "pronostico": pick,
            "confianza_pct": round(conf * 100, 1),
            "cuota_justa_local": round(1/max(results["1"], 0.001), 2),
            "cuota_justa_empate": round(1/max(results["X"], 0.001), 2),
            "cuota_justa_visitante": round(1/max(results["2"], 0.001), 2),
            "modelo": "Advanced Ensemble (MLP + GBM)",
            "pesos_modelos": pesos,
            "probas_individuales": probas,
        }

    def predict_proximos(self, liga="liga_mx", dias=7):
        """Predice todos los próximos partidos."""
        from services.espn_scraper import get_proximos
        proximos = get_proximos(liga, dias)
        if not proximos:
            return {"error": "No hay próximos partidos", "liga": liga}

        resultados = []
        for p in proximos:
            home, away = p.get("home",""), p.get("away","")
            if not home or not away:
                continue
            try:
                pred = self.predict(home, away, liga)
                if "error" not in pred:
                    pred["fecha"] = p.get("fecha","")
                    resultados.append(pred)
            except Exception as e:
                logger.warning("Error prediciendo %s vs %s: %s", home, away, e)

        return {
            "liga": liga,
            "total": len(resultados),
            "predicciones": resultados,
        }


def auto_train_all_avanzado() -> dict:
    """Entrena modelos avanzados para todas las ligas."""
    total = 0
    errores = []
    for liga in LIGAS:
        try:
            ae = AdvancedEnsemble()
            r = ae.train(liga)
            if "error" not in r:
                total += r.get("n_muestras", 0)
            else:
                errores.append(f"{liga}: {r['error']}")
        except Exception as e:
            errores.append(f"{liga}: {e}")
    return {
        "total_muestras": total,
        "ligas_entrenadas": len(LIGAS) - len(errores),
        "errores": errores,
        "feature_count": 23,
    }


def get_feature_importance(liga="liga_mx") -> list:
    """Obtiene importancia de features desde DB."""
    from database import db, _fetchall
    try:
        with db() as conn:
            rows = _fetchall(conn,
                "SELECT feature_name, importance FROM feature_importance "
                "WHERE liga=? ORDER BY importance DESC LIMIT 30",
                (liga,))
        return rows or []
    except Exception:
        return []


def get_model_performance(liga="liga_mx") -> dict:
    """Obtiene rendimiento de modelos desde DB."""
    from database import db, _fetchall
    try:
        with db() as conn:
            rows = _fetchall(conn,
                "SELECT * FROM model_performance WHERE liga=? ORDER BY id DESC LIMIT 20",
                (liga,))
        return {"rendimiento": rows or []}
    except Exception as e:
        return {"error": str(e)}


def predict_single_avanzado(home, away, liga="liga_mx") -> dict:
    """Predicción única con modelo avanzado."""
    ae = AdvancedEnsemble()
    ae.mlp.load(liga)
    ae.gbm.load(liga)
    return ae.predict(home, away, liga)
