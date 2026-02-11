import re
from typing import List, Dict
from nlp.clarity_scorer import score_clarity, ACTION_VERBS
from nlp.keyword_extractor import extractor
from nlp.tokenizer import count_tokens

# =========================================================
# ---- COMMIT 18: TEXTUAL FEATURES (10 features) ----------
# =========================================================

def extract_textual_features(text: str) -> dict:
    words = text.split()
    sentences = re.split(r'[.!?]+', text)
    clean_sentences = [s for s in sentences if s.strip()]

    return {
        "char_count": len(text),
        "word_count": len(words),
        "avg_word_length": round(sum(len(w) for w in words) / max(len(words), 1), 2),
        "sentence_count": len(clean_sentences),
        "words_per_sentence": round(len(words) / max(len(clean_sentences), 1), 2),
        "uppercase_ratio": round(sum(1 for c in text if c.isupper()) / max(len(text), 1), 4),
        "punctuation_count": sum(1 for c in text if c in '.,;:!?'),
        "starts_with_verb": int(words[0].lower() in ACTION_VERBS) if words else 0,
        "ends_with_period": int(text.strip().endswith('.')),
        "has_parentheses": int('(' in text),
    }

# =========================================================
# ---- COMMIT 19: QUANT + ACTION FEATURES (8 features) ----
# =========================================================

def extract_quant_features(text: str) -> dict:
    lower = text.lower()

    # count raw numbers
    numbers = re.findall(r'\d+', text)
    percentages = re.findall(r'\d+%', text)
    dollar_amounts = re.findall(r'\$[\d,]+', text)
    multipliers = re.findall(r'\d+x', lower)

    # action verb analysis
    words = lower.split()
    verb_count = sum(1 for w in words if w in ACTION_VERBS)
    first_word_is_verb = int(words[0] in ACTION_VERBS) if words else 0

    # weak language detection
    weak_phrases = ["responsible for", "helped with", "assisted in", "involved in", "worked on"]
    has_weak_language = int(any(p in lower for p in weak_phrases))

    return {
        "number_count": len(numbers),
        "has_percentage": int(len(percentages) > 0),
        "has_dollar": int(len(dollar_amounts) > 0),
        "has_multiplier": int(len(multipliers) > 0),
        "verb_count": verb_count,
        "first_word_is_verb": first_word_is_verb,
        "has_weak_language": has_weak_language,
        "metric_density": round(len(numbers) / max(len(words), 1), 4),
    }

# =========================================================
# ---- COMMIT 20: STRUCTURAL FEATURES (8 features) --------
# =========================================================
def extract_structural_features(text: str, section: str = "") -> dict:
    lower = text.lower()
    words = text.split()

    # bullet-like structure
    has_bullet = int(text.strip().startswith(('-', '•', '*')))

    # list patterns
    comma_count = text.count(',')
    has_list_structure = int(comma_count >= 2)

    # conjunction chaining
    and_count = lower.count(' and ')

    # clause complexity
    clause_count = len(re.split(r'[,;:]', text))

    # comparison language
    comparison_words = ["improved", "reduced", "increased", "compared", "faster", "better"]
    has_comparison = int(any(w in lower for w in comparison_words))

    # -------- SECTION ONE-HOT ENCODING (VERY IMPORTANT) --------
    section_lower = section.lower()

    return {
        "has_bullet": has_bullet,
        "comma_count": comma_count,
        "has_list_structure": has_list_structure,
        "and_count": and_count,
        "clause_count": clause_count,
        "has_comparison": has_comparison,

        # categorical section features
        "is_experience": int(section_lower == "experience"),
        "is_project": int(section_lower == "projects"),
        "is_summary": int(section_lower == "summary"),
        "is_education": int(section_lower == "education"),
        "is_skills": int(section_lower == "skills"),
    }

# =========================================================
# ---- COMMIT 21: SEMANTIC FEATURES (8 features) ----------
# =========================================================

def extract_semantic_features(text: str) -> dict:
    # keyword extraction
    keywords = extractor.extract_keywords(text)
    num_keywords = sum(len(v) for v in keywords.values())

    has_language = int(len(keywords.get("languages", [])) > 0)
    has_framework = int(len(keywords.get("frameworks", [])) > 0)
    has_database = int(len(keywords.get("databases", [])) > 0)
    has_cloud = int(len(keywords.get("cloud_devops", [])) > 0)
    has_concept = int(len(keywords.get("concepts", [])) > 0)

    # tech stack breadth (how many categories covered)
    tech_breadth = sum(1 for v in keywords.values() if len(v) > 0)

    # token cost (for LLM budgeting later)
    token_count = count_tokens(text)

    return {
        "num_keywords": num_keywords,
        "has_language": has_language,
        "has_framework": has_framework,
        "has_database": has_database,
        "has_cloud": has_cloud,
        "has_concept": has_concept,
        "tech_breadth": tech_breadth,
        "token_count": token_count,
    }

# =========================================================
# ---- UNIFIED FEATURE BUILDER ----------------------------
# =========================================================
def _prefix(d: dict, name: str) -> dict:
    return {f"{name}_{k}": v for k, v in d.items()}


def build_feature_vector(claim: dict) -> Dict:
    text = claim["text"]
    section = claim.get("section", "")

    features = {}

    # prefix every feature group
    features.update(_prefix(extract_textual_features(text), "txt"))
    features.update(_prefix(extract_quant_features(text), "quant"))
    features.update(_prefix(extract_structural_features(text, section), "struct"))
    features.update(_prefix(extract_semantic_features(text), "sem"))

    # clarity scorer
    clarity = score_clarity(text)
    features["clarity_score"] = clarity["score"]
    features["clarity_has_action_verb"] = int(clarity["metrics"]["has_action_verb"])
    features["clarity_has_metrics"] = int(clarity["metrics"]["has_metrics"])
    features["clarity_word_count"] = clarity["metrics"]["word_count"]

    return features


def build_feature_matrix(claims: List[dict]) -> List[Dict]:
    """
    Convert all claims into feature vectors.
    Returns a list of 34-dimensional feature dicts.
    """
    return [build_feature_vector(c) for c in claims]