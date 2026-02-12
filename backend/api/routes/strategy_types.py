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
                "description": _get_strategy_description(st.value),
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


def _get_strategy_description(value: str) -> str:
    """获取策略类型的描述"""
    descriptions = {
        "moving_average": (
            "基于移动平均线的趋势跟踪策略。\n\n"
            "**默认参数：**\n"
            "- 短期均线：5日移动平均线（MA5）\n"
            "- 长期均线：20日移动平均线（MA20）\n\n"
            "**交易信号：**\n"
            "- **买入信号（金叉）**：当短期均线从下方上穿长期均线时，产生买入信号\n"
            "- **卖出信号（死叉）**：当短期均线从上方下穿长期均线时，产生卖出信号\n\n"
            "**适用场景：**\n"
            "- 适用于趋势明显的市场环境\n"
            "- 需要至少20天的历史数据才能计算长期均线\n"
            "- 在震荡市场中可能产生较多假信号\n\n"
            "**策略原理：**\n"
            "移动平均线能够平滑价格波动，反映价格趋势。当短期均线位于长期均线上方时，"
            "表明短期趋势向上，市场处于上涨状态；反之则表明市场处于下跌状态。"
        ),
        "momentum": (
            "动量策略基于价格动量指标进行交易决策。\n\n"
            "**策略原理：**\n"
            "动量策略认为价格具有惯性，上涨的股票会继续上涨，下跌的股票会继续下跌。"
            "通过计算价格动量指标（如ROC、RSI等），判断市场动量的强弱。\n\n"
            "**交易信号：**\n"
            "- 当股票价格动量增强时，产生买入信号\n"
            "- 当股票价格动量减弱时，产生卖出信号\n\n"
            "**适用场景：**\n"
            "- 适合捕捉市场趋势的延续性\n"
            "- 在强势上涨或下跌趋势中表现较好\n"
            "- 需要结合其他指标过滤假信号\n\n"
            "**注意事项：**\n"
            "该策略类型目前尚未实现，敬请期待。"
        ),
        "mean_reversion": (
            "均值回归策略基于价格围绕均值波动的原理。\n\n"
            "**策略原理：**\n"
            "均值回归策略认为价格会围绕其均值（如移动平均线）波动。"
            "当价格偏离均值较远时，预期价格会回归均值，从而产生交易机会。\n\n"
            "**交易信号：**\n"
            "- 当价格大幅低于均值时，预期价格会反弹，产生买入信号\n"
            "- 当价格大幅高于均值时，预期价格会回落，产生卖出信号\n\n"
            "**适用场景：**\n"
            "- 适合震荡市场环境\n"
            "- 在价格波动较大的股票中表现较好\n"
            "- 需要设置合理的偏离阈值\n\n"
            "**注意事项：**\n"
            "该策略类型目前尚未实现，敬请期待。"
        )
    }
    return descriptions.get(value, "暂无描述")

