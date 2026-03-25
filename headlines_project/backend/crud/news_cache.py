from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from ..models.news import Category,News
from sqlalchemy import update
from ..cache.news_cache import get_cached_categories,set_cached_categories,get_cached_news_list,set_cache_news_list,get_cached_news_detail,cache_news_detail,get_cached_related_news,cache_related_news
from fastapi.encoders import jsonable_encoder
from ..schemas.base import NewsItemBase
from ..schemas.news import NewsDetailResponse, RelatedNewsResponse

async def get_categories(
        db:AsyncSession,
        skip:int = 0,
        limit:int = 100
):
    #先尝试从缓存中获取数据
    cached_categories = await get_cached_categories()
    if cached_categories:
        return cached_categories
    #缓存中没有数据,照常查库
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()
    #写入缓存
    if categories:
        categories = jsonable_encoder(categories)#把Python对象转换为JSON可序列化的格式  JSON可序列化的格式包括基本数据类型(如字符串、数字、布尔值)以及列表和字典等复杂数据结构  但不包括自定义对象或数据库模型实例
        await set_cached_categories(categories)
    #返回数据
    return categories#FastAPI会自动将返回的Python对象转换为JSON格式响应

async def get_news_list(
        db:AsyncSession,
        category_id:int,
        skip:int = 0,#skip = (page - 1) * page_size
        limit:int =  10
):
    #先尝试从缓存中获取数据
    page = skip // limit +1 #//是整数除法,向下取整
    cached_list = await get_cached_news_list(category_id,page,limit)
    if cached_list:
        return [News(**item) for item in cached_list]
    #缓存中没有数据,照常查库
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()
    #写入缓存
    if news_list:
        news_data = [NewsItemBase.model_validate(item).model_dump(mode="json",by_alias=False) for item in news_list]
        await set_cache_news_list(category_id,page,limit,news_data)
    #返回数据
    return news_list

async def get_news_count(
        db:AsyncSession,
        category_id:int
):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()



async def get_news_details(
        db:AsyncSession,
        news_id:int
):
    cached_news = await get_cached_news_detail(news_id)
    if cached_news:
        return NewsDetailResponse.model_validate(cached_news)#model_validate()方法会将从缓存中获取的字典数据转换为NewsDetailResponse模型实例,这样我们就可以像使用普通的NewsDetailResponse对象一样使用它了
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news =  result.scalar_one_or_none()
    if news:
        detail_model = NewsDetailResponse.model_validate(news)
        await cache_news_detail(
            news_id,
            detail_model.model_dump(mode="json", by_alias=True, exclude={"related_news"}),#model_dump()方法会将NewsDetailResponse模型实例转换为字典数据,并且通过exclude参数排除掉related_news字段(因为related_news是一个列表,可能会比较大,我们不需要把它缓存到Redis中),mode="json"表示在转换过程中会自动处理日期等特殊类型的数据,by_alias=True表示在转换后的字典中使用字段的别名(如categoryId)而不是原始名称(category_id)作为键,这样可以保持与API接口定义的一致性
        )
        return detail_model
    return None

async def increase_news_views(
        db:AsyncSession,
        news_id:int
):
    stmt = update(News).where(News.id == news_id).values(views=News.views+1)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount>0#数据库更新操作时检查是否命中了数据

#不仅MySQL的数据库要增加浏览量,还要更新缓存中的浏览量,以保持数据的一致性
async def update_cached_news_views(news_id: int, views: int):
    cached_news = await get_cached_news_detail(news_id)
    if not cached_news:
        return
    detail_model = NewsDetailResponse.model_validate(cached_news)
    detail_model.views = views
    await cache_news_detail(
        news_id,
        detail_model.model_dump(mode="json", by_alias=True, exclude={"related_news"}),
    )

async def get_related_news(
        db:AsyncSession,
        news_id:int,
        category_id:int,
        limit:int = 5
):
    cached_related = await get_cached_related_news(news_id,category_id)
    if cached_related:
        return [RelatedNewsResponse.model_validate(item) for item in cached_related]
    stmt = select(News).where(News.category_id == category_id).where(News.id != news_id).order_by(News.views.desc(),News.publish_time.desc()).limit(limit)
    result = await db.execute(stmt)
    #result = result.scalars().all()
    related_news = result.scalars().all()
    if related_news:
        related_data = [
            RelatedNewsResponse.model_validate(item).model_dump(mode="json", by_alias=True)
            for item in related_news
        ]
        await cache_related_news(news_id,category_id,related_data)
        return [RelatedNewsResponse.model_validate(item) for item in related_data]
    return []