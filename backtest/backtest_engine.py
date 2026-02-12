"""
回测引擎
"""
import pandas as pd
from typing import Dict, List
from core.strategy.base_strategy import BaseStrategy
from core.config_manager import ConfigManager


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, strategy: BaseStrategy, initial_capital: float = None):
        self.strategy = strategy
        config = ConfigManager()
        self.initial_capital = initial_capital or config.get('trading.initial_capital', 1000000)
        self.commission_rate = config.get('trading.commission_rate', 0.0003)
        self.slippage = config.get('trading.slippage', 0.001)
        
        # 回测结果
        self.equity_curve = []  # 净值曲线
        self.trades = []  # 交易记录
        self.returns = []  # 收益率
    
    def run(self, data: pd.DataFrame, stock_code: str = None) -> Dict:
        """
        运行回测
        
        Args:
            data: 历史数据DataFrame
            stock_code: 股票代码
        
        Returns:
            回测结果字典
        """
        # 检查数据量
        if data.empty:
            raise ValueError("数据为空，无法运行回测")
        
        print(f"[回测引擎] 数据量: {len(data)} 条")
        print(f"[回测引擎] 日期范围: {data['date'].min()} 至 {data['date'].max()}")
        
        # 初始化策略资金
        self.strategy.set_cash(self.initial_capital)
        
        # 添加股票代码到数据
        if stock_code:
            data['stock_code'] = stock_code
        
        # 运行策略
        result = self.strategy.run(data)
        
        # 检查是否有交易
        if len(self.strategy.trade_history) == 0:
            print("[回测引擎] 警告: 策略没有产生任何交易")
            print("[回测引擎] 可能原因:")
            print("  1. 数据量不足（移动平均策略需要至少20天数据）")
            print("  2. 策略参数设置不当")
            print("  3. 没有满足交易条件的信号")
        
        # 计算回测指标
        metrics = self._calculate_metrics(data, result)
        
        return {
            'strategy_name': self.strategy.name,
            'initial_capital': self.initial_capital,
            'final_cash': self.strategy.cash,
            'final_positions': self.strategy.positions,
            'total_trades': len(self.strategy.trade_history),
            'trades': self.strategy.trade_history,
            'metrics': metrics
        }
    
    def _calculate_metrics(self, data: pd.DataFrame, result: Dict) -> Dict:
        """计算回测指标"""
        if data.empty:
            return {
                'strategy_return': 0.0,
                'buy_hold_return': 0.0,
                'excess_return': 0.0,
                'max_drawdown': 0.0,
                'total_trades': 0,
                'win_rate': 0.0
            }
        
        # 计算买入持有收益率（基准策略）
        # 买入持有策略：在回测开始时就买入股票，持有到结束，不进行任何交易
        # 这个指标与策略是否交易无关，它表示"如果什么都不做，只是买入持有"的收益率
        # 用于作为基准，对比策略的表现
        initial_price = data.iloc[0]['close']
        final_price = data.iloc[-1]['close']
        buy_hold_return = (final_price - initial_price) / initial_price
        
        # 计算策略收益率
        # 如果没有交易，策略收益率应该为0（因为没有操作，资金没有变化）
        if len(self.strategy.trade_history) == 0:
            strategy_return = 0.0
        else:
            # 计算最终资产价值（现金 + 持仓市值）
            final_value = self.strategy.cash
            for stock_code, shares in self.strategy.positions.items():
                if shares > 0:
                    final_value += final_price * shares
            
            strategy_return = (final_value - self.initial_capital) / self.initial_capital
        
        # 计算最大回撤（简化版本）
        max_drawdown = 0.0
        if len(self.strategy.trade_history) > 0:
            # 如果有交易，计算最大回撤
            equity_values = [self.initial_capital]
            current_value = self.initial_capital
            for trade in self.strategy.trade_history:
                if trade['action'] == 'buy':
                    current_value -= trade['amount']
                else:
                    current_value += trade['amount']
                equity_values.append(current_value)
            
            if len(equity_values) > 1:
                peak = equity_values[0]
                for value in equity_values:
                    if value > peak:
                        peak = value
                    drawdown = (peak - value) / peak if peak > 0 else 0
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown
        
        # 计算胜率（盈利交易数 / 总交易数）
        win_rate = 0.0
        if len(self.strategy.trade_history) > 0:
            # 简化计算：如果有卖出交易，计算胜率
            # 实际应该根据买入卖出配对计算
            profitable_trades = 0
            total_pairs = 0
            # 这里简化处理，实际需要更复杂的逻辑
            win_rate = 0.0  # 暂时设为0，需要更复杂的计算逻辑
        
        # 计算超额收益
        # 超额收益 = 策略收益率 - 买入持有收益率
        # 如果策略没有交易（strategy_return = 0），超额收益 = -buy_hold_return
        # 这表示策略"错过"了买入持有策略的收益（因为没有交易）
        excess_return = strategy_return - buy_hold_return
        
        return {
            'strategy_return': strategy_return,
            'buy_hold_return': buy_hold_return,
            'excess_return': excess_return,
            'max_drawdown': max_drawdown,
            'total_trades': len(self.strategy.trade_history),
            'win_rate': win_rate
        }

