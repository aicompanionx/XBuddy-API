import logging

from fastapi import APIRouter

from app.schemas.ai import (
    ImageRecognitionData,
    ImageRecognitionRequest,
    ImageRecognitionResponse,
)
from app.services.agent.image_recognition import ai_image_recognition
from app.utils.custom_exceptions import BadRequestException, ServerException
from app.utils.network_utils import is_public_url

router = APIRouter(prefix="/ai", tags=["AI functionality (non-stream)"])
logger = logging.getLogger(__name__)


@router.post(
    "/image_recognition",
    response_model=ImageRecognitionResponse,
    summary="Image recognition",
    description="Recognize image",
)
async def recognize_image(req: ImageRecognitionRequest):
    """
    Recognize image content and describe it with text
    """
    if not is_public_url(req.image_url):
        raise BadRequestException("Image URL must resolve to a public IP address.")

    try:
        text = await ai_image_recognition(req.image_url)
        result = ImageRecognitionData(text=text)
        return ImageRecognitionResponse(data=result)
    except Exception as e:
        logger.error(f"Failed to recognize image: {str(e)}")
        raise ServerException(f"Failed to recognize image: {str(e)}")
