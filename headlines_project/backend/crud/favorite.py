from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete,func
from ..models.favorite import Favorite
from ..models.news import News


async def is_news_favorite(
        db:AsyncSession,
        user_id:int,
        news_id:int
):
    query = select(Favorite).where(Favorite.user_id ==user_id,Favorite.news_id == news_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None

async def add_news_favorite(
        db:AsyncSession,
        user_id:int,
        news_id:int
):
    favorite = Favorite(user_id=user_id,news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

async def remove_news_favorite(
        db:AsyncSession,
        user_id:int,
        news_id:int
):
    query = delete(Favorite).where(Favorite.user_id ==user_id,Favorite.news_id == news_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0

async def get_favorite_list(
        db:AsyncSession,
        user_id:int,
        page:int = 1,
        page_size:int = 10
):
    #总量+收藏的新闻列表
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()
    #获取收藏列表-连表查询join()+收藏时间排序+分页limit()+offset()
    offset = (page-1)*page_size
    query = (select(News,Favorite.created_at.label("favorite_created_at"),Favorite.id.label("favorite_id"))
             .join(Favorite,Favorite.news_id == News.id)
             .where(Favorite.user_id == user_id)
             .order_by(Favorite.created_at.desc())
             .offset(offset).limit(page_size)
             )
    result = await db.execute(query)
    rows = result.all()
    return rows,total

async def clear_favorite_list(
        db:AsyncSession,
        user_id:int
):
    query = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount or 0