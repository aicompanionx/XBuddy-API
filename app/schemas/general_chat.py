from pydantic import BaseModel, Field
from app.schemas.base import ApiBase


class GeneralChatRequest(BaseModel):
    """
    General chat request
    """
    content: str = Field(..., description="Chat content")
    lang: str = Field("en", description="Response language, default is English")
    session_id: str = Field(..., description="Session ID used to save chat context")


class GeneralChatData(BaseModel):
    """
    General chat data
    """
    content: str = Field(..., description="Chat content")
    result: str = Field(..., description="Response result")


class GeneralChatResponse(ApiBase[GeneralChatData]):
    """
    General chat response
    """
    pass