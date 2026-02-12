# Docker 快速启动指南

## 🚀 3步启动系统

### 步骤1：安装 Docker（只需一次）

**Windows:**
1. 访问：https://www.docker.com/products/docker-desktop/
2. 下载并安装 Docker Desktop
3. 启动 Docker Desktop，等待启动完成

**验证安装：**
```bash
docker --version
docker-compose --version
```

### 步骤2：启动系统

**使用 Python 脚本（推荐）：**
```bash
python start_docker.py
```

选择选项 `1`（构建并启动）

**或直接使用命令：**
```bash
docker-compose up --build
```

### 步骤3：访问系统

等待构建和启动完成后（首次可能需要几分钟）：

- 🌐 **前端界面**：http://localhost:5173
- 📚 **API文档**：http://localhost:8000/api/docs
- 🔍 **健康检查**：http://localhost:8000/health

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

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
```

### 重启服务

```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

## 故障排除

### 问题1：Docker 未安装

**错误：** `'docker' is not recognized`

**解决：**
- 安装 Docker Desktop
- 确保 Docker Desktop 正在运行
- 重启终端

### 问题2：端口被占用

**错误：** `Bind for 0.0.0.0:8000 failed`

**解决：**
```bash
# 修改 docker-compose.yml 中的端口
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

## 优势

✅ **无需安装 Node.js** - Node.js 在容器内运行  
✅ **无需安装 Python** - Python 在容器内运行  
✅ **环境隔离** - 避免依赖冲突  
✅ **一键启动** - `docker-compose up` 即可  
✅ **易于部署** - 生产环境也可以使用

## 详细文档

- [Docker 安装指南](INSTALL_DOCKER.md) - 详细安装步骤
- [Docker 使用指南](DOCKER_GUIDE.md) - 完整使用说明

