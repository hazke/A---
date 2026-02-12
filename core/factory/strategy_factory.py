"""
策略工厂 - 工厂模式
"""
from core.strategy.base_strategy import BaseStrategy
from typing import Dict, Type


class StrategyFactory:
    """策略工厂（工厂模式）"""
    
    _strategies: Dict[str, Type[BaseStrategy]] = {}
    
    @staticmethod
    def register_strategy(name: str, strategy_class: Type[BaseStrategy]):
        """注册策略"""
        if not issubclass(strategy_class, BaseStrategy):
            raise TypeError("策略必须继承自BaseStrategy")
        StrategyFactory._strategies[name] = strategy_class
    
    @staticmethod
    def create_strategy(name: str, params: Dict = None) -> BaseStrategy:
        """
        创建策略实例
        
        Args:
            name: 策略名称
            params: 策略参数
        
        Returns:
            BaseStrategy实例
        """
        if name not in StrategyFactory._strategies:
            raise ValueError(f"未注册的策略: {name}")
        
        strategy_class = StrategyFactory._strategies[name]
        return strategy_class(name, params)
    
    @staticmethod
    def list_strategies() -> list:
        """列出所有已注册的策略"""
        return list(StrategyFactory._strategies.keys())

