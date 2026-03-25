import json
import os
from typing import Any
import redis.asyncio as redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

#创建Redis的连接对象
redis_client = redis.Redis(
    host = REDIS_HOST,
    port = REDIS_PORT,
    db = REDIS_DB,
    password = REDIS_PASSWORD or None,
    socket_timeout = 3,
    socket_connect_timeout = 3,
    decode_responses = True#是否将字节数据解码为字符串
)

#设置 和 读取 (字符串)

#读取:字符串:
async def get_cache(key:str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败:{e}")
        return None

#读取:列表或字典
async def get_json_cache(key:str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)#将JSON字符串转换回Python对象(如列表或字典) 为什么?:因为我们存储到Redis中的数据是经过json.dumps()序列化成字符串的,所以读取时需要用json.loads()反序列化回原来的数据结构(如列表或字典)才能使用
        return None
    except Exception as e:
        print(f"获取JSON缓存失败:{e}")
        return None

#设置缓存
async def set_cache(
        key:str,
        value:Any,
        expire:int = 3600
):
    try:
        if isinstance(value,(list,dict)):
            value = json.dumps(value,ensure_ascii=False)#将Python对象转换为JSON字符串(因为Redis只支持字符串)  ensure_ascii=False可以让中文等非ASCII字符正常显示而不是被转义成\uXXXX的形式
        await redis_client.setex(key,expire,value)
        return True
    except Exception as e:
        print(f"设置缓存失败:{e}")
        return False