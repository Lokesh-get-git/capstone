import random
import re
import pandas as pd
from ml.feature_builder import build_feature_vector

random.seed(42)

# =========================================================
# CLAIM TEMPLATES — organized by RISK LEVEL
# =========================================================

# ------- LOW RISK: Strong claims WITH metrics -------
STRONG_WITH_METRICS = [
    "Led a team of {n} engineers to redesign the {system}, reducing {metric} by {pct}%",
    "Built a {system} processing {n}+ requests per second using {tech}",
    "Implemented {tech} integration reducing deployment time from {n} days to {n2} hours",
    "Optimized {system} queries improving response time by {pct}%",
    "Developed REST APIs serving {n},000 daily users using {tech}",
    "Automated {system} using {tech}, cutting manual effort by {pct}%",
    "Migrated {system} to {tech}, reducing infrastructure costs by {pct}%",
    "Achieved {pct}% test coverage for {system} using {tech}",
    "Scaled {system} from {n} to {n2}00 concurrent users using {tech}",
    "Reduced {system} downtime by {pct}% through {tech} monitoring",
]
SHORT_STRONG_CLAIMS = [
    "Reduced latency by 40%",
    "Automated deployments using Docker",
    "Optimized SQL queries improving performance",
    "Built REST API using FastAPI",
    "Scaled service to 50k users",
    "Implemented caching with Redis",
    "Improved response time by 3x",
    "Deployed application on AWS",
    "Designed database schema for PostgreSQL",
    "Wrote unit tests achieving 90% coverage"
]

# ------- LOW RISK: Strong claims WITHOUT metrics -------
# (prevents model from learning "has numbers = low risk" shortcut)
STRONG_NO_METRICS = [
    "Designed caching strategy for {system} using Redis",
    "Refactored authentication service improving maintainability",
    "Implemented retry logic and circuit breaker pattern in {system}",
    "Wrote comprehensive integration tests for {system}",
    "Migrated backend service from Flask to FastAPI",
    "Introduced structured logging across all microservices",
    "Containerized entire application stack using Docker Compose",
    "Designed normalized database schema for {system}",
    "Implemented event-driven architecture using Kafka for {system}",
    "Set up automated CI pipeline with GitHub Actions for {system}",
    "Built real-time notification service using WebSockets",
    "Implemented role-based access control for {system}",
    "Created reusable component library for frontend dashboard",
    "Architected data pipeline for ETL processing using {tech}",
    "Implemented caching layer using Redis for {system}",
]

# ------- HIGH RISK: Weak/vague claims -------
WEAK_CLAIMS = [
    "Responsible for {system} maintenance",
    "Helped with {tech} related tasks",
    "Worked on various {system} projects",
    "Assisted in {system} development",
    "Involved in {tech} implementation",
    "Participated in {system} activities",
    "Contributed to {system} efforts",
    "Supported the team with {system} work",
    "Handled {system} duties",
    "Managed {system} responsibilities",
    "Tasked with {system} operations",
    "Part of the team working on {system}",
]

# ------- HIGH RISK: Buzzword stuffing -------
BUZZWORD_CLAIMS = [
    "Worked on scalable microservices architecture using {tech} and Docker",
    "Implemented distributed system using cloud native technologies and {tech}",
    "Built highly scalable platform leveraging modern DevOps tools",
    "Designed enterprise level solution using best practices and {tech}",
    "Developed AI powered system using machine learning and big data",
    "Utilized cutting edge technologies including {tech} and {tech2}",
    "Leveraged agile methodologies to deliver {system} solutions",
    "Employed industry standard frameworks for {system} development",
    "Applied best-in-class {tech} solutions for {system}",
    "Spearheaded transformational initiatives across {system}",
]

# ------- MEDIUM RISK: Decent but not great -------
MEDIUM_CLAIMS = [
    "Developed {system} using {tech}",
    "Built {tool} for {system} automation",
    "Created {system} module using {tech} and {tech2}",
    "Designed {system} architecture for {tool}",
    "Implemented {tech} solution for {system}",
    "Integrated {tech} with {system}",
    "Added {tech} support to existing {system}",
    "Updated {system} backend to use {tech}",
]

# ------- BELIEVABLE CLAIMS (medium, realistic) -------
BELIEVABLE_CLAIMS = [
    "Implemented REST API using FastAPI and PostgreSQL",
    "Built authentication service using JWT tokens",
    "Created dashboard using React and Chart.js",
    "Integrated Stripe payment gateway",
    "Developed backend endpoints for order management",
    "Designed database schema for inventory system",
    "Added Redis caching layer to API",
    "Containerized application with Docker",
    "Wrote unit tests using PyTest",
    "Set up logging and monitoring for services",
]

# =========================================================
# WORD POOLS
# =========================================================

TECHS = [
    "Python", "FastAPI", "React", "Docker", "PostgreSQL",
    "Redis", "AWS", "Kubernetes", "Flask", "TensorFlow",
    "Django", "Node.js", "TypeScript", "MongoDB"
]

