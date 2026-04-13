#这是一个验证脚本,用于检查Docker Compose部署的服务是否正常运行,包括检查容器状态、后端API、Redis服务、Nginx反向代理和前端页面是否可访问,如果任何检查失败,脚本会输出错误信息并退出,如果所有检查通过,则输出"Verify passed."
#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-$HOME/headlines_project}"
cd "$PROJECT_DIR"

echo "[1/5] Container status"
docker compose ps #显示当前Docker Compose项目中所有容器的状态,包括容器ID、名称、镜像、命令、创建时间、状态和端口映射等信息,可以用来检查容器是否正在运行以及是否有任何异常状态

echo "[2/5] Backend health check"
curl -fsS http://127.0.0.1:8000/ || { echo "backend direct check failed"; exit 1; } #curl -fsS意思是: -f表示如果HTTP状态码是错误的(4xx或5xx),则不显示输出; -s表示静默模式,不显示进度条; -S表示在发生错误时显示错误信息

echo "[3/5] Redis health check"
docker compose exec -T redis redis-cli ping | grep -q PONG || { echo "redis health check failed"; exit 1; } #docker compose exec是在运行中的容器中执行命令,这里是在redis容器中执行redis-cli ping命令来检查Redis服务是否响应,-T意思是不使用终端,如果输出包含PONG则表示Redis服务正常,否则输出错误信息并退出

echo "[4/5] Nginx reverse proxy check"
curl -fsS http://127.0.0.1/api/news/categories || { echo "nginx /api check failed"; exit 1; } #检查Nginx反向代理是否正常工作,这里使用curl访问后端API端点,如果无法访问则输出错误信息并退出

echo "[5/5] Frontend check"
curl -fsS http://127.0.0.1/ | head -n 5 #检查前端页面是否可访问,这里使用curl获取首页的内容并显示前5行,如果无法访问则输出错误信息并退出

echo "Verify passed."

#为什么没有检查MySQL服务的健康状态?因为在docker-compose.yml中已经设置了MySQL服务的健康检查,并且backend服务依赖于MySQL服务的健康状态,如果MySQL服务没有健康检查通过,则backend服务也无法启动,因此在这个验证脚本中只需要检查backend服务是否可访问即可间接验证MySQL服务的健康状态,如果backend服务能够正常响应请求,则说明MySQL服务也已经正常运行并且可以被访问到.
