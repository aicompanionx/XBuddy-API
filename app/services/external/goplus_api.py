import httpx
import logging
from app.utils.custom_exceptions import ServerException
from app.schemas.token import RiskOptions, SOLRiskOptions
from app.config import get_config
from app.utils.cache import get_cached_data, cache_data
from app.utils.retry import retry_async

APIS = {
    "token_safety": "/api/v1/token_security",
    "solana_token_safety": "/api/v1/solana/token_security",
    "sui_token_safety": "/api/v1/sui/token_security",
}

logger = logging.getLogger(__name__)


@retry_async(max_retries=3, base_delay=1, max_delay=5)
async def _request_goplus_api(url: str):
    """
    Unified request method to GoPlus API with retry mechanism
    """
    # Try to get data from cache
    cache_key = f"goplus_api:{url}"
    cached_data = await get_cached_data(cache_key)
    if cached_data:
        logger.debug(f"Using cached data: {cache_key}")
        return cached_data

    timeout = httpx.Timeout(30.0, connect=10.0)  # Total timeout 30 seconds, connect timeout 10 seconds
    async with httpx.AsyncClient(timeout=timeout) as client:
        client.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        logger.info(f"Requesting GoPlus API: {url}")
        response = await client.get(url)
        response.raise_for_status()

        data = response.json()
        if data.get("code") != 1:
            raise ServerException(data.get("message"))

        result = data.get("result")

        # Cache the result
        await cache_data(cache_key, result)

        return result


# ========================================================================
# Build URL
# ========================================================================

async def api_check_token_safety(chain_id: str, ca: str):
    """
    Check token safety
    """
    config = get_config()["external_apis"]["goplus"]
    url = f"{config['base_url']}{APIS['token_safety']}/{chain_id}?contract_addresses={ca}"
    logger.debug(f"Checking token safety: {url}")
    return await _request_goplus_api(url)


async def api_check_solana_token_safety(ca: str):
    """
    Check Solana token safety
    """
    config = get_config()["external_apis"]["goplus"]
    url = f"{config['base_url']}{APIS['solana_token_safety']}?contract_addresses={ca}"
    logger.debug(f"Checking Solana token safety: {url}")
    return await _request_goplus_api(url)


async def api_check_sui_token_safety(ca: str):
    """Check Sui token safety"""
    config = get_config()["external_apis"]["goplus"]
    url = f"{config['base_url']}{APIS['sui_token_safety']}?contract_addresses={ca}"
    logger.debug(f"Checking Sui token safety: {url}")
    return await _request_goplus_api(url)


# ========================================================================
# Parse Token Check API return value to object
# ========================================================================

def parse_goplus_data(ca_data: dict) -> RiskOptions:
    """
    Parse token safety data
    """
    is_open_source = ca_data.get("is_open_source") == "1"
    is_proxy = ca_data.get("is_proxy") == "1"
    is_mintable = ca_data.get("is_mintable") == "1"
    can_take_back_ownership = ca_data.get("can_take_back_ownership") == "1"
    owner_change_balance = ca_data.get("owner_change_balance") == "1"
    hidden_owner = ca_data.get("hidden_owner") == "1"
    selfdestruct = ca_data.get("selfdestruct") == "1"
    external_call = ca_data.get("external_call") == "1"
    gas_abuse = ca_data.get("gas_abuse") == "1" if "gas_abuse" in ca_data else False
    buy_tax = float(ca_data.get("buy_tax", "0"))
    sell_tax = float(ca_data.get("sell_tax", "0"))
    is_honeypot = ca_data.get("is_honeypot") == "1"
    transfer_pausable = ca_data.get("transfer_pausable") == "1"
    cannot_sell_all = ca_data.get("cannot_sell_all") == "1"
    cannot_buy = ca_data.get("cannot_buy") == "1"
    trading_cooldown = ca_data.get("trading_cooldown") == "1"
    is_anti_whale = ca_data.get("is_anti_whale") == "1"
    anti_whale_modifiable = ca_data.get("anti_whale_modifiable") == "1"
    slippage_modifiable = ca_data.get("slippage_modifiable") == "1"
    is_blacklisted = ca_data.get("is_blacklisted") == "1"
    is_whitelisted = ca_data.get("is_whitelisted") == "1"
    personal_slippage_modifiable = ca_data.get("personal_slippage_modifiable") == "1"

    token_name = ca_data.get("token_name")
    token_symbol = ca_data.get("token_symbol")
    total_supply = ca_data.get("total_supply")
    holder_count = ca_data.get("holder_count")
    holders = ca_data.get("holders", [])

    top_holders_percent = 0
    if holders:
        for holder in holders[:10]:
            top_holders_percent += float(holder.get("percent", 0))

    return RiskOptions(
        is_open_source=is_open_source,
        is_proxy=is_proxy,
        is_mintable=is_mintable,
        can_take_back_ownership=can_take_back_ownership,
        owner_change_balance=owner_change_balance,
        hidden_owner=hidden_owner,
        is_honeypot=is_honeypot,
        transfer_pausable=transfer_pausable,
        cannot_sell_all=cannot_sell_all,
        cannot_buy=cannot_buy,
        trading_cooldown=trading_cooldown,
        is_anti_whale=is_anti_whale,
        anti_whale_modifiable=anti_whale_modifiable,
        slippage_modifiable=slippage_modifiable,
        is_blacklisted=is_blacklisted,
        is_whitelisted=is_whitelisted,
        personal_slippage_modifiable=personal_slippage_modifiable,
        external_call=external_call,
        gas_abuse=gas_abuse,
        buy_tax=buy_tax,
        sell_tax=sell_tax,
        selfdestruct=selfdestruct,
        token_name=token_name,
        token_symbol=token_symbol,
        total_supply=total_supply,
        holder_count=holder_count,
        top_holders_percent=top_holders_percent,
    )


