import logging
from fastapi import APIRouter

from app.services.agent.twitter_raid import TweetAnalysisAgent
from app.services.twitter import extract_twitter_username
from app.services.twitter_raid import get_random_raid_object
from app.utils.chain_name_format import normalize_chain_name
from app.utils.custom_exceptions import ServerException
from app.schemas.twitter_raid import Tweet, TwitterRaidRequest, TwitterRaidResponse, TwitterRaidData
from app.services.external.twitterio_api import get_non_reply_tweets, get_random_tweet, get_tweets, is_not_retweet

router = APIRouter(prefix="/twitter_raid", tags=["Promotion"])
logger = logging.getLogger(__name__)


@router.post(
    "/push",
    response_model=TwitterRaidResponse,
    summary="Promotion",
    description="Promote your token",
)
async def api_twitter_raid(req: TwitterRaidRequest):
    """  Promotion  """
    try:
        chain = normalize_chain_name(req.chain)

        # Get promotion object
        random_raid_data = get_random_raid_object(chain)

        title=random_raid_data["name"]
        twitter_url=random_raid_data["url"]
        
        twitter_name = extract_twitter_username(twitter_url)
        
        logger.info(f"{title} getting tweet content")
        tweets = await get_tweets(twitter_name)
        tweets = get_non_reply_tweets(tweets) # Non-reply tweets
        tweets = is_not_retweet(tweets)       # Not a retweet
        tweet: Tweet = get_random_tweet(tweets[:5]) # Top 5 tweets

        # Build analysis prompt
        tweet_content = tweet.to_prompt()
        logger.debug(tweet_content)

        token_content = f"""
        {req.token_name}
        {req.token_symbol}
        {req.token_ca}
        {req.token_description}
        {req.logo_content}
        """
        logger.debug(token_content)

        logger.info("Starting analysis...")
        agent = TweetAnalysisAgent()
        response = agent.agent.run(
            token_content + tweet_content
        )
        raid_content = response.content

        logger.info("Promotion content: \n\n" + raid_content)
        
        result = TwitterRaidData(
            title=title,
            twitter_url=twitter_url,
            name=twitter_name,
            tweet_url=tweet.url,
            raid_content=raid_content
        )

        return TwitterRaidResponse(data=result)


    except Exception as e:
        logger.error(f"Promotion error: {str(e)}")
        raise ServerException(f"Promotion error: {str(e)}")
