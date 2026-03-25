from ..config.cache_config import get_json_cache,set_cache
from typing import Any, Optional

CATEGORIES_KEY = "news:categories"
NEWS_LIST_PREFIX = "news_list:"

#获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)

#写入新闻分类缓存:缓存的数据,过期时间
async def set_cached_categories(
        data:list[dict[str,Any]],
        expire:int = 7200#数据越稳定,缓存越持久   要避免所有的key同时过期,引起缓存雪崩
):
    return await set_cache(CATEGORIES_KEY,data,expire)

#写入新闻列表缓存 key = news_list:分类id:页码:每页数量+列表数据+过期时间
async def set_cache_news_list(
        category_id:Optional[int],
        page:int,
        page_size:int,
        news_list:list[dict[str,Any]],
        expire:int = 1800
):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{page_size}"
    return await set_cache(key,news_list,expire)

#读取新闻列表缓存
async def get_cached_news_list(
        category_id:int,
        page:int,
        page_size:int
):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{page_size}"
    return await get_json_cache(key)


async def get_cached_news_detail(
        news_id:int
) -> Optional[dict[str,Any]]:
    key = f"news_detail:{news_id}"
    return await get_json_cache(key)

async def cache_news_detail(
        news_id:int,
        news_detail:dict[str,Any],
        expire:int = 300
) -> bool:
    key = f"news_detail:{news_id}"
    return await set_cache(key,news_detail,expire)

async def get_cached_related_news(
        news_id:int,
        category_id:int
) -> Optional[list[dict[str,Any]]]:
    key = f"related_news:{news_id}:{category_id}"
    return await get_json_cache(key)

async def cache_related_news(
        news_id:int,
        category_id:int,
        related_news:list[dict[str,Any]],
        expire:int = 1800
) -> bool:
    key = f"related_news:{news_id}:{category_id}"
    return await set_cache(key,related_news,expire)