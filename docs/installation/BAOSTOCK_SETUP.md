# BaoStock 数据源配置指南

## 简介

BaoStock 是一个免费的A股数据接口，相比 AKShare 更稳定可靠。

## 已完成的配置

✅ 已创建 `BaoStockAdapter` 适配器  
✅ 已更新数据工厂，支持 BaoStock  
✅ 已更新配置文件，默认使用 BaoStock  
✅ 已添加 baostock 依赖到 requirements.txt

## 安装依赖

### 如果使用虚拟环境：

```bash
# 激活虚拟环境
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 安装 baostock
pip install baostock>=0.8.8
```

### 如果使用 Docker：

```bash
# 重新构建后端镜像（会自动安装新依赖）
docker-compose build backend
```

### 如果使用 requirements-all.txt：

```bash
pip install -r requirements-all.txt
```

## 配置数据源

### 方法1：使用配置文件（推荐）

编辑 `config/config.yaml`：

```yaml
data_source:
  default: baostock  # 使用 BaoStock
```

### 方法2：代码中指定

```python
from core.factory.data_factory import DataFactory

# 使用 BaoStock
adapter = DataFactory.create_adapter('baostock')
```

## BaoStock 特点

### 优势

✅ **免费** - 无需注册，无需 token  
✅ **稳定** - 连接更稳定，较少出现连接中断  
✅ **数据完整** - 提供完整的A股历史数据  
✅ **支持复权** - 支持前复权、后复权、不复权

### 注意事项

⚠️ **需要登录** - 使用前需要调用 `bs.login()`  
⚠️ **需要登出** - 使用后建议调用 `bs.logout()`  
⚠️ **日期格式** - 使用 `YYYY-MM-DD` 格式

## 使用示例

```python
from core.factory.data_factory import DataFactory

# 创建适配器（默认使用 BaoStock）
adapter = DataFactory.create_adapter()

# 获取股票数据
data = adapter.get_daily_data(
    stock_code='000001',
    start_date='2024-01-01',
    end_date='2024-01-31'
)

# 获取股票名称
name = adapter.get_stock_name('000001')
```

## 自动回退机制

如果 BaoStock 连接失败，系统会自动尝试：
1. BaoStock（默认）
2. AKShare（备用）
3. Tushare（备用，需要 token）

## 故障排除

### 问题1：BaoStock 登录失败

**错误：** `BaoStock登录失败`

**解决：**
- 检查网络连接
- 稍后重试（可能是服务器临时问题）
- 系统会自动回退到 AKShare

### 问题2：无法获取数据

**可能原因：**
- 日期是未来日期
- 股票代码错误
- 网络连接问题

**解决：**
- 使用历史日期（2024年或更早）
- 验证股票代码
- 查看后端日志获取详细错误

### 问题3：导入错误

**错误：** `ModuleNotFoundError: No module named 'baostock'`

**解决：**
```bash
pip install baostock>=0.8.8
```

## 验证安装

运行以下命令验证：

```bash
python -c "import baostock as bs; print('BaoStock版本:', bs.__version__)"
```

## 重启服务

安装依赖后，需要重启后端：

```bash
# Docker
docker-compose restart backend

# 本地
# 停止后端（Ctrl+C），然后重新运行
python start_backend.py
```

重启后，系统将默认使用 BaoStock 作为数据源。

