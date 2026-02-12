"""
数据服务层（Service层）
"""
from typing import List
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.factory.data_factory import DataFactory
from backend.models.schemas import StockDataRequest, StockDataResponse, StockDataPoint
import pandas as pd


class DataService:
    """数据服务"""
    
    def __init__(self):
        self.data_adapter = None
        self._adapter_error = None
        self._initialize_adapter()
    
    def _initialize_adapter(self):
        """延迟初始化适配器"""
        try:
            self.data_adapter = DataFactory.create_adapter()
        except Exception as e:
            self._adapter_error = str(e)
            print(f"[警告] 数据适配器初始化失败: {e}")
            # 不抛出异常，允许服务继续运行
    
    def _ensure_adapter(self):
        """确保适配器已初始化"""
        if self.data_adapter is None:
            if self._adapter_error:
                raise Exception(f"数据适配器未初始化: {self._adapter_error}")
            else:
                self._initialize_adapter()
                if self.data_adapter is None:
                    raise Exception("数据适配器初始化失败")
    
    def get_stock_list(self) -> List[str]:
        """获取股票列表"""
        self._ensure_adapter()
        return self.data_adapter.get_stock_list()
    
    def get_daily_data(self, request: StockDataRequest) -> StockDataResponse:
        """获取日线数据"""
        self._ensure_adapter()
        data = self.data_adapter.get_daily_data(
            request.stock_code,
            request.start_date.replace('-', ''),
            request.end_date.replace('-', '')
        )
        
        if data.empty:
            return StockDataResponse(
                stock_code=request.stock_code,
                data=[]
            )
        
        # 转换为响应格式
        data_points = [
            StockDataPoint(
                date=row['date'].strftime('%Y-%m-%d'),
                open=float(row['open']),
                high=float(row['high']),
                low=float(row['low']),
                close=float(row['close']),
                volume=int(row['volume'])
            )
            for _, row in data.iterrows()
        ]
        
        return StockDataResponse(
            stock_code=request.stock_code,
            data=data_points
        )

