# GitHub Actions + GHCR 镜像发布部署说明

目标：GitHub Actions 自动构建前后端 Docker 镜像，推送到 GitHub Container Registry；服务器执行脚本拉取指定版本镜像并更新容器。

---

## 1. 镜像地址

当前 workflow 会推送两个镜像：

```text
ghcr.io/<你的GitHub用户名小写>/headlines-backend:<版本>
ghcr.io/<你的GitHub用户名小写>/headlines-frontend:<版本>
```

例如你的 GitHub 用户名是 `RodolfoloLo`，GHCR 镜像地址要写小写：

```text
ghcr.io/rodolfololo/headlines-backend:latest
ghcr.io/rodolfololo/headlines-frontend:latest
```

---

## 2. GitHub Actions 如何触发

workflow 文件：

```text
.github/workflows/docker-image.yml
```

触发方式：

1. push 到 `main` 分支：生成 `latest` 和短提交号标签，例如 `a1b2c3d`
2. push `v*.*.*` 标签：生成版本标签，例如 `v1.0.0` 和 `latest`
3. 在 GitHub Actions 页面手动运行

---

## 3. GitHub 侧准备

进入仓库页面：

```text
Settings -> Actions -> General -> Workflow permissions
```

选择：

```text
Read and write permissions
```

否则 Actions 可能没有权限推送 GHCR package。

---

## 4. 服务器登录 GHCR

如果 GHCR package 是 private，服务器必须登录。

先在 GitHub 创建 Personal Access Token：

```text
GitHub -> Settings -> Developer settings -> Personal access tokens
```

token 至少需要：

```text
read:packages
```

服务器执行：

```bash
echo '你的GitHubToken' | docker login ghcr.io -u 你的GitHub用户名 --password-stdin
```

不要把 token 写进项目文件或提交到 Git。

---

## 5. 服务器 .env 配置

服务器项目根目录 `.env` 需要包含：

```env
MYSQL_DATABASE=news_app
MYSQL_USER=app_user
MYSQL_PASSWORD=你的数据库密码
MYSQL_ROOT_PASSWORD=你的root数据库密码
REGISTRY_IMAGE_BACKEND=ghcr.io/你的github用户名小写/headlines-backend
REGISTRY_IMAGE_FRONTEND=ghcr.io/你的github用户名小写/headlines-frontend
IMAGE_TAG=latest
```

例如：

```env
REGISTRY_IMAGE_BACKEND=ghcr.io/rodolfololo/headlines-backend
REGISTRY_IMAGE_FRONTEND=ghcr.io/rodolfololo/headlines-frontend
IMAGE_TAG=latest
```

后端环境变量仍然放在：

```text
backend/.env
```

---

## 6. 部署 latest

服务器进入项目目录后执行：

```bash
bash ops/40_pull_deploy.sh ~/headlines_project latest
```

---

## 7. 部署指定版本

本地打版本标签并推送：

```bash
git tag v1.0.0
git push origin v1.0.0
```

等 GitHub Actions 成功后，服务器执行：

```bash
bash ops/40_pull_deploy.sh ~/headlines_project v1.0.0
```

---

## 8. 回滚到旧版本

只要旧版本镜像还在 GHCR，就可以执行：

```bash
bash ops/40_pull_deploy.sh ~/headlines_project v0.9.0
```

---

## 9. 旧镜像如何处理

部署脚本使用：

```bash
docker image prune -f
```

它只清理未被任何容器使用的悬空镜像，不会删除正在运行容器依赖的镜像，也不会删除数据库 volume。

不要在服务器随意执行：

```bash
docker compose down -v
docker system prune -a --volumes
```

这些命令可能删除数据库数据卷或过度清理镜像。

---

## 10. 验证部署

执行：

```bash
bash ops/30_verify.sh ~/headlines_project
```

或者查看：

```bash
docker compose -f docker-compose.prod.yml ps
```
