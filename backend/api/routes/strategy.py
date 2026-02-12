"""
策略相关API路由（Controller层）
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from backend.models.schemas import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    ErrorResponse
)
from backend.services.strategy_service import StrategyService

router = APIRouter()

# 使用单例模式，确保所有路由共享同一个服务实例
def get_strategy_service():
    """获取策略服务实例（单例）"""
    return StrategyService()

strategy_service = get_strategy_service()


@router.post("/strategies", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(strategy: StrategyCreate):
    """创建策略"""
    try:
        return strategy_service.create_strategy(strategy)
    except ValueError as e:
        # 策略类型错误或创建失败
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # 其他错误
        import traceback
        error_detail = str(e)
        print(f"[错误] 创建策略失败: {error_detail}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建策略时发生错误: {error_detail}"
        )


@router.get("/strategies", response_model=List[StrategyResponse])
async def list_strategies():
    """获取策略列表"""
    return strategy_service.list_strategies()


@router.get("/strategies/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: str):
    """获取策略详情"""
    strategy = strategy_service.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"策略不存在: {strategy_id}"
        )
    return strategy


@router.put("/strategies/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(strategy_id: str, update: StrategyUpdate):
    """更新策略"""
    strategy = strategy_service.update_strategy(strategy_id, update)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"策略不存在: {strategy_id}"
        )
    return strategy


@router.delete("/strategies/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(strategy_id: str):
    """删除策略"""
    success = strategy_service.delete_strategy(strategy_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"策略不存在: {strategy_id}"
        )

