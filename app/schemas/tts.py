from pydantic import BaseModel, Field

from app.schemas.base import ApiBase


class TtsRequest(BaseModel):
    """
    Text-to-speech request parameters
    """

    text: str = Field(..., description="Text to be converted")
    optimize: bool = Field(True, description="Whether to use AI to optimize the text")


class TtsOptimizeRequest(BaseModel):
    """
    Request for optimizing TTS text
    """

    text: str = Field(..., description="Text to be optimized")


class TtsOptimizeData(BaseModel):
    """
    Optimized text data
    """

    optimized_text: str = Field(..., description="Optimized text")


class TtsAudioData(BaseModel):
    """
    Audio synthesis data
    """

    audio_base64: str = Field(..., description="Base64 encoded audio data")
    format: str = Field(..., description="Audio format")
    content_type: str = Field(..., description="Audio content type")


class TtsOptimizeResponse(ApiBase[TtsOptimizeData]):
    """
    Text optimization response
    """

    pass


class TtsAudioResponse(ApiBase[TtsAudioData]):
    """
    Audio synthesis response
    """

    pass
