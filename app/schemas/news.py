from pydantic import BaseModel, Field


class News(BaseModel):
    """
    Fields in the news message queue
    """
    title: str = Field(..., description="Title")
    abstract: str = Field(..., description="Abstract")
    cover_img: str = Field(..., description="Cover image")
    published_at: int = Field(..., description="Published timestamp, accurate to seconds")
    origin_url: str = Field(..., description="Origin URL")
    news_url: str = Field(..., description="Article URL, currently also the origin URL, redundant field for transition handling")
    source_id: str = Field(..., description="Platform ID in the platform: platform label + platform article ID")
    source_type: int = Field(..., description="Platform type ID: 5 for Odaily, 6 for The Block Beasts")
    source_name: str = Field(..., description="Platform type name: such as Odaily, The Block Beasts")
    type: int = Field(default=2, description="Processing type, currently only 2")
    sort_id: int = Field(..., description="Category ID: 1 for flash news, 2 for long articles")
    id: int = Field(default=0, description="ID")