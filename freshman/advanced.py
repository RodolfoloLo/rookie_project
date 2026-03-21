from fastapi import FastAPI,Query,Depends

app = FastAPI()

@app.middleware("http")
async def middleware1(request, call_next):#request是请求，call_next是传递请求
    print("中间件1开始")
    response = await call_next(request)
    print("中间件1结束")
    return response

@app.middleware("http")
async def middleware2(request, call_next):
    print("中间件2开始")
    response = await call_next(request)
    print("中间件2结束")
    return response
#"自下而上执行"

@app.get("/")
async def root():
    return {"message": "Hello World"}

#依赖项
async def common_parameters(
        skip: int = Query(0,ge=0),
        limit: int = Query(10,le=60)
):
    return {"skip": skip, "limit": limit}

#注入
@app.get("/news/news_list")
async def get_news_list(commons=Depends(common_parameters)):
    return commons

@app.get("/user/user_list")
async def get_user_list(commons=Depends(common_parameters)):
    return commons



#知识点

#中间件:每次请求进入FastAPI应用时都会被执行的函数   在请求到达实际的操作路径(路由处理函数)之前运行,并且在响应返回客户端之前再运行一次
#作用:为每个请求添加统一的处理逻辑(记录日志,身份认证,跨域,设置响应头,性能监控)
#依赖注入:在路由处理函数中注入依赖对象,并使用依赖对象来处理请求
#作用:为每个请求注入依赖对象,并使用依赖对象来处理请求
#创建依赖项  导入Depends  声明依赖项
#中间件和依赖注入的区别：中间件控制谁：everyone 依赖注入控制谁：我说了算~