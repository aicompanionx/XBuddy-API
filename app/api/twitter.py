from fastapi import APIRouter

from app.schemas.twitter import (
    RenameHistoryRequest,
    # TwitterStatisticRequest,
    # TwitterStatisticResponse,
    RenameHistoryResponse,
    TwitterUserInfoRequest,
    TwitterUserInfoResponse,
)
from app.services.external.getmoni_api import get_user_info
from app.services.twitter import get_rename_data_twitter
from app.utils.custom_exceptions import BadRequestException, ServerException
from app.utils.logger import get_logger

router = APIRouter(prefix="/twitter", tags=["Twitter Service"])
logger = get_logger(__name__)


# ========================================================================
# User Information
# ========================================================================
@router.post(
    "/user_info",
    response_model=TwitterUserInfoResponse,
    summary="Twitter User Information",
    description="Get Twitter user information",
)
async def api_twitter_user_info(req: TwitterUserInfoRequest):
    """
    Get Twitter user information
    """
    try:
        logger.debug(f"Requesting user info: {req.username}")
        result = await get_user_info(req.username)
        return TwitterUserInfoResponse(data=result)
    except BadRequestException as e:
        logger.warning(f"Invalid request: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Service failed: {str(e)}")
        raise ServerException(f"Twitter user information service error: {str(e)}")


# ========================================================================
# Rename History
# ========================================================================
@router.post(
    "/rename",
    response_model=RenameHistoryResponse,
    summary="Twitter Rename History",
    description="Get Twitter rename history and previous names",
)
async def api_twitter_rename_history(req: RenameHistoryRequest):
    """
    Analyze Twitter rename history
    """
    try:
        # Check if the URL is a valid Twitter URL
        url_str = req.url.lower()
        if not ("twitter.com" in url_str or "x.com" in url_str):
            raise BadRequestException(
                "Invalid Twitter URL, must be twitter.com or x.com"
            )

        logger.debug(f"Requesting rename history: {req.url}")
        result = await get_rename_data_twitter(req.url)
        return RenameHistoryResponse(data=result)
    except BadRequestException as e:
        logger.warning(f"Invalid request: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Service failed: {str(e)}")
        raise ServerException(f"Twitter rename analysis service error: {str(e)}")
