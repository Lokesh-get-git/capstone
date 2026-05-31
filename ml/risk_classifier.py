import os
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


class RiskClassifier:
    """
    Predicts if a resume claim is high-risk (weak/vague) or low-risk (strong).
    Trained on our synthetic data. Not a pre-built model

    - Trains multiple model families and selects the best on a validation split.
    - Calibrates probabilities for more reliable risk scores.
    - Learns an operating threshold from validation data (instead of fixed 0.50).
    """

    def __init__(self):
        self.candidate_models = {
            "logreg": Pipeline(
                steps=[
                    ("scaler", StandardScaler()),
                    (
                        "model",
                        LogisticRegression(
                            max_iter=2000,
                            random_state=42,
                            class_weight="balanced",
                        ),
                    ),
                ]
            ),
            "rf": RandomForestClassifier(
                n_estimators=350,
                max_depth=10,
                min_samples_leaf=2,
                random_state=42,
                class_weight="balanced_subsample",
            ),
        }

        self.base_model = None
        self.model = None
        self.feature_names: List[str] = []
        self.is_trained: bool = False
        self.model_name: str = ""
        self.decision_threshold: float = 0.50
        # Backward-compatibility for legacy artifacts that stored an external scaler.
        self.input_scaler = None

    def _select_best_model(self, X_train, y_train, X_val, y_val):
        best_name = None
        best_model = None
        best_score = -1.0

        for name, model in self.candidate_models.items():
            candidate = clone(model)
            candidate.fit(X_train, y_train)
            val_pred = candidate.predict(X_val)

            # Balanced objective: favor recall improvements without collapsing precision.
            val_f1 = f1_score(y_val, val_pred, zero_division=0)
            val_bal_acc = balanced_accuracy_score(y_val, val_pred)
            composite = 0.65 * val_f1 + 0.35 * val_bal_acc

            if composite > best_score:
                best_score = composite
                best_name = name
                best_model = candidate

        return best_name, best_model


    def _augment_training_data(self, X, y, noise_std: float = 0.03, copies: int = 1):
        """Feature-space jitter to reduce overfitting to synthetic templates."""
        if copies <= 0:
            return X, y

        rng = np.random.default_rng(42)
        X_aug = [X]
        y_aug = [y]

        for _ in range(copies):
            jitter = rng.normal(loc=0.0, scale=noise_std, size=X.shape)
            X_noisy = X.astype(float) + jitter
            # Keep naturally non-negative feature groups valid.
            X_noisy = np.clip(X_noisy, a_min=0.0, a_max=None)
            X_aug.append(X_noisy)
            y_aug.append(y)

        return np.vstack(X_aug), np.concatenate(y_aug)

    @staticmethod
    def _find_best_threshold(y_true, probas) -> float:
        best_threshold = 0.50
        best_score = -1.0

        for threshold in np.arange(0.30, 0.71, 0.02):
            pred = (probas >= threshold).astype(int)
            f1 = f1_score(y_true, pred, zero_division=0)
            rec = recall_score(y_true, pred, zero_division=0)
            score = 0.8 * f1 + 0.2 * rec
            if score > best_score:
                best_score = score
                best_threshold = float(round(threshold, 2))

        return best_threshold

    def train(self, csv_path: str = "synthetic_resume_training.csv") -> Dict[str, float]:
        df = pd.read_csv(csv_path)

        # separate features from metadata
        exclude = ["label", "text"]
        self.feature_names = [c for c in df.columns if c not in exclude]

        X = df[self.feature_names].values
        y = df["label"].values

        # 60/20/20 split for train/validation/test
        X_train_full, X_test, y_train_full, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_train_full,
            y_train_full,
            test_size=0.25,
            random_state=42,
            stratify=y_train_full,
        )

        X_train_aug, y_train_aug = self._augment_training_data(X_train, y_train, noise_std=0.02, copies=1)
        self.model_name, self.base_model = self._select_best_model(X_train_aug, y_train_aug, X_val, y_val)

        # ---- Calibrate probabilities (THIS is the upgrade) ----
        # Calibrate chosen model for probability reliability.
        self.model = CalibratedClassifierCV(self.base_model, method="sigmoid", cv=5)
        X_train_full_aug, y_train_full_aug = self._augment_training_data(X_train_full, y_train_full, noise_std=0.02, copies=1)
        self.model.fit(X_train_full_aug, y_train_full_aug)

        # Threshold tuning on validation split using calibrated probabilities.
        val_probs = self.model.predict_proba(X_val)[:, 1]
        self.decision_threshold = self._find_best_threshold(y_val, val_probs)

        self.is_trained = True
        self.input_scaler = None

        test_probs = self.model.predict_proba(X_test)[:, 1]
        y_pred = (test_probs >= self.decision_threshold).astype(int)


        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

        return {
            "model": self.model_name,
            "threshold": self.decision_threshold,
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "balanced_accuracy": round(balanced_accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
            "f1": round(report["1"]["f1-score"], 4),
            "roc_auc": round(roc_auc_score(y_test, test_probs), 4),
            "samples_train": len(X_train_full),
            "samples_test": len(X_test),
        }

    def predict(self, feature_vector: Dict) -> Dict[str, float]:
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call .train() first.")


        X = np.array([[feature_vector.get(f, 0) for f in self.feature_names]], dtype=float)
        if self.input_scaler is not None:
            X = self.input_scaler.transform(X)


        risk_prob = float(self.model.predict_proba(X)[0][1])
        label = int(risk_prob >= self.decision_threshold)

        # convert probability → human score
        risk_score = round(risk_prob * 100, 1)


        if risk_prob > 0.80:
            level = "very_high"
        elif risk_prob > 0.65:
            level = "high"
        elif risk_prob > 0.45:
            level = "medium"
        elif risk_prob > 0.25:
            level = "low"
        else:
            level = "very_low"

        return {
            "risk_label": level,
            "risk_score": risk_score,
            "risk_probability": round(risk_prob, 4),
            "predicted_class": label,
            "decision_threshold": self.decision_threshold,
            "model": self.model_name,
        }


    def get_feature_importance(self, top_n: int = 10) -> list:
        """Explainability — which features drive the risk score."""
        
        # Pipeline(logreg)
        if hasattr(self.base_model, "named_steps") and "model" in self.base_model.named_steps:
            model = self.base_model.named_steps["model"]
            if hasattr(model, "coef_"):
                weights = model.coef_[0]
                importance = sorted(
                    zip(self.feature_names, weights),
                    key=lambda x: abs(x[1]),
                    reverse=True,
                )
                return importance[:top_n]

        # Tree models
        if hasattr(self.base_model, "feature_importances_"):
            weights = self.base_model.feature_importances_
            importance = sorted(
                zip(self.feature_names, weights), key=lambda x: x[1], reverse=True
            )
            return importance[:top_n]

        # Linear models
        if hasattr(self.base_model, "coef_"):
            weights = self.base_model.coef_[0]
            importance = sorted(
                zip(self.feature_names, weights),
                key=lambda x: abs(x[1]),
                reverse=True,
            )
            return importance[:top_n]

        return []

    def save(self, path: str = "models/risk_model.joblib"):
        """Save trained model to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)

        joblib.dump(
            {
                "model": self.model,
                "features": self.feature_names,
                "base_model": self.base_model,
                "model_name": self.model_name,
                "decision_threshold": self.decision_threshold,
                "input_scaler": self.input_scaler,
            },
            path,
        )
        print(f"Model saved to {path}")

    @classmethod
    def load(cls, path: str = "models/risk_model.joblib"):
        """Load trained model from disk."""
        data = joblib.load(path)
        instance = cls()
        instance.model = data["model"]

        instance.feature_names = data["features"]
        instance.base_model = data.get("base_model")
        instance.model_name = data.get("model_name", "")
        instance.decision_threshold = data.get("decision_threshold", 0.50)
        instance.input_scaler = data.get("input_scaler", data.get("scaler"))

        if not instance.model_name and instance.base_model is not None:
            if hasattr(instance.base_model, "named_steps"):
                instance.model_name = "logreg" if "model" in instance.base_model.named_steps else type(instance.base_model).__name__
            else:
                instance.model_name = type(instance.base_model).__name__

        instance.is_trained = True
        return instance