# Docker 故障排除指南

## 常见错误

### 错误1: ERR_NAME_NOT_RESOLVED

**错误信息：** `Failed to load resource: net::ERR_NAME_NOT_RESOLVED`

**原因：**
- 浏览器无法解析 Docker 服务名 `backend`
- 前端代码直接使用了绝对URL而不是相对路径

**解决：**
1. 确保前端API使用相对路径 `/api/v1`（不是 `http://backend:8000/api/v1`）
2. Vite代理会自动将 `/api` 请求转发到后端
3. 重新构建前端容器

### 错误2: ECONNREFUSED

**错误信息：** `ECONNREFUSED` 或 `无法连接到服务器`

**原因：**
- 后端服务未启动
- Docker网络配置问题
- 端口映射错误

**解决：**
```bash
# 1. 检查容器状态
docker-compose ps

# 2. 检查后端日志
docker-compose logs backend

# 3. 测试网络连接（在前端容器内）
docker-compose exec frontend sh
wget -O- http://backend:8000/health
```

### 错误3: 500 Internal Server Error

**错误信息：** `POST http://localhost:5173/api/v1/strategies 500`

**原因：**
- 后端代码错误
- 策略类型未注册
- 数据验证失败

**解决：**
1. 查看后端日志：`docker-compose logs backend`
2. 检查策略类型是否已注册
3. 使用诊断工具：`python check_api.py`

## 诊断步骤

### 步骤1：检查容器状态

```bash
docker-compose ps
```

应该看到两个容器都在运行：
- `quant-backend` - 状态应该是 `Up`
- `quant-frontend` - 状态应该是 `Up`

### 步骤2：检查网络连接

```bash
# 进入前端容器
docker-compose exec frontend sh

# 测试后端连接
wget -O- http://backend:8000/health
# 或
curl http://backend:8000/health
```

如果成功，应该返回：`{"status":"healthy"}`

### 步骤3：检查Vite代理

查看前端容器日志，应该看到：
```
Vite代理配置: {
  isDocker: true,
  backendUrl: 'http://backend:8000',
  ...
}
```

### 步骤4：检查浏览器网络请求

1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 尝试创建策略
4. 查看请求URL：
   - ✅ 正确：`http://localhost:5173/api/v1/strategies`
   - ❌ 错误：`http://backend:8000/api/v1/strategies`

## 快速修复

### 修复1：重新构建容器

```bash
# 停止并删除容器
docker-compose down

# 重新构建
docker-compose build --no-cache

# 启动
docker-compose up
```

### 修复2：检查环境变量

```bash
# 检查前端容器环境变量
docker-compose exec frontend env | grep DOCKER
```

应该看到：`DOCKER=true`

### 修复3：验证Vite配置

```bash
# 查看前端容器日志
docker-compose logs frontend | grep "Vite代理配置"
```

## 配置检查清单

- [ ] `frontend/vite.config.ts` 中 `isDocker` 检测正确
- [ ] `docker-compose.yml` 中设置了 `DOCKER=true`
- [ ] `frontend/src/services/api.ts` 使用相对路径 `/api/v1`
- [ ] 两个容器都在 `quant-network` 网络中
- [ ] 后端容器健康检查通过

## 测试连接

### 从宿主机测试

```bash
# 测试后端（通过端口映射）
curl http://localhost:8000/health

# 测试前端
curl http://localhost:5173
```

### 从容器内测试

```bash
# 进入前端容器
docker-compose exec frontend sh

# 测试后端（通过Docker网络）
wget -O- http://backend:8000/health
```

## 如果仍然失败

1. **查看完整日志：**
   ```bash
   docker-compose logs --tail=100
   ```

2. **重启所有服务：**
   ```bash
   docker-compose restart
   ```

3. **完全重建：**
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

4. **检查Docker网络：**
   ```bash
   docker network inspect a股量化_quant-network
   ```

