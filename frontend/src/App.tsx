import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import AppLayout from './components/Layout/AppLayout'
import Dashboard from './pages/Dashboard'
import StrategyList from './pages/StrategyList'
import BacktestResult from './pages/BacktestResult'
import DataPerception from './pages/DataPerception'

function App() {
  return (
    <BrowserRouter>
      <Layout style={{ minHeight: '100vh' }}>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/perception" element={<DataPerception />} />
            <Route path="/strategies" element={<StrategyList />} />
            <Route path="/backtest/:id" element={<BacktestResult />} />
          </Routes>
        </AppLayout>
      </Layout>
    </BrowserRouter>
  )
}

export default App

