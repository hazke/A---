"""
健康检查和系统状态API
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()


class HealthStatus(BaseModel):
    """健康状态模型"""
    status: str
    data_source: Dict[str, Any]
    message: str = ""


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "data_source": {
            "status": "unknown"
        },
        "message": "API服务器运行正常"
    }


@router.get("/health/data-source", response_model=Dict[str, Any])
async def check_data_source():
    """检查数据源状态"""
    try:
        from backend.services.data_service import DataService
        service = DataService()
        
        if service.data_adapter is None:
            return {
                "status": "error",
                "message": service._adapter_error or "数据适配器未初始化",
                "suggestion": "请检查config/config.yaml中的data_source配置"
            }
        
        # 检查适配器类型和状态
        adapter_type = type(service.data_adapter).__name__
        adapter_status = "ok"
        error_msg = None
        
        if hasattr(service.data_adapter, 'initialized'):
            adapter_status = "ok" if service.data_adapter.initialized else "error"
            if hasattr(service.data_adapter, 'error_message'):
                error_msg = service.data_adapter.error_message
        
        return {
            "status": adapter_status,
            "adapter_type": adapter_type,
            "message": error_msg or "数据源正常",
            "suggestion": error_msg and "请检查配置或切换到akshare数据源" or None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "suggestion": "请检查config/config.yaml配置"
        }

