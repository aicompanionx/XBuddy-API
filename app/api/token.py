import logging

from fastapi import APIRouter

from app.schemas.token import (
    CAFromTwitterRequest,
    CAFromTwitterResponse,
    CheckSOLTokenRequest,
    CheckSOLTokenResponse,
    CheckTokenRequest,
    CheckTokenResponse,
    TokenChainData,
    TokenChainRequest,
    TokenChainResponse,
    TokenDetailRequest,
    TokenDetailResponse,
    TokenPairsRequest,
    TokenPairsResponse,
    TwitterFromCAData,
    TwitterFromCARequest,
    TwitterFromCAResponse,
)
from app.services.external.coingecko_api import get_token_desc
from app.services.external.dex_sreener_api import get_pairs_base
from app.services.token import (
    check_sol_token_safety as check_sol_token_safety_service,
)
from app.services.token import (
    check_token_safety_api,
    get_ca_from_twitter,
    get_twitter_from_ca,
    identify_token_chain,
)
from app.utils.custom_exceptions import BadRequestException, ExternalApiException

router = APIRouter(prefix="/token", tags=["Token Service"])

logger = logging.getLogger(__name__)


# ========================================================================
# Check token safety
# ========================================================================
@router.post(
    "/check",
    response_model=CheckTokenResponse,
    summary="Check token safety",
    description="Check token safety by providing the chain name and contract address",
)
async def check_token_safety(req: CheckTokenRequest):
    """
    Check token safety
    """
    result = await check_token_safety_api(req.chain, req.ca)
    return CheckTokenResponse(data=result)


# ========================================================================
# Check SOL token safety
# ========================================================================
@router.post(
    "/check-sol",
    response_model=CheckSOLTokenResponse,
    summary="Check SOL token safety",
    description="Check SOL token safety by providing the contract address",
)
async def check_sol_token_safety(req: CheckSOLTokenRequest):
    """
    Check SOL token safety
    """
    result = await check_sol_token_safety_service(req.ca)
    return CheckSOLTokenResponse(data=result)


# ========================================================================
# Get CA from Twitter
# ========================================================================
@router.post(
    "/ca-by-twitter",
    response_model=CAFromTwitterResponse,
    summary="Get CA from Twitter username",
    description="Get CA from Twitter username",
)
async def get_ca_by_twitter(req: CAFromTwitterRequest):
    """
    Get CA from Twitter username
    """
    token_data = await get_ca_from_twitter(req.twitter_name)

    return CAFromTwitterResponse(data=token_data)


# ========================================================================
# Get Twitter from CA
# ========================================================================
@router.post(
    "/twitter-by-ca",
    response_model=TwitterFromCAResponse,
    summary="Get Twitter username from CA",
    description="Get Twitter username from CA",
)
async def get_twitter_by_ca(req: TwitterFromCARequest):
    """
    Get Twitter username from CA
    """
    twitter_data: TwitterFromCAData = await get_twitter_from_ca(req.ca)

    return TwitterFromCAResponse(data=twitter_data)


# ========================================================================
# Get token info from pool
# ========================================================================
@router.post(
    "/token-by-pool",
    response_model=TokenPairsResponse,
    summary="Get token info from pool address",
    description="Get token info from pool address",
)
async def get_token_by_pool(req: TokenPairsRequest):
    """
    Get token info from pool address
    """
    token_data = await get_pairs_base(req.chain, req.pa)
    return TokenPairsResponse(data=token_data)


# ========================================================================
# Get token detail from CA
# ========================================================================
@router.post(
    "/token-detail-by-ca",
    response_model=TokenDetailResponse,
    summary="Get token detail from CA",
    description="Get token detail from CA",
)
async def get_token_detail_by_ca(req: TokenDetailRequest):
    """
    Get token detail from CA
    """
    try:
        result = await get_token_desc(req.chain, req.ca)
        return TokenDetailResponse(data=result)
    except ExternalApiException as e:
        logger.error(f"Get token detail failed: {str(e)}")
        raise BadRequestException(f"Get token detail failed: {str(e)}")


# ========================================================================
# Get token chain from CA
# ========================================================================
@router.post(
    "/chain-by-ca",
    response_model=TokenChainResponse,
    summary="Get token chain from CA",
    description="Get token chain from CA",
)
async def get_token_chain_by_ca(req: TokenChainRequest):
    """
    Get token chain from CA
    """
    try:
        chain_info = await identify_token_chain(req.ca)
        result = TokenChainData(chain=chain_info)
        return TokenChainResponse(data=result)
    except ExternalApiException as e:
        logger.error(f"Get token chain failed: {str(e)}")
        raise BadRequestException(f"Get token chain failed: {str(e)}")
