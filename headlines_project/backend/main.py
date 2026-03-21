import os

from fastapi import FastAPI
from .api import news,users,favorite,history
from fastapi.middleware.cors import CORSMiddleware
from .utils.exception_handlers import register_exception_handlers

app = FastAPI()

register_exception_handlers(app)

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