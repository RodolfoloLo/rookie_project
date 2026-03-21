from fastapi import APIRouter, Query, Depends, HTTPException
from ..models.users import User
from ..utils.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from ..config.db_config import get_database
from ..crud import favorite
from ..utils.response import success_response
from ..schemas.favorite import FavoriteCheckResponse, FavoriteAddRequest,FavoriteAddResponse,FavoriteListResponse
from starlette import status

router = APIRouter(prefix="/api/favorite",tags=["favorite"])

@router.get("/check")
async def check_favorite(
        news_id:int = Query(...,alias="newsId"),
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_database)
):
     is_favorite = await favorite.is_news_favorite(db,user.id,news_id)
     return success_response(message="检查收藏状态成功",data=FavoriteCheckResponse(isFavorite=is_favorite))

@router.post("/add")
async def add_favorite(
        data:FavoriteAddRequest,
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_database)
):
    result = await favorite.add_news_favorite(db,user.id,data.news_id)
    response_data = FavoriteAddResponse.model_validate(result)
    return success_response(message="添加收藏成功",data=response_data)

@router.delete("/remove")
async def remove_favorite(
        news_id:int = Query(...,alias="newsId"),
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_database)
):
    result = await favorite.remove_news_favorite(db,user.id,news_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="收藏记录不存在")
    return success_response(message="取消收藏成功")

@router.get("/list")
async def get_favorite_list(
        page:int = Query(default=1,ge=1),
        page_size:int = Query(10,ge=1,le=100,alias="pageSize"),
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_database)
):
    rows,total = await favorite.get_favorite_list(db,user.id,page,page_size)
    favorite_list = [{
        **news.__dict__,
        "favorite_time":favorite_time,
        "favorite_id":favorite_id
    } for news,favorite_time,favorite_id in rows]
    has_more = total > page*page_size
    data = FavoriteListResponse(list=favorite_list,total=total,hasMore=has_more)
    return success_response(message="获取收藏列表成功",data=data)

@router.delete("/clear")
async def clear_favorite_list(
        user:User = Depends(get_current_user),
        db:AsyncSession = Depends(get_database)
):
    count = await favorite.clear_favorite_list(db,user.id)
    return success_response(message=f"清空了{count}条记录")