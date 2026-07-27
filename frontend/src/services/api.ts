/**
 * API客户端
 */
import axios from 'axios'
import type {
  StrategyCreate,
  StrategyUpdate,
  StrategyResponse,
  BacktestRequest,
  BacktestResponse,
  StockDataRequest,
  StockDataResponse,
  LivePerception,
  FrozenSnapshot,
  FreezeSnapshotResponse,
} from '../types/api'

// API基础URL
// 始终使用相对路径，通过Vite代理转发到后端
// Vite代理在服务器端运行，可以访问Docker网络中的服务
const api = axios.create({
  baseURL: '/api/v1',  // 相对路径，通过Vite代理
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 回测涉及数据拉取与计算，耗时较长
const backtestClient = axios.create({
  baseURL: '/api/v1',
  timeout: 180000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
const handleResponse = (response: { data: unknown }) => response.data

const handleError = (error: {
  response?: { data?: { detail?: string; error?: string }; status?: number }
  request?: unknown
  message?: string
  code?: string
}) => {
  if (error.response) {
    const message = error.response.data?.detail || error.response.data?.error || '请求失败'
    console.error('API错误:', {
      status: error.response.status,
      data: error.response.data,
      message,
    })
    return Promise.reject(new Error(message))
  }
  if (error.request) {
    console.error('网络错误:', error.message)
    const isTimeout = error.code === 'ECONNABORTED'
    return Promise.reject(new Error(
      isTimeout
        ? '请求超时，回测可能仍在进行，请稍后重试或缩短回测日期范围'
        : '无法连接到服务器，请检查后端服务是否已启动'
    ))
  }
  console.error('请求错误:', error.message)
  return Promise.reject(error)
}

api.interceptors.request.use((config) => config, (error) => Promise.reject(error))
api.interceptors.response.use(handleResponse, handleError)
backtestClient.interceptors.response.use(handleResponse, handleError)

// 策略相关API
export const strategyAPI = {
  list: (): Promise<StrategyResponse[]> => api.get('/strategies'),
  get: (id: string): Promise<StrategyResponse> => api.get(`/strategies/${id}`),
  create: (data: StrategyCreate): Promise<StrategyResponse> => api.post('/strategies', data),
  update: (id: string, data: StrategyUpdate): Promise<StrategyResponse> =>
    api.put(`/strategies/${id}`, data),
  delete: (id: string): Promise<void> => api.delete(`/strategies/${id}`),
}

// 回测相关API
export const backtestAPI = {
  run: (data: BacktestRequest): Promise<BacktestResponse> => backtestClient.post('/backtest/run', data),
  get: (id: string): Promise<BacktestResponse> => api.get(`/backtest/${id}`),
}

// 策略类型相关API
export const strategyTypesAPI = {
  list: (): Promise<{ 
    available: Array<{ 
      value: string
      label: string
      description: string
      registered: boolean 
    }>
    registered: string[] 
  }> => api.get('/strategy-types'),
}

// 数据相关API
export const dataAPI = {
  getStocks: (): Promise<string[]> => api.get('/data/stocks'),
  getDailyData: (data: StockDataRequest): Promise<StockDataResponse> =>
    api.post('/data/daily', data),
}

// AgenticQ 数据感知 API (Stage 01)
export const perceptionAPI = {
  getLive: (symbol = '601138'): Promise<LivePerception> =>
    api.get('/perception/live', { params: { symbol } }),
  freezeSnapshot: (symbol = '601138'): Promise<FreezeSnapshotResponse> =>
    api.post('/perception/snapshots/freeze', { symbol }),
  getLatestSnapshot: (symbol = '601138'): Promise<FrozenSnapshot> =>
    api.get('/perception/snapshots/latest', { params: { symbol } }),
  getSnapshot: (snapshotId: string): Promise<FrozenSnapshot> =>
    api.get(`/perception/snapshots/${snapshotId}`),
}

export default api

