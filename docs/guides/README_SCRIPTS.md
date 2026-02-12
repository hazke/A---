# Python启动脚本说明

所有批处理文件（.bat）都已转换为Python脚本（.py），方便跨平台使用。

## 可用脚本

### 1. setup_venv.py - 设置虚拟环境
创建虚拟环境并安装所有依赖。

**使用方法：**
```bash
python setup_venv.py
```

### 2. start_backend.py - 启动后端
启动后端API服务器。

**使用方法：**
```bash
python start_backend.py
```

**功能：**
- 自动检测并使用虚拟环境
- 如果未找到虚拟环境，询问是否使用系统Python
- 实时显示后端日志

### 3. start_frontend.py - 启动前端
启动前端开发服务器。

**使用方法：**
```bash
python start_frontend.py
```

**功能：**
- 检查Node.js是否安装
- 自动检测并安装前端依赖（如果缺失）
- 启动Vite开发服务器

### 4. start_all.py - 一键启动
同时启动后端和前端服务器。

**使用方法：**
```bash
python start_all.py
```

**功能：**
- 在新窗口启动后端服务器
- 在新窗口启动前端服务器
- 显示访问地址

## 推荐使用流程

### 第一次使用

```bash
# 1. 设置虚拟环境（只需一次）
python setup_venv.py

# 2. 安装前端依赖（只需一次）
cd frontend
npm install
cd ..

# 3. 一键启动
python start_all.py
```

### 日常使用

```bash
# 一键启动（最简单）
python start_all.py

# 或分别启动
# 终端1：后端
python start_backend.py

# 终端2：前端
python start_frontend.py
```

## 优势

1. **跨平台**：Python脚本可在Windows、Linux、Mac上运行
2. **更清晰**：Python代码比批处理文件更易读
3. **错误处理**：更好的异常处理和错误提示
4. **灵活性**：可以轻松修改和扩展

## 注意事项

1. **虚拟环境**：脚本会自动检测虚拟环境，优先使用
2. **端口占用**：如果端口被占用，会显示错误信息
3. **依赖检查**：前端脚本会自动检查并安装缺失的依赖
4. **窗口管理**：`start_all.py` 会在新窗口启动服务（Windows）

## 故障排除

### 问题1：无法找到Python
```bash
# 检查Python是否安装
python --version
```

### 问题2：虚拟环境未创建
```bash
# 运行设置脚本
python setup_venv.py
```

### 问题3：端口被占用
- 后端端口8000：修改 `backend/main.py` 中的端口
- 前端端口5173：Vite会自动使用下一个可用端口

### 问题4：依赖安装失败
```bash
# 手动安装
# 后端依赖
venv\Scripts\activate  # Windows
pip install -r requirements-all.txt

# 前端依赖
cd frontend
npm install
```

## 与批处理文件的对比

| 功能 | .bat文件 | .py文件 |
|------|----------|---------|
| Windows支持 | ✅ | ✅ |
| Linux/Mac支持 | ❌ | ✅ |
| 错误处理 | 基础 | 完善 |
| 可读性 | 一般 | 优秀 |
| 可扩展性 | 有限 | 优秀 |

**建议**：优先使用Python脚本（.py），批处理文件（.bat）作为Windows用户的备选方案。

