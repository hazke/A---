import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import AppLayout from './components/Layout/AppLayout'
import Dashboard from './pages/Dashboard'
import StrategyList from './pages/StrategyList'
import BacktestResult from './pages/BacktestResult'

function App() {
  return (
    <BrowserRouter>
      <Layout style={{ minHeight: '100vh' }}>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/strategies" element={<StrategyList />} />
            <Route path="/backtest/:id" element={<BacktestResult />} />
          </Routes>
        </AppLayout>
      </Layout>
    </BrowserRouter>
  )
}

export default App

