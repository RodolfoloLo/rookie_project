from fastapi import APIRouter,Depends,Query,HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from ..config.db_config import get_database
from ..crud import news

#创建APIRouter实例

router = APIRouter(prefix="/api/news",tags=["news"])
#prefix:路由前缀 tags:路由标签

@router.get("/categories")
async def get_categories(
        skip:int = 0,
        limit:int = 100,
        db:AsyncSession = Depends(get_database)
):
    categories = await news.get_categories(db,skip,limit)
    return {
        "code":200,
        "message":"获取新闻分类成功",
        "data":jsonable_encoder(categories)
    }

@router.get("/list")
async def get_news_list(
        category_id:int = Query(alias="categoryId"),
        page:int = 1,
        page_size:int =  Query(10,alias="pageSize",le=100),
        db:AsyncSession = Depends(get_database)
):
    offset = (page - 1) * page_size
    news_list = await news.get_news_list(db,category_id,offset,page_size)
    total = await news.get_news_count(db,category_id)
    has_more = (offset+len(news_list)) < total
    return{
        "code":200,
        "message":"获取新闻列表成功",
        "data":{
            "list":jsonable_encoder(news_list),
            "total":total,
            "hasMore":has_more
        }
    }

@router.get("/details")
async def get_news_details(
        news_id:int = Query(alias="id"),
        db:AsyncSession = Depends(get_database)
):
    news_details = await news.get_news_details(db,news_id)
    if not news_details:
        raise HTTPException(status_code=404,detail="新闻不存在")

    views_result = await news.increase_news_views(db,news_details.id)
    if not views_result:
        raise HTTPException(status_code=500,detail="新闻不存在")

    related_news = await news.get_related_news(db,news_details.id,news_details.category_id)


    return {
        "code":200,
        "message":"success",
        "data":{
            "id":news_details.id,
            "title":news_details.title,
            "content":news_details.content,
            "image":news_details.image,
            "author":news_details.author,
            "publishTime":news_details.publish_time,
            "categoryId":news_details.category_id,
            "views":news_details.views,
            "relatedNews":related_news
        }
    }