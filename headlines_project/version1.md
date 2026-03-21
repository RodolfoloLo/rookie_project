# 从 0 开始部署指南（Ubuntu 22.04 + Docker + Nginx）

本指南按新手视角写，目标是把当前项目部署到阿里云 Ubuntu 22.04。

## 0. 你将得到什么

- 前端：Nginx 容器托管 Vue 打包产物
- 后端：FastAPI 容器
- 数据库：MySQL 8 容器（自动导入 `backend/database.sql`）
- 编排：`docker compose`

访问方式：

- 前端：`http://服务器公网IP`
- 后端接口：`http://服务器公网IP/api/...`（由 Nginx 反向代理到 FastAPI）

## 1. 服务器前置检查（Xshell 登录后执行）

```bash
uname -a
lsb_release -a
whoami
```

确保是 Ubuntu 22.04，且是可 sudo 用户。

## 2. 安装 Docker 与 Compose 插件

### 2.1 更新系统

```bash
sudo apt update
sudo apt upgrade -y
```

### 2.2 安装 Docker 依赖

```bash
sudo apt install -y ca-certificates curl gnupg lsb-release
```

### 2.3 添加 Docker 官方 GPG Key 与源

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 2.4 安装 Docker

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 2.5 启动并设为开机自启

```bash
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl status docker
```

### 2.6 允许当前用户免 sudo 运行 docker（可选但推荐）

```bash
sudo usermod -aG docker $USER
```

执行后断开 Xshell，重新登录一次。

## 3. 上传项目到服务器

你有 2 种方式，二选一。

### 方式 A：用 Git（推荐）

```bash
sudo apt install -y git
cd ~
git clone <你的仓库地址> headlines_project
cd headlines_project
```

### 方式 B：本地打包后上传（Xftp / scp）

本地把 `headlines_project` 压缩后上传到服务器 `~/`，再执行：

```bash
cd ~
unzip headlines_project.zip
cd headlines_project
```

## 4. 部署前检查项目文件

在服务器项目根目录执行：

```bash
cd ~/headlines_project
ls
```

应该看到这些关键文件：

- `docker-compose.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `backend/database.sql`

## 5. 修改生产环境密码（必须）

打开 `docker-compose.yml`，至少修改这些值：

- `MYSQL_ROOT_PASSWORD`
- `MYSQL_PASSWORD`
- `ASYNC_DATABASE_URL` 里的账号密码

要求：`ASYNC_DATABASE_URL` 与 MySQL 用户密码保持一致。

## 6. 开放服务器安全组端口（阿里云控制台）

在 ECS 安全组入方向放行：

- `22`（SSH）
- `80`（HTTP）
- `443`（未来 HTTPS）

数据库 `3306` 建议仅内网使用，生产不要公网开放。

## 7. 首次启动

在项目根目录执行：

```bash
cd ~/headlines_project
docker compose up -d --build
```

查看容器状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f db
docker compose logs -f backend
docker compose logs -f frontend
```

## 8. 验证是否部署成功

### 8.1 浏览器访问

- `http://你的公网IP`

### 8.2 后端健康验证

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1/api/news/categories
```

说明：

- 第一个是容器端口直连 FastAPI
- 第二个是通过 Nginx `/api` 反代

## 9. 常用运维命令

### 9.1 重启

```bash
docker compose restart
```

### 9.2 停止并删除容器（不删数据库卷）

```bash
docker compose down
```

### 9.3 停止并删除容器和数据库卷（会清空数据）

```bash
docker compose down -v
```

### 9.4 只重建后端

```bash
docker compose up -d --build backend
```

### 9.5 查看实时日志

```bash
docker compose logs -f backend
```

## 10. 发布更新流程（以后每次改代码）

```bash
cd ~/headlines_project
# 如果用 git：
git pull

docker compose up -d --build
```

## 11. 常见问题排查

### 11.1 页面能开但请求接口失败

- 看前端容器日志：`docker compose logs -f frontend`
- 看后端容器日志：`docker compose logs -f backend`
- 确认 `frontend/nginx.conf` 里 `/api/` 代理目标是 `http://backend:8000`

### 11.2 后端报数据库连接失败

- 等待 MySQL 初始化完成（首次可能 1-2 分钟）
- 检查 `docker-compose.yml` 的数据库密码是否一致
- 查看 `db` 日志是否有建库报错

### 11.3 首次登录失败 / 没有数据

- 检查 `backend/database.sql` 是否成功执行
- 若初始化失败可执行：

```bash
docker compose down -v
docker compose up -d --build
```

## 12. HTTPS（可选，后续做）

建议后续接入域名 + Nginx + certbot。

大致流程：

1. 域名解析到公网 IP
2. 宿主机安装 `certbot`
3. 申请证书
4. 在宿主机 Nginx 或网关层做 443 TLS 终止

你先把 HTTP 跑通，再做 HTTPS，成功率最高。

## 13. 你现在只需要执行这 4 条

```bash
cd ~/headlines_project
# 先改 docker-compose.yml 的数据库密码

docker compose up -d --build
docker compose ps
curl http://127.0.0.1/api/news/categories
```

如果有任何报错，把下面三段输出发我，我可以继续带你一步一步修：

```bash
docker compose ps
docker compose logs --tail=120 backend
docker compose logs --tail=120 db
```
