import logging
import base64
import hmac
import hashlib
import urllib.parse
from datetime import datetime, timezone

import httpx

from app.config import get_config
from app.utils.cache import cache_data, get_cached_data
from app.utils.custom_exceptions import ServerException
from app.utils.retry import retry_async

APIS = {
    "get_instruments": "/public/instruments",
    "get_currencies": "/asset/currencies",
}

BASE_URL = "https://www.okx.com/api/v5"

logger = logging.getLogger(__name__)


def _generate_signature(timestamp: str, method: str, request_path: str, body: str = "") -> str:
    """
    Generate OKX API signature
    """
    config = get_config()["external_apis"]["okx"]
    secret = config["secret"]
    
    message = f"{timestamp}{method}{request_path}{body}"
    return base64.b64encode(hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()).decode()

@retry_async(max_retries=3, base_delay=1, max_delay=5)
async def _request_okx_api(path: str, params: dict | None = None, authenticated: bool = False):
    """
    Unified request method to OKX API with retry mechanism and proper authentication
    """
    # Try to get data from cache
    query_string = urllib.parse.urlencode(params or {})
    cache_key = f"okx_api:{path}?{query_string}"
    cached_data = await get_cached_data(cache_key)
    if cached_data:
        logger.debug(f"Using cached data: {cache_key}")
        return cached_data
    
    # Construct the full request URL
    full_request_url = f"{BASE_URL}{path}"
    if query_string:
        full_request_url += f"?{query_string}"
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
    }
    
    # Add authentication headers if required
    if authenticated:
        config = get_config()["external_apis"]["okx"]
        api_key = config["key"]
        passphrase = config["passphrase"]
        
        # Correctly format the requestPath for signing
        base_uri_path_component = urllib.parse.urlparse(BASE_URL).path
        path_for_signing = base_uri_path_component + path
        if query_string:
            path_for_signing += f"?{query_string}"
            
        # Generate timestamp in ISO 8601 format (YYYY-MM-DDTHH:mm:ss.SSSZ)
        timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        
        signature = _generate_signature(timestamp, "GET", path_for_signing)
        
        headers.update({
            "OK-ACCESS-KEY": api_key,
            "OK-ACCESS-PASSPHRASE": passphrase,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-SIGN": signature,
        })

    # Increased timeout values for better reliability
    timeout = httpx.Timeout(60.0, connect=30.0)
    
    try:
        async with httpx.AsyncClient(timeout=timeout, headers=headers, verify=False) as client:
            logger.info(f"Requesting OKX API: {full_request_url}")
            response = await client.get(full_request_url)
            response.raise_for_status()

            data = response.json()
            if data.get("code") != "0":
                raise ServerException(data.get("msg", "Unknown OKX API error"))

            result = data.get("data")

            # Cache the result
            await cache_data(cache_key, result)

            return result
    except httpx.ConnectTimeout:
        logger.warning(f"Connection timeout for OKX API: {full_request_url}")
        # Try alternate API endpoint
        if BASE_URL == "https://www.okx.com/api/v5":
            logger.info("Trying alternate OKX API endpoint...")
            alt_url = full_request_url.replace("https://www.okx.com/api/v5", "https://www.okx.me/api/v5")
            async with httpx.AsyncClient(timeout=timeout, headers=headers, verify=False) as client:
                response = await client.get(alt_url)
                response.raise_for_status()
                data = response.json()
                if data.get("code") != "0":
                    raise ServerException(data.get("msg", "Unknown OKX API error"))
                result = data.get("data")
                await cache_data(cache_key, result)
                return result
        raise


async def get_instruments(inst_type: str = "SPOT", inst_id: str = None):
    """
    Get instrument information from OKX
    """
    params = {"instType": inst_type}
    if inst_id:
        params["instId"] = inst_id
    return await _request_okx_api(APIS["get_instruments"], params)

async def get_currencies(symbol: str = None):
    """
    Get currency information from OKX
    """
    params = {}
    if symbol:
        params["ccy"] = symbol
    return await _request_okx_api(APIS["get_currencies"], params, authenticated=True)

async def get_token_detail(symbol: str) -> dict:
    """
    Get comprehensive token details by combining data from multiple OKX API endpoints
    
    Returns a dictionary with the following structure:
    {
        "symbol": str,       # Token symbol (e.g., "BTC")
        "id": str,          # Token ID (same as symbol for now)
        "name": str,        # Token name (e.g., "Bitcoin")
        "platform": str,    # Platform/chain (e.g., "Bitcoin")
        "categories": list, # Categories this token belongs to
        "description": str, # Token description
        "logo_url": str,    # URL to token logo
        "twitter_url": str, # Twitter URL if available
        "public_notice": str # Public notices about this token if any
    }
    """
    try:
        currencies_data = await get_currencies(symbol)
        
        if not currencies_data or len(currencies_data) == 0:
            logger.warning(f"No data found for token: {symbol}")
            raise ServerException(f"No data found for token: {symbol}")
            
        currency = currencies_data[0]
        
        token_detail = {
            "symbol": symbol,
            "id": symbol,
            "name": currency.get("name", symbol),
            "platform": currency.get("chain", "").split("-")[-1] if currency.get("chain") else "",
            "categories": [],
            "description": "",
            "logo_url": currency.get("logoLink", ""),
            "twitter_url": "",
            "public_notice": ""
        }
        
        return token_detail
        
    except Exception as e:
        logger.error(f"Error fetching token details for {symbol}: {str(e)}")
        raise ServerException(f"Failed to get token details: {str(e)}")