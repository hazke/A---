"""
移动平均策略示例
"""
import pandas as pd
from core.strategy.base_strategy import BaseStrategy


class MovingAverageStrategy(BaseStrategy):
    """移动平均策略（金叉死叉策略）"""
    
    def __init__(self, name: str = "MovingAverage", params: dict = None):
        super().__init__(name, params)
        # 默认参数：短期均线5日，长期均线20日
        self.short_window = params.get('short_window', 5) if params else 5
        self.long_window = params.get('long_window', 20) if params else 20
    
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """数据预处理：计算移动平均线"""
        df = data.copy()
        
        # 计算短期和长期移动平均线
        df['ma_short'] = df['close'].rolling(window=self.short_window).mean()
        df['ma_long'] = df['close'].rolling(window=self.long_window).mean()
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号"""
        df = data.copy()
        df['signal'] = 0
        
        # 检查数据量是否足够计算长期均线
        if len(df) < self.long_window:
            print(f"[警告] 数据量不足：只有 {len(df)} 天数据，需要至少 {self.long_window} 天才能计算长期均线")
            return pd.DataFrame()
        
        # 金叉：短期均线上穿长期均线，买入信号
        # 死叉：短期均线下穿长期均线，卖出信号
        for i in range(1, len(df)):
            # 检查是否有NaN值（均线计算需要足够的数据）
            if pd.isna(df.iloc[i]['ma_short']) or pd.isna(df.iloc[i]['ma_long']):
                continue
            if pd.isna(df.iloc[i-1]['ma_short']) or pd.isna(df.iloc[i-1]['ma_long']):
                continue
            
            prev_short = df.iloc[i-1]['ma_short']
            prev_long = df.iloc[i-1]['ma_long']
            curr_short = df.iloc[i]['ma_short']
            curr_long = df.iloc[i]['ma_long']
            
            # 金叉：买入信号
            if prev_short <= prev_long and curr_short > curr_long:
                df.iloc[i, df.columns.get_loc('signal')] = 1
            # 死叉：卖出信号
            elif prev_short >= prev_long and curr_short < curr_long:
                df.iloc[i, df.columns.get_loc('signal')] = -1
        
        # 只返回有信号的记录，但保留所有必要信息
        signals = df[df['signal'] != 0].copy()
        
        # 确保包含必要的列
        if len(signals) > 0:
            # 添加价格信息（使用收盘价）
            if 'price' not in signals.columns:
                signals['price'] = signals['close']
            # 确保有股票代码
            if 'stock_code' not in signals.columns and 'stock_code' in df.columns:
                # 从原始数据获取股票代码
                stock_code = df['stock_code'].iloc[0] if 'stock_code' in df.columns else None
                if stock_code:
                    signals['stock_code'] = stock_code
            # 确保有日期信息（用于T+1限制检查）
            if 'date' not in signals.columns and 'date' in df.columns:
                # 从原始数据获取日期
                signals['date'] = signals.index.map(lambda idx: df.loc[idx, 'date'] if idx in df.index else None)
        
        return signals

