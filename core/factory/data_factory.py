"""
数据源工厂 - 工厂模式
"""
from core.data.data_adapter import DataAdapter
from core.data.tushare_adapter import TushareAdapter
from core.data.akshare_adapter import AKShareAdapter
from core.data.baostock_adapter import BaoStockAdapter
from core.config_manager import ConfigManager


class DataFactory:
    """数据源工厂（工厂模式）"""
    
    _adapters = {
        'tushare': TushareAdapter,
        'akshare': AKShareAdapter,
        'baostock': BaoStockAdapter
    }
    
    @staticmethod
    def create_adapter(source_type: str = None, fallback: bool = True) -> DataAdapter:
        """
        创建数据适配器
        
        Args:
            source_type: 数据源类型 ('tushare' 或 'akshare')
            fallback: 如果指定数据源失败，是否回退到其他数据源
        
        Returns:
            DataAdapter实例
        """
        if source_type is None:
            config = ConfigManager()
            source_type = config.get('data_source.default', 'baostock')  # 默认使用baostock
        
        if source_type not in DataFactory._adapters:
            raise ValueError(f"不支持的数据源类型: {source_type}")
        
        adapter_class = DataFactory._adapters[source_type]
        
        try:
            adapter = adapter_class()
            # 检查适配器是否初始化成功
            if hasattr(adapter, 'initialized') and not adapter.initialized:
                if fallback:
                    # 尝试回退到其他数据源
                    fallback_sources = ['baostock', 'akshare', 'tushare']
                    fallback_sources.remove(source_type)
                    for fallback_source in fallback_sources:
                        if fallback_source in DataFactory._adapters:
                            print(f"[警告] {source_type}适配器初始化失败，尝试回退到{fallback_source}")
                            try:
                                return DataFactory.create_adapter(fallback_source, fallback=False)
                            except:
                                continue
                    raise Exception(f"{source_type}适配器初始化失败，且所有备用数据源也失败")
                else:
                    # 不抛出异常，返回适配器但标记为未初始化
                    # 让调用者处理错误
                    pass
            # 检查BaoStock连接状态
            if hasattr(adapter, '_connected') and not adapter._connected:
                if fallback:
                    fallback_sources = ['akshare', 'tushare']
                    for fallback_source in fallback_sources:
                        if fallback_source in DataFactory._adapters:
                            print(f"[警告] BaoStock连接失败，尝试回退到{fallback_source}")
                            try:
                                return DataFactory.create_adapter(fallback_source, fallback=False)
                            except:
                                continue
                    raise Exception("BaoStock连接失败，且所有备用数据源也失败")
            return adapter
        except Exception as e:
            if fallback:
                # 尝试回退到其他数据源
                fallback_sources = ['baostock', 'akshare', 'tushare']
                if source_type in fallback_sources:
                    fallback_sources.remove(source_type)
                for fallback_source in fallback_sources:
                    if fallback_source in DataFactory._adapters:
                        print(f"[警告] 创建{source_type}适配器失败: {e}")
                        print(f"[信息] 自动回退到{fallback_source}数据源")
                        try:
                            return DataFactory.create_adapter(fallback_source, fallback=False)
                        except Exception as fallback_error:
                            continue
                raise Exception(f"所有数据源初始化失败。最后错误: {e}")
            else:
                raise
    
    @staticmethod
    def register_adapter(source_type: str, adapter_class: type):
        """注册新的数据适配器"""
        if not issubclass(adapter_class, DataAdapter):
            raise TypeError("适配器必须继承自DataAdapter")
        DataFactory._adapters[source_type] = adapter_class

