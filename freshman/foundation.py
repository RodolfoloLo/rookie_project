from fastapi import FastAPI,Path,Query,HTTPException
#fastapi是一个用于构建Web应用程序的Python框架,用于创建RESTful API,创建API,Path是pydantic中的一个类,用于定义路径参数,Query是pydantic中的一个类,用于定义查询参数,HTTPException是fastapi中的一个类,用于抛出HTTP异常
from pydantic import BaseModel,Field
#pydantic是一个用于数据验证和类型转换的Python库,用于处理请求数据,BaseModel是pydantic中的一个类,用于定义数据模型,Field是pydantic中的一个类,用于定义字段属性
from fastapi.responses import HTMLResponse,FileResponse

app = FastAPI()#创建一个FastAPI实例

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello")
async def get_hello():
    return {"msg": "Hello FastAPI"}

#路径参数:位置:URL路径的一部分  作用:指向唯一的,特定的资源  方法:GET
#两个路径参数例子
@app.get("/book/{id}")
async def get_book(id: int = Path(gt=0,lt=101,description="书籍id,取值范围1~100")):
    return {"id": id, "msg": f"这是第{id}本书"}

@app.get("/author/{name}")
async def get_author(name: str=Path(min_length=2,max_length=10,description="作者名称,取值范围2~10个字符")):
    return {"name": name, "msg": f"这是作者{name}"}

#查询参数:位置:URL?之后   作用:对资源集合进行过滤,排序,分页等操作  方法:GET
#一个查询参数例子(查询新闻->分页,skip:跳过的记录数,limit:返回的记录数 10)
@app.get("/news/news_list")
async def get_news_list(skip: int = Query(0,description="跳过的记录数",lt=100), limit: int = Query(10,description="返回的记录数")):
    return {"skip": skip, "limit": limit}

#请求体参数:位置:HTTP请求的消息体  作用:创建,更新资源,携带大量数据,如:JSON  方法:POST,PUT,DELETE
#一个请求体参数例子(注册:用户名和密码->str)
class User(BaseModel):
    username: str = Field(default="LeBron James",min_length=2,max_length=10,description="用户名,取值范围2~10个字符")
    password: str = Field(min_length=2,max_length=10,description="密码,取值范围2~10个字符")

@app.post("/register")
async def register(user: User):
    return user

#响应类型--HTMLResponse,FileResponse
@app.get("/html",response_class=HTMLResponse)
async def get_html():
    return """
    <html>
        <head>
            <title>后端学起来孩子们</title>
        </head>
        <body>
            <h1>虽然我在学,但是我最想做的一直都是看世界,然后享受世界!!!</h1>
        </body>
    </html>
    """

@app.get("")
async def get_file():
    path = "米高佐敦.jpg"
    return FileResponse(path)

#自定义响应类型:
class player(BaseModel):
    name: str
    age: int
    team: str
    position: str

@app.get("/player/{name}",response_model= player)
async def get_player(name:str):
    return {
        "name": name,
        "age": 41,
        "team": "Lakers",
        "position": "SG"
    }

@app.get("/news/{id}")
async def get_news(id: int):
    id_list=[1,2,3,4,5,6]
    if id not in id_list:
        raise HTTPException(status_code=404,detail="新闻不存在")
    return {"id": id}

#知识点

# 1. FastAPI 是一个用于构建 Web 应用的 Python 框架。
# 2. FastAPI 使用了 ASGI（Asynchronous Server Gateway Interface）作为其异步处理机制，因此它可以处理高并发的请求。
# 3. FastAPI 的路由系统基于路径参数和查询参数，因此它可以处理不同的 URL 并返回不同的内容。
# 4. FastAPI 的数据验证和类型转换功能使得处理请求数据变得简单和一致。
# 5. FastAPI 的文档生成功能使得开发人员可以轻松地生成 API 文档，并帮助用户理解 API 的用途和用法。
# 6. FastAPI 的依赖注入功能使得开发人员可以轻松地管理依赖关系，并确保应用程序的Each API endpoint can be defined using a single function.
# 7. FastAPI 的异常处理功能使得开发人员可以轻松地处理异常，并返回适当的错误信息。
# 8. FastAPI 的测试功能使得开发人员可以轻松地测试 API，并确保应用程序的Each API endpoint can be tested using a single function.
# 9. FastAPI 的性能优化功能使得开发人员可以轻松地优化应用程序的性能，并确保应用程序的Each API endpoint can be optimized using a single function.
# 10. FastAPI 的部署功能使得开发人员可以轻松地部署应用程序，并确保应用程序的Each API endpoint can be deployed using a single function.
#(以上内容由AI生成，仅供参考)

#什么是路由?
#路由就是URL地址和处理函数之间的映射关系,路由是FastAPI的核心概念，它定义了应用程序的URL地址和相应的处理函数。
#路由写法:@app.get("/")

#响应类型
#默认情况下,FastAPI会自动将路径操作函数返回的Python对象转换为JSON格式的响应数据。但是，FastAPI提供了多种方式来指定响应的类型。