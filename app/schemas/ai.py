from pydantic import BaseModel, Field

from app.schemas.base import ApiBase


class ImageRecognitionRequest(BaseModel):
    """Image recognition request"""
    image_url: str = Field(..., description="Image URL")

class ImageRecognitionData(BaseModel):
    """Image recognition data"""
    text: str = Field(..., description="Description of the content in the image")

class ImageRecognitionResponse(ApiBase[ImageRecognitionData]):
    """Image recognition response"""
    pass