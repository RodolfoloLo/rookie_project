# 部署总手册（保姆级）

面向对象：0 经验新手。

目标：把你的项目部署到阿里云 Ubuntu 22.04，使用 Docker + Nginx，能稳定访问并可排障。

你只需要按顺序复制命令执行，不要跳步骤。

---

## 0. 先知道你在部署什么

最终会启动 3 个容器：

1. `news_frontend`：Nginx，负责前端页面和 `/api` 反代
2. `news_backend`：FastAPI，负责接口
3. `news_db`：MySQL，负责数据存储

访问路径：

1. 前端页面：`http://你的服务器公网IP`
2. 后端接口：`http://你的服务器公网IP/api/...`

---

## 1. 你现在项目里已准备好的文件

你可以在本地确认这些文件都存在：

1. `docker-compose.yml`
2. `backend/Dockerfile`
3. `frontend/Dockerfile`
4. `frontend/nginx.conf`
5. `backend/.env`
6. `backend/database.sql`
7. `ops/10_server_preflight.sh`
8. `ops/20_deploy.sh`
9. `ops/30_verify.sh`

---

## 2. 上线前必须检查 2 个配置（非常重要）

### 2.1 检查 `backend/.env`

至少包含：

```env
DEBUG_MODE=false
DB_ECHO=false
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ASYNC_DATABASE_URL=mysql+aiomysql://<db_user>:<db_password>@db:3306/news_app?charset=utf8mb4
```

### 2.2 检查 `docker-compose.yml` 的数据库配置

确保这三者一致：

1. `db.environment.MYSQL_USER`
2. `db.environment.MYSQL_PASSWORD`
3. `backend/.env` 中 `ASYNC_DATABASE_URL` 的用户密码

注意：

- `MYSQL_USER` 不要写 `root`，建议改成 `app_user`。
- `MYSQL_ROOT_PASSWORD` 可以单独更复杂。

推荐范例：

```yaml
environment:
  MYSQL_DATABASE: news_app
  MYSQL_USER: app_user
  MYSQL_PASSWORD: 你的强密码A
  MYSQL_ROOT_PASSWORD: 你的强密码B
```

配套 `.env`：

```env
ASYNC_DATABASE_URL=mysql+aiomysql://app_user:你的强密码A@db:3306/news_app?charset=utf8mb4
```

---

## 3. 服务器安装 Docker（Ubuntu 22.04）

用 Xshell 登录服务器后，按顺序执行。

### 3.1 更新系统

```bash
sudo apt update
sudo apt upgrade -y
```

### 3.2 安装 Docker 官方仓库并安装

```bash
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 3.3 启动 Docker

```bash
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl status docker
```

看到 `active (running)` 就是成功。

### 3.4 免 sudo（推荐）

```bash
sudo usermod -aG docker $USER
```

执行后断开 Xshell，重新登录。

---

## 4. 上传项目到服务器

二选一：

1. Git：`git clone ...`
2. Xftp 上传整个 `headlines_project`

最终你要进入：

```bash
cd ~/headlines_project
```

---

## 5. 一键预检（先跑）

```bash
bash ops/10_server_preflight.sh ~/headlines_project
```

成功标志：最后出现 `Preflight completed successfully.`

如果失败：不要继续部署，把完整输出发我。

---

## 6. 一键部署

```bash
bash ops/20_deploy.sh ~/headlines_project
```

它会自动：

1. 关闭旧容器
2. 重新构建镜像
3. 启动容器
4. 打印状态

---

## 7. 一键验收

```bash
bash ops/30_verify.sh ~/headlines_project
```

成功标志：最后出现 `Verify passed.`

---

## 8. 浏览器验收（手工）

打开：

1. `http://你的公网IP`

然后做这几个动作：

1. 注册/登录
2. 打开新闻列表
3. 点一条新闻详情
4. 收藏一条新闻
5. 查看历史记录

---

## 9. 阿里云控制台要做的事

安全组入方向放行：

1. TCP 22
2. TCP 80
3. TCP 443（先放行，后面 HTTPS 用）

说明：

- 你当前 compose 已把 3306 绑定到 `127.0.0.1`，不会公网暴露，这是好的。

---

## 10. 后续更新（你以后每次发版）

```bash
cd ~/headlines_project
git pull
bash ops/20_deploy.sh ~/headlines_project
bash ops/30_verify.sh ~/headlines_project
```

---

## 11. 常见报错速查

### 11.1 页面打开但接口失败

```bash
docker compose logs --tail=200 frontend
docker compose logs --tail=200 backend
```

检查 `frontend/nginx.conf` 里 `/api/` 是否代理到 `http://backend:8000`。

### 11.2 后端数据库连不上

```bash
docker compose logs --tail=200 db
docker compose logs --tail=200 backend
```

重点检查：

1. `MYSQL_USER/MYSQL_PASSWORD`
2. `ASYNC_DATABASE_URL`
3. 三者是否一致

### 11.3 容器状态异常

```bash
docker compose ps
```

如果不是 `Up`，继续看日志。

### 11.4 端口冲突

```bash
ss -lntp | grep -E ':80 |:8000 |:3306 '
```

---

## 12. 回滚和备份（最低保障）

### 12.1 回滚代码

```bash
cd ~/headlines_project
git log --oneline -n 5
git checkout <上一个稳定commit>
bash ops/20_deploy.sh ~/headlines_project
```

### 12.2 备份数据库

```bash
docker exec -i news_db mysqldump -uroot -p你的root密码 news_app > ~/news_app_backup.sql
```

### 12.3 恢复数据库

```bash
cat ~/news_app_backup.sql | docker exec -i news_db mysql -uroot -p你的root密码 news_app
```

---

## 13. 一次性总执行清单（直接照抄）

```bash
cd ~/headlines_project

# 先手动确认 backend/.env 和 docker-compose.yml 的数据库用户密码一致

bash ops/10_server_preflight.sh ~/headlines_project
bash ops/20_deploy.sh ~/headlines_project
bash ops/30_verify.sh ~/headlines_project
```

---

## 14. 你只要把这 3 段输出发我，我就能继续远程陪跑

```bash
docker compose ps
docker compose logs --tail=120 backend
docker compose logs --tail=120 db
```
