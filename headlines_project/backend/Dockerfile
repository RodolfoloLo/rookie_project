FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_DEFAULT_TIMEOUT=180

WORKDIR /app

ARG PIP_INDEX_URL=https://pypi.org/simple

RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential python3-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --retries 10 --timeout 180 -i ${PIP_INDEX_URL} --upgrade pip setuptools wheel \
	&& pip install --no-cache-dir --retries 10 --timeout 180 -i ${PIP_INDEX_URL} -r /app/requirements.txt

COPY backend /app/backend

EXPOSE 8000

CMD ["uvicorn","backend.main:app","--host","0.0.0.0","--port","8000"]

#理解Docker镜像的最巧妙的设计:分层存储	
#分层的好处:
#1.节省空间:每一层只存储了相对于上一层的变化,如果多次使用相同的基础镜像,只需要存储一份基础镜像,而不是每次都存储完整的镜像,这样可以大大节省磁盘空间
#2.提高构建效率:当Dockerfile发生变化时,只有发生变化的层需要重新构建,其他未变化的层可以直接使用缓存,这样可以大大提高构建效率,尤其是在开发过程中频繁修改Dockerfile时
#3.便于维护:分层存储使得镜像的结构更加清晰,每一层对应Dockerfile中的一条指令,这样可以更容易地理解和维护镜像的构建过程,也方便调试和优化Dockerfile	

#第一层:FROM 基础镜像,这里使用官方的Python 3.12 slim版本,这个镜像已经包含了Python运行环境,但没有额外的库和工具,体积较小
#第二层:ENV 设置环境变量,PYTHONDONTWRITEBYTECODE=1表示不生成pyc文件(pyc文件是Python编译后的字节码文件),PYTHONUNBUFFERED=1表示输出不缓冲,直接显示在控制台,PIP_DEFAULT_TIMEOUT=180设置pip的默认超时时间为180秒
#第三层:WORKDIR 设置工作目录为/app,所有后续的命令都会在这个目录下执行 (/app是容器内的路径,不是宿主机的路径)
#第四层:ARG 定义构建参数PIP_INDEX_URL,默认值为https://pypi.org/simple,这个参数可以在构建镜像时通过--build-arg选项覆盖,用于指定pip的索引URL,如果不设置则使用默认的PyPI源 pypi.org是Python包的官方仓库，simple是PyPI的简单API端点，提供了包的基本信息和下载链接
#第五层:RUN 更新包列表并安装必要的系统依赖,这里安装了build-essential和python3-dev,这是一些编译工具和Python开发头文件,有些Python包需要编译安装,所以需要这些依赖,安装完成后清理apt缓存以减小镜像体积
#第六层:COPY 复制requirements.txt文件到镜像的/app目录下,这个文件列出了项目的Python依赖
#第七层:RUN 使用pip安装Python依赖,首先升级pip、setuptools和wheel,然后安装requirements.txt中列出的依赖,使用了--no-cache-dir选项来避免缓存安装包,使用--retries和--timeout选项来增加安装的稳定性,使用-i选项指定pip的索引URL
#第八层:COPY 复制backend目录下的所有文件到镜像的/app/backend目录下,这个目录包含了FastAPI应用的源代码
#第九层:EXPOSE 暴露8000端口,这是FastAPI应用默认的运行端口
#第十层:CMD 设置容器启动时的命令,使用uvicorn来运行FastAPI应用,指定应用的入口为backend.main:app,监听所有IP地址(0.0.0.0)和端口(8000)

#为什么先复制requirements.txt再复制整个backend目录?
#这是一个常见的Dockerfile优化技巧,通过先复制requirements.txt并安装依赖,可以利用Docker的缓存机制,如果requirements.txt没有变化,则安装依赖的层可以被缓存,这样在后续修改代码时就不需要重新安装依赖,提高构建效率

#这种Dockerfile不靠AI怎么写出来?需要对Docker的基本概念和命令有深入的理解,还需要了解Python应用的构建和运行过程,以及如何优化镜像的构建和运行效率,这需要一定的经验和实践积累,通过不断学习和尝试,可以逐渐掌握Dockerfile的编写技巧和最佳实践