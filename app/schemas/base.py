from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar('T')

class ApiBase(BaseModel, Generic[T]):
    """
    API unified response model
    
    Contains the standard structure for all API responses
    """
    code: int = Field(default=0, description="Status code")
    msg: str = Field(default="success", description="Response message")
    data: Optional[T] = Field(default=None, description="Response data")