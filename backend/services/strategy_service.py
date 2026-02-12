"""
策略服务层（Service层）
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.factory.strategy_factory import StrategyFactory
from core.strategy.base_strategy import BaseStrategy
from backend.models.schemas import StrategyCreate, StrategyUpdate, StrategyResponse


class StrategyService:
    """策略服务（单例模式）"""
    
    _instance = None
    _strategies: Dict[str, Dict] = {}
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StrategyService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 只初始化一次
        if not StrategyService._initialized:
            StrategyService._strategies = {}
            self._register_default_strategies()
            StrategyService._initialized = True
        # 使用类变量，确保所有实例共享数据
        self._strategies = StrategyService._strategies
    
    def _register_default_strategies(self):
        """注册默认策略"""
        try:
            from strategies.moving_average_strategy import MovingAverageStrategy
            StrategyFactory.register_strategy('moving_average', MovingAverageStrategy)
        except ImportError as e:
            print(f"[警告] 无法导入 moving_average 策略: {e}")
        
        # 其他策略类型暂时使用占位符
        # 如果策略不存在，会在创建时给出明确错误
    
    def create_strategy(self, strategy_data: StrategyCreate) -> StrategyResponse:
        """创建策略"""
        strategy_id = str(uuid.uuid4())
        strategy_type_str = strategy_data.strategy_type.value
        
        # 检查策略是否已注册
        available_strategies = StrategyFactory.list_strategies()
        if strategy_type_str not in available_strategies:
            available = ', '.join(available_strategies) if available_strategies else '无'
            raise ValueError(
                f"策略类型 '{strategy_type_str}' 未注册。"
                f"可用策略类型: {available}。"
                f"请确保策略已正确实现并注册。"
            )
        
        # 创建策略实例
        try:
            strategy = StrategyFactory.create_strategy(
                strategy_type_str,
                strategy_data.params or {}
            )
        except Exception as e:
            raise ValueError(f"创建策略实例失败: {str(e)}")
        
        # 保存策略信息
        strategy_info = {
            'id': strategy_id,
            'name': strategy_data.name,
            'strategy_type': strategy_data.strategy_type.value,
            'params': strategy_data.params,
            'description': strategy_data.description,
            'strategy_instance': strategy,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        self._strategies[strategy_id] = strategy_info
        
        return StrategyResponse(
            id=strategy_id,
            name=strategy_info['name'],
            strategy_type=strategy_info['strategy_type'],
            params=strategy_info['params'],
            description=strategy_info['description'],
            created_at=strategy_info['created_at'],
            updated_at=strategy_info['updated_at']
        )
    
    def get_strategy(self, strategy_id: str) -> Optional[StrategyResponse]:
        """获取策略"""
        if strategy_id not in self._strategies:
            return None
        
        info = self._strategies[strategy_id]
        return StrategyResponse(
            id=info['id'],
            name=info['name'],
            strategy_type=info['strategy_type'],
            params=info['params'],
            description=info['description'],
            created_at=info['created_at'],
            updated_at=info['updated_at']
        )
    
    def get_strategy_instance(self, strategy_id: str) -> Optional[BaseStrategy]:
        """获取策略实例"""
        if strategy_id not in self._strategies:
            return None
        return self._strategies[strategy_id]['strategy_instance']
    
    def list_strategies(self) -> List[StrategyResponse]:
        """列出所有策略"""
        return [
            StrategyResponse(
                id=info['id'],
                name=info['name'],
                strategy_type=info['strategy_type'],
                params=info['params'],
                description=info['description'],
                created_at=info['created_at'],
                updated_at=info['updated_at']
            )
            for info in self._strategies.values()
        ]
    
    def update_strategy(self, strategy_id: str, update_data: StrategyUpdate) -> Optional[StrategyResponse]:
        """更新策略"""
        if strategy_id not in self._strategies:
            return None
        
        info = self._strategies[strategy_id]
        
        if update_data.name is not None:
            info['name'] = update_data.name
        if update_data.params is not None:
            info['params'] = update_data.params
            # 重新创建策略实例
            info['strategy_instance'] = StrategyFactory.create_strategy(
                info['strategy_type'],
                update_data.params
            )
        if update_data.description is not None:
            info['description'] = update_data.description
        
        info['updated_at'] = datetime.now()
        
        return StrategyResponse(
            id=info['id'],
            name=info['name'],
            strategy_type=info['strategy_type'],
            params=info['params'],
            description=info['description'],
            created_at=info['created_at'],
            updated_at=info['updated_at']
        )
    
    def delete_strategy(self, strategy_id: str) -> bool:
        """删除策略"""
        if strategy_id in self._strategies:
            del self._strategies[strategy_id]
            return True
        return False

