import logging
# Comment or delete unused imports
# from agno.agent.agent import Agent
# from agno.models.openai.like import OpenAILike

from app.schemas.news import News
from datetime import datetime

logger = logging.getLogger(__name__)

async def create_fake_news() -> News:
    """
    This function has been deprecated and now only returns a warning message.
    Please use RabbitMQ message queue to push real data.
    """
    logger.warning("create_fake_news function has been deprecated. Please use RabbitMQ message queue.")
    
    # Return a warning message instead of fake data
    current_time = int(datetime.now().timestamp())
    return News(
        title="[System Notice] Fake data generation has been disabled",
        abstract="This function has been disabled. Please use RabbitMQ message queue to push real data.",
        cover_img="https://example.com/disabled.jpg",
        published_at=current_time,
        origin_url="https://example.com",
        news_url="https://example.com",
        source_id="system-notice",
        source_type=0,
        source_name="System Notice",
        type=0,
        sort_id=0
    )
