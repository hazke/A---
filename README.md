# A股量化交易系统

一个基于Python的A股量化交易框架，采用多种设计模式实现可扩展、可维护的交易系统。

## 架构设计

### 核心设计模式

1. **策略模式（Strategy Pattern）**：不同的交易策略可以灵活切换
2. **观察者模式（Observer Pattern）**：实时行情数据推送和事件通知
3. **工厂模式（Factory Pattern）**：创建数据源、策略实例
4. **适配器模式（Adapter Pattern）**：统一不同数据源接口
5. **命令模式（Command Pattern）**：订单执行和撤销
6. **单例模式（Singleton Pattern）**：配置管理、日志管理
7. **模板方法模式（Template Method Pattern）**：策略执行流程标准化

## 项目结构

```
a-stock-quant/
├── config/                 # 配置文件
├── core/                   # 核心模块
│   ├── strategy/          # 策略模块（策略模式）
│   ├── data/              # 数据模块（适配器模式）
│   ├── execution/         # 执行模块（命令模式）
│   ├── observer/          # 观察者模式
│   └── factory/           # 工厂模式
├── strategies/            # 具体策略实现
├── utils/                 # 工具函数
├── backtest/              # 回测引擎
├── requirements.txt       # 依赖包
└── main.py               # 主程序入口
```

## 功能模块

- **数据获取**：支持多种数据源（tushare、akshare等）
- **策略开发**：策略模式实现，易于扩展
- **回测引擎**：历史数据回测
- **订单管理**：命令模式实现订单执行
- **风险管理**：仓位控制、止损止盈
- **实时监控**：观察者模式实现事件通知

## 快速开始

### 环境要求

**方式1：系统安装（推荐开发环境）**
- **Python 3.8+** - 用于后端（可通过虚拟环境管理）
- **Node.js 18+** - 用于前端（需要系统安装）

**方式2：Docker（推荐生产环境，无需安装 Node.js）**
- **Docker** - 只需安装 Docker，无需安装 Node.js 和 Python

> 💡 **为什么需要安装 Node.js？**  
> Node.js 是独立的运行时环境（类似 Python 解释器），不能放到虚拟环境中。  
> 详细说明请查看：[为什么需要安装 Node.js？](docs/why_install_nodejs.md)  
> **不想安装 Node.js？** 可以使用 [Docker 方案](docs/docker/DOCKER_GUIDE.md)！

### 方式1：命令行模式（仅后端）

1. 安装依赖：`pip install -r requirements.txt`
2. 配置数据源：编辑 `config/config.yaml`（可选，默认使用akshare）
3. 运行示例：`python main.py`

### 方式2：全栈模式（前后端分离）

#### 选项A：系统安装（开发环境）

**详细启动步骤请查看：**
- 📖 [快速启动指南](docs/guides/QUICKSTART.md) - 5分钟快速上手
- 📚 [完整启动指南](docs/guides/启动指南.md) - 详细说明和故障排除

**快速命令：**
```bash
# 1. 安装 Python 依赖（使用虚拟环境）
python setup_venv.py

# 2. 安装前端依赖（需要先安装 Node.js）
cd frontend && npm install && cd ..

# 3. 启动系统
python start_all.py
```

#### 选项B：Docker（无需安装 Node.js）

**详细指南：** [Docker 部署指南](docs/docker/DOCKER_GUIDE.md)

**快速命令：**
```bash
# 一键启动（需要先安装 Docker）
python start_docker.py

# 或直接使用 docker-compose
docker-compose up --build
```

**访问地址：**
- 前端界面：http://localhost:5173
- API文档：http://localhost:8000/api/docs

## 使用示例

```python
from core.strategy.base_strategy import BaseStrategy
from core.factory.strategy_factory import StrategyFactory

# 使用工厂模式创建策略
strategy = StrategyFactory.create_strategy('moving_average')

# 运行策略
strategy.run()
```

