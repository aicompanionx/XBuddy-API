import logging
from fastapi import APIRouter

from app.services.agent.image_recognition import ai_image_recognition
from app.utils.custom_exceptions import ServerException
from app.schemas.ai import ImageRecognitionRequest, ImageRecognitionData, ImageRecognitionResponse

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
    try:
        text = await ai_image_recognition(req.image_url)
        result = ImageRecognitionData(text=text)
        return ImageRecognitionResponse(data=result)
    except Exception as e:
        logger.error(f"Failed to recognize image: {str(e)}")
        raise ServerException(f"Failed to recognize image: {str(e)}")
