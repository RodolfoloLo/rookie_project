from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,func,delete
from ..models.history import History
from ..models.news import News
from datetime import datetime

async def add_history(
        db:AsyncSession,
        user_id:int,
        news_id:int
):
    query = select(History).where(History.user_id ==user_id,History.news_id ==news_id)
    result = await db.execute(query)
    existing_history = result.scalar_one_or_none()
    #这个用户浏览过这条新闻:
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    #这个用户未浏览过这条新闻
    else:
        history = History(user_id=user_id,news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history

async def get_list(
        db:AsyncSession,
        user_id:int,
        page:int = 1,
        page_size:int = 10
):
    count_query = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page-1)*page_size
    query = (select(News,History.view_time.label("history_view_time"),History.id.label("history_id"))
             .join(History,History.news_id == News.id)
             .where(History.user_id == user_id)
             .order_by(History.view_time.desc())
             .offset(offset).limit(page_size)
             )
    result = await db.execute(query)
    rows = result.all()
    return rows,total

async def delete_history(
        db:AsyncSession,
        user_id:int,
        news_id:int
):
    query = delete(History).where(History.news_id == news_id,History.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount>0

async def clear_history(
        db:AsyncSession,
        user_id:int
):
    query = delete(History).where(History.user_id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.rowcount or 0