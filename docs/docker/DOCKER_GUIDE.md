# Docker 部署指南

## 概述

使用 Docker 可以：
- ✅ 无需系统安装 Node.js
- ✅ 无需系统安装 Python（可选）
- ✅ 环境隔离，避免依赖冲突
- ✅ 一键启动整个系统

## 前置要求

**只需要安装 Docker：**
- Windows: https://www.docker.com/products/docker-desktop/
- Linux: `sudo apt-get install docker.io docker-compose`
- Mac: https://www.docker.com/products/docker-desktop/

## 快速开始

### 1. 构建并启动

```bash
# 一键启动前后端
docker-compose up --build
```

### 2. 访问系统

- 前端界面：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/api/docs

### 3. 停止服务

```bash
# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

## 详细说明

### 服务说明

- **backend**: Python 后端服务（端口 8000）
- **frontend**: Node.js 前端服务（端口 5173）

### 开发模式

当前配置支持开发模式：
- 代码修改后自动重载（前端热重载，后端需要重启）
- 配置文件挂载，可以直接修改

### 生产模式

生产环境建议：
1. 修改 `Dockerfile.frontend`，使用构建模式：
   ```dockerfile
   # 构建生产版本
   RUN npm run build
   # 使用 nginx 服务静态文件
   ```

2. 使用环境变量管理配置
3. 移除开发模式的 volume 挂载

## 常用命令

### 启动服务

```bash
# 前台运行（查看日志）
docker-compose up

# 后台运行
docker-compose up -d

# 重新构建并启动
docker-compose up --build
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend

# 实时查看日志
docker-compose logs -f
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

## 配置文件

### 修改配置

配置文件挂载在 `./config` 目录，可以直接修改：

```bash
# 修改配置文件
vim config/config.yaml

# 重启服务使配置生效
docker-compose restart backend
```

### 环境变量

可以在 `docker-compose.yml` 中添加环境变量：

```yaml
services:
  backend:
    environment:
      - DATA_SOURCE_DEFAULT=akshare
      - LOG_LEVEL=INFO
```

## 故障排除

### 问题1：端口被占用

**错误：** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**解决：**
```bash
# 修改 docker-compose.yml 中的端口映射
ports:
  - "8001:8000"  # 改为其他端口
```

### 问题2：构建失败

**错误：** `npm install` 失败

**解决：**
```bash
# 清理并重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### 问题3：代码修改不生效

**原因：** Volume 挂载问题

**解决：**
```bash
# 检查 docker-compose.yml 中的 volumes 配置
# 确保代码目录正确挂载
```

### 问题4：容器无法启动

**检查：**
```bash
# 查看容器日志
docker-compose logs

# 检查容器状态
docker-compose ps

# 进入容器调试
docker-compose exec backend bash
```

## 性能优化

### 使用 .dockerignore

已创建 `.dockerignore` 文件，排除不必要的文件，加快构建速度。

### 多阶段构建（生产环境）

```dockerfile
# 构建阶段
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

## 与系统安装对比

| 特性 | Docker | 系统安装 |
|------|--------|----------|
| **Node.js** | ✅ 容器内 | ❌ 需要安装 |
| **Python** | ✅ 容器内 | ❌ 需要安装 |
| **环境隔离** | ✅ 完全隔离 | ⚠️ 可能冲突 |
| **启动速度** | ⚠️ 较慢 | ✅ 快速 |
| **开发体验** | ⚠️ 需要学习 | ✅ 简单 |
| **部署** | ✅ 一致 | ⚠️ 环境差异 |

## 推荐场景

### 使用 Docker 适合：
- ✅ 不想在系统安装 Node.js
- ✅ 需要环境隔离
- ✅ 生产部署
- ✅ 团队协作（环境一致）

### 使用系统安装适合：
- ✅ 本地开发（更快速）
- ✅ 简单项目
- ✅ 不想安装 Docker

## 总结

Docker 方案的优势：
1. **无需系统安装 Node.js** - 这正是你想要的！
2. **环境隔离** - 避免依赖冲突
3. **一键启动** - `docker-compose up` 即可
4. **易于部署** - 生产环境也可以使用

**快速命令：**
```bash
# 启动
docker-compose up --build

# 停止
docker-compose down
```

