"""
A股量化交易系统主程序
"""
import pandas as pd
from datetime import datetime, timedelta
from core.factory.data_factory import DataFactory
from core.factory.strategy_factory import StrategyFactory
from core.config_manager import ConfigManager
from strategies.moving_average_strategy import MovingAverageStrategy
from backtest.backtest_engine import BacktestEngine


def main():
    """主函数"""
    print("=" * 50)
    print("A股量化交易系统")
    print("=" * 50)
    
    # 1. 初始化配置
    config = ConfigManager()
    print("✓ 配置加载完成")
    
    # 2. 创建数据适配器（工厂模式）
    data_adapter = DataFactory.create_adapter()
    print(f"✓ 数据源: {config.get('data_source.default', 'tushare')}")
    
    # 3. 注册策略（工厂模式）
    StrategyFactory.register_strategy('moving_average', MovingAverageStrategy)
    print("✓ 策略注册完成")
    
    # 4. 获取数据示例
    print("\n获取股票数据...")
    stock_code = "000001"  # 平安银行
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=100)).strftime('%Y%m%d')
    
    try:
        data = data_adapter.get_daily_data(stock_code, start_date, end_date)
        if data.empty:
            print(f"⚠️ 无法获取 {stock_code} 的数据，请检查数据源配置")
            print("提示：如果使用tushare，需要在config/config.yaml中配置token")
            return
        print(f"✓ 获取到 {len(data)} 条数据")
    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
        return
    
    # 5. 创建策略（工厂模式）
    strategy_params = {
        'short_window': 5,
        'long_window': 20
    }
    strategy = StrategyFactory.create_strategy('moving_average', strategy_params)
    print(f"✓ 策略创建: {strategy.name}")
    
    # 6. 运行回测
    print("\n开始回测...")
    backtest = BacktestEngine(strategy, initial_capital=1000000)
    result = backtest.run(data, stock_code)
    
    # 7. 显示结果
    print("\n" + "=" * 50)
    print("回测结果")
    print("=" * 50)
    print(f"策略名称: {result['strategy_name']}")
    print(f"初始资金: {result['initial_capital']:,.2f} 元")
    print(f"最终现金: {result['final_cash']:,.2f} 元")
    print(f"持仓: {result['final_positions']}")
    print(f"总交易次数: {result['total_trades']}")
    
    if result['metrics']:
        metrics = result['metrics']
        print(f"\n策略收益率: {metrics.get('strategy_return', 0)*100:.2f}%")
        print(f"买入持有收益率: {metrics.get('buy_hold_return', 0)*100:.2f}%")
        print(f"超额收益: {metrics.get('excess_return', 0)*100:.2f}%")
    
    print("\n" + "=" * 50)
    print("回测完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()

