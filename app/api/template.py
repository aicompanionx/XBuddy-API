import logging

from fastapi import APIRouter

from app.schemas.template import Data, Request, Response
from app.utils.custom_exceptions import ServerException

router = APIRouter(prefix="/Route", tags=["Route Introduction Group"])
logger = logging.getLogger(__name__)


@router.post(
    "/get_xxx",
    response_model=Response,
    description="Get some data",
)
async def api_xxxxx(req: Request):
    """
    Get some data
    """
    try:
        result = Data(data="")
        return Response(data=result)
    except Exception as e:
        logger.error(f"Failed to get data: {str(e)}")
        raise ServerException(f"Failed to get data: {str(e)}")
