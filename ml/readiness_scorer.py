import joblib
import os
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from ml.feature_builder import build_feature_matrix

class ReadinessScorer:
    """
    Resume-level readiness score (0–100).
    Aggregates all claim features into a single resume score.
    Uses a neural network (MLP) trained on synthetic data.
    """

    def __init__(self):
        self.model = MLPRegressor(
            hidden_layer_sizes=(64, 32, 16),
            activation="relu",
            max_iter=500,
            random_state=42,
            early_stopping=True,
            validation_fraction=0.15,
        )
        self.scaler = StandardScaler()
        self.feature_names: list = []
        self.is_trained: bool = False

    def _aggregate_features(self, claims: list[dict]) -> dict:
        """
        Convert a LIST of claim feature vectors into ONE resume-level vector.
        Uses: mean, max, min, std, count.
        """
        if not claims:
            return {}

        matrix = build_feature_matrix(claims)
        df = pd.DataFrame(matrix)

        agg = {}
        for col in df.columns:
            agg[f"mean_{col}"] = df[col].mean()
            agg[f"max_{col}"] = df[col].max()
            agg[f"std_{col}"] = df[col].std() if len(df) > 1 else 0

        agg["claim_count"] = len(claims)
        return agg

    def _generate_training_data(self, n_resumes: int = 300) -> pd.DataFrame:
        """Generate synthetic resume-level training data with feature-driven scoring."""
        import random
        random.seed(42)

        from ml.synthetic_data import (
            STRONG_WITH_METRICS, STRONG_NO_METRICS, SHORT_STRONG_CLAIMS,
            WEAK_CLAIMS, BUZZWORD_CLAIMS, MEDIUM_CLAIMS,
            BELIEVABLE_CLAIMS, _fill_template, _fill_simple, SECTIONS
        )

        def _make_claim(kind: str) -> tuple:
            """Returns (claim_dict, quality_weight)."""
            section = random.choice(SECTIONS)
            if kind == "strong":
                if random.random() < 0.5:
                    text = _fill_template(random.choice(STRONG_WITH_METRICS))
                else:
                    text = _fill_simple(random.choice(STRONG_NO_METRICS + SHORT_STRONG_CLAIMS))
                return {"text": text, "section": section}, 1.0
            elif kind == "medium":
                text = _fill_simple(random.choice(MEDIUM_CLAIMS + BELIEVABLE_CLAIMS))
                return {"text": text, "section": section}, 0.5
            elif kind == "weak":
                text = _fill_simple(random.choice(WEAK_CLAIMS))
                return {"text": text, "section": section}, -0.3
            else:  # buzzword
                text = _fill_simple(random.choice(BUZZWORD_CLAIMS))
                return {"text": text, "section": section}, -0.5

        # Quality profiles: (strong%, medium%, weak%, buzzword%)
        profiles = [
            (1.00, 0.00, 0.00, 0.00),   # all strong
            (0.85, 0.15, 0.00, 0.00),   # excellent
            (0.70, 0.20, 0.10, 0.00),   # good
            (0.55, 0.25, 0.15, 0.05),   # above average
            (0.35, 0.30, 0.25, 0.10),   # average
            (0.15, 0.20, 0.45, 0.20),   # below average
            (0.05, 0.10, 0.55, 0.30),   # weak
            (0.00, 0.05, 0.60, 0.35),   # very weak
        ]

        rows = []
        per_profile = n_resumes // len(profiles)

        for strong_pct, med_pct, weak_pct, buzz_pct in profiles:
            for _ in range(per_profile):
                n_claims = random.randint(4, 14)
                claims = []
                weights = []

                for _ in range(n_claims):
                    r = random.random()
                    if r < strong_pct:
                        claim, w = _make_claim("strong")
                    elif r < strong_pct + med_pct:
                        claim, w = _make_claim("medium")
                    elif r < strong_pct + med_pct + weak_pct:
                        claim, w = _make_claim("weak")
                    else:
                        claim, w = _make_claim("buzzword")
                    claims.append(claim)
                    weights.append(w)

                agg = self._aggregate_features(claims)

                # SCORE = computed from actual quality, not random
                avg_quality = sum(weights) / len(weights)  # range: -0.5 to 1.0
                # normalize to 0-100 scale
                raw_score = ((avg_quality + 0.5) / 1.5) * 100
                # bonus for having many claims (resume depth)
                depth_bonus = min(5, (n_claims - 4) * 0.5)
                noise = random.uniform(-4, 4)
                score = max(0, min(100, raw_score + depth_bonus + noise))

                agg["readiness_score"] = round(score, 1)
                rows.append(agg)

        return pd.DataFrame(rows).fillna(0)

    def train(self) -> dict:
        df = self._generate_training_data(800)

        self.feature_names = [c for c in df.columns if c != "readiness_score"]
        X = df[self.feature_names].values
        y = df["readiness_score"].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)

        self.model.fit(X_train, y_train)
        self.is_trained = True

        y_pred = self.model.predict(X_test)
        mae = float(np.mean(np.abs(y_pred - y_test)))
        rmse = float(np.sqrt(np.mean((y_pred - y_test) ** 2)))

        return {
            "mae": round(mae, 2),
            "rmse": round(rmse, 2),
            "samples_train": len(X_train),
            "samples_test": len(X_test),
        }

    def predict(self, claims: list[dict]) -> dict:
        """MLP-based prediction (may overfit on synthetic patterns)."""
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call .train() first.")

        agg = self._aggregate_features(claims)
        X = np.array([[agg.get(f, 0) for f in self.feature_names]])
        X = self.scaler.transform(X)

        score = float(self.model.predict(X)[0])
        score = max(0, min(100, round(score, 1)))

        return {
            "readiness_score": score,
            "readiness_level": self._level(score),
        }

    def predict_with_risk(self, claims: list[dict], risk_classifier) -> dict:
        """
        Grounded readiness score using actual risk classifier predictions.
        This is the PRIMARY scoring method for real resumes.
        """
        from ml.feature_builder import build_feature_vector

        if not claims:
            return {"readiness_score": 0, "readiness_level": "weak", "breakdown": {}}

        risk_probs = []
        has_metrics_count = 0
        has_tech_count = 0

        for claim in claims:
            features = build_feature_vector(claim)
            risk = risk_classifier.predict(features)
            risk_probs.append(risk["risk_probability"])

            # track quality signals
            if features.get("clarity_has_metrics", 0):
                has_metrics_count += 1
            if features.get("sem_num_keywords", 0) > 0:
                has_tech_count += 1

        # --- Core score: inverse of average risk ---
        avg_risk = sum(risk_probs) / len(risk_probs)
        base_score = (1 - avg_risk) * 100

        # --- Penalties ---
        n = len(claims)

        # Penalty: too few claims (thin resume)
        depth_penalty = max(0, (8 - n) * 3) if n < 8 else 0

        # Penalty: no quantified claims (no metrics anywhere)
        metrics_ratio = has_metrics_count / n
        if metrics_ratio < 0.2:
            metrics_penalty = 15
        elif metrics_ratio < 0.4:
            metrics_penalty = 8
        else:
            metrics_penalty = 0

        # Penalty: high variance in claim quality (inconsistent)
        risk_std = float(np.std(risk_probs)) if len(risk_probs) > 1 else 0
        consistency_penalty = min(10, risk_std * 20)

        total_penalty = depth_penalty + metrics_penalty + consistency_penalty
        final_score = max(0, min(100, round(base_score - total_penalty, 1)))

        return {
            "readiness_score": final_score,
            "readiness_level": self._level(final_score),
            "breakdown": {
                "base_score": round(base_score, 1),
                "avg_risk": round(avg_risk, 4),
                "claims_analyzed": n,
                "claims_with_metrics": has_metrics_count,
                "depth_penalty": round(depth_penalty, 1),
                "metrics_penalty": metrics_penalty,
                "consistency_penalty": round(consistency_penalty, 1),
            }
        }

    @staticmethod
    def _level(score: float) -> str:
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "needs_improvement"
        else:
            return "weak"

    def save(self, path: str = "models/readiness_model.joblib"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({"model": self.model, "scaler": self.scaler,
                     "features": self.feature_names}, path)

    @classmethod
    def load(cls, path: str = "models/readiness_model.joblib"):
        data = joblib.load(path)
        instance = cls()
        instance.model = data["model"]
        instance.scaler = data["scaler"]
        instance.feature_names = data["features"]
        instance.is_trained = True
        return instance