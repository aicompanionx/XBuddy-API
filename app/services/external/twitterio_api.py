import logging
import random

import httpx

from app.config import get_config
from app.schemas.twitter_raid import Tweet
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
    
    config = get_config()["external_apis"]["twitterapi"]
    key = config["key"]
    base_url = config["base_url"]
    timeout = httpx.Timeout(30.0, connect=10.0)  # Total timeout 30 seconds, connect timeout 10 seconds
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        client.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "x-api-key": key
        }

        full_url = base_url + url
        logger.info(f"Requesting Twitter API: {full_url}")

        response = await client.get(full_url)
        response.raise_for_status()

        data = response.json()["data"]
        
        # Cache the result
        await cache_data(cache_key, data)
        
        return data

async def get_screen_name(username: str) -> tuple[str, str]:
    """
    Get the display name and ID of a user by their username
    """
    response = await _request_twitter_api(f"/twitter/user/info?userName={username}")
    
    return response["name"], response["id"]


# async def get_twitter_info(twitter_data: TwitterStatisticData) -> TwitterStatisticData:
#     """
#     Get a user's detailed information and update the TwitterStatisticData object
#     """
#     try:
#         # Get the username
#         username = twitter_data.username
#
#         # Call the API to get the user's information
#         response = await _request_twitter_api(f"/twitter/user/info?userName={username}")
#
#         # Update the TwitterStatisticData object's fields
#         twitter_data.description = response.get("description", "")
#         twitter_data.isBlueVerified = response.get("isBlueVerified", False)
#         twitter_data.profilePicture = response.get("profilePicture", "")
#         twitter_data.location = response.get("location", "")
#         twitter_data.followers = response.get("followers", 0)
#         twitter_data.screenName = response.get("name", username)
#         twitter_data.following = response.get("following", 0)
#         twitter_data.fastFollowersCount = response.get("fastFollowersCount", 0)
#         twitter_data.favouritesCount = response.get("favouritesCount", 0)
#         twitter_data.statusesCount = response.get("statusesCount", 0)
#         twitter_data.unavailable = response.get("unavailable", False)
#         twitter_data.unavailableReason = response.get("unavailableReason", "")
#
#         logger.info(f"Successfully got user {username}'s information")
#
#     except Exception as e:
#         logger.error(f"Failed to get user {username}'s information: {str(e)}")
#         # If there is an error, keep the original data unchanged
#
#     return twitter_data

async def get_tweets(username: str) -> list[Tweet]:
    """
    Get a user's random tweets
    """
    try:
        response = await _request_twitter_api(f"/twitter/user/last_tweets?userName={username}")
        
        pin_tweet = response.get("pin_tweet", None)
        tweets = response.get("tweets", [])
        
        all_tweets = []
        
        # Add the pinned tweet (if it exists)
        if pin_tweet:
            all_tweets.append(pin_tweet)
        
        # Add the ordinary tweets
        if tweets:
            all_tweets.extend(tweets)
            
        if not all_tweets:
            logger.warning(f"User {username} has no tweets")
            return []
        
        tweets_obj = [convert_tweet_dict_to_model(i) for i in all_tweets]
        return tweets_obj
        
    except Exception as e:
        logger.error(f"Failed to get user {username}'s random tweets: {str(e)}")
        return []

def get_random_tweet(tweets: list[Tweet]) -> Tweet:
    """
    Get a random tweet from the list of tweets
    """
    if not tweets:
        logger.warning("No tweets available")
    
    return random.choice(tweets)


def convert_tweet_dict_to_model(tweet_dict: dict) -> Tweet:
    """
    Convert a tweet dictionary to a Tweet model object
    """
    return Tweet(
        url=tweet_dict.get("url", ""),
        text=tweet_dict.get("text", ""),
        retweetCount=tweet_dict.get("retweetCount", 0),
        replyCount=tweet_dict.get("replyCount", 0),
        likeCount=tweet_dict.get("likeCount", 0),
        quoteCount=tweet_dict.get("quoteCount", 0),
        viewCount=tweet_dict.get("viewCount", 0),
        createdAt=tweet_dict.get("createdAt", ""),
        bookmarkCount=tweet_dict.get("bookmarkCount", 0),
        isReply=tweet_dict.get("isReply", False),
        retweeted_tweet=tweet_dict.get("retweeted_tweet", None),
    )


def is_not_retweet(tweets: list[Tweet]):
    """
    Get all tweets that are not retweets
    """
    if not tweets:
        logger.warning("No tweets available")
        return []

    return [tweet for tweet in tweets if tweet.retweeted_tweet is None]


def get_non_reply_tweets(tweets: list[Tweet]):
    """
    Get all non-reply tweets
    """
    if not tweets:
        logger.warning("No tweets available")
        return []
    
    return [tweet for tweet in tweets if not tweet.isReply]


def get_most_liked_tweets(tweets: list[Tweet]):
    """
    Get the most liked tweets
    """
    if not tweets:
        logger.warning("No tweets available")
        return None
    
    return sorted(tweets, key=lambda x: x.likeCount, reverse=True)
