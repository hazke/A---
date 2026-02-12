"""
配置管理器 - 单例模式
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any


class ConfigManager:
    """配置管理器（单例模式）"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        # 获取项目根目录
        # __file__ 是 core/config_manager.py
        # 需要向上两级到项目根目录
        current_file = Path(__file__)
        project_root = current_file.parent.parent  # core -> 项目根目录
        
        config_path = project_root / 'config' / 'config.yaml'
        
        if not config_path.exists():
            # 如果配置文件不存在，创建默认配置
            print(f"[警告] 配置文件不存在: {config_path}")
            print("使用默认配置...")
            self._config = self._get_default_config()
            # 尝试创建配置文件
            try:
                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)
                print(f"✓ 已创建默认配置文件: {config_path}")
            except Exception as e:
                print(f"[警告] 无法创建配置文件: {e}")
        else:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'data_source': {
                'default': 'baostock',
                'tushare': {
                    'token': ''
                },
                'akshare': {
                    'timeout': 30
                },
                'baostock': {}
            },
            'trading': {
                'initial_capital': 1000000,
                'commission_rate': 0.0003,
                'slippage': 0.001,
                'min_trade_amount': 100
            },
            'risk_control': {
                'max_position': 0.3,
                'max_total_position': 0.95,
                'stop_loss': 0.05,
                'take_profit': 0.20
            },
            'logging': {
                'level': 'INFO',
                'file': 'logs/trading.log'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def get_config(self) -> Dict:
        """获取完整配置"""
        return self._config.copy()

