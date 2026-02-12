/**
 * API类型定义
 */

export interface StrategyCreate {
  name: string
  strategy_type: 'moving_average' | 'momentum' | 'mean_reversion'
  params?: Record<string, any>
  description?: string
}

export interface StrategyUpdate {
  name?: string
  params?: Record<string, any>
  description?: string
}

export interface StrategyResponse {
  id: string
  name: string
  strategy_type: string
  params: Record<string, any>
  description?: string
  created_at: string
  updated_at: string
}

export interface BacktestRequest {
  strategy_id: string
  stock_code: string
  start_date: string
  end_date: string
  initial_capital?: number
  commission_rate?: number
}

export interface TradeRecord {
  time: string
  stock_code: string
  action: 'buy' | 'sell'
  price: number
  shares: number
  amount: number
}

export interface BacktestMetrics {
  strategy_return: number
  buy_hold_return: number
  excess_return: number
  max_drawdown: number
  total_trades: number
  win_rate: number
}

export interface BacktestResponse {
  id: string
  strategy_name: string
  stock_code: string
  stock_name?: string  // 股票名称
  start_date: string
  end_date: string
  initial_capital: number
  final_cash: number
  final_positions: Record<string, number>
  total_trades: number
  trades: TradeRecord[]
  metrics: BacktestMetrics
  created_at: string
  logs?: string[]  // 回测日志
  data_info?: {  // 数据获取信息
    data_source: string
    data_count: number
    date_range?: {
      start: string | null
      end: string | null
    }
  }
}

export interface StockDataRequest {
  stock_code: string
  start_date: string
  end_date: string
}

export interface StockDataPoint {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface StockDataResponse {
  stock_code: string
  data: StockDataPoint[]
}

