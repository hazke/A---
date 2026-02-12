"""
回测服务层（Service层）
"""
from typing import Optional, Dict, List
from datetime import datetime
import uuid
import pandas as pd
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.factory.data_factory import DataFactory
from backtest.backtest_engine import BacktestEngine
from backend.models.schemas import BacktestRequest, BacktestResponse, BacktestMetrics, TradeRecord
from backend.services.strategy_service import StrategyService


class LogCollector:
    """日志收集器（用于收集回测过程中的日志）"""
    def __init__(self):
        self.logs = []
    
    def add(self, message: str, level: str = "INFO"):
        """添加日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.logs.append(f"[{timestamp}] [{level}] {message}")
    
    def get_logs(self) -> List[str]:
        """获取所有日志"""
        return self.logs.copy()
    
    def clear(self):
        """清空日志"""
        self.logs = []


class BacktestService:
    """回测服务"""
    
    _instance = None
    _backtests: Dict[str, Dict] = {}
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BacktestService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # 只初始化一次
        if not BacktestService._initialized:
            BacktestService._backtests = {}
            BacktestService._initialized = True
        # 使用类变量，确保所有实例共享数据
        self._backtests = BacktestService._backtests
        # 使用单例的 StrategyService
        self.strategy_service = StrategyService()
    
    def run_backtest(self, request: BacktestRequest) -> BacktestResponse:
        """运行回测"""
        # 创建日志收集器
        log_collector = LogCollector()
        log_collector.add(f"开始回测: 策略ID={request.strategy_id}, 股票={request.stock_code}, 日期范围={request.start_date} 至 {request.end_date}")
        
        # 获取策略实例
        strategy = self.strategy_service.get_strategy_instance(request.strategy_id)
        if not strategy:
            error_msg = f"策略不存在: {request.strategy_id}"
            log_collector.add(error_msg, "ERROR")
            raise ValueError(error_msg)
        log_collector.add(f"策略加载成功: {strategy.name}")
        
        # 获取数据
        data_info = {}
        try:
            log_collector.add("正在连接数据源...")
            data_adapter = DataFactory.create_adapter()
            data_source_type = type(data_adapter).__name__
            log_collector.add(f"数据源: {data_source_type}")
            
            log_collector.add(f"正在获取股票数据: {request.stock_code} ({request.start_date} 至 {request.end_date})")
            data = data_adapter.get_daily_data(
                request.stock_code,
                request.start_date,
                request.end_date
            )
            
            if data.empty:
                error_msg = f"无法获取股票 {request.stock_code} 的数据。可能原因：1) 股票代码错误 2) 日期范围内无数据 3) 数据源连接失败"
                log_collector.add(error_msg, "ERROR")
                raise ValueError(error_msg)
            
            data_info = {
                "data_source": data_source_type,
                "data_count": len(data),
                "date_range": {
                    "start": str(data['date'].min()) if 'date' in data.columns else None,
                    "end": str(data['date'].max()) if 'date' in data.columns else None
                }
            }
            log_collector.add(f"✓ 成功获取 {len(data)} 条数据")
        except ValueError as e:
            log_collector.add(str(e), "ERROR")
            raise
        except Exception as e:
            error_msg = f"获取股票数据时发生错误: {str(e)}"
            log_collector.add(error_msg, "ERROR")
            raise ValueError(
                f"{error_msg}。请检查：1) 股票代码是否正确 2) 日期格式是否正确 3) 数据源是否可用"
            ) from e
        
        # 获取股票名称（在获取数据后，确保适配器已连接）
        stock_name = None
        try:
            # 标准化股票代码（移除可能的前缀）
            stock_code_clean = request.stock_code
            if '.' in stock_code_clean:
                stock_code_clean = stock_code_clean.split('.')[-1]  # 取最后部分
            
            log_collector.add(f"正在获取股票名称: {stock_code_clean}")
            
            if hasattr(data_adapter, 'get_stock_name'):
                stock_name = data_adapter.get_stock_name(stock_code_clean)
                if stock_name:
                    log_collector.add(f"✓ 获取股票名称成功: {stock_name}")
                else:
                    log_collector.add(f"⚠ 无法获取股票名称: {stock_code_clean}，将只显示代码", "WARN")
            else:
                log_collector.add("⚠ 数据适配器不支持获取股票名称", "WARN")
        except Exception as e:
            log_collector.add(f"⚠ 获取股票名称失败: {e}", "WARN")
        
        # 运行回测
        log_collector.add(f"开始运行回测引擎，初始资金: ¥{request.initial_capital:,.2f}")
        backtest_engine = BacktestEngine(strategy, request.initial_capital)
        result = backtest_engine.run(data, request.stock_code)
        
        # 收集回测结果信息
        log_collector.add(f"回测完成: 总交易次数={result['total_trades']}, 最终现金=¥{result['final_cash']:,.2f}")
        if result['total_trades'] == 0:
            log_collector.add("⚠ 策略没有产生任何交易", "WARN")
        
        # 保存回测结果
        backtest_id = str(uuid.uuid4())
        
        # 转换交易记录
        trades = [
            TradeRecord(
                time=trade['time'],
                stock_code=trade['stock_code'],
                action=trade['action'],
                price=trade['price'],
                shares=trade['shares'],
                amount=trade['amount']
            )
            for trade in result['trades']
        ]
        
        # 构建指标
        metrics = BacktestMetrics(
            strategy_return=result['metrics'].get('strategy_return', 0),
            buy_hold_return=result['metrics'].get('buy_hold_return', 0),
            excess_return=result['metrics'].get('excess_return', 0),
            max_drawdown=result['metrics'].get('max_drawdown', 0),
            total_trades=result['total_trades'],
            win_rate=result['metrics'].get('win_rate', 0)
        )
        
        backtest_response = BacktestResponse(
            id=backtest_id,
            strategy_name=result['strategy_name'],
            stock_code=request.stock_code,
            stock_name=stock_name,  # 添加股票名称
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=result['initial_capital'],
            final_cash=result['final_cash'],
            final_positions=result['final_positions'],
            total_trades=result['total_trades'],
            trades=trades,
            metrics=metrics,
            created_at=datetime.now(),
            logs=log_collector.get_logs(),  # 添加日志
            data_info=data_info  # 添加数据信息
        )
        
        # 保存到内存（生产环境应保存到数据库）
        backtest_dict = backtest_response.dict()
        self._backtests[backtest_id] = backtest_dict
        
        return backtest_response
    
    def get_backtest(self, backtest_id: str) -> Optional[BacktestResponse]:
        """获取回测结果"""
        if backtest_id not in self._backtests:
            return None
        
        data = self._backtests[backtest_id]
        # 调试：打印读取的数据
        print(f"[回测服务] 读取数据 - stock_name字段: {data.get('stock_name')}")
        response = BacktestResponse(**data)
        print(f"[回测服务] 返回响应 - stock_name: {response.stock_name}")
        return response

