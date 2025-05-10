import asyncio
import logging

import httpx

from app.config import get_config
from app.utils.cache import get_cached_data, cache_data
from app.utils.retry import retry_async

logger = logging.getLogger(__name__)


@retry_async(max_retries=3, base_delay=1, max_delay=5)
async def _request_twitter_api(url: str):
    """
    Send a request to the Twitter API with retry mechanism
    """
    # Try to get data from cache
    cache_key = f"twitter_api:{url}"
    cached_data = await get_cached_data(cache_key)
    if cached_data:
        logger.debug(f"Using cached data: {cache_key}")
        return cached_data
    
    config = get_config()["external_apis"]["twitter"]
    key = config["key"]
    base_url = config["base_url"]
    timeout = httpx.Timeout(30.0, connect=10.0)  # Total timeout 30 seconds, connect timeout 10 seconds
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        client.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        url = base_url + url
        logger.info(f"Requesting Twitter API: {url}")

        client.headers["Authorization"] = "Bearer " + key
        response = await client.get(url)
        response.raise_for_status()

        data = response.json()["data"]
        
        # Cache the result
        await cache_data(cache_key, data)
        
        return data


async def get_screen_name(username: str) -> tuple[str, str]:
    """
    Get the display name by username
    """
    response = await _request_twitter_api(f"/users/by/username/{username}")
    
    return response["name"], response["id"]


if __name__ == '__main__':
    asyncio.run(get_screen_name("AMAZlNGNATURE"))