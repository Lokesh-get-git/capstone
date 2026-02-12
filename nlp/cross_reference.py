from nlp.keyword_extractor import extractor
from nlp.ontology import get_implied_skills
from typing import Dict, List

def cross_reference_claims(claims: List[dict]) -> Dict:
    """
    Cross-reference extracted keywords across all claims.
    Detect inconsistencies and gaps.
    """
    # Step 1: Collect ALL keywords from all claims
    all_keywords = set()
    claim_keywords = []

    for claim in claims:
        kw = extractor.extract_keywords(claim["text"])
        flat = set()
        for words in kw.values():
            flat.update(words)
        implied_local = get_implied_skills(flat)
        local_gaps = implied_local - flat
        claim_keywords.append({
                "claim": claim["text"],
                "keywords": kw,
                "flat": flat,
                "implied": implied_local,
                "gaps": local_gaps
            })

        all_keywords.update(flat)
        
    # Step 2: Expand with ontology
    implied = get_implied_skills(all_keywords)

    # Step 3: Find gaps — keywords implied but never explicitly mentioned
    gaps = implied - all_keywords

    return {
        "explicit_skills": sorted(all_keywords),
        "implied_skills": sorted(set(implied)),
        "potential_gaps": sorted(gaps),
        "per_claim": claim_keywords
    }