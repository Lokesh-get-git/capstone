import re
from nlp.tokenizer import count_tokens

ACTION_VERBS = {
    "led", "built", "created", "designed", "developed", 
    "implemented", "optimized", "reduced", "increased"
}

def score_clarity(text: str) -> dict:
    """
    Heuristic score (0.0 to 1.0) for claim clarity.
    """
    word_count = len(text.split())
    lower_text = text.lower()
    
    # 1. Length Score (Ideal: 15-40 tokens)
    if word_count < 5: length_score = 0.2
    elif word_count < 15: length_score = 0.5
    elif word_count < 40: length_score = 1.0
    else: length_score = 0.8 # Too verbose
    
    # 2. Action Verb Score
    # Check if first word is a strong verb
    words = lower_text.split()[:4]  # check first few words
    verb_score = 1.0 if any(w in ACTION_VERBS for w in words) else 0.0
    
    # 3. Quantitative Score
    # Look for %, $, or digits
    has_numbers = bool(re.search(r'\d+%|\$\d+|\d+[kKmM]?|\d+\s*(ms|sec|s|x)', lower_text))

    quant_score = 1.0 if has_numbers else 0.0
    
    # Weighted Average
    final_score = (length_score * 0.25) + (verb_score * 0.25) + (quant_score * 0.5)

    
    return {
        "score": round(final_score, 2),
        "metrics": {
            "word_count": word_count,
            "has_action_verb": verb_score == 1.0,
            "has_metrics": has_numbers
        }
    }