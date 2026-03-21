from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

# 显式加载 backend/.env，避免从不同工作目录启动时读不到环境变量
BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

# 数据库URL：优先环境变量，缺失时回退本地默认值
DEFAULT_ASYNC_DATABASE_URL = (
    "mysql+aiomysql://app_user:change_me@localhost:3306/news_app?charset=utf8mb4"
)
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", DEFAULT_ASYNC_DATABASE_URL)

# SQL日志开关：可通过环境变量控制，默认关闭
DB_ECHO = os.getenv("DB_ECHO", "false").lower() in {"1", "true", "yes", "on"}

#创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=DB_ECHO,
    pool_size=10,#设置连接池中保持的持久连接数
    max_overflow=20,#设置连接池允许创建的额外连接数
)

#创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,    #绑定数据库引擎
    class_=AsyncSession,    #指定会话类
    expire_on_commit=False,    #提交后不会话过期，不会重新查询数据库
)

#创建依赖项
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()