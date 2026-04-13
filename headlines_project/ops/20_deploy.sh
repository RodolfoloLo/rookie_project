#这是一个帮你一键部署的脚本
#!/usr/bin/env bash 
set -euo pipefail #这行代码的作用是设置bash脚本的错误处理选项,具体来说:
#-e选项表示如果脚本中的任何命令返回一个非零的退出状态,
#-u选项表示如果脚本中使用了未定义的变量,
#-o pipefail选项表示如果脚本中的任何一个管道命令返回一个非零的退出状态,
#则立即退出脚本并返回该状态码,这有助于捕捉和处理错误,避免脚本继续执行可能导致更严重问题的后续命令

PROJECT_DIR="${1:-$HOME/headlines_project}"
cd "$PROJECT_DIR"

echo "[1/5] Stop old stack (if exists)"
docker compose down || true

echo "[2/5] Build images"
docker compose build --no-cache #--no-cache选项表示在构建Docker镜像时不使用任何缓存,即使之前已经构建过相同的镜像,也会重新执行Dockerfile中的所有指令来构建新的镜像,这有助于确保构建过程中的每个步骤都能得到最新的结果,避免因为使用缓存而导致的问题,例如依赖更新后没有重新构建镜像等情况

echo "[3/5] Start stack"
docker compose up -d #-d选项表示以分离模式启动容器,即在后台运行容器,这样你就可以继续在终端执行其他命令而不被容器的输出干扰,如果不使用-d选项,则docker compose up命令会在前台运行容器,并显示容器的日志输出,直到你按下Ctrl+C来停止容器
#build和up命令的区别是:docker compose build是用来构建Docker镜像的,它会根据Dockerfile中的指令来创建一个新的镜像,而docker compose up是用来启动Docker容器的,它会根据docker-compose.yml文件中的配置来创建和启动容器,如果镜像不存在则会先构建镜像再启动容器,如果镜像已经存在则直接启动容器

echo "[4/5] Wait for containers"
sleep 8

echo "[5/5] Show status"
docker compose ps

echo "Deployment done. Next run: bash ops/30_verify.sh"
