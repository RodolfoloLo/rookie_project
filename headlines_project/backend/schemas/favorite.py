from pydantic import BaseModel, Field, ConfigDict
from .base import NewsItemBase
from datetime import datetime

class FavoriteCheckResponse(BaseModel):
    is_favorite:bool = Field(...,alias="isFavorite")

class FavoriteAddRequest(BaseModel):
    news_id:int = Field(...,alias="newsId")

class FavoriteAddResponse(BaseModel):
    id:int
    user_id:int = Field(...,alias="userId")
    news_id:int = Field(...,alias="newsId")
    created_at:datetime = Field(...,alias="createTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

class FavoriteNewsItemResponse(NewsItemBase):
    favorite_time:datetime = Field(alias="favoriteTime")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
    )

class FavoriteListResponse(BaseModel):
    list:list[FavoriteNewsItemResponse]
    total:int
    has_more:bool = Field(alias="hasMore")

    model_config = ConfigDict(
        populate_by_name = True,
        from_attributes = True
    )