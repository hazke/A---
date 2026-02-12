# A股量化交易系统 - 全栈架构

## 架构概览

本系统采用**前后端分离**架构，使用**MVC模式**组织后端代码。

### 技术栈

#### 后端
- **FastAPI**: 高性能异步Web框架
- **Pydantic**: 数据验证和序列化
- **WebSocket**: 实时数据推送
- **架构模式**: MVC (Model-View-Controller)

#### 前端
- **React 18**: UI框架
- **TypeScript**: 类型安全
- **Redux Toolkit**: 状态管理
- **React Query**: 服务器状态管理
- **Ant Design**: UI组件库
- **ECharts**: 图表库
- **Vite**: 构建工具

## 项目结构

```
A股量化/
├── backend/              # 后端API服务
│   ├── api/             # Controller层（路由处理）
│   │   └── routes/      # 路由定义
│   ├── services/        # Service层（业务逻辑）
│   ├── models/          # Model层（数据模型）
│   └── main.py          # FastAPI应用入口
│
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── components/  # React组件
│   │   ├── pages/       # 页面组件
│   │   ├── store/       # Redux状态管理
│   │   ├── services/    # API客户端
│   │   └── types/       # TypeScript类型
│   └── package.json
│
└── core/                # 核心交易模块（保持不变）
```

## MVC架构说明

### Model层 (`backend/models/`)
- **职责**: 定义数据模型、DTO、响应格式
- **技术**: Pydantic模型
- **示例**: `StrategyResponse`, `BacktestRequest`

### View层
- **职责**: API响应格式（JSON）
- **实现**: FastAPI自动序列化Pydantic模型为JSON

### Controller层 (`backend/api/routes/`)
- **职责**: 处理HTTP请求、参数验证、调用Service
- **技术**: FastAPI路由
- **示例**: `strategy.py`, `backtest.py`

### Service层 (`backend/services/`)
- **职责**: 业务逻辑处理、调用Core模块
- **示例**: `StrategyService`, `BacktestService`

## 快速开始

### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务器
python main.py
# 或使用uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问API文档: http://localhost:8000/api/docs

### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
# 或
yarn install

# 启动开发服务器
npm run dev
# 或
yarn dev
```

访问前端: http://localhost:5173

## API接口

### 策略管理
- `GET /api/v1/strategies` - 获取策略列表
- `POST /api/v1/strategies` - 创建策略
- `GET /api/v1/strategies/{id}` - 获取策略详情
- `PUT /api/v1/strategies/{id}` - 更新策略
- `DELETE /api/v1/strategies/{id}` - 删除策略

### 回测
- `POST /api/v1/backtest/run` - 运行回测
- `GET /api/v1/backtest/{id}` - 获取回测结果

### 数据
- `GET /api/v1/data/stocks` - 获取股票列表
- `POST /api/v1/data/daily` - 获取日线数据

### WebSocket
- `WS /ws/market` - 实时行情推送

## 开发指南

### 添加新的API接口

1. **定义Model** (`backend/models/schemas.py`)
```python
class MyRequest(BaseModel):
    field: str
```

2. **实现Service** (`backend/services/my_service.py`)
```python
class MyService:
    def process(self, request: MyRequest):
        # 业务逻辑
        pass
```

3. **创建路由** (`backend/api/routes/my_route.py`)
```python
router = APIRouter()
service = MyService()

@router.post("/my-endpoint")
async def my_endpoint(request: MyRequest):
    return service.process(request)
```

4. **注册路由** (`backend/main.py`)
```python
app.include_router(my_route.router, prefix="/api/v1")
```

### 前端添加新页面

1. **创建页面组件** (`frontend/src/pages/MyPage.tsx`)
2. **添加路由** (`frontend/src/App.tsx`)
3. **创建API服务** (`frontend/src/services/api.ts`)
4. **使用React Query** 获取数据

## 部署

### 后端部署
```bash
# 使用Docker
docker build -t quant-backend ./backend
docker run -p 8000:8000 quant-backend

# 或使用gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 前端部署
```bash
# 构建
npm run build

# 使用Nginx部署dist目录
```

## 架构优势

1. **前后端分离**: 独立开发、部署、扩展
2. **MVC清晰分层**: 代码组织清晰，易于维护
3. **类型安全**: TypeScript + Pydantic双重保障
4. **自动文档**: FastAPI自动生成Swagger文档
5. **实时通信**: WebSocket支持实时数据推送
6. **状态管理**: Redux + React Query管理复杂状态

## 注意事项

1. **CORS配置**: 开发环境已配置，生产环境需要调整
2. **数据存储**: 当前使用内存存储，生产环境需要数据库
3. **认证授权**: 当前未实现，生产环境需要添加JWT等认证
4. **错误处理**: 已实现基础错误处理，可进一步完善

## 扩展建议

1. **数据库**: 使用SQLAlchemy + PostgreSQL存储数据
2. **缓存**: 使用Redis缓存热点数据
3. **消息队列**: 使用Celery处理异步任务
4. **监控**: 添加日志、性能监控
5. **测试**: 添加单元测试和集成测试

