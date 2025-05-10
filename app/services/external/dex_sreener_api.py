import logging
import httpx

from app.config import get_config
from app.utils.cache import get_cached_data, cache_data
from app.schemas.token import TokenInfo, TokenPairsData
from app.utils.custom_exceptions import ServerException
from app.utils.retry import retry_async

logger = logging.getLogger(__name__)


@retry_async(max_retries=3, base_delay=1, max_delay=5)
async def _request_dex_api(url: str):
    """
    Send a request to the DEX API with retry mechanism
    """
    # Try to get data from cache
    cache_key = f"dex_api:{url}"
    cached_data = await get_cached_data(cache_key)
    if cached_data:
        logger.debug(f"Using cached data: {cache_key}")
        return cached_data
        
    config = get_config()["external_apis"]["dex"]
    base_url = config["base_url"]
    timeout = httpx.Timeout(30.0, connect=10.0)  # Total timeout 30 seconds, connect timeout 10 seconds
    async with httpx.AsyncClient(timeout=timeout) as client:
        client.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        url = base_url + url
        logger.info(f"Requesting DEX API: {url}")

        response = await client.get(url)
        response.raise_for_status()

        data = response.json()
        
        # Cache the result
        await cache_data(cache_key, data)
        
        return data


async def get_pairs_base(chain: str,  pair_address: str) -> TokenPairsData:
    """
    Get token information by pair address
    """
    logger.debug(f"Starting to get pair information: {pair_address}")
    response = await _request_dex_api(f"/latest/dex/pairs/{chain}/{pair_address}")

    pair_datas = response["pairs"]

    if pair_datas is None:
        raise ServerException("Failed to get pool related information, please check if it is a pair address")

    pair_data = pair_datas[0]

    # Build TokenInfo object
    token_info = TokenInfo(
        ca=pair_data["baseToken"]["address"],
        name=pair_data["baseToken"]["name"],
        symbol=pair_data["baseToken"]["symbol"],
        twitter=next((social["url"] for social in pair_data["info"]["socials"] 
                    if social["type"] == "twitter"), ""),
        imageUrl=pair_data["info"]["imageUrl"],
        marketCap=pair_data["marketCap"],
        priceUsd=float(pair_data["priceUsd"])
    )
    
    # Build TokenPairsData object
    result = TokenPairsData(
        pa=pair_data["pairAddress"],
        token=token_info
    )
    
    return result