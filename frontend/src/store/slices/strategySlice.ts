import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { strategyAPI } from '../../services/api'
import type { StrategyResponse } from '../../types/api'

interface StrategyState {
  strategies: StrategyResponse[]
  currentStrategy: StrategyResponse | null
  loading: boolean
  error: string | null
}

const initialState: StrategyState = {
  strategies: [],
  currentStrategy: null,
  loading: false,
  error: null,
}

// 异步thunks
export const fetchStrategies = createAsyncThunk(
  'strategy/fetchStrategies',
  async () => {
    return await strategyAPI.list()
  }
)

export const fetchStrategy = createAsyncThunk(
  'strategy/fetchStrategy',
  async (id: string) => {
    return await strategyAPI.get(id)
  }
)

const strategySlice = createSlice({
  name: 'strategy',
  initialState,
  reducers: {
    setCurrentStrategy: (state, action: PayloadAction<StrategyResponse | null>) => {
      state.currentStrategy = action.payload
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchStrategies.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchStrategies.fulfilled, (state, action) => {
        state.loading = false
        state.strategies = action.payload
      })
      .addCase(fetchStrategies.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message || '获取策略列表失败'
      })
      .addCase(fetchStrategy.fulfilled, (state, action) => {
        state.currentStrategy = action.payload
      })
  },
})

export const { setCurrentStrategy, clearError } = strategySlice.actions
export default strategySlice.reducer