# ========================================================================
# Parse SOL Token Check API return value to object
# ========================================================================

def parse_solana_token_data(ca_data: dict) -> SOLRiskOptions:
    """
    Parse Solana token safety data to SOLRiskOptions object
    """
    is_mintable = ca_data.get("mintable", {}).get("status") == "1"
    metadata_mutable = ca_data.get("metadata_mutable", {}).get("status") == "1"
    freezable = ca_data.get("freezable", {}).get("status") == "1"
    closable = ca_data.get("closable", {}).get("status") == "1"
    non_transferable = ca_data.get("non_transferable") == "1"
    balance_mutable = ca_data.get("balance_mutable_authority", {}).get("status") == "1"

    transfer_fee = 0
    if ca_data.get("transfer_fee") and isinstance(ca_data.get("transfer_fee"), dict):
        transfer_fee = float(ca_data.get("transfer_fee", {}).get("fee_rate", 0))

    transfer_fee_upgradable = ca_data.get("transfer_fee_upgradable", {}).get("status") == "1"
    transfer_hook = len(ca_data.get("transfer_hook", [])) > 0
    default_account_state = ca_data.get("default_account_state", "")

    metadata = ca_data.get("metadata", {})
    symbol = metadata.get("symbol")
    name = metadata.get("name")
    description = metadata.get("description")
    total_supply = ca_data.get("total_supply")
    holder_count = ca_data.get("holder_count")
    holders = ca_data.get("holders", [])

    top_holders_percent = 0
    if holders:
        for holder in holders[:10]:
            top_holders_percent += float(holder.get("percent", 0))

    dex = ca_data.get("dex", [])
    trusted_token = ca_data.get("trusted_token")

    return SOLRiskOptions(
        is_mintable=is_mintable,
        metadata_mutable=metadata_mutable,
        freezable=freezable,
        closable=closable,
        non_transferable=non_transferable,
        balance_mutable=balance_mutable,
        transfer_fee=transfer_fee,
        transfer_fee_upgradable=transfer_fee_upgradable,
        transfer_hook=transfer_hook,
        default_account_state=default_account_state,
        symbol=symbol,
        name=name,
        description=description,
        total_supply=total_supply,
        holder_count=holder_count,
        top_holders_percent=top_holders_percent,
        holders=holders,
        dex=dex,
        trusted_token=trusted_token,
    )


# ========================================================================
# Process Token Risk Data
# ========================================================================

async def process_token_risk(chain_id: str, contract_address: str) -> RiskOptions | None:
    """
    Process token risk check data and return structured risk info

    Args:
        chain_id: Chain ID, e.g., "1" for Ethereum mainnet
        contract_address: Contract address

    Returns:
        dict: Dictionary containing risk assessment information
    """
    try:
        # Request token safety data
        token_data = await api_check_token_safety(chain_id, contract_address)

        # Ensure response is a dict and contains the contract address
        if not token_data or not isinstance(token_data, dict):
            logger.warning(f"GoPlus API did not return valid data: {contract_address}")
            return None

        ca_data = token_data.get(contract_address.lower())
        if not ca_data:
            logger.warning(f"Contract data not found in GoPlus API response: {contract_address}")
            return None

        risk_options = parse_goplus_data(ca_data)
        return risk_options

    except Exception as e:
        logger.error(f"Error processing token risk data: {str(e)}")
        return None


async def process_solana_token_risk(contract_address: str) -> SOLRiskOptions | None:
    """
    Process Solana token risk check data and return structured risk info

    Args:
        contract_address: Contract address

    Returns:
        dict: Dictionary containing risk assessment information
    """
    try:
        # Request token safety data
        token_data = await api_check_solana_token_safety(contract_address)

        # Ensure response is a dict and contains the contract address
        if not token_data or not isinstance(token_data, dict):
            logger.warning(f"GoPlus API did not return valid Solana token data: {contract_address}")
            return None

        ca_data = token_data.get(contract_address)
        if not ca_data:
            logger.warning(f"Contract data not found in GoPlus Solana data: {contract_address}")
            return None

        risk_options = parse_solana_token_data(ca_data)
        return risk_options

    except Exception as e:
        logger.error(f"Error processing Solana token risk data: {str(e)}")
        return None


async def process_sui_token_risk(contract_address: str):
    """
    Process Sui token risk check data and return structured risk info

    Args:
        contract_address: Contract address

    Returns:
        dict: Dictionary containing risk assessment information
    """
    try:
        # Request token safety data
        token_data = await api_check_sui_token_safety(contract_address)

        # Custom parsing logic can be added here for Sui's return format
        # Currently using generic parsing
        if not token_data or not isinstance(token_data, dict):
            logger.warning(f"GoPlus API did not return valid Sui token data: {contract_address}")
            return None

        ca_data = token_data.get(contract_address)
        if not ca_data:
            logger.warning(f"Contract data not found in GoPlus Sui data: {contract_address}")
            return None

        # TODO: Implement Sui-specific risk parsing function, currently returning raw data
        return ca_data

    except Exception as e:
        logger.error(f"Error processing Sui token risk data: {str(e)}")
        return None