import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Card, Row, Col, Statistic, Table, Spin, message, Collapse, Tag, Descriptions } from 'antd'
import { backtestAPI } from '../services/api'
import BacktestChart from '../components/Backtest/BacktestChart'

const { Panel } = Collapse

const BacktestResult: React.FC = () => {
  const { id } = useParams<{ id: string }>()

  const { data: backtest, isLoading, error } = useQuery({
    queryKey: ['backtest', id],
    queryFn: () => backtestAPI.get(id!),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: 50 }}>
        <Spin size="large" />
      </div>
    )
  }

  if (error || !backtest) {
    message.error('获取回测结果失败')
    return <div>回测结果不存在</div>
  }

  // 调试：检查股票名称
  console.log('回测结果数据:', backtest)
  console.log('股票名称:', backtest.stock_name, '类型:', typeof backtest.stock_name)
  console.log('股票代码:', backtest.stock_code)

  const tradeColumns = [
    {
      title: '时间',
      dataIndex: 'time',
      key: 'time',
      render: (text: string) => new Date(text).toLocaleString('zh-CN'),
    },
    {
      title: '股票代码',
      dataIndex: 'stock_code',
      key: 'stock_code',
    },
    {
      title: '操作',
      dataIndex: 'action',
      key: 'action',
      render: (text: string) => (
        <span style={{ color: text === 'buy' ? '#52c41a' : '#ff4d4f' }}>
          {text === 'buy' ? '买入' : '卖出'}
        </span>
      ),
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      render: (value: number) => `¥${value.toFixed(2)}`,
    },
    {
      title: '数量',
      dataIndex: 'shares',
      key: 'shares',
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      render: (value: number) => `¥${value.toFixed(2)}`,
    },
  ]

  return (
    <div>
      <h2>回测结果</h2>

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="策略收益率"
              value={backtest.metrics.strategy_return * 100}
              precision={2}
              suffix="%"
              valueStyle={{ color: backtest.metrics.strategy_return >= 0 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="买入持有收益率"
              value={backtest.metrics.buy_hold_return * 100}
              precision={2}
              suffix="%"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="超额收益"
              value={backtest.metrics.excess_return * 100}
              precision={2}
              suffix="%"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="最大回撤"
              value={backtest.metrics.max_drawdown * 100}
              precision={2}
              suffix="%"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={12}>
          <Card title="基本信息">
            <p><strong>策略名称:</strong> {backtest.strategy_name}</p>
            <p><strong>股票:</strong> {
              backtest.stock_name && backtest.stock_name.trim() 
                ? `${backtest.stock_name} (${backtest.stock_code})` 
                : backtest.stock_code
            }</p>
            <p><strong>回测期间:</strong> {backtest.start_date} 至 {backtest.end_date}</p>
            <p><strong>初始资金:</strong> ¥{backtest.initial_capital.toLocaleString()}</p>
            <p><strong>最终现金:</strong> ¥{backtest.final_cash.toLocaleString()}</p>
            <p><strong>总交易次数:</strong> {backtest.total_trades}</p>
            <p><strong>胜率:</strong> {(backtest.metrics.win_rate * 100).toFixed(2)}%</p>
          </Card>
        </Col>
        <Col span={12}>
          <Card title="持仓信息">
            {Object.keys(backtest.final_positions).length > 0 ? (
              <ul>
                {Object.entries(backtest.final_positions).map(([code, shares]) => (
                  <li key={code}>
                    {code}: {shares} 股
                  </li>
                ))}
              </ul>
            ) : (
              <p>无持仓</p>
            )}
          </Card>
        </Col>
      </Row>

      <Card title="回测图表" style={{ marginTop: 16 }}>
        <BacktestChart backtest={backtest} />
      </Card>

      <Card title="交易记录" style={{ marginTop: 16 }}>
        <Table
          columns={tradeColumns}
          dataSource={backtest.trades}
          rowKey={(record, index) => `${record.time}-${index}`}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Card title="回测详情" style={{ marginTop: 16 }}>
        <Collapse defaultActiveKey={['data', 'logs']}>
          {/* 数据获取信息 */}
          {backtest.data_info && (
            <Panel header="数据获取信息" key="data">
              <Descriptions column={1} bordered size="small">
                <Descriptions.Item label="数据源">
                  <Tag color="blue">{backtest.data_info.data_source}</Tag>
                </Descriptions.Item>
                <Descriptions.Item label="数据条数">
                  {backtest.data_info.data_count} 条
                </Descriptions.Item>
                {backtest.data_info.date_range && (
                  <>
                    <Descriptions.Item label="开始日期">
                      {backtest.data_info.date_range.start || 'N/A'}
                    </Descriptions.Item>
                    <Descriptions.Item label="结束日期">
                      {backtest.data_info.date_range.end || 'N/A'}
                    </Descriptions.Item>
                  </>
                )}
              </Descriptions>
            </Panel>
          )}

          {/* 回测日志 */}
          {backtest.logs && backtest.logs.length > 0 && (
            <Panel header={`回测日志 (${backtest.logs.length} 条)`} key="logs">
              <div
                style={{
                  maxHeight: '400px',
                  overflowY: 'auto',
                  backgroundColor: '#f5f5f5',
                  padding: '12px',
                  borderRadius: '4px',
                  fontFamily: 'monospace',
                  fontSize: '12px',
                  lineHeight: '1.6',
                }}
              >
                {backtest.logs.map((log, index) => {
                  // 根据日志级别设置颜色
                  let color = '#333'
                  if (log.includes('[ERROR]')) {
                    color = '#ff4d4f'
                  } else if (log.includes('[WARN]')) {
                    color = '#faad14'
                  } else if (log.includes('✓') || log.includes('成功')) {
                    color = '#52c41a'
                  }
                  
                  return (
                    <div
                      key={index}
                      style={{
                        color,
                        marginBottom: '4px',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      {log}
                    </div>
                  )
                })}
              </div>
            </Panel>
          )}
        </Collapse>
      </Card>
    </div>
  )
}

export default BacktestResult

