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
#model_config = ConfigDict(from_attributes=True)表示这个模型可以从一个对象的属性中创建实例,而不仅仅是从字典数据中创建实例  populate_by_name=True表示在创建模型实例时,可以使用字段的别名(如categoryId)来提供数据,而不仅仅是使用字段的原始名称(category_id)
#models文件夹中定义的模型是用来定义数据库表结构的,不可以创建实例,而schemas文件夹中的模型是用来定义API接口的数据结构的,可以创建实例,并且可以使用Pydantic提供的各种功能来验证和处理数据

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
