from pydantic import BaseModel, Field
from app.schemas.base import ApiBase


class PhishingRequest(BaseModel):
    """
    Phishing website detection request
    """
    url: str = Field(..., description="URL to be detected")
    lang: str = Field("en", description="Language of the response, default is English")


class PhishingData(BaseModel):
    """
    Phishing website detection data
    """
    url: str = Field(..., description="URL to be detected")
    isPhishing: bool = Field(..., description="Whether it is a phishing website")
    message: str = Field(..., description="Detection result description")


class PhishingResponse(ApiBase[PhishingData]):
    """
    Phishing website detection response
    """
    pass
