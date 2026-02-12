"""
Pydantic数据模型（Model层）
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class StrategyType(str, Enum):
    """策略类型"""
    MOVING_AVERAGE = "moving_average"
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"


class StrategyCreate(BaseModel):
    """创建策略请求模型"""
    name: str = Field(..., description="策略名称")
    strategy_type: StrategyType = Field(..., description="策略类型")
    params: Dict[str, Any] = Field(default_factory=dict, description="策略参数")
    description: Optional[str] = Field(None, description="策略描述")


class StrategyUpdate(BaseModel):
    """更新策略请求模型"""
    name: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class StrategyResponse(BaseModel):
    """策略响应模型"""
    id: str
    name: str
    strategy_type: str
    params: Dict[str, Any]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BacktestRequest(BaseModel):
    """回测请求模型"""
    strategy_id: str = Field(..., description="策略ID")
    stock_code: str = Field(..., description="股票代码")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")
    initial_capital: float = Field(1000000, description="初始资金")
    commission_rate: float = Field(0.0003, description="手续费率")


class TradeRecord(BaseModel):
    """交易记录模型"""
    time: datetime
    stock_code: str
    action: str  # buy/sell
    price: float
    shares: int
    amount: float


class BacktestMetrics(BaseModel):
    """回测指标模型"""
    strategy_return: float = Field(..., description="策略收益率")
    buy_hold_return: float = Field(..., description="买入持有收益率")
    excess_return: float = Field(..., description="超额收益")
    max_drawdown: float = Field(..., description="最大回撤")
    total_trades: int = Field(..., description="总交易次数")
    win_rate: float = Field(..., description="胜率")


class BacktestResponse(BaseModel):
    """回测响应模型"""
    id: str
    strategy_name: str
    stock_code: str
    stock_name: Optional[str] = None  # 股票名称
    start_date: str
    end_date: str
    initial_capital: float
    final_cash: float
    final_positions: Dict[str, int]
    total_trades: int
    trades: List[TradeRecord]
    metrics: BacktestMetrics
    created_at: datetime
    logs: Optional[List[str]] = None  # 回测日志信息
    data_info: Optional[Dict] = None  # 数据获取信息


class StockDataRequest(BaseModel):
    """股票数据请求模型"""
    stock_code: str = Field(..., description="股票代码")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")


class StockDataPoint(BaseModel):
    """股票数据点"""
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockDataResponse(BaseModel):
    """股票数据响应模型"""
    stock_code: str
    data: List[StockDataPoint]


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    detail: Optional[str] = None
    code: Optional[int] = None

