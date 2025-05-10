import httpx
import logging

from app.utils.custom_exceptions import ServerException
from app.utils.retry import retry_async

logger = logging.getLogger(__name__)
from app.utils.cache import get_cached_data, cache_data

@retry_async(max_retries=3, base_delay=1, max_delay=5)
async def fetch_twitter_api_data(username: str):
    """
    Fetch data from Twitter API with retry mechanism and caching
    """
    cache_key = f"twitter_api_data:{username}"
    cached_data = await get_cached_data(cache_key)
    if cached_data:
        logger.debug(f"Using cached data: {cache_key}")
        return cached_data

    api_url = f"https://kota.chaineye.tools/api/plugin/twitter/info?username={username}"

    timeout = httpx.Timeout(30.0, connect=10.0)  # Total timeout 30 seconds, connect timeout 10 seconds
    async with httpx.AsyncClient(timeout=timeout) as client:
        client.headers["user-agent"] = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                                        " (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")

        logger.info(f"Requesting Twitter API: {api_url}")
        response = await client.get(api_url)
        response.raise_for_status()
        data = response.json()

        if "data" not in data:
            raise ServerException(f"Twitter API returns abnormal data structure: {data}")

        await cache_data(cache_key, data["data"])
        return data["data"]
