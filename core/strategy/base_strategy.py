"""
策略基类 - 策略模式和模板方法模式
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
import pandas as pd


class BaseStrategy(ABC):
    """策略基类（策略模式 + 模板方法模式）"""
    
    def __init__(self, name: str, params: Optional[Dict] = None):
        self.name = name
        self.params = params or {}
        self.positions = {}  # 持仓 {stock_code: shares}
        self.position_dates = {}  # 持仓买入日期 {stock_code: {shares: date}} - 用于T+1限制
        self.cash = 0
        self.total_value = 0
        self.trade_history = []  # 交易历史
    
    def run(self, data: pd.DataFrame) -> Dict:
        """
        运行策略（模板方法模式）
        定义了策略执行的固定流程
        """
        # 1. 初始化
        self.on_init()
        
        # 2. 数据预处理
        processed_data = self.preprocess_data(data)
        
        # 3. 生成信号
        signals = self.generate_signals(processed_data)
        
        # 4. 执行交易
        trades = self.execute_trades(signals)
        
        # 5. 风险控制
        self.risk_control()
        
        # 6. 记录结果
        result = self.on_finish()
        
        return {
            'signals': signals,
            'trades': trades,
            'result': result
        }
    
    def on_init(self):
        """初始化（子类可重写）"""
        pass
    
    @abstractmethod
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """数据预处理（子类必须实现）"""
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号（子类必须实现）
        返回包含signal列的DataFrame，signal值：1=买入，-1=卖出，0=持有
        """
        pass
    
    def execute_trades(self, signals: pd.DataFrame) -> List[Dict]:
        """执行交易（子类可重写以自定义交易逻辑）"""
        trades = []
        
        if signals.empty:
            print("[信息] 没有交易信号")
            return trades
        
        for idx, row in signals.iterrows():
            # 获取股票代码
            stock_code = row.get('stock_code')
            if not stock_code:
                print(f"[警告] 信号行缺少股票代码，跳过: {idx}")
                continue
            
            # 获取价格（优先使用close，其次使用price）
            price = row.get('close') or row.get('price', 0)
            if price == 0:
                print(f"[警告] 信号行价格无效，跳过: {idx}")
                continue
            
            # 获取交易日期（用于T+1限制检查）
            trade_date = row.get('date')
            if trade_date is None:
                # 如果没有date列，尝试从index获取
                if hasattr(idx, 'date'):
                    trade_date = idx.date
                elif isinstance(idx, pd.Timestamp):
                    trade_date = idx
                else:
                    # 如果还是没有，使用当前日期（回测中应该总是有日期）
                    print(f"[警告] 信号行缺少交易日期，无法检查T+1限制: {idx}")
            
            if row['signal'] == 1:  # 买入信号
                trade = self._buy(stock_code, price, row.get('shares', 0), trade_date)
                if trade:
                    trades.append(trade)
            elif row['signal'] == -1:  # 卖出信号
                trade = self._sell(stock_code, price, row.get('shares', 0), trade_date)
                if trade:
                    trades.append(trade)
        
        return trades
    
    def _buy(self, stock_code: str, price: float, shares: int = 0, trade_date = None) -> Optional[Dict]:
        """
        买入
        
        Args:
            stock_code: 股票代码
            price: 买入价格
            shares: 买入股数（0表示全仓买入）
            trade_date: 交易日期（用于T+1限制）
        """
        if price <= 0:
            print(f"[策略] 买入失败: 价格无效 {price}")
            return None
        
        if shares == 0:
            # A股按手交易（100股为1手）
            available_shares = int(self.cash / price / 100) * 100
            if available_shares < 100:
                print(f"[策略] 买入失败: 资金不足，需要至少 {price * 100:.2f} 元")
                return None
            shares = available_shares
        
        cost = price * shares
        if cost > self.cash:
            print(f"[策略] 买入失败: 资金不足，需要 {cost:.2f} 元，当前资金 {self.cash:.2f} 元")
            return None
        
        self.cash -= cost
        if stock_code in self.positions:
            self.positions[stock_code] += shares
        else:
            self.positions[stock_code] = shares
        
        # 记录买入日期（用于T+1限制）
        # 使用FIFO（先进先出）原则，记录每批买入的日期
        if stock_code not in self.position_dates:
            self.position_dates[stock_code] = []
        
        # 将买入日期添加到队列中（每100股为一批，记录日期）
        # 简化处理：记录总股数和最早买入日期
        if trade_date is not None:
            # 转换为可比较的日期格式
            if isinstance(trade_date, pd.Timestamp):
                trade_date = trade_date.date()
            elif isinstance(trade_date, str):
                from datetime import datetime
                trade_date = datetime.strptime(trade_date, '%Y-%m-%d').date()
            
            # 记录这批股票的买入日期
            for _ in range(shares // 100):  # 每100股记录一次
                self.position_dates[stock_code].append(trade_date)
        else:
            # 如果没有日期，使用当前日期（回测中应该总是有日期）
            from datetime import date
            today = date.today()
            for _ in range(shares // 100):
                self.position_dates[stock_code].append(today)
        
        trade = {
            'time': trade_date if trade_date else datetime.now(),
            'stock_code': stock_code,
            'action': 'buy',
            'price': price,
            'shares': shares,
            'amount': cost
        }
        self.trade_history.append(trade)
        print(f"[策略] 买入: {stock_code} {shares}股 @ {price:.2f}元，金额: {cost:.2f}元，日期: {trade_date}")
        return trade
    
    def _sell(self, stock_code: str, price: float, shares: int = 0, trade_date = None) -> Optional[Dict]:
        """
        卖出（考虑A股T+1限制）
        
        Args:
            stock_code: 股票代码
            price: 卖出价格
            shares: 卖出股数（0表示全部卖出）
            trade_date: 交易日期（用于T+1限制检查）
        """
        if stock_code not in self.positions or self.positions[stock_code] == 0:
            print(f"[策略] 卖出失败: 无持仓 {stock_code}")
            return None
        
        if price <= 0:
            print(f"[策略] 卖出失败: 价格无效 {price}")
            return None
        
        # 检查T+1限制（A股：当日买入的股票，当日不能卖出）
        if trade_date is not None:
            # 转换为可比较的日期格式
            sell_date_obj = None
            if isinstance(trade_date, pd.Timestamp):
                sell_date_obj = trade_date.date()
            elif isinstance(trade_date, datetime):
                sell_date_obj = trade_date.date()
            elif isinstance(trade_date, date):
                sell_date_obj = trade_date
            elif isinstance(trade_date, str):
                # 尝试多种日期格式
                for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d']:
                    try:
                        sell_date_obj = datetime.strptime(trade_date, fmt).date()
                        break
                    except ValueError:
                        continue
                if sell_date_obj is None:
                    print(f"[警告] 无法解析卖出日期格式: {trade_date}")
                    sell_date_obj = date.today()
            
            # 检查是否有当日买入的股票（T+1限制）
            if stock_code in self.position_dates and self.position_dates[stock_code]:
                # 计算可以卖出的股票数量（买入日期早于卖出日期的股票）
                # T+1限制：买入日期必须 < 卖出日期（至少间隔1个交易日）
                available_shares = 0
                available_buy_dates = []
                
                for buy_date in self.position_dates[stock_code]:
                    # 检查买入日期是否早于卖出日期（至少间隔1天）
                    if buy_date < sell_date_obj:
                        available_shares += 100  # 每批100股
                        available_buy_dates.append(buy_date)
                
                if available_shares == 0:
                    # 检查是否所有持仓都是当日买入
                    earliest_buy_date = min(self.position_dates[stock_code])
                    if earliest_buy_date >= sell_date_obj:
                        print(f"[策略] 卖出失败: T+1限制 - {stock_code} 在 {sell_date_obj} 买入，当日不能卖出")
                    else:
                        print(f"[策略] 卖出失败: T+1限制 - {stock_code} 所有持仓都不满足T+1限制")
                    return None
                
                # 如果请求卖出的数量超过可卖出数量，限制为可卖出数量
                if shares == 0:
                    shares = min(self.positions[stock_code], available_shares)
                else:
                    shares = min(shares, available_shares, self.positions[stock_code])
                
                # 更新买入日期记录（只移除可卖出的部分）
                # 按FIFO原则，先移除最早的可卖出记录
                shares_to_remove = shares
                for buy_date in available_buy_dates:
                    if shares_to_remove <= 0:
                        break
                    if buy_date in self.position_dates[stock_code]:
                        self.position_dates[stock_code].remove(buy_date)
                        shares_to_remove -= 100
        else:
            # 如果没有日期信息，使用原有逻辑（但会打印警告）
            print(f"[警告] 卖出时缺少交易日期，无法检查T+1限制: {stock_code}")
            if shares == 0:
                shares = self.positions[stock_code]
        
        shares = min(shares, self.positions[stock_code])
        if shares == 0:
            print(f"[策略] 卖出失败: 可卖出数量为0")
            return None
        
        amount = price * shares
        
        # 更新持仓（买入日期记录已在T+1检查时更新）
        self.cash += amount
        self.positions[stock_code] -= shares
        
        # 如果T+1检查时没有更新日期记录，在这里更新（向后兼容）
        if trade_date is None and stock_code in self.position_dates:
            # 按FIFO原则移除（先买入的先卖出）
            shares_to_remove = shares
            while shares_to_remove > 0 and self.position_dates[stock_code]:
                self.position_dates[stock_code].pop(0)  # 移除最早的买入记录
                shares_to_remove -= 100  # 每批100股
        
        if self.positions[stock_code] == 0:
            del self.positions[stock_code]
            if stock_code in self.position_dates:
                del self.position_dates[stock_code]
        
        trade = {
            'time': trade_date if trade_date else datetime.now(),
            'stock_code': stock_code,
            'action': 'sell',
            'price': price,
            'shares': shares,
            'amount': amount
        }
        self.trade_history.append(trade)
        print(f"[策略] 卖出: {stock_code} {shares}股 @ {price:.2f}元，金额: {amount:.2f}元，日期: {trade_date}")
        return trade
    
    def risk_control(self):
        """风险控制（子类可重写）"""
        from core.config_manager import ConfigManager
        config = ConfigManager()
        
        # 检查单只股票仓位
        max_position = config.get('risk_control.max_position', 0.3)
        # 这里可以添加更多风险控制逻辑
        
    def on_finish(self) -> Dict:
        """策略结束（子类可重写）"""
        return {
            'cash': self.cash,
            'positions': self.positions.copy(),
            'total_trades': len(self.trade_history)
        }
    
    def set_cash(self, cash: float):
        """设置初始资金"""
        self.cash = cash
        self.total_value = cash

