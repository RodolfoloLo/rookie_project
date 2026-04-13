import os

from fastapi import FastAPI
from .api import news,users,favorite,history,ai_chat
from fastapi.middleware.cors import CORSMiddleware
from .utils.exception_handlers import register_exception_handlers

app = FastAPI()

register_exception_handlers(app) #注册全局异常处理器,如果某个接口报错,具体处理流程如下:
#1.接口抛出异常,如HTTPException(status_code=404,detail="Not Found")
#2.异常被FastAPI捕获!!!,根据异常类型查找对应的处理器,如http_exception_handler  
#3.执行处理器函数,如http_exception_handler(request,exc),生成JSONResponse响应

cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,#允许携带cookie
    allow_methods=["*"],#允许所有方法
    allow_headers=["*"],#允许所有头部
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

#挂载路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)
app.include_router(history.router)
app.include_router(ai_chat.router)