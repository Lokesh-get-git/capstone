import time
import functools
from utils.logger import get_logger

logger = get_logger(__name__)

def retry_on_exception(retries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    Retry decorator for external API calls (LLMs, Search).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{retries} failed for {func.__name__}: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            logger.error(f"All {retries} attempts failed for {func.__name__}")
            raise last_exception
            
        return wrapper
    return decorator
