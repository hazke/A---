# 安装 BaoStock 指南

## 问题：pip 命令未找到

如果遇到 `pip is not recognized` 错误，说明：
1. pip 不在系统 PATH 中
2. 需要使用 `python -m pip` 而不是直接使用 `pip`

## 解决方案

### 方法1：使用 Python 脚本（推荐）

运行安装脚本：

```bash
python install_baostock.py
```

这个脚本会自动：
- 检测虚拟环境
- 使用正确的 Python 和 pip
- 安装 baostock
- 验证安装

### 方法2：使用 python -m pip

```bash
# 如果使用虚拟环境
venv\Scripts\python.exe -m pip install baostock>=0.8.8

# 如果使用系统 Python
python -m pip install baostock>=0.8.8
```

### 方法3：使用 setup_venv.py（推荐用于首次设置）

如果你还没有设置虚拟环境，运行：

```bash
python setup_venv.py
```

这会：
- 创建虚拟环境
- 安装所有依赖（包括 baostock）

### 方法4：如果使用 Docker

Docker 会自动安装依赖，只需重新构建：

```bash
docker-compose build backend
docker-compose restart backend
```

## 验证安装

安装后，验证是否成功：

```bash
python -c "import baostock as bs; print('BaoStock版本:', bs.__version__)"
```

## 常见问题

### Q1: 仍然提示 pip 未找到

**解决：**
1. 确认 Python 已安装：`python --version`
2. 使用 `python -m pip` 而不是 `pip`
3. 检查 Python 安装时是否选择了 "Add Python to PATH"

### Q2: 权限错误

**解决：**
- Windows: 以管理员身份运行 PowerShell
- 或使用虚拟环境（推荐）

### Q3: 网络错误

**解决：**
- 检查网络连接
- 使用国内镜像：
  ```bash
  python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple baostock>=0.8.8
  ```

## 下一步

安装完成后：

1. **重启后端服务**
   ```bash
   # Docker
   docker-compose restart backend
   
   # 本地
   python start_backend.py
   ```

2. **验证数据源**
   查看后端日志，应该看到：
   ```
   [BaoStock] 登录成功
   ```

3. **测试回测**
   使用历史日期运行回测，应该可以正常获取数据。

