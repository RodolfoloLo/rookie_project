# 超详细部署任务书（小白版）

适用对象：第一次部署项目、第一次用服务器、第一次用 Docker。

目标：在阿里云 Ubuntu 22.04 上，把项目以 `Docker + Nginx + FastAPI + MySQL` 方式稳定跑起来。

你现在项目目录假设是：`~/headlines_project`

---

## A. 你先理解这套架构（1 分钟）

1. 浏览器访问服务器 `80` 端口，进入 `frontend` 容器（Nginx）。
2. 前端页面里的 `/api/...` 请求会被 Nginx 转发到 `backend` 容器（FastAPI:8000）。
3. 后端通过 `ASYNC_DATABASE_URL` 连接 `db` 容器（MySQL）。

一句话：`浏览器 -> Nginx(frontend) -> FastAPI(backend) -> MySQL(db)`。

---

## B. 第 0 天必须准备好的信息（先抄到记事本）

1. 服务器公网 IP（例如 `47.xx.xx.xx`）
2. 服务器登录用户名（通常 `root` 或你自己的 sudo 用户）
3. 你的项目目录路径（例如 `~/headlines_project`）
4. 你要设置的数据库密码：
- `MYSQL_ROOT_PASSWORD`
- `MYSQL_PASSWORD`
5. （可选）域名

---

## C. 本地出发前检查（Windows）

### C1. 确认这几个文件存在

1. `docker-compose.yml`
2. `backend/Dockerfile`
3. `frontend/Dockerfile`
4. `frontend/nginx.conf`
5. `backend/.env`
6. `backend/database.sql`
7. `ops/10_server_preflight.sh`
8. `ops/20_deploy.sh`
9. `ops/30_verify.sh`

### C2. 检查 `backend/.env` 内容（关键）

至少要有：

```env
DEBUG_MODE=false
DB_ECHO=false
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ASYNC_DATABASE_URL=mysql+aiomysql://app_user:app_password@db:3306/news_app?charset=utf8mb4
```

注意：`ASYNC_DATABASE_URL` 里的 `app_user/app_password`，必须和 `docker-compose.yml` 里 MySQL 用户密码一致。

### C3. 检查 `docker-compose.yml` 的数据库密码

在 `db.environment` 中，改成你自己的强密码。

---

## D. 服务器基础环境安装（Ubuntu 22.04）

> 在 Xshell 里逐条执行。

### D1. 更新系统

```bash
sudo apt update
sudo apt upgrade -y
```

### D2. 安装 Docker

```bash
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
```

### D3. 把当前用户加入 docker 组（推荐）

```bash
sudo usermod -aG docker $USER
```

执行后请重新登录 Xshell 一次。

---

## E. 上传项目到服务器

你可以用 git clone 或 Xftp 上传。上传后进入项目目录：

```bash
cd ~/headlines_project
```

---

## F. 先跑预检脚本（强烈建议）

```bash
bash ops/10_server_preflight.sh ~/headlines_project
```

预期：最后出现 `Preflight completed successfully.`

如果失败：把输出完整发我，我帮你定位。

---

## G. 正式部署

### G1. 一键部署

```bash
bash ops/20_deploy.sh ~/headlines_project
```

这个脚本会做：

1. 关闭旧容器（如果有）
2. 强制重新构建镜像
3. 启动三套服务
4. 打印容器状态

### G2. 验收

```bash
bash ops/30_verify.sh ~/headlines_project
```

预期：`Verify passed.`

---

## H. 浏览器验证

打开：

1. `http://你的公网IP`
2. 测试功能：登录、新闻列表、新闻详情、收藏、历史

---

## I. 阿里云控制台必须做的事

### I1. 安全组放行入方向

1. TCP 22（SSH）
2. TCP 80（HTTP）
3. TCP 443（将来 HTTPS）

### I2. 3306 建议

生产不建议对公网开放 3306。

---

## J. 你每天会用到的运维命令

### 查看状态

```bash
docker compose ps
```

### 看后端日志

```bash
docker compose logs -f backend
```

### 看数据库日志

```bash
docker compose logs -f db
```

### 重启全部

```bash
docker compose restart
```

### 更新代码后重建

```bash
git pull
docker compose up -d --build
```

---

## K. 最常见报错与处理

### K1. 页面能开，接口全 500

1. 看后端日志：`docker compose logs --tail=200 backend`
2. 看数据库日志：`docker compose logs --tail=200 db`
3. 高概率是 `backend/.env` 的数据库连接串不一致

### K2. 接口 404（尤其详情）

确认前端请求路径与后端一致。你项目现在详情路径是 `/api/news/details?id=...`。

### K3. 容器起不来

```bash
docker compose ps
docker compose logs --tail=200
```

把输出发我。

### K4. 端口冲突（80/3306 已占用）

```bash
ss -lntp | grep -E ':80 |:3306 '
```

找到占用进程后停掉，或改 `docker-compose.yml` 端口映射。

---

## L. 回滚方案（非常重要）

当你更新后异常：

```bash
# 回到上一个 git 版本
cd ~/headlines_project
git log --oneline -n 5
git checkout <上一个稳定commit>

docker compose up -d --build
```

如果你没用 git，也要至少保留一份部署前压缩包。

---

## M. 数据库备份与恢复（建议每周一次）

### 备份

```bash
docker exec -i news_db mysqldump -uroot -p你的root密码 news_app > ~/news_app_backup.sql
```

### 恢复

```bash
cat ~/news_app_backup.sql | docker exec -i news_db mysql -uroot -p你的root密码 news_app
```

---

## N. 上线前最终 Checklist（按顺序勾选）

1. [ ] `backend/.env` 已设置并检查密码一致
2. [ ] `docker-compose.yml` 中 MySQL 密码已改为强密码
3. [ ] 已执行 `bash ops/10_server_preflight.sh`
4. [ ] 已执行 `bash ops/20_deploy.sh`
5. [ ] 已执行 `bash ops/30_verify.sh`
6. [ ] 阿里云安全组已放行 22/80/443
7. [ ] 浏览器已能打开前端页面
8. [ ] 已实测登录 + 新闻详情 + 收藏 + 历史

---

## O. 你只要给我这 3 段输出，我就能继续手把手带你

```bash
docker compose ps
docker compose logs --tail=120 backend
docker compose logs --tail=120 db
```
