# 系统架构设计文档

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Frontend)                      │
│  React + TypeScript + Redux + ECharts                        │
│  - 策略管理界面                                                │
│  - 回测结果可视化                                              │
│  - 实时行情监控                                                │
│  - 持仓管理                                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket
┌──────────────────────┴──────────────────────────────────────┐
│                      API中间层 (API Layer)                    │
│  FastAPI + Pydantic + WebSocket                               │
│  - RESTful API                                                │
│  - WebSocket实时推送                                           │
│  - 请求验证和错误处理                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                     业务逻辑层 (Business Layer)                │
│  MVC架构模式                                                   │
│  - Controller: 处理请求，调用Service                          │
│  - Service: 业务逻辑处理                                       │
│  - Model: 数据模型和DTO                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                     核心交易层 (Core Layer)                    │
│  现有设计模式实现                                               │
│  - 策略模式、工厂模式、适配器模式等                              │
└──────────────────────────────────────────────────────────────┘
```

## 技术栈选择

### 后端技术栈

1. **FastAPI**
   - ✅ 高性能异步框架
   - ✅ 自动生成API文档（Swagger）
   - ✅ 类型提示和验证（Pydantic）
   - ✅ WebSocket原生支持
   - ✅ 与现有Python代码完美集成

2. **架构模式：MVC**
   - **Model**: 数据模型、DTO、数据库模型
   - **View**: API响应格式（JSON）
   - **Controller**: 路由处理、请求验证

3. **其他依赖**
   - `uvicorn`: ASGI服务器
   - `pydantic`: 数据验证
   - `python-multipart`: 文件上传支持
   - `websockets`: WebSocket支持

### 前端技术栈

1. **React + TypeScript**
   - ✅ 组件化开发
   - ✅ 类型安全
   - ✅ 丰富的生态系统

2. **状态管理**
   - **Redux Toolkit**: 全局状态管理
   - **React Query**: 服务器状态管理

3. **UI框架**
   - **Ant Design**: 企业级UI组件库
   - **ECharts**: 专业图表库

4. **构建工具**
   - **Vite**: 快速构建工具
   - **TypeScript**: 类型检查

## 目录结构

```
A股量化/
├── backend/                    # 后端API
│   ├── api/                   # API路由层（Controller）
│   │   ├── routes/           # 路由定义
│   │   │   ├── strategy.py   # 策略相关API
│   │   │   ├── backtest.py   # 回测相关API
│   │   │   ├── data.py       # 数据相关API
│   │   │   └── websocket.py  # WebSocket路由
│   │   └── dependencies.py   # 依赖注入
│   ├── services/             # 业务逻辑层（Service）
│   │   ├── strategy_service.py
│   │   ├── backtest_service.py
│   │   └── data_service.py
│   ├── models/               # 数据模型（Model）
│   │   ├── schemas.py        # Pydantic模型
│   │   └── responses.py      # 响应模型
│   ├── middleware/           # 中间件
│   │   ├── cors.py          # CORS配置
│   │   └── auth.py          # 认证（可选）
│   └── main.py              # FastAPI应用入口
│
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── components/      # React组件
│   │   │   ├── Strategy/    # 策略相关组件
│   │   │   ├── Backtest/    # 回测相关组件
│   │   │   ├── Chart/       # 图表组件
│   │   │   └── Layout/      # 布局组件
│   │   ├── pages/           # 页面组件
│   │   │   ├── Dashboard.tsx
│   │   │   ├── StrategyList.tsx
│   │   │   └── BacktestResult.tsx
│   │   ├── store/           # Redux状态管理
│   │   │   ├── slices/      # Redux slices
│   │   │   └── store.ts     # Store配置
│   │   ├── services/        # API服务
│   │   │   └── api.ts       # API客户端
│   │   ├── hooks/           # 自定义Hooks
│   │   ├── utils/           # 工具函数
│   │   └── App.tsx          # 根组件
│   ├── package.json
│   └── vite.config.ts
│
└── core/                      # 现有核心模块（保持不变）
```

## API设计

### RESTful API规范

```
GET    /api/v1/strategies          # 获取策略列表
POST   /api/v1/strategies          # 创建策略
GET    /api/v1/strategies/{id}     # 获取策略详情
PUT    /api/v1/strategies/{id}     # 更新策略
DELETE /api/v1/strategies/{id}     # 删除策略

POST   /api/v1/backtest/run        # 运行回测
GET    /api/v1/backtest/{id}       # 获取回测结果

GET    /api/v1/data/stocks         # 获取股票列表
GET    /api/v1/data/daily/{code}   # 获取日线数据

WS     /ws/market                  # WebSocket实时行情
```

## 数据流

### 回测流程
```
前端 → API Controller → Service → Core Strategy → Backtest Engine
  ← JSON响应 ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
```

### 实时行情流程
```
数据源 → Observer → WebSocket → 前端实时更新
```

## 安全考虑

1. **CORS配置**: 限制跨域请求
2. **请求验证**: Pydantic模型验证
3. **错误处理**: 统一错误响应格式
4. **认证授权**: （可选）JWT Token认证

## 部署建议

- **后端**: Docker + Nginx反向代理
- **前端**: Nginx静态文件服务
- **开发环境**: 前后端分离开发，使用代理

