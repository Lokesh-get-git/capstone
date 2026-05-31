import os
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from utils.logger import get_logger

logger = get_logger(__name__)

def get_llm(model_name: str = "llama-3.1-8b-instant", temperature: float = 0.1) -> ChatGroq:
    """
    Returns a configured ChatGroq instance.
    Creates a new instance per call so each agent gets its requested temperature.
    """
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        logger.error("GROQ_API_KEY not found in config or env vars.")
        raise ValueError("GROQ_API_KEY not set")

    logger.info(f"Initializing Groq LLM: {model_name} (temp={temperature})")
    return ChatGroq(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
        max_retries=2,
    )
