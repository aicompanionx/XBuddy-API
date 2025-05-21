import asyncio
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def retry_async(max_retries=3, base_delay=1, max_delay=10):
    """
    Asynchronous function retry decorator
    max_retries: Maximum number of retries
    base_delay: Base delay time (seconds)
    max_delay: Maximum delay time (seconds)
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            last_exception = None

            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    retries += 1
                    if retries >= max_retries:
                        logger.error(
                            f"Function {func.__name__} execution failed, has retried {retries} times: {str(e)}"
                        )
                        break

                    # Calculate delay time (exponential backoff strategy)
                    delay = min(base_delay * (2 ** (retries - 1)), max_delay)
                    logger.warning(
                        f"Function {func.__name__} execution failed, will retry in {delay} seconds, has retried {retries} times: {str(e)}"
                    )
                    await asyncio.sleep(delay)

            # If all retries fail, raise the last exception
            raise last_exception

        return wrapper

    return decorator
