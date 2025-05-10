import json

from app.dependencies import get_redis
import logging

logger = logging.getLogger(__name__)

async def get_cached_data(key: str):
    """
    Get data from cache
    """
    async with get_redis() as redis_client:
        cache = await redis_client.get(key)
    if cache:
        logger.debug(f"Get data from cache: {key}")
        return json.loads(cache)
    logger.debug(f"Cache not hit: {key}")
    return None


async def cache_data(key: str, data: dict, expire_seconds: int = 360000):
    """
    Cache data
    """
    async with get_redis() as redis_client:
        await redis_client.set(
            key,
            json.dumps(data),
            ex=expire_seconds
        )
        logger.debug(f"Data cached: {key}, expire in {expire_seconds} seconds")