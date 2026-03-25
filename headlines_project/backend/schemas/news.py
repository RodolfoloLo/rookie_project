from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RelatedNewsResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int = Field(alias="categoryId")
    publish_time: Optional[datetime] = Field(None, alias="publishTime")
    views: int

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class NewsDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    image: Optional[str] = None
    author: Optional[str] = None
    publish_time: Optional[datetime] = Field(None, alias="publishTime")
    category_id: int = Field(alias="categoryId")
    views: int
    related_news: list[RelatedNewsResponse] = Field(default_factory=list, alias="relatedNews")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
