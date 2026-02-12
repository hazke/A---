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

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      // FastAPI 错误格式: { detail: "错误信息" }
      const message = error.response.data?.detail || error.response.data?.error || '请求失败'
      console.error('API错误:', {
        status: error.response.status,
        data: error.response.data,
        message
      })
      return Promise.reject(new Error(message))
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('网络错误:', error.message)
      return Promise.reject(new Error('无法连接到服务器，请检查后端服务是否已启动'))
    } else {
      // 其他错误
      console.error('请求错误:', error.message)
      return Promise.reject(error)
    }
  }
)

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
  run: (data: BacktestRequest): Promise<BacktestResponse> => api.post('/backtest/run', data),
  get: (id: string): Promise<BacktestResponse> => api.get(`/backtest/${id}`),
}

// 策略类型相关API
export const strategyTypesAPI = {
  list: (): Promise<{ available: Array<{ value: string; label: string; registered: boolean }>; registered: string[] }> => 
    api.get('/strategy-types'),
}

// 数据相关API
export const dataAPI = {
  getStocks: (): Promise<string[]> => api.get('/data/stocks'),
  getDailyData: (data: StockDataRequest): Promise<StockDataResponse> =>
    api.post('/data/daily', data),
}

export default api

