import re
from typing import Dict, List, Set

TECH_KNOWLEDGE_BASE = {
    "languages": {
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", 
        "swift", "kotlin", "ruby", "php", "sql", "html", "css", "bash", "shell"
    },
    "frameworks": {
        "fastapi", "django", "flask", "react", "vue", "angular", "spring", "spring boot",
        "express", "next.js", "node.js", "pytorch", "tensorflow", "scikit-learn", "pandas",
        "numpy", "hibernate", ".net", "dotnet"
    },
    "databases": {
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb", 
        "oracle", "sql server", "cassandra", "sqlite", "firebase"
    },
    "cloud_devops": {
        "aws", "azure", "gcp", "docker", "kubernetes", "k8s", "terraform", "jenkins",
        "gitlab ci", "github actions", "circleci", "prometheus", "grafana", "linux"
    },
    "concepts": {
        "ci/cd", "rest api", "graphql", "microservices", "machine learning", "distributed systems",
        "agile", "scrum", "tdd", "unit testing", "system design", "cloud computing"
    }
}
ALIASES = {
    "ml": "machine learning",
    "restful api": "rest api",
    "rest apis": "rest api",
    "rest services": "rest api",
    "k8s": "kubernetes",
    "postgres": "postgresql",
    "psql": "postgresql",
    "nodejs": "node.js",
    "dockerized": "docker",
    "containerized": "docker",
    "ci cd": "ci/cd",
}

class TechKeywordExtractor:
    def __init__(self):
        self.patterns = self._compile_patterns()

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        patterns = {}
        for category, terms in TECH_KNOWLEDGE_BASE.items():
            # specific regex to match "Go" but not "go home"
            # boundaries \b are critical
            regex_list = [re.escape(term) for term in terms]
            # Special handling for C++ (escape +)
            pattern_str = r'\b(' + '|'.join(regex_list) + r')\b'
            # Case insensitive
            patterns[category] = re.compile(pattern_str, re.IGNORECASE)
        return patterns

    def extract_keywords(self, text: str) -> Dict[str, List[str]]:
        text = text.lower()

        # --- normalization step ---
        for alias, canonical in ALIASES.items():
            text = text.replace(alias, canonical)

        found = {}
        for category, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                found[category] = list(set(m.lower() for m in matches))

        return found


# Singleton instance
extractor = TechKeywordExtractor()