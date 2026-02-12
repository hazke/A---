import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import type { BacktestResponse } from '../../types/api'

interface BacktestState {
  currentBacktest: BacktestResponse | null
  loading: boolean
  error: string | null
}

const initialState: BacktestState = {
  currentBacktest: null,
  loading: false,
  error: null,
}

const backtestSlice = createSlice({
  name: 'backtest',
  initialState,
  reducers: {
    setBacktest: (state, action: PayloadAction<BacktestResponse | null>) => {
      state.currentBacktest = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    },
  },
})

export const { setBacktest, setLoading, setError } = backtestSlice.actions
export default backtestSlice.reducer

