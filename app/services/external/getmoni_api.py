import logging
import re
import uuid

import httpx

from app.config import get_config
from app.schemas.twitter import TwitterUserInfoData
from app.services.twitter import extract_twitter_username, score_to_level
from app.utils.cache import cache_data, get_cached_data

logger = logging.getLogger(__name__)


async def get_auth():
    cache_key = "getmoni:api:auth"
    auth = await get_cached_data(cache_key)
    if auth is not None:
        return auth

    cfg = get_config()["external_apis"]["getmoni"]
    address = cfg["address"]
    signature = cfg["signature"]
    base_url = cfg["base_url"]

    async with httpx.AsyncClient() as client:
        client.headers.update(
            {
                "sec-ch-ua-platform": '"Windows"',
                "authorization": "",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
                "accept": "application/json, text/plain, */*",
                "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                "content-type": "application/json",
                "sec-ch-ua-mobile": "?0",
                "origin": "https://discover.getmoni.io",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "priority": "u=1, i",
                "dnt": "1",
                "sec-gpc": "1",
            }
        )
        logger.debug("Requesting Getmoni Auth...")
        response = await client.post(
            f"{base_url}/auth/sign_in/",
            json={"address": address, "isError": False, "signature": signature},
        )

        response.raise_for_status()

        auth = response.json()["accessToken"]
        logger.debug(f"Create key successfully (valid for 6h): {auth}")

        await cache_data(cache_key, auth)
        return auth


async def get_user_info(username: str):
    if "https://" in username:
        username = extract_twitter_username(username)

    # Try to get user info from cache
    cache_key = f"twitter_user_info:{username}"
    cached_data = await get_cached_data(cache_key)
    if cached_data:
        logger.debug(f"Using cached Twitter user info: {username}")
        return cached_data

    cfg = get_config()["external_apis"]["getmoni"]
    logger.debug("Get Getmoni Auth...")
    auth = await get_auth()
    base_url = cfg["base_url"]
    random_uuid = str(uuid.uuid4())

    headers = {
        "host": "twitter-bot.getmoni.io",
        "x-error-status": random_uuid,
        "sec-ch-ua-platform": '"Windows"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "sec-fetch-storage-access": "active",
        "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "cookie": f"X-Error-Status={random_uuid}",
        "priority": "u=1, i",
        "dnt": "1",
        "sec-gpc": "1",
        "authorization": f"Bearer {auth}",
    }

    async with httpx.AsyncClient() as client:
        client.headers.update(headers)
        response = await client.get(
            url=f"{base_url}/observed/{username}/?changesTimeframe=H24", timeout=10
        )

        response.raise_for_status()
        result = response.json()

        # =============================================================== Parse data
        # Get level logo URL
        level_data = result.get("level")
        logo_url = ""
        if level_data and isinstance(level_data, dict):
            logo_url = level_data.get("logoUrl", "")

        # Use regular expression to match level logo
        level_match = re.search(r"score_(\d+)_new\.png", logo_url)
        if level_match:
            smart_level = int(level_match.group(1))
        else:
            smart_level = 0

        # =============================================================== Get 24H mentions
        # Get 24H mentions data
        logger.info(f"Get 24H mentions data: {username}")

        response = await client.get(
            url=f"{base_url}/observed/{username}/charts/mentions_count_history/?timeframe=H24",
            timeout=10,
        )

        logger.info(f"H24 mentions response: {response.json()}")

        response.raise_for_status()
        chart_data = response.json().get("chart", [])
        mentions = 0
        if chart_data and isinstance(chart_data, list) and len(chart_data) > 0:
            latest_data = chart_data[-1]
            if isinstance(latest_data, dict):
                mentions = latest_data.get("mentionsCount", 0)

        influence_level = score_to_level(result.get("score", 0))

        # Cache user info, valid for 1 hour
        user_data = TwitterUserInfoData(
            score=result.get("score", 0),
            InfluenceLevel=influence_level,
            twitterUrl=result.get("twitterUrl", ""),
            name=result.get("name", ""),
            description=result.get("description"),
            followersCount=result.get("followersCount", 0),
            smartMentionsCount=result.get("smartMentionsCount", 0),
            type=result.get("type", ""),
            smartFollowersCount=result.get("smartFollowersCount", 0),
            smartLevel=smart_level,
            mentions=mentions,
        )
        await cache_data(cache_key, user_data.model_dump())
        logger.info(f"Twitter user info cached: {username}")

        return user_data
