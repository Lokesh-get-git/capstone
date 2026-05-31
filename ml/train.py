from ml.risk_classifier import RiskClassifier

def train_and_save():
    print("Training Risk Classifier...")
    clf = RiskClassifier()
    
    # Train
    metrics = clf.train("synthetic_resume_training.csv")
    
    # Print metrics
    print("\nTraining Metrics:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
    
    # Save
    clf.save("models/risk_model.joblib")
    
    # Feature Importance
    print("\nTop 10 Feature Importances:")
    for feature, weight in clf.get_feature_importance(10):
        print(f"  {feature}: {weight:.4f}")

if __name__ == "__main__":
    train_and_save()