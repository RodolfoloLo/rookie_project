from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func
from ..models.news import Category,News
from sqlalchemy import update
from ..cache.news_cache import get_cached_categories,set_cached_categories,get_cached_news_list,set_cache_news_list
from fastapi.encoders import jsonable_encoder
from ..schemas.base import NewsItemBase

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
        categories = jsonable_encoder(categories)
        await set_cached_categories(categories)
    #返回数据
    return categories

async def get_news_list(
        db:AsyncSession,
        category_id:int,
        skip:int = 0,#skip = (page - 1) * page_size
        limit:int =  10
):
    #先尝试从缓存中获取数据
    page = skip // limit +1
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
    news_list =  result.scalar_one()

    return news_list

async def get_news_details(
        db:AsyncSession,
        news_id:int
):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def increase_news_views(
        db:AsyncSession,
        news_id:int
):
    stmt = update(News).where(News.id == news_id).values(views=News.views+1)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount>0#数据库更新操作时检查是否命中了数据

async def get_related_news(
        db:AsyncSession,
        news_id:int,
        category_id:int,
        limit:int = 5
):
    stmt = select(News).where(News.category_id == category_id).where(News.id != news_id).order_by(News.views.desc(),News.publish_time.desc()).limit(limit)
    result = await db.execute(stmt)
    #result = result.scalars().all()
    related_news = result.scalars().all()
    return [{
        "id": news_details.id,
        "title": news_details.title,
        "content": news_details.content,
        "image": news_details.image,
        "author": news_details.author,
        "publishTime": news_details.publish_time,
        "categoryId": news_details.category_id,
        "views": news_details.views
    } for news_details in related_news]