SYSTEMS = [
    "payment processing", "authentication service",
    "data pipeline", "API gateway", "search engine",
    "recommendation system", "analytics dashboard",
    "notification service", "order management", "inventory tracking"
]

TOOLS = [
    "CI/CD", "monitoring", "logging", "caching",
    "deployment", "alerting", "backup", "testing"
]

METRICS = ["latency", "errors", "failures", "processing time", "response time"]

SECTIONS = ["experience", "projects"]


# =========================================================
# NOISE INJECTION
# =========================================================

def add_noise(text: str) -> str:
    """Simulate real resume imperfections."""
    if random.random() < 0.15:
        text = text.lower()
    if random.random() < 0.15:
        text = text.replace(",", "")
    if random.random() < 0.20:
        text = text.replace(" using ", " with ")
    if random.random() < 0.15:
        text = text.rstrip(".")
    if random.random() < 0.10:
        text = text.replace(" ", "  ")
    return text

def synonym_variation(text: str) -> str:
    replacements = {
        "Built": random.choice(["Created", "Developed", "Implemented"]),
        "Led": random.choice(["Managed", "Directed", "Oversaw"]),
        "Reduced": random.choice(["Decreased", "Lowered", "Cut"]),
        "Improved": random.choice(["Enhanced", "Optimized", "Boosted"]),
        "Designed": random.choice(["Architected", "Planned", "Engineered"]),
    }
    for k, v in replacements.items():
        if random.random() < 0.4:
            text = text.replace(k, v)
    return text


# =========================================================
# TEMPLATE FILLER
# =========================================================

def _fill_template(template: str) -> str:
    text = template.format(
        n=random.randint(3, 20),
        n2=random.randint(1, 5),
        pct=random.randint(15, 80),
        tech=random.choice(TECHS),
        tech2=random.choice(TECHS),
        system=random.choice(SYSTEMS),
        tool=random.choice(TOOLS),
        metric=random.choice(METRICS)
    )
    return synonym_variation(add_noise(text))


def _fill_simple(template: str) -> str:
    """For templates that only use {system}/{tech}/{tool}."""
    text = template.format(
        system=random.choice(SYSTEMS),
        tech=random.choice(TECHS),
        tech2=random.choice(TECHS),
        tool=random.choice(TOOLS),
    )
    return synonym_variation(add_noise(text))


# =========================================================
# DATASET GENERATOR
# =========================================================

def generate_synthetic_dataset(n_per_class: int = 200) -> pd.DataFrame:
    """
    Generates balanced labeled training data.
    label 0 = strong (low risk)
    label 1 = weak (high risk)
    """
    rows = []

    for _ in range(n_per_class):
        section = random.choice(SECTIONS)

        # ===== LOW RISK (label=0) =====

        # 50% strong with metrics, 50% strong without metrics
        if random.random() < 0.5:
            text = _fill_template(random.choice(STRONG_WITH_METRICS))
        else:
            text = _fill_simple(random.choice(STRONG_NO_METRICS))

        claim = {"text": text, "section": section}
        features = build_feature_vector(claim)
        features["label"] = 0
        features["text"] = text
        rows.append(features)

        # ===== HIGH RISK (label=1) =====

        # 60% weak claims, 40% buzzword stuffing
        if random.random() < 0.6:
            text = _fill_simple(random.choice(WEAK_CLAIMS))
        else:
            text = _fill_simple(random.choice(BUZZWORD_CLAIMS))

        claim = {"text": text, "section": section}
        features = build_feature_vector(claim)
        features["label"] = 1
        features["text"] = text
        rows.append(features)

        # ===== MEDIUM (label varies) =====

        if random.random() < 0.5:
            text = _fill_simple(random.choice(MEDIUM_CLAIMS))
        else:
            text = random.choice(BELIEVABLE_CLAIMS)
            text = add_noise(text)

        claim = {"text": text, "section": section}
        features = build_feature_vector(claim)
        # medium claims: slight bias toward low risk (they ARE decent)
        features["label"] = 0 if random.random() < 0.6 else 1
        features["text"] = text
        rows.append(features)
        # Short strong claims (VERY IMPORTANT)
        text = random.choice(SHORT_STRONG_CLAIMS)
        claim = {"text": text, "section": random.choice(["experience", "projects"])}
        features = build_feature_vector(claim)
        features["label"] = 0  # LOW risk
        features["text"] = text
        rows.append(features)

    df = pd.DataFrame(rows)

    # shuffle to prevent ordering bias
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    return df


# =========================================================
# CLI ENTRY
# =========================================================

if __name__ == "__main__":
    df = generate_synthetic_dataset(250)

    print(f"\nGenerated {len(df)} samples")
    print(f"Features: {len(df.columns) - 2}")
    print(f"\nLabel distribution:\n{df['label'].value_counts()}")
    print(f"\nClass balance: {df['label'].value_counts(normalize=True).round(3).to_dict()}")

    df.to_csv("synthetic_resume_training.csv", index=False)
    print("\nSaved to: synthetic_resume_training.csv")
