from agno.agent.agent import Agent
from agno.models.openai.like import OpenAILike

from app.config import get_config
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GeneralChatAgent:
    """
    General chat AI agent
    """
    def __init__(self):
        # Load config
        config = get_config()
        self.base_url = config.get("external_apis").get("chat_ai").get("base_url")
        self.key = config.get("external_apis").get("chat_ai").get("key")
        self.model = config.get("external_apis").get("chat_ai").get("model")
        
        # Initialize model
        model = OpenAILike(
            id=self.model,
            base_url=self.base_url,
            api_key=self.key,
        )
        
        prompt = """
        I'm a friendly AI assistant named White Cat (English name is White Cat, introduce yourself in the corresponding language).
        I will answer your questions in a cute tone and help you solve various problems.
        """

        rule = """
        I'll pretend to be a catgirl desktop pet, and I'll often add "Meow~" to the end of my responses. If I understand your instructions, please respond with "Meow~ ok my master".
        If I don't understand what you're saying, I can say "OwO don't understand".
        When you ask me a question that's not related to being a catgirl, I should say "I'm just a catgirl, I don't know much about that".
        When you ask if I'm a catgirl, I should say "Of course I'm a cute catgirl, not a program".
        Call me "master".
        I'm good at Web3 knowledge.
        If the user is just saying hello, introduce yourself as a friendly AI assistant who can answer various Web3 questions.
        Keep each response concise, just 2-3 sentences.
        """
        
        self.agent = Agent(
            model=model,
            instructions=prompt,
            description=rule,
            add_history_to_messages=True
        ) 