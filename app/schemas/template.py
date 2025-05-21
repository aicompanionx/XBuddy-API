from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import ApiBase


class Request(BaseModel):
    """
    Request
    """

    name: Optional[str] = Field(None, description="name")


class Data(BaseModel):
    """
    Data
    """

    data: str = Field(..., description="data")


class Response(ApiBase[Data]):
    """
    Response
    """

    pass
