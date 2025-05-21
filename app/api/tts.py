import base64
import logging

from fastapi import APIRouter

from app.schemas.tts import (
    TtsAudioData,
    TtsAudioResponse,
    TtsOptimizeRequest,
    TtsOptimizeResponse,
    TtsRequest,
)
from app.services.tts import optimize_text_for_tts, text_to_speech
from app.utils.custom_exceptions import ServerException

router = APIRouter(prefix="/tts", tags=["Text-to-Speech"])
logger = logging.getLogger(__name__)


@router.post(
    "/optimize",
    response_model=TtsOptimizeResponse,
    summary="Optimize TTS text",
    description="Optimize the input text to get better TTS results",
)
async def optimize_text(req: TtsOptimizeRequest):
    """
    Optimize TTS text
    """
    try:
        result = await optimize_text_for_tts(req.text)
        return TtsOptimizeResponse(code=0, msg="success", data=result)
    except Exception as e:
        logger.error(f"Failed to optimize text: {str(e)}")
        raise ServerException(f"Failed to optimize text: {str(e)}")


@router.post(
    "/generate",
    response_model=TtsAudioResponse,
    summary="Generate audio",
    description="Generate audio from text and return the Base64 encoded audio data",
)
async def generate_speech(req: TtsRequest):
    """
    Generate audio
    """
    try:
        text = req.text

        # Optimize text if needed
        if req.optimize:
            try:
                optimized = await optimize_text_for_tts(text)
                text = optimized.optimized_text
            except Exception as e:
                logger.warning(
                    f"Failed to optimize text, will use the original text: {str(e)}"
                )

        audio_data = await text_to_speech(
            text=text,
        )

        # Convert binary data to Base64
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")

        # Concatenate into data:audio/ format;base64,Base64 string
        audio_base64_with_prefix = f"data:audio/mp3;base64,{audio_base64}"

        response_data = TtsAudioData(
            audio_base64=audio_base64_with_prefix,
            format="mp3",
            content_type="audio/mp3",
        )

        return TtsAudioResponse(
            code=0, msg="Audio generated successfully", data=response_data
        )

    except Exception as e:
        logger.error(f"Failed to generate audio: {str(e)}")
        raise ServerException(f"Failed to generate audio: {str(e)}")
