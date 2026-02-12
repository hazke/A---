# Docker 网络问题修复指南

## 问题分析

错误 `ERR_NAME_NOT_RESOLVED` 的原因：

1. **浏览器无法解析 Docker 服务名**
   - 浏览器运行在宿主机上
   - `backend` 是 Docker 网络中的服务名，浏览器无法解析

2. **解决方案**
   - 前端必须使用**相对路径** `/api/v1`
   - Vite 代理在**服务器端**运行，可以访问 Docker 网络
   - 浏览器请求 → Vite 代理 → Docker 网络中的后端

## 修复步骤

### 步骤1：确保前端使用相对路径

已修复：`frontend/src/services/api.ts` 现在使用 `/api/v1`

### 步骤2：确保 Vite 代理配置正确

已修复：`frontend/vite.config.ts` 在 Docker 中使用 `http://backend:8000`

### 步骤3：重新构建并启动

```bash
# 停止现有容器
docker-compose down

# 重新构建（重要！）
docker-compose build --no-cache frontend

# 启动
docker-compose up
```

### 步骤4：验证配置

查看前端容器日志，应该看到：
```
Vite代理配置: {
  isDocker: true,
  backendUrl: 'http://backend:8000',
  ...
}
```

## 关键点

### ✅ 正确配置

```typescript
// frontend/src/services/api.ts
baseURL: '/api/v1'  // 相对路径，通过Vite代理
```

```typescript
// frontend/vite.config.ts (在Docker中)
proxy: {
  '/api': {
    target: 'http://backend:8000',  // Vite服务器可以访问
  }
}
```

### ❌ 错误配置

```typescript
// 错误：浏览器无法解析
baseURL: 'http://backend:8000/api/v1'
```

## 数据流

```
浏览器 (宿主机)
  ↓ 请求 /api/v1/strategies
Vite 开发服务器 (前端容器)
  ↓ 代理到 http://backend:8000/api/v1/strategies
后端服务 (后端容器)
  ↓ 响应
Vite 代理
  ↓ 转发响应
浏览器
```

## 验证方法

### 1. 检查浏览器网络请求

打开开发者工具 → Network：
- ✅ 正确：`http://localhost:5173/api/v1/strategies`
- ❌ 错误：`http://backend:8000/api/v1/strategies`

### 2. 检查 Vite 日志

前端容器日志应该显示代理请求：
```
[代理] POST /api/v1/strategies -> http://backend:8000/api/v1/strategies
```

### 3. 测试网络连接

```bash
# 进入前端容器
docker-compose exec frontend sh

# 测试后端连接（应该成功）
wget -O- http://backend:8000/health
```

## 如果仍然失败

1. **清除浏览器缓存**
2. **重启所有容器**
3. **检查环境变量**：确保 `DOCKER=true` 已设置
4. **查看完整日志**：`docker-compose logs frontend`

