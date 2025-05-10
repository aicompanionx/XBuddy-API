import httpx
import logging

from app.utils.retry import retry_async
from app.utils.cache import get_cached_data, cache_data

logger = logging.getLogger(__name__)


@retry_async(max_retries=3, base_delay=1, max_delay=5)
async def fetch_rename_history_api(api_url: str):
    """
    Request rename history API with retry mechanism and caching
    """
    # Try to get data from cache
    cache_key = f"rename_history:{api_url}"
    cached_data = await get_cached_data(cache_key)
    if cached_data:
        logger.debug(f"Using cached data: {cache_key}")
        return cached_data
        
    timeout = httpx.Timeout(30.0, connect=10.0)  # Total timeout 30 seconds, connect timeout 10 seconds
    async with httpx.AsyncClient(timeout=timeout) as client:
        client.headers[
            "user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"

        logger.info(f"Requesting rename history API: {api_url}")
        response = await client.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Cache the result
        await cache_data(cache_key, data)
        
        return data