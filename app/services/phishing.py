import json

from goplus.phishing_site import PushingSite

from app.dependencies import get_redis
from app.schemas.phishing import PhishingData
from app.utils.custom_exceptions import BadRequestException, ServerException
from app.utils.localization import get_message
from app.utils.url_kit import truncate_url_path


async def check_phishing(url: str, lang: str = "zh") -> PhishingData:
    """
    Check if a URL is a phishing website
    """
    # Keep the domain name
    url = truncate_url_path(url, 0)

    # Check if the URL is a valid domain name
    if not url or len(url) < 5:
        raise BadRequestException("Invalid URL format")

    # First, get the cache from redis
    async with get_redis() as redis_client:
        cache = await redis_client.get(f"check_phishing:{url}")

    # If the cache exists, return the cached result directly
    if cache:
        cache_data = json.loads(cache)
        return PhishingData(
            url=url,
            isPhishing=cache_data.get("isPhishing"),
            message=cache_data.get("message"),
        )

    # If the cache does not exist, call the API
    try:
        data = PushingSite(access_token=None).pushing_site_security(url=url)
    except Exception as e:
        raise ServerException(f"Failed to call phishing detection API: {str(e)}")

    # Error
    if data.code != 1:
        result = PhishingData(
            url=url,
            isPhishing=True,
            message=data.message,
        )
    else:
        # Normal
        result = PhishingData(
            url=url,
            isPhishing=False if data.result.phishing_site == 0 else True,
            message=get_message("safe", lang)
            if data.result.phishing_site == 0
            else get_message("danger", lang),
        )

    # Store the result in the cache
    async with get_redis() as redis_client:
        await redis_client.set(
            f"check_phishing:{url}",
            json.dumps({"isPhishing": result.isPhishing, "message": result.message}),
            ex=36000,  # Cache for 10 hours
        )

    return result
