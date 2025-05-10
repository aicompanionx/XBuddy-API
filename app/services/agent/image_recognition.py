import logging
from agno.agent.agent import Agent
from agno.media import Image
from agno.models.openai.like import OpenAILike

from app.config import get_config

logger = logging.getLogger(__name__)

async def ai_image_recognition(url: str):
    """
    Recognize image content and describe it with text
    """
    config = get_config()["external_apis"]["image_recognition_ai"]
    
    model = OpenAILike(
        id=config["model"],
        base_url=config["base_url"],
        api_key=config["key"],
        max_tokens=500,
    )
    
    prompt = config["prompt"]
        
    agent = Agent(
        model=model,
        instructions=prompt,
    )

    image = Image(url=url)
    logger.info(f"Recognizing image: {url}")
    response = agent.run("", images=[image])

    logger.debug(response)
    if hasattr(response, 'content'):
        return response.content
    return response
