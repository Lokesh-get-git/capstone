import re
from typing import Dict, List, Set
TECH_KNOWLEDGE_BASE = {
    "languages": {
        "python","java","javascript","typescript","c++","c#","go","rust",
        "swift","kotlin","ruby","php","sql","html","css","bash","shell"
    },

    "frameworks": {
        "fastapi","django","flask","react","vue","angular","spring","spring boot",
        "express","next.js","node.js",".net","dotnet",
        "pytorch","tensorflow","scikit-learn","xgboost",
        "pandas","numpy","hibernate","langchain"
    },

    "databases": {
        "postgresql","mysql","mongodb","redis","elasticsearch","dynamodb",
        "oracle","sql server","cassandra","sqlite","firebase",
        "snowflake","timescaledb"
    },

    "cloud_devops": {
        "aws","azure","gcp","docker","kubernetes","k8s","terraform","jenkins",
        "github actions","gitlab ci","circleci",
        "prometheus","grafana","linux",
        "nginx","airflow"
    },

    "concepts": {
        "ci/cd","rest api","graphql","microservices",
        "machine learning","deep learning","distributed systems",
        "agile","scrum","tdd","unit testing",
        "system design","cloud computing",
        "data pipeline","etl","feature engineering"
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
def _normalize_for_matching(text: str) -> str:
    """
    Prepare resume text for keyword matching.
    Removes punctuation that breaks regex boundaries.
    """
    text = text.lower()

    # remove punctuation around words
    text = re.sub(r'[()\[\],.;:]', ' ', text)

    # normalize common variations
    replacements = {
        "nodejs": "node.js",
        "reactjs": "react",
        "nextjs": "next.js",
        "postgres": "postgresql",
        "k8s": "kubernetes",
        "ci cd": "ci/cd",
    }

    for bad, good in replacements.items():
        text = text.replace(bad, good)

    return text

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
        # normalize punctuation & spacing
        text = _normalize_for_matching(text)

        # apply alias canonicalization SAFELY
        for alias, canonical in ALIASES.items():
            text = re.sub(rf'\b{re.escape(alias)}\b', canonical, text)

        found = {}
        for category, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                found[category] = sorted(set(m.lower() for m in matches))

        return found



# Singleton instance
extractor = TechKeywordExtractor()