from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import ApiBase


class RenameHistory(BaseModel):
    """
    Twitter rename history
    """

    name: str = Field(..., description="Historical name")
    start_date: str = Field(..., description="Start date of using this name")
    end_date: str = Field(..., description="End date of using this name")


class RenameHistoryRequest(BaseModel):
    """
    Twitter rename request
    """

    url: str = Field(..., description="Twitter URL to be analyzed")
    lang: str = Field("en", description="Response language, default is English")


class RenameHistoryData(BaseModel):
    """
    Twitter rename response model
    """

    id: str = Field(..., description="Twitter user ID")
    screen_names: list[RenameHistory] = Field(..., description="Historical name list")
    name: str = Field(..., description="Current name")


class RenameHistoryResponse(ApiBase[RenameHistoryData]):
    """
    Twitter rename API response model
    """

    pass


# -------------------------------------------------------------------- #


class TwitterUserInfoRequest(BaseModel):
    """
    Twitter user information request
    """

    username: str = Field(..., description="Twitter username")
    lang: str = Field("en", description="Response language, default is English")


class TwitterUserInfoData(BaseModel):
    """
    Twitter user information data
    """

    score: int = Field(0, description="User score")
    twitterUrl: str = Field("", description="Twitter URL")
    name: str = Field("", description="Display name")
    description: Optional[str] = Field(None, description="User description")
    followersCount: int = Field(0, description="Followers count")
    smartMentionsCount: int = Field(0, description="Smart mentions count")
    type: str = Field("", description="Account type")
    smartFollowersCount: int = Field(0, description="Smart followers count")
    smartLevel: int = Field(0, description="User smart level")
    mentions: int = Field(0, description="Mentions")
    InfluenceLevel: str = Field("Level 0", description="Influence level")


class TwitterUserInfoResponse(ApiBase[TwitterUserInfoData]):
    """
    Twitter user information response
    """

    pass
