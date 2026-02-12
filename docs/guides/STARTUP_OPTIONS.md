# 启动方式说明

## 三种启动方式

### 1. 🐳 Docker 方式（推荐 - 生产环境）

**优点：**
- ✅ 无需安装 Python 和 Node.js
- ✅ 环境隔离，不污染系统
- ✅ 一键启动，简单方便
- ✅ 适合生产部署

**使用：**
```bash
python start_docker.py
# 或
docker-compose up --build
```

### 2. 🐍 Python 脚本方式（推荐 - 开发环境）

**优点：**
- ✅ 跨平台（Windows/Linux/Mac）
- ✅ 快速启动，无需构建镜像
- ✅ 便于调试和开发
- ✅ 需要安装 Python 和 Node.js

**使用：**
```bash
# 启动全部
python start_all.py

# 只启动后端
python start_backend.py

# 只启动前端
python start_frontend.py
```

### 3. 📜 批处理/Shell 脚本（可选 - 已废弃）

**说明：**
- ⚠️ 这些文件（.bat/.sh）已经**不再需要**
- ✅ Python 脚本（.py）提供了跨平台支持
- ✅ 如果习惯使用，可以保留，但建议使用 Python 脚本

**文件列表：**
- `start_all.bat` / `start_all.sh` - 可删除
- `start_backend.bat` / `start_backend.sh` - 可删除
- `start_frontend.bat` - 可删除

## 推荐方案

### 生产环境
使用 **Docker** 方式

### 开发环境
使用 **Python 脚本** 方式（.py 文件）

### 已废弃
**批处理/Shell 脚本**（.bat/.sh）可以安全删除

## 迁移指南

如果你之前使用 .bat/.sh 文件，现在可以：

1. **使用 Python 脚本替代：**
   ```bash
   # 旧方式
   start_backend.bat
   
   # 新方式
   python start_backend.py
   ```

2. **或使用 Docker：**
   ```bash
   python start_docker.py
   ```

