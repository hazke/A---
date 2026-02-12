"""
策略类型相关API
"""
from fastapi import APIRouter
from backend.models.schemas import StrategyType
from core.factory.strategy_factory import StrategyFactory

router = APIRouter()


@router.get("/strategy-types")
async def get_strategy_types():
    """获取可用的策略类型"""
    # 获取已注册的策略
    registered_strategies = StrategyFactory.list_strategies()
    
    # 所有定义的策略类型
    all_types = [st.value for st in StrategyType]
    
    # 返回策略类型及其可用性
    return {
        "available": [
            {
                "value": st.value,
                "label": _get_strategy_label(st.value),
                "registered": st.value in registered_strategies
            }
            for st in StrategyType
        ],
        "registered": registered_strategies
    }


def _get_strategy_label(value: str) -> str:
    """获取策略类型的中文标签"""
    labels = {
        "moving_average": "移动平均",
        "momentum": "动量策略",
        "mean_reversion": "均值回归"
    }
    return labels.get(value, value)

