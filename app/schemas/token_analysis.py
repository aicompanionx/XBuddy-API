from pydantic import BaseModel, Field

from app.schemas.base import ApiBase


class TokenAnalysisRequest(BaseModel):
    """
    Token analysis request
    """

    chain: str = Field(..., description="Blockchain name")
    ca: str = Field(..., description="Contract address")
    lang: str = Field("en", description="Language of response, default is English")
    session_id: str = Field(
        ..., description="Conversation ID, used to save chat context"
    )


class TokenAnalysisData(BaseModel):
    """
    Token analysis data
    """

    chain: str = Field(..., description="Blockchain name")
    ca: str = Field(..., description="Contract address")
    result: str = Field(..., description="Analysis result")


class TokenAnalysisResponse(ApiBase[TokenAnalysisData]):
    """
    Token analysis response
    """

    pass
