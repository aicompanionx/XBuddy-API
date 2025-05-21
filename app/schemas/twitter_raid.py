from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.base import ApiBase


class TwitterRaidRequest(BaseModel):
    """
    Twitter raid request
    """

    token_name: str = Field(..., description="Token name")
    token_symbol: str = Field(..., description="Token symbol")
    token_ca: str = Field(..., description="Token contract address")
    token_description: str = Field(..., description="Token description")
    logo_content: Optional[str] = Field("", description="Logo content")

    chain: Optional[str] = Field(None, description="Chain to raid on")


class Tweet(BaseModel):
    """
    Tweet data model
    """

    url: str = Field(..., description="Tweet URL")
    text: str = Field(..., description="Tweet content")
    retweetCount: int = Field(0, description="Retweet count")
    replyCount: int = Field(0, description="Reply count")
    likeCount: int = Field(0, description="Like count")
    quoteCount: int = Field(0, description="Quote count")
    viewCount: int = Field(0, description="View count")
    createdAt: str = Field(
        ..., description="Creation time, e.g. 'Tue Dec 10 07:00:30 +0000 2024'"
    )
    bookmarkCount: int = Field(0, description="Bookmark count")
    isReply: bool = Field(False, description="Is reply")
    # id: str = Field(..., description="Tweet ID")
    # source: str = Field(..., description="Tweet source, e.g. 'Twitter for iPhone'")
    # lang: Optional[str] = Field(None, description="Tweet language, e.g. 'en'")
    # inReplyToId: Optional[str] = Field(None, description="Reply to tweet ID")
    # conversationId: Optional[str] = Field(None, description="Conversation ID")
    # inReplyToUserId: Optional[str] = Field(None, description="Reply to user ID")
    # inReplyToUsername: Optional[str] = Field(None, description="Reply to username")
    # author: dict = Field(..., description="Tweet author information")
    # entities: Optional[dict] = Field(None, description="Entities in tweet, e.g. hashtags, links, mentions")
    # quoted_tweet: Optional[dict] = Field(None, description="Quoted tweet")
    retweeted_tweet: Optional[dict] = Field(None, description="Retweeted tweet")

    def to_prompt(self):
        """
        Convert tweet to natural language description
        """
        return f"""
Tweet link: {self.url}
Content: {self.text}
Engagement metrics:
- Retweets: {self.retweetCount}
- Replies: {self.replyCount}
- Likes: {self.likeCount}
- Quotes: {self.quoteCount}
- Views: {self.viewCount}
- Bookmarks: {self.bookmarkCount}
Posted at: {self.createdAt}
Type: {"Reply to someone" if self.isReply else "Original tweet"}
        """


class TwitterRaidData(BaseModel):
    """
    Twitter raid data
    """

    title: str = Field(..., description="Title of the target")
    twitter_url: str = Field(..., description="Target's Twitter URL")
    name: str = Field(..., description="Target's name")

    #   Tweet related
    tweet_url: str = Field(..., description="Raid tweet URL")
    raid_content: str = Field(..., description="Raid content")


class TwitterRaidResponse(ApiBase[TwitterRaidData]):
    """
    Twitter raid response
    """

    pass
