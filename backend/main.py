"""
FastAPI应用主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.api.routes import strategy, backtest, data, websocket, health, strategy_types
from core.config_manager import ConfigManager

# 创建FastAPI应用
app = FastAPI(
    title="A股量化交易系统API",
    description="量化交易系统后端API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # 前端开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(strategy.router, prefix="/api/v1", tags=["策略"])
app.include_router(strategy_types.router, prefix="/api/v1", tags=["策略类型"])
app.include_router(backtest.router, prefix="/api/v1", tags=["回测"])
app.include_router(data.router, prefix="/api/v1", tags=["数据"])
app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    config = ConfigManager()
    print("✓ API服务器启动完成")
    print(f"✓ 文档地址: http://localhost:8000/api/docs")
    
    # 检查数据源配置（不阻止启动）
    try:
        from backend.services.data_service import DataService
        service = DataService()
        if service.data_adapter is None:
            print("⚠ 数据适配器未初始化，请检查数据源配置")
        else:
            print("✓ 数据源已配置")
    except Exception as e:
        print(f"⚠ 数据源检查失败: {e}")
        print("提示：可以在config/config.yaml中配置数据源，或使用默认的akshare")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "A股量化交易系统API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    # 直接传递app对象，而不是字符串路径
    uvicorn.run(
        app,  # 直接传递app对象
        host="0.0.0.0",
        port=8000,
        reload=False,  # 直接传递对象时reload可能有问题，设为False
        log_level="info"
    )

