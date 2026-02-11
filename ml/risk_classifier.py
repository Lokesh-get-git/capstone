import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
from sklearn.calibration import CalibratedClassifierCV

class RiskClassifier:
    """
    Predicts if a resume claim is high-risk (weak/vague) or low-risk (strong).
    Trained on our synthetic data. Not a pre-built model — we train it ourselves.
    """

    def __init__(self):
        self.base_model = LogisticRegression(max_iter=1000, random_state=42,class_weight="balanced")
        self.model = None  # will become calibrated model
        self.scaler = StandardScaler()
        self.feature_names: list = []
        self.is_trained: bool = False


    def train(self, csv_path: str = "synthetic_resume_training.csv") -> dict:
        df = pd.read_csv(csv_path)

        # separate features from metadata
        exclude = ["label", "text"]
        self.feature_names = [c for c in df.columns if c not in exclude]

        X = df[self.feature_names].values
        y = df["label"].values

        # train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # scale features
        X_train = self.scaler.fit_transform(X_train)
        X_test = self.scaler.transform(X_test)

        # train
        # ---- Train base model ----
        self.base_model.fit(X_train, y_train)

        # ---- Calibrate probabilities (THIS is the upgrade) ----
        self.model = CalibratedClassifierCV(self.base_model, method="sigmoid", cv=5)
        self.model.fit(X_train, y_train)

        self.is_trained = True


        # evaluate
        y_pred = self.model.predict(X_test)
        report = classification_report(y_test, y_pred, output_dict=True)

        return {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "precision": round(report["1"]["precision"], 4),
            "recall": round(report["1"]["recall"], 4),
            "f1": round(report["1"]["f1-score"], 4),
            "samples_train": len(X_train),
            "samples_test": len(X_test),
        }

    def predict(self, feature_vector: dict) -> dict:
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call .train() first.")

        X = np.array([[feature_vector.get(f, 0) for f in self.feature_names]])
        X = self.scaler.transform(X)

        proba = self.model.predict_proba(X)[0]
        label = int(self.model.predict(X)[0])
        risk_prob = float(proba[1])

        # convert probability → human score
        risk_score = round(risk_prob * 100, 1)

        if risk_prob > 0.75:
            level = "very_high"
        elif risk_prob > 0.60:
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
        }


    def get_feature_importance(self, top_n: int = 10) -> list:
        """Explainability — which features drive the risk score."""
        weights = self.base_model.coef_[0]
        importance = sorted(
            zip(self.feature_names, weights),
            key=lambda x: abs(x[1]), reverse=True
        )
        return importance[:top_n]