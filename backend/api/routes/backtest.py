"""
回测相关API路由（Controller层）
"""
from fastapi import APIRouter, HTTPException, status
from backend.models.schemas import BacktestRequest, BacktestResponse
from backend.services.backtest_service import BacktestService

router = APIRouter()

# 使用单例模式，确保所有路由共享同一个服务实例
def get_backtest_service():
    """获取回测服务实例（单例）"""
    return BacktestService()

backtest_service = get_backtest_service()


@router.post("/backtest/run", response_model=BacktestResponse, status_code=status.HTTP_201_CREATED)
async def run_backtest(request: BacktestRequest):
    """运行回测"""
    try:
        return backtest_service.run_backtest(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"回测执行失败: {str(e)}"
        )


@router.get("/backtest/{backtest_id}", response_model=BacktestResponse)
async def get_backtest(backtest_id: str):
    """获取回测结果"""
    backtest = backtest_service.get_backtest(backtest_id)
    if not backtest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"回测结果不存在: {backtest_id}"
        )
    return backtest

