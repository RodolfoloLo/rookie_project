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
    async with AsyncSessionLocal() as session: #async with ... as是什么意思?:解答:async with ... as是Python中的异步上下文管理器语法，用于确保在使用完资源后正确地清理和释放它们。在这个例子中，async with AsyncSessionLocal() as session创建了一个新的异步数据库会话，并将其赋值给变量session。当代码块执行完毕后，无论是正常完成还是发生异常，都会自动调用session.close()来关闭会话，释放数据库连接。这种方式确保了资源的正确管理，避免了连接泄漏等问题。
        try:
            yield session #yield表示将session对象提供给调用者（如FastAPI的路由处理函数）。调用者可以在yield语句处暂停执行，使用session进行数据库操作。当调用者完成操作后，控制流会返回到yield之后，继续执行await session.commit()来提交事务，将更改保存到数据库。
            await session.commit() #为什么crud函数中已经有await db.commit()了还要在这里commit一次？解答:在crud函数中调用await db.commit()是为了确保在执行数据库操作后立即提交事务，将更改保存到数据库中。然而，在get_database依赖函数中再次调用await session.commit()是为了处理在调用者（如FastAPI的路由处理函数）执行数据库操作时可能发生的异常情况。如果调用者在执行数据库操作时发生异常，控制流会跳转到except块，执行await session.rollback()来回滚事务，撤销未提交的更改，确保数据库保持一致性。因此，在get_database依赖函数中再次调用await session.commit()是为了确保在正常情况下提交事务，而在异常情况下回滚事务，以维护数据库的完整性和一致性。
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

#详解这个依赖函数,深刻理解异步数据库会话的生命周期管理：
#1.创建会话：使用AsyncSessionLocal工厂创建一个新的异步会话实例session。这个会话是与数据库交互的主要接口。
#2.上下文管理：使用async with语句确保会话在使用完毕后正确关闭。无论操作成功还是发生异常，都会执行finally块中的session.close()来释放数据库连接。
#3.提交事务：在try块中，yield session将会话对象提供给调用者（如FastAPI的路由处理函数）。如果调用者成功完成数据库操作，控制流会返回到yield之后，执行await session.commit()来提交事务，将更改保存到数据库。
#4.异常处理：如果在调用者执行数据库操作时发生任何异常，控制流会跳转到except块，执行await session.rollback()来回滚事务，撤销未提交的更改，确保数据库保持一致性。
