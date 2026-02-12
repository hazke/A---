import { Card, Row, Col, Statistic } from 'antd'
import { useQuery } from '@tanstack/react-query'
import { strategyAPI } from '../services/api'

const Dashboard: React.FC = () => {
  const { data: strategies, isLoading } = useQuery({
    queryKey: ['strategies'],
    queryFn: () => strategyAPI.list(),
  })

  return (
    <div>
      <h2>仪表盘</h2>
      <Row gutter={16} style={{ marginTop: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="策略总数"
              value={strategies?.length || 0}
              loading={isLoading}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="运行中策略"
              value={0}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="今日收益"
              value={0}
              precision={2}
              suffix="%"
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总资产"
              value={0}
              precision={2}
              suffix="元"
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard

