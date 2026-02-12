"""
订单命令 - 命令模式
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime
from enum import Enum


class OrderType(Enum):
    """订单类型"""
    MARKET = "market"  # 市价单
    LIMIT = "limit"    # 限价单


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderCommand(ABC):
    """订单命令基类（命令模式）"""
    
    def __init__(self, stock_code: str, shares: int, order_type: OrderType = OrderType.MARKET):
        self.stock_code = stock_code
        self.shares = shares
        self.order_type = order_type
        self.status = OrderStatus.PENDING
        self.created_at = datetime.now()
        self.executed_at = None
        self.price = None
    
    @abstractmethod
    def execute(self) -> bool:
        """执行订单"""
        pass
    
    @abstractmethod
    def cancel(self) -> bool:
        """撤销订单"""
        pass
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'stock_code': self.stock_code,
            'shares': self.shares,
            'order_type': self.order_type.value,
            'status': self.status.value,
            'price': self.price,
            'created_at': self.created_at.isoformat(),
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }


class BuyOrder(OrderCommand):
    """买入订单"""
    
    def __init__(self, stock_code: str, shares: int, price: Optional[float] = None):
        order_type = OrderType.LIMIT if price else OrderType.MARKET
        super().__init__(stock_code, shares, order_type)
        self.limit_price = price
    
    def execute(self) -> bool:
        """执行买入订单"""
        if self.status != OrderStatus.PENDING:
            return False
        
        # 这里应该调用实际的交易接口
        # 示例：模拟执行
        from core.factory.data_factory import DataFactory
        
        try:
            adapter = DataFactory.create_adapter()
            data = adapter.get_realtime_data(self.stock_code)
            
            if not data.empty:
                self.price = data.iloc[0]['close']
                self.status = OrderStatus.FILLED
                self.executed_at = datetime.now()
                return True
            else:
                # 如果没有实时数据，使用限价
                if self.limit_price:
                    self.price = self.limit_price
                    self.status = OrderStatus.FILLED
                    self.executed_at = datetime.now()
                    return True
                else:
                    self.status = OrderStatus.REJECTED
                    return False
        except Exception as e:
            print(f"执行买入订单失败: {e}")
            self.status = OrderStatus.REJECTED
            return False
    
    def cancel(self) -> bool:
        """撤销买入订单"""
        if self.status == OrderStatus.PENDING:
            self.status = OrderStatus.CANCELLED
            return True
        return False


class SellOrder(OrderCommand):
    """卖出订单"""
    
    def __init__(self, stock_code: str, shares: int, price: Optional[float] = None):
        order_type = OrderType.LIMIT if price else OrderType.MARKET
        super().__init__(stock_code, shares, order_type)
        self.limit_price = price
    
    def execute(self) -> bool:
        """执行卖出订单"""
        if self.status != OrderStatus.PENDING:
            return False
        
        # 这里应该调用实际的交易接口
        from core.factory.data_factory import DataFactory
        
        try:
            adapter = DataFactory.create_adapter()
            data = adapter.get_realtime_data(self.stock_code)
            
            if not data.empty:
                self.price = data.iloc[0]['close']
                self.status = OrderStatus.FILLED
                self.executed_at = datetime.now()
                return True
            else:
                if self.limit_price:
                    self.price = self.limit_price
                    self.status = OrderStatus.FILLED
                    self.executed_at = datetime.now()
                    return True
                else:
                    self.status = OrderStatus.REJECTED
                    return False
        except Exception as e:
            print(f"执行卖出订单失败: {e}")
            self.status = OrderStatus.REJECTED
            return False
    
    def cancel(self) -> bool:
        """撤销卖出订单"""
        if self.status == OrderStatus.PENDING:
            self.status = OrderStatus.CANCELLED
            return True
        return False


class OrderInvoker:
    """订单调用者（命令模式的Invoker）"""
    
    def __init__(self):
        self.order_history = []
    
    def execute_order(self, order: OrderCommand) -> bool:
        """执行订单"""
        result = order.execute()
        self.order_history.append(order)
        return result
    
    def cancel_order(self, order: OrderCommand) -> bool:
        """撤销订单"""
        return order.cancel()
    
    def get_order_history(self) -> list:
        """获取订单历史"""
        return [order.to_dict() for order in self.order_history]

