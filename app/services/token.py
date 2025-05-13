import logging

from sqlalchemy import text

from app.dependencies import get_db
from app.services.external.goplus_api import process_token_risk, process_solana_token_risk, api_check_token_safety, \
    api_check_solana_token_safety
from app.services.twitter import extract_twitter_username
from app.schemas.token import CheckTokenData, TwitterFromCAData, CheckSOLTokenData, CAFromTwitterData
from app.utils.chain_name_format import API_SUPPORTED_CHAINS, normalize_chain_name
from app.utils.custom_exceptions import BadRequestException
logger = logging.getLogger(__name__)


# ========================================================================
# Check token safety using API
# ========================================================================
async def check_token_safety_api(chain: str, ca: str) -> CheckTokenData:
    """
    Check token safety using API
    """
    chain = normalize_chain_name(chain)

    chain_name = chain.lower()
    chain_id = API_SUPPORTED_CHAINS.get(chain_name)
    if chain_id is None:
        raise BadRequestException(f"Chain {chain} is not supported")
    logger.info(f"Checking {chain_name} token safety: {ca} (API)")

    # Process token risk data
    risks = await process_token_risk(chain_id, ca)

    # Return
    return CheckTokenData(chain=chain, ca=ca, risks=risks)


# ========================================================================
# Check SOL token safety using API
# ========================================================================
async def check_sol_token_safety(ca: str) -> CheckSOLTokenData:
    """
    Check SOL token safety using API
    """
    logger.info(f"Checking SOL token safety: {ca} (API)")

    # Process SOL token risk data
    risks = await process_solana_token_risk(ca)

    # Return
    return CheckSOLTokenData(ca=ca, risks=risks)


# ========================================================================
# Get CA from Twitter
# ========================================================================


async def get_ca_from_twitter(twitter_name: str) -> CAFromTwitterData:
    """
    Get CA from Twitter
    """
    
    if "https://" in twitter_name:
        twitter_name = extract_twitter_username(twitter_name)
    
    async with get_db() as db:
        x_url = "https://x.com/" + twitter_name
        twitter_url = "https://twitter.com/" + twitter_name

        # From database
        query = text(
            """
SELECT network, address
FROM news_coins,
     LATERAL jsonb_array_elements_text(twitter::jsonb) AS tw(tw_url)
WHERE tw.tw_url = :x_url OR tw.tw_url = :twitter_url
LIMIT 1
"""
        )

        result = await db.execute(query, {"x_url": x_url, "twitter_url": twitter_url})

        row = result.fetchone()
        if not row:
            logger.info(f"Did not find any tokens with Twitter name '{twitter_name}'")
            raise BadRequestException(
                f"Did not find any tokens with Twitter name '{twitter_name}'"
            )

        token_data = CAFromTwitterData(chain=row[0], ca=row[1])

        return token_data


# ========================================================================
# Get Twitter from CA
# ========================================================================
async def get_twitter_from_ca(ca: str) -> TwitterFromCAData:
    """
    Get Twitter from CA
    """
    async with get_db() as db:
        # Construct SQL query
        query = text(
            """
                    SELECT twitter
                    FROM news_coins
                    WHERE address = :ca
                    """
        )

        # Execute query
        result = await db.execute(query, {"ca": ca})

        # Get result
        row = result.fetchone()
        if not row:
            raise BadRequestException(f"Did not find any Twitter accounts with address '{ca}'")

        # Return Twitter account
        return TwitterFromCAData(twitter_name=row[0][0])


# ========================================================================
# Identify token chain
# ========================================================================
async def identify_token_chain(ca: str) -> str:
    """
    Identify the blockchain network that a token contract address belongs to
    """
    # Check if CA is empty
    if not ca:
        raise BadRequestException("Contract address cannot be empty")

    # Check if CA is a valid Ethereum address
    if ca.startswith("0x"):
        # Check if CA length is correct (standard contract address length is 42 characters, including 0x prefix)
        if len(ca) != 42:
            raise BadRequestException("Ethereum contract address length must be 42 characters (including 0x prefix)")
        
        # Check if CA only contains valid hexadecimal characters
        try:
            int(ca[2:], 16)
        except ValueError:
            raise BadRequestException("Contract address must be in valid hexadecimal format")
            
        # Check Ethereum series chains (in order of commonality)
        eth_chains = ["ethereum", "bsc", "base"]
        for chain in eth_chains:
            try:
                chain = normalize_chain_name(chain)
                chain_name = chain.lower()
                chain_id = API_SUPPORTED_CHAINS.get(chain_name)
                logger.info(f"Checking {chain_name} token chain: {ca} (API)")
                api_response = await api_check_token_safety(chain_id, ca)
                if len(api_response.keys()) != 0:
                    logger.debug(str(api_response)[:100])
                    return chain
            except Exception as e:
                logger.debug(f"{chain} chain detection failed: {str(e)}")
                continue
    else:
        # Check if CA is a valid Solana address
        # Solana addresses are usually base58 encoded and 44 characters long
        if len(ca) < 32 or len(ca) > 44:
            raise BadRequestException("Solana contract address length is incorrect")
        
        # Check if CA only contains valid base58 characters (excluding 0OIl characters)
        valid_chars = set("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")
        if not all(c in valid_chars for c in ca):
            raise BadRequestException("Solana contract address contains invalid characters")
            
        # Check Solana chain
        try:
            chain = "solana"
            api_response = await api_check_solana_token_safety(ca)
            if len(api_response.keys()) != 0:
                logger.debug(str(api_response)[:100])
                return chain
        except Exception as e:
            logger.debug(f"Solana chain detection failed: {str(e)}")

    # If all chains fail to detect
    raise BadRequestException("Failed to detect the blockchain network that the contract address belongs to")