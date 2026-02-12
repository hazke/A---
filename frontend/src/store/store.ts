import { configureStore } from '@reduxjs/toolkit'
import strategySlice from './slices/strategySlice'
import backtestSlice from './slices/backtestSlice'

export const store = configureStore({
  reducer: {
    strategy: strategySlice,
    backtest: backtestSlice,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

