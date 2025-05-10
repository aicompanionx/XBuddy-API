# ============================================================================
# Get token safety information
# ============================================================================

async def get_token_safety_info(chain_id: str, contract_address: str) -> RiskOptions | None:
    """
    Get token safety information
    
    Args:
        chain_id: chain id, e.g. "1" for Ethereum mainnet
        contract_address: contract address
        
    Returns:
        dict: token safety information
    """
    try:
        # request GoPlus API
        token_data = await api_check_token_safety(chain_id, contract_address)
        
        # ensure response is a dict and contains contract address
        if not token_data or not isinstance(token_data, dict):
            logger.warning(f"GoPlus API did not return valid data: {contract_address}")
            return None
            
        # get contract address data
        ca_data = token_data.get(contract_address.lower())
        if not ca_data:
            logger.warning(f"Contract data not found in GoPlus response: {contract_address}")
            return None
            
        # parse risk data
        risk_options = parse_goplus_data(ca_data)
        
        # return risk options as a dict
        return risk_options
        
    except Exception as e:
        logger.error(f"Failed to get token safety information: {str(e)}")
        return None


# ============================================================================
# Get Solana token safety information
# ============================================================================

async def get_solana_token_safety_info(contract_address: str) -> SOLRiskOptions | None:
    """
    Get Solana token safety information
    
    Args:
        contract_address: contract address
        
    Returns:
        dict: Solana token safety information
    """
    try:
        # request GoPlus API
        token_data = await api_check_solana_token_safety(contract_address)
        
        # ensure response is a dict and contains contract address
        if not token_data or not isinstance(token_data, dict):
            logger.warning(f"GoPlus API did not return valid Solana token data: {contract_address}")
            return None
            
        # get contract address data
        ca_data = token_data.get(contract_address)
        if not ca_data:
            logger.warning(f"Contract data not found in GoPlus Solana response: {contract_address}")
            return None
            
        # parse risk data
        risk_options = parse_solana_token_data(ca_data)
        
        # return risk options as a dict
        return risk_options
        
    except Exception as e:
        logger.error(f"Failed to get Solana token safety information: {str(e)}")
        return None


# ============================================================================
# Get Sui token safety information
# ============================================================================

async def get_sui_token_safety_info(contract_address: str):
    """
    Get Sui token safety information
    
    Args:
        contract_address: contract address
        
    Returns:
        dict: Sui token safety information
    """
    try:
        # request GoPlus API
        token_data = await api_check_sui_token_safety(contract_address)
        
        # ensure response is a dict and contains contract address
        if not token_data or not isinstance(token_data, dict):
            logger.warning(f"GoPlus API did not return valid Sui token data: {contract_address}")
            return None
            
        # get contract address data
        ca_data = token_data.get(contract_address)
        if not ca_data:
            logger.warning(f"Contract data not found in GoPlus Sui response: {contract_address}")
            return None
            
        # return raw data for now
        return ca_data
        
    except Exception as e:
        logger.error(f"Failed to get Sui token safety information: {str(e)}")
        return None