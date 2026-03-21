# 保姆级部署手册（从现在开始，一步一步照做）

适用对象：完全没有部署经验的同学。

你的目标：把这个项目部署到阿里云 Ubuntu 22.04，使用 Docker + Nginx，并能在公网访问。

本手册已经把你项目里已有的文件和脚本都整合进来了：

- `docker-compose.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `frontend/nginx.conf`
- `ops/10_server_preflight.sh`
- `ops/20_deploy.sh`
- `ops/30_verify.sh`

---

## 第 0 部分：先讲清楚你要做什么

你将完成 4 件事：

1. 在服务器安装 Docker（只做一次）
2. 把项目上传到服务器
3. 一键启动 3 个容器（MySQL + FastAPI + Nginx）
4. 用公网 IP 打开网站并验证接口

架构图（文字版）：

- 浏览器访问 `http://你的公网IP`
- 请求先到 `frontend`（Nginx）
- Nginx 把 `/api/...` 转发给 `backend`（FastAPI）
- backend 连接 `db`（MySQL）

---

## 第 1 部分：你“现在”在本地要做的事（Windows）

### 1.1 确认关键文件存在

在本地项目根目录 `headlines_project` 检查这些文件：

- `docker-compose.yml`
- `backend/.env`
- `frontend/.env`
- `ops/10_server_preflight.sh`
- `ops/20_deploy.sh`
- `ops/30_verify.sh`

### 1.2 检查 `backend/.env`

确保有这些配置（可以比这更多）：

```env
DEBUG_MODE=false
DB_ECHO=false
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
ASYNC_DATABASE_URL=mysql+aiomysql://app_user:app_password@db:3306/news_app?charset=utf8mb4
```

重点：`ASYNC_DATABASE_URL` 里的 `app_user` / `app_password` 要和 `docker-compose.yml` 的 MySQL 用户密码一致。

### 1.3 检查 `docker-compose.yml` 的数据库密码

你已经改过密码的话，再确认一次这 3 处一致：

1. `MYSQL_USER`
2. `MYSQL_PASSWORD`
3. `ASYNC_DATABASE_URL` 里的用户名和密码（在 `backend/.env`）

---

## 第 2 部分：连接你的阿里云服务器（Xshell）

### 2.1 登录

用 Xshell 连接你的 Ubuntu 22.04。

登录后先执行：

```bash
uname -a
lsb_release -a
whoami
```

确认是 Ubuntu 22.04，且是可 sudo 用户。

---

## 第 3 部分：安装 Docker（服务器上，只做一次）

按顺序复制执行：

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

执行完最后一条后：

1. 断开 Xshell
2. 重新连接一次（让 docker 用户组生效）

重新连接后测试：

```bash
docker --version
docker compose version
```

---

## 第 4 部分：上传项目到服务器

你可以用两种方式：

1. Git：

```bash
cd ~
git clone <你的仓库地址> headlines_project
cd headlines_project
```

2. Xftp 上传压缩包：
- 上传 `headlines_project.zip` 到 `~/`
- 然后：

```bash
cd ~
unzip headlines_project.zip
cd headlines_project
```

---

## 第 5 部分：阿里云安全组设置（必须）

在阿里云控制台 -> ECS -> 安全组 -> 入方向，放行：

1. TCP 22（SSH）
2. TCP 80（HTTP）
3. TCP 443（HTTPS，先放着）

注意：3306 不建议公网放开。

---

## 第 6 部分：部署前预检（非常重要）

在服务器执行：

```bash
cd ~/headlines_project
bash ops/10_server_preflight.sh ~/headlines_project
```

如果最后看到：`Preflight completed successfully.`，继续下一步。

如果失败，不要慌，把输出发我，我告诉你改哪一行。

---

## 第 7 部分：一键部署

在服务器执行：

```bash
cd ~/headlines_project
bash ops/20_deploy.sh ~/headlines_project
```

这会自动：

1. 停旧容器（如果有）
2. 重建镜像
3. 启动数据库 + 后端 + 前端
4. 打印容器状态

---

## 第 8 部分：一键验收

在服务器执行：

```bash
cd ~/headlines_project
bash ops/30_verify.sh ~/headlines_project
```

如果看到 `Verify passed.`，说明基础部署成功。

---

## 第 9 部分：浏览器访问

在你的电脑浏览器打开：

- `http://你的服务器公网IP`

然后手工点这几步：

1. 注册/登录
2. 新闻列表
3. 点击新闻详情
4. 收藏/取消收藏
5. 历史记录页面

---

## 第 10 部分：常用命令（以后天天会用）

### 看状态

```bash
docker compose ps
```

### 看日志

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

### 更新后重建

```bash
cd ~/headlines_project
git pull
docker compose up -d --build
```

### 停止服务

```bash
docker compose down
```

### 清库重来（危险，会清空数据库）

```bash
docker compose down -v
docker compose up -d --build
```

---

## 第 11 部分：最常见错误与处理

### 错误 1：网页能打开，但接口报错

执行：

```bash
docker compose logs --tail=120 backend
docker compose logs --tail=120 frontend
```

高频原因：

1. `backend/.env` 数据库连接串账号密码不一致
2. Nginx 反代没命中 `/api`

### 错误 2：backend 启动失败，提示数据库连接失败

执行：

```bash
docker compose logs --tail=200 db
docker compose logs --tail=200 backend
```

先看 db 是否 healthy，再看 backend 报错行。

### 错误 3：容器一直 restarting

执行：

```bash
docker compose ps
docker compose logs --tail=200 <容器名>
```

---

## 第 12 部分：上线后安全建议（先记住）

1. `backend/.env` 永远不要传到 Git 仓库。
2. 定期备份数据库。
3. 3306 仅本机绑定，不开公网。
4. 后续加 HTTPS（域名 + 证书）。

---

## 第 13 部分：从“现在”开始的执行顺序（超短版）

你只需要按这 5 条做：

1. 服务器安装 Docker（第 3 部分）
2. 上传项目到 `~/headlines_project`（第 4 部分）
3. 运行 `bash ops/10_server_preflight.sh ~/headlines_project`
4. 运行 `bash ops/20_deploy.sh ~/headlines_project`
5. 运行 `bash ops/30_verify.sh ~/headlines_project`

---

## 第 14 部分：你每做完一步，就把这 3 段发我

```bash
docker compose ps
docker compose logs --tail=120 backend
docker compose logs --tail=120 db
```

我会继续“保姆式”告诉你下一步，不会让你一个人猜。
