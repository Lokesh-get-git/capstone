

SKILL_ONTOLOGY = {
    "django": ["python", "backend"],
    "flask": ["python", "backend"],
    "fastapi": ["python", "backend", "api"],
    "react": ["javascript", "frontend"],
    "angular": ["javascript", "typescript", "frontend"],
    "spring": ["java", "backend"],
    "spring boot": ["java", "backend"],
    "kubernetes": ["docker", "devops", "cloud"],
    "terraform": ["devops", "cloud"],
    "pytorch": ["python", "machine learning"],
    "tensorflow": ["python", "machine learning"],
    "scikit-learn": ["python", "machine learning"],
    "pandas": ["python", "data"],
    "next.js": ["react", "javascript", "frontend"],
    "node.js": ["javascript", "backend"],
}
SKILL_ONTOLOGY.update({

    # API knowledge
    "api": ["http", "rest"],
    "rest": ["http methods", "status codes", "idempotency"],

    # Backend knowledge
    "backend": ["database design", "authentication", "caching"],

    # Databases
    "postgresql": ["sql", "indexes", "transactions"],
    "mysql": ["sql", "indexes", "transactions"],
    "mongodb": ["nosql", "indexing"],

    # DevOps
    "docker": ["containers"],
    "kubernetes": ["containers", "orchestration"],

    # ML
    "machine learning": ["supervised learning", "overfitting", "evaluation metrics"],
    "scikit-learn": ["machine learning"],
    "pytorch": ["neural networks"],
    "tensorflow": ["neural networks"],
})


def get_implied_skills(explicit_skills: set) -> set:
    """
    Expand skills transitively.
    fastapi -> python -> programming -> ...
    """
    expanded = set(explicit_skills)
    queue = list(explicit_skills)

    while queue:
        skill = queue.pop()

        if skill in SKILL_ONTOLOGY:
            for implied in SKILL_ONTOLOGY[skill]:
                if implied not in expanded:
                    expanded.add(implied)
                    queue.append(implied)

    return expanded
