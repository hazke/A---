"""
观察者模式实现
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime


class Observer(ABC):
    """观察者接口"""
    
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]):
        """接收事件通知"""
        pass


class Subject:
    """主题（被观察者）"""
    
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer):
        """添加观察者"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer):
        """移除观察者"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event_type: str, data: Dict[str, Any]):
        """通知所有观察者"""
        for observer in self._observers:
            observer.update(event_type, data)


class MarketDataSubject(Subject):
    """行情数据主题"""
    
    def update_price(self, stock_code: str, price: float, volume: int):
        """更新价格数据"""
        data = {
            'stock_code': stock_code,
            'price': price,
            'volume': volume,
            'timestamp': datetime.now()
        }
        self.notify('price_update', data)
    
    def update_trade(self, trade_info: Dict):
        """更新交易信息"""
        trade_info['timestamp'] = datetime.now()
        self.notify('trade_executed', trade_info)


class LoggingObserver(Observer):
    """日志观察者"""
    
    def __init__(self):
        from loguru import logger
        self.logger = logger
    
    def update(self, event_type: str, data: Dict[str, Any]):
        """记录日志"""
        if event_type == 'price_update':
            self.logger.info(
                f"价格更新: {data['stock_code']} = {data['price']:.2f}"
            )
        elif event_type == 'trade_executed':
            self.logger.info(
                f"交易执行: {data.get('action', 'unknown')} "
                f"{data.get('stock_code', 'unknown')} "
                f"{data.get('shares', 0)}股 @ {data.get('price', 0):.2f}"
            )


class AlertObserver(Observer):
    """警报观察者"""
    
    def __init__(self, alert_rules: Dict = None):
        self.alert_rules = alert_rules or {}
    
    def update(self, event_type: str, data: Dict[str, Any]):
        """检查警报条件"""
        if event_type == 'price_update':
            stock_code = data['stock_code']
            price = data['price']
            
            # 检查是否触发价格警报
            if stock_code in self.alert_rules:
                rule = self.alert_rules[stock_code]
                if 'max_price' in rule and price > rule['max_price']:
                    print(f"⚠️ 警报: {stock_code} 价格 {price:.2f} 超过上限 {rule['max_price']:.2f}")
                if 'min_price' in rule and price < rule['min_price']:
                    print(f"⚠️ 警报: {stock_code} 价格 {price:.2f} 低于下限 {rule['min_price']:.2f}")

