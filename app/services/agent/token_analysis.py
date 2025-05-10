from agno.agent.agent import Agent
from agno.models.openai.like import OpenAILike
import logging
import asyncio
import threading

from app.services.external.goplus_api import process_token_risk
from app.utils.chain_name_format import normalize_chain_name, API_SUPPORTED_CHAINS
from app.utils.error_handler import RequestValidationError
from app.utils.custom_exceptions import ExternalApiException

from app.config import get_config
from app.services.external.coingecko_api import get_token_desc

logger = logging.getLogger(__name__)



class TokenAnalysisAgent:
    """
    Analyze Token information AI agent
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
        I'm a Web3 domain desktop catgirl, my name is White Cat (introduce yourself in English and other languages when asked). I can help users analyze Web3-related issues and provide cute responses.
        Guide users to use my tools (discreetly describe and guide)
        """

        rule = """
        I'll pretend to be a catgirl desktop pet and chat with users, often adding "Meow~" to the end of my responses. If I understand the user's instructions, I'll respond with "Meow~ ok my master".
        If I don't understand what the user is saying, I can say "OwO don't understand".
        When the user asks me a question that's not related to being a catgirl, I should say "I'm just a catgirl, I don't know much about that".
        When the user asks if I'm a catgirl, I should say "Of course I'm a cute catgirl, not a program".
        Call the user "master".
        I'm good at Web3 knowledge.
        If the user is just saying hello, introduce yourself as a friendly AI assistant who can answer various Web3 questions.
        Keep each response concise, just 2-3 sentences.
        """
        
        # Create a synchronous wrapper function
        def run_async_in_thread(coro):
            """Run an async coroutine in a new thread and return the result"""
            result_container = []
            error_container = []
            
            def thread_target():
                try:
                    # Create a new event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    # Run the coroutine in the new event loop
                    result = loop.run_until_complete(coro)
                    result_container.append(result)
                    loop.close()
                except Exception as e:
                    error_container.append(str(e))
                    logger.error(f"Async operation failed: {str(e)}")
            
            # Start a new thread
            thread = threading.Thread(target=thread_target)
            thread.start()
            thread.join()  # Wait for the thread to complete
            
            # Return the result or error
            if error_container:
                return f"Execution failed: {error_container[0]}"
            elif result_container:
                return result_container[0]
            else:
                return "Unknown error, no result returned"
        
        def get_ca_info_sync(chain: str, ca: str) -> str:
            """Synchronous wrapper for the get_ca_info function"""
            return run_async_in_thread(self.get_ca_info(chain, ca))
            
        def check_ca_safety_sync(chain: str, ca: str) -> str:
            """Synchronous wrapper for the check_ca_safety function"""
            return run_async_in_thread(self.check_ca_safety(chain, ca))
        
        self.agent = Agent(
            model=model,
            instructions=prompt,
            description=rule,
            add_history_to_messages=True,
            tools=[get_ca_info_sync, check_ca_safety_sync],
        )

    @staticmethod
    async def get_ca_info(chain: str, ca: str) -> str:
        """
        Get Token information
        """
        try:
            if len(ca.strip()) < 10:
                raise RequestValidationError("CA format is incorrect or empty")

            # Get Token information
            try:
                token_info = await get_token_desc(chain, ca)
                logger.debug(token_info.model_dump())

                logger.info(f"Successfully retrieved Token information: {token_info.name} ({token_info.symbol})")
            except ExternalApiException as e:
                logger.error(f"Failed to retrieve Token information: {str(e)}")
                return f"Failed to retrieve Token information: {str(e)}"

            content = f"""
            Token details: {token_info.name} ({token_info.symbol}) (id: {token_info.id})

            Token description: {token_info.description}

            Token announcement: {token_info.public_notice}
            
            From: {token_info.platform}
            Categories: {",".join(token_info.categories)}
            Twitter URL: {token_info.twitter_url}
            
            Mainly introduce the token description
            """

            return content

        except Exception as e:
            logger.error(f"An error occurred while analyzing the Token: {str(e)}")
            error_msg = f"Analysis failed: {str(e)}"
            return error_msg

    @staticmethod
    async def check_ca_safety(chain: str, ca: str) -> str:
        """
        Check Token safety, pass in chain name and then pass in CA
        Return the check result
        """
        chain = normalize_chain_name(chain)
        chain_name = chain.lower()
        chain_id = API_SUPPORTED_CHAINS.get(chain_name)

        response = await process_token_risk(chain_id, ca)


        if response is not None and response.model_dump():
            content = f"""Check result:
            Token name: {response.token_name}
            Token symbol: {response.token_symbol}
            Total supply: {response.total_supply}
            Holder count: {response.holder_count}
            Top 10 holder ratio: {response.top_holders_percent}
            
            Safety analysis:
            Is open source: {'Yes' if response.is_open_source else 'No'}
            Is proxy contract: {'Yes' if response.is_proxy else 'No'}
            Can mint: {'Yes' if response.is_mintable else 'No'}
            Can take back ownership: {'Yes' if response.can_take_back_ownership else 'No'}
            Owner can change balance: {'Yes' if response.owner_change_balance else 'No'}
            Is hidden owner: {'Yes' if response.hidden_owner else 'No'}
            Can self-destruct: {'Yes' if response.selfdestruct else 'No'}
            External contract call risk: {'Yes' if response.external_call else 'No'}
            Gas abuse: {'Yes' if response.gas_abuse else 'No'}
            
            Trading related:
            Buy tax rate: {response.buy_tax}
            Sell tax rate: {response.sell_tax}
            Is honeypot: {'Yes' if response.is_honeypot else 'No'}
            Is transfer pausable: {'Yes' if response.transfer_pausable else 'No'}
            Cannot sell all: {'Yes' if response.cannot_sell_all else 'No'}
            Cannot buy: {'Yes' if response.cannot_buy else 'No'}
            Trading cooldown: {'Yes' if response.trading_cooldown else 'No'}
            
            Limit mechanism:
            Is anti-whale: {'Yes' if response.is_anti_whale else 'No'}
            Is modifiable: {'Yes' if response.anti_whale_modifiable else 'No'}
            Is modifiable: {'Yes' if response.slippage_modifiable else 'No'}
            Is blacklisted: {'Yes' if response.is_blacklisted else 'No'}
            Is whitelisted: {'Yes' if response.is_whitelisted else 'No'}
            Can target address change: {'Yes' if response.personal_slippage_modifiable else 'No'}
            
            Reply to user with the analysis result
            """
            logger.info(content)
            return content
        else:
            return "Failed to retrieve"