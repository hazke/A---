import ReactECharts from 'echarts-for-react'
import type { BacktestResponse } from '../../types/api'

interface BacktestChartProps {
  backtest: BacktestResponse
}

const BacktestChart: React.FC<BacktestChartProps> = ({ backtest }) => {
  // 这里可以添加更复杂的图表逻辑
  // 目前显示一个简单的收益对比图

  const option = {
    title: {
      text: '收益对比',
    },
    tooltip: {
      trigger: 'axis',
    },
    legend: {
      data: ['策略收益', '买入持有收益'],
    },
    xAxis: {
      type: 'category',
      data: ['收益率'],
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%',
      },
    },
    series: [
      {
        name: '策略收益',
        type: 'bar',
        data: [backtest.metrics.strategy_return * 100],
        itemStyle: {
          color: backtest.metrics.strategy_return >= 0 ? '#52c41a' : '#ff4d4f',
        },
      },
      {
        name: '买入持有收益',
        type: 'bar',
        data: [backtest.metrics.buy_hold_return * 100],
        itemStyle: {
          color: '#1890ff',
        },
      },
    ],
  }

  return <ReactECharts option={option} style={{ height: '400px' }} />
}

export default BacktestChart

