import tiktoken
import string
encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

def truncate_text(text: str, max_tokens: int) -> str:
    tokens = encoding.encode(text)
    if len(tokens) > max_tokens:
        return encoding.decode(tokens[:max_tokens])
    return text

def clean_text_for_tfidf(text: str) -> str:
    # Lowercase, remove punctuation, keep only alpha-numeric
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text