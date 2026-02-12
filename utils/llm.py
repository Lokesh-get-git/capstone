import os
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from utils.logger import get_logger

logger = get_logger(__name__)

_LLM_INSTANCE = None

def get_llm(model_name: str = "llama-3.1-8b-instant", temperature: float = 0.1):
    """
    Returns a configured ChatGroq instance.
    Uses singleton pattern for efficiency (though langchain clients are lightweight).
    """
    global _LLM_INSTANCE
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        logger.error("GROQ_API_KEY not found in config or env vars.")
        raise ValueError("GROQ_API_KEY not set")

    if _LLM_INSTANCE is None:
        logger.info(f"Initializing Groq LLM: {model_name}")
        _LLM_INSTANCE = ChatGroq(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
            max_retries=2,
            # rate_limit handling is built-in to some extent
        )
    
    return _LLM_INSTANCE
