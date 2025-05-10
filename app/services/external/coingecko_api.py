import logging

import httpx

from app.config import get_config
from app.schemas.token import TokenDetailData
from app.utils.cache import get_cached_data, cache_data
from app.utils.custom_exceptions import ExternalApiException
from app.utils.retry import retry_async

logger = logging.getLogger(__name__)

@retry_async(max_retries=3, base_delay=1, max_delay=5)
async def _request_coingeko_api(url: str):
    """
    Sends a request to Coingecko API with retry mechanism
    """
    # Try to get data from cache
    cache_key = f"coingecko_api:{url}"
    cached_data = await get_cached_data(cache_key)
    if cached_data:
        logger.debug(f"Using cached data: {cache_key}")
        return cached_data

    config = get_config()["external_apis"]["coingecko"]
    key = config["key"]
    base_url = config["base_url"]
    timeout = httpx.Timeout(30.0, connect=10.0)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            client.headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "x-cg-demo-api-key": key,
                "accept": 'application/json'
            }

            full_url = base_url + url
            logger.info(f"Requesting Coingecko API: {full_url}")

            response = await client.get(full_url)
            response.raise_for_status()

            data = response.json()

            # Cache the result
            await cache_data(cache_key, data)

            return data
    except Exception as e:
        raise ExternalApiException(f"Failed to request Coingecko API: {e}")

async def get_token_desc(chain: str, ca: str) -> TokenDetailData:
    """
    Gets token information
    """
    try:
        if chain.lower() == "bsc":
            chain = "binance-smart-chain"
        elif chain.lower() == "sol":
            chain = "solana"

        if chain not in ["solana", "binance-smart-chain", "base", "ethereum"]:
            raise ExternalApiException(f'Unsupported chain `{chain}`, only supports ["solana", "binance-smart-chain", "base", "ethereum"]')

        response: dict = await _request_coingeko_api(f"/coins/{chain}/contract/{ca}")

        logo_url = response.get("image", {}).get("large", "")

        # Safely get Twitter URL
        twitter_url = ""
        if response.get("links") and response["links"].get("twitter_screen_name"):
            twitter_url = f"https://x.com/{response['links']['twitter_screen_name']}"

        # Safely get categories
        categories = response.get("categories", [])
        if categories is None:
            categories = []

        # Safely get description
        description = ""
        if response.get("description") and response["description"].get("en"):
            description = response["description"]["en"]

        token_detail = TokenDetailData(
            symbol=response.get("symbol", ""),
            id=response.get("id", ""),
            name=response.get("name", ""),
            platform=response.get("asset_platform_id", ""),
            categories=categories,
            description=description,
            public_notice=response.get("public_notice", ""),
            twitter_url=twitter_url,
            logo_url=logo_url
        )
        
        return token_detail
    except Exception as e:
        logger.error(f"Failed to get token information: {str(e)}")
        raise ExternalApiException(f"Failed to get token information: {str(e)}")