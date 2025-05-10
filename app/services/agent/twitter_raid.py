from agno.agent.agent import Agent
from agno.models.openai.like import OpenAILike
import logging

from app.config import get_config

logger = logging.getLogger(__name__)



class TweetAnalysisAgent:
    """
    Analyze tweet content and generate promotional content
    """
    def __init__(self):
        # Load config file
        config = get_config()
        self.base_url = config.get("external_apis").get("analysis_ai").get("base_url")
        self.key = config.get("external_apis").get("analysis_ai").get("key")
        self.model = config.get("external_apis").get("analysis_ai").get("model")
        
        # Initialize model
        model = OpenAILike(
            id=self.model,
            base_url=self.base_url,
            api_key=self.key,
        )
        
        prompt = """
        I'm generating a promotional comment for a token I'm holding,
        I'm ready to comment on the following main tweet account,
        I expect the account to reply to me and let people who see the comment see my token information
        Please help me generate 1 comment content
        If the content has a Twitter account, don't add CA, this can increase the reply rate (after all, celebrities don't want to promote cryptocurrencies)
        But if the content doesn't have a Twitter account, you can add CA
        The content should not exceed 20 characters
        Add one or two emojis
        Write in a human-like tone and use English to generate tweets
        """
        
        self.agent = Agent(
            model=model,
            instructions=prompt,
            markdown=False
        )