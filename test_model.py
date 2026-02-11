"""Quick test of data generation + model training."""
from ml.synthetic_data import generate_synthetic_dataset
from ml.risk_classifier import RiskClassifier
from ml.feature_builder import build_feature_vector

# Generate and save
df = generate_synthetic_dataset(250)
df.to_csv("synthetic_resume_training.csv", index=False)
print(f"Samples: {len(df)}")
print(f"Balance: {df['label'].value_counts().to_dict()}")

# Train
clf = RiskClassifier()
m = clf.train()
print("\n=== METRICS ===")
for k, v in m.items():
    print(f"  {k}: {v}")

print("\n=== TOP RISK SIGNALS ===")
for name, weight in clf.get_feature_importance(10):
    d = "HIGH" if weight > 0 else "LOW"
    print(f"  {name:30} {weight:+.4f} {d}")

# Predict
tests = [
    {"text": "Led 8 engineers reducing failures by 40%", "section": "experience"},
    {"text": "Responsible for backend maintenance", "section": "experience"},
    {"text": "Implemented REST API with FastAPI", "section": "experience"},
    {"text": "Helped with various projects", "section": "experience"},
    {"text": "Leveraged cutting edge technologies", "section": "experience"},
    {"text": "Built CI/CD pipeline cutting time by 3x", "section": "projects"},
]

print("\n=== PREDICTIONS ===")
for t in tests:
    f = build_feature_vector(t)
    r = clf.predict(f)
    print(f"  {r['risk_label']:10} {r['risk_score']:5.1f}%  {t['text'][:50]}")
