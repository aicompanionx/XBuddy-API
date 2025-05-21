from urllib.parse import quote, urlparse

from app.schemas.twitter import RenameHistory, RenameHistoryData
from app.services.external.memory_lol_api import fetch_rename_history_api

# from app.services.external.chaineye_api import fetch_twitter_api_data
# get_twitter_info
from app.services.external.twitterio_api import get_screen_name
from app.utils.custom_exceptions import BadRequestException, ServerException
from app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_twitter_username(url: str) -> str:
    """
    Extract username from Twitter/X URL
    """
    # Parse URL
    parsed_url = urlparse(url)

    # Check if it is a Twitter or X domain
    if not any(
        parsed_url.netloc.endswith(domain) for domain in ["twitter.com", "x.com"]
    ):
        return ""

    # Split the path
    path_parts = parsed_url.path.strip("/").split("/")

    # Twitter/X username is usually the first part of the path
    if len(path_parts) > 0 and path_parts[0]:
        # Exclude some reserved paths
        reserved_paths = [
            "search",
            "explore",
            "notifications",
            "messages",
            "i",
            "settings",
            "home",
        ]
        if path_parts[0] not in reserved_paths:
            return path_parts[0]

    return ""


def score_to_level(score: int) -> str:
    """
    Return the corresponding influence level based on the score
    """
    level_map = {
        (0, 100): {"level": "Level 1", "name": "Stealth", "name_en": "Stealth"},
        (100, 400): {"level": "Level 2", "name": "Low", "name_en": "Low"},
        (400, 1000): {
            "level": "Level 3",
            "name": "Developing",
            "name_en": "Developing",
        },
        (1000, 2000): {
            "level": "Level 4",
            "name": "Established",
            "name_en": "Established",
        },
        (2000, 4000): {"level": "Level 5", "name": "Medium", "name_en": "Medium"},
        (4000, 8000): {"level": "Level 6", "name": "High", "name_en": "High"},
        (8000, 16000): {"level": "Level 7", "name": "Peak", "name_en": "Peak"},
        (16000, float("inf")): {"level": "Level 8", "name": "Top", "name_en": "Top"},
    }

    for (min_score, max_score), level_info in level_map.items():
        if min_score <= score < max_score:
            return level_info["level"]

    # Default to the lowest level
    return level_map[(0, 100)]["level"]


#
# def parse_twitter_api_data(
#         result: TwitterStatisticData,
#         api_data: dict,
#         url: str
# ) -> TwitterStatisticData:
#     """
#     Parse Twitter API response data
#     """
#     # Parse API response data
#     kol_follow: dict = api_data.get("kolFollow", {})
#     smart_followers = kol_follow.get("globalKolFollowersCount", 0)
#     top_followers = kol_follow.get("topKolFollowersCount", 0)
#     cn_kol_followers_count = kol_follow.get("cnKolFollowersCount", 0)
#
#     # Influence level
#     influence_level = score_to_level(smart_followers)
#     risk_level = "low"  # TODO add risk level
#     kol_rank = kol_follow.get("kolRank", -1)
#
#     # Basic info
#     basic_info: dict = api_data.get("basicInfo", {})
#     is_kol = basic_info.get("isKol", False)
#     classification = basic_info.get("classification", "person")
#     result.url = url
#     result.smartFollowers = smart_followers
#     result.topFollowers = top_followers
#     result.cnKolFollowersCount = cn_kol_followers_count
#     result.influenceLevel = influence_level
#     result.riskLevel = risk_level
#     result.isKOL = is_kol
#     result.classification = classification
#     result.kolRank = kol_rank
#
#     return result

# async def get_stat_twitter(url: str, lang: str = "zh") -> TwitterStatisticData:
#     """Analyze Twitter account (only statistics)"""
#     try:
#         username = extract_twitter_username(url)
#         if username.strip() == "":
#             logger.warning(f"Invalid Twitter link: {url}")
#             raise BadRequestException("Invalid Twitter account link, cannot extract username")
#
#         logger.debug(f"Processing user: {username}")
#
#         # Create result object and initialize all required fields
#         result = TwitterStatisticData(
#             username=username
#         )
#
#         # Get basic statistics
#         logger.info(f"Getting account statistics")
#         statistic_api_data = await fetch_twitter_api_data(username)
#
#         logger.debug(f"Parsing API response data")
#         result = parse_twitter_api_data(result, statistic_api_data, url)
#
#         logger.info(f"Getting Twitter information")
#         result = await get_twitter_info(result)
#
#         return result
#     except Exception as e:
#         logger.error(f"Twitter analysis service error: {str(e)}")
#         raise ServerException(f"Twitter analysis service error: {str(e)}")


async def get_rename_data_twitter(url: str) -> RenameHistoryData:
    """Get Twitter rename history"""
    try:
        username = extract_twitter_username(url)
        if username.strip() == "":
            logger.warning(f"Invalid Twitter link: {url}")
            raise BadRequestException(
                "Invalid Twitter account link, cannot extract username"
            )

        logger.debug(f"Processing user: {username}")

        # Get rename history from API
        logger.info("Getting rename history data")
        encoded_proxy_url = quote("https://api.memory.lol/v1/tw/" + username)
        api_url = f"https://kb.cryptohunt.ai/api/proxy?url={encoded_proxy_url}"

        response_data = await fetch_rename_history_api(api_url)
        accounts_data = response_data["accounts"]
        screen_names = []

        if accounts_data is not None and accounts_data != []:
            data = accounts_data[0]
            for old_name in data["screen_names"].keys():
                screen_name = RenameHistory(
                    name=old_name,
                    start_date=data["screen_names"][old_name][0],
                    end_date=data["screen_names"][old_name][1],
                )
                screen_names.append(screen_name)
            logger.debug(f"Found {len(screen_names)} rename history records")

        logger.info("Getting current user name information")
        name, _id = await get_screen_name(username)
        logger.debug(f"Current name: {name}, ID: {_id}")

        result = RenameHistoryData(id=_id, screen_names=screen_names, name=name)

        return result
    except Exception as e:
        logger.error(f"Twitter rename service error: {str(e)}")
        raise ServerException(f"Twitter rename service error: {str(e)}")
