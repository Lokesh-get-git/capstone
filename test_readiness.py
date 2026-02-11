from ml.readiness_scorer import ReadinessScorer

scorer = ReadinessScorer()
m = scorer.train()
print("MAE:", m["mae"], "RMSE:", m["rmse"])

strong = [
    {"text": "Led a team of 8 engineers reducing failures by 40%", "section": "experience"},
    {"text": "Built CI/CD pipeline with Docker cutting release time by 3x", "section": "experience"},
    {"text": "Developed REST APIs serving 50k daily users using FastAPI", "section": "experience"},
    {"text": "Implemented caching layer using Redis improving response time by 60%", "section": "projects"},
    {"text": "Designed normalized database schema for PostgreSQL", "section": "projects"},
]
weak = [
    {"text": "Responsible for backend maintenance", "section": "experience"},
    {"text": "Helped with various projects", "section": "experience"},
    {"text": "Worked on API development", "section": "experience"},
    {"text": "Assisted in testing activities", "section": "experience"},
    {"text": "Involved in team meetings", "section": "experience"},
]
mixed = [
    {"text": "Built authentication service using JWT tokens", "section": "experience"},
    {"text": "Responsible for code reviews", "section": "experience"},
    {"text": "Developed backend endpoints for order management", "section": "experience"},
    {"text": "Helped with deployment tasks", "section": "experience"},
]

r1 = scorer.predict(strong)
r2 = scorer.predict(weak)
r3 = scorer.predict(mixed)
print(f"Strong: {r1['readiness_score']}/100 ({r1['readiness_level']})")
print(f"Weak:   {r2['readiness_score']}/100 ({r2['readiness_level']})")
print(f"Mixed:  {r3['readiness_score']}/100 ({r3['readiness_level']})")
print(f"Gap:    {r1['readiness_score'] - r2['readiness_score']} points")
