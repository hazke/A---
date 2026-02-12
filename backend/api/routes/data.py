"""
数据相关API路由（Controller层）
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from backend.models.schemas import StockDataRequest, StockDataResponse
from backend.services.data_service import DataService

router = APIRouter()

# 使用延迟初始化，避免启动时失败
def get_data_service():
    """获取数据服务实例（延迟初始化）"""
    if not hasattr(get_data_service, '_instance'):
        get_data_service._instance = DataService()
    return get_data_service._instance


@router.get("/data/stocks", response_model=List[str])
async def get_stock_list():
    """获取股票列表"""
    try:
        service = get_data_service()
        return service.get_stock_list()
    except Exception as e:
        error_msg = str(e)
        # 提供更友好的错误信息
        if "token" in error_msg.lower() or "tushare" in error_msg.lower():
            error_msg = f"数据源配置错误: {error_msg}。请检查config/config.yaml中的data_source配置，或切换到akshare数据源。"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.post("/data/daily", response_model=StockDataResponse)
async def get_daily_data(request: StockDataRequest):
    """获取日线数据"""
    try:
        service = get_data_service()
        return service.get_daily_data(request)
    except Exception as e:
        error_msg = str(e)
        # 提供更友好的错误信息
        if "token" in error_msg.lower() or "tushare" in error_msg.lower():
            error_msg = f"数据源配置错误: {error_msg}。请检查config/config.yaml中的data_source配置，或切换到akshare数据源。"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

