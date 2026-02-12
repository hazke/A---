# Docker 方案 - 完整指南

## 📋 目录

1. [为什么使用 Docker？](#为什么使用-docker)
2. [安装 Docker](#安装-docker)
3. [快速启动](#快速启动)
4. [详细使用](#详细使用)
5. [故障排除](#故障排除)

## 为什么使用 Docker？

### 优势

✅ **无需安装 Node.js** - Node.js 在容器内运行  
✅ **无需安装 Python** - Python 在容器内运行  
✅ **环境隔离** - 避免依赖冲突  
✅ **一键启动** - `docker-compose up` 即可  
✅ **易于部署** - 生产环境也可以使用  
✅ **团队协作** - 环境一致，避免"在我机器上能跑"的问题

### 对比

| 特性 | Docker 方案 | 系统安装方案 |
|------|------------|------------|
| 需要安装 Node.js | ❌ 不需要 | ✅ 需要 |
| 需要安装 Python | ❌ 不需要 | ✅ 需要 |
| 环境隔离 | ✅ 完全隔离 | ⚠️ 可能冲突 |
| 启动速度 | ⚠️ 首次较慢 | ✅ 快速 |
| 开发体验 | ✅ 一键启动 | ✅ 简单直接 |
| 适合场景 | 生产/团队协作 | 本地开发 |

## 安装 Docker

### Windows

1. **下载 Docker Desktop**
   - 访问：https://www.docker.com/products/docker-desktop/
   - 下载 Windows 版本

2. **安装**
   - 运行安装程序
   - 按照向导完成安装
   - 安装完成后重启电脑

3. **启动 Docker Desktop**
   - 从开始菜单启动
   - 等待 Docker 启动完成

4. **验证**
   ```bash
   docker --version
   docker-compose --version
   ```

详细安装步骤：[INSTALL_DOCKER.md](INSTALL_DOCKER.md)

## 快速启动

### 方法1：使用 Python 脚本（推荐）

```bash
python start_docker.py
```

选择选项 `1`（构建并启动）

### 方法2：直接使用命令

```bash
# 首次使用（构建镜像）
docker-compose up --build

# 已构建（直接启动）
docker-compose up -d
```

### 访问系统

- 🌐 前端界面：http://localhost:5173
- 📚 API文档：http://localhost:8000/api/docs
- 🔍 健康检查：http://localhost:8000/health

## 详细使用

### 启动服务

```bash
# 前台运行（查看日志）
docker-compose up

# 后台运行
docker-compose up -d

# 重新构建并启动
docker-compose up --build
```

### 停止服务

```bash
# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 查看日志

```bash
# 查看所有日志
docker-compose logs

# 实时查看日志
docker-compose logs -f

# 查看特定服务
docker-compose logs backend
docker-compose logs frontend
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

### 查看状态

```bash
# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats
```

## 配置文件

### 修改配置

配置文件挂载在 `./config` 目录：

```bash
# 修改配置
vim config/config.yaml

# 重启服务使配置生效
docker-compose restart backend
```

### 环境变量

在 `docker-compose.yml` 中添加：

```yaml
services:
  backend:
    environment:
      - DATA_SOURCE_DEFAULT=akshare
      - LOG_LEVEL=INFO
```

## 故障排除

### 问题1：Docker 未安装

**错误：** `'docker' is not recognized`

**解决：**
1. 安装 Docker Desktop
2. 确保 Docker Desktop 正在运行
3. 重启终端

### 问题2：端口被占用

**错误：** `Bind for 0.0.0.0:8000 failed`

**解决：**
```yaml
# 修改 docker-compose.yml
ports:
  - "8001:8000"  # 改为其他端口
```

### 问题3：构建失败

**解决：**
```bash
# 清理并重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### 问题4：容器无法启动

**检查：**
```bash
# 查看日志
docker-compose logs

# 检查状态
docker-compose ps

# 进入容器调试
docker-compose exec backend bash
```

### 问题5：权限问题（Linux）

**错误：** `permission denied`

**解决：**
```bash
sudo usermod -aG docker $USER
# 重新登录
```

## 生产环境

### 优化建议

1. **使用多阶段构建**
2. **移除开发模式的 volume 挂载**
3. **使用环境变量管理配置**
4. **配置日志轮转**
5. **使用 Docker Swarm 或 Kubernetes**

### 示例配置

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    restart: always
    # 移除 volumes（生产环境）
    environment:
      - ENV=production
```

## 相关文档

- [Docker 快速启动](DOCKER_QUICKSTART.md) - 3步快速启动
- [Docker 安装指南](INSTALL_DOCKER.md) - 详细安装步骤
- [Docker 使用指南](DOCKER_GUIDE.md) - 完整使用说明

## 总结

Docker 方案特别适合：
- ✅ 不想在系统安装 Node.js/Python
- ✅ 需要环境隔离
- ✅ 团队协作
- ✅ 生产部署

**快速命令：**
```bash
# 启动
docker-compose up --build

# 停止
docker-compose down
```

