from fastapi import FastAPI,Depends,HTTPException
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker,AsyncSession
from datetime import datetime
from sqlalchemy import DateTime,func,String,Float,select
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from pydantic import BaseModel

app=FastAPI()

#chapter1   ORM~建表
#1,创建异步引擎
ASYNC_DATABASE_URL = os.getenv(
    "ASYNC_DATABASE_URL",
    "mysql+aiomysql://root:change_me@localhost:3306/PythonWeb_demo_db?charset=utf8",
)
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,#输出SQL日志
    pool_size=10,#常驻的连接数
    max_overflow=20,#允许额外的连接数
)

#2,定义模型类,基类+表对应的模型类
#基类:创建时间,更新时间   书籍表:id,书名,作者,价格,出版社
class Base(DeclarativeBase):
    create_time:Mapped[datetime] = mapped_column(DateTime,insert_default=func.now(),default=func.now,comment="创建时间")
    update_time:Mapped[datetime] = mapped_column(DateTime,insert_default=func.now(),default=func.now,onupdate=func.now(),comment="更新时间")

class Book(Base):
    __tablename__ = "book"
    id:Mapped[int] = mapped_column(primary_key=True,comment="id")
    name:Mapped[str] = mapped_column(String(255),comment="书名")
    author:Mapped[str] = mapped_column(String(255),comment="作者")
    price:Mapped[float] = mapped_column(Float,comment="价格")
    publisher:Mapped[str] = mapped_column(String(255),comment="出版社")

#3,建表:定义函数建表->FastAPI启动时调用建表的函数
async def create_tables():
    #获取异步引擎,创建事务-建表
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")#启动时执行
async def startup():
    await create_tables()

##chapter2  ORM~在路由中使用ORM
#核心：创建依赖项，使用Depends注入到处理函数

#需求：查询功能的接口，查询图书->依赖注入：创建依赖项获取数据库会话+Depends注入路由处理函数

#创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind = async_engine,#绑定数据库引擎
    class_ = AsyncSession,#指定会话类
    expire_on_commit = False,#提交后会话不过期，不会重新查询数据库
)

#创建依赖项，获取数据库会话
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session#返回数据库会话给路由处理函数
            await session.commit()#提交事务
        except:
            await session.rollback()#有异常，回滚
            raise
        finally:
            await session.close()#关闭会话

@app.get("/book/get_book")
async def get_book_list(db: AsyncSession = Depends(get_database)):
    #查询数据

    #获取所有
    #result = await db.execute(select(Book))
    #books = result.scalars().all()
    #获取第一条
    # books = result.scalars().first()
    #return books
    #获取指定数据
    result = await db.get(Book,1)#获取单条数据(根据主键)
    return result

@app.get("/book/get_book/{book_id}")
async def get_book_list(book_id:int,db: AsyncSession = Depends(get_database)):
    #比较查询
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    return book

@app.get("/book/search_book")
async def search_book(db: AsyncSession = Depends(get_database)):
    #模糊查询
    #like()
    #result = await db.execute(select(Book).where(Book.author.like("路%")))
    #& | ~与非
    #result = await db.execute(select(Book).where(Book.author.like("路%") & Book.price>23))
    #in_()包含
    author_list = ["路","余"]
    result = await db.execute(select(Book).where(Book.author.in_(author_list)))
    return result.scalars().all()

@app.get("/book/calculate")
async def calculate(db: AsyncSession = Depends(get_database)):
    #聚合查询
    #result = await db.execute((select(func.count(Book.id))))
    #result = await db.execute(select(func.sum(Book.price)))
    result = await db.execute(select(func.avg(Book.price)))
    #result = await db.execute(select(func.max(Book.price)))
    #result = await db.execute(select(func.min(Book.price)))
    answer = result.scalar()#用来提取一个数值
    return answer

@app.get("/book/books_into_pages")
async def books_into_pages(
        page:int =1,
        page_size:int = 2,
        db: AsyncSession = Depends(get_database)
):
    #分页查询
    skip = (page-1)*page_size
    stmt = select(Book).offset(skip).limit(page_size)#offset:跳过的记录数 limit:每一页的记录数
    result = await db.execute(stmt)
    books = result.scalars().all()
    return books

#新增数据

#ORM模型-负责数据库操作
#Pydantic模型-负责数据验证 <验证!!!>
class BookBase(BaseModel):
    id:int
    name:str
    author:str
    price:float
    publisher:str

@app.post("/book/add_book")
async def add_book(
        book:BookBase,
        db: AsyncSession = Depends(get_database)
):
    book_obj = Book(**book.__dict__)
    db.add(book_obj)
    await db.commit()
    return book

#更新数据

#"先查后改"
class BookUpdate(BaseModel):
    name:str
    author:str
    price:float
    publisher:str

@app.put("/book/update_book/{book_id}")
async def update_book(
        book_id:int,
        data:BookUpdate,
        db: AsyncSession = Depends(get_database)
):
    db_book = await db.get(Book,book_id)
    if db_book is None:
        raise HTTPException(
            status_code=404,
            detail="图书不存在"
        )

    #重新赋值
    db_book.name = data.name
    db_book.author = data.author
    db_book.price = data.price
    db_book.publisher = data.publisher

    await db.commit()
    return db_book

#删除数据

#"先查后删"
@app.delete("/book/delete_book/{book_id}")
async def delete_book(
        book_id:int,
        db: AsyncSession = Depends(get_database)
):
    db_book = await db.get(Book,book_id)
    if db_book is None:
        raise HTTPException(
            status_code=404,
            detail="图书不存在"
        )
    await db.delete(db_book)
    await db.commit()
    return {"msg:删除成功"}

